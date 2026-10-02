"""Import a local approved audio export and its speech-timed SRT; no service sign-in."""
import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=['primer', 'detailed'], required=True)
    parser.add_argument('--lesson', required=True)
    parser.add_argument('--audio', type=Path, required=True)
    parser.add_argument('--captions', type=Path, required=True)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / 'sources'
    course_file = root / ('course.json' if args.kind == 'primer' else 'deep-dive/course.json')
    known = {lesson['id'] for lesson in json.loads(course_file.read_text())['lessons']}
    if args.lesson not in known or not args.audio.is_file() or not args.captions.is_file():
        raise SystemExit('Choose an existing lesson and readable local audio/SRT files.')
    if '-->' not in args.captions.read_text():
        raise SystemExit('The caption input must be a speech-timed SRT export.')
    folder = root / ('production/descript/natural/audio' if args.kind == 'primer' else 'deep-dive/audio')
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as temporary:
        output = Path(temporary) / 'import.m4a'
        subprocess.run([args.ffmpeg, '-y', '-v', 'error', '-i', str(args.audio), '-map', '0:a:0', '-vn', '-c:a', 'aac', '-b:a', '192k', str(output)], check=True)
        information = subprocess.run([args.ffmpeg, '-hide_banner', '-i', str(output)], capture_output=True, text=True).stderr
        duration = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', information)
        if not duration:
            raise SystemExit('The imported audio duration could not be read.')
        seconds = int(duration[1]) * 3600 + int(duration[2]) * 60 + float(duration[3])
        output.replace(folder / (args.lesson + '.m4a'))
    captions = root / ('production/descript/natural/captions/' + args.lesson + '-raw.srt' if args.kind == 'primer' else 'deep-dive/' + args.lesson + '-raw.srt')
    shutil.copyfile(args.captions, captions)
    if args.kind == 'detailed':
        metadata = folder / 'sources.json'
        data = json.loads(metadata.read_text())
        data[args.lesson] = {'duration_seconds': seconds, 'voice': 'Warm Lulu', 'status': 'local approved export; render and speech checks required'}
        metadata.write_text(json.dumps(data, indent=2) + '\n')
    print('Imported local narration:', args.lesson, '— render and review before publication.')


if __name__ == '__main__':
    main()
