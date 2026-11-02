"""Derive approved Contacts navigation/practice revisions without changing v1.

Default/--check is read-only. --write-freeze writes only the new frozen-source
package, with no canonical, audio, timing, readiness, site or target mutation.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'
NAME='core-contacts-administration'
OLD=Path('expansion/plans/core-contacts-administration-candidate-20261028')
NEW=Path('expansion/plans/core-contacts-administration-capture-freeze-20261028')
EXPECTED={
 'candidate.json':'d6bbf01213d0499b8d7370ee65b7ad16c9bf846017d86e7f4c3ccbc681d6a53b',
 'captures.reviewed.json':'326872b591a6802e3cc81aa154abeb232ccefc56e4ca3b58e9c3f19f7fb3245e',
 'screen-sequence.json':'16604bc0e810fcac07dc5ad9aa8657b6091a4bc96445d5c8a6756d79c042687f',
 'source-evidence.json':'0ca20e0f95ce12e305a4e96826761f81acc02c89bb40e193236c60c3ee68e2e8'}
PRACTICES={
 'directory':'Find the category table and identify its contact-count column before adding an entry.',
 'category':'Save a fictional partner category with map display off, then verify its name and zero contact count.',
 'person':'Prepare a fictional Person entry with first and last names, the intended category and a useful operational description.',
 'person-readback':'Search for the saved person, open View and verify the saved channels and complete description.',
 'company':'Prepare a Location or Company entry with a clear organization name and a reserved office phone.',
 'location':'Save a fictional paired reference location and address with Same as Physical selected; keep entrance and exit pairs blank.',
 'filters':'Select the category, search for the organization, then clear the text search and confirm both entries return.',
 'readback':'Reopen Edit and verify the named category and copied mailing fields on that form.',
 'phone-edit':'Change the reserved office phone on your fictional organization, save, leave and reopen to verify the new final digit.',
 'handover':'Verify the category contains both practice contacts and choose who will review the directory before the next exercise.'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(obj): return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()

def prepare(sources):
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest
    for name,digest in EXPECTED.items():
        assert sha(sources/OLD/name)==digest,'Historical input changed: '+name
    source_evidence=json.loads((sources/OLD/'source-evidence.json').read_text())
    for entry in source_evidence['files']:
        assert sha(sources/entry['retained_file'])==entry['sha256'],entry['path']
    lesson=json.loads((sources/OLD/'candidate.json').read_text())
    historical=copy.deepcopy(lesson)
    captures=json.loads((sources/OLD/'captures.reviewed.json').read_text())
    sequence=json.loads((sources/OLD/'screen-sequence.json').read_text())
    by_id={x['id']:x for x in captures['screenshots']}
    assert len(by_id)==22 and len(captures['rejected_sources'])==2
    scene_by_id={x['id']:x for x in lesson['scenes']}
    old='open Contacts, then Categories'
    assert scene_by_id['directory']['narration'].count(old)==1
    scene_by_id['directory']['narration']=scene_by_id['directory']['narration'].replace(old,'we are in Contacts, on the Categories page')
    old='Return to Contacts and choose New Contact. Select Person, then Academy Partner Directory.'
    assert scene_by_id['person']['narration'].count(old)==1
    scene_by_id['person']['narration']=scene_by_id['person']['narration'].replace(old,'On the Add Contact form, select Person, then Academy Partner Directory.')
    scene_by_id['person']['required_labels'].insert(0,'Add Contact')
    row4=next(x for x in by_id.values() if x['id'].startswith('004-'))
    assert 'Add Contact' in row4['visible_labels'] and 'Add Contact' in row4['required_labels']
    for scene in lesson['scenes']:
        scene['practice']=PRACTICES[scene['id']]
        union={label for ident in scene['capture_refs'] for label in by_id[ident]['visible_labels']}
        assert set(scene['required_labels'])<=union,scene['id']
        for ident in scene['capture_refs']:
            row=by_id[ident]
            assert sha(sources/row['file'])==row['sha256']
            assert sha(sources/row['dom_file'])==row['dom_sha256']
    for scene in sequence['scenes']:
        revised=scene_by_id[scene['scene_id']]
        scene['narration']=revised['narration']
        scene['required_label_union']=revised['required_labels']
        scene['practice']=revised['practice']
    assert len(lesson['scenes'])==len(sequence['scenes'])==10
    # Only the requested two spoken paragraphs, one scene label requirement,
    # and ten practices differ from the historical candidate.
    restored=copy.deepcopy(lesson)
    old_by_id={x['id']:x for x in historical['scenes']}
    for scene in restored['scenes']:
        scene['practice']=old_by_id[scene['id']]['practice']
        if scene['id'] in {'directory','person'}:
            scene['narration']=old_by_id[scene['id']]['narration']
        if scene['id']=='person': scene['required_labels']=old_by_id['person']['required_labels']
    assert restored==historical
    narration='\n\n'.join(x['narration'] for x in lesson['scenes'])+'\n'
    count=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration))
    frames=[{key:r[key] for key in ['id','file','sha256','dom_file','dom_sha256']} for r in captures['screenshots']]
    source_hashes={'schema_version':1,'id':NAME,'status':'frozen source/narration inputs only; media qualification and canonical publication remain separate',
        'approved_revision_provenance':'Parent reviewed complete original Contacts script and all24 original-size source frames, then requested exactly these navigation/label and scene-practice revisions.',
        'historical_inputs':[{'file':(OLD/name).as_posix(),'sha256':digest} for name,digest in EXPECTED.items()],
        'narrated_source':{'file':NAME+'.narrated-source.json','sha256':hashlib.sha256(encoded(lesson)).hexdigest(),'authoring_sha256':lesson_content_digest(lesson),'scenes':10,'spoken_words':count},
        'captures':{'file':NAME+'.captures.reviewed.json','sha256':hashlib.sha256(encoded(captures)).hexdigest(),'retained_sources':22,'excluded':2,'raw24source_frames_unchanged':True},
        'screen_sequence':{'file':NAME+'.screen-sequence.json','sha256':hashlib.sha256(encoded(sequence)).hexdigest(),'timing':'untimed; no estimated cuts or cues'},
        'narration_text':{'file':'narration.txt','sha256':hashlib.sha256(narration.encode()).hexdigest()},'source_frames':frames,
        'revision_diff':[{'scene_id':slug,'before_narration':old_by_id[slug]['narration'],'after_narration':scene_by_id[slug]['narration']} for slug in ['directory','person']],
        'required_label_change':{'scene_id':'person','added':'Add Contact','actual_source':'004-person-identity-prepared','existing_reviewed004label_preserved':True},
        'practice_changes':[{'scene_id':x['id'],'before':old_by_id[x['id']]['practice'],'after':x['practice']} for x in lesson['scenes']],
        'protected_limits':['015 transient fade and022 failed Description replacement excluded.','View category numeric and mailing blank; named category/copy verified via list/Edit.','Phone0143→0144 actual prepared/reopened evidence; original Description unchanged.','No audio, timings, readiness, canonical, site or target output.']}
    return {NAME+'.narrated-source.json':encoded(lesson),NAME+'.captures.reviewed.json':encoded(captures),
        NAME+'.screen-sequence.json':encoded(sequence),'narration.txt':narration.encode(),'source-hashes.json':encoded(source_hashes)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--write-freeze',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args();sources=args.sources.resolve();out=(args.output_dir or sources/NEW).resolve()
    canonical=(sources/'expansion/lessons').resolve()
    assert out!=canonical and canonical not in out.parents,'Canonical output prohibited.'
    docs=prepare(sources)
    for name,payload in docs.items():
        p=out/name
        if p.exists(): assert p.read_bytes()==payload,'Retain differing prior output and choose a new version.'
    if args.write_freeze:
        out.mkdir(parents=True,exist_ok=True)
        for name,payload in docs.items():
            p=out/name
            if not p.exists():
                with p.open('xb') as stream: stream.write(payload)
    print(json.dumps({'passed':True,'operation':'write frozen source inputs' if args.write_freeze else 'read-only check',
        'files':[{'file':name,'sha256':hashlib.sha256(payload).hexdigest()} for name,payload in docs.items()],
        'words':json.loads(docs['source-hashes.json'])['narrated_source']['spoken_words'],'canonical_or_media_mutations':False},indent=2))

if __name__=='__main__': main()
