from __future__ import annotations

"""Deterministic four-video replay for the S11-R13 phase-identity contract."""

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


_MODULE = "tests.diagnostics.s11_r13_phase_identity_replay"

R13_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 6,
    "sample2": 5,
    "sample3": 32,
    "sample4": 78,
}
R13_TRACKING_FINGERPRINTS = {
    "base_sample_1": "9be36db34d83253bd6b5c0c2f94191103c3f38abc353e008a9d561b2078ce43c",
    "sample2": "9b2aa706a631482d5e5893822c6193e2120878878490279b282e70c94cfb262a",
    "sample3": "76e42925c2dec1e80ef133fc4f52b9ecf55df6f376fbf761e6e00f80758fe0ba",
    "sample4": "6bbcea601b01d0eae7d26f54b2b5e850e21bb6598cccb1c828c3fcd0b69747e1",
}


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
        expected_numeric_oil_counts=(
            R13_NUMERIC_OIL_COUNTS if verify_fingerprints else None
        ),
        expected_tracking_fingerprints=(
            R13_TRACKING_FINGERPRINTS if verify_fingerprints else None
        ),
        run_label="S11-R13",
        run_note="Typed phase identity, bounded composition and independent graph validity",
        manifest_schema="s11-r13-phase-identity-worker-replay-v1",
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


def run_r13_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r13-phase-identity"
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

    contract = _assert_r13_contract(audits, rows_by_sample)
    manifest = {
        "schema": "s11-r13-phase-identity-isolated-replay-v1",
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "samples": summaries,
        "total_tracking_rows": sum(int(item["tracking_row_count"]) for item in summaries),
        "total_numeric_oil": sum(int(item["numeric_oil_count"]) for item in summaries),
        "r13_visual_audit": audits,
        "r13_contract": contract,
        "secure_windows_status": "PENDING_R13_PRIVATE_VIDEO_REPLAY",
    }
    path = output_root / "replay_manifest.json"
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def _assert_r13_contract(
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
    if sum(
        row["oil_y"] is not None
        for row in rows_by_sample["sample3"]
        if float(row["timestamp_sec"]) >= 92.0
    ) < 10:
        raise AssertionError("Sample3 observed drain trajectory regressed")

    visual = audits["sample4"]["provisional_visual"]
    if int(visual["visible_range_match_count"]) < 7:
        raise AssertionError("Sample4 reviewed Oil trajectory regressed")

    truth = _aggregate_truth(audits)
    if truth["case_count"] != 13 or int(truth["numeric_count"]) < 9:
        raise AssertionError(f"R13 checked truth coverage regressed: {truth}")
    if float(truth["mean_absolute_error_px"]) > 6.0:
        raise AssertionError(f"R13 checked truth MAE regressed: {truth}")
    if float(truth["maximum_absolute_error_px"]) > 11.0:
        raise AssertionError(f"R13 checked truth maximum error regressed: {truth}")
    return {
        "combined_user_truth": truth,
        "sample3_completed_fill_numeric_count": 0,
        "sample4_visible_range_match_count": int(visual["visible_range_match_count"]),
        "same_frame_provenance": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r13-phase-identity"),
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
    manifest = run_r13_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
