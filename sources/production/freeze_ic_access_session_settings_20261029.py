"""Seal the approved IC settings source, without creating audio or media approval.

Default/--check is read-only. Before creation it checks all 31 protected input
files and the 15 matching original/isolated IC source files. --freeze writes only
the NEW named package, refusing any existing destination. Subsequent --check is
self-contained: it needs the frozen images/DOM/source snapshots, not the original
raw prefix, external IC checkout, app, credentials, browser or private runtime.

Exact parent script acceptance is separate from user listening approval. Neither
speech times, generated audio, a rendered video nor public readiness is inferred.
"""

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
SOURCES = Path(__file__).resolve().parents[1]
BASE = Path('expansion/plans/app-ic-access-session-settings-candidate-20261029')
RAW = Path('captures/expansion/ic-access-orientation-recovery-20261029')
FREEZE = Path('expansion/plans/app-ic-access-session-settings-capture-freeze-20261029')
NAME = 'app-ic-access-session-settings'
INPUT_PINS = [
    {'file': (BASE / 'lesson.candidate.json').as_posix(), 'sha256': '3ca130845b258669b4ed54619fc31c89260e8319337bcc6ace3d514eb3622788'},
    {'file': (BASE / 'narration.candidate.txt').as_posix(), 'sha256': '9c10fd168574aa31a595aa1c7edf84db007f909235289fb20fbf42ce9ca9fc7b'},
    {'file': (BASE / 'screen-sequence.untimed.json').as_posix(), 'sha256': 'eca77e700cee002a841dd25a70caf86283774d2cd7d5622b32aa115cb7b424e2'},
    {'file': (BASE / 'source-review.json').as_posix(), 'sha256': '5c8a31b28010dcb70a477ee4378568423e3914b55befcb379c8316806a811151'},
    {'file': (BASE / 'source-preflight.json').as_posix(), 'sha256': 'ab3a998dbcaef8677f41a5edce3a9732ad40b87edf1060ead24f0a9fcd9ed6d7'},
    {'file': (RAW / 'review/reviewed-source-subset-20261029.json').as_posix(), 'sha256': 'dde1c8f91b96156973e796b683cdd6f2b48d7354ae0afee490dc60bf8d22ae50'},
    {'file': (RAW / 'manifest.json').as_posix(), 'sha256': 'ffb88e4c156ee277a38fc3f2fb6502ed5e08ee51ad70c91cad72c7df4b9063c0'},
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def load(path):
    return json.loads(path.read_text())


def safe_relative(value):
    p = Path(value)
    require(not p.is_absolute() and '..' not in p.parts and p.parts, 'Unsafe package-relative path.')
    return p


def read_file(root, name):
    path = root / safe_relative(name)
    require(path.is_file() and not path.is_symlink(), 'Missing or symlinked input: ' + name)
    require(path.resolve().is_relative_to(root.resolve()), 'Input escapes its root: ' + name)
    return path.read_bytes()


def tools_for(sources):
    scripts = sources.parent / 'scripts'
    def module(file, name):
        spec = importlib.util.spec_from_file_location(name, scripts / file)
        result = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(result)
        return result
    return module('audit_public_repo.py', 'ic_freeze_privacy'), module('verify_capture_evidence.py', 'ic_freeze_images')


def validate_correspondence(lesson, sequence, captures, narration):
    require(lesson['id'] == NAME and lesson['app'] == 'IC', 'Wrong lesson/application.')
    require(lesson.get('export_ready') is False and lesson.get('publication_approved') is False, 'Source cannot be media-ready.')
    require(len(lesson['scenes']) == 8 and len(lesson['sector_examples']) == 6, 'Expected eight scenes and six sectors.')
    require(narration == '\n\n'.join(x['narration'] for x in lesson['scenes']) + '\n', 'Exact narration changed.')
    require(len(re.findall(r"\b[\w]+(?:['’][\w]+)*\b", narration)) == 710, 'Expected approved 710-word narration.')
    require(len(captures['screenshots']) == 10 and len(sequence['spans']) == 17, 'Expected ten sources and seventeen untimed holds.')
    rows = {r['id']: r for r in captures['screenshots']}
    require(len(rows) == 10, 'Duplicate capture identity.')
    for row in rows.values():
        require(row['app'] == 'IC' and row['kind'] == 'application_screenshot', 'Illustrated/non-IC substitute rejected.')
        require(row.get('eligible_for_lesson') is True and row['capture_review']['passed'] is True, 'Unreviewed source rejected.')
        require(row['capture_review']['sha256'] == row['sha256'], 'Review/image hash mismatch.')
        require(row['visible_controls'] == [], 'No invented icon semantics are permitted in this package.')
    spans_by_scene = {}
    for span in sequence['spans']:
        require(not {'start', 'end', 'start_seconds', 'end_seconds', 'duration'}.intersection(span), 'Invented cue timing rejected.')
        row = rows.get(span['source_id'])
        require(row is not None, 'Hold references a missing source.')
        require(span['source_sha256'] == row['sha256'] and span['source_file'] == row['file'], 'Hold/image identity mismatch.')
        require(set(span['required_labels']) <= set(row['visible_labels']), 'Spoken control missing from held screen.')
        spans_by_scene.setdefault(span['scene_id'], []).append(span)
    require(set(spans_by_scene) == {s['id'] for s in lesson['scenes']}, 'Scene coverage gap or foreign scene.')
    for scene in lesson['scenes']:
        require(''.join(s['narration_exact'] for s in spans_by_scene[scene['id']]) == scene['narration'], 'Unshown, duplicated or reordered narration.')
        require(all(r in rows for r in scene['capture_refs']), 'Scene source is missing.')
        labels = {v for r in scene['capture_refs'] for v in rows[r]['visible_labels']}
        require(set(scene['required_labels']) <= labels, 'Scene control coverage gap.')


def protected_inputs(sources):
    for row in INPUT_PINS:
        require(digest(read_file(sources, row['file'])) == row['sha256'], 'Changed approved input: ' + row['file'])
    raw = load(sources / RAW / 'manifest.json')
    require(len(raw['captures']) == 12, 'Raw capture count changed.')
    names = {r['file'] for r in INPUT_PINS}
    for row in raw['captures']:
        require(row.get('eligible_for_lesson') is False, 'Raw source was altered/promoted.')
        for field, hash_field in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            require(digest(read_file(sources, row[field])) == row[hash_field], 'Raw image/DOM bytes changed: ' + row[field])
            names.add(row[field])
    actual = {str(p.relative_to(sources)) for root in [sources / BASE, sources / RAW] for p in root.rglob('*') if p.is_file()}
    require(actual == names and len(names) == 31, 'Protected candidate/raw inventory changed.')
    return [{'file': n, 'sha256': digest(read_file(sources, n))} for n in sorted(names)]


def localize(captures, sequence):
    caps, seq = copy.deepcopy(captures), copy.deepcopy(sequence)
    caps['origin_source_manifest'] = caps.pop('source_manifest')
    caps['source_dependencies'] = 'Frozen images and DOM only; origin fields are historical provenance, not required files.'
    for row in caps['screenshots']:
        for key, folder in [('file', 'images'), ('dom_file', 'dom')]:
            row['origin_' + key] = row[key]
            row[key] = (FREEZE / folder / Path(row[key]).name).as_posix()
    seq['lesson'] = (FREEZE / (NAME + '.narrated-source.json')).as_posix()
    seq['reviewed_source_subset'] = (FREEZE / 'captures.reviewed.json').as_posix()
    seq['reviewed_source_subset_sha256'] = digest(encoded(caps))
    for span in seq['spans']:
        span['source_file'] = (FREEZE / 'images' / Path(span['source_file']).name).as_posix()
    return caps, seq


GENERATION_BRIEF = '''Create narration only for “Review IC access, session settings and sync status”.

Use stock Warm Lulu, consistently for all eight approved paragraphs. Read
narration.frozen.txt exactly once in its existing order and preserve all words,
including the factual boundaries about unsaved settings and the empty queue.
Use a warm, natural instructional pace with clear pauses between paragraphs.
Do not rewrite, summarize, improvise a greeting, add a conclusion, pronounce
filenames, create screenshot descriptions, or add music or sound effects.

Keep eight paragraph assignments so generated-asset completeness can be checked.
Generation is not export or approval. Export the complete actual narration plus
fresh plain transcript, speech-timed SRT and dense genuine word-time transcript
when available. Full decode, exact-script correspondence, non-silent energy for
every actual cue and complete eight-paragraph asset readback must pass before
timed authoring. Seventeen untimed holds are source text partitions, not cues.
Never invent cue/word times or replace missing narration with a robotic fallback.

Parent approved this script and its source correspondence. This is not a claim
that the user has heard or approved a future audio file. No audio exists in this
source package; no publish/share/export approval or public-video readiness follows.
'''


def prepare(sources, ic_source, capture_copy):
    before = protected_inputs(sources)
    privacy, images = tools_for(sources)
    lesson = load(sources / BASE / 'lesson.candidate.json')
    sequence = load(sources / BASE / 'screen-sequence.untimed.json')
    captures = load(sources / RAW / 'review/reviewed-source-subset-20261029.json')
    narration = (sources / BASE / 'narration.candidate.txt').read_text()
    review = load(sources / BASE / 'source-review.json')
    validate_correspondence(lesson, sequence, captures, narration)
    outputs = {
        NAME + '.narrated-source.json': read_file(sources, (BASE / 'lesson.candidate.json').as_posix()),
        'narration.frozen.txt': narration.encode(),
        'generation-brief.txt': GENERATION_BRIEF.encode(),
    }
    for row in INPUT_PINS:
        # Exact original bytes are provenance; their historical references are not active dependencies.
        outputs['input-history/' + Path(row['file']).name] = read_file(sources, row['file'])
    for row in captures['screenshots']:
        require(images._image_dimensions(sources / row['file']) == (1434, 829), 'Image dimensions changed.')
        outputs['images/' + Path(row['file']).name] = read_file(sources, row['file'])
        outputs['dom/' + Path(row['dom_file']).name] = read_file(sources, row['dom_file'])
    source_rows = []
    require(len(review['source_files']) == 15, 'Source snapshot count changed.')
    for row in review['source_files']:
        a, b = read_file(ic_source, row['file']), read_file(capture_copy, row['file'])
        require(digest(a) == row['sha256'] and a == b, 'Cited IC source/capture-copy changed: ' + row['file'])
        name = 'source-snapshots/IC/' + row['file']
        outputs[name] = a
        source_rows.append({'file': name, 'source_repository': 'IC', 'source_file': row['file'], 'sha256': row['sha256']})
    caps, seq = localize(captures, sequence)
    validate_correspondence(lesson, seq, caps, narration)
    outputs['captures.reviewed.json'] = encoded(caps)
    outputs['screen-sequence.untimed.json'] = encoded(seq)
    outputs['accepted-parent-script-review.json'] = encoded({
        'kind': 'actual_parent_script_and_correspondence_acceptance',
        'reviewer': 'Root agent /root',
        'approval_recorded_at': '2026-10-29T23:58:57+00:00',
        'parent_full_script_review_approved': True,
        'parent_source_hold_review_approved': True,
        'freeze_authorized': True,
        'candidate': INPUT_PINS[0], 'narration': INPUT_PINS[1], 'ordered_source_holds': INPUT_PINS[2],
        'review_scope': 'Parent read all8 paragraphs and17 exact source holds, crosschecked against personally observed12 browser images, and authorized this new source-only freeze. No scope extension.',
        'human_audio_listening_approval': False, 'audio_created': False,
        'publication_approved': False, 'export_ready': False,
        'candidate_metadata_history': 'Approved candidate bytes retain their earlier pending-review status. This separate receipt records the actual later parent acceptance without rewriting history.'
    })
    for name, data in outputs.items():
        require(not privacy.scan_bytes(data), 'Public privacy pattern finding in output: ' + name)
    require(protected_inputs(sources) == before, 'Protected inputs changed during preparation.')
    outputs['source-freeze.json'] = encoded({
        'schema_version': 1, 'id': NAME, 'kind': 'frozen_source_only',
        'frozen_at': datetime.now(timezone.utc).isoformat(),
        'source_only': True, 'export_ready': False, 'publication_approved': False,
        'audio_created': False, 'timing_created': False, 'video_qualified': False,
        'parent_script_review_approved': True, 'human_audio_listening_approval': False,
        'scenes': 8, 'spoken_words': 710, 'whitespace_words': 704, 'untimed_holds': 17,
        'six_sector_companions': 6, 'copied_images': 10, 'copied_dom_records': 10,
        'source_snapshots': source_rows, 'protected_original_inputs': before,
        'recipe': {'file': 'production/' + Path(__file__).name, 'sha256': digest(Path(__file__).read_bytes())},
        'outputs': [{'file': name, 'sha256': digest(data)} for name, data in sorted(outputs.items())],
        'privacy': {'scanner': 'scripts/audit_public_repo.py unchanged patterns', 'finding_count': 0, 'known_private_values_read': False},
        'limitations': ['Observed browser/source correspondence is not authenticated binary or execution identity.', 'No server save, credential save, MFA/passkey enrollment, saved shared policy, actual Logout, offline write/replay, hardware wake/audio or external Support visit.', 'Speech timing, full audio QA, render/frame review and real browser playback remain required.'],
    })
    require(not privacy.scan_bytes(outputs['source-freeze.json']), 'Public freeze receipt privacy finding.')
    return outputs, before


def write_new_package(destination, outputs):
    require(not destination.exists(), 'Refusing existing freeze destination.')
    for name in outputs:
        safe_relative(name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(exist_ok=False)
    try:
        for name, data in outputs.items():
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
    except BaseException:
        shutil.rmtree(destination)
        raise


def verify_package(sources):
    dest = sources / FREEZE
    receipt = load(dest / 'source-freeze.json')
    require(receipt['source_only'] is True and receipt['export_ready'] is False and receipt['publication_approved'] is False, 'Source-only flags changed.')
    expected = {r['file'] for r in receipt['outputs']} | {'source-freeze.json'}
    actual = {str(p.relative_to(dest)) for p in dest.rglob('*') if p.is_file()}
    require(actual == expected, 'Frozen package inventory changed.')
    for row in receipt['outputs']:
        require(digest(read_file(dest, row['file'])) == row['sha256'], 'Frozen output hash mismatch: ' + row['file'])
    for row in INPUT_PINS:
        require(digest(read_file(dest, 'input-history/' + Path(row['file']).name)) == row['sha256'], 'Approved history changed.')
    candidate_bytes = read_file(dest, NAME + '.narrated-source.json')
    require(digest(candidate_bytes) == INPUT_PINS[0]['sha256'], 'Approved lesson changed.')
    narration = read_file(dest, 'narration.frozen.txt').decode()
    require(digest(narration.encode()) == INPUT_PINS[1]['sha256'], 'Approved narration changed.')
    lesson = json.loads(candidate_bytes)
    caps, seq = localize(load(dest / 'input-history/reviewed-source-subset-20261029.json'), load(dest / 'input-history/screen-sequence.untimed.json'))
    require(encoded(caps) == read_file(dest, 'captures.reviewed.json'), 'Localized capture observations changed.')
    require(encoded(seq) == read_file(dest, 'screen-sequence.untimed.json'), 'Exact ordered source holds changed.')
    validate_correspondence(lesson, seq, caps, narration)
    original_review = load(dest / 'input-history/source-review.json')
    require(len(receipt['source_snapshots']) == len(original_review['source_files']) == 15, 'Snapshot inventory changed.')
    expected_source = {r['file']: r['sha256'] for r in original_review['source_files']}
    for row in receipt['source_snapshots']:
        require(row['sha256'] == expected_source.get(row['source_file']), 'Original source identity changed.')
        require(digest(read_file(dest, row['file'])) == row['sha256'], 'Snapshot bytes changed.')
    privacy, images = tools_for(sources)
    for row in caps['screenshots']:
        for f, h in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            require(digest(read_file(sources, row[f])) == row[h], 'Frozen image/DOM mismatch.')
        require(images._image_dimensions(sources / row['file']) == (1434, 829), 'Frozen image geometry mismatch.')
    for name in actual:
        require(not privacy.scan_bytes(read_file(dest, name)), 'Frozen public privacy pattern finding: ' + name)
    return {'passed': True, 'source_only': True, 'files': len(actual), 'scenes': 8, 'spoken_words': 710, 'untimed_holds': 17, 'images': 10, 'source_snapshots': 15, 'external_source_or_raw_prefix_required': False, 'source_freeze_sha256': digest(read_file(dest, 'source-freeze.json')), 'export_ready': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=SOURCES)
    parser.add_argument('--ic-source', type=Path)
    parser.add_argument('--capture-copy', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    sources = args.sources.resolve()
    if not args.freeze and (sources / FREEZE).exists():
        result = verify_package(sources)
    else:
        ic_source = (args.ic_source or sources.parents[4] / 'IC').resolve()
        capture_copy = (args.capture_copy or sources.parents[1] / 'capture-apps/IC').resolve()
        outputs, before = prepare(sources, ic_source, capture_copy)
        if args.freeze:
            write_new_package(sources / FREEZE, outputs)
            require(protected_inputs(sources) == before, 'Protected inputs changed during freeze.')
            result = verify_package(sources)
        else:
            result = {'passed': True, 'source_only': True, 'files_to_create': len(outputs), 'protected_inputs_verified': len(before), 'export_ready': False}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit('IC source freeze stopped: ' + str(error)) from error
