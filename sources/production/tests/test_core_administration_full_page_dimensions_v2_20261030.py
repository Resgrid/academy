"""Dimension guards using unchanged genuine full-page JPEGs; no proof is created."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
PRODUCTION = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'administration_full_page_qualifier', PRODUCTION / 'qualify_core_administration_releases_20261030_v2.py')
QUALIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(QUALIFY)

ACTUAL_BEGINNING = (
    ('core-customer-billing-review-take-02', (1291, 1360),
     '2c522bedcf1402a4dc09bbaa4bc2556e9f0b45bd288c44bfaac529e3fe1e0335'),
    ('core-shifts-administration-take-02', (1280, 1360),
     'de4c90996053d21961442f0ad865cc540141bec61c58994dc6369eb1404f48a3'),
    ('core-training-administration-take-01', (1291, 1360),
     'db073148846df7eaef48b0af31d1a7ca83fe8b5c13041849d9068537d072d543'),
)


class ActualFullPageDimensions(unittest.TestCase):
    def test_real_full_page_headers_match_actual_metadata_without_mutation(self):
        for take, dimensions, digest in ACTUAL_BEGINNING:
            with self.subTest(take=take):
                folder = QUALIFY.SOURCES / 'expansion/rendered' / take / 'playback/root-live-20261030'
                row = json.loads((folder / 'raw-observations.reviewed-selection.json').read_text())[0]
                screenshot = deepcopy(row['screenshot'])
                before = deepcopy(screenshot)
                image = QUALIFY.SOURCES / screenshot['file']
                self.assertEqual(QUALIFY.sha(image), digest)
                self.assertEqual(QUALIFY.validate_screenshot_dimensions(screenshot, image), dimensions)
                self.assertEqual(screenshot, before)
                self.assertEqual(QUALIFY.sha(image), digest)

    def test_misreported_viewport_dimensions_reject_real_full_page_image(self):
        folder = QUALIFY.SOURCES / 'expansion/rendered' / ACTUAL_BEGINNING[0][0] / 'playback/root-live-20261030'
        image = folder / 'beginning.jpg'
        for dimensions in ((1280, 720), (1291, 1359), (1290, 1360)):
            with self.subTest(dimensions=dimensions), self.assertRaisesRegex(ValueError, 'header dimensions'):
                QUALIFY.validate_screenshot_dimensions({'width': dimensions[0], 'height': dimensions[1]}, image)

    def test_missing_noninteger_or_boolean_metadata_is_rejected(self):
        image = QUALIFY.SOURCES / 'expansion/rendered' / ACTUAL_BEGINNING[0][0] / 'playback/root-live-20261030/beginning.jpg'
        for metadata in ({}, {'width': 1291}, {'width': '1291', 'height': 1360},
                         {'width': True, 'height': 1360}, {'width': 1291.0, 'height': 1360}):
            with self.subTest(metadata=metadata), self.assertRaisesRegex(ValueError, 'integer width and height'):
                QUALIFY.validate_screenshot_dimensions(metadata, image)

    def test_real_undersized_header_is_rejected_despite_truthful_metadata(self):
        image = QUALIFY.SOURCES / 'brand/favicon-32x32.png'
        with self.assertRaisesRegex(ValueError, '960x540 minimum'):
            QUALIFY.validate_screenshot_dimensions({'width': 32, 'height': 32}, image)

    def test_each_minimum_dimension_is_enforced(self):
        # In-memory header responses exercise boundary arithmetic only. No
        # image, browser proof, approval or accepted receipt is generated.
        sys.path.insert(0, str(QUALIFY.ROOT / 'scripts'))
        import verify_capture_evidence
        for width, height in ((959, 1360), (1291, 539)):
            with self.subTest(width=width, height=height), patch.object(
                    verify_capture_evidence, '_image_dimensions', return_value=(width, height)):
                with self.assertRaisesRegex(ValueError, '960x540 minimum'):
                    QUALIFY.validate_screenshot_dimensions({'width': width, 'height': height}, Path('header-only-negative-case'))

    def test_original_history_and_every_other_function_are_unchanged(self):
        original = PRODUCTION / 'qualify_core_administration_releases_20261030.py'
        self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),
                         '6da68e5e16a4daee97b37e474943308404364ab8240f976737128a69ae2bcce9')
        old = {node.name: node for node in ast.parse(original.read_text()).body if isinstance(node, ast.FunctionDef)}
        new = {node.name: node for node in ast.parse(Path(QUALIFY.__file__).read_text()).body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(set(new) - set(old), {'validate_screenshot_dimensions'})
        for name in set(old) - {'validate_playback'}:
            self.assertEqual(ast.dump(old[name]), ast.dump(new[name]), name)


if __name__ == '__main__':
    unittest.main()
