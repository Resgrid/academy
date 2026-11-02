"""Review Certification's current take02 canonical candidate; default never writes.

--adopt creates only this previously absent lesson after parent review. All36
other canonical files must still match their exact retained hashes. Never runs
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
BASE=SOURCES/'expansion/plans/core-certification-administration-canonical-adoption-20261028-v2'
TARGET=SOURCES/'expansion/lessons/core-certification-administration.json'
FROZEN=SOURCES/'expansion/plans/core-certification-administration-capture-freeze-20261028/core-certification-administration.narrated-source.json'
EVIDENCE=SOURCES/'expansion/rendered/core-certification-administration-take-02/evidence.reviewed.json'
QUALIFICATION=EVIDENCE.parent/'qualification.json'
PINS={
 'canonical-candidate.json':'2dc86c5cf366f663969a12eea9950fa6efb7773f04059d17104fb90e7a77dc41',
 'existing-canonical-hashes.json':'c2d71d0fff6de9c687696ea69cc0f73df9424b14606103f146c2f3e636228837',
 'learner-copy.review.json':'d390315c3d83b0957b6db79aeb8abca21195f43e6cc0486366507bd67d55af18'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 for name,digest in PINS.items():assert sha(BASE/name)==digest,'Changed reviewed adoption input.'
 assert not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson.'
 assert sha(FROZEN)=='f141a244ebd9ce37263cfc04e6a0415a6c8febcdf7aa738a3ad2214ddbcbf06d'
 assert sha(EVIDENCE)=='12c94c8fc6e7fff5f763123d9c4d726cac0afb169add607a61115c3ff03a18e3'
 assert sha(QUALIFICATION)=='c818964bbd1e6ac548cf81934bad86f2eb33a7356cbb9d5c536d8f51b528719b'
 assert sha(SOURCES/'expansion/audio/core-certification-administration.listening-review.json')=='cd55feaa6d87b7037da10c5edcd8e7361751ebf84b765a2a404e8fa5b41af1db'
 assert sha(SOURCES/'expansion/plans/core-certification-administration-take-01-final-inputs-20261028-v3/plan.json')=='f81b35dfb19f63e4f2e25e57aceb009aab92533e68742454106d9a1085202be3'
 baseline=json.loads((BASE/'existing-canonical-hashes.json').read_text())
 expected={str(SOURCES/r['file']):r['sha256'] for r in baseline['files']}
 current={str(p):sha(p) for p in (SOURCES/'expansion/lessons').glob('*.json')}
 assert baseline['existing_lessons']==36 and current==expected,'Another canonical file/count changed; retain this review and obtain a new baseline.'
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
  assert len(list((SOURCES/'expansion/lessons').glob('*.json')))==37
 print(json.dumps({'passed':True,'new_lesson':'core-certification-administration','candidate_sha256':PINS['canonical-candidate.json'],
  'other36_unchanged':True,'strict_evidence_and_export_preflight':'passed','canonical_written':args.adopt,
  'site_or_target_written':False,'Git_mutation':False}))
if __name__=='__main__':main()
