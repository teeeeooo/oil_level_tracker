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


def pair_results(positives, negatives, *, same_x=False, methods=METHODS, target="combined"):
    """Within-case only; pairing counts are correlated diagnostics, not iid trials."""
    o2.require(len(positives) * len(negatives) <= 10000, "too many comparison pairs; use a smaller review set")
    rows = []
    for a in positives:
        for b in negatives:
            if same_x and a["source_x_range"] != b["source_x_range"]:
                continue
            rows.append({"positive": a["key"], "negative": b["key"],
                         "outcomes": {m: order(a["scores"][m], b["scores"][m]) for m in methods}})
    common = [r for r in rows if all(v != "unscorable" for v in r["outcomes"].values())]
    counts = {m: dict(Counter(r["outcomes"][m] for r in rows)) for m in methods}
    changes = {}
    for base in methods:
        if base == target:
            continue
        improved = [r for r in common if r["outcomes"][base] != "correct" and r["outcomes"][target] == "correct"]
        regressed = [r for r in common if r["outcomes"][base] == "correct" and r["outcomes"][target] != "correct"]
        changes[base] = {"improved": len(improved), "regressed": len(regressed)}
    return {"pair_count": len(rows), "common_scorable_pair_count": len(common),
            "counts": counts, f"{target}_vs_baseline_on_common_pairs": changes, "pairs": rows}


def evaluate_case(case, scored, *, methods=METHODS, target="combined", include_path=True):
    def compare(positive, negative, **kwargs):
        return pair_results(positive, negative, methods=methods, target=target, **kwargs)
    annotations = {a["candidate_input_index"]: a for a in case["candidates"]}
    identity_rows, location_rows = [], []
    for c in scored:
        a = annotations[c["candidate_input_index"]]
        identity_rows.append({"key": c["candidate_input_index"], "identity": a["identity"], "scores": c["matched_scores"]})
        if not include_path:
            continue
        reviews = {o2.geometry_key(p): p["judgment"] for p in a["path_reviews"]}
        for point in c["points"]:
            location_rows.append({"key": {"candidate_input_index": c["candidate_input_index"],
                **{k: point[k] for k in ("geometry_basis", "source_x_range", "source_y")}},
                "source_x_range": point["source_x_range"], "geometry_basis": point["geometry_basis"],
                "identity": a["identity"], "judgment": reviews.get(o2.geometry_key(point), "unreviewed"), "scores": point["matched_scores"]})
    positives = [r for r in identity_rows if r["identity"] == "interface"]
    negatives = [r for r in identity_rows if r["identity"] == "non_interface"]
    ranks = {}
    for m in methods:
        eligible = [r for r in identity_rows if r["scores"][m] is not None]
        best = max((r["scores"][m] for r in eligible), default=None)
        ranks[m] = {"scored_candidate_count": len(eligible), "unscored_candidate_count": len(scored) - len(eligible),
                    "partially_scored_candidate_count": sum(0 < c["common_point_count"] < c["point_count"] for c in scored),
                    "top_ranked": [{"candidate_input_index": r["key"], "identity": r["identity"], "score": r["scores"][m]}
                                   for r in eligible if order(r["scores"][m], best) == "tie"]}
    path = {}
    for basis in (("native_path", "candidate_center") if include_path else ()):
        subset = [r for r in location_rows if r["geometry_basis"] == basis]
        # Only interface identity here: do not conflate structure rejection with localization.
        near = [r for r in subset if r["identity"] == "interface" and r["judgment"] == "near_interface"]
        off = [r for r in subset if r["identity"] == "interface" and r["judgment"] == "off_interface"]
        path[basis] = {"identity_judgment_counts": dict(Counter(f"{r['identity']}/{r['judgment']}" for r in subset)),
                       "interface_location": compare(near, off),
                       "interface_location_same_x": compare(near, off, same_x=True),
                       "identity_negative_control_same_x": compare(near, [r for r in subset if r["identity"] == "non_interface" and r["judgment"] == "off_interface"], same_x=True),
                       "rows": subset}
    return {"case_id": case["case_id"], "partition": case["partition"], "visibility": case["visibility"],
            "identity_counts": dict(Counter(r["identity"] for r in identity_rows)),
            "candidate_ranking": ranks, "identity_ordering": compare(positives, negatives), "path_ordering": path}


