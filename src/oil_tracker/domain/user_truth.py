from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Iterable
from uuid import uuid4

from oil_tracker.domain.enums import FillState


TRUTH_SCHEMA_VERSION = 1


class TruthValidationError(ValueError):
    """A user-correctable truth annotation validation error."""


class TruthDisposition(str, Enum):
    CONFIRMED_CORRECT = "confirmed_correct"
    CORRECTED = "corrected"
    UNUSABLE = "unusable"


class TruthErrorType(str, Enum):
    OIL_BOUNDARY_MISSING = "oil_boundary_missing"
    WRONG_CANDIDATE = "wrong_candidate"
    FOAM_MISCLASSIFIED = "foam_misclassified"
    GLARE_OR_REFLECTION = "glare_or_reflection"
    STRUCTURAL_EDGE = "structural_edge"
    ROI_CONFIGURATION = "roi_configuration"
    FILL_STATE_MISCLASSIFIED = "fill_state_misclassified"
    VIDEO_UNUSABLE = "video_unusable"
    OTHER = "other"


VISIBLE_INTERFACE_STATES = frozenset(
    {
        FillState.FILLING_VISIBLE,
        FillState.PARTIAL_VISIBLE,
        FillState.DRAINING_VISIBLE,
        FillState.FOAMING_VISIBLE,
    }
)
NO_INTERFACE_STATES = frozenset(
    {FillState.EMPTY_NO_INTERFACE, FillState.FULL_NO_INTERFACE}
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _finite(value: float | None, field_name: str) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise TruthValidationError(f"{field_name} 숫자 값이 올바르지 않습니다.") from exc
    if not math.isfinite(number):
        raise TruthValidationError(f"{field_name} 값은 유한한 숫자여야 합니다.")
    return number


@dataclass(frozen=True)
class TruthCoordinate:
    source_frame_y: float
    roi_local_y: float
    px_from_zero: float | None
    mm_from_zero: float | None

    def __post_init__(self) -> None:
        for field_name in ("source_frame_y", "roi_local_y", "px_from_zero", "mm_from_zero"):
            value = getattr(self, field_name)
            if value is not None and not math.isfinite(float(value)):
                raise TruthValidationError(f"{field_name} 값은 유한한 숫자여야 합니다.")

    def to_dict(self) -> dict[str, float | None]:
        return {
            "source_frame_y": self.source_frame_y,
            "roi_local_y": self.roi_local_y,
            "px_from_zero": self.px_from_zero,
            "mm_from_zero": self.mm_from_zero,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> TruthCoordinate | None:
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise TruthValidationError("truth coordinate는 JSON object여야 합니다.")
        source_y = _finite(payload.get("source_frame_y"), "source_frame_y")
        local_y = _finite(payload.get("roi_local_y"), "roi_local_y")
        if source_y is None or local_y is None:
            raise TruthValidationError("truth coordinate에는 source_frame_y와 roi_local_y가 필요합니다.")
        return cls(
            source_frame_y=source_y,
            roi_local_y=local_y,
            px_from_zero=_finite(payload.get("px_from_zero"), "px_from_zero"),
            mm_from_zero=_finite(payload.get("mm_from_zero"), "mm_from_zero"),
        )


@dataclass(frozen=True)
class TruthBundleIdentity:
    run_id: str
    recipe_id: str
    recipe_snapshot_hash: str
    source_video_basename: str
    source_width: int
    source_height: int
    source_fps: float
    source_duration_sec: float

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise TruthValidationError("bundle run ID가 비어 있습니다.")
        if not self.recipe_id.strip():
            raise TruthValidationError("recipe ID가 비어 있습니다.")
        if not self.recipe_snapshot_hash.strip():
            raise TruthValidationError("recipe snapshot hash가 비어 있습니다.")
        if self.source_width <= 0 or self.source_height <= 0:
            raise TruthValidationError("source 해상도가 올바르지 않습니다.")
        _finite(self.source_fps, "source_fps")
        _finite(self.source_duration_sec, "source_duration_sec")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "recipe_id": self.recipe_id,
            "recipe_snapshot_hash": self.recipe_snapshot_hash,
            "source_video_basename": self.source_video_basename,
            "source_width": self.source_width,
            "source_height": self.source_height,
            "source_fps": self.source_fps,
            "source_duration_sec": self.source_duration_sec,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> TruthBundleIdentity:
        if not isinstance(payload, dict):
            raise TruthValidationError("bundle_identity는 JSON object여야 합니다.")
        try:
            return cls(
                run_id=str(payload["run_id"]),
                recipe_id=str(payload["recipe_id"]),
                recipe_snapshot_hash=str(payload["recipe_snapshot_hash"]),
                source_video_basename=str(payload.get("source_video_basename", "")),
                source_width=int(payload["source_width"]),
                source_height=int(payload["source_height"]),
                source_fps=float(payload.get("source_fps", 0.0)),
                source_duration_sec=float(payload.get("source_duration_sec", 0.0)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise TruthValidationError(f"bundle identity를 읽을 수 없습니다: {exc}") from exc

    def mismatches(self, other: TruthBundleIdentity) -> tuple[str, ...]:
        mismatches: list[str] = []
        if self.run_id != other.run_id:
            mismatches.append("분석 run ID")
        if self.recipe_id != other.recipe_id:
            mismatches.append("recipe ID")
        if self.recipe_snapshot_hash != other.recipe_snapshot_hash:
            mismatches.append("recipe snapshot hash")
        if (self.source_width, self.source_height) != (other.source_width, other.source_height):
            mismatches.append("기준 영상 해상도")
        return tuple(mismatches)

    def metadata_warnings(self, other: TruthBundleIdentity) -> tuple[str, ...]:
        warnings: list[str] = []
        if self.source_video_basename and other.source_video_basename and self.source_video_basename != other.source_video_basename:
            warnings.append("원본 영상 파일명이 다릅니다.")
        if self.source_fps > 0 and other.source_fps > 0 and abs(self.source_fps - other.source_fps) > max(0.05, self.source_fps * 0.01):
            warnings.append("원본 영상 FPS가 다릅니다.")
        if self.source_duration_sec > 0 and other.source_duration_sec > 0 and abs(self.source_duration_sec - other.source_duration_sec) > max(0.25, self.source_duration_sec * 0.01):
            warnings.append("원본 영상 재생 시간이 다릅니다.")
        return tuple(warnings)


@dataclass(frozen=True)
class OfficialTrackingReference:
    sample_timestamp_sec: float
    frame_index: int
    fill_state: FillState
    oil_boundary: TruthCoordinate | None
    foam_front: TruthCoordinate | None
    confidence: float
    valid: bool
    flags: tuple[str, ...] = ()
    debug_record_id: str | None = None
    candidate_baseline_available: bool = False

    def __post_init__(self) -> None:
        _finite(self.sample_timestamp_sec, "official sample timestamp")
        _finite(self.confidence, "official confidence")

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_timestamp_sec": self.sample_timestamp_sec,
            "frame_index": self.frame_index,
            "fill_state": self.fill_state.value,
            "oil_boundary": None if self.oil_boundary is None else self.oil_boundary.to_dict(),
            "foam_front": None if self.foam_front is None else self.foam_front.to_dict(),
            "confidence": self.confidence,
            "valid": self.valid,
            "flags": list(self.flags),
            "debug_record_id": self.debug_record_id,
            "candidate_baseline_available": self.candidate_baseline_available,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> OfficialTrackingReference | None:
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise TruthValidationError("official tracking reference는 JSON object여야 합니다.")
        try:
            return cls(
                sample_timestamp_sec=float(payload["sample_timestamp_sec"]),
                frame_index=int(payload["frame_index"]),
                fill_state=FillState(str(payload["fill_state"])),
                oil_boundary=TruthCoordinate.from_dict(payload.get("oil_boundary")),
                foam_front=TruthCoordinate.from_dict(payload.get("foam_front")),
                confidence=float(payload.get("confidence", 0.0)),
                valid=bool(payload.get("valid", False)),
                flags=tuple(str(value) for value in payload.get("flags", [])),
                debug_record_id=str(payload["debug_record_id"]) if payload.get("debug_record_id") else None,
                candidate_baseline_available=bool(payload.get("candidate_baseline_available", False)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise TruthValidationError(f"official tracking reference를 읽을 수 없습니다: {exc}") from exc


@dataclass(frozen=True)
class UserTruthAnnotation:
    schema_version: int
    annotation_id: str
    annotation_set_id: str
    bundle_run_id: str
    recipe_id: str
    recipe_snapshot_hash: str
    glass_id: str
    glass_name_snapshot: str
    requested_timestamp_sec: float
    actual_decoded_timestamp_sec: float
    frame_index: int
    disposition: TruthDisposition
    truth_fill_state: FillState | None
    oil_boundary: TruthCoordinate | None
    foam_front: TruthCoordinate | None
    foam_present: bool
    error_types: tuple[TruthErrorType, ...]
    note: str
    official_tracking_reference: OfficialTrackingReference | None
    official_debug_record_id: str | None
    created_at: str
    updated_at: str
    revision: int

    @property
    def key(self) -> tuple[str, str, int | str]:
        frame_key: int | str = self.frame_index if self.frame_index >= 0 else f"{self.actual_decoded_timestamp_sec:.9f}"
        return self.bundle_run_id, self.glass_id, frame_key

    @property
    def usable_numeric_truth(self) -> bool:
        return self.disposition is not TruthDisposition.UNUSABLE and (
            self.oil_boundary is not None or self.foam_front is not None
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "annotation_id": self.annotation_id,
            "annotation_set_id": self.annotation_set_id,
            "bundle_run_id": self.bundle_run_id,
            "recipe_id": self.recipe_id,
            "recipe_snapshot_hash": self.recipe_snapshot_hash,
            "glass_id": self.glass_id,
            "glass_name_snapshot": self.glass_name_snapshot,
            "requested_timestamp_sec": self.requested_timestamp_sec,
            "actual_decoded_timestamp_sec": self.actual_decoded_timestamp_sec,
            "frame_index": self.frame_index,
            "disposition": self.disposition.value,
            "truth_fill_state": self.truth_fill_state.value if self.truth_fill_state is not None else None,
            "oil_boundary": None if self.oil_boundary is None else self.oil_boundary.to_dict(),
            "foam_front": None if self.foam_front is None else self.foam_front.to_dict(),
            "foam_present": self.foam_present,
            "error_types": [value.value for value in self.error_types],
            "note": self.note,
            "official_tracking_reference": None if self.official_tracking_reference is None else self.official_tracking_reference.to_dict(),
            "official_debug_record_id": self.official_debug_record_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> UserTruthAnnotation:
        if not isinstance(payload, dict):
            raise TruthValidationError("annotation은 JSON object여야 합니다.")
        try:
            version = int(payload.get("schema_version", -1))
            if version != TRUTH_SCHEMA_VERSION:
                raise TruthValidationError(f"지원하지 않는 annotation schema version입니다: {version}")
            raw_state = payload.get("truth_fill_state")
            return cls(
                schema_version=version,
                annotation_id=str(payload["annotation_id"]),
                annotation_set_id=str(payload["annotation_set_id"]),
                bundle_run_id=str(payload["bundle_run_id"]),
                recipe_id=str(payload["recipe_id"]),
                recipe_snapshot_hash=str(payload["recipe_snapshot_hash"]),
                glass_id=str(payload["glass_id"]),
                glass_name_snapshot=str(payload.get("glass_name_snapshot", "")),
                requested_timestamp_sec=float(payload["requested_timestamp_sec"]),
                actual_decoded_timestamp_sec=float(payload["actual_decoded_timestamp_sec"]),
                frame_index=int(payload.get("frame_index", -1)),
                disposition=TruthDisposition(str(payload["disposition"])),
                truth_fill_state=FillState(str(raw_state)) if raw_state else None,
                oil_boundary=TruthCoordinate.from_dict(payload.get("oil_boundary")),
                foam_front=TruthCoordinate.from_dict(payload.get("foam_front")),
                foam_present=bool(payload.get("foam_present", payload.get("foam_front") is not None)),
                error_types=tuple(TruthErrorType(str(value)) for value in payload.get("error_types", [])),
                note=str(payload.get("note", "")),
                official_tracking_reference=OfficialTrackingReference.from_dict(payload.get("official_tracking_reference")),
                official_debug_record_id=str(payload["official_debug_record_id"]) if payload.get("official_debug_record_id") else None,
                created_at=str(payload["created_at"]),
                updated_at=str(payload["updated_at"]),
                revision=int(payload.get("revision", 1)),
            )
        except TruthValidationError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise TruthValidationError(f"annotation을 읽을 수 없습니다: {exc}") from exc


@dataclass
class UserTruthSet:
    annotation_set_id: str
    bundle_identity: TruthBundleIdentity
    annotations: list[UserTruthAnnotation] = field(default_factory=list)
    schema_version: int = TRUTH_SCHEMA_VERSION
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    @classmethod
    def create(cls, identity: TruthBundleIdentity) -> UserTruthSet:
        return cls(annotation_set_id=str(uuid4()), bundle_identity=identity)

    def __post_init__(self) -> None:
        if self.schema_version != TRUTH_SCHEMA_VERSION:
            raise TruthValidationError(f"지원하지 않는 .oiltruth schema version입니다: {self.schema_version}")
        if not self.annotation_set_id.strip():
            raise TruthValidationError("annotation set ID가 비어 있습니다.")
        seen: set[tuple[str, str, int | str]] = set()
        for annotation in self.annotations:
            if annotation.annotation_set_id != self.annotation_set_id:
                raise TruthValidationError("annotation set ID가 annotation과 일치하지 않습니다.")
            if annotation.key in seen:
                raise TruthValidationError("동일 관찰창·frame의 annotation이 중복되어 있습니다.")
            seen.add(annotation.key)

    def sorted_annotations(self) -> tuple[UserTruthAnnotation, ...]:
        return tuple(
            sorted(
                self.annotations,
                key=lambda value: (
                    value.actual_decoded_timestamp_sec,
                    value.frame_index,
                    value.glass_id,
                    value.annotation_id,
                ),
            )
        )

    def find(self, glass_id: str, frame_index: int, actual_timestamp_sec: float | None = None) -> UserTruthAnnotation | None:
        frame_key: int | str = frame_index if frame_index >= 0 else f"{float(actual_timestamp_sec or 0.0):.9f}"
        key = (self.bundle_identity.run_id, glass_id, frame_key)
        return next((value for value in self.annotations if value.key == key), None)

    def upsert(self, annotation: UserTruthAnnotation, *, now: str | None = None) -> UserTruthAnnotation:
        if annotation.annotation_set_id != self.annotation_set_id:
            raise TruthValidationError("다른 annotation set의 정답은 저장할 수 없습니다.")
        if annotation.bundle_run_id != self.bundle_identity.run_id:
            raise TruthValidationError("다른 result run의 정답은 저장할 수 없습니다.")
        timestamp = now or utc_now_iso()
        for index, existing in enumerate(self.annotations):
            if existing.key == annotation.key:
                updated = replace(
                    annotation,
                    annotation_id=existing.annotation_id,
                    created_at=existing.created_at,
                    updated_at=timestamp,
                    revision=existing.revision + 1,
                )
                self.annotations[index] = updated
                self.updated_at = timestamp
                return updated
        created = replace(
            annotation,
            annotation_id=annotation.annotation_id or str(uuid4()),
            created_at=annotation.created_at or timestamp,
            updated_at=timestamp,
            revision=max(1, annotation.revision),
        )
        self.annotations.append(created)
        self.updated_at = timestamp
        return created

    def remove(self, annotation_id: str, *, now: str | None = None) -> bool:
        before = len(self.annotations)
        self.annotations[:] = [value for value in self.annotations if value.annotation_id != annotation_id]
        changed = len(self.annotations) != before
        if changed:
            self.updated_at = now or utc_now_iso()
        return changed

    def filtered(
        self,
        disposition: TruthDisposition | None = None,
        error_type: TruthErrorType | None = None,
    ) -> tuple[UserTruthAnnotation, ...]:
        return tuple(
            value
            for value in self.sorted_annotations()
            if (disposition is None or value.disposition is disposition)
            and (error_type is None or error_type in value.error_types)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "annotation_set_id": self.annotation_set_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "bundle_identity": self.bundle_identity.to_dict(),
            "annotations": [value.to_dict() for value in self.sorted_annotations()],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> UserTruthSet:
        if not isinstance(payload, dict):
            raise TruthValidationError(".oiltruth 최상위 값은 JSON object여야 합니다.")
        try:
            version = int(payload.get("schema_version", -1))
            if version != TRUTH_SCHEMA_VERSION:
                raise TruthValidationError(f"지원하지 않는 .oiltruth schema version입니다: {version}")
            annotations = [UserTruthAnnotation.from_dict(value) for value in payload.get("annotations", [])]
            return cls(
                annotation_set_id=str(payload["annotation_set_id"]),
                bundle_identity=TruthBundleIdentity.from_dict(payload["bundle_identity"]),
                annotations=annotations,
                schema_version=version,
                created_at=str(payload["created_at"]),
                updated_at=str(payload["updated_at"]),
            )
        except TruthValidationError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise TruthValidationError(f".oiltruth 내용을 읽을 수 없습니다: {exc}") from exc


@dataclass(frozen=True)
class TruthComparison:
    official_sample_exists: bool
    truth_disposition: TruthDisposition
    official_fill_state: FillState | None
    truth_fill_state: FillState | None
    state_matches: bool | None
    official_oil_y: float | None
    truth_oil_y: float | None
    oil_delta_px: float | None
    oil_delta_mm: float | None
    official_foam_y: float | None
    truth_foam_y: float | None
    foam_delta_px: float | None
    foam_delta_mm: float | None
    official_valid: bool | None
    error_types: tuple[TruthErrorType, ...]
    official_candidate_baseline_available: bool


def coordinate_from_source_y(source_y: float | None, glass) -> TruthCoordinate | None:
    value = _finite(source_y, "boundary Y")
    if value is None:
        return None
    ellipse = glass.geometry.ellipse
    if ellipse.horizontal_extent_at(value) is None:
        raise TruthValidationError("경계 Y가 선택 관찰창 ROI 타원 밖에 있습니다.")
    crop_origin_y = max(0, int(math.floor(ellipse.bounds.y)))
    local = value - crop_origin_y
    px = glass.geometry.level_px_from_zero(value)
    mm = glass.geometry.level_mm_from_zero(value, glass.mm_per_pixel)
    return TruthCoordinate(value, local, px, mm)


def official_reference_from_sample(
    sample,
    glass,
    *,
    debug_record_id: str | None = None,
    candidate_baseline_available: bool = False,
) -> OfficialTrackingReference:
    oil_y = sample.oil_boundary_y(glass.geometry.zero_line_y)
    foam_y = sample.foam_front_y(glass.geometry.zero_line_y)
    return OfficialTrackingReference(
        sample_timestamp_sec=float(sample.timestamp_sec),
        frame_index=int(sample.frame_index),
        fill_state=FillState(sample.fill_state),
        oil_boundary=coordinate_from_source_y(oil_y, glass) if oil_y is not None else None,
        foam_front=coordinate_from_source_y(foam_y, glass) if foam_y is not None else None,
        confidence=float(sample.overall_confidence),
        valid=bool(sample.is_valid),
        flags=tuple(str(value) for value in sample.flags),
        debug_record_id=debug_record_id,
        candidate_baseline_available=bool(candidate_baseline_available),
    )


def nearest_official_sample(samples: Iterable[Any], glass_id: str, timestamp_sec: float, tolerance_sec: float):
    candidates = [
        sample
        for sample in samples
        if sample.glass_id == glass_id and abs(float(sample.timestamp_sec) - float(timestamp_sec)) <= max(0.0, float(tolerance_sec))
    ]
    return min(
        candidates,
        key=lambda sample: (
            abs(float(sample.timestamp_sec) - float(timestamp_sec)),
            int(sample.frame_index),
            int(getattr(sample, "input_order", 0)),
        ),
        default=None,
    )


def normalized_annotation(annotation: UserTruthAnnotation) -> UserTruthAnnotation:
    if annotation.disposition is TruthDisposition.UNUSABLE:
        return replace(annotation, truth_fill_state=None, oil_boundary=None, foam_front=None, foam_present=False)
    if annotation.truth_fill_state in NO_INTERFACE_STATES:
        return replace(annotation, oil_boundary=None)
    if not annotation.foam_present:
        return replace(annotation, foam_front=None)
    return annotation


def validate_annotation(annotation: UserTruthAnnotation, glass, *, official_sample_required: bool = True) -> UserTruthAnnotation:
    annotation = normalized_annotation(annotation)
    if annotation.schema_version != TRUTH_SCHEMA_VERSION:
        raise TruthValidationError("annotation schema version이 올바르지 않습니다.")
    _finite(annotation.requested_timestamp_sec, "requested timestamp")
    _finite(annotation.actual_decoded_timestamp_sec, "actual decoded timestamp")
    if annotation.frame_index < -1:
        raise TruthValidationError("frame index가 올바르지 않습니다.")
    if annotation.disposition is TruthDisposition.CONFIRMED_CORRECT:
        if official_sample_required and annotation.official_tracking_reference is None:
            raise TruthValidationError("공식 결과가 없는 장면은 공식 결과 확인으로 저장할 수 없습니다.")
        if annotation.error_types:
            raise TruthValidationError("공식 결과 확인 정답에는 오류 유형을 저장하지 않습니다.")
        if annotation.official_tracking_reference is not None:
            reference = annotation.official_tracking_reference
            if annotation.truth_fill_state != reference.fill_state or annotation.oil_boundary != reference.oil_boundary or annotation.foam_front != reference.foam_front:
                raise TruthValidationError("공식 결과 확인 값이 official snapshot과 일치하지 않습니다.")
    elif annotation.disposition is TruthDisposition.CORRECTED:
        if annotation.truth_fill_state is None:
            raise TruthValidationError("수동 수정 정답에는 실제 fill state가 필요합니다.")
        if annotation.truth_fill_state is FillState.UNKNOWN_REVIEW:
            raise TruthValidationError("UNKNOWN_REVIEW는 수동 정답 상태로 사용할 수 없습니다. 판정 불가를 선택해 주세요.")
        if not annotation.error_types:
            raise TruthValidationError("수동 수정 정답에는 detector 오류 유형을 하나 이상 선택해야 합니다.")
        if annotation.truth_fill_state in VISIBLE_INTERFACE_STATES and annotation.oil_boundary is None:
            raise TruthValidationError("선택한 fill state에는 실제 유면 경계 Y가 필요합니다.")
        if annotation.truth_fill_state is FillState.FULL_WITH_FOAM and annotation.foam_present and annotation.foam_front is None:
            raise TruthValidationError("거품 경계가 보이는 FULL_WITH_FOAM 상태에는 foam front Y가 필요합니다.")
    else:
        if not annotation.error_types:
            raise TruthValidationError("판정 불가 정답에는 오류 유형을 하나 이상 선택해야 합니다.")
    if TruthErrorType.OTHER in annotation.error_types and not annotation.note.strip():
        raise TruthValidationError("기타 오류 유형을 선택한 경우 메모를 입력해 주세요.")
    for coordinate, label in ((annotation.oil_boundary, "유면 경계"), (annotation.foam_front, "거품 경계")):
        if coordinate is None:
            continue
        if glass.geometry.ellipse.horizontal_extent_at(coordinate.source_frame_y) is None:
            raise TruthValidationError(f"{label} Y가 선택 관찰창 ROI 타원 밖에 있습니다.")
        expected = coordinate_from_source_y(coordinate.source_frame_y, glass)
        if expected != coordinate:
            raise TruthValidationError(f"{label} 파생 좌표가 source-frame Y와 일치하지 않습니다.")
    return annotation


def confirmed_annotation(
    annotation_set_id: str,
    identity: TruthBundleIdentity,
    glass,
    requested_timestamp_sec: float,
    actual_timestamp_sec: float,
    frame_index: int,
    official_reference: OfficialTrackingReference,
    *,
    annotation_id: str = "",
    note: str = "",
    now: str | None = None,
) -> UserTruthAnnotation:
    timestamp = now or utc_now_iso()
    annotation = UserTruthAnnotation(
        schema_version=TRUTH_SCHEMA_VERSION,
        annotation_id=annotation_id or str(uuid4()),
        annotation_set_id=annotation_set_id,
        bundle_run_id=identity.run_id,
        recipe_id=identity.recipe_id,
        recipe_snapshot_hash=identity.recipe_snapshot_hash,
        glass_id=glass.id,
        glass_name_snapshot=glass.name,
        requested_timestamp_sec=float(requested_timestamp_sec),
        actual_decoded_timestamp_sec=float(actual_timestamp_sec),
        frame_index=int(frame_index),
        disposition=TruthDisposition.CONFIRMED_CORRECT,
        truth_fill_state=official_reference.fill_state,
        oil_boundary=official_reference.oil_boundary,
        foam_front=official_reference.foam_front,
        foam_present=official_reference.foam_front is not None,
        error_types=(),
        note=note,
        official_tracking_reference=OfficialTrackingReference.from_dict(official_reference.to_dict()),
        official_debug_record_id=official_reference.debug_record_id,
        created_at=timestamp,
        updated_at=timestamp,
        revision=1,
    )
    return validate_annotation(annotation, glass)


def compare_truth(annotation: UserTruthAnnotation) -> TruthComparison:
    official = annotation.official_tracking_reference
    truth_oil = annotation.oil_boundary
    truth_foam = annotation.foam_front
    return TruthComparison(
        official_sample_exists=official is not None,
        truth_disposition=annotation.disposition,
        official_fill_state=official.fill_state if official is not None else None,
        truth_fill_state=annotation.truth_fill_state,
        state_matches=(official.fill_state == annotation.truth_fill_state) if official is not None and annotation.truth_fill_state is not None else None,
        official_oil_y=official.oil_boundary.source_frame_y if official is not None and official.oil_boundary is not None else None,
        truth_oil_y=truth_oil.source_frame_y if truth_oil is not None else None,
        oil_delta_px=_coordinate_delta(truth_oil, official.oil_boundary if official is not None else None, "px_from_zero"),
        oil_delta_mm=_coordinate_delta(truth_oil, official.oil_boundary if official is not None else None, "mm_from_zero"),
        official_foam_y=official.foam_front.source_frame_y if official is not None and official.foam_front is not None else None,
        truth_foam_y=truth_foam.source_frame_y if truth_foam is not None else None,
        foam_delta_px=_coordinate_delta(truth_foam, official.foam_front if official is not None else None, "px_from_zero"),
        foam_delta_mm=_coordinate_delta(truth_foam, official.foam_front if official is not None else None, "mm_from_zero"),
        official_valid=official.valid if official is not None else None,
        error_types=annotation.error_types,
        official_candidate_baseline_available=bool(official and official.candidate_baseline_available),
    )


def _coordinate_delta(left: TruthCoordinate | None, right: TruthCoordinate | None, field_name: str) -> float | None:
    if left is None or right is None:
        return None
    left_value = getattr(left, field_name)
    right_value = getattr(right, field_name)
    return None if left_value is None or right_value is None else float(left_value) - float(right_value)
