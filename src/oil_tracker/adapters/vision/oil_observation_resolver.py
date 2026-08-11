from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Iterable, Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig


OIL_OBSERVATION_RESOLVER_VERSION = "r6-optics-aware-observation-v1"

_OIL_REPLACED_FLAGS = {
    "LOW_CONFIDENCE",
    "OIL_EVIDENCE_AMBIGUOUS",
    "OIL_PIPELINE_UNAVAILABLE",
    "OIL_REACQUISITION_PENDING",
    "SEQUENCE_INITIAL_STATE_PRIOR",
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
class OilObservationResolverConfig:
    entrance_band_ratio: float = 0.27
    recurring_track_min_frames: int = 6
    recurring_track_min_ratio: float = 0.18
    recurring_track_tolerance_ratio: float = 0.018
    direct_anchor_min_material: float = 0.24
    direct_anchor_max_artifact: float = 0.31
    direct_anchor_max_material_texture_conflict: float = 0.60
    terminal_anchor_min_sector_fraction: float = 0.78
    state_min_evidence: float = 0.58
    black_frame_max_mean: float = 2.0
    black_frame_max_std: float = 2.0
    black_frame_max_dynamic_range: float = 4.0
    unknown_transition_cost: float = 0.20
    incompatible_state_transition_cost: float = 2.5


@dataclass(frozen=True)
class OilObservationDiagnostics:
    version: str
    frame_count: int
    oil_frame_count: int
    full_frame_count: int
    empty_frame_count: int
    unknown_frame_count: int
    eligible_candidate_count: int
    ineligible_candidate_count: int
    recurring_track_count: int
    maximum_track_opposition: float


@dataclass(frozen=True)
class OilObservationResolution:
    detections: tuple[PhaseDetection, ...]
    diagnostics: OilObservationDiagnostics


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


class OilObservationResolver:
    """Resolve one image-supported Oil/state observation per sampled frame.

    Initial state is used only in the first-layer prior. FULL/EMPTY emissions
    come only from raw typed no-interface metrics, and every numeric output is
    copied from an explicitly eligible candidate in that same frame.
    """

    version = OIL_OBSERVATION_RESOLVER_VERSION

    def __init__(self, config: OilObservationResolverConfig | None = None) -> None:
        self.config = config or OilObservationResolverConfig()

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> OilObservationResolution:
        source = tuple(detections)
        if not source:
            return OilObservationResolution(
                (),
                OilObservationDiagnostics(
                    self.version,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0.0,
                ),
            )
        refs_by_frame, ineligible_count = self._candidate_refs(source, glass)
        refs_by_frame = self._apply_anchor_support(refs_by_frame, glass)
        refs_by_frame, track_count, maximum_track_opposition = (
            self._apply_track_opposition(refs_by_frame, glass)
        )
        layers = tuple(
            self._nodes_for_frame(detection, refs_by_frame[index])
            for index, detection in enumerate(source)
        )
        path = self._best_path(
            layers,
            source,
            glass,
            confirmed_initial_state,
        )
        path = self._bound_unanchored_oil_runs(path, layers, glass)
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
        counts = {
            kind: sum(node.kind == kind for node in path)
            for kind in ("oil", "full", "empty", "unknown")
        }
        return OilObservationResolution(
            resolved,
            OilObservationDiagnostics(
                version=self.version,
                frame_count=len(resolved),
                oil_frame_count=counts["oil"],
                full_frame_count=counts["full"],
                empty_frame_count=counts["empty"],
                unknown_frame_count=counts["unknown"],
                eligible_candidate_count=sum(map(len, refs_by_frame)),
                ineligible_candidate_count=ineligible_count,
                recurring_track_count=track_count,
                maximum_track_opposition=maximum_track_opposition,
            ),
        )

    def _candidate_refs(
        self,
        detections: tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[tuple[_CandidateRef, ...], ...], int]:
        limit = max(1, int(glass.detector_settings.candidate_top_k))
        rows: list[tuple[_CandidateRef, ...]] = []
        ineligible = 0
        # Build this without reusing projected fill/state. Only a selected
        # same-frame semantic Oil candidate has anchor authority here.
        semantic_anchors = tuple(
            (frame_offset, float(item.y))
            for frame_offset, detection in enumerate(detections)
            for item in detection.candidates
            if item.kind is BoundaryKind.OIL_AIR
            and _finite(item.y)
            and item.selected
            and _unit(item.features.get("r6_material_path", 0.0)) < 0.5
            and _candidate_material_texture_conflict(item)
            <= self.config.direct_anchor_max_material_texture_conflict
        )
        semantic_sequence_available = bool(semantic_anchors)
        for frame_offset, detection in enumerate(detections):
            refs: list[_CandidateRef] = []
            semantic_selected_rows = tuple(
                float(item.y)
                for item in detection.candidates
                if item.kind is BoundaryKind.OIL_AIR
                and _finite(item.y)
                and item.selected
                and _unit(item.features.get("r6_material_path", 0.0)) < 0.5
                and _candidate_material_texture_conflict(item)
                <= self.config.direct_anchor_max_material_texture_conflict
            )
            for candidate_offset, candidate in enumerate(detection.candidates):
                if candidate.kind is not BoundaryKind.OIL_AIR or not _finite(candidate.y):
                    continue
                if not _candidate_eligible(candidate):
                    ineligible += 1
                    continue
                material = _candidate_material_support(candidate)
                artifact = _candidate_artifact_signature(candidate)
                ambiguity = _candidate_ambiguity(candidate)
                material_texture_conflict = _candidate_material_texture_conflict(
                    candidate
                )
                material_path = bool(
                    _unit(candidate.features.get("r6_material_path", 0.0)) >= 0.5
                )
                strong_material_anchor = bool(
                    not material_path
                    and material >= 0.68
                    and artifact <= 0.18
                    and ambiguity <= 0.25
                    and material_texture_conflict
                    <= self.config.direct_anchor_max_material_texture_conflict
                )
                terminal_partition_support = _unit(
                    candidate.features.get(
                        "material_terminal_partition_support",
                        0.0,
                    )
                )
                terminal_fallback = bool(
                    not semantic_sequence_available
                    and terminal_partition_support >= 0.60
                    and _unit(
                        candidate.features.get(
                            "material_path_sector_fraction",
                            0.0,
                        )
                    )
                    >= self.config.terminal_anchor_min_sector_fraction
                )
                semantic_corroboration = bool(
                    _semantic_path_corroborated(
                        frame_offset,
                        float(candidate.y),
                        semantic_anchors,
                        glass,
                        same_frame_rows=semantic_selected_rows,
                    )
                    and _material_semantic_corroboration_allowed(
                        float(candidate.y),
                        terminal_partition_support,
                        semantic_selected_rows,
                        glass,
                        material_layer_topology=bool(
                            _unit(
                                candidate.features.get(
                                    "sequence_material_layer_topology",
                                    0.0,
                                )
                            )
                            >= 0.5
                        ),
                    )
                )
                independent_path_anchor = bool(
                    material_path
                    and _unit(candidate.features.get("boundary_likelihood", 0.0)) >= 0.52
                    and _candidate_optics_opposition(candidate) <= 0.30
                    and material_texture_conflict
                    <= self.config.direct_anchor_max_material_texture_conflict
                    and _unit(candidate.features.get("material_path_sector_fraction", 0.0)) >= 0.60
                    and (terminal_fallback or semantic_corroboration)
                )
                direct_anchor = bool(
                    independent_path_anchor
                    or (
                        (candidate.selected or strong_material_anchor)
                        and material >= self.config.direct_anchor_min_material
                        and artifact <= self.config.direct_anchor_max_artifact
                        and material_texture_conflict
                        <= self.config.direct_anchor_max_material_texture_conflict
                    )
                )
                refs.append(
                    _CandidateRef(
                        frame_offset=frame_offset,
                        candidate_offset=candidate_offset,
                        candidate=candidate,
                        local_quality=_candidate_quality(candidate)
                        + (0.36 if direct_anchor else 0.0),
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
        return tuple(rows), ineligible

    def _apply_anchor_support(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[_CandidateRef, ...], ...]:
        direct = tuple(
            ref
            for refs in refs_by_frame
            for ref in refs
            if ref.direct_anchor
        )
        horizon = max(2, min(3, int(glass.detector_settings.oil_path_window)))
        maximum_jump = max(
            1.0,
            float(glass.detector_settings.temporal_max_jump_px),
        )
        qualified = _qualified_anchor_keys(
            direct,
            frame_count=len(refs_by_frame),
            horizon=horizon,
            maximum_jump=maximum_jump,
        )
        anchors = tuple(
            ref
            for ref in direct
            if (ref.frame_offset, ref.candidate_offset) in qualified
            or (
                ref.candidate.selected
                and _unit(ref.candidate.features.get("r6_material_path", 0.0)) < 0.5
            )
        )
        output: list[tuple[_CandidateRef, ...]] = []
        for refs in refs_by_frame:
            row: list[_CandidateRef] = []
            for ref in refs:
                key = (ref.frame_offset, ref.candidate_offset)
                semantic_current_anchor = bool(
                    ref.candidate.selected
                    and _unit(ref.candidate.features.get("r6_material_path", 0.0))
                    < 0.5
                    and _candidate_material_texture_conflict(ref.candidate)
                    <= self.config.direct_anchor_max_material_texture_conflict
                )
                support = 1.0 if key in qualified or semantic_current_anchor else 0.0
                if support < 1.0:
                    for anchor in anchors:
                        gap = abs(anchor.frame_offset - ref.frame_offset)
                        if gap == 0 or gap > horizon:
                            continue
                        allowed = maximum_jump * gap * 0.65
                        distance = abs(float(anchor.candidate.y) - float(ref.candidate.y))
                        support = max(
                            support,
                            _unit(1.0 - distance / max(1.0, allowed)),
                        )
                row.append(replace(ref, anchor_support=support))
            output.append(tuple(row))
        return tuple(output)

    def _apply_track_opposition(
        self,
        refs_by_frame: tuple[tuple[_CandidateRef, ...], ...],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[tuple[_CandidateRef, ...], ...], int, float]:
        frame_count = len(refs_by_frame)
        height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
        tolerance = max(
            3.0,
            height * self.config.recurring_track_tolerance_ratio,
        )
        # Evaluate several shifted grids. A fixed row that jitters across one
        # quantization boundary must not escape the recurrence check.
        bucket_width = tolerance * 2.4
        buckets: dict[tuple[int, int], list[_CandidateRef]] = {}
        for phase, shift in enumerate((0.0, bucket_width / 3.0, 2.0 * bucket_width / 3.0)):
            for refs in refs_by_frame:
                for ref in refs:
                    bucket = int(math.floor((float(ref.candidate.y) + shift) / bucket_width))
                    buckets.setdefault((phase, bucket), []).append(ref)

        penalties: dict[tuple[int, int], float] = {}
        recurring_tracks: set[int] = set()
        maximum = 0.0
        for bucket_refs in buckets.values():
            best_by_frame: dict[int, _CandidateRef] = {}
            for ref in bucket_refs:
                prior = best_by_frame.get(ref.frame_offset)
                if prior is None or ref.local_quality > prior.local_quality:
                    best_by_frame[ref.frame_offset] = ref
            ordered = tuple(best_by_frame[index] for index in sorted(best_by_frame))
            presence_ratio = len(ordered) / max(1, frame_count)
            longest_run = _longest_consecutive(
                tuple(item.frame_offset for item in ordered)
            )
            if (
                len(ordered) < self.config.recurring_track_min_frames
                or presence_ratio < self.config.recurring_track_min_ratio
                or longest_run < self.config.recurring_track_min_frames
            ):
                continue
            ys = tuple(float(item.candidate.y) for item in ordered)
            mean_y = sum(ys) / len(ys)
            variance = sum((value - mean_y) ** 2 for value in ys) / len(ys)
            stability = max(
                0.0,
                1.0 - math.sqrt(variance) / max(1.0, tolerance * 1.5),
            )
            if stability <= 0.0:
                continue
            opposition = sum(
                _candidate_artifact_signature(item.candidate)
                for item in ordered
            ) / len(ordered)
            optics = sum(
                _candidate_optics_opposition(item.candidate)
                for item in ordered
            ) / len(ordered)
            material = sum(
                _candidate_material_support(item.candidate)
                for item in ordered
            ) / len(ordered)
            supplemental_ratio = sum(
                _unit(item.candidate.features.get("r6_material_path", 0.0)) >= 0.5
                for item in ordered
            ) / len(ordered)
            contradiction = max(
                0.0,
                max(opposition, optics) - 0.35 * material - 0.04,
            )
            recurrence = _unit(
                (presence_ratio - self.config.recurring_track_min_ratio)
                / max(0.01, 0.70 - self.config.recurring_track_min_ratio)
            )
            semantic_penalty = _unit(
                recurrence * stability * (0.18 + contradiction * 2.6)
            )
            # The supplemental path generator intentionally has broad recall.
            # A nearly fixed supplemental row therefore needs another semantic
            # anchor; continuity cannot turn it into truth by itself.
            supplemental_fixed_penalty = _unit(
                recurrence
                * stability
                * supplemental_ratio
                * (0.30 + 0.55 * (1.0 - material))
            )
            track_penalty = max(semantic_penalty, supplemental_fixed_penalty)
            if track_penalty <= 0.0:
                continue
            recurring_tracks.add(int(round(mean_y / tolerance)))
            maximum = max(maximum, track_penalty)
            for item in bucket_refs:
                semantic_anchor = bool(
                    item.candidate.selected
                    and _unit(
                        item.candidate.features.get("r6_material_path", 0.0)
                    )
                    < 0.5
                )
                value = track_penalty * (0.35 if semantic_anchor else 1.0)
                key = (item.frame_offset, item.candidate_offset)
                penalties[key] = max(penalties.get(key, 0.0), value)

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
        return output, len(recurring_tracks), maximum

    def _nodes_for_frame(
        self,
        detection: PhaseDetection,
        refs: tuple[_CandidateRef, ...],
    ) -> tuple[_Node, ...]:
        if _hard_unavailable(detection, self.config):
            return (_Node("unknown", 1.25, "unknown"),)

        nodes: list[_Node] = [
            _Node(
                "oil",
                _oil_emission(ref),
                f"oil:{ref.candidate.source}:{ref.candidate.y:.6f}",
                ref,
            )
            for ref in refs
        ]
        full = _raw_state_evidence(detection, FillState.FULL_NO_INTERFACE)
        empty = _raw_state_evidence(detection, FillState.EMPTY_NO_INTERFACE)
        if full >= self.config.state_min_evidence:
            nodes.append(
                _Node(
                    "full",
                    -0.10 + 1.05 * full,
                    "full",
                    state_evidence=full,
                )
            )
        if empty >= self.config.state_min_evidence:
            nodes.append(
                _Node(
                    "empty",
                    -0.10 + 1.05 * empty,
                    "empty",
                    state_evidence=empty,
                )
            )
        best_quality = max((ref.local_quality for ref in refs), default=0.0)
        ambiguity = _unit(detection.debug_metrics.get("oil_ambiguity_score", 0.0))
        no_interface = _unit(
            detection.debug_metrics.get("oil_no_interface_score", 0.0)
        )
        unknown = 0.12 + 0.34 * ambiguity + 0.08 * no_interface - 0.10 * best_quality
        nodes.append(_Node("unknown", unknown, "unknown"))
        return tuple(nodes)

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
            node.emission
            + _initial_score(node, glass, confirmed_initial_state)
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
                        + self._transition_score(prior, node, glass, dt),
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
            key=lambda index: (
                scores[-1][index],
                -_node_order(layers[-1][index]),
            ),
        )
        offsets = [last_offset]
        for frame_offset in range(len(layers) - 1, 0, -1):
            offsets.append(backpointers[frame_offset][offsets[-1]])
        offsets.reverse()
        return tuple(
            layers[index][offset]
            for index, offset in enumerate(offsets)
        )

    def _bound_unanchored_oil_runs(
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
            if not qualified:
                for index in range(start, end + 1):
                    bounded[index] = _unknown_node(layers[index])
                offset += 1
                continue
            preceded_by_supported_state = bool(
                start > 0 and path[start - 1].kind in {"full", "empty"}
            )
            if not preceded_by_supported_state:
                for index in range(start, max(start, qualified[0] - horizon)):
                    bounded[index] = _unknown_node(layers[index])
            for prior_anchor, next_anchor in zip(qualified, qualified[1:]):
                if next_anchor - prior_anchor <= horizon * 2:
                    continue
                for index in range(prior_anchor + 1, next_anchor):
                    bounded[index] = _unknown_node(layers[index])
            trailing_start = min(end + 1, qualified[-1] + horizon + 1)
            next_supported_state = bool(
                end + 1 < len(path)
                and path[end + 1].kind in {"full", "empty"}
                and path[end + 1].state_evidence >= self.config.state_min_evidence
            )
            if not next_supported_state:
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
    ) -> float:
        if prior.kind == current.kind:
            if current.kind == "oil":
                assert prior.y is not None and current.y is not None
                maximum = max(
                    1.0,
                    float(glass.detector_settings.temporal_max_jump_px),
                )
                time_scale = max(1.0, dt / 0.5)
                normalized = abs(current.y - prior.y) / (maximum * time_scale)
                return 0.22 - (0.12 * normalized + 0.30 * normalized * normalized)
            if current.kind in {"full", "empty"}:
                return 0.10 + 0.14 * current.state_evidence
            return 0.02

        if prior.kind == "unknown" or current.kind == "unknown":
            return -self.config.unknown_transition_cost
        if prior.kind in {"full", "empty"} and current.kind in {"full", "empty"}:
            return -self.config.incompatible_state_transition_cost
        if prior.kind == "oil" and current.kind in {"full", "empty"}:
            if current.state_evidence < self.config.state_min_evidence:
                return -self.config.incompatible_state_transition_cost
            return -_edge_transition_cost(prior, current.kind, glass, self.config)
        if current.kind == "oil" and prior.kind in {"full", "empty"}:
            assert current.candidate_ref is not None
            edge_cost = _edge_transition_cost(
                current,
                prior.kind,
                glass,
                self.config,
            )
            if (
                current.candidate_ref.direct_anchor
                or current.candidate_ref.anchor_support >= 0.45
            ):
                # A missed edge entrance must not lock a confirmed prior for the
                # rest of the video. Independent material anchors can release it
                # from any visible location, with edge proximity still preferred.
                return 0.08 - min(0.45, edge_cost * 0.18)
            return -max(0.35, edge_cost)
        return -0.10

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
        metrics = dict(detection.debug_metrics)
        metrics.update(
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
                "r6_state_image_evidence": float(node.state_evidence),
            }
        )
        if node.kind == "oil":
            assert node.y is not None and node.candidate_ref is not None
            y = float(node.y)
            zero = glass.geometry.zero_line_y
            px = None if zero is None else float(zero) - y
            mm = None if px is None or glass.mm_per_pixel is None else px * glass.mm_per_pixel
            confidence = _oil_confidence(node.candidate_ref)
            state = _visible_state(path, frame_offset)
            flags.extend(
                (
                    "R6_RESOLVED_OIL",
                    "SEQUENCE_RESOLVED_OIL",
                    "SEQUENCE_SAME_FRAME_CANDIDATE",
                )
            )
            return replace(
                detection,
                fill_state=state,
                oil_air_level_y=y,
                oil_air_level_px_from_zero=px,
                oil_air_level_mm_from_zero=mm,
                oil_air_confidence=confidence,
                overall_confidence=max(
                    confidence,
                    detection.visibility_confidence * 0.55,
                ),
                raw_oil_air_level_y=y,
                smoothed_oil_air_level_y=y,
                candidates=candidates,
                flags=sorted(set(flags)),
                debug_metrics=metrics,
            )
        if node.kind in {"full", "empty"}:
            state = (
                FillState.FULL_NO_INTERFACE
                if node.kind == "full"
                else FillState.EMPTY_NO_INTERFACE
            )
            flags.extend(("R6_IMAGE_SUPPORTED_STATE", "SEQUENCE_RESOLVED_STATE"))
            confidence = min(0.95, 0.46 + 0.46 * node.state_evidence)
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
                debug_metrics=metrics,
            )
        flags.extend(("R6_OBSERVATION_UNAVAILABLE", "SEQUENCE_UNAVAILABLE"))
        if confirmed_initial_state is not None:
            flags.append("R6_INITIAL_STATE_CONTEXT_ONLY")
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
            debug_metrics=metrics,
        )


