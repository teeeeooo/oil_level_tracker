"""Offline local arm topology of an existing edge raster, never Oil identity.

Preserves ordered contact geometry that band means/component counts discard.
No Canny recomputation, dilation, gap filling, thinning or physical labels.
"""
from __future__ import annotations

import cv2
import numpy as np

SPEC = {
    'id': 'saved-canny-local-arm-contact-v1',
    'edge_owner': 'unchanged captured preprocessing.canny',
    'connectivity': 8,
    'removed_core_radius': 1,
    'reference_half_width': 'existing witness band_width_px at each of its three scales',
    'patch_radius': '2 * reference_half_width; scales retained separately',
    'geometry': 'native_path when present, otherwise recorded candidate_center; no relocation',
    'decision': 'NOT_EVALUATED',
    'limits': 'Raster topology is not physical contact, target identity or scalar truth. '
              'No marker is not non-interface. Captured preprocessing remains an input limitation.',
}
MAX_PIXELS = 262_144
MAX_PATCH_PIXELS = 50_000_000


def _arm_pattern(patch):
    """Branches of the center component after removing its 3x3 junction core."""
    radius = patch.shape[0] // 2
    _, labels = cv2.connectedComponents(patch.astype(np.uint8), connectivity=8)
    component = labels == labels[radius, radius]
    component[radius-1:radius+2, radius-1:radius+2] = False
    count, split = cv2.connectedComponents(component.astype(np.uint8), connectivity=8)
    yy, xx = np.indices(patch.shape)
    dx, dy = xx-radius, yy-radius
    distance = np.maximum(np.abs(dx), np.abs(dy))
    inner, outer = distance == 2, distance == radius
    arms = []
    short = 0
    for label in range(1, count):
        branch = split == label
        if not np.any(branch & inner):
            continue
        exits = branch & outer
        if not np.any(exits):
            short += 1
            continue
        directions = set()
        for ex, ey in zip(dx[exits], dy[exits], strict=True):
            if abs(ex) == abs(ey):
                directions.add('corner')
            elif abs(ex) > abs(ey):
                directions.add('right' if ex > 0 else 'left')
            else:
                directions.add('down' if ey > 0 else 'up')
        arms.append(sorted(directions))
    arms.sort()
    singles = sorted(a[0] for a in arms if len(a) == 1)
    if short or len(singles) != len(arms) or 'corner' in singles or len(set(singles)) != len(singles):
        pattern = 'complex_or_short'
    elif singles == ['left', 'right', 'up']:
        pattern = 'upper_contact_shape'
    elif singles == ['down', 'left', 'right']:
        pattern = 'lower_contact_shape'
    elif singles == ['down', 'left', 'right', 'up']:
        pattern = 'crossing_shape'
    elif len(singles) == 2:
        pattern = 'two_arm_shape'
    elif len(singles) == 1:
        pattern = 'one_arm_shape'
    elif not singles:
        pattern = 'no_reaching_arm'
    else:
        pattern = 'other_arm_shape'
    return {'pattern': pattern, 'arms': arms, 'short_branches': short}


