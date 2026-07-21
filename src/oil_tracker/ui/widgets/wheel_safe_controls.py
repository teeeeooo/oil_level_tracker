from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox


class _WheelSafeMixin:
    """Let wheel gestures scroll the containing panel instead of editing a value."""

    def wheelEvent(self, event) -> None:  # noqa: N802 - Qt API
        event.ignore()


class WheelSafeSpinBox(_WheelSafeMixin, QSpinBox):
    pass


class WheelSafeDoubleSpinBox(_WheelSafeMixin, QDoubleSpinBox):
    pass


class WheelSafeComboBox(_WheelSafeMixin, QComboBox):
    pass
