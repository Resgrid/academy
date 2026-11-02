"""Package Pages separately from byte-identical videos; upload only in deployment CI."""
import argparse
from html import escape, unescape
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from media_delivery import asset_name, release_base, sha_file
from validate_site import local_target, validate


def package(site, destination, assets, repository, tag='academy-media'):
    site, destination, assets = [Path(p).resolve() for p in (site, destination, assets)]
    paths = [site, destination, assets]
    if any(a == b or a in b.parents or b in a.parents for i, a in enumerate(paths) for b in paths[i + 1:]):
        raise ValueError('Input site, Pages output and media output must be separate directories.')
    if destination.exists() or assets.exists():
        raise ValueError('Use fresh output directories; existing files are preserved.')
    if destination.parent != assets.parent:
        raise ValueError('Keep both generated outputs in the same parent directory.')
    base = release_base(repository, tag)
    checked = validate(site, pages_size_limit=False)
    if not checked['passed']:
        raise ValueError('Source site failed validation: ' + '; '.join(checked['issues']))
    manifest = json.loads((site / 'site-manifest.json').read_text())
    if manifest.get('format_version') != 2:
        raise ValueError('Package the original self-contained version2 site.')
    replacements, media, uploads = {}, [], {}
    for row in manifest['media']:
        source = site / row['path']
        digest = sha_file(source)
        if digest != row['sha256']:
            raise ValueError('Source video changed: ' + row['path'])
        name = asset_name(row['path'], digest)
        url = base + '/' + name
        replacements[source.resolve()] = url
        media.append(dict(path=row['path'], sha256=digest, bytes=source.stat().st_size, url=url))
        uploads[name] = dict(name=name, source_path=row['path'], sha256=digest,
                             bytes=source.stat().st_size, url=url)

    def reference(page, value):
        if not urlsplit(value).path.lower().endswith(('.mp4', '.webm')):
            return value
        try:
            return replacements.get(local_target(site, page, value), value)
        except ValueError:
            return value

    def json_references(page, value):
        if isinstance(value, dict):
            return {k: json_references(page, v) for k, v in value.items()}
        if isinstance(value, list):
            return [json_references(page, v) for v in value]
        return reference(page, value) if isinstance(value, str) else value

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.academy-release-', dir=destination.parent) as temporary:
        staged, staged_assets = Path(temporary) / 'site', Path(temporary) / 'media'
        staged.mkdir(); staged_assets.mkdir()
        for source in sorted(site.rglob('*')):
            if not source.is_file() or source.resolve() in replacements:
                continue
            target = staged / source.relative_to(site)
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == '.html':
                pattern = r'''(\b(?:src|href)\s*=\s*)(["'])(.*?)(\2)'''
                text = re.sub(pattern, lambda m: m[1] + m[2] + escape(reference(source, unescape(m[3])), quote=True) + m[4], source.read_text())
                target.write_text(text)
            elif source.suffix == '.json':
                target.write_text(json.dumps(json_references(source, json.loads(source.read_text())), indent=2, ensure_ascii=False) + '\n')
            else:
                shutil.copy2(source, target)
        for name, row in uploads.items():
            target = staged_assets / name
            shutil.copy2(site / row['source_path'], target)
            if sha_file(target) != row['sha256']:
                raise ValueError('Media copy failed its SHA256 check.')
        for lesson in manifest['lessons']:
            lesson['video'] = replacements[(site / lesson['video']).resolve()]
        manifest.update(format_version=3, media=media,
                        media_delivery=dict(kind='github_release', repository=repository, tag=tag))
        (staged / 'site-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        upload_manifest = dict(format_version=1, repository=repository, tag=tag,
                               assets=sorted(uploads.values(), key=lambda row: row['name']))
        (staged_assets / 'upload-manifest.json').write_text(json.dumps(upload_manifest, indent=2) + '\n')
        result = validate(staged)
        if not result['passed']:
            raise ValueError('Release delivery site failed validation: ' + '; '.join(result['issues']))
        staged.rename(destination)
        staged_assets.rename(assets)
    return dict(result, release_assets=len(uploads), release_bytes=sum(row['bytes'] for row in uploads.values()),
                originals_changed=False, upload_performed=False)


def checked_upload_manifest(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / 'upload-manifest.json').read_text())
    base = release_base(manifest['repository'], manifest['tag'])
    if manifest.get('format_version') != 1 or not manifest.get('assets'):
        raise ValueError('Missing Release asset inventory.')
    seen = set()
    for row in manifest['assets']:
        name = asset_name(row['source_path'], row['sha256'])
        path = directory / name
        if name != row['name'] or name in seen or row['url'] != base + '/' + name:
            raise ValueError('Invalid or duplicate Release asset entry.')
        if path.is_symlink() or not path.is_file() or type(row['bytes']) is not int or row['bytes'] <= 0:
            raise ValueError('Missing or unsafe Release asset.')
        if path.stat().st_size != row['bytes'] or sha_file(path) != row['sha256']:
            raise ValueError('Release asset bytes differ from the upload manifest.')
        seen.add(name)
    if {p.name for p in directory.iterdir()} != seen | {'upload-manifest.json'}:
        raise ValueError('Unexpected files in the Release upload directory.')
    return manifest


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Authenticated GitHub API redirects are not allowed.')


