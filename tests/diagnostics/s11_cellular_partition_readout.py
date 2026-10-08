"""Extent-supported revision; original cellular-basin experiment stays immutable."""
from __future__ import annotations
import math
import numpy as np
from tests.diagnostics.s11_cellular_basin_readout import (
    SPEC as BASE_SPEC, cellular_map, measure_sector, select_candidate,
)

SPEC = dict(BASE_SPEC, id='extent-supported-cellular-partition-v1',
            score='median rank-biserial * 2*sqrt(p*(1-p)); >=3 recorded sectors')

def extent_support(counts):
    if len(counts) != 2 or any(type(n) is not int or n < 0 for n in counts) or not sum(counts):
        raise ValueError('nonnegative side counts with positive total required')
    p = counts[0] / sum(counts)
    return 2 * math.sqrt(p*(1-p))

def score_candidate(views):
    if len({v['sector'] for v in views}) != len(views):
        raise ValueError('duplicate recorded sector')
    scores = [v['measurement']['score'] * extent_support(v['measurement']['counts'])
              for v in views if v['measurement']['status'] == 'AVAILABLE']
    return float(np.median(scores)) if len(scores) >= 3 else None
