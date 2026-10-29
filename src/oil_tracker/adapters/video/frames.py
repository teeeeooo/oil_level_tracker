"""Exact source frames as JPEG, for the Recipe screen and the reference frame."""

from __future__ import annotations

import math
import threading
from pathlib import Path

import cv2

from oil_tracker.application.ports import Frame, VideoInfo, VideoUnreadable

JPEG_QUALITY = 90


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
        self.info = VideoInfo(path.name, width, height, fps, frame_count)
        self._capture = capture
        self._lock = threading.Lock()
        self._next_index = 0  # the index the next plain read() returns

    def frame_at(self, time_sec: float, *, max_size: int | None = None) -> Frame:
        if not math.isfinite(time_sec):
            raise ValueError("time_sec must be finite")
        index = min(self.info.frame_count - 1, max(0, round(time_sec * self.info.fps)))
        with self._lock:
            if index != self._next_index:
                self._capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            ok, image = self._capture.read()
            self._next_index = index + 1 if ok else -1
        if not ok:
            raise VideoUnreadable(f"{index}번 프레임을 읽을 수 없습니다.")
        if max_size is not None and max(image.shape[:2]) > max_size:
            scale = max_size / max(image.shape[:2])
            size = (round(image.shape[1] * scale), round(image.shape[0] * scale))
            image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
        ok, data = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ok:
            raise VideoUnreadable(f"{index}번 프레임을 JPEG로 만들 수 없습니다.")
        return Frame(index, index / self.info.fps, data.tobytes())

    def close(self) -> None:
        with self._lock:
            self._capture.release()


def open_video(path: Path) -> OpenCvVideo:
    """Implements application.ports.VideoOpener."""
    return OpenCvVideo(path)
