"""Recorded exclusion contracts; none of these tests measures detector accuracy."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_candidate_loss_audit as audit
from tests.diagnostics import s11_shadow_experiment as old_experiment
from tests.unit.test_s11_shadow_experiment import inputs


def funnel(mode="hard_gate", ids=()):
    return {"status": "RECORDED", "phase": {"value": "filled_barrier", "reason": "fixture",
            "allowed_mode": mode, "allowed_tracklet_ids": None if ids is None else list(ids)},
        "selection": {"resolved_kind": "unknown", "selected_candidate": None}, "routes": {},
        "candidates": [{"candidate_input_index": 0, "status": "RECORDED", "first_known_loss": "not_selected",
            "member": {"candidate_offset": 0, "source": "material_path", "y": 40.0,
                       "tracklet_admitted": True, "selected": False},
            "row": {"row_hypothesis_id": "row0", "tracklet_id": "owner0", "phase_admitted": True, "publishable": True}},
            {"candidate_input_index": 1, "status": "NOT_IN_RETAINED_REFS", "first_known_loss": "UNKNOWN_BEFORE_RETAINED_REFS"}]}


def document():
    return {"schema_version": "s11-o2-target-audit-v1", "auto_acceptance": False,
            "production_decisions_emitted": False, "field_disposition": "FIELD FAIL",
            "scores": [{"case_id": "case", "frame_index": 10, "glass_id": "glass", "packet_sha256": "a"*64,
                        "candidates": [{"candidate_input_index": i, "witness_sha256": str(i)*64} for i in range(2)]}],
            "target_audit": [{"case_id": "case", "recorded_funnel": funnel(),
                              "context_summary": [{"candidate_input_index": 0, "identity": "interface"}]}]}


@pytest.mark.parametrize("mode,ids,boundary", [
    ("hard_gate", (), "PHASE_HARD_GATE"),
    ("owner_bounded", ("other",), "OWNER_NOT_ALLOWED"),
    ("owner_bounded", ("owner0",), "FINAL_SELECTION_UNRESOLVED"),
    ("unconstrained", None, "FINAL_SELECTION_UNRESOLVED"),
])
def test_row_admission_does_not_bypass_actual_owner_filter(mode, ids, boundary):
    source = funnel(mode, ids); before = copy.deepcopy(source)
    result = audit.refine_funnel(source)
    assert result["candidates"][0]["boundary"] == boundary
    assert result["candidates"][0]["legacy_first_known_loss"] == "not_selected"
    assert result["candidates"][1]["boundary"] == "UNKNOWN_BEFORE_RETAINED_REFS"
    assert result["source_funnel"] == before == source
    assert not result["candidates"][0]["final_choice_diagnosed"]


@pytest.mark.parametrize("field", ["allowed_mode", "allowed_tracklet_ids"])
def test_missing_owner_filter_is_unavailable_not_unconstrained(field):
    source = funnel(); del source["phase"][field]
    assert audit.refine_funnel(source)["candidates"][0]["boundary"] == "PHASE_FILTER_UNAVAILABLE"


@pytest.mark.parametrize("mode,ids", [("hard_gate", None), ("hard_gate", ["owner0"]),
                                      ("owner_bounded", []), ("owner_bounded", ["x", "x"]),
                                      ("unconstrained", []), ("bogus", None)])
def test_invalid_owner_contract_fails_closed(mode, ids):
    with pytest.raises(ValueError):
        audit.refine_funnel(funnel(mode, ids))


@pytest.mark.parametrize("owner,key,boundary", [("member", "tracklet_admitted", "TRACKLET_NOT_ADMITTED"),
    ("row", "phase_admitted", "ROW_NOT_PHASE_ADMITTED"), ("row", "publishable", "ROW_NOT_PUBLISHABLE")])
def test_all_recorded_exclusions_remain_visible(owner, key, boundary):
    source = funnel(); source["candidates"][0][owner][key] = False
    result = audit.refine_funnel(source)["candidates"][0]
    assert result["boundary"] == boundary
    assert result["recorded_exclusions"] == [boundary, "PHASE_HARD_GATE"]


def selected_funnel():
    source = funnel("owner_bounded", ("owner0",))
    member = source["candidates"][0]["member"]
    member["selected"] = True
    source["selection"] = {"resolved_kind": "oil", "selected_candidate":
                           {k: member[k] for k in ("candidate_offset", "source", "y")}}
    return source


def test_selection_is_exact_recorded_member_not_identity_accuracy():
    source = selected_funnel()
    result = audit.refine_funnel(source)
    assert result["candidates"][0]["boundary"] == "SELECTED_SAME_FRAME"
    assert "physical identity" in result["limitation"]


@pytest.mark.parametrize("fault", ["blocked", "selected_y", "selected_source", "selected_offset",
                                  "duplicate", "index_bool", "gate_bool", "missing_selection"])
def test_malformed_or_contradictory_selection_is_rejected(fault):
    source = selected_funnel()
    if fault == "blocked": source["phase"].update(allowed_mode="hard_gate", allowed_tracklet_ids=[])
    if fault == "selected_y": source["selection"]["selected_candidate"]["y"] += 1
    if fault == "selected_source": source["selection"]["selected_candidate"]["source"] = "another"
    if fault == "selected_offset": source["selection"]["selected_candidate"]["candidate_offset"] = 1
    if fault == "duplicate": source["candidates"].append(copy.deepcopy(source["candidates"][0]))
    if fault == "index_bool": source["candidates"][0]["member"]["candidate_offset"] = False
    if fault == "gate_bool": source["candidates"][0]["row"]["phase_admitted"] = 1
    if fault == "missing_selection": del source["selection"]["selected_candidate"]
    with pytest.raises(ValueError): audit.refine_funnel(source)


def test_no_physical_identity_or_target_role_is_inferred_from_exclusion():
    source = document(); before = copy.deepcopy(source)
    result = audit.refine_audit(source)
    assert result["cases"][0]["identity_boundary_counts"] == {
        "interface": {"PHASE_HARD_GATE": 1}, "NOT_AVAILABLE": {"UNKNOWN_BEFORE_RETAINED_REFS": 1}}
    assert result["cases"][0]["readout"]["candidates"][0]["target_role"] == "NOT_IMPORTED"
    source["target_audit"][0]["context_summary"][0]["identity"] = "non_interface"
    counter = audit.refine_audit(source)
    assert result["cases"][0]["readout"]["candidates"][0]["boundary"] == counter["cases"][0]["readout"]["candidates"][0]["boundary"]
    assert result["auto_acceptance"] is False and result["field_efficacy"] == "NOT_EVALUATED"
    assert result["cases"][0]["readout"]["source_funnel"] == before["target_audit"][0]["recorded_funnel"]


def save_input(tmp_path):
    path = tmp_path / "existing.json"
    path.write_text(json.dumps(document()), encoding="utf-8")
    return path, audit.file_sha(path)


def test_cli_is_standalone_foreign_cwd_unicode_and_preserves_all_inputs(tmp_path):
    source, digest = save_input(tmp_path); before = source.read_bytes()
    script = tmp_path / "독립 도구.py"; script.write_bytes(Path(audit.__file__).read_bytes())
    cwd = tmp_path / "다른 폴더"; cwd.mkdir()
    out = tmp_path / "새 결과"
    result = subprocess.run([sys.executable, str(script), "--audit", str(source),
                             "--expected-sha256", digest, "--output", str(out)],
                            cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                            text=True, encoding="utf-8", timeout=20)
    assert result.returncode == 0, result.stderr
    receipt = json.loads((out / "complete.json").read_text(encoding="utf-8"))
    assert receipt["source_before_sha256"] == receipt["source_after_sha256"] == digest
    assert all(audit.file_sha(out / name) == pin for name, pin in receipt["outputs"].items())
    assert source.read_bytes() == before and not receipt["auto_acceptance"]
    with pytest.raises(ValueError, match="already exists"):
        audit.run(source, out, digest)


@pytest.mark.parametrize("fault", ["hash", "schema", "case_duplicate", "case_inventory", "candidate_inventory",
                                  "witness_hash", "conflicting_identity", "unsafe_acceptance"])
def test_corrupt_or_wrong_audit_never_publishes_completion(tmp_path, fault):
    data = document()
    if fault == "schema": data["schema_version"] = "another"
    if fault == "case_duplicate": data["target_audit"] *= 2
    if fault == "case_inventory": data["scores"][0]["case_id"] = "other"
    if fault == "candidate_inventory": data["scores"][0]["candidates"].pop()
    if fault == "witness_hash": data["scores"][0]["candidates"][0]["witness_sha256"] = "unknown"
    if fault == "conflicting_identity": data["target_audit"][0]["context_summary"].append({"candidate_input_index":0,"identity":"non_interface"})
    if fault == "unsafe_acceptance": data["auto_acceptance"] = True
    path = tmp_path / "input.json"; path.write_text(json.dumps(data), encoding="utf-8")
    digest = "f"*64 if fault == "hash" else audit.file_sha(path)
    out = tmp_path / "out"
    with pytest.raises(ValueError): audit.run(path, out, digest)
    assert not (out / "complete.json").exists()


@pytest.mark.parametrize("raw", [b'{"a":1,"a":2}', b'{"value":NaN}', b'[]'])
def test_ambiguous_json_rejected(tmp_path, raw):
    path = tmp_path / "input.json"; path.write_bytes(raw)
    with pytest.raises(ValueError): audit.run(path, tmp_path / "out", audit.file_sha(path))
    assert not (tmp_path / "out" / "complete.json").exists()


def test_input_mutation_after_readout_leaves_no_completion(tmp_path, monkeypatch):
    source, digest = save_input(tmp_path)
    original = audit.render
    def mutate(report):
        source.write_bytes(source.read_bytes() + b" ")
        return original(report)
    monkeypatch.setattr(audit, "render", mutate)
    with pytest.raises(ValueError, match="input changed"):
        audit.run(source, tmp_path / "out", digest)
    assert not (tmp_path / "out" / "complete.json").exists()


def test_original_w3_schema_and_missing_sequence_are_preserved(inputs, tmp_path):
    baseline = tmp_path / "baseline"; old_experiment.run([inputs], baseline)
    w3 = tmp_path / "w3"
    old_experiment.run([inputs], w3, target_audit=True, reference=baseline / "experiment.json")
    source = w3 / "experiment.json"
    prior_files = {p: p.read_bytes() for parent in (inputs.parent, baseline, w3) for p in parent.iterdir() if p.is_file()}
    report = audit.run(source, tmp_path / "readout", audit.file_sha(source))
    assert all(c["readout"]["status"] == "NOT_REQUESTED" and not c["readout"]["candidates"] for c in report["cases"])
    assert all(path.read_bytes() == content for path, content in prior_files.items())


def test_empty_candidate_inventory_is_not_success():
    data = document(); data["scores"][0]["candidates"] = []
    case = data["target_audit"][0]
    case["recorded_funnel"]["candidates"] = []; case["context_summary"] = []
    report = audit.refine_audit(data)
    assert report["cases"][0]["identity_boundary_counts"] == {}
    assert not report["auto_acceptance"] and report["field_efficacy"] == "NOT_EVALUATED"
