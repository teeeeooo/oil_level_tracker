from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.sequence_foam_resolver import (
    FoamAdjacentEvidenceTracker,
    SequenceFoamEpisodeResolver,
    adjacent_evidence_features,
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
            "adjacent_dynamic_support": dynamic,
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
    return PhaseDetection(
        glass_id="glass-1",
        frame_index=index,
        time_sec=index * 0.5,
        fill_state=state,
        raw_oil_air_level_y=(140.0 if state is not FillState.UNKNOWN_REVIEW else None),
        oil_air_level_y=(140.0 if state is not FillState.UNKNOWN_REVIEW else None),
        oil_air_level_px_from_zero=(10.0 if state is not FillState.UNKNOWN_REVIEW else None),
        overall_confidence=0.7,
        candidates=[] if candidate is None else [candidate],
        debug_metrics={"foam_layer_publication_coherent": coherent},
    )


def _selected_oil_candidate() -> BoundaryCandidate:
    return BoundaryCandidate(
        source="oil",
        kind=BoundaryKind.OIL_AIR,
        y=140.0,
        selected=True,
        final_score=0.8,
    )


def test_adjacent_tracker_distinguishes_stable_mask_from_turnover() -> None:
    tracker = FoamAdjacentEvidenceTracker()
    first = np.zeros((30, 30), dtype=np.uint8)
    first[18:26, 7:22] = 255
    shifted = np.zeros_like(first)
    shifted[13:23, 4:25] = 255

    assert not tracker.evaluate("g", first, 18.0).available
    stable = tracker.evaluate("g", first.copy(), 18.0)
    changed = tracker.evaluate("g", shifted, 13.0)

    assert stable.available
    assert stable.dynamic_support == 0.0
    assert changed.dynamic_support > 0.20
    assert adjacent_evidence_features(changed)["adjacent_mask_turnover"] > 0.0


def test_constant_high_score_static_appearance_is_not_a_foam_episode() -> None:
    detections = tuple(
        _detection(index, _foam_candidate(185.0, dynamic=0.0, static=0.86))
        for index in range(8)
    )

    resolved, diagnostics = SequenceFoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 0
    assert diagnostics.rejected_static_episode_count == 1
    assert all(item.raw_foam_front_y is None for item in resolved)
    assert all("FOAM_SEQUENCE_STATIC_ARTIFACT_REJECTED" in item.flags for item in resolved)


def test_single_strong_component_does_not_start_foam() -> None:
    detections = (
        _detection(0, None),
        _detection(1, _foam_candidate(180.0, dynamic=0.9)),
        _detection(2, None),
    )

    resolved, diagnostics = SequenceFoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 0
    assert all(item.fill_state is FillState.PARTIAL_VISIBLE for item in resolved)
    assert all(item.raw_foam_front_y is None for item in resolved)


def test_dynamic_coherent_episode_composes_after_oil_and_bridges_one_gap() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.18)),
        _detection(1, _foam_candidate(184.0, dynamic=0.16)),
        _detection(2, None),
        _detection(3, _foam_candidate(175.0, dynamic=0.20)),
    )

    resolved, diagnostics = SequenceFoamEpisodeResolver().resolve(detections, glass_config())

    assert diagnostics.episode_count == 1
    assert diagnostics.confirmed_frame_count == 3
    assert diagnostics.bridged_frame_count == 1
    assert all(item.fill_state is FillState.FOAMING_VISIBLE for item in resolved)
    assert resolved[2].raw_foam_front_y is None
    assert "FOAM_SEQUENCE_EPISODE_GAP" in resolved[2].flags
    assert resolved[0].raw_foam_front_y == 190.0
    assert "FOAM_SEQUENCE_CONFIRMED" in resolved[0].flags


def test_dynamic_episode_does_not_backfill_a_static_prelude() -> None:
    detections = (
        _detection(0, _foam_candidate(190.0, dynamic=0.0)),
        _detection(1, _foam_candidate(184.0, dynamic=0.18)),
        _detection(2, _foam_candidate(178.0, dynamic=0.16)),
    )

    resolved, diagnostics = SequenceFoamEpisodeResolver().resolve(
        detections,
        glass_config(),
    )

    assert diagnostics.episode_count == 1
    assert diagnostics.confirmed_frame_count == 2
    assert resolved[0].fill_state is FillState.PARTIAL_VISIBLE
    assert resolved[0].raw_foam_front_y is None
    assert "FOAM_SEQUENCE_UNCONFIRMED" in resolved[0].flags
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
        detection.candidates.insert(0, _selected_oil_candidate())

    resolved, _ = SequenceFoamEpisodeResolver().resolve(detections, glass_config())

    assert all(
        sum(candidate.selected for candidate in detection.candidates) == 2
        for detection in resolved
    )


def test_foam_composes_with_full_but_cannot_promote_unknown() -> None:
    full = (
        _detection(0, _foam_candidate(180.0, dynamic=0.2), state=FillState.FULL_NO_INTERFACE),
        _detection(1, _foam_candidate(174.0, dynamic=0.2), state=FillState.FULL_NO_INTERFACE),
    )
    unknown = (
        _detection(0, _foam_candidate(180.0, dynamic=0.2), state=FillState.UNKNOWN_REVIEW),
        _detection(1, _foam_candidate(174.0, dynamic=0.2), state=FillState.UNKNOWN_REVIEW),
    )
    resolver = SequenceFoamEpisodeResolver()

    full_result, _ = resolver.resolve(full, glass_config())
    unknown_result, _ = resolver.resolve(unknown, glass_config())

    assert all(item.fill_state is FillState.FULL_WITH_FOAM for item in full_result)
    assert all(item.fill_state is FillState.UNKNOWN_REVIEW for item in unknown_result)
    assert all(item.raw_foam_front_y is None for item in unknown_result)
