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

from oil_tracker.application.services.event_presentation import event_type_label, is_major_event
from oil_tracker.domain.review import ReviewFilter
from oil_tracker.ui.presentation_labels import result_state_label


_FILTER_LABELS = (
    (ReviewFilter.ALL, "전체"),
    (ReviewFilter.INVALID, "유효하지 않은 검출"),
    (ReviewFilter.LOW_CONFIDENCE, "신뢰도 기준 미달"),
    (ReviewFilter.REVIEW_REQUIRED, "사용자 확인 필요"),
    (ReviewFilter.FOAM, "거품 영향"),
    (ReviewFilter.GLARE_OR_FOG, "흐림·반사광"),
    (ReviewFilter.DETECTION_LOST, "검출 유실"),
)

_DEBUG_FILTERS = (
    ("all", "전체", set()),
    ("low_confidence", "low confidence", {"low_confidence"}),
    ("invalid_review", "invalid / review", {"invalid", "unknown_review"}),
    ("detection_lost", "detection lost", {"detection_lost", "no_selected_candidate", "rejected_only"}),
    ("glare_fog", "glare / fog", {"glare_or_fog"}),
    ("foam", "foam", {"foam"}),
    ("position_jump", "position jump", {"oil_position_jump", "foam_position_jump"}),
    ("candidate_ambiguity", "candidate ambiguity", {"candidate_ambiguity"}),
    ("state_transition", "state transition", {"state_transition"}),
    ("markers", "start / end / compressor", {"first_sample", "last_sample", "compressor_nearest"}),
)

_EVENT_ROLE = int(Qt.ItemDataRole.UserRole) + 1
_DEBUG_ROLE = int(Qt.ItemDataRole.UserRole) + 2


