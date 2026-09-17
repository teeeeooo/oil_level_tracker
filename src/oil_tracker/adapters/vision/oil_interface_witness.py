"""O1 immutable, current-frame measurements. No classifier or resolver authority.

Geometry spread is not localization uncertainty. Peak hulls describe measured
alternatives only; neither a confidence interval nor a certified physical edge.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .oil_interface_diagnostics import _measure_sector

WITNESS_SCHEMA = "interface-observability-witness-trace-v1"
SCALE_MULTIPLIERS = (1, 2, 3)
SIGMA_FLOOR = 1.0 / 255.0
MAX_PEAKS = 3
PEAK_EPSILON = 1e-12


@dataclass(frozen=True)
class FrameOpticalObservability:
    frame_index: int
    glass_id: str
    visible_fraction: float | None
    saturation_fraction: float | None
    glare_fraction: float | None
    acquisition_mode: str = "passive_metadata_unavailable"
    exposure_identity: None = None
    texture_reference_available: None = None
    status: str = "NOT_EVALUATED"
    reasons: tuple[str, ...] = ("acquisition_metadata_unavailable", "classification_not_evaluated")


@dataclass(frozen=True)
class BandWitness:
    name: str
    local_y_range: tuple[int, int]
    clipped_local_y_range: tuple[int, int]
    available: bool
    reason: str
    valid_fraction: float
    valid_pixel_count: int
    gray_mean: float | None
    gray_std: float | None
    material_mean: float | None
    material_available: bool
    static_overlap: float | None
    static_available: bool
    glare_fraction: float | None
    edge_density: float | None
    gradient_magnitude: float | None
    gradient_valid_pixel_count: int
    normal_alignment: float | None
    saturation_fraction: float | None
    mask_excluded_fraction: float | None


@dataclass(frozen=True)
class PeakWitness:
    source_y: int
    plateau_source_y_range: tuple[int, int]
    signed_gradient: float
    touches_search_boundary: bool


@dataclass(frozen=True)
class ScaleWitness:
    band_width_px: int
    bands: tuple[BandWitness, ...]
    signed_delta: float | None
    absolute_delta: float | None
    normalization_denominator: float | None
    normalized_delta: float | None
    edge_density_delta: float | None
    search_local_y_range: tuple[int, int]
    clipped_search_local_y_range: tuple[int, int]
    peaks: tuple[PeakWitness, ...]
    peak_count_before_truncation: int
    peaks_truncated: bool
    peak_hull_source_y: tuple[int, int] | None
    localization_status: str


@dataclass(frozen=True)
class CenterWitness:
    role: str
    source_y: float
    sampling_center_local_y: int
    scales: tuple[ScaleWitness, ...]


@dataclass(frozen=True)
class InterfaceSectorWitness:
    sector: int
    source_x_range: tuple[int, int]
    path_source_y: float | None
    candidate_source_y: float
    centers: tuple[CenterWitness, ...]
    normal_mode: str = "vertical_approximation"


@dataclass(frozen=True)
class InterfaceContourHypothesis:
    geometry_source: str
    native_path_reason: str
    sector_source_y_range: tuple[float, float] | None
    # This range is contour shape, NEVER added to a local peak hull.
    curve_summary: None = None
    localization_uncertainty_px: None = None
    uncertainty_reason: str = "no_calibrated_uncertainty_estimator"


@dataclass(frozen=True)
class OilInterfaceWitness:
    candidate_input_index: int
    source: str
    kind: str
    canonical_y: float | None
    local_y: float | None
    rejected: bool
    measurement_status: str
    contour: InterfaceContourHypothesis
    sectors: tuple[InterfaceSectorWitness, ...]
    lineage_groups: tuple[tuple[str, ...], ...] = (
        ("current_rgb", "raw_gray", "canny_from_clahe_blurred_gray", "raw_material_map"),
        ("static_reference_when_available",),
    )
    decision: str = "NOT_EVALUATED"


@dataclass(frozen=True)
class FrameInterfaceWitness:
    schema_version: str
    source_frame_index: int
    glass_id: str
    crop_origin: tuple[int, int]
    crop_size: tuple[int, int]
    observability: FrameOpticalObservability
    candidates: tuple[OilInterfaceWitness, ...]
    candidate_index_space: str = "detection.candidates_before_trace_score_sort"
    coordinate_space: str = "source_frame_y"
    positive_direction: str = "down"
    diagnostic_only: bool = True
    sigma_floor: float = SIGMA_FLOOR
    scale_multipliers: tuple[int, ...] = SCALE_MULTIPLIERS
    max_peaks_per_scale: int = MAX_PEAKS
    peak_tie_break: str = "absolute_gradient_descending_then_lowest_source_y"
    plateau_tolerance: float = PEAK_EPSILON
    peak_gradient_channel: str = "central_difference_of_masked_raw_gray_row_mean"
    interval_semantics: str = "retained_peak_plateau_hull_not_confidence_interval"
    structural_reference_reason: str = "vessel_fitting_geometry_unavailable"


def _ratio(numerator, denominator):
    return float(numerator / denominator) if denominator else None


def _extra_channels(gray, visible, effective, canny):
    """One frame-local prefix cache per X extent; reuse old gray/material profiles."""
    values = np.where(np.isfinite(gray), gray, 0).astype(np.float64) / 255.0
    # Raw-gray spatial gradients; no CLAHE/Sobel polarity is promoted to identity.
    gx = np.zeros_like(values)
    gy = np.zeros_like(values)
    valid = np.zeros_like(visible)
    gx[1:-1, 1:-1] = (values[1:-1, 2:] - values[1:-1, :-2]) / 2
    gy[1:-1, 1:-1] = (values[2:, 1:-1] - values[:-2, 1:-1]) / 2
    valid[1:-1, 1:-1] = (visible[1:-1, 1:-1] & visible[1:-1, 2:]
        & visible[1:-1, :-2] & visible[2:, 1:-1] & visible[:-2, 1:-1])
    magnitude = np.hypot(gx, gy)
    channels = {
        "edge": np.where(visible, canny > 0, 0),
        "gradient_count": valid,
        "gradient": np.where(valid, magnitude, 0),
        "normal": np.where(valid, np.abs(gy), 0),
        "saturation": effective & ((gray == 0) | (gray == 255)),
        "excluded": ~effective,
    }
    return channels


def _extra_profiles(channels, start, stop):
    return {k: np.r_[0.0, np.cumsum(v[:, start:stop].sum(axis=1))] for k, v in channels.items()}


def _band_witness(name, measured, extra, height, width):
    start, stop = measured["local_y_range"]
    lo, hi = max(0, min(height, start)), max(0, min(height, stop))
    totals = {k: float(v[hi] - v[lo]) for k, v in extra.items()}
    available = measured["available"]
    area = (hi - lo) * width
    return BandWitness(
        name, (start, stop), (lo, hi), available, measured["reason"],
        measured["valid_fraction"], measured["valid_pixel_count"],
        measured["gray_mean"], measured["gray_std"], measured["material_mean"],
        measured["material_available"], measured["static_overlap"],
        measured["static_available"], measured["glare_fraction"],
        _ratio(totals["edge"], measured["valid_pixel_count"]) if available else None,
        _ratio(totals["gradient"], totals["gradient_count"]) if available else None,
        int(totals["gradient_count"]),
        _ratio(totals["normal"], totals["gradient"]) if available else None,
        _ratio(totals["saturation"], area), _ratio(totals["excluded"], area),
    )


def _peaks(gradient, valid, lo, hi, origin):
    """Local maxima of absolute row gradient, grouping equal-height plateaus."""
    peaks = []
    i = lo
    while i < hi:
        if not valid[i] or abs(gradient[i]) <= PEAK_EPSILON:
            i += 1
            continue
        end = i + 1
        while (end < hi and valid[end]
               and abs(gradient[end] - gradient[i]) <= PEAK_EPSILON):
            end += 1
        left = abs(gradient[i - 1]) if i > lo and valid[i - 1] and gradient[i - 1] * gradient[i] > 0 else -1
        right = abs(gradient[end]) if end < hi and valid[end] and gradient[end] * gradient[i] > 0 else -1
        if abs(gradient[i]) > max(left, right) + PEAK_EPSILON:
            peaks.append(PeakWitness(i + origin, (i + origin, end + origin),
                                     float(gradient[i]), i == lo or end == hi))
        i = end
    peaks.sort(key=lambda p: (-abs(p.signed_gradient), p.source_y))
    return tuple(peaks[:MAX_PEAKS]), len(peaks)


def _center(profile, extra, *, role, source_y, sector, band, origin, height):
    local_y = source_y - origin[1]
    center = int(math.floor(local_y + 0.5))
    scales = []
    for multiplier in SCALE_MULTIPLIERS:
        width = band * multiplier
        m = _measure_sector(profile, sector=sector, center=center, band=width,
                            local_y=local_y, crop_origin=origin, height=height)
        bands = tuple(_band_witness(k, v, extra, height, profile[1] - profile[0])
                      for k, v in m["bands"].items())
        above, below = bands[:2]
        delta = m["near_signed_contrast"]
        denominator = (math.sqrt(above.gray_std**2 + below.gray_std**2 + SIGMA_FLOOR**2)
                       if delta is not None else None)
        intended = (center - width, center + width + 1)
        lo, hi = max(0, intended[0]), min(height, intended[1])
        peaks, count = _peaks(profile[3], profile[4], lo, hi, origin[1])
        hull = ((min(p.plateau_source_y_range[0] for p in peaks),
                 max(p.plateau_source_y_range[1] for p in peaks)) if peaks else None)
        status = ("unavailable" if not np.any(profile[4][lo:hi]) else
                  "no_peak" if not peaks else
                  "truncated" if count > MAX_PEAKS else
                  "search_boundary" if any(p.touches_search_boundary for p in peaks) else
                  "multiple_peaks" if count > 1 else "single_peak")
        scales.append(ScaleWitness(width, bands, delta, abs(delta) if delta is not None else None,
            denominator, delta / denominator if denominator is not None else None,
            below.edge_density - above.edge_density if above.edge_density is not None and below.edge_density is not None else None,
            intended, (lo, hi), peaks, count, count > MAX_PEAKS, hull, status))
    return CenterWitness(role, source_y, center, tuple(scales))


def build_interface_witness(diagnostic, profiles, *, gray, visible, effective_mask, glare_mask,
                            canny, glass_id):
    """Consume validated geometry and shared old profile cache; never mutate them."""
    shape = gray.shape
    if canny.shape != shape:
        raise ValueError("Witness edge raster must share the diagnostic crop.")
    height, width = shape
    effective = effective_mask > 0
    count = int(effective.sum())
    frame = FrameOpticalObservability(diagnostic["source_frame_index"], glass_id,
        _ratio(visible.sum(), count),
        _ratio((effective & ((gray == 0) | (gray == 255))).sum(), count),
        _ratio((effective & (glare_mask > 0)).sum(), count))
    origin = tuple(diagnostic["crop_origin"])
    extra_cache = {}
    extra_channels = _extra_channels(gray, visible, effective, canny)
    candidates = []
    for row in diagnostic["candidates"]:
        path = row["path_aligned"]
        native = bool(path["sectors"])
        rows = path["sectors"] if native else row["sectors"]
        sectors = []
        for sector in rows:
            x0, x1 = sector["source_x_range"]
            extent = x0 - origin[0], x1 - origin[0]
            if extent not in extra_cache:
                extra_cache[extent] = _extra_profiles(extra_channels, *extent)
            centers = []
            path_y = sector.get("path_source_y") if native else None
            source_y = path_y if native else row["canonical_y"]
            centers.append(_center(profiles[extent], extra_cache[extent],
                role="native_path" if native else "candidate_center", source_y=source_y,
                sector=sector["sector"], band=diagnostic["band_width_px"], origin=origin, height=height))
            if native and path_y != row["canonical_y"]:
                centers.append(_center(profiles[extent], extra_cache[extent], role="candidate_center",
                    source_y=row["canonical_y"], sector=sector["sector"],
                    band=diagnostic["band_width_px"], origin=origin, height=height))
            sectors.append(InterfaceSectorWitness(sector["sector"], (x0, x1), path_y,
                                                  row["canonical_y"], tuple(centers)))
        ys = [s.path_source_y for s in sectors if s.path_source_y is not None]
        contour = InterfaceContourHypothesis("native_generator_path" if native else "candidate_center_only",
            path["reason"], (min(ys), max(ys)) if ys else None)
        candidates.append(OilInterfaceWitness(row["candidate_input_index"], row["source"], "oil_air",
            row["canonical_y"], row["local_y"], row["rejected"], row["measurement_status"], contour, tuple(sectors)))
    return FrameInterfaceWitness(WITNESS_SCHEMA, diagnostic["source_frame_index"], glass_id,
                                 origin, (width, height), frame, tuple(candidates))
