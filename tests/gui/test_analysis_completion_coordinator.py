from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtWidgets import QMainWindow, QMessageBox

from oil_tracker.domain.enums import ResultState, WorkbenchState
from oil_tracker.domain.results import AnalysisResult
from oil_tracker.ui.analysis_completion_coordinator import AnalysisCompletionCoordinator
from oil_tracker.ui.result_actions import ResultActionError


class _Progress:
    def __init__(self):
        self.accepted = False

    def accept(self):
        self.accepted = True


class _Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.workbench = SimpleNamespace(state=WorkbenchState.DRAFT)
        self.last_result_path = ""
        self.progress_dialog = _Progress()
        self.update_count = 0

    def _update_state(self):
        self.update_count += 1


class _ReviewCoordinator:
    def __init__(self, succeeds=False):
        self.succeeds = succeeds
        self.paths = []

    def open_bundle(self, path):
        self.paths.append(path)
        return self.succeeds


class _SameProfileCoordinator:
    def __init__(self):
        self.bundles = []
        self.closed = False

    def start(self, bundle):
        self.bundles.append(bundle)

    def close(self):
        self.closed = True


class _Actions:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def open_report(self, path):
        self.calls.append(("report", path))
        if self.fail:
            raise ResultActionError("report failed")

    def open_folder(self, path):
        self.calls.append(("folder", path))
        if self.fail:
            raise ResultActionError("folder failed")


class _BundleReader:
    def __init__(self, bundle):
        self.bundle = bundle
        self.paths = []

    def read(self, path):
        self.paths.append(path)
        return self.bundle


def _result():
    return AnalysisResult(
        run_id="run",
        overall_state=ResultState.PASS,
        glass_results=[],
        started_at="start",
        completed_at="end",
    )


def test_analysis_is_committed_before_dialog_and_close_does_not_change_result(qtbot, tmp_path):
    window = _Window()
    qtbot.addWidget(window)
    coordinator = AnalysisCompletionCoordinator(
        window,
        _ReviewCoordinator(True),
        _SameProfileCoordinator(),
        _Actions(),
        _BundleReader(object()),
    )
    output = str(tmp_path / "bundle")
    coordinator.analysis_completed(_result(), output)
    assert window.progress_dialog.accepted is True
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output
    assert window.update_count == 1
    assert coordinator.dialog is not None
    coordinator.close()
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output


def test_viewer_and_report_failures_preserve_analyzed_state(qtbot, tmp_path, monkeypatch):
    window = _Window()
    qtbot.addWidget(window)
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: warnings.append(args[2]) or QMessageBox.StandardButton.Ok)
    review = _ReviewCoordinator(False)
    actions = _Actions(fail=True)
    coordinator = AnalysisCompletionCoordinator(
        window,
        review,
        _SameProfileCoordinator(),
        actions,
        _BundleReader(object()),
    )
    output = str(tmp_path / "bundle")
    coordinator.analysis_completed(_result(), output)
    coordinator._open_viewer(output)
    coordinator._open_report(output)
    coordinator._open_folder(output)
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output
    assert len(warnings) == 3
    coordinator.close()


def test_same_profile_action_uses_reloaded_bundle(qtbot, tmp_path):
    window = _Window()
    qtbot.addWidget(window)
    bundle = object()
    reader = _BundleReader(bundle)
    same_profile = _SameProfileCoordinator()
    coordinator = AnalysisCompletionCoordinator(
        window,
        _ReviewCoordinator(True),
        same_profile,
        _Actions(),
        reader,
    )
    output = str(tmp_path / "bundle")
    coordinator._same_profile(output)
    assert reader.paths == [output]
    assert same_profile.bundles == [bundle]


def test_duplicate_action_key_is_ignored_while_action_is_active(qtbot):
    window = _Window()
    qtbot.addWidget(window)
    coordinator = AnalysisCompletionCoordinator(
        window,
        _ReviewCoordinator(True),
        _SameProfileCoordinator(),
        _Actions(),
        _BundleReader(object()),
    )
    calls = []

    def outer():
        calls.append("outer")
        coordinator._run_once("review", lambda: calls.append("duplicate"))

    coordinator._run_once("review", outer)
    assert calls == ["outer"]
