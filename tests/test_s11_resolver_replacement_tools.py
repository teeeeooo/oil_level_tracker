from copy import deepcopy

import pytest

from tests.diagnostics.s11_resolver_replacement_compare import compare


def _manifest():
    return {
        "sampling_fps": 2.0,
        "qualification_windows": {},
        "runtime_provenance": {"runtime_fingerprint_sha256": "same-runtime"},
        "samples": [
            {
                "sample": "control",
                "tracking_fingerprint_sha256": "same-output",
                "tracking_row_count": 13,
            }
        ],
        "control_visual_audit": {
            "control": {
                "sequence": {"numeric_without_same_frame_provenance": 0},
                "user_truth": {
                    "cases": [
                        {
                            "frame_index": i,
                            "truth_oil_y": 100.0,
                            "truth_timestamp_sec": float(i),
                            "sample_timestamp_sec": float(i),
                            "resolved_oil_y": 105.0,
                            "absolute_error_px": 5.0,
                        }
                        for i in range(13)
                    ]
                },
            }
        },
    }


def test_better_aggregate_does_not_hide_a_regressed_truth_case():
    baseline = _manifest()
    candidate = deepcopy(baseline)
    cases = candidate["control_visual_audit"]["control"]["user_truth"]["cases"]
    for case in cases:
        case.update(resolved_oil_y=100.0, absolute_error_px=0.0)
    cases[0].update(resolved_oil_y=106.0, absolute_error_px=6.0)
    result = compare(baseline, candidate)
    assert result["status"] == "FAIL"
    assert result["regressions"] == ["control:0"]


def test_sample_realignment_cannot_manufacture_truth_success():
    baseline = _manifest()
    candidate = deepcopy(baseline)
    candidate["control_visual_audit"]["control"]["user_truth"]["cases"][0][
        "sample_timestamp_sec"
    ] = 0.5
    with pytest.raises(AssertionError, match="alignment changed"):
        compare(baseline, candidate)


def test_environment_drift_is_not_detector_regression_evidence():
    baseline = _manifest()
    candidate = deepcopy(baseline)
    candidate["runtime_provenance"]["runtime_fingerprint_sha256"] = "different-runtime"
    with pytest.raises(AssertionError, match="ENVIRONMENT_DRIFT"):
        compare(baseline, candidate)


def test_nonfinite_or_stale_error_cannot_hide_a_regression():
    baseline = _manifest()
    for error in (float("nan"), 0.0):
        candidate = deepcopy(baseline)
        candidate["control_visual_audit"]["control"]["user_truth"]["cases"][0][
            "absolute_error_px"
        ] = error
        with pytest.raises(AssertionError, match="inconsistent truth error"):
            compare(baseline, candidate)


def test_dropping_nontruth_rows_does_not_pass_replay_comparison():
    baseline = _manifest()
    candidate = deepcopy(baseline)
    candidate["samples"][0]["tracking_row_count"] = 12
    with pytest.raises(AssertionError, match="row count changed"):
        compare(baseline, candidate)
