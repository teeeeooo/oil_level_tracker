"""Review the contact type of the already accepted A point, not a native path.

Reuse one saved source image and the frozen baseline preprocessor. An empty
native edge inventory must remain empty; never draw a candidate Y as a contour.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tests.diagnostics import s11_overlay_mask_comparison as comparison
from tests.diagnostics import s11_native_role_qualification as native

o2, g0 = native.o2, native.g0


def prepare(root, plan, output):
    o2.require(not output.exists(), "refuse overwrite")
    for pin in plan["sources"]:
        g0.pinned_path(root, pin)
    docs = {k: native.read_pin(root, v) for k, v in plan["inputs"].items()}
    subject, = [s for s in docs["review"]["subjects"] if s["id"] == plan["subject_id"]]
    qualified, = [r for r in docs["qualification"]["candidate_rows"] if r["id"] == plan["subject_id"]]
    o2.require(qualified["practical_acceptance"] == "ACCEPTED_APPROXIMATION" and
               qualified["candidate_sha256"] == subject["candidate_sha256"] and
               qualified["source_xy"] == subject["source_xy"],
               "original candidate acceptance changed")
    for pin in docs["qualification_plan"]["source_pins"]:
        if pin["path"] != docs["comparison_plan"]["preprocessor"]:
            g0.pinned_path(root, pin)
    frame = cv2.imread(str(g0.pinned_path(root, subject["source_image"])))
    recipe = comparison.InspectionRecipe.from_dict(native.read_pin(root, docs["qualification_plan"]["inputs"]["recipe"]))
    bundle = comparison.build_mask_bundle(frame, recipe.glasses[0])
    pre = comparison.baseline(docs["comparison_plan"]).preprocess(
        bundle.crop, bundle.effective_mask, recipe.glasses[0].detector_settings)
    rgb = np.ascontiguousarray(bundle.crop[:, :, ::-1])
    visible = (bundle.effective_mask > 0) & (pre.glare_mask == 0)
    original = docs["qualification"]["frames"][str(subject["frame_index"])]
    o2.require(list(bundle.crop_origin) == original["origin"] and
               comparison.rgb.native.array_hash(rgb) == original["rgb_sha256"] and
               comparison.rgb.native.array_hash(visible) == original["visible_sha256"],
               "original Recipe/RGB/visibility changed")
    x, y = subject["source_xy"]; ox, oy = bundle.crop_origin
    rows, graph = g0.edge_bindings(pre.canny > 0, visible, int(x-ox), True)
    # This preparation is for this already-exposed point, with no alternative edge selection.
    o2.require(not rows and graph["vertices"] == 0, "native source result changed; review scope again")
    sheet = Image.new("RGB", (1100, 850), "white")
    draw = ImageDraw.Draw(sheet)
    font, title = ImageFont.load_default(size=19), ImageFont.load_default(size=25)
    draw.text((20, 15), "sample3 A | f2249 / 75.042 s | contact type only", fill="black", font=title)
    draw.text((20, 55), "Original ROI at 2x. Yellow cross = previously accepted candidate POINT, not a contour.", fill="black", font=font)
    plain = Image.fromarray(rgb).resize((480, 480), Image.Resampling.NEAREST)
    marked = plain.copy(); pen = ImageDraw.Draw(marked)
    px, py = (x-ox)*2+1, (y-oy)*2+1
    pen.line((px-9, py, px+9, py), fill="yellow", width=2)
    pen.line((px, py-9, px, py+9), fill="yellow", width=2)
    sheet.paste(plain, (20, 95)); sheet.paste(marked, (560, 95))
    overview = Image.fromarray(frame[:, :, ::-1]).resize((320, 180), Image.Resampling.NEAREST)
    pen = ImageDraw.Draw(overview)
    pen.rectangle((ox/4, oy/4, (ox+240)/4, (oy+240)/4), outline="cyan", width=2)
    sheet.paste(overview, (20, 625))
    draw.text((20, 585), "Full-frame location below (cyan box)", fill="black", font=font)
    draw.text((370, 635), "At the yellow point, what meets the liquid?", fill="black", font=title)
    draw.text((370, 685), "Empty space / Foam / another boundary / unclear", fill="black", font=font)
    draw.text((370, 735), "A's approximation is already accepted. B is not being re-reviewed.", fill="black", font=font)
    draw.text((20, 820), "No native edge is available here under the frozen baseline; this reply cannot label a pixel path.", fill="black", font=font)
    output.mkdir(parents=True)
    image = output/"sample3-contact-review.png"
    sheet.save(image)
    pixels = np.array(sheet)
    assert np.array_equal(pixels[95:575, 20:500], np.repeat(np.repeat(rgb, 2, axis=0), 2, axis=1))
    result = dict(schema="s11-source-contact-type-review-v1", plan_sha256=o2.fingerprint_json(plan),
        subject=subject, subject_sha256=o2.fingerprint_json(subject),
        source_recording=docs["review"]["source_recording"],
        prior_practical_acceptance=qualified["practical_acceptance"],
        source_image=subject["source_image"], display_sha256=o2.sha256_file(image),
        display=dict(plain_xyxy=[20,95,500,575], marked_xyxy=[560,95,1040,575],
                     scale=2, source_origin=list(bundle.crop_origin), point_source_xy=[x,y]),
        checks=dict(rgb_equal=True, visible_equal=True, displayed_plain_pixels_equal=True),
        native_input=dict(baseline_head=docs["comparison_plan"]["baseline_head"],
            preprocessor_sha256=docs["comparison_plan"]["baseline_preprocessor_sha256"],
            canny_nonzero=int(np.count_nonzero(pre.canny)), visible_nonzero=int(np.count_nonzero(visible)),
            canny_sha256=comparison.rgb.native.array_hash(pre.canny), rows=rows, graph=graph,
            status="NO_NATIVE_EDGE_PATH", new_thresholds=False),
        question_ko="A의 노란 점이 표시된 경계에서 액체와 맞닿은 것은 빈공간인가요, 거품인가요? 다른 경계이거나 불분명하면 그대로 알려주세요.",
        scope="Contact type at previously accepted candidate only; no native path, pure-side, motion, exact-Y or whole-window truth",
        status="PENDING_CONTACT_TYPE_REVIEW", native_labels_created=0, model_calls=0,
        training_executed=False, production_changed=False, video_decodes=0)
    o2.write_new(output/"sample3-contact-review.json",result)
    return {"status": result["status"], "native_input": result["native_input"], "native_labels_created": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "plan", "output"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root.resolve(), o2.read_json(args.plan), args.output)))
