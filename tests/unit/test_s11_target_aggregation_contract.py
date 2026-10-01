"""W1 counter-controls: target consistency, not a new identity classifier.

Use the actual ranking/evaluation owners. Constructed local measurements isolate
pooling loss; raster controls separately exercise the O1 extraction boundary.
Truth never selects scoring points. Scripted decisions test evaluator semantics
only, and do not claim the current scorer can emit those decisions.
"""
import copy
from dataclasses import asdict

import numpy as np
import pytest

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_shadow_experiment as experiment
from tests.unit.test_oil_interface_witness import measure
from tests.unit.test_s11_shadow_experiment import candidate, scale


def proposal(norms, index=0):
    """Three exact geometries with measured, not label-derived, local inputs."""
    result = candidate(equal=True)
    result.update(candidate_input_index=index, canonical_y=10,
                  measurement_status="measured")
    result["sectors"] = []
    for i, norm in enumerate(norms):
        result["sectors"].append({
            "sector": i, "source_x_range": [20*i, 20*(i+1)],
            "path_source_y": 10, "candidate_source_y": 10,
            "centers": [{"role": "native_path", "source_y": 10,
                         "scales": [scale(norm=norm, delta=norm/100,
                                          width=w) for w in (8, 16, 24)]}],
        })
    return result


def annotation(raw, identity, judgments):
    return {
        "candidate_input_index": raw["candidate_input_index"],
        "identity": identity, "artifact_tags": [], "artifact_note": "",
        "entity_id": "", "witness_sha256": o2.fingerprint_json(raw),
        "path_reviews": [
            {"geometry_basis": "native_path",
             "source_x_range": s["source_x_range"], "source_y": s["path_source_y"],
             "judgment": judgment,
             "review": {"reviewer": "synthetic", "basis": "synthetic_construction",
                        "note": "Constructed counterexample, not a video label."}}
            for s, judgment in zip(raw["sectors"], judgments, strict=True)
        ],
    }


def case_for(annotations):
    return {"case_id": "synthetic", "partition": "regression",
            "visibility": "visible", "contour": [], "candidates": annotations,
            "packet_sha256": "synthetic-packet", "recording_group": "synthetic",
            "physical_case_id": "synthetic", "label_basis": "synthetic_construction"}


def native_points(scored):
    return [p for p in scored["points"] if p["geometry_basis"] == "native_path"]


def test_partial_positive_loses_identity_rank_despite_correct_local_order():
    partial, weak_negative = proposal([0, 9, 0]), proposal([1/9]*3, 1)
    annotations = [annotation(partial, "interface", ["off_interface", "near_interface", "off_interface"]),
                   annotation(weak_negative, "non_interface", ["off_interface"]*3)]
    for raw, label in zip((partial, weak_negative), annotations, strict=True):
        o2.validate_annotation_v2(label, raw)
    scored = [experiment.score_candidate(c) for c in (partial, weak_negative)]
    result = experiment.evaluate_case(case_for(annotations), scored)
    assert [p["matched_scores"]["contrast_only"] for p in native_points(scored[0])] == [0, .9, 0]
    assert scored[0]["matched_scores"]["contrast_only"] == 0
    assert scored[1]["matched_scores"]["contrast_only"] == pytest.approx(.1)
    assert result["identity_ordering"]["counts"]["contrast_only"] == {"reversed": 1}
    local = result["path_ordering"]["native_path"]["interface_location"]
    assert local["counts"]["contrast_only"] == {"correct": 2}
    assert local["counts"]["combined"] == {"correct": 2}
    assert result["identity_counts"] == {"interface": 1, "non_interface": 1}


def test_max_repairs_partial_rank_but_promotes_the_same_isolated_glare():
    partial, glare = proposal([0, 9, 0]), proposal([0, 9, 0], 1)
    full, weak_negative = proposal([1]*3, 2), proposal([1/9]*3, 3)
    # Hypothetical max is only a rejected oracle here, not an experiment mode.
    def maximum(raw):
        return max(p["matched_scores"]["contrast_only"]
                   for p in native_points(experiment.score_candidate(raw)))
    assert maximum(partial) > maximum(weak_negative)
    assert maximum(glare) > maximum(full)
    scored = [experiment.score_candidate(c) for c in (partial, glare)]
    assert native_points(scored[0]) == native_points(scored[1])
    labels = [annotation(partial, "interface", ["off_interface", "near_interface", "off_interface"]),
              annotation(glare, "non_interface", ["off_interface"]*3)]
    before = copy.deepcopy(scored)
    result = experiment.evaluate_case(case_for(labels), scored)
    assert all(counts == {"tie": 1} for counts in result["identity_ordering"]["counts"].values())
    assert scored == before
    assert "decision" not in scored[0]  # a tie is not an implemented abstainer


