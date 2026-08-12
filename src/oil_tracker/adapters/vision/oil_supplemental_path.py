from __future__ import annotations

import math

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

from .preprocessing import PreprocessResult
from .row_features import masked_row_mean, row_coverage


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
            source="r8_distributed_sobel_path",
            kind=BoundaryKind.OIL_AIR,
            y=source_y,
            features={
                "r8_supplemental_path": 1.0,
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
