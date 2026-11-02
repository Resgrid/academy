"""Reporting audio-bound v2 correspondence and guarded future final inputs.

Default: verify retained inputs without writes. --write-timing-v2 creates only a
new source-only timing/audit package. --assemble additionally requires a genuine,
URL-free, hash-bound User listening receipt. No render or publication occurs.
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

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-reporting-fundamentals'
OLD = Path('expansion/plans') / (NAME + '-take-01-proposed-20261029')
V2 = Path('expansion/plans') / (NAME + '-take-01-proposed-20261029-v2')
FINAL = Path('expansion/plans') / (NAME + '-take-01-final-inputs-20261029')
HELPER = Path('production/prepare_core_reporting_proposed_correspondence_20261029.py')
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
QA = Path('expansion/audio') / (NAME + '.aligned115.actual.qa.json')
CORRECTED = Path('expansion/audio') / (NAME + '.aligned115.corrected.srt')
LISTENING = Path('expansion/audio') / (NAME + '.listening-review.json')
PINS = {
    HELPER: '620f91bd5e39fcc612d25ecbc9308d8ba96becf17ec2da52d5bfbf89fd357dfd',
    OLD / 'correspondence.proposed.json': 'dbc42bf1b97fe5b112256bf1368b85997a93149c324801cee4614168510987bc',
    OLD / 'captures.held-review.json': '9d823a5338d207ca99e334c48f8d1e5ef3c38b2d72894c4667e5ded98419193c',
    OLD / 'cue-screen-correspondence.txt': '89d2a0e35c59c43c7a3eb81c52466f7e7397d39a0f84c4a7fac681883e09e5bc',
    OLD / 'ordered27span.compact.txt': '9b3342576efe11ff9539655eb988fe5e079546377af471a85b114b49614a8091',
    OLD / 'provenance.json': 'd9ba41d15b8de0fee3bdb76ac8d2b63a52ae88161502eafe70022a1280d52b42',
    OLD / 'parent-proposed-correspondence-review.json': '86dd5917a13d353d89f5a95dc84c11e5976c3367d0cb7b572381060e1d737fa0',
    AUDIO: 'c2b447cf277ece5ab21762932864b0d2197cfc4319140e2cf312027dc7dd86ea',
    QA: 'd701aaa58f7d314f6c0e687bca287fb9c9d8586f1f1fc82314d9238c621771bc',
    CORRECTED: 'b4cc24f04b84d576a1cd0ccfb20c78dfc3acf5f49289c415ca36f27ed6075f67',
}
FROZEN = '9df3ae7d5998b85bf989e744e70aee5f8d93bb1212497def4631aaf661411fd7'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def verify_audio_qa(qa, raw, corrected):
    require(qa.get('passed') is True and qa.get('issues') == [], 'Actual audio QA did not pass.')
    require(qa.get('possible_speech_gaps') == [], 'Unresolved possible speech gaps.')
    require(qa['lesson']['sha256'] == FROZEN, 'Wrong frozen narration identity.')
    audio = qa['audio']
    require(audio['sha256'] == PINS[AUDIO] and audio['full_decode'] == 'passed', 'Wrong or undecoded audio.')
    duration = audio['duration_seconds']
    require(isinstance(duration, (int, float)) and duration > raw[-1]['end'], 'Decoded duration does not close the last speech cue.')
    require(abs(audio['decoded_samples'] / audio['sample_rate'] - duration) < 0.000001, 'Duration is not derived from the decoded PCM.')
    require(qa['alignment']['match_ratio'] == 1.0 and qa['alignment']['text_changes'] == [], 'Narration alignment changed words.')
    require(qa['alignment']['cues'] == 115 and len(raw) == len(corrected) == 115, 'Wrong cue count.')
    require(qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0, 'Silent cue found.')
    require(qa['corrected_captions']['sha256'] == PINS[CORRECTED] and qa['corrected_captions']['exact_script'] is True, 'Wrong corrected caption identity.')
    for key, cues in [('raw_captions', raw), ('corrected_captions', corrected)]:
        energy = qa[key]['energy']
        require(len(energy) == len(cues), 'Missing per-cue PCM measurements.')
        for index, (cue, measured) in enumerate(zip(cues, energy), 1):
            require(measured['cue'] == index and measured['samples'] > 0, 'Missing measured cue samples.')
            require(abs(cue['start'] - measured['start']) < 0.000001 and abs(cue['end'] - measured['end']) < 0.000001, 'Measured PCM boundaries differ.')
            require(measured['below_threshold'] is False and measured['rms'] >= qa['signal_threshold_rms'], 'Unreviewed silent PCM cue.')
    for before, after in zip(raw, corrected):
        require((before['start'], before['end'], before['text'].split()) == (after['start'], after['end'], after['text'].split()), 'Corrected captions changed approved cue boundaries or words.')
    return duration


def load_inputs():
    require(__debug__, 'Optimized Python disables retained helper guards; use ordinary Python.')
    for path, expected in PINS.items():
        require(sha(SOURCES / path) == expected, 'Changed reviewed input: ' + str(path))
    spec = importlib.util.spec_from_file_location('reporting_retained_proposal', SOURCES / HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    rebuilt, manifest = helper.prepare()
    previous = json.loads((SOURCES / OLD / 'correspondence.proposed.json').read_text())
    require(encoded(rebuilt) == encoded(previous), 'Retained proposal no longer reproduces exactly.')
    require(encoded(manifest) == (SOURCES / OLD / 'captures.held-review.json').read_bytes(), 'Retained source manifest changed.')
    parent = json.loads((SOURCES / OLD / 'parent-proposed-correspondence-review.json').read_text())
    require(parent['passed_for_proposed_correspondence'] is True and parent['reviewer'] == 'Codex root', 'Missing actual parent correspondence review.')
    require(parent['source_sha256'] == FROZEN and parent['correspondence_sha256'] == PINS[OLD / 'cue-screen-correspondence.txt'], 'Parent reviewed different source correspondence.')
    require((parent['raw_cues'], parent['screen_holds'], parent['sources']) == (115, 27, 23), 'Parent review scope differs.')
    from render_walkthrough import load_cues
    raw = load_cues(SOURCES / helper.RAW)
    corrected = load_cues(SOURCES / CORRECTED)
    qa = json.loads((SOURCES / QA).read_text())
    require(qa['raw_captions']['sha256'] == helper.PINS[helper.RAW], 'QA used different raw captions.')
    duration = verify_audio_qa(qa, raw, corrected)
    return helper, previous, manifest, qa, duration


def timing_assets(helper, previous, manifest, qa, duration):
    current = deepcopy(previous)
    require(current['source_spans'][-1]['proposed_end_seconds'] is None, 'Historical final hold was not open.')
    current['source_spans'][-1]['proposed_end_seconds'] = duration
    current.update(kind='Reporting actual-audio-bound v2 source correspondence; listening pending',
                   status='Actual full-decode/per-cue QA passed. Last hold closes at decoded duration. Genuine User listening receipt required before final assembly.',
                   decoded_audio_duration_seconds=duration, final_screen_end_seconds=duration,
                   audio_qa_approved=True, human_listening_approved=False, parent_timing_review_pending=False)
    current['parent_review_scope'] = 'Previously accepted unchanged115 cue/image correspondences and27 holds; decoded audio closes only the former open final endpoint. No new parent listening or pixel review is asserted.'
    current['explicit_choices'][-1] = 'Last service cue ends431.969s; actual full PCM decode measures432.1698125s. The final hold closes at decoded media duration, leaving0.2008125s after the last cue. No speech/word boundary is moved or interpolated.'
    current['actual_audio_qa'] = {'file': QA.as_posix(), 'sha256': PINS[QA], 'audio_sha256': PINS[AUDIO], 'checked_at': qa['checked_at']}
    spans = current['source_spans']
    require(all(x['proposed_end_seconds'] - x['proposed_start_seconds'] >= 3.0 for x in spans), 'Unreadable source hold.')
    compact = ('\n\n'.join(f"{i:02} {x['scene_id']} | raw{x['first_raw_cue']:03}–{x['last_raw_cue']:03} | {x['proposed_start_seconds']:.3f}–{x['proposed_end_seconds']:.3f} | {x['capture_id']}\nLabels: " + ' | '.join(x['required_labels']) + '\n' + x['exact_narration_span'] for i, x in enumerate(spans, 1)) + '\n').encode()
    delta = {'kind': 'exact v1 to actual-audio-bound v2 timing delta', 'old_correspondence_sha256': PINS[OLD / 'correspondence.proposed.json'],
             'frozen_source_sha256': FROZEN, 'audio_sha256': PINS[AUDIO], 'actual_QA_sha256': PINS[QA],
             'scenes': 13, 'source_images': 23, 'holds': 27, 'cues': 115,
             'cue_screen_correspondence_sha256_unchanged': PINS[OLD / 'cue-screen-correspondence.txt'],
             'only_screen_endpoint_change': {'span': 27, 'before': None, 'after': duration, 'basis': 'Actual decoded_samples/sample_rate, not last subtitle or estimated speech time.'},
             'other26_screen_spans_identical': current['source_spans'][:-1] == previous['source_spans'][:-1],
             'all115_cue_entries_identical': current['cue_correspondence'] == previous['cue_correspondence'],
             'all115_caption_layout_entries_identical': current['caption_layout'] == previous['caption_layout'],
             'all27_spoken_spans_and_required_labels_unchanged': all(a['exact_narration_span'] == b['exact_narration_span'] and a['required_labels'] == b['required_labels'] for a,b in zip(spans, previous['source_spans'])),
             'caption_splits': 0, 'service_one_second_anchor_cuts': 0, 'timing_interpolation': False,
             'minimum_caption_seconds': min(x['duration_seconds'] for x in current['caption_layout']),
             'maximum_caption_characters_per_second': max(x['characters_per_second'] for x in current['caption_layout']),
             'minimum_hold_seconds': min(x['proposed_end_seconds']-x['proposed_start_seconds'] for x in spans),
             'silent_cues': 0, 'minimum_measured_cue_rms': qa['minimum_corrected_cue_rms'],
             'parent_review_file': (OLD / 'parent-proposed-correspondence-review.json').as_posix(),
             'parent_review_sha256': PINS[OLD / 'parent-proposed-correspondence-review.json'],
             'human_listening_approved': False, 'final_plan_created': False, 'rendered': False, 'canonical_or_site_changed': False}
    schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'title': 'Actual User full Reporting narration listening receipt', 'type': 'object',
              'required': ['reviewer','reviewed_at','lesson_sha256','audio_sha256','complete_natural_narration','evidence'],
              'properties': {'reviewer': {'const':'User'}, 'reviewed_at': {'type':'string','format':'date-time'},
                'lesson_sha256': {'const':FROZEN}, 'audio_sha256': {'const':PINS[AUDIO]},
                'complete_natural_narration': {'const':True}, 'evidence': {'type':'string','minLength':15}, 'question_call_id': {'type':'string'}},
              'description': 'No example approval is supplied. Runtime additionally requires URL-free content, actual complete/natural human response evidence, timezone-aware chronology after the actual QA, and an operator-supplied exact receipt SHA256. Technical signal checks do not establish human listening.'}
    assets = {'correspondence.audio-bound.json': encoded(current), 'captures.held-review.json': encoded(manifest),
              'cue-screen-correspondence.txt': (SOURCES / OLD / 'cue-screen-correspondence.txt').read_bytes(),
              'ordered27span.compact.txt': compact, 'delta-and-audio-audit.json': encoded(delta), 'listening-review.schema.json': encoded(schema)}
    provenance = {'kind':'Reporting v2 actual-audio binding; no assembly or listening approval', 'recipe_sha256':sha(__file__),
                  'input_hashes': {**{str(p):h for p,h in helper.PINS.items()}, **{str(p):h for p,h in PINS.items()}},
                  'historical_proposal_and_all_frozen_raw_sources_unchanged':True, 'audio_opened_for_hash_only_actual_PCM_QA_reused':True,
                  'source_reviews_reused_no_new_pixel_claim':True, 'requires_actual_User_listening_receipt':True,
                  'outputs': {name:hashlib.sha256(body).hexdigest() for name,body in assets.items()}}
    assets['provenance.json'] = encoded(provenance)
    return current, assets


def preflight():
    helper, previous, manifest, qa, duration = load_inputs()
    current, assets = timing_assets(helper, previous, manifest, qa, duration)
    if (SOURCES / V2).exists():
        require({p.name for p in (SOURCES / V2).iterdir()} == set(assets), 'Unknown or missing files in held v2 package.')
        for name, body in assets.items():
            require((SOURCES / V2 / name).read_bytes() == body, 'Held v2 bytes differ: ' + name)
    return helper, current, manifest, qa, assets


def validate_listening_record(record, source_sha, audio_sha, qa_checked_at, now=None):
    require(isinstance(record, dict), 'Listening receipt must be an object.')
    require(not re.search(r'(?i)(?:://|www\.|\blocalhost\b|\b127\.0\.0\.1\b)', json.dumps(record)), 'Listening receipt must be URL-free, including optional fields.')
    require(record.get('reviewer') == 'User', 'Require the actual User listening review, not technical agent QA.')
    require(record.get('complete_natural_narration') is True, 'Complete natural narration is not approved.')
    require(record.get('lesson_sha256') == source_sha and record.get('audio_sha256') == audio_sha, 'Listening receipt source/audio identity differs.')
    evidence = record.get('evidence')
    require(isinstance(evidence, str) and re.search(r'(?i)\b(?:complete|full)\b', evidence) and re.search(r'(?i)\bnatural\b', evidence), 'Retain actual full-listening request and natural/complete response.')
    checked = datetime.fromisoformat(record['reviewed_at'].replace('Z','+00:00'))
    earliest = datetime.fromisoformat(qa_checked_at.replace('Z','+00:00'))
    require(checked.tzinfo is not None and earliest.tzinfo is not None, 'Listening review chronology requires timezone-aware dates.')
    require(earliest <= checked <= (now or datetime.now(timezone.utc)), 'Listening review chronology must follow actual QA and cannot be future-dated.')
    return record


def listening(expected_sha, qa):
    require(isinstance(expected_sha, str) and re.fullmatch('[a-f0-9]{64}', expected_sha), 'Supply the exact real listening receipt SHA256.')
    path = SOURCES / LISTENING
    require(path.is_file(), 'Actual User listening receipt has not arrived; assembly is blocked.')
    require(sha(path) == expected_sha, 'Changed or unreviewed listening receipt.')
    return validate_listening_record(json.loads(path.read_text()), FROZEN, PINS[AUDIO], qa['checked_at'])


def build(expected_sha):
    helper, current, manifest, qa, _ = preflight()
    require((SOURCES / V2).is_dir(), 'Seal/review the new v2 timing package first.')
    heard = listening(expected_sha, qa)
    from render_walkthrough import load_cues
    from verify_capture_evidence import instruction_scene_digest
    lesson = json.loads((SOURCES / helper.BASE / (NAME+'.narrated-source.json')).read_text())
    entries = current['cue_correspondence']; rows = {r['id']:r for r in manifest['screenshots']}
    parsed = load_cues(SOURCES / CORRECTED)
    require(len(parsed) == len(entries) == 115, 'Wrong actual cue count.')
    for a,b in zip(parsed,entries):
        require((a['start'],a['end'],a['text'].split()) == (b['start'],b['end'],b['text'].split()), 'Cue/source correspondence changed.')
    now = datetime.now(timezone.utc).isoformat(); scenes = []
    for authored in lesson['scenes']:
        spans = [x for x in current['source_spans'] if x['scene_id'] == authored['id']]
        cues = [x for x in entries if x['scene_id'] == authored['id']]
        screens = [{'screenshot_id':x['capture_id'],'start':x['proposed_start_seconds'],'end':x['proposed_end_seconds']} for x in spans]
        full = {'id':authored['id'],'title':authored['title'],'kind':'operational','start':screens[0]['start'],'end':screens[-1]['end'],'visual_required_labels':authored['required_labels'],'screens':screens,'captions':cues}
        review = {'passed':True,'reviewer':'Codex retained Reporting source/cue correspondence reviewer','reviewed_at':now,'correspondence_reviewed':True,'no_unseen_controls':True,'mapping_sha256':instruction_scene_digest(full,rows),
                  'method':'Exact retained23 image reviews, all115 unchanged actual service captions and parent full correspondence acceptance reused.27 source holds; final endpoint only comes from complete PCM decode. No new source-pixel/encoded-frame/playback or chart/export/provider result review is claimed.'}
        scenes.append({'id':authored['id'],'start':full['start'],'end':full['end'],'screens':screens,
                       'captions':[{k:x[k] for k in ['cue','screenshot_id','required_labels','spoken_references','instructional']} for x in cues], 'instruction_review':review})
    plan = {'schema_version':1,'lesson_id':NAME,'duration_seconds':qa['audio']['duration_seconds'],'instruction_mapping':'reviewed_scene_coverage','display_context':'TRAINING ONLY · fictional department',
            'narration':{'file':AUDIO.as_posix(),'sha256':PINS[AUDIO],'kind':'approved_natural_narration','approval':{'reviewer':heard['reviewer'],'reviewed_at':heard['reviewed_at'],'sha256':PINS[AUDIO],'complete_natural_narration':True,'evidence':heard['evidence'],'qa_file':QA.as_posix(),'qa_sha256':PINS[QA],'listening_review_file':LISTENING.as_posix(),'listening_review_sha256':expected_sha}},
            'captions':{'file':(FINAL/(NAME+'.aligned115.srt')).as_posix(),'sha256':PINS[CORRECTED],'kind':'speech_timed_srt','approval':{'reviewer':'Codex exact frozen-script/actual-cue/PCM metadata reviewer','reviewed_at':now,'sha256':PINS[CORRECTED],'audio_sha256':PINS[AUDIO],'speech_timing_reviewed':True,'method':'Actual115 service SRT boundaries unchanged; exact frozen words, full decode and per-cue measured PCM QA. No new split, one-second marker cut, word-time interpolation or human listening inferred from signal.'}},
            'capture_manifests':[{'file':(FINAL/'captures.reviewed.json').as_posix(),'sha256':hashlib.sha256(encoded(manifest)).hexdigest()}],
            'screenshot_reviews':{row['id']:{'reviewer':row['capture_review']['reviewer'],'reviewed_at':row['capture_review']['reviewed_at'],'sha256':row['sha256'],'application_visible':True,'labels_legible':True,'no_errors':True} for row in rows.values()},
            'scenes':scenes,'publishable':False,'parent_timing_review':{'file':(OLD/'parent-proposed-correspondence-review.json').as_posix(),'sha256':PINS[OLD/'parent-proposed-correspondence-review.json'],'scope':'Previously accepted unchanged115cue/image mapping; the new decoded final endpoint is explicitly retained in v2 delta.'},
            'actual_audio_timing_audit':{'file':(V2/'delta-and-audio-audit.json').as_posix(),'sha256':sha(SOURCES/V2/'delta-and-audio-audit.json')},
            'limitations':['Different report windows/group filters remain separate historical observations; no current-data totals or duplicate-call inference.','Blank Call Summary charts are not chart-success evidence; only Staffing has a demonstrated chart.','Real retained CSV backs13unit rows/12distinctcalls; no spreadsheet/pending export or PDF success invented.','Blank and incomplete timestamps stay unknown; software staffing is not verified physical presence.','Actual encoded-frame/caption/pixel and beginning/middle/end playback reviews remain required after separate rendering.']}
    return helper, plan, (SOURCES/CORRECTED).read_bytes(), manifest


def write_new_directory(path, assets):
    require(not path.exists(), 'New-only output: preserve every prior package.')
    path.mkdir(parents=True)
    for name, body in assets.items():
        with (path/name).open('xb') as stream:
            stream.write(body)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--write-timing-v2',action='store_true')
    modes.add_argument('--assemble',action='store_true')
    parser.add_argument('--listening-review-sha256')
    args = parser.parse_args(argv)
    helper,current,manifest,qa,assets = preflight()
    if args.assemble:
        require(args.listening_review_sha256, '--assemble requires the real listening receipt hash.')
        helper,plan,captions,manifest = build(args.listening_review_sha256)
        out=SOURCES/FINAL
        output={'plan.json':encoded(plan),'captures.reviewed.json':encoded(manifest),NAME+'.aligned115.srt':captions}
        write_new_directory(out,output)
        from render_walkthrough import validate_inputs
        validated=validate_inputs(SOURCES/helper.BASE/(NAME+'.narrated-source.json'),out/'plan.json',SOURCES)
        provenance={'kind':'Reporting guarded final inputs after actual User listening','recipe_sha256':sha(__file__),'frozen_source_sha256':FROZEN,'listening_review_sha256':args.listening_review_sha256,'actual_QA_sha256':PINS[QA],'outputs':{name:sha(out/name) for name in output},'strict_renderer_inputs_passed':True,'rendered':False,'canonical_or_site_changed':False}
        with (out/'provenance.json').open('xb') as stream:stream.write(encoded(provenance))
        print(json.dumps({'strict_inputs_passed':True,'scenes':len(validated['scenes']),'cues':len(validated['cues']),'duration':validated['duration'],'plan_sha256':sha(out/'plan.json'),'rendered':False}));return
    if args.listening_review_sha256:
        listening(args.listening_review_sha256,qa)
    if args.write_timing_v2:
        write_new_directory(SOURCES/V2,assets)
    print(json.dumps({'source_preflight':True,'timing_v2_written':args.write_timing_v2,'scenes':13,'sources':23,'holds':27,'cues':115,'decoded_duration':qa['audio']['duration_seconds'],'final_hold_closed':True,'human_listening_receipt_present':(SOURCES/LISTENING).is_file(),'actual_User_listening_required':True,'final_inputs_written':False,'rendered':False,'canonical_ready':False}))


if __name__ == '__main__':
    main()
