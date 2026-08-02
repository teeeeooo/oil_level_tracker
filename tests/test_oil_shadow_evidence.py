from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum
import math

import numpy as np
import pytest

from oil_tracker.adapters.vision import oil_shadow_observations
from oil_tracker.adapters.vision.oil_shadow_observations import (
    evaluate_typed_current_observation,
    semantic_deduplicate,
)
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilShadowPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    AcceptedBoundaryOutcome,
    AmbiguousOutcome,
    BroadScaleEvidence,
    EvidenceUnavailableOutcome,
    NoInterfaceOutcome,
    OilShadowBounds,
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
    ShadowHypothesisLabel,
    ShadowNoInterfaceEvidence,
    ShadowNoInterfaceObservation,
    stable_digest,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _assert_deep_scalar_immutable(value):
    if isinstance(value, np.ndarray):
        raise AssertionError("shadow result retained an ndarray")
    if isinstance(value, (list, dict, set)):
        raise AssertionError("shadow result retained a mutable container")
    if isinstance(value, tuple):
        for item in value:
            _assert_deep_scalar_immutable(item)
        return
    if isinstance(value, Enum) or value is None or isinstance(
        value, (str, int, float, bool)
    ):
        return
    if is_dataclass(value):
        for item in fields(value):
            _assert_deep_scalar_immutable(getattr(value, item.name))
        return
    raise AssertionError(f"unexpected retained type: {type(value)!r}")


def _run(image, *, static=None, exclusion=None, effective=None, glare_threshold=245):
    mask = np.full(image.shape[:2], 255, dtype=np.uint8) if effective is None else effective
    exclusion = np.zeros_like(mask) if exclusion is None else exclusion
    pre = preprocess(image, mask, DetectorSettings(glare_threshold=glare_threshold))
    return OilShadowPipeline().run(
        glass_id="glass-evidence",
        pre=pre,
        effective_mask=mask,
        ellipse_mask=np.full_like(mask, 255),
        exclusion_mask=exclusion,
        static_artifact_map=static,
        crop_origin_y=10.0,
    )


def _step(above=170, below=80, *, line=True):
    image = np.full((80, 100), above, dtype=np.uint8)
    image[40:] = below
    if line:
        image[39:42] = min(255, above + 50)
    return image


def test_broad_and_narrow_evidence_are_separate_for_clear_and_weak_steps():
    clear = _run(_step(line=False))
    weak = _run(_step(130, 115, line=False))
    assert clear.hypotheses and weak.hypotheses
    clear_h = clear.hypotheses[0]
    weak_h = weak.hypotheses[0]
    assert clear_h.broad.available_scale_count == len(OilShadowBounds().broad_band_scales)
    assert clear_h.broad.strength > 0.25
    assert clear_h.narrow.peak_strength > 0.0
    assert clear_h.broad.strength != clear_h.narrow.peak_strength
    assert weak_h.broad.strength > 0.0
    assert weak_h.broad.scale_consistency > 0.70
    assert all(scale.available for scale in weak_h.broad.scales)


def test_narrow_line_and_paired_pulse_raise_continuous_artifact_evidence():
    clear = _run(_step(line=False)).hypotheses[0]
    line = np.full((80, 100), 100, dtype=np.uint8)
    line[39:42] = 200
    line_result = _run(line)
    assert line_result.hypotheses
    assert max(item.artifact_likelihood for item in line_result.hypotheses) > clear.artifact_likelihood
    assert max(item.narrow.paired_edge_strength for item in line_result.hypotheses) > 0.80

    pair = np.full((80, 100), 100, dtype=np.uint8)
    pair[35:38] = 200
    pair[44:47] = 40
    pair_result = _run(pair)
    assert len(pair_result.hypotheses) >= 2
    assert any(item.narrow.paired_edge_separation_px > 0.0 for item in pair_result.hypotheses)
    assert all(0.0 <= item.artifact_likelihood <= 1.0 for item in pair_result.hypotheses)


