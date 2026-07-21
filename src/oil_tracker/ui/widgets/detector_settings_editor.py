from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.application.services.detector_settings import (
    clone_detector_settings,
    compare_detector_settings,
    detector_setting_fields,
    update_detector_setting,
    validate_detector_settings,
)


_FIELD_LABELS = {
    "canny_low": "Canny 하한",
    "canny_high": "Canny 상한",
    "hough_threshold": "Hough threshold",
    "hough_min_line_length_ratio": "Hough 최소 선 길이 비율",
    "hough_max_line_gap": "Hough 최대 선 간격",
    "hough_max_angle_deg": "Hough 최대 각도",
    "minimum_horizontal_coverage": "최소 수평 coverage",
    "minimum_region_contrast": "최소 영역 contrast",
    "minimum_final_confidence": "최소 최종 confidence",
    "temporal_max_jump_px": "Temporal 최대 jump (px)",
    "smoothing_window": "Smoothing window",
    "glare_threshold": "Glare 밝기 threshold",
    "glare_ratio_unknown": "Glare unknown 비율",
    "foam_variance_threshold": "Foam variance 기준",
    "foam_edge_density_threshold": "Foam edge density 기준",
    "foam_min_area_ratio": "Foam 최소 면적 비율",
    "foam_lightness_threshold": "Foam lightness 하한",
    "foam_max_chroma": "Foam 최대 chroma",
    "foam_min_whiteness_ratio": "Foam 최소 백색도 비율",
    "foam_max_glare_overlap_ratio": "Foam 최대 glare 중첩",
    "foam_min_evidence_score": "Foam 최소 evidence score",
    "foam_strong_evidence_score": "Foam strong evidence score",
    "foam_persistence_frames": "Foam persistence sample",
    "foam_max_front_jump_px": "Foam front 최대 jump (px)",
    "state_hold_frames": "State hold sample",
    "candidate_top_k": "Candidate top K",
    "oil_consensus_tolerance_px": "Oil consensus Y 허용 거리 (px)",
    "oil_min_consensus_sources": "Oil 최소 consensus source",
    "oil_min_polarity_score": "Oil 최소 polarity evidence",
    "oil_no_interface_min_score": "Oil no-interface 최소 score",
    "oil_path_window": "Oil path window",
    "oil_path_beam_width": "Oil path beam width",
    "oil_path_min_margin": "Oil path 최소 margin",
    "oil_tracker_update_confidence": "Oil tracker 갱신 confidence",
    "oil_reacquire_frames": "Oil reacquire sample",
    "weight_edge": "가중치 · edge",
    "weight_coverage": "가중치 · coverage",
    "weight_region": "가중치 · region",
    "weight_gradient_direction": "가중치 · gradient direction",
    "weight_temporal": "가중치 · temporal",
    "weight_state": "가중치 · state",
    "penalty_glare": "Penalty · glare",
    "penalty_border": "Penalty · border",
    "penalty_exclusion": "Penalty · exclusion",
    "penalty_static": "Penalty · static artifact",
    "penalty_jump": "Penalty · jump",
}

_CATEGORY_LABELS = {
    "edge": "Edge",
    "hough": "Hough",
    "candidate": "Candidate",
    "confidence": "Confidence",
    "temporal": "Temporal",
    "artifact": "Artifact",
    "foam": "Foam",
    "oil_path": "Oil boundary path",
    "score_weight": "Score weight",
    "penalty": "Penalty",
}


