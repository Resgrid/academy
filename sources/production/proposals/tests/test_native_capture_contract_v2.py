"""Synthetic parser/geometry tests only; no native application evidence or IO."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import plistlib
import shutil
import struct
import unittest
import zlib

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec); spec.loader.exec_module(loaded)
    return loaded


v1_fixture = module('native_v1_synthetic_fixture', HERE / 'test_native_capture_contract_v1.py')
native = module('native_v2_unadopted_proposal', HERE.parent / 'native_capture_contract_v2.py')
NOW = v1_fixture.NOW
when = v1_fixture.when


def png(width, height):
    # Synthetic solid pixels; never simctl output or evidence of an application.
    chunk = v1_fixture.chunk
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\x12\x34\x56' * width) * height)) + chunk(b'IEND', b''))


class NativeV2Proposal(unittest.TestCase):
    def setUp(self):
        factory = v1_fixture.NativeContract(methodName='runTest')
        factory.setUp(); self.addCleanup(factory.doCleanups)
        self.roots = {k: v for k, v in factory.roots.items() if k in native.ROOTS}
        # V2 does not need or read bundle bytes. Delete even this fake fixture.
        shutil.rmtree(factory.roots['runtime'])
        self.asset, self.json_asset = factory.asset, factory.json_asset
        self.doc = copy.deepcopy(factory.doc)
        self.doc['schema'] = native.SCHEMA
        build = self.doc['build']
        build.update(mode='development_metro', source_git_revision='a' * 40, native_sdk='iphonesimulator27.1')
        info = plistlib.loads((self.roots['app'] / 'Info.plist').read_bytes())
        info['DTSDKName'] = build['native_sdk']
        build['info_plist'] = self.asset('app', 'Info.plist', plistlib.dumps(info))
        identity = native.source_identity_digest(build)
        self.receipts = []
        for index, category in enumerate(['entry_bundle', 'lazy_chunk']):
            measurement = native.stream_hash([b'synthetic test ', category.encode()])
            receipt = {'schema': native.STREAM_SCHEMA, 'session_id': factory.sid, 'udid': factory.udid,
                       'bundle_id': factory.bundle, 'request_id': f'33333333-3333-4333-8333-{index + 1:012d}',
                       'request_target_sha256': hashlib.sha256(category.encode()).hexdigest(), 'resource_category': category,
                       'source_identity_sha256': identity, 'method': 'development_response_stream_sha256',
                       'hash_stage': 'decoded_response_body', **measurement, 'response_status': 200,
                       'content_kind': 'hermes_bytecode', 'stream_started_at': when(-25 + index),
                       'stream_finished_at': when(-20 + index), 'transport_client_identity': 'not_authenticated_by_transport'}
            self.receipts.append(receipt)
        self.observed = {'session_id': factory.sid, 'udid': factory.udid, 'bundle_id': factory.bundle,
                         'source_identity_sha256': identity, 'method': 'native_runtime_and_metro_load_review',
                         'observed_through': when(-3), 'load_window_started_at': when(-30),
                         'request_ids': [x['request_id'] for x in self.receipts], 'entry_only': False,
                         'all_observed_loads_included': True, 'foreground_app_observed': True}
        build['runtime_js'] = {'method': 'stream_hashed_observed_load_set', 'coverage': 'complete_observed_session_load_set',
                               'lazy': True, 'entry_stream_sha256': self.receipts[0]['sha256'],
                               'stream_receipts': [], 'load_observation': {}}
        build['binding_review'].update(reviewed_at=when(-2), known_build_reviewed=True, stream_load_correspondence_reviewed=True)
        capture = self.doc['capture']
        capture.update(width=2732, height=2048, image=self.asset('assets', 'raw.png', png(2732, 2048)))
        capture['output_sha256'] = capture['image']['sha256']
        capture['display'] = {'orientation': 'landscape_left', 'dpr': 2,
                              'screen_points': {'width': 1366, 'height': 1024},
                              'app_viewport_points': {'x': 0, 'y': 0, 'width': 1366, 'height': 1024},
                              'method': 'xcuitest_frame_and_uiscreen_scale', 'measured_at': when(-2), 'receipt': {}}
        self.save_runtime(); self.save_geometry(); self.seal()

    def save_runtime(self):
        runtime = self.doc['build']['runtime_js']
        runtime['stream_receipts'] = [self.json_asset(f'stream-{i}.json', row) for i, row in enumerate(self.receipts)]
        runtime['load_observation'] = self.json_asset('observed-loads.json', self.observed)

    def save_geometry(self):
        display = self.doc['capture']['display']
        fields = ['method', 'measured_at', 'orientation', 'dpr', 'screen_points', 'app_viewport_points']
        row = {k: display[k] for k in fields}
        row.update(session_id=self.doc['session']['id'], udid=self.doc['session']['udid'], pixel_width=self.doc['capture']['width'], pixel_height=self.doc['capture']['height'])
        display['receipt'] = self.json_asset('geometry.json', row)

    def seal(self):
        self.doc['build']['binding_review']['identity_sha256'] = native.build_digest(self.doc['build'])
        self.doc['review']['metadata_sha256'] = native.review_digest(self.doc)

    def result(self):
        return native.validate(self.doc, self.roots, NOW)

    def reject(self, phrase):
        result = self.result()
        self.assertFalse(result['valid_traceability'], result)
        self.assertFalse(result['publishable'])
        self.assertIn(phrase, ' '.join(result['issues']))

    def test_synthetic_complete_loaded_set_without_any_retained_bundle(self):
        result = self.result()
        self.assertTrue(result['valid_traceability'], result)
        self.assertTrue(result['proposal_only'])
        self.assertFalse(result['publishable'])
        self.assertFalse(result['pixel_authenticity_proven'])
        self.assertNotIn('runtime', self.roots)
        self.assertFalse(any(p.suffix in ['.js', '.bundle'] for p in self.roots['assets'].rglob('*')))

    def test_fit_separates_dpr2_logical_geometry_from_less_than_point75_raw_scale(self):
        result = native.propose_landscape_fit(self.doc, self.roots, NOW)
        self.assertTrue(result['valid_fit_proposal'], result)
        fit = result['fit_proposal']
        self.assertLess(fit['raw_pixel_scale'], 0.75)
        self.assertEqual(fit['output_pixels_per_logical_point'], fit['raw_pixel_scale'] * 2)
        self.assertGreaterEqual(fit['output_pixels_per_logical_point'], 0.75)
        self.assertFalse(fit['cropped']); self.assertFalse(fit['rendered_frame_created'])
        rect = fit['image_rect_pixels']
        self.assertGreaterEqual(rect['y'], 48)
        self.assertLessEqual(rect['y'] + rect['height'], 960)
        self.assertEqual(fit['bindings']['source_png_sha256'], self.doc['capture']['image']['sha256'])
        self.assertEqual(fit['bindings']['native_metadata_sha256'], native.review_digest(self.doc))
        self.assertFalse(result['publishable'])

    def test_wrong_dpr_rejected_even_with_new_review_metadata(self):
        self.doc['capture']['display']['dpr'] = 1; self.save_geometry(); self.seal()
        self.reject('DPR/logical screen dimensions disagree')

    def test_wrong_logical_and_raw_dimensions_rejected(self):
        self.doc['capture']['display']['screen_points']['width'] = 1400; self.save_geometry(); self.seal()
        self.reject('DPR/logical screen dimensions disagree')

    def test_hash_bound_geometry_receipt_mismatch_rejected(self):
        self.doc['capture']['display']['method'] = 'native_screen_window_geometry_review'; self.seal()
        self.reject('declared DPR/viewport differs')

    def test_wrong_capture_method_never_relabels_native_as_browser(self):
        self.doc['capture']['method'] = 'browser_screenshot'; self.seal(); self.reject('genuine native provenance')

    def test_stale_source_identity_rejected_after_rehashing_reviews(self):
        self.doc['build']['source_git_revision'] = 'b' * 40; self.seal()
        self.reject('stale/wrong app/session/binary/source identity')

    def test_unknown_build_and_sdk_rejected(self):
        self.doc['build']['mode'] = 'unknown'; self.seal(); self.reject('unknown build branch')
        self.doc['build']['mode'] = 'development_metro'; self.doc['build']['native_sdk'] = 'iphonesimulator99.0'; self.seal()
        self.reject('SDK differs from actual installed Info.plist')

    def test_missing_stream_hash_rejected(self):
        del self.receipts[0]['sha256']; self.save_runtime(); self.seal(); self.reject('requires exactly fields')

    def test_response_stream_never_claims_authenticated_or_executed_identity(self):
        self.receipts[0]['executed_or_loaded_identity_proven'] = True; self.save_runtime(); self.seal()
        self.reject('cannot authenticate a simulator client or prove loaded/executed identity')

    def test_incomplete_empty_and_retained_payload_receipts_rejected(self):
        for field, value in [('stream_completed', False), ('byte_length', 0), ('raw_bundle_retained', True)]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.receipts)
                self.receipts[0][field] = value; self.save_runtime(); self.seal()
                self.assertFalse(self.result()['valid_traceability'])
                self.receipts = original

    def test_unknown_runtime_format_rejected(self):
        self.receipts[0]['content_kind'] = 'guessed_bundle'; self.save_runtime(); self.seal(); self.reject('unknown build/runtime format')

    def test_lazy_entry_only_cannot_establish_load_coverage(self):
        self.receipts = self.receipts[:1]; self.observed['request_ids'] = [self.receipts[0]['request_id']]
        self.save_runtime(); self.seal(); self.reject('lazy entry-only hash')

    def test_missing_chunk_observation_or_unknown_request_rejected(self):
        self.observed['request_ids'] = self.observed['request_ids'][:1]; self.save_runtime(); self.seal()
        self.reject('all observed entry/lazy chunk loads')

    def test_recent_native_load_and_geometry_observations_required(self):
        self.observed['observed_through'] = when(-15); self.doc['build']['binding_review']['reviewed_at'] = when(-4)
        self.save_runtime(); self.seal(); self.reject('current capture')

    def test_unknown_or_portrait_does_not_become_landscape(self):
        self.doc['capture']['display']['orientation'] = 'unknown'; self.save_geometry(); self.seal(); self.reject('unknown is not landscape')
        capture = self.doc['capture']; capture.update(width=2048, height=2732, image=self.asset('assets', 'raw.png', png(2048, 2732)))
        capture['output_sha256'] = capture['image']['sha256']
        capture['display'].update(orientation='portrait', screen_points={'width': 1024, 'height': 1366}, app_viewport_points={'x': 0, 'y': 0, 'width': 1024, 'height': 1366})
        self.save_geometry(); self.seal()
        self.assertTrue(self.result()['valid_traceability'])
        fit = native.propose_landscape_fit(self.doc, self.roots, NOW)
        self.assertFalse(fit['valid_fit_proposal']); self.assertIsNone(fit['fit_proposal'])
        self.assertIn('measured portrait', ' '.join(fit['issues']))

    def test_small_or_out_of_bounds_logical_viewport_rejected(self):
        viewport = self.doc['capture']['display']['app_viewport_points']
        viewport['width'] = 2000; self.save_geometry(); self.seal(); self.reject('outside full native screen')
        viewport.update(width=800, height=600); self.save_geometry(); self.seal()
        fit = native.propose_landscape_fit(self.doc, self.roots, NOW)
        self.assertFalse(fit['valid_fit_proposal']); self.assertIn('logical UI points', ' '.join(fit['issues']))

    def test_labels_and_required_source_review_binding_cannot_drift(self):
        self.doc['capture']['visible_labels'].append('Complete')
        self.reject('current actual pixel/identity')

    def test_no_error_review_cannot_approve_native_redbox(self):
        self.doc['review']['no_blocking_error'] = False; self.seal(); self.reject('actual pixel/identity')

    def test_url_query_body_and_bundle_file_fields_forbidden(self):
        for key, value in [('url', 'not-a-real-url'), ('query', 'redacted'), ('body', 'synthetic'), ('bundle_file', 'served.js')]:
            with self.subTest(key=key):
                original = copy.deepcopy(self.receipts)
                self.receipts[0][key] = value; self.save_runtime(); self.seal(); self.reject('invented DOM/URL/command')
                self.receipts = original

    def test_stream_hash_measures_incrementally_and_returns_no_payload_or_execution_claim(self):
        parts = [b'synthetic ', b'payload']
        receipt = native.stream_hash(iter(parts))
        self.assertEqual(receipt['sha256'], hashlib.sha256(b''.join(parts)).hexdigest())
        self.assertEqual(receipt['byte_length'], 17)
        self.assertFalse(receipt['raw_bundle_retained'])
        self.assertFalse(receipt['executed_or_loaded_identity_proven'])
        self.assertNotIn('body', receipt)
        with self.assertRaises(ValueError): native.stream_hash([])
        with self.assertRaises(ValueError): native.stream_hash(['not bytes'])
        def interrupted():
            yield b'partial'
            raise OSError('synthetic interrupted stream')
        with self.assertRaises(OSError): native.stream_hash(interrupted())


if __name__ == '__main__':
    unittest.main()
