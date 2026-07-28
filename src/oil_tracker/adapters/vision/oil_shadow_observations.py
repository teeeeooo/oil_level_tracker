from __future__ import annotations

from dataclasses import replace
import math
from statistics import median

import cv2
import numpy as np

from .preprocessing import PreprocessResult
from .row_features import (
    binary_band_overlap_profile,
    masked_band_intensity_profiles,
    masked_row_mean,
    row_coverage,
)
from .oil_shadow_types import (
    BoundedYProposal,
    BroadEvidenceSummary,
    BroadScaleEvidence,
    NarrowEvidenceSummary,
    NarrowScaleEvidence,
    OilShadowBounds,
    RawEdgeObservation,
    SemanticHypothesis,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowCurrentObservation,
    ShadowHypothesisLabel,
    ShadowNoInterfaceEvidence,
    ShadowNoInterfaceObservation,
    ShadowSourceFamily,
    ShadowUnavailableObservation,
    StaticPriorEvidence,
    stable_digest,
)


def extract_raw_observations(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    *,
    crop_origin_y: float,
    bounds: OilShadowBounds,
) -> tuple[RawEdgeObservation, ...]:
    """Extract bounded immutable observations without using legacy candidates."""

    _validate_same_shape(pre.gray, effective_mask)
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    height, width = effective.shape
    valid_support = effective.sum(axis=1).astype(np.float64) / max(1, width)
    visible_support = np.divide(
        visible.sum(axis=1).astype(np.float64),
        np.maximum(1, effective.sum(axis=1)),
    )
    observations: list[RawEdgeObservation] = []

    energy = masked_row_mean(pre.sobel_y_abs, effective)
    energy = _normalize_profile(energy)
    coverage = row_coverage(pre.horizontal_mask, effective)
    signed_sobel = masked_row_mean(pre.sobel_y_signed, effective)
    observations.extend(
        _profile_observations(
            ShadowSourceFamily.SOBEL,
            1,
            energy,
            signed_sobel,
            valid_support,
            visible_support,
            crop_origin_y,
            width,
            bounds,
            horizontal_support=coverage,
        )
    )

    observations.extend(
        _profile_observations(
            ShadowSourceFamily.CANNY,
            1,
            coverage,
            signed_sobel,
            valid_support,
            visible_support,
            crop_origin_y,
            width,
            bounds,
            horizontal_support=coverage,
        )
    )

    observations.extend(
        _hough_observations(
            pre,
            effective,
            valid_support,
            visible_support,
            crop_origin_y,
            bounds,
        )
    )

    for band in bounds.broad_band_scales:
        profiles = masked_band_intensity_profiles(
            pre.blurred,
            visible,
            band,
            reference_mask=effective,
            minimum_fraction=0.40,
            minimum_pixels=5,
        )
        signed = np.clip(profiles.signed_difference / 255.0, -1.0, 1.0)
        strength = np.where(profiles.available, np.abs(signed), 0.0)
        observations.extend(
            _profile_observations(
                ShadowSourceFamily.REGION_STEP,
                band,
                strength,
                signed,
                valid_support,
                visible_support,
                crop_origin_y,
                width,
                bounds,
                availability=profiles.available,
                band_height=float(band),
                horizontal_support=valid_support,
            )
        )

    ordered = sorted(observations, key=lambda item: item.canonical_key)
    return tuple(ordered[: bounds.total_raw_observations])


def build_bounded_proposals(
    observations: tuple[RawEdgeObservation, ...] | list[RawEdgeObservation],
    bounds: OilShadowBounds,
) -> tuple[BoundedYProposal, ...]:
    ordered = tuple(sorted(observations, key=lambda item: item.canonical_key))
    groups: list[list[RawEdgeObservation]] = []
    retained = 0
    for observation in ordered:
        if retained >= bounds.total_retained_members:
            break
        if not groups:
            groups.append([observation])
            retained += 1
            continue
        current = groups[-1]
        proposed_max = max(current[-1].local_y, observation.local_y)
        proposed_min = min(current[0].local_y, observation.local_y)
        fits = (
            proposed_max - proposed_min <= bounds.maximum_proposal_diameter_px + 1e-12
            and len(current) < bounds.members_per_proposal
        )
        if fits:
            current.append(observation)
            retained += 1
        elif len(groups) < bounds.total_proposals:
            groups.append([observation])
            retained += 1
        else:
            break

    proposals: list[BoundedYProposal] = []
    for group in groups[: bounds.total_proposals]:
        ys = sorted(float(item.local_y) for item in group)
        representative = float(median(ys))
        source_offset = float(median([item.source_y - item.local_y for item in group]))
        member_ids = tuple(sorted({item.identity for item in group}))
        identity = stable_digest(
            "oil-shadow-proposal",
            (
                ("member_ids", "|".join(member_ids)),
                ("minimum_local_y", ys[0]),
                ("maximum_local_y", ys[-1]),
                ("representative_local_y", representative),
            ),
        )
        proposals.append(
            BoundedYProposal(
                identity=identity,
                member_ids=member_ids,
                minimum_local_y=ys[0],
                maximum_local_y=ys[-1],
                representative_local_y=representative,
                representative_source_y=representative + source_offset,
                source_family_count=len({item.source_family for item in group}),
            )
        )
    return tuple(proposals)


