"""Guarded complete Core record-definition take01 author; default read-only.

The immutable1134 words map to135 genuine captions,39 source holds and35
actual Core images. --assemble requires exact genuine User hearing and Root
whole-map receipt hashes. No rendering, browser, app, publication, canonical,
site, target or Git action occurs here. Existing freeze/proposal/audio stay intact.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-records-administration'
FREEZE = Path('expansion/plans/core-records-administration-capture-freeze-20261030')
FROZEN = FREEZE / (NAME + '.narrated-source.json')
MANIFEST = FREEZE / (NAME + '.captures.reviewed.json')
MAP = Path('expansion/plans/core-records-administration-actual135-source-map-20261030/correspondence.actual.json')
PARENT = MAP.parent / 'root-complete-map-review.json'
PARENT_SHA = '667259f933efd42ff7cc106f4529708c66c1d5ca6ae214567885ceb512dc21aa'
SOURCE_SHA = '3d459af0acfd125a0b2b58fe4cc3a6478c874fc1315cb74dce65ec93130d0754'
AUDIO_SHA = '8daaaa5a75b40a075b966ca71bf9cfb4ef82eba0a6ff4a7a0d91f387cf14a86c'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
ORIGINAL_QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
DERIVED_QA = Path('expansion/audio') / (NAME + '.derived135.actual.qa.json')
CAPTIONS = Path('expansion/audio') / (NAME + '.derived135.corrected.srt')
ORIGINAL_RAW = Path('expansion/audio') / (NAME + '-generated-20261030.srt')
ORIGINAL_CHECKED = Path('expansion/audio') / (NAME + '.actual.corrected.srt')
DERIVED_RAW = Path('expansion/plans/core-records-administration-take-01-proposed-20261030/captions.derived135.proposed.srt')
LISTENING = Path('expansion/audio') / (NAME + '.listening-review.json')
FINAL = Path('expansion/plans/core-records-administration-take-01-final-inputs-20261030')
GUARDS = Path('production/author_core_billing_shifts_take_02_20261030_v2.py')
PINS = {
    FROZEN: SOURCE_SHA,
    FREEZE / 'source-freeze.json': 'aa56b6aabe37da1963af479bc09c38d1d595d510d32c0adeccf33e6c7cf89e8d',
    MANIFEST: '60fabcba27114439f26b633262af7782213c8fc1795068d2b9867deab386a32a',
    MAP: 'c08eebd5ddfe906e3c69ba064140314394cf3a308550ce0af6ef7b875358c48a',
    PARENT: PARENT_SHA,
    AUDIO: AUDIO_SHA,
    ORIGINAL_QA: '6976e836dc3641ce146d6069c5a75c9b55cd6ca15f14addaa8119fb04e39973e',
    DERIVED_QA: '9afe02c0a15459f9348d84d237716f15b75878e5878dface28408f6b2399cafb',
    ORIGINAL_RAW: '068fc7f45773ac7779b79d3927d4bdb6929d17b2eea0fc8fecde07811f806560',
    ORIGINAL_CHECKED: '0e0bef7b2c10bd3ed1870cbca121dde48e5be6e738b1f041b1a50a85bfe905c0',
    DERIVED_RAW: 'f19c19162ca3a413f576462134506645327d86e0b0925aba1f55248b36c87096',
    CAPTIONS: 'ba9f6be215c97cd426d5a0549c2014d626fbc633d3c6aa3787ec779d5bebd145',
    GUARDS: 'c6b733cc25a7c30596875cbd3c1a323786a90b87b0cd159629e6754f64e8ee6a',
}
CODE_PINS = {
    'scripts/render_walkthrough.py': '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881',
    'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
}
# Exact unchanged speech phrases, bound only when their complete source label
# is already present in that actual screenshot. No control is added by aliasing.
ALIASES = {
    'save-definition': {'Review impact & publish': ['Review impact and publish']},
    'impact': {'Publish impact': ['Publish impact']},
    'draft': {'Station / group': ['Station and group']},
    'attachment': {'242 bytes': ['two hundred forty-two bytes']},
    'revision': {'Item 1 / Byte Size': ['byte size'], 'Item 1 / Checksum': ['checksum'],
                 'Item 1 / Classification': ['classification']},
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def norm(text):
    return ' '.join(text.split()).casefold()


def contained(relative, must_exist=True):
    require(isinstance(relative, (str, Path)), 'Expected source-relative path.')
    value = str(relative)
    require(value and '\\' not in value and not re.search(r'(?i)(?:://|www\.)', value), 'Unsafe source path.')
    require(not value.startswith('/') and all(p not in ('', '.', '..', 'private', '.git', 'node_modules')
            and not p.startswith('.env') for p in value.split('/')), 'Unsafe source path.')
    path = S / value
    require(path.resolve().is_relative_to(S.resolve()), 'Source path escapes the package.')
    require(not any(p.is_symlink() for p in [path, *path.parents] if p == S or p.is_relative_to(S)), 'Symlink source is rejected.')
    require(not must_exist or path.is_file(), 'Missing retained source asset: ' + value)
    return path


def date(value):
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc), 'Review needs actual nonfuture timezone-aware date.')
    return stamp


def retained_guards():
    require(__debug__, 'Use ordinary Python; retained guards require assertions enabled.')
    for relative, digest in PINS.items():
        require(sha(contained(relative)) == digest, 'Changed pinned actual input: ' + str(relative))
    for relative, digest in CODE_PINS.items():
        require(sha(ROOT / relative) == digest, 'Changed renderer/evidence gate; obtain a new source review.')
    spec = importlib.util.spec_from_file_location('retained_actual_listening_and_PCM_guards', S / GUARDS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def annotate(mapping, manifest, captions):
    rows = {row['id']: row for row in manifest['screenshots']}
    require(len(mapping['cue_correspondence']) == len(captions) == 135, 'Incomplete actual cue set.')
    entries = []
    for number, (retained, actual) in enumerate(zip(mapping['cue_correspondence'], captions), 1):
        require(retained['cue'] == number and abs(retained['start'] - actual['start']) < 1e-9
                and abs(retained['end'] - actual['end']) < 1e-9 and retained['text'].split() == actual['text'].split(),
                'Actual SRT words/endpoints differ from Root-reviewed map.')
        row = rows[retained['screenshot_id']]
        require(row['sha256'] == retained['source_sha256'], 'Caption map source identity changed.')
        refs = {}
        for literal in row['visible_labels']:
            if re.search(r'(?<!\w)' + re.escape(literal) + r'(?!\w)', actual['text'], re.I):
                refs[literal] = literal
        for literal, phrases in ALIASES.get(retained['scene_id'], {}).items():
            if literal in row['visible_labels']:
                for phrase in phrases:
                    if norm(phrase) in norm(actual['text']):
                        refs[literal] = phrase
                        break
        require(all(label in row['visible_labels'] and norm(phrase) in norm(actual['text']) for label, phrase in refs.items()),
                'Unseen source label or absent spoken reference.')
        entries.append(dict(retained, start=actual['start'], end=actual['end'], text=actual['text'],
                            required_labels=list(refs), spoken_references=refs, instructional=bool(refs)))
    return entries


def instructions(lesson, mapping, manifest, entries, parent):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import instruction_scene_digest, _Validator, _normalized
    rows = {row['id']: row for row in manifest['screenshots']}
    scenes = []
    for original in lesson['scenes']:
        spans = [x for x in mapping['source_spans'] if x['scene_id'] == original['id']]
        caps = [x for x in entries if x['scene_id'] == original['id']]
        require(' '.join(x['text'] for x in caps).split() == original['narration'].split(), 'Scene script continuity changed.')
        screens = [{'screenshot_id': x['capture_id'], 'start': x['proposed_start_seconds'],
                    'end': x['proposed_end_seconds']} for x in spans]
        require(screens and all(x['end'] > x['start'] for x in screens), 'Missing or nonpositive real source span.')
        for cue in caps:
            require(any(x['screenshot_id'] == cue['screenshot_id'] and x['start'] <= cue['start'] + 1e-9
                        and x['end'] >= cue['end'] - 1e-9 for x in screens), 'Actual caption crosses mapped source boundary.')
        require(any(x['required_labels'] for x in caps), 'Operational scene needs a visible-control spoken reference.')
        scene = {'id': original['id'], 'title': original['title'], 'kind': 'operational',
                 'start': screens[0]['start'], 'end': screens[-1]['end'], 'screens': screens,
                 'captions': caps, 'visual_required_labels': original['required_labels']}
        scene['instruction_review'] = {'passed': True, 'reviewer': 'Root complete map; Codex exact literal/source/SRT binding',
            'reviewed_at': parent['reviewed_at'], 'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(scene, rows), 'root_timing_review_file': PARENT.as_posix(),
            'root_timing_review_sha256': PARENT_SHA,
            'method': 'Retain genuine Root full39span/1134word source correspondence and original35 bounded pixel/DOM reviews. Use only actual SRT endpoints with renderer arithmetic, unchanged source words and complete source labels. Exact adjacent same-image raw66+67 sentence merge accepted by Root. No new pixel, encoded-frame, browser-playback or human hearing claim.'}
        validator = _Validator(S)
        for cue in caps:
            validator.spoken_references(cue, {_normalized(x) for x in cue['required_labels']}, 'caption', True)
        validator.instruction_review(scene, rows, {key: {_normalized(x) for x in row['visible_labels']}
                                                  for key, row in rows.items()}, 'source scene', 'Core')
        require(not validator.issues, 'Actual source binding failed: ' + json.dumps(validator.issues))
        scenes.append(scene)
    return scenes


def preflight():
    guards = retained_guards()
    frozen = json.loads(contained(FREEZE / 'source-freeze.json').read_text())
    require((frozen['scenes'], frozen['words'], frozen['accepted_images'], frozen['untimed_exact_spans']) == (16, 1134, 35, 39),
            'Frozen source scope changed.')
    for name, digest in frozen['files'].items():
        require(sha(contained(FREEZE / name)) == digest, 'Changed frozen archive member: ' + name)
    lesson = json.loads(contained(FROZEN).read_text())
    manifest = json.loads(contained(MANIFEST).read_text())
    mapping = json.loads(contained(MAP).read_text())
    parent = json.loads(contained(PARENT).read_text())
    require(parent.get('reviewer') == 'Root' and parent.get('human_listening_claim') is False
            and parent.get('complete_source_and_cue_correspondence_reviewed') is True, 'Genuine Root complete map review required.')
    require((parent['lesson_sha256'], parent['audio_sha256'], parent['correspondence_sha256'], parent['source_spans'],
             parent['derived_cues'], parent['original_cues']) == (SOURCE_SHA, AUDIO_SHA, PINS[MAP], 39, 135, 136), 'Root receipt identities/scope differ.')
    date(parent['reviewed_at'])
    require((mapping['lesson_sha256'], mapping['audio_sha256']) == (SOURCE_SHA, AUDIO_SHA), 'Map source/audio identity changed.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    from verify_capture_evidence import _image_dimensions
    raw, checked = load_cues(contained(ORIGINAL_RAW)), load_cues(contained(ORIGINAL_CHECKED))
    derived_raw, derived = load_cues(contained(DERIVED_RAW)), load_cues(contained(CAPTIONS))
    original_qa = json.loads(contained(ORIGINAL_QA).read_text())
    qa = json.loads(contained(DERIVED_QA).read_text())
    duration = guards.verify_audio_qa(original_qa, raw, checked, SOURCE_SHA, AUDIO_SHA, PINS[ORIGINAL_RAW], PINS[ORIGINAL_CHECKED], 136)
    require(guards.verify_audio_qa(qa, derived_raw, derived, SOURCE_SHA, AUDIO_SHA, PINS[DERIVED_RAW], PINS[CAPTIONS], 135)
            == duration == mapping['decoded_duration_seconds'] == 476.8914375, 'Actual full PCM duration changed.')
    words = [word for scene in lesson['scenes'] for word in scene['narration'].split()]
    require(len(lesson['scenes']) == 16 and len(words) == 1134 and [word for cue in derived for word in cue['text'].split()] == words,
            'Full frozen1134word script is not continuous in actual captions.')
    require(len(manifest['screenshots']) == 35 and len({row['id'] for row in manifest['screenshots']}) == 35, 'Missing or duplicate actual sources.')
    for row in manifest['screenshots']:
        require(row['app'] == 'Core' and sha(contained(row['file'])) == row['sha256']
                and _image_dimensions(contained(row['file'])) == (row['width'], row['height']), 'Actual Core source pixels changed.')
        require(sha(contained(row['dom_file'])) == row['dom_sha256'], 'Actual source DOM changed.')
        review = row['capture_review']
        require(review.get('passed') is True and review.get('sha256') == row['sha256']
                and review.get('reviewer'), 'Actual source review identity missing.')
        require(date(review['reviewed_at']) >= date(row['provenance']['captured_at']), 'Source review predates its image.')
    spans = mapping['source_spans']
    require(len(spans) == 39 and spans[0]['proposed_start_seconds'] == 0
            and spans[-1]['proposed_end_seconds'] == duration, 'Incomplete measured source coverage.')
    position = 0
    for number, span in enumerate(spans, 1):
        require(span['span'] == number and span['word_start'] == position and span['word_end'] > position,
                'Source span order or word continuity changed.')
        require(span['exact_narration_span'].split() == words[position:span['word_end']], 'Source span transcript differs.')
        position = span['word_end']
        if number > 1:
            require(span['proposed_start_seconds'] == spans[number - 2]['proposed_end_seconds'], 'Source gap or overlap.')
    require(position == 1134 and not mapping['finer_cuts'], 'Unexpected unresolved cut or missing final source words.')
    merge = mapping['same_image_caption_merge']
    require(merge['raw_cues'] == [66, 67] and merge['same_screenshot_id'] == '001-published-v1-quickentry-custom-form'
            and merge['start'] == checked[65]['start'] and abs(merge['end'] - checked[66]['end']) < 1e-9
            and merge['text'].split() == (checked[65]['text'] + ' ' + checked[66]['text']).split(), 'Accepted same-image merge changed.')
    entries = annotate(mapping, manifest, derived)
    scenes = instructions(lesson, mapping, manifest, entries, parent)
    return {'guards': guards, 'lesson': lesson, 'manifest': manifest, 'mapping': mapping, 'parent': parent,
            'original_qa': original_qa, 'qa': qa, 'duration': duration, 'entries': entries, 'scenes': scenes}


def listening(data, expected_sha, override=None):
    require(isinstance(expected_sha, str) and re.fullmatch('[a-f0-9]{64}', expected_sha), 'Supply exact genuine User full-listening receipt SHA256.')
    relative = str(LISTENING) if override is None else override
    path = contained(relative)
    require(sha(path) == expected_sha, 'Changed/unreviewed actual User listening receipt; assembly blocked.')
    record = data['guards'].validate_listening_record(json.loads(path.read_text()), SOURCE_SHA, AUDIO_SHA,
                                                      data['original_qa']['checked_at'])
    return record, Path(relative)


def build(listening_sha, parent_sha, receipt_file=None):
    require(parent_sha == PARENT_SHA, 'Supply exact genuine Root whole-map review SHA256.')
    data = preflight()
    heard, receipt = listening(data, listening_sha, receipt_file)
    now = datetime.now(timezone.utc).isoformat()
    caption_name = NAME + '.derived135.srt'
    scenes = [{key: row[key] for key in ['id', 'start', 'end', 'screens', 'instruction_review']} | {
        'captions': [{key: cue[key] for key in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']}
                     for cue in row['captions']]} for row in data['scenes']]
    plan = {'schema_version': 1, 'lesson_id': NAME, 'duration_seconds': data['duration'],
        'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': AUDIO.as_posix(), 'sha256': AUDIO_SHA, 'kind': 'approved_natural_narration',
            'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': AUDIO_SHA,
                'complete_natural_narration': True, 'evidence': heard['evidence'], 'qa_file': DERIVED_QA.as_posix(),
                'qa_sha256': PINS[DERIVED_QA], 'listening_review_file': receipt.as_posix(), 'listening_review_sha256': listening_sha}},
        'captions': {'file': (FINAL / caption_name).as_posix(), 'sha256': PINS[CAPTIONS], 'kind': 'speech_timed_srt',
            'approval': {'reviewer': 'Codex retained full-PCM/actual-SRT/source correspondence reviewer', 'reviewed_at': now,
                'sha256': PINS[CAPTIONS], 'audio_sha256': AUDIO_SHA, 'speech_timing_reviewed': True,
                'method': 'Unchanged actual service cue endpoints and Root-accepted same-image raw66+67 merge. Full original136 and derived135 PCM/exact-script QA passed. Renderer arithmetic retained before mapping digest; no endpoint interpolation or hearing inferred.'}},
        'capture_manifests': [{'file': (FINAL / 'captures.reviewed.json').as_posix(),
                               'sha256': hashlib.sha256(encoded(data['manifest'])).hexdigest()}],
        'screenshot_reviews': {row['id']: {'reviewer': row['capture_review']['reviewer'], 'reviewed_at': row['capture_review']['reviewed_at'],
            'sha256': row['sha256'], 'application_visible': True, 'labels_legible': True, 'no_errors': True} for row in data['manifest']['screenshots']},
        'scenes': scenes, 'parent_timing_review': {'file': PARENT.as_posix(), 'sha256': PARENT_SHA},
        'actual_source_map': {'file': MAP.as_posix(), 'sha256': PINS[MAP]}, 'publishable': False,
        'limitations': data['lesson']['scope_limits'] + ['Actual encoded-frame/caption review, genuine browser beginning/middle/end playback and strict public evidence qualification remain required after a separate render.']}
    return data, plan, contained(CAPTIONS).read_bytes(), caption_name


def write_new_directory(path, assets):
    contained(path.relative_to(S).as_posix(), must_exist=False)
    require(not path.exists() and not path.is_symlink(), 'New-only author refuses existing final-input package.')
    require(all('/' not in name and name not in ('.', '..') for name in assets), 'Final-input filename escaped package.')
    path.mkdir(parents=True)
    for name, body in assets.items():
        with (path / name).open('xb') as stream:
            stream.write(body)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    parser.add_argument('--listening-review-sha256')
    parser.add_argument('--listening-review-file')
    parser.add_argument('--root-timing-review-sha256')
    args = parser.parse_args(argv)
    if args.assemble:
        require(not (S / FINAL).exists() and not (S / FINAL).is_symlink(), 'Preserve existing final package.')
        data, plan, captions, name = build(args.listening_review_sha256, args.root_timing_review_sha256, args.listening_review_file)
        destination = S / FINAL
        assets = {'plan.json': encoded(plan), 'captures.reviewed.json': encoded(data['manifest']), name: captions}
        write_new_directory(destination, assets)
        sys.path.insert(0, str(ROOT / 'scripts'))
        from render_walkthrough import validate_inputs
        valid = validate_inputs(S / FROZEN, destination / 'plan.json', S)
        provenance = {'kind': 'guarded_actual_hearing_and_Root_map_final_inputs_not_rendered', 'lesson_id': NAME,
            'recipe_sha256': sha(__file__), 'frozen_source_sha256': SOURCE_SHA, 'audio_sha256': AUDIO_SHA,
            'actual_User_listening_receipt_sha256': args.listening_review_sha256, 'root_timing_review_sha256': PARENT_SHA,
            'actual_source_map_sha256': PINS[MAP], 'actual_derived_QA_sha256': PINS[DERIVED_QA],
            'strict_renderer_inputs_passed': True, 'outputs': {name: sha(destination / name) for name in assets},
            'rendered': False, 'canonical_site_target_or_Git_changed': False}
        with (destination / 'provenance.json').open('xb') as stream:
            stream.write(encoded(provenance))
        print(json.dumps({'strict_renderer_inputs_passed': True, 'scenes': len(valid['scenes']), 'cues': len(valid['cues']),
                          'plan_sha256': sha(destination / 'plan.json'), 'final_inputs_written': True, 'rendered': False}))
        return
    data = preflight()
    if args.listening_review_sha256:
        listening(data, args.listening_review_sha256, args.listening_review_file)
    print(json.dumps({'source_and_actual_audio_preflight_passed': True, 'scenes': 16, 'words': 1134, 'sources': 35,
        'source_spans': 39, 'cues': 135, 'duration_seconds': data['duration'], 'root_complete_map_sha256': PARENT_SHA,
        'actual_User_full_listening_required': True, 'expected_listening_receipt': LISTENING.as_posix(),
        'receipt_present': contained(LISTENING, must_exist=False).is_file(), 'final_inputs_written': False,
        'renderer_executed': False, 'canonical_or_site_changed': False}, indent=2))


if __name__ == '__main__':
    main()
