"""Guarded actual71cue Dispatch scheduled-call author.

Default is read-only. --assemble creates NEW renderer inputs only after genuine
Root complete timed-map/learner-metadata review and complete User listening.
No rendering, browser/app action, dispatch, canonical/site/target or Git work.
Frozen source packages, all images and actual audio/SRT bytes stay unchanged.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'sources'
FREEZE=Path('expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2')
PROPOSAL=Path('expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030')
FINAL=Path('expansion/plans/app-dispatch-schedule-create-edit-take-01-final-inputs-20261030')
LESSON=FREEZE/'lesson.source-candidate.json'
AUDIO=Path('expansion/audio/app-dispatch-schedule-create-edit.m4a')
QA=Path('expansion/audio/app-dispatch-schedule-create-edit.actual.qa.json')
RAW=Path('expansion/audio/app-dispatch-schedule-create-edit-generated-20261030.raw.srt')
CAPTIONS=Path('expansion/audio/app-dispatch-schedule-create-edit.actual.corrected.srt')
HEARING=Path('expansion/audio/app-dispatch-schedule-create-edit.listening-review.json')
PUBLIC=PROPOSAL/'lesson.learner-projection.proposed.json'
PINS = {'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/lesson.source-candidate.json': '9cc1ac01b0c6819313eb50f6a91665565696a0f3c4afe593bcb0b85c3e586385', 'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/narration.txt': '2ea2b766512baa4102ebb9ef632fe65d3bf218b0072248be4a9eb47a14214f1e', 'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/screen-sequence.untimed.json': '697d7ec15d0bb7112c4b8c1359cc226505dff119a6f3a9bb7dacc3e5aac2fc44', 'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/captures.reviewed.json': 'e65b2fba62899af0414bda6f35509d18339ef9f290395740439f1384db95ab6d', 'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/inventory.json': '5c48c1c35566c84fba22a020f4ec7134d1ef722d32c2847eeb09356a8b207421', 'expansion/plans/app-dispatch-schedule-create-edit-source-candidate-20261030-v2/verify_source.py': '2b4fef42ed6ae1516234560c529172f4add787f5cf4744d5d6800d61b809890d', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/correspondence.proposed.json': '213a8d823367331d2058038ed2319473a16ca119a72cf273aa81a88a1d69d8cc', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/cue-screen-correspondence.txt': 'd6bc3a001db9b76fdc1f3190d44c9acc1e91e78ba3a315bedd66ed2fe3ccb54c', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/captures.source-relative.json': '37c71ad648b009c7c560e7eaecae78186b96f076212e87eeff3efe2b7b29f21a', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/caption-layout-measurements.json': '2004e5f43af2e8806dd4b34911872a4b8908b1fecb02d44aa02b1207bd01acd6', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/lesson.learner-projection.proposed.json': '45b5850dc8b06660ba529be15be1fa0e04f8fe791e364ce34d7b84006ffb11bd', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/practice-and-sector-prompts.txt': '324572a69e15ff8b7c2345867ad3a1f9cc82d90fdbdd77f2c20ead813c426fd9', 'expansion/plans/app-dispatch-schedule-create-edit-proposed71-correspondence-20261030/handoff.json': 'afc843c0410e2ba062af126c384ec0d0edb97f30a09e0e211474a62c53fd2acb', 'expansion/audio/app-dispatch-schedule-create-edit.m4a': 'feca025414f0712c42b33a329a3db601e171b6a421245ebd0ccbd70eae6830e8', 'expansion/audio/app-dispatch-schedule-create-edit.actual.qa.json': '0869c69d3b7f1c888e541298bc02cb21f1888c97c611d5d44d365954a6f42649', 'expansion/audio/app-dispatch-schedule-create-edit.actual.corrected.srt': 'ac9601cc0deab5896d41e9a9ba3d30aec250cfc1acddd3fc9dde76663e0fdc80', 'expansion/audio/app-dispatch-schedule-create-edit-generated-20261030.raw.srt': 'fb0d209b0d150e8bfa792c11e477447b4f59558e6727966c42771c4c659246b1', 'expansion/audio/app-dispatch-schedule-create-edit.listening-review.json': 'eae5a5c66b6b044bf3b3c924616358ccd1cdab3f0f4988eef02d7684178efb34', 'expansion/plans/app-dispatch-schedule-create-edit-narration-brief-20261030/root-complete-source-script-review.json': 'ac4f73bcba24132a6cbc36cf1b931c5b2e100ffe8e1dd5bbe54e06e991d6f882'}
CODE_PINS = {'scripts/render_walkthrough.py': '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881', 'scripts/verify_capture_evidence.py': '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa', 'scripts/expansion_site.py': 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8'}

def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def normalized(value):
    return ' '.join(value.split()).casefold()


def safe_source_path(value):
    require(isinstance(value, str) and value and '\\' not in value, 'Use a portable source-relative path.')
    path = Path(value)
    require(not path.is_absolute() and not re.search(r'(?i)(?:://|www\.)', value), 'Require a local source-relative path.')
    require(not any(p in {'.', '..', 'private', '.git', 'node_modules'} or p.startswith('.env') for p in path.parts), 'Unsafe source path.')
    absolute = S / path
    require(absolute.resolve().is_relative_to(S.resolve()), 'Source path escapes source root.')
    require(not any(p.is_symlink() for p in [absolute, *absolute.parents] if p.is_relative_to(S)), 'Symlinked source is not permitted.')
    return absolute


def actual_timestamp(value, earliest=None):
    require(isinstance(value, str), 'Actual review requires a timezone-aware timestamp.')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None and result <= datetime.now(timezone.utc), 'Actual review cannot be naive or future dated.')
    if earliest is not None:
        require(result >= actual_timestamp(earliest), 'Review predates the actual input QA.')
    return result


def receipt(value, digest):
    require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), 'Supply the exact genuine receipt SHA256.')
    path = safe_source_path(value)
    require(path.is_file(), 'Actual review receipt is absent; assembly remains blocked.')
    require(sha(path) == digest, 'Actual review receipt hash differs.')
    record = read(path)
    require(isinstance(record, dict), 'Review receipt must be an object.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)', json.dumps(record)), 'Public review receipt must be URL free.')
    return record


def preflight():
    require(__debug__, 'Use ordinary Python; optimized execution is forbidden.')
    for relative,digest in PINS.items():
        require(sha(safe_source_path(relative))==digest,'Immutable input changed: '+relative)
    for relative,digest in CODE_PINS.items():
        require(sha(ROOT/relative)==digest,'Pinned renderer/export gate changed.')
    spec=importlib.util.spec_from_file_location('frozen_dispatch_schedule_archive',S/FREEZE/'verify_source.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    archived=checker.verify(S/FREEZE)
    require(archived['passed'] is True and archived['accepted_images']==9 and archived['archival_supporting_images']==1,'Frozen operational/archival boundary changed.')
    sys.path.insert(0,str(ROOT/'scripts'))
    from render_walkthrough import load_cues,words
    from verify_capture_evidence import _Validator,_normalized,_image_dimensions,instruction_scene_digest
    from expansion_site import lesson_content_digest
    lesson=read(S/LESSON);public=read(S/PUBLIC);proposal=read(S/PROPOSAL/'correspondence.proposed.json')
    qa=read(S/QA);manifest=read(S/PROPOSAL/'captures.source-relative.json')
    cues=load_cues(S/CAPTIONS);raw=load_cues(S/RAW)
    require(len(cues)==len(raw)==71,'Actual whole caption count changed.')
    require(all(a['start']==b['start'] and a['end']==b['end'] for a,b in zip(cues,raw)),'Caption endpoint moved.')
    require(words(' '.join(x['text'] for x in cues))==words(' '.join(x['narration'] for x in lesson['scenes'])),'Corrected words differ from the frozen complete script.')
    require(words(' '.join(x['text'] for x in raw))==['warm','lulu']+words(' '.join(x['text'] for x in cues)),'Raw export change is not exactly the recorded leading speaker label.')
    require(len(lesson['scenes'])==12 and len(words(' '.join(x['text'] for x in cues)))==690,'Frozen paragraph/normalized-word counts changed.')
    require([{k:v for k,v in x.items() if k!='practice'} for x in public['scenes']]==lesson['scenes'],'Learner metadata changed spoken words, source labels or scene structure.')
    require(lesson_content_digest(public)=='d40a0b91d973f26c3bae039502c495acec9dc2d8f81a314ba3d34b7564091f82','Proposed learner content changed.')
    require(qa['passed'] is True and qa['issues']==qa['possible_speech_gaps']==[],'Actual audio QA has unresolved issues.')
    require(qa['lesson']['sha256']==PINS[str(LESSON)] and qa['audio']['sha256']==PINS[str(AUDIO)] and qa['audio']['full_decode']=='passed','Actual complete audio/source identity changed.')
    duration=qa['audio']['decoded_samples']/qa['audio']['sample_rate']
    require(duration==qa['audio']['duration_seconds']==252.49379166666668 and qa['audio']['decoded_samples']==12119702 and qa['audio']['sample_rate']==48000,'Measured complete PCM duration changed.')
    require(qa['alignment']['match_ratio']==0.9985 and qa['alignment']['text_changes']==[{'operation':'delete','transcription':'Warm Lulu:','script':''}],'Only the pinned speaker-label cleanup is permitted.')
    require(qa['silent_raw_cues']==qa['silent_corrected_cues']==0 and qa['signal_threshold_rms']>=.001 and qa['corrected_captions']['exact_script'] is True,'Every actual speech cue must be nonsilent and script-exact.')
    for key,actual,path in [('raw_captions',raw,RAW),('corrected_captions',cues,CAPTIONS)]:
        require(qa[key]['sha256']==PINS[str(path)] and len(qa[key]['energy'])==71,'Unmeasured caption export.')
        for n,(cue,energy) in enumerate(zip(actual,qa[key]['energy']),1):
            require(energy['cue']==n and all(round(energy[k]*1000)==round(cue[k]*1000) and abs(energy[k]-cue[k])<1e-9 for k in ['start','end']) and energy['samples']>0 and energy['rms']>=qa['signal_threshold_rms'] and energy['below_threshold'] is False,'Missing/changed actual cue PCM measurement.')
    source_review=read(S/'expansion/plans/app-dispatch-schedule-create-edit-narration-brief-20261030/root-complete-source-script-review.json')
    require(source_review['source_script_complete_reviewed'] is True and source_review['lesson_sha256']==PINS[str(LESSON)] and source_review['actual_Dispatch_images_personally_viewed']==9 and source_review['human_listening_claim'] is False,'Retained genuine Root source review differs.')
    rows={x['id']:x for x in manifest['screenshots']};observed={}
    require(len(rows)==9 and all(x['app']=='Dispatch' and not x['id'].startswith('013-') for x in rows.values()),'Core archival screenshot cannot become an operational input.')
    for ident,row in rows.items():
        image=safe_source_path(row['file']);dom=safe_source_path(row['dom_file'])
        require(sha(image)==row['sha256'] and sha(dom)==row['dom_sha256'] and _image_dimensions(image)==(1280,720),'Actual operational source bytes/dimensions changed.')
        review=row['capture_review'];require(review['passed'] is True and review['sha256']==row['sha256'] and all(review[k] is True for k in ['application_visible','labels_legible','no_errors']),'Actual bounded source review missing.')
        actual_timestamp(review['reviewed_at'],row['provenance']['captured_at'])
        v=_Validator(S);observed[ident]=v.observations(row,ident);require(not v.issues,'Invalid source observations: '+json.dumps(v.issues))
    require(len(proposal['source_spans'])==13 and len(proposal['cues'])==71 and proposal['unresolved_cross_image_cue_boundaries']==[],'Incomplete actual source/cue map.')
    require(proposal['bounded_recorded_scope']['dispatch_now_success'] is False and proposal['bounded_recorded_scope']['Core013_operational_input'] is False,'Bounded recorded scope changed.')
    entries=[]
    for n,(actual,proposed) in enumerate(zip(cues,proposal['cues']),1):
        require(proposed['raw_cue']==n and all(proposed[k]==actual[k] for k in ['start','end','text']),'Proposal differs from actual unchanged whole cue.')
        require(proposed['capture_id'] in rows and proposed['source_sha256']==rows[proposed['capture_id']]['sha256'],'Cue identifies a different real source.')
        references={x['literal_visible_label']:x['exact_spoken_reference'] for x in proposed['proposed_literal_correspondences']}
        require(all(label in rows[proposed['capture_id']]['visible_labels'] and normalized(phrase) in normalized(actual['text']) for label,phrase in references.items()),'A proposed spoken reference is unseen or absent.')
        entry=dict(actual,cue=n,screenshot_id=proposed['capture_id'],required_labels=list(references),spoken_references=references,instructional=bool(references))
        v=_Validator(S);v.spoken_references(entry,{_normalized(x) for x in references},'proposed actual cue',True);require(not v.issues,'Invalid exact spoken reference.')
        entries.append(entry)
    frozen=read(S/FREEZE/'screen-sequence.untimed.json')['source_spans'];ranges=[(1,7),(8,13),(14,19),(20,25),(26,30),(31,35),(36,37),(38,41),(42,45),(46,49),(50,55),(56,60),(61,71)]
    cursor=0
    for i,(span,original,(first,last)) in enumerate(zip(proposal['source_spans'],frozen,ranges)):
        require(span['raw_cue_first']==first and span['raw_cue_last']==last and span['capture_id']==original['capture_id'] and span['exact_narration']==original['text'],'Frozen source-span membership changed.')
        require(words(' '.join(c['text'] for c in cues[first-1:last]))==words(original['text']),'A whole cue crosses a source speech boundary.')
        begin=0.0 if i==0 else cues[first-1]['start'];end=cues[ranges[i+1][0]-1]['start'] if i+1<len(ranges) else duration
        require(span['proposed_screen_start']['seconds']==begin and span['proposed_screen_end']['seconds']==end and cues[last-1]['end']<=end,'Source hold is not actual whole-cue arithmetic.')
        count=len(words(original['text']));require(span['normalized_token_start']==cursor and span['normalized_token_end']==cursor+count,'Noncontiguous source token range.');cursor+=count
    require(cursor==690,'Source token map loses or adds speech.')
    scenes=[]
    for authored in lesson['scenes']:
        spans=[x for x in proposal['source_spans'] if x['scene_id']==authored['id']]
        caps=[c for c,p in zip(entries,proposal['cues']) if p['scene_id']==authored['id']]
        screens=[{'screenshot_id':p['capture_id'],'start':p['proposed_screen_start']['seconds'],'end':p['proposed_screen_end']['seconds']} for p in spans]
        require(words(' '.join(c['text'] for c in caps))==words(authored['narration']) and any(c['required_labels'] for c in caps),'Actual scene loses speech or has no visible spoken reference.')
        require(all(s['end']>s['start'] and (i==0 or screens[i-1]['end']==s['start']) for i,s in enumerate(screens)),'Source intervals do not cover this scene.')
        require(all(any(s['screenshot_id']==c['screenshot_id'] and s['start']<=c['start'] and s['end']>=c['end'] for s in screens) for c in caps),'Whole actual cue is cut across images.')
        full={'id':authored['id'],'title':authored['title'],'kind':'operational','start':screens[0]['start'],'end':screens[-1]['end'],'visual_required_labels':authored['required_labels'],'screens':screens,'captions':caps}
        require({_normalized(x) for x in full['visual_required_labels']}<=set().union(*(observed[s['screenshot_id']] for s in screens)),'Scene requires unseen primary-app labels.')
        full['proposed_mapping_sha256']=instruction_scene_digest(full,rows);scenes.append(full)
    require(scenes[0]['start']==0 and scenes[-1]['end']==duration and all(a['end']==b['start'] for a,b in zip(scenes,scenes[1:])),'Visual holds do not cover the full measured audio.')
    metrics=read(S/PROPOSAL/'caption-layout-measurements.json')
    require(metrics['summary']=={'cues_measured':71,'all_caption_ink_within_footer':True,'all_titles_fit':True},'Actual cue/title geometry has a gap.')
    return {'lesson':lesson,'manifest':manifest,'rows':rows,'proposal':proposal,'qa':qa,'duration':duration,'scenes':scenes,'cues':cues}


def root_review(data,value,digest):
    record=receipt(value,digest)
    require(record.get('reviewer') in {'Root','Codex /root'},'Require genuine Root complete-map review.')
    require(record.get('lesson_sha256')==PINS[str(LESSON)] and record.get('audio_sha256')==PINS[str(AUDIO)],'Root reviewed a different source or actual audio.')
    require(record.get('correspondence_sha256')==PINS[str(PROPOSAL/'correspondence.proposed.json')] and record.get('compact_sha256')==PINS[str(PROPOSAL/'cue-screen-correspondence.txt')],'Root reviewed a different complete timed map.')
    require(record.get('learner_projection_sha256')==PINS[str(PUBLIC)],'Root reviewed different learner practice/scenario metadata.')
    for key in ['complete_cue_correspondence_reviewed','screen_holds_and_required_controls_reviewed','semantic_reference_items_reviewed','learner_practice_prompts_reviewed','learner_sector_examples_reviewed']:
        require(record.get(key) is True,'Actual complete Root review is missing: '+key)
    require(record.get('cues')==71 and record.get('accepted_spans')==13 and record.get('source_images')==9,'Root accepted an incomplete timed-map scope.')
    require(record.get('human_listening_claim') is False,'Root timed-map review does not replace genuine User hearing.')
    require(isinstance(record.get('review'),str) and len(record['review'])>120,'Retain the genuine Root complete review account.')
    actual_timestamp(record.get('reviewed_at'),data['proposal']['created_at'])
    return record


def user_listening(data, value, digest):
    record = receipt(value, digest)
    require(record.get('reviewer') == 'User' and record.get('complete_natural_narration') is True, 'Actual User complete natural narration review is pending.')
    require(record.get('lesson_sha256') == PINS[str(LESSON)] and record.get('audio_sha256') == PINS[str(AUDIO)], 'User heard different source or audio.')
    evidence = record.get('evidence')
    require(isinstance(evidence, str) and re.search(r'(?i)\b(?:full|complete)\b', evidence) and re.search(r'(?i)\bnatural\b', evidence), 'Retain the actual complete listening question and natural response.')
    actual_timestamp(record.get('reviewed_at'), data['qa']['checked_at'])
    return record


def build(data, parent, parent_file, parent_sha, heard, heard_file, heard_sha):
    from verify_capture_evidence import instruction_scene_digest, _Validator, _normalized
    scenes = []
    for source in data['scenes']:
        full = deepcopy(source)
        full.pop('proposed_mapping_sha256')
        full['instruction_review'] = {
            'passed': True, 'reviewer': parent['reviewer'], 'reviewed_at': parent['reviewed_at'],
            'correspondence_reviewed': True, 'no_unseen_controls': True,
            'mapping_sha256': instruction_scene_digest(full, data['rows']),
            'parent_correspondence_review_file': parent_file, 'parent_correspondence_review_sha256': parent_sha,
            'method': 'Actual Root complete71-cue/13-span/9-Dispatch-source review, including explicit semantic items, retained source pixel/DOM reviews, unchanged actual SRT and full PCM audio QA. No new original-pixel inspection, User hearing, encoded-frame review or browser playback is inferred from this map receipt.'}
        v = _Validator(S)
        v.instruction_review(full, data['rows'], {ident: {_normalized(x) for x in row['visible_labels']} for ident, row in data['rows'].items()}, 'actual reviewed scene', data['lesson']['app'])
        require(not v.issues, 'Actual Root instruction mapping failed: ' + json.dumps(v.issues))
        scenes.append({'id': full['id'], 'start': full['start'], 'end': full['end'], 'screens': full['screens'],
                       'captions': [{k: c[k] for k in ['cue', 'screenshot_id', 'required_labels', 'spoken_references', 'instructional']} for c in full['captions']],
                       'instruction_review': full['instruction_review']})
    manifest_bytes = (S / PROPOSAL / 'captures.source-relative.json').read_bytes()
    caption_bytes = (S / CAPTIONS).read_bytes()
    plan = {'schema_version': 1, 'lesson_id': data['lesson']['id'], 'duration_seconds': data['duration'],
        'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
        'narration': {'file': str(AUDIO), 'sha256': PINS[str(AUDIO)], 'kind': 'approved_natural_narration',
            'approval': {'reviewer': heard['reviewer'], 'reviewed_at': heard['reviewed_at'], 'sha256': PINS[str(AUDIO)],
                'complete_natural_narration': True, 'evidence': heard['evidence'], 'qa_file': str(QA), 'qa_sha256': PINS[str(QA)],
                'listening_review_file': heard_file, 'listening_review_sha256': heard_sha}},
        'captions': {'file': str(FINAL / 'captions.actual.corrected.srt'), 'sha256': sha(S / CAPTIONS), 'kind': 'speech_timed_srt',
            'approval': {'reviewer': 'Codex actual unchanged export and pinned full PCM QA', 'reviewed_at': data['qa']['checked_at'],
                'sha256': sha(S / CAPTIONS), 'audio_sha256': PINS[str(AUDIO)], 'speech_timing_reviewed': True,
                'method': 'All71 corrected whole cues retain actual exported endpoints and exact frozen words; the sole pinned raw-export speaker-label cleanup is separately documented by full actual audio QA. Pinned complete PCM QA measures every cue; no word cut, endpoint movement, caption stretch or estimated timing. Actual Root whole-map and separate genuine User listening receipts are required.'}},
        'capture_manifests': [{'file': str(FINAL / 'captures.reviewed.json'), 'sha256': hashlib.sha256(manifest_bytes).hexdigest()}],
        'screenshot_reviews': {ident: {k: row['capture_review'][k] for k in ['reviewer', 'reviewed_at', 'sha256', 'application_visible', 'labels_legible', 'no_errors']} for ident, row in data['rows'].items()},
        'scenes': scenes, 'parent_correspondence_review': {'file': parent_file, 'sha256': parent_sha},
        'bounded_recorded_scope': data['proposal']['bounded_recorded_scope'], 'publishable': False,
        'limitations': data['proposal']['source_limits'] + ['Actual every-hold/caption encoded-frame inspection and genuine browser beginning/middle/end playback remain required after separate rendering.']}
    return plan, manifest_bytes, caption_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assemble', action='store_true')
    parser.add_argument('--correspondence-review-file')
    parser.add_argument('--correspondence-review-sha256')
    parser.add_argument('--listening-review-file', default=str(HEARING))
    parser.add_argument('--listening-review-sha256', default=PINS[str(HEARING)])
    args = parser.parse_args(argv)
    data = preflight()
    if args.assemble:
        require(all([args.correspondence_review_file, args.correspondence_review_sha256, args.listening_review_file, args.listening_review_sha256]), 'Assembly requires both actual Root whole-map and actual User listening receipt files/hashes.')
    require(bool(args.correspondence_review_file) == bool(args.correspondence_review_sha256), 'Supply both Root review path and exact hash.')
    require(bool(args.listening_review_file) == bool(args.listening_review_sha256), 'Supply both User listening path and exact hash.')
    parent = root_review(data, args.correspondence_review_file, args.correspondence_review_sha256) if args.correspondence_review_file else None
    heard = user_listening(data, args.listening_review_file, args.listening_review_sha256) if args.listening_review_file else None
    if not args.assemble:
        print(json.dumps({'source_preflight': True, 'lesson': data['lesson']['id'], 'scenes': 12, 'holds': 13, 'cues': 71,
            'actual_audio_sha256': PINS[str(AUDIO)], 'decoded_duration_seconds': data['duration'],
            'actual_Root_whole_map_receipt_validated': parent is not None, 'actual_User_listening_receipt_validated': heard is not None,
            'final_inputs_written': False, 'rendered': False, 'canonical_site_or_target_changed': False}, indent=2))
        return
    destination = S / FINAL
    require(not destination.exists() and not destination.is_symlink(), 'New-only final inputs refuse existing outputs; preserve history.')
    plan, manifest, captions = build(data, parent, args.correspondence_review_file, args.correspondence_review_sha256, heard, args.listening_review_file, args.listening_review_sha256)
    assets = {'plan.json': encoded(plan), 'captures.reviewed.json': manifest, 'captions.actual.corrected.srt': captions}
    destination.mkdir(parents=True)
    for name, body in assets.items():
        with (destination / name).open('xb') as stream:
            stream.write(body)
    from render_walkthrough import validate_inputs
    from verify_capture_evidence import instruction_scene_digest
    checked = validate_inputs(S / LESSON, destination / 'plan.json', S)
    for scene in checked['scenes']:
        require(instruction_scene_digest(scene, data['rows']) == scene['instruction_review']['mapping_sha256'], 'Actual renderer expansion changes the reviewed instruction digest.')
    report = {'kind': 'New immutable actual-input package after genuine separate reviews', 'lesson_id': data['lesson']['id'],
        'recipe_sha256': sha(__file__), 'frozen_sha256': PINS[str(LESSON)], 'actual_audio_sha256': PINS[str(AUDIO)],
        'Root_correspondence_receipt_sha256': args.correspondence_review_sha256, 'User_listening_receipt_sha256': args.listening_review_sha256,
        'strict_renderer_inputs_passed': True, 'all_scene_renderer_digest_roundtrips_passed': True,
        'rendered': False, 'canonical_site_or_target_changed': False, 'outputs': [{'file': name, 'sha256': sha(destination / name)} for name in assets]}
    with (destination / 'provenance.json').open('xb') as stream:
        stream.write(encoded(report))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
