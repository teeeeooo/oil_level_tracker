from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import DetectorSettings

from .candidate_generators import signed_region_contrast_profiles
from .preprocessing import PreprocessResult
from .row_features import (
    MaskedBandIntensityProfiles,
    binary_band_overlap_profile,
    masked_band_intensity_profiles,
    masked_row_mean,
    row_coverage,
)


@dataclass
class CandidateScoreContext:
    pre: PreprocessResult
    effective_mask: np.ndarray
    ellipse_mask: np.ndarray
    exclusion_mask: np.ndarray
    settings: DetectorSettings
    previous_y: float | None = None
    previous_state: FillState | None = None
    previous_polarity: float | None = None
    static_artifact_map: np.ndarray | None = None


@dataclass(frozen=True)
class _IntensityEvidence:
    above: float
    below: float
    signed_difference: float
    available: bool


def score_candidates(
    candidates: list[BoundaryCandidate],
    context: CandidateScoreContext,
) -> list[BoundaryCandidate]:
    if not candidates:
        return []
    pre, mask, settings = context.pre, context.effective_mask, context.settings
    effective = mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    energy = masked_row_mean(pre.sobel_y_abs, effective)
    energy /= max(1.0, float(energy.max()))
    coverage = row_coverage(pre.horizontal_mask, effective)
    signed = masked_row_mean(pre.sobel_y_signed, effective)
    h = mask.shape[0]
    valid_ys = np.flatnonzero(effective.any(axis=1))
    top = int(valid_ys.min()) if valid_ys.size else 0
    bottom = int(valid_ys.max()) if valid_ys.size else h - 1
    persistent_band = max(
        8,
        int(math.ceil(float(settings.oil_consensus_tolerance_px) * 2.5)),
    )
    local_intensity = masked_band_intensity_profiles(
        pre.blurred,
        visible,
        5,
        reference_mask=effective,
        minimum_fraction=0.45,
        minimum_pixels=5,
        include_center_extra=True,
    )
    persistent_intensity = masked_band_intensity_profiles(
        pre.blurred,
        visible,
        persistent_band,
        reference_mask=effective,
        minimum_fraction=0.45,
        minimum_pixels=5,
        include_center_extra=True,
    )
    glare_profile = binary_band_overlap_profile(pre.glare_mask, effective, 2)
    exclusion_profile = binary_band_overlap_profile(
        context.exclusion_mask,
        context.ellipse_mask,
        2,
    )
    static_profile = (
        binary_band_overlap_profile(
            context.static_artifact_map,
            context.ellipse_mask,
            3,
        )
        if context.static_artifact_map is not None
        else None
    )

    for candidate in candidates:
        y = int(round(candidate.y))
        if y < 1 or y >= h - 1 or not effective[y].any():
            candidate.rejected = True
            candidate.reject_reason = "outside_effective_mask"
            candidate.final_score = 0.0
            continue

        intensity = _profile_evidence(local_intensity, y)
        persistent = _profile_evidence(persistent_intensity, y)
        edge = _unit(energy[y])
        horizontal = _unit(coverage[y])
        signed_sobel_raw = _finite(signed[y])
        signed_sobel_normalized = _signed_unit(-signed_sobel_raw / 80.0)
        signed_contrast_normalized = (
            _signed_unit(intensity.signed_difference / 80.0)
            if intensity.available
            else 0.0
        )
        polarity_combined = (
            0.45 * signed_sobel_normalized + 0.55 * signed_contrast_normalized
            if intensity.available
            else signed_sobel_normalized
        )
        polarity_score = _unit(abs(polarity_combined))
        polarity_sign = (
            0.0
            if polarity_score < 1e-9
            else (1.0 if polarity_combined > 0.0 else -1.0)
        )
        polarity_confidence = _unit(
            0.50 * polarity_score
            + 0.50
            * (
                abs(intensity.signed_difference) / 42.0
                if intensity.available
                else 0.0
            )
        )
        polarity_consistency = _polarity_consistency(
            polarity_sign,
            polarity_score,
            context.previous_polarity,
        )
        region = (
            _unit(abs(intensity.signed_difference) / 80.0)
            if intensity.available
            else 0.0
        )
        persistent_region = (
            _unit(abs(persistent.signed_difference) / 80.0)
            if persistent.available
            else 0.0
        )
        persistent_polarity_sign = (
            0.0
            if not persistent.available
            or abs(persistent.signed_difference) < 1e-9
            else (1.0 if persistent.signed_difference > 0.0 else -1.0)
        )
        temporal = (
            0.5
            if context.previous_y is None
            else math.exp(
                -abs(candidate.y - context.previous_y)
                / max(1.0, settings.temporal_max_jump_px)
            )
        )
        state_score = _state_plausibility(
            candidate.y,
            top,
            bottom,
            context.previous_state,
        )
        consensus = _unit(candidate.features.get("consensus_score", 0.0))
        support = int(
            round(candidate.features.get("unique_generator_support_count", 1.0))
        )
        glare = _unit(glare_profile[y])
        exclusion = _unit(exclusion_profile[y])
        edge_distance = min(
            abs(candidate.y - top),
            abs(bottom - candidate.y),
        ) / max(1.0, bottom - top)
        border = (
            max(0.0, 1.0 - edge_distance / 0.10)
            if edge_distance < 0.10
            else 0.0
        )
        static = 0.0 if static_profile is None else _unit(static_profile[y])
        jump = 0.0
        if context.previous_y is not None:
            jump = max(
                0.0,
                abs(candidate.y - context.previous_y)
                - settings.temporal_max_jump_px,
            ) / max(1.0, settings.temporal_max_jump_px)
            jump = min(1.0, jump)

        single_source = (
            1.0
            if support < int(settings.oil_min_consensus_sources)
            else 0.0
        )
        polarity_conflict = (
            1.0 - polarity_consistency
            if context.previous_polarity not in (None, 0.0)
            and polarity_score >= settings.oil_min_polarity_score
            else 0.0
        )
        dynamic_evidence = _unit(
            max(
                region,
                persistent_region,
                polarity_score,
                0.72 * edge + 0.28 * horizontal,
            )
        )
        static_dynamic_relief = _unit(dynamic_evidence * consensus)
        effective_static = _unit(
            static * (1.0 - 0.72 * static_dynamic_relief)
        )
        glare_conflict = glare >= float(settings.glare_ratio_unknown)

        candidate.features.update(
            {
                "edge_strength": edge,
                "horizontal_coverage": horizontal,
                "region_contrast": region,
                "absolute_region_contrast": region,
                "signed_sobel_y": signed_sobel_raw,
                "signed_sobel_normalized": signed_sobel_normalized,
                "above_intensity": intensity.above,
                "below_intensity": intensity.below,
                "signed_above_minus_below": intensity.signed_difference,
                "polarity_score": polarity_score,
                "polarity_confidence": polarity_confidence,
                "polarity_sign": polarity_sign,
                "polarity_available": float(intensity.available),
                "polarity_consistency": polarity_consistency,
                "persistent_above_intensity": persistent.above,
                "persistent_below_intensity": persistent.below,
                "persistent_signed_above_minus_below": persistent.signed_difference,
                "persistent_region_contrast": persistent_region,
                "persistent_polarity_sign": persistent_polarity_sign,
                "persistent_polarity_available": float(persistent.available),
                "persistent_intensity_band_px": float(persistent_band),
                "gradient_direction": polarity_score,
                "temporal_score": temporal,
                "state_transition_score": state_score,
                "consensus_score": consensus,
                "unique_generator_support_count": float(support),
                "dynamic_boundary_evidence": dynamic_evidence,
                "static_dynamic_relief": static_dynamic_relief,
                "glare_band_visibility_conflict": float(glare_conflict),
            }
        )
        candidate.penalties.update(
            {
                "glare_penalty": glare,
                "border_penalty": border,
                "exclusion_penalty": exclusion,
                "static_artifact_penalty": effective_static,
                "jump_penalty": jump,
                "single_source_penalty": single_source,
                "polarity_conflict_penalty": polarity_conflict,
                "paired_structure_penalty": 0.0,
            }
        )

        legacy_feature_score = (
            edge * settings.weight_edge
            + horizontal * settings.weight_coverage
            + region * settings.weight_region
            + polarity_score * settings.weight_gradient_direction
            + temporal * settings.weight_temporal
            + state_score * settings.weight_state
        )
        observation_feature_score = (
            edge * settings.weight_edge
            + horizontal * settings.weight_coverage
            + region * settings.weight_region
            + polarity_score * settings.weight_gradient_direction
            + consensus * settings.weight_temporal
            + state_score * settings.weight_state
        )
        common_penalty = (
            glare * settings.penalty_glare
            + border * settings.penalty_border
            + exclusion * settings.penalty_exclusion
            + effective_static * settings.penalty_static
            + single_source * 0.08
            + polarity_conflict * 0.16
        )
        legacy_penalty = common_penalty + jump * settings.penalty_jump
        candidate.feature_score = float(legacy_feature_score)
        candidate.penalty = float(legacy_penalty)
        candidate.final_score = _unit(
            legacy_feature_score - legacy_penalty + 0.10 * consensus
        )
        candidate.features["observation_feature_score"] = _unit(
            observation_feature_score
        )
        candidate.features["observation_score"] = _unit(
            observation_feature_score - common_penalty + 0.12 * consensus
        )
        candidate.features["static_overlap"] = static

        relative_position = (candidate.y - top) / max(1.0, bottom - top)
        strong_state_transition = (
            support >= int(settings.oil_min_consensus_sources)
            and consensus >= 0.65
            and persistent_region
            >= max(0.45, float(settings.minimum_region_contrast) * 3.0)
            and candidate.features["observation_score"]
            >= max(float(settings.minimum_final_confidence), 0.62)
        )
        candidate.features["state_transition_prior_conflict"] = float(
            (
                context.previous_state
                in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}
                and relative_position > 0.32
            )
            or (
                context.previous_state == FillState.EMPTY_NO_INTERFACE
                and relative_position < 0.68
            )
        )
        candidate.features["strong_state_transition_override"] = float(
            strong_state_transition
        )

        if (
            horizontal < settings.minimum_horizontal_coverage * 0.35
            and region < settings.minimum_region_contrast * 0.55
            and support < 2
        ):
            candidate.rejected = True
            candidate.reject_reason = "insufficient_horizontal_region_or_consensus"
        elif glare > 0.65:
            candidate.rejected = True
            candidate.reject_reason = "glare_overlap"
        elif glare_conflict or (glare > 0.30 and not intensity.available):
            candidate.rejected = True
            candidate.reject_reason = "glare_visibility_conflict"
        elif border > 0.85:
            candidate.rejected = True
            candidate.reject_reason = "rim_or_border"
        elif static >= 0.62 and dynamic_evidence < 0.42 and consensus < 0.72:
            candidate.rejected = True
            candidate.reject_reason = "static_horizontal_structure"
        elif (
            context.previous_state
            in {FillState.FULL_NO_INTERFACE, FillState.FULL_WITH_FOAM}
            and relative_position > 0.32
            and not strong_state_transition
        ):
            candidate.rejected = True
            candidate.reject_reason = "implausible_full_to_visible_transition"
        elif (
            context.previous_state == FillState.EMPTY_NO_INTERFACE
            and relative_position < 0.68
            and not strong_state_transition
        ):
            candidate.rejected = True
            candidate.reject_reason = "implausible_empty_to_visible_transition"
        elif (
            candidate.features["observation_score"]
            < settings.minimum_final_confidence * 0.62
        ):
            candidate.rejected = True
            candidate.reject_reason = "insufficient_boundary_observation"

    suppress_paired_horizontal_structures(candidates, settings)
    return sorted(candidates, key=_candidate_sort_key)


