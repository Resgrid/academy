"""V2 guards: temp fixtures, mocked read-only Git metadata, no live copy/process."""
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib.parse import urlunsplit

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / 'sources/demo/client-support'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


u = module('tested_unit_recording_v2', SUPPORT / 'unit_recording_support_v2.py')
fixtures = module('retained_v1_fixture_provider', Path(__file__).with_name('test_unit_recording_support.py'))


class UnitRecordingV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        binding = mock.patch.object(fixtures, 'u', u)
        binding.start()
        self.addCleanup(binding.stop)
        self.f = fixtures.Fixture(Path(self.temp.name).resolve())
        extra = {'src/clock.ts': (b'old clock\n', b'new UTC clock\n'),
                 'src/history.ts': (b'old history\n', b'new UTC history\n'),
                 'src/clock.test.ts': (b'old mock\n', b'new mock\n'),
                 'src/utc.test.ts': (b'', b'UTC regression\n')}
        patch = ''
        for name, (old, new) in extra.items():
            if old:
                self.f.original[name] = old
                self.f.write(self.f.source / name, old)
                self.f.baseline['source_files'][name] = fixtures.checksum(old)
            else:
                self.f.baseline['must_be_absent'].append(name)
            self.f.output[name] = new
            self.f.baseline['patched_files'][name] = fixtures.checksum(new)
            patch += ''.join(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True),
                                               fromfile='a/' + name if old else '/dev/null', tofile='b/' + name))
        third = 'demo/client-support/third.patch'
        self.f.write(self.f.layout.sources / third, patch.encode())
        self.f.baseline['patches'].append({'file': third, 'sha256': fixtures.checksum(patch.encode())})
        self.f.write(self.f.layout.support / 'prior/v1-proof.json', b'{"held":true}\n')
        self.f.baseline['prior_support_files'] = {'prior/v1-proof.json': u.digest(self.f.layout.support / 'prior/v1-proof.json')}
        self.f.original['src/parser.ts'] = b'existing UTC parser\n'
        self.f.write(self.f.source / 'src/parser.ts', self.f.original['src/parser.ts'])
        self.f.baseline['source_files']['src/parser.ts'] = fixtures.checksum(self.f.original['src/parser.ts'])
        self.f.write(self.f.source / 'node_modules/sdk/date.js', b'existing date SDK\n')
        self.f.baseline['dependency_source_files']['sdk/date.js'] = u.digest(self.f.source / 'node_modules/sdk/date.js')
        self.f.state['files'] = list(self.f.original)
        self.pin = mock.patch.object(u, 'BASELINE_SHA256', self.f.seal())
        self.pin.start()
        self.addCleanup(self.pin.stop)
        self.git = mock.patch.object(u, 'git_state', side_effect=lambda source: dict(self.f.state))
        self.git_mock = self.git.start()
        self.addCleanup(self.git.stop)
        process = mock.patch.object(u.subprocess, 'run', side_effect=AssertionError('No Git/process in guard fixtures'))
        process.start()
        self.addCleanup(process.stop)

    def test_plan_needs_no_source_git_or_credentials(self):
        before = sorted(str(p) for p in Path(self.temp.name).rglob('*'))
        with mock.patch.dict(os.environ, {}, clear=True):
            plan = u.preparation_plan(self.f.layout)
            launch = u.launch_plan(self.f.layout)
        self.assertEqual(len(plan['patches']), 3)
        self.assertTrue(plan['destination'].endswith('Unit-recording-v2-20261027'))
        self.assertEqual(launch['support_version'], u.VERSION)
        self.assertEqual(before, sorted(str(p) for p in Path(self.temp.name).rglob('*')))
        self.git_mock.assert_not_called()

    def test_all_three_patches_and_eight_outputs_preserve_originals(self):
        u.prepare(self.f.layout)
        target = self.f.destination
        self.assertEqual(u.verify_prepared(self.f.layout), target)
        for name, data in self.f.output.items():
            self.assertEqual((target / name).read_bytes(), data)
        for name, data in self.f.original.items():
            self.assertEqual((self.f.source / name).read_bytes(), data)
        self.assertFalse((target / '.env.development').exists())
        self.assertFalse((target / 'private').exists())
        self.assertEqual(json.loads((target / u.PROVENANCE).read_text())['support_version'], u.VERSION)

    def test_prior_version_proof_tamper_refused_before_destination(self):
        (self.f.layout.support / 'prior/v1-proof.json').write_bytes(b'changed')
        with self.assertRaises(u.SupportError):
            u.prepare(self.f.layout)
        self.assertFalse(self.f.destination.exists())

    def test_third_patch_tamper_refused(self):
        patch = self.f.layout.sources / self.f.baseline['patches'][2]['file']
        patch.write_text(patch.read_text() + '\n')
        with self.assertRaises(u.SupportError):
            u.prepare(self.f.layout)
        self.assertFalse(self.f.destination.exists())

    def test_existing_utc_test_refused(self):
        self.f.write(self.f.source / 'src/utc.test.ts', b'unknown existing change\n')
        with self.assertRaises(u.SupportError):
            u.prepare(self.f.layout)
        self.assertFalse(self.f.destination.exists())

    def test_original_utc_parser_and_date_sdk_are_guarded(self):
        for path in [self.f.source / 'src/parser.ts', self.f.source / 'node_modules/sdk/date.js']:
            data = path.read_bytes()
            path.write_bytes(b'changed')
            with self.assertRaises(u.SupportError):
                u.prepare(self.f.layout)
            path.write_bytes(data)
        self.assertFalse(self.f.destination.exists())

    def test_dirty_source_and_wrong_head_refused(self):
        for field, value in [('status', ' M changed'), ('head', 'unknown-head')]:
            with mock.patch.dict(self.f.state, {field: value}):
                with self.assertRaises(u.SupportError):
                    u.prepare(self.f.layout)
        self.assertFalse(self.f.destination.exists())

    def test_v1_and_original_destination_names_refused(self):
        for path in [self.f.layout.captures / 'Unit-recording-20261027', self.f.source]:
            with self.assertRaises(u.SupportError):
                u.preparation_plan(self.f.layout, path)

    def test_existing_v2_destination_preserved(self):
        self.f.destination.mkdir(parents=True)
        (self.f.destination / 'keep.txt').write_text('keep')
        with self.assertRaises(u.SupportError):
            u.prepare(self.f.layout)
        self.assertEqual((self.f.destination / 'keep.txt').read_text(), 'keep')

    def test_utc_output_tamper_refused_before_launch(self):
        u.prepare(self.f.layout)
        (self.f.destination / 'src/clock.ts').write_text('unknown later edit')
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_loopback_only_and_inherited_key_still_required(self):
        userinfo_origin = urlunsplit(('http', 'training-user@localhost:18967', '', '', ''))
        for url in ['https://example.org', 'http://localhost:18967/other', userinfo_origin]:
            with self.assertRaises(u.SupportError):
                u.launch_plan(self.f.layout, api_origin=url)
        u.prepare(self.f.layout)
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(u.subprocess, 'call') as call:
            with self.assertRaises(u.SupportError):
                u.launch(self.f.layout)
            call.assert_not_called()


