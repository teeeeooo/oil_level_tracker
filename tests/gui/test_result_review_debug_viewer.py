from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PySide6.QtCore import Qt

from oil_tracker.adapters.storage.debug_case_exporter import DebugCaseExporter
from oil_tracker.adapters.vision.source_video_resolver import SourceVideoResolver
from oil_tracker.domain.debug_trace import DebugBundleIndex, DebugTraceRecord, DebugTraceSummary
from oil_tracker.domain.enums import FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.review import ReviewBundle, ReviewGlass, ReviewTrackingSample
from oil_tracker.domain.session import AnalysisSession, DebugTraceLevel, VideoMetadata
from oil_tracker.ui.controllers.result_review_controller import ResultReviewController
from oil_tracker.ui.result_review_window import ResultReviewWindow
from oil_tracker.ui.widgets.result_debug_panel import ResultDebugPanel
from review_raster_fixtures import (
    debug_artifact_presenter,
    png_exporter,
    presented_reader_factory,
)


class _Reader:
    def __init__(self, path):
        self.path = str(path)
        self.metadata = VideoMetadata(self.path, 320, 240, 10.0, 5.0, 50, "fake")
        self.closed = False

    def read_at(self, timestamp):
        actual = min(4.9, max(0.0, float(timestamp)) + 0.012)
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        frame[:, :, 1] = int(actual * 30) % 255
        return frame, int(actual * 10), actual

    def close(self):
        self.closed = True


class _BundleReader:
    def __init__(self, bundle):
        self.bundle = bundle

    def read(self, _source):
        return self.bundle


class _DebugRepository:
    def __init__(self, bundle):
        self.bundle = bundle
        glass_id = bundle.glasses[0].id
        self.summary = DebugTraceSummary(
            record_id="record-1",
            run_id=bundle.run_id,
            glass_id=glass_id,
            frame_index=20,
            timestamp_sec=2.0,
            capture_reasons=("low_confidence", "candidate_ambiguity"),
            confidence=0.42,
            fill_state="UNKNOWN_REVIEW",
            artifact_availability=("overlay", "normalized"),
            byte_offset=0,
            byte_length=100,
        )
        self.index = DebugBundleIndex(
            schema_version=1,
            run_id=bundle.run_id,
            trace_level="basic",
            trace_path="debug/debug_trace.jsonl",
            record_count=1,
            records=(self.summary,),
        )
        self.record = DebugTraceRecord(
            schema_version=1,
            record_id="record-1",
            run_id=bundle.run_id,
            glass_id=glass_id,
            glass_name=bundle.glasses[0].name,
            frame_index=20,
            timestamp_sec=2.0,
            capture_reasons=self.summary.capture_reasons,
            fill_state="UNKNOWN_REVIEW",
            confidence={"oil": 0.4, "foam": 0.2, "visibility": 0.5, "overall": 0.42},
            flags=("LOW_CONFIDENCE",),
            positions={"raw_oil_y": 115.0, "smoothed_oil_y": 118.0, "raw_foam_y": None, "smoothed_foam_y": None},
            state={"previous_state": "PARTIAL_VISIBLE", "proposed_state": "UNKNOWN_REVIEW", "glare_ratio": 0.2},
            candidates=(
                {
                    "rank": 1,
                    "kind": "oil_air",
                    "source": "sobel",
                    "canonical_y": 118.0,
                    "local_y": 38.0,
                    "features": {"edge_strength": 0.8, "new_dynamic_feature": 0.33},
                    "penalties": {"jump": 0.1, "new_dynamic_penalty": 0.02},
                    "feature_score": 0.8,
                    "total_penalty": 0.12,
                    "final_score": 0.68,
                    "selected": True,
                    "rejected": False,
                    "reject_reason": "",
                },
                {
                    "rank": 2,
                    "kind": "oil_air",
                    "source": "canny",
                    "canonical_y": 124.0,
                    "local_y": 44.0,
                    "features": {"edge_strength": 0.75},
                    "penalties": {},
                    "feature_score": 0.75,
                    "total_penalty": 0.1,
                    "final_score": 0.65,
                    "selected": False,
                    "rejected": True,
                    "reject_reason": "geometry",
                },
            ),
            images={"overlay": "unused", "normalized": "unused"},
        )
        self.record_load_count = 0
        self.image_load_count = 0
        self.closed = False

    @property
    def has_trace(self):
        return True

    def summaries(self, glass_id=None, reasons=None):
        values = (self.summary,) if not glass_id or glass_id == self.summary.glass_id else ()
        if reasons:
            values = tuple(value for value in values if set(reasons).intersection(value.capture_reasons))
        return values

    def nearest(self, glass_id, timestamp_sec, tolerance_sec):
        if glass_id == self.summary.glass_id and abs(timestamp_sec - self.summary.timestamp_sec) <= tolerance_sec:
            return self.summary
        return None

    def load_record(self, record_id):
        assert record_id == self.record.record_id
        self.record_load_count += 1
        return self.record

    def load_image(self, record, key):
        self.image_load_count += 1
        if key not in record.images:
            return None
        image = np.full((20, 30), 100, dtype=np.uint8)
        return np.dstack([image, image, image]) if key == "overlay" else image

    def close(self):
        self.closed = True


