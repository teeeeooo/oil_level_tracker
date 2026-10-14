"""Reuse two closed sample3 regional views for a new candidate-only question.

Frozen earlier renderers consume live capture files or one trial's population.
This archive adapter joins original current/native records without re-execution.
It does not extract the user's painted dots or assign labels from old track IDs.
"""
import argparse
import gzip
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from tests.diagnostics import s11_existing_material_reuse as reuse


def read_archive(root, pin, size):
    """This pinned 37-frame archive exceeds the small CR1 JSON reader's cap."""
    reuse.o2.require(type(size) is int and 0 < size <= 100_000_000, "archive expansion budget")
    path = reuse.g0.pinned_path(root, pin)
    with gzip.open(path, "rb") as stream:
        data = stream.read(size+1)
    reuse.o2.require(len(data) == size, "archive expanded bytes changed")
    return json.loads(data)


def prepare(root, plan, output):
    o2 = reuse.o2
    o2.require(not output.exists(), "refuse overwrite")
    o2.require(plan["schema"] == "s11-oil-candidate-source-expansion-review-v1", "unsupported plan")
    for pin in plan["inputs"].values():
        reuse.g0.pinned_path(root, pin)
    started = reuse.g0.time.monotonic()
    archive = read_archive(root, plan["inputs"]["archive"], plan["archive_expanded_bytes"])
    reply = reuse.read_pin(root, plan["inputs"]["regional_reply"])
    o2.require(reply["status"] == "CLOSED" and reply["qualification"] == "REGIONAL_PHYSICAL_ROLE_AND_VISIBILITY_ONLY", "regional scope changed")
    for pin in (reply["source_video"], reply["clean_review_image"], reply["user_marked_image"]):
        reuse.g0.pinned_path(root, pin)
    clean = np.array(Image.open(root/reply["clean_review_image"]["path"]).convert("RGB"))
    glass = archive["recipe"]["glasses"][0]
    x = glass["geometry"]["ellipse"]["center_x"]
    o2.require(x == 835 and float(x).is_integer(), "archived candidate query center changed")
    crop = plan["display"]["source_crop_xyxy"]
    scale = plan["display"]["scale"]
    o2.require(crop == reply["display_mapping"]["source_crop_xyxy"] and scale == 2
               and not plan["display"]["scores_shown"], "review display mapping changed")
    sheet = Image.new("RGB", (1500, 1020), "white")
    draw = ImageDraw.Draw(sheet)
    font, title = ImageFont.load_default(size=18), ImageFont.load_default(size=25)
    draw.text((15, 14), "sample3 A / B | candidate approximation only | regional Oil presence already confirmed", fill="black", font=title)
    draw.text((15, 54), "Yellow cross: stored candidate representative point. Cyan: saved pooled sector sample, NOT a contour.", fill="black", font=font)
    draw.text((15, 84), "Original pixels, 2x nearest-neighbor. No model scores, new fit, painted-dot extraction or tracking labels.", fill="black", font=font)
    population, subjects, checks = [], [], []
    o2.require(len(reply["reviewed_frames"]) == len(plan["subjects"]) == 2, "two original views required")
    for col, view in enumerate(reply["reviewed_frames"]):
        frame, sec = view["frame_index"], view["source_timestamp_sec"]
        raw = next(r for r in archive["saved_current_detections"] if r["frame_index"] == frame)
        native = next(r for r in archive["native_frames"] if r["frame"] == frame)
        case = next(r for r in archive["analysis"]["cases"] if r["frame"] == frame)
        o2.require(raw["time_sec"] == native["time_sec"] == sec, "source time changed")
        diag = native["state"]["oil_interface_diagnostics"]
        o2.require(not diag["resize"] and diag["source_frame_index"] == frame, "native geometry changed")
        indexed = {r["candidate_input_index"]: r for r in diag["candidates"]}
        o2.require(len(indexed) == len(diag["candidates"]) == len(raw["candidates"]), "complete candidate join required")
        for i, c in enumerate(raw["candidates"]):
            bound = indexed[i]
            o2.require(c["kind"] == "oil_air" and (c["source"], c["y"]) ==
                       (bound["source"], bound["canonical_y"]), "source/index/Y join changed")
            population.append({"id": f"s3-f{frame}-idx{i}", "frame_index": frame, "candidate_input_index": i,
                "candidate_sha256": o2.fingerprint_json(c), "source": c["source"], "source_xy": [x, c["y"]],
                "practical_acceptance": "UNASSESSED", "native_path_role": "NOT_QUALIFIED"})
        members = [r for r in case["upper_row"] if r["source"] == "material_path"]
        o2.require(len(members) == 1, "unique archived upper material member required")
        selected = [r for r in population if r["frame_index"] == frame and
                    (r["source"], r["source_xy"][1]) == (members[0]["source"], members[0]["y"])]
        o2.require(len(selected) == 1, "exact selected candidate required")
        candidate = selected[0]
        subject = {"view": view["view"], **{k: candidate[k] for k in ("id", "frame_index", "candidate_input_index", "candidate_sha256", "source", "source_xy")}, "time_sec": sec}
        o2.require(subject == plan["subjects"][col], "frozen review subject changed")
        path = indexed[candidate["candidate_input_index"]]["path_aligned"]
        centers = [s for s in path["sectors"] if s["source_x_range"][0] <= x < s["source_x_range"][1]]
        o2.require(len(centers) == 1, "one stored center-sector sample required")
        center = centers[0]
        for pin in (view["original_full_frame"], view["original_crop"]):
            reuse.g0.pinned_path(root, pin)
        image = Image.open(root/view["original_full_frame"]["path"]).convert("RGB")
        context = image.crop(tuple(crop))
        stored = Image.open(root/view["original_crop"]["path"]).convert("RGB")
        o2.require(np.array_equal(np.array(context), np.array(stored)), "source crop differs")
        panel = context.resize((720, 720), Image.Resampling.NEAREST)
        dx, dy, dw, dh = view["display_rect_xywh"]
        o2.require(np.array_equal(np.array(panel), clean[dy:dy+dh, dx:dx+dw]), "pixels differ from closed source review")
        overlay = ImageDraw.Draw(panel)
        a, b = center["source_x_range"]
        py = (center["path_source_y"]-crop[1]+0.5)*scale
        overlay.line(((a-crop[0])*scale, py, (b-crop[0])*scale, py), fill="cyan", width=2)
        cx, cy = (x-crop[0]+0.5)*scale, (candidate["source_xy"][1]-crop[1]+0.5)*scale
        o2.require(0 <= cx < 720 and 0 <= cy < 720, "candidate mark outside view")
        overlay.line((cx-8, cy, cx+8, cy), fill="yellow", width=2)
        overlay.line((cx, cy-8, cx, cy+8), fill="yellow", width=2)
        left, top = 15+col*750, 180
        sheet.paste(panel, (left, top))
        draw.text((left, 123), f"{view['view']} | f{frame} / {sec:.3f} s | idx{candidate['candidate_input_index']} / Y{candidate['source_xy'][1]:g}", fill="black", font=title)
        draw.text((left, 155), f"X{x:g}; cyan pooled center-sector Y{center['path_source_y']:g}", fill="black", font=font)
        draw.text((left, 915), "Is the YELLOW point an acceptable Oil-level approximation?", fill="black", font=font)
        subjects.append({**subject, "source_image": view["original_full_frame"], "center_sector": center,
                         "practical_acceptance": "UNASSESSED", "regional_role": "OIL_CONFIRMED_ORIGINAL_SCOPE"})
        checks.append({"frame_index": frame, "candidate_joins": len(indexed), "source_crop_equal": True,
                       "closed_review_pixels_equal": True, "old_candidate_and_path_not_reinterpreted": True})
    draw.text((15, 963), "Reply A / B: accept, reject or cannot assess. No exact-pixel truth or whole-video quality claim is requested.", fill="black", font=font)
    draw.text((15, 994), "sample3's position/focus limitations and previous C/D judgments remain unchanged.", fill="black", font=font)
    output.mkdir(parents=True)
    with (output/"candidate-review.png").open("xb") as f:
        sheet.save(f, format="PNG")
    result = {"schema": plan["schema"], "plan_sha256": o2.fingerprint_json(plan),
        "status": "AWAITING_TWO_SCOPED_CANDIDATE_JUDGMENTS", "source_recording": reply["source_video"],
        "subjects": subjects, "candidate_population": population, "checks": checks,
        "image_sha256": o2.sha256_file(output/"candidate-review.png"),
        "question": plan["question"], "scope": plan["scope"], "exposure": plan["exposure"],
        "new_labels": 0, "model_calls": 0, "training_executed": False, "video_decode": False,
        "production_changed": False, "model_specific_input_readiness": "NOT_PREPARED",
        "resources": {"seconds": reuse.g0.time.monotonic()-started, "peak_rss": reuse.g0.peak_rss(),
                      "archive_expanded_bytes": plan["archive_expanded_bytes"]}}
    o2.require(result["resources"]["seconds"] < plan["resources"]["seconds"], "preparation time budget")
    rss = result["resources"]["peak_rss"]["bytes"]
    o2.require(rss is None or rss < plan["resources"]["peak_rss_bytes"], "preparation memory budget")
    o2.write_new(output/"review.json", result)
    o2.require(sum(p.stat().st_size for p in output.iterdir()) <= plan["resources"]["retained_bytes"], "output budget")
    return {"candidate_records": len(population), "question_candidates": len(subjects), "pixel_checks": checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "plan", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root.resolve(), reuse.o2.read_json(args.plan), args.output)))
