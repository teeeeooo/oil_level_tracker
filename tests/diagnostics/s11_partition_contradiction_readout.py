"""FPC-1: which post-track Oil demotions rest on texture conflict alone, and how they sit relative to Foam. Read-only.

E1 design input (docs/20-architecture/s11-physical-interface-evidence-repair-design.md, the October 27 E1 draft).
Per frame it lists the Oil candidates whose initial tier was eligible and whose post-track tier is `CANDIDATE_ONLY` with
recurring-row opposition >= 0.60. For each it recomputes the inputs of `recurrence_hard_contradiction` with the
production evidence normaliser (material-texture conflict, artifact signature, optics, opposed-material identity) and
marks it TEXTURE-ONLY when texture conflict is the only one present. For those it reports the two candidate E1 scopes:
  A: R14's ordered-lower flag (`sequence_ordered_lower`; the Foam seed age is not traced);
  B: an eligible Foam-front candidate of the same frame above the row (`sequence_foam_eligible` >= 0.5).
It also lists the same-frame structural partition peers (material path, terminal support >= 0.60, layer topology < 0.5,
at least 8 px away; the rule's local-quality comparison is not traced). It reads a saved FULL-debug bundle (the sequence
snapshot joined to the frame's detector candidates, which are written before sequence resolution), or runs a local
control through the comparison runner and reads its completed detections. It changes no detector behaviour.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

REJECT_OPPOSITION = 0.60  # recurring_track_reject_opposition
TEXTURE_LIMIT = 0.60  # recurrence_hard_contradiction
ARTIFACT_LIMIT = 0.44
OPTICS_LIMIT = 0.46
TERMINAL_MINIMUM = 0.60  # superior partition: peer terminal support
TOPOLOGY_LIMIT = 0.50
MINIMUM_SEPARATION_PX = 8.0
TIERS = {0: "HARD_INVALID", 1: "CANDIDATE_ONLY", 2: "CONTINUATION_ELIGIBLE", 3: "ANCHOR_ELIGIBLE"}


def _number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _tier(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _kind(candidate: dict) -> str:
    kind = candidate.get("kind")
    return str(getattr(kind, "value", kind))


def _y(candidate: dict) -> float | None:
    value = candidate.get("canonical_y", candidate.get("y"))
    return None if value is None else float(value)


def contradiction(candidate: dict) -> dict:
    """The inputs of ``recurrence_hard_contradiction``, from the production evidence normaliser."""
    from oil_tracker.adapters.vision.oil_candidate_evidence import OilCandidateEvidence

    features = candidate.get("features") or {}
    evidence = OilCandidateEvidence.from_candidate(SimpleNamespace(
        features=features, penalties=candidate.get("penalties") or {}, feature_score=candidate.get("feature_score")))
    opposed = features.get("sequence_phase_identity") == "opposed_material"
    texture = evidence.material_texture_conflict >= TEXTURE_LIMIT
    artifact = evidence.artifact_signature >= ARTIFACT_LIMIT
    optics = evidence.optics_opposition >= OPTICS_LIMIT
    return dict(texture=round(evidence.material_texture_conflict, 3),
                artifact_signature=round(evidence.artifact_signature, 3),
                optics=round(evidence.optics_opposition, 3), opposed_material=opposed,
                texture_only=texture and not (artifact or optics or opposed),
                material_path=evidence.material_path, terminal=round(evidence.terminal_support, 3),
                topology=round(evidence.material_layer_topology, 3))


def frame_rows(time: float, frame: int, candidates: list[dict]) -> dict:
    """One frame's demoted Oil candidates with their contradiction class, scopes and partition peers."""
    oil = [(c, _y(c)) for c in candidates if _kind(c) == "oil_air" and _y(c) is not None]
    foam = sorted({_y(c) for c in candidates if _kind(c) == "foam_front" and _y(c) is not None
                   and _number((c.get("features") or {}).get("sequence_foam_eligible")) >= 0.5})
    peers = []
    for candidate, y in oil:
        fields = contradiction(candidate)
        if fields["material_path"] and fields["terminal"] >= TERMINAL_MINIMUM and fields["topology"] < TOPOLOGY_LIMIT:
            peers.append((y, (candidate.get("features") or {}).get("sequence_tracklet_id") or ""))
    demoted = []
    for candidate, y in oil:
        features = candidate.get("features") or {}
        initial = _tier(features.get("sequence_initial_authority_tier"))
        post = _tier(features.get("sequence_post_track_authority_tier"))
        opposition = _number(features.get("sequence_track_opposition"))
        if not (initial is not None and initial >= 2 and post == 1 and opposition >= REJECT_OPPOSITION):
            continue
        fields = contradiction(candidate)
        above = [f for f in foam if f < y]
        demoted.append(dict(
            y=y, source=candidate.get("source"), tracklet=features.get("sequence_tracklet_id") or "",
            initial=TIERS.get(initial), opposition=round(opposition, 3),
            phase_identity=features.get("sequence_phase_identity"),
            ordered_lower=_number(features.get("sequence_ordered_lower")) >= 0.5,
            foam_material_identity=round(_number(features.get("sequence_foam_material_identity")), 3),
            **{k: fields[k] for k in ("texture", "artifact_signature", "optics", "opposed_material", "texture_only")},
            scope_a=fields["texture_only"] and _number(features.get("sequence_ordered_lower")) >= 0.5,
            scope_b=fields["texture_only"] and bool(above),
            foam_above=above[-1] if above else None,
            peers=sorted(p for p in peers if abs(p[0] - y) >= MINIMUM_SEPARATION_PX)))
    demoted.sort(key=lambda item: (item["y"], str(item["source"])))
    return dict(time=round(time, 3), frame=frame, foam_fronts=foam, demoted=demoted)


