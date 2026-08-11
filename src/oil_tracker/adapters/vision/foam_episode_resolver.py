from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Sequence

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import GlassInspectionConfig


@dataclass(frozen=True)
class FoamEpisodeDiagnostics:
    raw_candidate_count: int
    eligible_candidate_count: int
    confirmed_frame_count: int
    episode_count: int
    rejected_static_episode_count: int
    rejected_unconfirmed_episode_count: int


@dataclass(frozen=True)
class _FoamEvidence:
    frame_offset: int
    candidate_offset: int
    candidate: BoundaryCandidate
    material_support: float
    material_bottom_y: float
    whiteness: float
    internal_motion: float
    dynamic_support: float
    static_opposition: float
    coherent: bool


class FoamEpisodeResolver:
    """Publish only explicitly eligible, materially changing Foam episodes.

    R5 read the first finite raw Foam candidate and let unregistered mask/front
    jitter override static opposition. R6 requires current-frame eligibility and
    registered internal material motion. This owner runs after Oil/state and has
    no authority to select or mask Oil.
    """

    def resolve(
        self,
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
    ) -> tuple[tuple[PhaseDetection, ...], FoamEpisodeDiagnostics]:
        source = tuple(detections)
        evidence = tuple(
            self._frame_evidence(index, detection, glass)
            for index, detection in enumerate(source)
        )
        eligible = tuple(item for item in evidence if item is not None)
        groups = _candidate_groups(eligible)
        confirmed_frames: set[int] = set()
        rejected_static_frames: set[int] = set()
        rejected_unconfirmed_frames: set[int] = set()
        episode_count = 0
        static_count = 0
        unconfirmed_count = 0
        for group in groups:
            accepted, static_dominated = _episode_accepted(group, glass)
            group_frames = {item.frame_offset for item in group}
            if accepted:
                supported = _supported_episode(group, glass)
                if supported:
                    episode_count += 1
                    confirmed_frames.update(item.frame_offset for item in supported)
                    rejected_unconfirmed_frames.update(
                        group_frames - {item.frame_offset for item in supported}
                    )
                else:
                    unconfirmed_count += 1
                    rejected_unconfirmed_frames.update(group_frames)
            elif static_dominated:
                static_count += 1
                rejected_static_frames.update(group_frames)
            else:
                unconfirmed_count += 1
                rejected_unconfirmed_frames.update(group_frames)

        resolved = tuple(
            self._project(
                detection,
                evidence[index],
                glass,
                confirmed=index in confirmed_frames,
                static_rejected=index in rejected_static_frames,
                unconfirmed_rejected=index in rejected_unconfirmed_frames,
            )
            for index, detection in enumerate(source)
        )
        raw_count = sum(
            1
            for detection in source
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.FOAM_FRONT and _finite(candidate.y)
        )
        return resolved, FoamEpisodeDiagnostics(
            raw_candidate_count=raw_count,
            eligible_candidate_count=len(eligible),
            confirmed_frame_count=len(confirmed_frames),
            episode_count=episode_count,
            rejected_static_episode_count=static_count,
            rejected_unconfirmed_episode_count=unconfirmed_count,
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
                if item.kind is BoundaryKind.FOAM_FRONT
                and _finite(item.y)
                and _unit(item.features.get("sequence_foam_eligible", 0.0)) >= 0.5
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
        optics = _unit(features.get("glare_overlap_ratio", 0.0))
        material = _unit(
            0.38 * score
            + 0.20 * texture
            + 0.10 * whiteness
            + 0.12 * area
            + 0.08 * width
            + 0.06 * fill
            + 0.06 * bottom
            - 0.30 * optics
        )
        internal_motion = _unit(
            features.get("registered_internal_motion_support", 0.0)
        )
        dynamic = _unit(features.get("registered_dynamic_support", 0.0))
        exact = _unit(features.get("static_exact_overlap", 0.0))
        tolerant = _unit(features.get("static_tolerant_overlap", exact))
        reciprocal = _unit(features.get("static_reciprocal_overlap", exact))
        static = _unit(max(exact, min(tolerant, reciprocal)))
        coherent = bool(
            _unit(
                features.get(
                    "foam_layer_coherent",
                    detection.debug_metrics.get(
                        "foam_layer_publication_coherent",
                        0.0,
                    ),
                )
            )
            >= 0.5
        )
        return _FoamEvidence(
            frame_offset=frame_offset,
            candidate_offset=candidate_offset,
            candidate=candidate,
            material_support=material,
            material_bottom_y=float(
                features.get("material_component_bottom_y", candidate.y)
            ),
            whiteness=whiteness,
            internal_motion=internal_motion,
            dynamic_support=dynamic,
            static_opposition=static,
            coherent=coherent,
        )

    def _project(
        self,
        detection: PhaseDetection,
        evidence: _FoamEvidence | None,
        glass: GlassInspectionConfig,
        *,
        confirmed: bool,
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
                "FOAM_SEQUENCE_CONFIRMED",
            }
        ]
        candidates = [
            replace(
                candidate,
                selected=False,
                rejected=True,
                reject_reason=(
                    candidate.reject_reason
                    or "not_confirmed_by_r6_foam_episode"
                ),
            )
            if candidate.kind is BoundaryKind.FOAM_FRONT
            else candidate
            for candidate in detection.candidates
        ]
        metrics = dict(detection.debug_metrics)
        metrics.update(
            {
                "r6_foam_episode_confirmed": bool(confirmed),
                "r6_foam_internal_motion_support": (
                    0.0 if evidence is None else float(evidence.internal_motion)
                ),
                "r6_foam_dynamic_support": (
                    0.0 if evidence is None else float(evidence.dynamic_support)
                ),
            }
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
            debug_metrics=metrics,
        )
        if static_rejected:
            flags.append("R6_FOAM_STATIC_ARTIFACT_REJECTED")
        elif unconfirmed_rejected:
            flags.append("R6_FOAM_UNCONFIRMED")

        topology_conflict = bool(
            confirmed
            and evidence is not None
            and evidence.whiteness >= 0.55
            and base.oil_air_level_y is not None
            and float(base.oil_air_level_y) <= evidence.material_bottom_y
        )
        if topology_conflict:
            flags.append("R6_FOAM_OIL_TOPOLOGY_CONFLICT")
            conflicted_candidates = [
                replace(
                    candidate,
                    selected=False,
                    rejected=True,
                    reject_reason="r6_confirmed_foam_oil_topology_conflict",
                )
                if candidate.kind in {BoundaryKind.OIL_AIR, BoundaryKind.FOAM_FRONT}
                else candidate
                for candidate in base.candidates
            ]
            return replace(
                base,
                fill_state=FillState.UNKNOWN_REVIEW,
                oil_air_level_y=None,
                oil_air_level_px_from_zero=None,
                oil_air_level_mm_from_zero=None,
                oil_air_confidence=0.0,
                overall_confidence=min(base.overall_confidence, 0.40),
                raw_oil_air_level_y=None,
                smoothed_oil_air_level_y=None,
                candidates=conflicted_candidates,
                flags=sorted(set(flags)),
            )

        state_known = base.fill_state in {
            FillState.FULL_NO_INTERFACE,
            FillState.FILLING_VISIBLE,
            FillState.PARTIAL_VISIBLE,
            FillState.DRAINING_VISIBLE,
        }
        if not confirmed or evidence is None or not state_known:
            return replace(base, flags=sorted(set(flags)))

        y = float(evidence.candidate.y)
        zero = glass.geometry.zero_line_y
        px = None if zero is None else float(zero) - y
        mm = None if px is None or glass.mm_per_pixel is None else px * glass.mm_per_pixel
        confidence = min(
            0.96,
            max(
                0.45,
                0.45
                + 0.38 * evidence.material_support
                + 0.24 * evidence.internal_motion
                - 0.22 * evidence.static_opposition,
            ),
        )
        selected_candidates: list[BoundaryCandidate] = []
        for offset, candidate in enumerate(base.candidates):
            if candidate.kind is not BoundaryKind.FOAM_FRONT:
                selected_candidates.append(candidate)
                continue
            selected = offset == evidence.candidate_offset
            selected_candidates.append(
                replace(
                    candidate,
                    selected=selected,
                    rejected=not selected,
                    reject_reason="" if selected else candidate.reject_reason,
                )
            )
        composed = (
            FillState.FULL_WITH_FOAM
            if base.fill_state is FillState.FULL_NO_INTERFACE
            else FillState.FOAMING_VISIBLE
        )
        flags.extend(("R6_FOAM_EPISODE_CONFIRMED", "FOAM_STRONG_EVIDENCE"))
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


