"""Context images: one pass over the video for every Glass (Product SSOT §3, analysis).

Ported from spike/webui:spikes/webui/context.py (the v1 "ellipse-central-40pct-row-rgb-median"
method). The row median sorts each row once instead of numpy.nanmedian, which was most of the
spike's time on SPL#1 (docs/60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md).
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.application.ports import VideoUnreadable
from oil_tracker.domain.geometry import Ellipse

CENTRAL_BAND = 0.4     # half-width of the sampled band, as a share of radius_x
PROGRESS_EVERY = 240   # decoded frames between progress calls
_OUTSIDE = 1000        # sorts after every 8-bit value


@dataclass(frozen=True)
class ContextImage:
    """One Glass. Column t is the frame at the pass's times[t]; row r is source row y0 + r."""

    rgb: np.ndarray  # rows x columns x 3, uint8: the RGB median of each row's band pixels
    y0: int


@dataclass(frozen=True)
class ContextPass:
    frame_indices: tuple[int, ...]
    times: tuple[float, ...]
    images: tuple[ContextImage, ...]  # in the order of the ellipses given
    frames_decoded: int
    hardware: bool                    # whether OpenCV reports hardware decoding
    seconds: dict[str, float] = field(default_factory=dict)  # "grab", "retrieve", "reduce"


class _Band:
    """The central band of one ellipse, prepared once: crop, outside mask and median ranks."""

    def __init__(self, ellipse: Ellipse, width: int, height: int) -> None:
        e = ellipse
        self.x0 = max(0, math.floor(e.center_x - CENTRAL_BAND * e.radius_x))
        self.x1 = min(width, math.ceil(e.center_x + CENTRAL_BAND * e.radius_x))
        self.y0 = max(0, math.floor(e.top))
        self.y1 = min(height, math.ceil(e.bottom))
        if self.x1 <= self.x0 or self.y1 <= self.y0:
            raise ValueError("The ellipse has no pixels inside the frame.")
        yy, xx = np.mgrid[self.y0:self.y1, self.x0:self.x1]
        self.outside = ((xx - e.center_x) / e.radius_x) ** 2 + ((yy - e.center_y) / e.radius_y) ** 2 > 1
        valid = (~self.outside).sum(axis=1)
        self.empty = valid == 0
        self.low = np.maximum(valid - 1, 0) // 2   # the two middle ranks; equal for an odd count
        self.high = valid // 2
        self.rows = np.arange(self.y1 - self.y0)
        self.columns: list[np.ndarray] = []

    def add(self, frame: np.ndarray) -> None:
        crop = frame[self.y0:self.y1, self.x0:self.x1].astype(np.int16)
        crop[self.outside] = _OUTSIDE
        crop.sort(axis=1)
        median = (crop[self.rows, self.low] + crop[self.rows, self.high]) // 2  # rounds down, as the spike
        median[self.empty] = 0
        self.columns.append(median[:, ::-1].astype(np.uint8))  # BGR to RGB

    def image(self) -> ContextImage:
        return ContextImage(np.stack(self.columns, axis=1), self.y0)


def sample_indices(fps: float, frame_count: int, start_sec: float, end_sec: float, rate: float) -> list[int]:
    """Frame indices at `rate` per second from start to end, clamped to the video."""
    last = frame_count - 1
    start = max(0.0, start_sec)
    end = min(end_sec, last / fps)
    if not end >= start:
        raise ValueError("The analysis range is empty.")
    count = math.floor((end - start) * rate + 1e-9) + 1
    return sorted({min(last, round((start + k / rate) * fps)) for k in range(count)})


def build_contexts(
    path: Path,
    ellipses: Sequence[Ellipse],
    *,
    start_sec: float,
    end_sec: float,
    rate: float,
    hardware: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> ContextPass:
    """Decode the range once and sample every Glass from the same frames."""
    params = [cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY] if hardware else []
    capture = cv2.VideoCapture(str(path), cv2.CAP_ANY, params)
    try:
        if not capture.isOpened():
            raise VideoUnreadable(f"영상을 열 수 없습니다: {path.name}")
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not math.isfinite(fps) or fps <= 0 or frame_count <= 0:
            raise VideoUnreadable(f"영상 정보를 읽을 수 없습니다: {path.name}")
        indices = sample_indices(fps, frame_count, start_sec, end_sec, rate)
        bands = [_Band(ellipse, width, height) for ellipse in ellipses]
        wanted = set(indices)
        first, last = indices[0], indices[-1]
        if first > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, first)
        seconds = {"grab": 0.0, "retrieve": 0.0, "reduce": 0.0}
        taken: list[int] = []
        index = first
        while index <= last:
            began = time.perf_counter()
            grabbed = capture.grab()
            seconds["grab"] += time.perf_counter() - began
            if not grabbed:
                break
            if index in wanted:
                began = time.perf_counter()
                ok, frame = capture.retrieve()
                seconds["retrieve"] += time.perf_counter() - began
                if ok:
                    began = time.perf_counter()
                    for band in bands:
                        band.add(frame)
                    seconds["reduce"] += time.perf_counter() - began
                    taken.append(index)
            index += 1
            if on_progress is not None and (index - first) % PROGRESS_EVERY == 0:
                on_progress(index - first, last - first + 1)
        hardware_used = bool(capture.get(cv2.CAP_PROP_HW_ACCELERATION))
    finally:
        capture.release()
    if not taken:
        raise VideoUnreadable(f"분석할 프레임을 읽지 못했습니다: {path.name}")
    if on_progress is not None:
        on_progress(last - first + 1, last - first + 1)
    return ContextPass(
        frame_indices=tuple(taken),
        times=tuple(i / fps for i in taken),
        images=tuple(band.image() for band in bands),
        frames_decoded=index - first,
        hardware=hardware_used,
        seconds=seconds,
    )


def background_view(rgb: np.ndarray) -> np.ndarray:
    """Distance of each pixel from its row's median over time, as an 8-bit grey image."""
    data = rgb.astype(np.float32)
    distance = np.abs(data - np.median(data, axis=1, keepdims=True)).sum(axis=2)
    scale = 255.0 / max(1.0, float(np.percentile(distance, 99.5)))
    return np.clip(distance * scale, 0, 255).astype(np.uint8)
