from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
from uuid import uuid4

from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository
from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriter
from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
from oil_tracker.domain.redetection import RedetectionPolicy, RedetectionSample
from oil_tracker.domain.session import DebugTraceLevel


class RedetectionWorkspaceError(OSError):
    pass


class RedetectionWorkspace:
    """Own one isolated, streaming, temporary re-detection run."""

    def __init__(
        self,
        run_id: str,
        recipe,
        *,
        policy: RedetectionPolicy | None = None,
        temporary_parent: str | Path | None = None,
    ) -> None:
        self.run_id = str(run_id)
        self.recipe = recipe
        self.policy = policy or RedetectionPolicy()
        parent = None if temporary_parent is None else str(Path(temporary_parent))
        try:
            self.root = Path(tempfile.mkdtemp(prefix="oil-redetection-", dir=parent))
            self.writer = JsonlDebugTraceWriter(
                self.run_id,
                DebugTraceLevel.FULL,
                staging_parent=self.root,
            )
            self.sample_path = self.root / "redetection_samples.jsonl"
            self.index_path = self.root / "redetection_index.json"
            self._sample_handle = self.sample_path.open("wb")
        except Exception as exc:
            root = getattr(self, "root", None)
            if root is not None:
                shutil.rmtree(root, ignore_errors=True)
            raise RedetectionWorkspaceError(
                f"임시 재검출 workspace를 만들 수 없습니다: {exc}"
            ) from exc
        self._sample_summaries: list[dict] = []
        self._repository: DebugTraceRepository | None = None
        self._finalized = False
        self._closed = False

    @classmethod
    def create(
        cls,
        recipe,
        *,
        policy: RedetectionPolicy | None = None,
        temporary_parent: str | Path | None = None,
    ) -> "RedetectionWorkspace":
        return cls(
            f"redetection-{uuid4()}",
            recipe,
            policy=policy,
            temporary_parent=temporary_parent,
        )

    @property
    def repository(self) -> DebugTraceRepository | None:
        return self._repository

    @property
    def finalized(self) -> bool:
        return self._finalized

    @property
    def sample_count(self) -> int:
        return len(self._sample_summaries)

    def write_detection(self, glass, detection, artifacts) -> str:
        if self._finalized or self._closed:
            raise RedetectionWorkspaceError("종료된 workspace에는 기록할 수 없습니다.")
        before = self.writer.record_count
        decision = DebugCaptureDecision(True, (DebugCaptureReason.FULL_TRACE,))
        try:
            self.writer.write(glass, detection, artifacts, decision)
        except Exception as exc:
            raise RedetectionWorkspaceError(
                f"재검출 artifact를 저장할 수 없습니다: {exc}"
            ) from exc
        if self.writer.record_count <= before:
            return ""
        return str(self.writer._summaries[-1]["record_id"])

    def append_sample(self, sample: RedetectionSample) -> None:
        if self._finalized or self._closed:
            raise RedetectionWorkspaceError("종료된 workspace에는 기록할 수 없습니다.")
        payload = _sample_payload(sample)
        try:
            encoded = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            offset = self._sample_handle.tell()
            self._sample_handle.write(encoded)
            self._sample_handle.write(b"\n")
            self._sample_handle.flush()
        except Exception as exc:
            raise RedetectionWorkspaceError(
                f"재검출 sample을 저장할 수 없습니다: {exc}"
            ) from exc
        self._sample_summaries.append(
            {
                "nominal_timestamp_sec": sample.nominal_timestamp_sec,
                "actual_timestamp_sec": sample.actual_timestamp_sec,
                "frame_index": sample.frame_index,
                "debug_record_id": sample.debug_record_id,
                "succeeded": sample.succeeded,
                "warmup": sample.warmup,
                "byte_offset": offset,
                "byte_length": len(encoded),
            }
        )

    def finalize(self) -> DebugTraceRepository:
        if self._finalized:
            if self._repository is None:
                raise RedetectionWorkspaceError("workspace repository가 없습니다.")
            return self._repository
        if self._closed:
            raise RedetectionWorkspaceError("정리된 workspace를 finalize할 수 없습니다.")
        try:
            self._sample_handle.flush()
            os.fsync(self._sample_handle.fileno())
            self._sample_handle.close()
            completion = self.writer.finalize()
            source_debug = Path(completion.staging_directory)
            destination_debug = self.root / "debug"
            if destination_debug.exists() or destination_debug.is_symlink():
                raise RedetectionWorkspaceError("재검출 debug namespace가 이미 존재합니다.")
            os.replace(source_debug, destination_debug)
            index = {
                "schema_version": 1,
                "run_id": self.run_id,
                "sample_file": self.sample_path.name,
                "sample_count": len(self._sample_summaries),
                "samples": self._sample_summaries,
                "debug_index": "debug/debug_index.json",
                "debug_trace": "debug/debug_trace.jsonl",
            }
            temporary = self.index_path.with_suffix(".json.tmp")
            temporary.write_text(
                json.dumps(index, ensure_ascii=False, indent=2, allow_nan=False),
                encoding="utf-8",
            )
            os.replace(temporary, self.index_path)
            bundle = SimpleNamespace(
                root=self.root,
                run_id=self.run_id,
                recipe=self.recipe,
                debug_trace_level=DebugTraceLevel.FULL.value,
                review_index={
                    "debug_trace_level": DebugTraceLevel.FULL.value,
                    "debug_index": "debug/debug_index.json",
                    "debug_trace": "debug/debug_trace.jsonl",
                },
            )
            self._repository = DebugTraceRepository(
                bundle,
                record_cache_size=self.policy.record_cache_size,
                image_cache_size=self.policy.image_cache_size,
            )
            self._finalized = True
            return self._repository
        except Exception as exc:
            self.cleanup()
            if isinstance(exc, RedetectionWorkspaceError):
                raise
            raise RedetectionWorkspaceError(
                f"재검출 workspace를 완료할 수 없습니다: {exc}"
            ) from exc

    def cleanup(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._repository is not None:
            self._repository.close()
            self._repository = None
        handle = getattr(self, "_sample_handle", None)
        if handle is not None and not handle.closed:
            handle.close()
        writer = getattr(self, "writer", None)
        if writer is not None and not self._finalized:
            writer.abort()
        shutil.rmtree(self.root, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback):
        self.cleanup()


def _sample_payload(sample: RedetectionSample) -> dict:
    tracking = sample.tracking_sample
    selected = sample.selected_candidate
    return {
        "nominal_timestamp_sec": sample.nominal_timestamp_sec,
        "requested_timestamp_sec": sample.requested_timestamp_sec,
        "actual_timestamp_sec": sample.actual_timestamp_sec,
        "frame_index": sample.frame_index,
        "fill_state": sample.fill_state.value if sample.fill_state is not None else None,
        "confidence": sample.confidence,
        "is_valid": sample.is_valid,
        "flags": list(sample.flags),
        "debug_record_id": sample.debug_record_id,
        "error_message": sample.error_message,
        "warmup": sample.warmup,
        "tracking": None if tracking is None else {
            "run_id": tracking.run_id,
            "glass_id": tracking.glass_id,
            "frame_index": tracking.frame_index,
            "timestamp_sec": tracking.timestamp_sec,
            "fill_state": tracking.fill_state.value,
            "raw_oil_air_level_y": tracking.raw_oil_air_level_y,
            "raw_oil_air_level_px_from_zero": tracking.raw_oil_air_level_px_from_zero,
            "raw_oil_air_level_mm_from_zero": tracking.raw_oil_air_level_mm_from_zero,
            "smoothed_oil_air_level_px_from_zero": tracking.smoothed_oil_air_level_px_from_zero,
            "smoothed_oil_air_level_mm_from_zero": tracking.smoothed_oil_air_level_mm_from_zero,
            "oil_air_confidence": tracking.oil_air_confidence,
            "raw_foam_front_y": tracking.raw_foam_front_y,
            "raw_foam_front_px_from_zero": tracking.raw_foam_front_px_from_zero,
            "raw_foam_front_mm_from_zero": tracking.raw_foam_front_mm_from_zero,
            "smoothed_foam_front_px_from_zero": tracking.smoothed_foam_front_px_from_zero,
            "smoothed_foam_front_mm_from_zero": tracking.smoothed_foam_front_mm_from_zero,
            "foam_confidence": tracking.foam_confidence,
            "visibility_confidence": tracking.visibility_confidence,
            "overall_confidence": tracking.overall_confidence,
            "is_valid": tracking.is_valid,
            "flags": list(tracking.flags),
        },
        "selected_candidate": None if selected is None else asdict(selected),
    }
