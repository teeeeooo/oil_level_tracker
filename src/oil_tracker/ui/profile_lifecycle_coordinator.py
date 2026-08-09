from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PySide6.QtGui import QAction, QUndoStack
from PySide6.QtWidgets import QFileDialog, QMenu, QMessageBox, QWidget

from oil_tracker.ui.wizard.new_recipe_wizard import NewRecipeWizard


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProfileLifecycleCallbacks:
    clear_interaction_target: Callable[[], None]
    set_placeholder: Callable[[], None]
    load_frame: Callable[[float, bool], None]
    refresh_all: Callable[[], None]
    refresh_inline_validation: Callable[[], object]
    schedule_preview: Callable[[], None]
    update_state: Callable[[], None]
    show_status: Callable[[str], None]
    report_error: Callable[[str, str], None]


class ProfileLifecycleCoordinator:
    """Own Profile UI lifecycle state without owning the MainWindow implementation."""

    def __init__(
        self,
        workbench,
        undo_stack: QUndoStack,
        recent_menu: QMenu,
        load_action: QAction,
        callbacks: ProfileLifecycleCallbacks,
        parent: QWidget,
    ) -> None:
        self.workbench = workbench
        self.undo_stack = undo_stack
        self.recent_menu = recent_menu
        self.load_action = load_action
        self.callbacks = callbacks
        self.parent = parent
        self.recent_profile_history = None
        self.pending_profile_path: Path | None = None
        self.refresh_recent_profile_menu()

    def new_recipe(self) -> None:
        wizard = NewRecipeWizard(
            reader_factory=self.workbench.reader_factory,
            parent=self.parent,
        )
        if wizard.exec() != NewRecipeWizard.DialogCode.Accepted:
            return
        self.callbacks.clear_interaction_target()
        if wizard.skipped:
            self.workbench.new_document()
            self.undo_stack.clear()
            self.callbacks.set_placeholder()
            self.callbacks.refresh_all()
            self.callbacks.refresh_inline_validation()
            return

        metadata = wizard.video_metadata
        width, height = (metadata.width, metadata.height) if metadata else (1280, 720)
        self.workbench.new_document(
            width,
            height,
            wizard.recipe_name.text().strip() or "새 유면 분석 프로필",
        )
        self.undo_stack.clear()
        self.workbench.recipe.description = wizard.description.toPlainText()
        if wizard.video_path.text():
            self.workbench.open_video(wizard.video_path.text())
            self.workbench.session.analysis_start_sec = wizard.start.value()
            self.workbench.session.analysis_end_sec = wizard.end.value()
            self.workbench.session.compressor_start_sec = wizard.compressor.value()
            self.workbench.session.sampling_fps = wizard.sampling.value()
            self.callbacks.load_frame(
                self.workbench.session.analysis_start_sec,
                True,
            )
        if wizard.create_glass.isChecked():
            self.workbench.add_glass()
        self.callbacks.refresh_all()
        self.callbacks.schedule_preview()
        self.callbacks.refresh_inline_validation()

    def set_recent_profile_history(self, history) -> None:
        self.recent_profile_history = history
        self.refresh_recent_profile_menu()

    def refresh_recent_profile_menu(self) -> None:
        self.recent_menu.clear()
        entries = (
            self.recent_profile_history.entries()
            if self.recent_profile_history is not None
            else ()
        )
        if entries:
            for index, entry in enumerate(entries):
                name = entry.profile_name or Path(entry.path).stem
                label = f"{name} — {entry.path}"
                if not entry.is_available():
                    label += " (경로를 찾을 수 없음)"
                action = self.recent_menu.addAction(label)
                action.setObjectName(f"recentProfileAction{index}")
                action.setData(entry.path)
                action.setEnabled(entry.is_available())
                action.triggered.connect(
                    lambda _checked=False, path=entry.path: self.open_recent_profile(path)
                )
            self.recent_menu.addSeparator()
        else:
            empty = self.recent_menu.addAction("최근 프로필 없음")
            empty.setEnabled(False)
        manual = self.recent_menu.addAction("다른 프로필 파일 선택…")
        manual.setObjectName("otherProfileFileAction")
        manual.triggered.connect(lambda _checked=False: self.load_action.trigger())

    def open_recent_profile(self, path: str | Path) -> None:
        self.pending_profile_path = Path(path)
        self.load_action.trigger()

    def register_recent_profile(self) -> None:
        if self.recent_profile_history is None or self.workbench.recipe_path is None:
            return
        try:
            self.recent_profile_history.record_recipe(
                self.workbench.recipe_path,
                self.workbench.recipe,
            )
        except Exception as exc:
            LOGGER.warning("Recent profile history could not be updated: %s", exc)
        self.refresh_recent_profile_menu()

    def save_recipe(self) -> bool:
        path = self.workbench.recipe_path
        if path is None:
            selected, _ = QFileDialog.getSaveFileName(
                self.parent,
                "분석 프로필 저장",
                "",
                "유면 분석 프로필 (*.oilrecipe)",
            )
            if not selected:
                return False
            path = Path(selected)
        try:
            self.workbench.save(path)
            self.register_recent_profile()
            self.callbacks.update_state()
            actual_path = self.workbench.recipe_path or path
            self.callbacks.show_status(f"프로필 저장 완료: {actual_path}")
            return True
        except Exception as exc:
            self.callbacks.report_error("프로필 저장 실패", str(exc))
            return False

    def load_recipe(self) -> None:
        path = self.pending_profile_path
        self.pending_profile_path = None
        if path is None:
            selected, _ = QFileDialog.getOpenFileName(
                self.parent,
                "분석 프로필 열기",
                "",
                "유면 분석 프로필 (*.oilrecipe)",
            )
            if not selected:
                return
            path = Path(selected)
        try:
            self.callbacks.clear_interaction_target()
            self.workbench.load(path)
            self.undo_stack.clear()
            self.callbacks.set_placeholder()
            self.callbacks.refresh_all()
            self.callbacks.refresh_inline_validation()
            self.register_recent_profile()
        except Exception as exc:
            self.callbacks.report_error("프로필 열기 실패", str(exc))

    def confirm_unsaved_profile_close(self):
        return QMessageBox.warning(
            self.parent,
            "저장되지 않은 Profile 변경",
            "현재 Profile에 아직 안전하게 저장되지 않은 변경이 있습니다.\n\n"
            "저장 후 닫기: 기존 Profile 저장 절차로 저장한 뒤 닫습니다.\n"
            "버리고 닫기: Profile 파일을 변경하지 않고 현재 변경을 버립니다.\n"
            "취소: 닫기를 중단하고 Workbench로 돌아갑니다.",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )

    def accept_close(self, confirm: Callable[[], QMessageBox.StandardButton]) -> bool:
        if not self.workbench.profile_has_unsaved_changes:
            return True
        answer = confirm()
        if answer == QMessageBox.StandardButton.Save:
            return self.save_recipe()
        return answer == QMessageBox.StandardButton.Discard
