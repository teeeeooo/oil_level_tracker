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
    time_sec: float
    oil_y: float | None
    candidate_offset: int
    candidate: BoundaryCandidate
    material_support: float
    material_bottom_y: float
    area_ratio: float
    width_ratio: float
    internal_motion: float
    dynamic_support: float
    static_opposition: float
    coherent: bool


@dataclass(frozen=True)
class _OilFoamRelation:
    kind: str
    oil_y: float | None
    separation: float | None

    @property
    def aliases(self) -> bool:
        return self.kind == "same_boundary"

    @property
    def inverted(self) -> bool:
        return self.kind == "inverted_topology"


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
        tracks = _foam_front_tracks(eligible, glass)
        confirmed_frames: set[int] = set()
        rejected_static_frames: set[int] = set()
        rejected_unconfirmed_frames: set[int] = set()
        rejected_oil_alias_frames: set[int] = set()
        episode_count = 0
        static_count = 0
        unconfirmed_count = 0
        oil_alias_count = 0
        for track in tracks:
            track_frames = {item.frame_offset for item in track}
            segments = _foam_confirmation_segments(track)
            rejected_unconfirmed_frames.update(track_frames)
            accepted_any = False
            static_dominated_any = _foam_track_static_dominated(track)
            oil_alias_any = False
            alias_group_frames: set[int] = set()
            for segment in segments:
                if _episode_aliases_oil(segment, source, glass):
                    oil_alias_any = True
                    alias_frames = {item.frame_offset for item in segment}
                    alias_group_frames.update(alias_frames)
                    rejected_oil_alias_frames.update(alias_frames)
                    continue
                if not _foam_segment_accepted(segment, glass):
                    continue
                accepted_any = True
                episode_count += 1
                confirmed_frames.update(item.frame_offset for item in segment)
                rejected_unconfirmed_frames.difference_update(
                    item.frame_offset for item in segment
                )
            if accepted_any:
                if oil_alias_any:
                    oil_alias_count += 1
                continue
            if oil_alias_any:
                oil_alias_count += 1
                rejected_unconfirmed_frames.difference_update(alias_group_frames)
                continue
            if static_dominated_any:
                static_count += 1
                rejected_static_frames.update(track_frames)
                rejected_unconfirmed_frames.difference_update(track_frames)
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
            time_sec=float(detection.time_sec),
            oil_y=(
                float(detection.raw_oil_air_level_y)
                if _finite(detection.raw_oil_air_level_y)
                else None
            ),
            candidate_offset=candidate_offset,
            candidate=candidate,
            material_support=material,
            material_bottom_y=float(
                features.get("material_component_bottom_y", candidate.y)
            ),
            area_ratio=_unit(features.get("area_ratio", 0.0)),
            width_ratio=width,
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
                "R10_FOAM_LAYER_SEPARATED",
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
        identity_tolerance = _oil_foam_identity_tolerance(glass)
        relation = _oil_foam_relation(evidence, detection, glass)
        source_oil_y = (
            detection.raw_oil_air_level_y
            if _finite(detection.raw_oil_air_level_y)
            else detection.oil_air_level_y
        )
        oil_foam_separation = (
            None
            if evidence is None or not _finite(source_oil_y)
            else float(source_oil_y) - float(evidence.candidate.y)
        )
        metrics.update(
            {
                "foam_episode_confirmed": bool(confirmed),
                "foam_internal_motion_support": (
                    0.0 if evidence is None else float(evidence.internal_motion)
                ),
                "foam_dynamic_support": (
                    0.0 if evidence is None else float(evidence.dynamic_support)
                ),
                "foam_evidence_preserved": bool(
                    confirmed and evidence is not None
                ),
                "foam_oil_identity_tolerance_px": identity_tolerance,
                "foam_oil_layer_separation_px": oil_foam_separation,
                "foam_oil_relation": relation.kind,
                "foam_oil_alias_match": relation.aliases,
                "foam_oil_matched_y": relation.oil_y,
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
        topology_conflict = relation.inverted
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
        } or _finite(base.oil_air_level_y):
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
        if (
            oil_foam_separation is not None
            and oil_foam_separation > identity_tolerance
        ):
            flags.append("R10_FOAM_LAYER_SEPARATED")
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


def _foam_front_tracks(
    evidence: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> tuple[tuple[_FoamEvidence, ...], ...]:
    if not evidence:
        return ()
    maximum_jump = max(
        1.0,
        float(glass.detector_settings.foam_max_front_jump_px),
    )
    groups: list[list[_FoamEvidence]] = []
    current: list[_FoamEvidence] = []
    for item in evidence:
        if not current:
            current = [item]
            continue
        prior = current[-1]
        frame_gap = item.frame_offset - prior.frame_offset
        time_gap = item.time_sec - prior.time_sec
        front_jump = abs(float(item.candidate.y) - float(prior.candidate.y))
        bottom_jump = abs(item.material_bottom_y - prior.material_bottom_y)
        extent_compatible = bool(
            bottom_jump <= maximum_jump * max(2, frame_gap * 2)
            or abs(item.width_ratio - prior.width_ratio) <= 0.35
        )
        if (
            0 < frame_gap <= 4
            and 0.0 < time_gap <= 2.0
            and front_jump <= maximum_jump * frame_gap
            and extent_compatible
        ):
            current.append(item)
        else:
            groups.append(current)
            current = [item]
    if current:
        groups.append(current)
    return tuple(tuple(group) for group in groups)


def _foam_confirmation_segments(
    track: tuple[_FoamEvidence, ...],
) -> tuple[tuple[_FoamEvidence, ...], ...]:
    dynamic = tuple(
        item
        for item in track
        if min(item.internal_motion, item.dynamic_support) >= 0.15
    )
    if not dynamic:
        return ()
    clusters: list[list[_FoamEvidence]] = [[dynamic[0]]]
    for item in dynamic[1:]:
        prior = clusters[-1][-1]
        frame_gap = item.frame_offset - prior.frame_offset
        oil_context_break = bool(
            frame_gap > 1
            and (prior.oil_y is None) != (item.oil_y is None)
        )
        if (
            frame_gap <= 4
            and item.time_sec - prior.time_sec <= 2.0
            and not oil_context_break
        ):
            clusters[-1].append(item)
        else:
            clusters.append([item])
    output: list[tuple[_FoamEvidence, ...]] = []
    for cluster in clusters:
        first = cluster[0].frame_offset
        last = cluster[-1].frame_offset
        selected = [
            item
            for item in track
            if first <= item.frame_offset <= last
        ]
        following = next(
            (
                item
                for item in track
                if item.frame_offset > last
                and item.frame_offset - last <= 2
            ),
            None,
        )
        if following is not None:
            selected.append(following)
        output.append(tuple(selected))
    return tuple(output)


def _foam_segment_accepted(
    segment: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> bool:
    if len(segment) < 2:
        return False
    material = sum(item.material_support for item in segment) / len(segment)
    coherent_ratio = sum(item.coherent for item in segment) / len(segment)
    static = sum(item.static_opposition for item in segment) / len(segment)
    registered_evolution = tuple(
        min(item.internal_motion, item.dynamic_support)
        for item in segment
    )
    dynamic_frames = sum(value >= 0.15 for value in registered_evolution)
    dynamic = sum(registered_evolution) / len(registered_evolution)
    dynamic_frame_ratio = dynamic_frames / len(segment)
    strong_dynamic_frames = sum(value >= 0.20 for value in registered_evolution)
    static_dominated = bool(
        static >= 0.65
        and (strong_dynamic_frames < 2 or max(registered_evolution) < 0.28)
    )
    required_material = max(
        0.30,
        float(glass.detector_settings.foam_min_evidence_score) * 0.72,
    )
    return bool(
        not static_dominated
        and material >= required_material
        and coherent_ratio >= 0.60
        and dynamic >= 0.10
        and dynamic_frames >= 2
        and dynamic_frame_ratio >= 0.50
        and _foam_formation_witness(segment, glass)
    )


def _foam_track_static_dominated(track: tuple[_FoamEvidence, ...]) -> bool:
    if not track:
        return False
    static = sum(item.static_opposition for item in track) / len(track)
    strong_dynamic = sum(
        min(item.internal_motion, item.dynamic_support) >= 0.20
        for item in track
    )
    return static >= 0.65 and strong_dynamic < 2


def _foam_formation_witness(
    segment: tuple[_FoamEvidence, ...],
    glass: GlassInspectionConfig,
) -> bool:
    """Require directed front formation or a bounded stable material layer.

    Area and width changes cannot independently turn splash, a fixed top row or
    descending wall residue into an episode. They may support a stable layer
    only when at least three dynamic observations remain spatially bounded away
    from the top entrance. This preserves a reviewed stable Foam layer without
    reopening the R17 Windows Y80 or descending-residue tracks.
    """

    front_rows = tuple(float(item.candidate.y) for item in segment)
    if len(front_rows) < 2:
        return False
    geometry_height = max(
        1.0,
        float(glass.geometry.ellipse.radius_y) * 2.0,
    )
    required_rise = max(4.0, geometry_height * 0.015)
    steps = tuple(
        prior - current
        for prior, current in zip(front_rows, front_rows[1:])
    )
    directional_agreement = sum(step >= -2.0 for step in steps) / len(steps)
    directed_front = bool(
        front_rows[0] - front_rows[-1] >= required_rise
        and directional_agreement >= 0.60
    )
    if directed_front:
        return directed_front
    front_span = max(front_rows) - min(front_rows)
    area_span = max(item.area_ratio for item in segment) - min(
        item.area_ratio for item in segment
    )
    width_span = max(item.width_ratio for item in segment) - min(
        item.width_ratio for item in segment
    )
    maximum_width = max(item.width_ratio for item in segment)
    geometry_top = float(
        glass.geometry.ellipse.center_y - glass.geometry.ellipse.radius_y
    )
    mean_relative_front = (
        sum(front_rows) / len(front_rows) - geometry_top
    ) / geometry_height
    bounded_stable_front = bool(
        front_span <= max(3.0, geometry_height * 0.015)
        and mean_relative_front > 0.12
    )
    substantial_two_frame_layer = bool(
        len(segment) == 2
        and min(item.area_ratio for item in segment) >= 0.25
        and min(item.width_ratio for item in segment) >= 0.60
    )
    stable_observation_support = bool(
        len(segment) >= 3 or substantial_two_frame_layer
    )
    extent_evolution = bool(
        area_span
        >= max(0.02, float(glass.detector_settings.foam_min_area_ratio))
        or width_span / max(0.01, maximum_width) >= 0.12
    )
    return (
        stable_observation_support
        and bounded_stable_front
        and extent_evolution
    )


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
    """Count final Oil rows that identify the same material boundary."""

    return sum(
        _oil_foam_relation(
            evidence,
            detections[evidence.frame_offset],
            glass,
        ).aliases
        for evidence in group
    )


def _oil_foam_relation(
    evidence: _FoamEvidence | None,
    detection: PhaseDetection,
    glass: GlassInspectionConfig,
) -> _OilFoamRelation:
    if evidence is None or not _finite(detection.raw_oil_air_level_y):
        return _OilFoamRelation("no_resolved_oil", None, None)
    oil_y = float(detection.raw_oil_air_level_y)
    separation = oil_y - float(evidence.candidate.y)
    tolerance = _oil_foam_identity_tolerance(glass)
    if abs(separation) <= tolerance:
        kind = "same_boundary"
    elif separation < -tolerance:
        kind = "inverted_topology"
    else:
        kind = "distinct_lower_oil"
    return _OilFoamRelation(kind, oil_y, separation)


def _oil_foam_identity_tolerance(glass: GlassInspectionConfig) -> float:
    """Return same-boundary tolerance independent of Oil temporal motion.

    A temporal jump allowance may be tens of pixels, while two material layers
    in one frame can legitimately be separated by that distance. Identity is
    therefore bounded to a small fraction of the analysis height.
    """

    height = max(1.0, float(glass.geometry.ellipse.radius_y) * 2.0)
    return max(3.0, min(8.0, height * 0.01))


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
