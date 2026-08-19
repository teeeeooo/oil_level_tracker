from __future__ import annotations

from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityContext,
    AuthorityReason,
    OilCandidateAuthority,
    evaluate_candidate_authority,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence
from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilObservationResolverConfig,
)
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


def _candidate(
    *,
    boundary: float = 0.60,
    material_path: bool = False,
    sector_fraction: float = 0.90,
    motion: float = 0.0,
    motion_coverage: float = 0.0,
    texture_conflict_feature: float = 0.0,
    texture_conflict_penalty: float = 0.0,
) -> BoundaryCandidate:
    return BoundaryCandidate(
        source="test",
        kind=BoundaryKind.OIL_AIR,
        y=100.0,
        features={
            "sequence_eligible": 1.0,
            "boundary_likelihood": boundary,
            "artifact_likelihood": 0.05,
            "ambiguity_likelihood": 0.10,
            "broad_strength": 0.70,
            "narrow_peak_strength": 0.65,
            "narrow_horizontal_coverage": 0.70,
            "broad_scale_consistency": 0.75,
            "polarity_confidence": 0.70,
            "r6_material_path": float(material_path),
            "material_path_sector_fraction": sector_fraction,
            "registered_oil_band_motion_support": motion,
            "registered_oil_band_motion_coverage": motion_coverage,
            "material_texture_conflict": texture_conflict_feature,
        },
        penalties={
            "artifact_likelihood": 0.05,
            "material_texture_conflict": texture_conflict_penalty,
        },
        feature_score=boundary,
        final_score=boundary,
    )


def test_boundary_dominant_candidate_reports_named_anchor_reason() -> None:
    decision = evaluate_candidate_authority(
        _candidate(),
        OilObservationResolverConfig(),
        AuthorityContext(),
    )

    assert decision.tier is OilCandidateAuthority.ANCHOR_ELIGIBLE
    assert decision.reason is AuthorityReason.BOUNDARY_DOMINANT


def test_registered_material_motion_corroborates_direct_phase_identity() -> None:
    decision = evaluate_candidate_authority(
        _candidate(
            boundary=0.50,
            material_path=True,
            motion=0.80,
            motion_coverage=0.80,
        ),
        OilObservationResolverConfig(),
        AuthorityContext(representation_support=0.24),
    )

    assert decision.tier is OilCandidateAuthority.ANCHOR_ELIGIBLE
    assert decision.reason is AuthorityReason.CORROBORATED_MATERIAL_PATH


def test_material_path_without_semantic_corridor_reports_hard_branch() -> None:
    decision = evaluate_candidate_authority(
        _candidate(material_path=True),
        OilObservationResolverConfig(),
        AuthorityContext(
            representation_support=0.10,
            semantic_sequence_available=True,
            semantic_corridor_support=0.0,
        ),
    )

    assert decision.tier is OilCandidateAuthority.CANDIDATE_ONLY
    assert decision.reason is AuthorityReason.MATERIAL_PATH_NO_CORRIDOR


def test_typed_evidence_uses_strongest_texture_conflict_source() -> None:
    evidence = OilCandidateEvidence.from_candidate(
        _candidate(
            texture_conflict_feature=0.35,
            texture_conflict_penalty=0.72,
        )
    )

    assert evidence.material_texture_conflict == 0.72


def test_typed_evidence_distinguishes_missing_from_measured_zero() -> None:
    measured = OilCandidateEvidence.from_candidate(_candidate())
    missing_candidate = _candidate()
    missing_candidate.features.pop("material_texture_conflict")
    missing_candidate.penalties.pop("material_texture_conflict")
    missing_candidate.features.pop("registered_oil_band_motion_support")
    missing_candidate.features.pop("registered_oil_band_motion_coverage")
    missing = OilCandidateEvidence.from_candidate(missing_candidate)

    assert measured.material_texture_conflict == missing.material_texture_conflict == 0.0
    assert measured.availability.material_texture
    assert measured.availability.motion
    assert not missing.availability.material_texture
    assert not missing.availability.motion


def test_terminal_support_only_relaxes_static_material_path() -> None:
    ordinary = _candidate()
    ordinary.features.update(
        {
            "material_terminal_partition_support": 1.0,
            "static_prior_contribution": 0.8,
        }
    )
    material = _candidate(material_path=True)
    material.features.update(
        {
            "material_terminal_partition_support": 1.0,
            "static_prior_contribution": 0.8,
        }
    )

    assert OilCandidateEvidence.from_candidate(ordinary).static_contradiction == 0.8
    assert OilCandidateEvidence.from_candidate(material).static_contradiction < 0.2


