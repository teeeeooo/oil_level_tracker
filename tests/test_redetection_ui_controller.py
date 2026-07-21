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
    assert editor.table.rowCount() == len(detector_setting_fields())
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


def test_controller_latest_generation_wins_and_stale_result_is_discarded(qtbot):
    service = FakeService(delay=0.03)
    controller = RedetectionController(service)
    first = _request(1)
    second = _request(2)
    controller.start(first, SimpleNamespace(), ())
    controller.start(second, SimpleNamespace(), ())
    qtbot.waitUntil(lambda: len(service.workspaces) >= 2, timeout=3000)
    qtbot.waitUntil(lambda: controller.state.status != RedetectionStatus.RUNNING, timeout=3000)
    assert controller.state.generation == 2
    assert controller.state.status == RedetectionStatus.COMPLETE
    assert service.workspaces[0].cleaned
    assert not service.workspaces[-1].cleaned
    controller.dispose()
    assert service.workspaces[-1].cleaned


def test_window_reopen_close_and_mode_labels(qtbot, tmp_path):
    bundle = make_bundle(tmp_path)
    window = RedetectionComparisonWindow()
    qtbot.addWidget(window)
    window.set_official_bundle(bundle)
    window.show()
    QCoreApplication.processEvents()
    assert window.mode_combo.count() == 3
    assert window.run_button.text() == "재검출 실행"
    window.close()
    window.show()
    QCoreApplication.processEvents()
    assert window.mode_combo.count() == 3
    assert window.settings_editor.changed_field_names() == ()
