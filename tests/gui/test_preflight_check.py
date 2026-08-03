from __future__ import annotations

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.preflight import (
    PreflightDetectionResult,
    PreflightGlassSummary,
    PreflightProgress,
    PreflightResult,
    PreflightSamplePoint,
    PreflightStatus,
    preflight_context_key,
)
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.enums import FillState, WorkbenchState
from oil_tracker.domain.session import VideoMetadata
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.preflight_coordinator import PreflightCoordinator
from oil_tracker.ui.widgets.preflight_panel import PreflightPanel


class DummyPreviewController(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def __init__(self):
        super().__init__()
        self.invalidations = 0
        self.requests = []

    def invalidate(self):
        self.invalidations += 1

    def request(self, frame, glass, frame_index, time_sec):
        self.requests.append((glass.id, frame_index, time_sec, id(frame)))


class DummyAnalysisController(QObject):
    progress = Signal(object)
    completed = Signal(object, str)
    failed = Signal(str)
    cancelled = Signal()

    def start(self, *_args):
        pass

    def cancel(self):
        pass


class DummyPreflightController(QObject):
    started = Signal()
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self):
        super().__init__()
        self.starts = []
        self.cancel_count = 0
        self.invalidations = 0

    def start(self, recipe, session):
        self.starts.append((recipe, session))
        self.started.emit()

    def cancel(self):
        self.cancel_count += 1
        self.cancelled.emit()

    def invalidate(self):
        self.invalidations += 1


class DummyRenderer:
    def export(self, *_args):
        return []


class FakeVideoReader:
    def __init__(self, metadata):
        self.metadata = metadata
        self.targets = []

    def read_at(self, timestamp):
        self.targets.append(timestamp)
        frame_index = int(round(timestamp * self.metadata.fps))
        return np.zeros((480, 640, 3), dtype=np.uint8), frame_index, float(timestamp)

    def close(self):
        pass


def _workbench() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
    )


def _window(qtbot):
    workbench = _workbench()
    preview = DummyPreviewController()
    window = MainWindow(workbench, preview, DummyAnalysisController(), DummyRenderer())
    window._confirm_unsaved_profile_close = lambda: QMessageBox.StandardButton.Discard
    qtbot.addWidget(window)
    window.show()
    workbench.new_document(640, 480)
    first = workbench.add_glass()
    second = workbench.add_glass()
    metadata = VideoMetadata("video.mp4", 640, 480, 10.0, 10.0, 100)
    workbench.session.input_video_path = metadata.path
    workbench.session.video_metadata = metadata
    workbench.session.analysis_start_sec = 0.0
    workbench.session.analysis_end_sec = 10.0
    workbench.session.compressor_start_sec = 2.0
    workbench.session.sampling_fps = 2.0
    reader = FakeVideoReader(metadata)
    workbench.video_reader = reader
    window._refresh_all()
    window._refresh_inline_validation()
    window._load_frame(0.0)
    return window, workbench, preview, reader, first, second


def _result(workbench, *, status=PreflightStatus.NORMAL, reason="정상적으로 검출되었습니다"):
    samples = []
    summaries = []
    enabled = [glass for glass in workbench.recipe.glasses if glass.enabled]
    for index, glass in enumerate(enabled):
        sample = PreflightDetectionResult(
            glass_id=glass.id,
            glass_name=glass.name,
            sample_point=PreflightSamplePoint(
                labels=("분석 구간 50%",),
                requested_timestamps=(3.2 + index,),
                requested_timestamp=3.2 + index,
                actual_timestamp=3.2 + index,
                frame_index=32 + index * 10,
            ),
            fill_state=FillState.PARTIAL_VISIBLE,
            confidence=0.88,
            oil_level_y=200.0,
            oil_level_px_from_zero=10.0,
            oil_level_mm_from_zero=None,
            foam_detected=False,
            flags=(),
            status=status,
            reason=reason,
        )
        samples.append(sample)
        summaries.append(
            PreflightGlassSummary(
                glass.id,
                glass.name,
                0.88,
                1 if status == PreflightStatus.NORMAL else 0,
                1 if status == PreflightStatus.REVIEW else 0,
                1 if status == PreflightStatus.FAILURE else 0,
                None if status == PreflightStatus.NORMAL else sample.sample_point.actual_timestamp,
                "" if status == PreflightStatus.NORMAL else reason,
                False,
            )
        )
    session = workbench.session
    metadata = session.video_metadata
    return PreflightResult(
        overall_status=status,
        samples=tuple(samples),
        glass_summaries=tuple(summaries),
        video_path=session.input_video_path,
        context_key=preflight_context_key(workbench.recipe, session),
        analysis_start_sec=session.analysis_start_sec,
        analysis_end_sec=session.effective_end_sec(),
        compressor_start_sec=session.compressor_start_sec,
        recipe_id=workbench.recipe.recipe_id,
        recipe_name=workbench.recipe.name,
        enabled_glass_ids=tuple(glass.id for glass in enabled),
        video_fps=metadata.fps,
        video_duration_sec=metadata.duration_sec,
    )


