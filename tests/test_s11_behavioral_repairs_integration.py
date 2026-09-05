from __future__ import annotations

import csv

import numpy as np

from oil_tracker.adapters.reporting.csv_exporter import CsvExporter
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.application.services.detection_processing import (
    tracking_sample_from_detection,
)
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import (
    BoundaryKind,
    FillState,
    InitialObservationState,
    ResultState,
)
from oil_tracker.domain.geometry import EllipseGeometry, GlassGeometry
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult
from tests.fixtures.synthetic import glass_config


def _base_control_glass():
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "base-cycle-control"
    glass.geometry.zero_line_y = 150.0
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _base_step_frame(y: int | None) -> np.ndarray:
    if y is None:
        return np.full((240, 320, 3), 70, dtype=np.uint8)
    frame = np.full((240, 320, 3), 110, dtype=np.uint8)
    frame[y:] = 80
    return frame


def test_initial_full_slow_drain_then_rapid_refill_closes_without_carry() -> None:
    glass = _base_control_glass()
    detector = OpenCvPhaseDetector()
    truth_y = (
        None,
        None,
        *range(65, 97, 2),
        80,
        65,
        None,
        None,
        None,
    )
    raw = tuple(
        detector.detect(
            _base_step_frame(y), glass, frame, frame * 0.5, debug=False
        )[0]
        for frame, y in enumerate(truth_y)
    )

    resolved = detector.resolve_sequence(
        raw,
        glass,
        InitialObservationState.FULL_NO_INTERFACE,
    ).detections
    refill_index = len(truth_y) - 4

    assert all(resolved[index].raw_oil_air_level_y is None for index in (0, 1))
    assert sum(item.raw_oil_air_level_y is not None for item in resolved[2:18]) >= 12
    assert resolved[refill_index - 1].raw_oil_air_level_y is None
    assert resolved[refill_index].raw_oil_air_level_y is not None
    assert abs(resolved[refill_index].raw_oil_air_level_y - 65.0) <= 4.0
    assert (
        resolved[refill_index].debug_metrics["sequence_material_phase_reason"]
        == "DRAIN_REFILL_CLOSURE_CONFIRMED"
    )
    assert all(
        item.raw_oil_air_level_y is None for item in resolved[refill_index + 1 :]
    )
    assert all(
        item.debug_metrics["sequence_material_phase"] == "filled_barrier"
        for item in resolved[refill_index:]
    )


_R20_SCALE_HEIGHT = 772.2137404580153


def _r20_scale_base_control_glass():
    glass = InspectionRecipe.default_glass(400, 1000)
    glass.id = "r20-scale-base-cycle-control"
    glass.geometry = GlassGeometry(
        EllipseGeometry(200.0, 500.0, 100.0, _R20_SCALE_HEIGHT / 2.0),
        zero_line_y=700.0,
        margin_ratio=0.06,
    )
    glass.initial_state = InitialObservationState.FULL_NO_INTERFACE
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _r20_scale_step_frame(y: int | None) -> np.ndarray:
    if y is None:
        return np.full((1000, 400, 3), 70, dtype=np.uint8)
    frame = np.full((1000, 400, 3), 110, dtype=np.uint8)
    frame[y:] = 80
    return frame


