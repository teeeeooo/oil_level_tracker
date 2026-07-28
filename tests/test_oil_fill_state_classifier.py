from __future__ import annotations

from dataclasses import replace

import numpy as np

from oil_tracker.adapters.vision.fill_state_classifier import classify_fill_state
from oil_tracker.adapters.vision.foam_front_detector import FoamDecisionStatus
from oil_tracker.adapters.vision.oil_hypothesis_projection import project_production_result
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousOutcome,
    EvidenceUnavailableOutcome,
    NoInterfaceOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    ReacquisitionPendingOutcome,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def image(value: int):
    return np.full((48, 64), value, dtype=np.uint8)


def mask():
    return np.full((48, 64), 255, dtype=np.uint8)


def foam(y: float = 12.0):
    candidate = BoundaryCandidate("foam_component", BoundaryKind.FOAM_FRONT, y)
    candidate.selected = True
    candidate.final_score = 0.9
    return candidate


def _run(frame, glass_id):
    mask_value = np.full(frame.shape[:2], 255, dtype=np.uint8)
    return OilHypothesisPipeline().run(
        glass_id=glass_id,
        pre=preprocess(frame, mask_value, DetectorSettings()),
        effective_mask=mask_value,
        ellipse_mask=mask_value,
        exclusion_mask=np.zeros_like(mask_value),
        static_artifact_map=None,
        crop_origin_y=0.0,
    )


def _outcomes():
    frame = np.full((240, 320), 175, dtype=np.uint8)
    frame[130:] = 70
    frame[129:132] = 225
    accepted = _run(frame, "accepted")
    no_interface = _run(np.full((240, 320), 75, dtype=np.uint8), "none")
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    assert isinstance(no_interface, NoInterfaceOutcome)
    return accepted, no_interface


def _classify(candidate, foam_candidate, previous, outcome, foam_status=FoamDecisionStatus.NO_EVIDENCE):
    return classify_fill_state(
        image(120),
        mask(),
        np.zeros((48, 64), dtype=np.uint8),
        candidate,
        foam_candidate,
        previous,
        DetectorSettings(),
        foam_status,
        outcome,
    )


def test_accepted_oil_uses_visible_state_and_accepted_foam_overrides():
    accepted, _no_interface = _outcomes()
    candidate = project_production_result(accepted).selected_candidate
    assert candidate is not None
    candidate.features["local_y"] = 24.0
    candidate.y = 24.0
    state, _visibility, flags = _classify(candidate, None, None, accepted)
    assert state is FillState.PARTIAL_VISIBLE
    assert "REVIEW_REQUIRED" not in flags
    state, _visibility, _flags = _classify(
        candidate,
        foam(),
        None,
        accepted,
        FoamDecisionStatus.ACCEPTED_STRONG,
    )
    assert state is FillState.FOAMING_VISIBLE


def test_non_boundary_outcomes_require_review_without_numeric_candidate():
    accepted, no_interface = _outcomes()
    variants = (
        AmbiguousOutcome(
            hypotheses=accepted.hypotheses,
            hypothesis_ids=(accepted.selected_hypothesis.identity,),
            projected_source_y=accepted.raw_source_y,
            boundary_likelihood=0.45,
            artifact_likelihood=0.40,
            ambiguity_likelihood=0.8,
            no_interface_likelihood=0.2,
            visibility=0.9,
            resources=accepted.resources,
            confidence=0.3,
            decision_margin=0.1,
            reason="ambiguous",
        ),
        ReacquisitionPendingOutcome(
            pending_hypothesis=accepted.selected_hypothesis,
            hypotheses=accepted.hypotheses,
            resources=accepted.resources,
            confidence=0.6,
            decision_margin=0.2,
            reason="pending",
        ),
        EvidenceUnavailableOutcome(
            hypotheses=accepted.hypotheses,
            resources=accepted.resources,
            visibility=0.1,
            confidence=0.1,
            decision_margin=0.0,
            stability_mode=no_interface.stability_mode,
            reason="unavailable",
        ),
        PipelineFailureOutcome("failed", PipelineFailureStage.PHASE_A),
    )
    for outcome in variants:
        state, _visibility, flags = _classify(None, None, None, outcome)
        assert state is FillState.UNKNOWN_REVIEW
        assert "REVIEW_REQUIRED" in flags


def test_no_interface_full_empty_and_ambiguous_use_canonical_evidence_and_prior():
    _accepted, base = _outcomes()
    full_outcome = replace(
        base,
        evidence=replace(base.evidence, full_likelihood=0.8, empty_likelihood=0.1),
    )
    empty_outcome = replace(
        base,
        evidence=replace(base.evidence, full_likelihood=0.1, empty_likelihood=0.8),
    )
    ambiguous_outcome = replace(
        base,
        evidence=replace(base.evidence, full_likelihood=0.5, empty_likelihood=0.48),
    )
    full, _visibility, _flags = _classify(
        None, None, FillState.FULL_NO_INTERFACE, full_outcome
    )
    empty, _visibility, _flags = _classify(
        None, None, FillState.EMPTY_NO_INTERFACE, empty_outcome
    )
    ambiguous, _visibility, flags = _classify(None, None, None, ambiguous_outcome)
    assert full is FillState.FULL_NO_INTERFACE
    assert empty is FillState.EMPTY_NO_INTERFACE
    assert ambiguous is FillState.UNKNOWN_REVIEW
    assert "REVIEW_REQUIRED" in flags


def test_accepted_foam_remains_authoritative_when_oil_fails():
    failure = PipelineFailureOutcome("failed", PipelineFailureStage.PHASE_A)
    state, _visibility, flags = _classify(
        None,
        foam(),
        None,
        failure,
        FoamDecisionStatus.ACCEPTED_STRONG,
    )
    assert state is FillState.FULL_WITH_FOAM
    assert "REVIEW_REQUIRED" not in flags


def test_numeric_candidate_with_non_boundary_outcome_is_rejected():
    accepted, _none = _outcomes()
    candidate = project_production_result(accepted).selected_candidate
    assert candidate is not None
    failure = PipelineFailureOutcome("failed", PipelineFailureStage.PHASE_A)
    import pytest
    with pytest.raises(ValueError, match="accepted canonical boundary"):
        _classify(candidate, None, None, failure)