ABLATION_SCHEMA = "s11-o2-locality-ablation-v1"
ABLATION_METHOD = "without_locality"
COMMON_METHODS = (*METHODS, ABLATION_METHOD)
CA_METHODS = (*METHODS[:2], ABLATION_METHOD)
ABLATION_SPEC = {
    "id": "fixed-exponent-locality-ablation-v1",
    "score": "(contrast*alignment)**(1/3)",
    "fixed": "v1 exponent, scale/point medians, geometry preference, labels and pair definitions",
    "common_support": "exact v1 all-three-method-available scales and preferred points",
    "ca_supported": "scales with contrast and alignment available; no locality imputation",
    "coverage_comparison": "newly scorable pairs reported separately, never counted as common-support improvements",
    "fitted": False, "threshold": None,
}


def ablation_scores(scored, *, common_support):
    """Derive both views from v1 scores, with no annotation or measurement changes."""
    methods = COMMON_METHODS if common_support else CA_METHODS
    candidates = []
    for candidate in scored:
        points = []
        for point in candidate["points"]:
            scales = []
            for scale in point["scales"]:
                raw = scale["scores"]
                c, a = raw["contrast_only"], raw["alignment_only"]
                without = (c * a) ** (1 / 3) if c is not None and a is not None else None
                values = {**raw, ABLATION_METHOD: without}
                scales.append({"band_width_px": scale["band_width_px"], "scores": values})
            usable = [s for s in scales if all(s["scores"][m] is not None for m in methods)]
            matched = {m: median([s["scores"][m] for s in usable]) for m in methods}
            if common_support:
                o2.require(all(matched[m] == point["matched_scores"][m] for m in METHODS),
                           "v1 point support/score changed during ablation")
            points.append({**{k: point[k] for k in ("geometry_basis", "source_x_range", "source_y")},
                           "scales": scales, "matched_scores": matched,
                           "common_scale_count": len(usable), "scale_count": len(scales),
                           "usable_band_widths": [s["band_width_px"] for s in usable]})
        preferred = [p for p in points if p["geometry_basis"] == candidate["identity_geometry_basis"]]
        matched = {m: median([p["matched_scores"][m] for p in preferred]) for m in methods}
        if common_support:
            o2.require(all(matched[m] == candidate["matched_scores"][m] for m in METHODS),
                       "v1 candidate support/score changed during ablation")
        candidates.append({"candidate_input_index": candidate["candidate_input_index"],
                           "witness_sha256": candidate["witness_sha256"],
                           "identity_geometry_basis": candidate["identity_geometry_basis"],
                           "matched_scores": matched, "points": points, "point_count": len(preferred),
                           "common_point_count": sum(p["common_scale_count"] > 0 for p in preferred)})
    return candidates


def evaluation_tasks(case):
    tasks = {"identity": case["identity_ordering"]}
    for basis, path in case["path_ordering"].items():
        for task in ("interface_location", "interface_location_same_x", "identity_negative_control_same_x"):
            tasks[f"{basis}/{task}"] = path[task]
    return tasks