def summary(frames: list[dict]) -> dict:
    rows = [row for frame in frames for row in frame["demoted"]]
    return {"frames": len(frames), "demoted": len(rows), "texture_only": sum(r["texture_only"] for r in rows),
            "scope_a": sum(r["scope_a"] for r in rows), "scope_b": sum(r["scope_b"] for r in rows),
            "frames_with_scope_a": sum(any(r["scope_a"] for r in f["demoted"]) for f in frames),
            "frames_with_scope_b": sum(any(r["scope_b"] for r in f["demoted"]) for f in frames)}


TIER_NUMBERS = {name: number for number, name in TIERS.items()}
SNAPSHOT_FEATURES = {  # sequence snapshot key -> the completed candidate's feature
    "initial_authority": "sequence_initial_authority_tier", "post_track_authority": "sequence_post_track_authority_tier",
    "track_opposition": "sequence_track_opposition", "phase_identity": "sequence_phase_identity",
    "ordered_lower": "sequence_ordered_lower", "tracklet_id": "sequence_tracklet_id",
    "sequence_foam_eligible": "sequence_foam_eligible",
}


def merge_record(record: dict) -> tuple[list[dict], int, int]:
    """Completed candidates from one trace record.

    The record's top-level candidates are the frame's detector candidates, written before sequence resolution; the
    sequence snapshot holds the resolved tiers, opposition and identity. Each snapshot candidate is joined to its
    detector candidate on (kind, source, canonical Y) for the raw features and penalties. Returns the merged candidates
    and the counts of missing and ambiguous joins (those snapshot candidates are left out).
    """
    raw: dict[tuple, list[dict]] = {}
    for candidate in record.get("candidates") or ():
        if candidate.get("canonical_y") is not None:
            raw.setdefault((candidate.get("kind"), candidate.get("source"), float(candidate["canonical_y"])),
                           []).append(candidate)
    merged, missing, ambiguous = [], 0, 0
    for snap in (record.get("sequence") or {}).get("candidates") or ():
        if snap.get("canonical_y") is None:
            continue
        matches = raw.get((snap.get("kind"), snap.get("source"), float(snap["canonical_y"])), [])
        if len(matches) != 1:
            missing += not matches
            ambiguous += len(matches) > 1
            continue
        features = dict(matches[0].get("features") or {})
        for key, feature in SNAPSHOT_FEATURES.items():
            value = snap.get(key)
            if key in ("initial_authority", "post_track_authority"):
                value = TIER_NUMBERS.get(value)
            if value is None:
                features.pop(feature, None)
            else:
                features[feature] = value
        merged.append({**matches[0], "features": features})
    return merged, missing, ambiguous


def from_bundle(bundle: Path, glass: str, window: tuple[float, float]) -> tuple[list[dict], list[str], dict]:
    from tests.diagnostics.s11_cadence_field import _rows
    from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop

    times = {int(row["frame_index"]): float(row["timestamp_sec"]) for row in _rows(bundle, glass)
             if window[0] <= float(row["timestamp_sec"]) <= window[1]}
    trace = bundle / "debug" / "debug_trace.jsonl"
    if not trace.is_file():
        _stop(f"no debug trace in {bundle}")
    frames, run_ids, joins = [], set(), {"missing": 0, "ambiguous": 0}
    with trace.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("glass_name") == glass and record.get("frame_index") in times:
                if "sequence" not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                frame = record["frame_index"]
                candidates, missing, ambiguous = merge_record(record)
                joins["missing"] += missing
                joins["ambiguous"] += ambiguous
                frames.append(frame_rows(times[frame], frame, candidates))
                run_ids.add(str(record.get("run_id")))
    frames.sort(key=lambda item: item["frame"])
    return frames, sorted(run_ids), joins


