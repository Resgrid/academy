"""Prepare complete actual-cue correspondence; never infer visual or listening approval."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))

PINS = {
    'work-order': {
        'manifest': '8e4f313efa92aa1aa46a636898f1cbaeca1b49454093bd0f6618c689c33f4a38',
        'audio': 'b1e73f1c87cd45e934d307084163e538f4b5496adfdb7f754c43a6d74ad8557b',
        'captions': 'f263402437e3c5caa27971ab2b65a98bb7f9acff1a1312b02b06184a740b6c14',
        'qa': '8da85f6d13cfd416b26d332660d39a13d22e3857a90650b3c58481eb8c4f41d6',
        'additional_observations': 'cfd2e4c726a41f5eb858d39394f5c05135700749c553561b125b1005e5a58f5d',
    },
    'notes-checkin': {
        'manifest': '0daada55656aba5124c58f23e62d6ee26402b5ab26546a72b430f13a6de09355',
        'audio': '5085bc06ed3ca4c16d5dd3916720d0b69fe0337ce51f75aef2bff63775a39ee4',
        'captions': '6f0a0f85a458e793759acc9e9758a9298e17c367ca6affe40c39f1f62e7c6370',
        'qa': '63b725299c7beb46333feb6c9f6c2b8a601ac5e8a2f5db29024868b7acd6e444',
    },
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def prepare(key, write=False):
    spec = importlib.util.spec_from_file_location('operations_literals', S / 'production/prepare_responder_operations_cue_maps_20261101.py')
    literals = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(literals)
    literals.prepare(key, False)
    from render_walkthrough import load_cues, words, find_font, caption_wrap
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest
    from PIL import Image, ImageDraw, ImageFont

    config = literals.CONFIG[key]
    pins = PINS[key]
    name = config['id']
    base = Path('expansion/plans') / config['folder']
    lessonfile = base / 'lesson.candidate.json'
    manifestfile = base / 'captures.reviewed.json'
    audio = Path('expansion/audio') / (name + '.m4a')
    captions = Path('expansion/audio') / (name + '.actual.corrected.srt')
    qafile = Path('expansion/audio') / (name + '.actual.qa.json')
    for file, digest in [(lessonfile, config['lesson_sha256']), (manifestfile, pins['manifest']), (audio, pins['audio']), (captions, pins['captions']), (qafile, pins['qa'])]:
        assert sha(S / file) == digest, str(file)
    lesson = read(S / lessonfile)
    manifest = deepcopy(read(S / manifestfile))
    rows = {row['id']: row for row in manifest['screenshots']}
    extra = base / 'additional-literal-observations-20261101.json'
    if 'additional_observations' in pins:
        assert sha(S / extra) == pins['additional_observations']
        for observation in read(S / extra)['observations']:
            row = rows[observation['capture_id']]
            assert row['sha256'] == observation['source_sha256']
            row['visible_labels'] = list(dict.fromkeys([*row['visible_labels'], *observation['labels']]))
            row['additional_literal_review'] = {'file': str(extra), 'sha256': sha(S / extra)}
    observed = {}
    for capture_id, row in rows.items():
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        validator = _Validator(S)
        observed[capture_id] = validator.observations(row, capture_id)
        assert not validator.issues, validator.issues
    cues = load_cues(S / captions)
    qa = read(S / qafile)
    assert len(cues) == config['cue_count'] and qa['passed'] and not qa['issues'] and qa['silent_corrected_cues'] == 0
    assert qa['audio']['sha256'] == pins['audio'] and qa['lesson']['sha256'] == config['lesson_sha256']
    duration = qa['audio']['duration_seconds']
    holds, entries = [], []
    for index, (scene_id, first, last, capture_id) in enumerate(config['spans']):
        start = 0.0 if index == 0 else cues[first - 1]['start']
        end = cues[config['spans'][index + 1][1] - 1]['start'] if index + 1 < len(config['spans']) else duration
        holds.append({'scene_id': scene_id, 'screenshot_id': capture_id, 'start': start, 'end': end, 'first_cue': first, 'last_cue': last})
        for number in range(first, last + 1):
            cue = cues[number - 1]
            aliases = config['references'].get(number, {})
            assert cue['start'] >= start and cue['end'] <= end
            assert {_normalized(label) for label in aliases} <= observed[capture_id], (number, capture_id)
            entry = dict(cue, cue=number, scene_id=scene_id, screenshot_id=capture_id, required_labels=list(aliases), spoken_references=aliases, instructional=bool(aliases))
            validator = _Validator(S)
            validator.spoken_references(entry, {_normalized(label) for label in aliases}, str(number), True)
            assert not validator.issues, validator.issues
            entries.append(entry)
    assert [entry['cue'] for entry in entries] == list(range(1, len(cues) + 1))
    scenes = []
    for original in lesson['scenes']:
        selected = [hold for hold in holds if hold['scene_id'] == original['id']]
        selected_cues = [{key: value for key, value in entry.items() if key != 'scene_id'} for entry in entries if entry['scene_id'] == original['id']]
        assert words(' '.join(cue['text'] for cue in selected_cues)) == words(original['narration'])
        union = set().union(*(observed[hold['screenshot_id']] for hold in selected))
        assert {_normalized(label) for label in original['required_labels']} <= union
        assert any(cue['required_labels'] for cue in selected_cues)
        scene = {'id': original['id'], 'title': original['title'], 'kind': 'operational', 'start': selected[0]['start'], 'end': selected[-1]['end'], 'visual_required_labels': original['required_labels'], 'screens': [{key: hold[key] for key in ['screenshot_id', 'start', 'end']} for hold in selected], 'captions': selected_cues}
        scene['proposed_mapping_sha256'] = instruction_scene_digest(scene, rows)
        scenes.append(scene)
    learner = deepcopy(lesson)
    learner['scope_limits'] = [limit for limit in learner['scope_limits'] if 'Source candidate only' not in limit]
    assert lesson_content_digest(lesson) == lesson_content_digest(learner)
    font = find_font()
    draw = ImageDraw.Draw(Image.new('RGB', (1920, 1080)))
    titlefont = ImageFont.truetype(str(font), 27)
    captionfont = ImageFont.truetype(str(font), 30)
    geometry = {'method': 'Unchanged renderer font sizes and1920x1080 geometry; numerical measurement only.', 'font_sha256': sha(font), 'titles': [], 'captions': []}
    for scene in scenes:
        width = draw.textbbox((0, 0), 'TRAINING ONLY · fictional department · ' + scene['title'], font=titlefont)[2]
        assert width <= 1856
        geometry['titles'].append({'scene_id': scene['id'], 'width_pixels': width, 'fits': True})
    for number, cue in enumerate(cues, 1):
        lines = caption_wrap(draw, cue['text'], captionfont, 1800)
        width = max(draw.textbbox((0, 0), line, font=captionfont)[2] for line in lines)
        assert width <= 1800 and len(lines) <= 2
        geometry['captions'].append({'cue': number, 'lines': lines, 'maximum_width_pixels': width, 'fits': True})
    proposal = {'created_at': datetime.now(timezone.utc).isoformat(), 'lesson_file': str(lessonfile), 'lesson_sha256': config['lesson_sha256'], 'audio_file': str(audio), 'audio_sha256': pins['audio'], 'captions_file': str(captions), 'captions_sha256': pins['captions'], 'qa_file': str(qafile), 'qa_sha256': pins['qa'], 'duration_seconds': duration, 'scenes': scenes, 'holds': holds, 'cues': entries, 'cue_count': len(cues), 'source_images': len(rows), 'distinct_source_images': len({row['sha256'] for row in rows.values()}), 'holds_count': len(holds), 'learner_content_sha256': lesson_content_digest(learner), 'review_state': 'proposal_only_no_review_or_hearing_approval_inferred'}
    if write:
        destination = S / 'expansion/plans' / (name + '-complete-correspondence-20261101')
        assert not destination.exists()
        destination.mkdir()
        for filename, data in [('captures.source-relative.json', manifest), ('correspondence.proposed.json', proposal), ('lesson.learner-projection.proposed.json', learner), ('caption-layout-measurements.json', geometry)]:
            with (destination / filename).open('x') as stream:
                stream.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        (destination / 'cue-screen-correspondence.txt').write_text('\n\n'.join(f"Cue{entry['cue']:03} · scene{entry['scene_id']} · {entry['start']:.3f}–{entry['end']:.3f} · {entry['screenshot_id']}\n{entry['text']}\nLiteral -> exact speech: {json.dumps(entry['spoken_references'], ensure_ascii=False)}" for entry in entries) + '\n')
    return {'passed': True, 'lesson_id': name, 'cues': len(cues), 'scenes': len(scenes), 'holds': len(holds), 'duration_seconds': duration, 'geometry_fits': True, 'written': write, 'actual_review_and_hearing': 'not inferred'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lesson', choices=PINS)
    parser.add_argument('--prepare', action='store_true')
    arguments = parser.parse_args()
    print(json.dumps(prepare(arguments.lesson, arguments.prepare), indent=2))
