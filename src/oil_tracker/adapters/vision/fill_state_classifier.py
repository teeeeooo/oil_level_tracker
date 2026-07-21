from __future__ import annotations

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .foam_front_detector import FoamDecisionStatus
from .oil_temporal_path import OilDecisionStatus


def classify_fill_state(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    oil_candidate: BoundaryCandidate | None,
    foam_candidate: BoundaryCandidate | None,
    previous_state: FillState | None,
    settings: DetectorSettings,
    foam_status: FoamDecisionStatus = FoamDecisionStatus.NO_EVIDENCE,
    oil_status: OilDecisionStatus | None = None,
) -> tuple[FillState, float, list[str]]:
    flags: list[str] = []
    valid = effective_mask > 0
    if valid.sum() == 0:
        return FillState.UNKNOWN_REVIEW, 0.0, ["EMPTY_EFFECTIVE_MASK", "REVIEW_REQUIRED"]
    glare_ratio = float(((glare_mask > 0) & valid).sum()) / int(valid.sum())
    visibility = max(0.0, 1.0 - glare_ratio)
    if glare_ratio >= settings.glare_ratio_unknown:
        return FillState.UNKNOWN_REVIEW, visibility, ["FOGGED_OR_GLARE", "REVIEW_REQUIRED"]

    foam_pending_or_ambiguous = foam_status in {
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }
    oil_review = oil_status in {
        OilDecisionStatus.AMBIGUOUS,
        OilDecisionStatus.PATH_PENDING,
        OilDecisionStatus.REACQUISITION_PENDING,
        OilDecisionStatus.REJECTED_BOUNDARY,
        OilDecisionStatus.LOW_MARGIN,
        OilDecisionStatus.UNAVAILABLE,
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
        elif foam_pending_or_ambiguous:
            flags.append(
                "FOAM_PERSISTENCE_PENDING"
                if foam_status is FoamDecisionStatus.PERSISTENCE_PENDING
                else "FOAM_EVIDENCE_AMBIGUOUS"
            )
        return state, visibility, flags

    if foam_candidate is not None:
        # Accepted Foam remains authoritative even while the oil boundary is absent.
        return FillState.FULL_WITH_FOAM, visibility, flags
    if oil_review:
        flags.extend(_oil_review_flags(oil_status))
        if foam_pending_or_ambiguous:
            flags.append(
                "FOAM_PERSISTENCE_PENDING"
                if foam_status is FoamDecisionStatus.PERSISTENCE_PENDING
                else "FOAM_EVIDENCE_AMBIGUOUS"
            )
        flags.append("REVIEW_REQUIRED")
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), list(dict.fromkeys(flags))
    if foam_pending_or_ambiguous:
        flags.append(
            "FOAM_PERSISTENCE_PENDING"
            if foam_status is FoamDecisionStatus.PERSISTENCE_PENDING
            else "FOAM_EVIDENCE_AMBIGUOUS"
        )
        flags.append("REVIEW_REQUIRED")
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags

    # A selected no-interface hypothesis carries no numeric position. Full versus
    # empty still requires image evidence; previous/initial state is only a prior.
    visible = valid & ~(glare_mask > 0)
    if int(visible.sum()) < max(10, int(valid.sum() * 0.08)):
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.35), ["NO_INTERFACE_VISIBILITY_CONFLICT", "REVIEW_REQUIRED"]
    values = gray[visible].astype(np.float32)
    mean_intensity = float(np.median(values))
    texture = float(np.std(values))
    full_evidence = max(0.0, min(1.0, (145.0 - mean_intensity) / 45.0)) * max(0.0, min(1.0, (55.0 - texture) / 35.0))
    empty_evidence = max(0.0, min(1.0, (mean_intensity - 115.0) / 55.0)) * max(0.0, min(1.0, (58.0 - texture) / 38.0))
    if previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
        full_evidence = min(1.0, full_evidence + 0.12)
    elif previous_state == FillState.EMPTY_NO_INTERFACE:
        empty_evidence = min(1.0, empty_evidence + 0.12)

    if full_evidence >= 0.52 and full_evidence - empty_evidence >= 0.14:
        return FillState.FULL_NO_INTERFACE, visibility, flags
    if empty_evidence >= 0.52 and empty_evidence - full_evidence >= 0.14:
        return FillState.EMPTY_NO_INTERFACE, visibility, flags
    flags.extend(("NO_INTERFACE_STATE_AMBIGUOUS", "REVIEW_REQUIRED"))
    return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags


def _oil_review_flags(status: OilDecisionStatus | None) -> list[str]:
    if status is OilDecisionStatus.PATH_PENDING:
        return ["OIL_PATH_PENDING"]
    if status is OilDecisionStatus.REACQUISITION_PENDING:
        return ["OIL_REACQUISITION_PENDING"]
    if status is OilDecisionStatus.LOW_MARGIN:
        return ["OIL_PATH_LOW_MARGIN", "OIL_EVIDENCE_AMBIGUOUS"]
    if status is OilDecisionStatus.REJECTED_BOUNDARY:
        return ["OIL_BOUNDARY_REJECTED"]
    return ["OIL_EVIDENCE_AMBIGUOUS"]