class RetainedV2BundleTests(unittest.TestCase):
    def test_real_v2_bundle_loads_offline_and_preserves_v1(self):
        with mock.patch.object(u, 'git_state', side_effect=AssertionError('No Git')), mock.patch.dict(os.environ, {}, clear=True):
            baseline, patches, _ = u.load_bundle(u.Layout(SUPPORT))
        self.assertEqual((len(patches), len(baseline['patched_files']), len(baseline['dependency_source_files'])), (3, 8, 14))
        for name, expected in baseline['prior_support_files'].items():
            self.assertEqual(u.digest(SUPPORT / name), expected)

    def test_all_eight_real_outputs_from_retained_inputs_without_live_copy(self):
        baseline, patches, _ = u.load_bundle(u.Layout(SUPPORT))
        inputs = {
            'src/components/maps/map-view.web.tsx': SUPPORT / 'unit-camera/baseline/map-view.web.tsx',
            'src/components/calls/call-images-modal.tsx': SUPPORT / 'unit-images/baseline/call-images-modal.tsx',
            'src/components/calls/__tests__/call-images-modal.test.tsx': SUPPORT / 'unit-images/baseline/call-images-modal.test.tsx',
        }
        for name in baseline['source_files']:
            if name.startswith('src/components/check-in-timers/'):
                inputs[name] = SUPPORT / 'unit-check-in-time/before' / name
        with tempfile.TemporaryDirectory() as temporary:
            layout = u.Layout(Path(temporary).resolve() / 'sources/demo/client-support')
            for name, retained in inputs.items():
                self.assertEqual(u.digest(retained), baseline['source_files'][name])
                fixtures.Fixture.write(layout.source / name, retained.read_bytes())
            outputs = u.patch_outputs(layout, baseline, patches)
            self.assertEqual(len(outputs), 8)
            for name, data in outputs.items():
                self.assertEqual(hashlib.sha256(data).hexdigest(), baseline['patched_files'][name])
            for name, retained in inputs.items():
                self.assertEqual((layout.source / name).read_bytes(), retained.read_bytes())


if __name__ == '__main__':
    unittest.main()