def suppress_paired_horizontal_structures(
    candidates: list[BoundaryCandidate],
    settings: DetectorSettings,
) -> None:
    """Resolve close opposite-polarity edges as a region step or a structure."""

    usable = sorted(
        (candidate for candidate in candidates if not candidate.rejected),
        key=lambda candidate: (float(candidate.y), str(candidate.source)),
    )
    minimum_distance = max(
        1.5,
        float(settings.oil_consensus_tolerance_px) * 0.45,
    )
    maximum_distance = max(
        8.0,
        float(settings.oil_consensus_tolerance_px) * 3.0,
    )
    resolved: set[int] = set()
    for left_index, left in enumerate(usable):
        if id(left) in resolved:
            continue
        for right in usable[left_index + 1 :]:
            if id(right) in resolved:
                continue
            distance = float(right.y) - float(left.y)
            if distance > maximum_distance:
                break
            if distance < minimum_distance:
                continue
            left_sign = float(left.features.get("polarity_sign", 0.0))
            right_sign = float(right.features.get("polarity_sign", 0.0))
            if (
                left_sign == 0.0
                or right_sign == 0.0
                or left_sign * right_sign >= 0.0
            ):
                continue

            left_score = float(
                left.features.get("observation_score", left.final_score)
            )
            right_score = float(
                right.features.get("observation_score", right.final_score)
            )
            primary, secondary = (
                (left, right)
                if _pair_candidate_order(left) <= _pair_candidate_order(right)
                else (right, left)
            )
            primary_score = max(left_score, right_score)
            secondary_score = min(left_score, right_score)
            primary_support = int(
                round(
                    primary.features.get(
                        "unique_generator_support_count",
                        0.0,
                    )
                )
            )
            secondary_polarity = abs(
                float(
                    secondary.features.get(
                        "polarity_score",
                        secondary.features.get("polarity_sign", 0.0),
                    )
                )
            )
            if (
                primary_score
                < max(0.68, float(settings.minimum_final_confidence) + 0.12)
                or primary_support < int(settings.oil_min_consensus_sources)
                or secondary_score
                < max(0.24, float(settings.minimum_final_confidence) * 0.55)
                or secondary_polarity
                < max(0.10, float(settings.oil_min_polarity_score))
            ):
                continue

            left_persistent = _unit(
                left.features.get("persistent_region_contrast", 0.0)
            )
            right_persistent = _unit(
                right.features.get("persistent_region_contrast", 0.0)
            )
            left_persistent_sign = float(
                left.features.get("persistent_polarity_sign", 0.0)
            )
            right_persistent_sign = float(
                right.features.get("persistent_polarity_sign", 0.0)
            )
            persistent_threshold = max(
                0.35,
                float(settings.minimum_region_contrast) * 3.0,
            )
            persistent_step = (
                max(left_persistent, right_persistent) >= persistent_threshold
                and left_persistent_sign != 0.0
                and right_persistent_sign != 0.0
                and left_persistent_sign * right_persistent_sign > 0.0
            )

            for candidate, partner in ((left, right), (right, left)):
                candidate.features["paired_structure_distance_px"] = distance
                candidate.features["paired_structure_partner_y"] = float(partner.y)
                candidate.features["paired_structure_opposite_polarity"] = 1.0
                candidate.features["paired_boundary_step_preserved"] = float(
                    persistent_step
                )

            if persistent_step:
                keeper, duplicate = (
                    (left, right)
                    if _pair_candidate_order(left) <= _pair_candidate_order(right)
                    else (right, left)
                )
                left_weight = max(0.05, left_score)
                right_weight = max(0.05, right_score)
                merged_y = (
                    left_weight * float(left.y) + right_weight * float(right.y)
                ) / (left_weight + right_weight)
                keeper.features["paired_boundary_original_y"] = float(keeper.y)
                keeper.features["paired_boundary_merged_y"] = float(merged_y)
                keeper.features["representative_local_y"] = float(merged_y)
                keeper.y = float(merged_y)
                keeper.rejected = False
                keeper.reject_reason = ""
                keeper.penalties["paired_structure_penalty"] = 0.0
                duplicate.penalties["paired_structure_penalty"] = 1.0
                duplicate.rejected = True
                duplicate.reject_reason = "paired_boundary_edge_duplicate"
            else:
                for candidate in (left, right):
                    candidate.penalties["paired_structure_penalty"] = 1.0
                    candidate.rejected = True
                    candidate.reject_reason = "paired_opposite_polarity_structure"
            resolved.update((id(left), id(right)))
            break

    for candidate in candidates:
        if id(candidate) not in resolved:
            candidate.features.setdefault("paired_structure_distance_px", 0.0)
            candidate.features.setdefault("paired_structure_partner_y", 0.0)
            candidate.features.setdefault("paired_structure_opposite_polarity", 0.0)
            candidate.features.setdefault("paired_boundary_step_preserved", 0.0)


