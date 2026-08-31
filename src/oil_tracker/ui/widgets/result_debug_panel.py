from __future__ import annotations

import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.ui.presentation_labels import debug_capture_reason_label, fill_state_label


_ARTIFACTS = (
    ("기본", "overlay", "검출 표시"),
    ("기본", "original_roi", "원본 ROI"),
    ("영역", "ellipse_mask", "타원 마스크"),
    ("영역", "effective_mask", "유효 영역 마스크"),
    ("영역", "exclusion_mask", "제외 영역 마스크"),
    ("영역", "static_artifact_map", "고정 장애물 지도"),
    ("경계", "grayscale", "회색조"),
    ("경계", "normalized", "명암 정규화"),
    ("경계", "blurred", "노이즈 완화"),
    ("경계", "sobel", "Sobel 경계"),
    ("경계", "canny", "Canny 경계"),
    ("경계", "horizontal_mask", "수평 경계 마스크"),
    ("경계", "glare_mask", "반사광 마스크"),
    ("거품", "foam_mask", "공간 성분 마스크"),
    ("거품", "foam_variance", "분산 지도"),
    ("거품", "foam_edge_density", "경계 밀도 지도"),
    ("거품", "foam_whiteness", "백색도 지도"),
    ("거품", "foam_texture_evidence", "질감 근거"),
    ("거품", "foam_glare_excluded_mask", "반사광 제외 마스크"),
    ("거품", "foam_combined_evidence", "통합 근거"),
    ("거품", "foam_accepted_component", "채택 성분"),
)
_ARTIFACT_LABELS = {key: label for _group, key, label in _ARTIFACTS}
_ARTIFACT_GROUPS = {key: group for group, key, _label in _ARTIFACTS}

_COLUMNS = (
    ("rank", "순위"),
    ("kind", "종류"),
    ("canonical_y", "위치 Y"),
    ("final_score", "최종 점수"),
    ("result", "결과"),
)

_CANDIDATE_KIND_LABELS = {
    "oil_air": "유면",
    "foam_front": "거품 경계",
}


