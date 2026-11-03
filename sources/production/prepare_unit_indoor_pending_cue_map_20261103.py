"""Verify the retained pre-export cue/screen proposals; audio and hearing gates remain separate."""
import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];S=R/'sources';sys.path.insert(0,str(R/'scripts'))
from render_walkthrough import load_cues,words
from verify_capture_evidence import _Validator,_normalized
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
configs={'viewer': {'name': 'app-unit-indoor-floor-reference', 'source_folder': 'app-unit-indoor-floor-reference-source-20261103', 'scene_apps': {}, 'spans': [['01', 1, 2, 11], ['01', 3, 6, 12], ['02', 7, 8, 12], ['02', 9, 12, 13], ['03', 13, 14, 14], ['03', 15, 18, 15], ['04', 19, 23, 5], ['04', 24, 26, 6], ['05', 27, 27, 6], ['05', 28, 30, 7], ['06', 31, 33, 8], ['06', 34, 35, 9], ['06', 36, 38, 10], ['07', 39, 39, 11], ['07', 40, 46, 12]], 'refs': {1: {'Maps': 'Maps', 'Indoor Maps': 'Indoor Maps', 'TRAINING ONLY - Community coordination centre': 'Community coordination centre'}, 3: {'TRAINING ONLY - Ground floor': 'Ground floor'}, 4: {'Indoor Maps': 'Indoor Maps'}, 7: {'TRAINING ONLY - Ground floor': 'Ground floor'}, 9: {'Briefing room - training': 'Briefing room'}, 13: {'TRAINING ONLY - GIS import': 'G I S import'}, 15: {'Training room - import': 'Training room import'}, 19: {'Equipment': 'Equipment'}, 24: {'Equipment - import': 'Equipment import'}, 27: {'Equipment': 'Equipment'}, 28: {'TRAINING ONLY - GIS import': 'G I S import'}, 31: {'TRAINING ONLY - KML and KMZ import': 'K M L and K M Z import'}, 34: {'KML training assembly area': 'each area'}, 35: {'Dispatch to this zone': 'Dispatch to this zone'}, 36: {'KMZ training access area': 'reference cards'}, 39: {'Maps': 'Maps', 'Indoor Maps': 'Indoor Maps'}, 40: {'TRAINING ONLY - Ground floor': 'Ground floor'}}, 'notes': ['Actual Unit viewer uses only authorized saved floor image and region coordinates. No fake image, physical position, live occupancy or call submission is claimed.', 'All clean final sources005–015 were personally viewed in the actual UI and the three source contact sheets. Earlier001–004 are excluded before narration production.', 'Maps entry/reopen read-only operations are grouped around the layer/detail/filter teaching sequence; original recording chronology and image bytes are retained.']}}
out=S/'production/unit_indoor_pending_audio_cue_map_20261103.json'
report=[]
for key,cfg in configs.items():
 base=S/'expansion/plans'/cfg['source_folder'];lesson=json.loads((base/'lesson.candidate.json').read_text());manifest=json.loads((base/'captures.reviewed.json').read_text());cues=load_cues(S/'expansion/audio'/(cfg['name']+'.raw.srt'))
 cfg.update(source_sha256=sha(base/'lesson.candidate.json'),captures_sha256=sha(base/'captures.reviewed.json'),raw_srt_sha256=sha(S/'expansion/audio'/(cfg['name']+'.raw.srt')),cue_count=len(cues),audio_export_downloaded=False,final_render_approval=False)
 rows={int(r['id'][:3]):r for r in manifest['screenshots']};observed={}
 for n,row in rows.items():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256']
  v=_Validator(S);observed[n]=v.observations(row,row['id']);assert not v.issues,v.issues
 selected=[]
 for scene,first,last,n in cfg['spans']:
  for i in range(first,last+1):
   c=cues[i-1];aliases=cfg['refs'].get(i,{})
   assert {_normalized(x) for x in aliases}<=observed[n],(key,i,n,'unobserved label',list(aliases))
   entry=dict(c,cue=i,required_labels=list(aliases),spoken_references=aliases,instructional=bool(aliases));v=_Validator(S);v.spoken_references(entry,{_normalized(x) for x in aliases},str(i),True);assert not v.issues,(key,v.issues)
   selected.append((scene,i,n))
 assert [x[1] for x in selected]==list(range(1,len(cues)+1))
 assert words(' '.join(c['text'] for c in cues))==words(' '.join(s['narration'] for s in lesson['scenes']))
 for scene in lesson['scenes']:
  subset=[x for x in selected if x[0]==scene['id']]
  assert words(' '.join(cues[x[1]-1]['text'] for x in subset))==words(scene['narration']),(key,scene['id'],'scene words')
  assert {_normalized(v) for v in scene['required_labels']}<=set().union(*(observed[x[2]] for x in subset)),(key,scene['id'],'scene labels')
 report.append({'lesson_id':cfg['name'],'speech_cues':len(cues),'screen_holds':len(cfg['spans']),'all_original_capture_hashes_and_actual_DOM_labels_checked':True,'exact_script_cue_correspondence':True,'audio_QA_or_listening_not_inferred':True})
payload=json.dumps({'kind':'pre_audio_export_screen_cue_proposal_only','configs':configs,'verification':report},ensure_ascii=False,indent=2)+'\n'
if out.exists():
 assert out.read_text()==payload,'Retain the existing proposal; use a new dated revision for changed inputs.'
else:
 out.write_text(payload)
print(json.dumps(report,indent=2))
