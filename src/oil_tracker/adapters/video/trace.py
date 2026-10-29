"""The point line: the draft's path pinned through the user's points (Product SSOT §6).

Implements application.ports.EdgeTracer. A Glass's edge strength is computed once from its cached
context pieces and kept for the next clicks, so a click costs only the path between two points.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from collections.abc import Callable, Sequence
from itertools import pairwise

import cv2
import numpy as np

from .draft import normalised_strength, strongest_path

KEEP = 2  # Glasses whose edge strength stays in memory (SPL#1: 24 MB each)


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
            rows.extend(strongest_path(strength[:, first:last + 1], start, end)[1:].tolist())
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
