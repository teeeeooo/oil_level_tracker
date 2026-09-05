from __future__ import annotations

from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilObservationResolverConfig,
    OilObservationResolver,
    _assert_publishable_path,
    _effective_track_opposition,
    _oil_confidence,
    _oil_emission,
)
from oil_tracker.adapters.vision.oil_interface_selector import (
    build_interface_layers,
)
from oil_tracker.adapters.vision.oil_candidate_authority import OilCandidateAuthority
from oil_tracker.adapters.vision.oil_phase_identity import OilPhaseIdentity
from oil_tracker.adapters.vision.oil_sequence_types import (
    OilCandidateRef,
    TrackletConfirmationProfile,
    TrackletLifecycle,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence
from dataclasses import replace

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.geometry import ArtifactTemplate
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


def _admitted_ref(
    candidate: BoundaryCandidate,
    *,
    candidate_offset: int,
    evidence: OilCandidateEvidence,
    row_hypothesis_id: str = "row-0",
) -> OilCandidateRef:
    return OilCandidateRef(
        frame_offset=0,
        candidate_offset=candidate_offset,
        candidate=candidate,
        evidence=evidence,
        local_quality=0.8,
        authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
        initial_authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
        post_track_authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
        cluster_support=1.0,
        trajectory_support=1.0,
        tracklet_id="track-0",
        row_hypothesis_id=row_hypothesis_id,
        tracklet_admitted=True,
    )


def _calibrated_candidate(
    y: float,
    *,
    source: str = "calibrated",
    motion: float = 0.82,
    motion_coverage: float = 0.88,
) -> BoundaryCandidate:
    candidate = _candidate(
        y,
        boundary=0.36,
        broad=0.38,
        artifact=0.08,
        ambiguity=0.32,
        registered_oil_motion=motion,
        registered_oil_motion_coverage=motion_coverage,
        source=source,
    )
    return replace(
        candidate,
        features={
            **candidate.features,
            "supplemental_path": 1.0,
            "calibrated_high_recall": 1.0,
        },
    )


def _foam_candidate(y: float) -> BoundaryCandidate:
    return BoundaryCandidate(
        source="foam_evidence",
        kind=BoundaryKind.FOAM_FRONT,
        y=y,
        features={"sequence_foam_eligible": 1.0},
        feature_score=0.9,
        final_score=0.9,
    )


def _material_candidate(
    y: float,
    *,
    material_texture_conflict: float = 0.78,
    terminal_support: float = 0.0,
) -> BoundaryCandidate:
    candidate = _candidate(
        y,
        boundary=0.82,
        broad=0.82,
        material_texture_conflict=material_texture_conflict,
        registered_oil_motion=0.90,
        registered_oil_motion_coverage=1.0,
        source="r6_material_path",
    )
    return replace(
        candidate,
        features={
            **candidate.features,
            "r6_material_path": 1.0,
            "material_path_sector_fraction": 1.0,
            "raw_material_row_support": 0.9,
            "material_texture_conflict": material_texture_conflict,
            "material_terminal_partition_support": terminal_support,
        },
    )


def _with_artifact_calibration():
    glass = glass_config()
    glass.geometry.artifact_templates.append(
        ArtifactTemplate(
            id="fixed-rim",
            kind="line",
            center_x=0.5,
            center_y=0.8,
            width=0.8,
            height=0.02,
        )
    )
    return glass


def test_motion_only_high_recall_is_never_numeric_without_calibration() -> None:
    detections = tuple(
        _detection(index, _calibrated_candidate(184.0 - 7.0 * index), ambiguity=0.25)
        for index in range(8)
    )

    result = OilObservationResolver().resolve(detections, glass_config())

    assert _oil_y(result) == [None] * 8


def test_motion_only_high_recall_is_not_authority_after_calibration() -> None:
    detections = tuple(
        _detection(index, _calibrated_candidate(184.0 - 7.0 * index), ambiguity=0.25)
        for index in range(8)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )

    assert _oil_y(result) == [None] * 8
    assert result.diagnostics.qualified_anchor_count == 0


def test_motion_keyframes_cannot_bridge_an_anchor_free_high_recall_path() -> None:
    detections = tuple(
        _detection(
            index,
            _calibrated_candidate(
                190.0 - 6.0 * index,
                motion=0.82 if index in {0, 9} else 0.24,
                motion_coverage=0.88 if index in {0, 9} else 0.12,
            ),
            ambiguity=0.25,
        )
        for index in range(10)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )

    assert _oil_y(result) == [None] * 10


def test_late_motion_keyframes_cannot_promote_a_long_prefix() -> None:
    detections = tuple(
        _detection(
            index,
            _calibrated_candidate(
                360.0 - 2.0 * index,
                motion=0.82 if index in {80, 88} else 0.04,
                motion_coverage=0.88 if index in {80, 88} else 0.0,
            ),
            ambiguity=0.25,
        )
        for index in range(100)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )
    assert _oil_y(result) == [None] * 100


def test_high_recall_static_or_competing_paths_remain_non_numeric() -> None:
    static = tuple(
        _detection(index, _calibrated_candidate(150.0), ambiguity=0.25)
        for index in range(8)
    )
    competing = tuple(
        _detection(
            index,
            _calibrated_candidate(184.0 - 7.0 * index, source="path-a"),
            _calibrated_candidate(112.0 + 7.0 * index, source="path-b"),
            ambiguity=0.25,
        )
        for index in range(8)
    )
    glass = _with_artifact_calibration()

    static_result = OilObservationResolver().resolve(static, glass)
    competing_result = OilObservationResolver().resolve(competing, glass)

    assert _oil_y(static_result) == [None] * 8
    assert _oil_y(competing_result) == [None] * 8


def test_initial_empty_bottom_motion_confirms_without_false_upper_anchor() -> None:
    upper = (90.0, 89.0, 88.0, 87.0, 86.0, 85.0)
    lower = (205.0, 190.0, 175.0, 160.0, 145.0, 130.0)
    detections = []
    for index, (upper_y, lower_y) in enumerate(zip(upper, lower, strict=True)):
        lower_candidate = _candidate(
            lower_y,
            boundary=0.46,
            broad=0.50,
            source="r6_material_path",
            registered_oil_motion=0.90,
            registered_oil_motion_coverage=0.80,
        )
        lower_candidate.features.update(
            {
                "r6_material_path": 1.0,
                "material_path_sector_fraction": 1.0,
            }
        )
        detections.append(
            _detection(
                index,
                _candidate(
                    upper_y,
                    boundary=0.82,
                    broad=0.82,
                    source="false-upper-anchor",
                ),
                lower_candidate,
                ambiguity=0.20,
            )
        )

    result = OilObservationResolver().resolve(
        detections,
        glass_config(),
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert _oil_y(result) == list(lower)
    for detection in result.detections:
        upper_candidate, lower_candidate = detection.candidates
        assert upper_candidate.features["sequence_final_authority_tier"] == float(
            OilCandidateAuthority.ANCHOR_ELIGIBLE
        )
        assert upper_candidate.features["sequence_tracklet_admitted"] == 1.0
        assert not upper_candidate.selected
        assert lower_candidate.features["sequence_final_authority_tier"] == float(
            OilCandidateAuthority.CONTINUATION_ELIGIBLE
        )
        assert lower_candidate.features["sequence_tracklet_admitted"] == 1.0
        assert (
            lower_candidate.features["sequence_tracklet_confirmation_profile"]
            == "motion_trajectory"
        )
        assert (
            upper_candidate.features["sequence_tracklet_id"]
            != lower_candidate.features["sequence_tracklet_id"]
        )


def test_initial_empty_stationary_lower_structure_remains_provisional() -> None:
    detections = []
    for index, y in enumerate((190.0, 191.0, 190.0, 191.0, 190.0, 191.0)):
        candidate = _candidate(
            y,
            boundary=0.46,
            broad=0.50,
            source="r6_material_path",
        )
        candidate.features.update(
            {
                "r6_material_path": 1.0,
                "material_path_sector_fraction": 1.0,
            }
        )
        detections.append(_detection(index, candidate, ambiguity=0.20))

    result = OilObservationResolver().resolve(
        detections,
        glass_config(),
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert _oil_y(result) == [None] * len(detections)
    assert result.diagnostics.confirmed_tracklet_count == 0
    assert all(
        detection.candidates[0].features["sequence_tracklet_failure_reason"]
        == "INSUFFICIENT_NET_PROGRESS"
        for detection in result.detections
    )


def test_high_recall_path_does_not_compete_with_qualified_path() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(150.0, boundary=0.78, broad=0.78, source="ordinary"),
            _calibrated_candidate(210.0 - 7.0 * index),
            ambiguity=0.20,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )

    assert _oil_y(result) == [150.0] * 8
    assert all(
        candidate.features.get("composition_lower_reserve", 0.0) == 0.0
        for detection in result.detections
        for candidate in detection.candidates
    )


def test_foam_material_identity_blocks_residue_and_reserves_lower_candidate() -> None:
    detections = tuple(
        _detection(
            index,
            *(
                (_foam_candidate(218.0),)
                if index == 0
                else ()
            ),
            _material_candidate(218.0 + min(index, 3)),
            _calibrated_candidate(
                450.0 + (index % 2),
                motion=0.05,
                motion_coverage=0.0,
            ),
            ambiguity=0.20,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )

    assert _oil_y(result) == [None] * 8
    assert result.diagnostics.foam_material_seeded_frame_count == 1
    assert result.diagnostics.foam_material_continued_frame_count == 7
    assert result.diagnostics.foam_material_opposed_candidate_count == 8
    assert all(
        any(
            candidate.features.get("sequence_authority_reason")
            == "foam_material_identity"
            for candidate in detection.candidates
            if candidate.source == "r6_material_path"
        )
        for detection in result.detections
    )
    assert all(
        any(
            candidate.features.get("composition_lower_reserve") == 1.0
            for candidate in detection.candidates
            if candidate.source == "calibrated"
        )
        for detection in result.detections
    )


def test_ordered_lower_interface_can_anchor_inside_broad_material_mask() -> None:
    detections = tuple(
        _detection(
            index,
            *((_foam_candidate(218.0),) if index == 0 else ()),
            _material_candidate(218.0 + min(index, 3)),
            _material_candidate(
                450.0 + (index % 2),
                material_texture_conflict=0.35,
                terminal_support=0.90,
            ),
            _calibrated_candidate(
                450.0 + (index % 2),
                motion=0.05,
                motion_coverage=0.0,
            ),
            ambiguity=0.20,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(
        detections,
        _with_artifact_calibration(),
    )

    assert all(y is not None and 449.0 <= y <= 452.0 for y in _oil_y(result))
    selected_identities = [
        next(
            candidate.features.get("sequence_phase_identity")
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.OIL_AIR and candidate.selected
        )
        for detection in result.detections
    ]
    assert "ordered_lower_interface" in selected_identities[:2]
    assert set(selected_identities).issubset(
        {"ordered_lower_interface", "continuation_only"}
    )


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
    assert all(
        item.debug_metrics["sequence_stage_best_path_kind"] == "oil"
        and item.debug_metrics["sequence_stage_continuation_bound_kind"] == "oil"
        and item.debug_metrics["sequence_stage_spike_suppressed_kind"] == "oil"
        and item.debug_metrics["sequence_stage_completed_fill_kind"] == "oil"
        for item in result.detections
    )


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


def test_clean_direct_interface_uses_soft_recurring_track_opposition() -> None:
    candidate = _candidate(132.0, boundary=0.78, broad=0.80, artifact=0.04)
    ref = OilCandidateRef(
        frame_offset=0,
        candidate_offset=0,
        candidate=candidate,
        evidence=OilCandidateEvidence.from_candidate(candidate),
        local_quality=0.8,
        authority=OilCandidateAuthority.ANCHOR_ELIGIBLE,
        phase_identity=OilPhaseIdentity.DIRECT_INTERFACE,
        track_opposition=0.80,
    )

    assert _effective_track_opposition(ref) == 0.20

    contradicted_candidate = replace(
        candidate,
        penalties={**candidate.penalties, "material_texture_conflict": 0.75},
    )
    contradicted = replace(
        ref,
        candidate=contradicted_candidate,
        evidence=OilCandidateEvidence.from_candidate(contradicted_candidate),
    )
    assert _effective_track_opposition(contradicted) == 0.80


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
    witness = result.detections[2].debug_metrics["sequence_decision_witness"]
    assert witness["schema_version"] == "r21-decision-witness-v1"
    assert witness["routes"]["direct"]["status"] == "EVALUATED"
    assert witness["selection"]["selected_candidate"]["y"] == top + 5.0
    selected_row = next(
        row for row in witness["rows"] if row["publishable"]
    )
    assert selected_row["phase_admitted"] is True
    assert any(member["selected"] for member in selected_row["members"])


def test_confirmed_empty_does_not_lock_out_a_sustained_late_visible_path() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    bottom = ellipse.center_y + ellipse.radius_y
    height = ellipse.radius_y * 2.0
    detections = (
        _detection(0, ambiguity=0.8),
        _detection(1, _candidate(bottom - height * 0.08, boundary=0.74, selected=True), ambiguity=0.2),
        _detection(2, _candidate(bottom - height * 0.12, boundary=0.74, selected=True), ambiguity=0.2),
        _detection(3, _candidate(bottom - height * 0.17, boundary=0.74, selected=True), ambiguity=0.2),
    )

    result = OilObservationResolver().resolve(
        detections,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert result.detections[0].fill_state is FillState.UNKNOWN_REVIEW
    assert result.detections[0].raw_oil_air_level_y is None
    assert _oil_y(result)[1:] == [
        bottom - height * 0.08,
        bottom - height * 0.12,
        bottom - height * 0.17,
    ]
    assert result.detections[-1].fill_state is FillState.FILLING_VISIBLE


def test_confirmed_empty_rejects_stationary_lower_component() -> None:
    glass = glass_config()
    bottom = glass.geometry.ellipse.center_y + glass.geometry.ellipse.radius_y
    detections = tuple(
        _detection(
            index,
            _candidate(bottom - 4.0 + index % 2, boundary=0.82, selected=True),
            ambiguity=0.15,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(
        detections,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    )

    assert _oil_y(result) == [None] * len(detections)


def test_registered_motion_extends_same_component_tail_beyond_old_horizon() -> None:
    detections = []
    for index in range(12):
        candidate = _candidate(
            180.0 + index,
            boundary=0.76 if index < 3 else 0.46,
            selected=index < 3,
            registered_oil_motion=0.85,
            registered_oil_motion_coverage=0.90,
            source="ordinary" if index < 3 else "r6_material_path",
        )
        if index >= 3:
            candidate.features.update(
                {"r6_material_path": 1.0, "material_path_sector_fraction": 1.0}
            )
        detections.append(_detection(index, candidate, ambiguity=0.15))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [180.0 + index for index in range(12)]


def test_registered_motion_tail_stops_at_first_coverage_break() -> None:
    detections = []
    for index in range(12):
        candidate = _candidate(
            180.0 + index,
            boundary=0.76 if index < 3 else 0.46,
            selected=index < 3,
            registered_oil_motion=0.85,
            registered_oil_motion_coverage=0.90 if index < 8 else 0.0,
            source="ordinary" if index < 3 else "r6_material_path",
        )
        if index >= 3:
            candidate.features.update(
                {"r6_material_path": 1.0, "material_path_sector_fraction": 1.0}
            )
        detections.append(_detection(index, candidate, ambiguity=0.15))

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result)[:8] == [180.0 + index for index in range(8)]
    assert _oil_y(result)[8:] == [None] * 4


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


def test_foam_front_proximity_is_comparative_not_an_oil_veto() -> None:
    with_alternative = tuple(
        _detection(
            index,
            _candidate(184.0 + index, boundary=0.84, broad=0.84),
            _candidate(150.0 + index, boundary=0.80, broad=0.80),
            BoundaryCandidate(
                source="foam_evidence",
                kind=BoundaryKind.FOAM_FRONT,
                y=182.0 + index,
                features={"sequence_foam_eligible": 1.0},
            ),
            ambiguity=0.10,
        )
        for index in range(5)
    )
    only_alias = tuple(
        _detection(
            index,
            _candidate(184.0 + index, boundary=0.84, broad=0.84),
            BoundaryCandidate(
                source="foam_evidence",
                kind=BoundaryKind.FOAM_FRONT,
                y=182.0 + index,
                features={"sequence_foam_eligible": 1.0},
            ),
            ambiguity=0.10,
        )
        for index in range(5)
    )

    alternative = OilObservationResolver().resolve(
        with_alternative,
        glass_config(),
    )
    alias_only = OilObservationResolver().resolve(only_alias, glass_config())

    assert _oil_y(alternative) == [150.0 + index for index in range(5)]
    assert _oil_y(alias_only) == [184.0 + index for index in range(5)]


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


def test_calibrated_artifacts_do_not_consume_actual_oil_top_k_capacity() -> None:
    detections = []
    for index in range(5):
        artifacts = []
        for offset in range(5):
            candidate = _candidate(
                60.0 + offset * 18.0,
                boundary=0.94 - offset * 0.01,
                broad=0.92,
            )
            candidate.features["calibrated_artifact_match"] = 0.95
            candidate.rejected = True
            candidate.reject_reason = f"calibrated_artifact:template-{offset}"
            artifacts.append(candidate)
        detections.append(
            _detection(
                index,
                *artifacts,
                _candidate(180.0 + index, boundary=0.82, broad=0.82),
                ambiguity=0.10,
            )
        )

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert _oil_y(result) == [180.0 + index for index in range(5)]
    assert result.diagnostics.ineligible_candidate_count == 25


def test_high_texture_conflict_blocks_ordinary_semantic_authority() -> None:
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

    assert _oil_y(resolver.resolve(conflicted, glass_config())) == [None] * 8
    assert _oil_y(resolver.resolve(neutral, glass_config())) == [132.0] * 8


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
    assert "R17_TRACKLET_WITNESS" in result.detections[0].flags
    assert "R17_TRACKLET_CONFIRMED" in result.detections[3].flags
    assert all(
        "R17_TRACKLET_CONTINUING" in item.flags
        for item in result.detections[4:6]
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


def test_short_duration_terminal_fallback_is_bounded_by_elapsed_time() -> None:
    detections = []
    for index in range(11):
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
        detections.append(
            replace(_detection(index, candidate, ambiguity=0.20), time_sec=index * 0.2)
        )

    result = OilObservationResolver().resolve(tuple(detections), glass_config())

    assert all(value is not None for value in _oil_y(result))


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


def test_completed_fill_blocks_contiguous_lower_material_cap_until_real_gap() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    top = ellipse.center_y - ellipse.radius_y
    height = ellipse.radius_y * 2.0
    rise = (0.58, 0.48, 0.38, 0.28, 0.22, 0.18)
    cap = (0.42, 0.44, 0.47, 0.45, 0.50, 0.48)
    detections = [
        _detection(
            index,
            _candidate(top + height * relative, boundary=0.78),
            ambiguity=0.15,
        )
        for index, relative in enumerate(rise + cap)
    ]

    result = OilObservationResolver().resolve(tuple(detections), glass)

    # The fill terminal remains an observed same-track row. The explicit
    # material phase barrier begins when the lower cap replaces that owner;
    # it does not move UNKNOWN backward through a global path.
    assert all(value is not None for value in _oil_y(result)[:6])
    assert _oil_y(result)[6:] == [None] * len(cap)


def test_completed_fill_material_owner_vetoes_confirmed_entrance_tracklet() -> None:
    glass = glass_config()
    ellipse = glass.geometry.ellipse
    top = ellipse.center_y - ellipse.radius_y
    height = ellipse.radius_y * 2.0
    detections = [
        _detection(
            index,
            _candidate(top + height * relative, boundary=0.78, broad=0.78),
            ambiguity=0.15,
        )
        for index, relative in enumerate((0.58, 0.48, 0.38, 0.28))
    ]
    entrance_y = top + height * 0.22
    detections.append(
        _detection(
            4,
            _material_candidate(
                entrance_y,
                material_texture_conflict=0.50,
            ),
            _candidate(
                entrance_y + 1.0,
                boundary=0.78,
                broad=0.78,
                source="independent-peer",
            ),
            ambiguity=0.15,
        )
    )

    result = OilObservationResolver().resolve(tuple(detections), glass)

    assert _oil_y(result) == [
        *(top + height * value for value in (0.58, 0.48, 0.38, 0.28)),
        None,
    ]
    final = result.detections[-1]
    assert final.debug_metrics["sequence_material_ownership_barrier"] == 1.0
    assert (
        final.debug_metrics["sequence_tracklet_failure_reason"]
        == "MATERIAL_OWNERSHIP_BARRIER"
    )
    assert all(
        candidate.features["sequence_tracklet_admitted"] == 1.0
        and candidate.features["sequence_material_ownership_barrier"] == 1.0
        and not candidate.selected
        for candidate in final.candidates
    )


def test_incompatible_oil_components_require_unknown_handoff() -> None:
    detections = tuple(
        _detection(
            index,
            _candidate(120.0 if index < 4 else 190.0, boundary=0.82),
            ambiguity=0.12,
        )
        for index in range(8)
    )

    result = OilObservationResolver().resolve(detections, glass_config())
    ys = _oil_y(result)

    assert 120.0 in ys
    assert 190.0 in ys
    assert any(value is None for value in ys[2:6])
    tracklet_ids = {
        detection.debug_metrics.get("sequence_selected_tracklet_id")
        for detection in result.detections
        if detection.raw_oil_air_level_y is not None
    }
    assert len(tracklet_ids) == 2


def test_completed_fill_barrier_releases_only_for_downward_drain_motion() -> None:
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
    drain = (0.38, 0.40, 0.44, 0.48, 0.53, 0.58)
    detections.extend(
        _detection(
            index,
            _candidate(top + height * relative, boundary=0.78),
            ambiguity=0.15,
        )
        for index, relative in enumerate(drain, start=len(detections))
    )

    result = OilObservationResolver().resolve(tuple(detections), glass)

    assert all(value is not None for value in _oil_y(result)[:6])
    assert _oil_y(result)[6:12] == [None] * 6
    assert all(value is not None for value in _oil_y(result)[12:])


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


def test_publishable_row_member_is_selected_before_fixed_lag_scoring() -> None:
    glass = glass_config()
    glass.detector_settings.minimum_final_confidence = 0.85
    high_emission = _candidate(150.0, source="high-emission-nonpublishable")
    publishable = _candidate(152.0, source="publishable-sibling")
    base_high = OilCandidateEvidence.from_candidate(high_emission)
    base_publishable = OilCandidateEvidence.from_candidate(publishable)
    high_ref = _admitted_ref(
        high_emission,
        candidate_offset=0,
        evidence=replace(
            base_high,
            material_support=0.20,
            registered_motion=1.0,
        ),
    )
    high_ref = replace(high_ref, semantic_corridor_support=0.50)
    publishable_ref = _admitted_ref(
        publishable,
        candidate_offset=1,
        evidence=replace(
            base_publishable,
            material_support=0.70,
            registered_motion=0.0,
        ),
    )

    assert _oil_emission(high_ref) > _oil_emission(publishable_ref)
    assert _oil_confidence(high_ref) < 0.85
    assert _oil_confidence(publishable_ref) >= 0.85

    detection = _detection(0, high_emission, publishable, ambiguity=0.15)
    _forward_phase, forward = build_interface_layers(
        detection,
        (high_ref, publishable_ref),
        hard_unavailable=False,
        minimum_confidence=0.85,
        state_min_evidence=OilObservationResolverConfig().state_min_evidence,
    )
    _reversed_phase, reversed_order = build_interface_layers(
        detection,
        (
            replace(publishable_ref, candidate_offset=0),
            replace(high_ref, candidate_offset=1),
        ),
        hard_unavailable=False,
        minimum_confidence=0.85,
        state_min_evidence=OilObservationResolverConfig().state_min_evidence,
    )

    forward_oil = tuple(node for node in forward if node.kind == "oil")
    reversed_oil = tuple(node for node in reversed_order if node.kind == "oil")
    assert len(forward_oil) == len(reversed_oil) == 1
    assert forward_oil[0].candidate_ref is publishable_ref
    assert reversed_oil[0].candidate_ref.candidate.source == "publishable-sibling"
    assert forward_oil[0].identity == reversed_oil[0].identity == "oil:row-0"
    assert _assert_publishable_path(forward_oil, 0.85) is forward_oil


def test_continuing_anchor_trajectory_can_publish_a_weak_measured_frame() -> None:
    glass = glass_config()
    glass.detector_settings.minimum_final_confidence = 0.85
    candidate = _candidate(
        152.0,
        boundary=0.30,
        broad=0.30,
        source="weak-current-anchor",
    )
    ref = replace(
        _admitted_ref(
            candidate,
            candidate_offset=0,
            evidence=OilCandidateEvidence.from_candidate(candidate),
        ),
        authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        initial_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        post_track_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        tracklet_lifecycle=TrackletLifecycle.CONTINUING,
        tracklet_confirmation_profile=(
            TrackletConfirmationProfile.ANCHOR_TRAJECTORY
        ),
    )
    assert _oil_confidence(ref) < 0.85

    _phase, publishable = build_interface_layers(
        _detection(0, candidate, ambiguity=0.15),
        (ref,),
        hard_unavailable=False,
        minimum_confidence=0.85,
        state_min_evidence=OilObservationResolverConfig().state_min_evidence,
    )

    oil = tuple(node for node in publishable if node.kind == "oil")
    assert len(oil) == 1
    assert oil[0].candidate_ref is ref
    assert _assert_publishable_path(oil, 0.85) is oil


def test_weak_anchor_witness_requires_continuing_noncontradicted_track() -> None:
    candidate = _candidate(
        152.0,
        boundary=0.30,
        broad=0.30,
        source="weak-current-anchor",
    )
    base = replace(
        _admitted_ref(
            candidate,
            candidate_offset=0,
            evidence=OilCandidateEvidence.from_candidate(candidate),
        ),
        authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        initial_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        post_track_authority=OilCandidateAuthority.CONTINUATION_ELIGIBLE,
        tracklet_confirmation_profile=(
            TrackletConfirmationProfile.ANCHOR_TRAJECTORY
        ),
    )
    contradicted_candidate = _candidate(
        152.0,
        boundary=0.30,
        broad=0.30,
        material_texture_conflict=0.80,
        source="contradicted-anchor",
    )
    contradicted = replace(
        base,
        candidate=contradicted_candidate,
        evidence=OilCandidateEvidence.from_candidate(contradicted_candidate),
        tracklet_lifecycle=TrackletLifecycle.CONTINUING,
    )
    confirmed_only = replace(
        base,
        tracklet_lifecycle=TrackletLifecycle.CONFIRMED,
    )

    for ref in (confirmed_only, contradicted):
        _phase, publishable = build_interface_layers(
            _detection(0, ref.candidate, ambiguity=0.15),
            (ref,),
            hard_unavailable=False,
            minimum_confidence=0.85,
            state_min_evidence=OilObservationResolverConfig().state_min_evidence,
        )
        assert not any(node.kind == "oil" for node in publishable)


def test_selector_output_is_prefix_invariant_after_its_fixed_lag_commit() -> None:
    lookahead = (
        OilObservationResolverConfig().tracklet_confirmation_window_frames
    )
    target = 8
    prefix = tuple(
        _detection(
            index,
            _candidate(
                170.0 - 2.0 * index,
                boundary=0.78,
                broad=0.78,
                source="prefix-owner",
            ),
            ambiguity=0.15,
        )
        for index in range(target + lookahead + 1)
    )
    suffix = tuple(
        _detection(
            index,
            _candidate(
                80.0 + 4.0 * (index - len(prefix)),
                boundary=0.95,
                broad=0.95,
                source="hostile-suffix",
            ),
            ambiguity=0.05,
        )
        for index in range(len(prefix), len(prefix) + 10)
    )

    committed = OilObservationResolver().resolve(
        prefix,
        glass_config(),
    ).detections[target]
    extended = OilObservationResolver().resolve(
        prefix + suffix,
        glass_config(),
    ).detections[target]

    assert committed.raw_oil_air_level_y == extended.raw_oil_air_level_y
    assert committed.fill_state is extended.fill_state
    for key in (
        "sequence_selected_tracklet_id",
        "sequence_material_phase",
        "sequence_material_phase_reason",
        "sequence_tracklet_failure_reason",
    ):
        assert committed.debug_metrics[key] == extended.debug_metrics[key]


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
        "R17_TRACKLET_CONTINUING" in result.detections[index].flags
        for index in range(3, 8)
    )
