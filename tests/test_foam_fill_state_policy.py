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
    NoInterfaceOutcome,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def _run(frame, glass_id):
    mask = np.full(frame.shape[:2], 255, dtype=np.uint8)
    return OilHypothesisPipeline().run(
        glass_id=glass_id,
        pre=preprocess(frame, mask, DetectorSettings()),
        effective_mask=mask,
        ellipse_mask=mask,
        exclusion_mask=np.zeros_like(mask),
        static_artifact_map=None,
        crop_origin_y=0.0,
    )


def _outcomes():
    frame = np.full((240, 320), 175, dtype=np.uint8)
    frame[130:] = 70
    frame[129:132] = 225
    accepted = _run(frame, "foam-accepted")
    none = _run(np.full((240, 320), 75, dtype=np.uint8), "foam-none")
    assert isinstance(accepted, AcceptedBoundaryOutcome)
    assert isinstance(none, NoInterfaceOutcome)
    return accepted, none


def _foam(y=50.0):
    value = BoundaryCandidate("foam", BoundaryKind.FOAM_FRONT, y, final_score=0.8)
    value.selected = True
    return value


def _classify(oil, foam, foam_status, outcome, previous=None):
    gray = np.full((100, 80), 100, dtype=np.uint8)
    effective = np.full_like(gray, 255)
    return classify_fill_state(
        gray,
        effective,
        np.zeros_like(gray),
        oil,
        foam,
        previous,
        DetectorSettings(),
        foam_status,
        outcome,
    )


def test_accepted_foam_with_oil_forces_foaming_visible():
    accepted, _none = _outcomes()
    oil = project_production_result(accepted).selected_candidate
    assert oil is not None
    oil.features["local_y"] = 50.0
    state, _visibility, flags = _classify(
        oil,
        _foam(),
        FoamDecisionStatus.ACCEPTED_STRONG,
        accepted,
    )
    assert state is FillState.FOAMING_VISIBLE
    assert flags == []


def test_accepted_foam_without_oil_remains_authoritative():
    accepted, _none = _outcomes()
    ambiguous = AmbiguousOutcome(
        hypotheses=accepted.hypotheses,
        hypothesis_ids=(accepted.selected_hypothesis.identity,),
        projected_source_y=accepted.raw_source_y,
        boundary_likelihood=0.45,
        artifact_likelihood=0.4,
        ambiguity_likelihood=0.8,
        no_interface_likelihood=0.2,
        visibility=0.9,
        resources=accepted.resources,
        confidence=0.3,
        decision_margin=0.1,
        reason="ambiguous",
    )
    state, _visibility, flags = _classify(
        None,
        _foam(),
        FoamDecisionStatus.ACCEPTED_MODERATE,
        ambiguous,
    )
    assert state is FillState.FULL_WITH_FOAM
    assert flags == []


def test_pending_or_ambiguous_with_clear_oil_preserves_visible_nonfoam_state():
    accepted, _none = _outcomes()
    oil = project_production_result(accepted).selected_candidate
    assert oil is not None
    oil.features["local_y"] = 50.0
    for status in (FoamDecisionStatus.PERSISTENCE_PENDING, FoamDecisionStatus.AMBIGUOUS):
        state, _visibility, flags = _classify(oil, None, status, accepted)
        assert state is FillState.PARTIAL_VISIBLE
        assert "FOAM" in flags[0]


def test_pending_or_ambiguous_without_oil_requires_review():
    _accepted, none = _outcomes()
    for status in (FoamDecisionStatus.PERSISTENCE_PENDING, FoamDecisionStatus.AMBIGUOUS):
        state, visibility, flags = _classify(None, None, status, none)
        assert state is FillState.UNKNOWN_REVIEW
        assert visibility <= 0.45
        assert "REVIEW_REQUIRED" in flags


def test_weak_rejected_uses_positive_canonical_no_interface_only():
    _accepted, none = _outcomes()
    full = replace(
        none,
        evidence=replace(none.evidence, full_likelihood=0.8, empty_likelihood=0.1),
    )
    state, _visibility, flags = _classify(
        None,
        None,
        FoamDecisionStatus.WEAK_REJECTED,
        full,
        previous=FillState.FULL_NO_INTERFACE,
    )
    assert state is FillState.FULL_NO_INTERFACE
    assert flags == []
