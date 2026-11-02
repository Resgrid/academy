"""Bind Training's genuine export cues to retained actual application screens.

Default checks are read-only. --write-correspondence retains a source-only
scaffold, not a renderer plan or derived SRT. Actual approved audio, full decode
and cue-energy QA, and hash-bound full listening review are still required.
No application, frozen input, canonical lesson, readiness or site is changed.
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
NAME = 'core-training-administration'
BASE = Path('expansion/plans/core-training-administration-capture-freeze-20261028-v2')
OUTPUT = Path('expansion/plans/core-training-administration-take-01-source-correspondence-20261028')
FROZEN = 'cba97decf7796e64239badb8faed3b0683ec7de2aa8009e63f14bb01ebdbb5ee'
MANIFEST = '6e407edcea942671b54a34d14fc04f495ea95d8b8d136126e8e969f5054a66e2'
SEQUENCE = '8d3e4afd86fe3afe905de49ad5c89d5bb70882f5e6464c9279deeb4688e3421a'
RAW_FILE = Path('expansion/audio/core-training-administration-generated-20261028.raw.srt')
RAW = '8fd7b612798a540402c55a6de0e52294b1874137c4493a05db402548b4a7acc8'
TEXT_FILE = Path('expansion/audio/core-training-administration-generated-20261028.raw.txt')
TEXT = '2cca2d0a1a4ff3bee929d4ec479d8265f383190314eb867de4b6c8e0c4e8a3cd'
ANCHORS_FILE = Path('expansion/audio/core-training-administration-generated-20261028.one-second.txt')
ANCHORS = 'bb16274d983a4f96a41500f5bb70accd291629f14479d1a3fe8646e3bf8a1e61'
RANGES = [(1,9),(10,18),(19,27),(28,37),(38,45),(46,54),(55,65),(66,73),(74,84),(85,97)]
SCREEN_STARTS = {1:1,4:2,10:3,19:5,28:6,38:7,41:8,46:7,47:9,52:12,
                 55:12,56:13,57:14,66:15,69:15,70:16,74:20,77:21,
                 81:22,83:21,84:23,85:23}
SPLITS = [
    {'cue':55,'at_seconds':191,'before':12,'after':13,
     'before_text':'Choose Take Quiz and','after_text':'read the welcome stage.',
     'before_references':{'Take Quiz':'Take Quiz'},'after_references':{'Start >':'welcome stage'},
     'reason':'Picture Take Quiz before the separately captured welcome stage.'},
    {'cue':69,'at_seconds':233,'before':15,'after':16,
     'before_text':'Submit once and check the','after_text':'returned catalog.',
     'before_references':{'Finish':'Submit'},'after_references':{'Trainings':'catalog'},
     'reason':'Keep the real lower Finish submission screen before the returned catalog. The two-word tail lasts0.750s; inspect derived readability after actual audio QA.'},
    {'cue':83,'at_seconds':285,'before':21,'after':23,
     'before_text':'Verify the assignment count and','after_text':'existing result separately',
     'before_references':{'Currently Assigned':'assignment count'},'after_references':{'Result':'result'},
     'reason':'The preserved assignment count and existing quiz result occupy different actual screens.'},
]
REFERENCES = {
 3:{'New Training':'New Training'},4:{'Training name':'Training name'},5:{'Description':'Description'},
 10:{'Training Text':'Training Text'},18:{'Training Text':'Training Text'},
 19:{'Minimum Score':'Minimum Score'},20:{'Due Date':'Due Date'},22:{'Add all Personnel':'Add all Personnel'},
 23:{'Groups To Add':'Groups To Add','Roles To Add':'Roles To Add','Users To Add':'Users To Add'},
 26:{'Add all Personnel':'Add all Personnel'},28:{'Questions':'Questions','Add Question':'Add Question'},
 30:{'Add Answer':'Add two answers'},33:{'Correct':'correct'},35:{'Add Training':'Add Training'},
 38:{'Trainings':'catalog','Due Date':'due date'},40:{'Report':'Report'},
 41:{'Viewed':'Viewed','Completed':'Completed','Score':'Score','Result':'Result'},
 42:{'Wallace Boden':'Boden','Not Viewed':'Not Viewed','Not Completed':'Not Completed','No Score':'No Score','Pending':'Pending'},
 46:{'View Training':'View Training'},47:{'Due By:':'due date','Description:':'description'},
 51:{'Take Quiz':'Take Quiz'},52:{'Training files':'training files'},56:{'Next':'Next'},
 59:{'Reopen the saved contact and verify the updated details.':'reopen the saved contact'},
 60:{'Reopen the saved contact and verify the updated details.':'verify the updated details'},
 62:{'Next':'Next'},65:{'Previous':'Previous'},66:{'Finish':'Finish'},67:{'Finish':'Finish'},
 70:{'Training Complete':'Training Complete'},72:{'Report':'Report'},
 75:{'academy-contact-verification.txt':'contact-verification'},76:{'quick-check.txt':'quick-check dot txt'},
 77:{'Existing Attachments':'Existing Attachments'},78:{'Currently Assigned':'Assigned'},
 79:{'Add Attachments':'Add Attachments','review.txt':'review dot txt'},80:{'Save Training':'Save Training'},
 81:{'Training files':'Training files'},85:{'Training Report':'Report'},86:{'100':'one hundred','Pass':'Pass'},
 87:{'Viewed':'Viewed'},89:{'Pending':'Pending'},
}

sys.path.insert(0,str(ROOT/'scripts'))
from render_walkthrough import load_cues, words
from verify_capture_evidence import _Validator, _normalized, _image_dimensions

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value): return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def service_anchors(text):
    parts=re.split(r'\[(\d{2}):(\d{2}):(\d{2})\]',text)
    assert len(parts)>4 and not words(parts[0]),'Require actual service timestamp export.'
    result=[];offset=0
    for i in range(1,len(parts),4):
        result.append((int(parts[i])*3600+int(parts[i+1])*60+int(parts[i+2]),offset))
        offset+=len(words(parts[i+3]))
    return result,words(re.sub(r'\[\d{2}:\d{2}:\d{2}\]','',text))

def references(cue,refs,row):
    assert set(refs)<=set(row['visible_labels']),'Required control is absent from its actual reviewed image.'
    checker=_Validator(SOURCES)
    checker.spoken_references(dict(cue,spoken_references=refs),{_normalized(x) for x in refs},str(cue.get('cue','source')),True)
    assert not checker.issues,checker.issues

def check_anchor(split,cues,anchors):
    cue=cues[split['cue']-1]
    before,after=split['before_text'],split['after_text']
    assert words(before)+words(after)==words(cue['text']),'Preserve the exact spoken order.'
    offset=sum(len(words(c['text'])) for c in cues[:split['cue']-1])+len(words(before))
    assert (split['at_seconds'],offset) in anchors,'Require a genuine whole-second marker at this exact word boundary.'
    assert cue['start']<split['at_seconds']<cue['end'],'Anchor must be inside its actual cue.'
    assert min(split['at_seconds']-cue['start'],cue['end']-split['at_seconds'])>=0.7,'Do not propose unreadable microcues.'
    return {'global_word_offset':offset,'before_seconds':split['at_seconds']-cue['start'],'after_seconds':cue['end']-split['at_seconds']}

def prepare():
    inputs={BASE/(NAME+'.narrated-source.json'):FROZEN,BASE/(NAME+'.captures.reviewed.json'):MANIFEST,
            BASE/(NAME+'.screen-sequence.json'):SEQUENCE,RAW_FILE:RAW,TEXT_FILE:TEXT,ANCHORS_FILE:ANCHORS}
    for path,digest in inputs.items():assert sha(SOURCES/path)==digest,'Changed frozen/export input: '+str(path)
    lesson=json.loads((SOURCES/BASE/(NAME+'.narrated-source.json')).read_text())
    manifest=json.loads((SOURCES/BASE/(NAME+'.captures.reviewed.json')).read_text())
    sequence=json.loads((SOURCES/BASE/(NAME+'.screen-sequence.json')).read_text())
    sequence_scenes={scene['scene_id']:scene for scene in sequence['scenes']}
    cues=load_cues(SOURCES/RAW_FILE);assert len(cues)==97 and len(lesson['scenes'])==10
    all_words=words(' '.join(s['narration'] for s in lesson['scenes']))
    assert all_words==words((SOURCES/TEXT_FILE).read_text())==words(' '.join(c['text'] for c in cues))
    anchors,anchor_words=service_anchors((SOURCES/ANCHORS_FILE).read_text());assert anchor_words==all_words
    rows={int(row['id'][:3]):row for row in manifest['screenshots']};assert len(rows)==21
    for row in rows.values():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file'])==row['sha256'] and sha(SOURCES/row['dom_file'])==row['dom_sha256']
        assert _image_dimensions(SOURCES/row['file'])==(row['width'],row['height'])
    mapped=[];selected=None
    for number,cue in enumerate(cues,1):
        if number in SCREEN_STARTS:selected=SCREEN_STARTS[number]
        refs=REFERENCES.get(number,{});references(cue,refs,rows[selected])
        mapped.append(dict(cue,raw_cue=number,screenshot_id=rows[selected]['id'],required_labels=list(refs),spoken_references=refs))
    mixed=[]
    for split in SPLITS:
        detail=check_anchor(split,cues,anchors)
        for side in ['before','after']:
            references({'text':split[side+'_text']},split[side+'_references'],rows[split[side]])
        mixed.append(dict(split,**detail,precision='Actual service whole-second marker; no millisecond word precision or interpolation.',proposed_only=True))
    scenes=[]
    for (first,last),scene in zip(RANGES,lesson['scenes']):
        assert words(' '.join(c['text'] for c in cues[first-1:last]))==words(scene['narration'])
        selected_rows={entry['screenshot_id'] for entry in mapped[first-1:last]}
        for split in SPLITS:
            if first<=split['cue']<=last:selected_rows.update(rows[split[side]]['id'] for side in ['before','after'])
        union={label for row in rows.values() if row['id'] in selected_rows for label in row['visible_labels']}
        assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
        scenes.append({'scene_id':scene['id'],'first_raw_cue':first,'last_raw_cue':last,'capture_refs':sorted(selected_rows),'required_labels':scene['required_labels'],'source_limits':sequence_scenes[scene['id']]['source_limits']})
    return {'schema_version':1,'lesson_id':NAME,'status':'source-only actual-cue correspondence; NOT an assembly plan',
      'renderer_ready':False,'narration_approved':False,'canonical_ready':False,'rendered':False,'publication_approved':False,
      'frozen_lesson_sha256':FROZEN,'reviewed_source_images':21,'raw_cues':97,'original_scene_count':10,
      'input_files':[{'file':p.as_posix(),'sha256':digest} for p,digest in inputs.items()],
      'scene_ranges':scenes,'raw_cue_correspondence':mapped,'proposed_genuine_word_cuts':mixed,
      'prospective_derived_cues':100,'derived_srt_written':False,
      'pending_assembly_requirements':['Actual approved-export audio with exact hash; no editor or signed-media URL in public inputs.','Passed full-decode/exact-script/raw-and-corrected-cue speech-energy QA bound to actual audio and frozen source.','Actual full human listening approval bound to this frozen source and actual audio.','Recheck derived cue readability/energy with actual corrected captions; retain original97cues and QA.','Strict renderer input validation, independent encoded-frame review and actual native playback evidence after rendering.'],
      'limitations':['No audio duration, voice quality, frame result, browser proof or public qualification is inferred here.','Raw004 date popup and011 clipped Save remain excluded; unmanifested full-page diagnostic is not renderer input.','Selected Matthew text is clipped in005; only bulk audience and readable selector labels are used.','Prepared006 Add Training precedes saved007. Quiz answer014 is preparation; lower Finish015 precedes returned016.','Saved012 file list before the quiz is distinct from prepared010 clipped filename and unpictured initial Save.','020 shows both existing handouts before additional review.txt;021 shows selected review.txt AND actual Save Training;022 is the fresh stored three-file result.','023 shows Boden100/Pass and upper12rows only. The other13Pending are supported by its retained full DOM and earlier017whole14-row source, not all14simultaneous pixels.','No reset, reassignment, renewed quiz attempt, attachment download or professional qualification is demonstrated.','At cue69 the genuine233s anchor leaves a0.750s two-word caption tail. Review this after actual alignment; never interpolate a replacement cut.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-preflight',action='store_true')
    parser.add_argument('--write-correspondence',action='store_true')
    args=parser.parse_args();source=prepare()
    if args.write_correspondence:
        path=SOURCES/OUTPUT/'correspondence.scaffold.json';payload=encoded(source)
        assert not path.exists() or path.read_bytes()==payload,'Preserve the retained source correspondence; choose a new version.'
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():path.write_bytes(payload)
    print(json.dumps({'passed_source_preflight':True,'scenes':10,'raw_cues':97,'reviewed_sources':21,'proposed_genuine_cuts':[s['at_seconds'] for s in SPLITS],'renderer_ready':False,'narration_approved':False,'rendered':False,'canonical_ready':False}))

if __name__=='__main__':main()
