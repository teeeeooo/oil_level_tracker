"""Bounded raw-pixel appearance fits at recorded geometry; no identity classifier.

The saved-output loader owns provenance. This module owns the frozen linear
models, held-out error and adjacency calculations, not acquisition or ranking.
"""
from __future__ import annotations

import copy

import numpy as np

from tests.diagnostics import s11_interface_shadow_evaluation as o2
from tests.diagnostics import s11_spatial_context_probe as probe


SPEC = {
    'id': 'candidate-region-competition-v1',
    'models': {'smooth': 3, 'partition': 4, 'ribbon_bw': 4, 'ribbon_2bw': 4},
    'basis': '1, normalized X, normalized Y; partition adds Y>=recorded source Y; '
             'ribbons add abs(Y-recorded source Y)<BW or <2*BW',
    'fit': 'float64 unregularized least squares per channel; full rank required; rcond=1e-10',
    'holdout': 'local crop X modulo 4 == 0; other columns train; identical split for every model/view',
    'loss': 'held-out mean squared residual over visible pixels AND channels, divided by 255^2',
    'support': ['recorded_bands', 'candidate_envelope'],
    'channels': ['gray', 'BGR'],
    'eligibility': 'all four recorded bands available; no rescue by envelope pixels',
    'adjacency': 'immediate visible neighbours on same candidate side, horizontal/vertical separately; no gap bridge',
    'aggregation': 'none; all geometry, roles, widths, support and channel views retained',
    'opposition': 'physical material/static/template evidence not measured by this saved-output model',
    'physical_identity': 'UNRESOLVED', 'decision': 'NOT_EVALUATED',
    'max_patch_pixels': 262144, 'max_total_patch_pixels': 50000000,
    'min_train_pixels': 8, 'min_test_pixels': 4, 'rank_rcond': 1e-10,
}


def _adjacency(values, mask, side):
    result = {}
    for name, a, b in (
        ('horizontal', (slice(None), slice(None, -1)), (slice(None), slice(1, None))),
        ('vertical', (slice(None, -1), slice(None)), (slice(1, None), slice(None))),
    ):
        valid = mask[a] & mask[b] & (side[a] == side[b])
        count = int(valid.sum())
        delta = values[a]-values[b]
        result[name] = {'pair_count': count,
                        'mean_squared_difference': float(np.mean(delta[valid]**2)) if count else None}
    return result


def _fit_view(values, mask, xx, yy, center_y, width, eligible):
    """Fits pixels in 2-D; never fits pooled band/row values or searches a center."""
    side = yy >= center_y
    train = mask & (xx.astype(np.int64) % 4 != 0)
    test = mask & ~train
    count_train, count_test = int(train.sum()), int(test.sum())
    state = ('o1_unavailable' if not eligible else 'insufficient_split_support'
             if count_train < SPEC['min_train_pixels'] or count_test < SPEC['min_test_pixels'] else 'observed')
    result = {
        'status': state, 'train_pixels': count_train, 'test_pixels': count_test,
        'visible_pixels': int(mask.sum()),
        'side_pixels': {'above': int((mask & ~side).sum()), 'below': int((mask & side).sum())},
        'within_side_adjacency': _adjacency(values, mask, side),
        'models': {}, 'physical_identity': 'UNRESOLVED',
    }
    # Normalization uses the geometric envelope, never pixel content or identity.
    x = (xx-xx.min()) / max(1, int(xx.max()-xx.min()))
    y = (yy-center_y) / max(1, int(yy.max()-yy.min()))
    base = np.stack([np.ones_like(x), x, y], axis=-1)
    terms = {'smooth': None, 'partition': side,
             'ribbon_bw': np.abs(yy-center_y) < width,
             'ribbon_2bw': np.abs(yy-center_y) < 2*width}
    for name, term in terms.items():
        item = {'parameters_per_channel': SPEC['models'][name], 'status': state,
                'train_mse': None, 'heldout_mse': None, 'rank': None, 'coefficients': None}
        if term is not None:
            edges = mask[1:] & mask[:-1] & (term[1:] != term[:-1])
            result_y = yy[1:][edges]
            item['observed_indicator_edge_pairs'] = {
                'above_center': int((result_y < center_y).sum()),
                'at_or_below_center': int((result_y >= center_y).sum()),
            }
        if state == 'observed':
            design = base if term is None else np.concatenate([base, term[..., None]], axis=-1)
            coeff, _, rank, _ = np.linalg.lstsq(design[train], values[train], rcond=SPEC['rank_rcond'])
            item['rank'] = int(rank)
            if rank == design.shape[-1]:
                item.update(coefficients=coeff.tolist(),
                            train_mse=float(np.mean((design[train] @ coeff-values[train])**2)),
                            heldout_mse=float(np.mean((design[test] @ coeff-values[test])**2)))
            else:
                item['status'] = 'rank_deficient'
        result['models'][name] = item
    if state == 'observed' and any(m['status'] != 'observed' for m in result['models'].values()):
        result['status'] = 'incomplete_model_support'
    return result


