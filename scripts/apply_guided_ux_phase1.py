from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"missing patch anchor: {label}")
    return text.replace(old, new, 1)


path = Path("src/oil_tracker/ui/main_window.py")
text = path.read_text(encoding="utf-8")

text = replace_once(
    text,
    "from PySide6.QtGui import QAction, QDesktopServices\n",
    "from PySide6.QtGui import QAction, QDesktopServices, QKeySequence, QUndoStack\n",
    "QtGui imports",
)
text = replace_once(
    text,
    "from oil_tracker.domain.recipe import DetectorSettings\n",
    "from oil_tracker.domain.recipe import DetectorSettings, InspectionRecipe\n",
    "recipe imports",
)
text = replace_once(
    text,
    "    result_state_label,\n    workbench_state_label,\n)",
    "    result_state_label,\n    validation_issue_message,\n    workbench_state_label,\n)",
    "presentation imports",
)
text = replace_once(
    text,
    "from oil_tracker.ui.widgets.analysis_progress_dialog import AnalysisProgressDialog\n",
    "from oil_tracker.ui.undo import RecipeSnapshotCommand\nfrom oil_tracker.ui.widgets.analysis_progress_dialog import AnalysisProgressDialog\nfrom oil_tracker.ui.widgets.bottom_action_bar import BottomActionBar\n",
    "widget imports one",
)
text = replace_once(
    text,
    "from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel\n",
    "from oil_tracker.ui.widgets.glass_settings_panel import GlassSettingsPanel\nfrom oil_tracker.ui.widgets.roi_editor_dialog import RoiEditorDialog\n",
    "widget imports two",
)
text = replace_once(
    text,
    "        self.last_result_path = \"\"\n        self.last_debug_artifacts = None\n        self.setWindowTitle",
    "        self.last_result_path = \"\"\n        self.last_debug_artifacts = None\n        self.undo_stack = QUndoStack(self)\n        self._last_validation = None\n        self.setWindowTitle",
    "init history",
)
text = replace_once(
    text,
    "        self._connect()\n        self._refresh_all()\n",
    "        self._connect()\n        self._refresh_all()\n        self._refresh_inline_validation()\n",
    "initial validation",
)

old_toolbar = '''        self.actions = {}
        definitions = (
            ("new", "새 프로필", QStyle.StandardPixmap.SP_FileIcon),
            ("load", "프로필 열기", QStyle.StandardPixmap.SP_DialogOpenButton),
            ("save", "프로필 저장", QStyle.StandardPixmap.SP_DialogSaveButton),
            ("validate", "설정 점검", QStyle.StandardPixmap.SP_DialogApplyButton),
            ("analyze", "분석 실행", QStyle.StandardPixmap.SP_MediaPlay),
            ("result", "결과 보고서", QStyle.StandardPixmap.SP_FileDialogDetailedView),
            ("debug", "ROI 상세보기", QStyle.StandardPixmap.SP_ComputerIcon),
        )
        for key, text, icon in definitions:
            action = QAction(self.style().standardIcon(icon), text, self)
            toolbar.addAction(action)
            button = toolbar.widgetForAction(action)
            if isinstance(button, QToolButton):
                button.setObjectName("primaryToolButton" if key == "analyze" else "toolbarButton")
                button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.actions[key] = action
            if key in {"save", "validate", "result"}:
                toolbar.addSeparator()
        self.actions["debug"].setCheckable(True)
        toolbar.addSeparator()
'''
new_toolbar = '''        self.actions = {}
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
'''
text = replace_once(text, old_toolbar, new_toolbar, "toolbar simplification")

text = replace_once(
    text,
    "        self.splitter.setSizes([left, max(660, width - left - right), right])\n        self.setCentralWidget(self.splitter)\n",
    "        self.splitter.setSizes([left, max(660, width - left - right), right])\n\n        self.action_bar = BottomActionBar()\n        shell = QWidget()\n        shell_layout = QVBoxLayout(shell)\n        shell_layout.setContentsMargins(0, 0, 0, 0)\n        shell_layout.setSpacing(0)\n        shell_layout.addWidget(self.splitter, 1)\n        shell_layout.addWidget(self.action_bar)\n        self.setCentralWidget(shell)\n",
    "bottom action bar layout",
)

text = replace_once(
    text,
    "        self.debug_dock.visibilityChanged.connect(self._sync_debug_action)\n        self.open_video_button.clicked.connect(self.open_video)\n",
    "        self.debug_dock.visibilityChanged.connect(self._sync_debug_action)\n        self.action_bar.validateRequested.connect(self.actions[\"validate\"].trigger)\n        self.action_bar.saveRequested.connect(self.actions[\"save\"].trigger)\n        self.action_bar.analyzeRequested.connect(self.actions[\"analyze\"].trigger)\n        self.open_video_button.clicked.connect(self.open_video)\n",
    "action bar connections",
)
text = replace_once(
    text,
    "        self.settings.restoreDefaultsRequested.connect(self.restore_defaults)\n        self.transport.playToggled.connect(self.toggle_play)\n",
    "        self.settings.restoreDefaultsRequested.connect(self.restore_defaults)\n        self.settings.editRoiRequested.connect(self.open_roi_editor)\n        self.settings.resetGlassRequested.connect(self.reset_selected_glass)\n        self.transport.playToggled.connect(self.toggle_play)\n",
    "settings connections",
)

