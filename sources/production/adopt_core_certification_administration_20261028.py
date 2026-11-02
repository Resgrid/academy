"""Review Certification's new canonical candidate; default never writes.

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
BASE=SOURCES/'expansion/plans/core-certification-administration-canonical-adoption-20261028'
TARGET=SOURCES/'expansion/lessons/core-certification-administration.json'
FROZEN=SOURCES/'expansion/plans/core-certification-administration-capture-freeze-20261028/core-certification-administration.narrated-source.json'
EVIDENCE=SOURCES/'expansion/rendered/core-certification-administration-take-01/evidence.reviewed.json'
QUALIFICATION=EVIDENCE.parent/'qualification.json'
PINS={
 'canonical-candidate.json':'f054575a728a581b37e546734376e86c6efe3f2a1704edc63fdbd863dc496685',
 'existing-canonical-hashes.json':'c2d71d0fff6de9c687696ea69cc0f73df9424b14606103f146c2f3e636228837',
 'learner-copy.review.json':'d390315c3d83b0957b6db79aeb8abca21195f43e6cc0486366507bd67d55af18'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 for name,digest in PINS.items():assert sha(BASE/name)==digest,'Changed reviewed adoption input.'
 assert not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson.'
 assert sha(FROZEN)=='f141a244ebd9ce37263cfc04e6a0415a6c8febcdf7aa738a3ad2214ddbcbf06d'
 assert sha(EVIDENCE)=='b1e56e6d574f5c1029936a9e267ab9ec425a15ac3719cd79bcd6830405aa6a3a'
 assert sha(QUALIFICATION)=='0eeca4dfef243719b898384feb3a3e6f9dfdaa8efedc39fb1077e147691f2ba6'
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