def evaluate_semantic_hypotheses(
    proposals: tuple[BoundedYProposal, ...],
    observations: tuple[RawEdgeObservation, ...],
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ellipse_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
    bounds: OilShadowBounds,
) -> tuple[SemanticHypothesis, ...]:
    _validate_same_shape(
        pre.gray,
        effective_mask,
        ellipse_mask,
        exclusion_mask,
        pre.glare_mask,
    )
    observation_by_id = {item.identity: item for item in observations}
    broad_profiles = _broad_profiles(pre, effective_mask, exclusion_mask, bounds)
    narrow_context = _narrow_context(
        pre,
        effective_mask,
        ellipse_mask,
        exclusion_mask,
        static_artifact_map,
        bounds,
    )
    hypotheses: list[SemanticHypothesis] = []
    for proposal in proposals:
        members = tuple(observation_by_id[item] for item in proposal.member_ids)
        broad = _broad_summary(proposal, broad_profiles, bounds)
        narrow = _narrow_summary(proposal, narrow_context, bounds)
        static_prior = _static_prior(narrow, broad, static_artifact_map, bounds)
        hypothesis = _semantic_hypothesis(
            proposal,
            members,
            broad,
            narrow,
            static_prior,
            crop_origin_y,
        )
        hypotheses.append(hypothesis)
    return semantic_deduplicate(tuple(hypotheses), bounds)


def semantic_deduplicate(
    hypotheses: tuple[SemanticHypothesis, ...] | list[SemanticHypothesis],
    bounds: OilShadowBounds,
) -> tuple[SemanticHypothesis, ...]:
    ordered = sorted(
        hypotheses,
        key=lambda item: (
            item.representative_local_y,
            item.label.value,
            item.identity,
        ),
    )
    groups: list[list[SemanticHypothesis]] = []
    tolerance = min(2.0, bounds.maximum_proposal_diameter_px / 3.0)
    for item in ordered:
        compatible_group = None
        for group in groups:
            minimum = min(value.minimum_local_y for value in group + [item])
            maximum = max(value.maximum_local_y for value in group + [item])
            if maximum - minimum > bounds.maximum_proposal_diameter_px + 1e-12:
                continue
            representative = float(median([value.representative_local_y for value in group]))
            if abs(item.representative_local_y - representative) > tolerance + 1e-12:
                continue
            if all(_semantically_compatible(item, prior) for prior in group):
                compatible_group = group
                break
        if compatible_group is None:
            groups.append([item])
        else:
            compatible_group.append(item)

    merged = [_merge_hypothesis_group(group) for group in groups]
    merged.sort(key=_hypothesis_order)
    return tuple(merged[: bounds.semantic_hypotheses])


def evaluate_typed_current_observation(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    hypotheses: tuple[SemanticHypothesis, ...],
) -> ShadowCurrentObservation:
    no_interface = _no_interface_evidence(pre, effective_mask, hypotheses)
    if not no_interface.available and no_interface.visibility < 0.20:
        return ShadowUnavailableObservation(
            visibility=no_interface.visibility,
            reason=no_interface.reason,
        )

    ordered = sorted(hypotheses, key=_hypothesis_order)
    best = ordered[0] if ordered else None
    second_boundary = ordered[1].boundary_likelihood if len(ordered) > 1 else 0.0
    if best is not None:
        boundary_margin = max(
            0.0,
            best.boundary_likelihood
            - max(best.artifact_likelihood, no_interface.likelihood, second_boundary),
        )
        standard_boundary = (
            best.boundary_likelihood >= 0.48
            and boundary_margin >= 0.08
            and best.ambiguity_likelihood < 0.72
            and best.visibility >= 0.30
        )
        corroborated_single_boundary = (
            _accepts_corroborated_single_dominant_boundary(
                best,
                ordered,
                no_interface,
            )
        )
        if standard_boundary or corroborated_single_boundary:
            return ShadowBoundaryObservation(
                hypothesis=best,
                alternatives=tuple(
                    sorted(item.identity for item in ordered[1:3])
                ),
            )

    competing_boundary = 0.0 if best is None else best.boundary_likelihood
    if (
        no_interface.available
        and no_interface.likelihood >= 0.58
        and no_interface.likelihood - competing_boundary >= 0.10
    ):
        return ShadowNoInterfaceObservation(evidence=no_interface)

    reason = "competing_boundary_artifact_or_no_interface_evidence"
    if best is not None and best.polarity_available is False:
        reason = "polarity_unavailable_or_conflicting"
    elif no_interface.glare_conflict >= 0.55:
        reason = "glare_visibility_conflict"
    return ShadowAmbiguousObservation(
        hypothesis_ids=tuple(sorted(item.identity for item in ordered[:3])),
        boundary_likelihood=competing_boundary,
        artifact_likelihood=0.0 if best is None else best.artifact_likelihood,
        ambiguity_likelihood=max(
            0.35,
            no_interface.glare_conflict,
            0.0 if best is None else best.ambiguity_likelihood,
        ),
        no_interface_likelihood=no_interface.likelihood,
        visibility=no_interface.visibility,
        projected_source_y=None if best is None else best.representative_source_y,
        reason=reason,
    )


