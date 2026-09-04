from __future__ import annotations

from oil_tracker.adapters.vision.foam_episode_resolver import (
    FoamEpisodeResolver,
    _foam_witness_windows,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from tests.fixtures.synthetic import glass_config


def _foam_candidate(
    y: float,
    *,
    score: float = 0.78,
    dynamic: float = 0.12,
    static: float = 0.05,
) -> BoundaryCandidate:
    return BoundaryCandidate(
        source="foam_evidence",
        kind=BoundaryKind.FOAM_FRONT,
        y=y,
        features={
            "foam_score": score,
            "bottom_connectivity": 1.0,
            "area_ratio": 0.08,
            "component_height_ratio": 0.25,
            "component_width_ratio": 0.70,
            "bounding_box_fill_ratio": 0.72,
            "whiteness_ratio": 0.55,
            "texture_support_ratio": 0.60,
            "glare_overlap_ratio": 0.02,
            "static_exact_overlap": static,
            "static_tolerant_overlap": static,
            "static_reciprocal_overlap": static,
            "registered_internal_motion_support": dynamic,
            "registered_dynamic_support": dynamic,
            "foam_layer_coherent": 1.0,
            "sequence_foam_eligible": 1.0,
        },
        feature_score=score,
        final_score=score,
    )


def _detection(
    index: int,
    candidate: BoundaryCandidate | None,
    *,
    state: FillState = FillState.PARTIAL_VISIBLE,
    coherent: bool = True,
) -> PhaseDetection:
    has_oil = state in {
        FillState.FILLING_VISIBLE,
        FillState.PARTIAL_VISIBLE,
        FillState.DRAINING_VISIBLE,
    }
    return PhaseDetection(
        glass_id="glass-1",
        frame_index=index,
        time_sec=index * 0.5,
        fill_state=state,
        raw_oil_air_level_y=(220.0 if has_oil else None),
        oil_air_level_y=(220.0 if has_oil else None),
        oil_air_level_px_from_zero=(10.0 if has_oil else None),
        overall_confidence=0.7,
        candidates=[] if candidate is None else [candidate],
        debug_metrics={"foam_layer_publication_coherent": coherent},
    )


def _selected_oil_candidate() -> BoundaryCandidate:
    return BoundaryCandidate(
        source="oil",
        kind=BoundaryKind.OIL_AIR,
        y=220.0,
        selected=True,
        final_score=0.8,
    )


def test_constant_high_score_static_appearance_is_not_a_foam_episode() -> None:
    detections = tuple(
        _detection(index, _foam_candidate(185.0, dynamic=0.0, static=0.86))
        for index in range(8)
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 0
    assert diagnostics.rejected_static_episode_count == 1
    assert all(item.raw_foam_front_y is None for item in resolved)
    assert all("R7_FOAM_STATIC_ARTIFACT_REJECTED" in item.flags for item in resolved)


def test_single_strong_component_does_not_start_foam() -> None:
    detections = (
        _detection(0, None),
        _detection(1, _foam_candidate(180.0, dynamic=0.9)),
        _detection(2, None),
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 0
    assert all(item.fill_state is FillState.PARTIAL_VISIBLE for item in resolved)
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_dynamic_coherent_episode_composes_after_oil_without_fabricating_gap() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.18)),
        _detection(1, _foam_candidate(184.0, dynamic=0.16)),
        _detection(2, None),
        _detection(3, _foam_candidate(175.0, dynamic=0.20)),
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 1
    assert diagnostics.confirmed_frame_count == 3
    assert resolved[2].fill_state is FillState.PARTIAL_VISIBLE
    assert resolved[2].raw_foam_front_y is None
    assert resolved[0].raw_foam_front_y == 190.0
    assert "R7_FOAM_EPISODE_CONFIRMED" in resolved[0].flags


def test_rapid_rising_foam_links_across_bounded_sample_gaps() -> None:
    rows = {0: 437.0, 2: 411.0, 5: 346.0, 8: 282.0, 11: 224.0, 12: 218.0}
    detections = tuple(
        _detection(
            index,
            None
            if index not in rows
            else _foam_candidate(rows[index], dynamic=0.30),
        )
        for index in range(13)
    )
    for detection in detections:
        detection.raw_oil_air_level_y = 550.0
        detection.oil_air_level_y = 550.0

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert diagnostics.confirmed_frame_count == len(rows)
    assert [
        resolved[index].raw_foam_front_y for index in sorted(rows)
    ] == list(rows.values())
    assert all(
        resolved[index].raw_foam_front_y is None
        for index in range(13)
        if index not in rows
    )


def test_dynamic_episode_does_not_backfill_a_static_prelude() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.0)),
        _detection(1, _foam_candidate(184.0, dynamic=0.18)),
        _detection(2, _foam_candidate(178.0, dynamic=0.16)),
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert diagnostics.confirmed_frame_count == 2
    assert resolved[0].fill_state is FillState.PARTIAL_VISIBLE
    assert resolved[0].raw_foam_front_y is None
    assert "R7_FOAM_UNCONFIRMED" in resolved[0].flags
    assert all(
        item.fill_state is FillState.FOAMING_VISIBLE
        for item in resolved[1:]
    )


