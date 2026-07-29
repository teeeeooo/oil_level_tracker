from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math

from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.recipe import DetectorSettings

from .oil_no_interface import NoInterfaceEvidence


class OilDecisionStatus(str, Enum):
    ACCEPTED_BOUNDARY = "accepted_boundary"
    NO_INTERFACE_SELECTED = "no_interface_selected"
    AMBIGUOUS = "ambiguous"
    PATH_PENDING = "path_pending"
    REACQUISITION_PENDING = "reacquisition_pending"
    REJECTED_BOUNDARY = "rejected_boundary"
    LOW_MARGIN = "low_margin"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class OilPathDecision:
    status: OilDecisionStatus
    candidate: BoundaryCandidate | None
    raw_y: float | None
    boundary_score: float
    no_interface_score: float
    decision_margin: float
    reason: str
    ambiguous: bool
    tracker_update_accepted: bool
    clear_smoothing: bool
    transition_cost: float
    path_cumulative_score: float
    path_second_score: float | None
    path_beam_count: int
    path_history_length: int
    reacquisition_count: int
    accepted_prior_y: float | None
    accepted_polarity: float | None
    flags: tuple[str, ...]


@dataclass(frozen=True)
class _Hypothesis:
    kind: str
    candidate_index: int | None
    y: float | None
    polarity: float | None
    observation_score: float
    cumulative_score: float
    transition_cost: float
    velocity: float | None
    history: tuple[tuple[str, float | None, float], ...]


