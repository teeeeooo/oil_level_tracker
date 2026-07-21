from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.fill_state_classifier import classify_fill_state
from oil_tracker.adapters.vision.foam_front_detector import FoamDecisionStatus
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def _candidate(kind: BoundaryKind, y: float = 50.0) -> BoundaryCandidate:
    return BoundaryCandidate("test", kind, y, final_score=0.8)


def _classify(oil, foam, status, *, previous=None, gray_value=100):
    gray = np.full((100, 80), gray_value, dtype=np.uint8)
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
    )


def test_accepted_foam_with_oil_forces_foaming_visible():
    state, _visibility, flags = _classify(
        _candidate(BoundaryKind.OIL_AIR),
        _candidate(BoundaryKind.FOAM_FRONT),
        FoamDecisionStatus.ACCEPTED_STRONG,
    )
    assert state is FillState.FOAMING_VISIBLE
    assert flags == []


def test_accepted_foam_without_oil_forces_full_with_foam():
    state, _visibility, flags = _classify(
        None,
        _candidate(BoundaryKind.FOAM_FRONT),
        FoamDecisionStatus.ACCEPTED_MODERATE,
    )
    assert state is FillState.FULL_WITH_FOAM
    assert flags == []


def test_pending_or_ambiguous_with_clear_oil_preserves_visible_nonfoam_state():
    for status in (
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
    ):
        state, _visibility, flags = _classify(
            _candidate(BoundaryKind.OIL_AIR, 50), None, status
        )
        assert state is FillState.PARTIAL_VISIBLE
        assert "FOAM" in flags[0]


def test_pending_or_ambiguous_without_oil_requires_unknown_review():
    for status in (
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
    ):
        state, visibility, flags = _classify(None, None, status, gray_value=100)
        assert state is FillState.UNKNOWN_REVIEW
        assert visibility <= 0.45
        assert "REVIEW_REQUIRED" in flags


def test_weak_and_glare_rejected_follow_existing_nonfoam_classifier():
    for status in (
        FoamDecisionStatus.WEAK_REJECTED,
        FoamDecisionStatus.GLARE_REJECTED,
    ):
        state, _visibility, flags = _classify(None, None, status, gray_value=100)
        assert state is FillState.FULL_NO_INTERFACE
        assert flags == []


def test_existing_visible_full_and_empty_paths_remain_available():
    oil = _candidate(BoundaryKind.OIL_AIR, 5)
    state, _visibility, _flags = _classify(
        oil, None, FoamDecisionStatus.NO_EVIDENCE, previous=FillState.FULL_NO_INTERFACE
    )
    assert state is FillState.DRAINING_VISIBLE
    full, _visibility, _flags = _classify(
        None,
        None,
        FoamDecisionStatus.NO_EVIDENCE,
        previous=FillState.FULL_NO_INTERFACE,
        gray_value=100,
    )
    empty, _visibility, _flags = _classify(
        None,
        None,
        FoamDecisionStatus.NO_EVIDENCE,
        previous=FillState.EMPTY_NO_INTERFACE,
        gray_value=200,
    )
    assert full is FillState.FULL_NO_INTERFACE
    assert empty is FillState.EMPTY_NO_INTERFACE
