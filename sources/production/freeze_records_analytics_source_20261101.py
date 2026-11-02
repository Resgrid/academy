"""Retain the already reviewed Analytics source; default is read-only.

--freeze writes new copies and source review only. Root actually viewed every
image below. No speech, encoded-frame, playback or publication approval is made.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

S = Path(__file__).resolve().parents[1]
BASE = Path('expansion/plans/core-records-analytics-summary-workload-source-proposal-20261101')
RAW = Path('captures/expansion/core-records-analytics-20261101')
LESSON_SHA = 'e7d697afba265c7fa8194f8bd0cf101a89dbaff2299ac7d94f607aefc7c8c866'
MANIFEST_SHA = 'e07f4205b20ffb0edca79f802ed4fcbd8a2ac62adc8f1f26bae173c2ccd5550d'
PIXELS = {
    '002-summary-measures': 'c9e7213f44b985663ce2a2ac9a5dbfa032fe9651292f883e0d98db207e36db6f',
    '003-headline-figures': 'ad716eba03a8928e16db41f689cc002f5e55593e685b1f925b015e9115568d63',
    '004-training-filter-prepared': 'bd1a22228fc391854bda33427733f9ebd652ae735181bf3d815b99f03b625590',
    '005-training-filter-applied': '93a58f0094ad94f7eadebc3c135046554e62d781dd02e5c3cc116e1aaa1e5bf6',
    '006-training-headline-figures': 'dc46e29304339795cddae78223a73a1774c6e1afad8fd635de0b9ff3b0c048ed',
    '007-engine-training-filter-applied': '06b45f56dc544b19763378798038b30711968f85f4285cb343754e5e33f3c88b',
    '008-empty-subset-headline': '83a79639977f9e1d3c3a1473b7b36ec133197c19662217a9203c2f7132d01ed9',
    '009-restored-all-filters-navigation': '60ccee0d16b582f4b54edd61cd04ff243de2318cf41897b746d600c94e58ba1b',
    '010-workload-overview': 'e79a47abad4b093a3ba9007d238bd16b5146873232dd002cdb30ef2af824c969',
    '012-workload-weekday-hour': '976b60aaafce605fb21a71502f6f21c14f6c1b18392825e347a8b293ae004253',
    '013-workload-complete-breakdowns': '423a5b45da6f0f7134f83855631c412a64cd293ea9f84a520fab936456da6615',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    assert sha(S / BASE / 'lesson.candidate.json') == LESSON_SHA
    assert sha(S / RAW / 'manifest.json') == MANIFEST_SHA
    lesson = json.loads((S / BASE / 'lesson.candidate.json').read_text())
    raw = json.loads((S / RAW / 'manifest.json').read_text())
    by_id = {row['id']: row for row in raw['captures']}
    assert len(lesson['scenes']) == 13 and len(lesson['sector_examples']) == 6
    assert {ref for scene in lesson['scenes'] for ref in scene['capture_refs']} == set(PIXELS)
    at = datetime.now(timezone.utc).isoformat()
    rows, files = [], {}
    for id, digest in PIXELS.items():
        row = deepcopy(by_id[id])
        assert row['sha256'] == digest and sha(S / row['file']) == digest
        assert sha(S / row['dom_file']) == row['dom_sha256']
        source = {'manifest_file': str(RAW / 'manifest.json'), 'manifest_sha256': MANIFEST_SHA,
                  'capture_id': id, 'image_file': row['file'], 'image_sha256': digest,
                  'dom_file': row['dom_file'], 'dom_sha256': row['dom_sha256']}
        labels = list(dict.fromkeys(label for scene in lesson['scenes'] if id in scene['capture_refs'] for label in scene['required_labels']))
        image_path, dom_path = BASE / 'images' / (id + '.jpg'), BASE / 'dom' / (id + '.dom.txt')
        files[image_path], files[dom_path] = (S / row['file']).read_bytes(), (S / row['dom_file']).read_bytes()
        row.update(file=str(image_path), dom_file=str(dom_path), visible_labels=labels,
                   visible_controls=[], visible_field_text=[], required_labels=labels,
                   missing_required_labels=[], visual_review='completed_actual_image_review',
                   eligible_for_lesson=True, publication_eligible=True, accepted=True,
                   review_status='accepted_bounded_source', raw_source=source,
                   label_observation_method='Root personally read the listed teaching labels in each complete actual AX screenshot. Raw DOM extraction misses some painted labels after scrolling; it is not used to manufacture pixel evidence. Unused/clipped content is excluded.',
                   capture_review={'passed': True, 'reviewer': 'Codex /root', 'reviewed_at': at,
                                   'sha256': digest, 'application_visible': True, 'no_errors': True,
                                   'controls_reviewed': True, 'controls_fully_visible': True,
                                   'controls_unobstructed': True,
                                   'method': 'Actual full screenshot personally viewed during recording; only listed fully visible teaching text and controls accepted. Source review only.'})
        rows.append(row)
    narration = '\n\n'.join(scene['narration'] for scene in lesson['scenes']) + '\n'
    manifest = {'app': 'Core', 'source_manifest': str(RAW / 'manifest.json'),
                'source_manifest_sha256': MANIFEST_SHA, 'reviewer': 'Codex /root', 'reviewed_at': at,
                'actual_raw_images_personally_viewed': 11, 'accepted_actual_images': 11, 'screenshots': rows}
    files[BASE / 'captures.reviewed.json'] = encoded(manifest)
    files[BASE / 'narration.txt'] = narration.encode()
    files[BASE / 'source-review.json'] = encoded({
        'created_at': at, 'reviewer': 'Codex /root', 'lesson_sha256': LESSON_SHA,
        'capture_manifest_sha256': hashlib.sha256(encoded(manifest)).hexdigest(),
        'script_sha256': hashlib.sha256(narration.encode()).hexdigest(),
        'words': len(narration.split()), 'scenes': 13, 'actual_source_images': 11,
        'source_images_reviewed': True, 'export_ready': False,
        'scope': 'Read-only Executive summary and Workload exercise. Applied Training and Engine51 filters, read actual results, restored broader filters. Distinct administrator transition/current-queue scopes were verified in source and actual results.',
        'excluded_primary_images': ['001-summary-filters (redundant)', '011-workload-month-definition (headings clipped)'],
        'remaining': ['Generate and verify exact natural narration.', 'Authorized private export, complete audio checks and genuine listening review.',
                      'Actual cue timing, encoded-frame/caption review and advancing browser playback qualification.']})
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
                      'app_mutations': 0, 'final_media_approval_generated': False,
                      'canonical_or_site_changes': 0, 'git_mutations': 0}))
