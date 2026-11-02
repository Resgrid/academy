"""Guarded configuration replay planning; local secret fixtures stay temporary."""
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('academy_core_configuration', ROOT / 'sources/demo/scenarios/core_configuration.py')
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)


class ConfigurationReplayTests(unittest.TestCase):
    def setUp(self):
        self.fixture = scenario.load_fixture()
        guard = self.fixture['guard']
        self.identity = {'database': guard['database'], 'department_id': guard['department_id'],
                         'department_name': guard['department_name'],
                         'unit_names': guard['required_units'], 'catalogs_match': True}

    def test_public_bundle_retains_exact_graph_and_disabled_ordered_workflows(self):
        card = self.fixture['run_cards'][0]
        nodes = card['alarm_levels'][0]['decision_nodes']
        keys = {node['key'] for node in nodes}
        condition = next(node for node in nodes if node['root'])
        self.assertEqual(condition['threshold_seconds'], 480)
        self.assertTrue({condition['yes'], condition['no']} <= keys)
        self.assertEqual(card['availability_selections'], [])
        self.assertEqual(card['auto_dispatch_override'], 'PrepopulateOnly')
        self.assertEqual([flow['trigger'] for flow in self.fixture['workflows']], ['CallAdded', 'CallClosed'])
        self.assertTrue(all(flow['enabled'] is False for flow in self.fixture['workflows']))
        self.assertEqual([step['order'] for step in self.fixture['workflows'][0]['steps']], [1, 2])
        self.assertEqual(self.fixture['workflows'][1]['retry_backoff_base_seconds'], 30)
        tuning = self.fixture['dispatch_settings']['closest_unit_tuning']
        self.assertEqual([tuning[name] for name in ('in_quarters_turnout_seconds', 'mobile_turnout_seconds', 'personnel_turnout_seconds')], [120, 0, 0])
        staffing = self.fixture['unit_staffing']
        self.assertEqual(len(staffing['configured_seats']), 1)
        self.assertFalse(staffing['configured_seats'][0]['personnel_role_required'])
        self.assertIsNone(staffing['configured_seats'][0]['required_personnel_role'])
        self.assertEqual(staffing['assignments'][0]['member_username'], 'herrmann')

    def test_offline_plan_never_probes_docker_or_generates_local_values(self):
        with patch.object(scenario, 'read_identity', side_effect=AssertionError('unexpected database probe')), patch.object(scenario.secrets, 'token_urlsafe', side_effect=AssertionError('unexpected credential generation')), patch.object(sys, 'argv', ['core_configuration.py', '--plan']):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(scenario.main(), 0)
        self.assertEqual(json.loads(output.getvalue())['state_changes'], 'none')

    def test_foreign_or_unseeded_database_is_rejected_before_local_write(self):
        for change in ({'database': 'production'}, {'department_id': 52}, {'department_name': 'Another department'}, {'unit_names': []}, {'catalogs_match': False}):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                identity = dict(self.identity, **change)
                with self.assertRaises(ValueError):
                    scenario.write_local_settings(self.fixture, identity, directory)
                self.assertFalse(list(Path(directory).iterdir()))

    def test_runtime_value_is_private_fresh_and_reused_without_echo(self):
        with tempfile.TemporaryDirectory() as directory:
            result = scenario.write_local_settings(self.fixture, self.identity, directory)
            path = Path(result['file'])
            data = json.loads(path.read_text())
            value = data['fields']['SmtpPassword']
            self.assertGreaterEqual(len(value), 32)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            self.assertNotIn(value, json.dumps(result))
            self.assertNotIn(value, json.dumps(self.fixture))
            before = path.read_bytes()
            self.assertEqual(scenario.write_local_settings(self.fixture, self.identity, directory)['status'], 'reused')
            self.assertEqual(path.read_bytes(), before)
            data['fields']['SmtpHost'] = 'different.invalid'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'differ'):
                scenario.write_local_settings(self.fixture, self.identity, directory)
            self.assertEqual(json.loads(path.read_text())['fields']['SmtpHost'], 'different.invalid')

    def test_symlinked_private_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / 'outside'
            outside.mkdir()
            (root / 'private').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                scenario.write_local_settings(self.fixture, self.identity, root)
            self.assertFalse(list(outside.iterdir()))

    def test_public_bundle_cannot_add_stored_secret_fields_or_enable_automation(self):
        for change in ('secret', 'workflow', 'automatic-dispatch', 'external-smtp'):
            data = copy.deepcopy(self.fixture)
            if change == 'secret':
                data['credential']['fields']['SmtpPassword'] = 'synthetic-example-forbidden'
            elif change == 'workflow':
                data['workflows'][0]['enabled'] = True
            elif change == 'automatic-dispatch':
                data['dispatch_settings']['automatically_dispatch_recommended_resources'] = True
            else:
                data['credential']['fields']['SmtpHost'] = 'external.invalid'
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'fixture.json'
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    scenario.load_fixture(path)


if __name__ == '__main__':
    unittest.main()
