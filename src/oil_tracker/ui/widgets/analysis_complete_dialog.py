from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from oil_tracker.ui.analysis_completion_summary import FinalRunSummary, build_final_run_summary
from oil_tracker.ui.presentation_labels import result_state_label


class AnalysisCompleteDialog(QDialog):
    reviewRequested = Signal()
    reportRequested = Signal()
    folderRequested = Signal()
    sameProfileRequested = Signal()

    def __init__(
        self,
        result,
        output_path: str | Path,
        parent=None,
        *,
        summary: FinalRunSummary | None = None,
    ) -> None:
        super().__init__(parent)
        self.result = result
        self.output_path = Path(output_path)
        self.summary = summary or build_final_run_summary(result, output_path)
        self.setWindowTitle("분석 완료")
        self.setModal(False)
        self.setMinimumWidth(620)
        layout = QVBoxLayout(self)
        self.title_label = QLabel(
            f"분석 완료 · 전체 판정: {result_state_label(self.summary.overall_state)}"
        )
        self.title_label.setObjectName("analysisCompleteTitle")
        layout.addWidget(self.title_label)

        layout.addWidget(QLabel("완료한 시험 식별"))
        identity = QGridLayout()
        identity.addWidget(QLabel("현재 시험"), 0, 0)
        self.run_name_label = QLabel(
            self.summary.run_name or "이름 없음 (현재 시험 이름 미지정)"
        )
        self.run_name_label.setObjectName("completedRunName")
        identity.addWidget(self.run_name_label, 0, 1)
        identity.addWidget(QLabel("Profile"), 1, 0)
        self.profile_name_label = QLabel(self.summary.profile_name or "확인할 수 없음")
        self.profile_name_label.setObjectName("completedProfileName")
        identity.addWidget(self.profile_name_label, 1, 1)
        identity.addWidget(QLabel("시험 영상"), 2, 0)
        self.source_video_label = QLabel(self.summary.source_video_name or "확인할 수 없음")
        self.source_video_label.setObjectName("completedSourceVideo")
        self.source_video_label.setToolTip(self.summary.source_video_path)
        identity.addWidget(self.source_video_label, 2, 1)
        layout.addLayout(identity)
        self.metadata_status_label = QLabel()
        self.metadata_status_label.setObjectName("completedMetadataStatus")
        self.metadata_status_label.setWordWrap(True)
        if not self.summary.finalized_metadata_available:
            self.metadata_status_label.setText(
                "결과 bundle의 식별 메타데이터를 읽지 못했습니다. 판정과 결과 경로는 완료된 분석 기준으로 유지됩니다."
            )
            layout.addWidget(self.metadata_status_label)

        self.path_label = QLabel(str(self.summary.output_path))
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(QLabel("완료 결과 위치"))
        layout.addWidget(self.path_label)
        self.summary_label = QLabel(self._glass_summary())
        self.summary_label.setWordWrap(True)
        layout.addWidget(QLabel("Glass별 판정"))
        layout.addWidget(self.summary_label)
        self.counts_label = QLabel(
            f"경고 {self.summary.warning_count}개 · 오류 {self.summary.error_count}개 · 상태: ANALYZED"
        )
        layout.addWidget(self.counts_label)
        actions = QGridLayout()
        self.review_button = QPushButton("완료 결과 검토")
        self.report_button = QPushButton("결과 보고서 열기")
        self.folder_button = QPushButton("결과 폴더 열기")
        self.same_profile_button = QPushButton("같은 Profile로 다음 영상 분석")
        actions.addWidget(self.review_button, 0, 0)
        actions.addWidget(self.report_button, 0, 1)
        actions.addWidget(self.folder_button, 1, 0)
        actions.addWidget(self.same_profile_button, 1, 1)
        layout.addLayout(actions)
        self.close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.close_box.rejected.connect(self.reject)
        layout.addWidget(self.close_box)
        self.review_button.clicked.connect(self.reviewRequested)
        self.report_button.clicked.connect(self.reportRequested)
        self.folder_button.clicked.connect(self.folderRequested)
        self.same_profile_button.clicked.connect(self.sameProfileRequested)

    def _glass_summary(self) -> str:
        if not self.summary.glasses:
            return "Glass 판정 없음"
        return "\n".join(
            f"• {glass.name}: {result_state_label(glass.result_state)}"
            for glass in self.summary.glasses
        )
