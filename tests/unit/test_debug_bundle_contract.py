from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from oil_tracker.adapters.reporting.csv_exporter import EVENT_COLUMNS, TRACKING_COLUMNS
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleError, ResultBundleReader
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, VideoMetadata


def _bundle(tmp_path: Path, *, level="none", pointers=False, create_debug=False):
    root = tmp_path / "bundle"
    root.mkdir(parents=True)
    recipe = InspectionRecipe.empty(320, 240, "debug")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    JsonRecipeRepository().save(root / "recipe_snapshot.oilrecipe", recipe)
    session = AnalysisSession(
        input_video_path="source.mp4",
        video_metadata=VideoMetadata("source.mp4", 320, 240, 30.0, 2.0, 60, "mp4v"),
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=1.0,
        sampling_fps=1.0,
        debug_trace_level=DebugTraceLevel(level),
    )
    (root / "session.json").write_text(json.dumps(session.to_dict()), encoding="utf-8")
    (root / "analysis_manifest.json").write_text(
        json.dumps({"run_id": "run-1", "review_index": "review_index.json", "analysis_range": [0.0, 2.0]}),
        encoding="utf-8",
    )
    tracking = {
        "run_id": "run-1",
        "glass_id": glass.id,
        "frame_index": "0",
        "timestamp_sec": "0.0",
        "fill_state": "PARTIAL_VISIBLE",
        "raw_oil_air_level_y": "120",
        "raw_oil_air_level_px_from_zero": "",
        "raw_oil_air_level_mm_from_zero": "",
        "smoothed_oil_air_level_px_from_zero": "10",
        "smoothed_oil_air_level_mm_from_zero": "",
        "oil_air_confidence": "0.8",
        "raw_foam_front_y": "",
        "raw_foam_front_px_from_zero": "",
        "raw_foam_front_mm_from_zero": "",
        "smoothed_foam_front_px_from_zero": "",
        "smoothed_foam_front_mm_from_zero": "",
        "foam_confidence": "0",
        "visibility_confidence": "0.9",
        "overall_confidence": "0.8",
        "is_valid": "true",
        "flags": "",
    }
    with (root / "tracking_data.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACKING_COLUMNS)
        writer.writeheader()
        writer.writerow(tracking)
    with (root / "events.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=EVENT_COLUMNS)
        writer.writeheader()
    index = {
        "schema_version": 1,
        "run_id": "run-1",
        "analysis_range": [0.0, 2.0],
        "recipe_snapshot": "recipe_snapshot.oilrecipe",
        "session": "session.json",
        "tracking_data": "tracking_data.csv",
        "events": "events.csv",
        "manifest": "analysis_manifest.json",
        "glasses": [{"id": glass.id, "name": glass.name, "result_status": "PASS"}],
        "debug_trace_level": level,
        "debug_record_count": 1 if level != "none" else 0,
    }
    if pointers:
        index["debug_index"] = "debug/debug_index.json"
        index["debug_trace"] = "debug/debug_trace.jsonl"
    if create_debug:
        (root / "debug").mkdir()
        (root / "debug" / "debug_index.json").write_text("{}", encoding="utf-8")
        (root / "debug" / "debug_trace.jsonl").write_text("", encoding="utf-8")
    (root / "review_index.json").write_text(json.dumps(index), encoding="utf-8")
    return root


def test_none_contract_disables_debug_even_if_session_default_would_be_basic(tmp_path):
    bundle = ResultBundleReader().read(_bundle(tmp_path, level="none"))
    assert bundle.debug_trace_level == "none"
    assert bundle.debug_record_count == 0
    assert not bundle.has_debug_trace


def test_valid_optional_pointers_make_debug_trace_available(tmp_path):
    bundle = ResultBundleReader().read(_bundle(tmp_path, level="basic", pointers=True, create_debug=True))
    assert bundle.debug_trace_level == "basic"
    assert bundle.debug_index_path == "debug/debug_index.json"
    assert bundle.debug_trace_path == "debug/debug_trace.jsonl"
    assert bundle.debug_record_count == 1
    assert bundle.has_debug_trace


def test_missing_debug_files_are_soft_warning_and_general_bundle_still_opens(tmp_path):
    bundle = ResultBundleReader().read(_bundle(tmp_path, level="basic", pointers=True, create_debug=False))
    assert bundle.samples
    assert bundle.debug_warning
    assert not bundle.has_debug_trace


def test_incomplete_debug_pointers_are_soft_warning(tmp_path):
    root = _bundle(tmp_path, level="full")
    bundle = ResultBundleReader().read(root)
    assert bundle.debug_trace_level == "full"
    assert "불완전" in bundle.debug_warning


def test_invalid_debug_level_is_clear_bundle_error(tmp_path):
    root = _bundle(tmp_path)
    index = json.loads((root / "review_index.json").read_text())
    index["debug_trace_level"] = "verbose"
    (root / "review_index.json").write_text(json.dumps(index))
    with pytest.raises(ResultBundleError, match="debug_trace_level"):
        ResultBundleReader().read(root)


def test_debug_pointer_traversal_does_not_escape_and_disables_only_debug(tmp_path):
    root = _bundle(tmp_path, level="basic", pointers=True)
    index = json.loads((root / "review_index.json").read_text())
    index["debug_index"] = "../outside.json"
    (root / "review_index.json").write_text(json.dumps(index))
    bundle = ResultBundleReader().read(root)
    assert bundle.samples
    assert "bundle 밖" in bundle.debug_warning
