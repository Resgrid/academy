import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import setup_demo
from settings import profile


class RecordingStackTests(unittest.TestCase):
    def test_reserved_original_stack_and_invalid_ports_are_rejected(self):
        for name, port in [('resgrid-academy', 18867), ('production', 18867), ('resgrid-academy-capture', 65535)]:
            with self.assertRaises(ValueError):
                profile(name, port)
        selected = profile('resgrid-academy-test', 18967)
        self.assertEqual(selected['ports']['api'], 18968)
        self.assertEqual(len(set(selected['ports'].values())), 5)

    def test_existing_storage_without_credentials_stops_before_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(setup_demo, 'DEMO', Path(directory)), patch.object(setup_demo.subprocess, 'run', return_value=SimpleNamespace(returncode=0)):
                with self.assertRaisesRegex(ValueError, 'credentials are missing'):
                    setup_demo.require_fresh_credentials_for_existing_storage('docker', profile())

    def test_existing_department_is_preserved_and_foreign_department_rejected(self):
        for name, expected in [('', True), ('Firehouse 51 — Training Department', False)]:
            self.assertEqual(setup_demo.department_seed_needed(SimpleNamespace(sql=lambda query: name)), expected)
        with self.assertRaises(ValueError):
            setup_demo.department_seed_needed(SimpleNamespace(sql=lambda query: 'Existing Department'))

    def test_fresh_credentials_and_full_fixture_seed_generate_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            demo = Path(directory)
            for name in ('prepare.py', 'settings.py', 'seed.py', 'fixtures.json', 'schema.json', 'feature-flags.json', 'loopback.conf'):
                shutil.copy2(ROOT / 'sources/demo' / name, demo / name)
            subprocess.run([sys.executable, str(demo / 'prepare.py')], check=True, capture_output=True)
            subprocess.run([sys.executable, str(demo / 'seed.py')], check=True, capture_output=True)
            seed = (demo / 'private/seed.sql').read_text()
            guard = seed[:seed.index('INSERT INTO')]
            self.assertIn('current_database()', guard)
            self.assertIn('WHERE departmentid=51)', guard)
            self.assertIn('refuses to overwrite department data', guard)
            self.assertTrue(seed.endswith('COMMIT;\n'))
            counts = json.loads((demo / 'seed-manifest.json').read_text())['counts']
            self.assertEqual(counts['departmentmembers'], 14)
            self.assertEqual(counts['units'], 6)
            self.assertEqual(counts['calls'], 4)
            self.assertGreater(len(counts), 45)
            self.assertEqual((demo / 'private/credentials.json').stat().st_mode & 0o777, 0o600)
            self.assertEqual((demo / '.env').stat().st_mode & 0o777, 0o600)
            config = json.loads((demo / 'private/ResgridConfig.json').read_text())
            self.assertEqual(config['SystemBehaviorConfig.ResgridBaseUrl'], 'http://127.0.0.1:18867')
            self.assertEqual(config['SystemBehaviorConfig.DoNotBroadcast'], 'true')
            self.assertIn('listen 127.0.0.1:18867;', (demo / 'private/loopback.conf').read_text())


if __name__ == '__main__':
    unittest.main()
