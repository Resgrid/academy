"""Normal export/build wiring with synthetic contract fixtures, never capture claims."""
import hashlib
import json
import shutil
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build as site_build
import test_expansion_site as contract
from export_site import export
from public_site import page
from validate_site import PageLinks, local_target


class ExpansionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = contract.ExpansionSiteTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.sources = self.fixture.root, self.fixture.sources
        self.output = self.root / 'site'
        shutil.copytree(Path(__file__).resolve().parents[2] / 'sources/brand', self.sources / 'brand')
        self.domain = self.root / 'pages.json'
        self.domain.write_text('{"custom_domain":"academy.resgrid.com"}\n')
        lesson = {'id': '00-start', 'title': 'Welcome', 'area': 'orientation', 'role': 'Members',
                  'features': [], 'duration_seconds': 3,
                  'video': 'media/00-start.mp4', 'poster': 'media/00-start.jpg', 'subtitle': 'media/00-start.vtt',
                  'scenes': [{'title': 'Welcome', 'narration': 'Learn the system.', 'start_seconds': 0}],
                  'sector_examples': {'Fire / EMS': 'Practice with a fictional team.'}}
        course = {'learning_paths': {'Complete series': ['00-start']}, 'lessons': [lesson], 'features': [], 'settings': []}
        for relative, content in {
            'course.json': json.dumps(course), 'index.html': '<h1>Source library</h1>',
            'coverage.csv': 'id,label\n', 'settings.csv': 'id,label\n',
            'media/00-start.mp4': 'synthetic existing primer, not a real recording',
            'media/00-start.jpg': 'synthetic poster', 'media/00-start.vtt': 'WEBVTT\n', 'media/00-start.srt': 'synthetic captions',
            'media/00-start.chapters.json': '[{"start":0,"title":"Welcome"}]',
            'deep-dive/index.html': '<h1>Walkthroughs</h1>', 'deep-dive/sectors.html': '<h1>Sectors</h1>',
            'deep-dive/course.json': '{"lessons":[]}', 'deep-dive/preparation-validation.json': '{"lessons":[]}',
            'deep-dive/sector-examples.json': json.dumps({'sectors': ['Fire / EMS'], 'deep_lessons': [], 'primer_lessons': [lesson]}),
            'captures/firehouse51/manifest.json': '[]',
            'captures/firehouse51/01-dashboard.jpg': 'synthetic dashboard',
            'captures/firehouse51/firehouse51-walkthrough.mp4': 'synthetic existing introduction',
            'captures/firehouse51/firehouse51-walkthrough.vtt': 'WEBVTT\n',
            'captures/firehouse51/firehouse51-walkthrough.srt': 'synthetic captions',
            'captures/firehouse51/firehouse51-walkthrough.chapters.json': '[{"start":0,"title":"Introduction"}]',
        }.items():
            path = self.sources / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        (self.sources / 'scripts').mkdir()

    def publish(self, video=False):
        if video:
            self.fixture.video_fixture()
            self.fixture.save()
        result = export(self.sources, self.output)
        self.assertTrue(result['passed'], result['issues'])
        self.assertEqual(self.domain.read_text(), '{"custom_domain":"academy.resgrid.com"}\n')
        return json.loads((self.output / 'site-manifest.json').read_text())

    def test_evidence_ready_video_reaches_normal_manifest_navigation_and_cards(self):
        manifest = self.publish(video=True)
        self.assertEqual(manifest['topic_guide_count'], 1)
        self.assertEqual(manifest['detailed_videos'], 1)
        self.assertEqual(manifest['expansion_videos'], 1)
        self.assertEqual({item['id'] for item in manifest['lessons']}, {'firehouse51-introduction', self.fixture.lesson['id']})
        self.assertEqual(manifest['topic_guides'][0]['id'], '00-start')
        entry = next(item for item in manifest['lessons'] if item['id'] == self.fixture.lesson['id'])
        for key in ('video', 'poster', 'captions', 'chapters'):
            self.assertTrue((self.output / entry[key]).is_file())
        for media in manifest['media']:
            self.assertEqual(hashlib.sha256((self.output / media['path']).read_bytes()).hexdigest(), media['sha256'])
        for relative in ('index.html', 'deep-dive/index.html'):
            markup = (self.output / relative).read_text()
            self.assertIn('Apps and configuration', markup)
            self.assertIn('walkthroughs/' + self.fixture.lesson['id'] + '/', markup)
            self.assertIn('Incident records', markup)
        landing = (self.output / 'index.html').read_text()
        self.assertIn('class="button primary" href="deep-dive/">Watch Resgrid walkthroughs', landing)
        self.assertLess(landing.index('id="app-walkthroughs"'), landing.index('id="learn"'))
        self.assertEqual(landing.count('id="app-walkthroughs"'), 1)
        self.assertFalse((self.output / 'media/00-start.mp4').exists())
        self.assertTrue((self.sources / 'media/00-start.mp4').exists())
        self.assertTrue((self.output / 'topics/00-start/index.html').exists())
        self.assertTrue((self.output / 'captures/firehouse51/firehouse51-walkthrough.mp4').exists())
        self.assertTrue((self.output / 'about/index.html').exists())

    def test_screenshot_guide_has_navigation_but_never_a_video_inventory_row(self):
        manifest = self.publish()
        self.assertEqual(manifest['expansion_videos'], 0)
        self.assertEqual(len(manifest['walkthrough_guides']), 1)
        self.assertNotIn(self.fixture.lesson['id'], {item['id'] for item in manifest['lessons']})
        markup = (self.output / 'walkthroughs' / self.fixture.lesson['id'] / 'index.html').read_text()
        self.assertIn('Screenshot guide', markup)
        self.assertNotIn('<video', markup)
        self.assertIn('Open screenshot guide', (self.output / 'index.html').read_text())

    def test_verified_webm_is_included_in_the_same_media_inventory(self):
        self.fixture.video_fixture()
        original = self.sources / self.fixture.evidence['video']['file']
        replacement = original.with_suffix('.webm')
        original.rename(replacement)
        self.fixture.evidence['video']['file'] = replacement.relative_to(self.sources).as_posix()
        for observation in self.fixture.evidence['browser_playback']:
            observation['current_src'] = 'http://localhost:8000/media/record.webm'
        self.fixture.save()
        manifest = self.publish()
        entry = next(item for item in manifest['lessons'] if item['id'] == self.fixture.lesson['id'])
        self.assertTrue(entry['video'].endswith('.webm'))
        self.assertIn(entry['video'], {item['path'] for item in manifest['media']})

    def test_incomplete_or_revoked_expansion_does_not_leave_public_cards_or_assets(self):
        self.publish(video=True)
        self.fixture.lesson['export_ready'] = False
        self.fixture.save()
        manifest = self.publish()
        self.assertEqual(manifest['expansion_videos'], 0)
        self.assertFalse((self.output / 'walkthroughs').exists())
        for relative in ('index.html', 'deep-dive/index.html', 'about/index.html'):
            markup = (self.output / relative).read_text()
            self.assertNotIn('Apps and configuration', markup)
            self.assertNotIn('walkthroughs/' + self.fixture.lesson['id'], markup)
        self.assertEqual(len(manifest['lessons']), 1)

    def test_public_projection_has_no_source_provenance_private_urls_or_production_labels(self):
        self.publish(video=True)
        forbidden = ('localhost', '/Users/', 'descript.com', 'evidence_file', 'source_files', 'browser_playback', 'Warm Lulu', 'capture_intent')
        for path in self.output.rglob('*'):
            if path.suffix in {'.html', '.json', '.txt', '.vtt'}:
                text = path.read_text()
                for token in forbidden:
                    self.assertNotIn(token, text, path)
        for relative in ('index.html', 'deep-dive/index.html', 'about/index.html', 'walkthroughs/index.html'):
            parser = PageLinks()
            target = self.output / relative
            parser.feed(target.read_text())
            for reference in parser.links:
                linked = local_target(self.output, target, reference)
                self.assertTrue(linked is None or linked.is_file(), (relative, reference))
        nested = page('Existing walkthrough', '<h1>Steps</h1>', '../../../', expansion=True)
        self.assertIn('href="../../../walkthroughs/"', nested)
        self.assertNotIn('href="/', nested)

    def test_normal_build_uses_the_integrated_export_after_source_preparation(self):
        self.fixture.video_fixture()
        self.fixture.save()
        # Source generation is outside this consumer test. Its real evidence gate
        # still runs through export and write_expansion_site without a mock.
        with patch.object(site_build, 'sync') as sync, patch.object(site_build, 'verify', return_value={'passed': True}), patch.object(site_build.subprocess, 'run') as prepare:
            result = site_build.build(self.root)
        self.assertTrue(result['passed'])
        sync.assert_called_once_with(self.sources.resolve())
        self.assertEqual(prepare.call_count, 2)
        manifest = json.loads((self.output / 'site-manifest.json').read_text())
        self.assertEqual(manifest['expansion_videos'], 1)


if __name__ == '__main__':
    unittest.main()
