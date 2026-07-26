from __future__ import annotations

from itertools import permutations

import pytest

from oil_tracker.adapters.vision.oil_candidate_consensus import build_oil_candidate_consensus
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


def candidate(
    source: str,
    y: float,
    strength: float,
    *,
    signed_region: float | None = None,
) -> BoundaryCandidate:
    features = {"generator_strength": strength}
    if signed_region is not None:
        features.update(
            {
                "generator_region_available": 1.0,
                "generator_signed_region_contrast": signed_region,
            }
        )
    return BoundaryCandidate(
        source,
        BoundaryKind.OIL_AIR,
        y,
        features,
    )


def signature(values):
    result = build_oil_candidate_consensus(values, 3.0)
    return tuple(
        (
            round(cluster.representative_y, 6),
            round(cluster.spread, 6),
            cluster.support_count,
            tuple(source for source, _y, _score in cluster.members),
        )
        for cluster in result.clusters
    )


def test_multi_generator_cluster_records_support_and_weighted_y():
    result = build_oil_candidate_consensus(
        [
            candidate("sobel", 20.0, 1.0),
            candidate("canny", 22.0, 0.5),
            candidate("hough", 21.0, 0.8),
            candidate("region_boundary", 20.5, 0.6),
        ],
        3.0,
    )
    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    assert cluster.support_count == 4
    assert cluster.spread == pytest.approx(2.0)
    assert 20.0 <= cluster.representative_y <= 22.0
    consensus = result.consensus_candidates[0]
    assert consensus.features["sobel_support"] == 1.0
    assert consensus.features["canny_support"] == 1.0
    assert consensus.features["hough_support"] == 1.0
    assert consensus.features["region_support"] == 1.0
    assert consensus.features["generator_support_count"] == 4.0


def test_same_source_duplicates_do_not_inflate_support():
    result = build_oil_candidate_consensus(
        [
            candidate("sobel", 20.0, 0.9),
            candidate("sobel", 21.0, 0.3),
            candidate("canny", 20.5, 0.7),
        ],
        3.0,
    )
    assert len(result.clusters) == 1
    assert result.clusters[0].support_count == 2
    assert len(result.clusters[0].members) == 2
    assert sum(item.features["consensus_member"] for item in result.raw_candidates) == 3.0


def test_opposite_region_edges_preserve_nearby_same_source_clusters():
    values = [
        candidate("canny", 20.0, 1.0),
        candidate("canny", 24.0, 1.0),
        candidate("hough", 20.0, 0.8),
        candidate("hough", 24.0, 0.8),
        candidate("sobel", 20.0, 1.0),
        candidate("sobel", 24.0, 1.0),
        candidate("region_boundary", 21.0, 0.4, signed_region=-0.4),
        candidate("region_boundary", 25.0, 0.4, signed_region=0.4),
    ]
    forward = build_oil_candidate_consensus(values, 4.0)
    reverse = build_oil_candidate_consensus(list(reversed(values)), 4.0)
    assert len(forward.clusters) == 2
    assert [cluster.members for cluster in forward.clusters] == [
        cluster.members for cluster in reverse.clusters
    ]
    assert [cluster.support_count for cluster in forward.clusters] == [4, 4]
    assert max(member[1] for member in forward.clusters[0].members) <= 21.0
    assert min(member[1] for member in forward.clusters[1].members) >= 24.0
    assert forward.clusters[0].signed_region_evidence < 0.0
    assert forward.clusters[1].signed_region_evidence > 0.0
    assert sum(item.features["consensus_member"] for item in forward.raw_candidates) == 8.0


def test_tolerance_boundary_and_multiple_clusters_are_deterministic():
    values = [
        candidate("sobel", 10.0, 0.8),
        candidate("canny", 13.0, 0.7),
        candidate("hough", 24.0, 0.9),
        candidate("region_boundary", 26.9, 0.5),
    ]
    expected = signature(values)
    assert len(expected) == 2
    for order in permutations(values):
        assert signature(list(order)) == expected


def test_polarity_correction_applies_only_inside_member_envelope():
    values = [
        candidate("sobel", 20.0, 1.0),
        candidate("canny", 22.0, 0.8),
        candidate("region_boundary", 21.0, 0.8, signed_region=0.20),
    ]
    expected = None
    for order in permutations(values):
        result = build_oil_candidate_consensus(list(order), 3.0)
        cluster = result.clusters[0]
        consensus = result.consensus_candidates[0]
        current = (
            cluster.representative_y,
            cluster.unrounded_representative_y,
            cluster.signed_region_evidence,
            cluster.edge_center_correction_px,
            cluster.edge_center_correction_deferred,
            consensus.features["representative_local_y"],
            consensus.features["polarity_edge_center_correction_px"],
            consensus.features["polarity_edge_center_correction_deferred"],
        )
        expected = current if expected is None else expected
        assert current == pytest.approx(expected)
    assert expected is not None
    assert expected[0] == 20.0
    assert expected[3] == -1.0
    assert expected[4] == 0.0


def test_polarity_correction_outside_envelope_is_deferred_in_debug_features():
    result = build_oil_candidate_consensus(
        [
            candidate("sobel", 20.0, 0.9),
            candidate("canny", 20.0, 0.8),
            candidate("region_boundary", 20.0, 0.7, signed_region=0.20),
        ],
        2.0,
    )
    cluster = result.clusters[0]
    consensus = result.consensus_candidates[0]
    assert cluster.representative_y == 20.0
    assert cluster.edge_center_correction_px == 0.0
    assert cluster.edge_center_correction_deferred == 1.0
    assert consensus.features["polarity_edge_center_correction_px"] == 0.0
    assert consensus.features["polarity_edge_center_correction_deferred"] == 1.0


def test_polarity_correction_requires_multi_source_and_threshold_evidence():
    single = build_oil_candidate_consensus(
        [candidate("region_boundary", 20.0, 0.8, signed_region=0.40)],
        2.0,
    ).clusters[0]
    weak = build_oil_candidate_consensus(
        [
            candidate("sobel", 20.0, 0.9),
            candidate("region_boundary", 21.0, 0.8, signed_region=0.049),
        ],
        2.0,
    ).clusters[0]
    absent = build_oil_candidate_consensus(
        [candidate("sobel", 20.0, 0.9), candidate("canny", 21.0, 0.8)],
        2.0,
    ).clusters[0]
    assert single.edge_center_correction_px == 0.0
    assert weak.edge_center_correction_px == 0.0
    assert absent.edge_center_correction_px == 0.0
    assert weak.edge_center_correction_deferred == 0.0
    assert absent.edge_center_correction_deferred == 0.0


def test_single_source_candidate_is_retained_but_has_no_false_consensus():
    result = build_oil_candidate_consensus([candidate("sobel", 18.0, 0.75)], 2.0)
    consensus = result.consensus_candidates[0]
    assert consensus.features["unique_generator_support_count"] == 1.0
    assert consensus.features["consensus_score"] < 0.75
    assert consensus.features["polarity_edge_center_correction_px"] == 0.0
