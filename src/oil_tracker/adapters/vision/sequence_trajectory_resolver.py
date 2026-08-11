from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Iterable, Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig


SEQUENCE_RESOLVER_VERSION = "r5-sequence-first-observation-v1"

_OIL_REPLACED_FLAGS = {
    "LOW_CONFIDENCE",
    "OIL_EVIDENCE_AMBIGUOUS",
    "OIL_PIPELINE_UNAVAILABLE",
    "OIL_REACQUISITION_PENDING",
}
_HARD_UNAVAILABLE_FLAGS = {
    "DETECTION_FAILED",
    "DETECTION_LOST",
    "FOGGED_OR_GLARE",
    "FRAME_UNAVAILABLE",
    "OIL_PIPELINE_FAILURE",
    "OIL_PIPELINE_UNAVAILABLE",
    "REDETECTION_SAMPLE_FAILED",
    "UNAVAILABLE",
}


@dataclass(frozen=True)
class SequenceResolverConfig:
    """Bounded, detector-independent costs for the final-analysis lattice."""

    hard_conflict_limit: float = 0.78
    entrance_band_ratio: float = 0.27
    recurring_track_min_frames: int = 6
    recurring_track_min_ratio: float = 0.18
    recurring_track_tolerance_ratio: float = 0.018
    direct_anchor_min_material: float = 0.24
    direct_anchor_max_artifact: float = 0.31
    state_entry_min_evidence: float = 0.30
    black_frame_max_mean: float = 2.0
    black_frame_max_std: float = 2.0
    black_frame_max_dynamic_range: float = 4.0
    unknown_transition_cost: float = 0.24
    state_transition_cost: float = 0.10
    incompatible_state_transition_cost: float = 3.0


@dataclass(frozen=True)
class SequenceResolutionDiagnostics:
    version: str
    frame_count: int
    oil_frame_count: int
    full_frame_count: int
    empty_frame_count: int
    unknown_frame_count: int
    recurring_track_count: int
    maximum_track_opposition: float
    foam_raw_candidate_count: int = 0
    foam_confirmed_frame_count: int = 0
    foam_bridged_frame_count: int = 0
    foam_episode_count: int = 0
    foam_rejected_static_episode_count: int = 0
    foam_rejected_unconfirmed_episode_count: int = 0


@dataclass(frozen=True)
class SequenceResolution:
    detections: tuple[PhaseDetection, ...]
    diagnostics: SequenceResolutionDiagnostics


@dataclass(frozen=True)
class _CandidateRef:
    frame_offset: int
    candidate_offset: int
    candidate: BoundaryCandidate
    local_quality: float
    direct_anchor: bool = False
    anchor_support: float = 0.0
    track_opposition: float = 0.0


@dataclass(frozen=True)
class _Node:
    kind: str
    emission: float
    identity: str
    candidate_ref: _CandidateRef | None = None
    state_evidence: float = 0.0

    @property
    def y(self) -> float | None:
        if self.candidate_ref is None:
            return None
        return float(self.candidate_ref.candidate.y)


