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


_STATIC_FOAM_EXACT_DOMINANCE_FRACTION = 0.80
_STATIC_FOAM_REGISTERED_MIN_EXACT_FRACTION = 0.70
_STATIC_FOAM_REGISTERED_MIN_CURRENT_FRACTION = 0.90
_STATIC_FOAM_REGISTERED_MIN_RECIPROCAL_FRACTION = 0.70
_STRONG_FOAM_CONFIRMATION_FRAMES = 2


@dataclass(frozen=True)
class FoamStaticMatch:
    exact_overlap: float = 0.0
    tolerant_overlap: float = 0.0
    reciprocal_overlap: float = 0.0
    tolerance_radius_px: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("exact overlap", self.exact_overlap),
            ("tolerant overlap", self.tolerant_overlap),
            ("reciprocal overlap", self.reciprocal_overlap),
        ):
            if not math.isfinite(float(value)) or not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"Foam static {name} must be finite and normalized.")
        if type(self.tolerance_radius_px) is not int or self.tolerance_radius_px < 0:
            raise ValueError("Foam static tolerance radius must be a non-negative integer.")

    @property
    def dominant(self) -> bool:
        exact = float(self.exact_overlap)
        return bool(
            exact >= _STATIC_FOAM_EXACT_DOMINANCE_FRACTION
            or (
                exact >= _STATIC_FOAM_REGISTERED_MIN_EXACT_FRACTION
                and float(self.tolerant_overlap)
                >= _STATIC_FOAM_REGISTERED_MIN_CURRENT_FRACTION
                and float(self.reciprocal_overlap)
                >= _STATIC_FOAM_REGISTERED_MIN_RECIPROCAL_FRACTION
            )
        )


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
    """Bounded per-Glass publication gate for strong/moderate Foam evidence.

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
        static_match: FoamStaticMatch | None = None,
        layer_coherent: bool = True,
    ) -> FoamTemporalDecision:
        key = str(glass_id)
        match = FoamStaticMatch() if static_match is None else static_match
        if type(match) is not FoamStaticMatch:
            raise TypeError("Foam temporal gate requires FoamStaticMatch evidence.")
        required = max(1, int(settings.foam_persistence_frames))
        candidate = evidence.candidate
        status = evidence.decision_status
        decision_required = (
            _STRONG_FOAM_CONFIRMATION_FRAMES
            if status is FoamDecisionStatus.ACCEPTED_STRONG
            else required
        )

        if (
            candidate is not None
            and status
            in {
                FoamDecisionStatus.ACCEPTED_STRONG,
                FoamDecisionStatus.MODERATE_EVIDENCE,
            }
            and match.dominant
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
                required_count=decision_required,
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
                required_count=decision_required,
                front_delta=None,
            )

        if status is FoamDecisionStatus.ACCEPTED_STRONG and candidate is not None:
            previous = self._states.get(key)
            delta = (
                None
                if previous is None or previous.last_y is None
                else abs(float(candidate.y) - previous.last_y)
            )
            max_jump = max(0.0, float(settings.foam_max_front_jump_px))
            continuous = previous is not None and delta is not None and delta <= max_jump
            pending_count = min(
                _STRONG_FOAM_CONFIRMATION_FRAMES,
                previous.pending_count + 1 if continuous else 1,
            )
            self._states[key] = FoamTemporalState(
                pending_count=pending_count,
                last_y=float(candidate.y),
                last_score=float(candidate.final_score),
            )
            if pending_count < _STRONG_FOAM_CONFIRMATION_FRAMES:
                candidate.selected = False
                candidate.rejected = True
                candidate.reject_reason = "foam_persistence_pending"
                return FoamTemporalDecision(
                    candidate=None,
                    accepted=False,
                    evidence_strength=FoamEvidenceStrength.STRONG,
                    decision_status=FoamDecisionStatus.PERSISTENCE_PENDING,
                    pending_count=pending_count,
                    required_count=_STRONG_FOAM_CONFIRMATION_FRAMES,
                    front_delta=delta,
                )
            candidate.selected = True
            candidate.rejected = False
            candidate.reject_reason = ""
            return FoamTemporalDecision(
                candidate=candidate,
                accepted=True,
                evidence_strength=FoamEvidenceStrength.STRONG,
                decision_status=FoamDecisionStatus.ACCEPTED_STRONG,
                pending_count=pending_count,
                required_count=_STRONG_FOAM_CONFIRMATION_FRAMES,
                front_delta=delta,
            )

        if status is FoamDecisionStatus.MODERATE_EVIDENCE and candidate is not None:
            previous = self._states.get(key)
            delta = None if previous is None or previous.last_y is None else abs(float(candidate.y) - previous.last_y)
            max_jump = max(0.0, float(settings.foam_max_front_jump_px))
            continuous = previous is not None and delta is not None and delta <= max_jump
            pending_count = min(
                required,
                previous.pending_count + 1 if continuous else 1,
            )
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
