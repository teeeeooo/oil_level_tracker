from __future__ import annotations

import argparse
import json
from pathlib import Path

from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_observation_replay_audit import (
    nearest,
    provisional_audit,
    sequence_audit,
    tracking_rows,
    user_truth_audit,
)
from tests.diagnostics.s11_report_observability_replay import run_replay


R6_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 0,
    "sample2": 5,
    "sample3": 96,
    "sample4": 89,
}
R6_TRACKING_FINGERPRINTS = {
    "base_sample_1": "83279239b61464ebecc6d7ce04a6695d6256d288ad6ef65df2eed8833f870e6e",
    "sample2": "55d608e38032ab03db49cb52ad6640d3f7ed73f0c8942847c698242bb73670b3",
    "sample3": "01f62d65b4556d2ebb6f7e66012b505e18ab20635cd50fc55c427446884b1f0d",
    "sample4": "e7a3410e06e475e4fd63c5d8b21fd49d1071747b66eca3b7953b8bc560283e22",
}


def run_r6_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r6-optics-aware"
        if output_root is None
        else Path(output_root)
    )
    manifest = run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=R6_NUMERIC_OIL_COUNTS,
        expected_tracking_fingerprints=R6_TRACKING_FINGERPRINTS,
        run_label="S11-R6",
        run_note="Optics-aware image-supported observation replay",
        manifest_schema="s11-r6-optics-aware-observation-replay-v1",
    )
    audits: dict[str, object] = {}
    rows_by_sample: dict[str, list[dict[str, object]]] = {}
    for summary in manifest["samples"]:
        sample = str(summary["sample"])
        rows = tracking_rows(Path(str(summary["bundle"])))
        rows_by_sample[sample] = rows
        sequence = sequence_audit(rows)
        if sequence["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample}: numeric Oil lacks same-frame provenance")
        audits[sample] = {
            "sequence": sequence,
            "provisional_visual": provisional_audit(root, sample, rows),
            "user_truth": user_truth_audit(root, sample, rows),
        }

    base = audits["base_sample_1"]["sequence"]
    if base["numeric_count"] != 0 or base["foam_numeric_count"] != 0:
        raise AssertionError("Base encoded-overlay window must remain unavailable")
    sample2 = audits["sample2"]["sequence"]
    if sample2["numeric_count"] != 5 or sample2["foam_numeric_count"] != 0:
        raise AssertionError("Sample2 clear boundary/static-Foam control regressed")
    black_row = nearest(rows_by_sample["sample3"], 67.0)
    if black_row["fill_state"] != "UNKNOWN_REVIEW" or black_row["oil_y"] is not None:
        raise AssertionError("Sample3 black/reframe barrier did not resolve UNKNOWN")
    if any(
        row["foam_y"] is not None
        for row in rows_by_sample["sample4"]
        if float(row["timestamp_sec"]) <= 33.6
    ):
        raise AssertionError("Sample4 annotated Foam-absent interval published Foam")

    manifest["r6_visual_audit"] = audits
    manifest["secure_windows_status"] = (
        "PENDING_PRIVATE_VIDEO_UNAVAILABLE_IN_THIS_CHECKOUT"
    )
    manifest_path = output_root / "replay_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay and visually reconcile the S11-R6 observation owners."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r6-optics-aware"),
    )
    parser.add_argument("--skip-fingerprint-check", action="store_true")
    args = parser.parse_args()
    manifest = run_r6_replay(
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
