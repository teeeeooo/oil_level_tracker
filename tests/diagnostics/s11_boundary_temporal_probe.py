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

# Appearance correspondence only. No displacement, speed, polarity or identity gate.
PATCH_SPEC = {
    'id': 'ordered-bgr-patch-correspondence-v1',
    'support': 'full rectangular ordered BGR patch; no resize, pooling or interpolation',
    'search': 'every fully contained integer Y in the same X interval',
    'loss': 'per-channel mean-centered squared pixel error divided by 255^2',
    'tie_atol': 1e-12,
    'max_compared_pixels': 50_000_000,
    'physical_identity': 'UNRESOLVED',
    'decision': 'NOT_EVALUATED',
    'limits': 'Raw appearance; no glare/material/camera validity is established. '
              'Unique appearance match and reciprocal agreement do not establish physical identity.',
}

SPLIT_SIDE_SPEC = {
    'id': 'ordered-two-side-transport-v1',
    'search': 'all fully visible integer 2D placements; no speed or direction prior',
    'sides': 'equal-depth ordered BGR strips above and below an excluded plateau',
    'fit': 'exact integer squared error with one additive BGR offset per side',
    'comparison': 'common displacement versus independent side displacements',
    'validation': 'alternate local columns, both train/test folds; no fitted tolerance',
    'max_compared_samples': 8_000_000,
    'max_offsets': 65_536,
    'physical_identity': 'UNRESOLVED',
    'limits': 'Transport of appearance is not physical flow or Foam identity. '
              'Adjacent columns and the two folds are correlated. Ties abstain. '
              'No camera truth, scalar, speed cutoff, optical-visibility inference or selection.',
}


def _side_costs(template, windows, columns):
    """Exact training numerator after fitting additive per-channel offsets."""
    diff = template[:, columns].astype(np.int16) - windows[:, :, columns].astype(np.int16)
    n = diff.shape[1] * diff.shape[2]
    sums = diff.sum(axis=(1, 2), dtype=np.int64)
    squared = np.square(diff.astype(np.int32)).sum(axis=(1, 2, 3), dtype=np.int64)
    return squared * n - np.square(sums).sum(axis=1), sums, n


def _test_side(template, window, columns, train_sum, train_count):
    diff = template[:, columns].astype(np.int16) - window[:, columns].astype(np.int16)
    test_count = diff.shape[0] * diff.shape[1]
    test_sum = diff.sum(axis=(0, 1), dtype=np.int64)
    squared = int(np.square(diff.astype(np.int32)).sum(dtype=np.int64))
    # Scale exact aggregate moments with Python integers: summing squared scaled
    # residuals in int64 can overflow for a large, otherwise valid patch.
    cross = sum(int(a) * int(b) for a, b in zip(test_sum, train_sum, strict=True))
    offset_squared = sum(int(v)**2 for v in train_sum)
    numerator = train_count**2 * squared - 2 * train_count * cross + test_count * offset_squared
    return numerator, int(diff.size) * train_count**2


