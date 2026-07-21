from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Callable, Iterable
from uuid import uuid4

import cv2
import numpy as np

from oil_tracker.adapters.storage.json_truth_repository import (
    TruthRepositoryError,
    build_truth_bundle_identity,
    sha256_file,
)
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.domain.user_truth import UserTruthAnnotation, UserTruthSet


DATASET_SCHEMA_VERSION = 1
FIXTURE_SCHEMA_VERSION = 1
TRUTH_FIXTURE_SCHEMA_VERSION = 1


class RegressionFixtureExportError(ValueError):
    pass


class RegressionFixtureExportCancelled(RegressionFixtureExportError):
    pass


@dataclass(frozen=True)
class FrameIdentityPolicy:
    minimum_tolerance_sec: float = 0.02
    frame_fraction: float = 0.55

    def timestamp_tolerance(self, fps: float) -> float:
        return max(self.minimum_tolerance_sec, self.frame_fraction / max(0.1, float(fps or 0.0)))

    def matches(
        self,
        annotation: UserTruthAnnotation,
        decoded_frame_index: int,
        decoded_timestamp_sec: float,
        fps: float,
    ) -> bool:
        timestamp_matches = abs(float(decoded_timestamp_sec) - annotation.actual_decoded_timestamp_sec) <= self.timestamp_tolerance(fps)
        if annotation.frame_index < 0:
            return timestamp_matches
        return decoded_frame_index == annotation.frame_index and timestamp_matches


@dataclass(frozen=True)
class FixtureExportProgress:
    annotation_id: str
    processed_fixtures: int
    total_fixtures: int
    stage: str
    message: str

    @property
    def fraction(self) -> float:
        return 0.0 if self.total_fixtures <= 0 else min(1.0, self.processed_fixtures / self.total_fixtures)


@dataclass(frozen=True)
class RegressionFixtureExportResult:
    dataset_path: Path
    dataset_id: str
    fixture_count: int
    decoded_frame_count: int
    warnings: tuple[str, ...]


