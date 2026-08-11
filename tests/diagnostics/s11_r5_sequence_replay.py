from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

from oil_tracker.adapters.storage.json_truth_repository import JsonTruthRepository
from tests.diagnostics.s11_evidence_probe import repository_root
from tests.diagnostics.s11_report_observability_replay import (
    QUALIFICATION_WINDOWS,
    run_replay,
)


R5_NUMERIC_OIL_COUNTS = {
    "base_sample_1": 0,
    "sample2": 2,
    "sample3": 49,
    "sample4": 97,
}
R5_TRACKING_FINGERPRINTS = {
    "base_sample_1": "a28aeaa603fb5912aaedf132423d8f78badf9a8a898bcdc9e937af911503af80",
    "sample2": "61a55cc9f0992f8027d0add32c3679e994c4f62688be79893ea438cafd8db9ae",
    "sample3": "476f49c9f13b3fc93e0aaff97238fb0bdf85cfc69353b29de074023cbc6c68f5",
    "sample4": "8cb1785825eab4124000c56bc5d4e20859a712c63302f2a0e996cb1ccf37b21b",
}
R4_NUMERIC_OIL_REFERENCE = {
    "base_sample_1": 2,
    "sample2": 2,
    "sample3": 21,
    "sample4": 64,
}


def _optional_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _tracking_rows(bundle: Path) -> list[dict[str, object]]:
    with (bundle / "tracking_data.csv").open(
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        source = list(csv.DictReader(handle))
    return [
        {
            **row,
            "frame_index": int(row["frame_index"]),
            "timestamp_sec": float(row["timestamp_sec"]),
            "oil_y": _optional_float(row["raw_oil_air_level_y"]),
            "foam_y": _optional_float(row["raw_foam_front_y"]),
            "flags_set": {
                item for item in str(row["flags"]).split(";") if item
            },
        }
        for row in source
    ]


def _nearest(
    rows: list[dict[str, object]],
    timestamp_sec: float,
) -> dict[str, object]:
    return min(
        rows,
        key=lambda row: abs(float(row["timestamp_sec"]) - timestamp_sec),
    )


def _provisional_audit(
    root: Path,
    sample: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    path = root / "sample" / f"{sample}.provisional-truth.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    start, end = QUALIFICATION_WINDOWS[sample]
    visible_count = visible_numeric = visible_range_match = 0
    no_interface_count = no_interface_numeric = 0
    foam_evaluated = foam_match = 0
    details: list[dict[str, object]] = []
    for annotation in payload["annotations"]:
        timestamp = float(annotation["timestamp_sec"])
        if timestamp < start - 1e-6 or timestamp > end + 0.26:
            continue
        row = _nearest(rows, timestamp)
        oil_y = row["oil_y"]
        foam_present = row["foam_y"] is not None or str(row["fill_state"]) in {
            "FOAMING_VISIBLE",
            "FULL_WITH_FOAM",
        }
        boundary_state = str(annotation.get("boundary_state", ""))
        expected_range = annotation.get("oil_level_y_range_px")
        range_match: bool | None = None
        if boundary_state == "visible" and expected_range is not None:
            visible_count += 1
            visible_numeric += oil_y is not None
            range_match = bool(
                oil_y is not None
                and float(expected_range[0]) <= float(oil_y) <= float(expected_range[1])
            )
            visible_range_match += range_match
        elif boundary_state == "no_interface":
            no_interface_count += 1
            no_interface_numeric += oil_y is not None
        foam_hint = str(annotation.get("foam_hint", "unclear"))
        foam_hint_match: bool | None = None
        if foam_hint in {"present", "absent"}:
            foam_evaluated += 1
            foam_hint_match = foam_present is (foam_hint == "present")
            foam_match += foam_hint_match
        details.append(
            {
                "annotation_timestamp_sec": timestamp,
                "sample_timestamp_sec": row["timestamp_sec"],
                "boundary_state": boundary_state,
                "expected_oil_y_range": expected_range,
                "resolved_oil_y": oil_y,
                "range_match": range_match,
                "foam_hint": foam_hint,
                "resolved_foam_present": foam_present,
                "foam_hint_match": foam_hint_match,
            }
        )
    return {
        "annotation_count": len(details),
        "visible_count": visible_count,
        "visible_numeric_count": visible_numeric,
        "visible_range_match_count": visible_range_match,
        "no_interface_count": no_interface_count,
        "no_interface_numeric_count": no_interface_numeric,
        "foam_evaluated_count": foam_evaluated,
        "foam_match_count": foam_match,
        "details": details,
    }


def _user_truth_audit(
    root: Path,
    sample: str,
    rows: list[dict[str, object]],
) -> dict[str, object]:
    truth = JsonTruthRepository().load(
        root / "sample" / f"{sample}.oiltruth"
    ).truth_set
    start, end = QUALIFICATION_WINDOWS[sample]
    cases: list[dict[str, object]] = []
    errors: list[float] = []
    for annotation in truth.annotations:
        if annotation.disposition.value == "unusable" or annotation.oil_boundary is None:
            continue
        timestamp = float(annotation.actual_decoded_timestamp_sec)
        if timestamp < start - 1e-6 or timestamp > end + 0.26:
            continue
        row = _nearest(rows, timestamp)
        resolved = row["oil_y"]
        expected = float(annotation.oil_boundary.source_frame_y)
        error = None if resolved is None else abs(float(resolved) - expected)
        if error is not None:
            errors.append(error)
        cases.append(
            {
                "frame_index": int(annotation.frame_index),
                "truth_timestamp_sec": timestamp,
                "sample_timestamp_sec": row["timestamp_sec"],
                "truth_oil_y": expected,
                "resolved_oil_y": resolved,
                "absolute_error_px": error,
            }
        )
    return {
        "case_count": len(cases),
        "numeric_count": len(errors),
        "mean_absolute_error_px": (
            None if not errors else sum(errors) / len(errors)
        ),
        "maximum_absolute_error_px": None if not errors else max(errors),
        "cases": cases,
        "authority_note": (
            "Checked-in user truth is regression evidence. Direct-image conflicts, "
            "including the explanatory-overlay Base anchors, remain visually censored."
        ),
    }


def _sequence_audit(rows: list[dict[str, object]]) -> dict[str, object]:
    numeric = [row for row in rows if row["oil_y"] is not None]
    missing_same_frame = sum(
        "SEQUENCE_SAME_FRAME_CANDIDATE" not in row["flags_set"]
        for row in numeric
    )
    return {
        "state_counts": dict(Counter(str(row["fill_state"]) for row in rows)),
        "numeric_count": len(numeric),
        "numeric_without_same_frame_provenance": missing_same_frame,
        "foam_numeric_count": sum(row["foam_y"] is not None for row in rows),
        "sequence_unavailable_count": sum(
            "SEQUENCE_UNAVAILABLE" in row["flags_set"] for row in rows
        ),
    }


def run_r5_replay(
    *,
    root: Path | None = None,
    output_root: Path | None = None,
    verify_fingerprints: bool = True,
) -> dict[str, object]:
    root = repository_root() if root is None else Path(root)
    output_root = (
        root / "sample" / "output" / "s11-r5-sequence-first"
        if output_root is None
        else Path(output_root)
    )
    manifest = run_replay(
        root=root,
        output_root=output_root,
        verify_accepted_counts=verify_fingerprints,
        expected_numeric_oil_counts=R5_NUMERIC_OIL_COUNTS,
        expected_tracking_fingerprints=R5_TRACKING_FINGERPRINTS,
        run_label="S11-R5",
        run_note="Sequence-first Oil/state and independent Foam episode replay",
        manifest_schema="s11-r5-sequence-first-replay-v1",
    )
    audits: dict[str, object] = {}
    for summary in manifest["samples"]:
        sample = str(summary["sample"])
        rows = _tracking_rows(Path(str(summary["bundle"])))
        sequence = _sequence_audit(rows)
        if sequence["numeric_without_same_frame_provenance"]:
            raise AssertionError(f"{sample}: numeric Oil lacks same-frame provenance")
        audits[sample] = {
            "sequence": sequence,
            "provisional_visual": _provisional_audit(root, sample, rows),
            "user_truth": _user_truth_audit(root, sample, rows),
        }

    if audits["base_sample_1"]["sequence"]["numeric_count"] != 0:
        raise AssertionError("Base explanatory-overlay window became numeric")
    if audits["base_sample_1"]["sequence"]["foam_numeric_count"] != 0:
        raise AssertionError("Base Foam-absent window published Foam")
    if audits["sample2"]["sequence"]["foam_numeric_count"] != 0:
        raise AssertionError("Sample2 unclear/static appearance published Foam")
    sample3_rows = _tracking_rows(
        Path(
            next(
                str(summary["bundle"])
                for summary in manifest["samples"]
                if summary["sample"] == "sample3"
            )
        )
    )
    black_row = _nearest(sample3_rows, 67.0)
    if black_row["fill_state"] != "UNKNOWN_REVIEW" or black_row["oil_y"] is not None:
        raise AssertionError("Sample3 black/reframe barrier did not resolve UNKNOWN")

    manifest["r4_numeric_oil_reference"] = R4_NUMERIC_OIL_REFERENCE
    manifest["r5_visual_audit"] = audits
    manifest["secure_windows_status"] = (
        "NOT_RUN_PRIVATE_VIDEO_UNAVAILABLE_IN_THIS_CHECKOUT"
    )
    manifest_path = output_root / "replay_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay and visually reconcile the S11-R5 sequence resolver."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("sample/output/s11-r5-sequence-first"),
    )
    parser.add_argument("--skip-fingerprint-check", action="store_true")
    args = parser.parse_args()
    manifest = run_r5_replay(
        output_root=args.output_root,
        verify_fingerprints=not args.skip_fingerprint_check,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
