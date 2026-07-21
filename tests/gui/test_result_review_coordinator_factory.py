from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow, QWidget

from oil_tracker.ui.result_review_coordinator import ResultReviewCoordinator


class _Workbench(QMainWindow):
    def __init__(self):
        super().__init__()
        self.actions = {}
        self.last_result_path = ""


class _Viewer(QWidget):
    sameProfileRequested = Signal(object)
    truthMarkerRequested = Signal(str)
    truthRequested = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    viewerClosing = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loaded = []
        self.bundle_guards = []
        self.glass_guards = []
        self.close_guards = []
        self.closed = False
        self.bundle = None
        self.active_video_path = None
        self.current_source_image = None
        self.current_frame_index = 0
        self.current_time = 0.0
        self.selected_glass_id = ""
        self.debug_repository = None

    def add_bundle_change_guard(self, callback):
        self.bundle_guards.append(callback)

    def add_glass_change_guard(self, callback):
        self.glass_guards.append(callback)

    def add_close_guard(self, callback):
        self.close_guards.append(callback)

    def set_truth_annotations(self, _annotations, *, selected_id=""):
        self.selected_truth_id = selected_id

    def load_bundle(self, path):
        self.loaded.append(str(path))
        return True

    def closeEvent(self, event):
        self.closed = True
        super().closeEvent(event)


def test_injected_viewer_factory_receives_workbench_and_reuses_single_window(qtbot):
    workbench = _Workbench()
    qtbot.addWidget(workbench)
    created = []

    def factory(parent):
        viewer = _Viewer(parent)
        created.append((parent, viewer))
        qtbot.addWidget(viewer)
        return viewer

    coordinator = ResultReviewCoordinator(workbench, viewer_factory=factory)
    assert coordinator.open_bundle("first")
    first = coordinator.viewer
    assert coordinator.open_bundle("second")
    assert coordinator.viewer is first
    assert created == [(workbench, first)]
    assert first.loaded == ["first", "second"]
    assert coordinator.truth_coordinator is not None
    coordinator.close()
    assert coordinator.viewer is None
    assert coordinator.truth_coordinator is None
    assert first.closed


def test_workbench_close_cleans_injected_viewer(qtbot):
    workbench = _Workbench()
    qtbot.addWidget(workbench)
    viewer_holder = []

    def factory(parent):
        viewer = _Viewer(parent)
        viewer_holder.append(viewer)
        qtbot.addWidget(viewer)
        return viewer

    coordinator = ResultReviewCoordinator(workbench, viewer_factory=factory)
    coordinator.open_bundle("bundle")
    workbench.close()
    qtbot.wait(1)
    assert coordinator.viewer is None
    assert viewer_holder[0].closed
