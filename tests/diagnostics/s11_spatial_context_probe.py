"""Offline measurement prototype: ordered full-height strip context, no identity rule.

This consumes explicitly supplied raw-gray rasters and exact source geometry.
It does not decode private video, infer masks, select candidates or issue predictions.
"""
from __future__ import annotations

import copy
import math

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

LATERAL_SPEC = {
    'id': 'ordered-column-side-context-v1',
    'gray_units': 'uint8 raw grayscale, 0..255',
    'extent': 'O1 near_above/near_below windows at each supplied sampling center',
    'purpose': 'retain horizontal side appearance, not segmentation or physical identity',
    'decision': 'NOT_EVALUATED', 'threshold': None,
    'max_band_width': 128, 'max_point_columns': 65536,
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


def measure_lateral_context(gray, effective_mask, glare_mask, points, *, band_width, origin=(0, 0)):
    """Keep X order of side means without selecting a path or inferring regions.

    Reuse the existing raster/geometry contract and include its row observation
    for direct comparison. Clipped windows retain partial measurements and counts;
    they do not acquire O1 band availability or classifier sufficiency.
    """
    width = o2.integer(band_width, 'band width')
    o2.require(0 < width <= LATERAL_SPEC['max_band_width'], 'band width exceeds lateral bounds')
    row_context = measure_context(gray, effective_mask, glare_mask, points, origin=origin)
    o2.require(sum(p['source_x_range'][1]-p['source_x_range'][0] for p in points)
               <= LATERAL_SPEC['max_point_columns'], 'lateral point columns exceed bound')
    ox, oy = row_context['origin']
    height = gray.shape[0]
    effective = effective_mask > 0
    visible = effective & ~(glare_mask > 0)
    result = []
    for point in row_context['points']:
        x0, x1 = point['source_x_range']
        center = math.floor(point['source_y']-oy+0.5)  # same sampling convention as O1
        bands = {}
        for name, start, stop in [('near_above', center-width-1, center-1),
                                  ('near_below', center+2, center+width+2)]:
            lo, hi = max(0, min(height, start)), max(0, min(height, stop))
            patch = gray[lo:hi, x0-ox:x1-ox]
            mask = visible[lo:hi, x0-ox:x1-ox]
            counts = mask.sum(axis=0)
            effective_counts = effective[lo:hi, x0-ox:x1-ox].sum(axis=0)
            means = masked_row_mean(patch.T, mask.T)
            bands[name] = {
                'local_y_range': [start, stop], 'source_y_range': [start+oy, stop+oy],
                'clipped_local_y_range': [lo, hi], 'clipped_source_y_range': [lo+oy, hi+oy],
                'crop_complete': lo == start and hi == stop,
                'requested_pixels_per_column': width, 'in_crop_pixels_per_column': hi-lo,
                'effective_count': effective_counts.astype(int).tolist(),
                'visible_count': counts.astype(int).tolist(),
                'glare_excluded_count': (effective_counts-counts).astype(int).tolist(),
                'gray_mean': [float(v) if n else None for v, n in zip(means, counts, strict=True)],
                'column_state': ['outside_crop' if hi == lo else 'observed' if n
                                 else 'glare_excluded' if e else 'outside_effective_mask'
                                 for n, e in zip(counts, effective_counts, strict=True)],
            }
        above, below = bands['near_above'], bands['near_below']
        result.append(copy.deepcopy(point) | {
            'sampling_center_local_y': center,
            'source_x_columns': list(range(x0, x1)), 'bands': bands,
            'signed_delta': [b-a if a is not None and b is not None else None
                             for a, b in zip(above['gray_mean'], below['gray_mean'], strict=True)],
        })
    return {'spec': copy.deepcopy(LATERAL_SPEC), 'band_width_px': width,
            'decision': 'NOT_EVALUATED', 'row_context': row_context, 'points': result,
            'limitation': 'Column side averages retain X order but lose vertical order within each band. '
                          'No connectivity, contour, physical identity or sufficient support is inferred.'}