def compare_split_sides(anchor, current, anchor_visible, current_visible, *, x_range, y_range, depth):
    """Compare held-out ordered appearance on two sides; no physical role assignment.

    x_range/y_range are half-open ROI coordinates. The whole proposed rectangle
    including its excluded plateau must be visible in both rasters. Search all
    contained placements, keeping model ties unavailable rather than choosing the
    first one. A different upper/lower best placement is only differential image
    transport, which optical warps can also produce.
    """
    if (not isinstance(anchor, np.ndarray) or anchor.dtype != np.uint8 or anchor.ndim != 3
            or anchor.shape[2] != 3 or not anchor.size or anchor.size > MAX_PIXELS):
        raise ValueError('bounded nonempty uint8 BGR required')
    if not isinstance(current, np.ndarray) or current.shape != anchor.shape or current.dtype != np.uint8:
        raise ValueError('same-shape current BGR required')
    for mask in (anchor_visible, current_visible):
        if not isinstance(mask, np.ndarray) or mask.dtype != bool or mask.shape != anchor.shape[:2]:
            raise ValueError('same-shape boolean visibility required')
    if (len(x_range) != 2 or len(y_range) != 2 or type(depth) is not int or depth < 1
            or any(type(v) is not int for v in (*x_range, *y_range))):
        raise ValueError('integer half-open geometry required')
    x0, x1 = x_range; y0, y1 = y_range
    h, w = anchor.shape[:2]
    if not (0 <= x0 < x1 <= w and x1-x0 >= 3 and 0 <= y0 < y1 <= h):
        raise ValueError('valid plateau and at least three columns required')
    top, bottom = y0-depth, y1+depth
    ph, pw = bottom-top, x1-x0
    base = dict(spec_id=SPLIT_SIDE_SPEC['id'], status='UNAVAILABLE', reason=None,
                x_range=list(x_range), y_range=list(y_range), depth=depth,
                physical_identity='UNRESOLVED', selected_front=None, folds=[])
    if top < 0 or bottom > h:
        return dict(base, reason='anchor_outside_crop')
    if not anchor_visible[top:bottom, x0:x1].all():
        return dict(base, reason='anchor_masked')
    positions = (h-ph+1)*(w-pw+1)
    if (positions > SPLIT_SIDE_SPEC['max_offsets']
            or positions * depth * pw * 3 > SPLIT_SIDE_SPEC['max_compared_samples']):
        raise ValueError('two-side search resource bound exceeded')
    # The view allocates no raster copy; index only fully observed rectangles.
    valid = np.lib.stride_tricks.sliding_window_view(current_visible, (ph,pw)).all(axis=(-1,-2))
    yy, xx = np.nonzero(valid)
    if not len(yy):
        return dict(base, reason='no_visible_current_placement')
    view = np.lib.stride_tricks.sliding_window_view(current, (depth,pw), axis=(0,1))
    # Advanced indexing yields N,C,H,W; transpose to N,H,W,C.
    windows = [view[yy,xx].transpose(0,2,3,1),
               view[yy+ph-depth,xx].transpose(0,2,3,1)]
    templates = [anchor[top:y0,x0:x1], anchor[y1:bottom,x0:x1]]
    folds=[]
    for parity in (0,1):
        train=np.arange(pw)%2==parity; test=~train
        fit=[_side_costs(t,v,train) for t,v in zip(templates,windows,strict=True)]
        assert fit[0][2]==fit[1][2]
        minima=[np.flatnonzero(c==c.min()) for c in [fit[0][0],fit[1][0],fit[0][0]+fit[1][0]]]
        fold=dict(training_column_parity=parity, minimizer_counts=[len(m) for m in minima],
                  status='AMBIGUOUS_FIT', common_test_error=None, split_test_error=None,
                  matches=None)
        if all(len(m)==1 for m in minima):
            ui,li,ci=[int(m[0]) for m in minima]
            common=[];split=[]
            for k,si in enumerate((ui,li)):
                common.append(_test_side(templates[k],windows[k][ci],test,fit[k][1][ci],fit[k][2]))
                split.append(_test_side(templates[k],windows[k][si],test,fit[k][1][si],fit[k][2]))
            assert len({den for _,den in common+split})==1
            ce=sum(num for num,_ in common);se=sum(num for num,_ in split)
            denominator=2*common[0][1]*255**2
            fold.update(common_test_error=ce/denominator,split_test_error=se/denominator,
                        matches={name:[int(xx[i])-x0,int(yy[i])-top]
                                 for name,i in [('upper_shift',ui),('lower_shift',li),('common_shift',ci)]},
                        status=('SHARED_MATCH' if ui==li else 'SPLIT_BETTER' if se<ce else
                                'COMMON_BETTER' if ce<se else 'TIED_TEST'))
        folds.append(fold)
    states=[f['status'] for f in folds]
    result_state=(states[0] if states[0]==states[1] else 'FOLD_DISAGREEMENT')
    required = ('upper_shift','lower_shift') if result_state=='SPLIT_BETTER' else ('common_shift',)
    if (result_state in {'SPLIT_BETTER','COMMON_BETTER','SHARED_MATCH'}
            and any(folds[0]['matches'][k] != folds[1]['matches'][k] for k in required)):
        result_state='FOLD_MATCH_DISAGREEMENT'
    return dict(base,status='MEASURED',reason=None,visible_placements=len(yy),folds=folds,
                transport_pattern=result_state)


