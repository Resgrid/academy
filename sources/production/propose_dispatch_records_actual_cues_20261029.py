"""Prepare source-only Dispatch/Records correspondence from actual speech cues.

Default is read-only. --write-proposals creates two NEW proposal directories.
No final renderer plan, cue split, listening receipt, media or readiness is made.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
sys.path.insert(0, str(ROOT / 'scripts'))
from qa_narration import alignment
from verify_capture_evidence import _image_dimensions

CONFIGS = [
    {'id': 'app-dispatch-map-and-site-reference', 'folder': 'app-dispatch-map-and-site-reference-capture-freeze-20261029',
     'lesson_sha256': 'b7753f1893ecc9881af038a7ac3b01380841583318df9dd46e0b906b7744837e',
     'map': 'ordered27span.accepted.json', 'map_sha256': '95389ab03e80d83cb6475c8bd6e295ae0587bde21f675fa83bf42c49188b9580',
     'captures': 'captures.reviewed.json', 'captures_sha256': '139b424d1e48fe3bb2f72e30eb05e7ffd2e6eb643a0d8a4069387a95be4af94c',
     'audio_sha256': 'a4ba3129ee15b9d62d055a3119e368a078e7111d0a1e52a6cd463ea3101e92db',
     'qa_sha256': '6c899147de08c6c66fba20db6764420083b7f4175afe9d09c7e773038fc13500',
     'corrected_sha256': '4c9c090e88b4bbe90b5006a4c5019cf2e5f72a9d27b6950014dbd06adfbb413d',
     'raw_sha256': '5082c3d8ae12152f5d033f3cc65bf680ca07e01470354e6028a239e88df0f5ce',
     'cue_count': 72, 'span_count': 27, 'sources': 21},
    {'id': 'core-records-training-entry', 'folder': 'core-records-training-entry-capture-freeze-20261029',
     'lesson_sha256': 'e3df33c2315187e211c0e5c83f8ea0468c22cb549230c0cb752d736853ad9bc5',
     'map': 'core-records-training-entry.screen-sequence.json', 'map_sha256': 'c3737fab6be3a420d64b9b0a284f41078325c02881d0a47d927964eb23adf08a',
     'captures': 'core-records-training-entry.captures.reviewed.json', 'captures_sha256': '5b68213bc9d30836bd390af797042554b0f024fa2e40aebc8c93b47ffdc2509f',
     'audio_sha256': 'f7f1235fb74e25a008a7c53d34c6309e67feb31f42cdeab46c314d7860babdc6',
     'qa_sha256': 'ba067586e0de227ba6c95570d3f05ac70a1030b8229941089eaba8007ba4c2fa',
     'corrected_sha256': '2e2fac56b6d78190576e119db643ad3bee5ed04244bb3b6e83e3cde5b66a1894',
     'raw_sha256': '46a9fe66642a0173d687faab96d0be60ae886438f7f41963e59f89ddc146f112',
     'cue_count': 112, 'span_count': 20, 'sources': 16},
]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def load(path, expected):
    assert sha(path) == expected, 'Changed reviewed input: ' + str(path)
    return json.loads(path.read_text())


def map_words(spans, cues, reference):
    """Use exact word offsets to identify boundaries; never interpolate time."""
    assert ' '.join(span['narration_exact'] for span in spans).split() == reference
    assert ' '.join(cue['text'] for cue in cues).split() == reference
    offset = 0
    for index, cue in enumerate(cues, 1):
        cue.update(cue=index, word_start=offset, word_end=offset + len(cue['text'].split()))
        offset = cue['word_end']
    offset, unresolved = 0, []
    for index, span in enumerate(spans, 1):
        length = len(span['narration_exact'].split())
        span.update(span=index, word_start=offset, word_end=offset + length)
        intersects = [cue for cue in cues if cue['word_start'] < span['word_end'] and cue['word_end'] > offset]
        span['actual_cues_intersecting'] = [cue['cue'] for cue in intersects]
        first = intersects[0]
        if offset == first['word_start']:
            span['proposed_start_seconds'] = 0.0 if index == 1 else alignment.seconds(first['start'])
            span['start_basis'] = 'Initial actual audio start' if index == 1 else 'Unchanged actual SRT cue start'
        else:
            words = first['text'].split()
            within = offset - first['word_start']
            span['proposed_start_seconds'] = None
            span['start_basis'] = 'UNRESOLVED: exact within-cue words require a genuine service marker'
            unresolved.append({'before_span': index, 'raw_cue': first['cue'],
                'actual_cue_start_seconds': alignment.seconds(first['start']),
                'actual_cue_end_seconds': alignment.seconds(first['end']),
                'exact_words_before_boundary_in_cue': ' '.join(words[:within]),
                'exact_words_after_boundary_in_cue': ' '.join(words[within:]),
                'resolved_cut_seconds': None, 'genuine_one_second_transcript_required': True})
        offset += length
    return unresolved


def prepare(config):
    name = config['id']
    base = SOURCES / 'expansion/plans' / config['folder']
    audio_base = SOURCES / 'expansion/audio'
    lesson_path = base / (name + '.narrated-source.json')
    lesson = load(lesson_path, config['lesson_sha256'])
    source_map = load(base / config['map'], config['map_sha256'])
    manifest = load(base / config['captures'], config['captures_sha256'])
    qa_path = audio_base / (name + '.actual.qa.json')
    qa = load(qa_path, config['qa_sha256'])
    assert qa['passed'] and not qa['issues'] and not qa['silent_raw_cues'] and not qa['silent_corrected_cues']
    assert qa['corrected_captions']['exact_script'] and not qa['alignment']['text_changes']
    assert qa['lesson']['sha256'] == config['lesson_sha256']
    audio = audio_base / (name + '.m4a')
    raw = audio_base / (name + '-generated-20261029.raw.srt')
    corrected = audio_base / (name + '.actual.corrected.srt')
    for path, key in [(audio, 'audio_sha256'), (raw, 'raw_sha256'), (corrected, 'corrected_sha256')]:
        assert sha(path) == config[key], 'Changed actual speech input.'
    assert qa['audio']['sha256'] == config['audio_sha256']
    assert qa['raw_captions']['sha256'] == config['raw_sha256']
    assert qa['corrected_captions']['sha256'] == config['corrected_sha256']
    captures = {row['id']: row for row in manifest['screenshots']}
    for row in captures.values():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert row['capture_review']['sha256'] == row['sha256']
        assert sha(SOURCES / row['file']) == row['sha256'] and sha(SOURCES / row['dom_file']) == row['dom_sha256']
        assert _image_dimensions(SOURCES / row['file']) == (row['width'], row['height'])
    spans = []
    if name.startswith('app-dispatch-'):
        for row in source_map['untimed_spans']:
            spans.append({'scene_id': row['scene_id'], 'source_id': row['source_id'],
                          'narration_exact': row['exact_spoken_segment'],
                          'required_pixel_labels': row['required_pixel_controls_or_context']})
    else:
        for scene in source_map['scenes']:
            for row in scene['screens']:
                spans.append({'scene_id': scene['scene_id'], 'source_id': row['capture_id'],
                              'narration_exact': row['narration_span'], 'required_pixel_labels': row['required_labels']})
    for span in spans:
        row = captures[span['source_id']]
        assert set(span['required_pixel_labels']) <= set(row['visible_labels']), 'Required literal missing from reviewed source.'
        span.update(source_file=row['file'], source_sha256=row['sha256'])
    cues = alignment.parse_srt(corrected.read_text())
    reference = ' '.join(scene['narration'] for scene in lesson['scenes']).split()
    assert len(cues) == config['cue_count'] and len(spans) == config['span_count']
    assert len({span['source_id'] for span in spans}) == config['sources']
    unresolved = map_words(spans, cues, reference)
    for i, span in enumerate(spans):
        span['proposed_end_seconds'] = spans[i + 1]['proposed_start_seconds'] if i + 1 < len(spans) else qa['audio']['duration_seconds']
        start, end = span['proposed_start_seconds'], span['proposed_end_seconds']
        span['proposed_hold_seconds'] = end - start if start is not None and end is not None else None
    cue_rows = []
    for cue in cues:
        matches = [span for span in spans if span['word_start'] < cue['word_end'] and span['word_end'] > cue['word_start']]
        cue_rows.append({'cue': cue['cue'], 'start': alignment.seconds(cue['start']), 'end': alignment.seconds(cue['end']),
            'text': cue['text'], 'scene_ids': list(dict.fromkeys(span['scene_id'] for span in matches)),
            'source_ids_in_exact_spoken_order': list(dict.fromkeys(span['source_id'] for span in matches)),
            'source_span_ids': [span['span'] for span in matches], 'within_cue_screen_cut_unresolved': len({span['source_id'] for span in matches}) > 1})
    holds = []
    if not unresolved:
        for span in spans:
            if holds and holds[-1]['source_id'] == span['source_id']:
                holds[-1]['end_seconds'] = span['proposed_end_seconds']
                holds[-1]['span_ids'].append(span['span'])
            else:
                holds.append({'source_id': span['source_id'], 'start_seconds': span['proposed_start_seconds'],
                              'end_seconds': span['proposed_end_seconds'], 'span_ids': [span['span']]})
        for hold in holds:
            hold['duration_seconds'] = hold['end_seconds'] - hold['start_seconds']
    proposal = {'kind': 'PROPOSED_SOURCE_ONLY_actual_speech_correspondence', 'lesson_id': name,
        'final_renderer_plan': False, 'audio_technical_qa_passed': True,
        'human_full_listening_approval_consumed': False, 'final_assembly_approved': False,
        'publication_approved': False, 'timing_precision': 'Unchanged actual SRT cue boundaries only; no interpolated word or operation times.',
        'input_pins': config, 'decoded_audio_seconds': qa['audio']['duration_seconds'],
        'scenes': len(lesson['scenes']), 'script_words_whitespace': len(reference),
        'actual_caption_count': len(cues), 'source_images': config['sources'], 'accepted_source_spans': len(spans),
        'source_spans': spans, 'actual_cues': cue_rows, 'unresolved_boundaries': unresolved,
        'whole_cue_continuous_holds_proposed': holds,
        'limits': ['Source maps, raw/corrected captions, audio and frozen narration remain unchanged.',
                   'No listening receipt, final assembly, render, frame review, browser playback, canonical readiness or publication is created.',
                   'Where within-cue boundaries are unresolved, no cut time or complete hold count is invented. Genuine service markers and readable screen holds need later review.',
                   'Whole-cue source correspondence is a proposal; existing source reviews are retained, with no new original-image review or frame-review assertion.']}
    compact = '\n'.join(f'{cue["cue"]:03d} {cue["start"]:.3f}–{cue["end"]:.3f} | ' + ' → '.join(cue['source_ids_in_exact_spoken_order']) + (' | NEED GENUINE WITHIN-CUE MARKER' if cue['within_cue_screen_cut_unresolved'] else '') + '\n' + cue['text'] for cue in cue_rows) + '\n'
    outputs = {'correspondence.proposed.json': encoded(proposal), 'cue-screen-map.compact.txt': compact.encode()}
    return proposal, outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-proposals', action='store_true')
    args = parser.parse_args()
    prepared = [(config, *prepare(config)) for config in CONFIGS]
    destinations = [SOURCES / 'expansion/plans' / (config['id'] + '-take-01-proposed-20261029') for config, _, _ in prepared]
    if args.write_proposals:
        assert all(not path.exists() for path in destinations), 'New-only proposals; preserve prior source/timing history.'
        spec = importlib.util.spec_from_file_location('proposal_privacy', ROOT / 'scripts/audit_public_repo.py')
        privacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(privacy)
        for (_, _, outputs), destination in zip(prepared, destinations):
            assert not [(name, rule) for name, body in outputs.items() for rule in privacy.scan_bytes(body)]
        for (config, proposal, outputs), destination in zip(prepared, destinations):
            outputs['preflight.json'] = encoded({'kind': 'source_only_actual_cue_proposal_preflight',
                'input_pins': config, 'helper_sha256': sha(__file__), 'ordinary_privacy_findings': [],
                'human_listening_approval_consumed': False, 'final_renderer_plan': False,
                'output_hashes': {name: hashlib.sha256(body).hexdigest() for name, body in outputs.items()}})
            destination.mkdir(parents=True)
            for name, body in outputs.items():
                with (destination / name).open('xb') as stream:
                    stream.write(body)
    for (config, proposal, outputs), destination in zip(prepared, destinations):
        print(json.dumps({'lesson': config['id'], 'technical_qa_passed': True,
            'actual_cues': proposal['actual_caption_count'], 'accepted_spans': proposal['accepted_source_spans'],
            'source_images': proposal['source_images'], 'unresolved_boundary_cues': [row['raw_cue'] for row in proposal['unresolved_boundaries']],
            'continuous_whole_cue_holds': len(proposal['whole_cue_continuous_holds_proposed']) if not proposal['unresolved_boundaries'] else None,
            'output': str(destination), 'files_written': args.write_proposals,
            'proposal_sha256': hashlib.sha256(outputs['correspondence.proposed.json']).hexdigest(),
            'compact_sha256': hashlib.sha256(outputs['cue-screen-map.compact.txt']).hexdigest(),
            'final_plan_or_listening_approval_created': False}))


if __name__ == '__main__':
    main()
