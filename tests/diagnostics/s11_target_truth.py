"""Immutable target-role binding of reviewed labels; no image or identity inference.

The existing evaluator owns packet validation and metrics. This companion owns a
separate snapshot because target membership must not rewrite physical review history.
"""
from __future__ import annotations

from collections import Counter
import copy
from pathlib import Path

from tests.diagnostics import s11_interface_shadow_evaluation as o2

SCHEMA = "s11-o2-target-truth-v1"
MAPPING_SCHEMA = "s11-o2-target-role-mapping-v1"
SPEC = "uppermost-actual-fluid-boundary-v1"
ROLES = {"target": "interface", "internal_interface": "non_interface",
         "other_non_target": "non_interface", "uncertain": "uncertain", "unreviewed": "unreviewed"}
SOURCE_IDENTITIES = {"target": {"interface"}, "internal_interface": {"interface"},
                     "other_non_target": {"non_interface"}, "uncertain": {"interface", "uncertain"},
                     "unreviewed": {"unreviewed"}}


def _keys(value, expected, name):
    o2.require(isinstance(value, dict) and set(value) == set(expected.split()), f"{name}: unexpected fields")


def project(physical, packets, mapping):
    """Bind explicit groups exhaustively; never use Y, score, or nearest geometry."""
    _keys(mapping, "schema_version target_spec_id source_labels_sha256 attribution cases", "mapping")
    o2.require(mapping["schema_version"] == MAPPING_SCHEMA and mapping["target_spec_id"] == SPEC,
               "unsupported target mapping")
    o2.text(mapping["attribution"], "mapping attribution")
    o2.require(physical["schema_version"] == o2.LABEL_SCHEMA, "target binding requires v2 physical labels")
    # Source logical label hash includes its original packet locators, as status does.
    o2.require(o2.fingerprint_json(physical) == mapping["source_labels_sha256"], "source labels hash mismatch")
    o2.validate_labels(physical, packets)
    requested = o2.unique(mapping["cases"], "case_id", "target cases")
    o2.require(set(requested) == {c["case_id"] for c in physical["cases"]}, "target case inventory mismatch")
    projected = {k: copy.deepcopy(physical[k]) for k in
                 ("schema_version", "dataset_id", "label_owner", "split_owner", "split_rationale")}
    projected["target_binding"] = {"target_spec_id": SPEC, "source_labels_sha256": mapping["source_labels_sha256"],
                                   "mapping_sha256": o2.fingerprint_json(mapping)}
    projected["cases"] = []
    bindings = []
    for case in physical["cases"]:
        request = requested[case["case_id"]]
        _keys(request, "case_id frame_index glass_id candidate_count target_visibility note groups", "target case")
        o2.text(request["note"], "target case note")
        o2.integer(request["frame_index"], "frame_index")
        o2.integer(request["candidate_count"], "candidate_count")
        frame = packets[case["packet_sha256"]][case["case_id"]]
        o2.require(request["frame_index"] == frame["frame_index"] and request["glass_id"] == frame["glass_id"],
                   "target frame/Glass mismatch")
        o2.require(request["candidate_count"] == len(case["candidates"]), "target candidate count mismatch")
        o2.require(request["target_visibility"] in ("visible", "not_visible", "uncertain"), "invalid target visibility")
        annotations = {a["candidate_input_index"]: a for a in case["candidates"]}
        assigned = {}
        for group in request["groups"]:
            o2.require(isinstance(group, dict), "target group must be an object")
            selector = "candidate_indices" if "candidate_indices" in group else "source_identity"
            _keys(group, f"role {selector} expected_count review_basis note", "target group")
            role = group["role"]
            o2.require(role in ROLES, "invalid target role")
            for key in ("review_basis", "note"):
                o2.text(group[key], key)
            o2.integer(group["expected_count"], "expected_count")
            if selector == "source_identity":
                o2.require(group[selector] == "non_interface" and role == "other_non_target",
                           "only explicitly authorized source non_interface groups may be inherited")
                indices = [i for i, a in annotations.items() if o2.identity(a) == "non_interface"]
            else:
                indices = group[selector]
                o2.require(isinstance(indices, list), "candidate_indices must be a list")
            o2.require(len(indices) == group["expected_count"], "target group count mismatch")
            for i in indices:
                o2.integer(i, "candidate_input_index")
                o2.require(i in annotations and i not in assigned, "unknown or duplicate target candidate")
                a = annotations[i]
                o2.require(o2.identity(a) in SOURCE_IDENTITIES[role], "target role conflicts with physical identity")
                assigned[i] = group
        o2.require(set(assigned) == set(annotations), "target candidate inventory incomplete")
        # Do not silently reuse material-relative path/contour/entity truth for a new target.
        target_case = {k: copy.deepcopy(case[k]) for k in
                       ("case_id", "packet_sha256", "recording_group", "episode_id", "physical_case_id",
                        "transform_id", "partition", "previously_reviewed", "label_basis", "reviewer")}
        target_case.update(visibility=request["target_visibility"], contour=[], candidates=[], review_note=request["note"])
        for i, a in annotations.items():
            group = assigned[i]
            target_case["candidates"].append({"candidate_input_index": i, "witness_sha256": a["witness_sha256"],
                "identity": ROLES[group["role"]], "entity_id": None, "path_reviews": [],
                "artifact_tags": [], "artifact_note": ""})
            bindings.append({"case_id": case["case_id"], "candidate_input_index": i,
                "packet_sha256": case["packet_sha256"], "witness_sha256": a["witness_sha256"],
                "record_id": frame["record_id"], "run_id": frame["run_id"], "glass_id": frame["glass_id"],
                "frame_index": frame["frame_index"], "physical_identity": o2.identity(a),
                "physical_annotation_sha256": o2.fingerprint_json(a), "target_role": group["role"],
                "review_basis": group["review_basis"], "note": group["note"]})
        projected["cases"].append(target_case)
    o2.validate_labels({**projected, "packets": physical["packets"]}, packets)
    return projected, bindings


