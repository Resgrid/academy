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
NAMES={'road': 'core-unit-road-guidance', 'layers': 'core-map-layer-authoring', 'indoor': 'core-indoor-call-location', 'kml': 'core-kml-kmz-import'}
PINS={'road': {'root-complete-correspondence-review.json': '30dc42923005c83e62ebb93e6dcc8c1a0fd4c4fad560cf8099dd7e8ff7e085ba', 'correspondence.proposed.json': 'cb2442f7b671e076539c7b755ca04291b8e1f7112b0bc44818a3370ea64dbbad', 'captures.source-relative.json': '7473ec8236605ba300402363c9508756e2d0b9171f8bfa717f94287759217fc6', 'lesson.learner-projection.proposed.json': '799ffd5ce2c4e0ea7bbbc7815f7e4424ffd119c2c4986ab6be0580409ddaa87d', 'caption-layout-measurements.json': '681b042161cd776d7374940746bf624eaaa4f377eb9812eadcc2f37bd8ec9acf'}, 'layers': {'root-complete-correspondence-review.json': '4322fce977db9b1e264ffc0bbcd0f59d09c377f275fee6fc6285c34eb5d1e26d', 'correspondence.proposed.json': '8f00b212a4d9b371bef632eddd68e6d02e48e67e462ab4198042963ed807b187', 'captures.source-relative.json': 'f065c25e9e420558305ac8b536cf71694d63610e012acd4ed89abbcbdb7eb287', 'lesson.learner-projection.proposed.json': '5c90ad63aa875762f0cf8d21c04cf946e928534c97611ce74be026cffeb90adc', 'caption-layout-measurements.json': '456575ce6361ce8c42e646e35e9eecf4a6b15c8fd2906f810149b9f53b5f3b39'}, 'indoor': {'root-complete-correspondence-review.json': 'c0f46fa9eae9eedb7f2ddd46cf6935b71584e26ce3fb1f1bd1f7579a841758fa', 'correspondence.proposed.json': '4c83050ec32295c483703d25ce4ef1fb9d5bbc159290c1fe73e3dbae77a73937', 'captures.source-relative.json': '3e8298f412b759cdd39b11b7a029a55d172a540c83140fa5c7bbe63d3931c885', 'lesson.learner-projection.proposed.json': 'c4ac5fc06a9292c58e1ca88306b438cb86a3529c77645a5682787fbf234a761d', 'caption-layout-measurements.json': '60571603b8fe58f2319e51be2b204701ea2493646580f8310813c41534886796'}, 'kml': {'root-complete-correspondence-review.json': '2506173505e848f81aff604a06babe2e027cc010b5055ca982cca64e41a9f414', 'correspondence.proposed.json': '75fbcea4ee15b16c4c124b5ef012d14f0b844e028c966ccb068723181d20723f', 'captures.source-relative.json': '64b34c2c8dbda9128ee4c20f2faf3d2289fcfd52d1b6573fd296970efa44088f', 'lesson.learner-projection.proposed.json': '72b362567f75e432293bff0933215bbec731b7f00a8fb9c30813f29a68b189e6', 'caption-layout-measurements.json': 'a4032d55d3f46049dcf4f662b94309a0edcd89b8a7a70534314afbe9d8ce0402'}}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def need(ok,message):
 if not ok:raise ValueError(message)
def put(path,data):
 with path.open('xb') as stream:stream.write(data)


def main(key,write=False):
 spec=importlib.util.spec_from_file_location('deployment_correspondence',S/'production/prepare_mapping_complete_20261103.py')
 source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source);source.prepare(key,False)
 name=NAMES[key];P=Path('expansion/plans')/(name+'-complete-correspondence-20261103');F=Path('expansion/plans')/(name+'-take-01-final-inputs-20261103')
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
