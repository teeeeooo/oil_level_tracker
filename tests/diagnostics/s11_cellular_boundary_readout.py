"""Cellular partition and co-located current edge, experimental ranking only."""
from __future__ import annotations
import cv2
import numpy as np
from tests.diagnostics import s11_cellular_basin_readout as base
from tests.diagnostics.s11_cellular_partition_readout import extent_support

SPEC = dict(base.SPEC, id='cellular-partition-colocated-boundary-v1',
    score='median rank-biserial * extent support * colocated mean abs gy / frame gradient RMS',
    edge_band=[-1,0,1], minimum_edge_samples=16, zero_gradient_rms=1e-6)
select_candidate = base.select_candidate

def cellular_map(image, valid):
    energy, usable = base.cellular_map(image, valid)
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY).astype(np.float64)
    blurred,_ = base._weighted_blur(gray, valid, 1.0)
    gx = cv2.Sobel(blurred,cv2.CV_64F,1,0,ksize=3,scale=.125)
    gy = cv2.Sobel(blurred,cv2.CV_64F,0,1,ksize=3,scale=.125)
    rms = float(np.sqrt(np.mean((gx*gx+gy*gy)[usable]))) if usable.any() else 0.0
    relative_gy = gy/rms if rms>SPEC['zero_gradient_rms'] else np.zeros_like(gy)
    edge_valid=cv2.erode(valid.astype(np.uint8),np.ones((3,3),np.uint8),
                         borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
    return np.stack([energy,relative_gy,edge_valid.astype(float)],axis=-1), usable

def measure_sector(features, valid, *, x_range, current_y):
    if features.ndim!=3 or features.shape[2]!=3:
        raise ValueError('expected cellular and vertical-gradient feature planes')
    result = base.measure_sector(features[:,:,0],valid,x_range=x_range,current_y=current_y)
    h,w = valid.shape; x0,x1 = x_range; values=[]
    for offset in SPEC['edge_band']:
        y=float(current_y)+offset; first=int(np.floor(y)); last=first+1
        if first<0 or last>=h: continue
        supported=(valid[first,x0:x1] & valid[last,x0:x1]
                   & (features[first,x0:x1,2]>0) & (features[last,x0:x1,2]>0))
        if supported.any():
            fraction=y-first
            row=(1-fraction)*features[first,x0:x1,1]+fraction*features[last,x0:x1,1]
            values.extend(np.abs(row[supported]).tolist())
    result['edge_samples']=len(values)
    result['relative_edge']=float(np.mean(values)) if len(values)>=16 else None
    if result['relative_edge'] is None:
        result.update(status='UNAVAILABLE',score=None,reason='insufficient_colocated_edge_support')
    return result

def score_candidate(views):
    if len({v['sector'] for v in views})!=len(views):
        raise ValueError('duplicate recorded sector')
    scores=[v['measurement']['score']*extent_support(v['measurement']['counts'])
            *v['measurement']['relative_edge'] for v in views
            if v['measurement']['status']=='AVAILABLE']
    return float(np.median(scores)) if len(scores)>=3 else None
