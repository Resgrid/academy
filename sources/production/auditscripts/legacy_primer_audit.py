"""Reproduce the source-only legacy-primer replacement audit.

Uses only retained speech cues/screenshots and hash-bound review inputs. It never
opens a browser, edits narration/media, renders a master or approves publication.
Requires an existing FFmpeg executable (or imageio_ffmpeg) and the Academy's
stdlib screenshot-header helper. Source checkouts and the retained route/cue
assumptions are verified before generated reports are overwritten. See README.md.
"""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit
import collections,difflib,hashlib,json,re,subprocess,sys
import argparse,shutil
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--source-root',type=Path,required=True,help='Directory containing the Core,Responder,Dispatch,IC and other cited source checkouts.')
parser.add_argument('--ffmpeg',type=Path,help='Existing FFmpeg executable. No download is performed.')
args=parser.parse_args()
ROOT=args.root.resolve(); S=ROOT/'sources'; OUT=S/'expansion/audits'; PLAN=S/'expansion/plans'; DATA=Path(__file__).with_name('legacy-audit-inputs.json'); NOW=datetime.now(timezone.utc).isoformat()
if not (ROOT/'scripts/verify_capture_evidence.py').is_file():parser.error('--root must be the Academy repository')
if not (args.source_root/'Core').is_dir():parser.error('--source-root must contain the cited source checkouts')
sys.path.insert(0,str(ROOT/'scripts'))
from verify_capture_evidence import _image_dimensions
FFMPEG=str(args.ffmpeg) if args.ffmpeg else shutil.which('ffmpeg')
if not FFMPEG:
 try:
  import imageio_ffmpeg
  FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
 except ImportError:parser.error('Provide an existing --ffmpeg executable or install the already declared encoder runtime separately.')
inputs=json.loads(DATA.read_text())
# Guard manual source/word assumptions before any audit-output mutation.
for pin in inputs['priority_source_guard']:
 source=args.source_root/pin['path']
 if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=pin['sha256']:
  parser.error('Priority source changed; explicitly review and update legacy-audit-inputs.json before regenerating: '+pin['path'])
for pin in inputs['priority_timing_inputs']:
 source=ROOT/pin['file']
 if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=pin['sha256']:
  parser.error('Priority media/cues changed; explicitly remap the retained cue/shot audit before regenerating: '+pin['file'])

def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def texthash(t):return hashlib.sha256(t.encode()).hexdigest()
def rel(p):
 try:return str(p.relative_to(ROOT))
 except ValueError:return p.name

def tokens(text):return re.findall(r"[\w]+(?:['’][\w]+)*",re.sub(r'<[^>]+>','',text).casefold().replace('’',"'"))
def stamp(text):
 h,m,s=re.split('[:,.]',text)[:3],None,None
 parts=re.split('[:,.]',text);return int(parts[0])*3600+int(parts[1])*60+int(parts[2])+int(parts[3])/1000

def parse_srt(path):
 result=[]
 for block in re.split(r'\n\s*\n',path.read_text().strip()):
  lines=block.splitlines();idx=next((i for i,l in enumerate(lines) if '-->' in l),None)
  if idx is None:continue
  a,b=lines[idx].split(' --> ');text=' '.join(lines[idx+1:]);result.append({'id':int(lines[0]),'start':stamp(a.strip()),'end':stamp(b.strip()),'text':text,'text_sha256':texthash(text)})
 return result

def media_info(path):
 if not path.exists():return {'exists':False}
 result=subprocess.run([FFMPEG,'-hide_banner','-i',str(path)],capture_output=True,text=True)
 match=re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)',result.stderr)
 dur=int(match[1])*3600+int(match[2])*60+float(match[3]) if match else None
 return {'file':rel(path),'sha256':hashfile(path),'exists':True,'duration_seconds':dur,'bytes':path.stat().st_size}

def normapp(value):
 value=str(value or '').casefold().replace(' ','').replace('-','')
 return {'core':'Core','responder':'Responder','dispatch':'Dispatch','ic':'IC','incidentcommand':'IC','unit':'Unit'}.get(value)
def route(url):
 if not url:return None
 path=urlsplit(url).path.rstrip('/').casefold();return re.sub(r'/index$','',path)

def file_from_row(row, manifest):
 value=row.get('file') or row.get('path') or row.get('image')
 if not isinstance(value,str):return None
 p=Path(value)
 if p.is_absolute():return p
 for candidate in [S/p,ROOT/p,manifest.parent/p]:
  if candidate.exists():return candidate
 return S/p

def getrows(data):
 if isinstance(data,list):return data
 if isinstance(data,dict):return data.get('captures',data.get('screenshots',[]))
 return []
course_path=S/'course.json';course=json.loads(course_path.read_text());prior_path=DATA;observed_path=DATA;prior=inputs['source_routes'];observed=inputs['observed_routes'];old={(x['lesson_id'],x['scene_index']):x for x in prior['scenes']};obs={(x['lesson_id'],x['scene_index']):x for x in observed['scenes']}
expected={(lesson['id'],i) for lesson in course['lessons'] for i,_ in enumerate(lesson['scenes'])}
if set(old)!=expected:parser.error('Course scene structure changed; explicitly review the retained route/capture research before regeneration.')
for lesson in course['lessons']:
 for i,scene in enumerate(lesson['scenes']):
  if old[(lesson['id'],i)]['existing_narration']!=scene['narration']:parser.error('Narration changed; review source routes, real screenshots and speech timing before updating the retained inputs: '+lesson['id'])
priority_lesson=next((lesson for lesson in course['lessons'] if lesson['id']=='07-mapping'),None)
if not priority_lesson or texthash('\n\n'.join(x['narration'] for x in priority_lesson['scenes']))!=inputs['priority_narration_sha256']:
 parser.error('Priority narration changed; the manual cue/shot mapping needs explicit review.')
OUT.mkdir(parents=True,exist_ok=True);PLAN.mkdir(parents=True,exist_ok=True)

