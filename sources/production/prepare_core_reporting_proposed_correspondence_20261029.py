"""Prepare Reporting's source-only timing proposal from actual service cues.

Default read-only. --write-proposed creates a NEW proposal only. No media is
opened or decoded: private export, audio QA and complete human listening are
still pending. No final renderer plan, approval, lesson or site is written.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
NAME = 'core-reporting-fundamentals'
BASE = Path('expansion/plans') / (NAME + '-capture-freeze-20261029')
ACCEPTED = Path('expansion/plans') / (NAME + '-script-acceptance-20261029')
RAW = Path('expansion/audio') / (NAME + '-generated-20261029.raw.srt')
TEXT = Path('expansion/audio') / (NAME + '-generated-20261029.raw.txt')
ANCHORS = Path('expansion/audio') / (NAME + '-generated-20261029.one-second.txt')
OUT = S / 'expansion/plans' / (NAME + '-take-01-proposed-20261029')
PINS = {
    BASE / (NAME + '.narrated-source.json'): '9df3ae7d5998b85bf989e744e70aee5f8d93bb1212497def4631aaf661411fd7',
    BASE / (NAME + '.captures.reviewed.json'): '9d823a5338d207ca99e334c48f8d1e5ef3c38b2d72894c4667e5ded98419193c',
    BASE / (NAME + '.screen-sequence.json'): '250d5d801da0b2d8a2e2928b04b6edcfc17fa635428623d76747bad165e0d60a',
    BASE / 'source-hashes.json': 'e2997ebec03d282ee3744ac7944b076fd0d27be8ce4899f7e5daaef0609ec406',
    BASE / 'narration.txt': '3d129124f4b22379aee8f6f92148e0e6f5a03a119a7336fbf9a12883b65cd1af',
    ACCEPTED / 'compact-correspondence.json': '8fe8bb08d4cf6c54280ce1630e22620e944a2c93d7706cff4f7ffd93bfbdc510',
    ACCEPTED / 'compact-map-acceptance.json': '9fd3df594457e230e6e7918daaf629f5dacf331c7634f7c64ed617de119417c6',
    ACCEPTED / 'accepted-script-review.json': 'a66125a911d94ac1533c30a347670f64c74f1664134591f62dac87fb56b86e65',
    RAW: '55acb26c204dd92cc63a5c2b85ed143303732656bea6fa592e1c8cda8478d710',
    TEXT: '83ffe6b3b7f3737f76b3dc42b996c1f5ea7782069cf4bb7d05b4d76b589bf1eb',
    ANCHORS: '5b7cf7b54a7a5e521640f401643cf0e616c47f18125e97e3030857fe6d6341a0',
}
# Literal reviewed UI text -> natural spoken reference in the indicated cue.
# These are proposed editorial correspondences, never additional pixel labels.
REFS = {
    3: {'Reporting': 'Reporting catalog'},
    4: {'Staffing Report': 'Staffing Report', 'View Report': 'View Report'},
    7: {'Truck 81': 'Truck 81', 'Available': 'Available', 'Unavailable': 'Unavailable', 'OnShift': 'On Shift'},
    10: {'Name': 'Name', 'Group': 'Group', 'Roles': 'Roles', 'Staffing': 'Staffing'},
    11: {'Staffing Timestamp': 'Staffing Timestamp'},
    12: {'Next Change': 'Next Change', 'Next Staffing': 'Next Staffing'},
    14: {'Wallace Boden': 'Wallace Boden'},
    15: {'Matthew Casey': 'Matthew Casey', 'Truck 81': 'Truck 81', 'Officer, TRAINING ONLY - Community response navigator': 'Officer'},
    16: {'Officer, TRAINING ONLY - Community response navigator': 'Community Response Navigator', 'On Shift': 'On Shift'},
    19: {'Call Summary Report': 'Call Summary Report', 'Report Start Time': 'Report Start Time'},
    20: {'Group': 'Group', 'Run Report': 'Run Report'},
    23: {'All Groups': 'All Groups'},
    28: {'Total Calls': 'calls', 'Open': 'open'},
    29: {'Unit Responses': 'responses', 'Personnel Responses': 'personnel responses'},
    33: {'Investigation': 'Investigation', 'Structure Fire': 'Structure Fire', 'Rescue': 'Rescue', 'Medical': 'Medical'},
    34: {'Call States': 'Call States', 'Closed': 'Closed', 'Active': 'Active'},
    37: {'Calls by Group': 'Calls by Group'},
    38: {'Each call counts once': 'Each call counts once'},
    43: {'Firehouse 51': 'Firehouse 51', 'Command': 'Command'},
    46: {'Calls': 'Calls'},
    47: {'Number': 'Number', 'Name': 'Name', 'Type': 'Type', 'Group': 'Group', 'Logged On': 'Logged On', 'Closed On': 'Closed On'},
    48: {'Open': 'Open'},
    49: {'OnScene Time': 'OnScene Time', 'N/A': 'N/A'},
    50: {'TRAINING ONLY - Native Unit response and deselection': 'native Unit response and deselection exercise'},
    51: {'FD51-2026-0008': 'zero zero zero eight', 'Open': 'Open'},
    52: {'N/A': 'N/A'},
    54: {'Call Unit Times': 'Call Unit Times'},
    56: {'Report Start Time': 'start', 'Report End Time': 'end times', 'Run Report': 'Run Report'},
    61: {'Dispatched': 'Dispatched', 'En Route': 'En Route', 'On Scene': 'On Scene', 'Staging': 'Staging'},
    62: {'Cleared': 'Cleared', 'Linked By': 'Linked By'},
    63: {'Dispatch only': 'Dispatch only'},
    65: {'Unit status': 'Unit status'},
    68: {'No unit was dispatched to this call or reported a status on it.': 'no unit dispatch or status data'},
    69: {'Ambulance 61': 'Ambulance 61', 'Dispatched': 'dispatch', 'En Route': 'en-route'},
    72: {'Download CSV': 'Download CSV'},
    73: {'Linked By': 'Linked By'},
    77: {'Dispatch only': 'DispatchOnly', 'Unit status': 'Explicit'},
    78: {'Dispatch only': 'Dispatch only', 'Unit status': 'Unit status'},
    83: {'Command': 'Command', 'Group': 'Group', 'Run Report': 'Run Report'},
    84: {'Group: Command (including the groups beneath it)': 'Command, including the groups beneath it'},
    85: {'Total Calls': 'calls', 'Open': 'open'},
    86: {'Calls': 'detail table', 'Command': 'Command'},
    89: {'Yearly Statistics': 'Yearly Statistics'},
    90: {'2025*': 'asterisk', 'Partial period: the report range covers only part of it.': 'partial period'},
    93: {'Quarterly Statistics': 'Quarterly Statistics', 'YTD': 'YTD'},
    95: {'Monthly Statistics': 'Monthly Statistics', 'Calls': 'Calls', 'YTD': 'YTD'},
    96: {'Oct 2026': 'October'},
    97: {'Nov 2026': 'November', 'Dec 2026': 'December'},
    100: {'All Groups': 'All Groups'},
    101: {'Run Report': 'Run Report'},
    102: {'Total Calls': 'calls', 'Open': 'open', 'Closed': 'closed'},
    111: {'Staffing': 'staffing'},
    113: {'Call Unit Times': 'unit status chronology'},
}


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def normalized(text):
    return ' '.join(text.split())


def terms(text):
    return re.findall(r"[\w]+", text.casefold())


def contains(text, reference):
    haystack, needle = terms(text), terms(reference)
    return bool(needle) and any(haystack[i:i + len(needle)] == needle for i in range(len(haystack) - len(needle) + 1))


def validate_references(cue, references, row):
    for literal, spoken in references.items():
        assert literal in row['visible_labels'], 'Unobserved literal: ' + literal
        assert contains(cue['text'], spoken), 'Spoken reference absent from this cue: ' + spoken


def service_anchor_words(text):
    pattern = r'\[(\d{2}):(\d{2}):(\d{2})\]'
    markers = list(re.finditer(pattern, text))
    assert markers and markers[0].start() == 0, 'Missing genuine service TXT markers.'
    anchors = []
    words_before = 0
    for i, marker in enumerate(markers):
        seconds = sum(int(n) * factor for n, factor in zip(marker.groups(), [3600, 60, 1]))
        assert not anchors or seconds > anchors[-1]['seconds'], 'Out-of-order service marker.'
        anchors.append({'seconds': seconds, 'word_offset': words_before})
        end = markers[i + 1].start() if i + 1 < len(markers) else len(text)
        words_before += len(text[marker.end():end].split())
    return re.sub(pattern, '', text), anchors


def match_spans(cues, compact, rows):
    """Each exact accepted spoken span must end at a genuine whole-cue boundary."""
    position = 0
    spans, entries = [], []
    for scene in compact['scenes']:
        for screen in scene['ordered_screens']:
            row = rows[screen['capture_id']]
            assert set(screen['required_labels']) <= set(row['visible_labels']), 'Missing required literal control.'
            goal = screen['exact_narration_span'].split()
            begin, spoken = position, []
            while position < len(cues) and len(spoken) < len(goal):
                spoken += cues[position]['text'].split()
                position += 1
            assert spoken == goal, 'Exact span crosses a cue boundary or changes spoken words.'
            assert position > begin
            start = 0.0 if begin == 0 else cues[begin]['start']
            end = cues[position]['start'] if position < len(cues) else None
            assert end is None or end - start >= 3.0, 'Unreadable proposed source hold.'
            span = {
                'scene_id': scene['scene_id'], 'title': scene['title'],
                'capture_id': row['id'], 'source_file': row['file'], 'source_sha256': row['sha256'],
                'first_raw_cue': begin + 1, 'last_raw_cue': position,
                'proposed_start_seconds': start, 'proposed_end_seconds': end,
                'required_labels': screen['required_labels'],
                'exact_narration_span': screen['exact_narration_span'],
                'timing_basis': 'Unchanged actual generated SRT cue boundaries; zero is proposed static opening pre-roll only.' if begin == 0 else 'Unchanged actual generated SRT cue boundaries.',
            }
            spans.append(span)
            for n in range(begin, position):
                entries.append(dict(cues[n], cue=n + 1, scene_id=scene['scene_id'], screenshot_id=row['id'], source_sha256=row['sha256']))
    assert position == len(cues), 'Unassigned speech remains.'
    assert spans[-1]['proposed_end_seconds'] is None, 'No decoded media: final hold must stay open.'
    return spans, entries


def prepare():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    from verify_capture_evidence import _image_dimensions
    for path, digest in PINS.items():
        assert sha(S / path) == digest, 'Changed held input: ' + str(path)
    lesson = json.loads((S / BASE / (NAME + '.narrated-source.json')).read_text())
    manifest = json.loads((S / BASE / (NAME + '.captures.reviewed.json')).read_text())
    freeze = json.loads((S / BASE / 'source-hashes.json').read_text())
    sequence = json.loads((S / BASE / (NAME + '.screen-sequence.json')).read_text())
    compact = json.loads((S / ACCEPTED / 'compact-correspondence.json').read_text())
    acceptance = json.loads((S / ACCEPTED / 'compact-map-acceptance.json').read_text())
    assert acceptance['accepted'] and acceptance['compact_correspondence']['sha256'] == PINS[ACCEPTED / 'compact-correspondence.json']
    for row in freeze['input_files']:
        assert sha(S / row['file']) == row['sha256'], 'Changed held freeze dependency: ' + row['file']
    rows = {row['id']: row for row in manifest['screenshots']}
    assert len(rows) == 23 and len(lesson['scenes']) == 13
    assert not any(row[:3] in {'004', '005', '013', '026'} for row in rows)
    for row in rows.values():
        assert row['eligible_for_lesson'] and row['capture_review']['passed']
        assert row['capture_review']['sha256'] == row['sha256']
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        assert _image_dimensions(S / row['file']) == (row['width'], row['height'])
    cues = load_cues(S / RAW)
    assert len(cues) == 115
    narration = normalized(' '.join(scene['narration'] for scene in lesson['scenes']))
    assert narration == normalized((S / BASE / 'narration.txt').read_text()) == normalized((S / TEXT).read_text())
    assert narration == normalized(' '.join(cue['text'] for cue in cues))
    anchor_text, anchors = service_anchor_words((S / ANCHORS).read_text())
    assert normalized(anchor_text) == narration
    assert len(narration.split()) == 1021
    assert [x['id'] for x in lesson['scenes']] == [x['scene_id'] for x in compact['scenes']]
    for scene, mapping, old in zip(lesson['scenes'], compact['scenes'], sequence['scenes']):
        assert normalized(' '.join(x['exact_narration_span'] for x in mapping['ordered_screens'])) == normalized(scene['narration'])
        assert [x['capture_id'] for x in mapping['ordered_screens']] == [x['capture_id'] for x in old['screens']]
        assert set(scene['required_labels']) <= {label for x in mapping['ordered_screens'] for label in rows[x['capture_id']]['visible_labels']}
    spans, entries = match_spans(cues, compact, rows)
    assert len(spans) == 27
    caption_layout = []
    for cue in entries:
        refs = deepcopy(REFS.get(cue['cue'], {}))
        validate_references(cue, refs, rows[cue['screenshot_id']])
        cue.update(spoken_references=refs, required_labels=list(refs), instructional=bool(refs))
        lines = textwrap.wrap(cue['text'], width=42, break_long_words=False, break_on_hyphens=False)
        if len(lines) > 2:
            lines = textwrap.wrap(cue['text'], width=48, break_long_words=False, break_on_hyphens=False)
        seconds = cue['end'] - cue['start']
        cps = len(cue['text']) / seconds
        assert len(lines) <= 2 and seconds >= 1.0 and cps <= 22.0, ('Review caption readability', cue['cue'])
        caption_layout.append({'cue': cue['cue'], 'duration_seconds': round(seconds, 3), 'characters_per_second': round(cps, 3), 'proposed_lines': lines})
    proposal = {
        'kind': 'PROPOSED pre-audio-QA Reporting actual-service cue correspondence',
        'lesson_id': NAME, 'frozen_lesson_sha256': PINS[BASE / (NAME + '.narrated-source.json')],
        'status': 'Proposed source correspondence only; no approved audio, audio QA, human listening or final renderer inputs.',
        'scenes': 13, 'narration_words': 1021, 'word_count_method': 'Whitespace-separated tokens in the unchanged exact narration.',
        'held_freeze_reported_word_count': 1023, 'source_images': 23, 'source_spans': spans,
        'raw_cue_count': 115, 'cue_correspondence': entries, 'caption_layout': caption_layout,
        'genuine_service_anchor_count': len(anchors), 'anchor_cuts_used': [],
        'caption_splits_or_text_changes': False, 'minimum_closed_hold_seconds': min(x['proposed_end_seconds'] - x['proposed_start_seconds'] for x in spans if x['proposed_end_seconds'] is not None),
        'observed_last_service_cue_end_seconds': cues[-1]['end'], 'decoded_audio_duration_seconds': None,
        'final_screen_end_seconds': None, 'audio_qa_approved': False, 'human_listening_approved': False,
        'parent_timing_review_pending': True, 'renderer_plan_created': False, 'rendered': False,
        'publication_approved': False, 'new_pixel_review_claimed': False,
        'review_attribution': 'Existing exact-image source-agent reviews and separately retained parent script/map acceptance only. This proposal validates their hashes and cue correspondence; it does not assert a new original-pixel inspection.',
        'explicit_choices': [
            '006 staffing headers precede003 lower Casey details;022 monthly headers precede024 lower rows.',
            '007 week parameters and008/009 fifteen-call results remain separate from018/019 Command five-call default-window results and025/027 matched AllGroups sixteen-call comparison.',
            '014 Call Unit Times begins thirty minutes earlier than the initial weekly Call Summary. No identical-window comparison is invented.',
            '015 is the actual report Download CSV control and table; the real CSV artifact independently backs thirteen unit rows/twelve calls and DispatchOnly/Explicit codes. No spreadsheet screen is fabricated.',
            '016 out-of-order timestamps,017 no-unit messages and blank later native-call fields remain literal. Only002 is a genuine staffing chart; no blank Call Summary chart is described.',
            'All27 accepted spans end at whole genuine SRT cue boundaries. One-second TXT is verified and retained, but no marker cut or interpolated word time is needed.',
            'Last observed service cue ends431.969s. This is not a decoded audio duration. Final hold stays unassigned until actual export, full decode/energy QA and User listening approval.',
        ],
    }
    return proposal, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-proposed', action='store_true')
    args = parser.parse_args()
    proposal, manifest = prepare()
    if args.write_proposed:
        assert not OUT.exists(), 'New-only proposal; preserve all historical inputs.'
        assets = {
            'correspondence.proposed.json': encoded(proposal),
            'captures.held-review.json': encoded(manifest),
            'cue-screen-correspondence.txt': ('\n'.join(f"{x['cue']:03} {x['start']:.3f}–{x['end']:.3f} {x['screenshot_id']} | {x['text']}" for x in proposal['cue_correspondence']) + '\n').encode(),
            'ordered27span.compact.txt': ('\n\n'.join(f"{i:02} {x['scene_id']} | raw{x['first_raw_cue']:03}–{x['last_raw_cue']:03} | {x['proposed_start_seconds']:.3f}–" + (f"{x['proposed_end_seconds']:.3f}" if x['proposed_end_seconds'] is not None else 'OPEN pending decoded audio') + f" | {x['capture_id']}\nLabels: " + ' | '.join(x['required_labels']) + '\n' + x['exact_narration_span'] for i, x in enumerate(proposal['source_spans'], 1)) + '\n').encode(),
        }
        provenance = {
            'kind': 'source_only_pre_audio_QA_proposed_Reporting_correspondence',
            'helper_sha256': sha(Path(__file__)), 'input_hashes': {str(k): v for k, v in PINS.items()},
            'frozen_raw_narration_and_captures_unchanged': True,
            'source_reviews_reused_without_new_pixel_attestation': True,
            'actual_audio_not_opened_or_assumed': True, 'parent_timing_review_pending': True,
            'audio_qa_and_complete_User_listening_required_before_final_authoring': True,
            'no_final_renderer_plan_approval_or_canonical_or_site_change': True,
            'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()},
        }
        assets['provenance.json'] = encoded(provenance)
        OUT.mkdir(parents=True)
        for name, body in assets.items():
            with (OUT / name).open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_preflight': True, 'files_written': args.write_proposed, 'scenes': 13, 'words_whitespace': 1021, 'held_freeze_reported_word_count': 1023, 'sources': 23, 'holds': 27, 'unchanged_cues': 115, 'minimum_closed_hold_seconds': round(proposal['minimum_closed_hold_seconds'], 3), 'final_hold': 'OPEN', 'audio_QA_and_listening_pending': True, 'rendered': False}))


if __name__ == '__main__':
    main()
