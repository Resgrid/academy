"""Finish Training renderer inputs after genuine narration approval.

Default is read-only. No speech generation, rendering, readiness, publication,
browser or Git operation is performed. Existing source and timing are retained.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
CATALOG = S / 'production/training_final_authoring_inputs_20261030.json'
CATALOG_SHA = '9575a4449ee4c5a5ccab465bf5b0db13b14a2b79f60b68ec1b58f475e81261cb'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def module(name, reference):
    path = S / reference['file']
    require(sha(path) == reference['sha256'], 'Changed retained helper: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def preflight():
    require(__debug__, 'Do not disable retained guards.')
    require(sha(CATALOG) == CATALOG_SHA, 'Changed reviewed Training catalog.')
    cfg = json.loads(CATALOG.read_text())
    roles = cfg['roles']
    for key, reference in roles.items():
        require(sha(S / reference['file']) == reference['sha256'], 'Changed input: ' + key)
    scaffold = module('retained_training_source_scaffold', roles['scaffold_helper'])
    scaffold.prepare()
    generic = module('retained_training_approval_guards', roles['generic_helper'])
    mapping = module('retained_training_instruction_mapper', roles['mapping_helper'])
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    lesson = json.loads((S / roles['lesson']['file']).read_text())
    manifest = json.loads((S / roles['manifest']['file']).read_text())
    proposal = json.loads((S / roles['proposal']['file']).read_text())
    qa = json.loads((S / roles['qa']['file']).read_text())
    parent = json.loads((S / roles['root_review']['file']).read_text())
    require(parent['reviewer'] == 'Root' and parent['human_listening_claim'] is False,
            'Require actual Root source review, separate from listening.')
    require(parent['complete_cue_correspondence_reviewed'] is True and
            parent['correspondence_sha256'] == roles['proposal']['sha256'] and
            parent['source_sha256'] == roles['lesson']['sha256'] and
            parent['audio_sha256'] == roles['audio']['sha256'], 'Wrong source review.')
    raw, checked = load_cues(S / roles['raw']['file']), load_cues(S / roles['captions']['file'])
    duration = generic.verify_audio_qa(qa, raw, checked, roles['lesson']['sha256'],
        roles['audio']['sha256'], roles['raw']['sha256'], roles['captions']['sha256'], 99)
    entries = deepcopy(proposal['cue_correspondence'])
    require(len(entries) == 99 and len(lesson['scenes']) == 10, 'Wrong Training scope.')
    for cue, actual in zip(entries, checked):
        require(abs(cue['start'] - actual['start']) < 0.001 and
                abs(cue['end'] - actual['end']) < 0.001 and
                cue['text'] == actual['text'], 'Changed actual derived cue.')
        # Use the renderer's exact SRT arithmetic in the instruction digest.
        # Historical JSON floats can differ by one binary bit; no SRT moves.
        cue.update(start=actual['start'], end=actual['end'], text=actual['text'])
    by_number = {cue['cue']: cue for cue in entries}
    spans = []
    assigned = []
    for scene in proposal['scenes']:
        for number in scene['derived_cues']:
            by_number[number]['scene_id'] = scene['scene_id']
            assigned.append(number)
        spans.extend({'scene_id': scene['scene_id'], 'capture_id': span['capture_ref'],
            'start': {'seconds': span['actual_start']}, 'end': {'seconds': span['actual_end']}}
            for span in scene['source_spans'])
    require(assigned == list(range(1, 100)), 'Incomplete or duplicate scene coverage.')
    require(spans[0]['start']['seconds'] == 0 and
            spans[-1]['end']['seconds'] == duration, 'Incorrect full-audio source extent.')
    parent_ref = roles['root_review']
    scenes = mapping.source_instructions(lesson, {'source_spans': spans}, manifest,
                                         entries, parent_ref)
    return cfg, generic, lesson, manifest, qa, duration, scenes


def assemble(expected_receipt_sha, receipt_override=None):
    cfg, generic, lesson, manifest, qa, duration, scenes = preflight()
    roles = cfg['roles']
    path, relative = generic.receipt_path({'listening': cfg['default_listening_file']}, receipt_override)
    require(path.is_file() and sha(path) == expected_receipt_sha,
            'Actual hash-bound User listening receipt is missing or changed.')
    original_qa = json.loads((S / roles['original_qa']['file']).read_text())
    heard = generic.validate_listening_record(json.loads(path.read_text()),
        roles['lesson']['sha256'], roles['audio']['sha256'], original_qa['checked_at'])
    folder = Path(cfg['final_folder'])
    captions = folder / 'core-training-administration.derived99.srt'
    now = datetime.now(timezone.utc).isoformat()
    plan = {'schema_version': 1, 'lesson_id': lesson['id'], 'duration_seconds': duration,
        'instruction_mapping': 'reviewed_scene_coverage',
        'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': roles['audio']['file'], 'sha256': roles['audio']['sha256'],
            'kind': 'approved_natural_narration', 'approval': {
                'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'],
                'sha256': roles['audio']['sha256'], 'complete_natural_narration': True,
                'evidence': heard['evidence'], 'qa_file': roles['qa']['file'],
                'qa_sha256': roles['qa']['sha256'], 'listening_review_file': relative.as_posix(),
                'listening_review_sha256': expected_receipt_sha}},
        'captions': {'file': captions.as_posix(), 'sha256': roles['captions']['sha256'],
            'kind': 'speech_timed_srt', 'approval': {'reviewer': 'Codex retained Training source/caption reviewer',
                'reviewed_at': now, 'sha256': roles['captions']['sha256'],
                'audio_sha256': roles['audio']['sha256'], 'speech_timing_reviewed': True,
                'method': 'Retained exact narration, genuine service cuts at 191, 233 and 285 seconds, and the explicit same-image caption merge; full derived PCM/caption QA. No inferred hearing.'}},
        'capture_manifests': [{'file': (folder / 'captures.reviewed.json').as_posix(),
            'sha256': hashlib.sha256(encoded(manifest)).hexdigest()}],
        'screenshot_reviews': {row['id']: {'reviewer': row['capture_review']['reviewer'],
            'reviewed_at': row['capture_review']['reviewed_at'], 'sha256': row['sha256'],
            'application_visible': True, 'labels_legible': True, 'no_errors': True}
            for row in manifest['screenshots']},
        'scenes': [{'id': scene['id'], 'start': scene['start'], 'end': scene['end'],
            'screens': scene['screens'], 'captions': [{key: cue[key] for key in
                ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']}
                for cue in scene['captions']], 'instruction_review': scene['instruction_review']}
            for scene in scenes], 'root_source_review': roles['root_review'],
        'publishable': False, 'limitations': ['Encoded-frame/caption review and genuine browser beginning/middle/end playback remain required after rendering.']}
    assets = {'plan.json': encoded(plan), 'captures.reviewed.json': encoded(manifest),
              captions.name: (S / roles['captions']['file']).read_bytes()}
    generic.write_new_directory(S / folder, assets)
    from render_walkthrough import validate_inputs
    result = validate_inputs(S / roles['lesson']['file'], S / folder / 'plan.json', S)
    provenance = {'kind': 'Training actual-approved final inputs, not a finished video',
        'recipe_sha256': sha(__file__), 'catalog_sha256': CATALOG_SHA,
        'listening_receipt_sha256': expected_receipt_sha, 'renderer_inputs_passed': True,
        'rendered': False, 'canonical_or_site_changed': False,
        'outputs': {name: sha(S / folder / name) for name in assets}}
    with (S / folder / 'provenance.json').open('xb') as stream:
        stream.write(encoded(provenance))
    return {'strict_renderer_inputs_passed': True, 'scenes': len(result['scenes']),
            'cues': len(result['cues']), 'rendered': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    parser.add_argument('--listening-review-sha256')
    parser.add_argument('--listening-review-file')
    args = parser.parse_args()
    if args.assemble:
        require(args.listening_review_sha256, 'Supply actual User listening receipt SHA256.')
        print(json.dumps(assemble(args.listening_review_sha256, args.listening_review_file)))
    else:
        cfg, _, _, _, _, duration, scenes = preflight()
        print(json.dumps({'source_audio_preflight_passed': True, 'duration_seconds': duration,
            'scenes': len(scenes), 'cues': 99, 'actual_User_listening_pending': True,
            'expected_receipt': cfg['default_listening_file'], 'final_inputs_written': False,
            'rendered_or_ready': False}, indent=2))
