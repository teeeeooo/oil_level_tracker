from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_observation_resolver import OilObservationResolver
from oil_tracker.adapters.vision.opencv_phase_detector import OpenCvPhaseDetector
from oil_tracker.domain.detection import BoundaryCandidate, PhaseDetection
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import InspectionRecipe
from tests.diagnostics import s11_r16_performance_profile as performance_profile


CURRENT_FRAME_FINGERPRINT = (
    "b9770bca0b310ff1881c7e9cf3e67fb838ce39cb04059ef9615d3071b9b4ffee"
)
R0_COMPLETED_WINDOW_FINGERPRINT = (
    "1050ca7966600d67b0cd430225c562c7ea32ae3329c3bad260bff89593b5cbe0"
)
R19_BOUNDED_DRAIN_RELEASE_COMPLETED_WINDOW_FINGERPRINT = (
    # R19 adds bounded release-chain diagnostics while preserving same-frame
    # candidate/projection provenance and the existing Foam contracts.
    "d9361d21006c96ceb5c8bdd3efe1d923f355489334e823fe27f1421de7fb8fbb"
)


def test_performance_evidence_requires_the_exact_clean_source_head(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path("/repository")
    monkeypatch.setattr(performance_profile, "_git_head", lambda _root: "abc123")
    monkeypatch.setattr(performance_profile, "_git_status", lambda _root: "")

    assert performance_profile._exact_source_head(root, "abc123") == "abc123"
    with pytest.raises(RuntimeError, match="source head mismatch"):
        performance_profile._exact_source_head(root, "def456")

    monkeypatch.setattr(
        performance_profile,
        "_git_status",
        lambda _root: " M src/oil_tracker/example.py",
    )
    with pytest.raises(RuntimeError, match="clean exact source head"):
        performance_profile._exact_source_head(root, "abc123")


def _glass(glass_id: str = "r0-characterization"):
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = glass_id
    glass.geometry.zero_line_y = 150.0
    glass.detector_settings.minimum_final_confidence = 0.35
    return glass


def _oil_frame(y: int = 130) -> np.ndarray:
    frame = np.full((240, 320, 3), 175, dtype=np.uint8)
    frame[y:] = 70
    frame[y - 1 : y + 2] = 225
    return frame


def _candidate_payload(candidate: BoundaryCandidate) -> dict[str, object]:
    return {
        "source": candidate.source,
        "kind": candidate.kind.value,
        "y": candidate.y,
        "features": candidate.features,
        "penalties": candidate.penalties,
        "feature_score": candidate.feature_score,
        "penalty": candidate.penalty,
        "final_score": candidate.final_score,
        "selected": candidate.selected,
        "rejected": candidate.rejected,
        "reject_reason": candidate.reject_reason,
    }


def _image_signatures(images: dict[str, np.ndarray]) -> tuple[tuple[object, ...], ...]:
    return tuple(
        sorted(
            (
                key,
                value.shape,
                str(value.dtype),
                sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            )
            for key, value in images.items()
        )
    )


def _fingerprint(payload: object) -> str:
    canonical = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _sequence_candidate(
    y: float,
    *,
    boundary: float,
    broad: float,
    artifact: float,
    ambiguity: float,
) -> BoundaryCandidate:
    return BoundaryCandidate(
        source=f"candidate-{y}",
        kind=BoundaryKind.OIL_AIR,
        y=y,
        features={
            "boundary_likelihood": boundary,
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "evidence_availability": 1.0,
            "visibility": 1.0,
            "broad_strength": broad,
            "narrow_peak_strength": boundary,
            "narrow_horizontal_coverage": 0.65,
            "broad_scale_consistency": 0.75,
            "polarity_confidence": 0.65,
            "static_prior_contribution": 0.0,
            "sequence_eligible": 1.0,
            "registered_motion_available": 0.0,
            "registered_internal_motion_support": 0.0,
            "registered_dynamic_support": 0.0,
            "registered_oil_band_motion_support": 0.0,
            "registered_oil_band_motion_coverage": 0.0,
        },
        penalties={
            "artifact_likelihood": artifact,
            "ambiguity_likelihood": ambiguity,
            "glare_conflict": 0.0,
            "border_penalty": 0.0,
            "exclusion_conflict": 0.0,
            "material_texture_conflict": 0.0,
        },
        feature_score=boundary,
        final_score=boundary,
    )


def _sequence_detection(index: int, candidate: BoundaryCandidate) -> PhaseDetection:
    ambiguity = candidate.features["ambiguity_likelihood"]
    return PhaseDetection(
        glass_id="r0-characterization",
        frame_index=index,
        time_sec=index * 0.5,
        fill_state=FillState.UNKNOWN_REVIEW,
        candidates=[candidate],
        visibility_confidence=1.0,
        overall_confidence=0.2,
        debug_metrics={
            "oil_ambiguity_score": ambiguity,
            "oil_no_interface_score": 0.0,
            "oil_no_interface_full_likelihood": 0.0,
            "oil_no_interface_empty_likelihood": 0.0,
            "proposed_state": FillState.UNKNOWN_REVIEW.value,
        },
    )


def test_r0_current_frame_candidate_and_debug_projection_fingerprint() -> None:
    detection, artifacts = OpenCvPhaseDetector().detect(
        _oil_frame(),
        _glass(),
        1,
        0.0,
        debug=True,
    )
    assert artifacts is not None

    payload = {
        "detection": {
            "frame_index": detection.frame_index,
            "time_sec": detection.time_sec,
            "fill_state": detection.fill_state.value,
            "oil_air_level_y": detection.oil_air_level_y,
            "foam_front_y": detection.foam_front_y,
            "oil_air_confidence": detection.oil_air_confidence,
            "foam_confidence": detection.foam_confidence,
            "visibility_confidence": detection.visibility_confidence,
            "overall_confidence": detection.overall_confidence,
            "raw_oil_air_level_y": detection.raw_oil_air_level_y,
            "raw_foam_front_y": detection.raw_foam_front_y,
            "smoothed_oil_air_level_y": detection.smoothed_oil_air_level_y,
            "smoothed_foam_front_y": detection.smoothed_foam_front_y,
            "flags": detection.flags,
            "candidates": [_candidate_payload(item) for item in detection.candidates],
            "debug_metrics": detection.debug_metrics,
        },
        "artifacts": {
            "profiles": artifacts.profiles,
            "candidate_rows": artifacts.candidate_rows,
            "state": artifacts.state,
            "images": _image_signatures(artifacts.images),
        },
    }

    assert _fingerprint(payload) == CURRENT_FRAME_FINGERPRINT


def test_r0_completed_window_stage_and_provenance_fingerprint() -> None:
    detections = tuple(
        _sequence_detection(
            index,
            _sequence_candidate(
                160.0 - index,
                boundary=0.72 if index < 3 or index >= 8 else 0.24,
                broad=0.62 if index < 3 or index >= 8 else 0.30,
                artifact=0.08 if index < 3 or index >= 8 else 0.21,
                ambiguity=0.20 if index < 3 or index >= 8 else 0.62,
            ),
        )
        for index in range(11)
    )

    result = OilObservationResolver().resolve(detections, _glass())
    payload = {
        "diagnostics": asdict(result.diagnostics),
        "detections": [
            {
                "frame_index": detection.frame_index,
                "time_sec": detection.time_sec,
                "fill_state": detection.fill_state.value,
                "raw_oil_air_level_y": detection.raw_oil_air_level_y,
                "oil_air_level_y": detection.oil_air_level_y,
                "oil_air_confidence": detection.oil_air_confidence,
                "overall_confidence": detection.overall_confidence,
                "flags": detection.flags,
                    "sequence_metrics": {
                        key: value
                        for key, value in detection.debug_metrics.items()
                        if key.startswith("sequence_")
                        and key
                        not in {
                            "sequence_material_phase_diagnostics",
                            "sequence_foam_episode_diagnostics",
                        }
                    },
                "candidates": [
                    _candidate_payload(item) for item in detection.candidates
                ],
            }
            for detection in result.detections
        ],
    }

    fingerprint = _fingerprint(payload)
    assert fingerprint == R19_BOUNDED_DRAIN_RELEASE_COMPLETED_WINDOW_FINGERPRINT
    assert fingerprint != R0_COMPLETED_WINDOW_FINGERPRINT
    for source, resolved in zip(detections, result.detections, strict=True):
        assert resolved.raw_oil_air_level_y in {
            candidate.y for candidate in source.candidates
        }
        assert sum(candidate.selected for candidate in resolved.candidates) == 1
