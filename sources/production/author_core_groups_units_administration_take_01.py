"""Guarded Groups/Units assembly after actual listening and parent timing review.

Default is read-only. --assemble creates NEW source inputs and runs unchanged
strict renderer validation. Rendering, canonical adoption and site export are
separate operations. Frozen narration, audio and original captions stay intact.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-groups-units-administration'
QA_HELPER=SOURCES/'production/qa_core_groups_units_proposed_captions_20261028.py'
QA_HELPER_SHA='f1e973e1604821ca3ec40295bca0e7212bad830269eb9e1cb9ea78878d7551ec'
PROPOSED=Path('expansion/plans/core-groups-units-administration-take-01-proposed-derived-20261028')
ASSEMBLY=Path('expansion/plans/core-groups-units-administration-take-01-final-inputs-20261028')
PINS={
 PROPOSED/'correspondence.proposed.json':'17d150abf2816cd67fd3564464183f52c20a572471ca8cda1815a89faca84a79',
 PROPOSED/(NAME+'.derived132.actual.qa.json'):'4e12397c1965e86617def40f6eebaca7b1d116a269b225ccc2047020e17c6863',
 PROPOSED/(NAME+'.derived132.corrected.srt'):'6250264b6cadf69e05cd39e78b5025f977adce46d30e099839df325943835d22',
 PROPOSED/'cue-screen-correspondence.txt':'b4418995ad9e9c446d1bf5255d46154d3caeb5f372a075dba86ee9c6dd8afced',
 PROPOSED/'provenance.json':'b4ba1e21ef5311a0c7945c14a6dd10f8bbf09a7869e44551431b60c407761524',
 Path('expansion/audits/core-groups-units-proposed-timing-source-review-20261028.json'):'b2abba9d0fc47efea6663eb0dcdd1eb72ad0ac26199c53815410eb91764aa773',
}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def prepare():
 assert sha(QA_HELPER)==QA_HELPER_SHA,'Retain exact proposed derivation recipe.'
 spec=importlib.util.spec_from_file_location('retained_groups_units_proposal',QA_HELPER)
 helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed proposed actual input: '+str(path)
 rebuilt,_,original=helper.prepare()
 proposed=json.loads((SOURCES/PROPOSED/'correspondence.proposed.json').read_text())
 for key in ['cue_correspondence','scenes','genuine_service_anchor_cuts','readability','explicit_timing_choices']:
  assert rebuilt[key]==proposed[key],'Retained proposed correspondence diverged.'
 derived=json.loads((SOURCES/PROPOSED/(NAME+'.derived132.actual.qa.json')).read_text())
 assert derived['passed'] and not derived['issues'] and not derived['possible_speech_gaps']
 assert derived['audio']==original['audio'] and derived['silent_raw_cues']==derived['silent_corrected_cues']==0
 assert derived['alignment']['text_changes']==[] and derived['lesson']['sha256']==helper.FROZEN
 assert derived['corrected_captions']['sha256']==PINS[PROPOSED/(NAME+'.derived132.corrected.srt')]
 heard=json.loads((SOURCES/helper.LISTENING).read_text())
 assert heard['complete_natural_narration'] is True and heard['lesson_sha256']==helper.FROZEN
 assert heard['audio_sha256']==helper.PINS[helper.AUDIO]
 return helper,proposed,derived,heard

def build():
 helper,proposed,derived,heard=prepare()
 lesson=json.loads((SOURCES/helper.BASE/(NAME+'.narrated-source.json')).read_text())
 manifest=json.loads((SOURCES/helper.BASE/(NAME+'.captures.reviewed.json')).read_text())
 rows={r['id']:r for r in manifest['screenshots']}
 captions=(SOURCES/PROPOSED/(NAME+'.derived132.corrected.srt')).read_bytes()
 now=datetime.now(timezone.utc).isoformat()
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import instruction_scene_digest
 from render_walkthrough import load_cues,words
 parsed=load_cues(SOURCES/PROPOSED/(NAME+'.derived132.corrected.srt'));entries=proposed['cue_correspondence']
 assert len(parsed)==len(entries)==132
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
    'method':'Exact123service cues/frozen words mapped to31reviewed actualCore images in the frozen15scene first-appearance order; nine genuine service whole-second cuts and explicit Units-list return for Available. Parent read and accepted all132compact cue/image lines before final assembly. Separate132cue full PCM QA passed. Source field readbacks do not imply crew assignment, eligibility, provider operation or a new status event.'}
  scenes.append({'id':scene['id'],'start':start,'end':end,'screens':screens,
    'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in cues],
    'instruction_review':review})
 audio_sha=helper.PINS[helper.AUDIO];caption_sha=hashlib.sha256(captions).hexdigest()
 plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':derived['audio']['duration_seconds'],
   'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
   'narration':{'file':helper.AUDIO.as_posix(),'sha256':audio_sha,'kind':'approved_natural_narration',
     'approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':audio_sha,
       'complete_natural_narration':True,'evidence':heard['evidence'],
       'qa_file':(PROPOSED/(NAME+'.derived132.actual.qa.json')).as_posix(),
       'qa_sha256':PINS[PROPOSED/(NAME+'.derived132.actual.qa.json')],
       'listening_review_file':helper.LISTENING.as_posix(),'listening_review_sha256':helper.PINS[helper.LISTENING]}},
   'captions':{'file':(ASSEMBLY/(NAME+'.derived132.srt')).as_posix(),'sha256':caption_sha,'kind':'speech_timed_srt',
     'approval':{'reviewer':'Codex exact words/genuine markers/full derived PCM review','reviewed_at':now,
       'sha256':caption_sha,'audio_sha256':audio_sha,'speech_timing_reviewed':True,
       'method':'Original123service cue boundaries plus nine genuine whole-second word markers27/80/149/192/229/237/247/312/317 only. Whole-second precision, no interpolation or millisecond word timing; all132captions retain exact original words.',
       'word_timing_file':helper.ANCHORS.as_posix(),'word_timing_sha256':helper.PINS[helper.ANCHORS]}},
   'capture_manifests':[{'file':(ASSEMBLY/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
   'screenshot_reviews':{r['id']:{'reviewer':r['capture_review']['reviewer'],'reviewed_at':r['capture_review']['reviewed_at'],
     'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True}for r in rows.values()},
   'scenes':scenes,'publishable':False,'limitations':proposed['coverage_limits'],
   'parent_timing_review':{'reviewer':'Parent/root','evidence':'Root explicitly read all132caption/image lines in compactb4418995… and accepted the nine real marker cuts, control/result views and028→026Available return at325.199 before final assembly.','compact_file':(PROPOSED/'cue-screen-correspondence.txt').as_posix(),'compact_sha256':PINS[PROPOSED/'cue-screen-correspondence.txt']},
   'proposed_correspondence_file':(PROPOSED/'correspondence.proposed.json').as_posix(),
   'proposed_correspondence_sha256':PINS[PROPOSED/'correspondence.proposed.json']}
 return helper,plan,captions,manifest

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assemble',action='store_true');a=parser.parse_args()
 helper,plan,captions,manifest=build()
 if not a.assemble:
  print(json.dumps({'passed_source_preflight':True,'scenes':15,'sources':31,'intervals':44,'cues':132,'files_written':False,'rendered':False,'canonical_ready':False}));return
 out=SOURCES/ASSEMBLY;assert not out.exists(),'NEW-only final inputs; preserve all proposals and takes.'
 out.mkdir(parents=True)
 assets={'captures.reviewed.json':encoded(manifest),NAME+'.derived132.srt':captions,'plan.json':encoded(plan)}
 for name,data in assets.items():
  with (out/name).open('xb')as f:f.write(data)
 from render_walkthrough import validate_inputs
 checked=validate_inputs(SOURCES/helper.BASE/(NAME+'.narrated-source.json'),out/'plan.json',SOURCES)
 provenance={'schema_version':1,'kind':'guarded_approved_groups_units_final_assembly_inputs','created_at':datetime.now(timezone.utc).isoformat(),
   'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
   'source_frozen_sha256':helper.FROZEN,'listening_review_sha256':helper.PINS[helper.LISTENING],
   'inputs':[{'file':p.as_posix(),'sha256':h}for p,h in helper.PINS.items()]+[{'file':p.as_posix(),'sha256':h}for p,h in PINS.items()],
   'outputs':[{'file':str((out/n).relative_to(SOURCES)),'sha256':sha(out/n)}for n in assets],
   'unchanged_strict_renderer_inputs_passed':True,'rendered':False,'publishable':False,'canonical_or_ready_changed':False}
 (out/'provenance.json').write_bytes(encoded(provenance))
 print(json.dumps({'passed':True,'scenes':len(checked['scenes']),'cues':len(checked['cues']),'duration':checked['duration'],
   'plan':str((out/'plan.json').relative_to(SOURCES)),'plan_sha256':sha(out/'plan.json'),'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
