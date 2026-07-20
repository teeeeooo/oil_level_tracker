from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import (
    QDockWidget, QDoubleSpinBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QSplitter, QToolBar, QVBoxLayout, QWidget,
)

from oil_tracker.config.defaults import DEFAULT_WINDOW_SIZE, PREVIEW_DEBOUNCE_MS, SUPPORTED_VIDEO_FILTER
from oil_tracker.domain.enums import InitialObservationState, JudgmentMode, WorkbenchState
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import DetectorSettings
from oil_tracker.ui.widgets.analysis_progress_dialog import AnalysisProgressDialog
from oil_tracker.ui.widgets.debug_panel import DebugPanel
from oil_tracker.ui.widgets.glass_list_panel import GlassListPanel
from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel
from oil_tracker.ui.widgets.transport_bar import TransportBar
from oil_tracker.ui.widgets.validation_panel import ValidationPanel
from oil_tracker.ui.widgets.video_overlay_canvas import VideoOverlayCanvas
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
        self.setWindowTitle("Rotary Oil Level Tracker — Recipe Workbench")
        self.resize(*DEFAULT_WINDOW_SIZE)
        self._build_ui()
        self._connect()
        self._refresh_all()

    def _build_ui(self) -> None:
        toolbar = QToolBar("Recipe", self); toolbar.setMovable(False); self.addToolBar(toolbar)
        self.actions = {}
        for key, text in (
            ("new", "새 Recipe"), ("load", "Recipe 불러오기"), ("save", "Recipe 저장"),
            ("validate", "Recipe 검증"), ("analyze", "분석 실행"), ("result", "결과 보기"), ("debug", "Debug mode"),
        ):
            action = QAction(text, self); toolbar.addAction(action); self.actions[key] = action
        self.actions["debug"].setCheckable(True)
        toolbar.addSeparator(); self.state_label = QLabel("상태: EMPTY"); toolbar.addWidget(self.state_label)

        self.glass_list = GlassListPanel(); self.canvas = VideoOverlayCanvas(); self.settings = GlassSettingsPanel(); self.transport = TransportBar()
        self.session_bar = self._build_session_bar()
        center = QWidget(); center_layout = QVBoxLayout(center); center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(self.session_bar); center_layout.addWidget(self.canvas, 1); center_layout.addWidget(self.transport)
        splitter = QSplitter(Qt.Orientation.Horizontal); splitter.addWidget(self.glass_list); splitter.addWidget(center); splitter.addWidget(self.settings)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1); splitter.setStretchFactor(2, 0); splitter.setSizes([210, 950, 320])
        self.setCentralWidget(splitter)

        self.validation_panel = ValidationPanel(); self.validation_dock = QDockWidget("Validation", self); self.validation_dock.setWidget(self.validation_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.validation_dock); self.validation_dock.hide()
        self.debug_panel = DebugPanel(); self.debug_dock = QDockWidget("Detector Debug", self); self.debug_dock.setWidget(self.debug_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.debug_dock); self.debug_dock.hide()
        self.statusBar().showMessage("Ready")

        self.play_timer = QTimer(self); self.preview_timer = QTimer(self); self.preview_timer.setSingleShot(True); self.preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)

    def _build_session_bar(self) -> QWidget:
        group = QGroupBox("Analysis Session")
        layout = QHBoxLayout(group)
        from PySide6.QtWidgets import QPushButton
        self.open_video_button = QPushButton("영상 열기")
        self.start_spin = _time_spin(); self.end_spin = _time_spin(); self.compressor_spin = _time_spin(); self.sampling_spin = _time_spin(); self.sampling_spin.setValue(2.0)
        for label, widget in (("", self.open_video_button), ("Start s", self.start_spin), ("End s", self.end_spin), ("Compressor s", self.compressor_spin), ("Sampling FPS", self.sampling_spin)):
            if label: layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        layout.addStretch(1)
        return group

    def _connect(self) -> None:
        self.actions["new"].triggered.connect(self.new_recipe)
        self.actions["load"].triggered.connect(self.load_recipe)
        self.actions["save"].triggered.connect(self.save_recipe)
        self.actions["validate"].triggered.connect(self.validate_workbench)
        self.actions["analyze"].triggered.connect(self.run_analysis)
        self.actions["result"].triggered.connect(self.open_result)
        self.actions["debug"].toggled.connect(self.debug_dock.setVisible)
        self.open_video_button.clicked.connect(self.open_video)
        self.glass_list.addRequested.connect(self.add_glass); self.glass_list.deleteRequested.connect(self.delete_glass)
        self.glass_list.selectionChanged.connect(self.select_glass); self.glass_list.enabledChanged.connect(self.set_enabled)
        self.canvas.geometryChanged.connect(self._geometry_changed); self.canvas.zeroLineChanged.connect(self._zero_changed)
        self.canvas.exclusionChanged.connect(self._exclusion_changed); self.canvas.glassSelected.connect(self.select_glass)
        self.settings.fieldChanged.connect(self._field_changed); self.settings.addExclusionRequested.connect(self.add_exclusion)
        self.settings.deleteExclusionRequested.connect(self.delete_exclusion); self.settings.restoreDefaultsRequested.connect(self.restore_defaults)
        self.transport.playToggled.connect(self.toggle_play); self.transport.stepRequested.connect(self.step_frame)
        self.transport.seekRequested.connect(self.seek_fraction); self.transport.seekReleased.connect(self.schedule_preview)
        self.transport.speedChanged.connect(lambda value: setattr(self, "playback_speed", value))
        self.play_timer.timeout.connect(self._play_tick); self.preview_timer.timeout.connect(self.request_preview)
        self.preview_controller.previewReady.connect(self._preview_ready); self.preview_controller.previewFailed.connect(self._preview_failed)
        self.analysis_controller.progress.connect(self._analysis_progress); self.analysis_controller.completed.connect(self._analysis_completed)
        self.analysis_controller.failed.connect(self._analysis_failed); self.analysis_controller.cancelled.connect(self._analysis_cancelled)
        self.validation_panel.issueActivated.connect(self._route_validation_issue)
        self.debug_panel.exportRequested.connect(self.export_debug)
        for spin in (self.start_spin, self.end_spin, self.compressor_spin, self.sampling_spin): spin.editingFinished.connect(self._session_changed)

    def new_recipe(self) -> None:
        wizard = NewRecipeWizard(self)
        if wizard.exec() == NewRecipeWizard.DialogCode.Accepted:
            if wizard.skipped:
                self.workbench.new_document(); self._set_placeholder(); self._refresh_all(); return
            metadata = wizard.video_metadata
            width, height = (metadata.width, metadata.height) if metadata else (1280, 720)
            self.workbench.new_document(width, height, wizard.recipe_name.text().strip() or "Untitled Recipe")
            self.workbench.recipe.description = wizard.description.toPlainText()
            if wizard.video_path.text():
                self.workbench.open_video(wizard.video_path.text())
                self.workbench.session.analysis_start_sec = wizard.start.value(); self.workbench.session.analysis_end_sec = wizard.end.value()
                self.workbench.session.compressor_start_sec = wizard.compressor.value(); self.workbench.session.sampling_fps = wizard.sampling.value()
                self._load_frame(self.workbench.session.analysis_start_sec)
            if wizard.create_glass.isChecked(): self.workbench.add_glass()
            self._refresh_all(); self.schedule_preview()

    def open_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "영상 열기", "", SUPPORTED_VIDEO_FILTER)
        if not path: return
        try:
            self.workbench.open_video(path); self._sync_session_fields(); self._load_frame(0.0); self._refresh_all(); self.schedule_preview()
        except Exception as exc: self._error("영상 열기 실패", str(exc))

    def add_glass(self) -> None:
        self.workbench.add_glass(); self._refresh_all(); self.schedule_preview()

    def delete_glass(self) -> None:
        self.workbench.delete_selected_glass(); self._refresh_all(); self.schedule_preview()

    def select_glass(self, glass_id: str) -> None:
        self.workbench.set_selected(glass_id); self._refresh_panels(); self.schedule_preview()

    def set_enabled(self, glass_id: str, enabled: bool) -> None:
        glass = next((g for g in self.workbench.recipe.glasses if g.id == glass_id), None)
        if glass: glass.enabled = enabled; self.workbench.mark_dirty(); self._refresh_all()

    def _geometry_changed(self, glass_id: str, ellipse) -> None:
        self.workbench.update_ellipse(glass_id, ellipse); self._refresh_panels(); self.schedule_preview()

    def _zero_changed(self, glass_id: str, y: float) -> None:
        self.workbench.update_zero_line(glass_id, y); self._refresh_panels(); self.schedule_preview()

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect) -> None:
        self.workbench.update_exclusion(glass_id, zone_id, rect); self._refresh_panels(); self.schedule_preview()

    def add_exclusion(self) -> None:
        glass = self.workbench.selected_glass()
        if glass: self.workbench.add_exclusion(glass.id); self._refresh_panels(); self.schedule_preview()

    def delete_exclusion(self, zone_id: str) -> None:
        glass = self.workbench.selected_glass()
        if glass: self.workbench.delete_exclusion(glass.id, zone_id); self._refresh_panels(); self.schedule_preview()

    def restore_defaults(self) -> None:
        glass = self.workbench.selected_glass()
        if glass: glass.detector_settings = DetectorSettings(); self.workbench.mark_dirty(); self._refresh_panels(); self.schedule_preview()

    def _field_changed(self, key: str, value) -> None:
        glass = self.workbench.selected_glass()
        if glass is None: return
        e = glass.geometry.ellipse
        if key in {"center_x", "center_y", "width", "height"}:
            cx = value if key == "center_x" else e.center_x; cy = value if key == "center_y" else e.center_y
            rx = value / 2 if key == "width" else e.radius_x; ry = value / 2 if key == "height" else e.radius_y
            self.workbench.update_ellipse(glass.id, EllipseGeometry(cx, cy, rx, ry))
        elif key == "zero_line_y": self.workbench.update_zero_line(glass.id, float(value))
        elif key == "name": glass.name = str(value); self.workbench.mark_dirty()
        elif key == "enabled": glass.enabled = bool(value); self.workbench.mark_dirty()
        elif key == "initial_state": glass.initial_state = InitialObservationState(value); self.workbench.mark_dirty()
        elif key == "mm_per_pixel": glass.mm_per_pixel = value; self.workbench.mark_dirty()
        elif key == "judgment_mode": glass.judgment_rule.mode = JudgmentMode(value); self.workbench.mark_dirty()
        elif key == "margin_ratio": glass.geometry.margin_ratio = float(value); self.workbench.mark_dirty()
        elif hasattr(glass.detector_settings, key): setattr(glass.detector_settings, key, value); self.workbench.mark_dirty()
        self._refresh_all(); self.schedule_preview()

    def _session_changed(self) -> None:
        self.workbench.session.analysis_start_sec = self.start_spin.value(); self.workbench.session.analysis_end_sec = self.end_spin.value()
        self.workbench.session.compressor_start_sec = self.compressor_spin.value(); self.workbench.session.sampling_fps = self.sampling_spin.value(); self.workbench.mark_dirty(); self._update_transport_markers(); self._update_state()

    def toggle_play(self, playing: bool) -> None:
        if playing and self.workbench.video_reader:
            fps = max(1.0, self.workbench.video_reader.metadata.fps); self.play_timer.start(max(15, int(1000 / fps)))
        else: self.play_timer.stop(); self.schedule_preview()

    def _play_tick(self) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None: self.transport.play.setChecked(False); return
        step = self.playback_speed / max(1.0, metadata.fps)
        target = self.current_time + step
        if target >= metadata.duration_sec: self.transport.play.setChecked(False); return
        self._load_frame(target)

    def step_frame(self, direction: int) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata: self._load_frame(max(0.0, min(metadata.duration_sec, self.current_time + direction / max(1.0, metadata.fps)))); self.schedule_preview()

    def seek_fraction(self, fraction: float) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata: self._load_frame(metadata.duration_sec * fraction); self.preview_timer.start()

    def _load_frame(self, timestamp: float) -> None:
        try:
            frame, frame_index, actual = self.workbench.read_at(timestamp)
            self.current_frame, self.current_frame_index, self.current_time = frame, frame_index, actual
            self.canvas.set_frame(frame); self.transport.set_position(actual, self.workbench.session.video_metadata.duration_sec if self.workbench.session.video_metadata else 0.0, frame_index)
        except Exception as exc: self.statusBar().showMessage(f"Frame decode: {exc}")

    def schedule_preview(self) -> None:
        self.preview_timer.start()

    def request_preview(self) -> None:
        glass = self.workbench.selected_glass()
        if glass is not None and self.current_frame is not None:
            self.statusBar().showMessage("Preview running..."); self.preview_controller.request(self.current_frame, glass, self.current_frame_index, self.current_time)

    def _preview_ready(self, detection, artifacts) -> None:
        self.canvas.set_detection(detection); self.debug_panel.set_artifacts(artifacts); self.last_debug_artifacts = artifacts
        self.statusBar().showMessage(f"Preview: {detection.fill_state.value}, confidence {detection.overall_confidence:.2f}")

    def _preview_failed(self, message: str) -> None: self.statusBar().showMessage(f"Preview failed: {message}")

    def save_recipe(self) -> None:
        path = self.workbench.recipe_path
        if path is None:
            selected, _ = QFileDialog.getSaveFileName(self, "Recipe 저장", "", "Oil Recipe (*.oilrecipe)")
            if not selected: return
            path = Path(selected)
        try: self.workbench.save(path); self._update_state(); self.statusBar().showMessage(f"Saved: {path}")
        except Exception as exc: self._error("저장 실패", str(exc))

    def load_recipe(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Recipe 불러오기", "", "Oil Recipe (*.oilrecipe)")
        if not selected: return
        try:
            self.workbench.load(Path(selected)); self._set_placeholder(); self._refresh_all()
        except Exception as exc: self._error("불러오기 실패", str(exc))

    def validate_workbench(self):
        result = self.workbench.validate(); self.validation_panel.set_result(result); self.validation_dock.show(); self._update_state()
        self.statusBar().showMessage("Validation passed" if result.is_ready else f"Validation: {len(result.errors)} error(s)")
        return result

    def _route_validation_issue(self, issue) -> None:
        if issue.glass_id: self.select_glass(issue.glass_id)
        field_map = {
            "zero_line_y": self.settings.zero, "margin": self.settings.margin, "mm_per_pixel": self.settings.scale,
            "geometry": self.settings.cx, "exclusions": self.settings.exclusions, "sampling_fps": self.sampling_spin,
            "input_video_path": self.open_video_button, "analysis_range": self.start_spin, "compressor_start": self.compressor_spin,
        }
        widget = field_map.get(issue.field)
        if widget is not None:
            widget.setFocus()
        self.statusBar().showMessage(issue.message)

    def run_analysis(self) -> None:
        result = self.validate_workbench()
        if not result.is_ready:
            QMessageBox.warning(self, "분석 불가", "Validation error를 먼저 수정하십시오."); return
        output = QFileDialog.getExistingDirectory(self, "Output root 선택", str(Path(self.workbench.session.input_video_path).parent))
        if not output: return
        self.workbench.session.output_directory = output; self.workbench.state = WorkbenchState.ANALYZING; self._update_state()
        self.progress_dialog = AnalysisProgressDialog(self); self.progress_dialog.cancelRequested.connect(self.analysis_controller.cancel)
        self.analysis_controller.start(self.workbench.recipe, self.workbench.session); self.progress_dialog.show()

    def _analysis_progress(self, update) -> None:
        if hasattr(self, "progress_dialog"): self.progress_dialog.update_progress(update)

    def _analysis_completed(self, result, output_path: str) -> None:
        if hasattr(self, "progress_dialog"): self.progress_dialog.accept()
        self.workbench.state = WorkbenchState.ANALYZED; self.last_result_path = output_path; self._update_state()
        QMessageBox.information(self, "분석 완료", f"{result.overall_state.value}\n{output_path}")

    def _analysis_failed(self, message: str) -> None:
        if hasattr(self, "progress_dialog"): self.progress_dialog.reject()
        self.workbench.state = WorkbenchState.ERROR; self._update_state(); self._error("분석 실패", message)

    def _analysis_cancelled(self) -> None:
        if hasattr(self, "progress_dialog"): self.progress_dialog.reject()
        self.workbench.state = WorkbenchState.VALIDATED; self._update_state(); self.statusBar().showMessage("Analysis cancelled")

    def open_result(self) -> None:
        if self.last_result_path: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(self.last_result_path) / "report.html")))
        else: QMessageBox.information(self, "결과", "현재 세션에 생성된 결과가 없습니다.")

    def export_debug(self) -> None:
        if self.last_debug_artifacts is None: return
        directory = QFileDialog.getExistingDirectory(self, "Debug export folder")
        if directory:
            paths = self.debug_renderer.export(Path(directory), self.current_frame_index, self.last_debug_artifacts)
            self.statusBar().showMessage(f"Exported {len(paths)} debug artifacts")

    def _refresh_all(self) -> None:
        self._refresh_panels(); self._sync_session_fields(); self._update_state()

    def _refresh_panels(self) -> None:
        self.glass_list.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)
        self.settings.set_glass(self.workbench.selected_glass())
        self.canvas.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)

    def _sync_session_fields(self) -> None:
        session = self.workbench.session
        for widget, value in ((self.start_spin, session.analysis_start_sec), (self.end_spin, session.analysis_end_sec or 0.0), (self.compressor_spin, session.compressor_start_sec or 0.0), (self.sampling_spin, session.sampling_fps)):
            widget.blockSignals(True); widget.setValue(value); widget.blockSignals(False)
        if session.video_metadata:
            self.sampling_spin.setMaximum(max(0.1, session.video_metadata.fps))
        self._update_transport_markers()

    def _update_transport_markers(self) -> None:
        session = self.workbench.session
        duration = session.video_metadata.duration_sec if session.video_metadata else 0.0
        self.transport.slider.set_markers(duration, session.analysis_start_sec, session.analysis_end_sec, session.compressor_start_sec)

    def _update_state(self) -> None:
        self.state_label.setText(f"상태: {self.workbench.state.value}")
        self.actions["analyze"].setEnabled(self.workbench.state == WorkbenchState.VALIDATED)
        self.actions["result"].setEnabled(bool(self.last_result_path))

    def _set_placeholder(self) -> None:
        self.current_frame = np.zeros((self.workbench.recipe.reference_frame_height, self.workbench.recipe.reference_frame_width, 3), dtype=np.uint8)
        self.canvas.set_frame(self.current_frame)

    def _error(self, title: str, message: str) -> None:
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event) -> None:
        self.workbench.close_video(); super().closeEvent(event)


def _time_spin() -> QDoubleSpinBox:
    box = QDoubleSpinBox(); box.setRange(0, 1_000_000); box.setDecimals(3); box.setKeyboardTracking(False); return box
