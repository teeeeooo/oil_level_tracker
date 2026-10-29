"""Exact source frames as JPEG, for the Recipe screen and the reference frame."""

from __future__ import annotations

import math
import threading
from pathlib import Path

import cv2

from oil_tracker.application.ports import Frame, Region, VideoInfo, VideoUnreadable

JPEG_QUALITY = 90
READ_ON_LIMIT = 15  # frames; a short jump forward reads on instead of seeking


class OpenCvVideo:
    """One opened video. Implements application.ports.OpenVideo; safe across threads."""

    def __init__(self, path: Path) -> None:
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            raise VideoUnreadable(f"영상을 열 수 없습니다: {path.name}")
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not math.isfinite(fps) or fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
            capture.release()
            raise VideoUnreadable(f"영상 정보를 읽을 수 없습니다: {path.name}")
        self.info = VideoInfo(path.name, width, height, fps, frame_count, path.stat().st_size)
        self._capture = capture
        self._lock = threading.Lock()
        self._next_index = 0  # the index the next plain read() returns

    def frame_at(self, time_sec: float, *, max_size: int | None = None, crop: Region | None = None) -> Frame:
        if not math.isfinite(time_sec):
            raise ValueError("time_sec must be finite")
        index = min(self.info.frame_count - 1, max(0, round(time_sec * self.info.fps)))
        with self._lock:
            skip = index - self._next_index
            if 0 < skip <= READ_ON_LIMIT:
                for _ in range(skip):
                    self._capture.grab()
            elif skip != 0:
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, image = self._capture.read()
            self._next_index = index + 1 if ok else -1
        if not ok:
            raise VideoUnreadable(f"{index}번 프레임을 읽을 수 없습니다.")
        region = None
        if crop is not None:
            x0, y0 = max(0, crop.x), max(0, crop.y)
            x1, y1 = min(image.shape[1], crop.x + crop.width), min(image.shape[0], crop.y + crop.height)
            if x1 <= x0 or y1 <= y0:
                raise ValueError("The crop lies outside the frame.")
            image = image[y0:y1, x0:x1]
            region = Region(x0, y0, x1 - x0, y1 - y0)
        if max_size is not None and max(image.shape[:2]) > max_size:
            scale = max_size / max(image.shape[:2])
            size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
            image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        ok, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ok:
            raise VideoUnreadable(f"{index}번 프레임을 JPEG로 만들 수 없습니다.")
        return Frame(index, index / self.info.fps, data.tobytes(), region)

    def close(self) -> None:
        with self._lock:
            self._capture.release()


def open_video(path: Path) -> OpenCvVideo:
    """Implements application.ports.VideoOpener."""
    return OpenCvVideo(path)
