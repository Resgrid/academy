"""Freeze two source-only lessons from personally reviewed real application shots.

No canonical lesson, generated speech, listening approval or publication is
created. Earlier raw captures, including excluded frames, remain unchanged.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
REVIEWED_AT = '2026-11-02T04:23:29+00:00'
CORE = 'core-record-definition-client-surfaces'
IC = 'app-ic-record-create-revise-finalize'
TITLE = 'TRAINING ONLY - IC coordination note'
SUMMARY = 'TRAINING ONLY - IC coordination handover software exercise'
UPDATE = 'TRAINING UPDATE - Handover note reviewed for software practice.'
CONFIG = {
    CORE: {
        'app': 'Core', 'title': 'Offer a department record form in IC',
        'summary': 'Review per-form app availability, prepare IC-only client surfaces, validate and save a draft, then inspect publication impact and the published version.',
        'audience': ['Department administrators', 'Records administrators', 'Department trainers'],
        'prerequisites': ['An authorized Core administrator session with Record Definitions available.',
                          'A separate fictional department-owned draft form. The definition-creation lesson covers creating and cloning forms.'],
        'raw': 'core-ic-record-surface-20261101',
        'raw_sha256': '6f0f83887faaf842e23a2a41b98f4293ce32ee3c22204ce2ba59321e44131970',
        'labels': {
            1: ['Client surfaces', 'Responder', 'Unit', 'IC', 'Dispatch', 'Allow offline', 'Allow attachments'],
            3: [TITLE + ' v1 · Draft', 'Definition created. Edit the schema, validate, then publish.', 'Settings', 'Lifecycle preset', 'QuickEntry'],
            4: ['Client surfaces', 'Responder', 'Unit', 'IC', 'Dispatch', 'Allow offline', 'Allow attachments', 'Summary', 'Notes'],
            5: [TITLE + ' v1 · Draft', 'The definition is valid.'],
            7: ['Validate', 'Save draft', 'Review impact & publish', 'Client capability: records.v1b'],
            8: [TITLE + ' v1 · Draft', 'Draft saved.', 'Review impact & publish'],
            9: ['Publish impact', 'Publishing freezes this version. Existing drafts keep their version until migrated; finalized records never change.',
                'Client readiness', 'App', 'Enabled', 'Client surfaces', 'Client capability', 'Responder', 'Unit', 'IncidentCommand', 'Dispatch',
                'Yes', 'No', 'records.v1b', 'This version is not offered to this app.', 'Clients at records.v1b or later can author this version.', 'Publish', 'Cancel'],
            13: [TITLE + ' v1 · Published', 'Open new draft', 'This version is published and read-only. Open a new draft to make changes.'],
        },
        'excluded': {2: 'Clone preparation is retained for fixture reproducibility; cloning is a prerequisite rather than an operation taught in this focused availability lesson.',
                     6: 'The narrow number-prefix field does not paint its complete value, and the surface row meets the footer. No numbering instruction uses this frame.',
                     10: 'Portrait647x722 publication receipt is not learner footage. Source013 supplies a readable landscape published-version view.'},
        'scenes': [
            ('01', 'Review which apps receive a form', [1], ['Client surfaces', 'Responder', 'IC'],
             'A department record form needs the right app availability before field staff can use it. On its definition page, scroll to Client surfaces. This existing training form has Responder selected and IC clear. Unit and Dispatch are also clear. Read this group of choices for the particular form you intend to offer. A form being available in one application does not tell you which other applications are selected here.',
             'Locate Client surfaces on a department definition and read the pictured Responder and IC choices.'),
            ('02', 'Work in a separate definition draft', [3], [TITLE + ' v1 · Draft', 'QuickEntry'],
             'For the practice change, we use a separate department-owned form called Training Only, IC coordination note. The heading identifies version one as Draft, and the creation notice says to edit the schema, validate, then publish. Lifecycle preset currently shows Quick Entry. Confirm the form name and version state before preparing its app choices. This keeps the availability decision tied to the intended definition version.',
             'Confirm the fictional form name, Draft version and displayed lifecycle before changing its app choices.'),
            ('03', 'Prepare IC-only availability', [4], ['Client surfaces', 'Responder', 'Unit', 'IC', 'Dispatch', 'Allow offline'],
             'In Client surfaces, clear Responder and select IC for this separate practice form. Unit and Dispatch remain clear. The pictured choices now target IC when this version is published. Allow offline is also clear for this exercise. Review the entire group before saving, rather than assuming that selecting one app automatically selects the others. These are prepared draft settings at this stage.',
             'Prepare IC selected and the other three app choices clear on a fictional draft. Read Allow offline without enabling it.'),
            ('04', 'Validate and read the result', [7, 5], ['Validate', 'The definition is valid.'],
             'At the bottom of the definition editor, choose Validate. The returned page displays The definition is valid. Read that result before moving toward publication. Validation is a useful checkpoint for the form definition you are preparing; it does not tell an operator which app choices you intended. Compare the configuration with the requested departmental use as well as checking that validation succeeds.',
             'Find Validate and read its returned validation notice.'),
            ('05', 'Save the intended draft configuration', [7, 8], ['Save draft', 'Draft saved.'],
             'Use Save draft to retain the prepared configuration. The returned page displays Draft saved, while the heading still identifies the version as Draft. Read that state before proceeding. Review impact and publish is the next action for deciding whether this version is ready to be offered. Keeping validation, saving and publication as explicit checkpoints makes it easier to explain where a form is in the setup process.',
             'Use Save draft and confirm the saved notice and Draft heading before opening the impact review.'),
            ('06', 'Compare app enablement with the form surface', [9], ['Client readiness', 'Enabled', 'Client surfaces', 'IncidentCommand', 'records.v1b'],
             'Open Review impact and publish, then inspect Client readiness. The Enabled column and Client surfaces column answer different questions. Here every app is enabled, but only the Incident Command row has Yes under Client surfaces. Responder, Unit and Dispatch say this version is not offered to that app. The IC row says clients at records version one B or later can author this version. Read the complete row, including its capability requirement, before publishing.',
             'Compare Enabled and Client surfaces for IC and one other app, then read the capability message.'),
            ('07', 'Publish the reviewed version', [9, 13], ['Publish', TITLE + ' v1 · Published', 'This version is published and read-only. Open a new draft to make changes.'],
             'The impact page explains that publishing freezes the version. After reviewing the intended form and its app readiness, choose Publish. The resulting definition page identifies version one as Published and displays the published, read-only notice. Verify that returned state before telling staff the setup is complete. The separate IC record walkthrough shows this published form being selected and used in the app.',
             'Read the publication consequence and verify the Published heading and read-only notice in a training environment.'),
            ('08', 'Plan future changes and departmental use', [13], ['Open new draft'],
             'Open new draft is available for the next definition change. Use the version heading to keep published forms and future work clear during administration. The same availability review can support a security handover form, a search-and-rescue coordination note, community paramedicine or mental health team documentation, wildland contractor records, industrial exercise forms, and fire or E M S department records. Choose app availability deliberately for the people who will actually fill out each form.',
             'Locate Open new draft and discuss which authorized app users should receive a fictional form for your department.'),
        ],
    },
    IC: {
        'app': 'IC', 'title': 'IC: create, revise and finalize a department record',
        'summary': 'Choose an offered department form, save and revise a fictional draft, review attestation and finalize it, then verify the numbered result under Recent.',
        'audience': ['Incident commanders', 'Command aides', 'Authorized department record authors'],
        'prerequisites': ['A signed-in IC account authorized to create the offered form.',
                          'A department-owned practice form already published for IC. The Core client-surfaces lesson covers that setup.',
                          'Use fictional practice data in a separate training department.'],
        'raw': 'ic-new-coordination-record-20261101',
        'raw_sha256': 'f361c9472e93368892d181e45f69f6f321b22434a79c1713d2dbcf5225e54b69',
        'labels': {
            1: ['Records', 'DRAFTS', 'RECENT'],
            2: ['New Record', TITLE, 'Academy software exercises'],
            3: [TITLE, 'This form is filled in online only.', 'Details', 'Summary', 'Notes', 'Save and send', 'Cancel'],
            4: [TITLE, 'Summary', SUMMARY, 'Notes', 'Save and send'],
            5: ['D-HGYT8', TITLE, 'DRAFT', 'Summary', SUMMARY, 'Notes', 'Save'],
            6: ['D-HGYT8', TITLE, 'DRAFT', 'Summary', 'Notes', UPDATE, 'Save'],
            8: ['D-HGYT8', TITLE, 'DRAFT', 'Summary', 'Notes', UPDATE, 'Save'],
            9: ['D-HGYT8', 'Notes', 'Save', 'I attest this Record is complete and accurate', 'Finalize'],
            10: ['D-HGYT8', 'Notes', 'I attest this Record is complete and accurate', 'Finalize'],
            11: ['ICNOTE-2026-0001', TITLE, 'FINALIZED', 'Finalized.', 'Summary', 'Notes', 'Back'],
            12: ['Records', 'DRAFTS', 'RECENT', 'ICNOTE-2026-0001', SUMMARY, 'FINALIZED'],
        },
        'excluded': {7: 'Direct reload displayed Offline—showing last synced data and a fallback definition key. This cached view is not server-persistence evidence or learner footage; source008 is the subsequent normal reopening without that notice.'},
        'scenes': [
            ('01', 'Open an offered department form', [1, 2], ['Records', 'New Record', TITLE],
             'Begin in Records in an authorized IC session. The plus button at the lower right opens the form selection screen. On New Record, this department offers Training Only, IC coordination note, in the Academy software exercises category. Choose that named form. Read the available name and category before starting; your own department may offer a different collection of forms for its work.',
             'Use the visible plus button, identify the offered training form and choose it by name.'),
            ('02', 'Read the form and its required field', [3], ['This form is filled in online only.', 'Summary', 'Notes', 'Save and send'],
             'The selected form says This form is filled in online only. In Details, Summary has an asterisk and Notes provides space for the longer explanation. Read those labels before entering information. A clear summary helps another authorized operator recognize the record later, while notes carry the supporting detail. Save and send is the action below the fields for this online example.',
             'Read the online-only message and identify Summary, Notes and Save and send.'),
            ('03', 'Enter fictional details and save a draft', [4, 5], ['Summary', 'Notes', 'Save and send', 'D-HGYT8', 'DRAFT'],
             'Enter a concise Summary and Notes for the software exercise. The example summary begins Training Only and describes an IC coordination handover. Review both fields, then choose Save and send. The returned record page has a draft reference at the top and a Draft tag beneath the form name. Read those together with your saved text. This is the working draft you can review before finalizing.',
             'Save a fictional summary and note, then identify the returned draft reference and Draft tag.'),
            ('04', 'Revise the note and verify the saved text', [6, 8], ['Notes', UPDATE, 'Save', 'DRAFT'],
             'While the record is a draft, update Notes with a clear practice revision. Here the added sentence begins Training Update and says the handover note was reviewed for software practice. Choose Save. The verified draft still shows that update in Notes, retains the original Summary and remains marked Draft. Compare the saved text with the change you intended before moving on to completion.',
             'Append a fictional revision, use Save and verify the retained Summary, updated Notes and Draft state.'),
            ('05', 'Review attestation before finalizing', [9, 10], ['I attest this Record is complete and accurate', 'Finalize'],
             'Read I attest this Record is complete and accurate before selecting its checkbox. Finalize is initially disabled in this example. After reviewing this fictional software record, the author selects the attestation and Finalize becomes available. Treat that as a deliberate completion decision based on the actual record contents. For practice, compare the unchecked and selected states before choosing the final action.',
             'Read the complete attestation and compare the disabled and available Finalize states using accurate fictional practice data.'),
            ('06', 'Finalize and verify the numbered result', [10, 11], ['Finalize', 'ICNOTE-2026-0001', 'FINALIZED'],
             'Choose Finalize for the reviewed practice record. The returned page shows Finalized and the header now reads I C note, twenty twenty-six, zero zero zero one. Its Summary and Notes are displayed read-only, and the draft editing actions are gone. Verify the state and number as the result of completion. The earlier draft reference and the final record number identify different stages of this same example.',
             'Finalize an accurate fictional record and verify its Finalized state, record number and read-only fields.'),
            ('07', 'Find the completed record under Recent', [12], ['Records', 'RECENT', 'ICNOTE-2026-0001', 'FINALIZED'],
             'Use Back to return to Records. Under Recent, find the same record number and the coordination handover summary, with the Finalized tag on the right. An unrelated Work record remains in Drafts above it. Read the section, number, summary and state together when selecting a record; completing one item does not mean that every draft in the workspace has been completed.',
             'Locate the numbered record in Recent and distinguish it from another item in Drafts.'),
            ('08', 'Apply the record workflow to your department', [12], ['RECENT'],
             'This workflow can document a security supervisor handover, a search-and-rescue coordination exercise, a community paramedicine or mental health team handover, wildland contractor coordination, industrial response exercises, or fire and E M S department work. The form fields and responsibilities should match your department. The repeatable pattern is to choose the correct form, review the working draft, verify revisions and confirm the final numbered record.',
             'Describe a fictional departmental example and identify who should author and review its record.'),
        ],
    },
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def prepare(name, write=False):
    from verify_capture_evidence import _image_dimensions
    cfg = CONFIG[name]
    raw_path = S / 'captures/expansion' / cfg['raw'] / 'manifest.json'
    assert sha(raw_path) == cfg['raw_sha256'], 'Changed raw capture package.'
    assert datetime.fromisoformat(REVIEWED_AT) <= datetime.now(timezone.utc)
    raw = json.loads(raw_path.read_text())
    by_number = {int(row['id'][:3]): row for row in raw}
    selected = []
    for number, labels in cfg['labels'].items():
        row = deepcopy(by_number[number])
        assert sha(S / row['file']) == row['sha256']
        actual_dimensions = _image_dimensions(S / row['file'])
        expected_dimensions = {(CORE, 9): (1265, 712), (CORE, 13): (1265, 712)}.get((name, number), (1280, 720))
        assert actual_dimensions == expected_dimensions
        if actual_dimensions != (row['width'], row['height']):
            # The browser returned these JPEG dimensions while its DOM witness
            # reported a1280x720 viewport. Preserve both observations; do not
            # change pixels or declare viewport dimensions as image dimensions.
            row['browser_viewport'] = {'width': row['width'], 'height': row['height']}
            row['width'], row['height'] = actual_dimensions
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[])
        row['capture_review'] = {'reviewer': 'Root', 'passed': True, 'reviewed_at': REVIEWED_AT,
                                'sha256': row['sha256'],
                                'method': 'Root personally displayed the exact stored JPEG with view_image. Only readable unobstructed foreground text is retained. No original pixels were changed.',
                                'notes': 'Generic DOM text from hidden background screens, clipped fields and unshown option values is not accepted as visible evidence. The original raw metadata remains preserved.'}
        text_path = S / 'captures/expansion' / cfg['raw'] / (row['id'] + '.txt')
        row.update(dom_file=text_path.relative_to(S).as_posix(), dom_sha256=sha(text_path))
        selected.append(row)
    scenes = []
    for ident, title, numbers, required, narration, practice in cfg['scenes']:
        assert set(required) <= {label for number in numbers for label in cfg['labels'][number]}, ident
        scenes.append({'id': ident, 'title': title,
                       'route': '/User/RecordDefinitions' if name == CORE else '/records',
                       'capture_intent': 'Use only the ordered corresponding actual application views. Cut to each page or control when its instruction is spoken.',
                       'capture_refs': [by_number[number]['id'] for number in numbers],
                       'required_labels': required, 'narration': narration, 'practice': practice})
    lesson = {'id': name, 'title': cfg['title'], 'app': cfg['app'], 'summary': cfg['summary'],
              'audience': cfg['audience'], 'prerequisites': cfg['prerequisites'], 'scenes': scenes,
              'sector_examples': [{'sector': sector, 'scenario': example} for sector, example in [
                  ('Fire/EMS', 'A command aide practices an authorized department coordination record.'),
                  ('Community response', 'A community paramedicine or mental health team practices a coordination handover form.'),
                  ('Search and rescue', 'A search coordinator practices a mission-support handover record.'),
                  ('Security', 'A supervisor practices a shift or event handover form.'),
                  ('Wildland', 'A contractor practices crew coordination documentation.'),
                  ('Industrial', 'An industrial response team practices exercise documentation.')]],
              'source_files': [], 'candidate_only': True, 'export_ready': False, 'publication_approved': False,
              'scope_limits': ['Source proposal only. Approved generated narration, exact cue mapping, encoded-frame review and real playback checks remain required.',
                               'Fictional software training data; no real operational or clinical event is represented.',
                               'No attachment upload, device permission, offline authoring, external delivery or PDF result is demonstrated.']}
    narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    assert 350 <= len(narration.split()) <= 700
    manifest = {'schema_version': 1, 'id': name,
                'raw_manifest': {'file': raw_path.relative_to(S).as_posix(), 'sha256': sha(raw_path)},
                'screenshots': selected,
                'excluded_sources': [{'id': by_number[number]['id'], 'sha256': by_number[number]['sha256'], 'reason': reason}
                                     for number, reason in cfg['excluded'].items()]}
    audit = {'reviewer': 'Root', 'reviewed_at': REVIEWED_AT, 'lesson_id': name,
             'raw_manifest_sha256': sha(raw_path), 'actual_originals_personally_viewed': list(cfg['labels']),
             'selected_actual_screens': len(selected), 'scenes': len(scenes), 'narration_words': len(narration.split()),
             'script_reviewed_against_actual_views': True, 'source_pixels_changed': False,
             'source_only': True, 'audio_or_final_video_approval_inferred': False,
             'specific_UI_limits': ['The IC plus button is visibly present but has no accessible name; no accessible name is invented for it.',
                                    'Attestation selection and enabled Finalize were separately observed through the live AX state and exact screenshot.'] if name == IC else [
                                    'Numbering and full clone selection names are outside this focused lesson. The narrow prefix field is excluded.',
                                    'The final publication view is the landscape recapture; the portrait receipt remains preserved.']}
    if write:
        dest = S / 'expansion/plans' / (name + '-source-proposal-20261101')
        assert not dest.exists(), 'New-only source proposal.'
        dest.mkdir()
        for filename, payload in [('lesson.candidate.json', encode(lesson)), ('narration.txt', narration.encode()),
                                  ('captures.reviewed.json', encode(manifest)), ('source-review.json', encode(audit))]:
            with (dest / filename).open('xb') as stream:
                stream.write(payload)
    return {'lesson_id': name, 'source_ready': True, 'written': write, 'scenes': len(scenes),
            'actual_screens': len(selected), 'narration_words': len(narration.split()),
            'lesson_sha256': hashlib.sha256(encode(lesson)).hexdigest(), 'finished_video': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=CONFIG)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.lesson, args.write), indent=2))
