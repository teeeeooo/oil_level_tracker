from __future__ import annotations

from copy import deepcopy

import pytest

from oil_tracker.application.observation_settings_copy import (
    GlassSettingsCopyError,
    GlassSettingsCopyOptions,
    GlassSettingsCopyRequest,
    copy_observation_window_settings,
)
from oil_tracker.domain.enums import InitialObservationState, JudgmentMode
from oil_tracker.domain.geometry import EllipseGeometry, ExclusionZone, Rect
from oil_tracker.domain.recipe import InspectionRecipe, SCHEMA_VERSION


def _recipe() -> InspectionRecipe:
    recipe = InspectionRecipe.empty(640, 480, "copy-test")
    source = InspectionRecipe.default_glass(640, 480, 1)
    first = InspectionRecipe.default_glass(640, 480, 2)
    second = InspectionRecipe.default_glass(640, 480, 3)

    source.judgment_rule.mode = JudgmentMode.HOLD_ABOVE_ZERO
    source.judgment_rule.recovery_limit_sec = 77.0
    source.judgment_rule.stable_hold_sec = 12.0
    source.judgment_rule.minimum_valid_coverage_ratio = 0.81
    source.judgment_rule.allowed_violation_sec = 3.0
    source.detector_settings.canny_low = 61
    source.detector_settings.minimum_final_confidence = 0.73
    source.geometry.margin_ratio = 0.17
    source.initial_state = InitialObservationState.FULL_NO_INTERFACE
    source.mm_per_pixel = 0.24
    source.geometry.ellipse = EllipseGeometry(320.0, 240.0, 64.0, 92.0)

    first.id = "target-1"
    first.name = "대상 관찰창 1"
    first.description = "keep-first"
    first.enabled = False
    first.geometry.ellipse = EllipseGeometry(500.0, 240.0, 40.0, 70.0)
    first.geometry.zero_line_y = 255.0
    first.geometry.margin_ratio = 0.05
    first.geometry.exclusions = [ExclusionZone("zone-1", Rect(480.0, 210.0, 10.0, 12.0), "keep")]
    first.mm_per_pixel = 0.9
    first.detector_settings.canny_low = 15

    second.id = "target-2"
    second.name = "대상 관찰창 2"
    second.description = "keep-second"
    second.geometry.ellipse = EllipseGeometry(160.0, 240.0, 44.0, 74.0)
    second.geometry.zero_line_y = 225.0
    second.geometry.margin_ratio = 0.09
    second.geometry.exclusions = [ExclusionZone("zone-2", Rect(145.0, 220.0, 8.0, 9.0), "keep")]
    second.mm_per_pixel = 0.7
    second.detector_settings.canny_low = 19

    source.id = "source"
    recipe.glasses = [source, first, second]
    return recipe


def _request(recipe, *, targets=("target-1",), options=None):
    return GlassSettingsCopyRequest(
        recipe.glasses[0].id,
        tuple(targets),
        options or GlassSettingsCopyOptions(),
    )


def _glass(recipe, glass_id):
    return next(glass for glass in recipe.glasses if glass.id == glass_id)


def test_rejects_missing_source_targets_source_as_target_and_empty_options():
    recipe = _recipe()
    with pytest.raises(GlassSettingsCopyError, match="원본"):
        copy_observation_window_settings(
            recipe,
            GlassSettingsCopyRequest("missing", ("target-1",), GlassSettingsCopyOptions()),
        )
    with pytest.raises(GlassSettingsCopyError, match="한 개 이상"):
        copy_observation_window_settings(recipe, _request(recipe, targets=()))
    with pytest.raises(GlassSettingsCopyError, match="원본 관찰창"):
        copy_observation_window_settings(recipe, _request(recipe, targets=("source",)))
    with pytest.raises(GlassSettingsCopyError, match="설정 항목"):
        copy_observation_window_settings(
            recipe,
            _request(recipe, options=GlassSettingsCopyOptions(False, False, False, False, False, False)),
        )
    with pytest.raises(GlassSettingsCopyError, match="대상 관찰창"):
        copy_observation_window_settings(recipe, _request(recipe, targets=("missing",)))


def test_deduplicates_targets_and_copies_multiple_targets_atomically():
    recipe = _recipe()
    result = copy_observation_window_settings(
        recipe,
        _request(recipe, targets=("target-1", "target-1", "target-2")),
    )
    assert result.requested_target_ids == ("target-1", "target-2")
    assert result.changed_target_ids == ("target-1", "target-2")
    assert _glass(recipe, "target-1").judgment_rule == recipe.glasses[0].judgment_rule
    assert _glass(recipe, "target-2").detector_settings == recipe.glasses[0].detector_settings


