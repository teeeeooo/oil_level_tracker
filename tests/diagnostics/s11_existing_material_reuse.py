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
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_preflight as g0
from tests.diagnostics import s11_native_role_qualification as roles

SCHEMA = "s11-existing-material-reuse-v1"
POLICY_SCHEMA = "s11-oil-support-policy-feasibility-v1"
PUBLIC_SCHEMA = "s11-public-oil-saved-candidate-audit-v1"
RIM_SCHEMA = "s11-candidate-rgb-rim-review-audit-v1"
SOURCE_SCHEMA = "s11-oil-candidate-source-qualification-v1"
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


def policy_audit(root: Path, manifest: dict, reused: dict, plan: dict) -> dict:
    """Bind a predeclared family falsification to the fully reverified corpus."""
    o2.require(plan["schema"] == POLICY_SCHEMA, "unsupported policy audit schema")
    o2.require(plan["reuse_manifest_sha256"] == o2.fingerprint_json(manifest), "reuse manifest changed")
    o2.require(reused == read_pin(root, plan["reuse_readout"]), "reuse readout changed")
    o2.require(plan["policy"] == {"id": g0.cr1.POLICY, "tau_support": None,
                                "tie_epsilon": g0.cr1.TIE_EPSILON}, "policy family changed")
    o2.require(plan["operation"] == "NECESSARY_CONDITION_NO_THRESHOLD_SELECTION", "unsupported operation")
    o2.require(plan["required_control_outcome"] == {"positive_loss": 0, "opposition_accepted": 0},
               "required control outcome changed")
    units = reused["oil_units"]
    baseline = read_pin(root, manifest["inputs"]["oil_readout"])
    o2.require(len(units) == len(baseline["rows"]), "complete population required")
    controls, facets = [], []
    for index, (unit, row) in enumerate(zip(units, baseline["rows"])):
        o2.require(unit["baseline_pointer"] == f"/rows/{index}" and unit["query"] == row["query"]
                   and unit["query_sha256"] == o2.fingerprint_json(row["query"]), "exact policy query join failed")
        if unit["candidate_role_comparison_ready"] or unit["physical_claim"] == "NOT_QUALIFIED":
            query = unit["query"]
            o2.require(type(query["initial_reference"]) is bool, "reference membership missing")
            result = {"id": query["id"], "query": query, "query_sha256": unit["query_sha256"],
                      "baseline_pointer": unit["baseline_pointer"], "claim": unit["physical_claim"],
                      "practical_acceptance": unit["practical_acceptance"],
                      "initial_reference": query["initial_reference"], "local": row["modes"]["local"],
                      "decision": "NOT_EVALUATED"}
            (controls if unit["candidate_role_comparison_ready"] else facets).append(result)
    roster = [{k: c[k] for k in ("id", "query_sha256", "claim", "initial_reference")} for c in controls]
    o2.require(roster == plan["controls"], "predeclared control roster changed")
    nonself = [c for c in controls if not c["initial_reference"]]
    results = {"all_current_controls": g0.cr1.support_policy_feasibility(controls),
               "excluding_initial_reference": g0.cr1.support_policy_feasibility(nonself)}
    return {"schema": POLICY_SCHEMA, "plan_sha256": o2.fingerprint_json(plan),
            "status": results["all_current_controls"]["status"], "results": results,
            "inputs": {"reuse_readout": plan["reuse_readout"], "oil_readout": manifest["inputs"]["oil_readout"]},
            "counts": {"population": len(units), "controls": len(controls),
                       "claims": dict(Counter(u["physical_claim"] for u in units)),
                       "local_availability": dict(Counter(r["modes"]["local"]["availability"] for r in baseline["rows"])),
                       "independent_scored_recordings": baseline["counts"]["independent_recordings"],
                       "untouched_holdout_recordings": 0},
            "full_population_query_digest": o2.fingerprint_json([u["query_sha256"] for u in units]),
            "controls": controls, "nonphysical_facets": facets,
            "production_changed": False, "training_executed": False, "model_calls": 0,
            "decision": "NOT_EVALUATED", "native_path_role_ready": False,
            "scope": "Necessary condition on exposed original-precision controls only; no operating point or accuracy claim."}