@pytest.mark.parametrize("judgments", [
    ["near_interface"]*3,
    ["off_interface", "near_interface", "off_interface"],
])
def test_supported_holistic_identity_does_not_certify_local_or_scalar_accuracy(judgments):
    raw = proposal([1]*3)
    label = annotation(raw, "interface", judgments)
    case = case_for([label])
    packets = {case["packet_sha256"]: {case["case_id"]: {"witness": {"candidates": [raw]}}}}
    before = copy.deepcopy((case, packets))
    report = o2.summarize([case], packets, {
        (case["case_id"], 0): {"decision": "INTERFACE_SUPPORTED"},
    })
    assert report["identity_recall"] == 1
    path = report["qualitative_path_review"]["supported_proposals"]["by_geometry_basis"]
    assert path["native_path"]["near_interface"] == judgments.count("near_interface")
    assert path["native_path"]["off_interface"] == judgments.count("off_interface")
    assert path["candidate_center"]["unreviewed"] == 3
    loc = report["localization"]["supported_interface_proposals"]
    assert loc["status"] == "not_measured"
    assert loc["mean_distance_to_review_interval_px"] is None
    assert report["localization"]["full_path_localization_pass"] is None
    assert (case, packets) == before  # no contour or scalar Y manufactured


def test_scripted_unresolved_collision_preserves_truth_and_visible_frame_denominator():
    raw = [proposal([0, 9, 0], i) for i in range(2)]
    labels = [annotation(raw[0], "interface", ["off_interface", "near_interface", "off_interface"]),
              annotation(raw[1], "non_interface", ["off_interface"]*3)]
    case = case_for(labels)
    packets = {case["packet_sha256"]: {case["case_id"]: {"witness": {"candidates": raw}}}}
    report = o2.summarize([case], packets, {
        (case["case_id"], i): {"decision": "UNRESOLVED"} for i in range(2)
    })
    assert report["confusion"]["interface"] == {"UNRESOLVED": 1}
    assert report["confusion"]["non_interface"] == {"UNRESOLVED": 1}
    assert report["abstention_count"] == 2
    assert report["visible_frame_count"] == 1
    assert report["visible_frame_identity_support_recall"] == 0
    assert report["wrong_non_interface_support_count"] == 0
    assert labels[0]["identity"] == "interface"  # ambiguity is not relabeling


@pytest.mark.parametrize('unknown_identity', ['uncertain', 'unreviewed'])
def test_truth_change_removes_rank_pairs_without_changing_measurements_or_scores(unknown_identity):
    """Constructed alternate truth is a denominator change, not a method gain."""
    raw = [proposal([0, 9, 0]), proposal([1/9]*3, 1)]
    case = case_for([annotation(raw[0], 'interface', ['near_interface']*3),
                     annotation(raw[1], 'non_interface', ['off_interface']*3)])
    scored = [experiment.score_candidate(c) for c in raw]
    before = copy.deepcopy((case, raw, scored))
    baseline = experiment.evaluate_case(case, scored)
    assert baseline['identity_ordering']['counts']['combined'] == {'reversed': 1}
    alternate = copy.deepcopy(case)
    alternate['candidates'][1]['identity'] = unknown_identity
    result = experiment.evaluate_case(alternate, scored)
    assert result['identity_counts'] == {'interface': 1, unknown_identity: 1}
    assert result['identity_ordering']['pairs'] == []
    for method in experiment.METHODS:
        assert result['candidate_ranking'][method]['scored_candidate_count'] == 2
    assert result['path_ordering']['native_path']['identity_judgment_counts'] == {
        'interface/near_interface': 3, f'{unknown_identity}/off_interface': 3}
    assert (case, raw, scored) == before
    assert experiment.evaluate_case(case, scored) == baseline


def test_spatial_permutation_is_lost_in_scalar_but_retained_in_point_evidence():
    a = experiment.score_candidate(proposal([0, 9, 9]))
    b = experiment.score_candidate(proposal([9, 0, 9]))
    assert a["matched_scores"] == b["matched_scores"]
    assert native_points(a) != native_points(b)
    assert [p["source_x_range"] for p in native_points(a)] == [[0, 20], [20, 40], [40, 60]]


def test_missing_native_is_not_replaced_by_clean_center_in_partial_candidate():
    raw = proposal([0, 9, 0])
    for s in raw["sectors"]:
        s["candidate_source_y"] = 12
        s["centers"].append({"role": "candidate_center", "source_y": 12, "scales": [scale()]})
        for sc in s["centers"][0]["scales"]:
            sc["bands"][2]["available"] = False
    scored = experiment.score_candidate(raw)
    assert scored["identity_geometry_basis"] == "native_path"
    assert scored["point_count"] == 3 and scored["common_point_count"] == 0
    assert scored["matched_scores"]["combined"] is None
    assert all(p["matched_scores"]["combined"] is not None
               for p in scored["points"] if p["geometry_basis"] == "candidate_center")


