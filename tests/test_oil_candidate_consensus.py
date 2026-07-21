from __future__ import annotations

from itertools import permutations

import pytest

from oil_tracker.adapters.vision.oil_candidate_consensus import build_oil_candidate_consensus
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


def candidate(source: str, y: float, strength: float) -> BoundaryCandidate:
    return BoundaryCandidate(
        source,
        BoundaryKind.OIL_AIR,
        y,
        {"generator_strength": strength},
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


def test_single_source_candidate_is_retained_but_has_no_false_consensus():
    result = build_oil_candidate_consensus([candidate("sobel", 18.0, 0.75)], 2.0)
    consensus = result.consensus_candidates[0]
    assert consensus.features["unique_generator_support_count"] == 1.0
    assert consensus.features["consensus_score"] < 0.75
