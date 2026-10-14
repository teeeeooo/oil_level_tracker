"""DTO-1: seed-free ordinal turnover; diagnostic only, no physical authority."""
from __future__ import annotations

import numpy as np

OFFSETS = ((-1, -1), (-1, 0), (-1, 1), (0, 1),
           (1, 1), (1, 0), (1, -1), (0, -1))


def ordinal(gray: np.ndarray) -> np.ndarray:
    """Eight ternary comparisons; exact ties remain distinct, no thresholds."""
    if (not isinstance(gray, np.ndarray) or gray.dtype != np.uint8 or
            gray.ndim != 2 or min(gray.shape) < 3 or gray.size > 2_000_000):
        raise ValueError("bounded 2-D uint8 gray with both dimensions >=3 required")
    h, w = gray.shape
    center = gray[1:-1, 1:-1].astype(np.int16)
    return np.stack([np.sign(gray[1+dy:h-1+dy, 1+dx:w-1+dx].astype(np.int16)
                              - center).astype(np.int8) for dy, dx in OFFSETS], axis=-1)


def measure(frames) -> dict[str, np.ndarray | int]:
    """Stream same-sized rasters; retain only prior ordinal and accumulated map."""
    previous = None
    total = None
    shape = None
    count = 0
    for gray in frames:
        code = ordinal(gray)
        if shape is not None and gray.shape != shape:
            raise ValueError("frame shapes differ")
        shape = gray.shape
        if total is None:
            total = np.zeros(code.shape[:2], dtype=np.float64)
        if previous is not None:
            total += np.mean(code != previous, axis=-1)
        previous = code
        count += 1
    if count < 2:
        raise ValueError("at least two frames required")
    turnover = np.full(shape, np.nan, dtype=np.float64)
    complexity = np.full(shape, np.nan, dtype=np.float64)
    turnover[1:-1, 1:-1] = total / (count - 1)
    complexity[1:-1, 1:-1] = np.mean(previous != np.roll(previous, 1, axis=-1), axis=-1)
    return {"turnover": turnover, "static_complexity": complexity, "frames": count}


def sample_side(field: np.ndarray, centers, radius: int = 3) -> dict:
    """No partial-patch rescue; exact original centers, no nearest-path lookup."""
    if radius != 3:
        raise ValueError("DTO-1 freezes original 7x7 sampling")
    h, w = field.shape
    values = []
    for x, y in centers:
        if any(type(v) is not int for v in (x, y)):
            raise ValueError("integer centers required")
        if x-radius < 0 or y-radius < 0 or x+radius >= w or y+radius >= h:
            continue
        patch = field[y-radius:y+radius+1, x-radius:x+radius+1]
        if np.isfinite(patch).all():
            values.append(float(patch.mean()))
    complete = bool(centers) and len(values) == len(centers)
    return {"requested": len(centers), "complete": len(values),
            "mean": float(np.mean(values)) if complete else None,
            "status": "AVAILABLE" if complete else "UNAVAILABLE"}


def paired_score(field: np.ndarray, upper, lower) -> dict:
    a, b = sample_side(field, upper), sample_side(field, lower)
    score = None if a["mean"] is None or b["mean"] is None else b["mean"]-a["mean"]
    return {"upper": a, "lower": b, "score": score}


def center_profile(field: np.ndarray, column: int) -> list[dict]:
    """All center rows, not a selected contour or a physical proposal."""
    if type(column) is not int or not 0 <= column < field.shape[1]:
        raise ValueError("center column outside raster")
    return [{"row": y, "score": paired_score(field, [[column, y-5]],
                                                [[column, y+5]])["score"]}
            for y in range(field.shape[0])]
