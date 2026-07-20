from __future__ import annotations

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]


def write(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dedent(content).lstrip(), encoding="utf-8")


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text was not found in {path}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


write(
    "src/oil_tracker/ui/readiness.py",
    r'''
    from __future__ import annotations

    from dataclasses import dataclass
    from enum import Enum

    from oil_tracker.domain.enums import FillState, ValidationSeverity, WorkbenchState
    from oil_tracker.ui.presentation_labels import fill_state_label, validation_issue_short_message


    class GlassReadinessState(str, Enum):
        COMPLETE = "complete"
        REVIEW = "review"
        ERROR = "error"
        EXCLUDED = "excluded"


    class ProgressStepState(str, Enum):
        COMPLETE = "complete"
        CURRENT = "current"
        ERROR = "error"
        WARNING = "warning"
        WAITING = "waiting"


    class PreviewQuality(str, Enum):
        NORMAL = "normal"
        REVIEW = "review"
        FAILURE = "failure"


    @dataclass(frozen=True)
    class GlassReadiness:
        glass_id: str
        state: GlassReadinessState
        label: str
        symbol: str
        reason: str = ""
        issue: object | None = None


    @dataclass(frozen=True)
    class ProgressStep:
        key: str
        label: str
        state: ProgressStepState
        detail: str


    @dataclass(frozen=True)
    class PreviewSummary:
        quality: PreviewQuality
        detection_status: str
        fill_state: str
        confidence: str
        reference_position: str
        judgment: str


    _SEVERITY_ORDER = {
        ValidationSeverity.ERROR: 0,
        ValidationSeverity.WARNING: 1,
        ValidationSeverity.INFORMATION: 2,
    }

    _FIELD_ORDER = {
        "geometry": 0,
        "reference_frame": 1,
        "zero_line_y": 10,
        "exclusions": 20,
        "judgment_mode": 30,
        "judgment_rule": 30,
        "compressor_start": 31,
        "margin": 40,
        "mm_per_pixel": 41,
        "minimum_final_confidence": 42,
        "detector_settings": 42,
    }

    _STATE_LABELS = {
        GlassReadinessState.COMPLETE: ("완료", "✓"),
        GlassReadinessState.REVIEW: ("확인 필요", "⚠"),
        GlassReadinessState.ERROR: ("수정 필요", "●"),
        GlassReadinessState.EXCLUDED: ("분석 제외", "—"),
    }


    def issue_sort_key(issue) -> tuple[int, int, str]:
        return (
            _SEVERITY_ORDER.get(issue.severity, 99),
            _FIELD_ORDER.get(issue.field or "", 90),
            issue.code,
        )


    def prioritize_issues(issues) -> list:
        return sorted(issues, key=issue_sort_key)


    def glass_readiness(glass, validation_result) -> GlassReadiness:
        if not glass.enabled:
            label, symbol = _STATE_LABELS[GlassReadinessState.EXCLUDED]
            return GlassReadiness(glass.id, GlassReadinessState.EXCLUDED, label, symbol)

        related = [
            issue
            for issue in validation_result.issues
            if issue.glass_id == glass.id
            and issue.severity in {ValidationSeverity.ERROR, ValidationSeverity.WARNING}
        ]
        ordered = prioritize_issues(related)
        issue = ordered[0] if ordered else None
        if any(item.severity == ValidationSeverity.ERROR for item in related):
            state = GlassReadinessState.ERROR
            issue = prioritize_issues(
                item for item in related if item.severity == ValidationSeverity.ERROR
            )[0]
        elif any(item.severity == ValidationSeverity.WARNING for item in related):
            state = GlassReadinessState.REVIEW
            issue = prioritize_issues(
                item for item in related if item.severity == ValidationSeverity.WARNING
            )[0]
        else:
            state = GlassReadinessState.COMPLETE
        label, symbol = _STATE_LABELS[state]
        reason = validation_issue_short_message(issue) if issue is not None else ""
        return GlassReadiness(glass.id, state, label, symbol, reason, issue)


    def glass_readiness_by_id(glasses, validation_result) -> dict[str, GlassReadiness]:
        return {glass.id: glass_readiness(glass, validation_result) for glass in glasses}


    def first_actionable_issue(glasses, validation_result):
        summaries = glass_readiness_by_id(glasses, validation_result)
        for target_state in (GlassReadinessState.ERROR, GlassReadinessState.REVIEW):
            for glass in glasses:
                summary = summaries[glass.id]
                if summary.state == target_state:
                    return summary.issue
        return None


    def first_issue_for_fields(validation_result, fields: set[str], *, errors_only: bool = False):
        issues = [
            issue
            for issue in validation_result.issues
            if issue.field in fields
            and (not errors_only or issue.severity == ValidationSeverity.ERROR)
        ]
        ordered = prioritize_issues(issues)
        return ordered[0] if ordered else None


    def first_validation_error(validation_result):
        ordered = prioritize_issues(validation_result.errors)
        return ordered[0] if ordered else None


    def build_workbench_progress(recipe, session, state: WorkbenchState, validation_result) -> list[ProgressStep]:
        errors = validation_result.errors
        warnings = validation_result.warnings
        video_fields = {"input_video_path", "video_metadata", "reference_frame"}
        time_fields = {"analysis_range", "sampling_fps", "compressor_start"}

        video_errors = [issue for issue in errors if issue.field in video_fields]
        video_warnings = [issue for issue in warnings if issue.field in video_fields]
        time_errors = [issue for issue in errors if issue.field in time_fields]
        time_warnings = [issue for issue in warnings if issue.field in time_fields]
        glass_errors = [
            issue
            for issue in errors
            if issue.code == "READY_GLASS"
            or (issue.glass_id is not None and issue.field not in time_fields)
        ]
        glass_warnings = [
            issue
            for issue in warnings
            if issue.glass_id is not None and issue.field not in time_fields
        ]

        video_complete = bool(session.input_video_path and session.video_metadata and not video_errors)
        if not session.input_video_path:
            video_step = ProgressStep("video", "영상 선택", ProgressStepState.CURRENT, "시험 영상을 선택해 주세요")
        elif not video_complete:
            video_step = ProgressStep("video", "영상 선택", ProgressStepState.ERROR, "영상 정보 확인 필요")
        elif video_warnings:
            video_step = ProgressStep("video", "영상 선택", ProgressStepState.WARNING, "영상 조건 확인 필요")
        else:
            video_step = ProgressStep("video", "영상 선택", ProgressStepState.COMPLETE, "영상 정보 읽음")

        if not video_complete:
            time_step = ProgressStep("time", "시간 설정", ProgressStepState.WAITING, "영상 선택 후 설정")
        elif time_errors:
            time_step = ProgressStep("time", "시간 설정", ProgressStepState.ERROR, "시간 조건 수정 필요")
        elif time_warnings:
            time_step = ProgressStep("time", "시간 설정", ProgressStepState.WARNING, "시간 조건 확인 필요")
        else:
            time_step = ProgressStep("time", "시간 설정", ProgressStepState.COMPLETE, "분석 시간 설정 완료")

        enabled_count = sum(1 for glass in recipe.glasses if glass.enabled)
        if enabled_count == 0:
            glass_state = ProgressStepState.CURRENT if video_complete else ProgressStepState.WAITING
            glass_step = ProgressStep("glasses", "관찰창 설정", glass_state, "분석할 관찰창이 필요함")
        elif glass_errors:
            glass_step = ProgressStep("glasses", "관찰창 설정", ProgressStepState.ERROR, "관찰창 수정 필요")
        elif glass_warnings:
            glass_step = ProgressStep("glasses", "관찰창 설정", ProgressStepState.WARNING, "관찰창 확인 필요")
        else:
            glass_step = ProgressStep(
                "glasses", "관찰창 설정", ProgressStepState.COMPLETE, f"{enabled_count}개 설정 완료"
            )

        prerequisites_ready = not errors and enabled_count > 0 and video_complete
        validated = state in {WorkbenchState.VALIDATED, WorkbenchState.ANALYZING, WorkbenchState.ANALYZED}
        if validated:
            validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.COMPLETE, "설정 점검 완료")
        elif prerequisites_ready and state == WorkbenchState.DRAFT_DIRTY:
            validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.CURRENT, "변경 후 재점검 필요")
        elif prerequisites_ready:
            validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.CURRENT, "설정 점검을 실행해 주세요")
        else:
            validation_step = ProgressStep("validation", "설정 점검", ProgressStepState.WAITING, "앞 단계 완료 후 실행")

        if state == WorkbenchState.ANALYZING:
            analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.CURRENT, "분석 중")
        elif state == WorkbenchState.ANALYZED:
            analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.COMPLETE, "분석 완료")
        elif state == WorkbenchState.VALIDATED:
            analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.CURRENT, "분석 실행 가능")
        else:
            analysis_step = ProgressStep("analysis", "분석 실행", ProgressStepState.WAITING, "설정 점검 후 실행")

        return [video_step, time_step, glass_step, validation_step, analysis_step]


    def build_detection_summary(detection, glass) -> PreviewSummary:
        if detection is None:
            return PreviewSummary(
                PreviewQuality.FAILURE,
                "검출 실패",
                "-",
                "-",
                "-",
                "검출 결과가 없습니다",
            )

        confidence = max(0.0, min(1.0, float(detection.overall_confidence)))
        threshold = float(glass.detector_settings.minimum_final_confidence)
        upper_flags = {str(flag).upper() for flag in detection.flags}
        visible_boundary_states = {
            FillState.FILLING_VISIBLE,
            FillState.PARTIAL_VISIBLE,
            FillState.DRAINING_VISIBLE,
        }
        unusable = (
            "DETECTION_LOST" in upper_flags
            or (detection.fill_state in visible_boundary_states and detection.oil_air_level_y is None)
        )
        if unusable:
            quality = PreviewQuality.FAILURE
            detection_status = "검출 실패"
            judgment = "검출 결과를 사용할 수 없음"
        elif detection.fill_state == FillState.UNKNOWN_REVIEW or confidence < threshold:
            quality = PreviewQuality.REVIEW
            detection_status = "확인 필요"
            judgment = "사용자 확인 필요"
        else:
            quality = PreviewQuality.NORMAL
            detection_status = "유면 확인됨" if detection.oil_air_level_y is not None else "유면 경계 미표시"
            judgment = "정상적으로 검출됨"

        reference_position = _reference_position(detection, glass)
        return PreviewSummary(
            quality=quality,
            detection_status=detection_status,
            fill_state=fill_state_label(detection.fill_state),
            confidence=f"{confidence * 100:.0f}%",
            reference_position=reference_position,
            judgment=judgment,
        )


    def _reference_position(detection, glass) -> str:
        if glass.geometry.zero_line_y is None:
            return "기준점 미설정"
        px = detection.oil_air_level_px_from_zero
        if px is None and detection.oil_air_level_y is not None:
            px = glass.geometry.zero_line_y - detection.oil_air_level_y
        if px is None:
            return "유면 경계가 화면에 없음"
        px = float(px)
        if abs(px) < 0.05:
            return "기준점과 같은 위치"
        direction = "위" if px > 0 else "아래"
        text = f"기준점보다 {abs(px):.1f} px {direction}"
        if glass.mm_per_pixel is not None:
            mm = detection.oil_air_level_mm_from_zero
            if mm is None:
                mm = px * glass.mm_per_pixel
            text += f" ({abs(float(mm)):.2f} mm)"
        return text
    ''',
)