def _semantic_path_corroborated(
    frame_offset: int,
    candidate_y: float,
    semantic_anchors: tuple[tuple[int, float], ...],
    glass: GlassInspectionConfig,
    *,
    same_frame_rows: tuple[float, ...],
) -> bool:
    if not semantic_anchors:
        return False
    same_frame_tolerance = max(
        6.0,
        float(glass.detector_settings.temporal_max_jump_px),
    )
    if any(
        abs(candidate_y - selected_y) <= same_frame_tolerance
        for selected_y in same_frame_rows
    ):
        return True
    # An independently observed candidate may bridge a missed semantic frame,
    # but only inside a bounded corridor defined by real anchors. The candidate
    # coordinate itself is never interpolated or carried.
    if len(semantic_anchors) < 3:
        return False
    maximum_gap = max(3, int(glass.detector_settings.oil_path_window) * 2)
    prior = next(
        (
            item
            for item in reversed(semantic_anchors)
            if item[0] < frame_offset and frame_offset - item[0] <= maximum_gap
        ),
        None,
    )
    following = next(
        (
            item
            for item in semantic_anchors
            if item[0] > frame_offset and item[0] - frame_offset <= maximum_gap
        ),
        None,
    )
    corridor_tolerance = max(
        8.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.48,
    )
    if prior is not None and following is not None:
        span = following[0] - prior[0]
        fraction = (frame_offset - prior[0]) / max(1, span)
        expected = prior[1] + fraction * (following[1] - prior[1])
        return abs(candidate_y - expected) <= corridor_tolerance
    nearest = prior if following is None else following
    if nearest is None:
        return False
    gap = abs(frame_offset - nearest[0])
    one_sided_gap = max(2, int(glass.detector_settings.oil_path_window))
    return bool(
        gap <= one_sided_gap
        and abs(candidate_y - nearest[1])
        <= corridor_tolerance + gap * 2.0
    )


