from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox

from oil_tracker.config.defaults import SUPPORTED_VIDEO_FILTER
from oil_tracker.domain.enums import WorkbenchState
from oil_tracker.ui.controllers.workbench_controller import WorkbenchReplacementError


LOGGER = logging.getLogger(__name__)


class SameProfileAnalysisCoordinator(QObject):
    """Prepare a new Workbench document from a result snapshot without mutating either source."""

    def __init__(self, window, parent=None) -> None:
        super().__init__(parent or window)
        self.window = window
        self._prepared = None

    def start(self, bundle) -> bool:
        if self.window.workbench.state == WorkbenchState.ANALYZING:
            QMessageBox.warning(
                self.window,
                "같은 프로필로 새 영상 분석",
                "현재 분석이 진행 중입니다. 분석이 끝나거나 취소된 뒤 다시 시도해 주세요.",
            )
            return False
        selected, _ = QFileDialog.getOpenFileName(
            self.window,
            "같은 프로필에 적용할 새 시험 영상 선택",
            str(Path(bundle.source_video_path).parent if bundle.source_video_path else bundle.root),
            SUPPORTED_VIDEO_FILTER,
        )
        if not selected:
            return False
        try:
            self._prepared = self.window.workbench.prepare_same_profile_video(
                bundle.recipe,
                bundle.session.sampling_fps,
                selected,
            )
        except WorkbenchReplacementError as exc:
            QMessageBox.warning(self.window, "새 영상 적용 불가", str(exc))
            return False
        except Exception as exc:
            LOGGER.exception("Same-profile video preparation failed")
            QMessageBox.critical(
                self.window,
                "새 영상 열기 실패",
                f"현재 Workbench는 변경하지 않았습니다.\n{exc}",
            )
            return False

        if self.window.workbench.state in {
            WorkbenchState.DRAFT,
            WorkbenchState.DRAFT_DIRTY,
            WorkbenchState.VALIDATED,
            WorkbenchState.ANALYZED,
        }:
            answer = QMessageBox.question(
                self.window,
                "현재 Workbench 교체 확인",
                "현재 작성 중인 프로필과 시험 영상이 새 작업으로 교체됩니다.\n"
                "기존 결과 bundle과 열려 있는 Result Review Viewer는 변경되지 않습니다.\n\n"
                "계속하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.cancel()
                return False
        try:
            self._commit()
            return True
        except Exception as exc:
            LOGGER.exception("Same-profile Workbench commit failed")
            QMessageBox.critical(
                self.window,
                "새 분석 준비 실패",
                f"새 작업을 적용하지 못했습니다.\n{exc}",
            )
            return False
        finally:
            self.cancel()

    def _commit(self) -> None:
        prepared = self._prepared
        if prepared is None:
            raise WorkbenchReplacementError("준비된 새 분석 작업이 없습니다.")
        window = self.window
        window.play_timer.stop()
        window.preview_timer.stop()
        window.workbench.commit_same_profile_video(prepared)
        window.undo_stack.clear()
        window.current_frame = prepared.frame
        window.current_frame_index = prepared.frame_index
        window.current_time = prepared.timestamp_sec
        window.last_result_path = ""
        window.canvas.set_frame(window.current_frame)
        window.transport.set_position(
            window.current_time,
            window.workbench.session.video_metadata.duration_sec,
            window.current_frame_index,
        )
        window._last_validation = None
        window._invalidate_preview("현재 장면 분석 대기")
        preflight = getattr(window, "preflight_coordinator", None)
        if preflight is not None:
            preflight.reset()
        window._refresh_all()
        window._refresh_inline_validation()
        window.schedule_preview()
        window.statusBar().showMessage(
            "분석 당시 프로필을 복사해 새 영상을 준비했습니다. 설정 점검 후 분석을 실행해 주세요.",
            12000,
        )
        window.show()
        window.raise_()
        window.activateWindow()

    def cancel(self) -> None:
        prepared, self._prepared = self._prepared, None
        if prepared is not None:
            prepared.close()

    def close(self) -> None:
        self.cancel()
