from __future__ import annotations

from dataclasses import dataclass
import math

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState

from .oil_candidate_authority import OilCandidateAuthority
from .oil_phase_identity import OilPhaseIdentity
from .oil_sequence_types import OilCandidateRef, OilSequenceNode


@dataclass(frozen=True)
class OilInterfaceSelectorPolicy:
    geometry_top_y: float
    geometry_height: float
    maximum_jump_px: float
    lookahead_frames: int
    ambiguity_margin: float
    unknown_transition_cost: float
    incompatible_state_transition_cost: float
    state_min_evidence: float
    entrance_band_ratio: float


def build_interface_layers(
    detection: PhaseDetection,
    refs: tuple[OilCandidateRef, ...],
    *,
    hard_unavailable: bool,
    minimum_confidence: float,
    state_min_evidence: float,
) -> tuple[tuple[OilSequenceNode, ...], tuple[OilSequenceNode, ...]]:
    """Build distinct physical-phase and publishable-selector layers."""

    if hard_unavailable:
        unavailable = (OilSequenceNode("unknown", 1.25, "unknown"),)
        return unavailable, unavailable

    phase_oil = tuple(
        OilSequenceNode(
            "oil",
            oil_candidate_emission(ref),
            f"oil:{ref.candidate.source}:{ref.candidate.y:.6f}",
            ref,
        )
        for ref in refs
        if _phase_admitted(ref)
    )
    by_hypothesis: dict[str, list[OilCandidateRef]] = {}
    for ref in refs:
        if not oil_candidate_is_publishable(ref, minimum_confidence):
            continue
        assert ref.row_hypothesis_id is not None
        by_hypothesis.setdefault(ref.row_hypothesis_id, []).append(ref)
    publishable_oil = tuple(
        OilSequenceNode(
            "oil",
            oil_candidate_emission(representative),
            f"oil:{hypothesis_id}",
            representative,
        )
        for hypothesis_id, representative in (
            (
                hypothesis_id,
                min(members, key=_publishable_member_order),
            )
            for hypothesis_id, members in sorted(by_hypothesis.items())
        )
    )
    shared = _state_and_unknown_nodes(detection, refs, state_min_evidence)
    return phase_oil + shared, publishable_oil + shared


def assert_publishable_path(
    path: tuple[OilSequenceNode, ...],
    minimum_confidence: float,
) -> tuple[OilSequenceNode, ...]:
    """Assert the selector seam without re-deciding its physical owner."""

    for node in path:
        if node.kind != "oil":
            continue
        if node.candidate_ref is None or not oil_candidate_is_publishable(
            node.candidate_ref,
            minimum_confidence,
        ):
            raise AssertionError(
                "Oil interface selector returned a non-publishable row member."
            )
    return path


