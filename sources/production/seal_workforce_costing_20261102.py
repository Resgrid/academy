"""Seal the personally reviewed resource/call-costing master after genuine User hearing approval."""
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
NOTES={'012-resource-cost-profiles-empty': 'Actual resource-cost list and Add resource profile.', '037-saved-resource-subject-and-effective-period': 'Later saved-profile readback shows selected Unit subject, full training van, name, effective dates and currency.', '014-resource-depreciation-prepared': 'Actual acquisition10000, salvage1000, operating-hour basis, useful-life900 and utilization600.', '015-resource-fuel-consumption-times-unit-price': 'Actual fuel component with consumption2, price4 and component approval; separate profile checkbox remains off in this initial preparation.', '038-resource-approval-and-components-reopened': 'Later actual reopened profile and component both show approval, unchanged2×4inputs and fully visible Save.', '016-resource-profile-saved-depreciation-ten': 'Saved profile index reads depreciation10,one component and Yes.', '020-call-hours-approved-prepared-upper': 'Actual worker,date,two Regular hours and establishment form.', '021-call-hours-source-approval-save': 'Actual call51001,fictional source,Approved and complete Save control.', '022-call-hours-saved-row': 'Saved two-hour approved call-specific work-entry row.', '039-call-number-calculation-control-replayed': 'Later clean calculator-location replay includes current final76index row; this is not evidence of a new historical run.', '024-cost-run-fifty-four-summary': 'Actual first retained personnel54,resources0,total54summary.', '025-cost-review-missing-inputs-and-usage': 'Actual first-run review summary and Resource usage control.', '028-resource-unit-phase-source-prepared': 'Actual community-van usage form with incident phase,manual source and exercise date.', '029-resource-operating-hours-approval-save': 'Actual two operating hours,blank unrelated meters/fuel fields,Approved and complete Save.', '030-resource-reading-saved-two-hours': 'Saved reading confirms2operating hours and matching fictional vehicle.', '031-cost-recalculated-personnel-fifty-four-resource-thirty-six': 'Actual second retained summary54personnel,36resources,total90; no offscreen cost-line flags are claimed.', '032-approved-payroll-cost-forty-prepared': 'Actual manual fictional payroll-cost40field,source,approval and Save; visible help explains estimate replacement.', '033-approved-payroll-cost-saved-forty': 'Actual saved work-entry row reads40with call context.', '034-approved-actual-forty-resource-thirty-six-total-seventy-six': 'Actual summary40personnel,36resources,total76.', '035-cost-summary-needs-review-after-actual': 'Actual76summary shows Missing inputs1and Frozen dash,with no freeze or cleared review claimed.', '036-latest-unfrozen-run-needs-review': 'Actual latest current cost-run index reads Needs review,total76; no multiple-row history or revenue claimed.'}
CFG=[('core-workforce-resource-call-costing', 'ccd7bcd84a23aa75163e2a6b7d4d72c874c58d3d3f164002a8be83147b5aa384', 27, 76, 7, 13, '-source-20261102')]
for name,master,holds,cues,contacts,strips,suffix in CFG:
 o=S/'expansion/rendered'/f'{name}-take-01';p=S/'expansion/plans'/f'{name}-complete-correspondence-20261102';source=S/'expansion/plans'/(name+suffix)/'lesson.candidate.json'
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
 put(framefile,{'recorded_at':now,'reviewer':'Root','video_sha256':master,'method':f'Root personally viewed all{contacts} actual encoded interval contact sheets and all{strips} full-width encoded caption-strip sheets, and personally inspected the actual source screenshots. Original pixels are retained, including explicitly identified later unsaved control replays. Separate numerical comparisons passed. No Root hearing claim.','caption_cues_personally_reviewed':cues,'interval_contact_sheets_personally_viewed':contacts,'caption_strip_images_personally_viewed':strips,'full_frame_observations':obs})
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
