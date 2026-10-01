"""Offline measurement prototype: ordered full-height strip context, no identity rule.

This consumes explicitly supplied raw-gray rasters and exact source geometry.
It does not decode private video, infer masks, select candidates or issue predictions.
"""
from __future__ import annotations

import copy

import numpy as np

from oil_tracker.adapters.vision.row_features import masked_row_mean
from tests.diagnostics import s11_interface_shadow_evaluation as o2

SPEC = {
    'id': 'ordered-full-height-strip-context-v1',
    'gray_units': 'uint8 raw grayscale, 0..255; no equalization or fitted normalization',
    'extent': 'all crop rows inside exact source X interval; no mask-gap interpolation',
    'purpose': 'test information outside finite candidate bands, not physical identity',
    'decision': 'NOT_EVALUATED', 'fitted': False, 'threshold': None,
    'max_dimension': 4096, 'max_points': 512,
}


def measure_context(gray, effective_mask, glare_mask, points, *, origin=(0, 0)):
    """Preserve ordered row means/counts and point references, including censoring.

    A positive visible count means a numeric mean exists, not that its support is
    sufficient for a classifier. All measurements retain coverage. Horizontal
    averaging still loses texture/shape; no region adjacency is inferred.
    """
    o2.require(isinstance(gray, np.ndarray) and gray.ndim == 2 and gray.dtype == np.uint8,
               'raw gray must be a two-dimensional uint8 array')
    h, w = gray.shape
    o2.require(0 < h <= SPEC['max_dimension'] and 0 < w <= SPEC['max_dimension'], 'raster exceeds probe bounds')
    for mask in (effective_mask, glare_mask):
        o2.require(isinstance(mask, np.ndarray) and mask.shape == gray.shape
                   and mask.dtype in (np.dtype('uint8'), np.dtype('bool')), 'invalid mask shape/type')
    o2.require(len(origin) == 2, 'origin must be source X/Y')
    ox, oy = (o2.integer(v, 'origin') for v in origin)
    o2.require(isinstance(points, list) and len(points) <= SPEC['max_points'], 'point inventory exceeds probe bound')
    seen, profiles, projected = set(), {}, []
    visible = (effective_mask > 0) & ~(glare_mask > 0)
    for point in points:
        idx = o2.integer(point['candidate_input_index'], 'candidate index')
        o2.require(point['geometry_basis'] in ('native_path', 'candidate_center'), 'unsupported geometry basis')
        x0, x1 = o2.interval(point['source_x_range'], 'source X', strict=True)
        o2.require(type(x0) is int and type(x1) is int and ox <= x0 < x1 <= ox+w, 'source X outside raster or nonintegral')
        y = o2.number(point['source_y'], 'source Y')
        o2.require(oy <= y < oy+h, 'source Y outside raster')
        key = (idx, o2.geometry_key(point))
        o2.require(key not in seen, 'duplicate point geometry')
        seen.add(key)
        strip = (x0, x1)
        if strip not in profiles:
            start, stop = x0-ox, x1-ox
            mask = visible[:, start:stop]
            effective = (effective_mask[:, start:stop] > 0).sum(axis=1)
            counts = mask.sum(axis=1)
            means = masked_row_mean(gray[:, start:stop], mask)
            profiles[strip] = {
                'profile_id': len(profiles), 'source_x_range': [x0, x1],
                'source_y_start': oy, 'source_y_stop_exclusive': oy+h,
                'effective_count': effective.astype(int).tolist(),
                'visible_count': counts.astype(int).tolist(),
                'glare_excluded_count': (effective-counts).astype(int).tolist(),
                'row_state': ['observed' if n else 'glare_excluded' if e else 'outside_effective_mask'
                              for n, e in zip(counts, effective, strict=True)],
                'gray_mean': [float(v) if n else None for v, n in zip(means, counts, strict=True)],
                'extent_censored': True,
            }
        projected.append({k: copy.deepcopy(point[k]) for k in
                          ('candidate_input_index', 'geometry_basis', 'source_x_range', 'source_y')}
                         | {'profile_id': profiles[strip]['profile_id']})
    return {'spec': copy.deepcopy(SPEC), 'decision': 'NOT_EVALUATED',
            'origin': [ox, oy], 'shape': [h, w], 'point_count': len(points),
            'points': projected, 'profiles': list(profiles.values()),
            'limitation': 'A return or sustained transition is appearance, not Oil/structure identity. '
                          'No observed return does not establish absence beyond crop/mask support.'}
