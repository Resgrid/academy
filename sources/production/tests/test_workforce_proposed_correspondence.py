"""Source-only timing guards; never generate speech, render or touch app data."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
MODULE=Path(__file__).resolve().parents[1]/'prepare_core_workforce_proposed_correspondence_20261029.py'
spec=importlib.util.spec_from_file_location('workforce_proposal',MODULE)
proposal=importlib.util.module_from_spec(spec);spec.loader.exec_module(proposal)
proposal.utility()
from render_walkthrough import load_cues


class WorkforceProposedCorrespondenceTests(unittest.TestCase):
    def inputs(self):
        helper=proposal.utility()
        cues=load_cues(proposal.SOURCES/proposal.CORRECTED)
        anchors,_=helper.service_anchors((proposal.SOURCES/proposal.ANCHORS).read_text())
        return cues,anchors

    def test_actual_source_proposal_preserves126_and_stays_unapproved(self):
        data,_,manifest=proposal.prepare()
        self.assertEqual((len(data['scenes']),len(data['cue_correspondence']),data['source_images'],data['screen_intervals']),(15,126,31,35))
        self.assertTrue(data['parent_timing_review_pending'])
        self.assertFalse(data['renderer_plan_created'])
        self.assertFalse(data['publication_approved'])
        self.assertEqual(len(manifest['screenshots']),31)
        self.assertGreaterEqual(data['minimum_screen_hold_seconds'],2)

    def test_unexported_word_marker_rejected(self):
        cues,anchors=self.inputs()
        with self.assertRaisesRegex(AssertionError,'genuine whole-second'):
            proposal.rebalance(cues,[x for x in anchors if x[0]!=77],proposal.REBALANCE)

    def test_invented_speech_rejected(self):
        cues,anchors=self.inputs()
        changed=[dict(proposal.REBALANCE[0],after_text='filing contacts are verified.')]
        with self.assertRaisesRegex(AssertionError,'Changed spoken words'):
            proposal.rebalance(cues,anchors,changed)

    def test_intervening_gap_is_not_silently_joined(self):
        cues,anchors=self.inputs();cues[12]=dict(cues[12],start=cues[12]['start']+.1)
        with self.assertRaisesRegex(AssertionError,'intervening pauses'):
            proposal.rebalance(cues,anchors,[proposal.REBALANCE[0]])

    def test_offscreen_employment_save_cannot_replace_actual_lower_form(self):
        with patch.dict(proposal.STARTS,{63:18}):
            with self.assertRaisesRegex(AssertionError,'Cue 63'):
                proposal.prepare()

    def test_hash_changed_image_rejected(self):
        real=proposal.sha
        def changed(path):
            return '0'*64 if Path(path).name=='017-employment-volunteer-one-day-period.jpg' else real(path)
        with patch.object(proposal,'sha',changed):
            with self.assertRaisesRegex(AssertionError,'Changed frozen asset'):
                proposal.prepare()


if __name__=='__main__':unittest.main()
