"""Prepare a NEW unvoiced Return candidate from reviewed immutable screenshots.

Default is read-only. No UI, API, database, reset, voice, timing, render, freeze,
canonical, site or target operation exists here. Replay remains manual and must
stop on the captured issuance, which is already Returned with zero outstanding.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-inventory-return-reconcile'
RAW = 'captures/expansion/core-inventory-return-report-20261028/manifest.json'
RAW_SHA = '956a8a7da22d17c91ae4a6e3369b154713a6c81f2ed93de14b57a4d50dfedbe2'
REVIEWED_AT = '2026-10-28T22:21:23Z'
NOTE = 'TRAINING ONLY - Return the remaining one fictional training battery pack to Station. Software exercise; no physical movement.'
MODAL = ['Return · Academy training batteries', 'Amount', 'Destination location', 'Status', 'Note', 'Close', 'Return']
STOCK = ['Items', 'Academy training batteries', 'Location', 'Filter', 'Unit', 'Person', 'Unit equipment', 'Personnel gear', 'Adjust stock', 'Item', 'Quantity', 'Status', 'Station', 'Personnel', '5.000000', 'History']
ISSUANCE = ['Inventory', 'On hand', 'Issuances', 'History', 'Item', 'Location', 'Outstanding', 'Expected return date', 'Status', 'Actions', 'Academy training batteries', 'Personnel', '10/26/2026', 'Issue equipment']
LABELS = {
    '001': STOCK + ['13.000000', '1.000000'],
    '002': ISSUANCE + ['1.000000', 'Partially returned', 'Return'],
    '004': MODAL + ['1.000000', '—', 'In service'],
    '005': MODAL + ['1', 'Station', 'In service', NOTE],
    '006': MODAL + ['1', 'Station', 'Out for repair', NOTE],
    '007': MODAL + ['1', 'Station', 'Damaged', NOTE],
    '008': MODAL + ['1', 'Station', 'In service', NOTE],
    '009': ISSUANCE + ['0.000000', 'Returned'],
    '010': ['Items', 'Location', 'Filter', 'When', 'Movement', 'Item', 'Quantity', 'Details', 'Return', 'Consume', 'Issue', 'Transfer', 'Receive', 'Academy training batteries', 'Personnel', 'Station', 'Unit', '1.000000', '2.000000', '5.000000', '20.000000', NOTE, 'Fictional training usage.', 'Fictional partial return.', 'Fictional training issue to Matthew Casey; software exercise.', 'Fictional Academy restock transfer — five training packs.', 'Fictional Academy opening receipt — software training only.', 'Attest as witness', 'Rebuild stock balances'],
    '011': STOCK + ['14.000000', '0.000000'],
}
SCOPES = {
    '001': 'Pre-return filtered balances13Station/5Unit/1Personnel,total19. On hand and Inventory headings are above this viewport; use002 for navigation labels.',
    '002': 'Readable Inventory/On hand/Issuances/History controls and single partially returned training row,outstanding1. Personnel is the printed holder label; no person name is printed in this row.',
    '004': 'Settled foreground Return modal only; blank destination, amount1.000000, In service selected. Dimmed background excluded.',
    '005': 'Foreground prepared return amount1,Station,In service and complete training note; no movement posted yet.',
    '006': 'Foreground Out for repair selection only, unsaved. No repair return or work order is established.',
    '007': 'Foreground Damaged selection only, unsaved. No damaged-stock return is established.',
    '008': 'Foreground final review restored In service,amount1,Station,note and complete Return button; not yet submitted in this frame.',
    '009': 'Fresh returned issuance,outstanding0 and no Return row action. On hand and History buttons fully visible; no literal No Return label is invented.',
    '010': 'All6 ledger rows visible, including newReturn1Personnel→Station/note, Consume1, olderReturn1,Issue2/Casey,Transfer5,Receive20. History heading itself is clipped and excluded. Witness/rebuild buttons not exercised.',
    '011': 'Fresh post-return balances14Station/5Unit/0Personnel,total19. On hand and Inventory headings are above viewport; no stock condition value is printed in these rows.',
}
# Exact narration chunks are bound to real images, with no assigned timings.
SCENES = [
    ('01', 'Read the stock context', [
        ('002', 'In Core Inventory, this recorded exercise returns the remaining issued stock and checks where the balance went. Open On hand to review the current item and location.'),
        ('001', 'Use Items to select Academy training batteries and choose Filter. The starting snapshot shows thirteen at Station, five at Unit and one at Personnel: nineteen altogether. These figures follow earlier usage, so they are later than the separate twenty-pack receipt example.'),
    ], ['Inventory', 'On hand', 'Items', 'Academy training batteries', 'Filter', 'Station', '13.000000', 'Unit', '5.000000', 'Personnel', '1.000000'], 'Identify the item and current holders before considering a return; use the quantities in your own permitted record.'),
    ('02', 'Open the outstanding issuance', [
        ('002', 'Choose Issuances. Find the training batteries row and compare Location, Outstanding and Status. This row says Personnel, one outstanding, and Partially returned. Personnel identifies the holder category here; it does not print a person’s name. Choose the row’s Return action.'),
        ('004', 'The Return window names the batteries and asks for Amount, Destination location, Status and Note. Opening this form has not recorded a return.'),
    ], ['Issuances', 'Outstanding', 'Partially returned', 'Return', 'Return · Academy training batteries', 'Amount', 'Destination location', 'Status', 'Note'], 'Open only an authorized practice issuance with a positive outstanding amount and a visible Return action.'),
    ('03', 'Prepare the amount and destination', [
        ('005', 'For this example, Amount is one and Destination location is Station. Read both before continuing: the quantity is coming back from the issuance holder to that destination. Add a useful Note explaining the return. Ours clearly marks a fictional software exercise with no physical movement. Check the complete note rather than relying on a shortened description elsewhere.'),
    ], ['Amount', '1', 'Destination location', 'Station', 'Note', NOTE], 'Compare the permitted amount, destination and complete note; never use the example quantities as instructions for unrelated stock.'),
    ('04', 'Review the condition without posting alternatives', [
        ('006', 'Status describes the condition the equipment came back in. Out for repair is one available choice, shown here without submitting it.'),
        ('007', 'Damaged is another choice, also left unsaved in this exercise.'),
        ('008', 'We restore In service for the final training return. Select the condition that matches your authorized record; choosing a software label does not establish a physical inspection or repair.'),
    ], ['Status', 'Out for repair', 'Damaged', 'In service'], 'Inspect the choices without posting alternative conditions. The captured return used In service; no repair or damaged return was recorded.'),
    ('05', 'Submit once and read the result', [
        ('008', 'Review Amount, Station, In service and the full Note together. When the intended return is correct, select the Return button at the bottom once.'),
        ('009', 'Read the resulting Issuances row. It now says Returned with zero outstanding, and its Return action is gone. That readback establishes the stored result; the prepared form alone did not. Avoid submitting again while waiting for a result.'),
    ], ['Return', 'Amount', 'Station', 'In service', 'Note', 'Issuances', 'Returned', '0.000000'], 'Compare the result with the intended return and stop when the issuance is Returned with zero outstanding.'),
    ('06', 'Check the new ledger entry', [
        ('009', 'Choose History to check the recorded movement.'),
        ('010', 'Filter Items to the same training batteries. The new top Return row shows one moving from Personnel to Station, with our complete training note. Earlier rows remain separate: Consume records one used pack, and the older Issue row records two, with Matthew Casey named in its note. Read the movement, quantity, direction and note together so an older return is not mistaken for the new one.'),
    ], ['History', 'Items', 'Filter', 'Academy training batteries', 'Return', 'Personnel', 'Station', '1.000000', NOTE, 'Consume', 'Issue', '2.000000', 'Fictional training issue to Matthew Casey; software exercise.'], 'Find the new Return by its direction, amount and note; distinguish it from the earlier partial return and usage.'),
    ('07', 'Reconcile the holdings', [
        ('009', 'Return to On hand for the balance check.'),
        ('011', 'The fresh filtered table now shows fourteen at Station, five at Unit and zero at Personnel. The total is still nineteen. Returning the issued pack moves its recorded holding; it does not restore the pack consumed earlier or create an extra receipt. Compare this result with the starting balances and the new ledger entry.'),
    ], ['On hand', 'Academy training batteries', 'Station', '14.000000', 'Unit', '5.000000', 'Personnel', '0.000000'], 'Reconcile the holder changes without changing the overall total or resetting the recorded usage.'),
    ('08', 'Leave the completed example intact', [
        ('009', 'The example issuance is now Returned with zero outstanding. Do not submit another return against it.'),
        ('011', 'For practice, use a different approved issuance that still has stock outstanding and read its current balances. The same return and reconciliation pattern serves fire and EMS, community paramedicine and mental health teams, search and rescue, security departments and companies, wildland contractors, and industrial emergency response teams.'),
    ], ['Returned', '0.000000', 'Academy training batteries', 'Station', 'Quantity'], 'If the issuance is Returned, outstanding is zero, or Return is absent, stop. Use a separate approved practice record to rehearse a future return.'),
]
SOURCE_FILES = [
    'Web/Resgrid.Web/Areas/User/Controllers/InventoryController.cs',
    'Web/Resgrid.Web/Areas/User/Views/Inventory/Workspace.cshtml',
    'Core/Resgrid.Services/InventoryIssuance.cs',
    'Core/Resgrid.Model/Inventories/InventoryContracts.cs',
]


def need(ok, message):
    if not ok: raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare(core):
    need(sha(SOURCES / RAW) == RAW_SHA, 'Raw18capture manifest changed; preserve all original evidence.')
    rows = json.loads((SOURCES / RAW).read_text()); need(isinstance(rows, list) and len(rows) == 18, 'Expected the held18rawcaptures.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions, _Validator, visible_controls_digest
    from expansion_site import _public_lesson
    by_prefix = {}
    for row in rows:
        for path_key, hash_key in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            rel = Path(row[path_key]); need(not rel.is_absolute() and '..' not in rel.parts and sha(SOURCES / rel) == row[hash_key], 'Raw image/DOM identity changed.')
        need(_image_dimensions(SOURCES / row['file']) == (1434, 773), 'Raw full-frame dimensions changed.')
        by_prefix[row['id'][:3]] = row
    reviewed = []
    for prefix, literals in LABELS.items():
        row = copy.deepcopy(by_prefix[prefix]); original = copy.deepcopy(row)
        # Native select values/textarea contents were read from real pixels and
        # corroborated in retained DOM. Raw recorder omissions are not repaired.
        row.update(visible_labels=list(dict.fromkeys(literals)), visible_field_text=[], visible_controls=[], required_labels=[], eligible_for_lesson=True, review_status='actual_original_size_pixels_and_full_dom_reviewed', visual_review='actual_original_size_pixels_and_full_dom_reviewed', source_observation_limits=SCOPES[prefix])
        row['capture_review'] = {'passed': True, 'reviewer': 'Codex dispatch_ic_coverage exact original-size JPEG/DOM review', 'reviewed_at': REVIEWED_AT, 'sha256': row['sha256'], 'controls_sha256': visible_controls_digest([]), 'application_visible': True, 'no_errors': True, 'controls_reviewed': True, 'controls_fully_visible': True, 'controls_unobstructed': True, 'method': 'Personally viewed the exact1434x773 original JPEG with view_image. Retained literals are readable foreground text only; modal backgrounds, clipped headings and inferred accessible names excluded. Complete DOM corroborates form values and stored rows but does not make offscreen text visible. Raw pixels/DOM/metadata remain unchanged.'}
        row['curation_provenance'] = {'raw_manifest': RAW, 'raw_manifest_sha256': RAW_SHA, 'raw_record_sha256': hashlib.sha256(json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest(), 'added_personally_readable_literals': [x for x in row['visible_labels'] if x not in original['visible_labels']], 'removed_raw_labels': [x for x in dict.fromkeys(original['visible_labels']) if x not in row['visible_labels']], 'raw_record_unmodified': True}
        v = _Validator(SOURCES); v.observations(row, row['id']); need(not v.issues, '; '.join(v.issues)); reviewed.append(row)
    shots = {row['id'][:3]: row for row in reviewed}
    scenes, spans = [], []
    for scene_id, title, chunks, required, practice in SCENES:
        refs = []
        for index, (prefix, text) in enumerate(chunks, 1):
            shot = shots[prefix]; refs.append(shot['id'])
            spans.append({'id': scene_id + '-' + str(index).zfill(2), 'scene_id': scene_id, 'capture_ref': shot['id'], 'file': shot['file'], 'sha256': shot['sha256'], 'narration_exact': text, 'required_labels': [label for label in required if label in shot['visible_labels']], 'timing_status': 'Unassigned; requires genuine completed speech timing after parent script review.', 'scope_limit': SCOPES[prefix]})
        union = {label for prefix, _ in chunks for label in shots[prefix]['visible_labels']}
        need(set(required) <= union, 'A named scene control is not visible in the corresponding original images.')
        scenes.append({'id': scene_id, 'title': title, 'route': '/User/Inventory', 'capture_intent': 'Use ordered actual reviewed originals; no invented clicks, result, timing or continuous recording claim.', 'capture_refs': list(dict.fromkeys(refs)), 'required_labels': required, 'narration': ' '.join(text for _, text in chunks), 'practice': practice})
    sectors = [
        {'sector': 'Fire / EMS', 'scenario': 'Return remaining issued training supplies to the intended station stock.', 'practice': 'Confirm the outstanding amount, return destination and ledger before a new restock.'},
        {'sector': 'Community response', 'scenario': 'Account for unused community care or mental health response supplies.', 'practice': 'Use an operational supply note without patient details and reconcile the recorded holder.'},
        {'sector': 'Search and rescue', 'scenario': 'Reconcile supplies issued for a search exercise.', 'practice': 'Distinguish unused returned stock from quantities already consumed.'},
        {'sector': 'Security', 'scenario': 'Return stock signed out for a security patrol assignment.', 'practice': 'Read the actual holder and remaining amount; do not infer a person from the Personnel label.'},
        {'sector': 'Wildland', 'scenario': 'Reconcile unused supplies from a contractor crew assignment.', 'practice': 'Select the appropriate permitted destination and condition, then verify the saved return.'},
        {'sector': 'Industrial response', 'scenario': 'Return unused exercise supplies to facility stock.', 'practice': 'Keep the software condition selection separate from any physical inspection or repair process.'},
    ]
    lesson = {'id': NAME, 'title': 'Return issued stock and reconcile the balance', 'app': 'Core', 'audience': ['Inventory coordinators', 'Authorized stock and equipment managers'], 'summary': 'Review a remaining issuance, prepare its return amount, destination and condition, post once, and reconcile the returned record, ledger and holdings.', 'prerequisites': ['Authorized Inventory access with permission to return the chosen practice issuance.', 'A clearly identified noncontrolled practice item and a positive outstanding quantity on the chosen issuance.', 'The captured example is already Returned with zero outstanding. Do not repeat its return or reset stock; use another authorized practice record if rehearsing.', 'Choose the actual permitted destination and condition for your record; this software exercise establishes no physical movement, inspection or repair.'], 'scenes': scenes, 'sector_examples': sectors, 'candidate_only': True, 'source_only': True, 'export_ready': False, 'publication_approved': False, 'narration_approved': False, 'scope_limits': ['This candidate covers one actual final return and readback; it does not recreate the earlier receipt/issue/partial return.', 'Unsaved Out for repair and Damaged selections were restored to In service before the one actual return.', 'Current total19 follows earlier Consume1; the separate movement lesson20pack snapshot remains unchanged.', 'History button is pictured in009; clipped History heading in010 is not a visible label.', 'No witness, rebuild, controlled-substance, kit, physical inspection, repair or provider operation is demonstrated.', 'Report, PDF and stock-count workflows are outside this Return lesson.', 'Browser captures establish these software records; native hardware, GPS and offline operation are unverified.']}
    _public_lesson(lesson)
    need('History' not in shots['010']['visible_labels'] and 'Return' not in shots['009']['visible_labels'], 'Clipped/absent controls must never become literal labels.')
    fixture = {'id': NAME, 'mode': 'manual_normal_ui_only', 'default': 'read_only_plan', 'automated_writes': False, 'captured_example': {'item': 'Academy training batteries', 'current_issuance_status': 'Returned', 'current_outstanding': 0, 'return_action_available': False, 'duplicate_return_allowed': False, 'historical_before': {'Station': 13, 'Unit': 5, 'Personnel': 1}, 'historical_after': {'Station': 14, 'Unit': 5, 'Personnel': 0}, 'total': 19, 'earlier_consume': 1, 'these_values_are_not_replay_targets': True}, 'guards': ['Read the live item, holder, issuance state and outstanding amount through normal Inventory UI; never force a captured item/issuance ID or revision.', 'If Returned, outstanding is zero, Return is absent, or identity is ambiguous: stop without submitting. The captured example meets this stop condition.', 'Use only a separate authorized noncontrolled practice issuance with positive outstanding; do not create/reset/issue stock as an implicit replay step.', 'Compare the approved return amount with the actual remaining quantity; never blindly copy1. Select the permitted destination and accurate condition.', 'Out for repair and Damaged may be inspected without submission only if appropriate; the captured example posted In service alone.', 'Enter and read back a clear training note. Submit exactly once only on the distinct permitted practice record, then wait for and inspect the actual UI result.', 'Read the fresh ledger and balances. If uncertain or an error appears, stop and inspect; do not repeat Return, rebuild balances, change database state or infer success.', 'Do not invoke witness/attestation, controlled stock, repair/work order, provider, import or report/PDF workflows from this lesson.'], 'normal_ui_steps': ['Inventory → On hand: choose item and Filter; read current balances.', 'Issuances: confirm the intended outstanding record and visible Return action.', 'Return form: read Amount, Destination location, Status and Note.', 'After a permitted single return: read Returned/remaining amount, History movement and On hand balances.'], 'fixed_numeric_or_guid_ids': [], 'current_example_replay_result': 'STOP: already Returned0; read-only review only.'}
    excluded = [{'id': row['id'], 'file': row['file'], 'sha256': row['sha256'], 'eligible_for_this_candidate': False, 'reason': 'Transient fade and clipped modal header; settled004 retained instead.' if row['id'].startswith('003') else 'ReportUnavailable failure diagnostic, retained only in audit; not a Return operation or PDF success.' if row['id'].startswith('016') else 'Separate stock-count/report workspace or report setup; outside the bounded Return lesson.'} for row in rows if row['id'][:3] not in LABELS]
    manifest = {'app': 'Core', 'kind': 'reviewed_return_source_subset_only', 'reviewed_at': REVIEWED_AT, 'source_manifest': RAW, 'source_manifest_sha256': RAW_SHA, 'screenshots': reviewed, 'excluded_sources': excluded, 'publication_approved': False, 'raw_files_modified': False}
    citations = []
    copies = {}
    for relative in SOURCE_FILES:
        p = core / relative; need(p.is_file(), 'Core source citation missing: ' + relative)
        copies['source/Core/' + relative] = p.read_bytes()
        citations.append({'logical_source': 'Core/' + relative, 'candidate_relative_file': 'source/Core/' + relative, 'sha256': sha(p)})
    narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    need(' '.join(x['narration_exact'] for x in spans) == ' '.join(scene['narration'] for scene in scenes), 'Untimed spans lost/repeated narrated words.')
    files = {'lesson.candidate.json': encoded(lesson), 'narration.candidate.txt': narration.encode(), 'untimed-screen-sequence.json': encoded({'lesson_id': NAME, 'spans': spans, 'timing_source': None, 'audio_created': False, 'rendered': False}), 'captures.reviewed.json': encoded(manifest), 'scenario-fixture.json': encoded(fixture), 'source-citations.json': encoded(citations), **copies}
    return lesson, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core-source', type=Path, required=True)
    parser.add_argument('--write-candidate', type=Path)
    args = parser.parse_args(); lesson, files = prepare(args.core_source.resolve())
    if args.write_candidate:
        destination = args.write_candidate.resolve()
        need(destination.is_relative_to((SOURCES / 'expansion/plans').resolve()) and not destination.exists(), 'Use a NEW candidate directory; preserve originals/history.')
        destination.mkdir(parents=True)
        for relative, data in files.items():
            path = destination / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    print(json.dumps({'source_preflight': 'passed', 'candidate_written': bool(args.write_candidate), 'scenes': 8, 'words': sum(len(scene['narration'].split()) for scene in lesson['scenes']), 'reviewed_sources': 10, 'untimed_spans': sum(len(x[2]) for x in SCENES), 'source_only': True, 'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}, indent=2))


if __name__ == '__main__':
    main()
