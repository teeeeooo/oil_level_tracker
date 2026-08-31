from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import pytest

from oil_tracker.application.services.redetection_service import (
    _official_judgment_note,
    _tracking_for_event_and_judgment,
)
from oil_tracker.domain.enums import EventType, FillState
from oil_tracker.domain.redetection import RedetectionMode, RedetectionSample
from oil_tracker.domain.review import ReviewEvent
from oil_tracker.ui.widgets.redetection_debug_comparison import RedetectionDebugComparison
from redetection_fixtures import make_bundle
from test_redetection_service import (
    FakeDetector,
    FakeReader,
    _request,
    _reset_fakes,
    _service,
)


def test_current_frame_target_is_decoded_once_despite_static_learning(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(_request(bundle, RedetectionMode.CURRENT), bundle)
    try:
        reader = FakeReader.instances[-1]
        detector = FakeDetector.instances[-1]
        assert detector.detect_count == 1
        assert reader.reads.count(3.0) == 1
        assert len(reader.reads) == len(set(reader.reads)) == 3
    finally:
        output.workspace.cleanup()


def test_short_range_has_expected_detection_count_and_no_duplicate_decode(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(
        _request(
            bundle,
            RedetectionMode.SHORT,
            before_sec=0.5,
            after_sec=0.5,
        ),
        bundle,
    )
    try:
        reader = FakeReader.instances[-1]
        detector = FakeDetector.instances[-1]
        assert detector.detect_count == 6
        assert len(output.result.samples) == 3
        assert len(reader.reads) == len(set(reader.reads)) == 7
        assert reader.reads.count(3.0) == 1
    finally:
        output.workspace.cleanup()


def test_full_range_decode_count_matches_schedule_and_detector_calls(tmp_path):
    _reset_fakes()
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        reader = FakeReader.instances[-1]
        detector = FakeDetector.instances[-1]
        assert detector.detect_count == 9
        assert len(reader.reads) == len(set(reader.reads)) == 9
        assert len(reader.reads) == detector.detect_count
    finally:
        output.workspace.cleanup()


def test_failed_full_range_sample_reduces_valid_coverage(tmp_path):
    _reset_fakes()
    FakeDetector.fail_calls = {5}
    bundle = make_bundle(tmp_path, fps=2.0)
    output = _service().run(_request(bundle, RedetectionMode.FULL), bundle)
    try:
        assert output.result.rerun_valid_coverage_ratio == pytest.approx(8.0 / 9.0)
        failed = next(sample for sample in output.result.samples if not sample.succeeded)
        placeholder = _tracking_for_event_and_judgment(
            output.workspace.run_id,
            "glass-1",
            failed,
        )
        assert placeholder.fill_state is FillState.UNKNOWN_REVIEW
        assert not placeholder.is_valid
        assert "DETECTION_LOST" in placeholder.flags
    finally:
        output.workspace.cleanup()


def test_official_judgment_note_comes_from_latest_saved_judgment_event(tmp_path):
    bundle = make_bundle(tmp_path)
    events = (
        ReviewEvent(
            "official",
            "glass-1",
            EventType.JUDGMENT_PASS,
            4.0,
            note="first",
            input_order=1,
        ),
        ReviewEvent(
            "official",
            "glass-1",
            EventType.REVIEW_REQUIRED,
            5.0,
            note="saved official judgment note",
            input_order=2,
        ),
    )
    bundle = replace(bundle, events=events)
    assert _official_judgment_note(bundle.events, "glass-1") == "saved official judgment note"


def _record(prefix: str, selected_y: float, feature: float, penalty: float):
    return SimpleNamespace(
        glass_name=f"{prefix} Glass",
        glass_id="glass-1",
        timestamp_sec=3.0,
        frame_index=90,
        capture_reasons=("full_trace",),
        fill_state=FillState.PARTIAL_VISIBLE.value,
        confidence={"oil": 0.8, "foam": 0.6, "visibility": 0.9, "overall": 0.8},
        flags=(),
        positions={
            "raw_oil_y": selected_y,
            "smoothed_oil_y": selected_y,
            "raw_foam_y": None,
            "smoothed_foam_y": None,
        },
        state={},
        candidates=(
            {
                "rank": 1,
                "kind": "oil_air",
                "source": prefix,
                "canonical_y": selected_y,
                "local_y": selected_y,
                "features": {"edge_strength": feature},
                "penalties": {"glare": penalty},
                "feature_score": feature,
                "total_penalty": penalty,
                "final_score": feature - penalty,
                "selected": True,
                "rejected": False,
                "reject_reason": "",
            },
        ),
        images={"overlay": f"{prefix}/overlay.png", "canny": f"{prefix}/canny.png"},
        warnings=(),
    )


def test_candidate_comparison_shows_feature_penalty_and_position_delta(qtbot):
    widget = RedetectionDebugComparison(artifact_only=False)
    qtbot.addWidget(widget)
    widget.set_records(
        _record("official", 100.0, 0.7, 0.1),
        _record("rerun", 103.0, 0.8, 0.2),
    )
    assert widget.official.tabs.currentIndex() == 1
    assert widget.official.tabs.tabText(1) == "후보 비교"
    rows = {
        widget.delta_table.item(row, 0).text(): widget.delta_table.item(row, 3).text()
        for row in range(widget.delta_table.rowCount())
    }
    assert rows["canonical_y"] == "+3"
    assert rows["feature.edge_strength"] == "+0.1"
    assert rows["penalty.glare"] == "+0.1"


def test_artifact_comparison_synchronizes_same_artifact_key(qtbot):
    widget = RedetectionDebugComparison(artifact_only=True)
    qtbot.addWidget(widget)
    widget.set_records(
        _record("official", 100.0, 0.7, 0.1),
        _record("rerun", 103.0, 0.8, 0.2),
    )
    canny = widget.official.artifact_combo.findData("canny")
    widget.official.artifact_combo.setCurrentIndex(canny)
    assert widget.official.current_artifact_key() == "canny"
    assert widget.rerun.current_artifact_key() == "canny"
