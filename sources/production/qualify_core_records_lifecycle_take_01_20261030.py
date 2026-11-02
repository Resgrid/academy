"""Guard Records lifecycle qualification behind genuine exact Root playback.

Default is read-only. This helper cannot supply missing browser observations or
review them for Root. --qualify requires the actual raw-proof and Root-review
hashes; it creates NEW evidence only and never changes a canonical lesson/site.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-records-training-entry'
T = S / 'expansion/rendered/core-records-training-entry-take-01'
SOURCE = S / 'expansion/plans/core-records-training-entry-capture-freeze-20261029/core-records-training-entry.narrated-source.json'
PLAN = S / 'expansion/plans/core-records-training-entry-take-01-final-inputs-20261030/plan.json'
LISTENING = S / 'expansion/audio/core-records-training-entry.listening-review.json'
MASTER = 'd9bde3b8a309a257258dd48e288b52f2252558ad2af8cf602b91c190f398c332'
PINS = {
    SOURCE: 'e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5',
    PLAN: 'c2f13e7bc96f4e4d90d0c607c162444581d8ccea27174422dcd4e64d389ffa8e',
    LISTENING: 'a7e3f587d0307ccf126a43ce100ad31003310faae1b28c69b59d9f4d5a6d8f10',
    T / (NAME + '.mp4'): MASTER,
    T / 'evidence.frames-reviewed.json': 'e28f62efdaca50bed9390c8b4472a0831031dc3bab9853e99efb8ad2c652ddca',
    T / 'frame-source-comparison.json': '93733989b17fb057b4bee40f6352a2fe56202977bc928831154fcb1491e7319f',
    T / 'cue-frame-check.json': '6f53f6552ac12c3647cc5f7511c1cd2238ace76ca342b9ca8a908300a042cd95',
    T / 'encoded-audio.qa.json': '27bc6e320208c0e3c1c9ee71d3ff987e61aec4c5f3a805863e8efd5534b8697c',
    ROOT / 'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
    ROOT / 'scripts/expansion_site.py': 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8',
}


def require(value, message):
    if not value: raise ValueError(message)


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d): return (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode()


def safe_relative(value, base):
    p = Path(value)
    require(not p.is_absolute() and all(x not in {'.', '..', 'private', '.git', 'node_modules'} and not x.startswith('.env') for x in p.parts), 'Unsafe proof/review path.')
    result = base / p
    require(result.resolve().is_relative_to(base.resolve()), 'Proof/review path escaped root.')
    require(not result.is_symlink(), 'Symlink proof/review is not allowed.')
    return result


def prepare(args):
    require(__debug__, 'Use ordinary Python; optimized execution disables retained guards.')
    for p, digest in PINS.items(): require(sha(p) == digest, 'Changed exact qualified input: ' + str(p))
    for argument in [args.proof_observations_sha256, args.root_review_sha256]:
        require(isinstance(argument, str) and len(argument) == 64 and all(c in '0123456789abcdef' for c in argument), 'Supply both genuine exact receipt SHA256 values.')
    raw = safe_relative(args.proof_observations_file, ROOT)
    review_file = safe_relative(args.root_review_file, ROOT)
    require(sha(raw) == args.proof_observations_sha256 and sha(review_file) == args.root_review_sha256, 'Actual Root proof/review receipt is absent or changed.')
    root_review = json.loads(review_file.read_text())
    require(root_review.get('reviewer') == 'Root' and root_review.get('video_sha256') == MASTER, 'Require genuine Root review of this exact master.')
    require(root_review.get('raw_observation_sha256') == args.proof_observations_sha256 and root_review.get('actual_images_viewed') == 3 and root_review.get('beginning_middle_end_advancing_without_errors') is True, 'Root must personally review all three actual advancing/error-free browser observations.')
    rows = deepcopy(json.loads(raw.read_text()))
    require(isinstance(rows, list) and len(rows) == 3 and [r.get('position') for r in rows] == ['beginning', 'middle', 'end'], 'Require exactly three genuine beginning/middle/end observations in order.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions, verify_document
    for r in rows:
        require(r.get('video_sha256') == MASTER, 'Playback proof references different master.')
        require(r.get('current_time', 0) > r.get('previous_time', 0), 'Actual browser playback did not advance.')
        require(r.get('paused') is False and r.get('ended') is False and r.get('ready_state') == 4 and r.get('network_state') == 1, 'Actual browser player was not playing/ready.')
        require(r.get('media_error', 'missing') is None and r.get('console_errors') == [], 'Playback has unresolved errors.')
        require((r.get('video_width'), r.get('video_height')) == (1920, 1080), 'Wrong rendered media dimensions.')
        screenshot = safe_relative(r['screenshot']['file'], S)
        require(sha(screenshot) == r['screenshot']['sha256'], 'Genuine playback screenshot changed.')
        width, height = _image_dimensions(screenshot)
        r['screenshot'].update(width=width, height=height)
    require(root_review.get('screenshot_sha256s') == [r['screenshot']['sha256'] for r in rows], 'Root personal review does not bind exact three images.')
    source = json.loads(SOURCE.read_text())
    heard = json.loads(LISTENING.read_text())
    plan = json.loads(PLAN.read_text())
    require(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True and heard.get('lesson_sha256') == PINS[SOURCE] and heard.get('audio_sha256') == plan['narration']['sha256'], 'Genuine complete User hearing does not match.')
    for name, count, key in [('frame-source-comparison.json', 20, 'intervals_checked'), ('cue-frame-check.json', 112, 'cues_checked')]:
        d = json.loads((T / name).read_text())
        require(d['passed'] is True and d[key] == count and d['video_sha256'] == MASTER, 'Incomplete actual source/caption numerical check.')
    audio = json.loads((T / 'encoded-audio.qa.json').read_text())
    require(audio['passed'] is True and audio['audio']['sha256'] == MASTER and audio['audio']['full_decode'] == 'passed' and audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0 and not audio['issues'], 'Encoded audio QA failed.')
    evidence = json.loads((T / 'evidence.frames-reviewed.json').read_text())
    require(not evidence['browser_playback'] and len(evidence['screenshots']) == 16 and len(evidence['scenes']) == 12 and len(evidence['rendered_segments']) == 20, 'Frames-only evidence scope/history changed.')
    from expansion_site import lesson_content_digest
    evidence['authoring_sha256'] = lesson_content_digest(source)
    evidence['browser_playback'] = rows
    evidence['qualification_review'] = {'frame_review_complete': True, 'browser_playback_pending': False,
        'root_raw_observation_sha256': args.proof_observations_sha256, 'root_actual_playback_review_sha256': args.root_review_sha256,
        'review': 'Source agent personally inspected all20 actual encoded interval frames and112 actual caption regions; complete encoded audio/script/energy checks passed. Root separately personally inspected the three exact advancing, error-free browser observations. Actual User full hearing receipt is independently bound. No source-agent browser or audio listening claim.',
        'canonical_or_ready_changed': False}
    report = verify_document(evidence, S)
    require(report['passed'] and report['issues'] == [], 'Strict evidence failed: ' + json.dumps(report))
    return rows, evidence, report, source


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qualify', action='store_true')
    p.add_argument('--proof-observations-file', required=True)
    p.add_argument('--proof-observations-sha256', required=True)
    p.add_argument('--root-review-file', required=True)
    p.add_argument('--root-review-sha256', required=True)
    args = p.parse_args()
    rows, evidence, report, source = prepare(args)
    targets = [T / 'playback/proofs.json', T / 'evidence.reviewed.json', T / 'qualification.json']
    if args.qualify:
        require(all(not p.exists() and not p.is_symlink() for p in targets), 'New-only qualification preserves earlier results.')
        targets[0].parent.mkdir(parents=True, exist_ok=True)
        for path, document in zip(targets[:2], [rows, evidence]):
            body = encoded(document)
            with path.open('xb') as f: f.write(body)
        from expansion_site import _prepare
        candidate = dict(source, export_ready=True, publication_mode='video', evidence_file=targets[1].relative_to(S).as_posix())
        _prepare(candidate, S)
        qualification = {'passed': True, 'lesson_id': NAME, 'issues': [], 'public_export_preflight': 'passed',
            'video_sha256': MASTER, 'frozen_source_sha256': PINS[SOURCE], 'authoring_sha256': evidence['authoring_sha256'],
            'evidence_sha256': sha(targets[1]), 'proofs_sha256': sha(targets[0]),
            'actual_User_full_listening_sha256': PINS[LISTENING], 'actual_Root_playback_review_sha256': args.root_review_sha256,
            'actual_Root_raw_browser_observations_sha256': args.proof_observations_sha256,
            'actual_encoded_intervals_reviewed': 20, 'continuous_image_holds': 17, 'actual_caption_regions_reviewed': 112,
            'root_canonical_adoption_pending': True, 'canonical_site_target_or_Git_changed': False}
        with targets[2].open('xb') as f: f.write(encoded(qualification))
    print(json.dumps({'strict_evidence_candidate_passed': True, 'qualification_written': args.qualify,
        'video_sha256': MASTER, 'root_canonical_adoption_pending': True}))


if __name__ == '__main__': main()
