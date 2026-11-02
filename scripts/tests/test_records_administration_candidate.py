"""Read-only guards for the bounded Core custom-definition source candidate."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('records_admin_candidate', ROOT / 'sources/production/build_core_records_administration_candidate_20261030.py')
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class RecordsAdministrationCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lesson, cls.assets, _ = BUILD.prepare()
        cls.captures = json.loads(cls.assets['captures.reviewed.json'])
        cls.sequence = json.loads(cls.assets['screen-sequence.untimed.json'])

    def test_all_exact_prose_has_untimed_source_and_literal_coverage(self):
        rows = {row['id']: row for row in self.captures['screenshots']}
        self.assertEqual(len(self.lesson['scenes']), 16)
        self.assertEqual(sum(len(scene['screens']) for scene in self.sequence['scenes']), 39)
        for scene, mapping in zip(self.lesson['scenes'], self.sequence['scenes']):
            self.assertEqual(' '.join(screen['narration_span'] for screen in mapping['screens']), scene['narration'])
            for screen in mapping['screens']:
                self.assertTrue(set(screen['required_labels']) <= set(rows[screen['capture_id']]['visible_labels']))
                self.assertIsNone(screen['timing'])

    def test_wrong_form_dom_only_and_misleading_frames_cannot_qualify(self):
        excluded = {row['alias'] for row in self.captures['excluded_sources']}
        included = {row['source_review_alias'] for row in self.captures['screenshots']}
        for alias in ['a006', 'p005', 'p006', 'u015', 'u018']:
            self.assertIn(alias, excluded)
            self.assertNotIn(alias, included)

    def test_numbering_frame_does_not_supply_offscreen_client_controls(self):
        self.assertNotIn('Client surfaces', BUILD.LABELS['u019'])
        self.assertNotIn('Standard', BUILD.LABELS['u019'])
        self.assertTrue({'Client surfaces', 'Standard', 'Fields'} <= set(BUILD.LABELS['u020']))

    def test_all_six_sectors_are_spoken_without_field_runtime_claim(self):
        self.assertEqual(len(self.lesson['sector_examples']), 6)
        last = self.lesson['scenes'][-1]['narration'].casefold()
        for phrase in ['fire and ems', 'community-care', 'mental-health', 'search-and-rescue', 'security', 'wildland', 'industrial']:
            self.assertIn(phrase, last)
        self.assertFalse(self.lesson['narration_frozen'])
        self.assertFalse(self.lesson['export_ready'])
        self.assertTrue(self.lesson['parent_full_script_review_pending'])

    def test_public_fixture_and_one_record_replay_identity_are_retained(self):
        self.assertEqual(len(self.assets['fixture/academy-record-exercise.txt']), 242)
        log = json.loads(self.assets['actual-operation-log.json'])
        delta = json.loads(self.assets['scenario.replay-delta.json'])
        self.assertEqual(log['draft_reference'], 'D-EKCMS')
        self.assertEqual(log['issued_record_number'], 'TRNADM-2026-0001')
        self.assertEqual(delta['actual_example']['state_of_record'], 'Finalized')
        self.assertFalse(delta['automatic_replay_or_DB_seed'])


if __name__ == '__main__':
    unittest.main()
