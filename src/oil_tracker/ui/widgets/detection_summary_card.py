from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, QSizePolicy

from oil_tracker.ui.readiness import build_detection_summary


class DetectionSummaryCard(QGroupBox):
    initialStateRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__("현재 장면", parent)
        self.setObjectName("detectionSummaryCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setHorizontalSpacing(8)
        layout.setVerticalSpacing(3)
        self.values: dict[str, QLabel] = {}
        for row, (key, label) in enumerate(
            (
                ("status", "상태"),
                ("fill_state", "관측 상태"),
                ("reference", "유면 위치"),
            )
        ):
            heading = QLabel(label)
            heading.setObjectName("detectionSummaryHeading")
            value = QLabel("-")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)
            self.values[key] = value
            layout.addWidget(heading, row, 0)
            layout.addWidget(value, row, 1)
        self.message = QLabel()
        self.message.setObjectName("detectionSummaryMessage")
        self.message.setWordWrap(True)
        self.message.hide()
        layout.addWidget(self.message, 3, 0, 1, 2)
        # Retain internal lookup aliases without rendering duplicate explanation rows.
        self.values["judgment"] = self.message
        self.values["interpretation"] = self.message
        self.values["recommendation"] = self.message
        self.action_button = QPushButton("시작 상태 확인")
        self.action_button.setObjectName("secondaryActionButton")
        self.action_button.clicked.connect(self.initialStateRequested)
        self.action_button.hide()
        layout.addWidget(self.action_button, 4, 0, 1, 2)
        layout.setColumnStretch(1, 1)
        self.set_empty("시험 영상과 Glass를 선택해 주세요")

    def set_empty(self, message: str) -> None:
        self._set_values("대기", "-", "-", message, "empty", False)

    def set_loading(self) -> None:
        self._set_values(
            "분석 중",
            "-",
            "-",
            "",
            "loading",
            False,
        )

    def set_failure(self, message: str) -> None:
        self._set_values(
            "검출 실패",
            "-",
            "-",
            message,
            "failure",
            False,
        )

    def set_detection(self, detection, glass, *, allow_initial_state_action: bool = False) -> None:
        summary = build_detection_summary(detection, glass)
        show_action = bool(summary.action_key == "initial_state" and allow_initial_state_action)
        self._set_values(
            summary.detection_status,
            summary.fill_state,
            summary.reference_position,
            "분석 시작 상태를 직접 확인해 주세요." if show_action else "",
            summary.quality.value,
            show_action,
        )

    def _set_values(
        self,
        status: str,
        fill_state: str,
        reference: str,
        message: str,
        quality: str,
        show_action: bool,
    ) -> None:
        for key, text in (
            ("status", status),
            ("fill_state", fill_state),
            ("reference", reference),
        ):
            self.values[key].setText(text)
        self.message.setText(message)
        self.message.setVisible(bool(message))
        self.action_button.setVisible(show_action)
        self.setProperty("quality", quality)
        self.style().unpolish(self)
        self.style().polish(self)
