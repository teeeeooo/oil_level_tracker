"""FOR-1: does a tracklet's recent motion separate fill owners at the level from low owners?

Reruns FOA-1's baseline (the IFO v2 + top-exit v3 arm at 2 fps, EMPTY initial state) and adds, per
Oil candidate, the confirmation profile and the recent-window fields the resolver already writes.
The frozen readings R1-R5 and the outcome are in docs/50-diagnostics/s11/2026-10-27-fill-owner-recency-local.md.
Diagnostics only. Use a managed experiment's work directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path

from tests.diagnostics import s11_initial_full_comparison as comparison
from tests.diagnostics.s11_fast_fill_cadence import FOA_RUN, ROI_INPUTS, foa_baseline, run_arm, surface_at

NEAR_LEVEL_PX = 32.0  # FOA-1's distance unit
MINIMUM_DIRECTIONAL_AGREEMENT = 0.60  # tracklet_confirmation_min_directional_agreement
DRAIN_MINIMUM_PROGRESS_RATIO = 0.025  # completed_fill_release_min_downward_ratio
RECENCY_FEATURES = (
    "sequence_tracklet_confirmation_profile",
    "sequence_tracklet_directional_agreement",
    "sequence_tracklet_recent_direction",
    "sequence_tracklet_recent_net_progress_px",
    "sequence_tracklet_recent_directional_agreement",
    "sequence_tracklet_recent_window_end_frame",
)
# R5: owner 0016's user-judged correct rows on sample7.
SAMPLE7_CORRECT_OWNER_SUFFIX = ":0016"
SAMPLE7_CORRECT_SPAN = (22.0, 31.5)


@contextmanager
def recency_readout():
    """FOA-1's owner readout with the recency fields added under a separate key."""
    original = comparison._owner_readout

    def extended(detection: dict) -> dict:
        frame = original(detection)
        frame["recency"] = [
            {"sequence_tracklet_id": candidate["features"].get("sequence_tracklet_id"),
             **{key: candidate["features"].get(key) for key in RECENCY_FEATURES}}
            for candidate in detection["candidates"] if candidate["kind"] == "oil_air"
        ]
        return frame

    comparison._owner_readout = extended
    try:
        yield
    finally:
        comparison._owner_readout = original


def minimum_progress(sample: str) -> float:
    recipe = json.loads((ROI_INPUTS / f"{sample}.oilrecipe").read_text(encoding="utf-8"))
    (glass,) = recipe["glasses"]
    height = max(1.0, float(glass["geometry"]["ellipse"]["radius_y"]) * 2.0)
    return max(4.0, height * DRAIN_MINIMUM_PROGRESS_RATIO)


def recent_pass(recency: dict, progress: float) -> bool:
    return bool(
        recency["sequence_tracklet_recent_direction"] < 0
        and recency["sequence_tracklet_recent_directional_agreement"] >= MINIMUM_DIRECTIONAL_AGREEMENT
        and recency["sequence_tracklet_recent_net_progress_px"] >= progress
    )


def position(offset: float | None) -> str | None:
    if offset is None:
        return None
    if abs(offset) <= NEAR_LEVEL_PX:
        return "level"
    return "low" if offset > 0 else "above"


def owner_row(frame: dict, owner: str) -> tuple[dict, dict] | None:
    """The owner's candidate and its recency fields; the selected one first, then the highest."""
    pairs = [(candidate, recency) for candidate, recency in zip(frame["oil_candidates"], frame["recency"], strict=True)
             if candidate["sequence_tracklet_id"] == owner]
    if not pairs:
        return None
    return sorted(pairs, key=lambda pair: (not pair[0]["selected"], pair[0]["y"]))[0]


def rate(passed: int, total: int) -> float | None:
    return round(passed / total, 3) if total else None


