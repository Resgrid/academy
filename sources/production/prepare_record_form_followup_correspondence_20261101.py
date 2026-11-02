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
CFG = {
 'core-form': {
  'name': 'core-record-definition-client-surfaces', 'cues': 60,
  'source_sha256': '5d0b41167590fcef6e50c8c28d03b6f3d8dd228fa9e4bd2a88cab4ae8d6986b9',
  'captures_sha256': '893cc6541c7c2a0be07d447f31da88c2d227dbdfdc1443f5f135a1971119ac62',
  'audio_sha256': '4c21c8fd08765e91ea5cd1ce4a9368cf06eab09895525a4594285ee9084100b8',
  'captions_sha256': 'd09414c6336f20f689d88edecdb23ae014f96fa084d2c50f56abf0064b36c548',
  'qa_sha256': 'df43254b8f7caf2931d29d93e542cffa1f89b4ccef5c6376c64cf035232dca7a',
  'spans': [('01',1,8,1),('02',9,15,3),('03',16,22,4),('04',23,23,7),('04',24,29,5),
            ('05',30,30,7),('05',31,37,8),('06',38,38,8),('06',39,44,9),
            ('07',45,46,9),('07',47,51,13),('08',52,60,13)],
  'refs': {
   3:{'Client surfaces':'Client surfaces'},4:{'Responder':'Responder','IC':'IC'},5:{'Unit':'Unit','Dispatch':'Dispatch'},
   10:{DRAFT:'Training Only, IC coordination note'},11:{DRAFT:'Draft'},
   12:{'Definition created. Edit the schema, validate, then publish.':'edit the schema, validate, then publish'},
   13:{'Lifecycle preset':'Lifecycle preset','QuickEntry':'Quick Entry'},
   16:{'Client surfaces':'Client surfaces','Responder':'Responder','IC':'IC'},17:{'Unit':'Unit','Dispatch':'Dispatch'},
   18:{'IC':'IC'},19:{'Allow offline':'Allow offline'},23:{'Validate':'Validate'},24:{'The definition is valid.':'The definition is valid'},
   30:{'Save draft':'Save draft'},31:{'Draft saved.':'Draft saved'},32:{DRAFT:'Draft'},
   34:{'Review impact & publish':'Review impact and publish'},38:{'Review impact & publish':'Review impact and publish'},
   39:{'Enabled':'Enabled','Client surfaces':'Client surfaces'},40:{'IncidentCommand':'Incident Command'},
   41:{'Yes':'Yes','Client surfaces':'Client surfaces'},42:{'Responder':'Responder','Unit':'Unit','Dispatch':'Dispatch',
       'This version is not offered to this app.':'this version is not offered to that app'},
   43:{'Clients at records.v1b or later can author this version.':'clients at records version one B or later can author this version'},
   45:{'Publishing freezes this version. Existing drafts keep their version until migrated; finalized records never change.':'publishing freezes the version'},
   46:{'Publish':'Publish'},47:{PUBLISHED:'Published'},48:{READONLY:'published, read-only notice'},52:{'Open new draft':'Open new draft'},
  },
  'context_notes': ['Cue38 shows the actual Review impact & publish entry control; cue39 cuts to its actual impact table. Both parts of the navigation instruction are shown in the ordered scene.'],
 },
 'ic-record': {
  'name': 'app-ic-record-create-revise-finalize', 'cues': 58,
  'source_sha256': '6229600323166e3bf461d39729a9a1909945b24c0dbfedd2c5d1e1705276128c',
  'captures_sha256': '712fe82fb23a884e69082ee3a0faf0f50d71e2044883595896038a64af27d742',
  'audio_sha256': 'ae8952429508ca325c50c98262ad63cd6ab56b3ff4ed920c866c26a9796ea7af',
  'captions_sha256': '7fcdcd06761e97345f1061521829fc892d3d173a79500eab6b7759ed6df155b5',
  'qa_sha256': 'eb92d9482093e5dc2e96174ab4b5c854ea62075726fbddf0e9a9f62dc17016aa',
  'spans': [('01',1,2,1),('01',3,7,2),('02',8,14,3),('03',15,17,4),('03',18,21,5),
            ('04',22,25,6),('04',26,28,8),('05',29,30,9),('05',31,36,10),
            ('06',37,37,10),('06',38,44,11),('07',45,45,11),('07',46,51,12),('08',52,58,12)],
  'refs': {
   1:{'Records':'Records'},3:{'New Record':'New Record',TITLE:'Training Only, IC coordination note'},
   4:{'Academy software exercises':'Academy software exercises'},5:{TITLE:'that named form'},
   8:{'This form is filled in online only.':'This form is filled in online only'},
   9:{'Details':'Details','Summary':'Summary','Notes':'Notes'},12:{'Summary':'summary'},13:{'Notes':'notes'},
   14:{'Save and send':'Save and send'},15:{'Summary':'Summary','Notes':'Notes'},16:{SUMMARY:'Training Only'},
   17:{'Save and send':'Save and send'},18:{'D-HGYT8':'draft reference'},19:{'DRAFT':'Draft'},
   22:{'DRAFT':'draft','Notes':'Notes'},23:{UPDATE:'Training Update'},24:{UPDATE:'was reviewed for software practice'},
   25:{'Save':'Save'},26:{'Notes':'Notes'},27:{'Summary':'Summary','DRAFT':'Draft'},
   29:{ATTEST:'I attest this Record is complete and accurate'},30:{'Finalize':'Finalize'},31:{ATTEST:'attestation'},32:{'Finalize':'Finalize'},
   37:{'Finalize':'Finalize'},38:{'FINALIZED':'Finalized','ICNOTE-2026-0001':'I C note'},
   39:{'ICNOTE-2026-0001':'twenty twenty-six, zero zero zero one'},40:{'Summary':'Summary','Notes':'Notes'},
   45:{'Back':'Back'},46:{'RECENT':'Recent','ICNOTE-2026-0001':'same record number',SUMMARY:'coordination handover summary'},
   47:{'FINALIZED':'Finalized'},48:{'DRAFTS':'Drafts'},
  },
  'context_notes': ['Cue2 names the visibly pictured plus icon at the lower right. It has no accessible name in the app, so no literal or accessible name is invented. Its actual pixels were personally reviewed at scene level; literal-name automation covers Records and the resulting New Record screen.',
                    'The saved revision uses source008, the normal workspace reopening without the offline notice. Excluded source007 cannot establish a current server result.',
                    'No uploaded attachment, review submission, external notification, offline authoring or operational incident is claimed.'],
 },
}


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
