from __future__ import annotations

from oil_tracker.application.services.report_presentation import (
    MAX_REPORT_LANDMARKS,
    build_glass_report_presentation,
    format_landmark_level,
)
from oil_tracker.domain.enums import EventType, FillState, ResultState
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import EventMarker, GlassAnalysisResult, TrackingSample


def _sample(
    glass_id: str,
    timestamp: float,
    *,
    oil: float | None = 0.0,
    foam: float | None = None,
    state: FillState = FillState.PARTIAL_VISIBLE,
    flags: tuple[str, ...] = (),
) -> TrackingSample:
    return TrackingSample(
        run_id="run",
        glass_id=glass_id,
        frame_index=int(timestamp * 10),
        timestamp_sec=timestamp,
        fill_state=state,
        smoothed_oil_air_level_px_from_zero=oil,
        smoothed_foam_front_px_from_zero=foam,
        overall_confidence=0.8,
        is_valid=oil is not None,
        flags=flags,
    )


def test_report_presentation_selects_extrema_and_consolidated_foam_without_debug_rows():
    config = InspectionRecipe.default_glass(320, 240, 1)
    values = {
        0.0: (8.0, None),
        0.5: (7.0, None),
        1.0: (None, 4.0),
        1.5: (None, 5.0),
        2.0: (None, None),
        2.5: (3.0, 6.0),
        3.0: (-4.0, 5.0),
        3.5: (1.0, None),
        4.0: (12.0, None),
        4.5: (11.0, 3.0),  # one-sample Foam flicker must not become an episode
        5.0: (10.0, None),
    }
    samples = [
        _sample(config.id, timestamp, oil=oil, foam=foam)
        for timestamp, (oil, foam) in values.items()
    ]
    events = [
        EventMarker("run", config.id, EventType.COMPRESSOR_START, 0.5),
        EventMarker("run", config.id, EventType.LOW_CONFIDENCE_START, 1.0),
        EventMarker("run", config.id, EventType.REVIEW_REQUIRED, 1.0),
    ]
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=samples,
        events=events,
    )

    report = build_glass_report_presentation(glass, config)
    types = [landmark.event_type for landmark in report.landmarks]

    assert EventType.MAXIMUM_OIL_LEVEL in types
    assert EventType.MINIMUM_OIL_LEVEL in types
    assert types.count(EventType.FOAM_START) == 1
    assert types.count(EventType.FOAM_END) == 1
    assert EventType.COMPRESSOR_START in types
    assert EventType.LOW_CONFIDENCE_START not in types
    assert EventType.REVIEW_REQUIRED not in types
    assert report.foam_episode_count == 1
    assert len(report.landmarks) <= MAX_REPORT_LANDMARKS
    assert "관측 최고" in report.movement_summary
    assert "상승과 하강이 모두 관측" in report.movement_summary
    assert "점선" in report.observation_note
    assert report.unavailable_intervals[0].display == "1.0–2.0초"
    assert "사용자 확인" in report.judgment_summary
    foam_start = next(
        landmark for landmark in report.landmarks if landmark.event_type is EventType.FOAM_START
    )
    foam_end = next(
        landmark for landmark in report.landmarks if landmark.event_type is EventType.FOAM_END
    )
    compressor = next(
        landmark
        for landmark in report.landmarks
        if landmark.event_type is EventType.COMPRESSOR_START
    )
    assert format_landmark_level(foam_start, config).startswith("거품 경계")
    assert format_landmark_level(foam_end, config) == "거품 경계가 더 이상 관측되지 않음"
    assert format_landmark_level(compressor, config) == "시험 기준 시점"


def test_all_missing_oil_does_not_claim_extrema_or_direction():
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, oil=None, state=FillState.UNKNOWN_REVIEW),
            _sample(config.id, 1.0, oil=None, state=FillState.UNKNOWN_REVIEW),
        ],
    )

    report = build_glass_report_presentation(glass, config)

    assert report.has_oil is False
    assert not {
        EventType.MAXIMUM_OIL_LEVEL,
        EventType.MINIMUM_OIL_LEVEL,
    }.intersection(landmark.event_type for landmark in report.landmarks)
    assert "확정할 수 없습니다" in report.movement_summary
    assert "유면 선을 표시하지 않습니다" in report.observation_note


