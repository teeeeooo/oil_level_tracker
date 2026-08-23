from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QFileDialog, QMessageBox

from oil_tracker.application.ports.review_io import (
    TruthFixtureExporterPort,
    TruthIdentityMismatchError,
    TruthRepositoryError,
    TruthRepositoryPort,
)
from oil_tracker.application.services.user_truth import (
    TruthFrameContext,
    TruthSession,
    UserTruthService,
)
from oil_tracker.application.services.truth_identity import build_truth_bundle_identity
from oil_tracker.domain.user_truth import (
    TruthDisposition,
    TruthValidationError,
    compare_truth,
)
from oil_tracker.ui.controllers.truth_export_controller import TruthExportController
from oil_tracker.ui.truth_annotation_window import TruthAnnotationWindow


LOGGER = logging.getLogger(__name__)
_IMAGE_BOUNDARY_MESSAGE = "현재 Viewer 장면을 이미지로 불러올 수 없습니다. 원본 영상 장면을 다시 선택해 주세요."


class TruthAnnotationCoordinator(QObject):
    """Own one modeless truth editor and keep official results immutable."""

    def __init__(
        self,
        viewer,
        *,
        repository: TruthRepositoryPort | None = None,
        service: UserTruthService | None = None,
        exporter: TruthFixtureExporterPort | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent or viewer)
        self.viewer = viewer
        self.repository = repository
        self.service = service or UserTruthService()
        self.export_controller = TruthExportController(exporter, self)
        self.window: TruthAnnotationWindow | None = None
        self.session = TruthSession()
        self.identity = None
        self.draft_dirty = False
        self._draft_image = QImage()
        self._closing = False

        viewer.truthRequested.connect(self.open)
        viewer.bundleChanged.connect(self._bundle_changed)
        viewer.sourceVideoChanged.connect(self._source_changed)
        viewer.selectedGlassChanged.connect(self._glass_changed)
        viewer.viewerClosing.connect(self._viewer_closed)
        viewer.add_bundle_change_guard(self._guard_bundle_change)
        viewer.add_glass_change_guard(self._guard_glass_change)
        viewer.add_close_guard(self._guard_close)

        self.export_controller.started.connect(self._export_started)
        self.export_controller.progress.connect(self._export_progress)
        self.export_controller.completed.connect(self._export_completed)
        self.export_controller.failed.connect(self._export_failed)
        self.export_controller.cancelled.connect(self._export_cancelled)

    def open(self) -> None:
        if self.viewer.bundle is None:
            QMessageBox.information(self.viewer, "사용자 정답", "먼저 결과 bundle을 열어 주세요.")
            return
        self._ensure_window()
        self._ensure_set()
        self._refresh_source_state()
        self._refresh_annotations()
        if self.window.context() is None and self._viewer_source_available():
            self.capture_current_frame()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _ensure_window(self) -> None:
        if self.window is not None:
            return
        self.window = TruthAnnotationWindow(self.viewer)
        self.window.loadCurrentRequested.connect(self.capture_current_frame)
        self.window.confirmOfficialRequested.connect(self.confirm_official)
        self.window.saveAnnotationRequested.connect(self.save_annotation)
        self.window.deleteAnnotationRequested.connect(self.delete_annotations)
        self.window.newTruthSetRequested.connect(self.new_truth_set)
        self.window.openTruthSetRequested.connect(self.open_truth_set)
        self.window.saveTruthSetRequested.connect(self.save_truth_set)
        self.window.saveTruthSetAsRequested.connect(lambda: self.save_truth_set(save_as=True))
        self.window.exportCurrentRequested.connect(self.export_current)
        self.window.exportSelectedRequested.connect(self.export_selected)
        self.window.exportAllRequested.connect(self.export_all)
        self.window.cancelExportRequested.connect(self.export_controller.cancel)
        self.window.annotationActivated.connect(self.activate_annotation)
        self.window.draftChanged.connect(self._draft_changed)
        self.window.disposition_filter.currentIndexChanged.connect(self._refresh_annotations)
        self.window.error_filter.currentIndexChanged.connect(self._refresh_annotations)

    def _ensure_set(self) -> None:
        if self.viewer.bundle is None:
            return
        self.identity = build_truth_bundle_identity(self.viewer.bundle)
        if self.session.truth_set is None:
            self.session.attach_new(self.service.create_set(self.identity))
        self._refresh_session_state()

    def capture_current_frame(self) -> None:
        if self.window is None or self.viewer.bundle is None:
            return
        if not self._viewer_source_available() or self.viewer.active_video_path is None:
            self._release_draft_image()
            self.window.clear_context("원본 영상이 없습니다. Viewer에서 원본 영상 다시 지정을 사용해 주세요.")
            self.window.set_source_available(False, "원본 영상 다시 지정 후 새 annotation을 작성할 수 있습니다.")
            return
        if not self._guard_draft_change("Viewer 장면을 다시 불러오기"):
            return
        glass = self.viewer.bundle.glass_config(self.viewer.selected_glass_id)
        if glass is None:
            QMessageBox.warning(self.window, "사용자 정답", "선택 관찰창이 result snapshot에 없습니다.")
            return
        image_error = self._set_draft_image(self.viewer.current_source_image)
        if image_error:
            self.window.clear_context("현재 Viewer 장면을 표시할 수 없습니다.")
            self.window.set_validation_error(image_error)
            return
        self._ensure_set()
        existing = self.session.truth_set.find(
            glass.id,
            int(self.viewer.current_frame_index),
            float(self.viewer.current_time),
        )
        context = TruthFrameContext(
            glass_id=glass.id,
            glass_name=glass.name,
            requested_timestamp_sec=float(self.viewer.current_time),
            actual_decoded_timestamp_sec=float(self.viewer.current_time),
            frame_index=int(self.viewer.current_frame_index),
        )
        official = self.service.official_reference(
            self.viewer.bundle,
            glass,
            context.actual_decoded_timestamp_sec,
            debug_repository=self.viewer.debug_repository,
        )
        self.window.set_context(
            self._draft_image,
            glass,
            context,
            official,
            existing,
        )
        self.draft_dirty = False
        if existing is not None:
            self._show_comparison(existing)
        else:
            self.window.set_comparison_text("저장 전 draft · 공식 결과와 비교하려면 정답을 저장해 주세요.")

    def confirm_official(self) -> None:
        if self.window is None:
            return
        self.window.apply_official_reference()
        self.draft_dirty = True

    def save_annotation(self, *, quiet: bool = False) -> bool:
        if self.window is None or self.viewer.bundle is None or self.window.context() is None:
            if not quiet:
                QMessageBox.information(self.viewer, "사용자 정답 저장", "먼저 현재 Viewer 장면을 불러와 주세요.")
            return False
        self._ensure_set()
        context = self.window.context()
        glass = self.viewer.bundle.glass_config(context.glass_id)
        if glass is None:
            self.window.set_validation_error("result snapshot에서 관찰창을 찾을 수 없습니다.")
            return False
        values = self.window.draft_values()
        try:
            annotation = self.service.make_annotation(
                self.session.truth_set,
                self.identity,
                glass,
                context,
                values.disposition,
                truth_fill_state=values.fill_state,
                oil_source_y=values.oil_source_y,
                foam_present=values.foam_present,
                foam_source_y=values.foam_source_y,
                error_types=values.error_types,
                note=values.note,
                official_reference=self.window.official_reference(),
                existing_annotation=self.window.existing_annotation(),
            )
            saved = self.session.truth_set.upsert(annotation)
        except (TruthValidationError, ValueError) as exc:
            self.window.set_validation_error(str(exc))
            if not quiet:
                QMessageBox.warning(self.window, "사용자 정답 입력 확인", str(exc))
            return False
        self.session.mark_dirty()
        self.draft_dirty = False
        self.window.set_context(
            None if self._draft_image.isNull() else self._draft_image,
            glass,
            context,
            saved.official_tracking_reference,
            saved,
        )
        self._show_comparison(saved)
        self._refresh_annotations(select_id=saved.annotation_id)
        self._refresh_markers(saved.annotation_id)
        self._refresh_session_state()
        self.window.set_validation_error("현재 정답을 annotation set에 반영했습니다. 파일 저장은 별도 action입니다.")
        return True

    def delete_annotations(self) -> None:
        if self.window is None or self.session.truth_set is None:
            return
        ids = self.window.selected_annotation_ids()
        if not ids and self.window.existing_annotation() is not None:
            ids = (self.window.existing_annotation().annotation_id,)
        if not ids:
            QMessageBox.information(self.window, "사용자 정답 삭제", "삭제할 annotation을 선택해 주세요.")
            return
        answer = QMessageBox.question(
            self.window,
            "사용자 정답 삭제 확인",
            f"선택한 사용자 정답 {len(ids)}개를 active truth set에서 제거합니다.\n"
            "공식 result bundle은 변경하지 않습니다.\n\n계속하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        changed = any(self.session.truth_set.remove(annotation_id) for annotation_id in ids)
        if changed:
            self.session.mark_dirty()
            self.draft_dirty = False
            self._release_draft_image()
            self.window.clear_context("annotation을 삭제했습니다. 현재 Viewer 장면을 다시 불러와 주세요.")
            self._refresh_annotations()
            self._refresh_markers()
            self._refresh_session_state()

    def new_truth_set(self) -> None:
        if self.viewer.bundle is None or not self._guard_truth_set_change("새 정답 세트"):
            return
        self.identity = build_truth_bundle_identity(self.viewer.bundle)
        self.session.attach_new(self.service.create_set(self.identity))
        self.draft_dirty = False
        self._release_draft_image()
        if self.window is not None:
            self.window.clear_context()
        self._refresh_annotations()
        self._refresh_markers()
        self._refresh_session_state()

    def open_truth_set(self) -> None:
        if self.viewer.bundle is None or self.window is None:
            return
        if not self._guard_truth_set_change("다른 사용자 정답 파일 열기"):
            return
        default = self.viewer.bundle.root.parent
        selected, _ = QFileDialog.getOpenFileName(
            self.window,
            "사용자 정답 파일 열기",
            str(default),
            "유면 사용자 정답 (*.oiltruth)",
        )
        if not selected:
            return
        if self.repository is None:
            QMessageBox.critical(self.window, "사용자 정답 열기 실패", "사용자 정답 저장소가 구성되지 않았습니다.")
            return
        expected = build_truth_bundle_identity(self.viewer.bundle)
        try:
            result = self.repository.load(
                selected,
                expected_identity=expected,
                bundle=self.viewer.bundle,
            )
        except TruthIdentityMismatchError as exc:
            LOGGER.warning("Truth identity mismatch: %s", exc)
            QMessageBox.warning(self.window, "사용자 정답 bundle 불일치", str(exc))
            return
        except TruthRepositoryError as exc:
            LOGGER.exception("Truth file load failed")
            QMessageBox.critical(self.window, "사용자 정답 열기 실패", str(exc))
            return
        self.identity = expected
        self.session.attach_loaded(result.truth_set, result.path)
        self.draft_dirty = False
        self._release_draft_image()
        self.window.clear_context("사용자 정답 파일을 열었습니다. 목록을 선택하거나 현재 장면을 불러와 주세요.")
        self._refresh_annotations()
        self._refresh_markers()
        self._refresh_session_state()
        if result.warnings:
            QMessageBox.warning(self.window, "사용자 정답 metadata 경고", "\n".join(result.warnings))

    def save_truth_set(self, *, save_as: bool = False) -> bool:
        if self.viewer.bundle is None or self.session.truth_set is None:
            return False
        if self.repository is None:
            QMessageBox.critical(self.window or self.viewer, "사용자 정답 저장 실패", "사용자 정답 저장소가 구성되지 않았습니다.")
            return False
        self._ensure_window()
        destination = None if save_as else self.session.path
        if destination is None:
            default = self.viewer.bundle.root.parent / f"{self.viewer.bundle.root.name}_사용자정답.oiltruth"
            selected, _ = QFileDialog.getSaveFileName(
                self.window,
                "사용자 정답 세트 저장",
                str(default),
                "유면 사용자 정답 (*.oiltruth)",
            )
            if not selected:
                return False
            destination = Path(selected)
        self.session.mark_saving()
        self._refresh_session_state()
        try:
            path = self.repository.save(
                destination,
                self.session.truth_set,
                bundle_root=self.viewer.bundle.root,
                bundle=self.viewer.bundle,
                confirm_overwrite=self._confirm_overwrite,
            )
        except TruthRepositoryError as exc:
            self.session.mark_failed()
            self._refresh_session_state()
            QMessageBox.critical(self.window, "사용자 정답 저장 실패", str(exc))
            return False
        self.session.mark_saved(path)
        self._refresh_session_state()
        self.window.set_validation_error(f"사용자 정답 세트 저장 완료 · {path}")
        return True

    def activate_annotation(self, annotation) -> None:
        if self.viewer.bundle is None or self.window is None:
            return
        if not self._guard_draft_change("다른 annotation 선택"):
            return
        self.viewer.playback.pause()
        if annotation.glass_id != self.viewer.selected_glass_id:
            if not self.viewer.select_glass(annotation.glass_id):
                return
        self.viewer._jump_to(annotation.actual_decoded_timestamp_sec)
        glass = self.viewer.bundle.glass_config(annotation.glass_id)
        if glass is None:
            return
        context = TruthFrameContext(
            annotation.glass_id,
            annotation.glass_name_snapshot,
            annotation.requested_timestamp_sec,
            annotation.actual_decoded_timestamp_sec,
            annotation.frame_index,
        )
        image_error = ""
        if not self._viewer_source_available():
            self._release_draft_image()
        else:
            image_error = self._set_draft_image(self.viewer.current_source_image)
        self.window.set_context(
            None if self._draft_image.isNull() else self._draft_image,
            glass,
            context,
            annotation.official_tracking_reference,
            annotation,
        )
        self.window.set_decode_delta(annotation.actual_decoded_timestamp_sec, self.viewer.current_time)
        if image_error:
            self.window.set_validation_error(image_error)
        elif not self._viewer_source_available():
            self.window.set_validation_error("annotation 장면을 원본 영상에서 불러오지 못했습니다.")
        elif self.viewer.current_frame_index != annotation.frame_index:
            self.window.set_validation_error(
                f"현재 decode frame {self.viewer.current_frame_index}가 annotation frame {annotation.frame_index}와 다릅니다. "
                "원본 영상 identity를 확인해 주세요."
            )
        self._show_comparison(annotation)
        self.draft_dirty = False
        self._refresh_markers(annotation.annotation_id)

    def export_current(self) -> None:
        annotation = self.window.existing_annotation() if self.window is not None else None
        if annotation is None:
            QMessageBox.information(self.window or self.viewer, "fixture export", "먼저 저장된 현재 annotation을 선택해 주세요.")
            return
        self._start_export((annotation,))

    def export_selected(self) -> None:
        if self.window is None or self.session.truth_set is None:
            return
        ids = set(self.window.selected_annotation_ids())
        selected = tuple(value for value in self.session.truth_set.sorted_annotations() if value.annotation_id in ids)
        if not selected:
            QMessageBox.information(self.window, "fixture export", "내보낼 annotation을 목록에서 선택해 주세요.")
            return
        self._start_export(selected)

    def export_all(self) -> None:
        if self.session.truth_set is not None:
            self._start_export(self.session.truth_set.sorted_annotations())

    def _start_export(self, annotations) -> None:
        if self.viewer.bundle is None or self.session.truth_set is None or self.window is None:
            return
        if not self.viewer.active_video_path:
            QMessageBox.warning(self.window, "fixture export 불가", "원본 영상 다시 지정 후 export해 주세요.")
            return
        selected = QFileDialog.getExistingDirectory(
            self.window,
            "regression fixture dataset을 만들 상위 폴더 선택",
            str(self.viewer.bundle.root.parent),
        )
        if not selected:
            return
        self.export_controller.start(
            bundle=self.viewer.bundle,
            truth_set=self.session.truth_set,
            annotations=tuple(annotations),
            destination=Path(selected),
            source_video_path=self.viewer.active_video_path,
            active_truth_path=self.session.path,
            debug_repository=self.viewer.debug_repository,
        )

    def _bundle_changed(self, bundle) -> None:
        self.identity = build_truth_bundle_identity(bundle) if bundle is not None else None
        self.session.clear()
        self.draft_dirty = False
        self._release_draft_image()
        if self.window is not None:
            self.window.clear_context("새 result bundle을 열었습니다. 새 정답 세트를 만들거나 .oiltruth를 열어 주세요.")
            self._refresh_source_state()
            self._refresh_annotations()
            self._refresh_session_state()
        self._refresh_markers()

    def _source_changed(self, _path) -> None:
        self._refresh_source_state()
        if self.window is not None and self.viewer.active_video_path is None:
            self.window.set_validation_error("원본 영상 없음 · 기존 정답 metadata는 유지되지만 새 annotation과 fixture export는 비활성화됩니다.")

    def _glass_changed(self, _glass_id: str) -> None:
        if self.window is not None:
            self._release_draft_image()
            self.window.clear_context("관찰창이 변경되었습니다. 현재 Viewer 장면을 명시적으로 불러와 주세요.")
            self.draft_dirty = False
            self._refresh_annotations()
            self._refresh_markers()

    def _draft_changed(self) -> None:
        if self.window is not None and self.window.context() is not None:
            self.draft_dirty = True

    def _guard_bundle_change(self) -> bool:
        self.export_controller.invalidate()
        return self._guard_draft_change("result bundle 변경") and self._guard_truth_set_change("result bundle 변경")

    def _guard_glass_change(self) -> bool:
        return self._guard_draft_change("관찰창 변경")

    def _guard_close(self) -> bool:
        self.export_controller.invalidate()
        return self._guard_draft_change("Viewer 닫기") and self._guard_truth_set_change("Viewer 닫기")

    def _guard_draft_change(self, title: str) -> bool:
        if not self.draft_dirty or self.window is None:
            return True
        answer = QMessageBox.question(
            self.window,
            title,
            "편집 중인 현재 장면 정답이 annotation set에 반영되지 않았습니다.\n\n"
            "저장: 현재 정답을 annotation set에 반영\n"
            "폐기: 현재 draft 변경 폐기\n"
            "취소: 작업 중단",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save_annotation(quiet=True)
        if answer == QMessageBox.StandardButton.Discard:
            self.draft_dirty = False
            return True
        return False

    def _guard_truth_set_change(self, title: str) -> bool:
        if not self.session.dirty or self.window is None:
            return True
        answer = QMessageBox.question(
            self.window,
            title,
            "사용자 정답 세트에 저장되지 않은 변경이 있습니다.\n\n"
            "저장: .oiltruth 파일 저장\n"
            "폐기: disk file을 변경하지 않고 변경 폐기\n"
            "취소: 작업 중단",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save_truth_set()
        if answer == QMessageBox.StandardButton.Discard:
            self.session.dirty = False
            return True
        return False

    def _set_draft_image(self, image) -> str:
        if not isinstance(image, QImage) or image.isNull():
            self._release_draft_image()
            return _IMAGE_BOUNDARY_MESSAGE
        self._draft_image = QImage(image).copy()
        return ""

    def _viewer_source_available(self) -> bool:
        image = getattr(self.viewer, "current_source_image", None)
        return isinstance(image, QImage) and not image.isNull()

    def _release_draft_image(self) -> None:
        self._draft_image = QImage()

    def _refresh_annotations(self, *_args, select_id: str = "") -> None:
        if self.window is None:
            return
        annotations = self.session.truth_set.sorted_annotations() if self.session.truth_set is not None else ()
        self.window.set_annotations(annotations)
        if select_id:
            for index in range(self.window.annotation_list.count()):
                item = self.window.annotation_list.item(index)
                if str(item.data(0x0100) or "") == select_id:
                    self.window.annotation_list.setCurrentItem(item)
                    break

    def _refresh_session_state(self) -> None:
        if self.window is None:
            return
        if self.session.truth_set is None:
            text = "정답 세트 없음"
        elif self.session.path is None:
            text = f"새 정답 세트 · {self.session.truth_set.annotation_set_id}"
        else:
            text = f"{Path(self.session.path).name} · {self.session.truth_set.annotation_set_id}"
        self.window.set_session_state(text, dirty=self.session.dirty)

    def _refresh_source_state(self) -> None:
        if self.window is None:
            return
        available = self.viewer.active_video_path is not None and self._viewer_source_available()
        message = "" if available else "원본 영상 다시 지정 후 새 annotation과 fixture export를 사용할 수 있습니다."
        self.window.set_source_available(available, message)

    def _refresh_markers(self, selected_id: str = "") -> None:
        annotations = self.session.truth_set.sorted_annotations() if self.session.truth_set is not None else ()
        self.viewer.set_truth_annotations(annotations, selected_id=selected_id)

    def _show_comparison(self, annotation) -> None:
        if self.window is None:
            return
        comparison = compare_truth(annotation)
        state = (
            "비교 없음"
            if comparison.state_matches is None
            else "일치"
            if comparison.state_matches
            else "불일치"
        )
        self.window.set_comparison_text(
            f"공식 sample: {'있음' if comparison.official_sample_exists else '없음'} · "
            f"state: {state}\n"
            f"oil Δ: {_number(comparison.oil_delta_px, 'px')} / {_number(comparison.oil_delta_mm, 'mm')} · "
            f"foam Δ: {_number(comparison.foam_delta_px, 'px')} / {_number(comparison.foam_delta_mm, 'mm')}\n"
            f"official valid: {comparison.official_valid if comparison.official_valid is not None else '-'} · "
            f"candidate baseline: {'있음' if comparison.official_candidate_baseline_available else '없음'}"
        )

    def _confirm_overwrite(self, path: Path) -> bool:
        answer = QMessageBox.question(
            self.window,
            "기존 사용자 정답 덮어쓰기 확인",
            f"이미 존재하는 파일입니다.\n{path}\n\n덮어쓰시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _export_started(self, _generation: int, _total: int) -> None:
        if self.window is not None:
            self.window.set_export_running(True)

    def _export_progress(self, update) -> None:
        if self.window is not None:
            self.window.set_export_progress(update)

    def _export_completed(self, result) -> None:
        if self.window is not None:
            self.window.set_export_running(False)
            self.window.export_progress.setValue(1000)
            QMessageBox.information(
                self.window,
                "regression fixture export 완료",
                f"fixture {result.fixture_count}개 · decoded frame {result.decoded_frame_count}개\n{result.dataset_path}",
            )

    def _export_failed(self, _generation: int, message: str) -> None:
        if self.window is not None:
            self.window.set_export_running(False)
            LOGGER.error("Truth fixture export failed: %s", message)
            QMessageBox.critical(self.window, "regression fixture export 실패", message)

    def _export_cancelled(self, _generation: int) -> None:
        if self.window is not None:
            self.window.set_export_running(False)
            self.window.set_validation_error("regression fixture export가 취소되었습니다. partial dataset은 남지 않았습니다.")

    def _viewer_closed(self) -> None:
        self.close()

    def close(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.export_controller.close()
        self._release_draft_image()
        if self.window is not None:
            self.window.close()
            self.window = None
        self.session.clear()
        self.identity = None
        self.draft_dirty = False


def _number(value, suffix: str) -> str:
    return "-" if value is None else f"{float(value):+.3f} {suffix}"
