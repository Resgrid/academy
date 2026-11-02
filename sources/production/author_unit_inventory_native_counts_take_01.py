#!/usr/bin/env python3
"""Propose a genuine90cue/25hold native-count assembly; NEVER renders.

Default checks held inputs only. --write-proposed requires the exact User full
listening receipt, exact full audio QA and a repeated complete decode. Root must
read the proposed files before any separately authorized renderer invocation.
No timing estimate, caption split, source reapproval, frame/playback approval,
canonical or publication write occurs.
"""
import argparse
from datetime import datetime,timezone
import hashlib,json,sys,tempfile,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues,words,validate_inputs,audio_duration
from verify_capture_evidence import _Validator,_normalized,instruction_scene_digest
from native_capture_public import validate_native_source,unique_json

NAME='app-unit-inventory-native-counts'
BASE=Path('expansion/plans/'+NAME+'-capture-freeze-20261028')
CAPS=Path('expansion/plans/'+NAME+'-020-label-review-20261029/captures.native-reviewed.json')
OUT=S/'expansion/plans'/ (NAME+'-take-01-proposed-20261029')
SOURCE='6bb6d3cb9165fec2156a0fc24d6ca4a3ac4d5d8416fb0a0365e15aafe6ceb701'
AUDIO='5e237fcf9cd38f043211d975932abc446cc4aa7a7210ef3a1333618426859c8b'
SRT='71f1b8582733001ae632c018b9015c0fb26fe49cd9db6b4acc34cbaa1d80b13d'
RAW='180be23429798c324034b40e7a01ec71622a10604dbadf80c3b095b72072c88b'
QA='dc534839d897e28b99b309eaf2b43186eca73968739c6d934ad215b6d7d82c41'
LISTEN='5d9816ede39c22fcafd59c420aae43ac17c75c56c1698dbfda3ecb4d63d4b23f'
MANIFEST='dfefdc0f46e281cc3002ef156c25aefc23d771c80f70280bbb61010d743d215c'
PINS={BASE/(NAME+'.narrated-source.json'):SOURCE,
      BASE/'source-freeze.json':'421693c5a83525b284e3073eb10f6778680ecfbb62f46a5f1638b458f20376ac',
      CAPS:MANIFEST,Path('expansion/audio/'+NAME+'.m4a'):AUDIO,
      Path('expansion/audio/'+NAME+'.srt'):SRT,
      Path('expansion/audio/'+NAME+'-generated-20261028.raw.srt'):RAW,
      Path('expansion/audio/'+NAME+'.actual.qa.json'):QA,
      Path('expansion/audio/'+NAME+'.listening-review.json'):LISTEN}
RANGES=[(1,7),(8,15),(16,22),(23,29),(30,36),(37,43),(44,50),(51,58),(59,64),(65,72),(73,81),(82,90)]
# firstcue,lastcue,original native image number; all cuts are real SRT starts.
PICTURES=[(1,2,7),(3,4,8),(5,7,15),(8,15,15),(16,16,15),(17,19,16),(20,20,15),(21,22,16),
 (23,29,16),(30,30,16),(31,36,17),(37,37,17),(38,43,18),(44,45,18),(46,50,19),
 (51,51,19),(52,58,20),(59,59,20),(60,64,21),(65,72,22),(73,73,22),(74,81,23),
 (82,83,24),(84,85,25),(86,90,26)]