def _material_semantic_corroboration_allowed(
    candidate_y: float,
    terminal_partition: float,
    same_frame_rows: tuple[float, ...],
    glass: GlassInspectionConfig,
    *,
    material_layer_topology: bool,
) -> bool:
    # Between semantic frames, a terminal Foam/material edge is precisely the
    # common wrong interface, so only the non-terminal Oil-side path may bridge.
    if not same_frame_rows:
        return terminal_partition < 0.60
    close = max(6.0, float(glass.detector_settings.temporal_max_jump_px) * 0.25)
    oil_side_offset = max(
        10.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.35,
    )
    return any(
        abs(candidate_y - selected_y) <= close
        or (
            material_layer_topology
            and candidate_y - selected_y >= oil_side_offset
        )
        for selected_y in same_frame_rows
    )


def _candidate_eligible(candidate: BoundaryCandidate) -> bool:
    explicit = candidate.features.get("sequence_eligible")
    if explicit is not None:
        return _unit(explicit) >= 0.5
    # Compatibility for non-production test/fake detectors. Production R6
    # always writes the explicit bit at hypothesis projection.
    availability = _unit(candidate.features.get("evidence_availability", 1.0))
    visibility = _unit(candidate.features.get("visibility", 1.0))
    conflicts = (
        _candidate_optics_opposition(candidate),
        _unit(candidate.penalties.get("exclusion_conflict", 0.0)),
        _unit(candidate.penalties.get("border_penalty", 0.0)),
    )
    return bool(availability >= 0.30 and visibility >= 0.30 and max(conflicts) < 0.55)


