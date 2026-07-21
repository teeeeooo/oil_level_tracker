from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision.candidate_scorer import CandidateScoreContext, score_candidates
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.detection import BoundaryCandidate
from oil_tracker.domain.enums import BoundaryKind
from oil_tracker.domain.recipe import DetectorSettings


def _score(above: int, below: int, *, glare: bool = False, excluded: bool = False):
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
        # Remove every pixel from the upper statistics band while retaining the
        # candidate row itself inside the effective mask.
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


def test_bright_above_dark_below_has_positive_signed_evidence():
    _image, _mask, candidate = _score(190, 70)
    assert candidate.features["signed_above_minus_below"] > 0.0
    assert candidate.features["polarity_sign"] == 1.0
    assert candidate.features["polarity_score"] > 0.5
    assert candidate.features["polarity_available"] == 1.0


def test_dark_above_bright_below_has_opposite_polarity():
    _image, _mask, candidate = _score(70, 190)
    assert candidate.features["signed_above_minus_below"] < 0.0
    assert candidate.features["polarity_sign"] == -1.0
    assert candidate.features["polarity_score"] > 0.5


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
        {"generator_strength": 0.9, "consensus_score": 0.8, "unique_generator_support_count": 3.0},
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
