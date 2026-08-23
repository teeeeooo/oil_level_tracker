from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from oil_tracker.adapters.storage.bundle_asset_resolver import BundleAssetResolver
from oil_tracker.adapters.vision.source_video_resolver import SourceVideoResolver
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewEvent, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.result_actions import ResultActionService
from oil_tracker.ui.result_review_window import ResultReviewWindow
from review_raster_fixtures import (
    debug_artifact_presenter,
    png_exporter,
    presented_reader_factory,
)


class _Reader:
    instances = []

    def __init__(self, path):
        self.path = str(path)
        name = Path(path).name
        width, height = (640, 480) if "wrong" in name else (320, 240)
        self.metadata = VideoMetadata(self.path, width, height, 10.0, 5.0, 50, "fake")
        self.fail_read = "decode-fail" in name
        self.closed = False
        self.__class__.instances.append(self)

    def read_at(self, timestamp):
        if self.fail_read:
            raise OSError("decode failed")
        actual = min(4.9, max(0.0, float(timestamp)) + 0.01)
        frame = np.zeros((self.metadata.height, self.metadata.width, 3), dtype=np.uint8)
        frame[:, :, 1] = int(actual * 20) % 255
        return frame, int(actual * 10), actual

    def close(self):
        self.closed = True


class _BundleReader:
    def __init__(self, bundle):
        self.bundle = bundle

    def read(self, _source):
        return self.bundle


def _bundle(tmp_path: Path, *, source_exists=True, capture=False):
    root = tmp_path / "bundle"
    root.mkdir()
    source = tmp_path / "source.mp4"
    if source_exists:
        source.write_bytes(b"video")
    recipe = InspectionRecipe.empty(320, 240, "snapshot")
    first = InspectionRecipe.default_glass(320, 240, 1)
    second = InspectionRecipe.default_glass(320, 240, 2)
    first.geometry.zero_line_y = 140.0
    second.geometry.zero_line_y = 145.0
    recipe.glasses.extend([first, second])
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=VideoMetadata(str(source), 320, 240, 10.0, 5.0, 50, "fake"),
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
    )
    samples = (
        ReviewTrackingSample(
            "run",
            first.id,
            10,
            1.0,
            FillState.PARTIAL_VISIBLE,
            smoothed_oil_air_level_px_from_zero=10.0,
            overall_confidence=0.8,
            is_valid=True,
        ),
        ReviewTrackingSample(
            "run",
            first.id,
            20,
            2.0,
            FillState.UNKNOWN_REVIEW,
            overall_confidence=0.2,
            is_valid=False,
            flags=("FOAM_REVIEW",),
        ),
        ReviewTrackingSample(
            "run",
            second.id,
            10,
            1.0,
            FillState.PARTIAL_VISIBLE,
            smoothed_oil_air_level_px_from_zero=5.0,
            overall_confidence=0.9,
            is_valid=True,
        ),
    )
    capture_path = "captures/event.png" if capture else ""
    events = (ReviewEvent("run", first.id, EventType.FOAM_START, 2.0, 2.5, confidence=0.7, capture_path=capture_path),)
    if capture:
        (root / "captures").mkdir()
        (root / capture_path).write_bytes(b"png")
        (root / "report.html").write_text("report", encoding="utf-8")
    return ReviewBundle(
        root=root,
        run_id="run",
        recipe=recipe,
        session=session,
        manifest={},
        source_video_path=str(source),
        source_video_candidates=(str(source),),
        source_metadata=session.video_metadata,
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        glasses=(
            ReviewGlass(first.id, first.name, ResultState.REVIEW_REQUIRED),
            ReviewGlass(second.id, second.name, ResultState.PASS),
        ),
        samples=samples,
        events=events,
    )


def _window(bundle, *, opener=None):
    raw_factory = lambda path: _Reader(path)
    return ResultReviewWindow(
        bundle_reader=_BundleReader(bundle),
        source_resolver=SourceVideoResolver(raw_factory),
        playback_controller=ResultReviewController(presented_reader_factory(raw_factory)),
        action_service=(
            ResultActionService(BundleAssetResolver(), opener=opener)
            if opener is not None
            else None
        ),
        png_exporter=png_exporter(),
        debug_artifact_presenter=debug_artifact_presenter(),
    )


def _state_snapshot(window):
    return {
        "reader": window.playback.reader,
        "path": window.video_path_label.text(),
        "source_image": window.current_source_image.copy(),
        "render_image": window.current_render_image.copy(),
        "frame_index": window.current_frame_index,
        "timestamp": window.current_time,
        "glass": window.selected_glass_id,
        "state": window.state,
        "save_enabled": window.save_png_action.isEnabled(),
        "detail": window.details.values["sample_time"].text(),
        "cursor": tuple(window.graph.cursor_artist.get_xdata()),
    }


