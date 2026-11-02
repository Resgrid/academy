"""Freeze the demonstrated Records defaults and existing-definition inspection.

This prepares source inputs only. It never grants audio or final-video approval.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

S = Path(__file__).resolve().parents[1]
NAME = 'core-records-review-defaults'
BASE = Path('expansion/plans') / (NAME + '-source-proposal-20261101')
RAW = Path('captures/expansion/core-records-defaults-20261101/manifest.json')


def scene(number, title, narration, practice, labels, capture):
    return {'id': f'{number:02}', 'title': title, 'narration': narration,
            'practice': practice, 'required_labels': labels, 'capture_refs': [capture]}


LESSON = {
    'id': NAME, 'app': 'Core',
    'title': 'Review Records defaults and definition-specific policy',
    'summary': 'Find Records Settings, save and verify lifecycle and review-deadline defaults, inspect existing definitions, then restore the practice values.',
    'audience': ['Department administrators', 'Records administrators', 'Department trainers'],
    'prerequisites': [
        'An authorized Core session with the Records Manage menu, Settings and Definitions available.',
        'A separate training department and a recorded baseline before practicing settings changes.',
        'An agreed department review policy and responsibility for maintaining each record definition.',
    ],
    'scenes': [
        scene(1, 'Find Settings from the Records Manage menu',
              'Records administration starts with finding the correct controls. In the Records area, open All records and choose Manage. The expanded menu contains Settings and Definitions. Settings holds department-level values; Definitions lets you inspect the forms and their own policies. Begin with Settings. This example uses the fictional Firehouse fifty-one training department, so the practice changes stay with a separate training environment.',
              'Open All records, expand Manage and locate Settings and Definitions.',
              ['Records', 'All records', 'Manage', 'Settings', 'Definitions'], '014-records-manage-menu'),
        scene(2, 'Record the lifecycle and deadline baseline',
              'On Records Settings, Default lifecycle preset for department definitions currently shows Quick Entry. Review due, in hours, is seventy-two. Record those baseline values before practicing. The displayed help says locked definitions retain their own lifecycle. It also says a definition-level deadline override takes precedence over the department deadline. This is an administrative review interval; the screen explicitly distinguishes it from a statutory deadline. Check the actual definition policy as well as this department form when planning a review process.',
              'Read QuickEntry,72hours and both help statements before making a practice change.',
              ['Records Settings', 'Default lifecycle preset for department definitions', 'QuickEntry', 'Review due (hours)', '72'], '002-baseline-selected-preset-visible'),
        scene(3, 'Prepare the two practice values',
              'For this exercise, select Review Required in Default lifecycle preset for department definitions, then enter forty-eight in Review due, in hours. Both prepared values are visible together. Forty-eight hours is the training example, not a recommended deadline for every department. Choose an interval that matches your own review responsibilities. At this point the form is prepared but has not yet been saved.',
              'Compare the prepared ReviewRequired and48hour values with the recorded baseline.',
              ['Default lifecycle preset for department definitions', 'ReviewRequired', 'Review due (hours)', '48'], '003-prepared-reviewrequired-48-hours'),
        scene(4, 'Save the reviewed practice change',
              'Scroll to the bottom of Records Settings. Save and Cancel are visible below the other settings sections. Review the intended change, then choose Save once. Typing a value into a field only prepares the form. The returned page and a fresh page load give you a separate check that the intended values were accepted and retained.',
              'Identify the actual Save action at the bottom of the settings form.',
              ['Save', 'Cancel'], '004-save-defaults-control'),
        scene(5, 'Read the saved result',
              'The returned page displays Records settings saved. The lifecycle field shows Review Required, and the review deadline shows forty-eight. Compare both saved values with the two values you intended to change. A success notice helps, and inspecting the fields confirms which configuration is now displayed.',
              'Read the success notice and verify both returned field values.',
              ['Records settings saved.', 'ReviewRequired', 'Review due (hours)', '48'], '005-reviewrequired-and-deadline-saved'),
        scene(6, 'Reopen Settings to verify persistence',
              'Reopening Records Settings shows Review Required and forty-eight hours again. This is a fresh page load after the save. It confirms that the department form retained those values. The next check is the policy on existing record definitions. A saved department value alone does not tell you the lifecycle shown by every form that personnel can use.',
              'Verify the same two values after reopening the page.',
              ['Records Settings', 'ReviewRequired', 'Review due (hours)', '48'], '006-defaults-persist-after-reopen'),
        scene(7, 'Return to Manage and open Definitions',
              'Return to All records and expand Manage again. Choose Definitions from this menu to inspect the record forms. This keeps the department settings check separate from the definition check, while giving administrators a repeatable route to both screens.',
              'Use the visible Manage menu to locate Definitions.',
              ['All records', 'Manage', 'Definitions'], '014-records-manage-menu'),
        scene(8, 'Inspect the locked definition policies',
              'The Definitions table includes Owner, Published version and Lifecycle preset columns. Run and Training are marked Product, locked. Both show published version one and Quick Entry. This screen was captured while the department form had the saved Review Required value. The locked definitions still show their own Quick Entry policy, matching the scope described in the department settings help. Read the row you actually intend to use.',
              'Compare the locked Run and Training rows with the saved department value.',
              ['Definitions', 'Owner', 'Published version', 'Lifecycle preset', 'Run', 'Training', 'Product (locked)', 'QuickEntry'], '007-locked-definition-policies-remain'),
        scene(9, 'Find the department-owned example',
              'In the same table, locate Training Only, Community software exercise. Its owner is Department, and its lifecycle column shows Quick Entry. The row has an Edit link. Choose Edit to inspect that definition version. Use the definition name and owner to distinguish a department-owned form from a locked product form before deciding which policy you are maintaining.',
              'Locate the fictional department-owned definition and its Edit link.',
              ['TRAINING ONLY - Community software exercise', 'Department', 'QuickEntry', 'Edit'], '015-department-definition-row-and-edit'),
        scene(10, 'Read the published version before editing',
              'The definition page identifies version one as Published. Its notice says this version is published and read-only, and it offers Open new draft for changes. Lifecycle preset still shows Quick Entry on this existing published definition. Review the version you are inspecting before planning an edit. This walkthrough reads the existing policy; it leaves Open new draft available for a separate definition-change exercise.',
              'Read the Published notice, Open new draft action and existing lifecycle value.',
              ['Published', 'This version is published and read-only. Open a new draft to make changes.', 'Open new draft', 'Lifecycle preset', 'QuickEntry'], '008-published-definition-retains-policy'),
        scene(11, 'Locate the definition-specific review controls',
              'Farther down the same definition page are Reviewer roles, Approver roles and Review due, in hours. The review deadline field is blank in this example. These are definition-specific controls to inspect when deciding how that form should be reviewed. The department settings help explains the precedence of a definition-level deadline override. Keep role assignments, the selected lifecycle and the review interval consistent with the people responsible for the process. This inspection does not change the published version.',
              'Locate the role controls and blank review-deadline field on the existing definition.',
              ['Reviewer roles', 'Approver roles', 'Review due (hours)'], '010-definition-deadline-and-role-controls'),
        scene(12, 'Prepare the original values for restoration',
              'Return to Records Settings after the exercise. The prepared restoration selects Quick Entry and enters seventy-two hours, matching the baseline. Compare both fields with the values you recorded at the start. Restoring a practice change should be an intentional configuration decision, using the same review of the complete form as the original change.',
              'Compare the prepared QuickEntry and72hour restoration with the baseline.',
              ['Records Settings', 'QuickEntry', 'Review due (hours)', '72'], '011-original-defaults-prepared-for-restoration'),
        scene(13, 'Use Save for the restoration too',
              'Use the same Save action at the bottom of the settings form to apply the restoration. The original values are still only prepared until you save them. Verify the returned result before ending the exercise.',
              'Identify the Save action used to apply the reviewed restoration.',
              ['Save', 'Cancel'], '004-save-defaults-control'),
        scene(14, 'Verify the original saved values',
              'Records settings saved appears again. Quick Entry and seventy-two hours are now displayed on the returned form. The demonstration has restored its original department defaults. No record was submitted for review, and no definition version was edited or published during this settings exercise.',
              'Read the restoration success notice and both original values.',
              ['Records settings saved.', 'QuickEntry', 'Review due (hours)', '72'], '012-original-defaults-restored'),
        scene(15, 'Apply the verification process to your department',
              'A final reopening still shows Quick Entry and seventy-two hours. Use this same baseline, save, reopen and definition-inspection process for your department. Security teams can organize post-report review, wildland contractors can review crew-support records, and industrial teams can coordinate exercise documentation. Community paramedicine and mental health teams can define appropriate outreach review responsibilities, while search-and-rescue teams can review mission-support documentation. Fire and E M S departments can use the same checks. Set a clear policy, then verify the specific form personnel will use.',
              'Verify the restored values after a fresh page load and plan a fictional review policy for your department.',
              ['Records Settings', 'QuickEntry', 'Review due (hours)', '72'], '013-original-defaults-persist-after-reopen'),
    ],
    'sector_examples': [{'sector': sector, 'scenario': scenario} for sector, scenario in [
        ('Fire / EMS', 'Verify the appropriate review policy on the particular station or department form.'),
        ('Community response', 'Agree on appropriate outreach documentation and review responsibilities.'),
        ('Search and rescue', 'Inspect the actual policy used for a mission-support record.'),
        ('Security', 'Coordinate post-report review with the authorized reviewers.'),
        ('Wildland', 'Review crew-support documentation under an agreed administrative interval.'),
        ('Industrial', 'Verify an exercise-documentation form and its responsible reviewers.'),
    ]],
    'scope_limits': [
        'Two normal local Records Settings saves are demonstrated: ReviewRequired/48hours, then the original QuickEntry/72hours. Fresh GETs confirm both persisted states.',
        'Existing locked and published definition policies are inspected. No new blank definition, draft, lifecycle transition, review submission, role edit or definition publication is performed; automatic policy inheritance on new definitions is not demonstrated.',
        'The department-definition row navigation was recorded after restoration; the published definition detail and locked-policy comparison were recorded while ReviewRequired/48hours was saved. The existing definition was unchanged throughout.',
        'The administrative interval is a department policy choice; the actual screen states it does not infer a statutory deadline.',
        'Source candidate only; natural narration, actual timing and complete encoded/browser reviews remain required.',
    ],
    'export_ready': False, 'publication_mode': 'source_candidate_only',
}


def freeze(write=False):
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    encode = lambda data: (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    manifest = S / RAW
    original_rows = {row['id']: row for row in json.loads(manifest.read_text())['captures']}
    reviewed_path = manifest.parent / 'captures.reviewed.json'
    reviewed = {row['id']: row for row in json.loads(reviewed_path.read_text())['screenshots']}
    files = {BASE / 'lesson.candidate.json': encode(LESSON)}
    rows = []
    for capture_id in dict.fromkeys(ref for item in LESSON['scenes'] for ref in item['capture_refs']):
        row = deepcopy(reviewed[capture_id])
        assert capture_id not in {'001-existing-lifecycle-and-deadline', '009-definition-review-deadline-field'}
        assert row['capture_review']['passed'] and row['capture_review']['reviewer'] == 'Codex /root'
        assert row['sha256'] == original_rows[capture_id]['sha256']
        labels = list(dict.fromkeys(label for item in LESSON['scenes'] if capture_id in item['capture_refs'] for label in item['required_labels']))
        assert set(labels) <= set(row['visible_labels']), (capture_id, set(labels) - set(row['visible_labels']))
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        image = BASE / 'images' / (capture_id + '.jpg')
        dom = BASE / 'dom' / (capture_id + '.dom.txt')
        files[image] = (S / row['file']).read_bytes()
        files[dom] = (S / row['dom_file']).read_bytes()
        row['raw_source'] = {'manifest_file': str(RAW), 'manifest_sha256': sha(manifest),
                             'reviewed_manifest_file': str(reviewed_path.relative_to(S)), 'reviewed_manifest_sha256': sha(reviewed_path),
                             'image_file': row['file'], 'image_sha256': row['sha256'],
                             'dom_file': row['dom_file'], 'dom_sha256': row['dom_sha256']}
        row.update(file=str(image), dom_file=str(dom), visible_labels=labels, required_labels=labels,
                   visible_controls=[], visible_field_text=[])
        row['capture_review'].pop('controls_sha256', None)
        rows.append(row)
    script = '\n\n'.join(item['narration'] for item in LESSON['scenes']) + '\n'
    files[BASE / 'narration.txt'] = script.encode()
    files[BASE / 'captures.reviewed.json'] = encode({'app': 'Core', 'screenshots': rows})
    files[BASE / 'source-provenance.json'] = encode({
        'created_at': datetime.now(timezone.utc).isoformat(),
        'lesson_sha256': hashlib.sha256(files[BASE / 'lesson.candidate.json']).hexdigest(),
        'script_words': len(script.split()), 'scenes': len(LESSON['scenes']),
        'reviewed_source_images': len(rows),
        'source_review_inherited_from_exact_reviewed_manifest_bytes': True,
        'actual_video_or_listening_approval_inferred': False,
    })
    if write:
        assert all(not (S / path).exists() for path in files)
        for path, data in files.items():
            destination = S / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(data)
    return {'lesson_id': NAME, 'words': len(script.split()), 'scenes': len(LESSON['scenes']),
            'actual_source_images': len(rows), 'source_sha256': hashlib.sha256(files[BASE / 'lesson.candidate.json']).hexdigest(),
            'written': write, 'qualified_video': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    arguments = parser.parse_args()
    print(json.dumps(freeze(arguments.freeze), indent=2))
