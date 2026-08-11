from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Sequence

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import GlassInspectionConfig


@dataclass(frozen=True)
class FoamAdjacentEvidence:
    available: bool = False
    exact_overlap: float = 0.0
    tolerant_overlap: float = 0.0
    reciprocal_overlap: float = 0.0
    mask_turnover: float = 0.0
    area_change_ratio: float = 0.0
    front_delta_ratio: float = 0.0
    dynamic_support: float = 0.0


@dataclass(frozen=True)
class FoamSequenceDiagnostics:
    raw_candidate_count: int
    confirmed_frame_count: int
    bridged_frame_count: int
    episode_count: int
    rejected_static_episode_count: int
    rejected_unconfirmed_episode_count: int


@dataclass
class _AdjacentState:
    mask: np.ndarray
    front_y: float | None


@dataclass(frozen=True)
class _FoamEvidence:
    frame_offset: int
    candidate_offset: int
    candidate: BoundaryCandidate
    material_support: float
    dynamic_support: float
    static_opposition: float
    coherent: bool


class FoamAdjacentEvidenceTracker:
    """Retain one prior raw Foam mask per Glass for bounded change evidence."""

    def __init__(self) -> None:
        self._states: dict[str, _AdjacentState] = {}

    @property
    def state_count(self) -> int:
        return len(self._states)

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._states.clear()
        else:
            self._states.pop(str(glass_id), None)

    def evaluate(
        self,
        glass_id: str,
        mask: np.ndarray,
        front_y: float | None,
    ) -> FoamAdjacentEvidence:
        current = np.asarray(mask) > 0
        prior = self._states.get(str(glass_id))
        evidence = FoamAdjacentEvidence()
        if prior is not None and prior.mask.shape == current.shape:
            evidence = _adjacent_evidence(
                prior.mask,
                current,
                prior.front_y,
                front_y,
            )
        owned = np.array(current, copy=True)
        owned.setflags(write=False)
        self._states[str(glass_id)] = _AdjacentState(
            owned,
            None if front_y is None else float(front_y),
        )
        return evidence


