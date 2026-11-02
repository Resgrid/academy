"""Reproduce the bounded, unvoiced Certification administration candidate.

Default/--check reads and verifies only. --write-source writes new source-review
artifacts only, refusing to replace changed existing bytes. No canonical lesson,
readiness, timing, media, browser, application, database or provider operation.
The original Core source is read only to verify the retained source-profile pins.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
CORE = ROOT.parents[2]
NAME = 'core-certification-administration'
BASE = Path('expansion/plans/core-certification-administration-candidate-20261028')
RAW = Path('captures/expansion/core-certification-administration-20261028/manifest.json')
REVIEW = Path('captures/expansion/core-certification-administration-20261028-reviewed/manifest.json')
TRACE = Path('expansion/plans/core-certification-administration-source-trace-20261028')
PINS = {
    RAW: '72ed387d579edea9547914e46f8b08f1695c10028e2d1a6f0a2353a7243d308e',
    TRACE / 'source-evidence.json': '37b7296d0174033eac886c665716f432c2610f63b18e2d7b386b82738b2c4b0e',
    TRACE / 'source-trace.json': '5c0b6acb8ae642bf50496171c1c80bd46475a464a01d1efba63098f19ed6a1b8',
    TRACE / 'capture-outline.json': 'b26b09ef29ef6b5971f432a9bf06b90e0e9b59a4bb98222cf1ffdacca43456e0',
}
REVIEWED_AT = '2026-10-28T23:08:42Z'
TYPE = 'TRAINING ONLY - Record review 20261028'
CODE = 'TRN-REVIEW-20261028'
AUTHORITY = 'Academy Software Exercise (fictional)'
DESCRIPTION = 'TRAINING ONLY - Software record verification exercise. This is not an actual professional qualification or authorization.'
RECORD = 'TRAINING ONLY - Software record review'
NUMBER = 'DEMO-CASEY-REVIEW-20261028'
AREA = 'Academy training department only'
OFF = 'Off – requirements are informational only'
WARN = 'Warn only – allow role changes, show warnings, notify'
ENFORCE_HELP = 'Enforce removes members from roles whose mandatory certifications lapsed; the removal is audited and the member is notified.'
TYPE_TOP = ['Type', TYPE, 'Code', CODE, 'Category', 'Other', 'Applies to', 'Person',
            'Issuing authority', AUTHORITY, 'Description', DESCRIPTION, 'Default validity (months)', '12', 'Never expires']
TYPE_OPTIONS = ['Credit hours per renewal', 'Requires supervisor verification',
                'New records stay pending until someone with manage rights signs them off.', 'Active', 'Cancel', 'Save']
POLICY = ['Enforcement mode', 'Grace period (days)', '30',
          'Treat records pending verification as valid for role requirements', 'Notifications',
          'Notify (days before expiry)', '60,30,14,7,1', 'Notify the holder directly',
          'Send department administrators a nightly digest']
RECORD_TOP = ['Member', 'Matthew Casey', 'Type', TYPE, 'Name', RECORD, 'Number', NUMBER,
              'Valid Area', AREA, 'Issued by', AUTHORITY, 'Issued on', '10/28/2026', 'Expires on', '10/28/2027']
RECORD_READ = ['Certification record', RECORD, 'Member', 'Matthew Casey', 'Type',
               TYPE + ' (' + CODE + ')', 'Number', NUMBER, 'Issued by', AUTHORITY,
               'Received on', '2026-10-28', 'Expires on', '2027-10-28', 'Edit', 'Renew']

# Only independently legible foreground pixels are promoted. Whole DOMs include
# offscreen rows/options and must not be treated as a visibility oracle.
LABELS = {
 1: ['Certifications', 'Export CSV', 'Add Certification', 'Dashboard', 'Certification types', 'Settings',
     'Compliance report', 'Expired', '0', 'Expiring within 60 days', '1', 'Suspended or revoked',
     'Pending verification', 'Scope', 'People', 'Category', 'All categories', 'Group', 'All groups', 'Role', 'All roles'],
 2: ['Certification record', 'Firefighter qualification', 'Pending verification', 'Member', 'Wallace Boden',
     'Type', 'Firefighter qualification (DEMO-CERT-1)', 'Number', 'DEMO-CERT-1', 'Issued by',
     'Academy Training Board (fictional)', 'Received on', '2026-10-26', 'Expires on', '2028-10-27', 'Edit', 'Renew', 'Add credit'],
 3: ['Certification settings', OFF] + POLICY,
 4: ['Certification settings', WARN] + POLICY,
 5: ['Certification settings', 'Enforce', ENFORCE_HELP] + POLICY,
 6: [OFF] + POLICY + ['Notification settings', 'Save'],
 7: ['Certification types', 'Show inactive', 'Template gallery', 'New type', 'Code', 'Type', 'Category',
     'Applies to', 'Validity', 'Records', 'Requirements', 'Edit', 'DEMO-CERT-3', 'Driver / operator endorsement',
     'DEMO-CERT-1', 'Firefighter qualification', 'DEMO-CERT-2', 'Paramedic qualification', 'Other', 'Person', '24 months', '0', '1', '9', '4'],
 8: ['Template gallery', 'SAR', 'Code', 'Type', 'Category', 'Applies to', 'Validity', 'Issuing authority',
     'SARTECH3', 'SARTECH III', 'Search and rescue', 'Person', 'Never expires', 'NASAR',
     'SARTECH2', 'SARTECH II', 'SARTECH1', 'SARTECH I', '36 months', 'ROPE-TECH', 'Rope Rescue Technician',
     'SWIFTWATER', 'Swiftwater Rescue Technician', 'AVALANCHE', 'Avalanche Rescue', 'K9-TEAM',
     'K9 Search Team Certification', 'HELO-OPS', 'Helicopter Operations', 'Cancel', 'Add selected'],
 9: ['New type', 'Type', 'Code', 'Derived from the name when empty', 'Category', 'Other', 'Applies to',
     'Person', 'Issuing authority', 'Description', 'Default validity (months)', 'Never expires'],
 10: TYPE_TOP + TYPE_OPTIONS,
 11: TYPE_TOP + TYPE_OPTIONS,
 12: ['Certification types', 'Saved.', 'Code', 'Type', 'Category', 'Applies to', 'Validity', 'Records',
      'Requirements', 'Edit', CODE, TYPE, 'Other', 'Person', '12 months', '0'],
 13: ['Certifications', 'Add Certification', 'Export CSV', 'Dashboard', 'Certification types', 'Settings',
      'Compliance report', 'Pending verification', '1', 'Scope', 'People', CODE],
 14: ['Add Certification', 'Member', 'Select a member', 'Type', 'Select a certification type', 'Name',
      'Number', 'Valid Area', 'Issued by', 'Issued on', 'Expires on', 'mm/dd/yyyy'],
 15: ['Add Certification', 'Member', 'Matthew Casey', 'Type', TYPE, 'Name', 'Number', 'Valid Area',
      'Issued by', 'Issued on', 'Expires on', 'mm/dd/yyyy'],
 16: RECORD_TOP + ['File', 'Choose File', 'No file chosen', 'PDF, image or office document, up to 10 MB.', 'Cancel', 'Save'],
 17: ['Certifications', 'Saved.', 'Pending verification', '2', 'Add Certification', 'Dashboard', CODE],
 18: RECORD_READ + ['Pending verification', 'Verify', 'Continuing-education credits', 'Add credit',
       '0 hours recorded', 'No credits recorded.'],
 19: RECORD_READ + ['Saved.', 'Active', 'Verified by', 'Wallace Boden', '2026-10-28', 'Suspend', 'Revoke',
       'Mark trainee', 'Continuing-education credits', 'Add credit', '0 hours recorded', 'No credits recorded.'],
 20: RECORD_READ + ['Active', 'Verified by', 'Wallace Boden', '2026-10-28', 'Suspend', 'Revoke',
       'Mark trainee', 'Continuing-education credits', 'Add credit', '0 hours recorded', 'No credits recorded.'],
 21: ['Matthew Casey', 'Add record', 'Dashboard', 'Certification types', 'Settings', 'Compliance report',
      'Name', 'Type', 'Expires on', 'Status', 'Firefighter qualification', 'Training', '2027-10-25',
      'Active', RECORD, TYPE, '2027-10-28', 'Edit'],
 22: ['Certification types', 'Settings', 'Compliance report', 'Code', 'Type', 'Category', 'Applies to',
      'Validity', 'Records', 'Requirements', CODE, TYPE, 'Other', 'Person', '12 months', '1', '0', 'Edit'],
 23: ['Edit type'] + TYPE_TOP,
 24: ['Edit type'] + TYPE_TOP + TYPE_OPTIONS,
 26: ['Certification settings', OFF] + POLICY,
 27: ['Compliance report', 'Firehouse 51 — Training Department', 'Run on 2026-10-28 17:59',
      'Expiring within 60 days: 1', 'Expired: 0', 'People', 'Member', 'DEMO-CERT-3', 'DEMO-CERT-1',
      'DEMO-CERT-2', CODE, 'Matthew Casey', '2027-10-25', '2027-10-28', 'Active'],
 28: ['Certifications', 'Export CSV', 'Add Certification', 'Compliance report', 'Pending verification',
      '1', 'Scope', 'People', 'Category', 'All categories', 'Group', 'Truck 81', 'Role', 'All roles',
      'Member', CODE, 'Blake Gallo', 'Brian Zvonecek', 'Matthew Casey', 'Randy McHolland',
      'Stella Kidd', '2027-10-28', 'Valid', 'Expiring soon', 'Expired, suspended or revoked'],
}
EXCLUDED = {25: 'Wrong foreground for intended report capture: JPEG shows the earlier Edit type page. The retained full DOM and provenance also describe Edit type. Raw state text claiming a report DOM is not corroborated by this held row. Use027 actual report only; preserve025 unchanged.'}
LIMITS = {
 1: 'Department counter cards and filter controls only. Lower dashboard rows are clipped; no whole-person matrix or specific lower-row navigation proof.',
 2: 'Existing holder Boden Pending record is read only. Verify is absent as expected for self-verification; no attempt, renewal or credit was performed in this administration exercise.',
 3: 'Current Off policy and readable settings only. Save is offscreen; no settings save or notification delivery.',
 4: 'Warn only selected for inspection but UNSAVED. No role change, worker evaluation, notice or delivery executed.',
 5: 'Enforce selector text is horizontally truncated; retain only literal Enforce prefix and fully legible warning/help. Unsaved; no role removal or enforcement outcome.',
 6: 'Off restored; notification values and Save are fully visible, but Save was not pressed. This is policy inspection, not a policy change or delivery test.',
 7: 'Actual baseline three Person types and counts. No edits/deletes of those original types.',
 8: 'Foreground gallery/filter SAR and unselected checkboxes only. Dim background catalog is excluded. Cancel inspection; no Add selected or template application.',
 9: 'Blank upper type fields only. Lower verification label is clipped; Active/Save are offscreen. Use011 for all options and Save.',
 10: 'Prepared own type; no stored proof until012. Do not infer actual issued-record dates from Default validity.',
 11: 'Complete prepared own Person type, options and Save;012 proves save. Verification ON, Never expires OFF, credit hours blank, Active ON.',
 12: 'Saved own new type with zero Records and zero Requirements. No role requirement was added.',
 13: 'Actual Dashboard Add Certification launcher. Casey row/record selection is not pictured in this viewport.',
 14: 'Blank upper Add fields only. File/Save are clipped or offscreen; use016. No hidden member list promoted.',
 15: 'Selected Casey/type but issued/expiry fields remain blank. No type-default expiry autofill was observed.',
 16: 'Complete prepared new record with explicit dates and empty optional file chooser; no uploaded document. Save is pictured;017/018 prove stored Pending state.',
 17: 'Saved dashboard and department-global Pending counter2 only. Casey row is offscreen. Do not invent a click on a hidden Casey cell.',
 18: 'Actual other-member Pending record and normal Verify button. No self-verification; no verification dialog or native confirmation is claimed.',
 19: 'Actual result Active and Verified by Boden, date2026-10-28 only. No hidden time, qualification award, worker or provider result.',
 20: 'Fresh normal record readback retains Active and Verified by Boden. No status/renewal/credit action was used.',
 21: 'Casey holdings show existing original record plus new training record. No new assignment or role qualification is inferred.',
 22: 'New type now has one Record and zero Requirements. Edit/Settings launchers are readable. No requirement editor or role change was executed.',
 23: 'Upper saved type readback: Applies to Person is disabled; Code is still editable with zero role requirements. Lower options/Save are offscreen; use024. No changes submitted.',
 24: 'Saved type options preserved after record creation. No type update performed. Code-lock rule is source-corroborated; no code-edit experiment.',
 26: 'Fresh settings remain Off/grace30/pending-invalid/leads60,30,14,7,1/both notices checked. Save is offscreen; no policy mutation. Off is role enforcement only, not a global notification switch.',
 27: 'Real HTML report foreground; Casey row readable. Boden row is clipped and excluded. No Unit section, PDF generation, CSV download, scheduled report or delivery proof.',
 28: 'Truck81 filter shows five rows and Casey expiry2027-10-28. Pending1 card is department-global, not a filtered-row count. Export CSV is available but not downloaded.',
}

# Each paragraph is an unvoiced candidate. All routes and pictures are actual;
# repetitions deliberately put the navigation control before the result.
SCENES = [
 ('overview', 'Separate records, review and self-verification', [1, 2], ['Certifications', 'Pending verification', 'Wallace Boden', 'Edit', 'Renew'],
  'Certifications brings together the types your department tracks and the records held by people or units. In this fictional Chicago Fire department, the dashboard starts with one record pending verification. Boden can inspect his own pending record, but this page offers no Verify button. Record holders cannot verify their own records. We will create a clearly marked software exercise for another member, then use the normal administrative review path. Use the viewing, management, and setup permissions your department has assigned.',
  'Identify the pending count, then compare the holder of a record with the signed-in reviewer.'),
 ('catalog', 'Inspect types and the template gallery', [1, 7, 8], ['Certification types', 'Template gallery', 'SAR', 'Code', 'Applies to', 'Validity', 'Records', 'Requirements', 'Cancel'],
  'Choose Certification types. The table separates each stable code, category, scope, validity, record count, and requirement count. Template gallery opens a separate selection window. Enter SAR in its filter to inspect relevant starter entries. Their displayed names, authorities, and validity periods are catalog starting points that your department must review. Keep every checkbox clear and use Cancel; nothing is added. We will create our own fictional Person type so the software exercise is distinct from the existing types.',
  'Filter the gallery without selecting or adding a template, then return to the catalog.'),
 ('type-identity', 'Give the exercise its own type and code', [7, 9, 10], ['New type', 'Type', TYPE, 'Code', CODE, 'Category', 'Other', 'Applies to', 'Person', 'Issuing authority', 'Description'],
  'Choose New type. Enter Training Only, Record Review, followed by the exercise date, as the Type. Give it the explicit code TRN-REVIEW-20261028. A stable, recognizable code helps distinguish this type later in tables and integrations. Keep Category as Other and Applies to as Person. Enter Academy Software Exercise, marked fictional, as the Issuing authority. The Description explicitly identifies a software verification exercise and says that it is not a professional qualification or authorization.',
  'Prepare a unique fictional type name, code, issuer, and purpose before saving.'),
 ('type-options', 'Save the verification rule and read back the type', [11, 12], ['Default validity (months)', '12', 'Never expires', 'Credit hours per renewal', 'Requires supervisor verification', 'Active', 'Save', 'Saved.', CODE, 'Records', 'Requirements', '0'],
  'Set Default validity to twelve months and leave Never expires clear. Credit hours per renewal stays blank. Check Requires supervisor verification and keep Active checked. The help explains that new records remain pending until someone with management rights signs them off. Use Save, then read the returned catalog row. Our code is present, its scope is Person, and its validity is twelve months. Both Records and Requirements are zero: creating this type has not created a member record or attached a role requirement.',
  'Save only your own exercise type and verify its code, twelve-month validity, and zero counts.'),
 ('member', 'Start an administrative record for Casey', [13, 14, 15], ['Add Certification', 'Member', 'Matthew Casey', 'Type', TYPE, 'Issued on', 'Expires on', 'mm/dd/yyyy'],
  'On the dashboard, choose Add Certification. This administrative form has an explicit Member selector. Choose Matthew Casey, then select the new training type. Check the selected member and type together before entering identifying information. Notice that Issued on and Expires on are still blank after selecting the type. The type’s twelve-month setting has not filled these fields on this form. We will enter the intended exercise dates explicitly rather than assume that a date was calculated.',
  'Select the intended fictional member and new type, then inspect both date fields.'),
 ('record-save', 'Enter explicit identity and dates, then save', [16, 17], ['Name', RECORD, 'Number', NUMBER, 'Valid Area', AREA, 'Issued by', AUTHORITY, '10/28/2026', '10/28/2027', 'File', 'Save', 'Saved.', 'Pending verification', '2'],
  'Use Training Only, Software Record Review as the Name and the DEMO-CASEY-REVIEW number shown here. Valid Area says Academy training department only, and Issued by repeats our fictional software issuer. Enter October twenty-eighth, twenty twenty-six as the issue date and October twenty-eighth, twenty twenty-seven as the expiry. File is optional and remains empty. Save once. The returned dashboard reports Saved and now has two pending records. Saving the record did not automatically complete its required verification.',
  'Save the explicit dates and exercise number, then check the returned pending count.'),
 ('verify', 'Verify another member and confirm persistence', [18, 19, 20], ['Pending verification', 'Matthew Casey', RECORD, 'Verify', 'Active', 'Verified by', 'Wallace Boden', '2026-10-28'],
  'Here is Casey’s saved record. Read its member, type, number, and expiry before using Verify. This button submits the review directly. The returned record is Active and shows Verified by Wallace Boden with the displayed date. Open the record again and check that the same status and reviewer remain. This confirms the stored software review. It does not establish that a real qualification was earned. We leave renewal, credits, suspension, and revocation unchanged throughout this exercise.',
  'Review your own fictional record for another member, then confirm the stored reviewer and status.'),
 ('holdings', 'Compare the person’s existing and new records', [20, 21], ['Matthew Casey', 'Name', 'Type', 'Expires on', 'Status', 'Firefighter qualification', RECORD, '2027-10-28', 'Active'],
  'Use Matthew Casey’s member link to open his holdings. The table lists each record separately with its name, type, expiry, and status. The existing Firefighter qualification remains, and the new training review appears on another row with its own date and Active status. Compare the exact record name and type before opening or editing anything. This person view helps you distinguish a newly added exercise record from an older record that should remain untouched.',
  'Find both rows and identify the new exercise without changing the original record.'),
 ('type-readback', 'Check counts and the locked scope', [21, 22, 23, 24], ['Certification types', CODE, 'Records', '1', 'Requirements', '0', 'Edit', 'Applies to', 'Person', 'Code', 'Requires supervisor verification'],
  'Return through Certification types. Our row now has one Record and still has zero Requirements. Use that row’s Edit control to inspect the saved type. Applies to is disabled at Person because a record now references it. Code remains editable here; code locking applies when role requirements reference the type. The lower options still show twelve months, verification required, and Active checked. This is a readback only. We do not change the code, add a role requirement, or save another type update.',
  'Read the one-record, zero-requirement counts and inspect the stored type without editing it.'),
 ('policy', 'Distinguish role enforcement from notifications', [22, 3, 4, 5, 6, 26], ['Settings', 'Enforcement mode', OFF, WARN, 'Enforce', ENFORCE_HELP, 'Grace period (days)', '30', 'Notify (days before expiry)', '60,30,14,7,1', 'Notify the holder directly', 'Send department administrators a nightly digest', 'Save'],
  'Settings separates role enforcement from expiry notifications. The saved mode is Off, with thirty days of grace and pending records not treated as valid for role requirements. Warn only permits role changes with warnings; Enforce can block unqualified role additions and remove members after grace. We inspect these choices, restore Off, and leave Save untouched. Off does not disable expiry processing or notifications. The holder and administrator-digest options remain checked, with lead days of sixty, thirty, fourteen, seven, and one. These settings do not prove message delivery.',
  'Read the current role and notification policies, leaving every saved setting unchanged.'),
 ('report', 'Filter the dashboard and read the actual report', [28, 27], ['Group', 'Truck 81', 'Matthew Casey', CODE, '2027-10-28', 'Pending verification', '1', 'Export CSV', 'Compliance report', 'Active'],
  'On the dashboard, Group is filtered to Truck 81. Five member rows appear, including Casey’s new expiry under the training code. The Pending verification card still describes the department, not just these filtered rows. Export CSV is available for the current filters; no file is downloaded here. Choose Compliance report to open the HTML report. In Casey’s row, the training column shows the same expiry and Active status. Read that actual row rather than infer a status from a color or a total.',
  'Compare Casey’s filtered expiry with the training column in the HTML report.'),
 ('adapt', 'Use a clear review process across sectors', [20, 28], ['Matthew Casey', 'Active', 'Verified by', CODE, '2027-10-28'],
  'Chicago Fire can use this pattern to organize a clearly identified exercise record. Community care and mental health teams can track operational training without patient detail. Search and rescue can distinguish person records from equipment records; security teams can organize reviewed staff records; wildland teams can keep seasonal training references current; and industrial response teams can separate staff records from unit inspections. In every setting, define the type, enter deliberate dates, use an authorized reviewer, and verify saved status. A software label alone does not authorize real duties.',
  'Define one appropriate fictional type and identify who should review it in your team.'),
]

GAPS = [
 'No role-requirement create/edit/save, AnyOf grouping, advisory/mandatory execution, grace expiry, role add/block/removal, worker run or notification delivery was demonstrated.',
 'No Unit certification record, template application, record attachment, renewal, continuing-education addition, suspend/revoke/trainee action or delete was performed.',
 'Export CSV control and filtered href are visible; no downloaded CSV bytes were inspected. HTML report is real; no PDF/print/scheduled report/delivery was demonstrated.',
 'Own Boden Pending record is a pre-existing Responder renewal and remains unchanged. Casey was not self-verified. Verification date is readable; no hidden timestamp is claimed.',
 '025 foreground/metadata mismatch is rejected.027 supersedes it only for the actual HTML report. Boden report row is clipped; do not claim it is readable.',
 '005 Enforce option is truncated; only its literal prefix and visible warning are retained. Policy explanations are source-corroborated implications, not executed outcomes.003/026 Save is offscreen;006 shows Save but no save occurred.',
 'Raw DOMs contain offscreen rows and unselected options. Reviewed labels are actual visible foreground pixels only; no hidden control geometry is promoted.',
]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()

def prepare(sources=SOURCES, core_source=CORE):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions, visible_controls_digest
    for rel, digest in PINS.items():
        assert sha(sources / rel) == digest, 'Changed retained input: ' + str(rel)
    source = json.loads((sources / TRACE / 'source-evidence.json').read_text())
    trace = json.loads((sources / TRACE / 'source-trace.json').read_text())
    for entry in source['files']:
        assert sha(core_source / entry['path']) == entry['sha256'], entry['path']
    profile = source['expansion_profile_manifest']
    assert sha(sources / profile['file']) == profile['sha256']
    raw = json.loads((sources / RAW).read_text())
    assert len(raw) == 28 and [int(r['id'][:3]) for r in raw] == list(range(1, 29))
    reviewed, rejected = [], []
    for n, row in enumerate(raw, 1):
        assert sha(sources / row['file']) == row['sha256'], row['id']
        assert sha(sources / row['dom_file']) == row['dom_sha256'], row['id']
        assert _image_dimensions(sources / row['file']) == (1434, 773)
        out = copy.deepcopy(row)
        labels = list(dict.fromkeys(LABELS.get(n, [])))
        out.update(visible_labels=labels, required_labels=labels, visible_controls=[], visible_field_text=[],
            missing_required_labels=[], eligible_for_lesson=n not in EXCLUDED, source_only=True,
            visual_review='actual_original_size_pixels_and_full_DOM_reviewed',
            label_observation_method='Every original1434x773 JPEG was individually viewed. Readable foreground literals only; all28 fullDOM files read/hashed/scanned. Generic clipping false-negatives corrected only in this new metadata; raw image/DOM/manifests unchanged.',
            scope_limit=LIMITS.get(n, EXCLUDED.get(n)),
            url=row['provenance']['url'], captured_at=row['provenance']['captured_at'])
        out['capture_review'] = dict(passed=n not in EXCLUDED, reviewer='Codex independent original-size stored-image/full-DOM review',
            reviewed_at=REVIEWED_AT, sha256=row['sha256'], controls_sha256=visible_controls_digest([]),
            application_visible=True, no_errors=n not in EXCLUDED, controls_reviewed=True,
            controls_fully_visible=n not in EXCLUDED, controls_unobstructed=n not in EXCLUDED,
            method='Manual original-size foreground pixel review, corroborated by retained complete DOM. Fully-visible scope applies only to the manually retained labels, not the entire page or raw metadata.')
        if n in EXCLUDED:
            out['exclusion_reason'] = EXCLUDED[n]
            rejected.append(out)
        else:
            reviewed.append(out)
    captures = dict(app='Core', kind='bounded_reviewed_certification_administration_sources',
        source_manifest=RAW.as_posix(), source_manifest_sha256=PINS[RAW], screenshots=reviewed,
        rejected_sources=rejected, source_only=True, export_ready=False, publication_approved=False)
    by_number = {int(r['id'][:3]):r for r in reviewed}
    sectors = {
      'Chicago Fire':'Separate a fictional exercise record from existing department records and use a non-holder reviewer.',
      'Community care and mental health':'Track operational training references without patient detail or clinical-authority claims.',
      'Search and rescue':'Distinguish reviewed person records from equipment records; starter templates require department review.',
      'Security':'Organize staff training records and their stored review status without treating a software label as authorization.',
      'Wildland':'Keep seasonal training references and explicit dates current; do not infer readiness from a color alone.',
      'Industrial response':'Keep staff records distinct from unit inspection records, using the appropriate scope and reviewer.'}
    lesson = dict(id=NAME, title='Create certification types and verify another member’s record', app='Core',
        audience=['department administrators', 'certification record reviewers'],
        summary='Create a fictional Person type and record, verify another member, confirm saved holdings and type constraints, inspect unchanged policy, and compare filters with the actual HTML report.',
        prerequisites=['Use a fictional practice department and your existing certification view, management and setup permissions.',
          'Choose another fictional member for review; record holders cannot verify their own records.',
          'Use Reports permission for the separate HTML report. Leave existing role requirements and global policies unchanged.'],
        scenes=[], sector_examples=sectors, source_files=[r['path'] for r in source['files']],
        source_evidence={'file':(TRACE / 'source-evidence.json').as_posix(), 'sha256':PINS[TRACE / 'source-evidence.json'], 'core_head':source['core_head']},
        candidate_only=True, source_review_required=True, bounded_scope_only=True,
        whole_module_operations_complete=False, export_ready=False, publication_approved=False)
    sequence = []
    for slug, title, numbers, labels, narration, practice in SCENES:
        assert set(numbers) <= set(by_number), slug
        union = {label for n in numbers for label in by_number[n]['visible_labels']}
        assert set(labels) <= union, (slug, set(labels)-union)
        refs = [by_number[n]['id'] for n in numbers]
        lesson['scenes'].append(dict(id=slug, title=title, route=by_number[numbers[0]]['url'].split(':18967')[-1],
          capture_refs=refs, capture_intent='Show each named launcher/control before prepared values or actual result; use only the scoped foreground sources in this order.',
          required_labels=labels, narration=narration, practice=practice,
          source_limits=[by_number[n]['scope_limit'] for n in numbers]))
        sequence.append(dict(scene_id=slug, title=title, screens=[dict(capture_id=by_number[n]['id'],
          file=by_number[n]['file'], sha256=by_number[n]['sha256'], required_labels=[x for x in labels if x in by_number[n]['visible_labels']],
          phase=by_number[n]['scope_limit']) for n in numbers], narration=narration,
          timing='untimed source-only candidate; no duration, cut or word-timing estimate'))
    narration = '\n\n'.join(s['narration'] for s in lesson['scenes']) + '\n'
    words = len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b", narration))
    assert 800 <= words <= 1150, words
    assert len(lesson['scenes']) == 12 and len(reviewed) == 27 and len(rejected) == 1
    citations = {key:trace[key] for key in ['permissions', 'normal_review_route', 'catalog', 'admin_add_record', 'role_requirements', 'settings_and_worker', 'csv_pdf']}
    correspondence = dict(kind='source_corroborated_controls_first_correspondence',
      source_trace={'file':(TRACE/'source-trace.json').as_posix(),'sha256':PINS[TRACE/'source-trace.json']},
      cited_source_identity={'file':(TRACE/'source-evidence.json').as_posix(),'sha256':PINS[TRACE/'source-evidence.json']},
      scene_source_topics={'overview':['permissions','normal_review_route'], 'catalog':['catalog'],
       'type-identity':['catalog'], 'type-options':['catalog','admin_add_record'], 'member':['admin_add_record'],
       'record-save':['admin_add_record'], 'verify':['normal_review_route'], 'holdings':['normal_review_route'],
       'type-readback':['catalog'], 'policy':['settings_and_worker','role_requirements'], 'report':['csv_pdf'], 'adapt':['catalog','permissions']},
      explicit_distinctions=['Actual creation/save/verification/readback are shown; worker/enforcement/notification effects are source explanations only.',
        'All role policies remain saved Off; Off does not disable independent expiry/notification processing.',
        'Pending after administrator creation follows the type verification flag; authorization alone is not automatic verification.',
        'Person scope is locked after a record; code is still editable with zero role requirements. Neither was changed.',
        'Default validity12 is a type setting; actual Add dates were explicitly entered, not automatically populated.',
        'Raw025 is rejected even though its state text requests report coverage. Actual027 is the only report source.'],
      citations=citations, limits=GAPS)
    scenario = dict(schema_version=1, id=NAME+'-actual-ui-20261028', mode='Manual normal-UI replay; no automatic writes or executable seed',
      department_id=51, environment='Firehouse 51 — Training Department (fictional)', executed_by_this_helper=False,
      actual_capture_manifest={'file':RAW.as_posix(),'sha256':PINS[RAW]},
      new_person_type={'actual_returned_id':51004,'type':TYPE,'code':CODE,'category':'Other','applies_to':'Person',
        'issuing_authority':AUTHORITY,'description':DESCRIPTION,'default_validity_months':12,'never_expires':False,
        'credit_hours_per_renewal':None,'requires_supervisor_verification':True,'active':True,'role_requirements_added':0},
      new_record={'actual_returned_id':51015,'member':'Matthew Casey','actual_seeded_user_id':'DA25F49E-FEA4-5C8D-82D9-163D7D2023F9',
        'type':TYPE,'name':RECORD,'number':NUMBER,'valid_area':AREA,'issued_by':AUTHORITY,
        'issued_on':'2026-10-28','expires_on':'2027-10-28','file':None,
        'created_status':'Pending verification','verified_status':'Active','verified_by':'Wallace Boden','displayed_verification_date':'2026-10-28'},
      preserved_policy={'enforcement_mode':'Off','grace_period_days':30,'pending_as_valid':False,
        'notify_lead_days':[60,30,14,7,1],'notify_holder':True,'notify_admin_digest':True,'settings_saved':False},
      guards=['Use only the isolated fictional Department51 and ordinary existing assigned permissions; no security/role/identity changes.',
        'Search exact type code and record number first. If present, reopen/read rather than recreate or overwrite. Actual returned IDs are observations, never IDs to fabricate.',
        'For a fresh replay, use a new clearly marked type/code only when absent, and select the actual current fictional member through the normal Member control.',
        'Leave original three types, existing Boden Pending record51001, Casey original51002, other member records, roles, policies, calls and units intact.',
        'Review another member only. No self-verification attempt, forced permission, API call, database write or template application.',
        'Do not add accredited/clinical/professional claims, real certification documents, providers, email tests, scheduled reports or payment data.'],
      replay=[
       {'step':1,'route':'/User/Certifications','action':'Inspect department cards; own Pending record is read only and has no Verify.','sources':[1,2]},
       {'step':2,'route':'/User/Certifications/Types','action':'Certification types → Template gallery → filter SAR; leave all unchecked → Cancel.','sources':[1,7,8]},
       {'step':3,'route':'/User/Certifications/EditType','action':'New type → exact fictional identity/Person/Other/issuer/description →12months/verificationON/ActiveON/creditsblank/NeverOFF → normal Save → verify catalog0Records0Requirements.','sources':[7,9,10,11,12]},
       {'step':4,'route':'/User/Certifications/Add','action':'Dashboard Add Certification → Member Casey/new type → explicit record identity and dates, no file → normal Save → dashboard Pending2.','sources':[13,14,15,16,17]},
       {'step':5,'route':'/User/Certifications/Record/51015','action':'Open actual returned Casey record normally; Pending → read member/number/expiry → normal Verify once → Active/Verified by Boden → fresh normal readback. Do not repeat Verify on an already Active record.','sources':[18,19,20]},
       {'step':6,'route':'/User/Certifications/Person?userId={actualSelectedMemberId}','action':'Member link → two holdings; Certification types →1Record0Requirements → own Edit readback Person disabled/options retained. No edits.','sources':[20,21,22,23,24]},
       {'step':7,'route':'/User/Certifications/Settings','action':'Read current policy. Recorded WarnOnly/Enforce selections were unsaved previews restored Off, with Save untouched. Replay may remain read-only on Off; do not apply policy.','sources':[3,4,5,6,26]},
       {'step':8,'route':'/User/Certifications?scope=person&category=&groupId=51004&roleId=','action':'Select Truck81 through Group → five rows/Casey expiry/globalPending1. Compliance report tab → real HTML CaseyActive; no export download or PDF.','sources':[28,27]}],
      observed_final_state={'own_new_record':'Active/Verified by Boden persisted freshGET', 'type_records':1,'type_role_requirements':0,
        'Casey_existing_record':'Preserved', 'department_pending_count':1, 'filtered_Truck81_rows':5,
        'role_or_global_policy_changes':False,'message_delivery_test':False}, result_boundaries=GAPS)
    review = dict(kind='bounded_certification_administration_source_review', status='Source-only candidate awaiting parent script/copy review; not frozen or voiced',
      reviewed_at=REVIEWED_AT, raw_manifest_sha256=PINS[RAW], original_jpegs_individually_reviewed=28,
      original_dimensions=[1434,773], full_dom_files_read=28, raw_media_dom_hash_matches=56,
      accepted_sources=27, excluded_sources=EXCLUDED, source_file_hashes_verified=len(source['files']),
      pinned_core_head=source['core_head'], binary_build_attestation=False, scenes=12, spoken_words=words,
      six_sector_outro_and_companions=True, controls_first_order=True,
      original_raw_bytes_unchanged=True, policy_preview_not_committed=True,
      source_review_not_video_qualification=True, missing_operations=GAPS,
      raw_bindings=[{k:r[k] for k in ['id','file','sha256','dom_file','dom_sha256']} for r in raw])
    outputs = {
      REVIEW:encoded(captures), BASE/'candidate.json':encoded(lesson), BASE/'captures.reviewed.json':encoded(captures),
      BASE/'screen-sequence.json':encoded(dict(id=NAME,status='untimed source-only candidate',scenes=sequence)),
      BASE/'narration.txt':narration.encode(), BASE/'scenario.json':encoded(scenario),
      BASE/'source-correspondence.json':encoded(correspondence), BASE/'source-review.json':encoded(review),
      BASE/'source-evidence.json':encoded(source),
    }
    outputs[BASE/'source-hashes.json'] = encoded(dict(id=NAME,status='Unvoiced source-only candidate; no freeze or publication',
      inputs=[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      outputs=[{'file':p.as_posix(),'sha256':hashlib.sha256(v).hexdigest()} for p,v in outputs.items()],
      helper={'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},
      historical_source_trace_preserved=True, limits=GAPS))
    return outputs, review

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--core-source',type=Path,default=CORE)
    parser.add_argument('--check',action='store_true',help='Read-only retained input, source pin and candidate verification (default).')
    parser.add_argument('--write-source',action='store_true',help='Write only new named reviewed/candidate source artifacts.')
    args = parser.parse_args()
    outputs, report = prepare(args.sources.resolve(),args.core_source.resolve())
    for rel,payload in outputs.items():
        path=args.sources/rel
        assert not path.exists() or path.read_bytes()==payload, 'Preserve existing candidate; choose a new version: '+str(rel)
    if args.write_source:
        for rel,payload in outputs.items():
            path=args.sources/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():
                path.write_bytes(payload)
    print(json.dumps({'passed':True,'source_only':True,'source_files':report['source_file_hashes_verified'],
      'accepted_sources':report['accepted_sources'],'excluded_sources':len(EXCLUDED), 'scenes':report['scenes'],
      'spoken_words':report['spoken_words'],'outputs':len(outputs),'frozen_or_canonical_or_ready':False}))

if __name__=='__main__':
    main()
