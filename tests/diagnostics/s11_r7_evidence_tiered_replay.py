from __future__ import annotations

"""Deterministic checked-video replay for the S11-R7 observation owners.

Each video runs in a fresh process.  Report rendering retains decoded frames and
Matplotlib/OpenCV allocations long enough that a four-video in-process replay can
be terminated by a constrained worker before sample3.  Process isolation makes
that resource boundary explicit without changing detector behavior.
"""

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


R7_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 13,
    "sample2": 5,
    "sample3": 28,
    "sample4": 62,
}
R7_TRACKING_FINGERPRINTS = {
    "base_sample_1": "ac7a4f0182145f89fbecd82fe5f2dfca81fb9f9b098148364aa32539c045df04",
    "sample2": "126464a910bca4d014adb26c3a7f9d902801408e64d249f6ea02d6d13a803852",
    "sample3": "59ce7b90d6ea253f16b422271bcff514cfb9b618fda95bec16024e50b352c338",
    "sample4": "b8ab53db8aa31db643ae9355924dfb8abd75a793797530ddcecaea376b5c1c44",
}
_MODULE = "tests.diagnostics.s11_r7_evidence_tiered_replay"


def _run_worker(
    *,
    root: Path,
    output_root: Path,
    sample: str,
    verify_fingerprints: bool,
) -> dict[str, object]:
    window = replay.QUALIFICATION_WINDOWS[sample]
    replay.QUALIFICATION_WINDOWS = {sample: window}
    return replay.run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=R7_NUMERIC_OIL_COUNTS,
        expected_tracking_fingerprints=R7_TRACKING_FINGERPRINTS,
        run_label="S11-R7",
        run_note="Evidence-tiered same-frame Oil and independent Foam replay",
        manifest_schema="s11-r7-evidence-tiered-worker-replay-v1",
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


def _assert_visual_contract(
    *,
    audits: dict[str, dict[str, object]],
    rows_by_sample: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    for sample, audit in audits.items():
        sequence = audit["sequence"]
        if sequence["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample}: numeric Oil lacks same-frame provenance")

    base_sequence = audits["base_sample_1"]["sequence"]
    if base_sequence["numeric_count"] != 13 or base_sequence["foam_numeric_count"]:
        raise AssertionError("Base checked interval Oil/Foam contract regressed")
    if any(
        row["oil_y"] is not None and float(row["timestamp_sec"]) > 6.01
        for row in rows_by_sample["base_sample_1"]
    ):
        raise AssertionError("Base explanatory-overlay interval became numeric")

    sample2_sequence = audits["sample2"]["sequence"]
    if sample2_sequence["numeric_count"] != 5 or sample2_sequence["foam_numeric_count"]:
        raise AssertionError("Sample2 clear boundary/static-Foam control regressed")

    sample3_rows = rows_by_sample["sample3"]
    black_row = nearest(sample3_rows, 67.0)
    if black_row["fill_state"] != "UNKNOWN_REVIEW" or black_row["oil_y"] is not None:
        raise AssertionError("Sample3 black/reframe barrier did not resolve UNKNOWN")
    if any(
        row["oil_y"] is not None
        for row in sample3_rows
        if 37.54 <= float(row["timestamp_sec"]) < 92.0
    ):
        raise AssertionError("Sample3 unobserved middle interval was synthesized")
    if sum(
        row["oil_y"] is not None
        for row in sample3_rows
        if float(row["timestamp_sec"]) >= 92.0
    ) < 15:
        raise AssertionError("Sample3 visually confirmed drain trajectory regressed")
    if any(
        row["foam_y"] is not None and float(row["timestamp_sec"]) > 38.0
        for row in sample3_rows
    ):
        raise AssertionError("Sample3 Foam leaked beyond the observed inflow episode")

    sample4_sequence = audits["sample4"]["sequence"]
    if sample4_sequence["numeric_count"] != 62 or sample4_sequence["foam_numeric_count"]:
        raise AssertionError("Sample4 coherent Oil/Foam-negative control regressed")
    for timestamp in (2.5, 3.0, 7.5, 9.5, 18.5, 19.0, 20.0, 35.5):
        if nearest(rows_by_sample["sample4"], timestamp)["oil_y"] is not None:
            raise AssertionError(
                f"Sample4 visually rejected partition at {timestamp:.1f}s became numeric"
            )

    padded_range_failures = []
    for detail in audits["sample4"]["provisional_visual"]["details"]:
        expected = detail["expected_oil_y_range"]
        resolved = detail["resolved_oil_y"]
        if detail["boundary_state"] != "visible" or expected is None or resolved is None:
            continue
        if not float(expected[0]) - 12.0 <= float(resolved) <= float(expected[1]) + 12.0:
            padded_range_failures.append(detail)
    if padded_range_failures:
        raise AssertionError("Sample4 numeric Oil left the direct-image trajectory band")

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or truth["numeric_count"] != 9:
        raise AssertionError(f"R7 checked truth coverage changed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 5.30:
        raise AssertionError(f"R7 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 11.0:
        raise AssertionError(f"R7 checked truth maximum error regressed: {truth}")
    return {
        "combined_user_truth": truth,
        "sample4_padded_visual_range_failure_count": len(padded_range_failures),
        "authority_note": (
            "Counts and fingerprints are deterministic regression alarms, not accuracy. "
            "The assertions above are tied to direct image review plus checked truth."
        ),
    }


def run_r7_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r7-evidence-tiered"
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
    workers = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in worker_manifests
    ]
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

    contract = _assert_visual_contract(
        audits=audits,
        rows_by_sample=rows_by_sample,
    )
    manifest = {
        "schema": "s11-r7-evidence-tiered-isolated-replay-v1",
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "inputs": {
            sample: payload
            for worker in workers
            for sample, payload in worker["inputs"].items()
        },
        "samples": summaries,
        "total_tracking_rows": sum(
            int(summary["tracking_row_count"]) for summary in summaries
        ),
        "total_numeric_oil": sum(
            int(summary["numeric_oil_count"]) for summary in summaries
        ),
        "total_captures": sum(int(summary["capture_count"]) for summary in summaries),
        "total_landmarks": sum(
            int(summary["report_landmark_count"]) for summary in summaries
        ),
        "r7_visual_audit": audits,
        "r7_contract": contract,
        "secure_windows_status": "PENDING_PRIVATE_VIDEO_UNAVAILABLE_IN_THIS_CHECKOUT",
    }
    manifest_path = output_root / "replay_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay and visually reconcile the S11-R7 observation owners."
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r7-evidence-tiered"),
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
    manifest = run_r7_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
