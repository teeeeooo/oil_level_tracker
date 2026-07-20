from __future__ import annotations

from pathlib import Path

import cv2

from oil_tracker.domain.session import VideoMetadata


class OpenCvVideoReader:
    """Timestamp-oriented OpenCV reader.

    CAP_PROP_POS_MSEC is used as a best-effort seek target. The actual timestamp
    reported by the backend is returned with every decoded frame because codecs
    and variable-frame-rate containers may land on a nearby keyframe/frame.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._capture = cv2.VideoCapture(self.path)
        if not self._capture.isOpened():
            raise ValueError(f"Unable to open video: {self.path}")
        width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(self._capture.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration = frame_count / fps if fps > 0 and frame_count > 0 else 0.0
        fourcc_value = int(self._capture.get(cv2.CAP_PROP_FOURCC) or 0)
        codec = "".join(chr((fourcc_value >> 8 * i) & 0xFF) for i in range(4)).strip("\x00")
        warning = "OpenCV timestamp seeking is backend/keyframe dependent; actual decoded timestamps are recorded."
        self._metadata = VideoMetadata(self.path, width, height, fps, duration, frame_count, codec, warning)

    @property
    def metadata(self) -> VideoMetadata:
        return self._metadata

    def read_at(self, timestamp_sec: float):
        if timestamp_sec < 0:
            raise ValueError("Timestamp must be non-negative.")
        target = float(timestamp_sec)
        if self._metadata.duration_sec > 0 and target >= self._metadata.duration_sec:
            frame_period = 1.0 / self._metadata.fps if self._metadata.fps > 0 else 0.001
            target = max(0.0, self._metadata.duration_sec - frame_period)
        self._capture.set(cv2.CAP_PROP_POS_MSEC, target * 1000.0)
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise EOFError(f"Unable to decode frame near {timestamp_sec:.3f}s")
        actual_msec = float(self._capture.get(cv2.CAP_PROP_POS_MSEC) or timestamp_sec * 1000.0)
        frame_index = max(0, int(round(self._capture.get(cv2.CAP_PROP_POS_FRAMES))) - 1)
        return frame, frame_index, actual_msec / 1000.0

    def read_next(self):
        ok, frame = self._capture.read()
        if not ok or frame is None:
            raise EOFError("End of video")
        actual_msec = float(self._capture.get(cv2.CAP_PROP_POS_MSEC) or 0.0)
        frame_index = max(0, int(round(self._capture.get(cv2.CAP_PROP_POS_FRAMES))) - 1)
        return frame, frame_index, actual_msec / 1000.0

    def close(self) -> None:
        self._capture.release()

    def __enter__(self) -> "OpenCvVideoReader":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()
