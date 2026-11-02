"""Propose exact real-screen cuts from the generated IC narration's SRT.

No complete audio, listening, final frame or browser review is inferred.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'app-ic-call-context-readiness-review'
BASE = Path('expansion/plans') / (NAME + '-source-proposal-20261101')
CAPTIONS = Path('expansion/audio') / (NAME + '.actual.raw.srt')
DESTINATION = Path('expansion/plans') / (NAME + '-cue-map-proposal-20261101')
CALLS = 'ic-07-calls'
CONTEXT = 'ic-39-call-context-chicago-map'
READINESS = 'ic-41-call-readiness-empty-checks'
CHECKIN = 'ic-42-call-check-in-not-active'
NATURE = 'Exercise: reported smoke at an unoccupied training warehouse. Squad 3 assigned for a search demonstration.'
TITLE = 'TRAINING — Warehouse alarm (DEMO-0001)'
LOCATION = 'Training site 1 (fictional), Chicago, IL'
NO_CHECKS = 'No completed checks in this window.'
NO_TIMERS = 'No check-in timers active'
SPANS = [
    ('01', 1, 9, CALLS),
    ('02', 10, 17, CONTEXT),
    ('03', 18, 25, CONTEXT),
    ('04', 26, 35, READINESS),
    ('05', 36, 40, CHECKIN),
    ('05', 41, 41, READINESS),
    ('05', 42, 42, CHECKIN),
    ('06', 43, 44, READINESS),
    ('06', 45, 51, CHECKIN),
    ('07', 52, 59, CONTEXT),
]
REFERENCES = {
    3: {'Calls': 'Calls'},
    4: {'TRAINING — Vehicle rescue exercise': 'Vehicle rescue exercise'},
    5: {'TRAINING — Community medical standby': 'Community medical standby', '#DEMO-0002': 'DEMO zero zero zero two'},
    9: {'Search calls...': 'Search calls'},
    10: {TITLE: 'Warehouse alarm'},
    11: {TITLE: 'DEMO zero zero zero one'},
    12: {'Call Details': 'Call Details'},
    13: {NATURE: 'reported smoke at an unoccupied training warehouse'},
    14: {NATURE: 'Three assigned for a search demonstration'},
    15: {'Active Command': 'Active Command', 'Open Command Board': 'Open Command Board'},
    20: {LOCATION: 'Training site one, fictional, Chicago, Illinois'},
    23: {'Notes': 'Notes', 'Images': 'Images', 'Files': 'Files', 'Route': 'Route'},
    26: {'Readiness': 'Readiness'},
    27: {'Readiness': 'selected tab'},
    28: {'Squad 3': 'Squad Three', 'Ready': 'Ready'},
    29: {NO_CHECKS: 'No completed checks in this window'},
    31: {'Ready': 'Ready'},
    36: {'Check-In': 'Check-In'},
    37: {'Check-In': 'selected tab', NO_TIMERS: 'No check-in timers active'},
    41: {'Ready': 'Ready'},
    42: {NO_TIMERS: 'no active check-in timers'},
    44: {'Readiness': 'Readiness', 'Squad 3': 'Squad Three', 'Ready': 'Ready', NO_CHECKS: 'no completed checks in this window'},
    45: {'Check-In': 'Check-In', NO_TIMERS: 'no active timers'},
    52: {'Call Details': 'call heading'},
    53: {'Open Command Board': 'Open Command Board'},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest

    pins = {
        BASE / 'lesson.candidate.json': 'd8b7588ede72732c72670ff65c4aff7df055c764364c764b6ab106ca90b5a232',
        BASE / 'captures.reviewed.json': 'c94aa9bd9fca560986ea6648e0b382dd925a6e6be3687a8c2626ee306a47e14e',
        CAPTIONS: '9e87e7cb2557c5a3b735c76f73bf06b7a07c3cb40f457556a65214fb117d124c',
    }
    for path, expected in pins.items():
        assert sha(S / path) == expected, str(path)
    lesson = json.loads((S / BASE / 'lesson.candidate.json').read_text())
    manifest = json.loads((S / BASE / 'captures.reviewed.json').read_text())
    rows = {row['id']: row for row in manifest['screenshots']}
    observed = {}
    for row in rows.values():
        assert sha(S / row['file']) == row['sha256']
        validator = _Validator(S)
        observed[row['id']] = validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
    cues = load_cues(S / CAPTIONS)
    assert len(cues) == 59
    assert words(' '.join(cue['text'] for cue in cues)) == words(' '.join(scene['narration'] for scene in lesson['scenes']))
    duration = 209.52  # Generated composition metadata; not a decoded container.
    holds, entries = [], []
    for index, (scene_id, first, last, screenshot) in enumerate(SPANS):
        start = 0.0 if index == 0 else cues[first - 1]['start']
        end = cues[SPANS[index + 1][1] - 1]['start'] if index + 1 < len(SPANS) else duration
        holds.append({'scene_id': scene_id, 'screenshot_id': screenshot, 'first_cue': first,
                      'last_cue': last, 'start': start, 'end': end})
        for number in range(first, last + 1):
            cue = cues[number - 1]
            aliases = REFERENCES.get(number, {})
            assert cue['start'] >= start and cue['end'] <= end
            labels = {_normalized(label) for label in aliases}
            assert labels <= observed[screenshot], (number, screenshot)
            entry = dict(cue, cue=number, scene_id=scene_id, screenshot_id=screenshot,
                         required_labels=list(aliases), spoken_references=aliases, instructional=bool(aliases))
            validator = _Validator(S)
            validator.spoken_references(entry, labels, str(number), True)
            assert not validator.issues, validator.issues
            entries.append(entry)
    assert [entry['cue'] for entry in entries] == list(range(1, 60))
    learner = deepcopy(lesson)
    scenes = []
    for original, projection in zip(lesson['scenes'], learner['scenes']):
        selected = [hold for hold in holds if hold['scene_id'] == original['id']]
        selected_cues = [{key: value for key, value in row.items() if key != 'scene_id'}
                        for row in entries if row['scene_id'] == original['id']]
        assert words(' '.join(row['text'] for row in selected_cues)) == words(original['narration'])
        assert {_normalized(label) for label in original['required_labels']} <= set().union(*(observed[hold['screenshot_id']] for hold in selected))
        projection['capture_refs'] = list(dict.fromkeys([*projection['capture_refs'], *[hold['screenshot_id'] for hold in selected]]))
        scene = {'id': original['id'], 'title': original['title'], 'kind': 'operational',
                 'start': selected[0]['start'], 'end': selected[-1]['end'],
                 'visual_required_labels': original['required_labels'],
                 'screens': [{key: hold[key] for key in ['screenshot_id', 'start', 'end']} for hold in selected],
                 'captions': selected_cues}
        scene['proposed_mapping_sha256'] = instruction_scene_digest(scene, rows)
        scenes.append(scene)
    assert lesson_content_digest(lesson) == lesson_content_digest(learner)
    proposal = {
        'created_at': datetime.now(timezone.utc).isoformat(), 'lesson_id': NAME,
        'lesson_file': str(BASE / 'lesson.candidate.json'), 'lesson_sha256': pins[BASE / 'lesson.candidate.json'],
        'captions_file': str(CAPTIONS), 'captions_sha256': pins[CAPTIONS],
        'duration_seconds_provisional': duration,
        'duration_source': 'Generated Descript composition metadata. Approved exported-container audio QA pending.',
        'scenes': scenes, 'holds': holds, 'cues': entries, 'cue_count': len(cues),
        'scenes_count': len(scenes), 'holds_count': len(holds), 'distinct_source_images_used': len(rows),
        'learner_content_sha256': lesson_content_digest(learner),
        'review_state': 'proposal_only_no_audio_decoding_hearing_encoded_or_browser_approval_inferred',
        'export_ready': False,
    }
    if write:
        destination = S / DESTINATION
        assert not destination.exists()
        destination.mkdir()
        for filename, data in [('captures.source-relative.json', manifest),
                               ('correspondence.proposed.json', proposal),
                               ('lesson.learner-projection.proposed.json', learner)]:
            (destination / filename).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        (destination / 'cue-screen-correspondence.txt').write_text('\n\n'.join(
            f"Cue{row['cue']:03} · scene{row['scene_id']} · {row['start']:.3f}–{row['end']:.3f} · {row['screenshot_id']}\n{row['text']}\nLiteral → exact speech: {json.dumps(row['spoken_references'], ensure_ascii=False)}"
            for row in entries) + '\n')
    return {'passed': True, 'lesson_id': NAME, 'scenes': len(scenes), 'holds': len(holds),
            'actual_cues': len(cues), 'actual_source_images': len(rows), 'written': write,
            'decoded_audio_or_listening_or_final_video_approval': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
