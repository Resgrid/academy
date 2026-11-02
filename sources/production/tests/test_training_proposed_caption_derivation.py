"""Protect actual Training words/anchors and the readable catalog coalescence."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'qa_core_training_proposed_captions_20261028.py'
SPEC=importlib.util.spec_from_file_location('training_proposed_qa',SCRIPT)
QA=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(QA)

class TrainingProposedCaptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.author,cls.proposed,cls.text,cls.original=QA.prepare()

    def test_split_and_merge_preserve_all_frozen_words_and_original97_inputs(self):
        raw=self.author.load_cues(QA.SOURCES/self.author.RAW_FILE)
        self.assertEqual(len(raw),97)
        self.assertEqual(len(self.proposed['cue_correspondence']),99)
        self.assertEqual(self.author.words(' '.join(c['text'] for c in raw)),self.author.words(' '.join(c['text'] for c in self.proposed['cue_correspondence'])))
        self.assertEqual(QA.sha(QA.SOURCES/self.author.RAW_FILE),self.author.RAW)
        for path,digest in QA.PINS.items():self.assertEqual(QA.sha(path),digest)

    def test_catalog_coalescence_uses_same_picture_and_real_adjacent_end(self):
        original=self.author.load_cues(QA.SOURCES/self.author.RAW_FILE)
        merged=next(c for c in self.proposed['cue_correspondence'] if c['raw_cues']==[69,70])
        self.assertEqual(merged['screenshot_id'],'016-training-complete-catalog')
        self.assertEqual(merged['end'],original[69]['end'])
        self.assertEqual(merged['start'],233.0)
        self.assertAlmostEqual(merged['end']-merged['start'],4.719)
        self.assertEqual(len(merged['text'].split()),10)
        self.assertFalse(self.proposed['narration_approved']);self.assertFalse(self.proposed['renderer_plan_created'])

    def test_written99_cues_keep_exact_mapping_times_and_passed_actual_pcm_identity(self):
        derived=QA.DIRECTORY/(QA.NAME+'.derived99.corrected.srt')
        if not derived.exists():self.skipTest('Actual proposed99PCM QA has not run.')
        cues=self.author.load_cues(derived)
        for a,b in zip(cues,self.proposed['cue_correspondence']):
            self.assertEqual((a['start'],a['end'],self.author.words(a['text'])),(b['start'],b['end'],self.author.words(b['text'])))
        report=json.loads((QA.DIRECTORY/(QA.NAME+'.derived99.actual.qa.json')).read_text())
        self.assertTrue(report['passed']);self.assertEqual(report['silent_raw_cues'],0);self.assertEqual(report['silent_corrected_cues'],0)
        self.assertEqual(report['audio']['decoded_samples'],self.original['audio']['decoded_samples'])
        self.assertEqual(report['audio']['sha256'],QA.PINS[QA.AUDIO])
        self.assertEqual(report['alignment']['text_changes'],[])

if __name__=='__main__':unittest.main()
