"""Prepare exact102-cue amendment correspondence; never infer hearing or review."""
import argparse,hashlib,json,sys
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
NAME='core-records-amendment-and-revisions';BASE=Path('expansion/plans')/(NAME+'-source-proposal-20261101')
NOTICE='An amendment is in progress. The last finalized revision remains authoritative until the amendment is finalized.'
ATTEST='I attest that this record is accurate and complete to the best of my knowledge.'
AMENDED='Amended (TRAINING-CORRECTION)'
CONFIG={'id':NAME,'base':str(BASE),'lesson_sha256':'41ae73e165868b28fa20902934555d7ceac609e736d165a4db7c7dffcf969171','manifest_sha256':'e59787238f3422358f134eb236284bffd5b8ee2a6797a6b2cdaeb147c5f9716b','audio_sha256':'1298b0dff37bc5d2c94e4a267345c03be22819d132ef1c968b65a4882aaced08','caption_suffix':'.actual.corrected.srt','captions_sha256':'ebfbf6f8f9d90bd693c2af6a2f084158f4ca01bf987481c086619bef678e5536','qa_suffix':'.actual.qa.json','qa_sha256':'4338cdc9e55462a71828691ab0b0cae5b888805e750d3e56c51a8694efba6cdb','cue_count':102}
REFERENCES={
1:{'View Record':'Open the intended record'},2:{'Finalized':'Finalized','TRN-2026-0002':'record number T R N'},3:{'TRN-2026-0002':'twenty-six, zero zero zero two','D-YXS93':'draft reference D, Y X S nine three'},4:{'Course':'Course','ACADEMY-REC-29':'Academy, R E C, twenty-nine'},5:{'Author':'author','Station / group':'group','Narrative':'narrative'},8:{'Amend':'Amend'},
9:{'Training TRN-2026-0002':'same Training record'},10:{NOTICE:'an amendment is in progress'},11:{NOTICE:'until the amendment is finalized'},13:{'Station / group':'Station slash group','External ID':'External ID','Start':'dates','End':'dates','Course':'Course','Course code':'Course code','Location':'Location'},14:{'Narrative':'Narrative'},
18:{'Course code':'Course code'},19:{'ACADEMY-REC-29A':'Academy, R E C, twenty-nine A'},20:{'Course':'Course title','Location':'fictional workspace','Narrative':'software-only narrative'},23:{'ACADEMY-REC-29A':'new field value',NOTICE:'amendment notice'},
25:{'Reason code':'Reason code','Reason':'Reason'},27:{'TRAINING-CORRECTION':'Training Correction','Reason code':'reason code'},28:{ATTEST:'attestation'},29:{'Save draft':'Save draft'},30:{'Save and finalize':'Save and finalize'},31:{'Reason':'reason',ATTEST:'attestation'},
33:{'ACADEMY-REC-29A':'corrected Course entry'},34:{'ACADEMY-REC-29A':'twenty-nine A',NOTICE:'amendment-in-progress notice'},35:{'Finalized':'Finalized',NOTICE:'warning'},38:{'Edit':'Edit','Abandon amendment':'Abandon amendment','Finalize':'Finalize'},39:{'Reason':'reason',ATTEST:'attestation'},
41:{'Finalize':'Finalize','Reason code':'reason code','TRAINING-CORRECTION':'Training Correction','Reason':'Reason'},42:{'Correct fictional course code only.':'Correct fictional course code only'},43:{ATTEST:'attestation'},44:{ATTEST:'complete to the best of your knowledge'},48:{'Finalize':'Finalize'},
49:{'Amended':'Amended'},50:{'TRN-2026-0002':'record number','D-YXS93':'draft reference','Course':'Course'},51:{'ACADEMY-REC-29A':'twenty-nine A'},
56:{'History':'History'},57:{'2':'Revision two',AMENDED:'Amended with the Training Correction reason code'},58:{'1':'one','Finalized':'Finalized'},60:{'Compare with previous':'Compare with previous',AMENDED:'amended row'},
63:{'Revision comparison':'Revision comparison','Revision 1 compared with revision 2':'Revision one compared with revision two'},64:{'Field':'Field','Before':'Before','After':'After'},65:{'Details.CourseCode':'Details dot Course Code','ACADEMY-REC-29':'Academy, R E C, twenty-nine'},66:{'ACADEMY-REC-29A':'twenty-nine A'},
71:{'History':'History','2':'revision two',AMENDED:'Amended row'},72:{'View':'View'},74:{'View':'View'},
77:{'Complete department record TRN-2026-0002 — revision 2':'record number and revision two'},78:{'Details':'Details','Course Code':'Course Code','ACADEMY-REC-29A':'twenty-nine A'},79:{'Fictional software workspace':'fictional location'},80:{'Attachments':'Attachments','academy-record-entry-handout.txt':'exercise handout'},81:{'Complete department record TRN-2026-0002 — revision 2':'revision heading'},
83:{'History':'History','1':'revision one','Finalized':'Finalized'},84:{'View':'View'},
89:{'Complete department record TRN-2026-0002 — revision 1':'revision one','Course Code':'Course Code'},90:{'ACADEMY-REC-29':'twenty-nine'},91:{'Attachments':'attachment metadata'},
99:{'Reason':'reason',ATTEST:'attestation'},100:{'Amended':'saved result'},101:{'Revision comparison':'comparison'}
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def prepare(write=False):
 sys.path.insert(0,str(ROOT/'scripts'))
 from render_walkthrough import load_cues,words,find_font,caption_wrap
 from verify_capture_evidence import _Validator,_normalized,instruction_scene_digest
 from expansion_site import lesson_content_digest
 from PIL import Image,ImageDraw,ImageFont
 c=CONFIG;lessonfile=BASE/'lesson.candidate.json';manifestfile=BASE/'captures.reviewed.json';audio=Path('expansion/audio')/(NAME+'.m4a');captions=Path('expansion/audio')/(NAME+c['caption_suffix']);qafile=Path('expansion/audio')/(NAME+c['qa_suffix']);extra=BASE/'additional-literal-observations-20261101.json'
 for file,pin in [(lessonfile,c['lesson_sha256']),(manifestfile,c['manifest_sha256']),(audio,c['audio_sha256']),(captions,c['captions_sha256']),(qafile,c['qa_sha256']),(extra,'df64ceb21d12161843fcfc34a66a729618807f7c810814ebf9ed852bb9babec5')]:assert sha(S/file)==pin,str(file)
 lesson=read(S/lessonfile);manifest=deepcopy(read(S/manifestfile));rows={r['id']:r for r in manifest['screenshots']}
 for obs in read(S/extra)['observations']:
  row=rows[obs['capture_id']];assert row['sha256']==obs['source_sha256'];row['visible_labels']=list(dict.fromkeys([*row['visible_labels'],*obs['labels']]));row['additional_literal_review']={'file':str(extra),'sha256':sha(S/extra)}
 observed={}
 for id,row in rows.items():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256'];v=_Validator(S);observed[id]=v.observations(row,id);assert not v.issues,v.issues
 cues=load_cues(S/captions);qa=read(S/qafile);assert len(cues)==102 and qa['passed'] and not qa['issues'] and qa['silent_corrected_cues']==0 and qa['audio']['sha256']==c['audio_sha256'];duration=qa['audio']['duration_seconds']
 spans=[];cursor=0
 for sc in lesson['scenes']:
  first=cursor+1;text=''
  while words(text)!=words(sc['narration']):
   assert cursor<len(cues);text+=' '+cues[cursor]['text'];cursor+=1;assert words(sc['narration'])[:len(words(text))]==words(text)
  if sc['id']=='14':spans.extend([('14',first,98,sc['capture_refs'][0]),('14',99,99,'007-amendment-reason-attestation-prepared'),('14',100,100,'008-fresh-amended-number-retained'),('14',101,102,'002-actual-course-code-comparison')])
  else:spans.append((sc['id'],first,cursor,sc['capture_refs'][0]))
 assert cursor==102 and [n for _,a,b,_ in spans for n in range(a,b+1)]==list(range(1,103))
 holds=[];entries=[]
 for i,(scene,first,last,id) in enumerate(spans):
  start=0.0 if i==0 else cues[first-1]['start'];end=cues[spans[i+1][1]-1]['start'] if i+1<len(spans) else duration;holds.append({'scene_id':scene,'screenshot_id':id,'start':start,'end':end,'first_cue':first,'last_cue':last})
  for n in range(first,last+1):
   cue=cues[n-1];aliases=REFERENCES.get(n,{});assert cue['start']>=start and cue['end']<=end and {_normalized(x) for x in aliases}<=observed[id],(n,id)
   entry=dict(cue,cue=n,scene_id=scene,screenshot_id=id,required_labels=list(aliases),spoken_references=aliases,instructional=bool(aliases));v=_Validator(S);v.spoken_references(entry,{_normalized(x) for x in aliases},str(n),True);assert not v.issues,v.issues;entries.append(entry)
 scenes=[]
 for sc in lesson['scenes']:
  selected=[h for h in holds if h['scene_id']==sc['id']];selectedc=[{k:v for k,v in e.items() if k!='scene_id'} for e in entries if e['scene_id']==sc['id']];assert words(' '.join(x['text'] for x in selectedc))==words(sc['narration'])
  union=set().union(*(observed[h['screenshot_id']] for h in selected));assert {_normalized(x) for x in sc['required_labels']}<=union and any(e['required_labels'] for e in selectedc)
  scene={'id':sc['id'],'title':sc['title'],'kind':'operational','start':selected[0]['start'],'end':selected[-1]['end'],'visual_required_labels':sc['required_labels'],'screens':[{k:h[k] for k in ['screenshot_id','start','end']} for h in selected],'captions':selectedc};scene['proposed_mapping_sha256']=instruction_scene_digest(scene,rows);scenes.append(scene)
 learner=deepcopy(lesson);learner['scope_limits']=[x for x in learner['scope_limits'] if 'Source candidate only' not in x];assert lesson_content_digest(lesson)==lesson_content_digest(learner)
 font=find_font();draw=ImageDraw.Draw(Image.new('RGB',(1920,1080)));tf=ImageFont.truetype(str(font),27);cf=ImageFont.truetype(str(font),30);geometry={'method':'Unchanged renderer font sizes and1920x1080 geometry; numerical measurement only.','font_sha256':sha(font),'titles':[],'captions':[]}
 for sc in scenes:
  width=draw.textbbox((0,0),'TRAINING ONLY · fictional department · '+sc['title'],font=tf)[2];assert width<=1856;geometry['titles'].append({'scene_id':sc['id'],'width_pixels':width,'fits':True})
 for i,cue in enumerate(cues,1):
  lines=caption_wrap(draw,cue['text'],cf,1800);width=max(draw.textbbox((0,0),x,font=cf)[2] for x in lines);geometry['captions'].append({'cue':i,'lines':lines,'maximum_width_pixels':width,'fits':True})
 proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_file':str(lessonfile),'lesson_sha256':c['lesson_sha256'],'audio_file':str(audio),'audio_sha256':c['audio_sha256'],'captions_file':str(captions),'captions_sha256':c['captions_sha256'],'qa_file':str(qafile),'qa_sha256':c['qa_sha256'],'duration_seconds':duration,'scenes':scenes,'holds':holds,'cues':entries,'cue_count':102,'source_images':13,'holds_count':len(holds),'learner_content_sha256':lesson_content_digest(learner),'review_state':'proposal_only_no_review_or_hearing_approval_inferred'}
 if write:
  dest=S/'expansion/plans'/(NAME+'-complete-correspondence-20261101');assert not dest.exists();dest.mkdir()
  for file,data in [('captures.source-relative.json',manifest),('correspondence.proposed.json',proposal),('lesson.learner-projection.proposed.json',learner),('caption-layout-measurements.json',geometry)]:
   with (dest/file).open('x') as stream:stream.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
  (dest/'cue-screen-correspondence.txt').write_text('\n\n'.join(f"Cue{e['cue']:03} · scene{e['scene_id']} · {e['start']:.3f}–{e['end']:.3f} · {e['screenshot_id']}\n{e['text']}\nLiteral -> exact speech: {json.dumps(e['spoken_references'],ensure_ascii=False)}" for e in entries)+'\n')
 return {'passed':True,'lesson_id':NAME,'cues':102,'scenes':14,'holds':len(holds),'source_images':13,'duration_seconds':duration,'geometry_fits':True,'written':write,'actual_review_and_hearing':'not inferred'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');args=p.parse_args();print(json.dumps(prepare(args.prepare),indent=2))
