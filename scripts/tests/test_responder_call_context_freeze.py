"""Focused guards for the source-only Responder incident-context freeze."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('responder_context_freeze', ROOT / 'sources/production/freeze_responder_call_context_20261029.py')
FREEZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FREEZE)


class ResponderContextFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = json.loads((FREEZE.SOURCES / FREEZE.BASE / 'candidate.json').read_text())
        cls.captures = json.loads((FREEZE.SOURCES / FREEZE.BASE / 'captures.reviewed.json').read_text())
        review = json.loads((FREEZE.SOURCES / FREEZE.BASE / 'source-pixel-review.json').read_text())
        cls.source_rows = review['source_identity']['managed_source_snapshots']

    def test_projection_preserves_approved_words_labels_and_source_ids(self):
        lesson = FREEZE.normalize(self.candidate, self.source_rows)
        self.assertIsInstance(lesson['audience'], str)
        self.assertTrue(all(isinstance(path, str) for path in lesson['source_files']))
        for original, projected in zip(self.candidate['scenes'], lesson['scenes']):
            self.assertEqual(original['narration'], projected['narration'])
            self.assertEqual(original['required_labels'], projected['required_labels'])
            self.assertEqual(original['capture_refs'], projected['capture_evidence']['capture_refs'])
        self.assertFalse(lesson['export_ready'])
        self.assertFalse(lesson['publication_approved'])

    def test_exact_spans_cover_all_words_and_all_eleven_sources(self):
        lesson = FREEZE.normalize(self.candidate, self.source_rows)
        sequence = FREEZE.make_sequence(lesson, self.captures)
        self.assertEqual(sequence['span_count'], 14)
        self.assertEqual(len({span['capture_id'] for span in sequence['untimed_spans']}), 11)
        for scene in sequence['scenes']:
            self.assertEqual(' '.join(span['narration_exact'] for span in scene['screens']), scene['narration'])
            self.assertTrue(all(span['timing_seconds'] is None for span in scene['screens']))

    def test_invented_or_ambiguous_prose_anchors_rejected(self):
        with self.assertRaises(AssertionError):
            FREEZE.exact_parts('Actual words only.', ['Invented words'])
        with self.assertRaises(AssertionError):
            FREEZE.exact_parts('Actual words. Actual words.', ['Actual'])

    def test_required_modal_label_cannot_come_from_occluded_background(self):
        captures = deepcopy(self.captures)
        notes = next(row for row in captures['screenshots'] if row['id'].startswith('015-'))
        notes['visible_labels'].remove('Cancel')
        lesson = FREEZE.normalize(self.candidate, self.source_rows)
        with self.assertRaisesRegex(AssertionError, 'Unseen required literal'):
            FREEZE.make_sequence(lesson, captures)

    def test_paths_cannot_escape_self_contained_package(self):
        for path in ['../outside', '/absolute/source']:
            with self.assertRaises(AssertionError):
                FREEZE.safe_relative(path)


if __name__ == '__main__':
    unittest.main()
