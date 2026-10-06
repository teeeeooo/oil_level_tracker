"""Read-only column geometry of saved Foam supports; never a substrate classifier.

The production Foam owner remains responsible for its existing gate. This probe
exposes bounding-box versus pixel placement without choosing a gap threshold,
material identity, component winner or Foam front.
"""
from __future__ import annotations

import numpy as np

MAX_PIXELS = 4_194_304


def _box(mask, origin):
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    ox, oy = origin
    return [int(xs.min()) + ox, int(ys.min()) + oy,
            int(xs.max()) + 1 + ox, int(ys.max()) + 1 + oy]


def measure(labels, visible, target_id, reference_id, *, origin=(0, 0)):
    """Measure retained raster IDs on one ROI; zeros/absent IDs are not negatives.

    A below gap counts rows strictly between the target column's LAST pixel and
    the reference's first pixel below it. Interleaving is separately recorded.
    Masked corridors retain their geometric gap but are not fully observed.
    No upper/lower extent is a physical boundary or a complete component mask.
    """
    if (not isinstance(labels, np.ndarray) or labels.ndim != 2
            or labels.dtype != np.uint16 or not labels.size
            or labels.size > MAX_PIXELS):
        raise ValueError('labels must be a nonempty bounded 2-D uint16 raster')
    if (not isinstance(visible, np.ndarray) or visible.shape != labels.shape
            or visible.dtype != np.bool_):
        raise ValueError('visible must be a same-shape boolean raster')
    if (any(type(i) is not int or not 1 <= i <= 65535 for i in (target_id, reference_id))
            or target_id == reference_id):
        raise ValueError('two distinct nonzero uint16 IDs required')
    if len(origin) != 2 or any(type(v) is not int for v in origin):
        raise ValueError('origin must contain two integers')
    target = labels == target_id
    reference = labels == reference_id
    if np.any((target | reference) & ~visible):
        raise ValueError('retained support lies outside the supplied visible mask')
    ox, oy = origin
    tb, rb = _box(target, origin), _box(reference, origin)
    rows = []
    for x in np.flatnonzero(target.any(axis=0)):
        a = np.flatnonzero(target[:, x])
        b = np.flatnonzero(reference[:, x])
        lo, hi = int(a[0]), int(a[-1])
        below = b[b > hi]
        above = b[b < lo]
        nb = int(below[0]) if len(below) else None
        na = int(above[-1]) if len(above) else None
        rows.append({
            'source_x': int(x) + ox,
            'target_top_source_y': lo + oy, 'target_bottom_source_y': hi + oy,
            'target_pixels': int(a.size), 'reference_pixels': int(b.size),
            'reference_top_source_y': int(b[0]) + oy if len(b) else None,
            'reference_bottom_source_y': int(b[-1]) + oy if len(b) else None,
            'reference_pixels_in_target_y_extent': int(np.count_nonzero((b >= lo) & (b <= hi))),
            'nearest_reference_below_source_y': nb + oy if nb is not None else None,
            'below_gap_px': nb - hi - 1 if nb is not None else None,
            'below_corridor_fully_visible': bool(visible[hi:nb+1, x].all()) if nb is not None else None,
            'nearest_reference_above_source_y': na + oy if na is not None else None,
            'above_gap_px': lo - na - 1 if na is not None else None,
            'above_corridor_fully_visible': bool(visible[na:lo+1, x].all()) if na is not None else None,
            'target_top_preceding_pixel_visible': bool(lo > 0 and visible[lo-1, x]),
            'target_bottom_following_pixel_visible': bool(hi+1 < labels.shape[0] and visible[hi+1, x]),
        })
    gaps = [r['below_gap_px'] for r in rows if r['below_corridor_fully_visible'] is True]
    return {
        'schema_version': 's11-foam-support-geometry-v1',
        'status': 'measured' if tb is not None and rb is not None else 'missing_retained_support',
        'decision': 'NOT_EVALUATED', 'physical_identity': 'UNRESOLVED',
        'substrate_decision': 'NOT_ASSIGNED', 'foam_front': 'NOT_ASSIGNED',
        'target_id': target_id, 'reference_id': reference_id,
        'origin': list(origin), 'shape': list(labels.shape),
        'bbox_convention': 'source_xyxy_half_open',
        'target_bbox': tb, 'reference_bbox': rb,
        'bbox_x_overlap_px': max(0, min(tb[2], rb[2])-max(tb[0], rb[0])) if tb and rb else None,
        'bbox_below_gap_px': rb[1]-tb[3] if tb and rb else None,
        'target_columns': len(rows),
        'shared_columns': sum(r['reference_pixels'] > 0 for r in rows),
        'columns_with_reference_in_target_y_extent': sum(r['reference_pixels_in_target_y_extent'] > 0 for r in rows),
        'below_columns': sum(r['below_gap_px'] is not None for r in rows),
        'fully_visible_below_columns': len(gaps),
        'visible_below_gap_min': min(gaps) if gaps else None,
        'visible_below_gap_max': max(gaps) if gaps else None,
        'columns': rows,
        'limits': 'retained support only; no reference in a column is not physical absence; '
                  'a clear mask corridor is not material identity or proof of no optical obstruction',
    }
