"""Bind separate saved semantic supports to scoped native roles, without fitting.

SCM-1 owns frozen inference; NRO/MRO and the qualifier own source/path truth.
This reader owns partial-role supervision and source-group readiness only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_semantic_context_trial as semantic

old, o2 = semantic.old, semantic.o2
SCHEMA = "s11-semantic-role-readiness-v1"
ROLES = ("FOAM_UPPER", "LIQUID_UPPER", "INTERNAL_FOAM_CHANGE", "STRUCTURE_BOUNDARY")
FAMILIES = {
    "EXTERNAL_FOAM_UPPER": "FOAM_UPPER",
    "OSCILLATING_LIQUID_UPPER": "LIQUID_UPPER",
    "INTERNAL_FOAM_CHANGE": "INTERNAL_FOAM_CHANGE",
    "STRUCTURE_BOUNDARY": "STRUCTURE_BOUNDARY",
}
INPUTS = dict(base=semantic.BASE, milk=semantic.MILK,
              manifest=semantic.HERE + "/manifest.json", readout=semantic.HERE + "/readout.json")


def scoped_roles(unit, subject):
    """Keep disjunctions; an external-surface label is not a Foam-only target."""
    if unit["qualification"] is None:
        o2.require(subject is None and unit["review_role"] is None, "unknown role was fabricated")
        return []
    o2.require(subject is not None and subject["id"] == unit["id"] and
               subject["subject_sha256"] == unit["subject_sha256"] and
               subject["capability_target"] == unit["review_role"] and
               subject["source_recording"] == unit["source_recording"] and
               subject["frame"] == unit["frame"], "qualified subject identity changed")
    o2.require(subject["scope"] == "DISPLAYED_FRAGMENT_ROLE_ONLY" and
               subject["dense_labels"] is False and subject["side_material_labels"] is None,
               "native role is not dense or pure-side truth")
    labels = subject["allowed_interpretations"]
    o2.require(labels and len(labels) == len(set(labels)) and set(labels) <= set(FAMILIES),
               "unsupported or repeated role interpretations")
    return sorted(FAMILIES[label] for label in labels)


def side_support(side, expected_count):
    """Audit saved arithmetic; return three observations, no fused score."""
    patches, means = side["prompt_patch_means"], side["prompt_means"]
    o2.require(type(expected_count) is int and expected_count > 0 and
               len(patches) == expected_count and len(means) == 3 and
               all(len(row) == 3 for row in patches), "semantic patch count/shape changed")
    values = [v for row in patches for v in row] + list(means)
    o2.require(all(type(v) in (int, float) and math.isfinite(v) and 0 <= v <= 1 for v in values),
               "invalid semantic support")
    expected = [math.fsum(row[i] for row in patches) / expected_count for i in range(3)]
    o2.require(all(abs(a-b) <= 1e-12 for a, b in zip(expected, means)), "saved prompt mean changed")
    return dict(zip(semantic.PROMPTS, means))


def bind_rows(units, saved_rows, qualifications):
    by_id = o2.unique(saved_rows, "id", "semantic row")
    o2.require(set(by_id) == {u["id"] for u in units} and len(units) == len(by_id),
               "complete semantic population changed")
    paths, source_paths, rows = set(), {}, []
    for index, unit in enumerate(units):
        sid = unit["id"]; raw = by_id[sid]; source = unit["source_recording"]
        previous = source_paths.setdefault(source["path"], source["sha256"])
        o2.require(previous == source["sha256"], "one recording path has conflicting source hashes")
        identity = (source["sha256"], unit["frame"], unit["path_sha256"])
        o2.require(identity not in paths, "duplicate source/frame/native path")
        paths.add(identity)
        o2.require(saved_rows[index]["id"] == sid and
                   raw["frame_key"] == f"{source['sha256']}:{unit['frame']}" and
                   raw["role"] == unit["review_role"] and raw["availability"] == unit["availability"],
                   "semantic row/source/role binding changed")
        subject = qualifications.get(sid)
        allowed = scoped_roles(unit, subject)
        sides = {}
        if unit["sides"]:
            o2.require(set(raw["sides"]) == set(unit["sides"]) == {"upper", "lower"},
                       "both ordered sides required")
            for side, descriptor in unit["sides"].items():
                sides[side] = side_support(raw["sides"][side], descriptor["shape"][0])
        else:
            o2.require(not raw["sides"] and raw["order_score"] is None, "unavailable row has a score")
        rows.append(dict(id=sid, source_recording=source, frame=unit["frame"],
                         path_sha256=unit["path_sha256"], qualification=unit["qualification"],
                         subject_sha256=unit["subject_sha256"],
                         original_interpretations=subject["allowed_interpretations"] if subject else [],
                         allowed_boundary_roles=allowed,
                         certain_boundary_role=allowed[0] if len(allowed) == 1 else None,
                         review_state="UNREVIEWED" if not allowed else
                                      "QUALIFIED_DISJUNCTION" if len(allowed) > 1 else "QUALIFIED_SINGLE_ROLE",
                         availability=unit["availability"], support=sides,
                         semantic_pointer=f"/rows/{index}",
                         pure_side_material_truth=False, physical_decision=None))
    return rows


def coverage(rows):
    result = {}
    for role in ROLES:
        certain = [r for r in rows if r["certain_boundary_role"] == role]
        available = [r for r in certain if r["support"]]
        result[role] = dict(certain_paths=[r["id"] for r in certain],
                            available_certain_paths=[r["id"] for r in available],
                            available_certain_sources=sorted({r["source_recording"]["sha256"] for r in available}),
                            compatible_disjunctions=[r["id"] for r in rows
                                if len(r["allowed_boundary_roles"]) > 1 and role in r["allowed_boundary_roles"]])
    return result


def grouped_folds(rows):
    """All derivatives of one source stay together; these are coverage checks."""
    sources = sorted({r["source_recording"]["sha256"] for r in rows})
    folds = []
    for held in sources:
        train = [r for r in rows if r["source_recording"]["sha256"] != held]
        test = [r for r in rows if r["source_recording"]["sha256"] == held]
        tc, ec = coverage(train), coverage(test)
        folds.append(dict(held_out_source=held, fitting_source_candidates=[s for s in sources if s != held],
                          fitting_subject_candidates=[r["id"] for r in train],
                          held_out_subjects=[r["id"] for r in test],
                          certain_available_counts={role: dict(fit=len(tc[role]["available_certain_paths"]),
                              held_out=len(ec[role]["available_certain_paths"])) for role in ROLES},
                          training_executed=False, evaluation_executed=False,
                          untouched_holdout=False))
    return folds


def audit(root, plan):
    o2.require(plan["schema"] == SCHEMA and plan["scope"] == "SAVED_INPUT_READINESS_ONLY",
               "unsupported role-readiness plan")
    o2.require(set(plan["inputs"]) == set(INPUTS), "readiness input roster changed")
    for key, path in INPUTS.items():
        o2.require(plan["inputs"][key]["path"] == path, "unexpected saved input")
        old.verified(root, plan["inputs"][key])
    for pin in plan["sources"]:
        old.verified(root, pin)
    manifest = o2.read_json(root / INPUTS["manifest"])
    saved = o2.read_json(root / INPUTS["readout"])
    o2.require(saved["schema"] == semantic.SCHEMA and saved["manifest"] == plan["inputs"]["manifest"] and
               manifest["configuration"] == semantic.CONFIG, "saved semantic protocol changed")
    for pin in manifest["sources"] + manifest["inputs"]:
        old.verified(root, pin)
    units, frames, _, pairs, counts = semantic.inputs(root)
    o2.require(saved["counts"] == manifest["counts"] == counts and manifest["frames"] == frames and
               manifest["pairs"] == pairs, "saved frame/population contract changed")
    qualifications, documents = {}, {}
    for unit in units:
        pin = unit["qualification"]
        if pin is None:
            continue
        path = old.verified(root, pin)
        if str(path) not in documents:
            documents[str(path)] = o2.unique(o2.read_json(path)["subjects"], "id", "qualified role")
        qualifications[unit["id"]] = documents[str(path)][unit["id"]]
    rows = bind_rows(units, saved["rows"], qualifications)
    roles = coverage(rows)
    missing = [role for role in ("FOAM_UPPER", "LIQUID_UPPER")
               if not roles[role]["available_certain_paths"]]
    insufficient_sources = [role for role in ("FOAM_UPPER", "LIQUID_UPPER")
                           if len(roles[role]["available_certain_sources"]) < 2]
    return dict(schema=SCHEMA, plan_sha256=o2.fingerprint_json(plan), inputs=plan["inputs"],
                status="ROLE_SUPERVISION_INCOMPLETE" if missing or insufficient_sources else
                       "INPUT_COVERAGE_ONLY_NOT_MODEL_ACCEPTANCE",
                counts=counts, review_states=dict(Counter(r["review_state"] for r in rows)),
                rows=rows, role_coverage=roles, source_group_folds=grouped_folds(rows),
                missing_single_role_positive=missing, missing_disjoint_positive_sources=insufficient_sources,
                untouched_holdout_recordings=0, training_executed=False, new_model_calls=0,
                new_video_decodes=0, production_changed=False, physical_labels_created=0,
                classification_or_threshold_selected=False,
                scope="Separate saved prompt observations and partial native roles; no fused score, fit or physical winner")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    result = audit(args.root.resolve(), o2.read_json(args.plan))
    o2.require(len(json.dumps(result).encode("utf-8")) < 200_000, "readiness output budget exceeded")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    o2.write_new(args.output, result)
    print(json.dumps({k: result[k] for k in ("status", "counts", "missing_single_role_positive")}))


if __name__ == "__main__":
    main()
