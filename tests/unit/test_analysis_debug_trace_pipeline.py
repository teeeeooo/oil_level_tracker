from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from oil_tracker.application.services.analysis_pipeline import AnalysisCancelled, AnalysisPipeline, SimpleCancellationToken
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.domain.debug_trace import DebugTraceCompletion
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, InitialStateConfirmation, VideoMetadata


class FakeReader:
    def __init__(self):
        self.closed = False
        self.metadata = VideoMetadata("video.mp4", 320, 240, 30.0, 2.0, 60, "mp4v")

    def read_at(self, timestamp):
        frame_index = int(round(float(timestamp) * 30))
        return np.zeros((240, 320, 3), dtype=np.uint8), frame_index, float(timestamp)

    def close(self):
        self.closed = True


class FakeDetector:
    def __init__(self, fail_at=None):
        self.calls = []
        self.reset_count = 0
        self.fail_at = fail_at
        self.learn_calls = 0

    def reset(self):
        self.reset_count += 1

    def learn_static_artifact(self, frames, glass):
        self.learn_calls += 1

    def detect(self, frame, glass, frame_index, timestamp, debug=False):
        self.calls.append((frame_index, timestamp, debug))
        if self.fail_at is not None and len(self.calls) == self.fail_at:
            raise RuntimeError("detector failed")
        candidate = BoundaryCandidate(
            source="fake",
            kind=BoundaryKind.OIL_AIR,
            y=100.0,
            feature_score=0.9,
            final_score=0.9,
            selected=True,
        )
        detection = PhaseDetection(
            glass_id=glass.id,
            frame_index=frame_index,
            time_sec=timestamp,
            fill_state=FillState.PARTIAL_VISIBLE,
            oil_air_level_y=100.0,
            oil_air_level_px_from_zero=20.0,
            oil_air_level_mm_from_zero=None,
            foam_front_y=None,
            foam_front_px_from_zero=None,
            foam_front_mm_from_zero=None,
            oil_air_confidence=0.9,
            foam_confidence=0.0,
            visibility_confidence=0.9,
            overall_confidence=0.9,
            raw_oil_air_level_y=100.0,
            smoothed_oil_air_level_y=100.0,
            candidates=[candidate],
        )
        artifacts = SimpleNamespace(
            images={"overlay": np.zeros((10, 10, 3), dtype=np.uint8)},
            state={"previous_state": "PARTIAL_VISIBLE", "proposed_state": "PARTIAL_VISIBLE"},
        ) if debug else None
        return detection, artifacts


class FakeSink:
    def __init__(self, fail_write=False, fail_finalize=False):
        self.records = []
        self.finalized = False
        self.aborted = False
        self.fail_write = fail_write
        self.fail_finalize = fail_finalize

    def write(self, glass, detection, artifacts, decision):
        if self.fail_write:
            raise OSError("trace write failed")
        assert artifacts is not None
        self.records.append((glass.id, detection.frame_index, tuple(reason.value for reason in decision.reasons)))

    def finalize(self):
        if self.fail_finalize:
            raise OSError("trace finalize failed")
        self.finalized = True
        return DebugTraceCompletion("/tmp/fake-debug", "basic", len(self.records))

    def abort(self):
        self.aborted = True


class FakeSinkFactory:
    def __init__(self, sink=None):
        self.sink = sink or FakeSink()
        self.created = 0

    def create(self, run_id, recipe, session):
        self.created += 1
        self.run_id = run_id
        self.level = session.debug_trace_level
        return self.sink


def _inputs(level):
    recipe = InspectionRecipe.empty(320, 240, "debug")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    recipe.glasses.append(glass)
    session = AnalysisSession(
        input_video_path="video.mp4",
        video_metadata=VideoMetadata("video.mp4", 320, 240, 30.0, 2.0, 60, "mp4v"),
        analysis_start_sec=0.0,
        analysis_end_sec=2.0,
        compressor_start_sec=1.0,
        sampling_fps=2.0,
        debug_trace_level=level,
    )
    glass.initial_state = InitialObservationState.UNKNOWN_REVIEW
    session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        InitialObservationState.UNKNOWN_REVIEW,
        session.input_video_path,
        session.analysis_start_sec,
    )
    return recipe, session