def _accepts_corroborated_single_dominant_boundary(
    best: SemanticHypothesis,
    ordered: list[SemanticHypothesis],
    no_interface: ShadowNoInterfaceEvidence,
) -> bool:
    """Accept only a fully corroborated single hypothesis below the general floor."""

    if len(ordered) != 1:
        return False
    pulse_artifact = _narrow_pulse_artifact(best.narrow)
    spatial_conflict = max(
        best.broad.glare_conflict,
        best.broad.exclusion_conflict,
        best.narrow.glare_overlap,
        best.narrow.exclusion_overlap,
        best.narrow.border_overlap,
    )
    polarity_coherent = (
        not best.polarity_available
        or best.broad.polarity_consistency >= 0.85
    )
    return (
        len(best.proposal_ids) == 1
        and len(best.observation_ids) >= 6
        and best.boundary_likelihood >= 0.43
        and best.boundary_likelihood - best.artifact_likelihood >= 0.26
        and best.boundary_likelihood - no_interface.likelihood > 1e-12
        and best.ambiguity_likelihood < 0.60
        and best.broad.available_scale_count >= 2
        and best.broad.strength >= 0.40
        and best.broad.scale_consistency >= 0.85
        and best.narrow.available
        and best.narrow.peak_strength >= 0.90
        and best.narrow.scale_persistence >= 0.90
        and pulse_artifact <= 0.50
        and best.narrow.paired_edge_strength <= 0.80
        and best.visibility >= 0.85
        and best.evidence_availability >= 0.90
        and polarity_coherent
        and spatial_conflict <= 0.15
        and best.static_prior.contribution <= 0.08
        and best.narrow.static_overlap <= 0.20
    )


def _profile_observations(
    family: ShadowSourceFamily,
    scale: int,
    response: np.ndarray,
    signed: np.ndarray,
    valid_support: np.ndarray,
    visible_support: np.ndarray,
    crop_origin_y: float,
    measurement_width: int,
    bounds: OilShadowBounds,
    *,
    availability: np.ndarray | None = None,
    band_height: float = 1.0,
    horizontal_support: np.ndarray | None = None,
) -> list[RawEdgeObservation]:
    rows = _bounded_peak_rows(
        response,
        bounds.observations_per_source_scale,
        minimum=0.04 if family is ShadowSourceFamily.REGION_STEP else 0.08,
        availability=availability,
    )
    support_profile = response if horizontal_support is None else horizontal_support
    output: list[RawEdgeObservation] = []
    for source_index, row in enumerate(rows):
        signed_value = float(signed[row])
        polarity_available = bool(
            (availability is None or availability[row])
            and abs(signed_value) >= 0.015
        )
        polarity = _signed_unit(signed_value) if polarity_available else 0.0
        scalar_items = (
            ("source_family", family.value),
            ("measurement_scale", scale),
            ("local_y", float(row)),
            ("source_y", float(row) + float(crop_origin_y)),
            ("polarity_available", polarity_available),
            ("polarity", polarity),
            ("response_strength", _unit(response[row])),
            ("horizontal_support", _unit(support_profile[row])),
            ("valid_mask_support", _unit(valid_support[row])),
            ("glare_visible_support", _unit(visible_support[row])),
            ("measurement_width_px", float(measurement_width)),
            ("band_height_px", float(band_height)),
            ("source_local_index", source_index),
        )
        output.append(
            RawEdgeObservation(
                identity=stable_digest("oil-shadow-observation", scalar_items),
                source_family=family,
                measurement_scale=scale,
                local_y=float(row),
                source_y=float(row) + float(crop_origin_y),
                polarity_available=polarity_available,
                polarity=polarity,
                response_strength=_unit(response[row]),
                horizontal_support=_unit(support_profile[row]),
                valid_mask_support=_unit(valid_support[row]),
                glare_visible_support=_unit(visible_support[row]),
                measurement_width_px=float(measurement_width),
                band_height_px=float(band_height),
                source_local_index=source_index,
            )
        )
    return output


