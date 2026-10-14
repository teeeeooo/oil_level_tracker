"""Inspect chromatic component provenance without changing the production mask.

The frozen RGB qualification exposes visibility, not the pre-opening component
that supplied it. This bounded audit reconstructs that stage, checks equality
with the production overlay, and retains only component statistics and hashes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import cv2
import numpy as np

from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import _digital_overlay_mask, preprocess
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_candidate_rgb_trial as rgb
from tests.diagnostics import s11_existing_material_reuse as reuse


def components(crop, valid):
    bgr = crop.astype(np.int16)
    colorful = valid & (np.ptp(bgr, axis=2) >= 48) & (bgr.max(axis=2) >= 92)
    columns = np.flatnonzero(np.any(valid, axis=0))
    width = int(columns[-1] - columns[0] + 1)
    length = max(9, round(width * .18))
    maximum_height = max(3, round(valid.shape[0] * .065))
    minimum_width = max(length, round(width * .32))
    core = cv2.morphologyEx(colorful.astype(np.uint8) * 255, cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_RECT, (length, 1)))
    _, parents, parent_stats, _ = cv2.connectedComponentsWithStats(colorful.astype(np.uint8), connectivity=8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    result = np.zeros(valid.shape, np.uint8)
    rows = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        admitted = w >= minimum_width and h <= maximum_height and w / max(1, h) >= 5
        support = labels == label
        sources = [int(p) for p in np.unique(parents[support]) if p]
        rows.append({"core_xywh_area": [x, y, w, h, area], "admitted": admitted,
                     "parents_xywh_area": [parent_stats[p].astype(int).tolist() for p in sources],
                     "core_pixels_without_parent": int(np.count_nonzero(support & (parents == 0)))})
        if admitted:
            result[support] = 255
    radius = max(3, min(12, round(valid.shape[0] * .04)))
    result = cv2.dilate(result, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 2*radius+1)))
    result = cv2.bitwise_and(result, valid.astype(np.uint8)*255)
    reuse.o2.require(np.array_equal(result, _digital_overlay_mask(crop, valid)), "overlay reconstruction drift")
    return {"horizontal_length": length, "maximum_height": maximum_height,
            "minimum_width": minimum_width, "components": rows,
            "overlay_pixels": int(np.count_nonzero(result)),
            "overlay_sha256": rgb.native.array_hash(result), "production_equal": True}


def run(root, plan):
    started = time.monotonic()
    for pin in plan["source_pins"]:
        reuse.g0.pinned_path(root, pin)
    reply = reuse.read_pin(root, plan["reply"])
    reuse.o2.require(reply["role"] == "FLUID_EMPTY_SPACE_INTERFACE", "regional role required")
    rows = []
    for item in plan["frames"]:
        path = reuse.g0.pinned_path(root, item["input"])
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
        reuse.o2.require(frame is not None, "missing frame")
        recipe = InspectionRecipe.from_dict(reuse.read_pin(root, item["recipe"]))
        glass = recipe.glasses[0]
        bundle = build_mask_bundle(frame, glass)
        pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
        row = {"id": item["id"], "input": item["input"], "frame_index": item["frame_index"],
               "recipe": item["recipe"], "origin": list(bundle.crop_origin),
               "shape": list(bundle.crop.shape), "bgr_sha256": rgb.native.array_hash(bundle.crop),
               "glare_sha256": rgb.native.array_hash(pre.glare_mask),
               **components(bundle.crop, bundle.effective_mask > 0)}
        if "source_xy" in item:
            local = [int(v-o) for v, o in zip(item["source_xy"], bundle.crop_origin)]
            context = rgb.context(bundle.crop[:, :, ::-1].copy(),
                                  (bundle.effective_mask > 0) & (pre.glare_mask == 0), local)
            row["native_context"] = {"status": context["status"],
                "patches": {k: s["patches"] for k, s in context["sides"].items()}}
        rows.append(row)
    return {"schema": "s11-overlay-component-audit-v1", "plan_sha256": reuse.o2.fingerprint_json(plan),
            "frames": rows, "production_changed": False, "model_calls": 0,
            "seconds": time.monotonic()-started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reuse.o2.require(not args.output.exists(), "refuse overwrite")
    result = run(ROOT, json.loads(args.plan.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
