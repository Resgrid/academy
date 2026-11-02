"""Prepare a source-backed Unit call-workflow candidate without generating media.

Preserves the current canonical and all raw captures. Requires the existing
independent image/DOM reviews and byte-identical source assets. Entry actions
that still lack a suitable foreground image remain explicit capture gaps.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S = ROOT / 'sources'
OUT = S / 'expansion/plans/app-unit-response-candidate-20261028'

# Folder, original capture prefix, authored scene id/title, actual labels,
# proposed narration, learner practice. No speech times are assigned here.
STEPS = [
('unit-response-actions-20261027', '009', 'call-details', 'Prepare a clear training incident',
 ['New Call', 'Create New Call', 'Name', 'Nature', 'Priority', 'Type'],
 'Unit gives a vehicle or response team a shared workspace for its calls. When your account permits call creation, New Call opens Create New Call. Give the incident a useful Name and Nature, then choose the appropriate Priority and Type. Here the name identifies a training walkthrough, the priority is Routine, and the type is Investigation. An outreach team, security patrol, or industrial response crew can use descriptions that fit its own work.',
 'Prepare a fictional incident with the intended classification.'),
('unit-response-actions-20261027', '005', 'location', 'Review the incident location',
 ['Call Location', 'Address', 'GPS Coordinates', 'Destination POI'],
 'In Call Location, review Address and GPS Coordinates as separate fields. Our exercise uses a supplied fictional address and a manually entered coordinate pair. The Destination POI is still unselected. Keep the incident location and any later destination distinct: an access point, staging area, or receiving site may represent a different place. The other location methods shown here require their own verified lookup; this exercise does not demonstrate those lookups.',
 'Verify the supplied training point and whether a destination is required.'),
('unit-response-actions-20261027', '007', 'initial-recipients', 'Choose a limited practice audience',
 ['Select Dispatch Recipients', 'Everyone', 'Wallace Boden', '1 selected', 'Confirm'],
 'In Select Dispatch Recipients, choose the intended training recipient. Wallace Boden is selected here, while Everyone remains off. Review the selection count, then choose Confirm. A department should agree its practice audience before creating an exercise. The recipient picker gives you a chance to check that scope rather than sending a training call to every available person.',
 'Confirm the selected person and avoid unintended broadcast selection.'),
('unit-response-actions-20261027', '011', 'create', 'Review the final form before creation',
 ['External ID', 'Dispatch Time', 'Dispatch To', '1 selected', 'Create'],
 'Review the lower form before Create. External ID contains an exercise reference, Dispatch To shows one selected recipient, and Dispatch Time is blank for this unscheduled exercise. Check the fields your department requires, then create the call. A saved call and the receipt of an external notification are separate results; this walkthrough checks the saved incident in the app.',
 'Review the reference, timing, and recipient count before Create.'),
('unit-response-followup-20261027', '005', 'find-created', 'Find and identify the saved incident',
 ['Calls', '51011', '#FD51-2026-0003', 'TRAINING ONLY - Unit response walkthrough'],
 'Return to Calls and locate the saved training incident. In this recording, searching for internal call ID five one zero one one finds the exercise. Confirm the displayed department number, title, and location before opening it. The returned number is F D fifty-one, twenty twenty-six, zero zero zero three. Use your own returned identifiers when repeating the exercise; do not assume the next number.',
 'Find the saved call and compare its displayed identity with your exercise.'),
('unit-response-actions-20261027', '013', 'edit-action', 'Open the incident editing action',
 ['Edit Call', 'Close Call'],
 'The call actions offer Edit Call and Close Call as separate choices. Choose Edit Call for a correction while the incident remains active. We will update the exercise contact instructions first and handle closure later. This helps keep a routine correction separate from ending an incident that other people may still be working.',
 'Locate Edit Call and distinguish it from Close Call.'),
('unit-response-actions-20261027', '015', 'save-contact', 'Save corrected contact instructions',
 ['Edit Call', 'Contact Info', 'External ID', 'Save'],
 'In Edit Call, update Contact Info with concise instructions. Our training text directs the crew to the fictional coordinator at the east exercise entrance. Check the External ID so you are still editing the intended exercise, then choose Save. An entrance or meeting-point correction can be useful for community care, event response, and contractor work without changing the incident classification.',
 'Save one permitted correction on the intended training call.'),
('unit-response-actions-20261027', '016', 'verify-contact', 'Read back the corrected contact information',
 ['Contact', 'External ID', 'Contact Name', 'Contact Info'],
 'Reopen Contact in Call Details. Compare the External ID, Contact Name, and Contact Info with the exercise you edited. The new east-entrance instructions are present in the saved readback. Checking this view is how you distinguish a completed correction from text that was only entered into the form.',
 'Verify the saved contact text after returning to the incident.'),
('unit-response-actions-20261027', '017', 'add-note', 'Record a useful incident note',
 ['Call Notes', 'Add New Note', 'Add Note'],
 'Use Call Notes for an update that should remain in the incident conversation. Enter the message under Add New Note, review it, and select Add Note. Our fictional access note identifies the exercise entrance and coordinator. Keep an incident note distinct from the contact fields and from a later status-update note; each has its own context.',
 'Add a short exercise note in Call Notes.'),
('unit-response-actions-20261027', '018', 'verify-note', 'Verify the stored note and its context',
 ['Call Notes', 'Wallace Boden', 'Add New Note'],
 'Reopen Call Notes and verify the saved message, author, and timestamp. The access note now appears as an entry rather than only in Add New Note. This gives the next operator a useful record of the update. For search teams or security staff, use the same habit to make an agreed handover instruction easy to find.',
 'Read the saved note before adding another update.'),
('unit-response-followup-20261027', '006', 'upload-image', 'Review an image before uploading',
 ['Add New Image', 'Image Note', 'Upload'],
 'In Add New Image, review the selected picture and its Image Note before Upload. This example uses a sample software icon, and the note identifies it as training content rather than an incident photograph. Use only material your department permits. The preview is the place to catch an incorrect selection before attaching it to the incident.',
 'Review a permitted sample image and explanatory note before Upload.'),
('unit-response-followup-20261027', '007', 'verify-image', 'Confirm the image is stored on the call',
 ['Call Images', 'Add Image'],
 'Reopen Call Images and confirm that the sample picture appears with its stored timestamp. A preview by itself would not establish that the image was saved. Review the resulting call gallery after an upload, especially when several similar training files are available. An industrial team might use an approved equipment image; another department might use a permitted exercise-site image.',
 'Verify the intended image in the reopened gallery.'),
('unit-response-completion-20261027', '002', 'choose-status', 'Choose the response status',
 ['Select Status', 'Responding', 'Next'],
 'The response workflow opens Select Status. Read the configured choices and choose Responding for this exercise, then continue with Next. The available states and their destination or note requirements come from department configuration. The following views show the choices offered in this training department, so inspect your own configured labels rather than relying only on a button color.',
 'Read the status choices and select the appropriate exercise status.'),
('unit-response-completion-20261027', '003', 'responding-destination', 'Associate the response with the correct call',
 ['Select Destination for Responding', 'Calls', 'Next'],
 'Select Destination for Responding lets you choose the context for the status. Under Calls, verify the training call number and title before Next. The view also offers No Destination, Stations, and POIs. Use the option that fits the actual assignment; responding to a call and responding to a station convey different information to the department.',
 'Verify the selected exercise call before continuing.'),
('unit-response-completion-20261027', '004', 'submit-responding', 'Review the response note and submit',
 ['Add Note', 'Note (optional):', 'Responding · FD51-2026-0003 - TRAINING ONLY - Unit response walkthrough', 'Submit'],
 'In Add Note, check the Responding summary and incident identity. Add a useful optional note, then choose Submit. Our message identifies this as a software training update. Review this final step carefully: choosing a state earlier in the workflow is separate from submitting the completed update.',
 'Check the status and call summary before submitting the note.'),
('unit-response-completion-20261027', '006', 'verify-responding', 'Verify the saved unit response',
 ['Engine 51', 'Responding', '#FD51-2026-0003'],
 'Review the unit panel after submission. Engine 51 now shows Responding, and the selected incident is the training call. Check both the unit identity and call identity so the update is associated with the intended apparatus and assignment. The software status supports coordination; your organization still governs the physical response and reporting procedure.',
 'Confirm the unit, saved status, and selected incident together.'),
('unit-response-completion-20261027', '007', 'on-scene-destination', 'Choose the context for the next status',
 ['Select Destination for On Scene', 'Calls', 'Next'],
 'For the next exercise update, Select Destination for On Scene again asks for the call context. Verify the same practice incident before Next. Notice that this path has two steps in the recorded configuration, while the earlier response path had three. Follow the controls actually offered for the chosen status.',
 'Check the call context when changing to the next configured state.'),
('unit-response-completion-20261027', '008', 'submit-on-scene', 'Review and submit the next status note',
 ['Add Note', 'On Scene · FD51-2026-0003 - TRAINING ONLY - Unit response walkthrough', 'Submit'],
 'Review the On Scene summary and optional note in Add Note, then choose Submit. The note explicitly identifies this as a simulated software selection. In everyday use, report a status according to your department procedure and the actual assignment. Useful status notes help a coordinator understand the change without having to reconstruct it from several other screens.',
 'Review the intended state and note before the final submission.'),
('unit-response-completion-20261027', '009', 'verify-on-scene', 'Verify the new saved status',
 ['Engine 51', 'On Scene', '#FD51-2026-0003'],
 'Check the unit panel again. Engine 51 now shows On Scene for the same training incident. Verifying the saved result is especially useful on a shared vehicle device, where the next operator needs a clear picture of the selected apparatus and its assignment.',
 'Confirm the saved result on the unit panel.'),
('unit-response-completion-20261027', '010', 'activity', 'Review the incident activity history',
 ['Activity', 'Responding', 'On Scene'],
 'Open Activity to review the recorded changes. The history includes the Responding and On Scene entries, their timestamps, and the notes supplied in the exercise. Use this view to review the sequence of updates. These are recorded software events; they do not independently establish a device position or physical arrival.',
 'Compare the two saved events with the notes you submitted.'),
('unit-response-completion-20261027', '013', 'add-unit-recipient', 'Add the apparatus to the recipient selection',
 ['Select Dispatch Recipients', 'Units (2)', 'Engine 51', '2 selected', 'Confirm'],
 'When the incident needs an additional resource, Edit Call can change its recipient selection. In Select Dispatch Recipients, select the intended Engine 51 unit under Units, review the selection count, and Confirm. A unit and a group are different recipient choices. Check the actual unit name rather than assuming that a station group represents only that apparatus.',
 'Add the intended unit without selecting its entire group.'),
('unit-response-completion-20261027', '014', 'save-recipients', 'Save the revised recipient scope',
 ['Edit Call', 'Dispatch To', '2 selected', 'Save'],
 'Back in Edit Call, Dispatch To now shows two selected recipients. Check the rest of the form, then Save. Confirming the picker updates the form; saving the form completes the incident edit. Keep those two steps distinct when teaching a new operator.',
 'Save the reviewed recipient change on the incident.'),
('unit-response-completion-20261027', '016', 'verify-recipients', 'Verify the saved dispatched resources',
 ['Dispatched', 'Wallace Boden', 'Type: User', 'Engine 51', 'Type: Unit'],
 'Open Dispatched and review the saved entries. Wallace Boden is listed as a User, and Engine 51 is listed as a Unit. This verifies the resulting recipient scope and makes the person-versus-apparatus distinction visible. A dispatched resource list is separate from the vehicle crew assignments covered in the Unit access and crew lesson.',
 'Check that the saved list contains the intended person and unit.'),
('unit-response-close-20261027', '001', 'close', 'Review closure type, note, and notifications',
 ['Close Call', 'Close Type', 'Closed', 'Close Note', 'Notify everyone on the call'],
 'Use Close Call when the authorized exercise is finished. Review Close Type, add a useful Close Note, and check Notify everyone on the call before submitting. We use Closed and leave the notification option off for this local practice. A real department should choose the closing audience deliberately, because this option can notify the people and resources associated with the incident.',
 'Review all closure choices before closing the agreed exercise.'),
('unit-response-close-20261027', '002', 'verify-closed-list', 'Check the active call list after closure',
 ['Calls', 'Search calls...', '#DEMO-0003', '#DEMO-0002', '#DEMO-0001'],
 'Review the main Calls list after closure with the search cleared. The exercise call has left the active list, while the three original training calls remain. Check the call list separately from the unit panel: ending an incident and reviewing the apparatus context are related checks, with different displayed fields.',
 'Verify the active list without confusing it with the selected unit context.'),
('unit-post-close-verification-20261027', '002', 'final-unit-context', 'Verify the final apparatus context',
 ['Engine 51', 'Released', 'No Active Call'],
 'Finish by checking the unit panel. This final readback shows Engine 51 as Released with No Active Call. Verify the intended call selection and status under your department workflow before handing over the device. The same habits apply to fire and EMS vehicles, community response teams, search and rescue units, security patrols, wildland contractors, and industrial response crews.',
 'Review the final unit identity, status, and call context before handover.')]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare():
    assert not OUT.exists(), 'Preserve previous candidates; choose a new output path.'
    now = datetime.now(timezone.utc).isoformat()
    inventories, sources, scenes, pinned = {}, [], [], {}
    for folder, prefix, ident, title, labels, narration, practice in STEPS:
        if folder not in inventories:
            path = S / 'captures/expansion' / folder / 'review/reviewed-source-subset-20261027.json'
            data = json.loads(path.read_text())
            inventories[folder] = data['screenshots']
            pinned[str(path.relative_to(S))] = digest(path)
        matches = [r for r in inventories[folder] if r['id'].startswith(prefix+'-')]
        assert len(matches) == 1, (folder, prefix)
        row = dict(matches[0])
        assert row.get('eligible_for_lesson') is True
        assert row['capture_review']['passed'] is True
        assert digest(S/row['file']) == row['sha256']
        assert digest(S/row['dom_file']) == row['dom_sha256']
        assert set(labels) <= set(row['visible_labels']), (ident, set(labels)-set(row['visible_labels']))
        row['original_id'] = row['id']
        row['id'] = folder + '-' + row['id']
        sources.append(row)
        scenes.append({'id': ident, 'title': title, 'required_labels': labels,
            'narration': narration, 'practice': practice,
            'capture_evidence': {'status': 'existing_independent_source_review_reused',
                'capture_refs': [row['id']], 'source_review': pinned},
            'timing_status': 'untimed; actual speech export required'})
    gaps = [
        {'operation': 'New Call launcher', 'before_scene': 'call-details',
         'required_capture': 'Foreground Calls action, including the actual accessible name of the plus/New Call control, followed by the opened form. Do not invent a literal label for an icon.'},
        {'operation': 'Set Active entry', 'before_scene': 'choose-status',
         'required_capture': 'An unobscured call header and Set Active action. The current raw screenshot has the call-actions sheet open; its dimmed background action is deliberately excluded from the reviewed subset.'},
        {'operation': 'Clear selection / Deselect confirmation', 'before_scene': 'final-unit-context',
         'required_capture': 'If the finished lesson teaches this operation, capture the actual web confirmation and settled state through the normal UI. Current footage verifies the final state only; it does not picture the confirmation.'}]
    candidate = {'id': 'app-unit-02-response-and-checks',
        'title': 'Unit: create, update and work a training call', 'app': 'Unit',
        'audience': ['Vehicle and apparatus crews', 'Response team leaders'],
        'summary': 'Follow a fictional call through creation, contact edits, notes, image upload, response statuses, recipient changes, and closure.',
        'scenes': scenes, 'narration_word_count': sum(len(s['narration'].split()) for s in scenes),
        'export_ready': False, 'authoring_status': 'source_backed_candidate_with_explicit_capture_gaps',
        'do_not_generate_narration_yet': True, 'capture_gaps': gaps,
        'scope_notes': ['Existing coherent historical exercise51011/FD51-2026-0003; it is now closed. No historical source was edited, reopened or reseeded.',
            'A new capture session must preserve chronology and call identity, or explicitly separate its scenario; do not substitute another incident as proof of this historical action.',
            'The final Released/No Active Call image is an observed later readback. Do not imply that closing the call by itself performed every selection/status cleanup operation.',
            'Checklists, personnel check-ins, crew setup, routes, inventory, provider routing and native hardware/offline behavior are outside this candidate; retain the completed companion lessons and remaining feature work.'],
        'completed_companions': ['app-unit-01-access-and-crew', 'app-unit-readiness-checklists', 'app-unit-personnel-checkins']}
    OUT.mkdir(parents=True)
    (OUT/'lesson.candidate.json').write_text(json.dumps(candidate,indent=2,ensure_ascii=False)+'\n')
    (OUT/'captures.reviewed.json').write_text(json.dumps({'app':'Unit','screenshots':sources,'original_source_pins':pinned},indent=2,ensure_ascii=False)+'\n')
    (OUT/'narration.proposed.txt').write_text('\n\n'.join(s['narration'] for s in scenes)+'\n')
    report = {'prepared_at':now, 'candidate_sha256':digest(OUT/'lesson.candidate.json'),
        'scenes':len(scenes), 'source_images':len(sources), 'words':candidate['narration_word_count'],
        'capture_gaps':gaps, 'existing_source_reviews_and_image_dom_hashes_checked':True,
        'new_independent_all_image_visual_review_claimed':False,
        'canonical_changed':False, 'audio_created':False, 'rendered':False, 'publication_approved':False}
    (OUT/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='capture_gaps'}))


if __name__ == '__main__':
    prepare()
