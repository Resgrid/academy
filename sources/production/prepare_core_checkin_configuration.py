"""Freeze the actual Core timer-configuration exercise for natural narration.

Uses retained, unedited application viewports. It assigns no speech timings and
does not render, approve audio, or qualify a lesson for publication.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-checkin-configuration'
BASE = SOURCES / 'expansion/plans/core-checkin-configuration-capture-freeze-20261028-v2'
CAPTURES = Path('captures/expansion/core-timer-configuration-20261028')

SPECS = [
('014', 'find-the-settings', 'Find the check-in settings',
 ['Department Settings', 'Calls & Dispatch', 'Call & Dispatch Settings'],
 'Start in Department Settings. Open Calls & Dispatch and choose Call & Dispatch Settings. This lesson follows the complete setup of a Personnel check-in rule, then tests it on one fictional call. Check-ins help coordinators organize agreed reporting updates, including community care visits and mental health response assignments. Department administrators configure the rules; operators use the resulting timers and history.',
 'Find Call & Dispatch Settings using the administrator menu.'),
('013', 'automatic-or-per-call', 'Choose automatic or per-call enablement',
 ['Check-In Timer Settings', 'Auto-Enable Check-In Timers for New Calls'],
 'Find Check-In Timer Settings. Auto-Enable Check-In Timers for New Calls controls whether new calls start with timers enabled. It is off in this training department. We leave it off and explicitly enable one practice call later. This separates department-wide enablement from the reporting interval and from the decision to use timers on an individual incident.',
 'Review the current automatic-enable setting before changing any timer rules.'),
('001', 'create-default', 'Create a Personnel default',
 ['Add New Default Timer', 'Target Type', 'Duration (minutes)', 'Warning Threshold (minutes)', 'Enabled', 'Active States', 'Add Timer Config'],
 'Under Add New Default Timer, choose Personnel as the Target Type. Set Duration to thirty minutes and Warning Threshold to five minutes. Leave Enabled selected. Active States can restrict when a timer applies; leaving it empty uses All States. Review the values, then select Add Timer Config. Use intervals and state filters that your department has agreed for its work.',
 'Create a reviewed training default and record its duration, warning threshold, and active states.'),
('002', 'verify-default', 'Verify the saved default and its impact',
 ['Default Timer Configurations', 'Personnel', '30', '5', 'Yes', 'All'],
 'Verify the saved Personnel row in Default Timer Configurations: thirty minutes, a five-minute warning threshold, Enabled Yes, and Active States All. This default applies when an enabled timer has no matching override. The warning threshold defines how close to the due time the server marks a timer as Warning. Here that window is the final five minutes of the thirty-minute interval. An overdue timer has reached its reporting deadline. Check the resulting behavior in the applications your department uses.',
 'Read back the saved row and explain its interval and warning period.'),
('003', 'create-override', 'Create a call-type override',
 ['Add New Override', 'Call Type ID', 'Call Priority', 'Target Type', 'Duration (minutes)', 'Warning Threshold (minutes)', 'Enabled', 'Active States', 'Add Override'],
 'Use Add New Override for a rule tied to a call type or priority. Here Call Type ID is Rescue, Call Priority is Any, Target Type is Personnel, Duration is forty-five minutes, and Warning Threshold is ten. We clear Enabled to save this example in a disabled state. Active States is empty. Select Add Override after reviewing the scope and values.',
 'Save a disabled training override and confirm that its scope is intentional.'),
('004', 'verify-override', 'Compare saved overrides with the default',
 ['Call Type / Priority Overrides', 'Investigation', '60', 'Rescue', '45', 'No'],
 'Review Call Type / Priority Overrides. The Rescue row now shows forty-five minutes, ten warning minutes, and Enabled No, so that example is inactive. The existing Investigation Personnel rule is enabled for sixty minutes with a five-minute warning threshold. Matching enabled overrides take precedence over the default. We will use Investigation to test that sixty-minute rule while retaining the thirty-minute default.',
 'Compare the enabled Investigation override with the disabled Rescue example.'),
('005', 'prepare-call', 'Prepare an identifiable training call',
 ['New Call', 'Name', 'Priority', 'Type', 'Call Identifier', 'Investigation'],
 'On New Call, enter a clear training Name and choose the intended Priority and Type. Our type is Investigation and the priority is Routine. The Call Identifier gives this exercise another recognizable reference. Keep the scenario fictional and identify it clearly so other operators can distinguish it from normal work. We use a supplied fictional location for this software exercise.',
 'Prepare a clearly named fictional call using a type that matches the enabled override.'),
('006', 'select-recipient', 'Choose the training recipient',
 ['Personnel', 'Wallace Boden'],
 'In Personnel, select Wallace Boden for this practice call. Review the selected row rather than assuming a station, role, or group contains the intended recipient. For a real rollout, test with an agreed training audience first. A call may have several participants, so the recipient scope matters when you review which personnel timers appear.',
 'Select the intended training recipient and verify the checked row.'),
('007', 'enable-call', 'Enable timers for the individual call',
 ['Check-In Timers', 'Enable Check-In Timers', 'Create and Dispatch Call'],
 'Near the bottom of the form, select Enable Check-In Timers. This is the per-call choice we planned while automatic enablement remained off. Review the rest of the call and its recipients, then choose Create and Dispatch Call. Saving timer configuration alone does not opt this call into timers; this checkbox makes that choice explicit for the exercise.',
 'Enable timers on the reviewed practice call before creating it.'),
('008', 'verify-effective-timer', 'Verify the override on the live call',
 ['Check-In Timers', 'Personnel', 'Time Remaining', 'OK', 'Show Check-In History'],
 'Open the new call and inspect Check-In Timers. Wallace Boden has a Personnel timer, the state is OK, and Time Remaining is just under sixty minutes. This call uses the enabled Investigation override rather than the thirty-minute default. Open Show Check-In History to inspect the saved entries; this new exercise initially has none. This readback checks the effect of the configuration on an actual call.',
 'Confirm the correct target and effective interval on the newly created call.'),
('009', 'record-checkin', 'Add a check-in note',
 ['Check In', 'Note'],
 'The Check In dialog provides a Note field. Enter a concise update under your department procedure, review it, and select Check In. Our note identifies a software practice check-in for this timer lesson. It makes no claim about physical arrival or device location. The note belongs to the check-in record, so it should explain the update clearly enough for another coordinator to understand.',
 'Enter and confirm one permitted software check-in note.'),
('010', 'verify-checkin', 'Read back the saved entry',
 ['Check-In Timers', 'Timestamp', 'Who', 'Type', 'Note'],
 'Review the timer and saved history after confirmation. The table shows Timestamp, Who, Type, and Note. Our new Personnel entry contains the exact practice note we entered. The timer has begun a new interval. Checking the saved history distinguishes a completed update from text left in a dialog. Keep status reporting, check-in reporting, and any physical safety verification under their appropriate department procedures.',
 'Verify the new timestamp and stored note after confirmation.'),
('011', 'close-practice', 'Close the completed practice call',
 ['Close Call', 'Completed Type', 'Send Notification', 'Completed Notes'],
 'Finish the exercise through Close Call. Review Completed Type, Send Notification, and Completed Notes. We use Closed, leave Send Notification off for this local practice, and record a clear completion note. Then select Close Call. Review these choices for your own audience: the notification option changes whether the closing event is sent to the call participants.',
 'Close only the agreed practice call with reviewed notes and notification choice.'),
('012', 'verify-closure', 'Verify closure and retain the history',
 ['Closed', 'Completed Notes:', 'Check-In Timers'],
 'Verify that the call now shows Closed and the expected Completed Notes. Its saved check-in history remains available for review. The same configuration and verification habits apply to search and rescue, security companies, wildland contractors, and industrial response teams: choose the reporting target, agree the interval, test the matching rule, and check the resulting record before extending the setup to everyday work.',
 'Verify the closed call and its retained check-in record.')]


def freeze():
    assert not BASE.exists(), 'Preserve existing freezes; use a fresh path for revisions.'
    raw = json.loads((SOURCES / CAPTURES / 'manifest.json').read_text())
    by_prefix = {row['id'][:3]: row for row in raw}
    selected, scenes = [], []
    now = datetime.now(timezone.utc).isoformat()
    for prefix, ident, title, labels, narration, practice in SPECS:
        row = dict(by_prefix[prefix])
        assert hashlib.sha256((SOURCES/row['file']).read_bytes()).hexdigest() == row['sha256']
        # The generic raw recorder omits some selected input values and retains
        # background text behind the modal. This reviewed snapshot retains only
        # the lesson's foreground labels inspected in the exact stored JPEG.
        for label in labels:
            assert label in row['visible_labels'] or (prefix == '006' and label == 'Personnel')
        row['visible_labels'] = labels
        row['eligible_for_lesson'] = True
        row['capture_review'] = {'passed': True, 'reviewed_at': now,
            'reviewer': 'Codex original-size actual screenshot inspection',
            'sha256': row['sha256'], 'method': 'Original application viewport inspected for the retained labels; no pixel edits, synthetic controls, loading views, or credential fields. Background modal labels are excluded.'}
        selected.append(row)
        scenes.append({'id': ident, 'title': title, 'narration': narration,
            'required_labels': labels, 'practice': practice,
            'capture_evidence': {'status': 'actual_screenshot_reviewed', 'capture_refs': [row['id']]}})
    examples = [('Fire / EMS', 'Coordinate agreed reporting updates during an incident.'),
        ('Community response', 'Use agreed check-ins during community paramedicine and mental health response visits.'),
        ('Search and rescue', 'Coordinate scheduled search-team reporting under the team procedure.'),
        ('Security', 'Review agreed updates for patrol or security assignments.'),
        ('Wildland', 'Coordinate contractor crew reporting during longer assignments.'),
        ('Industrial', 'Record agreed updates during an industrial response exercise.')]
    lesson = {'id': NAME, 'title': 'Configure check-in defaults, overrides and per-call timers',
        'app': 'Core', 'audience': ['Department administrators', 'Dispatchers and coordinators'],
        'summary': 'Create timer rules, understand their effect, enable one practice call, and verify a check-in and its saved history.',
        'prerequisites': ['Department administration permission in an isolated training department.', 'A reviewed training recipient and your department reporting procedure.'],
        'scenes': scenes, 'sector_examples': [dict(sector=s, scenario=t, practice='Test the intended timer rule on an authorized training call and verify the saved history.') for s,t in examples],
        'source_files': ['Core/Web/Resgrid.Web/Areas/User/Views/Department/DispatchSettings.cshtml', 'Core/Web/Resgrid.Web/wwwroot/js/app/internal/dispatch/resgrid.dispatch.checkin-timers.js', 'Core/Core/Resgrid.Services/CheckInTimerService.cs'],
        'capture_limitations': ['Warning and overdue thresholds are explained from the recorded configuration and current source; no timed warning transition or external alert delivery is demonstrated.', 'The exercise verifies a Personnel software check-in, not physical arrival or device location.'],
        'authoring_status': 'actual_capture_reviewed_narration_frozen', 'media_status': 'awaiting_natural_narration',
        'narration_word_count': sum(len(s['narration'].split()) for s in scenes)}
    BASE.mkdir(parents=True)
    (BASE/(NAME+'.narrated-source.json')).write_text(json.dumps(lesson,indent=2,ensure_ascii=False)+'\n')
    (BASE/'captures.reviewed.json').write_text(json.dumps({'app':'Core','screenshots':selected,'source_manifest':str(CAPTURES/'manifest.json')},indent=2,ensure_ascii=False)+'\n')
    (BASE/'narration.txt').write_text('\n\n'.join(s['narration'] for s in scenes)+'\n')
    print(json.dumps({'lesson':NAME,'scenes':len(scenes),'screenshots':len(selected),'words':lesson['narration_word_count'],'audio_generated':False}))


if __name__ == '__main__':
    freeze()
