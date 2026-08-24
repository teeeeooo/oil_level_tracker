from __future__ import annotations

"""Deterministic four-video replay for the authoritative S11 truth contract."""

import argparse
import json
from pathlib import Path

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_isolated_replay import run_isolated_replay
from tests.diagnostics.s11_observation_replay_audit import nearest
from tests.diagnostics.s11_r8_observation_recovery_replay import _aggregate_truth


_MODULE = (
    "tests.diagnostics.s11_r17_physical_observation_ownership_replay"
)

R17_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 28,
    "sample2": 4,
    "sample3": 29,
    "sample4": 101,
}
R17_TRACKING_FINGERPRINTS = {
    "base_sample_1": "5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7",
    "sample2": "85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976",
    "sample3": "feb7e139269894b0aa86d692722acb4512e487dd0b71367fa88859e67745d5a1",
    "sample4": "bc3a61417c26a3b64e2d66a6cd836c66b45be3dbb17f602dcb1e5eb6b77f78c2",
}


def _run_worker(
    *, root: Path, output_root: Path, sample: str, verify_fingerprints: bool
) -> dict[str, object]:
    replay.QUALIFICATION_WINDOWS = {
        sample: replay.QUALIFICATION_WINDOWS[sample]
    }
    return replay.run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=(
            R17_NUMERIC_OIL_COUNTS if verify_fingerprints else None
        ),
        expected_tracking_fingerprints=(
            R17_TRACKING_FINGERPRINTS if verify_fingerprints else None
        ),
        run_label="S11-R17",
        run_note=(
            "Physical observation ownership with authoritative checked truth, "
            "bounded representation correction, and current-anchor handoff"
        ),
        manifest_schema=(
            "s11-r17-physical-observation-ownership-worker-replay-v3"
        ),
    )


def _assert_r17_contract(
    audits: dict[str, dict[str, object]],
    rows_by_sample: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    for sample, audit in audits.items():
        if audit["sequence"]["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample} lost same-frame Oil provenance")

    completed_fill = [
        row
        for row in rows_by_sample["sample3"]
        if 39.0 <= float(row["timestamp_sec"]) < 64.0
    ]
    if any(row["oil_y"] is not None for row in completed_fill):
        raise AssertionError("Sample3 internal full-material cap became Oil")

    late_drain_count = sum(
        row["oil_y"] is not None
        for row in rows_by_sample["sample3"]
        if float(row["timestamp_sec"]) >= 90.0
    )
    if late_drain_count < 10:
        raise AssertionError("Sample3 reviewed drain trajectory regressed")
    reviewed_drain = nearest(rows_by_sample["sample3"], 100.0333)
    if reviewed_drain["oil_y"] is None or not (
        346.0 <= float(reviewed_drain["oil_y"]) <= 370.0
    ):
        raise AssertionError("Sample3 100 s drain witness left its reviewed band")

    visual = audits["sample4"]["provisional_visual"]
    if int(visual["visible_range_match_count"]) < 8:
        raise AssertionError("Sample4 reviewed Oil trajectory regressed")

    base_weak_frame = nearest(rows_by_sample["base_sample_1"], 5.005)
    if base_weak_frame["oil_y"] is None or not (
        360.0 <= float(base_weak_frame["oil_y"]) <= 400.0
    ):
        raise AssertionError("Base continuing anchor weak frame regressed")

    # Checked-in user truth is product authority.  A detector-owned branch
    # interpretation may explain a miss, but it cannot redefine the truth.
    required_recoveries = (
        ("sample2", 2.0),
        ("sample3", 34.5345),
    )
    for sample, timestamp in required_recoveries:
        if nearest(rows_by_sample[sample], timestamp)["oil_y"] is None:
            raise AssertionError(
                f"{sample} {timestamp:.4f} s authoritative truth is missing"
            )

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or truth["numeric_count"] < 10:
        raise AssertionError(f"R17 checked truth coverage changed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 10.0:
        raise AssertionError(f"R17 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 24.5:
        raise AssertionError(f"R17 checked truth maximum error regressed: {truth}")
    miss_penalty_px = 24.5
    coverage_adjusted_mae = (
        float(truth["mean_absolute_error_px"]) * int(truth["numeric_count"])
        + miss_penalty_px
        * (int(truth["case_count"]) - int(truth["numeric_count"]))
    ) / int(truth["case_count"])
    if coverage_adjusted_mae > 12.0:
        raise AssertionError(
            "R17 coverage-adjusted checked truth error regressed: "
            f"{coverage_adjusted_mae}"
        )

    checked_truth_misses = [
        {
            "sample": sample,
            "frame_index": int(case["frame_index"]),
            "timestamp_sec": float(case["truth_timestamp_sec"]),
            "truth_oil_y": float(case["truth_oil_y"]),
        }
        for sample, audit in audits.items()
        for case in audit["user_truth"]["cases"]
        if case["resolved_oil_y"] is None
    ]
    return {
        "combined_user_truth": truth,
        "checked_truth_miss_penalty_px": miss_penalty_px,
        "checked_truth_coverage_adjusted_mae_px": coverage_adjusted_mae,
        "sample3_completed_fill_numeric_count": 0,
        "sample3_late_drain_numeric_count": late_drain_count,
        "sample4_visible_range_match_count": int(
            visual["visible_range_match_count"]
        ),
        "same_frame_provenance": "PASS",
        "remaining_checked_truth_misses": checked_truth_misses,
    }


def run_r17_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    destination = (
        root / "sample" / "output" / "s11-r17-physical-observation-ownership"
        if output_root is None
        else Path(output_root)
    )
    return run_isolated_replay(
        module=_MODULE,
        root=root,
        output_root=destination,
        verify_fingerprints=verify_fingerprints,
        manifest_schema=(
            "s11-r17-physical-observation-ownership-isolated-replay-v3"
        ),
        audit_key="r17_visual_audit",
        contract_key="r17_contract",
        secure_windows_status="PENDING_R17_PRIVATE_VIDEO_REPLAY",
        assert_contract=_assert_r17_contract,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r17-physical-observation-ownership"),
    )
    parser.add_argument("--skip-fingerprint-check", action="store_true")
    parser.add_argument(
        "--worker-sample", choices=tuple(replay.QUALIFICATION_WINDOWS)
    )
    args = parser.parse_args()
    root = repository_root() if args.root is None else args.root
    if args.worker_sample is not None:
        _run_worker(
            root=root,
            output_root=args.output_root,
            sample=args.worker_sample,
            verify_fingerprints=not args.skip_fingerprint_check,
        )
        return 0
    manifest = run_r17_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
