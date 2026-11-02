"""Portable guards for the source-only Certification freeze (stdlib only)."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1]/'freeze_core_certification_administration_20261028.py'
SPEC = importlib.util.spec_from_file_location('certification_source_freeze',HELPER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CertificationSourceFreezeTests(unittest.TestCase):
    def fixture(self):
        captures={'screenshots':[{'id':'prepared','file':'prepared.jpg','sha256':'one',
          'visible_labels':['Save'],'eligible_for_lesson':True,'capture_review':{'passed':True}},
          {'id':'stored','file':'stored.jpg','sha256':'two','visible_labels':['Active'],
          'eligible_for_lesson':True,'capture_review':{'passed':True}}]}
        lesson={'scenes':[{'id':'review','narration':'Save, then read Active.',
          'capture_refs':['prepared','stored'],'required_labels':['Save','Active']}]}
        sequence={'scenes':[{'scene_id':'review','narration':'Save, then read Active.',
          'timing':'untimed source-only','screens':[{'capture_id':'prepared','file':'prepared.jpg',
          'sha256':'one','required_labels':['Save']},{'capture_id':'stored','file':'stored.jpg',
          'sha256':'two','required_labels':['Active']}]}]}
        return lesson,sequence,captures,'Save, then read Active.\n'

    def test_exact_source_order_and_words_are_accepted(self):
        MODULE.verify_correspondence(*self.fixture())

    def test_saved_result_cannot_replace_the_control_first_order(self):
        lesson,sequence,captures,narration=self.fixture()
        sequence['scenes'][0]['screens'].reverse()
        with self.assertRaisesRegex(AssertionError,'source order'):
            MODULE.verify_correspondence(lesson,sequence,captures,narration)

    def test_an_unpictured_required_control_is_rejected(self):
        lesson,sequence,captures,narration=self.fixture()
        lesson['scenes'][0]['required_labels'].append('Confirm')
        with self.assertRaisesRegex(AssertionError,'actual scene control'):
            MODULE.verify_correspondence(lesson,sequence,captures,narration)

    def test_source_sequence_cannot_change_the_accepted_words(self):
        lesson,sequence,captures,narration=self.fixture()
        sequence['scenes'][0]['narration']='Save and assume Active.'
        with self.assertRaisesRegex(AssertionError,'Narrated words'):
            MODULE.verify_correspondence(lesson,sequence,captures,narration)

    def test_new_package_never_overwrites_an_existing_freeze(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'freeze'
            MODULE.write_new_package(target,{'narration.txt':b'accepted'})
            with self.assertRaises(FileExistsError):
                MODULE.write_new_package(target,{'narration.txt':b'changed'})
            self.assertEqual((target/'narration.txt').read_bytes(),b'accepted')
            self.assertEqual([p.name for p in target.iterdir()],['narration.txt'])

    def test_escaping_output_is_rejected_before_creating_anything(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'freeze'
            with self.assertRaisesRegex(AssertionError,'Unsafe output'):
                MODULE.write_new_package(target,{'../escaped.txt':b'bad'})
            self.assertFalse(target.exists())
            self.assertFalse((Path(temp)/'escaped.txt').exists())


if __name__=='__main__':
    unittest.main()
