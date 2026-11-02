"""Retained recipes keep their exact gate; current Big Board support is additive."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_capture_evidence as current


class HistoricalToolTests(unittest.TestCase):
    def test_retained_publisher_matches_original_qualification_gate(self):
        publisher = ROOT / 'sources/production/tests/fixtures/review-tools-20261030/expansion_site.py.txt'
        self.assertEqual(hashlib.sha256(publisher.read_bytes()).hexdigest(), 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8')

    def test_retained_validator_is_exact_and_current_extension_changes_only_app_identity(self):
        old = ROOT / 'sources/production/tests/fixtures/review-tools-20261030/verify_capture_evidence.py.txt'
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa')
        expected = old.read_text().replace('Core, Dispatch, Responder, Unit or IC', 'Core, Dispatch, Responder, Unit, IC or BigBoard').replace('"Unit", "IC"}', '"Unit", "IC", "BigBoard"}')
        intermediate = ROOT / 'sources/production/tests/fixtures/review-tools-20261030/verify_capture_evidence-bigboard-20261101.py.txt'
        self.assertEqual(intermediate.read_text(), expected)
        self.assertEqual(hashlib.sha256(intermediate.read_bytes()).hexdigest(), 'b599eda4ebe0628c20f89f06adac13b89aa77675f5662f1f2761ed21d01c2f98')
        self.assertIn('BigBoard', current.APPS)
        self.assertEqual(current.APPS - {'BigBoard'}, {'Core', 'Dispatch', 'Responder', 'Unit', 'IC'})


if __name__ == '__main__':
    unittest.main()
