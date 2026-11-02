"""Temporary source fixtures only; no apps, credentials, installs or Git commits."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('records_prepare', Path(__file__).resolve().parents[1] / 'prepare.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class PrepareGuards(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package, self.target, self.original, self.core = [self.root / n for n in ['package', 'capture-apps/Unit-records', 'original', 'core']]
        for p in [self.package, self.target, self.original, self.core]:
            p.mkdir(parents=True)
        (self.original / 'node_modules').mkdir()
        (self.target / 'node_modules').symlink_to(self.original / 'node_modules')
        self.put(self.package / 'base.json', b'{}')
        self.put(self.package / 'patch.diff', b'fixture unified patch')
        self.put(self.package / 'core.json', b'fixture source excerpt')
        for root in [self.original, self.target]:
            self.put(root / 'src/record.ts', b'before')
            self.put(root / 'src/gate.ts', b'unchanged gate')
        self.put(self.target / 'metro.config.js', b'old compatibility')
        self.put(self.original / 'metro.config.js', b'old compatibility')
        self.put(self.core / 'contract.cs', b'unchanged contract')
        self.put(self.package / 'before/src/record.ts', b'before')
        self.put(self.package / 'after/src/record.ts', b'after')
        self.put(self.package / 'after/src/__tests__/record.test.ts', b'new test')
        self.metadata = {
            'patch': {'file': 'patch.diff', 'sha256': M.digest(b'fixture unified patch')},
            'contract_excerpts': {'file': 'core.json', 'sha256': M.digest(b'fixture source excerpt')},
            'base_compatibility_metadata': {'file': 'base.json', 'sha256': M.digest(b'{}')},
            'original_files': [{'file': 'src/record.ts', 'sha256': M.digest(b'before')}, {'file': 'src/gate.ts', 'sha256': M.digest(b'unchanged gate')}, {'file': 'metro.config.js', 'sha256': M.digest(b'old compatibility')}],
            'core_contract_files': [{'file': 'contract.cs', 'sha256': M.digest(b'unchanged contract')}],
            'base_compatibility_files': [{'file': 'metro.config.js', 'sha256': M.digest(b'old compatibility')}],
            'unchanged_target_gate_files': [{'file': 'src/gate.ts', 'sha256': M.digest(b'unchanged gate')}],
            'files': [
                {'file': 'src/record.ts', 'before_sha256': M.digest(b'before'), 'after_sha256': M.digest(b'after'), 'before_snapshot': 'before/src/record.ts', 'after_snapshot': 'after/src/record.ts', 'new_regression_test': False},
                {'file': 'src/__tests__/record.test.ts', 'before_sha256': None, 'after_sha256': M.digest(b'new test'), 'before_snapshot': None, 'after_snapshot': 'after/src/__tests__/record.test.ts', 'new_regression_test': True},
            ],
        }
        body = (json.dumps(self.metadata) + '\n').encode()
        self.put(self.package / 'contract-metadata.json', body)
        self.pin = patch.object(M, 'METADATA_SHA256', M.digest(body))
        self.pin.start()
        self.addCleanup(self.pin.stop)

    def put(self, path, body):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)

    def inspect(self):
        return M.inspect(self.target, self.original, self.core, self.package)

    def test_read_only_default_checks_without_writes(self):
        self.assertEqual(self.inspect()['state'], 'before')
        self.assertEqual((self.target / 'src/record.ts').read_bytes(), b'before')
        self.assertFalse((self.target / 'src/__tests__').exists())

    def test_complete_apply_preserves_original_gates_and_is_idempotent(self):
        self.assertEqual(M.apply(self.inspect()), 2)
        self.assertEqual(self.inspect()['state'], 'after')
        self.assertEqual((self.original / 'src/record.ts').read_bytes(), b'before')
        self.assertEqual((self.target / 'src/gate.ts').read_bytes(), b'unchanged gate')
        self.assertEqual(M.apply(self.inspect()), 0)

    def test_final_guard_failure_prevents_every_target_write(self):
        self.put(self.core / 'contract.cs', b'unknown contract')
        with self.assertRaisesRegex(ValueError, 'Core contract changed'):
            self.inspect()
        self.assertEqual((self.target / 'src/record.ts').read_bytes(), b'before')
        self.assertFalse((self.target / 'src/__tests__').exists())

    def test_unknown_target_edit_is_not_overwritten(self):
        self.put(self.target / 'src/record.ts', b'human edit')
        with self.assertRaisesRegex(ValueError, 'Unknown target edit'):
            self.inspect()
        self.assertEqual((self.target / 'src/record.ts').read_bytes(), b'human edit')

    def test_original_checkout_cannot_be_the_target(self):
        with self.assertRaisesRegex(ValueError, 'Original checkout'):
            M.inspect(self.original, self.original, self.core, self.package)

    def test_unknown_new_test_and_changed_snapshots_are_rejected(self):
        self.put(self.target / 'src/__tests__/record.test.ts', b'human test')
        with self.assertRaisesRegex(ValueError, 'Unknown existing test'):
            self.inspect()
        (self.target / 'src/__tests__/record.test.ts').unlink()
        self.put(self.package / 'after/src/record.ts', b'unreviewed')
        with self.assertRaisesRegex(ValueError, 'After snapshot changed'):
            self.inspect()

    def test_expected_pre_staged_tests_are_preserved(self):
        self.put(self.target / 'src/__tests__/record.test.ts', b'new test')
        self.assertEqual(M.apply(self.inspect()), 1)
        self.assertEqual((self.target / 'src/__tests__/record.test.ts').read_bytes(), b'new test')

    def test_changed_auth_gate_compatibility_and_metadata_fail_closed(self):
        for path, body, expected in [(self.target / 'src/gate.ts', b'changed', 'compatibility/gate'), (self.target / 'metro.config.js', b'changed', 'compatibility/gate'), (self.package / 'contract-metadata.json', b'{}', 'metadata changed')]:
            original = path.read_bytes()
            self.put(path, body)
            with self.assertRaisesRegex(ValueError, expected):
                self.inspect()
            self.put(path, original)

    def test_symlinked_target_file_is_rejected(self):
        p = self.target / 'src/record.ts'
        p.unlink()
        p.symlink_to(self.original / 'src/record.ts')
        with self.assertRaisesRegex(ValueError, 'Symlinked file'):
            self.inspect()

    def test_partial_production_patch_is_not_completed_silently(self):
        for root in [self.original, self.target]:
            self.put(root / 'src/other.ts', b'other before')
        self.put(self.package / 'before/src/other.ts', b'other before')
        self.put(self.package / 'after/src/other.ts', b'other after')
        self.metadata['original_files'].append({'file': 'src/other.ts', 'sha256': M.digest(b'other before')})
        self.metadata['files'].append({'file': 'src/other.ts', 'before_sha256': M.digest(b'other before'), 'after_sha256': M.digest(b'other after'), 'before_snapshot': 'before/src/other.ts', 'after_snapshot': 'after/src/other.ts', 'new_regression_test': False})
        body = json.dumps(self.metadata).encode()
        self.put(self.package / 'contract-metadata.json', body)
        self.put(self.target / 'src/record.ts', b'after')
        with patch.object(M, 'METADATA_SHA256', M.digest(body)):
            with self.assertRaisesRegex(ValueError, 'Partially patched'):
                self.inspect()
        self.assertEqual((self.target / 'src/other.ts').read_bytes(), b'other before')
        self.assertFalse((self.target / 'src/__tests__').exists())

    def test_write_failure_restores_only_the_known_changed_file(self):
        checked = self.inspect()
        original_write = M.atomic_write

        def fail_new_test(path, data, mode=0o644):
            if path.name == 'record.test.ts':
                raise OSError('synthetic write failure')
            original_write(path, data, mode)

        with patch.object(M, 'atomic_write', fail_new_test):
            with self.assertRaisesRegex(OSError, 'synthetic write failure'):
                M.apply(checked)
        self.assertEqual((self.target / 'src/record.ts').read_bytes(), b'before')
        self.assertEqual((self.original / 'src/record.ts').read_bytes(), b'before')
        self.assertFalse((self.target / 'src/__tests__/record.test.ts').exists())


    def copy_module(self):
        spec = importlib.util.spec_from_file_location('unit_records_copy_guards', Path(__file__).resolve().parents[1] / 'create_copy.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_new_copy_keeps_original_and_unlisted_environment_outside_target(self):
        module = self.copy_module()
        destination = self.root / 'capture-apps/Unit-records-replay'
        self.put(self.original / '.env.synthetic', b'synthetic excluded fixture')
        with patch.object(module.M, 'METADATA_SHA256', M.METADATA_SHA256):
            result = module.create(destination, self.original, self.core, self.package)
        self.assertEqual(result['production_state'], 'before')
        self.assertFalse((destination / '.env.synthetic').exists())
        self.assertEqual((destination / 'src/record.ts').read_bytes(), b'before')
        self.assertTrue((destination / 'node_modules').is_symlink())

    def test_copy_contract_failure_prevents_destination_creation(self):
        module = self.copy_module()
        destination = self.root / 'capture-apps/Unit-records-replay'
        self.put(self.core / 'contract.cs', b'changed contract')
        with patch.object(module.M, 'METADATA_SHA256', M.METADATA_SHA256):
            with self.assertRaisesRegex(ValueError, 'Core contract changed'):
                module.create(destination, self.original, self.core, self.package)
        self.assertFalse(destination.exists())

    def test_native_tree_is_never_a_copy_or_patch_target(self):
        module = self.copy_module()
        destination = self.root / 'native-unit-history/source/capture-apps/Unit-records'
        with self.assertRaisesRegex(ValueError, 'Historical native'):
            module.create(destination, self.original, self.core, self.package)
        destination.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'Historical native'):
            M.inspect(destination, self.original, self.core, self.package)
        self.assertEqual(list(destination.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
