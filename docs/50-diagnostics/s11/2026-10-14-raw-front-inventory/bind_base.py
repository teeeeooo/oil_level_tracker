"""Compose frozen corpus/delta owners with the inspected legacy-frame reply.

The first extension runner assumes the original corpus and its source-review
manifest. This one-off composition accepts the already prepared legacy capture
without changing that frozen runner or copying the preceding 135 observations.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import numpy as np
from PIL import Image
from tests.diagnostics import s11_native_role_extension as extension

corpus, native, old, o2 = extension.corpus, extension.native, extension.old, extension.o2


def bind(root, plan):
    o2.require(plan["schema"] == "s11-native-legacy-contact-extension-v1", "unsupported plan")
    for pin in plan["sources"]:
        old.verified(root, pin)
    inputs = {key: native.read_pin(root, pin) for key, pin in plan["inputs"].items()}
    previous = inputs["previous_readout"]
    o2.require(extension.build(root, inputs["previous_plan"]) == previous,
               "frozen first extension changed")
    original = native.read_pin(root, previous["base"])
    base = dict(rows=original["rows"] + previous["added_rows"],
                frames={**original["frames"], **previous["added_frames"]})
    before_hash = o2.fingerprint_json(base)
    manifest, saved = inputs["manifest"], inputs["native_readout"]
    o2.require(manifest["schema"] == "s11-native-review-source-reuse-v1" and
               saved["schema"] == "s11-native-source-review-readout-v1" and
               saved["manifest_sha256"] == o2.fingerprint_json(manifest), "legacy manifest changed")
    packet = corpus.reuse.native_packet(root,
        native.read_pin(root, manifest["inputs"]["g0_manifest"]),
        native.read_pin(root, manifest["inputs"]["g0_readout"]), manifest["case_id"])
    o2.require(saved["native_review_packets"] == [packet], "complete legacy population changed")
    reply = inputs["reply"]
    proposal = native.read_pin(root, reply["proposal"])
    o2.require(proposal["reuse_readout"] == plan["inputs"]["native_readout"] and
               all(proposal[key] == manifest["inputs"][key] for key in ("g0_manifest", "g0_readout")),
               "reply belongs to another population")
    qualification = extension.liquid.qualify(root, reply)
    view, = proposal["views"]
    with Image.open(old.verified(root, view["source"])) as image:
        rgb = np.array(image.convert("RGB"))
    added, frames = extension.population(packet, view, rgb, plan["inputs"]["native_readout"])
    result = extension.join(base, added, frames, qualification, plan["inputs"]["reply"])
    o2.require(o2.fingerprint_json(base) == before_hash, "preceding observations changed")

    # Keep the conflicting historical scalar annotation attributed and frozen.
    # It cannot be reused as a Foam-negative label for this new path population.
    prior = saved["prior_scalar_context"]
    annotation, = [row for row in inputs["legacy_truth"]["annotations"]
                   if row["annotation_id"] == prior["annotation_id"]]
    o2.require(annotation["frame_index"] == prior["frame_index"] == packet["frame"] and
               annotation["foam_present"] is prior["foam_present"] is False,
               "expected legacy Foam-absence conflict changed")
    subject, = qualification["subjects"]
    o2.require(subject["allowed_interpretations"] == ["FOAM_LOWER_LIQUID_INTERFACE"],
               "this legacy conflict receipt requires a Foam-liquid reply")
    for frame in frames.values():
        frame["legacy_foam_absence_allowed"] = False
    conflict = dict(legacy_truth=plan["inputs"]["legacy_truth"],
        annotation_id=prior["annotation_id"], review_id=prior["review_id"],
        frame=packet["frame"], historical_foam_present=False,
        current_relation="FOAM_LOWER_LIQUID_INTERFACE", current_reply=plan["inputs"]["reply"],
        legacy_foam_absence_allowed=False, scalar_truth_changed=False,
        disposition="NEW_EXACT_PATH_ROLE_SUPERSEDES_FOAM_ABSENCE_FOR_THIS_FRAME_ONLY",
        scope="No new Foam upper, pure-side material, motion, exact scalar or adjacent-frame truth")
    return dict(schema=plan["schema"], plan_sha256=o2.fingerprint_json(plan),
        parent=plan["inputs"]["previous_readout"], inputs=plan["inputs"],
        qualification=qualification, **result, historical_conflict=conflict,
        unchanged_base_rows=len(base["rows"]), unchanged_base_sha256=before_hash,
        model_calls=0, training_executed=False, production_changed=False, video_decodes=0,
        untouched_holdout_recordings=0, status="SCOPED_CONTACT_EXTENSION_NOT_MODEL_ACCEPTANCE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = bind(args.root.resolve(), o2.read_json(args.plan))
    o2.require(len(json.dumps(result).encode("utf-8")) < 100_000, "extension budget exceeded")
    o2.write_new(args.output, result)
    print(json.dumps({key: result[key] for key in ("status", "counts")}))
