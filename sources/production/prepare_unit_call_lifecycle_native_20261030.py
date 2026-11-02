"""Retain a new bounded native Unit call lesson candidate; never renders or publishes.

Default is a read-only verification of the new candidate. --build is new-only.
Original images/public projections/canonical lessons remain unchanged. No app,
database, credentials, audio-generation or Git operation is performed.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
BASE = Path('expansion/plans/app-unit-call-lifecycle-native-candidate-20261030')
PROJECTION = Path('expansion/plans/unit-native-call-public-source-projection-20261029')
PINNED = {
    'native-captures.public.json': 'bedba95fd5e88993815ae4344a934722e4580ef7ed50706736de6e6260b1d430',
    'native-context.public.json': 'b6647b52957c284f7ccec941317290c502c45662501bdbe282b1191e5ac1c77c',
    'core-corroboration.public.json': '158888b43789e94511c1b3650694d55e2489a7e11eaa0a8467ccad3cc5f1835e',
    'projection-audit.json': None,
}

# Labels below were manually inspected in the actual returned images by this
# recorder. They are not an OCR or complete accessibility-tree transcription.
LABELS = {
    17: ['Calls', 'Ambulance 61', 'Firehouse 51', '0 of 1 Roles', 'No Active Call', 'Search calls...'],
    43: ['Select Dispatch Recipients', 'Units (8)', 'Ambulance 61', 'Engine 51', 'Truck 81', 'Squad 3', '2 selected', 'Confirm', 'Cancel'],
    44: ['Select Dispatch Recipients', 'Everyone', 'Users (14)', 'Wallace Boden', '2 selected', 'Confirm', 'Cancel'],
    47: ['New Call', 'Create New Call', 'Name*', 'Nature*', 'Priority*', 'Routine', 'Type*', 'Investigation', 'Note'],
    48: ['New Call', 'Call Location', 'Address', 'GPS Coordinates', 'what3words', 'Plus Code', 'Select Location on Map', 'Destination POI', 'No destination selected', 'Contact Name', 'Contact Info', 'External ID', 'Incident ID'],
    49: ['New Call', 'Dispatch Time', 'Dispatch To', '2 selected', 'Cancel', 'Create'],
    51: ['Calls', 'TRAINING ONLY - Native Unit response and deselection', 'Wallace Boden', 'Ambulance 61', 'No Active Call'],
    62: ['Call Details', 'TRAINING ONLY - Native Unit response and deselection (FD51-2026-0008)', 'Set Active', 'Info', 'Priority', 'Routine', 'Type', 'Investigation', 'Note'],
    63: ['Call set as active', 'Select Status', 'Responding', 'Available', 'Committed', 'On Scene', 'Staging', 'Returning', 'Out of Service', 'Cancel', 'Next'],
    64: ['Step 1 of 3', 'Select Status', 'Responding', 'Available', 'Committed', 'On Scene', 'Staging', 'Returning', 'Out of Service', 'Cancel', 'Next'],
    65: ['Step 2 of 3', 'Select Destination for Responding', 'No Destination', 'Calls', 'Stations', 'POIs', 'FD51-2026-0008 - TRAINING ONLY - Native Unit response and deselection', 'Previous', 'Next'],
    68: ['Step 3 of 3', 'Add Note', 'Note (optional):', 'Responding · FD51-2026-0008 - TRAINING ONLY - Native Unit response and deselection', 'TRAINING ONLY - Native status workflow software exercise; no physical response.', 'Previous', 'Submit'],
    69: ['Call Details', 'Status saved successfully!', 'Info', 'Priority', 'Routine', 'Type', 'Investigation'],
    70: ['Calls', 'Ambulance 61', 'Responding', '0 of 1 Roles', '#FD51-2026-0008', 'TRAINING ONLY - Native Unit response and deselection'],
    71: ['Deselect Active Call', 'Are you sure you want to deselect the current active call?', 'Cancel', 'Confirm'],
    72: ['Calls', 'Ambulance 61', 'Responding', 'No Active Call', '#FD51-2026-0008', 'TRAINING ONLY - Native Unit response and deselection'],
    73: ['Call Details', 'TRAINING ONLY - Native Unit response and deselection (FD51-2026-0008)', 'Set Active', 'Info', 'Routine', 'Investigation'],
    74: ['Call Details', 'Edit Call', 'Close Call'],
    75: ['Close Call', 'Close Type', 'Select close type', 'Close Note', 'Notify everyone on the call', 'Cancel'],
    76: ['Closed', 'Cancelled', 'Unfounded', 'Founded', 'Minor', 'Transferred', 'False Alarm'],
    78: ['Close Call', 'Close Type', 'Closed', 'Close Note', 'TRAINING ONLY - Software workflow complete; no real incident or physical response.', 'Notify everyone on the call', 'Cancel'],
    79: ['Calls', 'Call closed successfully', 'No Active Call', 'Responding', '#DEMO-0003', '#DEMO-0002', '#DEMO-0001'],
    81: ['Calls', 'Ambulance 61', 'Released', '0 of 1 Roles', 'No Active Call', '#DEMO-0003', '#DEMO-0002', '#DEMO-0001'],
}

# Each sentence has one explicitly selected actual native image. The entries are
# deliberately untimed; an actual generated transcript must supply all timings.
SCENES = [
    ('01', 'Confirm the unit and open a new call', [
        (17, 'The Unit app keeps a vehicle or operational team in view while you work its calls.', ['Calls', 'Ambulance 61']),
        (17, 'Here, the Calls screen shows Ambulance Sixty-one and No Active Call.', ['Calls', 'No Active Call']),
        (17, 'The roles card reads zero of one, so this recording does not establish a staffed crew.', ['0 of 1 Roles']),
        (17, 'Use the circular plus button at the lower right to open a new call when your department permits you to create one.', [], 'new-call-fab'),
    ]),
    ('02', 'Give the call a useful identity', [
        (47, 'In New Call, enter a clear Name and a useful Nature description.', ['New Call']),
        (47, 'Our example is explicitly labeled training only and describes a software exercise.', ['Create New Call']),
        (47, 'Review Priority and Type; this practice call uses Routine and Investigation.', ['Routine', 'Investigation']),
        (47, 'Use Note for additional context that belongs with the call.', ['Note']),
        (47, 'Choose names and classifications that make sense to your own operation rather than copying a firehouse example into live work.', ['Routine', 'Investigation']),
    ]),
    ('03', 'Review location inputs', [
        (48, 'Call Location provides Address, GPS Coordinates, what3words and Plus Code fields, along with Select Location on Map.', ['Call Location', 'Address', 'GPS Coordinates', 'what3words', 'Plus Code', 'Select Location on Map']),
        (48, 'Destination POI is a separate choice and currently reads No destination selected.', ['Destination POI', 'No destination selected']),
        (48, 'This software-only exercise leaves the location and contact inputs empty; a real assignment needs the location information required by your operating procedure.', ['Call Location', 'Contact Name', 'Contact Info']),
        (48, 'A visible location field does not establish that a device has supplied GPS coordinates or that an address lookup has succeeded.', ['GPS Coordinates', 'Address']),
    ]),
    ('04', 'Check the actual dispatch audience', [
        (44, 'In Select Dispatch Recipients, review individual users as well as the broad Everyone option.', ['Select Dispatch Recipients', 'Everyone']),
        (44, 'Wallace Boden is checked here, while Everyone remains unchecked.', ['Wallace Boden', 'Everyone']),
        (43, 'In the Units section, Ambulance Sixty-one is also selected, bringing this exercise to two selected recipients.', ['Units (8)', 'Ambulance 61', '2 selected']),
        (43, 'Confirm retains that reviewed audience; it does not demonstrate that a recipient has received a notification.', ['Confirm']),
    ]),
    ('05', 'Create once and inspect the returned call', [
        (49, 'Back on New Call, verify Dispatch To and its two selected recipients.', ['New Call', 'Dispatch To', '2 selected']),
        (49, 'Dispatch Time is blank in this exercise; no future schedule is entered.', ['Dispatch Time']),
        (49, 'After reviewing the form, use Create once.', ['Create']),
        (51, 'The Calls list now contains the new training exercise with Boden and Ambulance Sixty-one shown on its card.', ['Calls', 'Wallace Boden', 'Ambulance 61']),
    ]),
    ('06', 'Read details before selecting the call', [
        (62, 'Open the training call and check its identity in Call Details.', ['Call Details']),
        (62, 'This saved exercise has a department call number ending in eight, and its Info view retains Routine, Investigation and the original note.', ['Info', 'Routine', 'Investigation', 'Note']),
        (62, 'Choose Set Active for the incident you intend to work.', ['Set Active']),
        (63, 'The app reports Call set as active and opens Select Status.', ['Call set as active', 'Select Status']),
    ]),
    ('07', 'Choose the intended response status', [
        (64, 'Select Status is the first of three steps.', ['Select Status', 'Step 1 of 3']),
        (64, 'The configured choices include Responding, Available, Committed, On Scene, Staging, Returning and Out of Service.', ['Responding', 'Available', 'Committed', 'On Scene', 'Staging', 'Returning', 'Out of Service']),
        (64, 'Here, Responding is selected; use Next to review its destination.', ['Responding', 'Next']),
    ]),
    ('08', 'Associate the update with the right destination', [
        (65, 'Select Destination for Responding distinguishes Calls, Stations and POIs from No Destination.', ['Select Destination for Responding', 'Calls', 'Stations', 'POIs', 'No Destination']),
        (65, 'The selected row is our new training incident, ending in eight.', ['FD51-2026-0008 - TRAINING ONLY - Native Unit response and deselection']),
        (65, 'Check that identity before using Next, so the status update is associated with the intended call.', ['Next']),
    ]),
    ('09', 'Review the note and submit the status', [
        (68, 'Add Note shows the selected Responding status and the training call together.', ['Add Note']),
        (68, 'The optional note makes clear that this is a software exercise.', ['Note (optional):']),
        (68, 'Review the summary, then use Submit to save the update.', ['Submit']),
        (69, 'Status saved successfully is the returned result from that submission.', ['Status saved successfully!']),
    ]),
    ('10', 'Read unit status and active selection separately', [
        (70, 'Back in Calls, the sidebar now shows Responding and the selected training call.', ['Calls', 'Responding', '#FD51-2026-0008']),
        (70, 'Keep the unit identity, its status and the active call in view when changing tasks.', ['Ambulance 61', 'Responding']),
        (70, 'The circle with an X below the active-call card is the Deselect control.', [], 'Deselect'),
    ]),
    ('11', 'Confirm deselection', [
        (71, 'Deselect Active Call asks whether to deselect the current active call.', ['Deselect Active Call', 'Are you sure you want to deselect the current active call?']),
        (71, 'Use Cancel to keep the selection or Confirm to clear it.', ['Cancel', 'Confirm']),
        (72, 'After Confirm, the sidebar reads No Active Call, while the incident remains in Calls and the unit still reads Responding.', ['No Active Call', 'Calls', 'Responding']),
        (72, 'Clearing your active selection and closing the department incident are separate operations.', ['No Active Call', '#FD51-2026-0008']),
    ]),
    ('12', 'Open the incident closeout action', [
        (73, 'Reopen the same training incident from Calls and confirm its title in Call Details.', ['Call Details']),
        (73, 'The three-dot menu at the upper right opens the available incident actions.', [], 'kebab-menu-button'),
        (74, 'Edit Call and Close Call are separate choices.', ['Edit Call', 'Close Call']),
        (74, 'Choose Close Call only when you have the authority and the incident is ready for closeout.', ['Close Call']),
    ]),
    ('13', 'Read closeout defaults before submitting', [
        (75, 'The Close Call sheet requires a Close Type and provides a Close Note.', ['Close Call', 'Close Type', 'Close Note']),
        (75, 'Notify everyone on the call is enabled in this recorded starting state.', ['Notify everyone on the call']),
        (75, 'Review that setting explicitly because the sheet describes alerting the dispatched personnel, groups, roles, units and command team.', ['Notify everyone on the call']),
        (76, 'Close Type offers Closed, Cancelled, Unfounded, Founded, Minor, Transferred and False Alarm.', ['Closed', 'Cancelled', 'Unfounded', 'Founded', 'Minor', 'Transferred', 'False Alarm']),
    ]),
    ('14', 'Finish the practice call deliberately', [
        (78, 'Our example selects Closed and enters a Close Note explaining that the software workflow is complete.', ['Closed', 'Close Note']),
        (78, 'Notify everyone on the call is off for this local exercise.', ['Notify everyone on the call']),
        (78, 'Check the call identity and closeout information, then use the green Close Call button once.', ['Close Call']),
        (79, 'The app returns Call closed successfully and shows No Active Call.', ['Call closed successfully', 'No Active Call']),
        (79, 'The three earlier training calls remain listed, and this immediate view still shows the cached Responding status.', ['Responding', '#DEMO-0003', '#DEMO-0002', '#DEMO-0001']),
    ]),
    ('15', 'Verify the final state and apply the workflow', [
        (81, 'A fresh app readback shows Released, No Active Call and the original three training incidents.', ['Released', 'No Active Call', '#DEMO-0003', '#DEMO-0002', '#DEMO-0001']),
        (81, 'Released is the observed final status here; it should not be described as an Available selection or evidence of physical readiness.', ['Released']),
        (81, 'Use these same identity, selection and closeout checks for a community paramedicine car, a mental health response team, a search and rescue vehicle, a security patrol, a wildland crew or an industrial response unit.', ['Calls']),
        (81, 'The names in this example are fictional training data; choose the statuses, audience and incident details that fit your department.', ['Calls']),
    ]),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def inputs():
    for name, digest in PINNED.items():
        path = S / PROJECTION / name
        if digest is not None and sha(path) != digest:
            raise ValueError('Changed reviewed source projection: ' + name)
    rows = json.loads((S / PROJECTION / 'native-captures.public.json').read_text())['captures']
    by_number = {int(Path(row['metadata']['file']).name[:3]): row for row in rows}
    for number in LABELS:
        row = by_number[number]
        metadata = row['metadata']
        if sha(S / metadata['file']) != metadata['sha256']:
            raise ValueError('Changed original native image: ' + str(number))
        if metadata['width'] != 2732 or metadata['height'] != 2048:
            raise ValueError('Native geometry changed.')
    return by_number


def create():
    by_number = inputs()
    destination = S / BASE
    if destination.exists() or destination.is_symlink():
        raise ValueError('New-only candidate preserves all existing outputs.')
    assets = {}
    images = []
    now = datetime.now(timezone.utc).isoformat()
    for number in sorted(LABELS):
        row = by_number[number]
        m = deepcopy(row['metadata'])
        original = Path(m['file'])
        image_rel = BASE / 'images' / original.name
        metadata_rel = BASE / 'native-metadata' / (original.stem + '.public.native.json')
        metadata = {'kind': 'unchanged_recorded_metadata_from_retained_public_projection',
            'original_metadata': row['original_metadata'],
            'projection_file': str(PROJECTION / 'native-captures.public.json'),
            'projection_sha256': PINNED['native-captures.public.json'],
            'original_metadata_projection': m}
        assets[metadata_rel.relative_to(BASE).as_posix()] = encoded(metadata)
        elements = m['native_accessibility_observation']['result']['elements']
        wanted = {item[3] for _, _, sentences in SCENES for item in sentences if item[0] == number and len(item) > 3}
        controls = []
        for literal in wanted:
            matches = [e for e in elements if e.get('label') == literal or e.get('identifier') == literal]
            if len(matches) != 1:
                raise ValueError('Native icon source identity is not unique: ' + str((number, literal)))
            e = matches[0]
            controls.append({'accessible_label': e.get('label', ''), 'identifier': e.get('identifier', ''),
                'native_type': e['type'], 'rect_points': e['rect_points'],
                'icon_only': True, 'reviewed_in_actual_image': True,
                'hittable': e.get('hittable'), 'hittability_claim': 'Only the actual recorded value is retained; null is not inferred true.'})
        images.append({'id': original.stem, 'file': image_rel.as_posix(), 'sha256': m['sha256'],
            'app': 'Unit', 'width': m['width'], 'height': m['height'],
            'metadata_file': metadata_rel.as_posix(), 'metadata_sha256': hashlib.sha256(assets[metadata_rel.relative_to(BASE).as_posix()]).hexdigest(),
            'captured_at': m['provenance']['captured_at'], 'provenance': m['provenance'],
            'original_file': original.as_posix(), 'geometry': {'application_points': {'x': 0, 'y': 0, 'width': 1366, 'height': 1024},
                'physical_pixels': {'width': 2732, 'height': 2048}, 'dpr': 2, 'orientation_observed': 3},
            'manual_visible_labels': LABELS[number], 'reviewed_native_controls': controls,
            'review_scope': 'native_source_only_reviewed', 'source_only': True, 'publication_approved': False,
            'capture_review': {'reviewer': 'Codex /root/remaining_responder_unit', 'reviewed_at': now,
                'sha256': m['sha256'], 'actual_image_viewed': True, 'labels_legible_for_declared_scope': True,
                'displayed_review_pixels': {'width': 1824, 'height': 1367}, 'original_pixel_dimensions_claimed': False,
                'method': 'Actual view_image output inspected. Raw2732x2048 PNG retained byte-for-byte. Only manual visible labels and identified control rectangles are accepted. Parent, render and playback review remain separate.'}})
    indexed = {int(row['id'][:3]): row for row in images}
    lesson_scenes, sentence_map = [], []
    for scene_id, title, sentences in SCENES:
        bodies = []
        labels = []
        for i, item in enumerate(sentences, 1):
            number, text, required = item[:3]
            if any(label not in LABELS[number] for label in required):
                raise ValueError('Unseen declared literal.')
            bodies.append(text)
            labels.extend(required)
            sentence_map.append({'scene_id': scene_id, 'sentence_id': scene_id + '-' + str(i).zfill(2),
                'text': text, 'capture_id': indexed[number]['id'], 'image_sha256': indexed[number]['sha256'],
                'required_labels': required, 'native_control': item[3] if len(item) > 3 else None,
                'speech_timing': None})
        lesson_scenes.append({'id': scene_id, 'title': title, 'narration': ' '.join(bodies),
            'required_labels': list(dict.fromkeys(labels))})
    lesson = {'id': 'app-unit-call-lifecycle-native', 'title': 'Unit: create, select, respond to and close a call',
        'app': 'Unit', 'audience': ['Unit operators', 'Field supervisors', 'Department trainers'],
        'summary': 'Use the native Unit call workflow, distinguish unit status from active-call selection, and verify closeout through fresh readback.',
        'prerequisites': ['A permitted Unit sign-in and selected training unit', 'A fictional local call and reviewed audience',
            'Department authority for call creation, status changes and closeout'],
        'scenes': lesson_scenes, 'export_ready': False,
        'authoring_status': 'bounded_native_actual_source_candidate_frozen_parent_review_and_narration_pending',
        'sector_examples': {'community_paramedicine': 'A community-care vehicle uses the same unit/call identity checks.',
            'mental_health': 'A response team keeps the selected assignment and its status distinct.',
            'search_and_rescue': 'A search vehicle checks the call and destination before a status update.',
            'security': 'A patrol distinguishes its own active assignment from department incident closeout.',
            'wildland': 'A crew vehicle verifies its status and a separate incident selection.',
            'industrial': 'A site response vehicle reviews its audience and closeout setting.'},
        'capture_limitations': ['This is the native iPad training app, not a web/native parity claim.',
            'Creation images precede an isolated spinner-effect repair; response and closeout use the repaired recording copy. Native public context retains the exact source-profile history.',
            'The chosen unit has0of1roles throughout; no seat, other unit, live incident or qualification was changed by this source preparation.',
            'Status saved and close success are observed software results, without physical response, GPS, delivery, provider or hardware claims.',
            'Immediate post-close native header remains cachedResponding; fresh native readback showsReleased. Do not replace either with Available.',
            'Locations/schedule remain empty; no route/geocoder/location permission is exercised.',
            'No narration, final timed plan, encoded video, playback proof or publication approval is created by this candidate.']}
    assets['lesson.candidate.json'] = encoded(lesson)
    assets['narration.txt'] = ('\n\n'.join(scene['narration'] for scene in lesson_scenes) + '\n').encode()
    assets['sentence-screen-map.untimed.json'] = encoded({'kind': 'Exact untimed original-sentence/native-image mapping',
        'lesson_id': lesson['id'], 'sentences': sentence_map, 'all_timing_from_future_actual_speech_required': True,
        'parent_review_pending': True, 'human_listening_claim': False, 'rendered_or_publishable': False})
    assets['captures.native-reviewed.json'] = encoded({'kind': 'bounded_actual_native_source_review_not_video_qualification',
        'source_only': True, 'publication_approved': False, 'native_sources': images,
        'raw_pngs_copied_unchanged': True, 'public_metadata_projection_is_explicit': True})
    assets['context-provenance.json'] = encoded({'kind': 'Public native source-context boundary retained for parent review',
        'original_public_projection': {name: {'file': str(PROJECTION / name), 'sha256': sha(S / PROJECTION / name)} for name in PINNED},
        'context_retention': 'The copied public native context and Core corroboration preserve recorded history. Original host-sensitive contexts are provenance only and are never copied.',
        'parent_native_context_qualification_pending': True, 'native_runtime_profile_changes_disclosed': True})
    for name in ['native-context.public.json', 'core-corroboration.public.json', 'projection-audit.json']:
        assets['public-context/' + name] = (S / PROJECTION / name).read_bytes()
    assets['README.txt'] = ('Source-only native Unit call candidate.\n\n'
        'Read lesson.candidate.json and sentence-screen-map.untimed.json together.\n'
        'All selected original PNGs are unchanged. The23images were inspected through actual view_image output; the parent still needs to inspect selected pixels and approve the learner script before narration.\n'
        'The native runtime/source-profile history is retained in public-context. Keep the before/after isolated spinner fix explicit. Core screenshots corroborate state only and cannot substitute for native app footage.\n'
        'No future timing, human hearing, renderer inputs, video, readiness, canonical adoption or publication approval exists here.\n'
        'Run the preparation script without arguments to verify this frozen candidate. It never mutates the app or database.\n').encode()
    destination.mkdir(parents=True)
    for relative, body in assets.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(body)
    for row in images:
        path = S / row['file']
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(S / row['original_file'], path)
        if sha(path) != row['sha256']:
            raise ValueError('Copied PNG changed.')
    files = [{'file': path.relative_to(S).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}
        for path in sorted(destination.rglob('*')) if path.is_file()]
    freeze = {'kind': 'New immutable source candidate, not approved narration or video', 'created_at': now,
        'recipe_file': str(Path(__file__).relative_to(S)), 'recipe_sha256': sha(__file__),
        'lesson_sha256': sha(destination / 'lesson.candidate.json'), 'narration_sha256': sha(destination / 'narration.txt'),
        'scene_count': len(lesson_scenes), 'sentence_count': len(sentence_map), 'images': len(images),
        'words': len(' '.join(scene['narration'] for scene in lesson_scenes).split()),
        'parent_script_and_pixels_approved': False, 'audio_created': False, 'timing_estimated': False,
        'canonical_changed': False, 'rendered_or_published': False, 'files': files}
    with (destination / 'source-freeze.json').open('xb') as stream:
        stream.write(encoded(freeze))
    return freeze


def verify():
    inputs()
    destination = S / BASE
    freeze = json.loads((destination / 'source-freeze.json').read_text())
    for row in freeze['files']:
        if sha(S / row['file']) != row['sha256']:
            raise ValueError('Changed frozen file: ' + row['file'])
    lesson = json.loads((destination / 'lesson.candidate.json').read_text())
    mapping = json.loads((destination / 'sentence-screen-map.untimed.json').read_text())
    for scene in lesson['scenes']:
        if ' '.join(row['text'] for row in mapping['sentences'] if row['scene_id'] == scene['id']) != scene['narration']:
            raise ValueError('Sentence map differs from exact narration.')
    return {key: freeze[key] for key in ['lesson_sha256', 'narration_sha256', 'scene_count', 'sentence_count', 'images', 'words']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    if args.build:
        create()
    print(json.dumps({'verified_source_candidate': verify(), 'source_only': True, 'human_listening_or_publication_claim': False}, indent=2))
