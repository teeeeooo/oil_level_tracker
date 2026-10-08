"""Bounded reference-versus-measurement diagnostics, never matcher authority.

Current generators expose sampling footprints, not candidate-owned observed
edges. Spatial overlap below therefore has no physical identity semantics.
"""
from __future__ import annotations

import hashlib
import json
import math

import cv2
import numpy as np

from oil_tracker.domain.artifact_reference import MAX_REFERENCES_PER_GLASS, fingerprint, geometry_fingerprint
from oil_tracker.domain.enums import BoundaryKind
from .artifact_reference import decode_reference, reference_preprocessing, reviewed_edge_mask

SCHEMA = "s11-reference-measurement-comparison-v1"
MAX_CANDIDATES = 128
MAX_PAIRS = 512
MAX_DOMAIN_PIXELS = 8_388_608
MAX_RECORD_BYTES = 1_048_576


def _digest(array):
    if array.flags.c_contiguous:
        return hashlib.sha256(array).hexdigest()
    digest = hashlib.sha256()
    for row in array:
        digest.update(np.ascontiguousarray(row))
    return digest.hexdigest()


def _footprint(candidate, index, *, lineage, paths, crop_origin, shape):
    """Describe only actual available contrast operations, not all score inputs."""
    ox, oy = crop_origin
    height, width = shape
    result = {"candidate_input_index": index, "source": candidate.source,
              "kind": candidate.kind.value, "source_y": float(candidate.y),
              "basis": "unavailable", "reason": "no_captured_contrast_footprint",
              "observed_raw_edge": "unavailable", "windows": [],
              "omitted_operations": 0, "complete_score_dependency_mask": False}
    windows = result["windows"]
    if not math.isfinite(float(candidate.y)):
        result.update(source_y=None, reason="nonfinite_candidate_y")
        return result
    if candidate.source == "phase_transition_scan":
        record = lineage.get(index)
        if record is None or record["status"] != "measured":
            return result
        if record["source"] != candidate.source or record["source_y"] != candidate.y:
            raise ValueError("Reference diagnostic lineage binding mismatch.")
        rows = record["phase_support"]
        if len(rows) != 15:
            raise ValueError("Phase contrast requires its bounded 15 operation records.")
        for row in rows:
            if not row["pooled_available"]:
                result["omitted_operations"] += 1
                continue
            x0, x1 = row["source_x_range"]
            for side in ("upper", "lower"):
                y0, y1 = row[f"{side}_source_y_range"]
                windows.append([x0, y0, x1, y1])
        result["operation"] = "available_phase_pooled_contrast"
    elif candidate.source in {"material_path", "raster_material_path"}:
        binding = paths.get(index)
        if binding is None:
            return result
        if binding.candidate_source != candidate.source or binding.candidate_y != candidate.y:
            raise ValueError("Reference diagnostic native path binding mismatch.")
        samples = binding.evidence.diagnostic_samples
        if len(samples) > 5:
            raise ValueError("Native contrast exceeds five sectors.")
        for sample in samples:
            scale, y = sample.contrast_scale_px, sample.local_y
            if sample.contrast_channel == "unavailable":
                result["omitted_operations"] += 1
                continue
            if (scale not in (3, 6, 10) or not 0 <= y < height
                    or sample.contrast_channel not in {"blurred_gray_dynamic_range", "raw_combined_material"}):
                raise ValueError("Invalid native contrast operation.")
            # Exact intervals used by oil_material_path._window_mean. These
            # omit the separate Sobel term and nonlocal normalization context.
            for y0, y1 in ((max(0, y-scale), y), (y+1, min(height, y+scale+1))):
                if y1 > y0:
                    windows.append([ox+sample.start_x, oy+y0, ox+sample.stop_x, oy+y1])
        result["operation"] = "winning_native_contrast_only"
    for x0, y0, x1, y1 in windows:
        if (any(type(v) is not int for v in (x0, y0, x1, y1))
                or not ox <= x0 < x1 <= ox+width or not oy <= y0 < y1 <= oy+height):
            raise ValueError("Contrast footprint outside its source crop.")
    if windows:
        result.update(basis="native_measurement_footprint", reason="recorded_sampling_windows")
    result["measurement_sha256"] = fingerprint(result)
    return result


