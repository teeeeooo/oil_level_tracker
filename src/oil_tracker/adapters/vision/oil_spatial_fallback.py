from __future__ import annotations

from dataclasses import dataclass
from statistics import median

import numpy as np

from . import oil_shadow_observations as observations
from .oil_shadow_types import (
    BoundedYProposal,
    BroadEvidenceSummary,
    BroadScaleEvidence,
    OilShadowBounds,
    RawEdgeObservation,
    SemanticHypothesis,
    ShadowBoundaryObservation,
    ShadowSourceFamily,
    SuccessfulPipelineFrame,
)
from .preprocessing import PreprocessResult
from .row_features import masked_band_intensity_profiles


_SECTOR_COUNT = 5


@dataclass(frozen=True)
class _SpatialPathEvidence:
    accepted: bool
    sector_count: int
    rows: tuple[int, ...]
    span_px: int
    maximum_jump_px: int
    median_local_y: float | None


def build_spatial_positive_fallback_frame(
    *,
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ellipse_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    base_raw_observations: tuple[RawEdgeObservation, ...],
    crop_origin_y: float,
    bounds: OilShadowBounds,
    accepted_foam_front_local_y: float | None,
    accepted_foam_component_mask: np.ndarray | None,
) -> SuccessfulPipelineFrame | None:
    """Build a secondary boundary frame only from additional cross-ROI evidence.

    The caller owns the P0-first guard and invokes this function only after the
    ordinary current-frame path has remained ambiguous. Relative phase creates a
    candidate but is never sufficient for publication by itself; the candidate
    must also exhibit a bounded, independently optimized five-sector path.
    """

    raw = _relative_region_observations(
        pre,
        effective_mask,
        base_raw_observations,
        crop_origin_y=crop_origin_y,
        bounds=bounds,
    )
    proposals = observations.build_bounded_proposals(raw, bounds)
    hypotheses = _relative_hypotheses(
        proposals,
        raw,
        pre,
        effective_mask,
        ellipse_mask,
        exclusion_mask,
        static_artifact_map,
        crop_origin_y=crop_origin_y,
        bounds=bounds,
    )
    current = observations.evaluate_typed_current_observation(
        pre,
        effective_mask,
        hypotheses,
        accepted_foam_front_local_y=accepted_foam_front_local_y,
        accepted_foam_component_mask=accepted_foam_component_mask,
    )
    if isinstance(current, ShadowBoundaryObservation):
        path = _evaluate_spatial_path(
            pre,
            effective_mask,
            candidate_local_y=current.hypothesis.representative_local_y,
            accepted_foam_component_mask=accepted_foam_component_mask,
            bounds=bounds,
        )
        if not path.accepted:
            return None
    else:
        recovered = _select_spatially_corroborated_textured_boundary(
            pre,
            effective_mask,
            hypotheses,
            accepted_foam_component_mask=accepted_foam_component_mask,
            bounds=bounds,
        )
        if recovered is None:
            return None
        current = observations._boundary_observation(
            recovered,
            sorted(hypotheses, key=observations._hypothesis_order),
        )
    return SuccessfulPipelineFrame(
        raw_observations=raw,
        proposals=proposals,
        hypotheses=hypotheses,
        current_observation=current,
        frame_height=int(pre.gray.shape[0]),
        frame_width=int(pre.gray.shape[1]),
    )