def _hough_observations(
    pre: PreprocessResult,
    effective: np.ndarray,
    valid_support: np.ndarray,
    visible_support: np.ndarray,
    crop_origin_y: float,
    bounds: OilShadowBounds,
) -> list[RawEdgeObservation]:
    height, width = effective.shape
    lines = cv2.HoughLinesP(
        pre.canny,
        rho=1,
        theta=np.pi / 180.0,
        threshold=max(8, int(round(width * 0.06))),
        minLineLength=max(5, int(round(width * 0.20))),
        maxLineGap=max(2, int(round(width * 0.03))),
    )
    records: list[tuple[float, float, float, float]] = []
    if lines is not None:
        for raw in lines[: bounds.observations_per_source_scale * 5]:
            x1, y1, x2, y2 = (int(value) for value in raw[0])
            dx = float(x2 - x1)
            dy = float(y2 - y1)
            angle = abs(math.degrees(math.atan2(dy, dx if abs(dx) > 1e-12 else 1e-12)))
            if angle > 12.0:
                continue
            y = (float(y1) + float(y2)) / 2.0
            if y < 0.0 or y > height - 1:
                continue
            support = _unit(math.hypot(dx, dy) / max(1.0, width))
            records.append((-support, y, angle, support))
    records.sort()
    output: list[RawEdgeObservation] = []
    for source_index, (_negative, y, angle, support) in enumerate(
        records[: bounds.observations_per_source_scale]
    ):
        row = min(height - 1, max(0, int(round(y))))
        scalar_items = (
            ("source_family", ShadowSourceFamily.HOUGH.value),
            ("measurement_scale", 1),
            ("local_y", y),
            ("source_y", y + crop_origin_y),
            ("response_strength", support),
            ("horizontal_support", support),
            ("valid_mask_support", _unit(valid_support[row])),
            ("glare_visible_support", _unit(visible_support[row])),
            ("measurement_width_px", float(width)),
            ("band_height_px", 1.0),
            ("source_local_index", source_index),
            ("angle", angle),
        )
        output.append(
            RawEdgeObservation(
                identity=stable_digest("oil-shadow-observation", scalar_items),
                source_family=ShadowSourceFamily.HOUGH,
                measurement_scale=1,
                local_y=y,
                source_y=y + crop_origin_y,
                polarity_available=False,
                polarity=0.0,
                response_strength=support,
                horizontal_support=support,
                valid_mask_support=_unit(valid_support[row]),
                glare_visible_support=_unit(visible_support[row]),
                measurement_width_px=float(width),
                band_height_px=1.0,
                source_local_index=source_index,
                source_angle_deg=angle,
            )
        )
    return output


def _broad_profiles(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    bounds: OilShadowBounds,
) -> dict[int, tuple[object, np.ndarray, np.ndarray, np.ndarray]]:
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    output = {}
    for scale in bounds.broad_band_scales:
        profiles = masked_band_intensity_profiles(
            pre.blurred,
            visible,
            scale,
            reference_mask=effective,
            minimum_fraction=0.40,
            minimum_pixels=5,
        )
        visible_support = binary_band_overlap_profile(visible, effective, scale)
        glare = binary_band_overlap_profile(pre.glare_mask, effective, scale)
        exclusion = binary_band_overlap_profile(exclusion_mask, effective_mask, scale)
        output[scale] = (profiles, visible_support, glare, exclusion)
    return output


