"""Offline measurement prototype: ordered full-height strip context, no identity rule.

This consumes explicitly supplied raw-gray rasters and exact source geometry.
It does not decode private video, infer masks, select candidates or issue predictions.
"""
from __future__ import annotations

import copy
import math

import numpy as np

from oil_tracker.adapters.vision.row_features import masked_row_mean
from oil_tracker.adapters.vision import oil_interface_witness
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

JOINT_SPEC = {
    'id': 'unpooled-o1-gradient-context-v1',
    'operator': 'existing O1 raw-gray central differences, center plus four visible neighbours',
    'extent': 'whole crop, retaining joint source X/Y; no candidate selection',
    'purpose': 'inspect lateral arrangement lost by marginal pooling, not physical identity',
    'decision': 'NOT_EVALUATED', 'threshold': None,
    'invalid_encoding': 'zero storage plus explicit gradient_valid mask; never observed zero',
}


def measure_joint_context(gray, effective_mask, glare_mask, points, *, origin=(0, 0)):
    """Expose the existing O1 spatial stencil before pooling, with validity.

    This is not a new independent signal: both channels are deterministic functions
    of the saved pixels. No edge threshold, connected component or path is selected.
    Magnitudes intentionally lose polarity; even identical complete pixels can
    describe different physical causes. Return JSON metadata and numeric arrays.
    """
    rows = measure_context(gray, effective_mask, glare_mask, points, origin=origin)
    effective = effective_mask > 0
    visible = effective & ~(glare_mask > 0)
    channels = oil_interface_witness._extra_channels(gray, visible, effective, np.zeros_like(gray))
    arrays = {'gradient_valid': channels['gradient_count'].astype(np.uint8),
              'gradient_magnitude': channels['gradient'],
              'vertical_magnitude': channels['normal']}
    ox, _ = rows['origin']
    strips = []
    for profile in rows['profiles']:
        a, b = profile['source_x_range']
        strips.append({'profile_id': profile['profile_id'], 'source_x_range': [a, b],
                       'pixel_count': gray.shape[0]*(b-a),
                       'visible_pixel_count': int(visible[:, a-ox:b-ox].sum()),
                       'gradient_valid_count': int(arrays['gradient_valid'][:, a-ox:b-ox].sum())})
    return {'spec': copy.deepcopy(JOINT_SPEC), 'decision': 'NOT_EVALUATED',
            'origin': rows['origin'], 'shape': rows['shape'], 'points': rows['points'], 'strips': strips,
            'limitation': 'Spatial gradients retain local arrangement, not region ownership or physical '
                          'connectivity. Mask gaps cannot support continuity. Same pixels remain ambiguous.'}, arrays


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


COLOR_SIDE_SPEC = {
    'id': 'recorded-band-color-side-v1',
    'channels': ['B', 'G', 'R', 'gray'],
    'units': 'uint8 code values 0..255, float64 means; not calibrated radiometry',
    'support': 'effective and not glare; same pixels for all four channels',
    'pairing': 'below-minus-above per exact X column; equal-weight mean over paired columns',
    'eligibility': 'both recorded O1 bands available; a paired column needs visible pixels on both sides',
    'opponents': ['B-G', 'R-G'],
    'purpose': 'chromatic appearance retained beyond gray projection; not transparency or identity',
    'decision': 'NOT_EVALUATED', 'threshold': None,
    'max_band_columns': 1000000, 'max_sample_pixels': 100000000,
}


