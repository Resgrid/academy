"""Offline source-profile and isolation checks; never starts Docker or client apps."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'sources/demo'))
import launch_app
import prepare_apps
import setup_demo
import source_profiles as profiles


class SourceProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expansion = profiles.load_source_set('expansion', ROOT)

    def test_legacy_keeps_original_manifest_and_default_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            name, pin = profiles.select_profile(directory)
            self.assertEqual((name, pin), ('legacy', None))
            with patch.object(setup_demo, 'DEMO', Path(directory)):
                args = SimpleNamespace(source_profile=None, core=None, name=None, web_port=None)
                plan = setup_demo.plan(args)
            self.assertEqual(plan['stack']['ports']['web'], 18867)
            self.assertEqual(plan['source_set']['manifest_sha256'], profiles.digest(ROOT / 'sources/evidence/source-manifest.json'))
            self.assertFalse(list(Path(directory).iterdir()))

    def test_expansion_verifies_all_retained_files_and_pinned_support(self):
        source_set = self.expansion
        self.assertEqual(set(source_set['repositories']), {'Core', 'Dispatch', 'Responder', 'Unit', 'IC'})
        self.assertEqual(sum(len(files) for files in source_set['snapshots'].values()), 453)
        self.assertEqual(source_set['repositories']['Core']['head'], source_set['core_patch']['baseline_head'])
        for app in profiles.APPS:
            self.assertEqual(source_set['dependencies'][app]['package_manager'], 'yarn@1.22.22')

    def test_changed_support_file_is_rejected_before_setup(self):
        original_digest = profiles.digest
        def altered(path):
            return '0' * 64 if str(path).endswith('responder-web-compat.patch') else original_digest(path)
        with patch.object(profiles, 'digest', side_effect=altered):
            with self.assertRaisesRegex(ValueError, 'Recording support hash changed'):
                profiles.load_source_set('expansion', ROOT)

    def test_changed_evidence_snapshot_is_rejected(self):
        original_digest = profiles.digest
        def altered(path):
            return '0' * 64 if str(path).endswith('/Core/Resgrid.Model/CallNumbering.cs') else original_digest(path)
        with patch.object(profiles, 'digest', side_effect=altered):
            with self.assertRaisesRegex(ValueError, 'snapshot hash mismatch'):
                profiles.load_source_set('expansion', ROOT)

    def test_saved_selection_and_profile_definition_cannot_silently_change(self):
        with tempfile.TemporaryDirectory() as directory:
            profiles.save_pin(directory, self.expansion)
            name, pin = profiles.select_profile(directory)
            self.assertEqual(name, 'expansion')
            self.assertEqual((Path(directory) / 'private/source-profile.json').stat().st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ValueError, 'another source profile'):
                profiles.select_profile(directory, 'legacy')
            changed = dict(self.expansion, definition_sha256='0' * 64)
            with self.assertRaisesRegex(ValueError, 'definition differs'):
                profiles.verify_pin(pin, changed)

    def test_expansion_plan_is_offline_preserves_existing_stack_and_hides_environment_values(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = Path(directory)
            (demo / 'private').mkdir()
            stack = {'name': 'resgrid-academy-existing', 'ports': {'web': 19067, 'api': 19068, 'eventing': 19069, 'mail': 18226, 'rabbit': 15874}}
            (demo / 'private/stack.json').write_text(json.dumps(stack))
            before = {str(p): p.read_bytes() for p in demo.rglob('*') if p.is_file()}
            args = SimpleNamespace(source_profile='expansion', core=None, name=None, web_port=None)
            with patch.object(setup_demo, 'DEMO', demo), patch.object(subprocess, 'run', side_effect=AssertionError('plan executed a process')):
                plan = setup_demo.plan(args)
            self.assertEqual(plan['stack'], stack)
            self.assertEqual(plan['source_set']['source_profile'], 'expansion')
            self.assertEqual(before, {str(p): p.read_bytes() for p in demo.rglob('*') if p.is_file()})
            with patch.object(launch_app, 'DEMO', demo), patch.dict(launch_app.os.environ, {'IC_MAPBOX_PUBKEY': 'pk.NEVER_PRINT_THIS_VALUE'}):
                plan = launch_app.plan(SimpleNamespace(app='IC', source_profile='expansion', source=None, port=None, web_port=None))
            self.assertEqual(plan['api_origin'], 'http://127.0.0.1:19067')
            self.assertNotIn('NEVER_PRINT_THIS_VALUE', json.dumps(plan))

    def core_fixture(self, root):
        file = root / 'controller.cs'
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text('baseline')
        metadata = {'path': 'controller.cs', 'baseline_sha256': profiles.digest(file), 'modified_sha256': '0' * 64}
        return dict(self.expansion, core_patch={'files': [metadata], 'patch_sha256': '1' * 64}, snapshots={'Core': {}})

    def test_core_patch_refuses_original_or_other_nonmanaged_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = Path(directory)
            source = demo / 'someone-elses-source'
            source_set = self.core_fixture(source)
            with patch.object(profiles, 'verify_repository'), patch.object(subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'managed isolated'):
                    profiles.prepare_core(source, demo, source_set)
                run.assert_not_called()
            self.assertEqual((source / 'controller.cs').read_text(), 'baseline')

    def test_build_never_automatically_applies_a_missing_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = Path(directory)
            source = profiles.managed_source(demo, 'Core')
            source_set = self.core_fixture(source)
            with patch.object(profiles, 'verify_repository'), patch.object(subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'has not been applied'):
                    profiles.prepare_core(source, demo, source_set, allow_apply=False)
                run.assert_not_called()

    def test_unknown_core_edit_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = Path(directory)
            source = profiles.managed_source(demo, 'Core')
            source_set = self.core_fixture(source)
            (source / 'controller.cs').write_text('local work')
            with patch.object(profiles, 'verify_repository'), patch.object(subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'mixed or unknown'):
                    profiles.prepare_core(source, demo, source_set)
                run.assert_not_called()
            self.assertEqual((source / 'controller.cs').read_text(), 'local work')

    def test_existing_non_git_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'keep.txt').write_text('keep')
            with patch.object(subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'nonempty'):
                    profiles.acquire(root, 'Responder', self.expansion)
                run.assert_not_called()
            self.assertEqual((root / 'keep.txt').read_text(), 'keep')

    def test_missing_client_copy_reports_missing_directory_before_source_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(profiles, 'verify_repository') as verify:
                with self.assertRaisesRegex(ValueError, 'launch directory does not exist'):
                    profiles.verify_client(Path(directory), Path(directory) / 'missing', 'IC', self.expansion)
                verify.assert_not_called()

    def test_client_dependency_source_pins_are_checked_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            destination = Path(directory) / 'capture'
            dependency = source / 'node_modules/sdk/source.ts'
            dependency.parent.mkdir(parents=True)
            dependency.write_text('actual SDK implementation')
            destination.mkdir()
            (destination / 'node_modules').symlink_to(source / 'node_modules', target_is_directory=True)
            baseline = {'source_git_revision': self.expansion['repositories']['Responder']['head'],
                        'source_files': {}, 'patched_files': {},
                        'dependency_source_files': {'sdk/source.ts': profiles.digest(dependency)}}
            source_set = dict(self.expansion, snapshots={}, dependencies={'Responder': {'files': {}}})
            with patch.object(profiles, 'verify_repository'), patch.object(profiles, 'client_baseline', return_value=baseline):
                profiles.verify_client(source, destination, 'Responder', source_set)
                dependency.write_text('changed SDK implementation')
                with self.assertRaisesRegex(ValueError, 'source hash mismatch'):
                    profiles.verify_client(source, destination, 'Responder', source_set)

    def test_dependency_install_is_limited_to_managed_clones(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(prepare_apps, 'DEMO', Path(directory)), patch.object(subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'managed isolated'):
                    prepare_apps.install_dependencies(Path(directory) / 'original', 'IC', self.expansion)
                run.assert_not_called()

    def test_all_app_plan_uses_isolated_destinations_and_requires_single_source_override(self):
        args = SimpleNamespace(source_profile='expansion', app='all', source=None, destination=None, install_deps=False)
        with tempfile.TemporaryDirectory() as directory, patch.object(prepare_apps, 'DEMO', Path(directory)):
            plan = prepare_apps.plan(args)
            self.assertEqual(len(plan['apps']), 4)
            self.assertTrue(all(directory in entry['launch_directory'] for entry in plan['apps']))
            args.source = Path(directory) / 'some-source'
            with self.assertRaisesRegex(ValueError, 'single --app'):
                prepare_apps.plan(args)

    def test_manager_plan_does_not_require_docker(self):
        with patch('shutil.which', return_value=None):
            spec = importlib.util.spec_from_file_location('academy_demo_manager_test', ROOT / 'sources/demo/manage.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        output = io.StringIO()
        with patch.object(sys, 'argv', ['manage.py', 'plan', '--source-profile', 'expansion']), contextlib.redirect_stdout(output):
            module.main()
        self.assertEqual(json.loads(output.getvalue())['source_set']['source_profile'], 'expansion')


if __name__ == '__main__':
    unittest.main()
