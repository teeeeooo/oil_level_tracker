from __future__ import annotations

from itertools import permutations

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


def test_static_candidates_use_candidate_local_witnesses_deterministically():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)

    def make_candidates():
        return [
            _scored_scalar_candidate(40.0, -1.0, static_overlap=0.20),
            _scored_scalar_candidate(44.0, 1.0, static_overlap=0.25),
            _scored_scalar_candidate(48.0, -1.0, static_overlap=0.30),
            _scored_scalar_candidate(52.0, 1.0, static_overlap=0.20),
        ]

    expected = None
    for order in permutations(range(4)):
        values = make_candidates()
        arranged = [values[index] for index in order]
        suppress_paired_horizontal_structures(arranged, settings)
        signature = tuple(
            sorted(
                (
                    candidate.y,
                    candidate.rejected,
                    candidate.reject_reason,
                    candidate.features["candidate_local_static_structure"],
                    candidate.features["candidate_local_static_partner_y"],
                )
                for candidate in arranged
            )
        )
        expected = signature if expected is None else expected
        assert signature == expected
        assert all(candidate.rejected for candidate in arranged)
        assert {
            candidate.reject_reason for candidate in arranged
        } == {"candidate_local_static_structure"}
        assert all(
            candidate.features["multi_edge_static_structure"] == 0.0
            for candidate in arranged
        )


def test_undercovered_static_false_candidates_do_not_consume_weak_fringe():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)

    def make_candidates():
        return [
            _scored_scalar_candidate(
                40.0,
                -1.0,
                observation=0.96,
                persistent_contrast=0.44,
                persistent_polarity=-1.0,
                static_overlap=0.053,
                consensus=0.92,
                support=4,
            ),
            _scored_scalar_candidate(44.0, 1.0, static_overlap=0.064),
            _scored_scalar_candidate(48.0, -1.0, static_overlap=0.091),
            _scored_scalar_candidate(
                52.0,
                1.0,
                observation=0.98,
                persistent_contrast=0.52,
                persistent_polarity=1.0,
                static_overlap=0.052,
                consensus=0.93,
                support=4,
            ),
            _scored_scalar_candidate(
                58.0,
                -1.0,
                observation=0.30,
                persistent_contrast=0.21,
                persistent_polarity=1.0,
                static_overlap=0.0,
                consensus=0.40,
                support=2,
            ),
        ]

    expected = None
    for order in permutations(range(5)):
        values = make_candidates()
        arranged = [values[index] for index in order]
        suppress_paired_horizontal_structures(arranged, settings)
        signature = tuple(
            sorted(
                (
                    candidate.y,
                    candidate.rejected,
                    candidate.reject_reason,
                    candidate.features["candidate_local_static_structure"],
                )
                for candidate in arranged
            )
        )
        expected = signature if expected is None else expected
        assert signature == expected
        assert {
            candidate.y for candidate in arranged if candidate.rejected
        } == {40.0, 44.0, 48.0, 52.0}
        survivor = next(candidate for candidate in arranged if not candidate.rejected)
        assert survivor.y == 58.0
        assert survivor.features["candidate_local_static_structure"] == 0.0


def test_real_boundary_between_static_anchors_is_not_suppressed():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    upper_anchor = _scored_scalar_candidate(
        40.0,
        -1.0,
        static_overlap=0.20,
    )
    real = _scored_scalar_candidate(
        44.0,
        1.0,
        observation=0.62,
        persistent_contrast=0.28,
        persistent_polarity=1.0,
    )
    lower_anchor = _scored_scalar_candidate(
        48.0,
        -1.0,
        static_overlap=0.25,
    )
    suppress_paired_horizontal_structures(
        [lower_anchor, real, upper_anchor],
        settings,
    )
    assert not real.rejected
    assert real.reject_reason == ""
    assert real.features["candidate_local_static_structure"] == 0.0


def test_weak_real_boundary_immediately_outside_static_pair_is_preserved():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    static_group = [
        _scored_scalar_candidate(40.0, -1.0, static_overlap=0.04),
        _scored_scalar_candidate(44.0, 1.0, static_overlap=0.05),
    ]
    real = _scored_scalar_candidate(
        48.0,
        -1.0,
        observation=0.30,
        persistent_contrast=0.20,
        persistent_polarity=-1.0,
        consensus=0.40,
        support=2,
    )
    values = static_group + [real]
    suppress_paired_horizontal_structures(values, settings)
    assert all(candidate.rejected for candidate in static_group)
    assert not real.rejected
    assert real.features["candidate_local_static_structure"] == 0.0


def test_persistent_real_step_crossing_static_candidates_is_preserved():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    static_false = [
        _scored_scalar_candidate(32.0, -1.0, static_overlap=0.20),
        _scored_scalar_candidate(36.0, 1.0, static_overlap=0.22),
        _scored_scalar_candidate(52.0, -1.0, static_overlap=0.24),
        _scored_scalar_candidate(56.0, 1.0, static_overlap=0.21),
    ]
    real_upper = _scored_scalar_candidate(
        41.0,
        1.0,
        region_contrast=0.68,
        persistent_contrast=0.88,
        persistent_polarity=1.0,
        static_overlap=0.18,
    )
    real_lower = _scored_scalar_candidate(
        47.0,
        -1.0,
        region_contrast=0.62,
        persistent_contrast=0.84,
        persistent_polarity=1.0,
        static_overlap=0.16,
    )
    values = static_false + [real_upper, real_lower]
    suppress_paired_horizontal_structures(values, settings)
    kept = [candidate for candidate in values if not candidate.rejected]
    assert len(kept) == 1
    assert kept[0].y == 44.0
    assert kept[0].features["paired_boundary_step_preserved"] == 1.0
    assert kept[0].features[
        "candidate_local_static_protected_persistent_step"
    ] == 1.0
    assert all(candidate.rejected for candidate in static_false)


