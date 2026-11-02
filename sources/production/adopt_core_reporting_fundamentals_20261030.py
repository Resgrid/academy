"""Guarded Reporting candidate/adoption; default read-only and never builds a site.

Root first runs the separately reviewed qualification recipe. Supply exact new
qualification/evidence hashes for every subsequent operation. --write-candidate
creates a NEW review copy only; --adopt additionally requires its exact hash and
creates only the absent canonical lesson. All41 other lessons must be unchanged.
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
NAME='core-reporting-fundamentals'
BASE=SOURCES/'expansion/plans'/f'{NAME}-release-preparation-20261030'
TARGET=SOURCES/'expansion/lessons'/f'{NAME}.json'
QUALIFIER=SOURCES/'production/qualify_core_reporting_fundamentals_take_01.py'
QUALIFIER_SHA='dd6b0da8e8f483af1377870923d7ef2ecd0aa52949a956878b269575e74fd837'
BASELINE_SHA='5451d04f31ff979cc3286318c5e7ac70e87e7b5a512bc7b36e61c9d896ff6bd3'
LEARNER_SHA='a6234eb5e182d058c02bb55b401661559626e9538b62a05d64041f7b247fe77d'
EVIDENCE_SHA='4d9b40654eae4bc465305d7c1b09051ff41cb26103acf277c3f5fde8c77b0479'
CANDIDATE_SHA='ecb186176785980e45396b46acad50a8059ea53eb3a240b5ee533fc0a36768c8'
QUALIFICATION_SHA='d93fc230fca13fcf0c78fb017654d603c029f7e3e77ce48cdf0299b9625fde87'


def require(condition,message):
    if not condition:raise ValueError(message)


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def baseline():
    require(sha(BASE/'existing-canonical-hashes.json')==BASELINE_SHA,'Changed held41-lesson baseline; obtain a new explicit review, never silently refresh.')
    require(sha(BASE/'learner-copy.review-required.json')==LEARNER_SHA,'Changed learner projection.')
    require(not TARGET.exists() and not TARGET.is_symlink(),'New-only adoption refuses an existing lesson, including symlinks.')
    held=json.loads((BASE/'existing-canonical-hashes.json').read_text())
    expected={str(SOURCES/row['file']):row['sha256'] for row in held['files']}
    current={str(p):sha(p) for p in (SOURCES/'expansion/lessons').glob('*.json')}
    require(held['existing_lessons']==41 and len(expected)==41 and current==expected,'Canonical baseline drifted; preserve all files and seek a new reviewed baseline.')
    require(all(json.loads(Path(path).read_text()).get('id')!=NAME for path in expected),'Duplicate lesson identity already exists under another filename.')
    return expected


def qualifier():
    require(sha(QUALIFIER)==QUALIFIER_SHA,'Qualification recipe changed.')
    spec=importlib.util.spec_from_file_location('reporting_release_qualifier',QUALIFIER)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def prepare(evidence_sha,qualification_sha):
    expected=baseline();q=qualifier()
    rows,evidence,_,source=q.prepare()
    evidence_path=q.TAKE/'evidence.reviewed.json';qualified_path=q.TAKE/'qualification.json'
    require(evidence_sha==EVIDENCE_SHA,'Supply the exact reviewed evidence SHA256.')
    require(qualification_sha==QUALIFICATION_SHA,'Supply the exact retained qualification SHA256 after strict qualification.')
    require(evidence_path.is_file() and qualified_path.is_file(),'Qualification outputs have not arrived; adoption is blocked.')
    require(sha(evidence_path)==evidence_sha and evidence_path.read_bytes()==q.encoded(evidence),'Qualified evidence bytes differ from the pinned actual observations.')
    require(sha(qualified_path)==qualification_sha,'Changed or unreviewed qualification report.')
    require((q.TAKE/'playback/proofs.json').read_bytes()==q.encoded(rows),'Qualified playback observations changed.')
    result=json.loads(qualified_path.read_text())
    require(result['passed'] is True and result['issues']==[] and result['public_export_preflight']=='passed','Qualification/export preflight has not passed.')
    require(result['video_sha256']==q.MASTER and result['evidence_sha256']==evidence_sha and result['authoring_sha256']==q.AUTHORING,'Qualification source/media identity differs.')
    require(result['parent_actual_raw_observations_sha256']==q.RAW_SHA and result['actual_User_listening_receipt_sha256']==q.PINS[q.LISTENING],'Qualification omits actual playback or User review.')
    require(result['rendered_intervals']==27 and result['caption_regions_reviewed']==115 and result['source_images']==23,'Qualification review scope differs.')
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
        print(json.dumps({'read_only_preflight':True,'canonical_target_absent':True,'other41_unchanged':True,'actual_proof_candidate_strict_gate':'passed','root_qualification_and_pinned_output_hashes_required':True,'canonical_written':False,'site_or_target_written':False}));return
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
        require(len(list((SOURCES/'expansion/lessons').glob('*.json')))==42,'Canonical inventory changed during adoption.')
    print(json.dumps({'strict_evidence_and_export_preflight':'passed','candidate_sha256':CANDIDATE_SHA,'candidate_written':args.write_candidate,'canonical_written':args.adopt,'other41_unchanged':True,'site_or_target_written':False,'Git_mutation':False}))


if __name__=='__main__':main()
