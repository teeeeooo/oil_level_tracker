"""Paired overlay repair validation using existing frame and replay owners.

Only the original preprocessor is loaded from Git; no copied checkout, new
detector runner, alternate corpus, model inference or truth rewrite is needed.
"""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import cv2
import numpy as np

from oil_tracker.adapters.vision import preprocessing as current
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_candidate_rgb_trial as rgb
from tests.diagnostics import s11_existing_material_reuse as reuse
from tests.diagnostics import s11_interface_witness_replay as witness
from tests.diagnostics.s11_observation_replay_audit import tracking_rows, sequence_audit, user_truth_audit


def baseline(plan):
    source = subprocess.check_output(["git", "show", f"{plan['baseline_head']}:{plan['preprocessor']}"], cwd=ROOT)
    reuse.o2.require(hashlib.sha256(source).hexdigest() == plan["baseline_preprocessor_sha256"], "baseline changed")
    module = types.ModuleType("_s11_baseline_preprocessing")
    sys.modules[module.__name__] = module
    exec(compile(source, plan["preprocessor"], "exec"), module.__dict__)
    return module


def activate(owner, stack):
    for module in ("opencv_phase_detector", "phase_frame_detection"):
        stack.enter_context(patch(f"oil_tracker.adapters.vision.{module}.preprocess", owner.preprocess))


def frame_check(plan):
    original = baseline(plan)
    rows = []
    for item in plan["frames"]:
        path = reuse.g0.pinned_path(ROOT, item["input"])
        if path.suffix == ".png":
            frame = cv2.imread(str(path))
        else:
            cap = cv2.VideoCapture(str(path))
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES, item["frame_index"])
                ok, frame = cap.read()
                reuse.o2.require(ok, "decode failed")
            finally:
                cap.release()
        reuse.o2.require(frame is not None, "missing source frame")
        glass = InspectionRecipe.from_dict(reuse.read_pin(ROOT, item["recipe"])).glasses[0]
        bundle = build_mask_bundle(frame, glass)
        valid = bundle.effective_mask > 0
        row = {"id": item["id"], "bgr_sha256": rgb.native.array_hash(bundle.crop), "variants": {}}
        masks, overlays = [], []
        for name, owner in (("baseline", original), ("candidate", current)):
            pre = owner.preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
            overlay = owner._digital_overlay_mask(bundle.crop, valid)
            masks.append(pre.glare_mask)
            overlays.append(overlay)
            with ExitStack() as stack:
                activate(owner, stack)
                detection, artifacts = OpenCvPhaseDetector().detect(frame, glass, item["frame_index"], 0., debug=True)
            reuse.o2.require(np.array_equal(artifacts.images["glare_mask"], pre.glare_mask), "real detect mask mismatch")
            variant = {"glare_sha256": rgb.native.array_hash(pre.glare_mask),
                       "overlay_pixels": int(np.count_nonzero(overlay)),
                       "real_entry_mask_equal": True, "candidate_count": len(detection.candidates),
                       "detection_sha256": witness._digest(asdict(detection))}
            if "source_xy" in item:
                local = [int(v-o) for v, o in zip(item["source_xy"], bundle.crop_origin)]
                context = rgb.context(bundle.crop[:, :, ::-1].copy(), valid & (pre.glare_mask == 0), local)
                variant["context"] = {"status": context["status"], "patches": {k:s["patches"] for k,s in context["sides"].items()}}
            row["variants"][name] = variant
        row["mask_equal"] = np.array_equal(*masks)
        row["removed_opposition_pixels"] = int(np.count_nonzero((masks[0] > 0) & (masks[1] == 0)))
        reuse.o2.require(not np.any((masks[1] > 0) & (masks[0] == 0)), "new opposition appeared")
        reuse.o2.require(not np.any((overlays[1] > 0) & (overlays[0] == 0)), "new overlay appeared")
        reuse.o2.require(not np.any((masks[0] != masks[1]) & (overlays[0] == 0)), "non-overlay opposition changed")
        if item["id"] != "sample3-B":
            reuse.o2.require(row["mask_equal"], "preservation control changed")
        else:
            reuse.o2.require(row["variants"]["baseline"]["context"]["patches"]["upper"] == 0, "B baseline drift")
            reuse.o2.require(row["variants"]["candidate"]["context"]["status"] == "AVAILABLE", "B input not restored")
        rows.append(row)
    return {"schema":"s11-overlay-paired-frames-v1", "plan_sha256":reuse.o2.fingerprint_json(plan), "frames":rows}


def replay_one(plan, sample, variant, output):
    owner = baseline(plan) if variant == "baseline" else current
    # Reuse the existing worker's complete pipeline, reports, full row recording
    # and temporary cleanup. The wrapper adds baseline substitution and audit.
    with TemporaryDirectory(prefix="overlay-pair-", dir=output.parent) as scratch:
        work = Path(scratch)
        with ExitStack() as stack:
            activate(owner, stack)
            result = witness.run(ROOT, work/"window.json", sample, "none")
        with (work/"tracking_data.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(result["tracking_data.csv"][0]))
            writer.writeheader()
            writer.writerows(result["tracking_data.csv"])
        rows = tracking_rows(work)
        result["overlay_visual_audit"] = {sample: {"sequence": sequence_audit(rows), "user_truth": user_truth_audit(ROOT, sample, rows)}}
    result["variant"] = variant
    result["plan_sha256"] = reuse.o2.fingerprint_json(plan)
    result["baseline_substitution"] = variant == "baseline"
    if variant == "baseline":
        result["source_files"][plan["preprocessor"]] = plan["baseline_preprocessor_sha256"]
        result["source_sha256"] = witness._digest(result["source_files"])
    result["executing_preprocessor_sha256"] = result["source_files"][plan["preprocessor"]]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample", choices=("base_sample_1", "sample2", "sample3", "sample4"))
    parser.add_argument("--variant", choices=("baseline", "candidate"))
    args = parser.parse_args()
    reuse.o2.require(not args.output.exists(), "refuse overwrite")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    for pin in plan["source_pins"] + plan["replay_inputs"]:
        reuse.g0.pinned_path(ROOT, pin)
    reuse.o2.require(bool(args.sample) == bool(args.variant), "sample and variant required together")
    result = replay_one(plan, args.sample, args.variant, args.output) if args.sample else frame_check(plan)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(args.output, flush=True)


if __name__ == "__main__":
    main()
