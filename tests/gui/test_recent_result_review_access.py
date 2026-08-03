from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QListWidget, QMainWindow, QPushButton, QWidget

from oil_tracker.adapters.storage.recent_result_history import RecentResultHistory
from oil_tracker.ui.result_review_coordinator import ResultReviewCoordinator


class _Workbench(QMainWindow):
    applicationCloseAccepted = Signal()

    def __init__(self):
        super().__init__()
        self.actions = {}
        self.last_result_path = ""

    def closeEvent(self, event):
        super().closeEvent(event)
        if event.isAccepted():
            self.applicationCloseAccepted.emit()


class _Viewer(QWidget):
    sameProfileRequested = Signal(object)
    truthMarkerRequested = Signal(str)
    truthRequested = Signal()
    bundleChanged = Signal(object)
    sourceVideoChanged = Signal(object)
    selectedGlassChanged = Signal(str)
    viewerClosing = Signal()

    def __init__(self, bundles, parent=None):
        super().__init__(parent)
        self.bundles = bundles
        self.loaded = []
        self.bundle_guards = []
        self.glass_guards = []
        self.close_guards = []
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
        key = str(Path(path))
        self.loaded.append(key)
        self.bundle = self.bundles.get(key)
        return self.bundle is not None


def _bundle(root: Path, *, run_name: str, profile_name: str = "Profile", source="video.mp4"):
    root.mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(
        root=root,
        run_name=run_name,
        recipe=SimpleNamespace(name=profile_name),
        source_video_path=source,
    )


def _make_coordinator(qtbot, history, bundles):
    window = _Workbench()
    qtbot.addWidget(window)
    viewers = []

    def factory(parent):
        viewer = _Viewer(bundles, parent)
        viewers.append(viewer)
        qtbot.addWidget(viewer)
        return viewer

    coordinator = ResultReviewCoordinator(
        window,
        viewer_factory=factory,
        recent_result_history=history,
    )
    return window, coordinator, viewers


def _schedule_dialog_action(action):
    def run():
        dialog = next(
            widget
            for widget in QApplication.topLevelWidgets()
            if widget.windowTitle() == "결과 검토 열기"
        )
        action(dialog)

    QTimer.singleShot(0, run)


def test_restart_recovers_recent_entries_and_selected_recent_opens_authoritative_bundle(qtbot, tmp_path):
    storage = tmp_path / "recent.json"
    first_cached = _bundle(tmp_path / "first", run_name="cached first", profile_name="P1")
    second = _bundle(tmp_path / "second", run_name="second", profile_name="P2")
    original = RecentResultHistory(storage)
    original.record_bundle(first_cached)
    original.record_bundle(second)

    first_truth = SimpleNamespace(
        root=first_cached.root,
        run_name="bundle truth first",
        recipe=SimpleNamespace(name="Authoritative Profile"),
        source_video_path="truth.mp4",
    )
    restarted = RecentResultHistory(storage)
    window, coordinator, viewers = _make_coordinator(
        qtbot,
        restarted,
        {str(first_cached.root): first_truth, str(second.root): second},
    )

    def select_older(dialog):
        recent_list = dialog.findChild(QListWidget, "recentResultList")
        assert recent_list is not None
        assert recent_list.count() == 2
        assert "cached first" in recent_list.item(1).text()
        assert "P1" in recent_list.item(1).text()
        recent_list.setCurrentRow(1)
        button = dialog.findChild(QPushButton, "recentResultOpenButton")
        assert button is not None and button.isEnabled()
        button.click()

    _schedule_dialog_action(select_older)
    coordinator.open_dialog()

    assert viewers[0].loaded == [str(first_cached.root)]
    assert window.last_result_path == ""
    refreshed = restarted.entries()
    assert refreshed[0].path == str(first_cached.root)
    assert refreshed[0].run_name == "bundle truth first"
    assert refreshed[0].profile_name == "Authoritative Profile"
    coordinator.close()


def test_stale_recent_entry_is_disabled_without_blocking_other_history(qtbot, tmp_path):
    storage = tmp_path / "recent.json"
    valid = _bundle(tmp_path / "valid", run_name="valid")
    stale = _bundle(tmp_path / "stale", run_name="stale")
    history = RecentResultHistory(storage)
    history.record_bundle(valid)
    history.record_bundle(stale)
    stale.root.rmdir()

    window, coordinator, viewers = _make_coordinator(
        qtbot,
        RecentResultHistory(storage),
        {str(valid.root): valid},
    )

    def open_first_available(dialog):
        recent_list = dialog.findChild(QListWidget, "recentResultList")
        assert recent_list is not None
        assert "경로를 찾을 수 없음" in recent_list.item(0).text()
        assert not bool(recent_list.item(0).flags() & Qt.ItemFlag.ItemIsEnabled)
        button = dialog.findChild(QPushButton, "recentResultOpenButton")
        assert button is not None and button.isEnabled()
        button.click()

    _schedule_dialog_action(open_first_available)
    coordinator.open_dialog()

    assert viewers[0].loaded == [str(valid.root)]
    assert window.last_result_path == ""
    coordinator.close()


def test_manual_folder_open_remains_available_and_does_not_replace_last_result_path(
    qtbot, tmp_path, monkeypatch
):
    storage = tmp_path / "recent.json"
    manual = _bundle(tmp_path / "manual", run_name="manual truth", profile_name="Manual Profile")
    current = tmp_path / "current-analysis"
    current.mkdir()
    history = RecentResultHistory(storage)
    window, coordinator, viewers = _make_coordinator(
        qtbot,
        history,
        {str(manual.root): manual},
    )
    window.last_result_path = str(current)
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *_args, **_kwargs: str(manual.root),
    )

    def choose_manual(dialog):
        button = dialog.findChild(QPushButton, "otherResultFolderButton")
        assert button is not None
        button.click()

    _schedule_dialog_action(choose_manual)
    coordinator.open_dialog()

    assert viewers[0].loaded == [str(manual.root)]
    assert window.last_result_path == str(current)
    entries = history.entries()
    assert entries[0].path == str(manual.root)
    assert entries[0].run_name == "manual truth"
    coordinator.close()