def test_plateau_artifact_separates_glare_from_legitimate_phase_texture():
    mask = np.full((80, 100), 255, dtype=np.uint8)
    x = np.arange(100)
    uniform_bright_phase = np.full((80, 100), 70, dtype=np.uint8)
    uniform_bright_phase[:40] = 244
    local_line = np.full((80, 100), 90, dtype=np.uint8)
    local_line[39:42] = 244
    weak_stripes = np.full((80, 100), 70, dtype=np.uint8)
    weak_stripes[:40] = 180 + 12 * ((x // 12) % 2 * 2 - 1)
    smooth_gradient = np.full((80, 100), 70, dtype=np.uint8)
    smooth_gradient[:40] = np.clip(180 + 12 * (2 * x / 99 - 1), 0, 255)
    smooth_sinusoid = np.full((80, 100), 70, dtype=np.uint8)
    smooth_sinusoid[:40] = np.clip(
        180 + 12 * np.sin(2 * np.pi * x / 48),
        0,
        255,
    )
    localized_plateau = np.full((80, 100), 90, dtype=np.uint8)
    localized_plateau[42:, 25:75] = 244
    distributed_fine_glare = np.full((80, 100), 90, dtype=np.uint8)
    distributed_fine_glare[42:] = 244
    distributed_fine_glare[42:, ::2] = 240

    score = oil_shadow_observations._persistent_plateau_artifact
    assert score(uniform_bright_phase, mask, 40.0) == 0.0
    assert score(local_line, mask, 40.0) == 0.0
    assert score(weak_stripes, mask, 40.0) < 0.01
    assert score(smooth_gradient, mask, 40.0) < 0.01
    assert score(smooth_sinusoid, mask, 40.0) < 0.01
    assert score(localized_plateau, mask, 40.0) > 0.80
    assert score(distributed_fine_glare, mask, 40.0) > 0.40


@pytest.mark.parametrize("shape", ((40, 50), (80, 100), (160, 200)))
def test_plateau_artifact_scales_with_roi_and_rejects_fragmented_support(shape):
    height, width = shape
    center = height // 2
    plateau = np.full(shape, 90, dtype=np.uint8)
    plateau[center:, width // 4 : 3 * width // 4] = 244
    broad = np.full(shape, 255, dtype=np.uint8)
    sparse = np.zeros(shape, dtype=np.uint8)
    sparse[:, width // 2] = 255
    fragmented = np.zeros(shape, dtype=np.uint8)
    fragmented[:, ::8] = 255

    score = oil_shadow_observations._persistent_plateau_artifact
    assert score(plateau, broad, float(center)) > 0.80
    assert score(plateau, sparse, float(center)) == 0.0
    assert score(plateau, fragmented, float(center)) == 0.0


def test_real_boundary_adjacent_to_structure_keeps_multiple_explanations():
    image = _step(line=False)
    image[46:49] = 220
    result = _run(image)
    assert len(result.hypotheses) >= 2
    assert any(item.broad.strength > 0.15 for item in result.hypotheses)
    assert any(item.narrow.paired_edge_strength > 0.5 for item in result.hypotheses)
    assert all(item.observation_ids for item in result.hypotheses)


def test_glare_exclusion_and_unavailable_are_explicit_not_zero_negative_evidence():
    image = _step(line=False)
    image[34:47] = 255
    exclusion = np.zeros(image.shape, dtype=np.uint8)
    exclusion[36:44] = 255
    result = _run(image, exclusion=exclusion)
    assert result.hypotheses
    assert any(
        item.broad.glare_conflict > 0.0
        or item.broad.exclusion_conflict > 0.0
        or item.narrow.glare_overlap > 0.0
        or item.narrow.exclusion_overlap > 0.0
        for item in result.hypotheses
    )

    unavailable = BroadScaleEvidence(3, False, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0)
    available_zero = BroadScaleEvidence(3, True, 0.0, 0.0, 1.0, 0.0, 0.0, 10.0)
    assert unavailable != available_zero
    assert not unavailable.available and available_zero.available


def test_likelihoods_are_finite_normalized_and_ambiguity_is_first_class():
    line = np.full((80, 100), 100, dtype=np.uint8)
    line[39:42] = 200
    result = _run(line)
    assert isinstance(result, AmbiguousOutcome)
    for item in result.hypotheses:
        values = (
            item.boundary_likelihood,
            item.artifact_likelihood,
            item.ambiguity_likelihood,
            item.broad.strength,
            item.narrow.peak_strength,
            item.evidence_availability,
            item.visibility,
            item.polarity_confidence,
            item.static_prior.contribution,
        )
        assert all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values)
    _assert_deep_scalar_immutable(result)
    assert not hasattr(result.hypotheses[0], "selected")
    assert not hasattr(result.hypotheses[0], "rejected")


def test_static_prior_is_soft_bounded_neutral_when_absent_and_overcome_by_broad_step():
    image = _step(line=False)
    static = np.zeros(image.shape, dtype=np.uint8)
    static[37:44] = 255
    baseline = _run(image).hypotheses[0]
    prior = _run(image, static=static).hypotheses[0]
    assert baseline.observation_ids == prior.observation_ids
    assert baseline.proposal_ids == prior.proposal_ids
    assert not baseline.static_prior.available
    assert prior.static_prior.available
    assert 0.0 < prior.static_prior.contribution <= OilShadowBounds().maximum_static_prior
    assert prior.artifact_likelihood > baseline.artifact_likelihood

    strong = _run(_step(230, 20, line=False), static=static, glare_threshold=255).hypotheses[0]
    assert strong.broad.strength > 0.60
    assert strong.boundary_likelihood > strong.artifact_likelihood

    undercovered = np.zeros(image.shape, dtype=np.uint8)
    undercovered[40, 50] = 255
    neutral = _run(image, static=undercovered).hypotheses[0]
    assert not neutral.static_prior.available
    assert neutral.static_prior.contribution == 0.0


def test_semantic_dedup_is_deterministic_preserves_provenance_and_keeps_opposites():
    original = _run(_step()).hypotheses[0]
    proposal_id = stable_digest("duplicate-proposal", (("y", original.representative_local_y),))
    observation_id = stable_digest("duplicate-observation", (("y", original.representative_local_y),))
    duplicate = replace(
        original,
        identity=stable_digest("duplicate-hypothesis", (("y", original.representative_local_y + 0.5),)),
        proposal_ids=tuple(sorted(original.proposal_ids + (proposal_id,))),
        observation_ids=tuple(sorted(original.observation_ids + (observation_id,))),
        provenance=tuple(sorted(original.provenance + (proposal_id, observation_id))),
        representative_local_y=original.representative_local_y + 0.5,
        representative_source_y=original.representative_source_y + 0.5,
        maximum_local_y=original.maximum_local_y + 0.5,
    )
    forward = semantic_deduplicate((original, duplicate), OilShadowBounds())
    reverse = semantic_deduplicate((duplicate, original), OilShadowBounds())
    assert forward == reverse
    assert len(forward) == 1
    assert proposal_id in forward[0].proposal_ids
    assert observation_id in forward[0].observation_ids

    opposite = replace(
        duplicate,
        identity=stable_digest("opposite-hypothesis", (("y", duplicate.representative_local_y),)),
        polarity_available=True,
        polarity=-1.0 if original.polarity >= 0.0 else 1.0,
        label=ShadowHypothesisLabel.ARTIFACT_LIKE,
    )
    separated = semantic_deduplicate((original, opposite), OilShadowBounds())
    assert len(separated) == 2


def test_closed_no_interface_boundary_ambiguity_and_unavailable_outcomes():
    dark = _run(np.full((80, 100), 75, dtype=np.uint8))
    bright = _run(np.full((80, 100), 190, dtype=np.uint8))
    assert isinstance(dark, NoInterfaceOutcome)
    assert isinstance(bright, NoInterfaceOutcome)
    assert dark.evidence.full_likelihood > dark.evidence.empty_likelihood
    assert bright.evidence.empty_likelihood > bright.evidence.full_likelihood

    strong = _run(_step())
    assert isinstance(strong, (AcceptedBoundaryOutcome, AmbiguousOutcome))
    assert not isinstance(strong, NoInterfaceOutcome)

    glare = _run(np.full((80, 100), 255, dtype=np.uint8))
    assert isinstance(glare, EvidenceUnavailableOutcome)


def _typed_hypothesis(
    seed: str,
    *,
    y: float = 40.0,
    boundary: float = 0.445,
    artifact: float = 0.16,
    ambiguity: float = 0.52,
    broad_available_scale_count: int = 2,
    broad_strength: float = 0.47,
    broad_scale_consistency: float = 0.90,
    broad_polarity_consistency: float = 1.0,
    broad_glare: float = 0.0,
    broad_exclusion: float = 0.0,
    narrow_available: bool = True,
    narrow_peak_strength: float = 1.0,
    narrow_horizontal_coverage: float = 0.0,
    narrow_scale_persistence: float = 1.0,
    paired_edge_strength: float = 0.72,
    pulse_symmetry: float = 0.50,
    narrow_glare: float = 0.0,
    narrow_exclusion: float = 0.0,
    narrow_border: float = 0.0,
    narrow_static: float = 0.0,
    static_contribution: float = 0.0,
    visibility: float = 1.0,
    evidence_availability: float = 1.0,
    proposal_count: int = 1,
    observation_count: int = 6,
):
    template = _run(_step(line=False)).hypotheses[0]
    proposal_ids = tuple(
        sorted(
            stable_digest(
                "typed-proposal",
                (("seed", seed), ("index", index)),
            )
            for index in range(proposal_count)
        )
    )
    observation_ids = tuple(
        sorted(
            stable_digest(
                "typed-observation",
                (("seed", seed), ("index", index)),
            )
            for index in range(observation_count)
        )
    )
    broad = replace(
        template.broad,
        available_scale_count=broad_available_scale_count,
        strength=broad_strength,
        scale_consistency=broad_scale_consistency,
        polarity_consistency=broad_polarity_consistency,
        transition_local_y=y,
        visibility=1.0,
        glare_conflict=broad_glare,
        exclusion_conflict=broad_exclusion,
    )
    narrow = replace(
        template.narrow,
        available=narrow_available,
        peak_strength=narrow_peak_strength,
        horizontal_coverage=narrow_horizontal_coverage,
        paired_edge_strength=paired_edge_strength,
        pulse_symmetry=pulse_symmetry,
        scale_persistence=narrow_scale_persistence,
        border_overlap=narrow_border,
        exclusion_overlap=narrow_exclusion,
        glare_overlap=narrow_glare,
        static_overlap=narrow_static,
    )
    static_prior = replace(
        template.static_prior,
        available=static_contribution > 0.0,
        coverage=narrow_static if static_contribution > 0.0 else 0.0,
        overlap=narrow_static if static_contribution > 0.0 else 0.0,
        contribution=static_contribution,
    )
    identity = stable_digest("typed-hypothesis", (("seed", seed),))
    return replace(
        template,
        identity=identity,
        proposal_ids=proposal_ids,
        observation_ids=observation_ids,
        representative_local_y=y,
        representative_source_y=y + 10.0,
        minimum_local_y=y - 1.0,
        maximum_local_y=y + 1.0,
        broad=broad,
        narrow=narrow,
        static_prior=static_prior,
        boundary_likelihood=boundary,
        artifact_likelihood=artifact,
        ambiguity_likelihood=ambiguity,
        evidence_availability=evidence_availability,
        visibility=visibility,
        polarity_available=True,
        polarity=0.01,
        polarity_confidence=0.01,
        label=ShadowHypothesisLabel.BOUNDARY_LIKE,
        provenance=tuple(sorted(proposal_ids + observation_ids)),
    )


def _no_interface(
    likelihood: float,
    *,
    visibility: float = 1.0,
    glare_conflict: float = 0.0,
) -> ShadowNoInterfaceEvidence:
    return ShadowNoInterfaceEvidence(
        available=True,
        likelihood=likelihood,
        full_likelihood=likelihood,
        empty_likelihood=0.0,
        region_uniformity=0.5,
        weak_boundary_evidence=0.2,
        competing_boundary_likelihood=0.0,
        visibility=visibility,
        glare_conflict=glare_conflict,
        mean_intensity=100.0,
        texture=1.0,
        reason="test_no_interface_evidence",
    )


def _typed_observation(
    monkeypatch,
    hypotheses,
    *,
    no_interface=0.15,
    visibility=1.0,
    glare_conflict=0.0,
    accepted_foam_front_local_y=None,
    accepted_foam_component_mask=None,
):
    image = np.full((20, 20), 100, dtype=np.uint8)
    mask = np.full_like(image, 255)
    pre = preprocess(image, mask, DetectorSettings())
    evidence = _no_interface(
        no_interface,
        visibility=visibility,
        glare_conflict=glare_conflict,
    )
    monkeypatch.setattr(
        oil_shadow_observations,
        "_no_interface_evidence",
        lambda *_args: evidence,
    )
    return evaluate_typed_current_observation(
        pre,
        mask,
        tuple(hypotheses),
        accepted_foam_front_local_y=accepted_foam_front_local_y,
        accepted_foam_component_mask=accepted_foam_component_mask,
    )


def test_contextual_ambiguity_does_not_claim_one_hypothesis_projection(monkeypatch):
    target = _typed_hypothesis(
        "contextual-glare",
        boundary=0.31,
        artifact=0.22,
        ambiguity=0.66,
    )
    contextual = _typed_observation(
        monkeypatch,
        (target,),
        no_interface=0.22,
        visibility=0.11,
        glare_conflict=0.89,
    )
    assert isinstance(contextual, ShadowAmbiguousObservation)
    assert contextual.hypothesis_ids == (target.identity,)
    assert contextual.boundary_likelihood == target.boundary_likelihood
    assert contextual.artifact_likelihood == target.artifact_likelihood
    assert contextual.ambiguity_likelihood == 0.89
    assert contextual.projected_source_y is None
    assert contextual.reason == "glare_visibility_conflict"

    canonical = _typed_observation(
        monkeypatch,
        (target,),
        no_interface=0.22,
        visibility=0.40,
        glare_conflict=0.55,
    )
    assert isinstance(canonical, ShadowAmbiguousObservation)
    assert canonical.ambiguity_likelihood == target.ambiguity_likelihood
    assert canonical.projected_source_y == target.representative_source_y


def test_corroborated_single_boundary_requires_strict_no_interface_dominance(monkeypatch):
    boundary = 0.445
    target = _typed_hypothesis("dominance", boundary=boundary)

    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary - 1e-6),
        ShadowBoundaryObservation,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary),
        ShadowAmbiguousObservation,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary + 1e-6),
        ShadowAmbiguousObservation,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary - 1e-9),
        ShadowBoundaryObservation,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary - 1e-12),
        ShadowAmbiguousObservation,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=boundary - 5e-13),
        ShadowAmbiguousObservation,
    )

    alternative = _typed_hypothesis("dominance-alternative", y=55.0)
    assert isinstance(
        _typed_observation(
            monkeypatch,
            (target, alternative),
            no_interface=boundary - 1e-6,
        ),
        ShadowAmbiguousObservation,
    )
    assert isinstance(
        _typed_observation(
            monkeypatch,
            (_typed_hypothesis("below-narrow-floor", boundary=0.429999),),
            no_interface=0.20,
        ),
        ShadowAmbiguousObservation,
    )
    assert isinstance(
        _typed_observation(
            monkeypatch,
            (_typed_hypothesis("at-narrow-floor", boundary=0.43, artifact=0.16),),
            no_interface=0.20,
        ),
        ShadowBoundaryObservation,
    )