@pytest.mark.parametrize(
    ("options", "assertion"),
    [
        (GlassSettingsCopyOptions(True, False, False, False, False, False), "judgment"),
        (GlassSettingsCopyOptions(False, True, False, False, False, False), "detector"),
        (GlassSettingsCopyOptions(False, False, True, False, False, False), "margin"),
        (GlassSettingsCopyOptions(False, False, False, True, False, False), "initial"),
        (GlassSettingsCopyOptions(False, False, False, False, True, False), "mm"),
        (GlassSettingsCopyOptions(False, False, False, False, False, True), "ellipse"),
    ],
)
def test_copies_each_option_independently(options, assertion):
    recipe = _recipe()
    source = recipe.glasses[0]
    target_before = deepcopy(_glass(recipe, "target-1"))
    copy_observation_window_settings(recipe, _request(recipe, options=options))
    target = _glass(recipe, "target-1")

    if assertion == "judgment":
        assert target.judgment_rule == source.judgment_rule
        assert target.detector_settings == target_before.detector_settings
    elif assertion == "detector":
        assert target.detector_settings == source.detector_settings
        assert target.judgment_rule == target_before.judgment_rule
    elif assertion == "margin":
        assert target.geometry.margin_ratio == source.geometry.margin_ratio
        assert target.geometry.ellipse == target_before.geometry.ellipse
    elif assertion == "initial":
        assert target.initial_state == source.initial_state
        assert target.mm_per_pixel == target_before.mm_per_pixel
    elif assertion == "mm":
        assert target.mm_per_pixel == source.mm_per_pixel
        assert target.initial_state == target_before.initial_state
    else:
        assert target.geometry.ellipse.radius_x == source.geometry.ellipse.radius_x
        assert target.geometry.ellipse.radius_y == source.geometry.ellipse.radius_y
        assert target.geometry.ellipse.center_x == target_before.geometry.ellipse.center_x
        assert target.geometry.ellipse.center_y == target_before.geometry.ellipse.center_y


def test_copies_mm_per_pixel_none_exactly():
    recipe = _recipe()
    recipe.glasses[0].mm_per_pixel = None
    copy_observation_window_settings(
        recipe,
        _request(recipe, options=GlassSettingsCopyOptions(False, False, False, False, True, False)),
    )
    assert _glass(recipe, "target-1").mm_per_pixel is None


def test_preserves_target_identity_position_reference_exclusions_and_metadata():
    recipe = _recipe()
    target_before = deepcopy(_glass(recipe, "target-1"))
    copy_observation_window_settings(recipe, _request(recipe))
    target = _glass(recipe, "target-1")
    assert target.id == target_before.id
    assert target.name == target_before.name
    assert target.description == target_before.description
    assert target.enabled == target_before.enabled
    assert target.geometry.ellipse == target_before.geometry.ellipse
    assert target.geometry.zero_line_y == target_before.geometry.zero_line_y
    assert target.geometry.exclusions == target_before.geometry.exclusions
    assert recipe.recipe_id
    assert recipe.name == "copy-test"


def test_deep_copies_mutable_settings_without_aliasing_source_or_other_target():
    recipe = _recipe()
    copy_observation_window_settings(
        recipe,
        _request(recipe, targets=("target-1", "target-2")),
    )
    source = _glass(recipe, "source")
    first = _glass(recipe, "target-1")
    second = _glass(recipe, "target-2")
    assert first.judgment_rule is not source.judgment_rule
    assert first.detector_settings is not source.detector_settings
    assert first.geometry is not source.geometry
    assert first.judgment_rule is not second.judgment_rule
    assert first.detector_settings is not second.detector_settings
    first.judgment_rule.recovery_limit_sec = 999.0
    first.detector_settings.canny_low = 1
    first.geometry.margin_ratio = 0.01
    assert source.judgment_rule.recovery_limit_sec == 77.0
    assert second.judgment_rule.recovery_limit_sec == 77.0
    assert source.detector_settings.canny_low == 61
    assert second.detector_settings.canny_low == 61
    assert source.geometry.margin_ratio == 0.17


