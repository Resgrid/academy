"""Apply root's exact learner-copy edits to a NEW unvoiced Records candidate.

Default reads only. --write-candidate preserves all v1/raw bytes; no freeze,
audio, timing, renderer, canonical, site, target, browser or Git action occurs.
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
OLD = Path('expansion/plans/core-records-administration-source-candidate-20261030')
OUT = Path('expansion/plans/core-records-administration-source-candidate-20261030-v2')
PINS = {
    'candidate.json': 'c6b0a9e111fbf0a55d2ee740d03de6fe70acd6cda5c66085f2fc52e32a78e82d',
    'narration.candidate.txt': 'ddff488e3a163048a286f8bbbb480431a5982ff962c6cbfdd2fb0c161e149d94',
    'screen-sequence.untimed.json': '6de7f38bf67440f212153941dff897e8709d86b3116037ed6de687057ae759ef',
    'compact-correspondence.txt': 'd9122b19aa1ec7923a50ed628078f3ebfcf3ba69f4228690a8a37a4ff992b8e3',
    'captures.reviewed.json': 'd7f62579c97d07d59a98f7aa321f4cac46f6d92935ac7b7c5c3dc013c63604f0',
    'preflight.json': 'd24a1ba3031d3351bfa411e5bef5892776780e899bfb51d57a41536bde6c5fd5',
}
CHANGES = {
 ('policy', 'a008'): ('Under Numbering, Sequence width', 'Under Numbering, Number prefix gives record numbers a recognizable label. Sequence width'),
 ('fields', 'a007'): ('These settings express this version’s choices; they do not demonstrate a successful field-app submission.', 'Together, these choices control where the form is offered, whether it can be used offline, and whether authors can attach files.'),
 ('save-definition', 'a010'): ('The retained validation result says', 'The validation result says'),
 ('published', 'p003'): ('After the approved publication, the resumed version already shows Published and read-only. Open new draft is available for later changes; another Publish is not needed for this version.', 'A published version is read-only. Use Open new draft when the form needs a later change.'),
 ('draft', 'u004'): ('The returned record is Draft, with reference D, E, K, C, M, S and no final record number.', 'The returned record is Draft, with a draft reference and no final record number.'),
 ('attachment', 'u009'): ('The fresh list contains academy-record-exercise dot text, two hundred forty-two bytes.', 'The fresh list contains the software handout, with a size of two hundred forty-two bytes.'),
 ('finalize', 'u011'): ('The fresh result shows Finalized and the issued number T R N A D M, Twenty Twenty-Six, Zero Zero Zero One.', 'The fresh result shows Finalized. Its number uses our T R N A D M prefix, the year twenty twenty-six, and the four-digit sequence zero zero zero one.'),
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
        assert sha(S / OLD / name) == digest, 'Changed held v1: ' + name
    pre = json.loads((S / OLD / 'preflight.json').read_text())
    for name, digest in pre['outputs'].items():
        assert sha(S / OLD / name) == digest
    for path, digest in pre['input_files'].items():
        assert sha(S / path) == digest, 'Changed historical source/raw input.'
    assets = {p.relative_to(S / OLD).as_posix(): p.read_bytes() for p in (S / OLD).rglob('*') if p.is_file()}
    assets.pop('preflight.json')
    original = json.loads(assets['candidate.json'])
    lesson = deepcopy(original)
    sequence = json.loads(assets['screen-sequence.untimed.json'])
    changes = []
    for scene in sequence['scenes']:
        for screen in scene['screens']:
            key = (scene['scene_id'], screen['source_alias'])
            if key in CHANGES:
                before, after = CHANGES[key]
                assert screen['narration_span'].count(before) == 1
                screen['narration_span'] = screen['narration_span'].replace(before, after)
                changes.append({'scene_id': key[0], 'source_alias': key[1], 'before': before, 'after': after})
        scene['narration'] = ' '.join(screen['narration_span'] for screen in scene['screens'])
    assert len(changes) == len(CHANGES) == 7
    for scene, mapping, before in zip(lesson['scenes'], sequence['scenes'], original['scenes']):
        scene['narration'] = mapping['narration']
        for key in ['id', 'title', 'route', 'required_labels', 'practice', 'capture_evidence']:
            assert scene[key] == before[key], 'Unapproved scene/control/source change.'
    for index, path in enumerate(lesson['source_files']):
        lesson['source_files'][index] = (OUT / Path(path).relative_to(OLD)).as_posix()
    source = json.loads(assets['source-evidence.json'])
    for row in source['files']:
        row['file'] = (OUT / Path(row['file']).relative_to(OLD)).as_posix()
    delta = json.loads(assets['scenario.replay-delta.json'])
    delta['fixture']['file'] = (OUT / 'fixture/academy-record-exercise.txt').as_posix()
    audit = json.loads(assets['source-review.json'])
    audit.update(learner_copy_revision='v2, exact parent-requested learner edits; new full-script review pending',
        historical_v1_candidate={'file': (OLD / 'candidate.json').as_posix(), 'sha256': PINS['candidate.json']})
    assert lesson['parent_full_script_review_pending'] and not lesson['narration_frozen'] and not lesson['export_ready']
    narration = '\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n'
    assert 1000 <= len(narration.split()) <= 1300
    captures = json.loads(assets['captures.reviewed.json'])
    rows = {row['id']: row for row in captures['screenshots']}
    for scene in sequence['scenes']:
        for screen in scene['screens']:
            assert set(screen['required_labels']) <= set(rows[screen['capture_id']]['visible_labels'])
    compact = '\n\n'.join(scene['scene_id'] + ' | ' + screen['source_alias'] + ' | ' + screen['capture_id'] + '\n' + screen['narration_span'] + '\nVisible: ' + ' | '.join(screen['required_labels']) for scene in sequence['scenes'] for screen in scene['screens']) + '\n'
    assets.update({'candidate.json': encoded(lesson), 'narration.candidate.txt': narration.encode(),
        'screen-sequence.untimed.json': encoded(sequence), 'compact-correspondence.txt': compact.encode(),
        'source-evidence.json': encoded(source), 'source-review.json': encoded(audit), 'scenario.replay-delta.json': encoded(delta),
        'learner-copy-revision.json': encoded({'kind': 'parent_requested_learner_prose_v2_no_freeze',
            'prior_candidate_pins': PINS, 'changes': changes,
            'source_images_DOM_review_and_required_labels_unchanged': True,
            'six_sector_companions_unchanged': True, 'full_source_scope_limits_preserved_in_metadata': True,
            'parent_v2_full_script_review_pending': True, 'narration_frozen': False}),
        'historical-v1/narration.candidate.txt': (S / OLD / 'narration.candidate.txt').read_bytes(),
        'historical-v1/candidate.json': (S / OLD / 'candidate.json').read_bytes()})
    assert assets['captures.reviewed.json'] == (S / OLD / 'captures.reviewed.json').read_bytes()
    return lesson, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    lesson, assets = prepare()
    if args.write_candidate:
        destination = S / OUT
        assert not destination.exists(), 'New-only v2; preserve all v1/raw source bytes.'
        spec = importlib.util.spec_from_file_location('records_admin_v2_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        assert not findings, findings
        assets['preflight.json'] = encoded({'source_only': True, 'recipe_sha256': sha(__file__),
            'v1_pins': PINS, 'ordinary_privacy_findings': [], 'additional_known_private_values_checked': 0,
            'parent_full_script_review_pending': True, 'narration_frozen': False,
            'outputs': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_only': True, 'files_written': args.write_candidate,
        'scenes': len(lesson['scenes']), 'words': sum(len(scene['narration'].split()) for scene in lesson['scenes']),
        'candidate_sha256': hashlib.sha256(assets['candidate.json']).hexdigest(),
        'narration_sha256': hashlib.sha256(assets['narration.candidate.txt']).hexdigest(),
        'compact_sha256': hashlib.sha256(assets['compact-correspondence.txt']).hexdigest(),
        'output': str(S / OUT), 'parent_full_script_review_pending': True,
        'frozen_or_media_created': False}, indent=2))


if __name__ == '__main__':
    main()
