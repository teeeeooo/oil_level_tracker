from __future__ import annotations

import logging
from pathlib import Path
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QImage
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStyle,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from oil_tracker.application.ports.review_io import (
    BundleAssetError,
    DebugCaseExportError,
    DebugCaseExporterPort,
    DebugTraceError,
    DebugTraceRepositoryFactory,
    DebugTraceRepositoryPort,
    ResultBundleError,
    ResultBundleReaderPort,
    SourceVideoError,
    SourceVideoMismatchError,
    SourceVideoResolverPort,
)
from oil_tracker.application.services.review_graph import build_review_graph_model
from oil_tracker.application.services.review_query import ReviewQueryModel
from oil_tracker.config.defaults import SUPPORTED_VIDEO_FILTER
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.result_actions import ResultActionError, ResultActionService
from oil_tracker.ui.widgets.result_debug_panel import ResultDebugPanel
from oil_tracker.ui.widgets.result_review_canvas import ResultReviewCanvas
from oil_tracker.ui.widgets.result_review_details import ResultReviewDetails
from oil_tracker.ui.widgets.result_review_graph import ResultReviewGraph
from oil_tracker.ui.widgets.result_review_navigation import ResultReviewNavigation
from oil_tracker.ui.widgets.transport_bar import TransportBar


LOGGER = logging.getLogger(__name__)