def _broad_summary(
    proposal: BoundedYProposal,
    profiles_by_scale: dict[int, tuple[object, np.ndarray, np.ndarray, np.ndarray]],
    bounds: OilShadowBounds,
) -> BroadEvidenceSummary:
    rows: list[BroadScaleEvidence] = []
    height = next(iter(profiles_by_scale.values()))[1].size
    center = int(round(proposal.representative_local_y))
    search = range(max(0, center - 2), min(height, center + 3))
    for scale in bounds.broad_band_scales:
        profiles, visible_support, glare, exclusion = profiles_by_scale[scale]
        candidates = []
        for row in search:
            available = bool(profiles.available[row])
            signed = _signed_unit(float(profiles.signed_difference[row]) / 255.0) if available else 0.0
            candidates.append(
                (
                    -abs(signed),
                    row,
                    available,
                    signed,
                    _unit(visible_support[row]),
                    _unit(glare[row]),
                    _unit(exclusion[row]),
                )
            )
        _negative, row, available, signed, visible, glare_value, exclusion_value = min(candidates)
        strength = abs(signed) if available else 0.0
        transition_y = min(
            proposal.maximum_local_y,
            max(proposal.minimum_local_y, float(row)),
        )
        rows.append(
            BroadScaleEvidence(
                band_scale=scale,
                available=available,
                signed_contrast=signed,
                strength=strength,
                visible_support=visible,
                glare_conflict=glare_value,
                exclusion_conflict=exclusion_value,
                transition_local_y=transition_y,
            )
        )
    available_rows = [item for item in rows if item.available]
    strengths = [item.strength for item in available_rows]
    signs = [
        1.0 if item.signed_contrast > 0.0 else -1.0
        for item in available_rows
        if abs(item.signed_contrast) > 1e-12
    ]
    scale_consistency = (
        0.0
        if not strengths
        else _unit(1.0 - (max(strengths) - min(strengths)))
    )
    polarity_consistency = (
        0.0
        if not signs
        else max(signs.count(1.0), signs.count(-1.0)) / len(signs)
    )
    signed = (
        0.0
        if not available_rows
        else sum(item.signed_contrast for item in available_rows)
        / len(available_rows)
    )
    strength = (
        0.0
        if not strengths
        else _unit(
            sum(strengths)
            / len(strengths)
            * (0.55 + 0.45 * scale_consistency)
        )
    )
    transition = (
        proposal.representative_local_y
        if not available_rows
        else float(median([item.transition_local_y for item in available_rows]))
    )
    visibility = 0.0 if not rows else _unit(sum(item.visible_support for item in rows) / len(rows))
    glare = 0.0 if not rows else _unit(sum(item.glare_conflict for item in rows) / len(rows))
    exclusion = 0.0 if not rows else _unit(sum(item.exclusion_conflict for item in rows) / len(rows))
    return BroadEvidenceSummary(
        scales=tuple(rows),
        available_scale_count=len(available_rows),
        signed_contrast=_signed_unit(signed),
        strength=strength,
        scale_consistency=scale_consistency,
        polarity_consistency=_unit(polarity_consistency),
        transition_local_y=transition,
        visibility=visibility,
        glare_conflict=glare,
        exclusion_conflict=exclusion,
    )


def _narrow_context(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ellipse_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    bounds: OilShadowBounds,
) -> dict[str, np.ndarray]:
    effective = effective_mask > 0
    energy = _normalize_profile(masked_row_mean(pre.sobel_y_abs, effective))
    coverage = row_coverage(pre.horizontal_mask, effective)
    signed = np.clip(masked_row_mean(pre.sobel_y_signed, effective) / 255.0, -1.0, 1.0)
    context = {
        "energy": energy,
        "coverage": coverage,
        "signed": signed,
        "valid": effective.any(axis=1).astype(np.float32),
        "glare": binary_band_overlap_profile(pre.glare_mask, effective_mask, 2),
        "exclusion": binary_band_overlap_profile(exclusion_mask, ellipse_mask, 2),
        "border": _border_profile(effective),
        "static": np.zeros(effective.shape[0], dtype=np.float32),
    }
    if static_artifact_map is not None and static_artifact_map.shape == effective.shape:
        context["static"] = binary_band_overlap_profile(static_artifact_map, ellipse_mask, 2)
    return context


def _narrow_summary(
    proposal: BoundedYProposal,
    context: dict[str, np.ndarray],
    bounds: OilShadowBounds,
) -> NarrowEvidenceSummary:
    energy = context["energy"]
    coverage = context["coverage"]
    signed = context["signed"]
    height = energy.size
    center = min(height - 1, max(0, int(round(proposal.representative_local_y))))
    scale_rows: list[NarrowScaleEvidence] = []
    for scale in bounds.narrow_scales:
        start = max(0, center - scale)
        stop = min(height, center + scale + 1)
        available = bool(np.any(context["valid"][start:stop] > 0.0))
        peak = _unit(float(np.max(energy[start:stop]))) if available and stop > start else 0.0
        horizontal = _unit(float(np.max(coverage[start:stop]))) if available and stop > start else 0.0
        scale_rows.append(NarrowScaleEvidence(scale, available, peak, horizontal))

    center_peak = _unit(energy[center])
    paired_candidates: list[tuple[float, int, float]] = []
    radius = bounds.narrow_lobe_search_radius_px
    for row in range(
        max(0, center - radius), min(height, center + radius + 1)
    ):
        separation = abs(row - center)
        if separation < 2:
            continue
        strength = _unit(energy[row])
        paired_candidates.append((-strength, separation, float(row)))
    if paired_candidates:
        negative_strength, separation, paired_row = min(paired_candidates)
        paired_strength = _unit(min(center_peak, -negative_strength))
        symmetry = _unit(1.0 - abs(center_peak + negative_strength))
        center_offset = (paired_row - center) / 2.0
    else:
        separation = 0
        paired_strength = 0.0
        symmetry = 0.0
        center_offset = 0.0
    left = float(signed[max(0, center - 1)])
    right = float(signed[min(height - 1, center + 1)])
    lobe_order = _signed_unit((left - right) / 2.0)
    available_scales = [item for item in scale_rows if item.available]
    persistence = (
        0.0
        if not available_scales
        else _unit(
            sum(item.peak_strength for item in available_scales)
            / len(available_scales)
        )
    )
    return NarrowEvidenceSummary(
        scales=tuple(scale_rows),
        available=bool(available_scales),
        peak_strength=center_peak,
        horizontal_coverage=_unit(coverage[center]),
        signed_lobe_order=lobe_order,
        paired_edge_separation_px=float(separation),
        paired_edge_strength=paired_strength,
        pulse_symmetry=symmetry,
        center_offset_px=float(center_offset),
        scale_persistence=persistence,
        border_overlap=_unit(context["border"][center]),
        exclusion_overlap=_unit(context["exclusion"][center]),
        glare_overlap=_unit(context["glare"][center]),
        static_overlap=_unit(context["static"][center]),
    )


