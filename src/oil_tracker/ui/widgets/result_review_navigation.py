from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.domain.enums import EventType
from oil_tracker.ui.presentation_labels import result_state_label


_EVENT_LABELS = {
    EventType.ANALYSIS_START: "분석 시작",
    EventType.ANALYSIS_END: "분석 종료",
    EventType.COMPRESSOR_START: "압축기 기동",
    EventType.OIL_BOUNDARY_APPEARED_FROM_TOP: "상단 유면 출현",
    EventType.OIL_BOUNDARY_APPEARED_FROM_BOTTOM: "하단 유면 출현",
    EventType.OIL_DROP_START: "유면 하강 시작",
    EventType.MINIMUM_OIL_LEVEL: "최저 유면",
    EventType.ZERO_CROSS_UP: "기준점 상향 통과",
    EventType.ZERO_CROSS_DOWN: "기준점 하향 통과",
    EventType.ZERO_STABLE_RECOVERY: "기준점 안정 회복",
    EventType.FULL_NO_INTERFACE_START: "가득 참 시작",
    EventType.EMPTY_NO_INTERFACE_START: "비어 있음 시작",
    EventType.FOAM_START: "거품 시작",
    EventType.FOAM_FRONT_RISING: "거품 경계 상승",
    EventType.FOAM_REACH_ZERO: "거품 기준점 도달",
    EventType.FOAM_REACH_TOP: "거품 상단 도달",
    EventType.FOAM_END: "거품 종료",
    EventType.LOW_CONFIDENCE_START: "낮은 신뢰도 시작",
    EventType.LOW_CONFIDENCE_END: "낮은 신뢰도 종료",
    EventType.DETECTION_LOST: "검출 유실",
    EventType.FOGGED_OR_GLARE: "흐림 또는 반사광",
    EventType.REVIEW_REQUIRED: "사용자 검토 필요",
    EventType.JUDGMENT_PASS: "판정 합격",
    EventType.JUDGMENT_FAIL: "판정 불합격",
}


class ResultReviewNavigation(QWidget):
    glassChanged = Signal(str)
    eventActivated = Signal(float)
    reviewActivated = Signal(float)
    previousRequested = Signal()
    nextRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(290)
        self.glass_combo = QComboBox()
        self.result_label = QLabel("결과 bundle 없음")
        self.result_label.setWordWrap(True)
        self.tabs = QTabWidget()
        self.event_list = QListWidget()
        self.review_list = QListWidget()
        self.tabs.addTab(self.event_list, "이벤트")
        self.tabs.addTab(self.review_list, "검토 필요")
        self.previous_button = QPushButton("이전 항목")
        self.next_button = QPushButton("다음 항목")
        buttons = QHBoxLayout()
        buttons.addWidget(self.previous_button)
        buttons.addWidget(self.next_button)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("관찰창"))
        layout.addWidget(self.glass_combo)
        layout.addWidget(self.result_label)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(buttons)
        self.glass_combo.currentIndexChanged.connect(self._glass_changed)
        self.event_list.itemActivated.connect(self._event_activated)
        self.event_list.itemDoubleClicked.connect(self._event_activated)
        self.review_list.itemActivated.connect(self._review_activated)
        self.review_list.itemDoubleClicked.connect(self._review_activated)
        self.previous_button.clicked.connect(self.previousRequested)
        self.next_button.clicked.connect(self.nextRequested)

    def set_bundle(self, bundle, query, selected_glass_id: str | None = None) -> None:
        self.glass_combo.blockSignals(True)
        self.glass_combo.clear()
        for glass in bundle.glasses:
            self.glass_combo.addItem(glass.name, glass.id)
        if selected_glass_id:
            index = self.glass_combo.findData(selected_glass_id)
            if index >= 0:
                self.glass_combo.setCurrentIndex(index)
        self.glass_combo.blockSignals(False)
        self.refresh_items(bundle, query, self.current_glass_id())

    def current_glass_id(self) -> str:
        return str(self.glass_combo.currentData() or "")

    def refresh_items(self, bundle, query, glass_id: str) -> None:
        summary = bundle.glass_summary(glass_id)
        self.result_label.setText(
            f"전체 판정: {result_state_label(summary.result_state)}" if summary is not None else "판정 정보 없음"
        )
        self.event_list.clear()
        for event in query.events_for_glass(glass_id):
            duration = ""
            if event.end_time_sec is not None:
                duration = f"–{event.end_time_sec:.3f}s"
            item = QListWidgetItem(
                f"{event.start_time_sec:.3f}s{duration} · {_EVENT_LABELS.get(event.event_type, event.event_type.value)}"
            )
            item.setData(Qt.ItemDataRole.UserRole, event.start_time_sec)
            item.setToolTip(event.note or f"confidence {event.confidence:.3f}")
            self.event_list.addItem(item)
        self.review_list.clear()
        for interval in query.low_confidence_intervals(glass_id):
            reasons = ", ".join(interval.reasons)
            item = QListWidgetItem(
                f"{interval.start_time_sec:.3f}–{interval.end_time_sec:.3f}s · 최저 {interval.minimum_confidence:.3f}\n{reasons}"
            )
            item.setData(Qt.ItemDataRole.UserRole, interval.representative_time_sec)
            self.review_list.addItem(item)

    def active_tab_is_events(self) -> bool:
        return self.tabs.currentWidget() is self.event_list

    def _glass_changed(self, _index: int) -> None:
        glass_id = self.current_glass_id()
        if glass_id:
            self.glassChanged.emit(glass_id)

    def _event_activated(self, item: QListWidgetItem) -> None:
        self.eventActivated.emit(float(item.data(Qt.ItemDataRole.UserRole)))

    def _review_activated(self, item: QListWidgetItem) -> None:
        self.reviewActivated.emit(float(item.data(Qt.ItemDataRole.UserRole)))
