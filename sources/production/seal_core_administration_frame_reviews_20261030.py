"""Bind genuine Billing, Shifts or Training encoded-frame reviews; no publication.

Default is read-only. --write-review creates NEW frames-reviewed evidence and a
release-local audit. It preserves the original worksheet, captures, historical
source reviews, frozen narration, captions, master and canonical lessons.
Actual Root browser playback and final public qualification remain required.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
CATALOG = SOURCES / 'production/core_administration_render_review_inputs_20261030_v2.json'
CATALOG_SHA = '090c861ccca0fd0d29221668c27866abd3e1272659368ac5a543e7dbd620ed4d'


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
    require(path.is_relative_to(root.resolve()), 'Input escaped its asset root.')
    return path


def prepare(lesson):
    require(__debug__, 'Use ordinary Python; strict evidence validators contain assertions.')
    require(sha(CATALOG) == CATALOG_SHA, 'Changed reviewed release catalog.')
    catalog = json.loads(CATALOG.read_text())
    config = catalog['lessons'][lesson]
    for path, digest in catalog['tools'].items():
        require(sha(inside(ROOT, path)) == digest, 'Changed review tool: ' + path)
    for path, digest in config['pins'].items():
        require(sha(inside(SOURCES, path)) == digest, 'Changed reviewed input: ' + path)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import verify_document, _image_dimensions

    take = inside(SOURCES, config['take'])
    evidence = deepcopy(json.loads((take / 'evidence.pending.json').read_text()))
    assembly = json.loads((take / 'assembly.json').read_text())
    observations = json.loads((take / 'actual-frame-observations.json').read_text())
    addendum = json.loads(inside(SOURCES, config['label_addendum']).read_text())
    source_check = json.loads((take / 'frame-source-comparison.json').read_text())
    cue_check = json.loads((take / 'cue-frame-check.json').read_text())
    audio = json.loads((take / 'encoded-audio.qa.json').read_text())
    master = config['master_sha256']
    require(addendum['video_sha256'] == master and addendum['original_observations_sha256'] ==
            config['pins'][config['take'] + '/actual-frame-observations.json'] and
            addendum['browser_playback_claim'] is False and addendum['publication_approved'] is False,
            'Additional literal observations must bind the actual original review and unchanged master.')
    require(evidence['video']['sha256'] == master == observations['video_sha256'], 'Master review mismatch.')
    require(assembly['full_decode'] == 'passed', 'Actual encoded full decode did not pass.')
    require(len(evidence['scenes']) == config['scene_count'] and
            len(evidence['screenshots']) == config['source_count'] and
            len(evidence['rendered_segments']) == config['interval_count'] and
            sum(len(x['captions']) for x in evidence['scenes']) == config['cue_count'], 'Review scope changed.')
    for review in (source_check, cue_check):
        require(review['passed'] is True and review['video_sha256'] == master, 'Encoded pixel check failed.')
        require(review['visual_approval_inferred'] is False and
                review['browser_playback_inferred'] is False and review['publication_approved'] is False,
                'Technical checks must not manufacture actual review or playback.')
    require(source_check['intervals_checked'] == config['interval_count'] and
            cue_check['cues_checked'] == config['cue_count'], 'Incomplete interval/caption checks.')
    require(source_check['maximum_application_mean_absolute_pixel_error_0_255'] < 6 and
            cue_check['maximum_full_frame_mean_absolute_error_0_255'] < 6 and
            cue_check['maximum_caption_foreground_mean_absolute_error_0_255'] < 15, 'Pixel discrepancy.')
    require(audio['passed'] is True and not audio['issues'] and not audio['alignment']['text_changes'] and
            audio['audio']['sha256'] == master and audio['audio']['full_decode'] == 'passed' and
            audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0, 'Encoded narration QA failed.')
    require(set(observations['full_frame_observations']) ==
            {str(x) for x in range(1, config['interval_count'] + 1)}, 'Missing actual full-frame observations.')
    require(observations['caption_cues_personally_reviewed'] == config['cue_count'] and
            observations['caption_strips_personally_reviewed'] == list(range(1, config['strip_count'] + 1)),
            'Actual caption review is incomplete.')
    require(observations['source_or_audio_or_caption_bytes_changed'] is False and
            observations['browser_playback_claim'] is False and observations['publication_approved'] is False,
            'Actual frame review must retain its limited scope.')
    reviewed_at = datetime.fromisoformat(observations['recorded_at'])
    require(reviewed_at.tzinfo is not None and reviewed_at <= datetime.now(timezone.utc),
            'Current actual review needs its genuine timezone-aware timestamp.')
    require(evidence['browser_playback'] == [], 'Never overwrite genuine later playback evidence.')
    obs_relative = (take / 'actual-frame-observations.json').relative_to(SOURCES).as_posix()
    obs_sha = config['pins'][obs_relative]
    source_rows = {row['id']: row for row in evidence['screenshots']}
    frames = []
    for i, segment in enumerate(evidence['rendered_segments'], 1):
        frame = segment['frame']
        actual = observations['full_frame_observations'][str(i)]
        added = addendum['intervals'].get(str(i), {})
        source = source_rows[segment['screenshot_id']]
        require(sha(inside(SOURCES, frame['file'])) == frame['sha256'] == actual['frame_sha256'] and
                frame['video_sha256'] == master, 'Changed actual encoded frame.')
        require(_image_dimensions(inside(SOURCES, frame['file'])) == (1920, 1080), 'Wrong actual frame size.')
        require(not added or added['frame_sha256'] == frame['sha256'], 'Additional review frame changed.')
        labels = [label for label in actual.get('visible_labels', actual.get('labels', [])) +
                  added.get('additional_visible_labels', [])
                  if label in source['visible_labels']]
        require(labels and actual['notes'], 'No actual literal observed control supported by source.')
        frame.update(review_status='actual_frame_reviewed', application_visible=True,
                     visible_labels=labels, reviewed_control_names=[],
                     review={'reviewer': observations['reviewer'], 'reviewed_at': observations['recorded_at'],
                             'method': observations['method'], 'observation_file': obs_relative,
                             'observation_sha256': obs_sha, 'notes': actual['notes'],
                             'additional_literal_observations_file': config['label_addendum'],
                             'additional_literal_observations_sha256': config['pins'][config['label_addendum']]})
        frames.append({'interval': i, 'scene_id': segment['scene_id'], 'source_id': segment['screenshot_id'],
                       'source_sha256': source['sha256'], 'frame': frame['file'], 'frame_sha256': frame['sha256'],
                       'video_sha256': master, 'observed_literal_labels': labels, 'notes': actual['notes']})
    result = verify_document(evidence, SOURCES)
    expected_pending = ['browser_playback: must be a nonempty array'] + [
        f'browser_playback: supply exactly one {position} browser playback proof (found 0)'
        for position in ('beginning', 'middle', 'end')]
    require(result['issues'] == expected_pending, 'Unexpected strict evidence issue: ' + json.dumps(result))
    audit = {'kind': 'actual_administration_render_full_frame_and_caption_review',
             'lesson_id': config['lesson_id'], 'reviewer': observations['reviewer'],
             'reviewed_at': observations['recorded_at'], 'catalog_sha256': CATALOG_SHA,
             'video_sha256': master, 'input_hashes': config['pins'],
             'actual_full_frames_personally_inspected': config['interval_count'],
             'actual_caption_regions_personally_inspected': config['cue_count'],
             'actual_caption_strip_files': cue_check['full_width_caption_strips'], 'frames': frames,
             'encoded_full_decode_passed': True, 'encoded_audio_qa_passed': True,
             'minimum_raw_cue_rms': audio['minimum_raw_cue_rms'],
             'strict_partial_evidence_report': result,
             'limits': ['Actual encoded screenshot holds and caption regions were personally inspected through tool displays; no every-pixel inspection, agent hearing or browser playback is inferred.',
                        'All captures, historical reviews, frozen narration, captions and encoded master remain unchanged.',
                        'Root actual beginning/middle/end playback and full public evidence qualification remain required.'],
             'publishable': False, 'canonical_ready_site_target_or_Git_changed': False}
    return config, evidence, audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=('billing', 'shifts', 'training'))
    parser.add_argument('--write-review', action='store_true')
    args = parser.parse_args(argv)
    config, evidence, audit = prepare(args.lesson)
    take = inside(SOURCES, config['take'])
    outputs = {take / 'evidence.frames-reviewed.json': encoded(evidence),
               take / 'frame-review.audit.json': encoded(audit)}
    if args.write_review:
        require(all(not p.exists() and not p.is_symlink() for p in outputs), 'New-only review preserves history.')
        for path, body in outputs.items():
            with path.open('xb') as stream:
                stream.write(body)
    print(json.dumps({'lesson_id': config['lesson_id'], 'actual_frames_reviewed': config['interval_count'],
                      'actual_caption_regions_reviewed': config['cue_count'], 'encoded_audio_qa_passed': True,
                      'remaining_issues': audit['strict_partial_evidence_report']['issues'],
                      'predicted_evidence_sha256': hashlib.sha256(encoded(evidence)).hexdigest(),
                      'files_written': args.write_review, 'publishable': False, 'canonical_ready': False}))


if __name__ == '__main__':
    main()
