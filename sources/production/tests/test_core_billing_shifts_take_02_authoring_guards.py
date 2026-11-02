"""Actual-source authoring guards; synthetic approvals stay in memory only."""
import builtins
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/'author_core_billing_shifts_take_02_20261030.py'
sp=importlib.util.spec_from_file_location('billing_shifts_final_guard_tests',P)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
SOURCE='1'*64;AUDIO='2'*64;QA_TIME='2026-10-30T06:00:00Z';NOW=datetime(2026,10,30,7,tzinfo=timezone.utc)


class Take02AuthoringGuards(unittest.TestCase):
    def receipt(self):
        return {'reviewer':'User','reviewed_at':'2026-10-30T06:30:00Z','lesson_sha256':SOURCE,'audio_sha256':AUDIO,'complete_natural_narration':True,'evidence':'SYNTHETIC TEST ONLY: request to hear the full narration, then natural and complete response.'}

    def verify(self,row):return m.validate_listening_record(row,SOURCE,AUDIO,QA_TIME,NOW)

    def test_matching_actual_user_contract_in_memory(self):
        self.assertEqual(self.verify(self.receipt())['reviewer'],'User')

    def test_parent_or_agent_cannot_substitute_for_user(self):
        for reviewer in ['Root','Codex','technical QA']:
            row=self.receipt();row['reviewer']=reviewer
            with self.assertRaisesRegex(ValueError,'actual User'):self.verify(row)

    def test_wrong_media_source_or_incomplete_narration_rejected(self):
        for fields in [{'lesson_sha256':'3'*64},{'audio_sha256':'4'*64},{'complete_natural_narration':False},{'complete_natural_narration':'true'}]:
            row=self.receipt();row.update(fields)
            with self.assertRaises(ValueError):self.verify(row)

    def test_private_links_rejected_even_in_optional_fields(self):
        for value in ['https'+':'+'//example.invalid/private-review','localhost playback','127.0.0.1 review']:
            row=self.receipt();row['extra']={'location':value}
            with self.assertRaisesRegex(ValueError,'URL-free'):self.verify(row)

    def test_review_before_qa_future_or_without_timezone_rejected(self):
        for at in ['2026-10-30T05:59:00Z','2026-10-30T07:01:00Z','2026-10-30T06:30:00']:
            row=self.receipt();row['reviewed_at']=at
            with self.assertRaisesRegex(ValueError,'chronology'):self.verify(row)

    def test_explicit_receipt_hash_required_before_file_read(self):
        with self.assertRaisesRegex(ValueError,'exact genuine User listening receipt SHA256'):m.listening({},None)

    def test_missing_user_receipt_cannot_create_final_inputs(self):
        with tempfile.TemporaryDirectory()as temp:
            cfg=deepcopy(m.CONFIG);cfg['billing']['listening']='does-not-exist.json';cfg['billing']['final']='final'
            data={'config':cfg['billing']}
            with patch.object(m,'S',Path(temp)),patch.object(m,'CONFIG',cfg),patch.object(m,'preflight',return_value=data):
                with self.assertRaisesRegex(ValueError,'has not arrived'):
                    m.main(['--lesson','billing','--assemble','--listening-review-sha256','5'*64])
            self.assertEqual(list(Path(temp).iterdir()),[])

    def test_one_receipt_cannot_approve_both_lessons(self):
        with self.assertRaisesRegex(ValueError,'one lesson'):
            m.main(['--assemble','--listening-review-sha256','5'*64])

    def test_assemble_requires_hash_before_build_or_write(self):
        with patch.object(m,'build',side_effect=AssertionError('assembly attempted')):
            with self.assertRaisesRegex(ValueError,'requires the exact'):
                m.main(['--lesson','shifts','--assemble'])

    def test_existing_final_package_never_overwritten(self):
        with tempfile.TemporaryDirectory()as temp:
            folder=Path(temp)/'held';folder.mkdir();p=folder/'held.bin';p.write_bytes(b'held history')
            with self.assertRaisesRegex(ValueError,'New-only'):
                m.write_new_directory(folder,{'held.bin':b'replaced'})
            self.assertEqual(p.read_bytes(),b'held history');self.assertEqual(list(folder.iterdir()),[p])

    def test_receipt_path_cannot_escape_or_read_private_sources(self):
        for value in ['/tmp/review.json','../private.json','expansion/private/review.json','node_modules/review.json']:
            with self.assertRaises(ValueError):m.receipt_path(m.CONFIG['billing'],value)

    def test_real_parent_acceptance_and_all_caption_references_validate(self):
        for alias in ['billing','shifts']:
            data=m.preflight(alias)
            self.assertEqual(len(data['entries']),m.CONFIG[alias]['cues'])
            self.assertEqual(len(data['proposal']['source_spans']),m.CONFIG[alias]['holds'])
            self.assertTrue(all(any(c['required_labels']for c in scene['captions'])for scene in data['scenes']))
            self.assertEqual(data['duration'],data['qa']['audio']['duration_seconds'])

    def test_changed_parent_cuts_or_proposal_hash_rejected(self):
        data=m.preflight('shifts')
        for key in ['proposal_sha256','accepted_genuine_service_cuts']:
            parent=deepcopy(data['parent']);row=next(x for x in parent['lessons']if x['lesson_id']=='core-shifts-administration')
            row[key]='0'*64 if key=='proposal_sha256'else[]
            with self.assertRaises(ValueError):m.verify_parent(parent,data['proposal'],'shifts',m.CONFIG['shifts'])

    def test_failed_silent_wrong_audio_or_missing_pcm_measurements_rejected(self):
        data=m.preflight('billing');qa=data['qa'];cfg=data['config'];helper=m.retained_helper();raw=helper.cues(m.S/cfg['proposal']/'captions.proposed.srt');checked=helper.cues(m.S/cfg['proposal']/'captions.proposed.checked.srt')
        for change in ['failed','silent','audio','samples']:
            bad=deepcopy(qa)
            if change=='failed':bad['passed']=False
            elif change=='silent':bad['corrected_captions']['energy'][0]['below_threshold']=True
            elif change=='audio':bad['audio']['sha256']='0'*64
            else:bad['audio']['decoded_samples']-=48000
            with self.assertRaises(ValueError):m.verify_audio_qa(bad,raw,checked,data['frozen_sha'],data['audio_sha'],cfg['pins']['captions.proposed.srt'],cfg['pins']['captions.proposed.checked.srt'],cfg['cues'])

    def test_default_reads_only_and_never_imports_renderer_or_optional_libraries(self):
        before={p:m.sha(p)for p in m.S.glob('expansion/lessons/*.json')};real=builtins.__import__
        def guarded_import(name,*args,**kwargs):
            if name.split('.')[0]in {'render_walkthrough','PIL','numpy'}:raise AssertionError('Renderer or optional media dependency imported on read-only preflight.')
            return real(name,*args,**kwargs)
        with patch.object(m,'build',side_effect=AssertionError('assembly attempted')),patch.object(m,'write_new_directory',side_effect=AssertionError('write attempted')),patch('builtins.__import__',side_effect=guarded_import),redirect_stdout(io.StringIO())as output:
            m.main([])
        status=json.loads(output.getvalue());self.assertEqual(len(status),2)
        self.assertTrue(all(x['source_preflight']and not x['final_inputs_written']and not x['renderer_executed']for x in status))
        self.assertEqual(before,{p:m.sha(p)for p in m.S.glob('expansion/lessons/*.json')})


if __name__=='__main__':unittest.main()
