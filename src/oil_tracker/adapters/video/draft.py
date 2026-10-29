"""The Oil draft: one path along the strongest vertical edges (Product SSOT §4).

Method B of docs/50-diagnostics/2026-10-29-draft-method-comparison.md, with the parameters the
user judged on SPL#4 and SPL#1; the weak stretches are left empty for the user to draw.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from oil_tracker.domain.enums import SampleOrigin
from oil_tracker.domain.line import Line

EDGE_FULL = 24.0     # luma step that counts as a full-strength edge
JUMP_WEIGHT = 5.0    # cost of a jump of the whole Glass height
MAX_JUMP = 0.25      # of the Glass height per column
WEAK = 0.25          # mean strength below which a stretch is left empty
WEAK_WINDOW = 10     # columns (5 s at 2 per second)
WEAK_MIN_RUN = 4     # columns (2 s); shorter weak runs keep their line
TIE = 1e-9           # scores closer than this are equal paths


@dataclass(frozen=True)
class OilDraft:
    rows: np.ndarray   # one context row per column
    empty: np.ndarray  # True where the edge is weak: no draft line there


def draft_line(draft: OilDraft, y0: int) -> Line:
    """The draft as domain samples: source-frame y, or None where it is left empty."""
    ys = tuple(None if empty else float(y0 + row) for row, empty in zip(draft.rows.tolist(), draft.empty.tolist()))
    return Line(ys, (SampleOrigin.DRAFT,) * len(ys))


def edge_strength(rgb: np.ndarray) -> np.ndarray:
    """|L[y+1] - L[y-1]| of the luma, blurred over 5 columns."""
    luma = rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    strength = np.zeros_like(luma)
    strength[1:-1] = np.abs(luma[2:] - luma[:-2])
    return cv2.GaussianBlur(strength, (5, 1), 0)


def normalised_strength(rgb: np.ndarray) -> np.ndarray:
    """Edge strength from 0 to 1, as the draft path weighs it."""
    return np.minimum(edge_strength(rgb) / EDGE_FULL, 1.0)


def oil_draft(rgb: np.ndarray) -> OilDraft:
    s = normalised_strength(rgb)
    rows = strongest_path(s)
    return OilDraft(rows, weak_stretches(s[rows, np.arange(len(rows))]))


def strongest_path(s: np.ndarray, start: int | None = None, end: int | None = None) -> np.ndarray:
    """The row per column that maximises the summed strength minus the jump cost.

    `start` and `end` pin the first and last rows (the point line, Product SSOT §6). Pinned rows
    too far apart for the jump limit are joined by a straight line.

    The jump cost grows linearly, so each column's best score is a windowed maximum, taken in a
    few NumPy calls per column (_WindowMax); the path is traced back through the stored scores.
    """
    height, columns = s.shape
    jump = max(1, int(MAX_JUMP * height))
    penalty = JUMP_WEIGHT * np.abs(np.arange(-jump, jump + 1)) / height
    rise = JUMP_WEIGHT * np.arange(height) / height
    window = _WindowMax(height, jump)
    scores = np.empty((columns, height))
    score = s[:, 0].astype(np.float64)
    if start is not None:
        score = np.where(np.arange(height) == start, score, -np.inf)
    scores[0] = score
    for t in range(1, columns):
        score = np.maximum(window.up_to(score + rise) - rise, window.from_(score - rise) + rise) + s[:, t]
        scores[t] = score
    if end is not None and not np.isfinite(score[end]):
        return np.rint(np.linspace(start, end, columns)).astype(np.int32)
    path = np.zeros(columns, dtype=np.int32)
    path[-1] = _first_best(score) if end is None else end
    padded = np.full(height + 2 * jump, -np.inf)
    for t in range(columns - 1, 0, -1):
        padded[jump:jump + height] = scores[t - 1]
        row = int(path[t])
        path[t - 1] = row + _first_best(padded[row:row + 2 * jump + 1] - penalty) - jump
    return path


def _first_best(values: np.ndarray) -> int:
    """The first of the best, as a search over every pair of rows picks it. The windowed maxima
    round differently, so values within TIE of the best count as equal."""
    return int(np.argmax(values >= values.max() - TIE))


class _WindowMax:
    """Maxima of a column over the rows [r - jump, r] or [r, r + jump], from running maxima within
    blocks of jump + 1 rows (van Herk): a window spans at most two blocks."""

    def __init__(self, height: int, jump: int) -> None:
        self.block = jump + 1
        self.jump = jump
        self.height = height
        blocks = -(-height // self.block) + 1  # one block of -inf in front of the first row
        self.padded = np.full(blocks * self.block, -np.inf)
        self.rows = np.arange(self.block, self.block + height)

    def up_to(self, values: np.ndarray) -> np.ndarray:
        self.padded[self.block:self.block + self.height] = values
        blocks = self.padded.reshape(-1, self.block)
        ahead = np.maximum.accumulate(blocks, axis=1).ravel()
        behind = np.maximum.accumulate(blocks[:, ::-1], axis=1)[:, ::-1].ravel()
        return np.maximum(behind[self.rows - self.jump], ahead[self.rows])

    def from_(self, values: np.ndarray) -> np.ndarray:
        return self.up_to(values[::-1])[::-1]


def weak_stretches(strength: np.ndarray) -> np.ndarray:
    kernel = np.ones(WEAK_WINDOW)
    mean = np.convolve(strength, kernel, mode="same") / np.convolve(np.ones_like(strength), kernel, mode="same")
    weak = mean < WEAK
    start = None
    for t in range(len(weak) + 1):
        inside = t < len(weak) and weak[t]
        if inside and start is None:
            start = t
        elif not inside and start is not None:
            if t - start < WEAK_MIN_RUN:
                weak[start:t] = False
            start = None
    return weak
