from __future__ import annotations

from copy import deepcopy

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QMessageBox

from oil_tracker.application.observation_settings_copy import (
    GlassSettingsCopyError,
    copy_observation_window_settings,
)
from oil_tracker.ui.readiness import glass_readiness_by_id
from oil_tracker.ui.widgets.glass_settings_copy_dialog import GlassSettingsCopyDialog


class ObservationSettingsCopyCoordinator(QObject):
    """Connect the settings-copy dialog to the existing Workbench mutation flow."""

    def __init__(self, window) -> None:
        super().__init__(window)
        self.window = window
        self.window.glass_list.copyRequested.connect(self.open_dialog)

    def open_dialog(self) -> None:
        workbench = self.window.workbench
        source = workbench.selected_glass()
        if source is None or len(workbench.recipe.glasses) <= 1:
            return

        validation = self.window._last_validation or self.window._refresh_inline_validation()
        readiness = glass_readiness_by_id(workbench.recipe.glasses, validation)
        dialog = self._create_dialog(source.id, readiness)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        request = dialog.copy_request()
        try:
            planned = copy_observation_window_settings(deepcopy(workbench.recipe), request)
        except GlassSettingsCopyError as exc:
            QMessageBox.warning(self.window, "설정 복사 불가", str(exc))
            return

        if planned.is_no_op:
            QMessageBox.information(self.window, "설정 복사", "복사할 변경 사항이 없습니다.")
            return

        applied = {}

        def change() -> None:
            applied["result"] = copy_observation_window_settings(workbench.recipe, request)
            workbench.set_selected(source.id)
            workbench.mark_dirty()

        try:
            self.window._record_recipe_change("관찰창 설정 복사", change)
        except GlassSettingsCopyError as exc:
            QMessageBox.warning(self.window, "설정 복사 불가", str(exc))
            return

        result = applied.get("result", planned)
        option_summary = ", ".join(request.options.selected_labels())
        self.window.statusBar().showMessage(
            f"관찰창 {len(result.changed_target_ids)}개에 {option_summary}을(를) 복사했습니다.",
            7000,
        )

    def _create_dialog(self, source_glass_id: str, readiness):
        return GlassSettingsCopyDialog(
            self.window.workbench.recipe,
            source_glass_id,
            readiness,
            self.window,
        )
