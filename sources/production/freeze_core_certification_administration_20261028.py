"""Freeze the accepted Certification source set without changing its content.

Default/--check is read-only. --freeze creates only the named new package and
refuses an existing destination. All 28 raw pairs, 27 accepted images, 36 cited
Core files and the reviewed untimed narration/sequence must match retained pins.
No narration service, renderer, canonical lesson, readiness, site or app changes.
Use --core-source for a checkout of the pinned Core source-profile head.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
CORE = ROOT.parents[2]
NAME = 'core-certification-administration'
BASE = Path('expansion/plans/core-certification-administration-candidate-20261028')
FREEZE = Path('expansion/plans/core-certification-administration-capture-freeze-20261028')
RAW = Path('captures/expansion/core-certification-administration-20261028/manifest.json')
REVIEW = Path('captures/expansion/core-certification-administration-20261028-reviewed/manifest.json')
PINS = {
    RAW: '72ed387d579edea9547914e46f8b08f1695c10028e2d1a6f0a2353a7243d308e',
    REVIEW: '032953a6cc969b85f6dd2ca8ede133c72f80b1410c6e5b44d8cb46fc63a4fc68',
    BASE/'candidate.json': 'f141a244ebd9ce37263cfc04e6a0415a6c8febcdf7aa738a3ad2214ddbcbf06d',
    BASE/'captures.reviewed.json': '032953a6cc969b85f6dd2ca8ede133c72f80b1410c6e5b44d8cb46fc63a4fc68',
    BASE/'narration.txt': 'bb98211620cee00d1f1790c24d10f464017ab673798ead7d3f2cea2a4f45016c',
    BASE/'scenario.json': '3d6bed475770f92b2e6cc4a56193b0241fc2b0277cf2318af70973f4907df24b',
    BASE/'screen-sequence.json': '8337c73c3bbe486b0c91bd1adf2e9c767166f3bdcb38d5914759f1dc064e7a50',
    BASE/'source-correspondence.json': '995c531d6bd480718eab0e6392a4dc0c9380657d242dd786a4a3ddf93f4e9bd6',
    BASE/'source-evidence.json': '37b7296d0174033eac886c665716f432c2610f63b18e2d7b386b82738b2c4b0e',
    BASE/'source-hashes.json': '58d2ecac6f8abd86d5456547d59d7ae8508c7049c7e162cfffdf598b09286dee',
    BASE/'source-review.json': '2e35f7b65cc73f4f4cb0d459d6df9d3466edbe9491f50a30e26d9a9d8dd42e34',
    Path('production/author_core_certification_candidate_20261028.py'): '51cb0e44cba71dc16b48ab92de6665ab6a1d8ea6175deaaaca99399a543ce92e',
    Path('expansion/audits/core-certification-administration-source-candidate-preflight-20261028.json'): '5bdd8f886b5c0ff522abeb8629918434603da6e66d79ddd07e5ac034d9030717',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()

def verify_correspondence(lesson, sequence, captures, narration):
    """Check actual source order, exact paragraphs and foreground label coverage."""
    by_id = {r['id']:r for r in captures['screenshots']}
    assert len(by_id) == len(captures['screenshots']), 'Duplicate reviewed capture IDs.'
    assert len(sequence['scenes']) == len(lesson['scenes']), 'Scene count changed.'
    for scene, row in zip(lesson['scenes'], sequence['scenes']):
        assert row['scene_id'] == scene['id'], 'Scene order changed.'
        assert row['narration'] == scene['narration'], 'Narrated words changed.'
        assert [x['capture_id'] for x in row['screens']] == scene['capture_refs'], 'Control/result source order changed.'
        labels = set()
        for screen in row['screens']:
            actual = by_id[screen['capture_id']]
            assert actual['eligible_for_lesson'] and actual['capture_review']['passed'], 'Unreviewed source.'
            assert screen['file'] == actual['file'] and screen['sha256'] == actual['sha256'], 'Source identity changed.'
            assert set(screen['required_labels']) <= set(actual['visible_labels']), 'Invisible screen label.'
            labels.update(actual['visible_labels'])
        assert set(scene['required_labels']) <= labels, 'Missing actual scene control.'
        assert 'untimed' in row['timing'], 'Source freeze must remain untimed.'
    assert narration == '\n\n'.join(s['narration'] for s in lesson['scenes'])+'\n', 'Paragraph or word order changed.'

def prepare(sources=SOURCES, core_source=CORE):
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions, visible_controls_digest
    for path, digest in PINS.items():
        assert sha(sources/path) == digest, 'Changed accepted input: '+str(path)
    lesson = json.loads((sources/BASE/'candidate.json').read_text())
    captures = json.loads((sources/REVIEW).read_text())
    sequence = json.loads((sources/BASE/'screen-sequence.json').read_text())
    narration = (sources/BASE/'narration.txt').read_text()
    raw = json.loads((sources/RAW).read_text())
    source = json.loads((sources/BASE/'source-evidence.json').read_text())
    assert len(raw) == 28 and len(captures['screenshots']) == 27 and len(captures['rejected_sources']) == 1
    assert captures['rejected_sources'][0]['id'].startswith('025-')
    assert len(source['files']) == 36
    for row in raw:
        assert sha(sources/row['file']) == row['sha256'], row['id']
        assert sha(sources/row['dom_file']) == row['dom_sha256'], row['id']
        assert _image_dimensions(sources/row['file']) == (1434,773), row['id']
    raw_by_id = {r['id']:r for r in raw}
    for row in captures['screenshots']:
        original = raw_by_id[row['id']]
        for key in ['file','sha256','dom_file','dom_sha256','provenance']:
            assert row[key] == original[key], 'Reviewed source bytes or origin changed.'
        review = row['capture_review']
        assert review['passed'] and review['sha256'] == row['sha256']
        assert review['controls_sha256'] == visible_controls_digest(row['visible_controls'])
    for row in source['files']:
        assert sha(core_source/row['path']) == row['sha256'], 'Cited Core source changed: '+row['path']
    profile = source['expansion_profile_manifest']
    assert sha(sources/profile['file']) == profile['sha256'], 'Expansion source profile changed.'
    verify_correspondence(lesson,sequence,captures,narration)
    words = len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))
    assert words == 956 and len(lesson['scenes']) == 12 and len(lesson['sector_examples']) == 6
    scenario = json.loads((sources/BASE/'scenario.json').read_text())
    assert scenario['new_record']['member'] == 'Matthew Casey'
    assert scenario['new_record']['verified_by'] == 'Wallace Boden'
    assert scenario['preserved_policy']['enforcement_mode'] == 'Off'
    assert scenario['preserved_policy']['settings_saved'] is False
    parent_review = {
      'kind':'accepted_source_only_certification_script_review',
      'source_candidate_sha256':PINS[BASE/'candidate.json'], 'narration_sha256':PINS[BASE/'narration.txt'],
      'parent_script_review':{'reported_by':'Parent agent /root','basis':'Parent read all956 narrated words and compared recent actual raw views with the retained source trace.',
        'accepted':True,'accepted_scope':'Control-first operations, six-sector examples, and historical zero-requirement/type-editability limits before a later separate Personnel exercise.',
        'human_full_audio_listening':False,'audio_or_video_review':False},
      'independent_source_review':{'reviewer':'Codex source-review agent /root/core_configuration_coverage',
        'reviewed_at':'2026-10-28T23:08:42Z','all_raw_original_size_images_viewed':28,
        'accepted_original_size_images':27,'rejected_original_size_images':1,'full_dom_files_reviewed':28,
        'rejected':'025 wrong Edit type foreground/DOM/provenance, not a report. Actual027 is the only report source.'},
      'invariants':{'words_changed':0,'scenes_changed':0,'six_sector_examples_changed':0,'raw_or_reviewed_media_changed':False,
        'untimed':True,'narration_audio_created':False,'canonical_or_readiness_or_site_changed':False},
      'replay_scope':'Use the retained guarded manual scenario with an own fictional type and another fictional member. No self-verification, policy commit, role assignment, template application, provider action or automatic seed.',
      'historical_boundary':'022–024 record1/requirement0/editableCode are the state captured before a later separate Personnel role-requirement exercise. These images do not claim the later live type still has zero requirements.',
    }
    copies = {
      NAME+'.narrated-source.json':'candidate.json', NAME+'.captures.reviewed.json':'captures.reviewed.json',
      NAME+'.screen-sequence.json':'screen-sequence.json','narration.txt':'narration.txt',
      'scenario.json':'scenario.json','source-correspondence.json':'source-correspondence.json',
      'source-evidence.json':'source-evidence.json','source-review.json':'source-review.json',
    }
    outputs = {name:(sources/BASE/original).read_bytes() for name,original in copies.items()}
    outputs['accepted-script-review.json'] = encoded(parent_review)
    outputs['source-hashes.json'] = encoded({
      'schema_version':1,'id':NAME,'status':'Frozen source-only input; no narration audio, timing, video or publication qualification',
      'spoken_words':956,'scenes':12,'reviewed_sources':27,'raw_pairs_preserved':28,'source_file_pins':36,
      'candidate_sha256':PINS[BASE/'candidate.json'],'authoring_sha256':lesson_content_digest(lesson),
      'core_source_profile_head':source['core_head'],'source_identity_is_not_runtime_binary_attestation':True,
      'parent_script_review_accepted':True,'full_human_audio_listening_review':False,
      'input_files':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      'outputs':[{'file':name,'sha256':hashlib.sha256(data).hexdigest()} for name,data in outputs.items()],
      'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},
      'source_candidate_raw_and_historical_trace_preserved':True,
      'write_boundary':'--freeze creates this named new package only; existing destination is refused. Default/--check reads only.',
    })
    return outputs

def write_new_package(destination, outputs):
    # Check every filename before any write; there are no caller-selected app or
    # canonical paths. Never overwrite a historical package or follow a symlink.
    assert outputs and all(Path(name).name == name and name not in {'.','..'} for name in outputs), 'Unsafe output filename.'
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Existing freeze preserved; default/--check verifies it without writing.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.mkdir(exist_ok=False)
    for name,data in outputs.items():
        with (destination/name).open('xb') as stream:
            stream.write(data)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--core-source',type=Path,default=CORE)
    parser.add_argument('--check',action='store_true',help='Read-only verification (default).')
    parser.add_argument('--freeze',action='store_true',help='Create only the named new source-only freeze; refuse existing packages.')
    args=parser.parse_args()
    outputs=prepare(args.sources.resolve(),args.core_source.resolve())
    destination=args.sources/FREEZE
    if args.freeze:
        write_new_package(destination,outputs)
    elif destination.exists():
        assert {p.name for p in destination.iterdir()} == set(outputs), 'Freeze file inventory changed.'
        for name,data in outputs.items():
            assert (destination/name).read_bytes() == data, 'Changed frozen output: '+name
    print(json.dumps({'passed':True,'source_only':True,'words':956,'scenes':12,'reviewed_images':27,'raw_pairs':28,
      'source_files':36,'outputs':len(outputs),'files_written':args.freeze,'canonical_or_ready_changed':False}))

if __name__=='__main__':
    main()