def qualify_candidate_acceptance(packet: dict, reply: dict) -> set[int]:
    """A reply binds practical acceptance to displayed candidates, not paths."""
    o2.require(reply["schema"] == "s11-public-oil-candidate-acceptance-v1", "unsupported candidate reply")
    o2.require(reply["review_packet_sha256"] == o2.fingerprint_json(packet), "review packet changed")
    o2.require(reply["image_sha256"] == packet["image_sha256"], "displayed image changed")
    o2.require((reply["frame_index"], reply["time_sec"], reply["source_x"])
               == (packet["frame_index"], packet["time_sec"], packet["source_x"]), "reply frame/time/X mismatch")
    o2.require(reply["scope"] == "PRACTICAL_APPROXIMATION_AT_THIS_FRAME_ONLY", "reply scope broadened")
    o2.require(reply["user_text"] == "모두 허용", "unsupported all-candidate reply")
    subjects = [{"candidate_input_index": r["candidate_input_index"], "candidate_sha256": r["candidate_sha256"]}
                for r in packet["candidates"] if r["review_requested"]]
    o2.require(subjects and reply["subjects"] == subjects, "reply subject roster changed")
    indices = [s["candidate_input_index"] for s in subjects]
    o2.require(len(set(indices)) == len(indices), "duplicate reviewed candidate")
    return set(indices)


def saved_candidate_observations(raw: dict, packet: dict, transfer: dict, accepted: set[int]) -> list[dict]:
    """Exact coordinate lookup within one pinned source/geometry, never nearest Y."""
    geometry = transfer["geometry"]
    o2.require(len(raw["candidates"]) == len(packet["candidates"]), "complete candidate population required")
    anchors = {}
    for i, record in enumerate(transfer["results"]):
        key = tuple(record["query"]["source_xy"])
        o2.require(key not in anchors, "duplicate saved anchor")
        anchors[key] = (i, record)
    rows = []
    for i, (candidate, bound) in enumerate(zip(raw["candidates"], packet["candidates"])):
        o2.require(bound["candidate_input_index"] == i
                   and bound["candidate_sha256"] == o2.fingerprint_json(candidate)
                   and (bound["source"], bound["kind"], bound["representative_y"])
                   == (candidate["source"], candidate["kind"], candidate["y"]), "exact candidate binding failed")
        x, y = packet["source_x"], o2.number(candidate["y"], "candidate Y")
        required = [[x, v] for v in sorted({math.floor(y), math.ceil(y)})]
        found = [anchors.get(tuple(v)) for v in required]
        query = {"id": f"public-f{raw['frame_index']}-idx{i}", "frame": raw["frame_index"],
                 "candidate_index": i, "source": candidate["source"], "source_xy": [x, y]}
        row = {"query": query, "candidate_sha256": bound["candidate_sha256"],
               "practical_acceptance": "ACCEPTED_APPROXIMATION" if i in accepted else "NOT_REVIEWED",
               "physical_role": "NOT_QUALIFIED", "native_path_role": "NOT_QUALIFIED",
               "series": candidate["kind"], "required_anchors": required,
               "saved_score_pointers": [f"/results/{v[0]}" if v else None for v in found],
               "score_status": "NOT_SAVED" if any(v is None for v in found) else "SAVED",
               "decision": "NOT_EVALUATED", "modes": None}
        if all(v is not None for v in found):
            variants = []
            for xy, (_, record) in zip(required, found):
                o2.require(record["status"] in {"MEASURED", "UNAVAILABLE_COMMON_SUPPORT_OR_CROP"},
                           "saved anchor not executed")
                variants.append({"source_center_xy": xy, "common_columns": record["common_columns"],
                                 "modes": record["modes"], "status": record["status"]})
            observation = g0.cr1.observe({"query": query, "measurement": {
                "query": query, "status": "COMPARED", "variants": variants}}, {
                "native_shape": geometry["native_shape"][:2], "origin_xy": geometry["source_origin_xy"],
                "native_columns": list(range(-12, 13)), "minimum_common_columns": 8})
            row["modes"] = observation["modes"]
        rows.append(row)
    return rows


