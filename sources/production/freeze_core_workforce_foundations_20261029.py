#!/usr/bin/env python3
"""Freeze the parent-approved Workforce source/script only; default read-only.

No UI, source, DB, audio, media, canonical, site, target or Git mutation.
--freeze creates a new immutable package and refuses existing output.
No ignored local helper is imported by this portable public source freezer.
"""
import argparse,copy,hashlib,json
from pathlib import Path
S=Path(__file__).resolve().parents[1]
NAME='core-workforce-foundations-unapproved-time'
ORIGINAL=S/'expansion/plans'/ (NAME+'-candidate-20261029')
DEST=S/'expansion/plans'/ (NAME+'-capture-freeze-20261029')
INPUTS={NAME+'.candidate.json':'c294f6adc376160db6840ab5c939760a995d1c8ad2498084e44b06cf116ad780',
 'narration.txt':'5a4d5482b16327541eaae3a0c001956067cc812805017f685cd676729ff53307',
 'captures.reviewed.json':'0e5a20a6eb5a37a3c244038cbc4685bf4bdf0dd4c7ad2549f95d4d811b0a702e',
 'literal-source-review.json':'23bb0492079c13e536f767ce507680793db99714f0cb925bfd406d72bffecec6',
 'screen-sequence.untimed.json':'57692a1bc25cafde251202d71fcc43c1e4c467f207f75cd3a938b451e6eb8c24',
 'source-evidence.json':'68f8bba2eb40a39c64b2cdbe2f8295a8fc88efec0ed7b0f0783444923eb69591',
 'manual-replay-scenario.json':'bdb385107dfa210530c1199b790fa0d7b23b4d5e80749ca6ac5d460bb610d1cc',
 'preflight.json':'9b869734df3ea51fb96283aa6f2d8bdf0da2c4dc519e49d945311050b43be9d1'}
