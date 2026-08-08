from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass
from enum import Enum
from itertools import permutations
import math

import numpy as np
import pytest

from oil_tracker.adapters.vision.oil_shadow_observations import (
    build_bounded_proposals,
    extract_raw_observations,
)
from oil_tracker.adapters.vision.oil_shadow_types import (
    OilShadowBounds,
    RawEdgeObservation,
    ShadowSourceFamily,
    stable_digest,
)
from oil_tracker.adapters.vision.preprocessing import preprocess
from oil_tracker.domain.recipe import DetectorSettings


def _raw(y: float, *, family=ShadowSourceFamily.SOBEL, index=0, scale=1):
    identity = stable_digest(
        "test-observation",
        (
            ("family", family.value),
            ("y", y),
            ("index", index),
            ("scale", scale),
        ),
    )
    return RawEdgeObservation(
        identity=identity,
        source_family=family,
        measurement_scale=scale,
        local_y=y,
        source_y=y + 20.0,
        polarity_available=True,
        polarity=1.0,
        response_strength=0.8,
        horizontal_support=0.7,
        valid_mask_support=0.9,
        glare_visible_support=1.0,
        measurement_width_px=100.0,
        band_height_px=float(scale),
        source_local_index=index,
    )


def _step_inputs(y=40, above=170, below=80):
    image = np.full((80, 100), above, dtype=np.uint8)
    image[y:] = below
    mask = np.full_like(image, 255)
    pre = preprocess(image, mask, DetectorSettings())
    return image, mask, pre


def _assert_deep_scalar_immutable(value):
    if isinstance(value, np.ndarray):
        raise AssertionError("immutable shadow record retained an ndarray")
    if isinstance(value, (list, dict, set)):
        raise AssertionError("immutable shadow record retained a mutable container")
    if isinstance(value, tuple):
        for item in value:
            _assert_deep_scalar_immutable(item)
        return
    if isinstance(value, Enum) or value is None or isinstance(value, (str, int, float, bool)):
        return
    if is_dataclass(value):
        for item in fields(value):
            _assert_deep_scalar_immutable(getattr(value, item.name))
        return
    raise AssertionError(f"unexpected retained type: {type(value)!r}")


def test_raw_observations_are_frozen_deep_scalar_and_finite():
    value = _raw(12.0)
    with pytest.raises(FrozenInstanceError):
        value.local_y = 14.0
    _assert_deep_scalar_immutable(value)
    assert all(
        math.isfinite(number)
        for number in (
            value.local_y,
            value.source_y,
            value.response_strength,
            value.horizontal_support,
            value.valid_mask_support,
            value.glare_visible_support,
        )
    )
    with pytest.raises(ValueError, match="finite"):
        RawEdgeObservation(
            identity=value.identity,
            source_family=value.source_family,
            measurement_scale=1,
            local_y=float("nan"),
            source_y=1.0,
            polarity_available=False,
            polarity=0.0,
            response_strength=0.0,
            horizontal_support=0.0,
            valid_mask_support=0.0,
            glare_visible_support=0.0,
            measurement_width_px=1.0,
            band_height_px=1.0,
            source_local_index=0,
        )


def test_stable_digest_and_extraction_are_order_independent_and_repeatable():
    forward_mapping = {"b": 2.0, "a": 1.0, "enabled": True}
    reverse_mapping = {"enabled": True, "a": 1.0, "b": 2.0}
    assert stable_digest(
        "identity", tuple(forward_mapping.items())
    ) == stable_digest("identity", tuple(reverse_mapping.items()))
    image, mask, pre = _step_inputs()
    before_image = image.copy()
    before_mask = mask.copy()
    first = extract_raw_observations(
        pre,
        mask,
        crop_origin_y=17.0,
        bounds=OilShadowBounds(),
    )
    second = extract_raw_observations(
        pre,
        mask,
        crop_origin_y=17.0,
        bounds=OilShadowBounds(),
    )
    assert first == second
    assert tuple(item.identity for item in first) == tuple(
        item.identity for item in second
    )
    assert np.array_equal(image, before_image)
    assert np.array_equal(mask, before_mask)
    assert all(item.source_y - item.local_y == 17.0 for item in first)
    groups = {}
    for item in first:
        groups.setdefault((item.source_family, item.measurement_scale), 0)
        groups[(item.source_family, item.measurement_scale)] += 1
    assert all(count <= OilShadowBounds().observations_per_source_scale for count in groups.values())
    assert ShadowSourceFamily.REGION_STEP in {item.source_family for item in first}
    assert not any(
        item.source_family is ShadowSourceFamily.SOBEL_DISTRIBUTED
        for item in first
    )
    assert {item.source_family for item in first} <= {
        ShadowSourceFamily.REGION_STEP,
        ShadowSourceFamily.SOBEL,
        ShadowSourceFamily.CANNY,
        ShadowSourceFamily.HOUGH,
    }
    assert len(first) <= OilShadowBounds().total_raw_observations


def test_bounded_diameter_rejects_transitive_bridge_and_accepts_exact_limit():
    bounds = OilShadowBounds(maximum_proposal_diameter_px=4.0)
    exact = build_bounded_proposals((_raw(10.0), _raw(14.0, index=1)), bounds)
    assert len(exact) == 1
    assert exact[0].diameter_px == 4.0

    bridge = build_bounded_proposals(
        (_raw(10.0), _raw(13.0, index=1), _raw(16.0, index=2)),
        bounds,
    )
    assert len(bridge) == 2
    assert tuple(item.member_count for item in bridge) == (2, 1)
    assert all(item.diameter_px <= 4.0 for item in bridge)


def test_proposals_are_permutation_independent_with_canonical_provenance():
    values = (
        _raw(10.0, index=0),
        _raw(12.0, family=ShadowSourceFamily.CANNY, index=0),
        _raw(20.0, family=ShadowSourceFamily.REGION_STEP, index=0, scale=3),
    )
    expected = None
    for order in permutations(values):
        result = build_bounded_proposals(order, OilShadowBounds())
        signature = tuple(
            (
                item.identity,
                item.member_ids,
                item.minimum_local_y,
                item.maximum_local_y,
                item.representative_local_y,
            )
            for item in result
        )
        expected = signature if expected is None else expected
        assert signature == expected
        for proposal in result:
            _assert_deep_scalar_immutable(proposal)


def test_proposal_member_total_and_count_overflow_are_deterministic():
    bounds = OilShadowBounds(
        total_raw_observations=5,
        total_retained_members=5,
        members_per_proposal=2,
        total_proposals=2,
        maximum_proposal_diameter_px=1.0,
    )
    values = tuple(_raw(float(index * 10), index=index) for index in range(10))
    forward = build_bounded_proposals(values, bounds)
    reverse = build_bounded_proposals(tuple(reversed(values)), bounds)
    assert forward == reverse
    assert len(forward) == 2
    assert sum(item.member_count for item in forward) <= bounds.total_retained_members
    assert max(item.member_count for item in forward) <= bounds.members_per_proposal
    assert tuple(item.representative_local_y for item in forward) == (0.0, 10.0)
