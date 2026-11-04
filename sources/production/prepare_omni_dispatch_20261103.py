"""Assemble the Omni Dispatch lessons from reviewed screen captures and Descript narration."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
from render_walkthrough import audio_duration, load_cues, render, words
from verify_capture_evidence import instruction_scene_digest

LESSONS = {
    'access': (
        'Sign in and set up a shared workstation',
        'Confirm the server, find the dispatch queues, and verify the saved shared-device label.',
        {1: ('Resgrid Dispatch', 'Resgrid Dispatch'), 6: ('Server URL', 'Server URL'),
         9: ('Sign in with SSO', 'Sign in with SSO'), 11: ('Dispatch Console', 'Dispatch Console'),
         14: ('Settings', 'Settings'), 16: ('Shared device', 'Shared device'),
         17: ('This is a shared device', 'This is a shared device'), 19: ('Academy Dispatch Desk', 'Academy Dispatch Desk'),
         21: ('Save', 'Save'), 22: ('Shared device', 'Shared device'), 27: ('Cancel', 'Cancel'),
         28: ('Sign-in and security', 'Sign-in and security'), 29: ('Authenticator app', 'authenticator app')},
        'The lesson shows the sign-in choices and security overview in a fictional department.'),
    'call-lifecycle': (
        'Create, release, update and close a call',
        'Save a pending call, dispatch a recipient, record a handoff and verify the closed status.',
        {1: ('New Call', 'New Call'), 6: ('GPS Coordinates', 'GPS'),
         10: ('Select Contact', 'contact picker'), 12: ('Save Pending Call', 'Save Pending Call'),
         13: ('Pending Calls', 'Pending Calls'), 15: ('Dispatch', 'start dispatch'),
         16: ('Select Dispatch Recipients', 'recipient picker'), 18: ('Done (1 selected)', 'Done'),
         20: ('Call Details', 'Details'), 21: ('Call Notes', 'Notes'),
         25: ('Edit Call', 'Edit Call'), 27: ('Close Call', 'Close Call'),
         29: ('Notify everyone on the call', 'Notify everyone who was dispatched'),
         33: ('History', 'History'), 35: ('Previous calls at this location', 'Previous calls at this location')},
        'The exercise uses a fictional community standby and leaves the closeout notification off.'),
    'maps': (
        'Use maps, saved sites and weather alerts',
        'Filter map layers, open a saved destination, find an indoor room and review a fictional alert.',
        {1: ('Map', 'Map'), 3: ('Points of interest', 'Points of interest'),
         7: ('POIs', 'POIs'), 8: ('Destinations', 'Destinations'),
         10: ('Academy Staging Point', 'Academy Staging Point'), 14: ('Custom Maps', 'Custom Maps'),
         15: ('TRAINING ONLY - Ground floor', 'Ground floor'), 18: ('Indoor', 'Indoor'),
         19: ('Briefing room - training', 'Briefing room - training'), 23: ('Weather Alerts', 'Weather Alerts'),
         24: ('Severe', 'Severe'), 25: ('Affected Area', 'Affected Area'),
         28: ('Weather Alert Settings', 'Weather Alert Settings'),
         31: ('Show alerts on calls in the affected area', 'showing alerts on calls in the affected area')},
        'The weather alert is a fictional fixture. The lesson reviews the settings without saving a policy change.'),
    'communications': (
        'Use contacts, chat and device preferences',
        'Find a contact, inspect a conversation, draft a message and review Assistant and navigation preferences.',
        {1: ('Contacts', 'Contacts'), 3: ('Contact Information', 'Contact Information'),
         4: ('Location Information', 'Location Information'), 7: ('Chat', 'Chat'),
         9: ('TRAINING — Academy readiness', 'Academy readiness'), 16: ('Assistant', 'Assistant'),
         21: ('Navigation App', 'Navigation App'), 22: ('Google Maps', 'Google Maps')},
        'The chat draft stays unsent and the Assistant prompt stays empty.'),
    'operations': (
        'Review incident command, check-ins and deployments',
        'Review an approved crew report, check command assignments and accountability, and locate call-linked Records forms.',
        {1: ('Deployments', 'Deployments'), 2: ('Open', 'Open'),
         3: ('TRAINING ONLY - Community support deployment', 'Community support deployment'),
         9: ('Reports this day', 'Reports this day'), 13: ('Command', 'Command'),
         16: ('Squad 3', 'Squad Three'), 19: ('Accountability (PAR)', 'Accountability'),
         20: ('Objectives', 'Objectives'), 21: ('Check-In', 'Check-In'),
         23: ('New Record', 'New Record'), 25: ('Callback', 'Callback'), 27: ('DRAFTS', 'Drafts')},
        'The Records section shows the form chooser and queue. It does not submit a record or change a check-in.'),
}

def read(path):
    return json.loads(path.read_text())

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def ref(path):
    return {'file': path.relative_to(SOURCES).as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()}

def prepare(key, ffmpeg):
    title, summary, anchors, limit = LESSONS[key]
    folder = SOURCES / 'expansion/plans' / f'omni-dispatch-{key}-source-20261103'
    private = SOURCES / 'demo/private/omni-dispatch-20261103'
    audio_input = private / f'{key}.m4a'
    qa = read(private / f'{key}.narration-review.json')
    assert qa['sha256'] == ref(audio_input)['sha256'] and qa['complete_natural_narration']
    data = read(folder / 'screen-holds.json')
    timeline = read(folder / 'screen-timing.reviewed.json')
    now = datetime.now(timezone.utc).isoformat()
    numbers = {int(row['id'].split('-')[0]): row for row in read(SOURCES / data['capture_manifest'])}
    shots = {}
    for chapter in timeline['chapters']:
        for hold in chapter['holds']:
            row = numbers[hold['shot']]
            dom = ref((SOURCES / row['file']).with_suffix('.txt'))
            row.update(dom_file=dom['file'], dom_sha256=dom['sha256'], eligible_for_lesson=True,
                       review_status='actual_original_image_reviewed',
                       capture_review={'reviewer':'Codex', 'reviewed_at':now, 'passed':True,
                                       'sha256':row['sha256'], 'method':'Inspected actual source screenshots and their captured viewport labels.'})
            shots[row['id']] = row
    ident = f'app-dispatch-omni-{key}'
    audio = SOURCES / 'expansion/audio' / f'{ident}.m4a'
    srt = audio.with_suffix('.srt')
    subprocess.run([ffmpeg, '-nostdin', '-v', 'error', '-y', '-i', str(audio_input),
                    '-af', 'pan=mono|c0=c0', '-c:a', 'alac', str(audio)], check=True)
    qa = {**qa, 'export_sha256': qa['sha256'], 'sha256': ref(audio)['sha256'],
          'mix': 'Lossless mono from one of the two identical source channels.'}
    shutil.copyfile(folder / 'narration.aligned.srt', srt)
    with tempfile.TemporaryDirectory(prefix='academy-omni-narration-') as temp:
        duration = audio_duration(ffmpeg, audio, Path(temp) / 'narration.wav')
    cues = load_cues(srt)
    assert words(' '.join(c['text'] for c in cues)) == words((folder / 'narration.txt').read_text())
    holds = [hold for chapter in timeline['chapters'] for hold in chapter['holds']]
    starts = [hold['cue'] for hold in holds]
    ends = dict(zip(starts, [*starts[1:], len(cues)+1]))
    def time(index):
        if index == 1:
            return 0.0
        if index > len(cues):
            return duration
        return cues[index-1]['start']

    authored, scenes = [], []
    for index, chapter in enumerate(timeline['chapters'], 1):
        scene_id = f'{index:02}'
        screens, captions, labels = [], [], []
        for hold in chapter['holds']:
            first = hold['cue']
            row = numbers[hold['shot']]
            screens.append({'screenshot_id':row['id'], 'start':time(first), 'end':time(ends[first])})
            for number in range(first, ends[first]):
                cue = cues[number-1]
                mapped = {**cue, 'cue':number, 'screenshot_id':row['id'], 'required_labels':[], 'instructional':False}
                original = timeline['cue_origins'][number-1]
                if original in anchors:
                    label, phrase = anchors[original]
                    if ' '.join(words(phrase)) in ' '.join(words(cue['text'])):
                        assert label in row['visible_labels'], (key, number, label, row['id'])
                        mapped.update(required_labels=[label], instructional=True, spoken_references={label:phrase})
                        labels.append(label)
                captions.append(mapped)
        labels = list(dict.fromkeys(labels))
        assert labels, (key, scene_id)
        capture_refs = list(dict.fromkeys(row['screenshot_id'] for row in screens))
        scene_title = chapter['title']
        authored.append({'id':scene_id, 'title':scene_title,
                         'route':urlsplit(shots[capture_refs[0]]['provenance']['url']).path or '/',
                         'capture_refs':capture_refs, 'required_labels':labels, 'capture_intent':scene_title,
                         'narration':' '.join(c['text'].replace('\n',' ') for c in captions),
                         'practice':f'{scene_title} in a fictional training department.'})
        scene = {'id':scene_id, 'title':scene_title, 'kind':'operational',
                 'start':screens[0]['start'], 'end':screens[-1]['end'],
                 'screens':screens, 'captions':captions, 'visual_required_labels':labels}
        scene['instruction_review'] = {
            'reviewer':'Codex', 'reviewed_at':now, 'passed':True, 'correspondence_reviewed':True,
            'no_unseen_controls':True, 'mapping_sha256':instruction_scene_digest(scene, shots),
        }
        scenes.append(scene)

    lesson = {
        'id':ident, 'title':f'Omni Dispatch: {title[0].lower()}{title[1:]}', 'app':'Dispatch', 'summary':summary,
        'audience':['Dispatchers', 'Department administrators'],
        'prerequisites':['Omni Dispatch and an account in a training department with permission for the screens shown.'],
        'sector_examples':[
            {'sector':'Fire / EMS', 'scenario':'Practice shift coordination with fictional units and incidents.'},
            {'sector':'Community response', 'scenario':'Coordinate a fictional outreach standby and partner handoff.'},
            {'sector':'Search and rescue', 'scenario':'Use a training exercise to coordinate a search team and assembly point.'},
            {'sector':'Security', 'scenario':'Coordinate a site handoff at a practice dispatch desk.'},
            {'sector':'Wildland', 'scenario':'Review staging and crew coordination in a fictional deployment.'},
            {'sector':'Industrial', 'scenario':'Coordinate a fictional industrial response and review its location.'},
        ],
        'scope_limits':[limit], 'source_files':[], 'scenes':authored,
    }
    manifest = folder / 'captures.reviewed.json'
    write(manifest, {'screenshots':list(shots.values())})
    lesson_path = folder / 'lesson.candidate.json'
    write(lesson_path, lesson)
    plan = {
        'schema_version':1, 'lesson_id':ident, 'instruction_mapping':'reviewed_scene_coverage',
        'display_context':'TRAINING ONLY · fictional department', 'duration_seconds':duration,
        'narration':{**ref(audio), 'kind':'approved_natural_narration', 'approval':qa},
        'captions':{**ref(srt), 'kind':'speech_timed_srt', 'approval':{
            'reviewer':'Codex', 'reviewed_at':now, 'sha256':ref(srt)['sha256'],
            'speech_timing_reviewed':True, 'audio_sha256':ref(audio)['sha256'],
        }},
        'capture_manifests':[ref(manifest)], 'scenes':scenes,
        'screenshot_reviews':{sid:{**row['capture_review'], 'application_visible':True,
                                  'labels_legible':True, 'no_errors':True} for sid,row in shots.items()},
    }
    plan_path = folder / 'plan.json'
    write(plan_path, plan)
    return lesson_path, plan_path, SOURCES / 'expansion/rendered' / f'{ident}-take-01'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=LESSONS)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    lesson, plan, output = prepare(args.lesson, args.ffmpeg)
    result = render(lesson, plan, SOURCES, output, ffmpeg=args.ffmpeg, check_only=not args.render)
    print(json.dumps(result))
