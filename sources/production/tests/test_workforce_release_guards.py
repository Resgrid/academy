"""Source-only Workforce release tests; never qualify/adopt real assets."""
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from portable_test_evidence import retained_playback_raw

PRODUCTION=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PRODUCTION.parents[1]/'scripts'))


def load(name,file):
    spec=importlib.util.spec_from_file_location(name,PRODUCTION/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


qual=load('workforce_release_test_qualifier','qualify_core_workforce_foundations_take_01.py')
adopt=load('workforce_release_test_adopter','adopt_core_workforce_foundations_20261029.py')


def snapshot_tree(root):
    if root.is_symlink():
        return ('symlink',str(root.readlink()))
    if not root.exists():
        return None
    return {path.relative_to(root).as_posix():
            ('symlink',str(path.readlink())) if path.is_symlink() else
            ('directory',) if path.is_dir() else ('file',adopt.sha(path))
            for path in sorted(root.rglob('*'))}


@contextmanager
def isolated_adoption_state():
    """Exercise the historical forty-lesson guard without touching today's catalog."""
    with tempfile.TemporaryDirectory(prefix='academy-workforce-adoption-') as directory:
        root=Path(directory);sources=root/'sources';base=root/'release'
        canonical=sources/'expansion/lessons';canonical.mkdir(parents=True);base.mkdir()
        rows=[]
        for index in range(40):
            path=canonical/f'fixture-{index:02}.json'
            path.write_bytes(adopt.encoded({'id':f'synthetic-baseline-{index:02}'}))
            rows.append({'file':path.relative_to(sources).as_posix(),'sha256':adopt.sha(path)})
        baseline=base/'existing-canonical-hashes.json'
        baseline.write_bytes(adopt.encoded({'existing_lessons':40,'files':rows}))
        learner=base/'learner-copy.review-required.json'
        learner.write_bytes(adopt.encoded({'id':'synthetic-learner-projection-no-media'}))
        target=canonical/(adopt.NAME+'.json')
        with patch.object(adopt,'SOURCES',sources),patch.object(adopt,'BASE',base),\
                patch.object(adopt,'TARGET',target),\
                patch.object(adopt,'BASELINE_SHA',adopt.sha(baseline)),\
                patch.object(adopt,'LEARNER_SHA',adopt.sha(learner)):
            yield SimpleNamespace(root=root,sources=sources,canonical=canonical,base=base,target=target)


class WorkforceReleaseGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enterClassContext(retained_playback_raw(qual))

    def test_actual_three_proofs_and_strict_candidate_pass_without_writes(self):
        paths=[qual.TAKE/'evidence.reviewed.json',qual.TAKE/'playback/proofs.json',qual.TAKE/'qualification.json',adopt.TARGET]
        before={p:(p.read_bytes() if p.exists() else None) for p in paths}
        rows,evidence,report,_=qual.prepare()
        self.assertTrue(report['passed']);self.assertEqual(report['issues'],[])
        self.assertEqual(len(rows),3)
        self.assertTrue(all((x['screenshot']['width'],x['screenshot']['height'])==(1280,720) for x in rows))
        self.assertEqual(evidence['authoring_sha256'],qual.AUTHORING)
        self.assertEqual(before,{p:(p.read_bytes() if p.exists() else None) for p in paths})

    def test_stale_video_or_jpeg_and_missing_position_rejected(self):
        real=json.loads(qual.RAW.read_text())
        for which in ['video','jpeg','position','missing']:
            with self.subTest(which=which):
                rows=deepcopy(real)
                if which=='video':rows[0]['video_sha256']='0'*64
                elif which=='jpeg':rows[1]['screenshot']['sha256']='0'*64
                elif which=='position':rows[2]['position']='beginning'
                else:rows.pop()
                with self.assertRaises(ValueError):qual.validate_observations(rows)

    def test_paused_or_error_observation_cannot_qualify(self):
        real=json.loads(qual.RAW.read_text())
        for fields in [{'paused':True},{'ended':True},{'media_error':{'code':3}},{'console_errors':['synthetic test error']}]:
            rows=deepcopy(real);rows[0].update(fields)
            with self.assertRaises(ValueError):qual.validate_observations(rows)

    def test_qualification_write_requires_explicit_pinned_proof_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(qual,'TAKE',Path(temp)),patch.object(qual,'prepare',return_value=([],{}, {},{})):
                with self.assertRaisesRegex(ValueError,'exact reviewed raw-proof'):
                    qual.main(['--qualify'])
            self.assertEqual(list(Path(temp).iterdir()),[])

    def test_qualification_refuses_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            take=Path(temp);old=take/'evidence.reviewed.json';old.write_bytes(b'held synthetic history')
            with patch.object(qual,'TAKE',take),patch.object(qual,'prepare',return_value=([],{}, {},{})):
                with self.assertRaisesRegex(ValueError,'New-only'):
                    qual.main(['--qualify','--proof-observations-sha256',qual.RAW_SHA])
            self.assertEqual(old.read_bytes(),b'held synthetic history')
            self.assertEqual([p.name for p in take.iterdir()],['evidence.reviewed.json'])

    def test_missing_real_qualification_blocks_adoption(self):
        with isolated_adoption_state() as state:
            before=snapshot_tree(state.root)
            fake=SimpleNamespace(TAKE=state.root/'absent-qualification',prepare=lambda:([],{}, {},{}))
            with patch.object(adopt,'qualifier',return_value=fake):
                with self.assertRaisesRegex(ValueError,'have not arrived'):
                    adopt.prepare(adopt.EVIDENCE_SHA,'a'*64)
            self.assertEqual(snapshot_tree(state.root),before)

    def test_duplicate_target_refused_without_changing_existing_lesson(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'existing.json';target.write_bytes(b'held existing lesson')
            with patch.object(adopt,'TARGET',target):
                with self.assertRaisesRegex(ValueError,'existing lesson'):adopt.baseline()
            self.assertEqual(target.read_bytes(),b'held existing lesson')

    def test_canonical_baseline_drift_is_rejected(self):
        with isolated_adoption_state() as state:
            self.assertEqual(len(adopt.baseline()),40)
            changed=next(state.canonical.glob('*.json'))
            changed.write_bytes(changed.read_bytes()+b'\n')
            before=snapshot_tree(state.root)
            with self.assertRaisesRegex(ValueError,'baseline drifted'):adopt.baseline()
            self.assertEqual(snapshot_tree(state.root),before)

    def test_adoption_mutation_requires_exact_qualification_hashes(self):
        with isolated_adoption_state() as state:
            before=snapshot_tree(state.root)
            with self.assertRaisesRegex(ValueError,'exact qualified evidence/report'):
                adopt.main(['--adopt'])
            self.assertEqual(snapshot_tree(state.root),before)

    def test_both_defaults_are_read_only_and_preserve_current_catalog(self):
        canonical=adopt.SOURCES/'expansion/lessons'
        before=snapshot_tree(canonical)
        with redirect_stdout(io.StringIO()) as output:qual.main([])
        self.assertFalse(json.loads(output.getvalue())['qualified_outputs_written'])
        # Adoption remains intentionally new-only. Its historical default is
        # exercised against an isolated valid pre-adoption baseline, while the
        # real current catalog may legitimately contain the adopted lesson.
        with isolated_adoption_state() as state,patch.object(adopt,'qualifier',return_value=qual):
            held=snapshot_tree(state.root)
            with redirect_stdout(io.StringIO()) as output:adopt.main([])
            self.assertFalse(json.loads(output.getvalue())['canonical_written'])
            self.assertEqual(snapshot_tree(state.root),held)
            self.assertEqual(len(list(state.canonical.glob('*.json'))),40)
        self.assertEqual(snapshot_tree(canonical),before)


if __name__=='__main__':unittest.main()
