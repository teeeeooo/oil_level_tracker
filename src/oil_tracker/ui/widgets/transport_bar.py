from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPolygonF
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QVBoxLayout,
    QWidget,
)


class MarkerSlider(QSlider):
    fractionActivated = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._duration = 0.0
        self._markers = []
        self._review_points: list[tuple[float, QColor]] = []
        self._review_intervals: list[tuple[float, float, QColor]] = []
        self._debug_points: list[tuple[float, bool]] = []
        self._truth_points: list[tuple[float, str, bool]] = []
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setToolTip("파랑: 분석 시작·종료 / 주황: 압축기 기동")

    def set_markers(
        self,
        duration: float,
        analysis_start: float | None,
        analysis_end: float | None,
        compressor_start: float | None,
    ) -> None:
        self._duration = max(0.0, duration)
        self._markers = [
            (analysis_start, QColor(40, 170, 255)),
            (analysis_end, QColor(40, 170, 255)),
            (compressor_start, QColor(255, 120, 30)),
        ]
        self.update()

    def set_review_markers(
        self,
        duration: float,
        event_timestamps=(),
        review_intervals=(),
    ) -> None:
        self._duration = max(0.0, duration)
        self._review_points = [
            (float(timestamp), QColor(180, 100, 255))
            for timestamp in event_timestamps
            if timestamp is not None
        ]
        self._review_intervals = [
            (float(start), float(end), QColor(255, 80, 80, 90))
            for start, end in review_intervals
            if start is not None and end is not None
        ]
        self._update_tooltip()
        self.update()

    def set_debug_markers(self, duration: float, timestamps=(), selected_timestamp: float | None = None) -> None:
        self._duration = max(0.0, duration)
        self._debug_points = [
            (float(timestamp), selected_timestamp is not None and abs(float(timestamp) - float(selected_timestamp)) <= 1e-9)
            for timestamp in timestamps
            if timestamp is not None
        ]
        self._update_tooltip()
        self.update()

    def set_truth_markers(self, duration: float, markers=()) -> None:
        self._duration = max(0.0, duration)
        self._truth_points = [
            (
                float(marker.timestamp_sec),
                str(marker.disposition),
                bool(marker.selected),
            )
            for marker in markers
            if marker.timestamp_sec is not None
        ]
        self._update_tooltip()
        self.update()

    def clear_review_markers(self) -> None:
        self._review_points.clear()
        self._review_intervals.clear()
        self._debug_points.clear()
        self._truth_points.clear()
        self.setToolTip("파랑: 분석 시작·종료 / 주황: 압축기 기동")
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._duration <= 0:
            return
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider,
            option,
            QStyle.SubControl.SC_SliderGroove,
            self,
        )
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for start, end, color in self._review_intervals:
            left = groove.left() + self._ratio(start) * groove.width()
            right = groove.left() + self._ratio(end) * groove.width()
            painter.fillRect(
                QRectF(min(left, right), groove.top() - 4, max(2.0, abs(right - left)), groove.height() + 8),
                color,
            )
        for timestamp, color in self._markers:
            self._draw_triangle(painter, groove, timestamp, color, upward=True)
        for timestamp, color in self._review_points:
            self._draw_triangle(painter, groove, timestamp, color, upward=False)
        for timestamp, selected in self._debug_points:
            self._draw_debug_square(painter, groove, timestamp, selected)
        for timestamp, disposition, selected in self._truth_points:
            self._draw_truth_diamond(painter, groove, timestamp, disposition, selected)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            option = QStyleOptionSlider()
            self.initStyleOption(option)
            handle = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                option,
                QStyle.SubControl.SC_SliderHandle,
                self,
            )
            groove = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider,
                option,
                QStyle.SubControl.SC_SliderGroove,
                self,
            )
            if not handle.contains(event.position().toPoint()) and groove.width() > 0:
                fraction = min(
                    1.0,
                    max(0.0, (event.position().x() - groove.left()) / groove.width()),
                )
                self.setValue(round(self.minimum() + fraction * (self.maximum() - self.minimum())))
                self.fractionActivated.emit(fraction)
                event.accept()
                return
        super().mousePressEvent(event)

    def _draw_triangle(self, painter, groove, timestamp, color, *, upward: bool) -> None:
        if timestamp is None:
            return
        x = groove.left() + self._ratio(float(timestamp)) * groove.width()
        painter.setBrush(color)
        painter.setPen(color)
        if upward:
            points = [
                QPointF(x, groove.top() - 1),
                QPointF(x - 4, groove.top() - 7),
                QPointF(x + 4, groove.top() - 7),
            ]
        else:
            points = [
                QPointF(x, groove.bottom() + 1),
                QPointF(x - 4, groove.bottom() + 7),
                QPointF(x + 4, groove.bottom() + 7),
            ]
        painter.drawPolygon(QPolygonF(points))

    def _draw_debug_square(self, painter, groove, timestamp: float, selected: bool) -> None:
        x = groove.left() + self._ratio(timestamp) * groove.width()
        size = 8 if selected else 5
        color = QColor(20, 210, 210)
        painter.setPen(color)
        painter.setBrush(color if selected else Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(x - size / 2, groove.center().y() - size / 2, size, size))

    def _draw_truth_diamond(self, painter, groove, timestamp: float, disposition: str, selected: bool) -> None:
        x = groove.left() + self._ratio(timestamp) * groove.width()
        y = groove.center().y()
        size = 9 if selected else 6
        color = {
            "confirmed_correct": QColor(80, 210, 120),
            "corrected": QColor(255, 210, 50),
            "unusable": QColor(230, 100, 100),
        }.get(disposition, QColor(230, 230, 230))
        painter.setPen(color)
        painter.setBrush(color if selected else Qt.BrushStyle.NoBrush)
        painter.drawPolygon(
            QPolygonF(
                [
                    QPointF(x, y - size / 2),
                    QPointF(x + size / 2, y),
                    QPointF(x, y + size / 2),
                    QPointF(x - size / 2, y),
                ]
            )
        )

    def _update_tooltip(self) -> None:
        parts = ["파랑: 분석 범위", "주황: 압축기 기동", "보라 삼각형: 이벤트", "빨강 영역: 검토 필요"]
        if self._debug_points:
            parts.append("청록 사각형: 디버그 기록(채움: 선택 기록)")
        if self._truth_points:
            parts.append("마름모: 사용자 정답(채움: 선택 정답)")
        self.setToolTip(" / ".join(parts))

    def _ratio(self, timestamp: float) -> float:
        return min(1.0, max(0.0, timestamp / self._duration))


