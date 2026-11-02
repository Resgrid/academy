"""Export verified app/configuration lessons without publishing production records.

Integration: ``write_expansion_site(destination, sources)`` returns learner card
metadata, or [] without creating navigation when nothing qualifies. This module
owns only destination/walkthroughs/. The caller adds navigation only for a
nonempty return value. No source JSON, capture URLs or review records are copied.
Video cards additionally return site-relative video, poster, captions and chapters
paths for the normal public media inventory. Chapters contain learner titles and
verified start times only; screenshot-guide cards have no video asset fields.

Every lesson needs ``export_ready: true``, ``publication_mode: "video"|"guide"``
and a source-relative ``evidence_file``. Video evidence uses the existing
verify_capture_evidence schema, including beginning/middle/end browser playback,
and adds ``authoring_sha256 = lesson_content_digest(lesson)``. Cached reports or
an author's playback-passed string cannot replace that validator.

Guide evidence is separate: {schema_version: 1, kind: "screenshot_guide",
lesson_id, screenshots: [the same actual-application screenshot records],
scenes: [{id, screens: [{screenshot_id, required_labels: [...]}]}],
guide_review: {passed: true, reviewed_at: ISO8601-with-timezone,
content_sha256: guide_review_digest(lesson, evidence)}}. All authoring scenes and
named controls must be covered. The review digest binds the current learner text,
ordered screen mappings and exact image records. A guide never acquires a player
or a video label, even if unverified media happens to exist nearby.

These are evidence-contract gates, not an image-recognition or browser service.
Actual capture/visual review and browser playback observations must be recorded
honestly upstream. Missing, stale, rejected or partial evidence fails closed.
Literal labels and icon-control accessible names stay separate. Icon names may
satisfy a step only through the verifier's fully visible DOM-control bounds and
hash-bound image review; guide_review must additionally bind that current source
evidence. Videos still require separate extracted-frame review and playback.
"""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import html
import ipaddress
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
from urllib.parse import unquote, urlsplit

from public_site import CSS
from academy_brand import brand_head, brand_header, brand_footer
from verify_capture_evidence import APPS, _Validator, _normalized, verify_document

OUTPUT_DIRECTORY = 'walkthroughs'
OWNED_MARKER = '<!-- Resgrid Academy verified walkthrough export -->'
IDENTIFIER = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
TOKEN = re.compile(r'\b(?:pk|sk)\.[A-Za-z0-9._-]{16,}|\bsk-[A-Za-z0-9_-]{16,}|'
                   r'\b(?:access_token|refresh_token|client_secret|api_key|password)\s*[=:]\s*\S+|'
                   r'\bBearer\s+[A-Za-z0-9._~-]+|[?&](?:X-Amz-Signature|X-Goog-Signature|sig)=', re.I)
PRIVATE_PATH = re.compile(r'file://|codex://|/Users/|/home/|/private/|[A-Za-z]:\\Users\\', re.I)
PRODUCTION_LABEL = re.compile(r'\b(?:draft|preview|in[- ]progress)\s+(?:video|lesson|walkthrough)\b|'
                              r'\b(?:video|lesson|walkthrough)\s+(?:draft|preview|in[- ]progress)\b|'
                              r'coming soon|capture pending|screen recording plan|in production|Warm Lulu|human listening review', re.I)
URL = re.compile(r'(?:https?://|//)[^\s<>"\']+', re.I)
SECTORS = ('Fire / EMS', 'Community response', 'Search and rescue', 'Security', 'Wildland', 'Industrial')


