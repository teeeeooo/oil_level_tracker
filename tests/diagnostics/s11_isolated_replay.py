from __future__ import annotations

"""Shared process-isolated replay orchestration for versioned S11 gates."""

from collections.abc import Callable
import json
from pathlib import Path
import subprocess
import sys

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_observation_replay_audit import (
    provisional_audit,
    sequence_audit,
    tracking_rows,
    user_truth_audit,
)


ReplayContract = Callable[
    [dict[str, dict[str, object]], dict[str, list[dict[str, object]]]],
    dict[str, object],
]


def spawn_worker(
    *,
    module: str,
    root: Path,
    output_root: Path,
    sample: str,
    verify_fingerprints: bool,
) -> Path:
    sample_output = (output_root / sample).resolve()
    command = [
        sys.executable,
        "-m",
        module,
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


def run_isolated_replay(
    *,
    module: str,
    root: Path,
    output_root: Path,
    verify_fingerprints: bool,
    manifest_schema: str,
    audit_key: str,
    contract_key: str,
    secure_windows_status: str,
    assert_contract: ReplayContract,
) -> dict[str, object]:
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    worker_manifests = [
        spawn_worker(
            module=module,
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

    contract = assert_contract(audits, rows_by_sample)
    manifest = {
        "schema": manifest_schema,
        "sampling_fps": replay.SAMPLING_FPS,
        "qualification_windows": replay.QUALIFICATION_WINDOWS,
        "accepted_count_check_enabled": verify_fingerprints,
        "worker_isolation": "one_video_per_process",
        "worker_manifests": [str(path) for path in worker_manifests],
        "samples": summaries,
        "total_tracking_rows": sum(int(item["tracking_row_count"]) for item in summaries),
        "total_numeric_oil": sum(int(item["numeric_oil_count"]) for item in summaries),
        audit_key: audits,
        contract_key: contract,
        "secure_windows_status": secure_windows_status,
    }
    path = output_root / "replay_manifest.json"
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest
