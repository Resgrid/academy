"""Guard record-definition qualification behind genuine exact Root playback.

Default is read-only. This helper cannot supply missing browser observations or
review them for Root. --qualify requires the actual raw-proof and Root-review
hashes; it creates NEW evidence only and never changes a canonical lesson/site.
"""
import argparse
from datetime import datetime, timezone
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-records-administration'
T = S / 'expansion/rendered/core-records-administration-take-01'
SOURCE = S / 'expansion/plans/core-records-administration-capture-freeze-20261030/core-records-administration.narrated-source.json'
PLAN = S / 'expansion/plans/core-records-administration-take-01-final-inputs-20261030/plan.json'
LISTENING = S / 'expansion/audio/core-records-administration.listening-review.json'
MASTER = 'a99639492107cfea532cac2ad1f0328aeb945e3b311cb82f83076d3d05802377'
CANDIDATE = S / 'expansion/plans/core-records-administration-take-01-release-proposal-20261030/core-records-administration.canonical-proposed.json'
PROJECTION = S / 'expansion/plans/core-records-administration-take-01-release-proposal-20261030/learner-content.unchanged.json'
AUTHORING = '1c18beece6f840b2d995b18e1a53ce86434436399635db797c6de59617ab3e45'
SOURCE_PINS = {'expansion/plans/core-records-administration-capture-freeze-20261030/core-records-administration.narrated-source.json': '3d459af0acfd125a0b2b58fe4cc3a6478c874fc1315cb74dce65ec93130d0754', 'expansion/plans/core-records-administration-take-01-final-inputs-20261030/plan.json': '0bb6c8802c18d67eef05642ecb05635c9752f821cb63aedfd66352c5bd1d51bb', 'expansion/audio/core-records-administration.listening-review.json': '87244e5730feccf63f3ddd04c76dcd2ad51e9573ca21dadf99f070ec14cff634', 'expansion/rendered/core-records-administration-take-01/core-records-administration.mp4': 'a99639492107cfea532cac2ad1f0328aeb945e3b311cb82f83076d3d05802377', 'expansion/rendered/core-records-administration-take-01/evidence.frames-reviewed.json': 'a5b874bc459383b0d0fa6002922fcca98c5a1f459826f2f4bcb0c79eb988376b', 'expansion/rendered/core-records-administration-take-01/frame-source-comparison.json': 'e2dfeea2c733b14216b5b4b281b9ba8124f2ce8476bf517352fd82cdb2adcb71', 'expansion/rendered/core-records-administration-take-01/cue-frame-check.json': '97454eddd289193954bc79a9c22c50d07b4c7e949bcc447ce7f114df7db15687', 'expansion/rendered/core-records-administration-take-01/encoded-audio.qa.json': '818c9e59dcb948f91047d6f2ae42a7007b1952b2288ae666a4fdb014d00de322', 'expansion/rendered/core-records-administration-take-01/actual-frame-observations.json': '657381659e77f4fad6395237f261ff050f40244cd85a214d64cbc574eac3a201', 'expansion/rendered/core-records-administration-take-01/actual-frame-literal-addendum.json': 'cfd3ace75862f9756b40b693a8cf7306bbefb062fdde559cfd44886915e2d390', 'expansion/rendered/core-records-administration-take-01/assembly.json': '714334b41f31d4d190b7b607f73099f758e5004e49ec78798350933a738712a9', 'expansion/plans/core-records-administration-take-01-release-proposal-20261030/core-records-administration.canonical-proposed.json': 'fda07a5ca279d418bc82d575fe5265e5b600db75eb52ba2865ade3517f59d9b8', 'expansion/plans/core-records-administration-take-01-release-proposal-20261030/learner-content.unchanged.json': 'cd9b8c39f0f15edfe3568afa2ce3281fbf7884cc6b5d674de34bf83f69407388'}
CODE_PINS = {'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa', 'scripts/expansion_site.py': 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8'}
PINS = {S / p: h for p, h in SOURCE_PINS.items()} | {ROOT / p: h for p, h in CODE_PINS.items()}


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
    stamp = datetime.fromisoformat(root_review['reviewed_at'].replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc), 'Root actual playback review requires a nonfuture timezone-aware time.')
    require(root_review.get('learner_content_sha256') == AUTHORING and root_review.get('learner_projection_sha256') == PINS[PROJECTION], 'Root playback review must bind unchanged exact learner text and practice fields.')
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
        require(type(r['screenshot'].get('width')) is int and type(r['screenshot'].get('height')) is int and (r['screenshot']['width'], r['screenshot']['height']) == (width, height), 'Actual JPEG dimensions must match raw screenshot metadata.')
        require(width >= 960 and height >= 540, 'Actual playback screenshot is undersized.')
        require(r.get('captions', {}).get('mode') == 'showing' and isinstance(r['captions'].get('text'), str) and r['captions']['text'].strip(), 'Actual native caption is not shown in the genuine playback observation.')
    require(root_review.get('screenshot_sha256s') == [r['screenshot']['sha256'] for r in rows], 'Root personal review does not bind exact three images.')
    source = json.loads(SOURCE.read_text())
    heard = json.loads(LISTENING.read_text())
    plan = json.loads(PLAN.read_text())
    require(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True and heard.get('lesson_sha256') == PINS[SOURCE] and heard.get('audio_sha256') == plan['narration']['sha256'], 'Genuine complete User hearing does not match.')
    for name, count, key in [('frame-source-comparison.json', 39, 'intervals_checked'), ('cue-frame-check.json', 135, 'cues_checked')]:
        d = json.loads((T / name).read_text())
        require(d['passed'] is True and d[key] == count and d['video_sha256'] == MASTER, 'Incomplete actual source/caption numerical check.')
    audio = json.loads((T / 'encoded-audio.qa.json').read_text())
    require(audio['passed'] is True and audio['audio']['sha256'] == MASTER and audio['audio']['full_decode'] == 'passed' and audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0 and not audio['issues'], 'Encoded audio QA failed.')
    evidence = json.loads((T / 'evidence.frames-reviewed.json').read_text())
    require(not evidence['browser_playback'] and len(evidence['screenshots']) == 35 and len(evidence['scenes']) == 16 and len(evidence['rendered_segments']) == 39, 'Frames-only evidence scope/history changed.')
    from expansion_site import lesson_content_digest
    require(lesson_content_digest(source) == AUTHORING and lesson_content_digest(json.loads(CANDIDATE.read_text())) == AUTHORING, 'Frozen/candidate learner content or practice text changed.')
    evidence['authoring_sha256'] = AUTHORING
    evidence['browser_playback'] = rows
    evidence['qualification_review'] = {'frame_review_complete': True, 'browser_playback_pending': False,
        'root_raw_observation_sha256': args.proof_observations_sha256, 'root_actual_playback_review_sha256': args.root_review_sha256,
        'review': 'Source agent personally inspected all39 actual encoded interval frames and135 actual caption regions; complete encoded audio/script/energy checks passed. Root separately personally inspected the three exact advancing, error-free browser observations. Actual User full hearing receipt is independently bound. No source-agent browser or audio listening claim.',
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
        candidate = json.loads(CANDIDATE.read_text())
        require(candidate == dict(source, export_ready=True, publication_mode='video', evidence_file=targets[1].relative_to(S).as_posix()), 'Candidate changed frozen learner content or unsupported fields.')
        _prepare(candidate, S)
        qualification = {'passed': True, 'lesson_id': NAME, 'issues': [], 'public_export_preflight': 'passed',
            'video_sha256': MASTER, 'frozen_source_sha256': PINS[SOURCE], 'authoring_sha256': evidence['authoring_sha256'],
            'evidence_sha256': sha(targets[1]), 'proofs_sha256': sha(targets[0]),
            'actual_User_full_listening_sha256': PINS[LISTENING], 'proposed_canonical_sha256': PINS[CANDIDATE], 'unchanged_learner_projection_sha256': PINS[PROJECTION], 'actual_Root_playback_review_sha256': args.root_review_sha256,
            'actual_Root_raw_browser_observations_sha256': args.proof_observations_sha256,
            'actual_encoded_intervals_reviewed': 39, 'continuous_image_holds': 39, 'actual_caption_regions_reviewed': 135,
            'root_canonical_adoption_pending': True, 'canonical_site_target_or_Git_changed': False}
        with targets[2].open('xb') as f: f.write(encoded(qualification))
    print(json.dumps({'strict_evidence_candidate_passed': True, 'qualification_written': args.qualify,
        'video_sha256': MASTER, 'root_canonical_adoption_pending': True}))


if __name__ == '__main__': main()