def match_ordered_patch(anchor, current, *, x_range, anchor_y, radius):
    """Keep all vertical alternatives for a recorded spatial patch, not an Oil track."""
    if (not isinstance(anchor, np.ndarray) or anchor.ndim != 3 or anchor.shape[2] != 3
            or anchor.dtype != np.uint8 or not anchor.size or anchor.size > MAX_PIXELS):
        raise ValueError('bounded nonempty uint8 BGR anchor required')
    if not isinstance(current, np.ndarray) or current.shape != anchor.shape or current.dtype != np.uint8:
        raise ValueError('current must be same-shape uint8 BGR')
    if (len(x_range) != 2 or any(type(x) is not int for x in x_range)
            or type(anchor_y) is not int or type(radius) is not int or radius < 1):
        raise ValueError('integer patch geometry required')
    h, w = anchor.shape[:2]
    x0, x1 = x_range
    if not 0 <= x0 < x1 <= w or not 0 <= anchor_y < h:
        raise ValueError('patch query outside raster')
    result = dict(status='unavailable_patch', physical_identity='UNRESOLVED',
                  decision='NOT_EVALUATED', anchor_y=anchor_y, x_range=list(x_range),
                  radius=radius, best_y=[], best_loss=None, runner_up_margin=None,
                  centers=[], losses=[], validity='raw_unmasked_appearance_only')
    if anchor_y-radius < 0 or anchor_y+radius >= h:
        return result
    centers = list(range(radius, h-radius))
    if len(centers)*(2*radius+1)*(x1-x0) > PATCH_SPEC['max_compared_pixels']:
        raise ValueError('patch comparison resource bound exceeded')
    a = anchor[anchor_y-radius:anchor_y+radius+1, x0:x1].astype(np.float64)
    a -= a.mean(axis=(0, 1), keepdims=True)
    losses = []
    for y in centers:
        b = current[y-radius:y+radius+1, x0:x1].astype(np.float64)
        b -= b.mean(axis=(0, 1), keepdims=True)
        losses.append(float(np.mean((a-b)**2)/255**2))
    minimum = min(losses)
    best = [y for y, loss in zip(centers, losses, strict=True)
            if abs(loss-minimum) <= PATCH_SPEC['tie_atol']]
    ordered = sorted(losses)
    return dict(result, status='measured', centers=centers, losses=losses,
                best_y=best, best_loss=minimum,
                runner_up_margin=ordered[1]-ordered[0] if len(ordered) > 1 else None)


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


CONSTELLATION_SPEC = {
    'id': 'fixed-reference-constellation-v1',
    'max_points': 128, 'max_samples': 4096,
    'max_compared_values': 25_000_000,
    'sampling': 'unique pixels in vertical radius stencils at supplied points',
    'search': 'every integer XY translation with complete visible sample support',
    'loss': 'exact mean-centered BGR squared error; one offset per channel for all samples',
    'geometry': 'one translation for the complete constellation; no deformation or gap fill',
    'authority': 'appearance hypotheses only; no physical role, track or scalar authority',
}