def support_transition(common, expanded, *, method=ABLATION_METHOD):
    """Support changes can also change medians of already-scorable items."""
    output = {}
    expanded_tasks = evaluation_tasks(expanded)
    for task, previous in evaluation_tasks(common).items():
        def index(result):
            return {o2.fingerprint_json([r["positive"], r["negative"]]): r for r in result["pairs"]}
        old, new = index(previous), index(expanded_tasks[task])
        o2.require(old.keys() == new.keys(), "support views changed pair inventory")
        rows = []
        for key, before in old.items():
            after = new[key]
            a, b = before["outcomes"][method], after["outcomes"][method]
            o2.require(not (a != "unscorable" and b == "unscorable"), "expanded support lost a scorable pair")
            category = ("still_unscorable" if b == "unscorable" else "newly_scorable" if a == "unscorable"
                        else "retained_changed_order" if a != b else "retained_same_order")
            rows.append({"positive": before["positive"], "negative": before["negative"],
                         "category": category, "common_outcome": a, "ca_supported_outcome": b})
        output[task] = {"counts": dict(Counter(r["category"] for r in rows)),
                        "newly_scorable_outcomes": dict(Counter(r["ca_supported_outcome"] for r in rows if r["category"] == "newly_scorable")),
                        "pairs": rows}
    return output


def evaluate_locality_ablation(case, scored):
    common = ablation_scores(scored, common_support=True)
    expanded = ablation_scores(scored, common_support=False)
    common_evaluation = evaluate_case(case, common, methods=COMMON_METHODS, target=ABLATION_METHOD)
    expanded_evaluation = evaluate_case(case, expanded, methods=CA_METHODS, target=ABLATION_METHOD)
    return {"case_id": case["case_id"], "v1_common_scores_preserved": True,
            "common_support": {"scores": common, "evaluation": common_evaluation},
            "ca_supported": {"scores": expanded, "evaluation": expanded_evaluation},
            "support_transition": support_transition(common_evaluation, expanded_evaluation)}


def render_ablation_summary(report):
    lines = ["# S11 O2 controlled locality ablation", "",
             "No fit, thresholds, production decisions or new labels. Exponent and medians are unchanged.",
             "Common support isolates locality removal; C/A-supported results change support and are a separate experiment view.",
             "Newly scorable is not necessarily correct. Retained pair order can change when extra scales/points enter medians.",
             "No pooled task totals: same-X pairs overlap all-X pairs. See experiment.json for exact scale/point support.",
             f"Reference verified: input hashes, v1 scores and evaluation exactly equal. Reference file SHA256: {report['reference']['file_sha256']}", ""]
    for name, methods in (("common_support", COMMON_METHODS), ("ca_supported", CA_METHODS)):
        lines.extend([f"## View: {name}", "", render_summary(
            {"artifact": report["artifact"], "evaluation": [c[name]["evaluation"] for c in report["locality_ablation"]]},
            methods=methods, target=ABLATION_METHOD)])
    lines.extend(["## Support transitions and named controls", ""])
    for case in report["locality_ablation"]:
        lines.extend([f"Case: {case['case_id']}", ""])
        for task, result in case["support_transition"].items():
            if result["pairs"]:
                lines.append(f"- {task}: {result['counts']}; newly scorable outcomes={result['newly_scorable_outcomes']}")
        for task, result in evaluation_tasks(case["common_support"]["evaluation"]).items():
            for label, predicate in (
                ("improved vs combined", lambda r: r["outcomes"]["combined"] in ("reversed", "tie") and r["outcomes"][ABLATION_METHOD] == "correct"),
                ("regressed vs combined", lambda r: r["outcomes"]["combined"] == "correct" and r["outcomes"][ABLATION_METHOD] in ("reversed", "tie")),
                ("still reversed", lambda r: r["outcomes"][ABLATION_METHOD] == "reversed")):
                examples = [r for r in result["pairs"] if predicate(r)]
                for row in examples[:3]:
                    lines.append(f"- {task}, {label} (up to 3 of {len(examples)}): positive={row['positive']}, negative={row['negative']}; {row['outcomes']}")
        lines.append("")
    return "\n".join(lines)


