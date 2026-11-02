"""Read-only preparation and refusal tests; no synthetic hearing is approved."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
AUTHOR = S / 'production/author_core_records_administration_take_01_20261030.py'
spec = importlib.util.spec_from_file_location('records_definition_actual_author', AUTHOR)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class RecordsDefinitionGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = m.preflight()
        sys.path.insert(0, str(ROOT / 'scripts'))
        from render_walkthrough import load_cues
        cls.cues = load_cues(S / m.CAPTIONS)

    def test_actual_readonly_complete_preflight(self):
        # The retained author must remain read-only after the real lesson has
        # been released as well as before its first render.
        def snapshot():
            paths = [S / m.LISTENING]
            final = S / m.FINAL
            if final.exists():
                paths.extend(sorted(path for path in final.rglob('*') if path.is_file()))
            return {str(path): path.read_bytes() if path.is_file() else None for path in paths}

        before = snapshot()
        data = m.preflight()
        self.assertEqual((len(data['scenes']), len(data['entries']), len(data['mapping']['source_spans'])), (16, 135, 39))
        self.assertEqual(data['duration'], 476.8914375)
        self.assertEqual(snapshot(), before)

    def test_changed_source_pin_refused(self):
        with patch.dict(m.PINS, {m.MAP: '0' * 64}):
            with self.assertRaisesRegex(ValueError, 'Changed pinned actual input'):
                m.retained_guards()

    def test_missing_retained_input_refused(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(m, 'S', Path(folder)):
            with self.assertRaisesRegex(ValueError, 'Missing retained source asset'):
                m.retained_guards()

    def test_parent_receipt_argument_required(self):
        with patch.object(m, 'preflight', side_effect=AssertionError('must fail before preparation')):
            with self.assertRaisesRegex(ValueError, 'exact genuine Root'):
                m.build(None, '0' * 64)

    def test_missing_hearing_argument_refused(self):
        with self.assertRaisesRegex(ValueError, 'exact genuine User'):
            m.listening(self.data, None)

    def test_missing_actual_hearing_receipt_refused(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(m, 'S', Path(folder)):
            with self.assertRaisesRegex(ValueError, 'Missing retained source asset'):
                m.listening(self.data, 'a' * 64)

    def test_changed_actual_hearing_receipt_refused(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(m, 'S', Path(folder)):
            receipt = Path(folder) / m.LISTENING
            receipt.parent.mkdir(parents=True)
            receipt.write_text('changed fixture; never a genuine listening approval')
            with self.assertRaisesRegex(ValueError, 'Changed/unreviewed actual User listening receipt'):
                m.listening(self.data, 'a' * 64)

    def test_other_lesson_genuine_receipt_is_not_this_approval(self):
        other = json.loads((S / 'expansion/audio/app-responder-call-context-review.listening-review.json').read_text())
        with self.assertRaisesRegex(ValueError, 'identity differs'):
            self.data['guards'].validate_listening_record(other, m.SOURCE_SHA, m.AUDIO_SHA,
                                                           self.data['original_qa']['checked_at'])

    def test_raw_path_escape_and_private_path_refused(self):
        for path in ('../source.json', '/private/tmp/file', 'x/../file', 'x/./file', 'x//file',
                     'private/key.json', 'node_modules/file', '.env', 'x\\file', 'https://example.invalid/file'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                m.contained(path, must_exist=False)

    def test_symlink_input_refused(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(m, 'S', Path(folder)):
            (Path(folder) / 'actual').write_text('synthetic path fixture only')
            (Path(folder) / 'linked').symlink_to(Path(folder) / 'actual')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                m.contained('linked')

    def test_naive_or_future_review_date_refused(self):
        for value in ('2026-10-30T00:00:00', (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()):
            with self.subTest(value=value), self.assertRaises(ValueError):
                m.date(value)

    def test_changed_actual_caption_words_refused(self):
        cues = deepcopy(self.cues)
        cues[0]['text'] += ' invented'
        with self.assertRaisesRegex(ValueError, 'SRT words/endpoints differ'):
            m.annotate(self.data['mapping'], self.data['manifest'], cues)

    def test_changed_actual_caption_time_refused(self):
        cues = deepcopy(self.cues)
        cues[0]['end'] += .001
        with self.assertRaisesRegex(ValueError, 'SRT words/endpoints differ'):
            m.annotate(self.data['mapping'], self.data['manifest'], cues)

    def test_changed_source_identity_refused(self):
        mapping = deepcopy(self.data['mapping'])
        mapping['cue_correspondence'][0]['source_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'source identity changed'):
            m.annotate(mapping, self.data['manifest'], self.cues)

    def test_existing_final_package_preserved(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(m, 'S', Path(folder)):
            path = Path(folder) / 'out'
            path.mkdir()
            retained = path / 'keep.txt'
            retained.write_text('preserve synthetic output fixture')
            with self.assertRaisesRegex(ValueError, 'New-only'):
                m.write_new_directory(path, {'plan.json': b'not an actual plan'})
            self.assertEqual(retained.read_text(), 'preserve synthetic output fixture')
            self.assertFalse((path / 'plan.json').exists())

    def test_optimized_interpreter_cannot_disable_guards(self):
        result = subprocess.run([sys.executable, '-B', '-O', str(AUTHOR)], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('ordinary Python', result.stderr)


if __name__ == '__main__':
    unittest.main()
