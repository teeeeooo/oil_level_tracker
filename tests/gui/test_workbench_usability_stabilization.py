from __future__ import annotations

import numpy as np
from PySide6.QtCore import QObject, QPoint, QPointF, QRect, Qt, Signal
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication, QDockWidget, QLabel

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.application.services.recipe_validation_service import RecipeValidationService
from oil_tracker.application.use_cases.load_recipe import LoadRecipeUseCase
from oil_tracker.application.use_cases.save_recipe import SaveRecipeUseCase
from oil_tracker.application.use_cases.validate_workbench import ValidateWorkbenchUseCase
from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.ui.controllers.workbench_controller import WorkbenchController
from oil_tracker.ui.main_window import MainWindow
from oil_tracker.ui.preflight_coordinator import PreflightCoordinator
from oil_tracker.ui.readiness import ProgressStep, ProgressStepState
from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel
from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget


class DummyPreviewController(QObject):
    previewReady = Signal(object, object)
    previewFailed = Signal(str)

    def invalidate(self):
        pass

    def request(self, *_args):
        pass


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
        self.starts = 0
        self.invalidations = 0
        self.cancels = 0

    def start(self, *_args):
        self.starts += 1
        self.started.emit()

    def cancel(self):
        self.cancels += 1
        self.cancelled.emit()

    def invalidate(self):
        self.invalidations += 1


class DummyRenderer:
    def export(self, *_args):
        return []


def _controller() -> WorkbenchController:
    repository = JsonRecipeRepository()
    validator = RecipeValidationService()
    return WorkbenchController(
        SaveRecipeUseCase(repository, validator),
        LoadRecipeUseCase(repository),
        ValidateWorkbenchUseCase(validator),
    )


def _window(qtbot):
    workbench = _controller()
    window = MainWindow(workbench, DummyPreviewController(), DummyAnalysisController(), DummyRenderer())
    qtbot.addWidget(window)
    window.resize(1280, 760)
    window.show()
    QApplication.processEvents()
    return window, workbench


def _rect_in(widget, ancestor) -> QRect:
    origin = widget.mapTo(ancestor, QPoint(0, 0))
    return QRect(origin, widget.size())


def _wheel_event(delta: int = -120) -> QWheelEvent:
    return QWheelEvent(
        QPointF(5, 5),
        QPointF(5, 5),
        QPoint(0, 0),
        QPoint(0, delta),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )


def test_progress_buttons_are_single_line_meaningful_visible_and_non_overlapping(qtbot):
    widget = WorkbenchProgressWidget()
    qtbot.addWidget(widget)
    widget.resize(1280, 90)
    widget.show()
    states = (
        ProgressStepState.COMPLETE,
        ProgressStepState.CURRENT,
        ProgressStepState.WARNING,
        ProgressStepState.ERROR,
        ProgressStepState.WAITING,
    )
    labels = ("영상 선택", "시간 설정", "Glass 설정", "설정 점검", "분석 실행")
    steps = [
        ProgressStep(key, label, state, f"{label} 상세 설명")
        for key, label, state in zip(widget._buttons, labels, states, strict=True)
    ]
    widget.set_steps(steps, has_glass_issue=True)
    QApplication.processEvents()

    symbols = ("✓", "▶", "⚠", "●", "○")
    buttons = list(widget._buttons.values())
    for button, symbol, label, state in zip(buttons, symbols, labels, states, strict=True):
        assert "\n" not in button.text()
        assert symbol in button.text()
        assert label in button.text()
        assert button.toolTip() == f"{label} 상세 설명"
        assert button.property("stepState") == state.value
        assert button.isVisible()
    for left, right in zip(buttons, buttons[1:], strict=False):
        assert not left.geometry().intersects(right.geometry())

    with qtbot.waitSignal(widget.stepActivated) as activated:
        widget._buttons["glasses"].click()
    assert activated.args == ["glasses"]


