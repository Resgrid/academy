"""Freeze executed Core status timers and Big Board acknowledgement/mute screens."""
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
NAME = 'app-bigboard-unit-status-timers'
RAW = Path('captures/expansion/bigboard-unit-status-alerts-20261101')
RAW_SHA = '0f3504de83791eae5da86ecb592942000189c854940e91e66f86c9cba4fc43b2'
ACK_NOTE = 'TRAINING ONLY - Timer review practice; verify the unit state with the exercise coordinator.'
MUTE_NOTE = 'TRAINING ONLY - Practice a fifteen-minute mute; no operational response is being suppressed.'
LABELS = {
    1: ['Resgrid BigBoard', 'Add Widget', 'Unit Alerts'],
    2: ['Department Settings', 'Operations', 'Mapping and BigBoard Settings'],
    3: ['Unit Alerts', 'No status timers configured'],
    4: ['Unit Status Timers', 'Status', 'Warn after (minutes)', 'Alert after (minutes)', 'Dispatched', 'Responding', 'En Route', 'On Scene', 'Returning', '0'],
    5: ['Unit Status Timers', 'Warn after (minutes)', 'Alert after (minutes)', 'Responding', '2', '4'],
    6: ['Reason when acknowledging', 'Required for warnings and alerts', 'Save'],
    7: ['Unit Status Timers', 'Warn after (minutes)', 'Alert after (minutes)', 'Responding', '2', '4'],
    8: ['Reason when acknowledging', 'Required for warnings and alerts', 'Save'],
    9: ['Unit Alerts', 'Squad 3', 'Responding · Firehouse 51', '182h 18m'],
    10: ['Unit status alert', 'Squad 3', 'Reason (required)', 'A reason is required before this alert can be acknowledged or muted.', 'Mute for', 'Until status changes', '15 min', '30 min', '60 min', 'Acknowledge', 'Mute', 'Cancel'],
    11: ['Unit status alert', 'Squad 3', 'Reason (required)', ACK_NOTE, 'Acknowledge'],
    12: ['Unit Alerts', 'Squad 3', 'Responding · Firehouse 51'],
    13: ['Unit status alert', 'Squad 3', 'Seen by Wallace Boden', ACK_NOTE, 'Clear acknowledgement'],
    14: ['Unit Alerts', 'Widget Size', 'Width (grid units): 4', 'Height (grid units): 3', 'Save'],
    15: ['Unit Alerts', 'Squad 3', 'Responding · Firehouse 51', 'Seen by Wallace Boden: ' + ACK_NOTE],
    16: ['Unit status alert', 'Squad 3', 'Reason (required)', 'Mute for', '15 min', MUTE_NOTE, 'Mute'],
    17: ['Unit Alerts', 'Muted (1)'],
    18: ['Unit Alerts', 'Muted (1)', 'Squad 3', 'Responding · Firehouse 51', 'Seen by Wallace Boden: ' + MUTE_NOTE],
    19: ['Unit status alert', 'Squad 3', 'Seen by Wallace Boden', 'Muted until 12:56 AM', MUTE_NOTE, 'Clear acknowledgement'],
    20: ['Unit Alerts', 'Squad 3', 'Responding · Firehouse 51', '182h 24m'],
    21: ['Unit Alerts', 'Widget Size', 'Width (grid units): 4', 'Height (grid units): 3', 'Save'],
}
SCENES = [
    ('01', 'Add Unit Alerts and understand the empty state', [1, 3],
     'Unit Alerts helps a coordination team find units that have remained in a timed status longer than the department expects. In Big Board, use the plus icon and choose Unit Alerts from Add Widget. Scroll to the new panel. This department initially shows No status timers configured. That message describes the missing timer configuration; it does not establish that every unit has reported promptly. The thresholds are department settings managed in the Core website.'),
    ('02', 'Find the department timer table', [2, 4],
     'In Core, open Department Settings, choose Operations, then Mapping and BigBoard Settings. Scroll to Unit Status Timers. The table separates Status, Warn after in minutes, and Alert after in minutes. Each displayed status has its own row, including Dispatched, Responding, En Route and On Scene. Initially, both columns are zero throughout this training table. The helper text explains that leaving both at zero times nothing. Choose values that fit your department\'s reporting process.'),
    ('03', 'Set the fictional Responding thresholds', [5],
     'For this software exercise, enter two under Warn after and four under Alert after on the Responding row. Leave the other rows unchanged. These are demonstration values, not a recommended response standard. The two columns allow the department to distinguish a warning interval from a later alert interval for the same status. Review the row label and both minute values before saving, so the timer applies to the intended operational meaning.'),
    ('04', 'Require a reason and read back the saved settings', [6, 7, 8],
     'Below the table, set Reason when acknowledging to Required for warnings and alerts. The help explains that this policy applies when acknowledging or muting a status timer alert. Select Save. Reload Mapping and BigBoard Settings and return to the table: Responding still shows two and four. Scroll down again and verify the required-reason selection. Reading back both controls checks the saved configuration before you examine its effect in Big Board.'),
    ('05', 'Inspect the overdue unit on the refreshed board', [9],
     'Reload Big Board. Unit Alerts now shows Squad Three, its Responding state, Firehouse Fifty One and the elapsed time in that state. This fictional record is already more than one hundred eighty hours old, far beyond the four-minute alert threshold, so it appears red immediately. The elapsed value helps identify a status report needing review. It does not explain why the report is old. Use the unit\'s normal reporting and coordination process to investigate.'),
    ('06', 'Acknowledge with a reason and inspect the saved result', [10, 11, 13],
     'Select the Squad Three row to open Unit status alert. With Reason empty, the sheet explains the requirement and disables Acknowledge and Mute. Enter the clearly labeled training reason, then select Acknowledge. Reopen the row. The saved section now says Seen by Wallace Boden and retains the exercise note. Acknowledging records that review; the unit still has its Responding state. The sheet also offers Clear acknowledgement for removing the saved acknowledgement.'),
    ('07', 'Give the panel enough space for its note', [12, 14, 15, 21],
     'If the small alert panel clips the saved note, open the gear settings and select Unit Alerts. Under Widget Size, this example uses width four and height three grid units. Select Save and return to the panel. The wider, taller result shows the unit, state, reviewer and complete training note together. Reopening these settings after a later reload still shows four by three. Check the rendered result as well as the values in the editing form.'),
    ('08', 'Save and inspect a fifteen-minute training mute', [16, 17, 18],
     'Open the same alert again. Under Mute for, select fifteen minutes. Replace the reason with the note describing this fictional mute exercise, then choose Mute. The panel now has a collapsed Muted, one, section. Expand it to see Squad Three and the saved mute reason. The unit still says Responding. Moving an alert into this section changes how the timer alert is presented; it does not resolve the underlying unit state.'),
    ('09', 'Verify persistence and clear the saved mute', [19, 20],
     'Reload Big Board, expand Muted, one, and reopen Squad Three. The sheet retains the reviewer and reason and displays a Muted until time. This checks that the saved mute survived a reload. For this exercise, choose Clear acknowledgement. The unit returns to the active red alert panel, because its unchanged Responding record is still beyond the configured threshold. The timer, saved acknowledgement or mute, and underlying unit status are separate things to verify.'),
    ('10', 'Apply the review process across departments', [20],
     'A security control room can use status timers to review a delayed patrol update. Search-and-rescue coordinators can follow a team\'s reporting interval. Community paramedicine and mental health response teams, wildland contractors, industrial response teams, and fire and E M S departments can apply the same review process with appropriate statuses and thresholds. Configure the timer, inspect the actual unit and elapsed time, document the review, and verify the saved result using fictional data before adopting the process.'),
]


