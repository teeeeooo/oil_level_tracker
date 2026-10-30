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


class LineKind(StrEnum):
    """Only Oil feeds the judgment; Foam and reference lines are only shown (Product SSOT §4)."""

    OIL = "OIL"
    FOAM = "FOAM"
    REFERENCE = "REFERENCE"


class Verdict(StrEnum):
    """A Glass's judgment (Product SSOT §5)."""

    PASS = "PASS"      # 합격
    FAIL = "FAIL"      # 불합격
    REVIEW = "REVIEW"  # 검토 필요: too few valid samples, or no compressor start for RECOVERY


class LevelState(StrEnum):
    """Where an Oil sample at the Glass top or bottom puts the level (Product SSOT §4)."""

    FULL = "FULL_NO_INTERFACE"
    EMPTY = "EMPTY_NO_INTERFACE"
