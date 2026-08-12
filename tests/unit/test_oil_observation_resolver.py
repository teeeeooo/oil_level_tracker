from __future__ import annotations

from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilObservationResolver,
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
    material_texture_conflict: float = 0.0,
    registered_internal_motion: float = 0.0,
    registered_oil_motion: float = 0.0,
    registered_oil_motion_coverage: float = 0.0,
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
            "sequence_eligible": 1.0,
            "registered_motion_available": float(registered_internal_motion > 0.0),
            "registered_internal_motion_support": registered_internal_motion,
            "registered_dynamic_support": registered_internal_motion,
            "registered_oil_band_motion_support": registered_oil_motion,
            "registered_oil_band_motion_coverage": registered_oil_motion_coverage,
        },
        penalties={
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "glare_conflict": glare,
            "border_penalty": border,
            "exclusion_conflict": 0.0,
            "material_texture_conflict": material_texture_conflict,
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
                _candidate(
                    y,
                    boundary=0.48,
                    broad=0.52,
                    source="material",
                    selected=True,
                ),
                _candidate(
                    (80.0, 190.0, 90.0, 205.0, 75.0, 215.0)[index],
                    boundary=0.72,
                    broad=0.62,
                    source="disconnected",
                ),
                ambiguity=0.20,
            )
        )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0, 145.0, 140.0, 135.0, 130.0, 125.0]
    assert all("SEQUENCE_RESOLVED_OIL" in item.flags for item in result.detections)


def test_multiple_same_frame_candidates_do_not_fragment_anchor_track() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(128.0 + index, boundary=0.90, broad=0.90),
            _candidate(
                205.0 if index % 2 == 0 else 70.0,
                boundary=0.88,
                broad=0.88,
            ),
            ambiguity=0.18,
        )
        for index in range(7)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [128.0 + index for index in range(7)]


def test_weak_third_row_cannot_inherit_two_seed_anchor_authority() -> None:
    detections = (
        _detection(0, _candidate(150.0, boundary=0.82, broad=0.72), ambiguity=0.12),
        _detection(1, _candidate(140.0, boundary=0.82, broad=0.72), ambiguity=0.12),
        _detection(
            2,
            _candidate(
                150.0,
                boundary=0.30,
                broad=0.30,
                artifact=0.10,
                ambiguity=0.44,
            ),
            ambiguity=0.44,
        ),
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert result.diagnostics.qualified_anchor_count == 2
    assert "R7_OIL_ANCHOR" not in result.detections[2].flags


def test_stationary_material_supported_interface_is_not_a_static_hard_veto() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(132.0, boundary=0.78, broad=0.80, artifact=0.04),
            ambiguity=0.15,
        )
        for index in range(10)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

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

    result = OilObservationResolver().resolve(detections, glass_config())

    assert result.diagnostics.recurring_track_count == 1
    assert result.diagnostics.maximum_track_opposition > 0.0
    assert all(item.raw_oil_air_level_y is None for item in result.detections)


def test_confirmed_full_is_context_only_until_image_state_or_oil_evidence() -> None:
    glass = glass_config()
    top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    detections = (
        _detection(0, ambiguity=0.9),
        _detection(1, ambiguity=0.9),
        _detection(2, _candidate(top + 5.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(3, _candidate(top + 15.0, boundary=0.72, selected=True), ambiguity=0.2),
        _detection(4, _candidate(top + 27.0, boundary=0.72, selected=True), ambiguity=0.2),
    )

    result = OilObservationResolver().resolve(
        detections,
        glass,
        InitialObservationState.FULL_NO_INTERFACE,
    )

    assert [item.fill_state for item in result.detections[:2]] == [
        FillState.UNKNOWN_REVIEW,
        FillState.UNKNOWN_REVIEW,
    ]
    assert _oil_y(result)[:2] == [None, None]
    assert _oil_y(result)[2:] == [top + 5.0, top + 15.0, top + 27.0]
    assert result.detections[-1].fill_state is FillState.DRAINING_VISIBLE


def test_confirmed_empty_does_not_lock_out_a_sustained_late_visible_path() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    bottom = ellipse.center_y + ellipse.radius_y
    central = ellipse.center_y
    detections = (
        _detection(0, ambiguity=0.8),
        _detection(1, _candidate(central + 18.0, boundary=0.74, selected=True), ambiguity=0.2),
        _detection(2, _candidate(central + 5.0, boundary=0.74, selected=True), ambiguity=0.2),
        _detection(3, _candidate(central - 9.0, boundary=0.74, selected=True), ambiguity=0.2),
    )

    result = OilObservationResolver().resolve(
        detections,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.detections[0].fill_state is FillState.UNKNOWN_REVIEW
    assert result.detections[0].raw_oil_air_level_y is None
    assert _oil_y(result)[1:] == [central + 18.0, central + 5.0, central - 9.0]
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

    result = OilObservationResolver().resolve(detections, glass_config())

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

    result = OilObservationResolver().resolve((detection,), glass_config())

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

    result = OilObservationResolver().resolve(detections, glass)

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
            _detection(
                index,
                state=FillState.FULL_NO_INTERFACE,
                ambiguity=0.2,
                no_interface=0.75,
            )
            for index in range(3, 9)
        ),
    )

    result = OilObservationResolver().resolve(detections, glass)

    assert result.detections[-1].fill_state is FillState.FULL_NO_INTERFACE
    assert result.detections[-1].raw_oil_air_level_y is None


def test_continuous_same_frame_support_between_anchor_clusters_remains_numeric() -> None:
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

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0 + index for index in range(13)]
    assert all("SEQUENCE_SAME_FRAME_CANDIDATE" in item.flags for item in result.detections)


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

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0, 149.0, 148.0, 147.0, 146.0, 145.0]