def test_dynamic_material_texture_conflict_is_named_candidate_only_reason() -> None:
    decision = evaluate_candidate_authority(
        _candidate(
            boundary=0.48,
            material_path=True,
            motion=0.80,
            motion_coverage=0.80,
            texture_conflict_feature=0.75,
        ),
        OilObservationResolverConfig(),
        AuthorityContext(representation_support=0.21),
    )

    assert decision.tier is OilCandidateAuthority.CANDIDATE_ONLY
    assert decision.reason is AuthorityReason.MATERIAL_TEXTURE_CONFLICT
    assert decision.failed_gates == ("material_texture_conflict<0.60",)


def test_foam_material_identity_blocks_matching_candidate_not_independent_row() -> None:
    material_decision = evaluate_candidate_authority(
        _candidate(boundary=0.80, material_path=True, motion=0.80, motion_coverage=1.0),
        OilObservationResolverConfig(),
        AuthorityContext(
            representation_support=0.80,
            foam_material_identity=0.90,
        ),
    )
    lower_decision = evaluate_candidate_authority(
        _candidate(boundary=0.48),
        OilObservationResolverConfig(),
        AuthorityContext(),
    )

    assert material_decision.tier is OilCandidateAuthority.CANDIDATE_ONLY
    assert material_decision.reason is AuthorityReason.FOAM_MATERIAL_IDENTITY
    # A geometrically separate ordinary row uses only its own Oil evidence.
    assert lower_decision.reason is AuthorityReason.BOUNDARY_DOMINANT


def test_high_conflict_ordinary_candidate_cannot_bypass_typed_phase_identity() -> None:
    decision = evaluate_candidate_authority(
        _candidate(texture_conflict_feature=0.82),
        OilObservationResolverConfig(),
        AuthorityContext(
            semantic_sequence_available=True,
            semantic_corridor_support=1.0,
        ),
    )

    assert decision.tier is OilCandidateAuthority.CONTINUATION_ELIGIBLE
    assert decision.reason is AuthorityReason.CONTINUATION
    assert "material_texture_clean_or_ordered_lower" in decision.failed_gates


def test_strong_ordered_lower_interface_can_anchor_despite_broad_mask_conflict() -> None:
    decision = evaluate_candidate_authority(
        _candidate(texture_conflict_feature=0.82),
        OilObservationResolverConfig(),
        AuthorityContext(
            representation_support=0.60,
            foam_material_row=50.0,
            lower_separation_px=8.0,
        ),
    )

    assert decision.tier is OilCandidateAuthority.ANCHOR_ELIGIBLE
    assert decision.reason is AuthorityReason.ORDERED_LOWER_INTERFACE


def test_distributed_phase_scan_anchors_only_with_strong_direct_identity() -> None:
    candidate = _candidate()
    candidate.features.update(
        {
            "supplemental_path": 1.0,
            "calibrated_high_recall": 1.0,
            "phase_transition_scan": 1.0,
            "broad_scale_consistency": 0.80,
        }
    )

    decision = evaluate_candidate_authority(
        candidate,
        OilObservationResolverConfig(),
        AuthorityContext(),
    )

    assert decision.tier is OilCandidateAuthority.ANCHOR_ELIGIBLE
    assert decision.reason is AuthorityReason.DISTRIBUTED_PHASE_INTERFACE


def test_high_conflict_phase_scan_cannot_use_ordered_lower_exception() -> None:
    candidate = _candidate(texture_conflict_feature=0.82)
    candidate.features.update(
        {
            "supplemental_path": 1.0,
            "calibrated_high_recall": 1.0,
            "phase_transition_scan": 1.0,
            "broad_scale_consistency": 0.80,
        }
    )

    decision = evaluate_candidate_authority(
        candidate,
        OilObservationResolverConfig(),
        AuthorityContext(
            representation_support=0.60,
            foam_material_row=50.0,
            lower_separation_px=8.0,
        ),
    )

    assert decision.tier is OilCandidateAuthority.CONTINUATION_ELIGIBLE
    assert decision.reason is AuthorityReason.CONTINUATION