def test_confirming_foam_preserves_independently_selected_oil_provenance() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.18)),
        _detection(1, _foam_candidate(184.0, dynamic=0.16)),
    )
    for detection in detections:
        oil = _selected_oil_candidate()
        detection.candidates.insert(0, oil)
        detection.raw_oil_air_level_y = oil.y
        detection.oil_air_level_y = oil.y

    resolved, _ = FoamEpisodeResolver().resolve(detections, glass_config())

    assert all(
        sum(candidate.selected for candidate in detection.candidates) == 2
        for detection in resolved
    )


def test_foam_composes_with_full_and_preserves_unknown_observation() -> None:
    full = (
        _detection(0, _foam_candidate(180.0, dynamic=0.2), state=FillState.FULL_NO_INTERFACE),
        _detection(1, _foam_candidate(174.0, dynamic=0.2), state=FillState.FULL_NO_INTERFACE),
    )
    unknown = (
        _detection(0, _foam_candidate(180.0, dynamic=0.2), state=FillState.UNKNOWN_REVIEW),
        _detection(1, _foam_candidate(174.0, dynamic=0.2), state=FillState.UNKNOWN_REVIEW),
    )
    resolver = FoamEpisodeResolver()

    full_result, _ = resolver.resolve(full, glass_config())
    unknown_result, _ = resolver.resolve(unknown, glass_config())

    assert all(item.fill_state is FillState.FULL_WITH_FOAM for item in full_result)
    assert all(item.fill_state is FillState.UNKNOWN_REVIEW for item in unknown_result)
    assert [item.raw_foam_front_y for item in unknown_result] == [180.0, 174.0]
    assert all(
        "R8_FOAM_WITHOUT_RESOLVED_OIL_STATE" in item.flags
        for item in unknown_result
    )
    assert all(
        "R8_FOAM_EVIDENCE_PRESERVED" in item.flags
        for item in unknown_result
    )


def test_foam_track_aliasing_oil_is_rejected_with_raw_candidate_preserved() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.20)),
        _detection(1, _foam_candidate(184.0, dynamic=0.20)),
    )
    for index, detection in enumerate(detections):
        oil = _selected_oil_candidate()
        oil.y = 188.0 - 6.0 * index
        detection.candidates.insert(0, oil)
        detection.raw_oil_air_level_y = oil.y
        detection.oil_air_level_y = oil.y

    resolved, _ = FoamEpisodeResolver().resolve(detections, glass_config())

    assert all(item.fill_state is FillState.PARTIAL_VISIBLE for item in resolved)
    assert [item.raw_oil_air_level_y for item in resolved] == [188.0, 182.0]
    assert [item.raw_foam_front_y for item in resolved] == [None, None]
    assert all(
        "R8_FOAM_OIL_ALIAS_REJECTED" in item.flags
        for item in resolved
    )
    assert all(
        any(candidate.kind is BoundaryKind.FOAM_FRONT for candidate in item.candidates)
        for item in resolved
    )


