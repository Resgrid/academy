"""Assemble new renderer inputs only after real correspondence and User reviews.

Default checks the frozen inputs and reports any missing genuine listening review.
--assemble writes a NEW final-input directory. It never creates a listening review,
renders, approves final frames/playback, changes canonical/site files or uses Git.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
NAMES={'reports': 'core-records-saved-reports', 'exports': 'core-records-export-templates'}
PINS={'reports': {'root-complete-correspondence-review.json': '4998292df0c145146f61380d97b2b98cecd36492727cc2f36a53a8df404adb23', 'correspondence.proposed.json': 'bd6c0b39e66f803acce0812840c19e8cab9742ac14ccbc5f3a3931ebe11f8ad1', 'captures.source-relative.json': '2ac121e62a9f4a7a297482e8cc434793873d97f54413b3a550d12c30c1738058', 'lesson.learner-projection.proposed.json': '6a5111871b500aeed3a04397ad3daf847d96370a107fa85e250dda0a9e12997b', 'caption-layout-measurements.json': '464e134fd59a4ae846a09350b05d726fae543915506af4cd16eef71b6f6f7eb1'}, 'exports': {'root-complete-correspondence-review.json': '063f4bb1ef59909557b47e4e9f83d13b3c317352f6faa304fcc4ef06469627e5', 'correspondence.proposed.json': '00b527d3c2fe6f1141e564818d099acd184e1a98ad741ba5f0aae1862df42007', 'captures.source-relative.json': 'cd93fd5fdc336427190efef9747b2062cf385a4b16b9cb352ac63ffb252c1930', 'lesson.learner-projection.proposed.json': '385c6c8cf41fade0e0584d1ef46748f6d7eedf475422b6f0995984318e74d8f8', 'caption-layout-measurements.json': 'a0b69105784dc9b64423d751c94ac14243430a2ebfc150adaf378d5ba8d9729f'}}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def need(ok,message):
 if not ok:raise ValueError(message)
def put(path,data):
 with path.open('xb') as stream:stream.write(data)


def main(key,write=False):
 spec=importlib.util.spec_from_file_location('bigboard_correspondence',S/'production/prepare_records_reporting_complete_20261102.py')
 source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source);source.prepare(key,False)
 name=NAMES[key];P=Path('expansion/plans')/(name+'-complete-correspondence-20261102');F=Path('expansion/plans')/(name+'-take-01-final-inputs-20261102')
 for file,digest in PINS[key].items():need(sha(S/P/file)==digest,'Changed reviewed proposal: '+file)
 root=read(S/P/'root-complete-correspondence-review.json');data=read(S/P/'correspondence.proposed.json')
 need(root['reviewer']=='Codex /root' and root['human_listening_claim'] is False,'Missing actual Root review')
 for flag in ['complete_cue_correspondence_reviewed','screen_holds_and_required_controls_reviewed','semantic_reference_items_reviewed','learner_practice_prompts_reviewed','learner_sector_examples_reviewed','caption_layout_measurements_reviewed']:need(root[flag] is True,'Incomplete actual correspondence review')
 need(root['correspondence_sha256']==PINS[key]['correspondence.proposed.json'] and root['learner_projection_sha256']==PINS[key]['lesson.learner-projection.proposed.json'],'Review binds other prose or mapping')
 H=Path('expansion/audio')/(name+'.listening-review.json')
 if not (S/H).is_file():
  need(not write,'Genuine complete natural-narration User review is still required; no final inputs written.')
  return {'lesson_id':name,'verified_source_audio_and_mapping':True,'genuine_listening_review':'pending User response','final_inputs_written':False}
 hearing=read(S/H)
 need(hearing.get('reviewer')=='User' and hearing.get('complete_natural_narration') is True,'A generation confirmation or export permission is not a natural-narration review')
 need(hearing.get('audio_sha256')==data['audio_sha256'] and hearing.get('lesson_sha256')==data['lesson_sha256'],'Listening review binds another audio or script')
 need(hearing.get('evidence') and hearing.get('reviewed_at'),'Missing genuine listening evidence')
 if not write:return {'lesson_id':name,'passed':True,'read_only':True,'scenes':len(data['scenes']),'holds':data['holds_count'],'cues':data['cue_count']}
 sys.path.insert(0,str(ROOT/'scripts'))
 from render_walkthrough import validate_inputs
 from verify_capture_evidence import instruction_scene_digest
 destination=S/F;need(not destination.exists(),'Preserve existing final inputs');destination.mkdir()
 manifest=read(S/P/'captures.source-relative.json');rows={r['id']:r for r in manifest['screenshots']}
 put(destination/'captures.reviewed.json',(S/P/'captures.source-relative.json').read_bytes())
 put(destination/'captions.actual.corrected.srt',(S/data['captions_file']).read_bytes())
 plan={'schema_version':1,'lesson_id':name,'duration_seconds':data['duration_seconds'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
  'narration':{'file':data['audio_file'],'sha256':data['audio_sha256'],'kind':'approved_natural_narration','approval':{'reviewer':'User','reviewed_at':hearing['reviewed_at'],'sha256':data['audio_sha256'],'complete_natural_narration':True,'evidence':hearing['evidence'],'qa_file':data['qa_file'],'qa_sha256':data['qa_sha256'],'listening_review_file':str(H),'listening_review_sha256':sha(S/H)}},
  'captions':{'file':str(F/'captions.actual.corrected.srt'),'sha256':data['captions_sha256'],'kind':'speech_timed_srt','approval':{'reviewer':'Codex /root actual cue timing and complete PCM QA','reviewed_at':root['reviewed_at'],'sha256':data['captions_sha256'],'audio_sha256':data['audio_sha256'],'speech_timing_reviewed':True,'method':f"All {data['cue_count']} original exported speech cue boundaries retained. Exact frozen script and all non-silent speech cues verified on a complete audio decode. Genuine User hearing is separately required."}},
  'capture_manifests':[{'file':str(F/'captures.reviewed.json'),'sha256':PINS[key]['captures.source-relative.json']}],
  'screenshot_reviews':{id:{'reviewer':r['capture_review']['reviewer'],'reviewed_at':r['capture_review']['reviewed_at'],'sha256':r['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for id,r in rows.items()},
  'scenes':[],'parent_correspondence_review':{'file':str(P/'root-complete-correspondence-review.json'),'sha256':PINS[key]['root-complete-correspondence-review.json']},'publishable':False,
  'limitations':['Actual encoded screen/caption and advancing browser-playback reviews remain required.','Software-only fictional training data; respect the source lesson scope limits.']}
 if data.get('supporting_applications'):plan['supporting_applications']=data['supporting_applications']
 reviewed=[]
 for item in data['scenes']:
  scene=deepcopy(item);digest=scene.pop('proposed_mapping_sha256');need(instruction_scene_digest(scene,rows)==digest,'Changed exact instruction map')
  scene['instruction_review']={'reviewer':'Codex /root','reviewed_at':root['reviewed_at'],'passed':True,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':digest,'evidence_file':str(P/'root-complete-correspondence-review.json'),'evidence_sha256':PINS[key]['root-complete-correspondence-review.json']}
  reviewed.append(scene);plan['scenes'].append({'id':scene['id'],'start':scene['start'],'end':scene['end'],'screens':scene['screens'],'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in scene['captions']],'instruction_review':scene['instruction_review']})
 for planned,reviewed_scene in zip(plan['scenes'],reviewed):
  if 'instruction_app' in reviewed_scene:planned['instruction_app']=reviewed_scene['instruction_app']
 put(destination/'scenes.reviewed.json',encoded(reviewed));put(destination/'plan.json',encoded(plan))
 result=validate_inputs(S/data['lesson_file'],destination/'plan.json',S)
 need(all(instruction_scene_digest(sc,rows)==sc['instruction_review']['mapping_sha256'] for sc in result['scenes']),'Instruction digest roundtrip failed')
 put(destination/'provenance.json',encoded({'lesson_id':name,'source_file':data['lesson_file'],'source_sha256':data['lesson_sha256'],'strict_renderer_inputs_passed':True,'all_instruction_digest_roundtrips_passed':True,'genuine_root_map_review_sha256':PINS[key]['root-complete-correspondence-review.json'],'genuine_user_hearing_sha256':sha(S/H),'audio_sha256':data['audio_sha256'],'captions_sha256':data['captions_sha256'],'scenes':len(data['scenes']),'holds':data['holds_count'],'cues':data['cue_count'],'rendered':False,'canonical_or_site_changed':False}))
 return {'passed':True,'plan':str(F/'plan.json'),'plan_sha256':sha(destination/'plan.json'),'rendered':False}


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('lesson',choices=PINS);parser.add_argument('--assemble',action='store_true');args=parser.parse_args()
 print(json.dumps(main(args.lesson,args.assemble),indent=2))
