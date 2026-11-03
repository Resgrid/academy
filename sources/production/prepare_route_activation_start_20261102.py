"""Freeze personally reviewed, unchanged Core route start/monitor screenshots."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

S = Path(__file__).resolve().parents[1]
NAME = 'core-route-activation-start'
RAW = S / 'captures/expansion/core-route-activation-start-20261102'
OUT = S / 'expansion/plans' / (NAME + '-source-20261102-v2')

SCENES = [
    ('Review the prepared plan before activation', [1], ['Edit Route Plan', 'Name', 'Description', 'Unit', 'Status', 'Draft'],
     'Open the saved route in Edit and check its Name and Description before changing its state. This is the fictional Community supply loop from the route-planning lesson. It has two prepared stops. Unit still says Assign at start time, and Status is Draft. Practice in a separate training department. Before using a real plan, verify its locations, contacts and directions with the people responsible for the work.'),
    ('Activate the plan and verify the saved action', [2, 3, 4], ['Status', 'Active', 'Save Changes', 'Start'],
     'Change Status from Draft to Active. Scroll to the bottom and select Save Changes. The returned Routes list shows Active beside Community supply loop, and its Actions now include Start. The plan is ready for the start operation, but this saved status alone does not show a unit executing it. The next step explicitly chooses the unit and creates that execution.'),
    ('Choose the unit that will execute the route', [4, 5, 6], ['Start', 'Assign Unit', 'TRAINING ONLY - Community van 20261028', 'Start Route Now'],
     'Select Start on the saved route row. The Start Route page asks for Assign Unit and says to select the unit that will execute this route. Choose the fictional Community van from the dropdown. Review the route name and this unit selection together. In your department, choose the resource responsible for these stops. The Start Route Now button is the action that begins the execution; Cancel leaves this start form.'),
    ('Start and inspect the returned instance', [6, 7], ['Start Route Now', 'Instance Info', 'InProgress', '51008', 'Started', 'Ended', '0 / 2'],
     'Select Start Route Now once. The returned Route Instance page shows In Progress in Instance Info, the unit identifier, and a Started time. Here the selected training van is represented by unit number fifty-one thousand eight. Ended is a dash, and Progress is zero of two. These saved instance details show that the start succeeded. They do not say that either service stop has already been completed.'),
    ('Read the initial stop timeline', [8], ['Instance Info', 'Stop Timeline', 'Pending', '0 / 2'],
     'Scroll down to inspect Stop Timeline. Both entries are Pending in this newly started instance, and the progress remains zero of two. Use the status text and progress together when reviewing a route. This recording has not checked into either location, and the map does not display a generated road route. Starting an instance is an administration step; verify navigation and actual field progress separately before relying on them.'),
    ('Reopen from the In Progress overview', [22, 23, 24], ['In Progress', 'In Progress Routes', 'InProgress', '51008', '0 / 2', 'View Details'],
     'Return to Routes and select In Progress in the top action bar. The overview now contains the Community supply loop card, its unit number, start time and zero-of-two stop count. Select View Details on that card. The same instance information returns with In Progress and the original start time. This lets a supervisor find an executing route again without starting another instance.'),
    ('Inspect the plan history', [22, 13], ['History', 'Route History - TRAINING ONLY - Community supply loop', 'Status', 'Unit', 'Started', 'Ended', 'Stops', 'Detail'],
     'Return to Routes and select History on the Community supply loop row. Route History lists the stored execution with Status, Unit, Started, Ended and Stops columns. In this exercise there is one In Progress row, a start time, no end time and zero of two completed stops. Detail opens that execution. Use this history when checking which instance a progress report refers to, rather than treating the plan status as the execution history.'),
    ('Recognize the busy-unit guard', [22, 16, 17], ['Start', 'TRAINING ONLY - Community van 20261028', 'Start Route Now', 'Unit already has an active route instance.'],
     'For this training check, return to Start and select the same Community van while its first instance is still in progress. Select Start Route Now once. Resgrid returns Unit already has an active route instance. This refusal means the second start did not succeed. Do not keep retrying that unit. Review its existing route before deciding whether another appropriate resource should take a different assignment.'),
    ('Verify retained history and apply the review', [17, 21], ['Cancel', 'Route History - TRAINING ONLY - Community supply loop', 'InProgress', '51008', '0 / 2'],
     'Leave the refused start with Cancel, return to Routes and open History again. The recorded result still has the original single In Progress instance with zero of two stops completed. Keep the distinction clear: prepare the plan, start the intended unit, then inspect actual progress. This pattern can support search-and-rescue logistics, security service visits, wildland supplies, industrial response support, community paramedicine or mental health outreach, as well as fire and E M S. Match the stops and assigned resource to your department’s work.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not OUT.exists(), 'Preserve the frozen source; use a new dated revision.'
    rows = json.loads((RAW / 'manifest.json').read_text())
    numbered = {int(row['id'].split('-')[3]): row for row in rows}
    used = sorted({number for _, numbers, _, _ in SCENES for number in numbers})
    now = datetime.now(timezone.utc).isoformat()
    screenshots = []
    for number in used:
        row = deepcopy(numbered[number])
        assert sha(S / row['file']) == row['sha256']
        dom = RAW / (row['id'] + '.txt')
        row.update(dom_file=dom.relative_to(S).as_posix(), dom_sha256=sha(dom), eligible_for_lesson=True,
                   review_status='actual_source_contact_sheet_reviewed',
                   capture_review=dict(reviewer='Root', passed=True, reviewed_at=now, sha256=row['sha256'],
                       method='Root personally reviewed all six original source sheets and the full-size replacement Routes, In Progress and reopened-instance screenshots. Fading transitions were rejected. Original browser image bytes are unchanged. No final video approval inferred.'))
        screenshots.append(row)
    scope = ('One fictional plan was saved from Draft to Active through normal UI, then started once for the training Community van (unit51008). '
             'Instance9e14f10f-fa21-426c-8885-4b3a32f3fddc persisted InProgress, start2026-11-03T03:56UTC, zero of two complete, and both timeline entries Pending. '
             'Normal In Progress and History navigation reopened this execution. One repeat start for the same unit was refused; fresh history retained exactly one row. '
             'No road directions, live journey, field movement, ETA, stop check-in/completion, instance end/cancellation, paused behavior or archival is claimed. '
             'The recorded timeline labels are2/3 for two saved stops; those labels are not described as authoritative stop ordering. '
             'Sources022/023/024 are fresh settled navigation readbacks replacing faded earlier transitions; they do not claim another execution or another start time.')
    lesson = dict(id=NAME, title='Activate a route, assign a unit and review its execution', app='Core',
        summary='Activate a saved plan, start its assigned training unit, reopen progress and history, and recognize the busy-unit refusal.',
        audience=['Department administrators', 'Operations supervisors', 'Route and logistics coordinators'],
        prerequisites=['Authorized Routes access and a separate fictional training department.',
                       'A reviewed saved route and an appropriate available unit; verify road guidance before real operational use.'],
        scenes=[dict(id=f'{i:02}', title=title, route='/User/Routes', capture_refs=[numbered[n]['id'] for n in refs],
                     required_labels=labels, narration=speech, practice=title,
                     capture_intent='Show the actual prepared control, saved execution or returned refusal at the words discussing it.')
                for i, (title, refs, labels, speech) in enumerate(SCENES, 1)],
        candidate_only=True, export_ready=False, publication_approved=False, source_files=[],
        sector_examples=[dict(sector=sector, scenario='Assign an appropriate unit to a reviewed service or logistics plan and verify the saved instance, history and real progress.')
                         for sector in ['Community paramedicine and mental health response', 'Search and rescue', 'Security', 'Wildland', 'Industrial emergency response', 'Fire/EMS']],
        scope_limits=['Source proposal only; speech generation, complete correspondence, listening, encoded review and playback qualification remain required.', scope])
    manifest = dict(schema_version=1, id=NAME, screenshots=screenshots,
                    raw_manifest=dict(file=(OUT/'raw-manifest.snapshot.json').relative_to(S).as_posix(), sha256=sha(RAW/'manifest.json')),
                    excluded_sources=[dict(id=row['id'], sha256=row['sha256'], reason='Fading navigation transition or redundant source outside this bounded selection; original retained unchanged.')
                                      for number, row in numbered.items() if number not in used])
    OUT.mkdir(parents=True)
    (OUT/'raw-manifest.snapshot.json').write_bytes((RAW/'manifest.json').read_bytes())
    for file, obj in [('lesson.candidate.json', lesson), ('captures.reviewed.json', manifest),
                      ('source-review.json', dict(reviewer='Root', reviewed_at=now,
                          actual_images_reviewed=[r['id'] for r in screenshots], source_pixels_unchanged=True,
                          final_video_approval_inferred=False))]:
        (OUT/file).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')
    text = '\n\n'.join(scene['narration'] for scene in lesson['scenes'])+'\n'
    (OUT/'narration.txt').write_text(text)
    print(json.dumps(dict(lesson=NAME, scenes=len(SCENES), actual_sources=len(screenshots), words=len(text.split()), video_complete=False)))


if __name__ == '__main__':
    main()
