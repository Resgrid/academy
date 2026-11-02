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
NAME = 'core-mapping-points-and-filters'
BASE = Path('expansion/plans/core-mapping-points-and-filters-capture-freeze-20261028-v2')
MANIFEST_FILE = Path('expansion/plans/core-mapping-points-and-filters-take-01.captures.reviewed.json')
FROZEN = 'dfc21fa121d4727b55fb6b28e8aae9b438da403619b660768eae32833d49b2f6'
MANIFEST = 'efa59205f836e9148c2e8ccbbf5782485dc401d8545cb382d5000be6cb503f64'
AUDIO = '6e4acf0e59f4d7e991f94437ccdee952564a7dcaae1ce8590f9050f8d3a1b798'
CAPTIONS = '89e3f14e2e27b88418f165363df6ccf2b0ba38400c5cb3d0cfdb414f9c85062c'
QA = 'a24964c15a6405134ced9d66c2aa118a837bb6f1269e884f20f8f7f078903403'
REVIEWED_AT = '2026-10-28T19:21:18.205302+00:00'
SCENE_COUNT = 16
CUE_COUNT = 99
RANGES = [(1, 7), (8, 14), (15, 19), (20, 26), (27, 33), (34, 41), (42, 45), (46, 52), (53, 58), (59, 65), (66, 71), (72, 76), (77, 83), (84, 88), (89, 93), (94, 99)]
SCREEN_BY_CUE = {27: '003-engine-filter-result', 79: '019-poi-saved-list', 80: '020-poi-reopened-values'}
REFERENCES = {1: {'Address': 'Address', 'Default Map Center GPS Coordinates': 'Default Map Center GPS Coordinates'},
 8: {'Engine': 'Engine'},
 15: {'Filter marker text': 'text filter', 'Hide labels': 'Hide labels'},
 20: {'Show units': 'Show units'},
 24: {'Show units': 'Show units'},
 27: {'Manage POIs': 'Manage POIs'},
 29: {'Add POI Type': 'Add POI Type'},
 34: {'Academy Staging': 'Academy Staging', 'Name': 'Name'},
 35: {'Is Destination': 'Is Destination'},
 37: {'Color': 'Color', 'Icon': 'Icon', 'Marker': 'Marker'},
 39: {'Icon': 'Icon'},
 42: {'Preview': 'preview'},
 43: {'No custom icon. The default marker is used.': 'the default marker is used'},
 45: {'Add POI Type': 'Add POI Type'},
 46: {'#0080ff': 'saved blue color', 'Academy Staging': 'Academy Staging'},
 47: {'Yes': 'Yes'},
 48: {'View': 'View'},
 49: {'Add': 'Add'},
 50: {'Add': 'Add'},
 51: {'Import': 'Import'},
 53: {'Latitude': 'latitude', 'Longitude': 'longitude'},
 54: {'Academy Staging Point': 'Academy Staging Point'},
 55: {'Note': 'note'},
 56: {'Add POI': 'Add POI'},
 60: {'-87.6523': 'longitude', '41.8721': 'latitude'},
 61: {'Showing 1 to 1 of 1 entries': 'one entry'},
 65: {'Edit': 'Edit'},
 66: {'Edit POI': 'Edit POI'},
 70: {'Save POI': 'Save POI'},
 72: {'Academy Staging Point': 'Academy Staging Point', 'Mapping': 'map', 'Show POIs': 'Show POIs'},
 78: {'Academy Staging': 'Academy Staging'},
 79: {'Edit': 'Edit'},
 80: {'Latitude': 'coordinates', 'Longitude': 'coordinates'},
 84: {'Show POIs': 'Show POIs'},
 89: {'Show POIs': 'Show POIs'},
 94: {'Stations, hydrants and points of interest': 'Stations, hydrants and points of interest'},
 95: {'Academy Staging': 'Academy Staging'},
 96: {'These icons do not change with status.': 'these icons do not change with status'}}
METHOD = 'The unchanged16 source JPEGs retain their hash-bound original-size reviews. All99 actual speech cues were matched to the frozen script and readable controls/results. Manage POIs is shown on the actual operating-map toolbar before the category list; the popup, saved List and Edit views are shown when mentioned. Changes occur only at genuine cue boundaries. No failed layer, route save, device location or operational suitability is inferred.'
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
                'method':'All 99 genuine Descript speech boundaries retained; full decoded audio and every timed cue passed signal/layout/script checks.'}},
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
