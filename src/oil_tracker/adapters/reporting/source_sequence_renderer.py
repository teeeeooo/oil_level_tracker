"""Bounded offline source-frame review, independent of Oil/Foam measurements."""
from __future__ import annotations

from dataclasses import asdict
import json
import math
from pathlib import Path

import cv2
import numpy as np

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.application.ports.progress import AnalysisCancelled
from oil_tracker.application.services.report_review_windows import plan_source_review_windows

MAX_SEQUENCE_FRAMES = 240
TILE_SIZE = 192
PAGE_COLUMNS = 8
PAGE_ROWS = 5
PAGE_CAPACITY = PAGE_COLUMNS * PAGE_ROWS
SOURCE_SEQUENCE_METHOD = "source-crop-manual-sequence-v1"


def sequence_times(start: float, end: float, fps: float) -> np.ndarray:
    if not all(math.isfinite(x) for x in (start, end, fps)) or start < 0 or end < start or fps <= 0:
        raise ValueError("Invalid source sequence time range or native cadence.")
    count = max(1, int(min((end - start) * fps + 1e-9, MAX_SEQUENCE_FRAMES - 1)) + 1)
    return np.linspace(start, end, count)


def source_tile(frame: np.ndarray, geometry) -> tuple[np.ndarray, dict]:
    if frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
        raise ValueError("Source review requires an 8-bit BGR frame.")
    e = geometry.ellipse
    cx, cy, rx, ry = e.center_x, e.center_y, e.radius_x, e.radius_y
    if not all(math.isfinite(x) for x in (cx, cy, rx, ry)) or min(rx, ry) <= 0:
        raise ValueError("Invalid source review ellipse.")
    h, w = frame.shape[:2]
    x0, x1 = max(0, math.floor(cx-rx)), min(w, math.ceil(cx+rx))
    y0, y1 = max(0, math.floor(cy-ry)), min(h, math.ceil(cy+ry))
    if x0 >= x1 or y0 >= y1:
        raise ValueError("No source pixels inside the review crop.")
    crop = frame[y0:y1, x0:x1]
    scale = min(1.0, TILE_SIZE / max(crop.shape[:2]))
    th, tw = max(1, round(crop.shape[0]*scale)), max(1, round(crop.shape[1]*scale))
    reduced = crop if scale == 1 else cv2.resize(crop, (tw, th), interpolation=cv2.INTER_AREA)
    tile = np.zeros((TILE_SIZE, TILE_SIZE, 3), np.uint8)
    left, top = (TILE_SIZE-tw)//2, (TILE_SIZE-th)//2
    tile[top:top+th, left:left+tw] = reduced
    return tile, {"crop_source_xyxy": [x0, y0, x1, y1], "source_frame_size": [w, h],
                  "tile_content_xywh": [left, top, tw, th], "resize_scale": scale,
                  "resize_method": "none" if scale == 1 else "INTER_AREA"}


def _check_cancelled(cancellation):
    if cancellation is not None and cancellation.cancelled:
        raise AnalysisCancelled("Analysis cancelled during source-frame review.")


def _write_png(path: Path, image: np.ndarray):
    # imencode + Path handles non-ASCII Windows output paths consistently.
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise OSError("Unable to encode source review PNG.")
    path.write_bytes(encoded.tobytes())


MAX_SEQUENTIAL_ADVANCE = 32


class _SequenceSampler:
    """Seek once per bounded review, then decode nearby frames in source order.

    This adapter is report-only. Every returned frame still undergoes the normal
    identity/timestamp checks. Missing or non-monotonic decoder output is never
    replaced by the last valid source frame.
    """
    def __init__(self, reader, fps, cancellation=None):
        self.reader, self.fps, self.cancellation = reader, fps, cancellation
        self.last = None
        self.seek_count = self.sequential_read_count = 0

    def read_at(self, requested):
        previous = self.last
        try:
            if (previous is None or requested <= previous[2]
                    or (requested-previous[2])*self.fps > MAX_SEQUENTIAL_ADVANCE
                    or not callable(getattr(self.reader, "read_next", None))):
                self.seek_count += 1
                self.last = self.reader.read_at(requested)
            else:
                steps = 0
                while self.last[2] < requested - .5/self.fps:
                    _check_cancelled(self.cancellation)
                    if steps >= MAX_SEQUENTIAL_ADVANCE:
                        raise ValueError("sequential_decode_budget_exceeded")
                    before = self.last
                    self.sequential_read_count += 1
                    current = self.reader.read_next()
                    steps += 1
                    if (not math.isfinite(float(current[2])) or current[2] <= before[2]
                            or current[1] <= before[1]):
                        raise ValueError("nonmonotonic_sequential_frame")
                    self.last = current
            return self.last
        except (EOFError, OSError, ValueError, cv2.error):
            self.last = None
            raise


