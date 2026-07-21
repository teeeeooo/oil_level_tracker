from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar

from oil_tracker.ui.result_review_window import ResultReviewWindow


class RedetectionResultReviewWindow(ResultReviewWindow):
    bundleAboutToChange = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    redetectionRequested = Signal()
    truthRequested = Signal()
    viewerClosing = Signal()

    def __init__(self, *args, **kwargs) -> None:
        self._bundle_change_guards = []
        self._glass_change_guards = []
        self._close_guards = []
        super().__init__(*args, **kwargs)

    def _build_ui(self) -> None:
        super()._build_ui()
        self.redetection_action = QAction("부분 재검출과 비교", self)
        self.truth_action = QAction("사용자 정답", self)
        toolbar = self.findChild(QToolBar)
        if toolbar is not None:
            toolbar.insertAction(self.save_png_action, self.redetection_action)
            toolbar.insertAction(self.save_png_action, self.truth_action)
        self.redetection_action.setEnabled(False)
        self.truth_action.setEnabled(False)
        self.redetection_action.triggered.connect(self.redetectionRequested)
        self.truth_action.triggered.connect(self.truthRequested)

    def add_bundle_change_guard(self, callback) -> None:
        if callback not in self._bundle_change_guards:
            self._bundle_change_guards.append(callback)

    def add_glass_change_guard(self, callback) -> None:
        if callback not in self._glass_change_guards:
            self._glass_change_guards.append(callback)

    def add_close_guard(self, callback) -> None:
        if callback not in self._close_guards:
            self._close_guards.append(callback)

    def load_bundle(self, source) -> bool:
        if self.bundle is not None and not self._allow(self._bundle_change_guards):
            return False
        self.bundleAboutToChange.emit()
        loaded = super().load_bundle(source)
        if loaded:
            enabled = self.bundle is not None
            self.redetection_action.setEnabled(enabled)
            self.truth_action.setEnabled(enabled)
            self.bundleChanged.emit(self.bundle)
            self.sourceVideoChanged.emit(self.active_video_path)
            self.selectedGlassChanged.emit(self.selected_glass_id)
        return loaded

    def _open_resolved_video(self, path, timestamp: float, *, auto: bool) -> bool:
        opened = super()._open_resolved_video(path, timestamp, auto=auto)
        if opened:
            self.sourceVideoChanged.emit(self.active_video_path)
        return opened

    def _glass_changed(self, glass_id: str) -> None:
        previous = self.selected_glass_id
        if previous and glass_id != previous and not self._allow(self._glass_change_guards):
            combo = self.navigation.glass_combo
            index = combo.findData(previous)
            if index >= 0:
                combo.blockSignals(True)
                combo.setCurrentIndex(index)
                combo.blockSignals(False)
            return
        super()._glass_changed(glass_id)
        self.selectedGlassChanged.emit(glass_id)

    def select_glass(self, glass_id: str) -> bool:
        index = self.navigation.glass_combo.findData(glass_id)
        if index < 0:
            return False
        self.navigation.glass_combo.setCurrentIndex(index)
        return self.selected_glass_id == glass_id

    def closeEvent(self, event) -> None:
        if not self._allow(self._close_guards):
            event.ignore()
            return
        self.viewerClosing.emit()
        super().closeEvent(event)

    @staticmethod
    def _allow(guards) -> bool:
        for guard in tuple(guards):
            try:
                if not bool(guard()):
                    return False
            except Exception:
                return False
        return True
