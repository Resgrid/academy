"""Actual69cue transcript fixtures; no audio, UI, browser or network calls."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

PRODUCTION = Path(__file__).resolve().parents[1]
ROOT = PRODUCTION.parents[1]
spec = importlib.util.spec_from_file_location('pending_author', PRODUCTION / 'author_dispatch_pending_call_take_01.py')
author = importlib.util.module_from_spec(spec); spec.loader.exec_module(author)
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues


class PendingCorrespondence(unittest.TestCase):
    def setUp(self):
        self.cues = load_cues(author.SOURCES / 'expansion/audio/app-dispatch-pending-call-to-dispatch-generated-20261028.raw.srt')
        self.anchors = (author.SOURCES / 'expansion/audio/app-dispatch-pending-call-to-dispatch-generated-20261028.one-second.txt').read_text()
        lesson = json.loads((author.SOURCES / author.BASE / (author.NAME + '.narrated-source.json')).read_text())
        self.expected = author.normalized(' '.join(s['narration'] for s in lesson['scenes']))

    def call(self):
        return author.proposed_caption_parts(self.cues, self.anchors, self.expected)

    def test_real_service_marker_cuts_preserve598words_and_raw69(self):
        original = copy.deepcopy(self.cues)
        candidates, records = self.call()
        self.assertEqual(self.cues, original)
        self.assertEqual(len(candidates), 71)
        self.assertEqual([r['split_at_actual_service_seconds'] for r in records], [57, 77])
        self.assertEqual([c['text'] for c in candidates if c['raw_cue'] == 24], ['Check the exact title and description before', 'choosing Save Pending Call.'])
        self.assertEqual(author.normalized(' '.join(c['text'] for c in candidates)), self.expected)
        self.assertTrue(all(c['audio_energy_approved'] is False for c in candidates))

    def test_same_words_marker_shifted_after_wallace_rejected(self):
        self.assertIn('[00:00:57] Wallace', self.anchors)
        self.anchors = self.anchors.replace('[00:00:57] Wallace', 'Wallace [00:00:57]', 1)
        with self.assertRaisesRegex(ValueError, 'No exact genuine service marker'):
            self.call()

    def test_missing_marker_rejected_without_interpolation(self):
        self.anchors = self.anchors.replace('[00:01:17]', '', 1)
        with self.assertRaisesRegex(ValueError, 'never interpolate'):
            self.call()

    def test_changed_raw_words_rejected(self):
        self.cues[0]['text'] += ' fabricated'
        with self.assertRaisesRegex(ValueError, 'Raw SRT words differ'):
            self.call()

    def test_anchor_outside_raw_cue_rejected(self):
        self.cues[17]['end'] = 56.5
        with self.assertRaisesRegex(ValueError, 'does not fit original cue'):
            self.call()

    def test_actual25_source_holds_and_unapproved_final_duration(self):
        scaffold = author.prepare()
        spans = scaffold['source_spans']
        self.assertEqual(len(spans), 25)
        self.assertEqual(len({s['screenshot_id'] for s in spans}), 20)
        self.assertEqual([s['screenshot_id'][:3] for s in spans[6:9]], ['006', '003', '006'])
        self.assertEqual([s['screenshot_id'][:3] for s in spans[12:14]], ['007', '010'])
        self.assertIsNone(scaffold['decoded_audio_end_and_final_hold'])
        self.assertFalse(scaffold['audio_approved'])
        self.assertFalse(scaffold['renderer_plan_created'])


if __name__ == '__main__':
    unittest.main()