def measure(crop, gray, effective, glare, points, *, origin=(0, 0)):
    """Return a factorial ledger. O1 and color-side validation share one owner."""
    checked = probe.measure_color_side(crop, gray, effective, glare, points, origin=origin)
    ox, oy = origin
    total = 0
    # Preflight every envelope before model work (including unavailable views).
    for point in checked['points']:
        for scale in point['scales']:
            lo = min(b['clipped_local_y_range'][0] for b in scale['bands'])
            hi = max(b['clipped_local_y_range'][1] for b in scale['bands'])
            pixels = (hi-lo)*(point['source_x_range'][1]-point['source_x_range'][0])
            total += pixels
            o2.require(0 < pixels <= SPEC['max_patch_pixels'] and total <= SPEC['max_total_patch_pixels'],
                       'region sampling resource bound exceeded')
    result = []
    for point in checked['points']:
        entry = {k: copy.deepcopy(v) for k, v in point.items() if k != 'scales'}
        entry['scales'] = []
        x0, x1 = [x-ox for x in point['source_x_range']]
        for scale in point['scales']:
            bands = scale['bands']
            lo = min(b['clipped_local_y_range'][0] for b in bands)
            hi = max(b['clipped_local_y_range'][1] for b in bands)
            original = np.zeros((hi-lo, x1-x0), dtype=bool)
            for band in bands:
                a, b = band['clipped_local_y_range']
                original[a-lo:b-lo] = True
            visible = (effective[lo:hi, x0:x1] > 0) & (glare[lo:hi, x0:x1] == 0)
            yy, xx = np.mgrid[lo:hi, x0:x1]
            eligible = all(b['o1_available'] for b in bands)
            item = {
                'band_width_px': scale['band_width_px'], 'bands': bands,
                'envelope_source_y_range': [lo+oy, hi+oy],
                'requested_envelope_source_y_range': [min(b['local_y_range'][0] for b in bands)+oy,
                                                      max(b['local_y_range'][1] for b in bands)+oy],
                'crop_clipped': any(b['local_y_range'] != b['clipped_local_y_range'] for b in bands),
                'envelope_pixels': int(visible.size), 'masked_pixels': int((~visible).sum()),
                'original_band_visible_pixels': int((visible & original).sum()),
                'added_envelope_visible_pixels': int((visible & ~original).sum()),
                'extent': 'bounded_window; no claim about return or persistence outside support',
                'views': [],
            }
            for support, mask in [('recorded_bands', visible & original), ('candidate_envelope', visible)]:
                for channel, raw in [('gray', gray[lo:hi, x0:x1, None]), ('BGR', crop[lo:hi, x0:x1])]:
                    view = _fit_view(raw.astype(np.float64)/255., mask, xx, yy,
                                     point['source_y']-oy, scale['band_width_px'], eligible)
                    item['views'].append({'support': support, 'channels': channel, **view})
            entry['scales'].append(item)
        result.append(entry)
    return {'spec': copy.deepcopy(SPEC), 'decision': 'NOT_EVALUATED',
            'physical_identity': 'UNRESOLVED', 'points': result,
            'sample_patch_pixels': total, 'opposition_status': 'not_measured',
            'limitation': 'Same-frame overlapping fits are correlated. Template/material/static opposition and '
                          'physical connectivity are not measured. No candidate winner, threshold or scalar output.'}
