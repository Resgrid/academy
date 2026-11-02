"""Validate a portable static tutorial site before GitHub Pages deployment."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from media_delivery import asset_name, release_base

GITHUB_SITE_LIMIT = 1_000_000_000
GITHUB_FILE_LIMIT = 100 * 1024 * 1024
TEXT_TYPES = {'.html', '.json', '.txt', '.csv', '.srt', '.vtt', '.css', '.js', '.svg'}
FORBIDDEN_PARTS = {'local-stack', 'private', '.git', '.github', '__pycache__', 'build', 'descript'}
ACADEMY_PRODUCTION_PATTERN = re.compile(r'Warm\s+Lulu|illustrated\s+draft|live\s+(?:screen\s+)?walkthrough\s+pending|human\s+listening\s+review\s+(?:remains\s+)?pending|remaining\s+detailed\s+production|narrated\s+revision[^\n]{0,40}in\s+production', re.I)
PRIVATE_PATTERN = re.compile(r'https?://(?:web|share)\.descript\.com|https?://(?:127\.0\.0\.1|localhost)(?=[:/\s])|/Users/|[?&](?:X-Goog-Signature|X-Amz-Signature|access_token|sig)=', re.I)


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.tags = set()
        self.video_sources = []

    def handle_starttag(self, tag, attributes):
        self.tags.add(tag)
        values = dict(attributes)
        if tag in {'video', 'source'} and values.get('src'):
            self.video_sources.append(values['src'])
        if values.get('id'):
            self.ids.add(values['id'])
        for key in ('href', 'src', 'poster'):
            if values.get(key):
                self.links.append(values[key])


def local_target(root, page, reference):
    parsed = urlsplit(reference)
    if parsed.scheme in ('https', 'http', 'mailto', 'tel', 'data'):
        return None
    if parsed.scheme or parsed.netloc or reference.startswith('/'):
        raise ValueError('Site URLs must be relative so repository paths and custom domains both work.')
    target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        raise ValueError('Link escapes the published site.')
    if target.is_dir():
        target = target / 'index.html'
    return target


def validate(root, *, pages_size_limit=True):
    root = Path(root).resolve()
    issues, records = [], []
    pages = {}
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if path.is_symlink():
            issues.append(f'Symlink is not publishable: {relative}')
            continue
        if not path.is_file():
            continue
        if set(relative.parts) & FORBIDDEN_PARTS or path.suffix in {'.py', '.env', '.pem', '.pfx', '.key', '.zip', '.log'}:
            issues.append(f'Non-site file: {relative}')
        if path.stat().st_size >= GITHUB_FILE_LIMIT:
            issues.append(f'File exceeds GitHub regular-file limit: {relative}')
        records.append({'path': relative.as_posix(), 'bytes': path.stat().st_size})
        if path.suffix in TEXT_TYPES:
            text = path.read_text(encoding='utf-8')
            if ACADEMY_PRODUCTION_PATTERN.search(text):
                issues.append(f'Academy production label in public content: {relative}')
            if PRIVATE_PATTERN.search(text):
                issues.append(f'Private editor link, local address or temporary signed URL: {relative}')
            if path.suffix == '.html':
                parser = PageLinks()
                parser.feed(text)
                pages[path] = parser
    for page, parser in pages.items():
        for reference in parser.links:
            try:
                target = local_target(root, page, reference)
                if target is not None and not target.is_file():
                    issues.append(f'Missing local link in {page.relative_to(root)}: {reference}')
                elif target in pages and urlsplit(reference).fragment and unquote(urlsplit(reference).fragment) not in pages[target].ids:
                    issues.append(f'Missing chapter anchor in {page.relative_to(root)}: {reference}')
            except ValueError as error:
                issues.append(f'{page.relative_to(root)}: {error}')
    total = sum(row['bytes'] for row in records)
    if pages_size_limit and total >= GITHUB_SITE_LIMIT:
        issues.append('Site exceeds the GitHub Pages 1 GB limit; move media to a CDN before deployment.')
    if not (root / 'index.html').is_file():
        issues.append('The published site needs index.html at its root.')
    manifest_path = root / 'site-manifest.json'
    if not manifest_path.is_file():
        issues.append('Missing media manifest.')
    else:
        manifest = json.loads(manifest_path.read_text())
        remote_media = manifest.get('format_version') == 3
        listed = {item['path'] for item in manifest.get('media', [])}
        actual = {row['path'] for row in records if Path(row['path']).suffix.lower() in {'.mp4', '.webm'}}
        release_urls = set()
        if remote_media:
            delivery = manifest.get('media_delivery', {})
            try:
                if delivery.get('kind') != 'github_release':
                    raise ValueError('Unsupported external media delivery.')
                base = release_base(delivery.get('repository'), delivery.get('tag'))
                for item in manifest.get('media', []):
                    expected = base + '/' + asset_name(item['path'], item['sha256'])
                    if item.get('url') != expected or type(item.get('bytes')) is not int or item['bytes'] <= 0:
                        raise ValueError('Release media URL, size or hash is invalid.')
                    release_urls.add(expected)
            except (KeyError, TypeError, ValueError) as error:
                issues.append('Invalid Release media manifest: ' + str(error))
            if actual:
                issues.append('Release delivery bundle must not contain local videos.')
            if {lesson.get('video') for lesson in manifest.get('lessons', [])} != release_urls:
                issues.append('Release media manifest differs from the lesson inventory.')
            for parser in pages.values():
                if any(reference not in release_urls for reference in parser.video_sources):
                    issues.append('A video player uses an unlisted Release asset.')
        elif actual != listed:
            issues.append('Published videos differ from the media manifest.')
        if not remote_media and manifest.get('lessons') and {urlsplit(lesson['video']).path for lesson in manifest['lessons']} != listed:
            issues.append('Media manifest differs from the lesson inventory.')
        for item in manifest.get('media', []):
            if remote_media:
                continue
            try:
                path = local_target(root, root / 'index.html', item['path'])
                if path is None or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                    issues.append(f'Missing or changed media: {item["path"]}')
            except ValueError:
                issues.append('Invalid media manifest path.')
        for lesson in manifest.get('lessons', []):
            for key in ('video', 'poster', 'captions', 'chapters'):
                if not lesson.get(key):
                    issues.append(f'Missing {key} reference: {lesson["id"]}')
                    continue
                if remote_media and key == 'video':
                    if lesson[key] not in release_urls:
                        issues.append(f'Unlisted Release video: {lesson["id"]}')
                    continue
                target = local_target(root, root / 'index.html', lesson[key])
                if target is None or not target.is_file():
                    issues.append(f'Missing lesson asset: {lesson["id"]} {key}')
        course = json.loads((root / 'course.json').read_text()) if (root / 'course.json').is_file() else {}
        topic_guides = manifest.get('topic_guides', [])
        if manifest.get('format_version', 1) >= 2:
            if not isinstance(topic_guides, list) or manifest.get('topic_guide_count') != len(course.get('lessons', [])):
                issues.append('Topic guide count differs from the public course.')
                topic_guides = []
            guide_ids = [item.get('id') for item in topic_guides]
            if len(set(guide_ids)) != len(guide_ids) or set(guide_ids) != {item.get('id') for item in course.get('lessons', [])}:
                issues.append('Topic guide inventory differs from the public course.')
            if any(item.get('kind') not in {'actual application walkthrough', 'Video walkthrough'} for item in manifest.get('lessons', [])):
                issues.append('Only actual application walkthroughs belong in the video inventory.')
            for guide in topic_guides:
                if guide.get('kind') != 'topic_guide' or any(key in guide for key in ('video', 'poster', 'captions', 'chapters', 'subtitle')):
                    issues.append(f'Topic guide cannot expose illustrated media: {guide.get("id")}')
                for key in ('href', 'transcript'):
                    if not guide.get(key):
                        issues.append(f'Missing topic guide {key}: {guide.get("id")}')
                        continue
                    try:
                        target = local_target(root, root / 'index.html', guide[key])
                        if target is None or not target.is_file():
                            issues.append(f'Missing topic guide {key}: {guide.get("id")}')
                        elif key == 'href' and target in pages and pages[target].tags & {'video', 'track'}:
                            issues.append(f'Topic guide contains a media player: {guide.get("id")}')
                    except ValueError:
                        issues.append(f'Invalid topic guide {key}: {guide.get("id")}')
        for lesson in course.get('lessons', []):
            if manifest.get('format_version', 1) >= 2:
                if lesson.get('kind') != 'topic_guide' or any(key in lesson for key in ('video', 'poster', 'subtitle', 'duration_seconds')):
                    issues.append(f'Public topic content cannot expose a primer player: {lesson["id"]}')
                if lesson['id'] in {item.get('id') for item in manifest.get('lessons', [])}:
                    issues.append(f'Topic guide is incorrectly listed as a video: {lesson["id"]}')
                for suffix in ('.mp4', '.webm', '.vtt', '.srt', '.chapters.json'):
                    if (root / 'media' / (lesson['id'] + suffix)).exists():
                        issues.append(f'Illustrated primer asset is not public: {lesson["id"]}{suffix}')
            for key in ('video', 'poster', 'subtitle'):
                if lesson.get(key):
                    target = local_target(root, root / 'index.html', lesson[key])
                    if target is None or not target.is_file():
                        issues.append(f'Missing dynamic player asset: {lesson["id"]} {key}')
            script = root / 'scripts' / f'{lesson["id"]}.txt'
            if not script.is_file():
                issues.append(f'Missing lesson script: {lesson["id"]}')
        for feature in course.get('features', []):
            if not (root / 'scripts' / f'feature-{feature["id"]}.txt').is_file():
                issues.append(f'Missing feature brief: {feature["id"]}')
    local_videos = sum(Path(row['path']).suffix.lower() in {'.mp4', '.webm'} for row in records)
    remote_videos = len(release_urls) if manifest_path.is_file() and remote_media else 0
    return {'passed': not issues, 'files': len(records), 'bytes': total,
            'video_files': local_videos + remote_videos, 'local_video_files': local_videos,
            'release_video_files': remote_videos, 'pages_size_limit_enforced': pages_size_limit,
            'html_pages': len(pages), 'relative_links_checked': True,
            'private_links_and_local_addresses': 'excluded' if not any('Private editor' in x for x in issues) else 'found',
            'issues': sorted(set(issues))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site', default='site')
    parser.add_argument('--report')
    args = parser.parse_args()
    result = validate(args.site)
    if args.report:
        report = Path(args.report)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
