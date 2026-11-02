"""Publication-contract tests with synthetic assets, never capture/playback claims."""
import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from expansion_site import (
    SECTORS, guide_review_digest, lesson_content_digest,
    readiness_report, verify_guide_document, write_expansion_site,
)
from verify_capture_evidence import visible_controls_digest


def png():
    """Visibly synthetic test image; metadata never establishes authenticity."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    rows = (b'\0' + b'\x12\x34\x56' * 320) * 180
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 320, 180, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attributes):
        self.urls.extend(value for name, value in attributes if name in {'src', 'href', 'poster'} and value)


class ExpansionSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / 'sources'
        self.output = self.root / 'site'
        (self.sources / 'expansion/lessons').mkdir(parents=True)
        self.lesson_file = self.sources / 'expansion/lessons/app-ic-settings.json'
        self.evidence_file = self.sources / 'evidence/app-ic-settings.json'
        self.caption = 'Select Save draft to keep this incident record as a Draft.'
        self.lesson = {
            'id': 'app-ic-settings', 'title': 'Incident records', 'app': 'IC',
            'audience': ['Incident commanders', 'Department trainers'],
            'summary': 'Open an incident record and save your work.',
            'prerequisites': ['Use an authorized training department.', 'Open an existing training incident.'],
            'export_ready': True, 'publication_mode': 'guide',
            'evidence_file': 'evidence/app-ic-settings.json',
            'scenes': [{'id': 'save', 'title': 'Save a record',
                        'narration': self.caption, 'practice': 'Save a fictional training record.',
                        'required_labels': ['Save draft', 'Draft'],
                        'route': '/private/source-route',
                        'capture_intent': 'Internal source planning only.'}],
            'sector_examples': [{'sector': sector, 'scenario': 'Practice with an authorized ' + sector + ' training team.'} for sector in SECTORS],
            'source_files': ['/Users/operator/private/source.tsx'],
            'source_editor_url': 'https://web.descript.com/editor/private-project',
            'capture_url': 'http://localhost:19104/records',
        }
        self.evidence = self.guide_fixture()
        self.save()

    def asset(self, filename, content, image=False):
        path = self.sources / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        result = {'file': filename, 'sha256': hashlib.sha256(content).hexdigest()}
        if image:
            result.update(width=320, height=180)
        return result

    def screenshot(self):
        shot = self.asset('captures/record.png', png(), image=True)
        shot.update(id='record', app='IC', kind='application_screenshot',
                    provenance={'method': 'browser_screenshot',
                                'url': 'http://localhost:19104/records',
                                'captured_at': '2026-10-25T11:59:00Z'},
                    visible_labels=['Incident record', 'Draft', 'Save draft'])
        return shot

    def guide_fixture(self):
        return {'schema_version': 1, 'kind': 'screenshot_guide',
                'lesson_id': self.lesson['id'], 'screenshots': [self.screenshot()],
                'scenes': [{'id': 'save', 'screens': [{'screenshot_id': 'record', 'required_labels': ['Save draft', 'Draft']}]}]}

    def video_fixture(self):
        self.lesson['publication_mode'] = 'video'
        video = self.asset('media/record.mp4', b'synthetic test identity, not a playable recording')
        video.update(duration_seconds=30, width=320, height=180, assembled_at='2026-10-25T12:00:00Z')
        video['captions'] = self.asset('media/record.vtt', ('WEBVTT\n\n00:00.000 --> 00:30.000\n' + self.caption + '\n').encode())
        scene = {'id': 'save', 'kind': 'operational', 'start': 0, 'end': 30,
                 'screens': [{'screenshot_id': 'record', 'start': 0, 'end': 30}],
                 'captions': [{'start': 0, 'end': 30, 'text': self.caption, 'screenshot_id': 'record', 'required_labels': ['Save draft', 'Draft']}]}
        frame = self.asset('proof/rendered.png', png(), image=True)
        frame.update(time=15, video_sha256=video['sha256'], application_visible=True, visible_labels=['Save draft', 'Draft'], caption_text=self.caption)
        playback = []
        for position, time in [('beginning', 2), ('middle', 15), ('end', 28)]:
            playback.append({'position': position, 'video_sha256': video['sha256'],
                             'url': 'http://localhost:8000/record/',
                             'current_src': 'http://localhost:8000/media/record.mp4',
                             'captured_at': '2026-10-25T12:01:00Z',
                             'previous_time': time - .5, 'current_time': time,
                             'duration_seconds': 30, 'video_width': 320, 'video_height': 180,
                             'ready_state': 4, 'network_state': 1, 'paused': False,
                             'ended': False, 'media_error': None, 'console_errors': [],
                             'captions': {'mode': 'showing', 'text': self.caption},
                             'screenshot': self.asset('proof/' + position + '.png', png(), image=True)})
        self.evidence = {'schema_version': 1, 'lesson_id': self.lesson['id'],
                         'authoring_sha256': lesson_content_digest(self.lesson),
                         'video': video, 'screenshots': [self.screenshot()],
                         'scenes': [scene], 'rendered_segments': [{'scene_id': 'save', 'screenshot_id': 'record', 'start': 0, 'end': 30, 'frame': frame}],
                         'browser_playback': playback}
        return self.evidence

    def save(self, review=True):
        if review and self.lesson.get('publication_mode') == 'guide':
            self.evidence['guide_review'] = {
                'passed': True, 'reviewed_at': '2026-10-25T12:02:00Z',
                'content_sha256': guide_review_digest(self.lesson, self.evidence),
            }
        self.evidence_file.parent.mkdir(parents=True, exist_ok=True)
        self.evidence_file.write_text(json.dumps(self.evidence), encoding='utf-8')
        self.lesson_file.write_text(json.dumps(self.lesson), encoding='utf-8')

    def export(self):
        return write_expansion_site(self.output, self.sources)

    def assert_not_exported(self):
        self.assertEqual(self.export(), [])
        self.assertFalse((self.output / 'walkthroughs').exists())

    def lesson_html(self):
        return (self.output / 'walkthroughs' / self.lesson['id'] / 'index.html').read_text()

    def test_nothing_ready_creates_no_output_or_navigation(self):
        self.lesson.pop('export_ready')
        self.save()
        self.assert_not_exported()

    def receiver_guide(self):
        self.lesson['app'] = 'Core'
        self.evidence['screenshots'][0]['app'] = 'Core'
        self.evidence['primary_app'] = 'Core'
        self.evidence['supporting_applications'] = [{'app': 'Mailpit', 'for_app': 'Core', 'role': 'controlled_local_receiver', 'purpose': 'Inspect local SMTP receipts.'}]
        receiver = dict(self.screenshot(), id='receiver', app='Mailpit', visible_labels=['Mailpit'],
                        provenance={'method': 'browser_screenshot', 'url': 'http://127.0.0.1:18126/', 'captured_at': '2026-10-25T11:59:00Z'})
        self.evidence['screenshots'].append(receiver)
        self.evidence['scenes'][0]['screens'].append({'screenshot_id': 'receiver', 'required_labels': ['Mailpit']})
        return receiver

    def test_explicit_local_receiver_can_support_a_primary_app_guide(self):
        receiver = self.receiver_guide()
        self.save()
        self.assertEqual(len(self.export()), 1)
        receiver['provenance']['url'] = 'https://receiver.example/'
        self.save()
        self.assertEqual(self.export(), [])

    def test_receiver_cannot_replace_primary_configuration_or_bypass_declaration(self):
        self.receiver_guide()
        self.lesson['scenes'][0]['required_labels'].append('Mailpit')
        self.save()
        self.assert_not_exported()
        self.lesson['scenes'][0]['required_labels'].pop()
        self.evidence.pop('supporting_applications')
        self.save()
        self.assert_not_exported()
        self.assertFalse(self.output.exists())

    def test_readiness_is_an_explicit_boolean_not_a_truthy_value(self):
        for value in (False, 1, 'true', 'passed', None):
            with self.subTest(value=value):
                self.lesson['export_ready'] = value
                self.save()
                self.assert_not_exported()

    def test_complete_reviewed_guide_has_steps_practice_chapters_and_six_sectors(self):
        cards = self.export()
        self.assertEqual(cards, [{'id': self.lesson['id'], 'title': 'Incident records', 'app': 'IC', 'kind': 'Screenshot guide', 'mode': 'guide', 'href': 'walkthroughs/app-ic-settings/'}])
        page = self.lesson_html()
        for text in ['Incident commanders', 'Before you begin', 'Chapters', '#step-save', self.caption, 'Practice', 'Transcript', *SECTORS]:
            self.assertIn(text, page)
        self.assertIn('<img ', page)
        self.assertIn('Screenshot guide', page)
        self.assertNotIn('<video', page)
        self.assertNotIn('Video walkthrough', page)
        self.assertNotIn('Download video', page)
        self.assertTrue((self.output / 'walkthroughs/app-ic-settings/transcript.txt').is_file())

    def icon_guide(self):
        scene = self.lesson['scenes'][0]
        scene.update(required_labels=['Attach', 'Send'], narration='Choose Attach to inspect the file options, then Send the training message.')
        shot = self.evidence['screenshots'][0]
        shot['visible_labels'] = ['Chat']
        shot['visible_controls'] = [
            {'accessible_name': name, 'role': 'button', 'rect': {'x': x, 'y': 140, 'width': 24, 'height': 24}, 'icon_only': True, 'provenance': 'browser_dom'}
            for name, x in [('Attach', 220), ('Send', 260)]
        ]
        shot['capture_review'] = {'passed': True, 'reviewer': 'synthetic contract test, no actual image review',
                                  'reviewed_at': '2026-10-25T12:01:00Z', 'sha256': shot['sha256'],
                                  'controls_sha256': visible_controls_digest(shot['visible_controls']),
                                  'application_visible': True, 'no_errors': True, 'controls_reviewed': True,
                                  'controls_fully_visible': True, 'controls_unobstructed': True}
        self.evidence['scenes'][0]['screens'][0]['required_labels'] = ['Attach', 'Send']
        return shot

    def test_fully_reviewed_icon_controls_can_support_a_screenshot_guide(self):
        shot = self.icon_guide()
        self.save()
        self.assertEqual(len(self.export()), 1)
        self.assertEqual(shot['visible_labels'], ['Chat'])
        self.assertNotIn('capture_review', self.lesson_html())
        self.assertNotIn('visible_controls', self.lesson_html())

    def test_guide_cannot_promote_unreviewed_invented_or_clipped_icons(self):
        original_lesson, original_evidence = copy.deepcopy(self.lesson), copy.deepcopy(self.evidence)
        for fault in ['missing-review', 'changed-name', 'out-of-image', 'occluded', 'blocked', 'malformed']:
            with self.subTest(fault=fault):
                self.lesson, self.evidence = copy.deepcopy(original_lesson), copy.deepcopy(original_evidence)
                shot = self.icon_guide()
                if fault == 'missing-review':
                    shot.pop('capture_review')
                elif fault == 'changed-name':
                    shot['visible_controls'][0]['accessible_name'] = 'Invented action'
                elif fault == 'out-of-image':
                    shot['visible_controls'][0]['rect']['x'] = 319
                elif fault == 'occluded':
                    shot['capture_review']['controls_unobstructed'] = False
                elif fault == 'blocked':
                    shot['state'] = 'blocked_extension'
                else:
                    shot['visible_controls'] = [None]
                self.save()
                self.assert_not_exported()

    def test_icon_guide_still_requires_actual_image_hash(self):
        shot = self.icon_guide()
        shot['sha256'] = '0' * 64
        shot['capture_review']['sha256'] = shot['sha256']
        self.save()
        self.assert_not_exported()

    def test_video_export_accepts_icons_only_with_source_frame_and_playback_evidence(self):
        self.caption = 'Select Attach, then Send.'
        self.video_fixture()
        shot = self.icon_guide()
        self.lesson['scenes'][0]['narration'] = self.caption
        self.evidence['scenes'][0]['captions'][0]['required_labels'] = ['Attach', 'Send']
        frame = self.evidence['rendered_segments'][0]['frame']
        frame['visible_labels'] = ['Chat']
        frame['reviewed_control_names'] = ['Attach', 'Send']
        frame['control_review'] = dict(shot['capture_review'], sha256=frame['sha256'],
            controls_sha256=visible_controls_digest(frame['reviewed_control_names']),
            video_sha256=self.evidence['video']['sha256'], source_screenshot_sha256=shot['sha256'])
        self.evidence['authoring_sha256'] = lesson_content_digest(self.lesson)
        self.save()
        self.assertEqual(self.export()[0]['kind'], 'Video walkthrough')
        self.assertEqual(shot['visible_labels'], ['Chat'])
        self.evidence['browser_playback'].pop()
        self.save()
        self.assert_not_exported()

    def test_source_records_local_urls_editor_links_and_json_do_not_publish(self):
        self.export()
        files = list(self.output.rglob('*'))
        self.assertFalse(any(path.suffix == '.json' for path in files))
        for path in files:
            if path.suffix in {'.html', '.txt'}:
                text = path.read_text()
                for private in ['/Users/', '/private/source-route', 'localhost', 'descript.com', 'capture_intent', 'evidence_file', 'guide_review', 'Internal source planning']:
                    self.assertNotIn(private, text, path)

    def test_public_text_is_escaped(self):
        self.lesson['scenes'][0]['practice'] = 'Compare <script>alert("x")</script> as plain text.'
        self.save()
        self.export()
        self.assertIn('&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;', self.lesson_html())
        self.assertNotIn('<script>alert', self.lesson_html())

    def test_all_relative_links_work_at_domain_root_and_repository_subpath(self):
        # Shared navigation and branding are supplied by the parent site exporter.
        from academy_brand import write_brand_assets
        write_brand_assets(self.output, Path(__file__).resolve().parents[2] / 'sources')
        for relative in ('index.html', 'deep-dive/index.html', 'deep-dive/sectors.html', 'about/index.html'):
            target = self.output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('<h1>Synthetic parent page</h1>')
        self.video_fixture()
        self.save()
        self.export()
        for base in ['https://academy.example.org/', 'https://team.github.io/resgrid-academy/']:
            for page in self.output.rglob('*.html'):
                parser = Links()
                parser.feed(page.read_text())
                public_page = urljoin(base, page.relative_to(self.output).as_posix())
                for relative in parser.urls:
                    if urlsplit(relative).scheme:
                        continue
                    with self.subTest(base=base, page=page.name, relative=relative):
                        self.assertFalse(relative.startswith('/'))
                        target = urlsplit(urljoin(public_page, relative))
                        self.assertTrue(target.path.startswith(urlsplit(base).path))
                        local_path = unquote(target.path[len(urlsplit(base).path):])
                        if not local_path:  # The parent exporter owns the Academy home.
                            continue
                        local = self.output / local_path
                        self.assertTrue(local.is_file() or (local / 'index.html').is_file(), target)

    def test_missing_asset_wrong_hash_dimensions_and_illustration_fail_closed(self):
        for change in [{'file': 'captures/missing.png'}, {'sha256': '0' * 64}, {'width': 640}, {'kind': 'illustrated_slide'}]:
            with self.subTest(change=change):
                self.evidence = self.guide_fixture()
                self.evidence['screenshots'][0].update(change)
                self.save()
                self.assert_not_exported()

    def test_rejected_or_private_screenshot_cannot_be_promoted_by_export_ready(self):
        for change in [{'accepted': False}, {'publication_eligible': False}, {'contains_private_ui': True}]:
            with self.subTest(change=change):
                self.evidence = self.guide_fixture()
                self.evidence['screenshots'][0].update(change)
                self.save()
                self.assert_not_exported()

    def test_incomplete_scene_coverage_or_missing_control_is_rejected(self):
        for fault in ['missing-scene', 'extra-scene', 'missing-image', 'missing-control', 'missing-author-control']:
            with self.subTest(fault=fault):
                self.evidence = self.guide_fixture()
                if fault == 'missing-scene':
                    self.evidence['scenes'] = []
                elif fault == 'extra-scene':
                    self.evidence['scenes'].append({'id': 'extra', 'screens': []})
                elif fault == 'missing-image':
                    self.evidence['scenes'][0]['screens'][0]['screenshot_id'] = 'absent'
                elif fault == 'missing-control':
                    self.evidence['screenshots'][0]['visible_labels'] = ['Save draft']
                else:
                    self.evidence['scenes'][0]['screens'][0]['required_labels'] = ['Save draft']
                self.save()
                self.assert_not_exported()

    def test_every_scene_needs_evidence_even_when_other_scenes_are_complete(self):
        self.lesson['scenes'].append(dict(self.lesson['scenes'][0], id='second', title='Second operation'))
        self.save()
        self.assert_not_exported()

    def test_guide_review_must_be_explicit_current_and_after_the_capture(self):
        for fault in ['missing', 'failed', 'stale', 'old', 'no-timezone', 'boolean-schema']:
            with self.subTest(fault=fault):
                self.evidence = self.guide_fixture()
                self.save()
                if fault == 'missing':
                    self.evidence.pop('guide_review')
                elif fault == 'failed':
                    self.evidence['guide_review']['passed'] = False
                elif fault == 'stale':
                    self.evidence['guide_review']['content_sha256'] = '0' * 64
                elif fault == 'old':
                    self.evidence['guide_review']['reviewed_at'] = '2026-10-25T10:00:00Z'
                elif fault == 'no-timezone':
                    self.evidence['guide_review']['reviewed_at'] = '2026-10-25T12:02:00'
                else:
                    self.evidence['schema_version'] = True
                self.save(review=False)
                self.assert_not_exported()

    def test_changed_learner_text_invalidates_review_but_internal_metadata_does_not(self):
        self.lesson['capture_url'] = 'http://localhost:19104/new-internal-route'
        self.save(review=False)
        self.assertEqual(readiness_report(self.sources)['ready'], [self.lesson['id']])
        self.lesson['scenes'][0]['practice'] = 'A changed practice instruction.'
        self.save(review=False)
        self.assert_not_exported()

    def test_six_sector_examples_are_required_and_core_dictionary_format_is_supported(self):
        original = copy.deepcopy(self.lesson['sector_examples'])
        self.lesson['sector_examples'].pop()
        self.save(review=False)
        self.assert_not_exported()
        self.lesson['app'] = 'Core'
        self.evidence['screenshots'][0]['app'] = 'Core'
        self.lesson['sector_examples'] = {example['sector']: example['scenario'] for example in original}
        self.save()
        self.export()
        self.assertIn('Core configuration', (self.output / 'walkthroughs/index.html').read_text())

    def test_private_urls_paths_editor_links_and_tokens_in_learner_text_are_rejected(self):
        for unsafe in ['http://localhost:19104/calls', 'https://127.0.0.1/records', '//10.1.2.3/records',
                       'http://[::1]/calls', 'https://api.internal/records',
                       'https://web.descript.com/project/example', '/Users/operator/private/file.json',
                       'file:///private/tmp/record', 'pk.' + 'x' * 32,
                       'access_token=synthetic-example', 'Bearer synthetic-example',
                       'https://example.org/video?' + 'X-Amz-' + 'Signature=synthetic-example']:
            with self.subTest(unsafe=unsafe):
                self.lesson['summary'] = 'Open ' + unsafe
                self.lesson_file.write_text(json.dumps(self.lesson))
                self.assert_not_exported()
                issues = ' '.join(issue for item in readiness_report(self.sources)['excluded'] for issue in item['issues'])
                self.assertRegex(issues, 'unsafe URL|private|Credential')

    def test_production_labels_are_rejected_while_legitimate_draft_record_is_accepted(self):
        for label in ['Draft video', 'Preview walkthrough', 'Lesson in progress', 'Coming soon']:
            with self.subTest(label=label):
                self.lesson['summary'] = label
                self.lesson_file.write_text(json.dumps(self.lesson))
                self.assert_not_exported()
        self.lesson['summary'] = 'Save an incident record as a Draft.'
        self.save()
        self.assertEqual(len(self.export()), 1)

    def test_unsafe_asset_paths_and_symlinks_are_rejected(self):
        for unsafe in ['../outside.png', '/tmp/outside.png', 'captures/%2e%2e/record.png',
                       'https://example.org/record.png', 'private/record.png', 'captures\\record.png']:
            with self.subTest(path=unsafe):
                self.evidence = self.guide_fixture()
                self.evidence['screenshots'][0]['file'] = unsafe
                self.save()
                self.assert_not_exported()
        target = self.sources / 'captures/record.png'
        original = target.read_bytes()
        external = self.root / 'outside.png'
        external.write_bytes(original)
        target.unlink()
        target.symlink_to(external)
        self.evidence['screenshots'][0]['file'] = 'captures/record.png'
        self.save()
        self.assert_not_exported()

    def test_video_requires_validator_success_and_all_three_actual_playback_positions(self):
        self.video_fixture()
        self.evidence['browser_playback'].pop()
        self.evidence['validation_report'] = {'passed': True}
        self.lesson['playback_passed'] = True
        self.save()
        self.assert_not_exported()
        self.assertTrue(any('end' in issue for item in readiness_report(self.sources)['excluded'] for issue in item['issues']))

    def test_valid_video_contract_exports_hashed_media_and_no_private_proof_records(self):
        self.video_fixture()
        self.save()
        self.assertEqual(readiness_report(self.sources)['ready'], [self.lesson['id']])
        cards = self.export()
        self.assertEqual(cards[0]['kind'], 'Video walkthrough')
        for key in ('video', 'poster', 'captions', 'chapters'):
            self.assertFalse(cards[0][key].startswith('/'))
            self.assertTrue((self.output / cards[0][key]).is_file())
        self.assertEqual(json.loads((self.output / cards[0]['chapters']).read_text()), [{'start': 0, 'title': 'Save a record'}])
        self.assertEqual(cards[0]['video'], 'walkthroughs/assets/' + self.evidence['video']['sha256'] + '.mp4')
        page = self.lesson_html()
        self.assertIn('<video', page)
        self.assertIn('<track kind="captions"', page)
        self.assertNotIn('<track default', page)
        self.assertIn('Download captions', page)
        self.assertIn('data-start="0"', page)
        self.assertIn('Download video', page)
        self.assertNotIn('localhost', page)
        self.assertNotIn('proof/', page)
        public_assets = list((self.output / 'walkthroughs/assets').iterdir())
        self.assertEqual({path.suffix for path in public_assets}, {'.png', '.mp4', '.vtt'})
        self.assertTrue(all(len(path.stem) == 64 for path in public_assets))

    def test_stale_content_hash_or_playback_state_rejects_video(self):
        for fault in ['authoring', 'video-hash', 'error', 'paused', 'caption', 'missing-frame', 'missing-video', 'wrong-video-hash']:
            with self.subTest(fault=fault):
                self.video_fixture()
                if fault == 'authoring':
                    self.lesson['summary'] += ' Changed.'
                elif fault == 'video-hash':
                    self.evidence['browser_playback'][0]['video_sha256'] = '0' * 64
                elif fault == 'error':
                    self.evidence['browser_playback'][0]['media_error'] = {'code': 4}
                elif fault == 'paused':
                    self.evidence['browser_playback'][0]['paused'] = True
                elif fault == 'caption':
                    self.evidence['browser_playback'][0]['captions']['mode'] = 'hidden'
                elif fault == 'missing-frame':
                    self.evidence['rendered_segments'] = []
                elif fault == 'missing-video':
                    (self.sources / self.evidence['video']['file']).unlink()
                else:
                    self.evidence['video']['sha256'] = '0' * 64
                self.save()
                self.assert_not_exported()

    def test_public_captions_cannot_expose_private_urls_even_if_video_contract_passes(self):
        self.video_fixture()
        self.caption += ' Reference http://localhost:19104/private.'
        self.evidence['scenes'][0]['captions'][0]['text'] = self.caption
        self.evidence['rendered_segments'][0]['frame']['caption_text'] = self.caption
        for sample in self.evidence['browser_playback']:
            sample['captions']['text'] = self.caption
        self.evidence['video']['captions'] = self.asset('media/record.vtt', ('WEBVTT\n\n00:00.000 --> 00:30.000\n' + self.caption + '\n').encode())
        self.save()
        self.assert_not_exported()

    def test_readiness_revocation_removes_only_previously_owned_output(self):
        self.export()
        unrelated = self.output / 'index.html'
        unrelated.write_text('Parent home page')
        self.lesson['export_ready'] = False
        self.save()
        self.assert_not_exported()
        self.assertEqual(unrelated.read_text(), 'Parent home page')

    def test_unrelated_walkthrough_folder_is_never_replaced_or_removed(self):
        unrelated = self.output / 'walkthroughs'
        unrelated.mkdir(parents=True)
        (unrelated / 'index.html').write_text('A different site')
        with self.assertRaisesRegex(ValueError, 'unrelated'):
            self.export()
        self.lesson['export_ready'] = False
        self.save()
        self.assertEqual(self.export(), [])
        self.assertEqual((unrelated / 'index.html').read_text(), 'A different site')

    def test_duplicate_identifiers_are_excluded_and_valid_neighbors_still_export(self):
        duplicate = self.sources / 'expansion/lessons/duplicate.json'
        duplicate.write_text(self.lesson_file.read_text())
        self.assert_not_exported()
        self.assertEqual(readiness_report(self.sources)['ready'], [])
        duplicate.unlink()
        (self.sources / 'expansion/lessons/bad.json').write_text('{malformed')
        self.assertEqual(len(self.export()), 1)
        self.assertEqual(len(readiness_report(self.sources)['excluded']), 1)

    def test_invalid_direct_guide_input_returns_failed_report_without_throwing(self):
        for evidence in [None, [], {}, {'schema_version': 1, 'screenshots': []}]:
            with self.subTest(evidence=evidence):
                self.assertFalse(verify_guide_document(self.lesson, evidence, self.sources)['passed'])

    def test_export_cannot_overlap_source_records(self):
        for destination in [self.sources, self.sources / 'public', self.root]:
            with self.subTest(destination=destination):
                with self.assertRaisesRegex(ValueError, 'outside'):
                    write_expansion_site(destination, self.sources)


if __name__ == '__main__':
    unittest.main()