def _candidate_material_support(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    return _unit(
        0.34 * _unit(features.get("boundary_likelihood", candidate.feature_score))
        + 0.18 * _unit(features.get("broad_strength", features.get("region_contrast", 0.0)))
        + 0.14 * _unit(features.get("narrow_peak_strength", features.get("edge_strength", 0.0)))
        + 0.13 * _unit(features.get("narrow_horizontal_coverage", features.get("horizontal_coverage", 0.0)))
        + 0.07 * _unit(features.get("broad_scale_consistency", 0.0))
        + 0.05 * _unit(features.get("polarity_confidence", 0.0))
        + 0.09 * _unit(features.get("material_terminal_partition_support", 0.0))
    )


def _candidate_optics_opposition(candidate: BoundaryCandidate) -> float:
    penalties = candidate.penalties
    return _unit(
        max(
            penalties.get("optics_conflict", 0.0),
            penalties.get("glare_conflict", penalties.get("glare_penalty", 0.0)),
        )
    )


def _candidate_artifact_signature(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    penalties = candidate.penalties
    return _unit(
        0.40 * _unit(features.get("artifact_likelihood", penalties.get("artifact_likelihood", 0.0)))
        + 0.18 * _unit(features.get("static_prior_contribution", penalties.get("static_artifact_penalty", 0.0)))
        + 0.20 * _candidate_optics_opposition(candidate)
        + 0.12 * _unit(penalties.get("border_penalty", 0.0))
        + 0.10 * _unit(penalties.get("exclusion_conflict", penalties.get("exclusion_penalty", 0.0)))
    )


def _candidate_material_texture_conflict(candidate: BoundaryCandidate) -> float:
    return _unit(
        candidate.penalties.get(
            "material_texture_conflict",
            candidate.features.get("material_texture_conflict", 0.0),
        )
    )


def _candidate_ambiguity(candidate: BoundaryCandidate) -> float:
    return _unit(
        candidate.features.get(
            "ambiguity_likelihood",
            candidate.penalties.get("ambiguity_likelihood", 0.0),
        )
    )


def _candidate_quality(candidate: BoundaryCandidate) -> float:
    features = candidate.features
    material = _candidate_material_support(candidate)
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        0.64 * material
        + 0.18 * availability
        - 0.14 * _candidate_ambiguity(candidate)
        - 0.24 * _candidate_artifact_signature(candidate)
        - 0.12 * _candidate_material_texture_conflict(candidate)
    )


def _oil_emission(ref: _CandidateRef) -> float:
    candidate = ref.candidate
    features = candidate.features
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        -0.20
        + 0.68 * _candidate_material_support(candidate)
        + 0.10 * availability
        + (0.36 if ref.direct_anchor else 0.0)
        + 0.48 * ref.anchor_support
        - 0.76 * _candidate_artifact_signature(candidate)
        - 0.18 * _candidate_ambiguity(candidate)
        - 0.78 * ref.track_opposition
        - 0.34 * _candidate_material_texture_conflict(candidate)
    )


