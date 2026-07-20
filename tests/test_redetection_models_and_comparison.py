from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from oil_tracker.application.services.detector_settings import (
    clone_detector_settings,
    compare_detector_settings,
    detector_setting_fields,
    detector_settings_from_json,
    detector_settings_to_json,
    update_detector_setting,
    validate_detector_settings,
)
from oil_tracker.application.services.redetection_apply import (
    DetectorSettingsApplyScope,
    apply_detector_settings,
    check_workbench_compatibility,
    create_profile_from_snapshot,
    ensure_profile_destination_outside_bundle,
)
from oil_tracker.application.services.redetection_comparison import (
    align_redetection_samples,
    compare_events,
    summarize_comparison,
)
from oil_tracker.application.services.redetection_request import (
    RedetectionRequestError,
    build_redetection_range,
    build_redetection_request,
    redetection_schedule,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState, WorkbenchState
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.domain.redetection import RedetectionMode, RedetectionPolicy, RedetectionSample
from oil_tracker.domain.results import EventMarker, TrackingSample
from oil_tracker.domain.review import ReviewBundle, ReviewEvent, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


def _bundle(tmp_path: Path, *, fps: float = 2.0) -> ReviewBundle:
    recipe = InspectionRecipe.empty(320, 240, "fixture")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "glass-1"
    glass.name = "Glass 1"
    glass.mm_per_pixel = 0.25
    recipe.glasses = [glass]
    metadata = VideoMetadata("source.mp4", 320, 240, 30.0, 10.0, 300)
    session = AnalysisSession(
        input_video_path="source.mp4",
        video_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=9.0,
        compressor_start_sec=2.0,
        sampling_fps=fps,
    )
    samples = tuple(_official_sample(index, 1.0 + index / fps) for index in range(int(8 * fps) + 1))
    return ReviewBundle(
        root=tmp_path,
        run_id="official-run",
        recipe=recipe,
        session=session,
        manifest={},
        source_video_path="source.mp4",
        source_video_candidates=(),
        source_metadata=metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=9.0,
        compressor_start_sec=2.0,
        glasses=(ReviewGlass("glass-1", "Glass 1", ResultState.PASS),),
        samples=samples,
        events=(),
    )


def _official_sample(index: int, timestamp: float, **overrides) -> ReviewTrackingSample:
    values = dict(
        run_id="official-run",
        glass_id="glass-1",
        frame_index=index,
        timestamp_sec=timestamp,
        fill_state=FillState.VISIBLE_INTERFACE,
        raw_oil_air_level_y=120.0,
        raw_oil_air_level_px_from_zero=10.0,
        raw_oil_air_level_mm_from_zero=2.5,
        smoothed_oil_air_level_px_from_zero=11.0,
        smoothed_oil_air_level_mm_from_zero=2.75,
        oil_air_confidence=0.8,
        raw_foam_front_y=100.0,
        raw_foam_front_px_from_zero=30.0,
        raw_foam_front_mm_from_zero=7.5,
        smoothed_foam_front_px_from_zero=29.0,
        smoothed_foam_front_mm_from_zero=7.25,
        foam_confidence=0.7,
        visibility_confidence=0.9,
        overall_confidence=0.8,
        is_valid=True,
        flags=(),
        input_order=index,
    )
    values.update(overrides)
    return ReviewTrackingSample(**values)


def _tracking(index: int, timestamp: float, **overrides) -> TrackingSample:
    values = dict(
        run_id="rerun",
        glass_id="glass-1",
        frame_index=index,
        timestamp_sec=timestamp,
        fill_state=FillState.VISIBLE_INTERFACE,
        raw_oil_air_level_y=118.0,
        raw_oil_air_level_px_from_zero=12.0,
        raw_oil_air_level_mm_from_zero=3.0,
        smoothed_oil_air_level_px_from_zero=13.0,
        smoothed_oil_air_level_mm_from_zero=3.25,
        oil_air_confidence=0.85,
        raw_foam_front_y=98.0,
        raw_foam_front_px_from_zero=32.0,
        raw_foam_front_mm_from_zero=8.0,
        smoothed_foam_front_px_from_zero=31.0,
        smoothed_foam_front_mm_from_zero=7.75,
        foam_confidence=0.75,
        visibility_confidence=0.9,
        overall_confidence=0.9,
        is_valid=True,
        flags=[],
    )
    values.update(overrides)
    return TrackingSample(**values)


def _rerun_sample(nominal: float, actual: float | None = None, **tracking_overrides) -> RedetectionSample:
    actual = nominal if actual is None else actual
    tracking = _tracking(int(round(actual * 10)), actual, **tracking_overrides)
    return RedetectionSample(
        nominal_timestamp_sec=nominal,
        requested_timestamp_sec=nominal,
        actual_timestamp_sec=actual,
        frame_index=tracking.frame_index,
        tracking_sample=tracking,
        fill_state=tracking.fill_state,
        confidence=tracking.overall_confidence,
        is_valid=tracking.is_valid,
        flags=tuple(tracking.flags),
        selected_candidate=None,
        debug_record_id="record",
    )


def test_all_detector_settings_fields_have_editor_metadata():
    assert {item.name for item in detector_setting_fields()} == DetectorSettings.__dataclass_fields__.keys()


def test_detector_settings_clone_and_json_are_deep_and_stable():
    original = DetectorSettings()
    cloned = clone_detector_settings(original)
    cloned.canny_low = 12
    assert original.canny_low == 45
    assert detector_settings_from_json(detector_settings_to_json(original)) == original


def test_detector_settings_diff_noop_and_changed_category():
    baseline = DetectorSettings()
    temporary = update_detector_setting(baseline, "weight_edge", 0.33)
    diffs = compare_detector_settings(baseline, temporary)
    changed = [item for item in diffs if item.changed]
    assert len(changed) == 1
    assert changed[0].field_name == "weight_edge"
    assert changed[0].category == "score_weight"
    assert changed[0].numeric_delta == pytest.approx(0.11)
    assert not any(item.changed for item in compare_detector_settings(baseline, baseline))


@pytest.mark.parametrize(
    ("settings", "field"),
    [
        (DetectorSettings(canny_low=200, canny_high=100), "canny_high"),
        (DetectorSettings(minimum_final_confidence=1.1), "minimum_final_confidence"),
        (DetectorSettings(smoothing_window=0), "smoothing_window"),
        (DetectorSettings(weight_edge=float("nan")), "weight_edge"),
    ],
)
def test_detector_settings_validation(settings, field):
    assert field in validate_detector_settings(settings)


def test_current_range_and_schedule_have_one_sample(tmp_path):
    bundle = _bundle(tmp_path)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        4.125,
        RedetectionMode.CURRENT,
        bundle.recipe.glasses[0].detector_settings,
        1,
    )
    assert redetection_schedule(request) == ((4.125, False),)


