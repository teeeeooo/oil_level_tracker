from __future__ import annotations

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .foam_front_detector import FoamDecisionStatus
from .oil_shadow_types import ShadowNoInterfaceEvidence, ShadowTemporalStatus


def classify_fill_state(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    oil_candidate: BoundaryCandidate | None,
    foam_candidate: BoundaryCandidate | None,
    previous_state: FillState | None,
    settings: DetectorSettings,
    foam_status: FoamDecisionStatus = FoamDecisionStatus.NO_EVIDENCE,
    oil_status: ShadowTemporalStatus | None = None,
    oil_no_interface: ShadowNoInterfaceEvidence | None = None,
) -> tuple[FillState, float, list[str]]:
    flags: list[str] = []
    valid = effective_mask > 0
    if valid.sum() == 0:
        return FillState.UNKNOWN_REVIEW, 0.0, [
            "EMPTY_EFFECTIVE_MASK",
            "REVIEW_REQUIRED",
        ]
    glare_ratio = float(((glare_mask > 0) & valid).sum()) / int(valid.sum())
    visibility = max(0.0, 1.0 - glare_ratio)
    if glare_ratio >= settings.glare_ratio_unknown:
        return FillState.UNKNOWN_REVIEW, visibility, [
            "FOGGED_OR_GLARE",
            "REVIEW_REQUIRED",
        ]

    foam_pending_or_ambiguous = foam_status in {
        FoamDecisionStatus.PERSISTENCE_PENDING,
        FoamDecisionStatus.AMBIGUOUS,
        FoamDecisionStatus.MODERATE_EVIDENCE,
    }

    if oil_candidate is not None:
        valid_rows = np.where(valid.any(axis=1))[0]
        top, bottom = int(valid_rows.min()), int(valid_rows.max())
        local_y = float(oil_candidate.features.get("local_y", oil_candidate.y))
        relative_y = (local_y - top) / max(1.0, bottom - top)
        if (
            previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}
            or relative_y < 0.18
        ):
            state = FillState.DRAINING_VISIBLE
        elif previous_state is FillState.EMPTY_NO_INTERFACE or relative_y > 0.82:
            state = FillState.FILLING_VISIBLE
        else:
            state = FillState.PARTIAL_VISIBLE
        if foam_candidate is not None:
            state = FillState.FOAMING_VISIBLE
        elif foam_pending_or_ambiguous:
            flags.append(_foam_review_flag(foam_status))
        return state, visibility, flags

    if foam_candidate is not None:
        # S5-A accepted Foam remains authoritative even without an oil boundary.
        return FillState.FULL_WITH_FOAM, visibility, flags

    if oil_status is not ShadowTemporalStatus.NO_INTERFACE_ACCEPTED:
        flags.extend(_oil_review_flags(oil_status))
        if foam_pending_or_ambiguous:
            flags.append(_foam_review_flag(foam_status))
        flags.append("REVIEW_REQUIRED")
        return (
            FillState.UNKNOWN_REVIEW,
            min(visibility, 0.45),
            list(dict.fromkeys(flags)),
        )

    if foam_pending_or_ambiguous:
        flags.extend((_foam_review_flag(foam_status), "REVIEW_REQUIRED"))
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags

    if oil_no_interface is None or not oil_no_interface.available:
        return FillState.UNKNOWN_REVIEW, min(visibility, 0.35), [
            "NO_INTERFACE_EVIDENCE_UNAVAILABLE",
            "REVIEW_REQUIRED",
        ]

    visibility = min(visibility, float(oil_no_interface.visibility))
    full_evidence = float(oil_no_interface.full_likelihood)
    empty_evidence = float(oil_no_interface.empty_likelihood)
    if previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
        full_evidence = min(1.0, full_evidence + 0.12)
    elif previous_state is FillState.EMPTY_NO_INTERFACE:
        empty_evidence = min(1.0, empty_evidence + 0.12)

    if full_evidence >= 0.45 and full_evidence - empty_evidence >= 0.12:
        return FillState.FULL_NO_INTERFACE, visibility, flags
    if empty_evidence >= 0.45 and empty_evidence - full_evidence >= 0.12:
        return FillState.EMPTY_NO_INTERFACE, visibility, flags
    flags.extend(("NO_INTERFACE_STATE_AMBIGUOUS", "REVIEW_REQUIRED"))
    return FillState.UNKNOWN_REVIEW, min(visibility, 0.45), flags


def _foam_review_flag(status: FoamDecisionStatus) -> str:
    if status is FoamDecisionStatus.PERSISTENCE_PENDING:
        return "FOAM_PERSISTENCE_PENDING"
    return "FOAM_EVIDENCE_AMBIGUOUS"


def _oil_review_flags(status: ShadowTemporalStatus | None) -> list[str]:
    if status is ShadowTemporalStatus.REACQUISITION_PENDING:
        return ["OIL_REACQUISITION_PENDING"]
    if status is ShadowTemporalStatus.UNAVAILABLE:
        return ["OIL_PIPELINE_UNAVAILABLE"]
    if status is ShadowTemporalStatus.AMBIGUOUS:
        return ["OIL_EVIDENCE_AMBIGUOUS"]
    if status is ShadowTemporalStatus.BOUNDARY_ACCEPTED:
        return ["OIL_BOUNDARY_PROJECTION_MISSING"]
    return ["OIL_TYPED_DECISION_UNAVAILABLE"]
