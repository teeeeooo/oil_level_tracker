"""Bind new path-role replies to frozen G0; audit proposed RGB context, no ML.

CR1's qualifier only withdraws candidate truth or records approximations. This
supplement qualifies newly reviewed native fragments without changing that
contract, the G0 snapshot, or any production consumer. Reuse G0/O2 pin helpers.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_preflight as g0

o2 = g0.o2
SCHEMA = "s11-native-fragment-role-reply-v1"
ROLES = {
    "EXTERNAL_FOAM_UPPER": "EXTERNAL_SURFACE",
    "OSCILLATING_LIQUID_UPPER": "EXTERNAL_SURFACE",
    "INTERNAL_FOAM_CHANGE": "INTERNAL_FOAM_CHANGE",
}
# A proposed operation, not a fitted model or a new G0 support definition.
CONTEXT = {"kernel": 7, "side_centers_dy": {"upper": -5, "lower": 5},
           "columns": "existing G0 observed columns within fixed-X +/-12",
           "preprocessing": "saved native RGB / 255; no resize, CLAHE or image normalization",
           "padding": "NONE", "required": "all 49 RGB pixels visible per patch",
           "aggregation": "mean per side, one loss per fragment; patch count is not a model feature",
           "semantics": "ordered geometric context, NOT pure material labels"}


def read_pin(root, entry):
    g0.pinned_path(root, entry)  # Also rejects symlink escape.
    return g0.cr1.read_pinned(root, entry)


def by_id(rows, name):
    result = {r["id"]: r for r in rows}
    o2.require(len(result) == len(rows), f"duplicate {name}")
    return result


def context_support(visible, columns, path):
    """Complete 7x7 footprints; partial paths do not require invented columns.

    Count dependency sharing and path-side crossings, including outside the
    reviewed path's X extent. The operation may use this context but cannot call
    it an independently qualified pure-material observation.
    """
    height, width = visible.shape
    o2.require(len({x for x, _ in columns}) == len(columns), "ambiguous columns")
    path_y = dict(path)
    o2.require(len(path_y) == len(path), "nonmonotone reviewed path")
    sides, unions = {}, {}
    for side, dy in CONTEXT["side_centers_dy"].items():
        centers, union, rejected = [], set(), Counter()
        for x, y in columns:
            cy = y + dy
            footprint = {(px, py) for px in range(x-3, x+4) for py in range(cy-3, cy+4)}
            if any(not (0 <= px < width and 0 <= py < height) for px, py in footprint):
                rejected["crop"] += 1
            elif any(not visible[py, px] for px, py in footprint):
                rejected["mask"] += 1
            else:
                centers.append([x, cy]); union.update(footprint)
        crosses = sum(px in path_y and (py >= path_y[px] if side == "upper" else py <= path_y[px])
                      for px, py in union)
        sides[side] = {"requested_patches": len(columns), "complete_centers_xy": centers,
                       "complete_patches": len(centers), "censored_crop_patches": rejected["crop"],
                       "censored_mask_patches": rejected["mask"], "dependency_union_pixels": len(union),
                       "reused_pixel_uses": len(centers)*49-len(union),
                       "crossing_or_touching_path_pixels": crosses,
                       "outside_reviewed_path_columns": sum(px not in path_y for px, _ in union)}
        unions[side] = union
    return {"status": "AVAILABLE_PARTIAL_CONTEXT" if all(unions.values()) else "UNAVAILABLE_SIDE_CONTEXT",
            "sides": sides, "shared_upper_lower_pixels": len(unions["upper"] & unions["lower"]),
            "pure_material_truth": False}, unions["upper"] | unions["lower"]


def qualify(root, reply):
    o2.require(set(reply) == {"schema", "proposal", "display", "response_ko", "answers"},
               "invalid reply fields")
    o2.require(reply["schema"] == SCHEMA, "unsupported reply schema")
    o2.text(reply["response_ko"], "verbatim response")
    proposal = read_pin(root, reply["proposal"])
    g0.pinned_path(root, reply["display"])
    o2.require(proposal["schema"] == "s11-native-fragment-role-review-proposal-v1", "unsupported proposal")
    manifest = read_pin(root, proposal["g0_manifest"])
    baseline = read_pin(root, proposal["g0_readout"])
    o2.require(baseline["schema"] == g0.SCHEMA and baseline["manifest_sha256"] == o2.fingerprint_json(manifest),
               "G0 manifest/readout mismatch")
    subjects = by_id(proposal["subjects"], "subject")
    answers = by_id(reply["answers"], "answer")
    contexts = by_id(baseline["contexts"], "context")
    views = by_id(proposal["views"], "view")
    o2.require(set(answers) == set(subjects), "reply must account for each displayed subject")
    plan = read_pin(root, manifest["inputs"]["foam_preflight"])
    outputs, loaded, pixels = [], {}, {}
    for sid, subject in subjects.items():
        answer = answers[sid]
        o2.require(set(answer) == {"id", "subject_sha256", "statement_ko", "allowed_interpretations", "scope"},
                   "invalid answer fields")
        o2.require(answer["subject_sha256"] == o2.fingerprint_json(subject), "review subject changed")
        o2.require(answer["scope"] == "DISPLAYED_FRAGMENT_ROLE_ONLY", "unsupported review precision")
        o2.text(answer["statement_ko"], "subject statement")
        o2.require(answer["statement_ko"] in reply["response_ko"], "statement absent from response")
        roles = answer["allowed_interpretations"]
        o2.require(isinstance(roles, list) and roles and len(roles) == len(set(roles)) and set(roles) <= ROLES.keys(),
                   "unsupported or duplicate role")
        labels = {ROLES[r] for r in roles}
        o2.require(len(labels) == 1, "ambiguous surface/internal target")
        context = contexts[subject["case_id"]]
        o2.require(subject["frame"] == context["frame"], "review frame mismatch")
        geometry = context["geometry"]
        o2.require(geometry["scale_xy"] == [1, 1], "only native input is proposed")
        ox, oy = geometry["origin"]
        path = [(x-ox, y-oy) for x, y in subject["source_path_xy"]]
        o2.require(all(type(x) is int and type(y) is int for x, y in path), "noninteger native path")
        rows = [(ri, r) for ri, r in enumerate(context["rows"]) if r["source_xy"] == subject["fixed_column_xy"]]
        o2.require(len(rows) == 1, "missing or ambiguous exact center edge")
        ri, row = rows[0]
        matches = [(pi, p) for pi, p in enumerate(row["incident_fragments"])
                   if p["fragment_id"] == subject["native_fragment_id"]]
        o2.require(len(matches) == 1, "missing or ambiguous fragment")
        pi, fragment = matches[0]
        o2.require(o2.fingerprint_json(fragment) == subject["readout_subject_sha256"], "G0 fragment changed")
        o2.require(o2.fingerprint_json(path) == subject["raster_path_sha256"] == fragment["path_sha256"],
                   "native path geometry changed")
        o2.require(len(path) == subject["vertex_count"] == fragment["vertex_count"] and
                   subject["junction_incident"] == fragment["junction_incident"], "fragment extent mismatch")
        o2.require(fragment["orientation"] == "X_MONOTONE_PARTIAL_PATH", "unresolved path orientation")
        columns = [(x, y) for x, y in path if abs(x-geometry["column"]) <= 12]
        o2.require([list(p) for p in columns] == fragment["support_columns_xy"], "G0 support changed")
        cid = context["id"]
        if cid not in loaded:
            case = plan["cases"][context["original_case_ref"]["index"]]
            o2.require(case["id"] == cid and {k: case[k] for k in geometry} == geometry, "case geometry mismatch")
            # Hash every raster the existing loader will use; do not rerun old features.
            paths = [case[k] for k in ("raster", "graph", "stage", "rgb") if case.get(k)]
            paths += list(case.get("images", {}).values())
            for name in set(paths):
                g0.pinned_path(root, {"path": name, "sha256": plan["pins"][name]})
            rgb, visible, _ = g0.material.load_case(root, case)
            edges, _ = g0.load_edges_labels(root, case, {"labels": None})
            o2.require(rgb is not None, "missing reviewed RGB")
            loaded[cid] = rgb, visible, edges
        rgb, visible, edges = loaded[cid]
        o2.require(all(0 <= x < edges.shape[1] and 0 <= y < edges.shape[0] and edges[y, x] and visible[y, x]
                       for x, y in path), "review path absent from saved visible edges")
        view = views[subject["view_id"]]
        image_path = g0.pinned_path(root, view["source"])
        with Image.open(image_path) as image:
            displayed = np.array(image.convert("RGB"))
        vx, vy = view["image_origin_xy"]
        dx, dy = ox-vx, oy-vy
        h, w = visible.shape
        o2.require(dx >= 0 and dy >= 0 and np.array_equal(displayed[dy:dy+h, dx:dx+w], rgb),
                   "review image differs from native RGB")
        x0, y0, x1, y1 = view["display_xyxy"]
        o2.require(all(x0 <= x < x1 and y0 <= y < y1 for x, y in subject["source_path_xy"]),
                   "review path outside displayed crop")
        support, used = context_support(visible, columns, path)
        pixels[sid] = {((x+ox, y+oy)) for x, y in used}
        outputs.append({"id": sid, "subject_sha256": answer["subject_sha256"],
                        "case_id": cid, "frame": context["frame"], "time_sec": context["time_sec"],
                        "time_kind": context["time_kind"], "source_recording": context["source_recording"],
                        "geometry_sha256": context["geometry_sha256"],
                        "g0_pointer": ["contexts", list(contexts).index(cid), "rows", ri, "incident_fragments", pi],
                        "allowed_interpretations": roles, "capability_target": next(iter(labels)),
                        "scope": answer["scope"], "dense_labels": False, "coordinate_tolerance": None,
                        "side_material_labels": None, "inference_metadata_allowed": False,
                        "proposed_context": support, "decision": "NOT_EVALUATED"})
    sharing = []
    for i, first in enumerate(outputs):
        for second in outputs[i+1:]:
            if (first["source_recording"]["sha256"], first["frame"]) == (second["source_recording"]["sha256"], second["frame"]):
                sharing.append({"subjects": [first["id"], second["id"]],
                                "shared_dependency_pixels": len(pixels[first["id"]] & pixels[second["id"]]),
                                "independent_split_allowed": False})
    return {"schema": "s11-native-fragment-role-qualification-v1", "reply_sha256": o2.fingerprint_json(reply),
            "g0_readout": proposal["g0_readout"], "baseline_counts": baseline["counts"],
            "subjects": outputs, "same_frame_dependency": sharing, "proposed_context": CONTEXT,
            "status": "SCOPED_ROLES_BOUND", "decision": "NOT_EVALUATED",
            "qualified_units": len(outputs), "exposed_recordings": len({r["source_recording"]["sha256"] for r in outputs}),
            "untouched_holdout_recordings": 0, "model_calls": 0, "production_changed": False,
            "training_executed": False, "video_decode": False,
            "remaining": ["adopt a concrete learning scope before any training",
                          "independent native optical/structure opposition remains unqualified",
                          "no cross-source internal-Foam opposition or Oil material-role supervision",
                          "no G1 efficacy, O2/V5, raw-front integration or field acceptance"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reply", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = qualify(args.root.resolve(), o2.read_json(args.reply))
    o2.require(len(json.dumps(result).encode()) <= 100_000, "qualification output too large")
    o2.write_new(args.output, result)
    print(json.dumps({"status": result["status"], "qualified_units": result["qualified_units"],
                      "model_calls": 0, "output_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
