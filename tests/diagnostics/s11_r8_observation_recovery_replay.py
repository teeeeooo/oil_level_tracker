from __future__ import annotations

"""Deterministic four-video replay for the S11-R8 observation contract."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_observation_replay_audit import (
    nearest,
    provisional_audit,
    sequence_audit,
    tracking_rows,
    user_truth_audit,
)
from tests.diagnostics import s11_report_observability_replay as replay


R8_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 19,
    "sample2": 5,
    "sample3": 42,
    "sample4": 76,
}
R8_TRACKING_FINGERPRINTS = {
    "base_sample_1": "866af25913c3dc627f4f2af7c391c1c1a689442bdc67615aa5f173dc9e10cf02",
    "sample2": "126464a910bca4d014adb26c3a7f9d902801408e64d249f6ea02d6d13a803852",
    "sample3": "d0ac9850184808f5694a5629d17c4555086509bda85acc0bd2f92899b4244d54",
    "sample4": "efa07c4a0fff885b858ac179cff264bff6c79abfe49a48e205c0ce5e34560edd",
}
_MODULE = "tests.diagnostics.s11_r8_observation_recovery_replay"


def _run_worker(
    *,
    root: Path,
    output_root: Path,
    sample: str,
    verify_fingerprints: bool,
) -> dict[str, object]:
    replay.QUALIFICATION_WINDOWS = {sample: replay.QUALIFICATION_WINDOWS[sample]}
    return replay.run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=R8_NUMERIC_OIL_COUNTS,
        expected_tracking_fingerprints=R8_TRACKING_FINGERPRINTS,
        run_label="S11-R8",
        run_note="Independent Oil/Foam observation recovery replay",
        manifest_schema="s11-r8-observation-recovery-worker-replay-v1",
    )


def _spawn_worker(
    *,
    root: Path,
    output_root: Path,
    sample: str,
    verify_fingerprints: bool,
) -> Path:
    sample_output = (output_root / sample).resolve()
    command = [
        sys.executable,
        "-m",
        _MODULE,
        "--root",
        str(root.resolve()),
        "--output-root",
        str(sample_output),
        "--worker-sample",
        sample,
    ]
    if not verify_fingerprints:
        command.append("--skip-fingerprint-check")
    subprocess.run(command, cwd=root, check=True)
    return sample_output / "replay_manifest.json"


def _aggregate_truth(audits: dict[str, dict[str, object]]) -> dict[str, object]:
    cases = [
        case
        for audit in audits.values()
        for case in audit["user_truth"]["cases"]
    ]
    errors = [
        float(case["absolute_error_px"])
        for case in cases
        if case["absolute_error_px"] is not None
    ]
    return {
        "case_count": len(cases),
        "numeric_count": len(errors),
        "mean_absolute_error_px": None if not errors else sum(errors) / len(errors),
        "maximum_absolute_error_px": None if not errors else max(errors),
    }


def _assert_contract(
    *,
    audits: dict[str, dict[str, object]],
    rows_by_sample: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    for sample, audit in audits.items():
        sequence = audit["sequence"]
        if sequence["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample}: numeric Oil lacks same-frame provenance")

    for sample in ("base_sample_1", "sample2", "sample4"):
        if audits[sample]["sequence"]["foam_numeric_count"]:
            raise AssertionError(f"{sample}: false public Foam was emitted")

    sample3_rows = rows_by_sample["sample3"]
    black = nearest(sample3_rows, 67.0)
    if black["fill_state"] != "UNKNOWN_REVIEW" or black["oil_y"] is not None:
        raise AssertionError("Sample3 black/reframe barrier did not remain UNKNOWN")
    if any(
        row["foam_y"] is not None and float(row["timestamp_sec"]) > 38.0
        for row in sample3_rows
    ):
        raise AssertionError("Sample3 Foam leaked beyond the observed inflow episodes")
    if any(
        row["oil_y"] is not None
        for row in sample3_rows
        if 39.0 <= float(row["timestamp_sec"]) < 90.0
    ):
        raise AssertionError("Sample3 completed-fill texture was reacquired as Oil")
    if sum(
        row["oil_y"] is not None
        for row in sample3_rows
        if float(row["timestamp_sec"]) >= 92.0
    ) < 15:
        raise AssertionError("Sample3 observed drain trajectory regressed")

    padded_range_failures = []
    for detail in audits["sample4"]["provisional_visual"]["details"]:
        expected = detail["expected_oil_y_range"]
        resolved = detail["resolved_oil_y"]
        if detail["boundary_state"] != "visible" or expected is None or resolved is None:
            continue
        if not float(expected[0]) - 15.0 <= float(resolved) <= float(expected[1]) + 15.0:
            padded_range_failures.append(detail)
    if padded_range_failures:
        raise AssertionError("Sample4 numeric Oil left the reviewed trajectory band")

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or truth["numeric_count"] != 10:
        raise AssertionError(f"R8 checked truth coverage changed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 5.85 + 1e-9:
        raise AssertionError(f"R8 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 11.0:
        raise AssertionError(f"R8 checked truth maximum error regressed: {truth}")
    return {
        "combined_user_truth": truth,
        "sample4_padded_visual_range_failure_count": len(padded_range_failures),
        "authority_note": (
            "Fingerprints are deterministic alarms. Direct image review, same-frame "
            "provenance and checked truth define the accuracy contract."
        ),
    }


def run_r8_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r8-observation-recovery"
        if output_root is None
        else Path(output_root)
    ).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    worker_manifests = [
        _spawn_worker(
            root=root,
            output_root=output_root,
            sample=sample,
            verify_fingerprints=verify_fingerprints,
        )
        for sample in replay.QUALIFICATION_WINDOWS
    ]
    workers = [json.loads(path.read_text(encoding="utf-8")) for path in worker_manifests]
    summaries = [worker["samples"][0] for worker in workers]
    rows_by_sample: dict[str, list[dict[str, object]]] = {}
    audits: dict[str, dict[str, object]] = {}
    for summary in summaries:
        sample = str(summary["sample"])
        rows = tracking_rows(Path(str(summary["bundle"])))
        rows_by_sample[sample] = rows
        audits[sample] = {
            "sequence": sequence_audit(rows),
            "provisional_visual": provisional_audit(root, sample, rows),
            "user_truth": user_truth_audit(root, sample, rows),
        }
    contract = _assert_contract(audits=audits, rows_by_sample=rows_by_sample)
    manifest = {
        "schema": "s11-r8-observation-recovery-isolated-replay-v1",
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "samples": summaries,
        "total_tracking_rows": sum(int(item["tracking_row_count"]) for item in summaries),
        "total_numeric_oil": sum(int(item["numeric_oil_count"]) for item in summaries),
        "r8_visual_audit": audits,
        "r8_contract": contract,
        "secure_windows_status": "PENDING_R8_PRIVATE_VIDEO_REPLAY",
    }
    path = output_root / "replay_manifest.json"
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r8-observation-recovery"),
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
    manifest = run_r8_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
