from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.fill_state_classifier import classify_fill_state
from oil_tracker.adapters.vision.foam_front_detector import FoamDecisionStatus
from oil_tracker.adapters.vision.oil_temporal_path import OilDecisionStatus
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def image(value: int):
    return np.full((48, 64), value, dtype=np.uint8)


def mask():
    return np.full((48, 64), 255, dtype=np.uint8)


def oil(y: float = 24.0):
    candidate = BoundaryCandidate("oil_consensus", BoundaryKind.OIL_AIR, y)
    candidate.selected = True
    candidate.final_score = 0.9
    return candidate


def foam(y: float = 12.0):
    candidate = BoundaryCandidate("foam_component", BoundaryKind.FOAM_FRONT, y)
    candidate.selected = True
    candidate.final_score = 0.9
    return candidate


def test_accepted_oil_uses_visible_state_and_accepted_foam_overrides():
    settings = DetectorSettings()
    state, _visibility, flags = classify_fill_state(
        image(120), mask(), np.zeros((48, 64), dtype=np.uint8), oil(), None, None, settings,
        oil_status=OilDecisionStatus.ACCEPTED_BOUNDARY,
    )
    assert state is FillState.PARTIAL_VISIBLE
    assert "REVIEW_REQUIRED" not in flags
    state, _visibility, _flags = classify_fill_state(
        image(120), mask(), np.zeros((48, 64), dtype=np.uint8), oil(), foam(), None, settings,
        foam_status=FoamDecisionStatus.ACCEPTED_STRONG,
        oil_status=OilDecisionStatus.ACCEPTED_BOUNDARY,
    )
    assert state is FillState.FOAMING_VISIBLE


def test_pending_ambiguous_and_low_margin_oil_require_review_without_numeric_candidate():
    settings = DetectorSettings()
    for status in (
        OilDecisionStatus.PATH_PENDING,
        OilDecisionStatus.AMBIGUOUS,
        OilDecisionStatus.REACQUISITION_PENDING,
        OilDecisionStatus.LOW_MARGIN,
        OilDecisionStatus.REJECTED_BOUNDARY,
        OilDecisionStatus.UNAVAILABLE,
    ):
        state, _visibility, flags = classify_fill_state(
            image(120), mask(), np.zeros((48, 64), dtype=np.uint8), None, None, None, settings,
            oil_status=status,
        )
        assert state is FillState.UNKNOWN_REVIEW
        assert "REVIEW_REQUIRED" in flags


def test_no_interface_full_empty_and_ambiguous_use_image_evidence():
    settings = DetectorSettings()
    full, _visibility, _flags = classify_fill_state(
        image(65), mask(), np.zeros((48, 64), dtype=np.uint8), None, None,
        FillState.FULL_NO_INTERFACE, settings,
        oil_status=OilDecisionStatus.NO_INTERFACE_SELECTED,
    )
    empty, _visibility, _flags = classify_fill_state(
        image(205), mask(), np.zeros((48, 64), dtype=np.uint8), None, None,
        FillState.EMPTY_NO_INTERFACE, settings,
        oil_status=OilDecisionStatus.NO_INTERFACE_SELECTED,
    )
    ambiguous, _visibility, flags = classify_fill_state(
        image(130), mask(), np.zeros((48, 64), dtype=np.uint8), None, None,
        None, settings,
        oil_status=OilDecisionStatus.NO_INTERFACE_SELECTED,
    )
    assert full is FillState.FULL_NO_INTERFACE
    assert empty is FillState.EMPTY_NO_INTERFACE
    assert ambiguous is FillState.UNKNOWN_REVIEW
    assert "REVIEW_REQUIRED" in flags


def test_accepted_foam_remains_authoritative_without_oil_boundary():
    state, _visibility, flags = classify_fill_state(
        image(100), mask(), np.zeros((48, 64), dtype=np.uint8), None, foam(), None,
        DetectorSettings(),
        foam_status=FoamDecisionStatus.ACCEPTED_STRONG,
        oil_status=OilDecisionStatus.PATH_PENDING,
    )
    assert state is FillState.FULL_WITH_FOAM
    assert "REVIEW_REQUIRED" not in flags


def test_foam_pending_with_no_accepted_oil_requires_review():
    state, _visibility, flags = classify_fill_state(
        image(100), mask(), np.zeros((48, 64), dtype=np.uint8), None, None, None,
        DetectorSettings(),
        foam_status=FoamDecisionStatus.PERSISTENCE_PENDING,
        oil_status=OilDecisionStatus.NO_INTERFACE_SELECTED,
    )
    assert state is FillState.UNKNOWN_REVIEW
    assert "FOAM_PERSISTENCE_PENDING" in flags
    assert "REVIEW_REQUIRED" in flags