def test_missing_scale_does_not_hide_point_or_scale_denominators():
    raw = proposal([0, 9, 0])
    for sc in raw["sectors"][0]["centers"][0]["scales"][:2]:
        sc["bands"][2]["gray_mean"] = None
    scored = experiment.score_candidate(raw)
    points = native_points(scored)
    assert scored["common_point_count"] == scored["point_count"] == 3
    assert [p["scale_count"] for p in points] == [3, 3, 3]
    assert [p["common_scale_count"] for p in points] == [1, 3, 3]
    assert sum(p["common_scale_count"] for p in points) == 7
    assert points[0]["scales"][0]["field_status"]["far_above.gray_mean"] == "null"


def test_stationary_step_and_identical_structure_are_observationally_indistinguishable():
    raster = np.full((200, 200), 180, dtype=np.uint8)
    raster[100:] = 80
    # Same image can be constructed as an interface or a structural edge.
    # Neither physical truth is an input to extraction or profile scoring.
    a, b = measure(raster), measure(raster.copy())
    assert a == b
    scores = [experiment.profile_scale(asdict(c.scales[0]))["score"]
              for s in a.candidates[0].sectors for c in s.centers]
    assert all(s is not None and s > 0 for s in scores)
    assert a.candidates[0].decision == "NOT_EVALUATED"


def test_crossing_static_region_retains_context_but_does_not_supply_score_authority():
    raster = np.full((200, 200), 180, dtype=np.uint8)
    raster[100:] = 80
    static = np.zeros_like(raster)
    static[:, 80:120] = 1  # crossing known static reference, not an Oil truth mask
    clean = measure(raster, static_map=np.zeros_like(raster))
    crossed = measure(raster, static_map=static)
    bands = [s.centers[0].scales[0].bands[1] for s in crossed.candidates[0].sectors]
    assert [b.static_overlap for b in bands] == [0, 0, 1, 0, 0]
    assert all(b.static_available for b in bands)
    before = copy.deepcopy(asdict(crossed.candidates[0]))
    clean_score = experiment.score_candidate(asdict(clean.candidates[0]))
    crossed_score = experiment.score_candidate(asdict(crossed.candidates[0]))
    assert clean_score["points"] == crossed_score["points"]
    assert asdict(crossed.candidates[0]) == before
    assert crossed.candidates[0].decision == "NOT_EVALUATED"


@pytest.mark.parametrize("occlusion", ["mask", "glare"])
def test_raster_occlusion_retains_extent_and_unavailable_evidence(occlusion):
    raster = np.full((200, 200), 180, dtype=np.uint8)
    raster[100:] = 80
    mask, glare = np.ones_like(raster), np.zeros_like(raster)
    if occlusion == "mask":
        mask[:, :80] = 0
    else:
        glare[:, :80] = 1
    witness = measure(raster, effective_mask=mask, glare_mask=glare)
    raw = asdict(witness.candidates[0])
    scored = experiment.score_candidate(raw)
    assert scored["point_count"] == 5
    assert scored["points"][0]["matched_scores"]["combined"] is None
    band = witness.candidates[0].sectors[0].centers[0].scales[0].bands[1]
    assert not band.available and band.gray_mean is None and band.valid_pixel_count == 0
    assert (band.mask_excluded_fraction if occlusion == "mask" else band.glare_fraction) == 1
    assert witness.candidates[0].sectors[-1].centers[0].scales[0].bands[1].available


@pytest.mark.parametrize('return_row', [155, 175])
@pytest.mark.parametrize('invert', [False, True])
def test_wide_returning_region_is_outside_local_witness_support(return_row, invert):
    """A different full crop can have exactly the same candidate witness.

    Scene names describe constructed geometry, not machine-known physical truth.
    Wider context is potentially informative, never an automatic identity rule.
    """
    step = np.full((200, 200), 180, dtype=np.uint8)
    step[100:] = 80
    returning = step.copy()
    returning[return_row:] = 180
    if invert:
        step, returning = 255-step, 255-returning
    assert not np.array_equal(step, returning)
    a, b = measure(step), measure(returning)
    ca, cb = asdict(a.candidates[0]), asdict(b.candidates[0])
    sampled_stop = max(band.clipped_local_y_range[1]
                       for sector in a.candidates[0].sectors
                       for center in sector.centers for scale in center.scales
                       for band in scale.bands)
    assert sampled_stop + 2 < return_row  # outside bands and their gradient stencil
    assert ca == cb  # includes all geometry, scales, peaks and band context
    assert experiment.score_candidate(ca) == experiment.score_candidate(cb)
    for sa, sb in zip(ca['sectors'], cb['sectors']):
        for aa, bb in zip(sa['centers'][0]['scales'], sb['centers'][0]['scales']):
            assert experiment.profile_scale(aa) == experiment.profile_scale(bb)
    assert a.candidates[0].decision == b.candidates[0].decision == 'NOT_EVALUATED'


def test_return_inside_sampled_context_is_observed_without_identity_decision():
    step = np.full((200, 200), 180, dtype=np.uint8)
    step[100:] = 80
    returning = step.copy(); returning[106:] = 180
    a, b = measure(step), measure(returning)
    assert a.candidates[0] != b.candidates[0]
    assert a.candidates[0].decision == b.candidates[0].decision == 'NOT_EVALUATED'
