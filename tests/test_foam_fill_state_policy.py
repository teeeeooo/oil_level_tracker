from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.fill_state_classifier import classify_fill_state
from oil_tracker.adapters.vision.foam_front_detector import FoamDecisionStatus
from oil_tracker.adapters.vision.oil_shadow_types import (
    ShadowNoInterfaceEvidence,
    ShadowTemporalStatus,
)
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def _candidate(kind: BoundaryKind, y: float = 50.0) -> BoundaryCandidate:
    candidate = BoundaryCandidate("test", kind, y, final_score=0.8)
    if kind is BoundaryKind.OIL_AIR:
        candidate.features["local_y"] = y
    return candidate


def _no_interface(full: float, empty: float):
    return ShadowNoInterfaceEvidence(
        available=True,
        likelihood=0.9,
        full_likelihood=full,
        empty_likelihood=empty,
        region_uniformity=0.9,
        weak_boundary_evidence=0.9,
        competing_boundary_likelihood=0.0,
        visibility=0.95,
        glare_conflict=0.0,
        mean_intensity=90.0,
        texture=5.0,
        reason="foam_policy_no_interface",
    )


def _classify(
    oil,
    foam,
    status,
    *,
    previous=None,
    oil_status=ShadowTemporalStatus.NO_INTERFACE_ACCEPTED,
    no_interface=None,
):
    gray = np.full((100, 80), 100, dtype=np.uint8)
    effective = np.full_like(gray, 255)
    glare = np.zeros_like(gray)
    return classify_fill_state(
        gray,
        effective,
        glare,
        oil,
        foam,
        previous,
        DetectorSettings(),
        status,
        oil_status,
        no_interface,
    )


def test_accepted_foam_with_oil_forces_foaming_visible():
    state, _visibility, flags = _classify(
        _candidate(BoundaryKind.OIL_AIR),
        _candidate(BoundaryKind.FOAM_FRONT),
        FoamDecisionStatus.ACCEPTED_STRONG,
        oil_status=ShadowTemporalStatus.BOUNDARY_ACCEPTED,
    )
    assert state is FillState.FOAMING_VISIBLE
    assert flags == []


def test_accepted_foam_without_oil_forces_full_with_foam():
    state, _visibility, flags = _classify(
        None,
        _candidate(BoundaryKind.FOAM_FRONT),
        FoamDecisionStatus.ACCEPTED_MODERATE,
        oil_status=ShadowTemporalStatus.AMBIGUOUS,
    )
    assert state is FillState.FULL_WITH_FOAM
    assert flags == []


def test_pending_or_ambiguous_with_clear_oil_preserves_visible_nonfoam_state():
    for status in (
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
    ):
        state, _visibility, flags = _classify(
            _candidate(BoundaryKind.OIL_AIR, 50),
            None,
            status,
            oil_status=ShadowTemporalStatus.BOUNDARY_ACCEPTED,
        )
        assert state is FillState.PARTIAL_VISIBLE
        assert "FOAM" in flags[0]


def test_pending_or_ambiguous_without_oil_requires_unknown_review():
    for status in (
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
    ):
        state, visibility, flags = _classify(
            None,
            None,
            status,
            no_interface=_no_interface(0.8, 0.1),
        )
        assert state is FillState.UNKNOWN_REVIEW
        assert visibility <= 0.45
        assert "REVIEW_REQUIRED" in flags


def test_weak_and_glare_rejected_follow_typed_no_interface_classifier():
    for status in (
        FoamDecisionStatus.WEAK_REJECTED,
        FoamDecisionStatus.GLARE_REJECTED,
    ):
        state, _visibility, flags = _classify(
            None,
            None,
            status,
            previous=FillState.FULL_NO_INTERFACE,
            no_interface=_no_interface(0.8, 0.1),
        )
        assert state is FillState.FULL_NO_INTERFACE
        assert flags == []


def test_existing_visible_full_and_empty_paths_remain_available():
    oil = _candidate(BoundaryKind.OIL_AIR, 5)
    state, _visibility, _flags = _classify(
        oil,
        None,
        FoamDecisionStatus.NO_EVIDENCE,
        previous=FillState.FULL_NO_INTERFACE,
        oil_status=ShadowTemporalStatus.BOUNDARY_ACCEPTED,
    )
    assert state is FillState.DRAINING_VISIBLE
    full, _visibility, _flags = _classify(
        None,
        None,
        FoamDecisionStatus.NO_EVIDENCE,
        previous=FillState.FULL_NO_INTERFACE,
        no_interface=_no_interface(0.8, 0.1),
    )
    empty, _visibility, _flags = _classify(
        None,
        None,
        FoamDecisionStatus.NO_EVIDENCE,
        previous=FillState.EMPTY_NO_INTERFACE,
        no_interface=_no_interface(0.1, 0.8),
    )
    assert full is FillState.FULL_NO_INTERFACE
    assert empty is FillState.EMPTY_NO_INTERFACE
