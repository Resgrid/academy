"""Bind the complete BigBoard speech to reviewed actual UI screen holds. No approval is inferred."""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / "sources"
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "scripts"))
CFG = {'bigboard': {'name': 'app-bigboard-operational-display', 'cues': 105, 'source_sha256': '884b8cf7c577e898c604f097df5551d899ace214764d7db8f1d594537fc36428', 'captures_sha256': 'e6383915b3709261598ce665b25a9799c3acf98412c189e58eaea4ffb30dc5d3', 'audio_sha256': '3ef9a87b795edec7c77c675832358cbef13ad3eb9d43e30bb75fafd3451b0bcb', 'captions_sha256': '6fd304251287f47984dcdc8cd217cf22d4b1d11135daea023b78b149c031c424', 'qa_sha256': 'fbcdeda0e68d8f54e97f57f8895f3cb08b417c94b66390a6f871a7ba85524414', 'spans': [('01', 1, 8, 29), ('02', 9, 10, 6), ('02', 11, 16, 7), ('03', 17, 17, 16), ('03', 18, 24, 11), ('04', 25, 31, 12), ('05', 32, 39, 16), ('06', 40, 47, 22), ('07', 48, 56, 17), ('08', 57, 64, 23), ('09', 65, 73, 29), ('10', 74, 74, 29), ('10', 75, 80, 24), ('11', 81, 81, 24), ('11', 82, 88, 25), ('12', 89, 89, 25), ('12', 90, 96, 26), ('13', 97, 98, 30), ('13', 99, 105, 29)], 'refs': {1: {'Resgrid BigBoard': 'Resgrid Big Board'}, 2: {'Personnel': 'Personnel', 'Status': 'status'}, 3: {'Staffing': 'staffing'}, 9: {'Welcome to Your Dashboard': 'empty dashboard'}, 11: {'Add Widget': 'Add Widget'}, 12: {'Calls': 'Calls', 'Units': 'Units', 'Personnel': 'Personnel', 'Time': 'Time'}, 17: {'Calls': 'Calls'}, 18: {'Widget Size': 'Widget Size'}, 19: {'Width (grid units): 10': 'Width is ten grid units', 'Height (grid units): 4': 'Height is four'}, 21: {'Save': 'Save'}, 25: {'Calls Widget': 'Calls settings', 'Column Order': 'Column Order'}, 26: {'ID': 'I D', 'Priority': 'Priority', 'Name': 'Name'}, 27: {'Priority': 'Priority', 'Save': 'Save'}, 32: {'ID': 'I D', 'Priority': 'Priority', 'Name': 'Name'}, 33: {'Urgent': 'Urgent', 'TRAINING — Warehouse alarm': 'warehouse-alarm exercise', 'TRAINING — Community medical standby': 'community medical standby'}, 34: {'TRAINING — Vehicle rescue exercise': 'vehicle-rescue exercise'}, 35: {'Address': 'Address', 'Timestamp': 'Timestamp', 'Dispatched': 'Dispatched'}, 37: {'Dispatched': 'Dispatched'}, 40: {'Units Widget': 'Units Widget'}, 41: {'State': 'State', 'Name': 'Name'}, 42: {'Station': 'Station', 'Type': 'Type', 'Timestamp': 'Timestamp'}, 43: {'Widget Size': 'Widget Size', 'Width (grid units): 10': 'width of ten'}, 44: {'Height (grid units): 3': 'height of three grid units'}, 45: {'Save': 'Save'}, 48: {'Units': 'Units', 'Engine 51': 'Engine fifty-one', 'Available': 'Available'}, 49: {'Squad 3': 'three', 'Responding': 'Responding', 'Reserve Engine 51': 'Reserve Engine fifty-one', 'Out of Service': 'Out of Service'}, 50: {'TRAINING ONLY - Community response vehicle': 'community-response vehicle'}, 54: {'Updated': 'Updated', 'State': 'State'}, 57: {'Personnel': 'Personnel', 'Column Order': 'Column Order'}, 58: {'Status': 'Status', 'Name': 'Name', 'Group': 'Group'}, 59: {'Staffing': 'Staffing', 'Timestamp': 'Timestamp', 'Roles': 'Roles'}, 60: {'Save': 'Save'}, 65: {'Personnel': 'Personnel', 'Status': 'Status', 'Staffing': 'Staffing'}, 66: {'Darren Ritter': 'Darren Ritter', 'Standing By': 'Standing By', 'Status': 'Status'}, 67: {'Delayed': 'Delayed', 'Staffing': 'Staffing'}, 68: {'Blake Gallo': 'Blake Gallo', 'Standing By': 'Standing By', 'Unavailable': 'Unavailable'}, 71: {'Roles': 'Roles', 'Group': 'Group', 'Updated': 'Updated'}, 73: {'Time': 'Time'}, 74: {'Edit': 'Edit'}, 75: {'Done': 'Done'}, 77: {'Notes': 'Notes', 'Time': 'Time'}, 81: {'Notes': 'Notes'}, 82: {'Notes': 'Notes'}, 83: {'Time': 'Time'}, 89: {'Notes': 'Notes'}, 91: {'Personnel': 'Personnel', 'Time': 'Time'}, 92: {'Personnel': 'Personnel', 'Time': 'Time'}, 93: {'Done': 'Done'}, 98: {'Calls': 'Calls', 'ID': 'I D', 'Priority': 'Priority', 'Name': 'Name'}, 99: {'Personnel': 'Personnel'}, 100: {'Time': 'Time'}}, 'context_notes': ['Header gear and plus, row arrows, widget grips and red removal X controls were personally reviewed as actual nontextual UI symbols. The prior or current hold shows the corresponding real header or panel when each operation is discussed.', 'Source024 shows Notes beside Time; source025 shows Notes farther right. Source026 shows Notes removed while the clock stays on the left. No successful clock movement is claimed.', 'Source029 and030 prove real reload readbacks after normal dismissal of the transient development warning. No screenshot pixels were altered.', 'Displayed values, not real-time motion or response acceptance, are demonstrated. Old fictional unit updates are explicitly discussed as stale.', 'Generic font, availability filter and clock-format controls did not establish their intended display effect in this build and are excluded from instructional claims.', 'The long desktop board scrolls; narration explicitly distinguishes this example from a wall display with fewer panels.', 'Cue49 begins in the middle of the spoken name Squad three; the full label Squad 3 is visible for cues48 and49.']}}

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
