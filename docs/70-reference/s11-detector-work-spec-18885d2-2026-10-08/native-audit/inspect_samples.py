"""Read-only source-video sampling for the pinned S11 design audit."""
from pathlib import Path
import hashlib, json, math, subprocess
import cv2
from PIL import Image, ImageDraw
ROOT = Path('/Users/sunjaekim/Developer/oil_level_tracker')
OUT = Path(__file__).resolve().parent
HEAD = '18885d226a7a7745bc2d062fd750ec263b9c78f6'
assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() == HEAD
TIMES = {
 'base_sample_1': [0,4,5,5.04,6,8,10,12,14],
 'sample2': [0,.25,.5,.75,1,1.25,1.5,1.75,2],
 'sample3': [30.03,35,40,45,50,55,65,75.08,80,90,100,105],
 'sample4': [0,14,19,28,40,42,42.5,43,44,44.5,49.5,52],
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
summary = {'head':HEAD, 'opencv':cv2.__version__, 'scope':'exposed Mac regression, not pixel truth', 'samples':{}}
for name,times in TIMES.items():
 video, recipe_path = ROOT/f'sample/{name}.mp4', ROOT/f'sample/{name}.oilrecipe'
 video_hash, recipe_hash = sha(video), sha(recipe_path)
 recipe = json.loads(recipe_path.read_text())
 ellipse = recipe['glasses'][0]['geometry']['ellipse']
 cap = cv2.VideoCapture(str(video))
 assert cap.isOpened(), name
 fps, count = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
 targets = {round(t*fps):t for t in times}
 rows, tiles = [], []
 width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
 x0,y0 = max(0,math.floor(ellipse['center_x']-ellipse['radius_x'])), max(0,math.floor(ellipse['center_y']-ellipse['radius_y']))
 x1,y1 = min(width,math.ceil(ellipse['center_x']+ellipse['radius_x'])), min(height,math.ceil(ellipse['center_y']+ellipse['radius_y']))
 index = 0
 while index <= max(targets):
  ok, frame = cap.read()
  assert ok, (name,index)
  if index in targets:
   crop = frame[y0:y1,x0:x1]
   image = Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB))
   image.thumbnail((280,280),Image.Resampling.NEAREST)
   tile = Image.new('RGB',(300,315),'white')
   tile.paste(image,((300-image.width)//2,30))
   ImageDraw.Draw(tile).text((8,8),f'{name} f{index} t={index/fps:.3f}s',fill='black')
   tiles.append(tile)
   rows.append({'requested_sec':targets[index],'frame_index':index,'timestamp_sec':index/fps,'roi_pixel_sha256':hashlib.sha256(crop.tobytes()).hexdigest()})
  index += 1
 cap.release()
 assert len(rows)==len(targets)
 sheet=Image.new('RGB',(900,315*math.ceil(len(tiles)/3)),'white')
 for j,tile in enumerate(tiles): sheet.paste(tile,((j%3)*300,(j//3)*315))
 path=OUT/f'{name}-source-review.png'; assert not path.exists(); sheet.save(path)
 assert sha(video)==video_hash and sha(recipe_path)==recipe_hash
 summary['samples'][name]={'video_sha256':video_hash,'recipe_sha256':recipe_hash,'fps':fps,'frame_count':count,'frame_size':[width,height],'reviewed_frames':rows,'sheet_sha256':sha(path),'source_unchanged':True}
 print(name, len(rows), 'source frames reviewed; sources unchanged',flush=True)
assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() == HEAD
path=OUT/'source-review-receipt.json'; assert not path.exists()
path.write_text(json.dumps(summary,indent=2)+'\n')
print('COMPLETE',sum(len(v['reviewed_frames']) for v in summary['samples'].values()))