PROFILE_SCHEMA = "s11-o2-identity-profile-v1"
PROFILE_METHOD = "two_region_profile"
PROFILE_METHODS = (*COMMON_METHODS, PROFILE_METHOD)
PROFILE_BANDS = ("far_above", "near_above", "near_below", "far_below")
PROFILE_SPEC = {
    "id": "two-region-versus-ramp-excursion-v1",
    "observations": "four available raw-gray band means, equal band weight",
    "templates": {"step": [-1, -1, 1, 1], "near_above_excursion": [0, 1, 0, 0],
                  "near_below_excursion": [0, 0, 1, 0], "central_band": [0, 1, 1, 0]},
    "ramp_coordinates": "clipped_local_y_range half-open pixel midpoint; not visible-pixel centroid",
    "residual": "sum squared errors after within-profile offset/amplitude projection; not label training",
    "score": "(min(ramp,near_above_excursion,near_below_excursion,central_band) SSE - step SSE)/(centered_energy+4*(1/255)**2)",
    "aggregation": "unchanged median of available scales then preferred-geometry points",
    "common_support": "intersection of profile and original contrast/alignment/combined availability",
    "profile_supported": "all valid four-band profiles; no C/A/L imputation",
    "evaluation": "candidate identity only; no path judgment used or emitted",
    "limitation": "a structural step with the same profile is indistinguishable; not physical identity certification",
    "trained_on_labels": False, "threshold": None,
}


def profile_scale(scale):
    """Compare shapes of a four-band profile, not edge strength or signed polarity."""
    bands = o2.unique(scale.get("bands", []), "name", "profile bands")
    observations, reasons = [], []
    for name in PROFILE_BANDS:
        band = bands.get(name, {})
        gray, status = value(band, "gray_mean", bounded=True)
        available = band.get("available")
        o2.require(available is None or type(available) is bool, "invalid profile availability")
        extent = band.get("clipped_local_y_range")
        range_status = "missing" if "clipped_local_y_range" not in band else "null" if extent is None else "present"
        if extent is not None:
            o2.require(isinstance(extent, (list, tuple)) and len(extent) == 2
                       and all(type(v) is int and v >= 0 for v in extent) and extent[0] <= extent[1],
                       "invalid profile band range")
        midpoint = (extent[0] + extent[1] - 1) / 2 if extent is not None and extent[0] < extent[1] else None
        observations.append({"name": name, "gray_mean": gray, "gray_mean_status": status,
                             "available": available, "available_status": "missing" if "available" not in band else "null" if available is None else "present",
                             "clipped_local_y_range": extent, "range_status": range_status,
                             "reason": band.get("reason"), "valid_fraction": band.get("valid_fraction"),
                             "midpoint": midpoint})
        if available is not True or gray is None or midpoint is None:
            reasons.append(name + ":unavailable_profile_input")
    result = {"band_width_px": scale["band_width_px"], "observations": observations,
              "unavailable_reasons": reasons, "residuals": None, "centered_energy": None,
              "best_competing_models": [], "score": None}
    if reasons:
        return result
    y = [b["gray_mean"] for b in observations]
    x = [b["midpoint"] for b in observations]
    o2.require(all(a < b for a, b in zip(x, x[1:])), "profile band order must increase")
    centered = [v - sum(y)/4 for v in y]
    energy = sum(v*v for v in centered)
    def residual(template):
        h = [v - sum(template)/4 for v in template]
        amplitude = sum(a*b for a,b in zip(h,centered)) / sum(v*v for v in h)
        return sum((v-amplitude*t)**2 for v,t in zip(centered,h))
    residuals = {name: residual(template) for name, template in PROFILE_SPEC["templates"].items()}
    residuals["ramp"] = residual(x)
    rivals = {k:v for k,v in residuals.items() if k != "step"}
    best = min(rivals.values())
    result.update(residuals={"constant": energy, **residuals}, centered_energy=energy,
                  best_competing_models=[k for k,v in rivals.items() if math.isclose(v,best,rel_tol=0,abs_tol=1e-12)],
                  score=(best-residuals["step"])/(energy+4*(1/255)**2))
    return result