class SequenceFoamEpisodeResolver:
    """Resolve public Foam after the Oil/FULL/EMPTY sequence is fixed."""

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[PhaseDetection, ...], FoamSequenceDiagnostics]:
        source = tuple(detections)
        evidence = tuple(self._frame_evidence(index, detection, glass) for index, detection in enumerate(source))
        raw = tuple(item for item in evidence if item is not None)
        groups = _candidate_groups(raw, glass)
        confirmed_frames: set[int] = set()
        bridged_frames: set[int] = set()
        static_rejections: set[int] = set()
        unconfirmed_rejections: set[int] = set()
        accepted_episode_count = 0
        rejected_static_episode_count = 0
        rejected_unconfirmed_episode_count = 0
        for group in groups:
            accepted, static_dominated = _episode_accepted(group, glass)
            group_frames = {item.frame_offset for item in group}
            if accepted:
                episode = _bounded_episode_evidence(group, glass)
                episode_frames = {item.frame_offset for item in episode}
                accepted_episode_count += 1
                confirmed_frames.update(episode_frames)
                unconfirmed_rejections.update(group_frames - episode_frames)
                first = min(episode_frames)
                last = max(episode_frames)
                for frame_offset in range(first, last + 1):
                    if frame_offset not in episode_frames:
                        bridged_frames.add(frame_offset)
            elif static_dominated:
                rejected_static_episode_count += 1
                static_rejections.update(group_frames)
            else:
                rejected_unconfirmed_episode_count += 1
                unconfirmed_rejections.update(group_frames)

        resolved = tuple(
            self._project(
                detection,
                evidence[index],
                glass,
                confirmed=index in confirmed_frames,
                bridged=index in bridged_frames,
                static_rejected=index in static_rejections,
                unconfirmed_rejected=index in unconfirmed_rejections,
            )
            for index, detection in enumerate(source)
        )
        return resolved, FoamSequenceDiagnostics(
            raw_candidate_count=len(raw),
            confirmed_frame_count=len(confirmed_frames),
            bridged_frame_count=len(bridged_frames),
            episode_count=accepted_episode_count,
            rejected_static_episode_count=rejected_static_episode_count,
            rejected_unconfirmed_episode_count=rejected_unconfirmed_episode_count,
        )

    def _frame_evidence(
        self,
        frame_offset: int,
        detection: PhaseDetection,
        glass: GlassInspectionConfig,
    ) -> _FoamEvidence | None:
        candidate_offset, candidate = next(
            (
                (offset, item)
                for offset, item in enumerate(detection.candidates)
                if item.kind is BoundaryKind.FOAM_FRONT and _finite(item.y)
            ),
            (-1, None),
        )
        if candidate is None:
            return None
        features = candidate.features
        score = _unit(features.get("foam_score", candidate.feature_score))
        texture = _unit(features.get("texture_support_ratio", 0.0))
        whiteness = _unit(features.get("whiteness_ratio", 0.0))
        area = _unit(
            features.get(
                "area_ratio",
                detection.debug_metrics.get("foam_bottom_connected_area_ratio", 0.0),
            )
            / max(0.01, float(glass.detector_settings.foam_min_area_ratio) * 3.0)
        )
        width = _unit(features.get("component_width_ratio", 0.0))
        fill = _unit(features.get("bounding_box_fill_ratio", 0.0))
        bottom = _unit(features.get("bottom_connectivity", 0.0))
        glare = _unit(features.get("glare_overlap_ratio", 0.0))
        material = _unit(
            0.40 * score
            + 0.18 * texture
            + 0.10 * whiteness
            + 0.12 * area
            + 0.08 * width
            + 0.06 * fill
            + 0.06 * bottom
            - 0.25 * glare
        )
        dynamic = _unit(
            max(
                features.get("adjacent_dynamic_support", 0.0),
                features.get("adjacent_mask_turnover", 0.0),
                features.get("adjacent_area_change_ratio", 0.0),
                features.get("adjacent_front_delta_ratio", 0.0),
            )
        )
        exact = _unit(features.get("static_exact_overlap", 0.0))
        tolerant = _unit(features.get("static_tolerant_overlap", exact))
        reciprocal = _unit(features.get("static_reciprocal_overlap", exact))
        static = _unit(
            max(
                exact,
                min(tolerant, reciprocal),
            )
        )
        coherent = bool(
            detection.debug_metrics.get("foam_layer_publication_coherent", False)
        )
        return _FoamEvidence(
            frame_offset,
            candidate_offset,
            candidate,
            material,
            dynamic,
            static,
            coherent,
        )

    def _project(
        self,
        detection: PhaseDetection,
        evidence: _FoamEvidence | None,
        glass: GlassInspectionConfig,
        *,
        confirmed: bool,
        bridged: bool,
        static_rejected: bool,
        unconfirmed_rejected: bool,
    ) -> PhaseDetection:
        flags = [
            flag
            for flag in detection.flags
            if flag
            not in {
                "FOAM_MODERATE_EVIDENCE",
                "FOAM_PERSISTENCE_PENDING",
                "FOAM_REACH_TOP",
                "FOAM_STRONG_EVIDENCE",
            }
        ]
        candidates = list(detection.candidates)
        for offset, candidate in enumerate(candidates):
            if candidate.kind is BoundaryKind.FOAM_FRONT:
                candidates[offset] = replace(
                    candidate,
                    selected=False,
                    rejected=True,
                    reject_reason=(
                        candidate.reject_reason or "not_confirmed_by_sequence_foam"
                    ),
                )
        base = replace(
            detection,
            foam_front_y=None,
            foam_front_px_from_zero=None,
            foam_front_mm_from_zero=None,
            foam_confidence=0.0,
            raw_foam_front_y=None,
            smoothed_foam_front_y=None,
            candidates=candidates,
        )
        if static_rejected:
            flags.append("FOAM_SEQUENCE_STATIC_ARTIFACT_REJECTED")
        elif unconfirmed_rejected:
            flags.append("FOAM_SEQUENCE_UNCONFIRMED")

        state_known = base.fill_state in {
            FillState.FULL_NO_INTERFACE,
            FillState.FILLING_VISIBLE,
            FillState.PARTIAL_VISIBLE,
            FillState.DRAINING_VISIBLE,
        }
        if bridged and state_known:
            flags.extend(("FOAM_PERSISTENCE_PENDING", "FOAM_SEQUENCE_EPISODE_GAP"))
            composed = (
                FillState.FULL_WITH_FOAM
                if base.fill_state is FillState.FULL_NO_INTERFACE
                else FillState.FOAMING_VISIBLE
            )
            return replace(base, fill_state=composed, flags=sorted(set(flags)))
        if not confirmed or evidence is None or not state_known:
            return replace(base, flags=sorted(set(flags)))

        candidate = evidence.candidate
        y = float(candidate.y)
        zero = glass.geometry.zero_line_y
        px = None if zero is None else float(zero) - y
        mm = None if px is None or glass.mm_per_pixel is None else px * glass.mm_per_pixel
        confidence = min(
            0.96,
            max(0.45, 0.48 + 0.42 * evidence.material_support + 0.12 * evidence.dynamic_support - 0.18 * evidence.static_opposition),
        )
        selected_candidates = []
        for offset, item in enumerate(base.candidates):
            if item.kind is not BoundaryKind.FOAM_FRONT:
                selected_candidates.append(item)
                continue
            selected = offset == evidence.candidate_offset
            selected_candidates.append(
                replace(
                    item,
                    selected=selected,
                    rejected=not selected,
                    reject_reason="" if selected else item.reject_reason,
                )
            )
        composed = (
            FillState.FULL_WITH_FOAM
            if base.fill_state is FillState.FULL_NO_INTERFACE
            else FillState.FOAMING_VISIBLE
        )
        flags.extend(("FOAM_SEQUENCE_CONFIRMED", "FOAM_STRONG_EVIDENCE"))
        top = glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
        bottom = glass.geometry.ellipse.center_y + glass.geometry.ellipse.radius_y
        if (y - top) / max(1.0, bottom - top) <= 0.12:
            flags.append("FOAM_REACH_TOP")
        return replace(
            base,
            fill_state=composed,
            foam_front_y=y,
            foam_front_px_from_zero=px,
            foam_front_mm_from_zero=mm,
            foam_confidence=confidence,
            overall_confidence=max(base.overall_confidence, confidence * 0.85),
            raw_foam_front_y=y,
            smoothed_foam_front_y=y,
            candidates=selected_candidates,
            flags=sorted(set(flags)),
        )


