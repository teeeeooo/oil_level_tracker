"""Append one complete native frame and scoped contacts to a frozen corpus.

The original corpus/qualifiers stay immutable. Retain only the new frame's rows,
with a pin to the old corpus, rather than copying every earlier observation.
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

from tests.diagnostics import s11_native_role_corpus as corpus

liquid, native, old, o2 = corpus.liquid, corpus.native, corpus.old, corpus.o2
SCHEMA = "s11-native-role-extension-v1"
INPUTS = {"base_plan", "base_readout", "manifest", "native_readout", "reply"}


def population(packet, view, rgb, readout_pin):
    """Keep all paths, missing contexts and exact original-image footprints."""
    o2.require(packet["geometry"]["scale_xy"] == [1, 1], "extension must be native")
    roi = corpus.semantic.crop_roi(rgb, packet["geometry"], view["image_origin_xy"])
    key = f"{packet['source_recording']['sha256']}:{packet['frame']}"
    frame = dict(source_recording=packet["source_recording"], frame=packet["frame"],
                 rgb=view["source"], image_origin=view["image_origin_xy"],
                 geometry=packet["geometry"], roi_sha256=old.array_hash(roi), units=[])
    rows = []
    ox, oy = packet["geometry"]["origin"]
    vx, vy = view["image_origin_xy"]
    for index, fragment in enumerate(packet["fragments"]):
        context, sides = fragment["context_support"], {}
        if context["status"] == "AVAILABLE_PARTIAL_CONTEXT":
            o2.require(set(context["sides"]) == {"upper", "lower"}, "incomplete side roster")
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
                   native_observation=dict(input=readout_pin,
                                           pointer=f"/native_review_packets/0/fragments/{index}"),
                   pure_side_material_truth=False, physical_decision=None)
        rows.append(row)
        frame["units"].append(row["id"])
    corpus.validate_roster(rows)
    return rows, {key: frame}


def contact_coverage(rows):
    """Source-held-out contact coverage is an input limit, never model success."""
    sources = sorted({r["source_recording"]["sha256"] for r in rows})
    result = {}
    for relation in liquid.RELATIONS:
        matching = [r for r in rows if r["original_interpretations"] == [relation]
                    and r["certain_boundary_role"] == "LIQUID_UPPER" and r["native_sides"]]
        positive_sources = sorted({r["source_recording"]["sha256"] for r in matching})
        result[relation] = dict(available_paths=[r["id"] for r in matching],
            positive_sources=positive_sources,
            held_source_coverage=[dict(held_source=s, fit_positive_sources=[p for p in positive_sources if p != s],
                held_positive_paths=[r["id"] for r in matching if r["source_recording"]["sha256"] == s])
                for s in sources],
            disjoint_positive_sources_available=len(positive_sources) >= 2)
    return result


def join(base, added, frames, qualification, reply_pin):
    """Append only; never overwrite an old path, frame, role or observation."""
    o2.require(not (set(base["frames"]) & set(frames)), "frame already exists in base")
    added = deepcopy(added)
    rows = base["rows"] + added
    corpus.validate_roster(rows)
    for subject in qualification["subjects"]:
        corpus.apply_contact(added, subject, dict(reply=reply_pin,
            result_sha256=o2.fingerprint_json(qualification)))
    for row in added:
        row["targets"] = corpus.targets(row)
    counts = dict(total=len(rows), qualified=sum(bool(r["allowed_boundary_roles"]) for r in rows),
                  unknown=sum(not r["allowed_boundary_roles"] for r in rows),
                  native_available=sum(bool(r["native_sides"]) for r in rows),
                  semantic_available=sum(bool(r["support"]) for r in rows),
                  recordings=len({r["source_recording"]["sha256"] for r in rows}),
                  frames=len(base["frames"])+len(frames))
    return dict(added_rows=added, added_frames=frames, counts=counts,
                contact_coverage=contact_coverage(rows),
                native_input_coverage=corpus.input_coverage(rows, "native_sides"),
                saved_semantic_coverage=corpus.input_coverage(rows, "support"))


def build(root, plan):
    o2.require(plan["schema"] == SCHEMA and set(plan["inputs"]) == INPUTS,
               "unsupported extension plan")
    for pin in plan["sources"]:
        old.verified(root, pin)
    inputs = {k: native.read_pin(root, pin) for k, pin in plan["inputs"].items()}
    base = inputs["base_readout"]
    o2.require(corpus.build(root, inputs["base_plan"]) == base, "frozen corpus changed")
    manifest, saved = inputs["manifest"], inputs["native_readout"]
    o2.require(manifest["schema"] == "s11-native-review-source-reuse-v1" and
               saved["schema"] == "s11-native-review-source-readout-v1" and
               saved["manifest_sha256"] == o2.fingerprint_json(manifest), "review manifest changed")
    for pin in manifest["sources"]:
        old.verified(root, pin)
    # The candidate is provenance for review selection only; never a role input.
    native.read_pin(root, manifest["candidate_context_only"]["input"])
    packet = corpus.reuse.native_packet(root, native.read_pin(root, manifest["inputs"]["g0_manifest"]),
        native.read_pin(root, manifest["inputs"]["g0_readout"]), manifest["case_id"])
    o2.require(saved["native_review_packets"] == [packet], "complete native population changed")
    reply = inputs["reply"]
    proposal = native.read_pin(root, reply["proposal"])
    o2.require(proposal["reuse_readout"] == plan["inputs"]["native_readout"] and
               all(proposal[k] == manifest["inputs"][k] for k in ("g0_manifest", "g0_readout")),
               "proposal belongs to another population")
    qualification = liquid.qualify(root, reply)
    view, = proposal["views"]
    with Image.open(old.verified(root, view["source"])) as image:
        rgb = np.array(image.convert("RGB"))
    added, frames = population(packet, view, rgb, plan["inputs"]["native_readout"])
    result = join(base, added, frames, qualification, plan["inputs"]["reply"])
    return dict(schema=SCHEMA, plan_sha256=o2.fingerprint_json(plan), base=plan["inputs"]["base_readout"],
                inputs=plan["inputs"], qualification=qualification, **result,
                unchanged_base_rows=len(base["rows"]), model_calls=0, training_executed=False,
                production_changed=False, video_decodes=0, untouched_holdout_recordings=0,
                status="SCOPED_CONTACT_EXTENSION_NOT_MODEL_ACCEPTANCE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = build(args.root.resolve(), o2.read_json(args.plan))
    o2.require(len(json.dumps(result).encode("utf-8")) < 150_000, "extension output budget exceeded")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    o2.write_new(args.output, result)
    print(json.dumps({k: result[k] for k in ("status", "counts")}))


if __name__ == "__main__":
    main()
