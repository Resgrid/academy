"""Export approved tutorial media into a separate, portable GitHub Pages repository."""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from validate_site import PRIVATE_PATTERN, validate
from public_site import learner_course, write_public_site

PRIVATE_KEYS = {'descript_project', 'private_preview', 'editor_url', 'project_url'}


def public_data(value):
    if isinstance(value, dict):
        return {key: public_data(item) for key, item in value.items()
                if key not in PRIVATE_KEYS and not (isinstance(item, str) and PRIVATE_PATTERN.search(item))}
    if isinstance(value, list):
        return [public_data(item) for item in value if not (isinstance(item, str) and PRIVATE_PATTERN.search(item))]
    return value


def public_html(text):
    # Private narration compositions and the running demo stay in the local review library.
    text = re.sub(r'(?: · )?<a\b[^>]*href="https://(?:web|share)\.descript\.com/[^\"]+"[^>]*>.*?</a>', '', text, flags=re.S)
    text = re.sub(r'<a\b[^>]*href="http://127\.0\.0\.1:[^\"]+"[^>]*>.*?</a>\s*(?:·\s*)?', '', text, flags=re.S)
    text = re.sub(r'<p>The local stack configuration and credentials.*?</p>', '<p>These videos and screenshots use fictional Firehouse 51 training data.</p>', text, flags=re.S)
    return text


def export(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Export to a separate directory, outside the source review package.')
    if destination.exists() and not (destination / 'site-manifest.json').is_file():
        raise ValueError('Refusing to replace a directory without an Academy site manifest.')
    course = learner_course(public_data(json.loads((source / 'course.json').read_text())))
    for lesson in course['lessons']:
        for key in ('video', 'poster', 'subtitle'):
            path = urlsplit(lesson[key]).path
            original = source / path
            if original.is_symlink() or not original.is_file():
                raise ValueError('Missing or symlinked media asset: ' + path)
            lesson[key] = path + '?v=' + hashlib.sha256(original.read_bytes()).hexdigest()[:16]
    if course.get('narration_pilot'):
        course['narration_pilot']['video'] = course['lessons'][0]['video']
        course['narration_pilot']['subtitle'] = course['lessons'][0]['subtitle']
    detailed = json.loads((source / 'deep-dive/preparation-validation.json').read_text())
    ready = [lesson for lesson in detailed['lessons'] if lesson.get('browser_playback_review') == 'passed']
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.academy-export-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'site'
        staged.mkdir()

        def copy(relative, target_relative=None):
            original = source / relative
            target = staged / (target_relative or relative)
            if original.is_symlink() or not original.is_file():
                raise ValueError('Missing or symlinked website source: ' + relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if original.suffix == '.html':
                target.write_text(public_html(original.read_text()))
            elif original.suffix == '.json':
                target.write_text(json.dumps(public_data(json.loads(original.read_text())), ensure_ascii=False, indent=2) + '\n')
            elif original.suffix == '.vtt':
                target.write_text(re.sub(r'(?m)^NOTE[^\n]*(?:\n(?!\n)[^\n]*)*\n\n', '', original.read_text()))
            else:
                shutil.copy2(original, target)

        copy('index.html')
        (staged / 'course.json').write_text(json.dumps(course, ensure_ascii=False, indent=2) + '\n')
        for name in ('coverage.csv', 'settings.csv'):
            copy(name)
        for script in sorted((source / 'scripts').glob('*.txt')):
            copy(script.relative_to(source).as_posix())
        media_paths = set()
        for lesson in course['lessons']:
            media_paths.update([urlsplit(lesson['video']).path, urlsplit(lesson['poster']).path, urlsplit(lesson['subtitle']).path,
                f'media/{lesson["id"]}.srt', f'media/{lesson["id"]}.chapters.json'])
        for relative in sorted(media_paths):
            copy(relative)
        for name in ('index.html', 'sectors.html', 'course.json', 'sector-examples.json'):
            copy('deep-dive/' + name)
        for lesson in ready:
            ident = lesson['id']
            copy(f'deep-dive/media/{ident}.mp4')
            for asset in sorted((source / 'deep-dive/review' / ident).iterdir()):
                if (asset.suffix == '.jpg' and re.fullmatch(r'\d\d-\d\d\.jpg', asset.name)) or asset.name in {'index.html', 'captions.srt', 'captions.vtt', 'chapters.json'}:
                    copy(asset.relative_to(source).as_posix())
                    copy(asset.relative_to(source).as_posix(), f'deep-dive/lessons/{ident}/{asset.name}')
        for asset in sorted((source / 'captures/deep-dive').glob('*.jpg')):
            copy(asset.relative_to(source).as_posix())
        for asset in sorted((source / 'captures/firehouse51').iterdir()):
            if asset.suffix in {'.jpg', '.mp4', '.srt', '.vtt'} or asset.name in {'index.html', 'firehouse51-walkthrough.chapters.json'}:
                copy(asset.relative_to(source).as_posix())
        write_public_site(staged, source, course, ready)
        (staged / '.nojekyll').touch()
        lessons = []
        for lesson in course['lessons']:
            lessons.append({'id': lesson['id'], 'kind': 'illustrated primer', 'video': lesson['video'], 'poster': lesson['poster'], 'captions': lesson['subtitle'], 'chapters': f'media/{lesson["id"]}.chapters.json'})
        for lesson in ready:
            ident = lesson['id']
            lessons.append({'id': ident, 'kind': 'actual application walkthrough', 'video': f'deep-dive/media/{ident}.mp4', 'poster': f'deep-dive/lessons/{ident}/01-01.jpg', 'captions': f'deep-dive/lessons/{ident}/captions.vtt', 'chapters': f'deep-dive/lessons/{ident}/chapters.json'})
        lessons.append({'id': 'firehouse51-introduction', 'kind': 'actual application walkthrough', 'video': 'captures/firehouse51/firehouse51-walkthrough.mp4', 'poster': 'captures/firehouse51/01-dashboard.jpg', 'captions': 'captures/firehouse51/firehouse51-walkthrough.vtt', 'chapters': 'captures/firehouse51/firehouse51-walkthrough.chapters.json'})
        media = [{'path': path.relative_to(staged).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(staged.rglob('*.mp4'))]
        manifest = {'format_version': 1, 'site': 'Resgrid Academy', 'addressing': 'relative URLs; GitHub project paths and custom-domain roots supported', 'primers': len(course['lessons']), 'detailed_videos': len(ready), 'lessons': lessons, 'media': media, 'private_descript_links': 'excluded'}
        (staged / 'site-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        result = validate(staged)
        if not result['passed']:
            raise ValueError(json.dumps(result, indent=2))
        previous = Path(temporary) / 'previous'
        if destination.exists():
            destination.rename(previous)
        try:
            staged.rename(destination)
        except OSError:
            if previous.exists():
                previous.rename(destination)
            raise
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1] / 'sources')
    parser.add_argument('--destination', type=Path, default=Path(__file__).resolve().parents[1] / 'site')
    args = parser.parse_args()
    try:
        print(json.dumps(export(args.source, args.destination), indent=2))
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
