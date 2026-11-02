"""Compare all actual encoded native Unit cue frames to exact frozen compositions.

Numerical checks support, and never substitute for, separate personal image
inspection or genuine browser playback. Existing captures and media stay intact.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
T = S / 'expansion/rendered/app-unit-call-lifecycle-native-take-01'
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import validate_inputs, make_frame, find_font
from PIL import Image, ImageChops, ImageStat


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert __debug__, 'Do not disable retained numerical comparison guards.'
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--master-sha256',required=True);args=p.parse_args()
    recipe = validate_inputs(
        S / 'expansion/plans/app-unit-call-lifecycle-native-candidate-20261030/lesson.candidate.json',
        S / 'expansion/plans/app-unit-call-lifecycle-native-take-01-final-inputs-20261030/plan.json', S)
    manifest = T / 'frame-qa/extraction-and-pixel-metrics.json'
    extraction = json.loads(manifest.read_text())
    master = T / 'app-unit-call-lifecycle-native.mp4'
    master_sha = args.master_sha256
    assert len(master_sha)==64 and all(c in '0123456789abcdef' for c in master_sha)
    assert sha(master) == extraction['video_sha256'] == master_sha
    assert len(recipe['cues']) == len(extraction['cue_frames']) == 88
    outputs = [T / 'frame-source-comparison.json', T / 'cue-frame-check.json']
    assert not any(p.exists() for p in outputs), 'Preserve historical numerical checks.'
    frames = []
    font = find_font()
    indexed = {r['cue']: r for r in extraction['cue_frames']}
    with tempfile.TemporaryDirectory(prefix='academy-unit-native-cue-compare-') as folder:
        expected = Path(folder) / 'expected.png'
        for scene in recipe['scenes']:
            for cue in scene['captions']:
                row = indexed[cue['cue']]
                actual = S / row['file']
                assert sha(actual) == row['sha256']
                assert row['source_id'] == cue['screenshot_id']
                assert cue['start'] <= row['actual_time'] < cue['end']
                assert row['caption_text'] == cue['text']
                make_frame(recipe, {'scene_id': scene['id'], 'title': scene['title'],
                    'screenshot_id': cue['screenshot_id'], 'start': cue['start'],
                    'end': cue['end'], 'caption': cue['text']}, expected, font)
                a = Image.open(actual).convert('RGB')
                b = Image.open(expected).convert('RGB')
                delta = ImageChops.difference(a, b)
                full_mae = sum(ImageStat.Stat(delta).mean) / 3
                channels = b.crop((0, 960, 1920, 1080)).split()
                mask = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2]).point(lambda v: 255 if v > 180 else 0)
                caption_mae = sum(ImageStat.Stat(delta.crop((0, 960, 1920, 1080)), mask).mean) / 3
                assert full_mae < 4 and caption_mae < 12, (cue['cue'], full_mae, caption_mae)
                frames.append({**row, 'scene_id': scene['id'], 'required_labels': cue['required_labels'],
                    'full_frame_mean_absolute_error_0_255': round(full_mae, 4),
                    'caption_foreground_mean_absolute_error_0_255': round(caption_mae, 4),
                    'inside_actual_cue': True})
    intervals = extraction['pixel_comparisons']
    assert len(intervals) == 23 and max(r['mean_absolute_error_255'] for r in intervals) < 4
    source_report = {'passed': True, 'method': 'Numerical source comparison only; intact fitted source rectangle versus actual H264 interval frame.',
        'video_sha256': master_sha, 'intervals_checked': len(intervals),
        'maximum_application_mean_absolute_pixel_error_0_255': max(r['mean_absolute_error_255'] for r in intervals),
        'extraction_file': manifest.relative_to(S).as_posix(), 'extraction_sha256': sha(manifest), 'frames': intervals}
    cue_report = {'passed': True, 'method': 'All actual 30fps cue-midpoint JPEGs versus exact frozen source/header/burned caption composition. No inferred visual or human listening approval.',
        'video_sha256': master_sha, 'cues_checked': len(frames),
        'maximum_full_frame_mean_absolute_error_0_255': max(r['full_frame_mean_absolute_error_0_255'] for r in frames),
        'maximum_caption_foreground_mean_absolute_error_0_255': max(r['caption_foreground_mean_absolute_error_0_255'] for r in frames),
        'frames': frames, 'full_width_caption_strips': extraction['caption_reading_sheets']}
    for output, document in zip(outputs, (source_report, cue_report)):
        with output.open('x') as stream:
            stream.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': True, 'intervals': len(intervals), 'cues': len(frames),
        'max_source_mae': source_report['maximum_application_mean_absolute_pixel_error_0_255'],
        'max_frame_mae': cue_report['maximum_full_frame_mean_absolute_error_0_255'],
        'max_caption_mae': cue_report['maximum_caption_foreground_mean_absolute_error_0_255']}))


if __name__ == '__main__':
    main()
