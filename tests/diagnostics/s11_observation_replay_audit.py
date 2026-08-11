from __future__ import annotations

"""Shared visual/truth audit helpers for versioned S11 observation replays."""

import csv
import json
import math
from collections import Counter
from pathlib import Path

from oil_tracker.adapters.storage.json_truth_repository import JsonTruthRepository
from tests.diagnostics.s11_report_observability_replay import QUALIFICATION_WINDOWS


def tracking_rows(bundle: Path) -> list[dict[str, object]]:
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


def nearest(
    rows: list[dict[str, object]],
    timestamp_sec: float,
) -> dict[str, object]:
    return min(
        rows,
        key=lambda row: abs(float(row["timestamp_sec"]) - timestamp_sec),
    )


def provisional_audit(
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
        row = nearest(rows, timestamp)
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


def user_truth_audit(
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
        row = nearest(rows, timestamp)
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


def sequence_audit(rows: list[dict[str, object]]) -> dict[str, object]:
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


def _optional_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    number = float(value)
    return number if math.isfinite(number) else None
