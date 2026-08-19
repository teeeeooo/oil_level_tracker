from __future__ import annotations

from dataclasses import dataclass

from oil_tracker.domain.detection import BoundaryCandidate

from .oil_candidate_authority import AuthorityReason, OilCandidateAuthority
from .oil_phase_identity import OilPhaseIdentity


@dataclass(frozen=True)
class OilCandidateRef:
    frame_offset: int
    candidate_offset: int
    candidate: BoundaryCandidate
    local_quality: float
    authority: OilCandidateAuthority
    initial_authority: OilCandidateAuthority = OilCandidateAuthority.CANDIDATE_ONLY
    post_track_authority: OilCandidateAuthority = OilCandidateAuthority.CANDIDATE_ONLY
    representation_support: float = 0.0
    semantic_corridor_support: float = 0.0
    terminal_fallback: bool = False
    cluster_support: float = 0.0
    trajectory_support: float = 0.0
    track_opposition: float = 0.0
    foam_alias_penalty: float = 0.0
    authority_reason: AuthorityReason = AuthorityReason.INSUFFICIENT_AUTHORITY
    authority_failed_gates: tuple[str, ...] = ()
    foam_material_identity: float = 0.0
    phase_identity: OilPhaseIdentity = OilPhaseIdentity.CONTINUATION_ONLY
    phase_identity_failed_gates: tuple[str, ...] = ()
    ordered_lower: bool = False


@dataclass(frozen=True)
class OilSequenceNode:
    kind: str
    emission: float
    identity: str
    candidate_ref: OilCandidateRef | None = None
    state_evidence: float = 0.0

    @property
    def y(self) -> float | None:
        if self.candidate_ref is None:
            return None
        return float(self.candidate_ref.candidate.y)
