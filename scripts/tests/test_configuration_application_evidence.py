"""Synthetic in-memory contracts; no source images or review receipts are made."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_capture_evidence import _Validator, instruction_scene_digest
from expansion_site import _scene_screens, PublicationError


class ConfigurationSourceTests(unittest.TestCase):
    def declaration(self, **changes):
        return dict({'app': 'Core', 'for_app': 'BigBoard', 'role': 'configuration_source',
                     'purpose': 'SYNTHETIC TEST ONLY: identify the Core timer settings.'}, **changes)

    def test_core_configuration_requires_exact_source_role_and_client(self):
        validator = _Validator(Path('.'))
        declarations = validator.supporting_applications([self.declaration()], 'BigBoard')
        self.assertEqual(validator.issues, [])
        self.assertEqual(validator.instruction_application({'instruction_app': 'Core'}, 'BigBoard', declarations, 'scene'), 'Core')
        self.assertEqual(validator.issues, [])
        for change in ({'app': 'Mailpit'}, {'app': 'Dispatch'}, {'for_app': 'IC'}, {'role': 'receiver'}):
            invalid = _Validator(Path('.'))
            invalid.supporting_applications([self.declaration(**change)], 'BigBoard')
            self.assertTrue(invalid.issues)

    def test_undeclared_or_unrelated_instruction_app_is_rejected(self):
        for app in ('Core', 'Dispatch', 'Mailpit', 'unknown'):
            validator = _Validator(Path('.'))
            validator.instruction_application({'instruction_app': app}, 'BigBoard', {}, 'scene')
            self.assertTrue(validator.issues)

    def test_mailpit_receiver_declaration_stays_scoped_to_core(self):
        declaration = {'app': 'Mailpit', 'for_app': 'Core', 'role': 'controlled_local_receiver', 'purpose': 'SYNTHETIC TEST ONLY: receiver'}
        for primary in ('Core', 'BigBoard'):
            validator = _Validator(Path('.'))
            validator.supporting_applications([declaration], primary)
            self.assertEqual(bool(validator.issues), primary != 'Core')

    def test_configuration_context_is_bound_in_scene_digest(self):
        scene = {'id': 'one', 'title': 'Timer', 'kind': 'operational', 'start': 0, 'end': 5,
                 'visual_required_labels': ['Unit Status Timers'], 'screens': [], 'captions': []}
        original = instruction_scene_digest(scene, {})
        with_context = dict(scene, instruction_app='Core')
        self.assertNotEqual(original, instruction_scene_digest(with_context, {}))
        self.assertEqual(original, instruction_scene_digest(scene, {}))

    def test_client_or_receiver_screens_cannot_supply_core_settings_labels(self):
        for image_app, passes in [('Core', True), ('BigBoard', False), ('Mailpit', False)]:
            shot = {'app': image_app, 'provenance': {'captured_at': '2026-10-01T00:00:00Z'}}
            scene = {'id': 'one', 'title': 'Timer', 'kind': 'operational', 'start': 0, 'end': 5,
                     'instruction_app': 'Core', 'visual_required_labels': ['Unit Status Timers'],
                     'screens': [{'screenshot_id': 'synthetic', 'start': 0, 'end': 5}], 'captions': []}
            scene['instruction_review'] = {'reviewer': 'SYNTHETIC IN-MEMORY TEST', 'reviewed_at': datetime.now(timezone.utc).isoformat(),
                                           'passed': True, 'correspondence_reviewed': True, 'no_unseen_controls': True,
                                           'mapping_sha256': instruction_scene_digest(scene, {'synthetic': shot})}
            validator = _Validator(Path('.'))
            validator.instruction_review(scene, {'synthetic': shot}, {'synthetic': {'unit status timers'}}, 'scene', 'Core')
            self.assertEqual(not validator.issues, passes)

    def test_publication_accepts_only_declared_configuration_source_labels(self):
        public = {'app': 'BigBoard', 'scenes': [{'id': 'one', 'required_labels': ['Unit Status Timers']}]}
        scene = {'id': 'one', 'start': 0, 'instruction_app': 'Core',
                 'visual_required_labels': ['Unit Status Timers'],
                 'screens': [{'screenshot_id': 'synthetic', 'required_labels': ['Unit Status Timers']}],
                 'captions': []}
        evidence = {'supporting_applications': [self.declaration()], 'scenes': [scene]}
        for video in (False, True):
            for app, passes in [('Core', True), ('BigBoard', False), ('Mailpit', False)]:
                screenshots = {'synthetic': {'app': app, '_observed_names': {'unit status timers'}}}
                if passes:
                    self.assertEqual(_scene_screens(public, evidence, screenshots, video)[0], {'one': ['synthetic']})
                else:
                    with self.assertRaises(PublicationError):
                        _scene_screens(public, evidence, screenshots, video)
            undeclared = dict(evidence, supporting_applications=[])
            with self.assertRaises(PublicationError):
                _scene_screens(public, undeclared, {'synthetic': {'app': 'Core', '_observed_names': {'unit status timers'}}}, video)


if __name__ == '__main__':
    unittest.main()
