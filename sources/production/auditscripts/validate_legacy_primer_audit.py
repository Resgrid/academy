"""Validate legacy audit hashes, narration/cues and actual unchanged public-source secret rules.

This is an audit-source check, not audio listening, rendering, browser playback or
publication qualification. An optional local-only credentials JSON and inherited
Mapbox values are checked in memory and never emitted. See README.md.
"""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,os,re
import argparse,importlib.util
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--source-root',type=Path,help='Optional current source-checkout parent for checking every source hash.')
parser.add_argument('--private-values-json',type=Path,help='Optional local-only credentials JSON; values are never printed or copied.')
args=parser.parse_args()
R=args.root.resolve();S=R/'sources';P=S/'expansion/plans';A=S/'expansion/audits'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
course=json.loads((S/'course.json').read_text());audit=json.loads((A/'legacy-primer-replacement-audit.json').read_text());inv=json.loads((P/'legacy-capture-inventory.json').read_text());reg=inv['captures'];errors=[];warnings=[]
assert audit['source_course_sha256']==sha(S/'course.json')
assert len(course['lessons'])==audit['counts']['lessons']
plans=sorted(P.glob('legacy-*-replacement.json'));actions=[];cues=0;scenes=0
for p,lesson in zip(plans,course['lessons']):
 d=json.loads(p.read_text());assert d['lesson']==lesson['id'];assert not d['illustrated_input_compliant'];assert d['readiness']['publishable'] is False;assert not d['readiness']['strict_source_gate_passed'];assert not d['readiness']['speech_timing_authoritative']
 scene_narrations=[x['narration'] for x in d['scenes']];assert scene_narrations==[x['narration'] for x in lesson['scenes']]
 script='\n\n'.join(scene_narrations)
 assert hashlib.sha256(script.encode()).hexdigest()==d['narration']['text_sha256']
 words=re.findall(r"[\w]+(?:['’][\w]+)*",re.sub(r'<[^>]+>','',script).casefold().replace('’',"'"))
 assert hashlib.sha256(' '.join(words).encode()).hexdigest()==d['narration']['normalised_words_sha256']
 cue_ids={c['id'] for c in d['existing_actual_cues']}
 for c in d['existing_actual_cues']:
  assert c['start']>=0 and c['end']>c['start'];assert hashlib.sha256(c['text'].encode()).hexdigest()==c['text_sha256']
 for scene in d['scenes']:
  assert hashlib.sha256(scene['narration'].encode()).hexdigest()==scene['narration_sha256']
  for a in scene['spoken_requirements']:
   actions.append(a['id']);assert set(a['existing_cue_ids'])<=cue_ids
   assert hashlib.sha256(a['text'].encode()).hexdigest()==a['text_sha256']
   assert all(k in reg for k in a['candidate_capture_refs'])
  assert scene['precise_prior_capture_gaps']
  for t in scene['screen_targets']:assert all(k in reg and not reg[k]['excluded_by_owner'] for k in t['candidate_capture_refs'])
 for m in d['media'].values():
  if isinstance(m,dict) and m.get('file') and m.get('sha256'):assert sha(R/m['file'])==m['sha256']
 cues+=len(d['existing_actual_cues']);scenes+=len(d['scenes'])
assert len(actions)==len(set(actions))==audit['counts']['spoken_requirements'] and scenes==audit['counts']['scenes'] and cues==audit['counts']['actual_cues']
for k,row in reg.items():
 assert sha(R/row['image_file'])==row['image_sha256']
 assert row['app'] in ['Core','Responder','Dispatch','IC'];assert row['replacement_usable_without_new_review'] is False
 if row['recorded_hash_matches'] is False: warnings.append({'capture':k,'issue':'Owner-recorded screenshot hash differs; cannot become replacement evidence without resolution.'})
priority=json.loads((P/'legacy-07-mapping-priority.json').read_text());assert len(priority['actual_cue_screen_gap_map'])==72;assert len(priority['missing_shot_groups'])==12;assert priority['publishable'] is False
for c in priority['actual_cue_screen_gap_map']:
 assert all(k in reg for k in c['candidate_capture_refs'])
