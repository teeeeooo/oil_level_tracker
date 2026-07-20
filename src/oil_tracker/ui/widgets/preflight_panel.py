from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.application.preflight import PreflightStatus
from oil_tracker.ui.presentation_labels import fill_state_label


_STATUS_LABELS = {
    PreflightStatus.NORMAL: "정상",
    PreflightStatus.REVIEW: "확인 필요",
    PreflightStatus.FAILURE: "실패",
}


class PreflightPanel(QWidget):
    runRequested = Signal()
    cancelRequested = Signal()
    resultActivated = Signal(str, float, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("preflightPanel")
        self._updating = False
        self._result = None

        self.status_label = QLabel("점검하지 않음")
        self.status_label.setObjectName("preflightStatus")
        self.detail_label = QLabel("분석 구간의 대표 장면을 검사해 설정 품질을 확인합니다.")
        self.detail_label.setWordWrap(True)
        self.progress_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.progress_label.hide()

        self.run_button = QPushButton("여러 시점 점검")
        self.run_button.setObjectName("primaryActionButton")
        self.cancel_button = QPushButton("취소")
        self.cancel_button.hide()
        self.rerun_button = QPushButton("다시 점검")
        self.rerun_button.hide()
        self.run_button.clicked.connect(self.runRequested)
        self.rerun_button.clicked.connect(self.runRequested)
        self.cancel_button.clicked.connect(self.cancelRequested)

        header = QHBoxLayout()
        header.addWidget(self.status_label)
        header.addStretch(1)
        header.addWidget(self.run_button)
        header.addWidget(self.cancel_button)
        header.addWidget(self.rerun_button)

        self.summary_table = self._table(
            ("관찰창", "최저 신뢰도", "정상", "확인 필요", "실패", "위치 급변", "대표 문제")
        )
        self.result_table = self._table(
            ("관찰창", "대표 시점", "실제 시각", "상태", "관측 상태", "신뢰도", "문제 사유")
        )
        self.result_table.itemSelectionChanged.connect(self._selected_result)
        self.result_table.cellDoubleClicked.connect(lambda row, _column: self._activate_row(row))

        tabs = QTabWidget()
        tabs.addTab(self.result_table, "시점별 결과")
        tabs.addTab(self.summary_table, "관찰창별 요약")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.addLayout(header)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(tabs, 1)
        self.set_unchecked()

    @staticmethod
    def _table(headers: tuple[str, ...]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    def set_unchecked(self) -> None:
        self._result = None
        self._clear_tables()
        self._set_status("점검하지 않음", "분석 구간의 대표 장면을 검사해 설정 품질을 확인합니다.", "unchecked")
        self._set_buttons(running=False, has_run=False)

    def set_running(self) -> None:
        self._result = None
        self._clear_tables()
        self._set_status("진행 중", "대표 장면을 준비하고 관찰창별 검출을 실행하고 있습니다.", "running")
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.progress_label.setText("점검을 시작합니다...")
        self.progress_label.show()
        self._set_buttons(running=True, has_run=False)

    def set_progress(self, update) -> None:
        self.progress_bar.setRange(0, max(1, int(update.total)))
        self.progress_bar.setValue(int(update.completed))
        self.progress_label.setText(
            f"{update.completed}/{update.total} · {update.sample_label} · {update.glass_name}"
        )

    def set_result(self, result) -> None:
        self._result = result
        label = _STATUS_LABELS[result.overall_status]
        if result.overall_status == PreflightStatus.NORMAL:
            detail = "모든 대표 시점에서 사용할 수 있는 검출 결과를 확인했습니다."
        elif result.overall_status == PreflightStatus.REVIEW:
            detail = "사용자가 확인해야 할 대표 장면이 있습니다. 결과 행을 선택하면 해당 시점으로 이동합니다."
        else:
            detail = "일부 대표 장면 또는 관찰창에서 검출에 실패했습니다. 결과 행에서 원인을 확인해 주세요."
        self._set_status(label, detail, result.overall_status.value)
        self.progress_bar.hide()
        self.progress_label.hide()
        self._populate_results(result)
        self._set_buttons(running=False, has_run=True)

    def set_stale(self) -> None:
        self._set_status(
            "재점검 필요",
            "영상, 시간 또는 관찰창 설정이 변경되었습니다. 표시된 결과는 이전 설정 기준입니다.",
            "stale",
        )
        self.progress_bar.hide()
        self.progress_label.hide()
        self._set_buttons(running=False, has_run=True)

    def set_failure(self, message: str) -> None:
        self._set_status("실패", message, "failure")
        self.progress_bar.hide()
        self.progress_label.hide()
        self._set_buttons(running=False, has_run=True)

    def set_cancelled(self) -> None:
        self._set_status("취소됨", "여러 시점 점검을 취소했습니다.", "cancelled")
        self.progress_bar.hide()
        self.progress_label.hide()
        self._set_buttons(running=False, has_run=True)

    def _set_status(self, status: str, detail: str, state: str) -> None:
        self.status_label.setText(status)
        self.status_label.setProperty("preflightState", state)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.detail_label.setText(detail)

    def _set_buttons(self, *, running: bool, has_run: bool) -> None:
        self.run_button.setVisible(not running and not has_run)
        self.cancel_button.setVisible(running)
        self.rerun_button.setVisible(not running and has_run)

    def _clear_tables(self) -> None:
        self._updating = True
        self.result_table.setRowCount(0)
        self.summary_table.setRowCount(0)
        self._updating = False

    def _populate_results(self, result) -> None:
        self._updating = True
        try:
            self.result_table.setRowCount(len(result.samples))
            for row, sample in enumerate(result.samples):
                values = (
                    sample.glass_name,
                    sample.sample_point.label,
                    f"{sample.sample_point.actual_timestamp:.3f} 초",
                    _STATUS_LABELS[sample.status],
                    "-" if sample.fill_state is None else fill_state_label(sample.fill_state),
                    "-" if sample.confidence is None else f"{sample.confidence * 100:.0f}%",
                    sample.reason,
                )
                for column, text in enumerate(values):
                    item = QTableWidgetItem(text)
                    if column == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            (sample.glass_id, sample.sample_point.actual_timestamp, sample.reason),
                        )
                    self.result_table.setItem(row, column, item)
            self.result_table.resizeColumnsToContents()

            self.summary_table.setRowCount(len(result.glass_summaries))
            for row, summary in enumerate(result.glass_summaries):
                values = (
                    summary.glass_name,
                    "-" if summary.minimum_confidence is None else f"{summary.minimum_confidence * 100:.0f}%",
                    str(summary.normal_count),
                    str(summary.review_count),
                    str(summary.failure_count),
                    "있음" if summary.position_jump_detected else "없음",
                    summary.representative_issue_reason or "-",
                )
                for column, text in enumerate(values):
                    self.summary_table.setItem(row, column, QTableWidgetItem(text))
            self.summary_table.resizeColumnsToContents()
        finally:
            self._updating = False

    def _selected_result(self) -> None:
        if self._updating:
            return
        rows = self.result_table.selectionModel().selectedRows()
        if rows:
            self._activate_row(rows[0].row())

    def _activate_row(self, row: int) -> None:
        item = self.result_table.item(row, 0)
        if item is None:
            return
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            glass_id, timestamp, reason = data
            self.resultActivated.emit(str(glass_id), float(timestamp), str(reason))
