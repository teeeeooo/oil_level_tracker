"""Join scoped contact replies and complete native populations without fitting.

Frozen readers own pixels, paths and earlier roles. This successor owns the
combined roster and distinguishes native RGB from missing semantic observations.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_existing_material_reuse as reuse
from tests.diagnostics import s11_native_liquid_reply as liquid

ready, native = liquid.readiness, liquid.native
semantic, old, o2 = ready.semantic, ready.old, ready.o2
SCHEMA = "s11-native-role-corpus-v1"
INPUTS = {"base_plan", "base_readout", "contact_reply", "water_reply", "water_manifest", "water_readout"}
CHANNELS = ("FOAM_UPPER", "LIQUID_UPPER")


def identity(row):
    return row["source_recording"]["sha256"], row["frame"], row["path_sha256"]


def validate_roster(rows):
    o2.unique(rows, "id", "corpus row")
    seen, sources = set(), {}
    for row in rows:
        key = identity(row)
        o2.require(key not in seen, "duplicate source/frame/path")
        seen.add(key)
        source = row["source_recording"]
        o2.require(sources.setdefault(source["path"], source["sha256"]) == source["sha256"],
                   "recording path has conflicting hashes")
        o2.require(bool(row["native_sides"]) == (row["availability"] == "AVAILABLE_PARTIAL_CONTEXT"),
                   "native availability differs from saved support")
        o2.require(not row["support"] or bool(row["native_sides"]), "semantic support without native input")


def apply_contact(rows, subject, qualification):
    """Overlay a verified exact path, retaining original observation pointers."""
    matches = [r for r in rows if identity(r) == identity(subject)]
    o2.require(len(matches) == 1, "contact is absent or duplicated in corpus")
    row, = matches
    o2.require(row["subject_id"] == subject["id"] and row["review_state"] == "UNREVIEWED"
               and row["qualification"] is None and not row["allowed_boundary_roles"],
               "refuse role overwrite or subject alias")
    o2.require(subject["review_status"] == "QUALIFIED_ROLE" and
               subject["capability_target"] == "LIQUID_UPPER" and
               subject["allowed_interpretations"] in ([r] for r in liquid.RELATIONS) and
               not subject["dense_labels"] and subject["side_material_labels"] is None and
               not subject["motion_qualified"] and not subject["scalar_qualified"], "contact scope changed")
    o2.require(row["availability"] == subject["proposed_context"]["status"], "contact support changed")
    row.update(qualification=qualification, subject_sha256=subject["subject_sha256"],
               original_interpretations=subject["allowed_interpretations"],
               allowed_boundary_roles=["LIQUID_UPPER"], certain_boundary_role="LIQUID_UPPER",
               review_state="QUALIFIED_SINGLE_ROLE")


def targets(row):
    """A different positive channel is not an automatic negative label."""
    role = row["certain_boundary_role"]
    values = {c: (1 if role == c else 0 if role in
                    ("INTERNAL_FOAM_CHANGE", "STRUCTURE_BOUNDARY") else None) for c in CHANNELS}
    return dict(values=values, native_loss_mask={c: bool(row["native_sides"]) and v is not None
                                               for c, v in values.items()},
                allowed_roles=row["allowed_boundary_roles"],
                disjunction=len(row["allowed_boundary_roles"]) > 1)


def input_coverage(rows, input_key):
    selected = [dict(r, support=r[input_key]) for r in rows]
    roles = ready.coverage(selected)
    missing = [c for c in CHANNELS if len(roles[c]["available_certain_sources"]) < 2]
    return dict(role_coverage=roles, source_group_folds=ready.grouped_folds(selected),
                missing_disjoint_positive_sources=missing,
                status="POSITIVE_SOURCE_COVERAGE_ONLY" if not missing else "INCOMPLETE_POSITIVE_SOURCE_COVERAGE")


def build(root, plan):
    o2.require(plan["schema"] == SCHEMA and plan["scope"] == "NATIVE_INPUT_AND_ROLE_BINDING_ONLY"
               and set(plan["inputs"]) == INPUTS, "unsupported corpus plan")
    for pin in plan["sources"]:
        old.verified(root, pin)
    inputs = {k: native.read_pin(root, pin) for k, pin in plan["inputs"].items()}
    before = ready.audit(root, inputs["base_plan"])
    o2.require(before == inputs["base_readout"], "frozen role observations changed")
    units, frames, _, _, _ = semantic.inputs(root)
    frames = deepcopy(frames)
    for frame in frames.values():
        frame.pop("model_scale_xy")
    rows = deepcopy(before["rows"])
    for row, unit in zip(rows, units, strict=True):
        o2.require(row["id"] == unit["id"], "native observation order changed")
        row.update(subject_id=row["id"], frame_key=unit["frame_key"], native_sides=unit["sides"],
                   semantic_observation=dict(input=plan["inputs"]["base_readout"], pointer=row["semantic_pointer"]))

    manifest, saved = inputs["water_manifest"], inputs["water_readout"]
    o2.require(saved["manifest_sha256"] == o2.fingerprint_json(manifest), "water manifest changed")
    for pin in manifest["sources"]:
        old.verified(root, pin)
    native.read_pin(root, manifest["source_review"])
    native.read_pin(root, manifest["closed_interval_reply"])
    packet = reuse.native_packet(root, native.read_pin(root, manifest["inputs"]["g0_manifest"]),
                                native.read_pin(root, manifest["inputs"]["g0_readout"]), manifest["case_id"])
    o2.require(saved["native_review_packets"] == [packet], "complete water population changed")
    proposal = native.read_pin(root, inputs["water_reply"]["proposal"])
    subject, = proposal["subjects"]
    view = native.by_id(proposal["views"], "view")[subject["view_id"]]
    with Image.open(old.verified(root, view["source"])) as image:
        rgb = np.array(image.convert("RGB"))
    roi = semantic.crop_roi(rgb, packet["geometry"], view["image_origin_xy"])
    key = f"{packet['source_recording']['sha256']}:{packet['frame']}"
    o2.require(key not in frames, "new population duplicates an existing frame")
    frames[key] = dict(source_recording=packet["source_recording"], frame=packet["frame"],
                       rgb=view["source"], image_origin=view["image_origin_xy"], geometry=packet["geometry"],
                       roi_sha256=old.array_hash(roi), units=[])
    for index, fragment in enumerate(packet["fragments"]):
        context = fragment["context_support"]
        sides = {}
        if context["status"] == "AVAILABLE_PARTIAL_CONTEXT":
            ox, oy = packet["geometry"]["origin"]
            vx, vy = view["image_origin_xy"]
            for side, support in context["sides"].items():
                centers = support["complete_centers_xy"]
                pixels = old.patches(roi, centers)
                sides[side] = dict(centers_image_xy=[[x+ox-vx, y+oy-vy] for x, y in centers],
                                   shape=list(pixels.shape), uint8_sha256=old.array_hash(pixels))
        row = dict(id=fragment["id"], subject_id=f"fragment-{fragment['fragment_id']}",
                   source_recording=packet["source_recording"], frame=packet["frame"], frame_key=key,
                   path_sha256=o2.fingerprint_json(fragment["source_path_xy"]), qualification=None,
                   subject_sha256=None, original_interpretations=[], allowed_boundary_roles=[],
                   certain_boundary_role=None, review_state="UNREVIEWED", availability=context["status"],
                   native_sides=sides, support={}, semantic_observation=None,
                   native_observation=dict(input=plan["inputs"]["water_readout"],
                                           pointer=f"/native_review_packets/0/fragments/{index}"),
                   pure_side_material_truth=False, physical_decision=None)
        rows.append(row)
        frames[key]["units"].append(row["id"])
    validate_roster(rows)
    qualifications = {}
    for name in ("contact_reply", "water_reply"):
        result = liquid.qualify(root, inputs[name])
        qualifications[name] = result
        for subject in result["subjects"]:
            apply_contact(rows, subject, dict(reply=plan["inputs"][name],
                          result_sha256=o2.fingerprint_json(result)))
    for row in rows:
        row["targets"] = targets(row)
    native_coverage, semantic_coverage = (input_coverage(rows, key) for key in ("native_sides", "support"))
    return dict(schema=SCHEMA, plan_sha256=o2.fingerprint_json(plan), inputs=plan["inputs"],
                counts=dict(total=len(rows), qualified=sum(bool(r["allowed_boundary_roles"]) for r in rows),
                    unknown=sum(not r["allowed_boundary_roles"] for r in rows),
                    native_available=sum(bool(r["native_sides"]) for r in rows),
                    semantic_available=sum(bool(r["support"]) for r in rows),
                    recordings=len({r["source_recording"]["sha256"] for r in rows}), frames=len(frames)),
                rows=rows, frames=frames, qualifications=qualifications,
                native_input_coverage=native_coverage, saved_semantic_coverage=semantic_coverage,
                training_executed=False, model_calls=0, video_decodes=0, production_changed=False,
                untouched_holdout_recordings=0, training_contract_selected=False,
                status="SCOPED_CORPUS_BOUND_NOT_MODEL_ACCEPTANCE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = build(args.root.resolve(), o2.read_json(args.plan))
    o2.require(len(json.dumps(result).encode("utf-8")) < 1_000_000, "corpus output budget exceeded")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    o2.write_new(args.output, result)
    print(json.dumps({k: result[k] for k in ("status", "counts")}))


if __name__ == "__main__":
    main()
