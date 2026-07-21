from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QProgressBar,
    QVBoxLayout,
)

from oil_tracker.application.ports.progress import AnalysisStage


class AnalysisProgressDialog(QDialog):
    cancelRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("분석 실행")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.stage = QLabel("1/6 · 영상 분석")
        self.stage.setObjectName("analysisProgressStage")
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setFormat("전체 진행률 %p%")
        self.detail = QLabel("영상과 분석 영역을 준비하고 있습니다.")
        self.detail.setWordWrap(True)
        self.frame_detail = QLabel("")
        self.rate = QLabel("")
        self.finishing = QLabel("")
        self.finishing.setWordWrap(True)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button = self.buttons.button(QDialogButtonBox.StandardButton.Cancel)
        self.buttons.rejected.connect(self._request_cancel)
        layout = QVBoxLayout(self)
        layout.addWidget(self.stage)
        layout.addWidget(self.progress)
        layout.addWidget(self.detail)
        layout.addWidget(self.frame_detail)
        layout.addWidget(self.rate)
        layout.addWidget(self.finishing)
        layout.addWidget(self.buttons)
        self._last_value = 0
        self._terminal = False

    def update_progress(self, update) -> None:
        if self._terminal:
            return
        value = int(update.overall_fraction * 1000)
        if update.overall_fraction < 1.0:
            value = min(999, value)
        value = max(self._last_value, value)
        self._last_value = value
        self.progress.setValue(value)
        self.stage.setText(f"{update.stage_index}/{update.stage_count} · {update.stage_label}")
        self.detail.setText(update.message or update.stage_label)
        is_video = update.stage_key is AnalysisStage.VIDEO_ANALYSIS
        self.frame_detail.setVisible(is_video)
        self.rate.setVisible(is_video)
        if is_video:
            parts = []
            if update.completed or update.total:
                parts.append(f"처리 {update.completed}/{update.total}")
            if update.timestamp_sec is not None:
                parts.append(f"현재 시각 {update.timestamp_sec:.3f}초")
            if update.glass_name:
                parts.append(f"Glass {update.glass_name}")
            self.frame_detail.setText(" · ".join(parts))
            self.rate.setText(
                ""
                if update.rate_fps is None
                else f"처리 속도 {update.rate_fps:.2f} sampled frames/s"
            )
        else:
            self.frame_detail.clear()
            self.rate.clear()
        if update.stage_key is AnalysisStage.BUNDLE_FINALIZATION:
            self.finishing.setText(
                "완성된 결과 bundle을 안전하게 연결하는 중입니다. 이 단계가 끝난 뒤 완료 화면이 표시됩니다."
            )
        else:
            self.finishing.clear()

    def mark_cancelled(self) -> None:
        self._terminal = True
        self.detail.setText("분석이 취소되었습니다. 임시 결과를 정리했습니다.")
        self.cancel_button.setEnabled(False)

    def mark_failed(self, message: str = "") -> None:
        self._terminal = True
        self.detail.setText(message or "분석에 실패했습니다.")
        self.cancel_button.setEnabled(False)

    def mark_completed(self) -> None:
        self._terminal = True
        self.progress.setValue(1000)
        self.detail.setText("결과 bundle 생성이 완료되었습니다.")
        self.cancel_button.setEnabled(False)

    def _request_cancel(self) -> None:
        if self._terminal or not self.cancel_button.isEnabled():
            return
        self.cancel_button.setEnabled(False)
        self.detail.setText("취소 요청을 처리하고 임시 결과를 정리하고 있습니다.")
        self.finishing.setText("현재 작업 단위가 안전하게 종료될 때까지 창을 유지합니다.")
        self.cancelRequested.emit()

    def reject(self) -> None:
        if self._terminal:
            super().reject()
        else:
            self._request_cancel()
