"""Original ROI montage for the three supporting qualification recordings."""
from pathlib import Path
import sys,json,hashlib
import cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from oil_tracker.domain.recipe import InspectionRecipe
from oil_tracker.adapters.vision.geometry_masks import build_mask_bundle
fixed={'base_sample_1':[0,6,10,14],'sample2':[0,.5,1,1.5],'sample3':[30.03,50,76,104]}
canvas=Image.new('RGB',(1040,840),'white');records=[]
for i,(name,times) in enumerate(fixed.items()):
 recipe=InspectionRecipe.from_dict(json.loads((ROOT/'sample'/f'{name}.oilrecipe').read_text()));glass=next(g for g in recipe.glasses if g.enabled)
 cap=cv2.VideoCapture(str(ROOT/'sample'/f'{name}.mp4'));fps=cap.get(cv2.CAP_PROP_FPS)
 for j,t in enumerate(times):
  f=round(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,frame=cap.read();assert ok
  b=build_mask_bundle(frame,glass);img=Image.fromarray(cv2.cvtColor(b.crop,cv2.COLOR_BGR2RGB));img.thumbnail((248,236),Image.Resampling.NEAREST)
  x,y=j*260,i*280;canvas.paste(img,(x+6,y+36));ImageDraw.Draw(canvas).text((x+6,y+8),f'{name} / {t:g}s / f{f}',fill='black')
  records.append({'sample':name,'frame_index':f,'time_sec':f/fps,'crop_origin':b.crop_origin,'raw_roi_sha256':hashlib.sha256(b.crop.tobytes()).hexdigest(),'interpretation':'supporting media visual inspection, not new truth'})
 cap.release()
p=OUT/'other-samples-original-rois.jpg';assert not p.exists();canvas.save(p,quality=90)
(OUT/'supporting-media-receipt.json').write_text(json.dumps(records,indent=2)+'\n')
print('Original source ROIs',len(records),flush=True)
