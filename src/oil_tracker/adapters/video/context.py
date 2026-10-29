"""Context images: one pass over the video for every Glass (Product SSOT §3, analysis).

Ported from spike/webui:spikes/webui/context.py (the v1 "ellipse-central-40pct-row-rgb-median"
method). The row median partitions each row once instead of numpy.nanmedian, which was most of
the spike's time on SPL#1 (docs/60-evidence/2026-10-29-v2-2-draft-comparison-windows-result.md).
In uint8 with a partition it took 2.5x less worker time than the int16 sort on the slowest PC, with
identical values (docs/60-evidence/2026-10-30-v2-3-editor-slowest-pc-windows-result.md).
Worker threads compute the medians while the decoder reads on; OpenCV and NumPy's sort release
the GIL, so on a slow PC the pass takes about the longer of the two instead of their sum
(docs/60-evidence/2026-10-29-v2-2-analysis-timing-windows-result.md).
"""

from __future__ import annotations

import math
import os
import time
from collections import deque
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.application.ports import AnalysisCancelled, VideoUnreadable
from oil_tracker.domain.geometry import Ellipse
from oil_tracker.domain.inspection import sample_indices

CENTRAL_BAND = 0.4     # half-width of the sampled band, as a share of radius_x
PROGRESS_EVERY = 240   # decoded frames between progress calls and cancel checks
REDUCE_WORKERS = max(1, min(4, (os.cpu_count() or 2) // 2))
IN_FLIGHT = 2          # frames waiting per worker; bounds the memory


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
    # "grab", "retrieve", "reduce" (summed over the workers) and "wait" (the decoder held back)
    seconds: dict[str, float] = field(default_factory=dict)


class _Band:
    """The central band of one ellipse, prepared once: crop, outside mask and median positions.

    Half of each row's outside pixels are set to 0 and the rest to 255, so they fall below and above
    every inside value (a tie leaves the ranks' values alone). Then the middle ranks of every row sit
    at the same one or two positions, and one partition finds them. median() only reads this, so
    worker threads share it.
    """

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
        below = self.outside.sum(axis=1) // 2
        self.lower = self.outside & (np.cumsum(self.outside, axis=1) <= below[:, None])
        self.upper = self.outside & ~self.lower
        last = self.x1 - self.x0 - 1
        self.low_at = np.minimum(below + self.low, last)
        self.high_at = np.minimum(below + self.high, last)
        self.kth = sorted({int(k) for k in np.concatenate([self.low_at, self.high_at])})

    def median(self, frame: np.ndarray) -> np.ndarray:
        """One context column: the RGB median of each row's band pixels in a BGR frame."""
        data = np.ascontiguousarray(frame[self.y0:self.y1, self.x0:self.x1].transpose(2, 0, 1))  # channel first
        data[:, self.lower] = 0
        data[:, self.upper] = 255
        data.partition(self.kth, axis=2)
        pair = data[:, self.rows, self.low_at].astype(np.int16), data[:, self.rows, self.high_at].astype(np.int16)
        median = ((pair[0] + pair[1]) // 2).T  # rounds down, as the spike
        median[self.empty] = 0
        return median[:, ::-1].astype(np.uint8)  # BGR to RGB


def build_contexts(
    path: Path,
    ellipses: Sequence[Ellipse],
    *,
    start_sec: float,
    end_sec: float,
    rate: float,
    hardware: bool = False,
    workers: int = REDUCE_WORKERS,
    on_progress: Callable[[int, int], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> ContextPass:
    """Decode the range once and sample every Glass from the same frames.

    `workers` threads compute the medians; 0 computes them between decodes. `cancelled` is asked
    every PROGRESS_EVERY frames; when it returns True the pass stops with AnalysisCancelled.
    """
    params = [cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY] if hardware else []
    capture = cv2.VideoCapture(str(path), cv2.CAP_ANY, params)
    pool = ThreadPoolExecutor(workers, thread_name_prefix="context") if workers > 0 else None
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
        columns = [np.zeros((band.y1 - band.y0, len(indices), 3), np.uint8) for band in bands]

        def reduce(column: int, frame: np.ndarray) -> float:
            began = time.perf_counter()
            for band, image in zip(bands, columns):
                image[:, column] = band.median(frame)
            return time.perf_counter() - began

        wanted = set(indices)
        first, last = indices[0], indices[-1]
        if first > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, first)
        seconds = {"grab": 0.0, "retrieve": 0.0, "reduce": 0.0, "wait": 0.0}
        pending: deque[Future[float]] = deque()
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
                    if pool is None:
                        seconds["reduce"] += reduce(len(taken), frame)
                    else:
                        if len(pending) >= workers * IN_FLIGHT:
                            began = time.perf_counter()
                            seconds["reduce"] += pending.popleft().result()
                            seconds["wait"] += time.perf_counter() - began
                        pending.append(pool.submit(reduce, len(taken), frame))
                    taken.append(index)
            index += 1
            if (index - first) % PROGRESS_EVERY == 0:
                if cancelled is not None and cancelled():
                    raise AnalysisCancelled()
                if on_progress is not None:
                    on_progress(index - first, last - first + 1)
        began = time.perf_counter()
        while pending:
            seconds["reduce"] += pending.popleft().result()
        seconds["wait"] += time.perf_counter() - began
        hardware_used = bool(capture.get(cv2.CAP_PROP_HW_ACCELERATION))
    finally:
        if pool is not None:
            pool.shutdown(wait=True, cancel_futures=True)
        capture.release()
    if not taken:
        raise VideoUnreadable(f"분석할 프레임을 읽지 못했습니다: {path.name}")
    if on_progress is not None:
        on_progress(last - first + 1, last - first + 1)
    return ContextPass(
        frame_indices=tuple(taken),
        times=tuple(i / fps for i in taken),
        images=tuple(ContextImage(np.ascontiguousarray(image[:, :len(taken)]), band.y0)
                     for band, image in zip(bands, columns)),
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
