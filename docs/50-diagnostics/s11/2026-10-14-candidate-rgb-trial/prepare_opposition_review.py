"""Display the first unreviewed disjoint candidate group after the frozen trial.

The frozen public four-candidate renderer has a different input/subject envelope.
This adapter reuses the candidate RGB pin/roster reader; no model or new labels.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from tests.diagnostics import s11_candidate_rgb_trial as trial


def prepare(root, plan, output):
    o2 = trial.o2
    o2.require(not output.exists(), "refuse overwrite")
    o2.require(plan["schema"] == "s11-candidate-rgb-unknown-review-v1", "unsupported review")
    docs = {k: o2.read_json(trial.native.verified(root, p)) for k, p in plan["inputs"].items()}
    prepared, readout = docs["prepared"], docs["readout"]
    o2.require(readout["manifest"] == plan["inputs"]["prepared"], "trial input differs")
    trial.validate_units(prepared["units"], docs["trial_plan"])
    units = o2.unique(prepared["units"], "id", "prepared candidate")
    rows = o2.unique(readout["rows"], "id", "readout candidate")
    o2.require(list(units) == list(rows), "complete population differs")
    refs = {u["frame_id"]: u for u in units.values() if u["partition"] == "fit" and u["target"] == 0}

    def footprint(unit):
        return [min(v["source_xy"][1] for v in unit["variants"])-12,
                max(v["source_xy"][1] for v in unit["variants"])+12]

    potential = []
    for sid, row in rows.items():
        u = units[sid]
        o2.require(row["partition"] == u["partition"] and row["target"] == u["target"], "review binding changed")
        if row["partition"] != "unreviewed" or row["decision"] != trial.CLASSES[0] or u["frame_id"] not in refs:
            continue
        a, b = footprint(u), footprint(refs[u["frame_id"]])
        if a[1] < b[0] or b[1] < a[0]:
            potential.append(sid)
    o2.require(potential == plan["potential_ids"], "complete potential population changed")
    first = min((units[sid] for sid in potential), key=lambda u: u["query"]["frame"])["frame_id"]
    selected = [units[sid] for sid in potential if units[sid]["frame_id"] == first]
    o2.require(first == plan["frame_id"] and [u["id"] for u in selected] == plan["review_ids"], "first-frame selection changed")
    reference = refs[first]
    o2.require(reference["id"] == plan["reference_id"] and len(selected) == 3, "review layout subjects changed")
    frame = prepared["frames"][first]
    rgb, _ = trial.load_frame(root, frame)
    h, w, _ = rgb.shape
    scale = plan["display"]["scale"]
    o2.require((h, w, scale) == (104, 104, 3) and not plan["display"]["scores_shown"], "display geometry changed")
    image = Image.fromarray(rgb).resize((w*scale, h*scale), Image.Resampling.NEAREST)
    sheet = Image.new("RGB", (1410, 610), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=17)
    title = ImageFont.load_default(size=23)
    draw.text((20, 15), "sample4 | f1140 / 38 s | X595 | three NEW candidate-approximation questions", fill="black", font=title)
    draw.text((20, 52), "Green: existing accepted idx9 / Y844 (context only). Yellow: candidate representative point; NOT a contour.", fill="black", font=font)
    draw.text((20, 82), "Post-trial error discovery. No scores are displayed. Original source pixels, nearest-neighbor 3x.", fill="black", font=font)
    top = 175
    sheet.paste(image, (20, top))
    draw.text((20, 125), "Original context", fill="black", font=title)
    draw.text((20, 151), "No overlay", fill="black", font=font)
    marks = []
    for col, unit in enumerate(selected, 1):
        left = 20 + col*346
        panel = image.copy()
        overlay = ImageDraw.Draw(panel)
        for target, color in ((reference, "lime"), (unit, "yellow")):
            sx, sy = target["query"]["source_xy"]
            x, y = sx-frame["origin"][0], sy-frame["origin"][1]
            o2.require(0 <= x < w and 0 <= y < h, "mark outside source image")
            cx, cy = (x+0.5)*scale, (y+0.5)*scale
            overlay.line((cx-7, cy, cx+7, cy), fill=color, width=2)
            overlay.line((cx, cy-7, cx, cy+7), fill=color, width=2)
            marks.append({"panel": col, "id": target["id"], "source_xy": [sx, sy], "color": color})
        sheet.paste(panel, (left, top))
        q = unit["query"]
        draw.text((left, 125), f"idx{q['candidate_index']} / Y{q['source_xy'][1]:g}", fill="black", font=title)
        draw.text((left, 151), unit["id"], fill="black", font=font)
        draw.text((left, 498), "Accept / reject / cannot assess", fill="black", font=font)
    o2.require(np.array_equal(np.asarray(sheet)[top:top+h*scale:scale, 20:20+w*scale:scale], rgb), "display source pixels changed")
    draw.text((20, 545), "Question: is each YELLOW point an acceptable practical Oil-level approximation in this frame?", fill="black", font=title)
    draw.text((20, 581), "Reply for these three only. Existing green judgment stays closed; no labels transfer to other frames or paths.", fill="black", font=font)
    output.mkdir(parents=True)
    with (output/"opposition-review.png").open("xb") as f:
        sheet.save(f, format="PNG")
    result = {"schema": plan["schema"], "plan_sha256": o2.fingerprint_json(plan),
        "status": "AWAITING_SCOPED_PRACTICAL_ACCEPTANCE", "question": plan["question"], "scope": plan["scope"],
        "frame_id": first, "source_image": frame["rgb"], "source_recording": reference["source_recording"],
        "reference": {k: reference[k] for k in ("id", "query", "query_sha256", "label_basis")},
        "subjects": [{**{k: u[k] for k in ("id", "query", "query_sha256")}, "practical_acceptance": "UNASSESSED"} for u in selected],
        "all_disjoint_unreviewed_compatible": [{"id": sid, "frame_id": units[sid]["frame_id"], "query_sha256": units[sid]["query_sha256"],
                                               "source_xy": units[sid]["query"]["source_xy"]} for sid in potential],
        "image_sha256": o2.sha256_file(output/"opposition-review.png"), "marks": marks,
        "verification": {"original_context_pixel_equality": True, "prepared_rgb_pin_checked": True,
                         "all_records_bound": len(units), "potential_candidates": len(potential), "question_candidates": len(selected)},
        "model_calls": 0, "new_labels": 0, "production_changed": False}
    o2.write_new(output/"opposition-review.json", result)
    return result["verification"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "plan", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root.resolve(), trial.o2.read_json(args.plan), args.output)))
