from __future__ import annotations

from copy import deepcopy
import logging
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox

from oil_tracker.application.services.redetection_apply import (
    DetectorSettingsApplyScope,
    apply_detector_settings,
    check_workbench_compatibility,
    create_profile_from_snapshot,
    ensure_profile_destination_outside_bundle,
)
from oil_tracker.application.services.redetection_request import (
    RedetectionRequestError,
    build_redetection_request,
)
from oil_tracker.domain.redetection import RedetectionMode, RedetectionStatus
from oil_tracker.ui.redetection_comparison_window import RedetectionComparisonWindow


LOGGER = logging.getLogger(__name__)


class RedetectionComparisonCoordinator(QObject):
    """Keep one modeless comparison window per Result Review Viewer."""

    def __init__(self, main_window, viewer, controller, parent=None) -> None:
        super().__init__(parent or viewer)
        self.main_window = main_window
        self.viewer = viewer
        self.controller = controller
        self.window: RedetectionComparisonWindow | None = None
        self.generation = 0
        self.target_timestamp = 0.0
        self.current_result = None
        self.current_official_record = None
        self.current_rerun_record = None
        self._closing = False

        viewer.redetectionRequested.connect(self.open)
        viewer.bundleAboutToChange.connect(self._bundle_about_to_change)
        viewer.bundleChanged.connect(self._bundle_changed)
        viewer.sourceVideoChanged.connect(self._source_changed)
        viewer.selectedGlassChanged.connect(self._glass_changed)
        viewer.viewerClosing.connect(self.close)
        controller.started.connect(self._started)
        controller.progress.connect(self._progress)
        controller.completed.connect(self._completed)
        controller.failed.connect(self._failed)
        controller.cancelled.connect(self._cancelled)

    def open(self) -> None:
        if self.viewer.bundle is None:
            QMessageBox.information(
                self.viewer,
                "부분 재검출",
                "먼저 결과 bundle을 열어 주세요.",
            )
            return
        glass = self.viewer.bundle.glass_config(self.viewer.selected_glass_id)
        if glass is None:
            QMessageBox.warning(
                self.viewer,
                "부분 재검출",
                "선택한 관찰창이 결과 snapshot에 없습니다.",
            )
            return
        if self.window is None:
            self.window = RedetectionComparisonWindow(
                glass.detector_settings,
                self.viewer,
            )
            self.window.runRequested.connect(self.run)
            self.window.cancelRequested.connect(self.controller.cancel)
            self.window.currentTimestampRequested.connect(self.use_current_timestamp)
            self.window.contextEdited.connect(self._context_edited)
            self.window.comparisonSelected.connect(self._comparison_selected)
            self.window.applyCurrentRequested.connect(
                lambda: self._apply_to_workbench(DetectorSettingsApplyScope.SELECTED)
            )
            self.window.applyAllRequested.connect(
                lambda: self._apply_to_workbench(DetectorSettingsApplyScope.ALL)
            )
            self.window.saveSelectedRequested.connect(
                lambda: self._save_profile(DetectorSettingsApplyScope.SELECTED)
            )
            self.window.saveAllRequested.connect(
                lambda: self._save_profile(DetectorSettingsApplyScope.ALL)
            )
            for panel in (
                self.window.candidate_compare,
                self.window.artifact_compare,
            ):
                panel.officialArtifactRequested.connect(self._load_official_artifact)
                panel.rerunArtifactRequested.connect(self._load_rerun_artifact)
        self.target_timestamp = float(self.viewer.current_time)
        self._refresh_context(reset_baseline=True)
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def run(self) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        glass = self.viewer.bundle.glass_config(self.viewer.selected_glass_id)
        if glass is None:
            return
        mode = self.window.current_mode()
        if mode is RedetectionMode.FULL:
            answer = QMessageBox.question(
                self.window,
                "전체 구간 재검출 확인",
                "선택 관찰창의 전체 분석 구간을 순차 처리합니다.\n"
                "공식 결과는 변경하지 않으며 진행 중 취소할 수 있습니다.\n\n"
                "계속하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self.generation += 1
        self.controller.generation = self.generation
        try:
            request = build_redetection_request(
                self.viewer.bundle,
                self.viewer.active_video_path,
                self.viewer.selected_glass_id,
                self.target_timestamp,
                mode,
                self.window.temporary_settings(),
                self.generation,
                before_sec=self.window.short_before_sec(),
                after_sec=self.window.short_after_sec(),
                policy=self.controller.service.policy,
            )
        except (RedetectionRequestError, ValueError) as exc:
            QMessageBox.warning(self.window, "재검출 실행 불가", str(exc))
            return
        self.current_result = None
        self.window.clear_result("재검출 실행 중입니다.")
        official_times = ()
        if self.viewer.debug_repository is not None:
            official_times = tuple(
                summary.timestamp_sec
                for summary in self.viewer.debug_repository.summaries(
                    self.viewer.selected_glass_id
                )
            )
        self.controller.start(
            request,
            self.viewer.bundle,
            official_candidate_timestamps=official_times,
        )

    def use_current_timestamp(self) -> None:
        self.target_timestamp = float(self.viewer.current_time)
        if self.window is not None:
            self.window.set_target(self.target_timestamp)
        self._mark_stale("현재 Viewer decoded 시각을 새 target으로 선택했습니다. 다시 실행해 주세요.")

    def _bundle_about_to_change(self) -> None:
        self.generation += 1
        self.controller.invalidate(self.generation)
        self.current_result = None
        if self.window is not None:
            self.window.clear_result("결과 bundle이 변경되어 이전 재검출 context를 정리했습니다.")
            self.window.set_status(
                RedetectionStatus.CONTEXT_STALE,
                "context 변경됨 — 다시 실행 필요",
            )

    def _bundle_changed(self, _bundle) -> None:
        if self.window is not None:
            self.target_timestamp = float(self.viewer.current_time)
            self._refresh_context(reset_baseline=True)

    def _source_changed(self, _path) -> None:
        if self.window is not None:
            self._refresh_context(reset_baseline=False)
            self._mark_stale("원본 영상 경로가 변경되었습니다. 다시 실행해 주세요.")

    def _glass_changed(self, _glass_id: str) -> None:
        if self.window is not None:
            self.generation += 1
            self.controller.invalidate(self.generation)
            self.target_timestamp = float(self.viewer.current_time)
            self._refresh_context(reset_baseline=True)
            self._mark_stale("선택 관찰창이 변경되었습니다. 다시 실행해 주세요.")

    def _context_edited(self, kind: str) -> None:
        if self.window is None or self.current_result is None:
            return
        status = (
            RedetectionStatus.SETTINGS_STALE
            if kind == "settings"
            else RedetectionStatus.CONTEXT_STALE
        )
        message = (
            "설정 변경됨 — 다시 실행 필요"
            if kind == "settings"
            else "context 변경됨 — 다시 실행 필요"
        )
        self.window.set_status(status, message)

    def _mark_stale(self, message: str) -> None:
        if self.window is None:
            return
        self.window.set_status(RedetectionStatus.CONTEXT_STALE, message)

    def _refresh_context(self, *, reset_baseline: bool) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        glass = self.viewer.bundle.glass_config(self.viewer.selected_glass_id)
        if glass is None:
            return
        if reset_baseline:
            self.window.set_baseline_settings(glass.detector_settings)
        self.window.set_context(
            self.viewer.bundle,
            glass,
            str(self.viewer.active_video_path or ""),
            self.target_timestamp,
        )
        self._refresh_compatibility()

    def _refresh_compatibility(self) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        compatibility = check_workbench_compatibility(
            self.main_window.workbench.recipe,
            self.main_window.workbench.state,
            self.viewer.bundle.recipe,
            self.viewer.selected_glass_id,
            DetectorSettingsApplyScope.SELECTED,
        )
        self.window.set_apply_compatibility(
            compatibility.compatible,
            compatibility.reasons,
        )

    def _started(self, generation: int, mode: str) -> None:
        if self.window is not None and generation == self.generation:
            self.window.set_status(
                RedetectionStatus.RUNNING,
                f"재검출 실행 중 · {mode}",
            )

    def _progress(self, update) -> None:
        if self.window is not None and update.generation == self.generation:
            self.window.set_progress(update)

    def _completed(self, result) -> None:
        if self.window is None or result.request.generation != self.generation:
            return
        self.current_result = result
        glass = self.viewer.bundle.glass_config(result.request.selected_glass_id)
        if glass is None:
            self._failed(self.generation, "결과 snapshot의 관찰창을 찾을 수 없습니다.")
            return
        self.window.set_result(result, glass)
        self.window.set_status(
            RedetectionStatus.COMPLETED,
            f"재검출 완료 · 비교 sample {result.summary.comparison_sample_count}개",
        )
        self._refresh_compatibility()
        self._comparison_selected(0, result.request.target_timestamp_sec)

    def _failed(self, generation: int, message: str) -> None:
        if self.window is None or generation != self.generation:
            return
        self.current_result = None
        self.window.set_status(RedetectionStatus.FAILED, f"재검출 실패 · {message}")
        QMessageBox.critical(self.window, "재검출 실패", message)

    def _cancelled(self, generation: int) -> None:
        if self.window is None or generation != self.generation:
            return
        self.current_result = None
        self.window.set_status(RedetectionStatus.CANCELLED, "재검출이 취소되었습니다.")

    def _comparison_selected(self, index: int, timestamp: float) -> None:
        if self.current_result is None or self.window is None:
            return
        if index < 0 or index >= len(self.current_result.comparisons):
            return
        self.viewer._jump_to(timestamp)
        point = self.current_result.comparisons[index]
        official_record = None
        rerun_record = None
        official_message = ""
        if self.viewer.debug_repository is not None and point.official_timestamp_sec is not None:
            tolerance = self.controller.service.policy.alignment_tolerance(
                self.viewer.bundle.session.sampling_fps
            )
            summary = self.viewer.debug_repository.nearest(
                self.current_result.request.selected_glass_id,
                point.official_timestamp_sec,
                tolerance,
            )
            if summary is not None:
                try:
                    official_record = self.viewer.debug_repository.load_record(
                        summary.record_id
                    )
                except Exception as exc:
                    official_message = str(exc)
        else:
            official_message = (
                "공식 분석 당시 후보 상세가 저장되지 않아 candidate 단위 비교는 "
                "제공할 수 없습니다."
            )
        rerun_sample = point.rerun_sample
        repository = (
            self.controller.current_workspace.repository
            if self.controller.current_workspace is not None
            else None
        )
        if (
            repository is not None
            and rerun_sample is not None
            and rerun_sample.debug_record_id
        ):
            try:
                rerun_record = repository.load_record(rerun_sample.debug_record_id)
            except Exception as exc:
                LOGGER.exception("Rerun debug record load failed")
                self.window.set_apply_status(f"재검출 debug record 읽기 실패: {exc}")
        self.current_official_record = official_record
        self.current_rerun_record = rerun_record
        self.window.set_debug_records(
            official_record,
            rerun_record,
            official_message,
        )

    def _load_official_artifact(self, key: str) -> None:
        if self.window is None or not key:
            return
        image = None
        error = ""
        if self.viewer.debug_repository is not None and self.current_official_record is not None:
            try:
                image = self.viewer.debug_repository.load_image(
                    self.current_official_record,
                    key,
                )
            except Exception as exc:
                error = str(exc)
        for panel in (self.window.candidate_compare, self.window.artifact_compare):
            panel.set_official_artifact(key, image, error)

    def _load_rerun_artifact(self, key: str) -> None:
        if self.window is None or not key:
            return
        image = None
        error = ""
        repository = (
            self.controller.current_workspace.repository
            if self.controller.current_workspace is not None
            else None
        )
        if repository is not None and self.current_rerun_record is not None:
            try:
                image = repository.load_image(self.current_rerun_record, key)
            except Exception as exc:
                error = str(exc)
        for panel in (self.window.candidate_compare, self.window.artifact_compare):
            panel.set_rerun_artifact(key, image, error)

    def _apply_to_workbench(self, scope: DetectorSettingsApplyScope) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        compatibility = check_workbench_compatibility(
            self.main_window.workbench.recipe,
            self.main_window.workbench.state,
            self.viewer.bundle.recipe,
            self.viewer.selected_glass_id,
            scope,
        )
        if not compatibility.compatible:
            QMessageBox.warning(
                self.window,
                "Workbench 적용 불가",
                "\n".join(compatibility.reasons),
            )
            self.window.set_apply_compatibility(False, compatibility.reasons)
            return
        settings = self.window.temporary_settings()
        planned_recipe = deepcopy(self.main_window.workbench.recipe)
        planned = apply_detector_settings(
            planned_recipe,
            self.viewer.selected_glass_id,
            settings,
            scope,
        )
        if planned.is_no_op:
            QMessageBox.information(
                self.window,
                "검출 설정 적용",
                "현재 Workbench에 적용할 변경 사항이 없습니다.",
            )
            return
        target_text = "동일 관찰창" if scope is DetectorSettingsApplyScope.SELECTED else "모든 관찰창"
        answer = QMessageBox.question(
            self.window,
            "검출 설정 적용 확인",
            f"임시 detector 설정을 현재 Workbench의 {target_text}에 적용합니다.\n"
            "한 번의 Undo/Redo 항목으로 기록되며 자동 저장하지 않습니다.\n\n"
            "계속하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        selected_before = self.main_window.workbench.selected_glass_id

        def change() -> None:
            apply_detector_settings(
                self.main_window.workbench.recipe,
                self.viewer.selected_glass_id,
                settings,
                scope,
            )
            self.main_window.workbench.selected_glass_id = selected_before
            self.main_window.workbench.mark_dirty()

        self.main_window._record_recipe_change(
            "재검출 detector 설정 적용",
            change,
        )
        preflight = getattr(self.main_window, "preflight_coordinator", None)
        if preflight is not None:
            preflight.reset()
        self.main_window._last_validation = None
        self.main_window._invalidate_preview("검출 설정 변경 · 현재 장면 재분석 필요")
        self.main_window._refresh_all()
        self.main_window._refresh_inline_validation()
        self.window.set_apply_status(
            f"Workbench 적용 완료 · {len(planned.changed_glass_ids)}개 관찰창 · 자동 저장하지 않음"
        )
        self._refresh_compatibility()

    def _save_profile(self, scope: DetectorSettingsApplyScope) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        default = self.viewer.bundle.root.parent / (
            f"{self.viewer.bundle.recipe.name}_재검출_설정.oilrecipe"
        )
        selected, _ = QFileDialog.getSaveFileName(
            self.window,
            "재검출 설정을 적용한 새 profile 저장",
            str(default),
            "유면 분석 프로필 (*.oilrecipe)",
        )
        if not selected:
            return
        try:
            destination = ensure_profile_destination_outside_bundle(
                self.viewer.bundle.root,
                selected,
            )
        except ValueError as exc:
            QMessageBox.warning(self.window, "새 profile 저장 불가", str(exc))
            return
        if destination.exists():
            answer = QMessageBox.question(
                self.window,
                "기존 profile 덮어쓰기 확인",
                f"이미 존재하는 파일입니다.\n{destination}\n\n덮어쓰시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            recipe = create_profile_from_snapshot(
                self.viewer.bundle.recipe,
                self.viewer.selected_glass_id,
                self.window.temporary_settings(),
                scope,
            )
            self.main_window.workbench.save_use_case.execute(destination, recipe)
        except Exception as exc:
            LOGGER.exception("Redetection profile save failed")
            QMessageBox.critical(
                self.window,
                "새 profile 저장 실패",
                f"새 profile을 저장하지 못했습니다.\n{exc}",
            )
            return
        self.window.set_apply_status(f"새 profile 저장 완료 · {destination}")
        QMessageBox.information(
            self.window,
            "새 profile 저장 완료",
            f"현재 Workbench는 변경하지 않았습니다.\n{destination}",
        )

    def close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.generation += 1
        self.controller.invalidate(self.generation)
        self.controller.close()
        if self.window is not None:
            self.window.close()
            self.window = None
        self.current_result = None
        self.current_official_record = None
        self.current_rerun_record = None
