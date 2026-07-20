from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class ValidationPanel(QWidget):
    issueActivated = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list = QListWidget(); QVBoxLayout(self).addWidget(self.list)
        self.list.itemActivated.connect(lambda item: self.issueActivated.emit(item.data(Qt.ItemDataRole.UserRole)))

    def set_result(self, result) -> None:
        self.list.clear()
        for issue in result.issues:
            item = QListWidgetItem(f"[{issue.severity.value}] {issue.message}")
            item.setData(Qt.ItemDataRole.UserRole, issue)
            if issue.severity.value == "Error": item.setForeground(Qt.GlobalColor.red)
            elif issue.severity.value == "Warning": item.setForeground(Qt.GlobalColor.darkYellow)
            self.list.addItem(item)