def test_short_range_clamps_and_hides_warmup(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        1.5,
        RedetectionMode.SHORT,
        bundle.recipe.glasses[0].detector_settings,
        1,
        before_sec=2.0,
        after_sec=2.0,
    )
    assert request.requested_range.display_start_sec == 1.0
    assert request.requested_range.display_end_sec == 3.5
    assert request.requested_range.warmup_start_sec == 1.0
    schedule = redetection_schedule(request)
    assert schedule[0] == (1.0, False)
    assert schedule[-1] == (3.5, False)


def test_short_range_includes_warmup_only_before_display(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        5.0,
        RedetectionMode.SHORT,
        bundle.recipe.glasses[0].detector_settings,
        2,
    )
    schedule = redetection_schedule(request)
    warmups = [timestamp for timestamp, warmup in schedule if warmup]
    visible = [timestamp for timestamp, warmup in schedule if not warmup]
    assert warmups == [1.0, 1.5, 2.0, 2.5]
    assert visible[0] == 3.0
    assert visible[-1] == 7.0


def test_short_range_max_duration_is_named_policy(tmp_path):
    bundle = _bundle(tmp_path)
    with pytest.raises(RedetectionRequestError):
        build_redetection_range(
            bundle,
            5.0,
            RedetectionMode.SHORT,
            before_sec=16,
            after_sec=15,
            policy=RedetectionPolicy(short_max_display_duration_sec=30),
        )