def _reference_domain(reference, glass, template, frame_size, preprocessing):
    status = reference.correspondence_status(glass, *frame_size, template)
    if status != "bound_reference":
        return status, None
    snapshot, images = decode_reference(reference)
    if (snapshot["preprocessing_sha256"] != fingerprint(snapshot["preprocessing"])
            or snapshot["preprocessing"] != preprocessing):
        return "preprocessing_mismatch", None
    if reference.review_state != "reviewed_support":
        return "reviewed_reference_unavailable", None
    if reference.review_rect is None or any(type(v) is not int for v in reference.review_rect):
        return "reference_unavailable", None
    x, y = snapshot["crop_origin"]
    w, h = snapshot["crop_size"]
    if (any(type(v) is not int for v in (x, y, w, h))
            or not 0 <= x < x+w <= frame_size[0] or not 0 <= y < y+h <= frame_size[1]):
        return "reference_outside_frame", None
    edges = reviewed_edge_mask(images, reference.review_rect)
    scope = np.zeros_like(edges)
    rx, ry, rw, rh = reference.review_rect
    scope[ry:ry+rh, rx:rx+rw] = True
    eligible = scope & (images["effective_mask"] > 0) & (images["glare_mask"] == 0)
    return "available", (snapshot, edges, eligible)


