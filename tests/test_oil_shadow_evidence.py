from __future__ import annotations

from dataclasses import fields, is_dataclass, replace
from enum import Enum
import math

import numpy as np

from oil_tracker.adapters.vision.oil_shadow_observations import semantic_deduplicate
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilShadowPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    BroadScaleEvidence,
    OilShadowBounds,
    ShadowHypothesisLabel,
    ShadowObservationKind,
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
    assert result.current_observation.kind is ShadowObservationKind.AMBIGUOUS
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


def test_typed_no_interface_boundary_ambiguity_and_unavailable_outputs():
    dark = _run(np.full((80, 100), 75, dtype=np.uint8))
    bright = _run(np.full((80, 100), 190, dtype=np.uint8))
    assert dark.current_observation.kind is ShadowObservationKind.NO_INTERFACE
    assert bright.current_observation.kind is ShadowObservationKind.NO_INTERFACE
    assert dark.current_observation.evidence.full_likelihood > dark.current_observation.evidence.empty_likelihood
    assert bright.current_observation.evidence.empty_likelihood > bright.current_observation.evidence.full_likelihood

    strong = _run(_step())
    assert strong.current_observation.kind in {
        ShadowObservationKind.BOUNDARY,
        ShadowObservationKind.AMBIGUOUS,
    }
    assert strong.current_observation.kind is not ShadowObservationKind.NO_INTERFACE

    glare = _run(np.full((80, 100), 255, dtype=np.uint8))
    assert glare.current_observation.kind is ShadowObservationKind.UNAVAILABLE
