from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPolygonF
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStyle,
    QStyleOptionSlider,
    QWidget,
)


class MarkerSlider(QSlider):
    def __init__(self, parent=None) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._duration = 0.0
        self._markers = []
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
        for timestamp, color in self._markers:
            if timestamp is None:
                continue
            ratio = min(1.0, max(0.0, float(timestamp) / self._duration))
            x = groove.left() + ratio * groove.width()
            painter.setBrush(color)
            painter.setPen(color)
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(x, groove.top() - 1),
                        QPointF(x - 4, groove.top() - 7),
                        QPointF(x + 4, groove.top() - 7),
                    ]
                )
            )


class TransportBar(QWidget):
    """Compact single-row video transport shared by the workbench and wizard."""

    playToggled = Signal(bool)
    stepRequested = Signal(int)
    seekRequested = Signal(float)
    seekReleased = Signal()
    speedChanged = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("transportBar")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.play = QPushButton("재생")
        self.play.setObjectName("transportPrimaryButton")
        self.play.setCheckable(True)
        self.prev = QPushButton("이전")
        self.next = QPushButton("다음")
        self.slider = MarkerSlider()
        self.slider.setRange(0, 10000)
        self.time = QLabel("00:00.000 / 00:00.000 · 장면 0")
        self.time.setObjectName("timecodeLabel")
        self.speed_label = QLabel("배속")
        self.speed = QComboBox()
        self.speed.setMinimumContentsLength(4)
        for value in (0.5, 1.0, 1.5, 2.0, 4.0):
            self.speed.addItem(f"{value:g}×", value)
        self.speed.setCurrentIndex(1)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(5)
        layout.addWidget(self.play)
        layout.addWidget(self.prev)
        layout.addWidget(self.next)
        layout.addWidget(self.time)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.speed_label)
        layout.addWidget(self.speed)

        self.play.toggled.connect(self._play)
        self.prev.clicked.connect(lambda: self.stepRequested.emit(-1))
        self.next.clicked.connect(lambda: self.stepRequested.emit(1))
        self.slider.sliderMoved.connect(lambda value: self.seekRequested.emit(value / 10000.0))
        self.slider.sliderReleased.connect(self.seekReleased)
        self.speed.currentIndexChanged.connect(
            lambda _i: self.speedChanged.emit(float(self.speed.currentData()))
        )

    def _play(self, checked: bool) -> None:
        self.play.setText("정지" if checked else "재생")
        self.playToggled.emit(checked)

    def set_position(self, time_sec: float, duration_sec: float, frame_index: int) -> None:
        ratio = 0.0 if duration_sec <= 0 else min(1.0, max(0.0, time_sec / duration_sec))
        self.slider.blockSignals(True)
        self.slider.setValue(int(ratio * 10000))
        self.slider.blockSignals(False)
        self.time.setText(f"{_format(time_sec)} / {_format(duration_sec)} · 장면 {frame_index}")


def _format(sec: float) -> str:
    minutes = int(sec // 60)
    seconds = sec - minutes * 60
    return f"{minutes:02d}:{seconds:06.3f}"
