"""Read-only verification of the installed native Unit candidate archive.

Only the copied candidate and its existing Root source-review receipt are read.
Original recordings, public projections, host paths and the historical generator
are provenance references, never file dependencies. The old generator's --build
still requires its original source archive. This checker does not regenerate,
review pixels, approve speech, render, qualify or publish anything.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import struct


ROOT = Path(__file__).resolve().parents[2]
BASE = PurePosixPath('expansion/plans/app-unit-call-lifecycle-native-candidate-20261030')
FREEZE_SHA256 = 'f3b3ffb533e9b73a1508aa3fe3c473aebb63a117c58caec688356e53d8376c15'
REVIEW = PurePosixPath('expansion/plans/app-unit-call-lifecycle-native-root-source-review-20261030.json')
REVIEW_SHA256 = 'c0ec07512aff508128e9cb699ebb86b27efa2a5ee1290a33072edf905245bffa'
EXPECTED = {'scene_count': 15, 'sentence_count': 59, 'images': 23, 'words': 835}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def relative(value):
    require(isinstance(value, str) and value and '\\' not in value,
            'Use a canonical source-relative POSIX path.')
    path = PurePosixPath(value)
    require(path.parts and not path.is_absolute() and '..' not in path.parts
            and path.as_posix() == value and ':' not in value,
            'Unsafe source-relative path.')
    return path


def safe_file(sources, value, candidate_only=True):
    """Reject escapes and every symlink before any file content is opened."""
    path = relative(value)
    require(not candidate_only or path.is_relative_to(BASE),
            'Archive reference leaves the self-contained candidate.')
    sources = Path(sources)
    require(sources.is_dir() and not sources.is_symlink(),
            'Sources root must be an existing real directory.')
    target = sources
    for part in path.parts:
        target /= part
        require(not target.is_symlink(), 'Symlinked archive path is not allowed.')
    require(target.resolve().is_relative_to(sources.resolve()), 'Archive path escapes sources.')
    require(target.is_file(), 'Required archived file is missing: ' + value)
    return target


def checked_bytes(sources, value, sha256=None, candidate_only=True):
    body = safe_file(sources, value, candidate_only).read_bytes()
    require(sha256 is None or digest(body) == sha256, 'Changed archived file: ' + value)
    return body


def tree_membership(sources, declared):
    """List the bounded copied tree without following a directory symlink."""
    candidate = safe_file(sources, str(BASE / 'source-freeze.json')).parent
    actual = set()
    for directory, folders, files in os.walk(candidate, followlinks=False):
        for name in folders + files:
            entry = Path(directory) / name
            require(not entry.is_symlink(), 'Symlinked archive path is not allowed.')
        for name in files:
            entry = Path(directory) / name
            require(entry.is_file(), 'Non-file archive entry is not allowed.')
            actual.add(entry.relative_to(sources).as_posix())
    require(actual == declared | {str(BASE / 'source-freeze.json')},
            'Copied archive has undeclared or missing files.')


def json_bytes(body):
    try:
        return json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError('Invalid archived JSON.') from error


def png_geometry(body):
    require(len(body) >= 33 and body[:8] == b'\x89PNG\r\n\x1a\n'
            and body[8:16] == b'\x00\x00\x00\rIHDR', 'Archived image is not a PNG with IHDR.')
    width, height = struct.unpack('>II', body[16:24])
    require((width, height) == (2732, 2048), 'Native PNG geometry differs from the retained capture.')
    return width, height


def continuity(lesson, mapping, narration, captures):
    """Check exact words/order, labels and control identities without timing guesses."""
    scenes, sentences, images = lesson['scenes'], mapping['sentences'], captures['native_sources']
    require(len(scenes) == 15 and len(sentences) == 59 and len(images) == 23,
            'Expected exactly 15 paragraphs, 59 untimed sentences and 23 native images.')
    require(lesson['id'] == mapping['lesson_id'] == 'app-unit-call-lifecycle-native'
            and lesson['app'] == 'Unit', 'Wrong native lesson identity.')
    require([scene['id'] for scene in scenes] == [str(i).zfill(2) for i in range(1, 16)],
            'Scene order or identity differs.')
    require(lesson.get('export_ready') is False
            and mapping.get('human_listening_claim') is False
            and mapping.get('rendered_or_publishable') is False
            and mapping.get('all_timing_from_future_actual_speech_required') is True,
            'A source archive cannot supply audio, timing or publication approval.')
    require(captures.get('source_only') is True and captures.get('publication_approved') is False,
            'Native capture archive qualification state changed.')
    by_id = {image['id']: image for image in images}
    require(len(by_id) == len(images), 'Duplicate native capture identity.')
    expected_sentence_order, used = [], set()
    for scene in scenes:
        rows = [row for row in sentences if row['scene_id'] == scene['id']]
        require(rows and ' '.join(row['text'] for row in rows) == scene['narration'],
                'Sentence continuity differs from exact scene narration.')
        require([row['sentence_id'] for row in rows]
                == [scene['id'] + '-' + str(i).zfill(2) for i in range(1, len(rows) + 1)],
                'Sentence identity or order differs.')
        labels = list(dict.fromkeys(label for row in rows for label in row['required_labels']))
        require(labels == scene['required_labels'], 'Scene label union differs from its sentence map.')
        for row in rows:
            require(isinstance(row['text'], str) and row['text'].strip()
                    and row.get('speech_timing') is None, 'Empty sentence or invented source timing.')
            require(row['capture_id'] in by_id, 'Sentence references an absent native image.')
            image = by_id[row['capture_id']]
            require(row['image_sha256'] == image['sha256'], 'Sentence references another image revision.')
            require(all(label in image['manual_visible_labels'] for label in row['required_labels']),
                    'Sentence names an undeclared visible label.')
            control = row.get('native_control')
            require(control is None or any(control in (item.get('identifier'), item.get('accessible_label'))
                    for item in image['reviewed_native_controls']), 'Native icon has no retained control observation.')
            expected_sentence_order.extend([row['sentence_id']])
            used.add(image['id'])
    require(expected_sentence_order == [row['sentence_id'] for row in sentences],
            'The full sentence map is interleaved, reordered or has an unknown scene.')
    require(used == set(by_id), 'Every archived native image must belong to the actual sentence map.')
    expected_narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    require(narration == expected_narration and len(narration.strip().split('\n\n')) == 15,
            'Narration file differs from the 15 exact scene paragraphs.')
    require(len(' '.join(scene['narration'] for scene in scenes).split()) == 835,
            'Exact 835-word narration count differs.')
    return by_id


def verify(sources=ROOT / 'sources'):
    sources = Path(sources)
    freeze_body = checked_bytes(sources, str(BASE / 'source-freeze.json'), FREEZE_SHA256)
    freeze = json_bytes(freeze_body)
    require(all(freeze[key] == value for key, value in EXPECTED.items()), 'Frozen archive scope differs.')
    require(len(freeze['files']) == 55, 'Frozen candidate must contain its 55 declared assets.')
    bodies, names = {}, set()
    for row in freeze['files']:
        name = row['file']
        require(name not in names, 'Duplicate frozen asset path.')
        names.add(name)
        body = checked_bytes(sources, name, row['sha256'])
        require(len(body) == row['bytes'], 'Archived byte size differs: ' + name)
        bodies[name] = body
    tree_membership(sources, names)
    lesson = json_bytes(bodies[str(BASE / 'lesson.candidate.json')])
    mapping = json_bytes(bodies[str(BASE / 'sentence-screen-map.untimed.json')])
    captures = json_bytes(bodies[str(BASE / 'captures.native-reviewed.json')])
    narration = bodies[str(BASE / 'narration.txt')].decode('utf-8')
    by_id = continuity(lesson, mapping, narration, captures)
    require(digest(bodies[str(BASE / 'lesson.candidate.json')]) == freeze['lesson_sha256']
            and digest(bodies[str(BASE / 'narration.txt')]) == freeze['narration_sha256'],
            'Freeze source identity differs.')
    declared_images, declared_metadata = set(), set()
    for image in by_id.values():
        image_file, metadata_file = image['file'], image['metadata_file']
        require(relative(image_file).parent == BASE / 'images'
                and relative(metadata_file).parent == BASE / 'native-metadata',
                'Native assets leave their copied archive folders.')
        require(image_file in bodies and metadata_file in bodies, 'Native image/metadata is not a frozen local asset.')
        require(digest(bodies[image_file]) == image['sha256']
                and digest(bodies[metadata_file]) == image['metadata_sha256'], 'Native image/metadata identity differs.')
        require(png_geometry(bodies[image_file]) == (image['width'], image['height']), 'Native image declaration differs.')
        metadata = json_bytes(bodies[metadata_file])
        projected = metadata['original_metadata_projection']
        require(projected['file'] == image['original_file'] and projected['sha256'] == image['sha256']
                and projected['provenance'] == image['provenance']
                and (projected['width'], projected['height']) == (2732, 2048), 'Copied native metadata differs from its image.')
        elements = projected['native_accessibility_observation']['result']['elements']
        for control in image['reviewed_native_controls']:
            matches = [element for element in elements if
                (control.get('identifier') and element.get('identifier') == control['identifier'])
                or (control.get('accessible_label') and element.get('label') == control['accessible_label'])]
            require(len(matches) == 1, 'Native icon observation is not unique in copied metadata.')
            native = matches[0]
            require(control['native_type'] == native['type']
                    and control['rect_points'] == native['rect_points']
                    and control.get('hittable') == native.get('hittable'), 'Native control observation was strengthened or changed.')
        declared_images.add(image_file)
        declared_metadata.add(metadata_file)
    require(len(declared_images) == len(declared_metadata) == 23
            and declared_images == {name for name in names if relative(name).parent == BASE / 'images'}
            and declared_metadata == {name for name in names if relative(name).parent == BASE / 'native-metadata'},
            'Copied PNG/metadata membership differs from the 23 declared capture pairs.')
    review = json_bytes(checked_bytes(sources, str(REVIEW), REVIEW_SHA256, candidate_only=False))
    require(review['reviewer'] == 'Root' and review['full_script_approved_for_narration'] is True
            and review['lesson_sha256'] == freeze['lesson_sha256']
            and review['narration_sha256'] == freeze['narration_sha256']
            and review['sentence_screen_map_sha256'] == digest(bodies[str(BASE / 'sentence-screen-map.untimed.json')])
            and (review['words'], review['paragraphs'], review['untimed_sentences'], review['actual_native_images_viewed'])
                == (835, 15, 59, 23)
            and review['human_listening_claim'] is False and review['rendered_or_publishable'] is False,
            'Existing Root review does not bind this source archive.')
    require(len(review['images']) == 23
            and {(row['id'], row['file'], row['sha256']) for row in review['images']}
            == {(row['id'], row['file'], row['sha256']) for row in by_id.values()}
            and all(row['accepted_for_script_correspondence'] is True for row in review['images']),
            'Existing Root image review membership differs.')
    return {'self_contained_archive_verified': True, 'frozen_assets_checked': 55,
            'unchanged_native_pngs_checked': 23, 'copied_native_metadata_checked': 23,
            'paragraphs': 15, 'untimed_sentences': 59, 'exact_words': 835,
            'source_freeze_sha256': FREEZE_SHA256, 'existing_Root_source_review_sha256': REVIEW_SHA256,
            'read_only': True, 'historical_source_paths_followed': False,
            'historical_build_requires_original_archive': True,
            'new_pixel_review_or_human_listening_or_publication_claim': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources-root', type=Path, default=ROOT / 'sources',
                        help='Installed sources directory containing only the retained candidate and Root receipt if desired.')
    args = parser.parse_args()
    print(json.dumps(verify(args.sources_root), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, UnicodeDecodeError) as error:
        raise SystemExit('Native Unit archive check stopped: ' + str(error)) from error
