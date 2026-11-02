"""Bind actual authored Records lifecycle frame observations; no publication approval.

Read-only by default. --write-review creates NEW frame-reviewed evidence and
an audit only. The pending worksheet, source, master and all captions stay
unchanged. Genuine browser playback and root qualification remain required.
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
TAKE = Path('expansion/rendered') / (NAME + '-take-01')
FINAL = Path('expansion/plans') / (NAME + '-take-01-final-inputs-20261030')
OBS = Path('expansion/audits/core-records-lifecycle-take-01-actual-frame-observations-20261030-complete-labels.json')
AUDIT = Path('expansion/audits/core-records-lifecycle-take-01-render-and-frame-review-20261030.json')
PINS = {
    TAKE / (NAME + '.mp4'): 'd9bde3b8a309a257258dd48e288b52f2252558ad2af8cf602b91c190f398c332',
    TAKE / 'evidence.pending.json': '6248e8e554ce5fe0995341b21dadad83dbf826d90a787edc34ebe9a6f138030e',
    TAKE / 'assembly.json': '993fbbd24341a6c9b96baafde0ede065f24e82709d5697e0f5f1558610664fa3',
    TAKE / 'frame-source-comparison.json': '93733989b17fb057b4bee40f6352a2fe56202977bc928831154fcb1491e7319f',
    TAKE / 'cue-frame-check.json': '6f53f6552ac12c3647cc5f7511c1cd2238ace76ca342b9ca8a908300a042cd95',
    TAKE / 'encoded-audio.qa.json': '27bc6e320208c0e3c1c9ee71d3ff987e61aec4c5f3a805863e8efd5534b8697c',
    FINAL / 'plan.json': 'c2f13e7bc96f4e4d90d0c607c162444581d8ccea27174422dcd4e64d389ffa8e',
    OBS: 'fe1b965c5d777560df2a36b46beedf0d4bd063a679f2b35d250755cf8f957781',
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import verify_document, _image_dimensions
    for path, digest in PINS.items():
        assert sha(S / path) == digest, 'Changed actual reviewed input: ' + str(path)
    evidence = deepcopy(json.loads((S / TAKE / 'evidence.pending.json').read_text()))
    observations = json.loads((S / OBS).read_text())
    source_check = json.loads((S / TAKE / 'frame-source-comparison.json').read_text())
    cue_check = json.loads((S / TAKE / 'cue-frame-check.json').read_text())
    audio = json.loads((S / TAKE / 'encoded-audio.qa.json').read_text())
    assert source_check['passed'] and cue_check['passed'] and audio['passed']
    assert source_check['intervals_checked'] == 20 and cue_check['cues_checked'] == 112
    assert audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0
    assert not audio['issues'] and not audio['alignment']['text_changes']
    assert audio['audio']['sha256'] == evidence['video']['sha256']
    assert set(observations['full_frame_observations']) == {str(x) for x in range(1, 21)}
    assert observations['caption_cues_personally_reviewed'] == 112
    assert observations['caption_strips_personally_reviewed'] == list(range(1, 20))
    assert not evidence['browser_playback'], 'Never overwrite genuine later playback evidence.'
    rows = {x['id']: x for x in evidence['screenshots']}
    frame_rows = []
    for i, segment in enumerate(evidence['rendered_segments'], 1):
        frame = segment['frame']
        actual = observations['full_frame_observations'][str(i)]
        assert sha(S / frame['file']) == frame['sha256']
        assert _image_dimensions(S / frame['file']) == (1920, 1080)
        # Only authored observations already supported by source literal text
        # enter evidence. Extra actual-frame notes remain in the manual receipt.
        labels = [x for x in actual['labels'] if x in rows[segment['screenshot_id']]['visible_labels']]
        assert labels
        frame.update(review_status='actual_frame_reviewed', application_visible=True,
                     visible_labels=labels, reviewed_control_names=[],
                     review={'reviewer': observations['reviewer'], 'reviewed_at': observations['recorded_at'],
                             'method': observations['method'], 'observation_file': OBS.as_posix(),
                             'observation_sha256': PINS[OBS], 'notes': actual['notes']})
        frame_rows.append({'interval': i, 'scene_id': segment['scene_id'], 'source_id': segment['screenshot_id'],
                           'source_sha256': rows[segment['screenshot_id']]['sha256'],
                           'frame': frame['file'], 'frame_sha256': frame['sha256'], 'video_sha256': frame['video_sha256'],
                           'observed_literal_labels': labels, 'notes': actual['notes']})
    result = verify_document(evidence, S)
    expected_pending = ['browser_playback: must be a nonempty array'] + [
        f'browser_playback: supply exactly one {position} browser playback proof (found 0)'
        for position in ('beginning', 'middle', 'end')]
    assert result['issues'] == expected_pending, result
    audit = {
        'kind': 'actual_Records lifecycle_render_full_frame_and_caption_review',
        'lesson_id': NAME, 'reviewer': observations['reviewer'], 'reviewed_at': observations['recorded_at'],
        'source_frozen_sha256': 'e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5',
        'video_sha256': evidence['video']['sha256'], 'plan_sha256': PINS[FINAL / 'plan.json'],
        'input_hashes': {str(path): digest for path, digest in PINS.items()},
        'actual_full_frames_personally_inspected': 20, 'actual_caption_regions_personally_inspected': 112,
        'actual_caption_strip_files': cue_check['full_width_caption_strips'],
        'frames': frame_rows, 'encoded_full_decode_passed': True,
        'encoded_audio_qa': {'file': (TAKE / 'encoded-audio.qa.json').as_posix(), 'sha256': PINS[TAKE / 'encoded-audio.qa.json'],
                             'silent_cues': 0, 'minimum_raw_cue_rms': audio['minimum_raw_cue_rms'],
                             'method': 'Full encoded AAC decode and exact-script/per-cue energy checks; not agent human listening.'},
        'source_pixel_comparison_max_mean_absolute_error_0_255': source_check['maximum_application_mean_absolute_pixel_error_0_255'],
        'cue_frame_comparison_max_mean_absolute_error_0_255': cue_check['maximum_full_frame_mean_absolute_error_0_255'],
        'caption_foreground_comparison_max_mean_absolute_error_0_255': cue_check['maximum_caption_foreground_mean_absolute_error_0_255'],
        'partial_strict_evidence_report': result,
        'limits': ['Actual current controls, legibility and intact recorded viewport were reviewed through tool displays; no100-percent manual pixel-inspection claim.',
                   'Historical initial finalization is retained. Original optional unit-time inputs are blank; their horizontal overflow is preserved. No attendance, physical response, licensed PDF or later amendment is asserted.',
                   'Browser beginning/middle/end, root final review and public qualification remain pending. This does not adopt a canonical lesson or publish media.'],
        'publishable': False, 'canonical_ready_or_site_changed': False,
    }
    return evidence, audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-review', action='store_true')
    args = parser.parse_args()
    evidence, audit = prepare()
    if args.write_review:
        outputs = {TAKE / 'evidence.frames-reviewed.json': encoded(evidence), AUDIT: encoded(audit)}
        assert not any((S / path).exists() for path in outputs), 'New-only actual review; preserve history.'
        for path, body in outputs.items():
            with (S / path).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'actual_frames_reviewed': 20, 'actual_caption_regions_reviewed': 112,
                      'encoded_audio_qa_passed': True, 'strict_issues_remaining': audit['partial_strict_evidence_report']['issues'],
                      'files_written': args.write_review, 'publishable': False, 'canonical_ready': False}))


if __name__ == '__main__':
    main()
