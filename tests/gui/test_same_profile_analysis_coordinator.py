from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.same_profile_analysis_coordinator import SameProfileAnalysisCoordinator


class _Prepared:
    def __init__(self):
        self.frame = np.zeros((24, 32, 3), dtype=np.uint8)
        self.frame_index = 0
        self.timestamp_sec = 0.01
        self.closed = False

    def close(self):
        self.closed = True


class _Timer:
    def __init__(self):
        self.stopped = 0

    def stop(self):
        self.stopped += 1


class _Undo:
    def __init__(self):
        self.cleared = 0

    def clear(self):
        self.cleared += 1


class _Canvas:
    def __init__(self):
        self.frame = None
        self.reset_view = None

    def set_frame(self, frame, *, reset_view=False):
        self.frame = frame
        self.reset_view = reset_view


class _Transport:
    def __init__(self):
        self.position = None

    def set_position(self, timestamp, duration, frame_index):
        self.position = (timestamp, duration, frame_index)


class _Preflight:
    def __init__(self):
        self.reset_count = 0

    def reset(self):
        self.reset_count += 1


class _Workbench:
    def __init__(self, state=WorkbenchState.DRAFT):
        self.state = state
        self.prepared = None
        self.prepare_calls = []
        self.commit_calls = []
        self.session = SimpleNamespace(
            video_metadata=VideoMetadata("new.mp4", 320, 240, 10.0, 5.0, 50, "fake")
        )

    def prepare_same_profile_video(self, recipe, sampling_fps, selected):
        self.prepare_calls.append((recipe, sampling_fps, selected))
        self.prepared = _Prepared()
        return self.prepared

    def commit_same_profile_video(self, prepared):
        self.commit_calls.append(prepared)
        self.state = WorkbenchState.DRAFT


class _Window(QMainWindow):
    applicationCloseAccepted = Signal()

    def __init__(self, state=WorkbenchState.DRAFT):
        super().__init__()
        self.workbench = _Workbench(state)
        self.play_timer = _Timer()
        self.preview_timer = _Timer()
        self.undo_stack = _Undo()
        self.canvas = _Canvas()
        self.transport = _Transport()
        self.preflight_coordinator = _Preflight()
        self.current_frame = np.ones((2, 2, 3), dtype=np.uint8)
        self.current_frame_index = 9
        self.current_time = 3.0
        self.last_result_path = "old-result"
        self._last_validation = object()
        self.calls = []

    def _invalidate_preview(self, message):
        self.calls.append(("invalidate", message))

    def _refresh_all(self):
        self.calls.append(("refresh_all",))

    def _refresh_inline_validation(self):
        self.calls.append(("validation",))

    def schedule_preview(self):
        self.calls.append(("preview",))


def _bundle(tmp_path):
    return SimpleNamespace(
        source_video_path=str(tmp_path / "source.mp4"),
        root=tmp_path / "bundle",
        recipe=object(),
        session=SimpleNamespace(sampling_fps=2.0),
    )


def test_analyzing_workbench_is_rejected_before_file_selection(qtbot, tmp_path, monkeypatch):
    window = _Window(WorkbenchState.ANALYZING)
    qtbot.addWidget(window)
    selected = []
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: selected.append(True) or ("new.mp4", ""))
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    coordinator = SameProfileAnalysisCoordinator(window)
    assert coordinator.start(_bundle(tmp_path)) is False
    assert selected == []
    assert window.workbench.prepare_calls == []
    assert window.workbench.state == WorkbenchState.ANALYZING


def test_replacement_confirmation_cancel_closes_candidate_and_preserves_workbench(qtbot, tmp_path, monkeypatch):
    window = _Window(WorkbenchState.ANALYZED)
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("new.mp4", ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.No)
    coordinator = SameProfileAnalysisCoordinator(window)
    assert coordinator.start(_bundle(tmp_path)) is False
    assert window.workbench.prepared.closed is True
    assert window.workbench.commit_calls == []
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == "old-result"
    assert window.undo_stack.cleared == 0
    assert window.preflight_coordinator.reset_count == 0


def test_success_applies_prepared_candidate_and_resets_session_ui_state(qtbot, tmp_path, monkeypatch):
    window = _Window(WorkbenchState.VALIDATED)
    qtbot.addWidget(window)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: ("new.mp4", ""))
    monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.StandardButton.Yes)
    coordinator = SameProfileAnalysisCoordinator(window)
    assert coordinator.start(_bundle(tmp_path)) is True
    prepared = window.workbench.prepared
    assert window.workbench.commit_calls == [prepared]
    assert window.workbench.state == WorkbenchState.DRAFT
    assert window.play_timer.stopped == 1
    assert window.preview_timer.stopped == 1
    assert window.undo_stack.cleared == 1
    assert window.last_result_path == ""
    assert window.current_frame is prepared.frame
    assert window.canvas.reset_view is True
    assert window.current_frame_index == 0
    assert window.current_time == 0.01
    assert window.transport.position == (0.01, 5.0, 0)
    assert window._last_validation is None
    assert window.preflight_coordinator.reset_count == 1
    assert ("refresh_all",) in window.calls
    assert ("validation",) in window.calls
    assert ("preview",) in window.calls
    assert prepared.closed is True
