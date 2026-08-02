from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from oil_tracker.adapters.vision.source_video_resolver import SourceVideoResolver
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewEvent, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.result_review_window import ResultReviewWindow
from review_raster_fixtures import (
    debug_artifact_presenter,
    png_exporter,
    presented_reader_factory,
)


class _Mp4Controller(QObject):
    progress = Signal(object)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()
    runningChanged = Signal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.payload = None
        self.cancel_calls = 0
        self.close_calls = 0

    def start(self, **payload):
        self.payload = payload
        self.running = True
        self.runningChanged.emit(True)

    def cancel(self):
        self.cancel_calls += 1

    def close(self):
        self.close_calls += 1
        self.running = False
        self.runningChanged.emit(False)
        return True


class _BundleReader:
    def __init__(self, bundle):
        self.bundle = bundle
        self.sources = []

    def read(self, source):
        self.sources.append(Path(source))
        return self.bundle


class _VideoReader:
    instances = []

    def __init__(self, path):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, 320, 240, 10.0, 5.0, 50, "fake")
        self.closed = False
        self.__class__.instances.append(self)

    def read_at(self, timestamp):
        actual = min(4.9, max(0.0, float(timestamp)) + 0.01)
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[:, :, 1] = int(actual * 20) % 255
        return frame, int(actual * 10), actual

    def close(self):
        self.closed = True


def _bundle(tmp_path: Path, *, video_exists=True):
    root = tmp_path / "bundle"
    root.mkdir()
    video = tmp_path / "source.mp4"
    if video_exists:
        video.write_bytes(b"video")
    recipe = InspectionRecipe.empty(320, 240, "snapshot")
    first = InspectionRecipe.default_glass(320, 240, 1)
    second = InspectionRecipe.default_glass(320, 240, 2)
    first.geometry.zero_line_y = 140.0
    second.geometry.zero_line_y = 145.0
    recipe.glasses.extend([first, second])
    session = AnalysisSession(
        input_video_path=str(video),
        video_metadata=VideoMetadata(str(video), 320, 240, 10.0, 5.0, 50, "fake"),
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
    )
    samples = (
        ReviewTrackingSample("run", first.id, 10, 1.0, FillState.PARTIAL_VISIBLE, smoothed_oil_air_level_px_from_zero=10.0, overall_confidence=0.8, is_valid=True),
        ReviewTrackingSample("run", first.id, 20, 2.0, FillState.UNKNOWN_REVIEW, overall_confidence=0.2, is_valid=False, flags=("REVIEW_REQUIRED",)),
        ReviewTrackingSample("run", second.id, 10, 1.0, FillState.PARTIAL_VISIBLE, smoothed_oil_air_level_px_from_zero=5.0, overall_confidence=0.9, is_valid=True),
    )
    events = (ReviewEvent("run", first.id, EventType.FOAM_START, 2.0, 2.5, confidence=0.7),)
    return ReviewBundle(
        root=root,
        run_id="run",
        recipe=recipe,
        session=session,
        manifest={},
        source_video_path=str(video),
        source_video_candidates=(str(video),),
        source_metadata=session.video_metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        glasses=(ReviewGlass(first.id, first.name, ResultState.REVIEW_REQUIRED), ReviewGlass(second.id, second.name, ResultState.PASS)),
        samples=samples,
        events=events,
    )


def _window(bundle, mp4_controller=None):
    raw_factory = lambda path: _VideoReader(path)
    return ResultReviewWindow(
        bundle_reader=_BundleReader(bundle),
        source_resolver=SourceVideoResolver(raw_factory),
        playback_controller=ResultReviewController(presented_reader_factory(raw_factory)),
        png_exporter=png_exporter(),
        mp4_export_controller=mp4_controller,
        debug_artifact_presenter=debug_artifact_presenter(),
    )


def test_viewer_loads_bundle_video_navigation_and_details(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root) is True
    assert window.state == "영상 로드됨 · 일시정지"
    assert not window.current_source_image.isNull()
    assert not window.current_render_image.isNull()
    assert window.navigation.event_list.count() == 1
    assert window.navigation.review_list.count() == 1
    assert window.details.values["sample_time"].text() != "-"
    assert (window.canvas.source_image_size.width(), window.canvas.source_image_size.height()) == (320, 240)
    window.close()


