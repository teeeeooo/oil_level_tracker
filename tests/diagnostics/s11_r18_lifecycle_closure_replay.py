from __future__ import annotations

"""Deterministic four-video replay for the S11-R18 lifecycle contract."""

import argparse
import json
from pathlib import Path

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_isolated_replay import run_isolated_replay
from tests.diagnostics.s11_r17_physical_observation_ownership_replay import (
    _assert_r17_contract,
)


_MODULE = "tests.diagnostics.s11_r18_lifecycle_closure_replay"

R18_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 28,
    "sample2": 4,
    "sample3": 29,
    "sample4": 101,
}
R18_TRACKING_FINGERPRINTS = {
    "base_sample_1": (
        "5879657ce71ced5970c13272867f61def7d7972195b5d264a3cf63c99f1122b7"
    ),
    "sample2": (
        "85713bc131a808d81d073bec5bff8d035604cb4c1912ba6412c1b5c448fe4976"
    ),
    "sample3": (
        "6e531bd32286f0ec2149e3cbc0d1f24debb8618f06b69eeda2f3023483e28dc5"
    ),
    "sample4": (
        "0f2029475506c87aac3ec46bf118b3ae9a1ead0da45eb0d214e1d23ececf9154"
    ),
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
            R18_NUMERIC_OIL_COUNTS if verify_fingerprints else None
        ),
        expected_tracking_fingerprints=(
            R18_TRACKING_FINGERPRINTS if verify_fingerprints else None
        ),
        run_label="S11-R18",
        run_note=(
            "Explicit initial-state lifecycle, established partial-fill "
            "reversal, and bounded Foam formation"
        ),
        manifest_schema="s11-r18-lifecycle-closure-worker-replay-v1",
    )


def run_r18_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    destination = (
        root / "sample" / "output" / "s11-r18-lifecycle-closure"
        if output_root is None
        else Path(output_root)
    )
    return run_isolated_replay(
        module=_MODULE,
        root=root,
        output_root=destination,
        verify_fingerprints=verify_fingerprints,
        manifest_schema="s11-r18-lifecycle-closure-isolated-replay-v1",
        audit_key="r18_visual_audit",
        contract_key="r18_contract",
        secure_windows_status="PENDING_R18_PRIVATE_VIDEO_REPLAY",
        assert_contract=_assert_r17_contract,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r18-lifecycle-closure"),
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
    manifest = run_r18_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
