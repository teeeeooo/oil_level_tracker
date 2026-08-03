from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from oil_tracker.adapters.reporting.csv_exporter import EVENT_COLUMNS, TRACKING_COLUMNS
from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleError, ResultBundleReader
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, VideoMetadata


def _bundle(tmp_path: Path, *, with_index: bool = True, tracking_rows=None, event_rows=None):
    root = tmp_path / "oil_level_analysis_test"
    root.mkdir()
    recipe = InspectionRecipe.empty(320, 240, "review")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    JsonRecipeRepository().save(root / "recipe_snapshot.oilrecipe", recipe)
    session = AnalysisSession(
        input_video_path=str(tmp_path / "source.mp4"),
        video_metadata=VideoMetadata(str(tmp_path / "source.mp4"), 320, 240, 30.0, 5.0, 150, "mp4v"),
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
    )
    (root / "session.json").write_text(json.dumps(session.to_dict()), encoding="utf-8")
    manifest = {
        "run_id": "run-1",
        "source_video_path": session.input_video_path,
        "source_metadata": session.video_metadata.to_dict(),
        "analysis_range": [1.0, 4.0],
    }
    if with_index:
        manifest["review_index"] = "review_index.json"
    (root / "analysis_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    default_tracking = [
        _tracking_row(glass.id, 20, 2.0, flags="LOW_CONFIDENCE;FOGGED_OR_GLARE", valid="false"),
        _tracking_row(glass.id, 10, 1.0, oil_px="12.5", foam_px="", valid="true"),
    ]
    _write_csv(root / "tracking_data.csv", TRACKING_COLUMNS, default_tracking if tracking_rows is None else tracking_rows)
    _write_csv(root / "events.csv", EVENT_COLUMNS, [] if event_rows is None else event_rows)
    if with_index:
        index = {
            "schema_version": 1,
            "run_id": "run-1",
            "source_video_path": session.input_video_path,
            "source_metadata": session.video_metadata.to_dict(),
            "analysis_range": [1.0, 4.0],
            "compressor_start_sec": 1.5,
            "recipe_snapshot": "recipe_snapshot.oilrecipe",
            "session": "session.json",
            "tracking_data": "tracking_data.csv",
            "events": "events.csv",
            "manifest": "analysis_manifest.json",
            "glasses": [{"id": glass.id, "name": glass.name, "result_status": "REVIEW_REQUIRED"}],
            "debug_trace_level": "none",
        }
        (root / "review_index.json").write_text(json.dumps(index), encoding="utf-8")
    return root, glass


def _tracking_row(glass_id: str, frame: int, timestamp: float, *, oil_px="", foam_px="", flags="", valid="true"):
    return {
        "run_id": "run-1",
        "glass_id": glass_id,
        "frame_index": frame,
        "timestamp_sec": timestamp,
        "fill_state": "PARTIAL_VISIBLE",
        "raw_oil_air_level_y": "100" if oil_px == "" else "",
        "raw_oil_air_level_px_from_zero": "",
        "raw_oil_air_level_mm_from_zero": "",
        "smoothed_oil_air_level_px_from_zero": oil_px,
        "smoothed_oil_air_level_mm_from_zero": "",
        "oil_air_confidence": "0.6",
        "raw_foam_front_y": "",
        "raw_foam_front_px_from_zero": "",
        "raw_foam_front_mm_from_zero": "",
        "smoothed_foam_front_px_from_zero": foam_px,
        "smoothed_foam_front_mm_from_zero": "",
        "foam_confidence": "0.4",
        "visibility_confidence": "0.8",
        "overall_confidence": "0.35" if valid == "false" else "0.8",
        "is_valid": valid,
        "flags": flags,
    }


def _event_row(glass_id: str):
    return {
        "run_id": "run-1",
        "glass_id": glass_id,
        "event_type": "FOAM_START",
        "start_time_sec": "2.0",
        "end_time_sec": "2.5",
        "representative_frame_index": "20",
        "oil_level_px": "",
        "oil_level_mm": "",
        "foam_front_px": "4.5",
        "foam_front_mm": "",
        "confidence": "0.7",
        "capture_path": "captures/foam.png",
        "note": "foam",
    }


def _write_csv(path: Path, columns, rows) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


@pytest.mark.parametrize("entry", ["directory", "manifest", "index"])
def test_reader_accepts_supported_entry_points(tmp_path, entry):
    root, glass = _bundle(tmp_path)
    source = root if entry == "directory" else root / ("analysis_manifest.json" if entry == "manifest" else "review_index.json")
    bundle = ResultBundleReader().read(source)
    assert bundle.root == root.resolve()
    assert bundle.glasses[0].id == glass.id


