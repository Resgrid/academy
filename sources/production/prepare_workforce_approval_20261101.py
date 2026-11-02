"""Prepare the executed workforce approval source without inferring audio/video reviews."""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'core-workforce-work-entry-approval'
RAW = Path('captures/expansion/core-workforce-approval-20261101')
RAW_SHA = '1d88b2aba05ce072ec2e1b229329a0140468c5efc284c1e86a32755843867314'
REVIEWED_AT = '2026-11-02T06:12:20+00:00'
LABELS = {
    1: ['Work entries', 'Add work entry', 'Date', 'Worker', 'Hours', 'Hours type', 'Establishment', 'Context', 'Approved payroll cost', 'Approved', 'Matthew Casey', '2.00', 'No'],
    2: ['Add work entry', 'Worker *', 'Matthew Casey', 'Date *', 'Hours *', '2026-11-01', '1.25', 'Hours type', 'Standby', 'Establishment', 'Work mode', 'Non-remote'],
    3: ['Approved payroll cost', 'The actual from the payroll system; when present it replaces the estimate for this day.', 'External source', 'External id', 'Approved', 'Save', 'Cancel'],
    4: ['Work entries', 'Saved.', 'Date', 'Worker', 'Hours', 'Hours type', 'Context', 'Approved', '2026-11-01', 'Matthew Casey', '1.25', 'Standby', 'TRAINING ONLY - Approval exercise', 'No'],
    5: ['Approved payroll cost', 'External source', 'External id', 'Approved', 'Save', 'Cancel'],
    7: ['Work entries', 'Date', 'Worker', 'Hours', 'Hours type', 'Establishment', 'Context', 'Approved payroll cost', 'Approved', '2026-11-01', 'Matthew Casey', '1.25', 'Standby', 'TRAINING ONLY - Approval exercise', 'Yes', '2026-10-28', '2.00', 'No'],
    10: ['Work entries', 'Filter', '2026-11-01', 'Matthew Casey', '1.25', 'Standby', 'TRAINING ONLY - Approval exercise', 'Yes'],
    11: ['Work entries', 'Filter', 'Date', 'Worker', 'Hours', 'Hours type', 'Establishment', 'Context', 'Approved payroll cost', 'Approved', '2026-11-01', 'Matthew Casey', '1.25', 'Standby', 'TRAINING ONLY - Approval exercise', 'Yes'],
}
SCENES = [
    ('01', 'Find the work-entry approval column', [1], ['Work entries', 'Worker', 'Hours', 'Hours type', 'Approved', 'No', 'Add work entry'],
     'Open Workforce and choose Work entries. The table separates the worker, hours, hours type, establishment, context and approval status. In this training department, the existing two-hour entry shows No under Approved. We will create a separate example and follow it from an unapproved save to a verified approved result. An administrator needs the appropriate workforce access for these controls. The earlier example remains unchanged.',
     'Identify the Approved column and choose a separate fictional entry for practice.'),
    ('02', 'Prepare a separate standby entry', [2], ['Add work entry', 'Matthew Casey', 'Date *', 'Hours *', '1.25', 'Hours type', 'Standby', 'Establishment'],
     'Select Add work entry. In the form, the worker is Matthew Casey. Set Date to November first, twenty twenty-six, enter one point two five Hours, and choose Standby under Hours type. Select the training establishment appropriate to the example. These fields describe this individual work entry. Check the worker, date, quantity and hours type together before continuing, so the approval will refer to the intended row.',
     'Prepare a fictional worker, date, hours quantity, hours type and establishment.'),
    ('03', 'Save the entry with approval clear', [3, 4], ['External source', 'External id', 'Approved payroll cost', 'Approved', 'Save', 'Saved.', 'TRAINING ONLY - Approval exercise', 'No'],
     'Scroll to the bottom of the form. External source and External id provide references for this example. Leave the Approved checkbox clear for the first save. The Approved payroll cost field is also blank in this exercise. Select Save, then find the new row with the context TRAINING ONLY, Approval exercise. Its date, one point two five hours and Standby type are visible, and Approved still reads No. This returned row confirms the initial saved state.',
     'Save the example unapproved and verify the returned row instead of relying only on the form.'),
    ('04', 'Select approval for the intended row', [4, 5], ['TRAINING ONLY - Approval exercise', 'Approved', 'Save'],
     'Use the pencil control at the right of the new exercise row to reopen it. Scroll to Approved and select the checkbox. In this view, the table on the left still shows the earlier saved value, No, while the form checkbox on the right is selected. The form change still needs to be saved. Confirm that this is the intended training entry, then select Save to store its approval status.',
     'Reopen the correct row, select Approved, and save the change.'),
    ('05', 'Reload and compare the saved result', [7], ['2026-11-01', 'Matthew Casey', '1.25', 'Standby', 'TRAINING ONLY - Approval exercise', 'Approved', 'Yes', 'No'],
     'Reload the Work entries page. The new exercise row now shows Yes under Approved. The worker, date, one point two five hours and Standby type remain visible on that same row. The earlier two-hour entry still shows No. Compare the complete row when reviewing an approval, rather than reading a Yes value without its worker and date. The Approved payroll cost column remains blank for this software exercise.',
     'Reload and verify that the intended row changed to Yes while the earlier entry stayed No.'),
    ('06', 'Filter to the work date', [10, 11], ['Filter', '2026-11-01', 'TRAINING ONLY - Approval exercise', 'Yes'],
     'Use the two date fields above the table to focus the review. Set both boundaries to November first, twenty twenty-six, then select Filter. The returned table contains the single exercise entry for that date, including its Standby hours, context and Yes approval value. Changing the date fields alone does not refresh this table; the Filter button applies the selected range. Check those boundaries when a saved entry seems to be missing from the list.',
     'Apply a single-day range and verify the matching entry in the returned table.'),
    ('07', 'Use consistent review responsibilities', [11], ['Work entries', 'Date', 'Worker', 'Hours', 'Hours type', 'Context', 'Approved', 'Yes'],
     'This workflow gives a department a visible saved approval status for a particular work entry. A security supervisor can review patrol standby time, a search-and-rescue coordinator can review an exercise entry, and a community paramedicine or mental health response team can review its recorded work. Wildland contractors, industrial response teams, and fire and E M S departments can use the same worker, date, hours type and context checks. Agree who reviews entries, then verify the saved result in the appropriate date range.',
     'Define who reviews entries for your department and which row details they must check.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from verify_capture_evidence import _image_dimensions, _Validator
    path = S / RAW / 'manifest.json'
    assert sha(path) == RAW_SHA
    rows = json.loads(path.read_text())
    numbered = {int(row['id'][:3]): row for row in rows}
    selected = []
    for number, labels in LABELS.items():
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        dimensions = _image_dimensions(S / row['file'])
        if dimensions != (row['width'], row['height']):
            row['browser_viewport'] = dict(width=row['width'], height=row['height'])
            row['width'], row['height'] = dimensions
        dom = S / RAW / (row['id'] + '.txt')
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[],
                   dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom))
        row['capture_review'] = dict(reviewer='Root', passed=True, reviewed_at=REVIEWED_AT,
                                    sha256=row['sha256'], method='Root personally viewed this exact stored original using view_image. Original pixels unchanged; clipped reference values excluded.')
        check = _Validator(S)
        check.observations(row, row['id'])
        assert not check.issues, check.issues
        selected.append(row)
    scenes = [dict(id=i, title=t, route='/User/Workforce/WorkEntries', capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the actual work-entry form, approval checkbox, saved row or applied date filter as discussed.',
                   required_labels=labels, narration=speech, practice=practice)
              for i, t, refs, labels, speech, practice in SCENES]
    lesson = dict(id=NAME, title='Approve a workforce work entry and verify the saved result', app='Core',
                  summary='Create a separate standby-hours example, save it unapproved, select and save approval, verify the returned row after reload, and apply a single-day filter.',
                  audience=['Workforce administrators', 'Authorized department supervisors', 'Department trainers'],
                  prerequisites=['Authorized workforce view and management access in a fictional training department.',
                                 'An existing worker, employment and training establishment.'],
                  scenes=scenes, sector_examples=[dict(sector=sector, scenario=text) for sector, text in [
                      ('Security', 'Review the worker, date, hours type and context of a patrol standby entry.'),
                      ('Search and rescue', 'Use a training entry to practice supervisor review without changing the earlier example.'),
                      ('Community response', 'Review work-entry details for a community paramedicine or mental health response team.'),
                      ('Wildland', 'Apply a consistent date and context review to contractor work entries.'),
                      ('Industrial', 'Compare work-entry approval with the recorded worker, quantity and context.'),
                      ('Fire/EMS', 'Verify the saved approval of a department standby-hours exercise.')]],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; generated speech, complete listening, caption correspondence, actual encoded frames and live playback remain required.',
                                'Only one fictional entry is created and its approval flag changed. No payroll amount, compensation profile, cost run, payroll payment, annual report or external integration is demonstrated.',
                                'The earlier two-hour entry is preserved. External reference inputs are clipped in the narrow form and their complete values are not narrated as readable.'])
    narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=str(path.relative_to(S)), sha256=RAW_SHA), screenshots=selected,
                    excluded_sources=[dict(id=row['id'], sha256=row['sha256'], reason='Additional raw readback; not selected for this bounded lesson.') for row in rows if int(row['id'][:3]) not in LABELS])
    review = dict(reviewer='Root', reviewed_at=REVIEWED_AT, actual_originals_personally_viewed=list(LABELS), source_pixels_changed=False,
                  script_reviewed_against_actual_views=True, source_only=True, narration_words=len(narration.split()), audio_or_final_approval_inferred=False,
                  notes=['Native date fields paint 11/01/2026; their DOM-backed canonical value is 2026-11-01. These are the same recorded date.',
                         'Source003 checkbox is clear. Source005 checkbox is visibly selected while the left table still says No. Source007 is the actual reloaded Yes result.',
                         'Source010 shows entered filter bounds before submission; source011 is the returned filtered table. No result is inferred from typed fields alone.',
                         'No real payroll cost or protected value was entered or exposed.'])
    if write:
        dest = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
        assert not dest.exists()
        dest.mkdir()
        for file, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest), ('source-review.json', review)]:
            (dest / file).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        (dest / 'narration.txt').write_text(narration)
    return dict(source_ready=True, lesson_id=NAME, scenes=len(scenes), actual_screens=len(selected), words=len(narration.split()), written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