def identity_profile_views(raw_candidates, scored):
    """Use existing geometry joins and v1 scores; never feed labels to projection."""
    raw = {c["candidate_input_index"]: c for c in raw_candidates}
    derived = ablation_scores(scored, common_support=True)
    for source, target in zip(scored, derived):
        sectors = {tuple(s["source_x_range"]): s for s in raw[source["candidate_input_index"]]["sectors"]}
        for old_point, point in zip(source["points"], target["points"]):
            sector = sectors[tuple(point["source_x_range"])]
            centers = {c["role"]: c for c in sector.get("centers", [])}
            center = centers.get(old_point["measurement_role"])
            raw_scales = {s["band_width_px"]: s for s in center["scales"]} if center else {}
            for scale in point["scales"]:
                detail = profile_scale(raw_scales[scale["band_width_px"]])
                scale["profile"] = detail
                scale["scores"][PROFILE_METHOD] = detail["score"]
    views = {}
    for name, methods in (("common_support", PROFILE_METHODS), ("profile_supported", (PROFILE_METHOD,))):
        candidates = copy.deepcopy(derived)
        for candidate in candidates:
            for point in candidate["points"]:
                usable = [s for s in point["scales"] if all(s["scores"][m] is not None for m in methods)]
                point["matched_scores"] = {m: median([s["scores"][m] for s in usable]) for m in methods}
                point["common_scale_count"] = len(usable)
                point["usable_band_widths"] = [s["band_width_px"] for s in usable]
            preferred = [p for p in candidate["points"] if p["geometry_basis"] == candidate["identity_geometry_basis"]]
            candidate["matched_scores"] = {m: median([p["matched_scores"][m] for p in preferred]) for m in methods}
            candidate["common_point_count"] = sum(p["common_scale_count"] > 0 for p in preferred)
        views[name] = candidates
    return views


def evaluate_identity_profile(case, raw_candidates, scored):
    scores = identity_profile_views(raw_candidates, scored)
    views = {name: {"scores": scores[name], "evaluation": evaluate_case(
        case, scores[name], methods=methods, target=PROFILE_METHOD, include_path=False)}
        for name,methods in (("common_support", PROFILE_METHODS), ("profile_supported", (PROFILE_METHOD,)))}
    return {"case_id": case["case_id"], **views,
            "support_transition": support_transition(views["common_support"]["evaluation"],
                views["profile_supported"]["evaluation"], method=PROFILE_METHOD)}


def render_profile_summary(report):
    lines = ["# S11 O2 candidate identity profile experiment", "",
             "A two-region shape is a hypothesis, not physical identity. A structural step may be indistinguishable.",
             "Equal-weight four-band profiles compare persistent steps with ramps and local excursions; no label training or threshold.",
             "Negative scores favor a competing shape; zero is not a certified negative or abstention decision.",
             "Candidate identity only. No near/off truth or numeric localization is evaluated in this mode.",
             f"Reference v1 inputs/scores/evaluation reproduced. Reference SHA256: {report['reference']['file_sha256']}", ""]
    for name, methods in (("common_support", PROFILE_METHODS), ("profile_supported", (PROFILE_METHOD,))):
        lines.extend([f"## View: {name}", "", render_summary(
            {"artifact": report["artifact"], "evaluation": [c[name]["evaluation"] for c in report["identity_profile"]]},
            methods=methods,target=PROFILE_METHOD)])
    lines.extend(["## Availability changes and failure examples", ""])
    for case in report["identity_profile"]:
        lines.extend([f"Case: {case['case_id']}", ""])
        preferred_scales = [s for c in case["profile_supported"]["scores"] for p in c["points"]
                            if p["geometry_basis"] == c["identity_geometry_basis"] for s in p["scales"]]
        reasons = Counter(reason for s in preferred_scales for reason in s["profile"]["unavailable_reasons"])
        lines.append(f"- Preferred-geometry scales: total={len(preferred_scales)}, profile available={sum(s['profile']['score'] is not None for s in preferred_scales)}; missing-input reasons (may overlap): {dict(reasons)}")
        transition = case["support_transition"]["identity"]
        lines.append(f"- Support changes: {transition['counts']}; newly scorable outcomes: {transition['newly_scorable_outcomes']}")
        for name in ("common_support", "profile_supported"):
            candidate_scores = {c["candidate_input_index"]: c["matched_scores"] for c in case[name]["scores"]}
            rows = case[name]["evaluation"]["identity_ordering"]["pairs"]
            for outcome in ("reversed", "tie", "unscorable"):
                examples = [r for r in rows if r["outcomes"][PROFILE_METHOD] == outcome]
                for row in examples[:3]:
                    lines.append(f"- {name}/{outcome} (up to 3 of {len(examples)}): positive={row['positive']}, negative={row['negative']}; {row['outcomes']}")
                    lines.append(f"  Scores: positive={candidate_scores[row['positive']]}; negative={candidate_scores[row['negative']]}")
        lines.append("")
    return "\n".join(lines)


