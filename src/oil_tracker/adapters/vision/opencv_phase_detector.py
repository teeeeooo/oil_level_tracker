from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .fill_state_classifier import classify_fill_state
from .artifact_calibration import (
    apply_artifact_templates,
    attach_spatial_signature,
)
from .foam_front_detector import (
    FoamDecisionStatus,
    FoamDetectionResult,
    detect_bottom_connected_foam,
    evaluate_foam_layer_coherence,
)
from .foam_temporal_gate import FoamStaticMatch, FoamTemporalDecision, FoamTemporalGate
from .geometry_masks import MaskBundle, build_mask_bundle
from .oil_hypothesis_projection import (
    build_hypothesis_debug_profiles,
    project_production_result,
)
from .oil_material_path import (
    generate_material_path_candidates,
    material_layer_context_features,
)
from .oil_supplemental_path import generate_distributed_sobel_candidates
from .oil_shadow_pipeline import (
    OilHypothesisPipeline,
    oil_debug_detail,
    oil_runtime_metrics,
    outcome_hypotheses,
)
from .oil_shadow_types import (
    CompatibilityTrackerAction,
    EvidenceUnavailableOutcome,
    OilCanonicalOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
    SmoothingAction,
)
from .preprocessing import PreprocessResult, preprocess
from .observation_sequence_resolver import (
    ObservationSequenceResolution,
    ObservationSequenceResolver,
)
from .temporal_raster_evidence import (
    RegisteredFoamMotionTracker,
    RegisteredOilMotionTracker,
    registered_foam_motion_features,
    registered_oil_candidate_features,
)
from .temporal_tracker import TemporalTracker


@dataclass
class PhaseDetectionDebugArtifacts:
    images: dict[str, np.ndarray] = field(default_factory=dict)
    profiles: dict[str, list[float]] = field(default_factory=dict)
    candidate_rows: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)


