from __future__ import annotations

import csv
from dataclasses import asdict
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


def test_two_local_xy_scopes_with_initial_full_reach_completed_csv_and_trace(tmp_path):
    from oil_tracker.adapters.storage.jsonl_debug_trace_writer import JsonlDebugTraceWriterFactory
    from oil_tracker.adapters.vision.artifact_calibration import region_template_from_source_rect
    from oil_tracker.adapters.vision.oil_measurement_scope import OilMeasurementScope
    from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
    from oil_tracker.application.services.analysis_pipeline import AnalysisPipeline
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.application.use_cases.analyze_video import AnalyzeVideoUseCase
    from oil_tracker.domain.enums import InitialObservationState
    from oil_tracker.domain.geometry import Rect
    from oil_tracker.domain.session import InitialStateConfirmation
    from tests.test_oil_detector_integration import glass
    from tests.test_s11_behavioral_repairs_integration import _base_step_frame

    recipe = InspectionRecipe.empty(320, 240, "two-scopes")
    recipe.glasses = [
        glass(InitialObservationState.FULL_NO_INTERFACE, "base"),
        glass(InitialObservationState.EMPTY_NO_INTERFACE, "accum"),
    ]
    rects = ((Rect(146, 126, 8, 8), Rect(180, 140, 6, 8)), (Rect(120, 124, 6, 16),))
    scopes = []
    for index, (config, rectangles) in enumerate(zip(recipe.glasses, rects, strict=True)):
        config.geometry.artifact_templates = [
            region_template_from_source_rect(rect, config, name="fixed structure")
            for rect in rectangles
        ]
        scopes.append(OilMeasurementScope.bind(
            config, frame_size=(320, 240), reference_sha256=("a", "b")[index] * 64,
            rectangles=rectangles,
        ))
    recipe_before = recipe.to_dict()
    metadata = VideoMetadata(str(tmp_path / "synthetic.mp4"), 320, 240, 30.0, 4.0, 120, "synthetic")

    class Reader:
        def __init__(self):
            self.metadata = metadata
            self.closed = False

        def read_at(self, timestamp):
            return _base_step_frame(112 + round(timestamp * 10)), round(timestamp * 30), timestamp

        def close(self):
            self.closed = True

    outputs = []
    for active_scopes in ((), tuple(scopes)):
        session = AnalysisSession(
            input_video_path=metadata.path, video_metadata=metadata,
            analysis_start_sec=0.0, analysis_end_sec=4.0, compressor_start_sec=0.0,
            sampling_fps=2.0, debug_trace_level=DebugTraceLevel.FULL,
            resolution_confirmed=True, output_directory=str(tmp_path),
        )
        for config in recipe.glasses:
            session.initial_state_confirmations[config.id] = InitialStateConfirmation(
                config.initial_state, session.input_video_path, session.analysis_start_sec,
            )
        reader = Reader()
        detector = OpenCvPhaseDetector(
            initial_full_observation=True, oil_measurement_scopes=active_scopes,
        )
        pipeline = AnalysisPipeline(
            lambda _path: reader, detector, RecipeValidationService(),
            JsonlDebugTraceWriterFactory(tmp_path),
        )
        # Existing bundle fixture replaces image/report rendering only. Detector,
        # sequence, tracking, CSV serialization and JSONL writer remain real.
        output = AnalyzeVideoUseCase(pipeline, _store()).execute(recipe, session, output_root=tmp_path)
        assert not output.result.errors
        assert reader.closed and recipe.to_dict() == recipe_before
        assert ("+oil-local-xy-v1:" in detector.version) == bool(active_scopes)
        assert len(detector.measurement_scope_manifest) == len(active_scopes)

        with (output.output_path / "tracking_data.csv").open(encoding="utf-8-sig", newline="") as stream:
            csv_rows = {(row["glass_id"], int(row["frame_index"])): row for row in csv.DictReader(stream)}
        trace = [json.loads(line) for line in (output.output_path / "debug/debug_trace.jsonl").read_text(encoding="utf-8").splitlines()]
        records = {(row["glass_id"], row["frame_index"]): row for row in trace}
        samples = {(group.glass_id, sample.frame_index): sample
                   for group in output.result.glass_results for sample in group.samples}
        assert len(csv_rows) == len(records) == len(samples) == 18
        assert csv_rows.keys() == records.keys() == samples.keys()
        assert any(sample.raw_oil_air_level_y is not None for sample in samples.values())
        scopes_by_id = {s.glass_id: s for s in active_scopes}
        for key, sample in samples.items():
            row, record = csv_rows[key], records[key]
            sequence = record["sequence"]
            version = sequence["state"]["sequence_resolver_version"]
            assert version.endswith("+initial-full-observation-v2")
            for field, position in (("raw_oil_air_level_y", "raw_oil_y"), ("raw_foam_front_y", "raw_foam_y")):
                value = None if row[field] == "" else float(row[field])
                assert value == getattr(sample, field) == sequence["positions"][position]
            if sample.raw_oil_air_level_y is not None:
                selected = [c for c in sequence["candidates"] if c["kind"] == "oil_air" and c["selected"]]
                assert len(selected) == 1 and selected[0]["canonical_y"] == sample.raw_oil_air_level_y
            lineage = record["state"]["oil_measurement_lineage"]["candidates"]
            bound = [item["sampling_scope"] for item in lineage if "sampling_scope" in item]
            if active_scopes:
                assert bound
                assert all(item["sha256"] == scopes_by_id[key[0]].sha256 for item in bound)
            else:
                assert not bound
        outputs.append((records, samples))

    baseline, scoped = outputs
    for key, record in baseline[0].items():
        assert record["state"]["foam_component_diagnostics"] == scoped[0][key]["state"]["foam_component_diagnostics"]
        # Equality is scoped to this synthetic scene, not a field guarantee.
        foam = lambda sample: {k: v for k, v in asdict(sample).items() if "foam" in k}
        assert foam(baseline[1][key]) == foam(scoped[1][key])
