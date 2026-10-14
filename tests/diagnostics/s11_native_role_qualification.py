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
FACET_SCHEMA = "s11-native-fragment-role-reply-v2"
REVIEW_SCHEMA = "s11-native-fragment-role-reply-v3"
INSPECTION_SCHEMA = "s11-native-fragment-proposal-inspection-v1"
PREPARATION_SCHEMA = "s11-native-fragment-review-preparation-v1"
ROLES = {
    "EXTERNAL_FOAM_UPPER": "EXTERNAL_SURFACE",
    "OSCILLATING_LIQUID_UPPER": "EXTERNAL_SURFACE",
    "INTERNAL_FOAM_CHANGE": "INTERNAL_FOAM_CHANGE",
    "STRUCTURE_BOUNDARY": "STRUCTURE_BOUNDARY",
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


def prepare_proposal(root, plan):
    """Retain every saved fragment in a reviewed interval or an unlabelled row."""
    o2.require(plan["schema"] == PREPARATION_SCHEMA, "unsupported preparation schema")
    reuse_manifest = read_pin(root, plan["reuse_manifest"])
    reused = read_pin(root, plan["reuse_readout"])
    o2.require(reused["manifest_sha256"] == o2.fingerprint_json(reuse_manifest), "reuse manifest mismatch")
    baseline = read_pin(root, reuse_manifest["inputs"]["g0_readout"])
    manifest = read_pin(root, reuse_manifest["inputs"]["g0_manifest"])
    o2.require(baseline["manifest_sha256"] == o2.fingerprint_json(manifest), "G0 manifest mismatch")
    packet = by_id([dict(id=p["case_id"], **p) for p in reused["native_review_packets"]], "packet")[plan["case_id"]]
    context = by_id(baseline["contexts"], "context")[plan["case_id"]]
    for field in ("frame", "geometry", "source_recording"):
        o2.require(packet[field] == context[field], f"packet {field} changed")
    bands = {b["original"]["id"]: b for b in packet["intervals"]}
    o2.require(len(bands) == len(packet["intervals"]), "duplicate interval")
    o2.require(("interval_id" in plan) != ("fixed_column_source_y" in plan),
               "choose exactly one interval or unlabelled row")
    band = bands[plan["interval_id"]] if "interval_id" in plan else None
    fragments = by_id(packet["fragments"], "fragment")
    if band is not None:
        lo, hi = band["original"]["interval"]
        selected = band["compatible_fragments"]
    else:
        lo = hi = plan["fixed_column_source_y"]
        o2.require(type(lo) in (int, float) and np.isfinite(lo), "invalid unlabelled row")
        o2.text(plan["selection_reason"], "unlabelled row selection reason")
        selected = [fid for fid, f in fragments.items() if lo in f["fixed_column_source_ys"]]
    o2.require(selected and len(selected) == len(set(selected)), "empty or duplicate fragment selection")
    expected = {fid for fid, f in fragments.items()
                if any(lo <= y <= hi for y in f["fixed_column_source_ys"])}
    o2.require(set(selected) == expected, "interval selection drops or adds a saved fragment")
    view = plan["view"]
    for pin in (view["source"], plan["display"]):
        g0.pinned_path(root, pin)
    subjects = []
    ox, oy = context["geometry"]["origin"]
    for fid in selected:
        saved = fragments[fid]
        matches = [(row, f) for row in context["rows"] for f in row["incident_fragments"]
                   if f["fragment_id"] == saved["fragment_id"]
                   and lo <= row["source_xy"][1] <= hi]
        o2.require(len(matches) == 1, "ambiguous fixed-column fragment binding")
        row, fragment = matches[0]
        local_path = [[x-ox, y-oy] for x, y in saved["source_path_xy"]]
        o2.require(o2.fingerprint_json(fragment) == saved["g0_fragment_sha256"], "saved fragment changed")
        o2.require(o2.fingerprint_json(local_path) == fragment["path_sha256"], "saved native path changed")
        subjects.append(dict(id=f"fragment-{saved['fragment_id']}", case_id=packet["case_id"],
                             frame=packet["frame"], view_id=view["id"], fixed_column_xy=row["source_xy"],
                             native_fragment_id=saved["fragment_id"], source_path_xy=saved["source_path_xy"],
                             raster_path_sha256=fragment["path_sha256"],
                             readout_subject_sha256=saved["g0_fragment_sha256"],
                             vertex_count=fragment["vertex_count"], junction_incident=fragment["junction_incident"]))
    result = dict(schema="s11-native-fragment-role-review-proposal-v1",
                g0_manifest=reuse_manifest["inputs"]["g0_manifest"],
                g0_readout=reuse_manifest["inputs"]["g0_readout"], display=plan["display"],
                subjects=subjects, views=[view], preparation_plan_sha256=o2.fingerprint_json(plan),
                reuse_readout=plan["reuse_readout"], selection_interval=band["original"] if band is not None else None,
                selection="Every saved fragment intersecting the closed interval; no score or length choice",
                preserved_intervals=[b for b in packet["intervals"] if b is not band],
                complete_saved_fragment_count=len(fragments), question=plan["question"],
                status="PENDING_PATH_ROLE_REVIEW", qualified_units=0, training_executed=False,
                scope="Displayed path role only; no dense/pure-side/coordinate truth or training grant")
    if band is None:
        result.pop("selection_interval")
        result.update(selection="Every saved fragment at the selected unlabelled row; no score or length choice",
                      selection_row={"source_y": lo, "reason": plan["selection_reason"],
                                     "physical_role": "UNREVIEWED"})
    return result


def qualify(root, reply):
    inspection = reply.get("schema") == INSPECTION_SCHEMA
    expected = {"schema", "proposal", "display"}
    if not inspection:
        expected |= {"response_ko", "answers"}
    o2.require(set(reply) == expected,
               "invalid reply fields")
    o2.require(reply["schema"] in (SCHEMA, FACET_SCHEMA, REVIEW_SCHEMA, INSPECTION_SCHEMA),
               "unsupported reply schema")
    has_facets = reply["schema"] in (FACET_SCHEMA, REVIEW_SCHEMA)
    explicit_status = reply["schema"] == REVIEW_SCHEMA
    if not inspection:
        o2.text(reply["response_ko"], "verbatim response")
    proposal = read_pin(root, reply["proposal"])
    g0.pinned_path(root, reply["display"])
    o2.require(proposal["schema"] == "s11-native-fragment-role-review-proposal-v1", "unsupported proposal")
    if explicit_status or inspection:
        o2.require(reply["display"] == proposal["display"], "display differs from proposal")
    manifest = read_pin(root, proposal["g0_manifest"])
    baseline = read_pin(root, proposal["g0_readout"])
    o2.require(baseline["schema"] == g0.SCHEMA and baseline["manifest_sha256"] == o2.fingerprint_json(manifest),
               "G0 manifest/readout mismatch")
    subjects = by_id(proposal["subjects"], "subject")
    answers = by_id(reply["answers"], "answer") if not inspection else {}
    contexts = by_id(baseline["contexts"], "context")
    views = by_id(proposal["views"], "view")
    if not inspection:
        o2.require(set(answers) == set(subjects), "reply must account for each displayed subject")
    plan = read_pin(root, manifest["inputs"]["foam_preflight"])
    outputs, loaded, pixels, seen_paths = [], {}, {}, set()
    for sid, subject in subjects.items():
        # Inspection checks real source/path/display bindings without inventing a
        # human reply. Pending, ambiguous and unassessable subjects have no target.
        answer = answers.get(sid)
        roles, facets, labels = [], [], set()
        status = "PENDING_REVIEW" if inspection else "QUALIFIED_ROLE"
        if answer is not None:
            fields = {"id", "subject_sha256", "statement_ko", "allowed_interpretations", "scope"}
            fields |= {"context_facets"} if has_facets else set()
            fields |= {"review_status"} if explicit_status else set()
            o2.require(set(answer) == fields, "invalid answer fields")
            o2.require(answer["subject_sha256"] == o2.fingerprint_json(subject), "review subject changed")
            o2.require(answer["scope"] == "DISPLAYED_FRAGMENT_ROLE_ONLY", "unsupported review precision")
            o2.text(answer["statement_ko"], "subject statement")
            o2.require(answer["statement_ko"] in reply["response_ko"], "statement absent from response")
            status = answer.get("review_status", "QUALIFIED_ROLE")
            o2.require(status in {"QUALIFIED_ROLE", "AMBIGUOUS_ROLE", "UNASSESSABLE"},
                       "unsupported review status")
            roles = answer["allowed_interpretations"]
            o2.require(isinstance(roles, list) and len(roles) == len(set(roles)) and set(roles) <= ROLES.keys(),
                       "unsupported or duplicate role")
            labels = {ROLES[r] for r in roles}
            if status == "QUALIFIED_ROLE":
                o2.require(bool(roles), "qualified role must have an interpretation")
                o2.require(len(labels) == 1, "ambiguous surface/internal target")
            elif status == "AMBIGUOUS_ROLE":
                o2.require(len(roles) >= 2, "ambiguous role needs explicit alternatives")
            else:
                o2.require(not roles, "unassessable subject cannot assert a role")
            facets = answer.get("context_facets", [])
        o2.require(isinstance(facets, list), "invalid context facets")
        for facet in facets:
            o2.require(set(facet) == {"kind", "certainty", "statement_ko"}, "invalid facet fields")
            o2.require((facet["kind"], facet["certainty"]) in {
                ("GLASS_CIRCULAR_PATTERN_PATH_INFLUENCE", "USER_SUSPECTED"),
                ("CIRCULAR_RIM", "USER_CONFIRMED_CONTEXT"),
            }, "unsupported facet or certainty")
            o2.text(facet["statement_ko"], "facet statement")
            o2.require(facet["statement_ko"] in answer["statement_ko"], "facet absent from subject statement")
        o2.require(len({f["kind"] for f in facets}) == len(facets), "duplicate facet")
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
        identity = (context["source_recording"]["sha256"], context["frame"],
                    o2.fingerprint_json(subject["source_path_xy"]))
        o2.require(identity not in seen_paths, "duplicate native subject under another id")
        seen_paths.add(identity)
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
        outputs.append({"id": sid, "subject_sha256": o2.fingerprint_json(subject),
                        "case_id": cid, "frame": context["frame"], "time_sec": context["time_sec"],
                        "time_kind": context["time_kind"], "source_recording": context["source_recording"],
                        "geometry_sha256": context["geometry_sha256"],
                        "g0_pointer": ["contexts", list(contexts).index(cid), "rows", ri, "incident_fragments", pi],
                        "allowed_interpretations": roles,
                        "capability_target": next(iter(labels)) if status == "QUALIFIED_ROLE" else None,
                        "scope": "DISPLAYED_FRAGMENT_ROLE_ONLY", "dense_labels": False, "coordinate_tolerance": None,
                        "side_material_labels": None, "inference_metadata_allowed": False,
                        "proposed_context": support, "decision": "NOT_EVALUATED"})
        if has_facets:
            outputs[-1].update(context_facets=facets, causal_mechanism_verified=False)
        if explicit_status or inspection:
            outputs[-1]["review_status"] = status
    sharing = []
    for i, first in enumerate(outputs):
        for second in outputs[i+1:]:
            if (first["source_recording"]["sha256"], first["frame"]) == (second["source_recording"]["sha256"], second["frame"]):
                sharing.append({"subjects": [first["id"], second["id"]],
                                "shared_dependency_pixels": len(pixels[first["id"]] & pixels[second["id"]]),
                                "independent_split_allowed": False})
    result = {"schema": "s11-native-fragment-role-qualification-v2" if has_facets else
                      "s11-native-fragment-role-qualification-v1", "reply_sha256": o2.fingerprint_json(reply),
            "g0_readout": proposal["g0_readout"], "baseline_counts": baseline["counts"],
            "subjects": outputs, "same_frame_dependency": sharing, "proposed_context": CONTEXT,
            "status": "SCOPED_ROLES_BOUND", "decision": "NOT_EVALUATED",
            "qualified_units": len(outputs), "exposed_recordings": len({r["source_recording"]["sha256"] for r in outputs}),
            "untouched_holdout_recordings": 0, "model_calls": 0, "production_changed": False,
            "training_executed": False, "video_decode": False,
            "remaining": (["only this supplement's displayed roles are qualified; combine source groups explicitly",
                           "no pure-side material labels or verified optical cause",
                           "no G1 efficacy, O2/V5, raw-front integration or field acceptance"] if has_facets else
                          ["adopt a concrete learning scope before any training",
                          "independent native optical/structure opposition remains unqualified",
                          "no cross-source internal-Foam opposition or Oil material-role supervision",
                          "no G1 efficacy, O2/V5, raw-front integration or field acceptance"])}
    if explicit_status or inspection:
        counts = Counter(s["review_status"] for s in outputs)
        result.update(schema=INSPECTION_SCHEMA if inspection else "s11-native-fragment-role-qualification-v3",
                      status="PROPOSAL_VERIFIED_PENDING_REVIEW" if inspection else "SCOPED_REVIEW_BOUND",
                      qualified_units=counts["QUALIFIED_ROLE"], accounted_units=len(outputs),
                      review_status_counts=dict(counts), new_training_labels=0)
        result["remaining"] = [
            "only qualified displayed roles can constrain a separately declared comparison",
            "pending, ambiguous and unassessable subjects supply no target or negative success",
            "no pure-side truth, learning grant, G1 efficacy, O2/V5 or field acceptance",
        ]
        if inspection:
            result["request_sha256"] = result.pop("reply_sha256")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--reply", type=Path)
    mode.add_argument("--inspect-proposal", type=Path)
    mode.add_argument("--prepare-plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    if args.prepare_plan:
        result = prepare_proposal(args.root.resolve(), o2.read_json(args.prepare_plan))
        o2.require(len(json.dumps(result).encode()) <= 100_000, "proposal output too large")
        o2.write_new(args.output, result)
        print(json.dumps({"status": result["status"], "subjects": len(result["subjects"]),
                          "qualified_units": 0, "output_bytes": args.output.stat().st_size}))
        return
    if args.inspect_proposal:
        proposal_path = args.inspect_proposal.resolve()
        root = args.root.resolve()
        o2.require(proposal_path.is_relative_to(root), "proposal escapes repository")
        proposal = o2.read_json(proposal_path)
        request = {"schema": INSPECTION_SCHEMA,
                   "proposal": {"path": str(proposal_path.relative_to(root)),
                                "sha256": o2.sha256_file(proposal_path)},
                   "display": proposal["display"]}
    else:
        request = o2.read_json(args.reply)
    result = qualify(args.root.resolve(), request)
    o2.require(len(json.dumps(result).encode()) <= 100_000, "qualification output too large")
    o2.write_new(args.output, result)
    print(json.dumps({"status": result["status"], "qualified_units": result["qualified_units"],
                      "model_calls": 0, "output_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
