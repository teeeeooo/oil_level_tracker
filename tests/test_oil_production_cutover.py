from __future__ import annotations

from dataclasses import fields
import hashlib
import importlib.util
import inspect
import json

import numpy as np
import pytest

from foam_benchmark_fixtures import controlled_scenes
from oil_tracker.adapters.vision import opencv_phase_detector as detector_module
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.oil_hypothesis_projection import project_production_result
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousDecision,
    AmbiguousOutcome,
    BoundaryAcceptedDecision,
    EvidenceUnavailableDecision,
    EvidenceUnavailableOutcome,
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


DETECTOR_VERSION = "opencv-phase-detector-r14-phase-component-replacement-v1"


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


def test_failure_unavailable_and_numeric_ownership_are_structurally_distinct():
    accepted = _pipeline_result(_oil_frame(), "accepted")
    unavailable = _pipeline_result(_uniform_frame(255), "unavailable")
    failure = PipelineFailureOutcome(
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


def test_legacy_oil_owners_are_retired_from_the_runtime_package():
    source = inspect.getsource(OpenCvPhaseDetector)
    legacy_modules = (
        "candidate_generators",
        "candidate_scorer",
        "oil_candidate_consensus",
        "oil_no_interface",
        "oil_temporal_path",
    )
    for module_name in legacy_modules:
        assert importlib.util.find_spec(
            f"oil_tracker.adapters.vision.{module_name}"
        ) is None
    for forbidden_name in (
        "generate_oil_air_candidates",
        "build_oil_candidate_consensus",
        "score_candidates",
        "evaluate_no_interface",
        "OilTemporalPath",
    ):
        assert forbidden_name not in source

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


def test_successful_stable_absence_clear_is_not_shared_with_pipeline_failure(monkeypatch):
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

    failed_detector = OpenCvPhaseDetector()
    failed_glass = _glass("pipeline-failure")
    first, _ = failed_detector.detect(_oil_frame(), failed_glass, 1, 0.0)
    sample_count = first.debug_metrics["oil_smoothing_sample_count"]
    before_count = failed_detector.oil_temporal_state_count
    monkeypatch.setattr(
        failed_detector._oil_pipeline,
        "run",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("injected pipeline failure")),
    )
    failures = [
        failed_detector.detect(_oil_frame(), failed_glass, index, index * 0.5)[0]
        for index in range(2, 10)
    ]
    assert all(item.debug_metrics["oil_decision_status"] == "pipeline_failure" for item in failures)
    assert all(item.debug_metrics["oil_tracker_action"] == "NO_UPDATE" for item in failures)
    assert all(item.debug_metrics["oil_smoothing_action"] == "PRESERVE" for item in failures)
    assert all(item.debug_metrics["oil_smoothing_sample_count"] == sample_count for item in failures)
    assert failed_detector.oil_temporal_state_count == before_count == 1


def test_detector_has_no_post_owner_result_rejection_or_failure_conversion():
    source = inspect.getsource(OpenCvPhaseDetector._evaluate_oil_pipeline)
    assert "validate_production_result" not in source
    assert source.index("try:") < source.index("kwargs = _isolated_pipeline_inputs")
    assert source.index("kwargs = _isolated_pipeline_inputs") < source.index(
        "return self._oil_pipeline.run(**kwargs)"
    )
    failure = PipelineFailureOutcome("injected", PipelineFailureStage.PHASE_A)
    projection = project_production_result(failure)
    assert projection.raw_source_y is None
    assert projection.selected_candidate is None
    assert projection.tracker_action.value == "NO_UPDATE"
    assert projection.smoothing_action.value == "PRESERVE"


@pytest.mark.parametrize("debug", (False, True))
@pytest.mark.parametrize("failure_site", ("input_helper", "array_copy"))
def test_detector_normalizes_pre_owner_preparation_failure_and_preserves_foam(
    monkeypatch,
    debug,
    failure_site,
):
    detector = OpenCvPhaseDetector()
    glass = _glass(f"pre-owner-{failure_site}-{debug}")
    glass.detector_settings.foam_strong_evidence_score = 1.0
    glass.detector_settings.foam_min_evidence_score = 0.20

    accepted, _ = detector.detect(_oil_frame(130), glass, 1, 0.0, debug=False)
    assert accepted.raw_oil_air_level_y is not None
    before_store = detector._oil_pipeline._debug_store_reference
    before_replacements = detector._oil_pipeline._debug_store_replacement_count
    before_record = before_store.records[glass.id]
    before_snapshot = detector._oil_pipeline.temporal_snapshot(glass.id)

    def fail(*_args, **_kwargs):
        raise RuntimeError(f"injected detector {failure_site} failure")

    scene = next(
        item for item in controlled_scenes() if item.case_id == "partial-foam"
    )
    with monkeypatch.context() as patch:
        patch.setattr(
            detector_module,
            (
                "_isolated_pipeline_inputs"
                if failure_site == "input_helper"
                else "_isolated_readonly_copy"
            ),
            fail,
        )
        detection, artifacts = detector.detect(
            scene.frame,
            glass,
            2,
            scene.timestamp,
            debug=debug,
        )

    assert isinstance(detection, PhaseDetection)
    assert detection.raw_oil_air_level_y is None
    assert detection.smoothed_oil_air_level_y is None
    assert detection.oil_air_level_y is None
    assert detection.oil_air_level_px_from_zero is None
    assert detection.oil_air_level_mm_from_zero is None
    assert not any(
        item.selected for item in detection.candidates if item.kind.value == "oil_air"
    )
    assert detection.debug_metrics["oil_pipeline_available"] is False
    assert detection.debug_metrics["oil_tracker_action"] == "NO_UPDATE"
    assert detection.debug_metrics["oil_smoothing_action"] == "PRESERVE"
    assert detection.debug_metrics["oil_no_interface_score"] == 0.0
    assert detection.debug_metrics["oil_no_interface_reason"] == "not_available"
    assert "OIL_PIPELINE_FAILURE" in detection.flags

    assert detector._oil_pipeline._debug_store_reference is before_store
    assert detector._oil_pipeline._debug_store_replacement_count == before_replacements
    assert detector._oil_pipeline._debug_store_reference.records[glass.id] is before_record
    assert detector._oil_pipeline.temporal_snapshot(glass.id) == before_snapshot

    foam_state = detector._foam_gate.state_for(glass.id)
    assert foam_state is not None
    assert foam_state.pending_count == 1
    assert detection.debug_metrics["foam_decision_status"] == "persistence_pending"
    assert detection.debug_metrics["foam_temporal_pending_count"] == 1
    assert detector.foam_temporal_state_count == 1
    assert (artifacts is not None) is debug
    if artifacts is not None:
        assert "foam_combined_evidence" in artifacts.images
        assert artifacts.state["foam_decision_status"] == "persistence_pending"

    recovered, _ = detector.detect(_oil_frame(132), glass, 3, 1.0, debug=False)
    assert recovered.debug_metrics["oil_pipeline_available"] is True
    assert recovered.raw_oil_air_level_y is not None
    assert detector._oil_pipeline._debug_store_replacement_count == before_replacements + 1