def test_prior_oil_alias_does_not_suppress_later_independent_foam() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.20)),
        _detection(1, _foam_candidate(189.0, dynamic=0.20)),
        _detection(2, None, state=FillState.UNKNOWN_REVIEW),
        _detection(3, None, state=FillState.UNKNOWN_REVIEW),
        _detection(
            4,
            _foam_candidate(188.0, dynamic=0.20),
            state=FillState.UNKNOWN_REVIEW,
        ),
        _detection(
            5,
            _foam_candidate(180.0, dynamic=0.20),
            state=FillState.UNKNOWN_REVIEW,
        ),
    )
    for index, detection in enumerate(detections[:2]):
        detection.raw_oil_air_level_y = 188.0 + index
        detection.oil_air_level_y = 188.0 + index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.rejected_oil_alias_episode_count == 1
    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved] == [
        None,
        None,
        None,
        None,
        188.0,
        180.0,
    ]
    assert all(
        "R8_FOAM_OIL_ALIAS_REJECTED" in resolved[index].flags
        for index in (0, 1)
    )


def test_separated_oil_and_foam_are_both_published() -> None:
    detections = (
        _detection(0, _foam_candidate(411.0, dynamic=0.20)),
        _detection(1, _foam_candidate(405.0, dynamic=0.20)),
    )
    for detection in detections:
        next(
            candidate
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.FOAM_FRONT
        ).features["material_component_bottom_y"] = 520.0
        detection.raw_oil_air_level_y = 448.0
        detection.oil_air_level_y = 448.0
        detection.candidates.insert(
            0,
            BoundaryCandidate(
                source="oil",
                kind=BoundaryKind.OIL_AIR,
                y=448.0,
                features={
                    "boundary_likelihood": 0.94,
                    "artifact_likelihood": 0.08,
                },
                selected=True,
                final_score=0.94,
            ),
        )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert diagnostics.rejected_oil_alias_episode_count == 0
    assert [item.raw_oil_air_level_y for item in resolved] == [448.0, 448.0]
    assert [item.raw_foam_front_y for item in resolved] == [411.0, 405.0]
    assert all(item.fill_state is FillState.FOAMING_VISIBLE for item in resolved)
    assert all(
        "R8_FOAM_OIL_TOPOLOGY_CONFLICT" not in item.flags
        for item in resolved
    )


def test_thin_dynamic_foam_layer_is_not_alias_under_large_oil_jump_setting() -> None:
    glass = glass_config()
    glass.detector_settings.temporal_max_jump_px = 64.0
    detections = (
        _detection(0, _foam_candidate(219.0, dynamic=0.20)),
        _detection(1, _foam_candidate(213.0, dynamic=0.20)),
    )
    for index, detection in enumerate(detections):
        oil_y = 236.0 - index * 6.0
        detection.raw_oil_air_level_y = oil_y
        detection.oil_air_level_y = oil_y
        detection.candidates.insert(
            0,
            BoundaryCandidate(
                source="selected-oil",
                kind=BoundaryKind.OIL_AIR,
                y=oil_y,
                selected=True,
                final_score=0.94,
            ),
        )
        detection.candidates.append(
            BoundaryCandidate(
                source="unselected-foam-twin",
                kind=BoundaryKind.OIL_AIR,
                y=219.0 - index * 6.0,
                features={
                    "boundary_likelihood": 0.96,
                    "artifact_likelihood": 0.02,
                },
                selected=False,
                final_score=0.96,
            )
        )

    resolved, diagnostics = FoamEpisodeResolver().resolve(detections, glass)

    assert diagnostics.rejected_oil_alias_episode_count == 0
    assert [item.raw_foam_front_y for item in resolved] == [219.0, 213.0]
    assert all("R10_FOAM_LAYER_SEPARATED" in item.flags for item in resolved)
    assert all(
        item.debug_metrics["foam_oil_identity_tolerance_px"] <= 8.0
        for item in resolved
    )


def test_inverted_public_oil_foam_topology_is_rejected_beyond_identity_tolerance() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.20)),
        _detection(1, _foam_candidate(184.0, dynamic=0.20)),
    )
    for index, detection in enumerate(detections):
        oil_y = 170.0 - index * 6.0
        detection.raw_oil_air_level_y = oil_y
        detection.oil_air_level_y = oil_y
        detection.candidates.insert(
            0,
            BoundaryCandidate(
                source="selected-inverted-oil",
                kind=BoundaryKind.OIL_AIR,
                y=oil_y,
                selected=True,
                final_score=0.94,
            ),
        )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.rejected_oil_alias_episode_count == 0
    assert [item.raw_foam_front_y for item in resolved] == [190.0, 184.0]
    assert all(
        "R8_FOAM_OIL_TOPOLOGY_CONFLICT" in item.flags
        and "R8_FOAM_OIL_ALIAS_REJECTED" not in item.flags
        and item.debug_metrics["foam_oil_relation"] == "inverted_topology"
        for item in resolved
    )


