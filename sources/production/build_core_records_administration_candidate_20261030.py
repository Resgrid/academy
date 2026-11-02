"""Curate a NEW source-only department record-definition lesson candidate.

Default reads only. --write-candidate preserves all raw/historical bytes and
creates no freeze, narration generation, media, canonical lesson or publication.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-records-administration'
PLAN = Path('expansion/plans/core-records-administration-source-plan-20261029')
PRIOR = Path('expansion/plans/core-records-definition-partial-review-20261029')
OUT = Path('expansion/plans/core-records-administration-source-candidate-20261030')
BINDING_AT = '2026-10-30T06:02:22Z'
BATCHES = {
    'a': ('core-records-administration-20261029', '3c099fd2536762f815db3ad2aa2905e89db5a21a68e24212e1b07121ba01eecd', 16),
    'p': ('core-records-definition-publication-20261029', '44872064a0324c52bbbb2655e57b97c9e2c73d5793eab9427c004018d2b0ff25', 6),
    'u': ('core-custom-definition-use-20261030', 'bb02f3664e46c8909efd6123d9f5085dd483083711ac1c6a1c7e396dfaeff1cd', 22),
}
DEFINITION = 'TRAINING ONLY - Community software exercise'
KEY = 'trn-community-software-20261029'
ATTEST = 'I attest that this record is accurate and complete to the best of my knowledge.'
FIXTURE = Path('demo/fixtures/records/academy-record-exercise.txt')
FIXTURE_SHA = 'dcebe4204625aac14de7720b7e3fda03a3862ee15c3ecbcf2056b58e76c28296'
# Exact images this agent displayed through view_image(original), with no claim
# of 100-percent/manual inspection or a fresh review of the other images.
OWN_VIEWS = {'a003', 'a004', 'a007', 'a008', 'a014', 'a015', 'p003', 'p004',
    'u001', 'u002', 'u003', 'u004', 'u005', 'u006', 'u007', 'u008', 'u009',
    'u010', 'u011', 'u012', 'u013', 'u014', 'u016', 'u019', 'u020', 'u021', 'u022'}
# Literal foreground observations, narrowed separately from the raw collector.
LABELS = {
 'p003': [DEFINITION + ' v1 · Published', 'Version 1 published.', 'This version is published and read-only. Open a new draft to make changes.', 'History', 'Open new draft', 'Settings'],
 'p004': ['History: ' + DEFINITION, 'Version', 'State', 'Lifecycle preset', 'Client capability', 'Published on', 'v1 current', 'Published', 'QuickEntry', 'records.v1b'],
 'u001': ['New Record — ' + DEFINITION, 'v1 · QuickEntry', 'Station / group', 'None', 'Call', 'No call', 'Start', 'End', 'External ID', 'Details', 'Summary', 'Notes'],
 'u002': ['Summary', 'Notes', 'Attachments', 'Choose Files', 'No file chosen', ATTEST, 'Save draft', 'Save and finalize', 'Cancel'],
 'u003': ['Station / group', 'None', 'Call', 'No call', 'Start', 'End', 'External ID', 'Summary', 'Notes', 'Attachments', 'No file chosen', 'Save draft', 'Save and finalize'],
 'u004': [DEFINITION, 'Edit', 'Draft', DEFINITION + ' v1', 'Record #', 'Draft reference', 'D-EKCMS', 'Author', 'Owner', 'Wallace Boden', 'Station / group', 'Command', 'Details', 'Summary', 'Notes', 'Finalize'],
 'u005': ['Summary', 'Notes', 'Attachments', 'No file chosen', 'Save draft', 'Save and finalize', 'Cancel'],
 'u006': [DEFINITION, 'Draft', DEFINITION + ' v1', 'D-EKCMS', 'Draft reference', 'Record #', 'Station / group', 'Command', 'Edit', 'Details', 'Summary', 'Notes'],
 'u007': ['Attachments', 'Choose Files', 'No file chosen', 'File classification', 'Restricted', 'Add attachment'],
 'u008': ['Attachments', 'Choose Files', 'File classification', 'Unrestricted operational content', 'Add attachment'],
 'u009': ['Attachments', 'academy-record-exercise.txt', '242 bytes', 'File classification', 'Restricted', 'Add attachment'],
 'u010': ['Draft', 'D-EKCMS', 'Draft reference', 'Record #', 'Summary', 'Notes', ATTEST, 'Finalize'],
 'u011': ['Finalized', 'TRNADM-2026-0001', 'D-EKCMS', DEFINITION + ' v1', 'Record #', 'Draft reference', 'Station / group', 'Command', 'Amend', 'History', 'Transition', 'By', 'Date', 'View'],
 'u012': ['Attachments', 'academy-record-exercise.txt', '242 bytes', 'History', 'Transition', '1', 'Finalized', 'Wallace Boden', 'By', 'Date', 'View'],
 'u013': ['Complete department record TRNADM-2026-0001 — revision 1', 'Attachments', 'Item 1 / Byte Size', '242', 'Item 1 / Checksum', FIXTURE_SHA, 'Item 1 / Classification', 'Unrestricted', 'Item 1 / Content Type', 'text/plain', 'Item 1 / File Name', 'academy-record-exercise.txt', 'Item 1 / Media Location Retained', 'No', 'Draft Reference', 'D-EKCMS', 'Record Number', 'TRNADM-2026-0001'],
 'u014': ['Draft Reference', 'D-EKCMS', 'Record Number', 'TRNADM-2026-0001', 'Station Group Id', '51002', 'Values', 'Details / Summary', 'Details / Notes'],
 'u016': ['Name', 'Definition', 'Category', 'Owner', 'Published version', 'Draft version', 'Lifecycle preset', 'Client capability', DEFINITION, KEY, 'Department', '1', '-', 'QuickEntry', 'records.v1b', 'Edit', 'History', 'New Record'],
 'u019': ['Require author attestation at finalize', 'Numbering', 'Number prefix', 'Sequence width', '4', 'Assign number', 'OnFinalize', 'Sequence per station', 'Sequence per incident', 'Reset yearly'],
 'u020': ['Numbering', 'Sequence width', '4', 'Assign number', 'OnFinalize', 'Reset yearly', 'Classification', 'Standard', 'Client surfaces', 'Responder', 'Unit', 'IC', 'Dispatch', 'Allow offline', 'Allow attachments', 'Keep photo coordinates on attachments', 'Fields', 'Summary', 'ShortText', 'Yes', 'Notes', 'LongText', 'No'],
 'u021': ['New Record — ' + DEFINITION, 'v1 · QuickEntry', 'Station / group', 'None', 'Call', 'No call', 'Start', 'End', 'External ID', 'Summary', 'Notes'],
 'u022': ['Records', 'Record #', 'Type', 'State', 'Summary', 'TRNADM-2026-0001', DEFINITION, 'Finalized', 'TRN-2026-0002', 'Training', 'Amended', 'D-469KP', 'Work', 'Draft', 'TRN-2026-0001'],
}

# Each paragraph is assembled from exact, untimed source spans. These are only
# proposed narration words: root has not read/approved/frozen them yet.
SCENES = [
 ('entry', 'Start with the definition catalog', [
  ('a001', ['Records', 'Manage', 'Definitions'], 'Department administrators use record definitions to give authors a consistent form and lifecycle. In Records, open Manage and choose Definitions. This example builds a department-owned form for a fictional community coordination exercise.'),
  ('a002', ['Definitions', 'New definition', 'Published version', 'Draft version'], 'The catalog separates published and draft versions. A definition describes the form; an individual record stores one completed entry. Choose New definition for the new exercise, leaving the product-owned forms unchanged.')], 'Distinguish a form definition from one record, then locate the permitted New definition control.'),
 ('blank', 'Create a distinct blank definition', [
  ('a003', ['Create definition', 'Blank definition', 'Definition', 'Name', 'Category'], 'Start from template is set to Blank definition. Give Definition a unique lower-case key, then enter the Name and Category. Here the name is Training Only, Community Software Exercise, and the category is Academy Software Exercises. The key cannot be changed after creation, so review it before choosing Create definition.'),
  ('a009', ['v1', 'Draft', 'Definition created. Edit the schema, validate, then publish.'], 'The returned editor identifies version one as Draft and confirms that the definition was created. It is not yet a published form.')], 'Plan a distinct training key and descriptive category. Inspect this existing example instead of submitting its key again.'),
 ('policy', 'Choose a lifecycle and numbering policy', [
  ('a004', ['Lifecycle preset', 'QuickEntry', 'Records per call', 'Multiple per call', 'Require author attestation at finalize'], 'Lifecycle preset is QuickEntry, supporting a draft followed by finalization. Records per call is Multiple per call. Require author attestation at finalize is checked; reviewer and approver roles are not selected for this example.'),
  ('a008', ['Numbering', 'Number prefix', 'Sequence width', 'Assign number', 'OnFinalize', 'Sequence per station', 'Sequence per incident', 'Reset yearly'], 'Under Numbering, Sequence width is four and Assign number is OnFinalize. Reset yearly is checked, while the station and incident sequence options are off. These choices provide one annual sequence for this definition and issue the number when the record is finalized, rather than when its draft first appears.')], 'Explain why the draft has a reference before it receives a final number; identify the actual sequence options.'),
 ('fields', 'Review fields, classification and client choices', [
  ('a007', ['Classification', 'Standard', 'Client surfaces', 'Responder', 'Unit', 'IC', 'Dispatch', 'Allow offline', 'Allow attachments', 'Keep photo coordinates on attachments'], 'Classification is Standard. In Client surfaces, only Responder is selected. Allow offline is off, Allow attachments is on, and Keep photo coordinates on attachments is off. These settings express this version’s choices; they do not demonstrate a successful field-app submission.'),
  ('a011', ['Fields', 'Summary', 'ShortText', 'Yes', 'Notes', 'LongText', 'No'], 'The Fields table describes the unchanged starter form: Summary is required ShortText, while Notes is optional LongText. A short summary helps identify an entry; longer notes provide its context. Check that table rather than mistaking the nearby JSON example for the saved form.')], 'Read the two field types and required flags, keeping definition classification separate from a later attachment classification.'),
 ('save-definition', 'Keep validation and saving distinct', [
  ('a014', ['Validate', 'Save draft', 'Review impact & publish'], 'At the foot of the reopened draft, Validate, Save draft and Review impact and publish are separate controls. Validate checks the definition without publishing it.'),
  ('a010', ['The definition is valid.', 'Draft'], 'The retained validation result says The definition is valid, while the version remains Draft.'),
  ('a012', ['Draft saved.', 'Draft'], 'The save confirmation says Draft saved. That confirms a definition save, not an individual record entry.'),
  ('a013', ['Numbering', 'Sequence width', 'Assign number', 'OnFinalize', 'Require author attestation at finalize'], 'Freshly reopening the saved version retains its numbering and attestation settings. Keep the validation result, saved configuration and publication state distinct.')], 'Identify the separate control and result for validation, saving and publication; do not resave this published example.'),
 ('impact', 'Review publication impact', [
  ('a015', ['Publish impact', 'Published version', 'Breaking change', 'Client readiness'], 'Review impact and publish opens Publish impact. Before the first publication, Published version is a dash and Breaking change is No. Read the impact before making the version available.'),
  ('a016', ['Client readiness', 'Responder', 'Unit', 'IncidentCommand', 'Dispatch', 'Client surfaces', 'Publish'], 'Client readiness compares app availability, client surfaces and capability. Only Responder is offered this version. Publish is the publication control; the table itself is neither publication confirmation nor a demonstration of using the form in that app.')], 'Compare the client-surface column with the enabled-app column and explain why they answer different questions.'),
 ('published', 'Verify the published version and its settings', [
  ('p003', [DEFINITION + ' v1 · Published', 'This version is published and read-only. Open a new draft to make changes.', 'Open new draft'], 'After the approved publication, the resumed version already shows Published and read-only. Open new draft is available for later changes; another Publish is not needed for this version.'),
  ('p004', ['Version', 'Published', 'Published on', 'QuickEntry'], 'History identifies the current published version and its publication date.'),
  ('u019', ['Require author attestation at finalize', 'Sequence width', 'Assign number', 'OnFinalize'], 'Its saved numbering and author-attestation choices remain visible.'),
  ('u020', ['Classification', 'Standard', 'Client surfaces', 'Responder', 'Fields', 'Summary', 'Notes'], 'The complete settings view also retains Standard, the client and attachment choices, and the Summary and Notes fields. This is the configuration authors will use.')], 'Verify the actual current version and saved choices without opening a new draft or repeating publication.'),
 ('prepare-record', 'Use the actual department form', [
  ('u001', ['New Record — ' + DEFINITION, 'v1 · QuickEntry', 'Summary', 'Notes'], 'The published department form identifies its name and version one, QuickEntry, above Summary and Notes. Confirm that identity before typing; a generic Training form would be a different record type.'),
  ('u002', ['Attachments', 'No file chosen', 'Save draft', 'Save and finalize'], 'The lower form offers Save draft and Save and finalize. We start without a file or attestation.'),
  ('u003', ['Summary', 'Notes', 'Save draft'], 'Enter a distinct exercise Summary and explain its purpose in Notes. Here the text describes software practice and makes no claim of a visit, care, attendance or operational action. Choose Save draft first so the saved entry can be checked before finalization.')], 'Check the form name, required Summary and factual Notes; do not create another copy of the existing example.'),
 ('draft', 'Read the saved draft identity', [
  ('u004', ['Draft', 'D-EKCMS', 'Record #', 'Draft reference', 'Author', 'Owner', 'Station / group', 'Command'], 'The returned record is Draft, with reference D, E, K, C, M, S and no final record number. Author and Owner are Wallace Boden. Station and group resolves to Command, although the new form showed None. Read the saved result rather than assuming that a blank selection remained blank. Keep this reference so later editing and attachment work stay with the same record.')], 'Find the draft reference and returned group, then explain why the empty Record number is expected.'),
 ('edit', 'Edit and reopen the same draft', [
  ('u004', ['Edit', 'D-EKCMS'], 'Use Edit on this draft instead of opening another New Record form.'),
  ('u005', ['Notes', 'Save draft'], 'Update Notes to explain that the summary and public handout were reviewed in the fictional exercise. Read the complete statement in the editor, then use Save draft.'),
  ('u006', ['Draft', 'D-EKCMS', 'Notes'], 'A fresh readback of the same reference contains those revised Notes and remains Draft. The separate readback is the check that the intended text was retained.')], 'Compare the intended Notes with the reopened saved text on the same reference; do not duplicate the record.'),
 ('attachment', 'Add the handout from the saved record', [
  ('u007', ['Attachments', 'Choose Files', 'File classification', 'Add attachment'], 'On the saved record, Attachments provides Choose Files, File classification and Add attachment.'),
  ('u008', ['Choose Files', 'File classification', 'Unrestricted operational content', 'Add attachment'], 'Choose the public software handout and select Unrestricted operational content, then use Add attachment. This choice is for that file; it is separate from the form’s Standard classification.'),
  ('u009', ['academy-record-exercise.txt', '242 bytes', 'Restricted'], 'The fresh list contains academy-record-exercise dot text, two hundred forty-two bytes. The next-upload selector has reset to Restricted. That reset does not describe the file already stored; check its retained metadata in the finalized revision.')], 'Distinguish the prepared chooser, stored filename and next-upload selector; verify only the public exercise file.'),
 ('finalize', 'Attest and verify the issued number', [
  ('u010', [ATTEST, 'Finalize', 'D-EKCMS'], 'Read the saved Summary and Notes before checking the accuracy attestation and choosing Finalize. The statement applies to the entry’s actual contents; it does not turn a software exercise into physical work or attendance.'),
  ('u011', ['Finalized', 'TRNADM-2026-0001', 'D-EKCMS', 'Amend'], 'The fresh result shows Finalized and the issued number T R N A D M, Twenty Twenty-Six, Zero Zero Zero One. The draft reference remains alongside it. Amend is available for a later correction to a finalized record.')], 'Identify the actual issued number and retained draft reference without finalizing again or opening an amendment.'),
 ('revision', 'Inspect the retained revision and attachment', [
  ('u012', ['History', 'Finalized', 'View', 'academy-record-exercise.txt'], 'History now shows revision one, Finalized, with the author and date. The handout remains listed. Use View on that history row.'),
  ('u013', ['Complete department record TRNADM-2026-0001 — revision 1', 'Item 1 / Byte Size', '242', 'Item 1 / Checksum', 'Item 1 / Classification', 'Unrestricted'], 'The resulting HTML revision identifies the same record. Its attachment metadata retains the filename, byte size, checksum and Unrestricted classification. The checksum matches the public handout. This is the stored classification, independent of the reset upload selector.'),
  ('u014', ['Values', 'Details / Summary', 'Details / Notes', 'D-EKCMS', 'TRNADM-2026-0001'], 'Farther down, Values preserves the saved Summary and Notes alongside the draft reference and record number. Review this specific revision when checking what finalization retained.')], 'Compare the saved values and attachment metadata with the intended entry. Do not interpret Scan State3 as a safety certification or claim a PDF export.'),
 ('queue', 'Reconcile the record queue', [
  ('u022', ['Record #', 'Type', 'State', 'Summary', 'TRNADM-2026-0001', 'TRN-2026-0002', 'Amended', 'D-469KP', 'Draft', 'TRN-2026-0001'], 'Back in Records, the new custom row is Finalized. The three earlier records remain present: an Amended Training entry, a Work Draft and the older Finalized Training entry. Read Record number, Type, State and Summary together to choose the intended row. This record-entry sequence created only its own custom entry; finding it again does not require creating a replacement.')], 'Locate all four rows and distinguish the new custom form from the two built-in Training entries and Work draft.'),
 ('launcher', 'Find the right form through its catalog row', [
  ('u016', [DEFINITION, KEY, 'Department', 'Published version', 'Draft version', 'New Record'], 'For later use, return to the definition catalog. The department-owned row shows published version one, no draft version, and its own New Record control. Use that row to select the intended form.'),
  ('u021', ['New Record — ' + DEFINITION, 'v1 · QuickEntry', 'Summary', 'Notes'], 'The actual launcher opens the named version-one form with Summary and Notes. This later check leaves the new form empty.'),
  ('u022', ['TRNADM-2026-0001', 'TRN-2026-0002', 'D-469KP', 'TRN-2026-0001'], 'Returning to the queue still shows four records, with no second custom draft.')], 'Use the correct catalog row for a read-only form check; preserve the existing finalized exercise and all earlier records.'),
 ('sectors', 'Apply the pattern to your department', [
  ('u014', ['Values', 'Details / Summary', 'Details / Notes'], 'Fire and EMS teams can use a small form for exercise briefings. Community-care and mental-health teams can standardize coordination notes with suitable information rules. Search-and-rescue teams can organize mission-preparation summaries. Security teams can structure patrol briefings, wildland coordinators can prepare seasonal orientation forms, and industrial teams can retain system-training notes and a public handout.'),
  ('u022', ['Record #', 'Type', 'State', 'Summary'], 'Across those settings, choose fields, numbering and client access for the task. Test the actual published form, verify the saved draft and attachment, and retain the finalized revision that supports the entry.')], 'Choose one department use and explain which Summary, Notes, numbering and access choices would support it, without claiming an unshown workflow.'),
]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    assert __debug__, 'Use ordinary Python so retained guards remain enabled.'
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions
    from expansion_site import lesson_content_digest
    raw, raw_manifests, input_files = {}, [], {}
    for prefix, (folder, digest, count) in BATCHES.items():
        manifest = Path('captures/expansion') / folder / 'manifest.json'
        assert sha(S / manifest) == digest, 'Changed held raw batch.'
        rows = json.loads((S / manifest).read_text())
        assert len(rows) == count
        raw_manifests.append({'file': manifest.as_posix(), 'sha256': digest, 'rows': count})
        input_files[manifest.as_posix()] = digest
        for row in rows:
            alias = prefix + row['id'][:3]
            assert alias not in raw
            for field, hashfield in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
                assert sha(S / row[field]) == row[hashfield], 'Changed raw image/DOM.'
                input_files[row[field]] = row[hashfield]
            assert _image_dimensions(S / row['file']) == (1280, 720)
            raw[alias] = row
    assert len(raw) == 44
    prior_path = PRIOR / 'captures.reviewed.json'
    prior = json.loads((S / prior_path).read_text())
    assert prior['raw_manifest']['sha256'] == BATCHES['a'][1]
    prior_rows = {'a' + row['id'][:3]: row for row in prior['screenshots']}
    used = {alias for _, _, segments, _ in SCENES for alias, _, _ in segments}
    assert used <= set(raw) and not {'a006', 'p005', 'p006', 'u015', 'u018'} & used
    captures, literal_reviews = [], []
    for alias in sorted(used):
        original = raw[alias]
        row = deepcopy(original)
        if alias.startswith('a'):
            finding = prior_rows[alias]
            assert finding['review_status'] == 'accepted_bounded_source' and finding['visual_review']['completed']
            labels = list(finding['visible_labels'])
            if alias == 'a007':
                # This agent also displayed007: both printed literals are clear
                # above Client surfaces, although omitted by the older subset.
                labels += ['Classification', 'Standard']
            attribution = {'reviewer': 'Codex /root/core_configuration_coverage',
                'reviewed_at': finding['visual_review']['reviewed_at'],
                'method': 'Retained bounded source review copied without a new original-pixel claim.',
                'historical_review': {'file': prior_path.as_posix(), 'sha256': sha(S / prior_path)},
                'limits': finding['limits']}
        else:
            labels = LABELS[alias]
            attribution = {'reviewer': 'Codex /root', 'reviewed_at': BINDING_AT,
                'method': 'Hash binding of direct parent all-image review of these completed raw batches. This time records the binding, not an invented earlier image-view time.',
                'parent_source_review_authority': 'Direct task instruction: parent personally viewed every new actual full image, supplied exclusions and concrete lifecycle observations.',
                'independent_display_review_by': 'Codex /root/dispatch_ic_coverage' if alias in OWN_VIEWS else None,
                'independent_method': 'Exact stored JPEG displayed with view_image(original); no100-percent/manual inspection assertion.' if alias in OWN_VIEWS else None}
        assert row['id'] == (prior_rows[alias]['id'] if alias.startswith('a') else row['id'])
        added = [label for label in labels if label not in original.get('visible_labels', [])]
        row.update(visible_labels=labels, visible_controls=[], visible_field_text=[], required_labels=[],
            missing_required_labels=[], eligible_for_lesson=True,
            capture_review={'passed': True, **attribution, 'sha256': row['sha256']},
            source_review_alias=alias)
        if added:
            assert alias in OWN_VIEWS or alias.startswith('a'), 'No unsupported manual literal supplement.'
            row['supplemental_literal_review'] = {'literal_labels_added': added, 'sha256': row['sha256'],
                'reviewer': 'Codex /root/dispatch_ic_coverage' if alias in OWN_VIEWS else attribution['reviewer'],
                'binding_recorded_at': BINDING_AT,
                'reason': 'Actual printed text/painted values were omitted by raw root-scroll/body clipping or whole-node collection. Only personally displayed or retained reviewed pixel literals are added; no DOM-only hidden option or stale geometry is promoted.'}
        row['source_observation_limits'] = ['Only this narrowed literal set and its cited pixel review may satisfy a later control claim. Raw intent/DOM presence is not eligibility.',
            'All icon-control and field-rectangle metadata removed from the new subset; no pixel or raw sidecar changed.']
        captures.append(row)
        literal_reviews.append({'alias': alias, 'id': row['id'], 'sha256': row['sha256'],
            'literal_labels': labels, 'added_to_raw_literal_list': added,
            'independently_displayed_by_this_agent': alias in OWN_VIEWS})
    by_alias = {row['source_review_alias']: row for row in captures}
    scenes, sequence = [], []
    for ident, title, segments, practice in SCENES:
        screens, required = [], []
        for alias, labels, words in segments:
            row = by_alias[alias]
            assert set(labels) <= set(row['visible_labels']), (alias, set(labels) - set(row['visible_labels']))
            for label in labels:
                if label not in required:
                    required.append(label)
            screens.append({'capture_id': row['id'], 'source_alias': alias, 'file': row['file'], 'sha256': row['sha256'],
                'required_labels': labels, 'narration_span': words, 'timing': None})
        narration = ' '.join(words for _, _, words in segments)
        scene = {'id': ident, 'title': title, 'route': raw[segments[0][0]]['provenance']['url'].split(':18967')[-1],
            'capture_intent': 'Use the exact actual foreground source order and declared chronology limits.',
            'required_labels': required, 'narration': narration, 'practice': practice,
            'capture_evidence': {'status': 'candidate_actual_sources_parent_full_script_review_pending',
                'capture_refs': [screen['capture_id'] for screen in screens]}}
        scenes.append(scene)
        sequence.append({'scene_id': ident, 'title': title, 'narration': narration, 'screens': screens})
    narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    assert 1000 <= len(narration.split()) <= 1300, len(narration.split())
    assert len(scenes) == 16
    source_evidence = json.loads((S / PLAN / 'source-evidence.json').read_text())
    assert len(source_evidence['files']) == 35
    assets, snapshots = {}, []
    for row in source_evidence['files']:
        path = S / row['snapshot_file']
        assert sha(path) == row['sha256'], 'Changed retained source snapshot.'
        target = 'source/' + row['repo'] + '/' + row['path']
        assets[target] = path.read_bytes()
        snapshots.append({'repository': row['repo'], 'repository_path': row['path'], 'sha256': row['sha256'],
            'file': (OUT / target).as_posix(), 'retained_source_profile_not_runtime_attestation': True})
    assert sha(S / FIXTURE) == FIXTURE_SHA and (S / FIXTURE).stat().st_size == 242
    assets['fixture/academy-record-exercise.txt'] = (S / FIXTURE).read_bytes()
    examples = [
        {'sector': 'Fire / EMS', 'scenario': 'Use Summary, Notes and a public exercise handout for a fictional briefing, with a distinct definition number sequence.'},
        {'sector': 'Community response', 'scenario': 'Plan a coordination form with appropriate information rules and deliberate client access; this example carries no client history or clinical determination.'},
        {'sector': 'Search and rescue', 'scenario': 'Structure mission-preparation summaries and preserve the finalized version actually reviewed, without claiming a mission response.'},
        {'sector': 'Security', 'scenario': 'Organize a patrol briefing form with clear summary and notes; select the correct department definition rather than a similarly named system form.'},
        {'sector': 'Wildland', 'scenario': 'Use a seasonal orientation form with an annual numbering policy and verify the published fields before authors use it.'},
        {'sector': 'Industrial', 'scenario': 'Retain system-training notes and a public handout with verified attachment classification; do not treat the record as a physical inspection certificate.'},
    ]
    lesson = {'id': NAME, 'title': 'Create a department record definition and use its published form', 'app': 'Core',
        'audience': 'Department administrators and authorized record authors',
        'summary': 'Configure a simple department-owned definition, distinguish validation/save/publication, and follow one custom record through draft, attachment and final revision.',
        'prerequisites': ['An authorized Core session with Records already usable and existing rights to manage/publish definitions and author/finalize records.',
            'A fictional practice department and a new unused definition key for any separate replay; this existing published example and finalized record must not be submitted again.',
            'Only the public242-byte software handout is used. No activation, security/role changes, import or production records are required.'],
        'scenes': scenes, 'sector_examples': examples,
        'source_files': [row['file'] for row in snapshots if row['repository'] == 'Core'],
        'candidate_only': True, 'narration_frozen': False, 'parent_full_script_review_pending': True,
        'export_ready': False, 'publication_approved': False,
        'scope_limits': ['Core browser definition administration and one QuickEntry record lifecycle only.',
            'The approved v1 was already Published on resume; no repeated Publish action or native confirmation pixels are claimed.',
            'Client flags/compatibility do not establish Responder, Unit, IC or Dispatch record save/content display; known field-app failures remain separate.',
            'HTML revision rendering is not a PDF export; Scan State3 is not interpreted as malware clearance. No photo GPS/metadata-stripping, external delivery or attendance outcome.',
            'No template application, JSON schema customization, new version, migration, review/approval assignment, amend/void/reassignment or counter reset is demonstrated.']}
    excluded = []
    reasons = {'a005': 'Redundant prepared view; full prefix is clipped. Better numbering and complete classification/field images are selected.',
        'a006': 'Prior review excluded poor framing: client controls/action buttons clipped.',
        'p001': 'Historical retained pre-publication readback; not needed beyond earlier configuration sources.',
        'p002': 'Duplicate impact view; earlier actual impact/readiness sources retained.',
        'p005': 'Custom type option is DOM-only, not painted. Cannot establish visible filter selection.',
        'p006': 'Selected custom option still leaves built-in Training/Course form. Not successful custom rendering.',
        'u015': 'Bottom existing TRN-2026-0001 row clipped;022 supplies all four complete rows.',
        'u017': 'Redundant read-only published header; publication003 supplies the state.',
        'u018': 'Misleading framing after scrolling inside Schema JSON; not accepted settings/client proof.'}
    for alias in sorted(set(raw) - used):
        assert alias in reasons, 'Undocumented omitted source: ' + alias
        excluded.append({'alias': alias, 'id': raw[alias]['id'], 'sha256': raw[alias]['sha256'], 'reason': reasons[alias]})
    operation_log = {'kind': 'source_only_reconciled_actual_UI_operation_log', 'department_id': 51,
        'definition_key': KEY, 'version': 1, 'actual_record_id': 'ba3dbedd-c693-4937-b892-5679c41761c5',
        'draft_reference': 'D-EKCMS', 'issued_record_number': 'TRNADM-2026-0001', 'revision': 1,
        'statement_scope': 'Actual parent-recorded UI outcomes and retained images only; this agent made no app request or mutation. Screenshot timestamps are not asserted as click timestamps.',
        'operations': [
            {'phase': 'Definition configuration', 'source_aliases': ['a003', 'a004', 'a007', 'a008', 'a009', 'a010', 'a012', 'a013', 'a014'], 'result': 'Own v1 created, validated, saved and freshly reopened as a definition Draft.014 is a reopened control view, not the missing original pre-first-Save screenshot.'},
            {'phase': 'Impact/publication', 'source_aliases': ['a015', 'a016', 'p003', 'p004'], 'result': 'Human approved localv1 publication. On resume v1 already Published/read-only; no repeat Publish submitted or native confirmation invented.'},
            {'phase': 'Create one record', 'source_aliases': ['u001', 'u002', 'u003', 'u004'], 'result': 'Actual custom Summary/Notes form; one Save draft returns own ID/D-EKCMS with Command fallback and no final number.'},
            {'phase': 'Edit same record', 'source_aliases': ['u005', 'u006'], 'result': 'Explicit Save draft followed by fresh same-ID revised Notes; no duplicate creation.'},
            {'phase': 'Attach public fixture', 'source_aliases': ['u007', 'u008', 'u009'], 'result': 'Details Add attachment with Unrestricted operational content; fresh stored242-byte file. Reset Restricted chooser does not reclassify stored upload.'},
            {'phase': 'Finalize own accurate entry', 'source_aliases': ['u010', 'u011', 'u012', 'u013', 'u014'], 'result': 'Ordinary attestation/Finalize; fresh Finalized TRNADM-2026-0001, same draft reference and revision1, retained Unrestricted fixture/checksum and saved Values.'},
            {'phase': 'Catalog verification and queue', 'source_aliases': ['u016', 'u021', 'u022'], 'result': 'Later real catalog-row New Record opens correct empty form, then cancelled with no second Draft. All four current rows present, prior3 unchanged during custom-record sequence.'}],
        'source_only_no_new_execution': True}
    old_replay = json.loads((S / PLAN / 'scenario.replay.json').read_text())
    replay_delta = {'kind': 'manual_replay_delta_from_source_plan_no_execution',
        'base_file': (PLAN / 'scenario.replay.json').as_posix(), 'base_sha256': sha(S / PLAN / 'scenario.replay.json'),
        'preserved_definition_choices': old_replay['new_definition'],
        'actual_example': {'definition_key': KEY, 'version': 1, 'state': 'Published/read-only',
            'record_id': operation_log['actual_record_id'], 'draft_reference': 'D-EKCMS', 'state_of_record': 'Finalized', 'number': 'TRNADM-2026-0001'},
        'necessary_deltas': ['Existing published key is already complete: inspect, do not overwrite, republish or submit another identical record.',
            'Use actual returned IDs, draft references, row versions and issued numbers on a separately authorized replay; never force the captured GUID/D-EKCMS/TRNADM number.',
            'New form Station/group None resolved to Command in saved Details; do not claim persisted blank group.',
            'Use catalog-row New Record and confirm the custom title/Summary/Notes. The old dropdown-only Training fallback frames are excluded.',
            'No files on initial create/edit. Upload only from saved Details with the correctly displayed Unrestricted operational content choice.',
            'Stop on normal permissions/protection/validation refusal; inspect an existing returned record before retrying any create.',
            'The later empty launcher check was cancelled and did not create another Draft. Original3 records remain untouched.',
            'Field-app catalog/form appearances or known failures cannot be promoted to successful saves/content display. No client/runtime patch or API bypass belongs to this lesson.'],
        'fixture': {'file': (OUT / 'fixture/academy-record-exercise.txt').as_posix(), 'sha256': FIXTURE_SHA, 'bytes': 242},
        'automatic_replay_or_DB_seed': False}
    audit = {'kind': 'bounded_Records_administration_actual_source_candidate_review', 'binding_recorded_at': BINDING_AT,
        'raw_manifests': raw_manifests, 'raw_pairs_unchanged': 44,
        'accepted_images': len(captures), 'excluded_images': excluded,
        'literal_observations': literal_reviews, 'independently_displayed_key_images_by_this_agent': sorted(OWN_VIEWS),
        'independent_display_count': len(OWN_VIEWS),
        'review_attribution': 'Existing owner16-original review retained for old configuration images. Direct root all-new-image review retained for publication/use batches. This agent independently displayed the exact27listed keyJPEGs; other accepted images rely on those explicit retained reviews. No100-percent inspection or new review of unviewed images claimed.',
        'chronology_limits': ['Old014 is the freshly reopened definition controls, not the missing original first pre-Save framing.',
            'Published resumed state is actual; no captured native publication-confirmation sequence is inferred.',
            'Later settings/catalog/empty-launcher checks follow the record lifecycle. Their teaching placement verifies the same unchanged published version, not a fabricated earlier click.',
            'New019 supports numbering/attestation only; full classification/client/Fields use020. Prefix input is clipped; full TRNADM is claimed only with actual issued number.'],
        'privacy_pixel_findings': [], 'privacy_pixel_scope': '27exact displayed key images plus retained explicit root/owner reviews; fictional seeded names/record IDs and public software text only. No credentials/editor exports or clinical/client histories identified. Application author UUIDs in revision metadata are seeded record metadata, not authentication credentials.',
        'parent_full_script_review_pending': True, 'narration_frozen': False}
    for name in ['source-evidence.json', 'source-trace.json', 'scenario.replay.json', 'capture-outline.json']:
        assets['historical-source-plan/' + name] = (S / PLAN / name).read_bytes()
        input_files[(PLAN / name).as_posix()] = sha(S / PLAN / name)
    assets['historical-source-plan/prior-captures.reviewed.json'] = (S / prior_path).read_bytes()
    assets['historical-source-plan/prior-actual-operation-log.partial.json'] = (S / PRIOR / 'actual-operation-log.partial.json').read_bytes()
    manifest = {'schema_version': 1, 'id': NAME, 'status': 'source-only candidate, full parent script review pending',
        'raw_manifests': raw_manifests, 'screenshots': captures, 'excluded_sources': excluded}
    source = {'repositories': source_evidence['repositories'], 'files': snapshots,
        'limits': 'Exact retained35 Core/Responder source snapshots are copied from the historical source plan. This is source correspondence, not current deployment/executed-code attestation. Only30 Core files are learner source citations;5 Responder traces document unexercised/gated client limits.'}
    compact = '\n\n'.join(scene['scene_id'] + ' | ' + screen['source_alias'] + ' | ' + screen['capture_id'] + '\n' + screen['narration_span'] + '\nVisible: ' + ' | '.join(screen['required_labels']) for scene in sequence for screen in scene['screens']) + '\n'
    assets.update({'candidate.json': encoded(lesson), 'narration.candidate.txt': narration.encode(),
        'captures.reviewed.json': encoded(manifest), 'screen-sequence.untimed.json': encoded({'id': NAME, 'timing_assigned': False, 'scenes': sequence}),
        'compact-correspondence.txt': compact.encode(), 'source-review.json': encoded(audit),
        'source-evidence.json': encoded(source), 'actual-operation-log.json': encoded(operation_log),
        'scenario.replay-delta.json': encoded(replay_delta)})
    assert len(lesson['sector_examples']) == 6
    return lesson, assets, input_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    lesson, assets, inputs = prepare()
    if args.write_candidate:
        destination = S / OUT
        assert not destination.exists(), 'New-only candidate; retain all historical sources.'
        spec = importlib.util.spec_from_file_location('records_admin_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        assert not findings, findings
        assets['preflight.json'] = encoded({'source_only': True, 'recipe_sha256': sha(__file__),
            'input_files': inputs, 'files_scanned': len(assets), 'ordinary_privacy_findings': [],
            'additional_known_private_values_checked': 0, 'no_credential_or_auth_reads': True,
            'parent_full_script_review_pending': True, 'narration_frozen': False,
            'outputs': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(body)
    manifest = json.loads(assets['captures.reviewed.json'])
    print(json.dumps({'source_preflight_passed': True, 'files_written': args.write_candidate,
        'scenes': len(lesson['scenes']), 'narration_words': sum(len(scene['narration'].split()) for scene in lesson['scenes']),
        'accepted_images': len(manifest['screenshots']), 'raw_pairs_preserved': 44,
        'independently_displayed_key_images': len(OWN_VIEWS), 'source_snapshots': 35,
        'untimed_spans': sum(len(scene['screens']) for scene in json.loads(assets['screen-sequence.untimed.json'])['scenes']),
        'candidate_sha256': hashlib.sha256(assets['candidate.json']).hexdigest(),
        'narration_sha256': hashlib.sha256(assets['narration.candidate.txt']).hexdigest(),
        'compact_sha256': hashlib.sha256(assets['compact-correspondence.txt']).hexdigest(),
        'output': str(S / OUT), 'parent_script_review_pending': True,
        'frozen_media_canonical_ready_or_site_changed': False}, indent=2))


if __name__ == '__main__':
    main()