marker = '''        for spin in (self.start_spin, self.end_spin, self.compressor_spin, self.sampling_spin):
            spin.editingFinished.connect(self._session_changed)

    def new_recipe(self) -> None:
'''
methods = '''        for spin in (self.start_spin, self.end_spin, self.compressor_spin, self.sampling_spin):
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
        result = self.workbench.validate()
        self._last_validation = result
        selected_id = self.workbench.selected_glass_id
        self.settings.set_validation_issues(result.issues, selected_id)
        self.validation_panel.set_result(result)
        self.action_bar.set_validation_result(result)
        self._update_state()
        return result

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
'''
text = replace_once(text, marker, methods, "history and ROI methods")

text = replace_once(
    text,
    "                self.workbench.new_document()\n                self._set_placeholder()",
    "                self.workbench.new_document()\n                self.undo_stack.clear()\n                self._set_placeholder()",
    "new blank undo clear",
)
text = replace_once(
    text,
    "            self.workbench.new_document(width, height, wizard.recipe_name.text().strip() or \"새 유면 분석 프로필\")\n            self.workbench.recipe.description",
    "            self.workbench.new_document(width, height, wizard.recipe_name.text().strip() or \"새 유면 분석 프로필\")\n            self.undo_stack.clear()\n            self.workbench.recipe.description",
    "new wizard undo clear",
)
text = replace_once(
    text,
    "            self._refresh_all()\n            self.schedule_preview()\n\n    def open_video",
    "            self._refresh_all()\n            self.schedule_preview()\n            self._refresh_inline_validation()\n\n    def open_video",
    "new wizard validation",
)
text = replace_once(
    text,
    "            self._refresh_all()\n            self.schedule_preview()\n        except Exception as exc:\n            self._error(\"영상 열기 실패\", str(exc))",
    "            self._refresh_all()\n            self.schedule_preview()\n            self._refresh_inline_validation()\n        except Exception as exc:\n            self._error(\"영상 열기 실패\", str(exc))",
    "open video validation",
)

old_handlers = '''    def add_glass(self) -> None:
        self.workbench.add_glass()
        self._refresh_all()
        self.schedule_preview()

    def delete_glass(self) -> None:
        self.workbench.delete_selected_glass()
        self._refresh_all()
        self.schedule_preview()

    def select_glass(self, glass_id: str) -> None:
        self.workbench.set_selected(glass_id)
        self._refresh_panels()
        self.schedule_preview()

    def set_enabled(self, glass_id: str, enabled: bool) -> None:
        glass = next((g for g in self.workbench.recipe.glasses if g.id == glass_id), None)
        if glass:
            glass.enabled = enabled
            self.workbench.mark_dirty()
            self._refresh_all()

    def _geometry_changed(self, glass_id: str, ellipse) -> None:
        self.workbench.update_ellipse(glass_id, ellipse)
        self._refresh_panels()
        self.schedule_preview()

    def _zero_changed(self, glass_id: str, y: float) -> None:
        self.workbench.update_zero_line(glass_id, y)
        self._refresh_panels()
        self.schedule_preview()

    def _exclusion_changed(self, glass_id: str, zone_id: str, rect) -> None:
        self.workbench.update_exclusion(glass_id, zone_id, rect)
        self._refresh_panels()
        self.schedule_preview()

    def add_exclusion(self) -> None:
        glass = self.workbench.selected_glass()
        if glass:
            self.workbench.add_exclusion(glass.id)
            self._refresh_panels()
            self.schedule_preview()

    def delete_exclusion(self, zone_id: str) -> None:
        glass = self.workbench.selected_glass()
        if glass:
            self.workbench.delete_exclusion(glass.id, zone_id)
            self._refresh_panels()
            self.schedule_preview()

    def restore_defaults(self) -> None:
        glass = self.workbench.selected_glass()
        if glass:
            glass.detector_settings = DetectorSettings()
            self.workbench.mark_dirty()
            self._refresh_panels()
            self.schedule_preview()

    def _field_changed(self, key: str, value) -> None:
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
        self._refresh_all()
        self.schedule_preview()
'''
new_handlers = '''    def add_glass(self) -> None:
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
'''
text = replace_once(text, old_handlers, new_handlers, "undoable handlers")

