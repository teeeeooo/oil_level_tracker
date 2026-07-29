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
    "oil_consensus_tolerance_px",
    "oil_min_consensus_sources",
    "oil_min_polarity_score",
    "oil_no_interface_min_score",
    "oil_path_window",
    "oil_path_beam_width",
    "oil_path_min_margin",
    "oil_tracker_update_confidence",
    "oil_reacquire_frames",
}


def test_defaults_and_specs_include_all_oil_path_settings():
    settings = DetectorSettings()
    names = {field.name for field in detector_setting_fields()}
    assert NEW_FIELDS <= names
    assert settings.oil_consensus_tolerance_px >= 0
    assert 1 <= settings.oil_min_consensus_sources <= 4
    assert 0 <= settings.oil_min_polarity_score <= 1
    assert 0 <= settings.oil_no_interface_min_score <= 1
    assert settings.oil_path_window >= 1
    assert 1 <= settings.oil_path_beam_width <= settings.candidate_top_k
    assert settings.oil_path_min_margin >= 0
    assert 0 <= settings.oil_tracker_update_confidence <= 1
    assert 1 <= settings.oil_reacquire_frames <= settings.oil_path_window


def test_old_recipe_without_oil_fields_loads_defaults_and_schema_stays_one():
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


def test_round_trip_clone_compare_update_and_fingerprint_include_oil_fields():
    settings = DetectorSettings(oil_path_window=7, oil_path_beam_width=5, candidate_top_k=8)
    cloned = clone_detector_settings(settings)
    assert cloned == settings
    loaded = detector_settings_from_json(detector_settings_to_json(settings))
    assert loaded == settings
    changed = update_detector_setting(cloned, "oil_path_min_margin", 0.14)
    diffs = {item.field_name: item for item in compare_detector_settings(cloned, changed)}
    assert diffs["oil_path_min_margin"].changed
    assert fingerprint_json(asdict(cloned)) != fingerprint_json(asdict(changed))


def test_oil_setting_range_integer_and_cross_field_validation():
    settings = DetectorSettings(
        oil_consensus_tolerance_px=float("inf"),
        oil_min_consensus_sources=0,
        oil_min_polarity_score=1.1,
        oil_no_interface_min_score=-0.1,
        oil_path_window=2,
        oil_path_beam_width=9,
        candidate_top_k=8,
        oil_path_min_margin=-0.1,
        oil_tracker_update_confidence=1.1,
        oil_reacquire_frames=3,
    )
    errors = validate_detector_settings(settings)
    assert {
        "oil_consensus_tolerance_px",
        "oil_min_consensus_sources",
        "oil_min_polarity_score",
        "oil_no_interface_min_score",
        "oil_path_beam_width",
        "oil_path_min_margin",
        "oil_tracker_update_confidence",
        "oil_reacquire_frames",
    } <= set(errors)
    assert "oil_path_window" not in errors
    assert "Oil reacquire" in errors["oil_reacquire_frames"]


def test_editor_lists_searches_changes_and_resets_oil_fields(qtbot):
    baseline = DetectorSettings()
    editor = DetectorSettingsEditor(baseline)
    qtbot.addWidget(editor)
    fields = {
        editor.table.item(row, 2).text(): row for row in range(editor.table.rowCount())
    }
    assert NEW_FIELDS <= set(fields)
    editor.search.setText("reacquire")
    assert not editor.table.isRowHidden(fields["oil_reacquire_frames"])
    editor.search.clear()
    editor._editors["oil_path_window"].setValue(baseline.oil_path_window + 1)
    assert "oil_path_window" in editor.changed_field_names()
    editor.reset_to_baseline()
    assert editor.changed_field_names() == ()
