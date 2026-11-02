"""Actual Contacts source correspondence and negative approval/timing guards.

Uses the retained real source/QA exports. No listening approval or successful
media is fabricated; no assembly plan or application state is written.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'author_core_contacts_administration_take_01.py'
SPEC=importlib.util.spec_from_file_location('contacts_author_scaffold',SCRIPT)
AUTHOR=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(AUTHOR)
MEDIA=AUTHOR.SOURCES/AUTHOR.ASSEMBLY/'media-inputs.pending-listening.json'

class ContactsAuthoringScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lesson_path,cls.lesson,cls.manifest,cls.source=AUTHOR.prepare()
        cls.inputs=json.loads(MEDIA.read_text())

    def modified_input(self,mutate):
        temporary=tempfile.TemporaryDirectory(prefix='contacts-negative-source-')
        self.addCleanup(temporary.cleanup)
        path=Path(temporary.name)/'inputs.json';value=copy.deepcopy(self.inputs);mutate(value)
        path.write_text(json.dumps(value));return path,AUTHOR.sha(path)

    def test_default_is_read_only_and_not_renderer_ready(self):
        before=AUTHOR.sha(self.lesson_path)
        result=subprocess.run([sys.executable,str(SCRIPT)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        for key in ['renderer_ready','narration_approved','rendered','canonical_ready']:self.assertFalse(report[key])
        self.assertEqual(AUTHOR.sha(self.lesson_path),before)

    def test_frozen_words_all95_cues_and22_real_images_are_bound(self):
        self.assertEqual((len(self.lesson['scenes']),len(self.source['cues']),len(self.manifest['screenshots'])),(10,95,22))
        self.assertEqual(AUTHOR.sha(self.lesson_path),AUTHOR.FROZEN)
        self.assertEqual(AUTHOR.words(' '.join(c['text'] for c in self.source['cues'])),AUTHOR.words(' '.join(s['narration'] for s in self.lesson['scenes'])))

    def test_added_pixel_observations_do_not_modify_the_frozen_manifest(self):
        original=AUTHOR.SOURCES/AUTHOR.BASE/(AUTHOR.NAME+'.captures.reviewed.json')
        self.assertEqual(AUTHOR.sha(original),AUTHOR.MANIFEST)
        rows={int(r['id'][:3]):r for r in self.manifest['screenshots']}
        self.assertTrue({'Additional Info','Category:','0'}<=set(rows[7]['visible_labels']))
        self.assertIn('Mailing Address',rows[17]['visible_labels'])

    def test_actual_word_markers_produce99_source_cues_without_approving_voice(self):
        _,review,captions,_=AUTHOR.build(MEDIA,AUTHOR.sha(MEDIA),source_review_only=True)
        self.assertIsNone(captions)
        self.assertEqual(review['derived_cues'],99)
        self.assertEqual(AUTHOR.words(' '.join(c['text'] for c in review['cue_correspondence'])),AUTHOR.words(' '.join(s['narration'] for s in self.lesson['scenes'])))
        self.assertFalse(review['renderer_ready']);self.assertFalse(review['narration_approved'])

    def test_assembly_rejects_pending_inputs_without_full_listening_review(self):
        with self.assertRaises(KeyError):AUTHOR.build(MEDIA,AUTHOR.sha(MEDIA))

    def test_changed_approval_input_hash_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'exact reviewed approval-input'):AUTHOR.build(MEDIA,'0'*64,source_review_only=True)

    def test_interpolated_time_is_rejected_even_with_exact_words(self):
        path,digest=self.modified_input(lambda x:x['splits'][0].update(at_seconds=54.1))
        with self.assertRaisesRegex(AssertionError,'genuine transcript marker'):AUTHOR.build(path,digest,source_review_only=True)

    def test_real_marker_at_the_wrong_word_position_is_rejected(self):
        path,digest=self.modified_input(lambda x:x['splits'][0].update(at_seconds=53))
        with self.assertRaisesRegex(AssertionError,'genuine transcript marker'):AUTHOR.build(path,digest,source_review_only=True)

    def test_reordered_spoken_words_are_rejected(self):
        path,digest=self.modified_input(lambda x:x['splits'][0].update(before_text='then Save,'))
        with self.assertRaises(AssertionError):AUTHOR.build(path,digest,source_review_only=True)

    def test_wrong_source_screen_cannot_supply_a_spoken_control(self):
        path,digest=self.modified_input(lambda x:x['splits'][0].update(after_references={'Save':'returned category row'}))
        with self.assertRaises(AssertionError):AUTHOR.build(path,digest,source_review_only=True)

    def test_asset_reference_cannot_escape_sources(self):
        with self.assertRaises(AssertionError):AUTHOR.safe_asset({'file':'../private-outside-test','sha256':'0'*64})

    def test_output_without_hash_bound_listening_inputs_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory(prefix='contacts-unapproved-output-') as temporary:
            path=Path(temporary)/'not-created'/'plan.json'
            result=subprocess.run([sys.executable,str(SCRIPT),'--output',str(path)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Require output plus exact approved-input',result.stderr)
            self.assertFalse(path.parent.exists())

    def test_whole_second_splits_bind_the_exact_srt_parser_serialization(self):
        approved=AUTHOR.SOURCES/AUTHOR.ASSEMBLY/'approved-inputs.json'
        if not approved.exists():self.skipTest('Actual complete listening review has not yet been retained.')
        lesson,plan,_,_=AUTHOR.build(approved,AUTHOR.sha(approved))
        with tempfile.TemporaryDirectory(prefix='contacts-real-plan-check-') as temporary:
            path=Path(temporary)/'actual-input-plan.json';path.write_text(json.dumps(plan))
            checked=AUTHOR.validate_inputs(lesson,path,AUTHOR.SOURCES)
            self.assertEqual(len(checked['cues']),99)
            self.assertEqual(sum(len(s['screens']) for s in checked['scenes']),28)

if __name__=='__main__':unittest.main()
