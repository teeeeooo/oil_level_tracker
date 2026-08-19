from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from oil_tracker.domain.detection import BoundaryCandidate

from .oil_candidate_evidence import OilCandidateEvidence


class OilPhaseIdentity(str, Enum):
    CONTINUATION_ONLY = "continuation_only"
    DIRECT_INTERFACE = "direct_interface"
    ORDERED_LOWER_INTERFACE = "ordered_lower_interface"
    OPPOSED_MATERIAL = "opposed_material"


@dataclass(frozen=True)
class PhaseIdentityContext:
    representation_support: float = 0.0
    foam_material_identity: float = 0.0
    foam_material_row: float | None = None
    lower_separation_px: float = 0.0


@dataclass(frozen=True)
class PhaseIdentityDecision:
    identity: OilPhaseIdentity
    ordered_lower: bool = False
    failed_gates: tuple[str, ...] = ()

    @property
    def independently_identified(self) -> bool:
        return self.identity in {
            OilPhaseIdentity.DIRECT_INTERFACE,
            OilPhaseIdentity.ORDERED_LOWER_INTERFACE,
        }


class PhaseIdentityThresholds(Protocol):
    anchor_min_material: float
    anchor_min_boundary: float
    anchor_min_boundary_advantage: float
    anchor_max_artifact: float
    anchor_max_ambiguity: float


def evaluate_phase_identity(
    candidate: BoundaryCandidate,
    config: PhaseIdentityThresholds,
    context: PhaseIdentityContext,
) -> PhaseIdentityDecision:
    """Classify physical Oil identity before authority or trajectory policy."""

    evidence = OilCandidateEvidence.from_candidate(candidate)
    if context.foam_material_identity >= 0.50:
        return PhaseIdentityDecision(
            OilPhaseIdentity.OPPOSED_MATERIAL,
            failed_gates=("independent_from_foam_material_track",),
        )

    ordered_lower = bool(
        context.foam_material_row is not None
        and float(candidate.y)
        >= float(context.foam_material_row) + max(0.0, context.lower_separation_px)
        and context.foam_material_identity < 0.20
    )
    localized_boundary = bool(
        (
            evidence.narrow_strength >= 0.34
            and evidence.horizontal_coverage >= 0.20
        )
        or (
            evidence.horizontal_coverage >= 0.08
            and float(candidate.features.get("broad_strength", 0.0)) >= 0.42
        )
    )
    direct_quality = bool(
        evidence.availability.phase
        and evidence.material_support >= config.anchor_min_material
        and evidence.boundary >= config.anchor_min_boundary
        and evidence.boundary - evidence.artifact_likelihood
        >= config.anchor_min_boundary_advantage
        and evidence.artifact_signature <= config.anchor_max_artifact
        and evidence.ambiguity <= config.anchor_max_ambiguity
        and evidence.optics_opposition <= 0.38
        and localized_boundary
    )
    texture_clean = bool(
        evidence.availability.material_texture
        and evidence.material_texture_conflict < 0.60
    )

    if (
        ordered_lower
        and direct_quality
        and context.representation_support >= 0.20
        and (
            float(candidate.features.get("phase_transition_scan", 0.0)) < 0.5
            or texture_clean
        )
    ):
        return PhaseIdentityDecision(
            OilPhaseIdentity.ORDERED_LOWER_INTERFACE,
            ordered_lower=True,
        )
    if direct_quality and texture_clean:
        return PhaseIdentityDecision(OilPhaseIdentity.DIRECT_INTERFACE)

    failed: list[str] = []
    if not evidence.availability.phase:
        failed.append("phase_evidence_available")
    if evidence.material_support < config.anchor_min_material:
        failed.append("material_support")
    if evidence.boundary < config.anchor_min_boundary:
        failed.append("boundary")
    if evidence.ambiguity > config.anchor_max_ambiguity:
        failed.append("ambiguity")
    if not localized_boundary:
        failed.append("localized_boundary")
    if not texture_clean and not ordered_lower:
        failed.append("material_texture_clean_or_ordered_lower")
    if ordered_lower and context.representation_support < 0.20:
        failed.append("ordered_lower_cross_representation")
    return PhaseIdentityDecision(
        OilPhaseIdentity.CONTINUATION_ONLY,
        ordered_lower=ordered_lower,
        failed_gates=tuple(failed),
    )