write(
    "src/oil_tracker/ui/widgets/workbench_progress.py",
    r'''
    from __future__ import annotations

    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

    from oil_tracker.ui.readiness import ProgressStepState


    _SYMBOLS = {
        ProgressStepState.COMPLETE: "✓",
        ProgressStepState.CURRENT: "▶",
        ProgressStepState.ERROR: "●",
        ProgressStepState.WARNING: "⚠",
        ProgressStepState.WAITING: "○",
    }

    _LABELS = {
        ProgressStepState.COMPLETE: "완료",
        ProgressStepState.CURRENT: "현재 단계",
        ProgressStepState.ERROR: "수정 필요",
        ProgressStepState.WARNING: "확인 필요",
        ProgressStepState.WAITING: "대기",
    }


    class WorkbenchProgressWidget(QWidget):
        stepActivated = Signal(str)
        nextIssueRequested = Signal()

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.setObjectName("workbenchProgress")
            title = QLabel("작업 진행")
            title.setObjectName("progressTitle")
            self._buttons: dict[str, QPushButton] = {}
            steps_layout = QHBoxLayout()
            steps_layout.setContentsMargins(0, 0, 0, 0)
            steps_layout.setSpacing(5)
            for index, (key, label) in enumerate(
                (
                    ("video", "영상 선택"),
                    ("time", "시간 설정"),
                    ("glasses", "관찰창 설정"),
                    ("validation", "설정 점검"),
                    ("analysis", "분석 실행"),
                )
            ):
                button = QPushButton(label)
                button.setObjectName("progressStepButton")
                button.setMinimumHeight(48)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                button.clicked.connect(lambda _checked=False, step_key=key: self.stepActivated.emit(step_key))
                self._buttons[key] = button
                steps_layout.addWidget(button, 1)
                if index < 4:
                    arrow = QLabel("→")
                    arrow.setObjectName("progressArrow")
                    steps_layout.addWidget(arrow)

            self.next_issue = QPushButton("다음 문제로 이동")
            self.next_issue.setObjectName("nextIssueButton")
            self.next_issue.clicked.connect(self.nextIssueRequested)
            self.next_issue.hide()

            top = QHBoxLayout()
            top.addWidget(title)
            top.addStretch(1)
            top.addWidget(self.next_issue)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 6, 8, 6)
            layout.setSpacing(5)
            layout.addLayout(top)
            layout.addLayout(steps_layout)

        def set_steps(self, steps, has_glass_issue: bool) -> None:
            for step in steps:
                button = self._buttons[step.key]
                button.setText(f"{_SYMBOLS[step.state]} {step.label}\n{_LABELS[step.state]}")
                button.setToolTip(step.detail)
                button.setProperty("stepState", step.state.value)
                button.style().unpolish(button)
                button.style().polish(button)
            self.next_issue.setVisible(has_glass_issue)
    ''',
)

