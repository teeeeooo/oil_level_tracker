from __future__ import annotations

from oil_tracker.adapters.vision.sequence_trajectory_resolver import (
    SequenceTrajectoryResolver,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from tests.fixtures.synthetic import glass_config


def _candidate(
    y: float,
    *,
    boundary: float = 0.55,
    artifact: float = 0.08,
    ambiguity: float = 0.20,
    broad: float = 0.55,
    static: float = 0.0,
    glare: float = 0.0,
    border: float = 0.0,
    source: str | None = None,
    selected: bool = False,
) -> BoundaryCandidate:
    return BoundaryCandidate(
        source=source or f"candidate-{y}",
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={
            "boundary_likelihood": boundary,
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "evidence_availability": 1.0,
            "visibility": 1.0,
            "broad_strength": broad,
            "narrow_peak_strength": boundary,
            "narrow_horizontal_coverage": 0.65,
            "broad_scale_consistency": 0.75,
            "polarity_confidence": 0.65,
            "static_prior_contribution": static,
        },
        penalties={
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "glare_conflict": glare,
            "border_penalty": border,
            "exclusion_conflict": 0.0,
        },
        feature_score=boundary,
        final_score=boundary,
        selected=selected,
    )


def _detection(
    index: int,
    *candidates: BoundaryCandidate,
    state: FillState = FillState.UNKNOWN_REVIEW,
    flags: tuple[str, ...] = (),
    ambiguity: float = 0.55,
    no_interface: float = 0.0,
    photometric: tuple[float, float, float] | None = None,
) -> PhaseDetection:
    debug_metrics = {
        "oil_ambiguity_score": ambiguity,
        "oil_no_interface_score": no_interface,
        "oil_no_interface_full_likelihood": (
            0.9 if state is FillState.FULL_NO_INTERFACE else 0.0
        ),
        "oil_no_interface_empty_likelihood": (
            0.9 if state is FillState.EMPTY_NO_INTERFACE else 0.0
        ),
        "proposed_state": state.value,
    }
    if photometric is not None:
        debug_metrics.update(
            {
                "effective_gray_mean": photometric[0],
                "effective_gray_std": photometric[1],
                "effective_gray_dynamic_range": photometric[2],
            }
        )
    return PhaseDetection(
        glass_id="glass-1",
        frame_index=index,
        time_sec=index * 0.5,
        fill_state=state,
        candidates=list(candidates),
        flags=list(flags),
        visibility_confidence=1.0,
        overall_confidence=0.2,
        debug_metrics=debug_metrics,
    )


def _oil_y(result) -> list[float | None]:
    return [item.raw_oil_air_level_y for item in result.detections]


def test_continuous_material_path_beats_disconnected_stronger_rows() -> None:
    detections = []
    for index, y in enumerate((150.0, 145.0, 140.0, 135.0, 130.0, 125.0)):
        detections.append(
            _detection(
                index,
                _candidate(y, boundary=0.48, broad=0.52, source="material"),
                _candidate(
                    (80.0, 190.0, 90.0, 205.0, 75.0, 215.0)[index],
                    boundary=0.72,
                    broad=0.62,
                    source="disconnected",
                ),
                ambiguity=0.20,
            )
        )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0, 145.0, 140.0, 135.0, 130.0, 125.0]
    assert all("SEQUENCE_RESOLVED_OIL" in item.flags for item in result.detections)


def test_stationary_material_supported_interface_is_not_a_static_hard_veto() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(132.0, boundary=0.78, broad=0.80, artifact=0.04),
            ambiguity=0.15,
        )
        for index in range(10)
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [132.0] * 10
    assert result.diagnostics.maximum_track_opposition < 0.30


def test_recurring_artifact_signature_is_opposed_without_forcing_a_number() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                190.0,
                boundary=0.43,
                broad=0.12,
                artifact=0.82,
                static=0.78,
                glare=0.35,
                source="fixed-glass-edge",
            ),
            ambiguity=0.80,
        )
        for index in range(12)
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert result.diagnostics.recurring_track_count == 1
    assert result.diagnostics.maximum_track_opposition > 0.0
    assert all(item.raw_oil_air_level_y is None for item in result.detections)


def test_confirmed_full_persists_then_releases_only_through_top_entry() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    detections = (
        _detection(0, ambiguity=0.9),
        _detection(1, ambiguity=0.9),
        _detection(2, _candidate(top + 5.0, boundary=0.72), ambiguity=0.2),
        _detection(3, _candidate(top + 15.0, boundary=0.72), ambiguity=0.2),
        _detection(4, _candidate(top + 27.0, boundary=0.72), ambiguity=0.2),
    )

    result = SequenceTrajectoryResolver().resolve(
        detections,
        glass,
        InitialObservationState.FULL_NO_INTERFACE,
    )

    assert [item.fill_state for item in result.detections[:2]] == [
        FillState.FULL_NO_INTERFACE,
        FillState.FULL_NO_INTERFACE,
    ]
    assert _oil_y(result)[:2] == [None, None]
    assert _oil_y(result)[2:] == [top + 5.0, top + 15.0, top + 27.0]
    assert result.detections[-1].fill_state is FillState.DRAINING_VISIBLE