def test_r20_scale_rapid_refill_handoffs_to_fresh_confirmed_owner() -> None:
    glass = _r20_scale_base_control_glass()
    detector = OpenCvPhaseDetector()
    truth_y = (
        None,
        None,
        *range(200, 321, 10),
        250,
        220,
        190,
        160,
        130,
        None,
        None,
    )
    raw = tuple(
        detector.detect(
            _r20_scale_step_frame(y), glass, frame, frame * 0.5, debug=False
        )[0]
        for frame, y in enumerate(truth_y)
    )
    resolved = detector.resolve_sequence(
        raw,
        glass,
        InitialObservationState.FULL_NO_INTERFACE,
    ).detections

    closure_index = truth_y.index(160)
    prior_drain = resolved[truth_y.index(320)]
    closure = resolved[closure_index]
    assert prior_drain.raw_oil_air_level_y is not None
    assert closure.raw_oil_air_level_y is not None
    assert abs(float(closure.raw_oil_air_level_y) - 160.0) <= 4.0
    assert (
        closure.debug_metrics["sequence_material_phase_reason"]
        == "DRAIN_REFILL_HANDOFF_CONFIRMED"
    )
    selected_prior = next(c for c in prior_drain.candidates if c.selected)
    selected_closure = next(c for c in closure.candidates if c.selected)
    assert selected_prior.features["sequence_tracklet_id"] != (
        selected_closure.features["sequence_tracklet_id"]
    )
    assert closure.raw_oil_air_level_y == selected_closure.y
    assert all(
        item.raw_oil_air_level_y is None
        for item in resolved[closure_index + 1 :]
    )
    assert all(
        item.debug_metrics["sequence_material_phase"] == "filled_barrier"
        for item in resolved[closure_index:]
    )


def _accum_control_glass():
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "accum-cycle-control"
    glass.geometry.zero_line_y = 150.0
    glass.initial_state = InitialObservationState.EMPTY_NO_INTERFACE
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _accum_step_frame(y: int | None) -> np.ndarray:
    frame = np.full((240, 320, 3), 110, dtype=np.uint8)
    if y is not None:
        frame[y:] = 80
    return frame


def test_initial_empty_slow_fill_recovers_after_gap_without_backfill() -> None:
    glass = _accum_control_glass()
    detector = OpenCvPhaseDetector()
    truth_y = (
        None,
        None,
        175,
        170,
        165,
        160,
        None,
        150,
        145,
        140,
        135,
        130,
        125,
        120,
        115,
        110,
        105,
        100,
        95,
        90,
        85,
        80,
        75,
        70,
        65,
    )
    raw = tuple(
        detector.detect(
            _accum_step_frame(y), glass, frame, frame * 0.5, debug=False
        )[0]
        for frame, y in enumerate(truth_y)
    )
    resolved = detector.resolve_sequence(
        raw,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    ).detections

    assert resolved[6].raw_oil_air_level_y is None
    assert resolved[5].raw_oil_air_level_y is not None
    assert resolved[7].raw_oil_air_level_y is not None
    assert all(
        item.raw_oil_air_level_y is not None
        for index, item in enumerate(resolved)
        if truth_y[index] is not None
    )
    assert resolved[-1].debug_metrics["sequence_material_phase"] == "filled_barrier"
    assert all(
        item.raw_oil_air_level_y
        == next(candidate.y for candidate in item.candidates if candidate.selected)
        for item in resolved
        if item.raw_oil_air_level_y is not None
    )


def _oil_candidate(y: float) -> BoundaryCandidate:
    """Build a normal physical boundary proposal for the completed resolver."""

    return BoundaryCandidate(
        source="oil_hypothesis:synthetic_boundary",
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={
            "boundary_likelihood": 0.80,
            "artifact_likelihood": 0.05,
            "ambiguity_likelihood": 0.10,
            "broad_strength": 0.80,
            "narrow_peak_strength": 0.80,
            "narrow_horizontal_coverage": 0.80,
            "broad_scale_consistency": 0.80,
            "polarity_confidence": 0.80,
            "material_texture_conflict": 0.0,
            "sequence_eligible": 1.0,
        },
        penalties={"material_texture_conflict": 0.0},
        feature_score=0.80,
        final_score=0.80,
    )


