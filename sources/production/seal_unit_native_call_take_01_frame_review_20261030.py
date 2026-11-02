"""Bind genuine encoded native Unit frame observations; never infer browser approval.

Read-only by default; --write-review stores NEW frame-reviewed evidence/audit.
Existing pending evidence, media, sources, native profiles and old reviews remain.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources'
NAME='app-unit-call-lifecycle-native';T=Path('expansion/rendered')/(NAME+'-take-01')
OBS=Path('expansion/audits/app-unit-call-lifecycle-native-take-01-actual-frame-observations-20261030.json')
PINS={'expansion/rendered/app-unit-call-lifecycle-native-take-01/app-unit-call-lifecycle-native.mp4': 'd4fcf9c6d7a974b71757d1510508d4666beaef180b16b0bf642cebe3a93c9b78', 'expansion/rendered/app-unit-call-lifecycle-native-take-01/assembly.json': '591469c18a060d72f77a67df1616486f2ce42cf9c59005b5d130efc26ffd00d1', 'expansion/rendered/app-unit-call-lifecycle-native-take-01/evidence.pending.json': '31a03c4ea62a6c3239c62ab8feab1a457b81efe7772cca14cd04860e8d3975a6', 'expansion/rendered/app-unit-call-lifecycle-native-take-01/frame-source-comparison.json': 'e0337b3f6a87c04302bc9bfa743f4cff9bb0a00388ddaae9cd6c84ef1140ce3a', 'expansion/rendered/app-unit-call-lifecycle-native-take-01/cue-frame-check.json': '930a4cd5c68fa30cb33122127858a56388fd9ad51001e4a66803b64ca3d18ac9', 'expansion/rendered/app-unit-call-lifecycle-native-take-01/encoded-audio.qa.json': 'ef816dc2387d065b50faf886aac038a2a0030a029694cddb36c70eddaed1c848', 'expansion/audits/app-unit-call-lifecycle-native-take-01-actual-frame-observations-20261030.json': '494c4dc5fdc9aeceb188d7eb3b2d6123894ac36b57e9219bb91cfac92d9447e7', 'expansion/plans/app-unit-call-lifecycle-native-take-01-final-inputs-20261030/plan.json': '26c931bcba9dfa9ebfdfb9765969079b5fcc3275516eb63ec0459c33f92ca4c4', 'expansion/audio/app-unit-call-lifecycle-native.listening-review.json': '3bcd147443de70481cdb6ef9853476c6b563f2d2476316b6b47e13b20483f6a1'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def encoded(d):return (json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
def require(ok,message):
 if not ok:raise ValueError(message)
def prepare():
 require(__debug__,'Use ordinary Python; retained guards must remain enabled.')
 for p,d in PINS.items():require(sha(S/p)==d,'Changed exact native frame-review input: '+p)
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import verify_document,_image_dimensions
 from native_capture_public import digest
 from expansion_site import lesson_content_digest
 evidence=deepcopy(read(S/T/'evidence.pending.json'));obs=read(S/OBS)
 require(obs['video_sha256']==evidence['video']['sha256'],'Actual image observations identify a different master.')
 require(obs['actual_full_frames_personally_inspected']==23 and obs['caption_cues_personally_reviewed']==88 and obs['caption_strips_personally_reviewed']==list(range(1,16)),'Require complete actual personal frame/caption observations.')
 require(set(obs['full_frame_observations'])=={str(i) for i in range(1,24)},'Require all23 actual native holds.')
 at=datetime.fromisoformat(obs['recorded_at']);assembled=datetime.fromisoformat(evidence['video']['assembled_at'])
 require(assembled<=at<=datetime.now(timezone.utc),'Actual encoded review must follow assembly.')
 require(obs['browser_playback_performed_by_this_agent'] is False and not evidence['browser_playback'],'Do not infer or overwrite later genuine playback.')
 for name,count,key in [('frame-source-comparison.json',23,'intervals_checked'),('cue-frame-check.json',88,'cues_checked')]:
  d=read(S/T/name);require(d['passed'] and d[key]==count and d['video_sha256']==evidence['video']['sha256'],'Actual source/caption numerical check failed.')
 audio=read(S/T/'encoded-audio.qa.json')
 require(audio['passed'] and audio['audio']['sha256']==evidence['video']['sha256'] and audio['audio']['full_decode']=='passed' and audio['silent_raw_cues']==audio['silent_corrected_cues']==0 and not audio['issues'] and not audio['possible_speech_gaps'],'Actual full encoded audio QA failed.')
 require(audio['alignment']['match_ratio']==1 and audio['alignment']['text_changes']==[],'Encoded narration/caption mismatch.')
 checks={k:True for k in ['application_visible','raw_full_viewport_visible','controls_legible','caption_text_verified','no_blocking_error','no_private_values_visible']}
 shots={r['id']:r for r in evidence['screenshots']};rows=[]
 for i,segment in enumerate(evidence['rendered_segments'],1):
  f=segment['frame'];o=obs['full_frame_observations'][str(i)];source=shots[segment['screenshot_id']]
  require(o['frame_file']==f['file'] and o['frame_sha256']==f['sha256']==sha(S/f['file']),'Changed actual viewed native frame.')
  require(o['source_id']==segment['screenshot_id'] and o['source_sha256']==source['sha256'],'Changed actual source observation.')
  require(_image_dimensions(S/f['file'])==(1920,1080),'Wrong actual encoded frame geometry.')
  require(o['labels'] and set(o['labels'])<=set(source['visible_labels']),'Unseen label introduced into frame evidence.')
  f.update(review_status='actual_frame_reviewed',application_visible=True,visible_labels=o['labels'],reviewed_control_names=[])
  binding=digest({'frame_sha256':f['sha256'],'video_sha256':evidence['video']['sha256'],'source_binding_sha256':digest(f['native_binding']),'visible_labels':f['visible_labels'],'caption_text':f['caption_text']})
  f['native_frame_review']={'reviewer':obs['reviewer'],'reviewed_at':obs['recorded_at'],'method':obs['method'],'binding_sha256':binding,'checks':checks.copy(),'findings':o['notes']}
  rows.append({'hold':i,'scene_id':segment['scene_id'],'source_id':segment['screenshot_id'],'source_sha256':source['sha256'],'frame':f['file'],'frame_sha256':f['sha256'],'native_frame_review_binding_sha256':binding,'observed_labels':o['labels'],'findings':o['notes']})
 source=read(S/'expansion/plans/app-unit-call-lifecycle-native-candidate-20261030/lesson.candidate.json')
 evidence['authoring_sha256']=lesson_content_digest(source)
 evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':True,'source_observation_file':str(OBS),'source_observation_sha256':PINS[str(OBS)],'actual_full_frames_personally_reviewed':23,'actual_caption_regions_personally_reviewed':88,'actual_User_full_listening_receipt_sha256':'3bcd147443de70481cdb6ef9853476c6b563f2d2476316b6b47e13b20483f6a1','no_browser_or_Root_review_inferred':True,'canonical_site_target_or_Git_changed':False}
 report=verify_document(evidence,S)
 pending=['browser_playback: must be a nonempty array']+[f'browser_playback: supply exactly one {p} browser playback proof (found 0)' for p in ['beginning','middle','end']]
 require(report['issues']==pending,'Unexpected strict native evidence issues: '+json.dumps(report))
 audit={'kind':'Actual native Unit call full-frame and caption review, genuine browser playback pending','lesson_id':NAME,'video_sha256':evidence['video']['sha256'],'reviewer':obs['reviewer'],'reviewed_at':obs['recorded_at'],'input_pins':PINS,'frame_holds_personally_reviewed':23,'caption_regions_personally_reviewed':88,'caption_sheets':obs['caption_sheet_files'],'frames':rows,'strict_remaining_issues':report['issues'],'native_source_profiles_preserved':True,'actual_User_listening_receipt_sha256':'3bcd147443de70481cdb6ef9853476c6b563f2d2476316b6b47e13b20483f6a1','canonical_site_target_or_Git_changed':False}
 return evidence,audit

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-review',action='store_true');a=p.parse_args();evidence,audit=prepare()
 targets=[S/T/'evidence.frames-reviewed.pending-playback.json',S/T/'native-frame-review.json']
 if a.write_review:
  require(all(not p.exists() and not p.is_symlink() for p in targets),'New-only frame review preserves existing history.')
  for path,d in zip(targets,[evidence,audit]):
   with path.open('xb') as f:f.write(encoded(d))
 print(json.dumps({'native_frame_gate_passed_except_genuine_browser_playback':True,'review_written':a.write_review,'holds':23,'captions':88,'video_sha256':evidence['video']['sha256'],'browser_playback_pending':True,'canonical_site_target_or_Git_changed':False}))
if __name__=='__main__':main()