def _oil_confidence(ref: _CandidateRef) -> float:
    return min(
        0.95,
        max(
            0.44,
            0.46
            + 0.48 * _candidate_material_support(ref.candidate)
            - 0.20 * _candidate_artifact_signature(ref.candidate)
            - 0.20 * ref.track_opposition,
        ),
    )


def _raw_state_evidence(detection: PhaseDetection, state: FillState) -> float:
    key = (
        "oil_no_interface_full_likelihood"
        if state is FillState.FULL_NO_INTERFACE
        else "oil_no_interface_empty_likelihood"
    )
    return _unit(detection.debug_metrics.get(key, 0.0))


def _initial_score(
    node: _Node,
    glass: GlassInspectionConfig,
    confirmed_initial_state: InitialObservationState | None,
) -> float:
    if confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE:
        if node.kind == "full":
            return 0.55
        if node.kind == "empty":
            return -1.0
        if node.kind == "oil" and node.y is not None:
            return 0.18 if _relative_y(node.y, glass) <= 0.27 else -0.18
    if confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE:
        if node.kind == "empty":
            return 0.55
        if node.kind == "full":
            return -1.0
        if node.kind == "oil" and node.y is not None:
            return 0.18 if _relative_y(node.y, glass) >= 0.73 else -0.18
    return 0.06 if node.kind == "unknown" else 0.0


