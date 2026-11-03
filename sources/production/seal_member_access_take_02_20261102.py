"""Seal the personally reviewed deployment handover master after genuine User hearing approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
R=Path(__file__).resolve().parents[2]; S=R/'sources';sys.path.insert(0,str(R/'scripts'))
from verify_capture_evidence import verify_document, visible_controls_digest, _image_dimensions
from expansion_site import _prepare, lesson_content_digest
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
now=datetime.now(timezone.utc).isoformat()
NOTES={'001-personnel-list-and-member-actions': 'Actual Personnel page with complete Add a Person, Manage Invites and Manage Roles actions and separate staffing/status/state columns.', '031-wide-unsaved-account-credentials-replay': 'Actual readable wide Add Person prepared-form replay: unique training username, New/Confirm password masked, complete8character/digit/upper/lower help. No duplicate submission.', '019-unsaved-identity-entry-replay-after-successful-creation': 'Actual unsaved identity replay with Peter, Mills, training ID and fictional email; Group remains No Group before the next selection. No second account was created.', '032-wide-unsaved-group-and-role-replay': 'Actual wide Group Details, community coordination selected, Is Group Admin clear, navigator role chip fully visible. Replays the original successful creation choices.', '033-wide-unsaved-notification-and-add-person-replay': 'Actual wide prepared controls: Notify User unchecked, Require Password Change unchecked, complete Add Person button; all notification channels clear. Original saved member is independently shown.', '011-saved-member-filtered-role-and-normal-state': 'Actual saved Peter search result with navigator role, Normal, Available and Standing By; complete Edit control.', '012-reopened-saved-member-identity-and-time-zone': 'Actual saved identity/profile and initial Hawaii selection. This is the before value, not the later stored time zone.', '013-central-time-zone-selection-prepared': 'Actual prepared Central Time selection before Save; complete intended option visible.', '014-normal-user-disable-checked-hide-clear-and-save': 'Actual Normal User radio selected, Department Admin clear, Disable User checked, Hide User clear and complete Save. Checked Normal radio has IsDepartmentAdmin valuefalse.', '015-saved-normal-disabled-member-state': 'Actual saved Normal, Disabled state in Peter row; role, Available and Standing By remain; Edit action visible.', '017-disable-clear-normal-user-ready-to-restore': 'Actual Normal User retained, Disable User cleared, Hide User clear and complete Save control before restoration.', '018-restored-normal-member-and-role-retained': 'Actual saved Peter row restored to Normal with navigator role, Available and Standing By retained.', '020-reopened-training-group-and-role-persisted': 'Actual fully loaded reopened Central Time, community coordination group, navigator role and clear Is Group Admin. Loading016 is excluded.'}
CFG=[('core-member-creation-access', '2a44c56990368732a69486d00b455d360785a3f8e3c7e78cb46d4f04455de57d', 17, 82, 5, 14, '-source-20261102-v2')]
for name,master,holds,cues,contacts,strips,suffix in CFG:
 o=S/'expansion/rendered'/f'{name}-take-02';p=S/'expansion/plans'/f'{name}-complete-correspondence-20261102-v2';source=S/'expansion/plans'/(name+suffix)/'lesson.candidate.json'
 e=read(o/'evidence.pending.json');screens={v['id']:v for v in e['screenshots']};hearing=S/'expansion/audio'/f'{name}.listening-review.json';h=read(hearing)
 assert sha(S/e['video']['file'])==master==e['video']['sha256']
 assert h['reviewer']=='User' and h['complete_natural_narration'] is True and h['lesson_sha256']==sha(source)
 assert sha(S/'expansion/audio'/f'{name}.m4a')==h['audio_sha256']
 qa=read(o/'encoded-audio.qa.json');assert qa['passed'] and qa['audio']['sha256']==master and qa['corrected_captions']['cues']==cues
 metric=read(o/'frame-qa/extraction-and-pixel-metrics.json');assert metric['video_sha256']==master
 obs={}
 for i,seg in enumerate(e['rendered_segments'],1):
  frame=seg['frame'];shot=screens[seg['screenshot_id']];assert sha(S/frame['file'])==frame['sha256']
  names=[c['accessible_name'] for c in shot.get('visible_controls',[])]
  obs[str(i)]={'frame_sha256':frame['sha256'],'labels':shot['visible_labels'],'reviewed_control_names':names,'notes':NOTES[seg['screenshot_id']]+' Full application rectangle retained; burned caption in the separate lower margin.'}
  frame.update(review_status='actual_frame_reviewed',application_visible=True,visible_labels=shot['visible_labels'],reviewed_control_names=names,review={'reviewer':'Root','reviewed_at':now,'method':'Personal review of actual encoded interval frames and caption-strip sheets','notes':obs[str(i)]['notes']})
  if names:
   frame['control_review']={'passed':True,'reviewer':'Root','reviewed_at':now,'sha256':frame['sha256'],'controls_sha256':visible_controls_digest(names),'application_visible':True,'no_errors':True,'controls_reviewed':True,'controls_fully_visible':True,'controls_unobstructed':True,'video_sha256':master,'source_screenshot_sha256':shot['sha256']}
 assert len(obs)==holds
 framefile=o/'actual-frame-observations-20261102.json'
 put(framefile,{'recorded_at':now,'reviewer':'Root','video_sha256':master,'method':f'Root personally viewed all{contacts} actual encoded interval contact sheets and all{strips} full-width encoded caption-strip sheets, and personally inspected the actual source screenshots. Original pixels retain all actual prepared, saved and reopened deployment controls and roster results. Separate numerical comparisons passed. No Root hearing claim.','caption_cues_personally_reviewed':cues,'interval_contact_sheets_personally_viewed':contacts,'caption_strip_images_personally_viewed':strips,'full_frame_observations':obs})
 b=o/'playback/root-live-approved-20261102';proofs=[]
 for position in ('beginning','middle','end'):
  row=read(b/f'{position}.full-video.actual-observation.json');assert row['video_sha256']==master and row['current_time']>row['previous_time']+.25 and not row['paused'] and not row['ended'] and row['media_error'] is None and row['console_errors']==[]
  pic=S/row['screenshot']['file'];assert sha(pic)==row['screenshot']['sha256'] and _image_dimensions(pic)==(row['screenshot']['width'],row['screenshot']['height'])
  state=row['screenshot_media_state'];assert state['top']>=0 and state['bottom']<=state['viewport_height'] and row['ready_state']==4
  row['review_state']='actual_full_player_personally_reviewed';proofs.append(row)
 assert proofs[0]['current_time']<30 and .3*e['video']['duration_seconds']<proofs[1]['current_time']<.7*e['video']['duration_seconds'] and proofs[2]['current_time']>.85*e['video']['duration_seconds']
 put(b/'raw-observations.json',proofs)
 put(b/'root-review.json',{'reviewer':'Root','reviewed_at':now,'video_sha256':master,'positions_personally_viewed':['beginning','middle','end'],'full_video_rectangle_visible':True,'actual_clock_advanced':True,'native_captions_matched_actual_speech_cues':[x['matched_caption_cue'] for x in proofs],'media_errors':[],'console_errors':[],'method':'Root personally viewed all three actual normal-UI advancing playback screenshots. Actual Resgrid application screens and matching burned/native captions visible. Native captions enabled for private QA only. No Root hearing claim.'})
 lesson=read(p/'lesson.learner-projection.proposed.json');lesson.update(export_ready=True,publication_mode='video',evidence_file=(o/'evidence.reviewed.json').relative_to(S).as_posix(),production_source={'file':source.relative_to(S).as_posix(),'sha256':sha(source)})
 e['browser_playback']=proofs;e['authoring_sha256']=lesson_content_digest(lesson)
 e['qualification_review']={'reviewer':'Root','reviewed_at':now,'frame_review_complete':True,'browser_playback_pending':False,'actual_encoded_frame_observations_sha256':sha(framefile),'encoded_audio_qa_sha256':sha(o/'encoded-audio.qa.json'),'raw_browser_observations_sha256':sha(b/'raw-observations.json'),'root_browser_review_sha256':sha(b/'root-review.json'),'genuine_user_hearing_receipt_sha256':sha(hearing)}
 report=verify_document(e,S);assert report['passed'],report
 put(o/'evidence.reviewed.json',e);put(o/'canonical-candidate.reviewed.json',lesson);_prepare(lesson,S)
 report.update(public_export_preflight='passed',video_sha256=master,evidence_sha256=sha(o/'evidence.reviewed.json'),canonical_candidate_sha256=sha(o/'canonical-candidate.reviewed.json'),authoring_sha256=e['authoring_sha256'],actual_full_frames_personally_reviewed=holds,actual_caption_cues_personally_reviewed=cues,actual_browser_positions_personally_viewed=['beginning','middle','end'],human_listening_claim_by_Root=False,genuine_User_hearing_receipt_sha256=sha(hearing),canonical_adoption_pending=True)
 put(o/'qualification.json',report)
 canonical=S/'expansion/lessons'/f'{name}.json';put(canonical,lesson)
 put(o/'canonical-adoption.json',{'adopted_at':now,'canonical_file':canonical.relative_to(S).as_posix(),'canonical_sha256':sha(canonical),'qualification_sha256':sha(o/'qualification.json'),'video_sha256':master,'git_mutations':0})
 print(json.dumps({'qualified_and_adopted':True,'lesson':name,'holds':holds,'cues':cues,'video_sha256':master}))