def test_production_constructor_surfaces_have_no_oil_injection_callbacks():
    detector_parameters = inspect.signature(OpenCvPhaseDetector).parameters
    pipeline_parameters = inspect.signature(OilHypothesisPipeline).parameters
    assert not detector_parameters
    assert set(pipeline_parameters) == {"bounds"}
    for forbidden in (
        "oil_runner",
        "oil_precommit_probe",
        "temporal_evaluator",
        "outcome_preparer",
        "commit_hook",
        "handoff_hook",
        "transaction_admitted_hook",
        "global_reset_waiting_hook",
    ):
        assert forbidden not in detector_parameters
        assert forbidden not in pipeline_parameters


class _AdversarialRasterRunner:
    def __init__(self):
        self.mutated = 0

    def run(self, **kwargs):
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


def test_raster_isolation_and_foam_processing_survive_oil_failure(monkeypatch):
    runner = _AdversarialRasterRunner()
    detector = OpenCvPhaseDetector()
    monkeypatch.setattr(detector._oil_pipeline, "run", runner.run)
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
        projection = project_production_result(outcome)
        assert projection.tracker_action is outcome.tracker_action
        assert projection.smoothing_action is outcome.smoothing_action

    detector = OpenCvPhaseDetector()
    detector.detect(_oil_frame(125), _glass("a"), 1, 0.0)
    detector.detect(_oil_frame(145), _glass("b"), 1, 0.0)
    assert detector.oil_temporal_state_count == 2
    detector.reset("a")
    assert detector.oil_temporal_state_count == 1
    detector.reset()
    assert detector.oil_temporal_state_count == 0
    assert detector.foam_temporal_state_count == 0


def test_projection_is_exhaustive_and_non_rejecting_for_closed_outcome_family():
    accepted = _pipeline_result(_oil_frame(), "projection-boundary")
    no_interface = _pipeline_result(_uniform_frame(75), "projection-none")
    unavailable = _pipeline_result(_uniform_frame(255), "projection-unavailable")
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    assert isinstance(no_interface, NoInterfaceOutcome)
    assert isinstance(unavailable, EvidenceUnavailableOutcome)
    hypothesis = accepted.selected_hypothesis
    ambiguous = AmbiguousOutcome(
        hypotheses=accepted.hypotheses,
        hypothesis_ids=(hypothesis.identity,),
        projected_source_y=hypothesis.representative_source_y,
        boundary_likelihood=hypothesis.boundary_likelihood,
        artifact_likelihood=hypothesis.artifact_likelihood,
        ambiguity_likelihood=hypothesis.ambiguity_likelihood,
        no_interface_likelihood=0.0,
        visibility=hypothesis.visibility,
        resources=accepted.resources,
        confidence=0.5,
        decision_margin=0.1,
        reason="projection ambiguity",
    )
    pending = ReacquisitionPendingOutcome(
        pending_hypothesis=hypothesis,
        hypotheses=accepted.hypotheses,
        resources=accepted.resources,
        confidence=0.5,
        decision_margin=0.1,
        reason="projection pending",
    )
    failure = PipelineFailureOutcome("projection failure", PipelineFailureStage.PHASE_A)

    family = (accepted, no_interface, ambiguous, unavailable, pending, failure)
    projections = tuple(project_production_result(outcome) for outcome in family)
    assert projections[0].raw_source_y == accepted.raw_source_y
    assert projections[0].selected_candidate is not None
    for projection in projections[1:]:
        assert projection.raw_source_y is None
        assert projection.selected_candidate is None
    for outcome, projection in zip(family, projections):
        assert projection.tracker_action is outcome.tracker_action
        assert projection.smoothing_action is outcome.smoothing_action