def test_reader_recovers_old_bundle_without_review_index(tmp_path):
    root, _glass = _bundle(tmp_path, with_index=False)
    session_payload = json.loads((root / "session.json").read_text())
    session_payload.pop("run_name")
    (root / "session.json").write_text(json.dumps(session_payload), encoding="utf-8")

    bundle = ResultBundleReader().read(root)
    assert bundle.review_index is None
    assert bundle.run_name == ""
    assert bundle.analysis_start_sec == 1.0
    assert bundle.source_video_candidates[-1].endswith("source.mp4")


def test_reader_parses_bom_nullable_bool_flags_and_sorts(tmp_path):
    root, glass = _bundle(tmp_path, event_rows=[_event_row("placeholder")])
    rows = [_tracking_row(glass.id, 20, 2.0, flags="LOW_CONFIDENCE; REVIEW_REQUIRED", valid="0"), _tracking_row(glass.id, 10, 1.0)]
    _write_csv(root / "tracking_data.csv", TRACKING_COLUMNS, rows)
    _write_csv(root / "events.csv", EVENT_COLUMNS, [_event_row(glass.id)])
    bundle = ResultBundleReader().read(root)
    assert [sample.timestamp_sec for sample in bundle.samples] == [1.0, 2.0]
    assert bundle.samples[0].smoothed_oil_air_level_mm_from_zero is None
    assert bundle.samples[1].is_valid is False
    assert bundle.samples[1].flags == ("LOW_CONFIDENCE", "REVIEW_REQUIRED")
    assert bundle.events[0].end_time_sec == 2.5


def test_reader_reports_missing_required_file(tmp_path):
    root, _glass = _bundle(tmp_path)
    (root / "session.json").unlink()
    with pytest.raises(ResultBundleError, match="session.json"):
        ResultBundleReader().read(root)


def test_reader_reports_missing_required_column(tmp_path):
    root, glass = _bundle(tmp_path)
    columns = [column for column in TRACKING_COLUMNS if column != "fill_state"]
    _write_csv(root / "tracking_data.csv", columns, [{key: value for key, value in _tracking_row(glass.id, 1, 1.0).items() if key in columns}])
    with pytest.raises(ResultBundleError, match="fill_state"):
        ResultBundleReader().read(root)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [("timestamp_sec", "bad", "timestamp_sec"), ("fill_state", "NOT_A_STATE", "enum")],
)
def test_reader_reports_malformed_row_with_filename_and_row(tmp_path, field, value, message):
    root, glass = _bundle(tmp_path)
    row = _tracking_row(glass.id, 1, 1.0)
    row[field] = value
    _write_csv(root / "tracking_data.csv", TRACKING_COLUMNS, [row])
    with pytest.raises(ResultBundleError) as caught:
        ResultBundleReader().read(root)
    text = str(caught.value)
    assert "tracking_data.csv" in text and "row 2" in text and message in text


def test_reader_rejects_unknown_glass_id(tmp_path):
    root, _glass = _bundle(tmp_path)
    _write_csv(root / "tracking_data.csv", TRACKING_COLUMNS, [_tracking_row("unknown", 1, 1.0)])
    with pytest.raises(ResultBundleError, match="snapshot에 없는 glass_id"):
        ResultBundleReader().read(root)


def test_reader_rejects_unsupported_review_index_version(tmp_path):
    root, _glass = _bundle(tmp_path)
    index = json.loads((root / "review_index.json").read_text())
    index["schema_version"] = 99
    (root / "review_index.json").write_text(json.dumps(index))
    with pytest.raises(ResultBundleError, match="지원하지 않는"):
        ResultBundleReader().read(root)


@pytest.mark.parametrize("malicious", ["../outside.csv", "/tmp/outside.csv"])
def test_reader_rejects_bundle_path_traversal(tmp_path, malicious):
    root, _glass = _bundle(tmp_path)
    index = json.loads((root / "review_index.json").read_text())
    index["tracking_data"] = malicious
    (root / "review_index.json").write_text(json.dumps(index))
    with pytest.raises(ResultBundleError, match="bundle 밖|벗어납니다"):
        ResultBundleReader().read(root)


def test_reader_allows_header_only_events(tmp_path):
    root, _glass = _bundle(tmp_path)
    bundle = ResultBundleReader().read(root)
    assert bundle.events == ()


def test_reader_rejects_empty_tracking_data(tmp_path):
    root, _glass = _bundle(tmp_path, tracking_rows=[])
    with pytest.raises(ResultBundleError, match="tracking row"):
        ResultBundleReader().read(root)
