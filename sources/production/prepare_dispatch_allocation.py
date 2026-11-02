"""Check the frozen Dispatch allocation sources before genuine audio timing.

This offline preparation never assigns durations, renders media, approves image
contents or marks a lesson ready. The existing source review is retained as
history. Exact exported speech cues and genuine transcript anchors are required
before authoring a separate timed take recipe.

Default: read-only source checks and a compact JSON result on stdout.
Optional --report / --blueprint paths are relative to the staged repository;
existing different outputs are preserved rather than overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = 'app-dispatch-allocation'
SOURCE_SHA256 = 'a9f03e25388af4aa7387685368ba5db686239416a9daf4836165cbf62244b2f7'
FREEZE_SHA256 = '5404213c949d28750d653a37ae4342de6c3fd64020be36e73e7f060f381c0323'
SEQUENCE_SHA256 = 'eed82cb9263b6bdaae8d460b684c197fbe16c57b19426f121641d8979d1fef15'
REFERENCES_SHA256 = 'cc91cd1697582a872a88553265968bfa7f9cdce2bf4ca6a1063e1e73a4d53ce3'
MANIFEST_SHA256 = 'd189f942107c099978504eed17e12960761b27275c3847b04a05fa0cba1cf692'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_file(root, relative):
    path = root / relative
    require(not Path(relative).is_absolute() and '..' not in Path(relative).parts,
            'Use a relative path inside the staged repository.')
    require(root.resolve() in path.resolve().parents and not path.is_symlink(),
            'Source must remain inside the staged repository without symlinks.')
    require(path.is_file(), 'Required retained source is missing: ' + relative)
    return path


def prepare(root):
    root = root.resolve()
    sources = root / 'sources'
    base = 'sources/expansion/plans/app-dispatch-allocation-capture-freeze-20261027/'
    lesson_path = relative_file(root, f'sources/expansion/lessons/{NAME}.json')
    freeze_path = relative_file(root, base + 'freeze.json')
    sequence_path = relative_file(root, base + 'untimed-screen-sequence.json')
    refs_path = relative_file(root, base + 'natural-spoken-ui-references.json')
    inputs = {lesson_path: SOURCE_SHA256, freeze_path: FREEZE_SHA256,
              sequence_path: SEQUENCE_SHA256, refs_path: REFERENCES_SHA256}
    for path, expected in inputs.items():
        require(digest(path) == expected, 'Frozen input changed: ' + str(path.relative_to(root)))
    lesson = json.loads(lesson_path.read_text())
    freeze = json.loads(freeze_path.read_text())
    sequence = json.loads(sequence_path.read_text())
    refs = json.loads(refs_path.read_text())
    require(lesson['id'] == NAME and lesson.get('export_ready') is not True,
            'Preparation expects the unchanged, unpublished frozen candidate.')
    require(all(d['lesson_sha256'] == SOURCE_SHA256 for d in [freeze, sequence, refs]),
            'Source bindings disagree.')
    manifest_path = relative_file(root, 'sources/' + freeze['capture_manifest'])
    require(digest(manifest_path) == MANIFEST_SHA256 == freeze['capture_manifest_sha256']
            == sequence['capture_manifest_sha256'], 'Capture manifest changed.')
    inputs[manifest_path] = MANIFEST_SHA256
    manifest = json.loads(manifest_path.read_text())
    records = {item['id']: item for item in manifest['screenshots']}
    require(len(records) == len(manifest['screenshots']), 'Duplicate capture IDs.')
    selected = freeze['source_hashes']
    require(len(selected) == 22, 'Expected 22 frozen source images.')
    for ident, expected in selected.items():
        shot = records[ident]
        image_path = relative_file(sources, shot['file'])
        require(digest(image_path) == expected == shot['sha256'],
                'Frozen screenshot changed: ' + ident)
        require(shot.get('eligible_for_lesson') is True and
                shot.get('review_status') == 'visually_reviewed' and
                shot.get('capture_review', {}).get('passed') is True,
                'Retained source review is missing: ' + ident)
        inputs[image_path] = expected
    require(len(lesson['scenes']) == len(sequence['scenes']) == 8,
            'Expected eight frozen scenes.')
    scenes, used, word_total, span_total = [], set(), 0, 0
    for authored, ordered in zip(lesson['scenes'], sequence['scenes']):
        require(authored['id'] == ordered['id'], 'Scene order differs.')
        spans, offset = [], 0
        for span in ordered['ordered_spans']:
            ident = span['screenshot_id']
            require(ident in selected and span['sha256'] == selected[ident],
                    'Span references an unbound screenshot: ' + ident)
            require(span['first_word'] == offset and
                    span['word_count'] == len(span['speech'].split()),
                    'Frozen word offsets differ: ' + span['id'])
            require(set(span['visible_labels']) <= set(records[ident]['visible_labels']),
                    'Span labels differ from the reviewed capture: ' + span['id'])
            spans.append({key: span[key] for key in
                          ['id', 'speech', 'first_word', 'word_count', 'screenshot_id', 'sha256']})
            offset += span['word_count']
            used.add(ident)
        require(' '.join(x['speech'] for x in spans).split() == authored['narration'].split(),
                'Frozen narration/span text differs: ' + authored['id'])
        observed = {label for span in ordered['ordered_spans'] for label in span['visible_labels']}
        require(set(authored['required_labels']) <= observed,
                'A named scene control lacks a source observation: ' + authored['id'])
        scenes.append({'id': authored['id'], 'title': authored['title'],
                       'required_labels': authored['required_labels'], 'ordered_spans': spans})
        word_total += offset
        span_total += len(spans)
    require(word_total == 812 and span_total == 29, 'Frozen word/span count differs.')
    used_images = len(used)
    require(used_images == 21 and 'dispatch-24-own-pinned-preview-after-reload' not in used,
            'The reviewed untimed sequence changed its selected images.')
    blueprint = {
        'kind': 'offline_untimed_recipe_preparation', 'lesson_id': NAME,
        'lesson_sha256': SOURCE_SHA256, 'scene_count': 8, 'spoken_words': word_total,
        'retained_source_images': 22, 'sequence_source_images': used_images,
        'retained_but_not_planned_images': sorted(set(selected) - used),
        'span_count': span_total, 'timings_assigned': False,
        'ordered_scene_spans': scenes, 'natural_spoken_ui_references': refs['scene_references'],
        'inputs': [{'file': path.relative_to(root).as_posix(), 'sha256': expected}
                   for path, expected in inputs.items()],
        'next_steps': [
            'Receive approved complete audio, full-decode/exact-script/per-cue signal QA, corrected real SRT and the genuine one-second transcript export.',
            'Independently inspect the selected original source images. Preserve the frozen words, control observations and source hashes.',
            'Map actual speech cues to the exact ordered spans. Any cut within a cue needs a genuine transcript anchor; no word-count interpolation.',
            'Review practical readability, including all newly split short cues, before retaining the separate timed take recipe.',
            'Run the unchanged strict render check, render a new unpublished take, and review every screen interval and actual encoded cue frame.',
            'Merge three genuine final-master native playback proofs, run the full evidence and publication preflight, and only then consider readiness.'
        ],
        'limits': [
            'Existing source-review metadata is verified for identity, not treated as a new visual inspection by this preparation script.',
            'No audio duration, cue timing, rendered media, operational outcome, browser playback or publication approval is created.',
            'The freeze retains 22 images; the existing ordered 29 spans use 21. The separate created-console image remains retained without filler footage.',
            'No application settings, source freeze, canonical lesson, import, MFA, provider or runtime state is changed.'
        ]
    }
    report = {key: blueprint[key] for key in ['kind', 'lesson_id', 'lesson_sha256',
              'scene_count', 'spoken_words', 'retained_source_images', 'sequence_source_images',
              'retained_but_not_planned_images', 'span_count', 'timings_assigned']}
    report.update(source_integrity_passed=True, image_review_performed=False,
                  publication_ready=False, frozen_inputs_unchanged=True)
    return report, blueprint


def retain(root, relative, value):
    target = root / relative
    require(not Path(relative).is_absolute() and '..' not in Path(relative).parts and
            root.resolve() in target.resolve().parents and not target.is_symlink(),
            'Output must remain inside the staged repository.')
    body = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    require(not target.exists() or target.read_text() == body,
            'Different retained output already exists; use a new versioned path.')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--report', help='Optional new repository-relative JSON report.')
    parser.add_argument('--blueprint', help='Optional new repository-relative untimed preparation JSON.')
    args = parser.parse_args()
    root = args.root.resolve()
    report, blueprint = prepare(root)
    if args.report:
        retain(root, args.report, report)
    if args.blueprint:
        retain(root, args.blueprint, blueprint)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
