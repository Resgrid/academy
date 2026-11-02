"""Propose explicit Dispatch screen-cut choices from genuine one-second TXT.

Default reads only. --write-proposal creates a separate NEW proposal; no frozen
map, speech words, captions, final plan, listening receipt or media is changed.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'app-dispatch-map-and-site-reference'
OLD = Path('expansion/plans') / (NAME + '-take-01-proposed-20261029')
FREEZE = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
TXT = Path('expansion/audio') / (NAME + '-generated-20261030.one-second.txt')
OUT = Path('expansion/plans') / (NAME + '-one-second-resolution-proposed-20261030')
PINS = {
    OLD / 'correspondence.proposed.json': '149a10685589f71acbfadd60e1ab28389d6a999fdd840ef5437486478fb2f0b7',
    FREEZE / (NAME + '.narrated-source.json'): 'b7753f1893ecc9881af038a7ac3b01380841583318df9dd46e0b906b7744837e',
    FREEZE / 'ordered27span.accepted.json': '95389ab03e80d83cb6475c8bd6e295ae0587bde21f675fa83bf42c49188b9580',
    TXT: '036ba0e87ab717b55774a9f962d8c4fe7d1c058f419328bf9fa01d024bf6385a',
}
# These are actual service markers, never interpolated word or operation times.
CHOICES = {4: 36, 5: 42, 7: 52, 18: 146, 21: 176, 22: 180, 23: 184, 24: 193}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def anchors(text):
    pattern = re.compile(r'\[(\d{2}):(\d{2}):(\d{2})\]')
    found = list(pattern.finditer(text))
    assert found and not text[:found[0].start()].strip()
    rows, words = [], []
    for index, marker in enumerate(found):
        seconds = sum(int(n) * factor for n, factor in zip(marker.groups(), [3600, 60, 1]))
        assert not rows or seconds > rows[-1]['seconds']
        end = found[index + 1].start() if index + 1 < len(found) else len(text)
        chunk = text[marker.end():end].split()
        rows.append({'seconds': seconds, 'word_offset': len(words), 'following_word_group': ' '.join(chunk)})
        words.extend(chunk)
    return rows, words


def prepare():
    assert __debug__, 'Use ordinary Python; optimized mode disables retained guards.'
    for path, digest in PINS.items():
        assert sha(S / path) == digest, 'Changed reviewed input: ' + str(path)
    previous = json.loads((S / OLD / 'correspondence.proposed.json').read_text())
    lesson = json.loads((S / FREEZE / (NAME + '.narrated-source.json')).read_text())
    reference = ' '.join(scene['narration'] for scene in lesson['scenes']).split()
    service, words = anchors((S / TXT).read_text())
    assert words == reference and len(words) == 634
    assert len(service) == 248 and service[0]['seconds'] == 0 and service[-1]['seconds'] == 247
    by_second = {row['seconds']: row for row in service}
    spans = deepcopy(previous['source_spans'])
    decisions = []
    for unresolved in previous['unresolved_boundaries']:
        number = unresolved['before_span']
        old_offset = spans[number - 1]['word_start']
        exact = [row for row in service if row['word_offset'] == old_offset and row['following_word_group']]
        chosen = by_second[CHOICES[number]]
        before = max((row for row in service if row['word_offset'] < old_offset), key=lambda row: row['seconds'], default=None)
        after = min((row for row in service if row['word_offset'] > old_offset), key=lambda row: row['seconds'], default=None)
        assert unresolved['actual_cue_start_seconds'] <= chosen['seconds'] <= unresolved['actual_cue_end_seconds']
        delta = chosen['word_offset'] - old_offset
        reassigned = words[min(old_offset, chosen['word_offset']):max(old_offset, chosen['word_offset'])]
        decisions.append({'before_span': number, 'raw_cue': unresolved['raw_cue'],
            'original_exact_words_before_boundary_in_cue': unresolved['exact_words_before_boundary_in_cue'],
            'original_exact_words_after_boundary_in_cue': unresolved['exact_words_after_boundary_in_cue'],
            'original_boundary_status': 'Direct genuine service word marker' if exact else 'Ambiguous inside a genuine one-second word group',
            'original_exact_boundary_service_seconds': exact[0]['seconds'] if exact else None,
            'enclosing_service_group': None if exact else {'start_seconds': before['seconds'], 'next_marker_seconds': after['seconds'], 'actual_group_words': before['following_word_group']},
            'proposed_editorial_alternative': {'service_marker_seconds': chosen['seconds'],
                'following_actual_word_group': chosen['following_word_group'], 'service_word_offset': chosen['word_offset'],
                'word_offset_delta_from_original_map': delta, 'exact_words_reassigned': ' '.join(reassigned),
                'reassignment': 'None' if not delta else ('Next span prefix moves to previous source' if delta > 0 else 'Previous span suffix moves to next source'),
                'requires_parent_source_map_review': True},
            'precision_limit': 'Genuine one-second service formatting, not measured subsecond word onset or UI operation time. No point within a group is interpolated.'})
        spans[number - 1]['word_start'] = chosen['word_offset']
        spans[number - 1]['proposed_start_seconds'] = float(chosen['seconds'])
        spans[number - 1]['start_basis'] = 'PROPOSED editorial alternative at retained genuine one-second TXT marker; parent review pending'
    assert len(decisions) == 8 and sum(row['original_exact_boundary_service_seconds'] is not None for row in decisions) == 1
    for index, span in enumerate(spans):
        end_word = spans[index + 1]['word_start'] if index + 1 < len(spans) else len(words)
        span['word_end'] = end_word
        span['narration_exact'] = ' '.join(words[span['word_start']:end_word])
        span['proposed_end_seconds'] = spans[index + 1]['proposed_start_seconds'] if index + 1 < len(spans) else previous['decoded_audio_seconds']
        span['proposed_hold_seconds'] = span['proposed_end_seconds'] - span['proposed_start_seconds']
        assert span['proposed_hold_seconds'] >= 2.0, 'Do not approve an unreadable flash hold.'
        span.pop('actual_cues_intersecting', None)
        span['raw_cues_overlapping_proposed_time'] = [cue['cue'] for cue in previous['actual_cues'] if cue['start'] < span['proposed_end_seconds'] and cue['end'] > span['proposed_start_seconds']]
    assert ' '.join(span['narration_exact'] for span in spans).split() == reference
    assert [span['source_id'] for span in spans] == [span['source_id'] for span in previous['source_spans']]
    assert [span['required_pixel_labels'] for span in spans] == [span['required_pixel_labels'] for span in previous['source_spans']]
    for scene in lesson['scenes']:
        assert ' '.join(span['narration_exact'] for span in spans if span['scene_id'] == scene['id']).split() == scene['narration'].split()
    proposal = {'kind': 'PROPOSED genuine-one-second Dispatch source-span editorial alternatives',
        'lesson_id': NAME, 'input_pins': {str(path): digest for path, digest in PINS.items()},
        'source_only': True, 'parent_review_pending': True, 'human_listening_approval_consumed': False,
        'frozen_map_changed': False, 'narration_changed': False, 'captions_split_or_changed': False,
        'final_renderer_plan': False, 'publication_approved': False,
        'service_anchor_count': len(service), 'exact_script_words': len(words), 'decisions': decisions,
        'original_exact_boundaries_resolved': 1, 'original_exact_boundaries_still_ambiguous': 7,
        'proposed_source_spans': spans, 'minimum_proposed_hold_seconds': min(span['proposed_hold_seconds'] for span in spans),
        'limits': ['All8 suggested cuts use retained real service markers. Seven choices explicitly reassign short unchanged words between adjacent source holds; they do not resolve the original boundary to an invented exact time.',
                   'No frozen source/correspondence or actual SRT is rewritten. Parent must review these explicit editorial changes before any derived captions or final assembly.',
                   'Source IDs/order, literal required controls and every narrated word remain unchanged. No new original-pixel, frame, listening or playback review is asserted.']}
    compact = '\n\n'.join(f'{span["span"]:02d} {span["scene_id"]} {span["proposed_start_seconds"]:.3f}–{span["proposed_end_seconds"]:.3f} | {span["source_id"]}\n{span["narration_exact"]}\nVisible: ' + ' | '.join(span['required_pixel_labels']) for span in spans) + '\n'
    assets = {'resolution.proposed.json': encoded(proposal), 'ordered27span.editorial-alternative.txt': compact.encode(),
              'service-anchors.exact.json': encoded({'source_file': TXT.as_posix(), 'sha256': PINS[TXT], 'anchors': service, 'words_exact_frozen_script': True})}
    return proposal, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-proposal', action='store_true')
    args = parser.parse_args()
    proposal, assets = prepare()
    if args.write_proposal:
        destination = S / OUT
        assert not destination.exists(), 'New-only proposal; preserve previous map and all source bytes.'
        spec = importlib.util.spec_from_file_location('dispatch_marker_privacy', ROOT / 'scripts/audit_public_repo.py')
        scanner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scanner)
        findings = [(name, rule) for name, body in assets.items() for rule in scanner.scan_bytes(body)]
        assert not findings, findings
        assets['preflight.json'] = encoded({'source_only': True, 'recipe_sha256': sha(__file__),
            'input_pins': proposal['input_pins'], 'ordinary_privacy_findings': [],
            'no_interpolation': True, 'parent_review_pending': True,
            'output_hashes': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}})
        destination.mkdir(parents=True)
        for name, body in assets.items():
            with (destination / name).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_only': True, 'files_written': args.write_proposal,
        'direct_original_boundaries': 1, 'ambiguous_original_boundaries': 7,
        'genuine_editorial_alternatives_for_parent_review': 8,
        'minimum_proposed_hold_seconds': proposal['minimum_proposed_hold_seconds'],
        'proposal_sha256': hashlib.sha256(assets['resolution.proposed.json']).hexdigest(),
        'compact_sha256': hashlib.sha256(assets['ordered27span.editorial-alternative.txt']).hexdigest(),
        'output': str(S / OUT), 'final_plan_or_caption_edits': False}, indent=2))


if __name__ == '__main__':
    main()