def _assert_state_preserved(window, before):
    assert window.playback.reader is before["reader"]
    assert window.playback.reader.closed is False
    assert window.video_path_label.text() == before["path"]
    assert window.current_source_image == before["source_image"]
    assert window.current_render_image == before["render_image"]
    assert window.current_frame_index == before["frame_index"]
    assert window.current_time == before["timestamp"]
    assert window.selected_glass_id == before["glass"]
    assert window.state == before["state"]
    assert window.save_png_action.isEnabled() == before["save_enabled"]
    assert window.details.values["sample_time"].text() == before["detail"]
    assert tuple(window.graph.cursor_artist.get_xdata()) == before["cursor"]


def test_resolution_mismatch_replacement_preserves_complete_viewer_state(qtbot, tmp_path, monkeypatch):
    bundle = _bundle(tmp_path)
    wrong = tmp_path / "wrong.mp4"
    wrong.write_bytes(b"wrong")
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    before = _state_snapshot(window)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    assert window._open_resolved_video(wrong, window.current_time, auto=False) is False
    _assert_state_preserved(window, before)
    window.close()


def test_candidate_decode_failure_preserves_complete_viewer_state(qtbot, tmp_path, monkeypatch):
    bundle = _bundle(tmp_path)
    candidate = tmp_path / "decode-fail.mp4"
    candidate.write_bytes(b"bad")
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    before = _state_snapshot(window)
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    assert window._open_resolved_video(candidate, window.current_time, auto=False) is False
    _assert_state_preserved(window, before)
    assert any(reader.path.endswith("decode-fail.mp4") and reader.closed for reader in _Reader.instances)
    window.close()


def test_failed_candidate_from_missing_video_state_keeps_missing_state(qtbot, tmp_path, monkeypatch):
    bundle = _bundle(tmp_path, source_exists=False)
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    assert window.state == "bundle 준비됨 · 영상 없음"
    monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.StandardButton.Ok)
    assert window._open_resolved_video(tmp_path / "missing.mp4", 1.0, auto=False) is False
    assert window.state == "bundle 준비됨 · 영상 없음"
    assert window.playback.reader is None
    assert window.current_source_image.isNull()
    assert window.current_render_image.isNull()
    window.close()


def test_graph_click_pauses_seeks_and_uses_actual_decoded_timestamp(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    rebuilds = window.graph.series_rebuild_count
    window.playback.play()
    window._graph_clicked(2.0)
    assert window.playback.is_playing is False
    assert window.current_time == 2.01
    assert tuple(window.graph.cursor_artist.get_xdata()) == (2.01, 2.01)
    assert window.graph.series_rebuild_count == rebuilds
    window.close()


def test_review_filter_updates_count_highlights_and_preserves_events_and_glass_change(qtbot, tmp_path):
    bundle = _bundle(tmp_path)
    window = _window(bundle)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    assert window.navigation.event_list.count() == 1
    lost_index = window.navigation.filter_combo.findData("detection_lost")
    window.navigation.filter_combo.setCurrentIndex(lost_index)
    assert window.navigation.current_filter().value == "detection_lost"
    assert window.navigation.filter_count.text() == "0개"
    empty_flags = window.navigation.review_list.item(0).flags()
    assert not (empty_flags & Qt.ItemFlag.ItemIsEnabled)
    assert not (empty_flags & Qt.ItemFlag.ItemIsSelectable)
    assert len(window.graph.model.highlights) == 0
    assert window.navigation.event_list.count() == 1
    window.navigation.glass_combo.setCurrentIndex(1)
    assert window.navigation.current_filter().value == "detection_lost"
    window.close()


def test_report_folder_and_selected_capture_actions_do_not_pause_playback(qtbot, tmp_path):
    bundle = _bundle(tmp_path, capture=True)
    opened = []
    window = _window(bundle, opener=lambda url: opened.append(Path(url.toLocalFile())) or True)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    window.navigation.event_list.setCurrentRow(0)
    assert window.capture_action.isEnabled()
    window.playback.play()
    window.open_report()
    window.open_result_folder()
    window.open_event_capture()
    assert window.playback.is_playing is True
    assert opened == [
        (bundle.root / "report.html").resolve(),
        bundle.root.resolve(),
        (bundle.root / "captures/event.png").resolve(),
    ]
    window.close()
