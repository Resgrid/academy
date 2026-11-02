"""Freeze approved Dispatch source only, with later acceptance receipts retained.

Default read-only; --freeze creates a NEW portable snapshot. No audio, timing,
canonical readiness, site, target, Git or application operation is performed.
"""
import argparse
from copy import deepcopy
import hashlib,importlib.util,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';APP=ROOT.parents[3]/'Dispatch'
NAME='app-dispatch-map-and-site-reference'
BASE=Path('expansion/plans')/(NAME+'-candidate-20261029')
MAP=Path('expansion/plans')/(NAME+'-27span-proposed-20261029')
FINAL=Path('expansion/plans')/(NAME+'-capture-freeze-20261029')
PARENT=Path('expansion/audits/dispatch-map-site-reference-parent-freeze-acceptance-20261029.json')
PRIVACY=Path('expansion/audits/dispatch-map-site-reference-known-values-20261029.json')
PINS={
 BASE/(NAME+'.candidate.json'):'5b08b842e0efd9ca37114732cb8e43002f8b31b1059da18f3611a8d8b509c4dd',
 BASE/'narration.txt':'5e8db2a4fd8fcfa4f168c0c0dace29fcfa41841ab2ffa838400674b06cb62994',
 BASE/'captures.reviewed.json':'30ff227e9108944854f9759fdea6151d22b552bceb814ce3039e86215251834f',
 BASE/'screen-sequence.untimed.json':'b3374ef074b73ff1326e1b486805327262be9fdd97ed2d73c31610a6ebfe620e',
 BASE/'literal-source-review.json':'2d9b84211e51bc3099b2caca63614ee9e9efac9ebde6bf0d27f33a46c276196d',
 BASE/'source-evidence.json':'e5f44b271799035b9cbe31ee6bbf7547fa8f514892cb18528c18fe1acdbfd0ba',
 BASE/'api-and-scope.json':'3f1166a881a084263880ff90a38d7d1e34116fc3cbd5d89962739ad23020e810',
 BASE/'preflight.json':'507fd2e3e45d6579304a488ac6a3cba226d737a06d966ed16f8d7c88d38b73e4',
 MAP/'ordered27span.proposed.json':'129d3e787b6b974cac6a0de4551352c28ebd909fcd2af3d0453907960a279a73',
 MAP/'ordered27span.compact.txt':'523c209c5e7ee81dc5a894b33190e02973fe7c9ad5359f45706fa8a21a3ae0e0',
 MAP/'literal-glyph-supplement.proposed.json':'2dd79d6b5faa6bf1ebad742443f5f926c6a7c656303620079ad0e37d244e98fa',
 MAP/'provenance.json':'2c60bc7f9b2b15cd6e2d0337628199d2a3018744943c0e98e22fc33446103f72',
 PARENT:'3012e8dbe9c85e32f134d533e9cfbfbaa9e0112369f369ea974ec60830614860',
 PRIVACY:'55dc9503950cfb5cc91d9e9d7c9dcf77e113539168cd20037df4f1e174b90daf',
}
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def prepare():
 for path,digest in PINS.items():assert sha(S/path)==digest,'Changed reviewed input: '+str(path)
 parent=json.loads((S/PARENT).read_text());privacy=json.loads((S/PRIVACY).read_text())
 assert parent['parent_whole_script_approved'] and parent['ordered_source_correspondence_approved'] and parent['literal_glyph_finding_approved']
 assert parent['narration_sha256']==PINS[BASE/'narration.txt'] and parent['ordered27span_compact_sha256']==PINS[MAP/'ordered27span.compact.txt']
 assert privacy['passed'] and privacy['known_private_values_checked']==17 and privacy['file_count']==58 and not privacy['findings']
 for row in privacy['files']:
  file=ROOT/row['file'];assert file.is_file() and sha(file)==row['sha256'],'Changed known-value audited source: '+row['file']
 lesson=json.loads((S/BASE/(NAME+'.candidate.json')).read_text());original_scenes=encoded(lesson['scenes'])
 lesson.update(status='Parent-approved source and narration freeze; actual audio and all media reviews remain unassigned.',narration_frozen=True,parent_whole_script_approved=True,publication_approved=False)
 manifest=deepcopy(json.loads((S/BASE/'captures.reviewed.json').read_text()));sequence=deepcopy(json.loads((S/BASE/'screen-sequence.untimed.json').read_text()))
 compact=deepcopy(json.loads((S/MAP/'ordered27span.proposed.json').read_text()));glyph=json.loads((S/MAP/'literal-glyph-supplement.proposed.json').read_text())
 assert len(lesson['scenes'])==8 and len(compact['untimed_spans'])==27 and len(manifest['screenshots'])==21
 assets={};pathmap={}
 for row in manifest['screenshots']:
  for field,hashfield,sub in [('file','sha256','images'),('dom_file','dom_sha256','dom')]:
   before=row[field];src=S/before;assert sha(src)==row[hashfield]
   target=Path(sub)/src.name;assets[target.as_posix()]=src.read_bytes();new=(FINAL/target).as_posix();row[field]=new;pathmap[before]={'file':new,'sha256':row[hashfield]}
  if row['id'][:3] in ['005','006']:
   assert '✕' not in row['visible_labels'];row['visible_labels'].append('✕')
   row['supplemental_literal_review']={'literal_label':'✕','spoken_alias':'close the panel','source_sha256':row['sha256'],'agent_finding_receipt':'original-review/literal-glyph-supplement.proposed.json','parent_acceptance_receipt':'parent-freeze-acceptance.json','binding_recorded_at':parent['binding_recorded_at'],'scope':'Only the actual visible literal close glyph is added. No accessible control name or new original-size/100-percent image inspection is asserted. Prior actual image review remains unchanged.'}
 for scene in sequence['scenes']:
  for screen in scene['screens']:
   assert screen['file'] in pathmap;screen['file']=pathmap[screen['file']]['file']
 for span in compact['untimed_spans']:
  assert span['source_file'] in pathmap;span['source_file']=pathmap[span['source_file']]['file']
 compact['root_review_pending']=False;compact['parent_acceptance_receipt']='parent-freeze-acceptance.json';compact['known_value_audit_pending']=False;compact['narration_frozen']=True
 compact['one_actual_literal_supplement']['parent_acceptance_into_frozen_subset_pending']=False
 assert encoded(lesson['scenes'])==original_scenes,'Frozen narrated scenes must remain byte-identical as JSON values.'
 narration=(S/BASE/'narration.txt').read_bytes();assert len(narration.decode().split())==634
 for file in (S/BASE).iterdir():
  if file.is_file():assets['original-review/'+file.name]=file.read_bytes()
 for file in (S/MAP).iterdir():
  if file.is_file():assets['original-review/'+file.name]=file.read_bytes()
 code=json.loads((S/BASE/'source-evidence.json').read_text())
 for row in code['files']:
  file=APP/row['path'];assert sha(file)==row['sha256'];assets['source/Dispatch/'+row['path']]=file.read_bytes()
 assets.update({NAME+'.narrated-source.json':encoded(lesson),'narration.frozen.txt':narration,'captures.reviewed.json':encoded(manifest),'screen-sequence.untimed.json':encoded(sequence),'ordered27span.accepted.json':encoded(compact),'ordered27span.compact.txt':(S/MAP/'ordered27span.compact.txt').read_bytes(),'parent-freeze-acceptance.json':(S/PARENT).read_bytes(),'known-values-audit.json':(S/PRIVACY).read_bytes()})
 recipe={'kind':'immutable_Dispatch_reference_source_only_freeze','lesson_id':NAME,'source_only':True,'parent_whole_script_approved':True,'publication_approved':False,'audio_or_timing_assigned':False,'scenes':8,'narration_words':634,'source_images':21,'untimed_spans':27,'source_git_revision':code['git_revision'],'source_code_snapshots':len(code['files']),'six_sectors_spoken_and_companions':True,'original_input_hashes':{str(k):v for k,v in PINS.items()},'public_package_path_map':pathmap,'narrated_source_sha256':hashlib.sha256(assets[NAME+'.narrated-source.json']).hexdigest(),'narration_sha256':hashlib.sha256(narration).hexdigest(),'freeze_files':{name:hashlib.sha256(body).hexdigest() for name,body in assets.items()},'limits':['No rendered video, speech timing, natural-voice listening, frame or playback approval exists.','All21 JPEG and DOM copies are byte-identical; only new metadata paths and accepted literal005/006 close glyph observations are added.','Known-value audit17 covers its exact58 retained originals; extra acceptance/map/source-code metadata receives ordinary rule scanning here, with no credential-file reread.']}
 assets['source-freeze.json']=encoded(recipe)
 return recipe,assets

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');a=p.parse_args();recipe,assets=prepare()
 if a.freeze:
  out=S/FINAL;assert not out.exists(),'New-only freeze; preserve history.'
  spec=importlib.util.spec_from_file_location('unchanged_privacy',ROOT/'scripts/audit_public_repo.py');privacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(privacy)
  issues=[{'file':name,'rule':rule} for name,body in assets.items() for rule in privacy.scan_bytes(body)]
  assert not issues,issues
  out.mkdir(parents=True)
  for name,body in assets.items():
   file=out/name;file.parent.mkdir(parents=True,exist_ok=True)
   with file.open('xb') as stream:stream.write(body)
  assert all(sha(out/name)==digest for name,digest in recipe['freeze_files'].items())
 print(json.dumps({'passed_source_preflight':True,'files_written':a.freeze,'output':str(S/FINAL),'scenes':8,'words':634,'images':21,'spans':27,'source_code_snapshots':recipe['source_code_snapshots'],'frozen_source_sha256':recipe['narrated_source_sha256'],'narration_sha256':recipe['narration_sha256'],'source_freeze_sha256':sha(S/FINAL/'source-freeze.json') if a.freeze else None,'audio_or_timing_assigned':False,'ready_or_canonical_changed':False}))
if __name__=='__main__':main()
