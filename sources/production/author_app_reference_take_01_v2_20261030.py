"""Guarded v2 full authoring for Dispatch reference, IC access and Responder Calls.

Preserves v1 and fixes only exact renderer cue arithmetic before digest creation.

Default reads only. --assemble requires the exact genuine User listening hash
AND retained Root transition hash; IC also requires a genuine Root projection
review. No renderer, publication, app operation, canonical or Git action occurs.
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
OUTPUTS = Path('production/app_reference_prepared_outputs_20261030.json')
OUTPUTS_SHA = 'e3501dadcbfb908ba924a43a4f6cdd3c4d872572f71c80e23648effd88f4435b'
SCHEMAS = Path('expansion/plans/app-reference-authoring-required-reviews-20261030')
# Exact existing literals -> unchanged natural cue phrases; no labels are added.
ALIASES = {
 'dispatch': {
  '01': {'☰': ['menu']},
  '02': {'🗂️': ['folder control'], '✕': ['close']},
  '03': {'Name (A-Z)': ['Name, A to Z'], 'Search POIs...': ['Search POIs']},
  '06': {'Search contacts...': ['Search contacts'], 'Training Warehouse (fictional)': ['Training Warehouse, marked fictional']},
  '07': {'No notes found for this contact': ['no notes'], 'No pre-incident plan has been recorded for this contact.': ['no pre-incident plan has been recorded'], 'No files have been attached to this contact.': ['no files have been attached']},
 },
 'ic': {
  '01-find-settings': {'MENU': ['menu']},
  '03-read-security-summary': {'Not set up. Set one up in Resgrid on the web.': ['not set up'], 'No passkeys for this app yet.': ['none yet'], 'No verifications in the last 30 days.': ['no verifications']},
  '05-review-shared-device': {'Device label (optional)': ['Device label']},
  '06-preferences-and-support': {'System ⚙️': ['System']},
  '07-read-sync-status': {'Sync & Offline Queue': ['Sync and Offline Queue'], '0 pending · 0 failed · 0 done': ['zero pending, zero failed and zero done']},
 },
 'responder': {
  '01': {'Search calls...': ['Search calls'], '#DEMO-0001': ['DEMO-0001']},
  '04': {'Type: User': ['User'], 'Type: Unit': ['Unit'], 'Group: Squad 3': ['Squad Three'], 'Group: Firehouse 51': ['Firehouse Fifty-one']},
  '06': {'Add a new note...': ['Add a new note']},
  '08': {'3': ['three'], '0': ['zero'], "CALLS I'M ON": ['Calls I’m On']},
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


def load_preparer():
    require(__debug__, 'Use ordinary Python; do not disable retained guards.')
    require(sha(S / OUTPUTS) == OUTPUTS_SHA, 'Changed completed-derived-input catalog.')
    outputs = json.loads((S / OUTPUTS).read_text())
    reference = outputs['preparer']
    require(sha(S / reference['file']) == reference['sha256'], 'Changed reviewed caption preparer.')
    spec = importlib.util.spec_from_file_location('three_reference_retained_preparer', S / reference['file'])
    preparer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preparer)
    catalog, parser, parent = preparer.inputs()
    generic = preparer.module('retained_reference_listening_and_PCM_guards', catalog['retained_listening_helper'])
    return outputs, preparer, catalog, parser, generic, parent


def validate_projection_review(record, projection, expected_provenance_sha):
    require(isinstance(record, dict) and record.get('reviewer') == 'Root', 'Actual Root projection review is required.')
    require(record.get('approved_for_public_label_projection') is True, 'IC public-label projection is not approved.')
    require(record.get('projection_provenance_sha256') == expected_provenance_sha, 'Root reviewed another projection.')
    for field, value in [('original_source_sha256', projection['original_source']['sha256']),
        ('projected_source_sha256', projection['prospective_source_sha256']),
        ('original_manifest_sha256', projection['original_manifest']['sha256']),
        ('projected_manifest_sha256', projection['prospective_manifest_sha256'])]:
        require(record.get(field) == value, 'Projection receipt identity differs: ' + field)
    require(record.get('narration_words_unchanged') is True and record.get('only_two_arrays_changed') is True,
        'Root must accept the exact limited metadata change.')
    require(record.get('human_listening_claim') is False, 'Projection review cannot impersonate User listening.')
    require(not re.search(r'(?i)(?:://|www\.)', json.dumps(record)), 'Root review receipt must be URL-free.')
    stamp = datetime.fromisoformat(record['recorded_at'].replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc), 'Root review needs a real nonfuture timezone-aware date.')
    return record


def use_projection(outputs, generic, expected_sha=None, override=None):
    projection = outputs['ic_projection']
    base = Path(projection['folder'])
    for name, digest in projection['pins'].items():
        require(sha(S / base / name) == digest, 'Changed IC proposed projection.')
    provenance = json.loads((S / base / 'projection.provenance.json').read_text())
    if expected_sha is None:
        return None
    require(re.fullmatch('[a-f0-9]{64}', expected_sha or ''), 'Supply exact genuine Root projection receipt hash.')
    path, relative = generic.receipt_path({'listening': projection['root_review_file']}, override)
    require(path.is_file() and sha(path) == expected_sha, 'Actual Root projection receipt absent/changed; IC assembly remains blocked.')
    record = validate_projection_review(json.loads(path.read_text()), provenance, projection['pins']['projection.provenance.json'])
    lesson = json.loads((S / base / 'lesson.learner-projection.proposed.json').read_text())
    manifest = json.loads((S / base / 'captures.public-projection.proposed.json').read_text())
    return {'lesson': lesson, 'manifest': manifest, 'frozen': base / 'lesson.learner-projection.proposed.json',
        'receipt_file': relative.as_posix(), 'receipt_sha256': expected_sha, 'record': record,
        'provenance': provenance, 'provenance_file': (base / 'projection.provenance.json').as_posix(),
        'provenance_sha256': projection['pins']['projection.provenance.json']}


def annotate(alias, proposal, manifest):
    rows = {row['id']: row for row in manifest['screenshots']}
    result = []
    for original in proposal['cue_correspondence']:
        cue = deepcopy(original)
        row, refs = rows[cue['screenshot_id']], {}
        for literal in row['visible_labels']:
            if re.search(r'(?<!\w)' + re.escape(literal) + r'(?!\w)', cue['text'], re.I):
                refs[literal] = literal
        for literal, phrases in ALIASES.get(alias, {}).get(cue['scene_id'], {}).items():
            if literal not in row['visible_labels']:
                continue
            for phrase in phrases:
                if norm(phrase) in norm(cue['text']):
                    refs[literal] = phrase
                    break
        require(all(literal in row['visible_labels'] and norm(phrase) in norm(cue['text']) for literal, phrase in refs.items()), 'Absent actual label or spoken phrase.')
        cue.update(required_labels=list(refs), spoken_references=refs, instructional=bool(refs))
        result.append(cue)
    return result


def source_instructions(lesson, proposal, manifest, entries, parent_reference):
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import instruction_scene_digest, _Validator, _normalized
    rows = {row['id']: row for row in manifest['screenshots']}
    scenes = []
    reviewed_at = datetime.now(timezone.utc).isoformat()
    for authored in lesson['scenes']:
        spans = [span for span in proposal['source_spans'] if span['scene_id'] == authored['id']]
        captions = [cue for cue in entries if cue['scene_id'] == authored['id']]
        screens = [{'screenshot_id': span['capture_id'], 'start': span['start']['seconds'], 'end': span['end']['seconds']} for span in spans]
        require(' '.join(cue['text'] for cue in captions).split() == authored['narration'].split(), 'Annotated scene transcript differs.')
        require(any(cue['required_labels'] for cue in captions), 'Operational scene lacks a visible-control reference.')
        for cue in captions:
            require(any(screen['screenshot_id'] == cue['screenshot_id'] and screen['start'] <= cue['start'] + 1e-6 and screen['end'] >= cue['end'] - 1e-6 for screen in screens), 'Actual cue crosses a mapped source boundary.')
        full = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational',
            'start': screens[0]['start'], 'end': screens[-1]['end'], 'screens': screens,
            'captions': captions, 'visual_required_labels': authored['required_labels']}
        full['instruction_review'] = {'passed': True, 'reviewer': 'Codex exact frozen-speech/source binding; retained Root source-transition review',
            'reviewed_at': reviewed_at, 'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(full, rows), 'root_transition_receipt': parent_reference,
            'method': 'Exact retained image/DOM review and Root-accepted source transitions. Every caption phrase/literal/source interval checked now; whole-word-group cuts and same-image caption readability derivation remain explicit. This is metadata correspondence review, not new original-pixel, encoded-frame, browser-playback or User listening.'}
        validator = _Validator(S)
        for cue in captions:
            validator.spoken_references(cue, {_normalized(label) for label in cue['required_labels']}, 'caption', True)
        validator.instruction_review(full, rows, {key: {_normalized(label) for label in row['visible_labels']} for key, row in rows.items()}, 'scene', lesson['app'])
        require(not validator.issues, 'Actual source instruction validation failed: ' + json.dumps(validator.issues))
        scenes.append(full)
    return scenes


def preflight(alias, projection_sha=None, projection_file=None):
    outputs, preparer, catalog, parser, generic, parent = load_preparer()
    require(alias in catalog['lessons'], 'Select dispatch, ic or responder.')
    cfg, proposal, rebuilt = preparer.propose(alias)
    prepared = outputs['lessons'][alias]
    for name, digest in prepared['pins'].items():
        require(sha(S / prepared['proposal'] / name) == digest, 'Changed actual derived QA/proposal input: ' + name)
    for name, body in rebuilt.items():
        require((S / prepared['proposal'] / name).read_bytes() == body, 'Proposal no longer reproduces exactly.')
    roles = cfg['roles']
    lesson = json.loads((S / roles['lesson']).read_text())
    manifest = json.loads((S / roles['manifest']).read_text())
    projection = use_projection(outputs, generic, projection_sha, projection_file) if alias == 'ic' else None
    if projection:
        require([scene['narration'] for scene in lesson['scenes']] == [scene['narration'] for scene in projection['lesson']['scenes']], 'Projection changed heard narration.')
        lesson, manifest = projection['lesson'], projection['manifest']
    original_qa = json.loads((S / roles['qa']).read_text())
    folder = Path(prepared['proposal'])
    raw = parser.cues(S / folder / 'captions.derived.srt')
    checked = parser.cues(S / folder / 'captions.derived.checked.srt')
    qa = json.loads((S / folder / 'derived-captions.actual.qa.json').read_text())
    duration = generic.verify_audio_qa(qa, raw, checked, cfg['expected_source_sha256'], cfg['expected_audio_sha256'],
        prepared['pins']['captions.derived.srt'], prepared['pins']['captions.derived.checked.srt'], prepared['derived_cues'])
    require(duration == proposal['decoded_duration_seconds'] and len(manifest['screenshots']) == cfg['images'], 'Derived source/audio scope changed.')
    entries = annotate(alias, proposal, manifest)
    require([(cue['start'], cue['end'], cue['text']) for cue in entries] == [(cue['start'], cue['end'], cue['text']) for cue in checked], 'Annotation changed derived cue timing/text.')
    # The renderer and evidence gate parse explicit SRT milliseconds. Historical
    # proposal floats may differ by one binary bit; retain all actual endpoints
    # and exact words while using that same arithmetic in the binding digest.
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    exact = load_cues(S / folder / 'captions.derived.checked.srt')
    require(len(exact) == len(entries), 'Renderer cue scope changed.')
    for cue, actual in zip(entries, exact):
        require(abs(cue['start'] - actual['start']) < 1e-9 and
                abs(cue['end'] - actual['end']) < 1e-9 and
                cue['text'] == actual['text'], 'Renderer cue endpoints or words differ.')
        cue.update(start=actual['start'], end=actual['end'], text=actual['text'])
    scenes = source_instructions(lesson, proposal, manifest, entries, catalog['parent'])
    return {'cfg': cfg, 'prepared': prepared, 'catalog': catalog, 'generic': generic, 'lesson': lesson,
        'manifest': manifest, 'proposal': proposal, 'entries': entries, 'scenes': scenes,
        'qa': qa, 'original_qa': original_qa, 'duration': duration, 'projection': projection,
        'renderer_lesson': projection['frozen'] if projection else Path(roles['lesson'])}


def listening(data, expected_sha, override=None):
    require(re.fullmatch('[a-f0-9]{64}', expected_sha or ''), 'Supply exact genuine User full-listening receipt SHA256.')
    generic = data['generic']
    path, relative = generic.receipt_path({'listening': data['cfg']['listening']}, override)
    require(path.is_file() and sha(path) == expected_sha, 'Actual User listening receipt absent/changed; assembly remains blocked.')
    # User heard the ORIGINAL immutable narration. IC's proposed label arrays
    # never cause an invented listening receipt for a different JSON metadata pin.
    record = generic.validate_listening_record(json.loads(path.read_text()), data['cfg']['expected_source_sha256'],
        data['cfg']['expected_audio_sha256'], data['original_qa']['checked_at'])
    return record, relative


def build(alias, listening_sha, timing_sha, projection_sha=None, receipt_override=None, projection_file=None):
    data = preflight(alias, projection_sha, projection_file)
    require(timing_sha == data['catalog']['parent']['sha256'], 'Supply exact retained Root transition review SHA256.')
    require(alias != 'ic' or data['projection'] is not None, 'IC public projection still requires the genuine hash-bound Root approval; no final inputs created.')
    heard, receipt = listening(data, listening_sha, receipt_override)
    cfg, prepared = data['cfg'], data['prepared']
    final = Path(cfg['final'] + '-v2')
    caption_name = cfg['name'] + f'.derived{prepared["derived_cues"]}.srt'
    caption_sha = prepared['pins']['captions.derived.checked.srt']
    qa_ref = Path(prepared['proposal']) / 'derived-captions.actual.qa.json'
    now = datetime.now(timezone.utc).isoformat()
    scenes = [{'id': scene['id'], 'start': scene['start'], 'end': scene['end'], 'screens': scene['screens'],
        'captions': [{key: cue[key] for key in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']} for cue in scene['captions']],
        'instruction_review': scene['instruction_review']} for scene in data['scenes']]
    plan = {'schema_version': 1, 'lesson_id': cfg['name'], 'duration_seconds': data['duration'],
        'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': cfg['roles']['audio'], 'sha256': cfg['expected_audio_sha256'], 'kind': 'approved_natural_narration',
            'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': cfg['expected_audio_sha256'],
                'complete_natural_narration': True, 'evidence': heard['evidence'], 'qa_file': qa_ref.as_posix(),
                'qa_sha256': prepared['pins']['derived-captions.actual.qa.json'], 'listening_review_file': receipt.as_posix(),
                'listening_review_sha256': listening_sha, 'heard_original_source_sha256': cfg['expected_source_sha256']}},
        'captions': {'file': (final / caption_name).as_posix(), 'sha256': caption_sha, 'kind': 'speech_timed_srt',
            'approval': {'reviewer': 'Codex actual script/service-marker/full-PCM caption reviewer', 'reviewed_at': now,
                'sha256': caption_sha, 'audio_sha256': cfg['expected_audio_sha256'], 'speech_timing_reviewed': True,
                'method': 'Original real SRT endpoints and genuine integer-second word groups only, explicit Root-accepted source transitions and same-image caption readability cuts/merges. Complete derived PCM/word/layout QA; no timing interpolation or inferred listening.'}},
        'capture_manifests': [{'file': (final / 'captures.reviewed.json').as_posix(), 'sha256': hashlib.sha256(encoded(data['manifest'])).hexdigest()}],
        'screenshot_reviews': {row['id']: {'reviewer': row['capture_review']['reviewer'], 'reviewed_at': row['capture_review']['reviewed_at'],
            'sha256': row['sha256'], 'application_visible': True, 'labels_legible': True, 'no_errors': True} for row in data['manifest']['screenshots']},
        'scenes': scenes, 'root_transition_review': data['catalog']['parent'],
        'actual_caption_derivation': {'file': str(Path(prepared['proposal']) / 'caption-derivation.json'), 'sha256': prepared['pins']['caption-derivation.json']},
        'publishable': False, 'limitations': data['proposal']['limits'] + ['Actual encoded-frame/caption/pixel review, genuine browser beginning/middle/end playback and the complete public evidence gate remain required.']}
    if data['projection']:
        projection = data['projection']
        plan['learner_label_projection'] = {'file': projection['provenance_file'], 'sha256': projection['provenance_sha256'],
            'root_review_file': projection['receipt_file'], 'root_review_sha256': projection['receipt_sha256'],
            'heard_original_source_sha256': cfg['expected_source_sha256'],
            'projected_renderer_source_sha256': projection['provenance']['prospective_source_sha256'], 'narration_words_unchanged': True}
    return data, plan, (S / prepared['proposal'] / 'captions.derived.checked.srt').read_bytes(), caption_name


def schemas():
    outputs, _, catalog, _, _, _ = load_preparer()
    assets = {}
    for alias, cfg in catalog['lessons'].items():
        assets[alias + '.listening-review.schema.json'] = encoded({'type': 'object',
            'required': ['reviewer', 'reviewed_at', 'lesson_sha256', 'audio_sha256', 'complete_natural_narration', 'evidence'],
            'properties': {'reviewer': {'const': 'User'}, 'reviewed_at': {'type': 'string', 'format': 'date-time'},
                'lesson_sha256': {'const': cfg['expected_source_sha256']}, 'audio_sha256': {'const': cfg['expected_audio_sha256']},
                'complete_natural_narration': {'const': True}, 'evidence': {'type': 'string'}, 'question_call_id': {'type': 'string'}},
            'description': 'Schema only, not an approval example. Runtime requires exact operator-supplied hash, URL-free real full natural/complete response and chronology after original full-audio QA.'})
    projection = json.loads((S / outputs['ic_projection']['folder'] / 'projection.provenance.json').read_text())
    assets['ic.root-projection-review.schema.json'] = encoded({'type': 'object', 'required': ['reviewer', 'recorded_at',
        'approved_for_public_label_projection', 'projection_provenance_sha256', 'original_source_sha256', 'projected_source_sha256',
        'original_manifest_sha256', 'projected_manifest_sha256', 'narration_words_unchanged', 'only_two_arrays_changed', 'human_listening_claim'],
        'properties': {'reviewer': {'const': 'Root'}, 'recorded_at': {'type': 'string', 'format': 'date-time'},
            'approved_for_public_label_projection': {'const': True},
            'projection_provenance_sha256': {'const': outputs['ic_projection']['pins']['projection.provenance.json']},
            'original_source_sha256': {'const': projection['original_source']['sha256']},
            'projected_source_sha256': {'const': projection['prospective_source_sha256']},
            'original_manifest_sha256': {'const': projection['original_manifest']['sha256']},
            'projected_manifest_sha256': {'const': projection['prospective_manifest_sha256']},
            'narration_words_unchanged': {'const': True}, 'only_two_arrays_changed': {'const': True}, 'human_listening_claim': {'const': False}},
        'description': 'Root reviews exactly two public label-array removals, preserving actual pixels and heard narration. This schema does not supply an actual receipt.'})
    return assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=['dispatch', 'ic', 'responder', 'all'], default='all')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--assemble', action='store_true')
    mode.add_argument('--write-review-schemas', action='store_true')
    parser.add_argument('--listening-review-sha256')
    parser.add_argument('--root-timing-review-sha256')
    parser.add_argument('--listening-review-file')
    parser.add_argument('--projection-review-sha256')
    parser.add_argument('--projection-review-file')
    args = parser.parse_args()
    require(not args.assemble or args.lesson != 'all', 'Assemble only one lesson per actual approval.')
    if args.assemble:
        data, plan, captions, caption_name = build(args.lesson, args.listening_review_sha256,
            args.root_timing_review_sha256, args.projection_review_sha256, args.listening_review_file, args.projection_review_file)
        generic = data['generic']
        destination = S / (data['cfg']['final'] + '-v2')
        assets = {'plan.json': encoded(plan), 'captures.reviewed.json': encoded(data['manifest']), caption_name: captions}
        generic.write_new_directory(destination, assets)
        sys.path.insert(0, str(ROOT / 'scripts'))
        from render_walkthrough import validate_inputs
        valid = validate_inputs(S / data['renderer_lesson'], destination / 'plan.json', S)
        provenance = {'kind': 'guarded_actual_approval_reference_final_inputs_not_rendered', 'recipe_sha256': sha(__file__),
            'root_transition_sha256': data['catalog']['parent']['sha256'], 'actual_User_listening_receipt_sha256': args.listening_review_sha256,
            'actual_derived_audio_qa_sha256': data['prepared']['pins']['derived-captions.actual.qa.json'],
            'original_heard_source_sha256': data['cfg']['expected_source_sha256'], 'renderer_inputs_passed': True,
            'outputs': {name: sha(destination / name) for name in assets}, 'rendered_or_publication_approved': False}
        with (destination / 'provenance.json').open('xb') as stream:
            stream.write(encoded(provenance))
        print(json.dumps({'strict_renderer_inputs_passed': True, 'scenes': len(valid['scenes']), 'cues': len(valid['cues']),
            'plan_sha256': sha(destination / 'plan.json'), 'rendered': False}))
        return
    aliases = ['dispatch', 'ic', 'responder'] if args.lesson == 'all' else [args.lesson]
    data = [(alias, preflight(alias, args.projection_review_sha256 if alias == 'ic' else None, args.projection_review_file)) for alias in aliases]
    if args.write_review_schemas:
        assets = schemas()
        data[0][1]['generic'].write_new_directory(S / SCHEMAS, assets)
    print(json.dumps([{'lesson': row['cfg']['name'], 'source_and_actual_audio_preflight_passed': True,
        'derived_cues': len(row['entries']), 'source_spans': len(row['proposal']['source_spans']),
        'actual_User_listening_required': True, 'IC_public_projection_review_required': alias == 'ic' and row['projection'] is None,
        'expected_listening_receipt': row['cfg']['listening'], 'source_for_actual_listening_receipt': row['cfg']['expected_source_sha256'],
        'expected_root_timing_sha256': row['catalog']['parent']['sha256'], 'final_inputs_written': False,
        'review_schemas_written': args.write_review_schemas, 'rendered_or_ready': False} for alias, row in data], indent=2))


if __name__ == '__main__':
    main()
