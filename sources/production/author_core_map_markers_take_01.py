"""Prepare the frozen marker lesson's untimed, hash-bound assembly correspondence.

Offline preparation only. Reads the separate immutable narrated-source snapshot,
never the canonical lesson that later gains publication flags. No audio is read,
no duration/cue/screen timing is assigned, and no media approval is generated.
Historical source reviews are verified, not repeated by running this recipe.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_capture_evidence import _Validator

NAME = 'core-map-markers'
VOICE = 'expansion/plans/core-map-markers.narrated-source.json'
BASE = 'expansion/plans/core-map-markers-capture-freeze-20261027'
PINS = {
    VOICE: 'ccd153d425239d73199b8d3a2b14ff0e7767fcb95e71cd564a76c9a2cd26c40c',
    BASE + '/freeze.json': 'ccd7110fdce827e6c2af1a51408279e6da69fc542540e76e2ee66c03b64e584e',
    BASE + '/untimed-screen-sequence.json': 'a8f0039107a95799d3c40a112cba15029ae85fe563eb60c45171bad78985b932',
    BASE + '/natural-spoken-ui-references.json': '0157b760a760d148146cbc33db144534c758c98d703de3df502c25bdb76871ce',
    'captures/expansion/core-marker-recovery-20261027/reviewed-map-marker-lesson-subset-20261027.json': 'ae55ee7a679cff3cbef7e6c1ce0f709522808d154c3aa7844b59403744ac27f9',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def retained(root, relative, expected):
    path = (root / relative).resolve()
    need(not Path(relative).is_absolute() and root in path.parents, 'Input must remain inside sources: ' + relative)
    need(path.is_file() and digest(path) == expected, 'Frozen input missing or changed: ' + relative)
    return path


def build(root):
    sources = (root / 'sources').resolve()
    inputs = []
    for relative, expected in PINS.items():
        path = retained(sources, relative, expected)
        inputs.append({'file': relative, 'sha256': expected})
    lesson = json.loads((sources / VOICE).read_text())
    freeze = json.loads((sources / BASE / 'freeze.json').read_text())
    sequence = json.loads((sources / BASE / 'untimed-screen-sequence.json').read_text())
    references = json.loads((sources / BASE / 'natural-spoken-ui-references.json').read_text())
    manifest_name = freeze['capture_manifest']
    manifest = json.loads((sources / manifest_name).read_text())
    need(PINS[VOICE] == freeze['lesson_sha256'] == sequence['lesson_sha256'], 'Narrated source pin disagrees with freeze/sequence.')
    need(PINS[manifest_name] == freeze['capture_manifest_sha256'], 'Capture manifest pin disagrees with freeze.')
    need(lesson['id'] == NAME and lesson['app'] == 'Core', 'Unexpected lesson identity.')
    need(len(lesson['scenes']) == len(sequence['scenes']) == 10, 'Expected all ten frozen scenes.')
    need(len(lesson['sector_examples']) == 6, 'Retain all six frozen sector companions.')
    need(sum(len(scene['narration'].split()) for scene in lesson['scenes']) == 923, 'Frozen narration word count changed.')
    records = {row['id']: row for row in manifest['screenshots']}
    need(len(records) == len(freeze['source_hashes']) == 35, 'All35 original reviewed captures must remain available.')
    validator = _Validator(sources)
    for ident, expected in freeze['source_hashes'].items():
        row = records[ident]
        need(row['sha256'] == expected, 'Capture hash changed: ' + ident)
        retained(sources, row['file'], expected)
        retained(sources, row['dom_file'], row['dom_sha256'])
        validator.asset(row, ident, image=True)
        validator.observations(row, ident)
        review = row.get('capture_review', {})
        need(review.get('passed') is True and review.get('sha256') == expected, 'Historical image review is missing: ' + ident)
        need(row.get('privacy_review', {}).get('passed') is True, 'Historical pixel privacy review is missing: ' + ident)
        inputs.extend([{'file': row['file'], 'sha256': expected}, {'file': row['dom_file'], 'sha256': row['dom_sha256']}])
    need(not validator.issues, 'Capture evidence refused: ' + '; '.join(validator.issues))
    scenes, used, multiple, global_word = [], set(), [], 0
    for authored, ordered in zip(lesson['scenes'], sequence['scenes']):
        sid = authored['id']
        need(sid == ordered['id'], 'Scene order changed.')
        need(' '.join(span['text'] for span in ordered['spans']) == authored['narration'], 'Exact ordered speech changed in scene ' + sid)
        union = {label for ident in authored['capture_evidence']['capture_refs'] for label in records[ident]['visible_labels']}
        need(set(authored['required_labels']) <= union, 'Required visible label missing in scene ' + sid)
        spans, scene_word = [], 0
        for index, original in enumerate(ordered['spans'], 1):
            text = original['text']
            need(bool(text.strip()), 'Empty speech span cannot acquire an invented hold.')
            candidates = []
            for ident in original['capture_refs']:
                row = records[ident]
                used.add(ident)
                candidates.append({'id': ident, 'file': row['file'], 'sha256': row['sha256'], 'visible_labels': row['visible_labels']})
            span_id = f'{NAME}-{sid}-span-{index:02}'
            item = {'id': span_id, 'speech': text, 'first_word_in_scene': scene_word,
                    'first_word_in_lesson': global_word, 'word_count': len(text.split()),
                    'ordered_real_screens': candidates, 'purpose': original['purpose'],
                    'timings_assigned': False}
            if len(candidates) > 1:
                item['screen_cut_requirement'] = 'Choose exact cuts only after inspecting the real speech SRT and genuine one-second TXT anchors; preserve readable holds and the visible named subject. Never divide time equally or interpolate from word counts.'
                multiple.append(span_id)
            spans.append(item)
            scene_word += item['word_count']
            global_word += item['word_count']
        scenes.append({'id': sid, 'title': authored['title'], 'required_labels': authored['required_labels'],
                       'ordered_spans': spans, 'narration_word_count': scene_word})
    need(global_word == 923 and len(used) == 33 and sum(len(scene['ordered_spans']) for scene in scenes) == 38, 'Frozen correspondence counts changed.')
    return {
        'kind': 'offline_untimed_author_recipe', 'lesson_id': NAME,
        'narrated_source': {'file': VOICE, 'sha256': PINS[VOICE]},
        'canonical_lesson_read': False, 'scene_count': 10, 'spoken_words': 923,
        'retained_source_images': 35, 'sequence_source_images': 33, 'span_count': 38,
        'retained_but_not_planned_images': sorted(set(records) - used),
        'timings_assigned': False, 'audio_consumed': False, 'media_created': False,
        'ordered_scene_spans': scenes, 'multi_screen_spans_requiring_real_anchor_review': multiple,
        'natural_spoken_ui_references': references['scene_references'],
        'sector_companions': list(lesson['sector_examples']), 'inputs': inputs,
        'fixture_reports': freeze['fixture_reports'],
        'assembly_context': 'TRAINING ONLY · fictional department · simulated station fixtures',
        'pending_inputs': ['Completed full-length M4A and its exact hash', 'Fresh actual speech-timed SRT',
                           'Genuine one-second transcript TXT export', 'Full-decode, exact frozen-script and every-cue signal QA'],
        'next_steps': [
            'Keep the narrated-source snapshot immutable when the canonical lesson gains readiness/media metadata.',
            'Require the completed audio and matching QA to pass before creating any timed recipe; preserve the failed or partial exports separately if any.',
            'Map genuine speech cues and one-second anchors to these exact38 ordered spans; word offsets locate text, never measure speech time.',
            'Review every multi-screen cut against the named entity/control being spoken and the actual source; avoid short legend or name flashes. Keep all required scene labels covered.',
            'Use the unchanged reviewed_scene_coverage renderer and instruction_scene_digest with a new explicitly reviewed timed take; do not generate a passed review from timing alone.',
            'Review every rendered interval and actual encoded cue frame, then retain three genuine final-master browser playback proofs before publication gating.',
        ],
        'limits': [
            'Running this recipe verifies historical capture identities and reviews; it performs no fresh visual or audio review.',
            'No duration, cue boundary, within-cue cut, audio approval, rendered frame, browser proof or publication approval is assigned.',
            'Both Reserve station-location appends were separate declared simulated fixture setup; the status saves themselves used the ordinary application UI.',
            'Urgent was the actual configured priority despite the filename call-emergency.png. Engine51 remains Released; original three calls were preserved.',
            'All35 raw screenshots/DOM records and all six narrated-source sector companions remain unchanged. No native/provider/GPS result is inferred.',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write-preparation', action='store_true', help='Retain the verified untimed preparation JSON; refuses different existing bytes.')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    recipe = build(root)
    output = root / 'sources/expansion/plans/core-map-markers-timing-preparation-20261027.json'
    if args.write_preparation:
        body = json.dumps(recipe, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
        need(not output.exists() or output.read_text() == body, 'Refusing to overwrite a different retained recipe.')
        output.write_text(body)
    print(json.dumps({'lesson': NAME, 'narrated_source_sha256': PINS[VOICE], 'scene_count': 10,
                      'spoken_words': 923, 'span_count': 38, 'sequence_source_images': 33,
                      'timings_assigned': False, 'canonical_lesson_read': False,
                      'preparation': output.relative_to(root).as_posix() if args.write_preparation else None}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