def bind(labels_path, mapping_path, output):
    labels_path, mapping_path, output = map(Path, (labels_path, mapping_path, output))
    o2.require(not output.exists(), "target output already exists")
    labels_before, mapping_before = o2.sha256_file(labels_path), o2.sha256_file(mapping_path)
    physical, mapping = o2.read_json(labels_path), o2.read_json(mapping_path)
    packet_paths = [(labels_path.parent / p["path"]).resolve() for p in physical["packets"]]
    inputs = [labels_path, mapping_path, *packet_paths]
    before = [labels_before, mapping_before, *(o2.sha256_file(p) for p in packet_paths)]
    packets = o2.load_packets(physical, labels_path.parent)
    content, bindings = project(physical, packets, mapping)
    o2.require(before == [o2.sha256_file(p) for p in inputs], "source changed during target binding")
    payload = {"target_spec_id": SPEC, "physical_labels": physical, "mapping": mapping,
               "evaluation_content": content, "bindings": bindings,
               "source_labels_file_sha256": labels_before, "source_mapping_file_sha256": mapping_before,
               "source_packet_file_sha256s": dict(zip((p["sha256"] for p in physical["packets"]), before[2:]))}
    snapshot = {"schema_version": SCHEMA, "payload": payload, "artifact_sha256": o2.fingerprint_json(payload),
                "content_sha256": o2.fingerprint_json(content),
                "packets": [{"sha256": p["sha256"], "path": o2.relative_path(path, output.parent)}
                            for p, path in zip(physical["packets"], packet_paths)]}
    o2.write_new(output, snapshot)
    return {"status": "BOUND_NOT_EVALUATED", "target_spec_id": SPEC,
            "artifact_sha256": snapshot["artifact_sha256"], "evaluation_truth_sha256": snapshot["content_sha256"],
            "target_role_counts": dict(Counter(r["target_role"] for r in bindings)),
            "preserved_input_count": len(inputs), "field_disposition": "FIELD FAIL", "auto_acceptance": False}


def load(path, snapshot):
    _keys(snapshot, "schema_version payload artifact_sha256 content_sha256 packets", "target snapshot")
    o2.require(snapshot["schema_version"] == SCHEMA, "unsupported target truth schema")
    payload = snapshot["payload"]
    o2.require(o2.fingerprint_json(payload) == snapshot["artifact_sha256"], "target artifact hash mismatch")
    o2.require(payload["target_spec_id"] == SPEC, "unsupported target specification")
    packets = o2.load_packets(snapshot, Path(path).parent)
    o2.require({p["sha256"] for p in snapshot["packets"]} ==
               {p["sha256"] for p in payload["physical_labels"]["packets"]}, "target packet inventory mismatch")
    content, bindings = project(payload["physical_labels"], packets, payload["mapping"])
    o2.require(content == payload["evaluation_content"] and bindings == payload["bindings"], "target projection mismatch")
    o2.require(o2.fingerprint_json(content) == snapshot["content_sha256"], "target content hash mismatch")
    # In-memory v2 projection only; persisted artifact cannot be mistaken for original labels.
    frozen = {"schema_version": o2.FREEZE_SCHEMA, "content": content, "content_sha256": snapshot["content_sha256"],
              "packets": snapshot["packets"], "target_truth": {"schema_version": SCHEMA, "target_spec_id": SPEC,
              "artifact_sha256": snapshot["artifact_sha256"], "source_labels_sha256": payload["mapping"]["source_labels_sha256"],
              "physical_identity_counts": dict(Counter(r["physical_identity"] for r in bindings)),
              "target_role_counts": dict(Counter(r["target_role"] for r in bindings)),
              "local_scalar_entity_truth": "NOT_TRANSFERRED"}}
    return frozen, packets
