"""Contract controls for the offline CR1 preflight; no model or local media needed."""
from __future__ import annotations

import copy
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from tests.diagnostics import s11_contextual_role_preflight as role


GEOMETRY = {"native_shape": [104, 104], "origin_xy": [0, 0],
            "native_columns": list(range(-12, 13)), "minimum_common_columns": 8}


def mode(interface=0.7, structure=0.2, texture=0.3):
    scores = dict(zip(role.ROLES, (interface, structure, texture)))
    ordered = sorted(scores, key=scores.get, reverse=True)
    margin = scores[ordered[0]] - scores[ordered[1]]
    tied = margin <= role.TIE_EPSILON
    return {"status": "TIE" if tied else "MEASURED", "preference": None if tied else ordered[0],
            "scores": scores, "top_margin": margin}


def record(y=40.0):
    query = {"id": "fixture-0", "frame": 10, "source_xy": [52, y], "candidate_index": 0,
             "source": "fixture", "label": "UNREVIEWED"}
    variants = [{"source_center_xy": [52, v], "common_columns": list(range(-12, 13)),
                 "modes": {"full": mode(0.4, 0.2, 0.6), "local": mode()}, "status": "MEASURED"}
                for v in sorted({int(y), int(y) + (y % 1 != 0)})]
    return {"query": query, "exposure": "outside_reference_episode_development",
            "measurement": {"query": copy.deepcopy(query), "status": "COMPARED", "variants": variants}}


def test_full_texture_and_tiny_local_advantage_are_preserved_without_decision():
    item = record(40.5)
    item["measurement"]["variants"][1]["modes"]["local"] = mode(0.6, 0.2, 0.599998)
    before = copy.deepcopy(item)
    result = role.observe(item, GEOMETRY)
    assert result["modes"]["local"]["minimum_interface_similarity"] == 0.6
    assert result["modes"]["local"]["minimum_interface_margin"] == pytest.approx(0.000002)
    assert result["modes"]["full"]["variant_preferences"] == ["texture", "texture"]
    assert result["decision"] == result["native_role"] == result["scalar_localization"] == "NOT_EVALUATED"
    assert item == before
    for original, observed in zip(item["measurement"]["variants"], result["variants"]):
        for name in role.MODES:
            assert observed["modes"][name]["raw"] == original["modes"][name]


def test_labels_cannot_change_measurements():
    item = record()
    original = role.observe(item, GEOMETRY)
    item["query"]["label"] = item["measurement"]["query"]["label"] = "confirmed_target"
    assert role.observe(item, GEOMETRY) == original


def test_unit_vector_roundoff_is_retained_at_the_frozen_verifier_precision():
    item = record()
    value = 1.0000000000000002
    item["measurement"]["variants"][0]["modes"]["local"] = mode(value)
    result = role.observe(item, GEOMETRY)
    assert result["modes"]["local"]["minimum_interface_similarity"] == value


@pytest.mark.parametrize("unavailable", ["all", "one_variant", "one_role"])
def test_missing_support_or_class_never_uses_favorable_remainder(unavailable):
    item = record(40.5)
    variants = item["measurement"]["variants"]
    if unavailable == "one_role":
        del variants[1]["modes"]["local"]["scores"]["texture"]
    else:
        for v in variants if unavailable == "all" else variants[1:]:
            v.update(status="UNAVAILABLE_COMMON_SUPPORT_OR_CROP", common_columns=[], modes={})
    result = role.observe(item, GEOMETRY)
    local = result["modes"]["local"]
    assert local["availability"] == ("UNAVAILABLE" if unavailable == "all" else "PARTLY_UNAVAILABLE")
    assert local["minimum_interface_similarity"] is None
    assert local["minimum_interface_margin"] is None
    assert result["decision"] == "NOT_EVALUATED"


@pytest.mark.parametrize("change,expected", [(mode(0.5, 0.2, 0.5), "NUMERICAL_TIE"),
                                           (mode(0.5, 0.2, 0.6), "VARIANT_DISAGREEMENT")])
