from __future__ import annotations

from types import SimpleNamespace
import time

from PySide6.QtCore import QCoreApplication

from oil_tracker.application.services.detector_settings import detector_setting_fields
from oil_tracker.application.services.redetection_service import RedetectionCancelled
from oil_tracker.domain.recipe import DetectorSettings
from oil_tracker.domain.redetection import RedetectionMode, RedetectionStatus
from oil_tracker.ui.controllers.redetection_controller import RedetectionController
from oil_tracker.ui.redetection_comparison_window import RedetectionComparisonWindow
from oil_tracker.ui.widgets.detector_settings_editor import DetectorSettingsEditor
from redetection_fixtures import make_bundle


class FakeWorkspace:
    def __init__(self, name):
        self.name = name
        self.cleaned = False
        self.repository = None

    def cleanup(self):
        self.cleaned = True


class FakeService:
    def __init__(self, *, delay=0.0):
        self.delay = delay
        self.policy = SimpleNamespace()
        self.calls = []
        self.workspaces = []

    def run(
        self,
        request,
        official_bundle,
        *,
        official_candidate_timestamps=(),
        progress=None,
        cancellation=None,
    ):
        self.calls.append(request.generation)
        if progress is not None:
            progress(
                SimpleNamespace(
                    generation=request.generation,
                    stage="redetection",
                    processed_samples=0,
                    total_samples=1,
                    current_timestamp_sec=1.0,
                    message="재검출",
                    fraction=0.0,
                )
            )
        deadline = time.monotonic() + self.delay
        while time.monotonic() < deadline:
            if cancellation is not None and cancellation.cancelled:
                raise RedetectionCancelled("cancelled")
            time.sleep(0.002)
        if cancellation is not None and cancellation.cancelled:
            raise RedetectionCancelled("cancelled")
        workspace = FakeWorkspace(f"workspace-{request.generation}")
        self.workspaces.append(workspace)
        result = SimpleNamespace(request=request)
        return SimpleNamespace(result=result, workspace=workspace)


def _request(generation, mode=RedetectionMode.CURRENT):
    return SimpleNamespace(generation=generation, mode=mode)


def test_editor_displays_every_detector_setting_and_noop_state(qtbot):
    editor = DetectorSettingsEditor(DetectorSettings())
    qtbot.addWidget(editor)
    assert editor.table.rowCount() == len(detector_setting_fields()) == 29
    assert editor.changed_field_names() == ()
    assert editor.validation_errors() == {}
    assert editor.changed_count.text() == "변경 0개"
    assert editor.table.horizontalScrollBar() is not None


def test_editor_change_count_search_reset_one_and_reset_all(qtbot):
    editor = DetectorSettingsEditor(DetectorSettings())
    qtbot.addWidget(editor)
    canny = editor._editors["canny_low"]
    weight = editor._editors["weight_edge"]
    canny.setValue(40)
    weight.setValue(0.33)
    assert set(editor.changed_field_names()) == {"canny_low", "weight_edge"}
    assert editor.changed_count.text() == "변경 2개"
    editor.search.setText("score weight")
    assert editor.table.isRowHidden(editor._rows["canny_low"])
    assert not editor.table.isRowHidden(editor._rows["weight_edge"])
    editor.table.selectRow(editor._rows["weight_edge"])
    editor.reset_selected_field()
    assert editor.changed_field_names() == ("canny_low",)
    editor.reset_to_baseline()
    assert editor.changed_field_names() == ()


def test_editor_invalid_snapshot_emits_korean_validation(qtbot):
    editor = DetectorSettingsEditor(DetectorSettings())
    qtbot.addWidget(editor)
    editor._temporary = DetectorSettings(canny_low=200, canny_high=100)
    editor._sync_editors()
    editor._refresh_state()
    assert "canny_high" in editor.validation_errors()
    assert "재검출을 실행할 수 없습니다" in editor.validation_label.text()


