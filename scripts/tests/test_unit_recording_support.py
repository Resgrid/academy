"""Fail-closed Unit support tests using only synthetic temp files and a fake Git boundary."""
import contextlib
import difflib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / 'sources/demo/client-support'
spec = importlib.util.spec_from_file_location('tested_unit_recording_support', SUPPORT / 'unit_recording_support.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


def checksum(data):
    return hashlib.sha256(data).hexdigest()


class Fixture:
    def __init__(self, root):
        self.layout = u.Layout(root / 'sources/demo/client-support')
        self.layout.support.mkdir(parents=True)
        self.source = self.layout.source
        self.source.mkdir(parents=True)
        (self.source / '.git').mkdir()
        self.destination = self.layout.default_destination
        self.original = {
            'src/map.ts': b'center\nold map\n',
            'src/images.ts': b'old read\n',
            'src/images.test.ts': b'old tests\n',
            'package.json': b'{"version":"training"}\n',
            'yarn.lock': b'pinned dependencies\n',
            'assets/training.txt': b'fictional asset\n',
            '.env.development': b'sample environment excluded\n',
            'private/credentials.json': b'sample private fixture excluded\n',
        }
        self.output = {'src/map.ts': b'center\nnew map\n',
                       'src/camera.test.ts': b'new camera regression\n',
                       'src/images.ts': b'new web read\n',
                       'src/images.test.ts': b'new tests\n'}
        for name, data in self.original.items():
            self.write(self.source / name, data)
        self.dependencies = {'sdk/library.js': b'reviewed SDK\n', 'sdk/package.json': b'{"version":"fixture"}\n'}
        for name, data in self.dependencies.items():
            self.write(self.source / 'node_modules' / name, data)
        self.write(self.source / 'node_modules/expo/bin/cli', b'// synthetic CLI; never executed\n')
        for name in u.HELPERS:
            self.write(self.layout.support / name, ('fixture helper ' + name).encode())
        self.baseline = {'schema_version': 1, 'app': 'Unit', 'source_git_revision': 'fixture-pinned-head',
                         'source_files': {name: checksum(self.original[name]) for name in ('src/map.ts', 'src/images.ts', 'src/images.test.ts')},
                         'must_be_absent': ['src/camera.test.ts'],
                         'patched_files': {name: checksum(data) for name, data in self.output.items()},
                         'dependency_files': {name: checksum(self.original[name]) for name in ('package.json', 'yarn.lock')},
                         'dependency_source_files': {name: checksum(data) for name, data in self.dependencies.items()},
                         'patches': []}
        for number, names in enumerate([('src/map.ts', 'src/camera.test.ts'), ('src/images.ts', 'src/images.test.ts')]):
            text = ''
            for name in names:
                old = self.original.get(name, b'').decode()
                text += ''.join(difflib.unified_diff(old.splitlines(keepends=True), self.output[name].decode().splitlines(keepends=True),
                                                   fromfile='a/' + name if name in self.original else '/dev/null', tofile='b/' + name))
            relative = f'demo/client-support/fixture-{number}.patch'
            path = self.layout.sources / relative
            self.write(path, text.encode())
            self.baseline['patches'].append({'file': relative, 'sha256': u.digest(path)})
        self.seal()
        self.state = {'root': str(self.source), 'head': self.baseline['source_git_revision'], 'status': '', 'files': list(self.original)}

    @staticmethod
    def write(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def seal(self):
        path = self.layout.support / u.BASELINE_NAME
        path.write_text(json.dumps(self.baseline))
        return u.digest(path)


class UnitRecordingSupportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = Fixture(Path(self.temp.name).resolve())
        self.pin = mock.patch.object(u, 'BASELINE_SHA256', self.f.seal())
        self.pin.start()
        self.addCleanup(self.pin.stop)
        self.git = mock.patch.object(u, 'git_state', side_effect=lambda source: dict(self.f.state)).start()
        self.addCleanup(mock.patch.stopall)
        self.no_git_process = mock.patch.object(u.subprocess, 'run', side_effect=AssertionError('Tests must never execute Git')).start()

    def prepare(self):
        return u.prepare(self.f.layout)

    def assert_no_destination(self):
        self.assertFalse(self.f.destination.exists())

    def test_plan_needs_no_source_credentials_git_or_writes(self):
        before = sorted(str(p) for p in Path(self.temp.name).rglob('*'))
        with mock.patch.dict(os.environ, {}, clear=True):
            prep = u.preparation_plan(self.f.layout)
            launch = u.launch_plan(self.f.layout)
        self.assertEqual(prep['credential_requirement'], 'none for planning')
        self.assertEqual(launch['port'], 19103)
        self.git.assert_not_called()
        self.no_git_process.assert_not_called()
        self.assertEqual(before, sorted(str(p) for p in Path(self.temp.name).rglob('*')))

    def test_prepare_applies_both_exact_patches_excludes_private_and_preserves_source(self):
        record = self.prepare()
        for name, data in self.f.output.items():
            self.assertEqual((self.f.destination / name).read_bytes(), data)
        for name, data in self.f.original.items():
            self.assertEqual((self.f.source / name).read_bytes(), data)
        self.assertFalse((self.f.destination / '.env.development').exists())
        self.assertFalse((self.f.destination / 'private').exists())
        self.assertFalse((self.f.destination / '.git').exists())
        self.assertTrue((self.f.destination / 'node_modules').is_symlink())
        self.assertEqual(u.verify_prepared(self.f.layout), self.f.destination)
        self.assertFalse(record['environment_values_recorded'])
        self.no_git_process.assert_not_called()

    def test_wrong_head_and_dirty_or_untracked_inputs_refused_before_copy(self):
        for change in [{'head': 'different'}, {'status': ' M src/map.ts'}, {'status': '?? src/unknown.ts'}]:
            with self.subTest(change=change):
                original = dict(self.f.state)
                self.f.state.update(change)
                with self.assertRaises(u.SupportError):
                    self.prepare()
                self.f.state = original
                self.assert_no_destination()

    def test_source_hash_or_lock_or_sdk_tamper_refused(self):
        for name in ['src/map.ts', 'yarn.lock', 'node_modules/sdk/library.js']:
            with self.subTest(name=name):
                path = self.f.source / name
                original = path.read_bytes()
                path.write_bytes(b'changed')
                with self.assertRaises(u.SupportError):
                    self.prepare()
                path.write_bytes(original)
                self.assert_no_destination()

    def test_recording_only_test_already_present_is_refused(self):
        self.f.write(self.f.source / 'src/camera.test.ts', b'unreviewed')
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assert_no_destination()

    def test_baseline_patch_or_helper_identity_tamper_refused(self):
        baseline = self.f.layout.support / u.BASELINE_NAME
        data = baseline.read_bytes()
        baseline.write_bytes(data + b' ')
        with self.assertRaises(u.SupportError):
            self.prepare()
        baseline.write_bytes(data)
        patch = self.f.layout.sources / self.f.baseline['patches'][0]['file']
        patch.write_text(patch.read_text() + '\n')
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assert_no_destination()

    def test_authenticated_patch_path_escape_is_refused(self):
        path = self.f.layout.sources / self.f.baseline['patches'][0]['file']
        path.write_text(path.read_text().replace('b/src/map.ts', 'b/../../outside.ts'))
        self.f.baseline['patches'][0]['sha256'] = u.digest(path)
        with mock.patch.object(u, 'BASELINE_SHA256', self.f.seal()):
            with self.assertRaises(u.SupportError):
                self.prepare()
        self.assert_no_destination()

    def test_exact_hunk_position_required_no_fuzzy_apply(self):
        with self.assertRaises(u.SupportError):
            u.exact_patch('extra\nold\n', ['@@ -1 +1 @@\n', '-old\n', '+new\n'])
        self.assertEqual(u.exact_patch('old\n', ['@@ -1 +1 @@\n', '-old\n', '+new\n']), 'new\n')

    def test_existing_even_empty_destination_preserved(self):
        self.f.destination.mkdir(parents=True)
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assertEqual(list(self.f.destination.iterdir()), [])
        self.f.write(self.f.destination / 'keep.txt', b'keep')
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assertEqual((self.f.destination / 'keep.txt').read_bytes(), b'keep')

    def test_original_overlapping_outside_and_linked_destinations_refused(self):
        for path in [self.f.source, self.f.source / 'Unit-recording-test', Path(self.temp.name) / 'outside', self.f.layout.captures / '../Unit-recording-test']:
            with self.subTest(path=path), self.assertRaises(u.SupportError):
                u.preparation_plan(self.f.layout, path)
        self.f.destination.parent.mkdir(parents=True)
        self.f.destination.symlink_to(self.f.source, target_is_directory=True)
        with self.assertRaises(u.SupportError):
            u.preparation_plan(self.f.layout)

    def test_managed_source_symlink_refused(self):
        moved = self.f.source.with_name('saved-source')
        self.f.source.rename(moved)
        self.f.source.symlink_to(moved, target_is_directory=True)
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assert_no_destination()

    def test_tracked_source_symlink_refused(self):
        path = self.f.source / 'assets/training.txt'
        path.unlink()
        path.symlink_to(self.f.source / 'src/map.ts')
        with self.assertRaises(u.SupportError):
            self.prepare()
        self.assert_no_destination()

    def test_untracked_inputs_cannot_be_supplied_as_pinned_tracked_files(self):
        self.f.state['files'].remove('src/map.ts')
        with self.assertRaises(u.SupportError):
            self.prepare()

    def test_partial_output_hash_mismatch_refused_before_directory_creation(self):
        self.f.baseline['patched_files']['src/map.ts'] = checksum(b'wrong result')
        with mock.patch.object(u, 'BASELINE_SHA256', self.f.seal()), self.assertRaises(u.SupportError):
            self.prepare()
        self.assert_no_destination()

    def test_corrupted_output_and_forged_provenance_do_not_launch(self):
        self.prepare()
        (self.f.destination / 'src/images.ts').write_bytes(b'tampered')
        record_path = self.f.destination / u.PROVENANCE
        record = json.loads(record_path.read_text())
        record['prepared_files']['src/images.ts'] = checksum(b'tampered')
        record_path.write_text(json.dumps(record))
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_extra_private_env_or_empty_directory_refused(self):
        self.prepare()
        for name in ['.env.development', 'private/credentials.json', 'src/unreviewed.ts']:
            with self.subTest(name=name):
                path = self.f.destination / name
                self.f.write(path, b'sample excluded')
                with self.assertRaises(u.SupportError):
                    u.verify_prepared(self.f.layout)
                path.unlink()
                if path.parent.name == 'private':
                    path.parent.rmdir()
        (self.f.destination / 'unknown-empty').mkdir()
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_wrong_dependency_link_or_later_sdk_change_refused(self):
        self.prepare()
        link = self.f.destination / 'node_modules'
        link.unlink()
        other = Path(self.temp.name) / 'other-dependencies'
        other.mkdir()
        link.symlink_to(other, target_is_directory=True)
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)
        link.unlink()
        link.symlink_to(self.f.source / 'node_modules', target_is_directory=True)
        (self.f.source / 'node_modules/sdk/library.js').write_bytes(b'changed SDK')
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_helper_revision_change_requires_fresh_preparation(self):
        self.prepare()
        (self.f.layout.support / 'unit-recording-launch.py').write_bytes(b'changed helper')
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_runtime_cache_allowed_but_cache_symlink_is_not(self):
        self.prepare()
        self.f.write(self.f.destination / '.expo/cache.json', b'{"sample":true}')
        self.assertEqual(u.verify_prepared(self.f.layout), self.f.destination)
        cache = self.f.destination / '.metro-cache'
        cache.symlink_to(self.f.source, target_is_directory=True)
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_launch_requires_inherited_key_without_start_or_value_disclosure(self):
        self.prepare()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(u.subprocess, 'call') as execute:
            with self.assertRaises(u.SupportError) as caught:
                u.launch(self.f.layout)
            self.assertIn('UNIT_MAPBOX_PUBKEY', str(caught.exception))
            execute.assert_not_called()

    def test_launch_inherits_key_only_in_memory_and_preserves_local_no_browser_flags(self):
        self.prepare()
        sample_value = 'pk.training-example-key'
        output = io.StringIO()
        with mock.patch.dict(os.environ, {'UNIT_MAPBOX_PUBKEY': sample_value}, clear=True), mock.patch.object(u.shutil, 'which', return_value='/sample/node'), mock.patch.object(u.subprocess, 'call', return_value=7) as execute, contextlib.redirect_stdout(output):
            self.assertEqual(u.launch(self.f.layout, port=19133, api_origin='http://127.0.0.1:18967'), 7)
        args, kwargs = execute.call_args
        self.assertNotIn(sample_value, str(args))
        self.assertNotIn(sample_value, output.getvalue())
        self.assertEqual(kwargs['env']['UNIT_MAPBOX_PUBKEY'], sample_value)
        self.assertEqual(kwargs['env']['CI'], '1')
        self.assertEqual(kwargs['env']['BROWSER'], 'none')
        self.assertEqual(kwargs['env']['EXPO_NO_DOTENV'], '1')
        self.assertEqual(kwargs['env']['UNIT_BASE_API_URL'], 'http://127.0.0.1:18967')
        self.assertEqual(args[0][-1], '--clear')
        self.assertEqual(kwargs['cwd'], self.f.destination)
        self.assertNotIn(sample_value, (self.f.destination / u.PROVENANCE).read_text())

    def test_only_explicit_loopback_origins_and_safe_ports_accepted(self):
        for origin in ['https://example.test:8443', 'http://' + 'user:sample@' + '127.0.0.1:18967', 'http://127.0.0.1:18967/path', 'http://localhost', 'http://localhost:80', 'http://localhost:18967?value=sample']:
            with self.subTest(origin=origin), self.assertRaises(u.SupportError):
                u.launch_plan(self.f.layout, api_origin=origin)
        for port in [1, 65536, True]:
            with self.subTest(port=port), self.assertRaises(u.SupportError):
                u.launch_plan(self.f.layout, port=port)
        self.assertEqual(u.launch_plan(self.f.layout, api_origin='http://[::1]:18967')['api_origin'], 'http://[::1]:18967')


    def test_copy_interruption_never_creates_accepted_provenance(self):
        original_read = Path.read_bytes
        source_asset = self.f.source / 'assets/training.txt'
        attempts = 0
        def changing_read(path):
            nonlocal attempts
            if path == source_asset:
                attempts += 1
                if attempts == 2:
                    return b'sample changed during copy'
            return original_read(path)
        with mock.patch.object(Path, 'read_bytes', changing_read), self.assertRaises(u.SupportError):
            self.prepare()
        self.assertFalse((self.f.destination / u.PROVENANCE).exists())
        self.assertEqual(source_asset.read_bytes(), self.f.original['assets/training.txt'])
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)

    def test_runtime_directory_must_not_hide_an_environment_directory(self):
        self.prepare()
        (self.f.destination / 'private').mkdir()
        with self.assertRaises(u.SupportError):
            u.verify_prepared(self.f.layout)


