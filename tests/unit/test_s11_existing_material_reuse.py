"""Regression guards for claim-scoped reuse, not detector accuracy tests."""
from copy import deepcopy
import json

import pytest

from tests.diagnostics import s11_existing_material_reuse as reuse


def row(label="confirmed_target", *, index=1, physical="HISTORICAL_ONLY", practical="NOT_REVIEWED"):
    return {"query": {"id": f"q{index}", "frame": 10, "candidate_index": index,
                      "source": "material_path", "source_xy": [50, 60.0], "label": label},
            "time_sec": 1.0, "glass_id": "g", "baseline_pointer": f"/rows/{index}",
            "physical_qualification": physical, "practical_acceptance": practical,
            "native_support": {}, "path": {"representation": "POOLED_SECTOR_SAMPLES",
                                            "status": "native_generator_path"}}


def control(r):
    q = r["query"]
    return {"frame": q["frame"], "candidate_input_index": q["candidate_index"],
            "source": q["source"], "source_y": q["source_xy"][1],
            "time_sec": r["time_sec"], "target_role": q["label"],
            "authority": {"frame": q["frame"], "index": q["candidate_index"],
                          "source": q["source"], "y": q["source_xy"][1],
                          "authority": "ANCHOR_ELIGIBLE", "reason": "test", "failed_gates": []}}


def test_physical_practical_and_historical_scopes_remain_separate():
    positive = row()
    negative = row("rejected_target", index=2)
    withdrawn = row(index=3, physical="NOT_QUALIFIED")
    practical = row("UNREVIEWED", index=4, physical="NOT_QUALIFIED", practical="ACCEPTED_APPROXIMATION")
    rows = [positive, negative, withdrawn, practical]
    original = deepcopy(rows)
    output = reuse.oil_units(rows, [control(r) for r in rows[:3]])
    assert [r["physical_claim"] for r in output] == [
        "TARGET_CORRESPONDENCE", "OPPOSED_OIL_TARGET", "NOT_QUALIFIED", "NOT_QUALIFIED"]
    assert output[3]["practical_acceptance"] == "ACCEPTED_APPROXIMATION"
    assert not any(r["training_label_created"] or r["native_path_role_ready"] for r in output)
    assert rows == original


@pytest.mark.parametrize("field,value", [("source", "other"), ("source_y", 61.0),
    ("candidate_input_index", 2), ("frame", 11), ("time_sec", 2.0), ("target_role", "rejected_target")])
def test_control_must_match_exact_subject(field, value):
    candidate = row()
    altered = control(candidate)
    altered[field] = value
    with pytest.raises(ValueError):
        reuse.oil_units([candidate], [altered])


def test_same_y_different_candidate_is_not_a_join():
    candidate = row(index=1)
    other = row(index=2)
    with pytest.raises(ValueError):
        reuse.oil_units([candidate], [control(other)])


def test_duplicate_controls_and_queries_are_rejected():
    candidate = row()
    c = control(candidate)
    with pytest.raises(ValueError):
        reuse.oil_units([candidate], [c, c])
    with pytest.raises(ValueError):
        reuse.oil_units([candidate, candidate], [c])


def test_authority_identity_is_not_inferred_from_control_label():
    candidate = row()
    c = control(candidate)
    c["authority"]["index"] = 9
    with pytest.raises(ValueError):
        reuse.oil_units([candidate], [c])


@pytest.mark.parametrize("pointer", ["/a/-1", "/a/3", "/missing", "a/0"])
def test_invalid_json_pointer_is_rejected(pointer):
    with pytest.raises(ValueError):
        reuse.exact_pointer({"a": [1, 2]}, pointer)


def test_source_derivatives_cannot_cross_split(tmp_path):
    a, b = tmp_path / "a.bin", tmp_path / "b.bin"
    a.write_bytes(b"same recording")
    b.write_bytes(a.read_bytes())
    digest = reuse.o2.sha256_file(a)
    sources = [{"path": "a.bin", "sha256": digest, "use": "DEVELOPMENT"},
               {"path": "b.bin", "sha256": digest, "use": "EXPOSED_EVALUATION"}]
    with pytest.raises(ValueError, match="conflicting"):
        reuse.source_groups(tmp_path, sources)
    sources[1]["use"] = "DEVELOPMENT"
    assert len(reuse.source_groups(tmp_path, sources)) == 1


def test_source_hash_change_fails_closed(tmp_path):
    path = tmp_path / "source.bin"
    path.write_bytes(b"source")
    pin = {"path": "source.bin", "sha256": reuse.o2.sha256_file(path), "use": "DEVELOPMENT"}
    path.write_bytes(b"changed source")
    with pytest.raises(ValueError, match="hash"):
        reuse.source_groups(tmp_path, [pin])


def test_reuse_is_not_training_entrypoint(tmp_path):
    with pytest.raises(ValueError, match="training"):
        reuse.audit(tmp_path, {"schema": reuse.SCHEMA, "training_executed": True})


@pytest.mark.parametrize("field,value", [("source", "other"), ("canonical_y", 61.0), ("candidate_input_index", 5)])
def test_rehashed_support_cannot_point_at_another_candidate(tmp_path, field, value):
    candidate = row()
    subject = {"source": "material_path", "canonical_y": 60.0, "candidate_input_index": 1}
    subject[field] = value
    path = tmp_path / "capture.json"
    path.write_text(json.dumps({"subjects": [subject]}))
    candidate["native_support"] = {"oil_interface_witness": {
        "path": "capture.json", "pointer": "/subjects/0",
        "sha256": reuse.o2.fingerprint_json(subject)}}
    with pytest.raises(ValueError, match="index/source/Y"):
        reuse.verify_support(tmp_path, candidate, {})


def test_cli_refuses_overwrite_before_loading_inputs(tmp_path, monkeypatch):
    path = tmp_path / "old.json"
    path.write_text("frozen")
    monkeypatch.setattr("sys.argv", ["reuse", "--manifest", str(tmp_path / "missing.json"),
                                     "--output", str(path)])
    with pytest.raises(ValueError, match="overwrite"):
        reuse.main()
    assert path.read_text() == "frozen"


def test_same_candidate_under_different_query_ids_is_rejected():
    candidate = row()
    alias = deepcopy(candidate)
    alias["query"]["id"] = "another-query"
    with pytest.raises(ValueError, match="duplicate candidate identity"):
        reuse.oil_units([candidate, alias], [control(candidate)])


def test_json_pointer_escaping():
    assert reuse.exact_pointer({"a/b": {"~key": [7]}}, "/a~1b/~0key/0") == 7


def test_unreviewed_records_are_retained_not_negative():
    candidate = row("UNREVIEWED")
    result = reuse.oil_units([candidate], [])
    assert len(result) == 1
    assert result[0]["physical_claim"] == "UNASSESSED"
    assert not result[0]["candidate_role_comparison_ready"]


def test_native_shape_reduction_is_not_silently_upscaled(tmp_path):
    baseline = {"contexts": [{"id": "test", "geometry": {"scale_xy": [2, 2]}}]}
    with pytest.raises(ValueError, match="reduced"):
        reuse.native_packet(tmp_path, {}, baseline, "test")
