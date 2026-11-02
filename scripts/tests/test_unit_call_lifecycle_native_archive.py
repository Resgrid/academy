"""Archive fixtures only: no recording hosts, credentials, media creation or apps."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'native_unit_archival_checker', ROOT / 'sources/production/check_unit_call_lifecycle_native_archive_20261030.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class NativeUnitArchiveChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='academy-native-unit-archive-test-')
        self.addCleanup(self.temporary.cleanup)
        self.sources = Path(self.temporary.name) / 'sources'
        self.candidate = self.sources / str(M.BASE)
        shutil.copytree(ROOT / 'sources' / str(M.BASE), self.candidate)
        review = self.sources / str(M.REVIEW)
        review.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'sources' / str(M.REVIEW), review)
        self.lesson = json.loads((self.candidate / 'lesson.candidate.json').read_text())
        self.mapping = json.loads((self.candidate / 'sentence-screen-map.untimed.json').read_text())
        self.narration = (self.candidate / 'narration.txt').read_text()
        self.captures = json.loads((self.candidate / 'captures.native-reviewed.json').read_text())
        self.image = self.sources / self.captures['native_sources'][0]['file']

    def check_continuity(self, lesson=None, mapping=None, narration=None, captures=None):
        return M.continuity(lesson or self.lesson, mapping or self.mapping,
                            narration or self.narration, captures or self.captures)

    def test_installed_subset_works_without_original_recipe_projection_or_host_paths(self):
        expected = {p.resolve() for p in self.candidate.rglob('*') if p.is_file()}
        expected.add((self.sources / str(M.REVIEW)).resolve())
        opened = []
        real_open = Path.open

        def bounded_open(path, *args, **kwargs):
            self.assertIn(path.resolve(), expected, 'Checker attempted an external or historical file read.')
            opened.append(path.resolve())
            return real_open(path, *args, **kwargs)

        with patch.object(Path, 'open', bounded_open):
            result = M.verify(self.sources)
        self.assertEqual(set(opened), expected)
        self.assertEqual(len(opened), 57)
        self.assertEqual((result['paragraphs'], result['untimed_sentences'], result['exact_words']), (15, 59, 835))
        self.assertTrue(result['read_only'])
        self.assertFalse(result['historical_source_paths_followed'])
        self.assertFalse(result['new_pixel_review_or_human_listening_or_publication_claim'])
        self.assertFalse((self.sources / 'production/prepare_unit_call_lifecycle_native_20261030.py').exists())

    def test_missing_native_image_is_rejected(self):
        self.image.unlink()
        with self.assertRaisesRegex(ValueError, 'Required archived file is missing'):
            M.verify(self.sources)

    def test_default_cli_runs_from_a_minimal_relocated_installed_package(self):
        checker = self.sources / 'production/check_unit_call_lifecycle_native_archive_20261030.py'
        checker.parent.mkdir()
        shutil.copyfile(ROOT / 'sources/production/check_unit_call_lifecycle_native_archive_20261030.py', checker)
        result = subprocess.run([sys.executable, '-B', str(checker)], cwd=self.temporary.name,
                                check=True, capture_output=True, text=True)
        summary = json.loads(result.stdout)
        self.assertTrue(summary['self_contained_archive_verified'])
        self.assertEqual(summary['unchanged_native_pngs_checked'], 23)
        self.assertFalse(summary['historical_source_paths_followed'])

    def test_tampered_native_image_is_rejected(self):
        self.image.write_bytes(self.image.read_bytes() + b'tampered')
        with self.assertRaisesRegex(ValueError, 'Changed archived file'):
            M.verify(self.sources)

    def test_missing_copied_metadata_is_rejected(self):
        metadata = self.sources / self.captures['native_sources'][0]['metadata_file']
        metadata.unlink()
        with self.assertRaisesRegex(ValueError, 'Required archived file is missing'):
            M.verify(self.sources)

    def test_missing_or_changed_existing_root_review_is_rejected(self):
        review = self.sources / str(M.REVIEW)
        review.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Changed archived file'):
            M.verify(self.sources)
        review.unlink()
        with self.assertRaisesRegex(ValueError, 'Required archived file is missing'):
            M.verify(self.sources)

    def test_equal_bytes_through_a_file_symlink_are_rejected(self):
        outside = self.sources / 'outside.png'
        self.image.rename(outside)
        self.image.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'Symlinked archive path'):
            M.verify(self.sources)

    def test_directory_symlink_is_rejected_before_following_it(self):
        images = self.candidate / 'images'
        outside = self.sources / 'outside-images'
        images.rename(outside)
        images.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinked archive path'):
            M.verify(self.sources)

    def test_escape_and_noncanonical_paths_are_rejected_without_file_content_reads(self):
        for value in ['/tmp/other.png', '../other.png', str(M.BASE) + '/../../outside.png',
                      str(M.BASE) + '//images/file.png', './' + str(M.BASE) + '/images/file.png',
                      str(M.BASE) + '\\images\\file.png', 'production/old-recipe.py', '.']:
            with self.subTest(value=value), patch.object(Path, 'read_bytes', side_effect=AssertionError('Unexpected read')):
                with self.assertRaises(ValueError):
                    M.safe_file(self.sources, value)

    def test_extra_undeclared_archive_asset_is_rejected(self):
        (self.candidate / 'unreviewed-extra.txt').write_text('not part of the frozen archive')
        with self.assertRaisesRegex(ValueError, 'undeclared or missing files'):
            M.verify(self.sources)

    def test_changed_narration_or_sentence_order_breaks_exact_continuity(self):
        changed = deepcopy(self.mapping)
        changed['sentences'][0]['text'] += ' Extra invented claim.'
        with self.assertRaisesRegex(ValueError, 'Sentence continuity'):
            self.check_continuity(mapping=changed)
        changed = deepcopy(self.mapping)
        changed['sentences'][0], changed['sentences'][1] = changed['sentences'][1], changed['sentences'][0]
        with self.assertRaisesRegex(ValueError, 'Sentence continuity|Sentence identity'):
            self.check_continuity(mapping=changed)
        with self.assertRaisesRegex(ValueError, 'Narration file differs'):
            self.check_continuity(narration=self.narration.replace('\n\n', '\n', 1))

    def test_missing_sentence_and_invented_timing_are_rejected(self):
        changed = deepcopy(self.mapping)
        changed['sentences'].pop()
        with self.assertRaisesRegex(ValueError, '59 untimed sentences'):
            self.check_continuity(mapping=changed)
        changed = deepcopy(self.mapping)
        changed['sentences'][0]['speech_timing'] = {'start': 0, 'end': 3}
        with self.assertRaisesRegex(ValueError, 'invented source timing'):
            self.check_continuity(mapping=changed)

    def test_wrong_source_revision_or_unseen_control_is_rejected(self):
        changed = deepcopy(self.mapping)
        changed['sentences'][0]['image_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'another image revision'):
            self.check_continuity(mapping=changed)
        changed = deepcopy(self.mapping)
        changed['sentences'][3]['native_control'] = 'invented-button'
        with self.assertRaisesRegex(ValueError, 'no retained control observation'):
            self.check_continuity(mapping=changed)

    def test_real_png_signature_and_geometry_are_checked(self):
        body = self.image.read_bytes()
        self.assertEqual(M.png_geometry(body), (2732, 2048))
        with self.assertRaisesRegex(ValueError, 'not a PNG'):
            M.png_geometry(b'not a real PNG' + body[14:])
        changed = bytearray(body)
        changed[16:20] = (1).to_bytes(4, 'big')
        with self.assertRaisesRegex(ValueError, 'geometry differs'):
            M.png_geometry(changed)


if __name__ == '__main__':
    unittest.main()
