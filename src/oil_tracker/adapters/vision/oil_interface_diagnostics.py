"""R22-2 raster measurements for trace only; never detector authority.

All channels share the current raster. Channel/source names do not prove
independence. No Oil/interface classification or temporal state is produced.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

from .oil_material_path import MaterialPathDiagnostic


INTERFACE_DIAGNOSTICS_SCHEMA = "r22-2-interface-path-diagnostics-v1"


def measure_oil_interfaces(
    candidates: Sequence[BoundaryCandidate],
    *,
    gray: np.ndarray,
    effective_mask: np.ndarray,
    glare_mask: np.ndarray,
    material_map: np.ndarray,
    static_map: np.ndarray | None,
    crop_origin: tuple[int, int],
    frame_index: int,
    material_paths: Mapping[int, MaterialPathDiagnostic] | None = None,
) -> dict[str, object]:
    """Measure every Oil candidate, including rejected ones, without mutation.

    Five fixed sectors and four bands bound each candidate's trace size. Row
    prefix sums are frame-local and discarded after this call. Missing bands,
    nonfinite samples and absent static maps are explicit, not measured zero.
    """
    shape = gray.shape
    if gray.ndim != 2 or any(
        array.shape != shape for array in (effective_mask, glare_mask, material_map)
    ) or (static_map is not None and static_map.shape != shape):
        raise ValueError("Interface diagnostic rasters must share one 2D crop.")
    height, width = shape
    band = max(3, min(12, int(round(height * 0.01))))
    visible = (effective_mask > 0) & (glare_mask == 0) & np.isfinite(gray)
    glared = (effective_mask > 0) & (glare_mask > 0)
    profiles = []
    for sector in range(5):
        start, stop = width * sector // 5, width * (sector + 1) // 5
        profiles.append(_sector_profile(gray, visible, material_map, static_map, glared, start, stop))
    profile_cache = {(profile[0], profile[1]): profile for profile in profiles}

    rows = []
    for index, candidate in enumerate(candidates):
        if candidate.kind is not BoundaryKind.OIL_AIR:
            continue
        source_y = float(candidate.y)
        local_y = source_y - crop_origin[1]
        row: dict[str, object] = {
            "candidate_input_index": index,
            "source": candidate.source,
            "canonical_y": source_y if math.isfinite(source_y) else None,
            "local_y": local_y if math.isfinite(local_y) else None,
            "rejected": candidate.rejected,
            "measurement_status": "measured",
            "sectors": [],
            "path_aligned": {"status": "unavailable", "reason": "candidate_outside_raster", "sectors": []},
        }
        if not math.isfinite(local_y) or not 0 <= local_y < height:
            row["measurement_status"] = "candidate_outside_raster"
            rows.append(row)
            continue
        # Retain exact candidate Y above; all pixel windows use this explicit center.
        center = int(math.floor(local_y + 0.5))
        row["sample_center_local_y"] = center
        sectors = []
        contrasts = []
        for sector, profile in enumerate(profiles):
            measured = _measure_sector(
                profile, sector=sector, center=center, band=band,
                local_y=local_y, crop_origin=crop_origin, height=height,
            )
            sectors.append(measured)
            if measured["near_signed_contrast"] is not None:
                contrasts.append(measured["near_signed_contrast"])

        row["path_aligned"] = _measure_native_path(
            (material_paths or {}).get(index), candidate, profile_cache,
            gray=gray, visible=visible, material_map=material_map, static_map=static_map, glared=glared,
            crop_origin=crop_origin, center=center, band=band,
        )
        row["sectors"] = sectors
        row["usable_near_sector_count"] = len(contrasts)
        row["median_near_signed_contrast"] = float(np.median(contrasts)) if contrasts else None
        if not contrasts:
            row["measurement_status"] = "insufficient_visible_pixels"
        rows.append(row)
    return {
        "schema_version": INTERFACE_DIAGNOSTICS_SCHEMA,
        "diagnostic_only": True,
        "classification": "not_evaluated",
        "source_frame_index": int(frame_index),
        "coordinate_space": "source_frame_y",
        "positive_direction": "down",
        "crop_origin": list(crop_origin),
        "crop_size": [width, height],
        "resize": False,
        "band_width_px": band,
        "edge_exclusion_px": 1,
        "sector_count": 5,
        "minimum_band_valid_fraction": 0.5,
        "minimum_band_valid_pixels": 8,
        "gray_scale": "uint8_divided_by_255",
        "material_channel": "raw_combined_material_evidence_not_final_foam",
        "static_map_available": static_map is not None,
        "edge_measurement": "central_difference_of_masked_sector_row_mean",
        "peak_tie_break": "lowest_source_y_within_search_band",
        "candidate_index_space": "detection.candidates_before_trace_score_sort",
        "oil_candidate_count": len(rows),
        "candidates": rows,
    }


def _band(prefix, start: int, stop: int, height: int, width: int) -> dict[str, object]:
    complete = 0 <= start < stop <= height and width > 0
    lo, hi = max(0, min(height, start)), max(0, min(height, stop))
    totals = {key: float(value[hi] - value[lo]) for key, value in prefix.items()}
    area = max(0, stop - start) * width
    count = totals["count"]
    fraction = count / area if area else 0.0
    usable = complete and count >= 8 and fraction >= 0.5
    mean = totals["gray"] / count if usable else None
    return {
        "local_y_range": [start, stop],
        "available": usable,
        "reason": "available" if usable else "outside_crop" if not complete else "insufficient_visible_pixels",
        "valid_fraction": fraction,
        "valid_pixel_count": int(count),
        "gray_mean": mean,
        "gray_std": math.sqrt(max(0.0, totals["gray_squared"] / count - mean * mean)) if usable else None,
        "material_available": usable and totals["material_count"] == count,
        "material_mean": totals["material"] / count if usable and totals["material_count"] == count else None,
        "static_available": usable and totals.get("static_count") == count,
        "static_overlap": totals["static"] / count if usable and totals.get("static_count") == count else None,
        "glare_fraction": totals["glare"] / area if area else None,
    }


def _difference(below: dict, above: dict) -> float | None:
    if not below["available"] or not above["available"]:
        return None
    return float(below["gray_mean"] - above["gray_mean"])


def _sector_profile(gray, visible, material_map, static_map, glared, start, stop):
    height = gray.shape[0]
    values = gray[:, start:stop].astype(np.float64) / 255.0
    valid = visible[:, start:stop]
    material = material_map[:, start:stop]
    material_valid = valid & np.isfinite(material)
    counts = valid.sum(axis=1)
    channels = {
        "count": counts,
        "gray": np.where(valid, values, 0.0).sum(axis=1),
        "gray_squared": np.where(valid, values * values, 0.0).sum(axis=1),
        "material_count": material_valid.sum(axis=1),
        "material": np.where(material_valid, material, 0.0).sum(axis=1),
        "glare": glared[:, start:stop].sum(axis=1),
    }
    if static_map is not None:
        static = static_map[:, start:stop]
        channels["static_count"] = (valid & np.isfinite(static)).sum(axis=1)
        channels["static"] = (valid & np.isfinite(static) & (static > 0)).sum(axis=1)
    prefix = {key: np.r_[0.0, np.cumsum(value)] for key, value in channels.items()}
    row_mean = np.divide(channels["gray"], counts, out=np.zeros(height), where=counts > 0)
    gradient = np.zeros(height)
    gradient_valid = np.zeros(height, dtype=bool)
    if height > 2:
        gradient[1:-1] = (row_mean[2:] - row_mean[:-2]) / 2.0
        enough = counts >= max(2, math.ceil((stop - start) * 0.5))
        gradient_valid[1:-1] = enough[2:] & enough[:-2]
    return start, stop, prefix, gradient, gradient_valid


def _measure_sector(profile, *, sector, center, band, local_y, crop_origin, height):
    start, stop, prefix, gradient, gradient_valid = profile
    bands = {
        "near_above": _band(prefix, center - band - 1, center - 1, height, stop - start),
        "near_below": _band(prefix, center + 2, center + band + 2, height, stop - start),
        "far_above": _band(prefix, center - 3 * band - 1, center - 2 * band - 1, height, stop - start),
        "far_below": _band(prefix, center + 2 * band + 2, center + 3 * band + 2, height, stop - start),
    }
    near = _difference(bands["near_below"], bands["near_above"])
    far = _difference(bands["far_below"], bands["far_above"])
    lo, hi = max(0, center - band), min(height, center + band + 1)
    eligible = np.flatnonzero(gradient_valid[lo:hi]) + lo
    peak = int(eligible[np.argmax(np.abs(gradient[eligible]))]) if eligible.size else None
    # A flat profile has no localized edge even if pixels are available.
    if peak is not None and abs(float(gradient[peak])) <= 1e-12:
        peak = None
    return {
        "sector": sector,
        "source_x_range": [start + crop_origin[0], stop + crop_origin[0]],
        "bands": bands,
        "near_signed_contrast": near,
        "far_signed_contrast": far,
        "near_minus_far_abs_contrast": None if near is None or far is None else abs(near) - abs(far),
        "peak_source_y": None if peak is None else peak + crop_origin[1],
        "peak_offset_from_candidate_px": None if peak is None else peak - local_y,
        "peak_signed_gradient": None if peak is None else float(gradient[peak]),
    }


def _measure_native_path(path, candidate, profile_cache, *, gray, visible,
                         material_map, static_map, glared, crop_origin, center, band):
    unavailable = {"status": "unavailable", "reason": "no_captured_native_path", "sectors": []}
    if path is None:
        return unavailable
    if path.candidate_source != candidate.source or path.candidate_y != float(candidate.y):
        return {**unavailable, "reason": "candidate_provenance_mismatch"}
    samples = path.evidence.diagnostic_samples
    if not samples:
        return {**unavailable, "reason": "native_path_samples_unavailable"}
    height, width = gray.shape
    # Do not repair, sort, or infer missing path members at this boundary.
    if (len(samples) > 5 or len({s.sector_index for s in samples}) != len(samples)
        or any(not (0 <= s.sector_index < 5 and 0 <= s.start_x < s.stop_x <= width
                    and 0 <= s.local_y < height) for s in samples)):
        return {**unavailable, "reason": "invalid_native_path_geometry"}
    sectors = []
    for sample in samples:
        extent = (sample.start_x, sample.stop_x)
        if extent not in profile_cache:
            profile_cache[extent] = _sector_profile(
                gray, visible, material_map, static_map, glared, *extent,
            )
        profile = profile_cache[extent]
        measured = _measure_sector(
            profile, sector=sample.sector_index, center=sample.local_y, band=band,
            local_y=sample.local_y, crop_origin=crop_origin, height=height,
        )
        measured.update({
            "path_local_y": sample.local_y,
            "path_source_y": sample.local_y + crop_origin[1],
            "generator_strength": sample.strength,
            "generator_signed_contrast": sample.signed_contrast,
            "generator_contrast_channel": sample.contrast_channel,
            "generator_contrast_scale_px": sample.contrast_scale_px,
            "candidate_center_on_same_sector": _measure_sector(
                profile, sector=sample.sector_index, center=center, band=band,
                local_y=float(candidate.y) - crop_origin[1], crop_origin=crop_origin, height=height,
            ),
        })
        # The shared measurement helper's offset is relative to its sampling center.
        measured["peak_offset_from_path_px"] = measured.pop("peak_offset_from_candidate_px")
        sectors.append(measured)
    usable = sum(s["near_signed_contrast"] is not None for s in sectors)
    return {
        "status": "measured" if usable else "insufficient_visible_pixels",
        "reason": "native_generator_path",
        "geometry_source": "material_path_generation",
        "classification": "not_evaluated",
        "independent_support": "not_evaluated",
        "sector_grid": "effective_mask_x_extent_rounded_fifths",
        "generator_gray_channel": "pre.blurred",
        "measurement_gray_channel": "pre.gray_uint8_divided_by_255",
        "shared_derivation": ["current_frame_gray", "sobel_from_blurred_gray"]
            + (["raw_combined_material_evidence"] if candidate.source == "material_path" else []),
        "generator_strength_formula": "clip(0.78*max_multiscale_contrast_score+0.22*sobel_score,0,1)",
        "edge_exclusion_reference": "native_path_row_not_certified_physical_edge",
        "usable_near_sector_count": usable,
        "sectors": sectors,
    }
