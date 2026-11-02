"""Make still layout previews; these are not encoded-video evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'app-ic-call-context-readiness-review'
P = S / 'expansion/plans' / (NAME + '-cue-map-proposal-20261101')
OUT = S / 'expansion/plans' / (NAME + '-layout-preview-20261101')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from PIL import Image, ImageDraw, ImageFont
    from render_walkthrough import caption_wrap, find_font, layout, make_frame, WIDTH
    data = json.loads((P / 'correspondence.proposed.json').read_text())
    manifest = json.loads((P / 'captures.source-relative.json').read_text())
    rows = {row['id']: row for row in manifest['screenshots']}
    for row in rows.values():
        assert sha(S / row['file']) == row['sha256']
    recipe = {'screenshots': {ident: {'path': S / row['file'], 'layout': layout(row['width'], row['height'])}
                              for ident, row in rows.items()},
              'plan': {'display_context': 'TRAINING ONLY · fictional department'}}
    font = find_font()
    draw = ImageDraw.Draw(Image.new('RGB', (1920, 1080)))
    caption_font = ImageFont.truetype(str(font), 30)
    measures = [{'cue': row['cue'], 'lines': caption_wrap(draw, row['text'], caption_font, WIDTH - 120)}
                for row in data['cues']]
    report = {'created_at': datetime.now(timezone.utc).isoformat(),
              'kind': 'unencoded_still_layout_preview', 'lesson_id': NAME,
              'correspondence_sha256': sha(P / 'correspondence.proposed.json'),
              'caption_layout_measured': len(measures), 'max_caption_lines': max(len(row['lines']) for row in measures),
              'cue_layouts': measures, 'preview_frames': [],
              'complete_audio_decode_review': False, 'listening_review': False,
              'actual_encoded_frame_review': False, 'browser_playback_review': False,
              'export_ready': False}
    if write:
        assert not OUT.exists(), 'New-only layout previews.'
        OUT.mkdir()
        scenes = {scene['id']: scene for scene in data['scenes']}
        for index, hold in enumerate(data['holds'], 1):
            cue = next(row for row in data['cues'] if hold['first_cue'] <= row['cue'] <= hold['last_cue'] and row['required_labels'])
            dest = OUT / f'{index:02}-cue-{cue["cue"]:03}.png'
            make_frame(recipe, {'screenshot_id': hold['screenshot_id'], 'title': scenes[hold['scene_id']]['title'],
                                'caption': cue['text']}, dest, font)
            report['preview_frames'].append({'file': dest.relative_to(S).as_posix(), 'sha256': sha(dest),
                                            'scene_id': hold['scene_id'], 'source_screenshot_id': hold['screenshot_id'],
                                            'cue': cue['cue'], 'encoded_video_frame': False})
        (OUT / 'layout-preview-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'passed': True, 'written': write, 'measured_cues': len(measures), 'max_lines': report['max_caption_lines'],
            'still_previews': len(report['preview_frames']), 'encoded_video_or_review_claim': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    print(json.dumps(prepare(parser.parse_args().write), indent=2))