class SourceSequenceRenderer:
    def __init__(self, reader_factory=None):
        self.reader_factory = reader_factory or OpenCvVideoReader

    def render(self, result, recipe, session, directory: Path, *, presentation,
               cancellation=None, progress=None) -> dict[str, list[dict]]:
        directory.mkdir(parents=True, exist_ok=True)
        configs = {glass.id: glass for glass in recipe.glasses}
        output = {}
        reader, open_error = None, None
        _check_cancelled(cancellation)
        try:
            try:
                reader = self.reader_factory(session.input_video_path)
            except (ValueError, OSError, cv2.error) as error:
                open_error = type(error).__name__
            for gi, glass in enumerate(result.glass_results, 1):
                _check_cancelled(cancellation)
                view, config = presentation.for_glass(glass.glass_id), configs.get(glass.glass_id)
                sequences = []
                end = session.effective_end_sec()
                if view is not None and config is not None and end is not None:
                    for wi, window in enumerate(plan_source_review_windows(view, session.analysis_start_sec, end), 1):
                        prefix = f"source_sequence_{gi:02d}_{wi:02d}"
                        payload = {"method": SOURCE_SEQUENCE_METHOD, "numeric_measurement": False,
                                   "glass_id": glass.glass_id, **asdict(window),
                                   "status": "UNAVAILABLE", "source_error": open_error,
                                   "frames": [], "preview_path": "", "tile_size": TILE_SIZE,
                                   "metadata_path": f"assets/{prefix}.json"}
                        if reader is not None:
                            payload.update(self._collect(reader, config, window, directory, prefix,
                                                         cancellation=cancellation))
                        payload["available_count"] = sum(f["status"] == "AVAILABLE" for f in payload["frames"])
                        payload["frame_count"] = len(payload["frames"])
                        (directory / f"{prefix}.json").write_text(
                            json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
                        sequences.append(payload)
                output[glass.glass_id] = sequences
                if progress is not None:
                    progress(gi, len(result.glass_results))
        finally:
            if reader is not None:
                reader.close()
        return output

    def _collect(self, reader, config, window, directory, prefix, *, cancellation=None):
        try:
            fps = float(reader.metadata.fps)
            times = sequence_times(window.start_sec, window.end_sec, fps)
        except (ValueError, TypeError):
            return {"status": "UNAVAILABLE", "source_error": "unknown_native_cadence"}
        tolerance = max(.05, 1.5/fps)
        sampler = _SequenceSampler(reader, fps, cancellation)
        frames, seen = [], set()
        geometry, preview_path, last_actual = None, "", None
        page = None
        for i, requested in enumerate(times):
            _check_cancelled(cancellation)
            slot = i % PAGE_CAPACITY
            if slot == 0:
                page = np.zeros((PAGE_ROWS*TILE_SIZE, PAGE_COLUMNS*TILE_SIZE, 3), np.uint8)
            page_name = f"{prefix}_page_{i//PAGE_CAPACITY:02d}.png"
            tile_x, tile_y = (slot % PAGE_COLUMNS)*TILE_SIZE, (slot // PAGE_COLUMNS)*TILE_SIZE
            entry = {"requested_time_sec": float(requested), "status": "UNAVAILABLE"}
            try:
                frame, frame_id, actual = sampler.read_at(float(requested))
                if not math.isfinite(float(actual)) or abs(actual-requested) > tolerance:
                    raise ValueError("decoded_timestamp_outside_tolerance")
                if not isinstance(frame_id, (int, np.integer)) or frame_id < 0:
                    raise ValueError("invalid_source_frame_index")
                entry.update(frame_index=int(frame_id), actual_time_sec=float(actual))
                if last_actual is not None and actual <= last_actual:
                    raise ValueError("nonmonotonic_decoded_time")
                if frame_id in seen:
                    raise ValueError("duplicate_decoded_frame")
                tile, current_geometry = source_tile(frame, config.geometry)
                if geometry is not None and geometry != current_geometry:
                    raise ValueError("source_geometry_changed")
                geometry = current_geometry
                seen.add(frame_id)
                last_actual = float(actual)
                page[tile_y:tile_y+TILE_SIZE, tile_x:tile_x+TILE_SIZE] = tile
                entry.update(status="AVAILABLE", page_path=f"assets/{page_name}", tile_xy=[tile_x, tile_y])
            except (EOFError, OSError, ValueError, cv2.error) as error:
                sampler.last = None
                entry["reason"] = type(error).__name__+": "+str(error)
            _check_cancelled(cancellation)
            if entry["status"] == "AVAILABLE" and not preview_path:
                preview_path = f"assets/{prefix}_preview.png"
                _write_png(directory / f"{prefix}_preview.png", tile)
            frames.append(entry)
            if slot == PAGE_CAPACITY-1 or i == len(times)-1:
                _write_png(directory / page_name, page)
        available = sum(f["status"] == "AVAILABLE" for f in frames)
        spacing = float(times[1]-times[0]) if len(times) > 1 else None
        return {"status": "UNAVAILABLE" if not available else "AVAILABLE" if available == len(frames) else "PARTIAL",
                "source_error": None, "frames": frames, "geometry": geometry,
                "preview_path": preview_path, "nominal_source_fps": fps,
                "requested_spacing_sec": spacing, "subsampled": spacing is not None and spacing > 1/fps + 1e-6,
                "seek_tolerance_sec": tolerance, "timestamp_basis": "OpenCV actual decoded frame/time; bounded sequential reads or best-effort seek",
                "decode_strategy": {"maximum_sequential_advance": MAX_SEQUENTIAL_ADVANCE,
                                    "seek_count": sampler.seek_count,
                                    "sequential_read_count": sampler.sequential_read_count}}
