from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from oil_tracker.domain.enums import InitialObservationState, JudgmentMode


class GlassSettingsPanel(QWidget):
    fieldChanged = Signal(str, object)
    addExclusionRequested = Signal()
    deleteExclusionRequested = Signal(str)
    restoreDefaultsRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._updating = False
        container = QWidget(); self.form = QFormLayout(container)
        self.name = QLineEdit(); self.enabled = QCheckBox("Enabled")
        self.cx = _double(0, 100000); self.cy = _double(0, 100000)
        self.width = _double(1, 100000); self.height = _double(1, 100000)
        self.zero = _double(0, 100000)
        self.initial = QComboBox(); self.initial.addItems([x.value for x in InitialObservationState])
        self.has_scale = QCheckBox("Use mm/pixel"); self.scale = _double(0.000001, 1000, decimals=6)
        self.judgment = QComboBox(); self.judgment.addItems([x.value for x in JudgmentMode])
        self.margin = _double(0, 0.79, decimals=3); self.margin.setSingleStep(0.01)
        self.crop = QLabel("-")
        self.form.addRow("Glass name", self.name); self.form.addRow(self.enabled)
        self.form.addRow("Center X", self.cx); self.form.addRow("Center Y", self.cy)
        self.form.addRow("Width", self.width); self.form.addRow("Height", self.height)
        self.form.addRow("Derived crop ROI", self.crop); self.form.addRow("Zero line Y", self.zero)
        self.form.addRow("Initial state", self.initial)
        scale_row = QHBoxLayout(); scale_row.addWidget(self.has_scale); scale_row.addWidget(self.scale)
        self.form.addRow("Scale", scale_row)
        self.form.addRow("Judgment mode", self.judgment); self.form.addRow("Margin ratio", self.margin)

        ex_group = QGroupBox("Exclusion zones"); ex_layout = QVBoxLayout(ex_group)
        self.exclusions = QListWidget(); ex_layout.addWidget(self.exclusions)
        ex_buttons = QHBoxLayout(); self.add_ex = QPushButton("추가"); self.del_ex = QPushButton("삭제")
        ex_buttons.addWidget(self.add_ex); ex_buttons.addWidget(self.del_ex); ex_layout.addLayout(ex_buttons)
        self.form.addRow(ex_group)

        advanced = QGroupBox("Detector advanced settings"); advanced.setCheckable(True); advanced.setChecked(False)
        adv = QFormLayout(advanced)
        self.min_conf = _double(0, 1, decimals=3); self.canny_low = QSpinBox(); self.canny_low.setRange(0, 255)
        self.canny_high = QSpinBox(); self.canny_high.setRange(0, 255)
        self.min_coverage = _double(0, 1, decimals=3); self.max_jump = _double(0, 10000)
        self.foam_variance = _double(0, 100000); self.foam_area = _double(0, 1, decimals=3)
        adv.addRow("Minimum confidence", self.min_conf); adv.addRow("Canny low", self.canny_low); adv.addRow("Canny high", self.canny_high)
        adv.addRow("Minimum horizontal coverage", self.min_coverage); adv.addRow("Temporal max jump px", self.max_jump)
        adv.addRow("Foam variance", self.foam_variance); adv.addRow("Foam min area ratio", self.foam_area)
        self.restore = QPushButton("기본값 복원"); adv.addRow(self.restore)
        self.form.addRow(advanced)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(container)
        layout = QVBoxLayout(self); layout.addWidget(scroll)
        self.setMinimumWidth(290)
        self._connect()

    def _connect(self) -> None:
        self.name.editingFinished.connect(lambda: self._emit("name", self.name.text()))
        self.enabled.toggled.connect(lambda v: self._emit("enabled", v))
        for key, widget in (("center_x", self.cx), ("center_y", self.cy), ("width", self.width), ("height", self.height), ("zero_line_y", self.zero), ("margin_ratio", self.margin)):
            widget.editingFinished.connect(lambda k=key, w=widget: self._emit(k, w.value()))
        self.initial.currentTextChanged.connect(lambda v: self._emit("initial_state", v))
        self.has_scale.toggled.connect(self._scale_changed); self.scale.editingFinished.connect(self._scale_changed)
        self.judgment.currentTextChanged.connect(lambda v: self._emit("judgment_mode", v))
        for key, widget in (("minimum_final_confidence", self.min_conf), ("canny_low", self.canny_low), ("canny_high", self.canny_high), ("minimum_horizontal_coverage", self.min_coverage), ("temporal_max_jump_px", self.max_jump), ("foam_variance_threshold", self.foam_variance), ("foam_min_area_ratio", self.foam_area)):
            signal = widget.editingFinished if hasattr(widget, "editingFinished") else widget.valueChanged
            signal.connect(lambda k=key, w=widget: self._emit(k, w.value()))
        self.add_ex.clicked.connect(self.addExclusionRequested)
        self.del_ex.clicked.connect(self._delete_exclusion)
        self.restore.clicked.connect(self.restoreDefaultsRequested)

    def set_glass(self, glass) -> None:
        self._updating = True
        self.setEnabled(glass is not None)
        if glass is None:
            self._updating = False; return
        e = glass.geometry.ellipse
        self.name.setText(glass.name); self.enabled.setChecked(glass.enabled)
        self.cx.setValue(e.center_x); self.cy.setValue(e.center_y); self.width.setValue(e.radius_x*2); self.height.setValue(e.radius_y*2)
        self.crop.setText(f"x={e.bounds.x:.1f}, y={e.bounds.y:.1f}, w={e.bounds.width:.1f}, h={e.bounds.height:.1f}")
        self.zero.setValue(glass.geometry.zero_line_y or e.center_y)
        self.initial.setCurrentText(glass.initial_state.value)
        self.has_scale.setChecked(glass.mm_per_pixel is not None); self.scale.setValue(glass.mm_per_pixel or 1.0); self.scale.setEnabled(glass.mm_per_pixel is not None)
        self.judgment.setCurrentText(glass.judgment_rule.mode.value); self.margin.setValue(glass.geometry.margin_ratio)
        ds = glass.detector_settings
        self.min_conf.setValue(ds.minimum_final_confidence); self.canny_low.setValue(ds.canny_low); self.canny_high.setValue(ds.canny_high)
        self.min_coverage.setValue(ds.minimum_horizontal_coverage); self.max_jump.setValue(ds.temporal_max_jump_px)
        self.foam_variance.setValue(ds.foam_variance_threshold); self.foam_area.setValue(ds.foam_min_area_ratio)
        self.exclusions.clear()
        for zone in glass.geometry.exclusions:
            item = QListWidgetItem(f"{zone.name} ({zone.rect.x:.0f},{zone.rect.y:.0f},{zone.rect.width:.0f},{zone.rect.height:.0f})")
            item.setData(Qt.ItemDataRole.UserRole, zone.id); self.exclusions.addItem(item)
        self._updating = False

    def _emit(self, key: str, value) -> None:
        if not self._updating: self.fieldChanged.emit(key, value)

    def _scale_changed(self, *_args) -> None:
        self.scale.setEnabled(self.has_scale.isChecked())
        self._emit("mm_per_pixel", self.scale.value() if self.has_scale.isChecked() else None)

    def _delete_exclusion(self) -> None:
        item = self.exclusions.currentItem()
        if item: self.deleteExclusionRequested.emit(item.data(Qt.ItemDataRole.UserRole))


def _double(minimum: float, maximum: float, decimals: int = 2) -> QDoubleSpinBox:
    box = QDoubleSpinBox(); box.setRange(minimum, maximum); box.setDecimals(decimals); box.setKeyboardTracking(False)
    return box
