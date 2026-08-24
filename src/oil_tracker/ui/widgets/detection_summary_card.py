from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from oil_tracker.ui.readiness import build_detection_summary


class DetectionSummaryCard(QGroupBox):
    initialStateRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__("현재 장면", parent)
        self.setObjectName("detectionSummaryCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 7, 8, 7)
        layout.setSpacing(5)
        self.values: dict[str, QLabel] = {}
        metrics = QGridLayout()
        metrics.setHorizontalSpacing(8)
        metrics.setVerticalSpacing(2)
        for column, (key, label) in enumerate(
            (
                ("status", "상태"),
                ("fill_state", "관측 상태"),
                ("confidence", "신뢰도"),
                ("reference", "기준점"),
            )
        ):
            heading = QLabel(label)
            heading.setObjectName("detectionSummaryHeading")
            value = QLabel("-")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            value.setWordWrap(True)
            self.values[key] = value
            metrics.addWidget(heading, 0, column)
            metrics.addWidget(value, 1, column)
            metrics.setColumnStretch(column, 1)
        layout.addLayout(metrics)

        self.values["interpretation"] = QLabel("-")
        self.values["interpretation"].setObjectName("detectionSummaryInterpretation")
        self.values["interpretation"].setWordWrap(True)
        layout.addWidget(self.values["interpretation"])
        self.values["recommendation"] = QLabel("-")
        self.values["recommendation"].setObjectName("detectionSummaryRecommendation")
        self.values["recommendation"].setWordWrap(True)
        layout.addWidget(self.values["recommendation"])
        # Keep the pre-S3 field lookup available for callers while presenting the new wording.
        self.values["judgment"] = self.values["interpretation"]
        self.action_button = QPushButton("초기 상태 설정으로 이동")
        self.action_button.setObjectName("secondaryActionButton")
        self.action_button.clicked.connect(self.initialStateRequested)
        self.action_button.hide()
        layout.addWidget(self.action_button)
        self.set_empty("시험 영상과 Glass를 선택해 주세요")

    def set_empty(self, message: str) -> None:
        self._set_values("대기", "-", "-", "-", message, "-", "empty", False)

    def set_loading(self) -> None:
        self._set_values(
            "분석 중",
            "-",
            "-",
            "-",
            "현재 장면을 확인하고 있습니다",
            "잠시 후 안내를 확인하세요.",
            "loading",
            False,
        )

    def set_failure(self, message: str) -> None:
        self._set_values(
            "검출 실패",
            "-",
            "-",
            "-",
            message,
            "분석 영역과 현재 영상 장면을 확인하세요.",
            "failure",
            False,
        )

    def set_detection(self, detection, glass, *, allow_initial_state_action: bool = False) -> None:
        summary = build_detection_summary(detection, glass)
        self._set_values(
            summary.detection_status,
            summary.fill_state,
            summary.confidence,
            summary.reference_position,
            summary.interpretation,
            summary.recommendation,
            summary.quality.value,
            bool(summary.action_key == "initial_state" and allow_initial_state_action),
        )

    def _set_values(
        self,
        status: str,
        fill_state: str,
        confidence: str,
        reference: str,
        interpretation: str,
        recommendation: str,
        quality: str,
        show_action: bool,
    ) -> None:
        for key, text in (
            ("status", status),
            ("fill_state", fill_state),
            ("confidence", confidence),
            ("reference", reference),
            ("interpretation", interpretation),
            ("recommendation", recommendation),
        ):
            self.values[key].setText(text)
        self.action_button.setVisible(show_action)
        self.setProperty("quality", quality)
        self.style().unpolish(self)
        self.style().polish(self)
