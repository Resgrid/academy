"""Prepare exact Unit native authoring; assemble only with genuine named reviews.

--write-recipe stores a NEW source-only recipe, never approved audio or media.
--assemble requires independently supplied actual User hearing and Root whole-
map receipts with exact SHA256s. No app, rendering, browser or Git operation.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'app-unit-call-lifecycle-native'
B = Path('expansion/plans/app-unit-call-lifecycle-native-candidate-20261030')
CONTEXT = Path('expansion/plans/app-unit-call-lifecycle-native-context-reviewed-20261030')
PROPOSAL = Path('expansion/plans/app-unit-call-lifecycle-native-take-01-proposed-20261030/actual-cue-source-proposal.json')
RECIPE = Path('expansion/plans/app-unit-call-lifecycle-native-authoring-recipe-20261030/authoring-recipe.json')
FINAL = Path('expansion/plans/app-unit-call-lifecycle-native-take-01-final-inputs-20261030')
SOURCE = B / 'lesson.candidate.json'
AUDIO = Path('expansion/audio') / (NAME + '.m4a')
CAPTIONS = Path('expansion/audio') / (NAME + '.actual.corrected.srt')
QA = Path('expansion/audio') / (NAME + '.actual.qa.json')
ROOT_REVIEW = Path('expansion/plans/app-unit-call-lifecycle-native-root-final-recipe-review-20261030.json')
ROOT_REVIEW_SHA = '2cc3b662b635f1302e584e35ad3c75796e4f1e54fada99c5fab10f8983bff95e'
ROOT_MAP = Path('expansion/plans/app-unit-call-lifecycle-native-root-actual-map-context-review-20261030.json')
ROOT_MAP_SHA = '2e7bb4ac9fd8f0c30cc77334146b66bd07c5061438d7b8701a544b5f5ee6de97'
PINS = {SOURCE: 'a98a596197aa748981d9ed30b65f3a76e2bf64166ffa697e1eb8b134f97d759c',
    AUDIO: 'e95e8fed105ed21c44334898e4b5476767bc29ca5b9152ec478cb2808c37986d',
    CAPTIONS: '6c8880bcca673beac948c4a67d963c727d151aa97fd2b83a1e5b2a492da085ee',
    QA: '77d0fbe0dbcfd93c006008ea4b5159084194381ec8485a15c139de018d46f1e5',
    PROPOSAL: '4f030c27d37358565595d29b6c8224b42690baf31c5cf1f8955c772fed488426',
    CONTEXT / 'captures.reviewed.json': '091d053c08570819f84c5cdffacec5e2c3d269165d003f6619d4b1a6ec9aa532',
    CONTEXT / 'current-validator-report-v2.json': '24b863b4980208cca7936395634f7710017bfca9a960815acca8a8095754885d'}
ALIASES = {'Ambulance 61': ['Ambulance Sixty-one'], '0 of 1 Roles': ['zero of one'],
    'Name*': ['Name'], 'Nature*': ['Nature'], 'Priority*': ['Priority'], 'Type*': ['Type'],
    'Units (8)': ['Units section'], '2 selected': ['two selected'], 'Note (optional):': ['optional note'],
    'Step 1 of 3': ['first of three steps']}


def require(value, message):
    if not value: raise ValueError(message)


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def encoded(d): return (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode()
def norm(v): return ' '.join(v.split()).casefold()


def prepare():
    require(__debug__, 'Use ordinary Python; optimized execution disables retained guards.')
    for p, digest in PINS.items(): require(sha(S / p) == digest, 'Changed exact Unit authoring input: ' + str(p))
    sys.path.insert(0, str(ROOT / 'scripts'))
    from native_capture_public import validate_native_source
    from render_walkthrough import load_cues
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    source, proposal, qa = read(S / SOURCE), read(S / PROPOSAL), read(S / QA)
    manifest = read(S / CONTEXT / 'captures.reviewed.json')
    rows = {r['id']: r for r in manifest['screenshots']}
    require(len(rows) == 23 and len(source['scenes']) == 15, 'Changed complete source scope.')
    for row in rows.values(): validate_native_source(row, S, 'Unit')
    require(qa['passed'] is True and qa['issues'] == qa['possible_speech_gaps'] == [], 'Actual audio QA has an unresolved issue.')
    require(qa['audio']['full_decode'] == 'passed' and qa['audio']['sha256'] == PINS[AUDIO] and qa['lesson']['sha256'] == PINS[SOURCE], 'Wrong exact decoded audio or source.')
    require(qa['alignment']['match_ratio'] == 1 and qa['alignment']['text_changes'] == [] and qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0, 'Actual narration/script/signal QA failed.')
    cues = load_cues(S / CAPTIONS)
    require(len(cues) == len(proposal['actual_cues']) == 88, 'All original88 actual cues are required.')
    annotated = []
    for number, (cue, original) in enumerate(zip(cues, proposal['actual_cues']), 1):
        require((cue['start'], cue['end'], norm(cue['text'])) == (original['start'], original['end'], norm(original['text'])), 'Actual words or SRT endpoints changed.')
        require(len(original['scene_ids']) == len(original['source_ids_in_exact_spoken_order']) == 1 and original['within_cue_screen_cut_unresolved'] is False, 'Unresolved within-cue source boundary.')
        ident = original['source_ids_in_exact_spoken_order'][0]
        require(ident in rows and rows[ident]['sha256'] == original['image_sha256'], 'Wrong actual source image.')
        refs = {}
        for literal in rows[ident]['visible_labels']:
            if re.search(r'(?<!\w)' + re.escape(literal) + r'(?!\w)', cue['text'], re.I): refs[literal] = literal
            if literal not in refs:
                for phrase in ALIASES.get(literal, []):
                    if norm(phrase) in norm(cue['text']):
                        refs[literal] = phrase
                        break
        entry = dict(cue, cue=number, screenshot_id=ident, scene_id=original['scene_ids'][0],
            required_labels=list(refs), spoken_references=refs, instructional=bool(refs))
        v = _Validator(S)
        v.spoken_references(entry, {_normalized(x) for x in refs}, 'native actual cue', True)
        require(not v.issues, 'Invalid actual literal/spoken reference: ' + json.dumps(v.issues))
        annotated.append(entry)
    scenes = []
    for authored in source['scenes']:
        spans = [x for x in proposal['scene_bounded_source_spans'] if x['scene_id'] == authored['id']]
        cc = [x for x in annotated if x['scene_id'] == authored['id']]
        require(spans and cc and any(x['required_labels'] for x in cc), 'Every operational scene needs actual spoken-control coverage.')
        require(' '.join(x['text'] for x in cc).split() == authored['narration'].split(), 'Scene does not contain exact complete narration.')
        screens = [{k: span[k] for k in ['screenshot_id', 'start', 'end']} for span in spans]
        for cue in cc:
            require(any(x['screenshot_id'] == cue['screenshot_id'] and x['start'] <= cue['start'] and x['end'] >= cue['end'] for x in screens), 'Actual cue crosses its intended source.')
        scene = {'id': authored['id'], 'title': authored['title'], 'kind': 'operational',
            'start': screens[0]['start'], 'end': screens[-1]['end'], 'screens': screens, 'captions': cc,
            'visual_required_labels': authored['required_labels']}
        union = {_normalized(label) for x in screens for label in rows[x['screenshot_id']]['visible_labels']}
        require({_normalized(x) for x in authored['required_labels']} <= union, 'Authored scene names an unseen actual native label.')
        scene['proposed_mapping_sha256'] = instruction_scene_digest(scene, rows)
        scenes.append(scene)
    recipe = {'kind': 'Exact native Unit source/actual-cue authoring recipe, awaiting real Root map and User hearing',
        'lesson_id': NAME, 'source_file': SOURCE.as_posix(), 'duration_seconds': qa['audio']['duration_seconds'],
        'scenes': scenes, 'native_capture_manifest': {'file': (CONTEXT / 'captures.reviewed.json').as_posix(), 'sha256': PINS[CONTEXT / 'captures.reviewed.json']},
        'input_pins': {p.as_posix(): d for p, d in PINS.items()}, 'actual_cues': 88,
        'source_images': 23, 'source_spans': 23, 'continuous_holds': 23,
        'native_context_current_validator_passed': True, 'parent_whole_map_review': 'pending',
        'actual_User_full_listening': 'pending', 'rendered_or_publishable': False,
        'limits': ['No inferred word timing, synthetic frame, invented native accessible icon name or omitted narration.',
            'Icon instructions retain actual23-source locations and genuine source-pixel review, without DOM relabeling.',
            'Creation is pre-spinner, response/closeout post-spinner; both exact source identities remain bound.',
            'No staffed crew, live response, GPS lookup, delivery receipt, Available cleanup, offline or hardware claim.']}
    return recipe, manifest, qa


def actual_receipt(name, digest, kind, qa):
    require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), 'Supply exact genuine ' + kind + ' receipt SHA256.')
    p = Path(name)
    require(not p.is_absolute() and not any(x in {'.', '..', 'private', '.git', 'node_modules'} or x.startswith('.env') for x in p.parts), 'Unsafe receipt path.')
    path = S / p
    require(path.resolve().is_relative_to(S.resolve()) and not path.is_symlink(), 'Receipt escaped the public source root.')
    require(path.is_file() and sha(path) == digest, 'Genuine ' + kind + ' receipt absent or changed; final authoring remains blocked.')
    r = read(path)
    require(r.get('lesson_sha256') == PINS[SOURCE] and r.get('audio_sha256') == PINS[AUDIO], 'Review identifies different source or audio.')
    at = datetime.fromisoformat(r.get('reviewed_at', '').replace('Z', '+00:00'))
    require(datetime.fromisoformat(qa['checked_at']) <= at <= datetime.now(timezone.utc), 'Review must follow actual audio QA and cannot be in future.')
    if kind == 'User listening':
        require(r.get('reviewer') == 'User' and r.get('complete_natural_narration') is True and bool(r.get('evidence')), 'Require actual User complete natural narration hearing.')
    else:
        require(r.get('reviewer') in {'Root', 'Codex /root'} and r.get('complete_cue_correspondence_reviewed') is True and r.get('screen_holds_and_required_controls_reviewed') is True, 'Require actual Root full source/cue correspondence review.')
        require(r.get('correspondence_sha256') == PINS[PROPOSAL] and r.get('authoring_recipe_sha256') == sha(S / RECIPE), 'Root review must bind exact actual-cue proposal and annotated recipe.')
        require((r.get('cues'), r.get('accepted_spans'), r.get('continuous_holds'), r.get('source_images')) == (88, 23, 23, 23), 'Incomplete Root map scope.')
    return r, p


def actual_root_preflight(qa):
    # These genuine later receipts supplement the immutable earlier recipe;
    # do not rewrite that recipe after Root bound its exact SHA256.
    require(sha(S / ROOT_REVIEW) == ROOT_REVIEW_SHA and sha(S / ROOT_MAP) == ROOT_MAP_SHA,
            'Genuine Root whole-map/context review changed or is absent.')
    root, path = actual_receipt(ROOT_REVIEW.as_posix(), ROOT_REVIEW_SHA, 'Root map', qa)
    require(root.get('context_and_map_review') == {'file': ROOT_MAP.as_posix(), 'sha256': ROOT_MAP_SHA}, 'Wrong supporting actual Root review.')
    require(root.get('native_context_manifest_sha256') == PINS[CONTEXT / 'captures.reviewed.json'] and root.get('native_context_current_validator_report_sha256') == PINS[CONTEXT / 'current-validator-report-v2.json'], 'Root review identifies changed native packages.')
    require(root.get('all_88_annotation_rows_personally_read') is True and root.get('caption_endpoints_and_text_preserved') is True and root.get('two_native_source_profiles_retained') is True and root.get('no_invented_native_accessible_names') is True, 'Actual Root recipe scope is incomplete.')
    require(root.get('actual_User_hearing_claimed') is False and root.get('rendered_or_browser_review_claimed') is False, 'Source-only Root review cannot replace hearing/render/playback.')
    context = read(S / ROOT_MAP)
    require(context.get('reviewer') == 'Root' and context.get('delegated_context_review_accepted') is True and context.get('actual_cues_personally_read') == 88 and context.get('source_spans_personally_read') == 23, 'Supporting Root map/context scope is incomplete.')
    for ref in context['inputs'].values():
        p = Path(ref['file'])
        require(not p.is_absolute() and '..' not in p.parts and sha(S / p) == ref['sha256'], 'Changed Root-reviewed source/context reference.')
    require(root.get('native_context_review_index_sha256') == sha(S / CONTEXT / 'source-context-review-index.json'), 'Root context index differs.')
    return root, path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--write-recipe', action='store_true')
    p.add_argument('--assemble', action='store_true')
    p.add_argument('--listening-review-file', default='expansion/audio/' + NAME + '.listening-review.json')
    p.add_argument('--listening-review-sha256')
    p.add_argument('--parent-review-file', default=ROOT_REVIEW.as_posix())
    p.add_argument('--parent-review-sha256', default=ROOT_REVIEW_SHA)
    a = p.parse_args()
    require(not (a.write_recipe and a.assemble), 'Create recipe and assemble sequentially after genuine review.')
    recipe, manifest, qa = prepare()
    recipe_body = encoded(recipe)
    if a.write_recipe:
        require(not (S / RECIPE).exists() and not (S / RECIPE).parent.exists(), 'Preserve exact existing source recipe.')
        (S / RECIPE).parent.mkdir(parents=True)
        with (S / RECIPE).open('xb') as f: f.write(recipe_body)
    elif (S / RECIPE).exists(): require((S / RECIPE).read_bytes() == recipe_body, 'Retained authoring recipe changed.')
    require(a.parent_review_file == ROOT_REVIEW.as_posix() and a.parent_review_sha256 == ROOT_REVIEW_SHA,
            'Supply the exact genuine pinned Root final recipe review; alternative reviews require a new version.')
    actual_root_preflight(qa)
    if a.assemble:
        require((S / RECIPE).is_file() and (S / RECIPE).read_bytes() == recipe_body, 'Retain the exact recipe before asking for Root review.')
        require(a.parent_review_file, 'Actual Root map receipt is required.')
        heard, heard_path = actual_receipt(a.listening_review_file, a.listening_review_sha256, 'User listening', qa)
        parent, parent_path = actual_receipt(a.parent_review_file, a.parent_review_sha256, 'Root map', qa)
        now = datetime.now(timezone.utc).isoformat()
        scenes = []
        for original in recipe['scenes']:
            scene = deepcopy(original)
            digest = scene.pop('proposed_mapping_sha256')
            scene['instruction_review'] = {'passed': True, 'reviewer': 'Codex exact-source/cue reviewer; actual Root full-map review',
                'reviewed_at': now, 'correspondence_reviewed': True, 'no_unseen_controls': True, 'mapping_sha256': digest,
                'parent_review_file': parent_path.as_posix(), 'parent_review_sha256': a.parent_review_sha256,
                'method': 'All88 original actual speech cues, actual Root full-map review, and23 independently reviewed native sources/context packages. No encoded-frame, browser or User hearing is inferred from script/source checks.'}
            scenes.append(scene)
        captions_name = NAME + '.aligned88.srt'
        plan = {'schema_version': 1, 'lesson_id': NAME, 'duration_seconds': recipe['duration_seconds'],
            'instruction_mapping': 'reviewed_scene_coverage', 'display_context': 'TRAINING ONLY · fictional department',
            'narration': {'file': AUDIO.as_posix(), 'sha256': PINS[AUDIO], 'kind': 'approved_natural_narration',
                'approval': {'reviewer': 'User', 'reviewed_at': heard['reviewed_at'], 'sha256': PINS[AUDIO],
                    'complete_natural_narration': True, 'evidence': heard['evidence'], 'qa_file': QA.as_posix(), 'qa_sha256': PINS[QA],
                    'listening_review_file': heard_path.as_posix(), 'listening_review_sha256': a.listening_review_sha256}},
            'captions': {'file': (FINAL / captions_name).as_posix(), 'sha256': PINS[CAPTIONS], 'kind': 'speech_timed_srt',
                'approval': {'reviewer': 'Codex actual full-script/cue/PCM metadata reviewer', 'reviewed_at': now,
                    'sha256': PINS[CAPTIONS], 'audio_sha256': PINS[AUDIO], 'speech_timing_reviewed': True}},
            'capture_manifests': [{'file': (FINAL / 'captures.reviewed.json').as_posix(), 'sha256': hashlib.sha256(encoded(manifest)).hexdigest()}],
            'screenshot_reviews': {row['id']: {'reviewer': 'Codex /root/remaining_responder_unit source pixel/context reviewer',
                'reviewed_at': '2026-10-30T21:12:28+00:00', 'sha256': row['sha256'], 'application_visible': True, 'labels_legible': True, 'no_errors': True} for row in manifest['screenshots']},
            'scenes': scenes, 'parent_timing_review': {'file': parent_path.as_posix(), 'sha256': a.parent_review_sha256},
            'source_recipe': {'file': RECIPE.as_posix(), 'sha256': sha(S / RECIPE)}, 'publishable': False,
            'limitations': recipe['limits'] + ['Actual encoded23-frame/88-caption and native frame-binding reviews, genuine beginning/middle/end browser playback, public gate and parent adoption remain required.']}
        require(not (S / FINAL).exists(), 'New-only final-input authoring preserves history.')
        bodies = {'plan.json': encoded(plan), 'captures.reviewed.json': encoded(manifest), captions_name: (S / CAPTIONS).read_bytes()}
        (S / FINAL).mkdir(parents=True)
        for name, body in bodies.items():
            with (S / FINAL / name).open('xb') as f: f.write(body)
        from render_walkthrough import validate_inputs
        validated = validate_inputs(S / SOURCE, S / FINAL / 'plan.json', S)
        provenance = {'kind': 'Actual named-review guarded native Unit final authoring', 'strict_renderer_inputs_passed': True,
            'source_sha256': PINS[SOURCE], 'audio_sha256': PINS[AUDIO], 'actual_User_hearing_sha256': a.listening_review_sha256,
            'actual_Root_map_review_sha256': a.parent_review_sha256, 'files': {n: sha(S / FINAL / n) for n in bodies},
            'actual_cues': len(validated['cues']), 'source_images': len(validated['screenshots']), 'rendered_or_published': False}
        with (S / FINAL / 'provenance.json').open('xb') as f: f.write(encoded(provenance))
    print(json.dumps({'source_recipe_ready': True, 'recipe_written': a.write_recipe, 'recipe_sha256': hashlib.sha256(recipe_body).hexdigest(),
        'final_inputs_written': a.assemble, 'actual_cues': 88, 'source_spans': 23, 'actual_User_hearing_required': True,
        'actual_Root_full_map_review_passed': True, 'actual_Root_full_map_review_sha256': ROOT_REVIEW_SHA,
        'rendered_or_published': False}))


if __name__ == '__main__': main()
