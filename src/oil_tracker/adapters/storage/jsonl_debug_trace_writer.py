from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any

import cv2
import numpy as np

from oil_tracker.domain.debug_trace import (
    DEBUG_TRACE_SCHEMA_VERSION,
    DebugCaptureDecision,
    DebugTraceCompletion,
)
from oil_tracker.domain.session import DebugTraceLevel


_BASIC_IMAGE_KEYS = (
    "overlay",
    "original_roi",
    "normalized",
    "sobel",
    "canny",
    "effective_mask",
    "glare_mask",
    "foam_mask",
    "foam_combined_evidence",
    "foam_accepted_component",
)

_FULL_IMAGE_KEYS = (
    "overlay",
    "original_roi",
    "ellipse_mask",
    "effective_mask",
    "exclusion_mask",
    "grayscale",
    "normalized",
    "blurred",
    "sobel",
    "canny",
    "horizontal_mask",
    "glare_mask",
    "foam_mask",
    "foam_variance",
    "foam_edge_density",
    "foam_whiteness",
    "foam_texture_evidence",
    "foam_glare_excluded_mask",
    "foam_combined_evidence",
    "foam_accepted_component",
    "static_artifact_map",
)


class JsonlDebugTraceWriterFactory:
    def __init__(self, staging_parent: str | Path | None = None) -> None:
        self.staging_parent = Path(staging_parent) if staging_parent is not None else None

    def create(self, run_id: str, recipe, session):
        return JsonlDebugTraceWriter(
            run_id,
            session.debug_trace_level,
            staging_parent=self.staging_parent,
        )