def test_comparison_window_has_required_tabs_and_mode_limitations(qtbot, tmp_path):
    bundle = make_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    window = RedetectionComparisonWindow(glass.detector_settings)
    qtbot.addWidget(window)
    window.set_context(bundle, glass, bundle.source_video_path, 3.0)
    assert [window.tabs.tabText(index) for index in range(window.tabs.count())] == [
        "요약",
        "Tracking 비교",
        "후보와 점수",
        "Artifact 비교",
        "Event·판정 비교",
        "설정 적용",
    ]
    assert window.current_mode() is RedetectionMode.CURRENT
    assert not window.before.isEnabled()
    window.mode.setCurrentIndex(1)
    assert window.current_mode() is RedetectionMode.SHORT
    assert window.before.isEnabled() and window.after.isEnabled()
    window.set_status(RedetectionStatus.SETTINGS_STALE, "설정 변경됨 — 다시 실행 필요")
    assert "다시 실행 필요" in window.state_label.text()
    assert window.run_button.isEnabled()


def test_window_disables_run_without_source_or_with_invalid_settings(qtbot, tmp_path):
    bundle = make_bundle(tmp_path)
    glass = bundle.recipe.glasses[0]
    window = RedetectionComparisonWindow(glass.detector_settings)
    qtbot.addWidget(window)
    window.set_context(bundle, glass, "", 3.0)
    assert not window.run_button.isEnabled()
    window.set_context(bundle, glass, bundle.source_video_path, 3.0)
    assert window.run_button.isEnabled()
    window.settings_editor._temporary = DetectorSettings(canny_low=200, canny_high=100)
    window.settings_editor._sync_editors()
    window.settings_editor._refresh_state()
    assert not window.run_button.isEnabled()


def test_async_controller_emits_started_progress_completed_without_blocking(qtbot):
    service = FakeService(delay=0.03)
    controller = RedetectionController(service)
    completed = []
    progress = []
    controller.completed.connect(completed.append)
    controller.progress.connect(progress.append)
    controller.generation = 1
    controller.start(_request(1), object())
    assert controller.running
    qtbot.waitUntil(lambda: bool(completed), timeout=3000)
    assert service.calls == [1]
    assert progress and progress[0].generation == 1
    assert completed[0].request.generation == 1
    controller.close()


def test_controller_rapid_rerun_cancels_first_and_only_completes_latest(qtbot):
    service = FakeService(delay=0.08)
    controller = RedetectionController(service)
    completed = []
    cancelled = []
    controller.completed.connect(completed.append)
    controller.cancelled.connect(cancelled.append)
    controller.generation = 1
    controller.start(_request(1), object())
    qtbot.waitUntil(lambda: controller.running, timeout=1000)
    controller.generation = 2
    controller.start(_request(2), object())
    qtbot.waitUntil(lambda: bool(completed), timeout=5000)
    assert service.calls == [1, 2]
    assert completed[-1].request.generation == 2
    assert all(result.request.generation == 2 for result in completed)
    assert 1 not in cancelled  # stale cancellation signal is intentionally suppressed
    controller.close()


def test_controller_new_run_cleans_previous_workspace(qtbot):
    service = FakeService()
    controller = RedetectionController(service)
    completed = []
    controller.completed.connect(completed.append)
    controller.generation = 1
    controller.start(_request(1), object())
    qtbot.waitUntil(lambda: len(completed) == 1, timeout=3000)
    first_workspace = service.workspaces[0]
    controller.generation = 2
    controller.start(_request(2), object())
    qtbot.waitUntil(lambda: len(completed) == 2, timeout=3000)
    assert first_workspace.cleaned
    second_workspace = service.workspaces[1]
    controller.close()
    assert second_workspace.cleaned


def test_controller_cancel_reports_current_generation(qtbot):
    service = FakeService(delay=0.2)
    controller = RedetectionController(service)
    cancelled = []
    controller.cancelled.connect(cancelled.append)
    controller.generation = 3
    controller.start(_request(3), object())
    controller.cancel()
    qtbot.waitUntil(lambda: cancelled == [3], timeout=3000)
    assert not controller.running
    controller.close()
