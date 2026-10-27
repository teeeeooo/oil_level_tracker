"""Owner-above readout: single-owner fill frames with an admitted non-owner interface above the owner. Read-only.

E2 design input (docs/20-architecture/s11-physical-interface-evidence-repair-design.md, the October 27 E2 draft).
Per row whose lifecycle decision allows fill owners (`FILL_MOTION_OWNER`, `FILL_PHASE_REENTRY`,
`FILL_CURRENT_ANCHOR_HANDOFF`, the single owner of `FILL_CHAIN_AMBIGUOUS`, `FILL_OWNER_COLOCATED`) and that publishes
numeric Oil, it lists the Oil observations of admitted tracklets outside the allowed set and the owner chain that lie
more than one association step (the Recipe's `temporal_max_jump_px`) above every observation of the allowed owners.
It reads a saved bundle's FULL debug trace or a local comparison file with owner readouts, and runs no detector.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path

SINGLE_OWNER_REASONS = frozenset({
    "FILL_MOTION_OWNER", "FILL_PHASE_REENTRY", "FILL_CURRENT_ANCHOR_HANDOFF", "FILL_CHAIN_AMBIGUOUS",
    "FILL_OWNER_COLOCATED",
})


def hits(frames: list[dict], step_px: float) -> list[dict]:
    """Frames whose allowed owners lie more than ``step_px`` below an admitted non-owner observation.

    Each frame: time, frame, fill, published_y, reason, allowed, owner_chain and candidates
    [{y, tracklet, admitted}]. Only frames that publish numeric Oil under a single-owner reason are read.
    """
    found = []
    for frame in frames:
        if frame["published_y"] is None or frame["reason"] not in SINGLE_OWNER_REASONS or not frame["allowed"]:
            continue
        own = set(frame["allowed"]) | set(frame["owner_chain"])
        owner_ys = [c["y"] for c in frame["candidates"] if c["tracklet"] in frame["allowed"] and c["y"] is not None]
        if not owner_ys:
            continue
        top = min(owner_ys)
        above = sorted((c["y"], c["tracklet"]) for c in frame["candidates"]
                       if c["admitted"] and c["tracklet"] and c["tracklet"] not in own
                       and c["y"] is not None and c["y"] < top - step_px)
        if above:
            found.append({**{k: frame[k] for k in ("time", "frame", "fill", "published_y", "reason")},
                          "allowed": sorted(frame["allowed"]), "owner_top_y": top,
                          "above": [{"y": y, "tracklet": t, "gap_px": round(top - y, 1)} for y, t in above]})
    return found


def _admitted(value) -> bool:
    return value is True or value == 1 or value == 1.0


def _chain(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [item for item in value if item]
    return [item for item in (value or "").split(";") if item]


def from_comparison(path: Path, arm: str) -> list[dict]:
    """Frames from a ``s11_initial_full_comparison --owner-readout`` file (JSON or gzipped JSON)."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        data = json.load(handle)
    variant = data["variants"][arm]
    frames = []
    for row, owner in zip(variant["rows"], variant["owner_readout"], strict=True):
        frames.append(dict(
            time=round(float(row["timestamp_sec"]), 3), frame=row["frame_index"], fill=row["fill_state"],
            published_y=row["raw_oil_air_level_y"], reason=owner["reason"],
            allowed=list(owner["allowed_tracklet_ids"] or []), owner_chain=_chain(owner["owner_chain"]),
            candidates=[{"y": c["y"], "tracklet": c["sequence_tracklet_id"] or "",
                         "admitted": _admitted(c["sequence_tracklet_admitted"])} for c in owner["oil_candidates"]]))
    return frames


def from_bundle(bundle: Path, glass: str, window: tuple[float, float]) -> tuple[list[dict], float, list[str]]:
    """Frames, the Recipe step and the run IDs from a saved bundle's FULL debug trace."""
    from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
    from tests.diagnostics.s11_cadence_field import _rows
    from tests.diagnostics.s11_layer_bottom_topology_2_field import _stop, _y

    recipe = JsonRecipeRepository().load(bundle / "recipe_snapshot.oilrecipe")
    config = next((g for g in recipe.glasses if g.name == glass), None)
    if config is None:
        _stop(f"no Glass {glass} in the Recipe snapshot")
    step = max(1.0, float(config.detector_settings.temporal_max_jump_px))
    rows = {int(row["frame_index"]): row for row in _rows(bundle, glass)
            if window[0] <= float(row["timestamp_sec"]) <= window[1]}
    trace = bundle / "debug" / "debug_trace.jsonl"
    if not trace.is_file():
        _stop(f"no debug trace in {bundle}")
    records, run_ids = {}, set()
    with trace.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("glass_name") == glass and record.get("frame_index") in rows:
                if "sequence" not in record:
                    _stop(f"record {record.get('record_id')} has no sequence snapshot")
                records[record["frame_index"]] = record["sequence"]
                run_ids.add(str(record.get("run_id")))
    frames = []
    for frame, row in sorted(rows.items()):
        sequence = records.get(frame) or {}
        state = sequence.get("state") or {}
        diagnostic = state.get("sequence_material_phase_diagnostics") or {}
        frames.append(dict(
            time=round(float(row["timestamp_sec"]), 3), frame=frame, fill=row["fill_state"],
            published_y=_y(row["raw_oil_air_level_y"]), reason=state.get("sequence_material_phase_reason"),
            allowed=list(diagnostic.get("allowed_tracklet_ids") or []),
            owner_chain=_chain(state.get("sequence_material_phase_owner_chain")),
            candidates=[{"y": c.get("canonical_y"), "tracklet": c.get("tracklet_id") or "",
                         "admitted": _admitted(c.get("tracklet_admitted"))}
                        for c in sequence.get("candidates") or () if c.get("kind") == "oil_air"]))
    return frames, step, sorted(run_ids)


