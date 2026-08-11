from __future__ import annotations

import numpy as np


UPPER_DARK_CAP_MAX_AREA_FRACTION = 0.12
LOWER_DARK_CAP_MAX_AREA_FRACTION = 0.055
UPPER_DARK_CAP_MAX_MEDIAN_FRACTION = 0.15
LOWER_DARK_CAP_MAX_MEDIAN_FRACTION = 0.20
DARK_CAP_MIN_PHASE_CONTRAST = 0.15
DARK_CAP_GAP_ROWS = 2


def dark_border_cap_conflict(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    *,
    local_y: float,
) -> bool:
    """Return whether a row is the dark terminal cap of the Glass raster.

    This is shared hard topology for ordinary and supplemental Oil proposals.
    A dark lower phase can be real Oil, so only an extreme terminal sliver is a
    hard conflict. Less terminal rows remain candidates and must be resolved by
    representation, trajectory and competing-interface evidence.
    """

    if gray.ndim != 2:
        raise ValueError("Oil phase topology requires two-dimensional grayscale.")
    if effective_mask.shape != gray.shape or glare_mask.shape != gray.shape:
        raise ValueError("Oil phase topology rasters must share one shape.")
    visible = (effective_mask > 0) & ~(glare_mask > 0)
    available = int(np.count_nonzero(visible))
    if available == 0:
        return False

    center = min(gray.shape[0] - 1, max(0, int(round(float(local_y)))))
    upper_stop = max(0, center - DARK_CAP_GAP_ROWS)
    lower_start = min(gray.shape[0], center + DARK_CAP_GAP_ROWS + 1)
    upper = visible[:upper_stop]
    lower = visible[lower_start:]
    upper_count = int(np.count_nonzero(upper))
    lower_count = int(np.count_nonzero(lower))
    if upper_count < 10 or lower_count < 10:
        return False

    finite = np.asarray(gray, dtype=np.float32)
    maximum = float(np.max(finite)) if finite.size else 0.0
    gray_scale = 255.0 if maximum > 1.5 else 1.0
    upper_median = float(np.median(finite[:upper_stop][upper])) / gray_scale
    lower_median = float(np.median(finite[lower_start:][lower])) / gray_scale
    upper_cap = bool(
        upper_count / available <= UPPER_DARK_CAP_MAX_AREA_FRACTION
        and upper_median <= UPPER_DARK_CAP_MAX_MEDIAN_FRACTION
        and lower_median - upper_median >= DARK_CAP_MIN_PHASE_CONTRAST
    )
    lower_cap = bool(
        lower_count / available <= LOWER_DARK_CAP_MAX_AREA_FRACTION
        and lower_median <= LOWER_DARK_CAP_MAX_MEDIAN_FRACTION
        and upper_median - lower_median >= DARK_CAP_MIN_PHASE_CONTRAST
    )
    return upper_cap or lower_cap