def test_full_schedule_preserves_analysis_boundaries_and_fps(tmp_path):
    bundle = _bundle(tmp_path, fps=2.0)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        4.0,
        RedetectionMode.FULL,
        bundle.recipe.glasses[0].detector_settings,
        3,
    )
    schedule = redetection_schedule(request)
    assert schedule[0] == (1.0, False)
    assert schedule[-1] == (9.0, False)
    assert len(schedule) == 17
    assert [timestamp for timestamp, _ in schedule] == sorted({timestamp for timestamp, _ in schedule})


def test_request_snapshots_do_not_alias_ui_objects(tmp_path):
    bundle = _bundle(tmp_path)
    settings = deepcopy(bundle.recipe.glasses[0].detector_settings)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        4.0,
        RedetectionMode.CURRENT,
        settings,
        7,
    )
    settings.canny_low = 1
    bundle.recipe.glasses[0].detector_settings.canny_low = 2
    assert detector_settings_from_json(request.detector_settings_json).canny_low == 45


def test_alignment_exact_nominal_and_no_interpolation(tmp_path):
    bundle = _bundle(tmp_path)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        2.0,
        RedetectionMode.SHORT,
        DetectorSettings(),
        1,
        before_sec=0.5,
        after_sec=0.5,
    )
    official = (_official_sample(1, 1.5), _official_sample(2, 2.0), _official_sample(3, 2.5))
    rerun = (_rerun_sample(2.0, 2.02),)
    points = align_redetection_samples(request, official, rerun, 2.0)
    matched = [point for point in points if point.match_status == "matched"]
    assert len(matched) == 1
    assert matched[0].official_timestamp_sec == 2.0
    assert matched[0].rerun_actual_timestamp_sec == 2.02
    assert matched[0].oil_position_delta_px == pytest.approx(2.0)


def test_current_alignment_uses_actual_timestamp_and_tolerance(tmp_path):
    bundle = _bundle(tmp_path, fps=10.0)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        2.0,
        RedetectionMode.CURRENT,
        DetectorSettings(),
        1,
    )
    official = (_official_sample(1, 2.0), _official_sample(2, 2.1))
    points = align_redetection_samples(request, official, (_rerun_sample(2.0, 2.09),), 10.0)
    assert points[0].official_timestamp_sec == 2.1
    far = align_redetection_samples(request, official, (_rerun_sample(2.0, 2.30),), 10.0)
    assert far[0].official_sample is None
    assert far[0].match_status == "rerun_only"


def test_duplicate_official_timestamp_is_deterministic(tmp_path):
    bundle = _bundle(tmp_path)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        2.0,
        RedetectionMode.SHORT,
        DetectorSettings(),
        1,
        before_sec=0,
        after_sec=0.5,
    )
    official = (
        _official_sample(9, 2.0, input_order=2),
        _official_sample(3, 2.0, input_order=8),
    )
    point = align_redetection_samples(request, official, (_rerun_sample(2.0),), 2.0)[0]
    assert point.official_sample.frame_index == 3


def test_comparison_flags_state_valid_and_nan_safe(tmp_path):
    bundle = _bundle(tmp_path)
    request = build_redetection_request(
        bundle,
        "source.mp4",
        "glass-1",
        2.0,
        RedetectionMode.CURRENT,
        DetectorSettings(),
        1,
    )
    official = (_official_sample(1, 2.0, flags=("A",), overall_confidence=float("nan")),)
    rerun = (
        _rerun_sample(
            2.0,
            flags=["B"],
            fill_state=FillState.UNKNOWN_REVIEW,
            is_valid=False,
        ),
    )
    point = align_redetection_samples(request, official, rerun, 2.0)[0]
    assert point.fill_state_same is False
    assert point.validity_same is False
    assert point.flags_added == ("B",)
    assert point.flags_removed == ("A",)
    assert point.confidence_delta is None


