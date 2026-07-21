from __future__ import annotations

import math

import numpy as np
from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QImage, QKeyEvent, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget


class TruthAnnotationCanvas(QWidget):
    """Single-frame editor that stores and emits only source-frame canonical Y."""

    oilLineChanged = Signal(float)
    foamLineChanged = Signal(float)
    validationError = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self._frame: np.ndarray | None = None
        self._pixmap = QPixmap()
        self._glass = None
        self._official = None
        self._oil_y: float | None = None
        self._foam_y: float | None = None
        self._edit_target = "oil"
        self._dragging = False
        self._scale = 1.0
        self._show_official = True
        self._status_text = ""
        self.setMinimumSize(320, 240)

    @property
    def scale_factor(self) -> float:
        return self._scale

    @property
    def oil_y(self) -> float | None:
        return self._oil_y

    @property
    def foam_y(self) -> float | None:
        return self._foam_y

    @property
    def edit_target(self) -> str:
        return self._edit_target

    def set_frame(self, frame: np.ndarray | None) -> None:
        self._frame = None if frame is None else np.ascontiguousarray(frame.copy())
        self._pixmap = QPixmap() if frame is None else _pixmap(self._frame)
        self._resize_for_scale()
        self.update()

    def set_context(
        self,
        glass,
        *,
        official_reference=None,
        truth_oil_y: float | None = None,
        truth_foam_y: float | None = None,
        status_text: str = "",
    ) -> None:
        self._glass = glass
        self._official = official_reference
        self._oil_y = None if truth_oil_y is None else float(truth_oil_y)
        self._foam_y = None if truth_foam_y is None else float(truth_foam_y)
        self._status_text = str(status_text)
        self.update()

    def clear(self, message: str = "현재 Viewer 장면을 불러와 주세요.") -> None:
        self._frame = None
        self._pixmap = QPixmap()
        self._glass = None
        self._official = None
        self._oil_y = None
        self._foam_y = None
        self._status_text = message
        self._resize_for_scale()
        self.update()

    def set_edit_target(self, target: str) -> None:
        if target not in {"oil", "foam"}:
            raise ValueError(f"지원하지 않는 편집 대상입니다: {target}")
        self._edit_target = target
        self.update()

    def set_official_visible(self, visible: bool) -> None:
        self._show_official = bool(visible)
        self.update()

    def set_truth_y(self, target: str, value: float | None, *, emit: bool = False) -> bool:
        if target not in {"oil", "foam"}:
            raise ValueError(target)
        if value is None:
            if target == "oil":
                self._oil_y = None
            else:
                self._foam_y = None
            self.update()
            return True
        try:
            source_y = float(value)
        except (TypeError, ValueError):
            self.validationError.emit("Y 값은 숫자여야 합니다.")
            return False
        if not math.isfinite(source_y):
            self.validationError.emit("Y 값은 유한한 숫자여야 합니다.")
            return False
        if not self._inside_vertical_roi(source_y):
            self.validationError.emit("입력한 Y가 선택 관찰창 ROI 타원 밖에 있습니다.")
            return False
        if target == "oil":
            self._oil_y = source_y
            if emit:
                self.oilLineChanged.emit(source_y)
        else:
            self._foam_y = source_y
            if emit:
                self.foamLineChanged.emit(source_y)
        self.update()
        return True

    def remove_line(self, target: str) -> None:
        self.set_truth_y(target, None)

    def zoom_in(self) -> None:
        self.set_scale(self._scale * 1.25)

    def zoom_out(self) -> None:
        self.set_scale(self._scale / 1.25)

    def actual_size(self) -> None:
        self.set_scale(1.0)

    def fit_to(self, width: int, height: int) -> None:
        if self._pixmap.isNull():
            return
        ratio = min(max(1, width - 12) / self._pixmap.width(), max(1, height - 12) / self._pixmap.height())
        self.set_scale(max(0.05, ratio))

    def set_scale(self, value: float) -> None:
        self._scale = min(8.0, max(0.05, float(value)))
        self._resize_for_scale()
        self.update()

    def sizeHint(self) -> QSize:
        if self._pixmap.isNull():
            return QSize(640, 420)
        return QSize(
            max(1, int(round(self._pixmap.width() * self._scale))),
            max(1, int(round(self._pixmap.height() * self._scale))),
        )

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(20, 22, 25))
        if self._pixmap.isNull():
            painter.setPen(QColor(220, 224, 230))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self._status_text or "장면 없음")
            return
        target = QRectF(0.0, 0.0, self._pixmap.width() * self._scale, self._pixmap.height() * self._scale)
        painter.drawPixmap(target, self._pixmap, QRectF(self._pixmap.rect()))
        if self._glass is None:
            return
        self._draw_geometry(painter)
        if self._show_official and self._official is not None:
            if self._official.oil_boundary is not None:
                self._draw_boundary(painter, self._official.oil_boundary.source_frame_y, "공식 oil", QColor(255, 190, 30), dashed=True)
            if self._official.foam_front is not None:
                self._draw_boundary(painter, self._official.foam_front.source_frame_y, "공식 foam", QColor(200, 80, 255), dashed=True)
        if self._oil_y is not None:
            self._draw_boundary(painter, self._oil_y, "정답 oil", QColor(40, 230, 90), dashed=False, active=self._edit_target == "oil")
        if self._foam_y is not None:
            self._draw_boundary(painter, self._foam_y, "정답 foam", QColor(40, 190, 255), dashed=False, active=self._edit_target == "foam")
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QPointF(12, 22), f"편집 대상: {'유면' if self._edit_target == 'oil' else '거품'} · {self._status_text}")

    def _draw_geometry(self, painter: QPainter) -> None:
        geometry = self._glass.geometry
        ellipse = geometry.ellipse
        painter.setPen(QPen(QColor(70, 220, 230), max(1.0, 1.5 * self._scale)))
        bounds = ellipse.bounds
        painter.drawEllipse(QRectF(bounds.x * self._scale, bounds.y * self._scale, bounds.width * self._scale, bounds.height * self._scale))
        if geometry.zero_line_y is not None:
            self._draw_geometry_line(painter, geometry.zero_line_y, "기준선", QColor(255, 230, 30), Qt.PenStyle.DotLine)
        painter.setPen(QPen(QColor(255, 80, 80), max(1.0, self._scale)))
        painter.setBrush(QColor(255, 80, 80, 40))
        for zone in geometry.exclusions:
            rect = zone.rect
            painter.drawRect(QRectF(rect.x * self._scale, rect.y * self._scale, rect.width * self._scale, rect.height * self._scale))

    def _draw_geometry_line(self, painter, source_y, label, color, style) -> None:
        extent = self._glass.geometry.ellipse.horizontal_extent_at(float(source_y))
        if extent is None:
            return
        pen = QPen(color, max(1.0, 1.2 * self._scale), style)
        painter.setPen(pen)
        y = float(source_y) * self._scale
        painter.drawLine(QPointF(extent[0] * self._scale, y), QPointF(extent[1] * self._scale, y))
        painter.drawText(QPointF(extent[0] * self._scale + 4, max(14.0, y - 4)), label)

    def _draw_boundary(self, painter, source_y, label, color, *, dashed, active=False) -> None:
        extent = self._glass.geometry.ellipse.horizontal_extent_at(float(source_y))
        if extent is None:
            return
        width = 3.0 if active else 2.0
        style = Qt.PenStyle.DashLine if dashed else Qt.PenStyle.SolidLine
        painter.setPen(QPen(color, width, style))
        y = float(source_y) * self._scale
        painter.drawLine(QPointF(extent[0] * self._scale, y), QPointF(extent[1] * self._scale, y))
        painter.drawText(QPointF(extent[0] * self._scale + 4, max(14.0, y - 5)), label)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._frame is None or self._glass is None:
            super().mousePressEvent(event)
            return
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self._dragging = self._apply_pointer(event.position())
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_pointer(event.position())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() not in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            super().keyPressEvent(event)
            return
        current = self._oil_y if self._edit_target == "oil" else self._foam_y
        if current is None:
            self.validationError.emit("먼저 편집할 경계선을 지정해 주세요.")
            return
        step = 5.0 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 1.0
        delta = -step if event.key() == Qt.Key.Key_Up else step
        self.set_truth_y(self._edit_target, current + delta, emit=True)
        event.accept()

    def _apply_pointer(self, point) -> bool:
        source_y = float(point.y()) / self._scale
        if not self._inside_vertical_roi(source_y):
            self.validationError.emit("선택 위치가 ROI 타원 밖입니다. 경계선을 변경하지 않았습니다.")
            return False
        return self.set_truth_y(self._edit_target, source_y, emit=True)

    def _inside_vertical_roi(self, source_y: float) -> bool:
        return self._glass is not None and self._glass.geometry.ellipse.horizontal_extent_at(float(source_y)) is not None

    def _resize_for_scale(self) -> None:
        self.resize(self.sizeHint())
        self.updateGeometry()


def _pixmap(frame: np.ndarray) -> QPixmap:
    if frame.ndim == 2:
        array = np.ascontiguousarray(frame)
        image = QImage(array.data, array.shape[1], array.shape[0], array.strides[0], QImage.Format.Format_Grayscale8).copy()
    elif frame.shape[2] == 4:
        array = np.ascontiguousarray(frame[:, :, [2, 1, 0, 3]])
        image = QImage(array.data, array.shape[1], array.shape[0], array.strides[0], QImage.Format.Format_RGBA8888).copy()
    else:
        array = np.ascontiguousarray(frame[:, :, ::-1])
        image = QImage(array.data, array.shape[1], array.shape[0], array.strides[0], QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(image)
