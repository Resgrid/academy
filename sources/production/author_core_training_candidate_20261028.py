"""Reproduce an unvoiced Training candidate with its explicit Save-control gap.

Default/--check is read-only. --write-candidate writes only its candidate package.
No browser, database, TTS, canonical/readiness, freeze, media or site mutation.
The17-row input snapshot remains historical when later raw captures are appended.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-training-administration'
BASE=Path('expansion/plans/core-training-administration-candidate-20261028')
SNAPSHOT_SHA='bd378801e758c7a6fa086df7f1e0d4dbbc7acd49678a6dbe675b4447aef8364b'
SOURCE_SHA='b24c0ebae37ad661621b50ab33719d77b0ec1554fa41e11a77b6465ea86f387a'
TITLE='Academy - Shared contact verification exercise'
DESCRIPTION='TRAINING ONLY - Practice finding and checking fictional operational contacts.'
TEXT='TRAINING ONLY. Open Contacts and find Academy Partner Directory. Check the contact identity, category and current phone details before using them. Reopen the saved contact after an edit to verify the result. This exercise does not authorize real outreach.'
QUESTION='What should you do after updating a shared contact?'
CORRECT='Reopen the saved contact and verify the updated details.'
OTHER='Assume the edit was saved without checking.'
EXCLUDED={4:'Date popup covers part of the audience controls; use005 instead.',11:'Save Training is clipped by the fixed footer. Question/answer text is also horizontally clipped. Do not promote the raw requested full literals or Save control.'}
LABELS={
 1:['New Training','Training name','Description','Training Text'],
 2:['New Training','Training name',TITLE,'Description',DESCRIPTION],
 3:['Training Text',TEXT],
 5:['Training Text',TEXT,'Minimum Score','100','%','Due Date','11/15/2026','Attachments','Choose Files','Add all Personnel','Groups To Add','Roles To Add','Users To Add','Questions','Add Question'],
 6:['Due Date','11/15/2026','Add all Personnel','Groups To Add','Roles To Add','Users To Add','Questions','Add Question','Question','Answers','Correct','Answer Text','Add Answer',QUESTION,CORRECT,OTHER,'Add Training'],
 7:['Trainings','Add Training','Name','Description','Due Date','Action',TITLE,DESCRIPTION,'11/15/2026','View Training','Edit','Report'],
 8:['Training Report','Name','Group','Viewed','Completed','Score','Result','Wallace Boden','Command','Not Viewed','Not Completed','No Score','Pending'],
 9:['View Training',TITLE,'Status:','Active','Created By:','Wallace Boden','Due By:','11/15/2026','Description:',DESCRIPTION,TEXT,'Training Attachments','Training files','Training Quiz','Take Quiz'],
 10:['Minimum Score','100','Due Date','11/15/2026 12:00:00 AM','Add Attachments','Choose Files','Currently Assigned','14 user(s) currently assigned to this training.','Add all Personnel','Add Groups','Add Roles','Add Users','Questions','Add Question'],
 12:['View Training',TITLE,'11/15/2026','Description:',DESCRIPTION,TEXT,'Training Attachments','Training files','academy-contact-verification.txt','Training Quiz','Take Quiz'],
 13:['Training Quiz','Start >','Question 1 >','Finish','Next'],
 14:['Training Quiz','Start >','Question 1 >','Finish',QUESTION,CORRECT,OTHER,'Previous','Next'],
 15:['Training Quiz','Finish','Click the finish button below to submit your quiz answers. You can go back to ensure you answered every question you wish. Your quiz will be graded and the result will be shown on the training home page.','Previous'],
 16:['Trainings','Name','Description','Due Date','Action',TITLE,DESCRIPTION,'11/15/2026','Training Complete','Edit','Report'],
 17:['Name','Group','Viewed','Completed','Score','Result','Wallace Boden','Command','10/28/2026 15:27:00','10/28/2026 15:27:45','100','Pass','Pending'],
}
LIMITS={
 1:'Blank New Training form; lower editors and controls extend offscreen. Intro begins on this form, not an unpictured catalog launcher.',
 3:'Prepared full Training Text only. Incidental default Minimum Score0 is not the later saved100 policy.',
 5:'Score100/date and Add all Personnel checked are readable. Group/role/user selector text is horizontally clipped; Matthew Casey is not a supported visible label. Bulk selection overrides those narrower inputs in source.',
 6:'Prepared one-question/two-answer quiz and first correct radio are readable; Add Training button fully visible. Narrow audience selected labels remain clipped.',
 7:'Actual new catalog row51004 alongside originalthree; View Training is not completion.',
 8:'Initial visible report rows are Pending/Not Viewed/Not Completed/No Score. Finaltwo rows are below viewport.14 assignments are established separately by010 and final017 full table, not this frame alone.',
 9:'Opening this quiz-bearing training records Viewed only. No attachment is listed yet and no completion is claimed.',
 10:'Attachment is selected but chooser filename is truncated. Retain Choose Files/Add Attachments/14 assigned literals only. Full saved filename is supplied by012. Save Training is below viewport and remains a missing instructional-control shot.',
 12:'Actual saved attachment filename and Take Quiz visible. No actual download/open or content-viewing result claimed.',
 13:'Quiz welcome stage only; top Finish tab is navigation, not the lower submit control.',
 14:'Correct option selected, before submission. Answer selection alone does not prove score/completion.',
 15:'Finish stage with actual lower-right Finish submit control. Prepared submission state;016/017 supply later result.',
 16:'Current Boden catalog action Training Complete after actual submission; score/pass must be verified in017.',
 17:'All14 rows are readable: Boden has Viewed/Completed timestamps,100/Pass; remaining13 are Pending. Page heading is above viewport. No Reset User action, credential/competence certification or everyone-complete claim.'}
SCENES=[
 ('purpose','Name a focused training',[1,2],['New Training','Training name',TITLE,'Description',DESCRIPTION],
  'Training gives you a place to publish instructions, assign people, and review their recorded progress. We are on the New Training form in the fictional Chicago Fire department. Enter Academy, Shared contact verification exercise as the Training name. Use Description for a short explanation of what the training is about. Here it says that this is practice finding and checking fictional operational contacts. A clear title and description help a member recognize the assignment before opening the full lesson.',
  'Prepare a uniquely named software practice training with a concise description.'),
 ('content','Write the actual training instructions',[3],['Training Text',TEXT],
  'Training Text is the separate area for the instructions themselves. Our exercise asks the learner to open Contacts, find Academy Partner Directory, check the contact identity and current details, and reopen an entry after an edit. Read the complete paragraph before assigning it. It gives someone a concrete task and a way to verify the result. The wording also makes clear that the exercise does not authorize real outreach. Keep the catalog description short and put the actual learning steps in Training Text.',
  'Write a short sequence with one clear verification step in Training Text.'),
 ('score-audience','Choose the score, due date and audience',[5],['Minimum Score','100','Due Date','11/15/2026','Add all Personnel','Groups To Add','Roles To Add','Users To Add'],
  'Set Minimum Score to one hundred percent for this one-question exercise and choose November fifteenth, twenty twenty-six as its Due Date. Review the audience before creating the training. Add all Personnel is checked here, which selects the whole fictional department. Groups To Add, Roles To Add, and Users To Add are the narrower alternatives when you choose a smaller audience. Do not assume a previously selected individual limits an assignment while Add all Personnel is checked. We will verify the resulting fourteen assignments after saving.',
  'Choose the intended audience and review the bulk checkbox before submitting a practice assignment.'),
 ('question','Add a question and mark its correct answer',[6],['Questions','Add Question','Question','Answers','Correct','Answer Text','Add Answer',QUESTION,CORRECT,OTHER,'Add Training'],
  'In Questions, use Add Question and enter: What should you do after updating a shared contact? Add two answers. The first says to reopen the saved contact and verify the updated details. The second says to assume the edit was saved without checking. Mark the first answer as correct using its radio control. Check the question, both answers, and the selected correct answer before choosing Add Training. One clear question is enough to demonstrate the difference between assigning content and checking the learner’s response.',
  'Add two distinct answers and verify which radio control marks the correct one.'),
 ('initial-report','Verify creation and the initial progress report',[7,8],['Trainings',TITLE,'11/15/2026','View Training','Report','Training Report','Viewed','Completed','Score','Result','Wallace Boden','Not Viewed','Not Completed','No Score','Pending'],
  'The new training appears in the catalog with its description and due date, alongside the existing training entries. Open Report for this training before completing the exercise. The report separates Viewed, Completed, Score, and Result. Boden’s initial row says Not Viewed, Not Completed, No Score, and Pending. An assignment has been created, but that row does not yet record participation. Use these separate columns to decide whether someone has opened the training, submitted the quiz, or met the required score.',
  'Find your new catalog row and read one assignee’s initial progress columns.'),
 ('learner','Read the saved learner view',[9],['View Training',TITLE,'Due By:','11/15/2026','Description:',DESCRIPTION,TEXT,'Training Quiz','Take Quiz'],
  'Open View Training for the saved exercise. Check the title, due date, description, and full training text from the learner’s side. This training has a quiz, so opening its page records that it was viewed; the learner still needs to answer and submit the quiz. Take Quiz is a separate action in the right-hand panel. Before taking it, review the instructions and any training files. The learner view is a useful check that the content people receive matches what you meant to assign.',
  'Open the saved learner view and verify its title, due date and complete instructions.'),
 ('attachment','Add and verify a practice handout',[10,12],['Add Attachments','Choose Files','Currently Assigned','14 user(s) currently assigned to this training.','Save Training','Training Attachments','Training files','academy-contact-verification.txt'],
  'On the edit form, Add Attachments provides a file chooser. Choose the fictional contact-verification text handout. Currently Assigned still shows fourteen users, so this edit is adding a file to an existing assignment. Use Save Training at the bottom of the form, then reopen the learner view. Training files now lists academy-contact-verification dot txt. That listed filename is the saved attachment readback. File selection by itself was only preparation; the learner page confirms that the handout is attached to this training.',
  'Attach a software-only handout and verify its filename on the saved learner page.'),
 ('answer','Start the quiz and select an answer',[12,13,14],['Take Quiz','Training Quiz','Start >','Question 1 >','Next',QUESTION,CORRECT,OTHER],
  'Choose Take Quiz and read the welcome stage. Use Next to open Question One. The same question and two answers from the training editor now appear as learner choices. Select the answer that says to reopen the saved contact and verify the updated details. The filled radio control shows the current choice. Use Next to continue. Selecting an answer is still preparation; a quiz result is recorded after the learner submits it. You can use Previous to review the question before finishing.',
  'Read both quiz options and select the answer that matches the training instructions.'),
 ('submit','Submit and check the catalog result',[15,16],['Training Quiz','Finish','Previous',TITLE,'Training Complete','Report'],
  'At the Finish stage, read the instruction to submit the quiz answers. The Finish control at the lower right performs that submission; the Finish label across the top identifies the stage. Submit once and check the returned catalog. For Boden, this exercise now shows Training Complete. That is the completion indicator for the current learner. Open Report to check the score and pass result as well, rather than treating a completed submission as proof of the required score.',
  'Submit the prepared quiz once and inspect the returned completion indicator before opening Report.'),
 ('results','Read the result and plan follow-up',[16,17],['Report','Name','Group','Viewed','Completed','Score','Result','Wallace Boden','100','Pass','Pending'],
  'Boden’s row now has viewed and completed timestamps, a score of one hundred, and Pass. The other thirteen assignments remain Pending. Follow up with those learners separately. Chicago Fire can use this workflow for a department software refresher. Community care and mental health teams can assign operational process learning; search and rescue can review support procedures; security teams can teach site workflows; wildland crews can prepare seasonal information; and industrial response teams can review facility coordination steps. These recorded results describe this training and quiz; professional qualifications belong in their own reviewed process.',
  'Compare the completed learner’s score and result with the remaining pending rows.')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()

def prepare(sources):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    snapshot=sources/BASE/'raw-manifest-17-rows.json';evidence=sources/BASE/'source-evidence.json'
    assert sha(snapshot)==SNAPSHOT_SHA and sha(evidence)==SOURCE_SHA
    sources_doc=json.loads(evidence.read_text())
    for x in sources_doc['files']:assert sha(sources/x['retained_file'])==x['sha256'],x['path']
    attachment=sources_doc['attachment'];assert sha(sources/attachment['file'])==attachment['sha256']
    raw=json.loads(snapshot.read_text());assert len(raw)==17
    rows={int(x['id'][:3]):x for x in raw};accepted=[];rejected=[]
    for n,row in rows.items():
        assert sha(sources/row['file'])==row['sha256'] and sha(sources/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(sources/row['file'])==(row['width'],row['height'])
        out=copy.deepcopy(row);labels=LABELS.get(n,[])
        out.update(visible_labels=labels,visible_controls=[],visible_field_text=[],required_labels=labels,missing_required_labels=[],
            eligible_for_lesson=n not in EXCLUDED,visual_review='actual_pixels_and_full_dom_reviewed',review_status='visually_reviewed',source_only=True,
            scope_limit=LIMITS.get(n,'Prepared fields only; saved results require the later owning-screen readback.'),
            label_observation_method='Independent overview and original-size review of all17 JPEGs. Shared fullDOM navigation and bodies/differences reviewed. Only actually readable scoped labels retained; no clipped picker names, truncated chooser filename, offscreen Save or metadata-only controls.')
        out['url']=row.get('url',row.get('provenance',{}).get('url'))
        out['captured_at']=row.get('captured_at',row.get('provenance',{}).get('captured_at'))
        out['capture_review']={'passed':n not in EXCLUDED,'reviewer':'Codex actual original-size stored-image/full-DOM review','reviewed_at':'2026-10-28',
            'sha256':row['sha256'],'controls_sha256':visible_controls_digest([]),'application_visible':True,'no_errors':n not in EXCLUDED,
            'controls_reviewed':True,'controls_fully_visible':n not in EXCLUDED,'controls_unobstructed':n not in EXCLUDED,
            'method':'Scoped literal pixel review; all raw bytes and field redactions unchanged. Datepopup004 and clippedSave011 rejected, regardless of requested raw metadata.'}
        if n in EXCLUDED:out['exclusion_reason']=EXCLUDED[n];rejected.append(out)
        else:accepted.append(out)
    by_id={x['id']:x for x in accepted};lesson={'id':NAME,'title':'Create training, assign members and verify quiz results','app':'Core',
        'audience':['department training administrators','assigned members'],
        'summary':'Create a focused software training, verify its audience and handout, complete a one-question quiz and distinguish viewed, completed, score and pass results.',
        'prerequisites':['Use a fictional practice department and the existing permission to create/update training and review its report.','Prepare an appropriate practice topic and a public software-only handout.'],
        'source_files':[x['retained_file'] for x in sources_doc['files']],'candidate_only':True,'export_ready':False,'publication_approved':False,'source_complete':False,'scenes':[],
        'sector_examples':{'Chicago Fire':'Assign a fictional contact-verification software refresher and review per-person quiz results.','Community care and mental health':'Assign operational process learning without patient details or a clinical authorization claim.','Search and rescue':'Assign support-procedure learning and follow up on pending participants.','Security':'Teach site software workflows with fictional site details.','Wildland':'Prepare seasonal information and review each learner’s recorded result.','Industrial response':'Review facility coordination software steps; the quiz result does not certify equipment or response readiness.'}}
    seq=[];gaps=[]
    for slug,title,numbers,labels,narration,practice in SCENES:
        ids=[rows[n]['id'] for n in numbers];assert set(ids)<=set(by_id)
        union={label for ident in ids for label in by_id[ident]['visible_labels']};missing=sorted(set(labels)-union)
        assert missing==(['Save Training'] if slug=='attachment' else []),(slug,missing)
        if missing:gaps.append({'scene_id':slug,'missing_required_labels':missing,'required_shot':'Normal full-viewport EditTraining51004 bottom with unobscured Save Training; no submit or progress reset needed.','unqualified_related_source':'018-edit-full-page.jpg is parent retained but unmanifested and unsuitable for current whole-viewport renderer.','source_complete':False})
        lesson['scenes'].append({'id':slug,'title':title,'route':by_id[ids[0]]['url'].split(':18967')[-1],
            'capture_refs':ids,'required_labels':labels,'capture_intent':'Use actual prepared controls before owning saved results; the attachment Save-control interval remains missing.',
            'narration':narration,'practice':practice,'missing_capture_labels':missing})
        seq.append({'scene_id':slug,'title':title,'capture_refs':ids,'required_labels':labels,'narration':narration,'missing_capture_labels':missing,'timing':'untimed; no audio, cues or duration estimate'})
    words=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",' '.join(x['narration'] for x in lesson['scenes'])))
    assert 600<=words<=1100
    scenario={'id':NAME+'-20261028','mode':'Manual normal-UI replay definition only; helper executes no application operations','department':'Isolated fictional Department51 Firehouse51',
        'actual_returned_training_id_parent_provenance':51004,'training':{'name':TITLE,'description':DESCRIPTION,'training_text':TEXT,'minimum_score_percent':100,'due_date':'2026-11-15','add_all_personnel':True},
        'quiz':{'question':QUESTION,'answers':[{'text':CORRECT,'correct':True},{'text':OTHER,'correct':False}]},'attachment':attachment,
        'actors':{'creator_editor_and_assigned_learner':'Wallace Boden','actual_assigned_count':14,'actual_completed_learner_count':1,'other_pending_count':13},
        'guards':['Confirm the isolated fictional department; search the exact training name and reopen rather than duplicate or overwrite an unknown training.','Use actual returned IDs;51004 is observed provenance, not a reusable reserved insertion ID.','Add all Personnel intentionally assigns the whole fictional department despite narrower selected inputs. Use a separately reviewed audience outside this sandbox.','Keep the three baseline trainings and all existing assignment history unchanged. No Reset User, deletion, permission, authentication or credential operation.','Use the retained software-only TXT; no real-person information, external delivery, clinical/credential or accreditation claim.'],
        'replay':['New Training→name/description/Training Text→Minimum Score100→Due Date11/15/2026→Add all Personnel.','Add Question→two answers→firstcorrectradio→Add Training once→catalog and initial Report.','Open learner View→review actual content; viewing this quiz-bearing training is not quiz submission.','Edit same new training→Choose Files ownTXT→ordinary Save Training→reopen learner page and verify listed filename.','Take Quiz→Next→correct answer→Next→lower-rightFinish once→catalogTraining Complete→Report100Pass.'],
        'readback_boundaries':['CurrentlyAssigned14 and final reportall14 verify audience; initialreport008 clipsfinaltwo.','Chooser010filename is truncated; saved012 provesfullfilename. No actualdownload/open captured.','Score100/Pass applies to Boden only;13othersPending. Completion timestamp and threshold result are separate.','Current source without quiz can markcompletiononview; this demonstrated training containsaquiz.','004popup/011clippedSave excluded; source freeze awaits normal viewport SaveTraining shot.']}
    review={'kind':'core_training_administrative_source_completion_review','status':'candidate only; one known capture-control gap; no source/narration freeze',
        'raw_snapshot_sha256':SNAPSHOT_SHA,'source_evidence_sha256':SOURCE_SHA,'scenes':10,'spoken_words':words,'original_jpegs_reviewed':17,'full_dom_files_reviewed':17,
        'media_dom_hash_matches':34,'accepted_source_rows':15,'excluded_rows':EXCLUDED,'known_missing_scene_requirements':gaps,
        'administrative_operations_captured':['Create unique training/title/description/instruction text.','Set minimum score100 and explicit due date.','Bulk assign14fictionalusers and verify resultingassignmentcount.','Author onequestion/twoanswers andcorrectradio.','Verify saved catalog and initialpending report.','Read saved learnercontent.','Select attachment and verify saved filename.','Start/answer/submitquiz.','Read Boden Viewed/Completed/100/Pass and13Pending.'],
        'not_demonstrated':['Unobscured normal-viewport SaveTraining editcontrol.','Readable specificselectedgroup/role/user names in narrow005/006pickers.','Actual attachment download/open.','A nonquiz acknowledgement workflow, failed-score/retry/reset or completion by other13users.','Qualification/accreditation/providerdelivery/native-device proof.'],
        'matrix_relationship':'Original detailed topic17-trainings now has bounded actual source operations, but retains pending/unqualified video status until complete source review, narration/media and strict publication gate. No existing completion matrix or canonical is edited.',
        'dom_review_method':'Full common NewTraining001 record, exact differences002–006, shared common navigation and full bodies007/008/009/010/013 with every complete difference011/012/014–017 reviewed. Raw images/DOM remain unchanged.',
        'source_bindings':[{'id':x['id'],'file':x['file'],'sha256':x['sha256'],'dom_file':x['dom_file'],'dom_sha256':x['dom_sha256']} for x in raw]}
    return {'candidate.json':lesson,'captures.reviewed.json':{'app':'Core','source_only':True,'export_ready':False,'publication_approved':False,'source_snapshot':(BASE/'raw-manifest-17-rows.json').as_posix(),'source_snapshot_sha256':SNAPSHOT_SHA,'screenshots':accepted,'rejected_sources':rejected},
        'screen-sequence.json':{'id':NAME,'source_complete':False,'status':'untimed incomplete candidate','scenes':seq},'scenario.json':scenario,'source-review.json':review}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--check',action='store_true');p.add_argument('--write-candidate',action='store_true');p.add_argument('--output-dir',type=Path)
    a=p.parse_args();out=(a.output_dir or a.sources/BASE).resolve();canonical=(a.sources/'expansion/lessons').resolve()
    assert out!=canonical and canonical not in out.parents,'Canonical output prohibited.'
    docs=prepare(a.sources.resolve())
    for name,obj in docs.items():
        f=out/name
        if f.exists():assert f.read_bytes()==encoded(obj),'Retain historical output and choose a new version.'
    if a.write_candidate:
        out.mkdir(parents=True,exist_ok=True)
        for name,obj in docs.items():
            f=out/name
            if not f.exists():
                with f.open('xb') as stream:stream.write(encoded(obj))
    print(json.dumps({'candidate_valid':True,'source_complete':False,'canonical_or_media_mutations':False,'scenes':10,'words':docs['source-review.json']['spoken_words'],
        'gap':docs['source-review.json']['known_missing_scene_requirements'],'files':[{'file':name,'sha256':hashlib.sha256(encoded(obj)).hexdigest()} for name,obj in docs.items()]},indent=2))

if __name__=='__main__':main()
