from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.oil_no_interface import evaluate_no_interface
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind, FillState
from oil_tracker.domain.recipe import DetectorSettings


def _candidate(score: float, *, rejected: bool = False) -> BoundaryCandidate:
    value = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        24.0,
        {
            "observation_score": score,
            "unique_generator_support_count": 1.0,
        },
    )
    value.final_score = score
    value.rejected = rejected
    return value


def _evidence(image: np.ndarray, candidates=(), previous_state=None, settings=None):
    settings = settings or DetectorSettings()
    mask = np.full(image.shape[:2], 255, dtype=np.uint8)
    pre = preprocess(image, mask, settings)
    return evaluate_no_interface(pre, mask, candidates, previous_state, settings)


def test_uniform_dark_full_scene_prefers_no_interface():
    image = np.full((48, 64, 3), 75, dtype=np.uint8)
    evidence = _evidence(image, previous_state=FillState.FULL_NO_INTERFACE)
    assert evidence.available
    assert evidence.score >= 0.58
    assert evidence.uniformity_score > 0.8
    assert evidence.boundary_score == 0.0


def test_uniform_bright_empty_scene_prefers_no_interface():
    image = np.full((48, 64, 3), 190, dtype=np.uint8)
    evidence = _evidence(image, previous_state=FillState.EMPTY_NO_INTERFACE)
    assert evidence.available
    assert evidence.score >= 0.58
    assert evidence.mean_intensity is not None


def test_clear_strong_boundary_caps_no_interface_score():
    image = np.full((48, 64, 3), 180, dtype=np.uint8)
    image[24:] = 60
    evidence = _evidence(image, [_candidate(0.90)])
    assert evidence.boundary_score == 0.90
    assert evidence.score <= 0.42
    assert evidence.reason == "strong_boundary_evidence"


def test_weak_structural_candidate_can_lose_to_no_interface():
    image = np.full((48, 64, 3), 90, dtype=np.uint8)
    image[23:25] = 120
    evidence = _evidence(image, [_candidate(0.30)])
    assert evidence.score > evidence.boundary_score
    assert evidence.reason in {
        "uniform_region_with_weak_boundary",
        "weak_boundary_evidence",
    }


def test_glare_visibility_conflict_is_explicit_and_finite():
    settings = DetectorSettings(glare_threshold=220, glare_ratio_unknown=0.35)
    image = np.full((48, 64, 3), 255, dtype=np.uint8)
    evidence = _evidence(image, settings=settings)
    assert not evidence.available
    assert evidence.reason == "insufficient_visible_pixels"
    assert np.isfinite(evidence.glare_conflict)
    assert np.isfinite(evidence.score)
