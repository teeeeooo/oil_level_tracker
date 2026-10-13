"""Offline NSR G0 binding/readiness; no classifier, new edge or physical label.

CR1's saved-score envelope cannot describe native fragments and weak source
constraints. Reuse its identity/review checks and the existing lossless geometry
owners here. Output references reconstruct support without copying image banks.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_contextual_role_preflight as cr1
from tests.diagnostics import s11_contour_contact_probe as contours
from tests.diagnostics import s11_foam_material_sides as material
from tests.diagnostics import s11_foam_support_geometry as faces
from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics.s11_resolver_replacement_profile import peak_rss

SCHEMA = "s11-native-role-preflight-v1"
SIDE_OFFSETS = {"upper": list(range(-12, -1)), "lower": list(range(2, 13))}
DEPENDENCIES = {
    "saved_rgb_point": {
        "operation": "identity of one saved RGB pixel; no feature/head executed",
        "footprint": [[0, 0]], "normalization": None, "padding": None,
        "aggregation": None, "shared_upper_lower_pixels": 0,
        "source_scope": "Native saved RGB only; reduced pixels retain resize context, not a one-source-pixel claim.",
    },
    "saved_canny": {
        "use": "geometry only, never an independent pure-side feature",
        "upstream": "BGR-to-gray, CLAHE 8x8 tiles, Gaussian 5x5, Canny including hysteresis, effective mask",
        "source_dependency": "ROI_CONTEXT; exact active upstream dependency not captured",
        "shared_sides": "POSSIBLE; disjoint edge centers do not certify independent input",
    },
    "existing_foam_texture": {
        "use": "NOT_EXECUTED; prior values are not promoted to side-contained evidence",
        "upstream": "small/large reflected box filters over gray and saved Canny, pointwise normalization, final valid mask",
        "source_dependency": "Canny/CLAHE/hysteresis context and reflected padding precede output masking",
        "shared_sides": "POSSIBLE; center visibility does not certify dependency containment",
    },
    "proposed_role_head": {
        "status": "NOT_ADOPTED", "complete_dependency": "UNSPECIFIED",
        "limit": "Three 3x3 stride-one convolutions alone have a 7x7 local field; preprocessing/normalization/aggregation may enlarge it.",
    },
}


def pinned_path(root, entry):
    rel = Path(entry["path"])
    o2.require(not rel.is_absolute() and ".." not in rel.parts, "input must be repository relative")
    path = root / rel
    o2.require(path.resolve().is_relative_to(root.resolve()), "input escapes repository")
    o2.require(o2.sha256_file(path) == entry["sha256"], f"input hash mismatch: {rel}")
    return path


def resolve(documents, reference):
    """Bind an exact original object; list position and precision are not inferred."""
    o2.require(set(reference) == {"input", "keys", "sha256"}, "invalid reference fields")
    o2.require(reference["input"] in documents, "unknown reference input")
    value = documents[reference["input"]]
    for key in reference["keys"]:
        o2.require((isinstance(value, dict) and isinstance(key, str) and key in value)
                   or (isinstance(value, list) and type(key) is int and 0 <= key < len(value)),
                   "reference path missing")
        value = value[key]
    o2.require(o2.fingerprint_json(value) == reference["sha256"], "referenced subject changed")
    return value


def membership(visible, columns, offsets, *, requested_columns=25):
    """Exact point dependencies on observed path columns; never bridge a gap.

    columns are explicit (x, y) samples in the captured raster. Missing columns
    stay censored. A visible point is geometric support, not material purity.
    """
    o2.require(len({x for x, _ in columns}) == len(columns), "ambiguous path column")
    h, w = visible.shape
    observed = cropped = masked = 0
    for x, y in columns:
        for dy in offsets:
            if not (0 <= x < w and 0 <= y + dy < h):
                cropped += 1
            elif not visible[y + dy, x]:
                masked += 1
            else:
                observed += 1
    missing = (requested_columns - len(columns)) * len(offsets)
    o2.require(missing >= 0, "support exceeds declared columns")
    return {"requested": requested_columns * len(offsets), "observed": observed,
            "censored_crop": cropped, "censored_mask": masked, "missing_path": missing,
            "status": "COMPLETE" if not (cropped + masked + missing) else "PARTIAL_OR_UNAVAILABLE"}


def fragment_binding(graph, fragment_id, column, row, visible):
    ids = graph["fragments"][fragment_id]
    xy = graph["vertices_xy"][ids]
    kind = graph["fragment_kinds"][fragment_id]
    dx = np.diff(xy[:, 0])
    monotone = len(xy) > 1 and (bool(np.all(dx == 1)) or bool(np.all(dx == -1)))
    # A junction endpoint does not determine which outgoing arm is the boundary.
    junction = bool(np.any(graph["degree"][ids] > 2))
    orientation = "X_MONOTONE_PARTIAL_PATH" if monotone else "UNRESOLVED_VERTICAL_CYCLE_OR_TURN"
    columns = [(int(x), int(y)) for x, y in xy if abs(int(x) - column) <= 12] if monotone else []
    return {"fragment_id": fragment_id, "vertex_count": len(ids), "kind": kind,
            "path_sha256": o2.fingerprint_json(xy.tolist()),
            "fixed_column_rows": sorted({int(y) for x, y in xy if x == column}),
            "orientation": orientation, "junction_incident": junction,
            "crop_adjacent": bool(graph["crop_adjacent"][ids].any()),
            "mask_adjacent": bool(graph["unavailable_adjacent"][ids].any()),
            "support_columns_xy": columns,
            "side_support": {side: membership(visible, columns, offsets)
                             for side, offsets in SIDE_OFFSETS.items()},
            "physical_orientation": "NOT_QUALIFIED", "candidate_positive": False}


def shared_support(paths, visible):
    """Count actual reused pixels across alternative views, not independent votes."""
    h, w = visible.shape
    unions = {side: set() for side in SIDE_OFFSETS}
    totals = Counter()
    for path in paths:
        for side, offsets in SIDE_OFFSETS.items():
            pixels = {(x, y + dy) for x, y in path["support_columns_xy"] for dy in offsets
                      if 0 <= x < w and 0 <= y + dy < h and visible[y + dy, x]}
            unions[side].update(pixels)
            totals[side] += len(pixels)
    return {"observed_union": {s: len(v) for s, v in unions.items()},
            "reused_within_side": {s: totals[s] - len(unions[s]) for s in unions},
            "shared_upper_lower_pixels": len(unions["upper"] & unions["lower"]),
            "independent_votes": False}


def edge_bindings(edges, visible, column, rgb_available):
    """Retain every center edge and every incident fragment, including junctions."""
    graph = contours.measure_edge_fragments(edges, visible)
    by_vertex = defaultdict(list)
    for fid, vertices in enumerate(graph["fragments"]):
        for vertex in set(vertices):
            if graph["vertices_xy"][vertex, 0] == column:
                by_vertex[vertex].append(fid)
    rows = []
    for vid, (x, y) in enumerate(graph["vertices_xy"]):
        if x != column:
            continue
        y = int(y)
        columns = [(column + dx, y) for dx in range(-12, 13)]
        context = {side: membership(visible, columns, offsets)
                   for side, offsets in SIDE_OFFSETS.items()}
        legacy = material.side_support(visible, (column, y))
        o2.require({s: v["observed"] for s, v in context.items()} == legacy["visible_pixels"],
                   "fixed context support changed")
        paths = [fragment_binding(graph, fid, column, y, visible) for fid in by_vertex[vid]]
        rows.append({"row": y, "vertex_id": vid, "degree": int(graph["degree"][vid]),
                     "incident_fragments": paths, "shared_path_support": shared_support(paths, visible),
                     "vertical_context": context,
                     "context_membership": {"columns": [column - 12, column + 13], "center_y": y},
                     "rgb_status": "AVAILABLE" if rgb_available else "UNAVAILABLE_SAVED_RGB",
                     "legacy_rl_support_status": legacy["status"] if rgb_available else "UNAVAILABLE_SAVED_RGB",
                     "physical_role": "UNREVIEWED", "decision": "NOT_EVALUATED"})
    return rows, {"vertices": len(graph["vertices_xy"]), "links": len(graph["links"]),
                  "fragments": len(graph["fragments"]), "spec_id": contours.FRAGMENT_SPEC["id"]}


def load_edges_labels(root, case, binding):
    """Use captured rasters only. Extra labels require equal captured geometry."""
    labels = None
    if case["kind"] == "default_images":
        with Image.open(root / case["images"]["canny"]) as image:
            edges = np.asarray(image) > 0
    else:
        path = case.get("graph", case.get("stage", case["raster"]))
        with np.load(root / path, allow_pickle=False) as archive:
            edges = archive["edges"].astype(bool) if "edges" in archive else archive["canny"] > 0
        with np.load(root / case["raster"], allow_pickle=False) as archive:
            key = "labels" if "labels" in archive else "foam_component_labels"
            if key in archive:
                labels = archive[key].copy()
    if binding.get("labels") is not None:
        o2.require(case["kind"] == "default_images", "extra labels require captured-image case")
        extra = binding["labels"]
        o2.require(set(extra["equivalent_images"]) == {"canny", "effective_mask", "glare_mask"},
                   "extra labels need complete saved geometry equivalence")
        for key, path in extra["equivalent_images"].items():
            with Image.open(root / path) as a, Image.open(root / case["images"][key]) as b:
                o2.require(np.array_equal(np.asarray(a), np.asarray(b)), "label/capture geometry mismatch")
        with Image.open(root / extra["path"]) as image:
            labels = np.asarray(image).astype(np.uint16)
    return edges, labels


def center_faces(labels, visible, column):
    if labels is None:
        return {"status": "UNAVAILABLE_SAVED_LABELS", "faces": []}
    result = faces.measure_boundary_faces(labels, visible)
    a, b = result["start_xy2"], result["end_xy2"]
    chosen = np.flatnonzero((a[:, 1] == b[:, 1]) & (np.minimum(a[:, 0], b[:, 0]) <= 2 * column)
                            & (2 * column <= np.maximum(a[:, 0], b[:, 0])))
    rows = [{"face_id": int(i), "raster_y": float(a[i, 1] / 2),
             "inside_label": int(result["inside_label"][i]),
             "outside_label": int(result["outside_label"][i]),
             "status": result["status_names"][int(result["status"][i])],
             "outward_normal_xy": result["outward_normal_xy"][i].tolist()} for i in chosen]
    return {"status": "CAPTURED_APPEARANCE_ONLY", "spec_id": faces.BOUNDARY_SPEC["id"],
            "total_faces": len(a), "faces": rows,
            "physical_identity": "UNRESOLVED", "zero_label": "OUTSIDE_RETAINED_SUPPORT_NOT_AIR"}


def weak_constraints(plan, cases):
    """A hit of cardinality zero, one or many never supplies correspondence."""
    results = []
    for original in plan["evaluation_only"]["qualified_intervals"]:
        case = cases[original["case_id"]]
        low, high = o2.interval(original["interval"], "reviewed interval")
        hits = [r["row"] for r in case["rows"] if low <= r["source_xy"][1] <= high]
        face_hits = [f["face_id"] for f in case["component_faces"]["faces"]
                     if low <= f["source_y"] <= high and f["status"].startswith("VISIBLE")]
        results.append({"original": original, "unit": "SOURCE_CONTAINMENT_INTERVAL",
                        "compatible_edge_rows": hits, "compatible_face_ids": face_hits,
                        "candidate_positive_ids": [], "candidate_negative_ids": [],
                        "correspondence": "NOT_QUALIFIED", "decision": "NOT_EVALUATED"})
    for original in plan["evaluation_only"]["guides"]:
        case_id = f"s4-f{original['frame']}"
        case = cases[case_id]
        hits = [r["row"] for r in case["rows"] if r["source_xy"] == original["source_xy"]]
        results.append({"original": original, "case_id": case_id, "unit": "SCOPED_SOURCE_GUIDE",
                        "exact_edge_rows": hits, "nearest_edge_used": False,
                        "correspondence": "GEOMETRIC_ONLY" if hits else "NO_EXACT_EDGE",
                        "candidate_positive_ids": [], "candidate_negative_ids": [],
                        "decision": "NOT_EVALUATED"})
    return results


def oil_bindings(root, baseline, qualification):
    """Reuse exact A1/O1 bindings; do not inflate pooled sectors into pixel paths."""
    captures = {}
    overrides = {r["query_id"]: r for r in qualification["overrides"]}
    rows = []
    for index, row in enumerate(baseline["rows"]):
        native = row["native_support"]
        query = row["query"]
        path = None
        witness_ref = native.get("oil_interface_witness", {})
        if "path" in witness_ref:
            capture_path = witness_ref["path"]
            if capture_path not in captures:
                captures[capture_path] = o2.read_json(root / capture_path)
            capture = captures[capture_path]
            witness = capture["state"]["oil_interface_witness"]
            o2.require(witness["source_frame_index"] == query["frame"]
                       and witness["glass_id"] == row["glass_id"], "witness frame/Glass mismatch")
            j = int(witness_ref["pointer"].rsplit("/", 1)[1])
            subject = witness["candidates"][j]
            o2.require(o2.fingerprint_json(subject) == witness_ref["sha256"], "witness changed")
            o2.require(subject["candidate_input_index"] == query["candidate_index"], "candidate index mismatch")
            samples = [{"sector": s["sector"], "source_x_range": s["source_x_range"],
                        "path_source_y": s["path_source_y"]} for s in subject["sectors"]]
            path = {"status": subject["contour"]["native_path_reason"], "representation": "POOLED_SECTOR_SAMPLES",
                    "samples": samples, "support": witness_ref,
                    "actual_membership": "O1 band bounds/counts retained at reference; per-pixel membership not serialized",
                    "complete_feature_dependency": "NOT_CAPTURED; legacy feature means are not pure-side observations"}
        override = overrides.get(query["id"], {})
        rows.append({"query": query, "baseline_pointer": f"/rows/{index}", "time_sec": row["time_sec"],
                     "time_status": row["time_status"], "glass_id": row["glass_id"],
                     "native_support": native, "path": path, "exposure": row["exposure"],
                     "physical_qualification": override.get("facets", {}).get("physical", {}).get("status", "HISTORICAL_ONLY"),
                     "practical_acceptance": override.get("facets", {}).get("practical", {}).get("status", "NOT_REVIEWED"),
                     "decision": "NOT_EVALUATED", "training_label_created": False})
    return rows


def audit(root, manifest):
    started = time.monotonic()
    o2.require(manifest["schema"] == SCHEMA, "unsupported native preflight schema")
    o2.require(manifest["dependencies"] == DEPENDENCIES, "dependency contract changed")
    o2.require(manifest["side_offsets"] == SIDE_OFFSETS, "side support changed")
    docs = {name: cr1.read_pinned(root, entry) for name, entry in manifest["inputs"].items()}
    o2.unique(manifest["artifacts"], "path", "artifact pins")
    for entry in manifest["artifacts"]:
        pinned_path(root, entry)
    pinned = {e["path"] for e in manifest["artifacts"]}
    plan = docs["foam_preflight"]
    # Reuses all 142 frozen input/source pins and reference-footprint verification;
    # validate() never imports or runs the encoder used by the closed R/L trial.
    loaded, references = material.validate(plan, root)
    baseline = cr1.audit(root, docs["oil_manifest"])
    qualification = cr1.qualify_reviews(root, baseline, docs["oil_review_manifest"])
    cases = o2.unique(plan["cases"], "id", "original contexts")
    bindings = o2.unique(manifest["bindings"], "id", "native bindings")
    o2.require(list(bindings) == list(cases), "complete original context roster/order required")
    o2.require(len(cases) <= manifest["resources"]["max_cases"], "context budget exceeded")
    output = []
    for cid, case in cases.items():
        o2.require(time.monotonic() - started <= manifest["resources"].get("seconds_limit", 180),
                   "readiness time budget exceeded; no partial prefix output")
        binding = bindings[cid]
        o2.require(o2.fingerprint_json(case) == binding["case_sha256"], "case/frame/geometry changed")
        o2.require(binding["source_recording"] in manifest["artifacts"], "source recording is not pinned")
        recipe = binding["glass_recipe"]
        for key in ("recipe", "authority"):
            if key in recipe:
                resolve(docs, recipe[key])
        identity = resolve(docs, binding["identity"])
        o2.require(binding["time_key"] in (None, "time_sec", "nominal_time_sec", "timestamp_sec", "decoder_pos_msec"),
                   "unsupported timestamp field")
        o2.require(binding["time_kind"] == ("UNAVAILABLE" if binding["time_key"] is None else
                   "NOMINAL_ONLY" if binding["time_key"] == "nominal_time_sec" else
                   "DECODER_POSITION" if binding["time_key"] == "decoder_pos_msec" else "RECORDED"),
                   "timestamp precision changed")
        o2.require(identity[binding["frame_key"]] == case["frame"], "identity frame mismatch")
        if binding.get("labels"):
            extra = binding["labels"]
            o2.require({extra["path"], *extra["equivalent_images"].values()} <= pinned,
                       "unfrozen label geometry input")
            label_case = resolve(docs, extra["authority"])
            o2.require(label_case["retained_labels_path"] == extra["path"]
                       and label_case["source_identity"]["frame_index"] == case["frame"]
                       and label_case["crop_xyxy"][:2] == case["origin"]
                       and label_case["shape"] == case["shape"]
                       and all(label_case["images"][k] == v for k, v in extra["equivalent_images"].items()),
                       "label authority binding mismatch")
        rgb, visible, original_rows = loaded[cid]
        edges, labels = load_edges_labels(root, case, binding)
        o2.require(edges.shape == visible.shape and edges.dtype == bool, "edge geometry mismatch")
        rows, graph = edge_bindings(edges, visible, case["column"], rgb is not None)
        o2.require([r["row"] for r in rows] == original_rows, "original edge population changed")
        ox, oy = case["origin"]; sx, sy = case["scale_xy"]
        for r in rows:
            r["source_xy"] = [ox + (case["column"] + .5) * sx - .5, oy + (r["row"] + .5) * sy - .5]
        boundary = center_faces(labels, visible, case["column"])
        for f in boundary["faces"]:
            f["source_y"] = oy + (f["raster_y"] + .5) * sy - .5
        time_key = binding["time_key"]
        timestamp = identity[time_key] if time_key else None
        if "crop_origin" in identity:
            o2.require(identity["crop_origin"] == case["origin"], "capture origin mismatch")
        if "image_inputs" in identity:
            for name in ("canny", "effective_mask", "glare_mask"):
                o2.require(identity["image_inputs"][name]["path"] == case["images"][name],
                           "capture image/frame binding mismatch")
        if timestamp is not None:
            o2.number(timestamp, "timestamp")
            if time_key == "decoder_pos_msec":
                timestamp /= 1000
        output.append({"id": cid, "original_case_ref": {"input": "foam_preflight", "index": len(output)},
                       "identity": binding["identity"], "frame": case["frame"], "time_sec": timestamp,
                       "source_recording": binding["source_recording"],
                       "glass_recipe": binding["glass_recipe"],
                       "time_kind": binding["time_kind"], "geometry": {k: case[k] for k in ("origin", "shape", "scale_xy", "column")},
                       "geometry_sha256": o2.fingerprint_json({k: case[k] for k in ("origin", "shape", "scale_xy", "column")}),
                       "representation": "NATIVE_RASTER" if sx == sy == 1 else "REDUCED_WORKING_RASTER",
                       "exposure": case["exposure"], "graph": graph, "component_faces": boundary, "rows": rows,
                       "support_reconstruction": "Pinned case masks intersect explicit fragment columns or vertical context bounds with side_offsets; no fill or padding.",
                       "decision": "NOT_EVALUATED"})
    groups = defaultdict(list)
    for case in output:
        group = f"{case['source_recording']['sha256']}:f{case['frame']}"
        groups[group].append(case["id"])
    constraints = weak_constraints(plan, {c["id"]: c for c in output})
    opposition = []
    for reference in manifest.get("regional_opposition", []):
        unit = resolve(docs, reference)
        o2.require(unit["case_id"] in cases and unit["frame_index"] == cases[unit["case_id"]]["frame"],
                   "regional opposition frame mismatch")
        opposition.append({"reference": reference, "case_id": unit["case_id"],
                           "unit": "REVIEWED_UPPER_BAND_ONLY", "dense_pixel_labels": False,
                           "candidate_labels": [], "decision": "NOT_EVALUATED"})
    oil = oil_bindings(root, baseline, qualification)
    total = sum(len(c["rows"]) for c in output)
    o2.require(total <= manifest["resources"]["max_edges"], "edge budget exceeded")
    return {"schema": SCHEMA, "manifest_sha256": o2.fingerprint_json(manifest),
            "status": "BINDINGS_VERIFIED_ROLE_NOT_READY", "decision": "NOT_EVALUATED",
            "production_changed": False, "encoder_forwards": 0, "video_decode": False,
            "counts": {"contexts": len(output), "edges": total, "oil_records": len(oil),
                       "legacy_rl_support": dict(Counter(r["legacy_rl_support_status"] for c in output for r in c["rows"])),
                       "component_capture": dict(Counter(c["component_faces"]["status"] for c in output)),
                       "new_physical_labels": 0, "untouched_holdout_recordings": 0},
            "readiness": [
                {"capability": "saved_edge_path_and_support_binding", "status": "READY", "scope": "All scheduled edges, all incident fragments, geometric side support only"},
                {"capability": "saved_component_face_binding", "status": "READY", "scope": "Captured labels only; absent captures remain explicitly unavailable"},
                {"capability": "weak_review_and_oil_lineage_binding", "status": "READY", "scope": "Original precision, A withdrawal and B practical acceptance; no new labels"},
                {"capability": "foam_external_upper_vs_internal_transition", "status": "NOT_READY", "missing": ["qualified native-path correspondence", "observed gas/Foam sides versus real Foam/Foam transition at the same unit", "independent opposition to projected optical structure"]},
                {"capability": "oil_boundary_role", "status": "NOT_READY", "missing": ["qualified side roles on native paths", "complete feature dependencies for a selected observation", "separate calibration/evaluation scope"]},
                {"capability": "train_or_production_consume", "status": "NOT_READY", "missing": ["selected and adopted observation/training plan", "qualified G1 usefulness", "O2/V5 and behavior acceptance"]}],
            "same_source_frame_views": dict(groups),
            "dependencies": DEPENDENCIES, "side_offsets": SIDE_OFFSETS,
            "reference_units": [{"original": ref, "unit": "REGIONAL_APPEARANCE", "independent_units": 1,
                                 "dense_pixel_labels": False, "boundary_correspondence": "NOT_QUALIFIED"}
                                for ref, _, _ in references.values()],
            "regional_opposition": opposition,
            "weak_constraints": constraints, "contexts": output, "oil_rows": oil,
            "p0_roster": docs["oil_manifest"]["inputs"]["scene_roster"],
            "p0_obligations": baseline["scene_claims"],
            "scope": "Development binding feasibility; no physical prediction, retried R/L score, classifier or field acceptance."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    manifest = o2.read_json(args.manifest)
    cv2.setNumThreads(2)
    started = time.monotonic()
    result = audit(args.root.resolve(), manifest)
    elapsed = time.monotonic() - started
    memory = peak_rss()
    o2.require(elapsed <= manifest["resources"].get("seconds_limit", 180), "readiness time budget exceeded")
    if memory["bytes"] is not None:
        o2.require(memory["bytes"] <= manifest["resources"].get("peak_rss_bytes_limit", 800000000),
                   "readiness memory budget exceeded")
    raw = (json.dumps(result, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    o2.require(len(raw) <= manifest["resources"]["max_output_bytes"], "output exceeds budget")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(gzip.compress(raw, mtime=0) if args.output.suffix == ".gz" else raw)
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "elapsed_seconds": elapsed, "peak_rss": memory, "output_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
