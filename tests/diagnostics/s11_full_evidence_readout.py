"""FER-1: per frame, where the image FULL evidence stops on its way to a published FULL. Read-only.

Design input for path F (docs/50-diagnostics/s11/2026-10-27-owner-free-full-review.md, OFF-1). The sequence's `full`
state node is gated three times before selection:
  gate 1: the frame outcome is no-interface (`oil_decision_status` = no_interface_accepted). Only then does
          `oil_runtime_metrics` carry `oil_no_interface_full_likelihood`; otherwise it is 0.0. The frame becomes
          no-interface when absence >= 0.58 and >= 0.10 above the best boundary hypothesis;
  gate 2: that FULL likelihood reaches the state evidence threshold (0.58), which creates the `full` node;
  gate 3: the lifecycle does not reduce the layer to UNKNOWN (`allowed_mode` hard_gate is the empty allowed set).
Per frame it reports the raw outcome, the absence and boundary likelihoods, the FULL and EMPTY likelihoods, the first
gate that fails, the lifecycle phase, reason and allowed mode, the resolved kind, the published fill state and the
source of a published FULL (image node or top-exit), the eligible Foam fronts and the admitted Oil rows. For a
boundary-accepted frame the absence likelihood is not traced (the outcome reports 0.0). It reads a saved FULL-debug
bundle (the record's frame metrics and its sequence snapshot), or runs a local control through the comparison runner
and reads its completed detections. It changes no detector behaviour.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path

ABSENCE_MINIMUM = 0.58  # _positive_no_interface_is_authoritative
ABSENCE_MARGIN = 0.10
STATE_MIN_EVIDENCE = 0.58  # OilObservationResolverConfig.state_min_evidence
NO_INTERFACE = "no_interface_accepted"
RUN_LENGTH = 3  # the reading unit for a sustained `full` node (OFF-1's K is open)


def _number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _optional(value) -> float | None:
    try:
        return None if value is None else round(float(value), 3)
    except (TypeError, ValueError):
        return None


def _kind(candidate: dict) -> str:
    kind = candidate.get("kind")
    return str(getattr(kind, "value", kind))


def _y(candidate: dict) -> float | None:
    value = candidate.get("canonical_y", candidate.get("y"))
    return None if value is None else float(value)


def _admitted(value) -> bool:
    return value is True or value == 1 or value == 1.0


def frame_row(time: float, frame: int, fill_state, published_y, metrics: dict, candidates: list[dict]) -> dict:
    """One frame's FULL evidence and the first gate it fails.

    ``metrics`` holds the frame metrics (``oil_*``) and the sequence metrics (``sequence_*``). ``candidates`` are
    completed candidates (features carry ``sequence_*``) or sequence-snapshot candidates (top-level keys).
    """
    status = metrics.get("oil_decision_status")
    absence = _number(metrics.get("oil_no_interface_score"))
    boundary = _number(metrics.get("oil_boundary_score"))
    full = _number(metrics.get("oil_no_interface_full_likelihood"))
    empty = _number(metrics.get("oil_no_interface_empty_likelihood"))
    diagnostics = metrics.get("sequence_material_phase_diagnostics") or {}
    allowed_mode = diagnostics.get("allowed_mode")
    resolved = metrics.get("sequence_resolved_kind")
    fill = str(getattr(fill_state, "value", fill_state))
    full_node = full >= STATE_MIN_EVIDENCE
    if status != NO_INTERFACE:
        if status == "ambiguous":
            closed = "absence_low" if absence < ABSENCE_MINIMUM else "absence_margin"
        else:
            closed = str(status)
        gate = f"gate1:{closed}"
    elif not full_node:
        gate = "gate2:full_below"
    elif allowed_mode == "hard_gate":
        gate = "gate3:hard_gate"
    elif resolved != "full":
        gate = f"selection:{resolved}"
    else:
        gate = "selected"
    foam, admitted = [], []
    for candidate in candidates:
        features = candidate.get("features") or {}
        y = _y(candidate)
        if y is None:
            continue
        if _kind(candidate) == "foam_front" and _number(
                candidate.get("sequence_foam_eligible", features.get("sequence_foam_eligible"))) >= 0.5:
            foam.append(y)
        if _kind(candidate) == "oil_air" and _admitted(
                candidate.get("tracklet_admitted", features.get("sequence_tracklet_admitted"))):
            admitted.append(y)
    full_published = fill.startswith("FULL")
    return dict(
        time=round(time, 3), frame=frame, fill=fill, published_y=_optional(published_y),
        status=status, outcome_reason=metrics.get("oil_decision_reason"),
        absence=round(absence, 3), boundary=round(boundary, 3), absence_margin=round(absence - boundary, 3),
        absence_reason=metrics.get("oil_no_interface_reason"),
        outcome_y=_optional(metrics.get("oil_temporal_projected_source_y")),
        full=round(full, 3), empty=round(empty, 3), full_node=full_node, gate=gate,
        phase=metrics.get("sequence_material_phase"), phase_reason=metrics.get("sequence_material_phase_reason"),
        allowed_mode=allowed_mode, resolved=resolved,
        full_source=("top_exit" if allowed_mode == "state_only" else "image_node") if full_published else None,
        foam_fronts=sorted(set(foam)), admitted_oil=sorted(set(admitted)))


def _runs(rows: list[dict]) -> list[tuple[int, int]]:
    """(start index, length) of each run of consecutive rows with a `full` node."""
    runs, start = [], None
    for index, row in enumerate(rows + [{"full_node": False}]):
        if row["full_node"] and start is None:
            start = index
        elif not row["full_node"] and start is not None:
            runs.append((start, index - start))
            start = None
    return runs


def summary(rows: list[dict]) -> dict:
    def count(key) -> dict:
        found: dict[str, int] = {}
        for row in rows:
            found[str(row[key])] = found.get(str(row[key]), 0) + 1
        return dict(sorted(found.items()))

    runs = _runs(rows)
    sustained = [(rows[s]["time"], length, any(rows[i]["foam_fronts"] for i in range(s, s + length)))
                 for s, length in runs if length >= RUN_LENGTH]
    longest = max(runs, key=lambda item: item[1], default=None)
    return {"rows": len(rows), "status": count("status"), "gate": count("gate"),
            "full_node": sum(r["full_node"] for r in rows),
            "published_full": count("full_source") if any(r["full_source"] for r in rows) else {},
            "longest_run": None if longest is None else {"start": rows[longest[0]]["time"], "length": longest[1]},
            "sustained_runs": [{"start": t, "length": n, "foam_in_run": f} for t, n, f in sustained]}


def from_bundle(bundle: Path, glass: str, window: tuple[float, float]) -> tuple[list[dict], list[str]]:
    from tests.diagnostics.s11_cadence_field import _rows
    from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop

    table = {int(row["frame_index"]): row for row in _rows(bundle, glass)
             if window[0] <= float(row["timestamp_sec"]) <= window[1]}
    trace = bundle / "debug" / "debug_trace.jsonl"
    if not trace.is_file():
        _stop(f"no debug trace in {bundle}")
    records, run_ids = {}, set()
    with trace.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("glass_name") == glass and record.get("frame_index") in table:
                if "sequence" not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                records[record["frame_index"]] = record
                run_ids.add(str(record.get("run_id")))
    rows = []
    for frame, row in sorted(table.items()):
        record = records.get(frame)
        if record is None:
            _stop(f"no trace record for {glass} frame {frame}")
        sequence = record["sequence"]
        metrics = {**(record.get("state") or {}), **(sequence.get("state") or {})}
        rows.append(frame_row(float(row["timestamp_sec"]), frame, row["fill_state"],
                              _number(row["raw_oil_air_level_y"], None), metrics, sequence.get("candidates") or []))
    return rows, sorted(run_ids)


@contextmanager
def _local_capture():
    """Add this readout's per-frame row to the comparison runner's owner readout."""
    from tests.diagnostics import s11_initial_full_comparison as comparison

    original = comparison._owner_readout

    def extended(detection: dict) -> dict:
        frame = original(detection)
        frame["fer1"] = frame_row(0.0, detection["frame_index"], detection["fill_state"],
                                  detection["raw_oil_air_level_y"], detection["debug_metrics"], detection["candidates"])
        return frame

    comparison._owner_readout = extended
    try:
        yield comparison
    finally:
        comparison._owner_readout = original


def run_local(work: Path, roi_inputs: Path, sample: str, *, original_recipe: bool, initial_state: str) -> Path:
    """Run one control (E4 comparison mode, reference arm read) and keep its comparison file."""
    with _local_capture() as comparison:
        comparison.compare(work, roi_inputs, sample, fill_owner_colocation_comparison=True, owner_readout=True,
                           original_recipe=original_recipe, initial_state=initial_state)
    return work / "comparison.json"


def from_comparison(path: Path, arm: str) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    variant = data["variants"][arm]
    rows = []
    for table_row, owner in zip(variant["rows"], variant["owner_readout"], strict=True):
        row = dict(owner["fer1"])
        row["time"] = round(float(table_row["timestamp_sec"]), 3)
        rows.append(row)
    return rows


FRAME_FIELDS = ("time", "fill", "published_y", "status", "absence", "boundary", "absence_margin", "outcome_y",
                "full", "empty", "gate", "phase", "phase_reason", "allowed_mode", "resolved", "full_source")


def _text(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "T" if value else "F"
    if isinstance(value, list):
        return ";".join(f"{v:g}" for v in value) or "-"
    return str(value)


def print_result(label: str, result: dict, *, frame_lines: bool) -> None:
    s = result["summary"]
    longest = s["longest_run"]
    print(f"full evidence readout {label} | rows {s['rows']} | full node {s['full_node']} | longest run "
          + ("-" if longest is None else f"{longest['length']} from {longest['start']:.3f}")
          + f" | runs >= {RUN_LENGTH}: {len(s['sustained_runs'])}")
    print("status " + " ".join(f"{k}={v}" for k, v in s["status"].items()))
    print("gate " + " ".join(f"{k}={v}" for k, v in s["gate"].items()))
    print("published full " + (" ".join(f"{k}={v}" for k, v in s["published_full"].items()) or "-"))
    for run in s["sustained_runs"]:
        print(f"run start {run['start']:.3f} | length {run['length']} | foam in run {_text(run['foam_in_run'])}")
    if frame_lines:
        print("-- frames: " + " | ".join(FRAME_FIELDS) + " | foam fronts | admitted oil --")
        for row in result["frames"]:
            print(f"{row['time']:.3f} | " + " | ".join(_text(row[f]) for f in FRAME_FIELDS[1:])
                  + f" | {_text(row['foam_fronts'])} | {_text(row['admitted_oil'])}")


def _write(out: Path, name: str, result: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    path = out / name
    path.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    bundle = sub.add_parser("bundle", help="read a saved FULL-debug bundle")
    bundle.add_argument("--bundle", type=Path, required=True)
    bundle.add_argument("--glass-name", default="BASE")
    bundle.add_argument("--start", type=float, default=0.0)
    bundle.add_argument("--end", type=float, default=1e9)
    bundle.add_argument("--no-frames", action="store_true", help="print only the summary")
    bundle.add_argument("--out", type=Path, required=True)
    local = sub.add_parser("local", help="run one local control and read its reference arm")
    local.add_argument("--work", type=Path, required=True)
    local.add_argument("--roi-inputs", type=Path, required=True)
    local.add_argument("--sample", required=True)
    local.add_argument("--original-recipe", action="store_true")
    local.add_argument("--initial-state", default="full")
    args = parser.parse_args(argv)
    if args.mode == "bundle":
        rows, run_ids = from_bundle(args.bundle, args.glass_name, (args.start, args.end))
        label = f"{args.glass_name} {args.start}-{args.end} s | bundle {args.bundle} | run_id {','.join(run_ids)}"
        result = {"source": label, "summary": summary(rows), "frames": rows}
        print_result(label, result, frame_lines=not args.no_frames)
        _write(args.out, f"full_evidence_readout_{args.glass_name}.json", result)
    else:
        path = run_local(args.work, args.roi_inputs, args.sample, original_recipe=args.original_recipe,
                         initial_state=args.initial_state)
        rows = from_comparison(path, "top_exit")
        label = f"{args.sample} local | arm top_exit | {path}"
        result = {"source": label, "summary": summary(rows), "frames": rows}
        print_result(label, result, frame_lines=True)
        _write(args.work, "full_evidence_readout.json", result)


if __name__ == "__main__":
    main()
