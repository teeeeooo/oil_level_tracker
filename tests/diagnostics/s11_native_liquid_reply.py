"""Bind liquid-contact roles without changing frozen native qualifiers.

The old qualifier owns pixel/path inspection. This supplement owns the new
Foam-lower/liquid or air/liquid relation, never oscillation or pure patch labels.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_native_role_qualification as native
from tests.diagnostics import s11_semantic_role_preflight as readiness

o2 = native.o2
SCHEMA = "s11-native-liquid-role-reply-v1"
RELATIONS = {
    "FOAM_LOWER_LIQUID_INTERFACE": "Foam lower boundary in contact with bulk liquid",
    "LIQUID_AIR_INTERFACE": "Bulk-liquid upper boundary in contact with air",
}


def bind_subjects(reply, proposal, inspection):
    o2.require(set(reply) == {"schema", "proposal", "display", "response_ko", "answers"}
               and reply["schema"] == SCHEMA, "unsupported liquid reply")
    o2.text(reply["response_ko"], "verbatim response")
    o2.require(reply["display"] == proposal["display"], "display differs from proposal")
    subjects = native.by_id(proposal["subjects"], "proposal subject")
    inspected = native.by_id(inspection["subjects"], "inspected subject")
    answers = native.by_id(reply["answers"], "answer")
    o2.require(set(subjects) == set(inspected) == set(answers), "incomplete reply population")
    o2.require(inspection["status"] == "PROPOSAL_VERIFIED_PENDING_REVIEW"
               and inspection["qualified_units"] == 0, "expected unqualified path inspection")
    outputs = []
    for sid, subject in subjects.items():
        answer, checked = answers[sid], inspected[sid]
        o2.require(set(answer) == {"id", "subject_sha256", "statement_ko", "role", "scope"},
                   "invalid answer fields")
        o2.require(answer["subject_sha256"] == checked["subject_sha256"] ==
                   o2.fingerprint_json(subject), "review subject changed")
        o2.require(answer["scope"] == checked["scope"] == "DISPLAYED_FRAGMENT_ROLE_ONLY"
                   and not checked["dense_labels"] and checked["side_material_labels"] is None,
                   "unsupported review precision")
        o2.text(answer["statement_ko"], "subject statement")
        o2.require(answer["statement_ko"] in reply["response_ko"], "statement absent from response")
        o2.require(answer["role"] in RELATIONS, "unsupported liquid-contact role")
        output = deepcopy(checked)
        output.update(path_sha256=o2.fingerprint_json(subject["source_path_xy"]),
                      allowed_interpretations=[answer["role"]],
                      capability_target="LIQUID_UPPER", boundary_relation=RELATIONS[answer["role"]],
                      review_status="QUALIFIED_ROLE", role_source="USER_REPLY",
                      motion_qualified=False, scalar_qualified=False)
        outputs.append(output)
    return outputs


def qualify(root, reply):
    proposal = native.read_pin(root, reply["proposal"])
    inspection = native.qualify(root, dict(schema=native.INSPECTION_SCHEMA,
        proposal=reply["proposal"], display=reply["display"]))
    subjects = bind_subjects(reply, proposal, inspection)
    return dict(schema="s11-native-liquid-role-qualification-v1",
                reply_sha256=o2.fingerprint_json(reply), proposal=reply["proposal"], display=reply["display"],
                subjects=subjects, qualified_units=len(subjects), status="SCOPED_LIQUID_ROLE_BOUND",
                model_calls=0, training_executed=False, production_changed=False,
                scope="Displayed contact relation only; no pure-side, motion, scalar or whole-layer truth")


def merge_coverage(before, subjects):
    """Apply only previously unknown, exactly matched paths; never relabel old roles."""
    rows = deepcopy(before["rows"])
    overridden = []
    for subject in subjects:
        identity = (subject["source_recording"]["sha256"], subject["frame"], subject["path_sha256"])
        matches = [r for r in rows if (r["source_recording"]["sha256"], r["frame"], r["path_sha256"]) == identity]
        o2.require(len(matches) == 1, "new reply is absent or duplicated in saved observation population")
        row = matches[0]
        o2.require(row["id"] == subject["id"] and row["review_state"] == "UNREVIEWED"
                   and row["qualification"] is None and not row["allowed_boundary_roles"],
                   "refuse to overwrite an existing role or alias a subject")
        o2.require(subject["review_status"] == "QUALIFIED_ROLE" and
                   subject["capability_target"] == "LIQUID_UPPER" and
                   subject["allowed_interpretations"] in ([r] for r in RELATIONS),
                   "unsupported qualified role")
        o2.require(row["availability"] == subject["proposed_context"]["status"],
                   "saved and inspected context availability differ")
        row.update(certain_boundary_role="LIQUID_UPPER", allowed_boundary_roles=["LIQUID_UPPER"],
                   review_state="QUALIFIED_SINGLE_ROLE")
        overridden.append(row["id"])
    roles = readiness.coverage(rows)
    missing = [r for r in ("FOAM_UPPER", "LIQUID_UPPER") if not roles[r]["available_certain_paths"]]
    insufficient = [r for r in ("FOAM_UPPER", "LIQUID_UPPER")
                    if len(roles[r]["available_certain_sources"]) < 2]
    counts = {k: v for k, v in before["counts"].items() if k != "pairs"}
    counts.update(qualified=counts["qualified"] + len(overridden), unknown=counts["unknown"] - len(overridden))
    return dict(overridden_ids=overridden, population_counts=counts,
                unchanged_observation_rows=len(rows), review_states=dict(Counter(r["review_state"] for r in rows)),
                role_coverage=roles, source_group_folds=readiness.grouped_folds(rows),
                missing_single_role_positive=missing, missing_disjoint_positive_sources=insufficient,
                status="ROLE_SUPERVISION_INCOMPLETE" if missing or insufficient else
                       "INPUT_COVERAGE_ONLY_NOT_MODEL_ACCEPTANCE",
                training_executed=False, evaluation_executed=False, untouched_holdout_recordings=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--reply", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-plan", type=Path)
    parser.add_argument("--base-readout", type=Path)
    args = parser.parse_args()
    o2.require(not args.output.exists(), "refuse overwrite")
    o2.require(bool(args.base_plan) == bool(args.base_readout), "both readiness inputs are required")
    root = args.root.resolve()
    result = qualify(root, o2.read_json(args.reply))
    if args.base_plan:
        before = o2.read_json(args.base_readout)
        o2.require(readiness.audit(root, o2.read_json(args.base_plan)) == before,
                   "saved readiness differs from its frozen inputs")
        result["base_readout"] = {"path": str(args.base_readout.resolve().relative_to(root)),
                                  "sha256": o2.sha256_file(args.base_readout)}
        result["readiness_after_reply"] = merge_coverage(before, result["subjects"])
    o2.require(len(json.dumps(result).encode("utf-8")) < 100_000, "qualification output budget exceeded")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    o2.write_new(args.output, result)
    print(json.dumps({"status": result["status"], "qualified_units": result["qualified_units"]}))


if __name__ == "__main__":
    main()
