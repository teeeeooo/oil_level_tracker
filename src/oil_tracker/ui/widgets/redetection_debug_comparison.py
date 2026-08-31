from __future__ import annotations

import math

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.ui.widgets.result_debug_panel import ResultDebugPanel


class RedetectionDebugComparison(QWidget):
    officialArtifactRequested = Signal(str)
    rerunArtifactRequested = Signal(str)

    def __init__(self, *, artifact_only: bool, parent=None) -> None:
        super().__init__(parent)
        self.artifact_only = artifact_only
        self._syncing_artifact = False
        self.message = QLabel()
        self.message.setWordWrap(True)
        self.official = ResultDebugPanel()
        self.rerun = ResultDebugPanel()
        self.official.export_button.hide()
        self.rerun.export_button.hide()
        self.delta_table = QTableWidget()
        self.delta_table.setColumnCount(4)
        self.delta_table.setHorizontalHeaderLabels(
            ["선택 후보 항목", "공식", "재검출", "Delta / 상태"]
        )
        self.delta_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.delta_table.setAlternatingRowColors(True)
        self.delta_table.verticalHeader().setVisible(False)
        self.delta_table.setMinimumHeight(150)
        if artifact_only:
            self.official.tabs.setTabVisible(0, False)
            self.official.tabs.setTabVisible(1, False)
            self.rerun.tabs.setTabVisible(0, False)
            self.rerun.tabs.setTabVisible(1, False)
            self.official.tabs.setCurrentIndex(2)
            self.rerun.tabs.setCurrentIndex(2)
            self.delta_table.hide()
        else:
            self.official.tabs.setTabVisible(0, False)
            self.official.tabs.setTabVisible(2, False)
            self.rerun.tabs.setTabVisible(0, False)
            self.rerun.tabs.setTabVisible(2, False)
            self.official.tabs.setCurrentIndex(1)
            self.rerun.tabs.setCurrentIndex(1)
        split = QSplitter()
        split.addWidget(self.official)
        split.addWidget(self.rerun)
        split.setSizes([600, 600])
        layout = QVBoxLayout(self)
        layout.addWidget(self.message)
        layout.addWidget(split, 1)
        layout.addWidget(self.delta_table)
        self.official.artifactRequested.connect(self.officialArtifactRequested)
        self.rerun.artifactRequested.connect(self.rerunArtifactRequested)
        self.official.candidateSelected.connect(lambda _row: self._refresh_candidate_delta())
        self.rerun.candidateSelected.connect(lambda _row: self._refresh_candidate_delta())
        if artifact_only:
            self.official.artifact_combo.currentIndexChanged.connect(
                lambda _index: self._synchronize_artifact(self.official, self.rerun)
            )
            self.rerun.artifact_combo.currentIndexChanged.connect(
                lambda _index: self._synchronize_artifact(self.rerun, self.official)
            )
        self.clear()

    def clear(self, message: str = "comparison sample을 선택해 주세요.") -> None:
        self.message.setText(message)
        self.official.clear("공식 debug record 없음")
        self.rerun.clear("재검출 debug record 없음")
        self.delta_table.setRowCount(0)

    def set_records(self, official_record, rerun_record, *, official_message: str = "") -> None:
        if official_record is None:
            self.official.clear(
                official_message
                or "공식 분석 당시 후보 상세가 저장되지 않아 candidate 단위 비교는 제공할 수 없습니다."
            )
        else:
            self.official.set_record(official_record)
            self._select_saved_candidate(self.official, official_record)
        if rerun_record is None:
            self.rerun.clear("선택한 재검출 sample에 debug record가 없습니다.")
        else:
            self.rerun.set_record(rerun_record)
            self._select_saved_candidate(self.rerun, rerun_record)
        self.message.setText(
            "왼쪽: 공식 분석 · 오른쪽: 임시 설정 재검출"
            if official_record is not None
            else "공식 debug baseline 없이 재검출 후보와 artifact만 표시합니다."
        )
        self._refresh_candidate_delta()
        if self.artifact_only:
            self._synchronize_artifact(self.official, self.rerun)

    def set_official_artifact(self, key: str, image, error: str = "") -> None:
        self.official.set_artifact(key, image, error)

    def set_rerun_artifact(self, key: str, image, error: str = "") -> None:
        self.rerun.set_artifact(key, image, error)

    def _synchronize_artifact(self, source: ResultDebugPanel, target: ResultDebugPanel) -> None:
        if self._syncing_artifact:
            return
        key = source.current_artifact_key()
        if not key:
            return
        index = target.artifact_combo.findData(key)
        if index < 0 or index == target.artifact_combo.currentIndex():
            return
        self._syncing_artifact = True
        try:
            target.artifact_combo.setCurrentIndex(index)
        finally:
            self._syncing_artifact = False

    @staticmethod
    def _select_saved_candidate(panel: ResultDebugPanel, record) -> None:
        for index, candidate in enumerate(record.candidates):
            if candidate.get("selected"):
                panel.candidates.selectRow(index)
                return

    def _refresh_candidate_delta(self) -> None:
        if self.artifact_only:
            return
        official = self._selected_candidate(self.official)
        rerun = self._selected_candidate(self.rerun)
        rows: list[tuple[str, object, object, str]] = []
        for name in (
            "canonical_y",
            "rank",
            "source",
            "feature_score",
            "total_penalty",
            "final_score",
            "selected",
            "rejected",
            "reject_reason",
        ):
            left = None if official is None else official.get(name)
            right = None if rerun is None else rerun.get(name)
            rows.append((name, left, right, _delta_text(left, right)))
        feature_keys = sorted(
            set((official or {}).get("features") or {})
            | set((rerun or {}).get("features") or {})
        )
        penalty_keys = sorted(
            set((official or {}).get("penalties") or {})
            | set((rerun or {}).get("penalties") or {})
        )
        for key in feature_keys:
            left = ((official or {}).get("features") or {}).get(key)
            right = ((rerun or {}).get("features") or {}).get(key)
            rows.append((f"feature.{key}", left, right, _delta_text(left, right)))
        for key in penalty_keys:
            left = ((official or {}).get("penalties") or {}).get(key)
            right = ((rerun or {}).get("penalties") or {}).get(key)
            rows.append((f"penalty.{key}", left, right, _delta_text(left, right)))
        self.delta_table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                self.delta_table.setItem(row, column, QTableWidgetItem(_display(value)))
        self.delta_table.resizeColumnsToContents()
        self.delta_table.horizontalHeader().setStretchLastSection(True)

    @staticmethod
    def _selected_candidate(panel: ResultDebugPanel):
        record = panel._record
        row = panel.selected_candidate_index()
        if record is None or row is None or row < 0 or row >= len(record.candidates):
            return None
        return record.candidates[row]


def _display(value) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.6g}" if math.isfinite(value) else "-"
    return str(value)


def _delta_text(left, right) -> str:
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(
        right, (int, float)
    ) and not isinstance(right, bool):
        if math.isfinite(float(left)) and math.isfinite(float(right)):
            return f"{float(right) - float(left):+.6g}"
    if left is None or right is None:
        return "비교 없음"
    return "일치" if left == right else "변경"
