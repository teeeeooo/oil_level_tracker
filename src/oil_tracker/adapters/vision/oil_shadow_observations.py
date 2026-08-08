from __future__ import annotations

from dataclasses import dataclass, replace
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


_ORDINARY_BOUNDARY_LIKELIHOOD_FLOOR = 0.48


@dataclass(frozen=True)
class _SingleFrameIdentifiabilityEvidence:
    phase_ceiling_pressure: float
    texture_relief: float
    broad_corroboration_deficit: float
    evidence_reliability: float
    collision_pressure: float
    semantic_support: float
    acceptance_margin: float


@dataclass(frozen=True)
class _PlateauEvidenceContext:
    first_row: int
    last_row: int
    window_height: int
    center_gap: int
    reference_width: int
    row_scores: np.ndarray

    def __post_init__(self) -> None:
        if self.row_scores.ndim != 1 or self.row_scores.flags.writeable:
            raise TypeError("Plateau row scores must be one-dimensional and read-only.")


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
    _height, width = effective.shape
    valid_support = effective.sum(axis=1).astype(np.float64) / max(1, width)
    visible_support = np.divide(
        visible.sum(axis=1).astype(np.float64),
        np.maximum(1, effective.sum(axis=1)),
    )
    observations: list[RawEdgeObservation] = []

    # Region/phase-transition evidence is the primary Y-proposal source.
    # Ordinary Sobel/Canny/Hough rows remain because retained controlled, Spatial,
    # and ambiguity safety anchors still require their competing evidence.
    energy = _normalize_profile(masked_row_mean(pre.sobel_y_abs, effective))
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

    return tuple(
        sorted(observations, key=lambda item: item.canonical_key)[
            : bounds.total_raw_observations
        ]
    )


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
    plateau_context = (
        _build_plateau_evidence_context(pre.gray, effective_mask)
        if proposals
        else None
    )
    hypotheses: list[SemanticHypothesis] = []
    for proposal in proposals:
        members = tuple(observation_by_id[item] for item in proposal.member_ids)
        broad = _broad_summary(proposal, broad_profiles, bounds)
        narrow = _narrow_summary(proposal, narrow_context, bounds)
        static_prior = _static_prior(narrow, broad, static_artifact_map, bounds)
        bright_plateau_artifact = _plateau_artifact_from_context(
            plateau_context,
            broad.transition_local_y,
        )
        hypothesis = _semantic_hypothesis(
            proposal,
            members,
            broad,
            narrow,
            static_prior,
            bright_plateau_artifact,
            crop_origin_y,
        )
        hypotheses.append(hypothesis)
    return semantic_deduplicate(tuple(hypotheses), bounds)


def semantic_deduplicate(
    hypotheses: tuple[SemanticHypothesis, ...] | list[SemanticHypothesis],
    bounds: OilShadowBounds,
) -> tuple[SemanticHypothesis, ...]:
    groups = _semantic_groups(hypotheses, bounds)
    merged = [_merge_hypothesis_group(group) for group in groups]
    merged.sort(key=_hypothesis_order)
    return tuple(merged[: bounds.semantic_hypotheses])


def _semantic_groups(
    hypotheses: tuple[SemanticHypothesis, ...] | list[SemanticHypothesis],
    bounds: OilShadowBounds,
) -> list[list[SemanticHypothesis]]:
    ordered = sorted(
        hypotheses,
        key=lambda item: (
            item.representative_local_y,
            item.label.value,
            item.identity,
        ),
    )
    groups: list[list[SemanticHypothesis]] = []
    for item in ordered:
        compatible_group = next(
            (group for group in groups if _can_join_semantic_group(item, group, bounds)),
            None,
        )
        if compatible_group is None:
            groups.append([item])
        else:
            compatible_group.append(item)
    return groups


def _can_join_semantic_group(
    item: SemanticHypothesis,
    group: list[SemanticHypothesis],
    bounds: OilShadowBounds,
) -> bool:
    minimum = min(value.minimum_local_y for value in group + [item])
    maximum = max(value.maximum_local_y for value in group + [item])
    if maximum - minimum > bounds.maximum_proposal_diameter_px + 1e-12:
        return False
    tolerance = min(2.0, bounds.maximum_proposal_diameter_px / 3.0)
    representative = float(median([value.representative_local_y for value in group]))
    if abs(item.representative_local_y - representative) > tolerance + 1e-12:
        return False
    return all(_semantically_compatible(item, prior) for prior in group)


