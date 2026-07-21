from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.domain.enums import JudgmentMode, ValidationSeverity
from oil_tracker.ui.presentation_labels import (
    INITIAL_STATE_CHOICES,
    JUDGMENT_MODE_LABELS,
    initial_state_for_ui,
    validation_issue_message,
)
from oil_tracker.ui.widgets.wheel_safe_controls import (
    WheelSafeComboBox,
    WheelSafeDoubleSpinBox,
    WheelSafeSpinBox,
)


class GlassSettingsPanel(QWidget):
    fieldChanged = Signal(str, object)
    addExclusionRequested = Signal()
    deleteExclusionRequested = Signal(str)
    restoreDefaultsRequested = Signal()
    editRoiRequested = Signal()
    resetGlassRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._updating = False
        self._validation_messages: dict[str, QLabel] = {}
        self._last_focused_field: str | None = None
        self._selected_glass_id: str | None = None
        self._scale_cache: dict[str, float] = {}

        container = QWidget()
        container.setMinimumWidth(350)
        container.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(4, 4, 8, 8)
        container_layout.setSpacing(8)

        self.name = QLineEdit()
        self.enabled = QCheckBox("이 Glass를 분석에 포함")
        self.zero = _double(0, 100000)
        self.initial = WheelSafeComboBox()
        for label, value in INITIAL_STATE_CHOICES:
            self.initial.addItem(label, value.value)
        self.judgment = WheelSafeComboBox()
        for value in JudgmentMode:
            self.judgment.addItem(JUDGMENT_MODE_LABELS[value], value.value)

        self.edit_roi = QPushButton("분석 영역 편집")
        self.edit_roi.setObjectName("secondaryActionButton")
        self.reset_glass = QPushButton("Glass 초기화")
        area_buttons = QHBoxLayout()
        area_buttons.setSpacing(6)
        area_buttons.addWidget(self.edit_roi, 1)
        area_buttons.addWidget(self.reset_glass)

        self.has_scale = QCheckBox("mm 단위도 함께 표시")
        self.has_scale.setToolTip(
            "선택 사항입니다. 사용하지 않아도 분석과 px 단위 결과 생성에는 영향이 없습니다."
        )
        self.scale = _double(0.000001, 1000, decimals=6)
        self.scale.setSuffix(" mm")
        self.scale.setToolTip("1 px에 해당하는 실제 길이를 mm 단위로 입력합니다.")
        scale_row = QHBoxLayout()
        scale_row.setSpacing(6)
        scale_row.addWidget(self.has_scale)
        scale_row.addWidget(QLabel("1 px ="))
        scale_row.addWidget(self.scale, 1)

        basic = QGroupBox("기본 설정")
        self.form = QFormLayout(basic)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.form.addRow("Glass 이름", self.name)
        self.form.addRow(self.enabled)
        self.form.addRow("분석 영역", area_buttons)
        self.form.addRow(self._message_label("geometry"))
        self.form.addRow("기준선 Y", self.zero)
        self.form.addRow(self._message_label("zero_line_y"))
        self.form.addRow("분석 시작 상태", self.initial)
        self.form.addRow("판정 방식", self.judgment)
        self.form.addRow("실제 길이 환산 — 선택 사항", scale_row)
        self.form.addRow(self._message_label("mm_per_pixel"))
        container_layout.addWidget(basic)

        ex_group = QGroupBox("검출 제외 영역")
        ex_layout = QVBoxLayout(ex_group)
        self.exclusions = QListWidget()
        self.exclusions.setMinimumHeight(90)
        ex_layout.addWidget(self.exclusions)
        ex_buttons = QHBoxLayout()
        self.add_ex = QPushButton("영역 추가")
        self.del_ex = QPushButton("선택 영역 삭제")
        ex_buttons.addWidget(self.add_ex)
        ex_buttons.addWidget(self.del_ex)
        ex_layout.addLayout(ex_buttons)
        ex_layout.addWidget(self._message_label("exclusions"))
        container_layout.addWidget(ex_group)

        self.advanced_toggle = QToolButton()
        self.advanced_toggle.setObjectName("advancedToggle")
        self.advanced_toggle.setText("고급 설정 보기")
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        container_layout.addWidget(self.advanced_toggle)

        self.advanced_container = QWidget()
        advanced_layout = QVBoxLayout(self.advanced_container)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.setSpacing(8)

        self.cx = _double(0, 100000)
        self.cy = _double(0, 100000)
        self.width = _double(1, 100000)
        self.height = _double(1, 100000)
        self.margin = _double(0, 0.79, decimals=3)
        self.margin.setSingleStep(0.01)
        self.margin.setToolTip("분석 영역 테두리를 검출에서 제외하는 비율입니다.")

        geometry_group = QGroupBox("좌표와 분석 범위")
        geometry_form = QFormLayout(geometry_group)
        geometry_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        geometry_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        geometry_form.addRow("중심 X", self.cx)
        geometry_form.addRow("중심 Y", self.cy)
        geometry_form.addRow("너비", self.width)
        geometry_form.addRow("높이", self.height)
        geometry_form.addRow("테두리 제외 범위", self.margin)
        geometry_form.addRow(self._message_label("margin"))
        advanced_layout.addWidget(geometry_group)

        detector_group = QGroupBox("고급 검출 설정")
        detector_form = QFormLayout(detector_group)
        detector_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)
        self.min_conf = _double(0, 1, decimals=3)
        self.canny_low = WheelSafeSpinBox()
        self.canny_low.setRange(0, 255)
        self.canny_high = WheelSafeSpinBox()
        self.canny_high.setRange(0, 255)
        self.min_coverage = _double(0, 1, decimals=3)
        self.max_jump = _double(0, 10000)
        self.foam_variance = _double(0, 100000)
        self.foam_area = _double(0, 1, decimals=3)
        detector_form.addRow("최소 신뢰도", self.min_conf)
        detector_form.addRow("경계 감도 하한", self.canny_low)
        detector_form.addRow("경계 감도 상한", self.canny_high)
        detector_form.addRow("최소 수평 연속 비율", self.min_coverage)
        detector_form.addRow("장면 간 최대 이동량(px)", self.max_jump)
        detector_form.addRow("거품 질감 기준", self.foam_variance)
        detector_form.addRow("최소 거품 면적 비율", self.foam_area)
        self.restore = QPushButton("검출 설정 기본값 복원")
        detector_form.addRow(self.restore)
        advanced_layout.addWidget(detector_group)
        self.advanced_container.hide()
        container_layout.addWidget(self.advanced_container)
        container_layout.addStretch(1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setWidget(container)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.scroll)
        self.setMinimumWidth(370)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setObjectName("settingsPanel")

        self._field_widgets = {
            "geometry": [self.edit_roi, self.cx, self.cy, self.width, self.height],
            "zero_line_y": [self.zero, self.edit_roi],
            "initial_state": [self.initial],
            "exclusions": [self.exclusions, self.add_ex, self.del_ex],
            "mm_per_pixel": [self.has_scale, self.scale],
            "margin": [self.margin],
            "glasses": [self.enabled],
        }
        self._connect()

    def _message_label(self, field: str) -> QLabel:
        label = QLabel()
        label.setObjectName("inlineValidationMessage")
        label.setWordWrap(True)
        label.hide()
        self._validation_messages[field] = label
        return label

    def _connect(self) -> None:
        self.name.editingFinished.connect(lambda: self._emit("name", self.name.text()))
        self.enabled.toggled.connect(lambda value: self._emit("enabled", value))
        for key, widget in (
            ("center_x", self.cx),
            ("center_y", self.cy),
            ("width", self.width),
            ("height", self.height),
            ("zero_line_y", self.zero),
            ("margin_ratio", self.margin),
        ):
            widget.editingFinished.connect(lambda k=key, w=widget: self._emit(k, w.value()))
        self.initial.currentIndexChanged.connect(
            lambda _index: self._emit("initial_state", self.initial.currentData())
        )
        self.has_scale.toggled.connect(self._scale_changed)
        self.scale.editingFinished.connect(self._scale_changed)
        self.judgment.currentIndexChanged.connect(
            lambda _index: self._emit("judgment_mode", self.judgment.currentData())
        )
        for key, widget in (
            ("minimum_final_confidence", self.min_conf),
            ("canny_low", self.canny_low),
            ("canny_high", self.canny_high),
            ("minimum_horizontal_coverage", self.min_coverage),
            ("temporal_max_jump_px", self.max_jump),
            ("foam_variance_threshold", self.foam_variance),
            ("foam_min_area_ratio", self.foam_area),
        ):
            widget.editingFinished.connect(lambda k=key, w=widget: self._emit(k, w.value()))
        self.add_ex.clicked.connect(self.addExclusionRequested)
        self.del_ex.clicked.connect(self._delete_exclusion)
        self.restore.clicked.connect(self.restoreDefaultsRequested)
        self.edit_roi.clicked.connect(self.editRoiRequested)
        self.reset_glass.clicked.connect(self.resetGlassRequested)
        self.advanced_toggle.toggled.connect(self.set_advanced_visible)

    def set_advanced_visible(self, visible: bool) -> None:
        self.advanced_container.setVisible(visible)
        self.advanced_toggle.setArrowType(
            Qt.ArrowType.DownArrow if visible else Qt.ArrowType.RightArrow
        )
        self.advanced_toggle.setText("고급 설정 숨기기" if visible else "고급 설정 보기")
        if self.advanced_toggle.isChecked() != visible:
            self.advanced_toggle.blockSignals(True)
            self.advanced_toggle.setChecked(visible)
            self.advanced_toggle.blockSignals(False)

    def set_glass(self, glass) -> None:
        self._updating = True
        self.setEnabled(glass is not None)
        if glass is None:
            self._selected_glass_id = None
            self._updating = False
            return
        self._selected_glass_id = glass.id
        e = glass.geometry.ellipse
        self.name.setText(glass.name)
        self.enabled.setChecked(glass.enabled)
        self.cx.setValue(e.center_x)
        self.cy.setValue(e.center_y)
        self.width.setValue(e.radius_x * 2)
        self.height.setValue(e.radius_y * 2)
        self.zero.setValue(
            glass.geometry.zero_line_y if glass.geometry.zero_line_y is not None else e.center_y
        )
        initial = initial_state_for_ui(glass.initial_state)
        index = self.initial.findData(initial.value)
        self.initial.setCurrentIndex(max(0, index))
        if glass.mm_per_pixel is not None and glass.mm_per_pixel > 0:
            self._scale_cache[glass.id] = float(glass.mm_per_pixel)
        cached_scale = self._scale_cache.get(glass.id, 1.0)
        self.has_scale.setChecked(glass.mm_per_pixel is not None)
        self.scale.setValue(float(glass.mm_per_pixel or cached_scale))
        self.scale.setEnabled(glass.mm_per_pixel is not None)
        judgment_index = self.judgment.findData(glass.judgment_rule.mode.value)
        self.judgment.setCurrentIndex(max(0, judgment_index))
        self.margin.setValue(glass.geometry.margin_ratio)
        ds = glass.detector_settings
        self.min_conf.setValue(ds.minimum_final_confidence)
        self.canny_low.setValue(ds.canny_low)
        self.canny_high.setValue(ds.canny_high)
        self.min_coverage.setValue(ds.minimum_horizontal_coverage)
        self.max_jump.setValue(ds.temporal_max_jump_px)
        self.foam_variance.setValue(ds.foam_variance_threshold)
        self.foam_area.setValue(ds.foam_min_area_ratio)
        self.exclusions.clear()
        for zone in glass.geometry.exclusions:
            item = QListWidgetItem(
                f"{zone.name} · X {zone.rect.x:.0f}, Y {zone.rect.y:.0f}, "
                f"너비 {zone.rect.width:.0f}, 높이 {zone.rect.height:.0f}"
            )
            item.setData(Qt.ItemDataRole.UserRole, zone.id)
            self.exclusions.addItem(item)
        self._updating = False

    def set_validation_issues(self, issues, glass_id: str | None) -> None:
        for widgets in self._field_widgets.values():
            for widget in widgets:
                self._set_validation_state(widget, "")
        for label in self._validation_messages.values():
            label.clear()
            label.hide()
            label.setProperty("validationState", "")

        grouped: dict[str, list] = {}
        for issue in issues:
            if issue.field not in self._field_widgets:
                continue
            if issue.glass_id is not None and issue.glass_id != glass_id:
                continue
            grouped.setdefault(issue.field, []).append(issue)

        priority = {
            ValidationSeverity.ERROR: 2,
            ValidationSeverity.WARNING: 1,
            ValidationSeverity.INFORMATION: 0,
        }
        for field, field_issues in grouped.items():
            field_issues.sort(key=lambda issue: priority.get(issue.severity, 0), reverse=True)
            strongest = field_issues[0].severity
            state = "error" if strongest == ValidationSeverity.ERROR else "warning"
            messages = []
            for issue in field_issues:
                message = validation_issue_message(issue)
                if message not in messages:
                    messages.append(message)
            for widget in self._field_widgets[field]:
                self._set_validation_state(widget, state)
            label = self._validation_messages.get(field)
            if label is not None:
                prefix = "오류" if state == "error" else "주의"
                label.setText(f"{prefix}: " + " ".join(messages))
                label.setProperty("validationState", state)
                label.style().unpolish(label)
                label.style().polish(label)
                label.show()

    def focus_field(self, field: str | None) -> None:
        self._last_focused_field = field
        if field in {"geometry", "margin"}:
            self.set_advanced_visible(True)
        widgets = self._field_widgets.get(field or "", [])
        if not widgets:
            return
        widget = widgets[0]
        widget.setFocus()
        self.scroll.ensureWidgetVisible(widget, 20, 20)

    def _set_validation_state(self, widget, state: str) -> None:
        widget.setProperty("validationState", state)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def _emit(self, key: str, value) -> None:
        if not self._updating:
            self.fieldChanged.emit(key, value)

    def _scale_changed(self, *_args) -> None:
        enabled = self.has_scale.isChecked()
        self.scale.setEnabled(enabled)
        if enabled and self._selected_glass_id is not None:
            self._scale_cache[self._selected_glass_id] = float(self.scale.value())
        self._emit("mm_per_pixel", float(self.scale.value()) if enabled else None)

    def _delete_exclusion(self) -> None:
        item = self.exclusions.currentItem()
        if item:
            self.deleteExclusionRequested.emit(item.data(Qt.ItemDataRole.UserRole))


def _double(minimum: float, maximum: float, decimals: int = 2) -> WheelSafeDoubleSpinBox:
    box = WheelSafeDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setKeyboardTracking(False)
    return box