class ResultReviewWindow(QMainWindow):
    sameProfileRequested = Signal(object)

    def __init__(
        self,
        bundle_reader: ResultBundleReaderPort | None = None,
        source_resolver: SourceVideoResolverPort | None = None,
        playback_controller: ResultReviewController | None = None,
        action_service: ResultActionService | None = None,
        debug_repository_factory: DebugTraceRepositoryFactory | None = None,
        debug_case_exporter: DebugCaseExporterPort | None = None,
        png_exporter=None,
        mp4_export_controller=None,
        debug_artifact_presenter=None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.bundle_reader = bundle_reader
        self.source_resolver = source_resolver
        self.playback = playback_controller or ResultReviewController(parent=self)
        self.action_service = action_service
        self.debug_repository_factory = debug_repository_factory
        self.debug_case_exporter = debug_case_exporter
        self.png_exporter = png_exporter
        self.mp4_export_controller = mp4_export_controller
        if self.mp4_export_controller is not None and self.mp4_export_controller.parent() is None:
            self.mp4_export_controller.setParent(self)
        self.mp4_export_progress = None
        self.debug_artifact_presenter = debug_artifact_presenter
        self.bundle = None
        self.query: ReviewQueryModel | None = None
        self.debug_repository: DebugTraceRepositoryPort | None = None
        self.selected_glass_id = ""
        self.selected_event = None
        self.selected_debug_summary = None
        self.selected_debug_record = None
        self.current_source_image = QImage()
        self.current_render_image = QImage()
        self.current_frame_index = 0
        self.current_time = 0.0
        self.highlighted_candidate: int | None = None
        self.video_override: Path | None = None
        self.active_video_path: Path | None = None
        self.mode = "general"
        self.state = "bundle 없음"
        self.setWindowTitle("Rotary Oil Level Tracker — 결과 검토")
        self.setMinimumSize(1280, 760)
        self.resize(1540, 900)
        self._build_ui()
        self._connect()
        self._set_state("bundle 없음")

    def _build_ui(self) -> None:
        toolbar = QToolBar("결과 검토 도구", self)
        toolbar.setObjectName("resultReviewToolBar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(toolbar)
        self.open_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "결과 열기", self)
        self.reassign_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon), "원본 영상 다시 지정", self)
        self.report_action = QAction("결과 보고서 열기", self)
        self.folder_action = QAction("결과 폴더 열기", self)
        self.capture_action = QAction("선택 이벤트 캡처 열기", self)
        self.same_profile_action = QAction("같은 프로필로 새 영상 분석", self)
        self.save_png_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "현재 장면 PNG 저장", self)
        self.export_mp4_action = QAction("주석 MP4 내보내기", self)
        self.export_mp4_action.setToolTip("선택한 Glass의 저장된 분석 결과를 분석 구간 전체 MP4에 렌더링합니다.")
        self.details_action = QAction("세부 정보 보기", self)
        self.details_action.setCheckable(True)
        toolbar.addAction(self.open_action)
        toolbar.addWidget(QLabel("보기"))
        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("resultReviewModeCombo")
        self.mode_combo.addItem("일반 검토", "general")
        self.mode_combo.addItem("디버그", "debug")
        self.mode_combo.setToolTip("일반 검토는 공식 tracking 결과를, 디버그는 분석 당시 저장된 detector trace를 표시합니다.")
        toolbar.addWidget(self.mode_combo)

        self.review_actions_menu = QMenu("결과 작업", self)
        self.review_actions_menu.setObjectName("resultReviewActionMenu")
        self.review_actions_menu.addSection("보기")
        self.review_actions_menu.addAction(self.details_action)
        self.review_actions_menu.addAction(self.reassign_action)
        self.review_actions_menu.addSection("결과 열기")
        self.review_actions_menu.addAction(self.report_action)
        self.review_actions_menu.addAction(self.folder_action)
        self.review_actions_menu.addAction(self.capture_action)
        self.review_actions_menu.addSection("내보내기")
        self.review_actions_menu.addAction(self.save_png_action)
        self.review_actions_menu.addAction(self.export_mp4_action)
        self.review_actions_menu.addSection("다음 작업")
        self.review_actions_menu.addAction(self.same_profile_action)
        self.review_actions_button = QToolButton(toolbar)
        self.review_actions_button.setObjectName("toolbarMenuButton")
        self.review_actions_button.setText("작업")
        self.review_actions_button.setMenu(self.review_actions_menu)
        self.review_actions_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.review_actions_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar.addWidget(self.review_actions_button)

        toolbar_spacer = QWidget(toolbar)
        toolbar_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(toolbar_spacer)
        self.state_label = QLabel()
        self.state_label.setObjectName("stateBadge")
        toolbar.addWidget(self.state_label)

        self.navigation = ResultReviewNavigation()
        self.canvas = ResultReviewCanvas()
        self.graph = ResultReviewGraph()
        self.details = ResultReviewDetails()
        self.debug_details = ResultDebugPanel()
        self.detail_stack = QStackedWidget()
        self.detail_stack.addWidget(self.details)
        self.detail_stack.addWidget(self.debug_details)
        self.transport = TransportBar()
        self.video_path_label = QLabel("원본 영상 정보 없음")
        self.video_path_label.setWordWrap(True)
        self.video_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.visual_splitter = QSplitter(Qt.Orientation.Vertical)
        self.visual_splitter.setChildrenCollapsible(False)
        self.visual_splitter.addWidget(self.canvas)
        self.visual_splitter.addWidget(self.graph)
        self.visual_splitter.setStretchFactor(0, 1)
        self.visual_splitter.setStretchFactor(1, 0)
        self.visual_splitter.setSizes([560, 240])
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(6, 6, 6, 6)
        center_layout.addWidget(self.video_path_label)
        center_layout.addWidget(self.visual_splitter, 1)
        center_layout.addWidget(self.transport)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.addWidget(self.navigation)
        self.main_splitter.addWidget(center)
        self.main_splitter.addWidget(self.detail_stack)
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setStretchFactor(2, 0)
        self._details_splitter_sizes = [300, 850, 390]
        self.main_splitter.setSizes(self._details_splitter_sizes)
        self.setCentralWidget(self.main_splitter)
        self._set_details_visible(False)
        self.statusBar().showMessage("결과 bundle을 열어 주세요.")
        self._set_debug_mode_available(False, "이 결과에는 디버그 기록이 없습니다.")

    def _connect(self) -> None:
        self.open_action.triggered.connect(self.choose_bundle)
        self.reassign_action.triggered.connect(self.choose_replacement_video)
        self.report_action.triggered.connect(self.open_report)
        self.folder_action.triggered.connect(self.open_result_folder)
        self.capture_action.triggered.connect(self.open_event_capture)
        self.same_profile_action.triggered.connect(self.prepare_same_profile_analysis)
        self.save_png_action.triggered.connect(self.save_current_png)
        self.export_mp4_action.triggered.connect(self.export_annotated_mp4)
        self.details_action.toggled.connect(self._set_details_visible)
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        self.navigation.glassChanged.connect(self._glass_changed)
        self.navigation.filterChanged.connect(self._review_filter_changed)
        self.navigation.debugFilterChanged.connect(self._debug_filter_changed)
        self.navigation.eventSelected.connect(self._event_selected)
        self.navigation.eventActivated.connect(self._jump_to)
        self.navigation.reviewActivated.connect(self._jump_to)
        self.navigation.debugActivated.connect(self._debug_record_activated)
        self.navigation.previousRequested.connect(lambda: self._navigate_item(-1))
        self.navigation.nextRequested.connect(lambda: self._navigate_item(1))
        self.graph.timestampClicked.connect(self._graph_clicked)
        self.debug_details.candidateSelected.connect(self._candidate_highlight_changed)
        self.debug_details.artifactRequested.connect(self._load_debug_artifact)
        self.debug_details.exportRequested.connect(self.export_debug_case)
        self.transport.playToggled.connect(self._play_toggled)
        self.transport.stepRequested.connect(self.playback.step)
        self.transport.seekRequested.connect(self._seek_fraction)
        self.transport.speedChanged.connect(self.playback.set_speed)
        self.playback.frameReady.connect(self._frame_ready)
        self.playback.metadataChanged.connect(self._metadata_changed)
        self.playback.playbackStateChanged.connect(self._playback_state_changed)
        self.playback.failed.connect(self._playback_failed)
        if self.mp4_export_controller is not None:
            self.mp4_export_controller.progress.connect(self._mp4_export_progress)
            self.mp4_export_controller.completed.connect(self._mp4_export_completed)
            self.mp4_export_controller.failed.connect(self._mp4_export_failed)
            self.mp4_export_controller.cancelled.connect(self._mp4_export_cancelled)
            self.mp4_export_controller.runningChanged.connect(self._mp4_export_running_changed)

    def _set_details_visible(self, visible: bool) -> None:
        visible = bool(visible)
        self.detail_stack.setVisible(visible)
        if visible:
            self.main_splitter.setSizes(self._details_splitter_sizes)
        if self.details_action.isChecked() != visible:
            self.details_action.blockSignals(True)
            self.details_action.setChecked(visible)
            self.details_action.blockSignals(False)

    def choose_bundle(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "분석 결과 bundle 폴더 선택",
            str(self.bundle.root.parent if self.bundle is not None else Path.home()),
        )
        if directory:
            self.load_bundle(directory)

    def load_bundle(self, source: str | Path) -> bool:
        self.statusBar().showMessage("결과 bundle을 확인하고 있습니다...")
        debug_repository = None
        try:
            if self.bundle_reader is None:
                raise ResultBundleError("결과 bundle 접근 서비스가 구성되지 않았습니다.")
            bundle = self.bundle_reader.read(source)
            query = ReviewQueryModel(bundle)
            if bundle.has_debug_trace:
                try:
                    if self.debug_repository_factory is None:
                        raise DebugTraceError("debug trace 접근 서비스가 구성되지 않았습니다.")
                    debug_repository = self.debug_repository_factory(bundle)
                except DebugTraceError as exc:
                    bundle.debug_warning = str(exc)
                    debug_repository = None
        except ResultBundleError as exc:
            LOGGER.exception("Result bundle load failed")
            QMessageBox.critical(self, "결과 bundle 열기 실패", str(exc))
            self.statusBar().showMessage("기존 결과 검토 상태를 유지했습니다.")
            return False
        except Exception as exc:
            LOGGER.exception("Unexpected result bundle load failure")
            QMessageBox.critical(self, "결과 bundle 열기 실패", f"결과 파일을 읽을 수 없습니다: {exc}")
            self.statusBar().showMessage("기존 결과 검토 상태를 유지했습니다.")
            return False

        selected_glass_id = bundle.glasses[0].id if bundle.glasses else ""
        source_problem = ""
        if self.source_resolver is None:
            resolution = None
            source_problem = "원본 영상 접근 서비스가 구성되지 않았습니다."
        else:
            resolution = self.source_resolver.resolve(bundle)
        prepared = None
        validation = None
        if resolution is not None and resolution.path is not None:
            try:
                validation = self.source_resolver.validate_candidate(bundle, resolution.path)
                prepared = self.playback.prepare_video(validation.path, bundle.analysis_start_sec, emit_failure=False)
            except (SourceVideoError, SourceVideoMismatchError, Exception) as exc:
                LOGGER.exception("Resolved source video preparation failed")
                source_problem = str(exc)
                prepared = None

        self.playback.pause()
        if self.debug_repository is not None:
            self.debug_repository.close()
        self.debug_repository = debug_repository
        self.bundle = bundle
        self.query = query
        self.selected_glass_id = selected_glass_id
        self.selected_event = None
        self.selected_debug_summary = None
        self.selected_debug_record = None
        self.current_source_image = QImage()
        self.current_render_image = QImage()
        self.current_frame_index = 0
        self.current_time = bundle.analysis_start_sec
        self.highlighted_candidate = None
        self.video_override = None
        self.active_video_path = None
        self.mode = "general"
        self.mode_combo.blockSignals(True)
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.blockSignals(False)
        self.detail_stack.setCurrentWidget(self.details)
        self.navigation.set_bundle(bundle, query, selected_glass_id)
        self.details.clear()
        self.debug_details.clear()
        if debug_repository is not None:
            self._set_debug_mode_available(True, "")
            self.navigation.set_debug_records(debug_repository.index.records, enabled=True)
        else:
            message = bundle.debug_warning or "이 결과에는 디버그 기록이 없습니다."
            self._set_debug_mode_available(False, message)
            self.navigation.set_debug_records((), enabled=False, message=message)
        self._rebuild_graph()
        self._refresh_markers()
        if prepared is None:
            self.playback.close_video()
            self._show_missing_video(source_problem)
            if bundle.debug_warning:
                self.statusBar().showMessage(f"일반 결과는 열었습니다. 디버그 기록 경고: {bundle.debug_warning}", 15000)
            return True
        try:
            self.video_path_label.setText(str(validation.path))
            self.active_video_path = Path(validation.path)
            self.playback.activate_prepared(prepared)
        finally:
            prepared.close()
        messages = list(validation.warnings)
        if bundle.debug_warning:
            messages.append("디버그 기록: " + bundle.debug_warning)
        if messages:
            self.statusBar().showMessage("원본/디버그 확인 필요: " + " / ".join(messages), 15000)
        self._set_state("영상 로드됨 · 일시정지")
        return True

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
        if self.source_resolver is None:
            QMessageBox.critical(self, "원본 영상 열기 실패", "원본 영상 접근 서비스가 구성되지 않았습니다.")
            return False
        prepared = None
        try:
            validation = self.source_resolver.validate_candidate(self.bundle, path)
            prepared = self.playback.prepare_video(validation.path, timestamp, emit_failure=False)
        except SourceVideoMismatchError as exc:
            LOGGER.info("Rejected replacement video resolution mismatch: %s", path)
            QMessageBox.warning(self, "원본 영상 해상도 불일치", str(exc))
            return False
        except (SourceVideoError, Exception) as exc:
            LOGGER.exception("Source video preparation failed")
            QMessageBox.critical(self, "원본 영상 열기 실패", f"새 원본 영상을 적용하지 않았습니다.\n{exc}")
            return False
        try:
            self.playback.activate_prepared(prepared)
        finally:
            prepared.close()
        self.video_override = None if auto else validation.path
        self.active_video_path = Path(validation.path)
        self.video_path_label.setText(str(validation.path))
        if validation.warnings:
            self.statusBar().showMessage("원본 영상 확인 필요: " + " / ".join(validation.warnings), 12000)
        self._set_state("영상 로드됨 · 일시정지")
        return True

    def _show_missing_video(self, problem: str = "") -> None:
        if self.bundle is None:
            return
        original = self.bundle.source_video_path or "기록된 경로 없음"
        self.video_path_label.setText(f"분석 당시 경로: {original}")
        self.current_source_image = QImage()
        self.current_render_image = QImage()
        self.canvas.set_message("원본 영상을 찾을 수 없음\n저장된 debug artifact는 디버그 panel에서 확인할 수 있습니다.")
        self._set_state("bundle 준비됨 · 영상 없음")
        message = "영상 없이도 관찰창, 이벤트, 검토 목록과 저장된 debug artifact를 확인할 수 있습니다."
        if problem:
            message += f" 원본 영상 준비 실패: {problem}"
        self.statusBar().showMessage(message, 12000)

    def _metadata_changed(self, metadata) -> None:
        self.transport.set_position(self.current_time, metadata.duration_sec, self.current_frame_index)
        self._refresh_markers()

    def _frame_ready(self, image, frame_index: int, timestamp: float) -> None:
        if self.bundle is None or self.query is None or not self.selected_glass_id:
            return
        if not isinstance(image, QImage) or image.isNull():
            self._playback_failed("Result Review presentation boundary가 빈 Qt image를 반환했습니다.")
            return
        self.current_source_image = QImage(image).copy()
        self.current_frame_index = int(frame_index)
        self.current_time = float(timestamp)
        self._render_current_scene()
        metadata = self.playback.metadata
        duration = metadata.duration_sec if metadata is not None else 0.0
        self.transport.set_position(self.current_time, duration, self.current_frame_index)
        self.graph.set_cursor(self.current_time)
        self._set_state("재생 중" if self.playback.is_playing else "영상 로드됨 · 일시정지")

    def _render_current_scene(self) -> bool:
        if (
            self.bundle is None
            or self.query is None
            or not self.selected_glass_id
            or self.current_source_image.isNull()
            or self.playback.reader is None
        ):
            return False
        glass = self.bundle.glass_config(self.selected_glass_id)
        if glass is None:
            return False
        overlay = self.query.overlay_at(self.selected_glass_id, self.current_time)
        active = self.query.active_events(self.selected_glass_id, self.current_time)
        debug_matches = False
        try:
            if self.mode == "debug":
                record = self.selected_debug_record
                tolerance = self._debug_tolerance()
                debug_matches = (
                    record is not None
                    and record.glass_id == self.selected_glass_id
                    and abs(record.timestamp_sec - self.current_time) <= tolerance
                )
                if debug_matches:
                    rendered = self.playback.render_debug(
                        glass,
                        record,
                        self.current_time,
                        self.highlighted_candidate,
                    )
                else:
                    rendered = self.playback.render_general(glass, overlay)
            else:
                rendered = self.playback.render_general(glass, overlay)
        except Exception as exc:
            LOGGER.exception("Result Review raster presentation failed")
            self.statusBar().showMessage(f"현재 장면 overlay를 표시할 수 없습니다: {exc}", 12000)
            return False
        if not isinstance(rendered, QImage) or rendered.isNull():
            self.statusBar().showMessage("현재 장면 overlay adapter가 빈 Qt image를 반환했습니다.", 12000)
            return False
        self.current_render_image = QImage(rendered).copy()
        self.canvas.set_image(self.current_render_image)
        if self.mode == "debug" and debug_matches:
            self.debug_details.set_record(self.selected_debug_record, self.current_time)
        elif self.mode == "debug":
            self.debug_details.summary.setText(
                "현재 decoded 시각에는 선택된 debug record가 없습니다.\n"
                "일반 tracking overlay만 임시 표시되며 candidate layer는 숨겨졌습니다."
            )
        else:
            self.details.update_details(
                self.bundle,
                self.selected_glass_id,
                overlay,
                self.current_frame_index,
                self.current_time,
                active,
            )
        return True

    def _candidate_highlight_changed(self, candidate_index: int) -> None:
        self.highlighted_candidate = int(candidate_index)
        if self.mode == "debug":
            self._render_current_scene()

    def _glass_changed(self, glass_id: str) -> None:
        if self.bundle is None or self.query is None:
            return
        self.selected_glass_id = glass_id
        self.selected_event = None
        self.highlighted_candidate = None
        if self.selected_debug_record is not None and self.selected_debug_record.glass_id != glass_id:
            self.selected_debug_summary = None
            self.selected_debug_record = None
            self.debug_details.clear("선택한 관찰창의 디버그 장면을 선택해 주세요.")
        self.navigation.refresh_items(self.bundle, self.query, glass_id)
        self._refresh_markers()
        self._rebuild_graph()
        self._render_current_scene()

    def _review_filter_changed(self, _value: str) -> None:
        if self.bundle is None or self.query is None:
            return
        self.navigation.refresh_items(self.bundle, self.query, self.selected_glass_id)
        self._refresh_markers()
        self._rebuild_graph()

    def _debug_filter_changed(self, _value: str) -> None:
        self._refresh_markers()
        self._rebuild_graph()

    def _event_selected(self, event) -> None:
        self.selected_event = event
        self.capture_action.setEnabled(bool(self.bundle is not None and event is not None and event.capture_path))

    def _mode_changed(self, _index: int) -> None:
        requested = str(self.mode_combo.currentData() or "general")
        if requested == "debug" and self.debug_repository is None:
            message = self.bundle.debug_warning if self.bundle is not None and self.bundle.debug_warning else "이 결과에는 디버그 기록이 없습니다."
            QMessageBox.information(self, "디버그 기록 없음", message)
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(0)
            self.mode_combo.blockSignals(False)
            requested = "general"
        self.mode = requested
        self.highlighted_candidate = None
        self.detail_stack.setCurrentWidget(self.debug_details if self.mode == "debug" else self.details)
        if self.mode == "debug":
            self._set_details_visible(True)
        self._render_current_scene()
        self._rebuild_graph()
        self._refresh_markers()

    def _set_debug_mode_available(self, enabled: bool, message: str) -> None:
        item = self.mode_combo.model().item(1)
        if item is not None:
            item.setEnabled(enabled)
            item.setToolTip("분석 당시 저장된 trace를 표시합니다." if enabled else message)
        self.mode_combo.setToolTip(message if not enabled else "일반 검토와 분석 당시 저장된 디버그 trace를 전환합니다.")

    def _debug_record_activated(self, summary) -> None:
        if self.debug_repository is None:
            return
        try:
            record = self.debug_repository.load_record(summary.record_id)
        except DebugTraceError as exc:
            QMessageBox.warning(self, "디버그 장면 읽기 실패", str(exc))
            return
        self.playback.pause()
        self.selected_debug_summary = summary
        self.selected_debug_record = record
        self.highlighted_candidate = None
        self.mode_combo.setCurrentIndex(1)
        self.debug_details.set_record(record, None)
        self._load_debug_artifact(self.debug_details.current_artifact_key())
        self._rebuild_graph()
        self._refresh_markers()
        self._jump_to(record.timestamp_sec)

    def _load_debug_artifact(self, key: str) -> None:
        if self.debug_repository is None or self.selected_debug_record is None or not key:
            return
        if self.debug_artifact_presenter is None:
            self.debug_details.set_artifact(key, None, "debug artifact presentation adapter가 구성되지 않았습니다.")
            return
        try:
            image = self.debug_artifact_presenter.present(
                self.debug_repository,
                self.selected_debug_record,
                key,
            )
            self.debug_details.set_artifact(key, image)
        except (DebugTraceError, TypeError, ValueError) as exc:
            self.debug_details.set_artifact(key, None, str(exc))

    def _rebuild_graph(self) -> None:
        if self.bundle is None or self.query is None or not self.selected_glass_id:
            self.graph.clear_model()
            return
        model = build_review_graph_model(
            self.bundle,
            self.selected_glass_id,
            self.navigation.current_filter(),
            self.current_time,
            self.query,
            self._filtered_debug_summaries(),
            self.selected_debug_summary.record_id if self.selected_debug_summary is not None else "",
        )
        self.graph.set_model(model)

    def _graph_clicked(self, timestamp: float) -> None:
        if self.mode == "debug" and self.debug_repository is not None:
            summary = self.debug_repository.nearest(self.selected_glass_id, timestamp, self._debug_tolerance())
            if summary is not None and summary in self._filtered_debug_summaries():
                self._debug_record_activated(summary)
                return
        self._jump_to(timestamp)

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
        QMessageBox.critical(self, "영상 재생 오류", message)

    def _seek_fraction(self, fraction: float) -> None:
        metadata = self.playback.metadata
        if metadata is not None:
            self.playback.seek(metadata.duration_sec * float(fraction))

    def _jump_to(self, timestamp: float) -> None:
        if self.bundle is None:
            return
        timestamp = min(self.bundle.analysis_end_sec, max(self.bundle.analysis_start_sec, float(timestamp)))
        self.playback.pause()
        if self.playback.reader is not None:
            self.playback.seek(timestamp)
        else:
            self.current_time = timestamp
            self.graph.set_cursor(timestamp)
            if self.mode == "debug" and self.selected_debug_record is not None:
                self.debug_details.set_record(self.selected_debug_record, None)
            self.statusBar().showMessage(f"원본 영상 없음 · 선택 항목 시각 {timestamp:.3f}초")

    def _navigate_item(self, direction: int) -> None:
        if self.query is None or not self.selected_glass_id:
            return
        if self.navigation.active_tab_is_debug():
            values = list(self._filtered_debug_summaries())
            current = self.current_time
            ordered = sorted(values, key=lambda item: (item.timestamp_sec, item.frame_index, item.record_id))
            if direction < 0:
                target = next((item for item in reversed(ordered) if item.timestamp_sec < current - 1e-9), None)
            else:
                target = next((item for item in ordered if item.timestamp_sec > current + 1e-9), None)
            if target is not None:
                self._debug_record_activated(target)
                return
            timestamp = None
        elif self.navigation.active_tab_is_events():
            target = self.query.previous_event(self.selected_glass_id, self.current_time) if direction < 0 else self.query.next_event(self.selected_glass_id, self.current_time)
            timestamp = target.start_time_sec if target is not None else None
        else:
            target = self.query.previous_review(self.selected_glass_id, self.current_time, self.navigation.current_filter()) if direction < 0 else self.query.next_review(self.selected_glass_id, self.current_time, self.navigation.current_filter())
            timestamp = target.representative_time_sec if target is not None else None
        if timestamp is None:
            self.statusBar().showMessage("현재 필터에서 이동할 이전/다음 항목이 없습니다.")
        else:
            self._jump_to(timestamp)

    def _filtered_debug_summaries(self):
        if self.debug_repository is None:
            return ()
        _key, reasons = self.navigation.current_debug_filter()
        return self.debug_repository.summaries(self.selected_glass_id, reasons or None)

    def _debug_tolerance(self) -> float:
        if self.bundle is None:
            return 0.05
        fps = max(0.1, float(self.bundle.session.sampling_fps or 1.0))
        return max(0.05, 0.55 / fps)

    def _refresh_markers(self) -> None:
        if self.bundle is None or self.query is None:
            return
        metadata = self.playback.metadata or self.bundle.source_metadata
        duration = metadata.duration_sec if metadata is not None else max(self.bundle.analysis_end_sec, 0.0)
        self.transport.slider.set_markers(duration, self.bundle.analysis_start_sec, self.bundle.analysis_end_sec, self.bundle.compressor_start_sec)
        events = [event.start_time_sec for event in self.query.events_for_glass(self.selected_glass_id)]
        intervals = [
            (interval.start_time_sec, interval.end_time_sec)
            for interval in self.query.filtered_intervals(self.selected_glass_id, self.navigation.current_filter())
        ]
        self.transport.slider.set_review_markers(duration, events, intervals)
        summaries = self._filtered_debug_summaries()
        self.transport.slider.set_debug_markers(
            duration,
            [summary.timestamp_sec for summary in summaries],
            self.selected_debug_summary.timestamp_sec if self.selected_debug_summary is not None else None,
        )

    def export_debug_case(self) -> None:
        if self.bundle is None or self.debug_repository is None or self.selected_debug_record is None:
            QMessageBox.information(self, "디버그 재현 패키지", "내보낼 디버그 장면을 먼저 선택해 주세요.")
            return
        if self.debug_case_exporter is None:
            QMessageBox.critical(self, "디버그 재현 패키지 실패", "debug case export 서비스가 구성되지 않았습니다.")
            return
        destination = QFileDialog.getExistingDirectory(self, "디버그 재현 패키지를 만들 상위 폴더 선택", str(self.bundle.root.parent))
        if not destination:
            return
        try:
            output = self.debug_case_exporter.export(
                self.bundle,
                self.debug_repository,
                self.selected_debug_record.record_id,
                destination,
                source_video_path=self.active_video_path,
            )
        except (DebugCaseExportError, DebugTraceError, OSError, ValueError) as exc:
            LOGGER.exception("Debug case export failed")
            QMessageBox.critical(self, "디버그 재현 패키지 실패", str(exc))
            return
        QMessageBox.information(self, "디버그 재현 패키지 완료", f"독립 패키지를 생성했습니다.\n{output}")

    def open_report(self) -> None:
        self._run_result_action("결과 보고서 열기", lambda: self.action_service.open_report(self.bundle))

    def open_result_folder(self) -> None:
        self._run_result_action("결과 폴더 열기", lambda: self.action_service.open_folder(self.bundle))

    def open_event_capture(self) -> None:
        event = self.selected_event
        if event is None or not event.capture_path:
            QMessageBox.information(self, "이벤트 캡처", "캡처가 기록된 이벤트를 먼저 선택해 주세요.")
            return
        self._run_result_action("이벤트 캡처 열기", lambda: self.action_service.open_capture(self.bundle, event.capture_path))

    def _run_result_action(self, title: str, action) -> bool:
        if self.bundle is None:
            QMessageBox.information(self, title, "먼저 결과 bundle을 열어 주세요.")
            return False
        if self.action_service is None:
            QMessageBox.critical(self, title, "결과 파일 작업 서비스가 구성되지 않았습니다.")
            return False
        try:
            action()
            return True
        except (BundleAssetError, ResultActionError) as exc:
            QMessageBox.warning(self, title, str(exc))
        except Exception as exc:
            LOGGER.exception("Result action failed")
            QMessageBox.critical(self, title, f"작업을 완료할 수 없습니다: {exc}")
        return False

    def prepare_same_profile_analysis(self) -> None:
        if self.bundle is not None:
            self.sameProfileRequested.emit(self.bundle)

    def save_current_png(self) -> None:
        if self.bundle is None or self.current_render_image.isNull():
            QMessageBox.information(self, "PNG 저장", "저장할 원본 영상 장면이 없습니다.")
            return
        if self.png_exporter is None:
            QMessageBox.critical(self, "PNG 저장 실패", "PNG storage adapter가 구성되지 않았습니다.")
            return
        glass = self.bundle.glass_config(self.selected_glass_id)
        name = _safe_filename(glass.name if glass is not None else self.selected_glass_id)
        default = self.bundle.root.parent / f"review_{name}_{self.current_time:.3f}.png"
        selected, _ = QFileDialog.getSaveFileName(self, "overlay 장면 PNG 저장", str(default), "PNG 이미지 (*.png)")
        if not selected:
            return
        try:
            destination = self.png_exporter.export(
                QImage(self.current_render_image).copy(),
                selected,
                protected_roots=(self.bundle.root,),
                overwrite=True,
            )
        except Exception as exc:
            LOGGER.exception("Review PNG save failed")
            QMessageBox.critical(self, "PNG 저장 실패", f"PNG 이미지를 저장할 수 없습니다: {exc}")
            return
        QMessageBox.information(self, "PNG 저장 완료", f"원본 해상도 overlay 이미지를 저장했습니다.\n{destination}")

    def export_annotated_mp4(self) -> None:
        if (
            self.bundle is None
            or self.query is None
            or self.active_video_path is None
            or not self.selected_glass_id
        ):
            QMessageBox.information(self, "주석 MP4 내보내기", "결과 bundle과 원본 영상을 먼저 준비해 주세요.")
            return
        if self.mp4_export_controller is None:
            QMessageBox.critical(self, "주석 MP4 내보내기 실패", "MP4 export controller가 구성되지 않았습니다.")
            return
        presets = ["일반 공유용"]
        if self.debug_repository is not None:
            presets.append("디버그 정보 포함")
        preset, accepted = QInputDialog.getItem(
            self,
            "주석 MP4 preset",
            "내보낼 overlay preset을 선택해 주세요.",
            presets,
            0,
            False,
        )
        if not accepted:
            return
        include_debug = preset == "디버그 정보 포함"
        glass = self.bundle.glass_config(self.selected_glass_id)
        name = _safe_filename(glass.name if glass is not None else self.selected_glass_id)
        suffix = "_debug" if include_debug else ""
        default = self.bundle.root.parent / f"review_{name}_annotated{suffix}.mp4"
        selected, _ = QFileDialog.getSaveFileName(self, "주석 MP4 저장", str(default), "MP4 비디오 (*.mp4)")
        if not selected:
            return
        destination = _normalized_mp4_path(selected)
        overwrite = False
        if destination.exists():
            answer = QMessageBox.question(
                self,
                "기존 MP4 덮어쓰기",
                f"이미 같은 파일이 있습니다. 명시적으로 덮어쓰시겠습니까?\n{destination}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            overwrite = True
        self._open_mp4_progress()
        try:
            self.mp4_export_controller.start(
                bundle=self.bundle,
                query=self.query,
                source_video_path=Path(self.active_video_path),
                glass_id=self.selected_glass_id,
                destination=destination,
                include_debug=include_debug,
                overwrite=overwrite,
            )
        except Exception as exc:
            self._finish_mp4_progress()
            QMessageBox.critical(self, "주석 MP4 내보내기 실패", str(exc))

    def _open_mp4_progress(self) -> None:
        dialog = QProgressDialog("주석 MP4를 내보내고 있습니다...", "취소", 0, 100, self)
        dialog.setWindowTitle("주석 MP4 내보내기")
        dialog.setWindowModality(Qt.WindowModality.NonModal)
        dialog.setMinimumDuration(0)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.canceled.connect(self.mp4_export_controller.cancel)
        self.mp4_export_progress = dialog
        dialog.show()

    def _mp4_export_progress(self, update) -> None:
        dialog = self.mp4_export_progress
        if dialog is None:
            return
        total = max(1, int(getattr(update, "estimated_total_frames", 1)))
        processed = max(0, int(getattr(update, "processed_frames", 0)))
        dialog.setValue(min(99, int(100 * processed / total)))
        dialog.setLabelText(
            f"주석 MP4 인코딩 중 · {processed}/{total} frame · "
            f"{float(getattr(update, 'timestamp_sec', 0.0)):.3f}s"
        )

    def _mp4_export_completed(self, result) -> None:
        if self.mp4_export_progress is not None:
            self.mp4_export_progress.setValue(100)
        self._finish_mp4_progress()
        self.statusBar().showMessage(f"주석 MP4 저장 완료: {result.path}", 12000)
        QMessageBox.information(self, "주석 MP4 저장 완료", f"분석 구간 annotated MP4를 저장했습니다.\n{result.path}")

    def _mp4_export_failed(self, message: str) -> None:
        self._finish_mp4_progress()
        LOGGER.error("Annotated MP4 export failed: %s", message)
        QMessageBox.critical(self, "주석 MP4 내보내기 실패", message)

    def _mp4_export_cancelled(self) -> None:
        self._finish_mp4_progress()
        self.statusBar().showMessage("주석 MP4 내보내기를 취소했습니다.", 8000)

    def _mp4_export_running_changed(self, _running: bool) -> None:
        self._set_state(self.state)

    def _finish_mp4_progress(self) -> None:
        dialog, self.mp4_export_progress = self.mp4_export_progress, None
        if dialog is not None:
            dialog.close()
            dialog.deleteLater()

    def _set_state(self, state: str) -> None:
        self.state = state
        self.state_label.setText(f"상태: {state}")
        has_bundle = self.bundle is not None
        self.reassign_action.setEnabled(has_bundle)
        self.report_action.setEnabled(has_bundle)
        self.folder_action.setEnabled(has_bundle)
        self.same_profile_action.setEnabled(has_bundle)
        self.capture_action.setEnabled(has_bundle and self.selected_event is not None and bool(self.selected_event.capture_path))
        self.save_png_action.setEnabled(has_bundle and not self.current_render_image.isNull())
        export_running = bool(
            self.mp4_export_controller is not None
            and self.mp4_export_controller.running
        )
        self.export_mp4_action.setEnabled(
            has_bundle
            and self.query is not None
            and self.active_video_path is not None
            and bool(self.selected_glass_id)
            and self.mp4_export_controller is not None
            and not export_running
        )

    def closeEvent(self, event) -> None:
        if self.mp4_export_controller is not None and not self.mp4_export_controller.close():
            event.ignore()
            self.statusBar().showMessage(
                "주석 MP4 작업이 아직 종료되지 않아 Viewer를 닫지 않았습니다.",
                10000,
            )
            return
        self._finish_mp4_progress()
        self.playback.close()
        self.graph.close()
        if self.debug_repository is not None:
            self.debug_repository.close()
            self.debug_repository = None
        self.debug_details.clear()
        self.current_source_image = QImage()
        self.current_render_image = QImage()
        self.highlighted_candidate = None
        self.selected_event = None
        self.selected_debug_summary = None
        self.selected_debug_record = None
        super().closeEvent(event)


def _safe_filename(value: str) -> str:
    normalized = re.sub(r"[\\/:*?\"<>|]+", "_", value.strip())
    normalized = re.sub(r"\s+", "_", normalized).strip("._")
    return normalized or "glass"


def _normalized_mp4_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.suffix.lower() == ".mp4" else path.with_suffix(".mp4")
