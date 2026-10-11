from __future__ import annotations

from dataclasses import dataclass
import math

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

from .preprocessing import PreprocessResult
from .oil_measurement_scope import active_exclusion, band_selection
from .oil_phase_topology import dark_border_cap_conflict


@dataclass(frozen=True)
class MaterialPathSample:
    sector_index: int
    start_x: int
    stop_x: int
    local_y: int
    strength: float
    signed_contrast: float
    contrast_channel: str
    contrast_scale_px: int


@dataclass(frozen=True)
class MaterialPathEvidence:
    local_y: float
    rows: tuple[int, ...]
    sector_count: int
    sector_fraction: float
    median_strength: float
    median_signed_contrast: float
    terminal_material_partition: float
    maximum_jump_px: int
    static_overlap: float
    optics_overlap: float
    diagnostic_samples: tuple[MaterialPathSample, ...] = ()


@dataclass(frozen=True)
class MaterialPathDiagnostic:
    """Frame-local sidecar; never stored in resolver-facing candidates."""

    candidate_source: str
    candidate_y: float
    evidence: MaterialPathEvidence


def material_layer_context_features(
    material_evidence_map: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    *,
    local_y: float,
) -> dict[str, float]:
    """Describe whether a candidate lies inside raw textured material.

    This is generic raster context, not a Foam decision. A high row support is
    comparative opposition for an Oil boundary; the lower material partition
    remains positive corroboration for the supplemental path generator.
    """

    if (
        material_evidence_map.shape != effective_mask.shape
        or glare_mask.shape != effective_mask.shape
    ):
        raise ValueError("Material layer context rasters must share one shape.")
    visible = (effective_mask > 0) & ~(glare_mask > 0)
    profile = _material_row_profile(material_evidence_map, visible)
    if profile is None or profile.size == 0:
        return {
            "raw_material_row_support": 0.0,
            "material_terminal_partition_support": 0.0,
            "material_texture_conflict": 0.0,
        }
    row = min(profile.size - 1, max(0, int(round(float(local_y)))))
    band = profile[max(0, row - 2) : min(profile.size, row + 3)]
    row_support = _unit(float(np.mean(band)) / 0.42) if band.size else 0.0
    terminal = _terminal_material_partition(profile, row)
    return {
        "raw_material_row_support": row_support,
        "material_terminal_partition_support": terminal,
        "material_texture_conflict": _unit(row_support * (1.0 - 0.25 * terminal)),
    }