def test_event_jump_pauses_and_uses_actual_decoded_timestamp(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    window.playback.play()
    window._jump_to(2.0)
    assert window.playback.is_playing is False
    assert window.current_time == 2.01
    window.close()


def test_glass_change_preserves_video_timestamp_and_rerenders(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    before_time = window.current_time
    before_image = window.current_render_image.copy()
    window.navigation.glass_combo.setCurrentIndex(1)
    assert window.current_time == before_time
    assert window.selected_glass_id == bundle.glasses[1].id
    assert window.navigation.event_list.count() == 0
    assert not window.current_render_image.isNull()
    assert window.current_render_image != before_image
    window.close()


def test_missing_video_keeps_bundle_and_event_information_available(qtbot, tmp_path):
    bundle = _bundle(tmp_path, video_exists=False)
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root) is True
    assert window.state == "bundle 준비됨 · 영상 없음"
    assert "분석 당시 경로" in window.video_path_label.text()
    assert window.navigation.event_list.count() == 1
    assert window.playback.reader is None
    assert window.current_source_image.isNull()
    assert window.current_render_image.isNull()
    window.close()


def test_close_releases_viewer_reader_and_qimage_state(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    active_reader = window.playback.reader
    window.close()
    assert active_reader.closed is True
    assert window.playback.reader is None
    assert window.current_source_image.isNull()
    assert window.current_render_image.isNull()


def test_mp4_export_action_follows_bundle_and_video_readiness(qtbot, tmp_path):
    controller = _Mp4Controller()
    bundle = _bundle(tmp_path)
    window = _window(bundle, controller)
    qtbot.addWidget(window)
    assert not window.export_mp4_action.isEnabled()
    assert window.load_bundle(bundle.root)
    assert window.export_mp4_action.isEnabled()
    window.close()
    assert controller.close_calls == 1

    missing_controller = _Mp4Controller()
    missing_root = tmp_path / "missing-case"
    missing_root.mkdir()
    missing = _bundle(missing_root, video_exists=False)
    missing_window = _window(missing, missing_controller)
    qtbot.addWidget(missing_window)
    assert missing_window.load_bundle(missing.root)
    assert not missing_window.export_mp4_action.isEnabled()
    missing_window.close()


def test_mp4_export_uses_selected_glass_snapshot_and_does_not_mutate_viewer_state(qtbot, tmp_path, monkeypatch):
    controller = _Mp4Controller()
    bundle = _bundle(tmp_path)
    window = _window(bundle, controller)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    destination = tmp_path / "shared.mp4"
    monkeypatch.setattr(QInputDialog, "getItem", lambda *args, **kwargs: ("일반 공유용", True))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(destination), "MP4 비디오 (*.mp4)"))
    before_time = window.current_time
    before_glass = window.selected_glass_id
    before_image = window.current_render_image.copy()
    window.export_annotated_mp4()
    assert controller.payload is not None
    assert controller.payload["bundle"] is bundle
    assert controller.payload["query"] is window.query
    assert controller.payload["glass_id"] == before_glass
    assert controller.payload["source_video_path"] == window.active_video_path
    assert controller.payload["destination"] == destination
    assert controller.payload["include_debug"] is False
    assert controller.payload["overwrite"] is False
    assert window.current_time == before_time
    assert window.selected_glass_id == before_glass
    assert window.current_render_image == before_image
    assert not window.export_mp4_action.isEnabled()
    window.close()


def test_mp4_debug_preset_and_terminal_signals_preserve_viewer_state(qtbot, tmp_path, monkeypatch):
    controller = _Mp4Controller()
    bundle = _bundle(tmp_path)
    window = _window(bundle, controller)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    window.debug_repository = object()
    seen_presets = []

    def choose_preset(_parent, _title, _label, items, *_args):
        seen_presets.extend(items)
        return "디버그 정보 포함", True

    monkeypatch.setattr(QInputDialog, "getItem", choose_preset)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *args, **kwargs: (str(tmp_path / "debug.mp4"), "MP4 비디오 (*.mp4)"))
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    before = (window.current_time, window.selected_glass_id, window.current_render_image.copy())
    window.export_annotated_mp4()
    assert seen_presets == ["일반 공유용", "디버그 정보 포함"]
    assert controller.payload["include_debug"] is True
    controller.running = False
    controller.runningChanged.emit(False)
    controller.completed.emit(SimpleNamespace(path=tmp_path / "debug.mp4"))
    assert (window.current_time, window.selected_glass_id, window.current_render_image) == before

    controller.failed.emit("simulated failure")
    controller.cancelled.emit()
    assert (window.current_time, window.selected_glass_id, window.current_render_image) == before
    window.debug_repository = None
    window.close()