class GitHub:
    def __init__(self, token):
        self.token = token
        self.opener = build_opener(NoRedirects())

    def request(self, method, path, payload=None, media_type=None):
        url = path if path.startswith('https://') else 'https://api.github.com' + path
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in {'api.github.com', 'uploads.github.com'} or parsed.username:
            raise ValueError('Unexpected authenticated API destination.')
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode() if payload is not None else None
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                   'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'resgrid-academy-media',
                   'Content-Type': media_type or 'application/json'}
        try:
            with self.opener.open(Request(url, data=data, headers=headers, method=method), timeout=120) as response:
                return json.load(response)
        except HTTPError as error:
            if method == 'GET' and error.code == 404:
                return None
            raise ValueError(f'GitHub API {method} failed with HTTP{error.code}; no existing assets were replaced.') from None


def verify_remote_asset(asset, expected):
    if not asset or any(asset.get(k) != v for k, v in {
        'name': expected['name'], 'size': expected['bytes'], 'state': 'uploaded',
        'digest': 'sha256:' + expected['sha256'], 'browser_download_url': expected['url'],
    }.items()):
        raise ValueError('GitHub Release asset size, SHA256, state or URL does not match the validated master.')


def publish_assets(directory, api, repository, commit):
    manifest = checked_upload_manifest(directory)
    if manifest['repository'] != repository or not re.fullmatch(r'[0-9a-f]{40,64}', commit):
        raise ValueError('Release inventory must match the deployment repository and commit.')
    repo = api.request('GET', '/repos/' + repository)
    if not repo or repo.get('private') is not False or repo.get('full_name', '').lower() != repository.lower():
        raise ValueError('Academy video delivery requires the selected public repository.')
    endpoint = '/repos/' + repository + '/releases'
    release = api.request('GET', endpoint + '/tags/' + quote(manifest['tag'], safe=''))
    if release is None:
        release = api.request('POST', endpoint, {'tag_name': manifest['tag'], 'target_commitish': commit,
                              'name': 'Academy video library', 'body': 'Qualified Academy video masters, named by SHA256. Existing assets are preserved.',
                              'draft': False, 'prerelease': False, 'make_latest': 'false'})
    if release.get('tag_name') != manifest['tag'] or release.get('draft') is not False or type(release.get('id')) is not int:
        raise ValueError('Unexpected Release identity or visibility.')
    assets = []
    for page in range(1, 1001):
        batch = api.request('GET', endpoint + f'/{release["id"]}/assets?per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('Could not list existing Release assets.')
        assets.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError('Release asset pagination exceeded its bound.')
    existing = {row['name']: row for row in assets}
    if len(existing) != len(assets):
        raise ValueError('Duplicate existing Release asset names.')
    missing = [row for row in manifest['assets'] if row['name'] not in existing]
    # Validate every existing match before the first new upload.
    for row in manifest['assets']:
        if row['name'] in existing:
            verify_remote_asset(existing[row['name']], row)
    if missing and release.get('immutable'):
        raise ValueError('The media Release is immutable; use a separate appendable media tag before publishing more videos.')
    for row in missing:
        payload = (Path(directory) / row['name']).read_bytes()
        if len(payload) != row['bytes'] or __import__('hashlib').sha256(payload).hexdigest() != row['sha256']:
            raise ValueError('Upload input changed after validation.')
        url = f'https://uploads.github.com/repos/{repository}/releases/{release["id"]}/assets?name=' + quote(row['name'])
        uploaded = api.request('POST', url, payload, 'video/mp4' if row['name'].endswith('.mp4') else 'video/webm')
        verify_remote_asset(uploaded, row)
    return dict(verified_assets=len(manifest['assets']), uploaded_assets=len(missing),
                reused_assets=len(manifest['assets']) - len(missing), deleted_assets=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    pack = commands.add_parser('package')
    for flag in ('site', 'destination', 'assets'):
        pack.add_argument('--' + flag, type=Path, required=True)
    pack.add_argument('--repository', required=True)
    pack.add_argument('--tag', default='academy-media')
    upload = commands.add_parser('upload')
    upload.add_argument('--assets', type=Path, required=True)
    upload.add_argument('--execute', action='store_true', help='Publish only from the guarded default-branch deployment job.')
    args = parser.parse_args()
    if args.command == 'package':
        result = package(args.site, args.destination, args.assets, args.repository, args.tag)
    elif not args.execute:
        manifest = checked_upload_manifest(args.assets)
        result = dict(verified_local_assets=len(manifest['assets']), upload_performed=False)
    else:
        if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('GITHUB_EVENT_NAME') not in {'push', 'workflow_dispatch'}:
            raise ValueError('Media publication runs only in the deployment workflow.')
        branch = os.environ.get('ACADEMY_DEFAULT_BRANCH', '')
        if not branch or os.environ.get('GITHUB_REF') != 'refs/heads/' + branch or not os.environ.get('GITHUB_TOKEN'):
            raise ValueError('A default-branch run and automatic workflow token are required.')
        result = publish_assets(args.assets, GitHub(os.environ['GITHUB_TOKEN']), os.environ['GITHUB_REPOSITORY'], os.environ['GITHUB_SHA'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(str(error))
