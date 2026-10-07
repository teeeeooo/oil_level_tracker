"""Frozen uncalibrated region-exchange challenger; no production consumers.

Geometry comes from the current candidate, not truth or a propagated track.
Pixel fits are nuisance estimates, never supervised fits to candidate labels.
"""
from __future__ import annotations

import numpy as np

SPEC = {
    'id': 'joint-temporal-region-exchange-v1',
    'input': 'current and immediate native-frame neighbours, raw BGR, effective AND nonglare masks',
    'support': 'full-height recorded sector X strip; common pixels across each pair',
    'base': '1, normalized X, normalized Y, neighbour indicator',
    'models': ['smooth', 'illumination_plane', 'static_step', 'moving_step',
               'moving_ribbon_bw', 'moving_ribbon_2bw'],
    'extra_terms': 'step Y>=cut; ribbon abs(Y-cut)<width; illumination adds T*X and T*Y',
    'search': 'all integer neighbour cuts 1..height-1; current candidate cut fixed',
    'fit': 'float64 ordinary least squares; full rank; BGR/255; rcond=1e-10',
    'spatial_split': 'crop-local X modulo 4 == 0 validates; others fit all models on identical pixels',
    'operating_point': 'both temporal pairs: unique uncensored moving-step training minimum, '
                       'validation MSE strictly lower than every competitor by 1e-12; '
                       'all five recorded sectors must pass for candidate support; otherwise UNRESOLVED',
    'geometry': 'native views if any native view exists; otherwise candidate-center views; no invented sectors',
    'base_bw': 3, 'tie_atol': 1e-12, 'rank_rcond': 1e-10,
    'min_train_pixels_per_frame': 8, 'min_test_pixels_per_frame': 4,
    'max_height': 256, 'max_width': 256,
    'fit_partitions': [], 'evaluation_regime': 'EXPLORATORY_UNCALIBRATED',
    'limitations': 'Region interpretation is a tested hypothesis, not physical proof. '
                  'Reflections or unmodelled texture can collide; no motion-only authority, '
                  'new scalar, calibrated confidence or chemical-species output.',
}


def _check_raster(image, mask, shape=None):
    if (not isinstance(image, np.ndarray) or image.dtype != np.uint8 or image.ndim != 3
            or image.shape[2] != 3 or not 4 <= image.shape[0] <= SPEC['max_height']
            or not 4 <= image.shape[1] <= SPEC['max_width']):
        raise ValueError('bounded uint8 BGR raster required')
    if shape is not None and image.shape != shape:
        raise ValueError('pair raster shapes differ')
    if not isinstance(mask, np.ndarray) or mask.shape != image.shape[:2] or mask.dtype != np.bool_:
        raise ValueError('same-shape boolean validity required')


