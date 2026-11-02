"""Prepare/check Records' audio-bound authoring recipe; no final assembly.

Default reads only. --write-recipe creates a NEW source-only recipe/schema
package. --check-approved-inputs requires exact genuine receipt hashes and checks
them without making any plan, narration, media, readiness or publication writes.
"""
import argparse
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
OLD = Path('expansion/plans') / (NAME + '-take-01-proposed-20261029')
OUT = Path('expansion/plans') / (NAME + '-authoring-recipe-20261030')
HELPER = Path('production/propose_dispatch_records_actual_cues_20261029.py')
LISTENING = Path('expansion/audio') / (NAME + '.listening-review.json')
PARENT = OLD / 'parent-proposed-correspondence-review.json'
SOURCE_SHA = 'e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5'
AUDIO_SHA = 'f7f1235fb74e25a008a7c53d34c6309e67feb31f42cdeab46c314d7860babdc6'
PROPOSAL_SHA = '75e76faaaae9da34210fc99b507721f750829477c4e842fa0c393a26614e6637'
COMPACT_SHA = '5332aa4b69cdd7e6bcd03dc0a6429815fca8b4d6c44fce83947f02ec774827b9'
PINS = {
    HELPER: '2f8bb4f7156689b58ad4693a50bbc53f504981ffdab7604265c64fafddbb645c',
    OLD / 'correspondence.proposed.json': PROPOSAL_SHA,
    OLD / 'cue-screen-map.compact.txt': COMPACT_SHA,
    OLD / 'preflight.json': '50a2a59b86d73bfe86dedc1ebd8ef8d2401112e8642d6a5c5c1ad76a9b7cfbfc',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def validate_receipt(record, kind, earliest, now=None):
    require(isinstance(record, dict), 'A genuine review receipt must be an object.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)', json.dumps(record)), 'Receipts must be URL-free.')
    require(record.get('lesson_sha256') == SOURCE_SHA and record.get('audio_sha256') == AUDIO_SHA, 'Review binds different source/audio bytes.')
    try:
        observed = datetime.fromisoformat(record['reviewed_at'].replace('Z', '+00:00'))
        minimum = datetime.fromisoformat(earliest.replace('Z', '+00:00'))
    except (KeyError, AttributeError, ValueError) as error:
        raise ValueError('Require the actual timezone-aware review time.') from error
    require(observed.tzinfo is not None and minimum.tzinfo is not None and minimum <= observed <= (now or datetime.now(timezone.utc)), 'Review chronology precedes QA or is future/naive.')
    if kind == 'listening':
        require(record.get('reviewer') == 'User' and record.get('complete_natural_narration') is True, 'Actual User full natural/complete listening approval is missing.')
        evidence = record.get('evidence', '')
        require(isinstance(evidence, str) and re.search(r'(?i)\b(?:full|complete)\b', evidence) and re.search(r'(?i)\bnatural\b', evidence), 'Retain the actual full-listening request and natural/complete User response.')
    elif kind == 'parent':
        require(record.get('reviewer') == 'Codex /root', 'Require the named parent correspondence reviewer.')
        require(record.get('correspondence_sha256') == PROPOSAL_SHA and record.get('compact_sha256') == COMPACT_SHA, 'Parent reviewed a different cue/screen map.')
        require(record.get('complete_cue_correspondence_reviewed') is True and record.get('screen_holds_and_required_controls_reviewed') is True, 'Complete source/cue review is pending.')
        require((record.get('cues'), record.get('accepted_spans'), record.get('continuous_holds'), record.get('source_images')) == (112, 20, 17, 16), 'Parent review scope differs.')
    else:
        raise ValueError('Unknown review kind.')
    return record


def checked_receipt(path, expected, kind, earliest):
    require(isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected), 'Supply the exact independently reviewed receipt SHA256.')
    require((S / path).is_file(), 'Actual ' + kind + ' receipt has not arrived.')
    require(sha(S / path) == expected, 'Receipt changed or its supplied hash is wrong.')
    return validate_receipt(json.loads((S / path).read_text()), kind, earliest)