# Preserve the actual existing evidence as references; never modify a capture or its source manifest.
registry={};alias=collections.defaultdict(list);all_manifests=[]
for p in sorted((S/'captures').rglob('*manifest*.json')):
 try:data=json.loads(p.read_text())
 except (ValueError,OSError):continue
 all_manifests.append({'file':rel(p),'sha256':hashfile(p)})
 for index,row in enumerate(getrows(data)):
  if not isinstance(row,dict):continue
  app=normapp(row.get('app') or (data.get('app') if isinstance(data,dict) else None));url=row.get('url') or row.get('actual_url') or row.get('provenance',{}).get('url')
  if app is None and isinstance(url,str) and '/User/' in url:app='Core'
  if app not in {'Core','Responder','Dispatch','IC'}:continue
  image=file_from_row(row,p)
  if image is None or not image.exists() or image.suffix.lower() not in {'.jpg','.jpeg','.png'}:continue
  try:
   width,height=_image_dimensions(image)
  except (OSError,ValueError):continue
  digest=hashfile(image);original=row.get('sha256');capture_id=str(row.get('id') or image.stem);key=app+':'+capture_id+':'+digest[:12]
  labels=row.get('visible_labels',[]);labels=[labels] if isinstance(labels,str) else labels or []
  captured=row.get('captured_at') or row.get('provenance',{}).get('captured_at')
  excluded=row.get('eligible_for_lesson') is False or row.get('coverage_eligible') is False or any(row.get(x) is True for x in ['blocked','rejected','private'])
  review=row.get('capture_review') or {};review_text=str(row.get('visual_review',''))
  reviewed=review.get('passed') is True or ((row.get('coverage_eligible') is True or row.get('eligible_for_lesson') is True) and not re.search('pending|excluded|not.?reviewed|reject|error',review_text,re.I))
  facts={'capture_id':capture_id,'app':app,'image_file':rel(image),'image_sha256':digest,'recorded_image_sha256':original,'recorded_hash_matches':original==digest if original else None,'width':width,'height':height,'url':url,'captured_at':captured,'source_manifest':rel(p),'source_manifest_sha256':hashfile(p),'source_row_index':index,'excluded_by_owner':excluded,'owner_reviewed':reviewed,'owner_review':review_text,'viewport_label_observation':row.get('label_observation_method','not explicitly viewport-scoped; per-label image review required'),'literal_labels':[str(x) for x in labels],'visible_controls':row.get('visible_controls',[]),'capture_review':review,'provenance_complete':bool(url and captured),'kind':row.get('kind',row.get('evidence_kind','not supplied')),'replacement_usable_without_new_review':False}
  facts['integrity_ready']=not excluded and original==digest and bool(url and captured) and reviewed
  if key in registry:
   if facts['integrity_ready'] and not registry[key]['integrity_ready']:registry[key]=facts
  else:registry[key]=facts
  alias[capture_id].append(key)
# Reuse only historically inspected, hash-bound images; regeneration is not another visual review.
for row in registry.values():
 recorded=inputs['image_reviews'].get(row['capture_id'])
 if recorded and row['image_sha256']==recorded['image_sha256']:
  row['bounded_independent_review']=recorded['review']
