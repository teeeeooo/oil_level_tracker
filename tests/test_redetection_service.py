from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import oil_tracker.application.services.redetection_service as redetection_service_module
from oil_tracker.adapters.storage.redetection_workspace import (
    RedetectionWorkspace,
    RedetectionWorkspaceError,
)
from oil_tracker.application.services.detection_processing import (
    learn_static_artifacts,
    static_artifact_sample_timestamps,
    tracking_sample_from_detection,
)
from oil_tracker.application.services.redetection_request import build_redetection_request
from oil_tracker.application.services.redetection_service import (
    PartialRedetectionService,
    RedetectionCancelled,
    RedetectionError,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, EventType, FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.redetection import RedetectionMode
from oil_tracker.domain.retrospective import RetrospectiveInterpretation, RetrospectiveStatus
from oil_tracker.domain.review import ReviewEvent
from oil_tracker.domain.session import InitialStateConfirmation
from redetection_fixtures import make_bundle


class FakeReader:
    instances = []
    fail_times = set()

    def __init__(self, path: str) -> None:
        self.path = path
        self.metadata = SimpleNamespace(width=320, height=240)
        self.reads = []
        self.closed = False
        type(self).instances.append(self)

    def read_at(self, timestamp: float):
        self.reads.append(float(timestamp))
        if round(float(timestamp), 6) in type(self).fail_times:
            raise OSError("decode failed")
        frame_index = int(round(float(timestamp) * 30))
        return np.full((240, 320, 3), frame_index % 255, np.uint8), frame_index, float(timestamp) + 0.001

    def close(self):
        self.closed = True


class FakeDetector:
    instances = []
    fail_calls = set()

    def __init__(self) -> None:
        self.reset_count = 0
        self.detect_count = 0
        self.learned = []
        self.last_y = None
        type(self).instances.append(self)

    def reset(self, glass_id=None):
        self.reset_count += 1
        self.last_y = None

    def learn_static_artifact(self, frames, glass):
        self.learned.append((len(frames), glass.id))

    def detect(self, frame, glass, frame_index, time_sec, debug=False):
        self.detect_count += 1
        if self.detect_count in type(self).fail_calls:
            raise RuntimeError("detector failed")
        raw_y = 120.0 - self.detect_count
        smooth_y = raw_y if self.last_y is None else (raw_y + self.last_y) / 2.0
        self.last_y = smooth_y
        zero = float(glass.geometry.zero_line_y)
        candidate = BoundaryCandidate(
            source="hough",
            kind=BoundaryKind.OIL_AIR,
            y=raw_y,
            features={"edge_strength": 0.8},
            penalties={"glare": 0.1},
            feature_score=0.8,
            penalty=0.1,
            final_score=0.7,
            selected=True,
        )
        detection = PhaseDetection(
            glass_id=glass.id,
            frame_index=frame_index,
            time_sec=time_sec,
            fill_state=FillState.PARTIAL_VISIBLE,
            oil_air_level_y=smooth_y,
            oil_air_level_px_from_zero=zero - smooth_y,
            oil_air_level_mm_from_zero=(zero - smooth_y) * (glass.mm_per_pixel or 1.0),
            foam_front_y=smooth_y - 10.0,
            foam_front_px_from_zero=zero - smooth_y + 10.0,
            foam_front_mm_from_zero=(zero - smooth_y + 10.0) * (glass.mm_per_pixel or 1.0),
            oil_air_confidence=0.8,
            foam_confidence=0.6,
            visibility_confidence=0.9,
            overall_confidence=0.8,
            raw_oil_air_level_y=raw_y,
            raw_foam_front_y=raw_y - 10.0,
            smoothed_oil_air_level_y=smooth_y,
            smoothed_foam_front_y=smooth_y - 10.0,
            candidates=[candidate],
            flags=[],
            debug_metrics={"history": self.detect_count},
        )
        artifacts = SimpleNamespace(
            images={"overlay": frame, "original_roi": frame[60:180, 80:240]},
            state={"detect_count": self.detect_count},
        )
        assert debug is True
        return detection, artifacts


class Cancellation:
    def __init__(self, cancelled=False):
        self.cancelled = cancelled


def _reset_fakes():
    FakeReader.instances.clear()
    FakeReader.fail_times = set()
    FakeDetector.instances.clear()
    FakeDetector.fail_calls = set()


def _request(bundle, mode, generation=1, **kwargs):
    return build_redetection_request(
        bundle,
        bundle.source_video_path,
        "glass-1",
        3.0,
        mode,
        bundle.recipe.glasses[0].detector_settings,
        generation,
        **kwargs,
    )


def _service(workspace_factory=RedetectionWorkspace.create):
    return PartialRedetectionService(FakeReader, FakeDetector, workspace_factory)


def test_static_artifact_policy_uses_start_middle_end_and_available_frames_only():
    _reset_fakes()
    assert static_artifact_sample_timestamps([1, 2, 3, 4, 5]) == (1.0, 3.0, 5.0)
    FakeReader.fail_times = {3.0}
    reader = FakeReader("x")
    detector = FakeDetector()
    glass = InspectionRecipe.default_glass(320, 240)
    decoded = learn_static_artifacts(reader, detector, [glass], [1, 2, 3, 4, 5])
    assert decoded == (1.0, 5.0)
    assert detector.learned == [(2, glass.id)]


def test_tracking_conversion_preserves_raw_smoothed_mm_and_validity():
    _reset_fakes()
    glass = InspectionRecipe.default_glass(320, 240)
    glass.mm_per_pixel = 0.25
    detector = FakeDetector()
    detector.reset()
    detection, _ = detector.detect(np.zeros((240, 320, 3), np.uint8), glass, 3, 1.0, debug=True)
    sample = tracking_sample_from_detection("run", glass, detection)
    assert sample.raw_oil_air_level_px_from_zero == pytest.approx(glass.geometry.zero_line_y - detection.raw_oil_air_level_y)
    assert sample.raw_oil_air_level_mm_from_zero == pytest.approx(sample.raw_oil_air_level_px_from_zero * 0.25)
    assert sample.smoothed_oil_air_level_px_from_zero == detection.oil_air_level_px_from_zero
    assert sample.is_valid


def test_tracking_conversion_handles_explicit_full_state_and_minimum_confidence():
    glass = InspectionRecipe.default_glass(320, 240)
    detection = PhaseDetection(
        glass.id,
        1,
        1.0,
        FillState.FULL_NO_INTERFACE,
        overall_confidence=0.9,
    )
    assert tracking_sample_from_detection("run", glass, detection).is_valid
    detection.overall_confidence = 0.1
    assert not tracking_sample_from_detection("run", glass, detection).is_valid


def test_tracking_conversion_keeps_confirmed_foam_valid_when_oil_is_unknown():
    glass = InspectionRecipe.default_glass(320, 240)
    detection = PhaseDetection(
        glass.id,
        1,
        1.0,
        FillState.UNKNOWN_REVIEW,
        raw_foam_front_y=120.0,
        foam_front_px_from_zero=30.0,
        foam_confidence=0.9,
        overall_confidence=0.4,
        flags=["R8_FOAM_EPISODE_CONFIRMED"],
    )

    sample = tracking_sample_from_detection("run", glass, detection)

    assert not sample.is_valid
    assert sample.oil_is_valid is False
    assert sample.foam_is_valid is True


def test_current_frame_has_one_detection_fresh_detector_and_lazy_artifact(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path)
    output = _service().run(_request(bundle, RedetectionMode.CURRENT), bundle)
    root = Path(output.result.workspace_root)
    try:
        detector = FakeDetector.instances[-1]
        reader = FakeReader.instances[-1]
        assert detector.reset_count == 1
        assert detector.detect_count == 1
        assert detector.learned == [(3, "glass-1")]
        assert len(output.result.samples) == 1
        assert output.result.samples[0].actual_timestamp_sec == pytest.approx(3.001)
        assert output.result.limitation_message.startswith("현재 장면만 독립적으로")
        assert reader.closed
        repository = output.workspace.repository
        record = repository.load_record(output.result.samples[0].debug_record_id)
        assert record.candidates[0]["selected"] is True
        assert repository.load_image(record, "overlay").shape == (240, 320, 3)
        assert repository.record_cache_size == output.workspace.policy.record_cache_size
    finally:
        output.workspace.cleanup()
    assert not root.exists()


def test_each_run_gets_new_detector_and_state_does_not_leak(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path)
    service = _service()
    first = service.run(_request(bundle, RedetectionMode.CURRENT, 1), bundle)
    first_y = first.result.samples[0].tracking_sample.raw_oil_air_level_y
    first.workspace.cleanup()
    second = service.run(_request(bundle, RedetectionMode.CURRENT, 2), bundle)
    try:
        assert len(FakeDetector.instances) == 2
        assert first_y == second.result.samples[0].tracking_sample.raw_oil_air_level_y
        assert all(item.reset_count == 1 for item in FakeDetector.instances)
    finally:
        second.workspace.cleanup()


def test_short_range_warmup_builds_state_but_is_not_returned(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(
        _request(bundle, RedetectionMode.SHORT, before_sec=0.5, after_sec=0.5),
        bundle,
    )
    try:
        assert FakeDetector.instances[-1].detect_count == 6
        assert len(output.result.samples) == 3
        assert all(not sample.warmup for sample in output.result.samples)
        assert output.result.summary.rerun_judgment is None
        assert "구간 참고 결과" in output.result.rerun_judgment_note
    finally:
        output.workspace.cleanup()


def test_full_range_detection_count_matches_complete_schedule_and_rejudges(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        assert FakeDetector.instances[-1].detect_count == 9
        assert len(output.result.samples) == 9
        assert output.result.summary.rerun_judgment is not None
        assert output.result.rerun_valid_coverage_ratio == pytest.approx(1.0)
        assert output.result.rerun_events
    finally:
        output.workspace.cleanup()


def test_interval_detector_failure_records_one_sample_and_continues(tmp_path):
    _reset_fakes()
    FakeDetector.fail_calls = {5}
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        failures = [sample for sample in output.result.samples if not sample.succeeded]
        assert len(failures) == 1
        assert "detector failed" in failures[0].error_message
        assert len(output.result.samples) == 9
    finally:
        output.workspace.cleanup()


def test_current_detector_failure_fails_and_cleans_workspace(tmp_path):
    _reset_fakes()
    FakeDetector.fail_calls = {1}
    bundle = make_bundle(tmp_path)
    created = []

    def factory(recipe, policy):
        workspace = RedetectionWorkspace.create(recipe, policy=policy, temporary_parent=tmp_path)
        created.append(workspace)
        return workspace

    with pytest.raises(RedetectionError, match="현재 장면"):
        _service(factory).run(_request(bundle, RedetectionMode.CURRENT), bundle)
    assert created and not created[0].root.exists()


def test_workspace_write_failure_is_fatal_not_recoverable_sample_failure(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path)

    class BrokenWorkspace:
        run_id = "broken"
        root = tmp_path / "broken"
        repository = None
        cleaned = False

        def write_detection(self, *args):
            raise RedetectionWorkspaceError("artifact write failed")

        def append_sample(self, sample):
            raise AssertionError("must not append after artifact failure")

        def cleanup(self):
            self.cleaned = True

    workspace = BrokenWorkspace()
    with pytest.raises(RedetectionWorkspaceError, match="artifact write failed"):
        _service(lambda recipe, policy: workspace).run(
            _request(bundle, RedetectionMode.CURRENT),
            bundle,
        )
    assert workspace.cleaned


def test_cancellation_before_run_creates_no_detector_reader_or_workspace(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path)
    with pytest.raises(RedetectionCancelled):
        _service().run(
            _request(bundle, RedetectionMode.CURRENT),
            bundle,
            cancellation=Cancellation(True),
        )
    assert not FakeDetector.instances
    assert not FakeReader.instances


def test_resolution_mismatch_closes_reader_and_cleans_workspace(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path)
    created = []

    class WrongReader(FakeReader):
        def __init__(self, path):
            super().__init__(path)
            self.metadata.width = 640

    def factory(recipe, policy):
        workspace = RedetectionWorkspace.create(recipe, policy=policy, temporary_parent=tmp_path)
        created.append(workspace)
        return workspace

    service = PartialRedetectionService(WrongReader, FakeDetector, factory)
    with pytest.raises(RedetectionError, match="해상도"):
        service.run(_request(bundle, RedetectionMode.CURRENT), bundle)
    assert WrongReader.instances[-1].closed
    assert not created[0].root.exists()


def _retrospective_fixture() -> RetrospectiveInterpretation:
    return RetrospectiveInterpretation(
        glass_id="glass-1",
        status=RetrospectiveStatus.ACCEPTED,
        confirmed_prior=InitialObservationState.FULL_NO_INTERFACE,
        interpreted_state=FillState.FULL_NO_INTERFACE,
        start_time_sec=1.0,
        end_time_sec=1.5,
        start_frame_index=0,
        end_frame_index=1,
        evidence_frame_indices=(2, 3),
        evidence_timestamps_sec=(2.0, 2.5),
        evidence_relative_positions=(0.1, 0.2),
        reason="fixture",
    )


def _bundle_with_retrospective(bundle):
    glass = bundle.recipe.glasses[0]
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    bundle.session.initial_state_confirmations[glass.id] = InitialStateConfirmation(
        InitialObservationState.FULL_NO_INTERFACE,
        bundle.session.input_video_path,
        bundle.session.analysis_start_sec,
    )
    return replace(
        bundle,
        result_semantics_version=2,
        retrospective_interpretations=(_retrospective_fixture(),),
    )


def test_full_redetection_recomputes_retrospective_from_saved_confirmation_and_compares_separately(tmp_path, monkeypatch):
    _reset_fakes()
    bundle = _bundle_with_retrospective(make_bundle(tmp_path, fps=2.0))
    rerun = _retrospective_fixture()
    calls = []

    def fake_reconstruct(glass, samples, confirmation):
        calls.append((glass.id, len(samples), confirmation))
        return rerun

    monkeypatch.setattr(redetection_service_module, "reconstruct_initial_state", fake_reconstruct)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        assert len(calls) == 1
        assert calls[0][0] == "glass-1"
        assert calls[0][1] == len(output.result.samples)
        assert calls[0][2] == bundle.session.initial_state_confirmations["glass-1"]
        assert output.result.official_retrospective == bundle.retrospective_for_glass("glass-1")
        assert output.result.rerun_retrospective == rerun
        assert output.result.retrospective_comparison is not None
        assert output.result.retrospective_comparison.status == "matched"
        assert output.result.retrospective_comparison.changed is False
        assert output.result.rerun_effective_state_aware_coverage_ratio is not None
    finally:
        output.workspace.cleanup()


@pytest.mark.parametrize("mode", [RedetectionMode.CURRENT, RedetectionMode.SHORT])
def test_local_redetection_does_not_reconstruct_leading_sequence(tmp_path, monkeypatch, mode):
    _reset_fakes()
    bundle = _bundle_with_retrospective(make_bundle(tmp_path, fps=2.0))

    def forbidden(*_args, **_kwargs):
        raise AssertionError("local redetection must not reconstruct the leading sequence")

    monkeypatch.setattr(redetection_service_module, "reconstruct_initial_state", forbidden)
    kwargs = {"before_sec": 0.5, "after_sec": 0.5} if mode is RedetectionMode.SHORT else {}
    output = _service().run(_request(bundle, mode, **kwargs), bundle)
    try:
        assert output.result.official_retrospective == bundle.retrospective_for_glass("glass-1")
        assert output.result.rerun_retrospective is None
        assert output.result.retrospective_comparison is not None
        assert output.result.retrospective_comparison.status == "not_recomputed_without_full_sequence"
        assert output.result.retrospective_comparison.changed is False
    finally:
        output.workspace.cleanup()


def test_full_legacy_bundle_without_saved_confirmation_stays_observed_only(tmp_path, monkeypatch):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("legacy observed-only bundle must not synthesize retrospective interpretation")

    monkeypatch.setattr(redetection_service_module, "reconstruct_initial_state", forbidden)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        assert output.result.official_retrospective is None
        assert output.result.rerun_retrospective is None
        assert output.result.retrospective_comparison is not None
        assert output.result.retrospective_comparison.status == "both_unavailable"
        assert output.result.retrospective_comparison.changed is False
    finally:
        output.workspace.cleanup()


def test_short_official_event_comparison_excludes_retrospective_provenance(tmp_path):
    bundle = make_bundle(tmp_path, fps=2.0)
    request = _request(
        bundle,
        RedetectionMode.SHORT,
        before_sec=0.5,
        after_sec=0.5,
    )
    observed = ReviewEvent(
        run_id="run-1",
        glass_id="glass-1",
        event_type=EventType.REVIEW_REQUIRED,
        start_time_sec=3.0,
        note="observed",
    )
    retrospective = ReviewEvent(
        run_id="run-1",
        glass_id="glass-1",
        event_type=EventType.FULL_NO_INTERFACE_START,
        start_time_sec=3.0,
        note="provenance=retrospective_initial_state",
    )

    selected = redetection_service_module._official_events_for_request(
        (observed, retrospective),
        request,
    )
    assert selected == (observed,)

    full_selected = redetection_service_module._official_events_for_request(
        (observed, retrospective),
        _request(bundle, RedetectionMode.FULL),
    )
    assert full_selected == (observed, retrospective)
