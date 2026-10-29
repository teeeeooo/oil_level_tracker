"""The analysis: one pass for every Glass, then each Glass's draft and pictures (Product SSOT §3, §4).

Implements application.ports.VideoAnalyser. The pictures leave as PNG pieces for the inspection
cache (docs/20-architecture/inspection-folder.md).
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.application.ports import AnalysisCancelled, GlassImages, VideoAnalysis
from oil_tracker.domain.inspection import ANALYSIS_RATE, AnalysisSettings, GlassDraft
from oil_tracker.domain.recipe import Glass

from .context import REDUCE_WORKERS, background_view, build_contexts
from .draft import draft_line, oil_draft

PIECE_COLUMNS = 4096  # the cache's PNG pieces
FINISH_SHARE = 0.1    # of the progress, for the drafts and pictures after the pass


@dataclass(frozen=True)
class AnalysisTimings:
    """Where the time went, for the timing script."""

    frames_decoded: int
    hardware_used: bool
    pass_seconds: dict[str, float]               # grab, retrieve, reduce, wait, total
    glass_seconds: tuple[dict[str, float], ...]  # draft, background, png


def png_pieces(image: np.ndarray, columns: int = PIECE_COLUMNS) -> tuple[bytes, ...]:
    """An RGB or grey image as PNG pieces of at most `columns` columns, in time order."""
    pieces = []
    for start in range(0, image.shape[1], columns):
        piece = image[:, start:start + columns]
        ok, data = cv2.imencode(".png", piece[:, :, ::-1] if piece.ndim == 3 else piece)
        if not ok:
            raise RuntimeError("PNG encoding failed")
        pieces.append(data.tobytes())
    return tuple(pieces)


def run_analysis(
    path: Path,
    glasses: Sequence[Glass],
    settings: AnalysisSettings,
    progress: Callable[[int, int], None],
    cancelled: Callable[[], bool],
    *,
    hardware: bool = False,
    workers: int = REDUCE_WORKERS,
) -> tuple[VideoAnalysis, AnalysisTimings]:
    """Progress counts the decoded frames, then a FINISH_SHARE more for the Glasses by height."""
    units = {"frames": 0, "finish": 0}

    def on_frames(done: int, total: int) -> None:
        units["frames"], units["finish"] = total, max(1, math.ceil(total * FINISH_SHARE))
        progress(done, total + units["finish"])

    began = time.perf_counter()
    passed = build_contexts(
        path,
        [glass.ellipse for glass in glasses],
        start_sec=settings.start_sec,
        end_sec=settings.end_sec,
        rate=ANALYSIS_RATE,
        hardware=hardware,
        workers=workers,
        on_progress=on_frames,
        cancelled=cancelled,
    )
    pass_seconds = dict(passed.seconds, total=time.perf_counter() - began)

    total = units["frames"] + units["finish"]
    heights = [image.rgb.shape[0] for image in passed.images]
    finished = 0
    drafts, images, glass_seconds = [], [], []
    for glass, image in zip(glasses, passed.images):
        if cancelled():
            raise AnalysisCancelled()
        step = time.perf_counter()
        draft = oil_draft(image.rgb)
        draft_sec = time.perf_counter() - step
        step = time.perf_counter()
        background = background_view(image.rgb)
        background_sec = time.perf_counter() - step
        step = time.perf_counter()
        context_png, background_png = png_pieces(image.rgb), png_pieces(background)
        png_sec = time.perf_counter() - step
        drafts.append(GlassDraft(glass.id, draft_line(draft, image.y0)))
        images.append(GlassImages(glass.id, image.y0, image.rgb.shape[0], context_png, background_png))
        glass_seconds.append({"draft": draft_sec, "background": background_sec, "png": png_sec})
        finished += image.rgb.shape[0]
        progress(units["frames"] + round(units["finish"] * finished / sum(heights)), total)

    analysis = VideoAnalysis(passed.times, tuple(drafts), tuple(images))
    return analysis, AnalysisTimings(passed.frames_decoded, passed.hardware, pass_seconds, tuple(glass_seconds))


class OpenCvAnalyser:
    """Implements application.ports.VideoAnalyser with software decoding (the A4 result)."""

    def analyse(
        self,
        path: Path,
        glasses: Sequence[Glass],
        settings: AnalysisSettings,
        progress: Callable[[int, int], None],
        cancelled: Callable[[], bool],
    ) -> VideoAnalysis:
        return run_analysis(path, glasses, settings, progress, cancelled)[0]
