from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Protocol

from oil_tracker.domain.detection import BoundaryCandidate

from .oil_candidate_evidence import OilCandidateEvidence, candidate_is_eligible


class OilCandidateAuthority(IntEnum):
    HARD_INVALID = 0
    CANDIDATE_ONLY = 1
    CONTINUATION_ELIGIBLE = 2
    ANCHOR_ELIGIBLE = 3


class AuthorityReason(str, Enum):
    INELIGIBLE = "ineligible"
    MATERIAL_LAYER_TERMINAL = "material_layer_terminal"
    STATIC_MATERIAL_FRONT_TWIN = "static_material_front_twin"
    BOUNDARY_DOMINANT = "boundary_dominant"
    SEMANTIC_SEQUENCE_ANCHOR = "semantic_sequence_anchor"
    CORROBORATED_MATERIAL_PATH = "corroborated_material_path"
    TERMINAL_MATERIAL_BOUNDARY = "terminal_material_boundary"
    REGISTERED_DYNAMIC_MATERIAL_PATH = "registered_dynamic_material_path"
    MATERIAL_PATH_NO_CORRIDOR = "material_path_no_corridor"
    CONTINUATION = "continuation"
    INSUFFICIENT_AUTHORITY = "insufficient_authority"


@dataclass(frozen=True)
class AuthorityDecision:
    tier: OilCandidateAuthority
    reason: AuthorityReason


@dataclass(frozen=True)
class AuthorityContext:
    representation_support: float = 0.0
    semantic_corridor_support: float = 0.0
    semantic_sequence_available: bool = False
    semantic_sequence_anchor: bool = False
    allow_terminal_anchor: bool = True
    allow_material_layer_terminal: bool = False


class AuthorityThresholds(Protocol):
    anchor_min_material: float
    anchor_min_boundary: float
    anchor_min_boundary_advantage: float
    anchor_max_artifact: float
    anchor_max_ambiguity: float
    continuation_min_material: float
    continuation_min_boundary: float
    continuation_max_artifact: float
    continuation_max_ambiguity: float
    terminal_anchor_min_support: float
    terminal_anchor_min_sector_fraction: float
    dynamic_anchor_min_support: float
    dynamic_anchor_min_coverage: float