def _relative_region_observations(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    base_raw_observations: tuple[RawEdgeObservation, ...],
    *,
    crop_origin_y: float,
    bounds: OilShadowBounds,
) -> tuple[RawEdgeObservation, ...]:
    retained = [
        item
        for item in base_raw_observations
        if item.source_family is not ShadowSourceFamily.REGION_STEP
    ]
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    _height, width = effective.shape
    valid_support = effective.sum(axis=1).astype(np.float64) / max(1, width)
    visible_support = np.divide(
        visible.sum(axis=1).astype(np.float64),
        np.maximum(1, effective.sum(axis=1)),
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
        signed = _relative_signed_profile(profiles)
        strength = np.where(profiles.available, np.abs(signed), 0.0)
        retained.extend(
            observations._profile_observations(
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
    return tuple(
        sorted(retained, key=lambda item: item.canonical_key)[
            : bounds.total_raw_observations
        ]
    )


def _relative_signed_profile(profiles) -> np.ndarray:
    denominator = np.maximum(
        np.abs(profiles.above) + np.abs(profiles.below),
        1.0,
    )
    relative = 2.0 * profiles.signed_difference / denominator
    return np.where(
        profiles.available,
        np.clip(relative, -1.0, 1.0),
        0.0,
    )


def _relative_hypotheses(
    proposals: tuple[BoundedYProposal, ...],
    raw: tuple[RawEdgeObservation, ...],
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ellipse_mask: np.ndarray,
    exclusion_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
    bounds: OilShadowBounds,
) -> tuple[SemanticHypothesis, ...]:
    observation_by_id = {item.identity: item for item in raw}
    broad_profiles = observations._broad_profiles(
        pre,
        effective_mask,
        exclusion_mask,
        bounds,
    )
    narrow_context = observations._narrow_context(
        pre,
        effective_mask,
        ellipse_mask,
        exclusion_mask,
        static_artifact_map,
        bounds,
    )
    plateau_context = (
        observations._build_plateau_evidence_context(pre.gray, effective_mask)
        if proposals
        else None
    )
    hypotheses: list[SemanticHypothesis] = []
    for proposal in proposals:
        members = tuple(observation_by_id[item] for item in proposal.member_ids)
        broad = _relative_broad_summary(proposal, broad_profiles, bounds)
        narrow = observations._narrow_summary(proposal, narrow_context, bounds)
        static_prior = observations._static_prior(
            narrow,
            broad,
            static_artifact_map,
            bounds,
        )
        plateau = observations._plateau_artifact_from_context(
            plateau_context,
            broad.transition_local_y,
        )
        hypotheses.append(
            observations._semantic_hypothesis(
                proposal,
                members,
                broad,
                narrow,
                static_prior,
                plateau,
                crop_origin_y,
            )
        )
    return observations.semantic_deduplicate(tuple(hypotheses), bounds)


def _relative_broad_summary(
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
        signed_profile = _relative_signed_profile(profiles)
        candidates = []
        for row in search:
            available = bool(profiles.available[row])
            signed = float(signed_profile[row]) if available else 0.0
            candidates.append(
                (
                    -abs(signed),
                    row,
                    available,
                    signed,
                    observations._unit(visible_support[row]),
                    observations._unit(glare[row]),
                    observations._unit(exclusion[row]),
                )
            )
        (
            _negative,
            row,
            available,
            signed,
            visible,
            glare_value,
            exclusion_value,
        ) = min(candidates)
        transition_y = min(
            proposal.maximum_local_y,
            max(proposal.minimum_local_y, float(row)),
        )
        rows.append(
            BroadScaleEvidence(
                band_scale=scale,
                available=available,
                signed_contrast=signed,
                strength=abs(signed) if available else 0.0,
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
        else observations._unit(1.0 - (max(strengths) - min(strengths)))
    )
    polarity_consistency = (
        0.0
        if not signs
        else max(signs.count(1.0), signs.count(-1.0)) / len(signs)
    )
    signed = (
        0.0
        if not available_rows
        else sum(item.signed_contrast for item in available_rows) / len(available_rows)
    )
    strength = (
        0.0
        if not strengths
        else observations._unit(
            sum(strengths)
            / len(strengths)
            * (0.55 + 0.45 * scale_consistency)
        )
    )
    transition = (
        proposal.representative_local_y
        if not available_rows
        else float(median(item.transition_local_y for item in available_rows))
    )
    visibility = (
        0.0
        if not rows
        else observations._unit(
            sum(item.visible_support for item in rows) / len(rows)
        )
    )
    glare = (
        0.0
        if not rows
        else observations._unit(sum(item.glare_conflict for item in rows) / len(rows))
    )
    exclusion = (
        0.0
        if not rows
        else observations._unit(
            sum(item.exclusion_conflict for item in rows) / len(rows)
        )
    )
    return BroadEvidenceSummary(
        scales=tuple(rows),
        available_scale_count=len(available_rows),
        signed_contrast=observations._signed_unit(signed),
        strength=strength,
        scale_consistency=scale_consistency,
        polarity_consistency=observations._unit(polarity_consistency),
        transition_local_y=transition,
        visibility=visibility,
        glare_conflict=glare,
        exclusion_conflict=exclusion,
    )


def _select_spatially_corroborated_textured_boundary(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    hypotheses: tuple[SemanticHypothesis, ...],
    *,
    accepted_foam_component_mask: np.ndarray | None,
    bounds: OilShadowBounds,
) -> SemanticHypothesis | None:
    """Recover weak scalar evidence only when current-frame Spatial adds proof.

    The ordinary relative-phase route remains authoritative when it can already
    form a typed boundary. This secondary route is narrower: it reuses the
    existing textured-boundary glare/collision safeguards, but replaces missing
    aggregate horizontal coverage with a four-sector coherent phase path.
    """

    ordered = sorted(hypotheses, key=observations._hypothesis_order)
    no_interface = observations._no_interface_evidence(
        pre,
        effective_mask,
        hypotheses,
    )
    if not no_interface.available or no_interface.likelihood > 0.40:
        return None

    for candidate in ordered:
        spatial_conflict = max(
            candidate.broad.glare_conflict,
            candidate.broad.exclusion_conflict,
            candidate.narrow.glare_overlap,
            candidate.narrow.exclusion_overlap,
            candidate.narrow.border_overlap,
        )
        if not (
            candidate.boundary_likelihood > candidate.artifact_likelihood
            and candidate.broad.available_scale_count == len(candidate.broad.scales)
            and candidate.broad.strength >= 0.12
            and candidate.broad.scale_consistency >= 0.60
            and candidate.broad.polarity_consistency >= 0.85
            and candidate.polarity_confidence >= 0.20
            and candidate.narrow.available
            and candidate.narrow.peak_strength >= 0.25
            and candidate.narrow.paired_edge_strength <= 0.80
            and candidate.visibility >= 0.85
            and candidate.evidence_availability >= 0.90
            and spatial_conflict <= 0.15
            and candidate.static_prior.contribution <= 0.08
        ):
            continue

        second_boundary = max(
            (
                item.boundary_likelihood
                for item in ordered
                if item.identity != candidate.identity
            ),
            default=0.0,
        )
        identifiability = observations._single_frame_identifiability_evidence(
            pre,
            effective_mask,
            candidate,
            no_interface,
            second_boundary,
        )
        if not (
            identifiability.texture_relief >= 0.55
            and identifiability.phase_ceiling_pressure <= 0.20
            and identifiability.collision_pressure <= 0.10
            and identifiability.evidence_reliability >= 0.75
        ):
            continue

        path = _evaluate_spatial_path(
            pre,
            effective_mask,
            candidate_local_y=candidate.representative_local_y,
            accepted_foam_component_mask=accepted_foam_component_mask,
            bounds=bounds,
        )
        path_alignment = (
            float("inf")
            if path.median_local_y is None
            else abs(path.median_local_y - candidate.representative_local_y)
        )
        if (
            path.accepted
            and path.sector_count >= _SECTOR_COUNT - 1
            and path.span_px <= 2.0 * bounds.maximum_proposal_diameter_px
            and path_alignment <= bounds.maximum_proposal_diameter_px
        ):
            return candidate
        # Do not search lower-ranked hypotheses after the first candidate that
        # passes the non-spatial safety gate. This keeps the fallback fail-closed
        # and bounds the added Spatial work to one five-sector path evaluation.
        return None
    return None


def _evaluate_spatial_path(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    *,
    candidate_local_y: float,
    accepted_foam_component_mask: np.ndarray | None,
    bounds: OilShadowBounds,
) -> _SpatialPathEvidence:
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    residual = (
        visible
        if accepted_foam_component_mask is None
        else visible & ~(accepted_foam_component_mask > 0)
    )
    columns = np.flatnonzero(np.any(effective, axis=0))
    center = float(candidate_local_y)
    depth = max(bounds.broad_band_scales)
    gap = max(2, int(round(bounds.maximum_proposal_diameter_px / 2.0)))
    height = effective.shape[0]
    if columns.size < _SECTOR_COUNT:
        return _rejected_path(center)
    if center < depth + gap or center >= height - depth - gap:
        return _rejected_path(center)

    edges = np.linspace(
        int(columns[0]),
        int(columns[-1]) + 1,
        _SECTOR_COUNT + 1,
        dtype=int,
    )
    records: list[tuple[int, int, int, bool, float]] = []
    for sector in range(_SECTOR_COUNT):
        value = _best_sector_phase(
            pre,
            visible,
            residual,
            center=center,
            first_column=int(edges[sector]),
            last_column=int(edges[sector + 1]),
            depth=depth,
            gap=gap,
            radius=bounds.narrow_lobe_search_radius_px,
        )
        if value is not None:
            row, sign, strong, strength = value
            records.append((sector, row, sign, strong, strength))

    best_run: list[tuple[int, int, int, bool, float]] = []
    for sign in (-1, 1):
        current: list[tuple[int, int, int, bool, float]] = []
        for record in records:
            sector, _row, record_sign, strong, _strength = record
            if record_sign == sign and strong:
                if current and sector != current[-1][0] + 1:
                    current = []
                current.append(record)
                if _path_run_key(current, center) < _path_run_key(best_run, center):
                    best_run = list(current)
            else:
                current = []

    if not best_run:
        return _rejected_path(center)
    path_rows = tuple(record[1] for record in best_run)
    span = max(path_rows) - min(path_rows)
    jumps = tuple(
        abs(path_rows[index + 1] - path_rows[index])
        for index in range(len(path_rows) - 1)
    )
    maximum_jump = max(jumps, default=0)
    path_median = float(np.median(path_rows))
    alignment = abs(path_median - center)
    minimum_sector_count = _SECTOR_COUNT // 2 + 1
    accepted = (
        len(best_run) >= minimum_sector_count
        # This is a fallback non-degeneracy check, not a physical rule about
        # Oil geometry. A valid flat surface may remain ambiguous here.
        and span > 1
        and maximum_jump <= 2.0 * bounds.maximum_proposal_diameter_px
        and alignment <= bounds.narrow_lobe_search_radius_px
    )
    return _SpatialPathEvidence(
        accepted=accepted,
        sector_count=len(best_run),
        rows=path_rows,
        span_px=int(span),
        maximum_jump_px=int(maximum_jump),
        median_local_y=path_median,
    )


def _best_sector_phase(
    pre: PreprocessResult,
    visible: np.ndarray,
    residual: np.ndarray,
    *,
    center: float,
    first_column: int,
    last_column: int,
    depth: int,
    gap: int,
    radius: int,
) -> tuple[int, int, bool, float] | None:
    height = visible.shape[0]
    quantization = observations._gray_quantization_step(pre.blurred)
    gray_scale = observations._gray_scale(pre.blurred)
    best = None
    for row in range(
        max(depth + gap, int(round(center)) - radius),
        min(height - depth - gap, int(round(center)) + radius + 1),
    ):
        top = observations._robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            range(row - gap - depth, row - gap),
            first_column,
            last_column,
        )
        bottom = observations._robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            range(row + gap, row + gap + depth),
            first_column,
            last_column,
        )
        if top is None or bottom is None:
            continue
        top_median, top_mad = top
        bottom_median, bottom_mad = bottom
        contrast = (top_median - bottom_median) / gray_scale
        noise = max(top_mad, bottom_mad, quantization) / gray_scale
        strength = abs(contrast) / max(noise, 1e-12)
        key = (-strength, abs(float(row) - center), row)
        if best is None or key < best[0]:
            sign = 1 if contrast > 0.0 else -1
            strong = (
                abs(contrast) > noise
                and abs(contrast) > quantization / gray_scale
            )
            best = (key, row, sign, strong, strength)
    if best is None:
        return None
    _key, row, sign, strong, strength = best
    return int(row), int(sign), bool(strong), float(strength)


def _path_run_key(
    records: list[tuple[int, int, int, bool, float]],
    center: float,
) -> tuple[float, float, float, float]:
    if not records:
        return (float("inf"),) * 4
    rows = tuple(record[1] for record in records)
    jumps = tuple(
        abs(rows[index + 1] - rows[index])
        for index in range(len(rows) - 1)
    )
    return (
        -float(len(records)),
        float(max(jumps, default=0)),
        abs(float(np.median(rows)) - center),
        float(records[0][0]),
    )


def _rejected_path(center: float) -> _SpatialPathEvidence:
    return _SpatialPathEvidence(
        accepted=False,
        sector_count=0,
        rows=(),
        span_px=0,
        maximum_jump_px=0,
        median_local_y=None,
    )