def compare_reference_measurements(*, frame, glass, detection, pre, bundle, lineage, material_paths):
    """Frame-local, debug-only, without retained caches or input mutation.

All resource exhaustion is explicit and all-or-none, never order-dependent
truncation. Missing/corrupt references or lineage do not change detection.
"""
    candidates = [(i, c) for i, c in enumerate(detection.candidates) if c.kind is BoundaryKind.OIL_AIR]
    templates = glass.geometry.artifact_templates
    result = {"schema_version": SCHEMA, "diagnostic_only": True, "decision": "NOT_EVALUATED",
              "physical_identity": "NOT_EVALUATED", "target_role": "NOT_EVALUATED",
              "path_identity": "NOT_EVALUATED", "scalar_eligibility": "NOT_EVALUATED",
              "optical_visibility": "NOT_ESTABLISHED", "source_frame_index": detection.frame_index,
              "time_sec": detection.time_sec, "glass_id": glass.id,
              "candidate_index_space": "detection.candidates_before_trace_score_sort",
              "coordinate_space": "source_frame_xy_half_open",
              "candidate_count": len(candidates), "reference_count": len(templates),
              "status": "unavailable", "reason": "no_registered_templates",
              "candidates": [], "references": []}
    if not templates:
        return result
    if (len(templates) > MAX_REFERENCES_PER_GLASS or len(candidates) > MAX_CANDIDATES
            or len(templates) * len(candidates) > MAX_PAIRS):
        result["reason"] = "resource_limit"
        return result
    try:
        if (pre.gray.ndim != 2 or pre.gray.shape != bundle.effective_mask.shape
                or pre.gray.shape != pre.glare_mask.shape):
            raise ValueError("Current rasters must share one crop.")
        ox, oy = bundle.crop_origin
        h, w = pre.gray.shape
        if (any(type(v) is not int for v in (ox, oy)) or ox < 0 or oy < 0
                or ox+w > frame.shape[1] or oy+h > frame.shape[0]):
            raise ValueError("Current crop outside source frame.")
        if (lineage["source_frame_index"] != detection.frame_index or lineage["glass_id"] != glass.id
                or tuple(lineage["crop_origin"]) != tuple(bundle.crop_origin)
                or lineage["candidate_index_space"] != result["candidate_index_space"]):
            raise ValueError("Lineage frame/context mismatch.")
        bindings = {r["candidate_input_index"]: r for r in lineage["candidates"]}
        if len(bindings) != len(lineage["candidates"]):
            raise ValueError("Duplicate lineage indices.")
        measurements = [_footprint(c, i, lineage=bindings, paths=material_paths,
                                  crop_origin=bundle.crop_origin, shape=pre.gray.shape) for i, c in candidates]
        result["candidates"] = measurements
        preprocessing = reference_preprocessing(glass)
        result["current_input_sha256"] = fingerprint({"frame": _digest(frame),
            "frame_index": detection.frame_index, "time_sec": detection.time_sec, "glass_id": glass.id,
            "geometry": geometry_fingerprint(glass),
            "effective": _digest(bundle.effective_mask), "glare": _digest(pre.glare_mask),
            "crop_origin": list(bundle.crop_origin), "preprocessing": preprocessing,
            "measurements": measurements, "version": SCHEMA})
        pixel_work = 0
        for template in templates:
            reference = template.support_reference
            item = {"template_id": template.id, "status": "unavailable", "reason": "geometry_only",
                    "edge_overlap": None, "candidates": []}
            result["references"].append(item)
            if reference is None:
                continue
            item.update(reference_snapshot_sha256=reference.snapshot_sha256,
                        review_state=reference.review_state, review_rect=reference.review_rect)
            try:
                reason, domain = _reference_domain(reference, glass, template, [frame.shape[1], frame.shape[0]], preprocessing)
            except (KeyError, TypeError, ValueError, OverflowError, cv2.error):
                reason, domain = "reference_unavailable", None
            if domain is None:
                item["reason"] = reason
                continue
            snapshot, edges, eligible = domain
            rx, ry = snapshot["crop_origin"]
            rh, rw = edges.shape
            pixel_work += rw * rh * len(measurements)
            if pixel_work > MAX_DOMAIN_PIXELS:
                result.update(status="unavailable", reason="resource_limit", references=[], candidates=[])
                return result
            common = np.zeros_like(edges)
            x0, y0, x1, y1 = max(rx, ox), max(ry, oy), min(rx+rw, ox+w), min(ry+rh, oy+h)
            if x1 > x0 and y1 > y0:
                common[y0-ry:y1-ry, x0-rx:x1-rx] = (
                    (bundle.effective_mask[y0-oy:y1-oy, x0-ox:x1-ox] > 0)
                    & (pre.glare_mask[y0-oy:y1-oy, x0-ox:x1-ox] == 0))
            common &= eligible
            usable_edges = edges & common
            edge_count = int(usable_edges.sum())
            item.update(status="recorded", reason="measurement_footprints_only",
                        reference_edge_count=int(edges.sum()), reference_edges_in_common=edge_count,
                        common_sampling_pixels=int(common.sum()),
                        reference_edges_unavailable=int((edges & ~common).sum()))
            item["comparison_sha256"] = fingerprint({"input": result["current_input_sha256"],
                "snapshot": reference.snapshot_sha256, "review_state": reference.review_state,
                "review_rect": reference.review_rect, "geometry": snapshot["geometry_sha256"]})
            for measurement in measurements:
                row = {"candidate_input_index": measurement["candidate_input_index"],
                       "basis": measurement["basis"], "statistics": None, "reason": measurement["reason"]}
                item["candidates"].append(row)
                if measurement["basis"] == "unavailable" or not common.any():
                    if not common.any():
                        row["reason"] = "no_common_sampling_domain"
                    continue
                footprint = np.zeros_like(edges)
                for wx0, wy0, wx1, wy1 in measurement["windows"]:
                    a, b, c, d = max(rx, wx0), max(ry, wy0), min(rx+rw, wx1), min(ry+rh, wy1)
                    if c > a and d > b:
                        footprint[b-ry:d-ry, a-rx:c-rx] = True
                footprint &= common
                sampled = int((usable_edges & footprint).sum())
                row["statistics"] = {"measurement_pixels_in_common": int(footprint.sum()),
                    "reference_edges_sampled": sampled, "reference_edges_not_sampled": edge_count-sampled,
                    "reference_sampling_fraction": sampled/edge_count if edge_count else None}
        result.update(status="recorded", reason="diagnostic_only", compared_domain_pixel_budget_used=pixel_work)
        if len(json.dumps(result, allow_nan=False).encode()) > MAX_RECORD_BYTES:
            result.update(status="unavailable", reason="record_size_limit", references=[], candidates=[])
    except (KeyError, TypeError, ValueError, OverflowError):
        result.update(status="unavailable", reason="invalid_measurement_input", candidates=[], references=[])
    return result
