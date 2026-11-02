"""Check actual caption-to-screen proposals; never infer hearing or final approval."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues,words
from verify_capture_evidence import _Validator,_normalized
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
NOTE='TRAINING ONLY — virtual access plan reviewed in the Academy software exercise. No real response or physical inspection requested.'
CHECKNOTE='TRAINING ONLY — virtual personnel check-in for Academy software practice. No physical arrival, GPS or safety verification is asserted.'
CALL='TRAINING ONLY — Responder call and check-in practice (FD51-2026-0001)'
ORDER='TRAINING ONLY — Assigned software practice';ORDERID='WO-2099-000001 · Assigned · Normal'
ACCEPTED='2026-10-26 19:40 · Assignment accepted';PROGRESS='2026-10-26 19:43 · Status changed → In progress'
CONFIG={
'notes-checkin':{'id':'app-responder-call-notes-personnel-checkin','folder':'app-responder-call-notes-personnel-checkin-source-proposal-20261101','lesson_sha256':'3c13f2888bb10aaedc505d4410daa26e3a220b92f696241741608017e63a52fa','cue_count':57,'spans':[('01',1,8,'208-disposable-call-created'),('02',9,16,'213-disposable-call-note-prepared'),('03',17,24,'215-disposable-call-note-reopened'),('04',25,32,'218-personnel-timer-before-check-in'),('05',33,40,'219-personnel-check-in-confirmation'),('06',41,49,'220-personnel-check-in-history'),('07',50,57,'220-personnel-check-in-history')],
'references':{2:{'Call Details':'Call Details'},3:{CALL:'Training Only, Responder call and check-in practice'},4:{CALL:'twenty twenty-six, zero zero zero one'},8:{'Notes':'Notes'},9:{'Call Notes':'Call Notes','Search notes...':'search field','Add Note':'Add Note'},10:{NOTE:'virtual access plan'},11:{NOTE:'Academy software exercise'},12:{NOTE:'physical inspection requested'},14:{'Add Note':'Add Note'},17:{'Call Notes':'Call Notes'},18:{NOTE:'same complete text','Wallace Boden':'Wallace Boden'},19:{'10/26/2026 15:00:00':'recorded timestamp'},21:{NOTE:'actual saved text'},25:{'Check-In':'Check-In tab'},26:{'Wallace Boden':'Wallace Boden','Personnel':'Personnel','Check In':'Check In'},27:{'42:28':'forty-two minutes and twenty-eight seconds'},28:{'17.5 / 60 min':'seventeen point five of sixty minutes elapsed'},29:{'Wallace Boden':'whose timer'},30:{'Quick Check-In':'Quick Check-In','Check-In History ▼':'Check-In History'},31:{'Check In':'Check In button','Wallace Boden':"Wallace Boden's card"},33:{'Select Check-In Type: Wallace Boden':'Select Check-In Type, Wallace Boden'},34:{'Personnel':'Personnel','Add Note (Optional)':'Add Note is optional'},35:{CHECKNOTE:'virtual personnel check-in'},36:{CHECKNOTE:'Academy software practice'},38:{'Personnel':'selected type','Add Note (Optional)':'note','Confirm Check-In':'Confirm Check-In'},41:{'Personnel':'Personnel','59:38':'fifty-nine minutes and thirty-eight'},42:{'Last check-in: 0.1 min ago':'Last check-in, zero point one minutes ago'},43:{'Check-In History ▲':'Check-In History','Personnel':'Personnel'},44:{CHECKNOTE:'practice note','2026-10-26 20:13':'timestamp'},45:{'Check-In History ▲':'saved history','59:38':'changed timer'},48:{'Check-In History ▲':'saved entry'},57:{'Check-In History ▲':'check-in history',CHECKNOTE:'saved note'}}},
'work-order':{'id':'app-responder-work-order-assignment-review','folder':'app-responder-work-order-assignment-review-source-proposal-20261101-v2','lesson_sha256':'348c3a9dcd531c8fe7dcf024cdebbd2b4627ba2de818958f451755fe3476d396','cue_count':50,'spans':[('01',1,8,'190-assigned-order-before-acceptance'),('02',9,15,'190-assigned-order-before-acceptance'),('02',16,21,'191-assigned-order-on-hold-reason'),('03',22,28,'192-assigned-order-completion-inputs'),('04',29,34,'190-assigned-order-before-acceptance'),('05',35,41,'193-assigned-order-accepted-activity'),('06',42,50,'193-assigned-order-accepted-activity')],
'references':{1:{'Work orders':'Work orders'},3:{ORDER:'Training Only, Assigned software practice'},4:{ORDERID:'Assigned','Inspection':'Inspection'},5:{'Station: Firehouse 51':'Firehouse fifty-one'},7:{'Steps':'Steps'},9:{'Accept assignment':'Accept assignment','Steps':'Steps'},10:{'Change status':'Change status','Update status':'Update status'},11:{'Log hours':'Log hours','Save hours':'Save hours'},16:{'On hold':'On hold','Change status':'Change status'},17:{'Reason':'Reason','Update status':'Update status'},18:{ORDERID:'Assigned'},20:{'Reason':'reason'},22:{'Completed':'Completed','What was done to fix it':'What was done to fix it','Cause':'Cause'},23:{'All steps are complete':'All steps are complete'},24:{'All steps are complete':'switch','Update status':'Update status'},29:{ORDER:'intended assignment'},30:{ORDER:'title',ORDERID:'Assigned status'},31:{'Accept assignment':'Accept assignment'},35:{'Activity':'Activity',ACCEPTED:'Assignment accepted'},36:{PROGRESS:'Status changed to In progress'},37:{'Change status':'Change status','In progress':'In progress'},40:{'Log hours':'Log hours','Add comment':'comment','Take photo':'photo controls','Choose photo':'photo controls'},50:{'Activity':'Activity'}}}
}
def prepare(key,write=False):
 c=CONFIG[key];b=Path('expansion/plans')/c['folder'];l=b/'lesson.candidate.json';assert sha(S/l)==c['lesson_sha256'];lesson=json.loads((S/l).read_text());raw=Path('expansion/audio')/(c['id']+'.actual-raw.srt');cues=load_cues(S/raw);assert len(cues)==c['cue_count'];manifest=deepcopy(json.loads((S/b/'captures.reviewed.json').read_text()));rows={r['id']:r for r in manifest['screenshots']}
 extra=S/b/'additional-literal-observations-20261101.json'
 if extra.exists():
  for obs in json.loads(extra.read_text())['observations']:
   r=rows[obs['capture_id']];assert r['sha256']==obs['source_sha256'];r['visible_labels']=list(dict.fromkeys(r['visible_labels']+obs['labels']))
 observed={}
 for id,row in rows.items():
  assert sha(S/row['file'])==row['sha256'] and sha(S/row['dom_file'])==row['dom_sha256'];v=_Validator(S);observed[id]=v.observations(row,id);assert not v.issues,v.issues
 result=[]
 for scene,first,last,id in c['spans']:
  for n in range(first,last+1):
   cue=cues[n-1];refs=c['references'].get(n,{});assert {_normalized(x) for x in refs}<=observed[id],(n,id,set(refs)-observed[id]);r=dict(cue,cue=n,scene_id=scene,screenshot_id=id,required_labels=list(refs),spoken_references=refs,instructional=bool(refs));v=_Validator(S);v.spoken_references(r,{_normalized(x) for x in refs},str(n),True);assert not v.issues,v.issues;result.append(r)
 assert len(result)==c['cue_count']
 for scene in lesson['scenes']:
  assert words(' '.join(r['text'] for r in result if r['scene_id']==scene['id']))==words(scene['narration'])
 proposal={'created_at':datetime.now(timezone.utc).isoformat(),'lesson_file':str(l),'lesson_sha256':c['lesson_sha256'],'actual_raw_captions':str(raw),'actual_raw_captions_sha256':sha(S/raw),'scene_count':len(lesson['scenes']),'cue_count':len(cues),'screen_holds':len(c['spans']),'cues':result,'word_timings_interpolated':False,'final_end_requires_downloaded_audio_duration':True,'review_state':'proposal_only; full audio QA, Root correspondence, genuine User hearing and final encoded/browser reviews still required','approved_for_render':False}
 if write:
  dest=S/'expansion/plans'/(c['id']+'-literal-cue-proposal-20261101.json');assert not dest.exists();dest.write_text(json.dumps(proposal,indent=2,ensure_ascii=False)+'\n')
 return {'lesson_id':c['id'],'actual_cues':len(cues),'scene_count':len(lesson['scenes']),'source_dom_labels_and_spoken_references':'passed','word_timings_interpolated':False,'written':write,'approved_for_render':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('lesson',choices=CONFIG);p.add_argument('--prepare',action='store_true');a=p.parse_args();print(json.dumps(prepare(a.lesson,a.prepare),indent=2))
