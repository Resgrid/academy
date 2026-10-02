import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_domain import check_domain, configured_domain, normalize_domain
from export_site import public_data, public_html
from validate_site import local_target, validate


class DeploymentTests(unittest.TestCase):
    def test_relative_assets_work_at_domain_root_and_repository_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            page = root / 'deep-dive/review/lesson/index.html'
            self.assertEqual(local_target(root, page, '../../media/lesson.mp4?v=123'), root / 'deep-dive/media/lesson.mp4')
            for reference in ('/media/lesson.mp4', '//example.com/video.mp4', '../../../../outside.mp4'):
                with self.assertRaises(ValueError):
                    local_target(root, page, reference)

    def test_private_previews_and_local_environment_do_not_enter_public_data(self):
        cleaned = public_data({'title': 'Tutorial', 'descript_project': {'url': 'https://web.descript.com/project'}, 'nested': {'private_preview': 'https://share.descript.com/view/preview', 'environment': 'http://127.0.0.1:18767/', 'video': 'media/lesson.mp4'}})
        self.assertEqual(cleaned, {'title': 'Tutorial', 'nested': {'video': 'media/lesson.mp4'}})
        html = '<p><a href="lesson/">Watch</a> · <a href="https://share.descript.com/view/preview">Private audio</a></p>'
        self.assertEqual(public_html(html), '<p><a href="lesson/">Watch</a></p>')

    def test_custom_domain_is_preserved_unless_explicitly_checked(self):
        self.assertIn('existing', check_domain('', 'https://owner.github.io/Academy'))
        self.assertIn('matches', check_domain('ACADEMY.EXAMPLE.COM.', 'https://academy.example.com/'))
        with self.assertRaises(ValueError):
            check_domain('academy.example.com', 'https://owner.github.io/Academy')
        for domain in ('https://academy.example.com', '*.example.com', 'example.com/path', 'example.com:443', '-bad.example.com', 'example..com'):
            with self.assertRaises(ValueError):
                normalize_domain(domain)

    def test_repository_hostname_is_used_on_every_automatic_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'pages.json'
            path.write_text('{"custom_domain":"academy.resgrid.com"}')
            expected = configured_domain('', path)
            self.assertEqual(expected, 'academy.resgrid.com')
            for scheme in ('https', 'http'):
                self.assertIn('matches', check_domain(expected, scheme + '://academy.resgrid.com/'))
            with self.assertRaises(ValueError):
                check_domain(expected, 'https://resgrid.github.io/academy')
            self.assertEqual(configured_domain('training.example.com', path), 'training.example.com')

    def test_deployment_rejects_missing_links_and_altered_video(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('<a href="missing.html">Missing</a>')
            (root / 'movie.mp4').write_bytes(b'changed movie')
            (root / 'site-manifest.json').write_text(json.dumps({'media': [{'path': 'movie.mp4', 'sha256': hashlib.sha256(b'original movie').hexdigest()}]}))
            result = validate(root)
            self.assertFalse(result['passed'])
            self.assertTrue(any('Missing local link' in x for x in result['issues']))
            self.assertTrue(any('changed media' in x for x in result['issues']))

    def test_deployment_rejects_private_files_and_signed_media_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text('https://storage.example.com/file?X-Goog-Signature=secret')
            (root / 'credentials.env').write_text('SECRET=example')
            (root / 'site-manifest.json').write_text('{"media": []}')
            result = validate(root)
            self.assertFalse(result['passed'])
            self.assertTrue(any('Private editor' in x for x in result['issues']))
            self.assertTrue(any('Non-site file' in x for x in result['issues']))


if __name__ == '__main__':
    unittest.main()