def measure_pair(anchor, neighbour, anchor_valid, neighbour_valid, *, x_range, current_y):
    """Return same-pixel model comparison. Never replace the current candidate Y."""
    _check_raster(anchor, anchor_valid)
    _check_raster(neighbour, neighbour_valid, anchor.shape)
    h, w = anchor.shape[:2]
    if (len(x_range) != 2 or any(type(x) is not int for x in x_range)
            or not 0 <= x_range[0] < x_range[1] <= w):
        raise ValueError('valid integer X interval required')
    if (isinstance(current_y, (bool, np.bool_))
            or not isinstance(current_y, (int, float, np.integer, np.floating))
            or not np.isfinite(current_y)):
        raise ValueError('finite current candidate Y required')
    if not 0 <= current_y < h:
        raise ValueError('candidate outside raster')
    x0, x1 = x_range
    yy, xx = np.mgrid[:h, x0:x1]
    common = anchor_valid[:, x0:x1] & neighbour_valid[:, x0:x1]
    train = common & (xx % 4 != 0)
    test = common & (xx % 4 == 0)
    result = dict(status='unavailable', supported=False, current_y=float(current_y),
                  x_range=list(x_range), train_pixels_per_frame=int(train.sum()),
                  test_pixels_per_frame=int(test.sum()), models={}, reason='insufficient_common_support')
    if (train.sum() < SPEC['min_train_pixels_per_frame']
            or test.sum() < SPEC['min_test_pixels_per_frame']):
        return result
    # The coordinate normalization depends only on geometry, not image values.
    xn = (xx-x0)/max(1, x1-x0-1)
    yn = yy/max(1, h-1)
    spatial = np.stack([np.ones_like(xn), xn, yn], axis=-1)
    base = np.concatenate([
        np.concatenate([spatial, np.zeros_like(xn)[..., None]], axis=-1)[None],
        np.concatenate([spatial, np.ones_like(xn)[..., None]], axis=-1)[None]], axis=0)
    values = np.stack([anchor[:, x0:x1], neighbour[:, x0:x1]]).astype(np.float64)/255
    tr, te = np.stack([train, train]), np.stack([test, test])
    xtr, xte, ytr, yte = base[tr], base[te], values[tr], values[te]
    beta, _, rank, _ = np.linalg.lstsq(xtr, ytr, rcond=SPEC['rank_rcond'])
    if rank != 4:
        return dict(result, reason='rank_deficient_base')
    inverse = np.linalg.pinv(xtr, rcond=SPEC['rank_rcond'])
    residual = ytr-xtr@beta
    predicted = xte@beta

    def plain(design):
        a, b = design[tr], design[te]
        coeff, _, n, _ = np.linalg.lstsq(a, ytr, rcond=SPEC['rank_rcond'])
        if n != a.shape[1]:
            return dict(status='rank_deficient', train_mse=None, validation_mse=None)
        return dict(status='measured', train_mse=float(np.mean((a@coeff-ytr)**2)),
                    validation_mse=float(np.mean((b@coeff-yte)**2)))

    def indicator(kind, cut):
        if kind == 'step':
            return yy >= cut
        width = SPEC['base_bw']*(2 if kind == 'ribbon_2bw' else 1)
        return np.abs(yy-cut) < width

    def conditional(kind, search):
        z0 = indicator(kind, current_y)
        fits = []
        for cut in search:
            z = np.stack([z0, indicator(kind, cut)]).astype(np.float64)
            ztr, zte = z[tr], z[te]
            projection = inverse@ztr
            rz = ztr-xtr@projection
            denominator = float(rz@rz)
            if denominator <= SPEC['rank_rcond']:
                continue
            coeff = (rz@residual)/denominator
            train_error = float(np.mean((residual-rz[:, None]*coeff)**2))
            test_error = float(np.mean((predicted+(zte-xte@projection)[:, None]*coeff-yte)**2))
            fits.append(dict(neighbour_cut=float(cut), train_mse=train_error, validation_mse=test_error))
        if not fits:
            return dict(status='rank_deficient', train_mse=None, validation_mse=None, fits=[])
        minimum = min(f['train_mse'] for f in fits)
        tied = [f for f in fits if abs(f['train_mse']-minimum) <= SPEC['tie_atol']]
        best = tied[0]  # deterministic geometry order; tie is retained, never confidence.
        return dict(status='measured', **best, tied_cuts=[f['neighbour_cut'] for f in tied], fits=fits)

    models = {'smooth': plain(base)}
    t = base[..., 3]
    illumination = np.concatenate([base, (t*xn)[..., None], (t*yn)[..., None]], axis=-1)
    models['illumination_plane'] = plain(illumination)
    models['static_step'] = conditional('step', [current_y])
    models['moving_step'] = conditional('step', range(1, h))
    models['moving_ribbon_bw'] = conditional('ribbon_bw', range(1, h))
    models['moving_ribbon_2bw'] = conditional('ribbon_2bw', range(1, h))
    result.update(status='measured', models=models)
    if any(m['status'] != 'measured' for m in models.values()):
        return dict(result, reason='incomplete_competitor_support')
    step = models['moving_step']
    if len(step['tied_cuts']) != 1:
        return dict(result, reason='ambiguous_moving_step')
    if step['neighbour_cut'] in (1, h-1) or current_y in (0, h-1):
        return dict(result, reason='censored_step')
    # A ribbon whose return is outside the raster cannot disprove that alternative.
    for name, width in [('moving_ribbon_bw', SPEC['base_bw']),
                        ('moving_ribbon_2bw', 2*SPEC['base_bw'])]:
        cuts = [current_y, *models[name]['tied_cuts']]
        if any(c-width < 0 or c+width >= h for c in cuts):
            return dict(result, reason='censored_ribbon_alternative')
        for cut in cuts:
            z = np.abs(yy-cut) < width
            edge = (z[1:] != z[:-1]) & common[1:] & common[:-1]
            edge_y = yy[1:][edge]
            if not (np.any(edge_y < cut) and np.any(edge_y >= cut)):
                return dict(result, reason='masked_ribbon_return')
    margin = min(m['validation_mse'] for name, m in models.items() if name != 'moving_step')-step['validation_mse']
    return dict(result, supported=margin > SPEC['tie_atol'], validation_margin=float(margin),
                reason='moving_partition_dominates' if margin > SPEC['tie_atol'] else 'competing_explanation')


def decide_candidate(views):
    """Conservative five-sector conjunction, not majority/max or independent votes."""
    if len(views) != 5 or {v['sector'] for v in views} != set(range(5)):
        return 'UNRESOLVED', 'incomplete_recorded_sector_geometry'
    if not all(len(v['pairs']) == 2 and all(p['supported'] for p in v['pairs']) for v in views):
        return 'UNRESOLVED', 'joint_spatial_temporal_support_not_established'
    return 'INTERFACE_SUPPORTED', 'all_recorded_sectors_support_joint_region_exchange'