def readings(sample: str, readout: list[dict], times: list[float], estimates: list[dict]) -> dict:
    progress = minimum_progress(sample)
    pairs, per_frame, table = [], Counter(), Counter()
    for frame, t in zip(readout, times, strict=True):
        if frame["reason"] != "FILL_OWNER_AMBIGUOUS":
            continue
        surface = surface_at(estimates, t)
        passing = 0
        for owner in frame["dynamic_fill_owner_ids"] or ():
            found = owner_row(frame, owner)
            entry = dict(t=t, owner=owner, row=found is not None)
            if found is not None:
                candidate, recency = found
                offset = None if surface is None else round(candidate["y"] - surface, 1)
                entry |= dict(y=candidate["y"], selected=candidate["selected"],
                              fixed_direction=candidate["sequence_tracklet_direction"],
                              fixed_net_progress_px=candidate["sequence_tracklet_net_progress_px"],
                              **{key.removeprefix("sequence_tracklet_"): recency[key] for key in RECENCY_FEATURES},
                              passes=recent_pass(recency, progress), offset_px=offset, position=position(offset))
                passing += entry["passes"]
                if entry["position"] is not None:
                    table[(entry["position"], entry["passes"])] += 1
            pairs.append(entry)
        per_frame[min(passing, 2)] += 1
    published = []
    for frame, t in zip(readout, times, strict=True):
        if frame["published_oil_y"] is None:
            continue
        selected = [(c, r) for c, r in zip(frame["oil_candidates"], frame["recency"], strict=True) if c["selected"]]
        if not selected:
            continue
        candidate, recency = selected[0]
        surface = surface_at(estimates, t)
        offset = None if surface is None else round(frame["published_oil_y"] - surface, 1)
        published.append(dict(t=t, tracklet=candidate["sequence_tracklet_id"], y=frame["published_oil_y"],
                              offset_px=offset, passes=recent_pass(recency, progress)))
    out = dict(minimum_recent_progress_px=round(progress, 3), r1_owner_rows=pairs,
               r2_table={f"{where}/{'pass' if passed else 'fail'}": n for (where, passed), n in sorted(table.items())},
               r3_frames_by_passing_owners={("2+" if k == 2 else str(k)): v for k, v in sorted(per_frame.items())},
               owner_pairs=len(pairs), owner_pairs_without_row=sum(not p["row"] for p in pairs))
    for where in ("level", "low", "above"):
        total = table[(where, True)] + table[(where, False)]
        out[f"{where}_pass_rate"] = rate(table[(where, True)], total)
    if sample == "sample5":
        wrong = [p for p in published if p["offset_px"] is not None and p["offset_px"] > NEAR_LEVEL_PX and p["t"] > 9.0]
        out["r4_wrong_rows"] = wrong
        out["r4_pass_rate"] = rate(sum(p["passes"] for p in wrong), len(wrong))
    else:
        correct = [p for p in published if p["tracklet"].endswith(SAMPLE7_CORRECT_OWNER_SUFFIX)
                   and SAMPLE7_CORRECT_SPAN[0] <= p["t"] <= SAMPLE7_CORRECT_SPAN[1]]
        out["r5_correct_rows"] = correct
        out["r5_pass_rate"] = rate(sum(p["passes"] for p in correct), len(correct))
    return out


def outcome(sample5: dict, sample7: dict) -> str:
    low, level = sample5["low_pass_rate"], sample5["level_pass_rate"]
    if low is not None and level is not None and abs(low - level) < 0.25:
        return "NO-SEP"
    sample5_separates = low is not None and low <= 0.25 and (level is None or level >= 0.75)
    sample7_keeps = sample7["r5_pass_rate"] is not None and sample7["r5_pass_rate"] >= 0.75
    return "SEP" if sample5_separates and sample7_keeps else "MIXED"


def run(sample: str, work: Path) -> dict:
    with recency_readout():
        out = run_arm(sample, "baseline", work)
    kept = foa_baseline(sample)
    base = [{key: value for key, value in frame.items() if key != "recency"} for frame in out["owner_readout"]]
    out["identity_rows_equal_foa"] = out["rows"] == kept["rows"]
    out["identity_readout_equal_foa"] = base == kept.get("owner_readout")
    estimates = json.loads((FOA_RUN / "surface-estimates.json").read_text(encoding="utf-8"))[sample]["estimates"]
    times = [row["timestamp_sec"] for row in out["rows"]]
    out["for1"] = readings(sample, out["owner_readout"], times, estimates)
    return out


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args(argv)
    args.work.mkdir(parents=True, exist_ok=True)
    results = {sample: run(sample, args.work) for sample in ("sample5", "sample7")}
    identity = all(r["identity_rows_equal_foa"] and r["identity_readout_equal_foa"] for r in results.values())
    summary = dict(identity_gate="PASS" if identity else "FAIL",
                   outcome=outcome(results["sample5"]["for1"], results["sample7"]["for1"]) if identity else "VOID")
    for sample, result in results.items():
        target = args.work / f"for1-{sample}.json.gz"
        payload = json.dumps(result, ensure_ascii=False, allow_nan=False, default=str).encode("utf-8")
        target.write_bytes(gzip.compress(payload, mtime=0))  # mtime 0: the hash depends on the content only
        readings_only = {k: v for k, v in result["for1"].items() if k != "r1_owner_rows"}
        summary[sample] = dict(detector_version=result["detector_version"], rows=len(result["rows"]),
                               identity_rows=result["identity_rows_equal_foa"],
                               identity_readout=result["identity_readout_equal_foa"],
                               readings=readings_only, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (args.work / "for1-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("identity_gate", "outcome")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
