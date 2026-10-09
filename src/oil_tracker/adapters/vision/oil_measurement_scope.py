"""Explicit sampling withdrawal for Oil proposal measurements, never pixel truth.

The immutable input is separate from recipe exclusion and artifact matching.
Original processed rasters and all nonmeasurement context remain unchanged.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import re

import numpy as np

from oil_tracker.domain.artifact_reference import fingerprint, geometry_fingerprint
from oil_tracker.domain.geometry import Rect

VERSION = "oil-local-xy-v1"
MAX_RECTS = 16
MAX_SCOPES = 32
MAX_ROI_PIXELS = 1_048_576
MAX_ROI_AXIS = 2048
MAX_TRACE_BYTES = 1_048_576


@dataclass(frozen=True)
class OilMeasurementScope:
    glass_id: str
    geometry_sha256: str
    settings_sha256: str
    frame_size: tuple[int, int]
    reference_sha256: str
    rectangles: tuple[Rect, ...]

    def __post_init__(self):
        if not isinstance(self.glass_id, str) or not self.glass_id:
            raise ValueError("Scope requires a Glass identity.")
        for digest in (self.geometry_sha256, self.settings_sha256, self.reference_sha256):
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValueError("Scope requires lowercase SHA-256 bindings.")
        if (type(self.frame_size) is not tuple or len(self.frame_size) != 2
                or any(type(v) is not int or v <= 0 for v in self.frame_size)):
            raise ValueError("Scope frame size must be two positive integers.")
        if type(self.rectangles) is not tuple or len(self.rectangles) > MAX_RECTS:
            raise ValueError("Scope must contain at most 16 immutable rectangles.")
        for rect in self.rectangles:
            if not isinstance(rect, Rect) or any(
                type(v) not in (int, float) or not -(2**31) <= v < 2**31 or not math.isfinite(v) or int(v) != v
                for v in (rect.x, rect.y, rect.width, rect.height)
            ) or rect.width <= 0 or rect.height <= 0:
                raise ValueError("Scope rectangles must have integral bounds and positive area.")

    @classmethod
    def bind(cls, glass, *, frame_size, reference_sha256, rectangles):
        return cls(glass.id, geometry_fingerprint(glass), fingerprint(asdict(glass.detector_settings)),
                   tuple(frame_size), reference_sha256, tuple(rectangles))

    @property
    def manifest(self):
        return {"version": VERSION, **asdict(self)}

    @property
    def sha256(self):
        return fingerprint(self.manifest)

    def validate(self, glass, frame):
        if (glass.id != self.glass_id or geometry_fingerprint(glass) != self.geometry_sha256
                or fingerprint(asdict(glass.detector_settings)) != self.settings_sha256
                or (frame.shape[1], frame.shape[0]) != self.frame_size):
            raise ValueError("Oil measurement scope binding mismatch.")
        roi = glass.geometry.crop_roi
        h, w = frame.shape[:2]
        cw = max(0, min(w, math.ceil(roi.right)) - max(0, math.floor(roi.x)))
        ch = max(0, min(h, math.ceil(roi.bottom)) - max(0, math.floor(roi.y)))
        if cw * ch > MAX_ROI_PIXELS or max(cw, ch) > MAX_ROI_AXIS:
            raise ValueError("Oil measurement scope ROI resource bound exceeded.")
        # The same new reference cannot also reject whole candidates.
        for template in glass.geometry.artifact_templates:
            reference = getattr(template, "support_reference", None)
            if reference is not None and reference.snapshot_sha256 == self.reference_sha256:
                raise ValueError("Oil scope reference is already used by an artifact veto.")

    def rasterize(self, shape, crop_origin):
        h, w = shape
        if h * w > MAX_ROI_PIXELS or max(h, w) > MAX_ROI_AXIS:
            raise ValueError("Oil measurement scope ROI resource bound exceeded.")
        ox, oy = crop_origin
        excluded = np.zeros(shape, dtype=bool)
        for rect in self.rectangles:
            x0, x1 = max(0, int(rect.x)-ox), min(w, int(rect.right)-ox)
            y0, y1 = max(0, int(rect.y)-oy), min(h, int(rect.bottom)-oy)
            if x0 < x1 and y0 < y1:
                excluded[y0:y1, x0:x1] = True
        excluded.flags.writeable = False
        return excluded


def active_exclusion(excluded, visible):
    """Return None for an exact legacy path; never modify caller arrays."""
    if excluded is None:
        return None
    if excluded.shape != visible.shape or excluded.dtype != np.bool_:
        raise ValueError("Oil sampling exclusion must be a matching boolean raster.")
    return excluded if np.any(excluded & visible) else None


def band_selection(upper_visible, lower_visible, upper_excluded, lower_excluded, *, minimum):
    """Choose actual samples; untouched operations retain independent pooling."""
    affected = bool(np.any(upper_visible & upper_excluded) or np.any(lower_visible & lower_excluded))
    if not affected:
        uv, lv = upper_visible, lower_visible
        reason = "legacy_pool"
    else:
        uv, lv = upper_visible & ~upper_excluded, lower_visible & ~lower_excluded
        common = np.all(uv, axis=0) & np.all(lv, axis=0)
        if not uv.shape[0] or not lv.shape[0]:
            common[:] = False
        uv = np.broadcast_to(common, uv.shape)
        lv = np.broadcast_to(common, lv.shape)
        reason = "complete_common_x"
    available = np.count_nonzero(uv) >= minimum and np.count_nonzero(lv) >= minimum
    return uv, lv, affected, reason if available else "insufficient_common_support" if affected else "insufficient_visible_pixels"


def band_record(visible, excluded, *, row, radius, start, stop, crop_origin, minimum, legacy_zero_weight=False):
    """Bounded trace of the same selection primitive used by both generators."""
    h = visible.shape[0]
    upper = (slice(max(0, row-radius), row), slice(start, stop))
    lower = (slice(row+1, min(h, row+radius+1)), slice(start, stop))
    ov, lv = visible[upper], visible[lower]
    ue, le = excluded[upper], excluded[lower]
    u, l, affected, reason = band_selection(ov, lv, ue, le, minimum=minimum)
    if legacy_zero_weight and not affected:
        # Native prefix pooling has no per-side area floor; a zero-weight band
        # has legacy value zero. Do not claim the new guard ran on this window.
        reason = "legacy_pool"
    available = reason in ("legacy_pool", "complete_common_x")
    ox, oy = crop_origin
    windows = []
    ranges = ((max(0, row-radius)+oy, row+oy), (row+1+oy, min(h, row+radius+1)+oy))
    if available:
        if affected:
            from .oil_supplemental_path import _column_runs
            runs = _column_runs(np.all(u, axis=0) & np.all(l, axis=0), start+ox)
        else:
            runs = ((start+ox, stop+ox),)
        windows = [[x0, y0, x1, y1] for y0, y1 in ranges for x0, x1 in runs if y1 > y0]
    return {"radius": radius, "source_x_range": [start+ox, stop+ox],
            "affected": affected, "rule": "complete_common_x" if affected else "legacy_pool",
            "available": available, "reason": reason,
            "minimum_per_side": 0 if legacy_zero_weight and not affected else minimum,
            "legacy_zero_weight_value": 0.0 if legacy_zero_weight and not affected else None,
            "original_counts": [int(ov.sum()), int(lv.sum())],
            "excluded_counts": [int((ov & ue).sum()), int((lv & le).sum())],
            "remaining_counts": [int((ov & ~ue).sum()), int((lv & ~le).sum())],
            "used_counts": [int(u.sum()), int(l.sum())] if available else [0, 0],
            "original_capacity": [int(ov.size), int(lv.size)], "used_windows": windows}
