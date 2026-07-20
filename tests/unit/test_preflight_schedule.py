from __future__ import annotations

import pytest

from oil_tracker.application.preflight import build_preflight_schedule
from oil_tracker.domain.session import VideoMetadata


def _metadata(*, fps: float = 10.0, duration: float = 100.0) -> VideoMetadata:
    return VideoMetadata(
        path="video.mp4",
        width=640,
        height=480,
        fps=fps,
        duration_sec=duration,
        frame_count=int(round(fps * duration)),
    )


def test_long_range_contains_start_compressor_quartiles_and_end_in_time_order():
    schedule = build_preflight_schedule(10.0, 90.0, _metadata(), 20.0)

    assert [point.label for point in schedule] == [
        "분석 시작",
        "압축기 기동 직후",
        "분석 구간 25%",
        "분석 구간 50%",
        "분석 구간 75%",
        "분석 종료 직전",
    ]
    assert [point.normalized_timestamp for point in schedule] == pytest.approx(
        [10.0, 20.1, 30.0, 50.0, 70.0, 89.9]
    )
    assert [point.frame_key for point in schedule] == sorted(point.frame_key for point in schedule)


def test_short_range_deduplicates_targets_that_resolve_to_the_same_frame_and_preserves_labels():
    schedule = build_preflight_schedule(
        1.0,
        1.04,
        _metadata(fps=25.0, duration=2.0),
        1.0,
    )

    assert len(schedule) == 1
    assert schedule[0].frame_key == 25
    assert schedule[0].labels == (
        "분석 시작",
        "압축기 기동 직후",
        "분석 구간 25%",
        "분석 구간 50%",
        "분석 구간 75%",
        "분석 종료 직전",
    )


def test_compressor_start_outside_range_is_excluded():
    before = build_preflight_schedule(10.0, 20.0, _metadata(duration=30.0), 9.9)
    after = build_preflight_schedule(10.0, 20.0, _metadata(duration=30.0), 20.1)

    assert all("압축기 기동 직후" not in point.labels for point in before)
    assert all("압축기 기동 직후" not in point.labels for point in after)


def test_compressor_target_merges_with_quartile_when_they_resolve_to_same_frame():
    schedule = build_preflight_schedule(
        0.0,
        1.0,
        _metadata(fps=10.0, duration=1.0),
        0.15,
    )

    merged = next(point for point in schedule if "압축기 기동 직후" in point.labels)
    assert "분석 구간 25%" in merged.labels
    assert merged.normalized_timestamp == pytest.approx(0.2)


def test_start_and_end_are_clamped_to_decodable_frames_when_end_equals_duration():
    schedule = build_preflight_schedule(
        0.03,
        2.0,
        _metadata(fps=10.0, duration=2.0),
        None,
    )

    assert schedule[0].normalized_timestamp >= 0.03
    assert schedule[-1].normalized_timestamp == pytest.approx(1.9)
    assert schedule[-1].frame_key == 19
    assert schedule[-1].normalized_timestamp < 2.0


def test_timestamps_with_different_meanings_but_same_frame_decode_once():
    schedule = build_preflight_schedule(
        0.0,
        0.2,
        _metadata(fps=5.0, duration=1.0),
        None,
    )

    assert len({point.frame_key for point in schedule}) == len(schedule)
    assert len(schedule) == 1
    assert len(schedule[0].labels) == 5


def test_invalid_range_or_missing_fps_is_rejected():
    with pytest.raises(ValueError, match="분석 구간"):
        build_preflight_schedule(1.0, 1.0, _metadata(), None)
    with pytest.raises(ValueError, match="FPS"):
        build_preflight_schedule(0.0, 1.0, _metadata(fps=0.0), None)
