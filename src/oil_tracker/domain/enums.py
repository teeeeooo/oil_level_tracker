from __future__ import annotations

from enum import StrEnum


class JudgmentMode(StrEnum):
    RECOVERY = "RECOVERY"
    HOLD_BELOW_ZERO = "HOLD_BELOW_ZERO"
    HOLD_ABOVE_ZERO = "HOLD_ABOVE_ZERO"
