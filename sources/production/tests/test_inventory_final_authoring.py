"""Actual Inventory approval identities and renderer-plan fail-closed guards."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'author_core_inventory_movements_take_01_final.py'
SPEC=importlib.util.spec_from_file_location('inventory_final_author',SCRIPT)
AUTHOR=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(AUTHOR)
INPUTS=AUTHOR.SOURCES/'expansion/plans/core-inventory-movements-take-01-approved-assembly-20261028/approved-inputs.json'

class InventoryFinalAuthoringTests(unittest.TestCase):
    def mutated(self,change):
        temporary=tempfile.TemporaryDirectory(prefix='inventory-approval-negative-');self.addCleanup(temporary.cleanup)
        p=Path(temporary.name)/'inputs.json';value=json.loads(INPUTS.read_text());change(value);p.write_text(json.dumps(value));return p,AUTHOR.sha(p)

    def test_actual_approved_inputs_preserve_all93_cues_and16_source_intervals(self):
        lesson,plan,mapping=AUTHOR.build(INPUTS,AUTHOR.sha(INPUTS))
        self.assertEqual((len(plan['scenes']),sum(len(s['screens']) for s in plan['scenes']),len(mapping['captions'])),(12,16,93))
        self.assertFalse(plan['publishable']);self.assertFalse(mapping['publication_approved'])
        self.assertEqual(AUTHOR.sha(AUTHOR.PEER),AUTHOR.PEER_SHA)
        self.assertEqual(AUTHOR.sha(lesson),'261b4f3f205e38e0579e96ac24bdd56c600c41c708d3987fb498c3155866975c')

    def test_changed_input_or_audio_hash_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'approved-input'):AUTHOR.build(INPUTS,'0'*64)
        p,digest=self.mutated(lambda x:x['audio'].update(sha256='0'*64))
        with self.assertRaisesRegex(AssertionError,'Changed reviewed asset'):AUTHOR.build(p,digest)

    def test_missing_actual_listening_review_cannot_be_inferred_from_qa(self):
        p,digest=self.mutated(lambda x:x.pop('listening_review'))
        with self.assertRaises(KeyError):AUTHOR.build(p,digest)

    def test_another_actual_lesson_listening_review_does_not_approve_this_audio(self):
        other=AUTHOR.SOURCES/'expansion/audio/core-contacts-administration.listening-review.json'
        p,digest=self.mutated(lambda x:x.update(listening_review={'file':str(other.relative_to(AUTHOR.SOURCES)),'sha256':AUTHOR.sha(other)}))
        with self.assertRaises(AssertionError):AUTHOR.build(p,digest)

    def test_raw_srt_cannot_replace_the_actual_qa_bound_corrected_caption_asset(self):
        raw=AUTHOR.SOURCES/'expansion/audio/core-inventory-movements-generated-20261028.raw.srt'
        p,digest=self.mutated(lambda x:x.update(captions={'file':str(raw.relative_to(AUTHOR.SOURCES)),'sha256':AUTHOR.sha(raw)}))
        with self.assertRaises(AssertionError):AUTHOR.build(p,digest)

    def test_public_asset_path_cannot_escape_sources(self):
        with self.assertRaisesRegex(AssertionError,'within public sources'):AUTHOR.asset({'file':'../outside-approval-test','sha256':'0'*64})

    def test_output_without_required_approval_arguments_creates_nothing(self):
        with tempfile.TemporaryDirectory(prefix='inventory-unapproved-plan-') as temporary:
            p=Path(temporary)/'never-created'/'plan.json';result=subprocess.run([sys.executable,str(SCRIPT),'--output',str(p)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertFalse(p.parent.exists())

if __name__=='__main__':unittest.main()