def _adjacent_evidence(
    prior: np.ndarray,
    current: np.ndarray,
    prior_front_y: float | None,
    current_front_y: float | None,
) -> FoamAdjacentEvidence:
    prior_count = int(np.count_nonzero(prior))
    current_count = int(np.count_nonzero(current))
    if prior_count == 0 or current_count == 0:
        return FoamAdjacentEvidence()
    radius = max(1, min(3, int(round(min(current.shape[:2]) * 0.01))))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    dilated_prior = cv2.dilate(prior.astype(np.uint8), kernel) > 0
    dilated_current = cv2.dilate(current.astype(np.uint8), kernel) > 0
    intersection = int(np.count_nonzero(prior & current))
    union = int(np.count_nonzero(prior | current))
    exact = intersection / max(1, union)
    tolerant = float(np.count_nonzero(current & dilated_prior)) / current_count
    reciprocal = float(np.count_nonzero(prior & dilated_current)) / prior_count
    turnover = _unit(1.0 - min(tolerant, reciprocal))
    area_change = _unit(abs(current_count - prior_count) / max(prior_count, current_count))
    front_delta = 0.0
    if prior_front_y is not None and current_front_y is not None:
        front_delta = _unit(abs(float(current_front_y) - float(prior_front_y)) / max(1.0, current.shape[0] * 0.15))
    dynamic = _unit(max(turnover, area_change, front_delta))
    return FoamAdjacentEvidence(
        available=True,
        exact_overlap=exact,
        tolerant_overlap=tolerant,
        reciprocal_overlap=reciprocal,
        mask_turnover=turnover,
        area_change_ratio=area_change,
        front_delta_ratio=front_delta,
        dynamic_support=dynamic,
    )