H0='In progress · 0 of 3 counted · 0 differences'
H1='In progress · 1 of 3 counted · 1 differences'
H2='In progress · 1 of 3 counted · 0 differences'
H3='In progress · 3 of 3 counted · 0 differences'
HC='Completed · 3 of 3 counted · 0 differences'
TITLE='Ambulance 61 check 2026-10-28'
HEADING='Inventory · Ambulance 61'
REFERENCES={
 1:{'Settings':'Settings','Active Unit':'Active Unit'},3:{'Select Unit':'Select Unit'},4:{'Ambulance 61':'Ambulance 61'},
 5:{HEADING:'Inventory'},8:{HEADING:'Ambulance 61'},
 9:{'Academy training batteries':'training batteries','Nitrile gloves':'nitrile gloves'},10:{'Training oxygen cylinder':'training oxygen cylinders'},11:{'Recent counts':'Recent counts'},
 16:{'Start count':'Start count'},17:{TITLE:'new count'},19:{H0:'zero of three counted'},20:{'Completed':'completed count'},21:{TITLE:'new record'},
 23:{'Expected 5 packs':'Expected','Expected 24 boxes':'Expected','Expected 6 cylinders':'Expected'},
 24:{'Expected 5 packs':'five','Expected 24 boxes':'twenty four','Expected 6 cylinders':'six'},26:{H0:'zero of three counted'},27:{'Complete':'Complete'},28:{H0:'zero differences'},
 30:{'Expected 5 packs':'battery field'},31:{'Expected 5 packs':'expected five'},32:{H1:'header shows one of'},33:{H1:'three counted with one difference'},
 37:{'Expected 5 packs':'batteries'},38:{H2:'zero differences'},39:{H2:'one of three counted'},
 44:{'Matches':'Matches','Expected 24 boxes':'glove','Expected 6 cylinders':'oxygen'},
 46:{'Expected 24 boxes':'twenty four','Expected 6 cylinders':'six'},47:{'Matches':'Matches'},
 49:{'Expected 5 packs':'five','Expected 24 boxes':'twenty four','Expected 6 cylinders':'six',H3:'header shows three'},50:{H3:'of three counted with zero differences'},
 51:{'Save progress':'Save progress'},52:{H3:'In progress'},59:{'Inventory':'Inventory'},60:{'Recent counts':'Recent counts'},
 61:{'In progress':'In progress','Completed':'Completed'},62:{'2026-10-28 22:42':'timestamp','2026-10-28 22:36':'timestamp'},63:{'In progress':'In progress'},
 65:{H3:'In progress, three of three'},66:{H3:'zero differences'},
 67:{'Expected 5 packs':'five batteries','Expected 24 boxes':'twenty four'},68:{'Expected 6 cylinders':'six oxygen cylinders'},72:{'Complete':'Complete'},73:{'Complete':'Complete'},
 74:{'Complete count?':'Complete count'},75:{'Everything matches what was expected.':'everything matches what was expected'},76:{'Cancel':'Cancel','Complete':'Complete'},79:{'Complete':'Complete'},
 82:{HC:'Completed','Count completed.':'Count completed'},84:{'Recent counts':'Inventory history','Completed':'Completed'},
 85:{'Academy training batteries':'five','Nitrile gloves':'twenty four','Training oxygen cylinder':'six'},86:{HC:'completed result'},
}
METHOD=('Read the complete frozen789word narration and every actual90cue caption against the parent-proposed25hold sequence and the genuine reviewed native source label/identity packages. '
 'Cuts use only actual unchanged SRT starts, including the older Completed history atcue20 before returning to the SAME new count atcue21. '
 'Cue30battery field andcue37batteries bind the real Expected5packs row with the actual visible minus/plus glyphs; no invented native AX control names or narrative-only omission is used. '
 'Cue59return to Inventory binds its actual printed Inventory context while the real back-arrow glyph remains visible. '
 'Source017/018/020were independently viewed through tool-fit previews by this agent; other original source observations retain their genuine owner/parent attribution. '
 'No100percent-original manual inspection is newly asserted. Native source review is not encoded-frame, caption-readability or playback approval. Parent must read this proposed plan before rendering.')

def need(ok,message):
 if not ok:raise ValueError(message)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return unique_json(Path(p).read_text())