def prepare():
    require(__debug__, 'Use ordinary Python so retained helper guards remain enabled.')
    for path, digest in PINS.items():
        require(sha(S / path) == digest, 'Changed authoring prerequisite: ' + str(path))
    spec = importlib.util.spec_from_file_location('retained_records_actual_proposal', S / HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    config = next(row for row in helper.CONFIGS if row['id'] == NAME)
    proposal, rebuilt = helper.prepare(config)
    require(sha(S / OLD / 'correspondence.proposed.json') == hashlib.sha256(rebuilt['correspondence.proposed.json']).hexdigest(), 'Proposal no longer reproduces.')
    require(not proposal['unresolved_boundaries'], 'Unresolved source/cue timing cannot enter authoring.')
    require(len(proposal['whole_cue_continuous_holds_proposed']) == 17, 'Wrong continuous screen hold count.')
    qa_path = Path('expansion/audio') / (NAME + '.actual.qa.json')
    qa = json.loads((S / qa_path).read_text())
    require(qa['audio']['full_decode'] == 'passed' and qa['possible_speech_gaps'] == [], 'Full audio QA is incomplete.')
    require(qa['alignment']['match_ratio'] == 1.0 and qa['alignment']['text_changes'] == [], 'Speech transcript identity changed.')
    require(abs(qa['audio']['decoded_samples'] / qa['audio']['sample_rate'] - proposal['decoded_audio_seconds']) < 1e-6, 'Final hold is not bound to actual PCM duration.')
    common = {'lesson_sha256': {'const': SOURCE_SHA}, 'audio_sha256': {'const': AUDIO_SHA}, 'reviewed_at': {'type': 'string', 'format': 'date-time'}}
    listening_schema = {'type': 'object', 'title': 'Actual User complete Records narration listening receipt',
        'required': ['reviewer', 'reviewed_at', 'lesson_sha256', 'audio_sha256', 'complete_natural_narration', 'evidence'],
        'properties': {**common, 'reviewer': {'const': 'User'}, 'complete_natural_narration': {'const': True},
                       'evidence': {'type': 'string'}, 'question_call_id': {'type': 'string'}},
        'description': 'No approval example is generated. Runtime additionally checks exact supplied SHA, URL-free content, actual full natural/complete response and chronology after actual QA.'}
    parent_schema = {'type': 'object', 'title': 'Parent complete Records cue/source review receipt',
        'required': ['reviewer', 'reviewed_at', 'lesson_sha256', 'audio_sha256', 'correspondence_sha256', 'compact_sha256', 'complete_cue_correspondence_reviewed', 'screen_holds_and_required_controls_reviewed', 'cues', 'accepted_spans', 'continuous_holds', 'source_images'],
        'properties': {**common, 'reviewer': {'const': 'Codex /root'}, 'correspondence_sha256': {'const': PROPOSAL_SHA},
            'compact_sha256': {'const': COMPACT_SHA}, 'complete_cue_correspondence_reviewed': {'const': True},
            'screen_holds_and_required_controls_reviewed': {'const': True}, 'cues': {'const': 112},
            'accepted_spans': {'const': 20}, 'continuous_holds': {'const': 17}, 'source_images': {'const': 16}},
        'description': 'Reviews the whole exact112cue/screen map, not merely a representative frame. Retained source reviews can be cited honestly; no new original-size inspection is required or inferred.'}
    recipe = {'kind': 'GUARDED_SOURCE_ONLY_Records_authoring_input_recipe', 'lesson_id': NAME,
        'input_pins': {**{str(path): digest for path, digest in PINS.items()}, **config},
        'source_file': ('expansion/plans/' + config['folder'] + '/' + NAME + '.narrated-source.json'),
        'actual_audio_qa_file': qa_path.as_posix(), 'actual_audio_qa_sha256': config['qa_sha256'],
        'decoded_duration_seconds': proposal['decoded_audio_seconds'], 'raw_and_corrected_cues': 112,
        'scenes': 12, 'accepted_exact_source_spans': 20, 'continuous_holds': 17, 'source_images': 16,
        'caption_splits': 0, 'timing_interpolation': False,
        'listening_receipt_expected_path': LISTENING.as_posix(), 'parent_timing_receipt_expected_path': PARENT.as_posix(),
        'actual_User_listening_required': True, 'parent_complete_timing_review_required': True,
        'final_renderer_plan_created': False, 'review_or_listening_receipt_created': False,
        'assembly_supported_by_this_preparation_tool': False,
        'ordered_whole_cue_holds': proposal['whole_cue_continuous_holds_proposed'],
        'limits': ['This prepares exact guarded authoring inputs and required review schemas; it does not author final renderer inputs or consume a nonexistent approval.',
                   'After both genuine reviews, a separately authorized final authoring step must map per-cue literal controls/natural references and bind instruction_scene_digest without weakening source/frame/playback gates.',
                   'No actual source pixels, frozen script, recorded app actions, audio, raw/corrected captions or existing proposal are changed.']}
    assets = {'authoring-recipe.json': encoded(recipe), 'listening-review.schema.json': encoded(listening_schema),
              'parent-timing-review.schema.json': encoded(parent_schema),
              'cue-screen-map.compact.txt': (S / OLD / 'cue-screen-map.compact.txt').read_bytes()}
    return recipe, qa, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write-recipe', action='store_true')
    mode.add_argument('--check-approved-inputs', action='store_true')
    parser.add_argument('--listening-review-sha256')
    parser.add_argument('--parent-timing-review-sha256')
    args = parser.parse_args()
    recipe, qa, assets = prepare()
    if args.check_approved_inputs:
        checked_receipt(LISTENING, args.listening_review_sha256, 'listening', qa['checked_at'])
        checked_receipt(PARENT, args.parent_timing_review_sha256, 'parent', qa['checked_at'])
    if args.write_recipe:
        destination = S / OUT
        require(not destination.exists(), 'New-only recipe output; preserve every previous package.')
        spec = importlib.util.spec_from_file_location('records_recipe_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        require(not findings, 'Privacy findings: ' + repr(findings))
        assets['preflight.json'] = encoded({'source_only': True, 'helper_sha256': sha(__file__),
            'ordinary_privacy_findings': [], 'actual_approvals_inferred': False,
            'outputs': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            with (destination / name).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'preflight_passed': True, 'files_written': args.write_recipe,
        'approval_checks_requested': args.check_approved_inputs, 'actual_approvals_inferred': False,
        'output': str(S / OUT), 'recipe_sha256': hashlib.sha256(assets['authoring-recipe.json']).hexdigest(),
        'expected_listening_receipt': LISTENING.as_posix(), 'expected_parent_timing_receipt': PARENT.as_posix(),
        'source_sha256': SOURCE_SHA, 'audio_sha256': AUDIO_SHA,
        'final_plan_or_assembly_or_render_created': False}, indent=2))


if __name__ == '__main__':
    main()
