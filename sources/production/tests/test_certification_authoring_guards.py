"""Final Certification assembly must not infer or accept stale listening review."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'author_core_certification_administration_take_01_v2.py'
SPEC=importlib.util.spec_from_file_location('certification_final_author',SCRIPT)
AUTHOR=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(AUTHOR)

class CertificationAuthoringGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.prepared=AUTHOR.prepare()

    def test_readonly_prepare_has_no_final_package_side_effect(self):
        final=AUTHOR.SOURCES/AUTHOR.ASSEMBLY
        before={str(p):p.read_bytes() for p in final.rglob('*') if p.is_file()} if final.exists() else None
        AUTHOR.prepare()
        after={str(p):p.read_bytes() for p in final.rglob('*') if p.is_file()} if final.exists() else None
        self.assertEqual(before,after)

    def test_outside_review_is_rejected_without_a_package(self):
        with tempfile.TemporaryDirectory() as temp:
            review=Path(temp)/'not-approved.json';review.write_text('{}')
            with self.assertRaisesRegex(AssertionError,'inside sources'):
                AUTHOR.build(review,hashlib.sha256(review.read_bytes()).hexdigest())

    def test_incomplete_or_wrong_audio_review_cannot_author_inputs(self):
        helper,_,_=self.prepared
        # Deliberately invalid synthetic metadata only; never approval evidence.
        examples=[{'complete_natural_narration':False},
                  {'complete_natural_narration':True,'audio_sha256':'0'*64,'lesson_sha256':helper.FROZEN}]
        for payload in examples:
            with self.subTest(payload=payload),tempfile.TemporaryDirectory() as temp:
                root=Path(temp);review=root/'invalid-listening.json';review.write_text(json.dumps(payload))
                with patch.object(AUTHOR,'SOURCES',root),patch.object(AUTHOR,'prepare',return_value=self.prepared):
                    with self.assertRaises(AssertionError):AUTHOR.build(review,hashlib.sha256(review.read_bytes()).hexdigest())
                self.assertEqual(list(root.iterdir()),[review])

    def test_outro_field_reference_is_on_actual_derived105_only(self):
        review=AUTHOR.SOURCES/'expansion/audio/core-certification-administration.listening-review.json'
        if not review.exists():self.skipTest('Actual full listening review has not been retained.')
        _,plan,_,_=AUTHOR.build(review,hashlib.sha256(review.read_bytes()).hexdigest())
        outro=plan['scenes'][-1]['captions'];by_number={c['cue']:c for c in outro}
        self.assertEqual(by_number[104]['required_labels'],[])
        self.assertEqual(by_number[105]['spoken_references'],
                         {'TRAINING ONLY - Software record review':'exercise record'})
        self.assertEqual(by_number[105]['screenshot_id'],'020-active-verified-fresh-readback')
        self.assertEqual(plan['v2_metadata_correction']['raw_cue'],104)
        self.assertEqual(plan['v2_metadata_correction']['derived_cue'],105)

if __name__=='__main__':unittest.main()