def select_best_candidate(
    candidates: list[BoundaryCandidate],
    minimum_confidence: float,
) -> BoundaryCandidate | None:
    """Backward-compatible greedy helper; production uses OilTemporalPath."""

    for candidate in candidates:
        if not candidate.rejected and candidate.final_score >= minimum_confidence:
            candidate.selected = True
            return candidate
    return None


def build_oil_debug_profiles(
    context: CandidateScoreContext,
    candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...],
) -> dict[str, list[float]]:
    mask = context.effective_mask
    signed_sobel = masked_row_mean(context.pre.sobel_y_signed, mask)
    signed_sobel = np.clip(-signed_sobel / 80.0, -1.0, 1.0)
    coverage = row_coverage(context.pre.horizontal_mask, mask)
    glare_excluded = (mask > 0) & ~(context.pre.glare_mask > 0)
    signed_contrast, _absolute, _available = signed_region_contrast_profiles(
        context.pre.blurred,
        glare_excluded,
        band=5,
    )
    consensus = np.zeros(mask.shape[0], dtype=np.float32)
    for candidate in candidates:
        y = int(round(candidate.y))
        if 0 <= y < consensus.size:
            consensus[y] = max(
                consensus[y],
                _unit(candidate.features.get("consensus_score", 0.0)),
            )
    static = np.zeros(mask.shape[0], dtype=np.float32)
    if context.static_artifact_map is not None:
        static = row_coverage(
            context.static_artifact_map,
            context.ellipse_mask,
        )
    return {
        "oil_signed_sobel_profile": _finite_profile(signed_sobel),
        "oil_signed_contrast_profile": _finite_profile(signed_contrast),
        "oil_horizontal_coverage_profile": _finite_profile(coverage),
        "oil_consensus_support_profile": _finite_profile(consensus),
        "oil_static_overlap_profile": _finite_profile(static),
    }


