from __future__ import annotations

from enum import StrEnum


class JudgmentMode(StrEnum):
    RECOVERY = "RECOVERY"
    HOLD_BELOW_ZERO = "HOLD_BELOW_ZERO"
    HOLD_ABOVE_ZERO = "HOLD_ABOVE_ZERO"


class InspectionState(StrEnum):
    NOT_ANALYSED = "NOT_ANALYSED"  # 분석 안 됨: new, cancelled or interrupted
    ANALYSED = "ANALYSED"          # 분석 완료
    FAILED = "FAILED"              # 분석 실패, with a reason


class SampleOrigin(StrEnum):
    """Where a line sample came from (architecture.md: lines)."""

    DRAFT = "DRAFT"
    EDITED = "EDITED"
    DRAWN = "DRAWN"
