"""Review the qualified Groups/Units take01 canonical candidate; default never writes.

--adopt creates only this previously absent lesson after parent review. All37
other canonical files must still match their exact retained hashes. Root currently holds this recipe for a fixed two-candidate batch against the
same37baseline; this agent must not invoke --adopt. Never runs
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
BASE=SOURCES/'expansion/plans/core-groups-units-administration-canonical-adoption-20261028'
TARGET=SOURCES/'expansion/lessons/core-groups-units-administration.json'
FROZEN=SOURCES/'expansion/plans/core-groups-units-administration-capture-freeze-20261028/core-groups-units-administration.narrated-source.json'
EVIDENCE=SOURCES/'expansion/rendered/core-groups-units-administration-take-01/evidence.reviewed.json'
QUALIFICATION=EVIDENCE.parent/'qualification.json'
PINS={
 'canonical-candidate.json':'10f5e6ecb6368c651f2e2f6caea96e68eea37b0fc4cee4ceb4bc08dc9709ab62',
 'existing-canonical-hashes.json':'cbb0c2a9bdf854271de19edb3e7abb7aafeefc6c649fcf3a612788256184c83c',
 'learner-copy.review.json':'ac48c18e1c83f4c5105ffbd99e1e9dd1f8fd7547b25f6b1b42f955143e48cb38'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 for name,digest in PINS.items():assert sha(BASE/name)==digest,'Changed reviewed adoption input.'
 assert not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson.'
 assert sha(FROZEN)=='56b13d11be889d0825950a2cb33c0453c51302872939788ee03c6d1fd7bfee5c'
 assert sha(EVIDENCE)=='faa235b25acb8b826ecaaecfd5a38601b3438a63d2766a7745f2e83c4804a709'
 assert sha(QUALIFICATION)=='af6daadd89aab98aaebaf2157079a1e7de3619d6a1691f8b5a6f601d4f124554'
 assert sha(SOURCES/'expansion/audio/core-groups-units-administration.listening-review.json')=='7b2ff52ceeecc526669a9e707cba49af87fe304d2d3b152c472d63359fec0e56'
 assert sha(SOURCES/'expansion/plans/core-groups-units-administration-take-01-final-inputs-20261028/plan.json')=='383acc572ab1c52f0d791bbcc44dea24506718aee35e2d4522196ff6be07f6e9'
 baseline=json.loads((BASE/'existing-canonical-hashes.json').read_text())
 expected={str(SOURCES/r['file']):r['sha256'] for r in baseline['files']}
 current={str(p):sha(p) for p in (SOURCES/'expansion/lessons').glob('*.json')}
 assert baseline['existing_lessons']==37 and current==expected,'Another canonical file/count changed; retain this review and obtain a new baseline.'
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
  assert len(list((SOURCES/'expansion/lessons').glob('*.json')))==38
 print(json.dumps({'passed':True,'new_lesson':'core-groups-units-administration','candidate_sha256':PINS['canonical-candidate.json'],
  'other37_unchanged':True,'strict_evidence_and_export_preflight':'passed','canonical_written':args.adopt,
  'site_or_target_written':False,'Git_mutation':False}))
if __name__=='__main__':main()
