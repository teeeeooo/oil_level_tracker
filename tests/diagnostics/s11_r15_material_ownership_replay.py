from __future__ import annotations

"""Deterministic four-video replay for the S11-R15 material-ownership contract."""

import argparse
import json
from pathlib import Path

from tests.diagnostics import s11_report_observability_replay as replay
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_isolated_replay import run_isolated_replay
from tests.diagnostics.s11_r14_phase_component_replay import (
    _assert_phase_component_contract,
)


_MODULE = "tests.diagnostics.s11_r15_material_ownership_replay"

R15_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 30,
    "sample2": 3,
    "sample3": 43,
    "sample4": 111,
}
R15_TRACKING_FINGERPRINTS = {
    "base_sample_1": "0a68c47d131ec3c0414d78c3dd8e61422ab484ba403c7320d4af0e28bd496a34",
    "sample2": "834c323e96c1df35f9ff17f746510c99dfece43b10cd015d15206a6d11b97b07",
    "sample3": "c2fe7b1eb3de3ad5b169f61ba06c9ebcc7aec016c6e6a082f3517ca3d517d4c9",
    "sample4": "2da3ba6cdacb59bda03541243132d0a3ce014b38c49451411a05d5aef928bfe2",
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
            R15_NUMERIC_OIL_COUNTS if verify_fingerprints else None
        ),
        expected_tracking_fingerprints=(
            R15_TRACKING_FINGERPRINTS if verify_fingerprints else None
        ),
        run_label="S11-R15",
        run_note="State-aware Oil entry, material-owned Foam and dynamic droplet support",
        manifest_schema="s11-r15-material-ownership-worker-replay-v1",
    )


def run_r15_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    destination = (
        root / "sample" / "output" / "s11-r15-material-ownership"
        if output_root is None
        else Path(output_root)
    )
    return run_isolated_replay(
        module=_MODULE,
        root=root,
        output_root=destination,
        verify_fingerprints=verify_fingerprints,
        manifest_schema="s11-r15-material-ownership-isolated-replay-v1",
        audit_key="r15_visual_audit",
        contract_key="r15_contract",
        secure_windows_status="PENDING_R15_PRIVATE_VIDEO_REPLAY",
        assert_contract=_assert_phase_component_contract,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r15-material-ownership"),
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
    manifest = run_r15_replay(
        root=root,
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
