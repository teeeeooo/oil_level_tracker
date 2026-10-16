"""Post-run source inspection: all 113 frozen sampled frames, no new role labels."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cv2
from oil_tracker.adapters.vision.opencv_video_reader import OpenCvVideoReader
from tests.diagnostics.s11_role_consumer_intervention import SAVED, BUNDLE, PINS, digest, require, write_json

VIDEO_SHA = 'ee971b3871d806ff194117eb64960cca3ad158e8ae3d1be4097ebc20fe472892'


def capture(root: Path, comparison: Path, output: Path):
    require(not any(output.iterdir()), 'empty managed work directory required')
    video = root/'sample/sample4.mp4'
    require(digest(video) == VIDEO_SHA, 'source video changed')
    require(digest(root/SAVED/'raw.json') == PINS[str(SAVED/'raw.json')], 'saved raw changed')
    raw = json.loads((root/SAVED/'raw.json').read_text())
    compare = json.loads(comparison.read_text())
    recipe = json.loads((root/BUNDLE/'recipe_snapshot.oilrecipe').read_text())
    e = recipe['glasses'][0]['geometry']['ellipse']
    x0,y0 = int(e['center_x']-e['radius_x']),int(e['center_y']-e['radius_y'])
    w,h = int(2*e['radius_x']),int(2*e['radius_y'])
    pre = {'video_sha256': VIDEO_SHA, 'raw_sha256': PINS[str(SAVED/'raw.json')],
           'comparison_path': str(comparison.relative_to(root)), 'comparison_sha256': digest(comparison),
           'recipe_sha256': digest(root/BUNDLE/'recipe_snapshot.oilrecipe'),
           'source_crop_xywh':[x0,y0,w,h], 'display_scale':2, 'resize':'nearest; no measurement',
           'selection':'Every original sampled frame, including unchanged early context; post-run visual inspection, not holdout.',
           'new_physical_labels':False, 'harness_sha256':digest(Path(__file__))}
    write_json(output/'preflight.json',pre)
    combined = next(v for v in compare['variants'] if v['variant']=='negative_veto_positive_authority')
    changes = {d['frame_index']:d for d in combined['changed_selections']}
    rows=[]; pages=[]; tile_w,tile_h=2*w+16,2*h+42
    font=ImageFont.load_default(size=13)
    with OpenCvVideoReader(video) as reader:
        metadata=asdict(reader.metadata)
        for i,d in enumerate(raw):
            frame,index,actual=reader.read_at(d['time_sec'])
            require(index==d['frame_index'] and abs(actual-d['time_sec'])<1e-6,'decode/source identity mismatch')
            crop=cv2.cvtColor(frame[y0:y0+h,x0:x0+w],cv2.COLOR_BGR2RGB)
            require(crop.shape==(h,w,3),'invalid source crop')
            image=Image.fromarray(crop)
            if i%30==0: pages.append(Image.new('RGB',(tile_w*5,tile_h*6),'white'))
            page=pages[-1]; px=(i%5)*tile_w+8; py=((i%30)//5)*tile_h
            draw=ImageDraw.Draw(page)
            draw.text((px,py+2),f"f{index} / {actual:g} s",font=font,fill='black')
            change=changes.get(index)
            caption='Oil selection unchanged' if change is None else f"Y OFF {change['baseline_y']} / joint {change['variant_y']}"
            draw.text((px,py+19),caption,font=font,fill='black')
            page.paste(image.resize((2*w,2*h),Image.Resampling.NEAREST),(px,py+38))
            recovered=page.crop((px,py+38,px+2*w,py+38+2*h)).resize((w,h),Image.Resampling.NEAREST)
            sha=hashlib.sha256(image.tobytes()).hexdigest()
            require(hashlib.sha256(recovered.tobytes()).hexdigest()==sha,'atlas altered original pixels')
            rows.append({'frame_index':index,'actual_time_sec':actual,'original_rgb_sha256':sha,
                         'page':len(pages),'display_xywh':[px,py+38,2*w,2*h]})
    for i,page in enumerate(pages,1): page.save(output/f'source-{i}.png')
    require(digest(video)==VIDEO_SHA and digest(comparison)==pre['comparison_sha256'],'input mutation')
    result={'schema':'s11-role-source-context-v1','preflight':pre,'metadata':metadata,'frames':rows,
            'source_frame_joins':len(rows),'pixel_roundtrip_checks':len(rows),'new_physical_labels':False,
            'page_sha256':{p.name:digest(p) for p in output.glob('*.png')}}
    write_json(output/'source-context.json',result)
    print(json.dumps({'source_frame_joins':len(rows),'pixel_roundtrip_checks':len(rows),'pages':len(pages)}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--comparison',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    capture(a.root.resolve(),a.comparison.resolve(),a.output.resolve())