def prepare(write=False):
    from verify_capture_evidence import _Validator, _image_dimensions
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    raw = S / RAW / 'manifest.json'
    assert sha(raw) == RAW_SHA
    numbered = {int(row['id'][:3]): row for row in json.loads(raw.read_text())}
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
    scenes = [dict(id=i, title=title, route='/User/Department/MappingSettings' if i in {'02', '03', '04'} else '/home',
                   capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the actual Core threshold/policy controls, Big Board alert sheet, widget sizing form or persisted result being discussed.',
                   required_labels=list(dict.fromkeys(label for n in refs for label in LABELS[n])),
                   narration=text, practice=title + ' in an isolated fictional training department.')
              for i, title, refs, text in SCENES]
    lesson = dict(id=NAME, title='Big Board: configure unit timers, acknowledge and mute alerts', app='BigBoard',
                  summary='Configure Core unit status timers and required reasons, inspect an overdue unit in Big Board, acknowledge and mute it, improve note visibility, and verify the persisted results.',
                  audience=['Department administrators configuring unit timers', 'Authorized dispatch and coordination staff', 'Duty supervisors'],
                  prerequisites=['An isolated fictional department with authorized Core settings access and a signed-in Big Board session.', 'A fictional unit with an existing timed status; acknowledgement controls require the supported call-creation permission.'],
                  scenes=scenes,
                  sector_examples=[dict(sector=sector, scenario=text) for sector, text in [
                      ('Security', 'Review delayed patrol-unit status reports and document the reason.'),
                      ('Search and rescue', 'Use department-defined reporting intervals to review team updates.'),
                      ('Community response', 'Review unit status reports for paramedicine and mental health response coordination.'),
                      ('Wildland', 'Document a contractor resource status-timer review.'),
                      ('Industrial', 'Inspect aging response-unit states and saved review notes.'),
                      ('Fire/EMS', 'Practice timer configuration and acknowledgement using fictional units.')]],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; generated narration, listening, complete correspondence, encoded-frame review and actual playback remain required.',
                                'The two/four-minute thresholds are fictional exercise inputs, not operational response standards.',
                                'The unit already had an older Responding record. A live warning-to-alert crossing, escalation invalidation and automatic mute expiry are not demonstrated.',
                                'No unit state, dispatch assignment, real notification, roster or payment changed in this exercise.',
                                'Source012 illustrates the clipped note in a small widget; no complete-note legibility is claimed there. Sources014/015/021 show the actual size change, legible result and retained dimensions.',
                                'The re-opened sheet resets its Mute for chooser to Until status changes; the saved Muted until time is the readback of the earlier fifteen-minute mute.',
                                'The small red elapsed/status line partly overlaps the saved acknowledgement box in the reopened sheet. Its text is not selected as a legible label in sources013/019.',
                                'Core thresholds and required-reason policy remain configured; the fictional acknowledgement/mute was cleared.'])
    narration = '\n\n'.join(x['narration'] for x in scenes) + '\n'
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=raw.relative_to(S).as_posix(), sha256=RAW_SHA), screenshots=selected)
    review = dict(reviewer='Root', reviewed_at=reviewed_at, actual_originals_personally_viewed=list(LABELS),
                  source_pixels_changed=False, script_reviewed_against_actual_views=True, source_only=True,
                  narration_words=len(narration.split()), audio_or_final_approval_inferred=False,
                  notes=['All twenty-one exact original JPEGs personally viewed before writing this proposal.',
                         'Core and Big Board were reloaded to verify the saved thresholds, reason policy, mute and board dimensions.',
                         'Both acknowledgement reasons are explicitly fictional. The final Clear acknowledgement returned the unchanged Responding unit to the active alert panel.',
                         'Source012 is used only to show the clipped-note problem, followed by the real configuration change and readable result. No pixels were edited.',
                         'No credential values were displayed or captured during the authorized local demo sign-in.'])
    if write:
        out = S / 'expansion/plans' / (NAME + '-source-proposal-20261101-v2')
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
