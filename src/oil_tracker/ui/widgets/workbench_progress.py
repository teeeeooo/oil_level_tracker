from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from oil_tracker.ui.readiness import ProgressStepState


_SYMBOLS = {
    ProgressStepState.COMPLETE: "✓",
    ProgressStepState.CURRENT: "▶",
    ProgressStepState.ERROR: "●",
    ProgressStepState.WARNING: "⚠",
    ProgressStepState.WAITING: "○",
}

_LABELS = {
    ProgressStepState.COMPLETE: "완료",
    ProgressStepState.CURRENT: "현재",
    ProgressStepState.ERROR: "수정 필요",
    ProgressStepState.WARNING: "확인 필요",
    ProgressStepState.WAITING: "대기",
}


class WorkbenchProgressWidget(QWidget):
    stepActivated = Signal(str)
    nextIssueRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("workbenchProgress")
        title = QLabel("작업 진행")
        title.setObjectName("progressTitle")
        title.hide()
        self.preflight_status = QLabel("사전 점검 · 미실행")
        self.preflight_status.setObjectName("preflightProgressStatus")
        self._buttons: dict[str, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(5)
        for index, (key, label) in enumerate(
            (
                ("video", "영상 선택"),
                ("time", "시간 설정"),
                ("glasses", "Glass 설정"),
                ("validation", "설정 점검"),
                ("analysis", "분석 실행"),
            )
        ):
            button = QPushButton(label)
            button.setObjectName("progressStepButton")
            button.setMinimumHeight(36)
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda _checked=False, step_key=key: self.stepActivated.emit(step_key))
            self._buttons[key] = button
            layout.addWidget(button, 1)
            if index < 4:
                arrow = QLabel("→")
                arrow.setObjectName("progressArrow")
                layout.addWidget(arrow)

        self.next_issue = QPushButton("문제 위치")
        self.next_issue.setObjectName("nextIssueButton")
        self.next_issue.clicked.connect(self.nextIssueRequested)
        self.next_issue.hide()

        layout.addSpacing(5)
        layout.addWidget(self.preflight_status)
        layout.addWidget(self.next_issue)

    def set_steps(self, steps, has_glass_issue: bool) -> None:
        for step in steps:
            button = self._buttons[step.key]
            button.setText(f"{_SYMBOLS[step.state]} {step.label}")
            button.setToolTip(step.detail)
            button.setProperty("stepState", step.state.value)
            button.style().unpolish(button)
            button.style().polish(button)
        self.next_issue.setVisible(has_glass_issue)

    def set_preflight_status(self, status: str, detail: str) -> None:
        self.preflight_status.setText(f"사전 점검 · {status}")
        self.preflight_status.setToolTip(detail)
        self.preflight_status.setProperty("preflightState", status)
        self.preflight_status.style().unpolish(self.preflight_status)
        self.preflight_status.style().polish(self.preflight_status)
