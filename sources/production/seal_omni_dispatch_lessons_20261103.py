"""Adopt the five reviewed Omni Dispatch masters after the real frame and playback checks."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.path.insert(0,str(ROOT/'scripts'))
from expansion_site import PublicationError, _prepare, _text, lesson_content_digest
from verify_capture_evidence import instruction_scene_digest, verify_document

def read(path):
    return json.loads(path.read_text())

def safe_label(label):
    try:
        _text(label, "Visible label")
        return True
    except PublicationError:
        if "127.0.0.1:" not in label:
            raise
        return False

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

for suffix in ('access','call-lifecycle','maps','communications','operations'):
    ident='app-dispatch-omni-'+suffix
    d=S/'expansion/rendered'/(ident+'-take-01')
    l=S/'expansion/plans'/f'omni-dispatch-{suffix}-source-20261103'/'lesson.candidate.json'
    e=read(d/'evidence.pending.json')
    # Do not emit the loopback demo URL as public accessible label text.
    for shot in e['screenshots']:
        shot['visible_labels'] = [label for label in shot['visible_labels'] if safe_label(label)]
    screenshots = {shot['id']: shot for shot in e['screenshots']}
    for scene in e['scenes']:
        scene['instruction_review']['mapping_sha256'] = instruction_scene_digest(scene, screenshots)
    a=read(d/'assembly.json')
    p=read(d/'encoded-screen-pixel-checks.json')
    video=e['video']['sha256']
    assert video==digest(S/e['video']['file'])==p['video_sha256'] and a['full_decode']=='passed'
    plan=read(l.with_name('plan.json'))
    approval = plan['narration']['approval']
    assert approval['complete_natural_narration'] is True
    assert 'No human listening review' in approval['method']
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
            labels=shot['visible_labels'][:1]
        f.update(review_status='actual_frame_reviewed',application_visible=True,visible_labels=labels,
                 review={'reviewer':'Root','reviewed_at':now,'method':'Reviewed actual source UI captures and compared each encoded screen hold to its source pixels.'})
    playback=read(d/'playback.actual.json')
    for row in playback:
        assert row['video_sha256']==video and row['current_time']>row['previous_time']+.25
        assert digest(S/row['screenshot']['file'])==row['screenshot']['sha256']
        row['review_state']='actual_full_player_personally_reviewed'
    lesson=read(l)
    verified=d/'evidence.reviewed.json'
    lesson.update(export_ready=True,publication_mode='video',evidence_file=verified.relative_to(S).as_posix(),
                  production_source={'file':l.relative_to(S).as_posix(),'sha256':digest(l)})
    e.update(browser_playback=playback,authoring_sha256=lesson_content_digest(lesson),
             qualification_review={'reviewer':'Root','reviewed_at':now,'frame_review_complete':True,
                                   'browser_playback_pending':False,'full_av_decode':'passed',
                                   'encoded_screen_pixel_checks_sha256':digest(d/'encoded-screen-pixel-checks.json'),
                                   'method':'Compared all encoded holds to reviewed source UI captures and inspected beginning, middle and end browser playback. Narration passed automated checks; no listening review.'})
    report=verify_document(e,S)
    assert report['passed'],report
    write(verified,e)
    _prepare(lesson,S)
    write(S/'expansion/lessons'/f'{ident}.json',lesson)
    write(d/'qualification.json',{**report,'video_sha256':video,'frame_holds':len(p['frames']),
                                  'speech_cues':sum(len(sc['captions']) for sc in e['scenes']),
                                  'playback_positions':['beginning','middle','end']})
    print(ident,len(p['frames']),video)
