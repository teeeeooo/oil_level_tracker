from __future__ import annotations

from dataclasses import replace

import numpy as np

from oil_tracker.adapters.vision.foam_front_detector import (
    FoamDecisionStatus,
    FoamDetectionResult,
    FoamEvidenceStrength,
)
from oil_tracker.adapters.vision.foam_temporal_gate import FoamTemporalGate
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


def _evidence(status: FoamDecisionStatus, y: float = 50.0, score: float = 0.60):
    shape = (20, 20)
    zeros_f = np.zeros(shape, dtype=np.float32)
    zeros_u8 = np.zeros(shape, dtype=np.uint8)
    candidate = BoundaryCandidate(
        source="test_foam",
        kind=BoundaryKind.FOAM_FRONT,
        y=y,
        features={"foam_score": score},
        feature_score=score,
        final_score=score,
    )
    strength = (
        FoamEvidenceStrength.STRONG
        if status is FoamDecisionStatus.ACCEPTED_STRONG
        else FoamEvidenceStrength.MODERATE
        if status is FoamDecisionStatus.MODERATE_EVIDENCE
        else FoamEvidenceStrength.WEAK
    )
    return FoamDetectionResult(
        mask=zeros_u8,
        variance_map=zeros_f,
        edge_density_map=zeros_f,
        whiteness_map=zeros_f,
        texture_evidence_map=zeros_f,
        glare_excluded_mask=zeros_u8,
        combined_evidence_map=zeros_f,
        candidate=candidate,
        components=(),
        selected_component=None,
        final_evidence_score=score,
        evidence_strength=strength,
        decision_status=status,
        ambiguous=status is FoamDecisionStatus.AMBIGUOUS,
        bottom_connected_area_ratio=0.1,
        whiteness_ratio=0.5,
        texture_support_ratio=0.5,
        glare_overlap_ratio=0.0,
        component_height_ratio=0.3,
        component_width_ratio=0.5,
        bounding_box_fill_ratio=0.5,
        front_y=y,
    )


def test_strong_evidence_is_accepted_immediately():
    gate = FoamTemporalGate()
    decision = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.ACCEPTED_STRONG), DetectorSettings())
    assert decision.accepted
    assert decision.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert decision.candidate is not None and decision.candidate.selected
    assert gate.state_count == 0


def test_moderate_evidence_requires_persistence_and_accepts_current_candidate():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=3, foam_max_front_jump_px=4.0)
    first = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 50), settings)
    second = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 52), settings)
    third = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 51), settings)
    assert not first.accepted and first.pending_count == 1
    assert not second.accepted and second.pending_count == 2
    assert third.accepted and third.pending_count == 3
    assert third.decision_status is FoamDecisionStatus.ACCEPTED_MODERATE


def test_transient_shimmer_dropout_and_jump_restart_chain():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=2, foam_max_front_jump_px=3.0)
    pending = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 50), settings)
    dropped = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.WEAK_REJECTED, 50), settings)
    restarted = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 50), settings)
    jumped = gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 60), settings)
    assert pending.pending_count == 1
    assert not dropped.accepted and gate.state_count == 1
    assert restarted.pending_count == 1
    assert jumped.pending_count == 1
    assert jumped.front_delta == 10.0


def test_glass_isolation_reset_one_and_reset_all():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=3)
    gate.evaluate("glass-1", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE), settings)
    gate.evaluate("glass-2", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE), settings)
    assert gate.state_count == 2
    gate.reset("glass-1")
    assert gate.state_for("glass-1") is None
    assert gate.state_for("glass-2") is not None
    gate.reset()
    assert gate.state_count == 0


def test_state_is_bounded_scalar_only_and_repeated_sequence_is_deterministic():
    settings = DetectorSettings(foam_persistence_frames=2)
    outputs = []
    for _ in range(2):
        gate = FoamTemporalGate()
        sequence = [
            gate.evaluate("g", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 40), settings),
            gate.evaluate("g", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 41), settings),
        ]
        state = gate.state_for("g")
        assert state is not None
        assert set(vars(state)) == {"pending_count", "last_y", "last_score"}
        assert not any(isinstance(value, np.ndarray) for value in vars(state).values())
        outputs.append([(item.accepted, item.pending_count, item.decision_status) for item in sequence])
    assert outputs[0] == outputs[1]


def test_ambiguous_and_glare_rejected_never_advance_pending_state():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=2)
    gate.evaluate("g", _evidence(FoamDecisionStatus.MODERATE_EVIDENCE), settings)
    for status in (FoamDecisionStatus.AMBIGUOUS, FoamDecisionStatus.GLARE_REJECTED):
        decision = gate.evaluate("g", _evidence(status), settings)
        assert not decision.accepted
        assert decision.decision_status is status
        assert gate.state_for("g") is None