def generate_material_path_candidates(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    crop_origin_y: float,
    top_k: int = 4,
    material_evidence_map: np.ndarray | None = None,
    diagnostic_paths: dict[int, MaterialPathEvidence] | None = None,
    measurement_exclusion: np.ndarray | None = None,
) -> tuple[BoundaryCandidate, ...]:
    """Generate low-contrast cross-column phase paths independently of Foam.

    Each sector contributes its own vertical band-contrast profile. A candidate
    must be supported by at least three spatially distinct sectors with a
    bounded curved path. No Foam mask/front or temporal/public state is read.
    """

    if pre.gray.ndim != 2 or effective_mask.shape != pre.gray.shape:
        raise ValueError("Material path inputs must share one two-dimensional ROI shape.")
    if static_artifact_map is not None and static_artifact_map.shape != pre.gray.shape:
        raise ValueError("Material path static map must match the ROI shape.")
    if material_evidence_map is not None and material_evidence_map.shape != pre.gray.shape:
        raise ValueError("Material evidence map must match the ROI shape.")
    if top_k < 1:
        raise ValueError("Material path top_k must be positive.")

    effective = effective_mask > 0
    visible = effective & ~(pre.glare_mask > 0)
    measurement_exclusion = active_exclusion(measurement_exclusion, visible)
    material_row_profile = _material_row_profile(
        material_evidence_map,
        visible,
    )
    rows, columns = np.where(effective)
    if rows.size < 32:
        return ()
    x0, x1 = int(columns.min()), int(columns.max()) + 1
    width = x1 - x0
    if width < 12:
        return ()

    sector_profiles: list[_SectorProfile] = []
    for sector in range(5):
        start = x0 + int(round(width * sector / 5.0))
        stop = x0 + int(round(width * (sector + 1) / 5.0))
        if stop - start < 2:
            continue
        profile = _sector_profile(
            pre.blurred,
            visible,
            start,
            stop,
            material_evidence_map=material_evidence_map,
            sector_index=sector,
            capture_diagnostics=diagnostic_paths is not None,
            measurement_exclusion=measurement_exclusion,
        )
        if profile is not None:
            sector_profiles.append(profile)
    if len(sector_profiles) < 3:
        return ()

    height = pre.gray.shape[0]
    # Curved menisci in the checked sight-glass geometry can move by roughly
    # seven percent of the ROI height between neighbouring fifths.  The old
    # 14 px cap forced those paths to collapse onto straighter internal texture.
    maximum_jump = max(5, min(24, int(round(height * 0.075))))
    seeds = _seed_rows(sector_profiles)
    paths: list[MaterialPathEvidence] = []
    for seed in seeds:
        evidence = _path_for_seed(
            seed,
            sector_profiles,
            visible,
            pre.glare_mask,
            static_artifact_map,
            material_row_profile=material_row_profile,
            maximum_jump=maximum_jump,
            capture_diagnostics=diagnostic_paths is not None,
        )
        if evidence is None:
            continue
        deduplication_radius = max(6, maximum_jump // 2)
        if any(
            abs(evidence.local_y - item.local_y) <= deduplication_radius
            for item in paths
        ):
            continue
        paths.append(evidence)
        if len(paths) >= top_k:
            break

    candidates = tuple(
        _candidate_from_path(
            item,
            crop_origin_y=crop_origin_y,
            border_cap_conflict=dark_border_cap_conflict(
                pre.blurred,
                effective_mask,
                pre.glare_mask,
                local_y=item.local_y,
            ),
        )
        for item in paths
    )
    if diagnostic_paths is not None:
        diagnostic_paths.update((id(candidate), path) for candidate, path in zip(candidates, paths))
    return tuple(
        sorted(
            candidates,
            key=lambda item: (-item.final_score, item.y, item.source),
        )
    )


@dataclass(frozen=True)
class _SectorProfile:
    start_x: int
    stop_x: int
    score: np.ndarray
    signed: np.ndarray
    support: np.ndarray
    sector_index: int = 0
    contrast_channel: np.ndarray | None = None
    contrast_scale: np.ndarray | None = None


def _sector_profile(
    gray: np.ndarray,
    visible: np.ndarray,
    start_x: int,
    stop_x: int,
    *,
    material_evidence_map: np.ndarray | None,
    sector_index: int = 0,
    capture_diagnostics: bool = False,
    measurement_exclusion: np.ndarray | None = None,
) -> _SectorProfile | None:
    sector_gray = gray[:, start_x:stop_x].astype(np.float32, copy=False)
    sector_mask = visible[:, start_x:stop_x]
    row_count = np.count_nonzero(sector_mask, axis=1).astype(np.float32)
    capacity = max(1, stop_x - start_x)
    support = np.clip(row_count / capacity, 0.0, 1.0)
    weighted = np.where(sector_mask, sector_gray, 0.0)
    row_mean = np.divide(
        np.sum(weighted, axis=1),
        np.maximum(row_count, 1.0),
    ).astype(np.float32)
    valid_values = sector_gray[sector_mask]
    if valid_values.size < 24:
        return None
    dynamic_range = max(
        18.0,
        float(np.percentile(valid_values, 90.0) - np.percentile(valid_values, 10.0)),
    )
    excluded = active_exclusion(measurement_exclusion, visible)
    sector_excluded = None if excluded is None else excluded[:, start_x:stop_x]
    used_mask = sector_mask if sector_excluded is None else sector_mask & ~sector_excluded
    used_count = np.count_nonzero(used_mask, axis=1).astype(np.float32)
    used_support = support if sector_excluded is None else np.clip(used_count / capacity, 0.0, 1.0)
    any_contrast = np.zeros(row_mean.size, bool)
    height = row_mean.size
    combined = np.zeros(height, dtype=np.float32)
    signed_best = np.zeros(height, dtype=np.float32)
    channel = np.zeros(height, dtype=np.uint8) if capture_diagnostics else None
    chosen_scale = np.zeros(height, dtype=np.uint8) if capture_diagnostics else None
    for scale in (3, 6, 10):
        upper = _window_mean(row_mean, support, scale, before=True)
        lower = _window_mean(row_mean, support, scale, before=False)
        availability = _window_support(used_support, scale)
        if sector_excluded is not None:
            _scoped_contrast(sector_gray, sector_mask, sector_excluded, scale, upper, lower, availability)
        signed = (lower - upper) / dynamic_range
        if sector_excluded is not None:
            any_contrast |= np.isfinite(signed)
            signed = np.nan_to_num(signed, nan=0.0)
        strength = np.abs(signed)
        score = strength * np.clip((availability - 0.35) / 0.65, 0.0, 1.0)
        replace_rows = score > combined
        combined[replace_rows] = score[replace_rows]
        signed_best[replace_rows] = signed[replace_rows]
        if channel is not None:
            channel[replace_rows] = 1
            chosen_scale[replace_rows] = scale

    if material_evidence_map is not None:
        material = np.clip(
            material_evidence_map[:, start_x:stop_x].astype(np.float32, copy=False),
            0.0,
            1.0,
        )
        material_row = np.divide(
            np.sum(np.where(sector_mask, material, 0.0), axis=1),
            np.maximum(row_count, 1.0),
        ).astype(np.float32)
        for scale in (3, 6, 10):
            upper = _window_mean(material_row, support, scale, before=True)
            lower = _window_mean(material_row, support, scale, before=False)
            availability = _window_support(used_support, scale)
            if sector_excluded is not None:
                _scoped_contrast(material, sector_mask, sector_excluded, scale, upper, lower, availability)
            signed = lower - upper
            if sector_excluded is not None:
                any_contrast |= np.isfinite(signed)
                signed = np.nan_to_num(signed, nan=0.0)
            score = (
                np.clip(np.abs(signed) / 0.32, 0.0, 1.0)
                * np.clip((availability - 0.35) / 0.65, 0.0, 1.0)
            )
            replace_rows = score > combined
            combined[replace_rows] = score[replace_rows]
            signed_best[replace_rows] = signed[replace_rows]
            if channel is not None:
                channel[replace_rows] = 2
                chosen_scale[replace_rows] = scale

    sobel = np.abs(
        np.divide(
            np.sum(
                np.where(
                    used_mask,
                    np.abs(cv2.Sobel(sector_gray, cv2.CV_32F, 0, 1, ksize=3)),
                    0.0,
                ),
                axis=1,
            ),
            np.maximum(used_count, 1.0),
        )
    )
    sobel_score = np.clip(sobel / 90.0, 0.0, 1.0)
    combined = np.clip(0.78 * combined + 0.22 * sobel_score, 0.0, 1.0)
    combined[used_support < 0.42] = 0.0
    if sector_excluded is not None:
        combined[~any_contrast] = 0.0
    margin = max(4, int(round(height * 0.05)))
    combined[:margin] = 0.0
    combined[-margin:] = 0.0
    return _SectorProfile(start_x, stop_x, combined, signed_best, used_support,
                          sector_index, channel, chosen_scale)


def _scoped_contrast(values, visible, excluded, scale, upper, lower, availability):
    """Override only operations losing eligible band samples; keep base prefixes."""
    h, width = visible.shape
    changed_rows = np.flatnonzero(np.any(visible & excluded, axis=1))
    affected = set()
    for y in changed_rows:
        affected.update(range(max(0, int(y)-scale), min(h, int(y)+scale+1)))
    for row in sorted(affected):
        a, b = slice(max(0, row-scale), row), slice(row+1, min(h, row+scale+1))
        minimum = max(2, math.ceil(width * .42)) * max(row-max(0, row-scale), min(h, row+scale+1)-row-1)
        u, l, changed, reason = band_selection(visible[a], visible[b], excluded[a], excluded[b], minimum=minimum)
        if not changed:
            continue
        if reason != "complete_common_x":
            upper[row] = lower[row] = np.nan
            availability[row] = 0.0
        else:
            upper[row], lower[row] = np.mean(values[a][u]), np.mean(values[b][l])
            availability[row] = min(availability[row], float(np.all(u, axis=0).mean()))


def _window_mean(
    values: np.ndarray,
    support: np.ndarray,
    scale: int,
    *,
    before: bool,
) -> np.ndarray:
    size = int(values.size)
    if size == 0:
        return np.zeros_like(values, dtype=np.float32)
    rows = np.arange(size, dtype=np.int64)
    if before:
        starts = np.maximum(0, rows - int(scale))
        stops = rows
    else:
        starts = rows + 1
        stops = np.minimum(size, rows + int(scale) + 1)
    weights = support.astype(np.float64, copy=False)
    weighted = values.astype(np.float64, copy=False) * weights
    weight_prefix = np.concatenate(([0.0], np.cumsum(weights)))
    value_prefix = np.concatenate(([0.0], np.cumsum(weighted)))
    totals = weight_prefix[stops] - weight_prefix[starts]
    numerators = value_prefix[stops] - value_prefix[starts]
    output = np.zeros(size, dtype=np.float64)
    np.divide(numerators, totals, out=output, where=totals > 1e-6)
    return output.astype(np.float32)


def _window_support(support: np.ndarray, scale: int) -> np.ndarray:
    size = int(support.size)
    if size == 0:
        return np.zeros_like(support, dtype=np.float32)
    rows = np.arange(size, dtype=np.int64)
    starts = np.maximum(0, rows - int(scale))
    stops = np.minimum(size, rows + int(scale) + 1)
    prefix = np.concatenate(
        ([0.0], np.cumsum(support.astype(np.float64, copy=False)))
    )
    totals = prefix[stops] - prefix[starts]
    counts = np.maximum(1, stops - starts)
    return (totals / counts).astype(np.float32)


def _seed_rows(profiles: list[_SectorProfile]) -> tuple[int, ...]:
    height = profiles[0].score.size
    aggregate = np.zeros(height, dtype=np.float32)
    count = np.zeros(height, dtype=np.float32)
    for profile in profiles:
        aggregate += profile.score
        count += profile.score > 0.0
    aggregate = np.divide(aggregate, np.maximum(count, 1.0))
    aggregate[count < 3] = 0.0
    local_maximum = aggregate == cv2.dilate(
        aggregate.reshape(-1, 1),
        np.ones((9, 1), dtype=np.uint8),
    ).reshape(-1)
    seeds = np.flatnonzero(local_maximum & (aggregate >= 0.105))
    return tuple(
        int(row)
        for row in sorted(
            seeds,
            key=lambda row: (-float(aggregate[row]), int(row)),
        )
    )


def _path_for_seed(
    seed: int,
    profiles: list[_SectorProfile],
    visible: np.ndarray,
    glare_mask: np.ndarray,
    static_artifact_map: np.ndarray | None,
    *,
    material_row_profile: np.ndarray | None,
    maximum_jump: int,
    capture_diagnostics: bool = False,
) -> MaterialPathEvidence | None:
    alternatives = tuple(
        _polarity_path_for_seed(
            seed,
            profiles,
            polarity=polarity,
            maximum_jump=maximum_jump,
            capture_diagnostics=capture_diagnostics,
        )
        for polarity in (-1, 1)
    )
    path = max(
        (item for item in alternatives if item is not None),
        key=lambda item: (
            len(item[0]),
            float(np.median(np.asarray(item[1], dtype=np.float32))),
            -max(
                (
                    abs(current - prior)
                    for prior, current in zip(item[0], item[0][1:])
                ),
                default=0,
            ),
        ),
        default=None,
    )
    if path is None:
        return None
    ordered, strengths, signed, profile_indices = path
    jumps = tuple(
        abs(current - prior)
        for prior, current in zip(ordered, ordered[1:])
    )
    max_jump = max(jumps, default=0)
    if max_jump > maximum_jump:
        return None
    median_y = float(np.median(np.asarray(ordered, dtype=np.float32)))
    median_strength = float(np.median(np.asarray(strengths, dtype=np.float32)))
    median_signed = float(np.median(np.asarray(signed, dtype=np.float32)))
    if median_strength < 0.105 or abs(median_signed) < 0.035:
        return None
    row = int(round(median_y))
    band = slice(max(0, row - 2), min(visible.shape[0], row + 3))
    effective_band = visible[band] | (glare_mask[band] > 0)
    available = max(1, int(np.count_nonzero(effective_band)))
    optics = (
        float(np.count_nonzero((glare_mask[band] > 0) & effective_band))
        / available
    )
    static = 0.0
    if static_artifact_map is not None:
        static = float(
            np.count_nonzero((static_artifact_map[band] > 0) & effective_band)
        ) / available
    terminal_partition = _terminal_material_partition(
        material_row_profile,
        row,
    )
    return MaterialPathEvidence(
        local_y=median_y,
        rows=ordered,
        sector_count=len(ordered),
        sector_fraction=len(ordered) / max(1, len(profiles)),
        median_strength=median_strength,
        median_signed_contrast=median_signed,
        terminal_material_partition=terminal_partition,
        maximum_jump_px=max_jump,
        static_overlap=static,
        optics_overlap=optics,
        diagnostic_samples=tuple(
            MaterialPathSample(
                sector_index=profiles[index].sector_index,
                start_x=profiles[index].start_x,
                stop_x=profiles[index].stop_x,
                local_y=y,
                strength=strength,
                signed_contrast=contrast,
                contrast_channel={0: "unavailable", 1: "blurred_gray_dynamic_range", 2: "raw_combined_material"}[
                    int(profiles[index].contrast_channel[y])
                ],
                contrast_scale_px=int(profiles[index].contrast_scale[y]),
            )
            for index, y, strength, contrast in zip(profile_indices, ordered, strengths, signed)
        ),
    )


def _material_row_profile(
    material_evidence_map: np.ndarray | None,
    visible: np.ndarray,
) -> np.ndarray | None:
    if material_evidence_map is None:
        return None
    material = np.clip(
        material_evidence_map.astype(np.float32, copy=False),
        0.0,
        1.0,
    )
    count = np.count_nonzero(visible, axis=1).astype(np.float32)
    return np.divide(
        np.sum(np.where(visible, material, 0.0), axis=1),
        np.maximum(count, 1.0),
    ).astype(np.float32)


def _terminal_material_partition(
    profile: np.ndarray | None,
    row: int,
) -> float:
    if profile is None or profile.size < 12:
        return 0.0
    values: list[float] = []
    for ratio in (0.10, 0.16, 0.22):
        depth = max(4, int(round(profile.size * ratio)))
        upper = profile[max(0, row - depth) : row]
        lower = profile[row + 1 : min(profile.size, row + depth + 1)]
        if upper.size < 3 or lower.size < 3:
            continue
        values.append(float(np.mean(upper) - np.mean(lower)))
    if not values:
        return 0.0
    # This is positive evidence for the lower boundary of a coherent material
    # layer. Negative/flat profiles are not vetoes: Oil polarity remains free.
    return _unit(float(np.median(np.asarray(values, dtype=np.float32))) / 0.16)


_PathState = tuple[float, tuple[int, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]]


def _polarity_path_for_seed(
    seed: int,
    profiles: list[_SectorProfile],
    *,
    polarity: int,
    maximum_jump: int,
    capture_diagnostics: bool = False,
) -> tuple[tuple[int, ...], tuple[float, ...], tuple[float, ...], tuple[int, ...]] | None:
    """Find a contiguous cross-sector path without mixing phase polarity."""

    prior: dict[int, _PathState] = {}
    best: _PathState | None = None
    for profile_index, profile in enumerate(profiles):
        start = max(0, seed - maximum_jump)
        stop = min(profile.score.size, seed + maximum_jump + 1)
        current: dict[int, _PathState] = {}
        for row in range(start, stop):
            strength = float(profile.score[row])
            signed = float(profile.signed[row])
            if (
                strength < 0.09
                or profile.support[row] < 0.42
                or polarity * signed < 0.025
            ):
                continue
            phase_support = min(1.0, abs(signed) / 0.20)
            local_value = strength + 0.08 * phase_support
            previous = max(
                (
                    value
                    for prior_row, value in prior.items()
                    if abs(row - prior_row) <= maximum_jump
                ),
                key=lambda value: (
                    len(value[1]),
                    value[0],
                    -abs(row - value[1][-1]),
                ),
                default=None,
            )
            if previous is None:
                value = (local_value, (row,), (strength,), (signed,),
                         (profile_index,) if capture_diagnostics else ())
            else:
                value = (
                    previous[0] + local_value,
                    (*previous[1], row),
                    (*previous[2], strength),
                    (*previous[3], signed),
                    (*previous[4], profile_index) if capture_diagnostics else (),
                )
            current[row] = value
            if len(value[1]) >= 3 and (
                best is None
                or (len(value[1]), value[0]) > (len(best[1]), best[0])
            ):
                best = value
        prior = current
    if best is None:
        return None
    return best[1], best[2], best[3], best[4]


def _candidate_from_path(
    evidence: MaterialPathEvidence,
    *,
    crop_origin_y: float,
    border_cap_conflict: bool,
) -> BoundaryCandidate:
    path_consistency = _unit(1.0 - evidence.maximum_jump_px / 15.0)
    strength = _unit(evidence.median_strength / 0.32)
    boundary = _unit(
        0.34 * strength
        + 0.24 * evidence.sector_fraction
        + 0.18 * path_consistency
        + 0.08 * _unit(abs(evidence.median_signed_contrast) / 0.20)
        + 0.16 * evidence.terminal_material_partition
    )
    artifact = _unit(
        0.88 * evidence.optics_overlap
        + 0.12 * (1.0 - path_consistency)
    )
    ambiguity = _unit(0.48 * (1.0 - strength) + 0.32 * (1.0 - evidence.sector_fraction) + 0.20 * artifact)
    source_y = float(crop_origin_y + evidence.local_y)
    return BoundaryCandidate(
        source="material_path",
        kind=BoundaryKind.OIL_AIR,
        y=source_y,
        features={
            "material_path": 1.0,
            "local_y": float(evidence.local_y),
            "source_y": source_y,
            "boundary_likelihood": boundary,
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "evidence_availability": 1.0,
            "visibility": _unit(1.0 - evidence.optics_overlap),
            "broad_strength": strength,
            "narrow_peak_strength": strength,
            "narrow_horizontal_coverage": evidence.sector_fraction,
            "broad_scale_consistency": path_consistency,
            "polarity_confidence": _unit(abs(evidence.median_signed_contrast) / 0.20),
            "static_prior_contribution": evidence.static_overlap,
            "material_path_sector_count": float(evidence.sector_count),
            "material_path_sector_fraction": float(evidence.sector_fraction),
            "material_path_maximum_jump_px": float(evidence.maximum_jump_px),
            "material_path_median_signed_contrast": float(evidence.median_signed_contrast),
            "material_terminal_partition_support": float(
                evidence.terminal_material_partition
            ),
            "material_path_dark_border_cap_conflict": float(border_cap_conflict),
            "sequence_eligible": float(
                evidence.optics_overlap < 0.55 and not border_cap_conflict
            ),
        },
        penalties={
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "static_prior_contribution": evidence.static_overlap,
            "static_artifact_penalty": evidence.static_overlap,
            "glare_conflict": evidence.optics_overlap,
            "optics_conflict": evidence.optics_overlap,
            "exclusion_conflict": 0.0,
            "border_penalty": float(border_cap_conflict),
        },
        feature_score=boundary,
        penalty=_unit(artifact + ambiguity),
        final_score=boundary,
        selected=False,
        rejected=False,
    )


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return min(1.0, max(0.0, float(value)))


@dataclass(frozen=True)
class CenterPathAlternative:
    """One pooled-sector hypothesis, not a contour or a publishable candidate."""

    seed: int
    polarity: int
    center_row: int
    status: str
    objective_score: float | None = None
    rows: tuple[int, ...] = ()
    profile_indices: tuple[int, ...] = ()
    samples: tuple[MaterialPathSample, ...] = ()
    passes_path_median_checks: bool | None = None


@dataclass(frozen=True)
class CenterPathDiagnostics:
    """Complete bounded offline capture; unavailable never means a negative."""

    status: str
    reason: str
    center_sector_index: int
    seeds: tuple[int, ...] = ()
    maximum_jump: int = 0
    transition_bound: int = 0
    peak_live_states: int = 0
    alternatives: tuple[CenterPathAlternative, ...] = ()


def diagnose_center_path_alternatives(
    profiles: list[_SectorProfile],
    *,
    center_sector_index: int = 2,
    maximum_jump: int | None = None,
    max_records: int = 16384,
    max_transitions: int = 50_000_000,
) -> CenterPathDiagnostics:
    """Preserve each original seed/polarity's best path through each centre row.

    The DP state includes the centre row so different centre alternatives never
    compete before role analysis. Objective: sector count, then the existing
    sum(strength + .08 * min(1, abs(signed)/.20)). Median postchecks are reported
    separately, not optimized or relaxed. No production caller consumes this.
    Limits apply to the complete capture: no favourable partial prefix escapes.
    """
    if not 0 <= center_sector_index < 5:
        raise ValueError("The centre must name one of the original five sectors.")
    if max_records < 1 or max_transitions < 1:
        raise ValueError("Diagnostic budgets must be positive.")
    if not profiles:
        return CenterPathDiagnostics("UNAVAILABLE", "no_profiles", center_sector_index)
    height = profiles[0].score.size
    if len(profiles) > 5 or height > 2160:
        return CenterPathDiagnostics("UNAVAILABLE", "input_budget", center_sector_index)
    _validate_center_profiles(profiles, height)
    jump = max(5, min(24, int(round(height * .075)))) if maximum_jump is None else maximum_jump
    if not isinstance(jump, int) or not 1 <= jump <= 24:
        raise ValueError("maximum_jump must be an integer in [1, 24].")
    indices = [p.sector_index for p in profiles]
    if len(profiles) < 3 or center_sector_index not in indices:
        return CenterPathDiagnostics("UNAVAILABLE", "missing_center_or_sectors", center_sector_index)
    center_index = indices.index(center_sector_index)
    seeds = _seed_rows(profiles)
    widths = [min(height, seed + jump + 1) - max(0, seed - jump) for seed in seeds]
    record_bound = 2 * sum(widths)
    # Before centre: W states; after centre: at most W*W states, each with W predecessors.
    transition_bound = 2 * sum(
        (center_index + 1) * w * w + (len(profiles) - center_index - 1) * w ** 3
        for w in widths
    )
    if record_bound > max_records or transition_bound > max_transitions:
        return CenterPathDiagnostics("UNAVAILABLE", "work_or_record_budget", center_sector_index,
                                     seeds, jump, transition_bound)
    alternatives: list[CenterPathAlternative] = []
    peak = 0
    for seed in seeds:
        for polarity in (-1, 1):
            best, live = _center_conditioned_paths(seed, profiles, center_index, polarity, jump)
            peak = max(peak, live)
            for row in range(max(0, seed - jump), min(height, seed + jump + 1)):
                state = best.get(row)
                status = "PATH" if state is not None else (
                    "CENTER_INELIGIBLE" if not _center_node_ok(profiles[center_index], row, polarity)
                    else "NO_THREE_SECTOR_PATH")
                alternatives.append(_center_alternative(seed, polarity, row, status, state, profiles))
    return CenterPathDiagnostics("COMPLETE", "", center_sector_index, seeds, jump,
                                 transition_bound, peak, tuple(alternatives))


def _validate_center_profiles(profiles: list[_SectorProfile], height: int) -> None:
    if height < 1:
        raise ValueError("Profiles must have nonempty one-dimensional arrays.")
    indices = [p.sector_index for p in profiles]
    if indices != sorted(set(indices)) or any(i not in range(5) for i in indices):
        raise ValueError("Profiles must preserve unique original sector order.")
    for i, p in enumerate(profiles):
        arrays = (p.score, p.signed, p.support)
        if any(a.shape != (height,) or not np.all(np.isfinite(a)) for a in arrays):
            raise ValueError("Profile arrays must share a finite one-dimensional shape.")
        if np.any((p.score < 0) | (p.score > 1) | (p.support < 0) | (p.support > 1)):
            raise ValueError("Profile score and support must be in [0, 1].")
        if p.start_x < 0 or p.stop_x <= p.start_x or (i and p.start_x < profiles[i-1].stop_x):
            raise ValueError("Original sector X bands must be ordered and nonoverlapping.")
        if (p.contrast_channel is None) != (p.contrast_scale is None):
            raise ValueError("Channel and scale provenance must be available together.")
        if p.contrast_channel is not None:
            if (p.contrast_channel.shape != (height,) or p.contrast_scale.shape != (height,)
                    or not np.all(np.isin(p.contrast_channel, (0, 1, 2)))
                    or not np.all(np.isin(p.contrast_scale, (0, 3, 6, 10)))):
                raise ValueError("Invalid channel/scale provenance.")


def _center_node_ok(profile: _SectorProfile, row: int, polarity: int) -> bool:
    return (float(profile.score[row]) >= .09 and profile.support[row] >= .42
            and polarity * float(profile.signed[row]) >= .025)


def _center_conditioned_paths(
    seed: int, profiles: list[_SectorProfile], center_index: int, polarity: int, jump: int,
) -> tuple[dict[int, _PathState], int]:
    # Each group retains its centre condition; tuples are bounded backtraces (<=5 nodes).
    prior: dict[int | None, dict[int, _PathState]] = {}
    best: dict[int, _PathState] = {}
    peak = 0
    for index, profile in enumerate(profiles):
        current: dict[int | None, dict[int, _PathState]] = {}
        start, stop = max(0, seed-jump), min(profile.score.size, seed+jump+1)
        for row in range(start, stop):
            if not _center_node_ok(profile, row, polarity):
                continue
            strength, signed = float(profile.score[row]), float(profile.signed[row])
            local = strength + .08 * min(1., abs(signed)/.20)
            groups = [(None, prior.get(None, {}))] if index <= center_index else prior.items()
            for center, states in groups:
                previous = max(
                    (state for y, state in states.items() if abs(row-y) <= jump),
                    key=lambda state: (len(state[1]), state[0], -abs(row-state[1][-1])),
                    default=None,
                )
                if previous is None and index > center_index:
                    continue  # A restart to the right would not contain the centre.
                if previous is None:
                    value = (local, (row,), (strength,), (signed,), (index,))
                else:
                    value = (previous[0]+local, (*previous[1], row), (*previous[2], strength),
                             (*previous[3], signed), (*previous[4], index))
                key = row if index == center_index else center
                current.setdefault(key, {})[row] = value
                if key is not None and len(value[1]) >= 3:
                    old = best.get(key)
                    if old is None or (len(value[1]), value[0]) > (len(old[1]), old[0]):
                        best[key] = value
        peak = max(peak, sum(map(len, prior.values())) + sum(map(len, current.values())) + len(best))
        prior = current
    return best, peak


def _center_alternative(
    seed: int, polarity: int, row: int, status: str,
    state: _PathState | None, profiles: list[_SectorProfile],
) -> CenterPathAlternative:
    if state is None:
        return CenterPathAlternative(seed, polarity, row, status)
    score, rows, strengths, signed, indices = state
    samples = []
    for i, y, strength, contrast in zip(indices, rows, strengths, signed):
        p = profiles[i]
        channel = int(p.contrast_channel[y]) if p.contrast_channel is not None else 0
        scale = int(p.contrast_scale[y]) if p.contrast_scale is not None else 0
        samples.append(MaterialPathSample(
            p.sector_index, p.start_x, p.stop_x, y, strength, contrast,
            {0: "unavailable", 1: "blurred_gray_dynamic_range", 2: "raw_combined_material"}[channel], scale))
    passed = (float(np.median(np.asarray(strengths, np.float32))) >= .105
              and abs(float(np.median(np.asarray(signed, np.float32)))) >= .035)
    return CenterPathAlternative(seed, polarity, row, status, score, rows, indices,
                                 tuple(samples), passed)
