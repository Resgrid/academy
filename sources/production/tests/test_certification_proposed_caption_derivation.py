"""Protect genuine Certification cuts, original words and practical captions."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'qa_core_certification_proposed_captions_20261028.py'
SPEC=importlib.util.spec_from_file_location('certification_proposed_qa',SCRIPT)
QA=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(QA)

class CertificationProposedCaptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.proposed,cls.text,cls.original=QA.prepare()

    def test_all_original_words_and113_service_cues_are_preserved(self):
        raw=QA.load_cues(QA.SOURCES/QA.RAW)
        self.assertEqual(len(raw),113)
        self.assertEqual(len(self.proposed['cue_correspondence']),114)
        self.assertEqual(QA.words(' '.join(c['text'] for c in raw)),
                         QA.words(' '.join(c['text'] for c in self.proposed['cue_correspondence'])))
        for path,digest in QA.PINS.items():self.assertEqual(QA.sha(QA.SOURCES/path),digest)

    def test_adjacent_file_save_coalescence_has_same_picture_and_real_end(self):
        raw=QA.load_cues(QA.SOURCES/QA.RAW)
        merged=next(c for c in self.proposed['cue_correspondence'] if c['raw_cues']==[54,55])
        self.assertEqual(merged['screenshot_id'],'016-prepared-record-save-ready')
        self.assertEqual((merged['start'],merged['end']),(raw[53]['start'],raw[54]['end']))
        self.assertAlmostEqual(merged['end']-merged['start'],3.541)
        self.assertEqual(merged['text'],'File is optional and remains empty. Save once.')
        self.assertGreaterEqual(min(c['duration_seconds'] for c in self.proposed['readability']),1)
        self.assertFalse(self.proposed['listening_approved'])
        self.assertFalse(self.proposed['renderer_plan_created'])

    def test_invented_subsecond_anchor_and_unreadable_tail_are_rejected(self):
        raw=QA.load_cues(QA.SOURCES/QA.RAW)
        anchors,_=QA.service_anchors((QA.SOURCES/QA.ANCHORS).read_text())
        false=dict(QA.SPLITS[0],at_seconds=122.2)
        with self.assertRaisesRegex(AssertionError,'guessed|interpolated'):
            QA.check_anchor(false,raw,anchors)
        short=dict(QA.SPLITS[0],raw_cue=1)
        with self.assertRaisesRegex(AssertionError,'unreadable'):
            QA.check_anchor(short,[{'start':121.5,'end':123.86,'text':'Use Save, then read the returned catalog row.'}],[(122,2)])

    def test_actual_derived_qa_binds_complete_decode_and_no_silent_cues(self):
        report=QA.DIRECTORY/(QA.NAME+'.derived114.actual.qa.json')
        if not report.exists():self.skipTest('Separate actual derived PCM QA has not run.')
        result=json.loads(report.read_text())
        self.assertTrue(result['passed']);self.assertEqual(result['issues'],[])
        self.assertEqual(result['audio']['sha256'],QA.PINS[QA.AUDIO])
        self.assertEqual(result['audio']['decoded_samples'],self.original['audio']['decoded_samples'])
        self.assertEqual(result['audio']['duration_seconds'],self.original['audio']['duration_seconds'])
        self.assertEqual(result['silent_raw_cues'],0);self.assertEqual(result['silent_corrected_cues'],0)
        self.assertEqual(result['alignment']['text_changes'],[])
        corrected=QA.load_cues(QA.DIRECTORY/(QA.NAME+'.derived114.corrected.srt'))
        self.assertEqual(len(corrected),114)
        for measured,proposed in zip(corrected,self.proposed['cue_correspondence']):
            self.assertEqual((measured['start'],measured['end'],QA.words(measured['text'])),
                             (proposed['start'],proposed['end'],QA.words(proposed['text'])))

if __name__=='__main__':unittest.main()
