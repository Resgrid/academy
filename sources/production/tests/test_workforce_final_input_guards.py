"""Synthetic listening-receipt tests; no actual approval is authored here."""
from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
MODULE=Path(__file__).resolve().parents[1]/'author_core_workforce_foundations_take_01.py'
spec=importlib.util.spec_from_file_location('workforce_author',MODULE)
author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
SOURCE='1'*64
AUDIO='2'*64
QA_TIME='2026-10-29T04:59:20Z'
NOW=datetime(2026,10,29,5,20,tzinfo=timezone.utc)


class WorkforceFinalInputGuardTests(unittest.TestCase):
    def fixture(self):
        return {'reviewer':'User','reviewed_at':'2026-10-29T05:10:00Z','lesson_sha256':SOURCE,'audio_sha256':AUDIO,'complete_natural_narration':True,
                'evidence':'SYNTHETIC TEST FIXTURE ONLY: complete narration listening request and Natural and complete response.'}

    def verify(self,record):
        return author.validate_listening_record(record,SOURCE,AUDIO,QA_TIME,NOW)

    def test_complete_url_free_identity_bound_fixture(self):
        self.assertEqual(self.verify(self.fixture())['reviewer'],'User')

    def test_agent_technical_review_cannot_replace_user(self):
        row=self.fixture();row['reviewer']='Codex'
        with self.assertRaisesRegex(AssertionError,'actual User'):
            self.verify(row)

    def test_private_or_public_url_is_not_retained(self):
        for url in ['https'+':'+'//example.invalid/review','file'+':'+'///temporary/audio','localhost review']:
            with self.subTest(url=url):
                row=self.fixture();row['evidence']+=' '+url
                with self.assertRaisesRegex(AssertionError,'URL-free'):
                    self.verify(row)

    def test_incomplete_or_wrong_audio_is_rejected(self):
        for fields in [{'complete_natural_narration':False},{'audio_sha256':'3'*64},{'lesson_sha256':'4'*64}]:
            with self.subTest(fields=fields):
                row=self.fixture();row.update(fields)
                with self.assertRaises(AssertionError):self.verify(row)

    def test_future_or_pre_audio_review_is_rejected(self):
        for time in ['2026-10-29T05:21:00Z','2026-10-29T04:58:00Z']:
            row=self.fixture();row['reviewed_at']=time
            with self.assertRaisesRegex(AssertionError,'chronology'):
                self.verify(row)

    def test_missing_actual_receipt_blocks_before_any_authoring(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(author,'SOURCES',Path(temp)):
                with self.assertRaisesRegex(AssertionError,'has not arrived'):
                    author.listening(SimpleNamespace(),'5'*64)
            self.assertEqual(list(Path(temp).iterdir()),[])

    def test_current_source_preflight_does_not_author_final_inputs(self):
        helper,proposed,_,_,_=author.preflight()
        self.assertEqual((len(proposed['scenes']),proposed['screen_intervals']),(15,35))
        self.assertEqual(helper.FROZEN,'4982c376b8f3a844ae56f2c5dc369d3d16f6d4bdd0c18573cdfaff1826a01129')


if __name__=='__main__':unittest.main()
