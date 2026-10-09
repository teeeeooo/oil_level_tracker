from pathlib import Path
import json,hashlib
import cv2,numpy as np
from PIL import Image,ImageDraw
ROOT=Path('/Users/sunjaekim/Developer/oil_level_tracker');OUT=ROOT/'sample/output/s11-design-audit-cc17924-20261009-001'
plans={'base_sample_1':[0,150,151,433],'sample2':[0,30,60],'sample3':[930,1800,2550,3090],'sample4':[420,480,1275,1320,1560,1620,1680]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'visual-preflight.json').write_text(json.dumps({'scope':'Source review only, no detector; frozen native frame indices in existing fixed-geometry windows. No new truth or error tolerances. Existing public water/beer/milk sheets are reviewed separately.','plans':plans},indent=2)+'\n')
rows=[]
for name,frames in plans.items():
 path=ROOT/'sample'/f'{name}.mp4';recipe=ROOT/'sample'/f'{name}.oilrecipe';g=json.loads(recipe.read_text())['glasses'][0]['geometry']['ellipse'];box=tuple(int(v) for v in [g['center_x']-g['radius_x'],g['center_y']-g['radius_y'],g['center_x']+g['radius_x'],g['center_y']+g['radius_y']])
 cap=cv2.VideoCapture(str(path));assert cap.isOpened();fps=cap.get(cv2.CAP_PROP_FPS);total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));tw=330;cols=min(4,len(frames));nrows=(len(frames)+cols-1)//cols
 sheet=Image.new('RGB',(cols*tw,nrows*380+45),'white');dr=ImageDraw.Draw(sheet);dr.text((8,10),name+' | raw Recipe ROI | not new truth',fill='black')
 for i,f in enumerate(frames):
  assert f<total;cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,im=cap.read();assert ok;actual=int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))-1;assert actual==f
  crop=im[box[1]:box[3],box[0]:box[2]];image=Image.fromarray(crop[:,:,::-1]);image.thumbnail((tw-12,330),Image.Resampling.NEAREST);x=(i%cols)*tw+6;y=(i//cols)*380+72;sheet.paste(image,(x,y));dr.text((x,y-20),f'f{f} / nominal {f/fps:.3f}s',fill='black')
  rows.append({'sample':name,'video_sha256':sha(path),'recipe_sha256':sha(recipe),'frame':f,'returned_frame':actual,'nominal_time_s':f/fps,'decoder_timestamp_s':cap.get(cv2.CAP_PROP_POS_MSEC)/1000,'fps':fps,'crop_xyxy':box,'decoded_frame_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'interpretation':'agent visual context only; existing truth unchanged'})
 cap.release();sheet.save(OUT/(name+'-source-review.png'))
for role,frames in [('oil-positive',[1275,1281,1320,1350]),('foam-positive',[420,438,480,510])]:
 tw=275;sheet=Image.new('RGB',(tw*len(frames),605),'white');dr=ImageDraw.Draw(sheet);dr.text((8,8),role+' | A/B appearance partition, NOT Oil/Foam labels',fill='black')
 for i,f in enumerate(frames):
  a=np.load(OUT/'partition-trial'/f'{role}-f{f}.npz',allow_pickle=False);raw=a['crop'][:,:,::-1];lab=a['labels'];mix=raw.copy().astype(float)
  for cl,rgb in [(1,(255,90,70)),(2,(50,160,255))]:mix[lab==cl]=.6*mix[lab==cl]+.4*np.array(rgb)
  for j,img in enumerate([raw,mix.astype(np.uint8)]):
   image=Image.fromarray(img).resize((260,260),Image.Resampling.NEAREST);y=62+285*j;sheet.paste(image,(i*tw+5,y));dr.text((i*tw+5,y-20),f'f{f}: '+('raw' if j==0 else 'current partition'),fill='black')
 sheet.save(OUT/(role+'-partition-review.png'))
(OUT/'visual-review.json').write_text(json.dumps({'new_decode_records':rows,'public_sheets_reviewed':['sample/output/s11-public-scene-controls-20261009-001/water-controls.png','sample/output/s11-public-scene-controls-20261009-001/beer-controls.png','sample/output/s11-public-scene-controls-20261009-001/milk-controls.png'],'generated_sheets':{str(p.relative_to(ROOT)):sha(p) for p in OUT.glob('*review.png')},'scope':'bounded visual source review; not full video screening, current detector efficacy or user truth'},indent=2)+'\n')
print('decoded',len(rows),'frames; saved',str(OUT))
