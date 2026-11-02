"""Freeze a focused Responder certification lesson from actual saved UI states.

The original six JPEGs were inspected at original size on 2026-10-28. No new
certification, photo, department approval, narration or video is claimed here.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-responder-certification-renewal'
OUT = SOURCES / 'expansion/plans/app-responder-certification-renewal-capture-freeze-20261028'
REVIEWED_AT = '2026-10-28T14:46:19+00:00'
RAW = Path('captures/expansion/responder/manifest.json')
RAW_SHA = '836bca3143bf045b60b4731b1a862d2024a26e76a13d632f4db75b6008b79fa1'
STEPS = [
('114-certification-list', '2e6691cd0f8e1e1ca40266d986d474367afb60db0060b02717cac87265d05764',
 'find-record', 'Find the intended certification',
 ['My certifications','Firefighter qualification','Active','Number DEMO-CERT-1'],
 'Open My certifications in Responder. This area gives the signed-in member a place to review their own certification records. The training account has an existing Firefighter qualification, marked Active, with the number DEMO-CERT-1 and an expiry date. Open the intended record before changing it. An organization can use this recordkeeping pattern for its own required qualifications, including community response, search teams, security, contractor crews, and industrial response.',
 'Locate the intended record and compare its name, number and displayed status.'),
('118-certification-renewal-ce-controls', '1064a1f4cb551fb8c6bf81e5deafdacd7775db9a8a9369bb92ab9152b79a6337',
 'review-record', 'Review dates, verification and available fields',
 ['Firefighter qualification','Active','Number DEMO-CERT-1','Verified 2026-10-25','Renew','New expiry date','New number (optional)','Hours','Date (defaults to today)','Category (course, drill, conference)','What it was'],
 'Review the record detail before acting. Check the number, issuer, area, received date, expiry date, and verification date. Our example is issued by the fictional Academy Training Board. Renew has fields for a new expiry date and an optional new number. The continuing-education section starts with zero hours and offers Hours, Date, Category, and What it was. These fields help keep an education entry attached to the correct qualification.',
 'Compare the record identity and current verification before entering an update.'),
('119-certification-ce-prepared', '4549e863df514d7b5b7c75b3a46ebc182b44e85c9576d480f6fc0326498329ca',
 'add-education', 'Review and add an education entry',
 ['0.25','Date (defaults to today)','Training software demonstration','TRAINING ONLY — Academy interface practice; no accredited credit claimed.','Add hours'],
 'For this software exercise, enter zero point two five hours. The Date field indicates that it defaults to today. We enter Training software demonstration as the category and a note explicitly saying that no accredited credit is claimed. Review the amount, date choice, category, and description before choosing Add hours. Use the actual activity information your department requires when maintaining a real record.',
 'Review one permitted training entry and choose Add hours only when its values are correct.'),
('120-certification-ce-result', 'ed24c0aa0a3c0b654ca2ad893a4aa5a0db4761258a2ccfce6654a39d211fdf72',
 'verify-education', 'Read back the saved education hours',
 ['Hours added.','Number DEMO-CERT-1','0.25 continuing-education hours','2026-10-26 · 0.25 h · Training software demonstration · TRAINING ONLY — Academy interface practice; no accredited credit claimed.'],
 'Read back the result. Hours added appears, the total is now zero point two five continuing-education hours, and the stored entry includes its date, amount, category, and note. The number is still DEMO-CERT-1. This saved ledger distinguishes an entry that reached the record from text left in a form. The displayed training entry is a software demonstration; its note does not claim an accredited course or awarded qualification.',
 'Check the saved total and ledger entry after submission.'),
('122-certification-renewal-prepared', '197090f4cdc4dd68583c1021d5f398eef18a593537fdfdb5f73d0cec75f87dd8',
 'save-renewal', 'Review and save the renewal date',
 ['Renew','New expiry date','10/27/2028','New number (optional)','Save renewal'],
 'Next, review Renew. In this recorded training example, New expiry date is set to October twenty-seven, twenty twenty-eight. New number is optional and remains blank. Check the intended expiry date and whether the credential number needs to change, then choose Save renewal. Keep an education-hours entry and a certification renewal distinct: one adds an activity to the ledger, while this action updates the certification record.',
 'Review the renewal date and optional number before Save renewal.'),
('123-certification-renewal-result', 'c951e6cd6b1bf015f03f3a44919c3f5ce08c37210a86e0265fea39fda9dd4407',
 'verify-renewal', 'Read the saved renewal and verification state',
 ['Firefighter qualification','Renewal saved.','Awaiting verification','Number DEMO-CERT-1','Expires 2028-10-27 (732 days)','Not verified by the department yet','0.25 continuing-education hours'],
 'Verify the resulting record. Renewal saved appears, the expiry date is October twenty-seven, twenty twenty-eight, and the original number remains. The status now says Awaiting verification, with Not verified by the department yet. Read that state before treating the update as reviewed. The education entry remains visible below. This same habit supports fire and EMS personnel, community paramedicine and mental health response teams, search and rescue, security companies, wildland contractors, and industrial teams: maintain the details and check the department review state.',
 'Verify the saved expiry, retained number, education total and pending verification state.')]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    assert not OUT.exists(), 'Preserve previous freezes; use a new version path.'
    assert sha(SOURCES/RAW) == RAW_SHA
    raw = json.loads((SOURCES/RAW).read_text())
    raw = raw if isinstance(raw,list) else raw.get('captures',raw.get('screenshots',[]))
    by_id = {r['id']:r for r in raw}
    scenes,selected = [],[]
    for ident,expected,scene_id,title,labels,narration,practice in STEPS:
        row = dict(by_id[ident])
        assert row['sha256'] == expected == sha(SOURCES/row['file'])
        row['visible_labels'] = labels
        row['visible_controls'] = []
        row['eligible_for_lesson'] = True
        row['capture_review'] = {'passed':True,'reviewer':'Codex exact original-size JPEG inspection',
            'reviewed_at':REVIEWED_AT,'sha256':expected,'application_visible':True,
            'labels_legible':True,'no_errors':True,
            'scope':'Only the listed readable foreground labels/values were retained. The clipped title on the education/prepared-renewal views is excluded. No photo, new-certification save, or department approval is inferred.'}
        selected.append(row)
        scenes.append({'id':scene_id,'title':title,'required_labels':labels,
            'narration':narration,'practice':practice,
            'capture_evidence':{'status':'actual_screenshot_reviewed','capture_refs':[ident]}})
    cited = []
    for name in ['index.tsx','[id].tsx']:
        file = Path('evidence/expansion/Responder/src/app/(app)/certifications')/name
        current = Path('/Users/shawn/Documents/dev/Responder/src/app/(app)/certifications')/name
        assert (SOURCES/file).read_bytes() == current.read_bytes()
        cited.append({'file':str(file),'sha256':sha(SOURCES/file),'current_source_matches_retained_snapshot':True})
    lesson = {'id':NAME,'title':'Responder: renew certifications and record education hours',
        'app':'Responder','audience':['Department members','Personnel maintaining their own records'],
        'summary':'Review an existing certification, save an education-hours entry, renew its date, and understand the resulting verification state.',
        'prerequisites':['A normal authorized Responder account and an existing training certification.','Use fictional exercise values and follow your department record-review procedure.'],
        'scenes':scenes,'source_files':[r['file'] for r in cited],
        'sector_examples':[
            {'sector':'Fire / EMS','scenario':'Keep a training qualification record and its education entries together.','practice':'Review the saved renewal and department verification state.'},
            {'sector':'Community response','scenario':'Track the qualifications your community paramedicine or mental health response team requires.','practice':'Check the record identity before updating its education ledger.'},
            {'sector':'Search and rescue','scenario':'Review team qualification expiry dates and stored education activities.','practice':'Verify the new date and the resulting review state.'},
            {'sector':'Security','scenario':'Keep staff qualification records and permitted training entries organized.','practice':'Check the saved entry and record status after submission.'},
            {'sector':'Wildland','scenario':'Maintain contractor crew qualification records and education history.','practice':'Review dates and verification before relying on the updated record.'},
            {'sector':'Industrial','scenario':'Organize response-team qualification records under the site review procedure.','practice':'Verify the retained credential number, new expiry and education total.'}],
        'capture_limitations':['Existing fictional certification only; new-record creation, editing and removal are not demonstrated.','No photo attachment or native camera operation is demonstrated.','Awaiting verification is observed after renewal; no department approval or final verification operation is demonstrated.','The fictional education entry claims no accredited credit. Displayed dates and days remaining belong to the historical recording.'],
        'authoring_status':'actual_capture_reviewed_narration_frozen',
        'media_status':'awaiting_natural_narration','export_ready':False,
        'narration_word_count':sum(len(s['narration'].split()) for s in scenes)}
    OUT.mkdir(parents=True)
    def write(name,value):
        (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    write(NAME+'.narrated-source.json',lesson)
    write('captures.reviewed.json',{'app':'Responder','screenshots':selected,
        'source_manifest':str(RAW),'source_manifest_sha256':RAW_SHA,'reviewed_at':REVIEWED_AT})
    write('source-citations.json',{'reviewed_at':REVIEWED_AT,'sources':cited})
    (OUT/'narration.txt').write_text('\n\n'.join(s['narration'] for s in scenes)+'\n')
    report = {'passed':True,'reviewed_at':REVIEWED_AT,'scenes':6,'screenshots':6,
        'words':lesson['narration_word_count'],'lesson_sha256':sha(OUT/(NAME+'.narrated-source.json')),
        'raw_captures_modified':False,'canonical_lesson_changed':False,
        'narration_generated':False,'rendered':False,'publication_approved':False}
    write('source-preflight.json',report)
    print(json.dumps(report))


if __name__ == '__main__':
    freeze()
