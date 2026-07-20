from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.domain.redetection import RedetectionMode, RedetectionStatus
from oil_tracker.ui.presentation_labels import fill_state_label, result_state_label
from oil_tracker.ui.widgets.detector_settings_editor import DetectorSettingsEditor
from oil_tracker.ui.widgets.redetection_comparison_graph import RedetectionComparisonGraph
from oil_tracker.ui.widgets.redetection_debug_comparison import RedetectionDebugComparison


class RedetectionComparisonWindow(QMainWindow):
    runRequested = Signal()
    cancelRequested = Signal()
    currentTimestampRequested = Signal()
    comparisonSelected = Signal(int, float)
    applyCurrentRequested = Signal()
    applyAllRequested = Signal()
    saveSelectedRequested = Signal()
    saveAllRequested = Signal()
    contextEdited = Signal(str)

    def __init__(self, baseline_settings, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowTitle("부분 재검출과 설정 비교")
        self.resize(1480, 920)
        self._result = None
        self._glass = None
        self._running = False
        self._settings_valid = True
        self._source_available = False
        self._apply_compatible = False

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        context_box = QGroupBox("재검출 범위")
        context = QFormLayout(context_box)
        self.bundle_label = QLabel("-")
        self.glass_label = QLabel("-")
        self.source_label = QLabel("-")
        self.source_label.setWordWrap(True)
        self.target_label = QLabel("0.000 초")
        self.mode = QComboBox()
        self.mode.addItem("현재 장면 — 독립 검출", RedetectionMode.CURRENT.value)
        self.mode.addItem("앞뒤 짧은 구간", RedetectionMode.SHORT.value)
        self.mode.addItem("선택 관찰창 전체 구간", RedetectionMode.FULL.value)
        self.before = _seconds_spin(2.0)
        self.after = _seconds_spin(2.0)
        range_row = QWidget()
        range_layout = QHBoxLayout(range_row)
        range_layout.setContentsMargins(0, 0, 0, 0)
        range_layout.addWidget(QLabel("앞"))
        range_layout.addWidget(self.before)
        range_layout.addWidget(QLabel("초 · 뒤"))
        range_layout.addWidget(self.after)
        range_layout.addWidget(QLabel("초 (전체 최대 30초)"))
        self.use_current = QPushButton("현재 시각 사용")
        target_row = QWidget()
        target_layout = QHBoxLayout(target_row)
        target_layout.setContentsMargins(0, 0, 0, 0)
        target_layout.addWidget(self.target_label, 1)
        target_layout.addWidget(self.use_current)
        context.addRow("결과 bundle", self.bundle_label)
        context.addRow("관찰창", self.glass_label)
        context.addRow("원본 영상", self.source_label)
        context.addRow("Target", target_row)
        context.addRow("Mode", self.mode)
        context.addRow("Short range", range_row)

        controls = QHBoxLayout()
        self.changed_label = QLabel("변경 0개")
        self.run_button = QPushButton("재검출 실행")
        self.rerun_button = QPushButton("같은 조건으로 다시 실행")
        self.cancel_button = QPushButton("취소")
        self.cancel_button.setEnabled(False)
        controls.addWidget(self.changed_label)
        controls.addStretch(1)
        controls.addWidget(self.run_button)
        controls.addWidget(self.rerun_button)
        controls.addWidget(self.cancel_button)
        self.state_label = QLabel("실행 전")
        self.state_label.setWordWrap(True)
        self.limitation_label = QLabel()
        self.limitation_label.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)

        self.settings_editor = DetectorSettingsEditor(baseline_settings)
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setWidget(self.settings_editor)

        self.tabs = QTabWidget()
        self.summary_table = _table(
            ("항목", "공식 결과", "재검출 결과", "Delta / 일치")
        )
        self.summary_tab = _page(self.summary_table)
        self.tabs.addTab(self.summary_tab, "요약")

        self.tracking_graph = RedetectionComparisonGraph()
        self.tracking_table = _table(
            (
                "Nominal",
                "공식 시각",
                "재검출 decoded",
                "공식 oil",
                "재검출 oil",
                "oil Δ",
                "공식 foam",
                "재검출 foam",
                "foam Δ",
                "confidence Δ",
                "상태",
                "valid",
                "match",
            )
        )
        tracking_split = QSplitter(Qt.Orientation.Vertical)
        tracking_split.addWidget(self.tracking_graph)
        tracking_split.addWidget(self.tracking_table)
        tracking_split.setSizes([360, 420])
        self.tabs.addTab(_page(tracking_split), "Tracking 비교")

        self.candidate_compare = RedetectionDebugComparison(artifact_only=False)
        self.tabs.addTab(self.candidate_compare, "후보와 점수")
        self.artifact_compare = RedetectionDebugComparison(artifact_only=True)
        self.tabs.addTab(self.artifact_compare, "Artifact 비교")

        self.event_table = _table(
            ("Event", "공식 시각", "재검출 시각", "상태", "Δ초")
        )
        self.judgment_label = QLabel("현재 장면 mode에는 event·판정 비교가 적용되지 않습니다.")
        self.judgment_label.setWordWrap(True)
        event_page = QWidget()
        event_layout = QVBoxLayout(event_page)
        event_layout.addWidget(self.judgment_label)
        event_layout.addWidget(self.event_table, 1)
        self.tabs.addTab(event_page, "Event·판정 비교")

        self.compatibility_label = QLabel("Workbench compatibility를 확인 중입니다.")
        self.compatibility_label.setWordWrap(True)
        self.apply_status = QLabel()
        self.apply_status.setWordWrap(True)
        self.apply_current = QPushButton("현재 Workbench의 선택 관찰창에 적용")
        self.apply_all = QPushButton("현재 Workbench의 모든 관찰창에 적용")
        self.save_selected = QPushButton("선택 관찰창 적용 새 profile 저장")
        self.save_all = QPushButton("모든 관찰창 적용 새 profile 저장")
        apply_page = QWidget()
        apply_layout = QVBoxLayout(apply_page)
        apply_layout.addWidget(self.compatibility_label)
        apply_layout.addWidget(self.apply_status)
        apply_layout.addWidget(self.apply_current)
        apply_layout.addWidget(self.apply_all)
        apply_layout.addSpacing(16)
        apply_layout.addWidget(QLabel("현재 Workbench를 교체하지 않고 결과 snapshot 기반 새 .oilrecipe를 저장합니다."))
        apply_layout.addWidget(self.save_selected)
        apply_layout.addWidget(self.save_all)
        apply_layout.addStretch(1)
        self.tabs.addTab(apply_page, "설정 적용")

        main_split = QSplitter(Qt.Orientation.Horizontal)
        main_split.addWidget(settings_scroll)
        main_split.addWidget(self.tabs)
        main_split.setSizes([600, 880])

        root.addWidget(context_box)
        root.addLayout(controls)
        root.addWidget(self.state_label)
        root.addWidget(self.limitation_label)
        root.addWidget(self.progress)
        root.addWidget(main_split, 1)

        self.run_button.clicked.connect(self.runRequested)
        self.rerun_button.clicked.connect(self.runRequested)
        self.cancel_button.clicked.connect(self.cancelRequested)
        self.use_current.clicked.connect(self.currentTimestampRequested)
        self.mode.currentIndexChanged.connect(self._mode_changed)
        self.before.valueChanged.connect(lambda _value: self.contextEdited.emit("range"))
        self.after.valueChanged.connect(lambda _value: self.contextEdited.emit("range"))
        self.settings_editor.settingsChanged.connect(self._settings_changed)
        self.tracking_table.currentCellChanged.connect(self._tracking_selected)
        self.tracking_graph.comparisonSelected.connect(self._graph_selected)
        self.apply_current.clicked.connect(self.applyCurrentRequested)
        self.apply_all.clicked.connect(self.applyAllRequested)
        self.save_selected.clicked.connect(self.saveSelectedRequested)
        self.save_all.clicked.connect(self.saveAllRequested)
        self.set_status(RedetectionStatus.IDLE, "실행 전")
        self._mode_changed()

    def current_mode(self) -> RedetectionMode:
        return RedetectionMode(str(self.mode.currentData()))

    def short_before_sec(self) -> float:
        return float(self.before.value())

    def short_after_sec(self) -> float:
        return float(self.after.value())

    def temporary_settings(self):
        return self.settings_editor.temporary_settings()

    def set_context(self, bundle, glass, source_path: str, target_timestamp: float) -> None:
        self._glass = glass
        self.bundle_label.setText(f"{bundle.root.name} · run {bundle.run_id}")
        self.glass_label.setText(f"{glass.name} · {glass.id}")
        self.source_label.setText(source_path or "원본 영상 없음 — Viewer에서 원본 영상 다시 지정 필요")
        self._source_available = bool(source_path)
        self.target_label.setText(f"{target_timestamp:.3f} 초")
        self._refresh_run_enabled()

    def set_target(self, timestamp: float) -> None:
        self.target_label.setText(f"{timestamp:.3f} 초")

    def set_baseline_settings(self, settings) -> None:
        self.settings_editor.set_baseline(settings)

    def set_status(self, status: RedetectionStatus, message: str) -> None:
        self.state_label.setText(message)
        self._running = status is RedetectionStatus.RUNNING
        self.run_button.setEnabled(not self._running)
        self.rerun_button.setEnabled(not self._running and self._result is not None)
        self.cancel_button.setEnabled(self._running)
        self._refresh_run_enabled()

    def set_progress(self, update) -> None:
        self.progress.setValue(int(round(update.fraction * 1000)))
        timestamp = "" if update.current_timestamp_sec is None else f" · {update.current_timestamp_sec:.3f}초"
        self.state_label.setText(
            f"{update.message or update.stage} · {update.processed_samples}/{update.total_samples}{timestamp}"
        )

    def set_result(self, result, glass) -> None:
        self._result = result
        self._glass = glass
        self.progress.setValue(1000)
        self.limitation_label.setText(result.limitation_message)
        self._populate_summary(result)
        self._populate_tracking(result)
        self._populate_events(result)
        self.tracking_graph.set_result(result, glass)
        self.rerun_button.setEnabled(True)
        if result.comparisons:
            self.tracking_table.selectRow(0)

    def clear_result(self, message: str) -> None:
        self._result = None
        self.summary_table.setRowCount(0)
        self.tracking_table.setRowCount(0)
        self.event_table.setRowCount(0)
        self.tracking_graph.clear(message)
        self.candidate_compare.clear(message)
        self.artifact_compare.clear(message)
        self.limitation_label.setText(message)
        self.rerun_button.setEnabled(False)

    def set_debug_records(self, official_record, rerun_record, official_message: str = "") -> None:
        self.candidate_compare.set_records(
            official_record,
            rerun_record,
            official_message=official_message,
        )
        self.artifact_compare.set_records(
            official_record,
            rerun_record,
            official_message=official_message,
        )

    def set_apply_compatibility(self, compatible: bool, reasons=()) -> None:
        self._apply_compatible = bool(compatible)
        self.compatibility_label.setText(
            "현재 Workbench에 적용할 수 있습니다."
            if compatible
            else "현재 Workbench에 적용할 수 없습니다.\n" + "\n".join(f"• {reason}" for reason in reasons)
        )
        self._refresh_apply_enabled()

    def set_apply_status(self, message: str) -> None:
        self.apply_status.setText(message)

    def selected_comparison_index(self) -> int:
        return self.tracking_table.currentRow()

    def _settings_changed(self, _settings, valid: bool, changed_count: int) -> None:
        self._settings_valid = bool(valid)
        self.changed_label.setText(f"변경 {changed_count}개")
        self.contextEdited.emit("settings")
        self._refresh_run_enabled()
        self._refresh_apply_enabled()

    def _refresh_run_enabled(self) -> None:
        allowed = not self._running and self._settings_valid and self._source_available
        self.run_button.setEnabled(allowed)
        self.rerun_button.setEnabled(allowed and self._result is not None)

    def _refresh_apply_enabled(self) -> None:
        enabled = self._settings_valid and self._apply_compatible
        self.apply_current.setEnabled(enabled)
        self.apply_all.setEnabled(enabled)
        self.save_selected.setEnabled(self._settings_valid)
        self.save_all.setEnabled(self._settings_valid)

    def _mode_changed(self, _index: int = -1) -> None:
        short = self.current_mode() is RedetectionMode.SHORT
        self.before.setEnabled(short)
        self.after.setEnabled(short)
        self.contextEdited.emit("mode")

    def _tracking_selected(self, row: int, _column: int, _previous_row: int, _previous_column: int) -> None:
        if self._result is None or row < 0 or row >= len(self._result.comparisons):
            return
        point = self._result.comparisons[row]
        timestamp = point.rerun_actual_timestamp_sec
        if timestamp is None:
            timestamp = point.official_timestamp_sec
        if timestamp is None:
            timestamp = point.nominal_timestamp_sec
        self.tracking_graph.select_index(row)
        self.comparisonSelected.emit(row, float(timestamp))

    def _graph_selected(self, row: int, timestamp: float) -> None:
        self.tracking_table.selectRow(row)
        self.comparisonSelected.emit(row, timestamp)

    def _populate_summary(self, result) -> None:
        point = result.comparisons[0] if result.comparisons else None
        rows = []
        if point is not None:
            official = point.official_sample
            rerun = point.rerun_sample.tracking_sample if point.rerun_sample else None
            rows.extend(
                (
                    ("timestamp", _num(point.official_timestamp_sec), _num(point.rerun_actual_timestamp_sec), _delta_time(point)),
                    ("frame index", _attr(official, "frame_index"), _attr(rerun, "frame_index"), _same(_attr(official, "frame_index"), _attr(rerun, "frame_index"))),
                    ("fill state", _state(official), _state(rerun), _bool_same(point.fill_state_same)),
                    ("raw oil Y", _attr_num(official, "raw_oil_air_level_y"), _attr_num(rerun, "raw_oil_air_level_y"), "-"),
                    ("smoothed oil px", _attr_num(official, "smoothed_oil_air_level_px_from_zero"), _attr_num(rerun, "smoothed_oil_air_level_px_from_zero"), _num(point.oil_position_delta_px)),
                    ("smoothed oil mm", _attr_num(official, "smoothed_oil_air_level_mm_from_zero"), _attr_num(rerun, "smoothed_oil_air_level_mm_from_zero"), _num(point.oil_position_delta_mm)),
                    ("raw foam Y", _attr_num(official, "raw_foam_front_y"), _attr_num(rerun, "raw_foam_front_y"), "-"),
                    ("smoothed foam px", _attr_num(official, "smoothed_foam_front_px_from_zero"), _attr_num(rerun, "smoothed_foam_front_px_from_zero"), _num(point.foam_position_delta_px)),
                    ("smoothed foam mm", _attr_num(official, "smoothed_foam_front_mm_from_zero"), _attr_num(rerun, "smoothed_foam_front_mm_from_zero"), _num(point.foam_position_delta_mm)),
                    ("confidence", _attr_num(official, "overall_confidence"), _attr_num(rerun, "overall_confidence"), _num(point.confidence_delta)),
                    ("valid", _valid(official), _valid(rerun), _bool_same(point.validity_same)),
                    ("flags", _flags(official), _flags(rerun), f"추가: {', '.join(point.flags_added) or '-'} / 제거: {', '.join(point.flags_removed) or '-'}"),
                    ("selected candidate", "debug trace 참조", _candidate(point), "candidate 비교 가능" if point.candidate_comparison_available else "공식 candidate baseline 없음"),
                )
            )
        summary = result.summary
        rows.extend(
            (
                ("비교 sample", str(summary.comparison_sample_count), str(summary.matched_count), f"official-only {summary.official_only_count}, rerun-only {summary.rerun_only_count}"),
                ("oil |Δ| 평균/최대 px", "-", "-", f"{_num(summary.oil_mean_absolute_delta_px)} / {_num(summary.oil_max_absolute_delta_px)}"),
                ("foam |Δ| 평균/최대 px", "-", "-", f"{_num(summary.foam_mean_absolute_delta_px)} / {_num(summary.foam_max_absolute_delta_px)}"),
                ("상태/valid 변경", "-", "-", f"{summary.fill_state_change_count} / {summary.validity_change_count}"),
            )
        )
        _set_rows(self.summary_table, rows)

    def _populate_tracking(self, result) -> None:
        rows = []
        for point in result.comparisons:
            official = point.official_sample
            rerun = point.rerun_sample.tracking_sample if point.rerun_sample else None
            rows.append(
                (
                    _num(point.nominal_timestamp_sec),
                    _num(point.official_timestamp_sec),
                    _num(point.rerun_actual_timestamp_sec),
                    _attr_num(official, "smoothed_oil_air_level_px_from_zero"),
                    _attr_num(rerun, "smoothed_oil_air_level_px_from_zero"),
                    _num(point.oil_position_delta_px),
                    _attr_num(official, "smoothed_foam_front_px_from_zero"),
                    _attr_num(rerun, "smoothed_foam_front_px_from_zero"),
                    _num(point.foam_position_delta_px),
                    _num(point.confidence_delta),
                    _bool_same(point.fill_state_same),
                    _bool_same(point.validity_same),
                    point.match_status,
                )
            )
        _set_rows(self.tracking_table, rows)

    def _populate_events(self, result) -> None:
        rows = []
        for item in result.event_comparisons:
            rows.append(
                (
                    item.event_type.value,
                    _num(item.official_event.start_time_sec if item.official_event else None),
                    _num(item.rerun_event.start_time_sec if item.rerun_event else None),
                    item.status,
                    _num(item.timestamp_delta_sec),
                )
            )
        _set_rows(self.event_table, rows)
        summary = result.summary
        if result.request.mode is RedetectionMode.CURRENT:
            text = "현재 장면 mode에는 event·판정 비교가 적용되지 않습니다."
        elif result.request.mode is RedetectionMode.SHORT:
            text = result.rerun_judgment_note
        else:
            text = (
                f"공식 판정: {result_state_label(summary.official_judgment) if summary.official_judgment else '-'} · "
                f"재검출 판정: {result_state_label(summary.rerun_judgment) if summary.rerun_judgment else '-'} · "
                f"valid coverage: {_num(result.rerun_valid_coverage_ratio)}\n"
                f"재검출 note: {result.rerun_judgment_note or '-'}"
            )
        self.judgment_label.setText(text)