write(
    "src/oil_tracker/ui/widgets/detection_summary_card.py",
    r'''
    from __future__ import annotations

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel, QSizePolicy

    from oil_tracker.ui.readiness import PreviewQuality, build_detection_summary


    class DetectionSummaryCard(QGroupBox):
        def __init__(self, parent=None) -> None:
            super().__init__("현재 장면 검출", parent)
            self.setObjectName("detectionSummaryCard")
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
            layout = QGridLayout(self)
            layout.setContentsMargins(9, 7, 9, 7)
            layout.setHorizontalSpacing(14)
            layout.setVerticalSpacing(3)
            self.values: dict[str, QLabel] = {}
            for row, (key, label) in enumerate(
                (
                    ("status", "상태"),
                    ("fill_state", "관측 상태"),
                    ("confidence", "신뢰도"),
                    ("reference", "기준점"),
                    ("judgment", "판정"),
                )
            ):
                heading = QLabel(label)
                heading.setObjectName("detectionSummaryHeading")
                value = QLabel("-")
                value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                value.setWordWrap(True)
                self.values[key] = value
                layout.addWidget(heading, row, 0)
                layout.addWidget(value, row, 1)
            layout.setColumnStretch(1, 1)
            self.set_empty("시험 영상과 관찰창을 선택해 주세요")

        def set_empty(self, message: str) -> None:
            self._set_values("대기", "-", "-", "-", message, "empty")

        def set_loading(self) -> None:
            self._set_values("분석 중", "-", "-", "-", "현재 장면을 확인하고 있습니다", "loading")

        def set_failure(self, message: str) -> None:
            self._set_values("검출 실패", "-", "-", "-", message, "failure")

        def set_detection(self, detection, glass) -> None:
            summary = build_detection_summary(detection, glass)
            self._set_values(
                summary.detection_status,
                summary.fill_state,
                summary.confidence,
                summary.reference_position,
                summary.judgment,
                summary.quality.value,
            )

        def _set_values(
            self,
            status: str,
            fill_state: str,
            confidence: str,
            reference: str,
            judgment: str,
            quality: str,
        ) -> None:
            for key, text in (
                ("status", status),
                ("fill_state", fill_state),
                ("confidence", confidence),
                ("reference", reference),
                ("judgment", judgment),
            ):
                self.values[key].setText(text)
            self.setProperty("quality", quality)
            self.style().unpolish(self)
            self.style().polish(self)
    ''',
)

write(
    "src/oil_tracker/ui/widgets/glass_list_panel.py",
    r'''
    from __future__ import annotations

    from PySide6.QtCore import QSize, Qt, Signal
    from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget


    class GlassListPanel(QWidget):
        addRequested = Signal()
        deleteRequested = Signal()
        selectionChanged = Signal(str)
        enabledChanged = Signal(str, bool)
        issueActivated = Signal(object)

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.list = QListWidget()
            self.list.setWordWrap(True)
            self.list.setSpacing(2)
            self.list.currentItemChanged.connect(self._selected)
            self.list.itemChanged.connect(self._checked)
            self.list.itemDoubleClicked.connect(self._activated)
            self.add_button = QPushButton("관찰창 추가")
            self.delete_button = QPushButton("삭제")
            self.add_button.clicked.connect(self.addRequested)
            self.delete_button.clicked.connect(self.deleteRequested)
            buttons = QHBoxLayout()
            buttons.addWidget(self.add_button)
            buttons.addWidget(self.delete_button)
            layout = QVBoxLayout(self)
            layout.addWidget(self.list)
            layout.addLayout(buttons)
            self.setMinimumWidth(230)

        def set_glasses(self, glasses, selected_id: str | None, readiness_by_id=None) -> None:
            readiness_by_id = readiness_by_id or {}
            self.list.blockSignals(True)
            self.list.clear()
            selected_row = -1
            for row, glass in enumerate(glasses):
                readiness = readiness_by_id.get(glass.id)
                if readiness is None:
                    text = glass.name
                    tooltip = glass.name
                    issue = None
                else:
                    suffix = f" · {readiness.reason}" if readiness.reason else ""
                    text = f"{readiness.symbol} {glass.name}\n{readiness.label}{suffix}"
                    tooltip = f"{glass.name}: {readiness.label}{suffix}"
                    issue = readiness.issue
                item = QListWidgetItem(text)
                item.setToolTip(tooltip)
                item.setData(Qt.ItemDataRole.UserRole, glass.id)
                item.setData(Qt.ItemDataRole.UserRole + 1, issue)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked if glass.enabled else Qt.CheckState.Unchecked)
                item.setSizeHint(QSize(0, 52 if readiness is not None else 32))
                self.list.addItem(item)
                if glass.id == selected_id:
                    selected_row = row
            if selected_row >= 0:
                self.list.setCurrentRow(selected_row)
            self.list.blockSignals(False)

        def _selected(self, current, _previous) -> None:
            if current:
                self.selectionChanged.emit(current.data(Qt.ItemDataRole.UserRole))

        def _checked(self, item) -> None:
            self.enabledChanged.emit(
                item.data(Qt.ItemDataRole.UserRole),
                item.checkState() == Qt.CheckState.Checked,
            )

        def _activated(self, item) -> None:
            issue = item.data(Qt.ItemDataRole.UserRole + 1)
            if issue is not None:
                self.issueActivated.emit(issue)
    ''',
)

