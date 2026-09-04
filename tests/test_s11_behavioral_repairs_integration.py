from __future__ import annotations

import csv

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
from oil_tracker.domain.results import AnalysisResult, GlassAnalysisResult
from tests.fixtures.synthetic import glass_config


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
