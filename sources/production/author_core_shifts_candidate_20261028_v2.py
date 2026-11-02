"""Freeze the reviewed recurring-shift script with control-first source spans.

Preserves v1, the incomplete Static candidate, all raw captures and Training.
Default/--check verifies read-only; --write-source retains only new v2 packages.
No voice, timing, application, canonical, readiness, website or target operation.
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
NAME='core-shifts-administration'
OLD=Path('expansion/plans/core-shifts-administration-candidate-20261028')
NEW=Path('expansion/plans/core-shifts-administration-candidate-20261028-v2')
FREEZE=Path('expansion/plans/core-shifts-administration-capture-freeze-20261028-v2')
RAW=Path('captures/expansion/core-shifts-administration-20261028/manifest.json')
REVIEW=Path('captures/expansion/core-shifts-administration-20261028-reviewed/manifest.json')
PINS={RAW:'b5ee334f8af8575525ec5141c4c63095c5741372ab60c9222058c6ec988bb502',
      REVIEW:'97d1415642f327a05648b4bab5bacec9b4405c59b2d5da1b00bc6c121f46200c',
      OLD/'candidate.json':'44ce9754ff576afbef1322e01018bb6a24aab261e8bd394b5920be1f3891465b',
      OLD/'screen-sequence.json':'5c15bfc0ab92438f181e8a5deba267a14cc2a0885c3309e8912ff54813c02b4c',
      OLD/'narration.txt':'452ef598618505fec7af0ff0bf447457b8855df554fa3067c5dad6d42aeb5d1f',
      OLD/'source-evidence.json':'830eb757b05b5cc29a050eff25fc2edf4299b68cf92e96c6e2d7957744b5f7ed',
      Path('production/author_core_shifts_candidates_20261028.py'):'78bf5f273ac8c4dbae5c0ad237c9664728b0bca50abbed374d34be42d1d3dc89'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()

def prepare():
    sys.path.insert(0,str(ROOT/'scripts'))
    from expansion_site import lesson_content_digest
    from verify_capture_evidence import _image_dimensions
    for path,digest in PINS.items():assert sha(SOURCES/path)==digest,'Changed retained input: '+str(path)
    old=json.loads((SOURCES/OLD/'candidate.json').read_text())
    lesson=copy.deepcopy(old);scenes={s['id']:s for s in lesson['scenes']}
    reviewed=json.loads((SOURCES/REVIEW).read_text());by_id={r['id']:r for r in reviewed['screenshots']}
    by_number={int(r['id'][:3]):r for r in reviewed['screenshots']}
    changes={
      'assigned-start':{'numbers':[1,2],'labels':['Add Recurring Group Shift','New Shift'],
        'reason':'Show actual001 Add Recurring Group Shift launcher before prepared002 New Shift.'},
      'verify':{'numbers':[8,9,10,13,14,15],'labels':['Edit Details','Calendar','November 2026','04','Upcoming','Assigned'],
        'reason':'Actual008 Edit Details launcher precedes reopened009/010;013 shared November calendar precedes dated014/015. The calendar tile is truncated; full row above identifies the practice, and the dated detail supplies full identity.'},
      'policy':{'numbers':[16,1,39],'labels':['Approvals'],
        'reason':'Read-only016 policy, then actual001 Approvals launcher before039 empty queues. No approval action is demonstrated.'},
    }
    revision=[]
    for ident,change in changes.items():
        scene=scenes[ident];before=copy.deepcopy(scene)
        scene['capture_refs']=[by_number[n]['id'] for n in change['numbers']]
        scene['required_labels']=list(dict.fromkeys(scene['required_labels']+change['labels']))
        scene['route']=by_number[change['numbers'][0]]['url'].replace('http://127.0.0.1:18967','')
        scene['source_limits']=[by_id[ref]['scope_limit'] for ref in scene['capture_refs']]
        scene['capture_intent']=change['reason']
        revision.append({'scene_id':ident,'before_capture_refs':before['capture_refs'],'after_capture_refs':scene['capture_refs'],
            'added_required_labels':change['labels'],'reason':change['reason'],'narration_unchanged':scene['narration']==before['narration']})
    selected={ref for scene in lesson['scenes'] for ref in scene['capture_refs']}
    assert len(selected)==24 and selected<=set(by_id)
    captures=copy.deepcopy(reviewed)
    captures.update(kind='frozen_recurring_shift_control_first_source_subset_v2',
        parent_reviewed_manifest=REVIEW.as_posix(),parent_reviewed_manifest_sha256=PINS[REVIEW],
        screenshots=[r for r in reviewed['screenshots'] if r['id'] in selected],
        rejected_sources=[r for r in reviewed['rejected_sources'] if int(r['id'][:3]) in {3,11,12,25}],
        source_only=True,export_ready=False,publication_approved=False)
    for row in captures['screenshots']:
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(row['width'],row['height'])
    source=json.loads((SOURCES/OLD/'source-evidence.json').read_text())
    for row in source['files']:assert sha(SOURCES/row['snapshot_file'])==row['sha256']
    sequence=[]
    for scene,original in zip(lesson['scenes'],old['scenes']):
        assert scene['id']==original['id'] and scene['narration']==original['narration']
        union={label for ident in scene['capture_refs'] for label in by_id[ident]['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        assert scene['renderable']
        sequence.append({'scene_id':scene['id'],'title':scene['title'],'capture_refs':scene['capture_refs'],
          'required_labels':scene['required_labels'],'narration':scene['narration'],'practice':scene['practice'],
          'source_limits':[by_id[ref]['scope_limit'] for ref in scene['capture_refs']],
          'timing':'untimed source-only freeze; no cue, cut or duration estimate'})
    assert scenes['signup-result']['capture_refs']==[by_number[n]['id'] for n in [22,23,24,26]]
    narration='\n\n'.join(scene['narration'] for scene in lesson['scenes'])+'\n'
    assert narration.encode()==(SOURCES/OLD/'narration.txt').read_bytes()
    count=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert count==996
    lesson.update(candidate_version=2,source_complete=True,bounded_scope_only=True,whole_module_operations_complete=False,
        candidate_only=True,export_ready=False,publication_approved=False)
    limits=['Specific View Calendar widget failed; only actual shared calendar and dated details are used.',
      'Actual013 calendar tile text is truncated. Its November2026 date and04entry identify the click context; full assigned row above and014/015 supply full identity.',
      'No executed member signup, approval/denial, trade or attendance; empty queues are not completed approval.',
      'Fully staffed reflects one configured Officer slot, not physical arrival, qualification or live unit crew assignment.',
      'Static workshift editor discrepancies remain incomplete, unchanged and outside this narrated recurring-shift freeze.']
    review={'kind':'recurring_shift_control_first_source_freeze_v2','scenes':12,'spoken_words':996,'reviewed_sources':24,
      'spoken_paragraphs_unchanged':12,'six_sectors_in_spoken_outro_and_companions':True,
      'parent_review':'Parent reported reading the full996-word v1 script and original002/005/007/015/017/026/039/013 images, then directed these exact source-span additions before source-only freeze. No spoken wording changed.',
      'revisions':revision,'limits':limits,'source_review_not_video_qualification':True,'no_audio_timing_or_publication':True}
    docs={'candidate.json':encoded(lesson),'captures.reviewed.json':encoded(captures),
      'screen-sequence.json':encoded({'id':NAME,'source_complete':True,'status':'control-first source-only freeze; no audio or timing','scenes':sequence}),
      'narration.txt':narration.encode(),'revision.json':encoded(review)}
    frozen={NAME+'.narrated-source.json':docs['candidate.json'],NAME+'.captures.reviewed.json':docs['captures.reviewed.json'],
      NAME+'.screen-sequence.json':docs['screen-sequence.json'],'narration.txt':docs['narration.txt']}
    metadata={'schema_version':1,'id':NAME,'status':'frozen source-only recurring-shift input; no narration audio or video qualification',
      'candidate_version':NEW.as_posix(),'historical_v1_static_and_training_preserved':True,'parent_spoken_script_review_completed_before_v2':True,
      'narrated_source_sha256':hashlib.sha256(frozen[NAME+'.narrated-source.json']).hexdigest(),
      'authoring_sha256':lesson_content_digest(lesson),'spoken_words':996,'scenes':12,'reviewed_sources':24,
      'narration_unchanged_from_v1_sha256':PINS[OLD/'narration.txt'],'source_evidence':{'file':(OLD/'source-evidence.json').as_posix(),'sha256':PINS[OLD/'source-evidence.json']},
      'input_files':[{'file':p.as_posix(),'sha256':digest} for p,digest in PINS.items()],
      'outputs':[{'file':p,'sha256':hashlib.sha256(payload).hexdigest()} for p,payload in frozen.items()],
      'source_revisions':revision,'limits':limits,'no_canonical_ready_site_target_app_or_git_operation':True}
    frozen['source-hashes.json']=encoded(metadata)
    return {**{NEW/path:payload for path,payload in docs.items()},**{FREEZE/path:payload for path,payload in frozen.items()}}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');parser.add_argument('--write-source',action='store_true')
    args=parser.parse_args();outputs=prepare()
    for rel,payload in outputs.items():
        path=SOURCES/rel
        assert not path.exists() or path.read_bytes()==payload,'Preserve historical v2 output; choose a new version.'
    if args.write_source:
        for rel,payload in outputs.items():
            path=SOURCES/rel;path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(payload)
    print(json.dumps({'passed':True,'scenes':12,'spoken_words':996,'reviewed_sources':24,'source_only':True,
        'spoken_paragraphs_changed':0,'static_still_incomplete':True,'voice_or_render_created':False,'canonical_ready':False,'outputs':len(outputs)}))

if __name__=='__main__':main()
