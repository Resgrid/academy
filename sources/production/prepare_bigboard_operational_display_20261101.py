"""Freeze reviewed BigBoard UI evidence and a narration source proposal.

No audio, listening, encoded-frame, publication or playback approval is inferred.
The raw originals and excluded development/unsupported-setting captures remain intact.
"""
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
NAME = 'app-bigboard-operational-display'
RAW = Path('captures/expansion/bigboard-display-20261101')
RAW_SHA = 'f5575d39ab9d2493e95f7c22a2f787df37b4d62da6d6ff6f1f98df7cecf6f518'
REVIEWED_AT = '2026-11-02T05:49:10+00:00'
LABELS = {
    6: ['Resgrid BigBoard', 'Edit', 'Welcome to Your Dashboard', 'Click the + button above to add widgets to your dashboard'],
    7: ['Add Widget', 'Close', 'Personnel', 'Units', 'Calls', 'Map', 'Weather', 'Notes', 'Time', 'Personnel Status Summary', 'Personnel Staffing Summary', 'Units Summary'],
    11: ['Calls', 'Widget Size', 'Width (grid units): 10', 'Height (grid units): 4', 'Save'],
    12: ['Calls Widget', 'Column Order', 'Use arrows to reorder columns', 'ID', 'Priority', 'Name', 'Save'],
    16: ['Calls', 'ID', 'Priority', 'Name', 'Address', 'Timestamp', 'Dispatched', 'DEMO-0001', 'Urgent', 'TRAINING — Warehouse alarm', 'DEMO-0002', 'TRAINING — Community medical standby', 'DEMO-0003', 'TRAINING — Vehicle rescue exercise'],
    17: ['Units', 'Name', 'State', 'Station', 'Type', 'Updated', 'Engine 51', 'Available', 'Squad 3', 'Responding', 'Reserve Engine 51', 'Out of Service', 'TRAINING ONLY - Community van 20261028', 'TRAINING ONLY - Community response vehicle'],
    22: ['Units Widget', 'Use arrows to reorder columns', 'Name', 'State', 'Station', 'Type', 'Timestamp', 'Widget Size', 'Width (grid units): 10', 'Height (grid units): 3', 'Save'],
    23: ['Personnel', 'Column Order', 'Use arrows to reorder columns', 'Name', 'Status', 'Group', 'Staffing', 'Timestamp', 'Roles', 'Save'],
    24: ['Done', 'Time', 'Notes'],
    25: ['Done', 'Time', 'Notes'],
    26: ['Done', 'Personnel', 'Time'],
    29: ['Resgrid BigBoard', 'Edit', 'Personnel', 'Name', 'Status', 'Group', 'Staffing', 'Updated', 'Roles', 'Darren Ritter', 'Standing By', 'Delayed', 'Blake Gallo', 'Unavailable', 'Time'],
    30: ['Resgrid BigBoard', 'Edit', 'Calls', 'ID', 'Priority', 'Name', 'Address', 'Timestamp', 'Dispatched', 'DEMO-0001', 'Urgent', 'TRAINING — Warehouse alarm'],
}