def test_unselected_oil_candidate_cannot_veto_dynamic_foam() -> None:
    detections = (
        _detection(
            0,
            _foam_candidate(190.0, dynamic=0.20),
            state=FillState.UNKNOWN_REVIEW,
        ),
        _detection(
            1,
            _foam_candidate(184.0, dynamic=0.20),
            state=FillState.UNKNOWN_REVIEW,
        ),
    )
    for index, detection in enumerate(detections):
        detection.candidates.insert(
            0,
            BoundaryCandidate(
                source="material_path",
                kind=BoundaryKind.OIL_AIR,
                y=188.0 - index * 4.0,
                features={
                    "boundary_likelihood": 0.94,
                    "artifact_likelihood": 0.08,
                },
                final_score=0.94,
            ),
        )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.rejected_oil_alias_episode_count == 0
    assert [item.raw_foam_front_y for item in resolved] == [190.0, 184.0]
    assert all(
        item.debug_metrics["foam_oil_relation"] == "no_resolved_oil"
        and "R8_FOAM_OIL_ALIAS_REJECTED" not in item.flags
        for item in resolved
    )


def test_one_registered_motion_spike_inside_static_glare_cannot_confirm_foam() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(
                185.0,
                dynamic=0.90 if index == 3 else 0.0,
                static=0.86,
            ),
        )
        for index in range(8)
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_dynamic_constant_glare_without_front_evolution_does_not_confirm() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(185.0, score=0.82, dynamic=1.0, static=0.0),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index in range(8)
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert diagnostics.rejected_unconfirmed_episode_count == 1
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_long_dynamic_prelude_cannot_borrow_distant_rise() -> None:
    """Formation authority is local to the four-frame/two-second suffix."""

    rows = [190.0] * 8 + [190.0, 184.0, 178.0, 172.0, 166.0]
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.30),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate(rows)
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved[:5]] == [
        None,
        None,
        None,
        None,
        None,
    ]
    assert [item.raw_foam_front_y for item in resolved[5:]] == rows[5:]
    windows = resolved[5].debug_metrics[
        "sequence_foam_episode_diagnostics"
    ]["segment_evaluations"]
    assert windows
    assert all(
        item["window_span_frame_offsets"] <= 4
        and item["window_span_seconds"] <= 2.0
        for item in windows
    )

    # Evidence appended beyond the local witness horizon cannot rewrite an
    # earlier confirmation or its selected same-frame coordinate.
    extended = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.30),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate(rows + [160.0, 154.0, 148.0, 142.0])
    )
    extended_resolved, _ = FoamEpisodeResolver().resolve(
        extended,
        glass_config(),
    )
    assert [
        item.raw_foam_front_y for item in extended_resolved[: len(rows)]
    ] == [item.raw_foam_front_y for item in resolved]


def test_witness_windows_scan_only_bounded_suffix_without_prefix_slices() -> None:
    """Every endpoint reads only its bounded suffix, never a full prefix copy."""

    from types import SimpleNamespace

    class NoSliceSegment:
        def __init__(self, items):
            self.items = tuple(items)
            self.index_reads = 0

        def __iter__(self):
            return iter(self.items)

        def __len__(self):
            return len(self.items)

        def __getitem__(self, index):
            if isinstance(index, slice):
                raise AssertionError("witness helper must not copy a prefix")
            self.index_reads += 1
            return self.items[index]

    segment = NoSliceSegment(
        SimpleNamespace(frame_offset=index, time_sec=index * 0.49)
        for index in range(1200)
    )

    windows = _foam_witness_windows(segment)

    assert len(windows) == len(segment)
    # Five members can be accepted, plus one indexed boundary probe that
    # discovers the sixth frame is outside the inclusive horizon.
    assert segment.index_reads == len(segment) * 6 - 15
    assert tuple(item.frame_offset for item in windows[-1]) == (
        1195,
        1196,
        1197,
        1198,
        1199,
    )
    assert all(
        window[-1].frame_offset - window[0].frame_offset <= 4
        for window in windows
    )
    assert all(
        window[-1].time_sec - window[0].time_sec <= 2.0
        for window in windows
    )