def test_single_temporally_confirmed_foam_publication_remains_a_report_episode():
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, oil=None),
            _sample(
                config.id,
                0.5,
                oil=None,
                foam=4.0,
                flags=("FOAM_STRONG_EVIDENCE",),
            ),
            _sample(config.id, 1.0, oil=None),
        ],
    )

    report = build_glass_report_presentation(glass, config)

    assert report.foam_episode_count == 1
    foam = [
        landmark
        for landmark in report.landmarks
        if landmark.event_type in {EventType.FOAM_START, EventType.FOAM_END}
    ]
    assert [landmark.timestamp_sec for landmark in foam] == [0.5, 1.0]


def test_pending_foam_support_connects_but_does_not_backdate_or_end_episode():
    config = InspectionRecipe.default_glass(320, 240, 1)
    pending = ("FOAM_PERSISTENCE_PENDING",)
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, oil=None, flags=pending),
            _sample(
                config.id,
                0.5,
                oil=None,
                foam=4.0,
                flags=("FOAM_STRONG_EVIDENCE",),
            ),
            _sample(config.id, 1.0, oil=None),
            _sample(config.id, 1.5, oil=None, flags=pending),
            _sample(config.id, 2.0, oil=None),
            _sample(
                config.id,
                2.5,
                oil=None,
                foam=5.0,
                flags=("FOAM_STRONG_EVIDENCE",),
            ),
            _sample(config.id, 3.0, oil=None, flags=pending),
        ],
    )

    report = build_glass_report_presentation(glass, config)
    foam = [
        landmark
        for landmark in report.landmarks
        if landmark.event_type in {EventType.FOAM_START, EventType.FOAM_END}
    ]

    assert report.foam_episode_count == 1
    assert [(landmark.event_type, landmark.timestamp_sec) for landmark in foam] == [
        (EventType.FOAM_START, 0.5)
    ]


def test_short_missing_run_is_still_disclosed_as_a_graph_bridge():
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, oil=3.0),
            _sample(config.id, 0.5, oil=None, state=FillState.UNKNOWN_REVIEW),
            _sample(config.id, 1.0, oil=4.0),
        ],
    )

    report = build_glass_report_presentation(glass, config)

    assert report.unavailable_intervals == ()
    assert "짧은 직접 관측 공백" in report.observation_note
    assert "관측 가능한 지점" in report.movement_summary


def test_leading_or_trailing_missing_samples_are_not_described_as_bridges():
    config = InspectionRecipe.default_glass(320, 240, 1)
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=[
            _sample(config.id, 0.0, oil=None, state=FillState.UNKNOWN_REVIEW),
            _sample(config.id, 0.5, oil=3.0),
            _sample(config.id, 1.0, oil=4.0),
        ],
    )

    report = build_glass_report_presentation(glass, config)

    assert "점선" not in report.observation_note
    assert "첫 관측 전" in report.observation_note


def test_oil_drop_landmark_states_observed_onset_without_backdating_timestamp():
    config = InspectionRecipe.default_glass(320, 240, 1)
    samples = [
        _sample(config.id, 0.0, oil=10.0),
        _sample(config.id, 0.5, oil=None, state=FillState.UNKNOWN_REVIEW),
        _sample(config.id, 1.0, oil=4.0),
    ]
    glass = GlassAnalysisResult(
        config.id,
        config.name,
        ResultState.REVIEW_REQUIRED,
        samples=samples,
        events=[
            EventMarker(
                "run",
                config.id,
                EventType.OIL_DROP_START,
                1.0,
            )
        ],
    )

    report = build_glass_report_presentation(glass, config)
    landmark = next(
        item
        for item in report.landmarks
        if item.event_type is EventType.OIL_DROP_START
    )

    assert landmark.timestamp_sec == 1.0
    assert landmark.label == "유면 하강 최초 관찰"
    assert "실제 물리적 시작은 더 이를 수" in landmark.description
