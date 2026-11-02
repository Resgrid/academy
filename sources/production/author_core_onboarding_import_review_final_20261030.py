"""Guarded final-input author for the bounded onboarding import review.

Default execution verifies immutable source/audio/caption correspondence only.
--assemble creates a NEW package after separate genuine, hash-bound Root whole
map and User complete-listening receipts. It never renders, applies an import,
publishes, adopts a lesson, changes the site, operates an app or performs Git work.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
FREEZE = Path('expansion/plans/core-onboarding-import-review-capture-freeze-20261030')
PROPOSAL = Path('expansion/plans/core-onboarding-import-review-proposed127-correspondence-20261030')
FINAL = Path('expansion/plans/core-onboarding-import-review-take-01-final-inputs-20261030')
LESSON = FREEZE / 'core-onboarding-import-review.narrated-source.json'
AUDIO = Path('expansion/audio/core-onboarding-import-review.m4a')
QA = Path('expansion/audio/core-onboarding-import-review.actual.qa.json')
RAW = Path('expansion/audio/core-onboarding-import-review-generated-20261030.raw.srt')
CAPTIONS = Path('expansion/audio/core-onboarding-import-review.actual.corrected.srt')
PINS = {
    str(FREEZE / 'freeze.json'): '5fbacadbb3a9422ea6dcc2141afe46a98001b37b9200720d66223cf8e916aadf',
    str(LESSON): '9f01f98c97b07f6a1eab43e1b933b90933c57670b3771f61fd25259e7f2382c5',
    str(FREEZE / 'narration.txt'): '976e0af58af91f0cf23a608e88a7828acd41b7747b93e2d00d09f1ffed273f4a',
    str(FREEZE / 'screen-sequence.json'): '5c0c73f747bc0fbf5270c23de086b5dcb52078de46b85f8a0ae2f0a1edd919b5',
    str(FREEZE / 'captures.reviewed.json'): 'a0b26aa4e2f3545267c2ac91161ccc6a009fd4f74782f183bdba9ce60d612ac8',
    str(FREEZE / 'source-asset-pins.json'): 'c1d19dc9100d43f3d3989f9c916a5858cea4c13db4a6706d1c185b61d5ce6434',
    str(FREEZE / 'root-script-review.original.json'): 'e27028e174407142cef3bf0cf63e408217cf47cbf405d2c9643ec9e324446af8',
    str(PROPOSAL / 'correspondence.proposed.json'): 'a320dcedb015dc60c7e9b9b229d03574ba39ba9d8c50e31eb630cc467a2c6ac6',
    str(PROPOSAL / 'cue-screen-correspondence.txt'): '4e6416ec64539b52b738ca2183b05d14c1d9e641061094d4e8b82620df6bf629',
    str(PROPOSAL / 'caption-layout-measurements.json'): 'd8088de65a904e88e7bec88bd05a9dfc5f73ec2d2a968d4e4e701a7e50f10785',
    str(PROPOSAL / 'handoff.json'): 'c26ac6f02ad4941fcc0254dfad19d7eabcb43ad1c9cbe30572902d8ec317c9f0',
    str(AUDIO): '3940d8ada7682141a12ba8d82ca28dcddc8eb76d4c3f9865dc4a00d988366011',
    str(QA): 'dda9dbca5b247a778f7bba369ca89fdaa4ea0fdf50eb6cb557e7bd0bb183cd31',
    str(RAW): 'a191633b228fc73eb20f7afc3d61f17e187563db35e6de38169938add6088307',
}
CODE_PINS = {
    'scripts/render_walkthrough.py': '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881',
    'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
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


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def normalized(value):
    return ' '.join(value.split()).casefold()


def safe_source_path(value):
    require(isinstance(value, str) and value and '\\' not in value, 'Use a portable source-relative path.')
    path = Path(value)
    require(not path.is_absolute() and not re.search(r'(?i)(?:://|www\.)', value), 'Require a local source-relative path.')
    require(not any(p in {'.', '..', 'private', '.git', 'node_modules'} or p.startswith('.env') for p in path.parts), 'Unsafe source path.')
    absolute = S / path
    require(absolute.resolve().is_relative_to(S.resolve()), 'Source path escapes source root.')
    require(not any(p.is_symlink() for p in [absolute, *absolute.parents] if p.is_relative_to(S)), 'Symlinked source is not permitted.')
    return absolute


def actual_timestamp(value, earliest=None):
    require(isinstance(value, str), 'Actual review requires a timezone-aware timestamp.')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None and result <= datetime.now(timezone.utc), 'Actual review cannot be naive or future dated.')
    if earliest is not None:
        require(result >= actual_timestamp(earliest), 'Review predates the actual input QA.')
    return result


def receipt(value, digest):
    require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), 'Supply the exact genuine receipt SHA256.')
    path = safe_source_path(value)
    require(path.is_file(), 'Actual review receipt is absent; assembly remains blocked.')
    require(sha(path) == digest, 'Actual review receipt hash differs.')
    record = read(path)
    require(isinstance(record, dict), 'Review receipt must be an object.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)', json.dumps(record)), 'Public review receipt must be URL free.')
    return record


def preflight():
    require(__debug__, 'Use ordinary Python; optimized execution is not accepted.')
    for relative, digest in PINS.items():
        require(sha(safe_source_path(relative)) == digest, 'Immutable source changed: ' + relative)
    for relative, digest in CODE_PINS.items():
        require(sha(ROOT / relative) == digest, 'Pinned renderer/validator changed; preserve this recipe and obtain a new review.')
    for asset in read(S / FREEZE / 'source-asset-pins.json')['assets']:
        path = safe_source_path(asset['file'])
        require(sha(path) == asset['sha256'] and path.stat().st_size == asset['bytes'], 'Original source image, DOM, code or fixture changed.')
    proposal = read(S / PROPOSAL / 'correspondence.proposed.json')
    lesson = read(S / LESSON)
    manifest = read(S / FREEZE / 'captures.reviewed.json')
    qa = read(S / QA)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, _normalized, _image_dimensions, instruction_scene_digest
    cues, raw = load_cues(S / CAPTIONS), load_cues(S / RAW)
    require(cues == raw and len(cues) == 127, 'Actual whole SRT cue text/endpoints differ.')
    require(sha(S / CAPTIONS) == proposal['provenance']['actual_exported_srt']['sha256'], 'Actual corrected SRT identity changed.')
    require(words(' '.join(c['text'] for c in cues)) == words(' '.join(s['narration'] for s in lesson['scenes'])), 'Full caption words differ from frozen narration.')
    require(qa['passed'] is True and qa['issues'] == [] and qa['possible_speech_gaps'] == [], 'Actual full audio QA has unresolved issues.')
    require(qa['lesson']['sha256'] == PINS[str(LESSON)] and qa['audio']['sha256'] == PINS[str(AUDIO)], 'Audio QA refers to different inputs.')
    require(qa['audio']['full_decode'] == 'passed' and qa['audio']['duration_seconds'] == 439.6930625, 'Complete actual PCM decode is absent or changed.')
    duration = qa['audio']['duration_seconds']
    require(abs(qa['audio']['decoded_samples'] / qa['audio']['sample_rate'] - duration) < 1e-6, 'Duration is not full measured PCM.')
    require(qa['alignment']['match_ratio'] == 1.0 and qa['alignment']['text_changes'] == [] and qa['alignment']['cues'] == 127, 'Exact full transcript QA differs.')
    require(qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0, 'Actual speech cues contain silence.')
    for key, actual, digest in [('raw_captions', raw, PINS[str(RAW)]), ('corrected_captions', cues, sha(S / CAPTIONS))]:
        require(qa[key]['sha256'] == digest and len(qa[key]['energy']) == 127, 'Actual per-cue audio QA is incomplete or different.')
        for index, (cue, measured) in enumerate(zip(actual, qa[key]['energy']), 1):
            require(measured['cue'] == index and measured['samples'] > 0 and measured['below_threshold'] is False and measured['rms'] >= qa['signal_threshold_rms'], 'Unmeasured or silent actual cue.')
            require(abs(cue['start'] - measured['start']) < 1e-9 and abs(cue['end'] - measured['end']) < 1e-9, 'Actual measured cue boundary changed.')
    require(qa['corrected_captions']['exact_script'] is True, 'Corrected captions lack exact frozen-script QA.')
    scope = proposal['bounded_recorded_scope']
    require(scope['proposed_group_additions'] == 2 and scope['proposed_people_additions'] == scope['proposed_unit_additions'] == scope['rows_imported'] == 0, 'Bounded two-group unapplied scope changed.')
    require(scope['import_applied'] is False and scope['confirmation_checkbox_checked'] is False and scope['second_factor_enrollment_or_confirmation_performed'] is False, 'This review lesson cannot claim import/MFA completion.')
    require(len(lesson['scenes']) == 13 and len(manifest['screenshots']) == len(proposal['source_spans']) == 18, 'Frozen source scope changed.')
    require(len(proposal['cues']) == 127 and proposal['unresolved_cross_image_cue_boundaries'] == [], 'Proposed actual cue coverage differs.')
    rows = {x['id']: x for x in manifest['screenshots']}
    observed = {}
    for ident, row in rows.items():
        require(sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256'], 'Actual source image or DOM changed.')
        require(_image_dimensions(S / row['file']) == (row['width'], row['height']) == (1434, 829), 'Actual source dimensions differ.')
        reviewed = row['capture_review']
        require(reviewed['passed'] is True and reviewed['sha256'] == row['sha256'], 'Retained actual source review does not bind this image.')
        require(all(reviewed[k] is True for k in ['application_visible', 'labels_legible', 'no_errors']), 'Retained actual source review has a gap.')
        require(actual_timestamp(reviewed['reviewed_at']) >= actual_timestamp(row['provenance']['captured_at']), 'Actual source review predates capture.')
        v = _Validator(S)
        observed[ident] = v.observations(row, ident)
        require(not v.issues, 'Invalid actual source control observations: ' + json.dumps(v.issues))
    entries = []
    for index, (actual, proposed) in enumerate(zip(cues, proposal['cues']), 1):
        require(proposed['raw_cue'] == index and all(proposed[k] == actual[k] for k in ['start', 'end', 'text']), 'Proposed cue differs from actual renderer SRT parsing.')
        require(proposed['capture_id'] in rows and proposed['source_sha256'] == rows[proposed['capture_id']]['sha256'], 'Proposed cue source differs.')
        references = {r['literal_visible_label']: r['exact_spoken_reference'] for r in proposed['proposed_literal_correspondences']}
        require(all(label in rows[proposed['capture_id']]['visible_labels'] and normalized(phrase) in normalized(actual['text']) for label, phrase in references.items()), 'A proposed instruction names an unseen control or absent spoken phrase.')
        entry = dict(actual, cue=index, screenshot_id=proposed['capture_id'], required_labels=list(references), spoken_references=references, instructional=bool(references))
        v = _Validator(S)
        v.spoken_references(entry, {_normalized(x) for x in entry['required_labels']}, 'actual proposed caption', True)
        require(not v.issues, 'Proposed instruction reference failed: ' + json.dumps(v.issues))
        entries.append(entry)
    scenes = []
    for authored in lesson['scenes']:
        spans = [x for x in proposal['source_spans'] if x['scene_id'] == authored['id']]
        caps = [c for c, p in zip(entries, proposal['cues']) if p['scene_id'] == authored['id']]
        screens = [{'screenshot_id': p['capture_id'], 'start': p['proposed_screen_start']['seconds'], 'end': p['proposed_screen_end']['seconds']} for p in spans]
        require(words(' '.join(c['text'] for c in caps)) == words(authored['narration']), 'Actual scene loses or changes frozen speech.')
        require(any(c['required_labels'] for c in caps), 'Operational scene has no actual spoken control reference.')
        require(all(s['end'] > s['start'] and (i == 0 or screens[i - 1]['end'] == s['start']) for i, s in enumerate(screens)), 'Actual source intervals do not cover the scene continuously.')
        for cap in caps:
            require(any(s['screenshot_id'] == cap['screenshot_id'] and s['start'] <= cap['start'] and s['end'] >= cap['end'] for s in screens), 'Actual whole caption crosses its source image.')
        full = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational', 'start': screens[0]['start'], 'end': screens[-1]['end'], 'visual_required_labels': authored['required_labels'], 'screens': screens, 'captions': caps}
        require({_normalized(x) for x in full['visual_required_labels']} <= set().union(*(observed[s['screenshot_id']] for s in screens)), 'Required visual controls are not present in this actual scene.')
        full['proposed_mapping_sha256'] = instruction_scene_digest(full, rows)
        scenes.append(full)
    require(scenes[0]['start'] == 0 and scenes[-1]['end'] == duration and all(a['end'] == b['start'] for a, b in zip(scenes, scenes[1:])), 'Actual visual coverage is not complete PCM duration.')
    metrics = read(S / PROPOSAL / 'caption-layout-measurements.json')
    require(metrics['summary']['cues_measured'] == 127 and metrics['summary']['all_caption_ink_within_footer'] is True and metrics['summary']['all_titles_fit'] is True, 'Pinned actual caption/title geometry has unresolved gaps.')
    return {'lesson': lesson, 'manifest': manifest, 'rows': rows, 'proposal': proposal, 'qa': qa, 'duration': duration, 'scenes': scenes, 'cues': cues}


def root_review(data, value, digest):
    record = receipt(value, digest)
    require(record.get('reviewer') in {'Root', 'Codex /root'}, 'Whole-map review requires the actual Root reviewer.')
    require(record.get('lesson_sha256') == PINS[str(LESSON)] and record.get('audio_sha256') == PINS[str(AUDIO)], 'Root reviewed another lesson or audio.')
    require(record.get('correspondence_sha256') == PINS[str(PROPOSAL / 'correspondence.proposed.json')] and record.get('compact_sha256') == PINS[str(PROPOSAL / 'cue-screen-correspondence.txt')], 'Root reviewed another complete proposed map.')
    require(record.get('complete_cue_correspondence_reviewed') is True and record.get('screen_holds_and_required_controls_reviewed') is True and record.get('semantic_reference_items_reviewed') is True, 'Actual whole-map, required-control or semantic-reference review is pending.')
    require(record.get('cues') == 127 and record.get('accepted_spans') == 18 and record.get('source_images') == 18, 'Root accepted an incomplete source/cue scope.')
    require(record.get('human_listening_claim') is False, 'Root map review cannot substitute for User hearing.')
    require(isinstance(record.get('review'), str) and len(record['review']) > 120, 'Retain the actual complete-map review account.')
    actual_timestamp(record.get('reviewed_at'), data['proposal']['created_at'])
    return record


def user_listening(data, value, digest):
    record = receipt(value, digest)
    require(record.get('reviewer') == 'User' and record.get('complete_natural_narration') is True, 'Actual User complete natural narration review is pending.')
    require(record.get('lesson_sha256') == PINS[str(LESSON)] and record.get('audio_sha256') == PINS[str(AUDIO)], 'User heard different source or audio.')
    evidence = record.get('evidence')
    require(isinstance(evidence, str) and re.search(r'(?i)\b(?:full|complete)\b', evidence) and re.search(r'(?i)\bnatural\b', evidence), 'Retain the actual complete listening question and natural response.')
    actual_timestamp(record.get('reviewed_at'), data['qa']['checked_at'])
    return record


def build(data, parent, parent_file, parent_sha, heard, heard_file, heard_sha):
    from verify_capture_evidence import instruction_scene_digest, _Validator, _normalized
    scenes = []
    for source in data['scenes']:
        full = deepcopy(source)
        full.pop('proposed_mapping_sha256')
        full['instruction_review'] = {
            'passed': True, 'reviewer': parent['reviewer'], 'reviewed_at': parent['reviewed_at'],
            'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(full, data['rows']),
            'parent_correspondence_review_file': parent_file, 'parent_correspondence_review_sha256': parent_sha,
            'method': 'Actual Root complete 127-cue/18-source review, including explicit semantic items, retained source pixel/DOM reviews, unchanged actual SRT and full PCM audio QA. No new original-pixel inspection, User hearing, encoded-frame review or browser playback is inferred from this map receipt.'}
        v = _Validator(S)
        v.instruction_review(full, data['rows'], {ident: {_normalized(x) for x in row['visible_labels']} for ident, row in data['rows'].items()}, 'actual reviewed scene', data['lesson']['app'])
        require(not v.issues, 'Actual Root instruction mapping failed: ' + json.dumps(v.issues))
        scenes.append({'id': full['id'], 'start': full['start'], 'end': full['end'], 'screens': full['screens'],
                       'captions': [{k: c[k] for k in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']} for c in full['captions']],
                       'instruction_review': full['instruction_review']})
    manifest_bytes = (S / FREEZE / 'captures.reviewed.json').read_bytes()
    caption_bytes = (S / CAPTIONS).read_bytes()
    plan = {'schema_version': 1, 'lesson_id': data['lesson']['id'], 'duration_seconds': data['duration'],
        'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': str(AUDIO), 'sha256': PINS[str(AUDIO)], 'kind': 'approved_natural_narration',
            'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': PINS[str(AUDIO)],
                'complete_natural_narration': True, 'evidence': heard['evidence'], 'qa_file': str(QA), 'qa_sha256': PINS[str(QA)],
                'listening_review_file': heard_file, 'listening_review_sha256': heard_sha}},
        'captions': {'file': str(FINAL / 'captions.actual.corrected.srt'), 'sha256': sha(S / CAPTIONS), 'kind': 'speech_timed_srt',
            'approval': {'reviewer': 'Codex actual unchanged export and pinned full PCM QA', 'reviewed_at': data['qa']['checked_at'],
                'sha256': sha(S / CAPTIONS), 'audio_sha256': PINS[str(AUDIO)], 'speech_timing_reviewed': True,
                'method': 'All127 complete exported cues retain actual explicit endpoints and exact frozen words. Pinned complete PCM QA measures every cue; no word cut, endpoint movement, caption stretch or estimated timing. Actual Root whole-map and separate genuine User listening receipts are required.'}},
        'capture_manifests': [{'file': str(FINAL / 'captures.reviewed.json'), 'sha256': hashlib.sha256(manifest_bytes).hexdigest()}],
        'screenshot_reviews': {ident: {k: row['capture_review'][k] for k in ['reviewer', 'reviewed_at', 'sha256', 'application_visible', 'labels_legible', 'no_errors']} for ident, row in data['rows'].items()},
        'scenes': scenes, 'parent_correspondence_review': {'file': parent_file, 'sha256': parent_sha},
        'bounded_recorded_scope': data['proposal']['bounded_recorded_scope'], 'publishable': False,
        'limitations': data['proposal']['source_limits'] + ['Actual every-hold/caption encoded-frame inspection and genuine browser beginning/middle/end playback remain required after separate rendering.']}
    return plan, manifest_bytes, caption_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    parser.add_argument('--correspondence-review-file')
    parser.add_argument('--correspondence-review-sha256')
    parser.add_argument('--listening-review-file')
    parser.add_argument('--listening-review-sha256')
    args = parser.parse_args(argv)
    data = preflight()
    if args.assemble:
        require(all([args.correspondence_review_file, args.correspondence_review_sha256, args.listening_review_file, args.listening_review_sha256]), 'Assembly requires both actual Root whole-map and actual User listening receipt files/hashes.')
    require(bool(args.correspondence_review_file) == bool(args.correspondence_review_sha256), 'Supply both Root review path and exact hash.')
    require(bool(args.listening_review_file) == bool(args.listening_review_sha256), 'Supply both User listening path and exact hash.')
    parent = root_review(data, args.correspondence_review_file, args.correspondence_review_sha256) if args.correspondence_review_file else None
    heard = user_listening(data, args.listening_review_file, args.listening_review_sha256) if args.listening_review_file else None
    if not args.assemble:
        print(json.dumps({'source_preflight': True, 'lesson': data['lesson']['id'], 'scenes': 13, 'holds': 18, 'cues': 127,
            'actual_audio_sha256': PINS[str(AUDIO)], 'decoded_duration_seconds': data['duration'],
            'actual_Root_whole_map_receipt_validated': parent is not None, 'actual_User_listening_receipt_validated': heard is not None,
            'final_inputs_written': False, 'rendered': False, 'canonical_site_or_target_changed': False}, indent=2))
        return
    destination = S / FINAL
    require(not destination.exists() and not destination.is_symlink(), 'New-only final inputs refuse existing outputs; preserve history.')
    plan, manifest, captions = build(data, parent, args.correspondence_review_file, args.correspondence_review_sha256, heard, args.listening_review_file, args.listening_review_sha256)
    assets = {'plan.json': encoded(plan), 'captures.reviewed.json': manifest, 'captions.actual.corrected.srt': captions}
    destination.mkdir(parents=True)
    for name, body in assets.items():
        with (destination / name).open('xb') as stream:
            stream.write(body)
    from render_walkthrough import validate_inputs
    from verify_capture_evidence import instruction_scene_digest
    checked = validate_inputs(S / LESSON, destination / 'plan.json', S)
    for scene in checked['scenes']:
        require(instruction_scene_digest(scene, data['rows']) == scene['instruction_review']['mapping_sha256'], 'Actual renderer expansion changes the reviewed instruction digest.')
    report = {'kind': 'New immutable actual-input package after genuine separate reviews', 'lesson_id': data['lesson']['id'],
        'recipe_sha256': sha(__file__), 'frozen_sha256': PINS[str(LESSON)], 'actual_audio_sha256': PINS[str(AUDIO)],
        'Root_correspondence_receipt_sha256': args.correspondence_review_sha256, 'User_listening_receipt_sha256': args.listening_review_sha256,
        'strict_renderer_inputs_passed': True, 'all_scene_renderer_digest_roundtrips_passed': True,
        'rendered': False, 'canonical_site_or_target_changed': False, 'outputs': [{'file': name, 'sha256': sha(destination / name)} for name in assets]}
    with (destination / 'provenance.json').open('xb') as stream:
        stream.write(encoded(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
