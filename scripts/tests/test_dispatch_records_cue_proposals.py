"""Synthetic parser guards; these fixtures are not application evidence."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('dispatch_records_cue_proposals', ROOT / 'sources/production/propose_dispatch_records_actual_cues_20261029.py')
PROPOSAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROPOSAL)


class ActualCueProposalTests(unittest.TestCase):
    def test_whole_cue_boundary_uses_exact_service_time(self):
        spans = [{'narration_exact': 'Choose Notes.'}, {'narration_exact': 'Read the result.'}]
        cues = [{'start': '00:00:00,070', 'end': '00:00:01,900', 'text': 'Choose Notes.'},
                {'start': '00:00:02,347', 'end': '00:00:04,000', 'text': 'Read the result.'}]
        unresolved = PROPOSAL.map_words(spans, cues, 'Choose Notes. Read the result.'.split())
        self.assertEqual(unresolved, [])
        self.assertEqual(spans[1]['proposed_start_seconds'], 2.347)

    def test_within_cue_word_boundary_remains_unassigned(self):
        spans = [{'narration_exact': 'Choose Notes.'}, {'narration_exact': 'Read the result.'}]
        cues = [{'start': '00:00:00,070', 'end': '00:00:04,000', 'text': 'Choose Notes. Read the result.'}]
        unresolved = PROPOSAL.map_words(spans, cues, 'Choose Notes. Read the result.'.split())
        self.assertIsNone(spans[1]['proposed_start_seconds'])
        self.assertEqual(unresolved[0]['raw_cue'], 1)
        self.assertEqual(unresolved[0]['exact_words_before_boundary_in_cue'], 'Choose Notes.')
        self.assertIsNone(unresolved[0]['resolved_cut_seconds'])

    def test_changed_source_span_words_rejected(self):
        with self.assertRaises(AssertionError):
            PROPOSAL.map_words([{'narration_exact': 'Invented action.'}],
                               [{'start': '00:00:00,000', 'end': '00:00:01,000', 'text': 'Actual words.'}],
                               ['Actual', 'words.'])

    def test_changed_actual_caption_words_rejected(self):
        with self.assertRaises(AssertionError):
            PROPOSAL.map_words([{'narration_exact': 'Actual words.'}],
                               [{'start': '00:00:00,000', 'end': '00:00:01,000', 'text': 'Invented action.'}],
                               ['Actual', 'words.'])


if __name__ == '__main__':
    unittest.main()
