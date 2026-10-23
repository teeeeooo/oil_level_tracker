"""Raw-pixel review zoom for a human Oil-boundary reading, and the reading of the reviewer's marks.

Generalises the review-013/review-014 generators (kept in their managed runs) so the same
material can be made on target Windows, where the media stay.

``prepare`` decodes the requested frames sequentially (exact frame indices), crops a box around
one Glass's Recipe ellipse, upscales it by nearest neighbour and draws only a source-Y ruler in
the margins: no detector value, ellipse, mask or band line. ``read-marks`` differences a copy of
the sheet that the reviewer marked in red against the clean sheet and maps every mark to source
coordinates with the geometry stored in the manifest.

Usage (repository root, ``PYTHONPATH=src``):
    python -m tests.diagnostics.s11_review_zoom prepare --video V --recipe R --glass-name Accum \
        --frames 16128,16140 --review-id review-012 --out OUT
    python -m tests.diagnostics.s11_review_zoom read-marks --manifest OUT/review-zoom.json \
        --marked MARKED.png
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

BACKGROUND = (24, 24, 24)
INK = (235, 235, 235)
TICK = (150, 150, 150)
LEFT, RIGHT, TOP, BOTTOM, HEADER = 58, 14, 30, 6, 34
COLUMNS = 3
BOX_MARGIN_PX = 8
TARGET_CROP_PX = 600
MIN_MARK_AREA = 15


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def zoom_box(ellipse, image_shape: tuple[int, ...]) -> tuple[int, int, int, int]:
    """Box around the Recipe ellipse plus a small margin, clipped to the image."""
    height, width = image_shape[:2]
    x0 = max(0, int(np.floor(ellipse.center_x - ellipse.radius_x)) - BOX_MARGIN_PX)
    y0 = max(0, int(np.floor(ellipse.center_y - ellipse.radius_y)) - BOX_MARGIN_PX)
    x1 = min(width, int(np.ceil(ellipse.center_x + ellipse.radius_x)) + BOX_MARGIN_PX)
    y1 = min(height, int(np.ceil(ellipse.center_y + ellipse.radius_y)) + BOX_MARGIN_PX)
    return x0, y0, x1, y1


def auto_scale(box: tuple[int, int, int, int]) -> int:
    return max(2, min(8, round(TARGET_CROP_PX / max(box[3] - box[1], 1))))


def ruler_steps(scale: int) -> tuple[int, int]:
    """(minor tick, labelled tick) in source px; 5/10 as in review-013/014 at scale 4 and above."""
    return (5, 10) if scale >= 4 else (10, 20)


def panel(image: np.ndarray, box: tuple[int, int, int, int], scale: int, title: str) -> np.ndarray:
    x0, y0, x1, y1 = box
    crop = cv2.resize(image[y0:y1, x0:x1], None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    canvas = np.full((crop.shape[0] + TOP + BOTTOM, crop.shape[1] + LEFT + RIGHT, 3), BACKGROUND, np.uint8)
    canvas[TOP:TOP + crop.shape[0], LEFT:LEFT + crop.shape[1]] = crop
    cv2.putText(canvas, title, (LEFT, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, INK, 1, cv2.LINE_AA)
    minor, label = ruler_steps(scale)
    for y in range(y0 - y0 % minor + (minor if y0 % minor else 0), y1, minor):
        row = TOP + (y - y0) * scale + scale // 2  # centre of source row y
        labelled = y % label == 0
        length = 12 if labelled else 6
        cv2.line(canvas, (LEFT - length, row), (LEFT - 1, row), INK if labelled else TICK, 1)
        cv2.line(canvas, (LEFT + crop.shape[1], row), (LEFT + crop.shape[1] + length - 2, row),
                 INK if labelled else TICK, 1)
        if labelled:
            cv2.putText(canvas, str(y), (4, row + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, INK, 1, cv2.LINE_AA)
    return canvas


def sheet(panels: list[np.ndarray], header: str) -> np.ndarray:
    height, width = panels[0].shape[:2]
    blank = np.full((height, width, 3), BACKGROUND, np.uint8)
    rows = [panels[start:start + COLUMNS] for start in range(0, len(panels), COLUMNS)]
    grid = np.concatenate([
        np.concatenate([*row, *([blank] * (COLUMNS - len(row)))], axis=1) for row in rows
    ], axis=0)
    strip = np.full((HEADER, grid.shape[1], 3), BACKGROUND, np.uint8)
    cv2.putText(strip, header, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.62, INK, 1, cv2.LINE_AA)
    return np.concatenate([strip, grid], axis=0)


def source_point(column: float, row: float, box: list[int], scale: int, panel_size: list[int]) -> tuple[int, float, float]:
    """Sheet pixel (column, row) -> (panel number, source x, source y), as in the review-013/014 replies."""
    width, height = panel_size
    panel_column, panel_row = int(column // width), int((row - HEADER) // height)
    x = box[0] + (column - width * panel_column - LEFT) / scale
    y = box[1] + (row - HEADER - height * panel_row - TOP) / scale - 0.5
    return panel_row * COLUMNS + panel_column, x, y


def decode(video: Path, frames: list[int]) -> dict[int, tuple[np.ndarray, float]]:
    capture = cv2.VideoCapture(str(video))
    if not capture.isOpened():
        raise OSError(f"Cannot open {video}")
    wanted, found, index = set(frames), {}, 0
    while wanted - set(found):
        ok, image = capture.read()
        if not ok:
            raise RuntimeError(f"decode stopped at frame {index}; missing {sorted(wanted - set(found))}")
        if index in wanted:
            found[index] = (image, capture.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
        index += 1
    capture.release()
    return found


def prepare(video: Path, recipe_path: Path, glass_name: str, frames: list[int], review_id: str,
            output: Path, scale: int | None = None) -> dict:
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository

    recipe = JsonRecipeRepository().load(recipe_path)
    matches = [glass for glass in recipe.glasses if glass.name == glass_name]
    if len(matches) != 1:
        raise SystemExit(f"Glass {glass_name!r} matches {len(matches)} Recipe glasses: "
                         f"{[glass.name for glass in recipe.glasses]}")
    glass = matches[0]
    ellipse = glass.geometry.ellipse
    decoded = decode(video, sorted(set(frames)))
    first = decoded[frames[0]][0]
    box = zoom_box(ellipse, first.shape)
    scale = scale or auto_scale(box)
    output.mkdir(parents=True, exist_ok=False)
    panels, records = [], []
    for frame in frames:
        image, seconds = decoded[frame]
        records.append({"frame_index": frame, "decoded_time_sec": round(seconds, 4),
                        "frame_sha256": sha256(image.tobytes())})
        panels.append(panel(image, box, scale, f"{seconds:.2f} s  (f{frame})"))
    header = (f"{review_id} | {glass.name} | raw pixels, nearest-neighbour x{scale} | ruler = source Y (px) | "
              "no detector or ROI overlay")
    image = sheet(panels, header)
    png = output / "review-zoom.png"
    if not cv2.imwrite(str(png), image, [cv2.IMWRITE_PNG_COMPRESSION, 9]):
        raise OSError(f"Cannot save {png} (use an ASCII-only output path)")
    manifest = {
        "schema": "s11-review-zoom-v1",
        "review_id": review_id,
        "video": {"path": str(video), "sha256": sha256(video.read_bytes()), "size_bytes": video.stat().st_size},
        "recipe": {"path": str(recipe_path), "sha256": sha256(recipe_path.read_bytes()), "name": recipe.name},
        "glass": {"id": glass.id, "name": glass.name,
                  "ellipse": {"center_x": ellipse.center_x, "center_y": ellipse.center_y,
                              "radius_x": ellipse.radius_x, "radius_y": ellipse.radius_y}},
        "zoom_source_xyxy": list(box),
        "scale": scale,
        "ruler_px": dict(zip(("minor", "labelled"), ruler_steps(scale))),
        "panel_size": [panels[0].shape[1], panels[0].shape[0]],
        "frames": records,
        "image": {"path": png.name, "sha256": sha256(png.read_bytes()), "width": image.shape[1],
                  "height": image.shape[0]},
    }
    (output / "review-zoom.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return manifest


def red_marks(clean: np.ndarray, marked: np.ndarray) -> np.ndarray:
    """Pixels the reviewer changed to a red hue (the review-014 rule)."""
    changed = np.abs(clean.astype(int) - marked.astype(int)).sum(axis=2) > 60
    blue, green, red = (marked[:, :, channel].astype(int) for channel in range(3))
    return changed & (red > 150) & (red - green > 80) & (red - blue > 80)


def read_marks(manifest_path: Path, marked_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    clean = cv2.imread(str(manifest_path.parent / manifest["image"]["path"]))
    marked = cv2.imread(str(marked_path))
    if marked is None:
        raise SystemExit(f"Cannot read {marked_path}")
    if marked.shape != clean.shape:
        raise SystemExit(f"STOP: marked image is {marked.shape[1]}x{marked.shape[0]}, "
                         f"the clean sheet is {clean.shape[1]}x{clean.shape[0]}; send the unscaled image")
    mask = red_marks(clean, marked)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    frames = [{"frame_index": record["frame_index"], "decoded_time_sec": record["decoded_time_sec"], "marks": []}
              for record in manifest["frames"]]
    for label in range(1, count):
        if stats[label][cv2.CC_STAT_AREA] < MIN_MARK_AREA:
            continue
        number, x, y = source_point(*centroids[label], manifest["zoom_source_xyxy"], manifest["scale"],
                                    manifest["panel_size"])
        if number < len(frames):
            frames[number]["marks"].append([round(x, 1), round(y, 1)])
    for frame in frames:
        frame["marks"].sort()
        ys = [y for _x, y in frame["marks"]]
        frame["y_range"] = [min(ys), max(ys)] if ys else None
    unchanged = np.abs(clean.astype(int) - marked.astype(int)).sum(axis=2) <= 60
    return {"schema": "s11-review-marks-v1", "review_id": manifest["review_id"],
            "marked_image": {"path": str(marked_path), "sha256": sha256(marked_path.read_bytes())},
            "clean_image_sha256": manifest["image"]["sha256"],
            "changed_not_red_px": int((~unchanged & ~mask).sum()), "frames": frames}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    modes = parser.add_subparsers(dest="mode", required=True)
    make = modes.add_parser("prepare")
    make.add_argument("--video", type=Path, required=True)
    make.add_argument("--recipe", type=Path, required=True)
    make.add_argument("--glass-name", required=True)
    make.add_argument("--frames", required=True, help="Comma-separated frame indices, in display order")
    make.add_argument("--review-id", required=True)
    make.add_argument("--out", type=Path, required=True)
    make.add_argument("--scale", type=int)
    marks = modes.add_parser("read-marks")
    marks.add_argument("--manifest", type=Path, required=True)
    marks.add_argument("--marked", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.mode == "prepare":
        frames = [int(value) for value in args.frames.split(",") if value.strip()]
        result = prepare(args.video, args.recipe, args.glass_name, frames, args.review_id, args.out, args.scale)
    else:
        result = read_marks(args.manifest, args.marked)
    print(json.dumps(result, indent=1, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
