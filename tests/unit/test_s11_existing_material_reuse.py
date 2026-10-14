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


def policy_fixture(tmp_path):
    rows = [row(index=0), row(index=1), row("rejected_target", index=2),
            row(index=3, physical="NOT_QUALIFIED"), row("UNREVIEWED", index=4)]
    for i, r in enumerate(rows):
        r["query"]["initial_reference"] = i == 0
    units = reuse.oil_units(rows, [control(r) for r in rows[:3]])
    baseline = {"rows": [{"query": r["query"], "modes": {"local": {
        "availability": "MEASURED", "minimum_interface_similarity": a,
        "minimum_interface_margin": 0.1}}} for r, a in zip(rows, [0.5, 0.8, 0.6, 0.9, 1.0])],
        "counts": {"independent_recordings": 1}}

    def write(name, value):
        path = tmp_path / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return {"path": name, "sha256": reuse.o2.sha256_file(path)}

    reused = {"oil_units": units}
    manifest = {"inputs": {"oil_readout": write("baseline.json", baseline)}}
    plan = {"schema": reuse.POLICY_SCHEMA, "reuse_manifest_sha256": reuse.o2.fingerprint_json(manifest),
        "reuse_readout": write("reuse.json", reused),
        "policy": {"id": reuse.g0.cr1.POLICY, "tau_support": None, "tie_epsilon": 1e-6},
        "operation": "NECESSARY_CONDITION_NO_THRESHOLD_SELECTION",
        "required_control_outcome": {"positive_loss": 0, "opposition_accepted": 0},
        "controls": [{"id": u["query"]["id"], "query_sha256": u["query_sha256"],
                      "claim": u["physical_claim"], "initial_reference": u["query"]["initial_reference"]}
                     for u in units[:3]]}
    return manifest, reused, plan


def test_policy_reference_and_nonphysical_cases_are_separate(tmp_path):
    manifest, reused, plan = policy_fixture(tmp_path)
    report = reuse.policy_audit(tmp_path, manifest, reused, plan)
    assert report["results"]["all_current_controls"]["status"] == "CONTRADICTED_BY_CONTROLS"
    assert report["results"]["excluding_initial_reference"]["status"] == "NOT_FALSIFIED_ON_EXPOSED_CONTROLS"
    assert report["counts"]["population"] == 5
    assert report["counts"]["claims"]["UNASSESSED"] == 1
    assert [r["id"] for r in report["nonphysical_facets"]] == ["q3"]


@pytest.mark.parametrize("change", ["threshold", "roster", "claim", "reference", "hash", "rebound_pointer"])
def test_policy_freeze_cannot_relabel_or_rebind_controls(tmp_path, change):
    manifest, reused, plan = policy_fixture(tmp_path)
    if change == "threshold":
        plan["policy"]["tau_support"] = 0.7
    elif change == "roster":
        plan["controls"].pop()
    elif change == "claim":
        plan["controls"][1]["claim"] = "OPPOSED_OIL_TARGET"
    elif change == "reference":
        plan["controls"][1]["initial_reference"] = True
    elif change == "hash":
        plan["reuse_readout"]["sha256"] = "0" * 64
    else:
        reused["oil_units"][1]["baseline_pointer"] = "/rows/0"
        path = tmp_path / "reuse.json"
        path.write_text(json.dumps(reused), encoding="utf-8")
        plan["reuse_readout"]["sha256"] = reuse.o2.sha256_file(path)
    with pytest.raises(ValueError):
        reuse.policy_audit(tmp_path, manifest, reused, plan)


def public_fixture():
    raw = {"frame_index": 10, "time_sec": 1.0, "candidates": [
        {"source": f"family-{i}", "y": y, "kind": "oil_air"} for i, y in enumerate((40.0, 40.5, 43.0, 40.0))]}
    packet = {"frame_index": 10, "time_sec": 1.0, "source_x": 52, "image_sha256": "image",
              "candidates": [{"candidate_input_index": i, "candidate_sha256": reuse.o2.fingerprint_json(c),
                              "source": c["source"], "kind": c["kind"], "representative_y": c["y"],
                              "review_requested": i in (0, 1)} for i, c in enumerate(raw["candidates"])]}
    reply = {"schema": "s11-public-oil-candidate-acceptance-v1", "review_packet_sha256": reuse.o2.fingerprint_json(packet),
             "frame_index": 10, "time_sec": 1.0, "source_x": 52, "image_sha256": "image",
             "scope": "PRACTICAL_APPROXIMATION_AT_THIS_FRAME_ONLY", "user_text": "모두 허용",
             "subjects": [{k: c[k] for k in ("candidate_input_index", "candidate_sha256")}
                          for c in packet["candidates"] if c["review_requested"]]}
    score = {"status": "MEASURED", "preference": "interface", "scores": {
        "interface": 0.7, "structure": 0.2, "texture": 0.3}, "top_margin": 0.4}
    transfer = {"geometry": {"native_shape": [104, 104, 3], "source_origin_xy": [0, 0]},
                "results": [{"query": {"source_xy": [52, y]}, "status": "MEASURED",
                             "common_columns": list(range(-12, 13)), "modes": {"full": deepcopy(score), "local": deepcopy(score)}}
                            for y in (40, 41)]}
    return raw, packet, reply, transfer


