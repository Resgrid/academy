"""Guard genuine marker use and actual control/source correspondence (stdlib)."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable_test_evidence import retained_core_sources

RECIPE = Path(__file__).resolve().parents[1] / 'qa_core_groups_units_proposed_captions_20261028.py'
spec = importlib.util.spec_from_file_location('groups_units_proposal', RECIPE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class GroupsUnitsCaptionDerivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enterClassContext(retained_core_sources(m))
        cls.plan, cls.text, cls.qa = m.prepare()

    def test_exact_audio_words_and_readable_genuine_subdivisions(self):
        p = self.plan
        self.assertEqual((p['original_raw_cues'], p['proposed_derived_cues'], p['screen_intervals']), (123, 132, 44))
        self.assertEqual(p['renderer_normalized_words'], 1050)
        self.assertEqual([c['at_seconds'] for c in p['genuine_service_anchor_cuts']], [27, 80, 149, 192, 229, 237, 247, 312, 317])
        self.assertGreaterEqual(min(c['duration_seconds'] for c in p['readability']), 1)
        self.assertLessEqual(max(c['characters_per_second'] for c in p['readability']), 22)
        self.assertTrue(p['parent_timing_review_pending'])
        self.assertFalse(p['renderer_plan_created'])

    def test_each_save_precedes_its_saved_readback(self):
        cues = self.plan['cue_correspondence']
        expected = {18: [4], 41: [10], 67: [19, 20], 91: [25]}
        for number, images in expected.items():
            actual = [int(c['screenshot_id'][:3]) for c in cues if c['raw_cues'] == [number]]
            self.assertEqual(actual, images)
        self.assertEqual([int(c['screenshot_id'][:3]) for c in cues if c['raw_cues'] == [92]], [26])

    def test_available_statement_returns_to_real_units_list(self):
        entries = [c for c in self.plan['cue_correspondence'] if c['raw_cues'] == [97]]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['screenshot_id'], '026-saved-own-unit-filtered-catalog')
        self.assertEqual(entries[0]['spoken_references'], {'Available': 'Available'})
        scene = next(s for s in self.plan['scenes'] if s['scene_id'] == 'unit-read')
        self.assertEqual([int(s['capture_ref'][:3]) for s in scene['source_spans']], [25, 26, 27, 28, 26])

    def test_no_guessed_marker_or_filled_in_word_is_accepted(self):
        helper = m.utility()
        from render_walkthrough import load_cues
        raw = load_cues(m.SOURCES / m.RAW)
        anchors, _ = helper.service_anchors((m.SOURCES / m.ANCHORS).read_text())
        invented = dict(m.SPLITS[0], at_seconds=27.25)
        with self.assertRaisesRegex(AssertionError, 'guessed or interpolated'):
            helper.check_anchor(invented, raw, anchors)
        altered = dict(m.SPLITS[0], after_text='keep Station Group selected.')
        with self.assertRaises(AssertionError):
            helper.check_anchor(altered, raw, anchors)

    def test_changed_retained_input_rejected_without_refresh(self):
        with patch.dict(m.PINS, {m.RAW: '0' * 64}):
            with self.assertRaisesRegex(AssertionError, 'Changed retained input'):
                m.prepare()


if __name__ == '__main__':
    unittest.main()