class BoundedOilInterfaceSelector:
    """Select one physical owner within causal phase-lifecycle constraints."""

    def __init__(self, policy: OilInterfaceSelectorPolicy) -> None:
        self.policy = policy

    def resolve(
        self,
        layers: tuple[tuple[OilSequenceNode, ...], ...],
        detections: tuple[PhaseDetection, ...],
        confirmed_initial_state: InitialObservationState | None,
        allowed_tracklet_ids: tuple[frozenset[str] | None, ...],
        owner_chains: tuple[tuple[str, ...], ...],
    ) -> tuple[OilSequenceNode, ...]:
        if not (
            len(layers)
            == len(detections)
            == len(allowed_tracklet_ids)
            == len(owner_chains)
        ):
            raise ValueError("Selector inputs must have identical frame cardinality.")
        if not layers:
            return ()
        constrained = tuple(
            _constrain_layer(layer, allowed)
            for layer, allowed in zip(
                layers,
                allowed_tracklet_ids,
                strict=True,
            )
        )
        selected: list[OilSequenceNode] = []
        committed: OilSequenceNode | None = None
        lookahead = max(0, int(self.policy.lookahead_frames))
        for start in range(len(constrained)):
            stop = min(len(constrained), start + lookahead + 1)
            segment = constrained[start:stop]
            suffix_scores = [node.emission for node in segment[-1]]
            for relative_offset in range(len(segment) - 2, -1, -1):
                absolute_offset = start + relative_offset + 1
                current_layer = segment[relative_offset]
                following_layer = segment[relative_offset + 1]
                dt = max(
                    1e-6,
                    float(detections[absolute_offset].time_sec)
                    - float(detections[absolute_offset - 1].time_sec),
                )
                current_suffix_scores: list[float] = []
                for current in current_layer:
                    choices = tuple(
                        (
                            self._transition_score(
                                current,
                                following,
                                dt,
                                owner_chains[absolute_offset],
                            )
                            + suffix_scores[following_offset],
                            following_offset,
                        )
                        for following_offset, following in enumerate(
                            following_layer
                        )
                    )
                    best_score, _best_offset = max(
                        choices,
                        key=lambda item: (
                            item[0],
                            -_node_order(following_layer[item[1]]),
                        ),
                    )
                    current_suffix_scores.append(
                        current.emission + best_score
                    )
                suffix_scores = current_suffix_scores

            if committed is None:
                current_scores = tuple(
                    suffix_scores[offset]
                    + self._initial_score(node, confirmed_initial_state)
                    for offset, node in enumerate(segment[0])
                )
            else:
                dt = max(
                    1e-6,
                    float(detections[start].time_sec)
                    - float(detections[start - 1].time_sec),
                )
                current_scores = tuple(
                    suffix_scores[offset]
                    + self._transition_score(
                        committed,
                        node,
                        dt,
                        owner_chains[start],
                    )
                    for offset, node in enumerate(segment[0])
                )
            selected_offset = max(
                range(len(segment[0])),
                key=lambda index: (
                    current_scores[index],
                    -_node_order(segment[0][index]),
                ),
            )
            committed = self._censor_competing_tracklets(
                segment[0][selected_offset],
                segment[0],
                current_scores,
            )
            selected.append(committed)
        return tuple(selected)

    def _censor_competing_tracklets(
        self,
        selected: OilSequenceNode,
        layer: tuple[OilSequenceNode, ...],
        bounded_scores: tuple[float, ...],
    ) -> OilSequenceNode:
        if selected.kind != "oil" or selected.candidate_ref is None:
            return selected
        selected_id = _node_tracklet_id(selected)
        if selected_id is None:
            return _unknown_node(layer)
        best_by_tracklet: dict[str, float] = {}
        for node, score in zip(layer, bounded_scores, strict=True):
            if node.kind != "oil" or node.candidate_ref is None:
                continue
            tracklet_id = _node_tracklet_id(node)
            if tracklet_id is None:
                continue
            best_by_tracklet[tracklet_id] = max(
                best_by_tracklet.get(tracklet_id, -math.inf),
                float(score),
            )
        selected_score = best_by_tracklet.get(selected_id, -math.inf)
        competing_score = max(
            (
                score
                for tracklet_id, score in best_by_tracklet.items()
                if tracklet_id != selected_id
            ),
            default=-math.inf,
        )
        if (
            competing_score > -math.inf
            and selected_score
            <= competing_score + self.policy.ambiguity_margin
        ):
            return _unknown_node(layer)
        return selected

    def _initial_score(
        self,
        node: OilSequenceNode,
        confirmed_initial_state: InitialObservationState | None,
    ) -> float:
        if confirmed_initial_state is InitialObservationState.FULL_NO_INTERFACE:
            if node.kind == "full":
                return 0.55
            if node.kind == "empty":
                return -1.0
            if node.kind == "oil" and node.y is not None:
                return 0.18 if self._relative_y(node.y) <= 0.27 else -0.18
        if confirmed_initial_state is InitialObservationState.EMPTY_NO_INTERFACE:
            if node.kind == "empty":
                return 0.55
            if node.kind == "full":
                return -1.0
            if node.kind == "oil" and node.y is not None:
                return 0.18 if self._relative_y(node.y) >= 0.73 else -0.18
        return 0.06 if node.kind == "unknown" else 0.0

    def _transition_score(
        self,
        prior: OilSequenceNode,
        current: OilSequenceNode,
        dt: float,
        owner_chain: tuple[str, ...],
    ) -> float:
        if prior.kind == current.kind:
            if current.kind == "oil":
                assert prior.y is not None and current.y is not None
                prior_id = _node_tracklet_id(prior)
                current_id = _node_tracklet_id(current)
                if (
                    prior_id != current_id
                    and not _adjacent_phase_owner_handoff(
                        prior_id,
                        current_id,
                        owner_chain,
                    )
                ):
                    return float("-inf")
                time_scale = max(1.0, dt / 0.5)
                normalized = abs(current.y - prior.y) / (
                    self.policy.maximum_jump_px * time_scale
                )
                current_ref = current.candidate_ref
                if (
                    normalized > 1.0
                    and current_ref is not None
                    and _independent_anchor(current_ref)
                ):
                    return -min(0.30, 0.04 + 0.08 * normalized)
                return 0.22 - (
                    0.12 * normalized + 0.30 * normalized * normalized
                )
            if current.kind in {"full", "empty"}:
                return 0.10 + 0.14 * current.state_evidence
            return 0.02

        if prior.kind == "unknown" or current.kind == "unknown":
            return -self.policy.unknown_transition_cost
        if prior.kind in {"full", "empty"} and current.kind in {"full", "empty"}:
            return -self.policy.incompatible_state_transition_cost
        if prior.kind == "oil" and current.kind in {"full", "empty"}:
            if current.state_evidence < self.policy.state_min_evidence:
                return -self.policy.incompatible_state_transition_cost
            return -self._edge_transition_cost(prior, current.kind)
        if current.kind == "oil" and prior.kind in {"full", "empty"}:
            assert current.candidate_ref is not None
            edge_cost = self._edge_transition_cost(current, prior.kind)
            if current.candidate_ref.tracklet_admitted:
                return 0.08 - min(0.45, edge_cost * 0.18)
            return -max(0.35, edge_cost)
        return -0.10

    def _edge_transition_cost(
        self,
        oil_node: OilSequenceNode,
        state_kind: str,
    ) -> float:
        assert oil_node.y is not None
        relative = self._relative_y(oil_node.y)
        band = self.policy.entrance_band_ratio
        if state_kind == "full":
            overflow = max(0.0, relative - band)
        else:
            overflow = max(0.0, (1.0 - band) - relative)
        if overflow <= 0.0:
            return 0.05
        return 0.35 + 1.8 * overflow

    def _relative_y(self, y: float) -> float:
        return (float(y) - self.policy.geometry_top_y) / max(
            1.0,
            self.policy.geometry_height,
        )