def public_candidate_audit(root: Path, plan: dict) -> dict:
    o2.require(plan["schema"] == PUBLIC_SCHEMA, "unsupported public candidate audit")
    o2.require(plan["operation"] == "SAVED_SIGN_NECESSITY_BEFORE_NEW_MEASUREMENTS", "unsupported operation")
    o2.require(plan["policy"] == {"id": g0.cr1.POLICY, "tau_support": None,
                                "tie_epsilon": g0.cr1.TIE_EPSILON}, "policy family changed")
    docs = {name: read_pin(root, pin) for name, pin in plan["inputs"].items()}
    review_plan, packet, reply, tp, transfer = (docs[k] for k in (
        "review_plan", "review_packet", "reply", "transfer_plan", "transfer_readout"))
    for pin in review_plan["inputs"].values():
        g0.pinned_path(root, pin)
    for path, digest in tp["pins"].items():
        g0.pinned_path(root, {"path": path, "sha256": digest})
    o2.require(packet["plan_sha256"] == o2.fingerprint_json(review_plan), "review plan changed")
    g0.pinned_path(root, {"path": plan["review_image"], "sha256": packet["image_sha256"]})
    o2.require(transfer["preflight_sha256"] == plan["inputs"]["transfer_plan"]["sha256"], "score preflight changed")
    o2.require(transfer["geometry"] == tp["geometry"] and transfer["pixel_controls"]["status"] == "PASS",
               "unverified transfer geometry")
    o2.require(transfer["status"] == "COMPLETE_DIAGNOSTIC_ONLY"
               and [r["query"] for r in transfer["results"]] == tp["queries"], "complete saved anchor population required")
    o2.require(all(tp["pins"][review_plan["inputs"][k]["path"]] == review_plan["inputs"][k]["sha256"]
                   for k in ("arrays", "capture", "position", "image")), "source/geometry inputs differ")
    raw = read_pin(root, review_plan["inputs"]["raw"])
    o2.require((raw["frame_index"], raw["time_sec"], packet["source_x"])
               == (transfer["frame_index"], transfer["timestamp_sec"], tp["source_x"])
               == (packet["frame_index"], packet["time_sec"], packet["source_x"]), "source frame/time/X changed")
    accepted = qualify_candidate_acceptance(packet, reply)
    o2.require(sorted(accepted) == plan["accepted_candidate_indices"] == review_plan["candidate_indices"],
               "predeclared acceptance set changed")
    rows = saved_candidate_observations(raw, packet, transfer, accepted)
    controls = [r for r in rows if r["query"]["candidate_index"] in accepted]
    o2.require(all(r["series"] == "oil_air" for r in controls), "other series cannot become Oil acceptance")
    missing = [r["query"]["id"] for r in controls if r["modes"] is None or
               r["modes"]["local"]["minimum_interface_margin"] is None]
    passed = [r["query"]["id"] for r in controls if r["modes"] is not None and
              r["modes"]["local"]["minimum_interface_margin"] is not None and
              r["modes"]["local"]["minimum_interface_margin"] > g0.cr1.TIE_EPSILON]
    status = ("INCOMPLETE_ACCEPTED_CONTROLS" if missing else "SIGN_PRESERVATION_POSSIBLE_NEEDS_OPPOSITION"
              if passed else "CONTRADICTED_PRACTICAL_FRAME_COVERAGE")
    return {"schema": PUBLIC_SCHEMA, "plan_sha256": o2.fingerprint_json(plan), "status": status,
            "counts": {"candidates": len(rows), "accepted_approximations": len(accepted),
                       "score_status": dict(Counter(r["score_status"] for r in rows)),
                       "series": dict(Counter(r["series"] for r in rows)), "sign_passing_accepted": len(passed)},
            "accepted_sign_passing_ids": passed, "missing_accepted_controls": missing,
            "candidate_rows": rows, "saved_anchor_count": len(transfer["results"]),
            "inputs": plan["inputs"], "source": review_plan["inputs"]["recording"],
            "geometry": transfer["geometry"], "scope": "Practical at-least-one candidate preservation at one exposed source frame only.",
            "tau_support": None, "decision": "NOT_EVALUATED", "physical_accuracy": "NOT_EVALUATED",
            "new_model_calls": 0, "training_executed": False, "production_changed": False,
            "untouched_holdout_recordings": 0}


