"""Synthetic contracts only; these fixtures are never application/public evidence."""

import copy
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import render_walkthrough as renderer
from verify_capture_evidence import verify, visible_controls_digest, instruction_scene_digest


def png(width=1280, height=720, color=b"\x24\x40\x58"):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    pixels = (b"\0" + color * width) * height
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


class WalkthroughContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-walkthrough-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.lesson_path, self.plan_path = self.root / "lesson.json", self.root / "plan.json"
        (self.root / "capture.png").write_bytes(png())
        with wave.open(str(self.root / "voice.wav"), "wb") as stream:
            stream.setnchannels(1); stream.setsampwidth(2); stream.setframerate(48000)
            stream.writeframes(b"\0\0" * 48000)  # Test signal only, never fallback narration.
        (self.root / "voice.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nSelect Save draft to keep Draft.\n\n")
        self.lesson = {"id": "synthetic-draft", "title": "Synthetic fixture", "app": "Core", "scenes": [
            {"id": "draft", "title": "Save a draft", "required_labels": ["Save draft", "Draft"], "narration": "Select Save draft to keep Draft."}]}
        digest = renderer._hash(self.root / "capture.png")
        self.capture = {"id": "draft-screen", "app": "Core", "kind": "application_screenshot", "file": "capture.png", "sha256": digest, "width": 1280, "height": 720,
                        "visible_labels": ["Save draft", "Draft"], "provenance": {"method": "browser_screenshot", "url": "http://localhost:8000/records/draft/1", "captured_at": "2020-01-01T00:00:00Z"}}
        self.additional_captures = []
        self.plan = {"schema_version": 1, "lesson_id": "synthetic-draft", "duration_seconds": 1,
                     "narration": {"file": "voice.wav", "sha256": renderer._hash(self.root / "voice.wav"), "kind": "approved_natural_narration"},
                     "captions": {"file": "voice.srt", "sha256": renderer._hash(self.root / "voice.srt"), "kind": "speech_timed_srt"},
                     "capture_manifests": [], "screenshot_reviews": {"draft-screen": self.approval(digest, application_visible=True, labels_legible=True, no_errors=True)},
                     "scenes": [{"id": "draft", "start": 0, "end": 1,
                                 "screens": [{"screenshot_id": "draft-screen", "start": 0, "end": 1}],
                                 "captions": [{"cue": 1, "screenshot_id": "draft-screen", "required_labels": ["Save draft", "Draft"]}]}]}
        self.plan["narration"]["approval"] = self.approval(self.plan["narration"]["sha256"], complete_natural_narration=True)
        self.plan["captions"]["approval"] = self.approval(self.plan["captions"]["sha256"], audio_sha256=self.plan["narration"]["sha256"], speech_timing_reviewed=True)

    def approval(self, digest, **flags):
        return {"reviewer": "synthetic unittest fixture", "reviewed_at": "2020-01-02T00:00:00Z", "sha256": digest, **flags}

    def save(self):
        (self.root / "manifest.json").write_text(json.dumps({"screenshots": [self.capture, *self.additional_captures]}))
        self.plan["capture_manifests"] = [{"file": "manifest.json", "sha256": renderer._hash(self.root / "manifest.json")}]
        self.lesson_path.write_text(json.dumps(self.lesson))
        self.plan_path.write_text(json.dumps(self.plan))

    def validate(self):
        self.save()
        return renderer.validate_inputs(self.lesson_path, self.plan_path, self.root)

    def reject(self, fragment):
        with self.assertRaisesRegex(renderer.AssemblyError, fragment):
            self.validate()

    def test_legitimate_incident_record_draft_is_allowed(self):
        recipe = self.validate()
        self.assertEqual(recipe["scenes"][0]["captions"][0]["text"], "Select Save draft to keep Draft.")
        self.assertFalse(recipe["screenshots"]["draft-screen"]["layout"]["cropped"])

    def local_receiver_plan(self):
        self.plan['supporting_applications'] = [{'app': 'Mailpit', 'for_app': 'Core', 'role': 'controlled_local_receiver', 'purpose': 'Inspect the isolated SMTP receipt.'}]
        (self.root / 'receiver.png').write_bytes(png(color=b'\x40\x24\x58'))
        receiver = dict(self.capture, id='receiver', app='Mailpit', file='receiver.png', sha256=renderer._hash(self.root / 'receiver.png'),
                        visible_labels=['Mailpit', 'Inbox'], provenance=dict(self.capture['provenance'], url='http://127.0.0.1:18126/'))
        self.additional_captures = [receiver]
        self.plan['screenshot_reviews']['receiver'] = self.approval(receiver['sha256'], application_visible=True, labels_legible=True, no_errors=True)
        self.lesson['scenes'][0]['narration'] += ' Inspect Mailpit.'
        (self.root / 'voice.srt').write_text('1\n00:00:00,000 --> 00:00:00,500\nSelect Save draft to keep Draft.\n\n2\n00:00:00,500 --> 00:00:01,000\nInspect Mailpit.\n\n')
        self.plan['captions']['sha256'] = renderer._hash(self.root / 'voice.srt')
        self.plan['captions']['approval']['sha256'] = self.plan['captions']['sha256']
        scene = self.plan['scenes'][0]
        scene['screens'] = [{'screenshot_id': 'draft-screen', 'start': 0, 'end': .5}, {'screenshot_id': 'receiver', 'start': .5, 'end': 1}]
        scene['captions'].append({'cue': 2, 'screenshot_id': 'receiver', 'required_labels': ['Mailpit']})
        return receiver

    def test_explicit_loopback_receiver_keeps_truthful_app_and_other_gates(self):
        receiver = self.local_receiver_plan()
        self.assertEqual(self.validate()['screenshots']['receiver']['metadata']['app'], 'Mailpit')
        self.plan['screenshot_reviews']['receiver']['no_errors'] = False
        self.reject('genuine visual review')
        self.plan['screenshot_reviews']['receiver']['no_errors'] = True
        receiver['sha256'] = '0' * 64
        self.reject('hash mismatch')

    def test_receiver_requires_authored_role_purpose_and_loopback_provenance(self):
        self.local_receiver_plan()
        original = copy.deepcopy(self.plan['supporting_applications'])
        self.plan.pop('supporting_applications')
        self.reject('explicitly declared')
        self.plan['supporting_applications'] = original
        self.additional_captures[0]['provenance']['url'] = 'https://receiver.example/'
        self.reject('loopback local receiver')
        self.additional_captures[0]['provenance']['url'] = 'http://localhost:18126/'
        for key, value in [('role', 'another_app'), ('for_app', 'Responder'), ('purpose', '')]:
            with self.subTest(key=key):
                self.plan['supporting_applications'] = copy.deepcopy(original)
                self.plan['supporting_applications'][0][key] = value
                self.reject('supporting_applications')

    def test_receiver_cannot_supply_authored_primary_app_controls(self):
        self.local_receiver_plan()
        self.lesson['scenes'][0]['required_labels'].append('Mailpit')
        self.reject('unmatched authored UI controls')

    def test_real_millisecond_timestamps_survive_float_addition_order(self):
        path = self.root / 'minute-boundary.srt'
        path.write_text('1\n00:01:34,199 --> 00:01:37,229\nOpen Dispatchable Statuses.\n\n')
        cues = renderer.load_cues(path)
        self.assertEqual(len(cues), 1)
        self.assertAlmostEqual(cues[0]['start'], 94.199, places=9)
        self.assertAlmostEqual(cues[0]['end'], 97.229, places=9)

    def reviewed_scene_plan(self):
        self.plan['instruction_mapping'] = 'reviewed_scene_coverage'
        authored, scene = self.lesson['scenes'][0], self.plan['scenes'][0]
        cues = renderer.load_cues(self.root / 'voice.srt')
        built = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational', 'start': scene['start'], 'end': scene['end'],
                 'screens': scene['screens'], 'visual_required_labels': authored['required_labels'],
                 'captions': [dict(cues[entry['cue']-1], screenshot_id=entry['screenshot_id'], required_labels=entry['required_labels'], instructional=entry.get('instructional', True), spoken_references=entry.get('spoken_references', {})) for entry in scene['captions']]}
        scene['instruction_review'] = {'passed': True, 'reviewer': 'synthetic contract fixture', 'reviewed_at': '2020-01-02T00:00:00Z',
            'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(built, {self.capture['id']: self.capture})}

    def test_reviewed_visual_scene_coverage_does_not_force_narrator_to_recite_context_labels(self):
        self.capture['visible_labels'].append('Department Settings')
        self.lesson['scenes'][0]['required_labels'].append('Department Settings')
        self.reviewed_scene_plan()
        self.assertIn('Department Settings', self.validate()['scenes'][0]['visual_required_labels'])

    def test_reviewed_mode_cannot_bypass_unseen_context_or_stale_correspondence_review(self):
        self.lesson['scenes'][0]['required_labels'].append('Unseen control')
        self.reviewed_scene_plan()
        self.reject('every required scene label must be visible')
        self.lesson['scenes'][0]['required_labels'].pop()
        self.reviewed_scene_plan()
        self.plan['scenes'][0]['instruction_review']['mapping_sha256'] = '0' * 64
        self.reject('exact current scene')

    def test_natural_reference_preserves_literal_control_and_frozen_spoken_phrase(self):
        self.capture['visible_labels'] = ['Save & close', 'Draft']
        self.lesson['scenes'][0].update(required_labels=['Save & close', 'Draft'], narration='Select Save and close to keep Draft.')
        (self.root / 'voice.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nSelect Save and close to keep Draft.\n\n')
        self.plan['captions']['sha256'] = renderer._hash(self.root / 'voice.srt')
        self.plan['captions']['approval'] = self.approval(self.plan['captions']['sha256'], audio_sha256=self.plan['narration']['sha256'], speech_timing_reviewed=True)
        self.plan['scenes'][0]['captions'][0].update(required_labels=['Save & close', 'Draft'], spoken_references={'Save & close': 'Save and close'})
        self.reviewed_scene_plan()
        self.assertEqual(self.validate()['scenes'][0]['captions'][0]['spoken_references'], {'Save & close': 'Save and close'})
        self.plan['scenes'][0]['captions'][0]['spoken_references']['Save & close'] = 'invented phrase'
        self.reviewed_scene_plan()
        self.reject('exact phrase from this speech cue')

    def test_illustrated_substitute_is_rejected(self):
        self.capture["kind"] = "illustration"
        self.reject("illustrated substitutes")

    def test_source_app_must_match(self):
        self.capture["app"] = "Unit"
        self.reject("screenshot app must match")

    def test_unknown_source_app_is_rejected_cleanly(self):
        self.lesson["app"] = {}
        self.reject("lesson.app")

    def test_missing_actual_control_is_rejected(self):
        self.capture["visible_labels"] = ["Draft"]
        self.reject("visible control 'Save draft' is missing")

    def icon_inputs(self):
        words = "Select Attach, then Send."
        labels = ["Attach", "Send"]
        self.lesson["scenes"][0].update(narration=words, required_labels=labels)
        (self.root / "voice.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\n" + words + "\n\n")
        self.plan["captions"]["sha256"] = renderer._hash(self.root / "voice.srt")
        self.plan["captions"]["approval"] = self.approval(self.plan["captions"]["sha256"], audio_sha256=self.plan["narration"]["sha256"], speech_timing_reviewed=True)
        self.plan["scenes"][0]["captions"][0]["required_labels"] = labels
        self.capture["visible_labels"] = ["Chat"]
        self.capture["visible_controls"] = [
            {"accessible_name": name, "role": "button", "rect": {"x": x, "y": 640, "width": 32, "height": 32}, "icon_only": True, "provenance": "browser_dom"}
            for name, x in [("Attach", 1100), ("Send", 1180)]
        ]
        self.capture["capture_review"] = self.approval(self.capture["sha256"], passed=True,
            controls_sha256=visible_controls_digest(self.capture["visible_controls"]),
            application_visible=True, no_errors=True, controls_reviewed=True,
            controls_fully_visible=True, controls_unobstructed=True)

    def test_renderer_accepts_reviewed_icon_send_attach_without_inventing_literal_text(self):
        self.icon_inputs()
        recipe = self.validate()
        self.assertEqual(recipe["screenshots"]["draft-screen"]["metadata"]["visible_labels"], ["Chat"])
        self.assertIn("send", recipe["screenshots"]["draft-screen"]["observed_names"])
        self.assertIn("attach", recipe["screenshots"]["draft-screen"]["observed_names"])

    def test_renderer_rejects_unreviewed_invented_and_clipped_icon_evidence(self):
        self.icon_inputs()
        self.capture["capture_review"]["controls_unobstructed"] = False
        self.reject("actual visual review")
        self.icon_inputs()
        self.capture["visible_controls"][0]["accessible_name"] = "Invented action"
        self.reject("exact ordered control observations")
        self.icon_inputs()
        self.capture["visible_controls"][0]["rect"]["x"] = 1270
        self.capture["capture_review"]["controls_sha256"] = visible_controls_digest(self.capture["visible_controls"])
        self.reject("offscreen/clipped")

    def test_renderer_icon_capture_still_needs_the_existing_source_visual_review(self):
        self.icon_inputs()
        self.plan["screenshot_reviews"]["draft-screen"]["no_errors"] = False
        self.reject("genuine visual review")

    def test_authored_control_cannot_be_omitted_from_mapping(self):
        self.plan["scenes"][0]["captions"][0]["required_labels"] = ["Draft"]
        self.reject("unmatched authored UI controls")

    def test_narrative_only_flag_cannot_bypass_operational_controls(self):
        self.plan["scenes"][0]["captions"][0].update(instructional=False, required_labels=[])
        self.reject("unmatched authored UI controls")

    def test_control_must_be_named_in_actual_speech_cue(self):
        self.capture["visible_labels"].append("Finalize")
        self.plan["scenes"][0]["captions"][0]["required_labels"].append("Finalize")
        self.reject("speech cue does not name")

    def test_wrong_screenshot_hash_is_rejected(self):
        self.capture["sha256"] = "0" * 64
        self.reject("hash mismatch")

    def test_missing_hash_is_rejected(self):
        del self.capture["sha256"]
        self.reject("record the asset's SHA-256")

    def test_present_dom_provenance_must_exist_and_match(self):
        self.capture.update(dom_file="capture.dom.txt", dom_sha256="0" * 64)
        self.reject("missing or empty asset")
        (self.root / "capture.dom.txt").write_text("synthetic DOM")
        self.reject("hash mismatch")

    def test_missing_image_is_rejected(self):
        (self.root / "capture.png").unlink()
        self.reject("missing or empty asset")

    def test_wrong_image_dimensions_are_rejected(self):
        self.capture["width"] = 1920
        self.reject("header dimensions")

    def test_full_page_inset_and_portrait_are_rejected(self):
        for dimensions in [(1280, 5000), (390, 844), (3840, 2160)]:
            with self.subTest(dimensions=dimensions), self.assertRaises(renderer.AssemblyError):
                renderer.layout(*dimensions)

    def test_screenshot_hash_bound_visual_review_is_required(self):
        self.plan["screenshot_reviews"]["draft-screen"]["sha256"] = "0" * 64
        self.reject("review must be tied")

    def test_failed_visual_review_is_rejected(self):
        for flag in ("application_visible", "labels_legible", "no_errors"):
            with self.subTest(flag=flag):
                self.plan["screenshot_reviews"]["draft-screen"][flag] = False
                self.reject("genuine visual review")
                self.plan["screenshot_reviews"]["draft-screen"][flag] = True

    def test_excluded_capture_is_rejected(self):
        self.capture["eligible_for_lesson"] = False
        self.reject("capture is excluded/blocked")

    def test_error_or_missing_labels_capture_is_rejected(self):
        self.capture["state"] = "blocked_auth"
        self.reject("capture is excluded/blocked")
        self.capture["state"] = "observed"
        self.capture["missing_required_labels"] = ["Save draft"]
        self.reject("reports missing required controls")

    def test_missing_browser_provenance_is_rejected(self):
        self.capture["provenance"]["method"] = "illustration_export"
        self.reject("actual browser capture")

    def test_credential_url_is_rejected(self):
        self.capture["provenance"]["url"] += "?access_" + "token=synthetic-only"
        self.reject("redact credential-bearing")

    def test_no_estimated_or_robotic_fallback_narration(self):
        self.plan["narration"]["kind"] = "robotic_fallback"
        self.reject("approved local natural narration")

    def test_missing_narration_never_creates_a_fallback(self):
        (self.root / "voice.wav").unlink()
        self.reject("missing or empty asset 'voice.wav'")
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ["capture.png", "lesson.json", "manifest.json", "plan.json", "voice.srt"])

    def test_changed_caption_asset_requires_new_review(self):
        (self.root / "voice.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nDifferent speech.\n")
        self.reject("hash mismatch")

    def test_missing_voice_approval_is_rejected(self):
        self.plan["narration"]["approval"]["complete_natural_narration"] = False
        self.reject("review the full audio")

    def test_captions_must_be_reviewed_against_same_audio(self):
        self.plan["captions"]["approval"]["audio_sha256"] = "0" * 64
        self.reject("exact audio")

    def test_unspoken_or_unrendered_words_are_rejected(self):
        self.lesson["scenes"][0]["narration"] += " Then finalize it."
        self.reject("complete spoken transcript")

    def test_source_punctuation_differences_are_permitted(self):
        self.lesson["scenes"][0]["narration"] = "Select ‘Save draft’ to keep Draft!"
        self.validate()

    def test_scene_coverage_gap_is_rejected(self):
        self.plan["scenes"][0]["start"] = 0.1
        self.plan["scenes"][0]["screens"][0]["start"] = 0.1
        self.reject("speech cue extends outside")

    def test_screen_coverage_gap_is_rejected(self):
        self.plan["scenes"][0]["screens"][0]["start"] = 0.1
        self.reject("gap/overlap")

    def test_screen_coverage_overlap_is_rejected(self):
        self.plan["scenes"][0]["screens"] = [{"screenshot_id": "draft-screen", "start": 0, "end": 0.8}, {"screenshot_id": "draft-screen", "start": 0.7, "end": 1}]
        self.reject("gap/overlap")

    def test_caption_cannot_cross_screen_cut(self):
        self.plan["scenes"][0]["screens"] = [{"screenshot_id": "draft-screen", "start": 0, "end": 0.5}, {"screenshot_id": "draft-screen", "start": 0.5, "end": 1}]
        self.reject("entire speech cue")

    def test_all_authored_scenes_must_be_present(self):
        self.lesson["scenes"].append(copy.deepcopy(self.lesson["scenes"][0]))
        self.reject("map every authored scene")

    def test_duplicate_speech_mapping_is_rejected(self):
        self.plan["scenes"][0]["captions"] *= 2
        self.reject("each speech cue must map exactly once")

    def test_missing_speech_mapping_is_rejected(self):
        self.plan["scenes"][0]["captions"] = []
        self.reject("nonempty list")

    def test_asset_path_escape_is_rejected(self):
        self.plan["narration"]["file"] = "../outside.wav"
        self.reject("path inside asset_root")

    def test_actual_audio_must_not_be_truncated_or_have_estimated_tail(self):
        renderer.check_audio_duration(1.0, 1.0)
        renderer.check_audio_duration(1.0, 1.02)
        for planned in (0.99, 1.1):
            with self.subTest(planned=planned), self.assertRaises(renderer.AssemblyError):
                renderer.check_audio_duration(1.0, planned)

    def test_does_not_replace_existing_output(self):
        self.save(); destination = self.root / "existing"; destination.mkdir()
        marker = destination / "human-work.txt"; marker.write_text("retain")
        with self.assertRaisesRegex(renderer.AssemblyError, "already exists"):
            renderer.render(self.lesson_path, self.plan_path, self.root, destination)
        self.assertEqual(marker.read_text(), "retain")

    def test_timeline_preserves_supplied_speech_boundaries(self):
        recipe = self.validate()
        self.assertEqual([(e["start"], e["end"]) for e in renderer.timeline(recipe)], [(0, 1)])

    def test_overlong_captions_fail_without_shrinking_application(self):
        class SyntheticDraw:
            def textbbox(self, origin, value, font):
                return 0, 0, len(value) * 10, 30
        with self.assertRaisesRegex(renderer.AssemblyError, "three readable lines"):
            renderer.caption_wrap(SyntheticDraw(), "word " * 20, None, 50)

    def test_malformed_srt_blocks_are_not_silently_discarded(self):
        p = self.root / "bad.srt"; p.write_text("Unrendered speech outside a cue.\n\n1\n00:00:00,000 --> 00:00:01,000\nSelect Save draft.\n")
        with self.assertRaisesRegex(renderer.AssemblyError, "sequential SRT"):
            renderer.load_cues(p)

    def test_overlapping_captions_are_rejected(self):
        p = self.root / "bad.srt"; p.write_text("1\n00:00:00,000 --> 00:00:01,000\nSelect\n\n2\n00:00:00,500 --> 00:00:01,500\nSave draft.\n")
        with self.assertRaisesRegex(renderer.AssemblyError, "overlapping"):
            renderer.load_cues(p)

    def test_complete_two_scene_transcript_and_timeline(self):
        (self.root / "voice.srt").write_text("1\n00:00:00,000 --> 00:00:00,500\nSelect Save draft.\n\n2\n00:00:00,500 --> 00:00:01,000\nKeep Draft.\n")
        self.plan["captions"]["sha256"] = renderer._hash(self.root / "voice.srt")
        self.plan["captions"]["approval"]["sha256"] = self.plan["captions"]["sha256"]
        self.lesson["scenes"] = [{"id": "save", "title": "Save", "required_labels": ["Save draft"], "narration": "Select Save draft."}, {"id": "keep", "title": "Keep", "required_labels": ["Draft"], "narration": "Keep Draft."}]
        self.plan["scenes"] = [{"id": "save", "start": 0, "end": 0.5, "screens": [{"screenshot_id": "draft-screen", "start": 0, "end": 0.5}], "captions": [{"cue": 1, "screenshot_id": "draft-screen", "required_labels": ["Save draft"]}]}, {"id": "keep", "start": 0.5, "end": 1, "screens": [{"screenshot_id": "draft-screen", "start": 0.5, "end": 1}], "captions": [{"cue": 2, "screenshot_id": "draft-screen", "required_labels": ["Draft"]}]}]
        recipe = self.validate()
        self.assertEqual([(e["start"], e["end"]) for e in renderer.timeline(recipe)], [(0, 0.5), (0.5, 1)])

    @unittest.skipUnless(os.environ.get("WALKTHROUGH_TEST_FFMPEG"), "optional actual FFmpeg/Pillow fixture; set WALKTHROUGH_TEST_FFMPEG")
    def test_optional_real_render_decode_and_pending_publication_gate(self):
        self.save(); output = self.root / "rendered"
        result = renderer.render(self.lesson_path, self.plan_path, self.root, output, ffmpeg=os.environ["WALKTHROUGH_TEST_FFMPEG"])
        self.assertFalse(result["publishable"])
        self.assertEqual(result["full_decode"], "passed")
        self.assertEqual(result["actual_media"]["video_codec"], "h264")
        self.assertEqual(result["actual_media"]["audio_codec"], "aac")
        self.assertEqual(result["actual_media"]["decoded_video_frames"], 30)
        self.assertEqual(result["browser_playback"], {"status": "pending", "proof": []})
        self.assertEqual(renderer._hash(self.root / "capture.png"), self.capture["sha256"])
        self.assertEqual((output / "synthetic-draft.srt").read_bytes(), (self.root / "voice.srt").read_bytes())
        self.assertEqual(renderer._image_dimensions(output / "synthetic-draft.jpg"), (1920, 1080))
        report = verify(output / "evidence.pending.json", self.root)
        self.assertFalse(report["passed"])
        self.assertTrue(any("browser_playback" in issue for issue in report["issues"]))
        self.assertTrue(any("application_visible" in issue for issue in report["issues"]))

    @unittest.skipUnless(os.environ.get("WALKTHROUGH_TEST_FFMPEG"), "optional actual two-screen FFmpeg/Pillow fixture")
    def test_optional_actual_frames_change_at_explicit_screen_cut(self):
        from PIL import Image
        self.test_complete_two_scene_transcript_and_timeline()
        (self.root / "second.png").write_bytes(png(color=b"\x58\x28\x24"))
        second = copy.deepcopy(self.capture)
        second.update(id="second-screen", file="second.png", sha256=renderer._hash(self.root / "second.png"))
        self.additional_captures.append(second)
        self.plan["screenshot_reviews"]["second-screen"] = self.approval(second["sha256"], application_visible=True, labels_legible=True, no_errors=True)
        self.plan["scenes"][1]["screens"][0]["screenshot_id"] = "second-screen"
        self.plan["scenes"][1]["captions"][0]["screenshot_id"] = "second-screen"
        self.save(); output = self.root / "two-screen-output"
        result = renderer.render(self.lesson_path, self.plan_path, self.root, output, ffmpeg=os.environ["WALKTHROUGH_TEST_FFMPEG"])
        frames = result["rendered_segments"]
        self.assertEqual(len(frames), 2)
        for frame, expected in zip(frames, [(36, 64, 88), (88, 40, 36)]):
            with Image.open(self.root / frame["frame"]["file"]) as image:
                pixel = image.convert("RGB").getpixel((960, 540))
            self.assertTrue(all(abs(a - b) <= 6 for a, b in zip(pixel, expected)), (pixel, expected))
        self.assertFalse(result["publishable"])


if __name__ == "__main__":
    unittest.main()
