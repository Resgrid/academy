"""Prepare a reviewed-source cue-map proposal, never a finished-video approval.

Times come from the repaired Descript SRT. The final container duration, decoded
audio, listening review, encoded frames and browser playback are still required.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'scripts'))
NAME = 'core-records-review-defaults'
BASE = Path('expansion/plans') / (NAME + '-source-proposal-20261101')
CAPTIONS = Path('expansion/audio') / (NAME + '.actual.raw.srt')
CROSS = Path('captures/expansion/core-records-policy-reference-20261101/captures.reviewed.json')
DESTINATION = Path('expansion/plans') / (NAME + '-cue-map-proposal-20261101')
HELP_LIFECYCLE = 'Default lifecycle for new department-owned definitions. Locked definitions retain their own lifecycle.'
HELP_DEADLINE = 'Default administrative review deadline; a definition-level override takes precedence. This is not a statutory deadline inference.'
# Retain the actual Root source review from this recovery turn. A future run
# reuses this same image-bound observation; it does not claim a new review.
LITERAL_REVIEWED_AT = '2026-11-02T01:39:57+00:00'
SPANS = [
    ('01', 1, 8, '014-records-manage-menu'),
    ('02', 9, 19, '002-baseline-selected-preset-visible'),
    ('03', 20, 26, '003-prepared-reviewrequired-48-hours'),
    ('04', 27, 32, '004-save-defaults-control'),
    ('05', 33, 37, '005-reviewrequired-and-deadline-saved'),
    ('06', 38, 43, '006-defaults-persist-after-reopen'),
    ('07', 44, 47, '014-records-manage-menu'),
    ('08', 48, 51, '007-locked-definition-policies-remain'),
    ('08', 52, 53, '006-defaults-persist-after-reopen'),
    ('08', 54, 56, '007-locked-definition-policies-remain'),
    ('09', 57, 62, '015-department-definition-row-and-edit'),
    ('10', 63, 69, '008-published-definition-retains-policy'),
    ('11', 70, 74, '010-definition-deadline-and-role-controls'),
    ('11', 75, 76, '002-baseline-selected-preset-visible'),
    ('11', 77, 79, '001-definition-review-policy-together'),
    ('12', 80, 85, '011-original-defaults-prepared-for-restoration'),
    ('13', 86, 89, '004-save-defaults-control'),
    ('14', 90, 94, '012-original-defaults-restored'),
    ('15', 95, 104, '013-original-defaults-persist-after-reopen'),
]
REFERENCES = {
    2: {'Records': 'Records area', 'All records': 'All records', 'Manage': 'Manage'},
    3: {'Settings': 'Settings', 'Definitions': 'Definitions'},
    4: {'Settings': 'Settings', 'Definitions': 'Definitions'},
    6: {'Settings': 'Settings'},
    9: {'Records Settings': 'Records Settings', 'Default lifecycle preset for department definitions': 'Default lifecycle preset for department definitions'},
    10: {'QuickEntry': 'Quick Entry'},
    11: {'Review due (hours)': 'Review due, in hours', '72': 'seventy-two'},
    13: {HELP_LIFECYCLE: 'locked definitions retain their own lifecycle'},
    14: {HELP_DEADLINE: 'definition-level deadline override takes precedence'},
    16: {HELP_DEADLINE: 'administrative review interval'},
    17: {HELP_DEADLINE: 'statutory deadline'},
    20: {'ReviewRequired': 'Review Required', 'Default lifecycle preset for department definitions': 'Default lifecycle preset'},
    21: {'Default lifecycle preset for department definitions': 'for department definitions', '48': 'forty-eight', 'Review due (hours)': 'Review due, in hours'},
    23: {'48': 'Forty-eight'},
    28: {'Save': 'Save', 'Cancel': 'Cancel'},
    29: {'Save': 'Save'},
    33: {'Records settings saved.': 'Records settings saved'},
    34: {'ReviewRequired': 'Review Required', 'Review due (hours)': 'review deadline', '48': 'forty-eight'},
    38: {'Records Settings': 'Records Settings', 'ReviewRequired': 'Review Required', '48': 'forty-eight hours'},
    44: {'All records': 'All records', 'Manage': 'Manage'},
    45: {'Definitions': 'Definitions'},
    48: {'Definitions': 'Definitions', 'Owner': 'Owner', 'Published version': 'Published version'},
    49: {'Lifecycle preset': 'Lifecycle preset'},
    50: {'Run': 'Run', 'Training': 'Training', 'Product (locked)': 'Product, locked'},
    51: {'Published version': 'published version one', 'QuickEntry': 'Quick Entry'},
    53: {'ReviewRequired': 'Review Required'},
    54: {'QuickEntry': 'Quick Entry'},
    57: {'TRAINING ONLY - Community software exercise': 'Training Only, Community software exercise'},
    58: {'Department': 'Department', 'QuickEntry': 'Quick Entry'},
    59: {'Edit': 'Edit'},
    60: {'Edit': 'Edit'},
    63: {'Published': 'Published'},
    64: {'This version is published and read-only. Open a new draft to make changes.': 'this version is published and read-only'},
    65: {'Open new draft': 'Open new draft'},
    66: {'Lifecycle preset': 'Lifecycle preset', 'QuickEntry': 'Quick Entry'},
    68: {'Open new draft': 'Open new draft'},
    70: {'Reviewer roles': 'Reviewer roles', 'Approver roles': 'Approver'},
    71: {'Approver roles': 'roles', 'Review due (hours)': 'Review due, in hours'},
    72: {'Review due (hours)': 'review deadline field'},
    75: {HELP_DEADLINE: 'department settings help'},
    76: {HELP_DEADLINE: 'definition-level deadline override'},
    77: {'Reviewer roles': 'role assignments', 'Approver roles': 'role assignments', 'Lifecycle preset': 'selected lifecycle', 'Review due (hours)': 'review'},
    78: {'Review due (hours)': 'interval'},
    80: {'Records Settings': 'Records Settings'},
    81: {'QuickEntry': 'Quick Entry', '72': 'seventy-two'},
    86: {'Save': 'Save'},
    88: {'Save': 'save them'},
    90: {'Records settings saved.': 'Records settings saved'},
    91: {'QuickEntry': 'Quick Entry', '72': 'seventy-two hours'},
    95: {'QuickEntry': 'Quick Entry', '72': 'seventy-two hours'},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(write=False):
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import _Validator, _normalized, instruction_scene_digest
    from expansion_site import lesson_content_digest

    pins = {
        BASE / 'lesson.candidate.json': 'ec824bb6f36081b37f88a424c6eedfc20b1aaf13bebeee93fcfe9592b28c0497',
        BASE / 'captures.reviewed.json': '3af5a9b006b380e2585709285c9295fb6a34af6c3b312fd1425346a1d637def7',
        CAPTIONS: 'e04ae1ed80ffb992ecd3ef222509e2be1cbf0e2111351d3fc30fa803351c4e06',
        CROSS: '8a0af241a36052c6a23baec58adf84b20e8711eb4774eb8369200cd68207bf94',
    }
    for file, digest in pins.items():
        assert sha(S / file) == digest, str(file)
    lesson = json.loads((S / BASE / 'lesson.candidate.json').read_text())
    manifest = deepcopy(json.loads((S / BASE / 'captures.reviewed.json').read_text()))
    cross = json.loads((S / CROSS).read_text())
    for row in cross['screenshots']:
        assert row['id'] not in {r['id'] for r in manifest['screenshots']}
        manifest['screenshots'].append(row)
    rows = {row['id']: row for row in manifest['screenshots']}
    baseline = rows['002-baseline-selected-preset-visible']
    assert baseline['sha256'] == 'addc39062fb70ecc3f978530fe1d49daaad01dbf210a74c408ca0a95a1b22c4a'
    extra = {'reviewer': 'Codex /root', 'reviewed_at': LITERAL_REVIEWED_AT,
             'capture_id': baseline['id'], 'source_sha256': baseline['sha256'],
             'labels': [HELP_LIFECYCLE, HELP_DEADLINE],
             'method': 'Root personally viewed this complete actual source image during the recovery turn. Both complete help paragraphs are readable beneath their respective controls. These observations add literal source text only; no final-video or listening approval is inferred.'}
    baseline['visible_labels'] = list(dict.fromkeys([*baseline['visible_labels'], *extra['labels']]))
    baseline['additional_literal_review'] = {'file': str(DESTINATION / 'additional-literal-observations.json')}
    observed = {}
    for row in rows.values():
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        validator = _Validator(S)
        observed[row['id']] = validator.observations(row, row['id'])
        assert not validator.issues, validator.issues
    cues = load_cues(S / CAPTIONS)
    assert len(cues) == 104
    assert words(' '.join(cue['text'] for cue in cues)) == words(' '.join(scene['narration'] for scene in lesson['scenes']))
    # Only a planning value from the generated composition; final encoded inputs
    # must replace this with the decoded, approved exported-container duration.
    proposed_duration = 359.68
    holds, entries = [], []
    for index, (scene_id, first, last, capture_id) in enumerate(SPANS):
        start = 0.0 if index == 0 else cues[first - 1]['start']
        end = cues[SPANS[index + 1][1] - 1]['start'] if index + 1 < len(SPANS) else proposed_duration
        holds.append({'scene_id': scene_id, 'screenshot_id': capture_id, 'first_cue': first, 'last_cue': last, 'start': start, 'end': end})
        for number in range(first, last + 1):
            cue = cues[number - 1]
            aliases = REFERENCES.get(number, {})
            assert cue['start'] >= start and cue['end'] <= end
            labels = {_normalized(label) for label in aliases}
            assert labels <= observed[capture_id], (number, capture_id)
            entry = dict(cue, cue=number, scene_id=scene_id, screenshot_id=capture_id,
                         required_labels=list(aliases), spoken_references=aliases, instructional=bool(aliases))
            validator = _Validator(S)
            validator.spoken_references(entry, labels, str(number), True)
            assert not validator.issues, validator.issues
            entries.append(entry)
    assert [entry['cue'] for entry in entries] == list(range(1, 105))
    scenes = []
    learner = deepcopy(lesson)
    for original, projection in zip(lesson['scenes'], learner['scenes']):
        selected = [hold for hold in holds if hold['scene_id'] == original['id']]
        selected_cues = [{k: v for k, v in row.items() if k != 'scene_id'} for row in entries if row['scene_id'] == original['id']]
        assert words(' '.join(row['text'] for row in selected_cues)) == words(original['narration'])
        assert {_normalized(label) for label in original['required_labels']} <= set().union(*(observed[hold['screenshot_id']] for hold in selected))
        assert any(row['required_labels'] for row in selected_cues)
        projection['capture_refs'] = list(dict.fromkeys([*projection['capture_refs'], *[hold['screenshot_id'] for hold in selected]]))
        scene = {'id': original['id'], 'title': original['title'], 'kind': 'operational',
                 'start': selected[0]['start'], 'end': selected[-1]['end'],
                 'visual_required_labels': original['required_labels'],
                 'screens': [{k: hold[k] for k in ['screenshot_id', 'start', 'end']} for hold in selected], 'captions': selected_cues}
        scene['proposed_mapping_sha256'] = instruction_scene_digest(scene, rows)
        scenes.append(scene)
    assert lesson_content_digest(lesson) == lesson_content_digest(learner)
    proposal = {'created_at': datetime.now(timezone.utc).isoformat(), 'lesson_id': NAME,
                'lesson_file': str(BASE / 'lesson.candidate.json'), 'lesson_sha256': pins[BASE / 'lesson.candidate.json'],
                'captions_file': str(CAPTIONS), 'captions_sha256': pins[CAPTIONS],
                'duration_seconds_provisional': proposed_duration, 'duration_source': 'Descript generated composition metadata; exported-container QA pending',
                'scenes': scenes, 'holds': holds, 'cues': entries,
                'cue_count': len(cues), 'scenes_count': len(scenes), 'holds_count': len(holds),
                'distinct_source_images_used': len({row['sha256'] for row in rows.values()}),
                'learner_content_sha256': lesson_content_digest(learner),
                'review_state': 'proposal_only_no_audio_decoding_hearing_encoded_or_browser_approval_inferred',
                'export_ready': False}
    if write:
        destination = S / DESTINATION
        assert not destination.exists()
        destination.mkdir()
        for name, value in [('captures.source-relative.json', manifest), ('correspondence.proposed.json', proposal),
                            ('lesson.learner-projection.proposed.json', learner), ('additional-literal-observations.json', extra)]:
            (destination / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        (destination / 'cue-screen-correspondence.txt').write_text('\n\n'.join(
            f"Cue{row['cue']:03} · scene{row['scene_id']} · {row['start']:.3f}–{row['end']:.3f} · {row['screenshot_id']}\n{row['text']}\nLiteral -> exact speech: {json.dumps(row['spoken_references'], ensure_ascii=False)}"
            for row in entries) + '\n')
    return {'passed': True, 'lesson_id': NAME, 'scenes': len(scenes), 'holds': len(holds),
            'actual_cues': len(cues), 'actual_source_images': len(rows), 'written': write,
            'decoded_audio_or_listening_or_final_video_approval': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-proposal', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.prepare_proposal), indent=2))
