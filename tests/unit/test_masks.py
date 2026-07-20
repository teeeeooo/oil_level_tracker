from dataclasses import replace

import numpy as np

from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle, effective_area_ratio
from oil_tracker.domain.geometry import ExclusionZone, Rect
from tests.fixtures.synthetic import glass_config, partial_frame


def test_ellipse_mask_and_margin_reduce_area():
    glass = glass_config(); frame = partial_frame()
    no_margin = replace(glass.geometry, margin_ratio=0.0)
    glass.geometry = no_margin
    base = build_mask_bundle(frame, glass)
    glass.geometry.margin_ratio = 0.2
    margin = build_mask_bundle(frame, glass)
    assert np.count_nonzero(base.ellipse_mask) > 0
    assert np.count_nonzero(margin.effective_mask) < np.count_nonzero(base.effective_mask)


def test_exclusion_zone_removed_from_effective_mask():
    glass = glass_config(); frame = partial_frame()
    zone = ExclusionZone("z", Rect(140, 100, 40, 40))
    glass.geometry.exclusions.append(zone)
    bundle = build_mask_bundle(frame, glass)
    x0, y0 = bundle.crop_origin
    assert bundle.exclusion_mask[110-y0, 150-x0] == 255
    assert bundle.effective_mask[110-y0, 150-x0] == 0
    assert 0 < effective_area_ratio(bundle) < 1