def test_exact_saved_candidate_scores_preserve_unknown_neighbors_and_missing_anchors():
    raw, packet, reply, transfer = public_fixture()
    accepted = reuse.qualify_candidate_acceptance(packet, reply)
    before = deepcopy((raw, packet, reply, transfer))
    rows = reuse.saved_candidate_observations(raw, packet, transfer, accepted)
    assert rows[1]["required_anchors"] == [[52, 40], [52, 41]]
    assert rows[2]["score_status"] == "NOT_SAVED" and rows[2]["modes"] is None
    assert rows[3]["saved_score_pointers"] == rows[0]["saved_score_pointers"]
    assert rows[3]["practical_acceptance"] == "NOT_REVIEWED"
    assert all(r["physical_role"] == r["native_path_role"] == "NOT_QUALIFIED" for r in rows)
    assert (raw, packet, reply, transfer) == before


@pytest.mark.parametrize("field,value", [("frame_index", 11), ("time_sec", 2.0), ("source_x", 53),
    ("image_sha256", "different"), ("scope", "GLOBAL_TOLERANCE"), ("user_text", "일부 허용")])
def test_public_reply_cannot_broaden_or_rebind_acceptance(field, value):
    _, packet, reply, _ = public_fixture()
    reply[field] = value
    with pytest.raises(ValueError):
        reuse.qualify_candidate_acceptance(packet, reply)


@pytest.mark.parametrize("change", ["omit_subject", "subject_hash", "duplicate_anchor", "candidate_rebound"])
def test_public_subject_and_score_corruption_rejected(change):
    raw, packet, reply, transfer = public_fixture()
    if change == "omit_subject":
        reply["subjects"].pop()
    elif change == "subject_hash":
        reply["subjects"][0]["candidate_sha256"] = "changed"
    elif change == "duplicate_anchor":
        transfer["results"].append(deepcopy(transfer["results"][0]))
    else:
        raw["candidates"][0]["source"] = "same-Y-other-candidate"
    with pytest.raises(ValueError):
        accepted = reuse.qualify_candidate_acceptance(packet, reply)
        reuse.saved_candidate_observations(raw, packet, transfer, accepted)


def test_public_fractional_candidate_keeps_unfavorable_variant():
    raw, packet, reply, transfer = public_fixture()
    transfer["results"][1]["modes"]["local"] = {"status": "MEASURED", "preference": "texture",
        "scores": {"interface": 0.4, "structure": 0.2, "texture": 0.6}, "top_margin": 0.2}
    rows = reuse.saved_candidate_observations(raw, packet, transfer, reuse.qualify_candidate_acceptance(packet, reply))
    assert rows[1]["modes"]["local"]["availability"] == "VARIANT_DISAGREEMENT"
    assert rows[1]["modes"]["local"]["minimum_interface_margin"] == pytest.approx(-0.2)


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


