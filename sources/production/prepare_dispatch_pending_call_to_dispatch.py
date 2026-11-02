"""Prepare an immutable, unvoiced Dispatch pending-call source freeze.

Offline plan/check is the default. --freeze writes only a new v2 source folder
and requires the pinned Dispatch source checkout. No browser, database, private
credential, provider, audio, timing, rendering, canonical or site operation occurs.
Replay the separate scenario through normal UI and read its new identity fresh.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
V1 = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-candidate-20261028')
OUT = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-capture-freeze-20261028-v2')
NAME = 'app-dispatch-pending-call-to-dispatch'
SCENARIO = Path('demo/scenarios/dispatch-pending-call.json')
FROZEN_AT = '2026-10-28T20:59:43Z'
SECTOR_SENTENCE = ('The same prepare and review pattern can serve fire and EMS, '
                   'community care and mental health teams, search and rescue, '
                   'security, wildland contractors, and industrial teams.')
PINS = {
    V1 / (NAME + '.narrated-source.json'): '181a5f5b7898e210d5478535aca643210a10c60a4a5a6e5e865573ccf0f0b3c0',
    V1 / 'narration.txt': '12eb86868cd120ef8537bf272c8a36d9a07d948e3f6d9a573eb50bb8d8b74db4',
    V1 / 'screen-sequence.untimed.json': '8fd307f80cded05e0908ed35db904944855f8b94b79907f93d8c92290dc0b618',
    V1 / 'source-preflight.json': '1c04013aa505975866f0c0b54ced36a932b66ee139a60895d0f0dabad967d3bb',
    V1 / 'validation.json': '50828d89c364fae6c08c8b17044efcaf714b3bc5b3aec0e8690ca10ff1525476',
    Path('captures/expansion/dispatch-pending-20261028/manifest.json'): '599285e558fb5acb32a006a82c670196a3463f78cb67eedf2ca604854ce3f254',
    Path('captures/expansion/dispatch-pending-20261028/action-ledger.json'): 'a7d25f3c52d57d49cc0ce1e02fa89a4c0d5e5c33046e6725b6f89ea796da0399',
    Path('captures/expansion/dispatch-pending-20261028/review/reviewed-source-subset-20261028.json'): 'b84a9502937ba0b15a8b58b8cf396af88eebaf421a89a11291c16e34c3467d8f',
    Path('captures/expansion/dispatch-pending-20261028/review/source-pixel-privacy-review-20261028.json'): '881f4cb09147e224cfada2d1195de97ccc7f21480083f75b96f5a2128f80e7e9',
    SCENARIO: '5c7a54d60005013889efe11a7ca9ff2754b543a5b5dc316d1b96e1f67d0c414a',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(relative):
    return json.loads((SOURCES / relative).read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def require_pin(path, expected):
    if not path.is_file() or digest(path) != expected:
        raise ValueError('Pinned input is missing or changed: ' + str(path))


def validate_inputs():
    for relative, expected in PINS.items():
        require_pin(SOURCES / relative, expected)
    prior = read(V1 / 'source-preflight.json')
    raw = read(Path(prior['raw_manifest']['file']))
    review = read(Path(prior['capture_review']['file']))
    assert len(raw['captures']) == 25 and len(review['screenshots']) == 20
    for row in raw['captures']:
        require_pin(SOURCES / row['file'], row['sha256'])
        require_pin(SOURCES / row['dom_file'], row['dom_sha256'])
    by_id = {r['id']: r for r in review['screenshots']}
    for row in by_id.values():
        assert row['eligible_for_lesson'] is True
        assert row['capture_review']['passed'] is True
        assert row['capture_review']['sha256'] == row['sha256']
        assert row['capture_review']['no_errors'] is True
    rejected = {r['id'] for r in review['rejected_sources']}
    lesson = read(V1 / (NAME + '.narrated-source.json'))
    for scene in lesson['scenes']:
        ids = [r['screenshot_id'] for r in scene['capture_evidence']['capture_refs']]
        assert not set(ids) & rejected
        labels = {label for ident in ids for label in by_id[ident]['visible_labels']}
        assert set(scene['required_labels']) <= labels
    assert len(lesson['sector_examples']) == 6
    return lesson, prior, review


def build():
    lesson, prior, review = validate_inputs()
    lesson = copy.deepcopy(lesson)
    original_final = lesson['scenes'][-1]['narration']
    marker = 'This browser exercise confirms these application records;'
    assert original_final.count(marker) == 1 and SECTOR_SENTENCE not in original_final
    lesson['scenes'][-1]['narration'] = original_final.replace(marker, SECTOR_SENTENCE + ' ' + marker)
    lesson['candidate_status'] = 'Frozen unvoiced narrated source v2; no audio, timing, media or publication qualification.'
    citations = []
    for row in prior['source_file_pins']:
        logical = Path(row['file'])
        retained = OUT / 'source' / logical
        citations.append({'logical_source': logical.as_posix(), 'file': retained.as_posix(), 'sha256': row['sha256']})
    lesson['source_files'] = [r['file'] for r in citations]
    assert lesson['scenes'][:-1] == read(V1 / (NAME + '.narrated-source.json'))['scenes'][:-1]
    assert lesson['scenes'][-1]['narration'].replace(SECTOR_SENTENCE + ' ', '') == original_final
    return lesson, prior, review, citations


def freeze(dispatch_source):
    out = SOURCES / OUT
    if out.exists():
        raise ValueError('Preserve the held v2 freeze; use --check or author a new version.')
    lesson, prior, review, citations = build()
    if dispatch_source is None:
        raise ValueError('--freeze requires --dispatch-source pointing to the matching read-only source checkout.')
    dispatch_source = dispatch_source.resolve()
    for citation in citations:
        logical = Path(citation['logical_source'])
        assert logical.parts[0] == 'Dispatch'
        require_pin(dispatch_source / Path(*logical.parts[1:]), citation['sha256'])
    # All input/source guards passed before the first output write.
    out.mkdir(parents=True)
    for citation in citations:
        logical = Path(citation['logical_source'])
        dest = SOURCES / citation['file']
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((dispatch_source / Path(*logical.parts[1:])).read_bytes())
    dump(out / (NAME + '.narrated-source.json'), lesson)
    (out / 'narration.txt').write_text('\n\n'.join(s['narration'] for s in lesson['scenes']) + '\n')
    (out / 'captures.reviewed.json').write_bytes((SOURCES / prior['capture_review']['file']).read_bytes())
    (out / 'scenario.json').write_bytes((SOURCES / SCENARIO).read_bytes())
    dump(out / 'source-citations.json', citations)
    sequence = read(V1 / 'screen-sequence.untimed.json')
    sequence['lesson_sha256'] = digest(out / (NAME + '.narrated-source.json'))
    sequence['narration_sha256'] = digest(out / 'narration.txt')
    sequence['reviewed_manifest'] = (OUT / 'captures.reviewed.json').as_posix()
    sequence['reviewed_manifest_sha256'] = digest(out / 'captures.reviewed.json')
    sequence['sector_context'] = {'scene_id': '08', 'spoken_sentence': SECTOR_SENTENCE,
                                'scope': 'Same captured workflow applied to six sectors; no separate sector operations claimed.'}
    dump(out / 'screen-sequence.untimed.json', sequence)
    dump(out / 'revision-provenance.json', {
        'frozen_at': FROZEN_AT, 'version': 2,
        'change': 'One spoken final-paragraph sentence explicitly applies the same prepare/review pattern to all six sectors. Other narrated words and source images remain unchanged.',
        'prior_inputs': [{'file': str(p), 'sha256': v} for p, v in PINS.items()],
        'added_sentence': SECTOR_SENTENCE, 'source_images_changed': False,
        'replay_identity': 'Read the newly saved full call number and numeric ID from actual UI/URL; historical captured identity remains only in the historical narration and evidence.',
    })
    files = sorted(p for p in out.rglob('*') if p.is_file())
    dump(out / 'source-preflight.json', {
        'kind': 'frozen_unvoiced_source_preflight', 'frozen_at': FROZEN_AT,
        'files': [{'file': p.relative_to(SOURCES).as_posix(), 'sha256': digest(p)} for p in files],
        'scene_count': len(lesson['scenes']),
        'word_count': sum(len(s['narration'].split()) for s in lesson['scenes']),
        'untimed_span_count': len(sequence['sequence']), 'distinct_source_images': 20,
        'six_sector_examples': 6, 'all_six_sectors_spoken_in_final_paragraph': True,
        'source_scope': '25 original JPEG/DOM pairs already manually reviewed;20clean sources;5warning originals excluded. Hash checks preserve identity and do not reapprove pixels.',
        'parent_script_review': 'Prior572words reviewed by parent; v2 adds only the requested sentence and awaits its final readback.',
        'canonical_readiness_audio_timing_render_site_target_git_changed': False,
        'helper': {'file': 'production/' + Path(__file__).name, 'sha256': digest(Path(__file__))},
    })
    return check()


def check():
    lesson, prior, review, citations = build()
    out = SOURCES / OUT
    preflight = read(OUT / 'source-preflight.json')
    for pin in preflight['files']:
        require_pin(SOURCES / pin['file'], pin['sha256'])
    require_pin(Path(__file__), preflight['helper']['sha256'])
    held = read(OUT / (NAME + '.narrated-source.json'))
    assert held == lesson
    assert (out / 'narration.txt').read_text() == '\n\n'.join(s['narration'] for s in held['scenes']) + '\n'
    assert read(OUT / 'captures.reviewed.json') == review
    assert len(held['scenes']) == 8 and SECTOR_SENTENCE in held['scenes'][-1]['narration']
    sequence = read(OUT / 'screen-sequence.untimed.json')
    assert sequence['lesson_sha256'] == digest(out / (NAME + '.narrated-source.json'))
    assert sequence['narration_sha256'] == digest(out / 'narration.txt')
    assert sequence['reviewed_manifest_sha256'] == digest(out / 'captures.reviewed.json')
    assert all(s['timing_status'].startswith('Unassigned') for s in sequence['sequence'])
    return {'result': 'PASS', 'mode': 'offline source freeze/check only',
            'output': OUT.as_posix(), 'scenes': 8, 'words': preflight['word_count'],
            'spans': len(sequence['sequence']), 'images': 20,
            'narrated_source_sha256': digest(out / (NAME + '.narrated-source.json')),
            'narration_sha256': digest(out / 'narration.txt'),
            'source_preflight_sha256': digest(out / 'source-preflight.json')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--freeze', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--plan', action='store_true')
    parser.add_argument('--dispatch-source', type=Path)
    args = parser.parse_args()
    if args.freeze:
        result = freeze(args.dispatch_source)
    elif args.check:
        result = check()
    else:
        lesson, _, _, _ = build()
        result = {'mode': 'offline source plan only; no writes', 'output': OUT.as_posix(),
                  'scenes': len(lesson['scenes']),
                  'words': sum(len(s['narration'].split()) for s in lesson['scenes']),
                  'added_sentence': SECTOR_SENTENCE,
                  'replay_scenario': SCENARIO.as_posix(), 'replay_id': 'Read fresh from actual saved UI/URL; do not reuse historical IDs.'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