class ReviewedSupportBundleTest(unittest.TestCase):
    def test_actual_bundle_checksums_are_valid_without_git_or_credentials(self):
        with mock.patch.object(u, 'git_state', side_effect=AssertionError('No Git in bundle test')), mock.patch.dict(os.environ, {}, clear=True):
            baseline, patches, identity = u.load_bundle(u.Layout(SUPPORT))
        self.assertEqual(len(patches), 2)
        self.assertEqual(len(baseline['patched_files']), 4)
        self.assertEqual(len(baseline['dependency_source_files']), 10)
        self.assertEqual(identity[u.BASELINE_NAME], u.BASELINE_SHA256)


    def test_retained_real_patches_produce_all_four_reviewed_outputs_without_a_live_checkout(self):
        baseline, patches, _ = u.load_bundle(u.Layout(SUPPORT))
        with tempfile.TemporaryDirectory() as temporary:
            layout = u.Layout(Path(temporary).resolve() / 'sources/demo/client-support')
            inputs = {
                'src/components/maps/map-view.web.tsx': SUPPORT / 'unit-camera/baseline/map-view.web.tsx',
                'src/components/calls/call-images-modal.tsx': SUPPORT / 'unit-images/baseline/call-images-modal.tsx',
                'src/components/calls/__tests__/call-images-modal.test.tsx': SUPPORT / 'unit-images/baseline/call-images-modal.test.tsx',
            }
            for name, retained in inputs.items():
                self.assertEqual(u.digest(retained), baseline['source_files'][name])
                Fixture.write(layout.source / name, retained.read_bytes())
            outputs = u.patch_outputs(layout, baseline, patches)
            self.assertEqual(set(outputs), set(baseline['patched_files']))
            for name, data in outputs.items():
                self.assertEqual(checksum(data), baseline['patched_files'][name])
            for name, retained in inputs.items():
                self.assertEqual((layout.source / name).read_bytes(), retained.read_bytes())

    def test_cli_parser_rejects_invalid_options_without_echoing_values(self):
        for filename in ('unit-recording-prepare.py', 'unit-recording-launch.py'):
            spec = importlib.util.spec_from_file_location('fixture_cli', SUPPORT / filename)
            entry = importlib.util.module_from_spec(spec)
            with mock.patch.dict('sys.modules', {'unit_recording_support': u}):
                spec.loader.exec_module(entry)
            parser = entry.QuietParser()
            parser.add_argument('--port', type=int)
            output = io.StringIO()
            sample_value = 'pk.training-example-key'
            with contextlib.redirect_stderr(output), self.assertRaises(SystemExit):
                parser.parse_args(['--port', sample_value])
            self.assertNotIn(sample_value, output.getvalue())


if __name__ == '__main__':
    unittest.main()