SCENES = [
    ('01', 'Choose what a shared display should answer', [29], ['Resgrid BigBoard', 'Personnel', 'Status', 'Staffing', 'Time'],
     'Resgrid Big Board brings department information into configurable widgets. Here, the Personnel table shows operational status beside staffing, with a clock below it. A duty supervisor can use this display to review readiness during a handover. The same approach can support a security control room, search-and-rescue coordination desk, community paramedicine or mental health response team, wildland contractor, industrial response team, or fire and E M S department. This walkthrough builds a readable board using fictional training data.',
     'Decide which readiness and incident questions your display must answer.'),
    ('02', 'Start with the actual widget chooser', [6, 7], ['Welcome to Your Dashboard', 'Add Widget', 'Calls', 'Units', 'Personnel', 'Time'],
     'Start on the empty dashboard. The message directs you to the plus button in the upper right. Select it to open Add Widget. The chooser includes Calls, Units, Personnel and Time. Add those four widgets for this exercise, choosing each from the menu. The chooser also offers other widget types. Add information for a specific audience and purpose; a coordination desk and a shared briefing display may need different amounts of detail.',
     'Use the plus control to add Calls, Units, Personnel and Time to a training board.'),
    ('03', 'Give the Calls widget enough room', [11], ['Calls', 'Widget Size', 'Width (grid units): 10', 'Height (grid units): 4', 'Save'],
     'Open the settings gear in the header and select Calls. Scroll to Widget Size. In this recorded desktop example, Width is ten grid units and Height is four. Adjust the width and height sliders to give the incident table enough room, then use Save to return to the board. Choose sizes for your actual display. A wider widget gives long incident names and addresses more horizontal space, while additional height makes more rows visible.',
     'Adjust the Calls width and height, save, and check the resulting table.'),
    ('04', 'Bring Priority beside the call identifier', [12], ['Calls Widget', 'Column Order', 'ID', 'Priority', 'Name', 'Save'],
     'In Calls settings, find Column Order and the instruction to use the arrows. Move Priority upward until the first three columns are I D, Priority and Name. Use the up arrow on the Priority row, then Save. This changes where the column appears. It helps a supervisor read an incident identifier and its priority together. We will check the table itself next, because the returned display is the useful confirmation of this setting.',
     'Move Priority after ID and verify that order on the board.'),
    ('05', 'Read the actual incident table', [16], ['Calls', 'ID', 'Priority', 'Name', 'Address', 'Timestamp', 'Dispatched', 'DEMO-0001', 'Urgent'],
     'The Calls table now begins with I D, Priority and Name. The warehouse-alarm exercise shows Urgent, while the community medical standby and vehicle-rescue exercise show Routine. Address, Timestamp and Dispatched provide more context across each row. Read these values together when comparing work. The Dispatched column lists dispatched recipients; this screen does not by itself verify that every recipient accepted the assignment or arrived at the incident. Use the relevant response and operational views for those checks.',
     'Find one training incident and read its identifier, priority, address and dispatched recipients.'),
    ('06', 'Set the Units table order and dimensions', [22], ['Units Widget', 'Name', 'State', 'Station', 'Type', 'Timestamp', 'Widget Size', 'Save'],
     'Open the gear again and select Units Widget. In the column-order controls, move State immediately after Name. Keep Station, Type and Timestamp after those columns for this example. The Widget Size controls below give this table a width of ten and a height of three grid units. Save and inspect the result. Putting the resource name beside its state makes it easier to scan which vehicle or team needs attention during a briefing.',
     'Place State after Name, choose readable dimensions, and save.'),
    ('07', 'Compare resource states and update age', [17], ['Units', 'State', 'Updated', 'Available', 'Responding', 'Out of Service', 'TRAINING ONLY - Community response vehicle'],
     'On the resulting Units table, Engine fifty-one is Available, Squad three is Responding, and Reserve Engine fifty-one is Out of Service. The community-response vehicle demonstrates that the table can include resources beyond fire apparatus. A security patrol vehicle or industrial response resource can be organized using the same fields. Read Updated as well as State. Several fictional exercise entries are days old, so a displayed state alone is not evidence of a fresh readiness report.',
     'Compare three unit states and check their displayed update age.'),
    ('08', 'Choose a personnel column order', [23], ['Personnel', 'Column Order', 'Name', 'Status', 'Group', 'Staffing', 'Timestamp', 'Roles', 'Save'],
     'Select Personnel in the configuration tabs and find Column Order. For this example, place Status immediately after Name, followed by Group and Staffing, then Timestamp and Roles. Use the arrows on each row to move the columns, then Save. This arrangement brings an individual and their operational status together while keeping team assignment, staffing and qualifications visible elsewhere in the same row. Choose a sequence that your supervisors can read consistently during handover.',
     'Set the personnel column sequence and compare it with the displayed table.'),
    ('09', 'Distinguish personnel status from staffing', [29], ['Personnel', 'Status', 'Staffing', 'Updated', 'Roles', 'Darren Ritter', 'Delayed', 'Blake Gallo', 'Unavailable', 'Time'],
     'The Personnel table shows Status and Staffing as separate columns. In this exercise, Darren Ritter has Standing By under Status and Delayed under Staffing. Blake Gallo has Standing By and Unavailable. These are different pieces of information, so read both before deciding that someone is ready for work. Roles and Group add organizational context, and Updated provides the displayed age of the entry. The Time widget below supplies a visible clock alongside the readiness information.',
     'Read one person’s Status and Staffing separately and check the update age.'),
    ('10', 'Enter edit mode and find the widget controls', [24], ['Done', 'Time', 'Notes'],
     'Return to the dashboard and select Edit in the header. The button changes to Done, and widget headings show a grip and a red removal control. A temporary Notes widget has been added beside Time for this layout exercise. The grip is the place to begin moving the widget. Check the heading before using a removal control, so you change the intended panel rather than another widget on a crowded display.',
     'Enter Edit and identify the grip and removal control on the temporary Notes widget.'),
    ('11', 'Move the temporary widget', [25], ['Done', 'Time', 'Notes'],
     'Drag the temporary Notes widget by its heading grip to the right. The resulting view shows Notes farther across the board, with Time remaining on the left. This is a layout change. It does not change the department note itself. Use the same placement check when arranging a shared display: confirm the final location of the panel and make sure important information is still visible at the distance from which people will read it.',
     'Move a temporary widget and inspect its resulting position.'),
    ('12', 'Remove the temporary panel and finish editing', [26], ['Done', 'Personnel', 'Time'],
     'Select the red removal control on the temporary Notes widget. That panel disappears, and the board returns to four widgets: Calls, Units, Personnel and Time. The pictured lower part of the board shows Personnel and Time remaining. Select Done to leave edit mode. Removing this display widget does not delete the underlying department note. Keep only the panels needed for this particular display, then check that its important tables remain readable.',
     'Remove only the temporary Notes widget and select Done.'),
    ('13', 'Reload and verify the saved display', [30, 29], ['Calls', 'ID', 'Priority', 'Name', 'Personnel', 'Status', 'Staffing', 'Time'],
     'Reload Big Board to check the saved result. Calls still begins with I D, Priority and Name. Scroll down to confirm that Personnel keeps its chosen sequence and that Time remains on the board. In this example, the larger tables require scrolling. For a wall display, choose a smaller set of panels that fits the screen and verify it on the actual monitor. For an interactive coordination desk, decide which tables staff will scroll through during routine work.',
     'Reload, compare the returned columns and widgets, and verify readability on the intended screen.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from verify_capture_evidence import _image_dimensions, _Validator
    raw_path = S / RAW / 'manifest.json'
    assert sha(raw_path) == RAW_SHA
    raw = json.loads(raw_path.read_text())
    numbered = {int(row['id'][:3]): row for row in raw}
    selected = []
    for number, labels in LABELS.items():
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        actual = _image_dimensions(S / row['file'])
        if actual != (row['width'], row['height']):
            row['browser_viewport'] = dict(width=row['width'], height=row['height'])
            row['width'], row['height'] = actual
        dom = S / RAW / (row['id'] + '.txt')
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[],
                   dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom))
        row['capture_review'] = dict(reviewer='Root', passed=True, reviewed_at=REVIEWED_AT,
                                    sha256=row['sha256'], method='Root personally viewed this exact stored original using view_image. Pixels unchanged; only readable foreground labels retained.')
        check = _Validator(S)
        check.observations(row, row['id'])
        assert not check.issues, check.issues
        selected.append(row)
    scenes = [dict(id=i, title=t, route='/configure' if refs[0] in (11, 12, 22, 23) else '/home',
                   capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the actual setting, chooser, widget, edit control or reloaded result at the spoken instruction.',
                   required_labels=labels, narration=speech, practice=practice)
              for i, t, refs, labels, speech, practice in SCENES]
    lesson = dict(id=NAME, title='Big Board: build and verify an operational display', app='BigBoard',
                  summary='Add operational widgets, choose readable dimensions, reorder call, unit and personnel columns, move and remove a temporary panel, and verify the saved board after reload.',
                  audience=['Department administrators', 'Duty supervisors', 'Dispatch and coordination teams', 'Department trainers'],
                  prerequisites=['An authorized signed-in BigBoard session in a fictional training department.',
                                 'Existing calls, personnel, units and a training note for a reversible display exercise.'],
                  scenes=scenes, sector_examples=[
                      dict(sector='Security', scenario='Review patrol resources and personnel readiness on a control-room display.'),
                      dict(sector='Search and rescue', scenario='Read team and resource readiness together during coordination.'),
                      dict(sector='Community response', scenario='Review community paramedicine or mental health team staffing alongside active work.'),
                      dict(sector='Wildland', scenario='Use consistent resource and personnel columns during contractor handovers.'),
                      dict(sector='Industrial', scenario='Review resource availability and update age during a response-team briefing.'),
                      dict(sector='Fire/EMS', scenario='Compare apparatus states, incident priority and personnel readiness.')],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; generated speech, complete listening review, cue correspondence, encoded-frame review and actual browser playback remain required.',
                                'No call dispatch, response acceptance, current device GPS, timed unit alert, weather result or cross-device preference synchronization is demonstrated.',
                                'Clock-format, personnel-filter and generic font controls are not presented as working display effects in this build.',
                                'This desktop example uses scrolling tables; it is not a demonstration of four full tables fitting on a wall monitor.'])
    narration = '\n\n'.join(row['narration'] for row in scenes) + '\n'
    reasons = {
        8: 'Default-size table is crowded and a development warning is visible. Not selected learner footage.',
        14: 'Font value changed in the generic configuration store; corresponding widget text did not demonstrate that display change.',
        15: '24-hour setting saves but the displayed clock remains 12-hour. No working-format claim.',
        18: 'Raw filename mentions 24-hour, but the actual clock is 12-hour. Use clean source029.',
        20: 'Hide Unavailable saves in the generic settings but the actual personnel table still contains unavailable people. No successful-filter claim.',
        27: 'Development warning overlays the reloaded board. Replaced by original clean capture030 after normal UI dismissal.',
        28: 'Development warning overlays the clock. Replaced by original clean capture029 after normal UI dismissal.',
    }
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=raw_path.relative_to(S).as_posix(), sha256=RAW_SHA),
                    screenshots=selected, excluded_sources=[dict(id=row['id'], sha256=row['sha256'], reason=reasons.get(int(row['id'][:3]), 'Outside this bounded display-layout lesson.')) for row in raw if int(row['id'][:3]) not in LABELS])
    review = dict(reviewer='Root', reviewed_at=REVIEWED_AT, actual_originals_personally_viewed=list(LABELS),
                  source_pixels_changed=False, script_reviewed_against_actual_views=True, narration_words=len(narration.split()),
                  source_only=True, audio_or_final_approval_inferred=False,
                  notes=['Source026 raw identifier says clock moved, but the clock remained on the left. It proves temporary Notes removal only. Only source025 proves the Notes movement.',
                         'Source029/030 follow a genuine reload and normal UI dismissal of the React development warning; no pixels were erased, masked or generated.',
                         'The Notes body contains literal HTML from the existing fixture. The lesson discusses only the temporary widget heading, position and removal.',
                         'Column order and dimensions are demonstrated with actual returned views. No success is inferred for unsupported format, generic font or availability-filter changes.'])
    if write:
        target = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
        assert not target.exists()
        target.mkdir()
        for filename, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest), ('source-review.json', review)]:
            (target / filename).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
        (target / 'narration.txt').write_text(narration)
    return dict(source_ready=True, lesson_id=NAME, scenes=len(scenes), actual_screens=len(selected), words=len(narration.split()), written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