class PublicationError(ValueError):
    """The candidate is not safe and complete enough for learner export."""


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _assert_no_credentials(value):
    if isinstance(value, str) and TOKEN.search(unquote(value)):
        raise PublicationError('Credential or signed-token material is not publishable.')


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise PublicationError(field + ' must contain learner-facing text.')
    value = value.strip()
    _assert_no_credentials(value)
    decoded = unquote(value)
    if PRIVATE_PATH.search(decoded) or PRODUCTION_LABEL.search(decoded):
        raise PublicationError(field + ' contains private or production-only content.')
    for match in URL.finditer(decoded):
        try:
            parsed = urlsplit(match.group().rstrip('.,);]'))
            hostname = (parsed.hostname or '').lower().rstrip('.')
            if parsed.username or parsed.password or not hostname:
                raise PublicationError('URLs with credentials are not publishable.')
            if hostname == 'localhost' or hostname.endswith(('.localhost', '.local', '.internal', '.descript.com')) or hostname == 'descript.com':
                raise PublicationError('Private/editor URLs are not publishable.')
            try:
                address = ipaddress.ip_address(hostname)
            except ValueError:
                if '.' not in hostname:
                    raise PublicationError('Local URLs are not publishable.')
            else:
                if not address.is_global:
                    raise PublicationError('Local/private addresses are not publishable.')
        except ValueError as exc:
            raise PublicationError(field + ' contains an unsafe URL.') from exc
    return value


def _identifier(value, field):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise PublicationError(field + ' must be a portable lowercase identifier.')
    return value


def _strings(value, field, allow_empty=False):
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or not value and not allow_empty:
        raise PublicationError(field + ' must be nonempty.')
    return [_text(item, field) for item in value]


def _sector(name):
    name = name.casefold()
    for label, pattern in [
        ('Wildland', r'wildland|wildfire'), ('Industrial', r'industrial|plant'),
        ('Security', r'security'), ('Search and rescue', r'search|\bsar\b'),
        ('Community response', r'community|volunteer|paramedicine|mental health'),
        ('Fire / EMS', r'fire|\bems\b|emergency services'),
    ]:
        if re.search(pattern, name):
            return label
    raise PublicationError('Unrecognized department scenario sector.')


def _public_lesson(lesson):
    if not isinstance(lesson, dict):
        raise PublicationError('Lesson must be an object.')
    app = lesson.get('app')
    if not isinstance(app, str) or app not in APPS:
        raise PublicationError('Lesson must name a supported Resgrid app.')
    scenes = lesson.get('scenes')
    if not isinstance(scenes, list) or not scenes:
        raise PublicationError('Lesson needs complete scenes.')
    projected = []
    for scene in scenes:
        if not isinstance(scene, dict):
            raise PublicationError('Scene must be an object.')
        projected.append({
            'id': _identifier(scene.get('id'), 'Scene id'),
            'title': _text(scene.get('title'), 'Scene title'),
            'narration': _text(scene.get('narration'), 'Step explanation'),
            'practice': _text(scene.get('practice'), 'Practice scenario'),
            'required_labels': _strings(scene.get('required_labels'), 'Required controls'),
        })
    if len({item['id'] for item in projected}) != len(projected):
        raise PublicationError('Scene identifiers must be unique.')
    examples = lesson.get('sector_examples')
    if isinstance(examples, dict):
        examples = [{'sector': name, 'scenario': text} for name, text in examples.items()]
    if not isinstance(examples, list):
        raise PublicationError('Six department scenarios are required.')
    sectors = {}
    for example in examples:
        if not isinstance(example, dict):
            raise PublicationError('Sector example must be an object.')
        name = _text(example.get('sector'), 'Sector')
        canonical = _sector(name)
        if canonical in sectors:
            raise PublicationError('Each department sector needs one distinct example.')
        sectors[canonical] = _text(example.get('scenario'), 'Sector scenario')
    if set(sectors) != set(SECTORS):
        raise PublicationError('All six department sectors are required.')
    return {
        'id': _identifier(lesson.get('id'), 'Lesson id'), 'app': app,
        'title': _text(lesson.get('title'), 'Title'),
        'summary': _text(lesson.get('summary'), 'Summary'),
        'audience': _strings(lesson.get('audience'), 'Audience'),
        'prerequisites': _strings(lesson.get('prerequisites'), 'Prerequisites'),
        'scenes': projected, 'sector_examples': {name: sectors[name] for name in SECTORS},
    }


