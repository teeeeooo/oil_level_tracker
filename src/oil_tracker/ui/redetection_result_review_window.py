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
    viewerClosing = Signal()

    def _build_ui(self) -> None:
        super()._build_ui()
        self.redetection_action = QAction("부분 재검출과 비교", self)
        toolbar = self.findChild(QToolBar)
        if toolbar is not None:
            toolbar.insertAction(self.save_png_action, self.redetection_action)
        self.redetection_action.setEnabled(False)
        self.redetection_action.triggered.connect(self.redetectionRequested)

    def load_bundle(self, source) -> bool:
        loaded = super().load_bundle(source)
        if loaded:
            self.bundleAboutToChange.emit()
            self.redetection_action.setEnabled(self.bundle is not None)
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
        super()._glass_changed(glass_id)
        self.selectedGlassChanged.emit(glass_id)

    def closeEvent(self, event) -> None:
        self.viewerClosing.emit()
        super().closeEvent(event)
