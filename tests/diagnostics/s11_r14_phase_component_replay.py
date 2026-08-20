from __future__ import annotations

"""Deterministic four-video replay for the S11-R14 phase-component contract."""

import argparse
import json
from pathlib import Path

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_isolated_replay import run_isolated_replay
from tests.diagnostics.s11_r8_observation_recovery_replay import _aggregate_truth


_MODULE = "tests.diagnostics.s11_r14_phase_component_replay"

R14_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 30,
    "sample2": 3,
    "sample3": 43,
    "sample4": 111,
}
R14_TRACKING_FINGERPRINTS = {
    "base_sample_1": "0a68c47d131ec3c0414d78c3dd8e61422ab484ba403c7320d4af0e28bd496a34",
    "sample2": "834c323e96c1df35f9ff17f746510c99dfece43b10cd015d15206a6d11b97b07",
    "sample3": "c2fe7b1eb3de3ad5b169f61ba06c9ebcc7aec016c6e6a082f3517ca3d517d4c9",
    "sample4": "4e654710c728e504fe81bec647d617b2b13f6fbe2b311d614f2e0345e7501e8c",
}


def _run_worker(
    *, root: Path, output_root: Path, sample: str, verify_fingerprints: bool
) -> dict[str, object]:
    replay.QUALIFICATION_WINDOWS = {sample: replay.QUALIFICATION_WINDOWS[sample]}
    return replay.run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=(
            R14_NUMERIC_OIL_COUNTS if verify_fingerprints else None
        ),
        expected_tracking_fingerprints=(
            R14_TRACKING_FINGERPRINTS if verify_fingerprints else None
        ),
        run_label="S11-R14",
        run_note="Phase-owned components, recent-Foam composition and bounded drain reacquisition",
        manifest_schema="s11-r14-phase-component-worker-replay-v1",
    )


def run_r14_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    destination = (
        root / "sample" / "output" / "s11-r14-phase-component"
        if output_root is None
        else Path(output_root)
    )
    return run_isolated_replay(
        module=_MODULE,
        root=root,
        output_root=destination,
        verify_fingerprints=verify_fingerprints,
        manifest_schema="s11-r14-phase-component-isolated-replay-v1",
        audit_key="r14_visual_audit",
        contract_key="r14_contract",
        secure_windows_status="PENDING_R14_PRIVATE_VIDEO_REPLAY",
        assert_contract=_assert_phase_component_contract,
    )


def _assert_phase_component_contract(
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
        raise AssertionError("Sample3 internal full-material cap became numeric Oil")
    late_drain_count = sum(
        row["oil_y"] is not None
        for row in rows_by_sample["sample3"]
        if float(row["timestamp_sec"]) >= 90.0
    )
    if late_drain_count < 10:
        raise AssertionError("Sample3 observed drain trajectory regressed")

    visual = audits["sample4"]["provisional_visual"]
    if int(visual["visible_range_match_count"]) < 8:
        raise AssertionError("Sample4 reviewed Oil trajectory regressed")

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or int(truth["numeric_count"]) < 10:
        raise AssertionError(f"Phase-component checked truth coverage regressed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 9.0:
        raise AssertionError(f"Phase-component checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 26.0:
        raise AssertionError(f"Phase-component checked truth maximum error regressed: {truth}")
    return {
        "combined_user_truth": truth,
        "sample3_completed_fill_numeric_count": 0,
        "sample3_late_drain_numeric_count": late_drain_count,
        "sample4_visible_range_match_count": int(visual["visible_range_match_count"]),
        "same_frame_provenance": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r14-phase-component"),
    )
    parser.add_argument("--skip-fingerprint-check", action="store_true")
    parser.add_argument("--worker-sample", choices=tuple(replay.QUALIFICATION_WINDOWS))
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
    manifest = run_r14_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