def test_delayed_reacquisition_completed_sequence_preserves_candidate_csv_y(
    tmp_path,
) -> None:
    """Exercise real candidates through sequence, samples and CSV output."""

    # Three lower-entry observations establish an initial-EMPTY fill owner.
    # The first post-grace candidate track is a real, confirmed but
    # non-draining distractor: its net movement is downward overall while
    # directional agreement is only 0.50.  A later, separate ready track is
    # the only candidate allowed to seed the unchanged delayed chain.
    y_by_frame = {
        0: 180.0,
        1: 150.0,
        2: 120.0,
        9: 90.0,
        10: 80.0,
        11: 100.0,
        12: 90.0,
        13: 110.0,
        16: 60.0,
        17: 80.0,
        18: 100.0,
        19: 105.0,
    }
    glass = glass_config()
    detections = tuple(
        PhaseDetection(
            glass_id=glass.id,
            frame_index=frame,
            time_sec=frame * 0.5,
            fill_state=FillState.UNKNOWN_REVIEW,
            candidates=(
                [_oil_candidate(y_by_frame[frame])]
                if frame in y_by_frame
                else []
            ),
        )
        for frame in range(20)
    )

    resolved = OpenCvPhaseDetector().resolve_sequence(
        detections,
        glass,
        InitialObservationState.EMPTY_NO_INTERFACE,
    )
    assert all(
        resolved.detections[frame].raw_oil_air_level_y is None
        for frame in (9, 10, 11, 12, 13, 16, 17, 18)
    )
    distractor_diagnostics = resolved.detections[13].debug_metrics[
        "sequence_material_phase_diagnostics"
    ]
    assert distractor_diagnostics["ownerless_barrier_attempt_consumed"] is False
    assert distractor_diagnostics["ownerless_barrier_state"] == "available"
    assert distractor_diagnostics["delayed_reacquisition_seed_predicates"][0][
        "drain_direction_ready"
    ] is False
    assert (
        distractor_diagnostics["delayed_reacquisition_seed_predicates"][0][
            "first_failed_predicate"
        ]
        == "drain_directional_agreement"
    )
    ready_seed_diagnostics = resolved.detections[18].debug_metrics[
        "sequence_material_phase_diagnostics"
    ]
    assert ready_seed_diagnostics["ownerless_barrier_attempt_consumed"] is True
    assert ready_seed_diagnostics["delayed_reacquisition_seed_predicates"][0][
        "drain_direction_ready"
    ] is True
    assert (
        resolved.detections[19].raw_oil_air_level_y
        == y_by_frame[19]
    )
    assert (
        resolved.detections[19].debug_metrics["sequence_material_phase_reason"]
        == "PARTIAL_FILL_DRAIN_DELAYED_REACQUISITION_CONFIRMED"
    )

    numeric = tuple(
        detection
        for detection in resolved.detections
        if detection.raw_oil_air_level_y is not None
    )
    assert numeric
    assert all(
        len(
            [candidate for candidate in detection.candidates if candidate.selected]
        )
        == 1
        for detection in numeric
    )
    assert all(
        detection.raw_oil_air_level_y
        == next(
            candidate.y
            for candidate in detection.candidates
            if candidate.selected
        )
        for detection in numeric
    )

    samples = [
        tracking_sample_from_detection("synthetic-run", glass, detection)
        for detection in resolved.detections
    ]
    assert [sample.raw_oil_air_level_y for sample in samples] == [
        detection.raw_oil_air_level_y for detection in resolved.detections
    ]
    result = AnalysisResult(
        run_id="synthetic-run",
        overall_state=ResultState.REVIEW_REQUIRED,
        glass_results=[
            GlassAnalysisResult(
                glass_id=glass.id,
                glass_name=glass.name,
                result_state=ResultState.REVIEW_REQUIRED,
                samples=samples,
            )
        ],
        started_at="synthetic",
        completed_at="synthetic",
    )
    tracking_path = tmp_path / "tracking_data.csv"
    events_path = tmp_path / "events.csv"
    CsvExporter().export(result, tracking_path, events_path)

    with tracking_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len(samples)
    assert [
        None if not row["raw_oil_air_level_y"] else float(row["raw_oil_air_level_y"])
        for row in rows
    ] == [sample.raw_oil_air_level_y for sample in samples]
