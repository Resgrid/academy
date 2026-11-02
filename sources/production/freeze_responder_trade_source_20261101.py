"""Retain the actually reviewed Responder trade source without changing the apps.

Default is read-only. --freeze copies hash-verified source images/DOM and writes
only new source review files. This records an already-performed pixel review;
it does not approve narration, video frames, playback, or publication.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

S = Path(__file__).resolve().parents[1]
BASE = Path('expansion/plans/app-responder-shift-trade-request-cancel-source-proposal-20261101')
RAW = Path('captures/expansion/responder-shift-trade-approved-20261101')
PINS = {
    BASE / 'lesson.candidate.json': '922f6d54e7aaca8115fa71547dc6da063abe2988fc5725d09740e35172bc9d92',
    RAW / 'manifest.json': '474ebeeda7fbdd321adacc70d1277f1c300cdfb9b5fb2335c7aa7c1353bf5117',
}
REVIEWED_IMAGES = {
    '001-future-standby-overview': '1d24a400787cffb6d859a834a87f269c4b014c9665ee50e26e892677a67c4b08',
    '002-trade-candidates': '9d5298d3b076409388a9a597f4fbf23ccb4fd479fb66951222e5ff9cb6996c0a',
    '003-request-ready-to-send': 'aedddee04a0f3eec0c77c4010a717e5339c7a193afb5d2ec121c90d9071a7b9b',
    '004-request-saved-notice': 'c5b9bd56dcd700a7ef6a8de46151a9769afe0c7080fd940155ab5e4b8c448357',
    '005-outgoing-open-no-reply': 'ac03f99a7c870ff18ac7f3685971cb2b2d0bd67ae5eb9f8a4951a72dfa98fa4d',
    '006-cancel-confirmation': 'afdbbd747c7743ed7b97dd39628ff1eef1df59eeaad9f975089fb7dbe49b82e0',
    '008-reloaded-trades-empty': '04e12fffc023942297b7798754e94e894585a901f3ecc43b636fb4cc87707817',
    '009-reopened-day-request-restored': '1d24a400787cffb6d859a834a87f269c4b014c9665ee50e26e892677a67c4b08',
    '010-roster-still-boden': '3408c36b5817c41b24497949c0aa5163b4f493e80c5854c3ca46cff07cc72c9a',
    '011-return-calendar-after-cancel': 'ba26b3289c00b0cffa86312be3939900a8a52401fb7e1f9254774c92dda158d4',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    for path, digest in PINS.items():
        assert sha(S / path) == digest, 'Changed reviewed source: ' + str(path)
    lesson = json.loads((S / BASE / 'lesson.candidate.json').read_text())
    raw = json.loads((S / RAW / 'manifest.json').read_text())
    by_id = {row['id']: row for row in raw['captures']}
    assert len(lesson['scenes']) == 11 and len(lesson['sector_examples']) == 6
    assert {ref for scene in lesson['scenes'] for ref in scene['capture_refs']} == set(REVIEWED_IMAGES)
    rows, files = [], {}
    at = datetime.now(timezone.utc).isoformat()
    for id, digest in REVIEWED_IMAGES.items():
        row = deepcopy(by_id[id])
        assert row['sha256'] == digest and sha(S / row['file']) == digest
        assert sha(S / row['dom_file']) == row['dom_sha256']
        labels = list(dict.fromkeys(label for scene in lesson['scenes'] if id in scene['capture_refs'] for label in scene['required_labels']))
        # These exact labels were personally read in the complete actual pixels.
        # Background DOM text and clipped controls are intentionally not accepted.
        raw_source = {'manifest_file': str(RAW / 'manifest.json'), 'manifest_sha256': PINS[RAW / 'manifest.json'],
                      'capture_id': id, 'image_file': row['file'], 'image_sha256': digest,
                      'dom_file': row['dom_file'], 'dom_sha256': row['dom_sha256']}
        image_path, dom_path = BASE / 'images' / (id + '.jpg'), BASE / 'dom' / (id + '.dom.txt')
        files[image_path] = (S / row['file']).read_bytes()
        files[dom_path] = (S / row['dom_file']).read_bytes()
        row.update(file=str(image_path), dom_file=str(dom_path), visible_labels=labels,
                   visible_controls=[], visible_field_text=[], required_labels=labels,
                   missing_required_labels=[], eligible_for_lesson=True, publication_eligible=True,
                   accepted=True, review_status='accepted_bounded_source',
                   visual_review='completed_actual_image_review', raw_source=raw_source,
                   capture_review={'passed': True, 'reviewer': 'Codex /root', 'reviewed_at': at,
                                   'sha256': digest, 'application_visible': True, 'no_errors': True,
                                   'controls_reviewed': True, 'controls_fully_visible': True,
                                   'controls_unobstructed': True,
                                   'method': 'Root personally viewed every selected complete actual screenshot. Only the listed teaching text and controls were accepted. This is source-pixel review, not final video qualification.'})
        rows.append(row)
    narration = '\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n'
    manifest = {'app': 'Responder', 'source_manifest': str(RAW / 'manifest.json'),
                'source_manifest_sha256': PINS[RAW / 'manifest.json'], 'reviewer': 'Codex /root',
                'reviewed_at': at, 'actual_raw_images_personally_viewed': 10,
                'accepted_actual_images': 10, 'screenshots': rows}
    files[BASE / 'captures.reviewed.json'] = encoded(manifest)
    files[BASE / 'narration.txt'] = narration.encode()
    files[BASE / 'source-review.json'] = encoded({
        'created_at': at, 'reviewer': 'Codex /root',
        'lesson_sha256': PINS[BASE / 'lesson.candidate.json'],
        'capture_manifest_sha256': hashlib.sha256(encoded(manifest)).hexdigest(),
        'script_sha256': hashlib.sha256(narration.encode()).hexdigest(),
        'words': len(narration.split()), 'scenes': 11, 'actual_source_images': 10,
        'source_images_reviewed': True, 'export_ready': False,
        'scope': 'One approved fictional trade request, its cancellation, refreshed empty queue and retained roster. No offer, acceptance, approval, reassignment or provider notification delivery is claimed.',
        'remaining': ['Generate and verify complete natural narration.', 'Obtain an authorized private audio export and genuine full listening review.',
                      'Match actual speech timing to all actual screens.', 'Review encoded frames and captions and verify genuine advancing browser playback before qualification.']})
    assert all(not (S / path).exists() for path in files), 'Refusing to overwrite a source freeze.'
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    files = prepare()
    if args.freeze:
        for path, data in files.items():
            destination = S / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('xb') as stream:
                stream.write(data)
    print(json.dumps({'new_source_files': len(files), 'written': args.freeze,
                      'app_mutations': 0, 'narration_or_video_approval_generated': False,
                      'canonical_or_site_changes': 0, 'git_mutations': 0}))
