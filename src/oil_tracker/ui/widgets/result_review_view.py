from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class ResultReviewView(QWidget):
    def __init__(self, result, output_path: str, parent=None) -> None:
        super().__init__(parent); self.output_path = output_path
        label = QLabel(f"Overall: {result.overall_state.value}\nOutput: {output_path}")
        button = QPushButton("HTML 보고서 열기"); button.clicked.connect(self.open_report)
        layout = QVBoxLayout(self); layout.addWidget(label); layout.addWidget(button)

    def open_report(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(f"{self.output_path}/report.html"))