def test_event_matching_is_deterministic_added_removed_shifted():
    official = (
        ReviewEvent("run", "glass-1", EventType.OIL_LEVEL_MINIMUM, 2.0),
        ReviewEvent("run", "glass-1", EventType.FOAM_FRONT_MAXIMUM, 5.0),
    )
    rerun = (
        EventMarker("rerun", "glass-1", EventType.OIL_LEVEL_MINIMUM, 2.2),
        EventMarker("rerun", "glass-1", EventType.GLARE_OR_FOG, 7.0),
    )
    compared = compare_events(official, rerun, 2.0)
    assert {item.status for item in compared} == {"shifted", "removed", "added"}


def test_summary_aggregates_changes():
    point = align_redetection_samples(
        type("Request", (), {
            "selected_glass_id": "glass-1",
            "mode": RedetectionMode.CURRENT,
            "requested_range": type("Range", (), {"display_start_sec": 0.0, "display_end_sec": 10.0})(),
        })(),
        (_official_sample(1, 2.0),),
        (_rerun_sample(2.0, fill_state=FillState.UNKNOWN_REVIEW, is_valid=False),),
        2.0,
    )
    summary = summarize_comparison(point, official_judgment=ResultState.PASS, rerun_judgment=ResultState.FAIL)
    assert summary.matched_count == 1
    assert summary.fill_state_change_count == 1
    assert summary.validity_change_count == 1
    assert summary.judgment_changed


def test_apply_selected_and_all_are_deep_and_noop_aware(tmp_path):
    bundle = _bundle(tmp_path)
    recipe = InspectionRecipe.from_dict(bundle.recipe.to_dict())
    second = InspectionRecipe.default_glass(320, 240, 2)
    second.id = "glass-2"
    second.enabled = False
    recipe.glasses.append(second)
    settings = DetectorSettings(canny_low=10)
    selected = apply_detector_settings(recipe, "glass-1", settings, DetectorSettingsApplyScope.SELECTED)
    assert selected.changed_glass_ids == ("glass-1",)
    assert recipe.glasses[1].detector_settings.canny_low == 45
    all_result = apply_detector_settings(recipe, "glass-1", settings, DetectorSettingsApplyScope.ALL)
    assert all_result.changed_glass_ids == ("glass-2",)
    settings.canny_low = 99
    assert all(glass.detector_settings.canny_low == 10 for glass in recipe.glasses)
    assert apply_detector_settings(recipe, "glass-1", DetectorSettings(canny_low=10), DetectorSettingsApplyScope.ALL).is_no_op


def test_workbench_compatibility_reports_each_contract(tmp_path):
    bundle = _bundle(tmp_path)
    same = InspectionRecipe.from_dict(bundle.recipe.to_dict())
    assert check_workbench_compatibility(same, WorkbenchState.DRAFT, bundle.recipe, "glass-1", DetectorSettingsApplyScope.SELECTED).compatible
    mismatched = InspectionRecipe.from_dict(bundle.recipe.to_dict())
    mismatched.recipe_id = "other"
    mismatched.reference_frame_width += 1
    mismatched.glasses.clear()
    result = check_workbench_compatibility(mismatched, WorkbenchState.ANALYZING, bundle.recipe, "glass-1", DetectorSettingsApplyScope.SELECTED)
    assert not result.compatible
    assert len(result.reasons) == 4


def test_new_profile_has_new_identity_timestamps_and_no_alias(tmp_path):
    bundle = _bundle(tmp_path)
    snapshot = bundle.recipe
    created = create_profile_from_snapshot(
        snapshot,
        "glass-1",
        DetectorSettings(canny_low=11),
        DetectorSettingsApplyScope.SELECTED,
    )
    assert created.recipe_id != snapshot.recipe_id
    assert created.created_at == created.updated_at
    assert created.schema_version == snapshot.schema_version
    assert created.name.endswith(" - 재검출 설정")
    created.glasses[0].detector_settings.canny_low = 77
    assert snapshot.glasses[0].detector_settings.canny_low == 45


def test_profile_destination_rejects_bundle_and_symlink_alias(tmp_path):
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    assert ensure_profile_destination_outside_bundle(bundle_root, outside / "새 프로필").suffix == ".oilrecipe"
    with pytest.raises(ValueError):
        ensure_profile_destination_outside_bundle(bundle_root, bundle_root / "profile")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(bundle_root, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(ValueError):
        ensure_profile_destination_outside_bundle(bundle_root, alias / "profile.oilrecipe")
