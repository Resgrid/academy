"""Propose exactly two IC public-label removals; no frozen inputs are edited.

Default reads only. --write-proposal creates NEW review-required files. The
actual training URL remains in unchanged pixels/DOM/provenance and historical
source; Server URL is an existing literal, never a replacement image label.
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
NAME = 'app-ic-access-session-settings'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
OUT = Path('expansion/plans') / (NAME + '-public-label-projection-proposed-20261030')
SOURCE_SHA = '3ca130845b258669b4ed54619fc31c89260e8319337bcc6ace3d514eb3622788'
MANIFEST_SHA = 'bf090b08e1dd54fcb3234869827fb9001a946a8631d7a6f9c532ba2496be63fe'
URL = 'http://127.0.0.1:18967'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    assert __debug__
    source = BASE / (NAME + '.narrated-source.json')
    manifest = BASE / 'captures.reviewed.json'
    assert sha(S / source) == SOURCE_SHA and sha(S / manifest) == MANIFEST_SHA
    original_lesson = json.loads((S / source).read_text())
    original_manifest = json.loads((S / manifest).read_text())
    lesson, captures = deepcopy(original_lesson), deepcopy(original_manifest)
    scene_index = next(i for i, scene in enumerate(lesson['scenes']) if scene['id'] == '02-review-server')
    image_index = next(i for i, row in enumerate(captures['screenshots']) if row['id'] == '003-readable-server-url-dialog')
    scene_labels = lesson['scenes'][scene_index]['required_labels']
    visible_labels = captures['screenshots'][image_index]['visible_labels']
    assert scene_labels.count(URL) == visible_labels.count(URL) == 1
    assert 'Server URL' in scene_labels and 'Server URL' in visible_labels
    operations = []
    for pointer, values in [(f'/scenes/{scene_index}/required_labels', scene_labels),
                            (f'/screenshots/{image_index}/visible_labels', visible_labels)]:
        before = list(values)
        values.remove(URL)
        operations.append({'json_pointer': pointer, 'before': before, 'after': list(values),
            'only_removed_literal': URL, 'existing_label_retained': 'Server URL'})
    # Reversing exactly these removals reconstructs the originals byte-for-byte
    # as JSON values; no identity/review/narration/URL substitution is hidden.
    reversed_lesson, reversed_captures = deepcopy(lesson), deepcopy(captures)
    reversed_lesson['scenes'][scene_index]['required_labels'] = operations[0]['before']
    reversed_captures['screenshots'][image_index]['visible_labels'] = operations[1]['before']
    assert reversed_lesson == original_lesson and reversed_captures == original_manifest
    assert [x['narration'] for x in lesson['scenes']] == [x['narration'] for x in original_lesson['scenes']]
    for before, after in zip(original_manifest['screenshots'], captures['screenshots']):
        for field in ['file', 'sha256', 'dom_file', 'dom_sha256', 'provenance', 'capture_review']:
            assert before[field] == after[field]
    sys.path.insert(0, str(ROOT / 'scripts'))
    from expansion_site import _public_lesson
    _public_lesson(lesson)
    provenance = {'kind': 'PROPOSED exact-two-array IC learner-label projection',
        'original_source': {'file': source.as_posix(), 'sha256': SOURCE_SHA},
        'original_manifest': {'file': manifest.as_posix(), 'sha256': MANIFEST_SHA},
        'prospective_source_sha256': hashlib.sha256(encoded(lesson)).hexdigest(),
        'prospective_manifest_sha256': hashlib.sha256(encoded(captures)).hexdigest(),
        'operations': operations, 'only_these_two_arrays_changed': True,
        'narration_required_words_unchanged': True, 'actual_pixels_DOM_provenance_reviews_unchanged': True,
        'existing_Server_URL_label_retained': True, 'privacy_gate_unchanged': True,
        'root_projection_review_required': True, 'projection_approved': False,
        'listening_identity_remains_original_source_sha256': SOURCE_SHA,
        'rationale': 'Learners identify the Server URL field; its visible local training value is retained in actual pixels and original source evidence, without treating a loopback address as a learner-facing required label. No hostname or pixels are substituted.',
        'limits': 'Root authorized preparation of this proposal only. No hearing receipt, parent approval, final plan, canonical or export readiness is created.'}
    assets = {'lesson.learner-projection.proposed.json': encoded(lesson),
        'captures.public-projection.proposed.json': encoded(captures), 'projection.provenance.json': encoded(provenance)}
    return provenance, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-proposal', action='store_true')
    args = parser.parse_args()
    provenance, assets = prepare()
    if args.write_proposal:
        destination = S / OUT
        assert not destination.exists(), 'New-only proposal; preserve all frozen files.'
        spec = importlib.util.spec_from_file_location('ic_projection_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        assert not findings, findings
        assets['preflight.json'] = encoded({'source_only': True, 'helper_sha256': sha(__file__),
            'ordinary_privacy_findings': [], 'root_projection_review_pending': True,
            'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            with (destination / name).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_only': True, 'written': args.write_proposal,
        'original_source_sha256': SOURCE_SHA, 'prospective_source_sha256': provenance['prospective_source_sha256'],
        'original_manifest_sha256': MANIFEST_SHA, 'prospective_manifest_sha256': provenance['prospective_manifest_sha256'],
        'projection_sha256': hashlib.sha256(assets['projection.provenance.json']).hexdigest(),
        'exact_array_changes': 2, 'root_review_required': True, 'output': str(S / OUT)}, indent=2))


if __name__ == '__main__':
    main()
