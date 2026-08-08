from __future__ import annotations

import json
from pathlib import Path

import pytest

from oil_tracker.adapters.storage.output_bundle_store import OutputBundleStore
from oil_tracker.domain.debug_trace import DebugTraceCompletion
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult, TrackingSample
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, VideoMetadata


class _NoCaptures:
    def create_event_captures(self, *_args, **_kwargs):
        return None


class _Graphs:
    def render(self, _result, directory, _recipe=None, **_kwargs):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "combined_levels.png").write_bytes(b"graph")
        return {"combined": "graphs/combined_levels.png"}


class _Html:
    def render(self, _result, _recipe, _session, _graphs, path, **_kwargs):
        path.write_text("<html>report</html>", encoding="utf-8")


class _FailingHtml:
    def render(self, *_args, **_kwargs):
        raise OSError("report failed")


def _store():
    store = OutputBundleStore()
    store.captures = _NoCaptures()
    store.graphs = _Graphs()
    store.html = _Html()
    return store


def _inputs(tmp_path: Path, level: DebugTraceLevel):
    recipe = InspectionRecipe.empty(320, 240, "debug")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    session = AnalysisSession(
        input_video_path=str(tmp_path / "source.mp4"),
        video_metadata=VideoMetadata(str(tmp_path / "source.mp4"), 320, 240, 30.0, 2.0, 60, "mp4v"),
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=1.0,
        sampling_fps=1.0,
        output_directory=str(tmp_path),
        debug_trace_level=level,
    )
    sample = TrackingSample(
        "run-1",
        glass.id,
        0,
        0.0,
        FillState.PARTIAL_VISIBLE,
        raw_oil_air_level_y=120.0,
        smoothed_oil_air_level_px_from_zero=10.0,
        overall_confidence=0.9,
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
            "analysis_range": [0.0, 2.0],
        },
    )
    return result, recipe, session


def _staging(tmp_path: Path) -> DebugTraceCompletion:
    staging = tmp_path / "staging-debug"
    (staging / "frames" / "g" / "r").mkdir(parents=True)
    trace = b'{"schema_version":1,"record_id":"r","run_id":"run-1","glass_id":"g"}\n'
    (staging / "debug_trace.jsonl").write_bytes(trace)
    (staging / "debug_index.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": "run-1",
                "trace_level": "basic",
                "trace_file": "debug_trace.jsonl",
                "record_count": 1,
                "glass_record_counts": {"g": 1},
                "capture_reason_counts": {"first_sample": 1},
                "records": [],
            }
        ),
        encoding="utf-8",
    )
    (staging / "frames" / "g" / "r" / "overlay.png").write_bytes(b"png")
    return DebugTraceCompletion(str(staging), "basic", 1)


def test_none_bundle_has_no_debug_directory_or_pointers(tmp_path):
    result, recipe, session = _inputs(tmp_path, DebugTraceLevel.NONE)
    output = _store().write_bundle(result, recipe, session, tmp_path)
    index = json.loads((output / "review_index.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "analysis_manifest.json").read_text(encoding="utf-8"))
    assert index["debug_trace_level"] == "none"
    assert index["debug_record_count"] == 0
    assert "debug_index" not in index and "debug_trace" not in index
    assert not (output / "debug").exists()
    assert manifest["debug_trace_level"] == "none"


@pytest.mark.parametrize("level", [DebugTraceLevel.BASIC, DebugTraceLevel.FULL])
def test_trace_bundle_copies_staging_and_adds_backward_compatible_optional_pointers(tmp_path, level):
    result, recipe, session = _inputs(tmp_path, level)
    completion = _staging(tmp_path)
    result.debug_trace_completion = DebugTraceCompletion(completion.staging_directory, level.value, 1)
    staging = Path(completion.staging_directory)
    output = _store().write_bundle(result, recipe, session, tmp_path)
    index = json.loads((output / "review_index.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "analysis_manifest.json").read_text(encoding="utf-8"))
    assert index["schema_version"] == 2
    assert index["result_semantics_version"] == 2
    assert index["debug_trace_level"] == level.value
    assert index["debug_schema_version"] == 1
    assert index["debug_index"] == "debug/debug_index.json"
    assert index["debug_trace"] == "debug/debug_trace.jsonl"
    assert index["debug_record_count"] == 1
    assert (output / index["debug_index"]).is_file()
    assert (output / index["debug_trace"]).is_file()
    assert (output / "tracking_data.csv").is_file()
    assert (output / "events.csv").is_file()
    assert (output / "report.html").is_file()
    assert manifest["debug_record_count"] == 1
    assert not staging.exists()
    assert result.debug_trace_completion is None


def test_bundle_failure_removes_temporary_bundle_and_debug_staging(tmp_path):
    result, recipe, session = _inputs(tmp_path, DebugTraceLevel.BASIC)
    completion = _staging(tmp_path)
    result.debug_trace_completion = completion
    store = _store()
    store.html = _FailingHtml()
    with pytest.raises(OSError, match="report failed"):
        store.write_bundle(result, recipe, session, tmp_path)
    assert not Path(completion.staging_directory).exists()
    assert not list(tmp_path.glob(".*.tmp-*"))
    assert result.debug_trace_completion is None
