"""Audit previously exposed source frames; no detection, new labels or sample3 access."""
from pathlib import Path
import hashlib,json,math,subprocess
import cv2,numpy as np
from PIL import Image,ImageDraw
ROOT=Path('/Users/sunjaekim/Developer/oil_level_tracker')
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selection={'base_sample_1':[150,151,240],'sample2':[0,30,60],'sample4':[420,450,480,1200,1260,1275,1290,1305,1320,1485,1560,1620,1635,1665,1680],'sample5':[0,205,815,822,829,1225,1232,1239,1438,1643],'sample6':[0,146,436],'sample7':[0,532,1063]}
public=json.loads((ROOT/'docs/50-diagnostics/s11/2026-10-09-public-scene-controls.json').read_text())
look={(Path(c['video']).stem,c['frame_index']):c['source_raster']['path'] for c in public['cases']}
record={'schema':'s11-source-frame-audit-v1','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'purpose':'previously exposed source-context audit, not physical acceptance','sample3':'QUARANTINED; not decoded','videos':[]}
for name,frames in selection.items():
 p=ROOT/'sample'/f'{name}.mp4';cap=cv2.VideoCapture(str(p));assert cap.isOpened(),p
 fps=cap.get(cv2.CAP_PROP_FPS);entry={'video':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,'fps':fps,'frame_count':int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),'width':int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),'height':int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),'frames':[]}
 if name in ['base_sample_1','sample2','sample4']:
  e=json.loads((ROOT/'sample'/f'{name}.oilrecipe').read_text())['glasses'][0]['geometry']['ellipse'];box=[int(e['center_x']-e['radius_x']),int(e['center_y']-e['radius_y']),int(e['center_x']+e['radius_x']),int(e['center_y']+e['radius_y'])]
 else:box={'sample5':[740,250,1160,1080],'sample6':[200,0,2500,1440],'sample7':[760,240,1480,1060]}[name]
 tiles=[]
 for f in frames:
  cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,bgr=cap.read();assert ok,(name,f)
  row={'frame':f,'time_s':cap.get(cv2.CAP_PROP_POS_MSEC)/1000,'native_pixel_sha256':hashlib.sha256(bgr.tobytes()).hexdigest()}
  if (name,f) in look:
   saved=cv2.imread(str(ROOT/look[(name,f)]));row['saved_full_frame']=look[(name,f)];row['saved_pixels_equal']=bool(np.array_equal(bgr,saved))
  rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB);crop=Image.fromarray(rgb).crop(box);crop.save(OUT/f'{name}-f{f:06d}.png');tile=Image.new('RGB',(280,330),'white');crop.thumbnail((272,300),Image.Resampling.NEAREST);tile.paste(crop,((280-crop.width)//2,25));ImageDraw.Draw(tile).text((5,5),f'{name} / f{f} / {row["time_s"]:.3f}s',fill='black');tiles.append(tile);entry['frames'].append(row)
 cap.release();cols=min(5,len(tiles));sheet=Image.new('RGB',(280*cols,330*math.ceil(len(tiles)/cols)),'white')
 for i,t in enumerate(tiles):sheet.paste(t,((i%cols)*280,(i//cols)*330))
 sheet.save(OUT/f'{name}-source-sheet.png');record['videos'].append(entry)
(OUT/'source-frame-audit.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'videos':len(record['videos']),'frames':sum(len(v['frames']) for v in record['videos']),'pixel_comparisons':[r['saved_pixels_equal'] for v in record['videos'] for r in v['frames'] if 'saved_pixels_equal' in r]},indent=2))
