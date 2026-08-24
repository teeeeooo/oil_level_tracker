from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

from oil_tracker.domain.detection import PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .foam_front_detector import detect_bottom_connected_foam
from .foam_temporal_gate import FoamTemporalGate
from .geometry_masks import MaskBundle, build_mask_bundle
from .observation_sequence_resolver import (
    ObservationSequenceResolution,
    ObservationSequenceResolver,
)
from .oil_shadow_pipeline import OilHypothesisPipeline
from .oil_shadow_types import (
    OilCanonicalOutcome,
    PipelineFailureOutcome,
    PipelineFailureStage,
)
from .phase_frame_detection import (
    CurrentFrameEvidenceOwner,
    CurrentFrameResultProjector,
    PhaseDebugProjector,
    PhaseDetectionDebugArtifacts,
    foam_static_match as _foam_static_match,
)
from .preprocessing import PreprocessResult, preprocess
from .temporal_raster_evidence import (
    RegisteredFoamMotionTracker,
    RegisteredOilMotionTracker,
)
from .temporal_tracker import TemporalTracker


class OpenCvPhaseDetector:
    version = "opencv-phase-detector-r17-physical-observation-ownership-v3"

    def __init__(self) -> None:
        self._trackers: dict[str, TemporalTracker] = {}
        self._static_maps: dict[str, np.ndarray] = {}
        self._static_foam_maps: dict[str, np.ndarray] = {}
        self._foam_gate = FoamTemporalGate()
        self._oil_pipeline = OilHypothesisPipeline()
        self._foam_motion_tracker = RegisteredFoamMotionTracker()
        self._oil_motion_tracker = RegisteredOilMotionTracker()
        self._observation_sequence_resolver = ObservationSequenceResolver()
        self._frame_evidence_owner = CurrentFrameEvidenceOwner(
            evaluate_oil=self._evaluate_oil_pipeline,
            foam_gate=self._foam_gate,
            foam_motion_tracker=self._foam_motion_tracker,
            oil_motion_tracker=self._oil_motion_tracker,
            static_maps=self._static_maps,
            static_foam_maps=self._static_foam_maps,
        )
        self._frame_result_projector = CurrentFrameResultProjector()
        self._debug_projector = PhaseDebugProjector(self._static_foam_maps)

    @property
    def foam_temporal_state_count(self) -> int:
        return self._foam_gate.state_count

    @property
    def oil_temporal_state_count(self) -> int:
        return self._oil_pipeline.temporal_state_count

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
        detections: Sequence[PhaseDetection],
        glass: GlassInspectionConfig,
        confirmed_initial_state: InitialObservationState | None = None,
    ) -> ObservationSequenceResolution:
        """Resolve the completed analysis window before public sample projection."""

        return self._observation_sequence_resolver.resolve(
            detections,
            glass,
            confirmed_initial_state,
        )

    def learn_static_artifact(
        self,
        frames: Sequence[np.ndarray],
        glass: GlassInspectionConfig,
    ) -> None:
        if not frames:
            return
        maps = []
        foam_maps = []
        for frame in frames:
            bundle = build_mask_bundle(frame, glass)
            pre = preprocess(
                bundle.crop,
                bundle.effective_mask,
                glass.detector_settings,
            )
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
        self._static_maps[glass.id] = np.where(
            persistence >= 0.75,
            255,
            0,
        ).astype(np.uint8)
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
        tracker = self._tracker_for(glass)
        evidence = self._frame_evidence_owner.observe(frame, glass)
        projection = self._frame_result_projector.project(
            evidence,
            tracker,
            glass,
            frame_index,
            time_sec,
            debug=debug,
        )
        artifacts = (
            self._debug_projector.project(frame, glass, evidence, projection)
            if debug
            else None
        )
        return projection.detection, artifacts

    def _tracker_for(self, glass: GlassInspectionConfig) -> TemporalTracker:
        settings = glass.detector_settings
        tracker = self._trackers.get(glass.id)
        if tracker is None:
            tracker = TemporalTracker(
                settings.smoothing_window,
                settings.state_hold_frames,
            )
            tracker.current_state = _initial_prior(glass.initial_state)
            self._trackers[glass.id] = tracker
        else:
            tracker.smoothing_window = max(1, int(settings.smoothing_window))
            tracker.state_hold_frames = max(1, int(settings.state_hold_frames))
        return tracker

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
            None
            if static_map is None
            else _isolated_readonly_copy(static_map)
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


def _initial_prior(initial: InitialObservationState) -> FillState | None:
    if initial is InitialObservationState.AUTO:
        return None
    return FillState(initial.value)