replace(
    "src/oil_tracker/ui/presentation_labels.py",
    '''VALIDATION_MESSAGE_BY_CODE = {
''',
    '''VALIDATION_MESSAGE_BY_CODE = {
''',
)
replace(
    "src/oil_tracker/ui/presentation_labels.py",
    '''    "WARN_DURATION": "분석 구간이 1초보다 짧습니다.",
}


def enum_label''',
    '''    "WARN_DURATION": "분석 구간이 1초보다 짧습니다.",
}

VALIDATION_SHORT_MESSAGE_BY_CODE = {
    "STRUCT_ELLIPSE": "관찰 영역 수정 필요",
    "STRUCT_MARGIN": "테두리 제외 범위 수정 필요",
    "STRUCT_MARGIN_AREA": "유효 관찰 영역 수정 필요",
    "READY_ZERO": "기준점 설정 필요",
    "READY_ZERO_BOUNDS": "기준점 위치 수정 필요",
    "WARN_ZERO_EDGE": "기준점 확인 필요",
    "STRUCT_EXCLUSION": "제외 영역 수정 필요",
    "STRUCT_EXCLUSION_BOUNDS": "제외 영역 위치 수정 필요",
    "READY_COMPRESSOR": "압축기 기동 시각 필요",
    "STRUCT_SCALE": "길이 환산값 수정 필요",
    "WARN_SCALE": "길이 환산값 확인 필요",
    "WARN_MARGIN": "테두리 제외 범위 확인 필요",
}


def enum_label''',
)
replace(
    "src/oil_tracker/ui/presentation_labels.py",
    '''def validation_issue_message(issue) -> str:
    return VALIDATION_MESSAGE_BY_CODE.get(issue.code, issue.message)
''',
    '''def validation_issue_message(issue) -> str:
    return VALIDATION_MESSAGE_BY_CODE.get(issue.code, issue.message)


def validation_issue_short_message(issue) -> str:
    if issue is None:
        return ""
    return VALIDATION_SHORT_MESSAGE_BY_CODE.get(issue.code, validation_issue_message(issue))
''',
)

replace(
    "src/oil_tracker/ui/controllers/workbench_controller.py",
    '''    def validate(self):
        result = self.validate_use_case.execute(self.recipe, self.session)
        self.state = WorkbenchState.VALIDATED if result.is_ready else WorkbenchState.DRAFT
        return result
''',
    '''    def validation_result(self):
        return self.validate_use_case.execute(self.recipe, self.session)

    def validate(self):
        result = self.validation_result()
        self.state = WorkbenchState.VALIDATED if result.is_ready else WorkbenchState.DRAFT
        return result
''',
)

replace(
    "src/oil_tracker/ui/controllers/preview_controller.py",
    '''    def request(self, frame, glass, frame_index: int, time_sec: float) -> None:
''',
    '''    def invalidate(self) -> None:
        self.generation += 1

    def request(self, frame, glass, frame_index: int, time_sec: float) -> None:
''',
)

replace(
    "src/oil_tracker/ui/widgets/glass_settings_panel.py",
    '''            "geometry": [self.crop, self.edit_roi, self.cx, self.cy, self.width, self.height],
''',
    '''            "geometry": [self.edit_roi, self.crop, self.cx, self.cy, self.width, self.height],
''',
)