def test_foam_only_glare_rejection_does_not_erase_independent_oil_candidate() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(150.0 + index, selected=True),
            flags=("FOAM_GLARE_REJECTED",),
            ambiguity=0.1,
        )
        for index in range(3)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [150.0, 151.0, 152.0]


def test_user_calibrated_artifact_is_ineligible_but_stays_in_trace() -> None:
    detections = []
    for index in range(4):
        candidate = _candidate(150.0, boundary=0.88, broad=0.88, selected=True)
        candidate.features["calibrated_artifact_match"] = 0.95
        candidate.rejected = True
        candidate.reject_reason = "calibrated_artifact:template-1"
        detections.append(_detection(index, candidate, ambiguity=0.10))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [None] * 4
    assert all(
        detection.candidates[0].reject_reason == "calibrated_artifact:template-1"
        for detection in result.detections
    )


def test_foam_material_texture_cannot_veto_independent_oil_authority() -> None:
    conflicted = tuple(
        _detection(
            index,
            _candidate(
                132.0,
                boundary=0.82,
                broad=0.82,
                material_texture_conflict=0.82,
                selected=True,
            ),
            ambiguity=0.20,
        )
        for index in range(8)
    )
    neutral = tuple(
        _detection(
            index,
            _candidate(
                132.0,
                boundary=0.82,
                broad=0.82,
                selected=True,
            ),
            ambiguity=0.20,
        )
        for index in range(8)
    )

    resolver = OilObservationResolver()

    assert _oil_y(resolver.resolve(conflicted, glass_config())) == _oil_y(
        resolver.resolve(neutral, glass_config())
    )


def test_foam_raster_motion_is_not_oil_motion_authority() -> None:
    static = tuple(
        _detection(
            index,
            _candidate(
                132.0,
                boundary=0.16,
                broad=0.16,
                material_texture_conflict=0.66,
                selected=True,
            ),
            ambiguity=0.20,
        )
        for index in range(6)
    )
    dynamic = tuple(
        _detection(
            index,
            _candidate(
                132.0 - index,
                boundary=0.16,
                broad=0.16,
                material_texture_conflict=0.66,
                registered_internal_motion=0.30,
                selected=True,
            ),
            ambiguity=0.20,
        )
        for index in range(6)
    )

    resolver = OilObservationResolver()

    assert _oil_y(resolver.resolve(static, glass_config())) == [None] * 6
    assert _oil_y(resolver.resolve(dynamic, glass_config())) == [None] * 6


def test_registered_oil_motion_extends_anchor_backed_material_continuation() -> None:
    detections = []
    for index in range(8):
        if index < 5:
            candidate = _candidate(
                170.0 - index * 4.0,
                boundary=0.46,
                broad=0.50,
                source="r6_material_path",
                registered_oil_motion=1.0,
                registered_oil_motion_coverage=1.0,
            )
            candidate.features.update(
                {
                    "r6_material_path": 1.0,
                    "material_path_sector_fraction": 1.0,
                }
            )
        else:
            candidate = _candidate(
                170.0 - index * 4.0,
                boundary=0.82,
                broad=0.82,
                selected=True,
            )
        detections.append(_detection(index, candidate, ambiguity=0.20))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [170.0 - index * 4.0 for index in range(8)]
    assert all(
        "R7_OIL_CONTINUATION" in item.flags
        for item in result.detections[:5]
    )


