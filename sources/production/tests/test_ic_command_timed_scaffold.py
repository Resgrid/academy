"""Negative media-gate tests never approve or render their synthetic inputs."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "author_ic_command_take_01_timed.py"
SPEC = importlib.util.spec_from_file_location("ic_timed_scaffold", SCRIPT)
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)


class IcCommandTimedScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ic-audio-gate-test-")
        self.addCleanup(self.temp.cleanup)
        self.sources = Path(self.temp.name)
        self.audio = self.sources / "synthetic-invalid-audio.m4a"
        self.corrected = self.sources / "synthetic-invalid-captions.srt"
        self.qa = self.sources / "synthetic-negative-qa.json"
        # Deliberately invalid media is only used to reach a negative QA branch.
        # It is never passed to a decoder, renderer or publication gate.
        self.audio.write_bytes(b"invalid-media-for-negative-test" * 6000)
        self.corrected.write_text("Not an SRT; no test approves this fixture.\n")
        self.audio_sha = AUTHOR.sha(self.audio)
        self.corrected_sha = AUTHOR.sha(self.corrected)
        energy = [{"below_threshold": False, "samples": 48000, "rms": .1} for _ in range(104)]
        self.invalid_qa = {
            "passed": True, "issues": [],
            "lesson": {"sha256": AUTHOR.FROZEN, "words": 887, "scenes": 9},
            "audio": {"sha256": self.audio_sha, "full_decode": "passed",
                      "duration_seconds": 355.2, "sample_rate": 48000, "decoded_samples": 17_049_600},
            "silent_raw_cues": 0, "silent_corrected_cues": 0,
            "signal_threshold_rms": .001,
            "raw_captions": {"sha256": AUTHOR.TRANSCRIPTS["app-ic-command-board.fresh.srt"],
                             "cues": 104, "energy": energy},
            "corrected_captions": {"sha256": self.corrected_sha, "cues": 104,
                                   "energy": list(energy), "exact_script": True},
            "possible_speech_gaps": [],
        }

    def reject(self, pattern, **overrides):
        self.qa.write_text(json.dumps(self.invalid_qa))
        arguments = dict(sources=self.sources, audio=self.audio, audio_sha=self.audio_sha,
                         corrected=self.corrected, corrected_sha=self.corrected_sha,
                         qa_path=self.qa, qa_sha=AUTHOR.sha(self.qa), raw=[{"end": 355.069}])
        arguments.update(overrides)
        with self.assertRaisesRegex(ValueError, pattern):
            AUTHOR.verify_media_qa(**arguments)

    def test_real_transcripts_retain_exact_frozen_words(self):
        lesson, recipe, freeze, cues, records, source_ids = AUTHOR.transcript_preflight(AUTHOR.ROOT)
        self.assertEqual((len(lesson["scenes"]), recipe["word_count"], len(cues), len(records)), (9, 887, 104, 19))
        self.assertEqual(source_ids[58], "ic-33-saved-objective-and-partial-need")
        self.assertEqual(source_ids[59], "ic-37-command-note-visibility")
        self.assertEqual(cues[58]["start"], 192.729)

    def test_write_without_actual_qa_refuses_before_creating_output(self):
        output = self.sources / "must-not-exist" / "plan.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "--write", str(output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Supply actual", result.stderr)
        self.assertFalse(output.parent.exists())

    def test_explicit_audio_hash_is_required(self):
        self.reject("explicit actual audio SHA256", audio_sha=None)

    def test_estimated_exports_are_rejected(self):
        self.reject("Estimated exports", audio=self.sources / "audio.estimated-before-generation.m4a")

    def test_failed_qa_is_rejected(self):
        self.invalid_qa["passed"] = False
        self.reject("QA must pass")

    def test_wrong_frozen_script_is_rejected(self):
        self.invalid_qa["lesson"]["sha256"] = "0" * 64
        self.reject("another narrated-source snapshot")

    def test_incomplete_decode_is_rejected(self):
        self.invalid_qa["audio"]["full_decode"] = "failed"
        self.reject("successful complete decode")

    def test_silent_cue_is_rejected(self):
        self.invalid_qa["silent_raw_cues"] = 1
        self.reject("must be non-silent")

    def test_missing_cue_energy_inventory_is_rejected(self):
        self.invalid_qa["raw_captions"]["energy"] = []
        self.reject("Incomplete, silent or low-energy")

    def test_weakened_signal_threshold_is_rejected(self):
        self.invalid_qa["signal_threshold_rms"] = 0
        self.reject("threshold is missing or weakened")

    def test_empty_audio_is_rejected_even_with_matching_hash(self):
        self.audio.write_bytes(b"empty")
        self.audio_sha = AUTHOR.sha(self.audio)
        self.invalid_qa["audio"]["sha256"] = self.audio_sha
        self.reject("empty placeholder")


if __name__ == "__main__":
    unittest.main()
