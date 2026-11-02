"""Guard native Unit call lifecycle qualification behind genuine exact Root playback.

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
NAME = 'app-unit-call-lifecycle-native'
T = S / 'expansion/rendered/app-unit-call-lifecycle-native-take-01'
SOURCE = S / 'expansion/plans/app-unit-call-lifecycle-native-take-01-adoption-proposal-20261030/lesson.adoption-candidate.json'
PLAN = S / 'expansion/plans/app-unit-call-lifecycle-native-take-01-final-inputs-20261030/plan.json'
LISTENING = S / 'expansion/audio/app-unit-call-lifecycle-native.listening-review.json'
MASTER = 'd4fcf9c6d7a974b71757d1510508d4666beaef180b16b0bf642cebe3a93c9b78'
PINS = {
    SOURCE: 'b2f2ce403fa9e1b0040b4a9140e5ef4d325159f2dd872bbaaf0f490041f44e31',
    PLAN: '26c931bcba9dfa9ebfdfb9765969079b5fcc3275516eb63ec0459c33f92ca4c4',
    LISTENING: '3bcd147443de70481cdb6ef9853476c6b563f2d2476316b6b47e13b20483f6a1',
    T / (NAME + '.mp4'): 'd4fcf9c6d7a974b71757d1510508d4666beaef180b16b0bf642cebe3a93c9b78',
    T / 'evidence.frames-reviewed.pending-playback.json': '623ca385a716128833b259fe2cf6b26203ba1e9e072df5087bb4e00f9de435da',
    T / 'frame-source-comparison.json': 'e0337b3f6a87c04302bc9bfa743f4cff9bb0a00388ddaae9cd6c84ef1140ce3a',
    T / 'cue-frame-check.json': '930a4cd5c68fa30cb33122127858a56388fd9ad51001e4a66803b64ca3d18ac9',
    T / 'encoded-audio.qa.json': 'ef816dc2387d065b50faf886aac038a2a0030a029694cddb36c70eddaed1c848',
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
    require(root_review.get('learner_projection_sha256') == PINS[SOURCE] and root_review.get('new_practice_prompts_and_six_sector_examples_reviewed') is True, 'Root must genuinely review the new15 practice prompts and six distinct sector scenarios before qualification.')
    rows = deepcopy(json.loads(raw.read_text()))
    require(isinstance(rows, list) and len(rows) == 3 and [r.get('position') for r in rows] == ['beginning', 'middle', 'end'], 'Require exactly three genuine beginning/middle/end observations in order.')
    require(root_review.get('screenshot_sha256s') == [row.get('screenshot', {}).get('sha256') for row in rows], 'Root screenshot review identifies a different image set.')
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
        require((r['screenshot'].get('width'), r['screenshot'].get('height')) == (width, height), 'Retain actual playback screenshot dimensions; do not normalize incorrect metadata.')
    require(root_review.get('screenshot_sha256s') == [r['screenshot']['sha256'] for r in rows], 'Root personal review does not bind exact three images.')
    source = json.loads(SOURCE.read_text())
    heard = json.loads(LISTENING.read_text())
    plan = json.loads(PLAN.read_text())
    require(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True and heard.get('lesson_sha256') == 'a98a596197aa748981d9ed30b65f3a76e2bf64166ffa697e1eb8b134f97d759c' and heard.get('audio_sha256') == plan['narration']['sha256'], 'Genuine complete User hearing does not match.')
    for name, count, key in [('frame-source-comparison.json', 23, 'intervals_checked'), ('cue-frame-check.json', 88, 'cues_checked')]:
        d = json.loads((T / name).read_text())
        require(d['passed'] is True and d[key] == count and d['video_sha256'] == MASTER, 'Incomplete actual source/caption numerical check.')
    audio = json.loads((T / 'encoded-audio.qa.json').read_text())
    require(audio['passed'] is True and audio['audio']['sha256'] == MASTER and audio['audio']['full_decode'] == 'passed' and audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0 and not audio['issues'], 'Encoded audio QA failed.')
    evidence = json.loads((T / 'evidence.frames-reviewed.pending-playback.json').read_text())
    require(not evidence['browser_playback'] and len(evidence['screenshots']) == 23 and len(evidence['scenes']) == 15 and len(evidence['rendered_segments']) == 23, 'Frames-only evidence scope/history changed.')
    from expansion_site import lesson_content_digest
    evidence['authoring_sha256'] = lesson_content_digest(source)
    require(evidence['authoring_sha256'] == 'a17f096511cfab22acbfa557726ff53460964e6b7941f6245b52623101dd8cb8', 'New learner projection changed.')
    evidence['browser_playback'] = rows
    evidence['qualification_review'] = {'frame_review_complete': True, 'browser_playback_pending': False,
        'root_raw_observation_sha256': args.proof_observations_sha256, 'root_actual_playback_review_sha256': args.root_review_sha256,
        'review': 'Source agent personally inspected all23 actual encoded native holds and88 actual caption regions; complete encoded audio/script/energy checks passed. Root separately personally inspected the three exact advancing, error-free browser observations. Actual User full hearing receipt is independently bound. No source-agent browser or audio listening claim.',
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
    proposal = T / 'canonical-adoption-proposal.json'
    if args.qualify:
        require(all(not p.exists() and not p.is_symlink() for p in targets + [proposal]), 'New-only qualification preserves earlier results.')
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
            'actual_encoded_intervals_reviewed': 23, 'continuous_image_holds': 23, 'actual_caption_regions_reviewed': 88,
            'root_canonical_adoption_pending': True, 'canonical_site_target_or_Git_changed': False}
        with targets[2].open('xb') as f: f.write(encoded(qualification))
        candidate['authoring_status'] = 'complete_source_only_canonical_adoption_proposal'
        candidate['root_canonical_adoption_pending'] = True
        with proposal.open('xb') as f: f.write(encoded(candidate))
    print(json.dumps({'strict_evidence_candidate_passed': True, 'qualification_written': args.qualify,
        'video_sha256': MASTER, 'root_canonical_adoption_pending': True}))


if __name__ == '__main__': main()