@pytest.mark.parametrize(
    ("guard", "changes"),
    (
        ("artifact-margin", {"artifact": 0.185001}),
        ("broad-scale-count", {"broad_available_scale_count": 1}),
        ("broad-strength", {"broad_strength": 0.399999}),
        ("broad-consistency", {"broad_scale_consistency": 0.849999}),
        ("ambiguity", {"ambiguity": 0.60}),
        ("narrow-availability", {"narrow_available": False}),
        ("narrow-peak", {"narrow_peak_strength": 0.899999}),
        ("narrow-persistence", {"narrow_scale_persistence": 0.899999}),
        (
            "pulse-artifact",
            {"paired_edge_strength": 0.96, "pulse_symmetry": 0.96},
        ),
        ("paired-edge", {"paired_edge_strength": 0.800001}),
        ("visibility", {"visibility": 0.849999}),
        ("evidence-availability", {"evidence_availability": 0.899999}),
        ("polarity-coherence", {"broad_polarity_consistency": 0.849999}),
        ("spatial-conflict", {"narrow_exclusion": 0.150001}),
        (
            "static-contribution",
            {"narrow_static": 0.10, "static_contribution": 0.080001},
        ),
        ("static-overlap", {"narrow_static": 0.200001}),
        ("observation-count", {"observation_count": 5}),
        ("proposal-count", {"proposal_count": 2}),
    ),
)
def test_single_dominant_boundary_closes_when_any_guard_fails(
    monkeypatch,
    guard,
    changes,
):
    target = _typed_hypothesis(f"guard-{guard}", **changes)
    assert isinstance(
        _typed_observation(monkeypatch, (target,), no_interface=0.15),
        ShadowAmbiguousObservation,
    )


