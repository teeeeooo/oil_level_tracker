"""Profile a content-identified Oil replacement without pretending dirty HEAD is clean.

Run one sample in one fresh process. Baseline/candidate comparisons must use the
same input/runtime hashes, debug level and serial scheduling. Expected outputs
come from the separately reviewed replay, never from this timing run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


def source_identity(root: Path) -> dict[str, object]:
    paths = sorted((root / "src").rglob("*.py"))
    # Include replay harnesses: they determine both output and measured stages.
    paths += sorted((root / "tests" / "diagnostics").glob("*.py"))
    entries = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in paths
    }
    return {
        "sha256": hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "files": entries,
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "git_status": subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=root, text=True
        ).splitlines(),
    }


def peak_rss() -> dict[str, object]:
    try:
        import resource
    except ImportError:
        return {
            "bytes": None,
            "status": "UNAVAILABLE",
            "method": "resource unavailable",
        }
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    system = platform.system()
    if system not in {"Darwin", "Linux"}:
        return {
            "bytes": None,
            "status": "UNAVAILABLE",
            "method": "unknown ru_maxrss unit",
        }
    return {
        "bytes": int(raw if system == "Darwin" else raw * 1024),
        "status": "MEASURED",
        "method": "process-lifetime peak RSS; one sample per fresh process",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument(
        "--sample",
        required=True,
        choices=("base_sample_1", "sample2", "sample3", "sample4"),
    )
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--expected-fingerprint", required=True)
    parser.add_argument(
        "--debug-level", choices=("none", "basic", "full"), default="none"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    before = source_identity(root)
    # Works for either a clean baseline checkout or an uncommitted candidate.
    sys.path[:0] = [str(root / "src"), str(root)]
    from tests.diagnostics.s11_r16_performance_profile import _run_once
    from tests.diagnostics.s11_replay_provenance import capture_runtime_provenance
    from tests.diagnostics.s11_evidence_probe import authoritative_input_hashes
    from oil_tracker.domain.session import DebugTraceLevel

    runtime = capture_runtime_provenance(root / "sample" / f"{args.sample}.mp4")
    inputs = authoritative_input_hashes(root)
    result = _run_once(
        root=root,
        output_root=args.output_root.resolve(),
        sample=args.sample,
        repeat=1,
        debug_trace_level=DebugTraceLevel(args.debug_level),
        behavior_owner="content-identified-oil-resolver-comparison",
        expected_numeric_oil_count=args.expected_count,
        expected_tracking_fingerprint=args.expected_fingerprint,
    )
    after = source_identity(root)
    if before != after:
        raise RuntimeError("Source changed during timing; discard this measurement")
    if inputs != authoritative_input_hashes(root):
        raise RuntimeError(
            "Replay inputs changed during timing; discard this measurement"
        )
    payload = {
        "schema": "s11-resolver-replacement-profile-v1",
        "source": before,
        "runtime": runtime,
        "input_hashes": inputs,
        "profile_driver_sha256": hashlib.sha256(
            Path(__file__).read_bytes()
        ).hexdigest(),
        "debug_level": args.debug_level,
        "result": result,
        "peak_rss": peak_rss(),
        "limits": "Host-specific measurement; source content is authority, not Git HEAD alone.",
    }
    destination = args.output_root / "profile.json"
    destination.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
