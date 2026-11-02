"""Freeze personally reviewed historical return screens; no final-video approval."""
import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-inventory-final-return'
RAW = S / 'captures/expansion/core-inventory-return-report-20261028'
DEST = S / 'expansion/plans/core-inventory-final-return-source-20261102'

# The exact original pixels were personally inspected before writing this recipe.
SCENES = [
    ('01', 'Find the remaining issued quantity', [2],
     ['Issuances', 'Outstanding', 'Partially returned', 'Return'],
     'In Inventory, open Issuances and find the item that has come back. This example follows Academy training batteries after an earlier partial return. The row still shows one outstanding, the Personnel location, and Partially returned. Check the item, outstanding quantity and expected return date together. Select Return on that row to open its return form. This is a fictional software exercise in the training department.',
     'Find the correct issuance and compare its outstanding quantity before opening Return.'),
    ('02', 'Read the return form before entering changes', [4],
     ['Amount', 'Destination location', 'Status', 'Note', 'Return'],
     'The Return dialog separates Amount, Destination location, Status and Note. Amount starts at the remaining quantity. The destination is initially blank, and the status is In service. The help beneath Destination location says to leave it blank when consuming or writing stock off. For this exercise the item is being returned to a stock location, so we will select a destination before submitting. Close exits this dialog without making the prepared return.',
     'Identify the amount, destination, condition and note controls in the actual dialog.'),
    ('03', 'Choose where the returned stock goes', [5],
     ['Amount', 'Destination location', 'Station', 'In service', 'Note'],
     'Set Amount to one and choose Station as the Destination location. Leave Status at In service for the intended return. Add a clear note explaining the movement. Here it says that the remaining fictional training battery pack is going back to Station, and that no physical movement is taking place. The quantity and destination are separate decisions: one tells Resgrid how much came back, and the other tells it where that stock is going.',
     'Prepare the remaining quantity, the intended stock location and a useful explanation.'),
    ('04', 'Distinguish return conditions', [6, 7],
     ['Status', 'Out for repair', 'Damaged'],
     'The Status control also offers Out for repair and Damaged. These screens show those choices selected in the form before saving. The help describes Status as the state the equipment came back in. Choose the condition that matches the actual return, following your department procedure. In this recording we inspect both alternatives and then restore In service; we do not post a damaged or repair return.',
     'Recognize the condition choices without submitting a condition that does not match the item.'),
    ('05', 'Submit the final return and verify its result', [8, 9],
     ['Amount', 'Station', 'In service', 'Return', 'Returned', 'Outstanding'],
     'Before submitting, check the final form again: one item, Station, In service, and the training note. Select Return at the bottom of the dialog. The returned Issuances table now shows zero outstanding and a green Returned status on the same item row. Its Return action is gone. This saved result is the check that the last outstanding quantity has been cleared; a completed form alone would not establish that the return was stored.',
     'Submit once, then verify zero outstanding and Returned on the matching issuance.'),
    ('06', 'Read the movement in History', [2, 10],
     ['History', 'Filter', 'Return', 'Personnel', 'Station'],
     'Open History to inspect the movement ledger. Filter to Academy training batteries. The newest row is a Return of one, moving from Personnel to Station, with the same explanatory note. The earlier partial return and the earlier Consume row remain visible as separate movements. Check the quantity, direction and note together when explaining a balance change. This review uses the ledger as shown; no witness attestation or stock-balance rebuild is performed.',
     'Match the return to its ledger quantity, direction and note.'),
    ('07', 'Reconcile on-hand balances', [2, 1, 11],
     ['On hand', 'Filter', 'Station', 'Unit', 'Personnel'],
     'Return to On hand and apply the item filter. Before this return, the recorded balances were thirteen at Station, five at Unit and one at Personnel. After the return, they are fourteen at Station, five at Unit and zero at Personnel. The total stays nineteen. Returning issued stock changes where that quantity is held; it does not reverse the separate earlier consumption or restore the original receipt of twenty.',
     'Compare the before and after locations, and reconcile the unchanged total.'),
    ('08', 'Use the same review across department types', [11],
     ['Academy training batteries', 'Station', 'Unit', 'Personnel'],
     'Use the same quantity, location and condition checks for other department equipment. A search-and-rescue team can track returned radio batteries, a security company can track issued equipment, and a wildland contractor can reconcile field supplies. Community paramedicine and mental health response teams, industrial emergency teams, and fire and E M S departments can use the same recorded return process. Agree who records returns, and verify both the issuance and the location balances after each exercise.',
     'Choose an example relevant to your department and define who verifies its return.')
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    if (DEST / 'lesson.candidate.json').exists():
        raise SystemExit('Preserve this source freeze; use a new dated recipe for changes.')
    raw = json.loads((RAW / 'manifest.json').read_text())
    numbered = {int(row['id'][:3]): row for row in raw}
    now = datetime.now(timezone.utc).isoformat()
    scenes = []
    for ident, title, refs, labels, speech, practice in SCENES:
        scenes.append(dict(id=ident, title=title, route='/User/Inventory',
                           capture_refs=[numbered[n]['id'] for n in refs],
                           required_labels=labels, narration=speech, practice=practice,
                           capture_intent='Show each real control before its recorded result; retain the separate historical balance checkpoints.'))
    selected = []
    for number in sorted({n for row in SCENES for n in row[2]}):
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        assert sha(S / row['dom_file']) == row['dom_sha256']
        row.update(eligible_for_lesson=True, review_status='actual_original_image_reviewed',
                   capture_review=dict(reviewer='Root', passed=True, reviewed_at=now,
                                       sha256=row['sha256'], method='Root personally inspected this original using view_image. No screenshot pixels changed.'))
        selected.append(row)
    lesson = dict(id=NAME, title='Return the final issued quantity and reconcile inventory balances',
                  app='Core', summary='Complete an outstanding equipment return, inspect its ledger movement, and reconcile before-and-after location balances.',
                  audience=['Inventory administrators', 'Equipment officers', 'Department supervisors'],
                  prerequisites=['Authorized Inventory access and a separate fictional training issuance.',
                                 'An existing partially returned issuance; this recording continues historical training data rather than creating a new issuance.'],
                  scenes=scenes, candidate_only=True, export_ready=False,
                  publication_approved=False, source_files=[],
                  sector_examples=[dict(sector=sector, scenario=scenario) for sector, scenario in [
                      ('Search and rescue', 'Reconcile a final radio-battery return to a base stock location.'),
                      ('Security', 'Review remaining issued equipment and its return condition.'),
                      ('Community response', 'Check returned equipment for community paramedicine and mental health teams.'),
                      ('Wildland', 'Trace returned field supplies without reversing earlier consumption.'),
                      ('Industrial', 'Review equipment condition and location balances.'),
                      ('Fire/EMS', 'Close the remaining issuance and verify the corresponding ledger movement.')]],
                  scope_limits=['New narration, exact caption correspondence, complete listening, encoded frame review and actual browser playback remain required.',
                                'Only the In service return is submitted. Repair and Damaged are inspected unsaved choices.',
                                'No record-linked consumption reversal, successful PDF export, witness attestation or balance rebuild is demonstrated.',
                                'Balances are the dated historical snapshots shown in the unmodified screenshots.'])
    manifest = dict(schema_version=1, id=NAME, screenshots=selected,
                    raw_manifest=dict(file=str((RAW / 'manifest.json').relative_to(S)), sha256=sha(RAW / 'manifest.json')),
                    excluded_sources=[dict(id=row['id'], sha256=row['sha256'], reason='Outside the final-return lesson; report setup/failure and transitional frame are not success footage.') for row in raw if row['id'] not in {x['id'] for x in selected}])
    for filename, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest),
                            ('source-review.json', dict(reviewer='Root', reviewed_at=now, actual_images_reviewed=[row['id'] for row in selected],
                                                       source_pixels_unchanged=True, source_only=True, narration_or_video_approval_inferred=False))]:
        (DEST / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    text = '\n\n'.join(row['narration'] for row in scenes) + '\n'
    (DEST / 'narration.txt').write_text(text)
    print(json.dumps(dict(lesson=NAME, scenes=len(scenes), screenshots=len(selected), words=len(text.split()))))


if __name__ == '__main__':
    main()
