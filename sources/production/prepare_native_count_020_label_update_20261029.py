#!/usr/bin/env python3
"""New-only020Inventory literal binding, preserving all earlier source packages."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';sys.path.insert(0,str(ROOT/'scripts'))
import native_capture_public as n
INPUT=S/'expansion/plans/app-unit-inventory-native-counts-018-label-review-20261029/captures.native-reviewed.json'
INPUT_SHA='7150d6be18dd77fd7e3df09df8dcb921889269f7e083e163a278ac93dcefaf41'
OUT=S/'expansion/plans/app-unit-inventory-native-counts-020-label-review-20261029'

def plan():
 if n.sha(INPUT)!=INPUT_SHA:raise ValueError('Preserve all previous source rows.')
 rows=copy.deepcopy(n.unique_json(INPUT.read_text())['screenshots']);row=next(r for r in rows if '-020-' in r['id'])
 old_ref=copy.deepcopy(row['native_review_package']);old=n.PublicCheck(S).asset(old_ref,'held020package');p=copy.deepcopy(old)
 if 'Inventory' in p['observations']['visible_labels']:raise ValueError('Label update already present.')
 p['observations']['visible_labels'].append('Inventory')
 p['review'].update(reviewer='Codex parent actual native source and context reviewer',reviewed_at='2026-10-29T04:20:03Z',
  method='Actual new parent context-and-literal binding after re-viewing unchanged020PNG with view_image original detail. The tool displays1824by1367previews of2732by2048rawpixels; no100-percent-original inspection is asserted. Review time is the actual later context-review time, not an invented image-tool timestamp.',
  findings=old['review']['findings']+' Additional parent actual pixel finding: the printed Inventory sidebar label is plainly visible and unobstructed. The real back-arrow glyph is visible, but no AX identifier or invented printed Back label is promoted. Add only Inventory to literal observations so cue59 return to Inventory has genuine visible context. Source-only review; no video/publication approval.')
 p['review']['binding_sha256']=n.review_digest(p)
 def body(v):return (json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode()
 name='020-native-save-progress-result.reviewed-labels-v2.json';data=body(p)
 row['visible_labels']=p['observations']['visible_labels'];row['native_review_package']={'file':(OUT/name).relative_to(S).as_posix(),'sha256':hashlib.sha256(data).hexdigest()}
 for key in ['capture','session','build','normal_ui','runtime','limitations']:
  if p[key]!=old[key]:raise ValueError('Held source identity changed: '+key)
 files={name:data,'captures.native-reviewed.json':body({'app':'Unit','kind':'actual_reviewed_native_source_subset','screenshots':rows,'source_only':True,'publication_approved':False}),
  'provenance.json':body({'kind':'actual_parent_native020literal_label_addendum','reviewer':p['review']['reviewer'],'reviewed_at':p['review']['reviewed_at'],'source_only':True,'publishable':False,'original_package':old_ref,'new_package':row['native_review_package'],'raw_png':p['capture']['image'],'literal_labels_added_only':['Inventory'],'required_labels_unchanged':True,'all_other_capture_build_ledger_fields_unchanged':True,'prior018source_manifest':{'file':INPUT.relative_to(S).as_posix(),'sha256':INPUT_SHA},'no_AX_icon_name_promotion':True,'new_UI_actions':False,'video_or_publication_approved':False})}
 return files,rows

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args();files,rows=plan()
 if args.write:
  if OUT.exists():raise ValueError('Preserve previous output; use a new version.')
  OUT.mkdir(parents=True)
  for name,data in files.items():(OUT/name).write_bytes(data)
 if OUT.exists():
  for name,data in files.items():
   if (OUT/name).read_bytes()!=data:raise ValueError('Held output changed: '+name)
  for row in rows:n.validate_native_source(row,S,'Unit')
 print(json.dumps({'source_only':True,'publishable':False,'ordinary_public_sources_validated':len(rows) if OUT.exists() else None,'written':args.write,'files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}},indent=2))
if __name__=='__main__':main()
