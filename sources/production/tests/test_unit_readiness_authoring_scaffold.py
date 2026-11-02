"""Source correspondence and fail-closed guards; no synthetic media is approved."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import wave


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "author_unit_readiness_checklists_take_01.py"
SPEC = importlib.util.spec_from_file_location("unit_readiness_scaffold", SCRIPT)
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)


class UnitReadinessScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = AUTHOR.source_preflight()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="unit-checklist-negative-media-")
        self.addCleanup(self.temporary.cleanup)
        self.sources = Path(self.temporary.name).resolve()
        self.context = dict(self.real, sources=self.sources)
        self.audio = self.sources / "synthetic-invalid.m4a"
        self.corrected = self.sources / "synthetic-negative-caption.srt"
        self.qa_path = self.sources / "synthetic-negative-qa.json"
        # Invalid bytes exist solely to exercise negative branches. They are
        # never decoded as successful audio, rendered, approved or retained.
        self.audio.write_bytes(b"invalid-media-negative-fixture" * 5000)
        self.corrected.write_bytes((self.real["sources"] / AUTHOR.RAW).read_bytes())
        energy = [{"cue": n, "start": c["start"], "end": c["end"], "samples": 48000,
                   "rms": .1, "peak": .2, "below_threshold": False}
                  for n, c in enumerate(self.real["raw"], 1)]
        self.qa = {"passed": True, "issues": [],
            "lesson": {"sha256": AUTHOR.FROZEN, "words": 497, "scenes": 8},
            "audio": {"sha256": AUTHOR.sha(self.audio), "full_decode": "passed",
                      "duration_seconds": 190.64, "sample_rate": 48000, "decoded_samples": 9150720},
            "raw_captions": {"sha256": AUTHOR.INPUTS[AUTHOR.RAW], "cues": 54, "energy": energy},
            "corrected_captions": {"sha256": AUTHOR.sha(self.corrected), "cues": 54,
                                   "energy": copy.deepcopy(energy), "exact_script": True},
            "signal_threshold_rms": .001, "silent_raw_cues": 0, "silent_corrected_cues": 0,
            "possible_speech_gaps": []}

    def arguments(self):
        self.qa_path.write_text(json.dumps(self.qa))
        return dict(audio=self.audio, audio_sha=AUTHOR.sha(self.audio), corrected=self.corrected,
                    corrected_sha=AUTHOR.sha(self.corrected), qa_path=self.qa_path, qa_sha=AUTHOR.sha(self.qa_path))

    def reject(self, message, **overrides):
        arguments = self.arguments()
        arguments.update(overrides)
        with self.assertRaisesRegex(ValueError, message):
            AUTHOR.verify_media_qa(self.context, **arguments)

    def test_real_source_and_exports_are_complete_and_unchanged(self):
        self.assertEqual((len(self.real["lesson"]["scenes"]), len(self.real["raw"]),
                          len(self.real["records"]), self.real["untimed_spans"]), (8, 54, 8, 17))
        self.assertEqual(sum(len(s["narration"].split()) for s in self.real["lesson"]["scenes"]), 497)
        self.assertEqual(self.real["raw"][42]["start"], 145.289)

    def test_no_arguments_never_creates_a_plan(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["concrete_plan_written"])
        self.assertFalse(report["render_or_publication_approved"])

    def test_write_without_actual_audio_qa_makes_no_directory(self):
        output = self.sources / "uncreated" / "plan.json"
        result = subprocess.run([sys.executable, str(SCRIPT), "--write-plan", str(output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Supply actual", result.stderr)
        self.assertFalse(output.parent.exists())

    def test_submitted_photo_cannot_cover_instruction_to_submit(self):
        assignments = dict(self.real["assignments"])
        assignments[42] = assignments[43]
        with self.assertRaisesRegex(ValueError, "unseen pictured control Submit checklist"):
            AUTHOR.check_correspondence(self.real["lesson"], self.real["raw"], self.real["records"], assignments, AUTHOR.cue_references())

    def test_missing_pictured_next_control_is_rejected(self):
        records = copy.deepcopy(self.real["records"])
        next(row for row in records if row["id"].startswith("010-"))["visible_labels"].remove("Next")
        with self.assertRaisesRegex(ValueError, "unseen pictured control Next"):
            AUTHOR.check_correspondence(self.real["lesson"], self.real["raw"], records, self.real["assignments"], AUTHOR.cue_references())

    def test_illustrated_substitute_is_rejected(self):
        original = AUTHOR.read

        def changed(path):
            document = original(path)
            if Path(path).name == "captures.reviewed.json":
                document["screenshots"][0]["kind"] = "illustration"
            return document

        with mock.patch.object(AUTHOR, "read", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "substitute/non-Unit"):
                AUTHOR.source_preflight()

    def test_missing_cue_assignment_is_rejected(self):
        assignments = dict(self.real["assignments"])
        del assignments[54]
        with self.assertRaisesRegex(ValueError, "Every genuine cue"):
            AUTHOR.check_correspondence(self.real["lesson"], self.real["raw"], self.real["records"], assignments, AUTHOR.cue_references())

    def test_source_hash_drift_is_rejected_without_editing_source(self):
        with mock.patch.dict(AUTHOR.INPUTS, {AUTHOR.BASE / "narration.txt": "0" * 64}):
            with self.assertRaisesRegex(ValueError, "Frozen source/export hash differs"):
                AUTHOR.source_preflight()

    def test_partial_first_paragraph_audio_cannot_cover_whole_script(self):
        self.qa["audio"].update(duration_seconds=24.96, decoded_samples=1198080)
        self.reject("Partial/truncated audio")

    def test_independent_audio_hash_is_required(self):
        self.reject("independent expected audio SHA256", audio_sha=None)

    def test_wrong_actual_audio_hash_is_rejected(self):
        self.reject("Actual audio changed", audio_sha="0" * 64)

    def test_wrong_expected_report_hash_is_rejected(self):
        self.reject("QA report hash differs", qa_sha="0" * 64)

    def test_qa_for_different_source_is_rejected(self):
        self.qa["lesson"]["sha256"] = "0" * 64
        self.reject("full eight-scene497-word")

    def test_incomplete_decode_is_rejected(self):
        self.qa["audio"]["full_decode"] = "failed"
        self.reject("complete decode")

    def test_missing_last_cue_energy_is_rejected(self):
        self.qa["raw_captions"]["energy"].pop()
        self.reject("All54 measured cue energies")

    def test_forged_energy_bound_is_rejected(self):
        self.qa["corrected_captions"]["energy"][42]["start"] = 145
        self.reject("Invalid/missing/silent cue-energy row")

    def test_silent_actual_cue_is_rejected(self):
        self.qa["raw_captions"]["energy"][8].update(rms=0, below_threshold=True)
        self.reject("Invalid/missing/silent cue-energy row")

    def test_weakened_energy_threshold_is_rejected(self):
        self.qa["signal_threshold_rms"] = 0
        self.reject("threshold missing or weakened")

    def test_guessed_caption_cut_is_rejected(self):
        self.corrected.write_text(self.corrected.read_text().replace("00:02:25,289", "00:02:25,000"))
        self.qa["corrected_captions"]["sha256"] = AUTHOR.sha(self.corrected)
        self.reject("preserve every genuine cue bound")

    def test_forged_success_report_cannot_skip_actual_decoder(self):
        arguments = self.arguments()
        with mock.patch.object(AUTHOR, "source_preflight", return_value=self.context):
            with self.assertRaisesRegex(ValueError, "narration.decode: cannot run FFmpeg"):
                AUTHOR.build(**arguments, ffmpeg=str(self.sources / "no-decoder-exists"))

    def test_missing_ffmpeg_is_rejected_before_a_plan(self):
        with self.assertRaisesRegex(ValueError, "mandatory actual full re-decode"):
            AUTHOR.repeat_actual_decode(self.context, self.audio, self.corrected, self.qa, None)

    def test_measured_silent_pcm_cannot_use_forged_non_silent_report(self):
        # A decoder-boundary fixture writes actual zero-valued PCM, never speech.
        # Its full inventory matches the forged report, so only real measured
        # cue energy can reject it. No plan or media approval is produced.
        raw = self.sources / AUTHOR.RAW
        raw.parent.mkdir(parents=True)
        raw.write_bytes((self.real["sources"] / AUTHOR.RAW).read_bytes())

        def silent_pcm(_ffmpeg, _source, destination):
            with wave.open(str(destination), "wb") as stream:
                stream.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
                stream.writeframes(b"\0\0" * self.qa["audio"]["decoded_samples"])
            return self.qa["audio"]["duration_seconds"]

        with mock.patch("render_walkthrough.audio_duration", side_effect=silent_pcm):
            with self.assertRaisesRegex(ValueError, "Actual re-decode found silent/truncated speech"):
                AUTHOR.repeat_actual_decode(self.context, self.audio, self.corrected, self.qa, "synthetic-decoder-boundary")


if __name__ == "__main__":
    unittest.main()
