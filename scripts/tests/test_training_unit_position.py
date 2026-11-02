"""Offline safety/refusal tests; these tests never connect to SQL or Docker."""
import base64
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('academy_training_unit_position', ROOT / 'sources/demo/scenarios/refresh_training_unit_position.py')
scenario = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scenario)
NOTE = 'TRAINING ONLY - Reserve Engine 51 marker demonstration; simulated Available, no destination or GPS.'


def success(appended=True, state='Available'):
    return {
        'scenario': 'fictional reserve apparatus station status location',
        'unit_id': 51006, 'department_id': 51, 'expected_state': scenario.STATES[state],
        'previous_status_id': 90001, 'status_id': 90002 if appended else 90001,
        'appended': appended, **scenario.POSITION,
        'status_fields_preserved': True, 'note_preserved': True,
        'prior_history_preserved': True, 'events_emitted': False,
        'live_location_written': False, 'source': scenario.SOURCE,
    }


class TrainingUnitPositionTests(unittest.TestCase):
    def test_offline_default_plan_and_help_neither_import_manage_nor_write(self):
        for argv in ([], ['--plan'], ['--plan', '--expected-state', 'Available', '--expected-note', NOTE], ['--help']):
            with self.subTest(argv=argv), tempfile.TemporaryDirectory() as directory, patch.object(scenario, 'ROOT', Path(directory)), patch.object(scenario, 'execute_query', side_effect=AssertionError('unexpected database contact')), patch.dict(sys.modules, {'manage': None}), contextlib.redirect_stdout(io.StringIO()) as output:
                if argv == ['--help']:
                    with self.assertRaises(SystemExit) as raised:
                        scenario.main(argv)
                    self.assertEqual(raised.exception.code, 0)
                else:
                    self.assertEqual(scenario.main(argv), 0)
                    report = json.loads(output.getvalue())
                    self.assertFalse(report['database_contacted'])
                    self.assertEqual(report['state_changes'], 'none')
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_invalid_or_incomplete_write_arguments_refuse_before_contact(self):
        cases = [
            ['--write-training-fix'],
            ['--write-training-fix', '--expected-state', 'Available'],
            ['--write-training-fix', '--expected-note', NOTE],
            ['--write-training-fix', '--plan'],
            ['--write-training-fix', '--expected-state', 'Responding', '--expected-note', NOTE],
            ['--write-training-fix', '--expected-state', '0', '--expected-note', NOTE],
            ['--unknown'],
        ]
        for invalid in ('', 'operational note', 'TRAINING ONLY - Engine 51 wrong apparatus', NOTE + '\nsecond line', NOTE + '\x00', NOTE + '\u2028second line', NOTE + 'x' * 500):
            cases.append(['--write-training-fix', '--expected-state', 'Available', '--expected-note', invalid])
        for argv in cases:
            with self.subTest(argv=argv), patch.object(scenario, 'execute_query', side_effect=AssertionError('unexpected database contact')), patch.dict(sys.modules, {'manage': None}), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    scenario.main(argv)
                self.assertEqual(raised.exception.code, 2)

    def test_exact_note_is_encoded_and_cannot_escape_sql_or_dollar_quotes(self):
        note = "TRAINING ONLY - Reserve Engine 51 note '); DROP TABLE units; -- $academy_unit_fixture$ $$"
        query = scenario.build_query('Available', note)
        self.assertNotIn(note, query)
        encoded = base64.b64encode(note.encode()).decode()
        self.assertIn("decode('" + encoded + "','base64')", query)
        self.assertEqual(base64.b64decode(encoded).decode(), note)
        self.assertEqual(query.count('$academy_unit_fixture$'), 2)
        self.assertNotIn('__EXPECTED_', query)
        with self.assertRaises(ValueError):
            scenario.build_query('Responding', NOTE)

    def test_transaction_binds_exact_target_and_preserves_other_fields_and_history(self):
        query = scenario.build_query('OutOfService', NOTE)
        for guard in (
            "current_database() <> 'resgrid_academy'", "name='Firehouse 51 — Training Department' AND code='FH51'",
            'departmentgroupid=51001', "name='Firehouse 51' AND type=2", "latitude::text='41.8721' AND longitude::text='-87.6523'",
            'unitid=51006 AND departmentid=51', "name='Reserve Engine 51' AND type='Engine' AND stationgroupid=51001",
            "vin='DEMO-APPARATUS-6' AND platenumber='TRAINING'", 'previous.state IS DISTINCT FROM expected_state',
            'previous.note::text IS DISTINCT FROM expected_note', 'expected_state integer := 4',
            "p.key LIKE 'protected%'", 'WHERE unitstateid=previous.unitstateid',
            'previous.latitude <> 41.8721', 'previous.longitude <> -87.6523',
            "previous.geolocationdata::text NOT IN ('','41.8721,-87.6523')", 'previous.timestamp > fresh_timestamp',
            'SHARE ROW EXCLUSIVE MODE', 'pg_advisory_xact_lock', "SET LOCAL lock_timeout = '5s'",
            "NOT tgisinternal AND tgenabled<>'D'", "schemaname='public' AND tablename='unitstates'",
            'jsonb_populate_record(NULL::public.unitstates,$1)', 'INTO seeded USING seeded_json',
            'to_jsonb(seeded) - changed_fields', 'previous_json - changed_fields',
            'IS DISTINCT FROM previous_json', 'before_count + appended::integer',
            'previous.localtimestamp + (fresh_timestamp - previous.timestamp)',
        ):
            with self.subTest(guard=guard):
                self.assertIn(guard, query)
        self.assertEqual(query.count('INSERT INTO'), 1)
        self.assertNotRegex(query, r'(?i)\b(?:UPDATE|DELETE|TRUNCATE)\b')
        self.assertTrue(query.strip().startswith('BEGIN;'))
        self.assertTrue(query.strip().endswith('COMMIT;'))
        # The only copied-row exceptions are the declared new identity/time/point.
        self.assertIn("ARRAY['unitstateid','timestamp','localtimestamp','latitude','longitude','geolocationdata']", query)

    def test_only_explicit_write_saves_sanitized_success_or_noop(self):
        for appended, state in ((True, 'Available'), (False, 'OutOfService')):
            result = success(appended, state)
            raw = 'BEGIN\n' + json.dumps({**result, 'unexpected_private_value': 'must not be published'}) + '\nCOMMIT'
            with self.subTest(appended=appended), tempfile.TemporaryDirectory() as directory, patch.object(scenario, 'ROOT', Path(directory)), patch.object(scenario, 'execute_query', return_value=raw) as execute, contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(scenario.main(['--write-training-fix', '--expected-state', state, '--expected-note', NOTE]), 0)
                execute.assert_called_once_with(scenario.build_query(state, NOTE))
                self.assertEqual(json.loads(output.getvalue()), result)
                self.assertEqual(json.loads((Path(directory) / 'scenario-reports/fresh-training-unit-position.json').read_text()), result)

    def test_failed_write_does_not_echo_exception_or_write_report(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(scenario, 'ROOT', Path(directory)), patch.object(scenario, 'execute_query', side_effect=RuntimeError('private connection secret')), contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()) as error:
            self.assertEqual(scenario.main(['--write-training-fix', '--expected-state', 'Available', '--expected-note', NOTE]), 1)
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertNotIn('private connection secret', output.getvalue() + error.getvalue())
            self.assertIn('failed or was refused', error.getvalue())

    def test_incomplete_or_inconsistent_results_cannot_claim_success(self):
        bad = [dict(success(), unit_id=51001), dict(success(), expected_state=4),
               dict(success(), status_fields_preserved=False), dict(success(), events_emitted=True),
               dict(success(), status_id=True), dict(success(), appended=False),
               dict(success(False), status_id=90002), dict(success(), latitude=0),
               dict(success(), note_preserved='true'), {}]
        for result in bad:
            with self.subTest(result=result), self.assertRaises(ValueError):
                scenario.read_report(json.dumps(result), 'Available')
        for raw in ('', '{}\n{}', 'not json'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                scenario.read_report(raw, 'Available')

    def test_remote_or_unisolated_docker_refuses_before_sql(self):
        for host, endpoint, internal, project in (
            ('tcp://remote:2375', 'unix:///local', 'true', 'resgrid-academy-test'),
            ('unix:///local', 'tcp://remote:2375', 'true', 'resgrid-academy-test'),
            ('unix:///local', 'unix:///local', 'false', 'resgrid-academy-test'),
            ('unix:///local', 'unix:///local', 'true', 'other-project'),
        ):
            fake = SimpleNamespace(STACK='resgrid-academy-test', sql=Mock(), docker=Mock(side_effect=[SimpleNamespace(stdout=json.dumps(endpoint)), SimpleNamespace(stdout=internal), SimpleNamespace(stdout=project)]))
            with self.subTest(host=host, endpoint=endpoint, internal=internal, project=project), patch.dict(sys.modules, {'manage': fake}), patch.dict(scenario.os.environ, {'DOCKER_HOST': host}), patch.object(sys, 'path', list(sys.path)):
                with self.assertRaises(ValueError):
                    scenario.execute_query('guarded query')
                fake.sql.assert_not_called()

    def test_local_named_internal_stack_passes_only_fixed_database(self):
        fake = SimpleNamespace(STACK='resgrid-academy-test', sql=Mock(return_value='result'), docker=Mock(side_effect=[SimpleNamespace(stdout='"unix:///local"'), SimpleNamespace(stdout='true\n'), SimpleNamespace(stdout='resgrid-academy-test\n')]))
        with patch.dict(sys.modules, {'manage': fake}), patch.dict(scenario.os.environ, {'DOCKER_HOST': 'unix:///local'}), patch.object(sys, 'path', list(sys.path)):
            self.assertEqual(scenario.execute_query('guarded query'), 'result')
            fake.sql.assert_called_once_with('guarded query', db='resgrid_academy')


if __name__ == '__main__':
    unittest.main()