def test_single_dominant_boundary_requires_independent_corroboration(monkeypatch):
    target = _typed_hypothesis("target")
    accepted = _typed_observation(monkeypatch, (target,))
    assert isinstance(accepted, ShadowBoundaryObservation)

    structural_pulse = _typed_hypothesis(
        "structural-pulse",
        paired_edge_strength=0.96,
        pulse_symmetry=0.96,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (structural_pulse,)),
        ShadowAmbiguousObservation,
    )

    glare_conflict = _typed_hypothesis(
        "glare-conflict",
        broad_glare=0.40,
        narrow_glare=0.40,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (glare_conflict,)),
        ShadowAmbiguousObservation,
    )

    polarity_conflict = _typed_hypothesis(
        "polarity-conflict",
        broad_polarity_consistency=0.40,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (polarity_conflict,)),
        ShadowAmbiguousObservation,
    )

    static_conflict = _typed_hypothesis(
        "static-conflict",
        narrow_static=0.60,
        static_contribution=0.12,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (static_conflict,)),
        ShadowAmbiguousObservation,
    )


def test_single_dominant_path_preserves_no_interface_and_real_alternatives(monkeypatch):
    first = _typed_hypothesis("alternative-a", y=35.0)
    second = _typed_hypothesis("alternative-b", y=55.0)
    no_interface = _typed_observation(monkeypatch, (), no_interface=0.80)
    assert isinstance(no_interface, ShadowNoInterfaceObservation)

    forward = _typed_observation(monkeypatch, (first, second))
    reverse = _typed_observation(monkeypatch, (second, first))
    assert isinstance(forward, ShadowAmbiguousObservation)
    assert forward == reverse