class TransportBar(QWidget):
    """Two-row precision video transport shared by the workbench and viewer."""

    playToggled = Signal(bool)
    stepRequested = Signal(int)
    skipRequested = Signal(float)
    seekRequested = Signal(float)
    seekReleased = Signal()
    timeRequested = Signal(float)
    speedChanged = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("transportBar")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.play = QPushButton("재생")
        self.play.setObjectName("transportPrimaryButton")
        self.play.setCheckable(True)
        self.prev = QPushButton("이전 프레임")
        self.next = QPushButton("다음 프레임")
        self.skip_back_10 = QPushButton("−10초")
        self.skip_back_5 = QPushButton("−5초")
        self.skip_forward_5 = QPushButton("+5초")
        self.skip_forward_10 = QPushButton("+10초")
        self.slider = MarkerSlider()
        self.slider.setRange(0, 10000)
        self.time_input = QLineEdit("00:00.000")
        self.time_input.setObjectName("timecodeInput")
        self.time_input.setMaximumWidth(96)
        self.time_input.setToolTip("이동할 시각을 초 또는 분:초 형식으로 입력하세요.")
        self.time = QLabel("/ 00:00.000 · 프레임 0")
        self.time.setObjectName("timecodeLabel")
        self.speed_label = QLabel("배속")
        self.speed = QComboBox()
        self.speed.setMinimumContentsLength(4)
        for value in (0.5, 1.0, 1.5, 2.0, 4.0):
            self.speed.addItem(f"{value:g}×", value)
        self.speed.setCurrentIndex(1)
        self._duration = 0.0
        self._current_time = 0.0
        self._pending_seek: float | None = None
        self._seek_timer = QTimer(self)
        self._seek_timer.setSingleShot(True)
        self._seek_timer.setInterval(50)

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(5)
        for widget in (
            self.play,
            self.prev,
            self.next,
            self.skip_back_10,
            self.skip_back_5,
            self.skip_forward_5,
            self.skip_forward_10,
        ):
            controls.addWidget(widget)
        controls.addStretch(1)
        controls.addWidget(self.time_input)
        controls.addWidget(self.time)
        controls.addWidget(self.speed_label)
        controls.addWidget(self.speed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)
        layout.addLayout(controls)
        layout.addWidget(self.slider)
        self.play.toggled.connect(self._play)
        self.prev.clicked.connect(lambda: self.stepRequested.emit(-1))
        self.next.clicked.connect(lambda: self.stepRequested.emit(1))
        self.skip_back_10.clicked.connect(lambda: self.skipRequested.emit(-10.0))
        self.skip_back_5.clicked.connect(lambda: self.skipRequested.emit(-5.0))
        self.skip_forward_5.clicked.connect(lambda: self.skipRequested.emit(5.0))
        self.skip_forward_10.clicked.connect(lambda: self.skipRequested.emit(10.0))
        self.slider.sliderMoved.connect(lambda value: self._queue_seek(value / 10000.0))
        self.slider.sliderReleased.connect(self._slider_released)
        self.slider.fractionActivated.connect(self._activate_seek)
        self.time_input.editingFinished.connect(self._time_edited)
        self.speed.currentIndexChanged.connect(lambda _i: self.speedChanged.emit(float(self.speed.currentData())))
        self._seek_timer.timeout.connect(self._emit_pending_seek)

    def _play(self, checked: bool) -> None:
        self.play.setText("정지" if checked else "재생")
        self.playToggled.emit(checked)

    def set_position(self, time_sec: float, duration_sec: float, frame_index: int) -> None:
        self._current_time = max(0.0, float(time_sec))
        self._duration = max(0.0, float(duration_sec))
        ratio = 0.0 if duration_sec <= 0 else min(1.0, max(0.0, time_sec / duration_sec))
        self.slider.blockSignals(True)
        self.slider.setValue(int(ratio * 10000))
        self.slider.blockSignals(False)
        if not self.time_input.hasFocus():
            self.time_input.setText(_format(time_sec))
        self.time.setText(f"/ {_format(duration_sec)} · 프레임 {frame_index}")

    def _queue_seek(self, fraction: float) -> None:
        self._pending_seek = min(1.0, max(0.0, float(fraction)))
        if not self._seek_timer.isActive():
            self._seek_timer.start()

    def _emit_pending_seek(self) -> None:
        if self._pending_seek is None:
            return
        fraction, self._pending_seek = self._pending_seek, None
        self.seekRequested.emit(fraction)

    def _slider_released(self) -> None:
        self._seek_timer.stop()
        self._pending_seek = self.slider.value() / 10000.0
        self._emit_pending_seek()
        self.seekReleased.emit()

    def _activate_seek(self, fraction: float) -> None:
        self._seek_timer.stop()
        self._pending_seek = None
        self.seekRequested.emit(min(1.0, max(0.0, float(fraction))))
        self.seekReleased.emit()

    def _time_edited(self) -> None:
        try:
            timestamp = _parse_timecode(self.time_input.text())
        except ValueError:
            self.time_input.setText(_format(self._current_time))
            self.time_input.selectAll()
            return
        if self._duration > 0:
            timestamp = min(self._duration, timestamp)
        self.timeRequested.emit(timestamp)


def _format(sec: float) -> str:
    minutes = int(sec // 60)
    seconds = sec - minutes * 60
    return f"{minutes:02d}:{seconds:06.3f}"


def _parse_timecode(value: str) -> float:
    text = str(value).strip()
    if not text:
        raise ValueError("empty timecode")
    parts = text.split(":")
    try:
        if len(parts) == 1:
            seconds = float(parts[0])
        elif len(parts) == 2:
            seconds = float(parts[0]) * 60.0 + float(parts[1])
        elif len(parts) == 3:
            seconds = float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
        else:
            raise ValueError("invalid timecode")
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid timecode") from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("invalid timecode")
    return seconds
