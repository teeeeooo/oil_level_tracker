"""Compare protected truth cases individually, not just aggregate coverage."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def cases(manifest: dict) -> dict[tuple[str, int], dict]:
    audits = [v for k, v in manifest.items() if k.endswith("_visual_audit")]
    if len(audits) != 1:
        raise ValueError("Expected exactly one replay audit")
    result = {}
    for sample, audit in audits[0].items():
        if audit["sequence"]["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample}: missing same-frame provenance")
        for case in audit["user_truth"]["cases"]:
            key = (sample, int(case["frame_index"]))
            if key in result:
                raise AssertionError(f"Duplicate truth case {key}")
            truth, resolved, error = (
                case["truth_oil_y"],
                case["resolved_oil_y"],
                case["absolute_error_px"],
            )
            if not math.isfinite(float(truth)):
                raise AssertionError(f"{key}: nonfinite truth")
            if resolved is None:
                if error is not None:
                    raise AssertionError(
                        f"{key}: missing observation has numeric error"
                    )
            elif (
                not math.isfinite(float(resolved))
                or error is None
                or not math.isfinite(float(error))
                or not math.isclose(
                    float(error), abs(float(resolved) - float(truth)), abs_tol=1e-9
                )
            ):
                raise AssertionError(f"{key}: inconsistent truth error")
            result[key] = case
    return result


def compare(baseline: dict, candidate: dict) -> dict:
    before, after = cases(baseline), cases(candidate)
    if len(before) != 13 or before.keys() != after.keys():
        raise AssertionError("Protected 13-case cohort changed")
    runtime = "runtime_fingerprint_sha256"
    if (
        baseline["runtime_provenance"][runtime]
        != candidate["runtime_provenance"][runtime]
    ):
        raise AssertionError("ENVIRONMENT_DRIFT: replay runtimes differ")
    for field in ("sampling_fps", "qualification_windows"):
        if baseline[field] != candidate[field]:
            raise AssertionError(f"Replay coverage changed: {field}")
    rows, regressions = [], []
    for key in sorted(before):
        old, new = before[key], after[key]
        for field in ("truth_oil_y", "truth_timestamp_sec", "sample_timestamp_sec"):
            if old[field] != new[field]:
                raise AssertionError(f"{key}: truth/sample alignment changed: {field}")
        old_error, new_error = old["absolute_error_px"], new["absolute_error_px"]
        regressed = old_error is not None and (
            new_error is None or float(new_error) > float(old_error) + 1e-9
        )
        if regressed:
            regressions.append(f"{key[0]}:{key[1]}")
        rows.append(
            {
                "sample": key[0],
                "frame_index": key[1],
                "truth_y": old["truth_oil_y"],
                "baseline_y": old["resolved_oil_y"],
                "candidate_y": new["resolved_oil_y"],
                "baseline_error_px": old_error,
                "candidate_error_px": new_error,
                "regressed": regressed,
            }
        )
    old_samples = {v["sample"]: v for v in baseline["samples"]}
    new_samples = {v["sample"]: v for v in candidate["samples"]}
    if old_samples.keys() != new_samples.keys():
        raise AssertionError("Replay sample cohort changed")
    for sample in old_samples:
        if (
            old_samples[sample]["tracking_row_count"]
            != new_samples[sample]["tracking_row_count"]
        ):
            raise AssertionError(f"{sample}: replay row count changed")
    fingerprints = {
        sample: old_samples[sample]["tracking_fingerprint_sha256"]
        == new_samples[sample]["tracking_fingerprint_sha256"]
        for sample in old_samples
    }
    return {
        "schema": "s11-resolver-casewise-comparison-v1",
        "case_count": len(rows),
        "regressions": regressions,
        "status": "FAIL" if regressions else "PASS",
        "cases": rows,
        "identical_tracking_fingerprints": fingerprints,
        "note": "Casewise truth comparison complements, not replaces, safety/temporal tests.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = compare(
        json.loads(args.baseline.read_text()), json.loads(args.candidate.read_text())
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"{result['status']}: {result['case_count']} protected truth cases")
    return 1 if result["regressions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