def _static_prior(
    narrow: NarrowEvidenceSummary,
    broad: BroadEvidenceSummary,
    static_map: np.ndarray | None,
    bounds: OilShadowBounds,
) -> StaticPriorEvidence:
    map_available = static_map is not None and static_map.size > 0
    undercovered = narrow.static_overlap < 0.01
    available = bool(map_available and not undercovered)
    if not available:
        return StaticPriorEvidence(False, 0.0, 0.0, 0.0)
    coverage = _unit(narrow.static_overlap)
    contribution = min(
        bounds.maximum_static_prior,
        bounds.maximum_static_prior
        * narrow.static_overlap
        * (1.0 - 0.85 * broad.strength),
    )
    return StaticPriorEvidence(
        True,
        coverage,
        _unit(narrow.static_overlap),
        _unit(contribution),
    )


def _narrow_boundary_support(narrow: NarrowEvidenceSummary) -> float:
    return _unit(
        0.45 * narrow.peak_strength
        + 0.30 * narrow.horizontal_coverage
        + 0.25 * narrow.scale_persistence
    )


def _narrow_pulse_artifact(narrow: NarrowEvidenceSummary) -> float:
    return _unit(
        0.36 * narrow.paired_edge_strength
        + 0.24 * narrow.pulse_symmetry
        + 0.14 * narrow.border_overlap
        + 0.12 * narrow.exclusion_overlap
        + 0.14 * narrow.glare_overlap
    )


def _semantic_hypothesis(
    proposal: BoundedYProposal,
    members: tuple[RawEdgeObservation, ...],
    broad: BroadEvidenceSummary,
    narrow: NarrowEvidenceSummary,
    static_prior: StaticPriorEvidence,
    crop_origin_y: float,
) -> SemanticHypothesis:
    polarity_values = [item.polarity for item in members if item.polarity_available]
    if broad.available_scale_count and abs(broad.signed_contrast) >= 0.015:
        polarity_values.append(broad.signed_contrast)
    polarity_available = bool(polarity_values)
    polarity = 0.0 if not polarity_values else _signed_unit(sum(polarity_values) / len(polarity_values))
    same_sign = 0.0
    if polarity_values:
        positives = sum(value > 0.0 for value in polarity_values)
        negatives = sum(value < 0.0 for value in polarity_values)
        same_sign = max(positives, negatives) / len(polarity_values)
    polarity_confidence = _unit(abs(polarity) * (0.55 + 0.45 * same_sign))
    availability = _unit(
        0.55 * (broad.available_scale_count / max(1, len(broad.scales)))
        + 0.45 * float(narrow.available)
    )
    visibility = _unit(0.65 * broad.visibility + 0.35 * (1.0 - narrow.glare_overlap))
    narrow_boundary = _narrow_boundary_support(narrow)
    pulse_artifact = _narrow_pulse_artifact(narrow)
    boundary = _unit(
        0.55 * broad.strength
        + 0.25 * narrow_boundary
        + 0.12 * polarity_confidence
        + 0.08 * visibility
        - 0.16 * pulse_artifact
        - 0.08 * static_prior.contribution
    )
    structural_artifact = _unit(
        0.58 * pulse_artifact
        + 0.18 * narrow.static_overlap
        + 0.12 * (1.0 - broad.scale_consistency)
        + 0.12 * (1.0 - broad.polarity_consistency)
    )
    artifact = _unit(
        structural_artifact * (1.0 - 0.82 * broad.strength)
        + static_prior.contribution
    )
    ambiguity = _unit(
        0.48 * (1.0 - abs(boundary - artifact))
        + 0.18 * (1.0 - polarity_confidence)
        + 0.18 * (1.0 - visibility)
        + 0.16 * (1.0 - availability)
    )
    if boundary - artifact >= 0.14 and ambiguity < 0.65:
        label = ShadowHypothesisLabel.BOUNDARY_LIKE
    elif artifact - boundary >= 0.14 and ambiguity < 0.65:
        label = ShadowHypothesisLabel.ARTIFACT_LIKE
    else:
        label = ShadowHypothesisLabel.AMBIGUOUS
    representative = (
        broad.transition_local_y
        if broad.available_scale_count >= 2
        and broad.scale_consistency >= 0.45
        and broad.polarity_consistency >= 0.50
        else proposal.representative_local_y
    )
    representative = min(
        proposal.maximum_local_y,
        max(proposal.minimum_local_y, representative),
    )
    identity = stable_digest(
        "oil-shadow-hypothesis",
        (
            ("proposal_id", proposal.identity),
            ("representative_local_y", representative),
            ("boundary_likelihood", boundary),
            ("artifact_likelihood", artifact),
            ("ambiguity_likelihood", ambiguity),
            ("polarity", polarity),
        ),
    )
    observation_ids = tuple(sorted(item.identity for item in members))
    return SemanticHypothesis(
        identity=identity,
        proposal_ids=(proposal.identity,),
        observation_ids=observation_ids,
        representative_local_y=representative,
        representative_source_y=representative + crop_origin_y,
        minimum_local_y=proposal.minimum_local_y,
        maximum_local_y=proposal.maximum_local_y,
        broad=broad,
        narrow=narrow,
        static_prior=static_prior,
        boundary_likelihood=boundary,
        artifact_likelihood=artifact,
        ambiguity_likelihood=ambiguity,
        evidence_availability=availability,
        visibility=visibility,
        polarity_available=polarity_available,
        polarity=polarity,
        polarity_confidence=polarity_confidence,
        label=label,
        provenance=tuple(sorted((proposal.identity,) + observation_ids)),
    )


