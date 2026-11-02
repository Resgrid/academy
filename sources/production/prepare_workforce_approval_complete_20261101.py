"""Bind the complete workforce approval speech to reviewed actual UI screen holds. No approval is inferred."""
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
CFG={'workforce': {'name': 'core-workforce-work-entry-approval', 'cues': 56, 'source_sha256': '2428c6a73ddf8efab643dcb71701de0d10cefd5cb554c892dd8600963ae5b1c3', 'captures_sha256': '7e4e9b2ec90b2f795fb93a5c0531f7993db53546b8bb00c2896bb506942e9d6b', 'audio_sha256': '23131ba7ba4b948a9aaf764b6cae1c912d6a9523ccc3fb9e8619900dac62a566', 'captions_sha256': '9496aaf94c31c4a0a3e32b1195ac2f99d1293df8a36dbbb2db7696ee6d633b39', 'qa_sha256': '47f4aa69427d011e6e746a666e50533d69e23f0484bd24f1e1d49628d87035d7', 'spans': [('01', 1, 8, 1), ('02', 9, 9, 1), ('02', 10, 16, 2), ('03', 17, 21, 3), ('03', 22, 25, 4), ('04', 26, 26, 4), ('04', 27, 32, 5), ('05', 33, 40, 7), ('06', 41, 42, 10), ('06', 43, 47, 11), ('07', 48, 56, 11)], 'refs': {1: {'Work entries': 'Work entries'}, 2: {'Worker': 'worker', 'Hours': 'hours', 'Hours type': 'hours type', 'Establishment': 'establishment'}, 3: {'Context': 'context', 'Approved': 'approval status'}, 4: {'2.00': 'two-hour', 'No': 'No', 'Approved': 'Approved'}, 9: {'Add work entry': 'Add work entry'}, 10: {'Matthew Casey': 'Matthew Casey'}, 11: {'Date *': 'Date'}, 12: {'Hours *': 'Hours', 'Standby': 'Standby', 'Hours type': 'Hours type'}, 13: {'Establishment': 'establishment'}, 18: {'External source': 'External source', 'External id': 'External id'}, 19: {'Approved': 'Approved'}, 20: {'Approved payroll cost': 'Approved payroll cost'}, 21: {'Save': 'Save'}, 22: {'TRAINING ONLY - Approval exercise': 'ONLY, Approval exercise'}, 23: {'1.25': 'one point two five hours', 'Standby': 'Standby'}, 24: {'Approved': 'Approved', 'No': 'No'}, 27: {'Approved': 'Approved'}, 29: {'No': 'No'}, 31: {'Save': 'Save'}, 33: {'Work entries': 'Work entries'}, 34: {'Yes': 'Yes', 'Approved': 'Approved'}, 35: {'1.25': 'one point two five hours', 'Standby': 'Standby'}, 37: {'2.00': 'two-hour', 'No': 'No'}, 39: {'Yes': 'Yes'}, 40: {'Approved payroll cost': 'Approved payroll cost'}, 42: {'2026-11-01': 'November first, twenty twenty-six', 'Filter': 'Filter'}, 44: {'Standby': 'Standby', 'Yes': 'Yes'}, 45: {'Filter': 'Filter'}}, 'context_notes': ['Native date inputs paint11/01/2026 and retain the DOM-backed canonical value2026-11-01. The narration names the same date in words.', 'Source003 checkbox is visibly clear; source005 checkbox selected while the old saved table row still says No. Only source007 proves the saved and reloaded Yes result.', 'Cue26 refers to the actual row pencil icon, personally reviewed in source004. No literal text is invented for this symbol.', 'External reference values are clipped in the narrow form and are not narrated as fully readable values.', 'Cue21 ends with the partial spoken context TRAINING; cue22 continues ONLY, Approval exercise while showing its complete saved context.', 'Source010 shows prepared bounds with the older table still present; source011 is the genuinely applied single-day result.', 'Approval describes this fictional entry flag. No payroll amount, payroll payment, compensation profile approval, cost run or external integration is claimed.']}}

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(key, write=False):
 from PIL import Image, ImageDraw, ImageFont
 from render_walkthrough import load_cues, words, caption_wrap, find_font, WIDTH
 from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
 from expansion_site import lesson_content_digest
 cfg=CFG[key];name=cfg['name'];base=Path('expansion/plans')/(name+'-source-proposal-20261101')
 audio=Path('expansion/audio')/(name+'.m4a');cap=Path('expansion/audio')/(name+'.actual.corrected.srt');qa_path=Path('expansion/audio')/(name+'.actual.qa.json')
 for path,digest in [(base/'lesson.candidate.json',cfg['source_sha256']),(base/'captures.reviewed.v2.json',cfg['captures_sha256']),
                     (audio,cfg['audio_sha256']),(cap,cfg['captions_sha256']),(qa_path,cfg['qa_sha256'])]:
  assert sha(S/path)==digest,str(path)
 lesson=json.loads((S/base/'lesson.candidate.json').read_text());manifest=json.loads((S/base/'captures.reviewed.v2.json').read_text());qa=json.loads((S/qa_path).read_text())
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
