"""Synthetic evidence-contract tests; no browser, ffmpeg or image library needed."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_capture_evidence import main, verify, verify_document, visible_controls_digest, instruction_scene_digest


def png(width=320, height=180):
    """A valid, visibly synthetic PNG. Passing metadata is not a visual review."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    rows = (b"\x00" + b"\x12\x34\x56" * width) * height
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


class CaptureEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.caption = "Select Save draft to keep this incident record as a Draft."
        self.data = self.fixture()

    def asset(self, filename, content, image=False):
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        asset = {"file": filename, "sha256": hashlib.sha256(content).hexdigest()}
        if image:
            asset.update(width=320, height=180)
        return asset

    def fixture(self):
        video = self.asset("media/incident-draft.mp4", b"synthetic video identity; validator does not decode media")
        video.update(duration_seconds=30, width=320, height=180, assembled_at="2026-10-25T12:00:00Z")
        video["captions"] = self.asset("media/incident-draft.vtt", f"WEBVTT\n\n00:00.000 --> 00:30.000\n{self.caption}\n".encode())
        screenshot = self.asset("captures/draft.png", png(), image=True)
        screenshot.update(id="draft", app="Core", kind="application_screenshot", provenance={"method": "browser_screenshot", "url": "http://localhost:5000/User/Records/Edit/123", "captured_at": "2026-10-25T11:59:00Z"}, visible_labels=["Incident record", "Draft", "Save draft"])
        scene = {"id": "save", "kind": "operational", "start": 0, "end": 30, "screens": [{"screenshot_id": "draft", "start": 0, "end": 30}], "captions": [{"start": 0, "end": 30, "text": self.caption, "screenshot_id": "draft", "required_labels": ["Save draft", "Draft"]}]}
        frame = self.asset("proof/frame.png", png(), image=True)
        frame.update(time=15, video_sha256=video["sha256"], application_visible=True, visible_labels=["Save draft", "Draft"], caption_text=self.caption)
        playback = []
        for position, time in [("beginning", 2), ("middle", 15), ("end", 28)]:
            playback.append({"position": position, "video_sha256": video["sha256"], "url": "http://localhost:8000/lessons/incident-draft", "current_src": "http://localhost:8000/media/incident-draft.mp4", "captured_at": "2026-10-25T12:01:00+00:00", "previous_time": time - 0.5, "current_time": time, "duration_seconds": 30, "video_width": 320, "video_height": 180, "ready_state": 4, "network_state": 1, "paused": False, "ended": False, "media_error": None, "console_errors": [], "captions": {"mode": "showing", "text": self.caption}, "screenshot": self.asset(f"proof/{position}.png", png(), image=True)})
        return {"schema_version": 1, "lesson_id": "incident-draft", "video": video, "screenshots": [screenshot], "scenes": [scene], "rendered_segments": [{"scene_id": "save", "screenshot_id": "draft", "start": 0, "end": 30, "frame": frame}], "browser_playback": playback}

    def check(self, data=None):
        return verify_document(self.data if data is None else data, self.root)

    def assert_rejected(self, text, data=None):
        report = self.check(data)
        self.assertFalse(report["passed"], report)
        self.assertTrue(any(text in issue for issue in report["issues"]), report)

    def icon_fixture(self):
        self.caption = "Select Attach, then Send."
        self.data = self.fixture()
        shot = self.data["screenshots"][0]
        shot["visible_labels"] = ["Chat"]
        shot["visible_controls"] = [
            {"accessible_name": name, "role": "button", "rect": {"x": x, "y": 130, "width": 24, "height": 24}, "icon_only": True, "provenance": "browser_dom"}
            for name, x in [("Attach", 220), ("Send", 260)]
        ]
        def review(item, observations, **extra):
            return {"passed": True, "reviewer": "synthetic contract fixture, no actual visual review",
                    "reviewed_at": "2026-10-25T12:01:00Z", "sha256": item["sha256"],
                    "controls_sha256": visible_controls_digest(observations),
                    "application_visible": True, "no_errors": True, "controls_reviewed": True,
                    "controls_fully_visible": True, "controls_unobstructed": True, **extra}
        shot["capture_review"] = review(shot, shot["visible_controls"])
        self.data["scenes"][0]["captions"][0]["required_labels"] = ["Attach", "Send"]
        frame = self.data["rendered_segments"][0]["frame"]
        frame["visible_labels"] = ["Chat"]
        frame["reviewed_control_names"] = ["Attach", "Send"]
        frame["control_review"] = review(frame, frame["reviewed_control_names"], video_sha256=self.data["video"]["sha256"], source_screenshot_sha256=shot["sha256"])
        return shot, frame

    def test_reviewed_icon_only_send_and_attach_are_distinct_from_literal_labels(self):
        shot, frame = self.icon_fixture()
        self.assertTrue(self.check()["passed"], self.check())
        self.assertEqual(shot["visible_labels"], ["Chat"])
        self.assertEqual(frame["visible_labels"], ["Chat"])
        shot["visible_labels"] = []
        frame["visible_labels"] = []
        self.assertTrue(self.check()["passed"], self.check())

    def test_invented_or_changed_control_observations_invalidate_the_image_review(self):
        shot, _ = self.icon_fixture()
        shot["visible_controls"][0]["accessible_name"] = "Invented action"
        self.assert_rejected("review must bind these exact ordered control observations")
        self.assert_rejected("required visible control/label")

    def test_icon_control_needs_specific_accessible_name_role_and_browser_provenance(self):
        for change in [{"accessible_name": ""}, {"accessible_name": "Button 12"}, {"accessible_name": "?"},
                       {"role": "img"}, {"role": []}, {"provenance": None}, {"icon_only": 1}]:
            with self.subTest(change=change):
                shot, _ = self.icon_fixture()
                shot["visible_controls"][0].update(change)
                shot["capture_review"]["controls_sha256"] = visible_controls_digest(shot["visible_controls"])
                self.assertFalse(self.check()["passed"], self.check())

    def test_offscreen_clipped_zero_size_and_malformed_control_rects_fail(self):
        for rect in [None, [], {}, {"x": -1, "y": 1, "width": 20, "height": 20},
                     {"x": 300, "y": 1, "width": 21, "height": 20},
                     {"x": 10, "y": 170, "width": 20, "height": 20},
                     {"x": 10, "y": 1, "width": 0, "height": 20},
                     {"x": 10, "y": 1, "width": True, "height": 20},
                     {"x": "10", "y": 1, "width": 20, "height": 20}]:
            with self.subTest(rect=rect):
                shot, _ = self.icon_fixture()
                shot["visible_controls"][0]["rect"] = rect
                shot["capture_review"]["controls_sha256"] = visible_controls_digest(shot["visible_controls"])
                self.assert_rejected(".rect")
        for flag in [{"clipped": True}, {"occluded": True}, {"fully_visible": False}]:
            with self.subTest(flag=flag):
                shot, _ = self.icon_fixture()
                shot["visible_controls"][0].update(flag)
                shot["capture_review"]["controls_sha256"] = visible_controls_digest(shot["visible_controls"])
                self.assert_rejected("clipped or occluded")

    def test_nonfinite_rect_is_rejected_without_crashing(self):
        shot, _ = self.icon_fixture()
        shot["visible_controls"][0]["rect"]["x"] = float("nan")
        self.assert_rejected(".rect")

    def test_icon_image_review_is_required_hash_bound_unobstructed_and_after_capture(self):
        for field, value in [("passed", False), ("sha256", "0" * 64), ("controls_sha256", "0" * 64),
                             ("controls_reviewed", False), ("controls_fully_visible", False),
                             ("controls_unobstructed", False), ("no_errors", False),
                             ("reviewed_at", "2026-10-25T10:00:00Z"), ("reviewed_at", "2999-01-01T00:00:00Z")]:
            with self.subTest(field=field, value=value):
                shot, _ = self.icon_fixture()
                shot["capture_review"][field] = value
                self.assertFalse(self.check()["passed"], self.check())
        shot, _ = self.icon_fixture()
        shot.pop("capture_review")
        self.assert_rejected("capture_review")

    def test_blocked_rejected_or_unreviewed_images_cannot_supply_icon_evidence(self):
        for change in [{"state": "blocked_extension"}, {"state": "loading"}, {"accepted": False},
                       {"eligible_for_lesson": False}, {"contains_private_ui": True}, {"review_status": "pending_visual_review"}]:
            with self.subTest(change=change):
                shot, _ = self.icon_fixture()
                shot.update(change)
                self.assert_rejected("not operational evidence")

    def test_icon_source_hash_and_playback_gates_still_apply(self):
        shot, _ = self.icon_fixture()
        shot["sha256"] = "0" * 64
        shot["capture_review"]["sha256"] = shot["sha256"]
        self.assert_rejected("hash mismatch")
        self.icon_fixture()
        self.data["browser_playback"].pop()
        self.assert_rejected("exactly one end")

    def test_rendered_icons_require_separate_frame_review_and_source_binding(self):
        for field, value in [("sha256", "0" * 64), ("controls_sha256", "0" * 64),
                             ("source_screenshot_sha256", "0" * 64), ("video_sha256", "0" * 64),
                             ("controls_unobstructed", False)]:
            with self.subTest(field=field):
                _, frame = self.icon_fixture()
                frame["control_review"][field] = value
                self.assertFalse(self.check()["passed"], self.check())
        _, frame = self.icon_fixture()
        frame.pop("control_review")
        self.assert_rejected("control_review")
        _, frame = self.icon_fixture()
        frame["reviewed_control_names"].append("Invented action")
        frame["control_review"]["controls_sha256"] = visible_controls_digest(frame["reviewed_control_names"])
        self.assert_rejected("must reference validated DOM controls")

    def test_legitimate_incident_record_draft_label_is_accepted(self):
        self.assertEqual(self.check(), {"passed": True, "lesson_id": "incident-draft", "issues": []})

    def receiver_evidence(self):
        self.data['primary_app'] = 'Core'
        self.data['supporting_applications'] = [{'app': 'Mailpit', 'for_app': 'Core', 'role': 'controlled_local_receiver', 'purpose': 'Inspect local SMTP receipts.'}]
        receiver = dict(self.data['screenshots'][0], id='receipt', app='Mailpit', visible_labels=['Mailpit'],
                        provenance=dict(self.data['screenshots'][0]['provenance'], url='http://127.0.0.1:18126/'))
        self.data['screenshots'].append(receiver)
        return receiver

    def test_local_receiver_identity_needs_explicit_context_and_keeps_hash_playback_gates(self):
        receiver = self.receiver_evidence()
        self.assertTrue(self.check()['passed'])
        self.data['supporting_applications'] = []
        self.assert_rejected('explicitly declared')
        self.data['supporting_applications'] = [{'app': 'Mailpit', 'for_app': 'Core', 'role': 'controlled_local_receiver', 'purpose': 'Inspect local SMTP receipts.'}]
        receiver['provenance']['url'] = 'https://mailpit.example/'
        self.assert_rejected('loopback local receiver')
        receiver['provenance']['url'] = 'http://127.0.0.1:18126/'
        self.data['browser_playback'] = []
        self.assert_rejected('browser_playback')

    def test_receiver_cannot_be_an_unknown_app_or_supply_primary_config_controls(self):
        receiver = self.receiver_evidence()
        receiver['app'] = 'Invented receiver'
        self.assert_rejected('explicitly declared')
        self.data['screenshots'] = self.data['screenshots'][:1]
        self.data['screenshots'][0]['app'] = 'Mailpit'
        scene = self.data['scenes'][0]
        scene['visual_required_labels'] = ['Save draft', 'Draft']
        self.review_instructions()
        self.assert_rejected('supporting receiver images cannot supply Resgrid configuration controls')

    def review_instructions(self):
        scene = self.data['scenes'][0]
        scene['instruction_review'] = {'passed': True, 'reviewer': 'synthetic contract fixture',
            'reviewed_at': '2026-10-25T12:01:00Z', 'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(scene, {shot['id']: shot for shot in self.data['screenshots']})}

    def test_reviewed_scene_coverage_preserves_context_labels_without_requiring_recital(self):
        self.data['screenshots'][0]['visible_labels'].append('Department Settings')
        self.data['scenes'][0]['visual_required_labels'] = ['Save draft', 'Draft', 'Department Settings']
        self.review_instructions()
        self.assertTrue(self.check()['passed'], self.check())

    def test_natural_spoken_reference_requires_review_and_an_actual_phrase_and_control(self):
        self.caption = 'Use the save control to keep this incident record as a Draft.'
        self.data = self.fixture()
        scene = self.data['scenes'][0]
        scene['visual_required_labels'] = ['Save draft', 'Draft']
        scene['captions'][0]['spoken_references'] = {'Save draft': 'save control'}
        self.review_instructions()
        self.assertTrue(self.check()['passed'], self.check())
        scene['captions'][0]['spoken_references']['Save draft'] = 'invented spoken phrase'
        self.review_instructions()
        self.assert_rejected('exact phrase from this speech cue')

    def test_scene_correspondence_review_is_current_and_cannot_approve_unseen_controls(self):
        scene = self.data['scenes'][0]
        scene['visual_required_labels'] = ['Save draft', 'Draft']
        self.review_instructions()
        scene['screens'][0]['end'] = 29
        self.assert_rejected('review must bind the exact current scene')
        scene['screens'][0]['end'] = 30
        scene['visual_required_labels'].append('Unseen control')
        self.review_instructions()
        self.assert_rejected('every required scene label must be visible')
        scene['visual_required_labels'].remove('Unseen control')
        self.review_instructions()
        scene.pop('instruction_review')
        self.assert_rejected('instruction_review')

    def test_all_five_application_sources_are_supported(self):
        for app in ("Core", "Dispatch", "Responder", "Unit", "IC"):
            with self.subTest(app=app):
                self.data["screenshots"][0]["app"] = app
                self.assertTrue(self.check()["passed"])

    def test_illustrated_substitute_is_rejected_even_with_valid_image_hash(self):
        self.data["screenshots"][0]["kind"] = "illustrated_slide"
        self.data["screenshots"][0]["provenance"]["method"] = "image_generation"
        self.assert_rejected("illustrated substitute")

    def test_illustrated_only_scene_cannot_replace_operational_screens(self):
        self.data["scenes"][0]["kind"] = "illustration"
        self.data["scenes"][0]["screens"] = []
        self.assert_rejected("every scene needs actual application screens")

    def test_svg_cannot_masquerade_as_a_screenshot(self):
        image = self.asset("captures/illustration.svg", b'<svg width="320" height="180"/>', image=True)
        self.data["screenshots"][0].update(image)
        self.assert_rejected("expected a PNG or JPEG")

    def test_wrong_and_missing_screenshot_hashes_fail(self):
        for digest in ("0" * 64, None, ""):
            with self.subTest(digest=digest):
                self.data["screenshots"][0]["sha256"] = digest
                self.assert_rejected("screenshots[0].sha256")

    def test_missing_screenshot_file_fails(self):
        (self.root / "captures/draft.png").unlink()
        self.assert_rejected("asset is missing")

    def test_missing_required_visible_control_fails(self):
        self.data["screenshots"][0]["visible_labels"] = ["Incident record", "Draft"]
        self.assert_rejected("required visible control/label")

    def test_caption_cannot_invent_a_control_not_named_in_its_text(self):
        self.data["scenes"][0]["captions"][0]["required_labels"].append("Incident record")
        self.data["rendered_segments"][0]["frame"]["visible_labels"].append("Incident record")
        # Normalized case-insensitive matching permits the legitimate phrase.
        self.assertTrue(self.check()["passed"])
        self.data["screenshots"][0]["visible_labels"].append("Finalize")
        self.data["scenes"][0]["captions"][0]["required_labels"].append("Finalize")
        self.assert_rejected("caption must name its required visible label")

    def test_scene_timeline_coverage_gap_is_rejected(self):
        self.data["scenes"][0]["start"] = 1
        self.assert_rejected("coverage gap from 0s to 1s")

    def test_screen_timeline_coverage_gap_is_rejected(self):
        self.data["scenes"][0]["screens"][0]["end"] = 29
        self.assert_rejected("coverage gap from 29s to 30s")

    def test_overlapping_scene_coverage_is_rejected(self):
        second = copy.deepcopy(self.data["scenes"][0])
        second["id"] = "duplicate-operation"
        self.data["scenes"].append(second)
        self.assert_rejected("overlapping coverage")

    def test_each_display_interval_needs_a_rendered_frame(self):
        self.data["rendered_segments"] = []
        self.assert_rejected("needs exactly one rendered segment")

    def test_rendered_frame_must_show_application_and_required_labels(self):
        frame = self.data["rendered_segments"][0]["frame"]
        frame["application_visible"] = False
        frame["visible_labels"] = ["Draft"]
        self.assert_rejected("real application is visible")
        self.assert_rejected("required caption controls/labels")

    def test_rendered_frame_hash_and_video_binding_are_checked(self):
        frame = self.data["rendered_segments"][0]["frame"]
        frame["sha256"] = "0" * 64
        frame["video_sha256"] = "1" * 64
        self.assert_rejected("hash mismatch")
        self.assert_rejected("current assembled video's hash")

    def test_video_reassembly_invalidates_stale_playback_proof(self):
        old_hash = self.data["video"]["sha256"]
        video = self.asset("media/incident-draft.mp4", b"new assembled video")
        self.data["video"].update(video)
        self.data["rendered_segments"][0]["frame"]["video_sha256"] = video["sha256"]
        self.assertNotEqual(old_hash, video["sha256"])
        self.assert_rejected("stale-video playback proof")

    def test_old_playback_timestamp_is_rejected_even_when_hash_matches(self):
        self.data["browser_playback"][0]["captured_at"] = "2026-10-25T11:00:00Z"
        self.assert_rejected("predates assembly")

    def test_beginning_middle_and_end_are_all_required(self):
        self.data["browser_playback"].pop()
        self.assert_rejected("exactly one end")

    def test_playback_sample_must_be_in_its_actual_position_band(self):
        self.data["browser_playback"][1]["current_time"] = 3
        self.data["browser_playback"][1]["previous_time"] = 2
        self.assert_rejected("percentage band")

    def test_playback_must_advance_be_ready_and_have_no_errors(self):
        for change, message in [({"previous_time": 2}, "forward playback progress"), ({"ready_state": 1}, "readyState must be 3 or 4"), ({"network_state": 3}, "networkState must be IDLE"), ({"paused": True}, "advancing playback"), ({"video_width": 0}, "zero dimensions"), ({"media_error": {"code": 4}}, "media_error=null"), ({"console_errors": ["failed to load media"]}, "console_errors=[]")]:
            with self.subTest(change=change):
                data = copy.deepcopy(self.data)
                data["browser_playback"][0].update(change)
                self.assert_rejected(message, data)

    def test_playback_requires_visible_matching_captions(self):
        self.data["browser_playback"][1]["captions"]["mode"] = "hidden"
        self.assert_rejected("captions must be showing")
        self.data["browser_playback"][1]["captions"] = {"mode": "showing", "text": "Unrelated caption"}
        self.assert_rejected("does not match the mapped caption")

    def test_caption_asset_must_match_scene_mappings(self):
        self.data["video"]["captions"] = self.asset("media/incident-draft.vtt", b"WEBVTT\n\n00:00.000 --> 00:30.000\nA different instruction.\n")
        self.assert_rejected("does not match a cue in the hashed VTT/SRT")

    def test_srt_is_supported(self):
        self.data["video"]["captions"] = self.asset("media/incident-draft.srt", f"1\n00:00:00,000 --> 00:00:30,000\n{self.caption}\n".encode())
        self.assertTrue(self.check()["passed"])

    def test_context_commentary_can_explicitly_omit_control_labels(self):
        self.data["scenes"][0]["kind"] = "context"
        cue = self.data["scenes"][0]["captions"][0]
        cue.update(instructional=False, required_labels=[])
        self.assertTrue(self.check()["passed"])

    def test_operational_scene_cannot_declare_all_captions_noninstructional(self):
        cue = self.data["scenes"][0]["captions"][0]
        cue.update(instructional=False, required_labels=[])
        self.assert_rejected("at least one instructional caption")

    def test_missing_provenance_and_non_application_source_are_rejected(self):
        self.data["screenshots"][0]["app"] = "Illustrator"
        self.data["screenshots"][0]["provenance"] = {}
        self.assert_rejected("must be Core, Dispatch, Responder, Unit or IC")
        self.assert_rejected("actual http(s) browser URL")
        self.assert_rejected("timestamp with timezone")

    def test_actual_image_dimensions_are_checked(self):
        self.data["screenshots"][0]["width"] = 640
        self.assert_rejected("differ from asset header")

    def test_asset_paths_cannot_escape_the_evidence_root(self):
        self.data["screenshots"][0]["file"] = "../outside.png"
        self.assert_rejected("inside asset_root")

    def test_nonfinite_or_boolean_timing_is_rejected(self):
        for duration in (float("nan"), float("inf"), True, -1):
            with self.subTest(duration=duration):
                self.data["video"]["duration_seconds"] = duration
                self.assert_rejected("positive finite number")

    def test_missing_or_malformed_evidence_is_actionable(self):
        missing = verify(self.root / "missing.json")
        self.assertFalse(missing["passed"])
        bad = self.root / "bad.json"
        bad.write_text("{broken")
        self.assertIn("cannot read", verify(bad)["issues"][0])
        self.assertFalse(verify_document([], self.root)["passed"])

    def test_malformed_references_and_source_types_fail_without_crashing(self):
        for target, key in [("screenshots", "app"), ("scenes", "kind"), ("rendered_segments", "scene_id"), ("rendered_segments", "screenshot_id"), ("browser_playback", "position")]:
            with self.subTest(target=target, key=key):
                data = copy.deepcopy(self.data)
                data[target][0][key] = ["not a string"]
                self.assertFalse(self.check(data)["passed"])

    def test_cli_and_default_asset_root(self):
        path = self.root / "lesson.json"
        path.write_text(json.dumps(self.data))
        self.assertTrue(verify(path)["passed"])
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main([str(path)]), 0)
        self.assertTrue(json.loads(output.getvalue())["passed"])


if __name__ == "__main__":
    unittest.main()
