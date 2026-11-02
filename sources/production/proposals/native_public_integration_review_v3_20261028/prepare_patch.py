#!/usr/bin/env python3
"""Read-only by default: compare isolated proposal with frozen production baseline.

--write-patch creates only the NEW proposal patch, never applies it. --check
requires an existing byte-identical patch and unchanged production baselines.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CHANGED=['render_walkthrough.py','verify_capture_evidence.py','expansion_site.py']
ADDED=['native_capture_public.py','native_capture_review.py','tests/test_native_public_package.py']
TARGET=HERE/'native-public-integration-review.patch'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plan():
 pieces=[];baselines={}
 for n in CHANGED:
  old=HERE/'base/scripts'/n;current=ROOT/'scripts'/n;new=HERE/'proposed/scripts'/n
  if sha(old)!=sha(current):raise ValueError('Production baseline changed; rebase proposal explicitly: '+n)
  baselines['scripts/'+n]=sha(old)
  pieces.extend(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='a/scripts/'+n,tofile='b/scripts/'+n))
 for n in ADDED:
  p=HERE/'proposed/scripts'/n
  pieces.extend(difflib.unified_diff([],p.read_text().splitlines(True),fromfile='/dev/null',tofile='b/scripts/'+n))
 return ''.join(pieces),baselines
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-patch',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
 content,baseline=plan()
 if args.write_patch:
  with TARGET.open('x') as stream:stream.write(content)
 if args.check:
  if not TARGET.is_file() or TARGET.read_text()!=content:raise ValueError('Proposal patch missing/changed; no production action performed.')
 print(json.dumps({'proposal_only':True,'publishable':False,'production_unchanged':True,'production_baselines':baseline,'patch':TARGET.name,'patch_sha256':hashlib.sha256(content.encode()).hexdigest(),'patch_written':args.write_patch,'checked':args.check},indent=2))
if __name__=='__main__':main()
