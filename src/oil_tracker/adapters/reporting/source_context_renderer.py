"""Bounded source-pixel context; never a detector or numerical series owner."""
from __future__ import annotations

import json
import math
from pathlib import Path
import warnings

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.visualization.matplotlib_font import (
    apply_font_to_axes, configure_matplotlib_korean_font,
)

MAX_CONTEXT_COLUMNS = 360
MAX_CONTEXT_HEIGHT = 240
CONTEXT_METHOD = "ellipse-central-40pct-row-rgb-median-v1"


def context_times(start: float, end: float, rate: float) -> np.ndarray:
    if not all(math.isfinite(v) for v in (start, end, rate)):
        raise ValueError("Context times must be finite.")
    if start < 0 or end < start or rate <= 0:
        raise ValueError("Invalid source-context interval or sampling rate.")
    count = max(1, int(min((end - start) * rate, MAX_CONTEXT_COLUMNS - 1)) + 1)
    return np.linspace(start, end, count)


def source_column(frame: np.ndarray, geometry) -> tuple[np.ndarray, dict]:
    """Compress only spatial RGB; no threshold, boundary or series is read."""
    e = geometry.ellipse
    cx, cy, rx, ry = e.center_x, e.center_y, e.radius_x, e.radius_y
    if not all(math.isfinite(v) for v in (cx, cy, rx, ry)) or min(rx, ry) <= 0:
        raise ValueError("Invalid source-context ellipse.")
    if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
        raise ValueError("Source context requires an 8-bit BGR frame.")
    h, w = frame.shape[:2]
    x0, x1 = max(0, math.floor(cx - .4 * rx)), min(w, math.ceil(cx + .4 * rx))
    y0, y1 = max(0, math.floor(cy - ry)), min(h, math.ceil(cy + ry))
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Ellipse has no source pixels.")
    yy, xx = np.mgrid[y0:y1, x0:x1]
    valid = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    rgb = frame[y0:y1, x0:x1, ::-1].astype(np.float32) / 255
    rgb[~valid] = np.nan
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        rows = np.nanmedian(rgb, axis=1)
    bounds = np.linspace(0, y1 - y0, min(MAX_CONTEXT_HEIGHT, y1 - y0) + 1, dtype=int)
    rgba = np.zeros((len(bounds) - 1, 4), dtype=np.float32)
    for i, (a, b) in enumerate(zip(bounds, bounds[1:])):
        finite = rows[a:b][np.isfinite(rows[a:b]).all(axis=1)]
        if finite.size:
            rgba[i, :3], rgba[i, 3] = np.median(finite, axis=0), 1
    return rgba, {"x_range": [x0, x1], "y_range": [y0, y1],
                  "height_bin_edges_source_y": (bounds + y0).tolist()}