def test_general_boundary_floor_remains_unchanged(monkeypatch):
    uncorroborated = _typed_hypothesis(
        "below-floor",
        boundary=0.479,
        broad_strength=0.35,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (uncorroborated,)),
        ShadowAmbiguousObservation,
    )

    at_general_floor = _typed_hypothesis(
        "at-floor",
        boundary=0.48,
        broad_strength=0.35,
    )
    assert isinstance(
        _typed_observation(monkeypatch, (at_general_floor,)),
        ShadowBoundaryObservation,
    )


def test_textured_low_contrast_recovery_requires_identifiable_phase_evidence(monkeypatch):
    target = _typed_hypothesis(
        "textured-low-contrast",
        y=12.0,
        boundary=0.26,
        artifact=0.20,
        ambiguity=0.61,
        broad_strength=0.17,
        broad_scale_consistency=0.90,
        narrow_peak_strength=0.40,
        narrow_horizontal_coverage=0.60,
        paired_edge_strength=0.30,
    )

    def evidence(texture_relief: float):
        return oil_shadow_observations._SingleFrameIdentifiabilityEvidence(
            phase_ceiling_pressure=0.0,
            texture_relief=texture_relief,
            broad_corroboration_deficit=1.0,
            evidence_reliability=0.90,
            collision_pressure=0.0,
            semantic_support=0.10,
            acceptance_margin=-0.30,
        )

    monkeypatch.setattr(
        oil_shadow_observations,
        "_single_frame_identifiability_evidence",
        lambda *_args: evidence(0.70),
    )
    recovered = _typed_observation(monkeypatch, (target,), no_interface=0.50)
    assert isinstance(recovered, ShadowBoundaryObservation)
    assert recovered.hypothesis.identity == target.identity

    monkeypatch.setattr(
        oil_shadow_observations,
        "_single_frame_identifiability_evidence",
        lambda *_args: evidence(0.20),
    )
    unresolved = _typed_observation(monkeypatch, (target,), no_interface=0.50)
    assert isinstance(unresolved, ShadowAmbiguousObservation)


