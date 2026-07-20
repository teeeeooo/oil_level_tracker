from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDockWidget, QStyle, QToolBar

from oil_tracker.application.preflight import preflight_context_key
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.ui.widgets.preflight_panel import PreflightPanel


class PreflightCoordinator(QObject):
    """Connect preflight application work to the existing Workbench without owning domain state."""

    def __init__(self, window, controller, parent=None) -> None:
        super().__init__(parent or window)
        self.window = window
        self.controller = controller
        self.panel = PreflightPanel()
        self.dock = QDockWidget("여러 시점 점검", window)
        self.dock.setObjectName("preflightDock")
        self.dock.setWidget(self.panel)
        self.dock.setMinimumHeight(300)
        window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock)
        self.dock.hide()

        self.action = QAction(
            window.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton),
            "여러 시점 점검",
            window,
        )
        toolbar = window.findChild(QToolBar, "mainToolBar")
        if toolbar is not None:
            toolbar.addSeparator()
            toolbar.addAction(self.action)

        self.last_result = None
        self._request_context_key: str | None = None
        self._context_check_pending = False
        self._running = False
        self._connect()
        window.installEventFilter(self)
        self._set_progress_status("점검하지 않음", "대표 장면 점검을 실행할 수 있습니다.")

    def _connect(self) -> None:
        self.action.triggered.connect(self.start)
        self.panel.runRequested.connect(self.start)
        self.panel.cancelRequested.connect(self.controller.cancel)
        self.panel.resultActivated.connect(self.navigate_to_result)
        self.controller.started.connect(self._started)
        self.controller.progress.connect(self.panel.set_progress)
        self.controller.completed.connect(self._completed)
        self.controller.failed.connect(self._failed)
        self.controller.cancelled.connect(self._cancelled)

        window = self.window
        change_signals = (
            window.actions["new"].triggered,
            window.actions["load"].triggered,
            window.open_video_button.clicked,
            window.glass_list.addRequested,
            window.glass_list.deleteRequested,
            window.glass_list.enabledChanged,
            window.canvas.geometryChanged,
            window.canvas.zeroLineChanged,
            window.canvas.exclusionChanged,
            window.settings.fieldChanged,
            window.settings.addExclusionRequested,
            window.settings.deleteExclusionRequested,
            window.settings.restoreDefaultsRequested,
            window.settings.editRoiRequested,
            window.settings.resetGlassRequested,
            window.undo_stack.indexChanged,
        )
        for signal in change_signals:
            signal.connect(self.schedule_context_check)
        for spin in (window.start_spin, window.end_spin, window.compressor_spin, window.sampling_spin):
            spin.editingFinished.connect(self.schedule_context_check)
        window.actions["analyze"].triggered.connect(self._analysis_action_finished)

    def start(self) -> None:
        self.dock.show()
        self.dock.raise_()
        self._request_context_key = self._current_context_key()
        self.controller.start(self.window.workbench.recipe, self.window.workbench.session)

    def navigate_to_result(self, glass_id: str, timestamp: float, reason: str) -> None:
        if not any(glass.id == glass_id for glass in self.window.workbench.recipe.glasses):
            self.window.statusBar().showMessage("해당 관찰창이 현재 설정에 없어 이동할 수 없습니다.")
            return
        self.window.select_glass(glass_id)
        self.window._load_frame(timestamp)
        self.window.schedule_preview()
        self.window.statusBar().showMessage(f"여러 시점 점검: {reason}")

    def schedule_context_check(self, *_args) -> None:
        if self._context_check_pending:
            return
        self._context_check_pending = True
        QTimer.singleShot(0, self._check_context)

    def _check_context(self) -> None:
        self._context_check_pending = False
        current = self._current_context_key()
        if self._running and current != self._request_context_key:
            self.controller.invalidate()
            self._running = False
            self.panel.set_stale()
            self._set_progress_status("재점검 필요", "설정 변경으로 실행 중 결과를 무효화했습니다.")
            return
        if self.last_result is not None:
            if current == self.last_result.context_key:
                if not self._running:
                    self.panel.set_result(self.last_result)
                    self._set_progress_status(self.panel.status_label.text(), self.panel.detail_label.text())
            else:
                self.panel.set_stale()
                self._set_progress_status("재점검 필요", "영상 또는 관찰창 설정이 변경되었습니다.")

    def _analysis_action_finished(self) -> None:
        if self.window.workbench.state != WorkbenchState.ANALYZING:
            return
        self.controller.invalidate()
        if self._running or self.last_result is not None:
            self.panel.set_stale()
            self._set_progress_status("재점검 필요", "정식 분석 시작으로 사전 점검 요청을 종료했습니다.")
        self._running = False

    def _started(self) -> None:
        self._running = True
        self.last_result = None
        self.panel.set_running()
        self._set_progress_status("진행 중", "대표 장면을 검사하고 있습니다.")
        self.window.statusBar().showMessage("여러 시점 점검을 시작했습니다.")

    def _completed(self, result) -> None:
        self._running = False
        if result.context_key != self._current_context_key():
            self.last_result = result
            self.panel.set_stale()
            self._set_progress_status("재점검 필요", "점검 중 설정이 변경되어 결과를 무효화했습니다.")
            return
        self.last_result = result
        self.panel.set_result(result)
        self._set_progress_status(self.panel.status_label.text(), self.panel.detail_label.text())
        self.window.statusBar().showMessage(f"여러 시점 점검 완료: {self.panel.status_label.text()}")

    def _failed(self, message: str) -> None:
        self._running = False
        self.panel.set_failure(message)
        self._set_progress_status("실패", message)
        self.window.statusBar().showMessage(f"여러 시점 점검 실패: {message}")

    def _cancelled(self) -> None:
        self._running = False
        self.panel.set_cancelled()
        self._set_progress_status("취소됨", "다시 점검할 수 있습니다.")
        self.window.statusBar().showMessage("여러 시점 점검이 취소되었습니다.")

    def _current_context_key(self) -> str:
        return preflight_context_key(self.window.workbench.recipe, self.window.workbench.session)

    def _set_progress_status(self, status: str, detail: str) -> None:
        setter = getattr(self.window.progress, "set_preflight_status", None)
        if callable(setter):
            setter(status, detail)

    def eventFilter(self, watched, event) -> bool:
        if watched is self.window and event.type() == QEvent.Type.Close:
            self.controller.invalidate()
        return super().eventFilter(watched, event)