def _candidate_groups(
    evidence: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[tuple[_FoamEvidence, ...], ...]:
    if not evidence:
        return ()
    maximum_jump = max(1.0, float(glass.detector_settings.foam_max_front_jump_px) * 1.5)
    groups: list[list[_FoamEvidence]] = []
    current: list[_FoamEvidence] = []
    for item in evidence:
        if not current:
            current = [item]
            continue
        prior = current[-1]
        frame_gap = item.frame_offset - prior.frame_offset
        front_jump = abs(float(item.candidate.y) - float(prior.candidate.y))
        if frame_gap <= 2 and front_jump <= maximum_jump * max(1, frame_gap):
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    if current:
        groups.append(current)
    return tuple(tuple(group) for group in groups)


def _episode_accepted(
    group: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[bool, bool]:
    if len(group) < 2:
        static = bool(group and group[0].static_opposition >= 0.70)
        return False, static
    material = sum(item.material_support for item in group) / len(group)
    dynamic = sum(item.dynamic_support for item in group) / len(group)
    coherent_ratio = sum(item.coherent for item in group) / len(group)
    static = sum(item.static_opposition for item in group) / len(group)
    fronts = tuple(float(item.candidate.y) for item in group)
    front_range = max(fronts) - min(fronts)
    scores = tuple(_unit(item.candidate.features.get("foam_score", item.candidate.feature_score)) for item in group)
    score_range = max(scores) - min(scores)
    height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    dynamic_episode = (
        dynamic >= 0.055
        or front_range >= max(3.0, height * 0.025)
        or score_range >= 0.055
    )
    static_dominated = static >= 0.72 and not (
        dynamic >= 0.15 or front_range >= height * 0.06
    )
    required_material = max(0.30, float(glass.detector_settings.foam_min_evidence_score) * 0.72)
    accepted = (
        not static_dominated
        and material >= required_material
        and coherent_ratio >= 0.50
        and dynamic_episode
    )
    return accepted, static_dominated


def _bounded_episode_evidence(
    group: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[_FoamEvidence, ...]:
    """Exclude a static prelude and an unbounded static tail from an episode.

    A raw component has no adjacent-frame evidence on its first appearance.  The
    public onset therefore begins at the first independently observed change,
    while one following component is retained as bounded persistence support.
    """

    if len(group) < 2:
        return group
    height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    front_change = max(3.0, height * 0.025)
    activation: list[int] = []
    for index, item in enumerate(group):
        if item.dynamic_support >= 0.055:
            activation.append(index)
            continue
        if index == 0:
            continue
        prior = group[index - 1]
        score = _unit(
            item.candidate.features.get("foam_score", item.candidate.feature_score)
        )
        prior_score = _unit(
            prior.candidate.features.get(
                "foam_score",
                prior.candidate.feature_score,
            )
        )
        if (
            abs(float(item.candidate.y) - float(prior.candidate.y)) >= front_change
            or abs(score - prior_score) >= 0.055
        ):
            activation.append(index)
    if not activation:
        return group
    first = activation[0]
    last = min(len(group) - 1, activation[-1] + 1)
    return group[first : last + 1]


def adjacent_evidence_features(evidence: FoamAdjacentEvidence) -> dict[str, float]:
    return {
        "adjacent_evidence_available": float(evidence.available),
        "adjacent_exact_overlap": float(evidence.exact_overlap),
        "adjacent_tolerant_overlap": float(evidence.tolerant_overlap),
        "adjacent_reciprocal_overlap": float(evidence.reciprocal_overlap),
        "adjacent_mask_turnover": float(evidence.mask_turnover),
        "adjacent_area_change_ratio": float(evidence.area_change_ratio),
        "adjacent_front_delta_ratio": float(evidence.front_delta_ratio),
        "adjacent_dynamic_support": float(evidence.dynamic_support),
    }


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _unit(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return min(1.0, max(0.0, number))
