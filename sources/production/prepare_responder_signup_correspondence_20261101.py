"""Prepare exact55-cue Responder signup correspondence; never infer hearing or review."""
import argparse,hashlib,json,sys
from copy import deepcopy
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
NAME='app-responder-shift-signup-withdraw';BASE=Path('expansion/plans')/(NAME+'-source-proposal-20261101')
TITLE='TRAINING — Academy signup practice'
DATE='Tuesday, October 27, 2026'
TIME='1:00 PM – 3:00 PM'
REMOVAL='You will be removed from the roster for Tuesday, October 27, 2026.'
CONFIG={'id':NAME,'base':str(BASE),'lesson_sha256':'605e830bca85624daec2f623a21fcce9dd791fef5c2618ad21c85d0629237e53','manifest_sha256':'c1187755e44a9db27d66618d0bcdf1e311e59c0fa91b029ed529d8fd795114bf','audio_sha256':'d8a0cfbccd23fbd2a1c1def05c319991f2f21e1d0a8c145b12452290aee315ac','caption_suffix':'.actual.corrected.srt','captions_sha256':'aceec589174a687d55d4c55ec0d09e1402044fe1a54a852f33f0a158069ce148','qa_suffix':'.actual.qa.json','qa_sha256':'31515aa2322b69a2ed9a3a049454ccc3e34dd5c771033253370be93021b61592','cue_count':55}
REFERENCES={
1:{'Roster':'day detail'},
2:{TITLE:'Training, Academy signup practice'},
3:{DATE:'October twenty-seventh, twenty twenty-six',TIME:'from one until three in the afternoon'},
5:{'Open slots: 2':'Open slots shows two'},
6:{'Open needs':'Open needs','Firehouse 51':'Firehouse fifty-one','Chief':'Chief','Needed: 2':'Needed, two'},
7:{'Roster':'Roster','No one is on this day yet.':'no one is on this day yet'},
9:{'Sign Up':'Sign Up'},
10:{'Choose your team':'Choose your team'},
12:{'Firehouse 51':'Firehouse fifty-one','Chief: 2':'Chief, two','Open: 2':'Open, two'},
14:{DATE:'shift date',TIME:'time'},
15:{'Back':'Back'},16:{'Confirm sign-up':'Confirm sign-up'},
17:{'You are on':'You are on','Open slots: 1':'Open slots'},18:{'Open slots: 1':'one'},
19:{'Roster':'Roster','FIREHOUSE 51':'Firehouse fifty-one','Wallace Boden':'Wallace Boden','YOU':'You label'},
20:{'Open needs':'Open needs','Chief':'Chief','Needed: 1':'Needed, one'},
22:{'Wallace Boden':'named roster entry','Open slots: 1':'count'},
26:{'Withdraw':'Withdraw'},27:{TITLE:'title',DATE:'date',TIME:'hours'},
29:{'Request trade':'Request trade'},32:{'Withdraw':'Withdraw'},
33:{'Withdraw from this shift?':'Withdraw from this shift'},34:{REMOVAL:'removed from the roster for Tuesday, October twenty-seventh'},
35:{TITLE:'shift title',TIME:'one-to-three time'},36:{'Back':'Back'},37:{'Withdraw':'Withdraw button'},
39:{'Sign Up':'Sign Up'},40:{'Open slots: 2':'Open slots is two','Open needs':'Open needs','Chief':'Chief','Needed: 2':'Needed, two'},
41:{'Roster':'Roster','No one is on this day yet.':'no one is on this day yet'},
52:{TITLE:'occurrence','Open needs':'team needs','Roster':'personal roster state'},
54:{'Roster':'returned result'}
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
 for file,pin in [(lessonfile,c['lesson_sha256']),(manifestfile,c['manifest_sha256']),(audio,c['audio_sha256']),(captions,c['captions_sha256']),(qafile,c['qa_sha256']),(extra,'0095bdd22d362f724b8cef882e7a36828ba56f30d6cb3d6cf0aef04b206f9b4c')]:assert sha(S/file)==pin,str(file)
 lesson=read(S/lessonfile);manifest=deepcopy(read(S/manifestfile));rows={r['id']:r for r in manifest['screenshots']}
 for obs in read(S/extra)['observations']:
  row=rows[obs['capture_id']];assert row['sha256']==obs['source_sha256'];row['visible_labels']=list(dict.fromkeys([*row['visible_labels'],*obs['labels']]));row['additional_literal_review']={'file':str(extra),'sha256':sha(S/extra)}
 observed={}
 for id,row in rows.items():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256'];v=_Validator(S);observed[id]=v.observations(row,id);assert not v.issues,v.issues
 cues=load_cues(S/captions);qa=read(S/qafile);assert len(cues)==55 and qa['passed'] and not qa['issues'] and qa['silent_corrected_cues']==0 and qa['audio']['sha256']==c['audio_sha256'];duration=qa['audio']['duration_seconds']
 spans=[];cursor=0
 for sc in lesson['scenes']:
  first=cursor+1;text=''
  while words(text)!=words(sc['narration']):
   assert cursor<len(cues);text+=' '+cues[cursor]['text'];cursor+=1;assert words(sc['narration'])[:len(words(text))]==words(text)
  spans.append((sc['id'],first,cursor,sc['capture_refs'][0]))
 assert cursor==55 and [n for _,a,b,_ in spans for n in range(a,b+1)]==list(range(1,56))
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
 proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_file':str(lessonfile),'lesson_sha256':c['lesson_sha256'],'audio_file':str(audio),'audio_sha256':c['audio_sha256'],'captions_file':str(captions),'captions_sha256':c['captions_sha256'],'qa_file':str(qafile),'qa_sha256':c['qa_sha256'],'duration_seconds':duration,'scenes':scenes,'holds':holds,'cues':entries,'cue_count':55,'source_images':5,'distinct_source_images':4,'holds_count':len(holds),'learner_content_sha256':lesson_content_digest(learner),'review_state':'proposal_only_no_review_or_hearing_approval_inferred'}
 if write:
  dest=S/'expansion/plans'/(NAME+'-complete-correspondence-20261101');assert not dest.exists();dest.mkdir()
  for file,data in [('captures.source-relative.json',manifest),('correspondence.proposed.json',proposal),('lesson.learner-projection.proposed.json',learner),('caption-layout-measurements.json',geometry)]:
   with (dest/file).open('x') as stream:stream.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
  (dest/'cue-screen-correspondence.txt').write_text('\n\n'.join(f"Cue{e['cue']:03} · scene{e['scene_id']} · {e['start']:.3f}–{e['end']:.3f} · {e['screenshot_id']}\n{e['text']}\nLiteral -> exact speech: {json.dumps(e['spoken_references'],ensure_ascii=False)}" for e in entries)+'\n')
 return {'passed':True,'lesson_id':NAME,'cues':55,'scenes':7,'holds':len(holds),'source_images':5,'distinct_source_images':4,'duration_seconds':duration,'geometry_fits':True,'written':write,'actual_review_and_hearing':'not inferred'}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');args=p.parse_args();print(json.dumps(prepare(args.prepare),indent=2))
