from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from oil_tracker.ui.widgets.preflight_panel import PreflightPanel


class PreflightWindow(QWidget):
    """One reusable modeless preflight shell per Workbench."""

    def __init__(self, panel: PreflightPanel | None = None, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.Window)
        self.setObjectName("preflightWindow")
        self.setWindowTitle("여러 시점 점검")
        self.setMinimumSize(900, 540)
        self.resize(1100, 680)
        self.panel = panel or PreflightPanel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.panel)
