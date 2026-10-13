"""Prepare one candidate-acceptance question from the closed public-source range.

The existing native-fragment renderer displays a different subject: Canny paths.
This small adapter shows original candidate representative points and explicitly
separate pooled sector samples. It reuses the saved position join, no detector.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tests.diagnostics import s11_existing_material_reuse as reuse


def prepare(root, plan, output):
    o2 = reuse.o2
    o2.require(not output.exists(), "refuse overwrite")
    o2.require(plan["schema"] == "s11-public-oil-candidate-review-v1", "unsupported review plan")
    for pin in plan["inputs"].values():
        reuse.g0.pinned_path(root, pin)
    docs = {key: reuse.read_pin(root, pin) for key, pin in plan["inputs"].items()
            if key in {"raw", "diagnostics", "capture", "position", "join"}}
    raw, join, reply = (docs[k] for k in ("raw", "join", "position"))
    o2.require(reply["status"] == "CLOSED_USER_CONFIRMED_BOTH_RANGES", "position review not closed")
    o2.require(raw["frame_index"] == reply["frame_index"] == join["frame_index"], "frame mismatch")
    o2.require(raw["time_sec"] == reply["timestamp_sec"] == join["timestamp_sec"], "time mismatch")
    native = next(c for c in docs["capture"]["cases"] if c["variant"]["id"] == "native")
    ox, oy = native["crop_origin"]
    image = Image.open(root / plan["inputs"]["image"]["path"]).convert("RGB")
    o2.require(plan["inputs"]["image"]["sha256"] == reply["source_image_sha256"], "review image changed")
    with np.load(root / plan["inputs"]["arrays"]["path"], allow_pickle=False) as arrays:
        bgr = arrays["original_roi"]
        o2.require(hashlib.sha256(bgr.tobytes()).hexdigest()
                   == native["images"]["original_roi"]["array_sha256"], "ROI hash changed")
        h, w = bgr.shape[:2]
        o2.require(np.array_equal(np.asarray(image)[oy:oy+h, ox:ox+w], bgr[:, :, ::-1]),
                   "display pixels differ from capture")
    o2.require(len(raw["candidates"]) == len(join["candidates"]), "complete candidate roster required")
    band = next(r for r in reply["proposed_ranges"] if r["role"] == "Oil upper")
    lo, hi = band["source_y_cell_bounds"]
    roster = []
    interfaces = {c["candidate_input_index"]: c for c in docs["diagnostics"]["state"]["oil_interface_diagnostics"]["candidates"]}
    for i, (candidate, bound) in enumerate(zip(raw["candidates"], join["candidates"])):
        o2.require(i == bound["candidate_input_index"] and all(candidate[k] == bound[k]
                   for k in ("source", "kind", "y")), "candidate join changed")
        compatible = candidate["kind"] == "oil_air" and lo <= candidate["y"] <= hi
        path = interfaces.get(i, {}).get("path_aligned", {})
        center = [{"source_x_range_half_open": s["source_x_range"], "pooled_path_source_y": s["path_source_y"],
                   "scalar_range_membership_only": [b["id"] for b in reply["proposed_ranges"]
                        if b["source_y_cell_bounds"][0] <= s["path_source_y"] <= b["source_y_cell_bounds"][1]]}
                  for s in path.get("sectors", []) if s["source_x_range"][0] <= reply["source_x"] < s["source_x_range"][1]]
        o2.require(center == bound["center_sector_samples"], "pooled sector join changed")
        roster.append({"candidate_input_index": i, "candidate_sha256": o2.fingerprint_json(candidate),
                       "source": candidate["source"], "kind": candidate["kind"], "representative_y": candidate["y"],
                       "review_requested": compatible, "center_sector_samples": center,
                       "physical_role": "UNREVIEWED", "practical_acceptance": "UNREVIEWED"})
    selected = [r for r in roster if r["review_requested"]]
    o2.require([r["candidate_input_index"] for r in selected] == plan["candidate_indices"], "review roster changed")
    o2.require(len(selected) == 4, "layout requires the four complete compatible candidates")
    x0, y0, x1, y1 = plan["detail_crop_xyxy"]
    o2.require(ox <= x0 < x1 <= ox+w and oy <= y0 < y1 <= oy+h, "crop outside original ROI")
    scale = plan["detail_scale"]
    o2.require(type(scale) is int and scale == 6, "fixed review scale changed")
    sheet = Image.new("RGB", (1300, 805), "white")
    draw = ImageDraw.Draw(sheet)
    font, title = ImageFont.load_default(size=17), ImageFont.load_default(size=21)
    draw.text((20, 14), "Public compressor f1499 | candidate approximation review | no scores", fill="black", font=title)
    draw.text((20, 48), "The Oil range at X578 is already confirmed: rows 421-435. No new boundary-range question.", fill="black", font=font)
    draw.text((20, 76), "Yellow cross: candidate representative point. Cyan: stored pooled sector sample, NOT a contour.", fill="black", font=font)
    context = image.crop((ox, oy, ox+w, oy+h)).resize((w*2, h*2), Image.Resampling.NEAREST)
    sheet.paste(context, (20, 160))
    draw.text((20, 123), "Original context, 2x; no overlay", fill="black", font=font)
    draw.text((20, 608), "Question: which lower candidates are", fill="black", font=font)
    draw.text((20, 636), "acceptable Oil-level approximations here?", fill="black", font=font)
    draw.text((20, 674), "All / selected indices / none / cannot tell", fill="black", font=font)
    draw.text((20, 712), "Candidate scope only; no native path truth.", fill="black", font=font)
    for j, r in enumerate(selected):
        left, top = 510 + (j % 2)*390, 120 + (j // 2)*320
        label = r["source"].split(":")[0]
        draw.text((left, top), f"idx{r['candidate_input_index']} | {label}", fill="black", font=font)
        draw.text((left, top+24), f"X578 / representative Y{r['representative_y']:g}", fill="black", font=font)
        crop = image.crop((x0, y0, x1, y1)).resize(((x1-x0)*scale, (y1-y0)*scale), Image.Resampling.NEAREST)
        overlay = ImageDraw.Draw(crop)
        for s in r["center_sector_samples"]:
            a, b = s["source_x_range_half_open"]
            y = (s["pooled_path_source_y"]-y0+0.5)*scale
            overlay.line(((max(a,x0)-x0)*scale, y, (min(b,x1)-x0)*scale, y), fill="cyan", width=2)
        cx, cy = (reply["source_x"]-x0+0.5)*scale, (r["representative_y"]-y0+0.5)*scale
        overlay.line((cx-8,cy,cx+8,cy), fill="yellow", width=2)
        overlay.line((cx,cy-8,cx,cy+8), fill="yellow", width=2)
        sheet.paste(crop, (left, top+55))
        if r["center_sector_samples"]:
            draw.text((left, top+278), "Cyan: X[557,600), pooled Y429", fill="black", font=font)
    draw.text((20, 778), "Every interval-compatible Oil candidate is shown; all 23 original candidates remain in review.json.", fill="black", font=font)
    output.mkdir(parents=True)
    with (output / "candidate-review.png").open("xb") as f:
        sheet.save(f, format="PNG")
    result = {"schema": plan["schema"], "plan_sha256": o2.fingerprint_json(plan),
              "status": "AWAITING_SCOPED_PRACTICAL_ACCEPTANCE", "frame_index": raw["frame_index"],
              "time_sec": raw["time_sec"], "source_x": reply["source_x"], "confirmed_oil_range": band,
              "candidates": roster, "selection_rule": "All Oil candidates with representative Y in the closed Oil interval; no score selection.",
              "image_sha256": o2.sha256_file(output / "candidate-review.png"),
              "verification": {"original_roi_equals_saved_rgb": True, "candidate_joins": len(roster),
                               "reviewed_candidates": len(selected), "new_labels": 0},
              "decision": "NOT_EVALUATED", "model_calls": 0, "production_changed": False}
    with (output / "review.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result["verification"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "plan", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, reuse.o2.read_json(args.plan), args.output)))
