"""Guarded Personnel assembly after actual listening and parent timing review.

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
NAME='core-personnel-administration'
QA_HELPER=SOURCES/'production/qa_core_personnel_proposed_captions_20261028_v2.py'
QA_HELPER_SHA='a605a7bd1fc153788cea69486e5199f0c11320ebf248ef56b08f0322a363c14e'
PROPOSED=Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2')
ASSEMBLY=Path('expansion/plans/core-personnel-administration-take-01-final-inputs-20261028')
PINS={
 Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2/correspondence.proposed.json'): '123bd52f668f8c7cf67fd1055a2043068fccc45ea43b383b73252b3a245481c5',
 Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2/core-personnel-administration.derived116.actual.qa.json'): '6b8e58a7a8a3cd1708fb7840785a6a967aebe8e12fec0a55ab50e9b39450fefa',
 Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2/core-personnel-administration.derived116.corrected.srt'): 'd4364f2817a860d2c73293374212ec88bc171713a652e8030d95ed82403932a3',
 Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2/cue-screen-correspondence.txt'): 'b92eb721a960976f2cd09f2f295122d48b6867f89f8a9b4c555c04f421032812',
 Path('expansion/plans/core-personnel-administration-take-01-proposed-derived-20261028-v2/provenance.json'): '457612edf875eccd76e36a65bcd5ef3b38fb4bbb42bbeaea3351ab5adbf23e9e',
 Path('expansion/audits/core-personnel-proposed-timing-source-review-20261028.json'): '910ee30538e3336c17cd1da055416c68ab28497a94697decfda7b5e33eed4077',
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
 for key in ['cue_correspondence','scenes','genuine_service_anchor_cuts','coalescence','caption_gap_hold','readability','explicit_timing_choices']:
  assert rebuilt[key]==proposed[key],'Retained proposed correspondence diverged.'
 derived=json.loads((SOURCES/PROPOSED/(NAME+'.derived116.actual.qa.json')).read_text())
 assert derived['passed'] and not derived['issues'] and not derived['possible_speech_gaps']
 assert derived['audio']==original['audio'] and derived['silent_raw_cues']==derived['silent_corrected_cues']==0
 assert derived['alignment']['text_changes']==[] and derived['lesson']['sha256']==helper.FROZEN
 assert derived['corrected_captions']['sha256']==PINS[PROPOSED/(NAME+'.derived116.corrected.srt')]
 heard=json.loads((SOURCES/helper.LISTENING).read_text())
 assert heard['complete_natural_narration'] is True and heard['lesson_sha256']==helper.FROZEN
 assert heard['audio_sha256']==helper.PINS[helper.AUDIO]
 return helper,proposed,derived,heard

def build():
 helper,proposed,derived,heard=prepare()
 lesson=json.loads((SOURCES/helper.BASE/(NAME+'.narrated-source.json')).read_text())
 manifest=json.loads((SOURCES/helper.BASE/(NAME+'.captures.reviewed.json')).read_text())
 rows={r['id']:r for r in manifest['screenshots']}
 captions=(SOURCES/PROPOSED/(NAME+'.derived116.corrected.srt')).read_bytes()
 now=datetime.now(timezone.utc).isoformat()
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import instruction_scene_digest
 from render_walkthrough import load_cues,words
 parsed=load_cues(SOURCES/PROPOSED/(NAME+'.derived116.corrected.srt'));entries=proposed['cue_correspondence']
 assert len(parsed)==len(entries)==116
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
    'method':'Exact112actualv2service cues/frozen words mapped to26reviewed actualCore images in their frozen12scene order, including the028catalog return. Five genuine service whole-second cuts, same022image75/76merge, and measured raw95gap hold to raw96start are explicit. Parent read and accepted all116compact cue/image lines before assembly. Separate116cue full PCM QA passed. No savedORcomparison, unrelated administrative change or enforcement/authorization result is implied.'}
  scenes.append({'id':scene['id'],'start':start,'end':end,'screens':screens,
    'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in cues],
    'instruction_review':review})
 audio_sha=helper.PINS[helper.AUDIO];caption_sha=hashlib.sha256(captions).hexdigest()
 plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':derived['audio']['duration_seconds'],
   'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
   'narration':{'file':helper.AUDIO.as_posix(),'sha256':audio_sha,'kind':'approved_natural_narration',
     'approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':audio_sha,
       'complete_natural_narration':True,'evidence':heard['evidence'],
       'qa_file':(PROPOSED/(NAME+'.derived116.actual.qa.json')).as_posix(),
       'qa_sha256':PINS[PROPOSED/(NAME+'.derived116.actual.qa.json')],
       'listening_review_file':helper.LISTENING.as_posix(),'listening_review_sha256':helper.PINS[helper.LISTENING]}},
   'captions':{'file':(ASSEMBLY/(NAME+'.derived116.srt')).as_posix(),'sha256':caption_sha,'kind':'speech_timed_srt',
     'approval':{'reviewer':'Codex exact words/genuine markers/full derived PCM review','reviewed_at':now,
       'sha256':caption_sha,'audio_sha256':audio_sha,'speech_timing_reviewed':True,
       'method':'Original112actualv2service cue boundaries plus genuine whole-second word markers72/82/112/314/319; raw75/76adjacent same022image merge ends at actualraw76end254.380, and raw95caption holds only to next realraw96start316.320across its0.451second gap. No estimated word time or changed words; all116captions retain the exact script.',
       'word_timing_file':helper.ANCHORS.as_posix(),'word_timing_sha256':helper.PINS[helper.ANCHORS]}},
   'capture_manifests':[{'file':(ASSEMBLY/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
   'screenshot_reviews':{r['id']:{'reviewer':r['capture_review']['reviewer'],'reviewed_at':r['capture_review']['reviewed_at'],
     'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True}for r in rows.values()},
   'scenes':scenes,'publishable':False,'limitations':proposed['coverage_limits'],
   'parent_timing_review':{'reviewer':'Parent/root','evidence':'Root explicitly read all116caption/image lines in compactb92eb721… and accepted five genuine marker cuts72/82/112/314/319,75+76same022merge and the raw95Casey314→316.320measured gap hold before final assembly.','compact_file':(PROPOSED/'cue-screen-correspondence.txt').as_posix(),'compact_sha256':PINS[PROPOSED/'cue-screen-correspondence.txt']},
   'proposed_correspondence_file':(PROPOSED/'correspondence.proposed.json').as_posix(),
   'proposed_correspondence_sha256':PINS[PROPOSED/'correspondence.proposed.json']}
 return helper,plan,captions,manifest

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assemble',action='store_true');a=parser.parse_args()
 helper,plan,captions,manifest=build()
 if not a.assemble:
  print(json.dumps({'passed_source_preflight':True,'scenes':12,'sources':26,'intervals':38,'cues':116,'files_written':False,'rendered':False,'canonical_ready':False}));return
 out=SOURCES/ASSEMBLY;assert not out.exists(),'NEW-only final inputs; preserve all proposals and takes.'
 out.mkdir(parents=True)
 assets={'captures.reviewed.json':encoded(manifest),NAME+'.derived116.srt':captions,'plan.json':encoded(plan)}
 for name,data in assets.items():
  with (out/name).open('xb')as f:f.write(data)
 from render_walkthrough import validate_inputs
 checked=validate_inputs(SOURCES/helper.BASE/(NAME+'.narrated-source.json'),out/'plan.json',SOURCES)
 provenance={'schema_version':1,'kind':'guarded_approved_personnel_final_assembly_inputs','created_at':datetime.now(timezone.utc).isoformat(),
   'recipe':{'file':str(Path(__file__).relative_to(SOURCES)),'sha256':sha(__file__)},
   'source_frozen_sha256':helper.FROZEN,'listening_review_sha256':helper.PINS[helper.LISTENING],
   'inputs':[{'file':p.as_posix(),'sha256':h}for p,h in helper.PINS.items()]+[{'file':p.as_posix(),'sha256':h}for p,h in PINS.items()],
   'outputs':[{'file':str((out/n).relative_to(SOURCES)),'sha256':sha(out/n)}for n in assets],
   'unchanged_strict_renderer_inputs_passed':True,'rendered':False,'publishable':False,'canonical_or_ready_changed':False}
 (out/'provenance.json').write_bytes(encoded(provenance))
 print(json.dumps({'passed':True,'scenes':len(checked['scenes']),'cues':len(checked['cues']),'duration':checked['duration'],
   'plan':str((out/'plan.json').relative_to(SOURCES)),'plan_sha256':sha(out/'plan.json'),'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