AUDIT=S/'expansion/audits/core-workforce-foundations-full-known-privacy-20261029.json'
AUDIT_SHA='702c4c88ca490d2e61e7db731a6d376d61de98a71fe69643ce2127b05ac41fc3'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def encoded(v):return (json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode()
def need(ok,message):
 if not ok:raise ValueError(message)

def prepare():
 for name,digest in INPUTS.items():need(sha(ORIGINAL/name)==digest,'Reviewed candidate changed: '+name)
 need(sha(AUDIT)==AUDIT_SHA,'Full known-value audit changed.')
 audit=json.loads(AUDIT.read_text());need(audit['known_private_values_checked']==17 and audit['findings']==[] and audit['files_scanned']==95,'Require actual17value/95file clean audit.')
 for file,digest in audit['file_pins'].items():need(sha(S/file)==digest,'Audited source changed: '+file)
 lesson=json.loads((ORIGINAL/(NAME+'.candidate.json')).read_text());captures=json.loads((ORIGINAL/'captures.reviewed.json').read_text());sequence=json.loads((ORIGINAL/'screen-sequence.untimed.json').read_text())
 need(len(lesson['scenes'])==15 and len(captures['screenshots'])==31 and len(sequence['spans'])==34,'Held source inventory changed.')
 need(len(lesson['sector_examples'])==6 and lesson['scenes'][-1]['narration'].endswith('before further review.'),'Parent-reviewed sector conclusion changed.')
 exact='\n\n'.join(sc['narration'] for sc in lesson['scenes'])+'\n'
 need(exact.encode()==(ORIGINAL/'narration.txt').read_bytes(),'Narration differs from parent-read exact text.')
 files={};mapping={};byid={r['id']:r for r in captures['screenshots']}
 for r in captures['screenshots']:
  need(r['capture_review']['passed'] is True and r['capture_review']['sha256']==r['sha256'],'Actual source review missing.')
  for field,hfield,folder in [('file','sha256','images'),('dom_file','dom_sha256','dom')]:
   old=r[field];p=S/old;need(sha(p)==r[hfield],'Raw asset changed: '+old)
   name=folder+'/'+Path(old).name;files[name]=p.read_bytes();r['original_'+field]=old
   r[field]=(DEST/name).relative_to(S).as_posix();mapping[old]={'file':r[field],'sha256':r[hfield]}
 for sc in lesson['scenes']:
  refs=sc['capture_evidence']['capture_refs'];need(set(refs)<=set(byid),'Unknown source ID.')
  need(set(sc['required_labels'])<={label for ident in refs for label in byid[ident]['visible_labels']},'Unseen named control: '+sc['id'])
 lesson.update(status='source_frozen_for_parent_approved_natural_narration',narration_frozen=True,
               parent_whole_script_approved=True,source_complete=True,publication_approved=False,
               narration_word_count=1047)
 review={'kind':'parent_whole_Workforce_script_and_source_order_approval','reviewer':'Codex parent whole-script and source-order reviewer',
  'reviewed_at':'2026-10-29T04:15:03Z','source_only':True,'parent_whole_script_approval':True,
  'method':'Parent read the complete1047word narration, all15required-label lists and capture orders, and accepted this bounded concept and specific field/Save/readback sequence. Parent had previously viewed all41original returned images. Agent independently viewed the31selected1434x773original JPEGs and curated only literal foreground controls. No new parent original-pixel inspection time is invented by this freeze.',
  'evidence':'Explicit parent task message authorized this NEW guarded source freeze after full-script review and the separate actual17known-value audit.',
  'unchanged_narration_sha256':INPUTS['narration.txt'],'original_candidate_sha256':INPUTS[NAME+'.candidate.json'],
  'scope':'EmployerNotdeclared; firstILestablishment; Caseyexistingworker; one-dayVolunteerperiod/assignment;2RegularhoursApprovedOFF and freshreadbacks. No pay/cost/coverage/attendance outcome.',
  'privacy_audit':{'file':AUDIT.relative_to(S).as_posix(),'sha256':AUDIT_SHA},'video_or_publication_approved':False}
 files.update({NAME+'.narrated-source.json':encoded(lesson),'narration.frozen.txt':exact.encode(),
  'captures.reviewed.json':encoded(captures),'screen-sequence.untimed.json':encoded(sequence),
  'parent-script-review.json':encoded(review),'full-known-privacy-audit.json':AUDIT.read_bytes()})
 for name in ['literal-source-review.json','source-evidence.json','manual-replay-scenario.json','preflight.json']:
  files['original-review/'+name]=(ORIGINAL/name).read_bytes()
 freeze={'kind':'immutable_parent_approved_Workforce_source_and_narration_freeze','lesson_id':NAME,
  'source_only':True,'parent_whole_script_approved':True,'publication_approved':False,'audio_or_timing_assigned':False,
  'original_candidate':{'file':ORIGINAL.relative_to(S).as_posix(),'inputs':INPUTS},
  'narrated_source_sha256':hashlib.sha256(files[NAME+'.narrated-source.json']).hexdigest(),
  'narration_sha256':INPUTS['narration.txt'],'scenes':15,'narration_words':1047,'source_images':31,'untimed_spans':34,
  'six_sectors_companion_and_spoken':True,'public_package_path_map':mapping,
  'freeze_files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()},
  'limits':['Candidate/raw41pairs remain unchanged. Only this new source package rebases the31copied image/DOM paths.',
   'Offscreen and clipped-control exclusions are retained; no full external-source/id pixel proof.',
   'Actual audio generation/listening, timing, encodedframes, playback and publication gates remain separate.']}
 files['source-freeze.json']=encoded(freeze)
 return files

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze',action='store_true');args=p.parse_args();files=prepare()
 if args.freeze:
  need(not DEST.exists(),'Preserve existing freeze; output already exists.');DEST.mkdir(parents=True)
  for name,data in files.items():target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 print(json.dumps({'source_only':True,'frozen':args.freeze,'scenes':15,'words':1047,'source_images':31,'untimed_spans':34,'known_private_values_checked':17,'privacy_findings':0,'narrated_source_sha256':hashlib.sha256(files[NAME+'.narrated-source.json']).hexdigest(),'narration_sha256':INPUTS['narration.txt'],'source_freeze_sha256':hashlib.sha256(files['source-freeze.json']).hexdigest(),'files':len(files),'publication_approved':False},indent=2))
if __name__=='__main__':main()
