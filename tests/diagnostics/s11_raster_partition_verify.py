"""Direct-loop arithmetic oracle for a CRW-1 readout; no extractor imports."""
from __future__ import annotations
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import cv2
import numpy as np


def verify(root: Path, readout: Path) -> dict:
    data=json.loads(gzip.decompress(readout.read_bytes()))
    prepared=json.loads((root/'docs/50-diagnostics/s11/2026-10-14-candidate-rgb-trial/prepared.json').read_text())
    rasters={}
    for fid,spec in prepared['frames'].items():
        if spec['rgb_format']=='RGB_PNG':
            gray=cv2.cvtColor(cv2.imread(str(root/spec['rgb']['path'])),cv2.COLOR_BGR2GRAY)
            with np.load(root/spec['visibility']['path'],allow_pickle=False) as z:
                mask=z[spec['mask_key']].copy()
        else:
            with np.load(root/spec['rgb']['path'],allow_pickle=False) as z:
                gray=cv2.cvtColor(z['original_roi'],cv2.COLOR_BGR2GRAY)
                mask=(z['effective_mask']>0)&(z['glare_mask']==0)
        rasters[fid]=(gray,mask,spec['origin'])
    errors=[]
    gradients=partitions=0
    def check(ok,unit,kind):
        if not ok: errors.append({'unit':unit,'check':kind})
    for unit in data['units']:
        if 'raster_witness' not in unit: continue
        w=unit['raster_witness']; uid=unit['id']
        gray,mask,origin=rasters[unit['raw_frame_id']]
        height,width=gray.shape
        for sector in w['sectors']:
            x0,x1=[x-origin[0] for x in sector['source_x_range']]
            for p in sector['profile']:
                gradients+=1; y=p['local_y']
                xs=[x for x in range(x0,x1) if 0<y<height-1 and mask[y-1,x] and mask[y+1,x]]
                available=len(xs)>=2 and len(xs)/(x1-x0)>=0.5
                check(p['available']==available,uid,'edge availability')
                check(xs==p['paired_columns'],uid,'edge columns')
                expected=sum(int(gray[y+1,x])-int(gray[y-1,x]) for x in xs)/(510.0*len(xs)) if available else None
                check(p['value']==expected or (available and abs(p['value']-expected)<1e-12),uid,'edge value')
            for group in sector['peak_groups']:
                for y,p in zip(group['local_rows'],group['partitions'],strict=True):
                    partitions+=1; band=w['raster_binding']['band']
                    rows=[[y-2-k for k in range(band)],[y+2+k for k in range(band)],
                          [y-2-2*band-k for k in range(band)],[y+2+2*band+k for k in range(band)]]
                    check(rows==p['rows'],uid,'band geometry')
                    complete=all(0<=yy<height for rr in rows for yy in rr)
                    samples=[(k,x) for k in range(band) for x in range(x0,x1)
                             if complete and all(mask[rr[k],x] for rr in rows)]
                    count=len(samples)
                    status='UNAVAILABLE_CROP' if not complete else 'MEASURED' if count>=8 and count/(band*(x1-x0))>=0.5 else 'UNAVAILABLE_SUPPORT'
                    check(status==p['status'],uid,'band availability')
                    check(count==p['paired_pixel_count'],uid,'band count')
                    if status!='MEASURED':
                        check(p['margin'] is None,uid,'unavailable margin'); continue
                    totals=[sum(int(gray[rr[k],x]) for k,x in samples) for rr in rows]
                    a,b,fa,fb=totals; n,f=b-a,fb-fa
                    drift=max(abs(a-fa),abs(b-fb))
                    margin=(min(abs(n),abs(f)) if n*f>0 else -min(abs(n),abs(f)))-drift
                    check(margin==p['integer_margin'],uid,'integer partition margin')
                    check(abs(p['margin']-margin/(255.0*count))<1e-12,uid,'normalized margin')
                    check(all(abs(v-t/(255.0*count))<1e-12 for v,t in zip(p['means'],totals,strict=True)),uid,'band means')
    for relative,digest in data['inputs'].items():
        check(sha256((root/relative).read_bytes()).hexdigest()==digest,relative,'input hash')
    return {'schema':'s11-raster-partition-direct-loop-verification-v1',
            'readout_sha256':sha256(readout.read_bytes()).hexdigest(),
            'gradient_references':gradients,'partition_references':partitions,
            'error_count':len(errors),'errors':errors,'arithmetic_atol':1e-12,
            'physical_or_report_acceptance':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--readout',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); result=verify(a.root.resolve(),a.readout)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return int(result['error_count']>0)


if __name__=='__main__':
    raise SystemExit(main())
