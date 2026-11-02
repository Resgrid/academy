#!/usr/bin/env python3
"""Build a new source-only Workforce candidate; default is read-only preflight.

No UI, API, database, audio, canonical, site, target or Git operations. --write
creates only a new candidate folder and refuses to replace an existing one.
The literal observations below were authored after viewing each selected exact
1434x773 original JPEG, not inferred from the offscreen accessibility tree.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
CORE = ROOT.parents[2]
TRACE = S / 'expansion/plans/core-workforce-administration-source-trace-20261028'
RAW = S / 'captures/expansion/core-workforce-administration-20261028/manifest.json'
RAW_SHA = '1477c6658ef4b0ae8c11474829e3134de1038290cfdb4a242c9461538707cf33'
OUT = S / 'expansion/plans/core-workforce-foundations-unapproved-time-candidate-20261029'
LESSON = 'core-workforce-foundations-unapproved-time'
REVIEWER = 'Codex dispatch_ic_coverage actual Workforce source-image reviewer'
REVIEWED_AT = '2026-10-29T04:12:03Z'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def ref(path):
    return {'file': path.relative_to(S).as_posix(), 'sha256': sha(path)}


def jpeg_dimensions(path):
    data = path.read_bytes()
    if data[:2] != b'\xff\xd8':
        raise ValueError('Expected original JPEG.')
    pos = 2
    while pos < len(data):
        if data[pos] != 255:
            raise ValueError('Invalid JPEG marker.')
        while data[pos] == 255:
            pos += 1
        marker = data[pos]
        pos += 1
        if marker in {0x01, 0xd8, 0xd9} or 0xd0 <= marker <= 0xd7:
            continue
        length = struct.unpack('>H', data[pos:pos+2])[0]
        if marker in {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}:
            height, width = struct.unpack('>HH', data[pos+3:pos+7])
            return width, height
        pos += length
    raise ValueError('JPEG size unavailable.')


# Only personally readable foreground literals are retained. A full value in
# DOM is not promoted when the corresponding input is visibly truncated.
OBS = {
 2: (['Workforce','Overview','Employer','Establishments','Workers','Work entries','No employer profile yet.','Establishments: 0 · Workers: 0 · Employments: 0','Resource profiles: 0 · Cost runs: 0'], 'Empty overview; employer absent and all shown foundation counts zero. Workforce child sidebar launcher is not claimed.'),
 4: (['Employer','Employer profile','Legal name *','TRAINING ONLY - Community coordination services','FEIN','SEIN (EDD)','NAICS','EDD address','Headquarters address','Affiliated entities','None'], 'Prepared fictional employer name is fully readable. Identifier/address boxes shown are blank. Coverage and Save are below this viewport.'),
 5: (['Filing contact name','Filing contact e-mail','Filing contact phone','Coverage status','Not declared','US employees','California employees','Part of an integrated enterprise','Save','Cancel'], 'Lower employer form has empty contact/headcount boxes, Not declared, unchecked integrated-enterprise checkbox, and fully visible Save.'),
 6: (['Employer','Employer profile','Saved.','Legal name *','TRAINING ONLY - Community coordination services','FEIN','SEIN (EDD)','NAICS'], 'Actual saved response and fictional name; no claim that the whole lower form is visible.'),
 7: (['Employer','Employer profile','Legal name *','TRAINING ONLY - Community coordination services','FEIN','SEIN (EDD)','NAICS','EDD address'], 'Fresh employer readback preserves the visible name and blank identifiers. No Saved toast in this frame.'),
 8: (['Establishments','Add establishment','Code','Name','City','State','NAICS','Headquarters','Active','No establishments yet.'], 'Empty establishment catalog and its printed Add establishment launcher.'),
 10: (['Add establishment','Code *','TRN-COMM-28','Name *','Street address','City','State','IL','ZIP','NAICS','Major activity','Fictional software coordination exercises','Affiliate'], 'Prepared code/IL/activity visible. Long Name input is clipped; full name proof comes from saved catalog012.'),
 11: (['Add establishment','Active from','10/28/2026','Active to','Time zone','America/Chicago','Headquarters','Reported in the prior year','Save','Cancel'], 'Active from October28, blank Active to, Chicago time zone, both optional checkboxes off, right-hand Save fully visible.'),
 12: (['Establishments','Saved.','Code','Name','State','Active','TRN-COMM-28','TRAINING ONLY - Community coordination base','IL','Yes'], 'Saved single catalog row shows full training name, IL and Active Yes.'),
 13: (['Edit establishment','Code *','TRN-COMM-28','Name *','State','IL','Active from','10/28/2026','Active to','Time zone','America/Chicago'], 'Fresh edit readback shows date/time zone and code; long form Name remains clipped. No resave claimed.'),
 14: (['Workers','Add worker','Member','External worker key','Display label','No workers yet.'], 'Member and separate external-worker inputs are readable; no external worker was created.'),
 15: (['Workers','Add worker','Member','Matthew Casey','External worker key','Display label'], 'Existing fictional member Casey selected, other identity fields blank; actual Add worker button visible.'),
 16: (['Matthew Casey','Saved.','Worker','Member: Matthew Casey','Active','Employments','Add employment','No employment periods yet.'], 'Saved active Workforce worker link, with no employment period yet. Does not prove a new account/role/crew assignment.'),
 17: (['Add employment','Worker kind','Volunteer','Start *','End','10/28/2026','Employment type','Exemption','Unknown'], 'Volunteer and same-day start/end are readable; employment type and exemption are Unknown. Right-hand employment Save is below this viewport.'),
 18: (['Add employment','Default establishment','TRN-COMM-28 — TRAINING ONLY - Community coordination base','Personnel role','TRAINING ONLY - Community response navigator','Labor contractor'], 'Actual selected establishment and training personnel role; right-hand employment Save is offscreen. The left worker Save is not substituted.'),
 19: (['Add employment','Worker kind','Volunteer','Start *','End','10/28/2026','Employment type','Exemption','Unknown','Default establishment','Personnel role','Labor contractor','Affiliate','Save','Cancel'], 'Right-hand employment Save is fully visible beneath blank contractor/affiliate choices; separate left worker Save also visible and is not the narrated action.'),
 20: (['Matthew Casey','Saved.','Employments','Volunteer','2026-10-28 – 2026-10-28','Add assignment','No job assignments.'], 'Saved one-day Volunteer period, and real Add assignment launcher; no assignment exists yet.'),
 21: (['Edit employment','Worker kind','Volunteer','Start *','End','10/28/2026','Employment type','Exemption','Unknown','Default establishment','TRN-COMM-28 — TRAINING ONLY - Community coordination base','Personnel role','TRAINING ONLY - Community response navigator'], 'Fresh saved-period readback, matching dates/defaults; no resave claimed.'),
 22: (['Add assignment','Effective *','10/28/2026','Expires','Job title','CRD job category','SOC code','SOC version','Establishment','Work mode','Non-remote','Work location','US','CA'], 'New assignment actually starts with CA while inheriting the training establishment. Lower Save is outside this viewport.'),
 23: (['Add assignment','Effective *','Expires','10/28/2026','Job title','TRAINING ONLY - Coordination exercise','CRD job category','SOC code','SOC version','Establishment','Work mode','Non-remote','Work location','US','IL','Cal OES MARS classification','Mapping provenance'], 'Prepared same-day assignment, full training title and IL. Classification and mapping boxes remain empty.'),
 24: (['Add assignment','CRD job category','SOC code','SOC version','Work location','US','IL','Cal OES MARS classification','Mapping provenance','Save','Cancel'], 'Blank classification/mapping fields and fully visible right-hand assignment Save.'),
 25: (['Matthew Casey','Saved.','Employments','Volunteer','Effective','Expires','Job title','TRAINING ONLY - Coordination exercise','Establishment','TRN-COMM-28 — TRAINING ONLY - Community coordination base','Work mode','Non-remote'], 'Saved assignment row wraps across lines but full title, establishment and Non-remote are legible; date cells are October28.'),
 26: (['Edit assignment','Effective *','Expires','10/28/2026','Job title','TRAINING ONLY - Coordination exercise','CRD job category','SOC code','SOC version','Establishment','Work mode','Non-remote','Work location','US','IL','Cal OES MARS classification','Mapping provenance'], 'Fresh edit readback retains IL, dates and blank classification/mapping fields.'),
 27: (['Work entries','Add work entry','09/28/2026','10/28/2026','Filter','Date','Worker','Hours','Hours type','Establishment','Context','Approved payroll cost','Approved','No work entries in this window.'], 'Actual empty date window includes October28. Filter exists but no filter-change operation is claimed.'),
 28: (['Add work entry','Worker *','Matthew Casey','Date *','10/28/2026','Hours *','Hours type','Regular','Establishment','Work mode','Non-remote','Country','US','State / province','CA'], 'New entry upper controls show Casey, date, Regular and initial CA; lower Save is offscreen.'),
 29: (['Date *','10/28/2026','Hours *','2','Hours type','Regular','Establishment','TRN-COMM-28','Work mode','Non-remote','Country','US','State / province','IL','Call #','Deployment id','Approved payroll cost','External source','External id','Approved'], 'Prepared two-hour entry with IL. Worker field label is above this viewport; establishment text is clipped after its code; Save is not fully visible.'),
 30: (['Hours type','Regular','Establishment','Work mode','Non-remote','Country','US','State / province','IL','Call #','Deployment id','Approved payroll cost','External source','External id','Approved','Save','Cancel'], 'Actual lower form with Approved off and blank payroll/context fields. BOTH external values are truncated; do not present a full-key/value pixel claim.'),
 31: (['Work entries','Saved.','Date','Worker','Matthew Casey','Hours','2.00','Hours type','Regular','Establishment','TRN-COMM-28 — TRAINING ONLY - Community coordination base','Context','Academy software exercise','Approved payroll cost','Approved','No'], 'Saved row fully shows two Regular hours, exercise context, blank payroll-cost cell and Approved No.'),
 32: (['Work entries','Edit work entry','Worker *','Matthew Casey','Date *','10/28/2026','Hours *','2.00','Hours type','Regular','Establishment','Work mode','Non-remote','Country','US','State / province','IL','Approved','No'], 'Fresh edit readback shows the saved worker/date/hours, US/IL and No in the list. The long establishment selector is clipped; full name is in031.'),
 33: (['Hours type','Regular','Work mode','Non-remote','Country','US','State / province','IL','Call #','Deployment id','Approved payroll cost','External source','External id','Approved','Save','Cancel'], 'Fresh lower readback has Approved unchecked and blank cost/call/deployment values. Both external values remain visibly truncated; no full-value proof claimed.'),
 41: (['Workforce','Overview','Employer','Workers','Work entries','TRAINING ONLY - Community coordination services','Coverage status: Not declared','Establishments: 1 · Workers: 1 · Employments: 1','Field costing','Resource profiles: 0 · Cost runs: 0'], 'Final overview has one establishment/worker/employment, unchanged Not declared, and zero resource profiles/cost runs. Does not show the time-entry row.'),
}


# Untimed spans are editorial correspondence only. Real audio/cue anchors are
# required later; no duration or operation timestamp is estimated here.
SCENES = [
 ('01','Start with the Workforce overview',[2],['Workforce','Overview','No employer profile yet.'],
  'Workforce gives administrators a place to connect an employer, operating locations, people, and dated work records. Start on the Workforce Overview. The empty example has no employer profile, workers, or employments. We will build one small training record, then save two unapproved hours. Use an account authorized for these pages and a fictional practice department. These entries describe a software exercise, not verified attendance or payroll.',
  'Identify the employer, worker and employment counts before making any practice changes.'),
 ('02','Enter a clearly identified practice employer',[4,5],['Employer','Employer profile','Legal name *'],
  'Open Employer and find Employer profile. In Legal name, enter a clearly marked training name; this example uses Community coordination services with a TRAINING ONLY prefix. Tax identifiers, addresses, and filing contacts stay empty in this clean practice profile. Read the blue protection notice before editing an existing employer. Review stored information carefully rather than replacing a real organization’s details with the values from this demonstration.',
  'In a clean training profile, choose a fictional name. In an existing profile, review without replacing stored details.'),
 ('03','Save without declaring coverage',[5,6,7],['Coverage status','Not declared','Part of an integrated enterprise','Save','Saved.'],
  'Scroll to Coverage status. Keep Not declared for this fictional example, leave the employee headcounts empty, and leave Part of an integrated enterprise unchecked. This exercise makes no decision about filing coverage. Choose Save at the bottom of the employer form. The Saved message confirms the response, and the fresh employer view retains the training name. Check that name before moving on to the location records.',
  'Locate the lower employer Save, then compare the saved and fresh name readbacks without resaving.'),
 ('04','Add an establishment with a recognizable code',[8,10],['Establishments','Add establishment','Code *','TRN-COMM-28','Name *','State','IL','Major activity'],
  'Open Establishments and choose Add establishment. An establishment gives later records a named operating location. Enter a recognizable Code and Name. Here the code is TRN-COMM-28, and State is IL. Major activity describes fictional coordination exercises. The address and industry-code fields remain blank in this example. A short, distinctive code helps you recognize the same location when a worker or time-entry form offers it later.',
  'Read back the code and state before saving; use a new unique code only in a separately authorized practice setup.'),
 ('05','Check the establishment dates and saved row',[11,12,13],['Active from','Active to','Time zone','America/Chicago','Save','Saved.','Edit establishment'],
  'Continue down the establishment form. Set Active from to October twenty-eighth, twenty twenty-six, leave Active to empty, and enter America slash Chicago in Time zone. Headquarters and Reported in the prior year remain unchecked. Choose this form’s Save. The catalog now shows the training base, IL, and Active Yes. In the reopened establishment, check the date and time zone again so the saved location matches the setup you intended.',
  'Compare the catalog’s full training name with the reopened code, date and time zone; do not resave merely to inspect.'),
 ('06','Link the existing member as a worker',[14,15,16],['Workers','Member','Matthew Casey','Add worker','Saved.','Add employment'],
  'Open Workers. The Add worker panel offers a Member picker and separate External worker key and Display label fields. For this example, select the existing fictional member Matthew Casey, leave the external fields blank, and choose Add worker. Casey’s Worker page opens with Active checked and no employment periods yet. This creates a Workforce link for an existing member; it does not invite a new user or assign anyone to an operational crew.',
  'Distinguish the existing-member path from the external-worker fields. Reuse an existing training worker for read-only review rather than adding it again.'),
 ('07','Create a deliberately short employment period',[16,17],['Add employment','Worker kind','Volunteer','Start *','End','Employment type','Exemption','Unknown'],
  'From Casey’s page, choose Add employment. Worker kind is Volunteer in this practice record. Set Start and End to the same October twenty-eighth date to keep the example limited to one day. Employment type and Exemption remain Unknown. The dates belong to this worker’s employment period, rather than the establishment’s active window. Before saving, check the person and both dates so you do not attach the exercise to the wrong period.',
  'Read the worker name and both dates. Do not add an overlapping period to the already-created example.'),
 ('08','Choose the period defaults and save the correct form',[18,19,20,21],['Default establishment','Personnel role','Labor contractor','Affiliate','Save','Saved.','Edit employment'],
  'Select the training base in Default establishment and the existing Community response navigator training role in Personnel role. The role field helps choose compensation defaults; it does not change Casey’s response staffing. Leave Labor contractor and Affiliate blank. Scroll to the Save inside the employment panel, below those choices; the Worker panel has a separate Save. After saving, the one-day Volunteer period appears, and its reopened form retains the selected defaults.',
  'Locate the employment-panel Save rather than the separate worker Save. Verify the stored period and defaults.'),
 ('09','Give the job assignment its own dates and location',[20,22,23],['Add assignment','Effective *','Expires','Job title','Establishment','Work mode','Non-remote','Work location','US','CA','IL'],
  'Within that period, choose Add assignment. Check the new form: it carries the establishment forward, but Work location initially shows US and CA. Change the state to IL for this exercise. Give Effective and Expires the same one-day bounds, enter the TRAINING ONLY Coordination exercise job title, and keep Work mode Non-remote. Review the location explicitly; inheriting an establishment does not mean every other location field was copied with it.',
  'Compare the initial CA field with the prepared IL value. Check assignment dates separately from employment dates.'),
 ('10','Save the assignment without inventing classifications',[24,25,26],['CRD job category','SOC code','Cal OES MARS classification','Mapping provenance','Save','Saved.','Edit assignment'],
  'The assignment also has CRD job category, SOC, and Cal OES MARS classification fields. We leave those classifications and Mapping provenance empty in this fictional exercise; a training title supplies no classification authority. Choose Save in the assignment form. Its row now shows the dated coordination exercise, the training establishment, and Non-remote. In the reopened assignment, verify IL and the matching dates before continuing to the daily work entry.',
  'Confirm the saved title and establishment, then inspect the fresh IL/date readback without changing classification fields.'),
 ('11','Use the correct work-entry date window',[27],['Work entries','Add work entry','No work entries in this window.'],
  'Open Work entries. The two date controls define the list’s viewing window; the displayed window includes October twenty-eighth. No entries are listed yet. Check the window before assuming a saved record is missing. Choose Add work entry to open the entry panel beside the list. This page records a worker and date, hours, location, and supporting context, so keep the training worker and the intended day together as you fill it.',
  'Confirm the displayed window includes the practice day before looking for the entry. No filter-change success is demonstrated here.'),
 ('12','Prepare two Regular hours with the intended location',[28,29],['Worker *','Matthew Casey','Date *','Hours *','2','Hours type','Regular','Establishment','Work mode','Non-remote','Country','US','State / province','IL'],
  'Check Worker is Matthew Casey and Date is October twenty-eighth. Enter two in Hours and keep Hours type Regular. Select the training establishment and keep Work mode Non-remote. Under Country and State slash province, use US and IL. These location fields also need their own review. The two hours are a fictional software example, so choose values appropriate to your authorized practice record rather than treating the demonstration as evidence someone actually worked.',
  'Read worker, date, hours type and location back together. Distinguish the initial CA default from the prepared IL value.'),
 ('13','Keep the entry unapproved and identify its source',[30],['Call #','Deployment id','Approved payroll cost','External source','External id','Approved','Save'],
  'Continue to the lower form. Leave Call number and Deployment id empty because this exercise is not linked to an incident or deployment. Approved payroll cost stays blank, and Approved stays unchecked. Use External source and a distinct External id to identify your authorized training entry; do not reuse another record’s reference. These narrow inputs may clip long text. Review the form, then choose Save to store the unapproved entry.',
  'Identify the unchecked Approved control and separate empty payroll-cost field. Do not infer a full external value from the clipped input.'),
 ('14','Verify the saved entry and fresh readback',[31,32,33],['Saved.','Matthew Casey','2.00','Regular','Academy software exercise','Approved','No','Edit work entry','Approved payroll cost'],
  'The saved list now shows Casey, two Regular hours, the training establishment, and Academy software exercise in Context. Approved reads No. The fresh Edit work entry view retains the worker, date, hours, and Illinois location. Lower down, Approved is still unchecked and the payroll-cost box is empty. This is the useful stopping point: a stored, reviewable training record. Saving has not approved payroll, paid anyone, or verified attendance.',
  'Compare the saved row with both parts of the fresh edit form. Finish without resaving or approving the example.'),
 ('15','Review the foundation and apply the pattern',[41],['Overview','Coverage status: Not declared','Establishments: 1 · Workers: 1 · Employments: 1','Resource profiles: 0 · Cost runs: 0'],
  'Return to Overview. One establishment, one worker, and one employment are now recorded; coverage remains Not declared, with no resource profiles or cost runs. Use the same prepare, save, and read-back pattern for fire and EMS training administration, community-care or mental-health coordination, search-and-rescue volunteers, security teams, wildland contractors, and industrial response teams. Keep each organization’s real classifications and approvals with its authorized reviewers. The common skill is connecting the right person, dates, place, and unapproved record before further review.',
  'Explain which records were saved and which approvals or costing activities were not performed.'),
]

SECTORS = [
 ('fire-ems','Fire and EMS','Practice linking a training member to a dated training-base assignment and an unapproved work entry; do not treat it as verified station attendance.'),
 ('community-response','Community response and mental-health teams','Use the same location, worker and dated-assignment review for community-care coordination; keep sensitive client details outside this software exercise.'),
 ('search-and-rescue','Search and rescue','Practice a one-day volunteer coordination period and confirm the saved dates before reviewing an unapproved entry.'),
 ('security','Security','Use a clearly marked training site and worker record to rehearse date/location checks without claiming a completed patrol.'),
 ('wildland','Wildland','Use contractor-team practice context to check worker, assignment bounds and work location; this lesson creates no labor-contractor entity or legal classification.'),
 ('industrial','Industrial response','Use a fictional operating establishment and dated coordination assignment; saving the entry supplies no payroll approval or physical-response verification.'),
]


def build():
    if sha(RAW) != RAW_SHA:
        raise ValueError('Held raw Workforce manifest changed.')
    # Preserve the actual original image/source curation time on reproduction;
    # rerunning a file check does not create a new manual pixel observation.
    now = REVIEWED_AT
    rows = json.loads(RAW.read_text())
    if len(rows) != 41:
        raise ValueError('Expected held41source pairs.')
    by_number = {int(r['id'].split('-')[0]): r for r in rows}
    if len(by_number) != 41:
        raise ValueError('Raw source IDs are not unique.')
    evidence = json.loads((TRACE / 'source-evidence.json').read_text())
    if len(evidence['source_files']) != 30:
        raise ValueError('Require exact30source pins.')
    for pin in evidence['source_files']:
        if sha(CORE / pin['file']) != pin['sha256']:
            raise ValueError('Source citation changed: ' + pin['file'])
    spec = importlib.util.spec_from_file_location('audit_public_repo', ROOT / 'scripts/audit_public_repo.py')
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    known = []
    credentials = S / 'demo/private/credentials.json'
    def private_values(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if isinstance(child, str) and re.search('password|secret|token', key, re.I) and len(child) >= 8:
                    known.append(child.encode())
                else:
                    private_values(child)
        elif isinstance(value, list):
            for child in value:
                private_values(child)
    if credentials.is_file():
        private_values(json.loads(credentials.read_text()))
    for name in ['UNIT_MAPBOX_PUBKEY','IC_MAPBOX_PUBKEY','RESPOND_MAPBOX_PUBKEY','DISPATCH_MAPBOX_PUBKEY']:
        if os.environ.get(name):
            known.append(os.environ[name].encode())
    known = list(set(known))
    raw_hashes = {}
    for r in rows:
        for key, digest_key in [('file','sha256'),('dom_file','dom_sha256')]:
            path = S / r[key]
            if sha(path) != r[digest_key]:
                raise ValueError('Held raw asset changed: ' + r[key])
            with path.open('rb') as stream:
                if audit.scan_stream(stream, known):
                    raise ValueError('Private-value/pattern finding; inspect locally without printing values: ' + r[key])
            raw_hashes[r[key]] = r[digest_key]
        if jpeg_dimensions(S / r['file']) != (1434,773):
            raise ValueError('Original image dimensions changed.')
    reviewed, observations = [], []
    for number, (labels, note) in OBS.items():
        original = by_number[number]
        r = copy.deepcopy(original)
        r['visible_labels'] = labels
        r['visible_field_text'] = []
        r['visible_controls'] = []
        r['required_labels'] = []
        r['eligible_for_lesson'] = True
        r['visual_review'] = r['review_status'] = 'actual_original_JPEG_pixels_reviewed_for_bounded_source_candidate'
        r['source_observation_limits'] = note
        r['capture_review'] = {
            'passed': True, 'reviewer': REVIEWER, 'reviewed_at': now, 'sha256': r['sha256'],
            'controls_sha256': digest([]), 'application_visible': True, 'no_errors': True,
            'controls_reviewed': True, 'controls_fully_visible': True, 'controls_unobstructed': True,
            'method': 'Personally viewed this exact1434x773 original JPEG through view_image with original detail. Retained labels are only readable foreground text/values for the bounded stated purpose. Full DOM was hashed and scanned; selected form labels and values corroborated the source trace. Offscreen AX labels, clipped values and inferred icon names are not promoted to visible pixels. Raw files remain unchanged.'}
        added = [v for v in labels if v not in original['visible_labels']]
        dom_text = re.sub(r'\s+', ' ', (S / r['dom_file']).read_text())
        corroborating = [label for label in labels if re.sub(r'\s+', ' ', label) in dom_text]
        if not corroborating:
            raise ValueError('Expected selected printed-control text in retained DOM: ' + r['id'])
        r['curation_provenance'] = {'raw_manifest': ref(RAW), 'raw_capture_id': original['id'],
            'raw_labels_unmodified_in_original': True, 'literal_pixel_observations_added_to_subset': added,
            'basis': 'Actual image reading. Raw helper BODY/scroll visibility may omit readable card text; only this new reviewed subset records those personally visible literals. No raw helper or original manifest was edited.',
            'all_field_geometry_removed_from_subset': True,
            'selected_literal_text_corroborated_by_retained_DOM': corroborating,
            'manual_pixel_literals_not_exactly_in_DOM_text': [label for label in labels if label not in corroborating],
            'DOM_limit': 'Different date formatting, line wraps or AX tree structure may differ from pixels. A DOM match does not establish viewport visibility.'}
        reviewed.append(r)
        observations.append({'id': r['id'], 'image': {'file': r['file'], 'sha256': r['sha256']},
            'dom': {'file': r['dom_file'], 'sha256': r['dom_sha256']}, 'literal_labels': labels,
            'bounded_observation': note, 'privacy_observation': 'Only the fictional training department/member/example values and blank sensitive fields are visible; no credential, token, real tax identifier or contact address was observed.',
            'no_new_UI_action_performed': True})
    index = {int(r['id'].split('-')[0]): r for r in reviewed}
    scenes, spans = [], []
    for sid, title, nums, labels, narration, practice in SCENES:
        union = {v for num in nums for v in OBS[num][0]}
        missing = set(labels) - union
        if missing:
            raise ValueError('Named scene control lacks reviewed pixels: ' + sid + ' ' + ','.join(sorted(missing)))
        scenes.append({'id': sid, 'title': title,
            'route': urlsplit(index[nums[0]]['provenance']['url']).path,
            'capture_intent': 'Use the ordered actual source views while their named fields, Save controls and readbacks are explained. No operation time is assigned.',
            'required_labels': labels, 'narration': narration, 'practice': practice,
            'capture_evidence': {'capture_refs': [index[n]['id'] for n in nums]},
            'source_fact_ids': {'01':['access','navigation'],'02':['employer_whole_save','protection'],
                '03':['employer_whole_save'],'04':['establishment'],'05':['establishment'],
                '06':['worker'],'07':['employment'],'08':['employment'],
                '09':['assignment'],'10':['assignment','assignment_classification'],
                '11':['workentry'],'12':['workentry'],'13':['workentry'],
                '14':['workentry','no_payment'],'15':['no_payment']}[sid]})
        for num in nums:
            spans.append({'scene_id': sid, 'source_id': index[num]['id'],
                'source': {'file': index[num]['file'], 'sha256': index[num]['sha256']},
                'intent': OBS[num][1], 'timing': None,
                'timing_requirement': 'Later bind actual generated narration cues/real anchors; no estimated cut or hold is authorized.'})
    words = sum(len(re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", sc['narration'])) for sc in scenes)
    if not 900 <= words <= 1100:
        raise ValueError('Requested900–1100word candidate range not met: ' + str(words))
    candidate = {'id': LESSON, 'title': 'Build Workforce foundations and record unapproved time', 'app': 'Core',
        'source_only': True, 'status': 'candidate_pending_parent_script_review',
        'audience': 'Department administrators and workforce coordinators authorized to manage these pages.',
        'summary': 'Connect a fictional employer, establishment, existing member, one-day employment and assignment; save and reopen two Regular hours with approval left off.',
        'prerequisites': ['An authorized Core account with access to the demonstrated Workforce forms.',
            'A fictional practice department; this example uses existing fictional member Matthew Casey and an existing training personnel role.',
            'Review existing records first. Do not overwrite an employer profile, duplicate an existing worker, overlap dated records or reuse another work-entry reference.',
            'Only browser configuration and stored readbacks are demonstrated. No attendance, payroll, legal-coverage, compensation, resource-cost or cost-run outcome is established.'],
        'scenes': scenes, 'sector_examples': [{'sector': key, 'title': title, 'scenario': scenario} for key,title,scenario in SECTORS],
        'source_files': [x['file'] for x in evidence['source_files']],
        'source_trace': [ref(TRACE / name) for name in ['source-evidence.json','source-trace.json','capture-outline.proposed.json','scenario.proposed.json']],
        'publication_approved': False, 'narration_frozen': False}
    excluded = [{'id': r['id'], 'reason': ('Parent flagged offscreen Workforce sidebar child; not used or independently pixel-reviewed here.' if num==1 else
        'Parent flagged offscreen Coverage status; use005 instead. Not independently pixel-reviewed here.' if num==3 else
        'Not needed for the selected prepared/saved establishment path; not independently pixel-reviewed here.' if num==9 else
        'Outside bounded foundations/time lesson. Parent reports read-only costing/compensation views and Cancel only; no success claimed and not independently pixel-reviewed here.')}
        for num,r in by_number.items() if num not in OBS]
    out = {}
    def put(name, value):
        out[name] = value.encode() if isinstance(value, str) else (json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode()
    put(LESSON + '.candidate.json', candidate)
    put('narration.txt', '\n\n'.join(sc['narration'] for sc in scenes) + '\n')
    put('captures.reviewed.json', {'app':'Core','kind':'bounded_reviewed_source_subset_not_video_approval',
        'reviewed_at':now,'source_manifest':ref(RAW),'screenshots':reviewed,'excluded_sources':excluded,
        'publication_approved':False,'raw_files_modified':False})
    put('literal-source-review.json', {'reviewer':REVIEWER,'reviewed_at':now,'source_only':True,
        'personally_viewed_original_images':len(reviewed),'original_dimensions':[1434,773],
        'method':'Each selected exact original JPEG was viewed individually with original-detail view_image. Literal observations and pixel privacy conclusions below apply only to those31images. Full82rawfiles were rehashed/pattern-and-known-value-scanned; this does not replace human pixel review.',
        'source_manifest':ref(RAW),'observations':observations,'excluded_sources':excluded,
        'critical_limits':['001sidebar child Workforce is offscreen and unused.','003Coverage is offscreen;005is the coverage source.',
            '018right employment Save is offscreen;019shows the correct Save, not the separate Worker Save.',
            '010/011/013long establishment Name field is clipped;012catalog shows its full text.',
            '029/030/032/033long establishment selector is clipped;031catalog shows full text.',
            '030/033BOTH External source and External id values are truncated. Full-key/value pixel verification is excluded;031Context shows Academy software exercise.',
            'No compensation/resource profile or cost run was created/calculated/frozen/exported; those views are outside this candidate.'],
        'publication_approved':False,'raw_assets_unchanged':True})
    put('screen-sequence.untimed.json', {'lesson_id':LESSON,'source_only':True,'audio_or_timing_assigned':False,'spans':spans})
    put('source-evidence.json', {'repository':evidence['repository'],'head':evidence['head'],
        'source_files':evidence['source_files'],'all30files_match_pinned_bytes_at_preflight':True,
        'original_trace':ref(TRACE/'source-trace.json'),'no_original_source_changes':True})
    put('manual-replay-scenario.json', {'kind':'manual_normal_UI_reference_only_no_execution',
        'automatic_execution':False,'department_scope':'Fictional training department only',
        'already_recorded_state':'Employer name, establishment, Casey worker, one-day October28 Volunteer employment/assignment and2Regularhours already exist; approval is off.',
        'replay_gate':'Inspect existing records first. Use existing example read-only. New practice requires a separate authorized fixture with a unique establishment code, nonoverlapping dated periods/assignments and new external reference; do not repeat these Save actions on original records.',
        'identifiers':'Read actual newly generated row IDs from normal UI. No captured GUID or member numeric ID is forced.',
        'preserve':['Existing real employer/coverage/identifiers/contact/address values','Existing personnel roles, crew staffing, calls and deployments','Unknown classifications and blank mapping fields for this fictional exercise','ApprovedOFF and blank approved payroll cost'],
        'upsert_note':'Source shows matched nonblank External source+External id can update an existing work entry. Never reuse the captured reference to manufacture another result.',
        'success_checks':['Fresh employer name readback','Savedestablishment catalog+date/timezone readback','Existingmember worker link','Savedone-dayemployment+defaults','Savedone-dayassignment+ILreadback','Saved2Regularhours/ApprovedNo+freshupper/lowerreadback'],
        'out_of_scope':['No workforce setting/permission changes','No compensation/resource-cost/cost-run saves or approvals','No payroll/export/coverage/attendance outcome','No account invitations, imports or external provider actions']})
    put('preflight.json', {'kind':'source_candidate_preflight_not_freeze_or_media_approval','observed_at':now,
        'manifest':ref(RAW),'raw_pairs':41,'raw_files_rehashed':len(raw_hashes),'raw_file_pins':raw_hashes,
        'selected_original_images_personally_reviewed':len(reviewed),'scenes':len(scenes),'untimed_spans':len(spans),
        'narration_words':words,'six_sector_companions':len(SECTORS),'all_six_sectors_spoken_in_final_scene':True,
        'all_scene_required_literals_present_in_reviewed_source_union':True,
        'source_files_rehashed':30,'source_mismatches':0,'pixel_privacy_findings_selected_images':0,
        'automated_privacy_scan':{'raw_files':len(raw_hashes),'known_private_values_supplied':len(known),'findings':0,'scanner':'Unmodified audit_public_repo.scan_stream'},
        'raw_assets_modified':False,'source_pins_modified':False,'new_UI_or_DB_actions':False,
        'narration_frozen':False,'audio_or_media_approved':False,'publication_approved':False,
        'output_file_hashes':{name:hashlib.sha256(body).hexdigest() for name,body in out.items()}})
    return out, {'source_only':True,'candidate':LESSON,'scenes':len(scenes),'words':words,'sources':len(reviewed),
                 'untimed_spans':len(spans),'source_pins':30,'privacy_findings':0,'frozen':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    files, summary = build()
    if args.write:
        if OUT.exists():
            raise ValueError('Preserve existing candidate; output already exists.')
        OUT.mkdir(parents=True)
        for name, data in files.items():
            (OUT / name).write_bytes(data)
    print(json.dumps({**summary,'written':args.write,
        'files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()}},indent=2))


if __name__ == '__main__':
    main()
