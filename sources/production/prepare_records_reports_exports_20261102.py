"""Freeze actual Records reporting screens and editable narration; no video approval."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys

S = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S.parent / 'scripts'))
from verify_capture_evidence import _image_dimensions

LESSONS = {
    'reports': dict(
        name='core-records-saved-reports', raw='core-saved-reports-20261102',
        title='Build, validate and run a saved Records report',
        summary='Choose a definition and columns, validate a finalized-record filter, download CSV, and add a grouped count.',
        excluded={7: 'Save is clipped by the fixed footer; use the complete controls in screen 005.'},
        scenes=[
            ('Find saved reports', [1, 2], ['Reports', 'Saved reports', 'New report'],
             'From Records, open Reports and select Saved reports. This is where you keep a reusable report instead of rebuilding the same query each time. The page explains that a saved report queries one definition, can group or aggregate its records, and can export the results to C S V. Results still respect record visibility and restricted fields. Select New report to begin a separate fictional community coordination report.'),
            ('Choose the definition and fields', [3, 4, 6], ['Definition', 'Report name', 'Columns', 'record.number', 'record.state', 'Summary'],
             'Give the report a recognizable name and description. Select the definition that owns the records you want to review. Here it is the training community software exercise. The Columns panel then offers record fields and that definition’s detail fields. Select record dot number, record dot state, and Summary. These three choices become the three result columns. Leave Notes unselected for this example. A clear report name helps supervisors choose the right recurring review.'),
            ('Set the sort and keep detail rows', [4], ['Sort by', 'record.number', 'Descending', 'Group by', 'Aggregates (JSON)'],
             'Set Sort by to record dot number and check Descending. The first version is a detail report, so leave Group by and Aggregates empty. This makes the newest training number appear first in the recorded result. Sorting determines the order of rows; grouping is a separate decision. Later we will edit this same report to count records by state without replacing the detail columns.'),
            ('Filter finalized records and limit the result', [5], ['Filters (JSON)', 'Max rows', 'Include drafts', 'Include restricted fields'],
             'Scroll to Filters. This example uses a J S O N array with FieldKey set to record dot state, Operator set to Equals, and Value set to Finalized. Match the quoted text and brackets shown in the form. The inline example and schema help explain the expected structure. Set Max rows to twenty-five. Leave Include drafts and Include restricted fields unchecked. Leave Version mappings empty for this exercise. These choices keep this report focused on a small, permitted set of finalized records.'),
            ('Validate before saving', [5, 6, 5, 9], ['Validate', 'The report is valid.', 'Save', 'Report saved.'],
             'Select Validate before saving. The page returns with The report is valid above the prepared settings and selected columns. Validation checks the report definition; it is not a result count and does not replace Save. Return to the bottom controls and select Save. The Saved reports page now shows Report saved, the report name, its definition, three columns, and the Run action. That saved row is the first readback that the reusable report exists.'),
            ('Run and download the detailed result', [9, 10], ['Run', 'Rows (2 / 2)', 'Record number', 'State', 'Summary', 'CSV'],
             'Select Run on the saved row. The result shows two of two rows, with Record number, State and Summary as configured. Both records are Finalized, and the larger training number is first. Compare those values with the purpose of the report before distributing its output. Use the C S V button on this result page to download the data. In this exercise the downloaded file contains the same three headers and the same two fictional records shown here.'),
            ('Reopen and add a grouped count', [10, 11, 12], ['Edit', 'Group by', 'record.state', 'Aggregates (JSON)', 'Count'],
             'Select Edit and review the persisted settings. The three column choices and descending record-number sort are still present. Set Group by to record dot state. In Aggregates, enter a J S O N array whose object has Aggregate set to Count, exactly as the form’s Count example shows. This asks a different question: how many matching records are in each state? The original detail columns remain selected.'),
            ('Validate, save and rerun the changed report', [13, 5, 14, 15], ['The report is valid.', 'Save', 'Run', 'Groups', 'Finalized', 'Count', 'Rows (2 / 2)'],
             'Validate the changed report and confirm The report is valid. Use the same bottom Save control, then run the saved report again. The updated index identifies Group by record dot state and shows a Last run time. The new result has a Groups section: Finalized has a count of two. The detail section still shows the same two rows. Check both sections so that the summary count can be traced back to its records.'),
            ('Apply the review to your department', [15], ['Groups', 'Rows (2 / 2)', 'Summary'],
             'Use this pattern for the records your department actually maintains. A community paramedicine or mental health response team can review completed coordination records. Search-and-rescue teams can summarize activity forms, security departments can review service records, and wildland contractors or industrial emergency teams can track their operational paperwork. Fire and E M S departments can use the same controls. Choose the appropriate definition, select only needed fields, validate the settings, and verify the detail behind each grouped total.')]),
}

LESSONS['exports'] = dict(
    name='core-records-export-templates', raw='core-export-templates-20261102',
    title='Configure a Records CSV export and verify its runs and schedule',
    summary='Build a six-column training-record export, verify a manual CSV, inspect the next scheduled run, and restore manual operation.',
    excluded={4: 'Transitional viewport contains unnecessary blank space.', 8: 'Save is not visible. Screen 020 replays the same unsaved creation settings and clearly shows Save.'},
    scenes=[
        ('Open report exports', [1, 2, 3], ['Manage', 'Report exports', 'New export'],
         'From Records, open Manage and select Report exports. This area defines a repeatable output file: its columns, format and scope. The page also explains that exports can be attached to a Workflow step or placed on a schedule. This lesson configures and checks the file locally; it does not send an email or upload anything to an outside agency. Select New export to prepare a separate training-record handoff.'),
        ('Name the export and give it a stable key', [21], ['Export name', 'Key', 'Description'],
         'Enter a meaningful Export name and a stable Key. The example is Training record handoff, with an academy training handoff key. The help requires lower-case letters, digits and hyphens, and explains that a Workflow step or agency import may rely on this key. Keep that relationship in mind before changing names in a live integration. Add a description of exactly what this file is intended to contain. Here the description explicitly limits the exercise to fictional training-record identity, state and dates.'),
        ('Choose the scope and CSV layout', [21, 20], ['Format', 'CSV', 'Scope', 'Training', 'File name', 'Delimiter', 'Include a header row', 'Enabled'],
         'Use C S V as the Format, and choose the window scope for finalized records. Check Training under Record definitions. The help says that leaving every definition unchecked would export all definitions, so select the intended scope deliberately. For File name, enter the template token followed by the date token, as shown. Keep the comma Delimiter, include a header row, and leave Enabled checked. These settings define the file layout that the receiving process will need to recognize.'),
        ('Choose six specific columns', [5], ['Columns', 'Record number', 'Record type', 'State', 'Duration (minutes)', 'Finalized (UTC)', 'Course (records)'],
         'Review Columns rather than accepting an unnecessarily broad output. Select Record number, Record type, State, Duration in minutes, Finalized in U T C, and Course from records. The screenshot shows those six checks. Other identity, participant and incident fields remain unselected in this example. Choose the smallest useful set for your actual handoff and agree its meaning with the recipient. A consistent set of fields makes repeated exports easier to compare and import.'),
        ('Review the narrative and restricted-content controls', [6], ['Include narrative and personal detail (Tier 2)', 'Include restricted sections (Tier 1)'],
         'Scroll through the narrative and restricted sections before saving. This exercise leaves all their column checkboxes unselected. It also leaves Include narrative and personal detail, Include restricted sections, and the acknowledgement about sending that content outside Resgrid unchecked. These are separate controls beneath the column catalog. Review them together with the selected columns and the intended Workflow destination when planning an actual integration. Our local file contains none of those narrative or restricted fields.'),
        ('Set the manual window and verify the saved template', [7, 20, 9, 10], ['Schedule', 'Window (days)', '30', 'Save', 'The export was saved.'],
         'For the first test, use No schedule and set Window to thirty days. The help explains that zero instead uses the schedule period ending at the run. Select Save after reviewing the prepared settings. The saved template can be reopened with the same format, Training selection and thirty-day window. The Report exports index confirms The export was saved and lists the window scope with No schedule. Saving the template establishes the configuration; it does not prove that the resulting file contains the expected records.'),
        ('Run locally and inspect the recorded result', [10, 11, 12], ['Runs', 'Run now', 'Manual', 'Records', 'Bytes', 'Checksum', 'Download'],
         'Open Runs for the template, then select Run now. The page says this renders the export for checking before an agency sees it, and audits every included record as an export. The completed run shows a Manual trigger, two records, three hundred sixteen bytes, a checksum and a Download link. Download the file and compare its headers and rows with the intended handoff. The retained exercise file has the six selected headers and two training records, including one amended record in this finalized-record window.'),
        ('Prepare and save a daily schedule', [13, 14, 15], ['Schedule', 'Daily', 'Hour (department local time)', 'Window (days)', 'Save'],
         'Return to Edit and change Schedule to Daily. Set Hour to six in department local time and keep the thirty-day window. The form also contains weekday and day-of-month controls for other schedule choices, but this exercise saves the Daily choice. Review the hour and window together, then select Save. Changing a schedule is a configuration step; the next screen will confirm the stored next-run time. We do not claim that an automatic run has already occurred.'),
        ('Verify next run and restore manual operation', [16, 17, 18, 19], ['Next run', '11/03/2026 06:00:00', 'Save', 'Schedule'],
         'After saving, Next run shows November third at six in the morning. The index independently shows Daily and the same next-run value. That is the saved scheduling result for this dated training exercise. To leave the department without an active timer, reopen the template, choose No schedule, and select Save again. Reopening now shows No schedule with a dash for Next run. Verify that stored result instead of assuming an unsaved selection stopped the schedule.'),
        ('Use a checked export for your department’s handoff', [19, 12], ['Schedule', 'Runs', 'Download'],
         'Use the same configuration and checking process across department types. Search-and-rescue teams, security companies, wildland contractors and industrial emergency teams can standardize their permitted record handoffs. Community paramedicine and mental health response teams can define an appropriate coordination or training export, as can fire and E M S departments. Start with the right definition and columns, check a manual file, and verify the schedule before relying on it. Delivery through a Workflow is a separate operation that must be configured and tested for the intended recipient.')])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(key):
    cfg = LESSONS[key]
    raw = S / 'captures/expansion' / cfg['raw']
    dest = S / 'expansion/plans' / (cfg['name'] + '-source-20261102')
    if dest.exists():
        raise SystemExit('Source freeze already exists; preserve it and create a revised dated version.')
    data = json.loads((raw / 'manifest.json').read_text())
    numbered = {int(row['id'][:3]): row for row in data}
    used = sorted({n for _, nums, _, _ in cfg['scenes'] for n in nums})
    assert not set(used) & set(cfg['excluded'])
    now = datetime.now(timezone.utc).isoformat()
    screens = []
    for number in used:
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        width, height = _image_dimensions(S / row['file'])
        row.setdefault('css_viewport', dict(width=row['width'], height=row['height']))
        row.update(width=width, height=height)
        dom = raw / (row['id'] + '.txt')
        row.update(dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom),
                   eligible_for_lesson=True, review_status='actual_source_contact_sheet_reviewed',
                   capture_review=dict(reviewer='Root', passed=True, reviewed_at=now, sha256=row['sha256'],
                                       method='Root personally inspected this original browser screenshot on the full-size source contact sheets. No screenshot pixels were changed.'))
        screens.append(row)
    scenes = [dict(id=f'{i:02}', title=title, route=cfg.get('route', '/User/Records'),
                   capture_refs=[numbered[n]['id'] for n in refs], required_labels=labels,
                   narration=speech, practice=title,
                   capture_intent='Show each actual control and distinguish prepared, validated, saved and executed states.')
              for i, (title, refs, labels, speech) in enumerate(cfg['scenes'], 1)]
    lesson = dict(id=cfg['name'], title=cfg['title'], app='Core', summary=cfg['summary'],
                  audience=cfg.get('audience', ['Department administrators', 'Records managers', 'Department supervisors']),
                  prerequisites=cfg.get('prerequisites', ['Authorized Records administration and a separate fictional training department.',
                                 'Existing permitted finalized records for the selected definition.']),
                  scenes=scenes, candidate_only=True, export_ready=False, publication_approved=False,
                  source_files=[], sector_examples=[dict(sector=sector, scenario=cfg.get('sector_scenario', 'Choose the appropriate department record definition and verify the matching output.'))
                      for sector in ['Community paramedicine and mental health response', 'Search and rescue', 'Security', 'Wildland', 'Industrial emergency response', 'Fire/EMS']],
                  scope_limits=['Source proposal only; actual speech generation, listening, complete correspondence, encoded-frame review and playback qualification remain required.',
                                cfg.get('scope', 'This exercise uses fictional records and demonstrates only the saved-report and CSV operations actually recorded.')])
    manifest = dict(schema_version=1, id=cfg['name'], screenshots=screens,
                    raw_manifest=dict(file=(raw/'manifest.json').relative_to(S).as_posix(), sha256=sha(raw/'manifest.json')),
                    excluded_sources=[dict(id=row['id'], sha256=row['sha256'], reason=cfg['excluded'].get(int(row['id'][:3]), 'Outside this bounded source selection.'))
                                      for row in data if int(row['id'][:3]) not in used])
    dest.mkdir(parents=True)
    for file, obj in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest),
                      ('source-review.json', dict(reviewer='Root', reviewed_at=now, actual_images_reviewed=[r['id'] for r in screens],
                                                 source_pixels_unchanged=True, final_video_approval_inferred=False))]:
        (dest/file).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
    text='\n\n'.join(scene['narration'] for scene in scenes)+'\n'
    (dest/'narration.txt').write_text(text)
    print(json.dumps(dict(lesson=cfg['name'], scenes=len(scenes), screens=len(screens), words=len(text.split()))))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=LESSONS)
    freeze(parser.parse_args().lesson)