def test_close_static_structures_keep_local_partner_identity():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)

    def make_candidates():
        return [
            _scored_scalar_candidate(40.0, -1.0, static_overlap=0.20),
            _scored_scalar_candidate(44.0, 1.0, static_overlap=0.20),
            _scored_scalar_candidate(55.0, -1.0, static_overlap=0.20),
            _scored_scalar_candidate(59.0, 1.0, static_overlap=0.20),
        ]

    expected = None
    for order in permutations(range(4)):
        values = make_candidates()
        arranged = [values[index] for index in order]
        suppress_paired_horizontal_structures(arranged, settings)
        signature = tuple(
            sorted(
                (
                    candidate.y,
                    candidate.features["candidate_local_static_partner_y"],
                    candidate.features["multi_edge_static_span_px"],
                )
                for candidate in arranged
            )
        )
        expected = signature if expected is None else expected
        assert signature == expected
    assert expected == (
        (40.0, 44.0, 0.0),
        (44.0, 40.0, 0.0),
        (55.0, 59.0, 0.0),
        (59.0, 55.0, 0.0),
    )


def test_pre_rejected_candidates_never_anchor_static_rejection():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    for reason in (
        "glare_overlap",
        "rim_or_border",
        "implausible_full_to_visible_transition",
    ):
        anchor = _scored_scalar_candidate(
            40.0,
            -1.0,
            static_overlap=0.20,
            rejected=True,
            reject_reason=reason,
        )
        real = _scored_scalar_candidate(
            44.0,
            1.0,
            observation=0.55,
            static_overlap=0.18,
        )
        suppress_paired_horizontal_structures([anchor, real], settings)
        assert anchor.rejected
        assert anchor.reject_reason == reason
        assert not real.rejected
        assert real.features["candidate_local_static_structure"] == 0.0


def test_pre_rejected_static_member_does_not_remove_nearby_real_boundary():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    static_group = [
        _scored_scalar_candidate(40.0, -1.0, static_overlap=0.20),
        _scored_scalar_candidate(44.0, 1.0, static_overlap=0.25),
        _scored_scalar_candidate(48.0, -1.0, static_overlap=0.30),
        _scored_scalar_candidate(
            52.0,
            1.0,
            observation=0.20,
            static_overlap=0.20,
            rejected=True,
            reject_reason="insufficient_boundary_observation",
        ),
    ]
    real = _scored_scalar_candidate(
        58.0,
        -1.0,
        observation=0.95,
        persistent_contrast=0.90,
        persistent_polarity=-1.0,
    )
    values = static_group + [real]
    suppress_paired_horizontal_structures(values, settings)
    assert not real.rejected
    assert real.reject_reason == ""
    assert static_group[-1].reject_reason == "insufficient_boundary_observation"
    assert all(candidate.rejected for candidate in static_group)


def test_low_observation_pre_rejected_partner_does_not_suppress_accepted():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    primary = _scored_scalar_candidate(40.0, 1.0, static_overlap=0.20)
    partner = _scored_scalar_candidate(
        47.0,
        -1.0,
        observation=0.20,
        static_overlap=0.15,
        rejected=True,
        reject_reason="insufficient_boundary_observation",
    )
    suppress_paired_horizontal_structures([primary, partner], settings)
    assert not primary.rejected
    assert primary.features["candidate_local_static_structure"] == 0.0
    assert partner.rejected
    assert partner.reject_reason == "insufficient_boundary_observation"


def test_persistent_step_does_not_resurrect_pre_rejected_candidate():
    settings = DetectorSettings(oil_consensus_tolerance_px=4.0)
    accepted = _scored_scalar_candidate(
        40.0,
        1.0,
        region_contrast=0.70,
        persistent_contrast=0.90,
        persistent_polarity=1.0,
    )
    rejected = _scored_scalar_candidate(
        46.0,
        -1.0,
        observation=0.30,
        region_contrast=0.65,
        persistent_contrast=0.85,
        persistent_polarity=1.0,
        rejected=True,
        reject_reason="insufficient_boundary_observation",
    )
    suppress_paired_horizontal_structures([rejected, accepted], settings)
    assert not accepted.rejected
    assert accepted.y == 40.0
    assert rejected.rejected
    assert rejected.reject_reason == "insufficient_boundary_observation"


def _scored_scalar_candidate(
    y: float,
    polarity: float,
    *,
    observation: float = 0.90,
    region_contrast: float = 0.0,
    persistent_contrast: float = 0.0,
    persistent_polarity: float = 0.0,
    static_overlap: float = 0.0,
    consensus: float = 0.80,
    support: int = 3,
    rejected: bool = False,
    reject_reason: str = "",
) -> BoundaryCandidate:
    candidate = BoundaryCandidate(
        "oil_consensus",
        BoundaryKind.OIL_AIR,
        y,
        {
            "observation_score": observation,
            "polarity_score": abs(polarity),
            "polarity_sign": polarity,
            "region_contrast": region_contrast,
            "persistent_region_contrast": persistent_contrast,
            "persistent_polarity_sign": persistent_polarity,
            "static_overlap": static_overlap,
            "consensus_score": consensus,
            "unique_generator_support_count": float(support),
        },
    )
    candidate.final_score = observation
    candidate.rejected = rejected
    candidate.reject_reason = reject_reason
    candidate.penalties["paired_structure_penalty"] = 0.0
    return candidate
