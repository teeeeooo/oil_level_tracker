from __future__ import annotations

"""R11 replay after one user-reviewed detector Artifact selection."""

import argparse
import json
from pathlib import Path

from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_r8_artifact_calibration_replay import run as run_calibration


def run(
    *,
    root: Path,
    output_root: Path,
    proposal_index: int = 0,
    proposal_time_sec: float = 3.0,
) -> dict[str, object]:
    payload = run_calibration(
        root=root,
        output_root=output_root,
        proposal_index=proposal_index,
        proposal_time_sec=proposal_time_sec,
        run_label="S11-R11-CAL",
        run_note="User-reviewed Artifact with bounded calibrated bootstrap",
        minimum_numeric_reference=65,
        allow_public_foam=True,
    )
    sequence = payload["sequence"]
    truth = payload["user_truth"]
    visual = payload["provisional_visual"]
    if int(sequence["numeric_count"]) != 92:
        raise AssertionError("R11 calibrated sample4 coverage changed")
    if int(sequence["foam_numeric_count"]) != 10:
        raise AssertionError("R11 calibrated dynamic Foam evidence changed")
    if int(sequence["numeric_without_same_frame_provenance"]) != 0:
        raise AssertionError("R11 calibration introduced unprovenanced Oil")
    if int(truth["numeric_count"]) != 3:
        raise AssertionError("R11 calibration changed checked truth coverage")
    if float(truth["mean_absolute_error_px"]) > 4.0:
        raise AssertionError("R11 calibration worsened checked truth MAE")
    if float(truth["maximum_absolute_error_px"]) > 11.0:
        raise AssertionError("R11 calibration worsened checked truth maximum error")
    if int(visual["visible_range_match_count"]) < 8:
        raise AssertionError("R11 calibration reduced reviewed visual matches")
    payload["schema"] = "s11-r11-artifact-calibration-replay-v1"
    payload["uncalibrated_r11_numeric_reference"] = 65
    payload["calibrated_recovery_boundary"] = (
        "User calibration expands proposals, while motion authority remains "
        "bounded to locally distributed keyframes."
    )
    payload["foam_review_boundary"] = (
        "The 39.5-47.0 s material episodes have wide, dense, registered dynamic "
        "evidence and are no longer suppressed by an Oil alias. Local visual "
        "truth labels this interval unclear, so field accuracy remains pending."
    )
    manifest = output_root / "artifact_calibration_manifest.json"
    manifest.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r11-artifact-calibration"),
    )
    parser.add_argument("--proposal-index", type=int, default=0)
    parser.add_argument("--proposal-time-sec", type=float, default=3.0)
    args = parser.parse_args()
    payload = run(
        root=repository_root() if args.root is None else args.root,
        output_root=args.output_root.resolve(),
        proposal_index=args.proposal_index,
        proposal_time_sec=args.proposal_time_sec,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