class ResultDebugPanel(QWidget):
    candidateSelected = Signal(int)
    artifactRequested = Signal(str)
    exportRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(340)
        self._record = None
        self._pixmap = QPixmap()
        self._scale = 1.0
        self.summary = QLabel("디버그 장면을 선택해 주세요.")
        self.summary.setWordWrap(True)
        self.summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.tabs = QTabWidget()

        summary_page = QWidget()
        summary_layout = QVBoxLayout(summary_page)
        self.state_summary = QTextEdit()
        self.state_summary.setReadOnly(True)
        self.raw_toggle = QToolButton()
        self.raw_toggle.setText("원시 진단값 보기")
        self.raw_toggle.setCheckable(True)
        self.raw_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.state_detail = QTextEdit()
        self.state_detail.setReadOnly(True)
        self.state_detail.setVisible(False)
        summary_layout.addWidget(self.state_summary, 1)
        summary_layout.addWidget(self.raw_toggle)
        summary_layout.addWidget(self.state_detail, 1)
        self.tabs.addTab(summary_page, "판정 요약")

        candidate_page = QWidget()
        candidate_layout = QVBoxLayout(candidate_page)
        self.candidates = QTableWidget()
        self.candidates.setColumnCount(len(_COLUMNS))
        self.candidates.setHorizontalHeaderLabels([title for _key, title in _COLUMNS])
        self.candidates.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.candidates.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.candidates.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self.candidates.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (2, 3, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        self.candidate_detail = QTextEdit()
        self.candidate_detail.setReadOnly(True)
        candidate_split = QSplitter(Qt.Orientation.Vertical)
        candidate_split.addWidget(self.candidates)
        candidate_split.addWidget(self.candidate_detail)
        candidate_split.setSizes([320, 220])
        candidate_layout.addWidget(candidate_split)
        self.tabs.addTab(candidate_page, "후보 비교")

        artifact_page = QWidget()
        artifact_layout = QVBoxLayout(artifact_page)
        self.artifact_combo = QComboBox()
        for group, key, label in _ARTIFACTS:
            self.artifact_combo.addItem(f"{group} · {label}", key)
        artifact_layout.addWidget(self.artifact_combo)
        controls = QHBoxLayout()
        self.fit_button = QPushButton("맞춤")
        self.actual_button = QPushButton("100%")
        self.zoom_out = QPushButton("−")
        self.zoom_in = QPushButton("+")
        controls.addWidget(self.fit_button)
        controls.addWidget(self.actual_button)
        controls.addStretch(1)
        controls.addWidget(self.zoom_out)
        controls.addWidget(self.zoom_in)
        self.artifact_status = QLabel("진단 이미지 없음")
        self.artifact_status.setWordWrap(True)
        self.image_label = QLabel("진단 이미지를 선택해 주세요.")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(280, 220)
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(False)
        self.image_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_scroll.setWidget(self.image_label)
        artifact_layout.addLayout(controls)
        artifact_layout.addWidget(self.artifact_status)
        artifact_layout.addWidget(self.image_scroll, 1)
        self.tabs.addTab(artifact_page, "진단 이미지")

        self.export_button = QPushButton("재현 패키지 내보내기")
        layout = QVBoxLayout(self)
        layout.addWidget(self.summary)
        layout.addWidget(self.tabs, 1)
        layout.addWidget(self.export_button)

        self.candidates.currentCellChanged.connect(self._candidate_changed)
        self.artifact_combo.currentIndexChanged.connect(self._artifact_changed)
        self.raw_toggle.toggled.connect(self._raw_visibility_changed)
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
        self.state_summary.clear()
        self.state_detail.clear()
        self.raw_toggle.setChecked(False)
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("진단 이미지를 선택해 주세요.")
        self.artifact_status.setText("진단 이미지 없음")
        self.export_button.setEnabled(False)

    def set_record(self, record, actual_timestamp: float | None = None) -> None:
        previous_row = self.candidates.currentRow() if self._record is record else -1
        self._record = record
        delta_text = ""
        if actual_timestamp is not None:
            delta = float(actual_timestamp) - float(record.timestamp_sec)
            delta_text = f" · decoded 차이 {delta:+.3f}초"
        reasons = ", ".join(
            debug_capture_reason_label(reason) for reason in record.capture_reasons
        )
        self.summary.setText(
            f"{record.glass_name or record.glass_id} · {record.timestamp_sec:.3f}초 · "
            f"장면 {record.frame_index}{delta_text}\n기록 이유: {reasons or '정기 기록'}"
        )
        target_row = -1
        previous_blocked = self.candidates.blockSignals(True)
        try:
            self.candidates.setRowCount(len(record.candidates))
            for row, candidate in enumerate(record.candidates):
                values = {
                    "rank": candidate.get("rank"),
                    "kind": _candidate_kind(candidate.get("kind")),
                    "canonical_y": candidate.get("canonical_y"),
                    "final_score": candidate.get("final_score"),
                    "result": _candidate_result(candidate),
                }
                for column, (key, _title) in enumerate(_COLUMNS):
                    value = values[key]
                    text = f"{value:.4f}" if isinstance(value, float) else _display(value)
                    item = QTableWidgetItem(text)
                    if key == "rank":
                        item.setData(Qt.ItemDataRole.UserRole, row)
                    self.candidates.setItem(row, column, item)
            if record.candidates:
                target_row = previous_row if 0 <= previous_row < len(record.candidates) else 0
                self.candidates.selectRow(target_row)
        finally:
            self.candidates.blockSignals(previous_blocked)
        if target_row >= 0:
            self._show_candidate(target_row, emit_selection=False)
        else:
            self.candidate_detail.clear()

        self.state_summary.setPlainText(_state_summary_text(record))
        self.state_detail.setPlainText(_raw_state_text(record))
        self.export_button.setEnabled(True)
        self._refresh_artifact_availability()
        self._artifact_changed(self.artifact_combo.currentIndex())

    def set_artifact(self, key: str, image: QImage | None, error: str = "") -> None:
        self._pixmap = QPixmap()
        if image is None or image.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(error or "이 장면에는 선택한 진단 이미지가 저장되지 않았습니다.")
            self.artifact_status.setText(error or "진단 이미지 없음")
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
            self._pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _candidate_changed(
        self,
        row: int,
        _column: int,
        _previous_row: int,
        _previous_column: int,
    ) -> None:
        self._show_candidate(row, emit_selection=True)

    def _show_candidate(self, row: int, *, emit_selection: bool) -> None:
        if self._record is None or row < 0 or row >= len(self._record.candidates):
            self.candidate_detail.clear()
            return
        candidate = self._record.candidates[row]
        lines = [
            f"최종 점수: {_display(candidate.get('final_score'))}",
            f"결과: {_candidate_result(candidate)}",
            f"탈락 사유: {_display(candidate.get('reject_reason'))}",
            "",
            f"특징 점수 합계: {_display(candidate.get('feature_score'))}",
        ]
        lines.extend(
            f"  {key}: {_display(value)}"
            for key, value in sorted((candidate.get("features") or {}).items())
        )
        lines.append("")
        lines.append(f"감점 합계: {_display(candidate.get('total_penalty'))}")
        lines.extend(
            f"  {key}: {_display(value)}"
            for key, value in sorted((candidate.get("penalties") or {}).items())
        )
        self.candidate_detail.setPlainText("\n".join(lines))
        if emit_selection:
            self.candidateSelected.emit(row)

    def _artifact_changed(self, _index: int) -> None:
        if self._record is not None:
            self.artifactRequested.emit(self.current_artifact_key())

    def _raw_visibility_changed(self, checked: bool) -> None:
        self.raw_toggle.setArrowType(
            Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
        )
        self.state_detail.setVisible(checked)

    def _refresh_artifact_availability(self) -> None:
        available = set(self._record.images) if self._record is not None else set()
        for index in range(self.artifact_combo.count()):
            key = str(self.artifact_combo.itemData(index))
            label = f"{_ARTIFACT_GROUPS.get(key, '기타')} · {_ARTIFACT_LABELS.get(key, key)}"
            self.artifact_combo.setItemText(
                index,
                label if key in available else f"{label} — 없음",
            )


def _state_summary_text(record) -> str:
    previous = fill_state_label(record.state.get("previous_state"))
    proposed = fill_state_label(record.state.get("proposed_state"))
    final = fill_state_label(record.fill_state)
    oil_position = _position_transition(
        record.positions.get("raw_oil_y"),
        record.positions.get("smoothed_oil_y"),
    )
    foam_position = _position_transition(
        record.positions.get("raw_foam_y"),
        record.positions.get("smoothed_foam_y"),
    )
    confidence = record.confidence
    lines = [
        "상태 판정",
        f"  이전: {previous}",
        f"  제안: {proposed}",
        f"  최종: {final}",
        "",
        "관측 위치",
        f"  유면: {oil_position}",
        f"  거품: {foam_position}",
        "",
        "신뢰도",
        f"  유면 {_display(confidence.get('oil'))} · 거품 {_display(confidence.get('foam'))}",
        f"  가시성 {_display(confidence.get('visibility'))} · 전체 {_display(confidence.get('overall'))}",
    ]
    if record.warnings:
        lines.extend(("", f"기록 경고 {len(record.warnings)}개", "  원시 진단값에서 확인"))
    return "\n".join(lines)


def _raw_state_text(record) -> str:
    payload = {
        "positions": getattr(record, "positions", {}),
        "confidence": getattr(record, "confidence", {}),
        "state": getattr(record, "state", {}),
        "flags": getattr(record, "flags", ()),
        "capture_reasons": getattr(record, "capture_reasons", ()),
        "profiles": getattr(record, "profiles", {}),
        "warnings": getattr(record, "warnings", ()),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def _candidate_kind(value) -> str:
    return _CANDIDATE_KIND_LABELS.get(str(value), _display(value))


def _position_transition(raw, smoothed) -> str:
    if raw is None and smoothed is None:
        return "관측값 없음"
    if raw is None:
        return f"{_display(smoothed)} px"
    if smoothed is None or smoothed == raw:
        return f"{_display(raw)} px"
    return f"{_display(raw)} → {_display(smoothed)} px"


def _candidate_result(candidate) -> str:
    if candidate.get("selected"):
        return "선택됨"
    if candidate.get("rejected"):
        return "탈락"
    return "후보"


def _display(value) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)
