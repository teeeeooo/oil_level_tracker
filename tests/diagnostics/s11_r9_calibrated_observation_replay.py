from __future__ import annotations

"""Deterministic local-video replay for the S11-R9 observation contract."""

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
from tests.diagnostics.s11_r8_observation_recovery_replay import (
    R8_NUMERIC_OIL_COUNTS,
    R8_TRACKING_FINGERPRINTS,
    _assert_contract,
)


_MODULE = "tests.diagnostics.s11_r9_calibrated_observation_replay"


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
        run_label="S11-R9",
        run_note="Calibrated high-recall and independent Oil/Foam replay",
        manifest_schema="s11-r9-calibrated-observation-worker-replay-v1",
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


def run_r9_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r9-calibrated-observation"
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
    contract = _assert_contract(audits=audits, rows_by_sample=rows_by_sample)
    manifest = {
        "schema": "s11-r9-calibrated-observation-isolated-replay-v1",
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "samples": summaries,
        "total_tracking_rows": sum(
            int(item["tracking_row_count"]) for item in summaries
        ),
        "total_numeric_oil": sum(
            int(item["numeric_oil_count"]) for item in summaries
        ),
        "r9_visual_audit": audits,
        "r9_contract": contract,
        "secure_windows_status": "PENDING_R9_PRIVATE_VIDEO_REPLAY",
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
        default=Path("sample/output/s11-r9-calibrated-observation"),
    )
    parser.add_argument("--skip-fingerprint-check", action="store_true")
    parser.add_argument(
        "--worker-sample",
        choices=tuple(replay.QUALIFICATION_WINDOWS),
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
    manifest = run_r9_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
