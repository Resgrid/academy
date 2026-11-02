"""Focused Records authoring guards; synthetic fixtures are not review evidence."""
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('records_lifecycle_final_author', ROOT / 'sources/production/author_core_records_training_entry_take_01_20261030.py')
AUTHOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHOR)


def snapshot_tree(root):
    if root.is_symlink():
        return ('symlink', str(root.readlink()))
    if not root.exists():
        return None
    return {path.relative_to(root).as_posix():
            ('symlink', str(path.readlink())) if path.is_symlink() else
            ('directory',) if path.is_dir() else ('file', AUTHOR.sha(path))
            for path in sorted(root.rglob('*'))}


class RecordsFinalAuthoringGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.final_before_preflight = snapshot_tree(AUTHOR.S / AUTHOR.FINAL)
        cls.data = AUTHOR.preflight()
        cls.final_after_preflight = snapshot_tree(AUTHOR.S / AUTHOR.FINAL)

    def test_actual_read_only_preflight_scope_preserves_final_package(self):
        self.assertEqual((len(self.data['scenes']), len(self.data['entries']), len(self.data['manifest']['screenshots'])), (12, 112, 16))
        self.assertEqual(len(self.data['proposal']['source_spans']), 20)
        self.assertEqual(len(self.data['proposal']['whole_cue_continuous_holds_proposed']), 17)
        self.assertEqual(self.data['duration'], 392.9745208333333)
        self.assertEqual(self.final_after_preflight, self.final_before_preflight)

    def test_instruction_digests_match_actual_renderer_cue_expansion(self):
        # A different float-addition order in the old proposal must never
        # invalidate an otherwise identical actual SRT/scene digest.
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from render_walkthrough import load_cues
        from verify_capture_evidence import instruction_scene_digest
        actual = load_cues(AUTHOR.S / self.data['corrected_file'])
        rows = {row['id']: row for row in self.data['manifest']['screenshots']}
        for original in self.data['scenes']:
            expanded = deepcopy(original)
            expanded['captions'] = [{**actual[cue['cue'] - 1], **{key: cue[key] for key in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']}} for cue in original['captions']]
            self.assertEqual(instruction_scene_digest(expanded, rows), original['instruction_review']['mapping_sha256'])

    def test_changed_actual_caption_or_crossed_source_is_rejected(self):
        captions = [{key: cue[key] for key in ['start', 'end', 'text']} for cue in self.data['entries']]
        for change in ['text', 'source']:
            proposal = deepcopy(self.data['proposal'])
            if change == 'text':
                proposal['actual_cues'][0]['text'] += ' synthetic changed words'
            else:
                proposal['actual_cues'][0]['source_ids_in_exact_spoken_order'].append('absent-second-image')
            with self.subTest(change=change), self.assertRaises(ValueError):
                AUTHOR.annotate(proposal, self.data['manifest'], captions)

    def test_absent_actual_source_cannot_supply_control_reference(self):
        captions = [{key: cue[key] for key in ['start', 'end', 'text']} for cue in self.data['entries']]
        with self.assertRaises(ValueError):
            AUTHOR.annotate(self.data['proposal'], {'screenshots': []}, captions)

    def test_spoken_aliases_use_only_present_literal_and_phrase(self):
        rows = {row['id']: row for row in self.data['manifest']['screenshots']}
        for cue in self.data['entries']:
            for literal, phrase in cue['spoken_references'].items():
                self.assertIn(literal, rows[cue['screenshot_id']]['visible_labels'])
                self.assertIn(AUTHOR.norm(phrase), AUTHOR.norm(cue['text']))

    def test_missing_wrong_or_unbound_receipt_is_rejected(self):
        m = self.data['preparer']
        for digest in [None, '', 'not-a-digest', '0' * 64]:
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                AUTHOR.actual_receipt(m, 'expansion/audio/synthetic-unwritten-missing-review.json', digest, 'listening', self.data['qa']['checked_at'])

    def test_complete_root_map_review_cannot_replace_user_listening(self):
        # The real parent map receipt exists and passes its own kind; asking
        # the same file to stand in for User hearing must fail.
        with self.assertRaises(ValueError):
            AUTHOR.actual_receipt(self.data['preparer'], self.data['parent_file'], AUTHOR.PARENT_SHA, 'listening', self.data['qa']['checked_at'])

    def test_wrong_parent_hash_stops_build_before_any_receipt_or_output(self):
        with patch.object(AUTHOR, 'preflight', side_effect=AssertionError('must not read for wrong parent')):
            with self.assertRaisesRegex(ValueError, 'Root'):
                AUTHOR.build('0' * 64, '1' * 64)

    def test_missing_user_receipt_stops_build_without_mutation(self):
        with tempfile.TemporaryDirectory(prefix='academy-records-missing-receipt-') as directory:
            root = Path(directory)
            before = snapshot_tree(root)
            # Retain the actual read-only preflight facts while isolating the
            # deliberately absent receipt and every possible output path.
            with patch.object(AUTHOR, 'S', root), patch.object(AUTHOR, 'preflight', return_value=self.data):
                with self.assertRaisesRegex(ValueError, 'Actual listening receipt absent or changed'):
                    AUTHOR.build('0' * 64, AUTHOR.PARENT_SHA, 'expansion/audio/synthetic-unwritten-missing-review.json')
            self.assertEqual(snapshot_tree(root), before)

    def test_receipt_path_rejects_private_remote_escape_empty_and_symlinks(self):
        for value in ['../outside.json', '/tmp/review.json', 'expansion/private/review.json', 'https://example.invalid/review.json', '', '.env.local']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                AUTHOR.receipt_path(value)
        with tempfile.TemporaryDirectory(prefix='academy-records-author-tests-') as directory:
            root = Path(directory)
            (root / 'linked').symlink_to(root / 'missing-target')
            with patch.object(AUTHOR, 'S', root), self.assertRaises(ValueError):
                AUTHOR.receipt_path('linked/review.json')

    def test_new_only_output_refuses_replacement_or_escape(self):
        with tempfile.TemporaryDirectory(prefix='academy-records-author-tests-') as directory:
            root = Path(directory)
            with patch.object(AUTHOR, 'S', root):
                path = root / 'new'
                AUTHOR.write_new_directory(path, {'fixture.txt': b'Synthetic file output guard; no media or review evidence.\n'})
                before = hashlib.sha256((path / 'fixture.txt').read_bytes()).hexdigest()
                with self.assertRaises(ValueError):
                    AUTHOR.write_new_directory(path, {'fixture.txt': b'cannot replace'})
                self.assertEqual(hashlib.sha256((path / 'fixture.txt').read_bytes()).hexdigest(), before)
                with self.assertRaises(ValueError):
                    AUTHOR.write_new_directory(root.parent / 'escaping-records-output', {})


if __name__ == '__main__':
    unittest.main()