def measure_edge_contacts(edges, visible, *, radii, origin=(0, 0)):
    """Read all existing edge centers; unavailable patches never imply a negative."""
    if (not isinstance(edges, np.ndarray) or edges.ndim != 2 or edges.dtype != bool
            or not edges.size or edges.size > MAX_PIXELS):
        raise ValueError('bounded nonempty boolean edge raster required')
    if (not isinstance(visible, np.ndarray) or visible.shape != edges.shape
            or visible.dtype != bool):
        raise ValueError('same-shape boolean visible raster required')
    if (not isinstance(radii, (tuple, list)) or not 1 <= len(radii) <= 3
            or any(type(r) is not int or not 3 <= r <= 32 for r in radii)
            or len(set(radii)) != len(radii)):
        raise ValueError('one to three distinct integer radii in 3..32 required')
    if len(origin) != 2 or any(type(v) is not int for v in origin):
        raise ValueError('integer source origin required')
    edge_positions = np.argwhere(edges & visible)
    cost = len(edge_positions) * sum((2*r+1)**2 for r in radii)
    if cost > MAX_PATCH_PIXELS:
        raise ValueError('edge patch resource bound exceeded')
    ox, oy = origin
    h, w = edges.shape
    results = []
    availability = {}
    for radius in radii:
        available = cv2.erode(visible.astype(np.uint8),
                             np.ones((2*radius+1, 2*radius+1), np.uint8),
                             borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
        availability[radius] = available
        for y, x in edge_positions:
            record = {'source_x': int(x+ox), 'source_y': int(y+oy), 'radius': radius}
            if not available[y, x]:
                clipped = x < radius or x+radius >= w or y < radius or y+radius >= h
                record.update(status='unavailable', reason='outside_crop' if clipped else 'masked_patch',
                              pattern=None, arms=None, short_branches=None)
            else:
                patch = edges[y-radius:y+radius+1, x-radius:x+radius+1]
                record.update(status='measured', reason='fully_observed_saved_edge_patch',
                              **_arm_pattern(patch))
            results.append(record)
    return ({'spec_id': SPEC['id'], 'decision': 'NOT_EVALUATED',
             'physical_identity': 'UNRESOLVED', 'origin': list(origin),
             'shape': [h, w], 'radii': list(radii),
             'visible_edge_centers': len(edge_positions), 'patch_pixel_budget_used': cost,
             'nodes': results}, availability)


def query_reference(measurement, availability, *, x_range, source_y, half_width):
    """Bind node coordinates to unchanged reference geometry; never choose a new Y."""
    ox, oy = measurement['origin']
    h, w = measurement['shape']
    if (len(x_range) != 2 or any(type(x) is not int for x in x_range)
            or not ox <= x_range[0] < x_range[1] <= ox+w
            or type(half_width) is not int or 2*half_width not in availability
            or isinstance(source_y, (bool, np.bool_)) or not np.isfinite(source_y)
            or not oy <= source_y < oy+h):
        raise ValueError('bounded original reference geometry required')
    radius = 2*half_width
    lower, upper = int(np.ceil(source_y-half_width)), int(np.floor(source_y+half_width))
    y0, y1 = max(oy, lower)-oy, min(oy+h, upper+1)-oy
    x0, x1 = x_range[0]-ox, x_range[1]-ox
    nodes = [n for n in measurement['nodes'] if n['radius'] == radius
             and x_range[0] <= n['source_x'] < x_range[1]
             and lower <= n['source_y'] <= upper]
    counts = {}
    for node in nodes:
        key = node['pattern'] if node['status'] == 'measured' else 'unavailable'
        counts[key] = counts.get(key, 0) + 1
    return {'source_x_range': list(x_range), 'reference_source_y': float(source_y),
            'half_width': half_width, 'patch_radius': radius,
            'requested_centers': (upper-lower+1)*(x1-x0),
            'in_crop_centers': (y1-y0)*(x1-x0),
            'fully_observed_centers': int(availability[radius][y0:y1, x0:x1].sum()),
            'edge_center_count': len(nodes), 'pattern_counts': counts, 'nodes': nodes,
            'decision': 'NOT_EVALUATED'}


CLEARANCE_SPEC = {
    'id': 'saved-canny-ordered-column-clearance-v1',
    'edge_owner': 'unchanged captured preprocessing.canny',
    'reference_band': 'all integer rows within each existing witness band_width_px of original Y',
    'ray': 'one source column outward from each band end, stopping at first edge, mask or crop',
    'geometry': 'native_path when present, otherwise recorded candidate_center; no relocation',
    'censoring': 'mask/crop stop is a lower bound on observed clear pixels, never an edge distance',
    'aggregation': 'retain every column and scale; no threshold, score or chosen scale',
    'decision': 'NOT_EVALUATED',
    'limits': 'Edge-free space is not empty material. Optical copies yield identical geometry. '
              'No row/column trace proves physical contact, material identity or scalar eligibility.',
}


def measure_edge_clearance(edges, visible, *, x_range, source_y, half_width, origin=(0, 0)):
    """Read ordered empty runs beside an unchanged reference, with censored ends.

    Unlike a T junction this does not require upper features to attach to the
    candidate edge. A run stops before hidden pixels and never crosses a gap in
    visibility. The reference band is recorded, not used to snap the given Y.
    """
    if (not isinstance(edges, np.ndarray) or edges.ndim != 2 or edges.dtype != bool
            or not edges.size or edges.size > MAX_PIXELS):
        raise ValueError('bounded nonempty boolean edge raster required')
    if (not isinstance(visible, np.ndarray) or visible.shape != edges.shape
            or visible.dtype != bool):
        raise ValueError('same-shape boolean visible raster required')
    if len(origin) != 2 or any(type(v) is not int for v in origin):
        raise ValueError('integer source origin required')
    ox, oy = origin
    h, w = edges.shape
    if (len(x_range) != 2 or any(type(x) is not int for x in x_range)
            or not ox <= x_range[0] < x_range[1] <= ox+w
            or type(half_width) is not int or not 1 <= half_width <= 32
            or not isinstance(source_y, (int, float, np.integer, np.floating))
            or isinstance(source_y, (bool, np.bool_)) or not np.isfinite(source_y)
            or not oy <= source_y < oy+h):
        raise ValueError('bounded original reference geometry required')
    lower = int(np.ceil(source_y-half_width))-oy
    upper = int(np.floor(source_y+half_width))-oy

    def ray(x, start, step):
        y, clear = start, 0
        while 0 <= y < h:
            if not visible[y, x]:
                reason = 'masked'
                break
            if edges[y, x]:
                return {'status': 'edge_found', 'stop_source_y': y+oy,
                        'clear_pixel_count': clear,
                        'edge_distance_from_reference': abs(y+oy-float(source_y))}
            clear += 1
            y += step
        else:
            reason = 'outside_crop'
        return {'status': 'censored', 'reason': reason, 'stop_source_y': y+oy,
                'clear_pixel_count': clear, 'edge_distance_from_reference': None}

    columns = []
    for sx in range(*x_range):
        x = sx-ox
        row = {'source_x': sx}
        if lower < 0 or upper >= h or not np.all(visible[lower:upper+1, x]):
            row.update(status='reference_unavailable',
                       reason='outside_crop' if lower < 0 or upper >= h else 'masked_band',
                       band_edge_source_y=None, above=None, below=None,
                       below_minus_above_edge_distance=None)
        else:
            above, below = ray(x, lower-1, -1), ray(x, upper+1, 1)
            da, db = above['edge_distance_from_reference'], below['edge_distance_from_reference']
            row.update(status='measured',
                       band_edge_source_y=(np.flatnonzero(edges[lower:upper+1, x])+lower+oy).tolist(),
                       above=above, below=below,
                       below_minus_above_edge_distance=None if da is None or db is None else db-da)
        columns.append(row)
    return {'spec_id': CLEARANCE_SPEC['id'], 'origin': list(origin), 'shape': [h, w],
            'source_x_range': list(x_range), 'reference_source_y': float(source_y),
            'half_width': half_width, 'reference_band_source_y': [lower+oy, upper+oy],
            'columns': columns, 'decision': 'NOT_EVALUATED', 'physical_identity': 'UNRESOLVED'}
