"""Synthetic recorder guard tests; these are not native product evidence.

No simulator, application, API, Git operation or credential is used here.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ui = load('academy_native_ui_guard_tests', 'native_ui.py')
build = load('academy_native_build_guard_tests', 'native_build_command.py')
DEVICE = '11111111-2222-4333-8444-555555555555'


class SessionGuardTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.session = {
            'owner': 'academy_training', 'dedicated': True,
            'user_session_reused': False, 'udid': DEVICE,
            'name': 'Academy Training Unit iPad 20261028',
        }
        self.write_session()
        (self.root / 'devices-before.private.json').write_text(json.dumps({'devices': {'test-runtime': []}}))
        self.patch = mock.patch.object(ui, 'BASE', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write_session(self):
        (self.root / 'session.json').write_text(json.dumps(self.session))

    def runner(self, **ready_changes):
        root = self.root / DEVICE / 'Containers/Data/Application/fixture-runner'
        inbox = root / 'Documents/AcademyDriver'
        inbox.mkdir(parents=True)
        ready = {'simulator_udid': DEVICE, 'normal_ui_only': True, **ready_changes}
        (inbox / 'ready.json').write_text(json.dumps(ready))
        return root, inbox

    def test_accepts_new_owned_session_only(self):
        self.assertEqual(ui.actual_session()['udid'], DEVICE)

    def test_rejects_preexisting_user_device(self):
        (self.root / 'devices-before.private.json').write_text(json.dumps({'devices': {'test-runtime': [{'udid': DEVICE}]}}))
        with self.assertRaisesRegex(ValueError, 'pre-existing'):
            ui.actual_session()

    def test_rejects_reused_or_unowned_session(self):
        for field, value in [('owner', 'another_session'), ('dedicated', False), ('user_session_reused', True)]:
            with self.subTest(field=field):
                original = self.session[field]
                self.session[field] = value
                self.write_session()
                with self.assertRaisesRegex(ValueError, 'dedicated'):
                    ui.actual_session()
                self.session[field] = original

    def test_rejects_non_uuid_device_before_native_command(self):
        self.session['udid'] = 'booted'
        self.write_session()
        with mock.patch.object(ui.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                ui.actual_session()
            run.assert_not_called()

    def test_only_own_runner_container_is_queried(self):
        root, inbox = self.runner()
        response = SimpleNamespace(returncode=0, stdout=str(root))
        with mock.patch.object(ui.subprocess, 'run', return_value=response) as run:
            self.assertEqual(ui.runner_directory(self.session), inbox.resolve())
            self.assertEqual(run.call_args.args[0], ['xcrun', 'simctl', 'get_app_container', DEVICE, ui.RUNNER_BUNDLE, 'data'])

    def test_rejects_container_from_other_device(self):
        response = SimpleNamespace(returncode=0, stdout='/tmp/another-device/Containers/Data/Application/runner')
        with mock.patch.object(ui.subprocess, 'run', return_value=response):
            with self.assertRaisesRegex(ValueError, 'outside'):
                ui.runner_directory(self.session)

    def test_rejects_stale_runner_binding(self):
        root, _ = self.runner(simulator_udid='66666666-2222-4333-8444-555555555555')
        with mock.patch.object(ui.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=str(root))):
            with self.assertRaisesRegex(ValueError, 'binding'):
                ui.runner_directory(self.session)

    def test_pending_command_is_not_overwritten(self):
        root, inbox = self.runner()
        pending = inbox / 'request.json'
        pending.write_text('{"action":"inspect"}')
        with mock.patch.object(ui.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=str(root))):
            with self.assertRaisesRegex(ValueError, 'still pending'):
                ui.send('signin')
        self.assertEqual(pending.read_text(), '{"action":"inspect"}')
        self.assertFalse((inbox / 'credentials.private.json').exists())

    def test_unknown_permission_grant_action_is_rejected(self):
        with mock.patch.object(ui.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'Unsupported'):
                ui.send('grant_location_permission')
            run.assert_not_called()


class CaptureAndRedactionTests(unittest.TestCase):
    def test_capture_fails_before_screenshot_when_privacy_guard_fails(self):
        with mock.patch.object(ui, 'send', return_value={'result': {'capture_allowed': False}}) as send, mock.patch.object(ui.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'Credentials/foreground'):
                ui.capture('001-synthetic-test')
            self.assertEqual(send.call_args_list, [mock.call('capture_guard')])
            run.assert_not_called()

    def test_capture_name_cannot_escape_raw_directory(self):
        with mock.patch.object(ui, 'send') as send:
            for name in ['../../other', '/tmp/other', 'new-image', '001-other.png']:
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'numbered'):
                    ui.capture(name)
            send.assert_not_called()

    def test_known_value_and_structural_credentials_are_scrubbed(self):
        example = 'a_private_demo_value_for_redaction'
        jwt = '.'.join(['eyJ' + 'a' * 24, 'b' * 24, 'c' * 24])
        map_value = '.'.join(['pk', 'x' * 20, 'y' * 20])
        text = 'diagnostic ' + ' '.join([example, jwt, map_value])
        cleaned = build.scrub(text, [example])
        for value in [example, jwt, map_value]:
            self.assertNotIn(value, cleaned)
        self.assertEqual(cleaned.count('[REDACTED]'), 3)

    def test_command_arguments_reject_sensitive_value_before_execution(self):
        example = 'a_private_demo_value_for_redaction'
        with self.assertRaisesRegex(ValueError, 'command arguments'):
            build.reject_sensitive_arguments(['tool', '--value=' + example], [example])
        build.reject_sensitive_arguments(['tool', '--configuration=local'], [example])


if __name__ == '__main__':
    unittest.main()