class OpenCvPhaseDetector:
    version = "opencv-phase-detector-r8-observation-recovery-v1"

    def __init__(self) -> None:
        self._trackers: dict[str, TemporalTracker] = {}
        self._static_maps: dict[str, np.ndarray] = {}
        self._static_foam_maps: dict[str, np.ndarray] = {}
        self._foam_gate = FoamTemporalGate()
        self._oil_pipeline = OilHypothesisPipeline()
        self._foam_motion_tracker = RegisteredFoamMotionTracker()
        self._oil_motion_tracker = RegisteredOilMotionTracker()
        self._observation_sequence_resolver = ObservationSequenceResolver()

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
            self._static_foam_maps.clear()
            self._foam_gate.reset()
            self._foam_motion_tracker.reset()
            self._oil_motion_tracker.reset()
            self._reset_oil_pipeline(None)
        else:
            key = str(glass_id)
            self._trackers.pop(key, None)
            self._static_maps.pop(key, None)
            self._static_foam_maps.pop(key, None)
            self._foam_gate.reset(key)
            self._foam_motion_tracker.reset(key)
            self._oil_motion_tracker.reset(key)
            self._reset_oil_pipeline(key)

    def resolve_sequence(
        self,
        detections: list[PhaseDetection] | tuple[PhaseDetection, ...],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> ObservationSequenceResolution:
        """Resolve the completed analysis window before public sample projection."""

        return self._observation_sequence_resolver.resolve(
            detections,
            glass,
            confirmed_initial_state,
        )

    def learn_static_artifact(self, frames: list[np.ndarray], glass: GlassInspectionConfig) -> None:
        if not frames:
            return
        maps = []
        foam_maps = []
        for frame in frames:
            bundle = build_mask_bundle(frame, glass)
            pre = preprocess(bundle.crop, bundle.effective_mask, glass.detector_settings)
            maps.append((pre.horizontal_mask > 0).astype(np.float32))
            foam = detect_bottom_connected_foam(
                bundle.crop,
                pre.gray,
                pre.canny,
                pre.glare_mask,
                bundle.effective_mask,
                glass.detector_settings,
            )
            foam_maps.append((foam.mask > 0).astype(np.float32))
        persistence = np.mean(maps, axis=0)
        self._static_maps[glass.id] = np.where(persistence >= 0.75, 255, 0).astype(np.uint8)
        foam_persistence = np.mean(foam_maps, axis=0)
        self._static_foam_maps[glass.id] = np.where(
            foam_persistence >= 0.75,
            255,
            0,
        ).astype(np.uint8)

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
        # R6 generates Oil evidence from the base effective raster. Raw or
        # current-frame accepted Foam cannot remove a candidate before the
        # independent observation owners have evaluated it.
        oil_result = self._evaluate_oil_pipeline(
            glass.id,
            pre,
            bundle,
            static_map,
        )
        oil_projection = project_production_result(oil_result)
        selected = oil_projection.selected_candidate
        selected_calibrated_artifact = False
        if selected is not None and glass.geometry.artifact_templates:
            signed_selected = attach_spatial_signature(
                selected,
                pre.horizontal_mask,
                glass,
                crop_origin=bundle.crop_origin,
            )
            _selected_candidates, selected_rejected_count = apply_artifact_templates(
                [signed_selected],
                glass,
            )
            selected_calibrated_artifact = selected_rejected_count > 0
            if selected_calibrated_artifact:
                selected = None
        foam = detect_bottom_connected_foam(
            bundle.crop,
            pre.gray,
            pre.canny,
            pre.glare_mask,
            bundle.effective_mask,
            settings,
        )
        foam_layer = evaluate_foam_layer_coherence(foam)
        material_layer_topology = bool(
            foam_layer.coherent
            and float(foam.component_width_ratio) >= 0.55
            and float(foam.bounding_box_fill_ratio) >= 0.35
        )
        white_material_layer_topology = bool(
            material_layer_topology and float(foam.whiteness_ratio) >= 0.55
        )
        white_material_texture_present = bool(
            float(foam.whiteness_ratio) >= 0.55
            and float(foam.component_width_ratio) >= 0.30
            and float(foam.bounding_box_fill_ratio) >= 0.30
        )
        foam_motion = self._foam_motion_tracker.evaluate(
            glass.id,
            pre.gray,
            bundle.effective_mask,
            foam.mask,
            foam.front_y,
        )
        material_motion_features = registered_foam_motion_features(foam_motion)
        oil_motion = self._oil_motion_tracker.evaluate(
            glass.id,
            pre.gray,
            bundle.effective_mask,
        )
        material_path_candidates: list[BoundaryCandidate] = []
        artifact_template_count = len(glass.geometry.artifact_templates)
        for candidate in generate_material_path_candidates(
                pre,
                bundle.effective_mask,
                static_map,
                crop_origin_y=float(bundle.crop_origin[1]),
                top_k=_artifact_compensated_top_k(
                    settings.candidate_top_k,
                    artifact_template_count,
                    base_cap=6,
                    calibrated_cap=8,
                ),
                # Generic material texture is corroboration for a lower phase
                # boundary; it is not accepted/public Foam authority.
                material_evidence_map=foam.combined_evidence_map,
            ):
            material_context = material_layer_context_features(
                foam.combined_evidence_map,
                bundle.effective_mask,
                pre.glare_mask,
                local_y=float(candidate.y) - float(bundle.crop_origin[1]),
            )
            path_features = {
                **candidate.features,
                **material_context,
                **registered_oil_candidate_features(
                    oil_motion,
                    local_y=float(candidate.y) - float(bundle.crop_origin[1]),
                ),
                "sequence_material_layer_topology": float(
                    material_layer_topology
                ),
                "sequence_white_material_layer_topology": float(
                    white_material_layer_topology
                ),
                "sequence_white_material_texture_present": float(
                    white_material_texture_present
                ),
            }
            path_penalties = {
                **candidate.penalties,
                "material_texture_conflict": float(
                    material_context["material_texture_conflict"]
                    if white_material_texture_present
                    else 0.0
                ),
            }
            material_path_candidates.append(
                replace(
                    candidate,
                    features=path_features,
                    penalties=path_penalties,
                )
            )
        # Keep a bounded phase-path proposal independent of the raw Foam-like
        # material raster. It is additive and starts without direct anchor
        # authority, so a false Foam texture cannot monopolize proposals.
        raster_material_path_candidates: list[BoundaryCandidate] = []
        for candidate in generate_material_path_candidates(
            pre,
            bundle.effective_mask,
            static_map,
            crop_origin_y=float(bundle.crop_origin[1]),
            top_k=_artifact_compensated_top_k(
                settings.candidate_top_k,
                artifact_template_count,
                base_cap=4,
                calibrated_cap=6,
            ),
            material_evidence_map=None,
        ):
            if any(
                abs(float(candidate.y) - float(existing.y)) <= 6.0
                for existing in material_path_candidates
            ):
                continue
            local_y = float(candidate.y) - float(bundle.crop_origin[1])
            raster_material_path_candidates.append(
                replace(
                    candidate,
                    source="r8_raster_material_path",
                    features={
                        **candidate.features,
                        **registered_oil_candidate_features(
                            oil_motion,
                            local_y=local_y,
                        ),
                        "r8_supplemental_path": 1.0,
                        "sequence_material_layer_topology": 0.0,
                        "sequence_white_material_layer_topology": 0.0,
                        "sequence_white_material_texture_present": 0.0,
                    },
                )
            )
        distributed_sobel_candidates = [
            replace(
                candidate,
                features={
                    **candidate.features,
                    **registered_oil_candidate_features(
                        oil_motion,
                        local_y=float(candidate.y) - float(bundle.crop_origin[1]),
                    ),
                },
            )
            for candidate in generate_distributed_sobel_candidates(
                pre,
                bundle.effective_mask,
                static_map,
                crop_origin_y=float(bundle.crop_origin[1]),
            )
        ]
        static_foam_map = self._static_foam_maps.get(glass.id)
        static_foam_match = _foam_static_match(foam.mask, static_foam_map)
        foam_temporal = self._foam_gate.evaluate(
            glass.id,
            foam,
            settings,
            static_match=static_foam_match,
            layer_coherent=foam_layer.coherent,
        )
        foam_candidate = foam_temporal.candidate
        foam_calibrated_artifact = False
        if foam_candidate is not None and glass.geometry.artifact_templates:
            source_foam_candidate = replace(
                foam_candidate,
                y=float(foam_candidate.y + bundle.crop_origin[1]),
            )
            signed_foam = attach_spatial_signature(
                source_foam_candidate,
                foam.material_support_mask,
                glass,
                crop_origin=bundle.crop_origin,
            )
            _foam_candidates, foam_rejected_count = apply_artifact_templates(
                [signed_foam],
                glass,
            )
            foam_calibrated_artifact = foam_rejected_count > 0
            if foam_calibrated_artifact:
                foam_candidate = None
        foam_context_authoritative = False
        foam_context_reason = "r6_independent_oil_evidence"
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
        if selected_calibrated_artifact or foam_calibrated_artifact:
            flags.append("R8_CALIBRATED_ARTIFACT_REJECTED")
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
        raw_oil_source = (
            None
            if selected_calibrated_artifact
            else oil_projection.raw_source_y
        )
        raw_foam_source = foam_candidate.y + origin_y if foam_candidate else None
        review_override = proposed_state is FillState.UNKNOWN_REVIEW or "REVIEW_REQUIRED" in flags
        if foam_calibrated_artifact:
            tracker.clear_foam()
        smoothed_oil, smoothed_foam, stabilized_state = tracker.update(
            raw_oil_source,
            raw_foam_source,
            proposed_state,
            oil_tracker_action=(
                CompatibilityTrackerAction.NO_UPDATE
                if selected_calibrated_artifact
                else oil_projection.tracker_action
            ),
            oil_smoothing_action=(
                SmoothingAction.CLEAR_STALE_AFTER_STABLE_ABSENCE
                if selected_calibrated_artifact
                else oil_projection.smoothing_action
            ),
            foam_update_accepted=foam_candidate is not None,
            review_override=review_override,
        )

        oil_conf = (
            0.0
            if selected_calibrated_artifact
            else oil_projection.confidence
        )
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
        oil_candidates: list[BoundaryCandidate] = []
        for candidate in oil_projection.candidates:
            if candidate.kind is not BoundaryKind.OIL_AIR:
                oil_candidates.append(candidate)
                continue
            material_context = material_layer_context_features(
                foam.combined_evidence_map,
                bundle.effective_mask,
                pre.glare_mask,
                local_y=float(candidate.y) - float(origin_y),
            )
            candidate_features = dict(candidate.features)
            candidate_features.update(material_context)
            candidate_features.update(
                registered_oil_candidate_features(
                    oil_motion,
                    local_y=float(candidate.y) - float(origin_y),
                )
            )
            candidate_features.update(
                {
                    "sequence_material_layer_topology": float(
                        material_layer_topology
                    ),
                    "sequence_white_material_layer_topology": float(
                        white_material_layer_topology
                    ),
                    "sequence_white_material_texture_present": float(
                        white_material_texture_present
                    ),
                }
            )
            candidate_penalties = dict(candidate.penalties)
            candidate_penalties["material_texture_conflict"] = float(
                material_context["material_texture_conflict"]
                if white_material_texture_present
                else 0.0
            )
            oil_candidates.append(
                replace(
                    candidate,
                    features=candidate_features,
                    penalties=candidate_penalties,
                )
            )
        candidates = [
            *oil_candidates,
            *material_path_candidates,
            *raster_material_path_candidates,
            *distributed_sobel_candidates,
        ]
        raw_foam_candidate = foam.candidate
        if raw_foam_candidate is not None:
            sequence_foam_eligible = bool(
                foam_layer.coherent
                and not static_foam_match.dominant
                and float(foam.glare_overlap_ratio)
                <= float(settings.foam_max_glare_overlap_ratio)
                # A public Foam episode is a cross-Glass material layer, not a
                # narrow bottom texture strip or one bright boundary.
                and float(foam.component_width_ratio) >= 0.55
                and float(foam.bounding_box_fill_ratio) >= 0.35
            )
            foam_features = dict(raw_foam_candidate.features)
            foam_features.setdefault("local_y", raw_foam_candidate.y)
            foam_features["source_y"] = float(raw_foam_candidate.y + origin_y)
            foam_features["temporal_pending_count"] = float(foam_temporal.pending_count)
            foam_features["temporal_required_count"] = float(foam_temporal.required_count)
            foam_features["temporal_front_delta"] = float(foam_temporal.front_delta or 0.0)
            foam_features["static_exact_overlap"] = float(
                static_foam_match.exact_overlap
            )
            foam_features["static_tolerant_overlap"] = float(
                static_foam_match.tolerant_overlap
            )
            foam_features["static_reciprocal_overlap"] = float(
                static_foam_match.reciprocal_overlap
            )
            foam_features["foam_layer_coherent"] = float(foam_layer.coherent)
            material_rows = np.flatnonzero(
                np.any(foam.material_support_mask > 0, axis=1)
            )
            foam_features["material_component_bottom_y"] = (
                float(raw_foam_candidate.y + origin_y)
                if material_rows.size == 0
                else float(material_rows[-1] + origin_y)
            )
            foam_features["sequence_foam_eligible"] = float(
                sequence_foam_eligible
            )
            foam_features.update(material_motion_features)
            foam_trace_candidate = replace(
                raw_foam_candidate,
                y=float(raw_foam_candidate.y + origin_y),
                features=foam_features,
                selected=False,
                rejected=not sequence_foam_eligible,
                reject_reason=(
                    ""
                    if sequence_foam_eligible
                    else "r6_foam_candidate_ineligible"
                ),
            )
            candidates.append(foam_trace_candidate)

        candidates = [
            attach_spatial_signature(
                candidate,
                (
                    foam.material_support_mask
                    if candidate.kind is BoundaryKind.FOAM_FRONT
                    else pre.horizontal_mask
                ),
                glass,
                crop_origin=bundle.crop_origin,
            )
            for candidate in candidates
        ]
        candidates, calibrated_artifact_rejected_count = apply_artifact_templates(
            candidates,
            glass,
        )
        if calibrated_artifact_rejected_count:
            flags.append("R8_CALIBRATED_ARTIFACT_REJECTED")

        debug_metrics = {
            "glare_ratio": float(np.count_nonzero(pre.glare_mask))
            / max(1, np.count_nonzero(bundle.effective_mask)),
            "oil_smoothing_sample_count": int(tracker.oil_sample_count),
            "oil_hypothesis_candidate_count": len(oil_projection.candidates),
            "r6_material_path_candidate_count": len(material_path_candidates),
            "r8_raster_material_path_candidate_count": len(
                raster_material_path_candidates
            ),
            "r8_distributed_sobel_candidate_count": len(
                distributed_sobel_candidates
            ),
            "r8_calibrated_artifact_rejected_count": (
                calibrated_artifact_rejected_count
            ),
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
            "foam_static_artifact_overlap": float(static_foam_match.exact_overlap),
            "foam_static_artifact_tolerant_overlap": float(
                static_foam_match.tolerant_overlap
            ),
            "foam_static_artifact_reciprocal_overlap": float(
                static_foam_match.reciprocal_overlap
            ),
            "foam_static_artifact_tolerance_radius_px": int(
                static_foam_match.tolerance_radius_px
            ),
            "foam_static_artifact_dominant": static_foam_match.dominant,
            "foam_static_artifact_pixel_count": (
                0 if static_foam_map is None else int(np.count_nonzero(static_foam_map))
            ),
            "foam_layer_publication_coherent": foam_layer.coherent,
            "foam_layer_publication_reason": foam_layer.reason,
            "foam_layer_wide_row_fraction": float(foam_layer.wide_row_fraction),
            "foam_layer_wide_row_compactness_median": float(
                foam_layer.wide_row_compactness_median
            ),
            "foam_oil_context_authoritative": foam_context_authoritative,
            "foam_oil_context_publication_accepted": foam_candidate is not None,
            "foam_oil_context_reason": foam_context_reason,
            "foam_oil_context_wide_row_fraction": 0.0,
            "foam_oil_context_wide_row_compactness_median": 0.0,
            "foam_temporal_pending_count": int(foam_temporal.pending_count),
            "foam_temporal_required_count": int(foam_temporal.required_count),
            "foam_front_delta": (
                None if foam_temporal.front_delta is None else float(foam_temporal.front_delta)
            ),
            "foam_adjacent_evidence_available": foam_motion.available,
            "foam_adjacent_exact_overlap": float(foam_motion.exact_overlap),
            "foam_adjacent_tolerant_overlap": float(foam_motion.tolerant_overlap),
            "foam_adjacent_reciprocal_overlap": float(foam_motion.reciprocal_overlap),
            "foam_adjacent_mask_turnover": float(foam_motion.mask_turnover),
            "foam_adjacent_area_change_ratio": float(foam_motion.area_change_ratio),
            "foam_adjacent_front_delta_ratio": float(foam_motion.front_delta_ratio),
            "foam_adjacent_dynamic_support": float(foam_motion.dynamic_support),
            "foam_registered_internal_motion_ratio": float(
                foam_motion.internal_motion_ratio
            ),
            "foam_registered_internal_motion_support": float(
                foam_motion.internal_motion_support
            ),
            "foam_registered_dx": float(foam_motion.registration_dx),
            "foam_registered_dy": float(foam_motion.registration_dy),
            "foam_registered_exposure_gain": float(foam_motion.exposure_gain),
            "foam_registered_exposure_offset": float(foam_motion.exposure_offset),
            "oil_registered_motion_available": oil_motion.available,
            "oil_registered_dx": float(oil_motion.registration_dx),
            "oil_registered_dy": float(oil_motion.registration_dy),
            "oil_registered_response": float(oil_motion.registration_response),
            "oil_registered_exposure_gain": float(oil_motion.exposure_gain),
            "oil_registered_exposure_offset": float(oil_motion.exposure_offset),
            "foam_min_evidence_score": float(settings.foam_min_evidence_score),
            "foam_strong_evidence_score": float(settings.foam_strong_evidence_score),
            "effective_area": int(np.count_nonzero(bundle.effective_mask)),
            "previous_state": previous_state.value if previous_state else None,
            "proposed_state": proposed_state.value,
            "stabilized_state": stabilized_state.value,
        }
        debug_metrics.update(_effective_photometric_metrics(pre, bundle.effective_mask))
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
            "foam_material_support_mask": foam.material_support_mask,
            "foam_variance": cv2.normalize(foam.variance_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
            "foam_edge_density": _unit_image(foam.edge_density_map),
            "foam_whiteness": _unit_image(foam.whiteness_map),
            "foam_texture_evidence": _unit_image(foam.texture_evidence_map),
            "foam_glare_excluded_mask": foam.glare_excluded_mask,
            "foam_combined_evidence": _unit_image(foam.combined_evidence_map),
            "foam_accepted_component": accepted_mask,
            "static_artifact_map": static_map if static_map is not None else np.zeros_like(bundle.effective_mask),
            "static_foam_artifact_map": (
                self._static_foam_maps.get(glass.id)
                if self._static_foam_maps.get(glass.id) is not None
                else np.zeros_like(bundle.effective_mask)
            ),
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

def _artifact_compensated_top_k(
    configured: int,
    artifact_template_count: int,
    *,
    base_cap: int,
    calibrated_cap: int,
) -> int:
    """Keep the ordinary proposal budget after user-confirmed exclusions."""

    ordinary = max(1, min(int(base_cap), int(configured)))
    compensation = min(3, max(0, int(artifact_template_count)))
    return min(int(calibrated_cap), ordinary + compensation)


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
    if temporal.decision_status is FoamDecisionStatus.INCOHERENT_REJECTED:
        return ["FOAM_LAYER_INCOHERENT_REJECTED"]
    if temporal.decision_status is FoamDecisionStatus.STATIC_REJECTED:
        return ["FOAM_STATIC_ARTIFACT_REJECTED"]
    if temporal.decision_status is FoamDecisionStatus.WEAK_REJECTED or (
        foam.candidate is not None and foam.candidate.rejected
    ):
        return ["FOAM_COMPONENT_REJECTED"]
    return []


def _foam_static_match(
    current_mask: np.ndarray,
    static_map: np.ndarray | None,
) -> FoamStaticMatch:
    if static_map is None:
        return FoamStaticMatch()
    if current_mask.shape != static_map.shape:
        raise ValueError("Foam and learned static maps must share one raster shape.")
    current = current_mask > 0
    static = static_map > 0
    current_count = int(np.count_nonzero(current))
    static_count = int(np.count_nonzero(static))
    if current_count == 0 or static_count == 0:
        return FoamStaticMatch()

    radius = max(1, min(3, int(round(min(current.shape[:2]) * 0.01))))
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (2 * radius + 1, 2 * radius + 1),
    )
    dilated_static = cv2.dilate(static.astype(np.uint8), kernel) > 0
    dilated_current = cv2.dilate(current.astype(np.uint8), kernel) > 0
    return FoamStaticMatch(
        exact_overlap=(
            float(np.count_nonzero(current & static)) / current_count
        ),
        tolerant_overlap=(
            float(np.count_nonzero(current & dilated_static)) / current_count
        ),
        reciprocal_overlap=(
            float(np.count_nonzero(static & dilated_current)) / static_count
        ),
        tolerance_radius_px=radius,
    )


def _effective_photometric_metrics(
    pre: PreprocessResult,
    effective_mask: np.ndarray,
) -> dict[str, float]:
    effective = effective_mask > 0
    values = pre.gray[effective].astype(np.float32, copy=False)
    if values.size == 0:
        return {
            "effective_gray_mean": 0.0,
            "effective_gray_std": 0.0,
            "effective_gray_dynamic_range": 0.0,
            "effective_edge_density": 0.0,
        }
    lower, upper = np.percentile(values, (5.0, 95.0))
    return {
        "effective_gray_mean": float(np.mean(values)),
        "effective_gray_std": float(np.std(values)),
        "effective_gray_dynamic_range": float(upper - lower),
        "effective_edge_density": float(np.count_nonzero(pre.canny[effective]))
        / float(values.size),
    }


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
