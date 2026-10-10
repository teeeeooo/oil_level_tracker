"""Read numeric Oil cadence from saved O1 replay CSV rows; never runs a detector.

This companion uses the existing replay format, not a new truth/label format.
It cannot certify physical cadence: validity flags are not reviewed identity,
and a captured span is not automatically a visible moving interval.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_interface_shadow_evaluation as evaluation

TARGET_SECONDS = 1.0
REPLAY_SCHEMA = "s11-o1-window-equality-v1"


def _csv_number(value, name):
    evaluation.require(isinstance(value, str), f"{name}: CSV text required")
    return evaluation.number(float(value), name)


def summarize_rows(rows):
    """Measure each Glass in input order; never sort away a broken timeline."""
    evaluation.require(isinstance(rows, list) and rows, "captured rows required")
    groups = defaultdict(list)
    for row in rows:
        glass = evaluation.text(row["glass_id"], "glass_id")
        frame_text = row["frame_index"]
        evaluation.require(isinstance(frame_text, str) and frame_text.isascii()
                           and frame_text.isdecimal(), "frame_index: integer CSV text required")
        frame = int(frame_text)
        timestamp = _csv_number(row["timestamp_sec"], "timestamp_sec")
        evaluation.require(timestamp >= 0, "negative timestamp")
        validity = row["oil_is_valid"]
        evaluation.require(validity in ("True", "False"), "explicit Oil validity required")
        raw_y = row["raw_oil_air_level_y"]
        y = None if raw_y == "" else _csv_number(raw_y, "raw Oil Y")
        prior = groups[glass]
        if prior:
            evaluation.require(timestamp > prior[-1]["timestamp_sec"]
                               and frame > prior[-1]["frame_index"],
                               "frame and source time must increase within each Glass")
        prior.append({"frame_index": frame, "timestamp_sec": timestamp,
                      "source_y": y, "oil_is_valid": validity == "True",
                      "numeric": validity == "True" and y is not None})

    results = []
    for glass, points in groups.items():
        indices = [i for i, point in enumerate(points) if point["numeric"]]
        start, end = points[0]["timestamp_sec"], points[-1]["timestamp_sec"]
        gaps = [{"start_frame": points[a]["frame_index"],
                 "end_frame": points[b]["frame_index"],
                 "start_sec": points[a]["timestamp_sec"],
                 "end_sec": points[b]["timestamp_sec"],
                 "elapsed_sec": points[b]["timestamp_sec"] - points[a]["timestamp_sec"],
                 "intervening_unavailable_rows": b - a - 1}
                for a, b in zip(indices, indices[1:])]
        durations = [gap["elapsed_sec"] for gap in gaps]
        # End spans are censored, not fictitious pairs of numeric observations.
        leading = trailing = None
        if indices:
            first, last = indices[0], indices[-1]
            leading = {"row_count": first, "start_sec": start,
                       "end_sec": points[first]["timestamp_sec"],
                       "elapsed_sec": points[first]["timestamp_sec"] - start}
            trailing = {"row_count": len(points) - last - 1,
                        "start_sec": points[last]["timestamp_sec"], "end_sec": end,
                        "elapsed_sec": end - points[last]["timestamp_sec"]}
        results.append({
            "glass_id": glass, "captured_span_sec": [start, end],
            "row_count": len(points), "numeric_observation_count": len(indices),
            "unavailable_row_count": len(points) - len(indices),
            "invalid_numeric_row_count": sum(p["source_y"] is not None
                                               and not p["oil_is_valid"] for p in points),
            "numeric_cadence_status": "MEASURED" if gaps else "NO_PAIRS",
            "pair_count": len(gaps), "maximum_interval_sec": max(durations, default=None),
            "p95_interval_sec": evaluation.deterministic_percentile(durations, .95),
            "pairs_within_target": sum(dt <= TARGET_SECONDS for dt in durations),
            "pairs_over_target": sum(dt > TARGET_SECONDS for dt in durations),
            "leading_unavailable": leading, "trailing_unavailable": trailing,
            "all_unavailable_span_sec": [start, end] if not indices else None,
            "observations": points, "intervals": gaps,
            "physical_cadence": {"status": "NOT_EVALUATED",
                "reason": "No joined same-interface scalar qualification and visible-moving interval review; numeric validity is not physical identity."},
        })
    return results


def measure_saved(paths):
    resolved = [Path(path).resolve() for path in paths]
    evaluation.require(resolved and len(set(resolved)) == len(resolved),
                       "distinct saved replay paths required")
    pins = {path: evaluation.sha256_file(path) for path in resolved}
    reports = []
    for path in resolved:
        saved = evaluation.read_json(path)
        evaluation.require(saved["schema_version"] == REPLAY_SCHEMA, "unsupported saved replay")
        reports.append({"path": str(path), "sha256": pins[path],
                        "sample": saved["sample"], "detector_version": saved["version"],
                        "recorded_source_sha256": saved["source_sha256"],
                        "tracking_fingerprint": saved["fingerprint"],
                        "glasses": summarize_rows(saved["tracking_data.csv"])})
    evaluation.require(all(evaluation.sha256_file(path) == sha for path, sha in pins.items()),
                       "saved replay changed during measurement")
    return {"schema_version": "s11-saved-numeric-cadence-v1",
            "comparison_scope": "unverified_numeric_cadence",
            "target_seconds": TARGET_SECONDS,
            "target_owner": "docs/50-diagnostics/s11/2026-10-10-temporal-usefulness-reply.json",
            "tool_sha256": evaluation.sha256_file(Path(__file__)),
            "physical_acceptance": "NOT_EVALUATED", "saved_replays": reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saved", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = measure_saved(args.saved)
    evaluation.write_new(args.output, report)
    print("Saved numeric cadence measured; physical acceptance NOT_EVALUATED.")


if __name__ == "__main__":
    main()
