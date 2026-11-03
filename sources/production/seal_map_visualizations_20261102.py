"""Seal the personally reviewed saved-map-visualization master after genuine User hearing approval."""
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
NOTES={'001-library-search-for-calls-by-type': 'Actual Library search/result with previous Call hot zones heading; template description and Customize visible.', '002-selected-template-date-and-time-controls': 'Actual selected Calls by type template, Customize, Last90days and unselected department-time day/hour controls.', '003-open-call-type-choices-and-unfiltered-map-summary': 'Actual open call-type choices with Investigation unchecked and unfiltered17calls/82percent completeness.', '004-investigation-filter-and-recomputed-map-summary': 'Actual Investigation filter and recomputed8calls/63percent summary; other visible filters remain All.', '005-layer-source-and-unlocated-call-summary': 'Actual enabled Calls layer/Data explanation, filtered8call total,63percent completeness and5located Investigation entries in legend. Overlap is not interpreted as separate visible dots.', '006-dots-colour-value-and-size-controls': 'Actual Calls source, Dots, Call type colour, Count, opacity/dot-size controls and location summary. Save as new is visible. Closing recap revisits these controls, not a new save execution.', '007-private-save-name-description-and-sharing-choice': 'Actual prepared name/description/private unchecked Share with whole department and Save control before submission.', '008-saved-private-visualization-listed-by-name': 'Actual returned saved heading and My visualizations entry with description/Only visible to you. Closing recap revisits stored visibility, not an additional publication.', '009-reopened-private-view-retains-ninety-day-range': 'Actual fresh-page saved view with retained Last90days date/time controls.', '010-reopened-investigation-filter-and-other-call-filters': 'Actual fresh-page Call types Investigation setting retained; no offscreen selector is relied upon for a new action.', '011-reopened-retained-data-and-dot-display-controls': 'Actual fresh-page retained Calls/Dots/Call type/Count fields and unchanged display sliders.', '012-saved-view-expanded-map-and-investigation-legend': 'Actual saved map with side panel closed and Investigation5 legend; complete displayed map retained.', '013-filtered-totals-location-coverage-and-time-summary': 'Actual filtered8calls/63percent location coverage, dated showing window, matching Investigation8 distribution, When calls come in grid and response-time dashes with explanatory text. Final planning recap remains bounded by those actual results.'}
CFG=[('core-map-visualizations-saved-review', '4b091243275983e291126743726c86e9bdc01ac4ea1de51264c5a1e46a7280c9', 20, 74, 5, 13, '-source-20261102')]
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
 put(framefile,{'recorded_at':now,'reviewer':'Root','video_sha256':master,'method':f'Root personally viewed all{contacts} actual encoded interval contact sheets and all{strips} full-width encoded caption-strip sheets, and personally inspected the actual source screenshots. Original pixels retain the actual prepared controls, saved readbacks and reopened result. The closing planning recap revisits actual controls and actual stored result views; it does not execute another save. All74exported cue timings remain unchanged. Separate numerical comparisons passed. No Root hearing claim.','caption_cues_personally_reviewed':cues,'interval_contact_sheets_personally_viewed':contacts,'caption_strip_images_personally_viewed':strips,'full_frame_observations':obs})
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
