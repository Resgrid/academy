"""Source-only Pending-call correspondence using genuine SRT/one-second anchors.

Default is read-only. Optional output is a NEW scaffold, never a renderer plan.
Frozen narration, original69cue SRT and22span sequence remain unchanged. Three
existing-image repeats produce25 instruction intervals; two genuine service
anchors propose71 caption parts pending actual downloaded-audio/cue QA/listening.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-dispatch-pending-call-to-dispatch'
BASE = Path('expansion/plans/app-dispatch-pending-call-to-dispatch-capture-freeze-20261028-v2')
PINS = {
    str(BASE / (NAME + '.narrated-source.json')): '53fb3845732f12d57d9367a496b0b3fa7ba638c04c2b7515d6f0801add24f837',
    str(BASE / 'captures.reviewed.json'): 'b84a9502937ba0b15a8b58b8cf396af88eebaf421a89a11291c16e34c3467d8f',
    str(BASE / 'narration.txt'): '0de0ad85031fe0a656d0d47111df76fc53d055bca57d6de3992101c6f26b7ab7',
    str(BASE / 'revision-provenance.json'): 'b14a56280c7252749c6f6f9feb90b77371ed79d1e864479eaf7e2f30aad0752f',
    str(BASE / 'scenario.json'): '5c7a54d60005013889efe11a7ca9ff2754b543a5b5dc316d1b96e1f67d0c414a',
    str(BASE / 'screen-sequence.untimed.json'): '946a37fd5d7fada543a78d74438651c859b3dda11c431a3ce7254065a376c3c9',
    str(BASE / 'source-citations.json'): 'be99b38ba3e5ee6508757cdd531804f461e764fb05a0496a11391e1dca1b1d3f',
    str(BASE / 'source-preflight.json'): '7cf435f9e41c459f1d9adcc116c0c2f0459dc0e700acf1c341c847ba49831487',
    'expansion/audio/app-dispatch-pending-call-to-dispatch-generated-20261028.raw.txt': '7d93bcc3dfe9f55edc42fb9763e1d173e57e12ebc1aa4e904b97dd70d49ff9f8',
    'expansion/audio/app-dispatch-pending-call-to-dispatch-generated-20261028.raw.srt': 'e75592c5fdb2477eba06434052b9ee76791c0a96609abf41aa66aa0a6941febf',
    'expansion/audio/app-dispatch-pending-call-to-dispatch-generated-20261028.one-second.txt': '29260187f6a73890159a2e3485bc0b1af272b764a52b876f314977032f5e55a6',
}
# (raw cue, zero-based word offset, actual service marker, next exact word)
SPLITS = [(18, 6, 57, 'Wallace'), (24, 7, 77, 'choosing')]
# Source transitions use actual raw cue starts, or one of the explicit anchors.
# Repeated003/006 teach title-before-Save; repeated007 shows Dispatch before picker.
CUTS = [
    ('01', '001-console-before-own-pending', 'cue', 1),
    ('01', '002-calls-navigation-pending-entry', 'cue', 5),
    ('01', '003-exact-new-call-fields', 'cue', 6),
    ('02', '004-pending-switch-on-and-footer', 'cue', 11),
    ('03', '004-pending-switch-on-and-footer', 'cue', 18),
    ('03', '005-proposed-boden-only', 'anchor', 57),
    ('03', '006-proposed-recipient-and-full-save', 'cue', 22),
    ('03', '003-exact-new-call-fields', 'cue', 24),
    ('03', '006-proposed-recipient-and-full-save', 'anchor', 77),
    ('04', '007-numbered-pending-identity', 'cue', 26),
    ('04', '008-pending-detail-banner', 'cue', 28),
    ('04', '009-pending-proposed-recipient-readback', 'cue', 31),
    ('05', '007-numbered-pending-identity', 'cue', 34),
    ('05', '010-dispatch-picker-one-saved-member', 'cue', 35),
    ('05', '011-dispatch-empty-selection-disabled', 'cue', 36),
    ('05', '012-dispatch-explicit-boden-confirm', 'cue', 37),
    ('06', '013-pending-empty-after-dispatch', 'cue', 41),
    ('06', '015-active-saved-recipient-readback', 'cue', 43),
    ('07', '016-own-call-close-entry', 'cue', 49),
    ('07', '017-close-own-call-notify-off', 'cue', 50),
    ('08', '023-clean-final-three-original-calls', 'cue', 57),
    ('08', '024-clean-own-call-not-active', 'cue', 59),
    ('08', '025-clean-original-warehouse-active', 'cue', 61),
    ('08', '020-own-record-readable-after-close', 'cue', 62),
    ('08', '023-clean-final-three-original-calls', 'cue', 64),
]
MARKER = re.compile(r'\[(\d\d):(\d\d):(\d\d)\]')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def normalized(text):
    return ' '.join(text.split())


def asset(relative):
    p = (SOURCES / relative).resolve()
    need(p.is_relative_to(SOURCES.resolve()), 'Path escapes staged sources.')
    return p


def proposed_caption_parts(cues, anchor_text, expected):
    need(normalized(' '.join(c['text'] for c in cues)) == expected, 'Raw SRT words differ from frozen narration.')
    need(normalized(MARKER.sub('', anchor_text)) == expected, 'Actual one-second words differ from frozen narration.')
    positions = {}
    for match in MARKER.finditer(anchor_text):
        seconds = int(match[1]) * 3600 + int(match[2]) * 60 + int(match[3])
        position = len(normalized(MARKER.sub('', anchor_text[:match.start()])).split())
        positions.setdefault(seconds, []).append(position)
    proposed, before, records = [], 0, []
    selected = {n: (offset, seconds, word) for n, offset, seconds, word in SPLITS}
    for number, original in enumerate(cues, 1):
        words = original['text'].split()
        if number in selected:
            offset, seconds, word = selected[number]
            need(original['start'] < seconds < original['end'] and words[offset] == word, 'Selected genuine anchor does not fit original cue/word.')
            need(positions.get(seconds) == [before + offset], 'No exact genuine service marker at the selected word boundary; never interpolate.')
            for part, start, end, text in [('a', original['start'], float(seconds), ' '.join(words[:offset])), ('b', float(seconds), original['end'], ' '.join(words[offset:]))]:
                need(end - start >= 2 / 30, 'Proposed actual-anchor caption part too short.')
                proposed.append({'raw_cue': number, 'part': part, 'start': start, 'end': end, 'text': text, 'timing_source': 'actual_exported_one_second_marker', 'audio_energy_approved': False})
            records.append({'raw_cue': number, 'split_at_actual_service_seconds': seconds, 'word_offset': offset, 'right_hand_word': word, 'word_precision_seconds': 1, 'interpolated': False, 'audio_energy_approved': False})
        else:
            proposed.append(dict(original, raw_cue=number, part='whole', timing_source='unchanged_actual_raw_srt', audio_energy_approved=False))
        before += len(words)
    need(normalized(' '.join(c['text'] for c in proposed)) == expected and len(proposed) == len(cues) + 2, 'Derived candidate lost/repeated spoken words.')
    return proposed, records


def prepare():
    for relative, digest in PINS.items():
        need(sha(asset(relative)) == digest, 'Changed held source/transcript: ' + relative)
    sys.path.insert(0, str(ROOT / 'scripts'))
    from render_walkthrough import load_cues
    from verify_capture_evidence import _Validator, _image_dimensions
    lesson = read(asset(str(BASE / (NAME + '.narrated-source.json'))))
    manifest = read(asset(str(BASE / 'captures.reviewed.json')))
    shots = {row['id']: row for row in manifest['screenshots']}
    untimed = read(asset(str(BASE / 'screen-sequence.untimed.json')))
    need(len(lesson['scenes']) == 8 and len(shots) == 20 and len(untimed['sequence']) == 22, 'Held8scene/20source/22span inventory differs.')
    for row in shots.values():
        need(sha(asset(row['file'])) == row['sha256'] and _image_dimensions(asset(row['file'])) == (row['width'], row['height']), 'Actual original screenshot bytes/dimensions differ.')
        need(sha(asset(row['dom_file'])) == row['dom_sha256'], 'Actual original DOM differs.')
        validator = _Validator(SOURCES); validator.observations(row, row['id'])
        need(not validator.issues, '; '.join(validator.issues))
    for citation in read(asset(str(BASE / 'source-citations.json'))):
        need(sha(asset(citation['file'])) == citation['sha256'], 'Copied source citation changed.')
    expected = normalized(' '.join(sc['narration'] for sc in lesson['scenes']))
    prefix = 'expansion/audio/' + NAME + '-generated-20261028'
    need(normalized(asset(prefix + '.raw.txt').read_text()) == expected and len(expected.split()) == 598, 'Actual plain transcript differs from frozen598words.')
    cues = load_cues(asset(prefix + '.raw.srt'))
    need(len(cues) == 69, 'Actual raw cue count differs.')
    proposed, splits = proposed_caption_parts(cues, asset(prefix + '.one-second.txt').read_text(), expected)
    scenes = {sc['id']: sc for sc in lesson['scenes']}
    starts = [cues[n - 1]['start'] if method == 'cue' else float(n) for _, _, method, n in CUTS]
    spans, assigned = [], []
    for index, (scene_id, ident, method, n) in enumerate(CUTS):
        start = starts[index]
        end = starts[index + 1] if index + 1 < len(starts) else cues[-1]['end']
        need(end - start >= 2, 'Unreadable source flash; do not invent a time to lengthen it.')
        current = [dict(c, candidate_cue=j + 1) for j, c in enumerate(proposed) if c['start'] >= start - 1e-9 and c['end'] <= end + 1e-9]
        need(current, 'Source interval has no actual speech correspondence.')
        assigned.extend(c['candidate_cue'] for c in current)
        shot = shots[ident]
        spans.append({'interval': index + 1, 'scene_id': scene_id, 'screenshot_id': ident, 'file': shot['file'], 'sha256': shot['sha256'], 'actual_exported_boundary': start, 'next_actual_exported_boundary': starts[index + 1] if index + 1 < len(starts) else None, 'boundary_method': 'actual_raw_srt_cue_start' if method == 'cue' else 'actual_exported_one_second_marker', 'raw_cue_or_marker': n, 'first_candidate_cue': current[0]['candidate_cue'], 'last_candidate_cue': current[-1]['candidate_cue'], 'last_actual_speech_end': current[-1]['end'], 'literal_source_labels': shot['visible_labels'], 'cue_correspondence': current, 'instruction_review_status': 'source-only correspondence; manual spoken-reference approval and actual-audio cue energy required before renderer plan'})
    need(assigned == list(range(1, 72)), 'Candidate speech has source gaps/overlap or an unsupported midcue cut.')
    for sc in lesson['scenes']:
        chosen = [x for x in spans if x['scene_id'] == sc['id']]
        words = ' '.join(c['text'] for x in chosen for c in x['cue_correspondence'])
        need(normalized(words) == normalized(sc['narration']), 'A scene lost or borrowed spoken words.')
        visible = {label for x in chosen for label in x['literal_source_labels']}
        need(set(sc['required_labels']) <= visible, 'Scene named controls lack actual reviewed pixels.')
    return {'kind': 'source_actual_transcript_correspondence_scaffold_only', 'lesson_id': NAME, 'source_pins': PINS, 'frozen_lesson_sha256': PINS[str(BASE / (NAME + '.narrated-source.json'))], 'words': 598, 'scenes': 8, 'actual_sources': 20, 'original_untimed_spans': 22, 'source_intervals_proposed': 25, 'raw_actual_cues': 69, 'candidate_caption_parts': 71, 'source_spans': spans, 'genuine_anchor_splits': splits, 'original_inputs_unchanged': True, 'sequence_revision': {'new_existing_image_repeats': ['003-exact-new-call-fields for title/Nature check in cue24', '006-proposed-recipient-and-full-save after the title check at genuine77s', '007-numbered-pending-identity before picker for queue Dispatch in cue34'], 'new_screenshots_created': False, 'unseen_menu_or_typing_steps_invented': False}, 'source_review_attribution': 'Retained exact original JPEG/DOM reviews by Codex dispatch_ic_coverage and parent critical012/017/023 original-pixel review. This scaffold is not a new video or playback review.', 'timing_precision': 'Two actual Descript one-second anchors; no interpolation or finer word precision. Other transitions use actual raw cue starts. Service anchors require cue-energy QA against downloaded audio before caption approval.', 'first_frame_start': None, 'decoded_audio_end_and_final_hold': None, 'audio_approved': False, 'renderer_plan_created': False, 'publication_approved': False, 'pending_requirements': ['Parent-obtained actual M4A hash and complete decoded duration/sample inventory.', 'Exact-script/raw/candidate-cue energy QA against actual downloaded audio; keep raw69cue SRT unchanged.', 'Actual complete listening approval bound to frozen source and actual audio.', 'Manual exact spoken-reference mapping and source/pixel/readable-hold approval before renderer plan.', 'Every encoded source/caption interval and actual native beginning/middle/end browser playback after rendering.'], 'scope_limits': ['Historical captured51015/FD51-2026-0007 is this example only; replay uses fresh normal-UI identity.', 'Only own fictional call was closed with actual NotifyOFF; original3calls and command remain preserved.', 'Pending Dispatched tab is proposed recipients until the pending state is actually dispatched.', 'No provider receipt, physical response, GPS, native device or archived-call result is established.', 'Rejected React warning originals remain preserved and excluded.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-scaffold', type=Path)
    args = parser.parse_args(); scaffold = prepare()
    if args.write_scaffold:
        target = args.write_scaffold.resolve()
        need(target.is_relative_to((SOURCES / 'expansion/plans').resolve()) and not target.exists(), 'Use a NEW source-plan file; preserve original history.')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8') as stream: stream.write(json.dumps(scaffold, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'source_transcript_preflight': 'passed', 'scenes': 8, 'words': 598, 'actual_sources': 20, 'original_untimed_spans': 22, 'proposed_source_intervals': 25, 'actual_raw_cues': 69, 'candidate_caption_parts': 71, 'genuine_one_second_splits': [57, 77], 'scaffold_written': bool(args.write_scaffold), 'renderer_plan_created': False, 'audio_or_publication_approved': False}, indent=2))


if __name__ == '__main__':
    main()
