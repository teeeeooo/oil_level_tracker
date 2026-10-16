"""Offline P1/P2 screen; no detector mutation, model or new physical labels."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
from types import SimpleNamespace

from oil_tracker.adapters.storage.json_recipe_repository import JsonRecipeRepository
from oil_tracker.adapters.vision.oil_candidate_authority import (
    AuthorityContext, OilCandidateAuthority, evaluate_candidate_authority,
)
from oil_tracker.adapters.vision.oil_candidate_evidence import (
    OilCandidateEvidenceIndex, candidate_is_eligible,
)
from oil_tracker.adapters.vision.oil_observation_resolver import (
    OilObservationResolverConfig, _candidate_representation_family,
    _cross_representation_support,
)
from oil_tracker.adapters.vision.oil_phase_identity import (
    OilPhaseIdentity, PhaseIdentityContext, evaluate_phase_identity,
)
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind

SCHEMA = "s11-corroboration-peer-screen-v1"
SUPPORT_FLOOR = 0.24  # unchanged production material-path corroboration floor
PREFIX = "docs/50-diagnostics/s11/"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fingerprint(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def candidate_from_dict(value: dict) -> BoundaryCandidate:
    return BoundaryCandidate(**{**value, "kind": BoundaryKind(value["kind"])})


def standalone_seed(candidate, config, evidence_index):
    """A nonrecursive policy counterfactual, not certified raster identity."""
    evidence = evidence_index.evidence(candidate)
    identity = evaluate_phase_identity(candidate, config, PhaseIdentityContext(), evidence)
    decision = evaluate_candidate_authority(
        candidate, config,
        AuthorityContext(allow_terminal_anchor=False, phase_identity=identity), evidence,
    )
    ordinary = _candidate_representation_family(candidate, evidence) == "phase_hypothesis"
    accepted = (ordinary and identity.identity is OilPhaseIdentity.DIRECT_INTERFACE
                and decision.tier is OilCandidateAuthority.ANCHOR_ELIGIBLE)
    return {"eligible_seed": accepted, "ordinary": ordinary,
            "identity": identity.identity.value, "tier": decision.tier.name,
            "reason": decision.reason.value, "failed_gates": list(decision.failed_gates)}


def audit_frame(raw_candidates, glass):
    """Use exact production pair scores; retain input indexes and all max ties."""
    candidates = tuple(candidate_from_dict(c) for c in raw_candidates)
    before = [asdict(c) for c in candidates]
    index = OilCandidateEvidenceIndex()
    oil = tuple((i, c) for i, c in enumerate(candidates)
                if c.kind is BoundaryKind.OIL_AIR and math.isfinite(c.y))
    config = OilObservationResolverConfig()
    seeds = {i: standalone_seed(c, config, index) for i, c in oil}
    rows = []
    for i, candidate in oil:
        whole = _cross_representation_support(
            candidate, tuple(c for _, c in oil), glass, evidence_index=index)
        contributors = []
        for j, peer in oil:
            score = _cross_representation_support(
                candidate, (candidate, peer), glass, evidence_index=index)
            if score > 0:
                contributors.append({"candidate_input_index": j, "source": peer.source,
                    "source_y": peer.y, "support": score,
                    "seed": seeds[j],
                    "evidence": asdict(index.evidence(peer))})
        pair_max = max((p["support"] for p in contributors), default=0.0)
        require(pair_max == whole, f"pair/whole support mismatch at {i}")
        seeded = max((p["support"] for p in contributors if p["seed"]["eligible_seed"]),
                     default=0.0)
        e = index.evidence(candidate)
        rows.append({"candidate_input_index": i, "source": candidate.source,
            "source_y": candidate.y, "family": _candidate_representation_family(candidate, e),
            "input_eligible": candidate_is_eligible(candidate, e),
            "evidence": asdict(e), "standalone_seed": seeds[i],
            "legacy_support": whole, "nonrecursive_support": seeded,
            "winning_peer_indexes": [p["candidate_input_index"] for p in contributors
                                     if p["support"] == whole],
            "nonrecursive_winning_peer_indexes": [p["candidate_input_index"]
                for p in contributors if p["seed"]["eligible_seed"] and p["support"] == seeded],
            "proposed_gate_consumer": e.material_path,
            "legacy_support_pass": whole >= SUPPORT_FLOOR,
            "nonrecursive_support_pass": seeded >= SUPPORT_FLOOR,
            "material_support_removed": (e.material_path and whole >= SUPPORT_FLOOR
                                         and seeded < SUPPORT_FLOOR),
            "contributors": contributors})
    require(before == [asdict(c) for c in candidates], "input mutation")
    return rows


def run(root: Path) -> dict:
    pins = {}

    def load(relative, expected=None):
        path = root / relative
        digest = fingerprint(path)
        require(expected is None or digest == expected, f"input hash mismatch: {relative}")
        pins[relative] = digest
        return json.loads(path.read_text(encoding="utf-8"))

    rim_plan = load(PREFIX + "2026-10-14-candidate-rgb-trial/rim-plan.json")
    prepared = load(**{"relative": rim_plan["inputs"]["prepared"]["path"],
                       "expected": rim_plan["inputs"]["prepared"]["sha256"]})
    rim = load(rim_plan["inputs"]["reply"]["path"], rim_plan["inputs"]["reply"]["sha256"])
    trial = load(rim_plan["inputs"]["trial_plan"]["path"],
                 rim_plan["inputs"]["trial_plan"]["sha256"])
    preflight = load(trial["inputs"]["cr1_preflight"]["path"],
                     trial["inputs"]["cr1_preflight"]["sha256"])
    public_plan = load(trial["inputs"]["public_review_plan"]["path"],
                       trial["inputs"]["public_review_plan"]["sha256"])
    public = load(public_plan["inputs"]["capture"]["path"],
                  public_plan["inputs"]["capture"]["sha256"])
    sample_recipe = root / "sample/sample4.oilrecipe"
    pins[str(sample_recipe.relative_to(root))] = fingerprint(sample_recipe)
    require(pins["sample/sample4.oilrecipe"] == preflight["inputs"]["sample/sample4.oilrecipe"],
            "sample4 Recipe mismatch")
    sample_glass = JsonRecipeRepository().load(sample_recipe).glasses[0]
    native = next(c for c in public["cases"] if c["variant"]["id"] == "native")
    public_glass = SimpleNamespace(detector_settings=SimpleNamespace(**native["settings"]))
    frames = {}
    raw_by_frame = {}
    frame_meta = {}
    for fid in prepared["frames"]:
        if fid.startswith("sample4-f"):
            frame = int(fid.split("-f")[1])
            path = f"sample/output/s11-a1-lineage-20261007-001/frames-final/f{frame}.json"
            raw = load(path, preflight["original_capture_pins"][path])["current"]
            glass = sample_glass
        else:
            require(fid == "public-f1499", f"unexpected source: {fid}")
            raw = load(public_plan["inputs"]["raw"]["path"],
                       public_plan["inputs"]["raw"]["sha256"])
            glass = public_glass
        raw_by_frame[fid] = raw
        frame_meta[fid] = {"frame_index": raw["frame_index"], "time_sec": raw["time_sec"],
            "candidate_count": len(raw["candidates"]),
            "temporal_max_jump_px": glass.detector_settings.temporal_max_jump_px}
        frames[fid] = {r["candidate_input_index"]: r
                       for r in audit_frame(raw["candidates"], glass)}
    rim_by_id = {s["id"]: s for s in rim["subjects"]}
    rows = []
    for unit in prepared["units"]:
        row = {k: unit[k] for k in ("id", "group", "frame_id", "query", "query_sha256",
                                    "is_oil_candidate", "label_basis")}
        row["review_label"] = ("ACCEPTED" if unit["target"] == 0 else
                               "OPPOSED" if unit["target"] == 1 else "UNASSESSED")
        if unit["id"] in rim_by_id:
            require(unit["query_sha256"] == rim_by_id[unit["id"]]["query_sha256"],
                    "rim query identity mismatch")
            row["review_label"] = "OPPOSED"
            row["rim_reply"] = rim_by_id[unit["id"]]
        query = unit["query"]
        if "candidate_index" in query:
            fid = unit["frame_id"] or f"{unit['group']}-f{query['frame']}"
            current = raw_by_frame[fid]["candidates"][query["candidate_index"]]
            require((current["source"], current["y"]) ==
                    (query["source"], query["source_xy"][1]),
                    f"candidate identity mismatch: {unit['id']}")
            row["raw_frame_id"] = fid
            row["source_kind"] = current["kind"]
            row["declared_kind_disagrees"] = (
                unit["is_oil_candidate"] != (current["kind"] == "oil_air"))
            if current["kind"] == "oil_air":
                row["measurement"] = frames[fid][query["candidate_index"]]
            else:
                require(row["review_label"] == "UNASSESSED", "reviewed Oil label on raw non-Oil")
        else:
            row["source_kind"] = "NON_CANDIDATE_CONTEXT"
            row["declared_kind_disagrees"] = False
        rows.append(row)
    actual_keys = {(r["raw_frame_id"], r["query"]["candidate_index"])
                   for r in rows if "measurement" in r}
    require(actual_keys == {(fid, i) for fid, group in frames.items() for i in group},
            "Oil population incomplete or extra")
    require(len(actual_keys) == sum("measurement" in r for r in rows), "duplicate Oil unit")
    summary = {"total_units": len(rows), "frames": len(frames),
        "oil_candidates": len(actual_keys),
        "foam_candidates": sum(r["source_kind"] == "foam_front" for r in rows),
        "contexts": sum(r["source_kind"] == "NON_CANDIDATE_CONTEXT" for r in rows),
        "legacy_declared_kind_mismatches": [r["id"] for r in rows if r["declared_kind_disagrees"]],
        "all_pair_whole_scores_equal": True, "source_inputs_unchanged": True,
        "by_review": {}}
    for label in ("ACCEPTED", "OPPOSED", "UNASSESSED"):
        group = [r for r in rows if r["review_label"] == label and "measurement" in r]
        summary["by_review"][label] = {
            "units": len(group),
            "legacy_support_pass": [r["id"] for r in group if r["measurement"]["legacy_support_pass"]],
            "nonrecursive_support_pass": [r["id"] for r in group if r["measurement"]["nonrecursive_support_pass"]],
            "standalone_seeds": [r["id"] for r in group if r["measurement"]["standalone_seed"]["eligible_seed"]],
            "material_consumers": [r["id"] for r in group if r["measurement"]["proposed_gate_consumer"]],
            "material_support_removed": [r["id"] for r in group if r["measurement"]["material_support_removed"]]}
    for rel, digest in pins.items():
        require(fingerprint(root/rel) == digest, f"source input changed during audit: {rel}")
    return {"schema": SCHEMA, "support_floor": SUPPORT_FLOOR, "summary": summary,
            "inputs": pins, "frame_metadata": frame_meta, "units": rows,
            "scope": "SAVED_CURRENT_CANDIDATES_AND_ISOLATED_SEED_AUTHORITY_ONLY",
            "physical_accuracy": "NOT_EVALUATED", "windows_721_replay": "NOT_AVAILABLE",
            "production_changed": False, "classifier_or_gate_adopted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+"\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
