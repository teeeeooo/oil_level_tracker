from __future__ import annotations

from dataclasses import asdict

from oil_tracker.application.services.detector_settings import (
    clone_detector_settings,
    compare_detector_settings,
    detector_setting_fields,
    detector_settings_from_json,
    detector_settings_to_json,
    update_detector_setting,
    validate_detector_settings,
)
from oil_tracker.domain.detector_benchmark import fingerprint_json
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.ui.widgets.detector_settings_editor import DetectorSettingsEditor


NEW_FIELDS = {
    "foam_lightness_threshold",
    "foam_max_chroma",
    "foam_min_whiteness_ratio",
    "foam_max_glare_overlap_ratio",
    "foam_min_evidence_score",
    "foam_strong_evidence_score",
    "foam_persistence_frames",
    "foam_max_front_jump_px",
}


def test_defaults_and_field_specs_include_all_foam_evidence_settings():
    settings = DetectorSettings()
    names = {field.name for field in detector_setting_fields()}
    assert NEW_FIELDS <= names
    assert settings.foam_persistence_frames >= 1
    assert 0 <= settings.foam_min_evidence_score <= settings.foam_strong_evidence_score <= 1


def test_foam_setting_ranges_and_cross_validation():
    settings = DetectorSettings(
        foam_min_whiteness_ratio=1.1,
        foam_persistence_frames=0,
        foam_max_front_jump_px=float("inf"),
        foam_min_evidence_score=0.8,
        foam_strong_evidence_score=0.7,
    )
    errors = validate_detector_settings(settings)
    assert "foam_min_whiteness_ratio" in errors
    assert "foam_persistence_frames" in errors
    assert "foam_max_front_jump_px" in errors
    assert "foam_strong_evidence_score" in errors


def test_old_recipe_without_new_fields_loads_defaults_and_schema_stays_one():
    recipe = InspectionRecipe.empty(320, 240, "old")
    recipe.glasses = [InspectionRecipe.default_glass(320, 240)]
    payload = recipe.to_dict()
    for field in NEW_FIELDS:
        payload["glasses"][0]["detector_settings"].pop(field)
    loaded = InspectionRecipe.from_dict(payload)
    defaults = DetectorSettings()
    assert loaded.schema_version == 1
    for field in NEW_FIELDS:
        assert getattr(loaded.glasses[0].detector_settings, field) == getattr(defaults, field)


def test_new_recipe_round_trip_clone_compare_update_and_json_are_lossless():
    recipe = InspectionRecipe.empty(320, 240, "new")
    glass = InspectionRecipe.default_glass(320, 240)
    glass.detector_settings.foam_lightness_threshold = 137.5
    glass.detector_settings.foam_persistence_frames = 4
    recipe.glasses = [glass]
    loaded = InspectionRecipe.from_dict(recipe.to_dict())
    assert asdict(loaded.glasses[0].detector_settings) == asdict(glass.detector_settings)

    cloned = clone_detector_settings(glass.detector_settings)
    changed = update_detector_setting(cloned, "foam_min_evidence_score", 0.51)
    diffs = {item.field_name: item for item in compare_detector_settings(cloned, changed)}
    assert diffs["foam_min_evidence_score"].changed
    assert detector_settings_from_json(detector_settings_to_json(changed)) == changed


def test_settings_fingerprint_changes_when_foam_evidence_setting_changes():
    baseline = DetectorSettings()
    changed = clone_detector_settings(baseline)
    changed.foam_max_chroma += 1.0
    assert fingerprint_json(asdict(baseline)) != fingerprint_json(asdict(changed))


def test_editor_lists_searches_changes_and_resets_new_foam_fields(qtbot):
    baseline = DetectorSettings()
    editor = DetectorSettingsEditor(baseline)
    qtbot.addWidget(editor)
    fields = {
        editor.table.item(row, 2).text(): row for row in range(editor.table.rowCount())
    }
    assert NEW_FIELDS <= set(fields)
    editor.search.setText("whiteness")
    assert not editor.table.isRowHidden(fields["foam_min_whiteness_ratio"])
    editor.search.clear()
    spin = editor._editors["foam_persistence_frames"]
    spin.setValue(baseline.foam_persistence_frames + 1)
    assert "foam_persistence_frames" in editor.changed_field_names()
    editor.reset_to_baseline()
    assert editor.changed_field_names() == ()