def _profile_evidence(
    profiles: MaskedBandIntensityProfiles,
    y: int,
) -> _IntensityEvidence:
    return _IntensityEvidence(
        above=float(profiles.above[y]),
        below=float(profiles.below[y]),
        signed_difference=float(profiles.signed_difference[y]),
        available=bool(profiles.available[y]),
    )


def _signed_intensity_evidence(
    gray: np.ndarray,
    mask: np.ndarray,
    glare_mask: np.ndarray,
    y: int,
    band: int = 5,
) -> _IntensityEvidence:
    effective = mask > 0
    profiles = masked_band_intensity_profiles(
        gray,
        effective & ~(glare_mask > 0),
        band,
        reference_mask=effective,
        minimum_fraction=0.45,
        minimum_pixels=5,
        include_center_extra=True,
    )
    return _profile_evidence(profiles, y)


def _region_contrast(
    gray: np.ndarray,
    mask: np.ndarray,
    y: int,
    band: int = 5,
) -> float:
    evidence = _signed_intensity_evidence(
        gray,
        mask,
        np.zeros_like(mask),
        y,
        band,
    )
    return (
        _unit(abs(evidence.signed_difference) / 80.0)
        if evidence.available
        else 0.0
    )


def _row_overlap(
    binary: np.ndarray,
    denominator_mask: np.ndarray,
    y: int,
    band: int = 2,
) -> float:
    profile = binary_band_overlap_profile(binary, denominator_mask, band)
    return float(profile[y]) if 0 <= y < profile.size else 0.0