def _semantically_compatible(left: SemanticHypothesis, right: SemanticHypothesis) -> bool:
    if left.polarity_available and right.polarity_available and left.polarity * right.polarity < 0.0:
        return False
    opposite_labels = {
        left.label,
        right.label,
    } == {
        ShadowHypothesisLabel.BOUNDARY_LIKE,
        ShadowHypothesisLabel.ARTIFACT_LIKE,
    }
    if opposite_labels:
        return False
    return (
        abs(left.boundary_likelihood - right.boundary_likelihood) <= 0.24
        and abs(left.artifact_likelihood - right.artifact_likelihood) <= 0.24
    )


def _merge_hypothesis_group(group: list[SemanticHypothesis]) -> SemanticHypothesis:
    if len(group) == 1:
        return group[0]
    ordered = sorted(group, key=_hypothesis_order)
    primary = ordered[0]
    proposal_ids = tuple(sorted({value for item in group for value in item.proposal_ids}))
    observation_ids = tuple(sorted({value for item in group for value in item.observation_ids}))
    provenance = tuple(sorted({value for item in group for value in item.provenance}))
    minimum = min(item.minimum_local_y for item in group)
    maximum = max(item.maximum_local_y for item in group)
    broad_candidates = [
        item
        for item in group
        if item.broad.available_scale_count >= 2
        and item.broad.scale_consistency >= 0.45
    ]
    representative = (
        float(median([item.broad.transition_local_y for item in broad_candidates]))
        if broad_candidates
        else float(median([item.representative_local_y for item in group]))
    )
    representative = min(maximum, max(minimum, representative))
    source_offset = float(median([item.representative_source_y - item.representative_local_y for item in group]))
    boundary = _unit(sum(item.boundary_likelihood for item in group) / len(group))
    artifact = _unit(sum(item.artifact_likelihood for item in group) / len(group))
    ambiguity = _unit(max(item.ambiguity_likelihood for item in group))
    polarity_values = [item.polarity for item in group if item.polarity_available]
    polarity = 0.0 if not polarity_values else _signed_unit(sum(polarity_values) / len(polarity_values))
    polarity_confidence = _unit(sum(item.polarity_confidence for item in group) / len(group))
    if boundary - artifact >= 0.14 and ambiguity < 0.65:
        label = ShadowHypothesisLabel.BOUNDARY_LIKE
    elif artifact - boundary >= 0.14 and ambiguity < 0.65:
        label = ShadowHypothesisLabel.ARTIFACT_LIKE
    else:
        label = ShadowHypothesisLabel.AMBIGUOUS
    identity = stable_digest(
        "oil-shadow-deduplicated-hypothesis",
        (
            ("proposal_ids", "|".join(proposal_ids)),
            ("observation_ids", "|".join(observation_ids)),
            ("representative_local_y", representative),
            ("boundary", boundary),
            ("artifact", artifact),
            ("ambiguity", ambiguity),
        ),
    )
    return replace(
        primary,
        identity=identity,
        proposal_ids=proposal_ids,
        observation_ids=observation_ids,
        provenance=provenance,
        representative_local_y=representative,
        representative_source_y=representative + source_offset,
        minimum_local_y=minimum,
        maximum_local_y=maximum,
        boundary_likelihood=boundary,
        artifact_likelihood=artifact,
        ambiguity_likelihood=ambiguity,
        evidence_availability=_unit(sum(item.evidence_availability for item in group) / len(group)),
        visibility=_unit(sum(item.visibility for item in group) / len(group)),
        polarity_available=bool(polarity_values),
        polarity=polarity,
        polarity_confidence=polarity_confidence,
        label=label,
    )


