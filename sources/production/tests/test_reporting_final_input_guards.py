"""Reporting guards; synthetic receipts stay in memory, never author approval."""
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
MODULE = Path(__file__).resolve().parents[1] / 'author_core_reporting_fundamentals_take_01.py'
spec = importlib.util.spec_from_file_location('reporting_final_author', MODULE)
author = importlib.util.module_from_spec(spec)
spec.loader.exec_module(author)
SOURCE = '1' * 64
AUDIO = '2' * 64
QA_TIME = '2026-10-29T23:21:08Z'
NOW = datetime(2026, 10, 30, 0, 0, tzinfo=timezone.utc)


class ReportingFinalInputGuardTests(unittest.TestCase):
    def receipt(self):
        return {'reviewer': 'User', 'reviewed_at': '2026-10-29T23:30:00Z',
                'lesson_sha256': SOURCE, 'audio_sha256': AUDIO,
                'complete_natural_narration': True,
                'evidence': 'SYNTHETIC TEST ONLY: full narration request; natural and complete response.'}

    def verify(self, record):
        return author.validate_listening_record(record, SOURCE, AUDIO, QA_TIME, NOW)

    def test_identity_bound_user_receipt_contract(self):
        self.assertEqual(self.verify(self.receipt())['reviewer'], 'User')

    def test_agent_qa_cannot_replace_actual_user(self):
        row = self.receipt(); row['reviewer'] = 'Codex root'
        with self.assertRaisesRegex(ValueError, 'actual User'):
            self.verify(row)

    def test_wrong_source_wrong_audio_and_incomplete_reply_rejected(self):
        for fields in [{'lesson_sha256': '3'*64}, {'audio_sha256': '4'*64},
                       {'complete_natural_narration': False}, {'complete_natural_narration': 'true'}]:
            with self.subTest(fields=fields):
                row = self.receipt(); row.update(fields)
                with self.assertRaises(ValueError): self.verify(row)

    def test_optional_fields_cannot_carry_a_link(self):
        for value in ['https' + ':' + '//example.invalid/review', 'localhost review', '127.0.0.1 review']:
            with self.subTest(value=value):
                row = self.receipt(); row['extra'] = {'review_location': value}
                with self.assertRaisesRegex(ValueError, 'URL-free'): self.verify(row)

    def test_pre_qa_future_and_timezone_free_receipts_rejected(self):
        for value in ['2026-10-29T23:20:00Z', '2026-10-30T00:01:00Z', '2026-10-29T23:30:00']:
            with self.subTest(value=value):
                row = self.receipt(); row['reviewed_at'] = value
                with self.assertRaisesRegex(ValueError, 'chronology'): self.verify(row)

    def test_missing_receipt_cannot_create_final_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'final'
            with patch.object(author, 'LISTENING', Path(temp)/'no-actual-review.json'), patch.object(author, 'FINAL', target):
                with self.assertRaisesRegex(ValueError, 'has not arrived'):
                    author.main(['--assemble', '--listening-review-sha256', '5'*64])
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_receipt_hash_is_required_before_file_read(self):
        with self.assertRaisesRegex(ValueError, 'exact real listening receipt SHA256'):
            author.listening(None, {})

    def test_existing_package_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)/'held'; output.mkdir()
            original = output/'held.bin'; original.write_bytes(b'preserve original')
            with self.assertRaisesRegex(ValueError, 'New-only'):
                author.write_new_directory(output, {'held.bin': b'changed'})
            self.assertEqual(original.read_bytes(), b'preserve original')
            self.assertEqual([x.name for x in output.iterdir()], ['held.bin'])

    def test_real_audio_binding_closes_only_former_open_endpoint(self):
        _, current, _, qa, assets = author.preflight()
        previous = json.loads((author.SOURCES/author.OLD/'correspondence.proposed.json').read_text())
        self.assertEqual(current['cue_correspondence'], previous['cue_correspondence'])
        self.assertEqual(current['caption_layout'], previous['caption_layout'])
        self.assertEqual(current['source_spans'][:-1], previous['source_spans'][:-1])
        self.assertIsNone(previous['source_spans'][-1]['proposed_end_seconds'])
        self.assertEqual(current['source_spans'][-1]['proposed_end_seconds'], 432.1698125)
        self.assertEqual(current['source_spans'][-1]['proposed_end_seconds'], qa['audio']['duration_seconds'])
        self.assertFalse(current['human_listening_approved'])
        self.assertEqual(assets['cue-screen-correspondence.txt'], (author.SOURCES/author.OLD/'cue-screen-correspondence.txt').read_bytes())

    def test_tampered_or_silent_qa_is_rejected(self):
        helper, _, _, qa, _ = author.preflight()
        from render_walkthrough import load_cues
        raw = load_cues(author.SOURCES/helper.RAW)
        corrected = load_cues(author.SOURCES/author.CORRECTED)
        for change in ['failed', 'silent', 'audio', 'samples']:
            with self.subTest(change=change):
                bad = deepcopy(qa)
                if change == 'failed': bad['passed'] = False
                elif change == 'silent': bad['corrected_captions']['energy'][0]['below_threshold'] = True
                elif change == 'audio': bad['audio']['sha256'] = '0'*64
                else: bad['audio']['decoded_samples'] -= 48000
                with self.assertRaises(ValueError): author.verify_audio_qa(bad, raw, corrected)

    def test_default_is_read_only_and_does_not_enter_assembly(self):
        before = {p: author.sha(author.SOURCES/p) for p in author.PINS}
        with patch.object(author, 'write_new_directory', side_effect=AssertionError('write attempted')), patch.object(author, 'build', side_effect=AssertionError('assembly attempted')):
            with redirect_stdout(io.StringIO()) as output: author.main([])
        status = json.loads(output.getvalue())
        self.assertTrue(status['source_preflight'])
        self.assertFalse(status['final_inputs_written'])
        self.assertFalse(status['rendered'])
        self.assertEqual(before, {p: author.sha(author.SOURCES/p) for p in author.PINS})


if __name__ == '__main__': unittest.main()
