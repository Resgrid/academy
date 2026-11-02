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

CONFIG = {'record-numbering': {'id': 'core-record-numbering-settings', 'folder': 'core-record-numbering-settings-source-proposal-20261101-v2', 'lesson_sha256': '9a5271952fd4918d8b06a340588322c70e1c44886d2018060d594f74602fc1f5', 'cue_count': 104, 'spans': [('01', 1, 8, '001-records-settings-lifecycle'), ('02', 9, 16, '006-pattern-tokens-padding-readable'), ('03', 17, 24, '006-pattern-tokens-padding-readable'), ('04', 25, 28, '005-year-start-readable'), ('04', 29, 30, '001-separate-call-number-year-controls'), ('04', 31, 32, '005-year-start-readable'), ('05', 33, 41, '008-prefix-heading-and-table'), ('06', 42, 48, '001-prepared-custom-pattern'), ('07', 49, 54, '002-save-control'), ('08', 55, 59, '003-settings-saved'), ('09', 60, 66, '006-pattern-after-reopen'), ('10', 67, 74, '005-new-pattern-next-numbers'), ('11', 75, 79, '007-original-pattern-restored'), ('12', 80, 87, '008-original-sequence-resumed'), ('13', 88, 95, '010-other-record-number-patterns'), ('14', 96, 104, '008-original-sequence-resumed')], 'references': {3: {'Records Settings': 'Records Settings'}, 9: {'Record numbering': 'Record numbering'}, 10: {'Number pattern': 'Number pattern', '{PREFIX}-{YYYY}-{SEQ}': 'prefix token, a hyphen'}, 11: {'{PREFIX}-{YYYY}-{SEQ}': 'four-digit year token'}, 13: {'{PREFIX}-{YYYY}-{SEQ}': 'record type prefix'}, 14: {'{PREFIX}-{YYYY}-{SEQ}': 'sequence'}, 17: {'Sequence digits': 'Sequence digits', '4': 'four'}, 18: {'4': 'four digits'}, 19: {'0184': 'zero one eight four'}, 20: {'3 to 8 digits': 'three through eight digits'}, 21: {'Sequence digits': 'width'}, 24: {'4': 'four-digit setting'}, 25: {'Numbering year starts': 'Numbering year starts'}, 26: {'January': 'January first', '1': 'first'}, 29: {'Call Numbering': 'call numbering'}, 30: {'Numbering year starts': 'year start'}, 32: {'January': 'January-first value'}, 33: {'Record type prefixes': 'Record type prefixes', 'Record type': 'type', 'Default': 'default', 'Number prefix': 'Number prefix'}, 34: {'Run': 'Run', 'RUN': 'R U N', 'Training': 'Training', 'TRN': 'T R N'}, 35: {'Work': 'Work', 'WRK': 'W R K', 'Meeting': 'Meeting', 'MTG': 'M T G'}, 36: {'Default': 'default'}, 39: {'{PREFIX}': 'prefix token'}, 42: {'Number pattern': 'Number'}, 43: {'Number pattern': 'pattern with underscores'}, 44: {'{PREFIX}_{YYYY}_{SEQ}': 'prefix, four-digit year and sequence tokens'}, 45: {'INC_2026_0153': 'example beside the field'}, 46: {'{PREFIX}_{YYYY}_{SEQ}': 'unsaved form value'}, 49: {'Save': 'Save', 'Cancel': 'Cancel'}, 50: {'Save': 'Save'}, 53: {'Save': 'Save'}, 55: {'Records settings saved.': 'Records settings saved'}, 60: {'{PREFIX}_{YYYY}_{SEQ}': 'underscore-separated pattern'}, 61: {'Number pattern': 'Number pattern', 'INC_2026_0153': 'matching example'}, 63: {'{PREFIX}_{YYYY}_{SEQ}': 'full pattern'}, 67: {'Next numbers for 2026': 'Next numbers for twenty twenty-six'}, 68: {'RUN_2026_0001': 'Run', 'TRN_2026_0001': 'Training previews'}, 71: {'Raise next to': 'Raise next to'}, 73: {'Raise next to': 'raise a counter'}, 74: {'Next number': 'previewed numbers'}, 75: {'{PREFIX}-{YYYY}-{SEQ}': 'hyphen-separated pattern'}, 76: {'Record numbering': 'Record numbering', '{PREFIX}-{YYYY}-{SEQ}': 'prefix, year and sequence arrangement'}, 80: {'TRN-2026-0003': 'Training ending in zero zero zero'}, 81: {'TRN-2026-0003': 'three'}, 82: {'RUN-2026-0001': 'Run ends in zero zero zero one'}, 83: {'TRN-2026-0003': 'existing sequence'}, 86: {'Raise next to': 'Raise next to'}, 88: {'Other record numbers': 'Other record numbers', 'Records requests': 'Records requests', 'Occupancies': 'Occupancies'}, 89: {'Inspections': 'Inspections', 'Permits': 'Permits', 'Investigations': 'Investigations'}, 90: {'Number pattern': 'Number pattern', 'Sequence digits': 'Sequence digits', 'Next number': 'next-number area'}, 91: {'Built-in, e.g.': 'built-in numbers'}, 104: {'Next numbers for 2026': 'next-number preview'}}}}
PINS = {'record-numbering': {'manifest': '05633643d5fd148e8e863f03c325bf1470b3174efffe08f66c7c10a5821185f6', 'audio': '2f06fe976f1a27b1e2a658632873222c7b28ea5e72a2b6d136a4f96ce8d72e14', 'captions': '238290efaf6f9dd43bee35a4f4eab81d313fb5d132eb64f115868041e08d2864', 'qa': '26341c0bcf7b126ff1a6a28f3ef9d5c0fc24d85e6ecaa2b02f40e0f5c2ef18b6', 'additional_observations': 'ce82e44774b523dceaf61c15a64a5a3f245d4e69212c30b6de6fa9dcddd2d88a', 'cross_reference_manifest': '8e6ec31e4548a86791f8182d7275ef34412760f742495a9cd0073563e852f1c0'}}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def prepare(key, write=False):
    from render_walkthrough import load_cues, words, find_font, caption_wrap
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest
    from PIL import Image, ImageDraw, ImageFont

    config = CONFIG[key]
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
    extra = Path('expansion/plans/core-record-numbering-settings-additional-literal-observations-20261101.json')
    cross = Path('captures/expansion/core-numbering-page-reference-20261101/captures.reviewed.json')
    assert sha(S / cross) == pins['cross_reference_manifest']
    for row in read(S / cross)['screenshots']:
        assert row['id'] not in rows
        row['additional_source_manifest'] = {'file': str(cross), 'sha256': sha(S / cross)}
        manifest['screenshots'].append(row)
        rows[row['id']] = row
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
    learner['scenes'][3]['capture_refs'].append('001-separate-call-number-year-controls')
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