def rgb_review_controls(packet: dict, reply: dict, prepared: dict, readout: dict) -> list[dict]:
    """Add scoped post-trial truth without changing the original fit/evaluation."""
    from tests.diagnostics import s11_candidate_rgb_trial as rgb
    o2.require(reply["schema"] == "s11-candidate-rgb-rim-reply-v1", "unsupported rim reply")
    o2.require(reply["review_packet_sha256"] == o2.fingerprint_json(packet)
               and reply["image_sha256"] == packet["image_sha256"], "review display changed")
    o2.require(reply["scope"] == "DISPLAYED_CANDIDATES_AT_THIS_FRAME_ONLY"
               and reply["frame_id"] == packet["frame_id"], "reply scope/frame changed")
    o2.require(reply["user_text"] == "노란 하단 후보는 구조물이야 glass 주변 rim임.", "unsupported received reply")
    expected = [{"id": s["id"], "query_sha256": s["query_sha256"],
                 "physical_role": "GLASS_RIM_STRUCTURE", "oil_acceptance": "REJECTED_APPROXIMATION"}
                for s in packet["subjects"]]
    o2.require(expected and reply["subjects"] == expected, "reply subject roster changed")
    subjects = o2.unique(packet["subjects"], "id", "review subject")
    units = o2.unique(prepared["units"], "id", "prepared candidate")
    rows = o2.unique(readout["rows"], "id", "saved model candidate")
    o2.require(list(units) == list(rows) and set(subjects) <= set(units), "complete population changed")
    frame = prepared["frames"][packet["frame_id"]]
    o2.require(packet["source_image"] == frame["rgb"], "review source image changed")
    controls = []
    for sid, unit in units.items():
        row = rows[sid]
        o2.require(all(row[k] == unit[k] for k in ("partition", "target", "availability")), "original trial row changed")
        o2.require(o2.fingerprint_json(unit["query"]) == unit["query_sha256"], "candidate query changed")
        if sid in subjects:
            s = subjects[sid]
            o2.require(s["query"] == unit["query"] and s["query_sha256"] == unit["query_sha256"]
                       and unit["frame_id"] == packet["frame_id"]
                       and unit["source_recording"] == packet["source_recording"], "exact review binding failed")
            o2.require(unit["is_oil_candidate"] and unit["target"] is None
                       and unit["partition"] == "unreviewed", "review cannot replace existing truth")
        measured = unit["availability"] == "AVAILABLE"
        margins = {}
        for field, decision_field in (("logits", "decision"), ("mean_color_logits", "mean_color_decision")):
            if measured:
                values = row[field]
                o2.require(len(values) == len(unit["variants"]), "required variants changed")
                o2.require(rgb.decision(values) == row[decision_field], "saved decision differs from logits")
                margins[field] = min(v[0]-v[1] for v in values)
            else:
                o2.require(field not in row and row[decision_field] ==
                           ("UNAVAILABLE" if unit["is_oil_candidate"] else "NOT_EVALUATED"), "missing input became a decision")
        if unit["target"] is not None or sid in subjects:
            o2.require(measured, "required reviewed control unavailable")
            controls.append({"id": sid, "query_sha256": unit["query_sha256"],
                "source_recording": unit["source_recording"], "query": unit["query"],
                "original_partition": unit["partition"], "original_target": unit["target"],
                "evaluation_group": "POST_TRIAL_REVIEW" if sid in subjects else unit["partition"],
                "qualified_target": 1 if sid in subjects else unit["target"],
                "physical_role": "GLASS_RIM_STRUCTURE" if sid in subjects else "UNCHANGED_ORIGINAL_SCOPE",
                "native_path_role": "NOT_EXTENDED", "margins": margins,
                "decisions": {k: row[k] for k in ("decision", "mean_color_decision")}})
    return controls