def _candidate_groups(
    evidence: tuple[_FoamEvidence, ...],
) -> tuple[tuple[_FoamEvidence, ...], ...]:
    if not evidence:
        return ()
    groups: list[list[_FoamEvidence]] = []
    current: list[_FoamEvidence] = []
    for item in evidence:
        if not current:
            current = [item]
            continue
        prior = current[-1]
        frame_gap = item.frame_offset - prior.frame_offset
        if 0 < frame_gap <= 2:
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
        return False, bool(group and group[0].static_opposition >= 0.65)
    material = sum(item.material_support for item in group) / len(group)
    coherent_ratio = sum(item.coherent for item in group) / len(group)
    static = sum(item.static_opposition for item in group) / len(group)
    dynamic_frames = sum(item.internal_motion >= 0.15 for item in group)
    supported_dynamic = tuple(
        item.dynamic_support
        for item in group
        if item.internal_motion >= 0.15
    )
    dynamic = (
        0.0
        if not supported_dynamic
        else sum(supported_dynamic) / len(supported_dynamic)
    )
    strong_dynamic_frames = sum(item.internal_motion >= 0.20 for item in group)
    static_dominated = bool(
        static >= 0.65
        and (strong_dynamic_frames < 2 or max(item.internal_motion for item in group) < 0.28)
    )
    required_material = max(
        0.30,
        float(glass.detector_settings.foam_min_evidence_score) * 0.72,
    )
    accepted = bool(
        not static_dominated
        and material >= required_material
        and coherent_ratio >= 0.60
        and dynamic >= 0.12
        and dynamic_frames >= 1
    )
    return accepted, static_dominated


def _supported_episode(
    group: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[_FoamEvidence, ...]:
    activation = [
        index
        for index, item in enumerate(group)
        if item.internal_motion >= 0.15
    ]
    if not activation:
        return ()
    first = activation[0]
    last = min(len(group) - 1, activation[-1] + 1)
    maximum_jump = max(
        1.0,
        float(glass.detector_settings.foam_max_front_jump_px),
    )
    supported: list[_FoamEvidence] = []
    for item in group[first : last + 1]:
        if not supported:
            supported.append(item)
            continue
        frame_gap = item.frame_offset - supported[-1].frame_offset
        jump = abs(float(item.candidate.y) - float(supported[-1].candidate.y))
        if jump <= maximum_jump * max(1, frame_gap):
            supported.append(item)
    return tuple(supported)


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
