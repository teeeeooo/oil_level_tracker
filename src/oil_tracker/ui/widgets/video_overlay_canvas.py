from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from oil_tracker.adapters.presentation.qt_frame_image_converter import QtFrameImageConverter
from oil_tracker.domain.geometry import EllipseGeometry, Rect
from oil_tracker.ui.presentation_labels import fill_state_label


MIN_ELLIPSE_SIZE = 20.0
ZOOM_STEP = 1.25
MIN_VIEW_SCALE = 0.05
MAX_VIEW_SCALE = 16.0
_FRAME_IMAGE_CONVERTER = QtFrameImageConverter()


def scene_rect_in_frame(item: QGraphicsItem, rect: QRectF, frame_rect: QRectF) -> QRectF:
    """Return one item's rectangle in canonical scene coordinates, clipped to the frame."""
    return item.mapRectToScene(rect).normalized().intersected(frame_rect)


def resized_rect(
    start_rect: QRectF,
    handle: str,
    point: QPointF,
    frame_rect: QRectF,
    minimum_size: float = MIN_ELLIPSE_SIZE,
) -> QRectF:
    left, top, right, bottom = (
        start_rect.left(),
        start_rect.top(),
        start_rect.right(),
        start_rect.bottom(),
    )
    if "l" in handle:
        left = min(point.x(), right - minimum_size)
    if "r" in handle:
        right = max(point.x(), left + minimum_size)
    if "t" in handle:
        top = min(point.y(), bottom - minimum_size)
    if "b" in handle:
        bottom = max(point.y(), top + minimum_size)
    left = max(frame_rect.left(), left)
    right = min(frame_rect.right(), right)
    top = max(frame_rect.top(), top)
    bottom = min(frame_rect.bottom(), bottom)
    if right - left < minimum_size:
        if "l" in handle:
            left = max(frame_rect.left(), right - minimum_size)
        else:
            right = min(frame_rect.right(), left + minimum_size)
    if bottom - top < minimum_size:
        if "t" in handle:
            top = max(frame_rect.top(), bottom - minimum_size)
        else:
            bottom = min(frame_rect.bottom(), top + minimum_size)
    return QRectF(QPointF(left, top), QPointF(right, bottom)).normalized()


class ResizeHandleItem(QGraphicsRectItem):
    SIZE = 10.0
    HIT_SIZE = 18.0

    def __init__(self, role: str, owner: "EditableEllipseItem") -> None:
        super().__init__(owner)
        self.role = role
        self.owner = owner
        self.setRect(-self.SIZE / 2, -self.SIZE / 2, self.SIZE, self.SIZE)
        self.setBrush(QBrush(QColor(22, 105, 170)))
        self.setPen(QPen(QColor(255, 255, 255), 1))
        self.setZValue(4)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setAcceptHoverEvents(True)
        self.setCursor(_handle_cursor(role))

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(-self.HIT_SIZE / 2, -self.HIT_SIZE / 2, self.HIT_SIZE, self.HIT_SIZE)
        return path

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.owner.begin_resize(self.role, event.scenePos())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        self.owner.continue_resize(event.scenePos())
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self.owner.end_resize(event.scenePos())
        event.accept()


