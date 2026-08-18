from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MaskedBandIntensityProfiles:
    """Vectorized above/below intensity evidence for every candidate row."""

    above: np.ndarray
    below: np.ndarray
    signed_difference: np.ndarray
    available: np.ndarray


def _bool_mask(mask: np.ndarray) -> np.ndarray:
    return mask if mask.dtype == np.bool_ else mask > 0


def masked_row_mean(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    valid = _bool_mask(mask)
    counts = valid.sum(axis=1).astype(np.float32)
    sums = (image.astype(np.float32, copy=False) * valid).sum(axis=1)
    return np.divide(
        sums,
        counts,
        out=np.zeros_like(sums, dtype=np.float32),
        where=counts > 0,
    )


def row_coverage(binary: np.ndarray, mask: np.ndarray) -> np.ndarray:
    valid = _bool_mask(mask)
    counts = valid.sum(axis=1).astype(np.float32)
    hits = ((binary > 0) & valid).sum(axis=1).astype(np.float32)
    return np.divide(hits, counts, out=np.zeros_like(hits), where=counts > 0)


def masked_band_intensity_profiles(
    image: np.ndarray,
    valid_mask: np.ndarray,
    band: int,
    *,
    reference_mask: np.ndarray | None = None,
    minimum_fraction: float = 0.0,
    minimum_pixels: int = 5,
    include_center_extra: bool = False,
) -> MaskedBandIntensityProfiles:
    """Return masked band means in O(frame-height) without per-candidate masks.

    Glare/exclusion robustness is supplied by ``valid_mask``. ``reference_mask``
    keeps unavailable distinct from zero evidence by requiring a bounded fraction
    of the effective pixels to remain visible. Inputs are never mutated.
    """

    valid = _bool_mask(valid_mask)
    reference = valid if reference_mask is None else _bool_mask(reference_mask)
    height = int(image.shape[0])
    width = max(1, int(band))

    row_counts = valid.sum(axis=1).astype(np.int64)
    reference_counts = reference.sum(axis=1).astype(np.int64)
    row_sums = (image.astype(np.float64, copy=False) * valid).sum(axis=1)

    sum_prefix = np.concatenate((np.zeros(1, dtype=np.float64), np.cumsum(row_sums)))
    count_prefix = np.concatenate((np.zeros(1, dtype=np.int64), np.cumsum(row_counts)))
    reference_prefix = np.concatenate(
        (np.zeros(1, dtype=np.int64), np.cumsum(reference_counts))
    )

    rows = np.arange(height, dtype=np.int64)
    above_start = np.maximum(0, rows - width)
    above_end = rows
    below_start = rows
    below_end = np.minimum(height, rows + width + int(include_center_extra))

    above_sums = sum_prefix[above_end] - sum_prefix[above_start]
    below_sums = sum_prefix[below_end] - sum_prefix[below_start]
    above_counts = count_prefix[above_end] - count_prefix[above_start]
    below_counts = count_prefix[below_end] - count_prefix[below_start]
    above_reference = reference_prefix[above_end] - reference_prefix[above_start]
    below_reference = reference_prefix[below_end] - reference_prefix[below_start]

    minimum = max(1, int(minimum_pixels))
    fraction = max(0.0, min(1.0, float(minimum_fraction)))
    above_required = np.maximum(minimum, np.floor(above_reference * fraction).astype(np.int64))
    below_required = np.maximum(minimum, np.floor(below_reference * fraction).astype(np.int64))
    available = (above_counts >= above_required) & (below_counts >= below_required)

    above = np.divide(
        above_sums,
        above_counts,
        out=np.zeros(height, dtype=np.float64),
        where=above_counts > 0,
    )
    below = np.divide(
        below_sums,
        below_counts,
        out=np.zeros(height, dtype=np.float64),
        where=below_counts > 0,
    )
    above[~available] = 0.0
    below[~available] = 0.0
    signed = above - below
    signed[~available] = 0.0
    return MaskedBandIntensityProfiles(
        above=above.astype(np.float32),
        below=below.astype(np.float32),
        signed_difference=signed.astype(np.float32),
        available=available,
    )


def binary_band_overlap_profile(
    binary: np.ndarray,
    denominator_mask: np.ndarray,
    band: int,
) -> np.ndarray:
    """Vectorized row-band overlap ratio for every row."""

    denominator = _bool_mask(denominator_mask)
    hits = ((binary > 0) & denominator).sum(axis=1).astype(np.int64)
    counts = denominator.sum(axis=1).astype(np.int64)
    hit_prefix = np.concatenate((np.zeros(1, dtype=np.int64), np.cumsum(hits)))
    count_prefix = np.concatenate((np.zeros(1, dtype=np.int64), np.cumsum(counts)))
    height = int(binary.shape[0])
    rows = np.arange(height, dtype=np.int64)
    width = max(0, int(band))
    starts = np.maximum(0, rows - width)
    ends = np.minimum(height, rows + width + 1)
    window_hits = hit_prefix[ends] - hit_prefix[starts]
    window_counts = count_prefix[ends] - count_prefix[starts]
    return np.divide(
        window_hits,
        window_counts,
        out=np.zeros(height, dtype=np.float32),
        where=window_counts > 0,
    ).astype(np.float32)
