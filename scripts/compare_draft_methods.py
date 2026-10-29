"""Compare Oil-draft methods on the local samples with truth (a diagnostic, not product code).

Plan and result: docs/50-diagnostics/2026-10-29-draft-method-comparison.md. Only this script
reads the v1 .oilrecipe, .oiltruth and .provisional-truth.json files; the product never does.

Usage:
  python scripts/compare_draft_methods.py [--samples sample] [--out DIR]
      the local samples with truth: methods A, B, C (fixed before the run) and D, E (after it)
  python scripts/compare_draft_methods.py --video VIDEO --recipe RECIPE.recipe.json [--out DIR]
      a v2 Recipe on any video, without truth: one picture per Glass for the user to judge
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

SAMPLES = ("base_sample_1", "sample2", "sample4")
RATE = 2.0           # columns per second (Product SSOT §3)
BAND = 0.4           # half-width of the sampled band, as a fraction of radius_x
HIT_PERCENT = 5.0    # a hit is an error within this share of the Glass height
MAX_TIME_GAP = 0.25  # s between a truth time and its column
# method B and C parameters, fixed in the plan before the run
EDGE_FULL = 24.0     # luma step that counts as a full-strength edge
JUMP_WEIGHT = 5.0    # cost of a jump of the whole Glass height
MAX_JUMP = 0.25      # of the Glass height per column
WEAK = 0.25
WEAK_WINDOW = 10     # columns (5 s)
WEAK_MIN_RUN = 4     # columns (2 s)
BG_MIX = 0.3
# added after the first run (labelled post-hoc in the diagnostic): D uses only the background view
POST_HOC_MIX = {"D": 1.0, "E": 0.5}

NAMES = {"A": "A spike", "B": "B DP", "C": "C DP 0.7 raw + 0.3 bg", "D": "D DP bg only (post-hoc)",
         "E": "E DP 0.5 raw + 0.5 bg (post-hoc)"}
COLOURS = {"A": (200, 60, 200), "B": (31, 119, 208), "C": (40, 170, 60), "D": (220, 50, 50), "E": (230, 150, 0)}  # RGB


@dataclass(frozen=True)
class Glass:
    name: str
    cx: float
    cy: float
    rx: float
    ry: float


@dataclass
class Context:
    rgb: np.ndarray      # rows x columns x 3, uint8
    times: np.ndarray    # s, per column
    y0: int              # source y of row 0
    build_sec: float


@dataclass
class Point:
    kind: str                         # "gold", "silver" or "silver-none"
    time: float
    y: float | None = None
    y_range: tuple[float, float] | None = None
    note: str = ""


@dataclass
class Draft:
    rows: np.ndarray                  # one row per column
    weak: np.ndarray | None = None    # True where "cannot judge"
    seconds: float = 0.0
    results: list[dict] = field(default_factory=list)


# ---- inputs (v1 files, diagnostic only) ---------------------------------------------------


def read_glass(recipe_path: Path) -> Glass:
    glass = json.loads(recipe_path.read_text(encoding="utf-8"))["glasses"][0]
    e = glass["geometry"]["ellipse"]
    return Glass(glass["name"], float(e["center_x"]), float(e["center_y"]), float(e["radius_x"]), float(e["radius_y"]))


def read_points(folder: Path, name: str) -> list[Point]:
    points = []
    gold = json.loads((folder / f"{name}.oiltruth").read_text(encoding="utf-8"))
    for a in gold["annotations"]:
        y = (a.get("oil_boundary") or {}).get("source_frame_y")
        if y is not None:
            points.append(Point("gold", a["actual_decoded_timestamp_sec"], y=float(y), note=a.get("truth_fill_state", "")))
    silver = json.loads((folder / f"{name}.provisional-truth.json").read_text(encoding="utf-8"))
    for a in silver["annotations"]:
        y, y_range = a.get("oil_level_y_px"), a.get("oil_level_y_range_px")
        note = f'{a.get("boundary_state")}/{a.get("confidence")}'
        if y is not None:
            points.append(Point("silver", a["timestamp_sec"], y=float(y), note=note))
        elif y_range is not None:
            points.append(Point("silver", a["timestamp_sec"], y_range=(float(y_range[0]), float(y_range[1])), note=note))
        else:
            points.append(Point("silver-none", a["timestamp_sec"], note=note))
    return points


# ---- context image (as spike/webui context.py and v1 source_context_renderer.py) ----------


def build_context(video: Path, glass: Glass) -> Context:
    began = time.perf_counter()
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise OSError(f"Cannot open video: {video}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    end = frame_count / fps - 1 / fps
    wanted = sorted({int(round(t * fps)) for t in np.arange(0.0, end + 1e-9, 1 / RATE)})
    wanted_set = set(wanted)
    x0, x1 = max(0, math.floor(glass.cx - BAND * glass.rx)), min(width, math.ceil(glass.cx + BAND * glass.rx))
    y0, y1 = max(0, math.floor(glass.cy - glass.ry)), min(height, math.ceil(glass.cy + glass.ry))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    outside = ((xx - glass.cx) / glass.rx) ** 2 + ((yy - glass.cy) / glass.ry) ** 2 > 1
    columns, times = [], []
    index = 0
    while index <= wanted[-1]:
        if not cap.grab():
            break
        if index in wanted_set:
            ok, frame = cap.retrieve()
            if ok:
                crop = frame[y0:y1, x0:x1, ::-1].astype(np.float32)
                crop[outside] = np.nan
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    columns.append(np.nan_to_num(np.nanmedian(crop, axis=1), nan=0.0))
                times.append(index / fps)
        index += 1
    cap.release()
    rgb = np.clip(np.stack(columns, axis=1), 0, 255).astype(np.uint8)
    return Context(rgb, np.array(times), y0, time.perf_counter() - began)


def luma(rgb: np.ndarray) -> np.ndarray:
    return rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)


def edge_strength(lum: np.ndarray) -> np.ndarray:
    g = np.zeros_like(lum)
    g[1:-1] = np.abs(lum[2:] - lum[:-2])
    return cv2.GaussianBlur(g, (5, 1), 0)  # over 5 columns, as the spike


# ---- methods ------------------------------------------------------------------------------


def draft_spike(g: np.ndarray) -> Draft:
    began = time.perf_counter()
    rows = g.argmax(axis=0)
    rows = np.median(sliding_window_view(np.pad(rows, 2, mode="edge"), 5), axis=1).round().astype(int)
    return Draft(rows, None, time.perf_counter() - began)


def draft_dp(g: np.ndarray) -> Draft:
    began = time.perf_counter()
    height, columns = g.shape
    s = np.minimum(g / EDGE_FULL, 1.0)
    jump = max(1, int(MAX_JUMP * height))
    penalty = JUMP_WEIGHT * np.abs(np.arange(-jump, jump + 1)) / height
    rows = np.arange(height)
    score = s[:, 0].copy()
    back = np.zeros((height, columns), dtype=np.int32)
    for t in range(1, columns):
        total = sliding_window_view(np.pad(score, jump, constant_values=-np.inf), 2 * jump + 1) - penalty
        k = total.argmax(axis=1)
        back[:, t] = rows + k - jump
        score = total[rows, k] + s[:, t]
    path = np.zeros(columns, dtype=int)
    path[-1] = int(score.argmax())
    for t in range(columns - 1, 0, -1):
        path[t - 1] = back[path[t], t]
    strength = s[path, np.arange(columns)]
    return Draft(path, weak_stretches(strength), time.perf_counter() - began)


def weak_stretches(strength: np.ndarray) -> np.ndarray:
    kernel = np.ones(WEAK_WINDOW)
    mean = np.convolve(strength, kernel, mode="same") / np.convolve(np.ones_like(strength), kernel, mode="same")
    weak = mean < WEAK
    start = None
    for t in range(len(weak) + 1):  # drop runs shorter than WEAK_MIN_RUN
        inside = t < len(weak) and weak[t]
        if inside and start is None:
            start = t
        elif not inside and start is not None:
            if t - start < WEAK_MIN_RUN:
                weak[start:t] = False
            start = None
    return weak


def methods(context: Context, keys: str = "ABCDE") -> dict[str, Draft]:
    lum = luma(context.rgb)
    g = edge_strength(lum)
    g_bg = edge_strength(lum - np.median(lum, axis=1, keepdims=True))
    mix = {"B": 0.0, "C": BG_MIX, **POST_HOC_MIX}
    return {key: draft_spike(g) if key == "A" else draft_dp((1 - mix[key]) * g + mix[key] * g_bg) for key in keys}


# ---- scoring ------------------------------------------------------------------------------


def score(context: Context, glass: Glass, points: list[Point], drafts: dict[str, Draft]) -> None:
    height = 2 * glass.ry
    for point in points:
        column = int(np.abs(context.times - point.time).argmin())
        gap = abs(context.times[column] - point.time)
        for draft in drafts.values():
            y = context.y0 + int(draft.rows[column])
            weak = bool(draft.weak[column]) if draft.weak is not None else False
            result = {"kind": point.kind, "time": point.time, "column": column, "gap": round(gap, 3),
                      "draft_y": y, "weak": weak, "note": point.note}
            if point.kind != "silver-none" and gap <= MAX_TIME_GAP:
                if point.y is not None:
                    error = abs(y - point.y)
                else:
                    low, high = point.y_range
                    error = 0.0 if low <= y <= high else min(abs(y - low), abs(y - high))
                percent = 100 * error / height
                result.update(error_px=round(error, 1), error_percent=round(percent, 1),
                              hit=percent <= HIT_PERCENT and not weak, close=percent <= HIT_PERCENT)
            draft.results.append(result)


# ---- picture ------------------------------------------------------------------------------


def picture(context: Context, points: list[Point], drafts: dict[str, Draft], path: Path) -> None:
    """One panel per method: the context image, that method's line and "cannot judge" shading, the truth."""
    rows, columns = context.rgb.shape[:2]
    ky = max(1, round(320 / rows))
    kx = max(1, round(720 / columns))
    base = cv2.cvtColor(cv2.resize(context.rgb, (columns * kx, rows * ky), interpolation=cv2.INTER_NEAREST),
                        cv2.COLOR_RGB2BGR)

    def xy(t, row):
        return int(t * kx + kx / 2), int(row * ky + ky / 2)

    panels = []
    for key, draft in drafts.items():
        image = base.copy()
        if draft.weak is not None and draft.weak.any():
            shade = image.copy()
            for t in np.flatnonzero(draft.weak):
                shade[:, t * kx:(t + 1) * kx] = (140, 140, 140)
            image = cv2.addWeighted(shade, 0.5, image, 0.5, 0)
        line = np.array([xy(t, r) for t, r in enumerate(draft.rows)], np.int32)
        cv2.polylines(image, [line], False, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.polylines(image, [line], False, COLOURS[key][::-1], 2, cv2.LINE_AA)
        for point in points:
            column = int(np.abs(context.times - point.time).argmin())
            if point.kind == "gold":
                cv2.circle(image, xy(column, point.y - context.y0), 7, (0, 0, 0), -1)
                cv2.circle(image, xy(column, point.y - context.y0), 5, (255, 255, 255), -1)
            elif point.kind == "silver" and point.y is not None:
                cv2.circle(image, xy(column, point.y - context.y0), 6, (255, 255, 255), 2)
            elif point.kind == "silver":
                a, b = xy(column, point.y_range[0] - context.y0), xy(column, point.y_range[1] - context.y0)
                cv2.line(image, a, b, (255, 255, 255), 3)
        label = np.full((26, image.shape[1], 3), 255, np.uint8)
        cv2.line(label, (6, 13), (30, 13), COLOURS[key][::-1], 3)
        weak = "" if draft.weak is None else f"   grey = cannot judge ({draft.weak.mean():.0%})"
        cv2.putText(label, NAMES[key] + weak, (36, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (40, 40, 40), 1, cv2.LINE_AA)
        panels.append(np.vstack([label, image]))
    cv2.imwrite(str(path), np.vstack(panels))


# ---- report -------------------------------------------------------------------------------


def report_drafts(context: Context, drafts: dict[str, Draft]) -> None:
    columns = context.rgb.shape[1]
    for key, draft in drafts.items():
        weak = "" if draft.weak is None else f" cannot_judge={draft.weak.mean():.0%}"
        print(f"  method {key} draft={draft.seconds * 1000:.1f}ms per_column={draft.seconds / columns * 1e6:.0f}us{weak}")


def run_recipe(video: Path, recipe_path: Path, out: Path) -> None:
    """A v2 Recipe on any video: no truth, one picture per Glass for the user."""
    from oil_tracker.adapters.storage.recipe_files import recipe_from_json

    recipe = recipe_from_json(recipe_path.read_text(encoding="utf-8"))
    for index, item in enumerate(recipe.glasses, start=1):
        e = item.ellipse
        glass = Glass(item.name, e.center_x, e.center_y, e.radius_x, e.radius_y)
        context = build_context(video, glass)
        drafts = methods(context, "ABDE")
        rows, columns = context.rgb.shape[:2]
        name = f"{video.stem}-{index}-{''.join(c if c.isalnum() else '_' for c in item.name)}.png"
        picture(context, [], drafts, out / name)
        print(f'glass name="{item.name}" picture="{name}" context={columns}x{rows} build={context.build_sec:.1f}s')
        report_drafts(context, drafts)


def run_samples(folder: Path, out: Path) -> None:
    summary = {}
    for name in SAMPLES:
        glass = read_glass(folder / f"{name}.oilrecipe")
        points = read_points(folder, name)
        context = build_context(folder / f"{name}.mp4", glass)
        drafts = methods(context)
        score(context, glass, points, drafts)
        picture(context, points, drafts, out / f"{name}.png")
        rows, columns = context.rgb.shape[:2]
        print(f"video {name} context={columns}x{rows} build={context.build_sec:.2f}s glass_height={2 * glass.ry:g}px")
        report_drafts(context, drafts)
        for index, point in enumerate(points):
            cells = []
            for key, draft in drafts.items():
                r = draft.results[index]
                if "error_percent" in r:
                    mark = "HIT" if r["hit"] else ("weak" if r["weak"] and r["close"] else "miss")
                    cells.append(f"{key}={r['draft_y']}({r['error_percent']}%,{mark}{',cj' if r['weak'] else ''})")
                else:
                    cells.append(f"{key}={r['draft_y']}{'(cj)' if r['weak'] else ''}")
            truth = point.y if point.y is not None else point.y_range
            print(f"  {point.kind:11} t={point.time:6.2f} truth={truth} [{point.note}] " + " ".join(cells))
        summary[name] = {key: draft.results for key, draft in drafts.items()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print("totals (D and E were added after the first run)")
    for kind in ("gold", "silver"):
        for key in "ABCDE":
            results = [r for name in SAMPLES for r in summary[name][key] if r["kind"] == kind and "hit" in r]
            hits = sum(r["hit"] for r in results)
            weak = sum(r["weak"] for r in results)
            weak_close = sum(r["weak"] and r["close"] for r in results)
            print(f"  {kind:6} {key}: hits={hits}/{len(results)} in_cannot_judge={weak} (of which close={weak_close})")
    for key in "BCDE":
        none = [r for name in SAMPLES for r in summary[name][key] if r["kind"] == "silver-none"]
        print(f"  silver-none {key}: in_cannot_judge={sum(r['weak'] for r in none)}/{len(none)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--samples", type=Path, default=Path("sample"))
    parser.add_argument("--video", type=Path)
    parser.add_argument("--recipe", type=Path)
    parser.add_argument("--out", type=Path, default=Path("sample/output/draft-comparison"))
    args = parser.parse_args(argv)
    if (args.video is None) != (args.recipe is None):
        parser.error("--video and --recipe go together")
    args.out.mkdir(parents=True, exist_ok=True)
    if args.video is not None:
        run_recipe(args.video, args.recipe, args.out)
    else:
        run_samples(args.samples, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