class JsonlDebugTraceWriter:
    """Streams one independent JSON object and its images per selected detection."""

    def __init__(
        self,
        run_id: str,
        trace_level: DebugTraceLevel,
        *,
        staging_parent: str | Path | None = None,
    ) -> None:
        if trace_level is DebugTraceLevel.NONE:
            raise ValueError("A debug writer must not be created for trace level 'none'.")
        parent = None if staging_parent is None else str(Path(staging_parent))
        self.staging_directory = Path(tempfile.mkdtemp(prefix="oil-debug-trace-", dir=parent))
        self.run_id = str(run_id)
        self.trace_level = trace_level
        self.trace_path = self.staging_directory / "debug_trace.jsonl"
        self.index_path = self.staging_directory / "debug_index.json"
        self.frames_directory = self.staging_directory / "frames"
        self.frames_directory.mkdir(parents=True, exist_ok=True)
        self._handle = self.trace_path.open("wb")
        self._summaries: list[dict[str, Any]] = []
        self._keys: set[tuple[str, int, int]] = set()
        self._sequence_annotations: dict[str, dict[str, Any]] = {}
        self._closed = False
        self._finalized = False

    @property
    def record_count(self) -> int:
        return len(self._summaries)

    def write(
        self,
        glass,
        detection,
        artifacts,
        decision: DebugCaptureDecision,
    ) -> str | None:
        if self._closed:
            raise RuntimeError("Debug trace writer is closed.")
        if not decision.capture:
            return None
        if artifacts is None:
            raise OSError("Selected debug trace record has no detector artifacts.")
        timestamp_key = int(round(float(detection.time_sec) * 1_000_000))
        key = (str(glass.id), int(detection.frame_index), timestamp_key)
        if key in self._keys:
            return None
        self._keys.add(key)

        record_id = _record_id(glass.id, detection.frame_index, detection.time_sec)
        glass_directory = self.frames_directory / _safe_component(glass.id) / record_id
        glass_directory.mkdir(parents=True, exist_ok=False)
        warnings: list[str] = []
        images: dict[str, str] = {}
        availability: list[str] = []
        requested_keys = _FULL_IMAGE_KEYS if self.trace_level is DebugTraceLevel.FULL else _BASIC_IMAGE_KEYS
        for image_key in requested_keys:
            image = artifacts.images.get(image_key)
            if image is None:
                warnings.append(f"missing_optional_image:{image_key}")
                continue
            relative = Path("frames") / _safe_component(glass.id) / record_id / f"{_safe_component(image_key)}.png"
            destination = self.staging_directory / relative
            try:
                _write_png(destination, image)
            except Exception as exc:
                destination.unlink(missing_ok=True)
                warnings.append(f"image_encode_failed:{image_key}:{type(exc).__name__}")
                continue
            images[image_key] = relative.as_posix()
            availability.append(image_key)

        candidates = []
        for rank, candidate in enumerate(
            sorted(detection.candidates, key=lambda item: item.final_score, reverse=True),
            1,
        ):
            candidates.append(
                {
                    "rank": rank,
                    "kind": candidate.kind.value,
                    "source": candidate.source,
                    "canonical_y": candidate.y,
                    "local_y": candidate.features.get("local_y"),
                    "features": dict(candidate.features),
                    "penalties": dict(candidate.penalties),
                    "feature_score": candidate.feature_score,
                    "total_penalty": candidate.penalty,
                    "final_score": candidate.final_score,
                    "selected": candidate.selected,
                    "rejected": candidate.rejected,
                    "reject_reason": candidate.reject_reason,
                }
            )
        state = dict(getattr(artifacts, "state", {}) or {})
        state.update(dict(detection.debug_metrics or {}))
        reasons = tuple(dict.fromkeys(reason.value for reason in decision.reasons))
        record = _json_safe(
            {
                "schema_version": DEBUG_TRACE_SCHEMA_VERSION,
                "record_id": record_id,
                "run_id": self.run_id,
                "glass_id": str(glass.id),
                "glass_name": str(glass.name),
                "frame_index": int(detection.frame_index),
                "timestamp_sec": float(detection.time_sec),
                "capture_reasons": list(reasons),
                "fill_state": detection.fill_state.value,
                "confidence": {
                    "oil": detection.oil_air_confidence,
                    "foam": detection.foam_confidence,
                    "visibility": detection.visibility_confidence,
                    "overall": detection.overall_confidence,
                },
                "flags": list(detection.flags),
                "positions": {
                    "raw_oil_y": detection.raw_oil_air_level_y,
                    "smoothed_oil_y": detection.smoothed_oil_air_level_y,
                    "raw_foam_y": detection.raw_foam_front_y,
                    "smoothed_foam_y": detection.smoothed_foam_front_y,
                },
                "state": state,
                "candidates": candidates,
                "images": images,
                "warnings": warnings,
            }
        )
        encoded = json.dumps(
            record,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        offset = self._handle.tell()
        self._handle.write(encoded)
        self._handle.write(b"\n")
        self._handle.flush()
        self._summaries.append(
            {
                "record_id": record_id,
                "run_id": self.run_id,
                "glass_id": str(glass.id),
                "glass_name": str(glass.name),
                "frame_index": int(detection.frame_index),
                "timestamp_sec": float(detection.time_sec),
                "capture_reasons": list(reasons),
                "confidence": _finite_or_none(detection.overall_confidence),
                "fill_state": detection.fill_state.value,
                "artifact_availability": sorted(availability),
                "byte_offset": offset,
                "byte_length": len(encoded),
            }
        )
        return record_id

    def annotate_sequence(self, glass, detections) -> None:
        """Attach final sequence decisions without re-running detection.

        Frame images and the top-level record remain the raw current-frame
        observation. The compact ``sequence`` member is added during finalize
        so one record exposes both pre- and post-resolver truth.
        """

        if self._closed:
            raise RuntimeError("Debug trace writer is closed.")
        captured_ids = {summary["record_id"] for summary in self._summaries}
        for detection in detections:
            record_id = _record_id(
                glass.id,
                detection.frame_index,
                detection.time_sec,
            )
            if record_id not in captured_ids:
                continue
            self._sequence_annotations[record_id] = _sequence_snapshot(detection)

    def finalize(self) -> DebugTraceCompletion:
        if self._finalized:
            return DebugTraceCompletion(
                str(self.staging_directory),
                self.trace_level.value,
                self.record_count,
            )
        if self._closed:
            raise RuntimeError("Debug trace writer was aborted.")
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.close()
        self._closed = True
        if self._sequence_annotations:
            self._apply_sequence_annotations()
        glass_counts = Counter(summary["glass_id"] for summary in self._summaries)
        reason_counts = Counter(
            reason
            for summary in self._summaries
            for reason in summary["capture_reasons"]
        )
        index = {
            "schema_version": DEBUG_TRACE_SCHEMA_VERSION,
            "run_id": self.run_id,
            "trace_level": self.trace_level.value,
            "trace_file": "debug_trace.jsonl",
            "record_count": self.record_count,
            "glass_record_counts": dict(sorted(glass_counts.items())),
            "capture_reason_counts": dict(sorted(reason_counts.items())),
            "records": self._summaries,
        }
        temporary = self.index_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(
                _json_safe(index),
                ensure_ascii=False,
                indent=2,
                allow_nan=False,
            ),
            encoding="utf-8",
        )
        os.replace(temporary, self.index_path)
        self._finalized = True
        return DebugTraceCompletion(
            str(self.staging_directory),
            self.trace_level.value,
            self.record_count,
        )

    def _apply_sequence_annotations(self) -> None:
        temporary = self.trace_path.with_suffix(".jsonl.tmp")
        try:
            with self.trace_path.open("rb") as source, temporary.open("wb") as target:
                for summary in self._summaries:
                    line = source.readline()
                    if not line:
                        raise OSError("Debug trace ended before its index summaries.")
                    record = json.loads(line)
                    annotation = self._sequence_annotations.get(summary["record_id"])
                    if annotation is not None:
                        record["sequence"] = annotation
                        summary["fill_state"] = annotation["fill_state"]
                        summary["confidence"] = annotation["confidence"]["overall"]
                    encoded = json.dumps(
                        _json_safe(record),
                        ensure_ascii=False,
                        separators=(",", ":"),
                        allow_nan=False,
                    ).encode("utf-8")
                    summary["byte_offset"] = target.tell()
                    summary["byte_length"] = len(encoded)
                    target.write(encoded)
                    target.write(b"\n")
                if source.readline():
                    raise OSError("Debug trace has records missing from its index.")
            os.replace(temporary, self.trace_path)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def abort(self) -> None:
        if not self._closed:
            try:
                self._handle.close()
            finally:
                self._closed = True
        shutil.rmtree(self.staging_directory, ignore_errors=True)