def test_workbench_layout_places_summary_left_and_separates_canvas_transport(qtbot):
    window, _workbench = _window(qtbot)
    assert window.splitter.widget(0) is window.left_panel
    assert window.splitter.widget(1) is window.center_panel
    assert window.splitter.widget(2) is window.settings
    assert window.detection_summary.parentWidget() is window.left_panel
    assert window.glass_list.parentWidget() is window.left_panel
    assert window.playback_panel.parentWidget() is window.center_panel
    assert window.canvas.parentWidget() is window.playback_panel
    assert window.transport.parentWidget() is window.playback_panel

    canvas_rect = _rect_in(window.canvas, window.playback_panel)
    transport_rect = _rect_in(window.transport, window.playback_panel)
    assert not canvas_rect.intersects(transport_rect)
    assert transport_rect.top() >= canvas_rect.bottom()
    assert window.canvas.width() >= 500
    assert window.canvas.height() >= 300
    initial_transport_height = window.transport.height()

    window.resize(1500, 900)
    QApplication.processEvents()
    canvas_rect = _rect_in(window.canvas, window.playback_panel)
    transport_rect = _rect_in(window.transport, window.playback_panel)
    assert not canvas_rect.intersects(transport_rect)
    assert transport_rect.top() >= canvas_rect.bottom()
    assert window.transport.height() > 0
    assert abs(window.transport.height() - initial_transport_height) <= 8

    splitter_rects = [_rect_in(window.splitter.widget(index), window.splitter) for index in range(3)]
    assert not splitter_rects[0].intersects(splitter_rects[1])
    assert not splitter_rects[1].intersects(splitter_rects[2])


def test_workbench_view_controls_are_ephemeral_and_explicit(qtbot):
    window, workbench = _window(qtbot)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    window.canvas.set_frame(frame, reset_view=True)
    recipe_before = workbench.recipe.to_dict()
    session_before = workbench.session.to_dict()
    profile_dirty_before = workbench.profile_has_unsaved_changes
    undo_index_before = window.undo_stack.index()

    panel = window.playback_panel
    assert panel.zoom_in_button.text() == "확대"
    assert panel.zoom_out_button.text() == "축소"
    assert panel.fit_button.text() == "맞춤"
    assert panel.actual_size_button.text() == "100%"
    hint = panel.findChild(QLabel, "canvasViewHint")
    assert hint is not None
    assert "Ctrl+휠" in hint.text()
    assert "가운데 버튼" in hint.text()

    panel.zoom_in_button.click()
    assert window.canvas.fit_mode is False
    panel.zoom_out_button.click()
    panel.actual_size_button.click()
    assert window.canvas.fit_mode is False
    panel.fit_button.click()
    assert window.canvas.fit_mode is True

    assert workbench.recipe.to_dict() == recipe_before
    assert workbench.session.to_dict() == session_before
    assert workbench.profile_has_unsaved_changes is profile_dirty_before
    assert window.undo_stack.index() == undo_index_before


def test_video_context_reset_and_same_context_frame_preserve_view_semantics(qtbot, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    from oil_tracker.domain.session import VideoMetadata

    class Reader:
        def __init__(self, path):
            self.metadata = VideoMetadata(str(path), 1280, 720, 30.0, 10.0, 300, "fake")

        def read_at(self, timestamp):
            return np.zeros((720, 1280, 3), dtype=np.uint8), int(timestamp * 30), float(timestamp)

        def close(self):
            pass

    window, workbench = _window(qtbot)
    workbench.reader_factory = Reader
    window.canvas.set_frame(np.zeros((720, 1280, 3), dtype=np.uint8), reset_view=True)
    window.canvas.zoom_in()
    assert window.canvas.fit_mode is False
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args, **_kwargs: ("new.mp4", ""))

    window.open_video()

    assert window.canvas.fit_mode is True
    window.canvas.zoom_in()
    manual_scale = window.canvas.transform().m11()
    window._load_frame(1.0)
    assert window.canvas.fit_mode is False
    assert abs(window.canvas.transform().m11() - manual_scale) < 1e-9
    assert workbench.profile_has_unsaved_changes is False


def test_settings_basic_area_has_no_coordinate_summary_and_scale_is_optional(qtbot):
    panel = GlassSettingsPanel()
    qtbot.addWidget(panel)
    panel.resize(420, 620)
    panel.show()
    glass = InspectionRecipe.default_glass(640, 480)
    panel.set_glass(glass)
    QApplication.processEvents()

    assert panel.findChild(QLabel, "roiSummaryCard") is None
    assert panel.edit_roi.text() == "분석 영역 편집"
    assert panel.reset_glass.text() == "Glass 초기화"
    assert panel.has_scale.text() == "mm 단위도 함께 표시"
    assert panel.has_scale.toolTip()
    assert panel.has_scale.parentWidget() is not panel.advanced_container
    assert not panel.has_scale.isChecked()
    assert not panel.scale.isEnabled()

    emitted = []
    panel.fieldChanged.connect(lambda key, value: emitted.append((key, value)))
    panel.has_scale.setChecked(True)
    assert panel.scale.isEnabled()
    assert emitted[-1][0] == "mm_per_pixel"
    assert emitted[-1][1] > 0
    panel.scale.setValue(0.25)
    panel.scale.editingFinished.emit()
    panel.has_scale.setChecked(False)
    assert emitted[-1] == ("mm_per_pixel", None)
    panel.has_scale.setChecked(True)
    assert panel.scale.value() == 0.25

    panel.focus_field("initial_state")
    QApplication.processEvents()
    assert panel._last_focused_field == "initial_state"
    assert panel.initial.hasFocus()


