from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from oil_tracker.ui.presentation_labels import result_state_label


class AnalysisCompleteDialog(QDialog):
    reviewRequested = Signal()
    reportRequested = Signal()
    folderRequested = Signal()
    sameProfileRequested = Signal()

    def __init__(self, result, output_path: str | Path, parent=None) -> None:
        super().__init__(parent)
        self.result = result
        self.output_path = Path(output_path)
        self.setWindowTitle("분석 완료")
        self.setModal(False)
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        title = QLabel(f"분석 완료 · 전체 판정: {result_state_label(result.overall_state)}")
        title.setObjectName("analysisCompleteTitle")
        layout.addWidget(title)
        path_label = QLabel(str(self.output_path))
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(path_label.textInteractionFlags())
        layout.addWidget(QLabel("결과 bundle 경로"))
        layout.addWidget(path_label)
        summary = QLabel(self._glass_summary())
        summary.setWordWrap(True)
        layout.addWidget(QLabel("관찰창별 판정"))
        layout.addWidget(summary)
        counts = QLabel(f"경고 {len(result.warnings)}개 · 오류 {len(result.errors)}개 · 상태: ANALYZED")
        layout.addWidget(counts)
        actions = QGridLayout()
        self.review_button = QPushButton("결과 영상 검토")
        self.report_button = QPushButton("결과 보고서 열기")
        self.folder_button = QPushButton("결과 폴더 열기")
        self.same_profile_button = QPushButton("같은 프로필로 새 영상 분석")
        actions.addWidget(self.review_button, 0, 0)
        actions.addWidget(self.report_button, 0, 1)
        actions.addWidget(self.folder_button, 1, 0)
        actions.addWidget(self.same_profile_button, 1, 1)
        layout.addLayout(actions)
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_box.rejected.connect(self.reject)
        layout.addWidget(close_box)
        self.review_button.clicked.connect(self.reviewRequested)
        self.report_button.clicked.connect(self.reportRequested)
        self.folder_button.clicked.connect(self.folderRequested)
        self.same_profile_button.clicked.connect(self.sameProfileRequested)

    def _glass_summary(self) -> str:
        if not self.result.glass_results:
            return "관찰창 판정 없음"
        return "\n".join(
            f"• {glass.glass_name}: {result_state_label(glass.result_state)}"
            for glass in self.result.glass_results
        )