def _bundle(tmp_path: Path, *, trace: bool):
    root = tmp_path / ("trace-bundle" if trace else "legacy-bundle")
    root.mkdir()
    source = tmp_path / ("trace-source.mp4" if trace else "legacy-source.mp4")
    source.write_bytes(b"video")
    recipe = InspectionRecipe.empty(320, 240, "snapshot")
    glass = InspectionRecipe.default_glass(320, 240, 1)
    glass.geometry.zero_line_y = 140.0
    recipe.glasses.append(glass)
    session = AnalysisSession(
        input_video_path=str(source),
        video_metadata=VideoMetadata(str(source), 320, 240, 10.0, 5.0, 50, "fake"),
        analysis_start_sec=1.0,
        analysis_end_sec=4.0,
        compressor_start_sec=1.5,
        sampling_fps=2.0,
        debug_trace_level=DebugTraceLevel.BASIC if trace else DebugTraceLevel.NONE,
    )
    samples = (
        ReviewTrackingSample(
            "run", glass.id, 10, 1.0, FillState.PARTIAL_VISIBLE,
            smoothed_oil_air_level_px_from_zero=10.0,
            overall_confidence=0.9,
            is_valid=True,
        ),
        ReviewTrackingSample(
            "run", glass.id, 20, 2.0, FillState.UNKNOWN_REVIEW,
            overall_confidence=0.42,
            is_valid=False,
            flags=("LOW_CONFIDENCE",),
        ),
    )
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
        glasses=(ReviewGlass(glass.id, glass.name, ResultState.REVIEW_REQUIRED),),
        samples=samples,
        events=(),
        debug_trace_level="basic" if trace else "none",
        debug_index_path="debug/debug_index.json" if trace else "",
        debug_trace_path="debug/debug_trace.jsonl" if trace else "",
        debug_record_count=1 if trace else 0,
        review_index={
            "debug_trace_level": "basic" if trace else "none",
            "debug_index": "debug/debug_index.json" if trace else "",
            "debug_trace": "debug/debug_trace.jsonl" if trace else "",
            "debug_record_count": 1 if trace else 0,
        },
    )


def _window(bundle, repository_holder=None):
    holder = repository_holder if repository_holder is not None else []

    def factory(value):
        repository = _DebugRepository(value)
        holder.append(repository)
        return repository

    raw_factory = lambda path: _Reader(path)
    return ResultReviewWindow(
        bundle_reader=_BundleReader(bundle),
        source_resolver=SourceVideoResolver(raw_factory),
        playback_controller=ResultReviewController(presented_reader_factory(raw_factory)),
        debug_repository_factory=factory,
        debug_case_exporter=DebugCaseExporter(),
        png_exporter=png_exporter(),
        debug_artifact_presenter=debug_artifact_presenter(),
    )


