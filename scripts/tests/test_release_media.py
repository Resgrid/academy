"""Delivery integrity and publication boundaries; synthetic media, no capture claims."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_media import checked_upload_manifest, package, publish_assets
from validate_site import validate


class ReleaseMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site, self.output, self.assets = [self.root / n for n in ('site', 'pages', 'assets')]
        self.site.mkdir()
        self.original = b'fictional encoded-video fixture\n' * 1000
        self.digest = hashlib.sha256(self.original).hexdigest()
        self.repository = 'Resgrid/academy'
        for name, contents in {'movie.mp4': self.original, 'p.jpg': b'poster', 'captions.vtt': b'WEBVTT\n',
                               'chapters.json': b'[]', 'CNAME': b'academy.resgrid.com\n',
                               'course.json': b'{"lessons":[],"features":[]}',
                               'index.html': b'<video src="movie.mp4?v=old" poster="p.jpg"></video>',
                               'catalog.json': b'{"video":"movie.mp4"}'}.items():
            (self.site / name).write_bytes(contents)
        page = self.site / 'lessons/one/index.html'
        page.parent.mkdir(parents=True)
        page.write_text('<video src="../../movie.mp4"></video><a href="../../movie.mp4" download>Download</a>')
        manifest = {'format_version': 2, 'topic_guide_count': 0, 'topic_guides': [],
                    'media': [{'path': 'movie.mp4', 'sha256': self.digest}],
                    'lessons': [{'id': 'example', 'kind': 'actual application walkthrough', 'video': 'movie.mp4',
                                 'poster': 'p.jpg', 'captions': 'captions.vtt', 'chapters': 'chapters.json'}]}
        (self.site / 'site-manifest.json').write_text(json.dumps(manifest))

    def pack(self):
        return package(self.site, self.output, self.assets, self.repository)

    def test_pack_keeps_originals_and_domain_and_rewrites_every_player(self):
        self.assertTrue(validate(self.site)['passed'])
        result = self.pack()
        self.assertTrue(result['passed'], result['issues'])
        self.assertEqual(result['local_video_files'], 0)
        self.assertEqual(result['release_video_files'], 1)
        self.assertEqual((self.site / 'movie.mp4').read_bytes(), self.original)
        self.assertEqual((self.assets / (self.digest + '.mp4')).read_bytes(), self.original)
        self.assertEqual((self.output / 'CNAME').read_bytes(), b'academy.resgrid.com\n')
        url = f'https://github.com/Resgrid/academy/releases/download/academy-media/{self.digest}.mp4'
        for name in ('index.html', 'lessons/one/index.html', 'catalog.json'):
            self.assertIn(url, (self.output / name).read_text())
        self.assertEqual(checked_upload_manifest(self.assets)['assets'][0]['sha256'], self.digest)

    def test_pages_size_gate_applies_to_delivery_bundle(self):
        with patch('validate_site.GITHUB_SITE_LIMIT', 5000):
            self.assertFalse(validate(self.site)['passed'])
            self.assertTrue(self.pack()['passed'])
            self.assertTrue(validate(self.output)['pages_size_limit_enforced'])

    def test_corrupt_original_or_upload_copy_fails_before_publication(self):
        (self.site / 'movie.mp4').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            self.pack()
        self.assertFalse(self.output.exists())
        (self.site / 'movie.mp4').write_bytes(self.original)
        self.pack()
        (self.assets / (self.digest + '.mp4')).write_bytes(b'changed')
        with self.assertRaises(ValueError):
            checked_upload_manifest(self.assets)

    def test_unlisted_or_signed_external_video_is_rejected(self):
        self.pack()
        # Fictional signature assembled at runtime; no real signed media URL is stored.
        synthetic_url = 'https://example.com/video.mp4?' + 'sig=' + 'temporary'
        (self.output / 'index.html').write_text(f'<video src="{synthetic_url}"></video>')
        result = validate(self.output)
        self.assertFalse(result['passed'])
        self.assertTrue(any('unlisted Release' in issue for issue in result['issues']))

    def fake_api(self, *, existing=False, corrupt=False, private=False, immutable=False):
        expected = checked_upload_manifest(self.assets)['assets'][0]
        remote = {'name': expected['name'], 'size': expected['bytes'], 'state': 'uploaded',
                  'digest': 'sha256:' + ('0' * 64 if corrupt else expected['sha256']), 'browser_download_url': expected['url']}

        class FakeAPI:
            def __init__(self):
                self.calls = []

            def request(api, method, path, payload=None, media_type=None):
                api.calls.append((method, path))
                if path == '/repos/Resgrid/academy':
                    return {'private': private, 'full_name': 'Resgrid/academy'}
                if '/tags/' in path:
                    return {'id': 10, 'tag_name': 'academy-media', 'draft': False, 'immutable': immutable}
                if method == 'GET' and '/assets?' in path:
                    return [remote] if existing else []
                if method == 'POST' and path.startswith('https://uploads.github.com/repos/Resgrid/academy/releases/10/assets?name='):
                    if payload != self.original or media_type != 'video/mp4':
                        raise AssertionError('Uploader did not use the validated original media bytes.')
                    return remote
                raise AssertionError((method, path))

        return FakeAPI()

    def test_matching_assets_are_reused_and_new_uploads_are_verified(self):
        self.pack()
        for existing in (True, False):
            api = self.fake_api(existing=existing)
            result = publish_assets(self.assets, api, self.repository, 'a' * 40)
            self.assertEqual(result['uploaded_assets'], 0 if existing else 1)
            self.assertEqual(result['deleted_assets'], 0)
            self.assertFalse(any(method in {'DELETE', 'PATCH'} for method, path in api.calls))

    def test_conflicting_asset_or_private_repository_or_immutable_release_is_preserved(self):
        self.pack()
        for options in ({'existing': True, 'corrupt': True}, {'private': True}, {'immutable': True}):
            api = self.fake_api(**options)
            with self.assertRaises(ValueError):
                publish_assets(self.assets, api, self.repository, 'a' * 40)
            self.assertFalse(any(method != 'GET' for method, path in api.calls))

    def test_cannot_replace_output_or_publish_to_another_repository(self):
        self.pack()
        with self.assertRaises(ValueError):
            self.pack()
        api = self.fake_api()
        with self.assertRaises(ValueError):
            publish_assets(self.assets, api, 'someone/else', 'a' * 40)
        self.assertEqual(api.calls, [])


if __name__ == '__main__':
    unittest.main()