replace(
    "src/oil_tracker/ui/main_window.py",
    '''from oil_tracker.ui.presentation_labels import (
    fill_state_label,
    result_state_label,
    validation_issue_message,
    workbench_state_label,
)
''',
    '''from oil_tracker.ui.presentation_labels import (
    fill_state_label,
    result_state_label,
    validation_issue_message,
    workbench_state_label,
)
from oil_tracker.ui.readiness import (
    build_workbench_progress,
    first_actionable_issue,
    first_issue_for_fields,
    first_validation_error,
    glass_readiness_by_id,
)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''from oil_tracker.ui.widgets.debug_panel import DebugPanel
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
''',
    '''from oil_tracker.ui.widgets.debug_panel import DebugPanel
from oil_tracker.ui.widgets.detection_summary_card import DetectionSummaryCard
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''from oil_tracker.ui.widgets.validation_panel import ValidationPanel
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas
''',
    '''from oil_tracker.ui.widgets.validation_panel import ValidationPanel
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas
from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self._last_validation = None
        self.setWindowTitle''',
    '''        self._last_validation = None
        self._preview_context: tuple[str, int, float] | None = None
        self.setWindowTitle''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self.transport = TransportBar()
        self.session_bar = self._build_session_bar()
        center = QWidget()
''',
    '''        self.transport = TransportBar()
        self.session_bar = self._build_session_bar()
        self.progress = WorkbenchProgressWidget()
        self.detection_summary = DetectionSummaryCard()
        center = QWidget()
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        center_layout.addWidget(self.session_bar)
        center_layout.addWidget(self.canvas, 1)
''',
    '''        center_layout.addWidget(self.session_bar)
        center_layout.addWidget(self.detection_summary)
        center_layout.addWidget(self.canvas, 1)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.splitter, 1)
''',
    '''        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.progress)
        shell_layout.addWidget(self.splitter, 1)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self.glass_list.enabledChanged.connect(self.set_enabled)
        self.canvas.geometryChanged.connect(self._geometry_changed)
''',
    '''        self.glass_list.enabledChanged.connect(self.set_enabled)
        self.glass_list.issueActivated.connect(self._route_validation_issue)
        self.progress.stepActivated.connect(self._progress_step_activated)
        self.progress.nextIssueRequested.connect(self._navigate_next_issue)
        self.canvas.geometryChanged.connect(self._geometry_changed)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''    def _refresh_inline_validation(self):
        if self.workbench.state == WorkbenchState.ANALYZING and self._last_validation is not None:
            return self._last_validation
        result = self.workbench.validate()
        self._last_validation = result
        selected_id = self.workbench.selected_glass_id
        self.settings.set_validation_issues(result.issues, selected_id)
        self.validation_panel.set_result(result)
        self.action_bar.set_validation_result(result)
        self._update_state()
        return result
''',
    '''    def _refresh_inline_validation(self):
        if self.workbench.state == WorkbenchState.ANALYZING and self._last_validation is not None:
            return self._last_validation
        result = self.workbench.validation_result()
        self._apply_validation_result(result)
        return result

    def _apply_validation_result(self, result) -> None:
        self._last_validation = result
        selected_id = self.workbench.selected_glass_id
        self.settings.set_validation_issues(result.issues, selected_id)
        self.validation_panel.set_result(result)
        self.action_bar.set_validation_result(result)
        self._refresh_panels()
        self._update_state()
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''                self._refresh_all()
                return
''',
    '''                self._refresh_all()
                self._refresh_inline_validation()
                return
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''            self.transport.set_position(
                actual,
                self.workbench.session.video_metadata.duration_sec if self.workbench.session.video_metadata else 0.0,
                frame_index,
            )
''',
    '''            self.transport.set_position(
                actual,
                self.workbench.session.video_metadata.duration_sec if self.workbench.session.video_metadata else 0.0,
                frame_index,
            )
            self._invalidate_preview("현재 장면 분석 대기")
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''    def schedule_preview(self) -> None:
        self.preview_timer.start()

    def request_preview(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None and self.current_frame is not None:
            self.statusBar().showMessage("현재 장면을 분석하고 있습니다...")
            self.preview_controller.request(
                self.current_frame,
                glass,
                self.current_frame_index,
                self.current_time,
            )

    def _preview_ready(self, detection, artifacts) -> None:
        self.canvas.set_detection(detection)
        self.debug_panel.set_artifacts(artifacts)
        self.last_debug_artifacts = artifacts
        self.statusBar().showMessage(
            f"현재 상태: {fill_state_label(detection.fill_state)} · 신뢰도 {detection.overall_confidence:.2f}"
        )

    def _preview_failed(self, message: str) -> None:
        self.statusBar().showMessage(f"현재 장면 분석 실패: {message}")
''',
    '''    def schedule_preview(self) -> None:
        self._invalidate_preview("현재 장면 분석 대기")
        if self.workbench.selected_glass() is not None and self.workbench.session.video_metadata is not None:
            self.preview_timer.start()
        else:
            self.preview_timer.stop()

    def request_preview(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None or self.current_frame is None or self.workbench.session.video_metadata is None:
            self._invalidate_preview("시험 영상과 관찰창을 선택해 주세요")
            return
        self._preview_context = (glass.id, self.current_frame_index, self.current_time)
        self.detection_summary.set_loading()
        self.statusBar().showMessage("현재 장면을 분석하고 있습니다...")
        self.preview_controller.request(
            self.current_frame,
            glass,
            self.current_frame_index,
            self.current_time,
        )

    def _preview_ready(self, detection, artifacts) -> None:
        context = self._preview_context
        if context is None:
            return
        selected_id = self.workbench.selected_glass_id
        if (
            detection.glass_id != selected_id
            or detection.glass_id != context[0]
            or detection.frame_index != self.current_frame_index
            or detection.frame_index != context[1]
            or abs(float(detection.time_sec) - self.current_time) > 1e-6
            or abs(float(detection.time_sec) - context[2]) > 1e-6
        ):
            return
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        self.canvas.set_detection(detection)
        self.detection_summary.set_detection(detection, glass)
        self.debug_panel.set_artifacts(artifacts)
        self.last_debug_artifacts = artifacts
        self.statusBar().showMessage(
            f"현재 상태: {fill_state_label(detection.fill_state)} · 신뢰도 {detection.overall_confidence:.2f}"
        )

    def _preview_failed(self, message: str) -> None:
        self.canvas.set_detection(None)
        self.detection_summary.set_failure(message)
        self.last_debug_artifacts = None
        self.statusBar().showMessage(f"현재 장면 분석 실패: {message}")

    def _invalidate_preview(self, message: str) -> None:
        self.preview_controller.invalidate()
        self._preview_context = None
        self.canvas.set_detection(None)
        self.last_debug_artifacts = None
        if self.workbench.session.video_metadata is None:
            self.detection_summary.set_empty("시험 영상을 선택해 주세요")
        elif self.workbench.selected_glass() is None:
            self.detection_summary.set_empty("관찰창을 선택해 주세요")
        else:
            self.detection_summary.set_empty(message)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''    def validate_workbench(self):
        result = self._refresh_inline_validation()
        self.validation_panel.set_result(result)
''',
    '''    def validate_workbench(self):
        result = self.workbench.validate()
        self._apply_validation_result(result)
        self.validation_panel.set_result(result)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self.statusBar().showMessage(validation_issue_message(issue))

    def run_analysis(self) -> None:
''',
    '''        self.statusBar().showMessage(validation_issue_message(issue))

    def _navigate_next_issue(self) -> None:
        if self._last_validation is None:
            return
        issue = first_actionable_issue(self.workbench.recipe.glasses, self._last_validation)
        if issue is None:
            self.statusBar().showMessage("수정하거나 확인할 관찰창 항목이 없습니다.")
            return
        self._route_validation_issue(issue)

    def _progress_step_activated(self, step_key: str) -> None:
        if step_key == "video":
            self.open_video_button.setFocus()
            self.statusBar().showMessage("시험 영상 열기에서 분석 영상을 선택해 주세요.")
            return
        if step_key == "time":
            issue = (
                first_issue_for_fields(
                    self._last_validation,
                    {"analysis_range", "sampling_fps", "compressor_start"},
                )
                if self._last_validation is not None
                else None
            )
            if issue is not None:
                self._route_validation_issue(issue)
            else:
                self.start_spin.setFocus()
                self.statusBar().showMessage("분석 시간과 압축기 기동 시각을 확인해 주세요.")
            return
        if step_key == "glasses":
            self._navigate_next_issue()
            if self.workbench.selected_glass_id is None:
                self.glass_list.list.setFocus()
            return
        if step_key == "validation":
            self.validation_dock.show()
            issue = first_validation_error(self._last_validation) if self._last_validation is not None else None
            if issue is not None:
                self._route_validation_issue(issue)
            else:
                self.action_bar.validate_button.setFocus()
                self.statusBar().showMessage("설정 점검을 실행해 분석 가능 상태를 확정해 주세요.")
            return
        if step_key == "analysis":
            self.action_bar.analyze_button.setFocus()
            message = "분석 실행을 선택해 주세요." if self.workbench.state == WorkbenchState.VALIDATED else "설정 점검 완료 후 분석할 수 있습니다."
            self.statusBar().showMessage(message)

    def run_analysis(self) -> None:
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''    def _refresh_panels(self) -> None:
        self.glass_list.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)
        self.settings.set_glass(self.workbench.selected_glass())
''',
    '''    def _refresh_panels(self) -> None:
        readiness = (
            glass_readiness_by_id(self.workbench.recipe.glasses, self._last_validation)
            if self._last_validation is not None
            else None
        )
        self.glass_list.set_glasses(
            self.workbench.recipe.glasses,
            self.workbench.selected_glass_id,
            readiness,
        )
        self.settings.set_glass(self.workbench.selected_glass())
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self.actions["analyze"].setEnabled(self.workbench.state == WorkbenchState.VALIDATED)
        self.actions["result"].setEnabled(bool(self.last_result_path))
        if self.workbench.state == WorkbenchState.ANALYZING:
            self.action_bar.analyze_button.setEnabled(False)
        elif self._last_validation is not None:
            self.action_bar.set_validation_result(self._last_validation)
''',
    '''        can_analyze = self.workbench.state == WorkbenchState.VALIDATED
        self.actions["analyze"].setEnabled(can_analyze)
        self.actions["result"].setEnabled(bool(self.last_result_path))
        if self._last_validation is not None:
            self.action_bar.set_validation_result(self._last_validation)
            issue = first_actionable_issue(self.workbench.recipe.glasses, self._last_validation)
            self.progress.set_steps(
                build_workbench_progress(
                    self.workbench.recipe,
                    self.workbench.session,
                    self.workbench.state,
                    self._last_validation,
                ),
                issue is not None,
            )
        self.action_bar.analyze_button.setEnabled(can_analyze)
''',
)
replace(
    "src/oil_tracker/ui/main_window.py",
    '''        self.canvas.set_frame(self.current_frame)
''',
    '''        self.canvas.set_frame(self.current_frame)
        self._invalidate_preview("시험 영상을 선택해 주세요")
''',
)

