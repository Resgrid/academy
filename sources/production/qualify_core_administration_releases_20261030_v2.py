"""Qualify administration masters against genuine Root full-page or viewport proofs.

Read-only by default. Both the exact raw-proof hash and genuine Root review
receipt hash are mandatory. No receipt, browser event, screenshot or hearing is
created here. --qualify writes NEW release-local reviewed evidence, proof rows
and qualification only after strict evidence and public-export preflight pass.
Canonical lessons, website, target repository and Git are never changed.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
CATALOG = SOURCES / 'production/core_administration_qualification_inputs_20261030.json'
CATALOG_SHA = '621ef37b5b5978280a8adda4a8ed7d882706923746c3e33d3616a395b0439e82'
POSITIONS = ('beginning', 'middle', 'end')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def inside(root, relative):
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), 'Input escaped its root.')
    return path


def actual_timestamp(value):
    stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc),
            'Actual review timestamp must be timezone-aware and not in the future.')
    return stamp


def validate_screenshot_dimensions(screenshot, path):
    """Validate the unchanged full-page or viewport image against actual metadata."""
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions
    dimensions = _image_dimensions(path)
    declared = (screenshot.get('width'), screenshot.get('height'))
    require(all(type(value) is int for value in declared),
            'Actual screenshot metadata must contain integer width and height.')
    require(dimensions == declared,
            'Actual screenshot header dimensions do not match supplied screenshot metadata.')
    require(dimensions[0] >= 960 and dimensions[1] >= 540,
            'Actual browser screenshot is smaller than the 960x540 minimum.')
    return dimensions


def validate_playback(rows, receipt, config, raw_sha, asset_root=SOURCES):
    master = config['master_sha256']
    require(isinstance(rows, list) and len(rows) == 3 and
            [x.get('position') for x in rows] == list(POSITIONS),
            'Require exactly three genuine beginning/middle/end observations, in order.')
    require(receipt.get('reviewer') == 'Root' and receipt.get('actual_playback_and_captions_reviewed') is True and
            receipt.get('raw_observations_sha256') == raw_sha and receipt.get('video_sha256') == master and
            isinstance(receipt.get('notes'), str) and receipt['notes'].strip(),
            'Genuine Root playback review must bind this exact raw proof and current master.')
    reviewed_at = actual_timestamp(receipt['reviewed_at'])
    positions = receipt.get('positions')
    require(isinstance(positions, list) and [x.get('position') for x in positions] == list(POSITIONS),
            'Genuine Root receipt must identify all three personally reviewed browser screens.')
    result = deepcopy(rows)
    for row, reviewed in zip(result, positions):
        require(row.get('video_sha256') == master and row.get('ready_state') == 4 and
                row.get('network_state') == 1 and row.get('paused') is False and row.get('ended') is False,
                'Playback must be the actual ready, advancing, current master.')
        require(row.get('media_error', 'missing') is None and row.get('console_errors') == [],
                'Resolve browser/media errors before qualification.')
        require((row.get('video_width'), row.get('video_height')) == (1920, 1080) and
                isinstance(row.get('previous_time'), (int, float)) and
                isinstance(row.get('current_time'), (int, float)) and
                0 <= row['previous_time'] < row['current_time'], 'Wrong dimensions or nonadvancing playback.')
        require(row.get('captions', {}).get('mode') == 'showing' and row['captions'].get('text'),
                'Actual browser proof must show a current caption.')
        require(actual_timestamp(row['captured_at']) <= reviewed_at,
                'Genuine Root review cannot precede its observed playback screenshot.')
        screenshot = row.get('screenshot', {})
        path = inside(Path(asset_root), screenshot['file'])
        require(path.is_relative_to(inside(Path(asset_root), config['take']) / 'playback'),
                'Proof image must belong to this exact release playback folder.')
        digest = sha(path)
        require(digest == screenshot.get('sha256') == reviewed.get('screenshot_sha256'),
                'Actual playback screenshot changed or was not personally reviewed by Root.')
        validate_screenshot_dimensions(screenshot, path)
    return result


def prepare(lesson, raw_file, raw_sha, receipt_file, receipt_sha):
    require(__debug__, 'Use ordinary Python; retained strict validators contain assertions.')
    require(sha(CATALOG) == CATALOG_SHA, 'Changed final qualification catalog.')
    catalog = json.loads(CATALOG.read_text())
    config = catalog['lessons'][lesson]
    for path, digest in catalog['tools'].items():
        require(sha(inside(ROOT, path)) == digest, 'Changed qualification tool: ' + path)
    for path, digest in config['pins'].items():
        require(sha(inside(SOURCES, path)) == digest, 'Changed genuine reviewed input: ' + path)
    raw_file, receipt_file = inside(ROOT, raw_file), inside(ROOT, receipt_file)
    require(raw_file.is_file() and receipt_file.is_file() and sha(raw_file) == raw_sha and
            sha(receipt_file) == receipt_sha, 'Exact actual proof and genuine review hashes are required.')
    receipt = json.loads(receipt_file.read_text())
    rows = validate_playback(json.loads(raw_file.read_text()), receipt, config, raw_sha)
    source = json.loads(inside(SOURCES, config['frozen']).read_text())
    plan = json.loads(inside(SOURCES, config['plan']).read_text())
    heard = json.loads(inside(SOURCES, config['listening']).read_text())
    require(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True and
            heard.get('lesson_sha256') == config['pins'][config['frozen']] and
            heard.get('audio_sha256') == plan['narration']['sha256'],
            'Genuine complete User hearing must match this frozen lesson and unchanged narration.')
    take = inside(SOURCES, config['take'])
    evidence = json.loads((take / 'evidence.frames-reviewed.json').read_text())
    require(evidence['browser_playback'] == [], 'Preserve original frames-only evidence.')
    require(len(evidence['screenshots']) == config['source_count'] and
            len(evidence['scenes']) == config['scene_count'] and
            len(evidence['rendered_segments']) == config['interval_count'] and
            sum(len(x['captions']) for x in evidence['scenes']) == config['cue_count'], 'Scope changed.')
    for filename, key, count in [('frame-source-comparison.json', 'intervals_checked', config['interval_count']),
                                 ('cue-frame-check.json', 'cues_checked', config['cue_count'])]:
        review = json.loads((take / filename).read_text())
        require(review['passed'] is True and review['video_sha256'] == config['master_sha256'] and
                review[key] == count, 'Actual encoded source/caption checks incomplete.')
    qa = json.loads((take / 'encoded-audio.qa.json').read_text())
    require(qa['passed'] is True and not qa['issues'] and not qa['alignment']['text_changes'] and
            qa['audio']['sha256'] == config['master_sha256'] and qa['audio']['full_decode'] == 'passed' and
            qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0, 'Encoded audio check failed.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import verify_document
    import expansion_site
    require(expansion_site.lesson_content_digest(source) == config['authoring_sha256'], 'Changed learner authoring.')
    evidence['authoring_sha256'] = config['authoring_sha256']
    evidence['browser_playback'] = rows
    evidence['qualification_review'] = {
        'frame_review_complete': True, 'browser_playback_pending': False,
        'parent_raw_observation_sha256': raw_sha, 'parent_actual_review_sha256': receipt_sha,
        'parent_actual_review_file': receipt_file.relative_to(ROOT).as_posix(),
        'review': 'Root genuinely reviewed the exact three advancing browser playback screens and current captions, as recorded in the separately hash-bound receipt. The source agent personally inspected every actual encoded hold and every full-width caption region. Full encoded decode, exact-script and per-cue audio checks supplement the genuine complete User listening receipt; they do not replace it.',
        'canonical_or_ready_changed': False}
    report = verify_document(evidence, SOURCES)
    require(report['passed'] is True and not report['issues'], 'Strict evidence gate: ' + json.dumps(report))
    final_path = take / 'evidence.reviewed.json'
    candidate = dict(source, export_ready=True, publication_mode='video',
                     evidence_file=final_path.relative_to(SOURCES).as_posix())
    # Supply only the not-yet-written candidate document in memory. The original
    # exporter, every actual source/media asset and full strict validator remain
    # intact. This allows a genuinely read-only public preflight before writing.
    original_read = expansion_site._read_json

    def candidate_read(root, relative):
        if Path(root).resolve() == SOURCES.resolve() and relative == candidate['evidence_file']:
            return deepcopy(evidence)
        return original_read(root, relative)

    with patch.object(expansion_site, '_read_json', side_effect=candidate_read):
        expansion_site._prepare(candidate, SOURCES)
    return config, rows, evidence, report, candidate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=('billing', 'shifts', 'training'))
    parser.add_argument('--proof-file', required=True, help='Actual raw observation file under staging root.')
    parser.add_argument('--proof-sha256', required=True)
    parser.add_argument('--root-review-file', required=True, help='Genuine separate Root playback review receipt.')
    parser.add_argument('--root-review-sha256', required=True)
    parser.add_argument('--qualify', action='store_true')
    args = parser.parse_args(argv)
    config, rows, evidence, report, candidate = prepare(
        args.lesson, args.proof_file, args.proof_sha256, args.root_review_file, args.root_review_sha256)
    take = inside(SOURCES, config['take'])
    proofs, final, qualification = take / 'playback/proofs.json', take / 'evidence.reviewed.json', take / 'qualification.json'
    evidence_sha = hashlib.sha256(encoded(evidence)).hexdigest()
    result = {'passed': True, 'lesson_id': config['lesson_id'], 'issues': [], 'public_export_preflight': 'passed',
              'frozen_source_sha256': config['pins'][config['frozen']],
              'authoring_sha256': config['authoring_sha256'], 'video_sha256': config['master_sha256'],
              'evidence_sha256': evidence_sha, 'proofs_sha256': hashlib.sha256(encoded(rows)).hexdigest(),
              'parent_actual_raw_observations_sha256': args.proof_sha256,
              'parent_actual_playback_review_sha256': args.root_review_sha256,
              'actual_User_listening_receipt_sha256': config['pins'][config['listening']],
              'rendered_intervals': config['interval_count'], 'caption_regions_reviewed': config['cue_count'],
              'source_images': config['source_count'], 'qualification_catalog_sha256': CATALOG_SHA,
              'root_canonical_adoption_pending': True, 'canonical_site_target_or_Git_changed': False}
    if args.qualify:
        require(all(not path.exists() and not path.is_symlink() for path in (proofs, final, qualification)),
                'New-only qualification preserves prior outputs.')
        require(proofs.parent.is_dir(), 'Actual playback folder must already exist from genuine browser captures.')
        for path, value in ((proofs, rows), (final, evidence), (qualification, result)):
            with path.open('xb') as stream:
                stream.write(encoded(value))
    elif final.exists():
        require(final.read_bytes() == encoded(evidence) and proofs.read_bytes() == encoded(rows) and
                qualification.read_bytes() == encoded(result), 'Existing qualification changed.')
    print(json.dumps({'lesson_id': config['lesson_id'], 'strict_evidence_passed': report['passed'],
                      'public_export_preflight': 'passed', 'qualified_outputs_written': args.qualify,
                      'evidence_sha256': evidence_sha, 'source_images': config['source_count'],
                      'intervals': config['interval_count'], 'caption_regions': config['cue_count'],
                      'canonical_or_site_changed': False}))


if __name__ == '__main__':
    main()
