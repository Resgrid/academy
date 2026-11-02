"""Guarded complete Records lifecycle final-input author; default is read-only.

The unchanged 112 actual speech cues map to twenty source spans (seventeen
continuous image holds). Assembly requires exact hashes for the genuine User
full-listening receipt and the actual Root whole-map review. This tool never
renders, publishes, operates apps, changes canonical readiness or invokes Git.
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
NAME = 'core-records-training-entry'
PREPARER = Path('production/prepare_core_records_authoring_recipe_20261030.py')
PREPARER_SHA = '747e1bea35a446f32d535c1fce1397fdfda1c703065927f06abfb27c2eeca407'
RECIPE = Path('expansion/plans/core-records-training-entry-authoring-recipe-20261030/authoring-recipe.json')
RECIPE_SHA = '921ccea34e76a229b0020e9896b3dec72c17e4d859e040fcd46083dc28172276'
PARENT_SHA = '1947d90026a948856abf8ce24e7933eef7325add900c6c9440c64a18cbc59e32'
FINAL = Path('expansion/plans/core-records-training-entry-take-01-final-inputs-20261030')
CODE_PINS = {
    'scripts/render_walkthrough.py': '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881',
    'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
}
# Natural references use exact phrases present in the unchanged spoken cue and
# exact labels already reviewed in that cue's actual source image. Partial
# spoken identifiers are deliberately not used to pretend a whole ID was said.
ALIASES = {
    'training-form': {'ACADEMY-REC-29': ['Academy Rec Twenty-Nine']},
    'save-draft': {'Station / group': ['Station and group']},
    'attachment': {'358 bytes': ['three hundred fifty-eight bytes']},
    'revision-metadata': {
        'Item 1 / File Name': ['filename'],
        'Item 1 / Byte Size': ['byte size'],
        'Item 1 / Checksum': ['checksum'],
        'Item 1 / Classification': ['classification'],
    },
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def norm(value):
    return ' '.join(value.split()).casefold()


def retained_preparer():
    require(__debug__, 'Use ordinary Python; optimized execution disables retained guards.')
    require(sha(S / PREPARER) == PREPARER_SHA, 'Changed retained Records preparer.')
    require(sha(S / RECIPE) == RECIPE_SHA, 'Changed retained Records recipe.')
    for name, digest in CODE_PINS.items():
        require(sha(ROOT / name) == digest, 'Changed renderer/evidence validator; retain this recipe and obtain a new review.')
    spec = importlib.util.spec_from_file_location('retained_records_training_recipe', S / PREPARER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def receipt_path(default, override=None):
    value = default if override is None else override
    require(isinstance(value, (str, Path)), 'Use a public source-relative receipt path.')
    value = str(value)
    require(value and '\\' not in value and not re.search(r'(?i)(?:://|www\.)', value), 'Unsafe receipt path.')
    relative = Path(value)
    require(not relative.is_absolute() and not any(part in {'.', '..', 'private', '.git', 'node_modules'} or part.startswith('.env') for part in relative.parts), 'Unsafe receipt path.')
    path = S / relative
    require(path.resolve().is_relative_to(S.resolve()), 'Receipt path escapes the source root.')
    require(not any(p.is_symlink() for p in [path, *path.parents] if p != S and p.is_relative_to(S)), 'Symlinked receipt paths are rejected.')
    return path, relative


def actual_receipt(m, default, expected, kind, earliest, override=None):
    require(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'Supply the exact genuine ' + kind + ' receipt SHA256.')
    path, relative = receipt_path(default, override)
    require(path.is_file() and sha(path) == expected, 'Actual ' + kind + ' receipt absent or changed; assembly remains blocked.')
    return m.validate_receipt(json.loads(path.read_text()), kind, earliest), relative


def actual_audio_qa(qa, raw, corrected, pins):
    require(qa.get('passed') is True and qa.get('issues') == [] and qa.get('possible_speech_gaps') == [], 'Actual audio QA has an unresolved issue or speech gap.')
    require(qa['lesson']['sha256'] == pins['lesson_sha256'], 'Wrong frozen source in audio QA.')
    a = qa['audio']
    require(a['sha256'] == pins['audio_sha256'] and a['full_decode'] == 'passed', 'Wrong or undecoded actual audio.')
    duration = a['duration_seconds']
    require(type(duration) in (int, float) and duration > raw[-1]['end'], 'Decoded audio does not close the last speech cue.')
    require(abs(a['decoded_samples'] / a['sample_rate'] - duration) < 1e-6, 'Duration is not actual complete PCM length.')
    require(qa['alignment']['match_ratio'] == 1.0 and qa['alignment']['text_changes'] == [] and qa['alignment']['cues'] == 112, 'Changed or incomplete actual script correspondence.')
    require(len(raw) == len(corrected) == 112 and qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0, 'Wrong count or silent speech cue.')
    require(qa['raw_captions']['sha256'] == pins['raw_sha256'] and qa['corrected_captions']['sha256'] == pins['corrected_sha256'] and qa['corrected_captions']['exact_script'] is True, 'Actual QA caption identity changed.')
    require(raw == corrected, 'Corrected captions changed actual words or endpoints beyond line wrapping.')
    for key, cues in [('raw_captions', raw), ('corrected_captions', corrected)]:
        energy = qa[key]['energy']
        require(len(energy) == 112, 'Incomplete per-cue PCM checks.')
        for number, (cue, measured) in enumerate(zip(cues, energy), 1):
            require(measured['cue'] == number and measured['samples'] > 0 and measured['below_threshold'] is False and measured['rms'] >= qa['signal_threshold_rms'], 'Missing or silent actual cue PCM.')
            require(abs(measured['start'] - cue['start']) < 1e-6 and abs(measured['end'] - cue['end']) < 1e-6, 'Actual PCM cue endpoints changed.')
    return duration


def annotate(proposal, manifest, actual_cues):
    rows = {row['id']: row for row in manifest['screenshots']}
    result = []
    require(len(proposal['actual_cues']) == len(actual_cues) == 112, 'Incomplete actual cue set.')
    for original, actual in zip(proposal['actual_cues'], actual_cues):
        require(abs(original['start'] - actual['start']) < 1e-9 and abs(original['end'] - actual['end']) < 1e-9 and original['text'].split() == actual['text'].split(), 'Actual SRT and retained source proposal differ.')
        require(len(original['scene_ids']) == len(original['source_ids_in_exact_spoken_order']) == 1 and original['within_cue_screen_cut_unresolved'] is False, 'An actual cue crosses a source/scene boundary.')
        scene = original['scene_ids'][0]
        ident = original['source_ids_in_exact_spoken_order'][0]
        require(ident in rows, 'Actual cue names an absent source image.')
        refs = {}
        for literal in rows[ident]['visible_labels']:
            if re.search(r'(?<!\w)' + re.escape(literal) + r'(?!\w)', original['text'], re.I):
                refs[literal] = literal
        for literal, phrases in ALIASES.get(scene, {}).items():
            if literal not in rows[ident]['visible_labels']:
                continue
            for phrase in phrases:
                if norm(phrase) in norm(original['text']):
                    refs[literal] = phrase
                    break
        require(all(literal in rows[ident]['visible_labels'] and norm(phrase) in norm(original['text']) for literal, phrase in refs.items()), 'Absent actual control or spoken phrase.')
        result.append({'cue': original['cue'], 'scene_id': scene, 'screenshot_id': ident,
            'start': actual['start'], 'end': actual['end'], 'text': actual['text'],
            'required_labels': list(refs), 'spoken_references': refs, 'instructional': bool(refs)})
    return result


def instruction_scenes(lesson, proposal, manifest, captions, parent_file):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    rows = {row['id']: row for row in manifest['screenshots']}
    result = []
    now = datetime.now(timezone.utc).isoformat()
    for authored in lesson['scenes']:
        spans = [span for span in proposal['source_spans'] if span['scene_id'] == authored['id']]
        cues = [cue for cue in captions if cue['scene_id'] == authored['id']]
        screens = [{'screenshot_id': span['source_id'], 'start': span['proposed_start_seconds'], 'end': span['proposed_end_seconds']} for span in spans]
        require(screens and all(screen['end'] > screen['start'] for screen in screens), 'Missing/unresolved source interval.')
        require(' '.join(cue['text'] for cue in cues).split() == authored['narration'].split(), 'Scene narration differs from the exact actual speech.')
        require(any(cue['required_labels'] for cue in cues), 'Operational scene lacks an actual spoken-control reference.')
        for cue in cues:
            require(any(screen['screenshot_id'] == cue['screenshot_id'] and screen['start'] <= cue['start'] + 1e-6 and screen['end'] >= cue['end'] - 1e-6 for screen in screens), 'A mapped cue crosses its real source interval.')
        full = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational',
            'start': screens[0]['start'], 'end': screens[-1]['end'], 'visual_required_labels': authored['required_labels'],
            'screens': screens, 'captions': cues}
        full['instruction_review'] = {'passed': True, 'reviewer': 'Codex retained source/literal correspondence reviewer; actual Root complete-map review',
            'reviewed_at': now, 'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(full, rows), 'parent_review_file': parent_file.as_posix(), 'parent_review_sha256': PARENT_SHA,
            'method': 'Exact frozen script, retained independently reviewed sixteen source images, unchanged112 real speech cues, and genuine Root twenty-span/seventeen-hold review. Each current literal/phrase and source interval is checked. No new original-pixel, encoded-frame, browser-playback or User hearing is claimed.'}
        validator = _Validator(S)
        for cue in cues:
            validator.spoken_references(cue, {_normalized(label) for label in cue['required_labels']}, 'source caption', True)
        validator.instruction_review(full, rows, {key: {_normalized(label) for label in row['visible_labels']} for key, row in rows.items()}, 'source scene', lesson['app'])
        require(not validator.issues, 'Actual source instruction validation failed: ' + json.dumps(validator.issues))
        result.append(full)
    return result


def preflight():
    m = retained_preparer()
    recipe, qa, assets = m.prepare()
    require((S / RECIPE).read_bytes() == assets['authoring-recipe.json'], 'Retained recipe no longer reproduces exactly.')
    config = recipe['input_pins']
    base = Path('expansion/plans') / config['folder']
    proposal = json.loads((S / m.OLD / 'correspondence.proposed.json').read_text())
    lesson = json.loads((S / recipe['source_file']).read_text())
    manifest = json.loads((S / base / config['captures']).read_text())
    parent, parent_file = actual_receipt(m, m.PARENT, PARENT_SHA, 'parent', qa['checked_at'])
    sys.path.insert(0, str(ROOT / 'scripts'))
    from qa_narration import alignment
    from verify_capture_evidence import _caption_cues
    def cues(path):
        text = path.read_text()
        parsed, strict = alignment.parse_srt(text), _caption_cues(text)
        require(len(parsed) == len(strict), 'Caption parsers disagree about the number of real cues.')
        # Use the evidence validator's explicit-millisecond arithmetic, just as
        # the renderer does. The historical proposal's different addition order
        # can differ by one binary floating-point bit; no SRT endpoint moves.
        return [{'start': exact[0], 'end': exact[1], 'text': ' '.join(c['text'].split())} for c, exact in zip(parsed, strict)]
    raw_file = Path('expansion/audio') / (NAME + '-generated-20261029.raw.srt')
    corrected_file = Path('expansion/audio') / (NAME + '.actual.corrected.srt')
    raw, corrected = cues(S / raw_file), cues(S / corrected_file)
    duration = actual_audio_qa(qa, raw, corrected, config)
    require(duration == proposal['decoded_audio_seconds'] == recipe['decoded_duration_seconds'], 'Changed actual decoded duration.')
    require((len(lesson['scenes']), len(manifest['screenshots']), len(proposal['source_spans']), len(proposal['whole_cue_continuous_holds_proposed'])) == (12, 16, 20, 17), 'Reviewed source scope changed.')
    require(proposal['unresolved_boundaries'] == [] and proposal['source_spans'][-1]['proposed_end_seconds'] == duration, 'Source endpoint is unresolved or does not close at actual media duration.')
    entries = annotate(proposal, manifest, corrected)
    for cue, real in zip(entries, corrected):
        require((cue['start'], cue['end'], cue['text'].split()) == (real['start'], real['end'], real['text'].split()), 'Caption annotations changed the actual speech timing or text.')
    scenes = instruction_scenes(lesson, proposal, manifest, entries, parent_file)
    return {'preparer': m, 'recipe': recipe, 'config': config, 'base': base, 'qa': qa, 'lesson': lesson,
        'manifest': manifest, 'proposal': proposal, 'entries': entries, 'scenes': scenes, 'duration': duration,
        'parent': parent, 'parent_file': parent_file, 'corrected_file': corrected_file}


def build(listening_sha, parent_sha, listening_override=None):
    require(parent_sha == PARENT_SHA, 'Supply the exact actual Root complete-map review SHA256.')
    data = preflight()
    m = data['preparer']
    heard, heard_file = actual_receipt(m, m.LISTENING, listening_sha, 'listening', data['qa']['checked_at'], listening_override)
    cfg = data['config']
    caption_name = NAME + '.aligned112.srt'
    now = datetime.now(timezone.utc).isoformat()
    scenes = [{'id': scene['id'], 'start': scene['start'], 'end': scene['end'], 'screens': scene['screens'],
        'captions': [{key: cue[key] for key in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']} for cue in scene['captions']],
        'instruction_review': scene['instruction_review']} for scene in data['scenes']]
    plan = {'schema_version': 1, 'lesson_id': NAME, 'duration_seconds': data['duration'],
        'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': 'expansion/audio/' + NAME + '.m4a', 'sha256': cfg['audio_sha256'], 'kind': 'approved_natural_narration',
            'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': cfg['audio_sha256'],
                'complete_natural_narration': True, 'evidence': heard['evidence'],
                'qa_file': data['recipe']['actual_audio_qa_file'], 'qa_sha256': cfg['qa_sha256'],
                'listening_review_file': heard_file.as_posix(), 'listening_review_sha256': listening_sha}},
        'captions': {'file': (FINAL / caption_name).as_posix(), 'sha256': cfg['corrected_sha256'], 'kind': 'speech_timed_srt',
            'approval': {'reviewer': 'Codex exact frozen-script/actual-cue/full-PCM metadata reviewer', 'reviewed_at': now,
                'sha256': cfg['corrected_sha256'], 'audio_sha256': cfg['audio_sha256'], 'speech_timing_reviewed': True,
                'method': 'All112 actual raw/corrected SRT cue endpoints and exact words retained; complete decoded PCM and per-cue script/signal checks. No split, estimated cut, interpolation or human hearing inferred from signal.'}},
        'capture_manifests': [{'file': (FINAL / 'captures.reviewed.json').as_posix(), 'sha256': hashlib.sha256(encoded(data['manifest'])).hexdigest()}],
        'screenshot_reviews': {row['id']: {'reviewer': row['capture_review']['reviewer'], 'reviewed_at': row['capture_review']['reviewed_at'],
            'sha256': row['sha256'], 'application_visible': True, 'labels_legible': True, 'no_errors': True} for row in data['manifest']['screenshots']},
        'scenes': scenes, 'parent_timing_review': {'file': data['parent_file'].as_posix(), 'sha256': PARENT_SHA},
        'source_timing_proposal': {'file': (m.OLD / 'correspondence.proposed.json').as_posix(), 'sha256': m.PROPOSAL_SHA},
        'publishable': False, 'limitations': [
            'Historical first-finalization sequence remains separate from the later amendment on the same record. No present-day database state is inferred.',
            'No physical training, attendance or unit response occurred. Empty participant/unit fields remain empty.',
            'HTML revision and stored public-handout metadata are demonstrated; no licensed PDF download or later amendment is claimed.',
            'Actual encoded-frame/caption/pixel review, genuine beginning/middle/end browser playback and the complete public evidence gate remain required after separate rendering.']}
    return data, plan, (S / data['corrected_file']).read_bytes(), caption_name


def write_new_directory(path, assets):
    require(not path.exists() and not path.is_symlink(), 'New-only final-input output refuses any existing package; preserve history.')
    require(path.resolve().is_relative_to(S.resolve()), 'Final output escapes source root.')
    path.mkdir(parents=True)
    for name, body in assets.items():
        with (path / name).open('xb') as stream:
            stream.write(body)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    parser.add_argument('--listening-review-sha256')
    parser.add_argument('--parent-timing-review-sha256')
    parser.add_argument('--listening-review-file')
    args = parser.parse_args(argv)
    if args.parent_timing_review_sha256 is not None:
        require(args.parent_timing_review_sha256 == PARENT_SHA, 'Supplied Root map review SHA256 differs from the actual retained review.')
    if args.listening_review_file is not None:
        require(args.listening_review_sha256, 'A receipt-file override needs its exact independently reviewed SHA256.')
    if args.assemble:
        require(not (S / FINAL).exists(), 'Preserve existing final-input packages.')
        data, plan, captions, caption_name = build(args.listening_review_sha256, args.parent_timing_review_sha256, args.listening_review_file)
        destination = S / FINAL
        assets = {'plan.json': encoded(plan), 'captures.reviewed.json': encoded(data['manifest']), caption_name: captions}
        write_new_directory(destination, assets)
        sys.path.insert(0, str(ROOT / 'scripts'))
        from render_walkthrough import validate_inputs
        checked = validate_inputs(S / data['recipe']['source_file'], destination / 'plan.json', S)
        provenance = {'kind': 'Guarded actual-review Records lifecycle final inputs; not rendered', 'recipe_sha256': sha(__file__),
            'source_sha256': data['config']['lesson_sha256'], 'audio_sha256': data['config']['audio_sha256'],
            'actual_User_listening_receipt_sha256': args.listening_review_sha256, 'actual_Root_timing_receipt_sha256': PARENT_SHA,
            'strict_renderer_inputs_passed': True, 'outputs': {name: sha(destination / name) for name in assets},
            'rendered_or_published': False, 'canonical_site_target_or_Git_changed': False}
        with (destination / 'provenance.json').open('xb') as stream:
            stream.write(encoded(provenance))
        print(json.dumps({'strict_renderer_inputs_passed': True, 'plan_sha256': sha(destination / 'plan.json'),
            'scenes': len(checked['scenes']), 'cues': len(checked['cues']), 'duration': checked['duration'], 'rendered': False}))
        return
    data = preflight()
    if args.listening_review_sha256:
        actual_receipt(data['preparer'], data['preparer'].LISTENING, args.listening_review_sha256, 'listening', data['qa']['checked_at'], args.listening_review_file)
    print(json.dumps({'lesson': NAME, 'source_actual_audio_and_Root_map_preflight_passed': True,
        'scenes': len(data['scenes']), 'actual_cues': len(data['entries']), 'source_images': len(data['manifest']['screenshots']),
        'source_spans': 20, 'continuous_holds': 17, 'decoded_duration': data['duration'],
        'expected_User_listening_receipt': data['preparer'].LISTENING.as_posix(),
        'actual_User_listening_required': True, 'expected_Root_review_sha256': PARENT_SHA,
        'final_inputs_written': False, 'rendered_or_published': False, 'canonical_or_site_changed': False}, indent=2))


if __name__ == '__main__':
    main()
