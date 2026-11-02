#!/usr/bin/env python3
"""New-only literal-label rebind authorized by the actual parent image review.

Default is read-only. Preserves every original PNG, package, freeze and ledger.
No UI, rendering, media approval, readiness, canonical or site operation.
"""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
sys.path.insert(0,str(ROOT/'scripts'))
import native_capture_public as n
BASE=S/'production/proposals/native_public_integration_review_v3_20261028'
INPUT=BASE/'actual-reviewed.public-offline-validation.json'
INPUT_SHA='20b26f04ebcee922f3834c656f1362de104e8a8706869c7b0f37f854c7c43779'
OLD_SHA='423f6d917b4bf340dc64dd8f034f13ede2b568d219213cef8697d3689569fd14'
OUT=S/'expansion/plans/app-unit-inventory-native-counts-018-label-review-20261029'
ADDED=['Matches','Expected 24 boxes','Expected 6 cylinders']

def plan():
 if n.sha(INPUT)!=INPUT_SHA:raise ValueError('Held all14 public source report changed.')
 original=n.unique_json(INPUT.read_text());rows=copy.deepcopy(original['sources'])
 row=next(r for r in rows if '-018-' in r['id']);old_ref=copy.deepcopy(row['native_review_package'])
 if old_ref['sha256']!=OLD_SHA:raise ValueError('Held018 package changed.')
 check=n.PublicCheck(S);old=check.asset(old_ref,'original018reviewedsource');package=copy.deepcopy(old)
 for label in ADDED:
  if label in package['observations']['visible_labels']:raise ValueError('Preserve original labels; update already present.')
 package['observations']['visible_labels']+=ADDED
 package['review'].update(reviewer='Codex parent actual native source and context reviewer',
  reviewed_at='2026-10-29T04:15:03Z',
  method='New named parent context-and-label binding after re-viewing actual018tool image. The tool shows1824by1367previews of2732by2048rawpixels; no100-percent-original inspection or exact image-tool timestamp is asserted. Existing raw/source/session reviews remain retained. The review time is the actual new binding time, not the User audio-approval time.',
  findings=old['review']['findings']+' Additional actual parent pixel finding: Matches is plainly printed three times; Expected 24 boxes and Expected 6 cylinders are legible and unobstructed in this unchanged018image. Only these three literal labels are added. Plus/minus glyphs are visible but native AX identifiers are not promoted to printed names. This review supplies no video or publication approval.')
 package['review']['binding_sha256']=n.review_digest(package)
 name='018-native-battery-corrected-before-save.reviewed-labels-v2.json'
 data=(json.dumps(package,indent=2,ensure_ascii=False)+'\n').encode()
 row['visible_labels']=package['observations']['visible_labels']
 row['native_review_package']={'file':(OUT/name).relative_to(S).as_posix(),'sha256':hashlib.sha256(data).hexdigest()}
 provenance={'kind':'actual_parent_native018literal_label_addendum','source_only':True,'publishable':False,
  'reviewer':package['review']['reviewer'],'reviewed_at':package['review']['reviewed_at'],
  'review_time_scope':'Actual new context/binding review time supplied by parent; no exact timestamp of the preceding tool image view was retained.04:12:19was audio approval and is not used as pixel-review time.',
  'original_package':old_ref,'new_package':row['native_review_package'],'raw_png':package['capture']['image'],
  'literal_labels_added_only':ADDED,'required_labels_unchanged':True,
  'unchanged':['raw PNG bytes','capture time/session/device/geometry','build/source identity','installed/runtime receipts','original complete UI/served ledgers','all original source packages and immutable freeze'],
  'evidence':'Parent explicitly re-viewed actual018image and authorized these three printed-label observations; current agent independently viewed the same source through tool fit preview, without a100-percent-original-pixel assertion.',
  'video_or_publication_approved':False,'new_UI_actions':False}
 for field in ['capture','session','build','normal_ui','runtime','limitations']:
  if package[field]!=old[field]:raise ValueError('018rebind changed held identity: '+field)
 def body(v):return (json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode()
 files={name:data,'captures.native-reviewed.json':body({'app':'Unit','kind':'actual_reviewed_native_source_subset','screenshots':rows,'source_only':True,'publication_approved':False}),'provenance.json':body(provenance)}
 return files,rows

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args();files,rows=plan()
 if args.write:
  if OUT.exists():raise ValueError('Use new output; preserve all existing history.')
  OUT.mkdir(parents=True)
  for name,data in files.items():(OUT/name).write_bytes(data)
 if OUT.exists():
  for name,data in files.items():
   if (OUT/name).read_bytes()!=data:raise ValueError('Held output differs: '+name)
  for row in rows:n.validate_native_source(row,S,'Unit')
 print(json.dumps({'source_only':True,'publishable':False,'source_rows':len(rows),'ordinary_public_sources_validated':len(rows) if OUT.exists() else None,'written':args.write,'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}},indent=2))
if __name__=='__main__':main()
