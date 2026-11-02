"""Bind genuine encoded-frame observations for the Dispatch scheduled-call take.

Read-only by default. --write-review creates NEW evidence/audit files in the
selected take folder. Original pending evidence, sources, audio, captions and
master remain unchanged. Genuine browser playback and Root qualification are
still required; this script cannot supply or infer them.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
MANIFEST = S / 'production/dispatch_schedule_take_01_frame_review_pins_20261030.json'
MANIFEST_SHA = '9150c3dbb3763978e4be2e4d4f55c5dabd29bb88d9092e691736f19cd27017db'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def safe_file(relative):
    require(isinstance(relative, str) and relative and '\\' not in relative
            and all(x not in ('', '.', '..') for x in relative.split('/')),
            'Expected contained source-relative path.')
    p = PurePosixPath(relative)
    require(not p.is_absolute() and p.parts and all(x not in ('.', '..') for x in p.parts),
            'Expected contained source-relative path.')
    path = S / p
    for ancestor in [path, *path.parents]:
        if ancestor == S.parent:
            break
        require(not ancestor.is_symlink(), 'Symlink input is not a frozen review asset.')
    require(path.resolve().is_relative_to(S.resolve()) and path.is_file(), 'Missing or escaped actual review asset.')
    return path


def prepare(alias):
    require(__debug__, 'Use ordinary Python; retained strict validators contain assertions.')
    require(sha(MANIFEST) == MANIFEST_SHA, 'Changed actual review manifest.')
    cfg = json.loads(MANIFEST.read_text())['lessons'][alias]
    for relative, digest in cfg['pins'].items():
        require(sha(safe_file(relative)) == digest, 'Changed pinned actual review input: ' + relative)
    take = Path('expansion/rendered') / (cfg['id'] + '-take-01')
    evidence = deepcopy(json.loads(safe_file((take / 'evidence.pending.json').as_posix()).read_text()))
    observations = json.loads(safe_file(cfg['observations']).read_text())
    source_check = json.loads(safe_file((take / 'frame-source-comparison.json').as_posix()).read_text())
    cue_check = json.loads(safe_file((take / 'cue-frame-check.json').as_posix()).read_text())
    audio = json.loads(safe_file((take / 'encoded-audio.qa.json').as_posix()).read_text())
    master = evidence['video']['sha256']
    require(source_check['passed'] and cue_check['passed'] and audio['passed'], 'Encoded QA did not pass.')
    require(source_check['intervals_checked'] == cfg['holds'] and cue_check['cues_checked'] == cfg['cues'],
            'Incomplete encoded source/caption checks.')
    require(source_check['video_sha256'] == cue_check['video_sha256'] == audio['audio']['sha256'] == master,
            'Reviews refer to a different master.')
    require(audio['audio']['full_decode'] == 'passed' and audio['silent_raw_cues'] == audio['silent_corrected_cues'] == 0
            and not audio['issues'] and not audio['alignment']['text_changes'], 'Encoded narration QA failed.')
    require(observations['video_sha256'] == master and observations['issues'] == [], 'Actual visual review has unresolved issues.')
    require(set(observations['full_frame_observations']) == {str(i) for i in range(1, cfg['holds'] + 1)},
            'Missing actual full-frame observations.')
    require(observations['caption_cues_personally_reviewed'] == cfg['cues'], 'Incomplete actual caption inspection.')
    strips = cue_check['full_width_caption_strips']
    require(observations['caption_strips_personally_reviewed'] == list(range(1, len(strips) + 1)),
            'Missing actual caption-strip inspection.')
    require([row['file'] for row in observations['caption_strip_files']] == strips, 'Caption-strip membership changed.')
    for row in observations['caption_strip_files']:
        require(sha(safe_file(row['file'])) == row['sha256'], 'Changed actually inspected caption strip.')
    require(evidence['browser_playback'] == [] and observations['browser_playback_reviewed'] is False,
            'Do not overwrite or invent later genuine browser review.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import verify_document, _image_dimensions
    rows = {x['id']: x for x in evidence['screenshots']}
    frames = []
    require(len(evidence['rendered_segments']) == cfg['holds'], 'Render scope changed.')
    for i, segment in enumerate(evidence['rendered_segments'], 1):
        frame = segment['frame']
        actual = observations['full_frame_observations'][str(i)]
        require((actual['frame'], actual['frame_sha256']) == (frame['file'], frame['sha256']),
                'Observation does not bind this actual encoded frame.')
        require(sha(safe_file(frame['file'])) == frame['sha256'] and
                _image_dimensions(safe_file(frame['file'])) == (1920, 1080), 'Encoded frame changed.')
        require(frame['video_sha256'] == master, 'Frame identifies stale master.')
        labels = actual['labels']
        require(labels and all(label in rows[segment['screenshot_id']]['visible_labels'] for label in labels),
                'Actual observation contains unsupported label.')
        require(actual['notes'].strip(), 'Actual app-state observation missing.')
        frame.update(review_status='actual_frame_reviewed', application_visible=True,
                     visible_labels=labels, reviewed_control_names=[],
                     review={'reviewer': observations['reviewer'], 'reviewed_at': observations['recorded_at'],
                             'method': observations['method'], 'observation_file': cfg['observations'],
                             'observation_sha256': cfg['pins'][cfg['observations']], 'notes': actual['notes']})
        frames.append({'interval': i, 'scene_id': segment['scene_id'], 'source_id': segment['screenshot_id'],
                       'frame': frame['file'], 'frame_sha256': frame['sha256'],
                       'source_sha256': rows[segment['screenshot_id']]['sha256'],
                       'observed_literal_labels': labels, 'notes': actual['notes']})
    report = verify_document(evidence, S)
    expected = ['browser_playback: must be a nonempty array'] + [
        f'browser_playback: supply exactly one {position} browser playback proof (found 0)'
        for position in ('beginning', 'middle', 'end')]
    require(report['issues'] == expected, 'Unexpected strict frame evidence failure: ' + json.dumps(report))
    audit = {'kind': 'actual_Dispatch_scheduled_call_encoded_frame_and_caption_review', 'lesson_id': cfg['id'],
             'reviewer': observations['reviewer'], 'reviewed_at': observations['recorded_at'],
             'video_sha256': master, 'input_hashes': cfg['pins'], 'manifest_sha256': MANIFEST_SHA,
             'actual_full_frames_personally_inspected': cfg['holds'],
             'actual_caption_regions_personally_inspected': cfg['cues'],
             'caption_strip_files': observations['caption_strip_files'], 'frames': frames,
             'encoded_full_decode_passed': True, 'encoded_audio_qa_passed': True,
             'maximum_application_mae_0_255': source_check['maximum_application_mean_absolute_pixel_error_0_255'],
             'maximum_full_frame_mae_0_255': cue_check['maximum_full_frame_mean_absolute_error_0_255'],
             'maximum_caption_foreground_mae_0_255': cue_check['maximum_caption_foreground_mean_absolute_error_0_255'],
             'partial_strict_evidence_report': report,
             'limits': ['Full recorded viewport/control legibility reviewed through actual image displays; no100-percent manual pixel-inspection claim.',
                        'Actual scheduled creation and full Edit Call time-change readbacks retained. No Core013 operational image, nearest calculation, automatic worker execution, dispatch-now success, notification delivery, acknowledgement or closure is inferred.',
                        'No audio listening by this agent. Genuine User hearing is separately retained in its original hash-bound receipt.',
                        'Actual browser beginning/middle/end and final Root qualification remain required.'],
             'publishable': False, 'canonical_site_target_or_Git_changed': False}
    return take, evidence, audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=('schedule',), default='schedule')
    parser.add_argument('--write-review', action='store_true')
    args = parser.parse_args(argv)
    take, evidence, audit = prepare(args.lesson)
    outputs = {take / 'evidence.frames-reviewed.json': encoded(evidence),
               take / 'render-and-frame-review-20261030.json': encoded(audit)}
    if args.write_review:
        require(all(not (S / path).exists() and not (S / path).is_symlink() for path in outputs),
                'New-only frame review refuses existing output.')
        for path, body in outputs.items():
            with (S / path).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'actual_frames_reviewed': audit['actual_full_frames_personally_inspected'],
                      'actual_caption_regions_reviewed': audit['actual_caption_regions_personally_inspected'],
                      'strict_issues_remaining': audit['partial_strict_evidence_report']['issues'],
                      'files_written': args.write_review, 'publishable': False}))


if __name__ == '__main__':
    main()