def test_terminal_material_fallback_requires_broad_cross_roi_support() -> None:
    candidates = []
    for index in range(6):
        candidate = _candidate(
            150.0,
            boundary=0.65,
            broad=0.82,
            source="r6_material_path",
        )
        candidate.features.update(
            {
                "r6_material_path": 1.0,
                "material_terminal_partition_support": 0.90,
                "material_path_sector_fraction": 0.60,
            }
        )
        candidates.append(_detection(index, candidate, ambiguity=0.20))

    result = OilObservationResolver().resolve(tuple(candidates), glass_config())

    assert _oil_y(result) == [None] * len(candidates)


def test_short_window_strong_terminal_material_path_can_use_three_sectors() -> None:
    detections = []
    for index in range(5):
        candidate = _candidate(
            150.0 + index,
            boundary=0.82,
            broad=0.82,
            source="r6_material_path",
        )
        candidate.features.update(
            {
                "r6_material_path": 1.0,
                "material_terminal_partition_support": 0.90,
                "material_path_sector_fraction": 0.60,
            }
        )
        detections.append(_detection(index, candidate, ambiguity=0.20))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [150.0 + index for index in range(5)]


def test_material_layer_terminal_cannot_become_long_window_oil_anchor() -> None:
    detections = []
    for index in range(8):
        candidate = _candidate(
            150.0,
            boundary=0.86,
            broad=0.86,
            source="r6_material_path",
        )
        candidate.features.update(
            {
                "r6_material_path": 1.0,
                "material_terminal_partition_support": 0.95,
                "material_path_sector_fraction": 1.0,
                "sequence_material_layer_topology": 1.0,
            }
        )
        detections.append(_detection(index, candidate, ambiguity=0.10))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [None] * len(detections)


def test_completed_fill_gap_blocks_upper_texture_reacquisition() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    top = ellipse.center_y - ellipse.radius_y
    height = ellipse.radius_y * 2.0
    rise = (0.58, 0.48, 0.38, 0.28, 0.22, 0.18)
    detections = [
        _detection(
            index,
            _candidate(top + height * relative, boundary=0.78),
            ambiguity=0.15,
        )
        for index, relative in enumerate(rise)
    ]
    detections.extend(
        _detection(index, ambiguity=0.85)
        for index in range(len(detections), len(detections) + 6)
    )
    detections.extend(
        _detection(
            index,
            _candidate(top + height * 0.20, boundary=0.78),
            ambiguity=0.15,
        )
        for index in range(len(detections), len(detections) + 3)
    )

    result = OilObservationResolver().resolve(tuple(detections), glass)

    assert all(value is not None for value in _oil_y(result)[:6])
    assert _oil_y(result)[6:] == [None] * 9


def test_selected_coordinate_is_always_a_candidate_from_the_same_frame() -> None:
    detections = tuple(
        _detection(index, _candidate(100.0 + index), _candidate(180.0 - index))
        for index in range(5)
    )
    resolver = OilObservationResolver()

    first = resolver.resolve(detections, glass_config())
    second = resolver.resolve(detections, glass_config())

    assert _oil_y(first) == _oil_y(second)
    for original, resolved in zip(detections, first.detections, strict=True):
        if resolved.raw_oil_air_level_y is None:
            continue
        assert resolved.raw_oil_air_level_y in {candidate.y for candidate in original.candidates}
        assert sum(candidate.selected for candidate in resolved.candidates) == 1


def test_weak_ambiguous_selected_shadow_cannot_start_oil() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                150.0,
                boundary=0.216,
                broad=0.10,
                artifact=0.216,
                ambiguity=0.605,
                selected=True,
            ),
            ambiguity=0.605,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [None] * len(detections)
    assert result.diagnostics.qualified_anchor_count == 0


