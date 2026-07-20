from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QTimer, Signal

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader


@dataclass
class PreparedReviewVideo:
    reader: object
    frame: object
    frame_index: int
    timestamp_sec: float

    def close(self) -> None:
        reader, self.reader = self.reader, None
        if reader is not None:
            reader.close()


class ResultReviewController(QObject):
    frameReady = Signal(object, int, float)
    metadataChanged = Signal(object)
    playbackStateChanged = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        reader_factory: Callable[[str | Path], object] = OpenCvVideoReader,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.reader_factory = reader_factory
        self.reader = None
        self.current_time = 0.0
        self.current_frame_index = 0
        self.speed = 1.0
        self._generation = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    @property
    def metadata(self):
        return self.reader.metadata if self.reader is not None else None

    @property
    def is_playing(self) -> bool:
        return self.timer.isActive()

    def prepare_video(
        self,
        path: str | Path,
        initial_timestamp: float = 0.0,
        *,
        emit_failure: bool = True,
    ) -> PreparedReviewVideo:
        reader = None
        try:
            reader = self.reader_factory(path)
            frame, frame_index, actual_timestamp = reader.read_at(max(0.0, float(initial_timestamp)))
            return PreparedReviewVideo(reader, frame, int(frame_index), float(actual_timestamp))
        except Exception as exc:
            if reader is not None:
                reader.close()
            if emit_failure:
                self.failed.emit(f"원본 영상을 열 수 없습니다: {exc}")
            raise

    def activate_prepared(self, prepared: PreparedReviewVideo) -> None:
        if prepared.reader is None:
            raise ValueError("준비된 video reader가 없습니다.")
        self.timer.stop()
        self._generation += 1
        previous = self.reader
        self.reader = prepared.reader
        prepared.reader = None
        self.current_time = float(prepared.timestamp_sec)
        self.current_frame_index = int(prepared.frame_index)
        self.metadataChanged.emit(self.reader.metadata)
        self.playbackStateChanged.emit("일시정지")
        self.frameReady.emit(prepared.frame, self.current_frame_index, self.current_time)
        if previous is not None:
            previous.close()

    def open_video(self, path: str | Path, initial_timestamp: float = 0.0) -> None:
        prepared = self.prepare_video(path, initial_timestamp)
        try:
            self.activate_prepared(prepared)
        finally:
            prepared.close()

    def close_video(self) -> None:
        self._generation += 1
        self.timer.stop()
        reader, self.reader = self.reader, None
        if reader is not None:
            reader.close()
        self.current_time = 0.0
        self.current_frame_index = 0
        self.playbackStateChanged.emit("영상 없음")

    def play(self) -> None:
        if self.reader is None:
            return
        fps = max(1.0, float(self.reader.metadata.fps or 0.0))
        self.timer.start(max(10, int(1000.0 / fps)))
        self.playbackStateChanged.emit("재생 중")

    def pause(self) -> None:
        self.timer.stop()
        self.playbackStateChanged.emit("일시정지" if self.reader is not None else "영상 없음")

    def set_speed(self, speed: float) -> None:
        if speed not in {0.5, 1.0, 1.5, 2.0, 4.0}:
            raise ValueError(f"지원하지 않는 재생 속도입니다: {speed}")
        self.speed = float(speed)

    def seek(self, timestamp_sec: float) -> None:
        if self.reader is None:
            return
        self.pause()
        self._decode_at(timestamp_sec)

    def step(self, direction: int) -> None:
        if self.reader is None or direction == 0:
            return
        self.pause()
        fps = max(1.0, float(self.reader.metadata.fps or 0.0))
        duration = max(0.0, float(self.reader.metadata.duration_sec or 0.0))
        target = min(duration, max(0.0, self.current_time + (1 if direction > 0 else -1) / fps))
        self._decode_at(target)

    def _tick(self) -> None:
        if self.reader is None:
            self.pause()
            return
        metadata = self.reader.metadata
        fps = max(1.0, float(metadata.fps or 0.0))
        duration = max(0.0, float(metadata.duration_sec or 0.0))
        target = self.current_time + self.speed / fps
        if duration > 0 and target >= duration:
            self.pause()
            return
        self._decode_at(target, keep_playing=True)

    def _decode_at(self, timestamp_sec: float, *, keep_playing: bool = False) -> None:
        if self.reader is None:
            return
        generation = self._generation
        try:
            frame, frame_index, actual_timestamp = self.reader.read_at(max(0.0, float(timestamp_sec)))
        except EOFError:
            self.pause()
            return
        except Exception as exc:
            self.pause()
            self.failed.emit(f"영상 장면을 읽지 못했습니다: {exc}")
            return
        if generation != self._generation or self.reader is None:
            return
        self.current_time = float(actual_timestamp)
        self.current_frame_index = int(frame_index)
        self.frameReady.emit(frame, self.current_frame_index, self.current_time)
        if not keep_playing:
            self.playbackStateChanged.emit("일시정지")

    def close(self) -> None:
        self.close_video()
