"""Offline texture-arrangement hypothesis. Never physical identity authority."""
from __future__ import annotations

import math
import cv2
import numpy as np


SPATIAL_CONJUNCTION_SPEC = {
    'id': 'signed-spatial-conjunction-v1',
    'radius': 2,
    'max_pixels': 4_194_304,
    'max_dimension': 4096,
    'minimum_side_centers': 16,
    'maximum_cost': 0.125,
    'minimum_margin': 0.05,
    'physical_decision': 'UNRESOLVED',
}


def measure_spatial_conjunction(gray, edges, visible, *, column):
    """Measure every observed center-column edge with one same-support ablation.

    Four signed derivative pairs must share an actual center and polarity.
    This is appearance only: printed cells can produce the identical result.
    No truth, source identity, selected scalar, fitted model or mutable input.
    """
    spec = SPATIAL_CONJUNCTION_SPEC
    if (not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.dtype != np.uint8
            or not gray.size or gray.size > spec['max_pixels']
            or max(gray.shape) > spec['max_dimension']):
        raise ValueError('bounded nonempty uint8 grayscale required')
    for value in (edges, visible):
        if not isinstance(value, np.ndarray) or value.dtype != bool or value.shape != gray.shape:
            raise ValueError('same-shape boolean edge and visibility rasters required')
    h, w = gray.shape
    if type(column) is not int or not 0 <= column < w:
        raise ValueError('an observed integer column is required')
    b = min(32, max(4, round(min(h, w) * 0.06)))
    # The largest actual sample offset is three. No border reflection/padding.
    shape = (max(0, h-6), max(0, w-6))
    valid = np.ones(shape, bool)
    derivatives = []
    pairs = (((0, 3), (0, 1)), ((0, -3), (0, -1)),
             ((3, 0), (1, 0)), ((-3, 0), (-1, 0)))
    for (ay, ax), (by, bx) in pairs:
        a = gray[3+ay:h-3+ay, 3+ax:w-3+ax]
        z = gray[3+by:h-3+by, 3+bx:w-3+bx]
        if h < 7 or w < 7:
            a = z = np.empty(shape, np.uint8)
        derivatives.append(a.astype(np.int16) - z.astype(np.int16))
        if h >= 7 and w >= 7:
            valid &= (visible[3+ay:h-3+ay, 3+ax:w-3+ax]
                      & visible[3+by:h-3+by, 3+bx:w-3+bx])
    e, west, south, north = derivatives
    joint = np.maximum(0, np.maximum(np.minimum.reduce(derivatives),
                                    -np.maximum.reduce(derivatives)))
    x = np.maximum(0, np.maximum(np.minimum(e, west), -np.maximum(e, west)))
    y = np.maximum(0, np.maximum(np.minimum(south, north), -np.maximum(south, north)))
    power = np.maximum(x, y)
    # Factor two avoids fractional integer arithmetic in the ablation.
    ablated_twice = x.astype(np.int32) + y

    def side(y0, y1):
        x0, x1 = column-b, column+b+1
        a, z = max(3, y0), min(h-3, y1)
        c, d = max(3, x0), min(w-3, x1)
        expected = (y1-y0)*(x1-x0)
        if a >= z or c >= d:
            return dict(available_centers=0, requested_centers=expected, status='UNAVAILABLE')
        sl = np.s_[a-3:z-3, c-3:d-3]
        mask = valid[sl]
        count = int(mask.sum())
        result = dict(available_centers=count, requested_centers=expected,
                      clipped_or_masked_centers=expected-count,
                      bounds_xyxy=[x0, y0, x1, y1])
        if count < spec['minimum_side_centers']:
            return dict(result, status='UNAVAILABLE')
        p = int(power[sl][mask].sum())
        r = int(joint[sl][mask].sum())
        r0_twice = int(ablated_twice[sl][mask].sum())
        return dict(result, status='AVAILABLE', axis_sum=p, joint_sum=r,
                    ablated_sum_twice=r0_twice,
                    joint_ratio=r/p if p else 0.0,
                    ablated_ratio=r0_twice/(2*p) if p else 0.0)

    def compare(upper, lower, variant):
        if upper['status'] != 'AVAILABLE' or lower['status'] != 'AVAILABLE':
            return dict(preference='UNAVAILABLE', costs=None, margin=None)
        u, v = upper[f'{variant}_ratio'], lower[f'{variant}_ratio']
        costs = {'upper_cellular': (u*u+(1-v)**2)/2,
                 'internal_cellular': ((1-u)**2+(1-v)**2)/2,
                 'noncellular': (u*u+v*v)/2}
        ordered = sorted(costs, key=costs.get)
        margin = costs[ordered[1]]-costs[ordered[0]]
        preference = (ordered[0] if costs[ordered[0]] <= spec['maximum_cost']
                      and margin >= spec['minimum_margin'] else 'AMBIGUOUS')
        return dict(preference=preference, costs=costs, margin=margin)

    rows = []
    for row in np.flatnonzero(edges[:, column] & visible[:, column]):
        row = int(row)
        upper = side(row-2-b, row-2)
        lower = side(row+3, row+3+b)
        rows.append(dict(row=row, column=column, upper=upper, lower=lower,
                         joint=compare(upper, lower, 'joint'),
                         ablated=compare(upper, lower, 'ablated'),
                         physical_role='UNRESOLVED', scalar_eligible=False))
    return dict(spec_id=spec['id'], shape=[h, w], band_width=b, column=column,
                rows=rows, physical_decision='UNRESOLVED', selected_scalar=None)

