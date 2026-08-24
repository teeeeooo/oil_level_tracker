from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from oil_tracker.domain.detection import BoundaryCandidate

from .oil_candidate_authority import AuthorityReason, OilCandidateAuthority
from .oil_candidate_evidence import OilCandidateEvidence
from .oil_phase_identity import OilPhaseIdentity


class TrackletLifecycle(str, Enum):
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"
    CONTINUING = "continuing"
    LOST = "lost"
    TERMINATED = "terminated"


class TrackletConfirmationProfile(str, Enum):
    NONE = "none"
    ANCHOR_CORRIDOR = "anchor_corridor"
    ANCHOR_TRAJECTORY = "anchor_trajectory"
    ENTRANCE_MOTION = "entrance_motion"
    MOTION_TRAJECTORY = "motion_trajectory"


@dataclass(frozen=True)
class OilCandidateRef:
    frame_offset: int
    candidate_offset: int
    candidate: BoundaryCandidate
    evidence: OilCandidateEvidence
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
    tracklet_id: str | None = None
    row_hypothesis_id: str | None = None
    tracklet_lifecycle: TrackletLifecycle = TrackletLifecycle.PROVISIONAL
    tracklet_admitted: bool = False
    tracklet_confirmation_profile: TrackletConfirmationProfile = (
        TrackletConfirmationProfile.NONE
    )
    tracklet_confirmation_support: float = 0.0
    tracklet_net_progress_px: float = 0.0
    tracklet_direction: int = 0
    tracklet_directional_agreement: float = 0.0
    tracklet_motion_support: float = 0.0
    tracklet_motion_coverage: float = 0.0
    tracklet_material_conflict: float = 0.0
    tracklet_incompatible: bool = False
    tracklet_failure_reason: str = ""


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
