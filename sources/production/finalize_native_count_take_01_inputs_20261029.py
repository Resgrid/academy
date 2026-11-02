#!/usr/bin/env python3
"""Retain NEW final source inputs from the exact parent-accepted proposed plan.

Default is read-only. --write creates a new guarded folder. This authoring
receipt records the genuine parent task authorization, not a manufactured
pixel/frame/playback review or an inferred timestamp for that parent review.
"""
import argparse,copy,hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import validate_inputs
NAME='app-unit-inventory-native-counts'
BASE=S/'expansion/plans'/ (NAME+'-take-01-proposed-20261029')
OUT=S/'expansion/plans'/ (NAME+'-take-01-final-inputs-20261029')
PINS={'plan.proposed.json':'3cef4abeaa71bd614209fbdf542c495b96a9943dddf075b84fb20a8f6d7abf03','correspondence.proposed.json':'7382227514ddb7ee8856c347176a00f1015f57701c5fa502f1c9d0e0356fdfb3'}
LESSON=S/'expansion/plans'/ (NAME+'-capture-freeze-20261028')/(NAME+'.narrated-source.json')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 for name,digest in PINS.items():
  if sha(BASE/name)!=digest:raise ValueError('Parent-reviewed proposal changed: '+name)
 p=json.loads((BASE/'plan.proposed.json').read_text());original=copy.deepcopy(p)
 p.update(parent_plan_review_pending=False,render_authorized=True)
 p['parent_plan_review']={'reviewer':'Codex parent actual25hold90cue correspondence reviewer','approval_received':True,
  'bound_at':datetime.now(timezone.utc).isoformat(),'source_inputs':PINS,
  'evidence':'Parent explicitly read the complete compact25hold screen order and all90actual cue texts/references against these exact proposed hashes, accepted them, and authorized this new final source-input package and render. The parent will separately review actual encoded frames and fresh beginning/middle/end playback.',
  'new_pixel_frame_or_playback_review_claimed':False,'publication_approved':False}
 for key in ['scenes','narration','captions','capture_manifests','screenshot_reviews','duration_seconds']:
  if p[key]!=original[key]:raise ValueError('Do not change approved actual source/timing: '+key)
 files={'plan.approved-source-inputs.json':(json.dumps(p,indent=2,ensure_ascii=False)+'\n').encode(),
  'parent-reviewed-correspondence.json':(BASE/'correspondence.proposed.json').read_bytes()}
 return files

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');a=parser.parse_args();files=prepare()
 if a.write:
  if OUT.exists():raise ValueError('Preserve final source inputs; use new output.')
  OUT.mkdir(parents=True)
  for name,data in files.items():(OUT/name).write_bytes(data)
  checked=validate_inputs(LESSON,OUT/'plan.approved-source-inputs.json',S)
  if len(checked['cues'])!=90 or sum(len(sc['screens']) for sc in checked['scenes'])!=25:raise ValueError('Approved actual cue/hold inventory changed.')
 print(json.dumps({'source_inputs_only':True,'publication_approved':False,'written':a.write,'files':{name:hashlib.sha256(body).hexdigest() for name,body in files.items()}},indent=2))
if __name__=='__main__':main()
