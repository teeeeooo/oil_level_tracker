from __future__ import annotations

from copy import deepcopy
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
from oil_tracker.application.services.redetection_request import (
    RedetectionRequestError,
    build_redetection_range,
    build_redetection_request,
    redetection_schedule,
)
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.domain.redetection import RedetectionMode, RedetectionPolicy
from redetection_fixtures import make_bundle


def test_every_detector_setting_has_editor_metadata():
    assert {item.name for item in detector_setting_fields()} == set(DetectorSettings.__dataclass_fields__)


def test_detector_setting_snapshot_is_deep_and_stable():
    original = DetectorSettings()
    cloned = clone_detector_settings(original)
    cloned.canny_low = 1
    assert original.canny_low == 45
    assert detector_settings_from_json(detector_settings_to_json(original)) == original


def test_setting_diff_reports_one_machine_field_and_category():
    baseline = DetectorSettings()
    temporary = update_detector_setting(baseline, "weight_edge", 0.33)
    changed = [item for item in compare_detector_settings(baseline, temporary) if item.changed]
    assert [(item.field_name, item.category) for item in changed] == [("weight_edge", "score_weight")]
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
def test_invalid_setting_has_korean_field_message(settings, field):
    errors = validate_detector_settings(settings)
    assert field in errors
    assert errors[field]


def test_current_request_has_one_timestamp_and_is_immutable(tmp_path):
    bundle = make_bundle(tmp_path)
    settings = deepcopy(bundle.recipe.glasses[0].detector_settings)
    request = build_redetection_request(
        bundle,
        bundle.source_video_path,
        "glass-1",
        3.125,
        RedetectionMode.CURRENT,
        settings,
        7,
    )
    settings.canny_low = 1
    bundle.recipe.glasses[0].detector_settings.canny_low = 2
    assert redetection_schedule(request) == ((3.125, False),)
    assert detector_settings_from_json(request.detector_settings_json).canny_low == 45


def test_short_schedule_clamps_and_marks_warmup(tmp_path):
    bundle = make_bundle(tmp_path, fps=2.0, duration=10.0)
    request = build_redetection_request(
        bundle,
        bundle.source_video_path,
        "glass-1",
        5.0,
        RedetectionMode.SHORT,
        DetectorSettings(),
        1,
    )
    schedule = redetection_schedule(request)
    warmup = [time for time, hidden in schedule if hidden]
    visible = [time for time, hidden in schedule if not hidden]
    assert warmup == [1.0, 1.5, 2.0, 2.5]
    assert visible[0] == 3.0
    assert visible[-1] == 7.0


def test_short_schedule_clamps_to_analysis_start(tmp_path):
    bundle = make_bundle(tmp_path, fps=2.0)
    request_range = build_redetection_range(
        bundle,
        1.5,
        RedetectionMode.SHORT,
        before_sec=2.0,
        after_sec=2.0,
    )
    assert request_range.display_start_sec == bundle.analysis_start_sec
    assert request_range.warmup_start_sec == bundle.analysis_start_sec


def test_short_schedule_rejects_more_than_named_maximum(tmp_path):
    bundle = make_bundle(tmp_path)
    with pytest.raises(RedetectionRequestError, match="30"):
        build_redetection_range(
            bundle,
            3.0,
            RedetectionMode.SHORT,
            before_sec=16.0,
            after_sec=15.0,
            policy=RedetectionPolicy(short_max_display_duration_sec=30.0),
        )


def test_full_schedule_preserves_original_sampling_fps_and_endpoints(tmp_path):
    bundle = make_bundle(tmp_path, fps=2.0, duration=6.0)
    request = build_redetection_request(
        bundle,
        bundle.source_video_path,
        "glass-1",
        3.0,
        RedetectionMode.FULL,
        DetectorSettings(),
        1,
    )
    schedule = redetection_schedule(request)
    assert schedule[0] == (1.0, False)
    assert schedule[-1] == (5.0, False)
    assert len(schedule) == 9
    assert [value for value, _hidden in schedule] == sorted({value for value, _hidden in schedule})


def test_selected_and_all_apply_are_deep_and_noop_aware(tmp_path):
    recipe = InspectionRecipe.from_dict(make_bundle(tmp_path).recipe.to_dict())
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


def test_workbench_compatibility_checks_state_identity_resolution_and_glass(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
    matching = InspectionRecipe.from_dict(snapshot.to_dict())
    assert check_workbench_compatibility(
        matching,
        WorkbenchState.DRAFT,
        snapshot,
        "glass-1",
        DetectorSettingsApplyScope.SELECTED,
    ).compatible
    mismatched = InspectionRecipe.from_dict(snapshot.to_dict())
    mismatched.recipe_id = "other"
    mismatched.reference_frame_width += 1
    mismatched.glasses.clear()
    result = check_workbench_compatibility(
        mismatched,
        WorkbenchState.ANALYZING,
        snapshot,
        "glass-1",
        DetectorSettingsApplyScope.SELECTED,
    )
    assert not result.compatible
    assert len(result.reasons) == 4


def test_new_profile_has_new_identity_timestamps_schema_and_no_alias(tmp_path):
    snapshot = make_bundle(tmp_path).recipe
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


def test_profile_destination_rejects_bundle_descendant_and_symlink_alias(tmp_path):
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
