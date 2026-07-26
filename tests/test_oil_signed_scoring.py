from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.candidate_scorer import (
    CandidateScoreContext,
    score_candidates,
    suppress_paired_horizontal_structures,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


def _score(
    above: int,
    below: int,
    *,
    glare: bool = False,
    excluded: bool = False,
):
    settings = DetectorSettings(
        minimum_final_confidence=0.05,
        minimum_horizontal_coverage=0.0,
        minimum_region_contrast=0.0,
        oil_min_polarity_score=0.0,
    )
    image = np.full((48, 64), above, dtype=np.uint8)
    image[24:] = below
    mask = np.full_like(image, 255)
    exclusion = np.zeros_like(image)
    if glare:
        image[19:29, 10:54] = 255
    if excluded:
        mask[19:24, :] = 0
        exclusion[19:24, :] = 255
    pre = preprocess(image, mask, settings)
    candidate = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        24.0,
        {
            "generator_strength": 0.9,
            "consensus_score": 0.8,
            "unique_generator_support_count": 3.0,
        },
    )
    scored = score_candidates(
        [candidate],
        CandidateScoreContext(
            pre=pre,
            effective_mask=mask,
            ellipse_mask=np.full_like(mask, 255),
            exclusion_mask=exclusion,
            settings=settings,
        ),
    )[0]
    return image, mask, scored


def _score_stationary_weak_boundary(*, static_overlap: bool) -> BoundaryCandidate:
    settings = DetectorSettings(
        minimum_final_confidence=0.05,
        minimum_horizontal_coverage=0.0,
        minimum_region_contrast=0.0,
        oil_min_polarity_score=0.0,
    )
    image = np.full((48, 64), 115, dtype=np.uint8)
    image[24:] = 95
    mask = np.full_like(image, 255)
    static_map = np.zeros_like(image)
    if static_overlap:
        static_map[21:28] = 255
    pre = preprocess(image, mask, settings)
    candidate = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        24.0,
        {
            "generator_strength": 0.75,
            "consensus_score": 0.65,
            "unique_generator_support_count": 3.0,
        },
    )
    return score_candidates(
        [candidate],
        CandidateScoreContext(
            pre=pre,
            effective_mask=mask,
            ellipse_mask=mask,
            exclusion_mask=np.zeros_like(mask),
            settings=settings,
            static_artifact_map=static_map,
        ),
    )[0]


def test_static_overlap_is_bounded_penalty_not_hard_reject():
    baseline = _score_stationary_weak_boundary(static_overlap=False)
    penalized = _score_stationary_weak_boundary(static_overlap=True)
    assert not penalized.rejected
    assert penalized.reject_reason != "static_horizontal_structure"
    assert penalized.features["static_overlap"] > 0.0
    assert penalized.penalties["static_artifact_penalty"] > 0.0
    assert 0.0 <= penalized.final_score <= baseline.final_score <= 1.0
    assert (
        0.0
        <= penalized.features["observation_score"]
        <= baseline.features["observation_score"]
        <= 1.0
    )
    assert np.isfinite(penalized.final_score)
    assert np.isfinite(penalized.features["observation_score"])


def test_bright_above_dark_below_has_positive_signed_evidence():
    _image, _mask, candidate = _score(190, 70)
    assert candidate.features["signed_above_minus_below"] > 0.0
    assert candidate.features["polarity_sign"] == 1.0
    assert candidate.features["polarity_score"] > 0.5
    assert candidate.features["polarity_available"] == 1.0
    assert candidate.features["persistent_signed_above_minus_below"] > 0.0
    assert candidate.features["persistent_region_contrast"] > 0.5


def test_dark_above_bright_below_has_opposite_polarity():
    _image, _mask, candidate = _score(70, 190)
    assert candidate.features["signed_above_minus_below"] < 0.0
    assert candidate.features["polarity_sign"] == -1.0
    assert candidate.features["polarity_score"] > 0.5
    assert candidate.features["persistent_polarity_sign"] == -1.0


def test_weak_contrast_is_finite_and_low_polarity():
    _image, _mask, candidate = _score(104, 101)
    for value in candidate.features.values():
        assert np.isfinite(float(value))
    assert candidate.features["polarity_score"] < 0.25