def _state_plausibility(
    y: float,
    top: int,
    bottom: int,
    previous_state: FillState | None,
) -> float:
    relative = (y - top) / max(1.0, bottom - top)
    if previous_state in {
        FillState.FULL_NO_INTERFACE,
        FillState.FULL_WITH_FOAM,
    }:
        return max(0.25, 1.0 - relative)
    if previous_state == FillState.EMPTY_NO_INTERFACE:
        return max(0.25, relative)
    if previous_state in {
        FillState.DRAINING_VISIBLE,
        FillState.FILLING_VISIBLE,
        FillState.PARTIAL_VISIBLE,
        FillState.FOAMING_VISIBLE,
    }:
        return 0.75
    return 0.60


def _polarity_consistency(
    sign: float,
    score: float,
    previous: float | None,
) -> float:
    if previous in (None, 0.0) or sign == 0.0:
        return 0.5
    if sign * float(previous) > 0.0:
        return 1.0
    return _unit(0.35 - 0.25 * score)


def _candidate_sort_key(
    candidate: BoundaryCandidate,
) -> tuple[float, float, float, str]:
    return (
        -float(
            candidate.features.get(
                "observation_score",
                candidate.final_score,
            )
        ),
        -float(
            candidate.features.get(
                "unique_generator_support_count",
                0.0,
            )
        ),
        float(candidate.y),
        str(candidate.source),
    )


def _pair_candidate_order(
    candidate: BoundaryCandidate,
) -> tuple[float, float, float, float, str]:
    return (
        -float(
            candidate.features.get(
                "observation_score",
                candidate.final_score,
            )
        ),
        -float(
            candidate.features.get(
                "unique_generator_support_count",
                0.0,
            )
        ),
        -float(candidate.features.get("persistent_region_contrast", 0.0)),
        float(candidate.y),
        str(candidate.source),
    )


def _finite_profile(values: np.ndarray) -> list[float]:
    finite = np.nan_to_num(
        values.astype(np.float64),
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )
    return [float(value) for value in finite]


def _finite(value: float) -> float:
    number = float(value)
    return number if math.isfinite(number) else 0.0


def _unit(value: float) -> float:
    return min(1.0, max(0.0, _finite(value)))


def _signed_unit(value: float) -> float:
    return min(1.0, max(-1.0, _finite(value)))
