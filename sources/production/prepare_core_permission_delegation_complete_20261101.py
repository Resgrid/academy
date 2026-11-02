"""Bind the two complete narration exports to explicitly ordered real views.

This verifies source, speech and proposed cuts. It never creates a hearing,
encoded-frame or browser-playback approval.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
TITLE = 'TRAINING ONLY - IC coordination note'
DRAFT = TITLE + ' v1 · Draft'
PUBLISHED = TITLE + ' v1 · Published'
READONLY = 'This version is published and read-only. Open a new draft to make changes.'
UPDATE = 'TRAINING UPDATE - Handover note reviewed for software practice.'
SUMMARY = 'TRAINING ONLY - IC coordination handover software exercise'
ATTEST = 'I attest this Record is complete and accurate'
CFG = {'permissions': {'name': 'core-permissions-group-and-role-delegation', 'cues': 64, 'source_sha256': '1df2920ae6cb58d1bbb2fd1d6aaa6377c715bdeb3b332de9e616dffb7e510d31', 'captures_sha256': '5dfa6b1ad35034e1b9f6458717e4835e363f64f3a5bcf4129dbb67a23a72bec3', 'audio_sha256': 'c5b25536e810fae3f277a47ca2de7f7d91da0a1412a897dd1980b1af8ecec857', 'captions_sha256': '2bbb75a01d535aa5dda9153e7ac803f7b1bb3736e06eacb1c4f0ec7f1e70e354', 'qa_sha256': '5245d6d1896aecff569b1d77c91cc86c0f52b8e6f58af4dc4e540acba70146d6', 'spans': [('01', 1, 1, 11), ('01', 2, 7, 1), ('02', 8, 15, 1), ('03', 16, 22, 2), ('04', 23, 29, 3), ('05', 30, 31, 4), ('05', 32, 33, 5), ('05', 34, 38, 6), ('06', 39, 39, 6), ('06', 40, 46, 9), ('07', 47, 55, 10), ('08', 56, 64, 1)], 'refs': {1: {'Security & Permissions': 'Security and Permissions'}, 2: {'Security and Permissions': 'Security and Permissions'}, 4: {'Permission': 'Permission', 'Note': 'Note', 'Selection': 'Selection'}, 5: {'Group Only': 'Group Only', 'Roles': 'Roles'}, 8: {'Who can Add Users': 'Who can Add Users'}, 9: {'Department Admins': 'Department Admins'}, 16: {'Who can Add Users': 'Who can Add Users', 'Department and Group Admins': 'Department and Group Admins'}, 19: {'Who can Remove Users': 'Who can Remove Users', 'Department Admins': 'Department Admins'}, 23: {'Who can Add Users': 'Who can Add Users', 'Department Admins': 'Department Admins'}, 30: {'Who can Create Trainings': 'Who can Create Trainings'}, 31: {'Department Admins': 'Department Admins', 'No Roles': 'No Roles'}, 32: {'Department Admins and Select Roles': 'Department Admins and Select Roles', 'Select roles...': 'Select roles'}, 33: {'Rescue Technician': 'Rescue Technician', 'Paramedic': 'Paramedic'}, 34: {'Rescue Technician': 'Rescue Technician'}, 35: {'Rescue Technician': 'Technician tag'}, 40: {'Who can Create Trainings': 'Create Trainings', 'Department Admins': 'Department Admins'}, 41: {'No Roles': 'No Roles'}, 47: {'Who can see the Location of Personnel': 'Who can see the Location of Personnel'}, 48: {'Who can see the Location of Units': 'Who can see the Location of Units'}, 49: {'Everyone': 'Everyone'}, 50: {'This option determines who can see the location of personnel on the maps. To lock the option to just group admins and roles within a group you need to check the Group Only option.': 'the Group Only option'}, 56: {'Security and Permissions': 'Security and Permissions'}, 57: {'Changes to the permissions will take effect on the next login to the Resgrid web application.': 'changes take effect on the next login to the Resgrid web application'}}, 'context_notes': ['The department menu entry uses Security & Permissions; the returned page heading spells Security and Permissions. Both exact actual labels are separately mapped.', 'Cue34 selects and reads the named Rescue Technician tag in source006; cue35 continues the same spoken label. Excluded source007 is not used to claim a readable role name after reload.', 'Cue39 shows the original selected-role control while the practice selection is removed; cue40 cuts to the separately verified restored Department Admins row. No clear-all success is inferred from excluded source008.', 'The Group Only explanation uses the exact fully visible location-row note. No checkbox change or working device location is demonstrated.', 'Only saved administrator settings are demonstrated. The narrated next-login account test is a learner practice plan, not an action shown as performed.']}}


def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(key, write=False):
 from PIL import Image, ImageDraw, ImageFont
 from render_walkthrough import load_cues, words, caption_wrap, find_font, WIDTH
 from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
 from expansion_site import lesson_content_digest
 cfg=CFG[key];name=cfg['name'];base=Path('expansion/plans')/(name+'-source-proposal-20261101')
 audio=Path('expansion/audio')/(name+'.m4a');cap=Path('expansion/audio')/(name+'.actual.corrected.srt');qa_path=Path('expansion/audio')/(name+'.actual.qa.json')
 for path,digest in [(base/'lesson.candidate.json',cfg['source_sha256']),(base/'captures.reviewed.json',cfg['captures_sha256']),
                     (audio,cfg['audio_sha256']),(cap,cfg['captions_sha256']),(qa_path,cfg['qa_sha256'])]:
  assert sha(S/path)==digest,str(path)
 lesson=json.loads((S/base/'lesson.candidate.json').read_text());manifest=json.loads((S/base/'captures.reviewed.json').read_text());qa=json.loads((S/qa_path).read_text())
 assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps'] and qa['silent_corrected_cues']==0
 assert qa['audio']['full_decode']=='passed' and qa['audio']['full_scale_samples']==0
 assert qa['lesson']['sha256']==cfg['source_sha256'] and qa['audio']['sha256']==cfg['audio_sha256']
 rows={row['id']:row for row in manifest['screenshots']};numbered={int(row['id'][:3]):row for row in rows.values()};observed={}
 for row in rows.values():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256']
  validator=_Validator(S);observed[row['id']]=validator.observations(row,row['id']);assert not validator.issues,validator.issues
 cues=load_cues(S/cap);assert len(cues)==cfg['cues']
 assert words(' '.join(cue['text'] for cue in cues))==words(' '.join(scene['narration'] for scene in lesson['scenes']))
 duration=qa['audio']['duration_seconds'];holds=[];entries=[]
 for index,(scene_id,first,last,number) in enumerate(cfg['spans']):
  capture_id=numbered[number]['id'];start=0.0 if index==0 else cues[first-1]['start']
  end=cues[cfg['spans'][index+1][1]-1]['start'] if index+1<len(cfg['spans']) else duration
  holds.append({'scene_id':scene_id,'screenshot_id':capture_id,'first_cue':first,'last_cue':last,'start':start,'end':end})
  for count in range(first,last+1):
   cue=cues[count-1];aliases=cfg['refs'].get(count,{})
   assert cue['start']>=start and cue['end']<=end
   labels={_normalized(label) for label in aliases};assert labels<=observed[capture_id],(count,capture_id)
   entry=dict(cue,cue=count,scene_id=scene_id,screenshot_id=capture_id,required_labels=list(aliases),spoken_references=aliases,instructional=bool(aliases))
   validator=_Validator(S);validator.spoken_references(entry,labels,str(count),True);assert not validator.issues,validator.issues
   if key=='ic-record' and count==2:entry['visual_symbol_review_note']=cfg['context_notes'][0]
   entries.append(entry)
 assert [row['cue'] for row in entries]==list(range(1,cfg['cues']+1))
 learner=deepcopy(lesson);learner['scope_limits']=[v for v in learner['scope_limits'] if not v.startswith('Source proposal only.')]
 scenes=[]
 for original,projection in zip(lesson['scenes'],learner['scenes']):
  selected=[h for h in holds if h['scene_id']==original['id']]
  captions=[{k:v for k,v in row.items() if k!='scene_id'} for row in entries if row['scene_id']==original['id']]
  assert words(' '.join(row['text'] for row in captions))==words(original['narration'])
  assert {_normalized(v) for v in original['required_labels']}<=set().union(*(observed[h['screenshot_id']] for h in selected))
  projection['capture_refs']=list(dict.fromkeys([*projection['capture_refs'],*[h['screenshot_id'] for h in selected]]))
  scene={'id':original['id'],'title':original['title'],'kind':'operational','start':selected[0]['start'],'end':selected[-1]['end'],
         'visual_required_labels':original['required_labels'],'screens':[{k:h[k] for k in ['screenshot_id','start','end']} for h in selected],'captions':captions}
  scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows);scenes.append(scene)
 assert lesson_content_digest(learner)==lesson_content_digest(lesson)
 draw=ImageDraw.Draw(Image.new('RGB',(1920,1080)));font=ImageFont.truetype(str(find_font()),30)
 metrics={'kind':'numeric_caption_layout_measurement_only','cues':[{'cue':row['cue'],'lines':caption_wrap(draw,row['text'],font,WIDTH-120)} for row in entries],
          'actual_encoded_frame_review':False,'listening_review':False}
 proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_id':name,'lesson_file':str(base/'lesson.candidate.json'),'lesson_sha256':cfg['source_sha256'],
           'audio_file':str(audio),'audio_sha256':cfg['audio_sha256'],'captions_file':str(cap),'captions_sha256':cfg['captions_sha256'],
           'qa_file':str(qa_path),'qa_sha256':cfg['qa_sha256'],'duration_seconds':duration,'duration_source':'Complete decode of the specifically approved private Descript export',
           'scenes':scenes,'holds':holds,'cues':entries,'cue_count':len(cues),'scenes_count':len(scenes),'holds_count':len(holds),
           'source_images':len(rows),'distinct_source_images':len({row['sha256'] for row in rows.values()}),'learner_content_sha256':lesson_content_digest(learner),
           'context_notes':cfg['context_notes'],'review_state':'complete_audio_and_cue_map_proposal_requires_actual_Root_and_User_reviews','export_ready':False}
 if write:
  dest=S/'expansion/plans'/(name+'-complete-correspondence-20261101');assert not dest.exists();dest.mkdir()
  for filename,data in [('correspondence.proposed.json',proposal),('captures.source-relative.json',manifest),('lesson.learner-projection.proposed.json',learner),('caption-layout-measurements.json',metrics)]:
   (dest/filename).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
  (dest/'cue-screen-correspondence.txt').write_text('\n\n'.join(f"Cue{row['cue']:03} · scene{row['scene_id']} · {row['start']:.3f}–{row['end']:.3f} · {row['screenshot_id']}\n{row['text']}\n{json.dumps(row['spoken_references'],ensure_ascii=False)}" for row in entries)+'\n')
 return {'passed':True,'lesson_id':name,'scenes':len(scenes),'holds':len(holds),'cues':len(cues),'actual_screens':len(rows),'max_caption_lines':max(len(row['lines']) for row in metrics['cues']),'written':write,'final_approval_inferred':False}


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('lesson',choices=CFG);parser.add_argument('--write',action='store_true');args=parser.parse_args()
 print(json.dumps(prepare(args.lesson,args.write),indent=2))
