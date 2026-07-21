from __future__ import annotations

from dataclasses import dataclass
import math

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind


_SOURCE_NAMES = ("sobel", "canny", "hough", "region_boundary")


@dataclass(frozen=True)
class OilCandidateCluster:
    """Immutable scalar evidence for one source-independent Y cluster."""

    representative_y: float
    spread: float
    support_count: int
    strongest_generator_score: float
    consensus_score: float
    members: tuple[tuple[str, float, float], ...]
    unrounded_representative_y: float = 0.0

    def to_candidate(self, cluster_index: int) -> BoundaryCandidate:
        supports = {source for source, _y, _score in self.members}
        features = {
            "generator_strength": float(self.strongest_generator_score),
            "raw_generator_count": float(len(self.members)),
            "unique_generator_support_count": float(self.support_count),
            "generator_support_count": float(self.support_count),
            "sobel_support": float("sobel" in supports),
            "canny_support": float("canny" in supports),
            "hough_support": float("hough" in supports),
            "region_support": float("region_boundary" in supports),
            "cluster_spread": float(self.spread),
            "representative_local_y": float(self.representative_y),
            "unrounded_representative_local_y": float(
                self.unrounded_representative_y
            ),
            "strongest_generator_score": float(self.strongest_generator_score),
            "consensus_score": float(self.consensus_score),
            "consensus_cluster_index": float(cluster_index),
        }
        return BoundaryCandidate(
            source="oil_consensus",
            kind=BoundaryKind.OIL_AIR,
            y=float(self.representative_y),
            features=features,
        )


@dataclass(frozen=True)
class OilConsensusResult:
    raw_candidates: tuple[BoundaryCandidate, ...]
    clusters: tuple[OilCandidateCluster, ...]
    consensus_candidates: tuple[BoundaryCandidate, ...]


def build_oil_candidate_consensus(
    candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...],
    tolerance_px: float,
) -> OilConsensusResult:
    """Cluster generator candidates deterministically and independently of input order."""

    tolerance = max(0.0, _finite(tolerance_px))
    raw = tuple(sorted(candidates, key=_candidate_sort_key))
    unique = _deduplicate_same_source(raw, tolerance)
    working: list[dict[str, BoundaryCandidate]] = []

    for candidate in unique:
        eligible: list[tuple[float, float, int]] = []
        for index, cluster in enumerate(working):
            if candidate.source in cluster:
                continue
            representative = _weighted_representative(tuple(cluster.values()))
            distance = abs(float(candidate.y) - representative)
            if distance <= tolerance + 1e-12:
                eligible.append((distance, representative, index))
        if eligible:
            _distance, _representative_y, target = min(eligible)
            working[target][candidate.source] = candidate
        else:
            working.append({candidate.source: candidate})

    clusters = tuple(
        sorted(
            (_make_cluster(tuple(cluster.values())) for cluster in working),
            key=lambda item: (
                item.representative_y,
                -item.support_count,
                -item.consensus_score,
                item.members,
            ),
        )
    )
    consensus = tuple(
        cluster.to_candidate(index) for index, cluster in enumerate(clusters)
    )

    membership: dict[tuple[str, float, float], tuple[int, float]] = {}
    for index, cluster in enumerate(clusters):
        for member in cluster.members:
            membership[member] = (index, cluster.representative_y)
    for candidate in raw:
        key = _member_key(candidate)
        match = membership.get(key)
        if match is None:
            source_matches = [
                (abs(float(candidate.y) - cluster.representative_y), index, cluster)
                for index, cluster in enumerate(clusters)
                if any(
                    source == candidate.source
                    for source, _y, _score in cluster.members
                )
            ]
            if source_matches:
                distance, index, cluster = min(source_matches)
                if distance <= tolerance + 1e-12:
                    match = (index, cluster.representative_y)
        if match is not None:
            candidate.features["consensus_cluster_index"] = float(match[0])
            candidate.features["consensus_representative_local_y"] = float(
                match[1]
            )
            candidate.features["consensus_member"] = 1.0
        else:
            candidate.features["consensus_cluster_index"] = -1.0
            candidate.features["consensus_member"] = 0.0

    return OilConsensusResult(raw, clusters, consensus)


def _deduplicate_same_source(
    candidates: tuple[BoundaryCandidate, ...], tolerance: float
) -> tuple[BoundaryCandidate, ...]:
    by_source: dict[str, list[BoundaryCandidate]] = {}
    for candidate in candidates:
        by_source.setdefault(candidate.source, []).append(candidate)
    kept: list[BoundaryCandidate] = []
    for source in sorted(by_source):
        ordered = sorted(
            by_source[source],
            key=lambda candidate: (
                -_strength(candidate),
                float(candidate.y),
                candidate.kind.value,
            ),
        )
        source_kept: list[BoundaryCandidate] = []
        for candidate in ordered:
            if all(
                abs(float(candidate.y) - float(prior.y)) > tolerance + 1e-12
                for prior in source_kept
            ):
                source_kept.append(candidate)
        kept.extend(source_kept)
    return tuple(sorted(kept, key=_candidate_sort_key))


def _make_cluster(
    candidates: tuple[BoundaryCandidate, ...],
) -> OilCandidateCluster:
    ordered = tuple(sorted(candidates, key=_candidate_sort_key))
    unrounded = _weighted_representative(ordered)
    representative = float(round(unrounded))
    ys = [float(candidate.y) for candidate in ordered]
    strengths = [_strength(candidate) for candidate in ordered]
    support = len({candidate.source for candidate in ordered})
    strongest = max(strengths, default=0.0)
    average = sum(strengths) / max(1, len(strengths))
    diversity = min(1.0, support / max(1, len(_SOURCE_NAMES)))
    consensus = min(1.0, 0.62 * diversity + 0.38 * average)
    members = tuple(_member_key(candidate) for candidate in ordered)
    return OilCandidateCluster(
        representative_y=representative,
        spread=max(ys) - min(ys) if ys else 0.0,
        support_count=support,
        strongest_generator_score=strongest,
        consensus_score=consensus,
        members=members,
        unrounded_representative_y=unrounded,
    )


def _weighted_representative(
    candidates: tuple[BoundaryCandidate, ...],
) -> float:
    weighted = [(_strength(candidate), float(candidate.y)) for candidate in candidates]
    total = sum(max(0.05, strength) for strength, _y in weighted)
    if total <= 0.0:
        return 0.0
    return sum(max(0.05, strength) * y for strength, y in weighted) / total


def _candidate_sort_key(
    candidate: BoundaryCandidate,
) -> tuple[float, str, float, str]:
    return (
        float(candidate.y),
        str(candidate.source),
        -_strength(candidate),
        candidate.kind.value,
    )


def _member_key(candidate: BoundaryCandidate) -> tuple[str, float, float]:
    return (str(candidate.source), float(candidate.y), _strength(candidate))


def _strength(candidate: BoundaryCandidate) -> float:
    value = candidate.features.get("generator_strength", 0.0)
    return min(1.0, max(0.0, _finite(value)))


def _finite(value: float) -> float:
    number = float(value)
    return number if math.isfinite(number) else 0.0
