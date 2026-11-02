"""Freeze the reviewed Big Board summary screens and their bounded lesson script."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'app-bigboard-readiness-summaries'
RAW = Path('captures/expansion/bigboard-readiness-summaries-20261101')
RAW_SHA = '7a8636e2aae2c8f41d8dc3b508e1196f901241f1dad5881e412c59c80b49c168'
LABELS = {
    1: ['Resgrid BigBoard', 'Edit', 'Add Widget', 'Close', 'Personnel Status Summary', 'Personnel Staffing Summary', 'Units Summary'],
    3: ['Personnel Status', 'Standing By', '14', 'Personnel Staffing', 'Available', '3', 'Delayed', '1', 'Unavailable', '2', 'Committed', 'On Shift', '8', 'Units', 'Total', '6', 'Responding'],
    4: ['Personnel Status Widget', 'Personnel Status Summary Widget', 'Display Options', 'Show Colors', 'Font Size: 14pt', 'Widget Size', 'Width (grid units): 4', 'Height (grid units): 4', 'Save'],
    5: ['Personnel Status', 'Responding', '0', 'Not Responding', 'On Scene', 'Standing By', '14', 'Personnel Staffing', 'Available', '3', 'Delayed', '1', 'Unavailable', '2', 'Committed', 'On Shift', '8', 'Units', 'Total', '6'],
    8: ['Personnel Status', 'Standing By', '14', 'Personnel Staffing', 'Available', '3', 'Delayed', '1', 'Unavailable', '2', 'Committed', '0', 'On Shift', '8', 'Units', 'Total', '6', 'Responding', 'On Scene'],
    9: ['Units', 'Name', 'State', 'Station', 'Type', 'Updated', 'Engine 51', 'Available', '4 days ago', 'Truck 81', '7 days ago', 'Squad 3', 'Responding', 'Ambulance 61', 'Released', 'Reserve Engine 51', 'Out of Service', '5 days ago', '1 minute ago'],
    10: ['Personnel Status Widget', 'Personnel Status Summary Widget', 'Display Options', 'Show Colors', 'Font Size: 14pt', 'Widget Size', 'Width (grid units): 4', 'Height (grid units): 4', 'Save'],
}
SCENES = [
    ('01', 'Add the three readiness summaries', [1, 3],
     'Big Board gives a duty supervisor or department coordinator a shared view of operational information. From the board, use the plus icon at the upper right to open Add Widget. Choose Personnel Status Summary, Personnel Staffing Summary and Units Summary. After adding them, scroll to the three rendered panels. This fictional department already has calls, units and a personnel list elsewhere on its board. These summary panels provide counts that you can compare with those detailed views.'),
    ('02', 'Separate personnel status from staffing', [3],
     'Read Personnel Status and Personnel Staffing as separate measures. Here, Standing By shows fourteen in the status panel. Staffing shows three Available, one Delayed, two Unavailable, zero Committed and eight On Shift. The same fourteen people are being described in different ways. A Standing By status therefore does not mean that fourteen people have Available staffing. Keep both panels visible when discussing the department\'s current staffing picture, rather than treating one count as a substitute for the other.'),
    ('03', 'Improve contrast and verify the visible result', [3, 4, 5],
     'The colored personnel-status counts are difficult to distinguish against this dark background. Use the gear icon at the upper right to open configuration, then select Personnel Status Widget. On Personnel Status Summary Widget, turn Show Colors off. This example keeps Font Size at fourteen points, with width and height both set to four grid units. Select Save and return to the board. The Personnel Status numbers now use neutral light text, making the zero values easier to see.'),
    ('04', 'Read the staffing distribution without overinterpreting it', [5],
     'In Personnel Staffing, compare all five rows. Available is three, Delayed is one, Unavailable is two, Committed is zero and On Shift is eight. These totals describe the staffing values currently reported for the demo roster. The panel does not identify which individuals make up each count. Use it to spot a staffing question, then consult the personnel details before making an assignment. A count alone does not tell you a person\'s qualifications, current location or suitability for a particular task.'),
    ('05', 'Compare unit totals with individual states', [5, 9],
     'Units Summary shows eight total units, six Available, one Responding and zero On Scene. Scroll to the detailed Units table to see the individual names and State values. Squad Three is Responding, Ambulance Sixty One is Released, and Reserve Engine Fifty One is Out of Service. Other rows say Available. The summary groups underlying status categories, so its Available number is not simply a count of rows containing that exact word. Review the detailed states when selecting a specific resource.'),
    ('06', 'Check the age of the underlying unit information', [9],
     'The Units table also includes Station, Type and Updated. In this recorded example, several unit updates are four, five or seven days old, while the two training vehicles show one minute ago. Those ages matter when interpreting a summary built from these states. A visible count does not establish that every underlying report is recent. Read Updated alongside State, and resolve stale information through your department\'s normal status-reporting process before relying on the board for an operational decision.'),
    ('07', 'Reload and read back the saved preferences', [8, 10],
     'After saving, reload the board and return to the summary panels. The neutral personnel-status counts remain visible. Reopen configuration and select Personnel Status Widget again. Show Colors is still off, and the form still shows fourteen points and four-by-four grid dimensions. This readback checks the setting that was actually saved. Repeat that check on the display used by your team, and assess the text from the distance where viewers will read it.'),
    ('08', 'Use the same panels across different organizations', [8],
     'These panels can support more than fire and E M S. A security supervisor can compare staffing with patrol-unit states. A search-and-rescue coordinator can review people and vehicles separately. Community paramedicine and mental health response teams, wildland contractors and industrial emergency response teams can use the same distinction between personnel status, staffing and unit state. Keep the labels meaningful to your department, use the detailed lists to investigate the counts, and make sure the displayed information is readable and current.'),
]


def prepare(write=False):
    from verify_capture_evidence import _Validator, _image_dimensions
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    raw = S / RAW / 'manifest.json'
    assert sha(raw) == RAW_SHA
    rows = json.loads(raw.read_text())
    numbered = {int(row['id'][:3]): row for row in rows}
    reviewed_at = datetime.now(timezone.utc).isoformat()
    selected = []
    for number, labels in LABELS.items():
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        assert _image_dimensions(S / row['file']) == (row['width'], row['height'])
        dom = S / RAW / (row['id'] + '.txt')
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[],
                   dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom),
                   capture_review=dict(reviewer='Root', passed=True, reviewed_at=reviewed_at,
                                       sha256=row['sha256'], method='Root personally viewed this exact stored original using view_image. Pixels unchanged; only literal visible labels selected.'))
        validator = _Validator(S)
        validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
        selected.append(row)
    scenes = [dict(id=i, title=title, route='/configure' if i == '03' else '/home',
                   capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the actual widget chooser, summary counts, configuration control, saved result or detailed unit rows being discussed.',
                   required_labels=list(dict.fromkeys(label for n in refs for label in LABELS[n])),
                   narration=text, practice=title + ' using an isolated fictional department and training board.')
              for i, title, refs, text in SCENES]
    lesson = dict(id=NAME, title='Big Board: interpret readiness summaries and improve contrast', app='BigBoard',
                  summary='Add personnel-status, staffing and unit summaries; improve status-count contrast; compare totals with unit states and update ages; and verify saved preferences.',
                  audience=['Duty supervisors', 'Department coordinators', 'Administrators configuring a shared operational display'],
                  prerequisites=['An authenticated Big Board session connected to an isolated fictional department.', 'Existing personnel staffing, personnel status and unit state data in the training department.'],
                  scenes=scenes,
                  sector_examples=[dict(sector=sector, scenario=text) for sector, text in [
                      ('Security', 'Compare staffing distribution with patrol-unit states.'),
                      ('Search and rescue', 'Review personnel and vehicle counts separately, then inspect the detailed units.'),
                      ('Community response', 'Distinguish staffing from personnel status for paramedicine and mental health response teams.'),
                      ('Wildland', 'Review contractor personnel and unit readiness with update ages.'),
                      ('Industrial', 'Use readable summary panels alongside detailed response-team resources.'),
                      ('Fire/EMS', 'Compare separate status, staffing and unit-state views in a fictional training department.')]],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; generated narration, listening, complete correspondence, encoded-frame review and actual playback remain required.',
                                'This is a scrollable training board, not a completed wall-display layout.',
                                'No live dispatch, status update, roster change, database write, advanced mapping or alert configuration is demonstrated.',
                                'Font16 did not persist in two raw attempts. Sources002 and006 are excluded; the lesson leaves and reads back14pt.',
                                'Source003 has a low-contrast personnel On Scene zero. It is not selected as a legible value; source005 shows the neutral readable result.',
                                'Available unit counts group underlying status categories. The lesson does not equate them with literal Available labels in every detail row.',
                                'Counts and relative update ages are recorded examples, not assertions about current operational availability.'])
    narration = '\n\n'.join(x['narration'] for x in scenes) + '\n'
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=raw.relative_to(S).as_posix(), sha256=RAW_SHA), screenshots=selected)
    review = dict(reviewer='Root', reviewed_at=reviewed_at,
                  actual_originals_personally_viewed=list(LABELS), source_pixels_changed=False,
                  script_reviewed_against_actual_views=True, source_only=True,
                  narration_words=len(narration.split()), audio_or_final_approval_inferred=False,
                  notes=['All seven selected exact original JPEGs personally viewed. Source010 was personally inspected after its fresh-session capture.',
                         'The upper-right plus and gear controls are visible in the board screenshots; the chooser and target settings page are shown separately.',
                         'Show Colors off and4x4 dimensions survived board reload and a fresh app tab. No working font16 change is claimed.',
                         'Counts are deliberately compared with individual unit states and their actual update ages.',
                         'The grouped unit-state explanation was checked against the actual recording app UnitsSummaryWidget.tsx and unit-status.ts source.'])
    if write:
        out = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
        assert not out.exists()
        out.mkdir()
        for file, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest), ('source-review.json', review)]:
            (out / file).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
        (out / 'narration.txt').write_text(narration)
    return dict(lesson_id=NAME, source_ready=True, scenes=len(scenes), actual_screens=len(selected), words=len(narration.split()), written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
