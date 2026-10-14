"""Render the newly missing upper input, without changing its mask or model.

The frozen archive renderer asks candidate positions. This follow-up instead
binds a pixel-mask cause and a new regional role question to that accepted point.
Reuse production preprocessing, the existing footprint reader and qualification.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
from oil_tracker.adapters.vision.preprocessing import preprocess, _digital_overlay_mask
from tests.diagnostics import s11_existing_material_reuse as reuse
from tests.diagnostics import s11_candidate_rgb_trial as rgb


def prepare(root, plan, output):
    o2 = reuse.o2
    started = reuse.g0.time.monotonic()
    o2.require(not output.exists(), "refuse overwrite")
    o2.require(plan["schema"] == "s11-source-upper-mask-review-v1", "unsupported review plan")
    for pin in plan["source_pins"]:
        reuse.g0.pinned_path(root, pin)
    qualified, packet, setup = [reuse.read_pin(root, plan["inputs"][k]) for k in ("qualified", "packet", "qualification_plan")]
    o2.require(qualified["plan_sha256"] == o2.fingerprint_json(setup), "qualification plan changed")
    for pin in setup["source_pins"]:
        reuse.g0.pinned_path(root, pin)
    o2.require(qualified["missing_accepted_inputs"] == [plan["subject_id"]], "missing accepted set changed")
    unit = next(u for u in qualified["candidate_rows"] if u["id"] == plan["subject_id"])
    subject = next(u for u in packet["subjects"] if u["id"] == unit["id"])
    o2.require(unit["practical_acceptance"] == "ACCEPTED_APPROXIMATION" and len(unit["variants"]) == 1,
               "accepted integer representative required")
    frame = qualified["frames"][str(unit["frame_index"]) ]
    path = reuse.g0.pinned_path(root, frame["source_image"])
    original = Image.open(path).convert("RGB")
    glass = InspectionRecipe.from_dict(reuse.read_pin(root, setup["inputs"]["recipe"])).glasses[0]
    bundle = build_mask_bundle(np.array(original)[:, :, ::-1].copy(), glass)
    pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
    visible = (bundle.effective_mask > 0) & (pre.glare_mask == 0)
    native = bundle.crop[:, :, ::-1].copy()
    o2.require(list(bundle.crop_origin) == frame["origin"] and list(native.shape[:2]) == frame["shape"]
               and rgb.native.array_hash(native) == frame["rgb_sha256"]
               and rgb.native.array_hash(visible) == frame["visible_sha256"], "qualified pixels or mask changed")
    sx, sy = map(int, unit["source_xy"])
    x, y = sx-bundle.crop_origin[0], sy-bundle.crop_origin[1]
    o2.require(rgb.context(native, visible, [x, y]) == {k: unit["variants"][0][k] for k in ("status", "sides")},
               "qualified footprint changed")
    region = np.zeros(visible.shape, bool)
    region[y-12:y-1, x-12:x+13] = True
    removed = region & (bundle.effective_mask > 0) & (pre.glare_mask > 0)
    overlay = _digital_overlay_mask(bundle.crop, bundle.effective_mask > 0) > 0
    saturated = (pre.gray >= glass.detector_settings.glare_threshold) & (bundle.effective_mask > 0)
    counts = {"upper_pixels": int(region.sum()), "outside_effective": int((region & (bundle.effective_mask == 0)).sum()),
        "removed_glare": int(removed.sum()), "remaining_visible": int((region & visible).sum()),
        "digital_overlay_overlap": int((removed & overlay).sum()), "saturation_overlap": int((removed & saturated).sum()),
        "other_glare_only": int((removed & ~overlay & ~saturated).sum())}
    o2.require(counts["upper_pixels"] == 275, "fixed upper footprint changed")
    crop = plan["display_crop_xyxy"]
    context = original.crop(tuple(crop))
    sheet = Image.new("RGB", (1500, 1220), "white")
    draw = ImageDraw.Draw(sheet)
    font, title = ImageFont.load_default(size=19), ImageFont.load_default(size=26)
    draw.text((15, 12), "sample3 B / 78.045 s | accepted Oil point retained | NEW question: upper region", fill="black", font=title)
    draw.text((15, 51), "Red box: original upper input. Red tint: pixels removed by the unchanged glare mask.", fill="black", font=font)
    draw.text((15, 81), "What is the removed bright region: fluid/Foam, reflection/structure, mixed, or cannot assess?", fill="black", font=font)
    masked = np.array(original)
    oy, ox = bundle.crop_origin[1], bundle.crop_origin[0]
    target = masked[oy:oy+removed.shape[0], ox:ox+removed.shape[1]]
    target[removed] = np.rint(target[removed]*0.5 + np.array([255, 0, 0])*0.5).astype(np.uint8)
    images = [context, Image.fromarray(masked).crop(tuple(crop))]
    for col, image in enumerate(images):
        left = 15+col*750
        panel = image.resize((720, 720), Image.Resampling.NEAREST)
        marks = ImageDraw.Draw(panel)
        px, py = (sx-crop[0])*2, (sy-crop[1])*2
        marks.rectangle((px-24, py-24, px+25, py-3), outline="red", width=2)
        marks.line((px-7, py, px+7, py), fill="yellow", width=2)
        marks.line((px, py-7, px, py+7), fill="yellow", width=2)
        sheet.paste(panel, (left, 155))
        draw.text((left, 121), "Original RGB" if col == 0 else "Same pixels + removed input overlay", fill="black", font=title)
        # Display enlargement only; inference never receives a resized input.
        zoom = image.crop((sx-crop[0]-12, sy-crop[1]-12, sx-crop[0]+13, sy-crop[1]+13))
        sheet.paste(zoom.resize((250, 250), Image.Resampling.NEAREST), (left, 900))
        draw.text((left+270, 915), "Same 25 x 25 native pixels, 10x display", fill="black", font=font)
        draw.text((left+270, 951), "Upper input: 11 x 25 pixels", fill="black", font=font)
        draw.text((left+270, 987), f"Removed: {counts['removed_glare']} / 275", fill="black", font=font)
        draw.text((left+270, 1023), "Complete upper 7 x 7 patches: 0", fill="black", font=font)
    draw.text((15, 1175), "The yellow Oil position is already accepted. No exact contour, mask correction or whole-video judgment is requested.", fill="black", font=font)
    output.mkdir(parents=True)
    with (output/"upper-mask-review.png").open("xb") as f:
        sheet.save(f, format="PNG")
    result = {"schema": plan["schema"], "plan_sha256": o2.fingerprint_json(plan), "subject": subject,
        "qualified_candidate_sha256": o2.fingerprint_json(unit), "source_upper_xyxy": [sx-12, sy-12, sx+13, sy-1],
        "counts": counts, "removed_mask_sha256": rgb.native.array_hash(removed),
        "qualified_rgb_and_visibility_equal": True, "image_sha256": o2.sha256_file(output/"upper-mask-review.png"),
        "question": plan["question"], "physical_role": "UNASSESSED", "status": "AWAITING_UPPER_REGION_ROLE",
        "new_model_calls": 0, "training_executed": False, "mask_changed": False, "production_changed": False,
        "resources": {"seconds": reuse.g0.time.monotonic()-started, "peak_rss": reuse.g0.peak_rss()}}
    o2.require(result["resources"]["seconds"] < plan["resource_limits"]["seconds"], "review time budget")
    rss = result["resources"]["peak_rss"]["bytes"]
    o2.require(rss is None or rss < plan["resource_limits"]["peak_rss_bytes"], "review memory budget")
    o2.write_new(output/"upper-mask-review.json", result)
    o2.require(sum(p.stat().st_size for p in output.iterdir()) <= plan["resource_limits"]["retained_bytes"], "review output budget")
    return {"counts": counts, "resources": result["resources"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "plan", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root.resolve(), reuse.o2.read_json(args.plan), args.output)))
