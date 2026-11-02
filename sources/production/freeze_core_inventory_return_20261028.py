"""Freeze the independently reviewed Return source package; default is read-only.

No speech, timing, media qualification, stock replay or publication is performed.
The recorded issuance is already Returned with zero outstanding.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCES = Path(__file__).resolve().parents[1]
ORIGINAL = SOURCES / 'expansion/plans/core-inventory-return-reconcile-candidate-20261028'
DESTINATION = SOURCES / 'expansion/plans/core-inventory-return-reconcile-capture-freeze-20261028'
NAME = 'core-inventory-return-reconcile'
PINS = {
    'captures.reviewed.json': '0e689449ad86607f8fe99371c55bee9d691791cfb2dd5c05bbe56d74213e624f',
    'lesson.candidate.json': 'ede45b4333ca32d7945ebce60c36a33b8031b9c2559e0a128279c8f29ccc2f5a',
    'narration.candidate.txt': 'f8ad8d1cb0828566244034b80e518ec65d6f9ae162ba2a513565446bba1f7661',
    'scenario-fixture.json': 'd265ac998bbdc8face131adfe6d60d819f81ea4678e961acbdfc30a1997360b9',
    'source-citations.json': 'ee8d1d5eed76b93829f87d3e842f8150954d553e57751640528f421b27cc129a',
    'source-preflight.json': '9268b7c6a838e79dd06686ce26cfe9847f372ae47cfc538bb157020cddb4e44f',
    'untimed-screen-sequence.json': '3e3bb92a841bb70e0d703500ee2cb1ae5bdb559735844ecbdfe20c36b42a0b95',
    'source/Core/Core/Resgrid.Model/Inventories/InventoryContracts.cs': '369cc895c2657abc0a2956c3c7940bf5318b1746c7246551e5542acbdbfa33e3',
    'source/Core/Core/Resgrid.Services/InventoryIssuance.cs': 'e43b0815fa502444452e37f252362023efd8663436f4d299228d8d0ce956b485',
    'source/Core/Web/Resgrid.Web/Areas/User/Controllers/InventoryController.cs': 'f77b3e69c1c0499dafc5ce9d401bd87bca8e9517d8ce2f54ccb4781bb06a9107',
    'source/Core/Web/Resgrid.Web/Areas/User/Views/Inventory/Workspace.cshtml': 'e91d91df5e6682c7bb5154cbdcabe35bf68b48b6f6bc308e2f48f1214b86c053',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def prepare():
    for name, expected in PINS.items():
        assert digest(ORIGINAL / name) == expected, 'Reviewed input changed: ' + name
    lesson = json.loads((ORIGINAL / 'lesson.candidate.json').read_text())
    manifest = json.loads((ORIGINAL / 'captures.reviewed.json').read_text())
    sequence = json.loads((ORIGINAL / 'untimed-screen-sequence.json').read_text())
    assert lesson['id'] == NAME and len(lesson['scenes']) == 8
    assert len(manifest['screenshots']) == 10 and len(sequence['spans']) == 16
    by_id = {shot['id']: shot for shot in manifest['screenshots']}
    for shot in by_id.values():
        assert shot['eligible_for_lesson'] and shot['capture_review']['passed']
        for file_key, hash_key in [('file', 'sha256'), ('dom_file', 'dom_sha256')]:
            relative = Path(shot[file_key])
            assert not relative.is_absolute() and '..' not in relative.parts
            assert digest(SOURCES / relative) == shot[hash_key], 'Capture changed: ' + shot['id']
    for scene in lesson['scenes']:
        assert scene['capture_refs'] and set(scene['capture_refs']) <= set(by_id)
        labels = {label for ref in scene['capture_refs'] for label in by_id[ref]['visible_labels']}
        assert set(scene['required_labels']) <= labels
    narration = '\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n'
    assert narration.encode() == (ORIGINAL / 'narration.candidate.txt').read_bytes()
    assert ' '.join(span['narration_exact'] for span in sequence['spans']) == ' '.join(scene['narration'] for scene in lesson['scenes'])
    assert sum(len(scene['narration'].split()) for scene in lesson['scenes']) == 508
    assert len(lesson['sector_examples']) == 6
    lesson.update(source_complete=True, source_freeze_review='parent-source-review.json')
    review = {
        'lesson_id': NAME, 'reviewer': 'Codex parent independent actual source and script review',
        'reviewed_at': '2026-10-28T23:02:00Z', 'source_only': True,
        'inputs': PINS, 'actual_original_sources_reviewed': 10,
        'narration_words': 508, 'narration_paragraphs': 8,
        'notes': [
            'Parent recorded and viewed the real original1434x773 images and read all508words.',
            'Captures show the Return launcher, settled form, amount, destination, unsaved condition alternatives, final Return, saved Returned0, ledger and reconciled balances.',
            'On hand and History launchers are supplied by002/009. Clipped headings in001/010/011 are not invented as visible labels.',
            'Starting13/5/1 and final14/5/0 both total19 following the earlier Consume1. The separate older20pack lesson remains unchanged.',
            'The completed example must not be returned again or reset. Replay fixture stops on Returned0 and requires a different permitted positive-outstanding issuance.',
            'No PDF, count, witness, rebuild, physical inspection or repair outcome is demonstrated.',
        ],
        'publication_approved': False, 'audio_reviewed': False, 'timings_assigned': False,
    }
    files = {name: (ORIGINAL / name).read_bytes() for name in PINS if name not in ['lesson.candidate.json', 'narration.candidate.txt']}
    files[NAME + '.narrated-source.json'] = encoded(lesson)
    files['narration.txt'] = narration.encode()
    files['parent-source-review.json'] = encoded(review)
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    files = prepare()
    if args.freeze:
        assert not DESTINATION.exists(), 'Preserve the existing frozen package.'
        DESTINATION.mkdir()
        for name, data in files.items():
            path = DESTINATION / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'source_preflight': 'passed', 'frozen': args.freeze, 'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}, indent=2))