def measure_color_side(crop, gray, effective_mask, glare_mask, points, *, origin=(0, 0)):
    """Measure exact recorded bands without searching/recentering or filling gaps.

    Input points already carry the runner's exact witness-center binding. Column
    order is retained, but vertical order within each band is still averaged.
    Recorded unavailable bands retain diagnostic observations, not pair deltas.
    """
    import cv2

    o2.require(isinstance(crop, np.ndarray) and crop.dtype == np.uint8 and
               crop.ndim == 3 and crop.shape[2] == 3, 'uint8 BGR crop required')
    o2.require(isinstance(gray, np.ndarray) and gray.dtype == np.uint8 and
               gray.ndim == 2 and crop.shape[:2] == gray.shape, 'color/gray shape or type mismatch')
    h, w = gray.shape
    o2.require(0 < h <= SPEC['max_dimension'] and 0 < w <= SPEC['max_dimension'], 'color raster exceeds bounds')
    o2.require(np.array_equal(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), gray), 'BGR-to-gray mismatch')
    for mask in (effective_mask, glare_mask):
        o2.require(isinstance(mask, np.ndarray) and mask.shape == gray.shape and
                   mask.dtype in (np.dtype('uint8'), np.dtype('bool')), 'invalid color mask')
    o2.require(len(origin) == 2 and isinstance(points, list) and len(points) <= SPEC['max_points'],
               'invalid color origin or point count')
    ox, oy = (o2.integer(v, 'origin') for v in origin)
    visible = (effective_mask > 0) & (glare_mask == 0)
    result, seen, columns_used, pixels_used = [], set(), 0, 0
    names = ('near_above', 'near_below', 'far_above', 'far_below')
    for p in points:
        key = (p['candidate_input_index'], *o2.geometry_key(p))
        o2.require(key not in seen and p['geometry_basis'] in ('native_path', 'candidate_center'), 'duplicate/invalid color point')
        seen.add(key)
        x0, x1 = (o2.integer(v, 'source X') - ox for v in p['source_x_range'])
        o2.require(0 <= x0 < x1 <= w and oy <= p['source_y'] < oy+h, 'color point outside crop')
        point_result = {k: copy.deepcopy(p[k]) for k in
                        ('candidate_input_index', 'geometry_basis', 'source_x_range', 'source_y',
                         'band_binding', 'band_center_role')}
        point_result['scales'] = []
        widths = set()
        o2.require(1 <= len(p['scales']) <= 3, 'invalid color scale count')
        for scale in p['scales']:
            width = o2.integer(scale['band_width_px'], 'band width')
            o2.require(0 < width <= 128 and width not in widths, 'invalid/duplicate color width')
            widths.add(width)
            bands = {b['name']: b for b in scale['bands']}
            o2.require(len(scale['bands']) == 4 and set(bands) == set(names), 'four unique O1 bands required')
            measured, by_band = [], {}
            for name in names:
                band = bands[name]
                lo, hi = (o2.integer(v, 'band Y') for v in band['clipped_local_y_range'])
                start, stop = band['local_y_range']
                o2.require(type(start) is int and type(stop) is int and start < stop and (lo, hi) == (max(0, min(h, start)), max(0, min(h, stop)))
                           and type(band['available']) is bool, 'invalid color band range/state')
                columns_used += x1-x0
                pixels_used += (hi-lo)*(x1-x0)
                o2.require(columns_used <= COLOR_SIDE_SPEC['max_band_columns'] and
                           pixels_used <= COLOR_SIDE_SPEC['max_sample_pixels'], 'color sampling resource bound exceeded')
                valid = visible[lo:hi, x0:x1]
                counts = valid.sum(axis=0)
                # Identical spatial support; gray is the saved uint8 conversion,
                # not a conversion of already-averaged BGR values.
                values = np.concatenate((crop[lo:hi, x0:x1], gray[lo:hi, x0:x1, None]), axis=2)
                sums = np.where(valid[..., None], values, 0).sum(axis=0, dtype=np.float64)
                means = np.divide(sums, counts[:, None], out=np.zeros_like(sums), where=counts[:, None] > 0)
                count = int(counts.sum())
                o2.require(count == band['valid_pixel_count'], 'color support differs from recorded O1 band')
                by_band[name] = (counts, means)
                measured.append({
                    'name': name, 'local_y_range': band['local_y_range'],
                    'clipped_local_y_range': [lo, hi], 'clipped_source_y_range': [lo+oy, hi+oy],
                    'o1_available': band['available'], 'o1_reason': band['reason'],
                    'visible_pixel_count': count, 'column_visible_counts': counts.tolist(),
                    'observed_mean_bgr_gray': (sums.sum(axis=0)/count).tolist() if count else None,
                })
            pairs = {}
            for region in ('near', 'far'):
                above, below = region+'_above', region+'_below'
                ac, av = by_band[above]; bc, bv = by_band[below]
                joint = (ac > 0) & (bc > 0)
                available = bands[above]['available'] and bands[below]['available']
                status = ('o1_unavailable' if not available else
                          'no_paired_columns' if not joint.any() else 'observed')
                delta = bv-av
                mean = delta[joint].mean(axis=0) if status == 'observed' else None
                pairs[region] = {
                    'status': status, 'observed_paired_columns': int(joint.sum()),
                    'total_columns': x1-x0,
                    'mean_column_delta_bgr_gray': mean.tolist() if mean is not None else None,
                    'mean_column_delta_opponents': [float(mean[0]-mean[1]), float(mean[2]-mean[1])] if mean is not None else None,
                    'column_delta_bgr_gray': [row.tolist() if status == 'observed' and ok else None
                                             for row, ok in zip(delta, joint, strict=True)],
                }
            point_result['scales'].append({'band_width_px': width, 'bands': measured, 'pairs': pairs})
        result.append(point_result)
    return {'spec': copy.deepcopy(COLOR_SIDE_SPEC), 'decision': 'NOT_EVALUATED', 'points': result,
            'band_columns_measured': columns_used, 'sample_pixels_measured': pixels_used}
