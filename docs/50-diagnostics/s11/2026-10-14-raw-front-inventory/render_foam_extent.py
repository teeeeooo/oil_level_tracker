"""Pixel-exact regional Foam-upper question; no proposed upper contour."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]


def render(plan, work):
    def read(pin):
        path = ROOT / pin["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"]
        return json.loads(path.read_text(encoding="utf-8"))
    for pin in plan["sources"]:
        assert hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"]
    proposal = read(plan["inputs"]["proposal"])
    reply = read(plan["inputs"]["reply"])
    assert reply["answers"][0]["role"] == "FOAM_LOWER_LIQUID_INTERFACE"
    view, = proposal["views"]
    source = ROOT / view["source"]["path"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == view["source"]["sha256"]
    original = np.array(Image.open(source).convert("RGB"))
    subject, = proposal["subjects"]
    ox, oy, width, height = plan["source_roi_xywh"]
    roi = original[oy:oy+height, ox:ox+width]
    marked = roi.copy()
    for x, y in subject["source_path_xy"]:
        assert 0 <= x-ox < width and 0 <= y-oy < height
        marked[y-oy, x-ox] = (255, 0, 255)
    scale, px, py = 3, 100, 135
    image = Image.new("RGB", (1050, 1150), "white")
    pixels = np.repeat(np.repeat(marked, scale, axis=0), scale, axis=1)
    image.paste(Image.fromarray(pixels), (px, py))
    draw = ImageDraw.Draw(image)
    font = lambda size: ImageFont.truetype(plan["font"], size)
    draw.text((25, 18), "거품 상단 위치 확인 — base_sample_1 / f144", font=font(30), fill="black")
    draw.text((25, 63), "보라색: 확인된 거품–액체 하단 / 왼쪽 숫자: 원본 Y좌표", font=font(24), fill="black")
    cx = px + (696-ox)*scale
    draw.text((cx, 110), "중앙 X696", anchor="mm", font=font(23), fill="#006888")
    draw.polygon([(cx-5, 123), (cx+5, 123), (cx, 132)], fill="#006888")
    for y in [240, 280, 320, 360, 400, 440, 480, 500]:
        sy = py + (y-oy)*scale
        draw.text((27, sy-15), str(y), font=font(24), fill="black")
        draw.line((78, sy, 96, sy), fill="black", width=2)
    draw.text((25, 1045), "중앙에서 거품의 윗경계는 대략 어느 Y인가요?", font=font(26), fill="black")
    draw.text((25, 1090), "정확한 픽셀은 필요 없습니다. 불분명하면 ‘판독 불가’로 남깁니다.", font=font(24), fill="black")
    assert np.array_equal(np.array(image)[py:py+height*scale, px:px+width*scale], pixels)
    output = work / "base-foam-upper-review.png"
    assert not output.exists()
    image.save(output)
    review = dict(schema="s11-regional-role-location-review-v1", source=view["source"],
        frame=144, time_sec=4.8048, source_roi_xywh=plan["source_roi_xywh"], scale=scale,
        image_origin_xy=view["image_origin_xy"], fixed_source_column=696,
        display=dict(path=plan["destination"]+"/"+output.name,
                     sha256=hashlib.sha256(output.read_bytes()).hexdigest()),
        existing_lower_contact=plan["inputs"]["reply"],
        question_ko="같은 화면 중앙 X696에서 거품의 윗경계는 대략 어느 Y인가요? 불분명하면 판독 불가로 남깁니다.",
        pixel_verification=dict(original_roi_unchanged_except_known_path=True,
            complete_display_panel_equal=True, marked_existing_path_pixels=len(subject["source_path_xy"]),
            invented_upper_path_pixels=0),
        scope="Regional Foam-upper location only; no exact path, pure-side, motion or adjacent-frame truth",
        physical_role="PENDING_USER_REPLY", qualified_new_paths=0)
    with (work / "base-foam-upper-review.json").open("x", encoding="utf-8") as handle:
        json.dump(review, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(review["pixel_verification"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    render(json.loads(args.plan.read_text(encoding="utf-8")), args.work)
