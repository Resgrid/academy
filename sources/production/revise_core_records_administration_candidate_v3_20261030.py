"""Apply the three final parent-requested speech edits; preserve v1/v2/raw.

Default reads only. --write-candidate creates NEW v3 source-only files. Root's
v3 full-script read is still pending; no freeze, voice, media or ready change.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
OLD = Path('expansion/plans/core-records-administration-source-candidate-20261030-v2')
OUT = Path('expansion/plans/core-records-administration-source-candidate-20261030-v3')
PINS = {'candidate.json': '332dde360e398de15ce1f9d45a868279b65f0608143ed64181bab9993274d323',
    'narration.candidate.txt': '5c6758e28715fc7b9fb39c59dca923404a8823bb512b444fe2894cbd33b6afde',
    'compact-correspondence.txt': '5b1e3fea159786958f61843eaf2d2298e82b89593c5077543f666bc8d1f2e80a',
    'captures.reviewed.json': 'd7f62579c97d07d59a98f7aa321f4cac46f6d92935ac7b7c5c3dc013c63604f0'}
CHANGES = {
 ('impact', 'a016'): ('Publish is the publication control; the table itself is neither publication confirmation nor a demonstration of using the form in that app.', 'Review this table before using Publish to make the version available to authors.'),
 ('prepare-record', 'u003'): ('Here the text describes software practice and makes no claim of a visit, care, attendance or operational action. ', ''),
 ('finalize', 'u010'): (' The statement applies to the entry’s actual contents; it does not turn a software exercise into physical work or attendance.', ''),
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    assert __debug__
    for name, digest in PINS.items():
        assert sha(S / OLD / name) == digest, 'Changed held v2.'
    pre = json.loads((S / OLD / 'preflight.json').read_text())
    for name, digest in pre['outputs'].items():
        assert sha(S / OLD / name) == digest
    assets = {p.relative_to(S / OLD).as_posix(): p.read_bytes() for p in (S / OLD).rglob('*') if p.is_file()}
    assets.pop('preflight.json')
    old = json.loads(assets['candidate.json'])
    lesson = deepcopy(old)
    sequence = json.loads(assets['screen-sequence.untimed.json'])
    changes = []
    for scene in sequence['scenes']:
        for screen in scene['screens']:
            key = (scene['scene_id'], screen['source_alias'])
            if key in CHANGES:
                before, after = CHANGES[key]
                assert screen['narration_span'].count(before) == 1
                screen['narration_span'] = screen['narration_span'].replace(before, after)
                assert screen['narration_span'].strip() == screen['narration_span']
                changes.append({'scene_id': key[0], 'source_alias': key[1], 'before': before, 'after': after})
        scene['narration'] = ' '.join(screen['narration_span'] for screen in scene['screens'])
    assert len(changes) == 3
    for scene, mapping, before in zip(lesson['scenes'], sequence['scenes'], old['scenes']):
        scene['narration'] = mapping['narration']
        for key in ['id', 'title', 'route', 'required_labels', 'practice', 'capture_evidence']:
            assert scene[key] == before[key]
    lesson['source_files'] = [(OUT / Path(path).relative_to(OLD)).as_posix() for path in lesson['source_files']]
    source = json.loads(assets['source-evidence.json'])
    for row in source['files']:
        row['file'] = (OUT / Path(row['file']).relative_to(OLD)).as_posix()
    delta = json.loads(assets['scenario.replay-delta.json'])
    delta['fixture']['file'] = (OUT / 'fixture/academy-record-exercise.txt').as_posix()
    audit = json.loads(assets['source-review.json'])
    audit.update(learner_copy_revision='v3, three final parent-requested speech edits; full-script review pending',
        historical_v2_candidate={'file': (OLD / 'candidate.json').as_posix(), 'sha256': PINS['candidate.json']})
    narration = '\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n'
    assert len(lesson['scenes']) == 16 and sum(len(scene['screens']) for scene in sequence['scenes']) == 39
    assert 1000 <= len(narration.split()) <= 1300
    assert not lesson['narration_frozen'] and not lesson['export_ready'] and lesson['parent_full_script_review_pending']
    assert lesson['scope_limits'] == old['scope_limits'] and lesson['sector_examples'] == old['sector_examples']
    compact = '\n\n'.join(scene['scene_id'] + ' | ' + screen['source_alias'] + ' | ' + screen['capture_id'] + '\n' + screen['narration_span'] + '\nVisible: ' + ' | '.join(screen['required_labels']) for scene in sequence['scenes'] for screen in scene['screens']) + '\n'
    assets.update({'candidate.json': encoded(lesson), 'narration.candidate.txt': narration.encode(),
        'screen-sequence.untimed.json': encoded(sequence), 'compact-correspondence.txt': compact.encode(),
        'source-evidence.json': encoded(source), 'source-review.json': encoded(audit), 'scenario.replay-delta.json': encoded(delta),
        'learner-copy-revision.json': encoded({'kind': 'three_final_parent_requested_learner_edits_v3',
            'prior_candidate_pins': PINS, 'changes': changes, 'metadata_claim_boundaries_unchanged': True,
            'source_image_DOM_reviews_controls_and_six_sectors_unchanged': True,
            'parent_v3_full_script_review_pending': True, 'narration_frozen': False}),
        'historical-v2/narration.candidate.txt': (S / OLD / 'narration.candidate.txt').read_bytes(),
        'historical-v2/candidate.json': (S / OLD / 'candidate.json').read_bytes(),
        'historical-v2/learner-copy-revision.json': (S / OLD / 'learner-copy-revision.json').read_bytes()})
    assert assets['captures.reviewed.json'] == (S / OLD / 'captures.reviewed.json').read_bytes()
    return lesson, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    lesson, assets = prepare()
    if args.write_candidate:
        destination = S / OUT
        assert not destination.exists(), 'New-only v3; preserve v1/v2/raw.'
        spec = importlib.util.spec_from_file_location('records_admin_v3_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        assert not findings, findings
        assets['preflight.json'] = encoded({'source_only': True, 'recipe_sha256': sha(__file__),
            'v2_pins': PINS, 'ordinary_privacy_findings': [], 'additional_known_private_values_checked': 0,
            'parent_full_script_review_pending': True, 'narration_frozen': False,
            'outputs': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_only': True, 'files_written': args.write_candidate,
        'paragraphs': 16, 'words': sum(len(scene['narration'].split()) for scene in lesson['scenes']),
        'untimed_spans': 39, 'candidate_sha256': hashlib.sha256(assets['candidate.json']).hexdigest(),
        'narration_sha256': hashlib.sha256(assets['narration.candidate.txt']).hexdigest(),
        'compact_sha256': hashlib.sha256(assets['compact-correspondence.txt']).hexdigest(),
        'output': str(S / OUT), 'full_root_review_pending': True, 'narration_frozen': False}, indent=2))


if __name__ == '__main__':
    main()
