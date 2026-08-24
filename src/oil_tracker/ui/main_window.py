from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl, Qt, Signal
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence, QUndoStack
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
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

from oil_tracker.config.defaults import DEFAULT_WINDOW_SIZE, SUPPORTED_VIDEO_FILTER
from oil_tracker.domain.enums import InitialObservationState, JudgmentMode, WorkbenchState
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe
from oil_tracker.ui.controllers.workbench_playback_controller import WorkbenchPlaybackController
from oil_tracker.ui.presentation_labels import (
    result_state_label,
    validation_issue_message,
    workbench_state_label,
)
from oil_tracker.ui.profile_lifecycle_coordinator import (
    ProfileLifecycleCallbacks,
    ProfileLifecycleCoordinator,
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
from oil_tracker.ui.widgets.video_playback_panel import VideoPlaybackPanel
from oil_tracker.ui.widgets.wheel_safe_controls import WheelSafeDoubleSpinBox
from oil_tracker.ui.widgets.workbench_progress import WorkbenchProgressWidget


class MainWindow(QMainWindow):
    applicationCloseAccepted = Signal()

    def __init__(
        self,
        workbench,
        preview_controller,
        analysis_controller,
        debug_renderer,
        parent=None,
        *,
        artifact_proposer=None,
    ) -> None:
        super().__init__(parent)
        self.workbench = workbench
        self.preview_controller = preview_controller
        self.analysis_controller = analysis_controller
        self.debug_renderer = debug_renderer
        self.artifact_proposer = artifact_proposer
        self.last_result_path = ""
        self.undo_stack = QUndoStack(self)
        self._last_validation = None
        self._interaction_glass_id: str | None = None
        self._interaction_target: str | None = None
        self._interaction_zone_id: str | None = None
        self.setWindowTitle("Rotary Oil Level Tracker — 분석 프로필 설정")
        self.setMinimumSize(1280, 760)
        self._resize_to_available_screen()
        self._build_ui()
        self.playback_controller = WorkbenchPlaybackController(
            self.workbench,
            self.preview_controller,
            self.canvas,
            self.transport,
            self.detection_summary,
            self.debug_panel,
            self.statusBar(),
            self,
        )
        self.profile_lifecycle = ProfileLifecycleCoordinator(
            self.workbench,
            self.undo_stack,
            self.recent_profile_menu,
            self.actions["load"],
            ProfileLifecycleCallbacks(
                clear_interaction_target=self._clear_interaction_target,
                set_placeholder=self._set_placeholder,
                load_frame=lambda timestamp, reset_view: self._load_frame(
                    timestamp,
                    reset_view=reset_view,
                ),
                refresh_all=self._refresh_all,
                refresh_inline_validation=self._refresh_inline_validation,
                schedule_preview=self.schedule_preview,
                update_state=self._update_state,
                show_status=lambda message: self.statusBar().showMessage(message),
                report_error=lambda title, message: self._error(title, message),
            ),
            self,
        )
        self._connect()
        self._refresh_all()
        self._refresh_inline_validation()

    @property
    def current_frame(self):
        return self.playback_controller.current_frame

    @current_frame.setter
    def current_frame(self, value) -> None:
        self.playback_controller.current_frame = value

    @property
    def current_time(self) -> float:
        return self.playback_controller.current_time

    @current_time.setter
    def current_time(self, value: float) -> None:
        self.playback_controller.current_time = float(value)

    @property
    def current_frame_index(self) -> int:
        return self.playback_controller.current_frame_index

    @current_frame_index.setter
    def current_frame_index(self, value: int) -> None:
        self.playback_controller.current_frame_index = int(value)

    @property
    def playback_speed(self) -> float:
        return self.playback_controller.playback_speed

    @playback_speed.setter
    def playback_speed(self, value: float) -> None:
        self.playback_controller.set_playback_speed(value)

    @property
    def last_debug_artifacts(self):
        return self.playback_controller.last_debug_artifacts

    @last_debug_artifacts.setter
    def last_debug_artifacts(self, value) -> None:
        self.playback_controller.last_debug_artifacts = value

    @property
    def _preview_context(self):
        return self.playback_controller.preview_context

    @_preview_context.setter
    def _preview_context(self, value) -> None:
        self.playback_controller.preview_context = value

    @property
    def play_timer(self):
        return self.playback_controller.play_timer

    @property
    def preview_timer(self):
        return self.playback_controller.preview_timer

    @property
    def recent_profile_history(self):
        return self.profile_lifecycle.recent_profile_history

    @recent_profile_history.setter
    def recent_profile_history(self, value) -> None:
        self.profile_lifecycle.set_recent_profile_history(value)

    @property
    def _pending_profile_path(self):
        return self.profile_lifecycle.pending_profile_path

    @_pending_profile_path.setter
    def _pending_profile_path(self, value) -> None:
        self.profile_lifecycle.pending_profile_path = value

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
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)
        self.main_toolbar = toolbar
        self.actions = {}
        definitions = (
            ("new", "새 프로필", QStyle.StandardPixmap.SP_FileIcon),
            ("load", "프로필 열기", QStyle.StandardPixmap.SP_DialogOpenButton),
            ("save", "프로필 저장", QStyle.StandardPixmap.SP_DialogSaveButton),
            ("validate", "설정 점검", QStyle.StandardPixmap.SP_DialogApplyButton),
            ("analyze", "분석 실행", QStyle.StandardPixmap.SP_MediaPlay),
            ("result", "결과 보고서", QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("debug", "분석 영역 상세보기", QStyle.StandardPixmap.SP_ComputerIcon),
        )
        for key, label, icon in definitions:
            action = QAction(self.style().standardIcon(icon), label, self)
            self.actions[key] = action
        self.recent_profile_menu = QMenu("최근 프로필", self)
        self.recent_profile_menu.setObjectName("recentProfileMenu")
        self.actions["load"].setMenu(self.recent_profile_menu)
        self.actions["debug"].setCheckable(True)
        self.actions["save"].setShortcut(QKeySequence.StandardKey.Save)

        self.actions["undo"] = self.undo_stack.createUndoAction(self, "실행 취소")
        self.actions["redo"] = self.undo_stack.createRedoAction(self, "다시 실행")
        self.actions["undo"].setShortcut(QKeySequence.StandardKey.Undo)
        self.actions["redo"].setShortcut(QKeySequence.StandardKey.Redo)
        self.actions["undo"].setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        self.actions["redo"].setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))

        for key in ("new", "load"):
            toolbar.addAction(self.actions[key])
            button = toolbar.widgetForAction(self.actions[key])
            if isinstance(button, QToolButton):
                button.setObjectName("toolbarButton")
                button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.workbench_menu = QMenu("워크벤치 작업", self)
        self.workbench_menu.setObjectName("workbenchActionMenu")
        self.workbench_menu.addAction(self.actions["save"])
        self.workbench_menu.addSeparator()
        self.workbench_menu.addAction(self.actions["result"])
        self.workbench_menu.addAction(self.actions["debug"])
        self.workbench_menu.addSeparator()
        self.workbench_menu.addAction(self.actions["undo"])
        self.workbench_menu.addAction(self.actions["redo"])
        self.workbench_menu_button = QToolButton(toolbar)
        self.workbench_menu_button.setObjectName("toolbarMenuButton")
        self.workbench_menu_button.setText("더보기")
        self.workbench_menu_button.setMenu(self.workbench_menu)
        self.workbench_menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.workbench_menu_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toolbar_more_action = toolbar.addWidget(self.workbench_menu_button)

        toolbar_spacer = QWidget(toolbar)
        toolbar_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar_spacer_action = toolbar.addWidget(toolbar_spacer)
        self.state_label = QLabel()
        self.state_label.setObjectName("stateBadge")
        toolbar.addWidget(self.state_label)

        self.glass_list = GlassListPanel()
        self.canvas = VideoOverlayCanvas()
        self.canvas.setMinimumSize(560, 300)
        self.settings = GlassSettingsPanel()
        self.transport = TransportBar()
        self.profile_context = self._build_profile_context()
        self.session_bar = self._build_session_bar()
        self.progress = WorkbenchProgressWidget()
        self.detection_summary = DetectionSummaryCard()
        self.playback_panel = VideoPlaybackPanel(self.canvas, self.transport)

        self.left_panel = QWidget()
        self.left_panel.setObjectName("workbenchLeftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(4, 4, 4, 4)
        left_layout.setSpacing(6)
        left_layout.addWidget(self.detection_summary, 0)
        left_layout.addWidget(self.glass_list, 1)
        self.left_panel.setMinimumWidth(250)

        self.center_panel = QWidget()
        self.center_panel.setObjectName("workbenchCenterPanel")
        center_layout = QVBoxLayout(self.center_panel)
        center_layout.setContentsMargins(6, 6, 6, 6)
        center_layout.setSpacing(6)
        center_layout.addWidget(self.session_bar, 0)
        center_layout.addWidget(self.playback_panel, 1)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.center_panel)
        self.splitter.addWidget(self.settings)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        width = max(1280, self.width())
        left = max(250, int(width * 0.20))
        right = max(370, int(width * 0.27))
        self.splitter.setSizes([left, max(580, width - left - right), right])

        self.action_bar = BottomActionBar()
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.progress)
        shell_layout.addWidget(self.profile_context)
        shell_layout.addWidget(self.splitter, 1)
        shell_layout.addWidget(self.action_bar)
        self.setCentralWidget(shell)

        self.validation_panel = ValidationPanel()
        self.validation_dock = QDockWidget("설정 점검 결과", self)
        self.validation_dock.setWidget(self.validation_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.validation_dock)
        self.validation_dock.hide()
        self.debug_panel = DebugPanel()
        self.debug_dock = QDockWidget("분석 영역 및 상세 검출 정보", self)
        self.debug_dock.setWidget(self.debug_panel)
        self.debug_dock.setMinimumSize(760, 560)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.debug_dock)
        self.debug_dock.setFloating(True)
        self.debug_dock.resize(980, 720)
        self.debug_dock.hide()
        self.statusBar().showMessage("분석 프로필을 새로 만들거나 열어 주세요.")

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

    def _build_profile_context(self) -> QWidget:
        group = QGroupBox("Profile — 재사용 설정")
        group.setObjectName("profileOwnershipGroup")
        group.setToolTip("Glass, 검출과 판정 설정은 이 Profile에 저장됩니다.")
        layout = QGridLayout(group)
        self.profile_name_label = QLabel()
        self.profile_name_label.setObjectName("profileIdentityName")
        self.profile_path_label = QLabel()
        self.profile_path_label.setObjectName("profileIdentityPath")
        self.profile_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(QLabel("Profile 이름"), 0, 0)
        layout.addWidget(self.profile_name_label, 0, 1)
        layout.addWidget(QLabel("저장 위치"), 0, 2)
        layout.addWidget(self.profile_path_label, 0, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 2)
        return group

    def _build_session_bar(self) -> QWidget:
        group = QGroupBox("현재 시험 — Profile에는 저장되지 않음")
        group.setObjectName("currentTestOwnershipGroup")
        group.setToolTip("영상, 시험 이름과 시간 범위는 이번 분석에만 적용됩니다.")
        layout = QGridLayout(group)
        self.open_video_button = QPushButton("영상 선택")
        self.open_video_button.setObjectName("secondaryActionButton")
        self.video_path_label = QLabel("선택된 시험 영상이 없습니다.")
        self.video_path_label.setObjectName("videoPathLabel")
        self.video_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.video_path_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.run_name_edit = QLineEdit()
        self.run_name_edit.setMaxLength(160)
        self.run_name_edit.setPlaceholderText("시험 이름 (선택)")
        self.run_name_edit.setToolTip(
            "현재 시험에만 적용되는 이름입니다. 프로필에는 저장되지 않으며 결과 bundle 이름과 metadata에 사용됩니다."
        )
        self.start_spin = _time_spin()
        self.end_spin = _time_spin()
        self.compressor_spin = _time_spin()
        self.sampling_spin = _time_spin()
        self.sampling_spin.setDecimals(2)
        self.sampling_spin.setSuffix(" 회/초")
        self.sampling_spin.setValue(2.0)
        layout.addWidget(self.open_video_button, 0, 0)
        layout.addWidget(self.video_path_label, 0, 1, 1, 7)
        layout.addWidget(QLabel("시험 이름"), 1, 0)
        layout.addWidget(self.run_name_edit, 1, 1, 1, 7)
        layout.addWidget(QLabel("분석 시작"), 2, 0)
        layout.addWidget(self.start_spin, 2, 1)
        layout.addWidget(QLabel("분석 종료"), 2, 2)
        layout.addWidget(self.end_spin, 2, 3)
        layout.addWidget(QLabel("압축기 기동"), 2, 4)
        layout.addWidget(self.compressor_spin, 2, 5)
        layout.addWidget(QLabel("분석 빈도"), 2, 6)
        layout.addWidget(self.sampling_spin, 2, 7)
        for column in (1, 3, 5, 7):
            layout.setColumnStretch(column, 1)
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
        self.canvas.interactionTargetRequested.connect(self._overlay_interaction_target)
        self.settings.fieldChanged.connect(self._field_changed)
        self.settings.interactionTargetChanged.connect(self._settings_interaction_target)
        self.settings.addExclusionRequested.connect(self.add_exclusion)
        self.settings.deleteExclusionRequested.connect(self.delete_exclusion)
        self.settings.restoreDefaultsRequested.connect(self.restore_defaults)
        self.settings.editRoiRequested.connect(self.open_roi_editor)
        self.settings.resetGlassRequested.connect(self.reset_selected_glass)
        self.settings.initialStateConfirmRequested.connect(self._confirm_initial_state)
        self.detection_summary.initialStateRequested.connect(self._focus_initial_state)
        self.analysis_controller.progress.connect(self._analysis_progress)
        self.analysis_controller.completed.connect(self._analysis_completed)
        self.analysis_controller.failed.connect(self._analysis_failed)
        self.analysis_controller.cancelled.connect(self._analysis_cancelled)
        self.validation_panel.issueActivated.connect(self._route_validation_issue)
        self.debug_panel.exportRequested.connect(self.export_debug)
        self.run_name_edit.editingFinished.connect(self._session_changed)
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
        self.workbench.invalidate_initial_state_confirmations_for_recipe_transition(
            before,
            after,
        )
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
            artifact_proposer=self.artifact_proposer,
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

        self._record_recipe_change("분석 영역 편집", apply_edit)

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

        self._record_recipe_change("Glass 초기화", reset)

    def new_recipe(self) -> None:
        self.profile_lifecycle.new_recipe()

    def open_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "시험 영상 열기", "", SUPPORTED_VIDEO_FILTER)
        if not path:
            return
        try:
            self.workbench.open_video(path)
            self._sync_session_fields()
            self._load_frame(0.0, reset_view=True)
            self._refresh_all()
            self.schedule_preview()
            self._refresh_inline_validation()
        except Exception as exc:
            self._error("영상 열기 실패", str(exc))

    def add_glass(self) -> None:
        self._record_recipe_change("Glass 추가", self.workbench.add_glass)

    def delete_glass(self) -> None:
        self._record_recipe_change("Glass 삭제", self.workbench.delete_selected_glass)

    def select_glass(self, glass_id: str) -> None:
        if glass_id != self.workbench.selected_glass_id:
            self._clear_interaction_target()
        self.workbench.set_selected(glass_id)
        self._refresh_panels()
        self.schedule_preview()
        self._refresh_inline_validation()

    def set_enabled(self, glass_id: str, enabled: bool) -> None:
        def change() -> None:
            glass = next((g for g in self.workbench.recipe.glasses if g.id == glass_id), None)
            if glass is not None:
                self.workbench.set_glass_enabled(glass_id, enabled)

        self._record_recipe_change("분석 포함 변경", change)

    def _geometry_changed(self, glass_id: str, ellipse) -> None:
        self._record_recipe_change(
            "분석 영역 위치 또는 크기 변경",
            lambda: self.workbench.update_ellipse(glass_id, ellipse),
        )

    def _zero_changed(self, glass_id: str, y: float) -> None:
        self._record_recipe_change("기준점 이동", lambda: self.workbench.update_zero_line(glass_id, y))

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect) -> None:
        self._record_recipe_change(
            "검출 제외 영역 변경",
            lambda: self.workbench.update_exclusion(glass_id, zone_id, rect),
        )

    def add_exclusion(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None:
            added = []

            def change() -> None:
                added.append(self.workbench.add_exclusion(glass.id))

            self._record_recipe_change("검출 제외 영역 추가", change)
            if added:
                self._set_interaction_target(glass.id, "exclusion", added[0].id, reveal=True)

    def delete_exclusion(self, zone_id: str) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None:
            self._record_recipe_change(
                "검출 제외 영역 삭제", lambda: self.workbench.delete_exclusion(glass.id, zone_id)
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
                self.workbench.set_glass_enabled(glass.id, bool(value))
            elif key == "initial_state":
                self.workbench.update_initial_state(
                    glass.id,
                    InitialObservationState(value),
                )
            elif key == "mm_per_pixel":
                glass.mm_per_pixel = None if value is None else float(value)
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

        self._record_recipe_change("Glass 설정 변경", change)

    def _settings_interaction_target(self, target: str, zone_id) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None:
            self._set_interaction_target(glass.id, target, zone_id)

    def _overlay_interaction_target(self, glass_id: str, target: str, zone_id) -> None:
        if glass_id != self.workbench.selected_glass_id:
            self.select_glass(glass_id)
        self._set_interaction_target(glass_id, target, zone_id, reveal=True)

    def _set_interaction_target(
        self,
        glass_id: str,
        target: str | None,
        zone_id: str | None = None,
        *,
        reveal: bool = False,
    ) -> None:
        if glass_id != self.workbench.selected_glass_id:
            self._clear_interaction_target()
            return
        glass = self.workbench.selected_glass()
        if glass is None:
            self._clear_interaction_target()
            return
        if target == "exclusion":
            if zone_id is None or not any(zone.id == zone_id for zone in glass.geometry.exclusions):
                self._clear_interaction_target()
                return
        elif target not in {"geometry", "zero_line", "margin"}:
            self._clear_interaction_target()
            return
        self._interaction_glass_id = glass_id
        self._interaction_target = target
        self._interaction_zone_id = zone_id if target == "exclusion" else None
        self.settings.set_interaction_target(target, self._interaction_zone_id, reveal=reveal)
        self.canvas.set_active_target(target, self._interaction_zone_id)

    def _clear_interaction_target(self) -> None:
        self._interaction_glass_id = None
        self._interaction_target = None
        self._interaction_zone_id = None
        if hasattr(self, "settings"):
            self.settings.set_interaction_target(None)
        if hasattr(self, "canvas"):
            self.canvas.set_active_target(None)

    def _reconcile_interaction_target(self) -> None:
        if self._interaction_target is None:
            self.settings.set_interaction_target(None)
            self.canvas.set_active_target(None)
            return
        selected = self.workbench.selected_glass()
        if selected is None or selected.id != self._interaction_glass_id:
            self._clear_interaction_target()
            return
        if self._interaction_target == "exclusion" and not any(
            zone.id == self._interaction_zone_id for zone in selected.geometry.exclusions
        ):
            self._clear_interaction_target()
            return
        self.settings.set_interaction_target(
            self._interaction_target, self._interaction_zone_id
        )
        self.canvas.set_active_target(self._interaction_target, self._interaction_zone_id)

    def _session_changed(self) -> None:
        self.workbench.session.run_name = self.run_name_edit.text().strip()
        self.workbench.update_analysis_start(self.start_spin.value())
        self.workbench.session.analysis_end_sec = self.end_spin.value()
        self.workbench.session.compressor_start_sec = self.compressor_spin.value()
        self.workbench.session.sampling_fps = self.sampling_spin.value()
        self.workbench.mark_dirty()
        self._update_transport_markers()
        self._update_state()
        self._refresh_inline_validation()

    def toggle_play(self, playing: bool) -> None:
        self.playback_controller.toggle_play(playing)

    def _play_tick(self) -> None:
        self.playback_controller.play_tick()

    def step_frame(self, direction: int) -> None:
        self.playback_controller.step_frame(direction)

    def seek_fraction(self, fraction: float) -> None:
        self.playback_controller.seek_fraction(fraction)

    def _load_frame(self, timestamp: float, *, reset_view: bool = False) -> None:
        self.playback_controller.load_frame(timestamp, reset_view=reset_view)

    def schedule_preview(self) -> None:
        self.playback_controller.schedule_preview()

    def request_preview(self) -> None:
        self.playback_controller.request_preview()

    def _preview_ready(self, detection, artifacts) -> None:
        self.playback_controller.preview_ready(detection, artifacts)

    def _preview_failed(self, message: str) -> None:
        self.playback_controller.preview_failed(message)

    def _invalidate_preview(self, message: str) -> None:
        self.playback_controller.invalidate_preview(message)

    def _focus_initial_state(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        if self.workbench.session.video_metadata is not None:
            self._load_frame(self.workbench.session.analysis_start_sec)
            self.schedule_preview()
        self.settings.focus_field("initial_state")
        self.statusBar().showMessage(
            f"{glass.name}의 분석 시작 장면과 선택 상태를 비교한 뒤 '현재 Run 상태 확인'을 누르세요."
        )

    def _confirm_initial_state(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        if glass.initial_state is InitialObservationState.AUTO:
            QMessageBox.warning(
                self,
                "초기 상태 확인 불가",
                "AUTO는 최종 분석의 현재 Run 확인 값이 될 수 없습니다. 먼저 상태를 명시적으로 선택해 주세요.",
            )
            return
        if self.workbench.session.video_metadata is None:
            QMessageBox.warning(self, "초기 상태 확인 불가", "먼저 현재 Run의 시험 영상을 선택해 주세요.")
            return
        self._load_frame(self.workbench.session.analysis_start_sec)
        answer = QMessageBox.question(
            self,
            "현재 Run 초기 상태 확인",
            f"분석 시작 장면({self.workbench.session.analysis_start_sec:.3f}초)을 직접 확인했고 "
            f"{glass.name}의 시작 상태가 {glass.initial_state.value}임을 현재 Run에 대해 확인합니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.workbench.confirm_initial_state(glass.id)
        self._refresh_panels()
        self._refresh_inline_validation()
        self.statusBar().showMessage(f"{glass.name} 현재 Run 초기 상태 확인을 기록했습니다.")

    def set_recent_profile_history(self, history) -> None:
        self.profile_lifecycle.set_recent_profile_history(history)

    def _refresh_recent_profile_menu(self) -> None:
        self.profile_lifecycle.refresh_recent_profile_menu()

    def open_recent_profile(self, path: str | Path) -> None:
        self.profile_lifecycle.open_recent_profile(path)

    def _register_recent_profile(self) -> None:
        self.profile_lifecycle.register_recent_profile()

    def save_recipe(self) -> bool:
        return self.profile_lifecycle.save_recipe()

    def load_recipe(self) -> None:
        self.profile_lifecycle.load_recipe()

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
            self.statusBar().showMessage("수정하거나 확인할 Glass 항목이 없습니다.")
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
            message = (
                "분석 실행을 선택해 주세요."
                if self.workbench.state == WorkbenchState.VALIDATED
                else "설정 점검 완료 후 분석할 수 있습니다."
            )
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
        selected = self.workbench.selected_glass()
        self.settings.set_glass(selected)
        if selected is not None:
            confirmation = self.workbench.initial_state_confirmation(selected.id)
            confirmed = bool(
                confirmation is not None
                and confirmation.matches(selected.initial_state, self.workbench.session)
            )
            self.settings.set_initial_state_confirmation(
                confirmed,
                "현재 Run 확인됨" if confirmed else "현재 Run 확인 필요",
            )
        else:
            self.settings.set_initial_state_confirmation(False, "선택한 Glass 없음")
        self.canvas.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)
        self._reconcile_interaction_target()
        if self._last_validation is not None:
            self.settings.set_validation_issues(
                self._last_validation.issues, self.workbench.selected_glass_id
            )

    def _sync_session_fields(self) -> None:
        session = self.workbench.session
        self.run_name_edit.blockSignals(True)
        self.run_name_edit.setText(session.run_name)
        self.run_name_edit.blockSignals(False)
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

    def _sync_profile_context(self) -> None:
        recipe = self.workbench.recipe
        path = self.workbench.recipe_path
        self.profile_name_label.setText(recipe.name or "이름 없는 Profile")
        self.profile_path_label.setText(str(path) if path is not None else "아직 저장되지 않음")
        self.profile_path_label.setToolTip(str(path) if path is not None else "이 Profile은 아직 .oilrecipe 파일로 저장되지 않았습니다.")

    def _update_state(self) -> None:
        self._sync_profile_context()
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
        self.playback_controller.set_placeholder()

    def _error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def _confirm_unsaved_profile_close(self):
        return self.profile_lifecycle.confirm_unsaved_profile_close()

    def closeEvent(self, event) -> None:
        if not self.profile_lifecycle.accept_close(self._confirm_unsaved_profile_close):
            event.ignore()
            return
        super().closeEvent(event)
        if not event.isAccepted():
            return
        self.applicationCloseAccepted.emit()
        self.playback_controller.close()
        self.workbench.close_video()


def _time_spin() -> WheelSafeDoubleSpinBox:
    box = WheelSafeDoubleSpinBox()
    box.setRange(0, 1_000_000)
    box.setDecimals(3)
    box.setKeyboardTracking(False)
    box.setSuffix(" 초")
    return box
