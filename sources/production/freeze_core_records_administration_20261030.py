"""Freeze root-approved Records administration source; no audio/media action.

Default/--check reads only. --freeze creates a NEW portable package. The
--verify-frozen mode needs only its retained files, not application/private roots.
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
NAME = 'core-records-administration'
BASE = Path('expansion/plans/core-records-administration-source-candidate-20261030-v3')
FINAL = Path('expansion/plans/core-records-administration-capture-freeze-20261030')
PARENT = Path('expansion/plans/core-records-administration-root-script-review-20261030.json')
PARENT_SHA = 'c7662d0bccf77e363873e0988ea803de4aecf3fd83d6e9dc27a80f2ea0163594'
PINS = {
    'candidate.json': '896abab3b7b5679f9a5a908be0e0fe7ea6bf7f9a20febb4cba6eb2acb618021e',
    'narration.candidate.txt': '3e0ec3e23d30428a350fb9d499323d9ba499e4e2a93fa69a95fc1e9318b71c40',
    'screen-sequence.untimed.json': '60a957474883c8299af79ee7617843ef42de619ffc412d9281bc0c2f5de66e8d',
    'compact-correspondence.txt': '07ae3ff09bce042b8234d90d0bf3362ba2db21e1b231fabea7fc8da4b39d21fe',
    'captures.reviewed.json': 'd7f62579c97d07d59a98f7aa321f4cac46f6d92935ac7b7c5c3dc013c63604f0',
    'source-evidence.json': '9deb0608957d93e5ea81f1c79cc47e99a1a36572f7f227a43ab8c6130e8a1ead',
    'scenario.replay-delta.json': '6047cd558bedef152a8350fe00dfb20af82c57e4d83a07022fc2c5fb81891826',
    'actual-operation-log.json': '7246f151a3bbb8c0e125ef01945c84ffeb74a42b04b5bbcabce0d454a9bae5a3',
    'source-review.json': 'a7cbcad0c917e4f2522a56995ee76296262d13304e87ca083463b15b0737c801',
    'preflight.json': '91da0f2f78767cb19c662602375e43133dfc4a2549a4c001c9245962f3be3939',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def safe(value):
    path = Path(value)
    assert not path.is_absolute() and '..' not in path.parts, 'Nonportable retained asset path.'
    return path


def compare_scenes(before, after):
    assert len(before['scenes']) == len(after['scenes']) == 16
    for old, new in zip(before['scenes'], after['scenes']):
        assert old == new, 'Approved narrated scene or visible control claim changed.'
    for key in ['id', 'title', 'app', 'audience', 'summary', 'prerequisites', 'sector_examples', 'scope_limits']:
        assert before[key] == after[key]


def prepare():
    assert __debug__, 'Use ordinary Python; retained guards must remain enabled.'
    for name, digest in PINS.items():
        assert sha(S / BASE / name) == digest, 'Changed approved v3 input: ' + name
    pre = json.loads((S / BASE / 'preflight.json').read_text())
    for name, digest in pre['outputs'].items():
        assert sha(S / BASE / safe(name)) == digest
    assert sha(S / PARENT) == PARENT_SHA
    parent = json.loads((S / PARENT).read_text())
    assert parent['approved_for_source_freeze_and_natural_narration_generation'] is True
    assert parent['script_sha256'] == PINS['narration.candidate.txt'] and parent['candidate_sha256'] == PINS['candidate.json']
    assert parent['paragraphs'] == 16 and parent['words'] == 1134
    assert parent['human_audio_listening_claim'] is False and parent['private_export_or_publication_approval'] is False
    original = json.loads((S / BASE / 'candidate.json').read_text())
    lesson = deepcopy(original)
    manifest = deepcopy(json.loads((S / BASE / 'captures.reviewed.json').read_text()))
    sequence = deepcopy(json.loads((S / BASE / 'screen-sequence.untimed.json').read_text()))
    source = deepcopy(json.loads((S / BASE / 'source-evidence.json').read_text()))
    assets, path_map = {}, {}
    # Retain candidate/revision history once; source snapshots are copied once
    # at their portable source/ paths rather than duplicating all35 bodies.
    for path in (S / BASE).rglob('*'):
        if path.is_file():
            relative = path.relative_to(S / BASE)
            if relative.parts[0] != 'source':
                assets['original-review/' + relative.as_posix()] = path.read_bytes()
    sys.path.insert(0, str(ROOT / 'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions
    assert len(manifest['screenshots']) == 35
    for row in manifest['screenshots']:
        assert row['eligible_for_lesson'] is True and row['capture_review']['passed'] is True
        assert row['capture_review']['sha256'] == row['sha256']
        assert not row['visible_controls'] and _image_dimensions(S / row['file']) == (1280, 720)
        for field, hashfield, folder in [('file', 'sha256', 'images'), ('dom_file', 'dom_sha256', 'dom')]:
            before = row[field]
            path = S / safe(before)
            assert sha(path) == row[hashfield]
            target = (Path(folder) / path.name).as_posix()
            assert target not in assets, 'Duplicate frozen filename.'
            assets[target] = path.read_bytes()
            row[field] = (FINAL / target).as_posix()
            path_map[before] = {'file': row[field], 'sha256': row[hashfield]}
        if 'historical_review' in row['capture_review']:
            row['frozen_review_dependency'] = {'file': (FINAL / 'original-review/historical-source-plan/prior-captures.reviewed.json').as_posix(),
                'sha256': row['capture_review']['historical_review']['sha256'],
                'scope': 'Exact retained owner review; original capture_review attribution remains unchanged.'}
    for raw in manifest['raw_manifests']:
        original_path = S / safe(raw['file'])
        assert sha(original_path) == raw['sha256']
        target = 'original-raw/' + original_path.parent.name + '.manifest.json'
        assets[target] = original_path.read_bytes()
        raw['historical_original_file'] = raw['file']
        raw['file'] = (FINAL / target).as_posix()
    manifest['raw_manifest_scope'] = 'Historical receipts. All35 accepted image/DOM pairs are local copies; excluded9 originals remain in their unchanged original batches and are not lesson dependencies.'
    rows = {row['id']: row for row in manifest['screenshots']}
    for scene in sequence['scenes']:
        for screen in scene['screens']:
            assert screen['file'] in path_map
            screen['file'] = path_map[screen['file']]['file']
            assert screen['sha256'] == rows[screen['capture_id']]['sha256']
            assert set(screen['required_labels']) <= set(rows[screen['capture_id']]['visible_labels'])
    assert len(sequence['scenes']) == 16 and sum(len(scene['screens']) for scene in sequence['scenes']) == 39
    for authored, mapped in zip(lesson['scenes'], sequence['scenes']):
        assert ' '.join(screen['narration_span'] for screen in mapped['screens']) == authored['narration']
    assert len(source['files']) == 35
    for row in source['files']:
        before = row['file']
        relative = safe(before).relative_to(BASE)
        path = S / before
        assert sha(path) == row['sha256']
        assets[relative.as_posix()] = path.read_bytes()
        row['file'] = (FINAL / relative).as_posix()
        path_map[before] = {'file': row['file'], 'sha256': row['sha256']}
    lesson['source_files'] = [path_map[path]['file'] for path in lesson['source_files']]
    lesson.update(candidate_only=False, source_only=True, source_complete=True, narration_frozen=True,
        parent_full_script_review_pending=False, parent_whole_script_approved=True,
        source_script_review={'file': (FINAL / 'root-script-review.json').as_posix(), 'sha256': PARENT_SHA},
        export_ready=False, publication_approved=False)
    compare_scenes(original, lesson)
    narration = (S / BASE / 'narration.candidate.txt').read_bytes()
    assert ('\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n').encode() == narration
    assert len(narration.decode().split()) == 1134
    fixture = S / BASE / 'fixture/academy-record-exercise.txt'
    assert sha(fixture) == 'dcebe4204625aac14de7720b7e3fda03a3862ee15c3ecbcf2056b58e76c28296' and fixture.stat().st_size == 242
    assets['fixture/academy-record-exercise.txt'] = fixture.read_bytes()
    delta = json.loads((S / BASE / 'scenario.replay-delta.json').read_text())
    delta['fixture']['file'] = (FINAL / 'fixture/academy-record-exercise.txt').as_posix()
    assets.update({NAME + '.narrated-source.json': encoded(lesson), 'narration.txt': narration,
        NAME + '.captures.reviewed.json': encoded(manifest), NAME + '.screen-sequence.json': encoded(sequence),
        'compact-correspondence.txt': (S / BASE / 'compact-correspondence.txt').read_bytes(),
        'source-evidence.json': encoded(source), 'scenario.replay.json': encoded(delta),
        'actual-operation-log.json': (S / BASE / 'actual-operation-log.json').read_bytes(),
        'root-script-review.json': (S / PARENT).read_bytes(),
        'path-rebinding.json': encoded({'kind': 'byte_identical_source_only_portable_copies', 'map': path_map,
            'approved_narration_required_labels_and_scene_metadata_unchanged': True,
            'only_main_lesson_review_flags_changed': 'Root-bound source freeze only; exportreadyfalse, no audio/listening/media review.'})})
    spec = importlib.util.spec_from_file_location('records_admin_freeze_privacy', ROOT / 'scripts/audit_public_repo.py')
    scanner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scanner)
    findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
    assert not findings, findings
    assets['privacy-preflight.json'] = encoded({'source_only': True, 'files_checked': len(assets),
        'bytes_checked': sum(map(len, assets.values())), 'ordinary_privacy_findings': [],
        'additional_known_private_values_checked': 0, 'scope': 'Unchanged public rules; no private config/auth/export files read. Root known-value review remains separate.'})
    freeze = {'kind': 'immutable_parent_approved_Core_records_administration_source_only_freeze',
        'lesson_id': NAME, 'source_only': True, 'scenes': 16, 'words': 1134, 'accepted_images': 35,
        'dom_sidecars': 35, 'source_snapshots': 35, 'untimed_exact_spans': 39,
        'raw_original_pairs_preserved_separately': 44, 'six_sectors_spoken_and_companions': True,
        'narrated_source_sha256': hashlib.sha256(assets[NAME + '.narrated-source.json']).hexdigest(),
        'narration_sha256': PINS['narration.candidate.txt'], 'learner_content_digest': lesson_content_digest(lesson),
        'approved_v3_input_pins': PINS, 'root_review_sha256': PARENT_SHA,
        'helper': {'file': 'production/' + Path(__file__).name, 'sha256': sha(__file__)},
        'parent_full_script_approved': True, 'audio_timing_or_media_assigned': False,
        'human_audio_listening_reviewed': False, 'export_ready': False, 'publication_approved': False,
        'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()},
        'limits': ['Only accepted actual Core images are lesson evidence. Retained5 Responder source snapshots document unexercised/gated client limits; no active Responder manifest is bound.',
            'Approved publication was already complete on resume; no secondPublish/native confirmation pixels are invented.',
            'Exact image/DOM bytes and original review attribution remain unchanged. No subjective listening, generated audio timing, rendered frame or browser playback review exists.']}
    assets['source-freeze.json'] = encoded(freeze)
    return freeze, assets


def verify_frozen(destination):
    freeze = json.loads((destination / 'source-freeze.json').read_text())
    expected = set(freeze['files']) | {'source-freeze.json'}
    assert {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()} == expected
    for name, digest in freeze['files'].items():
        assert sha(destination / safe(name)) == digest, 'Changed frozen retained file: ' + name
    assert sha(destination / 'root-script-review.json') == PARENT_SHA
    assert sha(destination / 'original-review/candidate.json') == PINS['candidate.json']
    assert sha(destination / 'narration.txt') == PINS['narration.candidate.txt']
    original = json.loads((destination / 'original-review/candidate.json').read_text())
    lesson = json.loads((destination / (NAME + '.narrated-source.json')).read_text())
    compare_scenes(original, lesson)
    assert sha(destination / (NAME + '.narrated-source.json')) == freeze['narrated_source_sha256']
    assert ('\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n').encode() == (destination / 'narration.txt').read_bytes()
    assert lesson['narration_frozen'] is True and lesson['export_ready'] is False
    return freeze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--freeze', action='store_true')
    mode.add_argument('--verify-frozen', action='store_true')
    args = parser.parse_args()
    destination = S / FINAL
    if args.verify_frozen:
        freeze = verify_frozen(destination)
    else:
        freeze, assets = prepare()
        if args.freeze:
            assert not destination.exists(), 'New-only freeze; preserve all candidates/history.'
            destination.mkdir(parents=True)
            for name, body in assets.items():
                path = destination / safe(name)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(body)
        if destination.exists():
            verify_frozen(destination)
            assert all((destination / name).read_bytes() == body for name, body in assets.items())
    print(json.dumps({'source_preflight_passed': True, 'files_written': args.freeze,
        'scenes': 16, 'words': 1134, 'images_DOM_pairs': 35, 'source_snapshots': 35, 'untimed_spans': 39,
        'narrated_source': str(destination / (NAME + '.narrated-source.json')),
        'narrated_source_sha256': freeze['narrated_source_sha256'],
        'narration_txt': str(destination / 'narration.txt'), 'narration_sha256': freeze['narration_sha256'],
        'source_freeze_sha256': sha(destination / 'source-freeze.json') if destination.exists() else None,
        'audio_timing_media_canonical_ready_site_target_Git_actions': False}, indent=2))


if __name__ == '__main__':
    main()
