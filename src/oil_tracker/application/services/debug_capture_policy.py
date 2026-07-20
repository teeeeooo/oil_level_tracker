from __future__ import annotations

from dataclasses import dataclass

from oil_tracker.domain.debug_trace import DebugCaptureDecision, DebugCaptureReason
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.session import DebugTraceLevel


@dataclass(frozen=True)
class DebugCapturePolicyConfig:
    oil_position_jump_ratio: float = 0.20
    foam_position_jump_ratio: float = 0.20
    candidate_ambiguity_score_gap: float = 0.08


class DebugCapturePolicy:
    """Pure application policy; it has no Qt or storage dependency."""

    def __init__(self, config: DebugCapturePolicyConfig | None = None) -> None:
        self.config = config or DebugCapturePolicyConfig()

    def decide(
        self,
        level: DebugTraceLevel,
        detection,
        *,
        is_valid: bool,
        minimum_confidence: float,
        effective_height: float,
        first_sample: bool = False,
        last_sample: bool = False,
        compressor_nearest: bool = False,
        previous_detection=None,
    ) -> DebugCaptureDecision:
        if level is DebugTraceLevel.NONE:
            return DebugCaptureDecision(False)

        reasons: set[DebugCaptureReason] = set()
        if first_sample:
            reasons.add(DebugCaptureReason.FIRST_SAMPLE)
        if last_sample:
            reasons.add(DebugCaptureReason.LAST_SAMPLE)
        if compressor_nearest:
            reasons.add(DebugCaptureReason.COMPRESSOR_NEAREST)
        if not is_valid:
            reasons.add(DebugCaptureReason.INVALID)
        if detection.overall_confidence < minimum_confidence or "LOW_CONFIDENCE" in detection.flags:
            reasons.add(DebugCaptureReason.LOW_CONFIDENCE)
        if detection.fill_state is FillState.UNKNOWN_REVIEW:
            reasons.add(DebugCaptureReason.UNKNOWN_REVIEW)
        if "DETECTION_LOST" in detection.flags:
            reasons.add(DebugCaptureReason.DETECTION_LOST)
        if any("GLARE" in flag or "FOG" in flag for flag in detection.flags):
            reasons.add(DebugCaptureReason.GLARE_OR_FOG)
        if (
            detection.foam_front_y is not None
            or detection.fill_state in {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE}
            or any("FOAM" in flag for flag in detection.flags)
        ):
            reasons.add(DebugCaptureReason.FOAM)

        if previous_detection is not None:
            if _jumped(
                detection.raw_oil_air_level_y,
                previous_detection.raw_oil_air_level_y,
                effective_height,
                self.config.oil_position_jump_ratio,
            ):
                reasons.add(DebugCaptureReason.OIL_POSITION_JUMP)
            if _jumped(
                detection.raw_foam_front_y,
                previous_detection.raw_foam_front_y,
                effective_height,
                self.config.foam_position_jump_ratio,
            ):
                reasons.add(DebugCaptureReason.FOAM_POSITION_JUMP)
            if detection.fill_state is not previous_detection.fill_state:
                reasons.add(DebugCaptureReason.STATE_TRANSITION)

        oil_candidates = [
            candidate
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.OIL_AIR and not candidate.rejected
        ]
        oil_candidates.sort(key=lambda candidate: candidate.final_score, reverse=True)
        selected = [candidate for candidate in oil_candidates if candidate.selected]
        if len(oil_candidates) >= 2 and oil_candidates[0].final_score - oil_candidates[1].final_score <= self.config.candidate_ambiguity_score_gap:
            reasons.add(DebugCaptureReason.CANDIDATE_AMBIGUITY)
        if not selected:
            reasons.add(DebugCaptureReason.NO_SELECTED_CANDIDATE)
            oil_all = [candidate for candidate in detection.candidates if candidate.kind is BoundaryKind.OIL_AIR]
            if oil_all and all(candidate.rejected for candidate in oil_all):
                reasons.add(DebugCaptureReason.REJECTED_ONLY)

        if level is DebugTraceLevel.FULL:
            reasons.add(DebugCaptureReason.FULL_TRACE)
            return DebugCaptureDecision(True, _ordered(reasons))
        return DebugCaptureDecision(bool(reasons), _ordered(reasons))


def _jumped(current, previous, height: float, ratio: float) -> bool:
    if current is None or previous is None or height <= 0:
        return False
    return abs(float(current) - float(previous)) / float(height) >= ratio


def _ordered(reasons: set[DebugCaptureReason]) -> tuple[DebugCaptureReason, ...]:
    order = {reason: index for index, reason in enumerate(DebugCaptureReason)}
    return tuple(sorted(reasons, key=lambda reason: order[reason]))