index={'audited_at':NOW,'scope':'Existing actual Core/Responder/Dispatch/IC screenshot evidence only; no new browser capture','source_manifests':all_manifests,'captures':registry,'rules':['Source-review flags do not prove a specific saved operation, provider/native result or an entire narrated scene.','Candidates remain unusable for a replacement until each required control/state is visually matched and strict evidence validation passes.','Unit initial/legacy screenshots are outside this requested four-app substitution inventory.','No original image, capture manifest, frozen lesson or public catalog changed.']}
(PLAN/'legacy-capture-inventory.json').write_text(json.dumps(index,indent=2,ensure_ascii=False)+'\n')
# Exact current media/caption/script binding and every spoken sentence/action.
summary=[];global_actions=[];all_plans=[];verb=re.compile(r'\b(?:set|add|choose|select|confirm|review|check|open|create|save|send|invite|assign|upload|draw|enable|disable|allow|keep|record|compare|follow|verify|test|inspect|start|close|link|configure|complete|publish|export|import|approve|grant|revoke|protect|renew|recover|install|deploy|submit|transfer|issue|receive|connect|route|respond)\b',re.I)
for lesson in course['lessons']:
 id=lesson['id'];script='\n\n'.join(x['narration'] for x in lesson['scenes']);script_words=tokens(script);srt=S/'media'/(id+'.srt');vtt=S/'media'/(id+'.vtt');cues=parse_srt(srt) if srt.exists() else [];cue_words=[];word_cues=[]
 for cue in cues:
  tw=tokens(cue['text']);cue_words.extend(tw);word_cues.extend([cue['id']]*len(tw))
 matcher=difflib.SequenceMatcher(None,script_words,cue_words,autojunk=False);word_map={};diffs=[]
 for tag,a,b,c,d in matcher.get_opcodes():
  if tag=='equal':word_map.update({a+i:c+i for i in range(b-a)})
  else:diffs.append({'operation':tag,'script':' '.join(script_words[a:b]),'captions':' '.join(cue_words[c:d]),'script_token_range':[a,b],'caption_token_range':[c,d]})
 video=S/lesson['video'];audio=S/'production/descript/natural/audio'/(id+'.m4a');raw_srt=S/'production/descript/natural/captions'/(id+'-raw.srt');validation=S/'production/descript/natural'/(id+'-validation.json');validated=json.loads(validation.read_text()) if validation.exists() else {}
 vm=media_info(video);am=media_info(audio)
 stream_hash=None
 if video.exists():
  h=subprocess.run([FFMPEG,'-v','error','-i',str(video),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],capture_output=True,text=True)
  match=re.search(r'SHA256=([0-9a-f]{64})',h.stdout,re.I);stream_hash=match[1] if match else None
 media={'existing_illustrated_video':vm,'raw_natural_narration_audio':am,'existing_video_aac_packet_payload_sha256':stream_hash,'srt':{'file':rel(srt),'sha256':hashfile(srt) if srt.exists() else None,'cue_count':len(cues)},'vtt':{'file':rel(vtt),'sha256':hashfile(vtt) if vtt.exists() else None},'raw_speech_srt':{'file':rel(raw_srt),'sha256':hashfile(raw_srt) if raw_srt.exists() else None},'retained_natural_validation':{'file':rel(validation),'sha256':hashfile(validation) if validation.exists() else None,'reported_voice':validated.get('voice'),'reported_cues':validated.get('cues'),'reported_match_ratio':validated.get('match_ratio'),'reported_duration_seconds':validated.get('duration_seconds'),'reported_raw_audio_seconds':validated.get('source_audio_seconds'),'reported_transition_pause_seconds':validated.get('transition_pause_seconds'),'human_playback':validated.get('human_playback_review'),'human_listening':validated.get('human_listening_review')},'course_metadata_duration_seconds':lesson.get('duration_seconds'),'caption_last_end_seconds':cues[-1]['end'] if cues else None,'timing_rule':'The listed caption timestamps are retained observations, never invented timing. Enclosing cue bounds are not word timestamps. Do not pair final SRT with raw audio unless the actual retained pause assembly is reproduced and revalidated.','replacement_audio_recommendation':'Reuse/retain the actual AAC track from the hash-pinned current final video with matching SRT, or reproduce the documented raw-audio transition-pause assembly and fully QA it. No audio is synthesized here.'}
 scenes=[];cursor=0;cue_to_scenes=collections.defaultdict(set);cue_to_actions=collections.defaultdict(list)
 for i,scene in enumerate(lesson['scenes']):
  prior_scene=old[(id,i)];observed_scene=obs.get((id,i),{});assert prior_scene['existing_narration']==scene['narration']
  start_token=cursor;count=len(tokens(scene['narration']));end_token=start_token+count;cursor=end_token
  ids=sorted({word_cues[word_map[x]] for x in range(start_token,end_token) if x in word_map});
  for cueid in ids:cue_to_scenes[cueid].add(i)
  candidates={}
  for target in prior_scene.get('screen_targets',[]):
   target_route=route(target.get('route'));app=normapp(target.get('app'));matches=[]
   for key,row in registry.items():
    if not row['excluded_by_owner'] and (app is None or app==row['app']) and target_route and route(row['url'])==target_route:matches.append(key)
   candidates.setdefault((target.get('app'),target.get('route')),{'app':target.get('app'),'route':target.get('route'),'intent':target.get('capture_intent'),'candidate_capture_refs':matches[:18],'existing_capture_count':len(matches),'source_evidence':[{'path':str(x.get('path','')),'line':x.get('line'),'sha256':x.get('sha256')} for x in target.get('source_evidence',[])],'source_suggested_labels_unverified':target.get('required_labels',[]),'source_label_warning':'Prior source labels may include hidden-modal text, HTML entities or unrelated nearby controls; these are NOT validated caption requirements.'})
  priorrefs=[]
  for rid in observed_scene.get('actual_refs',[]):priorrefs.extend(alias.get(rid,[]))
  # Sentences are text requirements. Their only timings are enclosing actual retained cues.
  sentences=[x.strip() for x in re.split(r'(?<=[.!?])\s+',scene['narration']) if x.strip()];action_rows=[];sentence_cursor=start_token
  for n,sentence in enumerate(sentences):
   cnt=len(tokens(sentence));a=sentence_cursor;b=a+cnt;sentence_cursor=b;related=sorted({word_cues[word_map[x]] for x in range(a,b) if x in word_map});aid=f'{id}:s{i+1:02}:a{n+1:02}'
   requirement={'id':aid,'text':sentence,'text_sha256':texthash(sentence),'type':'instruction_or_action' if verb.search(sentence) else 'spoken_claim_or_context','existing_cue_ids':related,'exact_caption_token_alignment':all(x in word_map for x in range(a,b)),'enclosing_cue_start':min((x['start'] for x in cues if x['id'] in related),default=None),'enclosing_cue_end':max((x['end'] for x in cues if x['id'] in related),default=None),'candidate_capture_refs':list(dict.fromkeys(priorrefs+[ref for target in candidates.values() for ref in target['candidate_capture_refs']]))[:24],'coverage_status':'requires_action_specific_image_and_result_review','gap':'Existing same-route or prior baseline screenshots are candidates only; verify the exact spoken setting/control/value and any saved result. No complete operational demonstration is inferred.'}
   action_rows.append(requirement);global_actions.append({'lesson':id,'scene_index':i,**requirement})
   for cueid in related:cue_to_actions[cueid].append(aid)
  gaps=[]
  for target in observed_scene.get('screen_targets',[]):
   if target.get('next_capture_requirement'):gaps.append({'app':target.get('app'),'route':target.get('route'),'missing_operation_or_result':target['next_capture_requirement'],'prior_status':target.get('status'),'scope':'Recheck against current candidates; prior baseline is not a result claim.'})
  if not gaps:gaps=[{'missing_operation_or_result':'Visually verify exact operational controls/state and outcome across the entire existing narration. Intro/context may use genuine relevant app screen, never an illustration.'}]
  scenes.append({'index':i,'number':i+1,'title':scene['title'],'kind':scene['kind'],'narration':scene['narration'],'narration_sha256':texthash(scene['narration']),'course_timing_proposal_only':{'start':scene.get('start_seconds'),'duration':scene.get('duration_seconds')},'actual_existing_cue_ids':ids,'source_narration_matches_prior_plan':True,'screen_targets':list(candidates.values()),'prior_observed_capture_refs':list(dict.fromkeys(priorrefs)),'spoken_requirements':action_rows,'precise_prior_capture_gaps':gaps,'prior_narration_corrections':prior_scene.get('narration_review',{}),'prerequisites':prior_scene.get('prerequisites',[]),'needed_fictional_entities':prior_scene.get('needed_fictional_entities',[]),'unsupported_or_native_only_notes':prior_scene.get('unsupported_or_native_only_notes',[]),'strict_scene_coverage':'NOT demonstrated; source candidates require full action/label/result/timing review'})
 assert cursor==len(script_words),(id,cursor,len(script_words))
 for cue in cues:cue['source_scene_indices']=sorted(cue_to_scenes[cue['id']]);cue['spoken_requirement_ids']=cue_to_actions[cue['id']];cue['timing_provenance']='Existing sources/media SRT unchanged';cue['screen_assignment']='pending exact per-control/state review; no artificial within-cue cuts'
 result={'schema_version':1,'lesson':id,'title':lesson['title'],'audited_at':NOW,'status':'BLOCKED — not a renderer-ready replacement plan','source_course':{'file':rel(course_path),'sha256':hashfile(course_path)},'narration':{'text_sha256':texthash(script),'normalised_words_sha256':texthash(' '.join(script_words)),'word_count':len(script_words),'source_scene_count':len(scenes),'script_caption_exact_normalized':script_words==cue_words,'alignment_ratio':matcher.ratio(),'differences':diffs},'media':media,'illustrated_input_compliant':False,'scenes':scenes,'existing_actual_cues':cues,'capture_registry':'sources/expansion/plans/legacy-capture-inventory.json','readiness':{'all_real_screens_matched':False,'all_controls_and_saved_results_demonstrated':False,'every_cue_screen_assignment_verified':False,'speech_timing_authoritative':bool(cues),'audio_timeline_binding_complete':False,'strict_source_gate_passed':False,'rendered_frame_review':'not run','genuine_browser_playback':'pending, separate proof required','publishable':False},'render_decision':'No master is prepared because real-screen/action coverage is incomplete; preserve exact missing-shot list.','not_changed':['Source lesson/narration/audio/captions','Frozen R1/R3','New site/catalog','Source screenshots and capture manifests','Original Academy repository']}
 (PLAN/('legacy-'+id+'-replacement.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n');all_plans.append(result)
 summary.append({'lesson':id,'title':lesson['title'],'scenes':len(scenes),'spoken_requirements':sum(len(x['spoken_requirements']) for x in scenes),'actual_cues':len(cues),'normalized_script_matches_captions':script_words==cue_words,'alignment_ratio':matcher.ratio(),'final_video_duration_seconds':vm.get('duration_seconds'),'raw_narration_duration_seconds':am.get('duration_seconds'),'course_duration_seconds':lesson.get('duration_seconds'),'plan':'sources/expansion/plans/legacy-'+id+'-replacement.json','status':'incomplete real-screen coverage; no replacement master','fully_compliant_scenes':0,'publishable':False})
 print(id,len(scenes),len(cues),round(matcher.ratio(),5),flush=True)
audit={'audited_at':NOW,'scope':'All24 existing illustrated primers,295 exact narrated scenes, every spoken sentence/action and unchanged existing speech cues. Mapping primer prioritized separately.','source_course_sha256':hashfile(course_path),'prior_source_plan_sha256':hashfile(prior_path),'prior_observed_map_sha256':hashfile(observed_path),'capture_inventory':'sources/expansion/plans/legacy-capture-inventory.json','counts':{'lessons':len(summary),'scenes':sum(x['scenes'] for x in summary),'spoken_requirements':len(global_actions),'actual_cues':sum(x['actual_cues'] for x in summary),'capture_records':len(registry),'distinct_existing_capture_images':len({x['image_sha256'] for x in registry.values()}),'capture_records_by_app':dict(collections.Counter(x['app'] for x in registry.values())),'compliant_replacement_masters':0},'lessons':summary,'global_gates':['Every operational setting/action/result needs a genuine readable current screenshot and per-cue screen/caption mapping. Same-route menu/empty/list/settings views do not prove a saved operation or provider/native success.','Do not use prior bulk source label suggestions as verified viewport observations.','Every existing illustrated video remains noncompliant with the actual-screen requirement, even where audio/script quality is already validated.','Final caption timing belongs to the pause-adjusted media; raw narration and course JSON duration may differ. No fabricated word-time cuts.','Browser playback proof remains separate and pending until an actual replacement master exists and is genuinely tested.','Chrome is explicitly blocked; no browser access, new screenshots, MFA, import, source-feature/security change or Git action performed.']}
(OUT/'legacy-primer-replacement-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n');(OUT/'legacy-spoken-action-map.json').write_text(json.dumps({'audited_at':NOW,'source_course_sha256':hashfile(course_path),'requirements':global_actions},indent=2,ensure_ascii=False)+'\n')
print(json.dumps(audit['counts']))


# Refine the mechanically enumerated candidates into the bounded retained audit.
P=PLAN;A=OUT;DEV=args.source_root.resolve()
def sha(p):return hashfile(p)
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def portable(v):
 if isinstance(v,str):return v.replace(str(DEV)+'/', '')
 if isinstance(v,list):return [portable(x) for x in v]
 if isinstance(v,dict):return {k:portable(x) for k,x in v.items()}
 return v
inventory=json.loads((P/'legacy-capture-inventory.json').read_text()); registry=inventory['captures']
for row in registry.values():
 u=urlsplit(row['url'] or '');row['provenance_complete']=bool(u.scheme in ['http','https'] and u.netloc and row['captured_at'])
 row['replacement_usable_without_new_review']=False
 row['integrity_ready']=bool(not row['excluded_by_owner'] and row['recorded_hash_matches'] and row['provenance_complete'] and row['owner_reviewed'])
write(P/'legacy-capture-inventory.json',portable(inventory))
# Pin current source bytes separately from historical citations; a hash does not attest a rendered control.
source_files={};plans=[]
for p in sorted(P.glob('legacy-*-replacement.json')):
 d=json.loads(p.read_text())
 for scene in d['scenes']:
  for target in scene['screen_targets']:
   for e in target['source_evidence']:
    f=DEV/e['path'];current=sha(f) if f.is_file() else None
    e['historical_citation_sha256']=e.pop('sha256',None);e['current_file_sha256']=current
    e['historical_hash_matches_current']=current==e['historical_citation_sha256'] if e['historical_citation_sha256'] else None
    source_files[e['path']]={'path':e['path'],'sha256':current,'exists':f.is_file(),'role':'Source route/control research; actual viewport/result evidence remains separate.'}
 d['readiness']['speech_timing_authoritative']=False
 d['readiness']['retained_cue_timestamps_present']=bool(d['existing_actual_cues'])
 d['readiness']['cue_timing_qualification']='Existing SRT timestamps are retained unchanged; audio timing/signal/listening binding still requires current-media QA. Normalized text equality alone does not verify speech timing.'
 d['existing_capture_scope']={'apps_requested':['Core','Responder','Dispatch','IC'],'app_counts':dict(collections.Counter(x['app'] for x in registry.values())),'dispatch_limitation':'No Dispatch application screenshot with a retained capture-manifest row was found in sources/captures. Unmanifested dispatch-login.jpg is not promoted; Core Dispatch MVC pages remain Core screenshots.','unit_excluded':True}
 write(p,portable(d));plans.append(d)
extra=[
'Core/Web/Resgrid.Web/Areas/User/Views/WeatherAlerts/Zones.cshtml',
'Core/Web/Resgrid.Web/Areas/User/Views/WeatherAlerts/Settings.cshtml',
'Core/Core/Resgrid.Services/WeatherAlertService.cs',
'Core/Web/Resgrid.Web/Areas/User/Views/Mapping/StationRouting.cshtml',
'Core/Web/Resgrid.Web/Areas/User/Views/Routes/StartRoute.cshtml',
'Core/Web/Resgrid.Web/Areas/User/Views/Notes/NewNote.cshtml',
'Core/Web/Resgrid.Web/Areas/User/Views/CustomMaps/Layers.cshtml',
'Core/Web/Resgrid.Web/Areas/User/Views/IndoorMaps/Floors.cshtml'
]
for name in extra:
 f=DEV/name; source_files[name]={'path':name,'sha256':sha(f) if f.is_file() else None,'exists':f.is_file(),'role':'Priority location route/control source audit; not rendered operation proof.'}
write(P/'legacy-source-file-pins.json',{'audited_at':NOW,'files':list(source_files.values()),'note':'Current read-only source bytes; historical source citation hashes are retained separately in each lesson plan. No repository or feature edits.'})
mapplan=next(d for d in plans if d['lesson']=='07-mapping')
def refs(*ids):return [k for k,v in registry.items() if v['capture_id'] in ids]
def brief_ref(k):
 r=registry[k]
 return {x:r.get(x) for x in ['capture_id','app','image_file','image_sha256','width','height','url','captured_at','source_manifest','source_manifest_sha256','excluded_by_owner','bounded_independent_review']}
M=[]
def missing(id,title,cues,route,labels,existing,missing,limit,source):
 M.append({'id':id,'title':title,'actual_cue_ids':cues,'source_route':route,'source_control_candidates_unverified_unless_reviewed':labels,'existing_capture_refs':refs(*existing),'exact_missing_shots_or_correction':missing,'limits':limit,'source_files':source,'status':'partial_or_missing; no completed operational scene'})
missing('M01','Location age: saved personnel60 and reviewed unit setting',[8,15,29,35,41,47,53,58],'/User/Department/MappingSettings',['TTL In Minutes for Personnel Locations','TTL In Minutes for Unit Locations','Save'],['legacy-core-048-mapping-settings-personnel-stable','legacy-core-052-mapping-map-style-choices'],['Current existing view is0; capture the actual60 value only if a coordinated fictional-department setting change is authorized, saved and freshly reopened.','Capture the unit location-age setting fully, with its actual value; do not substitute the clipped bottom of048.','Show a real, explicitly simulated recent/stale record and resulting marker behavior if narration claims expiration.'],['The visible60 is explanatory help, not the saved input. Zero disables TTL in this actual screen.','Changing a shared department setting requires coordination and restoration; no setting is changed by this plan.'],['Core/Web/Resgrid.Web/Areas/User/Views/Department/MappingSettings.cshtml','Core/Web/Resgrid.Web/Areas/User/Controllers/DepartmentController.cs'])
missing('M02','Stations/hospitals POI create, persist and view',[7,18,19,20,60,71],'/User/Mapping/POIs -> AddPOIType -> ViewType?poiTypeId=<actual> -> AddPOI?poiTypeId=<actual> -> Mapping',['Add POI Type','Name','Is Destination','Latitude','Longitude','Address','Note'],['core-config-028-poi-empty-baseline','core-config-029-poi-type-options-readonly','core-config-030-poi-icon-preview-readonly','157-map-poi-list'],['Capture a saved fictional station POI and hospital POI through actual type/coordinate forms; retain actual IDs and saved values.','Capture readable placed POI pins and a detail popup/list; existing zero-POI/type forms do not demonstrate adding locations.'],['Use declared simulated coordinates, no current-device location permission or external dispatch.','Names/source controls above are source candidates; only visually reviewed current screenshot labels may enter renderer requirements.'],['Core/Web/Resgrid.Web/Areas/User/Views/Mapping/AddPOI.cshtml','Core/Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs'])
missing('M03','Weather wording correction and actual monitoring settings',[23,24,25,62,65],'/User/WeatherAlerts/Zones and /User/WeatherAlerts/Settings',['Zone Name','Zone Code','Center Location','Radius (miles)','Primary Zone','Active','Save Zone'],['legacy-core-058-weather-zones','158-weather-alerts-filters'],['Cue25 cannot be illustrated faithfully: it says draw zones/choose audience, but actual zone UI is center/radius and contains no drawing canvas or recipient picker.','Propose revised narration explaining center/radius plus severity/time schedule and department recipient policy; new speech/cues need actual generation and QA before replacement.','Capture current source/settings and saved training-only zone if authorized; capture actual saved severity/window state separately without enabling external notification providers.'],['Current Settings has severity schedules/exclusions/call-integration, not a group/user picker. WeatherAlertService.GetAllMembersForDepartmentAsync sends auto-messages to non-disabled/non-deleted members; recipient behavior is source-backed, not exercised.','An empty Responder severity list is not weather delivery or zone coverage proof. No actual provider alert is asserted.'],['Core/Web/Resgrid.Web/Areas/User/Views/WeatherAlerts/Zones.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/WeatherAlerts/Settings.cshtml','Core/Core/Resgrid.Services/WeatherAlertService.cs'])
missing('M04','Draw and save a layer, then apply it',[26,27,62,64,71],'/User/Mapping/NewLayer -> Layers -> Mapping',['Name','Is Visible By Default','Is Destination','Color','Layer Elements'],['legacy-core-011-mapping-new-layer','legacy-core-012-mapping-layer-editor','core-config-023-map-layer-chooser'],['Capture actual fictional geometry during supported drawing, Save, saved list/detail and the loaded layer on the map.','Review readability and alignment on the resulting map. Existing toolbar/Hydrants checkbox is not proof of a new layer.'],['Do not derive an icon name from its picture; any icon-only action needs actual DOM semantics and hash-bound image review.'],['Core/Web/Resgrid.Web/Areas/User/Views/Mapping/NewLayer.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/Mapping/Index.cshtml'])
missing('M05','Responder sharing preference versus native permission',[28,34,40,46,52,66],'/settings',['Realtime Geolocation','Background Geolocation','Keep Alive'],['057-settings-native-capability-controls'],['Existing actual Settings view can show the preference names and off states, not that members have permitted or transmitted location.','A native OS-permission/tracking demonstration is unavailable under current no-real-GPS constraint. Reword to explicit browser/native limits or arrange a separately authorized actual-device demonstration.'],['No browser geolocation permission, real location grant, background tracking or device hardware is exercised.','Do not relabel Keep Alive as a location permission.'],['Responder/src/app/(app)/settings.tsx'])
missing('M06','Directions and responding-resource route result',[32,33],'/User/Mapping/LiveRouting?callId=<actual> or StationRouting?stationId=<actual>&callId=<actual>',['Distance','Duration'],['197-map-call-pin-details'],['Capture the actual route page, readable geometry/distance/duration/instructions and actual known endpoints.','LiveRouting explicitly requests browser geolocation and therefore cannot be exercised under the no-GPS constraint. A supported station-to-call route uses stored coordinates, but must be described correctly and genuinely render.'],['Existing Responder Route button is only an available control; no external navigation handoff or route success occurred.','Core routing source uses configured OSRM and real response; never draw replacement route geometry or treat a blank/error page as a route.'],['Core/Web/Resgrid.Web/Areas/User/Views/Mapping/LiveRouting.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/Mapping/StationRouting.cshtml','Core/Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs'])
missing('M07','Custom image layer import and alignment',[38,39,64,67,68],'/User/CustomMaps/New -> Layers?id=<actual> -> RegionEditor?id=<actual> or Import?id=<actual>',['Map Type','Name','Description','Draw Bounds','Layer Image','Add Layer'],['core-config-031-custom-maps-empty-baseline','core-config-032-custom-map-bounds-readonly','legacy-core-055-custom-maps'],['Capture a saved fictional custom map, supported local image selection/upload, saved layer and real region/alignment editor.','Capture current/reference revision context and actual alignment; blank new-map bounds UI does not establish upload or alignment.'],['File chooser permission is separately blocked; no alternate upload transport or injected file state.','If file-URL access remains rejected, keep upload as a missing shot; never substitute an illustration for the application screen.'],['Core/Web/Resgrid.Web/Areas/User/Views/CustomMaps/New.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/CustomMaps/Layers.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/CustomMaps/RegionEditor.cshtml'])
missing('M08','Indoor floor plan and zone result',[44,45,67,68],'/User/IndoorMaps/Floors?id=<actual> -> ZoneEditor?id=<actual>',['Floor Name','Floor Plan Image','Add Floor','Zone Editor'],['core-config-032-custom-map-bounds-readonly'],['Capture actual building/floor selection, floor image, saved zone geometry and source/reference context through IndoorMaps.','The New Custom Map type Indoor screen is a separate UI and is not an IndoorMaps floor or zone result.'],['No actual indoor positioning or navigation is asserted. Uploaded floor plans are reference material. File chooser remains subject to the actual permission boundary.'],['Core/Web/Resgrid.Web/Areas/User/Views/IndoorMaps/Floors.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/IndoorMaps/ZoneEditor.cshtml'])
missing('M09','Planned route and actual unit assignment',[50,51,62],'/User/Routes/Edit?id=<actual> -> Directions?id=<actual> -> StartRoute?id=<actual>',['Unit','Assign Unit'],[],['Capture a saved fictional route, actual stops, Directions and actual assignment control/result if assignment is narrated.','Source exposes Unit assignment, including assign-at-start; avoid implying an arbitrary individual-person assignment control.'],['No route execution, physical patrol or arrival proof exists. Preserve shared Engine51/Herrmann seat and ongoing scenarios.'],['Core/Web/Resgrid.Web/Areas/User/Views/Routes/Edit.cshtml','Core/Web/Resgrid.Web/Areas/User/Views/Routes/StartRoute.cshtml'])
missing('M10','Readable location source/age and recent-vs-stale comparison',[3,4,9,10,14,64,70],'/User/Mapping and real resource location/detail/history UI',['Mapping','Show units','Show personnel'],['core-config-022-mapping-populated-current','196-map-incident-pins-local','197-map-call-pin-details'],['Capture readable resource identity plus actual server-provided position timestamp/source and a clearly simulated stale comparison.','Show expected expiration only after actual saved TTL and fixture age are verified; static call coordinates do not establish current personnel/unit position.'],['Current Core resource labels are crowded; Responder call pins are static incidents, not live GPS fixes.','No false physical arrival, real-device tracking or elapsed-time claim; use honest simulated-fixture provenance.'],['Core/Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs'])
missing('M11','Actual department mapping access',[16,17,21,22,30,31,36,37,42,43,48,49,54,55],'/User/Security/Index and actual department module/role controls',['Permissions'],['legacy-core-032-permissions'],['Capture the actual intended role/module/location-visibility state that gates the shown feature, without changing security or enrolling MFA.','Repeated generic availability lines have a retained source narration-correction proposal; they are not evidence that every mapping submodule shares one permission.'],['No security settings or grants are changed. A successful map view demonstrates that session view only.'],['Core/Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs'])
missing('M12','Record an actual mapping follow-up',[69,71,72],'/User/Notes/NewNote or an already supported equivalent note editor',['Title','Category','Body'],['legacy-core-046-notes','090-reference-notes-list','091-reference-note-rich-text'],['If keeping the practice instruction, capture a public-safe TRAINING mapping follow-up note including the observed issue, named fictional owner and review date in the actual Body, then reopen the saved note.','No existing capture proves this mapping follow-up. Do not invent dedicated owner/review-date fields in the map UI.'],['This is an explicitly fictional software-practice note, not evidence that actual map data is current.'],['Core/Web/Resgrid.Web/Areas/User/Views/Notes/NewNote.cshtml'])
cue_to_missing=collections.defaultdict(list)
for m in M:
 for c in m['actual_cue_ids']:cue_to_missing[c].append(m['id'])
context_refs=refs('core-config-022-mapping-populated-current','196-map-incident-pins-local')
cue_map=[]
multiscreen=[28,34,40,46,52,64,71]
for c in mapplan['existing_actual_cues']:
 mid=cue_to_missing[c['id']]; cand=list(dict.fromkeys([r for m in M if m['id'] in mid for r in m['existing_capture_refs']]))
 cue_map.append({**{k:c[k] for k in ['id','start','end','text','text_sha256']},'actual_cue_source_sha256':mapplan['media']['srt']['sha256'],'candidate_capture_refs':cand or context_refs,'missing_requirement_ids':mid,'status':'blocked/action-specific screen/result missing' if mid else 'genuine context-screen candidate; assembly QA still pending','within_cue_word_anchors_required':c['id'] in multiscreen,'timing_note':'Retained cue bounds only; no inferred word timestamps. Multiple separately located controls may need genuine speech anchors or corrected speech/captions.' if c['id'] in multiscreen else 'Existing unchanged cue bounds; no arbitrary timing proposed.'})
selected=list(dict.fromkeys(context_refs+[k for m in M for k in m['existing_capture_refs']]))
priority={'schema_version':1,'audited_at':NOW,'lesson':'07-mapping','title':mapplan['title'],'status':'BLOCKED; no replacement master, actual evidence/timing plan incomplete','source_course':mapplan['source_course'],'narration':mapplan['narration'],'media':mapplan['media'],'priority_findings':[{'finding':'TTL contradicts scenario','actual':'Personnel TTL0; visible help says0 disables expiration. Unit TTL0 in separate view.','narrated':'60-minute personnel expiration','decision':'Do not show0 as60 or count explanatory help as saved state.'},{'finding':'Current media differs from retained validation','current_video_duration_seconds':mapplan['media']['existing_illustrated_video']['duration_seconds'],'current_caption_cues':len(mapplan['existing_actual_cues']),'current_caption_last_end_seconds':mapplan['media']['caption_last_end_seconds'],'course_metadata_duration_seconds':mapplan['media']['course_metadata_duration_seconds'],'older_validation_duration_seconds':mapplan['media']['retained_natural_validation']['reported_duration_seconds'],'older_validation_cues':mapplan['media']['retained_natural_validation']['reported_cues'],'raw_audio_duration_seconds':mapplan['media']['raw_natural_narration_audio']['duration_seconds'],'older_validation_transition_pause_seconds':mapplan['media']['retained_natural_validation']['reported_transition_pause_seconds'],'older_validation_transition_count':12,'older_validation_formula_seconds':round(mapplan['media']['raw_natural_narration_audio']['duration_seconds']+12*mapplan['media']['retained_natural_validation']['reported_transition_pause_seconds'],3),'decision':'Older validation does not describe current hashes; exact historical discrepancy unverified. Re-QA actual final AAC/SRT or regenerate a documented assembly; never pair raw213.44 audio directly with final captions.'},{'finding':'Weather instructions do not match controls','actual':'Zone form uses center/radius; Settings has severity/time scheduling, not a recipient picker. Service sends auto-messages to eligible department members.','narrated':'Draw zones and choose who is alerted.','proposed_narration_only':'Configure each monitoring zone with its center location and radius. Review the display severity and delivery schedule in Weather Alert Settings, and confirm the department recipient policy.','decision':'Requires narration correction plus fresh real speech/cues before a faithful replacement; do not fabricate drawing/audience UI.'}],'source_pins':'sources/expansion/plans/legacy-source-file-pins.json','capture_registry':'sources/expansion/plans/legacy-capture-inventory.json','existing_capture_candidates':[brief_ref(k) for k in selected],'missing_shot_groups':M,'actual_cue_screen_gap_map':cue_map,'speech_alignment_limits':{'multi_screen_cue_ids_needing_genuine_speech_anchors_or_rewrite':multiscreen,'caption_timestamps_copied_unchanged':True,'word_timings_invented':False,'normalized_words_match_source':mapplan['narration']['script_caption_exact_normalized'],'current_audio_signal_listening_and_caption_alignment_QA':'not performed by this source-only audit'},'required_assembly_sequence':['Resolve source/UI narration mismatches without changing original audio blindly.','Capture and review missing real application controls, saved values and results after human browser clearance and within current action permissions.','Pin final approved narration/audio/SRT and real speech anchors; validate exact script, full decode, per-cue signal and listening.','Create an explicit actual cue-to-image plan using full legible screenshots and current strict source gate; no illustrated substitutes or UI inset.','Render1080p H264/AAC with SRT/VTT/chapters/poster, bind source/output hashes and inspect decoded frames across all spoken controls.','Collect separate genuine browser beginning/middle/end playback with captions, correct video hash/dimensions/ready state/no errors.','Only a complete gate result may be considered for publication; this audit never marks it publishable.'],'browser_playback_proof':'pending; no browser used while explicitly blocked','publishable':False}
write(P/'legacy-07-mapping-priority.json',portable(priority))
# Produce concise per-primer missing-route/action index and retain exact scene requirements in the plans.
audit=json.loads((A/'legacy-primer-replacement-audit.json').read_text());audit['counts'].update({'capture_records':len(registry),'distinct_existing_capture_images':len({r['image_sha256'] for r in registry.values()}),'capture_records_by_app':dict(collections.Counter(x['app'] for x in registry.values()))})
audit['priority_plan']='sources/expansion/plans/legacy-07-mapping-priority.json'; audit['source_file_pins']='sources/expansion/plans/legacy-source-file-pins.json';audit['source_audit_limits']='Route candidates and prior source recommendations are mechanically enumerated; exact pixel/control/action reviews are bounded to the explicitly reviewed location captures. No full295-scene visual audit or audio listening is asserted.'
for summary,d in zip(audit['lessons'],plans):
 assert summary['lesson']==d['lesson']
 targets=[t for s in d['scenes'] for t in s['screen_targets']]
 summary['source_narration_correction_scene_numbers']=[s['number'] for s in d['scenes'] if s['prior_narration_corrections'].get('correction_recommended')]
 summary['target_occurrences']=len(targets);summary['target_occurrences_with_same_route_candidates']=sum(bool(t['candidate_capture_refs']) for t in targets)
 summary['routes_without_current_candidate']=list(dict.fromkeys(t['route'] for t in targets if not t['candidate_capture_refs']))
 summary['precise_gap_source']='Every scene’s precise_prior_capture_gaps plus spoken_requirements and native/provider restrictions in its replacement plan; generic baseline statuses are not operational completion.'
audit['counts']['source_narration_correction_scenes']=sum(len(x['source_narration_correction_scene_numbers']) for x in audit['lessons'])
write(A/'legacy-primer-replacement-audit.json',portable(audit))
app_counts=collections.Counter(row['app'] for row in registry.values())
inventory_sentence=('Each `plans/legacy-<lesson>-replacement.json` pins narration,current media/audio/caption hashes,exact existing cue text/times,source files,route candidates,per-scene missing operations and prior narration corrections. `legacy-capture-inventory.json` records{records} screenshot entries ({unique} distinct image hashes): Core{core},Responder{responder},IC{ic}. No retained Dispatch app manifest row was found; unmanifested login art is not promoted. Core Dispatch MVC screens are Core evidence. Unit is intentionally outside this substitution search.'.format(records=len(registry),unique=len({row['image_sha256'] for row in registry.values()}),core=app_counts['Core'],responder=app_counts['Responder'],ic=app_counts['IC']))
lines=['# Legacy primer replacement audit','', 'All24 existing illustrated primers remain outside the actual-screen compliance requirement. This source-only pass retains295 unchanged narrated scenes,1,276 spoken sentence/action requirements and1,561 existing caption cues. None is a qualified replacement master. Browser access remains explicitly blocked; no captures, feature/security changes, speech generation or import occurred.','', inventory_sentence,'', 'Same-route screens and source labels are candidates, not proof that a spoken action or saved result occurred. Older DOM labels may include hidden options. Only explicit bounded image reviews in the location priority plan confirm individual observations; no complete295-scene visual review is claimed.','', '| Primer | Scenes / actual cues | Route-target occurrences with candidates | Narration-correction scenes |','|---|---:|---:|---|']
for x in audit['lessons']:lines.append(f"| {x['lesson']} — {x['title']} | {x['scenes']} / {x['actual_cues']} | {x['target_occurrences_with_same_route_candidates']} / {x['target_occurrences']} | {', '.join(map(str,x['source_narration_correction_scene_numbers'])) or 'None flagged by prior source audit'} |")
lines+=['','## Location07 is the first replacement priority','', 'The current `07-mapping.mp4` measures214.97s; its hash-pinned SRT has72 cues ending214.729s and matches the source’s normalized522 words. Course metadata says214.954s. The older natural validation instead describes218.84s,73 cues and213.44s raw audio plus twelve0.45s pauses. That older record is stale for the current files; the reason for the historical mismatch is unverified. Current final audio/SRT need actual QA. No invented pause/cue schedule or within-cue word time is supplied.','', 'The Personnel TTL input visibly reads0 and its help says0 disables expiration. The narrated60-minute example therefore lacks saved-state/expired-marker proof. Station/hospital POI additions, saved custom geometry, live/station routing result, custom-image upload/alignment, indoor floor/zone result, planned-unit route assignment, readable source/age comparison and recorded follow-up are still missing.','', 'The weather cue also requires a source wording correction: current Monitoring Zones uses Center Location/Radius, not drawing. Current Settings has severity/time schedules; no recipient picker is rendered. The service sends eligible auto-messages to non-disabled/non-deleted department members. Do not invent drawing/audience controls or infer provider delivery.','', 'See `plans/legacy-07-mapping-priority.json` for all72 unchanged cue ranges, exact image hashes, bounded observed values/labels and12 concrete missing-shot groups. Cues28/34/40/46/52/64/71 may need genuine finer speech anchors or revised speech to switch between separate full application screens; enclosing cue bounds are not word timing.','', '## Completion gates','', 'Resolve source/UI mismatches; collect missing actual shots and saved results within current permissions; bind final speech/SRT with genuine anchors and QA; create explicit cue/screen requirements; pass current source/render gates; inspect decoded frames; retain separate genuine caption-enabled browser playback at beginning/middle/end. Until then, no replacement or publication qualification is asserted.','']
(A/'legacy-primer-replacement-audit.md').write_text('\n'.join(lines))
print(json.dumps({'lessons':len(plans),'scenes':audit['counts']['scenes'],'requirements':audit['counts']['spoken_requirements'],'cues':audit['counts']['actual_cues'],'capture_records':len(registry),'unique_image_hashes':audit['counts']['distinct_existing_capture_images'],'source_files':len(source_files),'priority_missing_groups':len(M)}))
