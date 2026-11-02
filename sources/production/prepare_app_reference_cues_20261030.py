"""Derive three reference lessons from accepted real source/speech boundaries.

Default reads only. --write-proposed creates NEW source-only packages and SRTs.
No listening review, final plan, assembly, render, app or publication is made.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
INPUTS = Path('production/app_reference_authoring_inputs_20261030.json')
INPUTS_SHA = 'b7c5a2f1aad8f015c3fa4486f0029591738fe63d3c81a2883cccf7b1e8d22b1a'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def module(name, reference):
    require(sha(S / reference['file']) == reference['sha256'], 'Changed retained helper.')
    spec = importlib.util.spec_from_file_location(name, S / reference['file'])
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def inputs():
    require(__debug__, 'Ordinary Python is required for retained helper guards.')
    require(sha(S / INPUTS) == INPUTS_SHA, 'Changed bound input catalog.')
    config = json.loads((S / INPUTS).read_text())
    for reference in [config['parent'], config['ic_responder_resolution']]:
        require(sha(S / reference['file']) == reference['sha256'], 'Changed Root transition evidence.')
    parent = json.loads((S / config['parent']['file']).read_text())
    require(parent['reviewer'] == 'Root' and parent['human_listening_claim'] is False, 'Source timing is not User listening.')
    require(parent['frozen_files_overwritten'] is False, 'Original frozen maps must stay intact.')
    for path, digest in config['production_code'].items():
        require(sha(ROOT / path) == digest, 'Changed reviewed production gate.')
    return config, module('retained_reference_parser', config['retained_parser_helper']), parent


def word_offsets(cues):
    offset = 0
    for cue in cues:
        cue['word_start'] = offset
        offset += len(cue['text'].split())
        cue['word_end'] = offset
    return offset


def layout(cue):
    duration = cue['end'] - cue['start']
    lines = textwrap.wrap(cue['text'], 48, break_long_words=False, break_on_hyphens=False)
    cps = len(cue['text']) / duration
    return {'duration_seconds': round(duration, 6), 'characters_per_second': round(cps, 6),
            'proposed_lines': lines, 'needs_review': duration < 1 or cps > 22 or len(lines) > 2}


def merge_short_same_screen(captions):
    """Retain exact endpoints/words; never merge across an actual source cut."""
    merged = deepcopy(captions)
    receipts = []
    while any(layout(cue)['needs_review'] for cue in merged):
        index = next(i for i, cue in enumerate(merged) if layout(cue)['needs_review'])
        current = merged[index]
        options = []
        for neighbour in [index + 1, index - 1]:
            if not 0 <= neighbour < len(merged):
                continue
            left, right = (current, merged[neighbour]) if neighbour > index else (merged[neighbour], current)
            if (left['screenshot_id'], left['scene_id'], left['word_end']) != (right['screenshot_id'], right['scene_id'], right['word_start']):
                continue
            combined = dict(left, end=right['end'], text=left['text'] + ' ' + right['text'],
                word_end=right['word_end'], raw_cues=list(dict.fromkeys(left['raw_cues'] + right['raw_cues'])))
            if not layout(combined)['needs_review']:
                options.append((min(index, neighbour), combined, left, right))
        require(options, 'Caption needs new timing/readability review; no same-screen genuine-endpoint merge is safe: ' + repr(current))
        start, combined, left, right = options[0]
        receipts.append({'raw_cues': combined['raw_cues'], 'same_screenshot_id': combined['screenshot_id'],
            'scene_id': combined['scene_id'], 'start': combined['start'], 'end': combined['end'],
            'left_text': left['text'], 'right_text': right['text'], 'merged_text': combined['text'],
            'basis': 'Adjacent exact words on one actual source/scene; retain both genuine endpoints, including any real intervening speech gap. No estimated time or across-screen merge.'})
        merged[start:start + 2] = [combined]
    return merged, receipts


def source_spans(alias, cfg, held, actual, anchors, script, parent):
    roles = cfg['roles']
    if alias == 'dispatch':
        spans = [{'scene_id': row['scene_id'], 'capture_id': row['source_id'],
            'word_start': row['word_start'], 'required_labels': row['required_pixel_labels']}
            for row in held['proposed_source_spans']]
        require([row['proposed_editorial_alternative']['service_marker_seconds'] for row in held['decisions']] == parent['accepted_editorial_decisions'][cfg['name']]['service_marker_cuts_seconds'], 'Dispatch accepted markers changed.')
    else:
        spans = [{'scene_id': row['scene_id'], 'capture_id': row['source_id'],
            'word_start': row['script_word_range_zero_based_exclusive_end'][0],
            'required_labels': row['required_labels_from_frozen_hold']}
            for row in held['source_holds']]
        if alias == 'ic':
            require(parent['accepted_editorial_decisions'][cfg['name']]['service_marker_cuts_seconds'] == [109, 245], 'IC accepted markers changed.')
            changes = {'006-empty-login-form-full-cancel-save': next(x['word_offset'] for x in anchors if x['seconds'] == 109),
                '007-signed-in-shared-device-options-unsaved': actual[40]['word_start'],
                '009-online-empty-sync-queue': actual[61]['word_start'],
                '008-logout-confirmation-before-cancel': next(x['word_offset'] for x in anchors if x['seconds'] == 245)}
            require([actual[40]['start'], actual[61]['start']] == [141.129, 217.06], 'Whole-cue entry/result boundaries changed.')
        else:
            require(parent['accepted_editorial_decisions'][cfg['name']]['service_marker_cuts_seconds'] == [167], 'Responder accepted marker changed.')
            changes = {'015-call-notes-readonly-empty': next(x['word_offset'] for x in anchors if x['seconds'] == 167)}
        for row in spans:
            if row['capture_id'] in changes:
                row['word_start'] = changes[row['capture_id']]
    require(spans[0]['word_start'] == 0, 'Missing initial source.')
    require([x['word_start'] for x in spans] == sorted(x['word_start'] for x in spans), 'Source words reordered.')
    for index, span in enumerate(spans):
        span['span'] = index + 1
        span['word_end'] = spans[index + 1]['word_start'] if index + 1 < len(spans) else len(script)
        require(span['word_end'] > span['word_start'], 'Empty or reversed source span.')
        span['exact_narration'] = ' '.join(script[span['word_start']:span['word_end']])
    return spans


def propose(alias):
    catalog, parser, parent = inputs()
    require(alias in catalog['lessons'], 'Unknown lesson alias.')
    cfg = catalog['lessons'][alias]
    for path, digest in cfg['pins'].items():
        require(sha(S / path) == digest, 'Changed retained source/audio/caption input: ' + path)
    roles = cfg['roles']
    lesson = json.loads((S / roles['lesson']).read_text())
    manifest = json.loads((S / roles['manifest']).read_text())
    qa = json.loads((S / roles['qa']).read_text())
    require(qa['passed'] is True and qa['issues'] == [] and qa['possible_speech_gaps'] == [] and qa['alignment']['text_changes'] == [], 'Original full audio/script QA did not pass.')
    require(qa['silent_raw_cues'] == qa['silent_corrected_cues'] == 0 and qa['lesson']['sha256'] == cfg['expected_source_sha256'] and qa['audio']['sha256'] == cfg['expected_audio_sha256'], 'Wrong original audio/source identity.')
    require(qa['audio']['full_decode'] == 'passed' and abs(qa['audio']['decoded_samples'] / qa['audio']['sample_rate'] - qa['audio']['duration_seconds']) < 1e-6, 'Final hold must use real decoded PCM duration.')
    rows = {row['id']: row for row in manifest['screenshots']}
    require(len(rows) == cfg['images'], 'Source count changed.')
    for row in rows.values():
        require(row['eligible_for_lesson'] and row['capture_review']['passed'] and row['capture_review']['sha256'] == row['sha256'], 'Unreviewed source cannot enter recipe.')
        for field, digest in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            require(sha(S / row[field]) == row[digest], 'Changed actual image/DOM pair.')
    raw, actual = parser.cues(S / roles['raw']), parser.cues(S / roles['corrected'])
    require(len(raw) == len(actual) == cfg['raw_cues'] and raw == actual, 'Original corrected cues changed words or real times.')
    script = ' '.join(scene['narration'] for scene in lesson['scenes']).split()
    require(word_offsets(actual) == len(script) and ' '.join(cue['text'] for cue in actual).split() == script, 'Actual speech words differ from frozen script.')
    service_words, anchors = parser.service_anchors((S / roles['anchors']).read_text())
    require(service_words == script, 'Genuine service transcript differs from frozen script.')
    held = json.loads((S / roles['map']).read_text())
    spans = source_spans(alias, cfg, held, actual, anchors, script, parent)
    for index, span in enumerate(spans):
        row = rows[span['capture_id']]
        require(set(span['required_labels']) <= set(row['visible_labels']), 'Unseen required source literal.')
        span.update(source_file=row['file'], source_sha256=row['sha256'])
        span['start'] = parser.boundary(span['word_start'], actual, anchors, len(script))
        if index == 0:
            span['start'] = {'seconds': 0.0, 'basis': 'Actual audio origin; static opening preroll before first speech'}
        span['end'] = parser.boundary(span['word_end'], actual, anchors, len(script))
        if span['end']['basis'] == 'decoded_audio_end':
            span['end'] = {'seconds': qa['audio']['duration_seconds'], 'basis': 'Actual full PCM decode duration'}
        require(span['start']['seconds'] is not None and span['end']['seconds'] is not None, 'An accepted cut still lacks genuine service evidence.')
        span['hold_seconds'] = span['end']['seconds'] - span['start']['seconds']
        require(span['hold_seconds'] >= 1.0, 'Actual image hold is too short for a useful source review.')
    for scene in lesson['scenes']:
        mapped = [span for span in spans if span['scene_id'] == scene['id']]
        require(' '.join(span['exact_narration'] for span in mapped).split() == scene['narration'].split(), 'Accepted edits crossed a frozen scene or changed words.')
        require(set(scene['required_labels']) <= {label for span in mapped for label in rows[span['capture_id']]['visible_labels']}, 'Frozen scene labels lack actual primary-app pixels.')
    derived, splits = [], []
    for cue in actual:
        cuts = [span['word_start'] for span in spans if cue['word_start'] < span['word_start'] < cue['word_end']]
        caption_only = []
        if alias == 'ic' and cue['cue'] == 48:
            # Original49 exceeds22 characters/second. The real166s marker
            # before department guidance permits a two-line same-image tail
            # merge; this is not an additional UI/source transition.
            anchor = next(item for item in anchors if item['seconds'] == 166)
            require(anchor['actual_service_text'] == 'department guidance', 'Caption-only service group changed.')
            require(cue['word_start'] < anchor['word_offset'] < cue['word_end'], 'Caption marker left original48.')
            caption_only = [anchor['word_offset']]
            cuts = sorted(set(cuts + caption_only))
        points = [cue['word_start']] + cuts + [cue['word_end']]
        for begin, end in zip(points, points[1:]):
            source = next(span for span in spans if span['word_start'] <= begin < span['word_end'])
            start_time = cue['start'] if begin == cue['word_start'] else parser.boundary(begin, actual, anchors, len(script))['seconds']
            end_time = cue['end'] if end == cue['word_end'] else parser.boundary(end, actual, anchors, len(script))['seconds']
            derived.append({'start': start_time, 'end': end_time,
                'text': ' '.join(script[begin:end]), 'raw_cues': [cue['cue']], 'word_start': begin, 'word_end': end,
                'scene_id': source['scene_id'], 'screenshot_id': source['capture_id'], 'source_sha256': source['source_sha256']})
        splits += [{'raw_cue': cue['cue'], 'word_offset': cut,
            'purpose': 'caption_readability_only_same_image' if cut in caption_only else 'Root_accepted_source_transition',
            **parser.boundary(cut, actual, anchors, len(script))} for cut in cuts]
    derived, merges = merge_short_same_screen(derived)
    caption_layout = []
    for index, cue in enumerate(derived, 1):
        cue['cue'] = index
        caption_layout.append({'cue': index, **layout(cue)})
    require(' '.join(cue['text'] for cue in derived).split() == script, 'Derived captions changed/omitted speech.')
    require(not any(item['needs_review'] for item in caption_layout), 'Caption layout still needs review.')
    proposal = {'kind': 'Root-cut-accepted source-only actual reference cue correspondence',
        'lesson_id': cfg['name'], 'frozen_source_sha256': cfg['expected_source_sha256'],
        'audio_sha256': cfg['expected_audio_sha256'], 'decoded_duration_seconds': qa['audio']['duration_seconds'],
        'scenes': len(lesson['scenes']), 'spoken_words': len(script), 'source_images': len(rows),
        'raw_cues': len(raw), 'derived_cues': len(derived), 'source_spans': spans,
        'cue_correspondence': derived, 'caption_layout': caption_layout, 'genuine_service_cuts': splits,
        'adjacent_same_image_caption_merges': merges, 'root_transition_receipt': catalog['parent'],
        'human_listening_approved': False, 'final_renderer_plan_created': False,
        'limits': ['Original frozen image/DOM reviews, scripts and raw/corrected service captions stay unchanged.',
            'Only Root-accepted whole-second source cuts and whole-cue entry frames are used. Integer service formatting is not measured phoneme/UI-operation timing.',
            'Tiny caption pieces merge only on the same actual screenshot and scene, retaining real endpoints and exact words. Merges are explicit; no across-source merge or interpolation.',
            'Full derived-cue PCM QA, actual User listening, final input authoring, encoded-frame/caption review and real browser playback are distinct later checks.']}
    compact = '\n'.join(f'{cue["cue"]:03d} | {cue["start"]:.3f}–{cue["end"]:.3f} | {cue["screenshot_id"]} | {cue["text"]}' for cue in derived) + '\n'
    screens = '\n\n'.join(f'{span["span"]:02d} {span["scene_id"]} | {span["start"]["seconds"]:.3f}–{span["end"]["seconds"]:.3f} | {span["capture_id"]}\n{span["exact_narration"]}\nVisible: ' + ' | '.join(span['required_labels']) for span in spans) + '\n'
    assets = {'correspondence.proposed.json': encoded(proposal), 'captions.derived.srt': parser.srt(derived),
        'cue-screen.compact.txt': compact.encode(), 'ordered-screens.compact.txt': screens.encode(),
        'caption-derivation.json': encoded({'raw_originals_unchanged': True, 'root_transition_receipt': catalog['parent'],
            'genuine_service_cuts': splits, 'same_image_caption_merges': merges, 'text_changes': False,
            'interpolation': False, 'derived_cues': len(derived), 'actual_User_listening_inferred': False}),
        'input-pins.json': encoded({'catalog': {'file': INPUTS.as_posix(), 'sha256': INPUTS_SHA}, 'inputs': cfg['pins'], 'parent': catalog['parent']})}
    return cfg, proposal, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lesson', choices=['dispatch', 'ic', 'responder', 'all'], default='all')
    parser.add_argument('--write-proposed', action='store_true')
    args = parser.parse_args()
    aliases = ['dispatch', 'ic', 'responder'] if args.lesson == 'all' else [args.lesson]
    prepared = [propose(alias) for alias in aliases]
    if args.write_proposed:
        require(all(not (S / cfg['out']).exists() for cfg, _, _ in prepared), 'New-only packages; preserve all prior proposals.')
        for cfg, _, assets in prepared:
            destination = S / cfg['out']
            destination.mkdir(parents=True)
            for name, body in assets.items():
                with (destination / name).open('xb') as stream:
                    stream.write(body)
    print(json.dumps([{'lesson': proposal['lesson_id'], 'raw_cues': proposal['raw_cues'],
        'derived_cues': proposal['derived_cues'], 'holds': len(proposal['source_spans']),
        'genuine_splits': len(proposal['genuine_service_cuts']), 'same_image_merges': len(proposal['adjacent_same_image_caption_merges']),
        'caption_layout_flags': sum(item['needs_review'] for item in proposal['caption_layout']),
        'proposal_sha256': hashlib.sha256(assets['correspondence.proposed.json']).hexdigest(),
        'output': str(S / cfg['out']), 'written': args.write_proposed, 'final_plan_or_listening_created': False}
        for cfg, proposal, assets in prepared], indent=2))


if __name__ == '__main__':
    main()