def _run(level, *, detector=None, factory=None, cancellation=None):
    recipe, session = _inputs(level)
    reader = FakeReader()
    detector = detector or FakeDetector()
    pipeline = AnalysisPipeline(
        lambda _path: reader,
        detector,
        RecipeValidationService(),
        factory,
    )
    result = pipeline.run(recipe, session, cancellation=cancellation)
    return result, reader, detector


def test_none_uses_debug_false_and_does_not_create_sink():
    factory = FakeSinkFactory()
    result, reader, detector = _run(DebugTraceLevel.NONE, factory=factory)
    assert factory.created == 0
    assert all(debug is False for _frame, _time, debug in detector.calls)
    assert result.debug_trace_completion is None
    assert reader.closed


@pytest.mark.parametrize("level", [DebugTraceLevel.BASIC, DebugTraceLevel.FULL])
def test_basic_and_full_use_single_debug_detector_call_per_sample(level):
    factory = FakeSinkFactory()
    result, reader, detector = _run(level, factory=factory)
    assert len(detector.calls) == 5
    assert all(debug is True for _frame, _time, debug in detector.calls)
    assert factory.sink.finalized
    assert result.debug_trace_completion.record_count == len(factory.sink.records)
    assert reader.closed


def test_basic_captures_only_markers_but_full_captures_every_sample():
    basic_factory = FakeSinkFactory()
    full_factory = FakeSinkFactory()
    basic, _reader, _detector = _run(DebugTraceLevel.BASIC, factory=basic_factory)
    full, _reader, _detector = _run(DebugTraceLevel.FULL, factory=full_factory)
    assert basic.debug_trace_completion.record_count == 3
    assert full.debug_trace_completion.record_count == 5


def test_official_tracking_is_identical_across_levels():
    results = []
    for level in DebugTraceLevel:
        factory = None if level is DebugTraceLevel.NONE else FakeSinkFactory()
        result, _reader, _detector = _run(level, factory=factory)
        samples = result.glass_results[0].samples
        results.append([(sample.frame_index, sample.timestamp_sec, sample.fill_state, sample.raw_oil_air_level_y, sample.overall_confidence) for sample in samples])
    assert results[0] == results[1] == results[2]


def test_cancellation_aborts_sink_and_closes_reader():
    token = SimpleCancellationToken()
    token.cancel()
    factory = FakeSinkFactory()
    recipe, session = _inputs(DebugTraceLevel.BASIC)
    reader = FakeReader()
    pipeline = AnalysisPipeline(lambda _path: reader, FakeDetector(), RecipeValidationService(), factory)
    with pytest.raises(AnalysisCancelled):
        pipeline.run(recipe, session, cancellation=token)
    assert factory.sink.aborted
    assert reader.closed


def test_detector_failure_aborts_sink_and_closes_reader():
    factory = FakeSinkFactory()
    recipe, session = _inputs(DebugTraceLevel.BASIC)
    reader = FakeReader()
    pipeline = AnalysisPipeline(lambda _path: reader, FakeDetector(fail_at=2), RecipeValidationService(), factory)
    with pytest.raises(RuntimeError, match="detector failed"):
        pipeline.run(recipe, session)
    assert factory.sink.aborted
    assert reader.closed


def test_trace_write_and_finalize_failures_abort_sink():
    for sink in (FakeSink(fail_write=True), FakeSink(fail_finalize=True)):
        factory = FakeSinkFactory(sink)
        recipe, session = _inputs(DebugTraceLevel.BASIC)
        reader = FakeReader()
        pipeline = AnalysisPipeline(lambda _path: reader, FakeDetector(), RecipeValidationService(), factory)
        with pytest.raises(OSError, match="trace"):
            pipeline.run(recipe, session)
        assert sink.aborted
        assert reader.closed
