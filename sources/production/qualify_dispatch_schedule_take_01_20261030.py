"""Qualify the actual Dispatch scheduled-call take only after genuine browser review.

Default is read-only source/frame preflight. Actual proof checking additionally
requires exact raw-proof and Root full-proof-review receipt hashes. --qualify
creates NEW evidence/proofs/qualification/candidate files in the selected take.
It never creates a hearing/playback receipt, adopts canonical content or changes
the site, target, apps, media, source narration or Git state.
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
CONFIG = S / 'production/dispatch_schedule_take_01_qualification_pins_20261030.json'
CONFIG_SHA = 'e0b8f6918467b1b99eabff04ea3253dc894700ccd8abb99d58865afeb86847cf'


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


def contained(relative, root=S):
    require(isinstance(relative, str) and relative and '\\' not in relative and not relative.startswith('/')
            and all(p not in ('', '.', '..', 'private', '.git', 'node_modules') and not p.startswith('.env')
                    for p in relative.split('/')), 'Unsafe proof/source path.')
    path = root / relative
    require(path.resolve().is_relative_to(root.resolve()), 'Proof/source path escaped its root.')
    require(not any(p.is_symlink() for p in [path, *path.parents] if p == root or p.is_relative_to(root)), 'Symlink proof/source rejected.')
    require(path.is_file(), 'Actual proof/source file is missing: ' + relative)
    return path


def exact_file(relative, digest, root=ROOT):
    require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), 'Supply exact genuine proof/receipt SHA256.')
    path = contained(relative, root)
    require(sha(path) == digest, 'Actual proof/receipt changed or has not been reviewed.')
    return path


def date(value):
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc), 'Proof review date must be real, aware and nonfuture.')
    return stamp


def preflight(alias):
    require(__debug__, 'Use ordinary Python; retained strict validators contain assertions.')
    require(sha(CONFIG) == CONFIG_SHA, 'Qualification config changed.')
    catalog = json.loads(CONFIG.read_text())
    cfg = catalog['lessons'][alias]
    for relative, digest in cfg['pins'].items():
        require(sha(contained(relative)) == digest, 'Changed qualification input: ' + relative)
    for relative, digest in catalog['code_pins'].items():
        require(sha(contained(relative, ROOT)) == digest, 'Changed public evidence/export gate.')
    sealer = catalog['sealer']
    require(sha(contained(sealer['file'])) == sealer['sha256'], 'Actual frame sealer changed.')
    spec = importlib.util.spec_from_file_location('actual_app_reference_frame_sealer', S / sealer['file'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    take, evidence, audit = module.prepare(alias)
    require((S / take / 'evidence.frames-reviewed.json').read_bytes() == encoded(evidence),
            'Sealed actual frame evidence no longer reproduces.')
    require((S / take / 'render-and-frame-review-20261030.json').read_bytes() == encoded(audit), 'Actual frame audit changed.')
    source = json.loads(contained(cfg['source']).read_text())
    original = json.loads(contained(cfg['original_heard_source']).read_text())
    require([x['narration'] for x in source['scenes']] == [x['narration'] for x in original['scenes']],
            'Learner metadata projection changed the actual heard narration.')
    heard_path = 'expansion/audio/' + cfg['id'] + '.listening-review.json'
    heard = json.loads(contained(heard_path).read_text())
    original_qa = json.loads(contained('expansion/audio/' + cfg['id'] + '.actual.qa.json').read_text())
    require(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True,
            'Genuine complete natural narration approval is missing.')
    require(heard.get('lesson_sha256') == cfg['pins'][cfg['original_heard_source']]
            and heard.get('audio_sha256') == original_qa['audio']['sha256'], 'User heard a different source/audio.')
    require(date(heard['reviewed_at']) >= date(original_qa['checked_at']), 'Actual hearing predates full-audio QA.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)', json.dumps(heard)),
            'Hearing receipt is not public-safe.')
    require(len(evidence['screenshots']) == cfg['sources'] and len(evidence['rendered_segments']) == cfg['holds']
            and sum(len(x['captions']) for x in evidence['scenes']) == cfg['cues'], 'Actual review scope differs.')
    timed_pin = cfg['Root_timed_map_and_metadata_receipt']
    timed = json.loads(exact_file(timed_pin['file'], timed_pin['sha256'], S).read_text())
    require(timed.get('reviewer') in {'Root', 'Codex /root'} and timed.get('learner_projection_sha256') == cfg['pins'][cfg['source']], 'Actual Root learner-metadata review identifies another source.')
    require(timed.get('lesson_sha256') == cfg['pins'][cfg['original_heard_source']] and timed.get('audio_sha256') == heard.get('audio_sha256'), 'Root timed-map review identifies another heard script/audio.')
    require(all(timed.get(key) is True for key in ('complete_cue_correspondence_reviewed', 'screen_holds_and_required_controls_reviewed', 'semantic_reference_items_reviewed', 'learner_practice_prompts_reviewed', 'learner_sector_examples_reviewed')), 'Actual whole-map or learner practice/scenario review is missing.')
    require(timed.get('cues') == 71 and timed.get('accepted_spans') == 13 and timed.get('source_images') == 9 and timed.get('human_listening_claim') is False, 'Root map review scope or hearing separation changed.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from expansion_site import lesson_content_digest
    return cfg, take, evidence, source, lesson_content_digest(source)


def validate_root_review(review, rows, raw_sha, master):
    require(isinstance(review, dict) and review.get('reviewer') == 'Root', 'Genuine Root actual browser review is required.')
    require(review.get('raw_observations_sha256') == raw_sha and review.get('video_sha256') == master,
            'Root reviewed a different raw proof or encoded master.')
    require(review.get('positions_personally_reviewed') == ['beginning', 'middle', 'end'], 'Root must review all three actual playback positions.')
    require(review.get('screenshot_sha256_in_order') == [row['screenshot']['sha256'] for row in rows],
            'Root review screenshot identities differ.')
    for key in ('actual_playback_observed', 'actual_screenshots_personally_viewed', 'application_visible',
                'advancing_error_free_playback', 'active_caption_text_checked'):
        require(review.get(key) is True, 'Incomplete genuine Root browser review: ' + key)
    require(review.get('human_listening_claim') is False, 'Browser review cannot replace actual User hearing.')
    stamp = date(review['reviewed_at'])
    require(all(stamp >= date(row['captured_at']) for row in rows), 'Root review predates actual playback.')
    require(isinstance(review.get('notes'), str) and len(review['notes'].strip()) > 40, 'Retain actual Root playback observations.')


def prepare(alias, raw_file, raw_sha, review_file, review_sha):
    cfg, take, evidence, source, authoring = preflight(alias)
    raw_path = exact_file(raw_file, raw_sha)
    review_path = exact_file(review_file, review_sha)
    rows = json.loads(raw_path.read_text())
    require(isinstance(rows, list) and len(rows) == 3 and [r.get('position') for r in rows] == ['beginning', 'middle', 'end'],
            'Exactly three actual ordered beginning/middle/end observations are required.')
    master = evidence['video']['sha256']
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import verify_document, _image_dimensions
    # A receipt never supplies dimensions or fixes browser state. Require the
    # actual rows and screenshots to have already retained the right values.
    for row in rows:
        require(row.get('video_sha256') == master and row.get('current_time', -1) > row.get('previous_time', -1) >= 0,
                'Stale or nonadvancing actual playback.')
        image_path = contained(row['screenshot']['file'])
        require(sha(image_path) == row['screenshot']['sha256'], 'Actual playback screenshot changed.')
        width, height = _image_dimensions(image_path)
        require((width, height) == (row['screenshot'].get('width'), row['screenshot'].get('height'))
                and width >= 960 and height >= 540, 'Retain actual sufficient playback screenshot dimensions.')
    review = json.loads(review_path.read_text())
    validate_root_review(review, rows, raw_sha, master)
    evidence = deepcopy(evidence)
    require(evidence['browser_playback'] == [], 'Frames-only history was overwritten.')
    evidence['browser_playback'] = deepcopy(rows)
    evidence['authoring_sha256'] = authoring
    evidence['qualification_review'] = {'frame_review_complete': True, 'browser_playback_pending': False,
        'parent_raw_observations_file': raw_file, 'parent_raw_observations_sha256': raw_sha,
        'actual_Root_browser_review_file': review_file, 'actual_Root_browser_review_sha256': review_sha,
        'review': 'The genuine hash-bound Root receipt identifies all three actual advancing/error-free browser screenshots and captions. Separate actual full-frame/caption source-agent review and complete encoded decode/PCM checks are retained. User hearing remains bound to the unchanged original scheduled-call speech source; genuine Root timed-map receipt separately binds the learner practice/scenario metadata. No browser review is inferred by this helper.',
        'canonical_or_ready_changed': False}
    report = verify_document(evidence, S)
    require(report['passed'] is True and report['issues'] == [], 'Strict capture/playback gate failed: ' + json.dumps(report))
    candidate = dict(source, export_ready=True, publication_mode='video',
                     evidence_file=(take / 'evidence.reviewed.json').as_posix())
    return cfg, take, rows, evidence, candidate, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=('schedule',), default='schedule')
    parser.add_argument('--qualify', action='store_true')
    parser.add_argument('--proof-observations-file')
    parser.add_argument('--proof-observations-sha256')
    parser.add_argument('--root-proof-review-file')
    parser.add_argument('--root-proof-review-sha256')
    args = parser.parse_args(argv)
    values = [args.proof_observations_file, args.proof_observations_sha256,
              args.root_proof_review_file, args.root_proof_review_sha256]
    if not any(values):
        require(not args.qualify, 'Actual proof and review paths/hashes are required for qualification.')
        cfg, _, _, _, _ = preflight(args.lesson)
        print(json.dumps({'read_only_source_frame_preflight_passed': True, 'holds': cfg['holds'], 'cues': cfg['cues'],
                          'actual_browser_playback_and_Root_receipt_required': True, 'qualified': False}))
        return
    require(all(values), 'Supply all exact actual proof/review paths and hashes.')
    cfg, take, rows, evidence, candidate, report = prepare(args.lesson, *values)
    targets = {take / 'playback/proofs.json': encoded(rows), take / 'evidence.reviewed.json': encoded(evidence),
               take / 'canonical-candidate.review-required.json': encoded(candidate)}
    qualification_path = S / take / 'qualification.json'
    if args.qualify:
        require(all(not (S / path).exists() and not (S / path).is_symlink() for path in targets)
                and not qualification_path.exists() and not qualification_path.is_symlink(), 'New-only qualification refuses prior output.')
        for path, body in targets.items():
            require((S / path).parent.resolve().is_relative_to(S.resolve())
                    and not (S / path).parent.is_symlink(), 'Qualification output escaped source package.')
            (S / path).parent.mkdir(parents=True, exist_ok=True)
            with (S / path).open('xb') as stream:
                stream.write(body)
        from expansion_site import _prepare
        _prepare(candidate, S)
        qualified = {'passed': True, 'lesson_id': cfg['id'], 'issues': [], 'public_export_preflight': 'passed',
            'video_sha256': evidence['video']['sha256'], 'authoring_sha256': evidence['authoring_sha256'],
            'evidence_sha256': sha(S / take / 'evidence.reviewed.json'), 'proofs_sha256': sha(S / take / 'playback/proofs.json'),
            'canonical_candidate_sha256': sha(S / take / 'canonical-candidate.review-required.json'),
            'parent_actual_raw_observations_sha256': args.proof_observations_sha256,
            'actual_Root_browser_review_sha256': args.root_proof_review_sha256,
            'actual_User_listening_receipt_sha256': cfg['pins']['expansion/audio/' + cfg['id'] + '.listening-review.json'],
            'actual_Root_timed_map_and_metadata_receipt_sha256': cfg['Root_timed_map_and_metadata_receipt']['sha256'],
            'learner_projection_sha256': cfg['pins'][cfg['source']],
            'rendered_intervals': cfg['holds'], 'caption_regions_reviewed': cfg['cues'], 'source_images': cfg['sources'],
            'root_canonical_adoption_pending': True, 'canonical_site_target_or_Git_changed': False}
        with qualification_path.open('xb') as stream:
            stream.write(encoded(qualified))
    print(json.dumps({'strict_evidence_candidate_passed': report['passed'], 'qualified_outputs_written': args.qualify,
                      'predicted_evidence_sha256': hashlib.sha256(encoded(evidence)).hexdigest(),
                      'canonical_or_site_changed': False}))


if __name__ == '__main__':
    main()
