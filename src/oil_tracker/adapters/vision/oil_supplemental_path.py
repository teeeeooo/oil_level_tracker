from __future__ import annotations

import math

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

from .preprocessing import PreprocessResult
from .row_features import masked_row_mean, row_coverage


def generate_calibrated_high_recall_candidates(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
    limit: int = 8,
) -> tuple[BoundaryCandidate, ...]:
    """Expose weak distributed rows after explicit negative calibration.

    This lane is called only when the operator has saved artifact templates.
    It deliberately retains more weak rows than the ordinary detector, while
    preserving the same hard visibility/optics boundary. Templates are applied
    to the returned spatial signatures before sequence resolution, so excluded
    structures cannot consume the useful calibrated budget.
    """

    if pre.sobel_y_abs.shape != effective_mask.shape:
        raise ValueError("Calibrated Sobel inputs must share one raster shape.")
    if (
        static_artifact_map is not None
        and static_artifact_map.shape != effective_mask.shape
    ):
        raise ValueError("Calibrated Sobel static map must match the Oil raster.")
    if limit < 1:
        return ()

    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    height, width = effective.shape
    if height < 32 or width < 12 or np.count_nonzero(visible) < 32:
        return ()

    energy = masked_row_mean(pre.sobel_y_abs, visible)
    maximum = float(np.max(energy)) if energy.size else 0.0
    if maximum <= 0.0:
        return ()
    response = np.clip(energy / maximum, 0.0, 1.0)
    signed = masked_row_mean(pre.sobel_y_signed, visible)
    canny_coverage = row_coverage(pre.horizontal_mask, visible)
    support = np.count_nonzero(visible, axis=1).astype(np.float32) / max(1, width)
    distributed = _distributed_band_support(pre.sobel_y_abs, visible)
    combined = np.clip(
        0.46 * response
        + 0.27 * distributed
        + 0.17 * canny_coverage
        + 0.10 * support,
        0.0,
        1.0,
    )
    # Mask coverage contributes at most 0.10 by itself; keep the floor above
    # that value so a completely flat visible row is never proposed.
    rows = _bounded_peak_rows(combined, max(limit * 4, 24), minimum=0.14)
    ranked = sorted(rows, key=lambda row: (-float(combined[row]), row))
    eligible: list[int] = []
    for row in ranked:
        if support[row] < 0.25:
            continue
        optics = _band_overlap(pre.glare_mask, effective, row, radius=2)
        if optics >= 0.55:
            continue
        eligible.append(row)

    selected: list[int] = []
    primary_count = max(1, limit // 2)
    for row in eligible:
        if any(abs(row - existing) <= 5 for existing in selected):
            continue
        selected.append(row)
        if len(selected) >= primary_count:
            break

    # Reserve the remaining fixed budget for vertical coverage. Strong rim or
    # texture rows often cluster in one part of the ellipse; pure score order
    # removed every weaker Oil row from other bands in the R9 Windows Base
    # replay. This does not lower the proposal floor or expand the total budget.
    reserve = max(0, limit - len(selected))
    for band in range(reserve):
        first = int(round(height * band / max(1, reserve)))
        last = int(round(height * (band + 1) / max(1, reserve)))
        choice = next(
            (
                row
                for row in eligible
                if first <= row < last
                and all(abs(row - existing) > 5 for existing in selected)
            ),
            None,
        )
        if choice is not None:
            selected.append(choice)

    for row in eligible:
        if len(selected) >= limit:
            break
        if all(abs(row - existing) > 5 for existing in selected):
            selected.append(row)

    output = []
    primary_rows = set(selected[:primary_count])
    for row in selected:
        strength = _unit(float(response[row]))
        horizontal = _unit(float(max(canny_coverage[row], distributed[row])))
        availability = _unit(float(support[row]))
        polarity = _unit(abs(float(signed[row])) / 80.0)
        static = _band_overlap(static_artifact_map, effective, row, radius=2)
        optics = _band_overlap(pre.glare_mask, effective, row, radius=2)
        boundary = _unit(
            0.42 * strength
            + 0.28 * horizontal
            + 0.14 * polarity
            + 0.16 * availability
        )
        artifact = _unit(0.65 * optics + 0.35 * static)
        ambiguity = _unit(
            0.42 * (1.0 - strength)
            + 0.26 * (1.0 - horizontal)
            + 0.20 * artifact
            + 0.12 * (1.0 - polarity)
        )
        source_y = float(crop_origin_y + row)
        output.append(
            BoundaryCandidate(
                source="calibrated_high_recall",
                kind=BoundaryKind.OIL_AIR,
                y=source_y,
                features={
                    "supplemental_path": 1.0,
                    "calibrated_high_recall": 1.0,
                    "vertical_reserve": float(
                        row not in primary_rows
                    ),
                    "local_y": float(row),
                    "source_y": source_y,
                    "boundary_likelihood": boundary,
                    "artifact_likelihood": artifact,
                    "ambiguity_likelihood": ambiguity,
                    "evidence_availability": availability,
                    "visibility": _unit(1.0 - optics),
                    "broad_strength": strength,
                    "narrow_peak_strength": strength,
                    "narrow_horizontal_coverage": horizontal,
                    "broad_scale_consistency": horizontal,
                    "polarity_confidence": polarity,
                    "static_prior_contribution": static,
                    "sequence_eligible": 1.0,
                },
                penalties={
                    "artifact_likelihood": artifact,
                    "ambiguity_likelihood": ambiguity,
                    "static_prior_contribution": static,
                    "static_artifact_penalty": static,
                    "glare_conflict": optics,
                    "optics_conflict": optics,
                    "exclusion_conflict": 0.0,
                    "border_penalty": 0.0,
                },
                feature_score=boundary,
                penalty=_unit(artifact + ambiguity),
                final_score=boundary,
                selected=False,
                rejected=False,
            )
        )
    return tuple(output)


def generate_phase_transition_candidates(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
    limit: int = 4,
) -> tuple[BoundaryCandidate, ...]:
    """Propose diffuse cross-row phase transitions without a local-peak gate.

    Each proposal must be distributed across horizontal sectors and survive at
    multiple vertical scales.  Selection is band-bounded and candidate-only;
    sequence authority is decided later from the shared phase identity.
    """

    if pre.normalized.shape != effective_mask.shape:
        raise ValueError("Phase-transition inputs must share one raster shape.")
    if (
        static_artifact_map is not None
        and static_artifact_map.shape != effective_mask.shape
    ):
        raise ValueError("Phase-transition static map must match the Oil raster.")
    if limit < 1:
        return ()

    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    height, width = effective.shape
    if height < 48 or width < 20 or np.count_nonzero(visible) < 64:
        return ()

    response, horizontal, scale_consistency, signed = _phase_transition_profile(
        pre.normalized,
        visible,
    )
    support = np.count_nonzero(visible, axis=1).astype(np.float32) / max(1, width)
    eligible = [
        row
        for row in range(12, height - 12)
        if response[row] >= 0.10
        and horizontal[row] >= 0.60
        and scale_consistency[row] >= 0.34
        and support[row] >= 0.25
        and _band_overlap(pre.glare_mask, effective, row, radius=3) < 0.55
    ]
    if not eligible:
        return ()

    selected: list[int] = []
    band_count = max(1, min(limit, 6))
    for band in range(band_count):
        first = int(round(height * band / band_count))
        last = int(round(height * (band + 1) / band_count))
        choices = [row for row in eligible if first <= row < last]
        if not choices:
            continue
        row = max(
            choices,
            key=lambda item: (
                float(response[item] + 0.12 * scale_consistency[item]),
                -item,
            ),
        )
        if all(abs(row - existing) > 8 for existing in selected):
            selected.append(row)

    for row in sorted(
        eligible,
        key=lambda item: (
            -float(response[item] + 0.12 * scale_consistency[item]),
            item,
        ),
    ):
        if len(selected) >= limit:
            break
        if all(abs(row - existing) > 8 for existing in selected):
            selected.append(row)

    output: list[BoundaryCandidate] = []
    for row in sorted(selected):
        strength = _unit(float(response[row]))
        coverage = _unit(float(horizontal[row]))
        consistency = _unit(float(scale_consistency[row]))
        availability = _unit(float(support[row]))
        polarity = _unit(abs(float(signed[row])))
        static = _band_overlap(static_artifact_map, effective, row, radius=3)
        optics = _band_overlap(pre.glare_mask, effective, row, radius=3)
        boundary = _unit(
            0.42 * strength
            + 0.24 * coverage
            + 0.18 * consistency
            + 0.16 * availability
        )
        artifact = _unit(0.65 * optics + 0.35 * static)
        ambiguity = _unit(
            0.40 * (1.0 - strength)
            + 0.24 * (1.0 - coverage)
            + 0.20 * (1.0 - consistency)
            + 0.16 * artifact
        )
        source_y = float(crop_origin_y + row)
        output.append(
            BoundaryCandidate(
                source="phase_transition_scan",
                kind=BoundaryKind.OIL_AIR,
                y=source_y,
                features={
                    "supplemental_path": 1.0,
                    "calibrated_high_recall": 1.0,
                    "phase_transition_scan": 1.0,
                    "local_y": float(row),
                    "source_y": source_y,
                    "boundary_likelihood": boundary,
                    "artifact_likelihood": artifact,
                    "ambiguity_likelihood": ambiguity,
                    "evidence_availability": availability,
                    "visibility": _unit(1.0 - optics),
                    "broad_strength": strength,
                    "narrow_peak_strength": strength,
                    "narrow_horizontal_coverage": coverage,
                    "broad_scale_consistency": consistency,
                    "polarity_confidence": polarity,
                    "static_prior_contribution": static,
                    "sequence_eligible": 1.0,
                },
                penalties={
                    "artifact_likelihood": artifact,
                    "ambiguity_likelihood": ambiguity,
                    "static_prior_contribution": static,
                    "static_artifact_penalty": static,
                    "glare_conflict": optics,
                    "optics_conflict": optics,
                    "exclusion_conflict": 0.0,
                    "border_penalty": 0.0,
                },
                feature_score=boundary,
                penalty=_unit(artifact + ambiguity),
                final_score=boundary,
                selected=False,
                rejected=False,
            )
        )
    return tuple(output)


def _phase_transition_profile(
    gray: np.ndarray,
    visible: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    height, width = gray.shape
    sector_edges = np.linspace(0, width, 6, dtype=int)
    scale_responses: list[np.ndarray] = []
    scale_signs: list[np.ndarray] = []
    scale_coverages: list[np.ndarray] = []
    values = gray.astype(np.float32, copy=False)
    for radius in (3, 6, 10):
        response = np.zeros(height, dtype=np.float32)
        signs = np.zeros(height, dtype=np.float32)
        coverage = np.zeros(height, dtype=np.float32)
        for row in range(radius, height - radius):
            sector_values: list[float] = []
            sector_signs: list[float] = []
            for first, last in zip(sector_edges[:-1], sector_edges[1:], strict=True):
                upper_visible = visible[row - radius : row, first:last]
                lower_visible = visible[row + 1 : row + radius + 1, first:last]
                minimum_pixels = max(2, int(radius * max(1, last - first) * 0.25))
                if (
                    np.count_nonzero(upper_visible) < minimum_pixels
                    or np.count_nonzero(lower_visible) < minimum_pixels
                ):
                    continue
                upper = float(
                    np.mean(values[row - radius : row, first:last][upper_visible])
                )
                lower = float(
                    np.mean(values[row + 1 : row + radius + 1, first:last][lower_visible])
                )
                difference = lower - upper
                sector_values.append(abs(difference) / 48.0)
                sector_signs.append(difference / 48.0)
            if len(sector_values) < 3:
                continue
            response[row] = _unit(float(np.median(sector_values)))
            signs[row] = float(np.median(sector_signs))
            coverage[row] = len(sector_values) / 5.0
        scale_responses.append(response)
        scale_signs.append(signs)
        scale_coverages.append(coverage)

    stacked = np.stack(scale_responses)
    strongest = np.max(stacked, axis=0)
    consistency = np.mean(
        stacked >= np.maximum(0.08, strongest * 0.60),
        axis=0,
    ).astype(np.float32)
    best_scale = np.argmax(stacked, axis=0)
    signs = np.take_along_axis(
        np.stack(scale_signs),
        best_scale.reshape(1, -1),
        axis=0,
    ).reshape(-1)
    coverage = np.take_along_axis(
        np.stack(scale_coverages),
        best_scale.reshape(1, -1),
        axis=0,
    ).reshape(-1)
    return strongest, coverage, consistency, signs


def _distributed_band_support(
    sobel: np.ndarray,
    visible: np.ndarray,
) -> np.ndarray:
    values = sobel.astype(np.float32, copy=False)
    visible_values = values[visible]
    if not visible_values.size:
        return np.zeros(values.shape[0], dtype=np.float32)
    threshold = max(4.0, float(np.percentile(visible_values, 65.0)))
    supported = visible & (values >= threshold)
    counts = np.count_nonzero(visible, axis=1)
    return np.divide(
        np.count_nonzero(supported, axis=1).astype(np.float32),
        np.maximum(1, counts),
    ).astype(np.float32)


def generate_distributed_sobel_candidates(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
) -> tuple[BoundaryCandidate, ...]:
    """Retain one broad weak ridge hidden behind stronger global Sobel rows.

    This is the bounded S11-D2 representation mechanism adapted as an additive
    R8 candidate lane.  It keeps the established Sobel floor, never changes the
    ordinary proposal budget and cannot become an Oil anchor without another
    representation or registered Oil motion.
    """

    if pre.sobel_y_abs.shape != effective_mask.shape:
        raise ValueError("Distributed Sobel inputs must share one raster shape.")
    if (
        static_artifact_map is not None
        and static_artifact_map.shape != effective_mask.shape
    ):
        raise ValueError("Distributed Sobel static map must match the Oil raster.")

    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    height, width = effective.shape
    if height < 48 or width < 12 or np.count_nonzero(effective) < 32:
        return ()

    energy = masked_row_mean(pre.sobel_y_abs, effective)
    maximum = float(np.max(energy)) if energy.size else 0.0
    if maximum <= 0.0:
        return ()
    response = np.clip(energy / maximum, 0.0, 1.0)
    signed = masked_row_mean(pre.sobel_y_signed, effective)
    coverage = row_coverage(pre.horizontal_mask, effective)
    valid_support = np.count_nonzero(effective, axis=1).astype(np.float32) / max(1, width)
    visible_support = np.divide(
        np.count_nonzero(visible, axis=1).astype(np.float32),
        np.maximum(1, np.count_nonzero(effective, axis=1)),
    )

    scale = 10
    primary = _bounded_peak_rows(response, 6, minimum=0.08)
    all_rows = sorted(_bounded_peak_rows(response, 48, minimum=0.08))
    secondary = [
        row
        for row in all_rows
        if all(abs(row - primary_row) > scale for primary_row in primary)
    ]
    group = _best_distributed_group(secondary, response, scale=scale)
    if group is None:
        return ()

    first, last = group[0], group[-1]
    center = 0.5 * (first + last)
    row = min(group, key=lambda item: (abs(item - center), -float(response[item]), item))
    mean_strength = float(np.mean([response[item] for item in group]))
    strength = _unit(mean_strength / 0.32)
    horizontal = _unit(float(np.mean([coverage[item] for item in group])))
    availability = _unit(float(np.mean([valid_support[item] for item in group])))
    visibility = _unit(float(np.mean([visible_support[item] for item in group])))
    signed_value = float(np.mean([signed[item] for item in group]))
    polarity = _unit(abs(signed_value) / 80.0)
    static = _band_overlap(static_artifact_map, effective, row, radius=2)
    optics = _band_overlap(pre.glare_mask, effective, row, radius=2)
    boundary = _unit(
        0.42 * strength
        + 0.20 * horizontal
        + 0.16 * polarity
        + 0.12 * availability
        + 0.10 * visibility
    )
    artifact = _unit(0.70 * optics + 0.30 * static)
    ambiguity = _unit(
        0.45 * (1.0 - strength)
        + 0.25 * (1.0 - horizontal)
        + 0.20 * artifact
        + 0.10 * (1.0 - polarity)
    )
    source_y = float(crop_origin_y + row)
    return (
        BoundaryCandidate(
            source="distributed_sobel_path",
            kind=BoundaryKind.OIL_AIR,
            y=source_y,
            features={
                "supplemental_path": 1.0,
                "local_y": float(row),
                "source_y": source_y,
                "boundary_likelihood": boundary,
                "artifact_likelihood": artifact,
                "ambiguity_likelihood": ambiguity,
                "evidence_availability": availability,
                "visibility": visibility,
                "broad_strength": strength,
                "narrow_peak_strength": strength,
                "narrow_horizontal_coverage": horizontal,
                "broad_scale_consistency": _unit(1.0 - (last - first - 20.0) / 10.0),
                "polarity_confidence": polarity,
                "static_prior_contribution": static,
                "distributed_sobel_group_count": float(len(group)),
                "distributed_sobel_group_span_px": float(last - first),
                "sequence_eligible": float(visibility >= 0.30 and optics < 0.55),
            },
            penalties={
                "artifact_likelihood": artifact,
                "ambiguity_likelihood": ambiguity,
                "static_prior_contribution": static,
                "static_artifact_penalty": static,
                "glare_conflict": optics,
                "optics_conflict": optics,
                "exclusion_conflict": 0.0,
                "border_penalty": 0.0,
            },
            feature_score=boundary,
            penalty=_unit(artifact + ambiguity),
            final_score=boundary,
            selected=False,
            rejected=False,
        ),
    )


def _best_distributed_group(
    rows: list[int],
    response: np.ndarray,
    *,
    scale: int,
) -> tuple[int, ...] | None:
    minimum_span = 2 * scale
    maximum_span = 3 * scale
    best: tuple[int, ...] | None = None
    best_key: tuple[float, int, int, tuple[int, ...]] | None = None
    for start_index, first in enumerate(rows):
        group: list[int] = []
        for row in rows[start_index:]:
            if group and row - group[-1] > scale:
                break
            span = row - first
            if span > maximum_span:
                break
            group.append(row)
            if len(group) < 3 or span < minimum_span:
                continue
            mean = float(np.mean([response[item] for item in group]))
            key = (-mean, -len(group), span, tuple(group))
            if best_key is None or key < best_key:
                best_key = key
                best = tuple(group)
    return best


def _bounded_peak_rows(
    values: np.ndarray,
    limit: int,
    *,
    minimum: float,
) -> tuple[int, ...]:
    if values.size == 0:
        return ()
    local = values == cv2.dilate(
        values.astype(np.float32).reshape(-1, 1),
        np.ones((3, 1), dtype=np.uint8),
    ).reshape(-1)
    rows = np.flatnonzero(local & (values >= minimum))
    return tuple(
        int(row)
        for row in sorted(
            rows,
            key=lambda item: (-float(values[item]), int(item)),
        )[:limit]
    )


def _band_overlap(
    binary: np.ndarray | None,
    effective: np.ndarray,
    row: int,
    *,
    radius: int,
) -> float:
    if binary is None:
        return 0.0
    band = slice(max(0, row - radius), min(effective.shape[0], row + radius + 1))
    available = int(np.count_nonzero(effective[band]))
    if available <= 0:
        return 0.0
    return _unit(float(np.count_nonzero((binary[band] > 0) & effective[band])) / available)


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return min(1.0, max(0.0, float(value)))
