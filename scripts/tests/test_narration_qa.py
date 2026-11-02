"""Audio signal QA tests with synthetic PCM, never a listening/recording claim."""
import array
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qa_narration import cue_energy


class NarrationSignalTests(unittest.TestCase):
    def test_audible_cue_does_not_hide_an_unfinished_silent_cue(self):
        samples = array.array('h', [8000] * 1000 + [0] * 1000)
        cues = [{'start': '00:00:00,000', 'end': '00:00:01,000'},
                {'start': '00:00:01,000', 'end': '00:00:02,000'}]
        energy, issues = cue_energy(samples, 1000, cues, 2, .001)
        self.assertFalse(energy[0]['below_threshold'])
        self.assertTrue(energy[1]['below_threshold'])
        self.assertEqual(issues, ['Silent/low-energy speech cue 2'])

    def test_nonempty_energy_does_not_excuse_out_of_bounds_or_overlapping_timing(self):
        samples = array.array('h', [8000] * 2000)
        cues = [{'start': '00:00:00,000', 'end': '00:00:01,500'},
                {'start': '00:00:01,000', 'end': '00:00:03,000'}]
        _, issues = cue_energy(samples, 1000, cues, 2, .001)
        self.assertIn('Invalid, overlapping or out-of-bounds cue 2', issues)


if __name__ == '__main__':
    unittest.main()
