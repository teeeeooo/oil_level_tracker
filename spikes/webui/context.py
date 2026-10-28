"""Context image, background view and a naive draft for one Glass (spike only)."""
from __future__ import annotations

import json
import math
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

CENTRAL_BAND = 0.4  # half-width of the sampled band, as a fraction of radius_x
DRAFT_POINT_SPACING_SEC = 2.0


@dataclass
class Glass:
    name: str
    cx: float
    cy: float
    rx: float
    ry: float
    zero_y: float


@dataclass
class Context:
    rgb: np.ndarray  # rows x columns x 3, uint8, RGB
    times: list[float]  # actual decoded time per column
    y0: int  # source y of row 0
    fps: float
    frame_count: int
    width: int
    height: int
    build_sec: float
    draft_points: list[dict] = field(default_factory=list)


def read_v1_glass(recipe_path: Path, index: int, name: str | None = None) -> Glass:
    """Read only the ellipse and zero line from a v1 .oilrecipe (spike convenience)."""
    recipe = json.loads(Path(recipe_path).read_text(encoding="utf-8"))
    if name is not None:
        matches = [i for i, g in enumerate(recipe["glasses"]) if g.get("name", "").strip().lower() == name.strip().lower()]
        if len(matches) != 1:
            names = [g.get("name", "") for g in recipe["glasses"]]
            raise ValueError(f"Glass name {name!r} matched {len(matches)} of {names}")
        index = matches[0]
    glass = recipe["glasses"][index]
    ellipse = glass["geometry"]["ellipse"]
    zero = glass["geometry"].get("zero_line_y")
    return Glass(
        name=glass.get("name", f"Glass {index + 1}"),
        cx=float(ellipse["center_x"]), cy=float(ellipse["center_y"]),
        rx=float(ellipse["radius_x"]), ry=float(ellipse["radius_y"]),
        zero_y=float(ellipse["center_y"] if zero is None else zero),
    )


def build_context(video: Path, glass: Glass, start: float, end: float | None,
                  rate: float, progress=None, draft_spacing: float = DRAFT_POINT_SPACING_SEC) -> Context:
    began = time.perf_counter()
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise OSError(f"Cannot open video: {video}")
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("Unknown video frame rate.")
    duration = frame_count / fps
    end = duration - 1 / fps if end is None else min(end, duration - 1 / fps)
    rate = min(rate, fps)
    wanted = sorted({int(round(t * fps)) for t in np.arange(start, end + 1e-9, 1 / rate)})
    wanted_set = set(wanted)

    x0 = max(0, math.floor(glass.cx - CENTRAL_BAND * glass.rx))
    x1 = min(width, math.ceil(glass.cx + CENTRAL_BAND * glass.rx))
    y0 = max(0, math.floor(glass.cy - glass.ry))
    y1 = min(height, math.ceil(glass.cy + glass.ry))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    outside = ((xx - glass.cx) / glass.rx) ** 2 + ((yy - glass.cy) / glass.ry) ** 2 > 1

    columns: list[np.ndarray] = []
    times: list[float] = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, wanted[0])
    index = wanted[0]
    last = wanted[-1]
    while index <= last:
        if not cap.grab():
            break
        if index in wanted_set:
            ok, frame = cap.retrieve()
            if ok:
                crop = frame[y0:y1, x0:x1, ::-1].astype(np.float32)
                crop[outside] = np.nan
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    rows = np.nanmedian(crop, axis=1)
                columns.append(np.nan_to_num(rows, nan=0.0))
                times.append(index / fps)
                if progress is not None and len(columns) % 50 == 0:
                    progress(len(columns), len(wanted))
        index += 1
    cap.release()
    if not columns:
        raise ValueError("No context columns decoded.")
    rgb = np.clip(np.stack(columns, axis=1), 0, 255).astype(np.uint8)
    context = Context(rgb=rgb, times=times, y0=y0, fps=fps, frame_count=frame_count,
                      width=width, height=height, build_sec=0.0)
    context.draft_points = naive_draft(context, glass, draft_spacing)
    context.build_sec = time.perf_counter() - began
    return context


def background_view(rgb: np.ndarray) -> np.ndarray:
    """Distance of each pixel from its row's temporal median, as a gray image."""
    data = rgb.astype(np.float32)
    median = np.median(data, axis=1, keepdims=True)
    diff = np.abs(data - median).sum(axis=2)
    scale = 255.0 / max(1.0, float(np.percentile(diff, 99.5)))
    gray = np.clip(diff * scale, 0, 255).astype(np.uint8)
    return np.repeat(gray[:, :, None], 3, axis=2)


def naive_draft(context: Context, glass: Glass, spacing: float = DRAFT_POINT_SPACING_SEC) -> list[dict]:
    """Strongest vertical edge per column, thinned; a placeholder, not extraction."""
    luma = context.rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    if luma.shape[0] < 5:
        return []
    grad = np.abs(luma[2:] - luma[:-2])
    grad = cv2.GaussianBlur(grad, (5, 1), 0)
    rows = grad.argmax(axis=0) + 1
    window = np.lib.stride_tricks.sliding_window_view(np.pad(rows, 2, mode="edge"), 5)
    rows = np.median(window, axis=1).astype(int)
    step = max(1, round(spacing / max(1e-6, _spacing(context.times))))
    points = []
    for c in range(0, len(context.times), step):
        h = glass.zero_y - (context.y0 + int(rows[c]))
        points.append({"t": round(context.times[c], 3), "h": float(h), "corner": False, "src": "draft"})
    return points


def _spacing(times: list[float]) -> float:
    return (times[-1] - times[0]) / (len(times) - 1) if len(times) > 1 else 1.0


def encode_png(rgb: np.ndarray) -> bytes:
    ok, data = cv2.imencode(".png", rgb[:, :, ::-1])
    if not ok:
        raise ValueError("PNG encoding failed.")
    return data.tobytes()
