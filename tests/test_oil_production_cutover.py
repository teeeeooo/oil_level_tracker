from __future__ import annotations

from dataclasses import fields
import hashlib
import inspect
import json

import numpy as np

from oil_tracker.adapters.vision import (
    candidate_generators,
    candidate_scorer,
    oil_candidate_consensus,
    oil_no_interface,
    oil_temporal_path,
)
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_hypothesis_projection import validate_production_result
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    EvidenceUnavailableOutcome,
    FailedPipelineFrame,
    NoInterfaceAcceptedDecision,
    NoInterfaceOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    ReacquisitionPendingDecision,
    ReacquisitionPendingOutcome,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowNoInterfaceObservation,
    ShadowUnavailableObservation,
    SuccessfulPipelineFrame,
)
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import InspectionRecipe


DETECTOR_VERSION = "opencv-phase-detector-s5b-typed-production-v1"


def _glass(glass_id: str = "typed-glass", initial=InitialObservationState.AUTO):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = glass_id
    glass.geometry.zero_line_y = 150.0
    glass.initial_state = initial
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _oil_frame(y: int = 130):
    frame = np.full((240, 320, 3), 175, dtype=np.uint8)
    frame[y:] = 70
    frame[y - 1 : y + 2] = 225
    return frame


def _uniform_frame(value: int):
    return np.full((240, 320, 3), value, dtype=np.uint8)