class SourceContextRenderer:
    def __init__(self, reader_factory=None) -> None:
        self.reader_factory = reader_factory or OpenCvVideoReader

    def render(self, result, recipe, session, directory: Path, *,
               cancellation=None, progress=None) -> dict[str, dict]:
        directory.mkdir(parents=True, exist_ok=True)
        configs = {glass.id: glass for glass in recipe.glasses}
        output: dict[str, dict] = {}
        reader = None
        open_error = None
        _check_cancelled(cancellation)
        try:
            try:
                reader = self.reader_factory(session.input_video_path)
            except (ValueError, OSError, cv2.error) as error:
                open_error = type(error).__name__
            for index, glass in enumerate(result.glass_results, 1):
                _check_cancelled(cancellation)
                config = configs.get(glass.glass_id)
                prefix = f"source_context_{index:02d}"
                payload = {"method": CONTEXT_METHOD, "glass_id": glass.glass_id,
                           "status": "UNAVAILABLE", "columns": [],
                           "numeric_measurement": False, "source_error": open_error}
                if reader is not None and config is not None:
                    payload.update(self._collect(reader, config, session,
                                                 cancellation=cancellation))
                raster = payload.pop("raster", None)
                image_path = ""
                if raster is not None:
                    self._plot(raster, payload, config, directory / f"{prefix}.png")
                    image_path = f"assets/{prefix}.png"
                metadata_path = f"assets/{prefix}.json"
                (directory / f"{prefix}.json").write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8",
                )
                output[glass.glass_id] = {"image_path": image_path,
                    "metadata_path": metadata_path, "status": payload["status"],
                    "column_count": len(payload["columns"]),
                    "spacing_sec": payload.get("requested_spacing_sec"),
                    "available_count": sum(c["status"] == "AVAILABLE" for c in payload["columns"])}
                if progress is not None:
                    progress(index, len(result.glass_results))
        finally:
            if reader is not None:
                reader.close()
        return output

    def _collect(self, reader, config, session, *, cancellation=None) -> dict:
        metadata = reader.metadata
        native_rate = float(metadata.fps)
        if not math.isfinite(native_rate) or native_rate <= 0:
            return {"status": "UNAVAILABLE", "source_error": "unknown_native_cadence"}
        rate = min(float(session.sampling_fps), native_rate)
        end = session.effective_end_sec()
        if end is None:
            end = max(0, metadata.duration_sec - 1 / native_rate)
        try:
            times = context_times(float(session.analysis_start_sec), float(end), rate)
        except ValueError as error:
            return {"source_error": str(error), "status": "UNAVAILABLE"}
        tolerance = max(.05, 1.5 / float(metadata.fps))
        columns, values, geometry = [], [], None
        seen_frames: set[int] = set()
        for requested in times:
            _check_cancelled(cancellation)
            entry = {"requested_time_sec": float(requested), "status": "UNAVAILABLE"}
            value = None
            try:
                frame, frame_id, actual = reader.read_at(float(requested))
                if not math.isfinite(float(actual)) or abs(actual - requested) > tolerance:
                    raise ValueError("decoded_timestamp_outside_tolerance")
                entry.update(frame_index=int(frame_id), actual_time_sec=float(actual))
                if frame_id in seen_frames:
                    raise ValueError("duplicate_decoded_frame")
                value, current_geometry = source_column(frame, config.geometry)
                if not np.any(value[:, 3]):
                    raise ValueError("no_visible_source_rows")
                if geometry is not None and current_geometry != geometry:
                    raise ValueError("source_geometry_changed")
                geometry = current_geometry
                seen_frames.add(frame_id)
                entry["status"] = "AVAILABLE"
            except (EOFError, OSError, ValueError, cv2.error) as error:
                value = None
                entry["reason"] = type(error).__name__ + ": " + str(error)
            columns.append(entry)
            values.append(value)
        valid_count = sum(value is not None for value in values)
        payload = {"columns": columns, "seek_tolerance_sec": tolerance,
                   "nominal_source_fps": native_rate,
                   "timestamp_basis": "OpenCV backend reported; seeking is best effort",
                   "requested_spacing_sec": float(times[1] - times[0]) if len(times) > 1 else None,
                   "requested_range_sec": [float(times[0]), float(times[-1])],
                   "status": "UNAVAILABLE" if not valid_count else
                   "AVAILABLE" if valid_count == len(values) else "PARTIAL"}
        if valid_count:
            height = next(value.shape[0] for value in values if value is not None)
            blank = np.zeros((height, 4), dtype=np.float32)
            payload.update(geometry=geometry,
                           raster=np.stack([blank if v is None else v for v in values], axis=1))
        return payload

    @staticmethod
    def _plot(raster, payload, config, path):
        start, end = payload["requested_range_sec"]
        step = (end - start) / max(1, raster.shape[1] - 1)
        half = max(step / 2, .001)
        y0, y1 = payload["geometry"]["y_range"]
        zero = config.geometry.zero_line_y
        top, bottom = (zero - y0, zero - y1) if zero is not None else (y0, y1)
        font = configure_matplotlib_korean_font()
        fig, ax = plt.subplots(figsize=(12, 3.2))
        try:
            ax.imshow(raster, extent=(start - half, end + half, bottom, top),
                      aspect="auto", interpolation="nearest", origin="upper")
            if zero is not None:
                ax.axhline(0, linestyle=":", linewidth=1)
            ax.set_xlabel("시간 (초) · 열마다 해당 시점의 원본 영상 색상")
            ax.set_ylabel("기준선 대비 높이 (px)" if zero is not None else "원본 Y (px)")
            ax.set_title("원본 영상 맥락 · 위치 측정이나 Oil/Foam 분류 결과가 아님")
            apply_font_to_axes(ax, font)
            fig.tight_layout()
            fig.savefig(path, dpi=140)
        finally:
            plt.close(fig)


def _check_cancelled(cancellation) -> None:
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis cancelled during source-context rendering.")