def cleanup_debug_staging(completion: DebugTraceCompletion | None) -> None:
    if completion is not None:
        shutil.rmtree(Path(completion.staging_directory), ignore_errors=True)


def _write_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(image)
    if array.dtype != np.uint8:
        finite = np.nan_to_num(array, nan=0.0, posinf=255.0, neginf=0.0)
        minimum, maximum = float(finite.min()), float(finite.max())
        if maximum > minimum:
            finite = (finite - minimum) * (255.0 / (maximum - minimum))
        array = np.clip(finite, 0, 255).astype(np.uint8)
    ok, encoded = cv2.imencode(".png", np.ascontiguousarray(array))
    if not ok:
        raise OSError("OpenCV PNG encoding failed.")
    path.write_bytes(encoded.tobytes())


def _record_id(glass_id: str, frame_index: int, timestamp_sec: float) -> str:
    digest = hashlib.sha256(
        f"{glass_id}\0{frame_index}\0{timestamp_sec:.9f}".encode("utf-8")
    ).hexdigest()[:12]
    return f"f{int(frame_index):09d}_{digest}"


def _safe_component(value: Any) -> str:
    text = re.sub(r"[^0-9A-Za-z._-]+", "_", str(value)).strip("._")
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8]
    return f"{text[:48] or 'item'}_{digest}"


