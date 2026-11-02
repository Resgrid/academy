"""Bind the actual decoded narration to the frozen screen-map proposal.

This does not create a listening review, instruction approval or finished video.
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
P = Path('expansion/plans') / (NAME + '-cue-map-proposal-20261101')
OUT = Path('expansion/plans') / (NAME + '-complete-correspondence-20261101')
PINS = {
    'correspondence.proposed.json': '354fa2fd29e8ee02ca6b54b7c7773d14d4520ce0df02431d06e9cd23d46cac65',
    'captures.source-relative.json': 'c94aa9bd9fca560986ea6648e0b382dd925a6e6be3687a8c2626ee306a47e14e',
    'lesson.learner-projection.proposed.json': 'f23f838f2bb465de6bc46e993d602079583af37513c84d8f079b91269f791808',
}

AUDIO = Path('expansion/audio') / (NAME + '.m4a')
CAPTIONS = Path('expansion/audio') / (NAME + '.actual.corrected.srt')
QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
AUDIO_PINS = {
    AUDIO: 'db105457eb8f8184e7aa3399f6c38efe200bf358cb1c1a0fdd7bdb8ae79389f7',
    CAPTIONS: 'f569ebb122e98f49fba6de3a83342afc92c0db99e908e2839bc58cb8f3dd9e1f',
    QA: 'e4085c4ae1f93669790e586839a0d7cdddb792f2dfcfb59ecdb95944acd30867',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def prepare(write=False):
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, instruction_scene_digest, _normalized
    from expansion_site import lesson_content_digest

    for name, digest in PINS.items():
        assert sha(S / P / name) == digest, name
    for path, digest in AUDIO_PINS.items():
        assert sha(S / path) == digest, str(path)
    qa = read(S / QA)
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['full_decode'] == 'passed' and qa['audio']['full_scale_samples'] == 0
    assert qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0
    assert qa['audio']['sha256'] == AUDIO_PINS[AUDIO] and qa['corrected_captions']['sha256'] == AUDIO_PINS[CAPTIONS]
    data = deepcopy(read(S / P / 'correspondence.proposed.json'))
    lesson = read(S / data['lesson_file'])
    assert sha(S / data['lesson_file']) == data['lesson_sha256'] == qa['lesson']['sha256']
    manifest = read(S / P / 'captures.source-relative.json')
    rows = {row['id']: row for row in manifest['screenshots']}
    observed = {}
    for row in rows.values():
        assert sha(S / row['file']) == row['sha256']
        if row.get('dom_file'):
            assert sha(S / row['dom_file']) == row['dom_sha256']
        validator = _Validator(S)
        observed[row['id']] = validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
    cues = load_cues(S / CAPTIONS)
    assert len(cues) == len(data['cues']) == 59
    for actual, mapped in zip(cues, data['cues']):
        assert all(actual[key] == mapped[key] for key in ['text', 'start', 'end'])
        labels = {_normalized(label) for label in mapped['required_labels']}
        assert labels <= observed[mapped['screenshot_id']]
        validator = _Validator(S)
        validator.spoken_references(mapped, labels, str(mapped['cue']), True)
        assert not validator.issues, validator.issues
    assert words(' '.join(cue['text'] for cue in cues)) == words(' '.join(scene['narration'] for scene in lesson['scenes']))
    duration = qa['audio']['duration_seconds']
    assert 0 <= duration - data['duration_seconds_provisional'] < 0.1
    data['holds'][-1]['end'] = duration
    data['scenes'][-1]['end'] = duration
    data['scenes'][-1]['screens'][-1]['end'] = duration
    for scene in data['scenes']:
        scene['proposed_mapping_sha256'] = instruction_scene_digest(scene, rows)
    learner = deepcopy(read(S / P / 'lesson.learner-projection.proposed.json'))
    learner['scope_limits'] = [item for item in learner['scope_limits'] if 'Source proposal only' not in item]
    assert lesson_content_digest(learner) == lesson_content_digest(lesson)
    data.update(created_at=datetime.now(timezone.utc).isoformat(), audio_file=str(AUDIO), audio_sha256=AUDIO_PINS[AUDIO],
                captions_file=str(CAPTIONS), captions_sha256=AUDIO_PINS[CAPTIONS], qa_file=str(QA), qa_sha256=AUDIO_PINS[QA],
                duration_seconds=duration, source_images=len(rows), distinct_source_images=len({row['sha256'] for row in rows.values()}),
                learner_content_sha256=lesson_content_digest(learner),
                review_state='complete_audio_and_cue_map_proposal_requires_actual_Root_correspondence_and_User_hearing_reviews')
    data['duration_source'] = 'Complete decode of the specifically approved private Descript Audio export'
    if write:
        destination = S / OUT
        assert not destination.exists()
        destination.mkdir()
        for name in ['captures.source-relative.json', 'cue-screen-correspondence.txt']:
            with (destination / name).open('xb') as stream:
                stream.write((S / P / name).read_bytes())
        for name, value in [('correspondence.proposed.json', data), ('lesson.learner-projection.proposed.json', learner)]:
            (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    return {'passed': True, 'lesson_id': NAME, 'duration_seconds': duration, 'scenes': 7, 'holds': 10,
            'cues': 59, 'source_images': len(rows), 'written': write, 'listening_or_final_video_approval_inferred': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.prepare), indent=2))
