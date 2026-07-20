from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from oil_tracker.domain.enums import FillState


class DetectionQuality(str, Enum):
    NORMAL = "normal"
    REVIEW = "review"
    FAILURE = "failure"


@dataclass(frozen=True)
class DetectionQualityAssessment:
    quality: DetectionQuality
    reason: str


_VISIBLE_BOUNDARY_STATES = {
    FillState.FILLING_VISIBLE,
    FillState.PARTIAL_VISIBLE,
    FillState.DRAINING_VISIBLE,
}

_FAILURE_FLAGS = {"DETECTION_LOST"}
_REVIEW_FLAGS = {
    "LOW_CONFIDENCE",
    "UNKNOWN_REVIEW",
    "FOGGED_OR_GLARE",
    "REVIEW_REQUIRED",
}


def assess_detection_quality(detection, minimum_confidence: float) -> DetectionQualityAssessment:
    """Classify a final detector result without depending on any UI module."""

    if detection is None:
        return DetectionQualityAssessment(DetectionQuality.FAILURE, "검출 결과가 없습니다")

    flags = {str(flag).upper() for flag in detection.flags}
    if flags & _FAILURE_FLAGS:
        return DetectionQualityAssessment(DetectionQuality.FAILURE, "유면 검출이 끊겼습니다")
    if detection.fill_state in _VISIBLE_BOUNDARY_STATES and detection.oil_air_level_y is None:
        return DetectionQualityAssessment(DetectionQuality.FAILURE, "보이는 유면 경계를 찾지 못했습니다")

    confidence = float(detection.overall_confidence)
    if not math.isfinite(confidence):
        return DetectionQualityAssessment(DetectionQuality.FAILURE, "검출 신뢰도 값이 올바르지 않습니다")

    if "FOGGED_OR_GLARE" in flags or any("GLARE" in flag or "FOG" in flag for flag in flags):
        return DetectionQualityAssessment(DetectionQuality.REVIEW, "반사광 또는 흐림 가능성을 확인해 주세요")
    if detection.fill_state in {FillState.FULL_WITH_FOAM, FillState.FOAMING_VISIBLE} or any("FOAM" in flag for flag in flags):
        return DetectionQualityAssessment(DetectionQuality.REVIEW, "거품 영향 가능성을 확인해 주세요")
    if detection.fill_state == FillState.UNKNOWN_REVIEW or flags & _REVIEW_FLAGS:
        return DetectionQualityAssessment(DetectionQuality.REVIEW, "사용자 확인이 필요한 장면입니다")
    if confidence < float(minimum_confidence):
        return DetectionQualityAssessment(DetectionQuality.REVIEW, "검출 신뢰도가 최소 기준보다 낮습니다")

    if detection.oil_air_level_y is None:
        return DetectionQualityAssessment(DetectionQuality.NORMAL, "관찰 범위 밖 상태를 정상적으로 판별했습니다")
    return DetectionQualityAssessment(DetectionQuality.NORMAL, "정상적으로 검출되었습니다")