def test_accepted_foam_context_recovers_only_a_distinct_broad_phase_below_front(monkeypatch):
    target = _typed_hypothesis(
        "foam-separated-oil",
        y=12.0,
        boundary=0.30,
        artifact=0.95,
        ambiguity=0.35,
        broad_strength=0.18,
        broad_scale_consistency=0.90,
        narrow_peak_strength=0.50,
        narrow_horizontal_coverage=0.60,
        paired_edge_strength=0.60,
    )
    foam_component = np.zeros((20, 20), dtype=np.uint8)
    monkeypatch.setattr(
        oil_shadow_observations,
        "_has_foam_separated_phase_support",
        lambda *_args: True,
    )
    below_foam = _typed_observation(
        monkeypatch,
        (target,),
        no_interface=0.35,
        accepted_foam_front_local_y=6.0,
        accepted_foam_component_mask=foam_component,
    )
    assert isinstance(below_foam, ShadowBoundaryObservation)
    assert below_foam.hypothesis.identity == target.identity

    front_only = _typed_observation(
        monkeypatch,
        (target,),
        no_interface=0.35,
        accepted_foam_front_local_y=6.0,
    )
    assert isinstance(front_only, ShadowAmbiguousObservation)

    above_foam = _typed_observation(
        monkeypatch,
        (target,),
        no_interface=0.35,
        accepted_foam_front_local_y=14.0,
        accepted_foam_component_mask=foam_component,
    )
    assert isinstance(above_foam, ShadowAmbiguousObservation)

    weak_broad = _typed_hypothesis(
        "foam-texture-without-phase",
        y=12.0,
        boundary=0.30,
        artifact=0.95,
        ambiguity=0.35,
        broad_strength=0.05,
        broad_scale_consistency=0.90,
        narrow_peak_strength=0.50,
        narrow_horizontal_coverage=0.80,
        paired_edge_strength=0.40,
    )
    no_phase = _typed_observation(
        monkeypatch,
        (weak_broad,),
        no_interface=0.35,
        accepted_foam_front_local_y=6.0,
        accepted_foam_component_mask=foam_component,
    )
    assert isinstance(no_phase, ShadowAmbiguousObservation)


def test_accepted_foam_context_requires_persistent_phase_not_structural_context(monkeypatch):
    structural = _typed_hypothesis(
        "foam-context-structural-artifact",
        y=12.0,
        boundary=0.30,
        artifact=0.70,
        ambiguity=0.35,
        broad_strength=0.18,
        broad_scale_consistency=0.90,
        narrow_peak_strength=0.55,
        narrow_horizontal_coverage=0.65,
        paired_edge_strength=0.96,
        pulse_symmetry=0.96,
    )
    without_foam = _typed_observation(
        monkeypatch,
        (structural,),
        no_interface=0.35,
    )
    assert isinstance(without_foam, ShadowAmbiguousObservation)

    monkeypatch.setattr(
        oil_shadow_observations,
        "_has_foam_separated_phase_support",
        lambda *_args: False,
    )
    with_foam = _typed_observation(
        monkeypatch,
        (structural,),
        no_interface=0.35,
        accepted_foam_front_local_y=6.0,
        accepted_foam_component_mask=np.zeros((20, 20), dtype=np.uint8),
    )
    assert isinstance(with_foam, ShadowAmbiguousObservation)
