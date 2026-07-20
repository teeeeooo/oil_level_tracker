from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStyle,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.config.defaults import DEFAULT_WINDOW_SIZE, PREVIEW_DEBOUNCE_MS, SUPPORTED_VIDEO_FILTER
from oil_tracker.domain.enums import InitialObservationState, JudgmentMode, WorkbenchState
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.ui.presentation_labels import (
    fill_state_label,
    result_state_label,
    validation_issue_message,
    workbench_state_label,
)
from oil_tracker.ui.readiness import (
    build_workbench_progress,
    first_actionable_issue,
    first_issue_for_fields,
    first_validation_error,
    glass_readiness_by_id,
)
from oil_tracker.ui.undo import RecipeSnapshotCommand
from oil_tracker.ui.widgets.analysis_progress_dialog import AnalysisProgressDialog
from oil_tracker.ui.widgets.bottom_action_bar import BottomActionBar
from oil_tracker.ui.widgets.debug_panel import DebugPanel
from oil_tracker.ui.widgets.detection_summary_card import DetectionSummaryCard
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel
from oil_tracker.ui.widgets.roi_editor_dialog import RoiEditorDialog
from oil_tracker.ui.widgets.transport_bar import TransportBar
from oil_tracker.ui.widgets.validation_panel import ValidationPanel
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas
from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget
from oil_tracker.ui.wizard.new_recipe_wizard import NewRecipeWizard