def test_trace_less_bundle_disables_debug_mode_and_keeps_general_viewer(qtbot, tmp_path):
    bundle = _bundle(tmp_path, trace=False)
    window = _window(bundle)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    assert window.mode == "general"
    assert window.mode_combo.model().item(1).isEnabled() is False
    assert window.navigation.tabs.isTabEnabled(window.navigation.debug_tab_index) is False
    assert "디버그 기록이 없습니다" in window.mode_combo.toolTip()
    assert not window.current_source_image.isNull()
    assert not window.current_render_image.isNull()
    assert not hasattr(window.canvas, "_debug_record")
    window.close()


def test_debug_record_activation_pauses_seeks_and_lazy_loads_once(qtbot, tmp_path):
    holder = []
    bundle = _bundle(tmp_path, trace=True)
    window = _window(bundle, holder)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    repository = holder[0]
    assert repository.record_load_count == 0
    assert window.mode_combo.model().item(1).isEnabled()
    assert window.navigation.debug_count.text() == "1개"
    window.playback.play()
    window._debug_record_activated(repository.summary)
    assert window.playback.is_playing is False
    assert repository.record_load_count == 1
    assert window.mode == "debug"
    assert not window.navigation.tabs.isTabVisible(window.navigation.event_tab_index)
    assert not window.navigation.tabs.isTabVisible(window.navigation.review_tab_index)
    assert window.navigation.tabs.isTabVisible(window.navigation.debug_tab_index)
    assert "낮은 신뢰도" in window.navigation.debug_list.item(0).text()
    assert "confidence" not in window.navigation.debug_list.item(0).text()
    assert window.current_time == 2.012
    assert window.selected_debug_record.record_id == "record-1"
    assert "decoded 차이 +0.012초" in window.debug_details.summary.text()
    assert not window.current_render_image.isNull()
    assert len(window.graph.model.debug_markers) == 1
    assert window.graph.model.debug_markers[0].selected
    assert window.transport.slider._debug_points == [(2.0, True)]
    load_count = repository.record_load_count
    image, index, actual = window.playback.reader.read_at(2.02)
    window._frame_ready(image, index, actual)
    assert repository.record_load_count == load_count
    window.close()
    assert repository.closed


def test_switching_back_to_general_hides_candidate_layer_and_preserves_time(qtbot, tmp_path):
    holder = []
    bundle = _bundle(tmp_path, trace=True)
    window = _window(bundle, holder)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    window._debug_record_activated(holder[0].summary)
    timestamp = window.current_time
    glass_id = window.selected_glass_id
    debug_image = window.current_render_image.copy()
    window.mode_combo.setCurrentIndex(0)
    assert window.mode == "general"
    assert window.current_time == timestamp
    assert window.selected_glass_id == glass_id
    assert window.detail_stack.currentWidget() is window.details
    assert window.navigation.tabs.isTabVisible(window.navigation.event_tab_index)
    assert window.navigation.tabs.isTabVisible(window.navigation.review_tab_index)
    assert not window.navigation.tabs.isTabVisible(window.navigation.debug_tab_index)
    assert window.current_render_image != debug_image
    window.close()


