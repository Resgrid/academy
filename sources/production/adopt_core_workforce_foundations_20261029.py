"""Guarded Workforce candidate/adoption; default read-only and never builds a site.

Root first runs the separately reviewed qualification recipe. Supply exact new
qualification/evidence hashes for every subsequent operation. --write-candidate
creates a NEW review copy only; --adopt additionally requires its exact hash and
creates only the absent canonical lesson. All40 other lessons must be unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-workforce-foundations-unapproved-time'
BASE=SOURCES/'expansion/plans'/f'{NAME}-release-preparation-20261029'
TARGET=SOURCES/'expansion/lessons'/f'{NAME}.json'
QUALIFIER=SOURCES/'production/qualify_core_workforce_foundations_take_01.py'
QUALIFIER_SHA='b3ba30c4e401e15a60196803fc97f25a15d2025946697eb327322b8a79f33cf3'
BASELINE_SHA='698e6fad9be610e35ce617aad514137b8efd93df290c75e7f6db8fc6fb064bea'
LEARNER_SHA='316709c08e7a7198849d55fe48af708fdfd7c5e74055fe72a94384dd9a0314b4'
EVIDENCE_SHA='45c389952b8f37150c4509aaca9af1f9871e7a21229f5277d920e75adbfaa50a'
CANDIDATE_SHA='53d6dbd7f80084132e1a0dccf029dd9d4d8ab215559cdb3b791667ff16bf310c'


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def baseline():
    require(sha(BASE/'existing-canonical-hashes.json')==BASELINE_SHA,'Changed held40-lesson baseline; obtain a new explicit review, never silently refresh.')
    require(sha(BASE/'learner-copy.review-required.json')==LEARNER_SHA,'Changed learner projection.')
    require(not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson, including symlinks.')
    held=json.loads((BASE/'existing-canonical-hashes.json').read_text())
    expected={str(SOURCES/row['file']):row['sha256'] for row in held['files']}
    current={str(p):sha(p) for p in (SOURCES/'expansion/lessons').glob('*.json')}
    require(held['existing_lessons']==40 and len(expected)==40 and current==expected,'Canonical baseline drifted; preserve all files and seek a new reviewed baseline.')
    require(all(json.loads(Path(path).read_text()).get('id')!=NAME for path in expected),'Duplicate lesson identity already exists under another filename.')
    return expected


def qualifier():
    require(sha(QUALIFIER)==QUALIFIER_SHA,'Qualification recipe changed.')
    spec=importlib.util.spec_from_file_location('workforce_release_qualifier',QUALIFIER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def prepare(evidence_sha,qualification_sha):
    expected=baseline();q=qualifier()
    rows,evidence,_,source=q.prepare()
    evidence_path=q.TAKE/'evidence.reviewed.json';qualified_path=q.TAKE/'qualification.json'
    require(evidence_sha==EVIDENCE_SHA,'Supply the exact reviewed evidence SHA256.')
    require(isinstance(qualification_sha,str) and len(qualification_sha)==64 and all(c in '0123456789abcdef' for c in qualification_sha),'Supply the exact real qualification SHA256 after root qualification.')
    require(evidence_path.is_file() and qualified_path.is_file(),'Qualification outputs have not arrived; adoption is blocked.')
    require(sha(evidence_path)==evidence_sha and evidence_path.read_bytes()==q.encoded(evidence),'Qualified evidence bytes differ from the pinned actual observations.')
    require(sha(qualified_path)==qualification_sha,'Changed or unreviewed qualification report.')
    require((q.TAKE/'playback/proofs.json').read_bytes()==q.encoded(rows),'Qualified playback observations changed.')
    result=json.loads(qualified_path.read_text())
    require(result['passed'] is True and result['issues']==[] and result['public_export_preflight']=='passed','Qualification/export preflight has not passed.')
    require(result['video_sha256']==q.MASTER and result['evidence_sha256']==evidence_sha and result['authoring_sha256']==q.AUTHORING,'Qualification source/media identity differs.')
    require(result['parent_actual_raw_observations_sha256']==q.RAW_SHA and result['actual_User_listening_receipt_sha256']==q.PINS[q.LISTENING],'Qualification omits actual playback or User review.')
    require(result['rendered_intervals']==35 and result['caption_regions_reviewed']==126 and result['source_images']==31,'Qualification review scope differs.')
    candidate=q.candidate(source)
    require(hashlib.sha256(encoded(candidate)).hexdigest()==CANDIDATE_SHA,'Unreviewed learner fields or publication metadata changed.')
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest,_prepare
    require(lesson_content_digest(candidate)==q.AUTHORING,'Candidate changed frozen learner content.')
    _prepare(candidate,SOURCES)
    return candidate,expected


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--write-candidate',action='store_true')
    modes.add_argument('--adopt',action='store_true')
    parser.add_argument('--evidence-sha256')
    parser.add_argument('--qualification-sha256')
    parser.add_argument('--candidate-sha256')
    args=parser.parse_args(argv)
    baseline()
    if not args.evidence_sha256 or not args.qualification_sha256:
        require(not args.adopt and not args.write_candidate,'Mutation requires exact qualified evidence/report hashes.')
        q=qualifier();q.prepare()
        print(json.dumps({'read_only_preflight':True,'canonical_target_absent':True,'other40_unchanged':True,'actual_proof_candidate_strict_gate':'passed','root_qualification_and_pinned_output_hashes_required':True,'canonical_written':False,'site_or_target_written':False}));return
    candidate,expected=prepare(args.evidence_sha256,args.qualification_sha256)
    path=BASE/'canonical-candidate.json'
    if args.write_candidate:
        require(not path.exists() and not path.is_symlink(),'New-only candidate refuses an existing review copy.')
        with path.open('xb') as stream:stream.write(encoded(candidate))
    if args.adopt:
        require(args.candidate_sha256==CANDIDATE_SHA,'Adoption requires the exact candidate hash after root review.')
        require(path.is_file() and sha(path)==CANDIDATE_SHA and path.read_bytes()==encoded(candidate),'Held candidate review copy differs or is missing.')
        with TARGET.open('xb') as stream:stream.write(path.read_bytes())
        require(all(sha(Path(p))==digest for p,digest in expected.items()),'An existing canonical file changed during adoption; inspect before any build.')
        require(len(list((SOURCES/'expansion/lessons').glob('*.json')))==41,'Canonical inventory changed during adoption.')
    print(json.dumps({'strict_evidence_and_export_preflight':'passed','candidate_sha256':CANDIDATE_SHA,'candidate_written':args.write_candidate,'canonical_written':args.adopt,'other40_unchanged':True,'site_or_target_written':False,'Git_mutation':False}))


if __name__=='__main__':main()