def oil_candidate_emission(ref: OilCandidateRef) -> float:
    candidate = ref.candidate
    evidence = ref.evidence
    features = candidate.features
    availability = min(
        _unit(features.get("evidence_availability", 1.0)),
        _unit(features.get("visibility", 1.0)),
    )
    return (
        -0.18
        + 0.62 * evidence.material_support
        + 0.08 * availability
        + (
            0.18
            if ref.authority is OilCandidateAuthority.ANCHOR_ELIGIBLE
            else 0.0
        )
        + 0.34 * ref.cluster_support
        + 0.30 * ref.trajectory_support
        + 0.14 * ref.representation_support
        + 0.24 * ref.semantic_corridor_support
        - 0.65 * evidence.artifact_signature
        - 0.34 * evidence.static_contradiction
        - 0.28 * evidence.ambiguity
        - 0.72 * effective_track_opposition(ref)
        - ref.foam_alias_penalty
        + (
            0.22
            * (evidence.terminal_support if evidence.material_path else 0.0)
            if ref.terminal_fallback
            else 0.0
        )
        + 0.24 * evidence.registered_motion
    )


def oil_candidate_confidence(ref: OilCandidateRef) -> float:
    evidence = ref.evidence
    return _unit(
        0.28
        + 0.50 * evidence.material_support
        + 0.16 * ref.cluster_support
        + 0.10 * ref.trajectory_support
        + 0.08 * ref.representation_support
        + 0.08 * ref.semantic_corridor_support
        - 0.20 * evidence.artifact_signature
        - 0.10 * evidence.static_contradiction
        - 0.12 * evidence.ambiguity
        - 0.22 * effective_track_opposition(ref)
        + (
            0.08
            * (evidence.terminal_support if evidence.material_path else 0.0)
            if ref.terminal_fallback
            else 0.0
        )
        + 0.08 * evidence.registered_motion
    )


def recurrence_hard_contradiction(ref: OilCandidateRef) -> bool:
    """Allow recurrence demotion only with candidate-local contradiction."""

    evidence = ref.evidence
    return bool(
        ref.phase_identity is OilPhaseIdentity.OPPOSED_MATERIAL
        or evidence.material_texture_conflict >= 0.60
        or evidence.artifact_signature >= 0.44
        or evidence.optics_opposition >= 0.46
    )