@contextmanager
def _local_capture():
    """Add this readout's per-frame rows to the comparison runner's owner readout."""
    from tests.diagnostics import s11_initial_full_comparison as comparison

    original = comparison._owner_readout

    def extended(detection: dict) -> dict:
        frame = original(detection)
        frame["fpc1"] = frame_rows(0.0, detection["frame_index"], detection["candidates"])
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
    frames = []
    for row, owner in zip(variant["rows"], variant["owner_readout"], strict=True):
        frame = dict(owner["fpc1"])
        frame["time"] = round(float(row["timestamp_sec"]), 3)
        frames.append(frame)
    return frames


ROW_FIELDS = ("y", "source", "tracklet", "initial", "opposition", "phase_identity", "ordered_lower",
              "foam_material_identity", "texture", "artifact_signature", "optics", "opposed_material", "texture_only",
              "scope_a", "scope_b", "foam_above")


def _text(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "T" if value else "F"
    return str(value)


def parse_marks(text: str | None) -> list[tuple[float, float]]:
    if not text:
        return []
    return [(float(t), float(y)) for t, y in (item.split(":") for item in text.split(",") if item)]


def _ys(values) -> str:
    return ";".join(f"{v:g}" for v in sorted(set(values))) or "-"


def print_result(label: str, result: dict, *, marks: list[tuple[float, float]], near: float,
                 frame_lines: bool) -> None:
    """The summary, one line per frame (scope-A and scope-B row Ys) and, near each mark, every demoted row."""
    s = result["summary"]
    print(f"partition contradiction readout {label} | frames {s['frames']} | demoted {s['demoted']} | "
          f"texture-only {s['texture_only']} | scope A {s['scope_a']} ({s['frames_with_scope_a']} frames) | "
          f"scope B {s['scope_b']} ({s['frames_with_scope_b']} frames)")
    if frame_lines:
        print("-- frames: time | demoted | texture-only | eligible foam fronts | scope A ys | scope B ys --")
        for frame in result["frames"]:
            rows = frame["demoted"]
            print(f"{frame['time']:.3f} | {len(rows)} | {sum(r['texture_only'] for r in rows)} | "
                  f"{_ys(frame['foam_fronts'])} | {_ys(r['y'] for r in rows if r['scope_a'])} | "
                  f"{_ys(r['y'] for r in rows if r['scope_b'])}")
    if marks:
        print(f"-- demoted rows within {near} px of a mark: time | mark | " + " | ".join(ROW_FIELDS)
              + " | partition peers (y tracklet) --")
        for mark_time, mark_y in marks:
            frame = min(result["frames"], key=lambda f: abs(f["time"] - mark_time), default=None)
            if frame is None or abs(frame["time"] - mark_time) > 0.25:
                print(f"{mark_time:.3f} | {mark_y} | no frame")
                continue
            for row in frame["demoted"]:
                if abs(row["y"] - mark_y) <= near:
                    peers = "; ".join(f"{y:g} {t or '-'}" for y, t in row["peers"]) or "-"
                    print(f"{frame['time']:.3f} | {mark_y} | " + " | ".join(_text(row[f]) for f in ROW_FIELDS)
                          + f" | {peers}")


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
    bundle.add_argument("--marks", help="comma-separated time:y pairs; demoted rows near them are printed in full")
    bundle.add_argument("--near", type=float, default=32.0)
    bundle.add_argument("--no-frames", action="store_true", help="print only the summary (and marks)")
    bundle.add_argument("--out", type=Path, required=True)
    local = sub.add_parser("local", help="run one local control and read its reference arm")
    local.add_argument("--work", type=Path, required=True)
    local.add_argument("--roi-inputs", type=Path, required=True)
    local.add_argument("--sample", required=True)
    local.add_argument("--original-recipe", action="store_true")
    local.add_argument("--initial-state", default="full")
    local.add_argument("--marks")
    local.add_argument("--near", type=float, default=32.0)
    args = parser.parse_args(argv)
    if args.mode == "bundle":
        frames, run_ids, joins = from_bundle(args.bundle, args.glass_name, (args.start, args.end))
        label = (f"{args.glass_name} {args.start}-{args.end} s | bundle {args.bundle} | run_id {','.join(run_ids)} | "
                 f"joins missing {joins['missing']} ambiguous {joins['ambiguous']}")
        result = {"source": label, "summary": summary(frames), "frames": frames}
        print_result(label, result, marks=parse_marks(args.marks), near=args.near, frame_lines=not args.no_frames)
        _write(args.out, f"partition_contradiction_readout_{args.glass_name}.json", result)
    else:
        path = run_local(args.work, args.roi_inputs, args.sample, original_recipe=args.original_recipe,
                         initial_state=args.initial_state)
        frames = from_comparison(path, "top_exit")
        label = f"{args.sample} local | arm top_exit | {path}"
        result = {"source": label, "summary": summary(frames), "frames": frames}
        print_result(label, result, marks=parse_marks(args.marks), near=args.near, frame_lines=True)
        _write(args.work, "partition_contradiction_readout.json", result)


if __name__ == "__main__":
    main()
