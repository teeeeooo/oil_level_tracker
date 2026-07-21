from __future__ import annotations

from PySide6.QtWidgets import QAbstractScrollArea, QComboBox, QDoubleSpinBox, QSpinBox


class _WheelSafeMixin:
    """Scroll the containing panel instead of editing a focused value control."""

    def wheelEvent(self, event) -> None:  # noqa: N802 - Qt API
        scroll_area = self._containing_scroll_area()
        if scroll_area is None:
            event.ignore()
            return

        vertical = scroll_area.verticalScrollBar()
        horizontal = scroll_area.horizontalScrollBar()
        pixel_delta = event.pixelDelta()
        angle_delta = event.angleDelta()

        if pixel_delta.y() and vertical.maximum() > vertical.minimum():
            vertical.setValue(vertical.value() - pixel_delta.y())
            event.accept()
            return
        if angle_delta.y() and vertical.maximum() > vertical.minimum():
            steps = angle_delta.y() / 120.0
            distance = max(vertical.singleStep(), 1) * 3
            vertical.setValue(vertical.value() - round(steps * distance))
            event.accept()
            return
        if pixel_delta.x() and horizontal.maximum() > horizontal.minimum():
            horizontal.setValue(horizontal.value() - pixel_delta.x())
            event.accept()
            return
        if angle_delta.x() and horizontal.maximum() > horizontal.minimum():
            steps = angle_delta.x() / 120.0
            distance = max(horizontal.singleStep(), 1) * 3
            horizontal.setValue(horizontal.value() - round(steps * distance))
            event.accept()
            return
        event.ignore()

    def _containing_scroll_area(self) -> QAbstractScrollArea | None:
        parent = self.parentWidget()
        while parent is not None:
            if isinstance(parent, QAbstractScrollArea):
                return parent
            parent = parent.parentWidget()
        return None


class WheelSafeSpinBox(_WheelSafeMixin, QSpinBox):
    pass


class WheelSafeDoubleSpinBox(_WheelSafeMixin, QDoubleSpinBox):
    pass


class WheelSafeComboBox(_WheelSafeMixin, QComboBox):
    pass
