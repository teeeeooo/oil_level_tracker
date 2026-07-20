from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QProgressBar, QVBoxLayout


class AnalysisProgressDialog(QDialog):
    cancelRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent); self.setWindowTitle("분석 실행"); self.setModal(True); self.setMinimumWidth(480)
        self.progress = QProgressBar(); self.detail = QLabel("준비 중..."); self.rate = QLabel("")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel); buttons.rejected.connect(self.cancelRequested)
        layout = QVBoxLayout(self); layout.addWidget(self.progress); layout.addWidget(self.detail); layout.addWidget(self.rate); layout.addWidget(buttons)

    def update_progress(self, update) -> None:
        self.progress.setRange(0, update.total); self.progress.setValue(update.completed)
        self.detail.setText(f"{update.timestamp_sec:.3f}s | {update.glass_name}")
        self.rate.setText(f"처리 속도 {update.rate_fps:.2f} sampled frames/s")