def test_current_frame_selected_bit_cannot_change_r7_path() -> None:
    selected_first = tuple(
        _detection(
            index,
            _candidate(140.0 + index, boundary=0.72, selected=True),
            _candidate(205.0 - index * 3.0, boundary=0.68),
            ambiguity=0.20,
        )
        for index in range(6)
    )
    selected_second = tuple(
        _detection(
            index,
            _candidate(140.0 + index, boundary=0.72),
            _candidate(205.0 - index * 3.0, boundary=0.68, selected=True),
            ambiguity=0.20,
        )
        for index in range(6)
    )

    resolver = OilObservationResolver()

    assert _oil_y(resolver.resolve(selected_first, glass_config())) == _oil_y(
        resolver.resolve(selected_second, glass_config())
    )


def test_missing_candidate_remains_a_real_gap_between_anchor_clusters() -> None:
    detections = (
        *(
            _detection(index, _candidate(150.0 - index, boundary=0.72), ambiguity=0.2)
            for index in range(3)
        ),
        _detection(3, ambiguity=0.8),
        *(
            _detection(index, _candidate(146.0 - index, boundary=0.72), ambiguity=0.2)
            for index in range(4, 7)
        ),
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result)[3] is None
    assert all(value is not None for value in (*_oil_y(result)[:3], *_oil_y(result)[4:]))


def test_weaker_one_frame_partition_spike_is_censored_not_interpolated() -> None:
    detections = []
    for index in range(7):
        if index == 3:
            detections.append(
                _detection(
                    index,
                    _candidate(120.0, boundary=0.82, broad=0.72),
                    ambiguity=0.12,
                )
            )
            continue
        terminal = _candidate(
            150.0,
            boundary=0.86,
            broad=0.86,
            source="r6_material_path",
        )
        terminal.features.update(
            {
                "r6_material_path": 1.0,
                "material_terminal_partition_support": 0.92,
                "material_path_sector_fraction": 1.0,
            }
        )
        detections.append(
            _detection(
                index,
                terminal,
                _candidate(150.0, boundary=0.76, broad=0.68),
                ambiguity=0.12,
            )
        )

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result)[:3] == [150.0, 150.0, 150.0]
    assert _oil_y(result)[3] is None
    assert _oil_y(result)[4:] == [150.0, 150.0, 150.0]
    assert "SEQUENCE_SAME_FRAME_CANDIDATE" not in result.detections[3].flags


def test_weaker_partition_spike_is_censored_across_one_missing_frame() -> None:
    detections = []
    for index in range(9):
        if index == 3:
            detections.append(
                _detection(
                    index,
                    _candidate(120.0, boundary=0.82, broad=0.72),
                    ambiguity=0.12,
                )
            )
            continue
        if index == 4:
            detections.append(_detection(index, ambiguity=0.85))
            continue
        terminal = _candidate(
            150.0,
            boundary=0.86,
            broad=0.86,
            source="r6_material_path",
        )
        terminal.features.update(
            {
                "r6_material_path": 1.0,
                "material_terminal_partition_support": 0.92,
                "material_path_sector_fraction": 1.0,
            }
        )
        detections.append(
            _detection(
                index,
                terminal,
                _candidate(150.0, boundary=0.76, broad=0.68),
                ambiguity=0.12,
            )
        )

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result)[3:5] == [None, None]
    assert all(value == 150.0 for value in (*_oil_y(result)[:3], *_oil_y(result)[5:]))


def test_one_sided_continuation_decays_after_anchor_cluster() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                150.0 - index,
                boundary=0.72 if index < 3 else 0.24,
                broad=0.62 if index < 3 else 0.30,
                artifact=0.08 if index < 3 else 0.21,
                ambiguity=0.20 if index < 3 else 0.62,
            ),
            ambiguity=0.20 if index < 3 else 0.62,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert all(value is not None for value in _oil_y(result)[:5])
    assert _oil_y(result)[5:] == [None, None, None]


def test_continuation_between_anchor_clusters_can_publish_same_frame_rows() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(
                160.0 - index,
                boundary=0.72 if index < 3 or index >= 8 else 0.24,
                broad=0.62 if index < 3 or index >= 8 else 0.30,
                artifact=0.08 if index < 3 or index >= 8 else 0.21,
                ambiguity=0.20 if index < 3 or index >= 8 else 0.62,
            ),
            ambiguity=0.20 if index < 3 or index >= 8 else 0.62,
        )
        for index in range(11)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [160.0 - index for index in range(11)]
    assert all(
        "R7_OIL_CONTINUATION" in result.detections[index].flags
        for index in range(3, 8)
    )
