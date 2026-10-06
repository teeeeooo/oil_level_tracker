"""Failed predicates explain the selected identity route without changing it."""

from dataclasses import replace

import pytest

from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence
from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolverConfig
from oil_tracker.adapters.vision.oil_phase_identity import (
    OilPhaseIdentity,
    PhaseIdentityContext,
    evaluate_phase_identity,
)
from tests.unit.test_oil_candidate_authority import _candidate


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("artifact_likelihood", 0.53, "boundary_advantage"),
        ("artifact_signature", 0.35, "artifact_signature"),
        ("optics_opposition", 0.39, "optics_opposition"),
    ],
)
def test_scalar_floors_can_pass_while_one_direct_gate_fails(field, value, reason):
    candidate = _candidate()
    evidence = replace(OilCandidateEvidence.from_candidate(candidate), **{field: value})
    decision = evaluate_phase_identity(
        candidate, OilObservationResolverConfig(), PhaseIdentityContext(), evidence
    )

    assert decision.identity is OilPhaseIdentity.CONTINUATION_ONLY
    assert decision.failed_gates == (reason,)


def test_multiple_direct_failures_are_all_reported():
    candidate = _candidate()
    evidence = replace(
        OilCandidateEvidence.from_candidate(candidate),
        artifact_likelihood=0.53, artifact_signature=0.35, optics_opposition=0.39,
    )
    decision = evaluate_phase_identity(
        candidate, OilObservationResolverConfig(), PhaseIdentityContext(), evidence
    )
    assert decision.failed_gates == (
        "boundary_advantage", "artifact_signature", "optics_opposition",
    )


@pytest.mark.parametrize("support", [0.12, 0.15, 0.20])
def test_ordered_lower_diagnostics_use_its_own_representation_and_texture_gates(support):
    candidate = _candidate(texture_conflict_feature=0.90)
    candidate.features["calibrated_high_recall"] = 1.0
    decision = evaluate_phase_identity(
        candidate, OilObservationResolverConfig(),
        PhaseIdentityContext(
            representation_support=support, foam_material_row=50.0,
            foam_seed_age_seconds=4.0, lower_separation_px=8.0,
        ),
    )
    assert decision.identity is OilPhaseIdentity.CONTINUATION_ONLY
    assert decision.ordered_lower
    assert decision.failed_gates == ("ordered_lower_recent_direct_foam",)


def test_ordered_lower_reports_support_below_its_actual_floor():
    decision = evaluate_phase_identity(
        _candidate(), OilObservationResolverConfig(),
        PhaseIdentityContext(
            representation_support=0.119, foam_material_row=50.0,
            foam_seed_age_seconds=1.0, lower_separation_px=8.0,
        ),
    )
    assert decision.identity is OilPhaseIdentity.CONTINUATION_ONLY
    assert decision.failed_gates == ("ordered_lower_cross_representation",)


@pytest.mark.parametrize("ordered_lower", [False, True])
def test_successful_identity_has_no_failed_gates(ordered_lower):
    decision = evaluate_phase_identity(
        _candidate(), OilObservationResolverConfig(),
        PhaseIdentityContext(
            representation_support=0.15,
            foam_material_row=50.0 if ordered_lower else None,
            foam_seed_age_seconds=1.0, lower_separation_px=8.0,
        ),
    )
    expected = OilPhaseIdentity.ORDERED_LOWER_INTERFACE if ordered_lower else OilPhaseIdentity.DIRECT_INTERFACE
    assert decision.identity is expected
    assert decision.failed_gates == ()
