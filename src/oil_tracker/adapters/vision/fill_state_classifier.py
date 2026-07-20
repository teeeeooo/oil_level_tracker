from __future__ import annotations

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings


def classify_fill_state(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    oil_candidate: BoundaryCandidate | None,
    foam_candidate: BoundaryCandidate | None,
    previous_state: FillState | None,
    settings: DetectorSettings,
) -> tuple[FillState, float, list[str]]:
    flags: list[str] = []
    valid = effective_mask > 0
    if valid.sum() == 0:
        return FillState.UNKNOWN_REVIEW, 0.0, ["EMPTY_EFFECTIVE_MASK"]
    glare_ratio = float(((glare_mask > 0) & valid).sum()) / int(valid.sum())
    visibility = max(0.0, 1.0 - glare_ratio)
    if glare_ratio >= settings.glare_ratio_unknown:
        return FillState.UNKNOWN_REVIEW, visibility, ["FOGGED_OR_GLARE"]

    if oil_candidate is not None:
        y = oil_candidate.y
        valid_rows = np.where(valid.any(axis=1))[0]
        top, bottom = int(valid_rows.min()), int(valid_rows.max())
        rel = (y - top) / max(1.0, bottom - top)
        if previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM} or rel < 0.18:
            state = FillState.DRAINING_VISIBLE
        elif previous_state == FillState.EMPTY_NO_INTERFACE or rel > 0.82:
            state = FillState.FILLING_VISIBLE
        else:
            state = FillState.PARTIAL_VISIBLE
        if foam_candidate is not None:
            state = FillState.FOAMING_VISIBLE
        return state, visibility, flags

    mean_intensity = float(gray[valid].mean())
    texture = float(gray[valid].std())
    if foam_candidate is not None:
        return FillState.FULL_WITH_FOAM, visibility, flags
    if previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM} and mean_intensity < 170:
        return FillState.FULL_NO_INTERFACE, visibility, flags
    if previous_state == FillState.EMPTY_NO_INTERFACE and mean_intensity > 85:
        return FillState.EMPTY_NO_INTERFACE, visibility, flags
    if mean_intensity <= 120 and texture < 40:
        return FillState.FULL_NO_INTERFACE, visibility, flags
    if mean_intensity >= 150 and texture < 50:
        return FillState.EMPTY_NO_INTERFACE, visibility, flags
    flags.append("NO_CONFIDENT_INTERFACE")
    return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags
