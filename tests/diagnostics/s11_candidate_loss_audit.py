"""Refine an EXISTING W3 audit's recorded exclusions without reading media.

This is a diagnostic readout, not a detector, classifier, or field acceptance.
The old audit, predictions, labels and packets are never rewritten or rerun.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "s11-recorded-candidate-loss-v1"
MAX_INPUT_BYTES = 256 * 1024 * 1024
LIMITATION = (
    "Recorded exclusions are not physical identity or the first causal video failure. "
    "Row membership cannot certify each member's scalar eligibility. "
    "An allowed but unselected member does not distinguish competition, ambiguity, "
    "continuation filtering or suppression. No target truth is inferred."
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def phase_filter(phase: dict) -> dict:
    require(isinstance(phase, dict), "phase must be an object")
    mode = phase.get("allowed_mode")
    if mode is None or "allowed_tracklet_ids" not in phase:
        return {"status": "UNAVAILABLE", "mode": mode, "allowed_tracklet_ids": None}
    require(mode in {"hard_gate", "owner_bounded", "unconstrained"}, "unknown allowed_mode")
    ids = phase["allowed_tracklet_ids"]
    if mode == "unconstrained":
        require(ids is None, "unconstrained IDs must be null")
    else:
        require(isinstance(ids, list) and all(isinstance(i, str) and i for i in ids),
                "bounded IDs must be nonempty strings in a list")
        require(len(set(ids)) == len(ids), "duplicate allowed owner IDs")
        require((len(ids) == 0) == (mode == "hard_gate"), "mode/ID inventory mismatch")
    return {"status": "RECORDED", "mode": mode, "allowed_tracklet_ids": copy.deepcopy(ids)}


def refine_funnel(funnel: dict) -> dict:
    require(isinstance(funnel, dict), "funnel must be an object")
    result = {"source_funnel_sha256": fingerprint(funnel), "source_funnel": copy.deepcopy(funnel),
              "status": funnel.get("status"), "candidates": [], "limitation": LIMITATION}
    if funnel.get("status") != "RECORDED":
        require(funnel.get("status") in {"UNAVAILABLE", "NOT_REQUESTED"}, "unknown funnel status")
        return result
    gate = phase_filter(funnel.get("phase", {}))
    result["phase_filter"] = gate
    selection = funnel.get("selection", {})
    require(isinstance(selection, dict), "selection must be an object")
    selection_available = "selected_candidate" in selection
    selected = selection.get("selected_candidate")
    require(selected is None or isinstance(selected, dict), "selected candidate must be an object or null")
    candidates = funnel.get("candidates")
    require(isinstance(candidates, list) and len(candidates) <= 128, "bounded candidate inventory required")
    seen, selected_members = set(), []
    for candidate in candidates:
        idx = candidate.get("candidate_input_index")
        require(type(idx) is int and idx >= 0 and idx not in seen, "invalid/duplicate candidate index")
        seen.add(idx)
        row_out = {"candidate_input_index": idx, "legacy_first_known_loss": candidate.get("first_known_loss"),
                   "recorded_exclusions": [], "final_choice_diagnosed": False}
        if candidate.get("status") == "NOT_IN_RETAINED_REFS":
            row_out["boundary"] = "UNKNOWN_BEFORE_RETAINED_REFS"
            result["candidates"].append(row_out)
            continue
        require(candidate.get("status") == "RECORDED", "unknown candidate status")
        member, row = candidate["member"], candidate["row"]
        require(isinstance(member, dict) and isinstance(row, dict), "member/row must be objects")
        for key, value in (("tracklet_admitted", member.get("tracklet_admitted")),
                           ("selected", member.get("selected")),
                           ("phase_admitted", row.get("phase_admitted")),
                           ("publishable", row.get("publishable"))):
            require(type(value) is bool, f"{key} must be a recorded boolean")
        require(member.get("candidate_offset") == idx, "member/candidate index mismatch")
        require(type(member.get("candidate_offset")) is int, "member index must be integer")
        owner = row.get("tracklet_id")
        require(owner is None or isinstance(owner, str) and owner, "invalid row owner")
        exclusions = row_out["recorded_exclusions"]
        for passed, reason in ((member["tracklet_admitted"], "TRACKLET_NOT_ADMITTED"),
                               (row["phase_admitted"], "ROW_NOT_PHASE_ADMITTED"),
                               (row["publishable"], "ROW_NOT_PUBLISHABLE")):
            if not passed:
                exclusions.append(reason)
        if gate["status"] == "RECORDED":
            if gate["mode"] == "hard_gate":
                exclusions.append("PHASE_HARD_GATE")
            elif gate["mode"] == "owner_bounded" and owner not in gate["allowed_tracklet_ids"]:
                exclusions.append("OWNER_NOT_ALLOWED")
        row_out["row_tracklet_id"] = owner
        if member["selected"]:
            require(not exclusions, "selected candidate contradicts recorded exclusions")
            require(selected is not None and selection_available, "selected member lacks final selection")
            require(all(selected.get(k) == member.get(k) for k in ("candidate_offset", "source", "y")),
                    "selected member/source/Y mismatch")
            selected_members.append(idx)
            row_out["boundary"] = "SELECTED_SAME_FRAME"
        elif exclusions:
            row_out["boundary"] = exclusions[0]
        elif gate["status"] == "UNAVAILABLE":
            row_out["boundary"] = "PHASE_FILTER_UNAVAILABLE"
        else:
            row_out["boundary"] = "FINAL_SELECTION_UNRESOLVED"
        row_out["selection_outcome"] = ("UNAVAILABLE" if not selection_available else
                                         "NONE_SELECTED" if selected is None else "A_CANDIDATE_SELECTED")
        result["candidates"].append(row_out)
    require(len(selected_members) == int(selected is not None), "selection/member inventory mismatch")
    result["boundary_counts"] = dict(Counter(c["boundary"] for c in result["candidates"]))
    return result


def refine_audit(document: dict) -> dict:
    require(document.get("schema_version") in {"s11-o2-target-audit-v1", "s11-o2-structure-context-audit-v1"},
            "input must be an existing W3 target/structure audit")
    require(document.get("production_decisions_emitted") is False and document.get("auto_acceptance") is False,
            "input is not a non-authoritative audit")
    cases, scores = document.get("target_audit"), document.get("scores")
    require(isinstance(cases, list) and 1 <= len(cases) <= 64 and isinstance(scores, list),
            "expected 1..64 audit cases and their source score inventory")
    identities = [c.get("case_id") for c in cases]
    require(all(isinstance(i, str) and i for i in identities) and len(set(identities)) == len(identities),
            "invalid/duplicate audit case IDs")
    score_ids = [s.get("case_id") for s in scores]
    require(len(set(score_ids)) == len(score_ids) and set(score_ids) == set(identities),
            "case/score inventory mismatch")
    by_case = {s["case_id"]: s for s in scores}
    rows = []
    for case in cases:
        source = by_case[case["case_id"]]
        inventory = source["candidates"]
        require(isinstance(inventory, list) and len(inventory) <= 128, "score inventory exceeds bound")
        indices = [c["candidate_input_index"] for c in inventory]
        require(all(type(i) is int and i >= 0 for i in indices) and len(set(indices)) == len(indices),
                "invalid/duplicate score indices")
        witness_hashes = {c["candidate_input_index"]: c["witness_sha256"] for c in inventory}
        require(all(isinstance(h, str) and re.fullmatch(r"[0-9a-f]{64}", h) for h in witness_hashes.values()),
                "invalid recorded witness hash")
        refined = refine_funnel(case["recorded_funnel"])
        if refined["status"] == "RECORDED":
            require({c["candidate_input_index"] for c in refined["candidates"]} == set(indices),
                    "funnel/score candidate inventory mismatch")
        physical = {}
        for summary in case.get("context_summary", []):
            idx, identity = summary["candidate_input_index"], summary["identity"]
            require(idx in witness_hashes, "context identity index is not in score inventory")
            require(identity in {"interface", "non_interface", "uncertain", "unreviewed"},
                    "unknown physical identity annotation")
            require(idx not in physical or physical[idx] == identity, "conflicting contextual identities")
            physical[idx] = identity
        cross_counts = {}
        for candidate in refined["candidates"]:
            idx = candidate["candidate_input_index"]
            identity = physical.get(idx, "NOT_AVAILABLE")
            candidate.update(witness_sha256=witness_hashes[idx], recorded_physical_identity=identity,
                             target_role="NOT_IMPORTED")
            bucket = cross_counts.setdefault(identity, Counter())
            bucket[candidate["boundary"]] += 1
        rows.append({"case_id": case["case_id"],
                     "source_identity": {k: source.get(k) for k in ("frame_index", "glass_id", "packet_sha256")},
                     "identity_boundary_counts": {k: dict(v) for k, v in cross_counts.items()},
                     "readout": refined})
    return {"schema_version": SCHEMA, "status": "READOUT_ONLY", "auto_acceptance": False,
            "production_decisions_emitted": False, "detector_rerun": False, "video_read": False,
            "field_efficacy": "NOT_EVALUATED", "source_field_disposition": document.get("field_disposition"),
            "cases": rows, "limitation": LIMITATION,
            "input_scope": "Hash-pinned existing audit; source packets/media are not independently reverified.",
            "target_scope": "Physical interface annotations are preserved, not promoted to uppermost-target truth."}


def render(report: dict) -> str:
    lines = ["# S11 recorded candidate-loss readout", "", LIMITATION, "",
             "No detector/media/label rerun. Candidate counts are correlated, not accuracy estimates.", ""]
    for case in report["cases"]:
        case_id = case["case_id"].replace("\n", " ").replace("|", "\\|")
        lines += [f"## {case_id}", "", f"Status: {case['readout']['status']}", "",
                  "| Recorded physical identity | Recorded boundary | Candidate count |",
                  "|---|---|---:|"]
        for identity, counts in case["identity_boundary_counts"].items():
            lines += [f"| {identity} | {boundary} | {count} |" for boundary, count in sorted(counts.items())]
        lines.append("")
    return "\n".join(lines)


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def run(audit_path: Path, output: Path, expected_sha256: str) -> dict:
    source, output = Path(audit_path).resolve(), Path(output).resolve()
    require(isinstance(expected_sha256, str) and re.fullmatch(r"[0-9a-f]{64}", expected_sha256),
            "expected SHA-256 must be 64 lowercase hex digits")
    require(not output.exists(), "output directory already exists")
    require(source.stat().st_size <= MAX_INPUT_BYTES, "audit exceeds byte bound")
    with source.open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    require(len(raw) <= MAX_INPUT_BYTES, "audit grew beyond byte bound")
    require(hashlib.sha256(raw).hexdigest() == expected_sha256, "input SHA-256 mismatch")
    document = json.loads(raw, object_pairs_hook=strict_object, parse_constant=reject_constant)
    require(isinstance(document, dict), "audit must be an object")
    code_sha = file_sha(Path(__file__))
    report = refine_audit(document)
    report.update(source_audit_sha256=expected_sha256, script_sha256=code_sha)
    require(file_sha(source) == expected_sha256, "input changed during readout")
    output.mkdir(parents=True, exist_ok=False)
    with (output / "readout.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
    with (output / "summary.md").open("x", encoding="utf-8") as handle:
        handle.write(render(report))
    require(file_sha(source) == expected_sha256, "input changed during publication")
    require(file_sha(Path(__file__)) == code_sha, "script changed during readout")
    receipt = {"schema_version": SCHEMA, "status": "COMPLETE", "meaning": "readout completion only",
               "source_before_sha256": expected_sha256, "source_after_sha256": file_sha(source),
               "script_sha256": code_sha, "detector_rerun": False, "video_read": False,
               "auto_acceptance": False,
               "outputs": {name: file_sha(output / name) for name in ("readout.json", "summary.md")}}
    with (output / "complete.json").open("x", encoding="utf-8") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2, allow_nan=False)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True, help="Existing W3 experiment.json; not a video")
    parser.add_argument("--expected-sha256", required=True, help="Previously recorded raw audit-file SHA-256")
    parser.add_argument("--output", type=Path, required=True, help="New directory; never overwrite an old result")
    args = parser.parse_args()
    try:
        result = run(args.audit, args.output, args.expected_sha256)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.error(str(error))
    print(f"READOUT COMPLETE: {len(result['cases'])} cases; detector/field efficacy NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
