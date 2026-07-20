from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class BottomActionBar(QWidget):
    validateRequested = Signal()
    saveRequested = Signal()
    analyzeRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("guidedActionBar")

        self.status = QLabel("설정을 확인하고 있습니다.")
        self.status.setObjectName("guidedStatusLabel")

        self.validate_button = QPushButton("설정 점검")
        self.save_button = QPushButton("프로필 저장")
        self.analyze_button = QPushButton("분석 실행")
        self.analyze_button.setObjectName("primaryActionButton")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 7, 10, 7)
        layout.setSpacing(7)
        layout.addWidget(self.status, 1)
        layout.addWidget(self.validate_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.analyze_button)

        self.validate_button.clicked.connect(self.validateRequested)
        self.save_button.clicked.connect(self.saveRequested)
        self.analyze_button.clicked.connect(self.analyzeRequested)
        self.analyze_button.setEnabled(False)

    def set_validation_result(self, result) -> None:
        errors = len(result.errors)
        warnings = len(result.warnings)
        if errors:
            text = f"설정 오류 {errors}개"
            if warnings:
                text += f" · 주의 {warnings}개"
            state = "error"
        elif warnings:
            text = f"분석 가능 · 주의 {warnings}개"
            state = "warning"
        else:
            text = "분석 준비 완료"
            state = "ready"

        self.status.setText(text)
        self.status.setProperty("validationState", state)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.analyze_button.setEnabled(result.is_ready)
