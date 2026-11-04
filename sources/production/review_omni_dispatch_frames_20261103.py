"""Extract review sheets and verify every encoded hold retains source application pixels."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT/'scripts'))
from render_walkthrough import layout

parser = argparse.ArgumentParser()
parser.add_argument('lesson')
args = parser.parse_args()
r = S/'expansion/rendered'/f'{args.lesson}-take-01'
e = json.loads((r/'evidence.pending.json').read_text())
screens = {v['id']:v for v in e['screenshots']}
frames = []
for seg in e['rendered_segments']:
    shot = screens[seg['screenshot_id']]
    frame = seg['frame']
    f = S/frame['file']
    assert sha256(f.read_bytes()).hexdigest()==frame['sha256']
    box = layout(shot['width'],shot['height'])
    with Image.open(f) as encoded, Image.open(S/shot['file']) as original:
        x,y,w,h = [box[key] for key in ('x','y','width','height')]
        a = np.asarray(encoded.convert('RGB').crop((x,y,x+w,y+h)), dtype=np.int16)
        b = np.asarray(original.convert('RGB').resize((w,h),Image.Resampling.LANCZOS), dtype=np.int16)
        mae = float(np.abs(a-b).mean())
        if mae >= 4:
            raise ValueError(f'Frame differs from {shot["id"]}: {mae:.3f}')
    frames.append({'file':frame['file'],'sha256':frame['sha256'],'source':shot['id'],'pixel_mae':round(mae,4)})
review = ROOT/'_reports/omni-dispatch-20261103/visual-review'
review.mkdir(parents=True, exist_ok=True)
for start in range(0,len(frames),6):
    subset=frames[start:start+6]
    sheet=Image.new('RGB',(1920,390*((len(subset)+2)//3)),'#dde6f0')
    draw=ImageDraw.Draw(sheet)
    for idx, row in enumerate(subset):
        x,y=idx%3*640,idx//3*390
        draw.text((x+5,y+5),row['source'],fill='black',font_size=15)
        with Image.open(S/row['file']) as im:
            sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y+28))
    sheet.save(review/f'{args.lesson}-encoded-{start//6+1}.jpg',quality=93)
(r/'encoded-screen-pixel-checks.json').write_text(json.dumps({'video_sha256':e['video']['sha256'],'frames':frames},indent=2)+'\n')
print(args.lesson,len(frames),max(row['pixel_mae'] for row in frames))