def context(frames: list[dict], window: tuple[float, float] | None) -> list[dict]:
    """Every row in ``window`` with its admitted Oil candidates, owners or not (for a near-miss reading)."""
    if window is None:
        return []
    return [{**{k: frame[k] for k in ("time", "frame", "fill", "published_y", "reason")},
             "allowed": sorted(frame["allowed"]),
             "admitted": sorted({(c["y"], c["tracklet"], c["tracklet"] in set(frame["allowed"]) | set(frame["owner_chain"]))
                                 for c in frame["candidates"] if c["admitted"] and c["tracklet"] and c["y"] is not None})}
            for frame in frames if window[0] <= frame["time"] <= window[1]]


def summary(frames: list[dict], step_px: float, context_window: tuple[float, float] | None = None) -> dict:
    published = [f for f in frames if f["published_y"] is not None and f["reason"] in SINGLE_OWNER_REASONS
                 and f["allowed"]]
    found = hits(frames, step_px)
    return {"step_px": step_px, "rows": len(frames), "single_owner_published": len(published),
            "hit_count": len(found), "hits": found, "context_window": context_window,
            "context": context(frames, context_window)}


def print_summary(label: str, result: dict) -> None:
    print(f"owner-above readout {label} | step {result['step_px']} px | rows {result['rows']} | "
          f"single-owner published {result['single_owner_published']} | hits {result['hit_count']}")
    print("-- hits: time | frame | fill | published y | reason | allowed | owner top y | above (y tracklet gap) --")
    for hit in result["hits"]:
        above = "; ".join(f"{a['y']} {a['tracklet']} {a['gap_px']}" for a in hit["above"])
        print(f"{hit['time']:.3f} | {hit['frame']} | {hit['fill']} | {hit['published_y']} | {hit['reason']} | "
              f"{','.join(hit['allowed'])} | {hit['owner_top_y']} | {above}")
    if result["context_window"] is not None:
        print(f"-- context {result['context_window'][0]}-{result['context_window'][1]} s: time | frame | fill | "
              "published y | reason | allowed | admitted Oil candidates (y tracklet owner?) --")
        for row in result["context"]:
            admitted = "; ".join(f"{y} {t} {'owner' if own else 'other'}" for y, t, own in row["admitted"]) or "(none)"
            print(f"{row['time']:.3f} | {row['frame']} | {row['fill']} | {row['published_y']} | {row['reason']} | "
                  f"{','.join(row['allowed']) or '-'} | {admitted}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bundle", type=Path, help="saved bundle with a FULL debug trace")
    source.add_argument("--comparison", type=Path, help="local comparison file with owner readouts")
    parser.add_argument("--glass-name", default="BASE")
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=1e9)
    parser.add_argument("--arm", default="top_exit", help="comparison arm (with --comparison)")
    parser.add_argument("--step-px", type=float, default=32.0, help="association step (with --comparison)")
    parser.add_argument("--context", type=float, nargs=2, metavar=("START", "END"),
                        help="also list every row's admitted Oil candidates in this window")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.bundle is not None:
        frames, step, run_ids = from_bundle(args.bundle, args.glass_name, (args.start, args.end))
        label = f"{args.glass_name} {args.start}-{args.end} s | bundle {args.bundle} | run_id {','.join(run_ids)}"
        name = f"owner_above_readout_{args.glass_name}.json"
    else:
        frames, step = from_comparison(args.comparison, args.arm), args.step_px
        label = f"{args.comparison} | arm {args.arm}"
        name = f"owner_above_readout_{args.arm}.json"
    result = {"source": label, **summary(frames, step, None if args.context is None else tuple(args.context))}
    print_summary(label, result)
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / name
    path.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"json {path.name} sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