def test_ties_and_disagreement_remain_distinct(change, expected):
    item = record(40.5)
    item["measurement"]["variants"][1]["modes"]["local"] = change
    result = role.observe(item, GEOMETRY)
    assert result["modes"]["local"]["availability"] == expected
    assert result["modes"]["local"]["minimum_interface_similarity"] == 0.5


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True, 1.01])
def test_invalid_scores_are_rejected(value):
    item = record()
    item["measurement"]["variants"][0]["modes"]["local"]["scores"]["interface"] = value
    with pytest.raises(ValueError):
        role.observe(item, GEOMETRY)


@pytest.mark.parametrize("error", ["missing_variant", "rebound_query", "wrong_rank", "bad_support"])
def test_corrupted_identity_or_geometry_is_not_abstention(error):
    item = record(40.5)
    if error == "missing_variant":
        item["measurement"]["variants"].pop()
    elif error == "rebound_query":
        item["measurement"]["query"]["candidate_index"] = 1
    elif error == "wrong_rank":
        item["measurement"]["variants"][0]["modes"]["local"]["preference"] = "texture"
    else:
        item["measurement"]["variants"][0]["common_columns"] = [0, 0]
    with pytest.raises(ValueError):
        role.observe(item, GEOMETRY)


def fixture_manifest(tmp_path):
    root = tmp_path / "source space"
    root.mkdir()

    def write(name, data):
        path = root / name
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        path.write_bytes(gzip.compress(encoded) if name.endswith(".gz") else encoded)
        return {"path": name, "sha256": role.o2.sha256_file(path)}

    item = record()
    capture = {"current": {"frame_index": 10, "time_sec": 0.333, "glass_id": "synthetic",
                            "candidates": [{"source": "fixture", "y": 40.0}]}, "state": {}}
    cap = write("capture.json", capture)
    pre = {"geometry": GEOMETRY, "references": {"fixture": "same frozen bank"},
           "original_capture_pins": {cap["path"]: cap["sha256"]}}
    inputs = {"cr1_preflight": write("pre.json", pre), "followup_preflight": write("followup.json", {})}
    prepared = {"queries": [item["query"]], "captures": [{"path": "capture.json", "frame": 10}],
                "original_frame_times": {"10": 0.333}, "preflight_sha256": inputs["cr1_preflight"]["sha256"]}
    inputs["prepared"] = write("prepared.json", prepared)
    inputs["readout"] = write("scores.json.gz", {"results": [item], "independent_recordings": 1,
        "untouched_holdout_recordings": 0, "followup_preflight_sha256": inputs["followup_preflight"]["sha256"]})
    inputs["scene_roster"] = write("scenes.json", {"units": [{"id": "synthetic-story"}]})
    source = root / "original.bin"
    source.write_bytes(b"synthetic source identity")
    manifest = {"schema": role.SCHEMA, "inputs": inputs,
        "source_identity": {"path": source.name, "sha256": role.o2.sha256_file(source)},
        "geometry_sha256": role.o2.fingerprint_json(GEOMETRY),
        "bank_sha256": role.o2.fingerprint_json(pre["references"]),
        "policy": {"id": role.POLICY, "tau_support": None, "tie_epsilon": 1e-6},
        "partitions": {"calibration": [], "holdout": []},
        "resources": {"encoder_forwards": 0, "max_records": 1, "max_output_bytes": 20000},
        "scene_claims": {"p0_unit_ids": ["synthetic-story"]}, "blockers": []}
    return root, manifest