def prepare():
 for rel,want in PINS.items():need(sha(S/rel)==want,'Held input changed: '+str(rel))
 lesson=read(S/BASE/(NAME+'.narrated-source.json'));freeze=read(S/BASE/'source-freeze.json')
 for file,digest in freeze['freeze_files'].items():need(sha(S/BASE/file)==digest,'Immutable freeze file changed: '+file)
 rows=read(S/CAPS)['screenshots'];qa=read(S/'expansion/audio'/(NAME+'.actual.qa.json'));heard=read(S/'expansion/audio'/(NAME+'.listening-review.json'))
 cues=load_cues(S/'expansion/audio'/(NAME+'.srt'));raw=load_cues(S/'expansion/audio'/(NAME+'-generated-20261028.raw.srt'))
 need(len(lesson['scenes'])==12 and len(rows)==14 and len(cues)==len(raw)==90 and len(PICTURES)==25,'Held scene/source/cue inventory changed.')
 need(words(' '.join(s['narration'] for s in lesson['scenes']))==words(' '.join(c['text'] for c in cues)),'Frozen narration differs from actual caption words.')
 need(all((a['start'],a['end'])==(b['start'],b['end']) for a,b in zip(cues,raw)),'Actual raw cue boundaries changed.')
 need(qa['passed'] is True and qa['issues']==[] and not qa.get('possible_speech_gaps'),'Full actual narration QA must pass.')
 need(qa['lesson']['sha256']==SOURCE and qa['lesson']['words']==789 and qa['audio']['sha256']==AUDIO and qa['audio']['full_decode']=='passed','Actual source/audio QA binding differs.')
 need(qa['audio']['decoded_samples']==15023125 and qa['audio']['sample_rate']==48000 and qa['audio']['duration_seconds']==312.9817708333333,'Decoded sample/duration inventory changed.')
 need(qa['signal_threshold_rms']>=.001 and qa['silent_raw_cues']==qa['silent_corrected_cues']==0 and qa['corrected_captions']['exact_script'] is True,'Speech-energy/exact-script gate missing.')
 for key,expected in [('raw_captions',RAW),('corrected_captions',SRT)]:
  q=qa[key];need(q['sha256']==expected and q['cues']==len(q['energy'])==90,'Every measured actual cue is required.')
  for number,(energy,cue) in enumerate(zip(q['energy'],cues),1):
   need(energy['cue']==number and abs(energy['start']-cue['start'])<1e-8 and abs(energy['end']-cue['end'])<1e-8 and energy['samples']>0 and energy['rms']>=qa['signal_threshold_rms'] and energy['below_threshold'] is False,'Invalid cue energy: '+str(number))
 need(heard['reviewer']=='User' and heard['complete_natural_narration'] is True and heard['audio_sha256']==AUDIO and heard['lesson_sha256']==SOURCE and heard['reviewed_at']=='2026-10-29T04:12:19Z','Exact real full User listening review required.')
 by_id={r['id']:r for r in rows};numbers={int(r['id'].split('-')[3]):r['id'] for r in rows};native={}
 for row in rows:native[row['id']]=validate_native_source(row,S,'Unit')
 assignments={}
 for first,last,num in PICTURES:
  for cue in range(first,last+1):need(cue not in assignments,'Duplicate cue.');assignments[cue]=numbers[num]
 need(set(assignments)==set(range(1,91)),'Every actual cue requires exactly one real source.')
 now=datetime.now(timezone.utc).isoformat();scenes=[];intervals=[]
 for ix,(authored,(first,last)) in enumerate(zip(lesson['scenes'],RANGES)):
  need(words(authored['narration'])==words(' '.join(c['text'] for c in cues[first-1:last])),'Actual scene words cross boundary: '+authored['id'])
  start=0 if ix==0 else cues[first-1]['start'];end=qa['audio']['duration_seconds'] if ix==11 else cues[RANGES[ix+1][0]-1]['start']
  screens=[];expanded=[];selected=assignments[first];screen_start=start
  for number in range(first,last+1):
   ident=assignments[number]
   if ident!=selected:screens.append({'screenshot_id':selected,'start':screen_start,'end':cues[number-1]['start']});selected=ident;screen_start=cues[number-1]['start']
   refs=REFERENCES.get(number,{})
   need(set(refs)<=set(by_id[ident]['visible_labels']),'Unseen literal cue'+str(number))
   entry=dict(cues[number-1],cue=number,screenshot_id=ident,required_labels=list(refs),spoken_references=refs,instructional=bool(refs))
   v=_Validator(S);v.spoken_references(entry,{_normalized(k) for k in refs},'cue'+str(number),True);need(not v.issues,'; '.join(v.issues));expanded.append(entry)
  screens.append({'screenshot_id':selected,'start':screen_start,'end':end});intervals+=screens
  visible={label for screen in screens for label in by_id[screen['screenshot_id']]['visible_labels']}
  need(set(authored['required_labels'])<=visible,'Scene literal coverage missing: '+authored['id'])
  need(all(screen['end']-screen['start']>=2 for screen in screens),'Unreadable flash cut.')
  built={'id':authored['id'],'title':authored['title'],'kind':'operational','start':start,'end':end,'screens':screens,'captions':expanded,'visual_required_labels':authored['required_labels']}
  review={'passed':True,'reviewer':'Codex actual90cue/reviewed-native-source correspondence reviewer','reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(built,by_id),'method':METHOD}
  scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,'captions':[{k:c[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for c in expanded],'instruction_review':review})
 need(len(intervals)==25,'Expected exact25parent-proposed holds.')
 reviews={}
 for row in rows:
  package=read(S/row['native_review_package']['file']);r=package['review']
  reviews[row['id']]={'reviewer':r['reviewer'],'reviewed_at':r['reviewed_at'],'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True,'method':r['method'],'evidence':'Genuine named native-source review package SHA256 '+row['native_review_package']['sha256']+'. No new source pixel approval is inferred from rendering.'}
 plan={'schema_version':1,'lesson_id':NAME,'duration_seconds':qa['audio']['duration_seconds'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional quantities · iOS simulator',
  'narration':{'file':'expansion/audio/'+NAME+'.m4a','sha256':AUDIO,'kind':'approved_natural_narration','approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':AUDIO,'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':'expansion/audio/'+NAME+'.actual.qa.json','qa_sha256':QA}},
  'captions':{'file':'expansion/audio/'+NAME+'.srt','sha256':SRT,'kind':'speech_timed_srt','approval':{'reviewer':'Codex exact789word/90actualcue correspondence','reviewed_at':now,'sha256':SRT,'audio_sha256':AUDIO,'speech_timing_reviewed':True,'method':'Every original genuine Descript SRT boundary retained. No caption split, finer anchor or estimated cut was used. Every measured cue passed full decoded audio QA.'}},
  'capture_manifests':[{'file':str(CAPS),'sha256':MANIFEST}],'screenshot_reviews':reviews,'scenes':scenes,
  'parent_plan_review_pending':True,'render_authorized':False,'publishable':False,
  'limitations':lesson['scope_limits']+['This is the proposed source/caption plan only. Root review precedes any render. Encoded native frame/caption readability and actual beginning/middle/end playback remain unreviewed.']}
 report={'kind':'proposed_native90cue25hold_correspondence','source_only':True,'rendered':False,'publication_approved':False,'lesson_sha256':SOURCE,'audio_sha256':AUDIO,'captions_sha256':SRT,'qa_sha256':QA,'listening_sha256':LISTEN,'capture_manifest_sha256':MANIFEST,'scenes':scenes,'holds':intervals,'actual_cues':cues,'native_source_bindings':{k:v['native_binding'] for k,v in native.items()},'glyph_context_method':METHOD,'minimum_actual_hold_seconds':min(x['end']-x['start'] for x in intervals)}
 return plan,report

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write-proposed',action='store_true');parser.add_argument('--ffmpeg',type=Path);args=parser.parse_args();plan,report=prepare()
 if args.write_proposed:
  need(not OUT.exists(),'Preserve all existing proposed plans; use a new output version.');need(args.ffmpeg is not None,'Repeat complete real decode before proposed plan write.')
  with tempfile.TemporaryDirectory(prefix='native-count-real-decode-') as temp:
   pcm=Path(temp)/'actual.wav';duration=audio_duration(str(args.ffmpeg),S/'expansion/audio'/(NAME+'.m4a'),pcm)
   with wave.open(str(pcm),'rb') as f:need(f.getframerate()==48000 and f.getnchannels()==1 and f.getsampwidth()==2 and f.getnframes()==15023125,'Repeated real decoded sample inventory differs.')
   need(abs(duration-plan['duration_seconds'])<1/48000,'Repeated duration differs.')
  OUT.mkdir(parents=True)
  for name,value in [('plan.proposed.json',plan),('correspondence.proposed.json',report)]:
   (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
  checked=validate_inputs(S/BASE/(NAME+'.narrated-source.json'),OUT/'plan.proposed.json',S)
  need(len(checked['cues'])==90 and sum(len(s['screens']) for s in checked['scenes'])==25,'Strict renderer preflight lost actual sources/cues.')
 print(json.dumps({'proposed_only':True,'rendered':False,'publishable':False,'scenes':12,'actual_cues':90,'sources':14,'holds':25,'minimum_hold_seconds':report['minimum_actual_hold_seconds'],'written':args.write_proposed,'strict_renderer_preflight_passed':args.write_proposed,'pins':{name:sha(OUT/name) for name in ['plan.proposed.json','correspondence.proposed.json']} if args.write_proposed else {}},indent=2))
if __name__=='__main__':main()
