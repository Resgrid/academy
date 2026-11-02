"""Read-only real-input and in-memory rejection tests; no listening receipt created."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
FILE = Path(__file__).with_name('author_unit_native_call_lifecycle_take_01_20261030.py')
spec = importlib.util.spec_from_file_location('native_unit_author_guard', FILE)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class ActualNativeUnitAuthorGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe, cls.manifest, cls.qa = a.prepare()
        cls.original_recipe = (a.S / a.RECIPE).read_bytes()
        cls.original_manifest = (a.S / a.CONTEXT / 'captures.reviewed.json').read_bytes()
        if (a.S / a.FINAL).exists():
            raise unittest.SkipTest('Final authoring already exists; this historical guard suite does not operate on it.')

    def tearDown(self):
        self.assertFalse((a.S / a.FINAL).exists(), 'Rejection tests must never create final inputs.')
        self.assertEqual((a.S / a.RECIPE).read_bytes(), self.original_recipe)
        self.assertEqual((a.S / a.CONTEXT / 'captures.reviewed.json').read_bytes(), self.original_manifest)

    def command_rejected(self, *arguments):
        result = subprocess.run([sys.executable, '-B', str(FILE), *arguments], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        return result.stderr

    def test_actual_public_source_and_complete_recipe_are_unchanged(self):
        self.assertEqual(a.encoded(self.recipe), self.original_recipe)
        self.assertEqual(len(self.manifest['screenshots']), 23)
        self.assertEqual(sum(len(s['captions']) for s in self.recipe['scenes']), 88)
        self.assertEqual(len({c['cue'] for s in self.recipe['scenes'] for c in s['captions']}), 88)

    def test_actual_genuine_Root_reviews_pass_readonly(self):
        receipt, path = a.actual_root_preflight(self.qa)
        self.assertEqual(path, a.ROOT_REVIEW)
        self.assertEqual(receipt['authoring_recipe_sha256'], a.sha(a.S / a.RECIPE))
        self.assertFalse(receipt['actual_User_hearing_claimed'])

    def test_recipe_cannot_be_overwritten(self):
        self.assertIn('Preserve exact existing source recipe', self.command_rejected('--write-recipe'))

    def test_wrong_Root_map_hash_rejected_before_authoring(self):
        self.assertIn('exact genuine pinned Root', self.command_rejected('--assemble', '--parent-review-sha256', '0' * 64))

    def test_missing_User_hearing_hash_rejected_before_authoring(self):
        self.assertIn('genuine User listening receipt SHA256', self.command_rejected('--assemble'))

    def test_nonmatching_User_hearing_hash_rejected_before_authoring(self):
        self.assertIn('User listening receipt absent or changed', self.command_rejected('--assemble', '--listening-review-sha256', '0' * 64))

    def test_real_different_lesson_hearing_is_not_reused(self):
        other = 'expansion/audio/core-records-training-entry.listening-review.json'
        digest = a.sha(a.S / other)
        with self.assertRaisesRegex(ValueError, 'different source or audio'):
            a.actual_receipt(other, digest, 'User listening', self.qa)

    def test_in_memory_false_Root_hearing_claim_is_rejected(self):
        # Synthetic in-memory negative fixture only; never written or accepted.
        actual_read = a.read
        def changed(p):
            d = deepcopy(actual_read(p))
            if p == a.S / a.ROOT_REVIEW: d['actual_User_hearing_claimed'] = True
            return d
        with patch.object(a, 'read', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'cannot replace hearing'):
                a.actual_root_preflight(self.qa)

    def test_in_memory_rejected_context_cannot_be_accepted(self):
        # Synthetic in-memory negative fixture only; all disk evidence unchanged.
        actual_read = a.read
        def changed(p):
            d = deepcopy(actual_read(p))
            if p == a.S / a.ROOT_MAP: d['delegated_context_review_accepted'] = False
            return d
        with patch.object(a, 'read', side_effect=changed):
            with self.assertRaisesRegex(ValueError, 'map/context scope is incomplete'):
                a.actual_root_preflight(self.qa)


if __name__ == '__main__': unittest.main()