def test_candidate_table_dynamic_details_and_highlight_rerenders_without_mutating_record(qtbot, tmp_path):
    holder = []
    bundle = _bundle(tmp_path, trace=True)
    window = _window(bundle, holder)
    qtbot.addWidget(window)
    window.load_bundle(bundle.root)
    repository = holder[0]
    window._debug_record_activated(repository.summary)
    panel = window.debug_details
    assert panel.candidates.rowCount() == 2
    assert panel.candidates.columnCount() == 5
    assert [panel.tabs.tabText(index) for index in range(panel.tabs.count())] == [
        "판정 요약",
        "후보 비교",
        "진단 이미지",
    ]
    assert "최종: 확인 필요" in panel.state_summary.toPlainText()
    assert "LOW_CONFIDENCE" not in panel.state_summary.toPlainText()
    assert panel.state_detail.isHidden()
    assert "new_dynamic_feature" in panel.candidate_detail.toPlainText()
    assert "source:" not in panel.candidate_detail.toPlainText()
    assert "canonical Y" not in panel.candidate_detail.toPlainText()
    record_before = repository.record
    normal = window.current_render_image.copy()
    panel.candidates.selectRow(1)
    assert window.highlighted_candidate == 1
    assert panel.candidates.currentRow() == 1
    assert "geometry" in panel.candidate_detail.toPlainText()
    assert panel.candidates.item(1, 4).text() == "탈락"
    panel.raw_toggle.setChecked(True)
    assert not panel.state_detail.isHidden()
    assert '"raw_oil_y"' in panel.state_detail.toPlainText()
    assert window.current_render_image != normal
    assert repository.record is record_before
    window.close()


def test_artifact_is_requested_lazily_and_presented_as_detached_qimage(qtbot, tmp_path):
    panel = ResultDebugPanel()
    qtbot.addWidget(panel)
    repository = _DebugRepository(_bundle(tmp_path, trace=True))
    requests = []
    panel.artifactRequested.connect(requests.append)
    panel.set_record(repository.record)
    assert requests
    image = debug_artifact_presenter().present(repository, repository.record, "normalized")
    panel.set_artifact("normalized", image)
    assert "lazy decode 완료" in panel.artifact_status.text()
    panel.set_artifact("foam_mask", None)
    assert "저장되지 않았습니다" in panel.image_label.text()


def test_bundle_internal_export_error_preserves_debug_viewer_state(qtbot, tmp_path, monkeypatch):
    import oil_tracker.ui.result_review_window as review_window_module

    holder = []
    bundle = _bundle(tmp_path, trace=True)
    window = _window(bundle, holder)
    qtbot.addWidget(window)
    assert window.load_bundle(bundle.root)
    repository = holder[0]
    window._debug_record_activated(repository.summary)

    before_bundle = {
        path.relative_to(bundle.root).as_posix(): ("directory", b"") if path.is_dir() else ("file", path.read_bytes())
        for path in sorted(bundle.root.rglob("*"), key=lambda value: value.relative_to(bundle.root).as_posix())
    }
    selected_summary = window.selected_debug_summary
    selected_record = window.selected_debug_record
    timestamp = window.current_time
    reader = window.playback.reader
    render_image = window.current_render_image.copy()
    record_load_count = repository.record_load_count
    messages = []

    monkeypatch.setattr(
        review_window_module,
        "QFileDialog",
        SimpleNamespace(getExistingDirectory=lambda *_args, **_kwargs: str(bundle.root)),
    )
    monkeypatch.setattr(
        review_window_module,
        "QMessageBox",
        SimpleNamespace(critical=lambda _parent, title, message: messages.append((title, message))),
    )

    window.export_debug_case()

    after_bundle = {
        path.relative_to(bundle.root).as_posix(): ("directory", b"") if path.is_dir() else ("file", path.read_bytes())
        for path in sorted(bundle.root.rglob("*"), key=lambda value: value.relative_to(bundle.root).as_posix())
    }
    assert messages
    assert messages[-1][0] == "디버그 재현 패키지 실패"
    assert "공식 결과 bundle 내부" in messages[-1][1]
    assert before_bundle == after_bundle
    assert not list(bundle.root.glob("debug_case_*"))
    assert not list(bundle.root.glob(".*.tmp-*"))
    assert window.selected_debug_summary is selected_summary
    assert window.selected_debug_record is selected_record
    assert window.current_time == timestamp
    assert window.mode == "debug"
    assert window.playback.reader is reader
    assert window.current_render_image == render_image
    assert window.debug_repository is repository
    assert repository.record_load_count == record_load_count
    window.close()
