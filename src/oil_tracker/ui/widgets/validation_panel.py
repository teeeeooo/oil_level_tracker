from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from oil_tracker.domain.enums import ValidationSeverity
from oil_tracker.ui.presentation_labels import validation_issue_message, validation_severity_label


class ValidationPanel(QWidget):
    issueActivated = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.list = QListWidget()
        QVBoxLayout(self).addWidget(self.list)
        self.list.itemActivated.connect(
            lambda item: self.issueActivated.emit(item.data(Qt.ItemDataRole.UserRole))
        )

    def set_result(self, result) -> None:
        self.list.clear()
        for issue in result.issues:
            item = QListWidgetItem(
                f"[{validation_severity_label(issue.severity)}] {validation_issue_message(issue)}"
            )
            item.setData(Qt.ItemDataRole.UserRole, issue)
            if issue.severity == ValidationSeverity.ERROR:
                item.setForeground(Qt.GlobalColor.red)
            elif issue.severity == ValidationSeverity.WARNING:
                item.setForeground(Qt.GlobalColor.darkYellow)
            self.list.addItem(item)