class RegressionFixtureExporter:
    def __init__(
        self,
        reader_factory: Callable[[str | Path], object] = OpenCvVideoReader,
        *,
        frame_policy: FrameIdentityPolicy | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.reader_factory = reader_factory
        self.frame_policy = frame_policy or FrameIdentityPolicy()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def deterministic_fixture_id(self, bundle, annotation: UserTruthAnnotation) -> str:
        prefix = _safe_component(annotation.glass_id)[:24] or "glass"
        source = "|".join(
            (
                str(bundle.run_id),
                annotation.glass_id,
                str(annotation.frame_index),
                annotation.annotation_id,
                str(annotation.revision),
            )
        )
        return f"{prefix}-{hashlib.sha256(source.encode('utf-8')).hexdigest()[:20]}"

    def export(
        self,
        bundle,
        truth_set: UserTruthSet,
        annotations: Iterable[UserTruthAnnotation],
        destination: str | Path,
        *,
        source_video_path: str | Path | None,
        active_truth_path: str | Path | None = None,
        debug_repository=None,
        cancellation=None,
        progress: Callable[[FixtureExportProgress], None] | None = None,
    ) -> RegressionFixtureExportResult:
        selected = tuple(
            sorted(
                annotations,
                key=lambda value: (
                    value.actual_decoded_timestamp_sec,
                    value.frame_index,
                    value.glass_id,
                    value.annotation_id,
                ),
            )
        )
        if not selected:
            raise RegressionFixtureExportError("내보낼 사용자 정답 annotation이 없습니다.")
        annotation_ids = {value.annotation_id for value in truth_set.annotations}
        if any(value.annotation_id not in annotation_ids for value in selected):
            raise RegressionFixtureExportError("현재 사용자 정답 세트에 없는 annotation이 포함되어 있습니다.")
        expected_identity = build_truth_bundle_identity(bundle)
        mismatches = truth_set.bundle_identity.mismatches(expected_identity)
        if mismatches:
            raise RegressionFixtureExportError(
                "현재 result bundle과 사용자 정답 세트 identity가 일치하지 않습니다: "
                + ", ".join(mismatches)
            )
        source = Path(source_video_path).expanduser() if source_video_path else None
        if source is None or not source.is_file():
            raise RegressionFixtureExportError("regression fixture export에는 원본 영상이 필요합니다.")
        parent = ensure_fixture_destination_safe(
            bundle.root,
            destination,
            active_truth_path=active_truth_path,
            source_video_path=source,
        )
        timestamp = self.clock().astimezone(timezone.utc)
        dataset_name = timestamp.strftime("oil_regression_dataset_%Y%m%d_%H%M%S")
        final = parent / dataset_name
        if final.exists() or final.is_symlink():
            raise RegressionFixtureExportError(f"기존 dataset directory를 덮어쓸 수 없습니다: {final}")
        parent.mkdir(parents=True, exist_ok=True)
        parent = ensure_fixture_destination_safe(
            bundle.root,
            parent,
            active_truth_path=active_truth_path,
            source_video_path=source,
        )
        temporary = Path(tempfile.mkdtemp(prefix=f".{dataset_name}.tmp-", dir=str(parent)))
        reader = None
        warnings: list[str] = []
        decoded_count = 0
        dataset_id = str(uuid4())
        fixture_entries: list[dict] = []
        try:
            self._check_cancel(cancellation)
            reader = self.reader_factory(source)
            metadata = reader.metadata
            if (metadata.width, metadata.height) != (expected_identity.source_width, expected_identity.source_height):
                raise RegressionFixtureExportError(
                    "원본 영상 해상도가 result snapshot과 다릅니다. "
                    f"snapshot {expected_identity.source_width}×{expected_identity.source_height}, "
                    f"현재 영상 {metadata.width}×{metadata.height}"
                )
            (temporary / "fixtures").mkdir()
            for index, annotation in enumerate(selected, start=1):
                self._check_cancel(cancellation)
                self._emit(progress, annotation, index - 1, len(selected), "frame_decode", "원본 frame decode")
                fixture_id = self.deterministic_fixture_id(bundle, annotation)
                fixture_dir = temporary / "fixtures" / fixture_id
                fixture_dir.mkdir()
                frame, decoded_index, decoded_timestamp = reader.read_at(annotation.actual_decoded_timestamp_sec)
                decoded_count += 1
                if frame is None or frame.ndim not in (2, 3):
                    raise RegressionFixtureExportError(f"{annotation.annotation_id}: frame decode 결과가 올바르지 않습니다.")
                frame_height, frame_width = frame.shape[:2]
                if (frame_width, frame_height) != (expected_identity.source_width, expected_identity.source_height):
                    raise RegressionFixtureExportError(
                        f"{annotation.annotation_id}: decoded frame 해상도가 snapshot과 다릅니다."
                    )
                if not self.frame_policy.matches(annotation, int(decoded_index), float(decoded_timestamp), metadata.fps):
                    delta = float(decoded_timestamp) - annotation.actual_decoded_timestamp_sec
                    raise RegressionFixtureExportError(
                        f"annotation frame identity 불일치: {annotation.annotation_id}\n"
                        f"저장 frame {annotation.frame_index}, {annotation.actual_decoded_timestamp_sec:.6f}초 / "
                        f"decode frame {decoded_index}, {decoded_timestamp:.6f}초 / 차이 {delta:+.6f}초"
                    )
                self._write_png(fixture_dir / "frame.png", frame)
                glass = bundle.glass_config(annotation.glass_id)
                if glass is None:
                    raise RegressionFixtureExportError(
                        f"{annotation.annotation_id}: result snapshot에 관찰창이 없습니다."
                    )
                crop, crop_origin = _roi_crop(frame, glass)
                self._write_png(fixture_dir / "roi_crop.png", crop)
                self._validate_coordinate_relationship(annotation, crop_origin)
                self._emit(progress, annotation, index - 1, len(selected), "json", "truth와 official reference 저장")
                _write_json(fixture_dir / "truth.json", _truth_payload(annotation))
                _write_json(
                    fixture_dir / "official_reference.json",
                    _official_payload(annotation),
                )
                recipe_source = Path(bundle.files.get("recipe_snapshot", bundle.root / "recipe_snapshot.oilrecipe"))
                session_source = Path(bundle.files.get("session", bundle.root / "session.json"))
                if not recipe_source.is_file() or not session_source.is_file():
                    raise RegressionFixtureExportError("fixture에 복사할 recipe/session snapshot이 없습니다.")
                shutil.copyfile(recipe_source, fixture_dir / "recipe_snapshot.oilrecipe")
                shutil.copyfile(session_source, fixture_dir / "session_snapshot.json")
                fixture_warnings: list[str] = []
                debug_files = self._export_debug(
                    annotation,
                    debug_repository,
                    fixture_dir,
                    fixture_warnings,
                    cancellation,
                )
                warnings.extend(f"{fixture_id}: {value}" for value in fixture_warnings)
                self._emit(progress, annotation, index - 1, len(selected), "hash", "fixture hash 계산")
                relative_files = _relative_file_hashes(fixture_dir, exclude={"fixture_manifest.json"})
                manifest = {
                    "fixture_schema_version": FIXTURE_SCHEMA_VERSION,
                    "fixture_id": fixture_id,
                    "bundle_run_id": expected_identity.run_id,
                    "recipe_id": expected_identity.recipe_id,
                    "recipe_snapshot_hash": expected_identity.recipe_snapshot_hash,
                    "source_video_metadata": {
                        "basename": source.name,
                        "width": metadata.width,
                        "height": metadata.height,
                        "fps": metadata.fps,
                        "duration_sec": metadata.duration_sec,
                        "frame_count": metadata.frame_count,
                        "codec": metadata.codec,
                    },
                    "requested_timestamp_sec": annotation.requested_timestamp_sec,
                    "annotation_actual_decoded_timestamp_sec": annotation.actual_decoded_timestamp_sec,
                    "decoded_timestamp_sec": float(decoded_timestamp),
                    "decoded_frame_index": int(decoded_index),
                    "frame_width": frame_width,
                    "frame_height": frame_height,
                    "frame_identity_tolerance_sec": self.frame_policy.timestamp_tolerance(metadata.fps),
                    "annotation_id": annotation.annotation_id,
                    "annotation_revision": annotation.revision,
                    "roi_crop_origin": {"x": crop_origin[0], "y": crop_origin[1]},
                    "roi_crop_size": {"width": crop.shape[1], "height": crop.shape[0]},
                    "relative_files": sorted(relative_files),
                    "sha256": relative_files,
                    "official_debug_files": debug_files,
                    "warnings": fixture_warnings,
                    "exporter_version": _software_version(),
                }
                _write_json(fixture_dir / "fixture_manifest.json", manifest)
                manifest_hash = sha256_file(fixture_dir / "fixture_manifest.json")
                fixture_entries.append(
                    {
                        "fixture_id": fixture_id,
                        "path": f"fixtures/{fixture_id}",
                        "manifest": f"fixtures/{fixture_id}/fixture_manifest.json",
                        "manifest_sha256": manifest_hash,
                        "annotation_id": annotation.annotation_id,
                        "revision": annotation.revision,
                    }
                )
                self._emit(progress, annotation, index, len(selected), "fixture_complete", "fixture 완료")
            self._check_cancel(cancellation)
            disposition_counts = Counter(value.disposition.value for value in selected)
            error_counts = Counter(error.value for value in selected for error in value.error_types)
            dataset_content_hash = hashlib.sha256(
                json.dumps(fixture_entries, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
            ).hexdigest()
            dataset_manifest = {
                "dataset_schema_version": DATASET_SCHEMA_VERSION,
                "dataset_id": dataset_id,
                "created_at": timestamp.isoformat(),
                "status": "complete",
                "source_bundle_identity": expected_identity.to_dict(),
                "annotation_set_identity": {
                    "annotation_set_id": truth_set.annotation_set_id,
                    "schema_version": truth_set.schema_version,
                    "created_at": truth_set.created_at,
                    "updated_at": truth_set.updated_at,
                },
                "fixture_count": len(fixture_entries),
                "disposition_counts": dict(sorted(disposition_counts.items())),
                "error_type_counts": dict(sorted(error_counts.items())),
                "numeric_truth_usable_count": sum(value.usable_numeric_truth for value in selected),
                "unusable_count": sum(value.disposition.value == "unusable" for value in selected),
                "decoded_frame_count": decoded_count,
                "fixtures": fixture_entries,
                "dataset_content_hash": dataset_content_hash,
                "warnings": warnings,
                "exporter_version": _software_version(),
            }
            _write_json(temporary / "dataset_manifest.json", dataset_manifest)
            self._check_cancel(cancellation)
            os.replace(temporary, final)
            return RegressionFixtureExportResult(
                final,
                dataset_id,
                len(fixture_entries),
                decoded_count,
                tuple(warnings),
            )
        except RegressionFixtureExportCancelled:
            raise
        except RegressionFixtureExportError:
            raise
        except Exception as exc:
            raise RegressionFixtureExportError(f"regression fixture export에 실패했습니다: {exc}") from exc
        finally:
            if reader is not None:
                reader.close()
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)

    def _export_debug(
        self,
        annotation,
        repository,
        fixture_dir: Path,
        warnings: list[str],
        cancellation,
    ) -> list[str]:
        if repository is None or not annotation.official_debug_record_id:
            return []
        self._check_cancel(cancellation)
        try:
            record = repository.load_record(annotation.official_debug_record_id)
        except Exception as exc:
            warnings.append(f"공식 debug record를 읽지 못했습니다: {exc}")
            return []
        debug_dir = fixture_dir / "official_debug"
        debug_dir.mkdir()
        _write_json(debug_dir / "detection_debug.json", _jsonable(record))
        written = ["official_debug/detection_debug.json"]
        keys = (
            "overlay",
            "original_roi",
            "normalized",
            "sobel",
            "canny",
            "effective_mask",
            "glare_mask",
            "foam_mask",
        )
        for key in keys:
            self._check_cancel(cancellation)
            if key not in getattr(record, "images", {}):
                continue
            try:
                image = repository.load_image(record, key)
            except Exception as exc:
                warnings.append(f"공식 debug artifact {key}를 읽지 못했습니다: {exc}")
                continue
            if image is None:
                warnings.append(f"공식 debug artifact {key}가 없습니다.")
                continue
            path = debug_dir / f"{key}.png"
            try:
                self._write_png(path, image)
            except Exception as exc:
                warnings.append(f"공식 debug artifact {key} 저장 실패: {exc}")
                continue
            written.append(f"official_debug/{key}.png")
        return sorted(written)

    def _validate_coordinate_relationship(self, annotation, crop_origin: tuple[int, int]) -> None:
        for coordinate, label in (
            (annotation.oil_boundary, "oil"),
            (annotation.foam_front, "foam"),
        ):
            if coordinate is None:
                continue
            expected = coordinate.source_frame_y - crop_origin[1]
            if not math.isclose(expected, coordinate.roi_local_y, abs_tol=1e-9):
                raise RegressionFixtureExportError(
                    f"{annotation.annotation_id}: {label} source-frame Y와 ROI-local Y 관계가 일치하지 않습니다."
                )

    @staticmethod
    def _write_png(path: Path, image: np.ndarray) -> None:
        ok, encoded = cv2.imencode(".png", np.ascontiguousarray(image))
        if not ok:
            raise RegressionFixtureExportError(f"PNG 인코딩에 실패했습니다: {path.name}")
        encoded.tofile(str(path))

    @staticmethod
    def _check_cancel(cancellation) -> None:
        if cancellation is not None and bool(getattr(cancellation, "cancelled", False)):
            raise RegressionFixtureExportCancelled("regression fixture export가 취소되었습니다.")

    @staticmethod
    def _emit(progress, annotation, processed, total, stage, message) -> None:
        if progress is not None:
            progress(FixtureExportProgress(annotation.annotation_id, processed, total, stage, message))


def ensure_fixture_destination_safe(
    bundle_root: str | Path,
    destination: str | Path,
    *,
    active_truth_path: str | Path | None = None,
    source_video_path: str | Path | None = None,
) -> Path:
    try:
        root = Path(bundle_root).expanduser().resolve(strict=True)
    except OSError as exc:
        raise RegressionFixtureExportError("공식 결과 bundle 경로를 확인할 수 없습니다.") from exc
    candidate = Path(destination).expanduser()
    try:
        resolved = candidate.resolve(strict=False)
    except OSError as exc:
        raise RegressionFixtureExportError("fixture destination 경로를 확인할 수 없습니다.") from exc
    if resolved == root or root in resolved.parents:
        raise RegressionFixtureExportError("regression fixture dataset은 공식 결과 bundle 내부에 만들 수 없습니다.")
    if active_truth_path:
        truth_path = Path(active_truth_path).expanduser().resolve(strict=False)
        if resolved == truth_path:
            raise RegressionFixtureExportError("active .oiltruth 파일 경로를 dataset destination으로 사용할 수 없습니다.")
    if source_video_path:
        source = Path(source_video_path).expanduser().resolve(strict=True)
        if resolved == source:
            raise RegressionFixtureExportError("원본 영상 파일을 dataset destination으로 사용할 수 없습니다.")
    if candidate.exists() and not candidate.is_dir():
        raise RegressionFixtureExportError("fixture destination은 폴더여야 합니다.")
    return candidate


def _roi_crop(frame: np.ndarray, glass) -> tuple[np.ndarray, tuple[int, int]]:
    bounds = glass.geometry.ellipse.bounds
    frame_height, frame_width = frame.shape[:2]
    x0 = max(0, int(math.floor(bounds.x)))
    y0 = max(0, int(math.floor(bounds.y)))
    x1 = min(frame_width, int(math.ceil(bounds.right)))
    y1 = min(frame_height, int(math.ceil(bounds.bottom)))
    if x1 <= x0 or y1 <= y0:
        raise RegressionFixtureExportError("snapshot ROI crop이 비어 있습니다.")
    return np.ascontiguousarray(frame[y0:y1, x0:x1].copy()), (x0, y0)


def _truth_payload(annotation: UserTruthAnnotation) -> dict:
    return {
        "truth_schema_version": TRUTH_FIXTURE_SCHEMA_VERSION,
        "annotation_id": annotation.annotation_id,
        "revision": annotation.revision,
        "disposition": annotation.disposition.value,
        "glass_id": annotation.glass_id,
        "requested_timestamp_sec": annotation.requested_timestamp_sec,
        "actual_decoded_timestamp_sec": annotation.actual_decoded_timestamp_sec,
        "frame_index": annotation.frame_index,
        "fill_state": annotation.truth_fill_state.value if annotation.truth_fill_state is not None else None,
        "oil": None if annotation.oil_boundary is None else annotation.oil_boundary.to_dict(),
        "foam": None if annotation.foam_front is None else annotation.foam_front.to_dict(),
        "foam_present": annotation.foam_present,
        "error_types": [value.value for value in annotation.error_types],
        "note": annotation.note,
        "usable_numeric_truth": annotation.usable_numeric_truth,
    }


def _official_payload(annotation: UserTruthAnnotation) -> dict:
    reference = annotation.official_tracking_reference
    if reference is None:
        return {
            "official_reference": None,
            "reason": "annotation timestamp tolerance 내 공식 tracking sample이 없습니다.",
        }
    payload = reference.to_dict()
    payload["official_debug_record_id"] = annotation.official_debug_record_id
    return {"official_reference": payload, "reason": None}


def _relative_file_hashes(root: Path, *, exclude: set[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for path in sorted(root.rglob("*"), key=lambda value: value.relative_to(root).as_posix()):
        if path.is_file() and path.name not in exclude:
            output[path.relative_to(root).as_posix()] = sha256_file(path)
    return output


def _write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _jsonable(value):
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, Path):
        return str(value)
    return value


def _safe_component(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value)).strip(".-_")
    return normalized or "glass"


def _software_version() -> str:
    try:
        return version("rotary-oil-level-tracker")
    except PackageNotFoundError:
        return "0.1.0"
