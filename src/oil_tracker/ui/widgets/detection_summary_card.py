from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QSizePolicy

from oil_tracker.ui.readiness import PreviewQuality, build_detection_summary


class DetectionSummaryCard(QGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__("현재 장면 검출", parent)
        self.setObjectName("detectionSummaryCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        layout = QGridLayout(self)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(3)
        self.values: dict[str, QLabel] = {}
        for row, (key, label) in enumerate(
            (
                ("status", "상태"),
                ("fill_state", "관측 상태"),
                ("confidence", "신뢰도"),
                ("reference", "기준점"),
                ("judgment", "판정"),
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
        layout.setColumnStretch(1, 1)
        self.set_empty("시험 영상과 관찰창을 선택해 주세요")

    def set_empty(self, message: str) -> None:
        self._set_values("대기", "-", "-", "-", message, "empty")

    def set_loading(self) -> None:
        self._set_values("분석 중", "-", "-", "-", "현재 장면을 확인하고 있습니다", "loading")

    def set_failure(self, message: str) -> None:
        self._set_values("검출 실패", "-", "-", "-", message, "failure")

    def set_detection(self, detection, glass) -> None:
        summary = build_detection_summary(detection, glass)
        self._set_values(
            summary.detection_status,
            summary.fill_state,
            summary.confidence,
            summary.reference_position,
            summary.judgment,
            summary.quality.value,
        )

    def _set_values(
        self,
        status: str,
        fill_state: str,
        confidence: str,
        reference: str,
        judgment: str,
        quality: str,
    ) -> None:
        for key, text in (
            ("status", status),
            ("fill_state", fill_state),
            ("confidence", confidence),
            ("reference", reference),
            ("judgment", judgment),
        ):
            self.values[key].setText(text)
        self.setProperty("quality", quality)
        self.style().unpolish(self)
        self.style().polish(self)
