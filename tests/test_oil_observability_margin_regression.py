from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import numpy as np

from oil_observability_fixtures import single_frame_observability_collisions
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
import oil_tracker.adapters.vision.oil_shadow_observations as observations
from oil_tracker.adapters.vision.oil_shadow_pipeline import OilHypothesisPipeline
from oil_tracker.adapters.vision.oil_shadow_types import (
    ShadowAmbiguousObservation,
    ShadowBoundaryObservation,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.geometry import EllipseGeometry
from oil_tracker.domain.recipe import InspectionRecipe


_CANONICAL_ELLIPSE = EllipseGeometry(160.0, 120.0, 36.0, 64.8)


@dataclass(frozen=True)
class _Analysis:
    observation: object
    evidence: object
    hypothesis: object


def _analyze(
    frame: np.ndarray,
    ellipse: EllipseGeometry = _CANONICAL_ELLIPSE,
) -> _Analysis:
    glass = InspectionRecipe.default_glass(320, 240)
    glass.id = "observability-margin-regression"
    glass.geometry.ellipse = ellipse
    bundle = build_mask_bundle(frame, glass)
    prepared = preprocess(
        bundle.crop,
        bundle.effective_mask,
        glass.detector_settings,
    )
    bounds = OilHypothesisPipeline().bounds
    raw = observations.extract_raw_observations(
        prepared,
        bundle.effective_mask,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )
    proposals = observations.build_bounded_proposals(raw, bounds)
    hypotheses = observations.evaluate_semantic_hypotheses(
        proposals,
        raw,
        prepared,
        bundle.effective_mask,
        bundle.ellipse_mask,
        bundle.exclusion_mask,
        None,
        crop_origin_y=float(bundle.crop_origin[1]),
        bounds=bounds,
    )
    ordered = sorted(hypotheses, key=observations._hypothesis_order)
    assert ordered
    best = ordered[0]
    second_boundary = (
        ordered[1].boundary_likelihood if len(ordered) > 1 else 0.0
    )
    no_interface = observations._no_interface_evidence(
        prepared,
        bundle.effective_mask,
        hypotheses,
    )
    boundary_margin = max(
        0.0,
        best.boundary_likelihood
        - max(
            best.artifact_likelihood,
            no_interface.likelihood,
            second_boundary,
        ),
    )
    standard_boundary = (
        best.boundary_likelihood >= 0.48
        and boundary_margin >= 0.08
        and best.ambiguity_likelihood < 0.72
        and best.visibility >= 0.30
    )
    corroborated_boundary = (
        observations._accepts_corroborated_single_dominant_boundary(
            best,
            ordered,
            no_interface,
        )
    )
    evidence = observations._single_frame_identifiability_evidence(
        prepared,
        bundle.effective_mask,
        best,
        no_interface,
        second_boundary,
        standard_boundary=standard_boundary,
        corroborated_single_boundary=corroborated_boundary,
    )
    current = observations.evaluate_typed_current_observation(
        prepared,
        bundle.effective_mask,
        hypotheses,
    )
    return _Analysis(current, evidence, best)


def _uniform_phase(high: int, *, low: int = 90) -> np.ndarray:
    frame = np.full((240, 320, 3), low, dtype=np.uint8)
    frame[80:] = high
    return frame


def _sparse_texture(
    kind: str,
    low: int,
    *,
    bright_side: str,
) -> np.ndarray:
    x = np.arange(320)
    values = np.full(320, 244.0)
    if kind == "alternating":
        values[x % 10 == 0] = low
    elif kind == "block":
        values[(x % 40) < 4] = low
    elif kind == "sinusoidal":
        phase = x % 40
        active = phase < 4
        values[active] = 244.0 - (244.0 - low) * np.sin(
            np.pi * (phase[active] + 1.0) / 5.0
        )
    else:
        raise ValueError(kind)
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    values = np.clip(values, 0, 255).astype(np.uint8)
    if bright_side == "below":
        frame[80:] = values[None, :, None]
    elif bright_side == "above":
        frame[:80] = values[None, :, None]
    else:
        raise ValueError(bright_side)
    return frame


def _near_ceiling_support_frame(center_x: int, count: int) -> np.ndarray:
    values = np.full(320, 244, dtype=np.uint8)
    start = center_x - count // 2
    values[start : start + count] = 239
    frame = np.full((240, 320, 3), 90, dtype=np.uint8)
    frame[80:] = values[None, :, None]
    return frame


def _accepted(row: _Analysis) -> bool:
    return isinstance(row.observation, ShadowBoundaryObservation)


def _assert_no_isolated_outcome(rows: list[_Analysis]) -> None:
    accepted = [_accepted(row) for row in rows]
    for left, current, right in zip(
        accepted,
        accepted[1:],
        accepted[2:],
        strict=False,
    ):
        assert not (left == right and current != left), accepted


def _assert_adjacent_margin_change(
    rows: list[_Analysis],
    maximum: float,
) -> None:
    margins = [row.evidence.acceptance_margin for row in rows]
    assert all(
        abs(right - left) <= maximum
        for left, right in zip(margins, margins[1:])
    ), margins


def test_discrete_observability_conflict_gate_is_retired() -> None:
    assert not hasattr(
        observations,
        "_has_single_frame_observability_conflict",
    )


def test_intensity_sweep_uses_one_continuous_margin() -> None:
    levels = list(range(235, 246))
    rows = [_analyze(_uniform_phase(level)) for level in levels]
    indexed = dict(zip(levels, rows, strict=True))

    assert not _accepted(indexed[239])
    assert not _accepted(indexed[240])
    assert [_accepted(row) for row in rows[:10]] == sorted(
        [_accepted(row) for row in rows[:10]],
        reverse=True,
    )
    margins = [row.evidence.acceptance_margin for row in rows[:10]]
    assert all(
        left > right
        for left, right in zip(margins, margins[1:])
    ), margins
    _assert_adjacent_margin_change(rows[:10], 0.05)
    assert isinstance(rows[-1].observation, ShadowAmbiguousObservation)
    assert (
        rows[-2].evidence.semantic_support
        - rows[-1].evidence.semantic_support
        > 0.60
    )
    _assert_no_isolated_outcome(rows)


def test_broad_evidence_neighborhood_has_no_independent_point_four_switch() -> None:
    lows = list(range(82, 90))
    rows = [
        _analyze(_uniform_phase(244, low=low))
        for low in lows
    ]
    indexed = dict(zip(lows, rows, strict=True))

    assert indexed[84].hypothesis.broad.strength > 0.40
    assert indexed[85].hypothesis.broad.strength < 0.40
    assert not _accepted(indexed[85])
    assert not _accepted(indexed[86])
    assert [_accepted(row) for row in rows] == sorted(
        [_accepted(row) for row in rows],
        reverse=True,
    )
    margins = [row.evidence.acceptance_margin for row in rows]
    assert all(
        left > right
        for left, right in zip(margins, margins[1:])
    ), margins
    _assert_adjacent_margin_change(rows, 0.06)
    assert (
        indexed[85].evidence.broad_corroboration_deficit
        < indexed[86].evidence.broad_corroboration_deficit
    )
    _assert_no_isolated_outcome(rows)


def test_sparse_texture_statistics_preserve_legitimate_boundary_recall() -> None:
    for kind in ("alternating", "block", "sinusoidal"):
        for bright_side in ("below", "above"):
            rows = [
                _analyze(
                    _sparse_texture(
                        kind,
                        low,
                        bright_side=bright_side,
                    )
                )
                for low in range(228, 235)
            ]
            assert all(_accepted(row) for row in rows), (
                kind,
                bright_side,
                [row.evidence.acceptance_margin for row in rows],
            )
            assert all(row.evidence.texture_relief > 0.40 for row in rows)
            _assert_adjacent_margin_change(rows, 0.06)
            _assert_no_isolated_outcome(rows)


def test_unresolved_texture_collisions_remain_ambiguous() -> None:
    grouped: dict[str, list[object]] = defaultdict(list)
    for scene in single_frame_observability_collisions():
        grouped[scene.collision_id].append(scene)

    for collision_id, scenes in grouped.items():
        left, right = [_analyze(scene.frame, scene.ellipse) for scene in scenes]
        assert isinstance(left.observation, ShadowAmbiguousObservation), collision_id
        assert isinstance(right.observation, ShadowAmbiguousObservation), collision_id
        assert left.evidence == right.evidence, collision_id
        assert left.evidence.acceptance_margin < 0.0, collision_id


def test_near_ceiling_support_sweep_is_monotonic_across_roi_geometry() -> None:
    geometries = (
        EllipseGeometry(160.0, 120.0, 36.0, 64.8),
        EllipseGeometry(152.0, 120.0, 34.0, 64.8),
        EllipseGeometry(168.0, 120.0, 40.0, 64.8),
    )
    for ellipse in geometries:
        center_x = int(round(ellipse.center_x))
        counts = list(range(4, 15))
        rows = [
            _analyze(
                _near_ceiling_support_frame(center_x, count),
                ellipse,
            )
            for count in counts
        ]
        indexed = dict(zip(counts, rows, strict=True))
        assert _accepted(indexed[8]) == _accepted(indexed[9])
        collision = [row.evidence.collision_pressure for row in rows]
        assert all(
            left >= right
            for left, right in zip(collision, collision[1:])
        ), (ellipse, collision)
        margins = [row.evidence.acceptance_margin for row in rows]
        assert all(
            left <= right
            for left, right in zip(margins, margins[1:])
        ), (ellipse, margins)
        _assert_adjacent_margin_change(rows, 0.04)
        _assert_no_isolated_outcome(rows)
