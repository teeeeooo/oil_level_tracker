"""Offline anchor-coordinate residuals, not Foam tracking or physical identity.

Reuse production registration/exposure math; preserve failure diagnostics. All
four ablations use the same fully interpolable support, without thresholding.
"""
from __future__ import annotations

import cv2
import numpy as np
from oil_tracker.adapters.vision import temporal_raster_evidence as temporal

CHANNELS = ('direct', 'exposure_only', 'registered', 'registered_exposure')
MAX_PIXELS = 4_194_304


def measure_pair(anchor, current, geometry_mask):
    if (not isinstance(anchor, np.ndarray) or anchor.ndim != 2 or anchor.dtype != np.uint8
            or not anchor.size or anchor.size > MAX_PIXELS):
        raise ValueError('bounded nonempty uint8 anchor required')
    if not isinstance(current, np.ndarray) or current.shape != anchor.shape or current.dtype != np.uint8:
        raise ValueError('current must be same-shape uint8')
    if (not isinstance(geometry_mask, np.ndarray) or geometry_mask.shape != anchor.shape
            or geometry_mask.dtype != np.bool_):
        raise ValueError('same-shape boolean geometry mask required')
    meta = {'status': 'insufficient_geometry', 'decision': 'NOT_EVALUATED',
            'physical_identity': 'UNRESOLVED', 'foam_front': None,
            'registration_current_to_anchor': None, 'registration_anchor_to_current': None,
            'cycle_translation_error_px': None, 'common_pixels': 0,
            'glare_validity': 'NOT_MEASURED',
            'limits': 'One ROI translation can follow changing material; accepted numerical registration '
                      'is not independently verified camera motion. Fixed anchor queries are not tracks. '
                      'Photometric residual is not displacement or physical identity; glare is not excluded.'}
    shape = anchor.shape
    empty = {key: np.full(shape, np.nan, np.float32) for key in CHANNELS}
    empty['valid'] = np.zeros(shape, bool)
    if geometry_mask.sum() < 32:
        return meta, empty
    a, b = anchor.astype(np.float32), current.astype(np.float32)
    forward, reverse = {}, {}
    dx, dy, _ = temporal._translation(b, a, geometry_mask, diagnostics=forward)
    rx, ry, _ = temporal._translation(a, b, geometry_mask, diagnostics=reverse)
    meta.update(registration_current_to_anchor=forward, registration_anchor_to_current=reverse)
    if forward['status'] != 'accepted' or reverse['status'] != 'accepted':
        meta['status'] = 'registration_unavailable'
        return meta, empty
    meta['cycle_translation_error_px'] = float(np.hypot(dx+rx, dy+ry))
    transform = np.array([[1, 0, dx], [0, 1, dy]], np.float32)
    size = (shape[1], shape[0])
    warped = cv2.warpAffine(b, transform, size, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    # Same interpolation and border rule: all contributing pixels must be valid.
    donor_weight = cv2.warpAffine(geometry_mask.astype(np.float32), transform, size,
                                 flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    common = geometry_mask & (donor_weight == 1.0)
    meta['common_pixels'] = int(common.sum())
    if common.sum() < 32:
        meta['status'] = 'insufficient_registered_support'
        return meta, empty
    direct_gain, direct_offset = temporal._exposure_fit(b[common], a[common])
    gain, offset = temporal._exposure_fit(warped[common], a[common])
    meta.update(status='measured', exposure_only_gain=direct_gain, exposure_only_offset=direct_offset,
                registered_gain=gain, registered_offset=offset)
    values = (np.abs(a-b), np.abs(a-(direct_gain*b+direct_offset)),
              np.abs(a-warped), np.abs(a-(gain*warped+offset)))
    arrays = {key: np.where(common, value, np.nan).astype(np.float32)
              for key, value in zip(CHANNELS, values)}
    arrays['valid'] = common
    meta['mean_absolute_residual'] = {key: float(arrays[key][common].mean()) for key in CHANNELS}
    return meta, arrays


def sample_queries(arrays, points, *, origin=(0, 0), radius=2):
    """Fixed anchor-coordinate squares; no tracking, masking by material or fitting."""
    if type(radius) is not int or not 0 <= radius <= 16:
        raise ValueError('radius must be an integer in 0..16')
    if len(origin) != 2 or any(type(v) is not int for v in origin):
        raise ValueError('integer source origin required')
    if len(points) > 4096:
        raise ValueError('point bound exceeded')
    mask = arrays['valid']
    if mask.ndim != 2 or mask.dtype != np.bool_:
        raise ValueError('boolean validity required')
    for key in CHANNELS:
        if arrays[key].shape != mask.shape or not np.isfinite(arrays[key][mask]).all():
            raise ValueError('invalid residual array')
    h, w = mask.shape
    result = []
    for p in points:
        sx, sy = p['source_x'], p['source_y']
        if type(sx) is not int or type(sy) is not int:
            raise ValueError('integer source query required')
        x, y = sx-origin[0], sy-origin[1]
        if not 0 <= x < w or not 0 <= y < h:
            raise ValueError('query outside anchor ROI')
        x0, x1 = max(0, x-radius), min(w, x+radius+1)
        y0, y1 = max(0, y-radius), min(h, y+radius+1)
        valid = mask[y0:y1, x0:x1]
        count = int(valid.sum())
        result.append({'source_x': sx, 'source_y': sy, 'radius_px': radius,
                       'requested_pixels': (2*radius+1)**2, 'valid_pixels': count,
                       'fully_observed': count == (2*radius+1)**2,
                       'mean_absolute_residual': {
                           key: float(arrays[key][y0:y1, x0:x1][valid].mean()) if count else None
                           for key in CHANNELS}})
    return result
