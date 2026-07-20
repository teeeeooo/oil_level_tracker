from __future__ import annotations

from typing import Callable

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.geometry import EllipseGeometry, Rect


class EditableEllipseItem(QGraphicsEllipseItem):
    HANDLE = 10.0

    def __init__(self, glass_id: str, rect: QRectF, frame_rect: QRectF, callback: Callable[[str, QRectF], None]) -> None:
        super().__init__(rect)
        self.glass_id = glass_id
        self.frame_rect = frame_rect
        self.callback = callback
        self._handle: str | None = None
        self._start_rect = QRectF(rect)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.setZValue(30)
        self.setPen(QPen(QColor(0, 220, 255), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

    def _handles(self) -> dict[str, QRectF]:
        r = self.rect()
        h = self.HANDLE
        points = {
            "tl": r.topLeft(), "t": QPointF(r.center().x(), r.top()), "tr": r.topRight(),
            "r": QPointF(r.right(), r.center().y()), "br": r.bottomRight(), "b": QPointF(r.center().x(), r.bottom()),
            "bl": r.bottomLeft(), "l": QPointF(r.left(), r.center().y()),
        }
        return {name: QRectF(point.x() - h / 2, point.y() - h / 2, h, h) for name, point in points.items()}

    def paint(self, painter: QPainter, option, widget=None) -> None:
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setBrush(QBrush(QColor(0, 160, 220)))
            for handle in self._handles().values():
                painter.drawRect(handle)

    def mousePressEvent(self, event) -> None:
        self._handle = None
        for name, rect in self._handles().items():
            if rect.contains(event.pos()):
                self._handle = name
                self._start_rect = QRectF(self.rect())
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._handle is None:
            super().mouseMoveEvent(event)
            return
        r = QRectF(self._start_rect)
        p = event.pos()
        if "l" in self._handle:
            r.setLeft(p.x())
        if "r" in self._handle:
            r.setRight(p.x())
        if "t" in self._handle:
            r.setTop(p.y())
        if "b" in self._handle:
            r.setBottom(p.y())
        r = r.normalized()
        if r.width() < 20:
            r.setWidth(20)
        if r.height() < 20:
            r.setHeight(20)
        r = r.intersected(self.frame_rect)
        self.setRect(r)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if self._handle is None:
            super().mouseReleaseEvent(event)
        else:
            self._handle = None
            event.accept()
        scene_rect = self.mapRectToScene(self.rect()).boundingRect()
        self.setPos(0, 0)
        self.setRect(scene_rect.intersected(self.frame_rect))
        self.callback(self.glass_id, self.rect())

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene() is not None:
            proposed = value
            moved = self.rect().translated(proposed)
            dx = proposed.x()
            dy = proposed.y()
            if moved.left() < self.frame_rect.left(): dx += self.frame_rect.left() - moved.left()
            if moved.right() > self.frame_rect.right(): dx -= moved.right() - self.frame_rect.right()
            if moved.top() < self.frame_rect.top(): dy += self.frame_rect.top() - moved.top()
            if moved.bottom() > self.frame_rect.bottom(): dy -= moved.bottom() - self.frame_rect.bottom()
            return QPointF(dx, dy)
        return super().itemChange(change, value)


class DraggableZeroLine(QGraphicsLineItem):
    def __init__(self, glass_id: str, y: float, x1: float, x2: float, min_y: float, max_y: float, callback) -> None:
        super().__init__(x1, y, x2, y)
        self.glass_id = glass_id
        self.min_y = min_y
        self.max_y = max_y
        self.callback = callback
        self.setPen(QPen(QColor(255, 255, 0), 2, Qt.PenStyle.DashLine))
        self.setZValue(50)
        self.setCursor(Qt.CursorShape.SizeVerCursor)

    def mouseMoveEvent(self, event) -> None:
        y = min(self.max_y, max(self.min_y, event.scenePos().y()))
        line = self.line()
        self.setLine(line.x1(), y, line.x2(), y)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self.callback(self.glass_id, self.line().y1())
        event.accept()


class EditableRectItem(QGraphicsRectItem):
    HANDLE = 9.0

    def __init__(self, glass_id: str, zone_id: str, rect: QRectF, frame_rect: QRectF, callback) -> None:
        super().__init__(rect)
        self.glass_id = glass_id
        self.zone_id = zone_id
        self.frame_rect = frame_rect
        self.callback = callback
        self._resize = False
        self._start = QRectF(rect)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setPen(QPen(QColor(255, 140, 0), 2, Qt.PenStyle.DashLine))
        self.setBrush(QBrush(QColor(255, 100, 0, 40)))
        self.setZValue(40)

    def _handle(self) -> QRectF:
        r = self.rect()
        return QRectF(r.right() - self.HANDLE, r.bottom() - self.HANDLE, self.HANDLE, self.HANDLE)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.fillRect(self._handle(), QColor(255, 255, 255))

    def mousePressEvent(self, event) -> None:
        if self._handle().contains(event.pos()):
            self._resize = True
            self._start = QRectF(self.rect())
            event.accept()
        else:
            self._resize = False
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not self._resize:
            super().mouseMoveEvent(event)
            return
        r = QRectF(self._start)
        r.setBottomRight(event.pos())
        r = r.normalized().intersected(self.frame_rect)
        if r.width() >= 8 and r.height() >= 8:
            self.setRect(r)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if not self._resize:
            super().mouseReleaseEvent(event)
        scene_rect = self.mapRectToScene(self.rect()).boundingRect().intersected(self.frame_rect)
        self.setPos(0, 0)
        self.setRect(scene_rect)
        self.callback(self.glass_id, self.zone_id, self.rect())
        self._resize = False
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene() is not None:
            proposed = value
            moved = self.rect().translated(proposed)
            dx, dy = proposed.x(), proposed.y()
            if moved.left() < 0: dx -= moved.left()
            if moved.top() < 0: dy -= moved.top()
            if moved.right() > self.frame_rect.right(): dx -= moved.right() - self.frame_rect.right()
            if moved.bottom() > self.frame_rect.bottom(): dy -= moved.bottom() - self.frame_rect.bottom()
            return QPointF(dx, dy)
        return super().itemChange(change, value)


class VideoOverlayCanvas(QGraphicsView):
    geometryChanged = Signal(str, object)
    zeroLineChanged = Signal(str, float)
    exclusionChanged = Signal(str, str, object)
    glassSelected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor(20, 22, 25))
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self._pixmap_item = QGraphicsPixmapItem()
        self._pixmap_item.setZValue(0)
        self._scene.addItem(self._pixmap_item)
        self._frame_size = (1280, 720)
        self._glasses = []
        self._selected_id: str | None = None
        self._detection = None
        self.setMinimumSize(640, 420)

    def set_frame(self, frame: np.ndarray) -> None:
        if frame is None:
            return
        if frame.ndim == 2:
            contiguous = np.ascontiguousarray(frame)
            image = QImage(contiguous.data, contiguous.shape[1], contiguous.shape[0], contiguous.strides[0], QImage.Format.Format_Grayscale8).copy()
        else:
            rgb = np.ascontiguousarray(frame[:, :, ::-1])
            image = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format.Format_RGB888).copy()
        self._frame_size = (image.width(), image.height())
        self._pixmap_item.setPixmap(QPixmap.fromImage(image))
        self._scene.setSceneRect(0, 0, image.width(), image.height())
        self.rebuild_overlays()
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_glasses(self, glasses, selected_id: str | None) -> None:
        self._glasses = list(glasses)
        self._selected_id = selected_id
        self.rebuild_overlays()

    def set_detection(self, detection) -> None:
        self._detection = detection
        self.rebuild_overlays()

    def rebuild_overlays(self) -> None:
        for item in list(self._scene.items()):
            if item is not self._pixmap_item:
                self._scene.removeItem(item)
        frame_rect = QRectF(0, 0, self._frame_size[0], self._frame_size[1])
        selected = None
        for glass in self._glasses:
            e = glass.geometry.ellipse
            rect = QRectF(e.center_x - e.radius_x, e.center_y - e.radius_y, e.radius_x * 2, e.radius_y * 2)
            if glass.id == self._selected_id:
                selected = glass
                item = EditableEllipseItem(glass.id, rect, frame_rect, self._ellipse_changed)
                item.setSelected(True)
                item.mousePressEvent
                self._scene.addItem(item)
            else:
                item = QGraphicsEllipseItem(rect)
                item.setPen(QPen(QColor(110, 160, 180), 1))
                item.setZValue(10)
                item.setData(0, glass.id)
                self._scene.addItem(item)
        if selected:
            self._add_selected_overlays(selected, frame_rect)
        if self._detection and self._detection.glass_id == self._selected_id and selected:
            self._add_detection_overlays(selected, self._detection)

    def _add_selected_overlays(self, glass, frame_rect: QRectF) -> None:
        e = glass.geometry.ellipse
        ratio = glass.geometry.margin_ratio
        inner = QRectF(e.center_x - e.radius_x * (1-ratio), e.center_y - e.radius_y * (1-ratio), 2*e.radius_x*(1-ratio), 2*e.radius_y*(1-ratio))
        margin = QGraphicsEllipseItem(inner)
        margin.setPen(QPen(QColor(80, 220, 120), 1, Qt.PenStyle.DotLine))
        margin.setZValue(35)
        self._scene.addItem(margin)
        if glass.geometry.zero_line_y is not None:
            extent = e.horizontal_extent_at(glass.geometry.zero_line_y)
            if extent:
                self._scene.addItem(DraggableZeroLine(glass.id, glass.geometry.zero_line_y, extent[0], extent[1], e.center_y-e.radius_y, e.center_y+e.radius_y, self.zeroLineChanged.emit))
        for zone in glass.geometry.exclusions:
            r = zone.rect
            self._scene.addItem(EditableRectItem(glass.id, zone.id, QRectF(r.x, r.y, r.width, r.height), frame_rect, self._exclusion_changed))
        label = QGraphicsSimpleTextItem(glass.name)
        label.setBrush(QBrush(QColor(255, 255, 255)))
        label.setPos(e.bounds.x, max(0, e.bounds.y - 22))
        label.setZValue(90)
        self._scene.addItem(label)

    def _add_detection_overlays(self, glass, detection) -> None:
        e = glass.geometry.ellipse
        for candidate in detection.candidates:
            if candidate.kind == BoundaryKind.FOAM_FRONT:
                color = QColor(255, 0, 255)
            else:
                color = QColor(0, 255, 80) if candidate.selected else QColor(255, 70, 70, 150)
            item = QGraphicsLineItem(e.bounds.x, candidate.y, e.bounds.right, candidate.y)
            item.setPen(QPen(color, 3 if candidate.selected else 1))
            item.setZValue(70 if candidate.selected else 60)
            self._scene.addItem(item)
        badge = QGraphicsSimpleTextItem(f"{detection.fill_state.value} | conf {detection.overall_confidence:.2f}")
        badge.setBrush(QBrush(QColor(255, 255, 255)))
        badge.setPos(e.bounds.x, e.bounds.bottom + 4)
        badge.setZValue(90)
        self._scene.addItem(badge)

    def _ellipse_changed(self, glass_id: str, rect: QRectF) -> None:
        ellipse = EllipseGeometry(rect.center().x(), rect.center().y(), rect.width()/2, rect.height()/2)
        self.geometryChanged.emit(glass_id, ellipse)

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect: QRectF) -> None:
        self.exclusionChanged.emit(glass_id, zone_id, Rect(rect.x(), rect.y(), rect.width(), rect.height()))

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.position().toPoint())
        glass_id = item.data(0) if item is not None else None
        if glass_id:
            self.glassSelected.emit(str(glass_id))
        super().mousePressEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._pixmap_item.pixmap().isNull():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