def evaluate_typed_current_observation(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    hypotheses: tuple[SemanticHypothesis, ...],
    *,
    accepted_foam_front_local_y: float | None = None,
    accepted_foam_component_mask: np.ndarray | None = None,
    allow_comparative_recovery: bool = True,
) -> ShadowCurrentObservation:
    bounds = OilShadowBounds()
    _validate_accepted_foam_context(
        pre.gray,
        effective_mask,
        accepted_foam_front_local_y,
        accepted_foam_component_mask,
    )
    no_interface = _no_interface_evidence(pre, effective_mask, hypotheses)
    if not no_interface.available and no_interface.visibility < 0.20:
        return ShadowUnavailableObservation(
            visibility=no_interface.visibility,
            reason=no_interface.reason,
        )

    oil_evidence_mask = effective_mask
    if accepted_foam_component_mask is not None:
        oil_evidence_mask = np.where(
            accepted_foam_component_mask > 0,
            0,
            effective_mask,
        ).astype(effective_mask.dtype, copy=False)

    ordered = sorted(hypotheses, key=_hypothesis_order)
    best = ordered[0] if ordered else None
    competing_boundary = 0.0 if best is None else best.boundary_likelihood
    if _positive_no_interface_is_authoritative(no_interface, competing_boundary):
        return ShadowNoInterfaceObservation(evidence=no_interface)

    second_boundary = ordered[1].boundary_likelihood if len(ordered) > 1 else 0.0
    identifiability = None
    canonical_boundary_candidate = False
    if best is not None:
        boundary_margin = max(
            0.0,
            best.boundary_likelihood
            - max(best.artifact_likelihood, second_boundary),
        )
        standard_boundary = (
            best.boundary_likelihood >= _ORDINARY_BOUNDARY_LIKELIHOOD_FLOOR
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
        canonical_boundary_candidate = (
            standard_boundary or corroborated_single_boundary
        )
        identifiability = _single_frame_identifiability_evidence(
            pre,
            oil_evidence_mask,
            best,
            no_interface,
            second_boundary,
        )
        if (
            canonical_boundary_candidate
            and identifiability.acceptance_margin >= 0.0
            and (
                accepted_foam_front_local_y is None
                or best.representative_local_y > accepted_foam_front_local_y
            )
        ):
            return _boundary_observation(best, ordered)

    recovered = _select_textured_low_contrast_boundary(
        pre,
        oil_evidence_mask,
        ordered,
        no_interface,
        accepted_foam_front_local_y=accepted_foam_front_local_y,
    )
    if recovered is None and allow_comparative_recovery:
        recovered = _select_comparative_textured_boundary(
            pre,
            oil_evidence_mask,
            ordered,
            no_interface,
            bounds,
            accepted_foam_front_local_y=accepted_foam_front_local_y,
        )
    if (
        recovered is None
        and accepted_foam_front_local_y is not None
        and accepted_foam_component_mask is not None
    ):
        recovered = _select_foam_separated_boundary(
            pre,
            effective_mask,
            ordered,
            accepted_foam_front_local_y,
            accepted_foam_component_mask,
        )
    if recovered is not None:
        return _boundary_observation(recovered, ordered)

    reason = "competing_boundary_artifact_or_no_interface_evidence"
    if (
        canonical_boundary_candidate
        and identifiability is not None
        and identifiability.acceptance_margin < 0.0
    ):
        reason = "single_frame_boundary_identifiability_margin"
    elif best is not None and best.polarity_available is False:
        reason = "polarity_unavailable_or_conflicting"
    elif no_interface.glare_conflict >= 0.55:
        reason = "glare_visibility_conflict"
    ambiguity_likelihood = max(
        0.35,
        no_interface.glare_conflict,
        0.0 if best is None else best.ambiguity_likelihood,
    )
    projected_source_y = (
        best.representative_source_y
        if best is not None
        and math.isclose(
            ambiguity_likelihood,
            best.ambiguity_likelihood,
            rel_tol=0.0,
            abs_tol=1e-9,
        )
        else None
    )
    return ShadowAmbiguousObservation(
        hypothesis_ids=tuple(sorted(item.identity for item in ordered[:3])),
        boundary_likelihood=competing_boundary,
        artifact_likelihood=0.0 if best is None else best.artifact_likelihood,
        ambiguity_likelihood=ambiguity_likelihood,
        no_interface_likelihood=no_interface.likelihood,
        visibility=no_interface.visibility,
        projected_source_y=projected_source_y,
        reason=reason,
    )


def _validate_accepted_foam_context(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    accepted_foam_front_local_y: float | None,
    accepted_foam_component_mask: np.ndarray | None,
) -> None:
    _validate_same_shape(gray, effective_mask)
    frame_height = gray.shape[0]
    if accepted_foam_front_local_y is None:
        if accepted_foam_component_mask is not None:
            raise ValueError("Foam component context requires an accepted Foam front.")
        return
    if not math.isfinite(float(accepted_foam_front_local_y)):
        raise ValueError("Accepted Foam front must be finite.")
    if not 0.0 <= float(accepted_foam_front_local_y) <= max(0, frame_height - 1):
        raise ValueError("Accepted Foam front must stay inside the current raster.")
    if accepted_foam_component_mask is None:
        return
    if type(accepted_foam_component_mask) is not np.ndarray:
        raise TypeError("Accepted Foam component context must be a raster array.")
    _validate_same_shape(gray, accepted_foam_component_mask)


def _boundary_observation(
    selected: SemanticHypothesis,
    ordered: list[SemanticHypothesis],
) -> ShadowBoundaryObservation:
    alternatives = [item for item in ordered if item.identity != selected.identity][:2]
    return ShadowBoundaryObservation(
        hypothesis=selected,
        alternatives=tuple(sorted(item.identity for item in alternatives)),
    )


def _positive_no_interface_is_authoritative(
    evidence: ShadowNoInterfaceEvidence,
    competing_boundary: float,
) -> bool:
    """Return whether current-frame evidence affirmatively establishes absence."""

    return bool(
        evidence.available
        and evidence.likelihood >= 0.58
        and evidence.likelihood - competing_boundary >= 0.10
    )


def _has_hard_current_frame_support(
    candidate: SemanticHypothesis,
    accepted_foam_front_local_y: float | None = None,
) -> bool:
    """Retain only direct observability/topology invalidity as hard rejection."""

    if (
        accepted_foam_front_local_y is not None
        and candidate.representative_local_y <= accepted_foam_front_local_y
    ):
        return False
    spatial_conflict = max(
        candidate.broad.glare_conflict,
        candidate.broad.exclusion_conflict,
        candidate.narrow.glare_overlap,
        candidate.narrow.exclusion_overlap,
        candidate.narrow.border_overlap,
    )
    return bool(
        candidate.visibility >= 0.30
        and candidate.evidence_availability >= 0.30
        and spatial_conflict < 0.55
    )


def _comparative_authority_score(
    candidate: SemanticHypothesis,
    no_interface: ShadowNoInterfaceEvidence,
    *,
    corroboration: float,
) -> float:
    """Fuse soft semantic evidence once after independent corroboration."""

    positive = math.sqrt(
        max(0.0, candidate.boundary_likelihood * _unit(corroboration))
    )
    qualified_absence = _unit(
        no_interface.likelihood * no_interface.region_uniformity
        if no_interface.available
        else 0.0
    )
    artifact = _unit(candidate.artifact_likelihood)
    opposition = 1.0 - (1.0 - artifact) * (1.0 - qualified_absence)
    return float(positive - opposition)


def _borrows_structural_neighborhood(
    candidate: SemanticHypothesis,
    hard_safe: list[SemanticHypothesis],
    bounds: OilShadowBounds,
) -> bool:
    """Detect a weak tail borrowing texture from a stronger local structure.

    A subcanonical weak tail beside a stronger structural hypothesis must not
    borrow that structure's texture while discarding its artifact opposition.
    Candidates that already meet the ordinary ``0.48`` boundary floor retain
    their existing authority.  Below that floor, require the neighbour to keep
    at least twice the direct narrow response so ordinary sloped/curved material
    boundaries with nearby support remain eligible.  This is a fail-closed
    integrity check after comparative ranking; it never transfers authority to
    a different candidate.
    """

    if candidate.boundary_likelihood >= _ORDINARY_BOUNDARY_LIKELIHOOD_FLOOR:
        return False

    for item in hard_safe:
        if (
            item.identity != candidate.identity
            and abs(item.representative_local_y - candidate.representative_local_y)
            <= bounds.maximum_proposal_diameter_px + 1e-12
            and item.boundary_likelihood + 1e-12 >= candidate.boundary_likelihood
            and item.artifact_likelihood > candidate.artifact_likelihood + 1e-12
            and item.narrow.peak_strength + 1e-12
            >= candidate.narrow.peak_strength * 2.0
        ):
            return True
    return False


def _has_local_authority_tie(
    selected: SemanticHypothesis,
    assessments: list[tuple[float, SemanticHypothesis]],
    bounds: OilShadowBounds,
) -> bool:
    """Fail closed when locally equivalent hypotheses retain similar authority."""

    selected_score = next(
        score for score, candidate in assessments if candidate.identity == selected.identity
    )
    for score, candidate in assessments:
        if candidate.identity == selected.identity:
            continue
        if (
            abs(candidate.representative_local_y - selected.representative_local_y)
            <= bounds.maximum_proposal_diameter_px + 1e-12
            and selected_score - score < 0.08
        ):
            return True
    return False


def _select_comparative_textured_boundary(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ordered: list[SemanticHypothesis],
    no_interface: ShadowNoInterfaceEvidence,
    bounds: OilShadowBounds,
    *,
    accepted_foam_front_local_y: float | None = None,
) -> SemanticHypothesis | None:
    """Compare every hard-safe weak hypothesis using independent texture proof.

    Boundary/artifact/absence terms decide comparative authority once. Broad,
    coverage, polarity and pulse morphology remain inside those semantic
    likelihoods instead of reappearing as independent vetoes. Texture and the
    continuous collision evidence are independent current-frame corroboration.
    """

    hard_safe = [
        candidate
        for candidate in ordered
        if _has_hard_current_frame_support(
            candidate,
            accepted_foam_front_local_y,
        )
    ]
    if not hard_safe:
        return None
    semantic_anchor = hard_safe[0]
    assessments: list[tuple[float, SemanticHypothesis]] = []
    for candidate in hard_safe:
        if (
            abs(candidate.representative_local_y - semantic_anchor.representative_local_y)
            > bounds.maximum_proposal_diameter_px + 1e-12
        ):
            continue
        second_boundary = max(
            (
                item.boundary_likelihood
                for item in hard_safe
                if item.identity != candidate.identity
            ),
            default=0.0,
        )
        evidence = _single_frame_identifiability_evidence(
            pre,
            effective_mask,
            candidate,
            no_interface,
            second_boundary,
        )
        if not (
            evidence.texture_relief >= 0.55
            and evidence.phase_ceiling_pressure <= 0.20
            and evidence.collision_pressure <= 0.10
            and evidence.evidence_reliability >= 0.75
        ):
            continue
        corroboration = evidence.texture_relief * evidence.evidence_reliability
        score = _comparative_authority_score(
            candidate,
            no_interface,
            corroboration=corroboration,
        )
        if score > 0.0:
            assessments.append((score, candidate))

    if not assessments:
        return None
    assessments.sort(key=lambda item: (-item[0], _hypothesis_order(item[1])))
    selected = assessments[0][1]
    if _has_local_authority_tie(selected, assessments, bounds):
        return None
    if (
        accepted_foam_front_local_y is None
        and _borrows_structural_neighborhood(selected, hard_safe, bounds)
    ):
        return None
    return selected


def _select_textured_low_contrast_boundary(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ordered: list[SemanticHypothesis],
    no_interface: ShadowNoInterfaceEvidence,
    *,
    accepted_foam_front_local_y: float | None = None,
) -> SemanticHypothesis | None:
    """Retain the accepted D2 scalar safety envelope for Spatial internals."""

    for candidate in ordered:
        spatial_conflict = max(
            candidate.broad.glare_conflict,
            candidate.broad.exclusion_conflict,
            candidate.narrow.glare_overlap,
            candidate.narrow.exclusion_overlap,
            candidate.narrow.border_overlap,
        )
        if not (
            (
                accepted_foam_front_local_y is None
                or candidate.representative_local_y > accepted_foam_front_local_y
            )
            and candidate.boundary_likelihood > candidate.artifact_likelihood
            and candidate.broad.available_scale_count >= 2
            and candidate.broad.strength >= 0.12
            and candidate.broad.scale_consistency >= 0.80
            and candidate.narrow.available
            and candidate.narrow.peak_strength >= 0.25
            and candidate.narrow.horizontal_coverage >= 0.40
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
        evidence = _single_frame_identifiability_evidence(
            pre,
            effective_mask,
            candidate,
            no_interface,
            second_boundary,
        )
        if (
            evidence.texture_relief >= 0.55
            and evidence.phase_ceiling_pressure <= 0.20
            and evidence.collision_pressure <= 0.10
            and evidence.evidence_reliability >= 0.75
        ):
            return candidate
    return None


def _select_foam_separated_boundary(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    ordered: list[SemanticHypothesis],
    accepted_foam_front_local_y: float,
    accepted_foam_component_mask: np.ndarray,
) -> SemanticHypothesis | None:
    """Recover Oil only when a separate phase persists outside local structure.

    Accepted S5-A Foam supplies only current-frame context.  The Foam component
    and glare are removed before testing three independent horizontal sectors.
    A recoverable Oil phase must repeat the same outer-plateau ordering in a
    majority of those sectors, with at least one sector exceeding its own
    robust within-plateau noise.  Local pulse geometry is excluded using the
    already-owned S5-B broad/pair/proposal scales rather than a new intensity
    threshold.
    """

    for candidate in ordered:
        spatial_conflict = max(
            candidate.broad.glare_conflict,
            candidate.broad.exclusion_conflict,
            candidate.narrow.glare_overlap,
            candidate.narrow.exclusion_overlap,
            candidate.narrow.border_overlap,
        )
        if not (
            candidate.representative_local_y > accepted_foam_front_local_y
            and candidate.boundary_likelihood >= 0.20
            and candidate.broad.available_scale_count >= 2
            and candidate.broad.strength >= 0.10
            and candidate.broad.scale_consistency >= 0.80
            and candidate.narrow.available
            and candidate.narrow.peak_strength >= 0.20
            and candidate.narrow.horizontal_coverage >= 0.20
            and candidate.visibility >= 0.85
            and candidate.evidence_availability >= 0.90
            and spatial_conflict <= 0.15
            and candidate.static_prior.contribution <= 0.08
        ):
            continue
        if _has_foam_separated_phase_support(
            pre,
            effective_mask,
            accepted_foam_component_mask,
            candidate,
        ):
            return candidate
    return None


def _has_foam_separated_phase_support(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    accepted_foam_component_mask: np.ndarray,
    candidate: SemanticHypothesis,
) -> bool:
    """Require repeatable outer phase evidence after Foam/local-pulse removal."""

    _validate_same_shape(pre.blurred, effective_mask, accepted_foam_component_mask)
    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    residual = visible & ~(accepted_foam_component_mask > 0)
    columns = np.flatnonzero(np.any(effective, axis=0))
    if columns.size < 3:
        return False

    broad_scale = max((item.band_scale for item in candidate.broad.scales), default=0)
    if broad_scale <= 0:
        return False
    local_gap = max(
        broad_scale,
        int(math.ceil(candidate.narrow.paired_edge_separation_px)),
        int(math.ceil(candidate.maximum_local_y - candidate.minimum_local_y)),
    )
    depth = 2 * broad_scale
    center = min(
        effective.shape[0] - 1,
        max(0, int(round(candidate.representative_local_y))),
    )
    top_rows = range(max(0, center - local_gap - depth), max(0, center - local_gap))
    bottom_rows = range(
        min(effective.shape[0], center + local_gap),
        min(effective.shape[0], center + local_gap + depth),
    )
    if not top_rows or not bottom_rows:
        return False

    left = int(columns[0])
    right = int(columns[-1]) + 1
    edges = np.linspace(left, right, 4, dtype=int)
    gray_scale = _gray_scale(pre.blurred)
    quantization = _gray_quantization_step(pre.blurred) / gray_scale
    directional: list[tuple[int, bool]] = []
    for index in range(3):
        top = _robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            top_rows,
            int(edges[index]),
            int(edges[index + 1]),
        )
        bottom = _robust_sector_phase(
            pre.blurred,
            visible,
            residual,
            bottom_rows,
            int(edges[index]),
            int(edges[index + 1]),
        )
        if top is None or bottom is None:
            continue
        top_median, top_mad = top
        bottom_median, bottom_mad = bottom
        contrast = (top_median - bottom_median) / gray_scale
        noise = max(top_mad, bottom_mad, _gray_quantization_step(pre.blurred)) / gray_scale
        if abs(contrast) <= quantization:
            continue
        directional.append((1 if contrast > 0.0 else -1, abs(contrast) > noise))

    for direction in (-1, 1):
        matching = [strong for sign, strong in directional if sign == direction]
        if len(matching) >= 2 and any(matching):
            return True
    return False


def _robust_sector_phase(
    image: np.ndarray,
    reference_mask: np.ndarray,
    residual_mask: np.ndarray,
    rows: range,
    first_column: int,
    last_column: int,
) -> tuple[float, float] | None:
    """Return median/MAD only when every visible sector row retains samples."""

    chunks: list[np.ndarray] = []
    for row in rows:
        reference = reference_mask[row, first_column:last_column]
        if not np.any(reference):
            continue
        selected = residual_mask[row, first_column:last_column]
        if not np.any(selected):
            return None
        chunks.append(image[row, first_column:last_column][selected].astype(np.float64))
    if not chunks:
        return None
    values = np.concatenate(chunks)
    center = float(np.median(values))
    mad = float(np.median(np.abs(values - center)))
    return center, mad


def _gray_quantization_step(image: np.ndarray) -> float:
    if np.issubdtype(image.dtype, np.integer):
        return 1.0
    if np.issubdtype(image.dtype, np.floating):
        return max(1.0, _gray_scale(image)) * float(np.finfo(image.dtype).eps)
    return 1.0


def _single_frame_identifiability_evidence(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    best: SemanticHypothesis,
    no_interface: ShadowNoInterfaceEvidence,
    second_boundary: float,
) -> _SingleFrameIdentifiabilityEvidence:
    """Combine current-frame semantic and photometric evidence into one margin."""

    effective = effective_mask > 0
    center = min(
        effective.shape[0] - 1,
        max(0, int(round(best.broad.transition_local_y))),
    )
    depth = max((item.band_scale for item in best.broad.scales), default=3)
    gap = 2
    side_ranges = (
        range(max(0, center - gap - depth), max(0, center - gap)),
        range(
            min(effective.shape[0], center + gap),
            min(effective.shape[0], center + gap + depth),
        ),
    )
    gray_scale = _gray_scale(pre.gray)
    side_evidence: list[tuple[float, float, float, float]] = []
    for rows in side_ranges:
        values = [
            pre.gray[row][effective[row]]
            for row in rows
            if np.any(effective[row])
        ]
        if not values:
            continue
        samples = np.concatenate(values).astype(np.float64)
        normalized = np.clip(samples / gray_scale, 0.0, 1.0)
        phase_ceiling_pressure = _smoothstep_mean(
            (normalized - 0.88) / 0.10
        )
        spread = float(np.std(samples)) / gray_scale
        lower_tail_asymmetry = _unit(
            (float(np.median(samples)) - float(np.mean(samples)))
            / max(float(np.std(samples)), 1e-12)
        )
        texture_relief = (
            _smoothstep(spread / 0.018)
            * _smoothstep(lower_tail_asymmetry / 0.25)
        )
        sample_confidence = samples.size / (samples.size + 20.0)
        photometric_collision = phase_ceiling_pressure * (
            1.0 - 0.90 * texture_relief
        )
        side_evidence.append(
            (
                photometric_collision,
                phase_ceiling_pressure,
                texture_relief,
                sample_confidence,
            )
        )

    if side_evidence:
        (
            photometric_collision,
            phase_ceiling_pressure,
            texture_relief,
            sample_confidence,
        ) = max(side_evidence, key=lambda item: item[0])
    else:
        photometric_collision = 0.0
        phase_ceiling_pressure = 0.0
        texture_relief = 0.0
        sample_confidence = 0.0

    broad_corroboration_deficit = _smoothstep(
        (0.46 - best.broad.strength) / 0.18
    )
    scale_fraction = best.broad.available_scale_count / max(
        1,
        len(best.broad.scales),
    )
    side_availability = len(side_evidence) / 2.0
    observable_reliability = (
        best.narrow.horizontal_coverage
        + best.evidence_availability
        + best.visibility
        + scale_fraction
        + no_interface.visibility
    ) / 5.0
    sampling_reliability = math.sqrt(
        max(0.0, side_availability * sample_confidence)
    )
    evidence_reliability = _unit(
        observable_reliability * sampling_reliability
    )
    collision_pressure = _unit(
        photometric_collision
        * (0.40 + 0.60 * broad_corroboration_deficit)
        * (1.15 - 0.15 * evidence_reliability)
    )

    boundary_support = _smoothstep(
        (best.boundary_likelihood - 0.40) / 0.14
    )
    artifact_dominance = _smoothstep(
        max(0.0, best.boundary_likelihood - best.artifact_likelihood) / 0.35
    )
    canonical_dominance = _smoothstep(
        max(
            0.0,
            best.boundary_likelihood
            - max(
                best.artifact_likelihood,
                no_interface.likelihood,
                second_boundary,
            ),
        )
        / 0.20
    )
    dominance_support = max(artifact_dominance, canonical_dominance)
    ambiguity_clearance = _smoothstep(
        (0.72 - best.ambiguity_likelihood) / 0.30
    )
    semantic_support = _unit(
        (
            0.50 * boundary_support
            + 0.30 * dominance_support
            + 0.20 * ambiguity_clearance
        )
        * (0.70 + 0.30 * evidence_reliability)
    )
    canonical_normalization = 0.39 + 0.01 * evidence_reliability
    acceptance_margin = (
        semantic_support - canonical_normalization - 1.10 * collision_pressure
    )
    return _SingleFrameIdentifiabilityEvidence(
        phase_ceiling_pressure=_unit(phase_ceiling_pressure),
        texture_relief=_unit(texture_relief),
        broad_corroboration_deficit=_unit(broad_corroboration_deficit),
        evidence_reliability=_unit(evidence_reliability),
        collision_pressure=_unit(collision_pressure),
        semantic_support=_unit(semantic_support),
        acceptance_margin=float(acceptance_margin),
    )


def _gray_scale(gray: np.ndarray) -> float:
    if np.issubdtype(gray.dtype, np.integer):
        return float(np.iinfo(gray.dtype).max)
    finite = np.asarray(gray, dtype=np.float64)
    finite = finite[np.isfinite(finite)]
    return max(1.0, float(np.max(np.abs(finite))) if finite.size else 1.0)


def _smoothstep(value: float) -> float:
    bounded = _unit(value)
    return bounded * bounded * (3.0 - 2.0 * bounded)


def _smoothstep_mean(values: np.ndarray) -> float:
    bounded = np.clip(np.asarray(values, dtype=np.float64), 0.0, 1.0)
    smooth = bounded * bounded * (3.0 - 2.0 * bounded)
    return 0.0 if smooth.size == 0 else float(np.mean(smooth))


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


def _persistent_plateau_artifact(
    gray: np.ndarray,
    effective_mask: np.ndarray,
    center_y: float,
) -> float:
    """Measure plateau evidence through one immutable per-frame context."""

    return _plateau_artifact_from_context(
        _build_plateau_evidence_context(gray, effective_mask),
        center_y,
    )


def _build_plateau_evidence_context(
    gray: np.ndarray,
    effective_mask: np.ndarray,
) -> _PlateauEvidenceContext | None:
    _validate_same_shape(gray, effective_mask)
    effective = effective_mask > 0
    row_widths = np.count_nonzero(effective, axis=1)
    valid_rows = np.flatnonzero(row_widths > 0)
    if valid_rows.size == 0:
        return None

    first_row = int(valid_rows[0])
    last_row = int(valid_rows[-1])
    roi_height = last_row - first_row + 1
    reference_width = int(np.max(row_widths[valid_rows]))
    row_scores = np.zeros(effective.shape[0], dtype=np.float64)
    if reference_width >= 4:
        minimum_run = max(3, int(math.ceil(0.25 * reference_width)))
        run_cache: dict[bytes, tuple[int, int]] = {}
        support_cache: dict[tuple[str, int, bytes], float] = {}
        for row in range(first_row, last_row + 1):
            mask_key = effective[row].tobytes()
            if mask_key not in run_cache:
                run_cache[mask_key] = _longest_contiguous_run(effective[row])
            start, stop = run_cache[mask_key]
            run_size = stop - start
            if run_size < minimum_run:
                continue
            values = gray[row, start:stop]
            cache_key = (values.dtype.str, run_size, values.tobytes())
            if cache_key not in support_cache:
                support_cache[cache_key] = _row_plateau_support(values)
            row_scores[row] = support_cache[cache_key] * (
                run_size / reference_width
            )
    row_scores.setflags(write=False)
    return _PlateauEvidenceContext(
        first_row=first_row,
        last_row=last_row,
        window_height=max(3, int(round(0.45 * roi_height))),
        center_gap=max(1, int(round(0.015 * roi_height))),
        reference_width=reference_width,
        row_scores=row_scores,
    )


def _plateau_artifact_from_context(
    context: _PlateauEvidenceContext | None,
    center_y: float,
) -> float:
    if context is None or context.reference_width < 4:
        return 0.0
    center = min(
        context.last_row,
        max(context.first_row, int(round(center_y))),
    )
    side_scores = []
    for start, stop in (
        (
            max(
                context.first_row,
                center - context.center_gap - context.window_height,
            ),
            max(context.first_row, center - context.center_gap),
        ),
        (
            min(context.last_row + 1, center + context.center_gap),
            min(
                context.last_row + 1,
                center + context.center_gap + context.window_height,
            ),
        ),
    ):
        side_scores.append(
            0.0
            if stop <= start
            else float(np.mean(context.row_scores[start:stop]))
        )
    return _unit(max(side_scores, default=0.0))


def _longest_contiguous_run(row_mask: np.ndarray) -> tuple[int, int]:
    columns = np.flatnonzero(row_mask)
    if columns.size == 0:
        return 0, 0
    gaps = np.flatnonzero(np.diff(columns) > 1)
    if gaps.size == 0:
        return int(columns[0]), int(columns[-1]) + 1
    starts = np.concatenate((columns[:1], columns[gaps + 1]))
    stops = np.concatenate((columns[gaps] + 1, columns[-1:] + 1))
    index = int(np.argmax(stops - starts))
    return int(starts[index]), int(stops[index])


def _row_plateau_support(values: np.ndarray) -> float:
    row = values.astype(np.float64)
    if row.size < 5:
        return 0.0
    differences = np.diff(row)
    magnitudes = np.abs(differences)
    total_variation = float(np.sum(magnitudes))
    if total_variation <= 1e-12:
        return 0.0

    edge_indices = np.argsort(magnitudes)[-min(6, magnitudes.size) :]
    prefix = np.concatenate(
        (np.zeros(1, dtype=np.float64), np.cumsum(row, dtype=np.float64))
    )
    row_size = int(row.size)
    prefix_means = {
        int(edge) + 1: float(prefix[int(edge) + 1] / (int(edge) + 1))
        for edge in edge_indices
    }
    suffix_means = {
        int(edge) + 1: float(
            (prefix[row_size] - prefix[int(edge) + 1])
            / (row_size - int(edge) - 1)
        )
        for edge in edge_indices
    }

    localized = 0.0
    for edge_index in edge_indices:
        split = int(edge_index) + 1
        localized = max(
            localized,
            _localized_component_support(
                abs(prefix_means[split] - suffix_means[split]),
                float(magnitudes[edge_index]),
                float(magnitudes[edge_index]) / total_variation,
            ),
        )

    for left_index, first_edge in enumerate(edge_indices):
        for second_edge in edge_indices[left_index + 1 :]:
            left, right = sorted((int(first_edge), int(second_edge)))
            if differences[left] * differences[right] >= 0.0:
                continue
            center_mean = float(
                (prefix[right + 1] - prefix[left + 1]) / (right - left)
            )
            left_delta = center_mean - prefix_means[left + 1]
            right_delta = center_mean - suffix_means[right + 1]
            if left_delta * right_delta <= 0.0:
                continue
            localized = max(
                localized,
                _localized_component_support(
                    min(abs(left_delta), abs(right_delta)),
                    min(float(magnitudes[left]), float(magnitudes[right])),
                    (float(magnitudes[left]) + float(magnitudes[right]))
                    / total_variation,
                ),
            )

    strongest_two = float(
        np.sum(np.sort(magnitudes)[-min(2, magnitudes.size) :])
    )
    distributed_fraction = max(0.0, 1.0 - strongest_two / total_variation)
    mean_variation = total_variation / max(1, row.size - 1)
    fine_texture = (
        min(1.0, (mean_variation / 4.5) ** 6)
        * distributed_fraction
    )
    return _unit(max(localized, fine_texture))


def _localized_component_support(
    contrast: float,
    edge_strength: float,
    edge_dominance: float,
) -> float:
    contrast_support = _unit(contrast / 64.0)
    edge_support = _unit(edge_strength / 64.0)
    return _unit(
        1.6
        * contrast_support**2
        * edge_support**2
        * _unit(edge_dominance)
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
    bright_plateau_artifact: float,
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
        + bright_plateau_artifact
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
    raw_values = pre.gray[visible].astype(np.float32)
    normalized_values = pre.normalized[visible].astype(np.float32)
    mean_intensity = float(np.median(raw_values))
    texture = float(np.std(raw_values))
    uniformity = _unit(1.0 - float(np.std(normalized_values)) / 58.0)
    row_energy = _normalize_profile(masked_row_mean(pre.sobel_y_abs, visible))
    raster_weakness = _unit(1.0 - float(np.max(row_energy)))
    competing = max((item.boundary_likelihood for item in hypotheses), default=0.0)
    weak_boundary = _unit(0.58 * (1.0 - competing) + 0.42 * raster_weakness)
    full = _unit((145.0 - mean_intensity) / 55.0) * uniformity
    empty = _unit((mean_intensity - 115.0) / 70.0) * uniformity
    likelihood = _unit(
        0.36 * weak_boundary
        + 0.44 * uniformity
        + 0.20 * visibility
        - 0.30 * glare_conflict
        - 0.38 * competing
    )
    if competing >= 0.72:
        reason = "strong_competing_boundary"
    elif glare_conflict >= 0.45:
        reason = "glare_visibility_conflict"
    elif likelihood >= 0.58 and uniformity >= 0.65:
        reason = "positive_exposure_decoupled_absence_evidence"
    else:
        reason = "mixed_exposure_decoupled_absence_evidence"
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
