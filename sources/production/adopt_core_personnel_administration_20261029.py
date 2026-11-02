"""Review the qualified Personnel take01 canonical candidate; default never writes.

--adopt creates only this previously absent lesson after parent review. All39
other canonical files must still match their exact retained hashes. Root reviews the exact new candidate before adoption; this agent must not invoke
--adopt. Never runs
a website build, target copy, application action, commit or push.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
BASE=SOURCES/'expansion/plans/core-personnel-administration-canonical-adoption-20261029'
TARGET=SOURCES/'expansion/lessons/core-personnel-administration.json'
FROZEN=SOURCES/'expansion/plans/core-personnel-administration-capture-freeze-20261028/core-personnel-administration.narrated-source.json'
EVIDENCE=SOURCES/'expansion/rendered/core-personnel-administration-take-01/evidence.reviewed.json'
QUALIFICATION=EVIDENCE.parent/'qualification.json'
PINS={
 'canonical-candidate.json':'cab79a36a7fba64145082e351b9474ed1aca1f38c1af1e06765803d96dd27aa8',
 'existing-canonical-hashes.json':'15f57c415dfb6878e9f6c46a96f07e07607ec1d5af17d5cc27c603954bc2aa12',
 'learner-copy.review.json':'48d48154e9135448dcf1b85ff000ad82d22d0a8a2ce3deedc340101e138a37cd'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 for name,digest in PINS.items():assert sha(BASE/name)==digest,'Changed reviewed adoption input.'
 assert not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson.'
 assert sha(FROZEN)=='e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8'
 assert sha(EVIDENCE)=='f1018536c36871b0ebc66f87ede61af64d441a53bf6a57722edf7838423b96c3'
 assert sha(QUALIFICATION)=='0360a161c8aea4e6c00e2993c7b62a98fe8c263605d2793a4cbdadb71dbb72b7'
 assert sha(SOURCES/'expansion/audio/core-personnel-administration.listening-review.json')=='025a4cd0d6c4729f2a824739f79d6a805fcfd7dd789dea616693a0aeae33f25b'
 assert sha(SOURCES/'expansion/plans/core-personnel-administration-take-01-final-inputs-20261028/plan.json')=='67b18be443a014e6fef31ada7fbd77fb28ad7bb6a210c29efc0d001a7c442bce'
 baseline=json.loads((BASE/'existing-canonical-hashes.json').read_text())
 expected={str(SOURCES/r['file']):r['sha256'] for r in baseline['files']}
 current={str(p):sha(p) for p in (SOURCES/'expansion/lessons').glob('*.json')}
 assert baseline['existing_lessons']==39 and current==expected,'Another canonical file/count changed; retain this review and obtain a new baseline.'
 frozen=json.loads(FROZEN.read_text());candidate=json.loads((BASE/'canonical-candidate.json').read_text())
 intended=dict(frozen,export_ready=True,publication_mode='video',evidence_file=str(EVIDENCE.relative_to(SOURCES)))
 assert candidate==intended,'Adoption must preserve every frozen learner field.'
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import verify_document
 from expansion_site import lesson_content_digest,_prepare
 evidence=json.loads(EVIDENCE.read_text());report=verify_document(evidence,SOURCES)
 assert report['passed'] and not report['issues'],report
 assert evidence['authoring_sha256']==lesson_content_digest(candidate)==lesson_content_digest(frozen)
 _prepare(candidate,SOURCES)
 return candidate,expected
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--adopt',action='store_true');args=p.parse_args()
 candidate,existing=prepare()
 if args.adopt:
  with TARGET.open('xb') as f:f.write((BASE/'canonical-candidate.json').read_bytes())
  assert all(sha(Path(path))==digest for path,digest in existing.items())
  assert len(list((SOURCES/'expansion/lessons').glob('*.json')))==40
 print(json.dumps({'passed':True,'new_lesson':'core-personnel-administration','candidate_sha256':PINS['canonical-candidate.json'],
  'other39_unchanged':True,'strict_evidence_and_export_preflight':'passed','canonical_written':args.adopt,
  'site_or_target_written':False,'Git_mutation':False}))
if __name__=='__main__':main()
