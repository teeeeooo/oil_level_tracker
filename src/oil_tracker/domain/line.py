"""Lines as dense samples at the analysis rate (architecture.md, "Lines are dense samples")."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .enums import SampleOrigin


@dataclass(frozen=True)
class Line:
    """One value per analysis sample: a source-frame y (down is larger), or None where empty.

    Source-frame y, not height above zero, so a corrected zero line moves no sample. An empty
    sample counts as invalid until it is drawn (Product SSOT §4).
    """

    ys: tuple[float | None, ...]
    origins: tuple[SampleOrigin, ...]

    def __post_init__(self) -> None:
        if len(self.ys) != len(self.origins):
            raise ValueError("A line needs one origin per sample.")
        if any(y is not None and not math.isfinite(y) for y in self.ys):
            raise ValueError("Line samples must be finite or empty.")

    @property
    def empty_count(self) -> int:
        return sum(y is None for y in self.ys)
