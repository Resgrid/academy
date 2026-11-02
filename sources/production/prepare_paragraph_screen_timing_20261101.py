"""Map exact exported speech cues to single-screen paragraphs, without rendering.

Default is read-only. --prepare writes a new timing proposal. This uses actual
SRT endpoints only; it refuses a paragraph boundary inside a cue. Exported audio,
genuine hearing, complete correspondence review and final video checks are still
required. It cannot mark a lesson ready or create any review approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

S = Path(__file__).resolve().parents[1]
CONFIG = {
    'responder-trade': {
        'id': 'app-responder-shift-trade-request-cancel',
        'base': 'expansion/plans/app-responder-shift-trade-request-cancel-source-proposal-20261101',
        'lesson_sha256': '922f6d54e7aaca8115fa71547dc6da063abe2988fc5725d09740e35172bc9d92',
        'manifest_sha256': '7383d224b26707e533f372c726b97b7ff188aae3a514e0f8a1209e7d93da0da7',
        'srt_sha256': 'acbb683c1d6b1cd7bce88533a67da30a5dee01d14a1474544ada0ae82e1cde37',
        'cue_count': 84,
    },
    'records-analytics': {
        'id': 'core-records-analytics-summary-workload',
        'base': 'expansion/plans/core-records-analytics-summary-workload-source-proposal-20261101',
        'lesson_sha256': 'e7d697afba265c7fa8194f8bd0cf101a89dbaff2299ac7d94f607aefc7c8c866',
        'manifest_sha256': '128ec414ea1f66df5130b3d06d11bb2f1125065b9b87960f53689cf3309540e6',
        'srt_sha256': '5eed8676566625069ca29f5dde65dda916dd61c7eaced810e7394b7e39fe8272',
        'cue_count': 111,
    },
    'responder-signup': {'id': 'app-responder-shift-signup-withdraw', 'base': 'expansion/plans/app-responder-shift-signup-withdraw-source-proposal-20261101', 'lesson_sha256': '605e830bca85624daec2f623a21fcce9dd791fef5c2618ad21c85d0629237e53', 'manifest_sha256': 'c1187755e44a9db27d66618d0bcdf1e311e59c0fa91b029ed529d8fd795114bf', 'srt_sha256': '6b4d868d4f560c6a61694e9612ad9eaefa738c0b726b727b950d21babea897d6', 'cue_count': 55},
    'records-amendment': {
        'id': 'core-records-amendment-and-revisions',
        'base': 'expansion/plans/core-records-amendment-and-revisions-source-proposal-20261101',
        'lesson_sha256': '41ae73e165868b28fa20902934555d7ceac609e736d165a4db7c7dffcf969171',
        'manifest_sha256': 'e59787238f3422358f134eb236284bffd5b8ee2a6797a6b2cdaeb147c5f9716b',
        'srt_sha256': '50674b8ad51fa1712d7e516621001d28479936106806169f12f787fade839b63',
        'cue_count': 102,
    },
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return ' '.join(text.split())


def seconds(value):
    h, m, s, ms = map(int, re.split('[:,]', value))
    return h * 3600 + m * 60 + s + ms / 1000


def propose(key):
    c = CONFIG[key]
    base = Path(c['base'])
    lesson_file, manifest_file = base / 'lesson.candidate.json', base / 'captures.reviewed.json'
    srt_file = Path('expansion/audio') / (c['id'] + '.actual-raw.srt')
    for file, digest in [(lesson_file, c['lesson_sha256']), (manifest_file, c['manifest_sha256']), (srt_file, c['srt_sha256'])]:
        assert sha(S / file) == digest, 'Changed frozen input: ' + str(file)
    lesson = json.loads((S / lesson_file).read_text())
    rows = {r['id']: r for r in json.loads((S / manifest_file).read_text())['screenshots']}
    cues, previous = [], 0.0
    for block in re.split(r'\n\s*\n', (S / srt_file).read_text().strip()):
        lines = block.splitlines()
        match = re.fullmatch(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
        assert match and int(lines[0]) == len(cues) + 1
        start, end = map(seconds, match.groups())
        assert start >= previous and end > start
        previous = end
        cues.append({'cue': int(lines[0]), 'start': start, 'end': end, 'text': normalized(' '.join(lines[2:]))})
    assert len(cues) == c['cue_count']
    assert normalized(' '.join(x['text'] for x in cues)) == normalized(' '.join(x['narration'] for x in lesson['scenes']))
    cursor, scenes = 0, []
    for scene in lesson['scenes']:
        assert len(scene['capture_refs']) == 1
        row = rows[scene['capture_refs'][0]]
        assert sha(S / row['file']) == row['sha256']
        assert sha(S / row['dom_file']) == row['dom_sha256']
        assert set(scene['required_labels']) <= set(row['visible_labels'])
        text, selected = '', []
        target = normalized(scene['narration'])
        while text != target:
            assert cursor < len(cues), 'Missing exact paragraph audio cues.'
            cue = cues[cursor]
            text = normalized(text + ' ' + cue['text'])
            assert target.startswith(text), 'Paragraph crosses a cue boundary; real word timing is required.'
            selected.append(cue)
            cursor += 1
        scenes.append({'scene_id': scene['id'], 'title': scene['title'],
                       'narration_exact': scene['narration'], 'practice_exact': scene['practice'],
                       'capture_id': row['id'], 'image_file': row['file'], 'image_sha256': row['sha256'],
                       'required_pixel_labels': scene['required_labels'],
                       'speech_start_seconds': selected[0]['start'], 'speech_end_seconds': selected[-1]['end'],
                       'cue_numbers': [x['cue'] for x in selected], 'actual_exported_cues': selected})
    assert cursor == len(cues)
    return {'lesson_id': c['id'], 'source_lesson': str(lesson_file), 'source_lesson_sha256': c['lesson_sha256'],
            'source_manifest': str(manifest_file), 'source_manifest_sha256': c['manifest_sha256'],
            'actual_srt': str(srt_file), 'actual_srt_sha256': c['srt_sha256'],
            'exact_complete_script_match': True, 'actual_cue_count': len(cues), 'scenes': scenes,
            'word_timing_interpolated': False, 'proposal_only': True, 'export_ready': False,
            'remaining': ['Authorized audio export, complete decoding and non-silent cue checks.',
                          'Genuine complete natural-narration listening review.',
                          'Full correspondence and geometry review before final authoring.',
                          'Complete encoded screen/caption review and advancing browser playback.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=CONFIG)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    proposal = propose(args.lesson)
    path = S / 'expansion/plans' / (proposal['lesson_id'] + '-actual-cue-proposal-20261101.json')
    if args.prepare:
        with path.open('x') as stream:
            json.dump(proposal, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({'lesson_id': proposal['lesson_id'], 'actual_cues': proposal['actual_cue_count'],
                      'single_screen_paragraphs': len(proposal['scenes']), 'exact_script': True,
                      'word_timing_interpolated': False, 'written': args.prepare,
                      'export_ready': False, 'audio_or_video_approval_created': False}))
