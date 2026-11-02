#!/usr/bin/env python3
"""Persist this reviewer's completed image observations; no playback/publication approval.

Run only for the pinned take after personally inspecting all 25 original-size
encoded PNGs and the 18 numbered cue contact sheets (71 actual cue frames).
The observations below are authored image review, not inferred pixel authentication.
"""
import copy, datetime, hashlib, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
from expansion_site import lesson_content_digest
from verify_capture_evidence import verify_document
NAME = 'app-dispatch-pending-call-to-dispatch'
O = S / 'expansion/rendered' / (NAME + '-take-01')
FROZEN = S / 'expansion/plans' / (NAME + '-capture-freeze-20261028-v2') / (NAME + '.narrated-source.json')
LEARNER = S / 'expansion/plans' / (NAME + '-take-01.learner-source.json')
PINS = {
 str(LEARNER.relative_to(S)): '1820061dff647dc17ea139766a4d18d342af38e12b36479e8932d1c97dc3d180',
 str(FROZEN.relative_to(S)): '53fb3845732f12d57d9367a496b0b3fa7ba638c04c2b7515d6f0801add24f837',
 str((O / (NAME + '.mp4')).relative_to(S)): '7140a9a9c96fd8cef68ad27342df91018b2de11b1e260163473aa76dc9aea641',
 'expansion/plans/' + NAME + '-take-01.checked.plan.json': 'a21a4361a24226e0a23489ad90a560dd6b6e328d901baa90ed2dc6fc68de8817',
 'expansion/audio/' + NAME + '.listening-review.json': '3b1848eeae43c865b1959a71323ffd9c7e6aadcf736ce8392a88c361dc996b7c',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def output(name, value):
 p=O/name
 if p.exists(): raise SystemExit('Refusing to overwrite review history: '+str(p.relative_to(S)))
 p.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
 return str(p.relative_to(S)),sha(p)
# Literal foreground application labels personally read in the encoded full-size PNGs.
LABELS = {
 '001':['Resgrid Dispatch','Active Calls','Pending','Scheduled','Engine 51','Christopher Herrmann','Available','1/1'],
 '002':['Menu','Calls','Calls List','Pending Calls','New Call','Close Menu'],
 '003':['New Call','Call Details','Name *','TRAINING ONLY - Academy pending dispatch 20261028','Nature *','Software-only pending-call exercise in the fictional local department. No operational response.','Priority *','Routine','Type *','Investigation','Call Location','Destination POI','No destination'],
 '004':['New Call','Save as pending (do not dispatch yet)','The call is saved and numbered, but nobody is notified and the field apps do not see it. Recipients you pick are kept as the proposed dispatch; dispatch it later from Pending Calls.','Dispatch To','Select Recipients'],
 '005':['Select Dispatch Recipients','Wallace Boden','Everyone','Users (1)','1 selected','Cancel','Confirm'],
 '006':['New Call','Save as pending (do not dispatch yet)','Dispatch To','1 selected','Cancel','Save Pending Call'],
 '007':['Resgrid Dispatch','Search pending calls...','Call #','Name','Type','Priority','Address','Received','Actions','Investigation','Routine','Dispatch','Cancel Call'],
 '008':['Call Details','#FD51-2026-0007','TRAINING ONLY - Academy pending dispatch 20261028','Pending — not yet dispatched','Dispatch','Info','Dispatched','Routine','Investigation'],
 '009':['Call Details','#FD51-2026-0007','TRAINING ONLY - Academy pending dispatch 20261028','Pending — not yet dispatched','Dispatched','Wallace Boden','Group: Command','Type: User'],
 '010':['Select Dispatch Recipients','Wallace Boden','Everyone','Users (1)','1 selected','Cancel','Confirm'],
 '011':['Select Dispatch Recipients','Wallace Boden','Everyone','Users (1)','0 selected','Cancel','Confirm'],
 '012':['Select Dispatch Recipients','Wallace Boden','Everyone','Users (1)','1 selected','Cancel','Confirm'],
 '013':['Resgrid Dispatch','Search pending calls...','No pending calls','There are no calls waiting to be dispatched.'],
 '015':['Call Details','#FD51-2026-0007','TRAINING ONLY - Academy pending dispatch 20261028','Close Call','Dispatched','Dispatch additional resources','Wallace Boden','Group: Command','Type: User'],
 '016':['Call Details','#FD51-2026-0007','TRAINING ONLY - Academy pending dispatch 20261028','Close Call','Dispatched','Wallace Boden'],
 '017':['Close Call','Close Type','Closed','Close Note','TRAINING ONLY - Academy pending dispatch exercise complete; no operational response. Closed without notifying call recipients.','Notify everyone on the call','Cancel'],
 '023':['Resgrid Dispatch','Active Calls','Pending','Scheduled','Search calls...','#DEMO-0003','TRAINING — Vehicle rescue exercise','#DEMO-0002','TRAINING — Community medical standby','Engine 51','Christopher Herrmann','Available','1/1'],
 '024':['Resgrid Dispatch','Active Calls','Pending','Scheduled','Academy pending dispatch 20261028','No active calls','Engine 51','Christopher Herrmann','Available','1/1'],
 '025':['Resgrid Dispatch','Active Calls','Pending','Scheduled','Warehouse','#DEMO-0001','TRAINING — Warehouse alarm','Engine 51','Christopher Herrmann','Available','1/1'],
 '020':['Call Details','#FD51-2026-0007','TRAINING ONLY - Academy pending dispatch 20261028','Routine','Info','Dispatched','Investigation'],
}
OBSERVATIONS = [
 'Baseline console shows 3 Active Calls, 0 Pending, 0 Scheduled, Engine 51 Available and Herrmann 1/1; real Chicago map remains visible.',
 'Expanded Calls menu exposes the named New Call action and Pending Calls entry.',
 'Exact exercise Name and Nature are readable; Routine and Investigation selected, location fields blank and destination No destination. Partially clipped Create New Call heading is not relied on.',
 'Pending switch is on and its complete saved/proposed dispatch explanation is readable. Save Pending Call is below this viewport and is not credited here.',
 'Select Recipients and pending switch remain visible while the first part of the genuine 57-second split cue is spoken.',
 'Foreground recipient picker shows Wallace Boden checked, Everyone unchecked and 1 selected; search and Confirm are readable.',
 'Full form footer shows 1 selected, pending switch on, and complete Save Pending Call button; no member name is claimed on this view.',
 'Exact title and description return before Save; all related fields remain readable for this 2.52-second hold.',
 'Full Save Pending Call control returns at the genuine 77-second spoken choosing boundary.',
 'Pending queue shows one numbered row with Routine, Investigation, Dispatch and Cancel Call. Narrow name/number cells are honestly truncated.',
 'Call Details reveals full FD51-2026-0007 identity and Pending — not yet dispatched banner.',
 'Dispatched tab shows proposed Wallace Boden, Command group/User type while pending banner remains visible.',
 'Pending queue Dispatch control corresponds to the instruction to return and choose Dispatch.',
 'Foreground dispatch picker retains one checked Boden proposed member and unchecked Everyone.',
 'Boden unchecked, 0 selected, Confirm disabled matches the explicit empty-selection explanation.',
 'Boden rechecked, 1 selected, Everyone unchecked and full Confirm visible for final release instruction.',
 'Settled queue says No pending calls; this is a true empty state, not loading.',
 'Same call identity remains and Dispatched lists Boden, Command/User; pending banner is absent and Dispatch additional resources is visible.',
 'Exercise identity and Close Call entry are readable before the close sheet.',
 'Foreground Close Call sheet has Closed type, full exercise Close Note, Notify everyone on the call switched off, Cancel and final Close Call. No dimmed background control is credited.',
 'Final unfiltered console shows department total 3 Active Calls, 0 Pending and 0 Scheduled, preserving Engine/Herrmann state.',
 'Exercise-name search gives local panel No active calls while department top counter remains 3.',
 'Warehouse search finds original #DEMO-0001 TRAINING — Warehouse alarm, top department count remains 3.',
 'Retained exercise Call Details identity is readable with no Close Call action present; no literal label is invented for its absence.',
 'Search cleared, original console restored while six-sector companion and browser/provider limitations finish; readable final hold through actual audio end.',
]
METHOD = ('Personally inspected all 25 complete actual encoded 1920x1080 interval PNGs individually using view_image, '
 'then all 71 actual encoded cue-midpoint JPEGs in 18 numbered four-frame contact sheets. '
 'Checked foreground literal labels, active caption text, screen continuity and relevant controls against the 20 retained source JPEG/DOM observations. '
 'All source images were personally reviewed during capture/curation; this pass re-opened critical original 003/004/005/006/007/011/012/017 before encoded review. '
 'No clipped or dimmed background control satisfies an instructional requirement. Separate numerical comparisons checked all 25 source rectangles and 71 caption compositions. '
 'No source image, narration, speech timing, master video or application state changed. This agent performed no browser playback or subjective audio listening; '
 'the actual complete user listening approval is separately pinned. These authored observations do not cryptographically authenticate pixels or prove provider/device operation.')
def main():
 for rel,want in PINS.items():
  if sha(S/rel)!=want: raise SystemExit('Input hash changed: '+rel)
 d=read(O/'evidence.pending.json'); src={x['id']:x for x in d['screenshots']}
 nr=read(O/'frame-source-comparison.json'); cr=read(O/'cue-frame-check.json')
 assert nr['passed'] and nr['intervals_checked']==25 and cr['passed'] and cr['cues_checked']==71
 assert len(d['rendered_segments'])==25 and len(d['screenshots'])==20 and not d['browser_playback']
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 rows=[]
 for i,seg in enumerate(d['rendered_segments'],1):
  f=seg['frame']; source=src[seg['screenshot_id']]; labels=LABELS[seg['screenshot_id'][:3]]
  assert set(labels)<=set(source['visible_labels'])
  assert sha(S/f['file'])==f['sha256'] and sha(S/source['file'])==source['sha256']
  f.update(review_status='visually_reviewed',application_visible=True,visible_labels=labels,reviewed_control_names=[])
  f['visual_review']={'reviewer':'Codex','reviewed_at':now,'sha256':f['sha256'],'video_sha256':d['video']['sha256'],
   'source_screenshot_sha256':source['sha256'],'caption_text_verified':True,'controls_legible':True,
   'complete_application_image_visible':True,'no_runtime_error_or_loading_overlay':True,'no_private_values_visible':True,
   'method':METHOD,'observations':OBSERVATIONS[i-1], 'application_mean_absolute_pixel_error_0_255':nr['frames'][i-1]['application_mean_absolute_pixel_error_0_255']}
  rows.append({'interval':i,'scene_id':seg['scene_id'],'screenshot_id':seg['screenshot_id'],'file':f['file'],
   'sha256':f['sha256'],'source_sha256':source['sha256'],'video_sha256':d['video']['sha256'],'visible_labels':labels,
   'caption_text':f['caption_text'],'observations':OBSERVATIONS[i-1]})
 d['authoring_sha256']=lesson_content_digest(read(LEARNER))
 d['review_summary']={'reviewer':'Codex','reviewed_at':now,'video_sha256':d['video']['sha256'],
  'authoring_sha256':d['authoring_sha256'],'source_images_reviewed':20,'rendered_intervals_reviewed':25,
  'actual_encoded_cue_frames_reviewed':71,'individually_inspected_full_size_intervals':list(range(1,26)),
  'method':METHOD,'source_narration_caption_hashes_unchanged':True,'browser_playback_approved':False,'publication_ready':False,
  'numerical_checks':{'interval_report':str((O/'frame-source-comparison.json').relative_to(S)),
   'interval_report_sha256':sha(O/'frame-source-comparison.json'),'cue_report':str((O/'cue-frame-check.json').relative_to(S)),
   'cue_report_sha256':sha(O/'cue-frame-check.json'),'maximum_application_mae_0_255':nr['maximum_application_mean_absolute_pixel_error_0_255'],
   'maximum_full_frame_mae_0_255':cr['maximum_full_frame_mean_absolute_error_0_255'],
   'maximum_caption_foreground_mae_0_255':cr['maximum_caption_foreground_mean_absolute_error_0_255']},
  'limitations':['Three genuine advancing beginning/middle/end native browser playback proofs and parent independent review are not supplied by this image review.',
   'Application state and recorded recipient are demonstrated; notification delivery, operational response and native device behavior are not demonstrated.',
   'Historical call FD51-2026-0007 is this exercise only; manual replay must read fresh identity and never force or close unrelated calls.']}
 audit={'schema_version':1,'lesson_id':NAME,**d['review_summary'],'pins':PINS,'intervals':rows,
  'cue_frames':[dict(x,visually_reviewed_by='Codex',reviewed_at=now,caption_and_corresponding_screen_checked=True) for x in cr['frames']],
  'contact_sheets':[{'file':str(p.relative_to(S)),'sha256':sha(p),'reviewed_by':'Codex'} for p in sorted((O/'review/cue-contact-sheets').glob('*.jpg'))]}
 for name,value in [('visual-review.json',audit),('evidence.reviewed.json',d)]: print(*output(name,value))
 report=verify_document(d,S)
 print(*output('reviewed.preplayback-gate.json',report));print(json.dumps(report,indent=2))
if __name__=='__main__': main()