class MainWindow(QMainWindow):
    def __init__(self, workbench, preview_controller, analysis_controller, debug_renderer, parent=None) -> None:
        super().__init__(parent)
        self.workbench = workbench
        self.preview_controller = preview_controller
        self.analysis_controller = analysis_controller
        self.debug_renderer = debug_renderer
        self.current_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.current_time = 0.0
        self.current_frame_index = 0
        self.playback_speed = 1.0
        self.last_result_path = ""
        self.last_debug_artifacts = None
        self.undo_stack = QUndoStack(self)
        self._last_validation = None
        self._preview_context: tuple[str, int, float] | None = None
        self.setWindowTitle("Rotary Oil Level Tracker — 분석 프로필 설정")
        self.setMinimumSize(1280, 760)
        self._resize_to_available_screen()
        self._build_ui()
        self._connect()
        self._refresh_all()
        self._refresh_inline_validation()

    def _resize_to_available_screen(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            self.resize(*DEFAULT_WINDOW_SIZE)
            return
        available = screen.availableGeometry()
        width = min(DEFAULT_WINDOW_SIZE[0], max(1280, int(available.width() * 0.94)))
        height = min(DEFAULT_WINDOW_SIZE[1], max(760, int(available.height() * 0.92)))
        self.resize(width, height)

    def _build_ui(self) -> None:
        toolbar = QToolBar("분석 프로필 도구", self)
        toolbar.setObjectName("mainToolBar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        self.actions = {}
        definitions = (
            ("new", "새 프로필", QStyle.StandardPixmap.SP_FileIcon),
            ("load", "프로필 열기", QStyle.StandardPixmap.SP_DialogOpenButton),
            ("save", "프로필 저장", QStyle.StandardPixmap.SP_DialogSaveButton),
            ("validate", "설정 점검", QStyle.StandardPixmap.SP_DialogApplyButton),
            ("analyze", "분석 실행", QStyle.StandardPixmap.SP_MediaPlay),
            ("result", "결과 보고서", QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("debug", "ROI 상세보기", QStyle.StandardPixmap.SP_ComputerIcon),
        )
        toolbar_keys = {"new", "load", "result", "debug"}
        for key, label, icon in definitions:
            action = QAction(self.style().standardIcon(icon), label, self)
            self.actions[key] = action
            if key not in toolbar_keys:
                continue
            toolbar.addAction(action)
            button = toolbar.widgetForAction(action)
            if isinstance(button, QToolButton):
                button.setObjectName("toolbarButton")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
            if key in {"load", "result"}:
                toolbar.addSeparator()
        self.actions["debug"].setCheckable(True)
        self.actions["save"].setShortcut(QKeySequence.StandardKey.Save)

        self.actions["undo"] = self.undo_stack.createUndoAction(self, "실행 취소")
        self.actions["redo"] = self.undo_stack.createRedoAction(self, "다시 실행")
        self.actions["undo"].setShortcut(QKeySequence.StandardKey.Undo)
        self.actions["redo"].setShortcut(QKeySequence.StandardKey.Redo)
        self.actions["undo"].setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        self.actions["redo"].setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        toolbar.addAction(self.actions["undo"])
        toolbar.addAction(self.actions["redo"])
        for key in ("undo", "redo"):
            button = toolbar.widgetForAction(self.actions[key])
            if isinstance(button, QToolButton):
                button.setObjectName("toolbarButton")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar.addSeparator()
        self.state_label = QLabel()
        self.state_label.setObjectName("stateBadge")
        toolbar.addWidget(self.state_label)

        self.glass_list = GlassListPanel()
        self.canvas = VideoOverlayCanvas()
        self.settings = GlassSettingsPanel()
        self.transport = TransportBar()
        self.session_bar = self._build_session_bar()
        self.progress = WorkbenchProgressWidget()
        self.detection_summary = DetectionSummaryCard()
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(6, 6, 6, 6)
        center_layout.setSpacing(6)
        center_layout.addWidget(self.session_bar)
        center_layout.addWidget(self.detection_summary)
        center_layout.addWidget(self.canvas, 1)
        center_layout.addWidget(self.transport)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.glass_list)
        self.splitter.addWidget(center)
        self.splitter.addWidget(self.settings)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        width = max(1280, self.width())
        left = max(180, int(width * 0.12))
        right = max(460, int(width * 0.28))
        self.splitter.setSizes([left, max(660, width - left - right), right])

        self.action_bar = BottomActionBar()
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.progress)
        shell_layout.addWidget(self.splitter, 1)
        shell_layout.addWidget(self.action_bar)
        self.setCentralWidget(shell)

        self.validation_panel = ValidationPanel()
        self.validation_dock = QDockWidget("설정 점검 결과", self)
        self.validation_dock.setWidget(self.validation_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.validation_dock)
        self.validation_dock.hide()
        self.debug_panel = DebugPanel()
        self.debug_dock = QDockWidget("ROI 및 상세 검출 정보", self)
        self.debug_dock.setWidget(self.debug_panel)
        self.debug_dock.setMinimumSize(760, 560)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_dock)
        self.debug_dock.setFloating(True)
        self.debug_dock.resize(980, 720)
        self.debug_dock.hide()
        self.statusBar().showMessage("분석 프로필을 새로 만들거나 열어 주세요.")

        self.play_timer = QTimer(self)
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)

    def _toggle_debug_view(self, visible: bool) -> None:
        if visible:
            if not self.debug_dock.isFloating():
                self.debug_dock.setFloating(True)
            self.debug_dock.resize(980, 720)
            self.debug_dock.show()
            self.debug_dock.raise_()
            self.debug_dock.activateWindow()
        else:
            self.debug_dock.hide()

    def _sync_debug_action(self, visible: bool) -> None:
        self.actions["debug"].blockSignals(True)
        self.actions["debug"].setChecked(visible)
        self.actions["debug"].blockSignals(False)

    def _build_session_bar(self) -> QWidget:
        group = QGroupBox("분석 영상 설정")
        layout = QGridLayout(group)
        self.open_video_button = QPushButton("시험 영상 열기")
        self.open_video_button.setObjectName("secondaryActionButton")
        self.video_path_label = QLabel("선택된 시험 영상이 없습니다.")
        self.video_path_label.setObjectName("videoPathLabel")
        self.video_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.video_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.start_spin = _time_spin()
        self.end_spin = _time_spin()
        self.compressor_spin = _time_spin()
        self.sampling_spin = _time_spin()
        self.sampling_spin.setDecimals(2)
        self.sampling_spin.setSuffix(" 회/초")
        self.sampling_spin.setValue(2.0)
        layout.addWidget(self.open_video_button, 0, 0)
        layout.addWidget(self.video_path_label, 0, 1, 1, 5)
        layout.addWidget(QLabel("분석 시작"), 1, 0)
        layout.addWidget(self.start_spin, 1, 1)
        layout.addWidget(QLabel("분석 종료"), 1, 2)
        layout.addWidget(self.end_spin, 1, 3)
        layout.addWidget(QLabel("압축기 기동"), 1, 4)
        layout.addWidget(self.compressor_spin, 1, 5)
        layout.addWidget(QLabel("분석 빈도"), 1, 6)
        layout.addWidget(self.sampling_spin, 1, 7)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(5, 1)
        layout.setColumnStretch(7, 1)
        return group

    def _connect(self) -> None:
        self.actions["new"].triggered.connect(self.new_recipe)
        self.actions["load"].triggered.connect(self.load_recipe)
        self.actions["save"].triggered.connect(self.save_recipe)
        self.actions["validate"].triggered.connect(self.validate_workbench)
        self.actions["analyze"].triggered.connect(self.run_analysis)
        self.actions["result"].triggered.connect(self.open_result)
        self.actions["debug"].toggled.connect(self._toggle_debug_view)
        self.debug_dock.visibilityChanged.connect(self._sync_debug_action)
        self.action_bar.validateRequested.connect(self.actions["validate"].trigger)
        self.action_bar.saveRequested.connect(self.actions["save"].trigger)
        self.action_bar.analyzeRequested.connect(self.actions["analyze"].trigger)
        self.open_video_button.clicked.connect(self.open_video)
        self.glass_list.addRequested.connect(self.add_glass)
        self.glass_list.deleteRequested.connect(self.delete_glass)
        self.glass_list.selectionChanged.connect(self.select_glass)
        self.glass_list.enabledChanged.connect(self.set_enabled)
        self.glass_list.issueActivated.connect(self._route_validation_issue)
        self.progress.stepActivated.connect(self._progress_step_activated)
        self.progress.nextIssueRequested.connect(self._navigate_next_issue)
        self.canvas.geometryChanged.connect(self._geometry_changed)
        self.canvas.zeroLineChanged.connect(self._zero_changed)
        self.canvas.exclusionChanged.connect(self._exclusion_changed)
        self.canvas.glassSelected.connect(self.select_glass)
        self.settings.fieldChanged.connect(self._field_changed)
        self.settings.addExclusionRequested.connect(self.add_exclusion)
        self.settings.deleteExclusionRequested.connect(self.delete_exclusion)
        self.settings.restoreDefaultsRequested.connect(self.restore_defaults)
        self.settings.editRoiRequested.connect(self.open_roi_editor)
        self.settings.resetGlassRequested.connect(self.reset_selected_glass)
        self.transport.playToggled.connect(self.toggle_play)
        self.transport.stepRequested.connect(self.step_frame)
        self.transport.seekRequested.connect(self.seek_fraction)
        self.transport.seekReleased.connect(self.schedule_preview)
        self.transport.speedChanged.connect(lambda value: setattr(self, "playback_speed", value))
        self.play_timer.timeout.connect(self._play_tick)
        self.preview_timer.timeout.connect(self.request_preview)
        self.preview_controller.previewReady.connect(self._preview_ready)
        self.preview_controller.previewFailed.connect(self._preview_failed)
        self.analysis_controller.progress.connect(self._analysis_progress)
        self.analysis_controller.completed.connect(self._analysis_completed)
        self.analysis_controller.failed.connect(self._analysis_failed)
        self.analysis_controller.cancelled.connect(self._analysis_cancelled)
        self.validation_panel.issueActivated.connect(self._route_validation_issue)
        self.debug_panel.exportRequested.connect(self.export_debug)
        for spin in (self.start_spin, self.end_spin, self.compressor_spin, self.sampling_spin):
            spin.editingFinished.connect(self._session_changed)

    def _record_recipe_change(self, text: str, change) -> None:
        before = self.workbench.recipe.to_dict()
        selected_before = self.workbench.selected_glass_id
        change()
        after = self.workbench.recipe.to_dict()
        selected_after = self.workbench.selected_glass_id
        if before == after and selected_before == selected_after:
            return
        self.undo_stack.push(
            RecipeSnapshotCommand(
                self.workbench,
                before,
                after,
                selected_before,
                selected_after,
                text,
                self._after_snapshot_restored,
                already_applied=True,
            )
        )
        self._after_user_change()

    def _after_snapshot_restored(self) -> None:
        self._refresh_all()
        self.schedule_preview()
        self._refresh_inline_validation()

    def _after_user_change(self) -> None:
        self._refresh_all()
        self.schedule_preview()
        self._refresh_inline_validation()

    def _refresh_inline_validation(self):
        if self.workbench.state == WorkbenchState.ANALYZING and self._last_validation is not None:
            return self._last_validation
        result = self.workbench.validation_result()
        self._apply_validation_result(result)
        return result

    def _apply_validation_result(self, result) -> None:
        self._last_validation = result
        selected_id = self.workbench.selected_glass_id
        self.settings.set_validation_issues(result.issues, selected_id)
        self.validation_panel.set_result(result)
        self.action_bar.set_validation_result(result)
        self._refresh_panels()
        self._update_state()

    def open_roi_editor(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        dialog = RoiEditorDialog(
            self.current_frame,
            glass,
            self.workbench.recipe.reference_frame_width,
            self.workbench.recipe.reference_frame_height,
            self,
        )
        if dialog.exec() != RoiEditorDialog.DialogCode.Accepted:
            return
        edited = dialog.edited_glass()

        def apply_edit() -> None:
            for index, candidate in enumerate(self.workbench.recipe.glasses):
                if candidate.id == edited.id:
                    self.workbench.recipe.glasses[index] = edited
                    self.workbench.selected_glass_id = edited.id
                    self.workbench.mark_dirty()
                    return

        self._record_recipe_change("ROI 집중 편집", apply_edit)

    def reset_selected_glass(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None:
            return

        def reset() -> None:
            current = self.workbench.selected_glass()
            if current is None:
                return
            default = InspectionRecipe.default_glass(
                self.workbench.recipe.reference_frame_width,
                self.workbench.recipe.reference_frame_height,
            )
            default.id = current.id
            default.name = current.name
            default.enabled = current.enabled
            default.description = current.description
            for index, candidate in enumerate(self.workbench.recipe.glasses):
                if candidate.id == current.id:
                    self.workbench.recipe.glasses[index] = default
                    self.workbench.mark_dirty()
                    return

        self._record_recipe_change("관찰창 초기화", reset)

    def new_recipe(self) -> None:
        wizard = NewRecipeWizard(self)
        if wizard.exec() == NewRecipeWizard.DialogCode.Accepted:
            if wizard.skipped:
                self.workbench.new_document()
                self.undo_stack.clear()
                self._set_placeholder()
                self._refresh_all()
                self._refresh_inline_validation()
                return
            metadata = wizard.video_metadata
            width, height = (metadata.width, metadata.height) if metadata else (1280, 720)
            self.workbench.new_document(width, height, wizard.recipe_name.text().strip() or "새 유면 분석 프로필")
            self.undo_stack.clear()
            self.workbench.recipe.description = wizard.description.toPlainText()
            if wizard.video_path.text():
                self.workbench.open_video(wizard.video_path.text())
                self.workbench.session.analysis_start_sec = wizard.start.value()
                self.workbench.session.analysis_end_sec = wizard.end.value()
                self.workbench.session.compressor_start_sec = wizard.compressor.value()
                self.workbench.session.sampling_fps = wizard.sampling.value()
                self._load_frame(self.workbench.session.analysis_start_sec)
            if wizard.create_glass.isChecked():
                self.workbench.add_glass()
            self._refresh_all()
            self.schedule_preview()
            self._refresh_inline_validation()

    def open_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "시험 영상 열기", "", SUPPORTED_VIDEO_FILTER)
        if not path:
            return
        try:
            self.workbench.open_video(path)
            self._sync_session_fields()
            self._load_frame(0.0)
            self._refresh_all()
            self.schedule_preview()
            self._refresh_inline_validation()
        except Exception as exc:
            self._error("영상 열기 실패", str(exc))

    def add_glass(self) -> None:
        self._record_recipe_change("관찰창 추가", self.workbench.add_glass)

    def delete_glass(self) -> None:
        self._record_recipe_change("관찰창 삭제", self.workbench.delete_selected_glass)

    def select_glass(self, glass_id: str) -> None:
        self.workbench.set_selected(glass_id)
        self._refresh_panels()
        self.schedule_preview()
        self._refresh_inline_validation()

    def set_enabled(self, glass_id: str, enabled: bool) -> None:
        def change() -> None:
            glass = next((g for g in self.workbench.recipe.glasses if g.id == glass_id), None)
            if glass is not None:
                glass.enabled = enabled
                self.workbench.mark_dirty()

        self._record_recipe_change("분석 포함 변경", change)

    def _geometry_changed(self, glass_id: str, ellipse) -> None:
        self._record_recipe_change(
            "관찰창 위치 또는 크기 변경",
            lambda: self.workbench.update_ellipse(glass_id, ellipse),
        )

    def _zero_changed(self, glass_id: str, y: float) -> None:
        self._record_recipe_change(
            "기준점 이동",
            lambda: self.workbench.update_zero_line(glass_id, y),
        )

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect) -> None:
        self._record_recipe_change(
            "검출 제외 영역 변경",
            lambda: self.workbench.update_exclusion(glass_id, zone_id, rect),
        )

    def add_exclusion(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None:
            self._record_recipe_change(
                "검출 제외 영역 추가",
                lambda: self.workbench.add_exclusion(glass.id),
            )

    def delete_exclusion(self, zone_id: str) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None:
            self._record_recipe_change(
                "검출 제외 영역 삭제",
                lambda: self.workbench.delete_exclusion(glass.id, zone_id),
            )

    def restore_defaults(self) -> None:
        def change() -> None:
            glass = self.workbench.selected_glass()
            if glass is not None:
                glass.detector_settings = DetectorSettings()
                self.workbench.mark_dirty()

        self._record_recipe_change("검출 설정 기본값 복원", change)

    def _field_changed(self, key: str, value) -> None:
        def change() -> None:
            glass = self.workbench.selected_glass()
            if glass is None:
                return
            e = glass.geometry.ellipse
            if key in {"center_x", "center_y", "width", "height"}:
                cx = value if key == "center_x" else e.center_x
                cy = value if key == "center_y" else e.center_y
                rx = value / 2 if key == "width" else e.radius_x
                ry = value / 2 if key == "height" else e.radius_y
                self.workbench.update_ellipse(glass.id, EllipseGeometry(cx, cy, rx, ry))
            elif key == "zero_line_y":
                self.workbench.update_zero_line(glass.id, float(value))
            elif key == "name":
                glass.name = str(value)
                self.workbench.mark_dirty()
            elif key == "enabled":
                glass.enabled = bool(value)
                self.workbench.mark_dirty()
            elif key == "initial_state":
                glass.initial_state = InitialObservationState(value)
                self.workbench.mark_dirty()
            elif key == "mm_per_pixel":
                glass.mm_per_pixel = value
                self.workbench.mark_dirty()
            elif key == "judgment_mode":
                glass.judgment_rule.mode = JudgmentMode(value)
                self.workbench.mark_dirty()
            elif key == "margin_ratio":
                glass.geometry.margin_ratio = float(value)
                self.workbench.mark_dirty()
            elif hasattr(glass.detector_settings, key):
                setattr(glass.detector_settings, key, value)
                self.workbench.mark_dirty()

        self._record_recipe_change("관찰창 설정 변경", change)

    def _session_changed(self) -> None:
        self.workbench.session.analysis_start_sec = self.start_spin.value()
        self.workbench.session.analysis_end_sec = self.end_spin.value()
        self.workbench.session.compressor_start_sec = self.compressor_spin.value()
        self.workbench.session.sampling_fps = self.sampling_spin.value()
        self.workbench.mark_dirty()
        self._update_transport_markers()
        self._update_state()
        self._refresh_inline_validation()

    def toggle_play(self, playing: bool) -> None:
        if playing and self.workbench.video_reader:
            fps = max(1.0, self.workbench.video_reader.metadata.fps)
            self.play_timer.start(max(15, int(1000 / fps)))
        else:
            self.play_timer.stop()
            self.schedule_preview()

    def _play_tick(self) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None:
            self.transport.play.setChecked(False)
            return
        step = self.playback_speed / max(1.0, metadata.fps)
        target = self.current_time + step
        if target >= metadata.duration_sec:
            self.transport.play.setChecked(False)
            return
        self._load_frame(target)

    def step_frame(self, direction: int) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata:
            self._load_frame(max(0.0, min(metadata.duration_sec, self.current_time + direction / max(1.0, metadata.fps))))
            self.schedule_preview()

    def seek_fraction(self, fraction: float) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata:
            self._load_frame(metadata.duration_sec * fraction)
            self.preview_timer.start()

    def _load_frame(self, timestamp: float) -> None:
        try:
            frame, frame_index, actual = self.workbench.read_at(timestamp)
            self.current_frame = frame
            self.current_frame_index = frame_index
            self.current_time = actual
            self.canvas.set_frame(frame)
            self.transport.set_position(
                actual,
                self.workbench.session.video_metadata.duration_sec if self.workbench.session.video_metadata else 0.0,
                frame_index,
            )
            self._invalidate_preview("현재 장면 분석 대기")
        except Exception as exc:
            self.statusBar().showMessage(f"영상 장면을 읽지 못했습니다: {exc}")

    def schedule_preview(self) -> None:
        self._invalidate_preview("현재 장면 분석 대기")
        if self.workbench.selected_glass() is not None and self.workbench.session.video_metadata is not None:
            self.preview_timer.start()
        else:
            self.preview_timer.stop()

    def request_preview(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None or self.current_frame is None or self.workbench.session.video_metadata is None:
            self._invalidate_preview("시험 영상과 관찰창을 선택해 주세요")
            return
        self._preview_context = (glass.id, self.current_frame_index, self.current_time)
        self.detection_summary.set_loading()
        self.statusBar().showMessage("현재 장면을 분석하고 있습니다...")
        self.preview_controller.request(
            self.current_frame,
            glass,
            self.current_frame_index,
            self.current_time,
        )

    def _preview_ready(self, detection, artifacts) -> None:
        context = self._preview_context
        if context is None:
            return
        selected_id = self.workbench.selected_glass_id
        if (
            detection.glass_id != selected_id
            or detection.glass_id != context[0]
            or detection.frame_index != self.current_frame_index
            or detection.frame_index != context[1]
            or abs(float(detection.time_sec) - self.current_time) > 1e-6
            or abs(float(detection.time_sec) - context[2]) > 1e-6
        ):
            return
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        self.canvas.set_detection(detection)
        self.detection_summary.set_detection(detection, glass)
        self.debug_panel.set_artifacts(artifacts)
        self.last_debug_artifacts = artifacts
        self.statusBar().showMessage(
            f"현재 상태: {fill_state_label(detection.fill_state)} · 신뢰도 {detection.overall_confidence:.2f}"
        )

    def _preview_failed(self, message: str) -> None:
        self.canvas.set_detection(None)
        self.detection_summary.set_failure(message)
        self.last_debug_artifacts = None
        self.statusBar().showMessage(f"현재 장면 분석 실패: {message}")

    def _invalidate_preview(self, message: str) -> None:
        invalidate = getattr(self.preview_controller, "invalidate", None)
        if callable(invalidate):
            invalidate()
        self._preview_context = None
        self.canvas.set_detection(None)
        self.last_debug_artifacts = None
        if self.workbench.session.video_metadata is None:
            self.detection_summary.set_empty("시험 영상을 선택해 주세요")
        elif self.workbench.selected_glass() is None:
            self.detection_summary.set_empty("관찰창을 선택해 주세요")
        else:
            self.detection_summary.set_empty(message)

    def save_recipe(self) -> None:
        path = self.workbench.recipe_path
        if path is None:
            selected, _ = QFileDialog.getSaveFileName(
                self,
                "분석 프로필 저장",
                "",
                "유면 분석 프로필 (*.oilrecipe)",
            )
            if not selected:
                return
            path = Path(selected)
        try:
            self.workbench.save(path)
            self._update_state()
            self.statusBar().showMessage(f"프로필 저장 완료: {path}")
        except Exception as exc:
            self._error("프로필 저장 실패", str(exc))

    def load_recipe(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "분석 프로필 열기",
            "",
            "유면 분석 프로필 (*.oilrecipe)",
        )
        if not selected:
            return
        try:
            self.workbench.load(Path(selected))
            self.undo_stack.clear()
            self._set_placeholder()
            self._refresh_all()
            self._refresh_inline_validation()
        except Exception as exc:
            self._error("프로필 열기 실패", str(exc))

    def validate_workbench(self):
        result = self.workbench.validate()
        self._apply_validation_result(result)
        self.validation_panel.set_result(result)
        self.validation_dock.show()
        self.statusBar().showMessage(
            "설정 점검을 통과했습니다."
            if result.is_ready
            else f"수정이 필요한 오류가 {len(result.errors)}개 있습니다."
        )
        return result

    def _route_validation_issue(self, issue) -> None:
        if issue.glass_id:
            self.select_glass(issue.glass_id)
        self.settings.focus_field(issue.field)
        field_map = {
            "sampling_fps": self.sampling_spin,
            "input_video_path": self.open_video_button,
            "analysis_range": self.start_spin,
            "compressor_start": self.compressor_spin,
        }
        widget = field_map.get(issue.field)
        if widget is not None:
            widget.setFocus()
        self.statusBar().showMessage(validation_issue_message(issue))

    def _navigate_next_issue(self) -> None:
        if self._last_validation is None:
            return
        issue = first_actionable_issue(self.workbench.recipe.glasses, self._last_validation)
        if issue is None:
            self.statusBar().showMessage("수정하거나 확인할 관찰창 항목이 없습니다.")
            return
        self._route_validation_issue(issue)

    def _progress_step_activated(self, step_key: str) -> None:
        if step_key == "video":
            self.open_video_button.setFocus()
            self.statusBar().showMessage("시험 영상 열기에서 분석 영상을 선택해 주세요.")
            return
        if step_key == "time":
            issue = (
                first_issue_for_fields(
                    self._last_validation,
                    {"analysis_range", "sampling_fps", "compressor_start"},
                )
                if self._last_validation is not None
                else None
            )
            if issue is not None:
                self._route_validation_issue(issue)
            else:
                self.start_spin.setFocus()
                self.statusBar().showMessage("분석 시간과 압축기 기동 시각을 확인해 주세요.")
            return
        if step_key == "glasses":
            self._navigate_next_issue()
            if self.workbench.selected_glass_id is None:
                self.glass_list.list.setFocus()
            return
        if step_key == "validation":
            self.validation_dock.show()
            issue = first_validation_error(self._last_validation) if self._last_validation is not None else None
            if issue is not None:
                self._route_validation_issue(issue)
            else:
                self.action_bar.validate_button.setFocus()
                self.statusBar().showMessage("설정 점검을 실행해 분석 가능 상태를 확정해 주세요.")
            return
        if step_key == "analysis":
            self.action_bar.analyze_button.setFocus()
            message = "분석 실행을 선택해 주세요." if self.workbench.state == WorkbenchState.VALIDATED else "설정 점검 완료 후 분석할 수 있습니다."
            self.statusBar().showMessage(message)

    def run_analysis(self) -> None:
        result = self.validate_workbench()
        if not result.is_ready:
            QMessageBox.warning(self, "분석을 시작할 수 없음", "설정 점검의 오류 항목을 먼저 수정해 주세요.")
            return
        output = QFileDialog.getExistingDirectory(
            self,
            "결과 저장 폴더 선택",
            str(Path(self.workbench.session.input_video_path).parent),
        )
        if not output:
            return
        self.workbench.session.output_directory = output
        self.workbench.state = WorkbenchState.ANALYZING
        self._update_state()
        self.progress_dialog = AnalysisProgressDialog(self)
        self.progress_dialog.cancelRequested.connect(self.analysis_controller.cancel)
        self.analysis_controller.start(self.workbench.recipe, self.workbench.session)
        self.progress_dialog.show()

    def _analysis_progress(self, update) -> None:
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.update_progress(update)

    def _analysis_completed(self, result, output_path: str) -> None:
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.accept()
        self.workbench.state = WorkbenchState.ANALYZED
        self.last_result_path = output_path
        self._update_state()
        QMessageBox.information(
            self,
            "분석 완료",
            f"전체 판정: {result_state_label(result.overall_state)}\n{output_path}",
        )

    def _analysis_failed(self, message: str) -> None:
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.reject()
        self.workbench.state = WorkbenchState.ERROR
        self._update_state()
        self._error("분석 실패", message)

    def _analysis_cancelled(self) -> None:
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.reject()
        self.workbench.state = WorkbenchState.VALIDATED
        self._update_state()
        self.statusBar().showMessage("분석이 취소되었습니다.")

    def open_result(self) -> None:
        if self.last_result_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.last_result_path) / "report.html")))
        else:
            QMessageBox.information(self, "결과 보고서", "현재 작업에서 생성된 결과가 없습니다.")

    def export_debug(self) -> None:
        if self.last_debug_artifacts is None:
            QMessageBox.information(self, "상세 정보", "먼저 현재 장면 분석을 실행해 주세요.")
            return
        directory = QFileDialog.getExistingDirectory(self, "상세 정보 저장 폴더 선택")
        if directory:
            paths = self.debug_renderer.export(Path(directory), self.current_frame_index, self.last_debug_artifacts)
            self.statusBar().showMessage(f"상세 정보 파일 {len(paths)}개를 저장했습니다.")

    def _refresh_all(self) -> None:
        self._refresh_panels()
        self._sync_session_fields()
        self._update_state()

    def _refresh_panels(self) -> None:
        readiness = (
            glass_readiness_by_id(self.workbench.recipe.glasses, self._last_validation)
            if self._last_validation is not None
            else None
        )
        self.glass_list.set_glasses(
            self.workbench.recipe.glasses,
            self.workbench.selected_glass_id,
            readiness,
        )
        self.settings.set_glass(self.workbench.selected_glass())
        self.canvas.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)
        if self._last_validation is not None:
            self.settings.set_validation_issues(
                self._last_validation.issues, self.workbench.selected_glass_id
            )

    def _sync_session_fields(self) -> None:
        session = self.workbench.session
        for widget, value in (
            (self.start_spin, session.analysis_start_sec),
            (self.end_spin, session.analysis_end_sec or 0.0),
            (self.compressor_spin, session.compressor_start_sec or 0.0),
            (self.sampling_spin, session.sampling_fps),
        ):
            widget.blockSignals(True)
            widget.setValue(value)
            widget.blockSignals(False)
        if session.video_metadata:
            self.sampling_spin.setMaximum(max(0.1, session.video_metadata.fps))
        self.video_path_label.setText(
            session.input_video_path if session.input_video_path else "선택된 시험 영상이 없습니다."
        )
        self._update_transport_markers()

    def _update_transport_markers(self) -> None:
        session = self.workbench.session
        duration = session.video_metadata.duration_sec if session.video_metadata else 0.0
        self.transport.slider.set_markers(
            duration,
            session.analysis_start_sec,
            session.analysis_end_sec,
            session.compressor_start_sec,
        )

    def _update_state(self) -> None:
        self.state_label.setText(f"상태: {workbench_state_label(self.workbench.state)}")
        self.state_label.setProperty("workbenchState", self.workbench.state.value)
        self.state_label.style().unpolish(self.state_label)
        self.state_label.style().polish(self.state_label)
        can_analyze = self.workbench.state == WorkbenchState.VALIDATED
        self.actions["analyze"].setEnabled(can_analyze)
        self.actions["result"].setEnabled(bool(self.last_result_path))
        if self._last_validation is not None:
            self.action_bar.set_validation_result(self._last_validation)
            issue = first_actionable_issue(self.workbench.recipe.glasses, self._last_validation)
            self.progress.set_steps(
                build_workbench_progress(
                    self.workbench.recipe,
                    self.workbench.session,
                    self.workbench.state,
                    self._last_validation,
                ),
                issue is not None,
            )
        self.action_bar.analyze_button.setEnabled(can_analyze)

    def _set_placeholder(self) -> None:
        self.current_frame = np.zeros(
            (self.workbench.recipe.reference_frame_height, self.workbench.recipe.reference_frame_width, 3),
            dtype=np.uint8,
        )
        self.canvas.set_frame(self.current_frame)
        self._invalidate_preview("시험 영상을 선택해 주세요")

    def _error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event) -> None:
        self.workbench.close_video()
        super().closeEvent(event)


def _time_spin() -> QDoubleSpinBox:
    box = QDoubleSpinBox()
    box.setRange(0, 1_000_000)
    box.setDecimals(3)
    box.setKeyboardTracking(False)
    box.setSuffix(" 초")
    return box
