"""Freeze accepted Groups/Units source bytes; default/--check is read-only.

--freeze creates only the named new package through the retained tested new-only
guard, refusing an existing destination. No application, narration, timing,
canonical, readiness, website, target or Git operation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]; SOURCES=ROOT/'sources'; CORE=ROOT.parents[2]
NAME='core-groups-units-administration'
BASE=Path('expansion/plans/core-groups-units-administration-candidate-20261028')
FREEZE=Path('expansion/plans/core-groups-units-administration-capture-freeze-20261028')
RAW=Path('captures/expansion/core-groups-units-administration-20261028/manifest.json')
REVIEW=Path('captures/expansion/core-groups-units-administration-20261028-reviewed/manifest.json')
GUARDS=Path('production/freeze_core_certification_administration_20261028.py')
PINS={RAW:'e9e15926ce3e965702edbde126d9450cc1aa71ed236c56f54259ea9847ccce0b',
 REVIEW:'655294154349fd715cb5396315d27448cbd481502e52e777f9e82622628a1e3f',
 BASE/'candidate.json':'56b13d11be889d0825950a2cb33c0453c51302872939788ee03c6d1fd7bfee5c',
 BASE/'captures.reviewed.json':'655294154349fd715cb5396315d27448cbd481502e52e777f9e82622628a1e3f',
 BASE/'narration.txt':'6f9576dcaed2283539754670c375f2560494334d41fa85ffd3e40ff2c9c8a6db',
 BASE/'scenario.json':'149491d198bd6a60d3fb4df30850ffa4dbbf413d4d83c48d581462886d23a955',
 BASE/'screen-sequence.json':'b114b67af040b34efffcde0eb5d0e510ecb2d897f15851c2ba3de4a620302844',
 BASE/'source-evidence.json':'d95a46bb7e6d79d0bdae1d545eefe2b0bc3bbdc055adad35bcb4a8dee6994713',
 BASE/'source-hashes.json':'f99b79e71d6429b1c247fbfe7dcdd27908cb0979635aa5fe13a60e72858f8967',
 BASE/'source-review.json':'6e2950314d50a34613013b658f8c8cadef0546dd361f2bc3279ce633c3da2815',
 Path('production/author_core_groups_units_candidate_20261028.py'):'e298629aacce4ae2d5cf8c8d832589524eec706bd69d70bcdb4db1cb480fde6e',
 GUARDS:'3383b1bfa075c00a43c2a7925b0e10e3cfde5ec65f82b7efc3937bb842feb7e2',
 Path('expansion/audits/core-groups-units-staffing-readonly-observation-20261028.json'):'46f85b7ae20bfb4aecc74bf006cc38120aef6001babf84728d50cbcde2406181',
 Path('expansion/audits/core-groups-units-administration-source-candidate-preflight-20261028.json'):'2da0ff6ca719c55cd810c020c38bf8b96fe1b3cce36f5adde6a9d01f3be2f2e4'}
PRESERVED={
 Path('expansion/plans/core-training-administration-capture-freeze-20261028-v2/core-training-administration.narrated-source.json'):'cba97decf7796e64239badb8faed3b0683ec7de2aa8009e63f14bb01ebdbb5ee',
 Path('expansion/plans/core-training-administration-take-01-proposed-derived-20261028/provenance.json'):'eafa0629ab1491f8ac2db49a425ee04706701e6e11ef1e5324b2a31a6b581234',
 Path('expansion/plans/core-certification-administration-capture-freeze-20261028/source-hashes.json'):'cbaf6b360a8fb0c6f64e3da61e7abac3617ef7af4d8a1cda653e0494e45971e8',
 Path('expansion/plans/core-personnel-administration-capture-freeze-20261028/source-hashes.json'):'770c4d93254de9170db090fa392f844166326b38df7da2604f4d5868a7f247b5'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def prepare(sources=SOURCES,core=CORE):
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    for p,h in {**PINS,**PRESERVED}.items():assert sha(sources/p)==h,'Changed retained input: '+str(p)
    spec=importlib.util.spec_from_file_location('retained_certification_freeze_guards',sources/GUARDS)
    guards=importlib.util.module_from_spec(spec);spec.loader.exec_module(guards)
    lesson=json.loads((sources/BASE/'candidate.json').read_text());sequence=json.loads((sources/BASE/'screen-sequence.json').read_text())
    captures=json.loads((sources/REVIEW).read_text());raw=json.loads((sources/RAW).read_text());narration=(sources/BASE/'narration.txt').read_text()
    source=json.loads((sources/BASE/'source-evidence.json').read_text())
    assert len(raw)==34 and len(captures['screenshots'])==31 and {r['id'][:3] for r in captures['rejected_sources']}=={'005','024','031'}
    original={r['id']:r for r in raw};assert len(original)==34
    for r in raw:
        assert sha(sources/r['file'])==r['sha256'] and sha(sources/r['dom_file'])==r['dom_sha256']
        assert _image_dimensions(sources/r['file'])==(1434,773)
    for r in captures['screenshots']:
        for key in ['file','sha256','dom_file','dom_sha256','provenance']:assert r[key]==original[r['id']][key]
        review=r['capture_review'];assert r['eligible_for_lesson'] and review['passed'] and review['sha256']==r['sha256']
        assert review['controls_sha256']==visible_controls_digest(r['visible_controls'])
    assert len(source['files'])==37
    for r in source['files']:assert sha(core/r['path'])==r['sha256'],'Cited Core source changed: '+r['path']
    guards.verify_correspondence(lesson,sequence,captures,narration)
    assert len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))==1041
    assert len(lesson['scenes'])==15 and len(lesson['sector_examples'])==6
    staffing=json.loads((sources/'expansion/audits/core-groups-units-staffing-readonly-observation-20261028.json').read_text())
    assert staffing['before']==staffing['after'] and len(staffing['before'])==8 and not staffing['global_staffing_save_clicked']
    accepted={'kind':'accepted_groups_units_source_script_review','source_sha256':PINS[BASE/'candidate.json'],
      'narration_sha256':PINS[BASE/'narration.txt'],
      'parent_review':{'reported_by':'Parent agent /root','accepted':True,'basis':'Parent reported reading all15paragraphs/1041words and accepting the exact script and control-first bounded scope.',
        'scope':'Full-script review only; no parent all-original-full-size-image review is attested.','human_audio_listening':False,'video_review':False},
      'independent_source_review':{'reviewer':'Codex source-review agent /root/core_configuration_coverage','reviewed_at':'2026-10-28T23:56:45Z',
        'original1434x773_images_individually_viewed':34,'accepted_images':31,'excluded':['005 clipped new group row','024 transient backdrop','031 stale byte-identical Casey-query image'],
        'fullDOM_streams_hashed_and_privacy_scanned':34},
      'invariants':{'spoken_words_changed':0,'scenes_changed':0,'six_sectors_changed':0,'raw_reviewed_candidate_proposals_changed':False,'untimed':True},
      'limits':['No staffing assignment/globalSave;8selectedvalues retained.','030does not prove qualificationfilter/Caseyselection.','Available/timestamps are not storedreadiness/event proof.','Fulltruncatedselector identities use owningcatalog/typeform/Stationdropdown.','No customicon/provider/GPS/physicalpresence claim.']}
    copies={NAME+'.narrated-source.json':'candidate.json',NAME+'.captures.reviewed.json':'captures.reviewed.json',
      NAME+'.screen-sequence.json':'screen-sequence.json','narration.txt':'narration.txt','scenario.json':'scenario.json',
      'source-evidence.json':'source-evidence.json','source-review.json':'source-review.json'}
    outputs={name:(sources/BASE/original).read_bytes() for name,original in copies.items()};outputs['accepted-script-review.json']=encoded(accepted)
    outputs['source-hashes.json']=encoded({'schema_version':1,'id':NAME,'status':'Frozen source-only input; no audio/timing/video/publication qualification',
      'spoken_words':1041,'scenes':15,'six_sectors':6,'raw_pairs_preserved':34,'accepted_sources':31,'source_file_pins':37,
      'narrated_source_sha256':PINS[BASE/'candidate.json'],'authoring_sha256':lesson_content_digest(lesson),
      'parent_full_script_review_accepted':True,'parent_all_original_pixel_review_not_attested':True,'human_audio_listening':False,
      'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      'previous_held_files_reverified':[{'file':p.as_posix(),'sha256':h} for p,h in PRESERVED.items()],
      'outputs':[{'file':p,'sha256':hashlib.sha256(v).hexdigest()} for p,v in outputs.items()],
      'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},'guard_recipe':{'file':GUARDS.as_posix(),'sha256':PINS[GUARDS]},
      'write_boundary':'Default/--check is read-only; --freeze uses the tested new-only guard and refuses an existing destination.'})
    return outputs,guards
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--core-source',type=Path,default=CORE)
    p.add_argument('--check',action='store_true');p.add_argument('--freeze',action='store_true');a=p.parse_args();outputs,guards=prepare(a.sources.resolve(),a.core_source.resolve());dest=a.sources/FREEZE
    if a.freeze:guards.write_new_package(dest,outputs)
    elif dest.exists():
        assert {p.name for p in dest.iterdir()}==set(outputs)
        for name,data in outputs.items():assert (dest/name).read_bytes()==data,'Changed frozen output: '+name
    print(json.dumps({'passed':True,'source_only':True,'words':1041,'scenes':15,'six_sectors':6,'accepted_images':31,'raw_pairs':34,
      'source_files':37,'prior_freezes_unchanged':True,'files_written':a.freeze,'canonical_or_ready_changed':False}))
if __name__=='__main__':main()