def test_stable_layer_needs_three_dynamic_rows_not_three_total_rows() -> None:
    """A static extent-changing tail cannot complete a stable-layer witness."""

    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.40 if index < 2 else 0.0),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((156.0, 158.0, 156.0))
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.12 + 0.20 * index
        candidate.features["component_width_ratio"] = 0.50 + 0.20 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolved)
    evaluations = resolved[0].debug_metrics[
        "sequence_foam_episode_diagnostics"
    ]["segment_evaluations"]
    assert evaluations
    assert all(
        item["formation"]["dynamic_observation_count"] == 2
        for item in evaluations
        if item["window_span_frame_offsets"] >= 1
    )
    assert evaluations[0]["window_span_frame_offsets"] == 2
    assert evaluations[0]["formation"]["predicates"][
        "stable_observation_support"
    ] is False


def test_downward_dynamic_residue_cannot_confirm_from_area_or_width_change() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.90, dynamic=0.80, static=0.0),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((410.0, 424.0, 441.0))
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.08 + 0.08 * index
        candidate.features["component_width_ratio"] = 0.55 + 0.15 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert diagnostics.rejected_unconfirmed_episode_count == 1
    assert all(item.raw_foam_front_y is None for item in resolved)
    segment = resolved[0].debug_metrics[
        "sequence_foam_episode_diagnostics"
    ]["segment_evaluations"][0]
    assert segment["predicates"]["formation_witness"] is False
    assert segment["formation"]["passed"] is False
    assert segment["formation"]["branch"] is None


def test_directional_foam_formation_tolerates_small_row_jitter() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.30),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((334.0, 321.0, 322.0, 306.0))
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved] == [
        334.0,
        321.0,
        322.0,
        306.0,
    ]
    episode = resolved[0].debug_metrics[
        "sequence_foam_episode_diagnostics"
    ]
    segment = episode["segment_evaluations"][0]
    assert episode["track_id"] == "foam-track:0000"
    assert episode["confirmed"] is True
    assert segment["passed"] is True
    assert segment["formation"]["branch"] == "directed_front"
    assert segment["formation"]["directional_agreement"] == 1.0


def test_stable_non_top_material_layer_confirms_with_extent_evolution() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.30),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((156.0, 158.0, 156.0))
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.08 + 0.04 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved] == [156.0, 158.0, 156.0]
    segment = resolved[0].debug_metrics[
        "sequence_foam_episode_diagnostics"
    ]["segment_evaluations"][0]
    assert segment["formation"]["branch"] == "stable_layer"
    assert segment["formation"]["predicates"] == {
        "stable_observation_support": True,
        "bounded_stable_front": True,
        "extent_evolution": True,
    }


def test_two_frame_stable_layer_requires_substantial_material_footprint() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.40),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((156.0, 158.0))
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.32 + 0.01 * index
        candidate.features["component_width_ratio"] = 0.68 + 0.10 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved] == [156.0, 158.0]


def test_two_frame_narrow_residue_cannot_use_stable_layer_path() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(y, score=0.86, dynamic=0.40),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index, y in enumerate((156.0, 158.0))
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.12 + 0.01 * index
        candidate.features["component_width_ratio"] = 0.68 + 0.10 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_stable_top_row_cannot_confirm_from_extent_evolution() -> None:
    detections = tuple(
        _detection(
            index,
            _foam_candidate(22.0, score=0.90, dynamic=0.80),
            state=FillState.UNKNOWN_REVIEW,
        )
        for index in range(3)
    )
    for index, detection in enumerate(detections):
        candidate = next(
            item
            for item in detection.candidates
            if item.kind is BoundaryKind.FOAM_FRONT
        )
        candidate.features["area_ratio"] = 0.08 + 0.05 * index
        candidate.features["component_width_ratio"] = 0.55 + 0.15 * index

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 0
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_time_adjacent_but_spatially_disconnected_foam_does_not_pool() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.30)),
        _detection(1, _foam_candidate(184.0, dynamic=0.30)),
        _detection(2, _foam_candidate(80.0, dynamic=0.30)),
        _detection(3, _foam_candidate(80.0, dynamic=0.30)),
    )

    resolved, diagnostics = FoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert [item.raw_foam_front_y for item in resolved] == [190.0, 184.0, None, None]
