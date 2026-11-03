"""Seal the personally reviewed route-plan and saved-stops master after genuine User hearing approval."""
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
NOTES={'001-routes-list-and-new-route-action': 'Actual initial empty Routes list with New Route action.', '003-prepared-route-name-unassigned-unit-and-draft-status': 'Actual prepared name, description, unassigned Unit and Draft state; same values repeated in the corrected successful run and independently reopened.', '004-routing-profile-radius-and-station-endpoints': 'Actual Driving profile, clear avoid choices, 100m base radius and Firehouse51 station endpoints; Add Stop is fully visible.', '013-corrected-run-first-stop-name-type-and-map-coordinates': 'Actual first Manual/Normal training-stop form with Chicago map selection and read-only41.854635/-87.698364coordinates.', '014-corrected-run-first-stop-details-and-add-action': 'Actual first-stop10minute dwell, blank inherited radius, fictional warehouse contact/number, pickup note and fully visible Add Stop.', '015-corrected-run-second-stop-name-and-coordinates': 'Actual second Manual training-stop name and own41.853879/-87.695618map selection.', '016-corrected-run-second-stop-details-and-add-action': 'Actual second-stop15minute dwell, explicit75m radius, fictional Community Centre contact/number, delivery note and fully visible Add Stop.', '017-corrected-run-two-stop-sequence-before-save': 'Actual two prepared client rows in pickup-before-delivery order before the whole route is saved.', '018-corrected-run-create-route-control': 'Actual Create Route control fully visible before its successful submission.', '019-saved-route-list-draft-two-stops-and-actions': 'Actual returned saved Draft plan, two stops, driving profile and View/Edit/Directions/History actions.', '020-saved-route-view-two-location-pins-and-draft-details': 'Actual returned Route Map with two named pins and Draft/driving/100m Details. Its side-summary number discrepancy is retained and is not treated as authoritative; the narration references named locations and the actual editor sequence.', '021-reopened-draft-route-name-unit-and-status': 'Actual reopened Edit form with stored name/description, unassigned Unit and Draft status. The preceding View screen exposes the Edit action.', '022-reopened-route-options-and-two-saved-stop-rows': 'Actual reopened station endpoints and two saved stop rows with their ordering arrows.', '023-saved-stop-order-community-point-first': 'Actual changed saved stop order with Community point B first.', '024-fresh-readback-retains-community-point-first': 'Actual fresh-page readback retaining B-first order, and Supply point A up-arrow for restoring pickup first.', '025-fresh-readback-pickup-before-delivery-restored': 'Actual fresh-page readback retaining restored A-first/B-second order.', '026-directions-warning-and-saved-stop-summary': 'Actual Directions warning and saved Stop Summary with10/15minute dwell, fictional contacts/numbers and pickup/delivery notes. This expected operational warning is explicitly taught; no road-route, travel estimate or provider success is asserted.', '027-calls-dashboard-routes-entry': 'Actual Calls page with the Routes navigation action fully visible.'}
CFG=[('core-route-plan-stops', '1d32d44ebd0757a93d8fdbb7f451cd003726ea1128369b6c63b57b2d9ea0780c', 22, 87, 6, 15, '-source-20261102')]
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
 put(framefile,{'recorded_at':now,'reviewer':'Root','video_sha256':master,'method':f'Root personally viewed all{contacts} actual encoded interval contact sheets and all{strips} full-width encoded caption-strip sheets, and personally inspected the actual source screenshots. Original pixels retain the actual prepared controls, saved readbacks and reopened result. The closing recap uses the actual stop summary and honest Directions warning. All87exported cue timings remain unchanged. Action/result transitions retain actual controls before their returned pages, without estimated word boundaries. Separate numerical comparisons passed. No Root hearing claim.','caption_cues_personally_reviewed':cues,'interval_contact_sheets_personally_viewed':contacts,'caption_strip_images_personally_viewed':strips,'full_frame_observations':obs})
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