def _edge_transition_cost(
    oil_node: _Node,
    state_kind: str,
    glass: GlassInspectionConfig,
    config: OilObservationResolverConfig,
) -> float:
    assert oil_node.y is not None
    relative = _relative_y(oil_node.y, glass)
    band = config.entrance_band_ratio
    if state_kind == "full":
        overflow = max(0.0, relative - band)
    else:
        overflow = max(0.0, (1.0 - band) - relative)
    if overflow <= 0.0:
        return 0.05
    return 0.35 + 1.8 * overflow


def _visible_state(path: tuple[_Node, ...], index: int) -> FillState:
    prior_y = next(
        (
            path[offset].y
            for offset in range(index - 1, max(-1, index - 4), -1)
            if path[offset].kind == "oil"
        ),
        None,
    )
    next_y = next(
        (
            path[offset].y
            for offset in range(index + 1, min(len(path), index + 4))
            if path[offset].kind == "oil"
        ),
        None,
    )
    current_y = path[index].y
    assert current_y is not None
    delta = 0.0
    if prior_y is not None and next_y is not None:
        delta = next_y - prior_y
    elif prior_y is not None:
        delta = current_y - prior_y
    elif next_y is not None:
        delta = next_y - current_y
    if delta < -2.0:
        return FillState.FILLING_VISIBLE
    if delta > 2.0:
        return FillState.DRAINING_VISIBLE
    return FillState.PARTIAL_VISIBLE


