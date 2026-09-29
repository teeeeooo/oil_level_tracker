"""Fixed, label-blind O2 ranking experiment. No detector or calibrated decisions.

Private packets/labels remain local. This is intentionally not the calibrated
shadow-predictions schema: regression truth evaluates scores, never fits them.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import inspect
import math
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from tests.diagnostics import s11_interface_shadow_evaluation as o2

SCHEMA = "s11-o2-score-experiment-v1"
METHODS = ("contrast_only", "alignment_only", "combined")
SPEC = {
    "id": "two-sided-localized-edge-ranking-v1",
    "contrast": "abs(normalized_delta)/(1+abs(normalized_delta))",
    "alignment": "mean(near_above.normal_alignment,near_below.normal_alignment)",
    "locality": "abs(signed_delta)/(abs(signed_delta)+abs(far_below.gray_mean-far_above.gray_mean)+1/255)",
    "combined": "(contrast*alignment*locality)**(1/3)",
    "aggregation": "median of available scales, then median of available preferred-geometry points",
    "ablation_comparison": "identical all-method-available scales and points; raw per-method scores retained",
    "preferred_geometry": "native_path if present; otherwise candidate_center; no missing-score fallback",
    "fit_partitions": [], "fitted": False, "threshold": None,
    "meaning": "uncalibrated evidence scores, not probabilities or identity/location decisions",
    "lineage": "correlated current-frame RGB features, not independent votes",
}


def median(values):
    return o2.deterministic_percentile([v for v in values if v is not None], 0.5)


def value(row, key, *, bounded=False):
    """Return value plus explicit missing/null/invalid status; bool is not numeric."""
    if key not in row:
        return None, "missing"
    v = row[key]
    if v is None:
        return None, "null"
    if type(v) not in (int, float) or not math.isfinite(v) or (bounded and not 0 <= v <= 1):
        raise ValueError(f"invalid measurement: {key}")
    return v, "present"


def scale_scores(scale):
    bands = o2.unique(scale.get("bands", []), "name", "scale bands")
    statuses, measurements = {}, {}

    def read(row, key, prefix, bounded=False):
        v, state = value(row, key, bounded=bounded)
        statuses[f"{prefix}{key}"] = state
        measurements[f"{prefix}{key}"] = v
        return v

    def band(name, key):
        b = bands.get(name, {})
        v = read(b, key, name + ".", bounded=True)
        a = b.get("available")
        statuses[name + ".available"] = "missing" if "available" not in b else "null" if a is None else "present"
        measurements[name + ".available"] = a
        o2.require(a is None or type(a) is bool, "band availability must be boolean or null")
        return v if a is True else None

    delta = read(scale, "signed_delta", "")
    norm = read(scale, "normalized_delta", "")
    above = band("near_above", "normal_alignment")
    below = band("near_below", "normal_alignment")
    far_above = band("far_above", "gray_mean")
    far_below = band("far_below", "gray_mean")
    near_available = all(bands.get(n, {}).get("available") is True for n in ("near_above", "near_below"))
    contrast = abs(norm) / (1 + abs(norm)) if norm is not None and near_available else None
    alignment = (above + below) / 2 if above is not None and below is not None else None
    locality = (abs(delta) / (abs(delta) + abs(far_below - far_above) + 1 / 255)
                if delta is not None and near_available and far_above is not None and far_below is not None else None)
    combined = (contrast * alignment * locality) ** (1 / 3) if all(v is not None for v in (contrast, alignment, locality)) else None
    return {"band_width_px": scale["band_width_px"], "field_status": statuses, "measurements": measurements,
            "locality": locality,
            "scores": dict(zip(METHODS, (contrast, alignment, combined)))}


def score_candidate(candidate):
    """No label, source family, Glass, frame, rank, rejection or Y as a feature."""
    o2.require(len(candidate["sectors"]) <= 16, "experiment supports at most 16 sectors per candidate")
    points = []
    # Validate center identities before matching against existing review geometry.
    sectors = {}
    for sector in candidate["sectors"]:
        x = tuple(sector["source_x_range"])
        o2.require(x not in sectors, "duplicate sector X range")
        sectors[x] = sector
        o2.unique(sector.get("centers", []), "role", "sector centers")
    for geometry in o2.review_geometry(candidate):
        sector = sectors[tuple(geometry["source_x_range"])]
        centers = {c["role"]: c for c in sector.get("centers", [])}
        center = centers.get(geometry["geometry_basis"])
        alias = False
        # O1 omits a duplicate center when candidate and native coordinates equal.
        if center is None and geometry["geometry_basis"] == "candidate_center":
            native = centers.get("native_path")
            if native and native["source_y"] == geometry["source_y"]:
                center, alias = native, True
        scales = []
        if center is not None:
            o2.require(center["source_y"] == geometry["source_y"], "center/geometry Y mismatch")
            o2.require(len(center["scales"]) <= 8, "experiment supports at most 8 scales")
            widths = [s["band_width_px"] for s in center["scales"]]
            o2.require(all(type(w) is int and w > 0 for w in widths) and len(set(widths)) == len(widths), "invalid/duplicate scale widths")
            scales = [scale_scores(s) for s in sorted(center["scales"], key=lambda s: s["band_width_px"])]
        scores = {m: median([s["scores"][m] for s in scales]) for m in METHODS}
        common = [s for s in scales if all(s["scores"][m] is not None for m in METHODS)]
        points.append({**geometry, "measurement_role": center["role"] if center else None,
                       "exact_center_alias": alias, "normal_mode": sector.get("normal_mode"), "scales": scales, "scores": scores,
                       "matched_scores": {m: median([s["scores"][m] for s in common]) for m in METHODS},
                       "common_scale_count": len(common),
                       "available_scale_count": {m: sum(s["scores"][m] is not None for s in scales) for m in METHODS},
                       "scale_count": len(scales)})
    basis = "native_path" if any(p["geometry_basis"] == "native_path" for p in points) else "candidate_center"
    preferred = [p for p in points if p["geometry_basis"] == basis]
    return {"candidate_input_index": candidate["candidate_input_index"],
            "witness_sha256": o2.fingerprint_json(candidate), "identity_geometry_basis": basis,
            "scores": {m: median([p["scores"][m] for p in preferred]) for m in METHODS},
            "matched_scores": {m: median([p["matched_scores"][m] for p in preferred]) for m in METHODS},
            "common_point_count": sum(p["common_scale_count"] > 0 for p in preferred),
            "available_point_count": {m: sum(p["scores"][m] is not None for p in preferred) for m in METHODS},
            "point_count": len(preferred), "points": points}


def order(a, b):
    if a is None or b is None:
        return "unscorable"
    return "tie" if math.isclose(a, b, abs_tol=1e-12, rel_tol=0) else "correct" if a > b else "reversed"


def pair_results(positives, negatives, *, same_x=False):
    """Within-case only; pairing counts are correlated diagnostics, not iid trials."""
    o2.require(len(positives) * len(negatives) <= 10000, "too many comparison pairs; use a smaller review set")
    rows = []
    for a in positives:
        for b in negatives:
            if same_x and a["source_x_range"] != b["source_x_range"]:
                continue
            rows.append({"positive": a["key"], "negative": b["key"],
                         "outcomes": {m: order(a["scores"][m], b["scores"][m]) for m in METHODS}})
    common = [r for r in rows if all(v != "unscorable" for v in r["outcomes"].values())]
    counts = {m: dict(Counter(r["outcomes"][m] for r in rows)) for m in METHODS}
    changes = {}
    for base in METHODS[:2]:
        improved = [r for r in common if r["outcomes"][base] != "correct" and r["outcomes"]["combined"] == "correct"]
        regressed = [r for r in common if r["outcomes"][base] == "correct" and r["outcomes"]["combined"] != "correct"]
        changes[base] = {"improved": len(improved), "regressed": len(regressed)}
    return {"pair_count": len(rows), "common_scorable_pair_count": len(common),
            "counts": counts, "combined_vs_baseline_on_common_pairs": changes, "pairs": rows}


def evaluate_case(case, scored):
    annotations = {a["candidate_input_index"]: a for a in case["candidates"]}
    identity_rows, location_rows = [], []
    for c in scored:
        a = annotations[c["candidate_input_index"]]
        identity_rows.append({"key": c["candidate_input_index"], "identity": a["identity"], "scores": c["matched_scores"]})
        reviews = {o2.geometry_key(p): p["judgment"] for p in a["path_reviews"]}
        for point in c["points"]:
            location_rows.append({"key": {"candidate_input_index": c["candidate_input_index"],
                **{k: point[k] for k in ("geometry_basis", "source_x_range", "source_y")}},
                "source_x_range": point["source_x_range"], "geometry_basis": point["geometry_basis"],
                "identity": a["identity"], "judgment": reviews.get(o2.geometry_key(point), "unreviewed"), "scores": point["matched_scores"]})
    positives = [r for r in identity_rows if r["identity"] == "interface"]
    negatives = [r for r in identity_rows if r["identity"] == "non_interface"]
    ranks = {}
    for m in METHODS:
        eligible = [r for r in identity_rows if r["scores"][m] is not None]
        best = max((r["scores"][m] for r in eligible), default=None)
        ranks[m] = {"scored_candidate_count": len(eligible), "unscored_candidate_count": len(scored) - len(eligible),
                    "partially_scored_candidate_count": sum(0 < c["common_point_count"] < c["point_count"] for c in scored),
                    "top_ranked": [{"candidate_input_index": r["key"], "identity": r["identity"], "score": r["scores"][m]}
                                   for r in eligible if order(r["scores"][m], best) == "tie"]}
    path = {}
    for basis in ("native_path", "candidate_center"):
        subset = [r for r in location_rows if r["geometry_basis"] == basis]
        # Only interface identity here: do not conflate structure rejection with localization.
        near = [r for r in subset if r["identity"] == "interface" and r["judgment"] == "near_interface"]
        off = [r for r in subset if r["identity"] == "interface" and r["judgment"] == "off_interface"]
        path[basis] = {"identity_judgment_counts": dict(Counter(f"{r['identity']}/{r['judgment']}" for r in subset)),
                       "interface_location": pair_results(near, off),
                       "interface_location_same_x": pair_results(near, off, same_x=True),
                       "identity_negative_control_same_x": pair_results(near, [r for r in subset if r["identity"] == "non_interface" and r["judgment"] == "off_interface"], same_x=True),
                       "rows": subset}
    return {"case_id": case["case_id"], "partition": case["partition"], "visibility": case["visibility"],
            "identity_counts": dict(Counter(r["identity"] for r in identity_rows)),
            "candidate_ranking": ranks, "identity_ordering": pair_results(positives, negatives), "path_ordering": path}


def artifact():
    files = [Path(__file__), Path(o2.__file__), Path(inspect.getfile(o2.fingerprint_json)), Path(inspect.getfile(o2.sha256_file))]
    payload = {"spec": SPEC, "code": {p.name: o2.sha256_file(p) for p in files}}
    return {**payload, "sha256": o2.fingerprint_json(payload)}


def run(label_paths, output):
    output = Path(output).resolve()
    o2.require(not output.exists(), "output directory already exists; choose a new name")
    paths = [Path(p).resolve() for p in label_paths]
    o2.require(paths and len(set(paths)) == len(paths), "labels paths must be nonempty and unique")
    snapshots, documents, all_packets, inputs = {}, [], {}, []
    for path in paths:
        o2.require(not path.with_name(path.name + ".lock").exists(), "labels writer lock present")
        source_sha = o2.sha256_file(path)
        snapshots[path] = source_sha
        labels = o2.read_json(path)
        o2.require(labels["schema_version"] == o2.LABEL_SCHEMA, "v2 labels required; migrate explicitly")
        for ref in labels["packets"]:
            p = (path.parent / ref["path"]).resolve()
            digest = o2.sha256_file(p)
            o2.require(p not in snapshots or snapshots[p] == digest, "input changed while loading")
            snapshots[p] = digest
        packets = o2.load_packets(labels, path.parent)
        o2.validate_labels(labels, packets)
        # This experiment consumes retrospective controls only; do not expose held-out labels.
        o2.require(all(c["partition"] == "regression" for c in labels["cases"]), "only regression inputs allowed; preserve development/calibration/holdout")
        documents.append(labels)
        all_packets.update(packets)
        inputs.append({"input_index": len(inputs), "dataset_id": labels["dataset_id"],
                       "owners": {k: labels[k] for k in ("label_owner", "split_owner", "split_rationale")},
                       "labels_file_sha256": source_sha,
                       "labels_sha256": o2.fingerprint_json(labels), "revision_count": len(labels.get("review_history", [])),
                       "case_ids": [c["case_id"] for c in labels["cases"]], "packet_sha256s": list(packets)})
    # Validate across files as well: catch duplicate cases/frames and renamed recording groups.
    merged = copy.deepcopy(documents[0])
    merged["cases"] = [c for d in documents for c in d["cases"]]
    merged["packets"] = [{"sha256": h} for h in all_packets]
    o2.validate_labels(merged, all_packets)
    cases, evaluation = [], []
    o2.require(len(merged["cases"]) <= 64, "experiment supports at most 64 cases")
    for case in merged["cases"]:
        frame = all_packets[case["packet_sha256"]][case["case_id"]]
        o2.require(len(frame["witness"]["candidates"]) <= 128, "experiment supports at most 128 candidates per case")
        scored = [score_candidate(c) for c in frame["witness"]["candidates"]]
        cases.append({"case_id": case["case_id"], "packet_sha256": case["packet_sha256"],
                      "frame_index": frame["frame_index"], "glass_id": frame["glass_id"], "candidates": scored})
        evaluation.append(evaluate_case(case, scored))
    for path, digest in snapshots.items():
        o2.require(o2.sha256_file(path) == digest, "input changed during experiment; discard run")
    report = {"schema_version": SCHEMA, "status": "EXPLORATORY_UNCALIBRATED", "auto_acceptance": False,
              "production_decisions_emitted": False, "field_disposition": "FIELD FAIL", "numeric_localization": "NOT_MEASURED",
              "artifact": artifact(), "runtime": {"python": platform.python_version(), "platform": platform.platform()},
              "inputs": inputs, "input_preservation": [{"file_index": i, "before_sha256": h, "after_sha256": o2.sha256_file(p)} for i, (p, h) in enumerate(snapshots.items())],
              "scores": cases, "evaluation": evaluation}
    output.mkdir(parents=True, exist_ok=False)
    o2.write_new(output / "experiment.json", report)
    with (output / "summary.md").open("x", encoding="utf-8") as handle:
        handle.write(render_summary(report))
    # Failure after publication leaves artifacts without the success receipt.
    for path, digest in snapshots.items():
        o2.require(o2.sha256_file(path) == digest, "input changed during publication; discard run")
    o2.write_new(output / "complete.json", {"schema_version": SCHEMA, "status": "COMPLETE",
        "artifact_sha256": report["artifact"]["sha256"],
        "outputs": {n: o2.sha256_file(output / n) for n in ("experiment.json", "summary.md")}})
    return report


def render_summary(report):
    lines = ["# S11 O2 fixed-score experiment", "", "EXPLORATORY_UNCALIBRATED — no production decisions, no fit, no numeric localization.",
             "Higher ranks are hypotheses, not interface acceptance. Partial evidence and ties remain visible.",
             "Rankings/pairs compare all methods on identical usable scales and points; raw baseline-only scores stay in experiment.json.",
             "Pair/scale counts are correlated; no holdout/generalization or field PASS claim.", "",
             f"Artifact: `{report['artifact']['sha256']}`", ""]
    for case in report["evaluation"]:
        key = str(case["case_id"]).replace("|", "\\|").replace("\n", " ")
        lines.extend([f"## Case {key}", "", f"Identity counts: `{case['identity_counts']}`.", "",
                      "| Task | Method | Correct | Reversed | Tie | Unscorable | Common pairs |",
                      "|---|---|---|---|---|---|---|"])
        tasks = {"identity": case["identity_ordering"]}
        for basis, p in case["path_ordering"].items():
            for task in ("interface_location", "interface_location_same_x", "identity_negative_control_same_x"):
                tasks[f"{basis}/{task}"] = p[task]
        notes = []
        for task, result in tasks.items():
            for m in METHODS:
                c = result["counts"][m]
                lines.append(f"| {task} | {m} | {c.get('correct', 0)} | {c.get('reversed', 0)} | {c.get('tie', 0)} | {c.get('unscorable', 0)} | {result['common_scorable_pair_count']} |")
            if result["pair_count"]:
                for baseline, change in result["combined_vs_baseline_on_common_pairs"].items():
                    notes.append(f"- {task}: combined vs {baseline}, improved={change['improved']}, regressed={change['regressed']}.")
        lines.extend(["", *notes, ""])
        for m in METHODS:
            r = case["candidate_ranking"][m]
            lines.append(f"- {m}: scored={r['scored_candidate_count']}, unscored={r['unscored_candidate_count']}, partial={r['partially_scored_candidate_count']}; top ranks={r['top_ranked']}")
        for basis, result in case["path_ordering"].items():
            available = sum(all(r["scores"][m] is not None for m in METHODS) for r in result["rows"])
            lines.append(f"- {basis}: common scored points={available}/{len(result['rows'])}; identity/judgment counts: {result['identity_judgment_counts']}")
        lines.append("")
    lines.extend(["Review full scores/coverage and pair failures in experiment.json. Zero pairs is not success.",
                  "A top non_interface remains a known negative; all-negative scenes have no positive ranking target and no abstention threshold is tested.",
                  "Only a complete.json receipt with matching output hashes confirms a completed run.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        run(args.labels, args.output)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f"Experiment failed: {exc}\n")
    print("Experiment complete. Read summary.md and complete.json in the output directory.")


if __name__ == "__main__":
    main()