def test_valid_ellipse_size_copy_preserves_target_center_zero_line_and_exclusions():
    recipe = _recipe()
    before = deepcopy(_glass(recipe, "target-1"))
    options = GlassSettingsCopyOptions(False, False, False, False, False, True)
    copy_observation_window_settings(recipe, _request(recipe, options=options))
    target = _glass(recipe, "target-1")
    assert (target.geometry.ellipse.radius_x, target.geometry.ellipse.radius_y) == (64.0, 92.0)
    assert (target.geometry.ellipse.center_x, target.geometry.ellipse.center_y) == (
        before.geometry.ellipse.center_x,
        before.geometry.ellipse.center_y,
    )
    assert target.geometry.zero_line_y == before.geometry.zero_line_y
    assert target.geometry.exclusions == before.geometry.exclusions


def test_rejects_ellipse_outside_frame_and_zero_line_outside_new_ellipse():
    options = GlassSettingsCopyOptions(False, False, False, False, False, True)
    recipe = _recipe()
    _glass(recipe, "target-1").geometry.ellipse = EllipseGeometry(610.0, 240.0, 20.0, 40.0)
    with pytest.raises(GlassSettingsCopyError, match="대상 관찰창 1"):
        copy_observation_window_settings(recipe, _request(recipe, options=options))

    recipe = _recipe()
    _glass(recipe, "target-1").geometry.zero_line_y = 100.0
    with pytest.raises(GlassSettingsCopyError, match="기준점"):
        copy_observation_window_settings(recipe, _request(recipe, options=options))


def test_rejects_too_small_effective_area_after_margin_copy():
    recipe = _recipe()
    source = _glass(recipe, "source")
    source.geometry.ellipse = EllipseGeometry(320.0, 240.0, 2.0, 2.0)
    source.geometry.margin_ratio = 0.17
    _glass(recipe, "target-1").geometry.zero_line_y = 240.0
    options = GlassSettingsCopyOptions(False, False, True, False, False, True)
    with pytest.raises(GlassSettingsCopyError, match="타원 크기"):
        copy_observation_window_settings(recipe, _request(recipe, options=options))


def test_one_invalid_target_leaves_every_target_unchanged():
    recipe = _recipe()
    before = recipe.to_dict()
    _glass(recipe, "target-2").geometry.ellipse = EllipseGeometry(620.0, 240.0, 10.0, 50.0)
    before = recipe.to_dict()
    options = GlassSettingsCopyOptions(False, True, False, False, False, True)
    with pytest.raises(GlassSettingsCopyError, match="대상 관찰창 2"):
        copy_observation_window_settings(
            recipe,
            _request(recipe, targets=("target-1", "target-2"), options=options),
        )
    assert recipe.to_dict() == before


def test_unrelated_copy_is_allowed_when_existing_target_geometry_is_invalid():
    recipe = _recipe()
    target = _glass(recipe, "target-1")
    target.geometry.zero_line_y = -100.0
    options = GlassSettingsCopyOptions(False, True, False, False, False, False)
    result = copy_observation_window_settings(recipe, _request(recipe, options=options))
    assert result.changed_target_ids == ("target-1",)
    assert _glass(recipe, "target-1").detector_settings.canny_low == 61
    assert _glass(recipe, "target-1").geometry.zero_line_y == -100.0


def test_no_op_does_not_replace_recipe_values():
    recipe = _recipe()
    source = _glass(recipe, "source")
    target = _glass(recipe, "target-1")
    target.judgment_rule = deepcopy(source.judgment_rule)
    options = GlassSettingsCopyOptions(True, False, False, False, False, False)
    before_glasses = recipe.glasses
    result = copy_observation_window_settings(recipe, _request(recipe, options=options))
    assert result.is_no_op
    assert recipe.glasses is before_glasses


def test_serialization_schema_and_preserved_geometry_contract_are_unchanged():
    recipe = _recipe()
    before = deepcopy(_glass(recipe, "target-1"))
    copy_observation_window_settings(recipe, _request(recipe))
    payload = recipe.to_dict()
    loaded = InspectionRecipe.from_dict(payload)
    target = _glass(loaded, "target-1")
    assert payload["schema_version"] == SCHEMA_VERSION == 1
    assert target.judgment_rule == _glass(recipe, "source").judgment_rule
    assert target.detector_settings == _glass(recipe, "source").detector_settings
    assert target.id == before.id
    assert target.geometry.ellipse == before.geometry.ellipse
    assert target.geometry.zero_line_y == before.geometry.zero_line_y
    assert target.geometry.exclusions == before.geometry.exclusions