replace(
    "src/oil_tracker/resources/styles/app.qss",
    '''QLabel#roiEditorHint {
    padding: 7px 9px;
    border: 1px solid #cbd7e2;
    border-radius: 5px;
    background: #f5f8fb;
    color: #33485d;
}
''',
    '''QLabel#roiEditorHint {
    padding: 7px 9px;
    border: 1px solid #cbd7e2;
    border-radius: 5px;
    background: #f5f8fb;
    color: #33485d;
}

/* Workbench readiness feedback */
QWidget#workbenchProgress {
    background: #f8fafc;
    border-bottom: 1px solid #c7d1dc;
}

QLabel#progressTitle {
    color: #26394d;
    font-weight: 800;
}

QLabel#progressArrow {
    color: #7b8c9c;
    font-weight: 700;
}

QPushButton#progressStepButton {
    min-width: 105px;
    padding: 4px 7px;
    border: 1px solid #c5d0db;
    border-radius: 5px;
    background: #eef2f6;
    color: #506174;
    font-weight: 700;
}

QPushButton#progressStepButton[stepState="complete"] {
    background: #dff3e7;
    border-color: #98c8aa;
    color: #1f6b3c;
}

QPushButton#progressStepButton[stepState="current"] {
    background: #e1effb;
    border-color: #7daed4;
    color: #155c91;
}

QPushButton#progressStepButton[stepState="error"] {
    background: #fde7e7;
    border-color: #d79999;
    color: #9d2424;
}

QPushButton#progressStepButton[stepState="warning"] {
    background: #fff2d5;
    border-color: #d8b76b;
    color: #855a08;
}

QPushButton#nextIssueButton {
    padding: 4px 10px;
    font-weight: 700;
}

QGroupBox#detectionSummaryCard {
    background: #ffffff;
    border: 1px solid #cbd6e1;
    border-radius: 5px;
}

QGroupBox#detectionSummaryCard[quality="normal"] {
    border: 2px solid #78b58d;
}

QGroupBox#detectionSummaryCard[quality="review"] {
    border: 2px solid #d4a340;
}

QGroupBox#detectionSummaryCard[quality="failure"] {
    border: 2px solid #cc6a6a;
}

QLabel#detectionSummaryHeading {
    color: #617286;
    font-weight: 700;
}
''',
)