def rgb_rim_audit(root: Path, plan: dict) -> dict:
    from tests.diagnostics import s11_candidate_rgb_trial as rgb
    o2.require(plan["schema"] == RIM_SCHEMA and plan["operation"] == "BIND_REVIEW_AND_CHECK_SAVED_ORDER_ONLY", "unsupported rim audit")
    docs = {k: read_pin(root, p) for k, p in plan["inputs"].items()}
    packet, reply, prepared, readout = (docs[k] for k in ("review_packet", "reply", "prepared", "readout"))
    o2.require(packet["plan_sha256"] == o2.fingerprint_json(docs["review_plan"]), "review plan changed")
    o2.require(prepared["plan"] == plan["inputs"]["trial_plan"]
               and readout["manifest"] == plan["inputs"]["prepared"], "saved trial input changed")
    o2.require(readout["schema"] == prepared["schema"] == rgb.SCHEMA, "trial schema changed")
    o2.require(readout["configuration"] == prepared["configuration"] == docs["trial_plan"]["configuration"]
               and readout["training_steps"] == prepared["configuration"]["steps"], "fixed trial changed")
    rgb.validate_units(prepared["units"], docs["trial_plan"])
    for pin in [packet["source_image"], packet["source_recording"]] + prepared["sources"]:
        g0.pinned_path(root, pin)
    g0.pinned_path(root, {"path": plan["review_image"], "sha256": packet["image_sha256"]})
    controls = rgb_review_controls(packet, reply, prepared, readout)
    new = [c for c in controls if c["evaluation_group"] == "POST_TRIAL_REVIEW"]
    o2.require([c["id"] for c in new] == plan["review_ids"] == docs["review_plan"]["review_ids"], "reviewed set changed")
    o2.require(rgb.summarize(readout["rows"]) == readout["accounting"]
               and rgb.summarize(readout["rows"], "mean_color_decision") == readout["mean_color_ablation"], "old accounting changed")
    order = {}
    for field, decision_field in (("logits", "decision"), ("mean_color_logits", "mean_color_decision")):
        positives = [c for c in controls if c["qualified_target"] == 0]
        oppositions = [c for c in controls if c["qualified_target"] == 1]
        o2.require(positives and oppositions, "both control types required")
        strongest_positive = max(positives, key=lambda c: c["margins"][field])
        strongest_opposition = max(oppositions, key=lambda c: c["margins"][field])
        lower = strongest_opposition["margins"][field]
        upper = strongest_positive["margins"][field]
        order[field] = {"family": "KEEP iff minimum required-variant class-0 minus class-1 logit > tau",
            "tau": None, "scope": "Necessary condition only, no threshold chosen or prediction changed",
            "strongest_opposition": {"id": strongest_opposition["id"], "margin": lower},
            "strongest_positive": {"id": strongest_positive["id"], "margin": upper},
            "can_reject_all_opposition_and_keep_any_known_positive": lower < upper,
            "new_rim_false_acceptances": [c["id"] for c in new if c["decisions"][decision_field] == rgb.CLASSES[0]]}
    failed = any(v["new_rim_false_acceptances"] for v in order.values())
    oil = [u for u in prepared["units"] if u["is_oil_candidate"]]
    return {"schema": RIM_SCHEMA, "plan_sha256": o2.fingerprint_json(plan),
        "status": "FALSIFIED_BY_REVIEWED_RIM" if failed else "NO_NEW_RIM_FALSE_ACCEPTANCE",
        "inputs": plan["inputs"], "original_trial_status": readout["status"],
        "counts": {"all_records": len(prepared["units"]), "oil_candidates": len(oil),
            "original_controls": len(controls)-len(new), "new_scoped_controls": len(new),
            "unreviewed_oil_candidates": len(oil)-len(controls),
            "unavailable_oil_candidates": sum(u["availability"] != "AVAILABLE" for u in oil),
            "still_unreviewed_other_potential_candidates": len(packet["all_disjoint_unreviewed_compatible"])-len(new)},
        "controls": controls, "margin_order": order,
        "training_executed": False, "new_model_calls": 0, "production_changed": False,
        "scope": "Candidate-level post-trial human opposition; no neighboring/native-path labels or accuracy estimate."}