def _pipeline_result(frame: np.ndarray, glass_id: str):
    pipeline = OilHypothesisPipeline()
    glass = _glass(glass_id)
    bundle = build_mask_bundle(frame, glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    return pipeline.run(
        glass_id=glass.id,
        pre=pre,
        effective_mask=bundle.effective_mask,
        ellipse_mask=bundle.ellipse_mask,
        exclusion_mask=bundle.exclusion_mask,
        static_artifact_map=None,
        crop_origin_y=float(bundle.crop_origin[1]),
    )


def _image_signature(images):
    return tuple(
        sorted(
            (
                key,
                value.shape,
                str(value.dtype),
                hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            )
            for key, value in images.items()
        )
    )


def test_closed_models_have_no_stored_duplicate_discriminators_or_clear_boolean():
    observation_types = (
        ShadowBoundaryObservation,
        ShadowNoInterfaceObservation,
        ShadowAmbiguousObservation,
        ShadowUnavailableObservation,
    )
    for value in observation_types:
        names = {item.name for item in fields(value)}
        assert "kind" not in names
        assert "failure" not in names
        assert "failure_reason" not in names

    decision_types = (
        BoundaryAcceptedDecision,
        NoInterfaceAcceptedDecision,
        AmbiguousDecision,
        EvidenceUnavailableDecision,
        ReacquisitionPendingDecision,
    )
    for value in decision_types:
        names = {item.name for item in fields(value)}
        assert "status" not in names
        assert "observation_kind" not in names
        assert "clear_smoothing" not in names
        assert "tracker_action" not in names
        assert "smoothing_action" not in names

    assert "current_observation" in {item.name for item in fields(SuccessfulPipelineFrame)}
    assert "failure" not in {item.name for item in fields(SuccessfulPipelineFrame)}
    failed_names = {item.name for item in fields(FailedPipelineFrame)}
    assert "current_observation" not in failed_names
    assert "hypotheses" not in failed_names
    assert "selected_hypothesis" not in failed_names


def test_failure_unavailable_and_numeric_ownership_are_structurally_distinct():
    accepted = _pipeline_result(_oil_frame(), "accepted")
    unavailable = _pipeline_result(_uniform_frame(255), "unavailable")
    failure = OilHypothesisPipeline().failure_outcome(
        "injected",
        PipelineFailureStage.PHASE_A,
    )
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    assert isinstance(unavailable, EvidenceUnavailableOutcome)
    assert isinstance(failure, PipelineFailureOutcome)
    assert hasattr(accepted, "raw_source_y")
    assert not hasattr(unavailable, "raw_source_y")
    assert not hasattr(failure, "raw_source_y")
    assert not hasattr(failure, "hypotheses")
    assert not hasattr(failure, "resources")
    assert type(unavailable) is not type(failure)


def test_production_detector_does_not_call_legacy_oil_owners(monkeypatch):
    source = inspect.getsource(OpenCvPhaseDetector)
    for forbidden_name in (
        "generate_oil_air_candidates",
        "build_oil_candidate_consensus",
        "score_candidates",
        "evaluate_no_interface",
        "OilTemporalPath",
    ):
        assert forbidden_name not in source

    def forbidden(*_args, **_kwargs):
        raise AssertionError("legacy oil owner was called")

    monkeypatch.setattr(candidate_generators, "generate_oil_air_candidates", forbidden)
    monkeypatch.setattr(oil_candidate_consensus, "build_oil_candidate_consensus", forbidden)
    monkeypatch.setattr(candidate_scorer, "score_candidates", forbidden)
    monkeypatch.setattr(oil_no_interface, "evaluate_no_interface", forbidden)
    monkeypatch.setattr(oil_temporal_path.OilTemporalPath, "evaluate", forbidden)

    detection, _ = OpenCvPhaseDetector().detect(_oil_frame(), _glass(), 1, 0.0)
    assert detection.raw_oil_air_level_y is not None
    assert detection.debug_metrics["oil_pipeline_available"] is True


def test_accepted_boundary_is_sole_numeric_candidate_authority():
    detector = OpenCvPhaseDetector()
    detection, artifacts = detector.detect(
        _oil_frame(130),
        _glass(),
        1,
        0.0,
        debug=True,
    )
    assert detector.version == DETECTOR_VERSION
    assert detection.debug_metrics["oil_decision_status"] == "boundary_accepted"
    assert detection.debug_metrics["oil_tracker_action"] == "ACCEPT_BOUNDARY"
    assert detection.debug_metrics["oil_smoothing_action"] == "PRESERVE"
    assert detection.raw_oil_air_level_y is not None
    assert detection.smoothed_oil_air_level_y == detection.raw_oil_air_level_y
    selected = [
        item for item in detection.candidates
        if item.kind.value == "oil_air" and item.selected
    ]
    assert len(selected) == 1
    assert selected[0].source.startswith("oil_hypothesis:")
    assert selected[0].y == detection.raw_oil_air_level_y
    assert artifacts is not None
    assert artifacts.state["oil_hypothesis"]["selected_hypothesis_id"] in selected[0].source


def test_positive_no_interface_projection_requires_canonical_evidence():
    cases = (
        (75, InitialObservationState.FULL_NO_INTERFACE, FillState.FULL_NO_INTERFACE),
        (205, InitialObservationState.EMPTY_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE),
        (135, InitialObservationState.AUTO, FillState.UNKNOWN_REVIEW),
    )
    for value, initial, expected in cases:
        detection, _ = OpenCvPhaseDetector().detect(
            _uniform_frame(value),
            _glass(f"none-{value}", initial),
            1,
            0.0,
        )
        assert detection.debug_metrics["oil_decision_status"] == "no_interface_accepted"
        assert detection.raw_oil_air_level_y is None
        assert detection.smoothed_oil_air_level_y is None
        assert not any(
            item.selected for item in detection.candidates if item.kind.value == "oil_air"
        )
        assert detection.fill_state is expected


def test_successful_stable_absence_clear_is_not_shared_with_pipeline_failure():
    detector = OpenCvPhaseDetector()
    glass = _glass("successful-unavailable")
    accepted, _ = detector.detect(_oil_frame(), glass, 1, 0.0)
    assert accepted.raw_oil_air_level_y is not None
    outputs = [
        detector.detect(_uniform_frame(255), glass, index, index * 0.5)[0]
        for index in range(2, 8)
    ]
    assert all(item.raw_oil_air_level_y is None for item in outputs)
    assert outputs[-1].debug_metrics["oil_decision_status"] == "unavailable"
    assert outputs[-1].debug_metrics["oil_smoothing_action"] == "CLEAR_STALE_AFTER_STABLE_ABSENCE"
    assert outputs[-1].debug_metrics["oil_smoothing_sample_count"] == 0

    calls = 0

    def fail_after_accepted(_kwargs):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise RuntimeError("injected pre-commit failure")

    failed_detector = OpenCvPhaseDetector(oil_precommit_probe=fail_after_accepted)
    failed_glass = _glass("pipeline-failure")
    first, _ = failed_detector.detect(_oil_frame(), failed_glass, 1, 0.0)
    sample_count = first.debug_metrics["oil_smoothing_sample_count"]
    failures = [
        failed_detector.detect(_oil_frame(), failed_glass, index, index * 0.5)[0]
        for index in range(2, 10)
    ]
    assert all(item.debug_metrics["oil_decision_status"] == "pipeline_failure" for item in failures)
    assert all(item.debug_metrics["oil_tracker_action"] == "NO_UPDATE" for item in failures)
    assert all(item.debug_metrics["oil_smoothing_action"] == "PRESERVE" for item in failures)
    assert all(item.debug_metrics["oil_smoothing_sample_count"] == sample_count for item in failures)
    assert failed_detector.oil_temporal_state_count == 1

def test_stateful_external_mutation_cannot_change_detector_temporal_state():
    external = OilHypothesisPipeline()

    def mutate_then_fail(kwargs):
        outcome = external.run(**kwargs)
        assert isinstance(outcome, AcceptedBoundaryOutcome)
        raise TypeError("invalid injected result")

    detector = OpenCvPhaseDetector(oil_precommit_probe=mutate_then_fail)
    detection, _ = detector.detect(_oil_frame(), _glass("invalid"), 1, 0.0)
    assert external.temporal_state_count == 1
    assert detector.oil_temporal_state_count == 0
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert detection.debug_metrics["oil_pipeline_available"] is False
    assert detection.debug_metrics["oil_tracker_action"] == "NO_UPDATE"
    assert detection.debug_metrics["oil_smoothing_action"] == "PRESERVE"
    assert "TypeError" in detection.debug_metrics["oil_pipeline_failure_reason"]
    assert "OIL_PIPELINE_FAILURE" in detection.flags


def test_stateful_runner_surface_is_removed_from_detector():
    parameters = inspect.signature(OpenCvPhaseDetector).parameters
    assert "oil_runner" not in parameters
    assert "oil_precommit_probe" in parameters
    try:
        OpenCvPhaseDetector(oil_runner=object())  # type: ignore[call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("stateful oil runner injection remained available")


class _AdversarialRasterRunner:
    def __init__(self):
        self.mutated = 0

    def run(self, kwargs):
        arrays = (
            kwargs["pre"].gray,
            kwargs["pre"].normalized,
            kwargs["pre"].blurred,
            kwargs["pre"].sobel_y_signed,
            kwargs["pre"].sobel_y_abs,
            kwargs["pre"].canny,
            kwargs["pre"].horizontal_mask,
            kwargs["pre"].glare_mask,
            kwargs["effective_mask"],
            kwargs["ellipse_mask"],
            kwargs["exclusion_mask"],
            kwargs["static_artifact_map"],
        )
        for array in arrays:
            assert array is not None
            assert not array.flags.writeable
            assert array.flags.owndata
            assert array.base is None
            array.setflags(write=True)
            array[...] = 0 if np.any(array != 0) else 1
            self.mutated += 1
        raise RuntimeError("adversarial raster mutation")



def test_raster_isolation_and_foam_processing_survive_oil_failure():
    runner = _AdversarialRasterRunner()
    detector = OpenCvPhaseDetector(oil_precommit_probe=runner.run)
    glass = _glass("raster")
    static = _oil_frame(115)
    detector.learn_static_artifact([static.copy()] * 3, glass)
    frame = _oil_frame(130)
    before = frame.copy()
    detection, artifacts = detector.detect(frame, glass, 1, 0.0, debug=True)
    assert np.array_equal(frame, before)
    assert runner.mutated == 12
    assert detection.raw_oil_air_level_y is None
    assert detection.debug_metrics["oil_pipeline_available"] is False
    assert "foam_decision_status" in detection.debug_metrics
    assert artifacts is not None
    assert _image_signature(artifacts.images)


def test_debug_projection_is_json_safe_deterministic_and_canonical_only():
    first, artifacts_a = OpenCvPhaseDetector().detect(
        _oil_frame(), _glass("det-a"), 1, 0.0, debug=True
    )
    second, artifacts_b = OpenCvPhaseDetector().detect(
        _oil_frame(), _glass("det-b"), 1, 0.0, debug=True
    )
    assert artifacts_a is not None and artifacts_b is not None
    assert artifacts_a.profiles == artifacts_b.profiles
    assert artifacts_a.candidate_rows == artifacts_b.candidate_rows
    assert artifacts_a.state["oil_hypothesis"] == artifacts_b.state["oil_hypothesis"]
    assert not any(item.source == "oil_consensus" for item in first.candidates)
    assert not any(key.startswith("shadow_oil_") for key in first.debug_metrics)
    json.dumps(first.debug_metrics, allow_nan=False, sort_keys=True)
    json.dumps(artifacts_a.candidate_rows, allow_nan=False, sort_keys=True)
    json.dumps(artifacts_a.state, allow_nan=False, sort_keys=True)


def test_external_phase_detection_shape_and_detector_version_are_unchanged():
    assert OpenCvPhaseDetector.version == DETECTOR_VERSION
    assert [item.name for item in fields(PhaseDetection)] == [
        "glass_id",
        "frame_index",
        "time_sec",
        "fill_state",
        "oil_air_level_y",
        "oil_air_level_px_from_zero",
        "oil_air_level_mm_from_zero",
        "foam_front_y",
        "foam_front_px_from_zero",
        "foam_front_mm_from_zero",
        "oil_air_confidence",
        "foam_confidence",
        "visibility_confidence",
        "overall_confidence",
        "raw_oil_air_level_y",
        "raw_foam_front_y",
        "smoothed_oil_air_level_y",
        "smoothed_foam_front_y",
        "candidates",
        "flags",
        "debug_metrics",
    ]


def test_canonical_outcomes_validate_and_typed_state_is_glass_local_resettable():
    for outcome in (
        _pipeline_result(_oil_frame(), "boundary"),
        _pipeline_result(_uniform_frame(75), "none"),
        _pipeline_result(_uniform_frame(120), "ambiguous"),
        _pipeline_result(_uniform_frame(255), "unavailable"),
        PipelineFailureOutcome("failed", PipelineFailureStage.PHASE_A),
    ):
        validate_production_result(outcome)

    detector = OpenCvPhaseDetector()
    detector.detect(_oil_frame(125), _glass("a"), 1, 0.0)
    detector.detect(_oil_frame(145), _glass("b"), 1, 0.0)
    assert detector.oil_temporal_state_count == 2
    detector.reset("a")
    assert detector.oil_temporal_state_count == 1
    detector.reset()
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0
