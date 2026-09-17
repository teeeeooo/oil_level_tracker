"""O2 offline label/partition and shadow-evaluation tooling. Never runs a detector.

Packets and labels stay on the work PC. Existing indexed trace readers own input
loading; no nearest-frame substitution or physical labels inferred from scores.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import json
import math
import os
from pathlib import Path
import sys

# Direct invocation must work outside the repository working directory.
ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from oil_tracker.application.services.truth_identity import sha256_file
from oil_tracker.domain.detector_benchmark import fingerprint_json, deterministic_percentile

PACKET_SCHEMA = "s11-o2-review-packet-v1"
LABEL_SCHEMA = "s11-o2-labels-v1"
FREEZE_SCHEMA = "s11-o2-frozen-labels-v1"
PREDICTION_SCHEMA = "s11-o2-shadow-predictions-v1"
WITNESS_SCHEMA = "interface-observability-witness-trace-v1"
PARTITIONS = ("development", "calibration", "holdout", "regression")
LABELS = ("interface", "localization_mismatch", "reflection", "residue", "structure", "unresolved", "unobservable", "unreviewed")
DECISIONS = ("INTERFACE_SUPPORTED", "INTERNAL_OR_ARTIFACT", "UNRESOLVED", "UNOBSERVABLE", "NOT_EVALUATED")
NEGATIVES = {"reflection", "residue", "structure"}
POSITIVES = {"interface", "localization_mismatch"}
MAX_CASES = 256


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), f"{name}: nonempty string required")
    return value


def integer(value, name):
    require(type(value) is int and value >= 0, f"{name}: nonnegative integer required")
    return value


def number(value, name):
    require(type(value) in (int, float) and math.isfinite(value), f"{name}: finite number required")
    return value


def interval(value, name, *, strict=False):
    require(isinstance(value, list) and len(value) == 2, f"{name}: pair required")
    a, b = (number(v, name) for v in value)
    require(a < b if strict else a <= b, f"{name}: invalid interval")
    return a, b


def unique(rows, key, name):
    result = {}
    for row in rows:
        value = row[key]
        require(value not in result, f"{name}: duplicate {value}")
        result[value] = row
    return result


def read_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, f"duplicate JSON key: {key}")
            out[key] = value
        return out
    def invalid(value):
        raise ValueError(f"nonfinite JSON: {value}")
    require(Path(path).stat().st_size <= 128 * 1024**2, "JSON exceeds 128 MiB; split review packet")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=pairs, parse_constant=invalid)


def write_new(path, payload):
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(encoded)


def extract_frame(record, case_id):
    """Preserve every Oil witness, including rejected/unadmitted candidates."""
    w = record.state.get("oil_interface_witness")
    require(isinstance(w, dict) and w.get("schema_version") == WITNESS_SCHEMA, "R22-3 witness required; do not substitute an older trace")
    require(w.get("source_frame_index") == record.frame_index and w.get("glass_id") == record.glass_id, "witness frame/Glass mismatch")
    require(w.get("coordinate_space") == "source_frame_y" and w.get("positive_direction") == "down", "unsupported witness coordinates")
    require(w.get("candidate_index_space") == "detection.candidates_before_trace_score_sort", "unsupported candidate index space")
    original = unique(record.candidates, "candidate_input_index", "raw candidates")
    candidates = unique(w["candidates"], "candidate_input_index", "witness candidates")
    oil_ids = {i for i, c in original.items() if c["kind"] == "oil_air"}
    require(set(candidates) == oil_ids, "Oil candidate inventory mismatch")
    for i, c in candidates.items():
        raw = original[i]
        require(all(c[k] == raw[k] for k in ("source", "kind", "canonical_y", "local_y", "rejected")), "candidate provenance mismatch")
    return {"case_id": case_id, "record_id": record.record_id, "run_id": record.run_id,
            "glass_id": record.glass_id, "frame_index": record.frame_index,
            "timestamp_sec": record.timestamp_sec, "witness": copy.deepcopy(w)}


def prepare(bundle_path, selection, output):
    from oil_tracker.adapters.storage.result_bundle_reader import ResultBundleReader
    from oil_tracker.adapters.storage.debug_trace_repository import DebugTraceRepository

    require(0 < len(selection["cases"]) <= 64, "select 1–64 exact records per packet")
    require(not Path(output).exists(), "output directory already exists")
    bundle = ResultBundleReader().read(bundle_path)
    repository = DebugTraceRepository(bundle, record_cache_size=1)
    frames, labels, seen = [], [], set()
    try:
        for case in selection["cases"]:
            key = text(case["case_id"], "case_id")
            require(key not in seen, "duplicate case_id")
            seen.add(key)
            fi = integer(case["frame_index"], "frame_index")
            matches = [s for s in repository.summaries(case["glass_id"]) if s.frame_index == fi]
            require(len(matches) == 1, f"{key}: expected one exact Glass/frame record, got {len(matches)}")
            frame = extract_frame(repository.load_record(matches[0].record_id), key)
            frames.append(frame)
            labels.append({**{k: case[k] for k in ("case_id", "recording_group", "episode_id", "physical_case_id", "transform_id", "partition", "previously_reviewed")},
                "visibility": "pending", "label_basis": "human_review", "reviewer": "", "review_note": "", "contour": [],
                "candidates": [{"candidate_input_index": c["candidate_input_index"],
                    "witness_sha256": fingerprint_json(c), "label": "unreviewed", "entity_id": None}
                    for c in frame["witness"]["candidates"]]})
    finally:
        repository.close()
    packet = {"schema_version": PACKET_SCHEMA, "manifest_sha256": sha256_file(bundle.files["manifest"]),
              "recipe_sha256": sha256_file(bundle.files["recipe_snapshot"]),
              "manifest": {k: v for k, v in bundle.manifest.items() if "version" in k or k in ("detector", "sequence_resolver")},
              "frames": frames}
    packet_hash = fingerprint_json(packet)
    for c in labels:
        c["packet_sha256"] = packet_hash
    draft = {"schema_version": LABEL_SCHEMA, "dataset_id": selection["dataset_id"],
             "label_owner": "", "split_owner": "", "split_rationale": "",
             "packets": [{"path": "packet.json", "sha256": packet_hash}], "cases": labels}
    write_new(Path(output) / "packet.json", packet)
    write_new(Path(output) / "labels.json", draft)
    return draft


def load_packets(document, directory):
    packets = {}
    for reference in document["packets"]:
        path = Path(directory) / reference["path"]
        packet = read_json(path)
        require(packet.get("schema_version") == PACKET_SCHEMA, "unsupported packet schema")
        digest = fingerprint_json(packet)
        require(digest == reference["sha256"], "packet hash mismatch")
        require(digest not in packets, "duplicate packet")
        packets[digest] = unique(packet["frames"], "case_id", "packet cases")
    return packets


def validate_labels(labels, packets):
    require(labels.get("schema_version") == LABEL_SCHEMA, "unsupported label schema")
    for k in ("dataset_id", "label_owner", "split_owner", "split_rationale"):
        text(labels[k], k)
    cases = labels["cases"]
    require(0 < len(cases) <= MAX_CASES, "dataset requires 1–256 cases")
    unique(cases, "case_id", "label cases")
    groups, physical, runs, records, used = {}, {}, {}, set(), set()
    for case in cases:
        for k in ("case_id", "recording_group", "episode_id", "physical_case_id", "transform_id", "reviewer", "review_note"):
            text(case[k], k)
        partition = case["partition"]
        require(partition in PARTITIONS, "invalid partition")
        require(type(case["previously_reviewed"]) is bool, "previously_reviewed must be boolean")
        require(not case["previously_reviewed"] or partition == "regression", "reviewed cases must stay in regression")
        # Conservative recording-level lock is stricter than episode-only splitting.
        group = case["recording_group"]
        require(groups.setdefault(group, partition) == partition, "recording/episode leakage across partitions")
        pair = (group, case["physical_case_id"])
        require(physical.setdefault(pair, (case["episode_id"], partition)) == (case["episode_id"], partition), "physical-case leakage")
        require(case["visibility"] in ("visible", "not_visible", "uncertain"), "human visibility review required")
        require(case["label_basis"] in ("human_review", "synthetic_construction"), "invalid label basis")
        frame = packets[case["packet_sha256"]][case["case_id"]]
        require(runs.setdefault(frame["run_id"], group) == group, "one bundle run cannot be renamed into multiple recording groups")
        used.add((case["packet_sha256"], case["case_id"]))
        record = (frame["run_id"], frame["glass_id"], frame["frame_index"])
        require(record not in records, "duplicate physical trace record")
        records.add(record)
        witness = frame["witness"]
        require(witness["schema_version"] == WITNESS_SCHEMA, "unsupported witness schema")
        require(witness["source_frame_index"] == frame["frame_index"] and witness["glass_id"] == frame["glass_id"], "packet frame provenance mismatch")
        refs = unique(witness["candidates"], "candidate_input_index", "witness candidates")
        annotated = unique(case["candidates"], "candidate_input_index", "candidate labels")
        require(set(refs) == set(annotated), "label inventory must include all candidates")
        for i, annotation in annotated.items():
            integer(i, "candidate_input_index")
            require(annotation["witness_sha256"] == fingerprint_json(refs[i]), "candidate hash mismatch")
            require(annotation["label"] in LABELS, "invalid physical label")
            require(annotation["label"] not in POSITIVES or case["visibility"] == "visible", "interface labels require a visible frame")
            require(annotation["entity_id"] is None or isinstance(annotation["entity_id"], str) and bool(annotation["entity_id"].strip()), "invalid entity_id")
        xs = set()
        for point in case["contour"]:
            x = interval(point["source_x_range"], "contour X", strict=True)
            require(x not in xs, "duplicate contour X extent")
            xs.add(x)
            interval(point["source_y_interval"], "reviewed contour Y")
        require(case["visibility"] != "not_visible" or not case["contour"], "not-visible frame cannot carry a reviewed contour")
    require(used == {(h, key) for h, frames in packets.items() for key in frames}, "packet frames cannot silently disappear from labels")
    fingerprint_json(labels)  # Strict finite JSON, including user metadata.


def freeze(labels_path, output):
    labels_path, output = Path(labels_path), Path(output)
    labels = read_json(labels_path)
    packets = load_packets(labels, labels_path.parent)
    validate_labels(labels, packets)
    # Paths are transport metadata, excluded from the immutable logical label hash.
    content = {k: v for k, v in labels.items() if k != "packets"}
    frozen = {"schema_version": FREEZE_SCHEMA, "content": content,
              "content_sha256": fingerprint_json(content),
              "packets": [{"sha256": p["sha256"], "path": Path(os.path.relpath((labels_path.parent / p["path"]).resolve(), output.parent.resolve())).as_posix()}
                          for p in labels["packets"]]}
    write_new(output, frozen)
    return frozen


def combine(paths, dataset_id, output):
    """Assemble locally reviewed packets without inventing or changing splits."""
    merged = {"schema_version": LABEL_SCHEMA, "dataset_id": text(dataset_id, "dataset_id"),
              "packets": [], "cases": []}
    owners = {k: set() for k in ("label_owner", "split_owner", "split_rationale")}
    seen = set()
    for path in map(Path, paths):
        draft = read_json(path)
        require(draft.get("schema_version") == LABEL_SCHEMA, "unsupported label schema")
        load_packets(draft, path.parent)
        for k in owners:
            if draft[k]:
                owners[k].add(draft[k])
        for p in draft["packets"]:
            if p["sha256"] not in seen:
                seen.add(p["sha256"])
                merged["packets"].append({"sha256": p["sha256"], "path": Path(os.path.relpath((path.parent / p["path"]).resolve(), Path(output).parent.resolve())).as_posix()})
        merged["cases"].extend(draft["cases"])
    unique(merged["cases"], "case_id", "combined cases")
    require(len(merged["cases"]) <= MAX_CASES, "combined dataset exceeds case bound")
    for k, values in owners.items():
        require(len(values) <= 1, f"conflicting {k}; resolve explicitly before combining")
        merged[k] = next(iter(values), "")
    write_new(output, merged)
    return merged


def load_frozen(path):
    frozen = read_json(path)
    require(frozen.get("schema_version") == FREEZE_SCHEMA, "unsupported freeze schema")
    require(fingerprint_json(frozen["content"]) == frozen["content_sha256"], "frozen label hash mismatch")
    packets = load_packets(frozen, Path(path).parent)
    validate_labels({**frozen["content"], "packets": frozen["packets"]}, packets)
    return frozen, packets


def ratio(n, d):
    return n / d if d else None


def summarize(cases, packets, predictions):
    confusion = {label: Counter() for label in LABELS}
    visibility = defaultdict(Counter)
    availability = defaultdict(Counter)
    missing = supported = tp = fp = unverified = visible_frames = recalled = proposals = 0
    localization_errors, widths, covered = [], [], []
    localization_rows = []
    localization_missing = 0
    consistency = defaultdict(list)
    for case in cases:
        frame = packets[case["packet_sha256"]][case["case_id"]]
        candidates = {c["candidate_input_index"]: c for c in frame["witness"]["candidates"]}
        frame_recalled = False
        if case["visibility"] == "visible":
            visible_frames += 1
            proposals += any(a["label"] in POSITIVES for a in case["candidates"])
        truth = {tuple(p["source_x_range"]): p["source_y_interval"] for p in case["contour"]}
        for annotation in case["candidates"]:
            key = (case["case_id"], annotation["candidate_input_index"])
            p = predictions.get(key)
            decision = p["decision"] if p else "NOT_EVALUATED"
            missing += p is None
            label = annotation["label"]
            confusion[label][decision] += 1
            visibility[case["visibility"]][decision] += 1
            if decision == "INTERFACE_SUPPORTED":
                supported += 1
                tp += label in POSITIVES
                fp += label in NEGATIVES
                unverified += label not in POSITIVES | NEGATIVES
                frame_recalled |= label == "interface"
            if annotation["entity_id"]:
                consistency[(case["recording_group"], case["physical_case_id"], annotation["entity_id"])].append((case["case_id"], decision))
            candidate = candidates[annotation["candidate_input_index"]]
            availability[candidate["measurement_status"]][decision] += 1
            intervals = {tuple(q["source_x_range"]): q["source_y_interval"] for q in p.get("intervals", [])} if p else {}
            if label in POSITIVES:
                matched = 0
                for sector in candidate["sectors"]:
                    x = tuple(sector["source_x_range"])
                    if x not in truth:
                        continue
                    matched += 1
                    lo, hi = truth[x]
                    y = sector["path_source_y"] if sector["path_source_y"] is not None else candidate["canonical_y"]
                    error = max(lo - y, 0, y - hi)
                    localization_errors.append(error)
                    bounds = intervals.get(x)
                    localization_rows.append({"case_id": case["case_id"],
                        "candidate_input_index": annotation["candidate_input_index"],
                        "source_x_range": list(x), "candidate_path_source_y": y,
                        "reviewed_source_y_interval": [lo, hi], "distance_px": error,
                        "reported_source_y_interval": bounds,
                        "interval_covers_review": bounds[0] <= lo and bounds[1] >= hi if bounds else None})
                    if x in intervals:
                        a, b = intervals[x]
                        widths.append(b - a)
                        covered.append(a <= lo and b >= hi)
                localization_missing += matched == 0
        recalled += case["visibility"] == "visible" and frame_recalled
    pairs = [values for values in consistency.values() if len({v[0] for v in values}) > 1]
    evaluated_pairs = [v for v in pairs if all(d != "NOT_EVALUATED" for _, d in v)]
    positive_count = sum(sum(confusion[label].values()) for label in POSITIVES)
    count = sum(sum(c.values()) for c in confusion.values())
    abstained = sum(c[d] for c in confusion.values() for d in ("UNRESOLVED", "UNOBSERVABLE"))
    negative_counts = {label: {"total": sum(confusion[label].values()), "rejected": confusion[label]["INTERNAL_OR_ARTIFACT"], "wrong_support": confusion[label]["INTERFACE_SUPPORTED"]} for label in sorted(NEGATIVES)}
    for values in negative_counts.values():
        values["rejection_rate"] = ratio(values["rejected"], values["total"])
    return {"frame_count": len(cases), "candidate_count": count,
            "frames_by_label_basis": dict(Counter(c["label_basis"] for c in cases)),
            "unreviewed_candidate_count": sum(confusion["unreviewed"].values()),
            "abstention_count": abstained, "abstention_rate": ratio(abstained, count),
            "missing_prediction_count": missing, "confusion": {l: dict(c) for l, c in confusion.items()},
            "by_human_visibility": {l: dict(c) for l, c in visibility.items()},
            "by_measurement_status": {l: dict(c) for l, c in availability.items()},
            "supported_count": supported, "wrong_structure_support_count": fp, "unverified_support_count": unverified,
            "verified_identity_precision": ratio(tp, tp + fp), "conservative_supported_precision": ratio(tp, supported),
            "identity_recall": ratio(tp, positive_count), "negative_families": negative_counts,
            "visible_frame_count": visible_frames, "visible_frames_with_interface_proposal": proposals,
            "visible_frames_with_localized_support": recalled, "visible_frame_support_recall": ratio(recalled, visible_frames),
            "localization": {"matched_sector_count": len(localization_errors), "unmatched_positive_candidates": localization_missing,
                "sector_results": localization_rows,
                "mean_distance_to_review_interval_px": ratio(sum(localization_errors), len(localization_errors)),
                "p95_distance_px": deterministic_percentile(localization_errors, .95),
                "reported_interval_count": len(covered), "full_review_interval_coverage": ratio(sum(covered), len(covered)),
                "mean_reported_interval_width_px": ratio(sum(widths), len(widths))},
            "paired_entity_groups": len(pairs), "fully_evaluated_pair_groups": len(evaluated_pairs),
            "paired_decision_consistency": ratio(sum(len({d for _, d in v}) == 1 for v in evaluated_pairs), len(evaluated_pairs)),
            "independent_evidence_vote_audit": "NOT_EVALUATED: prediction interface cannot certify internal classifier weighting"}


def evaluate(frozen, packets, prediction_document=None):
    predictions = {}
    known = {(c["case_id"], a["candidate_input_index"]): (c, a) for c in frozen["content"]["cases"] for a in c["candidates"]}
    if prediction_document is not None:
        p = prediction_document
        require(p.get("schema_version") == PREDICTION_SCHEMA, "unsupported prediction schema")
        require(p["frozen_labels_sha256"] == frozen["content_sha256"], "predictions target different labels")
        for k in ("classifier_id", "artifact_sha256", "operating_point_description"):
            text(p[k], k)
        require(len(p["artifact_sha256"]) == 64 and all(c in "0123456789abcdef" for c in p["artifact_sha256"]), "classifier artifact SHA-256 required")
        require(p["fit_partitions"] and set(p["fit_partitions"]) <= {"development", "calibration"}, "holdout/regression cannot select an operating point")
        for row in p["predictions"]:
            key = (row["case_id"], integer(row["candidate_input_index"], "candidate_input_index"))
            require(key in known and key not in predictions, "unknown or duplicate prediction key")
            case, annotation = known[key]
            require(row["witness_sha256"] == annotation["witness_sha256"], "prediction witness hash mismatch")
            require(row["decision"] in DECISIONS, "invalid shadow decision")
            text(row["reason"], "prediction reason")
            candidate = next(c for c in packets[case["packet_sha256"]][case["case_id"]]["witness"]["candidates"] if c["candidate_input_index"] == key[1])
            extents = {tuple(s["source_x_range"]) for s in candidate["sectors"]}
            seen = set()
            for q in row.get("intervals", []):
                x = interval(q["source_x_range"], "prediction X", strict=True)
                require(x in extents and x not in seen, "prediction interval needs one exact witness X extent")
                seen.add(x)
                interval(q["source_y_interval"], "prediction interval")
            predictions[key] = row
        fingerprint_json(p)
    cases = frozen["content"]["cases"]
    return {"schema_version": "s11-o2-shadow-report-v1", "frozen_labels_sha256": frozen["content_sha256"],
            "prediction_sha256": fingerprint_json(prediction_document) if prediction_document else None,
            "status": "EVALUATED_NOT_QUALIFIED" if predictions else "NOT_EVALUATED",
            "field_disposition": "FIELD FAIL", "auto_acceptance": False,
            "partitions": {s: summarize([c for c in cases if c["partition"] == s], packets, predictions) for s in PARTITIONS},
            "limitations": ["Human labels and recording-group independence are attestations, not machine-certified physical truth.",
                "No classifier, operating point or production authority is supplied by this evaluator.",
                "Unreviewed/unresolved support is reported separately; visible frames with no candidates remain misses.",
                "Localization compares exact X extents only; no scalar-to-curve or interpolated truth substitution.",
                "A content hash detects drift but cannot prove an untouched holdout or annotation chronology."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--bundle", type=Path, required=True)
    prepare_parser.add_argument("--selection", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    freeze_parser = commands.add_parser("freeze")
    freeze_parser.add_argument("--labels", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    combine_parser = commands.add_parser("combine")
    combine_parser.add_argument("--labels", type=Path, nargs="+", required=True)
    combine_parser.add_argument("--dataset-id", required=True)
    combine_parser.add_argument("--output", type=Path, required=True)
    audit_parser = commands.add_parser("evaluate")
    audit_parser.add_argument("--frozen", type=Path, required=True)
    audit_parser.add_argument("--predictions", type=Path)
    audit_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.bundle, read_json(args.selection), args.output)
        elif args.command == "freeze":
            freeze(args.labels, args.output)
        elif args.command == "combine":
            combine(args.labels, args.dataset_id, args.output)
        else:
            frozen, packets = load_frozen(args.frozen)
            predictions = read_json(args.predictions) if args.predictions else None
            write_new(args.output, evaluate(frozen, packets, predictions))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f"O2 input rejected: {exc}\n")
    print(f"{args.command} complete; no detector behavior changed")


if __name__ == "__main__":
    main()
