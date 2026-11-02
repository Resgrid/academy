"""Source-only actual-timing guard tests; no assembly or real app mutation."""
from contextlib import redirect_stdout
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/'prepare_core_billing_shifts_take_02_20261030.py'
spec=importlib.util.spec_from_file_location('billing_shifts_proposed_tests',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class BillingShiftsProposalTests(unittest.TestCase):
    def test_billing_uses_only_actual_boundaries_and_exact_sentence_merge(self):
        p,_=m.propose('billing')
        self.assertEqual((p['raw_cues'],p['proposed_derived_cues'],len(p['source_spans'])),(102,101,19))
        self.assertEqual(p['genuine_service_cuts'],[]);self.assertEqual(p['missing_anchors'],[])
        merged=p['adjacent_same_image_caption_merges']
        self.assertEqual(len(merged),1);self.assertEqual(merged[0]['raw_cues'],[5,6])
        self.assertEqual((merged[0]['start'],merged[0]['end']),(15.659,20.139))
        self.assertEqual(merged[0]['same_screenshot_id'],'001-invoicing-catalog-no-invoices')

    def test_shifts_seven_genuine_marker_cuts_and_same_image_microcue_merges(self):
        p,_=m.propose('shifts')
        self.assertEqual((p['raw_cues'],p['proposed_derived_cues'],len(p['source_spans'])),(116,121,29))
        self.assertEqual([x['seconds']for x in p['genuine_service_cuts']],[37,167,190,247,266,269,311])
        self.assertEqual([x['raw_cue']for x in p['genuine_service_cuts']],[11,52,58,74,80,81,93])
        self.assertEqual([x['raw_cues']for x in p['adjacent_same_image_caption_merges']],[[11,12],[74,75]])
        self.assertTrue(all(x['repeated_previous_source']for x in p['short_source_subspans']))
        self.assertEqual(p['missing_anchors'],[])

    def test_no_unreadable_caption_or_unapproved_final_plan(self):
        for alias in ['billing','shifts']:
            p,files=m.outputs(alias)
            self.assertFalse(any(x['needs_review']for x in p['caption_layout']))
            self.assertFalse(p['complete_User_listening_approved'])
            self.assertTrue(p['parent_timing_review_pending'])
            self.assertFalse(p['final_renderer_plan_created'])
            self.assertNotIn('plan.json',files)
            self.assertFalse(any('listening-review' in n for n in files))

    def test_changed_frozen_input_rejected(self):
        cfg=deepcopy(m.CONFIG);first=next(iter(cfg['billing']['pins']));cfg['billing']['pins'][first]='0'*64
        with patch.object(m,'CONFIG',cfg):
            with self.assertRaisesRegex(ValueError,'Changed retained input'):m.propose('billing')

    def test_invented_visible_control_rejected(self):
        shifts=deepcopy(m.SHIFTS);prefix,capture,_=shifts['minimums'][0];shifts['minimums'][0]=(prefix,capture,['Imaginary approval button'])
        with patch.object(m,'SHIFTS',shifts):
            with self.assertRaisesRegex(ValueError,'Missing source literal'):m.propose('shifts')

    def test_missing_real_anchor_stays_unresolved_without_captions(self):
        real=m.service_anchors
        def without_marker(text):
            words,anchors=real(text);return words,[x for x in anchors if x['seconds']!=247]
        with patch.object(m,'service_anchors',side_effect=without_marker):
            p,files=m.outputs('shifts')
        self.assertEqual(len(p['missing_anchors']),1)
        self.assertEqual(p['missing_anchors'][0]['raw_cue'],74)
        self.assertNotIn('captions.proposed.srt',files)
        self.assertFalse(p['final_renderer_plan_created'])

    def test_marker_outside_real_cue_is_rejected(self):
        actual=[{'cue':1,'word_start':0,'word_end':3,'start':10,'end':12,'text':'one two three'}]
        with self.assertRaisesRegex(ValueError,'outside containing raw cue'):
            m.boundary(1,actual,[{'word_offset':1,'seconds':15,'actual_service_text':'two three'}],3)

    def test_reordered_or_missing_source_span_rejected(self):
        with self.assertRaisesRegex(ValueError,'order changed'):
            m.partition('one two three',[('two','a',[]),('one','b',[])])
        with self.assertRaisesRegex(ValueError,'missing exact source span'):
            m.partition('one two three',[('not recorded','a',[])])

    def test_default_is_read_only(self):
        roots=[m.S/m.CONFIG[x]['out']for x in ['billing','shifts']]
        before={p:p.read_bytes()for root in roots for p in root.rglob('*')if p.is_file()}
        with redirect_stdout(io.StringIO()):m.main([])
        after={p:p.read_bytes()for root in roots for p in root.rglob('*')if p.is_file()}
        self.assertEqual(before,after)

    def test_new_only_refuses_existing_proposal(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);existing=root/m.CONFIG['billing']['out'];existing.mkdir(parents=True)
            marker=existing/'held';marker.write_bytes(b'held history')
            with patch.object(m,'S',root),patch.object(m,'outputs',return_value=({},{})):
                with self.assertRaisesRegex(ValueError,'New-only'):m.main(['--lesson','billing','--write-proposed'])
            self.assertEqual(marker.read_bytes(),b'held history')
            self.assertEqual(list(existing.iterdir()),[marker])

    def test_assembly_switch_is_not_implemented(self):
        with redirect_stdout(io.StringIO()),patch('sys.stderr',io.StringIO()):
            with self.assertRaises(SystemExit):m.main(['--assemble'])


if __name__=='__main__':unittest.main()