text = replace_once(
    text,
    "        self._update_transport_markers()\n        self._update_state()\n\n    def toggle_play",
    "        self._update_transport_markers()\n        self._update_state()\n        self._refresh_inline_validation()\n\n    def toggle_play",
    "session inline validation",
)
text = replace_once(
    text,
    "            self.workbench.load(Path(selected))\n            self._set_placeholder()\n            self._refresh_all()",
    "            self.workbench.load(Path(selected))\n            self.undo_stack.clear()\n            self._set_placeholder()\n            self._refresh_all()\n            self._refresh_inline_validation()",
    "load undo and validation",
)
text = replace_once(
    text,
    '''    def validate_workbench(self):
        result = self.workbench.validate()
        self.validation_panel.set_result(result)
        self.validation_dock.show()
        self._update_state()
''',
    '''    def validate_workbench(self):
        result = self._refresh_inline_validation()
        self.validation_panel.set_result(result)
        self.validation_dock.show()
''',
    "validate workbench reuse",
)
old_route = '''    def _route_validation_issue(self, issue) -> None:
        if issue.glass_id:
            self.select_glass(issue.glass_id)
        field_map = {
            "zero_line_y": self.settings.zero,
            "margin": self.settings.margin,
            "mm_per_pixel": self.settings.scale,
            "geometry": self.settings.cx,
            "exclusions": self.settings.exclusions,
            "sampling_fps": self.sampling_spin,
            "input_video_path": self.open_video_button,
            "analysis_range": self.start_spin,
            "compressor_start": self.compressor_spin,
        }
        widget = field_map.get(issue.field)
        if widget is not None:
            widget.setFocus()
        self.statusBar().showMessage(issue.message)
'''
new_route = '''    def _route_validation_issue(self, issue) -> None:
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
'''
text = replace_once(text, old_route, new_route, "validation routing")
text = replace_once(
    text,
    "        self.settings.set_glass(self.workbench.selected_glass())\n        self.canvas.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)\n",
    "        self.settings.set_glass(self.workbench.selected_glass())\n        self.canvas.set_glasses(self.workbench.recipe.glasses, self.workbench.selected_glass_id)\n        if self._last_validation is not None:\n            self.settings.set_validation_issues(\n                self._last_validation.issues, self.workbench.selected_glass_id\n            )\n",
    "refresh inline panel",
)
text = replace_once(
    text,
    "        self.actions[\"analyze\"].setEnabled(self.workbench.state == WorkbenchState.VALIDATED)\n        self.actions[\"result\"].setEnabled(bool(self.last_result_path))\n",
    "        self.actions[\"analyze\"].setEnabled(self.workbench.state == WorkbenchState.VALIDATED)\n        self.actions[\"result\"].setEnabled(bool(self.last_result_path))\n        if self.workbench.state == WorkbenchState.ANALYZING:\n            self.action_bar.analyze_button.setEnabled(False)\n        elif self._last_validation is not None:\n            self.action_bar.set_validation_result(self._last_validation)\n",
    "state action bar",
)

path.write_text(text, encoding="utf-8")

qss_path = Path("src/oil_tracker/resources/styles/app.qss")
qss = qss_path.read_text(encoding="utf-8")
marker = "/* Guided workbench phase 1 */"
if marker not in qss:
    qss += '''

/* Guided workbench phase 1 */
QWidget#guidedActionBar {
    background: #ffffff;
    border-top: 1px solid #c7d1dc;
}

QLabel#guidedStatusLabel {
    padding: 5px 9px;
    border-radius: 5px;
    background: #eef3f7;
    color: #33485d;
    font-weight: 700;
}

QLabel#guidedStatusLabel[validationState="error"] {
    background: #fde7e7;
    color: #9d2424;
}

QLabel#guidedStatusLabel[validationState="warning"] {
    background: #fff2d5;
    color: #855a08;
}

QLabel#guidedStatusLabel[validationState="ready"] {
    background: #dff3e7;
    color: #1f6b3c;
}

QPushButton#primaryActionButton {
    min-width: 110px;
    background: #1769aa;
    color: white;
    border-color: #125b94;
    font-weight: 800;
}

QPushButton#primaryActionButton:hover {
    background: #1d78bd;
}

QToolButton#advancedToggle {
    min-height: 28px;
    padding: 3px 8px;
    border: 1px solid #c6d1dc;
    border-radius: 5px;
    background: #f6f9fc;
    color: #2a3b4d;
    font-weight: 700;
}

QLabel#inlineValidationMessage {
    padding: 3px 5px;
    border-radius: 4px;
    font-size: 9pt;
}

QLabel#inlineValidationMessage[validationState="error"] {
    background: #fdeaea;
    color: #9e2424;
}

QLabel#inlineValidationMessage[validationState="warning"] {
    background: #fff4d8;
    color: #7c570b;
}

QLineEdit[validationState="error"],
QDoubleSpinBox[validationState="error"],
QSpinBox[validationState="error"],
QComboBox[validationState="error"],
QListWidget[validationState="error"],
QLabel#roiSummaryCard[validationState="error"] {
    border: 2px solid #c43c3c;
}

QLineEdit[validationState="warning"],
QDoubleSpinBox[validationState="warning"],
QSpinBox[validationState="warning"],
QComboBox[validationState="warning"],
QListWidget[validationState="warning"],
QLabel#roiSummaryCard[validationState="warning"] {
    border: 2px solid #d99a24;
}

QLabel#roiEditorHint {
    padding: 7px 9px;
    border: 1px solid #cbd7e2;
    border-radius: 5px;
    background: #f5f8fb;
    color: #33485d;
}
'''
    qss_path.write_text(qss, encoding="utf-8")
