"""Synthetic guard tests; no browser, apps, credentials, audio or Git operations."""

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'freeze_ic_access_session_settings_20261029.py'
SPEC = importlib.util.spec_from_file_location('ic_access_freezer', SCRIPT)
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)


def model():
    rows = []
    for n in range(10):
        rows.append({'id': f'screen-{n}', 'app': 'IC', 'kind': 'application_screenshot',
                     'sha256': f'{n:064x}', 'file': f'images/{n}.jpg',
                     'visible_labels': [f'Control {n}'], 'visible_controls': [],
                     'eligible_for_lesson': True,
                     'capture_review': {'passed': True, 'sha256': f'{n:064x}'}})
    scenes, spans = [], []
    for n, count in enumerate([90] * 7 + [80]):
        text = ' '.join(f'word{i}' for i in range(count))
        chosen = [rows[n], rows[(n + 3) % 10]]
        cuts = [0, 20, 40, count] if n == 0 else [0, 40, count]
        parts = text.split(' ')
        sid = f'scene-{n}'
        for i, (start, end) in enumerate(zip(cuts, cuts[1:])):
            row = chosen[i % 2]
            spans.append({'scene_id': sid, 'source_id': row['id'],
                          'source_file': row['file'], 'source_sha256': row['sha256'],
                          'required_labels': row['visible_labels'],
                          'narration_exact': ' '.join(parts[start:end]) + (' ' if end < count else '')})
        scenes.append({'id': sid, 'narration': text,
                       'capture_refs': [r['id'] for r in chosen],
                       'required_labels': [v for r in chosen for v in r['visible_labels']]})
    lesson = {'id': F.NAME, 'app': 'IC', 'export_ready': False,
              'publication_approved': False, 'scenes': scenes,
              'sector_examples': [{'sector': str(n)} for n in range(6)]}
    return lesson, {'spans': spans}, {'screenshots': rows}, '\n\n'.join(r['narration'] for r in scenes) + '\n'


class CorrespondenceGuards(unittest.TestCase):
    def setUp(self):
        self.args = model()

    def check(self):
        F.validate_correspondence(*self.args)

    def test_exact_untimed_source_model_passes(self):
        self.check()

    def test_illustrated_substitute_is_rejected(self):
        self.args[2]['screenshots'][0]['kind'] = 'illustration'
        with self.assertRaisesRegex(ValueError, 'Illustrated'):
            self.check()

    def test_missing_spoken_control_is_rejected(self):
        self.args[2]['screenshots'][0]['visible_labels'] = []
        with self.assertRaisesRegex(ValueError, 'control missing'):
            self.check()

    def test_review_hash_cannot_move_to_another_image(self):
        self.args[2]['screenshots'][0]['sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'Review/image hash'):
            self.check()

    def test_timing_cannot_be_invented(self):
        self.args[1]['spans'][0]['start_seconds'] = 0
        with self.assertRaisesRegex(ValueError, 'Invented cue timing'):
            self.check()

    def test_missing_narration_character_is_rejected(self):
        self.args[1]['spans'][0]['narration_exact'] = self.args[1]['spans'][0]['narration_exact'][1:]
        with self.assertRaisesRegex(ValueError, 'Unshown'):
            self.check()

    def test_reordered_holds_are_rejected(self):
        spans = self.args[1]['spans']
        spans[0], spans[1] = spans[1], spans[0]
        with self.assertRaisesRegex(ValueError, 'reordered narration'):
            self.check()

    def test_source_freeze_cannot_claim_publication(self):
        self.args[0]['export_ready'] = True
        with self.assertRaisesRegex(ValueError, 'media-ready'):
            self.check()

    def test_missing_sector_and_changed_exact_script_are_rejected(self):
        self.args[0]['sector_examples'].pop()
        with self.assertRaisesRegex(ValueError, 'six sectors'):
            self.check()
        self.args = model()
        self.args[0]['scenes'][0]['narration'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'Exact narration'):
            self.check()

    def test_duplicate_capture_identity_is_rejected(self):
        self.args[2]['screenshots'][1]['id'] = 'screen-0'
        with self.assertRaisesRegex(ValueError, 'Duplicate capture'):
            self.check()


class NewOnlyGuards(unittest.TestCase):
    def test_existing_package_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'freeze'
            dest.mkdir()
            sentinel = dest / 'human-work.txt'
            sentinel.write_text('keep exactly')
            with self.assertRaisesRegex(ValueError, 'existing freeze'):
                F.write_new_package(dest, {'human-work.txt': b'replace'})
            self.assertEqual(sentinel.read_text(), 'keep exactly')

    def test_parent_traversal_is_rejected_before_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'freeze'
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                F.write_new_package(dest, {'../escape.txt': b'no'})
            self.assertFalse(dest.exists())
            self.assertFalse((Path(directory) / 'escape.txt').exists())

    def test_write_is_new_only_and_preserves_nested_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'freeze'
            expected = {'images/a.jpg': b'fixture bytes', 'dom/a.txt': b'actual DOM fixture'}
            F.write_new_package(dest, expected)
            self.assertEqual({str(p.relative_to(dest)): p.read_bytes() for p in dest.rglob('*') if p.is_file()}, expected)
            with self.assertRaisesRegex(ValueError, 'existing freeze'):
                F.write_new_package(dest, expected)

    def test_symlinked_input_cannot_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'real').write_bytes(b'keep')
            (root / 'link').symlink_to(root / 'real')
            with self.assertRaisesRegex(ValueError, 'symlinked'):
                F.read_file(root, 'link')


if __name__ == '__main__':
    unittest.main()
