"""Freeze the accepted Personnel source set, preserving the native candidate.

Default/--check is read-only. --freeze creates only the named new package and
refuses an existing destination. Reuses the hash-pinned, tested Certification
freezer's correspondence/new-package guards; it never calls that recipe's main.
No browser, application, DB, narration, timing, canonical, readiness or site action.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
CORE=ROOT.parents[2]
NAME='core-personnel-administration'
BASE=Path('expansion/plans/core-personnel-administration-candidate-20261028')
FREEZE=Path('expansion/plans/core-personnel-administration-capture-freeze-20261028')
RAW=Path('captures/expansion/core-personnel-administration-20261028/manifest.json')
REVIEW=Path('captures/expansion/core-personnel-administration-20261028-reviewed/manifest.json')
GUARDS=Path('production/freeze_core_certification_administration_20261028.py')
PINS={
 RAW:'bc40abcc3cba9f8a193b7d9b2a646e1a9c691ae795bc7857ec4f5ddbe3a09192',
 REVIEW:'b06bbf5c331541b5fd20a4f520c0edc750f7bd50f04af4df2e65895dc8cb66d0',
 BASE/'candidate.json':'e044a6466848e9b8c14c7a3b8711cabad0c87c1e9b48c7f7e74476b09b0598b8',
 BASE/'captures.reviewed.json':'b06bbf5c331541b5fd20a4f520c0edc750f7bd50f04af4df2e65895dc8cb66d0',
 BASE/'narration.txt':'aac30cba795f111996ffa610673e723486f3969cbeffd859d700b27113555b0b',
 BASE/'scenario.json':'c6edeb8bb1c7971e9b1f5dc99f5788de4d152b3408c3930b95b21915537cb9ad',
 BASE/'screen-sequence.json':'c2e476a5f078a8aee72b6e41f70a21b443d97df7f52fa70db68c72e8e09153b3',
 BASE/'source-evidence.json':'72c6786690ea7ca38f0228b0ba9a0a97bab1a356c79e66e0d37282fa94d20292',
 BASE/'source-hashes.json':'7c84563623157678e4f2a54e92ddeb60c6879c5cce76d0d479abd3bf34eb1965',
 BASE/'source-review.json':'7ed18430aae4344937bcb72d199dd0ea4aee107a0e1a2e4d17ff1192d97e395d',
 BASE/'source-trace-links.json':'8e70d418eba63a9e206a5c29fee09f0b58edb3a3e31d864a1c2403eaac5e1224',
 Path('production/author_core_personnel_candidate_20261028.py'):'ded41b05e90e266682c5c8ff1d675984f6c9e3289a51847fc5f24752d559ae91',
 GUARDS:'3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2',
 Path('expansion/audits/core-personnel-role-profile-readback-20261028.json'):'6e5a114bc7d3c3ca36e8c1712640dc497da69caa1b5135103b2e9d08319cef1f',
 Path('expansion/audits/core-personnel-administration-source-candidate-preflight-20261028.json'):'9a4b5d7f81ca9507dcac99052cc5244cd16303b5682bcefc520ce4627fd96088',
}
PRESERVED={
 Path('expansion/plans/core-training-administration-capture-freeze-20261028-v2/core-training-administration.narrated-source.json'):'cba97decf7796e64239badb8faed3b0683ec7de2aa8009e63f14bb01ebdbb5ee',
 Path('expansion/plans/core-training-administration-take-01-proposed-derived-20261028/provenance.json'):'eafa0629ab1491f8ac2db49a425ee04706701e6e11ef1e5324b2a31a6b581234',
 Path('expansion/plans/core-certification-administration-capture-freeze-20261028/core-certification-administration.narrated-source.json'):'f141a244ebd9ce37263cfc04e6a0415a6c8febcdf7aa738a3ad2214ddbcbf06d',
 Path('expansion/plans/core-certification-administration-capture-freeze-20261028/source-hashes.json'):'cbaf6b360a8fb0c6f64e3da61e7abac3617ef7af4d8a1cda653e0494e45971e8',
}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def load_guards(sources):
    assert sha(sources/GUARDS)==PINS[GUARDS],'Reviewed guard recipe changed.'
    spec=importlib.util.spec_from_file_location('retained_certification_freeze_guards',sources/GUARDS)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def prepare(sources=SOURCES,core_source=CORE):
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    for path,digest in {**PINS,**PRESERVED}.items():
        assert sha(sources/path)==digest,'Changed retained input: '+str(path)
    guards=load_guards(sources)
    lesson=json.loads((sources/BASE/'candidate.json').read_text())
    sequence=json.loads((sources/BASE/'screen-sequence.json').read_text())
    captures=json.loads((sources/REVIEW).read_text())
    raw=json.loads((sources/RAW).read_text())
    narration=(sources/BASE/'narration.txt').read_text()
    source=json.loads((sources/BASE/'source-evidence.json').read_text())
    assert len(raw)==28 and len(captures['screenshots'])==26 and len(captures['rejected_sources'])==2
    assert {r['id'][:3] for r in captures['rejected_sources']}=={'017','018'}
    raw_by_id={r['id']:r for r in raw}
    assert len(raw_by_id)==28
    for row in raw:
        assert sha(sources/row['file'])==row['sha256'],row['id']
        assert sha(sources/row['dom_file'])==row['dom_sha256'],row['id']
        assert _image_dimensions(sources/row['file'])==(1434,773)
    for row in captures['screenshots']:
        original=raw_by_id[row['id']]
        for key in ['file','sha256','dom_file','dom_sha256','provenance']:
            assert row[key]==original[key],'Reviewed media origin changed.'
        review=row['capture_review']
        assert row['eligible_for_lesson'] and review['passed'] and review['sha256']==row['sha256']
        assert review['controls_sha256']==visible_controls_digest(row['visible_controls'])
    assert len(source['files'])==26
    for row in source['files']:
        assert sha(core_source/row['path'])==row['sha256'],'Cited Core source changed: '+row['path']
    guards.verify_correspondence(lesson,sequence,captures,narration)
    words=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))
    assert words==926 and len(lesson['scenes'])==12 and len(lesson['sector_examples'])==6
    assert all(not ref.startswith(('017-','018-')) for scene in lesson['scenes'] for ref in scene['capture_refs'])
    scenario=json.loads((sources/BASE/'scenario.json').read_text())
    assert scenario['role']['actual_returned_id']==51007 and scenario['role']['members_after']==1
    assert scenario['discarded_preview']['saved'] is False
    assert scenario['global_enforcement']=='Off'
    assert [r['id'] for r in scenario['member']['roles_after']]==[51002,51007]
    review={'kind':'accepted_source_only_personnel_script_review',
      'source_candidate_sha256':PINS[BASE/'candidate.json'],'narration_sha256':PINS[BASE/'narration.txt'],
      'parent_script_review':{'reported_by':'Parent agent /root','accepted':True,
        'basis':'Parent reported reading all926words of narration.txt aac30cba… and accepting the bounded source script.',
        'scope':'Full-script review only. No parent all-original-pixel review is attested or inferred.',
        'human_full_audio_listening':False,'audio_or_video_review':False},
      'independent_source_review':{'reviewer':'Codex source-review agent /root/core_configuration_coverage',
        'reviewed_at':'2026-10-28T23:34:19Z','all_raw_original_size_images_individually_viewed':28,
        'accepted_original_size_images':26,'excluded_original_size_images':2,
        'excluded':'017/018 unreadable narrow member picker; diagnostics only, not used by the learner workflow.',
        'fullDOM_byte_streams_hashed_and_privacy_scanned':28},
      'invariants':{'spoken_words_changed':0,'scenes_changed':0,'six_sector_examples_changed':0,
        'raw_candidate_reviewed_or_proposal_bytes_changed':False,'untimed':True,
        'Training_and_Certification_retained_hashes_reverified':True,
        'narration_media_canonical_readiness_site_app_or_target_changed':False},
      'scope_limits':['013/014 remain unsaved AND/OR previews;015 restored saved single rule.',
        'Long selected requirement type and020new-role option are clipped; complete identity/chips use011/012/021.',
        'Membership uses existing normal profileRoles with Officer retained; full-profile readback comparison is bounded to the35controls in the retained parent audit.',
        '027Qualified is a software result for one fictional rule while globalOff; no professional authorization or Enforce gate claim.']}
    copies={NAME+'.narrated-source.json':'candidate.json',NAME+'.captures.reviewed.json':'captures.reviewed.json',
      NAME+'.screen-sequence.json':'screen-sequence.json','narration.txt':'narration.txt','scenario.json':'scenario.json',
      'source-evidence.json':'source-evidence.json','source-review.json':'source-review.json','source-trace-links.json':'source-trace-links.json'}
    outputs={name:(sources/BASE/original).read_bytes() for name,original in copies.items()}
    outputs['accepted-script-review.json']=encoded(review)
    outputs['source-hashes.json']=encoded({'schema_version':1,'id':NAME,
      'status':'Frozen source-only Personnel input; no audio/timing/video/publication qualification',
      'spoken_words':926,'scenes':12,'six_sectors':6,'raw_pairs_preserved':28,'accepted_sources':26,
      'excluded_source_prefixes':['017','018'],'cited_source_file_pins':26,'source_identity_not_binary_attestation':True,
      'candidate_sha256':PINS[BASE/'candidate.json'],'authoring_sha256':lesson_content_digest(lesson),
      'parent_full_script_review_accepted':True,'parent_all_original_pixel_review_not_attested':True,
      'human_full_audio_listening_review':False,
      'input_files':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      'previous_held_files_reverified':[{'file':p.as_posix(),'sha256':h} for p,h in PRESERVED.items()],
      'outputs':[{'file':p,'sha256':hashlib.sha256(data).hexdigest()} for p,data in outputs.items()],
      'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},
      'guard_recipe':{'file':GUARDS.as_posix(),'sha256':PINS[GUARDS]},
      'write_boundary':'Default/--check reads only. --freeze calls the reviewed new-only guard and refuses an existing destination.',
      'native_candidate_raw_reviewed_and_proposals_preserved':True})
    return outputs,guards

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--core-source',type=Path,default=CORE)
    parser.add_argument('--check',action='store_true',help='Read-only pre/post freeze verification (default).')
    parser.add_argument('--freeze',action='store_true',help='Create only this named new source-only package; refuse existing destination.')
    args=parser.parse_args();outputs,guards=prepare(args.sources.resolve(),args.core_source.resolve())
    destination=args.sources/FREEZE
    if args.freeze:guards.write_new_package(destination,outputs)
    elif destination.exists():
        assert {p.name for p in destination.iterdir()}==set(outputs),'Freeze inventory changed.'
        for name,data in outputs.items():assert (destination/name).read_bytes()==data,'Changed frozen output: '+name
    print(json.dumps({'passed':True,'source_only':True,'words':926,'scenes':12,'six_sectors':6,'reviewed_images':26,
      'raw_pairs_preserved':28,'source_files':26,'Training_Certification_hashes_preserved':True,
      'outputs':len(outputs),'files_written':args.freeze,'canonical_or_ready_changed':False}))

if __name__=='__main__':main()
