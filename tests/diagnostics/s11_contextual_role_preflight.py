"""Post-CR1 saved-context contract audit; no fitting, inference or decisions.

CR1 has a different input envelope from O1 raster witnesses. This adapter reuses
the O2 identity/validation primitives and retains references to the frozen score
table; it neither changes that table nor introduces a production sidecar.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import gzip
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_interface_shadow_evaluation as o2

SCHEMA = "s11-contextual-role-preflight-v1"
POLICY = "local-role-and-absolute-support-v1"
ROLES = ("interface", "structure", "texture")
MODES = ("full", "local")
TIE_EPSILON = 1e-6
MAX_INPUT_BYTES = 8 * 1024**2


def read_pinned(root, entry):
    relative = Path(entry["path"])
    o2.require(not relative.is_absolute() and ".." not in relative.parts, "input must be repository relative")
    path = root / relative
    o2.require(o2.sha256_file(path) == entry["sha256"], f"input hash mismatch: {relative}")
    if path.suffix != ".gz":
        o2.require(path.stat().st_size <= MAX_INPUT_BYTES, "input exceeds bounded JSON size")
        return o2.read_json(path)
    with gzip.open(path, "rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    o2.require(len(data) <= MAX_INPUT_BYTES, "expanded input exceeds bounded JSON size")
    return json.loads(data.decode("utf-8"))


def mode_observation(mode):
    """Preserve every class value; a missing class cannot become a winner."""
    scores = mode.get("scores", {})
    o2.require(set(scores) <= set(ROLES), "unexpected role score")
    for name, value in scores.items():
        o2.number(value, name)
        # Match the frozen CR1 verifier's rounding allowance; never clip scores.
        o2.require(-1 - 1e-12 <= value <= 1 + 1e-12, "similarity outside normalized-vector range")
    if set(scores) != set(ROLES):
        return {"availability": "MISSING_ROLE_SCORES", "preference": None,
                "interface_margin": None, "raw": copy.deepcopy(mode)}
    ordered = sorted(ROLES, key=scores.get, reverse=True)
    gap = scores[ordered[0]] - scores[ordered[1]]
    tied = gap <= TIE_EPSILON
    preference = None if tied else ordered[0]
    o2.require(mode.get("status") == ("TIE" if tied else "MEASURED"), "rank status mismatch")
    o2.require(mode.get("preference") == preference, "rank preference mismatch")
    o2.require(math.isclose(o2.number(mode.get("top_margin"), "top margin"), gap,
                            rel_tol=0, abs_tol=1e-12), "rank margin mismatch")
    return {"availability": "NUMERICAL_TIE" if tied else "MEASURED",
            "preference": preference,
            "interface_margin": scores["interface"] - max(scores["structure"], scores["texture"]),
            "raw": copy.deepcopy(mode)}


def observe(record, geometry):
    """Read one original candidate/context; labels never enter this calculation."""
    query, measured = record["query"], record["measurement"]
    o2.require(query == measured["query"], "candidate/measurement join mismatch")
    o2.require(measured["status"] == "COMPARED", "unexecuted source measurement")
    x, y = (o2.number(v, "source coordinate") for v in query["source_xy"])
    o2.integer(query["frame"], "source frame")
    if "candidate_index" in query:
        o2.integer(query["candidate_index"], "candidate index")
    variants = measured["variants"]
    expected = [[x, value] for value in sorted({math.floor(y), math.ceil(y)})]
    o2.require([v["source_center_xy"] for v in variants] == expected,
               "required floor/ceil variants missing, reordered or rebound")
    view = []
    for variant in variants:
        columns = variant["common_columns"]
        o2.require(all(type(c) is int for c in columns), "support columns must be integers")
        o2.require(columns == sorted(set(columns)) and set(columns) <= set(geometry["native_columns"]),
                   "invalid common support")
        o2.require(set(variant["modes"]) <= set(MODES), "unexpected representation")
        support = len(columns) >= geometry["minimum_common_columns"]
        sx, sy = variant["source_center_xy"]
        ox, oy = geometry["origin_xy"]
        height, width = geometry["native_shape"]
        crop_complete = 12 <= sx - ox < width - 12 and 12 <= sy - oy < height - 12
        if variant["status"] == "MEASURED":
            o2.require(support and crop_complete, "measured variant has invalid crop/support")
        else:
            o2.require(variant["status"] == "UNAVAILABLE_COMMON_SUPPORT_OR_CROP",
                       "unknown variant status")
            o2.require(not variant["modes"] and not columns, "unavailable variant contains scores/support")
        view.append({"source_center_xy": list(variant["source_center_xy"]),
                     "common_columns": list(columns), "source_status": variant["status"],
                     "crop_complete": crop_complete,
                     "modes": {mode: mode_observation(variant["modes"].get(mode, {})) for mode in MODES}})
    aggregates = {}
    for mode in MODES:
        observations = [v["modes"][mode] for v in view]
        available = [v for v in observations if v["availability"] != "MISSING_ROLE_SCORES"]
        complete = len(available) == len(view)
        preferences = [v["preference"] for v in observations]
        if not complete:
            status = "PARTLY_UNAVAILABLE" if available else "UNAVAILABLE"
        elif any(v["availability"] == "NUMERICAL_TIE" for v in available):
            status = "NUMERICAL_TIE"
        elif len(set(preferences)) != 1:
            status = "VARIANT_DISAGREEMENT"
        else:
            status = "MEASURED"
        aggregates[mode] = {
            "availability": status,
            "variant_preferences": preferences,
            "minimum_interface_similarity": min(v["raw"]["scores"]["interface"] for v in available) if complete else None,
            "minimum_interface_margin": min(v["interface_margin"] for v in available) if complete else None,
        }
    return {"decision": "NOT_EVALUATED", "calibration": "UNCALIBRATED",
            "claim_scope": "regional_context_only", "native_role": "NOT_EVALUATED",
            "scalar_localization": "NOT_EVALUATED", "variants": view, "modes": aggregates}


def audit(root, manifest):
    o2.require(manifest["schema"] == SCHEMA, "unsupported preflight schema")
    policy = manifest["policy"]
    o2.require(policy["id"] == POLICY and policy["tau_support"] is None,
               "this preflight cannot choose or execute an operating point")
    o2.require(policy["tie_epsilon"] == TIE_EPSILON, "numerical tie rule changed")
    o2.require(manifest["partitions"]["calibration"] == [] and manifest["partitions"]["holdout"] == [],
               "existing exposed corpus cannot supply a new calibration/holdout")
    o2.require(manifest["resources"]["encoder_forwards"] == 0, "saved audit cannot run an encoder")
    source = manifest["source_identity"]
    o2.require(o2.sha256_file(root / source["path"]) == source["sha256"], "source recording changed")
    inputs = {name: read_pinned(root, entry) for name, entry in manifest["inputs"].items()}
    pre, prepared, data, roster = (inputs[k] for k in ("cr1_preflight", "prepared", "readout", "scene_roster"))
    o2.require(o2.fingerprint_json(pre["geometry"]) == manifest["geometry_sha256"], "geometry changed")
    o2.require(o2.fingerprint_json(pre["references"]) == manifest["bank_sha256"], "reference bank changed")
    o2.require(data["followup_preflight_sha256"] == manifest["inputs"]["followup_preflight"]["sha256"],
               "readout/followup preflight mismatch")
    o2.require(prepared["preflight_sha256"] == manifest["inputs"]["cr1_preflight"]["sha256"],
               "prepared/geometry preflight mismatch")
    records = data["results"]
    o2.require(len(records) <= manifest["resources"]["max_records"], "candidate capacity exceeded")
    o2.unique([r["query"] for r in records], "id", "query roster")
    o2.require([r["query"] for r in records] == prepared["queries"], "complete original roster/order required")
    o2.require(data["independent_recordings"] == 1 and data["untouched_holdout_recordings"] == 0,
               "source exposure changed")
    captures = {}
    for entry in prepared["captures"]:
        path = entry["path"]
        capture = read_pinned(root, {"path": path, "sha256": pre["original_capture_pins"][path]})
        current = capture["current"]
        o2.require(current["frame_index"] == entry["frame"], "capture/frame mismatch")
        o2.require(current["time_sec"] == prepared["original_frame_times"][str(entry["frame"])] ,
                   "actual timestamp mismatch")
        captures[entry["frame"]] = (path, capture)
    rows, duplicates = [], defaultdict(list)
    for index, record in enumerate(records):
        query = record["query"]
        observation = observe(record, pre["geometry"])
        binding = captures.get(query["frame"])
        frame = binding[1]["current"] if binding else None
        candidate_index = query.get("candidate_index")
        native_support = {"status": "CONTEXT_CONTROL_NO_CANDIDATE"}
        if candidate_index is not None:
            o2.require(frame is not None and candidate_index < len(frame["candidates"]), "candidate index outside original frame")
            candidate = frame["candidates"][candidate_index]
            o2.require(candidate["source"] == query["source"] and candidate["y"] == query["source_xy"][1],
                       "original candidate source/Y mismatch")
            native_support = {}
            for name, scalar in (("oil_interface_witness", "canonical_y"), ("oil_measurement_lineage", "source_y")):
                sidecar = binding[1]["state"].get(name, {})
                matches = [(i, row) for i, row in enumerate(sidecar.get("candidates", []))
                           if row["candidate_input_index"] == candidate_index]
                o2.require(len(matches) <= 1, "duplicate native witness binding")
                if not matches:
                    native_support[name] = {"status": "UNAVAILABLE_NO_BOUND_RECORD"}
                    continue
                i, native = matches[0]
                o2.require(sidecar["source_frame_index"] == query["frame"] and sidecar["glass_id"] == frame["glass_id"],
                           "native witness frame/Glass mismatch")
                o2.require(native["source"] == query["source"] and native[scalar] == query["source_xy"][1],
                           "native witness source/Y mismatch")
                native_support[name] = {"path": binding[0], "pointer": f"/state/{name}/candidates/{i}",
                                        "sha256": o2.fingerprint_json(native),
                                        "status": native.get("status", native.get("measurement_status")),
                                        "reason": native.get("reason", native.get("contour", {}).get("native_path_reason")),
                                        "physical_role": "NOT_EVALUATED"}
        key = (query["frame"], *query["source_xy"])
        duplicates[key].append(index)
        rows.append({"query": copy.deepcopy(query), "time_sec": frame["time_sec"] if frame else None,
                     "time_status": "SOURCE_CAPTURE" if frame else "CONTEXT_CONTROL_TIME_UNBOUND",
                     "glass_id": frame["glass_id"] if frame else None,
                     "native_support": native_support,
                     "partition": "development", "exposure": record["exposure"],
                     "raw_measurement": {"input": "readout", "pointer": f"/results/{index}/measurement",
                                         "sha256": o2.fingerprint_json(record["measurement"])},
                     "decision": observation["decision"], "modes": observation["modes"]})
    for indices in duplicates.values():
        first = records[indices[0]]["measurement"]["variants"]
        o2.require(all(records[i]["measurement"]["variants"] == first for i in indices),
                   "same-support records disagree")
    group_ids = [unit["id"] for unit in roster["units"]]
    o2.require(group_ids == manifest["scene_claims"]["p0_unit_ids"], "P0 scene/Windows obligations lost")
    return {"schema": SCHEMA, "policy_id": POLICY,
            "manifest_sha256": o2.fingerprint_json(manifest), "status": "CONTRACT_VERIFIED_CALIBRATION_NOT_READY",
            "calibration": "UNCALIBRATED", "tau_support": None, "decision": "NOT_EVALUATED",
            "production_changed": False, "encoder_forwards": 0, "raw_scores_duplicated": False,
            "counts": {"records": len(rows), "candidates": sum("candidate_index" in r["query"] for r in rows),
                       "context_controls": sum("candidate_index" not in r["query"] for r in rows),
                       "distinct_supports": len(duplicates), "duplicate_support_groups": sum(len(v) > 1 for v in duplicates.values()),
                       "labels": dict(Counter(r["query"]["label"] for r in rows)),
                       "exposure": dict(Counter(r["exposure"] for r in rows)),
                       "availability": {mode: dict(Counter(r["modes"][mode]["availability"] for r in rows)) for mode in MODES},
                       "independent_recordings": 1, "untouched_holdout_recordings": 0},
            "gates": {"numeric_calibration": "NOT_READY", "native_role": "NOT_QUALIFIED",
                      "production_shadow": "NOT_ENTERED", "o2": "OPEN", "field": "NOT_EVALUATED"},
            "blockers": manifest["blockers"], "scene_claims": manifest["scene_claims"],
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New managed work path; never overwrites")
    args = parser.parse_args()
    manifest = o2.read_json(args.manifest)
    result = audit(args.root.resolve(), manifest)
    o2.require(len((json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
               <= manifest["resources"]["max_output_bytes"], "output exceeds preflight budget")
    o2.write_new(args.output, result)
    print(json.dumps({"status": result["status"], "counts": result["counts"], "decision": result["decision"]}))


if __name__ == "__main__":
    main()
