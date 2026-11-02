"""Retain complete screen timing plans while actual narration exports are pending.

These are authoring inputs, not qualified render plans or listening receipts.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))

CONFIG = {
    'summaries': {
        'id': 'app-bigboard-readiness-summaries',
        'proposal': 'app-bigboard-readiness-summaries-source-proposal-20261101',
        'lesson_sha256': '526c9514f3de7d561f772d247ed21cf93bc4b4401c9e9243d2a55027fd32291a',
        'manifest_sha256': 'e34daec58abf9aca5034c11bee152a2a50a47dba425038cc35b25c0228968fb0',
        'srt': 'app-bigboard-readiness-summaries.raw.srt',
        'srt_sha256': '1c7c6f4ec54cc9041bac99de9a4b0077a59c576c2fc92dfc2142531059b45c72',
        'cues': 70, 'composition_seconds': 252.0,
        'spans': [('01', 1, 4, 1), ('01', 5, 8, 3), ('02', 9, 17, 3),
                  ('03', 18, 20, 3), ('03', 21, 25, 4), ('03', 26, 27, 5),
                  ('04', 28, 32, 5), ('04', 33, 36, 9), ('05', 37, 38, 5),
                  ('05', 39, 45, 9), ('06', 46, 53, 9), ('07', 54, 56, 8),
                  ('07', 57, 61, 10), ('08', 62, 70, 8)],
    },
    'timers': {
        'id': 'app-bigboard-unit-status-timers',
        'proposal': 'app-bigboard-unit-status-timers-source-proposal-20261101-v2',
        'lesson_sha256': 'b5efa8866435494c00c03d9423afd1af2d64583f59bcb68602ec31b5f8eede80',
        'manifest_sha256': 'a5260fd12f39df94fb1512707fe8465cdd8c3bbf5669afc6de6e9560c0253c07',
        'srt': 'app-bigboard-unit-status-timers.raw.v2.srt',
        'srt_sha256': '22369caf37916d424d6b714e72b1e692c209a0d5212665827a5a02aac53fdc8b',
        'cues': 85, 'composition_seconds': 294.56,
        'spans': [('01', 1, 3, 1), ('01', 4, 8, 3), ('02', 9, 10, 2),
                  ('02', 11, 17, 4), ('03', 18, 25, 5), ('04', 26, 30, 6),
                  ('04', 31, 32, 7), ('04', 33, 35, 8), ('05', 36, 43, 9),
                  ('06', 44, 46, 10), ('06', 47, 47, 11), ('06', 48, 52, 13),
                  ('07', 53, 53, 12), ('07', 54, 56, 14), ('07', 57, 58, 15),
                  ('07', 59, 60, 21), ('08', 61, 61, 15), ('08', 62, 64, 16),
                  ('08', 65, 65, 17), ('08', 66, 69, 18), ('09', 70, 70, 18),
                  ('09', 71, 73, 19), ('09', 74, 77, 20), ('10', 78, 85, 20)],
    },
}


def prepare(key, write=False):
    from render_walkthrough import load_cues, words
    c = CONFIG[key]
    base = S / 'expansion/plans' / c['proposal']
    lesson_file, manifest_file = base / 'lesson.candidate.json', base / 'captures.reviewed.json'
    srt_file = S / 'expansion/audio' / c['srt']
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for path, expected in [(lesson_file, c['lesson_sha256']), (manifest_file, c['manifest_sha256']), (srt_file, c['srt_sha256'])]:
        assert sha(path) == expected, str(path)
    lesson = json.loads(lesson_file.read_text())
    manifest = json.loads(manifest_file.read_text())
    numbered = {int(row['id'][:3]): row for row in manifest['screenshots']}
    for row in numbered.values():
        assert sha(S / row['file']) == row['sha256']
        assert sha(S / row['dom_file']) == row['dom_sha256']
    cues = load_cues(srt_file)
    assert len(cues) == c['cues']
    assert words(' '.join(cue['text'] for cue in cues)) == words(' '.join(scene['narration'] for scene in lesson['scenes']))
    holds, entries = [], []
    for i, (scene, first, last, number) in enumerate(c['spans']):
        row = numbered[number]
        start = 0.0 if i == 0 else cues[first - 1]['start']
        end = cues[c['spans'][i + 1][1] - 1]['start'] if i + 1 < len(c['spans']) else c['composition_seconds']
        holds.append(dict(scene_id=scene, first_cue=first, last_cue=last, screenshot_id=row['id'],
                          screenshot_sha256=row['sha256'], start=start, end=end))
        for n in range(first, last + 1):
            cue = cues[n - 1]
            assert start <= cue['start'] < cue['end'] <= end
            entries.append(dict(cue=n, scene_id=scene, screenshot_id=row['id'], **cue))
    assert [e['cue'] for e in entries] == list(range(1, len(cues) + 1))
    for scene in lesson['scenes']:
        selected = [e for e in entries if e['scene_id'] == scene['id']]
        assert words(' '.join(e['text'] for e in selected)) == words(scene['narration'])
    plan = dict(recorded_at=datetime.now(timezone.utc).isoformat(), lesson_id=c['id'],
                lesson_file=lesson_file.relative_to(S).as_posix(), lesson_sha256=c['lesson_sha256'],
                manifest_file=manifest_file.relative_to(S).as_posix(), manifest_sha256=c['manifest_sha256'],
                captions_file=srt_file.relative_to(S).as_posix(), captions_sha256=c['srt_sha256'],
                timeline_seconds=c['composition_seconds'],
                duration_source='Descript composition metadata; complete local audio decode remains pending.',
                scene_count=len(lesson['scenes']), cue_count=len(cues), hold_count=len(holds),
                actual_source_screens=len(numbered), holds=holds, cues=entries,
                review_state='pending_audio_export_decode_listening_and_final_literal_cue_review',
                qualified=False, final_render_inputs=False, human_listening_approval_inferred=False,
                notes=['Every cue has an actual reviewed application image assigned; all current script words and paragraph boundaries match.',
                       'Final preparation must bind the downloaded audio and its QA, review every literal/spoken control reference, measure caption layout, and use the normal qualification pipeline.',
                       'These files do not authorize a share export or establish audio audibility, final encoded pixels or browser playback.'])
    if write:
        destination = base / 'screen-timing.pending.json'
        assert not destination.exists()
        destination.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + '\n')
    return dict(lesson_id=c['id'], scenes=len(lesson['scenes']), cues=len(cues), holds=len(holds),
                source_screens=len(numbered), all_cues_assigned=True, qualified=False, written=write)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=CONFIG)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.lesson, args.write), indent=2))