def evaluate_candidate_authority(
    candidate: BoundaryCandidate,
    config: AuthorityThresholds,
    context: AuthorityContext,
) -> AuthorityDecision:
    if not candidate_is_eligible(candidate):
        return AuthorityDecision(OilCandidateAuthority.HARD_INVALID, AuthorityReason.INELIGIBLE)

    evidence = OilCandidateEvidence.from_candidate(candidate)
    static_material_front_twin = bool(
        evidence.raw_material_row_support >= 0.60
        and context.representation_support >= 0.20
        and evidence.registered_motion < config.dynamic_anchor_min_support
        and evidence.registered_motion_coverage < config.dynamic_anchor_min_coverage
    )
    material_layer_terminal = bool(
        evidence.material_path
        and evidence.material_layer_topology >= 0.5
        and evidence.terminal_support >= 0.55
        and not context.allow_material_layer_terminal
    )
    if material_layer_terminal:
        return AuthorityDecision(
            OilCandidateAuthority.CANDIDATE_ONLY,
            AuthorityReason.MATERIAL_LAYER_TERMINAL,
        )
    if static_material_front_twin:
        return AuthorityDecision(
            OilCandidateAuthority.CANDIDATE_ONLY,
            AuthorityReason.STATIC_MATERIAL_FRONT_TWIN,
        )

    boundary_dominant = bool(
        not evidence.material_path
        and not evidence.supplemental
        and evidence.material_support >= config.anchor_min_material
        and evidence.boundary >= config.anchor_min_boundary
        and evidence.boundary - evidence.artifact_likelihood
        >= config.anchor_min_boundary_advantage
        and evidence.artifact_signature <= config.anchor_max_artifact
        and evidence.ambiguity <= config.anchor_max_ambiguity
        and evidence.optics_opposition <= 0.38
        and (
            (evidence.narrow_strength >= 0.34 and evidence.horizontal_coverage >= 0.20)
            or (
                evidence.horizontal_coverage >= 0.08
                and float(candidate.features.get("broad_strength", 0.0)) >= 0.42
            )
        )
    )
    corroborated_material_path = bool(
        evidence.material_path
        and (
            not evidence.supplemental
            or (
                evidence.registered_motion >= config.dynamic_anchor_min_support
                and evidence.registered_motion_coverage
                >= config.dynamic_anchor_min_coverage
            )
        )
        and context.representation_support >= 0.24
        and (
            not context.semantic_sequence_available
            or context.semantic_corridor_support >= 0.35
        )
        and evidence.material_support >= 0.30
        and evidence.boundary >= 0.50
        and evidence.artifact_signature <= 0.36
        and evidence.optics_opposition <= 0.30
        and evidence.ambiguity <= 0.55
        and evidence.sector_fraction >= 0.80
        and evidence.static_contradiction <= 0.58
    )
    terminal_material_boundary = bool(
        evidence.material_path
        and not evidence.supplemental
        and context.allow_terminal_anchor
        and (
            evidence.material_layer_topology < 0.5
            or context.allow_material_layer_terminal
        )
        and evidence.terminal_support >= config.terminal_anchor_min_support
        and evidence.material_support >= 0.48
        and evidence.boundary >= 0.48
        and evidence.artifact_signature <= 0.42
        and evidence.optics_opposition <= 0.34
        and evidence.ambiguity <= 0.62
        and (
            evidence.sector_fraction >= config.terminal_anchor_min_sector_fraction
            or (
                evidence.terminal_support >= 0.85
                and evidence.boundary >= 0.70
                and evidence.sector_fraction >= 0.60
            )
        )
        and evidence.static_contradiction <= 0.58
    )
    registered_dynamic_material_path = bool(
        evidence.material_path
        and context.representation_support >= 0.20
        and (
            not context.semantic_sequence_available
            or context.semantic_corridor_support >= 0.10
        )
        and evidence.registered_motion >= config.dynamic_anchor_min_support
        and evidence.registered_motion_coverage >= config.dynamic_anchor_min_coverage
        and evidence.material_support >= 0.30
        and evidence.boundary >= 0.46
        and evidence.artifact_signature <= 0.44
        and evidence.optics_opposition <= 0.38
        and evidence.ambiguity <= 0.68
        and evidence.sector_fraction >= 0.60
    )

    for accepted, reason in (
        (boundary_dominant, AuthorityReason.BOUNDARY_DOMINANT),
        (context.semantic_sequence_anchor, AuthorityReason.SEMANTIC_SEQUENCE_ANCHOR),
        (corroborated_material_path, AuthorityReason.CORROBORATED_MATERIAL_PATH),
        (terminal_material_boundary, AuthorityReason.TERMINAL_MATERIAL_BOUNDARY),
        (registered_dynamic_material_path, AuthorityReason.REGISTERED_DYNAMIC_MATERIAL_PATH),
    ):
        if accepted:
            return AuthorityDecision(OilCandidateAuthority.ANCHOR_ELIGIBLE, reason)

    if (
        evidence.material_path
        and context.semantic_sequence_available
        and context.semantic_corridor_support < 0.20
        and not (
            evidence.registered_motion >= config.dynamic_anchor_min_support
            and evidence.registered_motion_coverage >= config.dynamic_anchor_min_coverage
        )
    ):
        return AuthorityDecision(
            OilCandidateAuthority.CANDIDATE_ONLY,
            AuthorityReason.MATERIAL_PATH_NO_CORRIDOR,
        )

    continuation = bool(
        evidence.material_support >= config.continuation_min_material
        and evidence.boundary >= config.continuation_min_boundary
        and evidence.boundary >= evidence.artifact_likelihood - 0.10
        and evidence.artifact_signature <= config.continuation_max_artifact
        and evidence.ambiguity <= config.continuation_max_ambiguity
        and evidence.optics_opposition <= 0.46
    )
    if continuation:
        return AuthorityDecision(
            OilCandidateAuthority.CONTINUATION_ELIGIBLE,
            AuthorityReason.CONTINUATION,
        )
    return AuthorityDecision(
        OilCandidateAuthority.CANDIDATE_ONLY,
        AuthorityReason.INSUFFICIENT_AUTHORITY,
    )