def source_candidate_acceptance(packet: dict, reply: dict) -> list[dict]:
    """Qualify only the displayed representatives, preserving the frozen packet."""
    o2.require(reply["schema"] == SOURCE_SCHEMA and reply["user_text"] == "모두 허용",
               "unsupported source acceptance reply")
    o2.require(reply["review_packet_sha256"] == o2.fingerprint_json(packet)
               and reply["image_sha256"] == packet["image_sha256"], "source review changed")
    o2.require(reply["scope"] == "DISPLAYED_REPRESENTATIVES_AT_THEIR_FRAMES_ONLY"
               and reply["native_path_role"] == "NOT_QUALIFIED"
               and reply["physical_scalar_truth"] == "NOT_QUALIFIED"
               and reply["global_tolerance_created"] is False, "source reply scope broadened")
    o2.require(reply["source_recording"] == packet["source_recording"], "source recording changed")
    keys = ("id", "view", "frame_index", "time_sec", "candidate_input_index",
            "candidate_sha256", "source", "source_xy")
    expected = [{k: s[k] for k in keys} for s in packet["subjects"]]
    o2.require(reply["subjects"] == expected and len(expected) == 2, "source subjects changed")
    subjects = o2.unique(expected, "id", "reviewed source candidate")
    population = o2.unique(packet["candidate_population"], "id", "source candidate")
    o2.require(set(subjects) <= set(population), "reviewed candidate missing")
    rows = []
    for unit in packet["candidate_population"]:
        o2.require(unit["practical_acceptance"] == "UNASSESSED"
                   and unit["native_path_role"] == "NOT_QUALIFIED", "original source scope changed")
        if unit["id"] in subjects:
            s = subjects[unit["id"]]
            o2.require(all(unit[k] == s[k] for k in keys if k not in {"view", "time_sec"}),
                       "candidate identity changed")
        rows.append({**unit, "practical_acceptance": "ACCEPTED_APPROXIMATION"
                     if unit["id"] in subjects else "UNASSESSED"})
    return rows


def check_saved_visibility(gray, effective, glare, sector, origin) -> int:
    """Reproduce saved band availability/gray evidence, without material inference."""
    import numpy as np
    from oil_tracker.adapters.vision import oil_interface_diagnostics as diagnostics
    visible = (effective > 0) & (glare == 0)
    glared = (effective > 0) & (glare > 0)
    a, b = [x-origin[0] for x in sector["source_x_range"]]
    o2.require(0 <= a < b <= gray.shape[1], "saved sector outside crop")
    profile = diagnostics._sector_profile(gray, visible, np.full(gray.shape, np.nan), None, glared, a, b)
    fields = ("available", "reason", "valid_fraction", "valid_pixel_count", "gray_mean", "gray_std", "glare_fraction")
    bands = [*sector["bands"].values(), *sector["candidate_center_on_same_sector"]["bands"].values()]
    for saved in bands:
        actual = diagnostics._band(profile[2], *saved["local_y_range"], gray.shape[0], b-a)
        for k in fields:
            equal = (math.isclose(actual[k], saved[k], rel_tol=0, abs_tol=1e-12)
                     if type(actual[k]) is float and type(saved[k]) is float else actual[k] == saved[k])
            o2.require(equal, "saved visibility/gray band changed: " + k)
    return len(bands)


