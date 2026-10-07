"""Offline texture-arrangement hypothesis. Never physical identity authority."""
from __future__ import annotations

import math
import cv2
import numpy as np

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
