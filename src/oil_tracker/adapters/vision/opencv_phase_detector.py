from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .fill_state_classifier import classify_fill_state
from .foam_front_detector import (
    FoamDecisionStatus,
    FoamDetectionResult,
    detect_bottom_connected_foam,
)
from .foam_temporal_gate import FoamTemporalDecision, FoamTemporalGate
from .geometry_masks import MaskBundle, build_mask_bundle
from .oil_hypothesis_projection import (
    build_hypothesis_debug_profiles,
    project_production_result,
)
from .oil_shadow_pipeline import (
    OilHypothesisPipeline,
    oil_debug_detail,
    oil_runtime_metrics,
    outcome_hypotheses,
)
from .oil_shadow_types import (
    EvidenceUnavailableOutcome,
    OilCanonicalOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
)
from .preprocessing import PreprocessResult, preprocess
from .temporal_tracker import TemporalTracker


@dataclass
class PhaseDetectionDebugArtifacts:
    images: dict[str, np.ndarray] = field(default_factory=dict)
    profiles: dict[str, list[float]] = field(default_factory=dict)
    candidate_rows: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)


class OpenCvPhaseDetector:
    version = "opencv-phase-detector-s5b-typed-production-v1"

    def __init__(self) -> None:
        self._trackers: dict[str, TemporalTracker] = {}
        self._static_maps: dict[str, np.ndarray] = {}
        self._foam_gate = FoamTemporalGate()
        self._oil_pipeline = OilHypothesisPipeline()

    @property
    def foam_temporal_state_count(self) -> int:
        return self._foam_gate.state_count

    @property
    def oil_temporal_state_count(self) -> int:
        return self._oil_pipeline.temporal_state_count

    @property
    def oil_bounds(self):
        return self._oil_pipeline.bounds

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._trackers.clear()
            self._static_maps.clear()
            self._foam_gate.reset()
            self._reset_oil_pipeline(None)
        else:
            key = str(glass_id)
            self._trackers.pop(key, None)
            self._static_maps.pop(key, None)
            self._foam_gate.reset(key)
            self._reset_oil_pipeline(key)

    def learn_static_artifact(self, frames: list[np.ndarray], glass: GlassInspectionConfig) -> None:
        if not frames:
            return
        maps = []
        for frame in frames:
            bundle = build_mask_bundle(frame, glass)
            pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
            maps.append((pre.horizontal_mask > 0).astype(np.float32))
        persistence = np.mean(maps, axis=0)
        self._static_maps[glass.id] = np.where(persistence >= 0.75, 255, 0).astype(np.uint8)

    def detect(
        self,
        frame: np.ndarray,
        glass: GlassInspectionConfig,
        frame_index: int,
        time_sec: float,
        debug: bool = False,
    ) -> tuple[PhaseDetection, PhaseDetectionDebugArtifacts | None]:
        settings = glass.detector_settings
        tracker = self._trackers.get(glass.id)
        if tracker is None:
            tracker = TemporalTracker(settings.smoothing_window, settings.state_hold_frames)
            tracker.current_state = _initial_prior(glass.initial_state)
            self._trackers[glass.id] = tracker
        else:
            tracker.smoothing_window = max(1, int(settings.smoothing_window))
            tracker.state_hold_frames = max(1, int(settings.state_hold_frames))

        bundle = build_mask_bundle(frame, glass)
        pre = preprocess(bundle.crop, bundle.effective_mask, settings)
        static_map = self._static_maps.get(glass.id)
        foam = detect_bottom_connected_foam(
            bundle.crop,
            pre.gray,
            pre.canny,
            pre.glare_mask,
            bundle.effective_mask,
            settings,
        )
        foam_temporal = self._foam_gate.evaluate(glass.id, foam, settings)
        foam_candidate = foam_temporal.candidate
        accepted_foam_component_mask = None if foam_candidate is None else foam.mask
        oil_result = self._evaluate_oil_pipeline(
            glass.id,
            pre,
            bundle,
            static_map,
            accepted_foam_front_local_y=(
                None if foam_candidate is None else float(foam_candidate.y)
            ),
            accepted_foam_component_mask=accepted_foam_component_mask,
        )
        oil_projection = project_production_result(oil_result)
        selected = oil_projection.selected_candidate
        previous_state = tracker.current_state
        proposed_state, visibility, flags = classify_fill_state(
            pre.gray,
            bundle.effective_mask,
            pre.glare_mask,
            selected,
            foam_candidate,
            previous_state,
            settings,
            foam_temporal.decision_status,
            oil_result,
        )
        flags.extend(_foam_flags(foam, foam_temporal))
        flags.extend(oil_projection.flags)
        valid_rows = np.where(bundle.effective_mask.any(axis=1))[0]
        if (
            selected is None
            and proposed_state is FillState.UNKNOWN_REVIEW
            and "FOGGED_OR_GLARE" not in flags
            and isinstance(oil_result, EvidenceUnavailableOutcome)
        ):
            flags.append("DETECTION_LOST")
        if foam_candidate is not None and valid_rows.size:
            foam_relative = (foam_candidate.y - float(valid_rows.min())) / max(
                1.0,
                float(np.ptp(valid_rows)),
            )
            if foam_relative <= 0.12:
                flags.append("FOAM_REACH_TOP")

        origin_y = bundle.crop_origin[1]
        raw_oil_source = oil_projection.raw_source_y
        raw_foam_source = foam_candidate.y + origin_y if foam_candidate else None
        review_override = proposed_state is FillState.UNKNOWN_REVIEW or "REVIEW_REQUIRED" in flags
        smoothed_oil, smoothed_foam, stabilized_state = tracker.update(
            raw_oil_source,
            raw_foam_source,
            proposed_state,
            oil_tracker_action=oil_projection.tracker_action,
            oil_smoothing_action=oil_projection.smoothing_action,
            foam_update_accepted=foam_candidate is not None,
            review_override=review_override,
        )

        oil_conf = oil_projection.confidence
        foam_conf = foam_candidate.final_score if foam_candidate else 0.0
        overall = _overall_confidence(stabilized_state, oil_conf, foam_conf, visibility)
        if overall < settings.minimum_final_confidence:
            flags.append("LOW_CONFIDENCE")

        zero = glass.geometry.zero_line_y
        oil_px = None if smoothed_oil is None or zero is None else zero - smoothed_oil
        foam_px = None if smoothed_foam is None or zero is None else zero - smoothed_foam
        mm = glass.mm_per_pixel
        oil_mm = None if oil_px is None or mm is None else oil_px * mm
        foam_mm = None if foam_px is None or mm is None else foam_px * mm

        debug_profiles = (
            build_hypothesis_debug_profiles(
                pre,
                bundle.effective_mask,
                bundle.ellipse_mask,
                static_map,
                outcome_hypotheses(oil_result),
            )
            if debug
            else {}
        )
        candidates = list(oil_projection.candidates)
        foam_trace_candidate = foam.candidate
        if foam_trace_candidate is not None:
            foam_trace_candidate.features.setdefault("local_y", foam_trace_candidate.y)
            foam_trace_candidate.features["source_y"] = float(foam_trace_candidate.y + origin_y)
            foam_trace_candidate.features["temporal_pending_count"] = float(foam_temporal.pending_count)
            foam_trace_candidate.features["temporal_required_count"] = float(foam_temporal.required_count)
            foam_trace_candidate.features["temporal_front_delta"] = float(foam_temporal.front_delta or 0.0)
            foam_trace_candidate.y += origin_y
            candidates.append(foam_trace_candidate)

        debug_metrics = {
            "glare_ratio": float(np.count_nonzero(pre.glare_mask))
            / max(1, np.count_nonzero(bundle.effective_mask)),
            "oil_smoothing_sample_count": int(tracker.oil_sample_count),
            "oil_hypothesis_candidate_count": len(oil_projection.candidates),
            "foam_bottom_connected_area_ratio": float(foam.bottom_connected_area_ratio),
            "foam_evidence_score": float(foam.final_evidence_score),
            "foam_evidence_strength": foam_temporal.evidence_strength.value,
            "foam_decision_status": foam_temporal.decision_status.value,
            "foam_whiteness_ratio": float(foam.whiteness_ratio),
            "foam_texture_support_ratio": float(foam.texture_support_ratio),
            "foam_glare_overlap_ratio": float(foam.glare_overlap_ratio),
            "foam_component_height_ratio": float(foam.component_height_ratio),
            "foam_component_width_ratio": float(foam.component_width_ratio),
            "foam_bounding_box_fill_ratio": float(foam.bounding_box_fill_ratio),
            "foam_temporal_pending_count": int(foam_temporal.pending_count),
            "foam_temporal_required_count": int(foam_temporal.required_count),
            "foam_front_delta": (
                None if foam_temporal.front_delta is None else float(foam_temporal.front_delta)
            ),
            "foam_min_evidence_score": float(settings.foam_min_evidence_score),
            "foam_strong_evidence_score": float(settings.foam_strong_evidence_score),
            "effective_area": int(np.count_nonzero(bundle.effective_mask)),
            "previous_state": previous_state.value if previous_state else None,
            "proposed_state": proposed_state.value,
            "stabilized_state": stabilized_state.value,
        }
        debug_metrics.update(oil_runtime_metrics(oil_result))
        oil_detail = oil_debug_detail(oil_result) if debug else None
        detection = PhaseDetection(
            glass_id=glass.id,
            frame_index=frame_index,
            time_sec=time_sec,
            fill_state=stabilized_state,
            oil_air_level_y=smoothed_oil,
            oil_air_level_px_from_zero=oil_px,
            oil_air_level_mm_from_zero=oil_mm,
            foam_front_y=smoothed_foam,
            foam_front_px_from_zero=foam_px,
            foam_front_mm_from_zero=foam_mm,
            oil_air_confidence=oil_conf,
            foam_confidence=foam_conf,
            visibility_confidence=visibility,
            overall_confidence=overall,
            raw_oil_air_level_y=raw_oil_source,
            raw_foam_front_y=raw_foam_source,
            smoothed_oil_air_level_y=smoothed_oil,
            smoothed_foam_front_y=smoothed_foam,
            candidates=candidates,
            flags=sorted(set(flags)),
            debug_metrics=debug_metrics,
        )
        artifacts = (
            self._debug_artifacts(
                frame,
                glass,
                bundle,
                pre,
                foam,
                foam_temporal,
                detection,
                static_map,
                debug_profiles,
                oil_detail,
            )
            if debug
            else None
        )
        return detection, artifacts

    def _reset_oil_pipeline(self, glass_id: str | None) -> None:
        self._oil_pipeline.reset(glass_id)

    def _evaluate_oil_pipeline(
        self,
        glass_id: str,
        pre: PreprocessResult,
        bundle: MaskBundle,
        static_map: np.ndarray | None,
        *,
        accepted_foam_front_local_y: float | None = None,
        accepted_foam_component_mask: np.ndarray | None = None,
    ) -> OilCanonicalOutcome:
        try:
            kwargs = _isolated_pipeline_inputs(
                glass_id=glass_id,
                pre=pre,
                bundle=bundle,
                static_map=static_map,
                accepted_foam_front_local_y=accepted_foam_front_local_y,
                accepted_foam_component_mask=accepted_foam_component_mask,
            )
            return self._oil_pipeline.run(**kwargs)
        except Exception as exc:
            reason = f"{type(exc).__name__}:{str(exc)[:120]}"
            return PipelineFailureOutcome(
                reason=reason or "oil_hypothesis_execution_failed",
                stage=PipelineFailureStage.EXTERNAL_RUNNER,
            )

    def _debug_artifacts(
        self,
        frame: np.ndarray,
        glass: GlassInspectionConfig,
        bundle: MaskBundle,
        pre: PreprocessResult,
        foam: FoamDetectionResult,
        foam_temporal: FoamTemporalDecision,
        detection: PhaseDetection,
        static_map: np.ndarray | None,
        profiles: dict[str, list[float]],
        oil_detail: dict[str, Any] | None,
    ) -> PhaseDetectionDebugArtifacts:
        overlay = frame.copy()
        e = glass.geometry.ellipse
        cv2.ellipse(
            overlay,
            (int(e.center_x), int(e.center_y)),
            (int(e.radius_x), int(e.radius_y)),
            0,
            0,
            360,
            (0, 220, 255),
            2,
        )
        if glass.geometry.zero_line_y is not None:
            extent = e.horizontal_extent_at(glass.geometry.zero_line_y)
            if extent:
                cv2.line(
                    overlay,
                    (int(extent[0]), int(glass.geometry.zero_line_y)),
                    (int(extent[1]), int(glass.geometry.zero_line_y)),
                    (255, 255, 0),
                    1,
                )
        for candidate in detection.candidates:
            extent = e.horizontal_extent_at(float(candidate.y))
            if extent is None:
                continue
            if candidate.kind.value == "foam_front":
                color = (255, 0, 255)
            elif candidate.source.startswith("oil_hypothesis:"):
                color = (0, 255, 0) if candidate.selected else (0, 0, 255)
            else:
                color = (120, 120, 120)
            cv2.line(
                overlay,
                (int(extent[0]), int(candidate.y)),
                (int(extent[1]), int(candidate.y)),
                color,
                2 if candidate.selected else 1,
                cv2.LINE_AA,
            )
        accepted_mask = foam.mask if foam_temporal.accepted else np.zeros_like(foam.mask)
        images = {
            "overlay": overlay,
            "original_roi": bundle.crop,
            "ellipse_mask": bundle.ellipse_mask,
            "effective_mask": bundle.effective_mask,
            "exclusion_mask": bundle.exclusion_mask,
            "grayscale": pre.gray,
            "normalized": pre.normalized,
            "blurred": pre.blurred,
            "sobel": pre.sobel_y_abs,
            "canny": pre.canny,
            "horizontal_mask": pre.horizontal_mask,
            "glare_mask": pre.glare_mask,
            "foam_mask": foam.mask,
            "foam_variance": cv2.normalize(foam.variance_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
            "foam_edge_density": _unit_image(foam.edge_density_map),
            "foam_whiteness": _unit_image(foam.whiteness_map),
            "foam_texture_evidence": _unit_image(foam.texture_evidence_map),
            "foam_glare_excluded_mask": foam.glare_excluded_mask,
            "foam_combined_evidence": _unit_image(foam.combined_evidence_map),
            "foam_accepted_component": accepted_mask,
            "static_artifact_map": static_map if static_map is not None else np.zeros_like(bundle.effective_mask),
        }
        rows = []
        for rank, candidate in enumerate(
            sorted(
                detection.candidates,
                key=lambda item: (
                    -float(item.features.get("observation_score", item.final_score)),
                    float(item.y),
                    item.source,
                ),
            ),
            1,
        ):
            rows.append(
                {
                    "rank": rank,
                    "kind": candidate.kind.value,
                    "source": candidate.source,
                    "y": candidate.y,
                    **candidate.features,
                    **candidate.penalties,
                    "feature_score": candidate.feature_score,
                    "penalty": candidate.penalty,
                    "final_score": candidate.final_score,
                    "selected": candidate.selected,
                    "rejected": candidate.rejected,
                    "reject_reason": candidate.reject_reason,
                }
            )
        return PhaseDetectionDebugArtifacts(
            images=images,
            profiles=profiles,
            candidate_rows=rows,
            state={
                "fill_state": detection.fill_state.value,
                "oil_air_confidence": detection.oil_air_confidence,
                "foam_confidence": detection.foam_confidence,
                "visibility_confidence": detection.visibility_confidence,
                "overall_confidence": detection.overall_confidence,
                "flags": detection.flags,
                "oil_hypothesis": oil_detail or {},
                **detection.debug_metrics,
            },
        )



def _isolated_pipeline_inputs(
    *,
    glass_id: str,
    pre: PreprocessResult,
    bundle: MaskBundle,
    static_map: np.ndarray | None,
    accepted_foam_front_local_y: float | None = None,
    accepted_foam_component_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    readonly_pre = PreprocessResult(
        *(
            _isolated_readonly_copy(value)
            for value in (
                pre.gray,
                pre.normalized,
                pre.blurred,
                pre.sobel_y_signed,
                pre.sobel_y_abs,
                pre.canny,
                pre.horizontal_mask,
                pre.glare_mask,
            )
        )
    )
    return {
        "glass_id": glass_id,
        "pre": readonly_pre,
        "effective_mask": _isolated_readonly_copy(bundle.effective_mask),
        "ellipse_mask": _isolated_readonly_copy(bundle.ellipse_mask),
        "exclusion_mask": _isolated_readonly_copy(bundle.exclusion_mask),
        "static_artifact_map": (
            None if static_map is None else _isolated_readonly_copy(static_map)
        ),
        "crop_origin_y": float(bundle.crop_origin[1]),
        "accepted_foam_front_local_y": (
            None
            if accepted_foam_front_local_y is None
            else float(accepted_foam_front_local_y)
        ),
        "accepted_foam_component_mask": (
            None
            if accepted_foam_component_mask is None
            else _isolated_readonly_copy(accepted_foam_component_mask)
        ),
    }


def _isolated_readonly_copy(value: np.ndarray) -> np.ndarray:
    isolated = np.array(value, copy=True, order="K", subok=False)
    isolated.flags.writeable = False
    return isolated


def _foam_flags(
    foam: FoamDetectionResult,
    temporal: FoamTemporalDecision,
) -> list[str]:
    if temporal.decision_status is FoamDecisionStatus.ACCEPTED_STRONG:
        return ["FOAM_STRONG_EVIDENCE"]
    if temporal.decision_status is FoamDecisionStatus.ACCEPTED_MODERATE:
        return ["FOAM_MODERATE_EVIDENCE"]
    if temporal.decision_status is FoamDecisionStatus.PERSISTENCE_PENDING:
        return ["FOAM_PERSISTENCE_PENDING"]
    if temporal.decision_status is FoamDecisionStatus.AMBIGUOUS:
        return ["FOAM_EVIDENCE_AMBIGUOUS"]
    if temporal.decision_status is FoamDecisionStatus.GLARE_REJECTED:
        return ["FOAM_GLARE_REJECTED"]
    if temporal.decision_status is FoamDecisionStatus.WEAK_REJECTED or (
        foam.candidate is not None and foam.candidate.rejected
    ):
        return ["FOAM_COMPONENT_REJECTED"]
    return []


def _unit_image(values: np.ndarray) -> np.ndarray:
    finite = np.nan_to_num(values, nan=0.0, posinf=1.0, neginf=0.0)
    return np.clip(finite * 255.0, 0.0, 255.0).astype(np.uint8)


def _initial_prior(initial: InitialObservationState) -> FillState | None:
    if initial == InitialObservationState.AUTO:
        return None
    return FillState(initial.value)


def _overall_confidence(state: FillState, oil: float, foam: float, visibility: float) -> float:
    if state in {FillState.FULL_NO_INTERFACE, FillState.EMPTY_NO_INTERFACE}:
        return max(0.0, min(1.0, visibility * 0.80))
    if state == FillState.FULL_WITH_FOAM:
        return max(0.0, min(1.0, visibility * 0.4 + foam * 0.6))
    if state == FillState.UNKNOWN_REVIEW:
        return min(0.35, visibility * 0.35)
    return max(0.0, min(1.0, visibility * 0.25 + oil * 0.60 + foam * 0.15))
