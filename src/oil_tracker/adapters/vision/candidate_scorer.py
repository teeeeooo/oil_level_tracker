from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .preprocessing import PreprocessResult
from .row_features import masked_row_mean, row_coverage


@dataclass
class CandidateScoreContext:
    pre: PreprocessResult
    effective_mask: np.ndarray
    ellipse_mask: np.ndarray
    exclusion_mask: np.ndarray
    settings: DetectorSettings
    previous_y: float | None = None
    previous_state: FillState | None = None
    static_artifact_map: np.ndarray | None = None


def score_candidates(candidates: list[BoundaryCandidate], context: CandidateScoreContext) -> list[BoundaryCandidate]:
    if not candidates:
        return []
    pre, mask, settings = context.pre, context.effective_mask, context.settings
    energy = masked_row_mean(pre.sobel_y_abs, mask)
    energy /= max(1.0, float(energy.max()))
    coverage = row_coverage(pre.horizontal_mask, mask)
    signed = masked_row_mean(pre.sobel_y_signed, mask)
    h = mask.shape[0]
    valid_ys = np.where(mask.any(axis=1))[0]
    top = int(valid_ys.min()) if valid_ys.size else 0
    bottom = int(valid_ys.max()) if valid_ys.size else h - 1

    for candidate in candidates:
        y = int(round(candidate.y))
        if y < 1 or y >= h - 1 or not mask[y].any():
            candidate.rejected = True
            candidate.reject_reason = "outside_effective_mask"
            candidate.final_score = 0.0
            continue
        region = _region_contrast(pre.blurred, mask, y)
        edge = float(energy[y])
        horizontal = float(max(coverage[y], candidate.features.get("generator_strength", 0.0) if candidate.source in {"hough", "canny"} else 0.0))
        gradient_direction = min(1.0, abs(float(signed[y])) / 80.0)
        temporal = 0.5 if context.previous_y is None else math.exp(-abs(candidate.y - context.previous_y) / max(1.0, settings.temporal_max_jump_px))
        state_score = _state_plausibility(candidate.y, top, bottom, context.previous_state)
        glare = _row_overlap(pre.glare_mask, mask, y)
        exclusion = _row_overlap(context.exclusion_mask, context.ellipse_mask, y)
        edge_distance = min(abs(candidate.y - top), abs(bottom - candidate.y)) / max(1.0, bottom - top)
        border = max(0.0, 1.0 - edge_distance / 0.10) if edge_distance < 0.10 else 0.0
        static = 0.0
        if context.static_artifact_map is not None:
            static = _row_overlap(context.static_artifact_map, context.ellipse_mask, y)
        jump = 0.0
        if context.previous_y is not None:
            jump = max(0.0, abs(candidate.y - context.previous_y) - settings.temporal_max_jump_px) / max(1.0, settings.temporal_max_jump_px)
            jump = min(1.0, jump)

        candidate.features.update(
            {
                "edge_strength": edge,
                "horizontal_coverage": horizontal,
                "region_contrast": region,
                "gradient_direction": gradient_direction,
                "temporal_score": temporal,
                "state_transition_score": state_score,
            }
        )
        candidate.penalties.update(
            {
                "glare_penalty": glare,
                "border_penalty": border,
                "exclusion_penalty": exclusion,
                "static_artifact_penalty": static,
                "jump_penalty": jump,
            }
        )
        feature_score = (
            edge * settings.weight_edge
            + horizontal * settings.weight_coverage
            + region * settings.weight_region
            + gradient_direction * settings.weight_gradient_direction
            + temporal * settings.weight_temporal
            + state_score * settings.weight_state
        )
        penalty = (
            glare * settings.penalty_glare
            + border * settings.penalty_border
            + exclusion * settings.penalty_exclusion
            + static * settings.penalty_static
            + jump * settings.penalty_jump
        )
        candidate.feature_score = float(feature_score)
        candidate.penalty = float(penalty)
        candidate.final_score = float(max(0.0, min(1.0, feature_score - penalty)))
        relative_position = (candidate.y - top) / max(1.0, bottom - top)
        if context.previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM} and relative_position > 0.32:
            candidate.rejected = True
            candidate.reject_reason = "implausible_full_to_visible_transition"
        elif context.previous_state == FillState.EMPTY_NO_INTERFACE and relative_position < 0.68:
            candidate.rejected = True
            candidate.reject_reason = "implausible_empty_to_visible_transition"
        elif horizontal < settings.minimum_horizontal_coverage * 0.35 and region < settings.minimum_region_contrast * 0.55:
            candidate.rejected = True
            candidate.reject_reason = "insufficient_horizontal_or_region_evidence"
        elif glare > 0.65:
            candidate.rejected = True
            candidate.reject_reason = "glare_overlap"
        elif border > 0.85:
            candidate.rejected = True
            candidate.reject_reason = "rim_or_border"
        elif candidate.final_score < settings.minimum_final_confidence:
            candidate.rejected = True
            candidate.reject_reason = "below_confidence_threshold"
    return sorted(candidates, key=lambda c: c.final_score, reverse=True)


def select_best_candidate(candidates: list[BoundaryCandidate], minimum_confidence: float) -> BoundaryCandidate | None:
    for candidate in candidates:
        if not candidate.rejected and candidate.final_score >= minimum_confidence:
            candidate.selected = True
            return candidate
    return None


def _region_contrast(gray: np.ndarray, mask: np.ndarray, y: int, band: int = 5) -> float:
    y0, y1 = max(0, y - band), min(gray.shape[0], y + band + 1)
    above_mask = mask[y0:y] > 0
    below_mask = mask[y:y1] > 0
    if above_mask.sum() < 5 or below_mask.sum() < 5:
        return 0.0
    above = float(gray[y0:y][above_mask].mean())
    below = float(gray[y:y1][below_mask].mean())
    return min(1.0, abs(above - below) / 80.0)


def _row_overlap(binary: np.ndarray, denominator_mask: np.ndarray, y: int, band: int = 2) -> float:
    y0, y1 = max(0, y - band), min(binary.shape[0], y + band + 1)
    denominator = denominator_mask[y0:y1] > 0
    count = int(denominator.sum())
    return 0.0 if count == 0 else float(((binary[y0:y1] > 0) & denominator).sum()) / count


def _state_plausibility(y: float, top: int, bottom: int, previous_state: FillState | None) -> float:
    relative = (y - top) / max(1.0, bottom - top)
    if previous_state in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}:
        return max(0.0, 1.0 - relative)
    if previous_state == FillState.EMPTY_NO_INTERFACE:
        return max(0.0, relative)
    if previous_state in {FillState.DRAINING_VISIBLE, FillState.FILLING_VISIBLE, FillState.PARTIAL_VISIBLE, FillState.FOAMING_VISIBLE}:
        return 0.75
    return 0.60
