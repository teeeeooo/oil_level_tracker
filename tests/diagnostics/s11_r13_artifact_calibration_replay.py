from __future__ import annotations

"""R13 replay after one user-reviewed detector Artifact selection."""

import argparse
import json
from pathlib import Path

from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_r8_artifact_calibration_replay import run as run_calibration


R13_CALIBRATED_TRACKING_FINGERPRINT = (
    "ef66e7980008545537d2d963ed86b5f11ff9ad1e20e1ea4e99eedbe7b7c7e75a"
)


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
        run_label="S11-R13-CAL",
        run_note="User-reviewed Artifact with typed phase identity recovery",
        minimum_numeric_reference=78,
        allow_public_foam=True,
    )
    sequence = payload["sequence"]
    truth = payload["user_truth"]
    visual = payload["provisional_visual"]
    summary = payload["summary"]
    if int(sequence["numeric_count"]) != 97:
        raise AssertionError("R13 calibrated sample4 coverage changed")
    if int(sequence["foam_numeric_count"]) != 0:
        raise AssertionError("R13 calibrated sample4 emitted false Foam")
    if int(sequence["numeric_without_same_frame_provenance"]) != 0:
        raise AssertionError("R13 calibration introduced unprovenanced Oil")
    if str(summary["tracking_fingerprint_sha256"]) != R13_CALIBRATED_TRACKING_FINGERPRINT:
        raise AssertionError("R13 calibrated tracking fingerprint changed")
    if int(truth["numeric_count"]) != 2:
        raise AssertionError("R13 calibration changed checked truth coverage")
    if float(truth["maximum_absolute_error_px"]) > 1.0:
        raise AssertionError("R13 calibration worsened checked truth error")
    if int(visual["visible_range_match_count"]) < 9:
        raise AssertionError("R13 calibration reduced reviewed visual matches")
    payload["schema"] = "s11-r13-artifact-calibration-replay-v1"
    payload["uncalibrated_r13_numeric_reference"] = 78
    payload["phase_identity_boundary"] = (
        "User calibration removes only matching geometry. Diffuse proposals still "
        "need typed direct or ordered-lower identity; high-conflict scans cannot "
        "use the ordered-lower exception."
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
        default=Path("sample/output/s11-r13-artifact-calibration"),
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
