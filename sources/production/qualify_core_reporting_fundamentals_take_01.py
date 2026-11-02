"""Review Reporting take01 against genuine pinned parent playback; default read-only.

--qualify creates NEW reviewed evidence/proofs/qualification only after all strict
checks. It requires the exact supplied raw-proof hash. No canonical/site/target
write, browser, application action, rendering or Git operation occurs here.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-reporting-fundamentals'
TAKE = SOURCES / 'expansion/rendered' / (NAME+'-take-01')
FROZEN = SOURCES / 'expansion/plans' / (NAME+'-capture-freeze-20261029') / (NAME+'.narrated-source.json')
PLAN = SOURCES / 'expansion/plans' / (NAME+'-take-01-final-inputs-20261029') / 'plan.json'
RAW = ROOT / '_reports/reporting-browser-proof-20261030.raw.json'
RAW_SHA = 'ddd2cfaaba52b5bc2b5a4c6c57cb089f22ee19c798f30548286719c5315da04e'
MASTER = '371993c6ace208ec5cbebf011495aa457bc010e816871d17dec37944c83c4f29'
AUTHORING = '514cc8a78c4d11f8ea5d473619860a0580282f0e5baf7b5bd458f3edc23ed71f'
LISTENING = SOURCES / 'expansion/audio' / (NAME+'.listening-review.json')
PINS = {
    FROZEN: '9df3ae7d5998b85bf989e744e70aee5f8d93bb1212497def4631aaf661411fd7',
    PLAN: '5f882f1547abcc3feec749c265eab51ac279d0723628afa2a75bea9665b22441',
    TAKE / 'evidence.frames-reviewed.json': '448b44ebcf977f68ec5e0b78c3736b8c0f20bcdb768715108946431807d6f024',
    TAKE / (NAME+'.mp4'): MASTER,
    TAKE / 'frame-source-comparison.json': '7e3c591f224420e1921181b412d31a2af92f890ee3ef7129a06ff15e42706e9c',
    TAKE / 'cue-frame-check.json': 'de3b550bdd296b85b082fba59b643ce6a8cfac01d0e05a269be9fe6a5a33a92a',
    TAKE / 'encoded-audio.qa.json': '2e53d323fc4d1c2549d90fc7a9771e81e0a5472ffafc5a07b37abec6cc243568',
    SOURCES / 'expansion/audits/core-reporting-take-01-actual-frame-observations-20261029.json': '8cc1cd52d83b888d55a0cee3c98b9472a6897f2da86a4ba594b8db6388e06d9c',
    LISTENING: '4608121148c195f0cd6859f7747279c9b40cf4c0afc77de328c9b2ab31a7cefd',
    ROOT / 'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
    ROOT / 'scripts/expansion_site.py': 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8',
}
EXPECTED = [
    ('beginning',12.965433,26.725899,'4340337ac180b9790fc3fbdfd15e84487cb6974d3d0df64563c47980a5f349ff'),
    ('middle',216.08508,236.752184,'941b20fac67264dc6c084f7da189052c5b41de4c9ee24f2c30d7875bd0db486c'),
    ('end',397.59646,407.91363,'752de4cd399070a6560bc17990b9d7235c987f287766ba0b77c9faec365ce46f'),
]


def require(condition, message):
    if not condition: raise ValueError(message)


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''): digest.update(block)
    return digest.hexdigest()


def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def validate_observations(rows, asset_root=SOURCES):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions
    require(isinstance(rows,list) and len(rows)==3, 'Require exactly3 actual beginning/middle/end observations.')
    result=deepcopy(rows)
    for row,(position,previous,current,digest) in zip(result,EXPECTED):
        require((row.get('position'),row.get('previous_time'),row.get('current_time'),row.get('video_sha256'),row.get('screenshot',{}).get('sha256'))==(position,previous,current,MASTER,digest), 'Changed or stale actual playback observation.')
        require(row.get('ready_state')==4 and row.get('network_state')==1 and row.get('paused') is False and row.get('ended') is False, 'Playback is not the retained ready/advancing observation.')
        require(row.get('media_error','missing') is None and row.get('console_errors')==[], 'Playback contains an unresolved error.')
        require((row.get('video_width'),row.get('video_height'))==(1920,1080) and current>previous, 'Wrong video dimensions or nonadvancing time.')
        path=(Path(asset_root)/row['screenshot']['file']).resolve()
        require(path.is_relative_to(Path(asset_root).resolve()), 'Playback screenshot escaped the source root.')
        require(sha(path)==digest, 'Actual playback JPEG bytes changed.')
        width,height=_image_dimensions(path)
        require((width,height)==(1280,720), 'Unexpected actual playback JPEG header dimensions.')
        row['screenshot'].update(width=width,height=height)
    return result


def prepare():
    require(__debug__, 'Use ordinary Python; retained strict validators contain assertions.')
    for path,digest in PINS.items(): require(sha(path)==digest,'Changed pinned qualification input: '+str(path))
    require(RAW.is_file(), 'Genuine parent playback observations have not arrived.')
    require(sha(RAW)==RAW_SHA, 'Changed parent playback observations; preserve and obtain a new review.')
    rows=validate_observations(json.loads(RAW.read_text()))
    source=json.loads(FROZEN.read_text())
    heard=json.loads(LISTENING.read_text())
    require(heard.get('reviewer')=='User' and heard.get('complete_natural_narration') is True and heard.get('lesson_sha256')==PINS[FROZEN], 'Actual User listening receipt does not match.')
    plan=json.loads(PLAN.read_text())
    require(heard.get('audio_sha256')==plan['narration']['sha256'], 'Listening receipt identifies different narration audio.')
    for name,key,count in [('frame-source-comparison.json','intervals_checked',27),('cue-frame-check.json','cues_checked',115)]:
        review=json.loads((TAKE/name).read_text())
        require(review['passed'] is True and review['video_sha256']==MASTER and review[key]==count, 'Incomplete encoded source/caption check.')
    qa=json.loads((TAKE/'encoded-audio.qa.json').read_text())
    require(qa['passed'] is True and not qa['issues'] and qa['audio']['sha256']==MASTER and qa['audio']['full_decode']=='passed' and qa['silent_raw_cues']==qa['silent_corrected_cues']==0, 'Encoded audio QA failed.')
    evidence=json.loads((TAKE/'evidence.frames-reviewed.json').read_text())
    require(len(evidence['screenshots'])==23 and len(evidence['scenes'])==13 and len(evidence['rendered_segments'])==27, 'Frame evidence scope changed.')
    require(sum(len(x['captions']) for x in evidence['scenes'])==115, 'Caption review scope changed.')
    require(evidence['browser_playback']==[], 'Historical frames-only evidence must remain unchanged.')
    evidence['browser_playback']=rows
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import verify_document
    from expansion_site import lesson_content_digest
    require(lesson_content_digest(source)==AUTHORING, 'Frozen learner authoring digest changed.')
    evidence['authoring_sha256']=AUTHORING
    evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':False,
        'parent_raw_observation_sha256':RAW_SHA,
        'review':'Root personally observed all3 advancing/error-free actual native IAB playback screens and current captions. This source agent independently viewed all3 exact1280x720 JPEGs at original size. This source agent personally inspected all27 actual1920x1080 encoded holds and115 actual caption regions at full width, in addition to the exact3 playback JPEGs. Full encoded audio decode, exact-script and cue-energy checks passed; these do not replace the genuine User listening receipt. Private QA nativeCC duplication is intentional; public nativeCC remains off.',
        'canonical_or_ready_changed':False}
    report=verify_document(evidence,SOURCES)
    require(report['passed'] and not report['issues'], 'Strict capture evidence gate failed: '+json.dumps(report))
    return rows,evidence,report,source


def candidate(source):
    return dict(source,export_ready=True,publication_mode='video',evidence_file=str((TAKE/'evidence.reviewed.json').relative_to(SOURCES)))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualify',action='store_true')
    parser.add_argument('--proof-observations-sha256')
    args=parser.parse_args(argv)
    rows,evidence,report,source=prepare()
    from expansion_site import _prepare
    targets=[TAKE/'playback/proofs.json',TAKE/'evidence.reviewed.json',TAKE/'qualification.json']
    if args.qualify:
        require(args.proof_observations_sha256==RAW_SHA, 'Mutation requires the exact reviewed raw-proof SHA256 argument.')
        require(all(not p.exists() and not p.is_symlink() for p in targets), 'New-only qualification refuses existing outputs.')
        for path,value in zip(targets[:2],[rows,evidence]):
            with path.open('xb') as stream: stream.write(encoded(value))
        _prepare(candidate(source),SOURCES)
        qualified={'passed':True,'lesson_id':NAME,'issues':[],'public_export_preflight':'passed',
            'frozen_source_sha256':PINS[FROZEN],'authoring_sha256':AUTHORING,'video_sha256':MASTER,
            'evidence_sha256':sha(targets[1]),'proofs_sha256':sha(targets[0]),'parent_actual_raw_observations_sha256':RAW_SHA,
            'actual_User_listening_receipt_sha256':PINS[LISTENING],
            'rendered_intervals':27,'caption_regions_reviewed':115,'source_images':23,
            'current_validator_sha256':PINS[ROOT/'scripts/verify_capture_evidence.py'],
            'current_exporter_sha256':PINS[ROOT/'scripts/expansion_site.py'],
            'root_canonical_adoption_pending':True,'canonical_site_target_or_Git_changed':False}
        with targets[2].open('xb') as stream: stream.write(encoded(qualified))
    elif targets[1].exists():
        require(targets[1].read_bytes()==encoded(evidence), 'Existing qualified evidence changed.')
        require(targets[0].read_bytes()==encoded(rows), 'Existing qualified playback rows changed.')
        _prepare(candidate(source),SOURCES)
    print(json.dumps({'strict_evidence_candidate_passed':True,'qualified_outputs_written':args.qualify,
        'sources':23,'holds':27,'caption_regions':115,'browser_proofs':3,'authoring_sha256':AUTHORING,
        'predicted_evidence_sha256':hashlib.sha256(encoded(evidence)).hexdigest(),
        'qualification_sha256':sha(targets[2]) if targets[2].is_file() else None,
        'canonical_or_site_changed':False}))


if __name__=='__main__': main()