def test_panel_states_summary_and_result_row_activation(qtbot):
    panel = PreflightPanel()
    qtbot.addWidget(panel)
    panel.show()
    workbench = _workbench()
    workbench.new_document(640, 480)
    workbench.add_glass()
    metadata = VideoMetadata("video.mp4", 640, 480, 10.0, 10.0, 100)
    workbench.session.input_video_path = metadata.path
    workbench.session.video_metadata = metadata
    workbench.session.analysis_end_sec = 10.0
    workbench.session.compressor_start_sec = 2.0

    assert panel.status_label.text() == "점검하지 않음"
    panel.set_running()
    panel.set_progress(PreflightProgress(1, 3, "분석 시작", "유면 관찰창 1"))
    assert panel.status_label.text() == "진행 중"
    assert panel.progress_bar.value() == 1

    result = _result(workbench, status=PreflightStatus.REVIEW, reason="반사광 확인 필요")
    panel.set_result(result)
    assert panel.status_label.text() == "확인 필요"
    assert panel.result_table.rowCount() == 1
    assert panel.summary_table.rowCount() == 1
    assert panel.summary_table.item(0, 3).text() == "1"

    with qtbot.waitSignal(panel.resultActivated) as activated:
        panel.result_table.selectRow(0)
    assert activated.args[0] == workbench.recipe.glasses[0].id
    assert activated.args[1] == 3.2
    assert activated.args[2] == "반사광 확인 필요"

    panel.set_stale()
    assert panel.status_label.text() == "재점검 필요"
    assert panel.rerun_button.isVisible()


def test_coordinator_marks_result_stale_on_relevant_change_but_not_selection(qtbot):
    window, workbench, _preview, _reader, first, second = _window(qtbot)
    controller = DummyPreflightController()
    coordinator = PreflightCoordinator(window, controller)

    coordinator.start()
    assert coordinator.panel.status_label.text() == "진행 중"
    result = _result(workbench)
    controller.completed.emit(result)
    assert coordinator.panel.status_label.text() == "정상"
    assert "정상" in window.progress.preflight_status.text()

    window.select_glass(second.id)
    qtbot.wait(20)
    assert coordinator.panel.status_label.text() == "정상"

    workbench.session.analysis_end_sec = 9.0
    coordinator.schedule_context_check()
    qtbot.waitUntil(lambda: coordinator.panel.status_label.text() == "재점검 필요")
    assert workbench.selected_glass_id == second.id
    assert first.id != second.id


def test_result_row_navigation_selects_glass_seeks_video_and_requests_live_preview(qtbot):
    window, workbench, preview, reader, first, _second = _window(qtbot)
    controller = DummyPreflightController()
    coordinator = PreflightCoordinator(window, controller)
    result = _result(workbench, status=PreflightStatus.REVIEW, reason="신뢰도 확인 필요")
    coordinator.last_result = result
    coordinator.panel.set_result(result)

    target_sample = result.samples[0]
    coordinator.navigate_to_result(
        target_sample.glass_id,
        target_sample.sample_point.navigation_timestamp,
        target_sample.reason,
    )

    assert workbench.selected_glass_id == first.id
    assert window.canvas._selected_id == first.id
    assert reader.targets[-1] == target_sample.sample_point.navigation_timestamp
    qtbot.waitUntil(lambda: bool(preview.requests), timeout=2000)
    assert preview.requests[-1][0] == first.id
    assert preview.requests[-1][2] == target_sample.sample_point.navigation_timestamp


def test_cancel_rerun_and_analysis_invalidation_states(qtbot):
    window, workbench, _preview, _reader, _first, _second = _window(qtbot)
    controller = DummyPreflightController()
    coordinator = PreflightCoordinator(window, controller)

    coordinator.start()
    coordinator.panel.cancel_button.click()
    assert controller.cancel_count == 1
    assert coordinator.panel.status_label.text() == "취소됨"

    coordinator.panel.rerun_button.click()
    assert len(controller.starts) == 2
    assert coordinator.panel.status_label.text() == "진행 중"

    coordinator.last_result = _result(workbench)
    workbench.state = WorkbenchState.ANALYZING
    coordinator._analysis_action_finished()
    assert controller.invalidations >= 1
    assert coordinator.panel.status_label.text() == "재점검 필요"