write(
    "tests/unit/test_readiness_feedback.py",
    r'''
    from __future__ import annotations

    from oil_tracker.domain.detection import PhaseDetection
    from oil_tracker.domain.enums import FillState, ValidationSeverity, WorkbenchState
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.domain.session import AnalysisSession, VideoMetadata
    from oil_tracker.domain.validation import ValidationIssue, ValidationResult
    from oil_tracker.ui.readiness import (
        GlassReadinessState,
        PreviewQuality,
        ProgressStepState,
        build_detection_summary,
        build_workbench_progress,
        first_actionable_issue,
        glass_readiness,
    )


    def _glass():
        return InspectionRecipe.default_glass(640, 480)


    def test_glass_readiness_states_and_global_issue_isolation():
        glass = _glass()
        glass.enabled = False
        result = ValidationResult([ValidationIssue(ValidationSeverity.ERROR, "READY_VIDEO", "missing")])
        assert glass_readiness(glass, result).state == GlassReadinessState.EXCLUDED

        glass.enabled = True
        error = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "missing", glass.id, "zero_line_y")
        assert glass_readiness(glass, ValidationResult([error])).state == GlassReadinessState.ERROR
        warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_SCALE", "scale", glass.id, "mm_per_pixel")
        assert glass_readiness(glass, ValidationResult([warning])).state == GlassReadinessState.REVIEW
        assert glass_readiness(glass, result).state == GlassReadinessState.COMPLETE
        assert glass_readiness(glass, ValidationResult([])).state == GlassReadinessState.COMPLETE


    def test_glass_reason_priority_prefers_geometry_then_zero_then_scale():
        glass = _glass()
        issues = [
            ValidationIssue(ValidationSeverity.ERROR, "STRUCT_SCALE", "scale", glass.id, "mm_per_pixel"),
            ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", glass.id, "zero_line_y"),
            ValidationIssue(ValidationSeverity.ERROR, "STRUCT_ELLIPSE", "ellipse", glass.id, "geometry"),
        ]
        summary = glass_readiness(glass, ValidationResult(issues))
        assert summary.issue.code == "STRUCT_ELLIPSE"
        assert summary.reason == "관찰 영역 수정 필요"


    def test_first_actionable_issue_prefers_error_glass_before_warning_glass():
        recipe = InspectionRecipe.empty(640, 480)
        first = InspectionRecipe.default_glass(640, 480, 1)
        second = InspectionRecipe.default_glass(640, 480, 2)
        recipe.glasses = [first, second]
        warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_SCALE", "scale", first.id, "mm_per_pixel")
        error = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", second.id, "zero_line_y")
        assert first_actionable_issue(recipe.glasses, ValidationResult([warning, error])) == error


    def test_detection_summary_normal_review_failure_and_position_units():
        glass = _glass()
        glass.mm_per_pixel = 0.2
        normal = PhaseDetection(
            glass.id,
            5,
            1.5,
            FillState.PARTIAL_VISIBLE,
            oil_air_level_y=250.0,
            oil_air_level_px_from_zero=-12.4,
            overall_confidence=0.87,
        )
        summary = build_detection_summary(normal, glass)
        assert summary.quality == PreviewQuality.NORMAL
        assert summary.confidence == "87%"
        assert "12.4 px 아래" in summary.reference_position
        assert "2.48 mm" in summary.reference_position

        review = PhaseDetection(glass.id, 5, 1.5, FillState.UNKNOWN_REVIEW, overall_confidence=0.8)
        assert build_detection_summary(review, glass).quality == PreviewQuality.REVIEW
        low = PhaseDetection(glass.id, 5, 1.5, FillState.PARTIAL_VISIBLE, oil_air_level_y=250, overall_confidence=0.1)
        assert build_detection_summary(low, glass).quality == PreviewQuality.REVIEW
        failed = PhaseDetection(glass.id, 5, 1.5, FillState.PARTIAL_VISIBLE, overall_confidence=0.9)
        assert build_detection_summary(failed, glass).quality == PreviewQuality.FAILURE


    def test_detection_summary_reports_above_and_missing_reference():
        glass = _glass()
        detection = PhaseDetection(
            glass.id,
            1,
            0.0,
            FillState.PARTIAL_VISIBLE,
            oil_air_level_y=200.0,
            oil_air_level_px_from_zero=10.0,
            overall_confidence=0.9,
        )
        assert "10.0 px 위" in build_detection_summary(detection, glass).reference_position
        glass.geometry.zero_line_y = None
        assert build_detection_summary(detection, glass).reference_position == "기준점 미설정"


    def test_progress_states_cover_unselected_invalid_validated_and_dirty():
        recipe = InspectionRecipe.empty(640, 480)
        session = AnalysisSession()
        empty = build_workbench_progress(
            recipe,
            session,
            WorkbenchState.EMPTY,
            ValidationResult([ValidationIssue(ValidationSeverity.ERROR, "READY_VIDEO", "missing", field="input_video_path")]),
        )
        assert empty[0].state == ProgressStepState.CURRENT
        assert empty[-1].state == ProgressStepState.WAITING

        glass = InspectionRecipe.default_glass(640, 480)
        recipe.glasses = [glass]
        session.input_video_path = "video.mp4"
        session.video_metadata = VideoMetadata("video.mp4", 640, 480, 30.0, 10.0, 300)
        session.analysis_end_sec = 10.0
        session.compressor_start_sec = 1.0
        ready = build_workbench_progress(recipe, session, WorkbenchState.VALIDATED, ValidationResult([]))
        assert all(step.state == ProgressStepState.COMPLETE for step in ready[:4])
        assert ready[4].state == ProgressStepState.CURRENT
        dirty = build_workbench_progress(recipe, session, WorkbenchState.DRAFT_DIRTY, ValidationResult([]))
        assert dirty[3].state == ProgressStepState.CURRENT
        assert "재점검" in dirty[3].detail
    ''',
)