def match_reference_constellation(anchor, current, points, anchor_visible,
                                  current_visible, *, radius=2):
    """Compare a fixed approximate reference's spatial pattern jointly.

    Points are native integer XY hints, not exact boundary truth. Duplicate or
    overlapping stencils contribute each pixel once. All shifts and exact ties
    survive; this operation neither selects a physical front nor updates its
    reference. Holes in the stencil remain holes, not reconstructed context.
    """
    if (not isinstance(anchor, np.ndarray) or anchor.dtype != np.uint8
            or anchor.ndim != 3 or anchor.shape[2] != 3 or not anchor.size
            or anchor.shape[0] * anchor.shape[1] > MAX_PIXELS):
        raise ValueError('bounded nonempty uint8 BGR anchor required')
    if (not isinstance(current, np.ndarray) or current.dtype != np.uint8
            or current.shape != anchor.shape):
        raise ValueError('same-shape uint8 BGR current required')
    for v in (anchor_visible, current_visible):
        if not isinstance(v, np.ndarray) or v.dtype != np.bool_ or v.shape != anchor.shape[:2]:
            raise ValueError('same-shape boolean visibility required')
    if (not isinstance(points, np.ndarray) or points.ndim != 2 or points.shape[1] != 2
            or points.dtype.kind not in 'iu' or not 1 <= len(points) <= CONSTELLATION_SPEC['max_points']
            or type(radius) is not int or not 0 <= radius <= 16):
        raise ValueError('bounded nonempty integer XY points and radius required')
    h, w = anchor.shape[:2]
    if np.any(points < 0) or np.any(points[:, 0] >= w) or np.any(points[:, 1] >= h):
        raise ValueError('reference point outside crop')
    p = points.astype(np.int64)
    samples = np.unique((p[:, None, :] + np.array([(0, dy) for dy in range(-radius, radius+1)])).reshape(-1, 2), axis=0)
    if len(samples) > CONSTELLATION_SPEC['max_samples']:
        raise ValueError('reference sample budget exceeded')
    result = dict(spec_id=CONSTELLATION_SPEC['id'], status='UNAVAILABLE', reason=None,
                  sample_xy=samples.copy(), shifts_xy=np.empty((0, 2), np.int64),
                  cost_numerators=np.empty(0, np.int64), cost_denominator=None,
                  best_shifts_xy=np.empty((0, 2), np.int64),
                  physical_identity='UNRESOLVED', selected_front=None)
    if np.any(samples < 0) or np.any(samples[:, 0] >= w) or np.any(samples[:, 1] >= h):
        return dict(result, reason='reference_stencil_outside_crop')
    sx, sy = samples.T
    if not anchor_visible[sy, sx].all():
        return dict(result, reason='reference_stencil_masked')
    reference = anchor[sy, sx].astype(np.int64)
    if np.all(reference == reference[0]):
        return dict(result, reason='constant_reference')
    # One additive offset per channel; bounded samples keep exact moments int64-safe.
    n = len(samples)
    dxs = np.arange(-sx.min(), w-sx.max(), dtype=np.int64)
    dys = np.arange(-sy.min(), h-sy.max(), dtype=np.int64)
    if len(dxs) * len(dys) * n * 3 > CONSTELLATION_SPEC['max_compared_values']:
        raise ValueError('reference search budget exceeded')
    dx, dy = np.meshgrid(dxs, dys)
    shifts = np.column_stack((dx.ravel(), dy.ravel()))
    measured_shifts, costs = [], []
    for start in range(0, len(shifts), 128):
        batch = shifts[start:start+128]
        x, y = sx[None, :]+batch[:, 0, None], sy[None, :]+batch[:, 1, None]
        complete = current_visible[y, x].all(axis=1)
        if not complete.any():
            continue
        batch, x, y = batch[complete], x[complete], y[complete]
        diff = reference[None, :, :] - current[y, x].astype(np.int64)
        sums = diff.sum(axis=1)
        cost = n * np.square(diff).sum(axis=(1, 2)) - np.square(sums).sum(axis=1)
        measured_shifts.append(batch)
        costs.append(cost)
    if not costs:
        return dict(result, reason='no_visible_current_placement')
    shifts, costs = np.concatenate(measured_shifts), np.concatenate(costs)
    best = shifts[costs == costs.min()]
    return dict(result, status='MEASURED', reason=None, shifts_xy=shifts,
                cost_numerators=costs, cost_denominator=3*n*n*255**2,
                best_shifts_xy=best, minimizer_count=len(best))


CURRENT_BOUNDARY_SPEC = {
    'id': 'current-boundary-reference-comparison-v1',
    'geometry_basis': 'observed_canny_pixel_centers',
    'correspondence': 'same source X on each unjoined observed fragment',
    'side_offset': 2,
    'loss': 'exact BGR L1 sum; identical pairs for AB, BA, AA, BB and structure',
    'max_reference_points': 128,
    'max_fragments': 8192,
    'max_vertices': 250_000,
    'max_fragment_indices': 2_000_000,
    'max_pair_budget': 65_536,
    'physical_decision': 'NOT_EVALUATED',
}


def _current_boundary_reference(image, visible, points, origin):
    """Return frozen source-column pairs; never infer pure material labels."""
    if (not isinstance(points, np.ndarray) or points.ndim != 2 or points.shape[1] != 2
            or points.dtype.kind not in 'iu'
            or len(points) > CURRENT_BOUNDARY_SPEC['max_reference_points']):
        raise ValueError('bounded integer source reference points required')
    if not len(points):
        return {}, 'no_reference'
    points = np.unique(points, axis=0)
    if len(np.unique(points[:, 0])) != len(points):
        return {}, 'ambiguous_reference_column'
    h, w = visible.shape
    result = {}
    for sx, sy in points:
        x, y = int(sx)-origin[0], int(sy)-origin[1]
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError('reference point outside source crop')
        offset = CURRENT_BOUNDARY_SPEC['side_offset']
        seen = (offset <= y < h-offset
                and visible[y, x] and visible[y-offset, x] and visible[y+offset, x])
        result[int(sx)] = {
            'source_y': int(sy), 'available': bool(seen),
            'a': image[y-offset, x].astype(np.int32) if seen else None,
            'b': image[y+offset, x].astype(np.int32) if seen else None,
        }
    return result, None


