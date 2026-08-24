from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QMessageBox

from oil_tracker.domain.session import DebugTraceLevel


_TRACE_OPTIONS = (
    (
        DebugTraceLevel.NONE,
        "저장 안 함",
        "정식 tracking과 event만 저장합니다. 디버그 폴더를 만들지 않습니다.",
    ),
    (
        DebugTraceLevel.BASIC,
        "문제 장면만 저장 — 권장",
        "분석 시작·종료, 압축기 기동 근처와 낮은 신뢰도·검출 유실·거품·반사광·상태 전이 등 문제 가능 장면만 저장합니다.",
    ),
    (
        DebugTraceLevel.FULL,
        "모든 장면 저장 — 개발용",
        "모든 분석 sample의 상세 검출 기록과 artifact를 저장합니다. 분석 시간과 결과 bundle 용량이 크게 증가할 수 있습니다.",
    ),
)


def install_debug_trace_selector(window) -> QComboBox:
    combo = QComboBox(window.session_bar)
    combo.setObjectName("debugTraceLevelCombo")
    combo.setMinimumContentsLength(22)
    for level, label, tooltip in _TRACE_OPTIONS:
        combo.addItem(label, level.value)
        combo.setItemData(combo.count() - 1, tooltip, Qt.ItemDataRole.ToolTipRole)
    combo.setToolTip("분석 당시 detector debug trace를 결과 bundle에 저장할 수준을 선택합니다. 프로필 파일에는 저장되지 않습니다.")
    layout = window.session_bar.layout()
    row = layout.rowCount()
    title = QLabel("분석 기록 옵션")
    title.setToolTip(combo.toolTip())
    layout.addWidget(title, row, 0)
    layout.addWidget(combo, row, 1, 1, 7)
    note = QLabel("문제 장면만 저장이 일반 분석의 권장 기본값입니다.")
    note.setWordWrap(True)
    note.setToolTip(combo.toolTip())
    note.hide()
    window.debug_trace_selector = combo
    window.debug_trace_note = note
    sync_debug_trace_selector(window)

    def changed(_index: int) -> None:
        level = DebugTraceLevel(str(combo.currentData()))
        if window.workbench.session.debug_trace_level is level:
            return
        window.workbench.session.debug_trace_level = level
        window.workbench.mark_dirty()
        if level is DebugTraceLevel.FULL:
            QMessageBox.information(
                window,
                "모든 장면 디버그 기록",
                "모든 분석 장면의 검출 artifact를 저장합니다.\n"
                "분석 시간이 증가하고 결과 bundle 용량이 크게 증가할 수 있습니다.\n"
                "개발 및 정밀 진단에만 사용해 주세요.",
            )
        window._update_state()
        window._refresh_inline_validation()
        window.statusBar().showMessage("분석 기록 옵션이 변경되었습니다. 분석 전에 설정 점검을 다시 실행해 주세요.", 10000)

    combo.currentIndexChanged.connect(changed)
    window.actions["new"].triggered.connect(lambda _checked=False: sync_debug_trace_selector(window))
    return combo


def sync_debug_trace_selector(window) -> None:
    combo = getattr(window, "debug_trace_selector", None)
    if combo is None:
        return
    level = window.workbench.session.debug_trace_level
    index = combo.findData(level.value)
    combo.blockSignals(True)
    combo.setCurrentIndex(max(0, index))
    combo.blockSignals(False)