def _digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def lesson_content_digest(lesson):
    """Bind video evidence to exactly the learner content that will be exported."""
    return _digest(_public_lesson(lesson))


def guide_review_digest(lesson, evidence):
    """Compute the binding recorded only after reviewing all guide scenes/images."""
    return _digest({'lesson': _public_lesson(lesson), 'screenshots': evidence.get('screenshots'), 'scenes': evidence.get('scenes')})


def _asset(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise PublicationError('Asset path must be source-relative.')
    _assert_no_credentials(relative)
    decoded = unquote(unquote(relative))
    parts = PurePosixPath(decoded)
    if decoded != relative or parts.is_absolute() or urlsplit(relative).scheme or urlsplit(relative).netloc or '?' in relative or '#' in relative:
        raise PublicationError('Asset paths cannot be URLs or encoded paths.')
    if any(part in {'.', '..', 'private', '.git', 'node_modules'} or part.startswith('.env') for part in parts.parts):
        raise PublicationError('Unsafe or private asset path.')
    path = root.joinpath(*parts.parts)
    for candidate in [path, *path.parents]:
        if candidate == root:
            break
        if candidate.is_symlink():
            raise PublicationError('Symlinked assets are not publishable.')
    if root not in path.resolve().parents or not path.is_file() or path.stat().st_size == 0:
        raise PublicationError('Required asset is missing, empty or outside sources.')
    return path


def _read_json(root, relative):
    return json.loads(_asset(root, relative).read_text(encoding='utf-8'))


def _screenshots(evidence, root, primary_app=None):
    records = evidence.get('screenshots')
    if not isinstance(records, list) or not records:
        raise PublicationError('Actual application screenshots are required.')
    validator = _Validator(root)
    supporting = validator.supporting_applications(evidence.get('supporting_applications', []), primary_app)
    result = {}
    for index, shot in enumerate(records):
        if not isinstance(shot, dict):
            raise PublicationError('Malformed screenshot record.')
        ident = _identifier(shot.get('id'), 'Screenshot id')
        if ident in result or shot.get('accepted') is False or shot.get('publication_eligible') is False or shot.get('contains_private_ui') is True:
            raise PublicationError('Duplicate, rejected or private screenshot.')
        validator.application(shot, 'Screenshot ' + str(index), supporting)
        if shot.get('kind') != 'application_screenshot':
            raise PublicationError('Illustrations cannot replace real application screenshots.')
        _asset(root, shot.get('file'))
        validator.asset(shot, 'Screenshot ' + str(index), image=True)
        validator.accepted_image(shot, 'Screenshot ' + str(index))
        provenance = shot.get('provenance')
        if isinstance(provenance, dict) and provenance.get('method') == 'ios_simulator_screenshot':
            try:
                from native_capture_public import validate_native_source
                validate_native_source(shot, root, primary_app)
            except (ValueError, OSError, TypeError, KeyError) as exc:
                raise PublicationError(str(exc)) from exc
        else:
            if not isinstance(provenance, dict) or provenance.get('method') != 'browser_screenshot' or 'native_review_package' in shot:
                raise PublicationError('Screenshot needs actual browser provenance; native evidence cannot be relabeled.')
            _assert_no_credentials(provenance.get('url'))
            validator.url(provenance.get('url'), 'Capture URL')
        validator.timestamp(provenance.get('captured_at'), 'Capture time')
        observed = validator.observations(shot, 'Screenshot ' + str(index))
        labels = _strings(shot.get('visible_labels'), 'Visible labels', allow_empty=bool(shot.get('visible_controls')))
        for control in shot.get('visible_controls', []) if isinstance(shot.get('visible_controls', []), list) else []:
            if not isinstance(control, dict):
                raise PublicationError('Malformed accessible control observation.')
            _text(control.get('accessible_name'), 'Accessible control name')
        result[ident] = dict(shot, visible_labels=labels, _observed_names=observed)
    if validator.issues:
        raise PublicationError('; '.join(validator.issues))
    return result


def _scene_screens(public, evidence, screenshots, video=False):
    scenes = evidence.get('scenes')
    if not isinstance(scenes, list) or any(not isinstance(item, dict) for item in scenes):
        raise PublicationError('Complete scene-to-screen mappings are required.')
    if Counter(item.get('id') for item in scenes) != Counter(item['id'] for item in public['scenes']):
        raise PublicationError('Evidence must cover every current authoring scene exactly once.')
    result = {}
    starts = {}
    for scene in scenes:
        bindings = scene.get('screens')
        if not isinstance(bindings, list) or not bindings:
            raise PublicationError('Each scene needs actual screenshots.')
        ids, labels = [], set()
        for binding in bindings:
            if not isinstance(binding, dict) or binding.get('screenshot_id') not in screenshots:
                raise PublicationError('Scene references a missing screenshot.')
            ident = binding['screenshot_id']
            if ident not in ids:
                ids.append(ident)
            visible = screenshots[ident]['_observed_names']
            if not video:
                required = {_normalized(text) for text in _strings(binding.get('required_labels'), 'Guide frame controls')}
                if not required <= visible:
                    raise PublicationError('Required controls are absent from the actual screenshot.')
                if screenshots[ident]['app'] == public['app']:
                    labels.update(required)
        if video:
            primary_visible = set().union(*(screenshots[ident]['_observed_names'] for ident in ids if screenshots[ident]['app'] == public['app']))
            if 'visual_required_labels' in scene:
                labels.update(_normalized(text) for text in scene['visual_required_labels'] if _normalized(text) in primary_visible)
            else:
                for caption in scene.get('captions', []):
                    if screenshots.get(caption.get('screenshot_id'), {}).get('app') == public['app']:
                        labels.update(_normalized(text) for text in caption.get('required_labels', []))
            starts[scene['id']] = scene['start']
        authored = next(item for item in public['scenes'] if item['id'] == scene['id'])
        if not {_normalized(text) for text in authored['required_labels']} <= labels:
            raise PublicationError('Every named authoring control needs captured evidence.')
        result[scene['id']] = ids
    return result, starts


def verify_guide_document(lesson, evidence, asset_root):
    """Verify a separately reviewed screenshot guide, never infer readiness from files."""
    try:
        public = _public_lesson(lesson)
        if not isinstance(evidence, dict) or type(evidence.get('schema_version')) is not int or evidence.get('schema_version') != 1 or evidence.get('kind') != 'screenshot_guide' or evidence.get('lesson_id') != public['id']:
            raise PublicationError('Guide needs its own matching evidence document.')
        screenshots = _screenshots(evidence, Path(asset_root).resolve(), public['app'])
        _scene_screens(public, evidence, screenshots)
        review = evidence.get('guide_review')
        if not isinstance(review, dict) or review.get('passed') is not True or review.get('content_sha256') != guide_review_digest(lesson, evidence):
            raise PublicationError('Guide review is missing, stale or not passed.')
        reviewed = datetime.fromisoformat(str(review.get('reviewed_at', '')).replace('Z', '+00:00'))
        if reviewed.tzinfo is None:
            raise PublicationError('Guide review needs a timezone-aware timestamp.')
        for shot in screenshots.values():
            captured = datetime.fromisoformat(shot['provenance']['captured_at'].replace('Z', '+00:00'))
            if reviewed < captured:
                raise PublicationError('Guide review predates its screenshots.')
        return {'passed': True, 'lesson_id': public['id'], 'issues': []}
    except (ValueError, OSError, UnicodeError, TypeError, KeyError) as exc:
        return {'passed': False, 'lesson_id': lesson.get('id') if isinstance(lesson, dict) else None, 'issues': [str(exc)]}


def _prepare(lesson, root):
    public = _public_lesson(lesson)
    mode = lesson.get('publication_mode')
    if mode not in {'video', 'guide'}:
        raise PublicationError('Choose an explicit video or guide publication mode.')
    evidence = _read_json(root, lesson.get('evidence_file'))
    if not isinstance(evidence, dict) or evidence.get('lesson_id') != public['id']:
        raise PublicationError('Evidence must match this lesson.')
    screenshots = _screenshots(evidence, root, public['app'])
    if mode == 'video':
        if evidence.get('authoring_sha256') != lesson_content_digest(lesson):
            raise PublicationError('Video evidence does not bind the current learner content.')
        # Validate all assets before the existing validator; never trust a cached passed report.
        video = evidence.get('video')
        if not isinstance(video, dict):
            raise PublicationError('Assembled video evidence is missing.')
        path = _asset(root, video.get('file'))
        if path.suffix.lower() not in {'.mp4', '.webm'}:
            raise PublicationError('A real assembled MP4/WebM asset is required.')
        _asset(root, video.get('captions', {}).get('file'))
        for segment in evidence.get('rendered_segments', []):
            _asset(root, segment.get('frame', {}).get('file'))
        for sample in evidence.get('browser_playback', []):
            _asset(root, sample.get('screenshot', {}).get('file'))
        report = verify_document(evidence, root)
        if report.get('passed') is not True:
            raise PublicationError('Capture/playback validator failed: ' + '; '.join(report.get('issues', [])))
        # Captions are public text too. Reject unsafe cues before a candidate is
        # considered ready, rather than aborting a whole export while copying.
        _caption_bytes(_asset(root, video['captions']['file']))
        public['video'] = video
    else:
        report = verify_guide_document(lesson, evidence, root)
        if report['passed'] is not True:
            raise PublicationError('; '.join(report['issues']))
    public['screen_ids'], public['starts'] = _scene_screens(public, evidence, screenshots, video=mode == 'video')
    public['screenshots'], public['mode'] = screenshots, mode
    return public


def _collect(sources):
    root = Path(sources).resolve()
    ready, excluded = [], []
    for path in sorted((root / 'expansion/lessons').glob('*.json')):
        try:
            if path.is_symlink():
                raise PublicationError('Symlinked lesson source is not supported.')
            lesson = json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(lesson, dict) or lesson.get('export_ready') is not True:
                continue
            ready.append(_prepare(lesson, root))
        except (ValueError, OSError, UnicodeError, KeyError, TypeError, AttributeError) as exc:
            excluded.append({'id': path.stem, 'issues': [str(exc)]})
    duplicates = {ident for ident, count in Counter(item['id'] for item in ready).items() if count > 1}
    excluded.extend({'id': ident, 'issues': ['Duplicate ready lesson identifier.']} for ident in sorted(duplicates))
    return [item for item in ready if item['id'] not in duplicates], excluded


def readiness_report(sources):
    ready, excluded = _collect(sources)
    return {'ready': [item['id'] for item in ready], 'excluded': excluded}


def _esc(value):
    return html.escape(str(value), quote=True)


def _page(title, content, prefix):
    site_prefix = prefix + '../'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Learn Resgrid with practical app walkthroughs and configuration guides."><title>{_esc(title)} | Resgrid Academy</title>{brand_head(site_prefix)}<style>{CSS}</style></head><body>{OWNED_MARKER}<a class="skip" href="#main">Skip to content</a>{brand_header(site_prefix, expansion=True)}<main id="main">{content}</main>{brand_footer(site_prefix)}</body></html>'''


def _caption_bytes(path):
    text = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    blocks = [block for block in re.split(r'\n\s*\n', text.strip()) if not block.startswith('NOTE')]
    text = '\n\n'.join(blocks)
    if path.suffix.lower() == '.srt':
        text = 'WEBVTT\n\n' + re.sub(r'(\d{2}:\d{2}:\d{2}),(\d{3})', r'\1.\2', text)
    _text(text, 'Public captions')
    return (text + '\n').encode()


def _write_bundle(bundle, sources, lessons):
    (bundle / 'assets').mkdir()
    cards = []
    for lesson in lessons:
        def copy_asset(record):
            original = _asset(sources, record['file'])
            name = record['sha256'] + original.suffix.lower()
            target = bundle / 'assets' / name
            shutil.copyfile(original, target)
            if _sha(target) != record['sha256'].lower():
                raise PublicationError('An approved asset changed during export.')
            return '../assets/' + name
        ident = lesson['id']
        folder = bundle / ident
        folder.mkdir()
        used_ids = list(dict.fromkeys(shot for scene in lesson['scenes'] for shot in lesson['screen_ids'][scene['id']]))
        images = {shot: copy_asset(lesson['screenshots'][shot]) for shot in used_ids}
        kind = 'Video walkthrough' if lesson['mode'] == 'video' else 'Screenshot guide'
        chapters = '<ol>' + ''.join(f'<li><a href="#step-{_esc(scene["id"])}">{_esc(scene["title"])}</a></li>' for scene in lesson['scenes']) + '</ol>'
        media = ''
        if lesson['mode'] == 'video':
            video = copy_asset(lesson['video'])
            captions = _caption_bytes(_asset(sources, lesson['video']['captions']['file']))
            caption_name = hashlib.sha256(captions).hexdigest() + '.vtt'
            (bundle / 'assets' / caption_name).write_bytes(captions)
            public_chapters = [{'start': lesson['starts'][scene['id']], 'title': scene['title']} for scene in lesson['scenes']]
            (folder / 'chapters.json').write_text(json.dumps(public_chapters, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            buttons = ''.join(f'<button type="button" class="chapter" data-start="{lesson["starts"][scene["id"]]}">{_esc(scene["title"])}</button>' for scene in lesson['scenes'])
            media = f'<section class="panel"><h2>Watch the walkthrough</h2><video id="lesson-video" controls playsinline preload="metadata" src="{video}" poster="{images[used_ids[0]]}"><track kind="captions" srclang="en" label="English" src="../assets/{caption_name}"></video><p><a href="{video}" download>Download video</a> · <a href="../assets/{caption_name}" download>Download captions</a></p><div class="chapters">{buttons}</div><p id="player-message" role="status"></p></section>'
            media += "<script>const p=document.getElementById('lesson-video');document.querySelectorAll('[data-start]').forEach(b=>b.addEventListener('click',()=>{p.currentTime=Number(b.dataset.start);p.scrollIntoView({block:'start'});p.play().catch(()=>{document.getElementById('player-message').textContent='Press Play to continue.';});}));p.addEventListener('error',()=>{document.getElementById('player-message').textContent='The video could not load. Reload the page or use the download link.';});</script>"
        steps = ''
        transcript = [lesson['title'], 'Audience: ' + ', '.join(lesson['audience']), '']
        for number, scene in enumerate(lesson['scenes'], 1):
            figures = ''.join(f'<figure><img loading="lazy" src="{images[shot]}" alt="{_esc(scene["title"])}: screen {index}"><figcaption>{_esc(scene["title"])} · Screen {index}</figcaption></figure>' for index, shot in enumerate(lesson['screen_ids'][scene['id']], 1))
            steps += f'<section class="panel" id="step-{_esc(scene["id"])}"><p class="eyebrow">Step {number}</p><h2>{_esc(scene["title"])}</h2><p>{_esc(scene["narration"])}</p>{figures}<h3>Practice</h3><p>{_esc(scene["practice"])}</p></section>'
            transcript += [scene['title'], scene['narration'], 'Practice: ' + scene['practice'], '']
        sectors = '<dl>' + ''.join(f'<dt>{_esc(name)}</dt><dd>{_esc(text)}</dd>' for name, text in lesson['sector_examples'].items()) + '</dl>'
        transcript += ['Examples for your department'] + [name + ': ' + text for name, text in lesson['sector_examples'].items()]
        (folder / 'transcript.txt').write_text('\n'.join(transcript) + '\n', encoding='utf-8')
        prerequisite_list = '<ul>' + ''.join('<li>' + _esc(item) + '</li>' for item in lesson['prerequisites']) + '</ul>'
        contents = f'<div class="hero"><p class="eyebrow">{_esc(lesson["app"])} · {kind}</p><h1>{_esc(lesson["title"])}</h1><p>{_esc(lesson["summary"])}</p><p class="meta">Audience: {_esc(", ".join(lesson["audience"]))}</p></div><section class="panel"><h2>Before you begin</h2>{prerequisite_list}</section><section class="panel"><h2>Chapters</h2>{chapters}</section>{media}{steps}<section class="panel"><h2>Examples for your department</h2>{sectors}</section><section class="panel transcript" id="transcript"><h2>Transcript</h2><a href="transcript.txt" download>Download transcript</a><details><summary>Read the complete transcript</summary><pre style="white-space:pre-wrap;font:inherit">{_esc(chr(10).join(transcript))}</pre></details></section>'
        (folder / 'index.html').write_text(_page(lesson['title'], contents, '../'), encoding='utf-8')
        card = {'id': ident, 'title': lesson['title'], 'app': lesson['app'], 'kind': kind, 'mode': lesson['mode'], 'href': f'{OUTPUT_DIRECTORY}/{ident}/'}
        if lesson['mode'] == 'video':
            card.update(video=f'{OUTPUT_DIRECTORY}/assets/{Path(video).name}',
                        poster=f'{OUTPUT_DIRECTORY}/assets/{Path(images[used_ids[0]]).name}',
                        captions=f'{OUTPUT_DIRECTORY}/assets/{caption_name}',
                        chapters=f'{OUTPUT_DIRECTORY}/{ident}/chapters.json')
        cards.append(card)
    groups = ''
    for app in sorted({item['app'] for item in lessons}):
        app_cards = ''
        for lesson in lessons:
            if lesson['app'] != app:
                continue
            ident = lesson['id']
            kind = 'Video walkthrough' if lesson['mode'] == 'video' else 'Screenshot guide'
            verb = 'Watch walkthrough' if lesson['mode'] == 'video' else 'Open screenshot guide'
            app_cards += f'<article class="card"><p class="eyebrow">{kind}</p><h3><a href="{ident}/">{_esc(lesson["title"])}</a></h3><p>{_esc(lesson["summary"])}</p><p class="meta">{_esc(", ".join(lesson["audience"]))}</p><a class="button" href="{ident}/">{verb}</a></article>'
        groups += f'<section><h2 class="section-title">{_esc(app)}' + (' configuration' if app == 'Core' else ' app') + f'</h2><div class="grid">{app_cards}</div></section>'
    intro = '<div class="hero"><p class="eyebrow">Resgrid Academy</p><h1>Apps and configuration</h1><p>Follow real Resgrid screens, prepare the right access, and practice the steps with examples for your team.</p></div>'
    (bundle / 'index.html').write_text(_page('Apps and configuration', intro + groups, ''), encoding='utf-8')
    return cards


def write_expansion_site(destination, sources):
    """Return only public card metadata; nothing ready means no new navigation."""
    destination, sources = Path(destination).resolve(), Path(sources).resolve()
    if destination == sources or sources in destination.parents or destination in sources.parents:
        raise ValueError('Export must be outside the source records.')
    ready, _ = _collect(sources)
    output = destination / OUTPUT_DIRECTORY
    owned = output.is_dir() and not output.is_symlink() and (output / 'index.html').is_file() and OWNED_MARKER in (output / 'index.html').read_text(encoding='utf-8')
    if not ready:
        if owned:
            shutil.rmtree(output)
        return []
    if output.exists() and not owned:
        raise ValueError('Refusing to replace an unrelated walkthrough directory.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.academy-walkthroughs-', dir=destination.parent) as temporary:
        staged = Path(temporary) / OUTPUT_DIRECTORY
        staged.mkdir()
        cards = _write_bundle(staged, sources, ready)
        destination.mkdir(parents=True, exist_ok=True)
        previous = Path(temporary) / 'previous'
        if owned:
            output.rename(previous)
        try:
            staged.rename(output)
        except OSError:
            if previous.exists():
                previous.rename(output)
            raise
    return cards


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path(__file__).resolve().parents[1] / 'sources')
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(write_expansion_site(args.destination, args.sources), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
