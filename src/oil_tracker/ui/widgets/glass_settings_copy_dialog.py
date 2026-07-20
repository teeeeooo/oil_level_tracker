from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.application.observation_settings_copy import (
    GlassSettingsCopyOptions,
    GlassSettingsCopyRequest,
)


class GlassSettingsCopyDialog(QDialog):
    def __init__(self, recipe, source_glass_id: str, readiness_by_id=None, parent=None) -> None:
        super().__init__(parent)
        self.recipe = recipe
        self.source_glass_id = source_glass_id
        self.readiness_by_id = readiness_by_id or {}
        self.target_checks: dict[str, QCheckBox] = {}
        self.option_checks: dict[str, QCheckBox] = {}
        self.setWindowTitle("관찰창 설정 복사")
        self.setModal(True)
        self.setMinimumSize(560, 560)
        self.resize(640, 680)
        self._build_ui()
        self._update_state()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        source = self._source_glass()
        source_group = QGroupBox("원본 관찰창")
        source_layout = QVBoxLayout(source_group)
        if source is None:
            source_text = "선택한 원본 관찰창을 찾을 수 없습니다."
        else:
            readiness = self.readiness_by_id.get(source.id)
            readiness_text = readiness.label if readiness is not None else "상태 확인 전"
            analysis_text = "분석 포함" if source.enabled else "분석 제외"
            source_text = f"{source.name}\n{analysis_text} · {readiness_text}"
        self.source_label = QLabel(source_text)
        self.source_label.setWordWrap(True)
        source_layout.addWidget(self.source_label)
        root.addWidget(source_group)

        target_group = QGroupBox("복사 대상")
        target_group_layout = QVBoxLayout(target_group)
        target_help = QLabel("원본을 제외한 관찰창 중 하나 이상을 선택해 주세요. 분석 제외 관찰창도 선택할 수 있습니다.")
        target_help.setWordWrap(True)
        target_group_layout.addWidget(target_help)
        target_buttons = QHBoxLayout()
        self.select_all_button = QPushButton("모두 선택")
        self.clear_all_button = QPushButton("모두 해제")
        target_buttons.addWidget(self.select_all_button)
        target_buttons.addWidget(self.clear_all_button)
        target_buttons.addStretch(1)
        target_group_layout.addLayout(target_buttons)
        target_content = QWidget()
        target_layout = QVBoxLayout(target_content)
        target_layout.setContentsMargins(4, 4, 4, 4)
        for glass in self.recipe.glasses:
            if glass.id == self.source_glass_id:
                continue
            readiness = self.readiness_by_id.get(glass.id)
            status_parts = []
            if not glass.enabled:
                status_parts.append("분석 제외")
            elif readiness is not None:
                status_parts.append(readiness.label)
            suffix = f" · {' · '.join(status_parts)}" if status_parts else ""
            check = QCheckBox(f"{glass.name}{suffix}")
            check.setToolTip("이 관찰창의 위치, 기준점, 제외 영역과 분석 포함 여부는 유지됩니다.")
            check.toggled.connect(self._update_state)
            self.target_checks[glass.id] = check
            target_layout.addWidget(check)
        target_layout.addStretch(1)
        target_scroll = QScrollArea()
        target_scroll.setWidgetResizable(True)
        target_scroll.setMinimumHeight(130)
        target_scroll.setWidget(target_content)
        target_group_layout.addWidget(target_scroll)
        root.addWidget(target_group, 1)

        option_group = QGroupBox("복사할 설정")
        option_layout = QVBoxLayout(option_group)
        source_mm = source.mm_per_pixel if source is not None else None
        mm_text = (
            "길이 환산값 (원본: 미설정 — 선택 시 None 복사)"
            if source_mm is None
            else f"길이 환산값 (원본: {source_mm:g} mm/pixel)"
        )
        option_specs = (
            ("judgment_rule", "판정 설정", "판정 mode와 recovery, hold, coverage, violation 관련 값을 모두 복사합니다.", True),
            ("detector_settings", "검출기 설정", "현재 검출기 설정 전체를 독립된 값으로 복사합니다.", True),
            ("margin_ratio", "테두리 제외 범위", "타원 내부의 테두리 제외 비율을 복사합니다.", True),
            ("initial_state", "분석 시작 시 상태", "분석 시작 시 유면 상태 가정을 복사합니다.", True),
            ("mm_per_pixel", mm_text, "미설정 값(None)도 선택한 경우 정확히 복사합니다.", False),
            ("ellipse_size", "타원 크기", "가로·세로 반지름만 복사합니다. 중심 위치와 기준점은 복사되지 않습니다.", False),
        )
        for key, text, tooltip, checked in option_specs:
            check = QCheckBox(text)
            check.setChecked(checked)
            check.setToolTip(tooltip)
            check.toggled.connect(self._update_state)
            self.option_checks[key] = check
            option_layout.addWidget(check)
        ellipse_note = QLabel("타원 크기를 선택해도 대상 관찰창의 중심 위치, 기준점과 제외 영역은 유지됩니다.")
        ellipse_note.setWordWrap(True)
        ellipse_note.setObjectName("fieldHelp")
        option_layout.addWidget(ellipse_note)
        root.addWidget(option_group)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName("copySummary")
        root.addWidget(self.summary_label)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Cancel
        )
        self.apply_button = self.button_box.button(QDialogButtonBox.StandardButton.Apply)
        self.cancel_button = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.apply_button.setText("적용")
        self.apply_button.setObjectName("primaryActionButton")
        self.apply_button.setDefault(True)
        self.cancel_button.setText("취소")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        root.addWidget(self.button_box)

        self.select_all_button.clicked.connect(lambda: self._set_all_targets(True))
        self.clear_all_button.clicked.connect(lambda: self._set_all_targets(False))

    def copy_request(self) -> GlassSettingsCopyRequest:
        target_ids = tuple(
            glass.id
            for glass in self.recipe.glasses
            if glass.id in self.target_checks and self.target_checks[glass.id].isChecked()
        )
        options = GlassSettingsCopyOptions(
            judgment_rule=self.option_checks["judgment_rule"].isChecked(),
            detector_settings=self.option_checks["detector_settings"].isChecked(),
            margin_ratio=self.option_checks["margin_ratio"].isChecked(),
            initial_state=self.option_checks["initial_state"].isChecked(),
            mm_per_pixel=self.option_checks["mm_per_pixel"].isChecked(),
            ellipse_size=self.option_checks["ellipse_size"].isChecked(),
        )
        return GlassSettingsCopyRequest(self.source_glass_id, target_ids, options)

    def _source_glass(self):
        return next((glass for glass in self.recipe.glasses if glass.id == self.source_glass_id), None)

    def _set_all_targets(self, checked: bool) -> None:
        for target_check in self.target_checks.values():
            target_check.setChecked(checked)
        self._update_state()

    def _update_state(self, _checked: bool | None = None) -> None:
        source = self._source_glass()
        selected_targets = [
            glass for glass in self.recipe.glasses if glass.id in self.target_checks and self.target_checks[glass.id].isChecked()
        ]
        selected_options = [check.text().split(" (")[0] for check in self.option_checks.values() if check.isChecked()]
        can_apply = source is not None and bool(selected_targets) and bool(selected_options)
        if hasattr(self, "apply_button"):
            self.apply_button.setEnabled(can_apply)
        if not hasattr(self, "summary_label"):
            return
        if source is None:
            self.summary_label.setText("원본 관찰창이 현재 분석 프로필에 없습니다.")
        elif not selected_targets:
            self.summary_label.setText("복사 대상 관찰창을 선택해 주세요.")
        elif not selected_options:
            self.summary_label.setText("복사할 설정 항목을 선택해 주세요.")
        else:
            target_names = ", ".join(glass.name for glass in selected_targets)
            self.summary_label.setText(
                f"{source.name}의 설정 {len(selected_options)}개를\n{target_names}에 복사합니다."
            )