def compare_current_boundary_reference(anchor, current, anchor_visible, current_visible,
                                       points, geometry, *, origin=(0, 0), center_x,
                                       structure_reference=None):
    """Measure declared side appearance on existing current edge fragments.

    ``geometry`` is the existing measure_edge_fragments result, in source pixels.
    ``points`` are approximate initial source XY hints, never scoring truth.
    Optional structure_reference is (image, visible, points) in the same crop.
    A provisional coordinate is diagnostic only; no physical/public value is set.
    """
    for im, mask in ((anchor, anchor_visible), (current, current_visible)):
        if (not isinstance(im, np.ndarray) or im.dtype != np.uint8 or im.ndim != 3
                or im.shape[2] != 3 or not im.size or im.shape[0]*im.shape[1] > MAX_PIXELS
                or not isinstance(mask, np.ndarray) or mask.dtype != np.bool_
                or mask.shape != im.shape[:2]):
            raise ValueError('bounded uint8 BGR and boolean visibility required')
    if anchor.shape != current.shape:
        raise ValueError('same-shape reference/current crops required')
    if (len(origin) != 2 or any(type(v) is not int or abs(v) > 2**50 for v in origin)
            or type(center_x) is not int):
        raise ValueError('bounded integer source origin and center required')
    h, w = current_visible.shape
    if not origin[0] <= center_x < origin[0]+w:
        raise ValueError('center outside crop')
    if (geometry.get('spec_id') != 'observed-edge-fragments-v1'
            or geometry.get('origin') != list(origin) or geometry.get('shape') != [h, w]):
        raise ValueError('current observed-edge geometry binding required')
    vertices, fragments = geometry['vertices_xy'], geometry['fragments']
    if (not isinstance(vertices, np.ndarray) or vertices.ndim != 2 or vertices.shape[1] != 2
            or vertices.dtype.kind not in 'iu' or not isinstance(fragments, list)):
        raise ValueError('integer vertices and fragment list required')
    base = dict(spec_id=CURRENT_BOUNDARY_SPEC['id'], status='UNAVAILABLE', reason=None,
                geometry_basis=CURRENT_BOUNDARY_SPEC['geometry_basis'], origin=list(origin),
                center_x=center_x, physical_decision='NOT_EVALUATED', selected_front=None,
                provisional_y=None, candidates=[])
    # Bound the input before allocating per-candidate support or numeric fields.
    if (len(vertices) > CURRENT_BOUNDARY_SPEC['max_vertices']
            or len(fragments) > CURRENT_BOUNDARY_SPEC['max_fragments']
            or sum(len(ids) for ids in fragments) > CURRENT_BOUNDARY_SPEC['max_fragment_indices']):
        return dict(base, reason='geometry_budget_exceeded')
    refs, reason = _current_boundary_reference(anchor, anchor_visible, points, origin)
    if reason:
        return dict(base, reason=reason)
    if not any(ref['available'] for ref in refs.values()):
        return dict(base, reason='no_visible_reference_pairs')
    if len(fragments)*len(refs) > CURRENT_BOUNDARY_SPEC['max_pair_budget']:
        return dict(base, reason='pair_budget_exceeded')
    local = vertices.astype(np.int64)-np.asarray(origin)
    if (np.any(local < 0) or np.any(local[:, 0] >= w) or np.any(local[:, 1] >= h)
            or not current_visible[local[:, 1], local[:, 0]].all()):
        raise ValueError('geometry contains unobserved/outside pixel')
    if len(vertices) != len(np.unique(vertices, axis=0)):
        raise ValueError('geometry vertices must be unique')
    structure, structure_reason = {}, 'not_supplied'
    if structure_reference is not None:
        sim, smask, spoints = structure_reference
        if (not isinstance(sim, np.ndarray) or sim.shape != anchor.shape or sim.dtype != np.uint8
                or not isinstance(smask, np.ndarray) or smask.shape != anchor_visible.shape
                or smask.dtype != np.bool_):
            raise ValueError('same-crop structure image and visibility required')
        structure, structure_reason = _current_boundary_reference(sim, smask, spoints, origin)
    result = dict(base, status='MEASURED', reason=None, reference_points=len(refs))
    winners = []
    offset = CURRENT_BOUNDARY_SPEC['side_offset']
    for candidate_id, raw_ids in enumerate(fragments):
        ids = np.asarray(raw_ids)
        if (ids.ndim != 1 or ids.dtype.kind not in 'iu' or not len(ids)
                or len(ids) > 2*len(vertices)+1 or np.any(ids >= len(vertices)) or np.any(ids < 0)):
            raise ValueError('bounded observed fragment vertex IDs required')
        # Cycle closure repeats its first vertex; each observed pixel counts once.
        xy = vertices[np.unique(ids)]
        center = sorted(int(y) for x, y in xy if x == center_x)
        common = sorted(set(int(x) for x in xy[:, 0]) & refs.keys())
        row = dict(candidate_id=candidate_id, center_crossings=center, requested_columns=common,
                   samples=[], missing=[], losses=None, denominator=None,
                   structure_loss=None, structure_status='NOT_MEASURED',
                   structure_reason=structure_reason, appearance='UNAVAILABLE', reason=None)
        result['candidates'].append(row)
        if any(np.count_nonzero(xy[:, 0] == x) != 1 for x in common):
            row['reason'] = 'ambiguous_current_column'
            continue
        costs = dict(AB=0, BA=0, AA=0, BB=0)
        struct_cost, struct_complete = 0, bool(structure)
        for sx in common:
            sy = int(xy[xy[:, 0] == sx, 1][0]); x, y = sx-origin[0], sy-origin[1]
            ref = refs[sx]
            if not ref['available']:
                row['missing'].append(dict(source_x=sx, reason='reference_side_unavailable'))
                continue
            if not (offset <= y < h-offset and current_visible[y-offset, x] and current_visible[y+offset, x]):
                row['missing'].append(dict(source_x=sx, reason='current_side_unavailable'))
                continue
            a, b = current[y-offset, x].astype(np.int32), current[y+offset, x].astype(np.int32)
            ra, rb = ref['a'], ref['b']
            for key, (u, v) in {'AB': (ra, rb), 'BA': (rb, ra), 'AA': (ra, ra), 'BB': (rb, rb)}.items():
                costs[key] += int(np.abs(a-u).sum()+np.abs(b-v).sum())
            row['samples'].append(dict(current_xy=[sx, sy], reference_xy=[sx, ref['source_y']],
                                       current_a=a.tolist(), current_b=b.tolist(),
                                       reference_a=ra.tolist(), reference_b=rb.tolist()))
            sr = structure.get(sx)
            if sr is None or not sr['available']:
                struct_complete = False
            else:
                struct_cost += int(np.abs(a-sr['a']).sum()+np.abs(b-sr['b']).sum())
        n = len(row['samples'])
        if not n:
            row['reason'] = 'no_common_visible_pairs'
            continue
        row.update(losses=costs, denominator=6*n, appearance='UNRESOLVED')
        if struct_complete:
            row.update(structure_status='MEASURED', structure_reason=None, structure_loss=struct_cost)
        elif structure_reference is not None:
            row['structure_reason'] = structure_reason or 'incomplete_common_support'
        if not all(costs['AB'] < costs[k] for k in ('BA', 'AA', 'BB')):
            row['reason'] = 'ordered_sides_not_strictly_preferred'
        elif struct_complete and struct_cost <= costs['AB']:
            row.update(appearance='CONTRADICTED', reason='structure_not_worse')
        else:
            row.update(appearance='PROVISIONAL_AB', reason=None)
            if len(center) == 1:
                winners.append(row)
    preferred = [r for r in result['candidates'] if r['appearance'] == 'PROVISIONAL_AB' and r['center_crossings']]
    if len(preferred) == 1 and len(winners) == 1:
        result.update(reason='unique_provisional_center', provisional_y=winners[0]['center_crossings'][0])
    elif preferred:
        result['reason'] = 'ambiguous_provisional_center'
    else:
        result['reason'] = 'no_provisional_center'
    return result