def _project_candidates(
    candidates: Iterable[BoundaryCandidate],
    selected_ref: _CandidateRef | None,
) -> list[BoundaryCandidate]:
    output: list[BoundaryCandidate] = []
    for offset, candidate in enumerate(candidates):
        if candidate.kind is not BoundaryKind.OIL_AIR:
            output.append(candidate)
            continue
        selected = selected_ref is not None and offset == selected_ref.candidate_offset
        eligible = _candidate_eligible(candidate)
        output.append(
            replace(
                candidate,
                selected=selected,
                rejected=not selected,
                reject_reason=(
                    ""
                    if selected
                    else (
                        "r6_candidate_ineligible"
                        if not eligible
                        else "not_selected_by_r6_observation_resolver"
                    )
                ),
            )
        )
    return output


def _hard_unavailable(
    detection: PhaseDetection,
    config: OilObservationResolverConfig,
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
    """Return anchors that belong to a bounded multi-frame path.

    Candidate order inside a frame is not temporal order.  The R5-style greedy
    grouping treated a second candidate from the same frame as a path break, so
    common top-k rasters fragmented every otherwise valid track.  R6 computes
    forward/backward path support across *different* frames and never connects
    candidates merely because they are adjacent in the flattened list.
    """

    if not anchors:
        return set()
    minimum = 2 if frame_count <= max(6, horizon * 2) else 3
    by_frame: dict[int, tuple[_CandidateRef, ...]] = {}
    for frame_offset in sorted({item.frame_offset for item in anchors}):
        by_frame[frame_offset] = tuple(
            item for item in anchors if item.frame_offset == frame_offset
        )

    forward: dict[tuple[int, int], int] = {}
    for anchor in sorted(
        anchors,
        key=lambda item: (item.frame_offset, float(item.candidate.y)),
    ):
        best = 0
        first = max(0, anchor.frame_offset - horizon * 2)
        for prior_frame in range(first, anchor.frame_offset):
            gap = anchor.frame_offset - prior_frame
            for prior in by_frame.get(prior_frame, ()):
                if (
                    abs(float(anchor.candidate.y) - float(prior.candidate.y))
                    <= maximum_jump * gap * 0.90
                ):
                    best = max(
                        best,
                        forward.get(
                            (prior.frame_offset, prior.candidate_offset),
                            1,
                        ),
                    )
        forward[(anchor.frame_offset, anchor.candidate_offset)] = best + 1

    backward: dict[tuple[int, int], int] = {}
    for anchor in sorted(
        anchors,
        key=lambda item: (-item.frame_offset, float(item.candidate.y)),
    ):
        best = 0
        last = min(frame_count - 1, anchor.frame_offset + horizon * 2)
        for next_frame in range(anchor.frame_offset + 1, last + 1):
            gap = next_frame - anchor.frame_offset
            for following in by_frame.get(next_frame, ()):
                if (
                    abs(float(anchor.candidate.y) - float(following.candidate.y))
                    <= maximum_jump * gap * 0.90
                ):
                    best = max(
                        best,
                        backward.get(
                            (following.frame_offset, following.candidate_offset),
                            1,
                        ),
                    )
        backward[(anchor.frame_offset, anchor.candidate_offset)] = best + 1

    return {
        key
        for key in forward
        if forward[key] + backward.get(key, 1) - 1 >= minimum
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
