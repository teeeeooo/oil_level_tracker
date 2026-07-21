from __future__ import annotations

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .foam_front_detector import FoamDecisionStatus


def classify_fill_state(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    oil_candidate: BoundaryCandidate | None,
    foam_candidate: BoundaryCandidate | None,
    previous_state: FillState | None,
    settings: DetectorSettings,
    foam_status: FoamDecisionStatus = FoamDecisionStatus.NO_EVIDENCE,
) -> tuple[FillState, float, list[str]]:
    flags: list[str] = []
    valid = effective_mask > 0
    if valid.sum() == 0:
        return FillState.UNKNOWN_REVIEW, 0.0, ["EMPTY_EFFECTIVE_MASK"]
    glare_ratio = float(((glare_mask > 0) & valid).sum()) / int(valid.sum())
    visibility = max(0.0, 1.0 - glare_ratio)
    if glare_ratio >= settings.glare_ratio_unknown:
        return FillState.UNKNOWN_REVIEW, visibility, ["FOGGED_OR_GLARE"]

    pending_or_ambiguous = foam_status in {
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }
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
        elif pending_or_ambiguous:
            flags.append(
                "FOAM_PERSISTENCE_PENDING"
                if foam_status is FoamDecisionStatus.PERSISTENCE_PENDING
                else "FOAM_EVIDENCE_AMBIGUOUS"
            )
        return state, visibility, flags

    if foam_candidate is not None:
        return FillState.FULL_WITH_FOAM, visibility, flags
    if pending_or_ambiguous:
        flags.append(
            "FOAM_PERSISTENCE_PENDING"
            if foam_status is FoamDecisionStatus.PERSISTENCE_PENDING
            else "FOAM_EVIDENCE_AMBIGUOUS"
        )
        flags.append("REVIEW_REQUIRED")
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags

    mean_intensity = float(gray[valid].mean())
    texture = float(gray[valid].std())
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
