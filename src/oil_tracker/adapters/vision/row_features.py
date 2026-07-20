from __future__ import annotations

import numpy as np


def masked_row_mean(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    valid = mask > 0
    counts = valid.sum(axis=1).astype(np.float32)
    sums = (image.astype(np.float32) * valid).sum(axis=1)
    return np.divide(sums, counts, out=np.zeros_like(sums, dtype=np.float32), where=counts > 0)


def row_coverage(binary: np.ndarray, mask: np.ndarray) -> np.ndarray:
    valid = mask > 0
    counts = valid.sum(axis=1).astype(np.float32)
    hits = ((binary > 0) & valid).sum(axis=1).astype(np.float32)
    return np.divide(hits, counts, out=np.zeros_like(hits), where=counts > 0)


def local_maxima(profile: np.ndarray, top_k: int, minimum: float = 0.0, separation: int = 4) -> list[int]:
    if profile.size < 3:
        return []
    candidates = [i for i in range(1, len(profile) - 1) if profile[i] >= profile[i - 1] and profile[i] >= profile[i + 1] and profile[i] >= minimum]
    candidates.sort(key=lambda i: float(profile[i]), reverse=True)
    selected: list[int] = []
    for idx in candidates:
        if all(abs(idx - prior) >= separation for prior in selected):
            selected.append(idx)
        if len(selected) >= top_k:
            break
    return selected