class EditableEllipseItem(QGraphicsEllipseItem):
    HANDLE_ROLES = ("tl", "t", "tr", "r", "br", "b", "bl", "l")

    def __init__(self, glass_id: str, rect: QRectF, frame_rect: QRectF, callback: Callable[[str, QRectF], None]) -> None:
        super().__init__(rect)
        self.glass_id = glass_id
        self.frame_rect = frame_rect
        self.callback = callback
        self._resizing = False
        self._active_handle: str | None = None
        self._start_scene_rect = QRectF(rect)
        self._handles = {role: ResizeHandleItem(role, self) for role in self.HANDLE_ROLES}
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setZValue(30)
        self.setPen(QPen(QColor(0, 220, 255), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self._sync_handles()

    def begin_resize(self, role: str, _scene_pos: QPointF) -> None:
        self._resizing = True
        self._active_handle = role
        self._start_scene_rect = scene_rect_in_frame(self, self.rect(), self.frame_rect)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def continue_resize(self, scene_pos: QPointF) -> None:
        if not self._resizing or self._active_handle is None:
            return
        new_scene_rect = resized_rect(
            self._start_scene_rect,
            self._active_handle,
            scene_pos,
            self.frame_rect,
        )
        self.setPos(0, 0)
        self.setRect(new_scene_rect)
        self._sync_handles()

    def end_resize(self, scene_pos: QPointF) -> None:
        if not self._resizing:
            return
        self.continue_resize(scene_pos)
        self._resizing = False
        self._active_handle = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.callback(self.glass_id, QRectF(self.rect()))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene() is not None:
            proposed = value
            moved = self.rect().translated(proposed)
            dx, dy = proposed.x(), proposed.y()
            if moved.left() < self.frame_rect.left():
                dx += self.frame_rect.left() - moved.left()
            if moved.right() > self.frame_rect.right():
                dx -= moved.right() - self.frame_rect.right()
            if moved.top() < self.frame_rect.top():
                dy += self.frame_rect.top() - moved.top()
            if moved.bottom() > self.frame_rect.bottom():
                dy -= moved.bottom() - self.frame_rect.bottom()
            return QPointF(dx, dy)
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._sync_handles()
        return super().itemChange(change, value)

    def mouseReleaseEvent(self, event) -> None:
        if self._resizing:
            event.accept()
            return
        super().mouseReleaseEvent(event)
        final_rect = scene_rect_in_frame(self, self.rect(), self.frame_rect)
        self.setPos(0, 0)
        self.setRect(final_rect)
        self._sync_handles()
        self.callback(self.glass_id, QRectF(self.rect()))

    def _sync_handles(self) -> None:
        r = self.rect()
        positions = {
            "tl": r.topLeft(),
            "t": QPointF(r.center().x(), r.top()),
            "tr": r.topRight(),
            "r": QPointF(r.right(), r.center().y()),
            "br": r.bottomRight(),
            "b": QPointF(r.center().x(), r.bottom()),
            "bl": r.bottomLeft(),
            "l": QPointF(r.left(), r.center().y()),
        }
        for role, handle in self._handles.items():
            handle.setPos(positions[role])
            handle.setVisible(self.isSelected())


class DraggableZeroLine(QGraphicsLineItem):
    HIT_HEIGHT = 14.0

    def __init__(self, glass_id: str, y: float, ellipse: EllipseGeometry, callback) -> None:
        extent = ellipse.horizontal_extent_at(y) or (
            ellipse.center_x - ellipse.radius_x,
            ellipse.center_x + ellipse.radius_x,
        )
        super().__init__(extent[0], y, extent[1], y)
        self.glass_id = glass_id
        self.ellipse = ellipse
        self.callback = callback
        self._dragging = False
        self.setData(0, glass_id)
        self.setPen(QPen(QColor(255, 220, 0), 3, Qt.PenStyle.DashLine))
        self.setZValue(50)
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        self.label = QGraphicsSimpleTextItem("기준점", self)
        self.label.setBrush(QBrush(QColor(255, 240, 80)))
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._position_label()

    def shape(self) -> QPainterPath:
        line = self.line()
        path = QPainterPath()
        path.addRect(
            min(line.x1(), line.x2()),
            line.y1() - self.HIT_HEIGHT / 2,
            abs(line.x2() - line.x1()),
            self.HIT_HEIGHT,
        )
        return path

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging:
            self._set_y(event.scenePos().y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._dragging:
            self._set_y(event.scenePos().y())
            self._dragging = False
            self.callback(self.glass_id, self.line().y1())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _set_y(self, requested_y: float) -> None:
        minimum = self.ellipse.center_y - self.ellipse.radius_y
        maximum = self.ellipse.center_y + self.ellipse.radius_y
        y = min(maximum, max(minimum, requested_y))
        extent = self.ellipse.horizontal_extent_at(y)
        if extent is None:
            return
        self.setLine(extent[0], y, extent[1], y)
        self._position_label()

    def _position_label(self) -> None:
        line = self.line()
        self.label.setPos(line.x1() + 6, line.y1() - 22)


class EditableRectItem(QGraphicsRectItem):
    HANDLE = 10.0

    def __init__(self, glass_id: str, zone_id: str, rect: QRectF, frame_rect: QRectF, callback) -> None:
        super().__init__(rect)
        self.glass_id = glass_id
        self.zone_id = zone_id
        self.frame_rect = frame_rect
        self.callback = callback
        self._resize = False
        self._start = QRectF(rect)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
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
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
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
        scene_rect = scene_rect_in_frame(self, self.rect(), self.frame_rect)
        self.setPos(0, 0)
        self.setRect(scene_rect)
        self.callback(self.glass_id, self.zone_id, QRectF(self.rect()))
        self._resize = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        event.accept()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene() is not None:
            proposed = value
            moved = self.rect().translated(proposed)
            dx, dy = proposed.x(), proposed.y()
            if moved.left() < self.frame_rect.left():
                dx += self.frame_rect.left() - moved.left()
            if moved.right() > self.frame_rect.right():
                dx -= moved.right() - self.frame_rect.right()
            if moved.top() < self.frame_rect.top():
                dy += self.frame_rect.top() - moved.top()
            if moved.bottom() > self.frame_rect.bottom():
                dy -= moved.bottom() - self.frame_rect.bottom()
            return QPointF(dx, dy)
        return super().itemChange(change, value)


class VideoOverlayCanvas(QGraphicsView):
    geometryChanged = Signal(str, object)
    zeroLineChanged = Signal(str, float)
    exclusionChanged = Signal(str, str, object)
    glassSelected = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("videoCanvas")
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setBackgroundBrush(QColor(20, 22, 25))
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self._pixmap_item = QGraphicsPixmapItem()
        self._pixmap_item.setZValue(0)
        self._scene.addItem(self._pixmap_item)
        self._frame_size = (1280, 720)
        self._glasses = []
        self._selected_id: str | None = None
        self._detection = None
        self._detection_badge = None
        self._editable_ellipse_item = None
        self._fit_mode = True
        self._panning = False
        self._pan_start = None
        self.setMinimumSize(640, 420)

    @property
    def fit_mode(self) -> bool:
        return self._fit_mode

    def set_frame(self, frame, *, reset_view: bool = False) -> None:
        if frame is None:
            return
        if reset_view:
            self._fit_mode = True
        image = _FRAME_IMAGE_CONVERTER.to_qimage(frame)
        self._frame_size = (image.width(), image.height())
        self._pixmap_item.setPixmap(QPixmap.fromImage(image))
        self._scene.setSceneRect(0, 0, image.width(), image.height())
        self.rebuild_overlays()
        if self._fit_mode:
            self._apply_fit()

    def fit_to_view(self) -> None:
        self._fit_mode = True
        self._apply_fit()

    def zoom_in(self) -> None:
        self._zoom_by(ZOOM_STEP)

    def zoom_out(self) -> None:
        self._zoom_by(1.0 / ZOOM_STEP)

    def actual_size(self) -> None:
        if self._pixmap_item.pixmap().isNull():
            return
        center = self.mapToScene(self.viewport().rect().center())
        self._fit_mode = False
        self.resetTransform()
        self.centerOn(center)

    def _zoom_by(self, factor: float) -> None:
        if self._pixmap_item.pixmap().isNull():
            return
        current = abs(self.transform().m11()) or 1.0
        target = min(MAX_VIEW_SCALE, max(MIN_VIEW_SCALE, current * factor))
        applied = target / current
        if abs(applied - 1.0) < 1e-9:
            return
        self._fit_mode = False
        self.scale(applied, applied)

    def _apply_fit(self) -> None:
        if self._pixmap_item.pixmap().isNull():
            return
        self.resetTransform()
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_glasses(self, glasses, selected_id: str | None) -> None:
        self._glasses = list(glasses)
        self._selected_id = selected_id
        self.rebuild_overlays()

    def set_detection(self, detection) -> None:
        self._detection = detection
        self._refresh_detection_status()

    def rebuild_overlays(self) -> None:
        for item in list(self._scene.items()):
            if item is not self._pixmap_item:
                self._scene.removeItem(item)
        frame_rect = QRectF(0, 0, self._frame_size[0], self._frame_size[1])
        self._detection_badge = None
        self._editable_ellipse_item = None
        selected = None
        for glass in self._glasses:
            e = glass.geometry.ellipse
            rect = QRectF(
                e.center_x - e.radius_x,
                e.center_y - e.radius_y,
                e.radius_x * 2,
                e.radius_y * 2,
            )
            if glass.id == self._selected_id:
                selected = glass
                item = EditableEllipseItem(glass.id, rect, frame_rect, self._ellipse_changed)
                item.setSelected(True)
                item.setData(0, glass.id)
                self._editable_ellipse_item = item
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
            self._add_detection_status(selected, self._detection)

    def _add_selected_overlays(self, glass, frame_rect: QRectF) -> None:
        e = glass.geometry.ellipse
        ratio = glass.geometry.margin_ratio
        inner = QRectF(
            e.center_x - e.radius_x * (1 - ratio),
            e.center_y - e.radius_y * (1 - ratio),
            2 * e.radius_x * (1 - ratio),
            2 * e.radius_y * (1 - ratio),
        )
        margin = QGraphicsEllipseItem(inner)
        margin.setPen(QPen(QColor(80, 220, 120), 1, Qt.PenStyle.DotLine))
        margin.setZValue(35)
        self._scene.addItem(margin)
        if glass.geometry.zero_line_y is not None:
            self._scene.addItem(
                DraggableZeroLine(
                    glass.id,
                    glass.geometry.zero_line_y,
                    e,
                    self.zeroLineChanged.emit,
                )
            )
        for zone in glass.geometry.exclusions:
            r = zone.rect
            self._scene.addItem(
                EditableRectItem(
                    glass.id,
                    zone.id,
                    QRectF(r.x, r.y, r.width, r.height),
                    frame_rect,
                    self._exclusion_changed,
                )
            )
        label = QGraphicsSimpleTextItem(glass.name)
        label.setBrush(QBrush(QColor(255, 255, 255)))
        label.setPos(e.bounds.x, max(0, e.bounds.y - 22))
        label.setZValue(90)
        self._scene.addItem(label)

    def _add_detection_status(self, glass, detection) -> None:
        e = glass.geometry.ellipse
        badge = QGraphicsSimpleTextItem(
            f"{fill_state_label(detection.fill_state)} · 신뢰도 {detection.overall_confidence:.2f}"
        )
        badge.setBrush(QBrush(QColor(255, 255, 255)))
        badge.setPos(e.bounds.x, e.bounds.bottom + 4)
        badge.setZValue(90)
        badge.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._detection_badge = badge
        self._scene.addItem(badge)

    def _refresh_detection_status(self) -> None:
        if self._detection_badge is not None and self._detection_badge.scene() is self._scene:
            self._scene.removeItem(self._detection_badge)
        self._detection_badge = None
        if self._detection is None or self._detection.glass_id != self._selected_id:
            return
        selected = next((glass for glass in self._glasses if glass.id == self._selected_id), None)
        if selected is not None:
            self._add_detection_status(selected, self._detection)

    def _ellipse_changed(self, glass_id: str, rect: QRectF) -> None:
        ellipse = EllipseGeometry(
            rect.center().x(),
            rect.center().y(),
            rect.width() / 2,
            rect.height() / 2,
        )
        self.geometryChanged.emit(glass_id, ellipse)

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect: QRectF) -> None:
        self.exclusionChanged.emit(
            glass_id,
            zone_id,
            Rect(rect.x(), rect.y(), rect.width(), rect.height()),
        )

    def wheelEvent(self, event) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            elif event.angleDelta().y() < 0:
                self.zoom_out()
            event.accept()
            return
        super().wheelEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            if self.horizontalScrollBar().maximum() <= 0 and self.verticalScrollBar().maximum() <= 0:
                event.accept()
                return
            self._fit_mode = False
            self._panning = True
            self._pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        item = self.itemAt(event.position().toPoint())
        clicked_auxiliary = isinstance(item, (ResizeHandleItem, DraggableZeroLine))
        current = item
        while current is not None:
            glass_id = current.data(0)
            if glass_id:
                if str(glass_id) != self._selected_id:
                    self.glassSelected.emit(str(glass_id))
                break
            current = current.parentItem()
        super().mousePressEvent(event)
        if clicked_auxiliary and self._editable_ellipse_item is not None:
            self._editable_ellipse_item.setSelected(True)

    def mouseMoveEvent(self, event) -> None:
        if self._panning and self._pan_start is not None:
            current = event.position().toPoint()
            delta = current - self._pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start = current
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._panning and event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_start = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._fit_mode:
            self._apply_fit()


def _handle_cursor(role: str) -> Qt.CursorShape:
    if role in {"l", "r"}:
        return Qt.CursorShape.SizeHorCursor
    if role in {"t", "b"}:
        return Qt.CursorShape.SizeVerCursor
    if role in {"tl", "br"}:
        return Qt.CursorShape.SizeFDiagCursor
    return Qt.CursorShape.SizeBDiagCursor
