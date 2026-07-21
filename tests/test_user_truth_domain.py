from __future__ import annotations

from dataclasses import replace
import math

import pytest

from oil_tracker.adapters.storage.json_truth_repository import build_truth_bundle_identity
from oil_tracker.application.services.user_truth import TruthFrameContext, UserTruthService
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import (
    OfficialTrackingReference,
    TruthBundleIdentity,
    TruthCoordinate,
    TruthDisposition,
    TruthErrorType,
    TruthValidationError,
    UserTruthAnnotation,
    UserTruthSet,
    compare_truth,
    coordinate_from_source_y,
    nearest_official_sample,
)
from user_truth_fixtures import make_truth_bundle, make_truth_set_and_annotation


def test_truth_enum_contract_is_machine_readable():
    assert [value.value for value in TruthDisposition] == [
        "confirmed_correct",
        "corrected",
        "unusable",
    ]
    assert {value.value for value in TruthErrorType} == {
        "oil_boundary_missing",
        "wrong_candidate",
        "foam_misclassified",
        "glare_or_reflection",
        "structural_edge",
        "roi_configuration",
        "fill_state_misclassified",
        "video_unusable",
        "other",
    }


def test_coordinate_uses_source_frame_and_integer_roi_crop_origin(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    y = glass.geometry.ellipse.center_y
    coordinate = coordinate_from_source_y(y, glass)
    expected_origin = max(0, math.floor(glass.geometry.ellipse.bounds.y))
    assert coordinate.source_frame_y == y
    assert coordinate.roi_local_y == y - expected_origin
    assert coordinate.px_from_zero == glass.geometry.zero_line_y - y
    assert coordinate.mm_from_zero == coordinate.px_from_zero * glass.mm_per_pixel


def test_coordinate_mm_is_none_without_calibration(tmp_path):
    bundle = make_truth_bundle(tmp_path, mm_per_pixel=None)
    coordinate = coordinate_from_source_y(130.0, bundle.recipe.glasses[0])
    assert coordinate.px_from_zero == 20.0
    assert coordinate.mm_from_zero is None


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_coordinate_rejects_non_finite_values(value):
    with pytest.raises(TruthValidationError):
        TruthCoordinate(value, 1.0, 2.0, None)


def test_coordinate_from_dict_requires_authoritative_and_local_y():
    with pytest.raises(TruthValidationError):
        TruthCoordinate.from_dict({"px_from_zero": 1.0})


def test_bundle_identity_strict_mismatch_and_metadata_warning(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    identity = build_truth_bundle_identity(bundle)
    strict = replace(identity, run_id="other", source_width=640)
    warning = replace(identity, source_video_basename="renamed.mp4", source_fps=29.0)
    assert identity.mismatches(strict) == ("분석 run ID", "기준 영상 해상도")
    assert identity.mismatches(warning) == ()
    assert identity.metadata_warnings(warning) == (
        "원본 영상 파일명이 다릅니다.",
        "원본 영상 FPS가 다릅니다.",
    )


def test_nearest_official_sample_is_tolerance_bounded_and_deterministic(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    sample = bundle.samples[0]
    duplicate_high_frame = replace(sample, frame_index=61, input_order=0)
    duplicate_low_frame = replace(sample, frame_index=59, input_order=9)
    selected = nearest_official_sample(
        (duplicate_high_frame, duplicate_low_frame, sample),
        "glass-1",
        2.0,
        0.1,
    )
    assert selected.frame_index == 59
    assert nearest_official_sample(bundle.samples, "glass-1", 2.2, 0.1) is None
    assert nearest_official_sample(bundle.samples, "other", 2.0, 1.0) is None


def test_confirmed_correct_requires_explicit_official_snapshot_and_deep_copy(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    glass = bundle.recipe.glasses[0]
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    official = service.official_reference(bundle, glass, 2.0)
    annotation = service.make_annotation(
        truth_set,
        identity,
        glass,
        context,
        TruthDisposition.CONFIRMED_CORRECT,
        official_reference=official,
    )
    assert annotation.truth_fill_state is official.fill_state
    assert annotation.error_types == ()
    assert annotation.official_tracking_reference == official
    assert annotation.official_tracking_reference is not official
    assert annotation.oil_boundary is not official.oil_boundary
    with pytest.raises(TruthValidationError, match="공식"):
        service.make_annotation(
            truth_set,
            identity,
            glass,
            context,
            TruthDisposition.CONFIRMED_CORRECT,
            official_reference=None,
        )


def test_corrected_visible_state_requires_oil_boundary(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    with pytest.raises(TruthValidationError, match="유면 경계"):
        service.make_annotation(
            truth_set,
            identity,
            bundle.recipe.glasses[0],
            context,
            TruthDisposition.CORRECTED,
            truth_fill_state=FillState.PARTIAL_VISIBLE,
            error_types=(TruthErrorType.OIL_BOUNDARY_MISSING,),
        )


@pytest.mark.parametrize("state", [FillState.EMPTY_NO_INTERFACE, FillState.FULL_NO_INTERFACE])
def test_no_interface_state_explicitly_removes_previous_oil_line(tmp_path, state):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    annotation = service.make_annotation(
        truth_set,
        identity,
        bundle.recipe.glasses[0],
        TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60),
        TruthDisposition.CORRECTED,
        truth_fill_state=state,
        oil_source_y=130.0,
        error_types=(TruthErrorType.FILL_STATE_MISCLASSIFIED,),
    )
    assert annotation.oil_boundary is None


def test_full_with_foam_requires_line_only_when_foam_is_marked_present(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    truth_set = service.create_set(identity)
    glass = bundle.recipe.glasses[0]
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    with pytest.raises(TruthValidationError, match="foam front"):
        service.make_annotation(
            truth_set,
            identity,
            glass,
            context,
            TruthDisposition.CORRECTED,
            truth_fill_state=FillState.FULL_WITH_FOAM,
            foam_present=True,
            error_types=(TruthErrorType.FOAM_MISCLASSIFIED,),
        )
    annotation = service.make_annotation(
        truth_set,
        identity,
        glass,
        context,
        TruthDisposition.CORRECTED,
        truth_fill_state=FillState.FULL_WITH_FOAM,
        foam_present=False,
        error_types=(TruthErrorType.FOAM_MISCLASSIFIED,),
    )
    assert annotation.foam_front is None


def test_unknown_review_is_not_accepted_as_corrected_truth(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    with pytest.raises(TruthValidationError, match="UNKNOWN_REVIEW"):
        service.make_annotation(
            service.create_set(identity),
            identity,
            bundle.recipe.glasses[0],
            TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60),
            TruthDisposition.CORRECTED,
            truth_fill_state=FillState.UNKNOWN_REVIEW,
            oil_source_y=130.0,
            error_types=(TruthErrorType.FILL_STATE_MISCLASSIFIED,),
        )


def test_corrected_and_unusable_require_error_type(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    for disposition in (TruthDisposition.CORRECTED, TruthDisposition.UNUSABLE):
        with pytest.raises(TruthValidationError, match="오류 유형"):
            service.make_annotation(
                service.create_set(identity),
                identity,
                bundle.recipe.glasses[0],
                context,
                disposition,
                truth_fill_state=FillState.PARTIAL_VISIBLE,
                oil_source_y=130.0,
            )


def test_unusable_clears_numeric_truth_and_other_requires_note(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    service = UserTruthService()
    identity = build_truth_bundle_identity(bundle)
    context = TruthFrameContext("glass-1", "관찰창 1", 2.0, 2.0, 60)
    annotation = service.make_annotation(
        service.create_set(identity),
        identity,
        bundle.recipe.glasses[0],
        context,
        TruthDisposition.UNUSABLE,
        truth_fill_state=FillState.PARTIAL_VISIBLE,
        oil_source_y=130.0,
        foam_present=True,
        foam_source_y=120.0,
        error_types=(TruthErrorType.VIDEO_UNUSABLE,),
    )
    assert annotation.truth_fill_state is None
    assert annotation.oil_boundary is None
    assert annotation.foam_front is None
    assert not annotation.usable_numeric_truth
    with pytest.raises(TruthValidationError, match="메모"):
        service.make_annotation(
            service.create_set(identity),
            identity,
            bundle.recipe.glasses[0],
            context,
            TruthDisposition.UNUSABLE,
            error_types=(TruthErrorType.OTHER,),
        )


def test_outside_ellipse_coordinates_are_rejected_without_hidden_clamp(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    with pytest.raises(TruthValidationError, match="타원 밖"):
        coordinate_from_source_y(glass.geometry.ellipse.bounds.y - 0.01, glass)


def test_same_frame_upsert_preserves_id_and_created_time_and_increments_revision(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, service = make_truth_set_and_annotation(bundle)
    original_id = annotation.annotation_id
    original_created = annotation.created_at
    changed = replace(annotation, note="수정", updated_at="later")
    updated = truth_set.upsert(changed, now="2026-07-21T10:00:00+00:00")
    assert len(truth_set.annotations) == 1
    assert updated.annotation_id == original_id
    assert updated.created_at == original_created
    assert updated.updated_at == "2026-07-21T10:00:00+00:00"
    assert updated.revision == annotation.revision + 1


def test_duplicate_annotation_key_is_rejected_on_load(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    payload = truth_set.to_dict()
    payload["annotations"].append(annotation.to_dict())
    with pytest.raises(TruthValidationError, match="중복"):
        UserTruthSet.from_dict(payload)


def test_truth_set_sort_filter_remove_and_timestamp_fallback(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    fallback = replace(
        annotation,
        annotation_id="fallback",
        frame_index=-1,
        actual_decoded_timestamp_sec=1.25,
        disposition=TruthDisposition.UNUSABLE,
        truth_fill_state=None,
        oil_boundary=None,
        foam_front=None,
        foam_present=False,
        error_types=(TruthErrorType.VIDEO_UNUSABLE,),
    )
    truth_set.upsert(fallback)
    assert [value.annotation_id for value in truth_set.sorted_annotations()] == ["fallback", annotation.annotation_id]
    assert truth_set.find("glass-1", -1, 1.25).annotation_id == "fallback"
    assert truth_set.filtered(TruthDisposition.UNUSABLE) == (truth_set.find("glass-1", -1, 1.25),)
    assert truth_set.remove("fallback")
    assert not truth_set.remove("missing")


def test_truth_comparison_reports_state_and_coordinate_deltas(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    _truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    comparison = compare_truth(annotation)
    assert comparison.official_sample_exists
    assert comparison.state_matches is True
    assert comparison.official_oil_y == 130.0
    assert comparison.truth_oil_y == 128.0
    assert comparison.oil_delta_px == 2.0
    assert comparison.oil_delta_mm == 0.5
    assert comparison.official_foam_y == 120.0
    assert comparison.truth_foam_y == 118.0
    assert comparison.foam_delta_px == 2.0
    assert comparison.foam_delta_mm == 0.5
    assert comparison.official_valid is True
    assert not comparison.official_candidate_baseline_available


def test_truth_comparison_does_not_interpolate_or_invent_missing_official(tmp_path):
    bundle = make_truth_bundle(tmp_path)
    _truth_set, annotation, _service = make_truth_set_and_annotation(bundle)
    annotation = replace(annotation, official_tracking_reference=None)
    comparison = compare_truth(annotation)
    assert not comparison.official_sample_exists
    assert comparison.state_matches is None
    assert comparison.official_oil_y is None
    assert comparison.oil_delta_px is None
    assert comparison.official_valid is None
