"""Reproduce the fixed, hash-bound review of the actual Unit response images.

Does not renew a visual review, change raw captures, approve narration or publish.
The native confirmation and faint navigation captions remain explicit gaps.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
FOLDER = Path('captures/expansion/unit-response-recapture-20261028')
REVIEWED_AT = '2026-10-28T05:38:32+00:00'
# Exact stored JPEGs inspected at original size during this review.
SPECS = [
('001', 'd7cdf343c8f3983097330538060142d453a5bb4da721b9a6da16587aa3f8e2c4', ['Calls', 'Engine 51', 'Released', 'No Active Call'], 'Lower-right plus glyph visible. It has no accessible name; do not invent a literal New Call label.'),
('002', '3cc6a3bc3fba78b2c5449b3573e6496554a93c526682fe7b9505fe3d891f627f', ['New Call', 'Create New Call', 'Name', 'Nature', 'Priority', 'Routine', 'Type', 'Investigation', 'Note'], 'Readable Light-theme form. Routine and Investigation are painted field values confirmed by the stored DOM.'),
('003', '536b15389064e4ffb30befb3701105f4562efd3b4a59697fd8e707f853cace9c', ['Call Location', 'Address', 'GPS Coordinates', 'what3words', 'Plus Code', 'Destination POI', 'No destination selected'], 'Supplied fictional address and coordinates; no lookup or routing result demonstrated.'),
('004', '1564faadd555572e852eb7d22880bb6781552721160082e3a4c7142b96df57f6', ['Select Dispatch Recipients', 'Everyone', 'Wallace Boden', '1 selected', 'Confirm'], 'Foreground picker only. Boden visibly checked, Everyone unchecked; dimmed form excluded.'),
('005', 'e1d5f22d82629798e6f33836fb670ac27da016efb802217a2d344981f9e67fac', ['External ID', 'ACADEMY-UNIT-SELECTION-20261028', 'Dispatch Time', 'Dispatch To', '1 selected', 'Create'], 'Blank unscheduled Dispatch Time and final Create control are visible.'),
('006', 'e140d72425a4c1e103219e1f90263985e32cc16ba9b1efcc69cc9aa123a0344b', ['Call Details', 'TRAINING ONLY - Unit selection and response (FD51-2026-0006)', 'Set Active', 'Priority', 'Routine', 'Type', 'Investigation'], 'Set Active and incident identity readable. Faint detail tabs and iframe text are deliberately excluded.'),
('007', '18fa192c4aff8249edfcc23082bbcef974caa64d0c9385ebc590bc7ccd6961d9', ['Step 1 of 3', 'Select Status', 'Responding', 'Available', 'Committed', 'On Scene', 'Next'], 'Responding visibly selected; no development-warning overlay.'),
('008', '7b3628fda5748e3e4e75ab2af64eab300d73f945e6918a51cce9d3e9da4e2b01', ['Select Destination for Responding', 'Calls', 'Stations', 'POIs', 'No Destination', 'FD51-2026-0006 - TRAINING ONLY - Unit selection and response', 'Next'], 'Own exercise visibly selected with blue border and check mark.'),
('009', 'e75909cbc577c27a55290ddfe0c4fb7b8627d25c31f3ae74a5cfcce36385d78a', ['Add Note', 'Note (optional):', 'Responding · FD51-2026-0006 - TRAINING ONLY - Unit selection and response', 'Submit'], 'Foreground note and summary are readable.'),
('010', 'f7671ebf2f539298d1d4740b52d31d78b652e41013a2e7084507b208d19f34ce', ['Engine 51', 'Responding', '#FD51-2026-0006'], 'Saved unit identity, status and selected call are simultaneously visible.'),
('011', '8d37da1220fdae813d8dfdc4d7676871b78bda3d49eb46bf081edb83bc45edbb', ['Step 1 of 2', 'Select Destination for On Scene', 'Calls', 'FD51-2026-0006 - TRAINING ONLY - Unit selection and response', 'Next'], 'Two-step destination flow; own exercise selected.'),
('012', '5d122e9df005b34fe95b46cca2aa1a1708bcf8129684ab8492596ddbfd21e49e', ['Add Note', 'On Scene · FD51-2026-0006 - TRAINING ONLY - Unit selection and response', 'Submit'], 'Simulation note and final submission control readable.'),
('014', '0bd67020bd9eeb83fc6a9091d585ca26263e491fa27d00ecd7373fc487296a54', ['TRAINING ONLY - Unit selection and response (FD51-2026-0006)', 'Responding', 'On Scene', 'Engine 51 - Firehouse 51'], 'Saved events, timestamps and notes readable; faint Activity navigation label excluded.'),
('015', 'e55d13d99a5b32b6be88f50bd72867a9315544cc3b359c4b0481bba84cc3813e', ['Close Call'], 'Foreground Close Call action only. Faint Edit Call and all dimmed background content excluded.'),
('016', '219513a65044422a1655788147ca58df5d67b7d144a80d73aa9bb69180409fa4', ['Close Call', 'Close Type', 'Closed', 'Close Note', 'Notify everyone on the call'], 'Close note and final Close Call button fully visible; notification switch visibly off.'),
('017', '7627767f9c92c3fca25a2452ab647eaf0c92656c2b00a7e3a64082674b37cfb6', ['Calls', 'Engine 51', 'On Scene', '#FD51-2026-0006', '#DEMO-0001', '#DEMO-0002', '#DEMO-0003'], 'Own call absent from main active list but remains selected in sidebar. This is not Released or No Active Call evidence.')]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review():
    raw = json.loads((SOURCES / FOLDER / 'manifest.json').read_text())
    selected = []
    for prefix, image_sha, labels, note in SPECS:
        matches = [r for r in raw if r['id'].startswith(prefix + '-')]
        assert len(matches) == 1
        row = dict(matches[0])
        assert row['sha256'] == image_sha == sha(SOURCES / row['file'])
        dom = FOLDER / (row['id'] + '.dom.txt')
        if prefix == '001':
            assert sha(SOURCES/dom) == 'fcceeea734c47caafe613df3b02d13a307e1c36f8f8424890bfde5088220d012'
        if row.get('dom_sha256'):
            assert row['dom_sha256'] == sha(SOURCES / dom)
        row['dom_file'], row['dom_sha256'] = str(dom), sha(SOURCES / dom)
        row['visible_labels'] = labels
        row['visible_field_text'] = [f for f in row.get('visible_field_text', [])
                                     if f.get('value') != 'on']
        row['eligible_for_lesson'] = True
        row['capture_review'] = {'passed': True,
            'reviewer': 'Codex original-size exact stored JPEG inspection',
            'reviewed_at': REVIEWED_AT, 'sha256': image_sha,
            'application_visible': True, 'labels_legible': True,
            'no_errors': True, 'scope': note}
        selected.append(row)
    rejected = next(r for r in raw if r['id'].startswith('013-'))
    assert sha(SOURCES/rejected['file']) == 'a8f53dcf76b2564ded92a1782cc06385cfe7915b92530314096ea909de39a9cf'
    report = {'app': 'Unit', 'source_manifest': str(FOLDER/'manifest.json'),
        'reviewed_at': REVIEWED_AT, 'screenshots': selected,
        'excluded_images': [{'id': rejected['id'], 'sha256': rejected['sha256'],
            'reason': 'Unit identity and saved status header are scrolled out of view. Do not claim simultaneous unit/status/call readback.'}],
        'capture_gaps': ['Readable Activity tab entry before saved-history view.',
            'Native Deselect Active Call confirmation screenshot; browser tool observed AX text but cannot capture its pixels.',
            'Settled final unit status/selection after confirmation; current tool session stalled.'],
        'publication_approved': False, 'narration_approved': False}
    output = SOURCES / FOLDER / 'review/reviewed-source-subset-20261028.json'
    output.parent.mkdir(exist_ok=True)
    if output.exists():
        assert json.loads(output.read_text()) == report, 'Review changed; preserve previous review and create a new version.'
    else:
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(json.dumps({'reviewed_images': len(selected), 'excluded_images': 1,
        'capture_gaps': len(report['capture_gaps']), 'publication_approved': False}))


if __name__ == '__main__':
    review()
