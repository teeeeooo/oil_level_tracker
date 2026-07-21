from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.domain.enums import FillState
from oil_tracker.domain.user_truth import TruthDisposition, TruthErrorType
from oil_tracker.ui.presentation_labels import fill_state_label
from oil_tracker.ui.widgets.truth_annotation_canvas import TruthAnnotationCanvas


_DISPOSITION_LABELS = {
    TruthDisposition.CONFIRMED_CORRECT: "공식 결과 확인",
    TruthDisposition.CORRECTED: "수동 수정",
    TruthDisposition.UNUSABLE: "판정 불가",
}
_ERROR_LABELS = {
    TruthErrorType.OIL_BOUNDARY_MISSING: "유면 경계 미검출",
    TruthErrorType.WRONG_CANDIDATE: "잘못된 후보 선택",
    TruthErrorType.FOAM_MISCLASSIFIED: "거품 오인",
    TruthErrorType.GLARE_OR_REFLECTION: "반사광·흐림",
    TruthErrorType.STRUCTURAL_EDGE: "구조물 경계 오인",
    TruthErrorType.ROI_CONFIGURATION: "ROI 설정 문제",
    TruthErrorType.FILL_STATE_MISCLASSIFIED: "상태 분류 오류",
    TruthErrorType.VIDEO_UNUSABLE: "영상 판독 불가",
    TruthErrorType.OTHER: "기타",
}
_ANNOTATION_ROLE = int(Qt.ItemDataRole.UserRole) + 31


@dataclass(frozen=True)
class TruthDraftValues:
    disposition: TruthDisposition
    fill_state: FillState | None
    oil_source_y: float | None
    foam_present: bool
    foam_source_y: float | None
    error_types: tuple[TruthErrorType, ...]
    note: str


