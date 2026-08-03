from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetError
from oil_tracker.adapters.storage.recent_result_history import RecentResultHistory
from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleError, ResultBundleReader
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.ui.analysis_completion_summary import build_final_run_summary
from oil_tracker.ui.result_actions import ResultActionError, ResultActionService
from oil_tracker.ui.widgets.analysis_complete_dialog import AnalysisCompleteDialog


LOGGER = logging.getLogger(__name__)


class AnalysisCompletionCoordinator(QObject):
    def __init__(
        self,
        window,
        result_review_coordinator,
        same_profile_coordinator,
        action_service: ResultActionService,
        bundle_reader: ResultBundleReader | None = None,
        recent_result_history: RecentResultHistory | None = None,
    ) -> None:
        super().__init__(window)
        self.window = window
        self.result_review_coordinator = result_review_coordinator
        self.same_profile_coordinator = same_profile_coordinator
        self.action_service = action_service
        self.bundle_reader = bundle_reader or ResultBundleReader()
        self.recent_result_history = recent_result_history
        self.dialog: AnalysisCompleteDialog | None = None
        self._active_actions: set[str] = set()
        window.applicationCloseAccepted.connect(self.close)

    def analysis_completed(self, result, output_path: str) -> None:
        progress_dialog = getattr(self.window, "progress_dialog", None)
        if progress_dialog is not None:
            mark_completed = getattr(progress_dialog, "mark_completed", None)
            if callable(mark_completed):
                mark_completed()
            progress_dialog.accept()
        self.window.workbench.state = WorkbenchState.ANALYZED
        self.window.last_result_path = output_path
        self._register_recent_result(output_path)
        self.window._update_state()
        self.show(result, output_path)

    def show(self, result, output_path: str | Path) -> None:
        if self.dialog is not None:
            self.dialog.close()
        summary = self._build_final_run_summary(result, output_path)
        dialog = AnalysisCompleteDialog(result, output_path, self.window, summary=summary)
        self.dialog = dialog
        dialog.reviewRequested.connect(lambda: self._run_once("review", lambda: self._open_viewer(output_path)))
        dialog.reportRequested.connect(lambda: self._run_once("report", lambda: self._open_report(output_path)))
        dialog.folderRequested.connect(lambda: self._run_once("folder", lambda: self._open_folder(output_path)))
        dialog.sameProfileRequested.connect(lambda: self._run_once("same_profile", lambda: self._same_profile(output_path)))
        dialog.finished.connect(self._dialog_finished)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _build_final_run_summary(self, result, output_path: str | Path):
        try:
            bundle = self.bundle_reader.read(output_path)
            return build_final_run_summary(result, output_path, bundle)
        except Exception:
            LOGGER.warning(
                "Finalized bundle metadata could not be loaded for completion summary: %s",
                output_path,
                exc_info=True,
            )
            return build_final_run_summary(result, output_path)

    def _register_recent_result(self, output_path: str | Path) -> None:
        if self.recent_result_history is None:
            return
        try:
            self.recent_result_history.register_path(output_path)
        except Exception:
            LOGGER.warning(
                "Completed result could not be registered in recent history: %s",
                output_path,
                exc_info=True,
            )

    def open_last_report(self) -> None:
        if not self.window.last_result_path:
            QMessageBox.information(self.window, "결과 보고서", "현재 작업에서 생성된 결과가 없습니다.")
            return
        self._open_report(self.window.last_result_path)

    def _run_once(self, key: str, action) -> None:
        if key in self._active_actions:
            return
        self._active_actions.add(key)
        try:
            action()
        finally:
            self._active_actions.discard(key)

    def _open_viewer(self, output_path) -> None:
        if not self.result_review_coordinator.open_bundle(output_path):
            QMessageBox.warning(
                self.dialog or self.window,
                "결과 영상 검토",
                "Viewer를 열지 못했습니다. 분석 결과는 ANALYZED 상태로 유지됩니다.",
            )

    def _open_report(self, output_path) -> None:
        self._safe_action("결과 보고서 열기", lambda: self.action_service.open_report(output_path))

    def _open_folder(self, output_path) -> None:
        self._safe_action("결과 폴더 열기", lambda: self.action_service.open_folder(output_path))

    def _same_profile(self, output_path) -> None:
        try:
            bundle = self.bundle_reader.read(output_path)
        except ResultBundleError as exc:
            QMessageBox.warning(self.dialog or self.window, "같은 프로필로 새 영상 분석", str(exc))
            return
        except Exception as exc:
            LOGGER.exception("Completion bundle reload failed")
            QMessageBox.critical(
                self.dialog or self.window,
                "같은 프로필로 새 영상 분석",
                f"결과 bundle을 다시 읽을 수 없습니다: {exc}",
            )
            return
        self.same_profile_coordinator.start(bundle)

    def _safe_action(self, title: str, action) -> bool:
        try:
            action()
            return True
        except (BundleAssetError, ResultActionError) as exc:
            QMessageBox.warning(self.dialog or self.window, title, str(exc))
        except Exception as exc:
            LOGGER.exception("Analysis completion result action failed")
            QMessageBox.critical(self.dialog or self.window, title, f"작업을 완료할 수 없습니다: {exc}")
        return False

    def _dialog_finished(self, _result: int) -> None:
        self.dialog = None
        self._active_actions.clear()

    def close(self) -> None:
        if self.dialog is not None:
            self.dialog.close()
            self.dialog = None
        self._active_actions.clear()
