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
    rejected_oil_alias_episode_count: int


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

    R7 requires current-frame eligibility plus multi-frame registered internal
    material evolution. This owner runs after Oil/state and has no authority to
    select or mask Oil.
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
        rejected_oil_alias_frames: set[int] = set()
        episode_count = 0
        static_count = 0
        unconfirmed_count = 0
        oil_alias_count = 0
        oil_alias_tracks: list[tuple[int, float]] = []
        for group in groups:
            group_frames = {item.frame_offset for item in group}
            onset_groups = _dynamic_onset_groups(group)
            rejected_unconfirmed_frames.update(group_frames)
            accepted_any = False
            static_dominated_any = False
            oil_alias_any = False
            alias_group_frames: set[int] = set()
            for onset in onset_groups or (group,):
                accepted, static_dominated = _episode_accepted(onset, glass)
                static_dominated_any = static_dominated_any or static_dominated
                if not accepted:
                    continue
                supported = _supported_episode(onset, glass)
                if supported:
                    if _episode_aliases_oil(
                        supported,
                        source,
                        glass,
                    ) or _episode_continues_oil_alias(
                        supported,
                        oil_alias_tracks,
                        source,
                        glass,
                    ):
                        oil_alias_any = True
                        alias_frames = {
                            item.frame_offset for item in supported
                        }
                        alias_group_frames.update(alias_frames)
                        rejected_oil_alias_frames.update(alias_frames)
                        oil_alias_tracks.append(
                            (
                                supported[-1].frame_offset,
                                float(supported[-1].candidate.y),
                            )
                        )
                        continue
                    accepted_any = True
                    episode_count += 1
                    confirmed_frames.update(item.frame_offset for item in supported)
                    rejected_unconfirmed_frames.difference_update(
                        item.frame_offset for item in supported
                    )
            if accepted_any:
                continue
            if oil_alias_any:
                oil_alias_count += 1
                rejected_unconfirmed_frames.difference_update(alias_group_frames)
                continue
            if static_dominated_any:
                static_count += 1
                rejected_static_frames.update(group_frames)
                rejected_unconfirmed_frames.difference_update(group_frames)
            else:
                unconfirmed_count += 1

        resolved = tuple(
            self._project(
                detection,
                evidence[index],
                glass,
                confirmed=index in confirmed_frames,
                static_rejected=index in rejected_static_frames,
                unconfirmed_rejected=index in rejected_unconfirmed_frames,
                oil_alias_rejected=index in rejected_oil_alias_frames,
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
            rejected_oil_alias_episode_count=oil_alias_count,
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
        oil_alias_rejected: bool,
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
                "R6_FOAM_EPISODE_CONFIRMED",
                "R6_FOAM_OIL_TOPOLOGY_CONFLICT",
                "R6_FOAM_STATIC_ARTIFACT_REJECTED",
                "R6_FOAM_UNCONFIRMED",
                "R7_FOAM_EPISODE_CONFIRMED",
                "R7_FOAM_OIL_TOPOLOGY_CONFLICT",
                "R7_FOAM_STATIC_ARTIFACT_REJECTED",
                "R7_FOAM_UNCONFIRMED",
                "R8_FOAM_EPISODE_CONFIRMED",
                "R8_FOAM_EVIDENCE_PRESERVED",
                "R8_FOAM_WITHOUT_RESOLVED_OIL_STATE",
                "R8_FOAM_EMPTY_STATE_CONFLICT",
                "R8_FOAM_OIL_TOPOLOGY_CONFLICT",
                "R8_FOAM_OIL_ALIAS_REJECTED",
            }
        ]
        candidates = [
            replace(
                candidate,
                selected=False,
                rejected=True,
                reject_reason=(
                    candidate.reject_reason
                    or "not_confirmed_by_r7_foam_episode"
                ),
            )
            if candidate.kind is BoundaryKind.FOAM_FRONT
            else candidate
            for candidate in detection.candidates
        ]
        metrics = dict(detection.debug_metrics)
        metrics.update(
            {
                "r7_foam_episode_confirmed": bool(confirmed),
                "r7_foam_internal_motion_support": (
                    0.0 if evidence is None else float(evidence.internal_motion)
                ),
                "r7_foam_dynamic_support": (
                    0.0 if evidence is None else float(evidence.dynamic_support)
                ),
                "r8_foam_evidence_preserved": bool(
                    confirmed and evidence is not None
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
            flags.append("R7_FOAM_STATIC_ARTIFACT_REJECTED")
        elif oil_alias_rejected:
            flags.append("R8_FOAM_OIL_ALIAS_REJECTED")
        elif unconfirmed_rejected:
            flags.append("R7_FOAM_UNCONFIRMED")

        if not confirmed or evidence is None:
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
        topology_conflict = bool(
            evidence.whiteness >= 0.55
            and base.oil_air_level_y is not None
            and float(base.oil_air_level_y) <= evidence.material_bottom_y
        )
        if topology_conflict:
            composed = FillState.UNKNOWN_REVIEW
            flags.extend(
                (
                    "R7_FOAM_OIL_TOPOLOGY_CONFLICT",
                    "R8_FOAM_OIL_TOPOLOGY_CONFLICT",
                )
            )
        elif base.fill_state in {
            FillState.FULL_NO_INTERFACE,
            FillState.FULL_WITH_FOAM,
        }:
            composed = FillState.FULL_WITH_FOAM
        elif base.fill_state in {
            FillState.FILLING_VISIBLE,
            FillState.PARTIAL_VISIBLE,
            FillState.DRAINING_VISIBLE,
            FillState.FOAMING_VISIBLE,
        }:
            composed = FillState.FOAMING_VISIBLE
        elif base.fill_state is FillState.EMPTY_NO_INTERFACE:
            composed = FillState.UNKNOWN_REVIEW
            flags.append("R8_FOAM_EMPTY_STATE_CONFLICT")
        else:
            composed = FillState.UNKNOWN_REVIEW
            flags.append("R8_FOAM_WITHOUT_RESOLVED_OIL_STATE")
        flags.extend(
            (
                "R7_FOAM_EPISODE_CONFIRMED",
                "R8_FOAM_EPISODE_CONFIRMED",
                "R8_FOAM_EVIDENCE_PRESERVED",
                "FOAM_STRONG_EVIDENCE",
            )
        )
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
            overall_confidence=(
                min(0.40, max(base.overall_confidence, confidence * 0.50))
                if composed is FillState.UNKNOWN_REVIEW
                else max(base.overall_confidence, confidence * 0.85)
            ),
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


def _dynamic_onset_groups(
    group: tuple[_FoamEvidence, ...],
) -> tuple[tuple[_FoamEvidence, ...], ...]:
    dynamic = tuple(
        item
        for item in group
        if min(item.internal_motion, item.dynamic_support) >= 0.15
    )
    if not dynamic:
        return ()
    clusters: list[list[_FoamEvidence]] = [[dynamic[0]]]
    for item in dynamic[1:]:
        if item.frame_offset - clusters[-1][-1].frame_offset <= 2:
            clusters[-1].append(item)
        else:
            clusters.append([item])
    output: list[tuple[_FoamEvidence, ...]] = []
    for cluster in clusters:
        first = cluster[0].frame_offset
        last = cluster[-1].frame_offset
        selected = [
            item
            for item in group
            if first <= item.frame_offset <= last
        ]
        following = next(
            (
                item
                for item in group
                if item.frame_offset > last
                and item.frame_offset - last <= 2
            ),
            None,
        )
        if following is not None:
            selected.append(following)
        output.append(tuple(selected))
    return tuple(output)


def _episode_accepted(
    group: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[bool, bool]:
    if len(group) < 2:
        return False, bool(group and group[0].static_opposition >= 0.65)
    material = sum(item.material_support for item in group) / len(group)
    coherent_ratio = sum(item.coherent for item in group) / len(group)
    static = sum(item.static_opposition for item in group) / len(group)
    registered_evolution = tuple(
        min(item.internal_motion, item.dynamic_support)
        for item in group
    )
    dynamic_frames = sum(value >= 0.15 for value in registered_evolution)
    dynamic = sum(registered_evolution) / len(registered_evolution)
    dynamic_frame_ratio = dynamic_frames / len(group)
    strong_dynamic_frames = sum(value >= 0.20 for value in registered_evolution)
    static_dominated = bool(
        static >= 0.65
        and (strong_dynamic_frames < 2 or max(registered_evolution) < 0.28)
    )
    required_material = max(
        0.30,
        float(glass.detector_settings.foam_min_evidence_score) * 0.72,
    )
    accepted = bool(
        not static_dominated
        and material >= required_material
        and coherent_ratio >= 0.60
        and dynamic >= 0.10
        and dynamic_frames >= 2
        and dynamic_frame_ratio >= 0.50
    )
    return accepted, static_dominated


def _supported_episode(
    group: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[_FoamEvidence, ...]:
    activation = [
        index
        for index, item in enumerate(group)
        if min(item.internal_motion, item.dynamic_support) >= 0.15
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


def _episode_aliases_oil(
    group: tuple[_FoamEvidence, ...],
    detections: tuple[PhaseDetection, ...],
    glass: GlassInspectionConfig,
) -> bool:
    """Reject a Foam track repeatedly coincident with same-frame Oil."""

    matched = _same_frame_oil_alias_matches(group, detections, glass)
    required = min(2, len(group))
    return required > 0 and matched >= required


def _same_frame_oil_alias_matches(
    group: tuple[_FoamEvidence, ...],
    detections: tuple[PhaseDetection, ...],
    glass: GlassInspectionConfig,
) -> int:
    """Count current-frame Oil rows that actually coincide with Foam."""

    tolerance = max(
        10.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.65,
    )
    matched = 0
    for evidence in group:
        detection = detections[evidence.frame_offset]
        oil_rows = [
            float(candidate.y)
            for candidate in detection.candidates
            if candidate.kind is BoundaryKind.OIL_AIR
            and _finite(candidate.y)
            and _unit(
                candidate.features.get(
                    "boundary_likelihood",
                    candidate.feature_score,
                )
            )
            >= 0.90
            and _unit(
                candidate.features.get(
                    "artifact_likelihood",
                    candidate.penalties.get("artifact_likelihood", 0.0),
                )
            )
            <= 0.46
        ]
        if _finite(detection.raw_oil_air_level_y):
            oil_rows.append(float(detection.raw_oil_air_level_y))
        if oil_rows and min(
            abs(float(evidence.candidate.y) - oil_y)
            for oil_y in oil_rows
        ) <= tolerance:
            matched += 1
    return matched


def _episode_continues_oil_alias(
    group: tuple[_FoamEvidence, ...],
    aliases: list[tuple[int, float]],
    detections: tuple[PhaseDetection, ...],
    glass: GlassInspectionConfig,
) -> bool:
    if not group or not aliases:
        return False
    # A prior rejected alias is context, never evidence for the next group.
    # Require at least one current same-frame Oil coincidence before bridging
    # a short dropout.  Otherwise a real Foam front that separates from Oil
    # (or appears while Oil is unavailable) would be suppressed indefinitely.
    if _same_frame_oil_alias_matches(group, detections, glass) < 1:
        return False
    horizon = max(4, int(glass.detector_settings.oil_path_window) * 2)
    tolerance = max(
        10.0,
        float(glass.detector_settings.temporal_max_jump_px) * 0.65,
    )
    first_frame = group[0].frame_offset
    return any(
        0 < first_frame - alias_frame <= horizon
        and min(
            abs(float(item.candidate.y) - alias_y)
            for item in group
        )
        <= tolerance
        for alias_frame, alias_y in aliases
    )


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
