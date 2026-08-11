from __future__ import annotations

import numpy as np
import pytest

from oil_tracker.adapters.vision.foam_front_detector import (
    FoamDecisionStatus,
    FoamDetectionResult,
    FoamEvidenceStrength,
)
from oil_tracker.adapters.vision.foam_temporal_gate import (
    FoamStaticMatch,
    FoamTemporalGate,
)
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
        material_support_mask=zeros_u8.copy(),
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


def test_strong_evidence_requires_two_compatible_samples_then_stays_accepted():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_max_front_jump_px=4.0)
    first = gate.evaluate(
        "glass-1",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 50),
        settings,
    )
    second = gate.evaluate(
        "glass-1",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 52),
        settings,
    )
    third = gate.evaluate(
        "glass-1",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 51),
        settings,
    )

    assert not first.accepted
    assert first.decision_status is FoamDecisionStatus.PERSISTENCE_PENDING
    assert first.pending_count == 1 and first.required_count == 2
    assert second.accepted and third.accepted
    assert second.decision_status is FoamDecisionStatus.ACCEPTED_STRONG
    assert third.pending_count == 2
    assert third.candidate is not None and third.candidate.selected
    assert gate.state_count == 1


def test_strong_front_jump_restarts_onset_confirmation():
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_max_front_jump_px=3.0)
    first = gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 40),
        settings,
    )
    jumped = gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 50),
        settings,
    )
    accepted = gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 51),
        settings,
    )

    assert first.pending_count == 1
    assert not jumped.accepted and jumped.pending_count == 1
    assert jumped.front_delta == 10.0
    assert accepted.accepted and accepted.pending_count == 2


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


def test_compatible_strong_and_moderate_samples_share_one_bounded_chain():
    settings = DetectorSettings(
        foam_persistence_frames=3,
        foam_max_front_jump_px=4.0,
    )

    moderate_then_strong = FoamTemporalGate()
    first = moderate_then_strong.evaluate(
        "g",
        _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 50),
        settings,
    )
    second = moderate_then_strong.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 51),
        settings,
    )
    assert first.pending_count == 1 and not first.accepted
    assert second.pending_count == 2 and second.accepted

    strong_then_moderate = FoamTemporalGate()
    strong = strong_then_moderate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG, 50),
        settings,
    )
    moderate = strong_then_moderate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 51),
        settings,
    )
    confirmed = strong_then_moderate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.MODERATE_EVIDENCE, 52),
        settings,
    )
    assert strong.pending_count == 1 and not strong.accepted
    assert moderate.pending_count == 2 and not moderate.accepted
    assert moderate.required_count == 3
    assert confirmed.pending_count == 3 and confirmed.accepted


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


@pytest.mark.parametrize(
    "status",
    (
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    ),
)
def test_static_dominated_foam_cannot_publish_or_advance_temporal_state(status):
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=2)
    gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.MODERATE_EVIDENCE),
        settings,
    )

    evidence = _evidence(status)
    candidate = evidence.candidate
    decision = gate.evaluate(
        "g",
        evidence,
        settings,
        static_match=FoamStaticMatch(exact_overlap=0.80),
    )

    assert not decision.accepted
    assert decision.candidate is None
    assert decision.decision_status is FoamDecisionStatus.STATIC_REJECTED
    assert decision.evidence_strength is FoamEvidenceStrength.WEAK
    assert decision.pending_count == 0
    assert gate.state_for("g") is None
    assert candidate is not None and candidate.rejected
    assert candidate.reject_reason == "foam_static_artifact_overlap"


def test_static_overlap_boundary_is_bounded_and_validated():
    settings = DetectorSettings()
    gate = FoamTemporalGate()
    pending = gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG),
        settings,
        static_match=FoamStaticMatch(exact_overlap=0.799999),
    )
    retained = gate.evaluate(
        "g",
        _evidence(FoamDecisionStatus.ACCEPTED_STRONG),
        settings,
        static_match=FoamStaticMatch(exact_overlap=0.799999),
    )
    assert not pending.accepted
    assert retained.accepted

    for invalid in (-0.01, 1.01, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="finite and normalized"):
            FoamStaticMatch(exact_overlap=invalid)


def test_registered_static_match_requires_all_conjunctive_support():
    accepted = FoamStaticMatch(
        exact_overlap=0.70,
        tolerant_overlap=0.90,
        reciprocal_overlap=0.70,
        tolerance_radius_px=2,
    )
    assert accepted.dominant

    for match in (
        FoamStaticMatch(0.699999, 1.0, 1.0, 2),
        FoamStaticMatch(0.75, 0.899999, 1.0, 2),
        FoamStaticMatch(0.75, 1.0, 0.699999, 2),
    ):
        assert not match.dominant


@pytest.mark.parametrize(
    "status",
    (
        FoamDecisionStatus.ACCEPTED_STRONG,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    ),
)
def test_fragmented_layer_cannot_publish_or_advance_temporal_state(status):
    gate = FoamTemporalGate()
    settings = DetectorSettings(foam_persistence_frames=2)

    evidence = _evidence(status)
    candidate = evidence.candidate
    decision = gate.evaluate(
        "g",
        evidence,
        settings,
        layer_coherent=False,
    )

    assert not decision.accepted
    assert decision.candidate is None
    assert decision.decision_status is FoamDecisionStatus.INCOHERENT_REJECTED
    assert decision.evidence_strength is FoamEvidenceStrength.WEAK
    assert gate.state_for("g") is None
    assert candidate is not None and candidate.rejected
    assert candidate.reject_reason == "foam_layer_row_topology_fragmented"
