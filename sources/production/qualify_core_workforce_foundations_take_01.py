"""Review Workforce take01 against genuine pinned parent playback; default read-only.

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
NAME = 'core-workforce-foundations-unapproved-time'
TAKE = SOURCES / 'expansion/rendered' / (NAME+'-take-01')
FROZEN = SOURCES / 'expansion/plans' / (NAME+'-capture-freeze-20261029') / (NAME+'.narrated-source.json')
PLAN = SOURCES / 'expansion/plans' / (NAME+'-take-01-final-inputs-20261029') / 'plan.json'
RAW = ROOT / '_reports/workforce-browser-proof-20261029.raw.json'
RAW_SHA = '1be3f881fba1cb6d3046459d4b98c91f13a730e44aa8c9070b8763d46aa489c6'
MASTER = '0b86ac0b872e5ac9e995d210f2ecf0efedef3ae1ed01fc7cd07eef77ea3e47b2'
AUTHORING = 'a4e2b839ebf0d2e6a94b26bb1d5b5304abc9ebbe016f62bb7399e1a42c0af4a1'
LISTENING = SOURCES / 'expansion/audio' / (NAME+'.listening-review.json')
PINS = {
    FROZEN: '4982c376b8f3a844ae56f2c5dc369d3d16f6d4bdd0c18573cdfaff1826a01129',
    PLAN: '0d5a61919605ec67771e5e6ff893aa91957268f64c66d6b4d8329c4222be1e9b',
    TAKE / 'evidence.frames-reviewed.json': '0e283cec3d2b84596f1f58ef8f1ce30b1998994144f03ae58539b70cc15c1468',
    TAKE / (NAME+'.mp4'): MASTER,
    TAKE / 'frame-source-comparison.json': 'c6dcfdb2a659c66f7c5f50c9fbce952d50e7c78ba14051b4e6695f493a11ebb8',
    TAKE / 'cue-frame-check.json': '782d0ee3f39edf013e710d62374f7c1eb246c2dca860638916b7766b9bc1ee2c',
    TAKE / 'encoded-audio.qa.json': '100428951bde11ddc9b60208c0abd4f25cefe2ebb3dd492da54346a50d7c8bab',
    SOURCES / 'expansion/audits/core-workforce-take-01-actual-frame-observations-20261029.json': 'cf6aec4930c5c73659bfe6f1fe67492d88acf75171fbe16a77804cb5da0e2777',
    LISTENING: 'dc3288253e046f2c34aa8ebbda884811c75f525c9f9c9e92f276aaa9a2bfb3f1',
    ROOT / 'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa',
    ROOT / 'scripts/expansion_site.py': 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8',
}
EXPECTED = [
    ('beginning',13.405084,20.266116,'27aa71238c18eaaf17c88bab94c4c5386bea59cf3a00c3fbdda028e4ae37327b'),
    ('middle',223.416732,229.739424,'ce57884bab709c3211b78469d2c8160ef6e249e5f8572b0642a88683a580971d'),
    ('end',411.086717,417.140507,'c0ee8223fda52829fcc7ae117af0c9576201b95b3cd2b93810e841e4fe4bc0b8'),
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
    for name,key,count in [('frame-source-comparison.json','intervals_checked',35),('cue-frame-check.json','cues_checked',126)]:
        review=json.loads((TAKE/name).read_text())
        require(review['passed'] is True and review['video_sha256']==MASTER and review[key]==count, 'Incomplete encoded source/caption check.')
    qa=json.loads((TAKE/'encoded-audio.qa.json').read_text())
    require(qa['passed'] is True and not qa['issues'] and qa['audio']['sha256']==MASTER and qa['audio']['full_decode']=='passed' and qa['silent_raw_cues']==qa['silent_corrected_cues']==0, 'Encoded audio QA failed.')
    evidence=json.loads((TAKE/'evidence.frames-reviewed.json').read_text())
    require(len(evidence['screenshots'])==31 and len(evidence['scenes'])==15 and len(evidence['rendered_segments'])==35, 'Frame evidence scope changed.')
    require(sum(len(x['captions']) for x in evidence['scenes'])==126, 'Caption review scope changed.')
    require(evidence['browser_playback']==[], 'Historical frames-only evidence must remain unchanged.')
    evidence['browser_playback']=rows
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import verify_document
    from expansion_site import lesson_content_digest
    require(lesson_content_digest(source)==AUTHORING, 'Frozen learner authoring digest changed.')
    evidence['authoring_sha256']=AUTHORING
    evidence['qualification_review']={'frame_review_complete':True,'browser_playback_pending':False,
        'parent_raw_observation_sha256':RAW_SHA,
        'review':'Root personally observed all3 advancing/error-free actual native IAB playback screens and current captions. This source agent independently viewed all3 exact1280x720 JPEGs at original size. Retained peer review covers35 actual encoded holds and126 actual caption regions; this recipe does not claim a second review of those frames. Private QA nativeCC duplication is intentional; public nativeCC remains off.',
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
            'rendered_intervals':35,'caption_regions_reviewed':126,'source_images':31,
            'current_validator_sha256':PINS[ROOT/'scripts/verify_capture_evidence.py'],
            'current_exporter_sha256':PINS[ROOT/'scripts/expansion_site.py'],
            'root_canonical_adoption_pending':True,'canonical_site_target_or_Git_changed':False}
        with targets[2].open('xb') as stream: stream.write(encoded(qualified))
    elif targets[1].exists():
        require(targets[1].read_bytes()==encoded(evidence), 'Existing qualified evidence changed.')
        require(targets[0].read_bytes()==encoded(rows), 'Existing qualified playback rows changed.')
        _prepare(candidate(source),SOURCES)
    print(json.dumps({'strict_evidence_candidate_passed':True,'qualified_outputs_written':args.qualify,
        'sources':31,'holds':35,'caption_regions':126,'browser_proofs':3,'authoring_sha256':AUTHORING,
        'predicted_evidence_sha256':hashlib.sha256(encoded(evidence)).hexdigest(),
        'qualification_sha256':sha(targets[2]) if targets[2].is_file() else None,
        'canonical_or_site_changed':False}))


if __name__=='__main__': main()