def artifact(*, locality_ablation=False, identity_profile=False):
    files = [Path(__file__), Path(o2.__file__), Path(inspect.getfile(o2.fingerprint_json)), Path(inspect.getfile(o2.sha256_file))]
    payload = {"spec": SPEC, "code": {p.name: o2.sha256_file(p) for p in files}}
    if locality_ablation:
        payload["ablation_spec"] = ABLATION_SPEC
    if identity_profile:
        payload["profile_spec"] = PROFILE_SPEC
    return {**payload, "sha256": o2.fingerprint_json(payload)}


def run(label_paths, output, *, locality_ablation=False, identity_profile=False, reference=None):
    output = Path(output).resolve()
    o2.require(not output.exists(), "output directory already exists; choose a new name")
    o2.require(not (locality_ablation and identity_profile), "experiment modes are mutually exclusive")
    o2.require((locality_ablation or identity_profile) == (reference is not None),
               "an experiment mode (--locality-ablation or --identity-profile) and --reference must be supplied together")
    paths = [Path(p).resolve() for p in label_paths]
    o2.require(paths and len(set(paths)) == len(paths), "labels paths must be nonempty and unique")
    snapshots, documents, all_packets, inputs = {}, [], {}, []
    prior = None
    if reference is not None:
        reference = Path(reference).resolve()
        snapshots[reference] = o2.sha256_file(reference)
        prior = o2.read_json(reference)
        o2.require(prior.get("schema_version") == SCHEMA, "reference must be a v1 score experiment")
        o2.require(prior.get("artifact", {}).get("spec") == SPEC, "reference score specification differs")
        fingerprint = {k: v for k, v in prior["artifact"].items() if k != "sha256"}
        o2.require(o2.fingerprint_json(fingerprint) == prior["artifact"].get("sha256"), "reference artifact hash mismatch")
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
    cases, evaluation, ablations, profiles = [], [], [], []
    o2.require(len(merged["cases"]) <= 64, "experiment supports at most 64 cases")
    for case in merged["cases"]:
        frame = all_packets[case["packet_sha256"]][case["case_id"]]
        o2.require(len(frame["witness"]["candidates"]) <= 128, "experiment supports at most 128 candidates per case")
        scored = [score_candidate(c) for c in frame["witness"]["candidates"]]
        cases.append({"case_id": case["case_id"], "packet_sha256": case["packet_sha256"],
                      "frame_index": frame["frame_index"], "glass_id": frame["glass_id"], "candidates": scored})
        evaluation.append(evaluate_case(case, scored))
        if locality_ablation:
            ablations.append(evaluate_locality_ablation(case, scored))
        if identity_profile:
            profiles.append(evaluate_identity_profile(case, frame["witness"]["candidates"], scored))
    if prior is not None:
        for key, actual in (("inputs", inputs), ("scores", cases), ("evaluation", evaluation)):
            o2.require(prior.get(key) == actual, f"reference {key} differs; preserve inputs and investigate drift")
    for path, digest in snapshots.items():
        o2.require(o2.sha256_file(path) == digest, "input changed during experiment; discard run")
    report = {"schema_version": SCHEMA, "status": "EXPLORATORY_UNCALIBRATED", "auto_acceptance": False,
              "production_decisions_emitted": False, "field_disposition": "FIELD FAIL", "numeric_localization": "NOT_MEASURED",
              "artifact": artifact(locality_ablation=locality_ablation, identity_profile=identity_profile), "runtime": {"python": platform.python_version(), "platform": platform.platform()},
              "inputs": inputs, "input_preservation": [{"file_index": i, "before_sha256": h, "after_sha256": o2.sha256_file(p)} for i, (p, h) in enumerate(snapshots.items())],
              "scores": cases, "evaluation": evaluation}
    if locality_ablation:
        report["schema_version"] = ABLATION_SCHEMA
        report["locality_ablation"] = ablations
    if identity_profile:
        report["schema_version"] = PROFILE_SCHEMA
        report["identity_profile"] = profiles
    if prior is not None:
        report["reference"] = {"file_sha256": snapshots[reference],
                               "artifact_sha256": prior["artifact"]["sha256"],
                               "inputs_scores_evaluation_equal": True}
    output.mkdir(parents=True, exist_ok=False)
    o2.write_new(output / "experiment.json", report)
    with (output / "summary.md").open("x", encoding="utf-8") as handle:
        handle.write(render_profile_summary(report) if identity_profile else
                     render_ablation_summary(report) if locality_ablation else render_summary(report))
    # Failure after publication leaves artifacts without the success receipt.
    for path, digest in snapshots.items():
        o2.require(o2.sha256_file(path) == digest, "input changed during publication; discard run")
    o2.write_new(output / "complete.json", {"schema_version": report["schema_version"], "status": "COMPLETE",
        "artifact_sha256": report["artifact"]["sha256"],
        "outputs": {n: o2.sha256_file(output / n) for n in ("experiment.json", "summary.md")}})
    return report


