"""Guards for the pre-audio-QA Reporting proposal; no media/approval is created."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'prepare_core_reporting_proposed_correspondence_20261029.py'
SPEC = importlib.util.spec_from_file_location('reporting_proposal', PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReportingProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proposal, cls.manifest = MODULE.prepare()

    def test_actual_inputs_have_all_cues_and_open_final_hold(self):
        p = self.proposal
        self.assertEqual((len(p['cue_correspondence']), len(p['source_spans']), p['source_images']), (115, 27, 23))
        self.assertEqual([c['cue'] for c in p['cue_correspondence']], list(range(1, 116)))
        self.assertIsNone(p['decoded_audio_duration_seconds'])
        self.assertIsNone(p['source_spans'][-1]['proposed_end_seconds'])
        self.assertFalse(p['audio_qa_approved'])
        self.assertFalse(p['human_listening_approved'])
        self.assertFalse(p['renderer_plan_created'])
        self.assertEqual(p['anchor_cuts_used'], [])

    def test_headers_precede_lower_rows_and_reporting_scopes_stay_distinct(self):
        spans = self.proposal['source_spans']
        self.assertEqual([x['capture_id'][:3] for x in spans],
                         ['001', '002', '006', '003', '007', '008', '009', '010', '011', '012', '014',
                          '015', '016', '017', '015', '018', '019', '023', '020', '021', '022', '024',
                          '025', '027', '010', '006', '015'])
        self.assertGreaterEqual(self.proposal['minimum_closed_hold_seconds'], 3)
        self.assertFalse({'004', '005', '013', '026'} & {x['capture_id'][:3] for x in spans})

    def test_invented_literal_or_spoken_reference_is_rejected(self):
        row = {'visible_labels': ['Download CSV']}
        with self.assertRaisesRegex(AssertionError, 'Unobserved literal'):
            MODULE.validate_references({'text': 'Download CSV'}, {'Print PDF': 'Download CSV'}, row)
        with self.assertRaisesRegex(AssertionError, 'Spoken reference absent'):
            MODULE.validate_references({'text': 'Keep the file'}, {'Download CSV': 'Download CSV'}, row)
        MODULE.validate_references({'text': 'Use Download CSV'}, {'Download CSV': 'Download CSV'}, row)

    def test_span_cannot_cut_inside_a_raw_cue(self):
        cues = [{'start': 0.1, 'end': 4.0, 'text': 'Choose Group then Run Report.'}]
        rows = {'a': {'id': 'a', 'file': 'a.jpg', 'sha256': 'a' * 64, 'visible_labels': ['Group']}}
        compact = {'scenes': [{'scene_id': 'test', 'title': 'test', 'ordered_screens': [
            {'capture_id': 'a', 'required_labels': ['Group'], 'exact_narration_span': 'Choose Group'}]}]}
        with self.assertRaisesRegex(AssertionError, 'crosses a cue boundary'):
            MODULE.match_spans(cues, compact, rows)

    def test_missing_required_control_and_flash_cut_are_rejected(self):
        rows = {'a': {'id': 'a', 'file': 'a.jpg', 'sha256': 'a' * 64, 'visible_labels': ['Group']}}
        def compact(first_label):
            return {'scenes': [{'scene_id': 'test', 'title': 'test', 'ordered_screens': [
                {'capture_id': 'a', 'required_labels': [first_label], 'exact_narration_span': 'First'},
                {'capture_id': 'a', 'required_labels': ['Group'], 'exact_narration_span': 'Second'}]}]}
        cues = [{'start': 0.1, 'end': 0.9, 'text': 'First'}, {'start': 1.0, 'end': 4.0, 'text': 'Second'}]
        with self.assertRaisesRegex(AssertionError, 'Missing required literal'):
            MODULE.match_spans(cues, compact('Run Report'), rows)
        with self.assertRaisesRegex(AssertionError, 'Unreadable proposed source hold'):
            MODULE.match_spans(cues, compact('Group'), rows)

    def test_absent_or_stale_service_anchor_sequence_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, 'Missing genuine'):
            MODULE.service_anchor_words('No actual markers')
        with self.assertRaisesRegex(AssertionError, 'Out-of-order'):
            MODULE.service_anchor_words('[00:00:02] First [00:00:01] second')


if __name__ == '__main__':
    unittest.main()
