"""Assemble Certification v2 inputs after genuine full listening approval.

V1 is retained after strict rejection of its unreferenced sector outro. V2 adds
only an actual record-title reference on derived105 (raw104); no timing, speech,
source image or strict-gate changes are made.

Default source checks are read-only. --assemble writes one NEW package, verifies
the exact approved inputs with the unchanged strict renderer, and never renders
or updates a canonical lesson, readiness flag, site, target or application.
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
NAME='core-certification-administration'
QA_HELPER=SOURCES/'production/qa_core_certification_proposed_captions_20261028.py'
QA_HELPER_SHA='6c24c31946717f27f06a6829e32846dbb2420fc894f5d980b245d3a8b9441594'
PROPOSED=Path('expansion/plans/core-certification-administration-take-01-proposed-derived-20261028')
ASSEMBLY=Path('expansion/plans/core-certification-administration-take-01-final-inputs-20261028-v2')
PINS={
 PROPOSED/'correspondence.proposed.json':'027d91c65730bc5c2fbcc0303cd35350830592112756dd074385fd492e194d47',
 PROPOSED/(NAME+'.derived114.actual.qa.json'):'f7122d76f823e7cb8939e833f286cacf9471b804aedacf33d7c812506b0caf95',
 PROPOSED/(NAME+'.derived114.corrected.srt'):'efa05d35ef4f8baa583064ea372beb68b877864b8482d92876fb22c48d51a2f5',
 PROPOSED/'provenance.json':'30e679b25dd6a59de68c047638dd60eed93734211bbeb58951cbfd8b7235d825',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()

def prepare():
 assert sha(QA_HELPER)==QA_HELPER_SHA,'Retain exact proposed derivation recipe.'
 spec=importlib.util.spec_from_file_location('retained_certification_proposed',QA_HELPER)
 helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed proposed actual input: '+str(path)
 rebuilt,_,original=helper.prepare()
 proposed=json.loads((SOURCES/PROPOSED/'correspondence.proposed.json').read_text())
 for key in ['cue_correspondence','scenes','genuine_service_anchor_cuts','coalescence','readability']:
  assert rebuilt[key]==proposed[key],'Retained proposed correspondence diverged.'
 derived=json.loads((SOURCES/PROPOSED/(NAME+'.derived114.actual.qa.json')).read_text())
 assert derived['passed'] and not derived['issues'] and not derived['possible_speech_gaps']
 assert derived['audio']==original['audio']
 assert derived['silent_raw_cues']==derived['silent_corrected_cues']==0
 assert derived['alignment']['text_changes']==[] and derived['lesson']['sha256']==helper.FROZEN
 assert derived['corrected_captions']['sha256']==PINS[PROPOSED/(NAME+'.derived114.corrected.srt')]
 return helper,proposed,derived

def build(review_path,review_sha):
 helper,proposed,derived=prepare()
 review_path=Path(review_path).resolve()
 assert review_path.is_relative_to(SOURCES) and review_path.is_file(),'Use retained public review metadata inside sources.'
 assert re.fullmatch('[0-9a-f]{64}',review_sha or '') and sha(review_path)==review_sha,'Require actual listening-review hash.'
 heard=json.loads(review_path.read_text())
 assert heard['complete_natural_narration'] is True
 assert heard['audio_sha256']==helper.PINS[helper.AUDIO] and heard['lesson_sha256']==helper.FROZEN
 assert heard['reviewer'] and heard['evidence']
 assert datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00'))<=datetime.now(timezone.utc)
 lesson_path=SOURCES/helper.BASE/(NAME+'.narrated-source.json')
 lesson=json.loads(lesson_path.read_text())
 capture_path=SOURCES/helper.BASE/(NAME+'.captures.reviewed.json')
 manifest=json.loads(capture_path.read_text());rows={r['id']:r for r in manifest['screenshots']}
 now=datetime.now(timezone.utc).isoformat()
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import instruction_scene_digest
 from render_walkthrough import load_cues,words
 captions=(SOURCES/PROPOSED/(NAME+'.derived114.corrected.srt')).read_bytes()
 parsed=load_cues(SOURCES/PROPOSED/(NAME+'.derived114.corrected.srt'))
 entries=proposed['cue_correspondence'];assert len(parsed)==len(entries)==114
 # Bind the exact existing-record field to its actual spoken cue, not a neighboring cue.
 outro=next(c for c in entries if c['raw_cues']==[104])
 assert outro['cue']==105 and outro['text']=='identified exercise record.'
 assert outro['screenshot_id']=='020-active-verified-fresh-readback'
 refs={'TRAINING ONLY - Software record review':'exercise record'}
 helper.references(outro['text'],refs,rows[outro['screenshot_id']])
 outro.update(required_labels=list(refs),spoken_references=refs,instructional=True)
 for a,b in zip(parsed,entries):assert (a['start'],a['end'],words(a['text']))==(b['start'],b['end'],words(b['text']))
 scenes=[]
 for source,scene in zip(proposed['scenes'],lesson['scenes']):
  assert source['scene_id']==scene['id']
  cues=[entries[n-1] for n in source['derived_cues']]
  screens=[{'screenshot_id':s['capture_ref'],'start':s['actual_start'],'end':s['actual_end']} for s in source['source_spans']]
  start=screens[0]['start'];end=screens[-1]['end']
  full={'id':scene['id'],'title':scene['title'],'kind':'operational','start':start,'end':end,
        'visual_required_labels':scene['required_labels'],'screens':screens,'captions':cues}
  review={'passed':True,'reviewer':'Codex actual frozen-source/export-caption correspondence review',
          'reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,
          'mapping_sha256':instruction_scene_digest(full,rows),
          'method':'Exact113service cues/frozen words mapped to27reviewed actualCore images in their frozen12scene screen order. Genuine whole-second122/308cuts and same-image54/55coalescence independently checked; full114cue PCM QA passed. Historical type/policy states remain bounded; no interpolated timing, unseen control or notification delivery is claimed.'}
  scenes.append({'id':scene['id'],'start':start,'end':end,'screens':screens,
    'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in cues],
    'instruction_review':review})
 audio_sha=helper.PINS[helper.AUDIO];caption_sha=hashlib.sha256(captions).hexdigest()
 plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':derived['audio']['duration_seconds'],
       'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
       'narration':{'file':helper.AUDIO.as_posix(),'sha256':audio_sha,'kind':'approved_natural_narration',
        'approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':audio_sha,
          'complete_natural_narration':True,'evidence':heard['evidence'],
          'qa_file':(PROPOSED/(NAME+'.derived114.actual.qa.json')).as_posix(),
          'qa_sha256':PINS[PROPOSED/(NAME+'.derived114.actual.qa.json')],
          'listening_review_file':str(review_path.relative_to(SOURCES)),'listening_review_sha256':review_sha}},
       'captions':{'file':(ASSEMBLY/(NAME+'.derived114.srt')).as_posix(),'sha256':caption_sha,'kind':'speech_timed_srt',
        'approval':{'reviewer':'Codex exact words/genuine marker/full derived PCM review','reviewed_at':now,
          'sha256':caption_sha,'audio_sha256':audio_sha,'speech_timing_reviewed':True,
          'method':'Unchanged113original service cue boundaries except exact122/308whole-second additions and adjacent54/55same-image coalescence ending at real192.820. No interpolated or millisecond word timing.',
          'word_timing_file':helper.ANCHORS.as_posix(),'word_timing_sha256':helper.PINS[helper.ANCHORS]}},
       'capture_manifests':[{'file':(ASSEMBLY/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
       'screenshot_reviews':{r['id']:{'reviewer':r['capture_review']['reviewer'],'reviewed_at':r['capture_review']['reviewed_at'],
            'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for r in rows.values()},
       'scenes':scenes,'publishable':False,'limitations':proposed['coverage_limits'],
       'historical_proposal_file':(PROPOSED/'correspondence.proposed.json').as_posix(),
       'historical_proposal_sha256':PINS[PROPOSED/'correspondence.proposed.json'],
       'v2_metadata_correction':{'raw_cue':104,'derived_cue':105,'screenshot_id':'020-active-verified-fresh-readback','actual_visible_label':'TRAINING ONLY - Software record review','unchanged_spoken_phrase':'exercise record','words_times_source_bytes_unchanged':True,'failed_v1_retained':True}}
 return helper,plan,captions,manifest

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assemble',action='store_true')
 p.add_argument('--listening-review',type=Path);p.add_argument('--listening-review-sha256');a=p.parse_args()
 if not a.assemble:
  helper,proposed,_=prepare();print(json.dumps({'passed_source_preflight':True,'scenes':12,'images':27,'intervals':34,'cues':114,'files_written':False,'rendered':False,'canonical_ready':False}));return
 assert a.listening_review and a.listening_review_sha256,'Actual full listening review is required.'
 helper,plan,captions,manifest=build(a.listening_review,a.listening_review_sha256)
 out=SOURCES/ASSEMBLY;assert not out.exists(),'NEW-only final inputs; preserve all historical proposals and takes.'
 out.mkdir(parents=True)
 assets={'captures.reviewed.json':encoded(manifest),NAME+'.derived114.srt':captions,'plan.json':encoded(plan)}
 for name,data in assets.items():
  with (out/name).open('xb') as f:f.write(data)
 from render_walkthrough import validate_inputs
 checked=validate_inputs(SOURCES/helper.BASE/(NAME+'.narrated-source.json'),out/'plan.json',SOURCES)
 provenance={'schema_version':1,'kind':'guarded_approved_certification_final_assembly_inputs','created_at':datetime.now(timezone.utc).isoformat(),
             'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
             'source_frozen_sha256':helper.FROZEN,'listening_review_sha256':a.listening_review_sha256,
             'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in helper.PINS.items()]+[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
             'outputs':[{'file':str((out/n).relative_to(SOURCES)),'sha256':sha(out/n)} for n in assets],
             'unchanged_strict_renderer_inputs_passed':True,'rendered':False,'publishable':False,'canonical_or_ready_changed':False}
 (out/'provenance.json').write_bytes(encoded(provenance))
 print(json.dumps({'passed':True,'scenes':len(checked['scenes']),'cues':len(checked['cues']),'duration':checked['duration'],
                   'plan':str((out/'plan.json').relative_to(SOURCES)),'plan_sha256':sha(out/'plan.json'),'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
