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


class _RecentHistory:
    def __init__(self, fail=False):
        self.fail = fail
        self.paths = []

    def register_path(self, path):
        self.paths.append(path)
        if self.fail:
            raise OSError("history unavailable")


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
    history = _RecentHistory()
    coordinator = AnalysisCompletionCoordinator(
        window,
        _ReviewCoordinator(True),
        _SameProfileCoordinator(),
        _Actions(),
        _BundleReader(object()),
        recent_result_history=history,
    )
    output = str(tmp_path / "bundle")
    coordinator.analysis_completed(_result(), output)
    assert window.progress_dialog.accepted is True
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output
    assert history.paths == [output]
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


def test_recent_history_failure_does_not_regress_completed_analysis(qtbot, tmp_path):
    window = _Window()
    qtbot.addWidget(window)
    history = _RecentHistory(fail=True)
    coordinator = AnalysisCompletionCoordinator(
        window,
        _ReviewCoordinator(True),
        _SameProfileCoordinator(),
        _Actions(),
        _BundleReader(object()),
        recent_result_history=history,
    )
    output = str(tmp_path / "bundle")

    coordinator.analysis_completed(_result(), output)

    assert history.paths == [output]
    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output
    assert coordinator.dialog is not None
    coordinator.close()


class _FailingBundleReader:
    def __init__(self):
        self.paths = []

    def read(self, path):
        self.paths.append(path)
        raise OSError("bundle summary unavailable")


def test_completed_summary_uses_finalized_bundle_not_mutable_workbench(qtbot, tmp_path):
    window = _Window()
    qtbot.addWidget(window)
    window.workbench.recipe = SimpleNamespace(name="mutable profile")
    window.workbench.session = SimpleNamespace(run_name="mutable run", input_video_path="mutable.mp4")
    bundle = SimpleNamespace(
        run_name="final run",
        recipe=SimpleNamespace(name="final profile"),
        source_video_path="final-source.mp4",
    )
    reader = _BundleReader(bundle)
    coordinator = AnalysisCompletionCoordinator(
        window, _ReviewCoordinator(True), _SameProfileCoordinator(), _Actions(), reader
    )
    output = str(tmp_path / "completed-bundle")
    coordinator.analysis_completed(_result(), output)

    window.workbench.recipe.name = "later profile"
    window.workbench.session.run_name = "later run"
    window.workbench.session.input_video_path = "later.mp4"
    assert coordinator.dialog.run_name_label.text() == "final run"
    assert coordinator.dialog.profile_name_label.text() == "final profile"
    assert coordinator.dialog.source_video_label.text() == "final-source.mp4"
    assert coordinator.dialog.path_label.text() == output
    assert reader.paths == [output]
    coordinator.close()


def test_bundle_summary_read_failure_degrades_without_revoking_completion(qtbot, tmp_path):
    window = _Window()
    qtbot.addWidget(window)
    reader = _FailingBundleReader()
    coordinator = AnalysisCompletionCoordinator(
        window, _ReviewCoordinator(True), _SameProfileCoordinator(), _Actions(), reader
    )
    output = str(tmp_path / "completed-bundle")

    coordinator.analysis_completed(_result(), output)

    assert window.workbench.state == WorkbenchState.ANALYZED
    assert window.last_result_path == output
    assert coordinator.dialog is not None
    assert coordinator.dialog.run_name_label.text() == "이름 없음 (현재 시험 이름 미지정)"
    assert coordinator.dialog.profile_name_label.text() == "확인할 수 없음"
    assert coordinator.dialog.source_video_label.text() == "확인할 수 없음"
    assert "식별 메타데이터를 읽지 못했습니다" in coordinator.dialog.metadata_status_label.text()
    assert coordinator.dialog.path_label.text() == output
    assert reader.paths == [output]
    coordinator.close()
