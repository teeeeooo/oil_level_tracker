from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .preprocessing import PreprocessResult
from .row_features import masked_row_mean


@dataclass(frozen=True)
class NoInterfaceEvidence:
    score: float
    boundary_score: float
    uniformity_score: float
    weak_boundary_score: float
    visibility_score: float
    glare_conflict: float
    prior_score: float
    mean_intensity: float | None
    texture: float | None
    reason: str
    available: bool


def evaluate_no_interface(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...],
    previous_state: FillState | None,
    settings: DetectorSettings,
) -> NoInterfaceEvidence:
    """Build an explicit no-interface hypothesis from image and boundary evidence."""

    valid = effective_mask > 0
    count = int(np.count_nonzero(valid))
    if count == 0:
        return NoInterfaceEvidence(
            score=0.0,
            boundary_score=0.0,
            uniformity_score=0.0,
            weak_boundary_score=0.0,
            visibility_score=0.0,
            glare_conflict=0.0,
            prior_score=0.0,
            mean_intensity=None,
            texture=None,
            reason="empty_effective_mask",
            available=False,
        )

    glare = (pre.glare_mask > 0) & valid
    glare_ratio = float(np.count_nonzero(glare)) / count
    visible = valid & ~glare
    visible_count = int(np.count_nonzero(visible))
    minimum_pixels = max(10, int(count * 0.08))
    if visible_count < minimum_pixels:
        return NoInterfaceEvidence(
            score=0.0,
            boundary_score=_best_boundary_score(candidates),
            uniformity_score=0.0,
            weak_boundary_score=0.0,
            visibility_score=max(0.0, 1.0 - glare_ratio),
            glare_conflict=min(1.0, glare_ratio),
            prior_score=_prior_score(previous_state),
            mean_intensity=None,
            texture=None,
            reason="insufficient_visible_pixels",
            available=False,
        )

    values = pre.gray[visible].astype(np.float32)
    mean_intensity = float(np.median(values))
    texture = float(np.std(values))
    uniformity = _unit(1.0 - texture / 58.0)

    row_profile = masked_row_mean(pre.sobel_y_abs, visible.astype(np.uint8) * 255)
    row_peak = float(row_profile.max()) if row_profile.size else 0.0
    row_weakness = _unit(1.0 - row_peak / 72.0)

    boundary_score = _best_boundary_score(candidates)
    weak_boundary = _unit(0.62 * (1.0 - boundary_score) + 0.38 * row_weakness)
    visibility = _unit(1.0 - glare_ratio)
    prior = _prior_score(previous_state)
    glare_conflict = _unit(glare_ratio / max(0.01, settings.glare_ratio_unknown))

    score = _unit(
        0.52 * weak_boundary
        + 0.28 * uniformity
        + 0.20 * visibility
        + 0.06 * prior
        - 0.22 * glare_conflict
    )
    if boundary_score >= max(0.78, settings.oil_tracker_update_confidence + 0.12):
        score = min(score, 0.42)
        reason = "strong_boundary_evidence"
    elif glare_conflict >= 0.75:
        reason = "glare_visibility_conflict"
    elif uniformity >= 0.70 and weak_boundary >= 0.65:
        reason = "uniform_region_with_weak_boundary"
    elif weak_boundary >= 0.65:
        reason = "weak_boundary_evidence"
    else:
        reason = "mixed_boundary_and_region_evidence"

    return NoInterfaceEvidence(
        score=score,
        boundary_score=boundary_score,
        uniformity_score=uniformity,
        weak_boundary_score=weak_boundary,
        visibility_score=visibility,
        glare_conflict=glare_conflict,
        prior_score=prior,
        mean_intensity=mean_intensity,
        texture=texture,
        reason=reason,
        available=True,
    )


def _best_boundary_score(candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...]) -> float:
    values = [
        float(candidate.features.get("observation_score", candidate.final_score))
        for candidate in candidates
        if not candidate.rejected
    ]
    return _unit(max(values, default=0.0))


def _prior_score(previous_state: FillState | None) -> float:
    return 1.0 if previous_state in {
        FillState.FULL_NO_INTERFACE,
        FillState.EMPTY_NO_INTERFACE,
        FillState.FULL_WITH_FOAM,
    } else 0.0


def _unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
