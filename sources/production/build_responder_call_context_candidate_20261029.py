"""Curate a bounded read-only Responder Calls candidate from actual new pixels.

Default read-only. --write-candidate creates a NEW unvoiced review package.
Raw captures remain eligible=false and unchanged; no canonical/media action.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
APP = ROOT.parents[3] / 'Responder'
COPY = ROOT.parent / 'capture-apps/Responder'
RAW = Path('captures/expansion/responder-calls-readonly-20261029-235')
OUT = S / 'expansion/plans/app-responder-call-context-review-candidate-20261029'
NAME = 'app-responder-call-context-review'
HEAD = '0760a098e78871a6ce193a328f28926fad123e3b'
MANIFEST_SHA = '17b604e83ce35810371900343d980b147f3326c8463e7b827669d2b5d17f128e'
LEDGER_SHA = 'bdbc38b6ef54b6316ec8aa45d3852dce5b0eb6d7437496c199e6831f1c2b57bb'
REVIEW_AT = '2026-10-30T00:14:03Z'
FILES = {
 'src/app/(app)/home/calls.tsx': '911e2486210c8ba70e29dc7291f24c5c518b7cafb0ecd363a1c887f47dca35ad',
 'src/app/call/[id]/index.tsx': 'ab628df6a8d389b65cce80bb142291e78d20e22c695b9964766dd7f45560412e',
 'src/components/calls/call-card.tsx': 'bd921aeb69d4937a7e94a6ac7d6f4298b5304a7a0442791232970009fae36fac',
 'src/components/calls/call-notes-modal.tsx': '441b05e11a189323c5caeaee013a1556898358fb49bc3c687a3deb3fdeae5b0d',
 'src/components/calls/call-images-modal.tsx': '728f21bbb101dbb94af946b7bdfbc4bcadbe07755ac508c84449fec08dd50fab',
 'src/components/calls/call-files-modal.tsx': '759b30f8629fd9f4f4d8c91ad4cea395fce70e73b66360262dcc98807d5f0504',
 'src/components/home/summary-stats-row.tsx': 'fa3f263969e8e5d35325d5b697125dbfb3b3dad1bca73353eaf368d1e13a2bf1',
 'src/components/home/status-buttons.tsx': 'd8ef30a72cfd49aa8758416c55ccd7bce9813a0f1af1d42a24d08a315977f288',
 'src/components/home/user-status-card.tsx': '5cc694da3204c40ad02e6c07d299228d0bafefaddc4659c0fdf0d0cf7a9d65b1',
 'src/stores/calls/detail-store.ts': '1d223245ccd7f8b76630ee1f96e55664357cb18a59ac1b4b6f69a6e26c00dcf7',
 'src/stores/calls/store.ts': '57065717fb8abed72595e44a7fc190c0912c789734820e54018483e49b6c8970',
 'src/lib/call-dispatch.ts': 'e5362c6a6b7ab81e5d4875dddef2a77508d61fa73a69eb223e582f7df0452d4e',
 'src/api/calls/calls.ts': 'a3364c9eb86f79fccec53781e39e367487874c158ab3829f8d1cf07d821add2a',
 'src/api/calls/callNotes.ts': 'b61e12a478347c6fabc4d54ab1c62c15115f1eb287dad487e3d5a56553775116',
 'src/api/calls/callFiles.ts': 'f60aab996674164d9a7348919501c6bdebdbded63aad271bbf15eddc42697d21',
}
NATURE = 'Exercise: reported smoke at an unoccupied training warehouse. Squad 3 assigned for a search demonstration.'
NOTE = 'Fictional exercise for Resgrid Academy. Do not dispatch real resources.'
LABELS = {
 6: ['Resgrid Responder', 'Wallace Boden', 'Firehouse 51 — Training Department', 'Home', 'Calls', 'Search calls...', '#DEMO-0003', '#DEMO-0002'],
 7: ['Calls', 'Warehouse', '#DEMO-0001', 'TRAINING — Warehouse alarm', 'Training site 1 (fictional), Chicago, IL', 'Kelly Severide', 'Joe Cruz', 'Squad 3'],
 9: ['Call Details', 'Info', 'Priority', 'Urgent', 'Timestamp', 'Oct 25, 11:49 AM', 'Type', 'Structure Fire', 'Address', 'Training site 1 (fictional), Chicago, IL', 'Note', NOTE],
 10: ['Call Details', 'TRAINING — Warehouse alarm (DEMO-0001)', NATURE, 'Notes', 'Images', 'Files', 'Route', 'Info', 'Protocols', 'Dispatched', 'Activity'],
 11: ['Call Details', 'Protocols', 'No protocols attached to this call', 'Activity'],
 13: ['Call Details', 'Dispatched', 'Kelly Severide', 'Joe Cruz', 'Squad 3', 'Group: Squad 3', 'Type: User', 'Group: Firehouse 51', 'Type: Unit', 'Protocols', 'Activity'],
 14: ['Call Details', 'Activity', 'No timeline events available', 'Notes', 'Images', 'Files'],
 15: ['Call Notes', 'Search notes...', 'No notes found', "There's nothing to display at the moment", 'Add a new note...', 'Cancel', 'Add Note'],
 16: ['Call Images', 'No images available', 'Add images to your call to help with documentation and communication'],
 17: ['Call Files', 'No files available', 'No files have been added to this call yet'],
 19: ['Home', 'Status', 'Responding', 'Not Responding', 'On Scene', 'Standing By', '3', 'ACTIVE CALLS', '0', "CALLS I'M ON", 'Calls'],
}
REJECTED = {
 1: 'Only first two call cards are in view; requested DEMO-0001 is below viewport. Superseded by readable006/007.',
 2: 'System-theme contrast makes typed search nearly white on white and urgent-card rich text black on black. DOM presence cannot establish legibility.',
 3: 'Initial detail title and timestamp have poor contrast. Superseded by009/010 after the ordinary Dark preference.',
 4: 'Original System preference is retained by AX/action ledger, but pixel contrast is poor; not learner evidence.',
 5: 'Readable Dark display preparation only; not an additional Calls lesson operation or server setting change.',
 8: 'Initial map rectangle is gray/loading. Superseded by actual loaded010; not operational cartography evidence.',
 12: 'Only first dispatched row is fully in view; Joe Cruz is clipped and Squad3 below viewport.013 supplies all rows.',
 18: 'Intended Home selection resolved to Settings. Preserved wrong-screen diagnostic; no Home/response claim.',
}
SCENES = [
 ('01', 'Find the incident you mean', '/home/calls', [6, 7], ['Calls', 'Search calls...', 'Warehouse', '#DEMO-0001'],
  'Begin on Calls in an authorized Responder session. The cards bring together a call number, name, location and assigned resources. Read those details before choosing any response. In this fictional department, enter Warehouse in Search calls. The list narrows to TRAINING — Warehouse alarm, numbered DEMO-0001, at Training site one in Chicago. Check the name, number and address together; a familiar word in a search result is not enough to identify an incident. The search changes the displayed list. It does not rename a call, dispatch anyone or change your personal status.',
  'Find the training warehouse by name and confirm its number and location without creating or editing a call.'),
 ('02', 'Read the nature and location in context', '/call/51001', [10], ['Call Details', 'TRAINING — Warehouse alarm (DEMO-0001)', NATURE],
  'Open that card to reach Call Details. The same name and number remain at the top, followed by the nature of the call. Here it describes reported smoke at an unoccupied training warehouse and a Squad Three search demonstration. The map provides context for the stored incident location. It does not establish where your device is or whether a crew has arrived. Route is available beside Notes, Images and Files, but we leave it untouched while reviewing the information already supplied.',
  'Confirm the incident identity and describe what the stored nature actually says, without opening Route or requesting location access.'),
 ('03', 'Check the Info fields and training note', '/call/51001', [10, 9], ['Info', 'Priority', 'Urgent', 'Timestamp', 'Type', 'Structure Fire', 'Address', 'Note', NOTE],
  'On Info, scroll until Priority, Timestamp, Type, Address and Note are visible together. This example shows Urgent and Structure Fire. Its timestamp is October twenty-fifth at eleven forty-nine in the morning; that displayed time is not an arrival report. Check the address against the intended training site. The note explicitly identifies a fictional Academy exercise and says not to dispatch real resources. Read qualifiers like this along with the headline, rather than carrying an assumption from the call list into your next action.',
  'Identify the priority, type, timestamp and training qualifier, keeping the timestamp distinct from an arrival time.'),
 ('04', 'Separate assignments from a response', '/call/51001', [9, 13], ['Dispatched', 'Kelly Severide', 'Joe Cruz', 'Squad 3', 'Type: User', 'Type: Unit'],
  'Choose Dispatched and bring all the resource rows into view. Kelly Severide and Joe Cruz appear as User entries associated with Squad Three. Squad Three also has its own Unit entry, associated with Firehouse Fifty-one. The Group and Type labels help distinguish a person from a vehicle or team resource. This is the recorded dispatch assignment for the call. A name in this list does not, by itself, prove that person acknowledged the call, changed status, reached the location or received an external notification.',
  'Distinguish both User rows from the Unit row and explain what the assignment list does and does not establish.'),
 ('05', 'Interpret the available protocol and activity views', '/call/51001', [13, 11, 14], ['Protocols', 'No protocols attached to this call', 'Activity', 'No timeline events available'],
  'Protocols and Activity answer different questions. In Protocols, this call currently returns No protocols attached to this call. Activity returns No timeline events available. Read each result in the context of the selected incident. Neither message supplies a missing procedure or confirms an arrival. An empty activity view is not a reason to invent a response history. If important guidance or chronology is missing, resolve that through your authorized coordination process before treating the information as complete.',
  'Compare the two empty messages and explain which question each tab is trying to answer.'),
 ('06', 'Inspect notes without posting', '/call/51001', [14, 15], ['Notes', 'Call Notes', 'No notes found', 'Add a new note...', 'Add Note', 'Cancel'],
  'Choose Notes to inspect Call Notes. This example says No notes found. The search box can help find an existing note when there are entries. Below it, Add a new note and Add Note belong to the writing workflow. We leave the field blank and use Cancel, so this inspection adds nothing to the incident. Reading the original note on Info and checking the separate Call Notes list are useful complementary checks; do not assume they are the same piece of information.',
  'Open Call Notes, read its current result and cancel without entering or posting text.'),
 ('07', 'Check which supporting material exists', '/call/51001', [14, 16, 14, 17], ['Images', 'Call Images', 'No images available', 'Files', 'Call Files', 'No files available'],
  'The Images and Files buttons open separate supporting views. Call Images currently says No images available. Call Files says No files available and explains that none have been added to this call. These are the results shown for this incident, not demonstrations of uploading, downloading or taking a photograph. Check the call identity before relying on an attachment from any source, and use only approved material when a later task genuinely requires adding one.',
  'Inspect both supporting views and distinguish an empty list from a successful upload or download.'),
 ('08', 'Keep review and response decisions distinct', '/home', [19], ['Home', 'Status', 'Responding', 'Not Responding', 'On Scene', 'Standing By', '3', 'ACTIVE CALLS', '0', "CALLS I'M ON"],
  'On Home, this example shows three Active Calls and zero Calls I’m On. Those counts answer different questions. The Status controls include Responding, Not Responding, On Scene and Standing By; the Standing By choice remains outlined during this review. We do not press a response button. Use the same read-before-response pattern for fire and EMS, community-care or mental-health teams, search and rescue, security patrols, wildland contractors and industrial teams. Find the correct incident, read its context and assignments, and identify missing information before making an authorized operational response.',
  'Explain why reading an incident and seeing an assignment are separate from sending your own response.'),
]


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(part)
    return digest.hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def prepare():
    assert sha(S / RAW / 'manifest.json') == MANIFEST_SHA and sha(S / RAW / 'action-ledger.json') == LEDGER_SHA
    raw = json.loads((S / RAW / 'manifest.json').read_text())
    assert len(raw['captures']) == 19 and all(row['eligible_for_lesson'] is False for row in raw['captures'])
    assert raw['session']['tab_id'] == '393909235'
    sys.path.insert(0, str(ROOT / 'scripts'))
    from verify_capture_evidence import _image_dimensions
    by_number = {int(row['id'][:3]): row for row in raw['captures']}
    for row in by_number.values():
        assert sha(S / row['file']) == row['sha256'] and sha(S / row['dom_file']) == row['dom_sha256']
        assert _image_dimensions(S / row['file']) == (1434, 773)
    assert subprocess.check_output(['git', '-C', str(APP), 'rev-parse', 'HEAD'], text=True).strip() == HEAD
    assets, source_rows = {}, []
    for path, digest in FILES.items():
        assert sha(APP / path) == digest and sha(COPY / path) == digest, 'Source/capture-copy mismatch: ' + path
        assert hashlib.sha256(subprocess.check_output(['git', '-C', str(APP), 'show', HEAD + ':' + path])).hexdigest() == digest
        name = 'source/Responder/' + path
        assets[name] = (APP / path).read_bytes()
        source_rows.append({'path': path, 'sha256': digest, 'snapshot': name, 'original_HEAD_and_recording_copy_equal': True})
    curated, reviews = [], []
    for number, labels in LABELS.items():
        row = deepcopy(by_number[number])
        added = [label for label in labels if label not in row['visible_labels']]
        assert added == ({9: [NOTE], 10: [NATURE]}.get(number, [])), (number, added)
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True,
                   required_labels=[], missing_required_labels=[], visual_review='actual_original_image_reviewed')
        row['capture_review'] = {'passed': True, 'reviewer': 'Codex /root/dispatch_ic_coverage', 'reviewed_at': REVIEW_AT,
                                 'sha256': row['sha256'], 'method': 'Personally displayed the exact JPEG bytes returned after storage by the supported screenshot helper. Foreground readable literal text only; no100-percent manual pixel-inspection claim. All19 originals were displayed, including excluded images.',
                                 'notes': 'No source pixels altered. Background labels behind modals and unnecessary icon-control geometry are removed from this new subset; raw manifest remains unchanged.'}
        if added:
            row['supplemental_literal_review'] = {'sha256': row['sha256'], 'literal_labels_added': added,
                                                  'reviewer': 'Codex /root/dispatch_ic_coverage', 'reviewed_at': REVIEW_AT,
                                                  'raw_mismatch_reason': 'Readable rich-text iframe content is visible in the original pixels/AX, but capture_application labels inspect the outer document only. No hidden-state label or DOM mutation is used.'}
        if number in (15, 16, 17):
            row['source_limits'] = ['Foreground viewer labels only. Occluded/dimmed background call controls cannot satisfy an instruction. Empty result is an observed current view, not independent backend inventory proof.']
        if number == 19:
            row['source_limits'] = ['3/ACTIVE CALLS and0/CALLS I\'M ON are separately printed values/labels. No invented combined literal. Standing By outlined button is visible; Current is an AX observation, not a printed label.']
        curated.append(row)
        reviews.append({'source_id': row['id'], 'sha256': row['sha256'], 'accepted_literal_labels': labels,
                        'raw_extra_labels_removed': [label for label in by_number[number]['visible_labels'] if label not in labels],
                        'raw_false_negative_literals': added})
    rows = {int(row['id'][:3]): row for row in curated}
    scenes, spans = [], []
    for ident, title, route, order, required, narration, practice in SCENES:
        assert set(required) <= {label for n in order for label in rows[n]['visible_labels']}
        scene = {'id': ident, 'title': title, 'route': route, 'capture_intent': 'Use only the actual ordered foreground views for these read-only instructions.',
                 'capture_refs': [rows[n]['id'] for n in order], 'required_labels': required,
                 'narration': narration, 'practice': practice}
        scenes.append(scene)
        spans.append({'scene_id': ident, 'title': title, 'narration': narration,
                      'ordered_sources': [{'capture_id': rows[n]['id'], 'file': rows[n]['file'], 'sha256': rows[n]['sha256']} for n in order],
                      'timing': None, 'limits': 'Untimed source order only; real approved speech cues/one-second markers are required before editorial cuts.'})
    narration = '\n\n'.join(scene['narration'] for scene in scenes) + '\n'
    assert 600 <= len(narration.split()) <= 800, len(narration.split())
    lesson = {'id': NAME, 'title': 'Responder: inspect an incident before responding', 'app': 'Responder',
              'audience': ['Responders and team members authorized to view department calls'],
              'summary': 'Find a training incident, inspect its information and assignments, and distinguish missing context from an operational response.',
              'prerequisites': ['An existing authorized Responder session; no sign-in flow is demonstrated.',
                                'Permission to read calls and their supporting views in a fictional practice department.',
                                'These browser screens use the app Dark display preference; no device-location or hardware permission is required.'],
              'scenes': scenes, 'source_files': [{'repository': 'Responder', 'path': x['path'], 'sha256': x['sha256']} for x in source_rows],
              'sector_examples': [
                  {'sector': 'Fire/EMS', 'scenario': 'Review the correct training alarm, priority, nature and assignments before choosing a personal response.'},
                  {'sector': 'Community care and mental health', 'scenario': 'Review a fictional operational call and missing guidance without adding client histories to notes.'},
                  {'sector': 'Search and rescue', 'scenario': 'Confirm the mission identity and assigned people/unit rows without treating them as arrival reports.'},
                  {'sector': 'Security', 'scenario': 'Inspect a patrol incident and its supporting material before making an authorized response.'},
                  {'sector': 'Wildland', 'scenario': 'Confirm the correct training incident location and group/type assignments without claiming physical resource positions.'},
                  {'sector': 'Industrial', 'scenario': 'Review a site exercise and recognize empty procedure/attachment views before acting.'}],
              'candidate_only': True, 'narration_frozen': False, 'parent_full_script_review_pending': True,
              'export_ready': False, 'publication_approved': False,
              'scope_limits': ['Read-only Calls context and response-control visibility. No actual response, dispatch, close, record creation, note/attachment upload or provider delivery is demonstrated.',
                               'Separate finished Responder orientation, communications and certification lessons remain unchanged. Broad calls/records and readiness drafts retain their gaps.',
                               'Empty screens are described as the current visible result; no hidden API/store inspection or complete backend inventory claim.',
                               'No GPS, offline persistence, camera/voice, permission, security or hardware result is claimed.']}
    capture_manifest = {'schema_version': 1, 'id': NAME, 'raw_manifest': {'file': (RAW / 'manifest.json').as_posix(), 'sha256': MANIFEST_SHA},
                        'raw_images_preserved': 19, 'screenshots': curated,
                        'excluded_sources': [{'id': by_number[n]['id'], 'sha256': by_number[n]['sha256'], 'reason': reason} for n, reason in REJECTED.items()]}
    audit = {'kind': 'actual_read_only_Responder_Calls_candidate_source_and_pixel_review', 'reviewer': 'Codex /root/dispatch_ic_coverage', 'reviewed_at': REVIEW_AT,
             'raw_manifest_sha256': MANIFEST_SHA, 'action_ledger_sha256': LEDGER_SHA, 'raw_pairs_preserved': 19,
             'accepted_sources': len(curated), 'scenes': 8, 'narration_words_whitespace': len(narration.split()),
             'exact_original_bytes_displayed_and_rehashed': True, 'literal_reviews': reviews,
             'normal_UI_only': True, 'recorded_display_preference_change': {'original': 'System', 'selected': 'Dark', 'authority': 'Root explicitly approved only ordinary app Theme Dark for contrast; no server/security/shared/KeepAlive/location/hardware control changed.', 'left_dark': True},
             'read_only_capture_outcomes': ['Original DEMO warehouse identity/nature, Info fields and training note readable.', 'Two dispatched User entries and one Unit entry fully visible in013.', 'Protocols/Activity/Notes/Images/Files actual empty-result text captured without writes.', 'Home019 shows3active/0mine and current outlinedStandingBy response choice; no response/status/staffing selection.'],
             'source_identity': {'repository': 'Responder', 'git_revision': HEAD, 'managed_source_snapshots': source_rows, 'scope': 'These15 original HEAD source files match the isolated recording copy. This is source/UI correspondence, not cryptographic executed-JS or native identity attestation.'},
             'source_read_endpoints': ['/Calls/GetActiveCalls', '/Calls/GetCall', '/Calls/GetCallExtraData', '/CallNotes/GetCallNotes', '/CallFiles/GetFilesForCall'],
             'endpoint_limit': 'Static source citations only; the agent did not issue direct requests or inspect auth/session stores. No provider delivery or network-execution assertion.',
             'privacy_pixel_review': 'All exact19 stored images displayed; no filled credentials, tokens, private employer fields or real patient/client material seen. Seed names/locations are explicitly fictional training data.',
             'canonical_frozen_media_site_or_target_changed': False, 'parent_review_pending': True}
    assets.update({'candidate.json': encoded(lesson), 'narration.txt': narration.encode(), 'captures.reviewed.json': encoded(capture_manifest),
                   'screen-sequence.untimed.json': encoded({'id': NAME, 'scenes': spans, 'timing_assigned': False}),
                   'source-pixel-review.json': encoded(audit)})
    return lesson, assets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    lesson, assets = prepare()
    if args.write_candidate:
        assert not OUT.exists(), 'New-only candidate; preserve prior raw, drafts and qualified lessons.'
        spec = importlib.util.spec_from_file_location('ordinary_privacy', ROOT / 'scripts/audit_public_repo.py')
        privacy = importlib.util.module_from_spec(spec); spec.loader.exec_module(privacy)
        raw_files = [p for p in (S / RAW).iterdir() if p.is_file()]
        issues = [{'file': p.relative_to(S).as_posix(), 'rule': rule} for p in raw_files for rule in privacy.scan_bytes(p.read_bytes())]
        issues += [{'file': name, 'rule': rule} for name, body in assets.items() for rule in privacy.scan_bytes(body)]
        assert not issues, issues
        provenance = {'kind': 'source_only_read_only_Responder_Calls_candidate_preflight', 'helper_sha256': sha(__file__),
                      'raw_manifest_sha256': MANIFEST_SHA, 'raw_action_ledger_sha256': LEDGER_SHA,
                      'ordinary_privacy_files_checked': len(raw_files) + len(assets), 'ordinary_privacy_findings': [],
                      'additional_known_private_values_checked': 0, 'scope': 'No credentials/tokens reread. Root known-value audit remains separate before installation.',
                      'narration_words': sum(len(x['narration'].split()) for x in lesson['scenes']),
                      'candidate_only': True, 'parent_script_review_pending': True, 'audio_timing_render_or_ready': False,
                      'files': {name: hashlib.sha256(body).hexdigest() for name, body in assets.items()}}
        assets['preflight.json'] = encoded(provenance)
        OUT.mkdir(parents=True)
        for name, body in assets.items():
            p = OUT / name; p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as stream:
                stream.write(body)
    print(json.dumps({'source_preflight': True, 'scenes': 8, 'words': sum(len(x['narration'].split()) for x in lesson['scenes']),
                      'accepted_sources': 11, 'original_pairs_preserved': 19, 'files_written': args.write_candidate,
                      'parent_script_review_pending': True, 'frozen_or_ready': False}))


if __name__ == '__main__':
    main()
