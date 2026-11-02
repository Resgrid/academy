"""Simulated telemetry must never write from help, a plan or invalid arguments."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('academy_training_positions', ROOT / 'sources/demo/scenarios/refresh_training_positions.py')
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)


class TrainingPositionsTests(unittest.TestCase):
    def test_default_and_plan_are_offline_and_write_no_report(self):
        for argv in ([], ['--plan']):
            with self.subTest(argv=argv), tempfile.TemporaryDirectory() as directory, patch.object(scenario, 'ROOT', Path(directory)), patch.object(scenario, 'execute_query', side_effect=AssertionError('unexpected database contact')):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(scenario.main(argv), 0)
                report = json.loads(output.getvalue())
                self.assertEqual(report['state_changes'], 'none')
                self.assertFalse(report['database_contacted'])
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_help_and_invalid_or_conflicting_options_never_contact_database(self):
        for argv, code in ((['--help'], 0), (['--unknown'], 2), (['--plan', '--write-training-fixes'], 2)):
            with self.subTest(argv=argv), patch.object(scenario, 'execute_query', side_effect=AssertionError('unexpected database contact')), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    scenario.main(argv)
                self.assertEqual(raised.exception.code, code)

    def test_only_explicit_write_sends_guarded_query_and_retains_actual_result(self):
        result = {'scenario': 'fresh fictional officer locations', 'fixes': [{'member': 'CASEY', 'status_type_preserved': 0}]}
        with tempfile.TemporaryDirectory() as directory, patch.object(scenario, 'ROOT', Path(directory)), patch.object(scenario, 'execute_query', return_value='BEGIN\n' + json.dumps(result) + '\nCOMMIT') as query, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(scenario.main(['--write-training-fixes']), 0)
            query.assert_called_once_with(scenario.QUERY)
            self.assertEqual(json.loads((Path(directory) / 'scenario-reports/fresh-training-positions.json').read_text()), result)

    def test_query_preserves_append_only_state_and_rejects_missing_or_null_fixture_state(self):
        self.assertIn("current_database() <> 'resgrid_academy'", scenario.QUERY)
        self.assertIn('pg_advisory_xact_lock', scenario.QUERY)
        self.assertIn('count(DISTINCT u.id)', scenario.QUERY)
        self.assertIn('Each seeded officer must already have a training status', scenario.QUERY)
        self.assertIn("geolocationdata IS DISTINCT FROM '41.8721,-87.6523'", scenario.QUERY)
        self.assertIn('a.note IS NULL', scenario.QUERY)
        self.assertIn('u.id,51,a.actiontypeid', scenario.QUERY)
        self.assertIn("interval '2 minutes'", scenario.QUERY)
        self.assertEqual(scenario.QUERY.count('INSERT INTO'), 1)
        self.assertNotRegex(scenario.QUERY, r'(?i)\b(?:UPDATE|DELETE|TRUNCATE)\b')


if __name__ == '__main__':
    unittest.main()
