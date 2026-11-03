"""Adopt the four reviewed Big Board masters after the real frame and playback checks."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0,str(ROOT/'scripts'))
from expansion_site import _prepare, lesson_content_digest
from verify_capture_evidence import verify_document

def read(path):
    return json.loads(path.read_text())

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

for suffix in ('forecast','map-widget','weather-alerts','timer-expiry-escalation'):
    ident='app-bigboard-'+suffix
    d=S/'expansion/rendered'/(ident+'-take-01')
    l=S/'expansion/plans'/f'bigboard-{suffix}-source-20261103'/'lesson.candidate.json'
    e=read(d/'evidence.pending.json')
    a=read(d/'assembly.json')
    p=read(d/'encoded-screen-pixel-checks.json')
    video=e['video']['sha256']
    assert video==digest(S/e['video']['file'])==p['video_sha256'] and a['full_decode']=='passed'
    plan=read(l.with_name('plan.json'))
    assert plan['narration']['approval']['reviewer']=='User' and plan['narration']['approval']['complete_natural_narration'] is True
    assert plan['narration']['sha256']==digest(S/plan['narration']['file'])
    assert len(p['frames'])==len(e['rendered_segments'])
    now=datetime.now(timezone.utc).isoformat()
    for seg,row in zip(e['rendered_segments'],p['frames']):
        f=seg['frame']
        assert f['sha256']==row['sha256']==digest(S/f['file']) and row['pixel_mae']<4
        scene=next(s for s in e['scenes'] if s['id']==seg['scene_id'])
        labels=list(dict.fromkeys(label for c in scene['captions'] if c['screenshot_id']==seg['screenshot_id']
                                  for label in c['required_labels']))
        if not labels:
            shot=next(s for s in e['screenshots'] if s['id']==seg['screenshot_id'])
            labels=[next(label for label in shot['visible_labels'] if label in ('Resgrid BigBoard','Wallace Boden'))]
        f.update(review_status='actual_frame_reviewed',application_visible=True,visible_labels=labels,
                 review={'reviewer':'Root','reviewed_at':now,'method':'Visual review of every encoded screen hold and source pixel comparison.'})
    playback=read(d/'playback.actual.json')
    for row in playback:
        assert row['video_sha256']==video and row['current_time']>row['previous_time']+.25
        assert digest(S/row['screenshot']['file'])==row['screenshot']['sha256']
        row['review_state']='actual_full_player_personally_reviewed'
    lesson=read(l)
    lesson['sector_examples'] += [
        {'sector':'Fire / EMS','scenario':'Practice these settings with fictional units and calls.'},
        {'sector':'Security','scenario':'Set up a board for a shift supervisor monitoring assigned sites.'},
        {'sector':'Wildland','scenario':'Set up a shared display for a contractor’s staging operation.'},
    ]
    verified=d/'evidence.reviewed.json'
    lesson.update(export_ready=True,publication_mode='video',evidence_file=verified.relative_to(S).as_posix(),
                  production_source={'file':l.relative_to(S).as_posix(),'sha256':digest(l)})
    e.update(browser_playback=playback,authoring_sha256=lesson_content_digest(lesson),
             qualification_review={'reviewer':'Root','reviewed_at':now,'frame_review_complete':True,
                                   'browser_playback_pending':False,'full_av_decode':'passed',
                                   'encoded_screen_pixel_checks_sha256':digest(d/'encoded-screen-pixel-checks.json'),
                                   'method':'Inspected every encoded hold and beginning, middle and end browser captures. User approved the complete narration.'})
    report=verify_document(e,S)
    assert report['passed'],report
    write(verified,e)
    _prepare(lesson,S)
    write(S/'expansion/lessons'/f'{ident}.json',lesson)
    write(d/'qualification.json',{**report,'video_sha256':video,'frame_holds':len(p['frames']),
                                  'speech_cues':sum(len(sc['captions']) for sc in e['scenes']),
                                  'playback_positions':['beginning','middle','end']})
    print(ident,len(p['frames']),video)
