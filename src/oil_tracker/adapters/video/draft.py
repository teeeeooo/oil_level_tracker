"""The Oil draft: one path along the strongest vertical edges (Product SSOT §4).

Method B of docs/50-diagnostics/2026-10-29-draft-method-comparison.md, with the parameters the
user judged on SPL#4 and SPL#1; the weak stretches are left empty for the user to draw.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from oil_tracker.domain.enums import SampleOrigin
from oil_tracker.domain.line import Line

EDGE_FULL = 24.0     # luma step that counts as a full-strength edge
JUMP_WEIGHT = 5.0    # cost of a jump of the whole Glass height
MAX_JUMP = 0.25      # of the Glass height per column
WEAK = 0.25          # mean strength below which a stretch is left empty
WEAK_WINDOW = 10     # columns (5 s at 2 per second)
WEAK_MIN_RUN = 4     # columns (2 s); shorter weak runs keep their line


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


def oil_draft(rgb: np.ndarray) -> OilDraft:
    s = np.minimum(edge_strength(rgb) / EDGE_FULL, 1.0)
    rows = strongest_path(s)
    return OilDraft(rows, weak_stretches(s[rows, np.arange(len(rows))]))


def strongest_path(s: np.ndarray) -> np.ndarray:
    """The row per column that maximises the summed strength minus the jump cost."""
    height, columns = s.shape
    jump = max(1, int(MAX_JUMP * height))
    penalty = JUMP_WEIGHT * np.abs(np.arange(-jump, jump + 1)) / height
    rows = np.arange(height)
    score = s[:, 0].astype(np.float64)
    back = np.zeros((height, columns), dtype=np.int32)
    for t in range(1, columns):
        total = sliding_window_view(np.pad(score, jump, constant_values=-np.inf), 2 * jump + 1) - penalty
        best = total.argmax(axis=1)
        back[:, t] = rows + best - jump
        score = total[rows, best] + s[:, t]
    path = np.zeros(columns, dtype=np.int32)
    path[-1] = int(score.argmax())
    for t in range(columns - 1, 0, -1):
        path[t - 1] = back[path[t], t]
    return path


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
