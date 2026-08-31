from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from oil_tracker.adapters.presentation.qt_frame_image_converter import blank_bgr_frame
from oil_tracker.config.defaults import PREVIEW_DEBOUNCE_MS
from oil_tracker.domain.enums import InitialObservationState
from oil_tracker.ui.presentation_labels import fill_state_label


class WorkbenchPlaybackController(QObject):
    """Own Workbench frame, transport, and live-preview presentation state."""

    def __init__(
        self,
        workbench,
        preview_controller,
        canvas,
        transport,
        detection_summary,
        debug_panel,
        status_bar,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.workbench = workbench
        self.preview_controller = preview_controller
        self.canvas = canvas
        self.transport = transport
        self.detection_summary = detection_summary
        self.debug_panel = debug_panel
        self.status_bar = status_bar

        self.current_frame = blank_bgr_frame(
            workbench.recipe.reference_frame_width,
            workbench.recipe.reference_frame_height,
        )
        self.current_time = 0.0
        self.current_frame_index = 0
        self.playback_speed = 1.0
        self.last_debug_artifacts = None
        self.preview_context: tuple[str, int, float] | None = None

        self.play_timer = QTimer(self)
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(PREVIEW_DEBOUNCE_MS)
        self._connect()

    def _connect(self) -> None:
        self.transport.playToggled.connect(self.toggle_play)
        self.transport.stepRequested.connect(self.step_frame)
        self.transport.skipRequested.connect(self.skip_seconds)
        self.transport.seekRequested.connect(self.seek_fraction)
        self.transport.seekReleased.connect(self.schedule_preview)
        self.transport.timeRequested.connect(self.seek_timestamp)
        self.transport.speedChanged.connect(self.set_playback_speed)
        self.play_timer.timeout.connect(self.play_tick)
        self.preview_timer.timeout.connect(self.request_preview)
        self.preview_controller.previewReady.connect(self.preview_ready)
        self.preview_controller.previewFailed.connect(self.preview_failed)

    def set_playback_speed(self, value: float) -> None:
        self.playback_speed = float(value)

    def toggle_play(self, playing: bool) -> None:
        if playing and self.workbench.video_reader:
            fps = max(1.0, self.workbench.video_reader.metadata.fps)
            self.play_timer.start(max(15, int(1000 / fps)))
        else:
            self.play_timer.stop()
            self.schedule_preview()

    def play_tick(self) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None:
            self.transport.play.setChecked(False)
            return
        step = self.playback_speed / max(1.0, metadata.fps)
        target = self.current_time + step
        if target >= metadata.duration_sec:
            self.transport.play.setChecked(False)
            return
        self.load_frame(target)

    def step_frame(self, direction: int) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None:
            return
        self.load_frame(
            max(
                0.0,
                min(
                    metadata.duration_sec,
                    self.current_time + direction / max(1.0, metadata.fps),
                ),
            )
        )
        self.schedule_preview()

    def seek_fraction(self, fraction: float) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None:
            return
        self.load_frame(metadata.duration_sec * fraction)
        self.preview_timer.start()

    def skip_seconds(self, delta_sec: float) -> None:
        self.seek_timestamp(self.current_time + float(delta_sec))

    def seek_timestamp(self, timestamp_sec: float) -> None:
        metadata = self.workbench.session.video_metadata
        if metadata is None:
            return
        self.load_frame(min(metadata.duration_sec, max(0.0, float(timestamp_sec))))
        self.schedule_preview()

    def load_frame(self, timestamp: float, *, reset_view: bool = False) -> None:
        try:
            frame, frame_index, actual = self.workbench.read_at(timestamp)
            self.present_frame(frame, frame_index, actual, reset_view=reset_view)
            self.invalidate_preview("현재 장면 분석 대기")
        except Exception as exc:
            self.status_bar.showMessage(f"영상 장면을 읽지 못했습니다: {exc}")

    def present_frame(
        self,
        frame,
        frame_index: int,
        timestamp: float,
        *,
        reset_view: bool = False,
    ) -> None:
        self.current_frame = frame
        self.current_frame_index = int(frame_index)
        self.current_time = float(timestamp)
        self.canvas.set_frame(frame, reset_view=reset_view)
        metadata = self.workbench.session.video_metadata
        self.transport.set_position(
            self.current_time,
            metadata.duration_sec if metadata else 0.0,
            self.current_frame_index,
        )

    def schedule_preview(self) -> None:
        self.invalidate_preview("현재 장면 분석 대기")
        if (
            self.workbench.selected_glass() is not None
            and self.workbench.session.video_metadata is not None
        ):
            self.preview_timer.start()
        else:
            self.preview_timer.stop()

    def request_preview(self) -> None:
        glass = self.workbench.selected_glass()
        if (
            glass is None
            or self.current_frame is None
            or self.workbench.session.video_metadata is None
        ):
            self.invalidate_preview("시험 영상과 Glass를 선택해 주세요")
            return
        self.preview_context = (glass.id, self.current_frame_index, self.current_time)
        self.detection_summary.set_loading()
        self.status_bar.showMessage("현재 장면을 분석하고 있습니다...")
        self.preview_controller.request(
            self.current_frame,
            glass,
            self.current_frame_index,
            self.current_time,
        )

    def preview_ready(self, detection, artifacts) -> None:
        context = self.preview_context
        if context is None:
            return
        selected_id = self.workbench.selected_glass_id
        if (
            detection.glass_id != selected_id
            or detection.glass_id != context[0]
            or detection.frame_index != self.current_frame_index
            or detection.frame_index != context[1]
            or abs(float(detection.time_sec) - self.current_time) > 1e-6
            or abs(float(detection.time_sec) - context[2]) > 1e-6
        ):
            return
        glass = self.workbench.selected_glass()
        if glass is None:
            return
        metadata = self.workbench.session.video_metadata
        tolerance = max(1.0, 2.0 / max(1.0, metadata.fps if metadata else 1.0))
        near_analysis_start = (
            abs(self.current_time - self.workbench.session.analysis_start_sec) <= tolerance
        )
        initial_state_needs_review = glass.initial_state in {
            InitialObservationState.AUTO,
            InitialObservationState.UNKNOWN_REVIEW,
        }
        self.canvas.set_detection(detection)
        self.detection_summary.set_detection(
            detection,
            glass,
            allow_initial_state_action=near_analysis_start or initial_state_needs_review,
        )
        self.debug_panel.set_artifacts(artifacts)
        self.last_debug_artifacts = artifacts
        self.status_bar.showMessage(
            f"현재 상태: {fill_state_label(detection.fill_state)} · "
            f"신뢰도 {detection.overall_confidence:.2f}"
        )

    def preview_failed(self, message: str) -> None:
        self.canvas.set_detection(None)
        self.detection_summary.set_failure(message)
        self.last_debug_artifacts = None
        self.status_bar.showMessage(f"현재 장면 분석 실패: {message}")

    def invalidate_preview(self, message: str) -> None:
        invalidate = getattr(self.preview_controller, "invalidate", None)
        if callable(invalidate):
            invalidate()
        self.preview_context = None
        self.canvas.set_detection(None)
        self.last_debug_artifacts = None
        if self.workbench.session.video_metadata is None:
            self.detection_summary.set_empty("시험 영상을 선택해 주세요")
        elif self.workbench.selected_glass() is None:
            self.detection_summary.set_empty("Glass를 선택해 주세요")
        else:
            self.detection_summary.set_empty(message)

    def set_placeholder(self) -> None:
        self.current_frame = blank_bgr_frame(
            self.workbench.recipe.reference_frame_width,
            self.workbench.recipe.reference_frame_height,
        )
        self.canvas.set_frame(self.current_frame, reset_view=True)
        self.invalidate_preview("시험 영상을 선택해 주세요")

    def close(self) -> None:
        self.play_timer.stop()
        self.preview_timer.stop()
        invalidate = getattr(self.preview_controller, "invalidate", None)
        if callable(invalidate):
            invalidate()
        self.preview_context = None