for row in priority['existing_capture_candidates']:assert sha(R/row['image_file'])==row['image_sha256']
tool_files=[p for p in Path(__file__).parent.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md']]
files=sorted(list(P.glob('legacy-*.json'))+list(A.glob('legacy-*.json'))+list(A.glob('legacy-*.md'))+tool_files+[A/'learning-log.md'])
files=[p for p in files if p.name!='legacy-audit-validation.json']
# Use the actual public-source scanner unchanged, with known local values as additional input.
secret_values=[]
creds=args.private_values_json or S/'demo/private/credentials.json'
if creds.is_file():
 def walk(value):
  if isinstance(value,dict):
   for item in value.values():walk(item)
  elif isinstance(value,list):
   for item in value:walk(item)
  elif isinstance(value,str) and len(value)>7:secret_values.append(value.encode())
 walk(json.loads(creds.read_text()))
# SMTP fixture credentials are separately retained only in the ignored private scenario.
smtp_path=S/'demo/private/scenarios/core-workflow-smtp.json'
if smtp_path.is_file():
 def collect_smtp(value):
  if isinstance(value,dict):
   for key,item in value.items():
    if key=='SmtpPassword' and isinstance(item,str) and len(item)>=8:secret_values.append(item.encode())
    elif isinstance(item,(dict,list)):collect_smtp(item)
  elif isinstance(value,list):
   for item in value:collect_smtp(item)
 collect_smtp(json.loads(smtp_path.read_text()))
for name,value in os.environ.items():
 if 'MAPBOX' in name and value.startswith(('pk.','sk.')):secret_values.append(value.encode())
secret_values=sorted(set(secret_values))
scanner_path=R/'scripts/audit_public_repo.py'
spec=importlib.util.spec_from_file_location('academy_public_scanner',scanner_path)
scanner=importlib.util.module_from_spec(spec);spec.loader.exec_module(scanner)
# Scan the report itself too, when present, while excluding its hash from its own manifest.
scan_paths=sorted(set(files+[A/'legacy-audit-validation.json']))
scan_paths=[p for p in scan_paths if p.is_file()]
for p in scan_paths:
 text=p.read_text()
 if re.search(r'/(?:Users|home)/[^/\s]+/',text):errors.append({'file':str(p.relative_to(R)),'issue':'Nonportable absolute user path'})
 with p.open('rb') as stream:
  for rule in scanner.scan_stream(stream,secret_values):errors.append({'file':str(p.relative_to(R)),'rule':rule})
sourcepins=json.loads((P/'legacy-source-file-pins.json').read_text())['files']
missing_sources=[x['path'] for x in sourcepins if not x['exists']]
if args.source_root:
 for pin in sourcepins:
  path=args.source_root/pin['path']
  if not path.is_file() or sha(path)!=pin['sha256']:errors.append({'file':pin['path'],'issue':'Source bytes changed since audit'})
report={'validated_at':datetime.now(timezone.utc).isoformat(),'scope':'Source-only legacy replacement audit consistency and asset hashes; no media render/playback/completion claim','passed':not errors,'counts':{'lessons':len(plans),'unchanged_source_scenes':scenes,'spoken_requirements':len(actions),'retained_actual_cues':cues,'capture_records':len(reg),'distinct_image_sha256':len({x['image_sha256'] for x in reg.values()}),'source_file_pins':len(sourcepins),'source_files_missing':len(missing_sources),'source_citation_recommended_narration_corrections':audit['counts']['source_narration_correction_scenes'],'location_missing_groups':12,'location_unchanged_actual_cues':72,'hash_pinned_audit_files':len(files),'replacement_masters':0,'publishable_replacements':0},'narration_checksum':{'field':'normalised_words_sha256','definition':'SHA256 of lowercase normalized narration words; same checksum values verified against unchanged source narration','plans_verified':len(plans)+1},'retained_reproduction':{'generator':'sources/production/auditscripts/legacy_primer_audit.py','validator':'sources/production/auditscripts/validate_legacy_primer_audit.py','inputs':'sources/production/auditscripts/legacy-audit-inputs.json','documentation':'sources/production/auditscripts/README.md'},'secret_scan':{'scanner':'scripts/audit_public_repo.py','scanner_sha256':sha(scanner_path),'method':'actual scan_stream, unchanged patterns and assignment rules','files_scanned':len(scan_paths),'known_private_values_checked':len(secret_values),'finding_count':sum('rule' in x for x in errors),'values_printed':False},'errors':errors,'warnings':warnings,'source_files_missing':missing_sources,'files':[{'file':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files],'excluded_from_modification':['Frozen Responder01/03 scene/narration/capture refs','Existing course/audio/media/captions','Newsite/catalog','Raw screenshots/source capture manifests','Original repositories'],'limited_authorized_existing_file_edit':'learning-log.md: only legacy timing paragraph corrected to current measured214.97s/72 cues versus old218.84s/73 cues','not_done':['Browser access while explicitly blocked','Replacement render','Audio signal/listening/timing qualification','Rendered-frame review','Browser playback proof','Import','MFA/security changes','Git actions']}
(A/'legacy-audit-validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'passed':report['passed'],'counts':report['counts'],'errors':errors,'warning_count':len(warnings),'missing_source_count':len(missing_sources)}))
if errors:raise SystemExit(1)