def test_wheel_safe_controls_do_not_change_values_and_keep_keyboard_editing(qtbot):
    panel = GlassSettingsPanel()
    qtbot.addWidget(panel)
    panel.resize(420, 260)
    panel.set_glass(InspectionRecipe.default_glass(640, 480))
    panel.set_advanced_visible(True)
    panel.show()
    QApplication.processEvents()

    for control in (panel.zero, panel.scale, panel.canny_low, panel.initial, panel.judgment):
        before = control.currentIndex() if hasattr(control, "currentIndex") else control.value()
        QApplication.sendEvent(control, _wheel_event())
        after = control.currentIndex() if hasattr(control, "currentIndex") else control.value()
        assert after == before

    scrollbar = panel.scroll.verticalScrollBar()
    assert scrollbar.maximum() > 0
    scrollbar.setValue(0)
    event = _wheel_event()
    QApplication.sendEvent(panel.zero, event)
    assert event.isAccepted()
    assert scrollbar.value() > 0

    panel.canny_low.setValue(10)
    panel.canny_low.setFocus()
    qtbot.keyClick(panel.canny_low, Qt.Key.Key_Up)
    assert panel.canny_low.value() == 11

    panel.initial.setCurrentIndex(0)
    panel.initial.setFocus()
    qtbot.keyClick(panel.initial, Qt.Key.Key_Down)
    assert panel.initial.currentIndex() == 1


def test_foam_action_navigates_without_mutating_recipe(qtbot):
    window, workbench = _window(qtbot)
    glass = workbench.add_glass()
    window._refresh_all()
    before = workbench.recipe.to_dict()
    foam = PhaseDetection(
        glass.id,
        0,
        0.0,
        FillState.FOAMING_VISIBLE,
        oil_air_level_y=glass.geometry.ellipse.center_y,
        overall_confidence=0.8,
    )
    window.detection_summary.set_detection(foam, glass, allow_initial_state_action=True)
    assert window.detection_summary.values["interpretation"].text() == "거품 가능성이 감지됨"
    assert window.detection_summary.values["recommendation"].text() == "영상에서 실제 거품인지 확인하세요."
    assert window.detection_summary.action_button.isVisible()
    window.detection_summary.action_button.click()
    assert window.settings._last_focused_field == "initial_state"
    assert workbench.selected_glass_id == glass.id
    assert workbench.recipe.to_dict() == before

    normal = PhaseDetection(
        glass.id,
        0,
        0.0,
        FillState.PARTIAL_VISIBLE,
        oil_air_level_y=glass.geometry.ellipse.center_y,
        overall_confidence=0.9,
    )
    window.detection_summary.set_detection(normal, glass, allow_initial_state_action=True)
    assert not window.detection_summary.action_button.isVisible()


def test_preflight_uses_one_modeless_window_without_compressing_workbench(qtbot):
    window, _workbench = _window(qtbot)
    controller = DummyPreflightController()
    coordinator = PreflightCoordinator(window, controller)
    preflight_window = coordinator.preflight_window

    assert window.findChild(QDockWidget, "preflightDock") is None
    assert preflight_window.isWindow()
    assert preflight_window.minimumWidth() == 900
    assert preflight_window.minimumHeight() == 540
    assert preflight_window.width() == 1100
    assert preflight_window.height() == 680

    canvas_geometry = window.canvas.geometry()
    coordinator.action.trigger()
    QApplication.processEvents()
    assert preflight_window.isVisible()
    assert window.canvas.geometry() == canvas_geometry
    first_identity = id(preflight_window)
    coordinator.action.trigger()
    assert id(coordinator.preflight_window) == first_identity

    coordinator.panel.run_button.click()
    assert controller.starts == 1
    coordinator.panel.cancel_button.click()
    assert controller.cancels == 1
    coordinator.panel.rerun_button.click()
    assert controller.starts == 2

    preflight_window.close()
    assert not preflight_window.isVisible()
    coordinator.show_window()
    assert preflight_window.isVisible()
    assert id(coordinator.preflight_window) == first_identity

    window.close()
    assert controller.invalidations >= 1
    assert not preflight_window.isVisible()