def _finite_or_none(value: Any):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _sequence_snapshot(detection) -> dict[str, Any]:
    candidates = []
    for candidate in sorted(
        detection.candidates,
        key=lambda item: item.final_score,
        reverse=True,
    ):
        if candidate.kind.value not in {"oil_air", "foam_front"}:
            continue
        features = candidate.features
        initial = _authority_name(features.get("r9_initial_authority_tier"))
        post_track = _authority_name(features.get("r9_post_track_authority_tier"))
        authority = _authority_name(features.get("r9_final_authority_tier"))
        candidates.append(
            {
                "kind": candidate.kind.value,
                "source": candidate.source,
                "canonical_y": candidate.y,
                "initial_authority": initial,
                "post_track_authority": post_track,
                "authority": authority,
                "authority_reason": features.get("r11_authority_reason"),
                "cross_representation_support": features.get(
                    "r9_cross_representation_support"
                ),
                "semantic_corridor_support": features.get(
                    "r9_semantic_corridor_support"
                ),
                "track_opposition": features.get("r9_track_opposition"),
                "cluster_support": features.get("r9_cluster_support"),
                "trajectory_support": features.get("r9_trajectory_support"),
                "foam_alias_penalty": features.get("r9_foam_alias_penalty"),
                "calibrated_dynamic_seed": features.get(
                    "r9_calibrated_dynamic_seed",
                    0.0,
                ),
                "calibrated_path_member": features.get(
                    "r10_calibrated_path_member",
                    0.0,
                ),
                "calibrated_motion_keyframe": features.get(
                    "r10_calibrated_motion_keyframe",
                    0.0,
                ),
                "selected": candidate.selected,
                "reject_stage": _sequence_reject_stage(candidate, authority),
            }
        )
    state = {
        str(key): value
        for key, value in detection.debug_metrics.items()
        if str(key).startswith(
            ("sequence_", "r7_", "r8_", "r9_", "r10_", "r11_")
        )
    }
    return _json_safe(
        {
            "fill_state": detection.fill_state.value,
            "confidence": {
                "oil": detection.oil_air_confidence,
                "foam": detection.foam_confidence,
                "visibility": detection.visibility_confidence,
                "overall": detection.overall_confidence,
            },
            "positions": {
                "raw_oil_y": detection.raw_oil_air_level_y,
                "smoothed_oil_y": detection.smoothed_oil_air_level_y,
                "raw_foam_y": detection.raw_foam_front_y,
                "smoothed_foam_y": detection.smoothed_foam_front_y,
            },
            "flags": list(detection.flags),
            "state": state,
            "candidates": candidates,
        }
    )


def _authority_name(value: Any) -> str | None:
    try:
        tier = int(float(value))
    except (TypeError, ValueError):
        return None
    return {
        0: "HARD_INVALID",
        1: "CANDIDATE_ONLY",
        2: "CONTINUATION_ELIGIBLE",
        3: "ANCHOR_ELIGIBLE",
    }.get(tier)


def _sequence_reject_stage(
    candidate,
    authority: str | None,
) -> str:
    if candidate.selected:
        return "ACCEPTED"
    if authority is None:
        return (
            "HARD_INVALID"
            if candidate.reject_reason == "r7_candidate_hard_invalid"
            else "TOP_K_PRUNED_OR_HARD_INVALID"
        )
    features = candidate.features
    if authority == "CANDIDATE_ONLY":
        if float(features.get("r9_track_opposition", 0.0)) >= 0.60:
            return "TRACK_OPPOSITION"
        return "CANDIDATE_ONLY"
    if authority == "ANCHOR_ELIGIBLE" and float(
        features.get("r9_cluster_support", 0.0)
    ) < 0.99:
        return "NO_CLUSTER_SUPPORT"
    if float(features.get("r9_trajectory_support", 0.0)) < 0.99:
        return "NO_TRAJECTORY_SUPPORT"
    return "GLOBAL_PATH_OR_RUN_BOUND"


def _json_safe(value: Any):
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, np.ndarray):
        return [_json_safe(item) for item in value.tolist()]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    enum_value = getattr(value, "value", None)
    if isinstance(enum_value, (str, int, float, bool)):
        return _json_safe(enum_value)
    return str(value)