class OilTemporalPath:
    """Bounded causal beam over scalar boundary/no-interface hypotheses.

    A beam item retains only scalar decision history. Frames, masks, candidates and
    preprocessing maps are never retained between calls.
    """

    def __init__(self) -> None:
        self._beam: tuple[_Hypothesis, ...] = ()
        self.accepted_y: float | None = None
        self.accepted_polarity: float | None = None
        self.accepted_velocity: float | None = None
        self._pending_y: float | None = None
        self._pending_polarity: float | None = None
        self._pending_velocity: float | None = None
        self._pending_count = 0
        self._no_interface_count = 0
        self._missing_count = 0
        self._smoothing_invalidated = False

    @property
    def beam_count(self) -> int:
        return len(self._beam)

    @property
    def retained_scalar_observation_count(self) -> int:
        return sum(len(item.history) for item in self._beam)

    @property
    def pending_count(self) -> int:
        return self._pending_count

    def reset(self) -> None:
        self._beam = ()
        self.accepted_y = None
        self.accepted_polarity = None
        self.accepted_velocity = None
        self._clear_pending()
        self._no_interface_count = 0
        self._missing_count = 0
        self._smoothing_invalidated = False

    def evaluate(
        self,
        candidates: list[BoundaryCandidate] | tuple[BoundaryCandidate, ...],
        no_interface: NoInterfaceEvidence,
        settings: DetectorSettings,
    ) -> OilPathDecision:
        usable = sorted(
            (candidate for candidate in candidates if not candidate.rejected),
            key=_candidate_order,
        )[: max(1, int(settings.candidate_top_k))]
        hypotheses = self._advance_beam(usable, no_interface, settings)
        self._beam = hypotheses
        best = hypotheses[0] if hypotheses else None
        second = hypotheses[1] if len(hypotheses) > 1 else None
        second_score = None if second is None else second.cumulative_score
        margin = (
            max(0.0, best.cumulative_score - second.cumulative_score)
            if best is not None and second is not None
            else (best.observation_score if best is not None else 0.0)
        )
        self._write_path_features(usable, hypotheses, margin)

        if best is None or best.kind == "missing":
            return self._missing_decision(no_interface, settings, best, second_score, margin)
        if best.kind == "no_interface":
            return self._no_interface_decision(no_interface, settings, best, second_score, margin)
        candidate = usable[best.candidate_index or 0]
        return self._boundary_decision(
            candidate,
            no_interface,
            settings,
            best,
            second_score,
            margin,
        )

    def _advance_beam(
        self,
        candidates: list[BoundaryCandidate],
        no_interface: NoInterfaceEvidence,
        settings: DetectorSettings,
    ) -> tuple[_Hypothesis, ...]:
        observations: list[tuple[str, int | None, float | None, float | None, float]] = [
            (
                "boundary",
                index,
                float(candidate.y),
                _candidate_polarity(candidate),
                _candidate_observation(candidate),
            )
            for index, candidate in enumerate(candidates)
        ]
        if no_interface.available:
            observations.append(("no_interface", None, None, None, _unit(no_interface.score)))
        else:
            observations.append(
                ("missing", None, None, None, 0.20 * _unit(no_interface.visibility_score))
            )

        previous: tuple[_Hypothesis | None, ...] = self._beam or (None,)
        expanded: list[_Hypothesis] = []
        window = max(1, int(settings.oil_path_window))
        for prior in previous:
            for kind, candidate_index, y, polarity, observation in observations:
                transition, velocity = self._transition(
                    prior,
                    kind,
                    y,
                    polarity,
                    settings,
                )
                prior_score = 0.0 if prior is None else prior.cumulative_score * 0.72
                history = () if prior is None else prior.history
                history = (history + ((kind, y, observation),))[-window:]
                expanded.append(
                    _Hypothesis(
                        kind=kind,
                        candidate_index=candidate_index,
                        y=y,
                        polarity=polarity,
                        observation_score=observation,
                        cumulative_score=float(prior_score + observation - transition),
                        transition_cost=float(transition),
                        velocity=velocity,
                        history=history,
                    )
                )

        # Best/second margin must compare distinct current decisions. Without this
        # collapse, two prior paths ending at the same current candidate can occupy
        # ranks one and two and create a false low-margin ambiguity.
        collapsed: dict[tuple[str, int | None], _Hypothesis] = {}
        for item in expanded:
            key = (item.kind, item.candidate_index)
            prior = collapsed.get(key)
            if prior is None or _hypothesis_order(item) < _hypothesis_order(prior):
                collapsed[key] = item
        ordered = sorted(collapsed.values(), key=_hypothesis_order)
        width = min(
            max(1, int(settings.oil_path_beam_width)),
            max(1, int(settings.candidate_top_k)),
        )
        return tuple(ordered[:width])

    def _transition(
        self,
        prior: _Hypothesis | None,
        kind: str,
        y: float | None,
        polarity: float | None,
        settings: DetectorSettings,
    ) -> tuple[float, float | None]:
        if prior is None:
            return 0.0, None
        if kind == "missing":
            return 0.10, prior.velocity
        if kind == "no_interface":
            return (0.02 if prior.kind == "no_interface" else 0.10), None
        if prior.kind != "boundary" or prior.y is None or y is None:
            return 0.10, None

        jump = abs(y - prior.y)
        scale = max(1.0, float(settings.temporal_max_jump_px))
        jump_cost = min(0.62, 0.12 * (jump / scale) ** 1.35)
        velocity = y - prior.y
        acceleration_cost = 0.0
        if prior.velocity is not None:
            acceleration_cost = min(
                0.24,
                0.08 * abs(velocity - prior.velocity) / scale,
            )
        polarity_cost = 0.0
        if prior.polarity not in (None, 0.0) and polarity not in (None, 0.0):
            if prior.polarity * polarity < 0.0:
                polarity_cost = 0.14
        return min(0.90, jump_cost + acceleration_cost + polarity_cost), velocity

    def _boundary_decision(
        self,
        candidate: BoundaryCandidate,
        no_interface: NoInterfaceEvidence,
        settings: DetectorSettings,
        best: _Hypothesis,
        second_score: float | None,
        margin: float,
    ) -> OilPathDecision:
        observation = _candidate_observation(candidate)
        support = int(
            round(candidate.features.get("unique_generator_support_count", 1.0))
        )
        polarity_score = _unit(candidate.features.get("polarity_score", 0.0))
        update_threshold = max(
            float(settings.minimum_final_confidence),
            float(settings.oil_tracker_update_confidence),
        )
        minimum_margin = float(settings.oil_path_min_margin)
        flags: list[str] = []

        if margin + 1e-12 < minimum_margin:
            self._on_unaccepted()
            return self._decision(
                OilDecisionStatus.LOW_MARGIN,
                None,
                no_interface,
                best,
                second_score,
                margin,
                "best_second_path_margin_below_threshold",
                True,
                False,
                False,
                ("OIL_PATH_LOW_MARGIN", "OIL_EVIDENCE_AMBIGUOUS"),
            )
        if observation + 1e-12 < float(settings.minimum_final_confidence):
            self._on_unaccepted()
            return self._decision(
                OilDecisionStatus.REJECTED_BOUNDARY,
                None,
                no_interface,
                best,
                second_score,
                margin,
                "boundary_observation_below_confidence",
                False,
                False,
                False,
                ("OIL_EVIDENCE_AMBIGUOUS",),
            )
        if support < int(settings.oil_min_consensus_sources):
            flags.append("OIL_SINGLE_SOURCE_WEAK")
            if observation < min(0.94, update_threshold + 0.18):
                self._on_unaccepted()
                return self._decision(
                    OilDecisionStatus.PATH_PENDING,
                    None,
                    no_interface,
                    best,
                    second_score,
                    margin,
                    "single_source_requires_stronger_evidence",
                    False,
                    False,
                    False,
                    tuple(flags + ["OIL_PATH_PENDING"]),
                )
        if polarity_score + 1e-12 < float(settings.oil_min_polarity_score):
            if observation < min(0.92, update_threshold + 0.20):
                self._on_unaccepted()
                return self._decision(
                    OilDecisionStatus.AMBIGUOUS,
                    None,
                    no_interface,
                    best,
                    second_score,
                    margin,
                    "polarity_evidence_below_threshold",
                    True,
                    False,
                    False,
                    tuple(flags + ["OIL_EVIDENCE_AMBIGUOUS"]),
                )
        if observation + 1e-12 < update_threshold:
            self._on_unaccepted()
            return self._decision(
                OilDecisionStatus.PATH_PENDING,
                None,
                no_interface,
                best,
                second_score,
                margin,
                "tracker_update_confidence_not_reached",
                False,
                False,
                False,
                tuple(flags + ["OIL_PATH_PENDING"]),
            )

        y = float(candidate.y)
        polarity = _candidate_polarity(candidate)
        if self.accepted_y is None:
            strong_initial = (
                support >= int(settings.oil_min_consensus_sources)
                or observation >= min(0.94, update_threshold + 0.18)
            )
            if not strong_initial:
                self._on_unaccepted()
                return self._decision(
                    OilDecisionStatus.PATH_PENDING,
                    None,
                    no_interface,
                    best,
                    second_score,
                    margin,
                    "initial_path_requires_consensus_or_strong_observation",
                    False,
                    False,
                    False,
                    tuple(flags + ["OIL_PATH_PENDING"]),
                )
            return self._accept(
                candidate,
                no_interface,
                best,
                second_score,
                margin,
                polarity,
                flags,
                clear=False,
                reacquired=False,
            )

        jump = abs(y - self.accepted_y)
        max_jump = max(1.0, float(settings.temporal_max_jump_px))
        predicted = self.accepted_y + (self.accepted_velocity or 0.0)
        velocity_residual = abs(y - predicted)
        continuous = jump <= max_jump * 1.25 or velocity_residual <= max_jump
        if continuous:
            return self._accept(
                candidate,
                no_interface,
                best,
                second_score,
                margin,
                polarity,
                flags,
                clear=False,
                reacquired=False,
            )

        strong_single = (
            observation >= 0.88
            and support >= max(3, int(settings.oil_min_consensus_sources))
            and margin >= max(minimum_margin * 2.0, 0.12)
        )
        if strong_single:
            return self._accept(
                candidate,
                no_interface,
                best,
                second_score,
                margin,
                polarity,
                flags,
                clear=True,
                reacquired=True,
            )

        tolerance = max(
            float(settings.oil_consensus_tolerance_px),
            max_jump * 0.45,
        )
        if self._pending_y is None:
            pending_count = 1
            pending_velocity = None
        else:
            predicted_pending = self._pending_y + (self._pending_velocity or 0.0)
            pending_continuous = (
                abs(y - predicted_pending) <= tolerance
                or abs(y - self._pending_y) <= tolerance
            )
            pending_count = self._pending_count + 1 if pending_continuous else 1
            pending_velocity = y - self._pending_y if pending_continuous else None
        self._pending_y = y
        self._pending_polarity = polarity
        self._pending_velocity = pending_velocity
        self._pending_count = pending_count
        self._missing_count = 0
        self._no_interface_count = 0
        if pending_count >= max(1, int(settings.oil_reacquire_frames)):
            return self._accept(
                candidate,
                no_interface,
                best,
                second_score,
                margin,
                polarity,
                flags,
                clear=True,
                reacquired=True,
            )
        return self._decision(
            OilDecisionStatus.REACQUISITION_PENDING,
            None,
            no_interface,
            best,
            second_score,
            margin,
            "large_jump_waiting_for_consistent_new_path",
            False,
            False,
            False,
            tuple(flags + ["OIL_REACQUISITION_PENDING"]),
        )

    def _accept(
        self,
        candidate: BoundaryCandidate,
        no_interface: NoInterfaceEvidence,
        best: _Hypothesis,
        second_score: float | None,
        margin: float,
        polarity: float | None,
        flags: list[str],
        *,
        clear: bool,
        reacquired: bool,
    ) -> OilPathDecision:
        previous = self.accepted_y
        self.accepted_velocity = (
            None if previous is None or clear else float(candidate.y) - previous
        )
        self.accepted_y = float(candidate.y)
        if polarity not in (None, 0.0):
            self.accepted_polarity = polarity
        self._clear_pending()
        self._missing_count = 0
        self._no_interface_count = 0
        self._smoothing_invalidated = False
        candidate.selected = True
        candidate.rejected = False
        candidate.reject_reason = ""
        candidate.features["tracker_update_accepted"] = 1.0
        flags.append("OIL_CONSENSUS_ACCEPTED")
        if reacquired:
            flags.append("OIL_REACQUIRED")
        return self._decision(
            OilDecisionStatus.ACCEPTED_BOUNDARY,
            candidate,
            no_interface,
            best,
            second_score,
            margin,
            "reacquired_consistent_path" if reacquired else "accepted_confident_path",
            False,
            True,
            clear,
            tuple(flags),
        )

    def _no_interface_decision(
        self,
        evidence: NoInterfaceEvidence,
        settings: DetectorSettings,
        best: _Hypothesis,
        second_score: float | None,
        margin: float,
    ) -> OilPathDecision:
        if evidence.score + 1e-12 < float(settings.oil_no_interface_min_score):
            self._on_unaccepted()
            return self._decision(
                OilDecisionStatus.AMBIGUOUS,
                None,
                evidence,
                best,
                second_score,
                margin,
                "no_interface_score_below_threshold",
                True,
                False,
                False,
                ("OIL_EVIDENCE_AMBIGUOUS",),
            )
        if margin + 1e-12 < float(settings.oil_path_min_margin):
            self._on_unaccepted()
            return self._decision(
                OilDecisionStatus.LOW_MARGIN,
                None,
                evidence,
                best,
                second_score,
                margin,
                "no_interface_path_margin_below_threshold",
                True,
                False,
                False,
                ("OIL_PATH_LOW_MARGIN", "OIL_EVIDENCE_AMBIGUOUS"),
            )
        self._no_interface_count += 1
        self._missing_count = 0
        self._clear_pending()
        stable = self._no_interface_count >= max(1, int(settings.oil_reacquire_frames))
        clear = stable and (
            self.accepted_y is not None or not self._smoothing_invalidated
        )
        if stable:
            self.accepted_y = None
            self.accepted_polarity = None
            self.accepted_velocity = None
            self._smoothing_invalidated = True
        return self._decision(
            OilDecisionStatus.NO_INTERFACE_SELECTED,
            None,
            evidence,
            best,
            second_score,
            margin,
            evidence.reason,
            False,
            False,
            clear,
            ("OIL_NO_INTERFACE_SELECTED",),
        )

    def _missing_decision(
        self,
        evidence: NoInterfaceEvidence,
        settings: DetectorSettings,
        best: _Hypothesis | None,
        second_score: float | None,
        margin: float,
    ) -> OilPathDecision:
        self._missing_count += 1
        self._no_interface_count = 0
        self._clear_pending()
        clear = self._missing_count >= max(1, int(settings.oil_path_window)) and (
            self.accepted_y is not None or not self._smoothing_invalidated
        )
        if clear:
            self.accepted_y = None
            self.accepted_polarity = None
            self.accepted_velocity = None
            self._smoothing_invalidated = True
            self._beam = ()
        fallback = best or _Hypothesis(
            "missing", None, None, None, 0.0, 0.0, 0.0, None, ()
        )
        return self._decision(
            OilDecisionStatus.UNAVAILABLE,
            None,
            evidence,
            fallback,
            second_score,
            margin,
            evidence.reason,
            True,
            False,
            clear,
            ("OIL_EVIDENCE_AMBIGUOUS",),
        )

    def _on_unaccepted(self) -> None:
        self._missing_count += 1
        self._no_interface_count = 0
        self._clear_pending()

    def _clear_pending(self) -> None:
        self._pending_y = None
        self._pending_polarity = None
        self._pending_velocity = None
        self._pending_count = 0

    def _decision(
        self,
        status: OilDecisionStatus,
        candidate: BoundaryCandidate | None,
        evidence: NoInterfaceEvidence,
        best: _Hypothesis,
        second_score: float | None,
        margin: float,
        reason: str,
        ambiguous: bool,
        update: bool,
        clear: bool,
        flags: tuple[str, ...],
    ) -> OilPathDecision:
        return OilPathDecision(
            status=status,
            candidate=candidate,
            raw_y=None if candidate is None else float(candidate.y),
            boundary_score=float(evidence.boundary_score),
            no_interface_score=float(evidence.score),
            decision_margin=float(max(0.0, margin)),
            reason=reason,
            ambiguous=ambiguous,
            tracker_update_accepted=update,
            clear_smoothing=clear,
            transition_cost=float(best.transition_cost),
            path_cumulative_score=float(best.cumulative_score),
            path_second_score=None if second_score is None else float(second_score),
            path_beam_count=len(self._beam),
            path_history_length=max(
                (len(item.history) for item in self._beam),
                default=0,
            ),
            reacquisition_count=int(self._pending_count),
            accepted_prior_y=(
                None if self.accepted_y is None else float(self.accepted_y)
            ),
            accepted_polarity=(
                None if self.accepted_polarity is None else float(self.accepted_polarity)
            ),
            flags=tuple(dict.fromkeys(flags)),
        )

    @staticmethod
    def _write_path_features(
        candidates: list[BoundaryCandidate],
        hypotheses: tuple[_Hypothesis, ...],
        margin: float,
    ) -> None:
        best_for_candidate: dict[int, tuple[int, _Hypothesis]] = {}
        for rank, hypothesis in enumerate(hypotheses, 1):
            if hypothesis.kind != "boundary" or hypothesis.candidate_index is None:
                continue
            best_for_candidate.setdefault(hypothesis.candidate_index, (rank, hypothesis))
        for index, candidate in enumerate(candidates):
            rank_and_path = best_for_candidate.get(index)
            if rank_and_path is None:
                candidate.features.setdefault("path_rank", 0.0)
                candidate.features.setdefault("path_cumulative_score", 0.0)
                candidate.features.setdefault("transition_cost", 0.0)
            else:
                rank, hypothesis = rank_and_path
                candidate.features["path_rank"] = float(rank)
                candidate.features["path_cumulative_score"] = float(
                    hypothesis.cumulative_score
                )
                candidate.features["transition_cost"] = float(
                    hypothesis.transition_cost
                )
            candidate.features["best_second_path_margin"] = float(
                max(0.0, margin)
            )
            candidate.features.setdefault("tracker_update_accepted", 0.0)


def _candidate_observation(candidate: BoundaryCandidate) -> float:
    return _unit(candidate.features.get("observation_score", candidate.final_score))


def _candidate_polarity(candidate: BoundaryCandidate) -> float | None:
    if candidate.features.get("polarity_available", 0.0) < 0.5:
        return None
    value = float(candidate.features.get("polarity_sign", 0.0))
    if not math.isfinite(value) or value == 0.0:
        return None
    return 1.0 if value > 0.0 else -1.0


def _candidate_order(candidate: BoundaryCandidate) -> tuple[float, float, float, str]:
    return (
        -_candidate_observation(candidate),
        -float(candidate.features.get("unique_generator_support_count", 0.0)),
        float(candidate.y),
        str(candidate.source),
    )


def _hypothesis_order(item: _Hypothesis) -> tuple[float, int, float, int]:
    kind_order = {"boundary": 0, "no_interface": 1, "missing": 2}
    return (
        -item.cumulative_score,
        kind_order.get(item.kind, 9),
        float("inf") if item.y is None else item.y,
        -1 if item.candidate_index is None else item.candidate_index,
    )


def _unit(value: float) -> float:
    number = float(value)
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
