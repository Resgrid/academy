"""Synthetic traceability tests only: no genuine app/media or native UI claim."""
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import plistlib
import struct
import tempfile
import unittest
import zlib

MODULE = Path(__file__).resolve().parents[1] / 'native_capture_contract_v1.py'
spec = importlib.util.spec_from_file_location('native_contract_proposal', MODULE)
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def when(seconds):
    return (NOW + timedelta(seconds=seconds)).isoformat()


def chunk(kind, body):
    return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xffffffff)


def png():
    # Deliberately synthetic pixels; they test the parser, never a capture claim.
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 320, 480, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\x12\x34\x56' * 320) * 480)) + chunk(b'IEND', b''))


class NativeContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.roots = {key: Path(self.temp.name) / key for key in native.ROOTS}
        for path in self.roots.values():
            path.mkdir()
        self.udid = '11111111-1111-4111-8111-111111111111'
        self.sid = '22222222-2222-4222-8222-222222222222'
        self.bundle = native.BUNDLES['Unit']
        self.device = 'com.apple.CoreSimulator.SimDeviceType.iPhone-18-Pro'
        self.runtime = 'com.apple.CoreSimulator.SimRuntime.iOS-27-0'
        session_receipt = {'session_id': self.sid, 'udid': self.udid, 'created_at': when(-60),
                           'command': ['xcrun', 'simctl', 'create', 'Academy Training Synthetic Fixture', self.device, self.runtime], 'exit_code': 0}
        self.ledger = {'session_id': self.sid, 'udid': self.udid, 'bundle_id': self.bundle,
                       'policy': {name: True for name in native.FLAGS}, 'actions': [
                           {'id': 'tap-save', 'at': when(-10), 'method': 'human_simulator_ui', 'kind': 'tap', 'target': 'Save progress', 'normal_ui': True, 'typed_value_recorded': False},
                           {'id': 'observe', 'at': when(-3), 'method': 'human_simulator_ui', 'kind': 'observe_screen', 'target': 'Draft', 'normal_ui': True, 'typed_value_recorded': False}]}
        image = self.asset('assets', 'raw.png', png())
        build = {'bundle_id': self.bundle, 'executable': self.asset('app', 'UnitFixture', b'\xcf\xfa\xed\xfe' + b'\0' * 100),
                 'info_plist': self.asset('app', 'Info.plist', plistlib.dumps({'CFBundleIdentifier': self.bundle, 'CFBundleExecutable': 'UnitFixture', 'DTPlatformName': 'iphonesimulator'})),
                 'sources': [self.asset('source', 'package.json', b'{"name":"synthetic-contract-test"}'),
                             self.asset('source', 'ios/Podfile.lock', b'SYNTHETIC TEST LOCK'),
                             self.asset('source', 'src/count.tsx', b'// synthetic contract test source')],
                 'modules': [self.asset('dependencies', 'react-native/Alert.js', b'// synthetic contract module')],
                 'runtime_js': self.asset('runtime', 'served.js', b'// synthetic runtime, no execution'),
                 'binding_review': {'passed': True, 'reviewer': 'Synthetic test assertion only', 'reviewed_at': when(-4), 'identity_sha256': '', 'binary_source_runtime_correspondence': True}}
        self.doc = {'schema': native.SCHEMA, 'app': 'Unit', 'kind': 'application_screenshot',
                    'session': {'id': self.sid, 'udid': self.udid, 'device_type': self.device, 'runtime': self.runtime, 'os_version': '27.0',
                                'created_at': when(-60), 'owner': 'academy_training', 'dedicated': True, 'user_session_reused': False,
                                'creation_receipt': self.json_asset('creation.json', session_receipt)},
                    'build': build, 'ui_ledger': self.json_asset('ui.json', self.ledger),
                    'capture': {'method': 'ios_simulator_screenshot', 'image': image, 'width': 320, 'height': 480,
                                'started_at': when(-2), 'captured_at': when(-1.5), 'finished_at': when(-1),
                                'command': ['xcrun', 'simctl', 'io', self.udid, 'screenshot', '--type=png', 'raw.png'],
                                'exit_code': 0, 'output_sha256': image['sha256'], 'last_action_id': 'observe',
                                'foreground': {'bundle_id': self.bundle, 'state': 'running_foreground', 'surface': 'app', 'method': 'human_simulator_ui', 'checked_at': when(-2)},
                                'visible_labels': ['Inventory count', 'Draft', 'Save progress'], 'required_labels': ['Draft', 'Save progress'], 'ui_sources': ['src/count.tsx']},
                    'review': {'reviewer': 'Synthetic test assertion only', 'reviewed_at': when(0), 'metadata_sha256': '', **{name: True for name in native.REVIEW_FLAGS}}}
        self.seal()

    def asset(self, root, name, data):
        path = self.roots[root] / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {'file': name, 'sha256': hashlib.sha256(data).hexdigest()}

    def json_asset(self, name, value):
        return self.asset('assets', name, json.dumps(value).encode())

    def seal(self):
        self.doc['build']['binding_review']['identity_sha256'] = native.build_digest(self.doc['build'])
        self.doc['review']['metadata_sha256'] = native.review_digest(self.doc)

    def ledger_changed(self):
        self.doc['ui_ledger'] = self.json_asset('ui.json', self.ledger)
        self.seal()

    def result(self):
        return native.validate(self.doc, self.roots, NOW)

    def reject(self, phrase):
        result = self.result()
        self.assertFalse(result['valid_traceability'], result)
        self.assertFalse(result['publishable'])
        self.assertIn(phrase, ' '.join(result['issues']))

    def test_synthetic_traceability_shape_permits_legitimate_draft_but_never_authenticates_pixels_or_publishes(self):
        result = self.result()
        self.assertTrue(result['valid_traceability'], result)
        self.assertTrue(result['proposal_only'])
        self.assertFalse(result['publishable'])
        self.assertFalse(result['pixel_authenticity_proven'])

    def test_illustrated_substitute_rejected_even_with_resealed_metadata(self):
        self.doc['kind'] = 'illustrated_slide'; self.seal(); self.reject('illustrated substitutes')

    def test_fake_browser_method_rejected(self):
        self.doc['capture']['method'] = 'browser_screenshot'; self.seal(); self.reject('genuine native provenance')

    def test_invented_url_dom_or_icon_name_fields_rejected(self):
        for key, value in [('url', 'http://localhost:19103/inventory'), ('dom_file', 'invented.txt'), ('visible_controls', [{'accessible_name': 'Complete'}])]:
            with self.subTest(key=key):
                original = copy.deepcopy(self.doc)
                self.doc['capture'][key] = value; self.seal(); self.reject('invented DOM/URL/command')
                self.doc = original

    def test_raw_png_missing(self):
        (self.roots['assets'] / 'raw.png').unlink(); self.reject('must exist')

    def test_wrong_or_missing_raw_hash(self):
        self.doc['capture']['image']['sha256'] = '0' * 64; self.seal(); self.reject('asset bytes changed')
        self.doc['capture']['image']['sha256'] = hashlib.sha256(png()).hexdigest()
        self.doc['capture']['output_sha256'] = '0' * 64; self.seal(); self.reject('raw simctl output')
        del self.doc['capture']['image']['sha256']; self.seal(); self.reject('requires exactly')

    def test_capture_crc_failure_even_if_attacker_rehashes(self):
        data = bytearray(png()); data[-1] ^= 1
        self.doc['capture']['image'] = self.asset('assets', 'raw.png', data)
        self.doc['capture']['output_sha256'] = self.doc['capture']['image']['sha256']; self.seal(); self.reject('CRC mismatch')

    def test_dimensions_must_be_actual_raw_png(self):
        self.doc['capture']['width'] = 1920; self.seal(); self.reject('dimensions do not match')

    def test_missing_visible_control(self):
        self.doc['capture']['required_labels'].append('Complete'); self.seal(); self.reject('not visibly reviewed')

    def test_changed_labels_invalidate_existing_review(self):
        self.doc['capture']['visible_labels'].append('Complete'); self.reject('current actual pixel')

    def test_occluded_or_unreviewed_capture_rejected(self):
        self.doc['review']['controls_unobstructed'] = False; self.reject('actual pixel')
        self.doc['review']['controls_unobstructed'] = True
        self.doc['review']['passed'] = False; self.reject('actual pixel')

    def test_reused_user_session_rejected(self):
        self.doc['session']['user_session_reused'] = True; self.seal(); self.reject('never existing user apps')

    def test_implicit_booted_target_rejected(self):
        self.doc['capture']['command'][3] = 'booted'; self.seal(); self.reject('explicit dedicated-device')

    def test_wrong_creation_or_capture_device_rejected(self):
        receipt = json.loads((self.roots['assets'] / 'creation.json').read_text())
        receipt['udid'] = self.sid; self.doc['session']['creation_receipt'] = self.json_asset('creation.json', receipt)
        self.seal(); self.reject('actual dedicated session creation')

    def test_wrong_os_runtime_rejected(self):
        self.doc['session']['os_version'] = '26.0'; self.seal(); self.reject('OS version must agree')

    def test_binary_or_module_source_drift_rejected(self):
        (self.roots['app'] / 'UnitFixture').write_bytes(b'changed')
        self.reject('asset bytes changed')
        self.doc['build']['executable'] = self.asset('app', 'UnitFixture', b'\xcf\xfa\xed\xfe' + b'\0' * 100)
        (self.roots['dependencies'] / 'react-native/Alert.js').write_text('changed')
        self.reject('asset bytes changed')

    def test_runtime_js_drift_rejected(self):
        (self.roots['runtime'] / 'served.js').write_text('wrong runtime'); self.reject('asset bytes changed')

    def test_rehashed_binary_still_requires_new_identity_review(self):
        self.doc['build']['executable'] = self.asset('app', 'UnitFixture', b'\xcf\xfa\xed\xfe' + b'new bytes')
        self.doc['review']['metadata_sha256'] = native.review_digest(self.doc)
        self.reject('binary/source/module/executed-JS')

    def test_no_build_runtime_correspondence_claim_without_actual_review(self):
        self.doc['build']['binding_review']['binary_source_runtime_correspondence'] = False
        self.seal(); self.reject('actual current binary')

    def test_mismatched_bundle_plist_rejected(self):
        self.doc['build']['info_plist'] = self.asset('app', 'Info.plist', plistlib.dumps({'CFBundleIdentifier': 'wrong.app', 'DTPlatformName': 'iphonesimulator'}))
        self.seal(); self.reject('same actual simulator application')

    def test_unknown_mapped_screen_source_rejected(self):
        self.doc['capture']['ui_sources'] = ['src/unrecorded.tsx']; self.seal(); self.reject('mapped screen source')

    def test_api_or_storage_injection_is_not_a_ui_action_even_with_resealed_hashes(self):
        for kind in ['api_write', 'storage_injection', 'evaluate_script', 'grant_permission', 'sign_attestation']:
            with self.subTest(kind=kind):
                self.ledger['actions'][0]['kind'] = kind; self.ledger_changed(); self.reject('ordinary visible UI interaction')

    def test_permission_attestation_reset_or_launch_bypass_rejected(self):
        for flag in native.FLAGS:
            with self.subTest(flag=flag):
                self.ledger['policy'][flag] = False; self.ledger_changed(); self.reject('no hidden writes')
                self.ledger['policy'][flag] = True

    def test_wrong_ledger_session(self):
        self.ledger['udid'] = self.sid; self.ledger_changed(); self.reject('wrong simulator/session/app')

    def test_stale_reordered_or_future_ui_ledger_rejected(self):
        self.ledger['actions'][-1]['at'] = when(-45); self.ledger_changed(); self.reject('chronology')
        self.ledger['actions'][0]['at'] = when(-55); self.ledger_changed(); self.reject('stale')
        self.ledger['actions'][-1]['at'] = when(5); self.ledger_changed(); self.reject('future')

    def test_typed_credential_values_not_recorded(self):
        self.ledger['actions'][0]['typed_value_recorded'] = True; self.ledger_changed(); self.reject('never store typed credential')

    def test_foreground_identity_and_freshness(self):
        self.doc['capture']['foreground']['bundle_id'] = 'com.apple.springboard'; self.seal(); self.reject('foreground observation')
        self.doc['capture']['foreground']['bundle_id'] = self.bundle
        self.doc['capture']['foreground']['checked_at'] = when(-15); self.seal(); self.reject('immediately precede')

    def test_review_before_capture(self):
        self.doc['review']['reviewed_at'] = when(-10); self.reject('must follow capture')

    def test_traversal_and_symlink_escape(self):
        self.doc['capture']['image']['file'] = '../outside.png'
        self.doc['capture']['command'][-1] = '../outside.png'; self.seal(); self.reject('confined relative')
        outside = Path(self.temp.name) / 'outside.png'; outside.write_bytes(png())
        target = self.roots['assets'] / 'link.png'; target.symlink_to(outside)
        self.doc['capture']['image']['file'] = 'link.png'; self.doc['capture']['command'][-1] = 'link.png'; self.seal(); self.reject('symlink escape')

    def test_runtime_bundle_cannot_be_staged_under_public_assets(self):
        self.roots['runtime'] = self.roots['assets'] / 'private-runtime'; self.reject('outside public screenshot assets')

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            native.unique_json('{"app":"Unit","app":"Responder"}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            native.unique_json('{"x":NaN}')


if __name__ == '__main__':
    unittest.main()
