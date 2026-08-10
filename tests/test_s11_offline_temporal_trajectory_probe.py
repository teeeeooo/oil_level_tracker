from __future__ import annotations

from tests.diagnostics.s11_offline_temporal_trajectory_probe import (
    TrajectoryObservation,
    TruthBaseline,
    build_manifest,
    estimate_held_out,
    run_probe,
)
from tests.s11_local_corpus import require_s11_local_corpus


def _observation(
    time_sec: float,
    frame_index: int,
    oil_y: float | None,
    *,
    state: str = "PARTIAL_VISIBLE",
    flags: tuple[str, ...] = (),
) -> TrajectoryObservation:
    return TrajectoryObservation(
        target_sec=time_sec,
        actual_sec=time_sec,
        frame_index=frame_index,
        raw_oil_y=oil_y,
        smoothed_oil_y=oil_y,
        fill_state=state,
        flags=flags,
    )


def _baseline(
    *,
    time_sec: float = 0.5,
    frame_index: int = 10,
    truth_y: float = 15.0,
    normally_observed: bool = True,
    fill_state: str = "PARTIAL_VISIBLE",
    flags: tuple[str, ...] = (),
) -> TruthBaseline:
    return TruthBaseline(
        case_id="synthetic:10",
        sample="synthetic",
        frame_index=frame_index,
        time_sec=time_sec,
        truth_oil_y=truth_y,
        normally_observed=normally_observed,
        production_oil_y=99.0 if normally_observed else None,
        production_error_px=84.0 if normally_observed else None,
        fill_state=fill_state,
        flags=flags,
    )


def test_held_out_observation_is_not_reused_as_estimator_input() -> None:
    stream = (
        _observation(0.0, 0, 10.0),
        _observation(0.5, 10, 99.0),
        _observation(1.0, 20, 20.0),
    )
    result = estimate_held_out(_baseline(), stream, temporal_max_jump_px=32.0)
    assert result.provenance == "estimated"
    assert result.oil_y == 15.0
    assert result.error_px == 0.0
    assert result.left_anchor_y == 10.0
    assert result.right_anchor_y == 20.0
    assert stream[1].raw_oil_y == 99.0


def test_no_interface_and_occlusion_are_never_promoted_to_numeric_oil() -> None:
    stream = (_observation(0.0, 0, 10.0), _observation(1.0, 20, 12.0))
    no_interface = estimate_held_out(
        _baseline(normally_observed=False, fill_state="FULL_NO_INTERFACE"),
        stream,
        temporal_max_jump_px=32.0,
    )
    occluded = estimate_held_out(
        _baseline(normally_observed=False, flags=("FOGGED_OR_GLARE",)),
        stream,
        temporal_max_jump_px=32.0,
    )
    assert (no_interface.provenance, no_interface.oil_y) == ("unavailable", None)
    assert no_interface.reason == "censored_no_interface_at_target"
    assert (occluded.provenance, occluded.oil_y) == ("unavailable", None)
    assert occluded.reason == "occlusion_or_detection_loss_at_target"


def test_unsupported_or_contradictory_support_abstains() -> None:
    long_gap = (
        _observation(0.0, 0, 10.0),
        _observation(1.5, 30, 12.0),
    )
    contradictory = (
        _observation(0.0, 0, 10.0),
        _observation(1.0, 20, 50.0),
    )
    repeated_ambiguity = (
        _observation(0.0, 0, 10.0),
        _observation(0.5, 5, None, flags=("OIL_EVIDENCE_AMBIGUOUS",)),
        _observation(1.0, 10, None, flags=("OIL_EVIDENCE_AMBIGUOUS",)),
        _observation(1.5, 20, 12.0),
    )
    assert estimate_held_out(_baseline(), long_gap, temporal_max_jump_px=32.0).reason == "unsupported_long_gap"
    assert estimate_held_out(_baseline(), contradictory, temporal_max_jump_px=32.0).reason == "contradictory_anchor_jump"
    assert estimate_held_out(
        _baseline(time_sec=1.0, frame_index=10, normally_observed=False),
        repeated_ambiguity,
        temporal_max_jump_px=32.0,
    ).reason == "unsupported_long_gap"


def test_no_interface_inside_support_is_censored_not_measurement() -> None:
    stream = (
        _observation(0.0, 0, 10.0),
        _observation(0.25, 5, None, state="EMPTY_NO_INTERFACE"),
        _observation(0.5, 10, None),
        _observation(1.0, 20, 12.0),
    )
    result = estimate_held_out(
        _baseline(normally_observed=False),
        stream,
        temporal_max_jump_px=32.0,
    )
    assert result.provenance == "unavailable"
    assert result.reason == "censored_no_interface_inside_support"


def test_four_video_held_out_reconstruction_is_insufficient_for_integration() -> None:
    root = require_s11_local_corpus()
    streams, baselines, estimates = run_probe(root)
    manifest = build_manifest(streams, baselines, estimates)
    truth = manifest["production_truth_anchor_baseline"]
    held_out = manifest["held_out_reconstruction"]
    stream = manifest["production_stream_baseline"]["total"]

    assert manifest["schema"] == "s11-offline-temporal-trajectory-probe-v2"
    assert manifest["estimator_design_base_sha"] == (
        "4bb52a2718d176874c59a97b9164453165a90c00"
    )
    assert manifest["production_stream_baseline_sha"] == (
        "16ea0cd1e63b929db469946ccddd75a8762042fb"
    )
    assert truth["usable_truth_count"] == 13
    assert truth["normally_observed_count"] == 8
    assert truth["normally_missing_count"] == 5
    assert truth["observed_oil_mae_px"] == 43.5 / 8.0
    assert truth["observed_oil_median_error_px"] == 6.5
    assert truth["observed_oil_worst_error_px"] == 11.0
    assert stream == {
        "sample_count": 299,
        "observed_numeric_count": 89,
        "unavailable_count": 210,
        "no_interface_count": 0,
        "blocking_flag_count": 0,
    }
    assert held_out["held_out_estimated_count"] == 3
    assert held_out["unavailable_count"] == 10
    assert held_out["recoverable_coverage"] == 3.0 / 13.0
    assert held_out["abstention_rate"] == 10.0 / 13.0
    assert held_out["estimated_mae_px"] == 22.0 / 3.0
    assert held_out["estimated_median_error_px"] == 8.5
    assert held_out["estimated_worst_error_px"] == 11.5
    assert held_out["estimated_worst_case_id"] == "sample4:1470"
    assert held_out["normally_missing_recovered_case_ids"] == []
    assert manifest["conclusion"] == "insufficient_trajectory_evidence"
    assert manifest["result_fingerprint_sha256"] == (
        "6112a32fd3bdb19d0e474bfde2e9e2568de2e6251cb47e4aa40fa60904f0478f"
    )
    assert build_manifest(streams, baselines, estimates)["result_fingerprint_sha256"] == (
        manifest["result_fingerprint_sha256"]
    )

    estimated = {
        row.case_id: (row.oil_y, row.error_px)
        for row in estimates
        if row.provenance == "estimated"
    }
    assert estimated == {
        "sample4:450": (850.5, 2.0),
        "sample4:900": (840.0, 8.5),
        "sample4:1470": (866.5, 11.5),
    }
