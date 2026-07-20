from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import cv2
import numpy as np

from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import FillState, InitialObservationState
from oil_tracker.domain.recipe import GlassInspectionConfig

from .candidate_generators import generate_oil_air_candidates
from .candidate_scorer import CandidateScoreContext, score_candidates, select_best_candidate
from .fill_state_classifier import classify_fill_state
from .foam_front_detector import FoamDetectionResult, detect_bottom_connected_foam
from .geometry_masks import MaskBundle, build_mask_bundle
from .preprocessing import PreprocessResult, preprocess
from .temporal_tracker import TemporalTracker


@dataclass
class PhaseDetectionDebugArtifacts:
    images: dict[str, np.ndarray] = field(default_factory=dict)
    profiles: dict[str, list[float]] = field(default_factory=dict)
    candidate_rows: list[dict[str, Any]] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)


class OpenCvPhaseDetector:
    def __init__(self) -> None:
        self._trackers: dict[str, TemporalTracker] = {}
        self._static_maps: dict[str, np.ndarray] = {}

    def reset(self, glass_id: str | None = None) -> None:
        if glass_id is None:
            self._trackers.clear()
            self._static_maps.clear()
        else:
            self._trackers.pop(glass_id, None)
            self._static_maps.pop(glass_id, None)

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
            prior = _initial_prior(glass.initial_state)
            tracker.current_state = prior
            self._trackers[glass.id] = tracker

        bundle = build_mask_bundle(frame, glass)
        pre = preprocess(bundle.crop, bundle.effective_mask, settings)
        candidates = generate_oil_air_candidates(pre, bundle.effective_mask, settings)
        previous_local = tracker.previous_y - bundle.crop_origin[1] if tracker.previous_y is not None else None
        previous_state = tracker.current_state
        static_map = self._static_maps.get(glass.id)
        scored = score_candidates(
            candidates,
            CandidateScoreContext(
                pre=pre,
                effective_mask=bundle.effective_mask,
                ellipse_mask=bundle.ellipse_mask,
                exclusion_mask=bundle.exclusion_mask,
                settings=settings,
                previous_y=previous_local,
                previous_state=previous_state,
                static_artifact_map=static_map,
            ),
        )
        selected = select_best_candidate(scored, settings.minimum_final_confidence)
        foam = detect_bottom_connected_foam(pre.gray, pre.canny, bundle.effective_mask, settings)
        foam_candidate = foam.candidate
        proposed_state, visibility, flags = classify_fill_state(
            pre.gray,
            bundle.effective_mask,
            pre.glare_mask,
            selected,
            foam_candidate,
            previous_state,
            settings,
        )
        valid_rows = np.where(bundle.effective_mask.any(axis=1))[0]
        if selected is None and proposed_state == FillState.UNKNOWN_REVIEW and "FOGGED_OR_GLARE" not in flags:
            flags.append("DETECTION_LOST")
        if foam_candidate is not None and valid_rows.size:
            foam_relative = (foam_candidate.y - float(valid_rows.min())) / max(1.0, float(np.ptp(valid_rows)))
            if foam_relative <= 0.12:
                flags.append("FOAM_REACH_TOP")

        origin_y = bundle.crop_origin[1]
        raw_oil_source = selected.y + origin_y if selected else None
        raw_foam_source = foam_candidate.y + origin_y if foam_candidate else None
        smoothed_oil, smoothed_foam, stabilized_state = tracker.update(raw_oil_source, raw_foam_source, proposed_state)

        oil_conf = selected.final_score if selected else 0.0
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

        # Store candidate y in canonical source-frame coordinates.
        for candidate in scored:
            candidate.features.setdefault("local_y", candidate.y)
            candidate.y += origin_y
        if foam_candidate is not None:
            foam_candidate.features.setdefault("local_y", foam_candidate.y)
            foam_candidate.y += origin_y
            scored.append(foam_candidate)

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
            candidates=scored,
            flags=sorted(set(flags)),
            debug_metrics={
                "glare_ratio": float(np.count_nonzero(pre.glare_mask)) / max(1, np.count_nonzero(bundle.effective_mask)),
                "foam_bottom_connected_area_ratio": foam.bottom_connected_area_ratio,
                "effective_area": int(np.count_nonzero(bundle.effective_mask)),
                "previous_state": previous_state.value if previous_state else None,
                "proposed_state": proposed_state.value,
                "stabilized_state": stabilized_state.value,
            },
        )
        artifacts = self._debug_artifacts(frame, glass, bundle, pre, foam, detection, static_map) if debug else None
        return detection, artifacts

    def _debug_artifacts(
        self,
        frame: np.ndarray,
        glass: GlassInspectionConfig,
        bundle: MaskBundle,
        pre: PreprocessResult,
        foam: FoamDetectionResult,
        detection: PhaseDetection,
        static_map: np.ndarray | None,
    ) -> PhaseDetectionDebugArtifacts:
        overlay = frame.copy()
        e = glass.geometry.ellipse
        cv2.ellipse(overlay, (int(e.center_x), int(e.center_y)), (int(e.radius_x), int(e.radius_y)), 0, 0, 360, (0, 220, 255), 2)
        if glass.geometry.zero_line_y is not None:
            extent = e.horizontal_extent_at(glass.geometry.zero_line_y)
            if extent:
                cv2.line(overlay, (int(extent[0]), int(glass.geometry.zero_line_y)), (int(extent[1]), int(glass.geometry.zero_line_y)), (255, 255, 0), 1)
        for candidate in detection.candidates:
            extent = e.horizontal_extent_at(float(candidate.y))
            if extent is None:
                continue
            if candidate.kind.value == "foam_front":
                color = (255, 0, 255)
            else:
                color = (0, 255, 0) if candidate.selected else (0, 0, 255)
            cv2.line(
                overlay,
                (int(extent[0]), int(candidate.y)),
                (int(extent[1]), int(candidate.y)),
                color,
                2 if candidate.selected else 1,
                cv2.LINE_AA,
            )
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
            "static_artifact_map": static_map if static_map is not None else np.zeros_like(bundle.effective_mask),
        }
        rows = []
        for rank, c in enumerate(sorted(detection.candidates, key=lambda x: x.final_score, reverse=True), 1):
            rows.append(
                {
                    "rank": rank,
                    "kind": c.kind.value,
                    "source": c.source,
                    "y": c.y,
                    **c.features,
                    **c.penalties,
                    "feature_score": c.feature_score,
                    "penalty": c.penalty,
                    "final_score": c.final_score,
                    "selected": c.selected,
                    "rejected": c.rejected,
                    "reject_reason": c.reject_reason,
                }
            )
        return PhaseDetectionDebugArtifacts(
            images=images,
            candidate_rows=rows,
            state={
                "fill_state": detection.fill_state.value,
                "oil_air_confidence": detection.oil_air_confidence,
                "foam_confidence": detection.foam_confidence,
                "visibility_confidence": detection.visibility_confidence,
                "overall_confidence": detection.overall_confidence,
                "flags": detection.flags,
                **detection.debug_metrics,
            },
        )


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