def test_unavailable_band_is_explicit_and_not_nan():
    _image, _mask, candidate = _score(190, 70, excluded=True)
    assert candidate.features["polarity_available"] == 0.0
    assert candidate.features["signed_above_minus_below"] == 0.0
    assert np.isfinite(candidate.features["observation_score"])


def test_inputs_are_not_mutated_by_scoring():
    image, mask, _candidate = _score(190, 70, glare=True)
    image_before = image.copy()
    mask_before = mask.copy()
    _score(190, 70, glare=True)
    assert np.array_equal(image, image_before)
    assert np.array_equal(mask, mask_before)


def test_recent_opposite_polarity_is_penalized_not_hard_coded():
    settings = DetectorSettings(
        minimum_final_confidence=0.05,
        minimum_horizontal_coverage=0.0,
        minimum_region_contrast=0.0,
        oil_min_polarity_score=0.0,
    )
    image = np.full((48, 64), 70, dtype=np.uint8)
    image[24:] = 190
    mask = np.full_like(image, 255)
    pre = preprocess(image, mask, settings)
    candidate = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        24.0,
        {
            "generator_strength": 0.9,
            "consensus_score": 0.8,
            "unique_generator_support_count": 3.0,
        },
    )
    result = score_candidates(
        [candidate],
        CandidateScoreContext(
            pre,
            mask,
            mask,
            np.zeros_like(mask),
            settings,
            previous_polarity=1.0,
        ),
    )[0]
    assert result.features["polarity_sign"] == -1.0
    assert result.features["polarity_consistency"] < 0.5
    assert result.penalties["polarity_conflict_penalty"] > 0.0


def test_close_strong_opposite_polarity_pair_is_rejected_as_structure():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    upper = _scored_scalar_candidate(40.0, 1.0)
    lower = _scored_scalar_candidate(47.0, -1.0)
    suppress_paired_horizontal_structures([upper, lower], settings)
    assert upper.rejected and lower.rejected
    assert upper.reject_reason == "paired_opposite_polarity_structure"
    assert lower.reject_reason == "paired_opposite_polarity_structure"
    assert upper.features["paired_structure_distance_px"] == 7.0
    assert upper.penalties["paired_structure_penalty"] == 1.0


def test_opposite_local_edges_with_persistent_region_step_are_merged():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    upper = _scored_scalar_candidate(
        40.0,
        1.0,
        observation=0.92,
        persistent_contrast=0.90,
        persistent_polarity=1.0,
    )
    lower = _scored_scalar_candidate(
        46.0,
        -1.0,
        observation=0.82,
        persistent_contrast=0.84,
        persistent_polarity=1.0,
    )
    suppress_paired_horizontal_structures([upper, lower], settings)
    kept = [candidate for candidate in (upper, lower) if not candidate.rejected]
    rejected = [candidate for candidate in (upper, lower) if candidate.rejected]
    assert len(kept) == 1
    assert len(rejected) == 1
    assert kept[0].y == 43.0
    assert kept[0].features["paired_boundary_unrounded_midpoint"] == 43.0
    assert kept[0].features["paired_boundary_step_preserved"] == 1.0
    assert rejected[0].reject_reason == "paired_boundary_edge_duplicate"


def test_single_signed_boundary_is_not_rejected_as_structure():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    candidate = _scored_scalar_candidate(40.0, 1.0)
    suppress_paired_horizontal_structures([candidate], settings)
    assert not candidate.rejected
    assert candidate.features["paired_structure_opposite_polarity"] == 0.0


def _scored_scalar_candidate(
    y: float,
    polarity: float,
    *,
    observation: float = 0.90,
    persistent_contrast: float = 0.0,
    persistent_polarity: float = 0.0,
) -> BoundaryCandidate:
    candidate = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        y,
        {
            "observation_score": observation,
            "polarity_score": abs(polarity),
            "polarity_sign": polarity,
            "persistent_region_contrast": persistent_contrast,
            "persistent_polarity_sign": persistent_polarity,
            "unique_generator_support_count": 3.0,
        },
    )
    candidate.final_score = observation
    candidate.penalties["paired_structure_penalty"] = 0.0
    return candidate
