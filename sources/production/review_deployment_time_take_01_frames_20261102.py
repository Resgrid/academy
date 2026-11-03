"""Extract actual department-administration frames and technical pixel checks.

This does not create a visual approval, hearing receipt or browser proof. All
actual source/master bytes remain intact. Full-width footer sheets are labeled
QA reading aids; they are not application screenshots or publication evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
CONFIG = {'time': ('core-deployment-time-expenses', 'core-deployment-time-expenses-take-01', 'expansion/plans/core-deployment-time-expenses-source-20261102-v2/lesson.candidate.json', 'expansion/plans/core-deployment-time-expenses-take-01-final-inputs-20261102/plan.json', 80)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=CONFIG, required=True)
    parser.add_argument('--master-sha256', required=True)
    parser.add_argument('--ffmpeg', required=True)
    args = parser.parse_args()
    name, take_name, source, plan, count = CONFIG[args.lesson]
    take = S / 'expansion/rendered' / take_name
    master = take / (name + '.mp4')
    require(len(args.master_sha256) == 64 and sha(master) == args.master_sha256, 'Wrong actual master identity.')
    assembly = json.loads((take / 'assembly.json').read_text())
    evidence = json.loads((take / 'evidence.pending.json').read_text())
    require(assembly['outputs']['video']['sha256'] == evidence['video']['sha256'] == args.master_sha256, 'Assembly/evidence/master mismatch.')
    from PIL import Image, ImageChops, ImageDraw, ImageStat
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import validate_inputs, load_cues, timeline, make_frame
    recipe = validate_inputs(S / source, S / plan, S)
    cues = load_cues(take / (name + '.srt'))
    require(len(cues) == count, 'Wrong actual caption count.')
    entries = timeline(recipe)
    shots = {row['id']: row for row in evidence['screenshots']}
    output = take / 'frame-qa'
    require(not output.exists(), 'New-only frame extraction; preserve prior outputs.')
    output.mkdir()
    numbers = [round((cue['start'] + cue['end']) / 2 * 30) for cue in cues]
    require(len(set(numbers)) == count, 'Two cues selected the same actual frame.')
    select = '+'.join('eq(n\\,' + str(number) + ')' for number in numbers)
    subprocess.run([args.ffmpeg, '-nostdin', '-v', 'error', '-i', str(master), '-vf', 'select=' + select,
        '-fps_mode', 'vfr', '-frames:v', str(count), '-q:v', '2', str(output / 'cue-%04d.jpg')], check=True)
    interval_checks, caption_checks, frame_rows = [], [], []
    for segment in assembly['rendered_segments']:
        row = shots[segment['screenshot_id']]
        actual = Image.open(S / segment['frame']['file']).convert('RGB')
        original = Image.open(S / row['file']).convert('RGB')
        require(original.size == (row['width'], row['height']) and actual.size == (1920, 1080), 'Changed actual image dimensions.')
        layout = assembly['screenshots'][segment['screenshot_id']]['layout']
        require(layout['cropped'] is False, 'Source screenshot was cropped.')
        box = (layout['x'], layout['y'], layout['x'] + layout['width'], layout['y'] + layout['height'])
        difference = ImageChops.difference(original.resize((layout['width'], layout['height']), Image.Resampling.LANCZOS), actual.crop(box))
        mean = sum(ImageStat.Stat(difference).mean) / 3
        interval_checks.append({'source_id': row['id'], 'source_sha256': row['sha256'], 'frame': segment['frame']['file'],
            'frame_sha256': sha(S / segment['frame']['file']), 'application_mean_absolute_pixel_error_0_255': mean,
            'fitted_region': layout, 'actual_source_intact': True})
    with tempfile.TemporaryDirectory(prefix='academy-three-core-frame-compare-') as temporary:
        expected_path = Path(temporary) / 'expected.png'
        for index, (cue, number) in enumerate(zip(cues, numbers), 1):
            at = number / 30
            require(cue['start'] <= at < cue['end'], 'Actual selected frame falls outside the real cue.')
            path = output / f'cue-{index:04}.jpg'
            actual = Image.open(path).convert('RGB')
            require(actual.size == (1920, 1080), 'Wrong actual cue frame dimensions.')
            entry = next(row for row in entries if row['start'] <= at < row['end'])
            require(entry['caption'] == cue['text'], 'Selected actual frame uses another speech cue.')
            make_frame(recipe, entry, expected_path, Path(assembly['font']['file']))
            expected = Image.open(expected_path).convert('RGB')
            difference = ImageChops.difference(expected, actual)
            full_mean = sum(ImageStat.Stat(difference).mean) / 3
            caption_box = (0, 960, 1920, 1080)
            delta = difference.crop(caption_box)
            mask = expected.crop(caption_box).convert('L').point(lambda value: 255 if value > 180 else 0)
            require(mask.getbbox() is not None, 'Expected real caption has no foreground text.')
            foreground = sum(ImageStat.Stat(delta, mask).mean) / 3
            frame_rows.append({'cue': index, 'file': path.relative_to(S).as_posix(), 'sha256': sha(path), 'width': 1920, 'height': 1080,
                'actual_frame_number': number, 'actual_time': at, 'requested_midpoint': (cue['start'] + cue['end']) / 2,
                'caption_text': cue['text'], 'source_id': entry['screenshot_id'], 'video_sha256': args.master_sha256,
                'visual_review_status': 'pending_personal_inspection'})
            caption_checks.append({'cue': index, 'actual_frame_number': number, 'actual_time': at, 'source_id': entry['screenshot_id'],
                'full_frame_mean_absolute_pixel_error_0_255': full_mean, 'caption_foreground_mean_absolute_pixel_error_0_255': foreground,
                'method': 'Actual decoded JPEG compared with expected intact-source/header/caption raster from pinned renderer; compression metrics are not visual/semantic approval.'})
    sheets = []
    for start in range(0, count, 6):
        group = frame_rows[start:start + 6]
        sheet = Image.new('RGB', (1920, 160 * len(group)), (30, 38, 50))
        draw = ImageDraw.Draw(sheet)
        for offset, row in enumerate(group):
            draw.text((16, offset * 160 + 8), f"Cue {row['cue']:03} | actual encoded frame {row['actual_frame_number']} at {row['actual_time']:.6f}s", fill='white')
            actual = Image.open(S / row['file']).convert('RGB')
            sheet.paste(actual.crop((0, 960, 1920, 1080)), (0, offset * 160 + 40))
        path = output / f'caption-sheet-{start // 6 + 1:02}.png'
        sheet.save(path)
        sheets.append({'file': path.relative_to(S).as_posix(), 'sha256': sha(path), 'cues': [row['cue'] for row in group],
            'kind': 'QA_only_unscaled_actual_encoded_caption_footer_strips'})
    interval_sheets = []
    for first in range(0, len(assembly['rendered_segments']), 4):
        canvas = Image.new('RGB', (1920, 1152), '#dbeafe')
        draw = ImageDraw.Draw(canvas)
        for offset, segment in enumerate(assembly['rendered_segments'][first:first + 4]):
            x, y = (offset % 2) * 960, (offset // 2) * 576
            draw.text((x + 8, y + 8), f"Interval{first + offset + 1:02} scene{segment['scene_id']} {segment['screenshot_id']}", fill='#111827')
            picture = Image.open(S / segment['frame']['file']).convert('RGB').resize((960, 540), Image.Resampling.LANCZOS)
            canvas.paste(picture, (x, y + 36))
        path = output / f'interval-sheet-{first // 4 + 1:02}.jpg'
        canvas.save(path, quality=95)
        interval_sheets.append({'file': path.relative_to(S).as_posix(), 'sha256': sha(path), 'first_interval': first + 1, 'count': min(4, len(assembly['rendered_segments']) - first), 'kind': 'QA_only_actual_encoded_interval_contact_sheet'})
    source_max = max(row['application_mean_absolute_pixel_error_0_255'] for row in interval_checks)
    full_max = max(row['full_frame_mean_absolute_pixel_error_0_255'] for row in caption_checks)
    caption_max = max(row['caption_foreground_mean_absolute_pixel_error_0_255'] for row in caption_checks)
    require(source_max < 6 and full_max < 6 and caption_max < 15, 'Actual decoded pixels differ materially; inspect before any review.')
    common = {'video_sha256': args.master_sha256, 'visual_approval_inferred': False, 'browser_playback_inferred': False, 'publication_approved': False}
    write_json(take / 'frame-source-comparison.json', {**common, 'passed': True, 'intervals_checked': len(interval_checks),
        'maximum_application_mean_absolute_pixel_error_0_255': source_max, 'checks': interval_checks})
    write_json(take / 'cue-frame-check.json', {**common, 'passed': True, 'cues_checked': count,
        'maximum_full_frame_mean_absolute_error_0_255': full_max, 'maximum_caption_foreground_mean_absolute_error_0_255': caption_max,
        'full_width_caption_strips': sheets, 'checks': caption_checks})
    write_json(output / 'extraction-and-pixel-metrics.json', {**common, 'kind': 'Actual encoded frame/caption QA inputs; personal review pending',
        'actual_interval_frames': len(interval_checks), 'actual_cue_frames': count, 'cue_frames': frame_rows,
        'caption_reading_sheets': sheets, 'interval_contact_sheets': interval_sheets, 'source_file': source, 'plan_file': plan,
        'source_sha256': sha(S / source), 'plan_sha256': sha(S / plan), 'recipe_sha256': sha(__file__)})
    print(json.dumps({'actual_extraction_and_pixel_checks_passed': True, 'lesson': name, 'intervals': len(interval_checks),
        'cues': count, 'caption_sheets': len(sheets), 'source_max_mae': source_max, 'cue_max_mae': full_max,
        'caption_foreground_max_mae': caption_max, 'personal_review': 'pending', 'browser_playback': 'pending'}))


if __name__ == '__main__':
    main()
