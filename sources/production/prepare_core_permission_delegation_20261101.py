"""Freeze the actual permission-delegation exercise as a new source proposal.

No speech, listening receipt, canonical lesson or final-video approval is made.
All original captures, including excluded readbacks, remain unchanged.
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
NAME = 'core-permissions-group-and-role-delegation'
RAW = Path('captures/expansion/core-permission-delegation-20261101')
RAW_SHA = '39e3ce25c89cca5a54259f83ecbdcb844442ac3689d9220c018fc8338206b1cc'
REVIEWED_AT = '2026-11-02T05:01:00+00:00'
LOGIN_NOTE = 'Changes to the permissions will take effect on the next login to the Resgrid web application.'
LOCATION_NOTE = 'This option determines who can see the location of personnel on the maps. To lock the option to just group admins and roles within a group you need to check the Group Only option.'
LABELS = {
    1: ['Security and Permissions', LOGIN_NOTE, 'Permission', 'Note', 'Selection', 'Group Only', 'Roles', 'Who can Add Users', 'Department Admins', 'Who can Remove Users', 'No Roles'],
    2: ['Security and Permissions', 'Who can Add Users', 'Department and Group Admins', 'Who can Remove Users', 'Department Admins'],
    3: ['Security and Permissions', 'Who can Add Users', 'Who can Remove Users', 'Department Admins'],
    4: ['Who can Create Trainings', 'Department Admins', 'No Roles'],
    5: ['Who can Create Trainings', 'Department Admins and Select Roles', 'Select roles...', 'Chief', 'Rescue Technician', 'Paramedic', 'Firefighter', 'Driver / Operator', 'Officer'],
    6: ['Who can Create Trainings', 'Department Admins and Select Roles', 'Rescue Technician'],
    9: ['Who can Create Trainings', 'Department Admins', 'No Roles'],
    10: ['Who can see the Location of Personnel', 'Who can see the Location of Units', 'Everyone', LOCATION_NOTE],
    11: ['Firehouse 51 — Training Department', 'Department Settings', 'Security & Permissions'],
}
SCENES = [
    ('01', 'Find the department permission table', [11, 1], ['Security & Permissions', 'Security and Permissions', 'Permission', 'Selection'],
     'Open the department name menu and choose Security and Permissions. The resulting Security and Permissions page contains a table of individual permissions. Read the Permission, Note and Selection columns together before changing a row. Group Only and Roles provide additional scope where offered. This lesson uses a fictional training department so we can compare a saved delegation with its original setting.',
     'Open Security & Permissions and identify the Permission, Note, Selection, Group Only and Roles columns.'),
    ('02', 'Read the administrator scope for adding users', [1], ['Who can Add Users', 'Department Admins'],
     'Find Who can Add Users. Its current selection is Department Admins. The note explains that department administrators and the managing member can add users by default, and that group administrators can be allowed to add users only to the group they administer. Read that scope before delegating this task. A station or community-response team may need local roster administration without receiving every department-wide responsibility.',
     'Read the complete Add Users note and describe the group boundary it states.'),
    ('03', 'Delegate one permission and verify the saved value', [2], ['Who can Add Users', 'Department and Group Admins', 'Who can Remove Users', 'Department Admins'],
     'For the practice change, set Who can Add Users to Department and Group Admins. This control saves when its selection changes. Reload the page and confirm that the same selection returns. Who can Remove Users still shows Department Admins. These are separate decisions: giving a group administrator permission to add a member does not change the remove-users selection. No person is created or removed in this exercise.',
     'In a training department, change Add Users, reload, and compare the separate Remove Users selection.'),
    ('04', 'Restore the practice setting deliberately', [3], ['Who can Add Users', 'Department Admins'],
     'Return Who can Add Users to Department Admins when the practice comparison is complete. After another reload, the original selection is visible again. Use this same readback habit when making an intended departmental change: confirm the exact row and returned value. Record who should own the task before delegating it, and review that decision when personnel or group responsibilities change.',
     'Restore the intended Add Users value and verify it after reloading.'),
    ('05', 'Choose a permission mode and a specific role', [4, 5, 6], ['Who can Create Trainings', 'Department Admins', 'Department Admins and Select Roles', 'Rescue Technician'],
     'Scroll to Who can Create Trainings. The starting selection is Department Admins with No Roles beside it. Choose Department Admins and Select Roles, then open Select roles. This training roster offers named choices including Rescue Technician and Paramedic. Select Rescue Technician for the example and read the resulting Rescue Technician tag beside the permission. This chooses a role for this particular permission; it does not demonstrate changing a member\u2019s role assignment or promoting anyone to department administrator.',
     'Inspect the offered role names and select an appropriate practice role for this permission only.'),
    ('06', 'Check the final permission mode after practice', [6, 9], ['Who can Create Trainings', 'Department Admins', 'No Roles'],
     'After the role-selection exercise, remove the practice selection and return Who can Create Trainings to Department Admins. The final view shows that mode and No Roles again. Compare both pieces, because a permission mode and its selected roles are separate parts of the configuration. Our demonstration restores the training baseline. For a real training coordinator, retain only the delegation your department has actually decided to use.',
     'Verify both the intended training-permission mode and its role selection after practice.'),
    ('07', 'Read location visibility and group scope together', [10], ['Who can see the Location of Personnel', 'Who can see the Location of Units', 'Everyone', LOCATION_NOTE],
     'The location rows separate Who can see the Location of Personnel from Who can see the Location of Units. Both pictured selections are Everyone. The personnel-location note explains the Group Only option for limiting group administrators and roles to a group. Read the row\u2019s selection and scope together rather than treating the checkbox as the entire permission. These controls address who may see locations; this view does not establish that a device is currently reporting its position.',
     'Read the personnel and unit location rows and explain the Group Only note before changing location visibility.'),
    ('08', 'Plan the login check and departmental responsibilities', [1], ['Security and Permissions', LOGIN_NOTE],
     'Return to the note above the Security and Permissions table. It says changes take effect on the next login to the Resgrid web application. After an intended change, plan a normal login and check with the affected authorized account. Our screenshots verify saved settings, not that second-account test. A security company, search-and-rescue team, community paramedicine or mental health service, wildland contractor, industrial response team, or fire and E M S department can use these controls to match administration to actual responsibilities.',
     'Identify the affected role or group administrator and plan a next-login permission check for your department.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from verify_capture_evidence import _image_dimensions, _Validator
    raw_path = S / RAW / 'manifest.json'
    assert sha(raw_path) == RAW_SHA
    assert datetime.fromisoformat(REVIEWED_AT) <= datetime.now(timezone.utc)
    raw = json.loads(raw_path.read_text())
    numbered = {int(r['id'][:3]): r for r in raw}
    selected = []
    for number, labels in LABELS.items():
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        dimensions = _image_dimensions(S / row['file'])
        assert dimensions in ((1280, 720), (1265, 712))
        if dimensions != (row['width'], row['height']):
            row['browser_viewport'] = dict(width=row['width'], height=row['height'])
            row['width'], row['height'] = dimensions
        text = S / RAW / (row['id'] + '.txt')
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   review_status='actual_original_image_reviewed', scene_ids=[],
                   dom_file=text.relative_to(S).as_posix(), dom_sha256=sha(text))
        row['capture_review'] = dict(reviewer='Root', passed=True, reviewed_at=REVIEWED_AT,
                                    sha256=row['sha256'], method='Root personally viewed this exact stored original with view_image. Only readable foreground text is retained; pixels are unchanged.')
        validator = _Validator(S)
        validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
        selected.append(row)
    scenes = [dict(id=i, title=t, route='/User/Security', capture_refs=[numbered[n]['id'] for n in refs],
                   capture_intent='Show the exact permission row, selected mode, role picker or returned result when discussed.',
                   required_labels=labels, narration=speech, practice=practice)
              for i, t, refs, labels, speech, practice in SCENES]
    lesson = dict(id=NAME, title='Delegate department permissions by group and personnel role', app='Core',
                  summary='Compare department and group administrator scope, save and verify an Add Users delegation, inspect role-based training permissions, and read location scope and next-login behavior.',
                  audience=['Department administrators', 'Managing members', 'Department trainers'],
                  prerequisites=['An authorized administrator session in a fictional training department.',
                                 'Existing groups and personnel roles appropriate to the practice scenario.'],
                  scenes=scenes, sector_examples=[
                      dict(sector='Security', scenario='Delegate local roster work to a group supervisor while deciding removal authority separately.'),
                      dict(sector='Search and rescue', scenario='Review a rescue-training role and group scope before assigning administration.'),
                      dict(sector='Community response', scenario='Match community paramedicine or mental health team administration to assigned responsibilities.'),
                      dict(sector='Wildland', scenario='Review contractor group administration and location visibility separately.'),
                      dict(sector='Industrial', scenario='Separate team roster administration from training and location permissions.'),
                      dict(sector='Fire/EMS', scenario='Review station administrator scope without granting every department responsibility.')],
                  source_files=[], candidate_only=True, export_ready=False, publication_approved=False,
                  scope_limits=['Source proposal only; actual generated speech, complete listening review, cue mapping, encoded-frame review and browser playback remain required.',
                                'No member is created, removed, assigned a role or promoted in this exercise. No affected second-account login, map-position result, MFA setup or external notification is demonstrated.'])
    narration = '\n\n'.join(s['narration'] for s in scenes) + '\n'
    manifest = dict(schema_version=1, id=NAME, raw_manifest=dict(file=raw_path.relative_to(S).as_posix(), sha256=RAW_SHA), screenshots=selected,
                    excluded_sources=[dict(id=numbered[n]['id'], sha256=numbered[n]['sha256'], reason=reason) for n, reason in {
                        7: 'Reloaded role tag is clipped and displays a numeric identifier. This is not learner footage or a readable role-name verification.',
                        8: 'Permission mode was restored but the hidden role selection was not yet cleared. Source009 is the subsequently verified complete baseline.'}.items()])
    review = dict(reviewer='Root', reviewed_at=REVIEWED_AT, actual_originals_personally_viewed=list(LABELS),
                  source_pixels_changed=False, script_reviewed_against_actual_views=True,
                  narration_words=len(narration.split()), source_only=True, audio_or_final_video_approval_inferred=False,
                  limits=['The role picker and selected Rescue Technician tag use sources005/006. No claim is made that a human-readable role name returned on reload.',
                          'The complete role baseline was verified only after ordinary Backspace removal through the role search input, followed by restoring Department Admins and reloading. The earlier clear-all click did not establish empty saved data.'])
    if write:
        dest = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
        assert not dest.exists()
        dest.mkdir()
        for filename, value in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest), ('source-review.json', review)]:
            with (dest / filename).open('x') as stream:
                stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        with (dest / 'narration.txt').open('x') as stream:
            stream.write(narration)
    return dict(lesson_id=NAME, source_ready=True, scenes=len(scenes), screenshot_records=len(selected),
                distinct_images=len({r['sha256'] for r in selected}), words=len(narration.split()), written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
