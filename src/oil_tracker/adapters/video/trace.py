"""The point line: the draft's path pinned through the user's points (Product SSOT §6).

Implements application.ports.EdgeTracer. A Glass's edge strength is computed once from its cached
context pieces and kept for the next clicks, so a click costs only the path between two points.

Between two points the path keeps within REACH rows of the straight line joining them (user,
2026-10-30): free to follow the strongest edges, it ran to the image's top or bottom, where the
strongest steps usually are.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from collections.abc import Callable, Sequence
from itertools import pairwise

import cv2
import numpy as np

from .draft import EDGE_FULL, normalised_strength, strongest_path

KEEP = 2  # Glasses whose edge strength stays in memory (SPL#1: 24 MB each)
REACH = 8  # rows each side of the straight line: the snap's reach (user, 2026-10-29)
NO_EDGE = 6 / EDGE_FULL  # a weaker luma step is no edge, as for the snap (web/lines.js SNAP_MIN_STEP)


def decode_piece(png: bytes) -> np.ndarray:
    """A cached context piece as RGB, the order the draft read it in."""
    image = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("A context piece cannot be decoded.")
    return image[:, :, ::-1]


class ContextEdgeTracer:
    def __init__(self, keep: int = KEEP) -> None:
        self._keep = keep
        self._strengths: OrderedDict[str, np.ndarray] = OrderedDict()
        self._lock = threading.Lock()

    def trace(
        self, key: str, piece: Callable[[int], bytes], pieces: int, points: Sequence[tuple[int, int]]
    ) -> tuple[int, ...]:
        strength = self._strength(key, piece, pieces)
        rows = [points[0][1]]
        for (first, start), (last, end) in pairwise(points):
            rows.extend(corridor_path(strength, first, start, last, end)[1:].tolist())
        return tuple(rows)

    def _strength(self, key: str, piece: Callable[[int], bytes], pieces: int) -> np.ndarray:
        with self._lock:
            found = self._strengths.get(key)
            if found is None:
                rgb = np.concatenate([decode_piece(piece(index)) for index in range(pieces)], axis=1)
                found = normalised_strength(rgb)
                self._strengths[key] = found
                while len(self._strengths) > self._keep:
                    self._strengths.popitem(last=False)
            self._strengths.move_to_end(key)
            return found


def corridor_path(strength: np.ndarray, first: int, start: int, last: int, end: int) -> np.ndarray:
    """The rows from (first, start) to (last, end) along the strongest edges within REACH rows of the
    straight line between them; straight where that band holds no edge.

    The band is cut out with the straight line as its middle row, so following the line costs no
    jumps and a path without edges stays on it.
    """
    columns = np.arange(first, last + 1)
    line = np.rint(start + (end - start) * (columns - first) / max(1, last - first)).astype(np.int64)
    rows = line[None, :] + np.arange(-REACH, REACH + 1)[:, None]
    inside = (rows >= 0) & (rows < strength.shape[0])
    band = strength[np.clip(rows, 0, strength.shape[0] - 1), columns[None, :]]
    band = np.where(inside, np.where(band >= NO_EDGE, band, 0.0), -np.inf)
    offsets = strongest_path(band, REACH, REACH, scale=strength.shape[0])
    return line + offsets - REACH
