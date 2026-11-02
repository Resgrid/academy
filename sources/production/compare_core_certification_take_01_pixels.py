"""Measure every actual Certification cue image against its intact source.

Pillow is optional until invoked. Metrics are compression/correspondence checks,
not semantic or visual approval. --write-new preserves the prior extraction.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCES=Path(__file__).resolve().parents[1]
TAKE=SOURCES/'expansion/rendered/core-certification-administration-take-01'
MASTER='77e6358b3ef936e80e9feb3f75a4a56f17512d4e029d352790752008fe9464b3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-new',action='store_true');args=p.parse_args()
 from PIL import Image,ImageChops,ImageStat
 assert sha(TAKE/'core-certification-administration.mp4')==MASTER
 assembly=json.loads((TAKE/'assembly.json').read_text());pending=json.loads((TAKE/'evidence.pending.json').read_text())
 extraction=TAKE/'frame-qa/extraction-and-pixel-metrics.json'
 assert sha(extraction)=='1b3a5a902c49e7ca2b642fd6de641a95c7295d2411f63b3dfef0358833d27751'
 data=json.loads(extraction.read_text());shots={r['id']:r for r in pending['screenshots']};rows=[]
 for cue in data['cue_frames']:
  path=SOURCES/cue['file'];assert sha(path)==cue['sha256']
  source=shots[cue['source_id']];source_path=SOURCES/source['file'];assert sha(source_path)==source['sha256']
  frame=Image.open(path).convert('RGB');image=Image.open(source_path).convert('RGB');assert frame.size==(1920,1080)
  layout=assembly['screenshots'][cue['source_id']]['layout'];assert layout['cropped'] is False
  box=(layout['x'],layout['y'],layout['x']+layout['width'],layout['y']+layout['height'])
  fitted=image.resize((layout['width'],layout['height']),Image.Resampling.LANCZOS)
  means=ImageStat.Stat(ImageChops.difference(fitted,frame.crop(box))).mean
  rows.append({'cue':cue['cue'],'actual_frame_file':cue['file'],'actual_frame_sha256':cue['sha256'],
    'actual_time':cue['actual_time'],'source_id':cue['source_id'],'source_sha256':source['sha256'],
    'fitted_region':layout,'mean_absolute_error_per_channel':means,'mean_absolute_error_255':sum(means)/3})
 assert len(rows)==114
 out={'kind':'actual114cue_source_pixel_comparison','video_sha256':MASTER,
      'extraction_file':str(extraction.relative_to(SOURCES)),'extraction_sha256':sha(extraction),
      'method':'Every actual encoded JPEG cue midpoint fitted region compared against the exact source resized with LANCZOS. Normal H264/JPEG/color differences are measured; no OCR, semantic or human visual approval inferred.',
      'comparisons':rows,'maximum_mae_255':max(r['mean_absolute_error_255'] for r in rows),'visual_approval_inferred':False}
 if args.write_new:
  path=TAKE/'frame-qa/all-cue-pixel-comparisons.json';assert not path.exists()
  with path.open('x') as f:f.write(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'cue_images_compared':114,'maximum_mae_255':out['maximum_mae_255'],'written':args.write_new,'visual_approval_inferred':False}))
if __name__=='__main__':main()