class TruthAnnotationWindow(QMainWindow):
    loadCurrentRequested = Signal()
    confirmOfficialRequested = Signal()
    saveAnnotationRequested = Signal()
    deleteAnnotationRequested = Signal()
    newTruthSetRequested = Signal()
    openTruthSetRequested = Signal()
    saveTruthSetRequested = Signal()
    saveTruthSetAsRequested = Signal()
    exportCurrentRequested = Signal()
    exportSelectedRequested = Signal()
    exportAllRequested = Signal()
    cancelExportRequested = Signal()
    annotationActivated = Signal(object)
    draftChanged = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.setWindowTitle("사용자 정답과 regression fixture")
        self.resize(1540, 900)
        self._context = None
        self._official = None
        self._current_annotation = None
        self._source_available = False
        self._building = False
        self._build_ui()
        self._connect()
        self.clear_context()
        self.set_session_state("정답 세트 없음", dirty=False)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        file_row = QHBoxLayout()
        self.new_set_button = QPushButton("새 정답 세트")
        self.open_set_button = QPushButton(".oiltruth 열기")
        self.save_set_button = QPushButton("정답 세트 저장")
        self.save_set_as_button = QPushButton("다른 이름으로 저장")
        self.session_label = QLabel("정답 세트 없음")
        self.session_label.setWordWrap(True)
        file_row.addWidget(self.new_set_button)
        file_row.addWidget(self.open_set_button)
        file_row.addWidget(self.save_set_button)
        file_row.addWidget(self.save_set_as_button)
        file_row.addStretch(1)
        file_row.addWidget(self.session_label)
        root.addLayout(file_row)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        filter_row = QHBoxLayout()
        self.disposition_filter = QComboBox()
        self.disposition_filter.addItem("전체", None)
        for value in TruthDisposition:
            self.disposition_filter.addItem(_DISPOSITION_LABELS[value], value)
        self.error_filter = QComboBox()
        self.error_filter.addItem("모든 오류 유형", None)
        for value in TruthErrorType:
            self.error_filter.addItem(_ERROR_LABELS[value], value)
        filter_row.addWidget(self.disposition_filter)
        filter_row.addWidget(self.error_filter)
        self.annotation_count = QLabel("0개")
        filter_row.addWidget(self.annotation_count)
        self.annotation_list = QListWidget()
        self.annotation_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(QLabel("저장된 정답 장면"))
        left_layout.addLayout(filter_row)
        left_layout.addWidget(self.annotation_list, 1)

        center = QWidget()
        center_layout = QVBoxLayout(center)
        context_row = QHBoxLayout()
        self.context_label = QLabel("현재 Viewer 장면을 불러와 주세요.")
        self.context_label.setWordWrap(True)
        self.load_current_button = QPushButton("현재 Viewer 장면 다시 불러오기")
        context_row.addWidget(self.context_label, 1)
        context_row.addWidget(self.load_current_button)
        zoom_row = QHBoxLayout()
        self.edit_target = QComboBox()
        self.edit_target.addItem("유면 경계 편집", "oil")
        self.edit_target.addItem("거품 경계 편집", "foam")
        self.fit_button = QPushButton("화면 맞춤")
        self.actual_button = QPushButton("원본 크기")
        self.zoom_out_button = QPushButton("축소")
        self.zoom_in_button = QPushButton("확대")
        self.official_toggle = QCheckBox("공식 overlay 표시")
        self.official_toggle.setChecked(True)
        zoom_row.addWidget(self.edit_target)
        zoom_row.addStretch(1)
        zoom_row.addWidget(self.official_toggle)
        zoom_row.addWidget(self.fit_button)
        zoom_row.addWidget(self.actual_button)
        zoom_row.addWidget(self.zoom_out_button)
        zoom_row.addWidget(self.zoom_in_button)
        self.canvas = TruthAnnotationCanvas()
        self.canvas_scroll = QScrollArea()
        self.canvas_scroll.setWidgetResizable(False)
        self.canvas_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas_scroll.setWidget(self.canvas)
        self.decode_delta_label = QLabel("")
        self.decode_delta_label.setWordWrap(True)
        center_layout.addLayout(context_row)
        center_layout.addLayout(zoom_row)
        center_layout.addWidget(self.canvas_scroll, 1)
        center_layout.addWidget(self.decode_delta_label)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        disposition_box = QGroupBox("정답 disposition")
        disposition_layout = QVBoxLayout(disposition_box)
        self.disposition_group = QButtonGroup(self)
        self.disposition_buttons = {}
        for value in TruthDisposition:
            button = QRadioButton(_DISPOSITION_LABELS[value])
            self.disposition_group.addButton(button)
            self.disposition_buttons[value] = button
            disposition_layout.addWidget(button)
        self.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
        self.confirm_official_button = QPushButton("공식 결과를 정답으로 확인")
        disposition_layout.addWidget(self.confirm_official_button)

        truth_box = QGroupBox("실제 상태와 위치")
        truth_form = QFormLayout(truth_box)
        self.fill_state = QComboBox()
        for state in FillState:
            if state is not FillState.UNKNOWN_REVIEW:
                self.fill_state.addItem(fill_state_label(state), state)
        self.oil_present = QCheckBox("유면 경계 있음")
        self.oil_y = _y_spin()
        oil_row = QWidget()
        oil_layout = QHBoxLayout(oil_row)
        oil_layout.setContentsMargins(0, 0, 0, 0)
        oil_layout.addWidget(self.oil_present)
        oil_layout.addWidget(self.oil_y)
        self.remove_oil = QPushButton("제거")
        oil_layout.addWidget(self.remove_oil)
        self.foam_present = QCheckBox("거품 front 있음")
        self.foam_y = _y_spin()
        foam_row = QWidget()
        foam_layout = QHBoxLayout(foam_row)
        foam_layout.setContentsMargins(0, 0, 0, 0)
        foam_layout.addWidget(self.foam_present)
        foam_layout.addWidget(self.foam_y)
        self.remove_foam = QPushButton("제거")
        foam_layout.addWidget(self.remove_foam)
        truth_form.addRow("fill state", self.fill_state)
        truth_form.addRow("oil boundary", oil_row)
        truth_form.addRow("foam front", foam_row)

        error_box = QGroupBox("detector 오류 유형 — 복수 선택")
        error_layout = QVBoxLayout(error_box)
        self.error_checks = {}
        for value in TruthErrorType:
            check = QCheckBox(_ERROR_LABELS[value])
            self.error_checks[value] = check
            error_layout.addWidget(check)
        self.note = QTextEdit()
        self.note.setPlaceholderText("사용자 메모 · 기타 선택 시 설명 필수")
        self.note.setMaximumHeight(130)
        self.comparison_label = QLabel("공식 결과와 정답 비교 없음")
        self.comparison_label.setWordWrap(True)
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setObjectName("truthValidationLabel")
        right_layout.addWidget(disposition_box)
        right_layout.addWidget(truth_box)
        right_layout.addWidget(error_box)
        right_layout.addWidget(QLabel("메모"))
        right_layout.addWidget(self.note)
        right_layout.addWidget(QLabel("공식/정답 비교"))
        right_layout.addWidget(self.comparison_label)
        right_layout.addWidget(self.validation_label)
        right_layout.addStretch(1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(left)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setSizes([330, 820, 390])
        root.addWidget(splitter, 1)

        bottom = QHBoxLayout()
        self.save_annotation_button = QPushButton("현재 정답 저장")
        self.delete_annotation_button = QPushButton("선택 정답 삭제")
        self.export_current_button = QPushButton("현재 fixture export")
        self.export_selected_button = QPushButton("선택 fixture export")
        self.export_all_button = QPushButton("전체 fixture export")
        self.cancel_export_button = QPushButton("export 취소")
        self.cancel_export_button.setEnabled(False)
        self.export_progress = QProgressBar()
        self.export_progress.setRange(0, 1000)
        self.export_progress.setValue(0)
        bottom.addWidget(self.save_annotation_button)
        bottom.addWidget(self.delete_annotation_button)
        bottom.addStretch(1)
        bottom.addWidget(self.export_current_button)
        bottom.addWidget(self.export_selected_button)
        bottom.addWidget(self.export_all_button)
        bottom.addWidget(self.cancel_export_button)
        bottom.addWidget(self.export_progress)
        root.addLayout(bottom)

    def _connect(self) -> None:
        self.new_set_button.clicked.connect(self.newTruthSetRequested)
        self.open_set_button.clicked.connect(self.openTruthSetRequested)
        self.save_set_button.clicked.connect(self.saveTruthSetRequested)
        self.save_set_as_button.clicked.connect(self.saveTruthSetAsRequested)
        self.load_current_button.clicked.connect(self.loadCurrentRequested)
        self.confirm_official_button.clicked.connect(self.confirmOfficialRequested)
        self.save_annotation_button.clicked.connect(self.saveAnnotationRequested)
        self.delete_annotation_button.clicked.connect(self.deleteAnnotationRequested)
        self.export_current_button.clicked.connect(self.exportCurrentRequested)
        self.export_selected_button.clicked.connect(self.exportSelectedRequested)
        self.export_all_button.clicked.connect(self.exportAllRequested)
        self.cancel_export_button.clicked.connect(self.cancelExportRequested)
        self.annotation_list.itemActivated.connect(self._annotation_activated)
        self.disposition_filter.currentIndexChanged.connect(self.draftChanged)
        self.error_filter.currentIndexChanged.connect(self.draftChanged)
        self.edit_target.currentIndexChanged.connect(
            lambda _index: self.canvas.set_edit_target(str(self.edit_target.currentData()))
        )
        self.official_toggle.toggled.connect(self.canvas.set_official_visible)
        self.fit_button.clicked.connect(self.fit_canvas)
        self.actual_button.clicked.connect(self.canvas.actual_size)
        self.zoom_out_button.clicked.connect(self.canvas.zoom_out)
        self.zoom_in_button.clicked.connect(self.canvas.zoom_in)
        self.canvas.oilLineChanged.connect(self._oil_from_canvas)
        self.canvas.foamLineChanged.connect(self._foam_from_canvas)
        self.canvas.validationError.connect(self.set_validation_error)
        self.remove_oil.clicked.connect(lambda: self._remove_line("oil"))
        self.remove_foam.clicked.connect(lambda: self._remove_line("foam"))
        for button in self.disposition_buttons.values():
            button.toggled.connect(self._draft_changed)
        self.fill_state.currentIndexChanged.connect(self._state_changed)
        self.oil_present.toggled.connect(self._draft_changed)
        self.foam_present.toggled.connect(self._draft_changed)
        self.oil_y.valueChanged.connect(self._oil_spin_changed)
        self.foam_y.valueChanged.connect(self._foam_spin_changed)
        for check in self.error_checks.values():
            check.toggled.connect(self._draft_changed)
        self.note.textChanged.connect(self._draft_changed)

    def set_source_available(self, available: bool, message: str = "") -> None:
        self._source_available = bool(available)
        self.load_current_button.setEnabled(self._source_available)
        self.export_current_button.setEnabled(self._source_available and self._context is not None)
        self.export_selected_button.setEnabled(self._source_available and bool(self.selected_annotation_ids()))
        self.export_all_button.setEnabled(self._source_available and self.annotation_list.count() > 0)
        if not available and message:
            self.validation_label.setText(message)

    def set_session_state(self, text: str, *, dirty: bool) -> None:
        suffix = " · 저장되지 않은 변경" if dirty else ""
        self.session_label.setText(text + suffix)
        self.save_set_button.setEnabled(text != "정답 세트 없음")
        self.save_set_as_button.setEnabled(text != "정답 세트 없음")

    def set_annotations(self, annotations) -> None:
        current_id = self.current_annotation_id()
        self.annotation_list.clear()
        disposition_filter = self.disposition_filter.currentData()
        error_filter = self.error_filter.currentData()
        visible = []
        for annotation in annotations:
            if disposition_filter is not None and annotation.disposition is not disposition_filter:
                continue
            if error_filter is not None and error_filter not in annotation.error_types:
                continue
            visible.append(annotation)
        for annotation in visible:
            errors = ", ".join(_ERROR_LABELS[value] for value in annotation.error_types) or "오류 없음"
            state = fill_state_label(annotation.truth_fill_state) if annotation.truth_fill_state is not None else "-"
            item = QListWidgetItem(
                f"{annotation.glass_name_snapshot or annotation.glass_id} · {annotation.actual_decoded_timestamp_sec:.3f}s · frame {annotation.frame_index}\n"
                f"{_DISPOSITION_LABELS[annotation.disposition]} · {state} · {errors} · r{annotation.revision}"
            )
            item.setData(_ANNOTATION_ROLE, annotation)
            item.setData(Qt.ItemDataRole.UserRole, annotation.annotation_id)
            self.annotation_list.addItem(item)
            if annotation.annotation_id == current_id:
                item.setSelected(True)
                self.annotation_list.setCurrentItem(item)
        self.annotation_count.setText(f"{len(visible)}개")
        self.delete_annotation_button.setEnabled(bool(self.selected_annotation_ids()))
        self.set_source_available(self._source_available)

    def selected_annotation_ids(self) -> tuple[str, ...]:
        return tuple(
            str(item.data(Qt.ItemDataRole.UserRole))
            for item in self.annotation_list.selectedItems()
            if item.data(Qt.ItemDataRole.UserRole)
        )

    def current_annotation_id(self) -> str:
        item = self.annotation_list.currentItem()
        return str(item.data(Qt.ItemDataRole.UserRole) or "") if item is not None else ""

    def current_annotation(self):
        item = self.annotation_list.currentItem()
        return item.data(_ANNOTATION_ROLE) if item is not None else None

    def set_context(self, frame, glass, context, official_reference, annotation=None) -> None:
        self._building = True
        try:
            self._context = context
            self._official = official_reference
            self._current_annotation = annotation
            self.context_label.setText(
                f"{context.glass_name} · requested {context.requested_timestamp_sec:.3f}s · "
                f"decoded {context.actual_decoded_timestamp_sec:.3f}s · frame {context.frame_index}"
            )
            if annotation is None:
                self.disposition_buttons[TruthDisposition.CORRECTED].setChecked(True)
                self.fill_state.setCurrentIndex(0)
                self.oil_present.setChecked(False)
                self.foam_present.setChecked(False)
                self.oil_y.setValue(0.0)
                self.foam_y.setValue(0.0)
                for check in self.error_checks.values():
                    check.setChecked(False)
                self.note.clear()
            else:
                self.disposition_buttons[annotation.disposition].setChecked(True)
                if annotation.truth_fill_state is not None:
                    index = self.fill_state.findData(annotation.truth_fill_state)
                    if index >= 0:
                        self.fill_state.setCurrentIndex(index)
                self.oil_present.setChecked(annotation.oil_boundary is not None)
                self.foam_present.setChecked(annotation.foam_present)
                if annotation.oil_boundary is not None:
                    self.oil_y.setValue(annotation.oil_boundary.source_frame_y)
                if annotation.foam_front is not None:
                    self.foam_y.setValue(annotation.foam_front.source_frame_y)
                for value, check in self.error_checks.items():
                    check.setChecked(value in annotation.error_types)
                self.note.setPlainText(annotation.note)
            self.canvas.set_frame(frame)
            self.canvas.set_context(
                glass,
                official_reference=official_reference,
                truth_oil_y=self.oil_y.value() if self.oil_present.isChecked() else None,
                truth_foam_y=self.foam_y.value() if self.foam_present.isChecked() else None,
                status_text=f"decoded {context.actual_decoded_timestamp_sec:.3f}s · frame {context.frame_index}",
            )
            self.fit_canvas()
            self.set_validation_error("")
            self._refresh_enabled()
        finally:
            self._building = False

    def clear_context(self, message: str = "현재 Viewer 장면을 불러와 주세요.") -> None:
        self._context = None
        self._official = None
        self._current_annotation = None
        self.context_label.setText(message)
        self.canvas.clear(message)
        self.decode_delta_label.clear()
        self.save_annotation_button.setEnabled(False)
        self.confirm_official_button.setEnabled(False)
        self.export_current_button.setEnabled(False)

    def context(self):
        return self._context

    def existing_annotation(self):
        return self._current_annotation

    def draft_values(self) -> TruthDraftValues:
        disposition = next(
            value for value, button in self.disposition_buttons.items() if button.isChecked()
        )
        fill_state = self.fill_state.currentData() if disposition is TruthDisposition.CORRECTED else None
        return TruthDraftValues(
            disposition=disposition,
            fill_state=fill_state,
            oil_source_y=self.oil_y.value() if self.oil_present.isChecked() else None,
            foam_present=self.foam_present.isChecked(),
            foam_source_y=self.foam_y.value() if self.foam_present.isChecked() else None,
            error_types=tuple(
                value for value, check in self.error_checks.items() if check.isChecked()
            ),
            note=self.note.toPlainText(),
        )

    def apply_official_reference(self) -> None:
        if self._official is None:
            self.set_validation_error("현재 장면에 확인할 공식 tracking sample이 없습니다.")
            return
        self._building = True
        try:
            self.disposition_buttons[TruthDisposition.CONFIRMED_CORRECT].setChecked(True)
            index = self.fill_state.findData(self._official.fill_state)
            if index >= 0:
                self.fill_state.setCurrentIndex(index)
            self.oil_present.setChecked(self._official.oil_boundary is not None)
            self.foam_present.setChecked(self._official.foam_front is not None)
            if self._official.oil_boundary is not None:
                self.oil_y.setValue(self._official.oil_boundary.source_frame_y)
            if self._official.foam_front is not None:
                self.foam_y.setValue(self._official.foam_front.source_frame_y)
            for check in self.error_checks.values():
                check.setChecked(False)
            self.canvas.set_truth_y("oil", self.oil_y.value() if self.oil_present.isChecked() else None)
            self.canvas.set_truth_y("foam", self.foam_y.value() if self.foam_present.isChecked() else None)
        finally:
            self._building = False
        self._refresh_enabled()
        self.draftChanged.emit()

    def set_comparison_text(self, text: str) -> None:
        self.comparison_label.setText(text or "공식 결과와 정답 비교 없음")

    def set_decode_delta(self, requested: float, decoded: float) -> None:
        delta = float(decoded) - float(requested)
        self.decode_delta_label.setText(
            f"annotation 시각 대비 현재 decode 차이: {delta:+.6f}초"
            if abs(delta) > 1e-9
            else "annotation frame identity와 현재 decode 시각이 일치합니다."
        )

    def set_validation_error(self, message: str) -> None:
        self.validation_label.setText(str(message))

    def set_export_running(self, running: bool) -> None:
        self.cancel_export_button.setEnabled(bool(running))
        for button in (self.export_current_button, self.export_selected_button, self.export_all_button):
            button.setEnabled(not running and self._source_available)
        self.export_progress.setValue(0 if running else self.export_progress.value())

    def set_export_progress(self, update) -> None:
        self.export_progress.setValue(int(round(update.fraction * 1000)))
        self.validation_label.setText(
            f"fixture export · {update.processed_fixtures}/{update.total_fixtures} · {update.message}"
        )

    def fit_canvas(self) -> None:
        viewport = self.canvas_scroll.viewport().size()
        self.canvas.fit_to(viewport.width(), viewport.height())

    def _annotation_activated(self, item: QListWidgetItem) -> None:
        annotation = item.data(_ANNOTATION_ROLE)
        if annotation is not None:
            self.annotationActivated.emit(annotation)

    def _oil_from_canvas(self, value: float) -> None:
        self._building = True
        self.oil_present.setChecked(True)
        self.oil_y.setValue(value)
        self._building = False
        self._draft_changed()

    def _foam_from_canvas(self, value: float) -> None:
        self._building = True
        self.foam_present.setChecked(True)
        self.foam_y.setValue(value)
        self._building = False
        self._draft_changed()

    def _remove_line(self, target: str) -> None:
        if target == "oil":
            self.oil_present.setChecked(False)
        else:
            self.foam_present.setChecked(False)
        self.canvas.remove_line(target)
        self._draft_changed()

    def _oil_spin_changed(self, value: float) -> None:
        if not self._building and self.oil_present.isChecked():
            if self.canvas.set_truth_y("oil", value):
                self._draft_changed()

    def _foam_spin_changed(self, value: float) -> None:
        if not self._building and self.foam_present.isChecked():
            if self.canvas.set_truth_y("foam", value):
                self._draft_changed()

    def _state_changed(self, _index: int) -> None:
        state = self.fill_state.currentData()
        if state in {FillState.EMPTY_NO_INTERFACE, FillState.FULL_NO_INTERFACE}:
            self.oil_present.setChecked(False)
            self.canvas.remove_line("oil")
        self._draft_changed()

    def _draft_changed(self, *_args) -> None:
        if self._building:
            return
        self._refresh_enabled()
        self.draftChanged.emit()

    def _refresh_enabled(self) -> None:
        disposition = next(
            value for value, button in self.disposition_buttons.items() if button.isChecked()
        )
        corrected = disposition is TruthDisposition.CORRECTED
        confirmed = disposition is TruthDisposition.CONFIRMED_CORRECT
        self.fill_state.setEnabled(corrected)
        self.oil_present.setEnabled(corrected)
        self.foam_present.setEnabled(corrected)
        self.oil_y.setEnabled(corrected and self.oil_present.isChecked())
        self.foam_y.setEnabled(corrected and self.foam_present.isChecked())
        self.remove_oil.setEnabled(corrected and self.oil_present.isChecked())
        self.remove_foam.setEnabled(corrected and self.foam_present.isChecked())
        for check in self.error_checks.values():
            check.setEnabled(not confirmed)
        self.confirm_official_button.setEnabled(self._official is not None and self._context is not None)
        self.save_annotation_button.setEnabled(self._context is not None)


def _y_spin() -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(-100000.0, 100000.0)
    spin.setDecimals(3)
    spin.setSingleStep(1.0)
    spin.setSuffix(" px Y")
    return spin
