from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget


class GlassListPanel(QWidget):
    addRequested = Signal()
    deleteRequested = Signal()
    selectionChanged = Signal(str)
    enabledChanged = Signal(str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list = QListWidget()
        self.list.currentItemChanged.connect(self._selected)
        self.list.itemChanged.connect(self._checked)
        self.add_button = QPushButton("Glass 추가")
        self.delete_button = QPushButton("삭제")
        self.add_button.clicked.connect(self.addRequested)
        self.delete_button.clicked.connect(self.deleteRequested)
        buttons = QHBoxLayout(); buttons.addWidget(self.add_button); buttons.addWidget(self.delete_button)
        layout = QVBoxLayout(self); layout.addWidget(self.list); layout.addLayout(buttons)
        self.setMinimumWidth(180)

    def set_glasses(self, glasses, selected_id: str | None) -> None:
        self.list.blockSignals(True)
        self.list.clear()
        selected_row = -1
        for row, glass in enumerate(glasses):
            item = QListWidgetItem(glass.name)
            item.setData(Qt.ItemDataRole.UserRole, glass.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if glass.enabled else Qt.CheckState.Unchecked)
            self.list.addItem(item)
            if glass.id == selected_id:
                selected_row = row
        if selected_row >= 0:
            self.list.setCurrentRow(selected_row)
        self.list.blockSignals(False)

    def _selected(self, current, _previous) -> None:
        if current:
            self.selectionChanged.emit(current.data(Qt.ItemDataRole.UserRole))

    def _checked(self, item) -> None:
        self.enabledChanged.emit(item.data(Qt.ItemDataRole.UserRole), item.checkState() == Qt.CheckState.Checked)
