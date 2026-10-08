"""Frozen offline cellular-basin ranking. No production consumers or truth input."""
from __future__ import annotations
import math
import cv2
import numpy as np

SPEC = {
    "id": "cellular-basin-structure-tensor-v1", "max_dimension": 1024,
    "blur_sigma": 1.0, "tensor_sigma": "max(1,min(H,W)/40)",
    "minimum_pool_weight": 0.5, "boundary_gap": 2,
    "minimum_side_pixels": 16, "minimum_side_rows": 4,
    "score": "median signed upper>lower rank-biserial over >=3 recorded sectors",
    "selection": "unique positive maximum; absolute tie tolerance 1e-12",
    "physical_identity_sufficient": False, "fit_partitions": [],
}

def _weighted_blur(values, valid, sigma):
    weight = cv2.GaussianBlur(valid.astype(np.float64), (0, 0), sigma,
                              borderType=cv2.BORDER_CONSTANT)
    total = cv2.GaussianBlur(np.where(valid, values, 0.0), (0, 0), sigma,
                             borderType=cv2.BORDER_CONSTANT)
    return np.divide(total, weight, out=np.zeros_like(total), where=weight > 0), weight

def cellular_map(image: np.ndarray, valid: np.ndarray):
    if (image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3
            or not 8 <= min(image.shape[:2]) <= max(image.shape[:2]) <= 1024
            or valid.dtype != np.bool_ or valid.shape != image.shape[:2]):
        raise ValueError("bounded uint8 BGR image and matching boolean mask required")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float64)
    blurred, _ = _weighted_blur(gray, valid, SPEC['blur_sigma'])
    gradient_valid = cv2.erode(valid.astype(np.uint8), np.ones((3, 3), np.uint8),
                               borderType=cv2.BORDER_CONSTANT, borderValue=0) > 0
    gx = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3, scale=0.125)
    gy = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3, scale=0.125)
    sigma = max(1.0, min(valid.shape) / 40.0)
    a, weight = _weighted_blur(gx*gx, gradient_valid, sigma)
    b, _ = _weighted_blur(gy*gy, gradient_valid, sigma)
    c, _ = _weighted_blur(gx*gy, gradient_valid, sigma)
    smaller = np.maximum(0.0, (a+b-np.sqrt((a-b)**2+4*c*c))/2)
    usable = valid & (weight >= SPEC['minimum_pool_weight'])
    return np.sqrt(smaller), usable

def rank_biserial(upper, lower):
    upper, lower = np.asarray(upper), np.sort(np.asarray(lower))
    if not upper.size or not lower.size:
        raise ValueError("both distributions must be nonempty")
    left = np.searchsorted(lower, upper, side='left')
    right = np.searchsorted(lower, upper, side='right')
    return float(np.mean((left+right)/2)/lower.size*2-1)

def measure_sector(energy, valid, *, x_range, current_y):
    h, w = valid.shape
    if (energy.shape != valid.shape or valid.dtype != np.bool_
            or not np.isfinite(energy).all() or len(x_range) != 2
            or any(type(x) is not int for x in x_range)
            or not 0 <= x_range[0] < x_range[1] <= w):
        raise ValueError("invalid measurement raster or sector extent")
    if (isinstance(current_y, (bool, np.bool_)) or not isinstance(current_y,
            (int, float, np.integer, np.floating)) or not math.isfinite(current_y)
            or not 0 <= current_y < h):
        raise ValueError("finite in-raster candidate Y required")
    x0, x1 = x_range
    d = np.arange(h)[:, None] - current_y
    v = valid[:, x0:x1]
    upper = v & (d < -SPEC['boundary_gap'])
    lower = v & (d > SPEC['boundary_gap'])
    counts = [int(m.sum()) for m in (upper, lower)]
    rows = [int(np.any(m, axis=1).sum()) for m in (upper, lower)]
    result = dict(status='UNAVAILABLE', score=None, counts=counts, rows=rows,
                  x_range=list(x_range), current_y=float(current_y))
    if min(counts) < SPEC['minimum_side_pixels'] or min(rows) < SPEC['minimum_side_rows']:
        return dict(result, reason='insufficient_two_sided_region_support')
    a, b = energy[:, x0:x1][upper], energy[:, x0:x1][lower]
    return dict(result, status='AVAILABLE', reason='measured_not_identity',
                score=rank_biserial(a, b), medians=[float(np.median(a)), float(np.median(b))])

def score_candidate(views):
    if len({v['sector'] for v in views}) != len(views):
        raise ValueError("duplicate recorded sector")
    scores = [v['measurement']['score'] for v in views
              if v['measurement']['status'] == 'AVAILABLE']
    return float(np.median(scores)) if len(scores) >= 3 else None

def select_candidate(rows):
    available = [r for r in rows if r['score'] is not None]
    if not available:
        return []
    best = max(r['score'] for r in available)
    if best <= 0:
        return []
    return [r['candidate_input_index'] for r in available
            if abs(r['score']-best) <= 1e-12]
