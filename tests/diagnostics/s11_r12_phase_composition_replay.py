from __future__ import annotations

"""Deterministic local-video replay for the S11-R12 composition contract."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_observation_replay_audit import (
    provisional_audit,
    sequence_audit,
    tracking_rows,
    user_truth_audit,
)
from tests.diagnostics.s11_r8_observation_recovery_replay import _aggregate_truth


_MODULE = "tests.diagnostics.s11_r12_phase_composition_replay"

# Filled from the first accepted replay.  Keeping these next to the contract
# makes later changes explicit rather than silently accepting output drift.
R12_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 19,
    "sample2": 5,
    "sample3": 40,
    "sample4": 69,
}
R12_TRACKING_FINGERPRINTS = {
    "base_sample_1": "866af25913c3dc627f4f2af7c391c1c1a689442bdc67615aa5f173dc9e10cf02",
    "sample2": "9b2aa706a631482d5e5893822c6193e2120878878490279b282e70c94cfb262a",
    "sample3": "096be0f97d00f07cc6701c3faafbd43eab94a0838b7a952bcf40d1af3ae4c0ba",
    "sample4": "f93409c90c6ea96255213be168f71dcc7382f8f87fc24d845621c7206ba91808",
}


def _run_worker(
    *,
    root: Path,
    output_root: Path,
    sample: str,
    verify_fingerprints: bool,
) -> dict[str, object]:
    replay.QUALIFICATION_WINDOWS = {sample: replay.QUALIFICATION_WINDOWS[sample]}
    expected_counts = R12_NUMERIC_OIL_COUNTS if verify_fingerprints else None
    expected_fingerprints = R12_TRACKING_FINGERPRINTS if verify_fingerprints else None
    return replay.run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=expected_counts,
        expected_tracking_fingerprints=expected_fingerprints,
        run_label="S11-R12",
        run_note="Phase identity, bounded material identity and independent series validity",
        manifest_schema="s11-r12-phase-composition-worker-replay-v1",
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


def run_r12_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r12-phase-composition"
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
    audits: dict[str, dict[str, object]] = {}
    rows_by_sample: dict[str, list[dict[str, object]]] = {}
    for summary in summaries:
        sample = str(summary["sample"])
        rows = tracking_rows(Path(str(summary["bundle"])))
        rows_by_sample[sample] = rows
        audits[sample] = {
            "sequence": sequence_audit(rows),
            "provisional_visual": provisional_audit(root, sample, rows),
            "user_truth": user_truth_audit(root, sample, rows),
        }
    contract = _assert_r12_contract(audits, rows_by_sample)
    manifest = {
        "schema": "s11-r12-phase-composition-isolated-replay-v1",
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "samples": summaries,
        "total_tracking_rows": sum(int(item["tracking_row_count"]) for item in summaries),
        "total_numeric_oil": sum(int(item["numeric_oil_count"]) for item in summaries),
        "r12_visual_audit": audits,
        "r12_contract": contract,
        "secure_windows_status": "PENDING_R12_PRIVATE_VIDEO_REPLAY",
    }
    path = output_root / "replay_manifest.json"
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def _assert_r12_contract(
    audits: dict[str, dict[str, object]],
    rows_by_sample: dict[str, list[dict[str, object]]],
) -> dict[str, object]:
    for sample, audit in audits.items():
        if audit["sequence"]["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample} lost same-frame Oil provenance")
    if sum(
        row["oil_y"] is not None
        for row in rows_by_sample["sample3"]
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
    if truth["case_count"] != 13 or int(truth["numeric_count"]) < 9:
        raise AssertionError(f"R12 checked truth coverage regressed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 6.5:
        raise AssertionError(f"R12 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 12.0:
        raise AssertionError(f"R12 checked truth maximum error regressed: {truth}")
    return {
        "combined_user_truth": truth,
        "sample4_padded_visual_range_failure_count": len(padded_range_failures),
        "same_frame_provenance": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r12-phase-composition"),
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
    manifest = run_r12_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