write(
    "tests/gui/test_workbench_readiness_feedback.py",
    r'''
    from __future__ import annotations

    from PySide6.QtCore import QObject, Signal

    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
    from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
    from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
    from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
    from oil_tracker.domain.detection import PhaseDetection
    from oil_tracker.domain.enums import FillState, ValidationSeverity, WorkbenchState
    from oil_tracker.domain.session import VideoMetadata
    from oil_tracker.domain.validation import ValidationIssue, ValidationResult
    from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
    from oil_tracker.ui.main_window import MainWindow
    from oil_tracker.ui.widgets.detection_summary_card import DetectionSummaryCard
    from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
    from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget


    class DummyPreviewController(QObject):
        previewReady = Signal(object, object)
        previewFailed = Signal(str)

        def __init__(self):
            super().__init__()
            self.invalidations = 0
            self.requests = []

        def invalidate(self):
            self.invalidations += 1

        def request(self, frame, glass, frame_index, time_sec):
            self.requests.append((glass.id, frame_index, time_sec))


    class DummyAnalysisController(QObject):
        progress = Signal(object)
        completed = Signal(object, str)
        failed = Signal(str)
        cancelled = Signal()

        def start(self, *_args):
            pass

        def cancel(self):
            pass


    class DummyRenderer:
        def export(self, *_args):
            return []


    def _controller() -> WorkbenchController:
        repository = JsonRecipeRepository()
        validator = RecipeValidationService()
        return WorkbenchController(
            SaveRecipeUseCase(repository, validator),
            LoadRecipeUseCase(repository),
            ValidateWorkbenchUseCase(validator),
        )


    def _window(qtbot):
        workbench = _controller()
        preview = DummyPreviewController()
        window = MainWindow(workbench, preview, DummyAnalysisController(), DummyRenderer())
        qtbot.addWidget(window)
        window.show()
        return window, workbench, preview


    def test_glass_list_shows_text_status_and_activates_issue(qtbot):
        panel = GlassListPanel()
        qtbot.addWidget(panel)
        from oil_tracker.domain.recipe import InspectionRecipe
        from oil_tracker.ui.readiness import glass_readiness_by_id

        glass = InspectionRecipe.default_glass(640, 480)
        issue = ValidationIssue(ValidationSeverity.ERROR, "READY_ZERO", "zero", glass.id, "zero_line_y")
        result = ValidationResult([issue])
        panel.set_glasses([glass], glass.id, glass_readiness_by_id([glass], result))
        item = panel.list.item(0)
        assert "수정 필요" in item.text()
        assert "기준점 설정 필요" in item.text()
        with qtbot.waitSignal(panel.issueActivated) as blocker:
            panel._activated(item)
        assert blocker.args == [issue]


    def test_progress_widget_emits_clicked_step(qtbot):
        widget = WorkbenchProgressWidget()
        qtbot.addWidget(widget)
        with qtbot.waitSignal(widget.stepActivated) as blocker:
            widget._buttons["glasses"].click()
        assert blocker.args == ["glasses"]


    def test_detection_card_loading_failure_and_result(qtbot):
        from oil_tracker.domain.recipe import InspectionRecipe

        card = DetectionSummaryCard()
        qtbot.addWidget(card)
        glass = InspectionRecipe.default_glass(640, 480)
        card.set_loading()
        assert card.values["status"].text() == "분석 중"
        card.set_failure("후보 없음")
        assert card.values["judgment"].text() == "후보 없음"
        detection = PhaseDetection(
            glass.id,
            1,
            0.1,
            FillState.PARTIAL_VISIBLE,
            oil_air_level_y=200,
            oil_air_level_px_from_zero=10,
            overall_confidence=0.9,
        )
        card.set_detection(detection, glass)
        assert card.property("quality") == "normal"
        assert "위" in card.values["reference"].text()


    def test_navigation_selects_first_error_glass_focuses_field_and_canvas(qtbot):
        window, workbench, _preview = _window(qtbot)
        first = workbench.add_glass()
        second = workbench.add_glass()
        workbench.set_selected(first.id)
        issue = ValidationIssue(ValidationSeverity.ERROR, "STRUCT_ELLIPSE", "geometry", second.id, "geometry")
        window._apply_validation_result(ValidationResult([issue]))
        window._navigate_next_issue()
        assert workbench.selected_glass_id == second.id
        assert window.canvas._selected_id == second.id
        assert window.settings.edit_roi.hasFocus()
        assert validation_issue_text(window) == "관찰 영역 수정 필요"


    def test_navigation_falls_back_to_warning_when_no_error(qtbot):
        window, workbench, _preview = _window(qtbot)
        first = workbench.add_glass()
        second = workbench.add_glass()
        warning = ValidationIssue(ValidationSeverity.WARNING, "WARN_ZERO_EDGE", "zero", second.id, "zero_line_y")
        window._apply_validation_result(ValidationResult([warning]))
        window._navigate_next_issue()
        assert workbench.selected_glass_id == second.id
        assert window.settings.zero.hasFocus()


    def test_preview_rejects_stale_glass_and_frame_results(qtbot):
        window, workbench, preview = _window(qtbot)
        glass = workbench.add_glass()
        workbench.session.input_video_path = "video.mp4"
        workbench.session.video_metadata = VideoMetadata("video.mp4", 1280, 720, 30.0, 10.0, 300)
        window.current_frame_index = 10
        window.current_time = 1.0
        window._preview_context = (glass.id, 10, 1.0)
        stale = PhaseDetection(glass.id, 9, 0.9, FillState.PARTIAL_VISIBLE, oil_air_level_y=200, overall_confidence=0.9)
        window._preview_ready(stale, object())
        assert window.canvas._detection is None
        current = PhaseDetection(glass.id, 10, 1.0, FillState.PARTIAL_VISIBLE, oil_air_level_y=200, overall_confidence=0.9)
        window._preview_ready(current, object())
        assert window.canvas._detection is current
        window.schedule_preview()
        assert window.canvas._detection is None
        assert preview.invalidations > 0


    def test_inline_validation_does_not_validate_until_explicit_check(qtbot):
        window, workbench, _preview = _window(qtbot)
        workbench.add_glass()
        workbench.session.input_video_path = "video.mp4"
        workbench.session.video_metadata = VideoMetadata("video.mp4", 1280, 720, 30.0, 10.0, 300)
        workbench.session.analysis_end_sec = 10.0
        workbench.session.compressor_start_sec = 1.0
        workbench.state = WorkbenchState.DRAFT
        result = window._refresh_inline_validation()
        assert result.is_ready
        assert workbench.state == WorkbenchState.DRAFT
        assert not window.action_bar.analyze_button.isEnabled()
        window.validate_workbench()
        assert workbench.state == WorkbenchState.VALIDATED
        assert window.action_bar.analyze_button.isEnabled()
        workbench.mark_dirty()
        window._refresh_inline_validation()
        assert workbench.state == WorkbenchState.DRAFT_DIRTY
        assert not window.action_bar.analyze_button.isEnabled()


    def validation_issue_text(window) -> str:
        return window.statusBar().currentMessage()
    ''',
)

print("Phase 2A-1 readiness implementation materialized.")
