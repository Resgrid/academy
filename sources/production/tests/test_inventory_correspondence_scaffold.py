"""Reject source/word drift and unsourced timing cuts without audio or network."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

PRODUCTION = Path(__file__).resolve().parents[1]
ROOT = PRODUCTION.parents[1]
spec = importlib.util.spec_from_file_location("inventory_scaffold", PRODUCTION / "author_core_inventory_movements_take_01.py")
author = importlib.util.module_from_spec(spec)
spec.loader.exec_module(author)
sys.path.insert(0, str(ROOT / "scripts"))
from render_walkthrough import load_cues


class ActualInventoryCorrespondence(unittest.TestCase):
    def setUp(self):
        base = author.SOURCES / author.FREEZE
        self.lesson = json.loads((base / "core-inventory-movements.narrated-source.json").read_text())
        self.spans = json.loads((base / "untimed-screen-sequence.json").read_text())["spans"]
        records = json.loads((base / "captures.reviewed.json").read_text())["screenshots"]
        self.shots = {row["id"]: row for row in records}
        self.cues = load_cues(author.SOURCES / "expansion/audio/core-inventory-movements-generated-20261028.raw.srt")

    def call(self):
        return author.correspondence(self.lesson, self.spans, self.cues, self.shots)

    def test_actual93_cues_keep_control_before_result(self):
        rows = self.call()
        self.assertEqual(len(rows), 16)
        self.assertEqual(sum(len(row["cue_correspondence"]) for row in rows), 93)
        self.assertEqual([(rows[i]["first_actual_cue"], rows[i]["actual_exported_cue_start"]) for i in [6, 8, 11]], [(38, 126.769), (45, 153.359), (58, 200.87)])
        self.assertIsNone(rows[-1]["next_source_actual_cue_start"])
        self.assertIsNone(rows[-1]["final_screen_hold_end"])

    def test_changed_spoken_word_is_rejected(self):
        self.cues[0]["text"] = self.cues[0]["text"].replace("Inventory", "Training")
        with self.assertRaisesRegex(ValueError, "SRT differs"):
            self.call()

    def test_same_words_inside_merged_cue_need_real_anchor(self):
        # The photo cut at word81 originally starts cue11. Retain every word,
        # but combine cues10/11: an author must now use genuine fine anchors.
        previous, following = self.cues[9:11]
        self.cues[9:11] = [{"start": previous["start"], "end": following["end"], "text": previous["text"] + " " + following["text"]}]
        with self.assertRaisesRegex(ValueError, "genuine service anchor required"):
            self.call()

    def test_invented_control_is_rejected(self):
        self.spans[0]["required_labels"].append("Export PDF now")
        with self.assertRaisesRegex(ValueError, "not in the retained reviewed foreground labels"):
            self.call()

    def test_source_narration_drift_is_rejected(self):
        self.spans[0]["narration_exact"] += " A made-up stock count."
        with self.assertRaisesRegex(ValueError, "Held source spans differ"):
            self.call()

    def test_missing_scene_control_is_rejected(self):
        self.lesson["scenes"][0]["required_labels"].append("Unseen receipt form")
        with self.assertRaisesRegex(ValueError, "no reviewed source"):
            self.call()


if __name__ == "__main__":
    unittest.main()
