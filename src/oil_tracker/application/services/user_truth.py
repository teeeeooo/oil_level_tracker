from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable
from uuid import uuid4

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.redetection import RedetectionPolicy
from oil_tracker.domain.user_truth import (
    TRUTH_SCHEMA_VERSION,
    OfficialTrackingReference,
    TruthBundleIdentity,
    TruthCoordinate,
    TruthDisposition,
    TruthErrorType,
    TruthValidationError,
    UserTruthAnnotation,
    UserTruthSet,
    coordinate_from_source_y,
    nearest_official_sample,
    official_reference_from_sample,
    utc_now_iso,
    validate_annotation,
)


class TruthSessionStatus(str, Enum):
    NONE = "none"
    NEW = "new"
    SAVED = "saved"
    MODIFIED = "modified"
    SAVING = "saving"
    SAVE_FAILED = "save_failed"
    IDENTITY_MISMATCH = "identity_mismatch"


@dataclass(frozen=True)
class TruthFrameContext:
    glass_id: str
    glass_name: str
    requested_timestamp_sec: float
    actual_decoded_timestamp_sec: float
    frame_index: int


@dataclass
class TruthSession:
    truth_set: UserTruthSet | None = None
    path: object | None = None
    status: TruthSessionStatus = TruthSessionStatus.NONE
    dirty: bool = False

    def attach_new(self, truth_set: UserTruthSet) -> None:
        self.truth_set = truth_set
        self.path = None
        self.status = TruthSessionStatus.NEW
        self.dirty = False

    def attach_loaded(self, truth_set: UserTruthSet, path) -> None:
        self.truth_set = truth_set
        self.path = path
        self.status = TruthSessionStatus.SAVED
        self.dirty = False

    def mark_dirty(self) -> None:
        if self.truth_set is not None:
            self.dirty = True
            self.status = TruthSessionStatus.MODIFIED

    def mark_saving(self) -> None:
        self.status = TruthSessionStatus.SAVING

    def mark_saved(self, path) -> None:
        self.path = path
        self.dirty = False
        self.status = TruthSessionStatus.SAVED

    def mark_failed(self) -> None:
        self.status = TruthSessionStatus.SAVE_FAILED
        self.dirty = True

    def clear(self) -> None:
        self.truth_set = None
        self.path = None
        self.status = TruthSessionStatus.NONE
        self.dirty = False


class UserTruthService:
    def __init__(self, policy: RedetectionPolicy | None = None) -> None:
        self.policy = policy or RedetectionPolicy()

    def create_set(self, identity: TruthBundleIdentity) -> UserTruthSet:
        return UserTruthSet.create(identity)

    def official_reference(
        self,
        bundle,
        glass,
        timestamp_sec: float,
        *,
        debug_repository=None,
    ) -> OfficialTrackingReference | None:
        tolerance = self.policy.alignment_tolerance(bundle.session.sampling_fps)
        sample = nearest_official_sample(bundle.samples, glass.id, timestamp_sec, tolerance)
        if sample is None:
            return None
        debug_record_id = None
        candidate_available = False
        if debug_repository is not None:
            summary = debug_repository.nearest(glass.id, sample.timestamp_sec, tolerance)
            if summary is not None:
                debug_record_id = summary.record_id
                candidate_available = True
        return official_reference_from_sample(
            sample,
            glass,
            debug_record_id=debug_record_id,
            candidate_baseline_available=candidate_available,
        )

    def make_annotation(
        self,
        truth_set: UserTruthSet,
        identity: TruthBundleIdentity,
        glass,
        context: TruthFrameContext,
        disposition: TruthDisposition,
        *,
        truth_fill_state: FillState | None = None,
        oil_source_y: float | None = None,
        foam_present: bool = False,
        foam_source_y: float | None = None,
        error_types: Iterable[TruthErrorType] = (),
        note: str = "",
        official_reference: OfficialTrackingReference | None = None,
        existing_annotation: UserTruthAnnotation | None = None,
        now: str | None = None,
    ) -> UserTruthAnnotation:
        timestamp = now or utc_now_iso()
        if identity.mismatches(truth_set.bundle_identity):
            raise TruthValidationError("현재 result bundle과 사용자 정답 세트 identity가 일치하지 않습니다.")
        if disposition is TruthDisposition.CONFIRMED_CORRECT:
            if official_reference is None:
                raise TruthValidationError("현재 장면에 확인할 공식 tracking sample이 없습니다.")
            truth_fill_state = official_reference.fill_state
            oil = _copy_coordinate(official_reference.oil_boundary)
            foam = _copy_coordinate(official_reference.foam_front)
            foam_present = foam is not None
            normalized_errors: tuple[TruthErrorType, ...] = ()
        elif disposition is TruthDisposition.UNUSABLE:
            truth_fill_state = None
            oil = None
            foam = None
            foam_present = False
            normalized_errors = _unique_errors(error_types)
        else:
            oil = coordinate_from_source_y(oil_source_y, glass) if oil_source_y is not None else None
            foam = coordinate_from_source_y(foam_source_y, glass) if foam_present and foam_source_y is not None else None
            normalized_errors = _unique_errors(error_types)
        created_at = existing_annotation.created_at if existing_annotation is not None else timestamp
        revision = existing_annotation.revision if existing_annotation is not None else 1
        annotation = UserTruthAnnotation(
            schema_version=TRUTH_SCHEMA_VERSION,
            annotation_id=existing_annotation.annotation_id if existing_annotation is not None else str(uuid4()),
            annotation_set_id=truth_set.annotation_set_id,
            bundle_run_id=identity.run_id,
            recipe_id=identity.recipe_id,
            recipe_snapshot_hash=identity.recipe_snapshot_hash,
            glass_id=glass.id,
            glass_name_snapshot=glass.name,
            requested_timestamp_sec=float(context.requested_timestamp_sec),
            actual_decoded_timestamp_sec=float(context.actual_decoded_timestamp_sec),
            frame_index=int(context.frame_index),
            disposition=disposition,
            truth_fill_state=truth_fill_state,
            oil_boundary=oil,
            foam_front=foam,
            foam_present=bool(foam_present),
            error_types=normalized_errors,
            note=str(note),
            official_tracking_reference=_copy_reference(official_reference),
            official_debug_record_id=official_reference.debug_record_id if official_reference is not None else None,
            created_at=created_at,
            updated_at=timestamp,
            revision=revision,
        )
        return validate_annotation(annotation, glass)


def _unique_errors(values: Iterable[TruthErrorType]) -> tuple[TruthErrorType, ...]:
    normalized = {value if isinstance(value, TruthErrorType) else TruthErrorType(str(value)) for value in values}
    return tuple(sorted(normalized, key=lambda value: value.value))


def _copy_coordinate(value: TruthCoordinate | None) -> TruthCoordinate | None:
    return None if value is None else TruthCoordinate.from_dict(value.to_dict())


def _copy_reference(value: OfficialTrackingReference | None) -> OfficialTrackingReference | None:
    return None if value is None else OfficialTrackingReference.from_dict(value.to_dict())
