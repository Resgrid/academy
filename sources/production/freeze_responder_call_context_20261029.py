"""Freeze the approved, read-only Responder incident-context lesson.

Default/--check is read-only. --freeze creates only a NEW self-contained source
package. --verify-frozen validates it without Responder, Node, a browser or private
configuration. No audio, timing, media, canonical lesson or publication is made.
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
SOURCES = ROOT / 'sources'
NAME = 'app-responder-call-context-review'
BASE = Path('expansion/plans') / (NAME + '-candidate-20261029')
FINAL = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
RAW = Path('captures/expansion/responder-calls-readonly-20261029-235')
BINDING_AT = '2026-10-30T00:23:31Z'
PINS = {
    'candidate.json': '882a6bba425dfb8e32807f4a820ebebae0cf4ee1eb36db6d454f5761353e6c54',
    'narration.txt': '7d6bd8a04fe7751de719e9fc8bff9718fd4a7a63931cf0bce1cd640a65510d30',
    'captures.reviewed.json': 'e89a65d75817abd06be2e2ea270726b82cb07bbc09826e34b407ba49cd3edc3c',
    'screen-sequence.untimed.json': '39ad10a0f8c913d788340baad45b9641fb858f29d55f7d878b26b04ae79bac75',
    'source-pixel-review.json': '5f9d0e08ec23fbf8a9e875e760150ac33312dba9e9cc95c542c49d3077ca8639',
    'preflight.json': 'b9ec8dbe55e9c9c433c98fc1656d1c40ef9bbd5870e86677537628f59505ff70',
}
RAW_PINS = {
    'manifest.json': '17b604e83ce35810371900343d980b147f3326c8463e7b827669d2b5d17f128e',
    'action-ledger.json': 'bdbc38b6ef54b6316ec8aa45d3852dce5b0eb6d7437496c199e6831f1c2b57bb',
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def read_json(path):
    return json.loads(Path(path).read_text())


def safe_relative(value):
    path = Path(value)
    assert not path.is_absolute() and '..' not in path.parts, 'Nonportable asset path.'
    return path


def exact_parts(text, anchors):
    """Split only at literal, unique paragraph text; never assign speech times."""
    offsets = [0]
    for anchor in anchors:
        assert text.count(anchor) == 1, 'Missing or ambiguous exact prose anchor.'
        offset = text.index(anchor)
        assert offset > offsets[-1], 'Prose anchors are out of order.'
        offsets.append(offset)
    offsets.append(len(text))
    parts = [text[start:end].strip() for start, end in zip(offsets, offsets[1:])]
    assert all(parts) and ' '.join(parts) == text, 'Spoken words changed.'
    return parts


def make_sequence(lesson, captures):
    by_number = {int(row['id'][:3]): row for row in captures['screenshots']}
    # These are prose boundaries, not estimated operation or word timings.
    rules = [
        ([6, 7], ['The list narrows'], [['Calls', 'Search calls...'], ['Warehouse', '#DEMO-0001']]),
        ([10], [], [lesson['scenes'][1]['required_labels']]),
        ([9], [], [lesson['scenes'][2]['required_labels']]),
        ([13], [], [lesson['scenes'][3]['required_labels']]),
        ([13, 11, 14], ['In Protocols,', 'Activity returns'],
         [['Protocols', 'Activity'], ['Protocols', 'No protocols attached to this call'], ['Activity', 'No timeline events available']]),
        ([14, 15], ['to inspect Call Notes.'],
         [['Notes'], ['Call Notes', 'No notes found', 'Add a new note...', 'Add Note', 'Cancel']]),
        ([14, 16, 17], ['Call Images currently', 'Call Files says'],
         [['Images', 'Files'], ['Call Images', 'No images available'], ['Call Files', 'No files available']]),
        ([19], [], [lesson['scenes'][7]['required_labels']]),
    ]
    scenes, flat = [], []
    for scene, (numbers, anchors, requirements) in zip(lesson['scenes'], rules):
        screens = []
        parts = exact_parts(scene['narration'], anchors)
        assert len(parts) == len(numbers) == len(requirements)
        for number, part, labels in zip(numbers, parts, requirements):
            row = by_number[number]
            assert set(labels) <= set(row['visible_labels']), 'Unseen required literal.'
            screen = {'span_id': f'{scene["id"]}-{len(screens) + 1:02d}',
                      'capture_id': row['id'], 'source_file': row['file'],
                      'source_sha256': row['sha256'], 'dom_file': row['dom_file'],
                      'dom_sha256': row['dom_sha256'], 'narration_exact': part,
                      'required_pixel_labels': labels, 'timing_seconds': None}
            screens.append(screen)
            flat.append({'scene_id': scene['id'], **screen})
        assert ' '.join(screen['narration_exact'] for screen in screens) == scene['narration']
        assert set(scene['required_labels']) <= {label for screen in screens for label in screen['required_pixel_labels']}
        scenes.append({'scene_id': scene['id'], 'title': scene['title'],
                       'narration': scene['narration'], 'screens': screens,
                       'accepted_context_refs': scene['capture_evidence']['capture_refs']})
    assert len(flat) == 14
    assert {screen['capture_id'] for screen in flat} == {row['id'] for row in captures['screenshots']}
    return {'lesson_id': NAME, 'timing_assigned': False, 'scenes': scenes,
            'untimed_spans': flat, 'span_count': len(flat),
            'limits': ['Exact prose segments and ordered actual screens only; no speech time is inferred.',
                       'Short control phrases can continue an already-held prior screen. Actual generated speech cues or genuine transcript anchors, readable holds and complete frame review are required before any timed edit.',
                       'Redundant historical context refs need not force additional editorial cuts. No required visual label or spoken word is removed.']}


def normalize(candidate, source_rows):
    lesson = deepcopy(candidate)
    assert isinstance(lesson['audience'], list) and len(lesson['audience']) == 1
    lesson['audience'] = lesson['audience'][0]
    lesson['source_files'] = [(FINAL / row['snapshot']).as_posix() for row in source_rows]
    lesson['source_file_hashes'] = [{'file': (FINAL / row['snapshot']).as_posix(),
                                   'sha256': row['sha256'], 'repository': 'Responder',
                                   'repository_path': row['path']} for row in source_rows]
    for scene in lesson['scenes']:
        refs = scene.pop('capture_refs')
        scene['capture_evidence'] = {'status': 'reviewed_actual_source_screens_only',
                                    'capture_refs': refs,
                                    'observations': ['Actual foreground literal labels are reviewed; no response, record write or provider result is claimed.']}
    lesson.update(candidate_only=False, source_only=True, source_complete=True,
                  narration_frozen=True, parent_full_script_review_pending=False,
                  parent_whole_script_approved=True, export_ready=False,
                  publication_approved=False)
    assert isinstance(lesson['audience'], str) and all(isinstance(x, str) for x in lesson['source_files'])
    for before, after in zip(candidate['scenes'], lesson['scenes']):
        for key in ['id', 'title', 'route', 'capture_intent', 'required_labels', 'narration', 'practice']:
            assert before[key] == after[key], 'Approved learner wording changed.'
        assert before['capture_refs'] == after['capture_evidence']['capture_refs']
    assert lesson['sector_examples'] == candidate['sector_examples']
    return lesson


def prepare(sources=SOURCES):
    base = sources / BASE
    assets = {}
    for name, digest in PINS.items():
        assert sha(base / name) == digest, 'Changed approved candidate: ' + name
        assets['original-candidate/' + name] = (base / name).read_bytes()
    for name, digest in RAW_PINS.items():
        assert sha(sources / RAW / name) == digest, 'Changed raw provenance: ' + name
        assets['original-raw/' + name] = (sources / RAW / name).read_bytes()
    candidate = read_json(base / 'candidate.json')
    captures = deepcopy(read_json(base / 'captures.reviewed.json'))
    source_review = read_json(base / 'source-pixel-review.json')
    preflight = read_json(base / 'preflight.json')
    for name, digest in preflight['files'].items():
        assert sha(base / safe_relative(name)) == digest, 'Changed retained candidate asset.'
    source_rows = source_review['source_identity']['managed_source_snapshots']
    assert len(source_rows) == 15 and len(captures['screenshots']) == 11
    for row in source_rows:
        original = base / safe_relative(row['snapshot'])
        assert sha(original) == row['sha256'], 'Changed source snapshot.'
        assets[row['snapshot']] = original.read_bytes()
    sys.path.insert(0, str(ROOT / 'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions
    raw = read_json(sources / RAW / 'manifest.json')
    assert len(raw['captures']) == 19 and all(row['eligible_for_lesson'] is False for row in raw['captures'])
    # The original excluded pairs are checked, but are not made lesson evidence.
    for row in raw['captures']:
        for field, hashfield in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            assert sha(sources / safe_relative(row[field])) == row[hashfield], 'Changed raw capture.'
    path_map = {}
    for row in captures['screenshots']:
        assert row['eligible_for_lesson'] is True and row['capture_review']['passed'] is True
        assert row['capture_review']['sha256'] == row['sha256'] and not row['visible_controls']
        assert _image_dimensions(sources / safe_relative(row['file'])) == (1434, 773)
        for field, hashfield, sub in [('file', 'sha256', 'images'), ('dom_file', 'dom_sha256', 'dom')]:
            before = row[field]
            original = sources / safe_relative(before)
            assert sha(original) == row[hashfield]
            destination = (Path(sub) / original.name).as_posix()
            assets[destination] = original.read_bytes()
            row[field] = (FINAL / destination).as_posix()
            path_map[before] = {'file': row[field], 'sha256': row[hashfield]}
    captures['raw_manifest'] = {'file': (FINAL / 'original-raw/manifest.json').as_posix(), 'sha256': RAW_PINS['manifest.json']}
    captures['raw_manifest_scope'] = 'Historical provenance only. All11 accepted image/DOM pairs are copied here. Excluded8 originals remain unchanged in the separate raw batch and are not dependencies of this lesson.'
    lesson = normalize(candidate, source_rows)
    assert len(lesson['scenes']) == 8 and len(lesson['sector_examples']) == 6
    narration = (base / 'narration.txt').read_bytes()
    assert ('\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n').encode() == narration
    assert len(narration.decode().split()) == 661
    sequence = make_sequence(lesson, captures)
    normalization = {'kind': 'typed_learner_projection_without_spoken_word_changes',
        'original_candidate_sha256': PINS['candidate.json'], 'narration_sha256': PINS['narration.txt'],
        'field_map': [
            {'from': 'audience[0]', 'to': 'audience', 'change': 'Single-item audience list becomes the same exact string.'},
            {'from': 'source_files[{repository,path,sha256}]', 'to': 'source_files[str] + source_file_hashes[{file,sha256,repository,repository_path}]', 'change': 'Use portable string paths to retained snapshots; preserve original hashes and repository paths separately.'},
            {'from': 'scenes[*].capture_refs', 'to': 'scenes[*].capture_evidence.capture_refs', 'change': 'Same ordered source IDs; source-only observation status added.'},
            {'from': 'candidate review flags', 'to': 'source-only frozen flags', 'change': 'Parent approved the exact661-word script and bounded correspondence. No audio, frame, playback or publication review is inferred.'},
            {'from': 'candidate asset paths', 'to': 'self-contained frozen image/DOM/source paths', 'change': 'Byte-identical copies only; image identity, dates, URLs, labels and existing review attribution remain unchanged.'}],
        'unchanged_fields': ['All8 narration paragraphs', 'Every scene required_labels entry', 'Scene titles, routes, practice and capture intent', 'All6 sector companions', 'Every source ID, original image/DOM hash and pixel-review receipt'],
        'context_order_note': 'Accepted context refs remain unchanged. Exact prose spans use their relevant actual screenshots; redundant prior context frames do not force a cut.',
        'public_package_path_map': path_map}
    acceptance = {'kind': 'parent_approved_bounded_Responder_incident_context_source',
        'reviewer': 'Codex /root', 'binding_recorded_at': BINDING_AT,
        'authority': 'Direct parent instruction after reading the entire661-word narration and all8 scene controls/capture refs.',
        'narration_sha256': PINS['narration.txt'], 'candidate_sha256': PINS['candidate.json'],
        'parent_whole_script_approved': True, 'bounded_correspondence_approved': True,
        'parent_personally_viewed_sources': ['009-call-info-priority-type-address', '013-dispatched-resource-rows-complete', '019-home-response-visibility-readback'],
        'other_accepted_source_review': 'Existing Codex /root/dispatch_ic_coverage actual display reviews, retained unchanged; no new or original-size/100-percent inspection is asserted.',
        'limits': 'Incident context review only. Does not complete actual response, writes, Records, readiness or native/provider coverage. This is not audio/video/publication approval.'}
    source_evidence = {'repository': 'Responder', 'git_revision': source_review['source_identity']['git_revision'],
        'files': [{'repository_path': row['path'], 'file': (FINAL / row['snapshot']).as_posix(), 'sha256': row['sha256']} for row in source_rows],
        'correspondence_scope': source_review['source_identity']['scope'],
        'read_endpoints': source_review['source_read_endpoints'], 'endpoint_limit': source_review['endpoint_limit']}
    compact = '\n\n'.join(f'{span["span_id"]} | {span["capture_id"]}\n{span["narration_exact"]}\nVisible: ' + ' | '.join(span['required_pixel_labels']) for span in sequence['untimed_spans']) + '\n'
    assets.update({NAME + '.narrated-source.json': encoded(lesson), 'narration.frozen.txt': narration,
        'captures.reviewed.json': encoded(captures), 'screen-sequence.untimed.json': encoded(sequence),
        'screen-sequence.compact.txt': compact.encode(), 'field-normalization-map.json': encoded(normalization),
        'parent-source-acceptance.json': encoded(acceptance), 'source-evidence.json': encoded(source_evidence)})
    spec = importlib.util.spec_from_file_location('unchanged_responder_privacy', ROOT / 'scripts/audit_public_repo.py')
    privacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(privacy)
    findings = [{'file': name, 'rule': rule} for name, body in assets.items() for rule in privacy.scan_bytes(body)]
    assert not findings, 'Privacy findings: ' + repr(findings)
    report = {'kind': 'independent_rule_based_source_freeze_privacy_preflight',
        'files_checked': len(assets), 'bytes_checked': sum(map(len, assets.values())),
        'findings': findings, 'additional_known_private_values_checked': 0,
        'scope': 'Unchanged public audit rules across actual image/DOM/source/metadata copies. No credential/auth/session reads; root known-value audit remains separate.',
        'pixel_review': 'Existing actual display reviews retained with exact hashes. This scan is not a substitute for image review.',
        'audio_or_timing_assigned': False, 'publication_approved': False}
    assets['privacy-preflight.json'] = encoded(report)
    recipe = {'kind': 'self_contained_approved_Responder_incident_context_source_freeze',
        'lesson_id': NAME, 'source_only': True, 'scenes': 8, 'narration_words_whitespace': 661,
        'accepted_images': 11, 'dom_sidecars': 11, 'raw_pairs_preserved_separately': 19,
        'source_snapshots': 15, 'untimed_exact_text_spans': 14, 'six_sectors_spoken_and_companions': True,
        'narrated_source_sha256': hashlib.sha256(assets[NAME + '.narrated-source.json']).hexdigest(),
        'narration_sha256': PINS['narration.txt'], 'learner_content_digest': lesson_content_digest(lesson),
        'original_candidate_pins': PINS, 'original_raw_pins': RAW_PINS,
        'helper': {'file': 'production/' + Path(__file__).name, 'sha256': sha(__file__)},
        'parent_whole_script_approved': True, 'audio_or_timing_assigned': False,
        'publication_approved': False, 'export_ready': False,
        'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()},
        'limits': ['Self-contained accepted image/DOM/source copies do not require a running app, npm, SDK or private configuration for replay verification.',
                   'Historical raw/candidate receipts are preserved. Excluded raw images remain in their original separate batch; none becomes an accepted capture.',
                   'No original scene wording or required labels changed. Human audio listening, source-to-speech timing, rendered-frame and beginning/middle/end playback reviews do not yet exist.']}
    assets['source-freeze.json'] = encoded(recipe)
    return recipe, assets


def verify_frozen(destination):
    recipe = read_json(destination / 'source-freeze.json')
    files = recipe['files']
    expected = set(files) | {'source-freeze.json'}
    assert {path.relative_to(destination).as_posix() for path in destination.rglob('*') if path.is_file()} == expected, 'Frozen file inventory changed.'
    for name, digest in files.items():
        assert sha(destination / safe_relative(name)) == digest, 'Frozen asset changed: ' + name
    for name, digest in PINS.items():
        assert sha(destination / 'original-candidate' / name) == digest
    assert sha(destination / 'narration.frozen.txt') == PINS['narration.txt']
    lesson = read_json(destination / (NAME + '.narrated-source.json'))
    candidate = read_json(destination / 'original-candidate/candidate.json')
    source_rows = read_json(destination / 'original-candidate/source-pixel-review.json')['source_identity']['managed_source_snapshots']
    assert lesson == normalize(candidate, source_rows), 'Typed learner projection changed.'
    assert recipe['narrated_source_sha256'] == sha(destination / (NAME + '.narrated-source.json'))
    captures = read_json(destination / 'captures.reviewed.json')
    assert read_json(destination / 'screen-sequence.untimed.json') == make_sequence(lesson, captures)
    for row in captures['screenshots']:
        for field, hashfield in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            relative = safe_relative(row[field]).relative_to(FINAL)
            assert sha(destination / relative) == row[hashfield], 'Missing/changed accepted source.'
    assert lesson['export_ready'] is False and recipe['audio_or_timing_assigned'] is False
    return recipe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only input and existing output checks (default).')
    mode.add_argument('--freeze', action='store_true', help='Create only a new named source package.')
    mode.add_argument('--verify-frozen', action='store_true', help='Check retained package only; no original apps/private roots.')
    args = parser.parse_args()
    destination = SOURCES / FINAL
    if args.verify_frozen:
        recipe = verify_frozen(destination)
    else:
        recipe, assets = prepare()
        if args.freeze:
            assert not destination.exists(), 'New-only freeze; preserve existing packages.'
            destination.mkdir(parents=True)
            for name, body in assets.items():
                path = destination / safe_relative(name)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(body)
        if destination.exists():
            verify_frozen(destination)
            for name, body in assets.items():
                assert (destination / name).read_bytes() == body, 'Freeze no longer matches guarded inputs.'
    print(json.dumps({'passed': True, 'files_written': args.freeze, 'self_contained': True,
        'output': str(destination), 'scenes': 8, 'words': 661, 'images': 11, 'dom_sidecars': 11,
        'source_snapshots': 15, 'exact_untimed_spans': 14,
        'narrated_source_sha256': recipe['narrated_source_sha256'], 'narration_sha256': recipe['narration_sha256'],
        'source_freeze_sha256': sha(destination / 'source-freeze.json') if destination.exists() else None,
        'audio_or_timing_assigned': False, 'ready_or_canonical_changed': False}, indent=2))


if __name__ == '__main__':
    main()
