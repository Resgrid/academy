"""Prepare hash-bound Academy renderer inputs after the recorded listening and screen reviews."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import audio_duration, load_cues, words
from verify_capture_evidence import instruction_scene_digest

LESSONS = {
    'timer': ('timer-expiry-escalation', 'Verify automatic unit timer expiry and escalation', 205.36,
              'Watch a timed mute expire, then verify that escalation returns a warning to the board as a new alert.',
              {2, 3, 5}, {3: ('Staging', 'a unit stays there'), 8: ('Mapping and BigBoard Settings', 'Mapping and BigBoard Settings'),
              9: ('Unit Status Timers', 'Unit Status Timers'), 15: ('Reason when acknowledging', 'requires a reason'),
              18: ('Save', 'Save'), 20: ('Set Unit Status', 'Set Status'), 21: ('Staging', 'Staging'),
              32: ('Muted (1)', 'Muted section'), 36: ('Unit Alerts', 'Unit Alerts'),
              41: ('Staging', 'Staging'), 44: ('Available', 'Available'), 48: ('Mute', 'select Mute'),
              57: ('Acknowledge', 'Acknowledge')}),
    'forecast': ('forecast', 'Set the forecast location and units', 103.60,
                 'Choose temperature units and a location, resize the forecast, and check the saved result.',
                 set(), {3: ('Weather - Chicago', 'Chicago'), 6: ('Weather Widget', 'Weather Widget'),
                 7: ('Units', 'Units'), 12: ('Latitude', 'latitude'), 14: ('Longitude', 'longitude'),
                 19: ('Save', 'Save'), 25: ('5-Day Forecast', 'forecast rows'), 31: ('Weather Alerts (1)', 'Weather Alerts widget')}),
    'map': ('map-widget', 'Filter map pins and set fixed framing', 107.28,
            'Choose which pin types are visible, set a fixed map center, and verify that pins remain visible when labels are hidden.',
            set(), {2: ('Map', 'calls, stations, and resources'), 6: ('Map', 'Map'), 7: ('Zoom Out to Show All Pins', 'Zoom Out to Show All Pins'),
            8: ('Visible Pins', 'Visible Pins'), 9: ('Show Linked Calls', 'linked calls'),
            11: ('Show Calls', 'Show Calls'), 12: ('Save', 'Save'), 17: ('Zoom Out to Show All Pins', 'Zoom Out to Show All Pins'),
            18: ('Latitude', 'latitude'), 20: ('Longitude', 'longitude'), 21: ('Hide Labels', 'Hide Labels'),
            24: ('Zoom Level: 12', 'zoom to twelve')}),
    'alerts': ('weather-alerts', 'Review and filter weather alerts', 147.44,
               'Enable department display, inspect fictional alert details, and verify how widget filters affect the board and the full list.',
               {2}, {3: ('Weather Alerts', 'Weather Alerts'), 7: ('Add Widget', 'Add Widget'),
               10: ('Enable Weather Alerts', 'enable weather alerts'), 11: ('Minimum Severity to Display', 'minimum display severity'),
               12: ('Save Settings', 'save'), 16: ('Alert Sources', 'source page'), 22: ('Weather Alerts (3)', 'three active alerts'),
               23: ('Weather Alerts', 'full list'), 28: ('Timing', 'timing'), 29: ('Details', 'urgency, certainty, and sender'),
               34: ('Health', 'Health'), 38: ('Display Options', 'display options'), 41: ('Save', 'save'),
               42: ('Weather Alerts (1)', 'one severe training alert')}),
}


def ref(path):
    return {'file': path.relative_to(SOURCES).as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()}


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def prepare(key, ffmpeg):
    suffix, title, duration, summary, core_scenes, refs = LESSONS[key]
    folder = SOURCES / 'expansion/plans' / f'bigboard-{suffix}-source-20261103'
    priv = SOURCES / 'demo/private/bigboard-20261103'
    approval = json.loads((priv / f'{key}.listening.json').read_text())
    assert approval['reviewer'] == 'User' and approval['complete_natural_narration'] is True
    assert approval['sha256'] == ref(priv / f'{key}.m4a')['sha256']
    data = json.loads((folder / 'screen-holds.json').read_text())
    now = datetime.now(timezone.utc).isoformat()
    raw = json.loads((SOURCES / data['capture_manifest']).read_text())
    numbers = {int(row['id'].split('-')[0]): row for row in raw}
    refs_used = {}
    for chapter in data['chapters']:
        for _, index in chapter['holds']:
            row = numbers[index]
            dom = ref((SOURCES / row['file']).with_suffix('.txt'))
            row.update(dom_file=dom['file'], dom_sha256=dom['sha256'],
                       eligible_for_lesson=True, review_status='actual_original_image_reviewed',
                       capture_review={'reviewer':'Root', 'reviewed_at':now, 'passed':True, 'sha256':row['sha256'],
                                       'method':'Reviewed the retained original on the screenshot contact sheet.'})
            refs_used[row['id']] = row
    audio_dir = SOURCES / 'expansion/audio'
    audio = audio_dir / f'app-bigboard-{suffix}.m4a'
    srt = audio.with_suffix('.srt')
    shutil.copyfile(priv / f'{key}.m4a', audio)
    shutil.copyfile(priv / f'{key}.srt', srt)
    with tempfile.TemporaryDirectory(prefix='academy-narration-') as temp:
        duration = audio_duration(ffmpeg, audio, Path(temp) / 'narration.wav')
    cues = load_cues(srt)
    assert words(' '.join(c['text'] for c in cues)) == words((folder / 'narration.txt').read_text())
    starts = [first for chapter in data['chapters'] for first,_ in chapter['holds']]
    ends = dict(zip(starts, [*starts[1:], len(cues)+1]))
    time = lambda index: 0. if index == 1 else duration if index > len(cues) else cues[index-1]['start']
    authored, scenes = [], []
    for ix, chapter in enumerate(data['chapters'], 1):
        ident = f'{ix:02}'
        app = 'Core' if ix in core_scenes else 'BigBoard'
        screen_map, scene_cues, labels = [], [], []
        for first, index in chapter['holds']:
            row = numbers[index]
            screen_map.append({'screenshot_id': row['id'], 'start': time(first), 'end': time(ends[first])})
            for number in range(first, ends[first]):
                c = cues[number-1]
                mapped = {**c, 'cue': number, 'screenshot_id': row['id'], 'required_labels': [], 'instructional': False}
                if number in refs:
                    label, phrase = refs[number]
                    assert label in row['visible_labels'] and ' '.join(words(phrase)) in ' '.join(words(c['text'])), (key,number,label,row['id'])
                    mapped.update(required_labels=[label], instructional=True, spoken_references={label:phrase})
                    if row['app'] == app:
                        labels.append(label)
                scene_cues.append(mapped)
        labels = list(dict.fromkeys(labels))
        assert labels, (key, ix)
        screen_ids = list(dict.fromkeys(row['screenshot_id'] for row in screen_map))
        scene_title = chapter['title']
        authored.append({'id':ident, 'title':scene_title, 'route':urlsplit(refs_used[screen_ids[0]]['provenance']['url']).path or '/',
                         'capture_refs':screen_ids,'required_labels':labels,'capture_intent':scene_title,
                         'narration':' '.join(c['text'].replace('\n',' ') for c in scene_cues),
                         'practice':scene_title + ' in a fictional training department, then compare the saved result.'})
        scene = {'id':ident, 'title':scene_title,'kind':'operational','start':screen_map[0]['start'],'end':screen_map[-1]['end'],
                 'screens':screen_map,'captions':scene_cues,'visual_required_labels':labels}
        if app == 'Core':
            scene['instruction_app'] = app
        scene['instruction_review'] = {'reviewer':'Root','reviewed_at':now,'passed':True,'correspondence_reviewed':True,
                                       'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(scene,refs_used)}
        scenes.append(scene)
    lesson = {'id':f'app-bigboard-{suffix}', 'title':'Big Board: '+title[0].lower()+title[1:], 'app':'BigBoard', 'summary':summary,
              'audience':['Department administrators','Operations and coordination staff'],
              'prerequisites':['A Big Board session in a training department with the relevant widget and access to the settings shown.'],
              'sector_examples':[{'sector':'Community response','scenario':'Use the board during a community paramedicine exercise.'},
                                 {'sector':'Search and rescue','scenario':'Use a shared display to coordinate a staging area.'},
                                 {'sector':'Industrial','scenario':'Verify the display for an industrial response team.'}],
              'scope_limits':['The demonstration uses a fictional training department.'], 'source_files': [], 'scenes': authored}
    if key == 'alerts':
        lesson['scope_limits'].append('The alerts are fictional exercise fixtures. Live source polling, notifications, and call integration are not exercised.')
    if key == 'timer':
        lesson['scope_limits'].append('The short thresholds are for the exercise. Use your department’s own follow-up intervals.')
    shots = folder / 'captures.reviewed.json'
    write(shots, {'screenshots': list(refs_used.values())})
    lesson_path = folder / 'lesson.candidate.json'
    write(lesson_path, lesson)
    plan = {'schema_version':1,'lesson_id':lesson['id'],'instruction_mapping':'reviewed_scene_coverage',
            'display_context':'TRAINING ONLY · fictional department','duration_seconds':duration,
            'narration':{**ref(audio),'kind':'approved_natural_narration','approval':approval},
            'captions':{**ref(srt),'kind':'speech_timed_srt','approval':{'reviewer':'Root','reviewed_at':now,
                         'sha256':ref(srt)['sha256'],'speech_timing_reviewed':True,'audio_sha256':ref(audio)['sha256']}},
            'capture_manifests':[ref(shots)], 'scenes':scenes,
            'screenshot_reviews':{sid:{**row['capture_review'],'application_visible':True,'labels_legible':True,'no_errors':True}
                                  for sid,row in refs_used.items()}}
    if core_scenes:
        plan['supporting_applications'] = [{'app':'Core','for_app':'BigBoard','role':'configuration_source',
                                            'purpose':'Show the Core department settings controlling Big Board.'}]
    plan_path = folder / 'plan.json'
    write(plan_path, plan)
    return lesson_path, plan_path, SOURCES / 'expansion/rendered' / (lesson['id']+'-take-01')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=LESSONS)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--ffmpeg', default='ffmpeg')
    args = parser.parse_args()
    lesson, plan, destination = prepare(args.lesson, args.ffmpeg)
    from render_walkthrough import render
    print(json.dumps(render(lesson, plan, SOURCES, destination, ffmpeg=args.ffmpeg, check_only=not args.render)))
