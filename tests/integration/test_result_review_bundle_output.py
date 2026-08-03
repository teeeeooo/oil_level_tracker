from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import pytest

import oil_tracker.adapters.storage.output_bundle_store as output_bundle_module
from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult, TrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.ui.analysis_completion_summary import build_final_run_summary


class _NoCaptures:
    def create_event_captures(self, *_args, **_kwargs):
        return None


class _Graphs:
    def render(self, _result, directory, _recipe=None, **_kwargs):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "combined_levels.png"
        path.write_bytes(b"graph")
        return {"combined": "graphs/combined_levels.png"}


class _Html:
    def render(self, _result, _recipe, _session, _graphs, path):
        path.write_text("<html>report</html>", encoding="utf-8")


class _FailingCsv:
    def export(self, *_args):
        raise OSError("write failed")


def _inputs(tmp_path: Path):
    recipe = InspectionRecipe.empty(320, 240, "review")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    session = AnalysisSession(
        input_video_path=str(tmp_path / "source.mp4"),
        video_metadata=VideoMetadata(str(tmp_path / "source.mp4"), 320, 240, 30.0, 5.0, 150, "mp4v"),
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
        output_directory=str(tmp_path),
    )
    sample = TrackingSample(
        "run-1", glass.id, 30, 1.0, FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=120.0,
        smoothed_oil_air_level_px_from_zero=10.0,
        overall_confidence=0.8,
        is_valid=True,
    )
    result = AnalysisResult(
        "run-1",
        ResultState.PASS,
        [GlassAnalysisResult(glass.id, glass.name, ResultState.PASS, [sample], [])],
        "start",
        "end",
        manifest={
            "run_id": "run-1",
            "source_video_path": session.input_video_path,
            "source_metadata": session.video_metadata.to_dict(),
            "analysis_range": [1.0, 4.0],
        },
    )
    return result, recipe, session, glass


def _store():
    store = OutputBundleStore()
    store.captures = _NoCaptures()
    store.graphs = _Graphs()
    store.html = _Html()
    return store


def test_new_bundle_writes_review_index_without_removing_existing_outputs(tmp_path):
    result, recipe, session, glass = _inputs(tmp_path)
    output = _store().write_bundle(result, recipe, session, tmp_path)
    assert (output / "review_index.json").is_file()
    for filename in ("report.html", "tracking_data.csv", "events.csv", "recipe_snapshot.oilrecipe", "session.json", "analysis_manifest.json"):
        assert (output / filename).is_file()
    index = json.loads((output / "review_index.json").read_text())
    assert index["schema_version"] == 1
    assert index["source_metadata"]["width"] == 320
    assert index["glasses"] == [{"id": glass.id, "name": glass.name, "result_status": "PASS"}]
    assert index["tracking_data"] == "tracking_data.csv"


def test_manifest_points_to_relative_review_index(tmp_path):
    result, recipe, session, _glass = _inputs(tmp_path)
    output = _store().write_bundle(result, recipe, session, tmp_path)
    manifest = json.loads((output / "analysis_manifest.json").read_text())
    assert manifest["review_index"] == "review_index.json"


def test_bundle_keeps_atomic_replace_and_no_temporary_directory(tmp_path):
    result, recipe, session, _glass = _inputs(tmp_path)
    output = _store().write_bundle(result, recipe, session, tmp_path)
    assert output.is_dir()
    assert not list(tmp_path.glob(".*.tmp-*"))


def test_write_failure_cleans_temporary_directory(tmp_path):
    result, recipe, session, _glass = _inputs(tmp_path)
    store = _store()
    store.csv = _FailingCsv()
    with pytest.raises(OSError, match="write failed"):
        store.write_bundle(result, recipe, session, tmp_path)
    assert not list(tmp_path.glob(".*.tmp-*"))
    assert not list(tmp_path.glob("oil_level_analysis_*"))


def test_run_name_drives_safe_folder_and_persisted_review_metadata(tmp_path):
    result, recipe, session, _glass = _inputs(tmp_path)
    session.run_name = "반복 시험 / 03"

    output = _store().write_bundle(result, recipe, session, tmp_path)

    assert output.parent == tmp_path
    assert "반복_시험_03" in output.name
    saved_session = json.loads((output / "session.json").read_text())
    index = json.loads((output / "review_index.json").read_text())
    manifest = json.loads((output / "analysis_manifest.json").read_text())
    assert saved_session["run_name"] == "반복 시험 / 03"
    assert index["run_name"] == "반복 시험 / 03"
    assert manifest["run_name"] == "반복 시험 / 03"
    assert ResultBundleReader().read(output).run_name == "반복 시험 / 03"


class _FixedDatetime:
    @classmethod
    def now(cls):
        return datetime(2026, 8, 3, 12, 34, 56)


def test_same_name_same_second_uses_suffix_without_overwriting(tmp_path, monkeypatch):
    monkeypatch.setattr(output_bundle_module, "datetime", _FixedDatetime)
    result, recipe, session, _glass = _inputs(tmp_path)
    session.run_name = "반복 시험"
    first = _store().write_bundle(result, recipe, session, tmp_path)
    sentinel = first / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")

    second = _store().write_bundle(result, recipe, session, tmp_path)

    assert first.name == "oil_level_analysis_반복_시험_20260803_123456"
    assert second.name == f"{first.name}_2"
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_final_run_summary_uses_saved_bundle_identity_without_mutation(tmp_path):
    result, recipe, session, _glass = _inputs(tmp_path)
    recipe.name = "회수 시험 Profile"
    session.run_name = "반복 시험 03"
    output = _store().write_bundle(result, recipe, session, tmp_path)
    before = {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }

    bundle = ResultBundleReader().read(output)
    summary = build_final_run_summary(result, output, bundle)

    assert summary.run_name == "반복 시험 03"
    assert summary.profile_name == "회수 시험 Profile"
    assert summary.source_video_name == "source.mp4"
    assert summary.overall_state == result.overall_state
    assert [(item.name, item.result_state) for item in summary.glasses] == [
        (result.glass_results[0].glass_name, result.glass_results[0].result_state)
    ]
    after = {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }
    assert after == before