def _seconds_spin(value: float) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(0.0, 30.0)
    spin.setDecimals(2)
    spin.setSingleStep(0.5)
    spin.setSuffix(" s")
    spin.setValue(value)
    return spin


def _table(headers) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(list(headers))
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    return table


def _page(widget) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.addWidget(widget)
    return page


def _set_rows(table: QTableWidget, rows) -> None:
    table.setRowCount(len(rows))
    for row, values in enumerate(rows):
        for column, value in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(str(value)))
    table.resizeColumnsToContents()


def _num(value) -> str:
    return "-" if value is None else f"{float(value):.4f}"


def _attr(value, name: str):
    return "-" if value is None else str(getattr(value, name, "-"))


def _attr_num(value, name: str) -> str:
    return _num(None if value is None else getattr(value, name, None))


def _state(value) -> str:
    return "-" if value is None else fill_state_label(value.fill_state)


def _valid(value) -> str:
    if value is None:
        return "-"
    return "유효" if value.is_valid else "확인 필요"


def _flags(value) -> str:
    return "-" if value is None or not value.flags else ", ".join(value.flags)


def _candidate(point) -> str:
    candidate = point.rerun_sample.selected_candidate if point.rerun_sample else None
    if candidate is None:
        return "-"
    return f"#{candidate.rank} {candidate.source} Y={_num(candidate.canonical_y)} score={candidate.final_score:.4f}"


def _same(left, right) -> str:
    return "일치" if left == right else "변경"


def _bool_same(value) -> str:
    return "비교 없음" if value is None else "일치" if value else "변경"


def _delta_time(point) -> str:
    if point.official_timestamp_sec is None or point.rerun_actual_timestamp_sec is None:
        return "비교 없음"
    return f"{point.rerun_actual_timestamp_sec - point.official_timestamp_sec:+.4f} 초"
