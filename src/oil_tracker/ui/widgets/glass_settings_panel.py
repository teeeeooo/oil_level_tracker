from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.domain.enums import InitialObservationState, JudgmentMode
from oil_tracker.ui.presentation_labels import (
    INITIAL_STATE_CHOICES,
    JUDGMENT_MODE_LABELS,
    initial_state_for_ui,
)


class GlassSettingsPanel(QWidget):
    fieldChanged = Signal(str, object)
    addExclusionRequested = Signal()
    deleteExclusionRequested = Signal(str)
    restoreDefaultsRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._updating = False
        container = QWidget()
        self.form = QFormLayout(container)
        self.form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.name = QLineEdit()
        self.enabled = QCheckBox("이 관찰창을 분석에 포함")
        self.cx = _double(0, 100000)
        self.cy = _double(0, 100000)
        self.width = _double(1, 100000)
        self.height = _double(1, 100000)
        self.zero = _double(0, 100000)
        self.initial = QComboBox()
        for label, value in INITIAL_STATE_CHOICES:
            self.initial.addItem(label, value.value)
        self.has_scale = QCheckBox("mm/pixel 사용")
        self.scale = _double(0.000001, 1000, decimals=6)
        self.judgment = QComboBox()
        for value in JudgmentMode:
            self.judgment.addItem(JUDGMENT_MODE_LABELS[value], value.value)
        self.margin = _double(0, 0.79, decimals=3)
        self.margin.setSingleStep(0.01)
        self.margin.setToolTip("관찰창 테두리부터 검출에서 제외하는 비율입니다.")
        self.crop = QLabel("-")
        self.crop.setWordWrap(True)
        self.form.addRow("관찰창 이름", self.name)
        self.form.addRow(self.enabled)
        self.form.addRow("중심 X", self.cx)
        self.form.addRow("중심 Y", self.cy)
        self.form.addRow("너비", self.width)
        self.form.addRow("높이", self.height)
        self.form.addRow("자동 계산된 분석 영역", self.crop)
        self.form.addRow("기준점 Y", self.zero)
        self.form.addRow("분석 시작 시 상태", self.initial)
        scale_row = QHBoxLayout()
        scale_row.addWidget(self.has_scale)
        scale_row.addWidget(self.scale, 1)
        self.form.addRow("길이 환산", scale_row)
        self.form.addRow("판정 방식", self.judgment)
        self.form.addRow("테두리 제외 비율", self.margin)

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
        self.form.addRow(ex_group)

        advanced = QGroupBox("고급 검출 설정")
        advanced.setCheckable(True)
        advanced.setChecked(False)
        adv = QFormLayout(advanced)
        self.min_conf = _double(0, 1, decimals=3)
        self.canny_low = QSpinBox()
        self.canny_low.setRange(0, 255)
        self.canny_high = QSpinBox()
        self.canny_high.setRange(0, 255)
        self.min_coverage = _double(0, 1, decimals=3)
        self.max_jump = _double(0, 10000)
        self.foam_variance = _double(0, 100000)
        self.foam_area = _double(0, 1, decimals=3)
        adv.addRow("최소 신뢰도", self.min_conf)
        adv.addRow("경계 감도 하한", self.canny_low)
        adv.addRow("경계 감도 상한", self.canny_high)
        adv.addRow("최소 수평 연속 비율", self.min_coverage)
        adv.addRow("장면 간 최대 이동량(px)", self.max_jump)
        adv.addRow("거품 질감 기준", self.foam_variance)
        adv.addRow("최소 거품 면적 비율", self.foam_area)
        self.restore = QPushButton("검출 설정 기본값으로 복원")
        adv.addRow(self.restore)
        self.form.addRow(advanced)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(scroll)
        self.setMinimumWidth(330)
        self.setObjectName("settingsPanel")
        self._connect()

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
            signal = widget.editingFinished if hasattr(widget, "editingFinished") else widget.valueChanged
            signal.connect(lambda k=key, w=widget: self._emit(k, w.value()))
        self.add_ex.clicked.connect(self.addExclusionRequested)
        self.del_ex.clicked.connect(self._delete_exclusion)
        self.restore.clicked.connect(self.restoreDefaultsRequested)

    def set_glass(self, glass) -> None:
        self._updating = True
        self.setEnabled(glass is not None)
        if glass is None:
            self._updating = False
            return
        e = glass.geometry.ellipse
        self.name.setText(glass.name)
        self.enabled.setChecked(glass.enabled)
        self.cx.setValue(e.center_x)
        self.cy.setValue(e.center_y)
        self.width.setValue(e.radius_x * 2)
        self.height.setValue(e.radius_y * 2)
        self.crop.setText(
            f"X {e.bounds.x:.1f} / Y {e.bounds.y:.1f} / "
            f"너비 {e.bounds.width:.1f} / 높이 {e.bounds.height:.1f}"
        )
        self.zero.setValue(glass.geometry.zero_line_y if glass.geometry.zero_line_y is not None else e.center_y)
        initial = initial_state_for_ui(glass.initial_state)
        index = self.initial.findData(initial.value)
        self.initial.setCurrentIndex(max(0, index))
        self.has_scale.setChecked(glass.mm_per_pixel is not None)
        self.scale.setValue(glass.mm_per_pixel or 1.0)
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

    def _emit(self, key: str, value) -> None:
        if not self._updating:
            self.fieldChanged.emit(key, value)

    def _scale_changed(self, *_args) -> None:
        self.scale.setEnabled(self.has_scale.isChecked())
        self._emit("mm_per_pixel", self.scale.value() if self.has_scale.isChecked() else None)

    def _delete_exclusion(self) -> None:
        item = self.exclusions.currentItem()
        if item:
            self.deleteExclusionRequested.emit(item.data(Qt.ItemDataRole.UserRole))


def _double(minimum: float, maximum: float, decimals: int = 2) -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(minimum, maximum)
    box.setDecimals(decimals)
    box.setKeyboardTracking(False)
    return box
