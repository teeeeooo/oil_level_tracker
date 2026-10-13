"""Compile claim-scoped reuse from frozen evidence; never fit or select a target.

The G0 geometry inventory and native trial remain immutable. This supplement
joins original candidate controls to current review facets and prepares exact,
still-unreviewed native subjects for a later, separately declared capability.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_preflight as g0
from tests.diagnostics import s11_native_role_qualification as roles

SCHEMA = "s11-existing-material-reuse-v1"
o2 = g0.o2


def read_pin(root: Path, entry: dict) -> dict:
    g0.pinned_path(root, entry)
    return g0.cr1.read_pinned(root, entry)


def source_groups(root: Path, sources: list[dict]) -> dict:
    """A recording and all its derivatives have one proposed use, not two splits."""
    by_hash = {}
    paths = set()
    allowed = {"DEVELOPMENT", "EXPOSED_EVALUATION", "FAILURE_RESPONSE",
               "LEGACY", "QUARANTINED", "UNASSESSED"}
    for row in sources:
        o2.require(row["use"] in allowed, "unsupported source use")
        o2.require(row["path"] not in paths, "duplicate source path")
        paths.add(row["path"])
        g0.pinned_path(root, row)
        previous = by_hash.get(row["sha256"])
        o2.require(previous is None or previous["use"] == row["use"],
                   "same recording assigned conflicting source groups")
        by_hash[row["sha256"]] = row
    return by_hash


def control_key(row: dict) -> tuple:
    return (row["frame"], row["candidate_input_index"], row["source"], row["source_y"])


def query_key(query: dict) -> tuple:
    return (query["frame"], query.get("candidate_index"), query.get("source"),
            query["source_xy"][1])


def exact_pointer(document: dict, pointer: str):
    o2.require(pointer.startswith("/"), "absolute JSON pointer required")
    value = document
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            o2.require(token.isdigit() and int(token) < len(value), "invalid list pointer")
            value = value[int(token)]
        else:
            o2.require(isinstance(value, dict) and token in value, "missing pointer")
            value = value[token]
    return value


def verify_support(root: Path, row: dict, captures: dict) -> None:
    query = row["query"]
    for name, ref in row["native_support"].items():
        if name not in {"oil_interface_witness", "oil_measurement_lineage"}:
            continue
        if "path" not in ref:
            continue
        path = (root / ref["path"]).resolve()
        o2.require(path.is_relative_to(root.resolve()), "capture escapes repository")
        if str(path) not in captures:
            captures[str(path)] = o2.read_json(path)
        subject = exact_pointer(captures[str(path)], ref["pointer"])
        o2.require(o2.fingerprint_json(subject) == ref["sha256"], "support subject changed")
        y_key = "canonical_y" if name == "oil_interface_witness" else "source_y"
        o2.require((subject["candidate_input_index"], subject["source"], subject[y_key])
                   == (query["candidate_index"], query["source"], query["source_xy"][1]),
                   "support index/source/Y mismatch")


def oil_units(rows: list[dict], controls: list[dict]) -> list[dict]:
    """Opposed means not this Oil target, never a non-interface material label."""
    indexed = {control_key(c): c for c in controls}
    o2.require(len(indexed) == len(controls), "duplicate control identity")
    o2.require(len({r["query"]["id"] for r in rows}) == len(rows), "duplicate query")
    seen, result = set(), []
    for row in rows:
        query = row["query"]
        key = query_key(query)
        control = indexed.get(key)
        claim = "UNASSESSED"
        if control is not None:
            o2.require(key not in seen, "duplicate candidate identity under another query id")
            seen.add(key)
            o2.require(control["time_sec"] == row["time_sec"], "control timestamp mismatch")
            o2.require(control["target_role"] == query["label"], "historical role mismatch")
            authority = control["authority"]
            o2.require((authority["frame"], authority["index"], authority["source"], authority["y"])
                       == key, "authority identity mismatch")
            o2.require(control["target_role"] in {"confirmed_target", "rejected_target"},
                       "unsupported candidate control role")
            claim = ("TARGET_CORRESPONDENCE" if control["target_role"] == "confirmed_target"
                     else "OPPOSED_OIL_TARGET")
        if row["physical_qualification"] == "NOT_QUALIFIED":
            claim = "NOT_QUALIFIED"
        path = row.get("path")
        result.append({
            "query": query, "query_sha256": o2.fingerprint_json(query),
            "baseline_pointer": row["baseline_pointer"], "time_sec": row["time_sec"],
            "glass_id": row["glass_id"], "physical_claim": claim,
            "practical_acceptance": row["practical_acceptance"],
            "native_support": row["native_support"],
            "representation": path["representation"] if path else "SCOPED_GUIDE_ONLY",
            "path_status": path["status"] if path else "NO_CANDIDATE_PATH",
            "authority": ({k: control["authority"][k]
                           for k in ("authority", "reason", "failed_gates")}
                          if control else None),
            "candidate_role_comparison_ready": claim in {"TARGET_CORRESPONDENCE", "OPPOSED_OIL_TARGET"},
            "native_path_role_ready": False, "pure_side_labels": False,
            "training_label_created": False, "decision": "NOT_EVALUATED",
        })
    o2.require(seen == set(indexed), "a reviewed control has no exact candidate join")
    return result


def native_packet(root: Path, manifest: dict, baseline: dict, case_id: str) -> dict:
    contexts = roles.by_id(baseline["contexts"], "context")
    context = contexts[case_id]
    o2.require(context["geometry"]["scale_xy"] == [1, 1], "native packet cannot use reduced view")
    plan = read_pin(root, manifest["inputs"]["foam_preflight"])
    case = plan["cases"][context["original_case_ref"]["index"]]
    o2.require(case["id"] == case_id, "case roster changed")
    paths = [case[k] for k in ("raster", "graph", "stage", "rgb") if case.get(k)]
    paths += list(case.get("images", {}).values())
    for path in set(paths):
        g0.pinned_path(root, {"path": path, "sha256": plan["pins"][path]})
    rgb, visible, _ = g0.material.load_case(root, case)
    edges, _ = g0.load_edges_labels(root, case, {"labels": None})
    o2.require(rgb is not None, "native RGB unavailable")
    graph = g0.contours.measure_edge_fragments(edges, visible)
    fragments, seen = [], set()
    ox, oy = context["geometry"]["origin"]
    for row in context["rows"]:
        for fragment in row["incident_fragments"]:
            fid = fragment["fragment_id"]
            if fid in seen:
                continue
            seen.add(fid)
            path = graph["vertices_xy"][graph["fragments"][fid]].tolist()
            o2.require(o2.fingerprint_json(path) == fragment["path_sha256"], "fragment geometry changed")
            monotone = fragment["orientation"] == "X_MONOTONE_PARTIAL_PATH"
            support = (roles.context_support(visible, fragment["support_columns_xy"], path)[0]
                       if monotone else {"status": "UNRESOLVED_PATH_ORIENTATION"})
            source_path = [[x + ox, y + oy] for x, y in path]
            fragments.append({"id": f"{case_id}/fragment-{fid}", "fragment_id": fid,
                              "g0_fragment_sha256": o2.fingerprint_json(fragment),
                              "source_path_xy": source_path,
                              "fixed_column_source_ys": [oy + y for y in fragment["fixed_column_rows"]],
                              "junction_incident": fragment["junction_incident"],
                              "context_support": support, "role": "UNREVIEWED",
                              "training_label_created": False})
    intervals = []
    for constraint in baseline["weak_constraints"]:
        original = constraint["original"]
        if constraint["unit"] != "SOURCE_CONTAINMENT_INTERVAL" or original["case_id"] != case_id:
            continue
        lo, hi = original["interval"]
        compatible = [f["id"] for f in fragments
                      if any(lo <= y <= hi for y in f["fixed_column_source_ys"])]
        intervals.append({"original": original, "compatible_fragments": compatible,
                          "physical_path_correspondence": "NOT_QUALIFIED",
                          "candidate_positive_ids": [], "candidate_negative_ids": []})
    return {"case_id": case_id, "source_recording": context["source_recording"],
            "frame": context["frame"], "time_sec": context["time_sec"],
            "geometry": context["geometry"], "geometry_sha256": context["geometry_sha256"],
            "fragments": fragments, "intervals": intervals,
            "scope": "All saved fixed-column fragments; no interval-to-path labels or selected winner."}


def audit(root: Path, manifest: dict) -> dict:
    o2.require(manifest["schema"] == SCHEMA, "unsupported reuse schema")
    o2.require(manifest["training_executed"] is False, "reuse is not a training entry point")
    groups = source_groups(root, manifest["sources"])
    documents = {name: read_pin(root, pin) for name, pin in manifest["inputs"].items()}
    frozen = documents["g0_readout"]
    gm = documents["g0_manifest"]
    o2.require(frozen["manifest_sha256"] == o2.fingerprint_json(gm), "G0 manifest mismatch")
    baseline = g0.cr1.audit(root, read_pin(root, gm["inputs"]["oil_manifest"]))
    o2.require(baseline == documents["oil_readout"], "original Oil readout changed")
    current = g0.cr1.qualify_reviews(root, baseline, read_pin(root, gm["inputs"]["oil_review_manifest"]))
    o2.require(current == documents["oil_review_readout"], "latest review supplement changed")
    bound = g0.oil_bindings(root, baseline, current)
    o2.require(bound == frozen["oil_rows"], "original Oil support binding changed")
    captures = {}
    for row in bound:
        verify_support(root, row, captures)
    units = oil_units(bound, documents["oil_controls"]["rows"])
    qualified = []
    for pair in manifest["native_qualifications"]:
        result = roles.qualify(root, read_pin(root, pair["reply"]))
        o2.require(result == read_pin(root, pair["readout"]), "native qualification changed")
        qualified.extend(result["subjects"])
    ids = roles.by_id(qualified, "qualified native subject")
    o2.require(set(ids) == set(manifest["qualified_subject_ids"]), "qualified subject roster mismatch")
    contexts = []
    for context in frozen["contexts"]:
        source = context["source_recording"]
        o2.require(source["sha256"] in groups, "context source missing from split")
        contexts.append({"id": context["id"], "source_sha256": source["sha256"],
                         "frame": context["frame"], "representation": context["representation"],
                         "proposed_use": groups[source["sha256"]]["use"]})
    for subject in qualified:
        digest = subject["source_recording"]["sha256"]
        o2.require(digest in groups, "qualified source missing from split")
        subject["proposed_use"] = groups[digest]["use"]
    o2.require(len(set(manifest["prepare_native_cases"])) == len(manifest["prepare_native_cases"]),
               "duplicate native packet case")
    packets = [native_packet(root, gm, frozen, cid) for cid in manifest["prepare_native_cases"]]
    claims = Counter(u["physical_claim"] for u in units)
    eligible = [u for u in units if u["candidate_role_comparison_ready"]]
    return {
        "schema": SCHEMA, "manifest_sha256": o2.fingerprint_json(manifest),
        "status": "REUSE_EXECUTED_NO_DETECTOR_PROMOTION", "production_changed": False,
        "training_executed": False, "model_calls": 0, "video_decode": False,
        "counts": {"source_recordings": len(groups), "contexts": len(contexts),
                   "unique_source_frames": len({(c["source_sha256"], c["frame"]) for c in contexts}),
                   "original_edges": frozen["counts"]["edges"], "oil_records": len(units),
                   "exact_support_records": sum(bool(u["native_support"].get("oil_interface_witness")) for u in units),
                   "physical_claims": dict(claims), "candidate_role_units": len(eligible),
                   "candidate_role_path_status": dict(Counter(u["path_status"] for u in eligible)),
                   "practical_approximations": sum(u["practical_acceptance"] == "ACCEPTED_APPROXIMATION" for u in units),
                   "qualified_native_subjects": len(qualified), "untouched_holdout_recordings": 0},
        "sources": manifest["sources"], "contexts": contexts, "oil_units": units,
        "qualified_native_subjects": qualified, "native_review_packets": packets,
        "weak_constraints": frozen["weak_constraints"],
        "readiness": {"oil_candidate_level_development_comparison": "READY_AT_ORIGINAL_PRECISION",
                      "oil_native_path_or_pure_side_labels": "NOT_QUALIFIED",
                      "successor_native_transfer": "NOT_READY_UNBOUND_EVALUATION_ROLES",
                      "production_consumer": "NOT_ENTERED_O2_V5_REQUIRED"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    manifest = o2.read_json(args.manifest)
    started = g0.time.monotonic()
    result = audit(args.root.resolve(), manifest)
    elapsed = g0.time.monotonic() - started
    limits = manifest["resources"]
    o2.require(elapsed <= limits["seconds"], "reuse time budget exceeded")
    memory = g0.peak_rss()
    if memory["bytes"] is not None:
        o2.require(memory["bytes"] <= limits["peak_rss_bytes"], "reuse memory budget exceeded")
    raw = (json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n").encode()
    o2.require(len(raw) <= limits["output_bytes"], "reuse output budget exceeded")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(gzip.compress(raw, mtime=0) if args.output.suffix == ".gz" else raw)
    print(json.dumps({"counts": result["counts"], "seconds": elapsed,
                      "peak_rss": memory, "output_bytes": args.output.stat().st_size}))


if __name__ == "__main__":
    main()
