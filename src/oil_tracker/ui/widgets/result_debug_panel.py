from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


_ARTIFACT_LABELS = {
    "overlay": "검출 overlay",
    "original_roi": "원본 ROI",
    "ellipse_mask": "ellipse mask",
    "effective_mask": "effective mask",
    "exclusion_mask": "exclusion mask",
    "grayscale": "grayscale",
    "normalized": "normalized",
    "blurred": "blurred",
    "sobel": "Sobel",
    "canny": "Canny",
    "horizontal_mask": "horizontal mask",
    "glare_mask": "glare mask",
    "foam_mask": "foam mask",
    "foam_variance": "foam variance",
    "static_artifact_map": "static artifact map",
}

_COLUMNS = (
    ("rank", "순위"),
    ("kind", "종류"),
    ("source", "출처"),
    ("canonical_y", "Y"),
    ("feature_score", "feature"),
    ("total_penalty", "penalty"),
    ("final_score", "final"),
    ("selected", "선택"),
    ("rejected", "탈락"),
    ("reject_reason", "탈락 사유"),
)


class ResultDebugPanel(QWidget):
    candidateSelected = Signal(int)
    artifactRequested = Signal(str)
    exportRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(420)
        self._record = None
        self._pixmap = QPixmap()
        self._scale = 1.0
        self.summary = QLabel("디버그 장면을 선택해 주세요.")
        self.summary.setWordWrap(True)
        self.tabs = QTabWidget()

        candidate_page = QWidget()
        candidate_layout = QVBoxLayout(candidate_page)
        self.candidates = QTableWidget()
        self.candidates.setColumnCount(len(_COLUMNS))
        self.candidates.setHorizontalHeaderLabels([title for _key, title in _COLUMNS])
        self.candidates.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.candidates.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.candidate_detail = QTextEdit()
        self.candidate_detail.setReadOnly(True)
        candidate_split = QSplitter(Qt.Orientation.Vertical)
        candidate_split.addWidget(self.candidates)
        candidate_split.addWidget(self.candidate_detail)
        candidate_split.setSizes([360, 240])
        candidate_layout.addWidget(candidate_split)
        self.tabs.addTab(candidate_page, "후보와 점수")

        self.state_detail = QTextEdit()
        self.state_detail.setReadOnly(True)
        self.tabs.addTab(self.state_detail, "상태와 smoothing")

        artifact_page = QWidget()
        artifact_layout = QVBoxLayout(artifact_page)
        controls = QHBoxLayout()
        self.artifact_combo = QComboBox()
        for key, label in _ARTIFACT_LABELS.items():
            self.artifact_combo.addItem(label, key)
        self.fit_button = QPushButton("화면 맞춤")
        self.actual_button = QPushButton("원본 크기")
        self.zoom_out = QPushButton("−")
        self.zoom_in = QPushButton("+")
        controls.addWidget(self.artifact_combo, 1)
        controls.addWidget(self.fit_button)
        controls.addWidget(self.actual_button)
        controls.addWidget(self.zoom_out)
        controls.addWidget(self.zoom_in)
        self.artifact_status = QLabel("artifact 없음")
        self.artifact_status.setWordWrap(True)
        self.image_label = QLabel("artifact를 선택해 주세요.")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(360, 260)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(False)
        self.image_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_scroll.setWidget(self.image_label)
        artifact_layout.addLayout(controls)
        artifact_layout.addWidget(self.artifact_status)
        artifact_layout.addWidget(self.image_scroll, 1)
        self.tabs.addTab(artifact_page, "검출 artifact")

        self.export_button = QPushButton("선택 장면 디버그 재현 패키지 내보내기")
        layout = QVBoxLayout(self)
        layout.addWidget(self.summary)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.export_button)

        self.candidates.currentCellChanged.connect(self._candidate_changed)
        self.artifact_combo.currentIndexChanged.connect(self._artifact_changed)
        self.fit_button.clicked.connect(self.fit_image)
        self.actual_button.clicked.connect(lambda: self._set_scale(1.0))
        self.zoom_out.clicked.connect(lambda: self._set_scale(self._scale / 1.25))
        self.zoom_in.clicked.connect(lambda: self._set_scale(self._scale * 1.25))
        self.export_button.clicked.connect(self.exportRequested)
        self.clear()

    def clear(self, message: str = "디버그 장면을 선택해 주세요.") -> None:
        self._record = None
        self._pixmap = QPixmap()
        self.summary.setText(message)
        self.candidates.setRowCount(0)
        self.candidate_detail.clear()
        self.state_detail.clear()
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("artifact를 선택해 주세요.")
        self.artifact_status.setText("artifact 없음")
        self.export_button.setEnabled(False)

    def set_record(self, record, actual_timestamp: float | None = None) -> None:
        previous_row = self.candidates.currentRow() if self._record is record else -1
        self._record = record
        delta_text = ""
        if actual_timestamp is not None:
            delta = float(actual_timestamp) - float(record.timestamp_sec)
            delta_text = f" · decoded 차이 {delta:+.3f}초"
        self.summary.setText(
            f"{record.glass_name or record.glass_id} · trace {record.timestamp_sec:.3f}초 · 장면 {record.frame_index}{delta_text}\n"
            f"저장 사유: {', '.join(record.capture_reasons) or '-'}"
        )
        target_row = -1
        previous_blocked = self.candidates.blockSignals(True)
        try:
            self.candidates.setRowCount(len(record.candidates))
            for row, candidate in enumerate(record.candidates):
                for column, (key, _title) in enumerate(_COLUMNS):
                    value = candidate.get(key)
                    if isinstance(value, float):
                        text = f"{value:.4f}"
                    elif key in {"selected", "rejected"}:
                        text = "예" if value else "아니오"
                    else:
                        text = "-" if value in (None, "") else str(value)
                    item = QTableWidgetItem(text)
                    if key == "rank":
                        item.setData(Qt.ItemDataRole.UserRole, row)
                    self.candidates.setItem(row, column, item)
            self.candidates.resizeColumnsToContents()
            if record.candidates:
                target_row = previous_row if 0 <= previous_row < len(record.candidates) else 0
                self.candidates.selectRow(target_row)
        finally:
            self.candidates.blockSignals(previous_blocked)
        if target_row >= 0:
            self._show_candidate(target_row, emit_selection=False)
        else:
            self.candidate_detail.clear()

        state_lines = [
            f"previous state: {_display(record.state.get('previous_state'))}",
            f"proposed state: {_display(record.state.get('proposed_state'))}",
            f"stabilized/final fill state: {_display(record.fill_state)}",
            f"raw oil Y: {_display(record.positions.get('raw_oil_y'))}",
            f"smoothed oil Y: {_display(record.positions.get('smoothed_oil_y'))}",
            f"raw foam Y: {_display(record.positions.get('raw_foam_y'))}",
            f"smoothed foam Y: {_display(record.positions.get('smoothed_foam_y'))}",
            f"oil confidence: {_display(record.confidence.get('oil'))}",
            f"foam confidence: {_display(record.confidence.get('foam'))}",
            f"visibility confidence: {_display(record.confidence.get('visibility'))}",
            f"overall confidence: {_display(record.confidence.get('overall'))}",
            f"glare ratio: {_display(record.state.get('glare_ratio'))}",
            f"foam bottom-connected ratio: {_display(record.state.get('foam_bottom_connected_area_ratio'))}",
            f"effective area: {_display(record.state.get('effective_area'))}",
            f"flags: {', '.join(record.flags) or '-'}",
            f"capture reasons: {', '.join(record.capture_reasons) or '-'}",
        ]
        extra = {
            key: value
            for key, value in record.state.items()
            if key not in {
                "previous_state", "proposed_state", "fill_state", "glare_ratio",
                "foam_bottom_connected_area_ratio", "effective_area",
            }
        }
        if extra:
            state_lines.append("\n추가 debug metrics:\n" + json.dumps(extra, ensure_ascii=False, indent=2))
        if record.warnings:
            state_lines.append("\ntrace warnings:\n" + "\n".join(record.warnings))
        self.state_detail.setPlainText("\n".join(state_lines))
        self.export_button.setEnabled(True)
        self._refresh_artifact_availability()
        self._artifact_changed(self.artifact_combo.currentIndex())

    def set_artifact(self, key: str, image: QImage | None, error: str = "") -> None:
        self._pixmap = QPixmap()
        if image is None or image.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(error or "이 장면에는 선택한 artifact가 저장되지 않았습니다.")
            self.artifact_status.setText(error or "artifact 없음")
            return
        detached = QImage(image).copy()
        self._pixmap = QPixmap.fromImage(detached)
        self.image_label.setText("")
        self.artifact_status.setText(
            f"{_ARTIFACT_LABELS.get(key, key)} · {detached.width()}×{detached.height()} · lazy decode 완료"
        )
        self.fit_image()

    def selected_candidate_index(self) -> int | None:
        row = self.candidates.currentRow()
        return row if row >= 0 else None

    def current_artifact_key(self) -> str:
        return str(self.artifact_combo.currentData() or "")

    def fit_image(self) -> None:
        if self._pixmap.isNull():
            return
        viewport = self.image_scroll.viewport().size()
        width = max(1, viewport.width() - 12)
        height = max(1, viewport.height() - 12)
        ratio = min(width / self._pixmap.width(), height / self._pixmap.height())
        self._set_scale(max(0.05, ratio))

    def _set_scale(self, scale: float) -> None:
        if self._pixmap.isNull():
            return
        self._scale = min(8.0, max(0.05, float(scale)))
        size = self._pixmap.size() * self._scale
        self.image_label.resize(size)
        self.image_label.setPixmap(
            self._pixmap.scaled(size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def _candidate_changed(self, row: int, _column: int, _previous_row: int, _previous_column: int) -> None:
        self._show_candidate(row, emit_selection=True)

    def _show_candidate(self, row: int, *, emit_selection: bool) -> None:
        if self._record is None or row < 0 or row >= len(self._record.candidates):
            self.candidate_detail.clear()
            return
        candidate = self._record.candidates[row]
        lines = [
            f"rank: {_display(candidate.get('rank'))}",
            f"kind: {_display(candidate.get('kind'))}",
            f"source: {_display(candidate.get('source'))}",
            f"canonical Y: {_display(candidate.get('canonical_y'))}",
            f"local Y: {_display(candidate.get('local_y'))}",
            f"selected: {'예' if candidate.get('selected') else '아니오'}",
            f"rejected: {'예' if candidate.get('rejected') else '아니오'}",
            f"reject reason: {_display(candidate.get('reject_reason'))}",
            "\nfeatures:",
        ]
        lines.extend(f"  {key}: {_display(value)}" for key, value in sorted((candidate.get("features") or {}).items()))
        lines.append("\npenalties:")
        lines.extend(f"  {key}: {_display(value)}" for key, value in sorted((candidate.get("penalties") or {}).items()))
        self.candidate_detail.setPlainText("\n".join(lines))
        if emit_selection:
            self.candidateSelected.emit(row)

    def _artifact_changed(self, _index: int) -> None:
        if self._record is not None:
            self.artifactRequested.emit(self.current_artifact_key())

    def _refresh_artifact_availability(self) -> None:
        available = set(self._record.images) if self._record is not None else set()
        for index in range(self.artifact_combo.count()):
            key = str(self.artifact_combo.itemData(index))
            label = _ARTIFACT_LABELS.get(key, key)
            self.artifact_combo.setItemText(index, label if key in available else f"{label} — 없음")


def _display(value) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
