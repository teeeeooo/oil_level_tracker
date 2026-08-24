from __future__ import annotations

"""Deterministic four-video replay for the corrected S11-R17 contract."""

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
    "sample2": 3,
    "sample3": 27,
    "sample4": 104,
}
R17_TRACKING_FINGERPRINTS = {
    "base_sample_1": "5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7",
    "sample2": "decaea14a5cdb052333470702acd2bd10075e67fe4fc3835dc69e8cce2a57572",
    "sample3": "be3c94709e01ab952e9de94816f1ef10e1de5743080a7164ec929e2f96471f92",
    "sample4": "575dddcc1c5f51de915608a67b5f073421643f99553f14e12f71552e48f0e5cb",
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
            "Physical observation ownership with checked-truth drain and "
            "continuing-anchor correction"
        ),
        manifest_schema=(
            "s11-r17-physical-observation-ownership-worker-replay-v2"
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

    # These are reported checked-truth misses, not silently removed cases.
    # The sample3 row is a newer-reviewed foreign branch; sample2 has explicit
    # provisional no-interface conflict; sample4 has no safe same-frame owner.
    expected_abstentions = (
        ("sample2", 0.0),
        ("sample2", 2.0),
        ("sample3", 34.5345),
        ("sample4", 0.0),
        ("sample4", 49.0),
    )
    for sample, timestamp in expected_abstentions:
        if nearest(rows_by_sample[sample], timestamp)["oil_y"] is not None:
            raise AssertionError(
                f"{sample} {timestamp:.4f} s safety abstention became numeric"
            )

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or truth["numeric_count"] != 8:
        raise AssertionError(f"R17 checked truth coverage changed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 9.0:
        raise AssertionError(f"R17 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 24.5:
        raise AssertionError(f"R17 checked truth maximum error regressed: {truth}")

    return {
        "combined_user_truth": truth,
        "sample3_completed_fill_numeric_count": 0,
        "sample3_late_drain_numeric_count": late_drain_count,
        "sample4_visible_range_match_count": int(
            visual["visible_range_match_count"]
        ),
        "same_frame_provenance": "PASS",
        "reported_checked_truth_abstentions": [
            {"sample": sample, "timestamp_sec": timestamp}
            for sample, timestamp in expected_abstentions
        ],
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
            "s11-r17-physical-observation-ownership-isolated-replay-v2"
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