def rgb_rim_fixture():
    source = {"path": "source.mp4", "sha256": "source"}
    image = {"path": "frame.png", "sha256": "pixels"}
    units, rows = [], []
    for i in range(6):
        query = {"id": f"q{i}", "frame": 10, "candidate_index": i,
                 "source_xy": [52, 40 if i in (2, 5) else 30+i], "source": f"family-{i}"}
        target = i if i < 2 else None
        partition = "fit" if i < 2 else "unreviewed"
        units.append({"id": query["id"], "query": query, "query_sha256": reuse.o2.fingerprint_json(query),
            "frame_id": "f10", "source_recording": source, "is_oil_candidate": True,
            "partition": partition, "target": target, "availability": "AVAILABLE", "variants": [{}]})
        values = [[-3, 2]] if target == 1 else [[3, -2]]
        decision = "OPPOSED_OIL_CANDIDATE" if target == 1 else "OIL_CANDIDATE_COMPATIBLE"
        rows.append({"id": query["id"], "target": target, "partition": partition, "availability": "AVAILABLE",
                     "logits": values, "mean_color_logits": deepcopy(values),
                     "decision": decision, "mean_color_decision": decision})
    prepared = {"units": units, "frames": {"f10": {"rgb": image}}}
    packet = {"frame_id": "f10", "image_sha256": "display", "source_image": image, "source_recording": source,
        "subjects": [{k: u[k] for k in ("id", "query", "query_sha256")} for u in units[2:5]]}
    reply = {"schema": "s11-candidate-rgb-rim-reply-v1", "frame_id": "f10", "image_sha256": "display",
        "review_packet_sha256": reuse.o2.fingerprint_json(packet),
        "scope": "DISPLAYED_CANDIDATES_AT_THIS_FRAME_ONLY",
        "user_text": "노란 하단 후보는 구조물이야 glass 주변 rim임.",
        "subjects": [{"id": s["id"], "query_sha256": s["query_sha256"], "physical_role": "GLASS_RIM_STRUCTURE",
                      "oil_acceptance": "REJECTED_APPROXIMATION"} for s in packet["subjects"]]}
    return packet, reply, prepared, {"rows": rows}


def test_rgb_rim_reply_preserves_original_trial_and_same_y_unknown():
    args = rgb_rim_fixture()
    before = deepcopy(args)
    controls = reuse.rgb_review_controls(*args)
    assert len(controls) == 5
    assert [c["id"] for c in controls if c["evaluation_group"] == "POST_TRIAL_REVIEW"] == ["q2", "q3", "q4"]
    assert controls[2]["original_target"] is None and controls[2]["qualified_target"] == 1
    assert controls[2]["physical_role"] == "GLASS_RIM_STRUCTURE"
    assert controls[2]["native_path_role"] == "NOT_EXTENDED"
    assert all(c["id"] != "q5" for c in controls)
    assert args == before


@pytest.mark.parametrize("change", ["image", "scope", "source", "frame", "subject_omitted", "duplicate_subject",
    "neighbor_query", "population_omitted", "original_target", "missing_variant", "nan", "decision", "unavailable"])
def test_rgb_rim_binding_fails_on_corrupt_or_broadened_evidence(change):
    packet, reply, prepared, readout = rgb_rim_fixture()
    if change == "image":
        reply["image_sha256"] = "changed"
    elif change == "scope":
        reply["scope"] = "ALL_LOWER_CANDIDATES"
    elif change == "source":
        prepared["units"][2]["source_recording"] = {"path": "other.mp4", "sha256": "other"}
    elif change == "frame":
        prepared["units"][2]["frame_id"] = "f11"
    elif change == "subject_omitted":
        reply["subjects"].pop()
    elif change == "duplicate_subject":
        packet["subjects"].append(deepcopy(packet["subjects"][0]))
        reply["subjects"].append(deepcopy(reply["subjects"][0]))
        reply["review_packet_sha256"] = reuse.o2.fingerprint_json(packet)
    elif change == "neighbor_query":
        packet["subjects"][0]["query"] = deepcopy(prepared["units"][5]["query"])
        reply["review_packet_sha256"] = reuse.o2.fingerprint_json(packet)
    elif change == "population_omitted":
        readout["rows"].pop()
    elif change == "original_target":
        readout["rows"][2]["target"] = 1
    elif change == "missing_variant":
        prepared["units"][2]["variants"].append({})
    elif change == "nan":
        readout["rows"][2]["logits"][0][0] = float("nan")
    elif change == "decision":
        readout["rows"][2]["decision"] = "OPPOSED_OIL_CANDIDATE"
    else:
        prepared["units"][2]["availability"] = "UNAVAILABLE_REQUIRED_VARIANT"
        readout["rows"][2]["availability"] = "UNAVAILABLE_REQUIRED_VARIANT"
    with pytest.raises(ValueError):
        reuse.rgb_review_controls(packet, reply, prepared, readout)


def test_rgb_review_keeps_all_fractional_variants_and_disagreement():
    packet, reply, prepared, readout = rgb_rim_fixture()
    prepared["units"][2]["variants"].append({})
    row = readout["rows"][2]
    for field, decision in (("logits", "decision"), ("mean_color_logits", "mean_color_decision")):
        row[field].append([-2, 1])
        row[decision] = "UNKNOWN"
    controls = reuse.rgb_review_controls(packet, reply, prepared, readout)
    assert controls[2]["margins"] == {"logits": -3, "mean_color_logits": -3}
    assert controls[2]["decisions"]["decision"] == "UNKNOWN"