@pytest.mark.parametrize("change", ["threshold", "holdout", "geometry", "source", "candidate", "story"])
def test_preflight_rejects_unsafe_freeze_changes(tmp_path, change):
    root, manifest = fixture_manifest(tmp_path)
    if change == "threshold":
        manifest["policy"]["tau_support"] = 0.6
    elif change == "holdout":
        manifest["partitions"]["holdout"] = ["same old source renamed"]
    elif change == "geometry":
        manifest["geometry_sha256"] = "0" * 64
    elif change == "source":
        (root / "original.bin").write_bytes(b"different source")
    elif change == "candidate":
        (root / "capture.json").write_text("{}", encoding="utf-8")
    else:
        manifest["scene_claims"]["p0_unit_ids"] = []
    with pytest.raises(ValueError):
        role.audit(root, manifest)


def test_real_cli_from_foreign_cwd_keeps_uncalibrated_record_and_refuses_overwrite(tmp_path):
    root, manifest = fixture_manifest(tmp_path)
    entry = root / "manifest.json"
    entry.write_text(json.dumps(manifest), encoding="utf-8")
    output = tmp_path / "result.json"
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = [sys.executable, "-B", str(Path(role.__file__).resolve()), "--root", str(root),
               "--manifest", str(entry), "--output", str(output)]
    result = subprocess.run(command, cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, encoding="utf-8", check=True)
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["counts"]["candidates"] == 1
    assert report["rows"][0]["time_sec"] == 0.333
    assert report["rows"][0]["query"]["source_xy"] == [52, 40.0]
    assert report["rows"][0]["decision"] == "NOT_EVALUATED"
    assert report["gates"]["numeric_calibration"] == "NOT_READY"
    assert json.loads(result.stdout)["decision"] == "NOT_EVALUATED"
    original = output.read_bytes()
    retry = subprocess.run(command, cwd=tmp_path, env=env, stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, encoding="utf-8")
    assert retry.returncode != 0 and output.read_bytes() == original


@pytest.mark.parametrize("change", ["valid", "native_frame", "native_y", "duplicate_native", "candidate_y", "timestamp"])
def test_hash_valid_artifacts_still_require_exact_native_and_candidate_joins(tmp_path, change):
    root, manifest = fixture_manifest(tmp_path)
    cap_path = root / "capture.json"
    capture = role.o2.read_json(cap_path)
    native = {"candidate_input_index": 0, "source": "fixture", "canonical_y": 40.0,
              "measurement_status": "measured", "contour": {"native_path_reason": "native_generator_path"}}
    sidecar = {"source_frame_index": 10, "glass_id": "synthetic", "candidates": [native]}
    capture["state"]["oil_interface_witness"] = sidecar
    if change == "native_frame":
        sidecar["source_frame_index"] = 11
    elif change == "native_y":
        native["canonical_y"] = 41.0
    elif change == "duplicate_native":
        sidecar["candidates"].append(copy.deepcopy(native))
    elif change == "candidate_y":
        capture["current"]["candidates"][0]["y"] = 41.0
    elif change == "timestamp":
        capture["current"]["time_sec"] = 0.9
    cap_path.write_text(json.dumps(capture), encoding="utf-8")
    pre = role.o2.read_json(root / "pre.json")
    pre["original_capture_pins"]["capture.json"] = role.o2.sha256_file(cap_path)
    (root / "pre.json").write_text(json.dumps(pre), encoding="utf-8")
    manifest["inputs"]["cr1_preflight"]["sha256"] = role.o2.sha256_file(root / "pre.json")
    prepared = role.o2.read_json(root / "prepared.json")
    prepared["preflight_sha256"] = manifest["inputs"]["cr1_preflight"]["sha256"]
    (root / "prepared.json").write_text(json.dumps(prepared), encoding="utf-8")
    manifest["inputs"]["prepared"]["sha256"] = role.o2.sha256_file(root / "prepared.json")
    if change != "valid":
        with pytest.raises(ValueError):
            role.audit(root, manifest)
    else:
        row = role.audit(root, manifest)["rows"][0]
        assert row["native_support"]["oil_interface_witness"]["physical_role"] == "NOT_EVALUATED"
        assert row["native_support"]["oil_measurement_lineage"]["status"] == "UNAVAILABLE_NO_BOUND_RECORD"