def source_candidate_audit(root: Path, plan: dict) -> dict:
    """Bind A/B and inspect the old input footprint; never reopen its failed model."""
    import numpy as np
    from PIL import Image
    from oil_tracker.domain.recipe import InspectionRecipe
    from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
    from oil_tracker.adapters.vision.preprocessing import preprocess
    from tests.diagnostics import s11_candidate_rgb_trial as rgb
    o2.require(plan["schema"] == SOURCE_SCHEMA and plan["operation"] == "QUALIFY_AND_CHECK_EXISTING_FOOTPRINT",
               "unsupported source audit")
    for pin in plan["source_pins"]:
        g0.pinned_path(root, pin)
    docs = {k: read_pin(root, p) for k, p in plan["inputs"].items()}
    packet, review_plan, reply = (docs[k] for k in ("review_packet", "review_plan", "reply"))
    o2.require(packet["plan_sha256"] == o2.fingerprint_json(review_plan), "source review plan changed")
    subject_keys = ("view", "id", "frame_index", "time_sec", "candidate_input_index", "candidate_sha256", "source", "source_xy")
    o2.require([{k: s[k] for k in subject_keys} for s in packet["subjects"]] == review_plan["subjects"],
               "review subjects differ from frozen plan")
    for pin in review_plan["inputs"].values():
        g0.pinned_path(root, pin)
    g0.pinned_path(root, packet["source_recording"])
    g0.pinned_path(root, plan["regional_opposition_reply"])
    g0.pinned_path(root, {"path": plan["review_image"], "sha256": packet["image_sha256"]})
    o2.require(o2.fingerprint_json(packet["candidate_population"]) == plan["population_sha256"],
               "complete source population changed")
    rows = source_candidate_acceptance(packet, reply)
    prior = rgb_rim_audit(root, docs["rim_plan"])
    o2.require(prior == docs["rim_readout"], "previous rim result changed")
    o2.require(plan["inputs"]["prepared"] == docs["rim_plan"]["inputs"]["prepared"], "prior population pin changed")
    prepared = docs["prepared"]
    sources = {u["source_recording"]["sha256"] for u in prepared["units"]}
    o2.require(packet["source_recording"]["sha256"] not in sources, "source expansion is not independent recording")
    recipe = InspectionRecipe.from_dict(docs["recipe"])
    o2.require(len(recipe.glasses) == 1, "one archived glass required")
    glass = recipe.glasses[0]
    o2.require(glass.geometry.ellipse.center_x == plan["geometry"]["source_x"]
               and not glass.geometry.exclusions and not glass.geometry.artifact_templates,
               "archived setup changed")
    frames = {}
    for subject in packet["subjects"]:
        source_path = g0.pinned_path(root, subject["source_image"])
        with Image.open(source_path) as image:
            source_rgb = np.array(image.convert("RGB"))
        bundle = build_mask_bundle(source_rgb[:, :, ::-1].copy(), glass)
        o2.require(list(bundle.crop_origin) == plan["geometry"]["origin"]
                   and list(bundle.crop.shape[:2]) == plan["geometry"]["shape"], "source geometry changed")
        pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
        bands = check_saved_visibility(pre.gray, bundle.effective_mask, pre.glare_mask,
                                       subject["center_sector"], bundle.crop_origin)
        native_rgb = bundle.crop[:, :, ::-1].copy()
        visible = (bundle.effective_mask > 0) & (pre.glare_mask == 0)
        frame_rows = [u for u in rows if u["frame_index"] == subject["frame_index"]]
        for u in frame_rows:
            x, y = u["source_xy"]
            o2.require(float(x).is_integer() and math.isfinite(y), "invalid source coordinate")
            u["variants"] = [{"source_xy": [x, sy], **rgb.context(native_rgb, visible,
                [int(x)-bundle.crop_origin[0], sy-bundle.crop_origin[1]])}
                for sy in sorted({math.floor(y), math.ceil(y)})]
            u["availability"] = "AVAILABLE" if all(v["status"] == "AVAILABLE" for v in u["variants"]) else "UNAVAILABLE_REQUIRED_VARIANT"
        frames[str(subject["frame_index"])] = {"source_image": subject["source_image"],
            "origin": list(bundle.crop_origin), "shape": list(native_rgb.shape[:2]),
            "rgb_sha256": rgb.native.array_hash(native_rgb), "visible_sha256": rgb.native.array_hash(visible),
            "saved_band_checks": bands, "candidate_count": len(frame_rows),
            "scope": "Reconstructed unchanged Recipe/preprocessing; no geometric recalibration or physical visibility label."}
    o2.require(sum(f["candidate_count"] for f in frames.values()) == len(rows), "source frame coverage incomplete")
    accepted = [u for u in rows if u["practical_acceptance"] == "ACCEPTED_APPROXIMATION"]
    missing = [u["id"] for u in accepted if u["availability"] != "AVAILABLE"]
    coverage = {}
    for c in prior["controls"]:
        key = c["source_recording"]["path"]
        counts = coverage.setdefault(key, {"accepted_or_corresponding": 0, "opposed": 0})
        counts["accepted_or_corresponding" if c["qualified_target"] == 0 else "opposed"] += 1
    coverage[packet["source_recording"]["path"]] = {"accepted_or_corresponding": len(accepted), "opposed": 0}
    return {"schema": SOURCE_SCHEMA, "plan_sha256": o2.fingerprint_json(plan), "inputs": plan["inputs"],
        "status": "SCOPED_CANDIDATES_QUALIFIED_INPUT_INCOMPLETE" if missing else "SCOPED_CANDIDATES_QUALIFIED_INPUT_AVAILABLE",
        "counts": {"all_records": len(prepared["units"])+len(rows),
            "oil_candidates": sum(u["is_oil_candidate"] for u in prepared["units"])+len(rows),
            "sample3_candidates": len(rows), "new_accepted": len(accepted), "new_opposed": 0,
            "sample3_unreviewed": len(rows)-len(accepted), "sample3_available": sum(u["availability"] == "AVAILABLE" for u in rows),
            "total_qualified_controls": len(prior["controls"])+len(accepted), "source_recordings": len(coverage)},
        "source_coverage": coverage, "missing_accepted_inputs": missing, "frames": frames, "candidate_rows": rows,
        "regional_opposition": {"reply": plan["regional_opposition_reply"], "candidate_targets_created": 0,
            "scope": "C external-frame structure remains regional; D remains unassessable. Neither is new whole-candidate truth."},
        "input_contract": "Existing complete visible 7x7 patches in two +/-12 native strips, floor/ceil required; no new model.",
        "previous_trial_status": prior["status"], "training_executed": False, "new_model_calls": 0,
        "production_changed": False, "future_fit": "RESERVED_PENDING_SEPARATE_CONTRACT",
        "untouched_holdout_recordings": 0, "native_path_labels_created": False, "physical_calibration": "NOT_EVALUATED"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    option = parser.add_mutually_exclusive_group()
    option.add_argument("--policy-manifest", type=Path,
                        help="Optional frozen necessary-condition audit; no threshold selection")
    option.add_argument("--public-candidate-manifest", type=Path,
                        help="Bind practical candidate replies to saved public-source scores")
    option.add_argument("--rgb-rim-manifest", type=Path,
                        help="Bind post-trial rim review without refitting or relabeling other candidates")
    option.add_argument("--source-candidate-manifest", type=Path,
                        help="Qualify reviewed source candidates and check the existing native input footprint")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    manifest = o2.read_json(args.manifest)
    started = g0.time.monotonic()
    result = audit(args.root.resolve(), manifest)
    if args.policy_manifest:
        result = policy_audit(args.root.resolve(), manifest, result, o2.read_json(args.policy_manifest))
    if args.public_candidate_manifest:
        result = public_candidate_audit(args.root.resolve(), o2.read_json(args.public_candidate_manifest))
    if args.rgb_rim_manifest:
        result = rgb_rim_audit(args.root.resolve(), o2.read_json(args.rgb_rim_manifest))
    if args.source_candidate_manifest:
        result = source_candidate_audit(args.root.resolve(), o2.read_json(args.source_candidate_manifest))
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
