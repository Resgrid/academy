"""Retain the reviewed Responder certification screen/cue correspondence for this export.

The six source JPEGs were inspected at original size alongside all 49 actual
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
NAME = 'app-responder-certification-renewal'
BASE = Path('expansion/plans/app-responder-certification-renewal-capture-freeze-20261028')
FROZEN = '2d83007f268a160f24ff20d19ee33bdcbc957f17b06e6a345a7a2b77c75e5754'
MANIFEST = '7398af9a2bad3f1f437e211af5a53399f72f3ff8f0576c9288746d35ae4a128b'
AUDIO = 'ee70f653654fa8b8cdfe7a328a2dbf3257dae17f99dbde9f1518c2b21f9207fe'
CAPTIONS = '7963d9953934d53436eadf8e55098c986ab53e716461c0553540b3893db399b2'
QA = 'cfe296c745ba7b2a592172bf9ce26db6dec03ce7ec48846842b90fb273973679'
REVIEWED_AT = '2026-10-28T17:04:44+00:00'
RANGES = [(1,9),(10,16),(17,23),(24,31),(32,39),(40,49)]
# Exact phrases from actual speech cues refer to reviewed readable fields/values.
# Two adjacent cues speak the numeric date; the unchanged screen covers both.
REFERENCES = {
  1: {'My certifications':'My certifications'},
  4: {'Firefighter qualification':'Firefighter qualification'},
  5: {'Active':'Active','Number DEMO-CERT-1':'number DEMO-CERT-1'},
  11: {'Verified 2026-10-25':'verification date','Number DEMO-CERT-1':'number'},
  13: {'Renew':'Renew','New expiry date':'new expiry date','New number (optional)':'optional new number'},
  15: {'Hours':'Hours','Date (defaults to today)':'Date','Category (course, drill, conference)':'Category','What it was':'What it was'},
  17: {'0.25':'zero point two five'},
  18: {'Date (defaults to today)':'Date field indicates that it defaults to today'},
  19: {'Training software demonstration':'Training software demonstration'},
  20: {'TRAINING ONLY — Academy interface practice; no accredited credit claimed.':'no accredited credit is claimed'},
  21: {'Add hours':'Add hours'},
  25: {'Hours added.':'Hours added','0.25 continuing-education hours':'zero point two five continuing-education'},
  26: {'2026-10-26 · 0.25 h · Training software demonstration · TRAINING ONLY — Academy interface practice; no accredited credit claimed.':'stored entry includes its date, amount, category, and note'},
  27: {'Number DEMO-CERT-1':'number is still DEMO-CERT-1'},
  32: {'Renew':'Renew'},
  33: {'New expiry date':'New expiry date'},
  34: {'10/27/2028':'twenty-seven, twenty twenty-eight'},
  35: {'New number (optional)':'New number is optional'},
  37: {'Save renewal':'Save renewal'},
  41: {'Renewal saved.':'Renewal saved','Expires 2028-10-27 (732 days)':'October twenty-seven, twenty twenty-eight'},
  42: {'Number DEMO-CERT-1':'original number remains'},
  43: {'Awaiting verification':'Awaiting verification','Not verified by the department yet':'Not verified by the department yet'},
  45: {'0.25 continuing-education hours':'education entry'}
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
    assert qa['raw_captions']['cues'] == qa['corrected_captions']['cues'] == 49
    assert len(lesson['scenes']) == len(records) == len(RANGES) == 6
    for row in records:
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert sha(SOURCES/row['file']) == row['sha256']
    cues = load_cues(SOURCES/captions)
    assert len(cues) == 49
    duration, scenes = qa['audio']['duration_seconds'], []
    by_id = {r['id']:r for r in records}
    for index, ((first,last), authored, shot) in enumerate(zip(RANGES,lesson['scenes'],records)):
        assert words(' '.join(c['text'] for c in cues[first-1:last])) == words(authored['narration'])
        start = 0 if index == 0 else cues[first-1]['start']
        end = duration if index == 5 else cues[RANGES[index+1][0]-1]['start']
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
            'method':'All six untouched Responder JPEGs inspected at original size with all 49 actual export cues. Each paragraph stays on its corresponding form or saved result. Natural references map spoken field names and numbers to readable controls/values. No new-certification save, photo attachment or department verification is inferred.'}
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
                'method':'All 49 genuine Descript speech boundaries retained; full decoded audio and every timed cue passed signal/layout/script checks.'}},
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
            'cues':49,'duration':duration,'narration_approved':False,'rendered':False}))
    else:
        if not args.listening_review or not args.output:
            parser.error('Supply --listening-review and --output after genuine listening review.')
        plan,lesson_path = build(args.listening_review)
        assert not args.output.exists(), 'Preserve existing plans; choose a new output.'
        args.output.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
        recipe = validate_inputs(lesson_path,args.output,SOURCES)
        print(json.dumps({'passed':True,'scenes':len(recipe['scenes']),
            'cues':len(recipe['cues']),'duration':recipe['duration'],'rendered':False}))
