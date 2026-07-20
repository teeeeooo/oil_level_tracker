from __future__ import annotations

import logging
from pathlib import Path
import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleError, ResultBundleReader
from oil_tracker.adapters.vision.source_video_resolver import (
    SourceVideoError,
    SourceVideoMismatchError,
    SourceVideoResolver,
)
from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.config.defaults import SUPPORTED_VIDEO_FILTER
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.widgets.result_review_canvas import ResultReviewCanvas
from oil_tracker.ui.widgets.result_review_details import ResultReviewDetails
from oil_tracker.ui.widgets.result_review_navigation import ResultReviewNavigation
from oil_tracker.ui.widgets.transport_bar import TransportBar


LOGGER = logging.getLogger(__name__)


class ResultReviewWindow(QMainWindow):
    def __init__(
        self,
        bundle_reader: ResultBundleReader | None = None,
        source_resolver: SourceVideoResolver | None = None,
        playback_controller: ResultReviewController | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.bundle_reader = bundle_reader or ResultBundleReader()
        self.source_resolver = source_resolver or SourceVideoResolver()
        self.playback = playback_controller or ResultReviewController(parent=self)
        self.bundle = None
        self.query: ReviewQueryModel | None = None
        self.selected_glass_id = ""
        self.current_frame = None
        self.current_frame_index = 0
        self.current_time = 0.0
        self.video_override: Path | None = None
        self.state = "bundle 없음"
        self.setWindowTitle("Rotary Oil Level Tracker — 결과 검토")
        self.setMinimumSize(1280, 760)
        self.resize(1540, 900)
        self._build_ui()
        self._connect()
        self._set_state("bundle 없음")

    def _build_ui(self) -> None:
        toolbar = QToolBar("결과 검토 도구", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        self.open_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton),
            "결과 bundle 열기",
            self,
        )
        self.reassign_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon),
            "원본 영상 다시 지정",
            self,
        )
        self.save_png_action = QAction(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton),
            "현재 장면 PNG 저장",
            self,
        )
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.reassign_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_png_action)
        toolbar.addSeparator()
        self.state_label = QLabel()
        toolbar.addWidget(self.state_label)

        self.navigation = ResultReviewNavigation()
        self.canvas = ResultReviewCanvas()
        self.details = ResultReviewDetails()
        self.transport = TransportBar()
        self.video_path_label = QLabel("원본 영상 정보 없음")
        self.video_path_label.setWordWrap(True)
        self.video_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(6, 6, 6, 6)
        center_layout.addWidget(self.video_path_label)
        center_layout.addWidget(self.canvas, 1)
        center_layout.addWidget(self.transport)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.navigation)
        splitter.addWidget(center)
        splitter.addWidget(self.details)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([300, 900, 340])
        self.setCentralWidget(splitter)
        self.statusBar().showMessage("결과 bundle을 열어 주세요.")

    def _connect(self) -> None:
        self.open_action.triggered.connect(self.choose_bundle)
        self.reassign_action.triggered.connect(self.choose_replacement_video)
        self.save_png_action.triggered.connect(self.save_current_png)
        self.navigation.glassChanged.connect(self._glass_changed)
        self.navigation.eventActivated.connect(self._jump_to)
        self.navigation.reviewActivated.connect(self._jump_to)
        self.navigation.previousRequested.connect(lambda: self._navigate_item(-1))
        self.navigation.nextRequested.connect(lambda: self._navigate_item(1))
        self.transport.playToggled.connect(self._play_toggled)
        self.transport.stepRequested.connect(self.playback.step)
        self.transport.seekRequested.connect(self._seek_fraction)
        self.transport.speedChanged.connect(self.playback.set_speed)
        self.playback.frameReady.connect(self._frame_ready)
        self.playback.metadataChanged.connect(self._metadata_changed)
        self.playback.playbackStateChanged.connect(self._playback_state_changed)
        self.playback.failed.connect(self._playback_failed)

    def choose_bundle(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "분석 결과 bundle 폴더 선택",
            str(self.bundle.root.parent if self.bundle is not None else Path.home()),
        )
        if directory:
            self.load_bundle(directory)

    def load_bundle(self, source: str | Path) -> bool:
        self._set_state("bundle 읽는 중")
        self.playback.close_video()
        self.current_frame = None
        self.video_override = None
        try:
            bundle = self.bundle_reader.read(source)
        except ResultBundleError as exc:
            LOGGER.exception("Result bundle load failed")
            self._set_state("오류")
            QMessageBox.critical(self, "결과 bundle 열기 실패", str(exc))
            return False
        except Exception as exc:
            LOGGER.exception("Unexpected result bundle load failure")
            self._set_state("오류")
            QMessageBox.critical(self, "결과 bundle 열기 실패", f"결과 파일을 읽을 수 없습니다: {exc}")
            return False

        self.bundle = bundle
        self.query = ReviewQueryModel(bundle)
        self.selected_glass_id = bundle.glasses[0].id if bundle.glasses else ""
        self.navigation.set_bundle(bundle, self.query, self.selected_glass_id)
        self.details.clear()
        self._refresh_markers()
        self.current_time = bundle.analysis_start_sec
        self.current_frame_index = 0
        resolution = self.source_resolver.resolve(bundle)
        if resolution.path is None:
            self._show_missing_video()
            return True
        return self._open_resolved_video(resolution.path, bundle.analysis_start_sec, auto=True)

    def choose_replacement_video(self) -> None:
        if self.bundle is None:
            QMessageBox.information(self, "원본 영상 다시 지정", "먼저 결과 bundle을 열어 주세요.")
            return
        selected, _ = QFileDialog.getOpenFileName(
            self,
            "원본 영상 다시 지정",
            str(Path(self.bundle.source_video_path).parent if self.bundle.source_video_path else self.bundle.root),
            SUPPORTED_VIDEO_FILTER,
        )
        if selected:
            self._open_resolved_video(Path(selected), self.current_time, auto=False)

    def _open_resolved_video(self, path: Path, timestamp: float, *, auto: bool) -> bool:
        assert self.bundle is not None
        try:
            validation = self.source_resolver.validate_candidate(self.bundle, path)
        except SourceVideoMismatchError as exc:
            LOGGER.info("Rejected replacement video resolution mismatch: %s", path)
            QMessageBox.warning(self, "원본 영상 해상도 불일치", str(exc))
            self._show_missing_video(keep_current=True)
            return False
        except SourceVideoError as exc:
            LOGGER.exception("Source video validation failed")
            QMessageBox.critical(self, "원본 영상 열기 실패", str(exc))
            self._show_missing_video(keep_current=True)
            return False
        try:
            self.playback.open_video(validation.path, timestamp)
        except Exception:
            self._show_missing_video(keep_current=True)
            return False
        self.video_override = None if auto else validation.path
        self.video_path_label.setText(str(validation.path))
        if validation.warnings:
            self.statusBar().showMessage("원본 영상 확인 필요: " + " / ".join(validation.warnings), 12000)
        self._set_state("영상 로드됨 · 일시정지")
        return True

    def _show_missing_video(self, *, keep_current: bool = False) -> None:
        if self.bundle is None:
            return
        if not keep_current:
            self.playback.close_video()
        original = self.bundle.source_video_path or "기록된 경로 없음"
        self.video_path_label.setText(f"분석 당시 경로: {original}")
        self.canvas.set_message(
            "원본 영상을 찾을 수 없음\n분석 당시 경로를 확인한 뒤 '원본 영상 다시 지정'을 선택해 주세요."
        )
        self._set_state("bundle 준비됨 · 영상 없음")
        self.statusBar().showMessage("영상 없이도 관찰창, 이벤트와 검토 필요 목록을 확인할 수 있습니다.")

    def _metadata_changed(self, metadata) -> None:
        self.transport.set_position(self.current_time, metadata.duration_sec, self.current_frame_index)
        self._refresh_markers()

    def _frame_ready(self, frame, frame_index: int, timestamp: float) -> None:
        if self.bundle is None or self.query is None or not self.selected_glass_id:
            return
        self.current_frame = frame.copy()
        self.current_frame_index = int(frame_index)
        self.current_time = float(timestamp)
        glass = self.bundle.glass_config(self.selected_glass_id)
        if glass is None:
            return
        overlay = self.query.overlay_at(self.selected_glass_id, self.current_time)
        self.canvas.set_review_frame(self.current_frame, glass, overlay)
        active = self.query.active_events(self.selected_glass_id, self.current_time)
        self.details.update_details(
            self.bundle,
            self.selected_glass_id,
            overlay,
            self.current_frame_index,
            self.current_time,
            active,
        )
        metadata = self.playback.metadata
        duration = metadata.duration_sec if metadata is not None else 0.0
        self.transport.set_position(self.current_time, duration, self.current_frame_index)

    def _glass_changed(self, glass_id: str) -> None:
        if self.bundle is None or self.query is None:
            return
        self.selected_glass_id = glass_id
        self.navigation.refresh_items(self.bundle, self.query, glass_id)
        self._refresh_markers()
        if self.current_frame is not None:
            glass = self.bundle.glass_config(glass_id)
            if glass is not None:
                overlay = self.query.overlay_at(glass_id, self.current_time)
                self.canvas.refresh_overlay(glass, overlay)
                self.details.update_details(
                    self.bundle,
                    glass_id,
                    overlay,
                    self.current_frame_index,
                    self.current_time,
                    self.query.active_events(glass_id, self.current_time),
                )

    def _play_toggled(self, playing: bool) -> None:
        if playing:
            self.playback.play()
        else:
            self.playback.pause()

    def _playback_state_changed(self, state: str) -> None:
        if state != "재생 중" and self.transport.play.isChecked():
            self.transport.play.blockSignals(True)
            self.transport.play.setChecked(False)
            self.transport.play.setText("재생")
            self.transport.play.blockSignals(False)
        if state == "재생 중":
            self._set_state("재생 중")
        elif self.playback.reader is not None:
            self._set_state("영상 로드됨 · 일시정지")

    def _playback_failed(self, message: str) -> None:
        LOGGER.error("Review playback failed: %s", message)
        self._set_state("오류")
        QMessageBox.critical(self, "영상 재생 오류", message)

    def _seek_fraction(self, fraction: float) -> None:
        metadata = self.playback.metadata
        if metadata is not None:
            self.playback.seek(metadata.duration_sec * float(fraction))

    def _jump_to(self, timestamp: float) -> None:
        self.playback.pause()
        if self.playback.reader is not None:
            self.playback.seek(float(timestamp))
        else:
            self.current_time = float(timestamp)
            self.statusBar().showMessage(f"원본 영상 없음 · 선택 항목 시각 {timestamp:.3f}초")

    def _navigate_item(self, direction: int) -> None:
        if self.query is None or not self.selected_glass_id:
            return
        target = None
        if self.navigation.active_tab_is_events():
            target = (
                self.query.previous_event(self.selected_glass_id, self.current_time)
                if direction < 0
                else self.query.next_event(self.selected_glass_id, self.current_time)
            )
            timestamp = target.start_time_sec if target is not None else None
        else:
            intervals = self.query.low_confidence_intervals(self.selected_glass_id)
            times = [item.representative_time_sec for item in intervals]
            candidates = [value for value in times if value < self.current_time] if direction < 0 else [value for value in times if value > self.current_time]
            timestamp = (candidates[-1] if direction < 0 else candidates[0]) if candidates else None
        if timestamp is None:
            self.statusBar().showMessage("이동할 이전/다음 항목이 없습니다.")
        else:
            self._jump_to(timestamp)

    def _refresh_markers(self) -> None:
        if self.bundle is None or self.query is None:
            return
        metadata = self.playback.metadata or self.bundle.source_metadata
        duration = metadata.duration_sec if metadata is not None else max(self.bundle.analysis_end_sec, 0.0)
        self.transport.slider.set_markers(
            duration,
            self.bundle.analysis_start_sec,
            self.bundle.analysis_end_sec,
            self.bundle.compressor_start_sec,
        )
        events = [event.start_time_sec for event in self.query.events_for_glass(self.selected_glass_id)]
        intervals = [
            (interval.start_time_sec, interval.end_time_sec)
            for interval in self.query.low_confidence_intervals(self.selected_glass_id)
        ]
        self.transport.slider.set_review_markers(duration, events, intervals)

    def save_current_png(self) -> None:
        if self.bundle is None or self.current_frame is None:
            QMessageBox.information(self, "PNG 저장", "저장할 원본 영상 장면이 없습니다.")
            return
        glass = self.bundle.glass_config(self.selected_glass_id)
        name = _safe_filename(glass.name if glass is not None else self.selected_glass_id)
        default = self.bundle.root.parent / f"review_{name}_{self.current_time:.3f}.png"
        selected, _ = QFileDialog.getSaveFileName(self, "overlay 장면 PNG 저장", str(default), "PNG 이미지 (*.png)")
        if not selected:
            return
        try:
            destination = self.canvas.save_png(selected)
        except Exception as exc:
            LOGGER.exception("Review PNG save failed")
            QMessageBox.critical(self, "PNG 저장 실패", f"PNG 이미지를 저장할 수 없습니다: {exc}")
            return
        QMessageBox.information(self, "PNG 저장 완료", f"원본 해상도 overlay 이미지를 저장했습니다.\n{destination}")

    def _set_state(self, state: str) -> None:
        self.state = state
        self.state_label.setText(f"상태: {state}")
        has_bundle = self.bundle is not None
        self.reassign_action.setEnabled(has_bundle)
        self.save_png_action.setEnabled(has_bundle and self.current_frame is not None)

    def closeEvent(self, event) -> None:
        self.playback.close()
        self.current_frame = None
        super().closeEvent(event)


def _safe_filename(value: str) -> str:
    normalized = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    normalized = re.sub(r"\s+", "_", normalized).strip("._")
    return normalized or "glass"