def effective_track_opposition(ref: OilCandidateRef) -> float:
    """Keep recurrence comparative when no physical contradiction exists."""

    if (
        ref.phase_identity is OilPhaseIdentity.DIRECT_INTERFACE
        and not recurrence_hard_contradiction(ref)
    ):
        return 0.25 * ref.track_opposition
    return ref.track_opposition


def oil_candidate_is_publishable(
    ref: OilCandidateRef,
    minimum_confidence: float,
) -> bool:
    return bool(
        _phase_admitted(ref)
        and ref.tracklet_id is not None
        and ref.row_hypothesis_id is not None
        and ref.trajectory_support >= 0.99
        and oil_candidate_confidence(ref) + 1e-9 >= minimum_confidence
    )


def _phase_admitted(ref: OilCandidateRef) -> bool:
    return bool(
        ref.authority >= OilCandidateAuthority.CONTINUATION_ELIGIBLE
        and ref.tracklet_admitted
        and not ref.tracklet_incompatible
        and (
            not ref.evidence.calibrated_high_recall
            or ref.trajectory_support >= 0.99
        )
    )


def _publishable_member_order(ref: OilCandidateRef) -> tuple[object, ...]:
    return (
        -oil_candidate_emission(ref),
        -oil_candidate_confidence(ref),
        -int(ref.authority),
        -float(ref.local_quality),
        float(ref.candidate.y),
        str(ref.candidate.source),
    )


def _state_and_unknown_nodes(
    detection: PhaseDetection,
    refs: tuple[OilCandidateRef, ...],
    state_min_evidence: float,
) -> tuple[OilSequenceNode, ...]:
    nodes: list[OilSequenceNode] = []
    full = _raw_state_evidence(detection, FillState.FULL_NO_INTERFACE)
    empty = _raw_state_evidence(detection, FillState.EMPTY_NO_INTERFACE)
    if full >= state_min_evidence:
        nodes.append(
            OilSequenceNode(
                "full",
                -0.10 + 1.05 * full,
                "full",
                state_evidence=full,
            )
        )
    if empty >= state_min_evidence:
        nodes.append(
            OilSequenceNode(
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
    nodes.append(OilSequenceNode("unknown", unknown, "unknown"))
    return tuple(nodes)


def _raw_state_evidence(detection: PhaseDetection, state: FillState) -> float:
    key = (
        "oil_no_interface_full_likelihood"
        if state is FillState.FULL_NO_INTERFACE
        else "oil_no_interface_empty_likelihood"
    )
    return _unit(detection.debug_metrics.get(key, 0.0))


def _unit(value: float) -> float:
    if not math.isfinite(float(value)):
        return 0.0
    return min(1.0, max(0.0, float(value)))


def _constrain_layer(
    layer: tuple[OilSequenceNode, ...],
    allowed: frozenset[str] | None,
) -> tuple[OilSequenceNode, ...]:
    if allowed is None:
        return layer
    if not allowed:
        return (_unknown_node(layer),)
    constrained = tuple(
        node
        for node in layer
        if node.kind != "oil" or _node_tracklet_id(node) in allowed
    )
    return constrained or (_unknown_node(layer),)


def _independent_anchor(ref: OilCandidateRef) -> bool:
    if ref.authority is not OilCandidateAuthority.ANCHOR_ELIGIBLE:
        return False
    if ref.cluster_support >= 0.99:
        return True
    evidence = ref.evidence
    return bool(
        evidence.availability.phase
        and ref.representation_support >= 0.50
        and ref.semantic_corridor_support >= 0.99
    )


def _node_tracklet_id(node: OilSequenceNode) -> str | None:
    if node.candidate_ref is None:
        return None
    return node.candidate_ref.tracklet_id


def _adjacent_phase_owner_handoff(
    prior_id: str | None,
    current_id: str | None,
    owner_chain: tuple[str, ...],
) -> bool:
    if prior_id is None or current_id is None:
        return False
    return any(
        left == prior_id and right == current_id
        for left, right in zip(owner_chain, owner_chain[1:])
    )


def _node_order(node: OilSequenceNode) -> int:
    base = {"oil": 0, "full": 1, "empty": 2, "unknown": 3}[node.kind]
    if node.y is None:
        return base * 1_000_000
    return base * 1_000_000 + int(round(node.y * 100.0))


def _unknown_node(layer: tuple[OilSequenceNode, ...]) -> OilSequenceNode:
    return next(node for node in layer if node.kind == "unknown")
