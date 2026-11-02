"""Prepare an unvoiced IC review lesson from personally inspected real captures.

Preserve the original capture manifest and pixels. This creates no canonical
lesson, listening approval, instruction-timing approval or publication.
"""
from copy import deepcopy
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'app-ic-call-context-readiness-review'
OUT = S / 'expansion/plans' / (NAME + '-source-proposal-20261101')
RAW = S / 'captures/expansion/ic/manifest.json'
REVIEWED_AT = '2026-11-02T03:05:00+00:00'
SOURCES = {
    'ic-07-calls': ('67d53d564262fc95caddf2bffc6d0e6ecd6723b5d0db6413f5c688f4ddfbbb11',
        ['Calls', 'Search calls...', '#DEMO-0003', 'TRAINING — Vehicle rescue exercise', '#DEMO-0002', 'TRAINING — Community medical standby', 'Start Command']),
    'ic-39-call-context-chicago-map': ('ca6318fd247a5a8ae970e0be2b3375843c7866bc9c14c585a328d70f4f2be0e0',
        ['Call Details', 'TRAINING — Warehouse alarm (DEMO-0001)', 'Active Command', 'Open Command Board',
         'Exercise: reported smoke at an unoccupied training warehouse. Squad 3 assigned for a search demonstration.',
         'Training site 1 (fictional), Chicago, IL', 'Notes', 'Images', 'Files', 'Route']),
    'ic-41-call-readiness-empty-checks': ('c1fa3e548438654b46c1a70e46359827cf1f3ebb8a7cb8aabb180399f8f4256e',
        ['Call Details', 'Readiness', 'Check-In', 'Squad 3', 'Ready', 'No completed checks in this window.']),
    'ic-42-call-check-in-not-active': ('899f0f7fc889940a951d3cd1878f3085b7f45712e6b06a38ce132146977db56f',
        ['Call Details', 'Readiness', 'Check-In', 'No check-in timers active']),
}
SCENES = [
    ('01', 'Identify the incident in Calls', '/calls', ['ic-07-calls'],
     ['Calls', 'Search calls...', '#DEMO-0003', '#DEMO-0002'],
     'IC gives incident commanders, command aides and supervisors a shared place to review an incident. Begin in Calls. The visible cards identify the Vehicle rescue exercise as DEMO zero zero zero three, and the Community medical standby as DEMO zero zero zero two. Each card brings together its name, location and assigned resources. Read those details together before selecting the incident you intend to review. Search calls is above the list when you need to locate another incident.',
     'Locate the Calls list and Search calls, then compare the number, name and resource tags on a fictional incident card.'),
    ('02', 'Confirm the selected call and command context', '/call/51001', ['ic-39-call-context-chicago-map'],
     ['Call Details', 'TRAINING — Warehouse alarm (DEMO-0001)', 'Active Command', 'Open Command Board'],
     'For the detailed review, we use the separate Warehouse alarm exercise, DEMO zero zero zero one. Call Details shows that name and number at the top. Its description says reported smoke at an unoccupied training warehouse, with Squad Three assigned for a search demonstration. Active Command and Open Command Board are visible on the right. Confirm the selected incident before carrying information into a command board; a similar exercise name in the list can refer to a different call.',
     'Confirm the selected incident number and read the exercise description before identifying Open Command Board.'),
    ('03', 'Check the stored incident location and reference tools', '/call/51001', ['ic-39-call-context-chicago-map'],
     ['Training site 1 (fictional), Chicago, IL', 'Notes', 'Images', 'Files', 'Route'],
     'Immediately below the incident description, the map shows the training incident pin in Chicago. The location label reads Training site one, fictional, Chicago, Illinois. Compare that stored location with the incident you are reviewing. It is incident context; it is not evidence of a responder arriving there. Notes, Images, Files and Route sit together below the map. Identify these entry points so you know where to look for supporting information when coordinating with another operator.',
     'Match the incident pin and location label, then locate Notes, Images, Files and Route without treating the pin as a crew position.'),
    ('04', 'Read the complete Readiness result', '/call/51001 → Readiness', ['ic-41-call-readiness-empty-checks'],
     ['Readiness', 'Squad 3', 'Ready', 'No completed checks in this window.'],
     'Scroll to the call tabs and choose Readiness. The selected tab is underlined. In this exercise, the unit row names Squad Three and shows Ready on the right. Read the next line as well: No completed checks in this window. Those two messages are visible together. The Ready label alone does not establish that someone completed an apparatus checklist. During a handover, report the unit name, the displayed status and the evidence message together. That helps the next operator identify what still needs confirmation.',
     'Read Squad 3, Ready and the completed-checks message together. Explain why the status label alone is not proof of a completed checklist.'),
    ('05', 'Inspect the Check-In tab independently', '/call/51001 → Check-In', ['ic-42-call-check-in-not-active'],
     ['Check-In', 'No check-in timers active'],
     'Choose Check-In at the right end of the same tab row. In this exercise, the selected tab says No check-in timers active. That is the current result for this call. It does not show a completed personnel check-in or an accountability result. Keep this observation separate from the unit readiness summary. An operator who only reports Ready has omitted the fact that this call view currently has no active check-in timers.',
     'Locate Check-In and read its actual result. Distinguish an inactive timer view from a completed check-in.'),
    ('06', 'Compare both views before a handover', '/call/51001 → Readiness → Check-In',
     ['ic-41-call-readiness-empty-checks', 'ic-42-call-check-in-not-active'],
     ['Readiness', 'Ready', 'No completed checks in this window.', 'Check-In', 'No check-in timers active'],
     'Compare the two tabs before briefing a relief operator. Readiness shows Squad Three as Ready, with no completed checks in this window. Check-In shows no active timers. A useful handover preserves both statements, instead of turning either one into a blanket assurance about the crew. Resolve missing operational information through your department\'s coordination process. In practice, read each tab aloud and have a colleague identify which facts were actually displayed.',
     'Give a short handover that includes both exact results and keeps missing information explicit.'),
    ('07', 'Carry the verified context into command coordination', '/call/51001', ['ic-39-call-context-chicago-map'],
     ['Call Details', 'Active Command', 'Open Command Board'],
     'Return to the call heading to confirm the incident identity again before moving on to Open Command Board. The same review pattern helps a fire or E M S command aide, a community paramedicine or mental health coordinator, a search-and-rescue lead, a security supervisor, a wildland contractor or an industrial response team. Names and assignments will differ, but the task is the same: identify the incident, read the actual status and evidence messages, then pass on a precise account of what the screens show.',
     'Summarize the incident identity, stored location, readiness evidence and timer state for another authorized operator.'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def prepare(write=False):
    assert datetime.fromisoformat(REVIEWED_AT) <= datetime.now(timezone.utc)
    raw = json.loads(RAW.read_text())
    rows = {row['id']: row for row in raw['screenshots']}
    curated = []
    for ident, (digest, labels) in SOURCES.items():
        row = deepcopy(rows[ident])
        assert sha(S / row['file']) == digest == row['sha256']
        row.update(visible_labels=labels, visible_controls=[], scene_ids=[],
                   eligible_for_lesson=True, review_status='actual_original_image_reviewed')
        row['capture_review'] = {
            'passed': True, 'reviewer': 'Root', 'reviewed_at': REVIEWED_AT,
            'sha256': digest,
            'method': 'Root personally displayed the exact original screenshot bytes with view_image. Only readable literal text in unobstructed app content is retained. No source pixel changes.',
            'notes': 'Archived fictional training captures from October25–26,2026. Not a current live department state or proof of an operational response.'}
        curated.append(row)
    scenes = []
    for ident, title, route, refs, required, narration, practice in SCENES:
        union = {label for ref in refs for label in SOURCES[ref][1]}
        assert set(required) <= union
        scenes.append({'id': ident, 'title': title, 'route': route,
                       'capture_intent': 'Show the exact corresponding actual IC call view. During comparisons, change the shown view with the spoken tab and result.',
                       'capture_refs': refs, 'required_labels': required,
                       'narration': narration, 'practice': practice})
    lesson = {
        'id': NAME, 'title': 'IC: review incident context, unit readiness and check-in status', 'app': 'IC',
        'audience': ['Incident commanders', 'Command aides', 'Department supervisors'],
        'summary': 'Identify the right incident, review its stored location, and compare unit readiness evidence with the call check-in timer state before a handover.',
        'prerequisites': ['An authorized signed-in IC session with permission to view the intended incident.',
                          'A fictional training incident for practice and your department\'s handover process.'],
        'scenes': scenes,
        'sector_examples': [
            {'sector': 'Fire/EMS', 'scenario': 'A command aide reports the incident identity and both readiness and timer messages during relief.'},
            {'sector': 'Community response', 'scenario': 'A community paramedicine or mental health coordinator confirms the selected operational incident and identifies missing readiness evidence.'},
            {'sector': 'Search and rescue', 'scenario': 'A search coordinator distinguishes a stored mission location from proof of a team arriving there.'},
            {'sector': 'Security', 'scenario': 'An event supervisor compares readiness and check-in views before handing a coordination workstation to a colleague.'},
            {'sector': 'Wildland', 'scenario': 'A contractor reports actual crew-unit status and evidence messages without treating an incident pin as a crew position.'},
            {'sector': 'Industrial', 'scenario': 'An exercise coordinator gives a precise briefing from the selected incident and its two status tabs.'}],
        'source_files': [], 'candidate_only': True, 'export_ready': False, 'publication_approved': False,
        'scope_limits': ['Read-only incident context, readiness and inactive check-in timer inspection from actual archived training screens.',
                         'No search-results operation, command creation, response, checklist completion, timer activation, personnel check-in, PAR, GPS or attachment operation is demonstrated.',
                         'The separate completed IC command-board lesson covers command-board operations. This focused lesson does not complete all IC coverage.',
                         'Source proposal only. Actual narration, caption timing, per-cue screen mapping, encoded-frame review and real browser playback remain required.']}
    files = {'lesson.candidate.json': encoded(lesson),
             'narration.txt': ('\n\n'.join(scene['narration'] for scene in scenes) + '\n').encode(),
             'captures.reviewed.json': encoded({'schema_version': 1, 'id': NAME,
                 'raw_manifest': {'file': RAW.relative_to(S).as_posix(), 'sha256': sha(RAW)},
                 'screenshots': curated,
                 'excluded_sources': [{'id': 'ic-40-call-information-tabs',
                     'reason': 'Root viewed this original; overlapping Info fields are not legible enough for learner footage. No Info-field instruction uses this image.'}]}),
             'source-review.json': encoded({'reviewer': 'Root', 'reviewed_at': REVIEWED_AT,
                 'all_four_originals_personally_viewed': True,
                 'source_pixels_changed': False, 'narration_personally_reviewed_against_visible_labels': True,
                 'raw_manifest_sha256': sha(RAW), 'scenes': len(scenes),
                 'holds_untimed': 8, 'distinct_actual_screens': len(curated),
                 'audio_or_video_approval_inferred': False})}
    if write:
        assert not OUT.exists(), 'New-only package; do not overwrite source history.'
        OUT.mkdir()
        for filename, data in files.items():
            with (OUT / filename).open('xb') as stream:
                stream.write(data)
    return {'source_proposal_ready': True, 'written': write, 'scenes': len(scenes),
            'actual_screens': len(curated), 'narration_words': len(files['narration.txt'].decode().split()),
            'lesson_sha256': hashlib.sha256(files['lesson.candidate.json']).hexdigest(),
            'finished_video': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