def _no_interface_evidence(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    hypotheses: tuple[SemanticHypothesis, ...],
) -> ShadowNoInterfaceEvidence:
    valid = effective_mask > 0
    count = int(np.count_nonzero(valid))
    if count == 0:
        return ShadowNoInterfaceEvidence(
            False, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, None, None, "empty_effective_mask"
        )
    glare = (pre.glare_mask > 0) & valid
    visible = valid & ~glare
    visible_count = int(np.count_nonzero(visible))
    visibility = _unit(visible_count / max(1, count))
    glare_conflict = _unit(np.count_nonzero(glare) / max(1, count))
    if visible_count < max(10, int(count * 0.08)):
        return ShadowNoInterfaceEvidence(
            False,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            max((item.boundary_likelihood for item in hypotheses), default=0.0),
            visibility,
            glare_conflict,
            None,
            None,
            "insufficient_visible_support",
        )
    values = pre.gray[visible].astype(np.float32)
    mean_intensity = float(np.median(values))
    texture = float(np.std(values))
    uniformity = _unit(1.0 - texture / 58.0)
    row_energy = _normalize_profile(masked_row_mean(pre.sobel_y_abs, visible))
    raster_weakness = _unit(1.0 - float(np.max(row_energy)))
    competing = max((item.boundary_likelihood for item in hypotheses), default=0.0)
    weak_boundary = _unit(0.58 * (1.0 - competing) + 0.42 * raster_weakness)
    full = _unit((145.0 - mean_intensity) / 55.0) * uniformity
    empty = _unit((mean_intensity - 115.0) / 70.0) * uniformity
    state_evidence = max(full, empty)
    likelihood = _unit(
        0.36 * weak_boundary
        + 0.27 * uniformity
        + 0.20 * visibility
        + 0.17 * state_evidence
        - 0.30 * glare_conflict
        - 0.38 * competing
    )
    if competing >= 0.72:
        reason = "strong_competing_boundary"
    elif glare_conflict >= 0.45:
        reason = "glare_visibility_conflict"
    elif state_evidence >= 0.45 and uniformity >= 0.65:
        reason = "positive_uniform_full_or_empty_evidence"
    else:
        reason = "mixed_no_interface_evidence"
    return ShadowNoInterfaceEvidence(
        True,
        likelihood,
        _unit(full),
        _unit(empty),
        uniformity,
        weak_boundary,
        _unit(competing),
        visibility,
        glare_conflict,
        mean_intensity,
        texture,
        reason,
    )


def _hypothesis_order(item: SemanticHypothesis) -> tuple[float, float, float, float, str]:
    return (
        -item.boundary_likelihood,
        item.artifact_likelihood,
        item.ambiguity_likelihood,
        item.representative_local_y,
        item.identity,
    )


def _bounded_peak_rows(
    profile: np.ndarray,
    limit: int,
    *,
    minimum: float,
    availability: np.ndarray | None = None,
) -> tuple[int, ...]:
    if profile.size < 3:
        return ()
    values = np.nan_to_num(profile.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    candidates = [
        row
        for row in range(1, values.size - 1)
        if values[row] >= minimum
        and values[row] >= values[row - 1]
        and values[row] >= values[row + 1]
        and (availability is None or bool(availability[row]))
    ]
    candidates.sort(key=lambda row: (-float(values[row]), row))
    selected: list[int] = []
    for row in candidates:
        if all(abs(row - prior) >= 3 for prior in selected):
            selected.append(row)
        if len(selected) >= limit:
            break
    return tuple(selected)


def _border_profile(effective: np.ndarray) -> np.ndarray:
    rows = np.flatnonzero(effective.any(axis=1))
    output = np.ones(effective.shape[0], dtype=np.float32)
    if not rows.size:
        return output
    top, bottom = int(rows.min()), int(rows.max())
    span = max(1.0, float(bottom - top))
    for row in range(effective.shape[0]):
        distance = min(abs(row - top), abs(bottom - row)) / span
        output[row] = _unit(1.0 - distance / 0.10) if distance < 0.10 else 0.0
    return output


def _normalize_profile(profile: np.ndarray) -> np.ndarray:
    finite = np.nan_to_num(profile.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    maximum = float(np.max(finite)) if finite.size else 0.0
    return np.zeros_like(finite) if maximum <= 1e-12 else np.clip(finite / maximum, 0.0, 1.0)


def _validate_same_shape(*arrays: np.ndarray) -> None:
    shape = arrays[0].shape[:2]
    if any(array.shape[:2] != shape for array in arrays):
        raise ValueError("Oil shadow raster inputs must share the same current-frame shape.")


def _unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))


def _signed_unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(-1.0, number))
