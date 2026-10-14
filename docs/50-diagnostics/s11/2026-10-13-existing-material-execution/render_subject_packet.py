"""Render all native fragments in the reviewed intervals or an unlabelled row.

The frozen N1-N5 renderers hard-code those subjects. This adapter only displays
this supplement's complete interval-compatible roster using original RGB pixels.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from tests.diagnostics import s11_existing_material_reuse as reuse


def render(root, manifest, readout, output, row_y=None):
    reuse.o2.require(not output.exists(), "refuse overwrite")
    reuse.o2.require(readout["manifest_sha256"] == reuse.o2.fingerprint_json(manifest), "readout mismatch")
    packet, = readout["native_review_packets"]
    gm = reuse.read_pin(root, manifest["inputs"]["g0_manifest"])
    reply = reuse.read_pin(root, gm["inputs"]["public_position_reply"])
    source = root / "docs/50-diagnostics/s11/2026-10-12-public-compressor-source/native-at-50.png"
    reuse.o2.require(reuse.o2.sha256_file(source) == reply["source_image_sha256"], "source changed")
    image = Image.open(source).convert("RGB")
    ox, oy = packet["geometry"]["origin"]
    height, width = packet["geometry"]["shape"]
    plan = reuse.read_pin(root, gm["inputs"]["foam_preflight"])
    case = next(c for c in plan["cases"] if c["id"] == packet["case_id"])
    reuse.g0.pinned_path(root, {"path": case["raster"], "sha256": plan["pins"][case["raster"]]})
    rgb, _, _ = reuse.g0.material.load_case(root, case)
    reuse.o2.require(np.array_equal(np.asarray(image)[oy:oy+height, ox:ox+width], rgb),
                     "native display differs from captured RGB")
    by_id = {f["id"]: f for f in packet["fragments"]}
    if row_y is None:
        entries = [(band["original"]["role"], by_id[fid]) for band in packet["intervals"]
                   for fid in band["compatible_fragments"]]
        reuse.o2.require(len(entries) == 7, "review layout needs complete seven-fragment roster")
    else:
        entries = [("unreviewed row", f) for f in packet["fragments"] if row_y in f["fixed_column_source_ys"]]
        reuse.o2.require(1 <= len(entries) <= 7, "row review layout needs one to seven fragments")
    height_px = 570 if row_y is not None and len(entries) <= 3 else 1030
    sheet = Image.new("RGB", (1600, height_px), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=17)
    title = ImageFont.load_default(size=22)
    draw.text((20, 12), "Public compressor f1499 | saved native paths | ALL ROLES UNREVIEWED", fill="black", font=title)
    subtitle = ("Original reviewed intervals are retained. A path inside an interval is NOT a positive label."
                if row_y is None else f"New question: every saved fragment at source Y={row_y:g}. Location alone assigns no physical role.")
    draw.text((20, 44), subtitle, fill="black", font=font)
    context = image.crop((ox, oy, ox+width, oy+height))
    context.thumbnail((370, 350), Image.Resampling.NEAREST)
    sheet.paste(context, (15, 140))
    draw.text((15, 86), "Original RGB context (no overlay)", fill="black", font=font)
    draw.text((15, 111), f"X={ox}..{ox+width-1} Y={oy}..{oy+height-1}", fill="black", font=font)
    baseline = reuse.read_pin(root, manifest["inputs"]["g0_readout"])
    case_context = next(c for c in baseline["contexts"] if c["id"] == packet["case_id"])
    saved = {f["fragment_id"]: f for r in case_context["rows"] for f in r["incident_fragments"]}
    for _, item in entries:
        native_xy = [[x-ox, y-oy] for x, y in item["source_path_xy"]]
        reuse.o2.require(reuse.o2.fingerprint_json(native_xy) == saved[item["fragment_id"]]["path_sha256"], "display path changed")
    roster = []
    for number, (role, item) in enumerate(entries, start=1):
        xbase, ybase = (number % 4)*400+15, (number//4)*460+86
        xy = np.asarray(item["source_path_xy"])
        x0, y0 = np.maximum(xy.min(0)-16, [ox, oy])
        x1, y1 = np.minimum(xy.max(0)+17, [ox+width, oy+height])
        scale = max(1, min(370//int(x1-x0), 320//int(y1-y0)))
        crop = image.crop(tuple(map(int, (x0, y0, x1, y1))))
        crop = crop.resize((crop.width*scale, crop.height*scale), Image.Resampling.NEAREST)
        lines = ImageDraw.Draw(crop)
        points = [((int(x)-int(x0)+.5)*scale, (int(y)-int(y0)+.5)*scale) for x, y in xy]
        lines.line(points, fill="magenta", width=2)
        sheet.paste(crop, (xbase, ybase+100))
        draw.text((xbase, ybase), f"fragment-{item['fragment_id']} | {role.replace('upper', 'range')}", fill="black", font=font)
        draw.text((xbase, ybase+24), f"Fixed-X Y={item['fixed_column_source_ys']} | UNREVIEWED", fill="black", font=font)
        state = item["context_support"]
        support = state.get("sides", {})
        sizes = "/".join(str(support[k]["complete_patches"]) for k in ("upper", "lower")) if support else "orientation unresolved"
        draw.text((xbase, ybase+48), f"7x7 support U/L: {sizes}", fill="black", font=font)
        draw.text((xbase, ybase+72), f"X {x0}..{x1-1}; Y {y0}..{y1-1}; zoom {scale}x", fill="black", font=font)
        roster.append({"id": item["id"], "path_sha256": reuse.o2.fingerprint_json(item["source_path_xy"]),
                       "display_crop_xyxy": list(map(int, (x0,y0,x1,y1))), "scale": scale})
    draw.text((20, height_px-36), "Previously reviewed Foam upper and lower Oil paths are outside this new row question."
              if row_y is not None else "Lower Oil paths are preservation guards, NOT negative labels for an external-surface classifier.",
              fill="black", font=font)
    with output.open("xb") as stream:
        sheet.save(stream, format="PNG")
    return {"source_sha256": reuse.o2.sha256_file(source), "image_sha256": reuse.o2.sha256_file(output),
            "original_roi_equals_saved_rgb": True, "subjects": roster, "physical_labels_created": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("root", "manifest", "readout", "output"):
        parser.add_argument("--"+arg, type=Path, required=True)
    parser.add_argument("--row-y", type=float)
    args = parser.parse_args()
    print(json.dumps(render(args.root, json.loads(args.manifest.read_text(encoding="utf-8")),
                            json.loads(args.readout.read_text(encoding="utf-8")), args.output, args.row_y)))
