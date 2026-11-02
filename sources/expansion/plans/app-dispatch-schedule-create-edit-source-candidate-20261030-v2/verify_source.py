#!/usr/bin/env python3
"""Read-only integrity/continuity check of this installed source archive only.

This cannot establish narration quality, new visual review or video readiness.
It deliberately never follows original host capture or external source paths.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

INVENTORY_SHA256 = '5c48c1c35566c84fba22a020f4ec7134d1ef722d32c2847eeb09356a8b207421'
COUNTS = {'accepted_images': 9, 'archival_supporting_images': 1, 'paragraphs': 12, 'untimed_spans': 13, 'words': 677, 'sentences': 49}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_file(root, name):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('Invalid relative archive file')
    rel = Path(name)
    if rel.is_absolute() or any(part in ('.', '..') for part in rel.parts):
        raise ValueError('Archive path must remain local')
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Archive symlinks are forbidden')
    if not current.is_file() or not current.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or escaped archive file')
    return current


def jpeg_dimensions(data):
    if not data.startswith(b'\xff\xd8'):
        raise ValueError('Expected an actual JPEG')
    at = 2
    while at < len(data):
        if data[at] != 255:
            raise ValueError('Malformed JPEG segment')
        while data[at] == 255:
            at += 1
        marker = data[at]
        at += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        size = struct.unpack('>H', data[at:at + 2])[0]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack('>HH', data[at + 3:at + 7])
            return width, height
        if size < 2:
            raise ValueError('Malformed JPEG segment length')
        at += size
    raise ValueError('No JPEG frame dimensions')


def verify(root):
    root = Path(root).resolve()
    inventory_bytes = safe_file(root, 'inventory.json').read_bytes()
    if digest(inventory_bytes) != INVENTORY_SHA256:
        raise ValueError('Frozen inventory mismatch')
    inventory = json.loads(inventory_bytes)
    if inventory['counts'] != COUNTS:
        raise ValueError('Frozen source counts changed')
    seen = set()
    for item in inventory['files']:
        if item['file'] in seen:
            raise ValueError('Duplicate inventory entry')
        seen.add(item['file'])
        if digest(safe_file(root, item['file']).read_bytes()) != item['sha256']:
            raise ValueError('Frozen archive asset hash mismatch: ' + item['file'])
    load = lambda name: json.loads(safe_file(root, name).read_text())
    shots = load('captures.reviewed.json')['screenshots']
    lesson = load('lesson.source-candidate.json')
    sequence = load('screen-sequence.untimed.json')
    review = load('source-review.json')
    by_id = {item['id']: item for item in shots}
    if len(by_id) != 9 or [item['id'][:3] for item in shots] != [f'{n:03}' for n in range(4, 13)]:
        raise ValueError('Exact reviewed source subset changed')
    if any(item['app'] != 'Dispatch' for item in shots):
        raise ValueError('Every operational source must be the primary Dispatch application')
    if review['original_images_personally_viewed'] != 13 or review['accepted_image_count'] != 9:
        raise ValueError('Recorded review scope changed')
    if any(item['eligible_for_lesson'] is not False for item in review['excluded_diagnostics']):
        raise ValueError('AX-only diagnostics cannot become lesson evidence')
    for item in shots:
        if item['file'] not in seen or item['dom_file'] not in seen:
            raise ValueError('Unfrozen capture or DOM')
        data = safe_file(root, item['file']).read_bytes()
        if digest(data) != item['sha256'] or jpeg_dimensions(data) != (item['width'], item['height']):
            raise ValueError('Capture bytes/dimensions changed')
        if digest(safe_file(root, item['dom_file']).read_bytes()) != item['dom_sha256']:
            raise ValueError('Complete DOM snapshot changed')
        record = item['capture_review']
        captured = datetime.fromisoformat(item['provenance']['captured_at'].replace('Z', '+00:00'))
        reviewed = datetime.fromisoformat(record['reviewed_at'].replace('Z', '+00:00'))
        if not captured <= reviewed <= datetime.now(timezone.utc):
            raise ValueError('Invalid recorded capture/review order')
        if record['passed'] is not True or record['sha256'] != item['sha256'] or item['eligible_for_lesson'] is not True:
            raise ValueError('Actual bounded image review missing')
        if item['visible_controls'] != []:
            raise ValueError('No new icon observations were reviewed')
    supporting = load('supporting-archive.json')['screenshots']
    if len(supporting) != 1:
        raise ValueError('Expected one archived supporting image')
    for item in supporting:
        if item['id'] != '013-core-department-time-zone' or item['app'] != 'Core' or item['eligible_for_lesson'] is not False or item['operational_input'] is not False or item['id'] in by_id:
            raise ValueError('Supporting Core image cannot become a Dispatch operational source')
        if item['file'] not in seen or item['dom_file'] not in seen:
            raise ValueError('Unfrozen supporting archive asset')
        data = safe_file(root, item['file']).read_bytes()
        if digest(data) != item['sha256'] or jpeg_dimensions(data) != (647, 722):
            raise ValueError('Supporting archive image changed')
        if digest(safe_file(root, item['dom_file']).read_bytes()) != item['dom_sha256']:
            raise ValueError('Supporting archive DOM changed')
    paragraphs = [item['narration'] for item in lesson['scenes']]
    if safe_file(root, 'narration.txt').read_text() != '\n\n'.join(paragraphs) + '\n':
        raise ValueError('Narration text differs from exact scene paragraphs')
    expected_scenes = [item['id'] for item in lesson['scenes']]
    if [item['scene_id'] for item in sequence['scenes']] != expected_scenes:
        raise ValueError('Scene order changed')
    flat = [span for scene in sequence['scenes'] for span in scene['screens']]
    if flat != sequence['source_spans']:
        raise ValueError('Flattened source correspondence differs')
    word_at = 0
    sentences = 0
    for scene, paragraph in zip(sequence['scenes'], paragraphs):
        if ' '.join(span['text'] for span in scene['screens']) != paragraph:
            raise ValueError('A scene loses or adds narration text')
        for span in scene['screens']:
            shot = by_id[span['capture_id']]
            words = span['text'].split()
            if span['scene_id'] != scene['scene_id'] or span['word_start'] != word_at or span['word_end_exclusive'] != word_at + len(words):
                raise ValueError('Noncontiguous source/narration word range')
            if span['image_sha256'] != shot['sha256'] or span['dom_sha256'] != shot['dom_sha256']:
                raise ValueError('Source span points to changed capture evidence')
            if not span['required_labels'] or not set(span['required_labels']) <= set(shot['visible_labels']):
                raise ValueError('Unseen required source label')
            word_at += len(words)
            sentences += len([s for s in re.split(r'(?<=[.!?])\s+', span['text']) if s.strip()])
    actual = {'accepted_images': len(shots), 'archival_supporting_images': len(supporting), 'paragraphs': len(paragraphs), 'untimed_spans': len(flat), 'words': word_at, 'sentences': sentences}
    if actual != COUNTS or sequence['word_count'] != word_at or sequence['sentence_count'] != sentences:
        raise ValueError('Exact source continuity counts changed')
    if lesson['parent_full_script_review'] != 'pending' or lesson['source_only'] is not True:
        raise ValueError('Source package cannot create a production approval')
    return {'passed': True, 'kind': 'Installed archival source integrity only', **actual, 'verified_inventory_files': len(seen), 'external_original_paths_read': 0, 'full_script_parent_review': 'pending'}


if __name__ == '__main__':
    try:
        print(json.dumps(verify(Path(__file__).parent), indent=2))
    except (OSError, KeyError, TypeError, ValueError, IndexError, struct.error) as exc:
        raise SystemExit('Source archive check failed: ' + str(exc))