class ResultReviewNavigation(QWidget):
    glassChanged = Signal(str)
    eventActivated = Signal(float)
    reviewActivated = Signal(float)
    debugActivated = Signal(object)
    eventSelected = Signal(object)
    filterChanged = Signal(str)
    debugFilterChanged = Signal(str)
    eventScopeChanged = Signal(str)
    previousRequested = Signal()
    nextRequested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(260)
        self.glass_combo = QComboBox()
        self.result_label = QLabel("결과 bundle 없음")
        self.result_label.setWordWrap(True)
        self.tabs = QTabWidget()
        self.event_list = QListWidget()
        self.review_list = QListWidget()
        self.debug_list = QListWidget()
        event_page = QWidget()
        event_layout = QVBoxLayout(event_page)
        event_layout.setContentsMargins(0, 0, 0, 0)
        event_filter_row = QHBoxLayout()
        event_filter_row.addWidget(QLabel("표시"))
        self.event_scope = QComboBox()
        self.event_scope.addItem("주요 이벤트", "major")
        self.event_scope.addItem("모든 이벤트", "all")
        event_filter_row.addWidget(self.event_scope, 1)
        event_layout.addLayout(event_filter_row)
        event_layout.addWidget(self.event_list, 1)
        self.event_page = event_page
        self.event_tab_index = self.tabs.addTab(event_page, "이벤트")

        review_page = QWidget()
        review_layout = QVBoxLayout(review_page)
        review_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_combo = QComboBox()
        for review_filter, label in _FILTER_LABELS:
            self.filter_combo.addItem(label, review_filter.value)
        self.filter_combo.setToolTip("검토 필요 항목을 기록된 사유 category로 필터링합니다.")
        self.filter_count = QLabel("0개")
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("사유"))
        filter_row.addWidget(self.filter_combo, 1)
        filter_row.addWidget(self.filter_count)
        review_layout.addLayout(filter_row)
        review_layout.addWidget(self.review_list, 1)
        self.review_tab_index = self.tabs.addTab(review_page, "검토 필요")

        debug_page = QWidget()
        debug_layout = QVBoxLayout(debug_page)
        debug_layout.setContentsMargins(0, 0, 0, 0)
        self.debug_filter_combo = QComboBox()
        for key, label, reasons in _DEBUG_FILTERS:
            self.debug_filter_combo.addItem(label, (key, tuple(sorted(reasons))))
        self.debug_count = QLabel("0개")
        debug_filter_row = QHBoxLayout()
        debug_filter_row.addWidget(QLabel("사유"))
        debug_filter_row.addWidget(self.debug_filter_combo, 1)
        debug_filter_row.addWidget(self.debug_count)
        debug_layout.addLayout(debug_filter_row)
        debug_layout.addWidget(self.debug_list, 1)
        self.debug_tab_index = self.tabs.addTab(debug_page, "디버그 장면")
        self._debug_summaries = ()
        self._debug_message = "이 결과에는 디버그 기록이 없습니다."

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
        self.filter_combo.currentIndexChanged.connect(self._filter_changed)
        self.debug_filter_combo.currentIndexChanged.connect(self._debug_filter_changed)
        self.event_scope.currentIndexChanged.connect(
            lambda _index: self.eventScopeChanged.emit(self.current_event_scope())
        )
        self.event_list.currentItemChanged.connect(self._event_selected)
        self.event_list.itemActivated.connect(self._event_activated)
        self.review_list.itemActivated.connect(self._review_activated)
        self.debug_list.itemActivated.connect(self._debug_activated)
        self.previous_button.clicked.connect(self.previousRequested)
        self.next_button.clicked.connect(self.nextRequested)
        self.set_debug_records((), enabled=False)
        self.set_mode("general")

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

    def clear(self) -> None:
        self.glass_combo.clear()
        self.event_list.clear()
        self.review_list.clear()
        self.result_label.setText("결과 bundle 없음")
        self.filter_count.setText("0개")
        self.set_debug_records((), enabled=False)
        self.eventSelected.emit(None)

    def current_glass_id(self) -> str:
        return str(self.glass_combo.currentData() or "")

    def current_filter(self) -> ReviewFilter:
        return ReviewFilter(str(self.filter_combo.currentData() or ReviewFilter.ALL.value))

    def current_event_scope(self) -> str:
        return str(self.event_scope.currentData() or "major")

    def current_debug_filter(self) -> tuple[str, set[str]]:
        value = self.debug_filter_combo.currentData() or ("all", ())
        return str(value[0]), set(value[1])

    def selected_event(self):
        item = self.event_list.currentItem()
        return item.data(_EVENT_ROLE) if item is not None else None

    def selected_debug(self):
        item = self.debug_list.currentItem()
        return item.data(_DEBUG_ROLE) if item is not None else None

    def set_debug_records(self, summaries, *, enabled: bool = True, message: str = "") -> None:
        self._debug_summaries = tuple(summaries)
        self._debug_message = message or "이 결과에는 디버그 기록이 없습니다."
        self.tabs.setTabEnabled(self.debug_tab_index, bool(enabled))
        self._refresh_debug_list()

    def refresh_items(self, bundle, query, glass_id: str) -> None:
        summary = bundle.glass_summary(glass_id)
        self.result_label.setText(
            f"전체 판정: {result_state_label(summary.result_state)}" if summary is not None else "판정 정보 없음"
        )
        self.event_list.clear()
        for event in query.events_for_glass(glass_id):
            if self.current_event_scope() != "all" and not is_major_event(event.event_type):
                continue
            duration = f"–{event.end_time_sec:.3f}s" if event.end_time_sec is not None else ""
            capture = " · 캡처 기록됨" if event.capture_path else ""
            item = QListWidgetItem(
                f"{event.start_time_sec:.3f}s{duration} · {event_type_label(event.event_type)}{capture}"
            )
            item.setData(Qt.ItemDataRole.UserRole, event.start_time_sec)
            item.setData(_EVENT_ROLE, event)
            tooltip = [f"confidence {event.confidence:.3f}"]
            if event.note:
                tooltip.append(event.note)
            if event.capture_path:
                tooltip.append(f"캡처: {event.capture_path}")
            item.setToolTip("\n".join(tooltip))
            self.event_list.addItem(item)
        self.review_list.clear()
        intervals = query.filtered_intervals(glass_id, self.current_filter())
        self.filter_count.setText(f"{len(intervals)}개")
        if not intervals:
            empty = QListWidgetItem("현재 필터에 해당하는 검토 항목이 없습니다.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self.review_list.addItem(empty)
        else:
            for interval in intervals:
                reasons = ", ".join(interval.reasons)
                item = QListWidgetItem(
                    f"{interval.start_time_sec:.3f}–{interval.end_time_sec:.3f}s · 최저 {interval.minimum_confidence:.3f}\n{reasons}"
                )
                item.setData(Qt.ItemDataRole.UserRole, interval.representative_time_sec)
                item.setToolTip("category: " + ", ".join(category.value for category in interval.categories))
                self.review_list.addItem(item)
        self._refresh_debug_list()
        self.eventSelected.emit(None)

    def active_tab_is_events(self) -> bool:
        return self.tabs.currentWidget() is self.event_page

    def active_tab_is_debug(self) -> bool:
        return self.tabs.currentWidget() is self.tabs.widget(self.debug_tab_index)

    def set_mode(self, mode: str) -> None:
        debug = mode == "debug"
        self.tabs.setTabVisible(self.event_tab_index, not debug)
        self.tabs.setTabVisible(self.review_tab_index, not debug)
        self.tabs.setTabVisible(self.debug_tab_index, debug)
        self.tabs.setCurrentIndex(self.debug_tab_index if debug else self.event_tab_index)

    def _refresh_debug_list(self) -> None:
        self.debug_list.clear()
        glass_id = self.current_glass_id()
        _key, reasons = self.current_debug_filter()
        values = [summary for summary in self._debug_summaries if not glass_id or summary.glass_id == glass_id]
        if reasons:
            values = [summary for summary in values if reasons.intersection(summary.capture_reasons)]
        self.debug_count.setText(f"{len(values)}개")
        if not values:
            empty = QListWidgetItem(self._debug_message if not self._debug_summaries else "현재 필터에 해당하는 디버그 장면이 없습니다.")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            self.debug_list.addItem(empty)
            return
        for summary in values:
            reasons_text = ", ".join(summary.capture_reasons)
            artifact = "artifact 있음" if summary.artifact_availability else "artifact 없음"
            item = QListWidgetItem(
                f"{summary.timestamp_sec:.3f}s · 장면 {summary.frame_index}\n"
                f"{summary.fill_state} · confidence {summary.confidence:.3f}\n{reasons_text} · {artifact}"
            )
            item.setData(Qt.ItemDataRole.UserRole, summary.timestamp_sec)
            item.setData(_DEBUG_ROLE, summary)
            item.setToolTip(
                f"glass: {summary.glass_id}\nrecord: {summary.record_id}\n"
                f"reasons: {reasons_text}\nartifacts: {', '.join(summary.artifact_availability) or '-'}"
            )
            self.debug_list.addItem(item)

    def _glass_changed(self, _index: int) -> None:
        glass_id = self.current_glass_id()
        if glass_id:
            self.glassChanged.emit(glass_id)

    def _filter_changed(self, _index: int) -> None:
        self.filterChanged.emit(self.current_filter().value)

    def _debug_filter_changed(self, _index: int) -> None:
        self._refresh_debug_list()
        self.debugFilterChanged.emit(self.current_debug_filter()[0])

    def _event_selected(self, current, _previous) -> None:
        self.eventSelected.emit(current.data(_EVENT_ROLE) if current is not None else None)

    def _event_activated(self, item: QListWidgetItem) -> None:
        self.eventActivated.emit(float(item.data(Qt.ItemDataRole.UserRole)))

    def _review_activated(self, item: QListWidgetItem) -> None:
        value = item.data(Qt.ItemDataRole.UserRole)
        if value is not None:
            self.reviewActivated.emit(float(value))

    def _debug_activated(self, item: QListWidgetItem) -> None:
        summary = item.data(_DEBUG_ROLE)
        if summary is not None:
            self.debugActivated.emit(summary)
