"""Retain the reviewed inventory lesson without altering its original captures.

Default is a read-only preflight. --freeze writes a new source-only package;
it never approves audio, video, publication, or application changes.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

SOURCES = Path(__file__).resolve().parents[1]
ORIGINAL = SOURCES / 'expansion/plans/core-inventory-movements-candidate-20261028'
DESTINATION = SOURCES / 'expansion/plans/core-inventory-movements-capture-freeze-20261028'
NAME = 'core-inventory-movements'
INPUTS = {
    'lesson.candidate.json': 'd418302ddb27c61dcb390b4313a5520eef916ca94dd06b937e015f8fd85267f6',
    'captures.reviewed.json': '281d31686119c2ae542ac7e78d11dd6e698f279759e0db7e3465c149cbad83e2',
    'untimed-screen-sequence.json': '4ab7c20052487c1519a5adb5af14fd7582f20fb1f7e6cf7f111ebb663447c1b6',
    'scenario-fixture.json': '00784d491927e6d348c9f19c913933e7c9c97e94d4ea857b7b6ef142b94cf501',
    'source-citations.json': 'e074d96870548a58631dd4634c1e333f94a02f33a4a5a59ba8aad3fc006dea17',
    'narration.txt': '6fea590f0441a6e9ce676fd1a5a5b5f4e0d5841dae2cc6ad987ae6f5b600e0cb',
}
SECTOR_SENTENCE = (' The same process supports fire and EMS, community paramedicine and mental health response, '
                   'search and rescue, security departments and companies, wildland contractors, '
                   'and industrial emergency response teams.')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def prepare():
    for name, expected in INPUTS.items():
        assert digest(ORIGINAL / name) == expected, 'Changed reviewed input: ' + name
    lesson = json.loads((ORIGINAL / 'lesson.candidate.json').read_text())
    captures = json.loads((ORIGINAL / 'captures.reviewed.json').read_text())
    sequence = json.loads((ORIGINAL / 'untimed-screen-sequence.json').read_text())
    shots = captures['screenshots']
    assert len(lesson['scenes']) == 12 and len(shots) == 16
    by_id = {shot['id']: shot for shot in shots}
    for shot in shots:
        review = shot['capture_review']
        assert shot['eligible_for_lesson'] and review['passed']
        assets = [('file', 'sha256')]
        if 'dom_file' in shot or 'dom_sha256' in shot:
            assert 'dom_file' in shot and 'dom_sha256' in shot
            assets.append(('dom_file', 'dom_sha256'))
        for path_key, hash_key in assets:
            relative = Path(shot[path_key])
            assert not relative.is_absolute() and '..' not in relative.parts
            assert digest(SOURCES / relative) == shot[hash_key]
    for scene in lesson['scenes']:
        refs = scene['capture_evidence']['capture_refs']
        assert refs and set(refs) <= set(by_id)
        union = {label for ref in refs for label in by_id[ref]['visible_labels']}
        assert set(scene['required_labels']) <= union
        scene['capture_refs'] = refs
    final = lesson['scenes'][-1]
    old = final['narration']
    final['narration'] += SECTOR_SENTENCE
    changed = 0
    for spans in sequence.values():
        if isinstance(spans, list):
            for span in spans:
                if isinstance(span, dict) and span.get('scene_id') == final['id']:
                    assert span['narration_exact'] == old
                    span['narration_exact'] = final['narration']
                    changed += 1
    assert changed == 1
    lesson['audience'] = ['Inventory administrators', 'Stock coordinators', 'Department administrators']
    lesson.update(candidate_only=True, export_ready=False, publication_approved=False,
                  source_complete=True, narration_word_count=sum(len(s['narration'].split()) for s in lesson['scenes']))
    final['narration_word_count'] = len(final['narration'].split())
    review = {'lesson_id': NAME, 'reviewer': 'Codex parent independent original-size source review',
              'reviewed_at': '2026-10-28T21:37:00+00:00',
              'actual_source_images_inspected': 16,
              'inputs': INPUTS, 'source_only': True, 'publication_approved': False,
              'notes': ['All sixteen original 1434x773 JPEGs were viewed independently by the parent.',
                        'Catalogue and lot setup are reviewed, with receipt/transfer/issue actions and saved results.',
                        'Partial return is a result review; its intervening entry form is not pictured.',
                        'Balances14/5/1 are a dated snapshot before later usage; current demo balances differ.',
                        'Report chooser and resolved low-stock alert do not establish a generated report or expiry alert.',
                        'These legacy source records retain screenshot provenance and pixel reviews; no new DOM capture is invented.',
                        'Final narration adds the same six department sectors without naming another unseen control.']}
    files = {NAME + '.narrated-source.json': encoded(lesson),
             'captures.reviewed.json': encoded(captures), 'untimed-screen-sequence.json': encoded(sequence),
             'narration.txt': ('\n\n'.join(s['narration'] for s in lesson['scenes']) + '\n').encode(),
             'parent-source-review.json': encoded(review)}
    for name in ['scenario-fixture.json', 'source-citations.json']:
        files[name] = (ORIGINAL / name).read_bytes()
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    files = prepare()
    if args.freeze:
        assert not DESTINATION.exists(), 'Frozen package already exists; do not overwrite it.'
        DESTINATION.mkdir()
        for name, data in files.items():
            (DESTINATION / name).write_bytes(data)
    print(json.dumps({'source_preflight': 'passed', 'frozen': args.freeze,
                      'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}, indent=2))
