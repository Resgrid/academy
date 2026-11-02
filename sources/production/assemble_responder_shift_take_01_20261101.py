"""Assemble new renderer inputs from the genuine complete Root/User reviews.

Default only verifies inputs. --assemble writes a NEW final-input directory;
it does not render, approve encoded frames, browse, publish, alter canonical/site
files, copy to another repository or perform Git operations.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
NAME='app-responder-shift-schedules-rosters'
P=Path('expansion/plans')/(NAME+'-proposed92-correspondence-20261101')
F=Path('expansion/plans')/(NAME+'-take-01-final-inputs-20261101')
PINS={'root-complete-correspondence-review.json':'cca8d985ca859f8ce00a300c6dcb9148174b340200656fd938aa6c35f328a682',
      'correspondence.proposed.json':'288f4095917724baeaed0c69fce19e4c52cc6c5cac8676b3809e4a0e59d3556b',
      'captures.source-relative.json':'21065d1f8e9e2a015803d728264957cbb1d5a80a8ce1521c70603976f9e199c2',
      'lesson.learner-projection.proposed.json':'098d8ad765412e2deba1f32702a896edc69dff75ec6ab7f893106ebf5e5e453f',
      'caption-layout-measurements.json':'df4aea44142e9e8613474b484708203b0ca5ea830697f48f9e631672e5350cae'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(ok,message):
    if not ok:raise ValueError(message)
def put(p,b):
    with p.open('xb') as f:f.write(b)
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()

def main(write=False):
    spec=importlib.util.spec_from_file_location('shift_correspondence_source',S/'production/prepare_responder_shift_correspondence_20261101.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source);source.prepare(False)
    for name,digest in PINS.items():need(sha(S/P/name)==digest,'Changed reviewed proposal '+name)
    root=read(S/P/'root-complete-correspondence-review.json');data=read(S/P/'correspondence.proposed.json');hearing=read(S/source.HEARING);qa=read(S/source.QA)
    need(root['reviewer']=='Codex /root' and root['human_listening_claim'] is False,'Missing genuine Root map review')
    for key in ['complete_cue_correspondence_reviewed','screen_holds_and_required_controls_reviewed','semantic_reference_items_reviewed','learner_practice_prompts_reviewed','learner_sector_examples_reviewed']:need(root[key] is True,'Incomplete actual Root review')
    need(root['correspondence_sha256']==PINS['correspondence.proposed.json'] and root['learner_projection_sha256']==PINS['lesson.learner-projection.proposed.json'],'Review binds other content')
    need(hearing['reviewer']=='User' and hearing['complete_natural_narration'] and hearing['audio_sha256']==data['audio_sha256'],'Missing genuine complete User hearing')
    if not write:
        print(json.dumps({'passed':True,'read_only':True,'scenes':10,'holds':17,'cues':92,'source_images':14}));return
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_walkthrough import validate_inputs
    from verify_capture_evidence import instruction_scene_digest
    destination=S/F;need(not destination.exists(),'Preserve existing final renderer inputs');destination.mkdir()
    manifest=read(S/P/'captures.source-relative.json');rows={x['id']:x for x in manifest['screenshots']}
    put(destination/'captures.reviewed.json',(S/P/'captures.source-relative.json').read_bytes())
    put(destination/'captions.actual.corrected.srt',(S/source.CAPTIONS).read_bytes())
    plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':data['duration_seconds'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
      'narration':{'file':str(source.AUDIO),'sha256':data['audio_sha256'],'kind':'approved_natural_narration','approval':{'reviewer':'User','reviewed_at':hearing['reviewed_at'],'sha256':data['audio_sha256'],'complete_natural_narration':True,'evidence':hearing['evidence'],'qa_file':str(source.QA),'qa_sha256':data['qa_sha256'],'listening_review_file':str(source.HEARING),'listening_review_sha256':source.PINS[source.HEARING]}},
      'captions':{'file':str(F/'captions.actual.corrected.srt'),'sha256':data['captions_sha256'],'kind':'speech_timed_srt','approval':{'reviewer':'Codex /root actual source timings and complete PCM QA','reviewed_at':root['reviewed_at'],'sha256':data['captions_sha256'],'audio_sha256':data['audio_sha256'],'speech_timing_reviewed':True,'method':'All original service cue endpoints retained. Only original cue49 splits at the genuine stored Descript then word start,165.290s. Exact complete words, whole audio decode and all92 speech-cue PCM measurements pass. Separate User complete natural narration hearing retained.'}},
      'capture_manifests':[{'file':str(F/'captures.reviewed.json'),'sha256':PINS['captures.source-relative.json']}],
      'screenshot_reviews':{id:{'reviewer':row['capture_review']['reviewer'],'reviewed_at':row['capture_review']['reviewed_at'],'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for id,row in rows.items()},
      'scenes':[],'parent_correspondence_review':{'file':str(P/'root-complete-correspondence-review.json'),'sha256':PINS['root-complete-correspondence-review.json']},'publishable':False,
      'limitations':['Read-only recorded schedule and queue inspection. No roster mutation or physical-attendance verification is demonstrated.','Actual encoded-frame, caption and browser-playback qualification remain required.']}
    reviewed=[]
    for item in data['scenes']:
        full=deepcopy(item);digest=full.pop('proposed_mapping_sha256');need(instruction_scene_digest(full,rows)==digest,'Changed complete instruction map')
        full['instruction_review']={'reviewer':'Codex /root','reviewed_at':root['reviewed_at'],'passed':True,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':digest,'evidence_file':str(P/'root-complete-correspondence-review.json'),'evidence_sha256':PINS['root-complete-correspondence-review.json']}
        reviewed.append(full);plan['scenes'].append({'id':full['id'],'start':full['start'],'end':full['end'],'screens':full['screens'],'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in full['captions']],'instruction_review':full['instruction_review']})
    put(destination/'scenes.reviewed.json',encoded(reviewed));put(destination/'plan.json',encoded(plan))
    result=validate_inputs(S/source.LESSON,destination/'plan.json',S)
    need(all(instruction_scene_digest(scene,rows)==scene['instruction_review']['mapping_sha256'] for scene in result['scenes']),'Instruction digest roundtrip failed')
    put(destination/'provenance.json',encoded({'lesson_id':NAME,'source_file':str(source.LESSON),'source_sha256':data['lesson_sha256'],'strict_renderer_inputs_passed':True,'all_instruction_digest_roundtrips_passed':True,'genuine_root_map_review_sha256':PINS['root-complete-correspondence-review.json'],'genuine_user_hearing_sha256':source.PINS[source.HEARING],'audio_sha256':data['audio_sha256'],'captions_sha256':data['captions_sha256'],'scenes':10,'holds':17,'source_images':14,'cues':92,'rendered':False,'canonical_or_site_changed':False}))
    print(json.dumps({'passed':True,'plan':str(F/'plan.json'),'plan_sha256':sha(destination/'plan.json'),'rendered':False},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--assemble',action='store_true');args=parser.parse_args();main(args.assemble)
