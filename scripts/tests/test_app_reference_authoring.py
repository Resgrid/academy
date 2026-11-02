"""Targeted source/approval guards; synthetic fixtures are not review evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'sources/production' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


PREP = module('reference_prep_guards', 'prepare_app_reference_cues_20261030.py')
AUTHOR = module('reference_author_guards', 'author_app_reference_take_01_20261030.py')
PROJECTION = module('reference_projection_guards', 'propose_ic_access_public_labels_20261030.py')
TIMING = 'c438f5f44138417c3f1faf5b63d49fa37c031fdc96dac723b2a1bc616ca2e254'


def synthetic_cue(start, end, text, word_start, word_end, image):
    return {'start': start, 'end': end, 'text': text, 'word_start': word_start,
        'word_end': word_end, 'screenshot_id': image, 'scene_id': 'synthetic', 'raw_cues': [1]}


class ReferenceAuthoringGuards(unittest.TestCase):
    def test_caption_merge_retains_real_endpoints_same_image_and_words(self):
        before = [synthetic_cue(1, 1.7, 'Call Notes.', 0, 2, 'same'),
                  synthetic_cue(2.1, 4.5, 'No notes found.', 2, 5, 'same')]
        merged, receipts = PREP.merge_short_same_screen(before)
        self.assertEqual((merged[0]['start'], merged[0]['end']), (1, 4.5))
        self.assertEqual(merged[0]['text'], 'Call Notes. No notes found.')
        self.assertEqual(len(receipts), 1)
        self.assertEqual(before[0]['end'], 1.7)

    def test_caption_merge_rejects_cross_screen_fabrication(self):
        before = [synthetic_cue(1, 1.7, 'Call Notes.', 0, 2, 'entry'),
                  synthetic_cue(2.1, 4.5, 'No notes found.', 2, 5, 'dialog')]
        with self.assertRaisesRegex(ValueError, 'no same-screen'):
            PREP.merge_short_same_screen(before)

    def test_missing_listening_hash_blocks_before_plan_creation(self):
        data = {'catalog': {'parent': {'sha256': TIMING}}}
        with patch.object(AUTHOR, 'preflight', return_value=data), self.assertRaisesRegex(ValueError, 'User full-listening'):
            AUTHOR.build('dispatch', None, TIMING)

    def test_wrong_timing_pin_cannot_be_replaced_by_listening(self):
        data = {'catalog': {'parent': {'sha256': TIMING}}}
        with patch.object(AUTHOR, 'preflight', return_value=data), patch.object(AUTHOR, 'listening') as heard:
            with self.assertRaisesRegex(ValueError, 'Root transition'):
                AUTHOR.build('dispatch', '0' * 64, '1' * 64)
            heard.assert_not_called()

    def test_ic_unreviewed_projection_blocks_even_with_listening_argument(self):
        data = {'catalog': {'parent': {'sha256': TIMING}}, 'projection': None}
        with patch.object(AUTHOR, 'preflight', return_value=data), patch.object(AUTHOR, 'listening') as heard:
            with self.assertRaisesRegex(ValueError, 'IC public projection'):
                AUTHOR.build('ic', '0' * 64, TIMING)
            heard.assert_not_called()

    def test_ic_projection_changes_exactly_two_arrays_and_no_pixels(self):
        provenance, _ = PROJECTION.prepare()
        self.assertEqual([row['json_pointer'] for row in provenance['operations']],
                         ['/scenes/1/required_labels', '/screenshots/1/visible_labels'])
        self.assertTrue(provenance['only_these_two_arrays_changed'])
        self.assertTrue(provenance['actual_pixels_DOM_provenance_reviews_unchanged'])
        self.assertFalse(provenance['projection_approved'])

    def test_projection_receipt_cannot_claim_user_listening_or_wrong_source(self):
        provenance, _ = PROJECTION.prepare()
        record = {'reviewer': 'Root', 'approved_for_public_label_projection': True,
            'projection_provenance_sha256': 'synthetic',
            'original_source_sha256': provenance['original_source']['sha256'],
            'projected_source_sha256': provenance['prospective_source_sha256'],
            'original_manifest_sha256': provenance['original_manifest']['sha256'],
            'projected_manifest_sha256': provenance['prospective_manifest_sha256'],
            'narration_words_unchanged': True, 'only_two_arrays_changed': True,
            'human_listening_claim': False, 'recorded_at': '2026-10-29T00:00:00Z'}
        for change in [{'human_listening_claim': True}, {'projected_source_sha256': '0' * 64}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                AUTHOR.validate_projection_review({**record, **change}, provenance, 'synthetic')

    def test_literal_annotations_never_invent_hidden_names(self):
        proposal = {'cue_correspondence': [{'cue': 1, 'scene_id': 'synthetic', 'screenshot_id': 'one',
            'text': 'Open a hidden control.', 'start': 0, 'end': 2}]}
        manifest = {'screenshots': [{'id': 'one', 'visible_labels': ['Visible control']}]}
        rows = AUTHOR.annotate('dispatch', proposal, manifest)
        self.assertEqual(rows[0]['required_labels'], [])
        self.assertEqual(rows[0]['spoken_references'], {})


if __name__ == '__main__':
    unittest.main()
