"""Offline Foam boundary alternatives on saved pixels, without material inference.

A component top anchors two fixed inspection windows. Every fully bracketed,
positive vertical-gradient local maximum is retained (including plateau extent).
Nothing selects a maximum or promotes the component minimum into a Foam scalar.
"""
from __future__ import annotations

import numpy as np

from oil_tracker.adapters.vision import oil_interface_witness
from tests.diagnostics.s11_foam_support_geometry import MAX_PIXELS

RADII = (4, 8)  # Inspection extents in saved pixels, not tuned acceptance widths.


def _peaks(values, valid, start, stop, origin_y):
    """Maximal exact-value runs; require valid, strictly lower neighbours.

    A plateau touching a window or validity boundary is censored, not a peak.
    No tolerance, amplitude cutoff, smoothing or bridge across invalid pixels.
    """
    peaks = []
    y = start
    while y < stop:
        end = y + 1
        while end < stop and valid[y] and valid[end] and values[end] == values[y]:
            end += 1
        if (valid[y:end].all() and values[y] > 0 and y > start and end < stop
                and valid[y - 1] and valid[end]
                and values[y - 1] < values[y] and values[end] < values[y]):
            peaks.append({'source_y_range': [y + origin_y, end + origin_y],
                          'vertical_magnitude': float(values[y]) / 510.0})
        y = end
    return peaks


def measure(gray, labels, effective, glare, *, origin=(0, 0)):
    """Return all retained components/columns with separate geometry and appearance.

    effective/glare are boolean. Noisy maxima are deliberately retained; one
    maximum is not unique physical identity, and no peak is not absence of Foam.
    Invalid gradient samples are JSON null, never the owner's storage zero.
    """
    if (not isinstance(gray, np.ndarray) or gray.ndim != 2 or gray.dtype != np.uint8
            or not gray.size or gray.size > MAX_PIXELS):
        raise ValueError('bounded nonempty raw uint8 gray required')
    for name, array, dtype in [('labels', labels, np.uint16),
                                ('effective', effective, np.bool_), ('glare', glare, np.bool_)]:
        if not isinstance(array, np.ndarray) or array.shape != gray.shape or array.dtype != dtype:
            raise ValueError(f'{name}: incorrect shape/type')
    if len(origin) != 2 or any(type(v) is not int for v in origin):
        raise ValueError('integer source origin required')
    if np.any((labels > 0) & ~effective):
        raise ValueError('support outside effective mask')
    ids = np.unique(labels[labels > 0])
    if len(ids) > 256:
        raise ValueError('retained component bound exceeded')
    visible = effective & ~glare
    channels = oil_interface_witness._extra_channels(gray, visible, effective, np.zeros_like(gray))
    gradient, valid = channels['normal'], channels['gradient_count']
    # Byte central-difference numerators give exact plateau equality. Recover
    # them from the existing operator; do not add a floating-point tolerance.
    peak_values = np.rint(gradient * 510).astype(np.uint16)
    ox, oy = origin
    h, _ = gray.shape
    components = []
    for component_id in ids:
        support = labels == component_id
        columns = []
        for x in np.flatnonzero(support.any(axis=0)):
            ys = np.flatnonzero(support[:, x])
            top = int(ys[0])
            views = []
            for radius in RADII:
                start, stop = max(0, top-radius), min(h, top+radius+1)
                peaks = _peaks(peak_values[:, x], valid[:, x], start, stop, oy)
                fully_observed = top-radius >= 0 and top+radius < h and bool(valid[start:stop, x].all())
                views.append({
                    'radius_px': radius, 'source_y_range': [start+oy, stop+oy],
                    'fully_observed': fully_observed,
                    'valid_count': int(valid[start:stop, x].sum()),
                    'sample_count': stop-start,
                    'vertical_samples': [float(gradient[y, x]) if valid[y, x] else None
                                         for y in range(start, stop)],
                    'peaks': peaks,
                    'appearance_state': ('censored' if not fully_observed else
                                         'no_bracketed_peak' if not peaks else
                                         'single_peak' if len(peaks) == 1 else 'multiple_peaks'),
                })
            columns.append({'source_x': int(x)+ox, 'support_top_source_y': top+oy,
                            'support_bottom_source_y': int(ys[-1])+oy, 'views': views})
        components.append({'component_id': int(component_id), 'pixel_count': int(support.sum()),
                           'physical_identity': 'UNRESOLVED', 'foam_front': None,
                           'columns': columns})
    return {'schema_version': 's11-foam-front-alternatives-v1', 'decision': 'NOT_EVALUATED',
            'field_disposition': 'FIELD FAIL', 'origin': list(origin), 'shape': list(gray.shape),
            'radii_px': list(RADII), 'components': components,
            'limits': 'Local maxima include texture/noise/reflection. Single peak does not establish '
                      'Foam identity. Censored/no peak does not establish absence. Windows are '
                      'support-conditioned; missing support cannot be recovered. No interpolation, '
                      'ranking, accepted contour, scalar or independent validation.'}
