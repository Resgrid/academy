"""Bind genuine parent Personnel playback and completed encoded-frame review.

Default verifies retained bytes and strict evidence without writing; once final
evidence exists it also runs the unchanged public export preflight.
--qualify writes NEW evidence/proofs/report only. Never adopts a canonical lesson,
builds a website or starts a browser. Actual parent observations are indispensable.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];SOURCES=ROOT/'sources'
NAME='core-personnel-administration'
TAKE=SOURCES/'expansion/rendered/core-personnel-administration-take-01'
FROZEN=SOURCES/'expansion/plans/core-personnel-administration-capture-freeze-20261028'/ (NAME+'.narrated-source.json')
PLAN=SOURCES/'expansion/plans/core-personnel-administration-take-01-final-inputs-20261028/plan.json'
RAW=ROOT/'_reports/personnel-browser-proof-20261029.raw.json'
MASTER='8b49de638b6db361e49b701a3e6e2492a6defe95f691c7eeabf9a4aac0bc8c8d'
EXPECTED=[('beginning',11.309361,26.144561,'d2fe3de2c634e98b467f9b38fa5158e575500d3dd928400d4c4959732b8c7a89'),('middle',188.488082,202.522886,'f3f4678b1efda3c4f589ec2bae93b320ebb46def0a5b396651140c822871c13d'),('end',346.818025,357.667745,'b01bbb4980f773372a21b1f6533f6a094007f13d97acd8b24722c5960c1800a0')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
def prepare():
 assert sha(TAKE/(NAME+'.mp4'))==MASTER
 assert sha(FROZEN)=='e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8'
 assert sha(PLAN)=='67b18be443a014e6fef31ada7fbd77fb28ad7bb6a210c29efc0d001a7c442bce'
 assert sha(TAKE/'encoded-frame-review.json')=='016b5701d5b2894140d0ff1bd6c63ee4ac0ef6eba639625b0957d778cf8f7d18'
 assert sha(TAKE/'evidence.frames-reviewed.json')=='eeca90453e4def52f728876ed326f9fa11e8b10c2e87b3ca242eddce18e35edb'
 assert sha(SOURCES/'expansion/audio/core-personnel-administration.listening-review.json')=='025a4cd0d6c4729f2a824739f79d6a805fcfd7dd789dea616693a0aeae33f25b'
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import verify_document,_image_dimensions
 from expansion_site import lesson_content_digest,_prepare
 rows=json.loads(RAW.read_text());assert len(rows)==3
 for row,(position,previous,current,digest) in zip(rows,EXPECTED):
  assert (row['position'],row['previous_time'],row['current_time'],row['video_sha256'],row['screenshot']['sha256'])==(position,previous,current,MASTER,digest)
  assert row['media_error'] is None and row['console_errors']==[] and row['ready_state']==4 and row['network_state']==1
  assert row['video_width']==1920 and row['video_height']==1080 and current>previous
  p=SOURCES/row['screenshot']['file'];assert sha(p)==digest
  width,height=_image_dimensions(p);assert (width,height)==(1280,720)
  row['screenshot'].update(width=width,height=height)
 evidence=json.loads((TAKE/'evidence.frames-reviewed.json').read_text());evidence['browser_playback']=rows
 evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':False,
  'parent_review':'Root personally viewed all3genuine IAB native playback JPEGs and observed advancing error-free actual Core screens with current captions. This agent independently viewed the exact3JPEGs; no browser interaction by this agent. PrivateQA nativeCC duplicates are intentional and the public player keeps nativeCC off by default.',
  'parent_raw_observation_sha256':sha(RAW),'canonical_or_ready_changed':False}
 lesson=json.loads(FROZEN.read_text());authoring=lesson_content_digest(lesson)
 assert authoring==evidence['authoring_sha256']=='fcd317387b02b75b97e9802b518ebc3a40de82823bf1661c4b4e177bbaa08e35'
 report=verify_document(evidence,SOURCES);assert report['passed'] and not report['issues'],report
 return rows,evidence,report,lesson

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--qualify',action='store_true');a=p.parse_args()
 rows,evidence,report,lesson=prepare()
 from expansion_site import _prepare
 if a.qualify:
  assert not (TAKE/'evidence.reviewed.json').exists() and not (TAKE/'playback/proofs.json').exists() and not (TAKE/'qualification.json').exists(),'New-only qualification.'
  for rel,obj in [('playback/proofs.json',rows),('evidence.reviewed.json',evidence)]:
   with (TAKE/rel).open('xb')as f:f.write(encoded(obj))
  candidate=dict(lesson,export_ready=True,publication_mode='video',evidence_file=str((TAKE/'evidence.reviewed.json').relative_to(SOURCES)))
  _prepare(candidate,SOURCES)
  q={'passed':True,'lesson_id':NAME,'issues':[],'public_export_preflight':'passed','parent_actual_browser_proofs':'all3genuinefreshparentIABJPEGsandobservationsretained',
   'rendered_intervals':38,'caption_regions_reviewed':116,'source_images':26,'authoring_sha256':evidence['authoring_sha256'],
   'frozen_source_sha256':sha(FROZEN),'video_sha256':MASTER,'evidence_sha256':sha(TAKE/'evidence.reviewed.json'),
   'encoded_frame_review_sha256':sha(TAKE/'encoded-frame-review.json'),'current_validator_sha256':sha(ROOT/'scripts/verify_capture_evidence.py'),
   'current_exporter_sha256':sha(ROOT/'scripts/expansion_site.py'),'canonical_or_ready_changed':False,'site_or_target_changed':False,'root_adoption_pending':True,
   'current_public_listening_review_sha256':sha(SOURCES/'expansion/audio/core-personnel-administration.listening-review.json'),'current_plan_sha256':sha(PLAN)}
  with (TAKE/'qualification.json').open('xb')as f:f.write(encoded(q))
 elif (TAKE/'evidence.reviewed.json').exists():
  assert (TAKE/'evidence.reviewed.json').read_bytes()==encoded(evidence)
  _prepare(dict(lesson,export_ready=True,publication_mode='video',evidence_file=str((TAKE/'evidence.reviewed.json').relative_to(SOURCES))),SOURCES)
 print(json.dumps({'passed':True,'written':a.qualify,'rendered_intervals':38,'caption_regions':116,'parent_actual_browser_proofs':3,'canonical_or_site_changed':False}))
if __name__=='__main__':main()
