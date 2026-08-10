from __future__ import annotations

import math
from dataclasses import dataclass

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.recipe import DetectorSettings

from .foam_front_detector import (
    FoamDecisionStatus,
    FoamDetectionResult,
    FoamEvidenceStrength,
)


_STATIC_FOAM_DOMINANCE_FRACTION = 0.80


@dataclass(frozen=True)
class FoamTemporalState:
    pending_count: int = 0
    last_y: float | None = None
    last_score: float = 0.0


@dataclass(frozen=True)
class FoamTemporalDecision:
    candidate: BoundaryCandidate | None
    accepted: bool
    evidence_strength: FoamEvidenceStrength
    decision_status: FoamDecisionStatus
    pending_count: int
    required_count: int
    front_delta: float | None


class FoamTemporalGate:
    """Bounded per-Glass persistence gate for moderate Foam evidence.

    The gate stores only counters and finite scalar evidence. It never retains an
    image, map, mask or candidate object between samples.
    """

    def __init__(self) -> None:
        self._states: dict[str, FoamTemporalState] = {}

    @property
    def state_count(self) -> int:
        return len(self._states)

    def state_for(self, glass_id: str) -> FoamTemporalState | None:
        return self._states.get(str(glass_id))

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._states.clear()
        else:
            self._states.pop(str(glass_id), None)

    def evaluate(
        self,
        glass_id: str,
        evidence: FoamDetectionResult,
        settings: DetectorSettings,
        *,
        static_overlap_ratio: float = 0.0,
        layer_coherent: bool = True,
    ) -> FoamTemporalDecision:
        key = str(glass_id)
        static_overlap = float(static_overlap_ratio)
        if not math.isfinite(static_overlap) or not 0.0 <= static_overlap <= 1.0:
            raise ValueError("Foam static overlap must be finite and normalized.")
        required = max(1, int(settings.foam_persistence_frames))
        candidate = evidence.candidate
        status = evidence.decision_status

        if (
            candidate is not None
            and status
            in {
                FoamDecisionStatus.ACCEPTED_STRONG,
                FoamDecisionStatus.MODERATE_EVIDENCE,
            }
            and static_overlap >= _STATIC_FOAM_DOMINANCE_FRACTION
        ):
            self._states.pop(key, None)
            candidate.selected = False
            candidate.rejected = True
            candidate.reject_reason = "foam_static_artifact_overlap"
            return FoamTemporalDecision(
                candidate=None,
                accepted=False,
                evidence_strength=FoamEvidenceStrength.WEAK,
                decision_status=FoamDecisionStatus.STATIC_REJECTED,
                pending_count=0,
                required_count=required,
                front_delta=None,
            )

        if (
            candidate is not None
            and status
            in {
                FoamDecisionStatus.ACCEPTED_STRONG,
                FoamDecisionStatus.MODERATE_EVIDENCE,
            }
            and not bool(layer_coherent)
        ):
            self._states.pop(key, None)
            candidate.selected = False
            candidate.rejected = True
            candidate.reject_reason = "foam_layer_row_topology_fragmented"
            return FoamTemporalDecision(
                candidate=None,
                accepted=False,
                evidence_strength=FoamEvidenceStrength.WEAK,
                decision_status=FoamDecisionStatus.INCOHERENT_REJECTED,
                pending_count=0,
                required_count=required,
                front_delta=None,
            )

        if status is FoamDecisionStatus.ACCEPTED_STRONG and candidate is not None:
            self._states.pop(key, None)
            candidate.selected = True
            candidate.rejected = False
            candidate.reject_reason = ""
            return FoamTemporalDecision(
                candidate=candidate,
                accepted=True,
                evidence_strength=FoamEvidenceStrength.STRONG,
                decision_status=FoamDecisionStatus.ACCEPTED_STRONG,
                pending_count=required,
                required_count=required,
                front_delta=None,
            )

        if status is FoamDecisionStatus.MODERATE_EVIDENCE and candidate is not None:
            previous = self._states.get(key)
            delta = None if previous is None or previous.last_y is None else abs(float(candidate.y) - previous.last_y)
            max_jump = max(0.0, float(settings.foam_max_front_jump_px))
            continuous = previous is not None and delta is not None and delta <= max_jump
            pending_count = previous.pending_count + 1 if continuous else 1
            state = FoamTemporalState(
                pending_count=pending_count,
                last_y=float(candidate.y),
                last_score=float(candidate.final_score),
            )
            self._states[key] = state
            if pending_count >= required:
                candidate.selected = True
                candidate.rejected = False
                candidate.reject_reason = ""
                return FoamTemporalDecision(
                    candidate=candidate,
                    accepted=True,
                    evidence_strength=FoamEvidenceStrength.MODERATE,
                    decision_status=FoamDecisionStatus.ACCEPTED_MODERATE,
                    pending_count=pending_count,
                    required_count=required,
                    front_delta=delta,
                )
            candidate.selected = False
            candidate.rejected = True
            candidate.reject_reason = "foam_persistence_pending"
            return FoamTemporalDecision(
                candidate=None,
                accepted=False,
                evidence_strength=FoamEvidenceStrength.MODERATE,
                decision_status=FoamDecisionStatus.PERSISTENCE_PENDING,
                pending_count=pending_count,
                required_count=required,
                front_delta=delta,
            )

        # A dropout, weak component, glare conflict or ambiguity breaks the
        # moderate-evidence chain immediately. This deterministic policy avoids
        # accepting isolated shimmer separated by missing samples.
        self._states.pop(key, None)
        return FoamTemporalDecision(
            candidate=None,
            accepted=False,
            evidence_strength=evidence.evidence_strength,
            decision_status=status,
            pending_count=0,
            required_count=required,
            front_delta=None,
        )