SPEC = {
    "id": "side-texture-persistence-lbp-v1",
    "radii": [1, 2], "neighbors": 8, "histogram_bins_per_radius": 10,
    "sampling": "circular bilinear OpenCV remap; neighbor >= center; uniform rotation-invariant LBP",
    "mask": "effective AND nonglare eroded by a 5x5 all-ones kernel",
    "band_thickness": "min(32,max(4,round(min(H,W)*0.06)))", "boundary_gap_px": 2,
    "minimum_band_pixels": 16,
    "sector_margin": "min cross-side JS distance minus max within-side near/far JS distance",
    "operating_point": "At least three complete recorded sectors with margin > 0; else unresolved.",
    "fit_partitions": [], "evaluation_regime": "EXPLORATORY_UNCALIBRATED",
    "physical_identity_sufficient": False,
    "collision": "Static textured optical half-planes can produce identical support; no promotion from this cue alone.",
}


def texture_maps(image: np.ndarray, valid: np.ndarray):
    if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError("Expected uint8 BGR input.")
    if valid.shape != image.shape[:2] or max(image.shape[:2]) > 1024:
        raise ValueError("Mask or bounded image shape invalid.")
    gray = cv2.cvtColor(image.astype(np.float32), cv2.COLOR_BGR2GRAY)
    yy, xx = np.mgrid[:gray.shape[0], :gray.shape[1]].astype(np.float32)
    maps = []
    for radius in SPEC["radii"]:
        bits = []
        for k in range(8):
            angle = k * math.pi / 4
            neighbor = cv2.remap(gray, xx + radius*math.cos(angle), yy + radius*math.sin(angle),
                                 interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            bits.append(neighbor >= gray)
        bits = np.stack(bits, axis=0)
        transitions = np.sum(bits != np.roll(bits, 1, axis=0), axis=0)
        maps.append(np.where(transitions <= 2, bits.sum(axis=0), 9).astype(np.uint8))
    usable = cv2.erode(valid.astype(np.uint8), np.ones((5, 5), np.uint8),
                       borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
    return maps, usable


def js_distance(a, b):
    middle = (a+b)/2
    def kl(p):
        selected = p > 0
        return float(np.sum(p[selected] * np.log(p[selected]/middle[selected])))
    return math.sqrt(max(0.0, (kl(a)+kl(b))/2))


def measure_sector(maps, valid, *, x_range, current_y):
    h, w = valid.shape
    x0, x1 = x_range
    if not (isinstance(x0, int) and isinstance(x1, int) and 0 <= x0 < x1 <= w):
        return {"status": "UNAVAILABLE", "reason": "invalid_sector_extent"}
    if not math.isfinite(current_y) or not 0 <= current_y < h:
        return {"status": "UNAVAILABLE", "reason": "invalid_candidate_y"}
    band = min(32, max(4, round(min(h, w)*.06)))
    d = np.arange(h)[:, None] - current_y
    xmask = np.zeros((h, w), dtype=bool); xmask[:, x0:x1] = True
    selections = {
        "upper_near": (d >= -2-band) & (d < -2),
        "upper_far": (d >= -2-2*band) & (d < -2-band),
        "lower_near": (d > 2) & (d <= 2+band),
        "lower_far": (d > 2+band) & (d <= 2+2*band),
    }
    histograms, counts = {}, {}
    for name, rows in selections.items():
        selected = rows & xmask & valid
        counts[name] = int(selected.sum())
        if counts[name] < SPEC["minimum_band_pixels"]:
            continue
        histograms[name] = np.concatenate([
            np.bincount(m[selected], minlength=10).astype(float) / counts[name] / len(maps)
            for m in maps
        ])
    payload = {"status": "UNAVAILABLE", "reason": "insufficient_band_support", "counts": counts,
               "band_thickness": band, "x_range": list(x_range), "current_y": float(current_y)}
    if len(histograms) != 4:
        return payload
    un, uf, ln, lf = (histograms[name] for name in selections)
    cross = [js_distance(a, b) for a in (un, uf) for b in (ln, lf)]
    within = [js_distance(un, uf), js_distance(ln, lf)]
    margin = min(cross)-max(within)
    payload.update(status="AVAILABLE", reason="persistent_side_texture" if margin > 0 else "texture_opposition",
                   cross_side=cross, within_side=within, margin=margin,
                   histograms={key: value.tolist() for key, value in histograms.items()})
    return payload


def decide_candidate(views):
    sectors = {view["sector"] for view in views if view["measurement"]["status"] == "AVAILABLE"
               and view["measurement"]["margin"] > 0}
    if len(sectors) >= 3:
        return "INTERFACE_SUPPORTED", "three_sectors_persistent_texture_change_not_identity_proof"
    return "UNRESOLVED", "insufficient_texture_separation"
