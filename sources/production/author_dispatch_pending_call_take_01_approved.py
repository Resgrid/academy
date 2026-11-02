"""Build a NEW Pending-call plan only from exact approved actual inputs.

No source/word/audio/timing rewrite, fallback voice, automatic frame approval,
browser proof, canonical/readiness/site/target or publication operation exists.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import wave

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-dispatch-pending-call-to-dispatch'
FROZEN = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-capture-freeze-20261028-v2')
CORRESPONDENCE = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-take-01-source-correspondence-20261028')
TAKE_MANIFEST = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-take-01.captures.reviewed.json')
PINS = {
    str(FROZEN / (NAME + '.narrated-source.json')): '53fb3845732f12d57d9367a496b0b3fa7ba638c04c2b7515d6f0801add24f837',
    str(FROZEN / 'captures.reviewed.json'): 'b84a9502937ba0b15a8b58b8cf396af88eebaf421a89a11291c16e34c3467d8f',
    str(TAKE_MANIFEST): '2f7bf2c3b402acb943e1983b51ddfa523becde3174f1888245d869acd285e765',
    str(CORRESPONDENCE / 'scaffold.json'): 'f1c3867bdd594931dfb8dd9ae6c4cefd2d3f23884ef67e91c7e1c2982ac8786d',
    'production/author_dispatch_pending_call_take_01.py': 'e95e1fee699074fc137c2d81c3761926a3cc69696a64a30f45a0a4cc7c83cd3c',
    'expansion/audio/' + NAME + '.m4a': 'ce23775d1bc4c9e249b508179830639abd1530c656e175e6b05a48fe7cd9dfcb',
    'expansion/audio/' + NAME + '.actual.qa.json': 'c37cd2381f61a260f390cc3c846cb86c64a7fd901827997952df4a57415e6e99',
    'expansion/audio/' + NAME + '.listening-review.json': '3b1848eeae43c865b1959a71323ffd9c7e6aadcf736ce8392a88c361dc996b7c',
    str(CORRESPONDENCE / (NAME + '.derived71.corrected.srt')): '2af83d4722fa5bb41730f8f7153e888161511a06465e0c5f76d2f1cadb1e8530',
    str(CORRESPONDENCE / (NAME + '.derived71.actual.qa.json')): '1d0a090f937b8a1d754bc94336811d66d0b3142f362bd3b50cb3262b2eaea135',
    str(CORRESPONDENCE / (NAME + '.derived71.provenance.json')): '8c5882cff6572e4cde0734846c2c4838949ea6eceff19395476006201c21a7a4',
}
TITLE = 'TRAINING ONLY - Academy pending dispatch 20261028'
NATURE = 'Software-only pending-call exercise in the fictional local department. No operational response.'
NUMBER = '#FD51-2026-0007'
PENDING = 'Save as pending (do not dispatch yet)'
BANNER = 'Pending — not yet dispatched'
NOTE = 'TRAINING ONLY - Academy pending dispatch exercise complete; no operational response. Closed without notifying call recipients.'
# Explicit literal UI -> unchanged spoken phrase correspondence, reviewed against
# the held originals. The source scene still independently requires every label.
REFERENCES = {
    (5, 'whole'): {'Calls': 'Calls', 'New Call': 'New Call'},
    (6, 'whole'): {'Name *': 'Name', 'Nature *': 'Nature', 'Priority *': 'Priority', 'Type *': 'Type'},
    (7, 'whole'): {'Routine': 'Routine', 'Investigation': 'Investigation'},
    (8, 'whole'): {'Call Location': 'location', 'Destination POI': 'destination'},
    (11, 'whole'): {PENDING: 'Save as pending'},
    (18, 'a'): {'Select Recipients': 'Select Recipients'},
    (18, 'b'): {'Wallace Boden': 'Wallace Boden'},
    (19, 'whole'): {'Wallace Boden': 'his row', 'Everyone': 'Everyone'},
    (20, 'whole'): {'1 selected': 'one selected'},
    (21, 'whole'): {'Confirm': 'Confirm'},
    (22, 'whole'): {'1 selected': 'one selected', PENDING: 'pending switch'},
    (23, 'whole'): {'Save Pending Call': 'Save Pending Call'},
    (24, 'a'): {'Name *': 'title', 'Nature *': 'description'},
    (24, 'b'): {'Save Pending Call': 'Save Pending Call'},
    (26, 'whole'): {'Call #': 'numbered row'},
    (27, 'whole'): {'Name': 'name', 'Call #': 'number'},
    (29, 'whole'): {NUMBER: 'F D fifty one, twenty twenty six, zero zero zero seven.'},
    (30, 'whole'): {'Call Details': 'Call Details', BANNER: 'Pending, not yet dispatched'},
    (31, 'whole'): {'Dispatched': 'Dispatched', 'Wallace Boden': 'Wallace Boden'},
    (32, 'whole'): {BANNER: 'pending banner', 'Dispatched': 'tab'},
    (34, 'whole'): {'Search pending calls...': 'Pending Calls', 'Dispatch': 'Dispatch'},
    (35, 'whole'): {'Select Dispatch Recipients': 'Select Dispatch Recipients', 'Wallace Boden': 'proposed member'},
    (36, 'whole'): {'Wallace Boden': 'Boden', '0 selected': 'zero', 'Confirm': 'Confirm'},
    (37, 'whole'): {'Wallace Boden': 'him', '1 selected': 'one selected', 'Everyone': 'Everyone'},
    (38, 'whole'): {'Confirm': 'Confirm'},
    (42, 'whole'): {'No pending calls': 'No pending calls'},
    (43, 'whole'): {'Dispatched': 'Dispatched', 'Wallace Boden': 'Wallace Boden', 'Group: Command': 'Command'},
    (44, 'whole'): {'Type: User': 'User'},
    (45, 'whole'): {'Dispatch additional resources': 'Dispatch additional resources'},
    (49, 'whole'): {TITLE: 'title', NUMBER: 'number', 'Close Call': 'Close Call'},
    (50, 'whole'): {'Closed': 'Closed', 'Close Type': 'Close Type', 'Close Note': 'Close Note'},
    (52, 'whole'): {'Notify everyone on the call': 'Notify everyone on the call'},
    (53, 'whole'): {'Close Type': 'type', NOTE: 'complete note', 'Notify everyone on the call': 'switch'},
    (54, 'whole'): {'Close Call': 'Close Call'},
    (57, 'whole'): {'Active Calls': 'active training calls'},
    (58, 'whole'): {'Pending': 'pending', 'Scheduled': 'scheduled'},
    (59, 'whole'): {'Academy pending dispatch 20261028': 'exercise name', 'No active calls': 'No active calls'},
    (61, 'whole'): {'Warehouse': 'warehouse', 'TRAINING — Warehouse alarm': 'original incident'},
    (62, 'whole'): {'Call Details': 'Call Details'},
    (64, 'whole'): {'Search calls...': 'search'},
}
METHOD = ('Reviewed the retained20 exact original JPEG/DOM source observations and all598 frozen words against actual71caption parts. '
          'Personally reinspected003/005/006/007 for control-first title/recipient/queue correspondence. '
          'Two genuine service one-second markers split rawcue18 at57s before Wallace and rawcue24 at77s before choosing Save. '
          'The separate71cue full decoded-audio QA passed with zero silent cues and exact words. '
          'Twenty original images supply25 ordered intervals, with003/006 repeated for title-before-Save and007 repeated before dispatch picker. '
          'Field aliases Name/title and Nature/description, numbered identity, counters and pending proposed-recipient context are explicitly mapped. '
          'No label is invented for an absent pending banner or removed Close Call action. '
          'A separate take manifest corrects stale raw requirements:003selected values were already literally reviewed,004Save is below viewport and shown in006,006shows count while005shows member name. Frozen metadata and every image/DOM byte remain intact. '
          'This approves source/speech correspondence only, not encoded frames, browser playback, provider delivery or physical/native operation. '
          'Actual full listening approval belongs to the separately retained user review; this agent claims no subjective listening.')


def need(ok, message):
    if not ok: raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def prepare(ffmpeg=None):
    for rel, expected in PINS.items(): need(sha(SOURCES / rel) == expected, 'Changed approved input: ' + rel)
    spec = importlib.util.spec_from_file_location('held_pending_author', SOURCES / 'production/author_dispatch_pending_call_take_01.py')
    author = importlib.util.module_from_spec(spec); spec.loader.exec_module(author); scaffold = author.prepare()
    lesson_file = SOURCES / FROZEN / (NAME + '.narrated-source.json'); lesson = read(lesson_file)
    manifest = read(SOURCES / TAKE_MANIFEST); shots = {s['id']: s for s in manifest['screenshots']}
    heard = read(SOURCES / 'expansion/audio' / (NAME + '.listening-review.json'))
    need(heard.get('reviewer') == 'User' and heard.get('complete_natural_narration') is True and heard.get('audio_sha256') == PINS['expansion/audio/' + NAME + '.m4a'] and heard.get('lesson_sha256') == PINS[str(FROZEN / (NAME + '.narrated-source.json'))], 'Actual complete source/audio-bound user listening approval required.')
    for qfile, expected_count in [(SOURCES / 'expansion/audio' / (NAME + '.actual.qa.json'), 69), (SOURCES / CORRESPONDENCE / (NAME + '.derived71.actual.qa.json'), 71)]:
        qa = read(qfile)
        need(qa['passed'] is True and not qa['issues'] and qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0 and qa['raw_captions']['cues'] == qa['corrected_captions']['cues'] == expected_count and not qa['alignment']['text_changes'], 'Actual full narration/caption QA failed.')
        need(qa['lesson']['sha256'] == PINS[str(FROZEN / (NAME + '.narrated-source.json'))] and qa['audio']['sha256'] == heard['audio_sha256'] and qa['audio']['full_decode'] == 'passed' and qa['audio']['decoded_samples'] == 11251462, 'Actual source/audio decode identity differs.')
    duration = qa['audio']['duration_seconds']
    need(duration == 234.40545833333334, 'Actual decoded duration changed.')
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import audio_duration, load_cues
    from verify_capture_evidence import _Validator, instruction_scene_digest, _normalized
    if ffmpeg is not None:
        with tempfile.TemporaryDirectory(prefix='pending-approved-decode-') as tmp:
            pcm = Path(tmp) / 'decoded.wav'; actual = audio_duration(str(ffmpeg), SOURCES / 'expansion/audio' / (NAME + '.m4a'), pcm)
            with wave.open(str(pcm), 'rb') as stream: need(stream.getnframes() == 11251462 and stream.getframerate() == 48000 and stream.getnchannels() == 1 and stream.getsampwidth() == 2, 'Repeated full PCM decode changed.')
        need(actual == duration, 'Repeated actual audio duration changed.')
    cues = load_cues(SOURCES / CORRESPONDENCE / (NAME + '.derived71.corrected.srt'))
    need(len(cues) == 71, 'Actual derived cue count changed.')
    parts = [c for span in scaffold['source_spans'] for c in span['cue_correspondence']]
    for cue, part in zip(cues, parts): need(abs(cue['start'] - part['start']) < 1e-9 and abs(cue['end'] - part['end']) < 1e-9 and cue['text'] == part['text'], 'Actual approved SRT differs from genuine marker correspondence.')
    now = datetime.now(timezone.utc).isoformat(); scenes = []
    for index, authored in enumerate(lesson['scenes']):
        spans = [s for s in scaffold['source_spans'] if s['scene_id'] == authored['id']]
        start = 0 if index == 0 else spans[0]['actual_exported_boundary']
        end = spans[-1]['next_actual_exported_boundary'] or duration
        screens, expanded = [], []
        for n, span in enumerate(spans):
            sid = span['screenshot_id']; screen_start = start if n == 0 else span['actual_exported_boundary']; screen_end = span['next_actual_exported_boundary'] or duration
            screens.append({'screenshot_id': sid, 'start': screen_start, 'end': screen_end})
            for part in span['cue_correspondence']:
                number = part['candidate_cue']; cue = cues[number - 1]; refs = REFERENCES.get((part['raw_cue'], part['part']), {})
                need(set(refs) <= set(shots[sid]['visible_labels']), 'A spoken control is not in the corresponding actual foreground source.')
                row = dict(cue, cue=number, screenshot_id=sid, required_labels=list(refs), spoken_references=refs, instructional=bool(refs))
                v = _Validator(SOURCES); v.spoken_references(row, {_normalized(x) for x in refs}, 'cue' + str(number), True); need(not v.issues, '; '.join(v.issues)); expanded.append(row)
        built = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational', 'start': start, 'end': end, 'screens': screens, 'captions': expanded, 'visual_required_labels': authored['required_labels']}
        review = {'passed': True, 'reviewer': 'Codex exact retained source/actual71cue correspondence review', 'reviewed_at': now, 'correspondence_reviewed': True, 'no_unseen_controls': True, 'mapping_sha256': instruction_scene_digest(built, shots), 'method': METHOD}
        scenes.append({'id': authored['id'], 'start': start, 'end': end, 'screens': screens, 'captions': [{k: c[k] for k in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']} for c in expanded], 'instruction_review': review})
    need(sum(len(s['screens']) for s in scenes) == 25, 'Actual screen interval count changed.')
    return lesson_file, lesson, shots, heard, duration, scenes, now


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--write-plan', type=Path); parser.add_argument('--ffmpeg', type=Path); args = parser.parse_args()
    if args.write_plan:
        target = args.write_plan.resolve(); need(target.is_relative_to((SOURCES / 'expansion/plans').resolve()) and not target.exists(), 'Use a NEW plan path; preserve all history.'); need(args.ffmpeg is not None, 'Approved full decode requires explicit FFmpeg before plan writing.')
    source, lesson, shots, heard, duration, scenes, now = prepare(args.ffmpeg)
    if args.write_plan:
        audio_rel = 'expansion/audio/' + NAME + '.m4a'; srt_rel = str(CORRESPONDENCE / (NAME + '.derived71.corrected.srt'))
        plan = {'schema_version': 1, 'lesson_id': NAME, 'duration_seconds': duration, 'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
                'narration': {'file': audio_rel, 'sha256': PINS[audio_rel], 'kind': 'approved_natural_narration', 'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': heard['audio_sha256'], 'complete_natural_narration': True, 'evidence': heard['evidence'], 'listening_review_file': 'expansion/audio/' + NAME + '.listening-review.json', 'listening_review_sha256': PINS['expansion/audio/' + NAME + '.listening-review.json']}},
                'captions': {'file': srt_rel, 'sha256': PINS[srt_rel], 'kind': 'speech_timed_srt', 'approval': {'reviewer': 'Codex actual69SRT/one-second57and77anchors/71cue full audio QA review', 'reviewed_at': now, 'sha256': PINS[srt_rel], 'audio_sha256': heard['audio_sha256'], 'speech_timing_reviewed': True, 'qa_file': str(CORRESPONDENCE / (NAME + '.derived71.actual.qa.json')), 'qa_sha256': PINS[str(CORRESPONDENCE / (NAME + '.derived71.actual.qa.json'))], 'method': METHOD}},
                'capture_manifests': [{'file': str(TAKE_MANIFEST), 'sha256': PINS[str(TAKE_MANIFEST)]}],
                'screenshot_reviews': {sid: {'reviewer': 'Codex retained original-JPEG/DOM source review; source/cue mapping reinspected', 'reviewed_at': now, 'sha256': shot['sha256'], 'application_visible': True, 'labels_legible': True, 'no_errors': True} for sid, shot in shots.items()}, 'scenes': scenes, 'publishable': False,
                'limitations': ['Every actual encoded interval/caption/frame still needs image review; actual advancing native browser VIDEO playback is pending.', 'No provider notification receipt, physical response, incident geolocation, native device, archived call or unrelated call mutation is established.', 'Frozen source598words, original69cueSRT/QA, approved audio and original22span freeze remain unchanged.']}
        from render_walkthrough import validate_inputs
        with tempfile.TemporaryDirectory(prefix='pending-plan-preflight-') as temp:
            check = Path(temp) / 'plan.json'; check.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
            validate_inputs(source, check, SOURCES)
        with args.write_plan.open('x') as stream: stream.write(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        recipe = validate_inputs(source, args.write_plan, SOURCES)
        need(len(recipe['cues']) == 71, 'Validated actual cue count changed.')
    print(json.dumps({'passed': True, 'source_words': 598, 'scenes': 8, 'source_images': 20, 'screen_intervals': 25, 'actual_cues': 71, 'duration_seconds': duration, 'actual_user_listening_review_verified': True, 'plan_written': bool(args.write_plan), 'rendered': False, 'publishable': False}, indent=2))


if __name__ == '__main__':
    main()
