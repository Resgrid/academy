"""Synthetic receipt/parser fixtures are not genuine User or app evidence."""
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'sources/production' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


MARKERS = module('dispatch_genuine_marker_proposal', 'resolve_dispatch_reference_service_markers_20261030.py')
RECIPE = module('records_source_authoring_recipe', 'prepare_core_records_authoring_recipe_20261030.py')


class DispatchMarkerTests(unittest.TestCase):
    def test_genuine_inputs_preserve_seven_original_boundary_ambiguities(self):
        proposal, _ = MARKERS.prepare()
        self.assertEqual(proposal['original_exact_boundaries_resolved'], 1)
        self.assertEqual(proposal['original_exact_boundaries_still_ambiguous'], 7)
        self.assertEqual([row['proposed_editorial_alternative']['service_marker_seconds'] for row in proposal['decisions']], [36, 42, 52, 146, 176, 180, 184, 193])
        self.assertFalse(proposal['captions_split_or_changed'])
        self.assertTrue(proposal['parent_review_pending'])

    def test_synthetic_marker_group_retains_words_without_subsecond_estimates(self):
        anchors, words = MARKERS.anchors('[00:00:00] Choose [00:00:01] Hide All and inspect [00:00:02] the switch.')
        self.assertEqual(anchors[1]['following_word_group'], 'Hide All and inspect')
        self.assertEqual(anchors[2]['word_offset'], 5)
        self.assertEqual(words, 'Choose Hide All and inspect the switch.'.split())


class RecordsApprovalGuards(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 30, tzinfo=timezone.utc)
        self.earliest = '2026-10-29T00:00:00Z'
        self.record = {'reviewer': 'User', 'reviewed_at': '2026-10-29T01:00:00Z',
            'lesson_sha256': RECIPE.SOURCE_SHA, 'audio_sha256': RECIPE.AUDIO_SHA,
            'complete_natural_narration': True,
            'evidence': 'Synthetic parser fixture: full narration natural and complete; not an actual User review.'}

    def test_synthetic_valid_receipt_schema_does_not_write_or_author(self):
        self.assertIs(RECIPE.validate_receipt(self.record, 'listening', self.earliest, self.now), self.record)

    def test_agent_qa_cannot_replace_user_listening(self):
        self.record['reviewer'] = 'Codex'
        with self.assertRaises(ValueError):
            RECIPE.validate_receipt(self.record, 'listening', self.earliest, self.now)

    def test_wrong_bound_source_or_audio_rejected(self):
        for key in ['lesson_sha256', 'audio_sha256']:
            with self.subTest(key=key), self.assertRaises(ValueError):
                RECIPE.validate_receipt({**self.record, key: '0' * 64}, 'listening', self.earliest, self.now)

    def test_url_or_unapproved_complete_state_rejected(self):
        for extra in [{'optional_note': 'https://example.invalid/review'}, {'complete_natural_narration': False}]:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                RECIPE.validate_receipt({**self.record, **extra}, 'listening', self.earliest, self.now)

    def test_future_naive_or_pre_qa_dates_rejected(self):
        for stamp in ['2026-10-31T00:00:00Z', '2026-10-29T01:00:00', '2026-10-28T23:59:59Z']:
            with self.subTest(stamp=stamp), self.assertRaises(ValueError):
                RECIPE.validate_receipt({**self.record, 'reviewed_at': stamp}, 'listening', self.earliest, self.now)

    def test_parent_review_requires_the_exact_complete_mapping_and_scope(self):
        parent = {**self.record, 'reviewer': 'Codex /root', 'correspondence_sha256': RECIPE.PROPOSAL_SHA,
            'compact_sha256': RECIPE.COMPACT_SHA, 'complete_cue_correspondence_reviewed': True,
            'screen_holds_and_required_controls_reviewed': True, 'cues': 112,
            'accepted_spans': 20, 'continuous_holds': 17, 'source_images': 16}
        self.assertIs(RECIPE.validate_receipt(parent, 'parent', self.earliest, self.now), parent)
        for changed in [{'cues': 111}, {'correspondence_sha256': '0' * 64}, {'complete_cue_correspondence_reviewed': False}]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                RECIPE.validate_receipt({**parent, **changed}, 'parent', self.earliest, self.now)


if __name__ == '__main__':
    unittest.main()
