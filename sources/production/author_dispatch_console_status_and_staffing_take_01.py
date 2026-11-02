"""Retain the frozen screen and actual speech-cue mapping for this export.

Original source-image reviews remain bound to the unchanged JPEGs. Explicit
transition cues show the control before its result. No speech timing is guessed;
full listening approval is required before producing the assembly plan.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-dispatch-console-status-and-staffing'
BASE = Path('expansion/plans/app-dispatch-console-status-and-staffing-capture-freeze-20261028')
MANIFEST_FILE = Path('expansion/plans/app-dispatch-console-status-and-staffing-capture-freeze-20261028/captures.reviewed.json')
FROZEN = 'b2b76d4cc8e034437ee162a937597e0594eb6f43b1bd1f48662015093171fa95'
MANIFEST = '9528696ef3604e1c71b66d034cff51f4f258a0ac5da6a11980a52bdca2a0eb7e'
AUDIO = 'e909b8a2b61d4133ed5becac7605ee9fcf887a46f09b91850e21f66e5e2cce1d'
CAPTIONS = '8bcc9b2d9c806b70f25578d6f1aee600c9eb0cee71da5e285210c7d685db48a2'
QA = '7c09f83fbc23349977323ffa7413fc2008382583c9f89eeaa450bf9ce4846d01'
REVIEWED_AT = '2026-10-28T19:21:18.205302+00:00'
SCENE_COUNT = 19
CUE_COUNT = 118
RANGES = [(1, 7), (8, 13), (14, 20), (21, 27), (28, 33), (34, 39), (40, 46), (47, 52), (53, 59), (60, 65), (66, 70), (71, 76), (77, 81), (82, 87), (88, 93), (94, 98), (99, 104), (105, 110), (111, 118)]
SCREEN_BY_CUE = {21: '003-selected-call-context', 71: '012-unit-status-update-observed', 111: '019-personnel-staffing-update-observed'}
REFERENCES = {1: {'Map': 'map', 'Personnel': 'personnel', 'Resgrid Dispatch': 'Resgrid Dispatch', 'Units': 'units'},
 2: {'Notes': 'notes'},
 8: {'Community': 'Community'},
 9: {'TRAINING — Community medical standby': 'community medical standby'},
 10: {'Active Calls': 'active calls'},
 15: {'Filtering by call: #DEMO-0002': 'Filtering by call banner identifies DEMO-0002'},
 16: {'Personnel on Call': 'Personnel on Call', 'Units on Call': 'Units on Call'},
 17: {'Call Notes': 'Call Notes'},
 21: {'Clear Filter': 'Clear Filter'},
 23: {'Notes': 'Notes', 'Personnel': 'Personnel', 'Units': 'Units'},
 24: {'Community': 'Community'},
 28: {'Available only': 'Available only'},
 30: {'Available': 'Available', 'Engine 51': 'Engine 51'},
 34: {'Engine': 'Engine'},
 35: {'Available': 'Available', 'Engine 51': 'Engine 51'},
 36: {'Out of Service': 'Out of Service'},
 40: {'Engine 51': 'Engine 51'},
 41: {'Engine 51': 'Engine 51', 'Status': 'Status'},
 42: {'Note (optional)': 'Note', 'Select Status': 'Select Status'},
 47: {'Select Status': 'Select Status'},
 48: {'Available': 'Available',
      'Committed': 'Committed',
      'On Scene': 'On Scene',
      'Responding': 'Responding'},
 49: {'Responding': 'Responding'},
 50: {'Available': 'Available',
      'Call destination': 'Call destination',
      'Station destination': 'Station destination'},
 52: {'Available': 'Available'},
 53: {'Destination': 'Destination'},
 54: {'No Destination': 'No Destination'},
 55: {'Firehouse 51': 'Firehouse 51', 'No Station': 'No Station', 'Stations (2)': 'Stations'},
 56: {'No Destination': 'No Destination', 'No Station': 'No Station'},
 58: {'No Destination': 'No Destination'},
 60: {'Available': 'Available', 'Engine 51': 'Engine 51', 'No Destination': 'No Destination'},
 61: {'TRAINING ONLY - Dispatch status practice.': 'Training only, Dispatch status practice'},
 62: {'Update Status': 'Update Status'},
 66: {'Activity Log': 'Activity Log', 'Unit status updated': 'Unit status updated'},
 67: {'Available': 'Available', 'Engine 51': 'Engine 51'},
 68: {'Available': 'Available'},
 71: {'Engine 51': 'Engine 51'},
 72: {'Available': 'Available',
      'Destination': 'Destination',
      'None': 'None',
      'Status Information': 'Status Information'},
 73: {'Status Updated': 'Updated'},
 74: {'Assigned Roles': 'Assigned Roles', 'Christopher Herrmann': 'Christopher Herrmann'},
 77: {'Note': 'Note'},
 78: {'TRAINING ONLY - Dispatch status practice.': 'exact training note'},
 82: {'Boden': 'Boden'},
 83: {'Chief': 'Chief', 'Command': 'Command', 'Wallace Boden': 'Wallace Boden'},
 84: {'Available': 'Available', 'Standing By': 'Standing By'},
 88: {'Wallace Boden': 'Wallace Boden'},
 90: {'Note (optional)': 'note field', 'Select Status': 'Select Status'},
 94: {'Select Staffing Level': 'Select Staffing Level'},
 95: {'Available': 'Available',
      'Committed': 'Committed',
      'Delayed': 'Delayed',
      'On Shift': 'On Shift',
      'Unavailable': 'Unavailable'},
 98: {'Available': 'Available'},
 99: {'Available': 'Available', 'Staffing': 'Staffing', 'Wallace Boden': 'Wallace Boden'},
 100: {'TRAINING ONLY - Dispatch staffing practice.': 'Dispatch staffing practice'},
 101: {'Update Staffing': 'Update Staffing'},
 105: {'Personnel staffing updated': 'Personnel staffing updated'},
 106: {'Available': 'Available', 'Standing By': 'Standing By', 'Wallace Boden': 'Wallace Boden'},
 111: {'Wallace Boden': 'Wallace Boden'},
 112: {'Available': 'Available',
       'Standing By': 'Standing By',
       'Status & Staffing': 'Status and Staffing'},
 113: {'Chief': 'Chief', 'Roles': 'Roles'}}
METHOD = 'The unchanged19 source JPEGs retain their hash-bound original-size reviews. All118 actual speech cues were matched to readable forms, chooser choices and saved results. Clear Filter remains visible for its action cue; unit and personnel cards precede their separate details readbacks. Changes occur only at genuine cue boundaries. No bulk update, personnel response-status change, staffing-note persistence, native GPS or provider delivery is inferred.'
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import load_cues, validate_inputs, words
from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    lesson_path = SOURCES / BASE / (NAME+'.narrated-source.json')
    manifest_path = SOURCES / MANIFEST_FILE
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
    assert qa['raw_captions']['cues'] == qa['corrected_captions']['cues'] == CUE_COUNT
    assert len(lesson['scenes']) == len(records) == len(RANGES) == SCENE_COUNT
    for row in records:
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file']) == row['sha256']
    cues = load_cues(SOURCES/captions)
    assert len(cues) == CUE_COUNT
    duration, scenes = qa['audio']['duration_seconds'], []
    by_id = {r['id']:r for r in records}
    for index, ((first,last), authored, primary) in enumerate(zip(RANGES,lesson['scenes'],records)):
        assert words(' '.join(c['text'] for c in cues[first-1:last])) == words(authored['narration'])
        start = 0 if index == 0 else cues[first-1]['start']
        end = duration if index == SCENE_COUNT-1 else cues[RANGES[index+1][0]-1]['start']
        screens, expanded = [], []
        selected, screen_start = SCREEN_BY_CUE.get(first,primary['id']), start
        for number in range(first,last+1):
            ident = SCREEN_BY_CUE.get(number,primary['id'])
            if ident != selected:
                screens.append({'screenshot_id':selected,'start':screen_start,'end':cues[number-1]['start']})
                selected, screen_start = ident, cues[number-1]['start']
            refs = REFERENCES.get(number,{})
            assert set(refs) <= set(by_id[ident]['visible_labels']), (number,ident,refs)
            entry = dict(cues[number-1],cue=number,screenshot_id=ident,
                         required_labels=list(refs),spoken_references=refs,instructional=bool(refs))
            validator = _Validator(SOURCES)
            validator.spoken_references(entry,{_normalized(x) for x in refs},'cue '+str(number),True)
            assert not validator.issues, validator.issues
            expanded.append(entry)
        screens.append({'screenshot_id':selected,'start':screen_start,'end':end})
        built = {'id':authored['id'],'title':authored['title'],'kind':'operational',
                 'start':start,'end':end,'visual_required_labels':authored['required_labels'],
                 'screens':screens,'captions':expanded}
        review = {'passed':True,'reviewer':'Codex frozen source-image and complete actual-cue correspondence review',
            'reviewed_at':REVIEWED_AT,'correspondence_reviewed':True,'no_unseen_controls':True,
            'mapping_sha256':instruction_scene_digest(built,by_id),'method':METHOD}
        scenes.append({'id':authored['id'],'start':start,'end':end,'screens':screens,
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
                'method':'All 118 genuine Descript speech boundaries retained; full decoded audio and every timed cue passed signal/layout/script checks.'}},
        'capture_manifests':[{'file':str(MANIFEST_FILE),'sha256':MANIFEST}],
        'screenshot_reviews':{r['id']:{'reviewer':'Codex exact original-size JPEG inspection',
            'reviewed_at':r['capture_review']['reviewed_at'],'sha256':r['sha256'],'application_visible':True,
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
            'cues':CUE_COUNT,'duration':duration,'narration_approved':False,'rendered':False}))
    else:
        if not args.listening_review or not args.output:
            parser.error('Supply --listening-review and --output after genuine listening review.')
        plan,lesson_path = build(args.listening_review)
        assert not args.output.exists(), 'Preserve existing plans; choose a new output.'
        args.output.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
        recipe = validate_inputs(lesson_path,args.output,SOURCES)
        print(json.dumps({'passed':True,'scenes':len(recipe['scenes']),
            'cues':len(recipe['cues']),'duration':recipe['duration'],'rendered':False}))
