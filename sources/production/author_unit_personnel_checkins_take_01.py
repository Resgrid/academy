"""Build the explicit Unit check-in screen plan from genuine exported speech.

Requires a completed listening review and the retained full-decode/cue-energy QA.
Does not render, publish, invent timings, or alter the frozen narration/captures.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
BASE = Path('expansion/plans/app-unit-personnel-checkins-capture-freeze-20261028-v2')
NAME = 'app-unit-personnel-checkins'
FROZEN = '23da16ac8965316b1d2d569cf6621323facb1d2b54f38789cb9fb324e1487c9a'
RANGES = [(1, 8), (9, 16), (17, 24), (25, 32), (33, 39), (40, 47)]
REFERENCES = {1: ['Calls'], 4: ['No Active Call'], 9: ['Check-In'],
              10: ['Personnel'], 17: ['History'], 18: ['Personnel'],
              25: ['Check In', 'Personnel'], 27: ['Add note'],
              29: ['Confirm Check-In'], 33: ['Personnel'], 35: ['OK'],
              40: ['History']}
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, validate_inputs


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(relative):
    return json.loads((SOURCES / relative).read_text())


def build(listening_review):
    lesson_path = SOURCES / BASE / (NAME + '.narrated-source.json')
    assert sha(lesson_path) == FROZEN, 'Frozen lesson changed.'
    lesson = json.loads(lesson_path.read_text())
    manifest = read(BASE / 'captures.reviewed.json')
    records = manifest['screenshots']
    assert len(records) == 6 and len(lesson['scenes']) == 6
    for row in records:
        assert row['eligible_for_lesson'] and sha(SOURCES / row['file']) == row['sha256']
        assert sha(SOURCES / row['dom_file']) == row['dom_sha256']
    audio = Path('expansion/audio/' + NAME + '.m4a')
    captions = Path('expansion/audio/' + NAME + '.corrected.srt')
    qa_file = Path('expansion/audio/' + NAME + '.actual.qa.json')
    qa = read(qa_file)
    assert qa['passed'] and not qa['possible_speech_gaps'] and not qa['issues']
    assert qa['lesson']['sha256'] == FROZEN and qa['lesson']['words'] == 424
    assert qa['audio']['sha256'] == sha(SOURCES / audio)
    assert qa['corrected_captions']['sha256'] == sha(SOURCES / captions)
    assert qa['raw_captions']['cues'] == qa['corrected_captions']['cues'] == 47
    assert qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0
    reviewed = json.loads(Path(listening_review).read_text())
    assert reviewed['complete_natural_narration'] is True
    assert reviewed['audio_sha256'] == qa['audio']['sha256']
    assert reviewed['lesson_sha256'] == FROZEN
    assert reviewed['reviewer'] and reviewed['reviewed_at'] and reviewed['evidence']
    cues = load_cues(SOURCES / captions)
    duration = qa['audio']['duration_seconds']
    assert len(cues) == 47
    now = datetime.now(timezone.utc).isoformat()
    scenes = []
    for index, ((first, last), authored) in enumerate(zip(RANGES, lesson['scenes'])):
        assert ' '.join(c['text'] for c in cues[first-1:last]).split() == authored['narration'].split()
        start = 0 if index == 0 else cues[first-1]['start']
        end = duration if index == 5 else cues[RANGES[index+1][0]-1]['start']
        selected = records[index]
        screens = [{'screenshot_id': selected['id'], 'start': start, 'end': end}]
        # Cue25 names the card action. Keep the unobscured card until the form
        # is described at the real start of cue26, not an estimated word time.
        if index == 3:
            cut = cues[25]['start']
            screens = [{'screenshot_id': records[1]['id'], 'start': start, 'end': cut},
                       {'screenshot_id': selected['id'], 'start': cut, 'end': end}]
        mapped = []
        for number in range(first, last+1):
            picture = records[1] if number == 25 else selected
            labels = REFERENCES.get(number, [])
            assert set(labels) <= set(picture['visible_labels'])
            mapped.append({'cue': number, 'screenshot_id': picture['id'],
                           'required_labels': labels, 'instructional': bool(labels)})
        scenes.append({'id': authored['id'], 'start': start, 'end': end,
                       'screens': screens, 'captions': mapped})
    result = {'schema_version': 1, 'lesson_id': NAME, 'duration_seconds': duration,
        'display_context': 'TRAINING ONLY · fictional community care check-in',
        'narration': {'file': str(audio), 'sha256': sha(SOURCES/audio),
            'kind': 'approved_natural_narration', 'approval': {
                'reviewer': reviewed['reviewer'], 'reviewed_at': reviewed['reviewed_at'],
                'sha256': sha(SOURCES/audio), 'complete_natural_narration': True,
                'evidence': reviewed['evidence'], 'qa_file': str(qa_file),
                'qa_sha256': sha(SOURCES/qa_file)}},
        'captions': {'file': str(captions), 'sha256': sha(SOURCES/captions),
            'kind': 'speech_timed_srt', 'approval': {
                'reviewer': 'Codex exact full-script/exported-cue correspondence',
                'reviewed_at': now, 'sha256': sha(SOURCES/captions),
                'audio_sha256': sha(SOURCES/audio), 'speech_timing_reviewed': True}},
        'capture_manifests': [{'file': str(BASE/'captures.reviewed.json'),
                              'sha256': sha(SOURCES/BASE/'captures.reviewed.json')}],
        'screenshot_reviews': {r['id']: {'reviewer': 'Codex actual original-size JPEG inspection',
            'reviewed_at': now, 'sha256': r['sha256'], 'application_visible': True,
            'labels_legible': True, 'no_errors': True} for r in records},
        'scenes': scenes, 'publishable': False,
        'limitations': ['Personnel software check-ins only; no hardware location, warning transition or external alert delivery demonstration.']}
    return result, lesson_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--listening-review', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    plan, lesson_path = build(args.listening_review)
    assert not args.output.exists(), 'Use a new plan path.'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False)+'\n')
    recipe = validate_inputs(lesson_path, args.output, SOURCES)
    print(json.dumps({'passed': True, 'scenes': len(recipe['scenes']),
        'cues': len(recipe['cues']), 'duration': recipe['duration'],
        'screens': len(recipe['screenshots']), 'rendered': False}))