def test_confirmed_empty_rejects_central_first_candidate_but_accepts_bottom_entry() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    bottom = ellipse.center_y + ellipse.radius_y
    central = ellipse.center_y
    detections = (
        _detection(0, _candidate(central, boundary=0.55), ambiguity=0.5),
        _detection(1, _candidate(bottom - 4.0, boundary=0.74), ambiguity=0.2),
        _detection(2, _candidate(bottom - 16.0, boundary=0.74), ambiguity=0.2),
        _detection(3, _candidate(bottom - 29.0, boundary=0.74), ambiguity=0.2),
    )

    result = SequenceTrajectoryResolver().resolve(
        detections,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.detections[0].fill_state is FillState.EMPTY_NO_INTERFACE
    assert result.detections[0].raw_oil_air_level_y is None
    assert _oil_y(result)[1:] == [bottom - 4.0, bottom - 16.0, bottom - 29.0]
    assert result.detections[-1].fill_state is FillState.FILLING_VISIBLE


def test_hard_unavailable_frame_stays_unknown_without_coordinate_carry() -> None:
    detections = (
        _detection(0, _candidate(150.0), ambiguity=0.1),
        _detection(
            1,
            _candidate(148.0),
            flags=("FOGGED_OR_GLARE",),
            ambiguity=0.1,
        ),
        _detection(2, _candidate(146.0), ambiguity=0.1),
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert result.detections[1].fill_state is FillState.UNKNOWN_REVIEW
    assert result.detections[1].raw_oil_air_level_y is None
    assert "SEQUENCE_UNAVAILABLE" in result.detections[1].flags


def test_black_frame_cannot_publish_a_false_no_interface_state() -> None:
    detection = _detection(
        0,
        state=FillState.FULL_NO_INTERFACE,
        no_interface=1.0,
        photometric=(0.0, 0.0, 0.0),
    )

    result = SequenceTrajectoryResolver().resolve((detection,), glass_config())

    assert result.detections[0].fill_state is FillState.UNKNOWN_REVIEW
    assert result.detections[0].raw_oil_air_level_y is None
    assert "SEQUENCE_UNAVAILABLE" in result.detections[0].flags


def test_unconfirmed_full_entry_requires_same_frame_no_interface_evidence() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    detections = (
        _detection(0, _candidate(top + 26.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(1, _candidate(top + 18.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(2, _candidate(top + 10.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(3, ambiguity=0.8),
        _detection(4, ambiguity=0.8),
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass)

    assert result.detections[-1].fill_state is FillState.UNKNOWN_REVIEW
    assert all(
        item.fill_state is not FillState.FULL_NO_INTERFACE
        for item in result.detections
    )


def test_supported_top_trajectory_can_enter_full_with_no_interface_evidence() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    detections = (
        _detection(0, _candidate(top + 26.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(1, _candidate(top + 18.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(2, _candidate(top + 10.0, boundary=0.72, selected=True), ambiguity=0.2),
        *(
            _detection(index, ambiguity=0.2, no_interface=0.45)
            for index in range(3, 9)
        ),
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass)

    assert result.detections[-1].fill_state is FillState.FULL_NO_INTERFACE
    assert result.detections[-1].raw_oil_air_level_y is None


def test_long_gap_between_qualified_anchor_clusters_stays_non_numeric() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                150.0 + index,
                boundary=0.62,
                selected=index in {0, 1, 2, 10, 11, 12},
            ),
            ambiguity=0.2,
        )
        for index in range(13)
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert all(value is not None for value in _oil_y(result)[:3])
    assert _oil_y(result)[3:10] == [None] * 7
    assert all(value is not None for value in _oil_y(result)[10:])


def test_short_edge_before_first_qualified_anchor_remains_observable() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                150.0 - index,
                boundary=0.62,
                selected=index in {2, 3, 4},
            ),
            ambiguity=0.2,
        )
        for index in range(6)
    )

    result = SequenceTrajectoryResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0, 149.0, 148.0, 147.0, 146.0, 145.0]


def test_foam_only_glare_rejection_does_not_erase_independent_oil_candidate() -> None:
    detection = _detection(
        0,
        _candidate(150.0),
        flags=("FOAM_GLARE_REJECTED",),
        ambiguity=0.1,
    )

    result = SequenceTrajectoryResolver().resolve((detection,), glass_config())

    assert result.detections[0].raw_oil_air_level_y == 150.0


def test_selected_coordinate_is_always_a_candidate_from_the_same_frame() -> None:
    detections = tuple(
        _detection(index, _candidate(100.0 + index), _candidate(180.0 - index))
        for index in range(5)
    )
    resolver = SequenceTrajectoryResolver()

    first = resolver.resolve(detections, glass_config())
    second = resolver.resolve(detections, glass_config())

    assert _oil_y(first) == _oil_y(second)
    for original, resolved in zip(detections, first.detections, strict=True):
        if resolved.raw_oil_air_level_y is None:
            continue
        assert resolved.raw_oil_air_level_y in {candidate.y for candidate in original.candidates}
        assert sum(candidate.selected for candidate in resolved.candidates) == 1