class DetectorSettingsEditor(QWidget):
    settingsChanged = Signal(object, bool, int)
    validationChanged = Signal(bool, object)

    def __init__(self, baseline_settings, parent=None) -> None:
        super().__init__(parent)
        self._baseline = clone_detector_settings(baseline_settings)
        self._temporary = clone_detector_settings(baseline_settings)
        self._editors = {}
        self._rows = {}
        self._updating = False

        self.search = QLineEdit()
        self.search.setPlaceholderText("설정 이름 또는 category 검색")
        self.changed_count = QLabel("변경 0개")
        self.validation_label = QLabel("설정이 유효합니다.")
        self.validation_label.setWordWrap(True)
        self.reset_selected = QPushButton("선택 field 기준값 복원")
        self.reset_all = QPushButton("기준 설정으로 전체 초기화")

        top = QHBoxLayout()
        top.addWidget(QLabel("검색"))
        top.addWidget(self.search, 1)
        top.addWidget(self.changed_count)
        top.addWidget(self.reset_selected)
        top.addWidget(self.reset_all)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Category", "설정", "Machine field", "기준값", "임시값", "Delta", "상태"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(420)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.validation_label)
        layout.addWidget(self.table, 1)

        self.search.textChanged.connect(self._apply_filter)
        self.reset_selected.clicked.connect(self.reset_selected_field)
        self.reset_all.clicked.connect(self.reset_to_baseline)
        self._build_rows()
        self._refresh_state(emit=False)

    @property
    def baseline_settings(self):
        return clone_detector_settings(self._baseline)

    def temporary_settings(self):
        return clone_detector_settings(self._temporary)

    def set_baseline(self, baseline_settings) -> None:
        self._baseline = clone_detector_settings(baseline_settings)
        self._temporary = clone_detector_settings(baseline_settings)
        self._sync_editors()
        self._refresh_state()

    def reset_to_baseline(self) -> None:
        self._temporary = clone_detector_settings(self._baseline)
        self._sync_editors()
        self._refresh_state()

    def reset_selected_field(self) -> None:
        row = self.table.currentRow()
        field_name = self.table.item(row, 2).text() if row >= 0 and self.table.item(row, 2) else ""
        if not field_name:
            return
        self._temporary = update_detector_setting(
            self._temporary,
            field_name,
            getattr(self._baseline, field_name),
        )
        self._sync_editor(field_name)
        self._refresh_state()

    def changed_field_names(self) -> tuple[str, ...]:
        return tuple(
            diff.field_name
            for diff in compare_detector_settings(self._baseline, self._temporary)
            if diff.changed
        )

    def validation_errors(self) -> dict[str, str]:
        return validate_detector_settings(self._temporary)

    def _build_rows(self) -> None:
        specs = detector_setting_fields()
        self.table.setRowCount(len(specs))
        for row, spec in enumerate(specs):
            self._rows[spec.name] = row
            category = QTableWidgetItem(_CATEGORY_LABELS.get(spec.category, spec.category))
            label = QTableWidgetItem(_FIELD_LABELS.get(spec.name, spec.name))
            machine = QTableWidgetItem(spec.name)
            baseline = QTableWidgetItem(_format_value(getattr(self._baseline, spec.name), spec.decimals))
            delta = QTableWidgetItem("-")
            status = QTableWidgetItem("동일")
            for item in (category, label, machine, baseline, delta, status):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setToolTip(spec.description)
            self.table.setItem(row, 0, category)
            self.table.setItem(row, 1, label)
            self.table.setItem(row, 2, machine)
            self.table.setItem(row, 3, baseline)
            editor = self._make_editor(spec)
            self._editors[spec.name] = editor
            self.table.setCellWidget(row, 4, editor)
            self.table.setItem(row, 5, delta)
            self.table.setItem(row, 6, status)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(1, max(220, self.table.columnWidth(1)))
        self.table.setColumnWidth(2, max(220, self.table.columnWidth(2)))
        self.table.horizontalHeader().setStretchLastSection(True)

    def _make_editor(self, spec):
        if spec.value_type is int:
            editor = QSpinBox()
            editor.setRange(int(spec.minimum), int(spec.maximum))
            editor.setSingleStep(int(spec.step))
            editor.setValue(int(getattr(self._temporary, spec.name)))
            editor.valueChanged.connect(
                lambda value, field_name=spec.name: self._editor_changed(field_name, value)
            )
        else:
            editor = QDoubleSpinBox()
            editor.setDecimals(spec.decimals)
            editor.setRange(float(spec.minimum), float(spec.maximum))
            editor.setSingleStep(float(spec.step))
            editor.setValue(float(getattr(self._temporary, spec.name)))
            editor.valueChanged.connect(
                lambda value, field_name=spec.name: self._editor_changed(field_name, value)
            )
        editor.setKeyboardTracking(False)
        editor.setToolTip(spec.description)
        editor.setMinimumWidth(150)
        return editor

    def _editor_changed(self, field_name: str, value) -> None:
        if self._updating:
            return
        self._temporary = update_detector_setting(self._temporary, field_name, value)
        self._refresh_state()

    def _sync_editors(self) -> None:
        self._updating = True
        try:
            for field_name in self._editors:
                self._sync_editor(field_name)
        finally:
            self._updating = False

    def _sync_editor(self, field_name: str) -> None:
        editor = self._editors[field_name]
        blocked = editor.blockSignals(True)
        editor.setValue(getattr(self._temporary, field_name))
        editor.blockSignals(blocked)

    def _refresh_state(self, *, emit: bool = True) -> None:
        diffs = compare_detector_settings(self._baseline, self._temporary)
        errors = validate_detector_settings(self._temporary)
        changed = 0
        for diff in diffs:
            row = self._rows[diff.field_name]
            spec = next(item for item in detector_setting_fields() if item.name == diff.field_name)
            self.table.item(row, 3).setText(_format_value(diff.baseline_value, spec.decimals))
            self.table.item(row, 5).setText(
                "-" if diff.numeric_delta is None else f"{diff.numeric_delta:+.{spec.decimals}f}"
            )
            if diff.field_name in errors:
                status = f"오류 · {errors[diff.field_name]}"
            elif diff.changed:
                status = "변경됨"
                changed += 1
            else:
                status = "동일"
            self.table.item(row, 6).setText(status)
            self.table.item(row, 6).setToolTip(status)
        self.changed_count.setText(f"변경 {changed}개")
        if errors:
            self.validation_label.setText(
                "재검출을 실행할 수 없습니다. "
                + " / ".join(
                    f"{_FIELD_LABELS.get(name, name)}: {message}"
                    for name, message in errors.items()
                )
            )
        else:
            self.validation_label.setText("설정이 유효합니다.")
        self.reset_selected.setEnabled(self.table.currentRow() >= 0)
        if emit:
            self.settingsChanged.emit(self.temporary_settings(), not errors, changed)
            self.validationChanged.emit(not errors, dict(errors))

    def _apply_filter(self, text: str) -> None:
        needle = text.strip().casefold()
        for field_name, row in self._rows.items():
            spec = next(item for item in detector_setting_fields() if item.name == field_name)
            haystack = " ".join(
                (
                    field_name,
                    _FIELD_LABELS.get(field_name, field_name),
                    spec.category,
                    _CATEGORY_LABELS.get(spec.category, spec.category),
                    spec.description,
                )
            ).casefold()
            self.table.setRowHidden(row, bool(needle and needle not in haystack))


def _format_value(value, decimals: int) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.{decimals}f}"
