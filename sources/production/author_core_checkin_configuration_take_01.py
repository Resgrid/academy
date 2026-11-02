"""Retain the reviewed Core timer screen/cue correspondence for this export.

The 14 source JPEGs were inspected at original size alongside all 97 actual
speech cues. Reproduction keeps that review fixed. A genuine full listening
review is required before producing an assembly plan. No media is synthesized,
no speech timing is estimated, and no publication review is generated.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-checkin-configuration'
BASE = Path('expansion/plans/core-checkin-configuration-capture-freeze-20261028-v2')
FROZEN = '0396ef88d272eeb59ca8dbf75b2f19d87b8e6f57247157c2a1969af499cd34e6'
MANIFEST = 'd7c87bd77d0064c8dbf55fe9b7ce76b99d7be51a1b49f70d5f0324ecad64addd'
AUDIO = '26d0667f1d0437995e7436510e6eef29590615105916886163cfb0341fcd6ae4'
CAPTIONS = 'c4bd7e34884a4ffceed4d70c74a3f678d99bbde52b2adbe5632e9645ce227bbb'
QA = '4b679d78a04a63bb31ca78af6bdc41ab30857e15210fa1767d5b6583a8e25b7c'
REVIEWED_AT = '2026-10-28T14:36:53+00:00'
RANGES = [(1,8),(9,15),(16,21),(22,29),(30,35),(36,43),(44,49),
          (50,55),(56,61),(62,69),(70,76),(77,84),(85,91),(92,97)]
# Explicit unchanged spoken phrases corresponding to the pictured field names.
# Numbers are painted table values; natural speech says thirty/five/sixty.
REFERENCES = {
  1: {'Department Settings':'Department Settings'},
  2: {'Calls & Dispatch':'Calls & Dispatch','Call & Dispatch Settings':'Call & Dispatch Settings'},
  9: {'Check-In Timer Settings':'Check-In Timer Settings'},
  10: {'Auto-Enable Check-In Timers for New Calls':'Auto-Enable Check-In Timers'},
  16: {'Add New Default Timer':'Add New Default Timer','Target Type':'Target Type'},
  17: {'Duration (minutes)':'Duration','Warning Threshold (minutes)':'Warning Threshold'},
  18: {'Enabled':'Enabled'}, 19: {'Active States':'Active States'},
  20: {'Add Timer Config':'Add Timer Config'},
  22: {'Personnel':'Personnel','Default Timer Configurations':'Default Timer Configurations','30':'thirty'},
  23: {'5':'five-minute','Yes':'Yes','All':'All'},
  30: {'Add New Override':'Add New Override'},
  31: {'Call Type ID':'Call Type ID','Call Priority':'Call Priority','Target Type':'Target Type'},
  32: {'Duration (minutes)':'Duration','Warning Threshold (minutes)':'Warning Threshold'},
  33: {'Enabled':'Enabled'}, 34: {'Active States':'Active States'},
  35: {'Add Override':'Add Override'},
  36: {'Call Type / Priority Overrides':'Call Type / Priority Overrides'},
  37: {'Rescue':'Rescue','45':'forty-five'}, 38: {'No':'No'},
  39: {'Investigation':'Investigation','60':'sixty'},
  44: {'New Call':'New Call','Name':'Name','Priority':'Priority','Type':'Type'},
  45: {'Investigation':'Investigation'}, 46: {'Call Identifier':'Call Identifier'},
  50: {'Personnel':'Personnel','Wallace Boden':'Wallace Boden'},
  56: {'Check-In Timers':'Check-In Timers','Enable Check-In Timers':'Enable Check-In Timers'},
  59: {'Create and Dispatch Call':'Create and Dispatch Call'},
  62: {'Check-In Timers':'Check-In Timers'},
  63: {'Personnel':'Personnel','OK':'OK','Time Remaining':'Time Remaining'},
  67: {'Show Check-In History':'Show Check-In History'},
  70: {'Check In':'Check In','Note':'Note'}, 72: {'Check In':'Check In'},
  77: {'Check-In Timers':'timer'},
  78: {'Timestamp':'Timestamp','Who':'Who','Type':'Type','Note':'Note'},
  85: {'Close Call':'Close Call'},
  86: {'Completed Type':'Completed Type','Send Notification':'Send Notification','Completed Notes':'Completed Notes'},
  89: {'Close Call':'Close Call'},
  92: {'Closed':'Closed','Completed Notes:':'Completed Notes'},
  93: {'Check-In Timers':'check-in history'}
}
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, validate_inputs, words
from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    lesson_path = SOURCES / BASE / (NAME+'.narrated-source.json')
    manifest_path = SOURCES / BASE / 'captures.reviewed.json'
    audio = Path('expansion/audio/'+NAME+'.m4a')
    captions = Path('expansion/audio/'+NAME+'.corrected.srt')
    qa_path = Path('expansion/audio/'+NAME+'.actual.qa.json')
    assert sha(lesson_path) == FROZEN and sha(manifest_path) == MANIFEST
    assert sha(SOURCES/audio) == AUDIO and sha(SOURCES/captions) == CAPTIONS
    assert sha(SOURCES/qa_path) == QA
    lesson = json.loads(lesson_path.read_text())
    records = json.loads(manifest_path.read_text())['screenshots']
    qa = json.loads((SOURCES/qa_path).read_text())
    assert qa['passed'] and not qa['issues'] and not qa['possible_speech_gaps']
    assert qa['audio']['sha256'] == AUDIO and qa['lesson']['sha256'] == FROZEN
    assert qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0
    assert qa['raw_captions']['cues'] == qa['corrected_captions']['cues'] == 97
    assert len(lesson['scenes']) == len(records) == len(RANGES) == 14
    for row in records:
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file']) == row['sha256']
    cues = load_cues(SOURCES/captions)
    assert len(cues) == 97
    duration, scenes = qa['audio']['duration_seconds'], []
    by_id = {r['id']:r for r in records}
    for index, ((first,last), authored, shot) in enumerate(zip(RANGES,lesson['scenes'],records)):
        assert words(' '.join(c['text'] for c in cues[first-1:last])) == words(authored['narration'])
        start = 0 if index == 0 else cues[first-1]['start']
        end = duration if index == 13 else cues[RANGES[index+1][0]-1]['start']
        screen = {'screenshot_id':shot['id'],'start':start,'end':end}
        expanded = []
        for number in range(first,last+1):
            refs = REFERENCES.get(number,{})
            assert set(refs) <= set(shot['visible_labels'])
            entry = dict(cues[number-1],cue=number,screenshot_id=shot['id'],
                         required_labels=list(refs),spoken_references=refs,instructional=bool(refs))
            validator = _Validator(SOURCES)
            validator.spoken_references(entry,{_normalized(x) for x in refs},'cue '+str(number),True)
            assert not validator.issues, validator.issues
            expanded.append(entry)
        built = {'id':authored['id'],'title':authored['title'],'kind':'operational',
                 'start':start,'end':end,'visual_required_labels':authored['required_labels'],
                 'screens':[screen],'captions':expanded}
        review = {'passed':True,'reviewer':'Codex exact source-image and full cue correspondence review',
            'reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,
            'mapping_sha256':instruction_scene_digest(built,by_id),
            'method':'All 14 untouched Core JPEGs inspected at original size with all 97 actual export cues. Each paragraph stays on its corresponding form or saved result. Natural references map spoken field names and numbers to visible controls/values. No warning/overdue transition, device location or notification delivery is inferred.'}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':[screen],
            'captions':[{k:e[k] for k in ('cue','screenshot_id','required_labels','spoken_references','instructional')} for e in expanded],
            'instruction_review':review})
    return lesson_path,lesson,records,qa,scenes,duration,audio,captions,qa_path


def build(listening_review):
    lesson_path,lesson,records,qa,scenes,duration,audio,captions,qa_path = prepare()
    heard = json.loads(Path(listening_review).read_text())
    assert heard['complete_natural_narration'] is True
    assert heard['audio_sha256'] == AUDIO and heard['lesson_sha256'] == FROZEN
    assert heard['reviewer'] and heard['reviewed_at'] and heard['evidence']
    assert datetime.fromisoformat(heard['reviewed_at'].replace('Z','+00:00')) <= datetime.now(timezone.utc)
    now = datetime.now(timezone.utc).isoformat()
    plan = {'schema_version':1,'lesson_id':NAME,'duration_seconds':duration,
        'instruction_mapping':'reviewed_scene_coverage',
        'display_context':'TRAINING ONLY · fictional department',
        'narration':{'file':str(audio),'sha256':AUDIO,'kind':'approved_natural_narration',
            'approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],
                'sha256':AUDIO,'complete_natural_narration':True,'evidence':heard['evidence'],
                'qa_file':str(qa_path),'qa_sha256':QA}},
        'captions':{'file':str(captions),'sha256':CAPTIONS,'kind':'speech_timed_srt',
            'approval':{'reviewer':'Codex exact frozen script/export correspondence',
                'reviewed_at':now,'sha256':CAPTIONS,'audio_sha256':AUDIO,'speech_timing_reviewed':True,
                'method':'All 97 genuine Descript speech boundaries retained; full decoded audio and every timed cue passed signal/layout/script checks.'}},
        'capture_manifests':[{'file':str(BASE/'captures.reviewed.json'),'sha256':MANIFEST}],
        'screenshot_reviews':{r['id']:{'reviewer':'Codex exact original-size JPEG inspection',
            'reviewed_at':REVIEWED_AT,'sha256':r['sha256'],'application_visible':True,
            'labels_legible':True,'no_errors':True} for r in records},
        'scenes':scenes,'publishable':False,
        'limitations':lesson['capture_limitations']}
    return plan,lesson_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-preflight',action='store_true')
    parser.add_argument('--listening-review',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.source_preflight:
        _,_,records,_,scenes,duration,_,_,_ = prepare()
        print(json.dumps({'passed':True,'scenes':len(scenes),'screens':len(records),
            'cues':97,'duration':duration,'narration_approved':False,'rendered':False}))
    else:
        if not args.listening_review or not args.output:
            parser.error('Supply --listening-review and --output after genuine listening review.')
        plan,lesson_path = build(args.listening_review)
        assert not args.output.exists(), 'Preserve existing plans; choose a new output.'
        args.output.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
        recipe = validate_inputs(lesson_path,args.output,SOURCES)
        print(json.dumps({'passed':True,'scenes':len(recipe['scenes']),
            'cues':len(recipe['cues']),'duration':recipe['duration'],'rendered':False}))
