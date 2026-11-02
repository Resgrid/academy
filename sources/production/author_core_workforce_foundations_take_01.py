"""Guarded Workforce final-input authoring after genuine User listening review.

Default is source-only/read-only. --assemble additionally requires the exact
SHA256 of the real URL-free listening review. No speech generation, rendering,
qualification, canonical lesson adoption or website build occurs here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-workforce-foundations-unapproved-time'
HELPER=SOURCES/'production/prepare_core_workforce_proposed_correspondence_20261029.py'
HELPER_SHA='7ca10cfa6d5994cb1d962c8d2b3544f41030aa02109a28966df08d96b9e6603b'
PROPOSED=Path('expansion/plans')/(NAME+'-take-01-proposed-20261029')
FINAL=Path('expansion/plans')/(NAME+'-take-01-final-inputs-20261029')
LISTENING=Path('expansion/audio')/(NAME+'.listening-review.json')
PARENT=Path('expansion/audits/core-workforce-proposed-timing-parent-review-20261029.json')
PINS={
 PROPOSED/'correspondence.proposed.json':'9bf7b396fcc2c26b4616fcba2f1b0edec39b665ca198e03b3f8a621560b928bf',
 PROPOSED/'captures.proposed.json':'56de4db097076d11ceaf1831c13309e86ee030ecbee5d8f5522998738f884cae',
 PROPOSED/(NAME+'.derived126.corrected.srt'):'7831cd35eebd9c6a0b632f727c5de16ec7fd1a6754fa1e26acee3a6961e217db',
 PROPOSED/(NAME+'.derived126.proposed.srt'):'7831cd35eebd9c6a0b632f727c5de16ec7fd1a6754fa1e26acee3a6961e217db',
 PROPOSED/(NAME+'.derived126.actual.qa.json'):'d41eb8e94926d6455aedf526561d9f7dbfc29a3d397f3fb288d92effd2f92d28',
 PROPOSED/'cue-screen-correspondence.txt':'7322161c39330d185df4247855ee6871ff8deff066822599cc628e4137163000',
 PROPOSED/'provenance.json':'fc6da20411a0e424b302494aba6e118fe00a83e187a2732b0fb2536a97d62cd0',
 Path('expansion/audits/core-workforce-proposed-timing-source-review-20261029.json'):'aa016019187e71f1ca09111f46a140eb6c22d124a96597f826bee8e64efeea79',
 PARENT:'b75f87f07b5f1a30b57f0fc89d7c5df40b74f1a85e6354eb1cb64ec029b327a2',
}

def sha(path):
 digest=hashlib.sha256()
 with Path(path).open('rb') as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
 return digest.hexdigest()

def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def preflight():
 assert sha(HELPER)==HELPER_SHA,'Changed proposed source/word-marker helper.'
 spec=importlib.util.spec_from_file_location('workforce_retained_proposal',HELPER)
 helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed reviewed proposed input: '+str(path)
 rebuilt,_,manifest=helper.prepare()
 proposed=json.loads((SOURCES/PROPOSED/'correspondence.proposed.json').read_text())
 for key in ['scenes','cue_correspondence','genuine_service_anchor_rebalances','readability','supplemental_literal_reviews','explicit_timing_choices']:
  assert rebuilt[key]==proposed[key],'Proposed source/caption correspondence diverged: '+key
 assert encoded(manifest)==(SOURCES/PROPOSED/'captures.proposed.json').read_bytes()
 qa=json.loads((SOURCES/PROPOSED/(NAME+'.derived126.actual.qa.json')).read_text())
 original=json.loads((SOURCES/helper.QA).read_text())
 assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
 assert qa['alignment']['text_changes']==[] and qa['silent_raw_cues']==qa['silent_corrected_cues']==0
 assert qa['audio']==original['audio'] and qa['lesson']['sha256']==helper.FROZEN
 assert qa['corrected_captions']['sha256']==PINS[PROPOSED/(NAME+'.derived126.corrected.srt')]
 parent=json.loads((SOURCES/PARENT).read_text())
 assert parent['reviewer']=='Parent/root' and parent['compact_sha256']==PINS[PROPOSED/'cue-screen-correspondence.txt']
 assert parent['correspondence_sha256']==PINS[PROPOSED/'correspondence.proposed.json']
 assert parent['accepted']=={'cues':126,'source_images':31,'screen_intervals':35,'whole_second_markers':[43,77,227],'source004_and017_literal_supplements':True,'frozen_narration_unchanged':True}
 assert parent['actual_user_listening_review_still_required'] is True
 return helper,proposed,qa,parent,manifest

def validate_listening_record(record,source_sha,audio_sha,qa_checked_at,now=None):
 """Validate retained named User review without asserting machine proof of listening."""
 assert isinstance(record,dict),'Listening review must be an authored object.'
 serialized=json.dumps(record,ensure_ascii=False)
 assert not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)',serialized),'Listening review must be URL-free.'
 assert record.get('reviewer')=='User','Require the actual User listening review; technical agent QA is separate.'
 assert record.get('complete_natural_narration') is True,'Complete natural narration was not approved.'
 assert record.get('lesson_sha256')==source_sha and record.get('audio_sha256')==audio_sha,'Listening review source/audio identity differs.'
 evidence=record.get('evidence')
 assert isinstance(evidence,str) and re.search(r'(?i)\b(?:complete|full)\b',evidence) and re.search(r'(?i)\bnatural\b',evidence),'Retain the actual full-listening request and human response.'
 checked=datetime.fromisoformat(record['reviewed_at'].replace('Z','+00:00'))
 earliest=datetime.fromisoformat(qa_checked_at.replace('Z','+00:00'))
 assert checked.tzinfo is not None and earliest.tzinfo is not None
 assert earliest<=checked<=(now or datetime.now(timezone.utc)),'Review chronology must follow the actual audio QA, never a future review.'
 return record

def listening(helper,expected_sha):
 assert isinstance(expected_sha,str) and re.fullmatch('[a-f0-9]{64}',expected_sha),'Supply the exact real listening-review SHA256 after the human reply.'
 file=SOURCES/LISTENING
 assert file.is_file(),'Actual URL-free User listening review has not arrived; final authoring is blocked.'
 assert sha(file)==expected_sha,'Changed or unreviewed listening receipt.'
 original=json.loads((SOURCES/helper.QA).read_text())
 return validate_listening_record(json.loads(file.read_text()),helper.FROZEN,helper.PINS[helper.AUDIO],original['checked_at'])

def build(expected_listening_sha):
 helper,proposed,qa,parent,manifest=preflight()
 heard=listening(helper,expected_listening_sha)
 from render_walkthrough import load_cues,words
 from verify_capture_evidence import instruction_scene_digest
 lesson=json.loads((SOURCES/helper.BASE/(NAME+'.narrated-source.json')).read_text())
 rows={r['id']:r for r in manifest['screenshots']};entries=proposed['cue_correspondence']
 captions=(SOURCES/PROPOSED/(NAME+'.derived126.corrected.srt')).read_bytes()
 parsed=load_cues(SOURCES/PROPOSED/(NAME+'.derived126.corrected.srt'))
 assert len(parsed)==len(entries)==126
 for a,b in zip(parsed,entries):assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
 now=datetime.now(timezone.utc).isoformat();scenes=[]
 for authored,source in zip(lesson['scenes'],proposed['scenes']):
  assert authored['id']==source['scene_id']
  cues=[entries[n-1] for n in source['cue_numbers']]
  screens=[{'screenshot_id':s['capture_ref'],'start':s['actual_start'],'end':s['actual_end']} for s in source['source_spans']]
  full={'id':authored['id'],'title':authored['title'],'kind':'operational','start':screens[0]['start'],'end':screens[-1]['end'],'visual_required_labels':authored['required_labels'],'screens':screens,'captions':cues}
  review={'passed':True,'reviewer':'Codex actual Workforce frozen-source/cue correspondence reviewer','reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(full,rows),
   'method':'Retained31 actual original Core images, all126 actual service cues and exact frozen words mapped to35 readable holds. Parent explicitly read every compact cue/image line and accepted43/77/227 genuine one-second word markers,019 correct employment Save timing and personally observed004/017 literal supplements. This is source/caption review; encoded-frame and real playback reviews are still required. No payroll, legal-coverage or attendance outcome is asserted.'}
  scenes.append({'id':authored['id'],'start':full['start'],'end':full['end'],'screens':screens,'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in cues],'instruction_review':review})
 audio_sha=helper.PINS[helper.AUDIO];caption_sha=hashlib.sha256(captions).hexdigest()
 plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':qa['audio']['duration_seconds'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
  'narration':{'file':helper.AUDIO.as_posix(),'sha256':audio_sha,'kind':'approved_natural_narration','approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':audio_sha,'complete_natural_narration':heard['complete_natural_narration'],'evidence':heard['evidence'],'qa_file':(PROPOSED/(NAME+'.derived126.actual.qa.json')).as_posix(),'qa_sha256':PINS[PROPOSED/(NAME+'.derived126.actual.qa.json')],'listening_review_file':LISTENING.as_posix(),'listening_review_sha256':expected_listening_sha}},
  'captions':{'file':(FINAL/(NAME+'.derived126.srt')).as_posix(),'sha256':caption_sha,'kind':'speech_timed_srt','approval':{'reviewer':'Codex exact words/genuine marker/full derived PCM review','reviewed_at':now,'sha256':caption_sha,'audio_sha256':audio_sha,'speech_timing_reviewed':True,'method':'Retained126 service cues, three adjacent-pair rebalances at actual43/77/227 whole-second word markers. Exact word order/count and each pair outer bounds retained; no speech/operation interpolation or finer word accuracy asserted.','word_timing_file':helper.ANCHORS.as_posix(),'word_timing_sha256':helper.PINS[helper.ANCHORS]}},
  'capture_manifests':[{'file':(FINAL/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
  'screenshot_reviews':{r['id']:{'reviewer':r['capture_review']['reviewer'],'reviewed_at':r['capture_review']['reviewed_at'],'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for r in rows.values()},
  'scenes':scenes,'publishable':False,'parent_timing_review':{'file':PARENT.as_posix(),'sha256':PINS[PARENT],'reviewer':'Parent/root','compact_file':(PROPOSED/'cue-screen-correspondence.txt').as_posix(),'compact_sha256':PINS[PROPOSED/'cue-screen-correspondence.txt'],'evidence':parent['evidence']},
  'proposed_correspondence_file':(PROPOSED/'correspondence.proposed.json').as_posix(),'proposed_correspondence_sha256':PINS[PROPOSED/'correspondence.proposed.json'],
  'limitations':['Fictional software records only; no verified attendance, payment, legal coverage or compensation/cost-run result.','External-source/id inputs visibly clip their values; no full-reference value is claimed.','All raw images/DOM/narration/audio remain unchanged;004/017 literal supplements are separate reviewed observations.','Actual encoded-frame, caption/pixel and beginning/middle/end browser playback review remain required after a separate render.']}
 return helper,plan,captions,manifest

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assemble',action='store_true');parser.add_argument('--listening-review-sha256');args=parser.parse_args()
 if not args.assemble:
  helper,proposed,_,_,_=preflight()
  if args.listening_review_sha256:listening(helper,args.listening_review_sha256)
  print(json.dumps({'source_preflight':True,'scenes':15,'sources':31,'cues':126,'intervals':35,'requires_actual_user_listening_review':True,'listening_receipt_present':(SOURCES/LISTENING).is_file(),'final_inputs_written':False,'rendered':False,'canonical_ready':False}));return
 assert args.listening_review_sha256,'--assemble requires the hash of the actual User listening review.'
 helper,plan,captions,manifest=build(args.listening_review_sha256)
 out=SOURCES/FINAL;assert not out.exists(),'Use NEW-only final inputs; preserve every earlier source, proposal and take.'
 out.mkdir(parents=True)
 assets={'captures.reviewed.json':encoded(manifest),NAME+'.derived126.srt':captions,'plan.json':encoded(plan)}
 for name,body in assets.items():
  with (out/name).open('xb') as stream:stream.write(body)
 from render_walkthrough import validate_inputs
 validated=validate_inputs(SOURCES/helper.BASE/(NAME+'.narrated-source.json'),out/'plan.json',SOURCES)
 provenance={'kind':'guarded_Workforce_final_source_inputs_after_actual_listening','created_at':datetime.now(timezone.utc).isoformat(),'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},'source_frozen_sha256':helper.FROZEN,'listening_review_sha256':args.listening_review_sha256,'parent_timing_review_sha256':PINS[PARENT],'input_hashes':{**{str(p):h for p,h in helper.PINS.items()},**{str(p):h for p,h in PINS.items()}},'outputs':{name:sha(out/name) for name in assets},'unchanged_strict_renderer_inputs_passed':True,'rendered':False,'publishable':False,'canonical_or_ready_or_site_changed':False}
 (out/'provenance.json').write_bytes(encoded(provenance))
 print(json.dumps({'strict_inputs_passed':True,'scenes':len(validated['scenes']),'cues':len(validated['cues']),'duration':validated['duration'],'plan':str((out/'plan.json').relative_to(SOURCES)),'plan_sha256':sha(out/'plan.json'),'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
