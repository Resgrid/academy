"""Real Training caption/source boundaries and fail-closed source-only authoring."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode=True
SCRIPT=Path(__file__).resolve().parents[1]/'author_core_training_administration_take_01.py'
SPEC=importlib.util.spec_from_file_location('training_author_scaffold',SCRIPT)
AUTHOR=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(AUTHOR)

class TrainingAuthoringScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=AUTHOR.prepare()
        cls.cues=AUTHOR.load_cues(AUTHOR.SOURCES/AUTHOR.RAW_FILE)
        cls.anchors,_=AUTHOR.service_anchors((AUTHOR.SOURCES/AUTHOR.ANCHORS_FILE).read_text())

    def test_all_actual97_cues_ten_scenes_and21_original_sources_are_bound(self):
        self.assertEqual((len(self.source['raw_cue_correspondence']),len(self.source['scene_ranges']),self.source['reviewed_source_images']),(97,10,21))
        lesson=json.loads((AUTHOR.SOURCES/AUTHOR.BASE/(AUTHOR.NAME+'.narrated-source.json')).read_text())
        self.assertEqual(AUTHOR.words(' '.join(c['text'] for c in self.source['raw_cue_correspondence'])),AUTHOR.words(' '.join(s['narration'] for s in lesson['scenes'])))

    def test_default_remains_read_only_and_cannot_approve_audio(self):
        p=AUTHOR.SOURCES/AUTHOR.BASE/(AUTHOR.NAME+'.narrated-source.json');before=AUTHOR.sha(p)
        result=subprocess.run([sys.executable,str(SCRIPT)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        for field in ['renderer_ready','narration_approved','rendered','canonical_ready']:self.assertFalse(report[field])
        self.assertEqual(AUTHOR.sha(p),before)
        self.assertFalse(self.source['derived_srt_written'])

    def test_real_controls_precede_separately_recorded_results(self):
        rows={entry['raw_cue']:entry['screenshot_id'] for entry in self.source['raw_cue_correspondence']}
        self.assertEqual(rows[35],'006-quiz-question-answers-prepared')
        self.assertEqual(rows[38],'007-training-created-catalog')
        self.assertEqual(rows[40],'007-training-created-catalog')
        self.assertEqual(rows[41],'008-training-report-initial')
        self.assertEqual(rows[80],'021-training-second-addition-anchor-state')
        self.assertEqual(rows[81],'022-training-review-handout-saved')

    def test_three_cuts_match_real_service_words_not_duration_ratios(self):
        self.assertEqual([s['at_seconds'] for s in self.source['proposed_genuine_word_cuts']],[191,233,285])
        for split in AUTHOR.SPLITS:self.assertGreaterEqual(min(AUTHOR.check_anchor(split,self.cues,self.anchors)[k] for k in ['before_seconds','after_seconds']),0.7)

    def test_interpolation_and_wrong_word_marker_are_rejected(self):
        for at in [191.1,190]:
            split=copy.deepcopy(AUTHOR.SPLITS[0]);split['at_seconds']=at
            with self.assertRaisesRegex(AssertionError,'genuine whole-second marker'):AUTHOR.check_anchor(split,self.cues,self.anchors)

    def test_changed_or_reordered_words_are_rejected(self):
        split=copy.deepcopy(AUTHOR.SPLITS[0]);split['before_text']='Take Quiz Choose and'
        with self.assertRaisesRegex(AssertionError,'exact spoken order'):AUTHOR.check_anchor(split,self.cues,self.anchors)

    def test_unpictured_control_cannot_be_borrowed_from_another_screen(self):
        with self.assertRaisesRegex(AssertionError,'absent'):
            AUTHOR.references({'text':'Save Training'},{'Save Training':'Save Training'},{'visible_labels':['Take Quiz']})

    def test_assembly_output_flag_is_not_supported_without_actual_qa_and_review(self):
        with tempfile.TemporaryDirectory(prefix='training-unapproved-source-') as temporary:
            target=Path(temporary)/'never-created'/'plan.json'
            result=subprocess.run([sys.executable,str(SCRIPT),'--output',str(target)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('unrecognized arguments',result.stderr)
            self.assertFalse(target.parent.exists())

if __name__=='__main__':unittest.main()
