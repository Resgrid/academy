"""Bind the genuine post-quiz additional-file flow, preserving Training v1.

Default/--check is read-only. --write-source writes the new candidate and frozen
input packages only. Parent script review still precedes narration production.
No audio, guessed timing, canonical/readiness, website or application operation.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-training-administration'
OLD=Path('expansion/plans/core-training-administration-candidate-20261028')
NEW=Path('expansion/plans/core-training-administration-candidate-20261028-v2')
FREEZE=Path('expansion/plans/core-training-administration-capture-freeze-20261028-v2')
OLD_HELPER=Path('production/author_core_training_candidate_20261028.py')
OLD_HELPER_SHA='70da3255fe2a97dc468fcc5dfbb10c94da221b96d085a0a81340cda2cfa55d1e'
RAW_SHA='6bc31c9b47342b8f408976e11b4607eea99c4c0d665a1f00174ce751fec245e4'
FIXTURE_SHA='64335214582159063ef20c673b606f0d07d4e7e413c52288ac820c1d1ac77fa2'
REVIEWED_AT='2026-10-28T20:55:47Z'
ATTACHMENT_NARRATION='An administrator can add another handout after a learner has completed the quiz. This training already lists the original contact-verification file and quick-check dot txt. On Edit, Existing Attachments identifies those saved files and Currently Assigned still shows fourteen users. Under Add Attachments, choose review dot txt. Check the selected filename and use Save Training at the bottom of this form. Reopen the learner view: Training files now lists all three handouts. This completed learner has no Take Quiz panel here. Verify the assignment count and existing result separately when maintaining a training.'
RESULT_NARRATION='After that edit, Report still shows Boden’s completed quiz, score of one hundred, and Pass. Viewed records the most recent opening, so its displayed time can be later than the completion time. The other thirteen assignments remain Pending. Follow up with those learners separately. Chicago Fire can use this workflow for a department software refresher. Community care and mental health teams can assign operational process learning; search and rescue can review support procedures; security teams can teach site workflows; wildland crews can prepare seasonal information; and industrial response teams can review facility coordination steps. These recorded results describe this training and quiz; professional qualifications belong in their own reviewed process.'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()

def prepare(sources):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    from expansion_site import lesson_content_digest
    assert sha(sources/OLD_HELPER)==OLD_HELPER_SHA
    spec=importlib.util.spec_from_file_location('historical_training_candidate_v1',sources/OLD_HELPER)
    v1=importlib.util.module_from_spec(spec);spec.loader.exec_module(v1)
    historical=v1.prepare(sources)
    for name,obj in historical.items():assert (sources/OLD/name).read_bytes()==v1.encoded(obj),name
    snapshot=sources/NEW/'raw-manifest-23-rows.json';fixtures=sources/NEW/'attachment-fixtures.json'
    assert sha(snapshot)==RAW_SHA and sha(fixtures)==FIXTURE_SHA
    raw=json.loads(snapshot.read_text());assert len(raw)==23
    by_number={int(r['id'][:3]):r for r in raw};assert set(by_number)==set(range(1,24))
    fixture_doc=json.loads(fixtures.read_text())
    for r in fixture_doc['files']:assert sha(sources/r['file'])==r['sha256']
    for row in raw:
        assert sha(sources/row['file'])==row['sha256'] and sha(sources/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(sources/row['file'])==(row['width'],row['height'])
    captures=copy.deepcopy(historical['captures.reviewed.json'])
    captures.update(source_snapshot=(NEW/'raw-manifest-23-rows.json').as_posix(),source_snapshot_sha256=RAW_SHA,
        source_complete=True,publication_approved=False,export_ready=False)
    new_labels={
      18:['Existing Attachments','academy-contact-verification.txt','Add Attachments','Choose Files','Currently Assigned','14 user(s) currently assigned to this training.','Save Training'],
      19:['Minimum Score','100','Due Date','Existing Attachments','academy-contact-verification.txt','Add Attachments','Choose Files','quick-check.txt','Currently Assigned','14 user(s) currently assigned to this training.'],
      20:['View Training',v1.TITLE,'Training Attachments','Training files','academy-contact-verification.txt','quick-check.txt'],
      21:['Existing Attachments','quick-check.txt','Add Attachments','Choose Files','review.txt','Currently Assigned','14 user(s) currently assigned to this training.','Save Training','Cancel'],
      22:['View Training',v1.TITLE,'Training Attachments','Training files','academy-contact-verification.txt','quick-check.txt','review.txt'],
      23:['Training Report','Name','Group','Viewed','Completed','Score','Result','Wallace Boden','Command','10/28/2026 15:52:50','10/28/2026 15:27:45','100','Pass','Pending'],
    }
    limits={
      18:'Read-only existing-file/control view before the additional selections. Save Training fully visible, but this is not the selected-review file frame.',
      19:'quick-check.txt selected, original file and14assigned readable. Save Training is below viewport despite raw state prose claiming otherwise. Used only for prepared file selection;020 proves the two saved files.',
      20:'Both existing handouts fully listed after quick-check save. Already-completed learner has no Take Quiz panel. This is the genuine before state for adding review.txt.',
      21:'Actual normal anchor viewport shows review.txt selected and Save Training fully unobscured, with14assigned. quick-check existing filename readable; original filename at the top is clipped and deliberately omitted here.020/022 supply full original filename. Question and first answer input text horizontally clipped and excluded.',
      22:'Actual saved learner view lists all three handouts after the parent-recorded ordinary Save. No Take Quiz panel for completed learner; no download/open or renewed quiz completion claimed.',
      23:'Post-edit Boden row is fully visible with Viewed15:52:50, Completed15:27:45,100/Pass. Remaining13Pending are confirmed by this full DOM and earlier017whole14-row image; current picture shows only the upper12rows, not all14simultaneously. No ResetUser, reassignment, timestamp equality or additional quiz submission.'}
    for n in range(18,24):
        row=copy.deepcopy(by_number[n]);labels=new_labels[n]
        row.update(visible_labels=labels,visible_controls=[],visible_field_text=[],required_labels=labels,missing_required_labels=[],
            eligible_for_lesson=True,visual_review='actual_pixels_and_full_dom_reviewed',review_status='visually_reviewed',source_only=True,
            scope_limit=limits[n],state={'reviewed_observation':limits[n],'reviewer_application_mutations':[]},
            label_observation_method='All six new original-size JPEGs independently viewed and every full-DOM difference from reviewed010/012/017 inspected. Selected filename review.txt restored from actual pixels; generic file-input internals are not used. Offscreen/clipped metadata is omitted.')
        row['url']=row.get('url',row.get('provenance',{}).get('url'))
        row['captured_at']=row.get('captured_at',row.get('provenance',{}).get('captured_at'))
        row['capture_review']={'passed':True,'reviewer':'Codex independent original-size pixel/full-DOM review','reviewed_at':REVIEWED_AT,
            'sha256':row['sha256'],'controls_sha256':visible_controls_digest([]),'application_visible':True,'no_errors':True,
            'controls_reviewed':True,'controls_fully_visible':True,'controls_unobstructed':True,
            'method':limits[n]+' No frame, source DOM, CSS or application state changed; scoped visible labels only.'}
        captures['screenshots'].append(row)
    assert len(captures['screenshots'])==21 and len(captures['rejected_sources'])==2
    assert all(not r['eligible_for_lesson'] for r in captures['rejected_sources'])
    by_id={r['id']:r for r in captures['screenshots']}
    lesson=copy.deepcopy(historical['candidate.json']);lesson['source_complete']=True
    scenes={s['id']:s for s in lesson['scenes']}
    a=scenes['attachment'];a.update(title='Add another handout after quiz completion',route='/User/Trainings/Edit?trainingId=51004#addQuestionButton',
        capture_refs=[by_number[n]['id'] for n in [20,21,22]],required_labels=['Training files','academy-contact-verification.txt','quick-check.txt','Existing Attachments','Add Attachments','Choose Files','review.txt','Currently Assigned','14 user(s) currently assigned to this training.','Save Training'],
        narration=ATTACHMENT_NARRATION,practice='Add a software-only handout to your own practice training, then verify the saved file list and preserved assignment count.',missing_capture_labels=[])
    result=scenes['results'];result.update(capture_refs=[by_number[23]['id']],route='/User/Trainings/Report?trainingId=51004',
        narration=RESULT_NARRATION,required_labels=['Training Report','Name','Group','Viewed','Completed','Score','Result','Wallace Boden','100','Pass','Pending'],missing_capture_labels=[])
    order=['purpose','content','score-audience','question','initial-report','learner','answer','submit','attachment','results']
    lesson['scenes']=[scenes[slug] for slug in order]
    sequence=[]
    for scene in lesson['scenes']:
        scene['missing_capture_labels']=[]
        scene['capture_intent']='Use the actual ordered controls before their saved result. Additional review.txt flow follows quiz completion; no post-completion Take Quiz is assumed.'
        union={label for ident in scene['capture_refs'] for label in by_id[ident]['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        sequence.append({'scene_id':scene['id'],'title':scene['title'],'capture_refs':scene['capture_refs'],
            'required_labels':scene['required_labels'],'narration':scene['narration'],'practice':scene['practice'],
            'source_limits':[by_id[ident]['scope_limit'] for ident in scene['capture_refs']],
            'timing':'untimed; no audio, cuts, cues or duration estimate'})
    # Other eight spoken paragraphs remain byte-identical to v1.
    old_scenes={s['id']:s for s in historical['candidate.json']['scenes']}
    for scene in lesson['scenes']:
        if scene['id'] not in {'attachment','results'}:assert scene['narration']==old_scenes[scene['id']]['narration']
    report_dom=(sources/by_number[23]['dom_file']).read_text()
    assert report_dom.count('- cell "Pending"')==13 and report_dom.count('- cell "Pass"')==1
    assert '10/28/2026 15:52:50' in report_dom and '10/28/2026 15:27:45' in report_dom
    narration='\n\n'.join(s['narration'] for s in lesson['scenes'])+'\n'
    words=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert 600<=words<=1100
    scenario=copy.deepcopy(historical['scenario.json'])
    scenario.update(id=NAME+'-20261028-v2',attachment_files=fixture_doc['files'],
        ordered_actual_extra_edits=[{'pending_source':by_number[19]['id'],'saved_source':by_number[20]['id'],'file':'quick-check.txt','limit':'Pending019 does not show Save; no single-frame submit claim.'},
            {'before_existing_files_source':by_number[20]['id'],'pending_and_save_source':by_number[21]['id'],'saved_source':by_number[22]['id'],'file':'review.txt','normal_save_parent_provenance':True}],
        final_report={'source':by_number[23]['id'],'preserved_completed_timestamp':'10/28/2026 15:27:45','refreshed_viewed_timestamp':'10/28/2026 15:52:50','score':100,'result':'Pass','assigned_count':14,'pending_count':13,'count_limit':'14/13 current fullDOM plus earlier017whole-roster picture; not all14simultaneously visible in023.'})
    scenario['replay']=['Create the uniquely named training,100minimum,due date and all14fictional members; add the one-question/two-answer quiz and save once.','Read the initial report and learner content; original handout is attached before the quiz and read back012.','Complete actual quiz once through Next/answer/Finish; verify016/017completion100Pass.','On completed training edit, add quick-check.txt and verify020lists firsttwohandouts.','Reopen Edit: select review.txt using normal chooser, normal browser anchor scroll preserves selection;021shows selectedfilename plus SaveTraining. Saveonce.','Reopen learner:022lists allthreefiles with no TakeQuiz. Check023report preserves completion/100Pass,14assignments/13Pending. No reset or further quiz submission.']
    scenario['readback_boundaries']=['Additional-file teaching sequence is020existingtwo→021reviewselected/unobscuredSave→022allthree→023posteditreport.','019quick-check selectedfile is genuine but Saveoffscreen; raw prose corrected only in curated metadata.','021originalfilename is clipped at top; use020/022 for full filename.','Viewed refreshes on every training reopen and may be later than Completed; no timestamp equality or reset implication.','All14 count is not claimed as simultaneously pictured023;CurrentAssigned14 plus fullDOM/earlier017 establish it.','Original004/011 and unmanifested1434x1801fullpage diagnostic remain excluded from render source.']
    review={'kind':'core_training_administrative_source_completion_review_v2','status':'complete bounded source version for parent script review; not a qualified video',
        'historical_candidate_unchanged':{'folder':OLD.as_posix(),'helper_sha256':OLD_HELPER_SHA},'raw_snapshot_sha256':RAW_SHA,
        'scenes':10,'spoken_words':words,'original_jpegs_individually_reviewed':23,'full_dom_files_reviewed':23,'media_dom_hash_matches':46,
        'accepted_sources':21,'rejected_sources':[4,11],'known_missing_scene_requirements':[],
        'closed_gap':'021normal complete viewport independently shows review.txt selected,CurrentlyAssigned14 and fully visible SaveTraining.022lists allthree saved files;023preserves100Pass.',
        'known_pixel_limits':limits,'helper_executes_application_operations':False,
        'administrative_completion':'Actual create/content/audience/question/save/report,learnerquizcompletion,post-completionadditionalattachmentmaintenance and finalreport source coverage. Existing canonical/public video status remains unchanged.',
        'source_bindings':[{k:r[k] for k in ['id','file','sha256','dom_file','dom_sha256']} for r in raw],
        'privacy_and_location_limits':'Only fictional software-learning data; no realGPS/auth/membergrants/reset/provider-delivery or qualification claims.'}
    candidate_docs={'candidate.json':encoded(lesson),'captures.reviewed.json':encoded(captures),
        'screen-sequence.json':encoded({'id':NAME,'source_complete':True,'status':'untimed source-complete candidate for parent review','scenes':sequence}),
        'scenario.json':encoded(scenario),'source-review.json':encoded(review)}
    freeze_docs={NAME+'.narrated-source.json':candidate_docs['candidate.json'],NAME+'.captures.reviewed.json':candidate_docs['captures.reviewed.json'],
        NAME+'.screen-sequence.json':candidate_docs['screen-sequence.json'],'narration.txt':narration.encode()}
    metadata={'schema_version':1,'id':NAME,'status':'frozen source input version for parent script review; no audio or publication qualification',
        'candidate_version':NEW.as_posix(),'historical_v1_preserved':True,'parent_script_review_pending':True,
        'narrated_source_sha256':hashlib.sha256(freeze_docs[NAME+'.narrated-source.json']).hexdigest(),'authoring_sha256':lesson_content_digest(lesson),
        'spoken_words':words,'scenes':10,'reviewed_sources':21,'excluded':[4,11],'raw_snapshot':{'file':(NEW/'raw-manifest-23-rows.json').as_posix(),'sha256':RAW_SHA},
        'attachment_fixtures':{'file':(NEW/'attachment-fixtures.json').as_posix(),'sha256':FIXTURE_SHA},
        'source_evidence':{'file':(OLD/'source-evidence.json').as_posix(),'sha256':v1.SOURCE_SHA},
        'outputs':[{'file':name,'sha256':hashlib.sha256(payload).hexdigest()} for name,payload in freeze_docs.items()],
        'spoken_changes':[{'scene_id':slug,'before':old_scenes[slug]['narration'],'after':scenes[slug]['narration']} for slug in ['attachment','results']],
        'scene_order':order,'order_reason':'Completed quiz precedes new post-completion attachment edit; there is no implied TakeQuiz after completed learner view.',
        'timing':'No audio/cue/cut estimates or production media created.'}
    freeze_docs['source-hashes.json']=encoded(metadata)
    return candidate_docs,freeze_docs

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--check',action='store_true');p.add_argument('--write-source',action='store_true')
    p.add_argument('--candidate-output',type=Path);p.add_argument('--freeze-output',type=Path)
    a=p.parse_args();sources=a.sources.resolve();candidate,freeze=prepare(sources)
    dirs=[(a.candidate_output or sources/NEW,candidate),(a.freeze_output or sources/FREEZE,freeze)];canonical=(sources/'expansion/lessons').resolve()
    planned=[]
    for directory,docs in dirs:
        directory=directory.resolve();assert directory!=canonical and canonical not in directory.parents,'Canonical output prohibited.'
        planned += [(directory/name,payload) for name,payload in docs.items()]
    assert len({str(path) for path,_ in planned})==len(planned),'Output packages must be distinct.'
    for path,payload in planned:
        if path.exists():assert path.read_bytes()==payload,'Retain historical output and choose a new version.'
    if a.write_source:
        for path,payload in planned:
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():
                with path.open('xb') as stream:stream.write(payload)
    meta=json.loads(freeze['source-hashes.json'])
    print(json.dumps({'source_complete':True,'parent_script_review_pending':True,'canonical_or_media_mutations':False,
        'scenes':10,'words':meta['spoken_words'],'authoring_sha256':meta['authoring_sha256'],
        'outputs':[{'file':str(path),'sha256':hashlib.sha256(payload).hexdigest()} for path,payload in planned]},indent=2))

if __name__=='__main__':main()
