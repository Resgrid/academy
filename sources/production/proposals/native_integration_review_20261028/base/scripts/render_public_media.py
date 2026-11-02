"""Refresh primer graphics and remove editorial closing lines using existing narration.

Needs Pillow and FFmpeg. Original exported narration remains in sources/production/.
Run this after assembling primer audio, then run scripts/build.py to publish the site.
"""
import argparse
import concurrent.futures
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TAIL = 'Use the linked feature scripts for the detailed screen recording plan.'
INTRO_TAIL = 'These illustrated lessons are based on the current source.'


def seconds(value):
    hours, minutes, secs = value.replace(',', '.').split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(secs)


def stamp(value, comma=False):
    milliseconds = round(value * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02}{"," if comma else "."}{milliseconds:03}'


def parse_captions(text):
    cues = []
    for block in re.split(r'\n\s*\n', text.strip()):
        lines = block.splitlines()
        timing = next((index for index, line in enumerate(lines) if ' --> ' in line), None)
        if timing is None:
            continue
        start, end = lines[timing].split(' --> ')
        cues.append({'start': seconds(start), 'end': seconds(end), 'text': ' '.join(lines[timing + 1:])})
    return cues


def publication_cut(ident, cues, duration):
    target = INTRO_TAIL if ident == '00-start' else TAIL
    for index in range(len(cues)):
        # Remove complete closing caption cues only; never cut a spoken word mid-cue.
        remaining = ' '.join(cue['text'] for cue in cues[index:])
        if remaining.startswith(target) and index:
            last = cues[index - 1]
            silence = max(0, cues[index]['start'] - last['end'])
            return round(last['end'] + min(.25, silence / 2), 3), cues[:index]
    return duration, cues


def render(root, ffmpeg, workers=3, only=None):
    source = root / 'sources'
    sys.path.insert(0, str(source / 'production'))
    spec = importlib.util.spec_from_file_location('academy_illustrations', source / 'production/render.py')
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    from PIL import Image
    course_path = source / 'course.json'
    course = json.loads(course_path.read_text())
    lessons = [lesson for lesson in course['lessons'] if not only or lesson['id'] in only]
    def one(lesson):
        ident = lesson['id']
        movie = source / 'media' / (ident + '.mp4')
        captions = parse_captions((source / 'media' / (ident + '.srt')).read_text())
        chapters = json.loads((source / 'media' / (ident + '.chapters.json')).read_text())
        end, cues = publication_cut(ident, captions, chapters[-1]['end'])
        chapters[-1]['end'] = end
        with tempfile.TemporaryDirectory(prefix='academy-media-') as directory:
            working = Path(directory)
            slides = source / 'production/descript/slides'
            slides.mkdir(parents=True, exist_ok=True)
            files = []
            for index, scene in enumerate(lesson['scenes']):
                slide = slides / f'{ident}-slide-{index+1:02}.png'
                renderer.image_for(lesson, scene, index, len(lesson['scenes']), slide)
                files += ["file '" + slide.as_posix().replace("'", "'\\''") + "'", 'duration ' + str(chapters[index]['end'] - chapters[index]['start'])]
            files.append(files[-2])
            listing = working / 'images.txt';listing.write_text('\n'.join(files) + '\n')
            srt = ''.join(f'{index}\n{stamp(cue["start"], True)} --> {stamp(cue["end"], True)}\n{cue["text"]}\n\n' for index, cue in enumerate(cues, 1))
            subtitle = working / 'captions.srt';subtitle.write_text(srt)
            metadata = ';FFMETADATA1\ntitle=' + lesson['title'].replace('=', '-') + '\ncomment=Resgrid Academy video lesson\n'
            for chapter in chapters:
                metadata += f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(chapter["start"]*1000)}\nEND={round(chapter["end"]*1000)}\ntitle={chapter["title"].replace("=", "-")}\n'
            meta = working / 'chapters.txt';meta.write_text(metadata)
            output = working / 'published.mp4'
            command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing), '-i', str(movie), '-i', str(subtitle), '-f', 'ffmetadata', '-i', str(meta), '-map', '0:v:0', '-map', '1:a:0', '-map', '2:0', '-map_metadata', '3', '-map_chapters', '3', '-t', str(end), '-r', '30', '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage', '-crf', '20', '-threads', '2', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-c:s', 'mov_text', '-metadata:s:s:0', 'language=eng', '-movflags', '+faststart', str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(ident + ': ' + result.stderr[-2500:])
            # Decode the complete video and audio before replacing the canonical public master.
            result = subprocess.run([ffmpeg, '-v', 'error', '-i', str(output), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-'], capture_output=True, text=True)
            if result.returncode or result.stderr:
                raise RuntimeError(ident + ': decode failed: ' + result.stderr[-2500:])
            movie.write_bytes(output.read_bytes())
            Image.open(slides / f'{ident}-slide-01.png').resize((960, 540)).save(source / 'media' / (ident + '.jpg'), quality=88)
            (source / 'media' / (ident + '.srt')).write_text(srt)
            vtt = 'WEBVTT\n\n' + ''.join(f'{stamp(cue["start"])} --> {stamp(cue["end"])}\n{cue["text"]}\n\n' for cue in cues)
            (source / 'media' / (ident + '.vtt')).write_text(vtt)
            (source / 'media' / (ident + '.chapters.json')).write_text(json.dumps(chapters, indent=2) + '\n')
            lesson['duration_seconds'] = end
            last = lesson['scenes'][-1]
            last['duration_seconds'] = end - last['start_seconds']
            if ident == '00-start':
                last['narration'] = last['narration'].split(INTRO_TAIL)[0].strip()
            else:
                last['narration'] = last['narration'].replace(TAIL, '').strip()
        print(f'Updated {ident}: {end:.1f}s; complete decode passed; existing narration retained', flush=True)
        return {'id': ident, 'duration_seconds': end, 'caption_cues': len(cues), 'full_decode': 'passed', 'narration': 'existing audio copied'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one, lessons))
    course_path.write_text(json.dumps(course, ensure_ascii=False, indent=2) + '\n')
    report = root / '_reports/public-media.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({'lessons': results}, indent=2) + '\n')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', required=True)
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--lesson', action='append')
    args = parser.parse_args()
    render(Path(__file__).resolve().parents[1], args.ffmpeg, args.workers, args.lesson)
