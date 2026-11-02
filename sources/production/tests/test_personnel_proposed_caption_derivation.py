"""Actual Personnel caption/source guards; no optional imaging dependency."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from portable_test_evidence import retained_core_sources

path=Path(__file__).resolve().parents[1]/'qa_core_personnel_proposed_captions_20261028_v2.py'
spec=importlib.util.spec_from_file_location('personnel_proposed',path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class PersonnelProposedCaptionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.enterClassContext(retained_core_sources(m))
  cls.proposed,cls.text,cls.qa=m.prepare()

 def test_exact_words_and_observed_markers_only(self):
  p=self.proposed
  self.assertEqual((p['original_raw_cues'],p['proposed_derived_cues'],p['screen_intervals']),(112,116,38))
  self.assertEqual(p['renderer_normalized_words'],932)
  self.assertEqual([c['at_seconds']for c in p['genuine_service_anchor_cuts']],[72,82,112,314,319])
  self.assertGreaterEqual(min(c['duration_seconds']for c in p['readability']),1)
  self.assertLessEqual(max(c['characters_per_second']for c in p['readability']),22)
  self.assertTrue(p['parent_timing_review_pending']);self.assertFalse(p['renderer_plan_created'])

 def test_short_tail_merges_unchanged_words_on_same_admin_screen(self):
  h=m.utility()
  from render_walkthrough import load_cues,words
  raw=load_cues(m.SOURCES/m.RAW)
  tail=next(c for c in self.proposed['cue_correspondence']if c['raw_cues']==[75,76])
  self.assertEqual(words(tail['text']),words(raw[74]['text'])+words(raw[75]['text']))
  self.assertEqual((tail['start'],tail['end']),(raw[74]['start'],raw[75]['end']))
  self.assertEqual(tail['screenshot_id'],'022-profile-admin-flags-and-save-unchanged')
  self.assertEqual(self.proposed['coalescence']['raw76_seconds'],0.95)

 def test_casey_hold_ends_at_next_real_cue_start(self):
  from render_walkthrough import load_cues
  raw=load_cues(m.SOURCES/m.RAW)
  c=next(c for c in self.proposed['cue_correspondence']if c['raw_cues']==[95]and c['start']==314)
  self.assertEqual(c['end'],raw[95]['start'])
  self.assertEqual(c['screenshot_id'],'026-role-view-saved-casey-member')
  self.assertEqual(self.proposed['caption_gap_hold']['actual_gap_seconds'],0.451)

 def test_catalog_launchers_precede_actual_readbacks_and_return(self):
  p=self.proposed['cue_correspondence']
  for cue,images in {23:[5,6],25:[6,16],34:[8,9],95:[28,26],96:[28,27]}.items():
   self.assertEqual([int(c['screenshot_id'][:3])for c in p if c['raw_cues']==[cue]],images)
  scene=next(s for s in self.proposed['scenes']if s['scene_id']=='verify-member')
  self.assertEqual([int(s['capture_ref'][:3])for s in scene['source_spans']],[23,28,26,28,27])
  self.assertFalse(any(int(c['screenshot_id'][:3])in(17,18)for c in p))

 def test_changed_original_service_caption_rejected(self):
  with patch.dict(m.PINS,{m.RAW:'0'*64}):
   with self.assertRaisesRegex(AssertionError,'Changed retained input'):m.prepare()


if __name__=='__main__':unittest.main()
