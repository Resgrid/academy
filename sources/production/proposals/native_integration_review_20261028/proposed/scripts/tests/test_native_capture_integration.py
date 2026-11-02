"""PROPOSAL synthetic contracts only; no genuine native screenshot or video.

No application, simulator, browser, media service or real renderer is operated.
Temporary parser fixtures cannot become actual reviewed/public evidence.
"""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import wave

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import native_capture_contract as contract
from native_capture_source import NativeContext, validate_native_source
import render_walkthrough as renderer
from verify_capture_evidence import verify_document
import expansion_site as exporter

# Works both inside the isolated review copy and at the proposed destination.
FIXTURE = next(parent / 'sources/production/proposals/tests/test_native_capture_contract_v2.py'
               for parent in Path(__file__).resolve().parents
               if (parent / 'sources/production/proposals/tests/test_native_capture_contract_v2.py').is_file())
spec = importlib.util.spec_from_file_location('native_integration_synthetic_fixture', FIXTURE)
fixture_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture_module)


class NativeIntegrationProposal(unittest.TestCase):
    def setUp(self):
        self.factory = fixture_module.NativeV2Proposal(methodName='runTest')
        self.factory.setUp(); self.addCleanup(self.factory.doCleanups)
        self.root = self.factory.roots['assets'].parent
        self.context = NativeContext(self.factory.roots)
        self.save_native_document()
        self.caption = 'Select Save progress to keep Draft.'
        self.video = self.asset('video.mp4', b'SYNTHETIC identity fixture only; not actual encoded video')
        self.video.update(width=1920, height=1080, duration_seconds=30, assembled_at='2026-01-01T01:00:00Z')
        self.video['captions'] = self.asset('captions.vtt', ('WEBVTT\n\n00:00.000 --> 00:30.000\n' + self.caption + '\n').encode())
        self.frame = self.asset('frame.png', fixture_module.png(1920, 1080))
        self.frame.update(width=1920, height=1080, time=15, video_sha256=self.video['sha256'], application_visible=True, review_status='synthetic_review_fixture', visible_labels=['Inventory count', 'Draft', 'Save progress'], reviewed_control_names=[], caption_text=self.caption)
        self.bind_frame()

    def asset(self, name, data):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)
        return {'file': name, 'sha256': hashlib.sha256(data).hexdigest()}

    def save_native_document(self):
        doc = self.factory.doc
        ref = self.asset('assets/native-evidence.json', json.dumps(doc).encode())
        self.row = {'id': 'native-unit-count', 'app': 'Unit', 'kind': 'application_screenshot',
                    'file': 'assets/' + doc['capture']['image']['file'], 'sha256': doc['capture']['image']['sha256'],
                    'width': doc['capture']['width'], 'height': doc['capture']['height'],
                    'provenance': {'method': 'ios_simulator_screenshot', 'captured_at': doc['capture']['captured_at']},
                    'native_evidence': ref, 'visible_labels': doc['capture']['visible_labels'],
                    'required_labels': doc['capture']['required_labels'], 'visible_controls': [],
                    'visible_field_text': [], 'eligible_for_lesson': True}

    def bind_frame(self):
        source = validate_native_source(self.row, self.root, 'Unit', self.context)
        self.frame['native_binding'] = source['native_binding']
        self.frame['native_frame_review'] = {
            'passed': True, 'reviewer': 'SYNTHETIC test assertion, not an actual review',
            'reviewed_at': datetime.now(timezone.utc).isoformat(), 'sha256': self.frame['sha256'],
            'video_sha256': self.video['sha256'], 'source_screenshot_sha256': self.row['sha256'],
            'native_binding_sha256': contract.digest(source['native_binding']),
            'visible_labels_sha256': contract.digest(self.frame['visible_labels']),
            'caption_text_sha256': contract.digest(self.caption),
            **{key: True for key in ['application_visible', 'raw_full_viewport_visible', 'controls_legible', 'caption_text_verified', 'no_blocking_error', 'no_private_values_visible']}}

    def evidence(self):
        playback = []
        for position, at in [('beginning', 2), ('middle', 15), ('end', 28)]:
            playback.append({'position': position, 'video_sha256': self.video['sha256'],
                             'url': 'http://localhost:18999/synthetic-review', 'current_src': 'http://localhost:18999/video.mp4',
                             'captured_at': '2026-01-01T01:01:00Z', 'previous_time': at - .5, 'current_time': at,
                             'duration_seconds': 30, 'video_width': 1920, 'video_height': 1080,
                             'ready_state': 4, 'network_state': 1, 'paused': False, 'ended': False,
                             'media_error': None, 'console_errors': [], 'captions': {'mode': 'showing', 'text': self.caption},
                             'screenshot': self.asset('proof/' + position + '.png', fixture_module.png(1280, 720))})
        return {'schema_version': 1, 'lesson_id': 'synthetic-native-unit', 'primary_app': 'Unit', 'video': self.video,
                'screenshots': [self.row], 'scenes': [{'id': 'count', 'kind': 'operational', 'start': 0, 'end': 30,
                'screens': [{'screenshot_id': self.row['id'], 'start': 0, 'end': 30}],
                'captions': [{'start': 0, 'end': 30, 'text': self.caption, 'screenshot_id': self.row['id'], 'required_labels': ['Save progress', 'Draft']}]}],
                'rendered_segments': [{'scene_id': 'count', 'screenshot_id': self.row['id'], 'start': 0, 'end': 30, 'frame': self.frame}],
                'browser_playback': playback}

    def test_valid_source_returns_only_traceability_and_never_publishable_or_browser_url(self):
        report = validate_native_source(self.row, self.root, 'Unit', self.context)
        self.assertTrue(report['traceability_passed']); self.assertFalse(report['publishable'])
        self.assertNotIn('url', self.row['provenance'])
        self.assertLess(report['layout']['raw_pixel_scale'], .75)
        self.assertGreaterEqual(report['layout']['output_pixels_per_logical_point'], .75)
        self.assertFalse(report['layout']['cropped'])

    def test_default_gate_cannot_trust_native_fields_without_explicit_roots(self):
        self.row['publishable'] = True
        report = verify_document(self.evidence(), self.root)
        self.assertFalse(report['passed']); self.assertIn('NativeContext', ' '.join(report['issues']))
        with self.assertRaises(ValueError): validate_native_source(self.row, self.root, 'Unit', self.context)

    def test_self_approval_or_record_roots_never_enable_native(self):
        for key, value in [('publishable', True), ('native_approved', True), ('native_context', {}), ('native_roots', {})]:
            with self.subTest(key=key):
                row = dict(self.row, **{key: value})
                with self.assertRaisesRegex(ValueError, 'self-approval fields forbidden'):
                    validate_native_source(row, self.root, 'Unit', self.context)

    def test_synthetic_full_contract_keeps_all_frame_and_playback_gates(self):
        evidence = self.evidence()
        self.assertTrue(verify_document(evidence, self.root, self.context)['passed'])
        evidence['browser_playback'] = []
        self.assertFalse(verify_document(evidence, self.root, self.context)['passed'])

    def test_no_native_frame_review_is_automatically_approved(self):
        self.frame['native_frame_review'] = None
        report = verify_document(self.evidence(), self.root, self.context)
        self.assertFalse(report['passed']); self.assertIn('native encoded-frame review', ' '.join(report['issues']))

    def test_native_frame_source_master_fit_caption_and_labels_are_bound(self):
        for field, changed in [('native_binding', {}), ('caption_text', 'Select Draft.'), ('visible_labels', ['Draft'])]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.frame); self.frame[field] = changed
                self.assertFalse(verify_document(self.evidence(), self.root, self.context)['passed'])
                self.frame = original

    def test_wrong_method_cannot_relabel_native_as_browser(self):
        self.row['provenance'] = {'method': 'browser_screenshot', 'url': 'http://localhost:19103/count', 'captured_at': self.factory.doc['capture']['captured_at']}
        report = verify_document(self.evidence(), self.root, self.context)
        self.assertFalse(report['passed']); self.assertIn('cannot be relabeled', ' '.join(report['issues']))

    def test_unknown_primary_and_native_app_identity_rejected(self):
        for primary in [None, 'Core', 'Responder', 'IC']:
            with self.subTest(primary=primary):
                with self.assertRaisesRegex(ValueError, 'Unit primary identity'):
                    validate_native_source(self.row, self.root, primary, self.context)

    def test_dpr_tamper_fails_even_after_resealed_metadata(self):
        self.factory.doc['capture']['display']['dpr'] = 1; self.factory.save_geometry(); self.factory.seal(); self.save_native_document()
        with self.assertRaisesRegex(ValueError, 'DPR/logical screen'):
            validate_native_source(self.row, self.root, 'Unit', self.context)

    def test_missing_or_unreadable_actual_source_asset_does_not_use_cached_pass(self):
        (self.factory.roots['source'] / 'package.json').unlink()
        with self.assertRaisesRegex(ValueError, 'must exist'):
            validate_native_source(self.row, self.root, 'Unit', self.context)

    def test_raw_png_changed_or_missing_is_rejected(self):
        (self.factory.roots['assets'] / 'raw.png').write_bytes(b'not a PNG')
        with self.assertRaisesRegex(ValueError, 'source asset hash changed'):
            validate_native_source(self.row, self.root, 'Unit', self.context)

    def test_key_bearing_bundle_retention_and_missing_stream_hash_rejected(self):
        self.factory.receipts[0]['raw_bundle_retained'] = True; self.factory.save_runtime(); self.factory.seal(); self.save_native_document()
        with self.assertRaisesRegex(ValueError, 'without retaining key-bearing'):
            validate_native_source(self.row, self.root, 'Unit', self.context)

    def test_browser_dom_or_native_icon_names_are_not_literal_native_evidence(self):
        for key, value in [('dom_file', 'invented.txt'), ('visible_controls', [{'accessible_name': 'Save progress'}])]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    validate_native_source(dict(self.row, **{key: value}), self.root, 'Unit', self.context)

    def test_browser_pixel_scale_floor_is_not_weakened(self):
        with self.assertRaises(renderer.AssemblyError): renderer.layout(2732, 2048)
        self.assertGreaterEqual(renderer.layout(1434, 773)['scale'], .75)

    def test_public_screenshot_branch_needs_context_and_preserves_true_native_method(self):
        evidence = self.evidence()
        with self.assertRaises(exporter.PublicationError): exporter._screenshots(evidence, self.root, 'Unit')
        result = exporter._screenshots(evidence, self.root, 'Unit', self.context)
        self.assertEqual(result[self.row['id']]['provenance']['method'], 'ios_simulator_screenshot')
        self.assertNotIn('url', result[self.row['id']]['provenance'])

    def test_renderer_checks_source_but_generates_no_review_flags_or_publication(self):
        lesson = {'id': 'synthetic-native-unit', 'app': 'Unit', 'title': 'Synthetic fixture',
                  'scenes': [{'id': 'count', 'title': 'Count', 'narration': self.caption, 'required_labels': ['Save progress', 'Draft']}]}
        with wave.open(str(self.root / 'voice.wav'), 'wb') as stream:
            stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(48000); stream.writeframes(b'\0\0' * 48000)
        caption = self.asset('voice.srt', ('1\n00:00:00,000 --> 00:00:01,000\n' + self.caption + '\n\n').encode())
        voice = {'file': 'voice.wav', 'sha256': hashlib.sha256((self.root / 'voice.wav').read_bytes()).hexdigest()}
        at = '2026-01-01T01:00:00Z'
        approval = lambda digest, **values: {'sha256': digest, 'reviewer': 'SYNTHETIC test, not listening', 'reviewed_at': at, **values}
        manifest = self.asset('manifest.json', json.dumps({'screenshots': [self.row]}).encode())
        plan = {'schema_version': 1, 'lesson_id': lesson['id'], 'duration_seconds': 1,
                'narration': {**voice, 'kind': 'approved_natural_narration', 'approval': approval(voice['sha256'], complete_natural_narration=True)},
                'captions': {**caption, 'kind': 'speech_timed_srt', 'approval': approval(caption['sha256'], audio_sha256=voice['sha256'], speech_timing_reviewed=True)},
                'capture_manifests': [manifest], 'screenshot_reviews': {self.row['id']: approval(self.row['sha256'], application_visible=True, labels_legible=True, no_errors=True)},
                'scenes': [{'id': 'count', 'start': 0, 'end': 1, 'screens': [{'screenshot_id': self.row['id'], 'start': 0, 'end': 1}],
                            'captions': [{'cue': 1, 'screenshot_id': self.row['id'], 'required_labels': ['Save progress', 'Draft']}]}]}
        lp, pp = self.root / 'lesson.json', self.root / 'plan.json'
        lp.write_text(json.dumps(lesson)); pp.write_text(json.dumps(plan))
        with self.assertRaises(renderer.AssemblyError): renderer.validate_inputs(lp, pp, self.root)
        recipe = renderer.validate_inputs(lp, pp, self.root, self.context)
        source = recipe['screenshots'][self.row['id']]
        self.assertLess(source['layout']['raw_pixel_scale'], .75)
        self.assertIn('native_binding', source)
        self.assertNotIn('native_frame_review', source)
        self.assertFalse(any(path.suffix == '.mp4' for path in self.root.glob('output*')))


if __name__ == '__main__':
    unittest.main()