def render_summary(report, *, methods=METHODS, target="combined"):
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
        tasks = evaluation_tasks(case)
        notes = []
        for task, result in tasks.items():
            for m in methods:
                c = result["counts"][m]
                lines.append(f"| {task} | {m} | {c.get('correct', 0)} | {c.get('reversed', 0)} | {c.get('tie', 0)} | {c.get('unscorable', 0)} | {result['common_scorable_pair_count']} |")
            if result["pair_count"]:
                for baseline, change in result[f"{target}_vs_baseline_on_common_pairs"].items():
                    notes.append(f"- {task}: {target} vs {baseline}, improved={change['improved']}, regressed={change['regressed']}.")
        lines.extend(["", *notes, ""])
        for m in methods:
            r = case["candidate_ranking"][m]
            lines.append(f"- {m}: scored={r['scored_candidate_count']}, unscored={r['unscored_candidate_count']}, partial={r['partially_scored_candidate_count']}; top ranks={r['top_ranked']}")
        for basis, result in case["path_ordering"].items():
            available = sum(all(r["scores"][m] is not None for m in methods) for r in result["rows"])
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
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--locality-ablation", action="store_true",
                        help="Compare removing locality on v1 common support; separately report C/A-supported coverage.")
    modes.add_argument("--identity-profile", action="store_true", help="Compare two-region versus ramp/excursion profile shape for candidate identity only.")
    parser.add_argument("--reference", type=Path, help="Existing original v1 experiment.json; required with either experiment mode.")
    args = parser.parse_args()
    try:
        run(args.labels, args.output, locality_ablation=args.locality_ablation,
            identity_profile=args.identity_profile, reference=args.reference)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f"Experiment failed: {exc}\n")
    print("Experiment complete. Read summary.md and complete.json in the output directory.")


if __name__ == "__main__":
    main()
