from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from oil_tracker.ui.widgets.transport_bar import TransportBar
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas


class VideoPreviewWidget(QWidget):
    timestampChanged = Signal(float)
    videoError = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.reader: OpenCvVideoReader | None = None
        self.current_time = 0.0
        self.current_frame_index = 0
        self.playback_speed = 1.0
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.canvas = VideoOverlayCanvas()
        self.canvas.setMinimumSize(520, 280)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.set_glasses([], None)
        self.transport = TransportBar()
        self.placeholder = QLabel("영상을 선택하면 이 영역에서 미리 볼 수 있습니다.")
        self.placeholder.setObjectName("previewHint")
        self.placeholder.setFixedHeight(22)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.placeholder)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.transport)

        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._play_tick)
        self.transport.playToggled.connect(self.toggle_play)
        self.transport.stepRequested.connect(self.step_frame)
        self.transport.seekRequested.connect(self.seek_fraction)
        self.transport.speedChanged.connect(self._set_speed)
        self.transport.setEnabled(False)

    @property
    def metadata(self):
        return self.reader.metadata if self.reader is not None else None

    @property
    def current_timestamp(self) -> float:
        return self.current_time

    def open_video(self, path: str) -> None:
        self.close_video()
        self.reader = OpenCvVideoReader(path)
        self.placeholder.setText(Path(path).name)
        self.placeholder.setToolTip(path)
        self.transport.setEnabled(True)
        self.load_frame(0.0, reset_view=True)

    def close_video(self) -> None:
        self.play_timer.stop()
        self.transport.play.blockSignals(True)
        self.transport.play.setChecked(False)
        self.transport.play.blockSignals(False)
        self.transport.play.setText("재생")
        if self.reader is not None:
            self.reader.close()
            self.reader = None
        self.transport.setEnabled(False)

    def set_markers(
        self,
        analysis_start: float | None,
        analysis_end: float | None,
        compressor_start: float | None,
    ) -> None:
        duration = self.reader.metadata.duration_sec if self.reader is not None else 0.0
        self.transport.slider.set_markers(duration, analysis_start, analysis_end, compressor_start)

    def load_frame(self, timestamp: float, *, reset_view: bool = False) -> None:
        if self.reader is None:
            return
        try:
            duration = self.reader.metadata.duration_sec
            target = max(0.0, min(duration, timestamp))
            frame, frame_index, actual = self.reader.read_at(target)
            self.current_time = actual
            self.current_frame_index = frame_index
            self.canvas.set_frame(frame, reset_view=reset_view)
            self.transport.set_position(actual, duration, frame_index)
            self.timestampChanged.emit(actual)
        except Exception as exc:
            self.videoError.emit(str(exc))

    def toggle_play(self, playing: bool) -> None:
        if playing and self.reader is not None:
            fps = max(1.0, self.reader.metadata.fps)
            self.play_timer.start(max(15, int(1000 / fps)))
        else:
            self.play_timer.stop()

    def _play_tick(self) -> None:
        if self.reader is None:
            self.transport.play.setChecked(False)
            return
        fps = max(1.0, self.reader.metadata.fps)
        target = self.current_time + self.playback_speed / fps
        if target >= self.reader.metadata.duration_sec:
            self.transport.play.setChecked(False)
            self.load_frame(self.reader.metadata.duration_sec)
            return
        self.load_frame(target)

    def step_frame(self, direction: int) -> None:
        if self.reader is None:
            return
        fps = max(1.0, self.reader.metadata.fps)
        self.load_frame(self.current_time + direction / fps)

    def seek_fraction(self, fraction: float) -> None:
        if self.reader is not None:
            self.load_frame(self.reader.metadata.duration_sec * fraction)

    def _set_speed(self, value: float) -> None:
        self.playback_speed = value

    def closeEvent(self, event) -> None:
        self.close_video()
        super().closeEvent(event)