class SequenceTrajectoryResolver:
    """Choose one physically coherent state/candidate path for a completed window.

    Numeric output is always copied from a candidate in the same frame.  FULL,
    EMPTY and UNKNOWN nodes never carry a coordinate.
    """

    version = SEQUENCE_RESOLVER_VERSION

    def __init__(self, config: SequenceResolverConfig | None = None) -> None:
        self.config = config or SequenceResolverConfig()

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> SequenceResolution:
        source = tuple(detections)
        if not source:
            return SequenceResolution(
                (),
                SequenceResolutionDiagnostics(
                    self.version,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0.0,
                ),
            )
        refs_by_frame = self._candidate_refs(source, glass)
        refs_by_frame = self._apply_anchor_support(refs_by_frame, glass)
        refs_by_frame, track_count, maximum_track_opposition = self._apply_track_opposition(
            refs_by_frame,
            glass,
        )
        layers = tuple(
            self._nodes_for_frame(
                detection,
                refs_by_frame[index],
                glass,
                confirmed_initial_state,
            )
            for index, detection in enumerate(source)
        )
        path = self._best_path(layers, source, glass, confirmed_initial_state)
        path = self._bound_unanchored_oil_run_edges(path, layers, glass)
        resolved = tuple(
            self._project_detection(
                detection,
                node,
                path,
                index,
                glass,
                confirmed_initial_state,
            )
            for index, (detection, node) in enumerate(zip(source, path, strict=True))
        )
        counts = {kind: sum(node.kind == kind for node in path) for kind in ("oil", "full", "empty", "unknown")}
        return SequenceResolution(
            resolved,
            SequenceResolutionDiagnostics(
                version=self.version,
                frame_count=len(resolved),
                oil_frame_count=counts["oil"],
                full_frame_count=counts["full"],
                empty_frame_count=counts["empty"],
                unknown_frame_count=counts["unknown"],
                recurring_track_count=track_count,
                maximum_track_opposition=maximum_track_opposition,
            ),
        )

    def _candidate_refs(
        self,
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[_CandidateRef, ...], ...]:
        limit = max(1, int(glass.detector_settings.candidate_top_k))
        rows: list[tuple[_CandidateRef, ...]] = []
        for frame_offset, detection in enumerate(detections):
            refs: list[_CandidateRef] = []
            for candidate_offset, candidate in enumerate(detection.candidates):
                if candidate.kind is not BoundaryKind.OIL_AIR or not _finite(candidate.y):
                    continue
                if self._hard_candidate_conflict(candidate):
                    continue
                material = _candidate_material_support(candidate)
                artifact = _candidate_artifact_signature(candidate)
                direct_anchor = bool(
                    candidate.selected
                    and detection.fill_state is not FillState.FULL_WITH_FOAM
                    and material >= self.config.direct_anchor_min_material
                    and artifact <= self.config.direct_anchor_max_artifact
                )
                refs.append(
                    _CandidateRef(
                        frame_offset,
                        candidate_offset,
                        candidate,
                        _candidate_quality(candidate)
                        + (0.42 if direct_anchor else 0.0),
                        direct_anchor=direct_anchor,
                    )
                )
            refs.sort(
                key=lambda item: (
                    -item.local_quality,
                    float(item.candidate.y),
                    item.candidate.source,
                )
            )
            rows.append(tuple(refs[:limit]))
        return tuple(rows)

    def _apply_anchor_support(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[_CandidateRef, ...], ...]:
        direct_anchors = tuple(
            ref
            for refs in refs_by_frame
            for ref in refs
            if ref.direct_anchor
        )
        horizon = max(
            2,
            min(3, int(glass.detector_settings.oil_path_window)),
        )
        maximum_jump = max(
            1.0,
            float(glass.detector_settings.temporal_max_jump_px),
        )
        qualified_keys = _qualified_anchor_keys(
            direct_anchors,
            frame_count=len(refs_by_frame),
            horizon=horizon,
            maximum_jump=maximum_jump,
        )
        anchors = tuple(
            ref
            for ref in direct_anchors
            if (ref.frame_offset, ref.candidate_offset) in qualified_keys
        )
        output: list[tuple[_CandidateRef, ...]] = []
        for refs in refs_by_frame:
            rows: list[_CandidateRef] = []
            for ref in refs:
                if (ref.frame_offset, ref.candidate_offset) in qualified_keys:
                    support = 1.0
                else:
                    support = 0.0
                    for anchor in anchors:
                        gap = abs(anchor.frame_offset - ref.frame_offset)
                        if gap == 0 or gap > horizon:
                            continue
                        allowed = maximum_jump * gap * 0.65
                        distance = abs(
                            float(anchor.candidate.y) - float(ref.candidate.y)
                        )
                        support = max(
                            support,
                            _unit(1.0 - distance / max(1.0, allowed)),
                        )
                rows.append(replace(ref, anchor_support=support))
            output.append(tuple(rows))
        return tuple(output)

    def _hard_candidate_conflict(self, candidate: BoundaryCandidate) -> bool:
        features = candidate.features
        penalties = candidate.penalties
        availability = _unit(features.get("evidence_availability", 1.0))
        visibility = _unit(features.get("visibility", 1.0))
        conflicts = (
            _unit(penalties.get("glare_conflict", penalties.get("glare_penalty", 0.0))),
            _unit(penalties.get("exclusion_conflict", penalties.get("exclusion_penalty", 0.0))),
            _unit(penalties.get("border_penalty", 0.0)),
        )
        return (
            availability < 0.20
            or visibility < 0.20
            or max(conflicts, default=0.0) >= self.config.hard_conflict_limit
        )

    def _apply_track_opposition(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[tuple[_CandidateRef, ...], ...], int, float]:
        frame_count = len(refs_by_frame)
        height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
        tolerance = max(3.0, height * self.config.recurring_track_tolerance_ratio)
        buckets: dict[int, list[_CandidateRef]] = {}
        for refs in refs_by_frame:
            for ref in refs:
                bucket = int(round(float(ref.candidate.y) / tolerance))
                buckets.setdefault(bucket, []).append(ref)

        penalties: dict[tuple[int, int], float] = {}
        recurring = 0
        maximum = 0.0
        for refs in buckets.values():
            best_by_frame: dict[int, _CandidateRef] = {}
            for ref in refs:
                prior = best_by_frame.get(ref.frame_offset)
                if prior is None or ref.local_quality > prior.local_quality:
                    best_by_frame[ref.frame_offset] = ref
            ordered = tuple(best_by_frame[index] for index in sorted(best_by_frame))
            presence_ratio = len(ordered) / max(1, frame_count)
            longest_run = _longest_consecutive(tuple(item.frame_offset for item in ordered))
            if (
                len(ordered) < self.config.recurring_track_min_frames
                or presence_ratio < self.config.recurring_track_min_ratio
                or longest_run < self.config.recurring_track_min_frames
            ):
                continue
            ys = tuple(float(item.candidate.y) for item in ordered)
            mean_y = sum(ys) / len(ys)
            variance = sum((value - mean_y) ** 2 for value in ys) / len(ys)
            stability = max(0.0, 1.0 - math.sqrt(variance) / max(1.0, tolerance * 1.5))
            if stability <= 0.0:
                continue
            opposition = sum(_candidate_artifact_signature(item.candidate) for item in ordered) / len(ordered)
            material = sum(_candidate_material_support(item.candidate) for item in ordered) / len(ordered)
            contradiction = max(0.0, opposition - 0.35 * material - 0.04)
            recurrence = _unit(
                (presence_ratio - self.config.recurring_track_min_ratio)
                / max(0.01, 0.70 - self.config.recurring_track_min_ratio)
            )
            track_penalty = _unit(
                recurrence
                * stability
                * (0.22 + contradiction * 2.4)
            )
            if track_penalty <= 0.0:
                continue
            recurring += 1
            maximum = max(maximum, track_penalty)
            for item in refs:
                penalties[(item.frame_offset, item.candidate_offset)] = (
                    track_penalty * (1.0 - 0.70 * item.anchor_support)
                )

        output = tuple(
            tuple(
                replace(
                    ref,
                    track_opposition=penalties.get(
                        (ref.frame_offset, ref.candidate_offset),
                        0.0,
                    ),
                )
                for ref in refs
            )
            for refs in refs_by_frame
        )
        return output, recurring, maximum

    def _nodes_for_frame(
        self,
        detection: PhaseDetection,
        refs: tuple[_CandidateRef, ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> tuple[_Node, ...]:
        if _hard_unavailable(detection, self.config):
            return (_Node("unknown", 1.25, "unknown"),)

        oil_nodes = tuple(
            _Node(
                "oil",
                _oil_emission(ref),
                f"oil:{ref.candidate.source}:{ref.candidate.y:.6f}",
                ref,
            )
            for ref in refs
        )
        full_strength = _state_evidence(detection, FillState.FULL_NO_INTERFACE)
        empty_strength = _state_evidence(detection, FillState.EMPTY_NO_INTERFACE)
        prior_full = confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE
        prior_empty = confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE
        generic_no_interface = _unit(
            detection.debug_metrics.get("oil_no_interface_score", 0.0)
        )
        full_emission = (
            -0.10
            + 0.85 * full_strength
            + 0.24 * generic_no_interface
        )
        empty_emission = (
            -0.10
            + 0.85 * empty_strength
            + 0.24 * generic_no_interface
        )
        best_quality = max((ref.local_quality for ref in refs), default=0.0)
        ambiguity = _unit(detection.debug_metrics.get("oil_ambiguity_score", 0.0))
        no_interface = _unit(detection.debug_metrics.get("oil_no_interface_score", 0.0))
        unknown_emission = 0.10 + 0.30 * ambiguity + 0.12 * no_interface - 0.10 * best_quality
        if prior_full:
            full_emission = max(full_emission, unknown_emission)
        if prior_empty:
            empty_emission = max(empty_emission, unknown_emission)
        return (
            *oil_nodes,
            _Node(
                "full",
                full_emission,
                "full",
                state_evidence=max(full_strength, generic_no_interface),
            ),
            _Node(
                "empty",
                empty_emission,
                "empty",
                state_evidence=max(empty_strength, generic_no_interface),
            ),
            _Node("unknown", unknown_emission, "unknown"),
        )

    def _best_path(
        self,
        layers: tuple[tuple[_Node, ...], ...],
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> tuple[_Node, ...]:
        scores: list[list[float]] = []
        backpointers: list[list[int]] = []
        first_scores = [
            node.emission + _initial_score(node, glass, confirmed_initial_state)
            for node in layers[0]
        ]
        scores.append(first_scores)
        backpointers.append([-1] * len(first_scores))
        for frame_offset in range(1, len(layers)):
            prior_layer = layers[frame_offset - 1]
            current_layer = layers[frame_offset]
            dt = max(
                1e-6,
                float(detections[frame_offset].time_sec)
                - float(detections[frame_offset - 1].time_sec),
            )
            current_scores: list[float] = []
            current_backpointers: list[int] = []
            for node in current_layer:
                choices = tuple(
                    (
                        scores[-1][prior_offset]
                        + self._transition_score(
                            prior,
                            node,
                            glass,
                            dt,
                            confirmed_initial_state,
                        ),
                        prior_offset,
                    )
                    for prior_offset, prior in enumerate(prior_layer)
                )
                best_score, best_offset = max(
                    choices,
                    key=lambda item: (
                        item[0],
                        -_node_order(prior_layer[item[1]]),
                    ),
                )
                current_scores.append(best_score + node.emission)
                current_backpointers.append(best_offset)
            scores.append(current_scores)
            backpointers.append(current_backpointers)

        last_offset = max(
            range(len(layers[-1])),
            key=lambda index: (scores[-1][index], -_node_order(layers[-1][index])),
        )
        offsets = [last_offset]
        for frame_offset in range(len(layers) - 1, 0, -1):
            offsets.append(backpointers[frame_offset][offsets[-1]])
        offsets.reverse()
        return tuple(layers[index][offset] for index, offset in enumerate(offsets))

    def _bound_unanchored_oil_run_edges(
        self,
        path: tuple[_Node, ...],
        layers: tuple[tuple[_Node, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[_Node, ...]:
        bounded = list(path)
        horizon = max(2, min(3, int(glass.detector_settings.oil_path_window)))
        offset = 0
        while offset < len(path):
            if path[offset].kind != "oil":
                offset += 1
                continue
            start = offset
            while offset + 1 < len(path) and path[offset + 1].kind == "oil":
                offset += 1
            end = offset
            qualified = [
                index
                for index in range(start, end + 1)
                if path[index].candidate_ref is not None
                and path[index].candidate_ref.direct_anchor
                and path[index].candidate_ref.anchor_support >= 0.99
            ]
            if qualified:
                prior_kind = path[start - 1].kind if start > 0 else None
                next_node = path[end + 1] if end + 1 < len(path) else None
                if prior_kind not in {"full", "empty"}:
                    for index in range(start, max(start, qualified[0] - horizon)):
                        bounded[index] = _unknown_node(layers[index])
                for prior_anchor, next_anchor in zip(qualified, qualified[1:]):
                    if next_anchor - prior_anchor <= horizon * 2:
                        continue
                    for index in range(prior_anchor + 1, next_anchor):
                        bounded[index] = _unknown_node(layers[index])
                supported_state_entry = bool(
                    next_node is not None
                    and next_node.kind in {"full", "empty"}
                    and next_node.state_evidence >= self.config.state_entry_min_evidence
                )
                if not supported_state_entry:
                    trailing_start = min(end + 1, qualified[-1] + horizon + 1)
                    for index in range(trailing_start, end + 1):
                        bounded[index] = _unknown_node(layers[index])
            offset += 1
        return tuple(bounded)

    def _transition_score(
        self,
        prior: _Node,
        current: _Node,
        glass: GlassInspectionConfig,
        dt: float,
        confirmed_initial_state: InitialObservationState | None,
    ) -> float:
        if prior.kind == current.kind:
            if current.kind == "oil":
                assert prior.y is not None and current.y is not None
                maximum = max(1.0, float(glass.detector_settings.temporal_max_jump_px))
                time_scale = max(1.0, dt / 0.5)
                normalized = abs(current.y - prior.y) / (maximum * time_scale)
                return 0.22 - (0.12 * normalized + 0.30 * normalized * normalized)
            if current.kind in {"full", "empty"}:
                confirmed_kind = (
                    "full"
                    if confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE
                    else "empty"
                    if confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE
                    else None
                )
                if current.kind == confirmed_kind:
                    return 0.22
                return 0.35
            return 0.02

        if prior.kind == "unknown" or current.kind == "unknown":
            if (
                prior.kind == "unknown"
                and current.kind in {"full", "empty"}
                and current.state_evidence < 0.58
            ):
                return -1_000_000.0
            return -self.config.unknown_transition_cost
        if prior.kind in {"full", "empty"} and current.kind in {"full", "empty"}:
            return -self.config.incompatible_state_transition_cost
        if prior.kind == "oil" and current.kind in {"full", "empty"}:
            if (
                prior.candidate_ref is None
                or prior.candidate_ref.anchor_support < 0.45
                or current.state_evidence < self.config.state_entry_min_evidence
            ):
                return -self.config.incompatible_state_transition_cost
            return -self._edge_transition_cost(prior, current.kind, glass)
        if current.kind == "oil" and prior.kind in {"full", "empty"}:
            cost = self._edge_transition_cost(current, prior.kind, glass)
            return 0.18 if cost <= self.config.state_transition_cost else -cost
        return -self.config.state_transition_cost

    def _edge_transition_cost(
        self,
        oil_node: _Node,
        state_kind: str,
        glass: GlassInspectionConfig,
    ) -> float:
        assert oil_node.y is not None
        relative = _relative_y(oil_node.y, glass)
        band = self.config.entrance_band_ratio
        if state_kind == "full":
            overflow = max(0.0, relative - band)
        else:
            overflow = max(0.0, (1.0 - band) - relative)
        if overflow <= 0.0:
            return self.config.state_transition_cost * 0.50
        return 0.80 + 3.0 * overflow

    def _project_detection(
        self,
        detection: PhaseDetection,
        node: _Node,
        path: tuple[_Node, ...],
        frame_offset: int,
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None,
    ) -> PhaseDetection:
        flags = [flag for flag in detection.flags if flag not in _OIL_REPLACED_FLAGS]
        candidates = _project_candidates(detection.candidates, node.candidate_ref)
        debug_metrics = dict(detection.debug_metrics)
        debug_metrics.update(
            {
                "sequence_resolver_version": self.version,
                "sequence_resolved_kind": node.kind,
                "sequence_resolved_source_y": node.y,
                "sequence_emission": float(node.emission),
                "sequence_track_opposition": (
                    0.0
                    if node.candidate_ref is None
                        else float(node.candidate_ref.track_opposition)
                ),
                "sequence_anchor_support": (
                    0.0
                    if node.candidate_ref is None
                    else float(node.candidate_ref.anchor_support)
                ),
            }
        )
        if node.kind == "oil":
            assert node.y is not None and node.candidate_ref is not None
            y = float(node.y)
            zero = glass.geometry.zero_line_y
            px = None if zero is None else float(zero) - y
            mm = None if px is None or glass.mm_per_pixel is None else px * glass.mm_per_pixel
            confidence = _sequence_oil_confidence(node.candidate_ref)
            state = _visible_state(path, frame_offset)
            flags.extend(("SEQUENCE_RESOLVED_OIL", "SEQUENCE_SAME_FRAME_CANDIDATE"))
            return replace(
                detection,
                fill_state=state,
                oil_air_level_y=y,
                oil_air_level_px_from_zero=px,
                oil_air_level_mm_from_zero=mm,
                oil_air_confidence=confidence,
                overall_confidence=max(confidence, detection.visibility_confidence * 0.55),
                raw_oil_air_level_y=y,
                smoothed_oil_air_level_y=y,
                candidates=candidates,
                flags=sorted(set(flags)),
                debug_metrics=debug_metrics,
            )
        if node.kind in {"full", "empty"}:
            state = (
                FillState.FULL_NO_INTERFACE
                if node.kind == "full"
                else FillState.EMPTY_NO_INTERFACE
            )
            flags.append("SEQUENCE_RESOLVED_STATE")
            prior = (
                InitialObservationState.FULL_NO_INTERFACE
                if node.kind == "full"
                else InitialObservationState.EMPTY_NO_INTERFACE
            )
            if confirmed_initial_state is prior and _state_evidence(detection, state) <= 0.0:
                flags.append("SEQUENCE_INITIAL_STATE_PRIOR")
            confidence = max(
                0.48,
                0.58 + 0.30 * _state_evidence(detection, state),
            )
            return replace(
                detection,
                fill_state=state,
                oil_air_level_y=None,
                oil_air_level_px_from_zero=None,
                oil_air_level_mm_from_zero=None,
                oil_air_confidence=0.0,
                overall_confidence=confidence,
                raw_oil_air_level_y=None,
                smoothed_oil_air_level_y=None,
                candidates=candidates,
                flags=sorted(set(flags)),
                debug_metrics=debug_metrics,
            )
        flags.append("SEQUENCE_UNAVAILABLE")
        return replace(
            detection,
            fill_state=FillState.UNKNOWN_REVIEW,
            oil_air_level_y=None,
            oil_air_level_px_from_zero=None,
            oil_air_level_mm_from_zero=None,
            oil_air_confidence=0.0,
            overall_confidence=min(detection.overall_confidence, 0.40),
            raw_oil_air_level_y=None,
            smoothed_oil_air_level_y=None,
            candidates=candidates,
            flags=sorted(set(flags)),
            debug_metrics=debug_metrics,
        )


def _candidate_material_support(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    return _unit(
        0.38 * _unit(features.get("boundary_likelihood", candidate.feature_score))
        + 0.20 * _unit(features.get("broad_strength", features.get("region_contrast", 0.0)))
        + 0.16 * _unit(features.get("narrow_peak_strength", features.get("edge_strength", 0.0)))
        + 0.14 * _unit(features.get("narrow_horizontal_coverage", features.get("horizontal_coverage", 0.0)))
        + 0.07 * _unit(features.get("broad_scale_consistency", 0.0))
        + 0.05 * _unit(features.get("polarity_confidence", 0.0))
    )


def _candidate_artifact_signature(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    penalties = candidate.penalties
    return _unit(
        0.42 * _unit(features.get("artifact_likelihood", penalties.get("artifact_likelihood", 0.0)))
        + 0.18 * _unit(features.get("static_prior_contribution", penalties.get("static_artifact_penalty", 0.0)))
        + 0.16 * _unit(penalties.get("glare_conflict", penalties.get("glare_penalty", 0.0)))
        + 0.14 * _unit(penalties.get("border_penalty", 0.0))
        + 0.10 * _unit(penalties.get("exclusion_conflict", penalties.get("exclusion_penalty", 0.0)))
    )


def _candidate_quality(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    material = _candidate_material_support(candidate)
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    ambiguity = _unit(features.get("ambiguity_likelihood", candidate.penalties.get("ambiguity_likelihood", 0.0)))
    artifact = _candidate_artifact_signature(candidate)
    return 0.62 * material + 0.18 * availability - 0.12 * ambiguity - 0.22 * artifact


def _oil_emission(ref: _CandidateRef) -> float:
    candidate = ref.candidate
    features = candidate.features
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    ambiguity = _unit(features.get("ambiguity_likelihood", candidate.penalties.get("ambiguity_likelihood", 0.0)))
    return (
        -0.20
        + 0.65 * _candidate_material_support(candidate)
        + 0.10 * availability
        + (0.42 if ref.direct_anchor else 0.0)
        + 0.50 * ref.anchor_support
        - 0.70 * _candidate_artifact_signature(candidate)
        - 0.18 * ambiguity
        - 0.72 * ref.track_opposition
    )


def _sequence_oil_confidence(ref: _CandidateRef) -> float:
    return min(
        0.95,
        max(
            0.44,
            0.46
            + 0.48 * _candidate_material_support(ref.candidate)
            - 0.18 * _candidate_artifact_signature(ref.candidate)
            - 0.20 * ref.track_opposition,
        ),
    )


def _state_evidence(detection: PhaseDetection, state: FillState) -> float:
    key = (
        "oil_no_interface_full_likelihood"
        if state is FillState.FULL_NO_INTERFACE
        else "oil_no_interface_empty_likelihood"
    )
    value = _unit(detection.debug_metrics.get(key, 0.0))
    if detection.fill_state is state:
        value = max(value, 0.82)
    return value


def _initial_score(
    node: _Node,
    glass: GlassInspectionConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> float:
    if confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE:
        if node.kind == "full":
            return 1.60
        if node.kind == "empty":
            return -2.0
        if node.kind == "oil" and node.y is not None:
            return 0.25 if _relative_y(node.y, glass) <= 0.27 else -0.75
    if confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE:
        if node.kind == "empty":
            return 1.60
        if node.kind == "full":
            return -2.0
        if node.kind == "oil" and node.y is not None:
            return 0.25 if _relative_y(node.y, glass) >= 0.73 else -0.75
    if node.kind in {"full", "empty"}:
        return 0.0 if node.state_evidence >= 0.58 else -1_000_000.0
    return 0.0


def _visible_state(path: tuple[_Node, ...], index: int) -> FillState:
    prior_y = next((path[offset].y for offset in range(index - 1, max(-1, index - 4), -1) if path[offset].kind == "oil"), None)
    next_y = next((path[offset].y for offset in range(index + 1, min(len(path), index + 4)) if path[offset].kind == "oil"), None)
    current_y = path[index].y
    assert current_y is not None
    reference_delta = 0.0
    if prior_y is not None and next_y is not None:
        reference_delta = next_y - prior_y
    elif prior_y is not None:
        reference_delta = current_y - prior_y
    elif next_y is not None:
        reference_delta = next_y - current_y
    if reference_delta < -2.0:
        return FillState.FILLING_VISIBLE
    if reference_delta > 2.0:
        return FillState.DRAINING_VISIBLE
    return FillState.PARTIAL_VISIBLE


def _project_candidates(
    candidates: Iterable[BoundaryCandidate],
    selected_ref: _CandidateRef | None,
) -> list[BoundaryCandidate]:
    output: list[BoundaryCandidate] = []
    for offset, candidate in enumerate(candidates):
        selected = selected_ref is not None and offset == selected_ref.candidate_offset
        output.append(
            replace(
                candidate,
                selected=selected,
                rejected=not selected,
                reject_reason=(
                    ""
                    if selected
                    else (
                        candidate.reject_reason
                        or "not_selected_by_sequence_resolver"
                    )
                ),
            )
        )
    return output


def _hard_unavailable(
    detection: PhaseDetection,
    config: SequenceResolverConfig,
) -> bool:
    flags = {str(flag).strip().upper() for flag in detection.flags}
    if flags.intersection(_HARD_UNAVAILABLE_FLAGS):
        return True
    mean = _optional_finite(detection.debug_metrics.get("effective_gray_mean"))
    standard_deviation = _optional_finite(
        detection.debug_metrics.get("effective_gray_std")
    )
    dynamic_range = _optional_finite(
        detection.debug_metrics.get("effective_gray_dynamic_range")
    )
    return bool(
        mean is not None
        and standard_deviation is not None
        and dynamic_range is not None
        and mean <= config.black_frame_max_mean
        and standard_deviation <= config.black_frame_max_std
        and dynamic_range <= config.black_frame_max_dynamic_range
    )


def _relative_y(y: float, glass: GlassInspectionConfig) -> float:
    ellipse = glass.geometry.ellipse
    top = float(ellipse.center_y - ellipse.radius_y)
    bottom = float(ellipse.center_y + ellipse.radius_y)
    return _unit((float(y) - top) / max(1.0, bottom - top))


def _longest_consecutive(indices: tuple[int, ...]) -> int:
    longest = 0
    current = 0
    prior: int | None = None
    for index in indices:
        current = current + 1 if prior is not None and index == prior + 1 else 1
        longest = max(longest, current)
        prior = index
    return longest


def _qualified_anchor_keys(
    anchors: tuple[_CandidateRef, ...],
    *,
    frame_count: int,
    horizon: int,
    maximum_jump: float,
) -> set[tuple[int, int]]:
    if not anchors:
        return set()
    ordered = sorted(
        anchors,
        key=lambda item: (
            item.frame_offset,
            float(item.candidate.y),
            item.candidate.source,
        ),
    )
    groups: list[list[_CandidateRef]] = []
    current: list[_CandidateRef] = []
    for anchor in ordered:
        if not current:
            current = [anchor]
            continue
        prior = current[-1]
        gap = anchor.frame_offset - prior.frame_offset
        distance = abs(float(anchor.candidate.y) - float(prior.candidate.y))
        if (
            0 < gap <= horizon * 2
            and distance <= maximum_jump * gap * 0.90
        ):
            current.append(anchor)
        else:
            groups.append(current)
            current = [anchor]
    if current:
        groups.append(current)

    minimum = 2 if frame_count <= max(6, horizon * 2) else 3
    return {
        (anchor.frame_offset, anchor.candidate_offset)
        for group in groups
        if len(group) >= minimum
        for anchor in group
    }


def _node_order(node: _Node) -> int:
    base = {"oil": 0, "full": 1, "empty": 2, "unknown": 3}[node.kind]
    if node.y is None:
        return base * 1_000_000
    return base * 1_000_000 + int(round(node.y * 100.0))


def _unknown_node(layer: tuple[_Node, ...]) -> _Node:
    return next(node for node in layer if node.kind == "unknown")


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _optional_finite(value: object) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _unit(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
