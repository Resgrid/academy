"""Freeze reviewed Dispatch console footage and its matching narration.

This retains source material only. It neither generates speech nor qualifies a
video. Preserve old freezes; changed source, speech or capture needs a new take.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-dispatch-console-status-and-staffing'
BASE = Path('expansion/plans/'+NAME+'-capture-freeze-20261028')
REVIEW = Path('captures/expansion/dispatch-workspace-20261028/review/reviewed-source-subset-20261028.json')
REVIEW_SHA = 'df6b2ac9024f8c9a94990d90ea3fadba537692872f74a2b86c481a17687584fc'
RAW_SHA = '8ee5a98d6585e047cc8f928a0b1512b30d6693b0882fe67598f8f6a291e980aa'
REVIEWED_AT = '2026-10-28T17:08:16+00:00'

# Each paragraph has one specific, unaltered application screenshot. Do not
# substitute the console overview while explaining a chooser or saved result.
STEPS = [
('001-console-overview', 'read-console', 'Find the console panels',
 ['Resgrid Dispatch','Active Calls','Units','Map','Personnel','Notes'],
 'Resgrid Dispatch brings calls, units, personnel, the map, and notes into one console. This walkthrough is for dispatchers and other authorized coordinators who need to find the right resource and maintain its recorded state. We use a fictional firehouse, but the same console pattern can support community response teams, search and rescue, security operations, wildland contractors, and industrial response.',
 'Locate the call, unit and personnel panels before choosing a resource.'),
('002-call-search-community', 'search-calls', 'Search within the call panel',
 ['Community','TRAINING — Community medical standby','Active Calls'],
 'Start in the call panel and enter Community in its search field. The list now shows the fictional community medical standby. Notice that the top summary still reports three active calls while the searched panel shows one. Search helps find an incident in the list; check the incident name before selecting it.',
 'Search for an existing fictional call without modifying it.'),
('003-selected-call-context', 'select-call-context', 'Recognize a selected call',
 ['Filtering by call: #DEMO-0002','Clear Filter','Units on Call','Personnel on Call','Call Notes','Active Filter'],
 'Select the intended call card. The blue Filtering by call banner identifies DEMO-0002, and the resource panels now say Units on Call and Personnel on Call. Call Notes is also scoped to that incident. Read this banner before acting. An On Call assignment label and the resource status are separate pieces of information.',
 'Confirm the call identifier in the banner and the incident-scoped panel headings.'),
('005-call-filter-cleared-search-retained', 'clear-call-context', 'Clear incident context and check searches',
 ['Active Calls','Community','Personnel','Units','Notes'],
 'Use Clear Filter to leave the incident context. The banner is gone and the resource headings return to Units, Personnel, and Notes. Community is still in the call search field, so that panel remains narrowed. Clear its search separately when you want the full call list. This distinction helps explain why a panel can still look filtered after leaving an incident.',
 'Clear the call context, then separately clear the call-panel search.'),
('006-available-unit-filter', 'filter-available-units', 'Inspect available units',
 ['Available only','Units','Engine 51','Available'],
 'With the call search cleared, turn on Available only at the top. In this recorded example, the unit panel contains four units instead of six. Engine 51 is listed as Available. Read the resulting list and its count when filtering resources. A recorded availability value still needs to be interpreted using your organization’s dispatch procedure.',
 'Compare the visible unit list before and after Available only.'),
('007-unit-search-engines', 'search-units', 'Restore the unit list and search',
 ['Engine','Engine 51','Reserve Engine 51','Out of Service','Available'],
 'Turn Available only off, then enter Engine in the unit search. Two matches are visible: Engine 51, marked Available, and Reserve Engine 51, marked Out of Service. Check the full unit name and displayed state. Similar names make it especially useful to select from the unit panel deliberately and verify the selected resource before submitting an update.',
 'Locate the intended unit and distinguish it from similarly named resources.'),
('008-selected-unit-status-controls', 'select-unit', 'Open the intended unit’s actions',
 ['Engine 51','Status','Select Status','Note (optional)','Additional Fields'],
 'Select Engine 51 in the unit panel. Its Actions area now identifies Engine 51 and exposes Status, Select Status, and Note. Check that identity before entering an update. This is the unit action form. Leave unrelated fields alone when the task only requires a status and its supporting note.',
 'Verify Engine 51 in the action area before opening Select Status.'),
('009-unit-status-choices', 'review-unit-status-choices', 'Read status and destination choices',
 ['Select Status','Responding','Call destination','Available','Station destination','Committed','On Scene'],
 'Open Select Status. The displayed choices include Responding, Available, Committed, and On Scene. The chooser also describes their destination support: Responding shows Call destination, while Available shows Station destination in this department. Choose the state that matches the intended action. For this software exercise, we choose Available.',
 'Review the actual department choices and select Available for this exercise.'),
('010-unit-station-destinations', 'review-unit-destination', 'Check the destination selection',
 ['Destination','No Destination','Stations (2)','No Station','Firehouse 51'],
 'Open Destination and review the current selection. No Destination is selected. The Stations section contains rows named No Station and Firehouse 51. A row named No Station and the separate No Destination choice are distinct entries in this example. We retain No Destination for the exercise. Check the selected destination before sending any status update.',
 'Confirm No Destination remains selected in this exercise.'),
('011-unit-status-ready-to-submit', 'submit-unit-status', 'Review and submit the unit update',
 ['Engine 51','Available','No Destination','TRAINING ONLY - Dispatch status practice.','Update Status'],
 'Review the prepared values: Engine 51, Available, and No Destination. The note says Training only, Dispatch status practice. Once the intended resource and values are correct, choose Update Status. The note provides context for this fictional software exercise. For actual operations, enter the information your organization requires for the status change.',
 'Check resource identity, status, destination and note before Update Status.'),
('012-unit-status-update-observed', 'observe-unit-update', 'Read the update result',
 ['Engine 51','Available','Activity Log','Unit status updated'],
 'After submission, the Activity Log reports Unit status updated, and Engine 51 still displays Available. We deliberately submitted the existing Available value as practice. Read the result rather than expecting a different status color. Next, inspect the unit’s separate details page to check the stored values.',
 'Find Unit status updated and compare the unit card’s displayed status.'),
('013-unit-details-saved-readback', 'verify-unit-details', 'Verify saved unit state and crew',
 ['Engine 51','Status Information','Available','Destination','None','Status Updated','Assigned Roles','Christopher Herrmann'],
 'Open Engine 51’s details using its details icon. Status Information shows Available, Destination shows None, and Status Updated provides a recorded timestamp. Assigned Roles still lists Christopher Herrmann. This readback lets a coordinator check the saved unit state and see the crew assignment on the same record.',
 'Read the status, destination and retained crew assignment in Unit Details.'),
('014-unit-details-saved-note', 'verify-unit-note', 'Read back the stored unit note',
 ['Engine 51','Note','TRAINING ONLY - Dispatch status practice.'],
 'Scroll within the same unit details page to Note. The exact training note is now visible as stored record text. Compare it with the note entered before submission. Checking the saved note is useful when another coordinator needs to understand the context of an update.',
 'Compare the saved Note with the submitted exercise text.'),
('015-personnel-search-boden', 'search-personnel', 'Find the intended person',
 ['Boden','Wallace Boden','Command','Chief','Standing By','Available'],
 'Return to the console and search for Boden in Personnel. The matching Wallace Boden card shows Command and Chief, along with Standing By and Available. Read these fields separately: the card presents a response status and a staffing value. Confirm the person’s name before opening their actions.',
 'Find Wallace Boden and distinguish response status from staffing.'),
('016-personnel-status-controls', 'select-personnel', 'Identify the separate personnel controls',
 ['Wallace Boden','Status','Select Status','Note (optional)'],
 'Select Wallace Boden. The Actions area now identifies that person and shows the response-status form with Select Status and its note field. Staffing has its own controls lower in this area. For this exercise, leave the response-status form unchanged and continue to the staffing selector.',
 'Confirm Wallace Boden and locate Staffing lower in the same action area.'),
('017-personnel-staffing-choices', 'review-staffing-choices', 'Choose a staffing level',
 ['Select Staffing Level','Available','Delayed','Unavailable','Committed','On Shift'],
 'Open Select Staffing Level. This department offers Available, Delayed, Unavailable, Committed, and On Shift. These are the staffing choices shown by this training configuration. Choose the level your organization intends to record. Our exercise uses Available, preserving the member’s existing response status.',
 'Review the staffing choices and select Available for this exercise.'),
('018-personnel-staffing-ready', 'submit-staffing', 'Review and submit personnel staffing',
 ['Wallace Boden','Staffing','Available','TRAINING ONLY - Dispatch staffing practice.','Update Staffing'],
 'Review Wallace Boden, Staffing Available, and the note Training only, Dispatch staffing practice. Choose Update Staffing when those values are correct. Check the action’s label before submitting: this exercise sends the staffing form. It does not submit the separate response-status form above it.',
 'Check member identity, staffing level and note before Update Staffing.'),
('019-personnel-staffing-update-observed', 'observe-staffing-update', 'Read the staffing update result',
 ['Wallace Boden','Standing By','Available','Personnel staffing updated'],
 'The Activity Log now reports Personnel staffing updated. Wallace Boden’s card shows Standing By and Available. Read both values after submission, then use the personnel details view for a separate readback. The update event confirms the software action shown here; the next view identifies which fields are available to inspect.',
 'Find Personnel staffing updated and compare both displayed member values.'),
('020-personnel-details-readback', 'verify-personnel-details', 'Verify status and staffing separately',
 ['Wallace Boden','Status & Staffing','Standing By','Staffing','Available','Staffing Updated','Roles','Chief'],
 'Open Wallace Boden’s details. Status and Staffing shows Standing By and Available in separate rows, with update timestamps, and Roles lists Chief. This page verifies the displayed response and staffing values; it does not display the staffing note. The same careful readback helps coordinators of community paramedicine, mental health response, search teams, security shifts, wildland crews, and industrial teams keep recorded staffing understandable.',
 'Verify the separate status and staffing rows without assuming an unshown note was read back.')
]

SOURCE_FILES = [
 'src/app/(app)/home.web.tsx',
 'src/components/dispatch-console/units-panel.tsx',
 'src/components/dispatch-console/unit-actions-panel.tsx',
 'src/components/dispatch-console/unit-status-sheets.tsx',
 'src/components/dispatch-console/personnel-panel.tsx',
 'src/components/dispatch-console/personnel-actions-panel.tsx',
 'src/app/units/[id].tsx',
 'src/app/personnel/[id].tsx'
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    out = SOURCES / BASE
    assert not out.exists(), 'Preserve existing freezes; choose a new version.'
    assert sha(SOURCES/REVIEW) == REVIEW_SHA
    reviewed = json.loads((SOURCES/REVIEW).read_text())
    assert reviewed['raw_manifest_sha256'] == RAW_SHA
    assert sha(SOURCES/reviewed['raw_manifest']) == RAW_SHA
    by_id = {r['id']:r for r in reviewed['screenshots']}
    selected, scenes = [], []
    for ident,scene_id,title,labels,narration,practice in STEPS:
        row = copy.deepcopy(by_id[ident])
        assert sha(SOURCES/row['file']) == row['sha256']
        assert row['capture_review']['passed']
        assert set(labels) <= set(row['visible_labels'])
        row['visible_labels'] = labels
        row['visible_controls'] = []
        row['eligible_for_lesson'] = True
        row['capture_review'].update({
            'reviewed_at':REVIEWED_AT,'sha256':row['sha256'],
            'labels_legible':True,'no_errors':True,
            'scope':'Original-size actual screenshot reviewed with the corresponding frozen narration. Only the listed readable foreground labels support this scene. No device GPS, physical readiness, radio delivery or unshown staffing-note readback is inferred.'
        })
        row['capture_review'].pop('narration_freeze_pending',None)
        selected.append(row)
        scenes.append({'id':scene_id,'title':title,'required_labels':labels,
            'narration':narration,'practice':practice,
            'capture_evidence':{'status':'actual_screenshot_reviewed','capture_refs':[ident]}})
    citations = []
    for relative in SOURCE_FILES:
        retained = Path('evidence/expansion/Dispatch')/relative
        current = Path('/Users/shawn/Documents/dev/Dispatch')/relative
        assert (SOURCES/retained).read_bytes() == current.read_bytes(), relative
        citations.append({'file':str(retained),'sha256':sha(SOURCES/retained),
            'current_source_matches_retained_snapshot':True,
            'scope':'Source reference; file equality alone does not identify the served client bundle.'})
    lesson = {'id':NAME,'title':'Dispatch: filter the console and update unit status and staffing',
        'app':'Dispatch','audience':['Dispatchers','Authorized resource coordinators'],
        'summary':'Find an incident or resource, recognize console filters, submit a unit status and personnel staffing update, and verify the saved fields.',
        'prerequisites':['A normal authorized Dispatch session in the isolated fictional training department.','Existing units, personnel and calls from the training seed.'],
        'scenes':scenes,'source_files':[r['file'] for r in citations],
        'sector_examples':[
            {'sector':sector,'scenario':scenario,'practice':'Find the correct resource, review the action and check the saved state under the organization’s operating procedure.'}
            for sector,scenario in [
                ('Fire / EMS','Coordinate recorded apparatus status and personnel staffing.'),
                ('Community response','Review community paramedicine or mental health response-team staffing.'),
                ('Search and rescue','Locate a search-team resource and maintain its recorded status.'),
                ('Security','Keep personnel staffing distinct from a patrol unit’s status.'),
                ('Wildland','Review contractor crew and vehicle records before a dispatch action.'),
                ('Industrial','Maintain understandable response-team status and staffing records.')]],
        'capture_limitations':reviewed['limitations']+[
            'Unit Available and personnel Available were already set; the exercise verifies an explicit submission and readback, not a transition from a different prior state.',
            'The fictional positions span different regions. No nearest-resource, fresh location, route, physical movement or GPS workflow is demonstrated.',
            'No new call, resource assignment, call closure, bulk update, note deletion or product configuration is performed in this focused lesson.'
        ],
        'authoring_status':'actual_capture_reviewed_narration_frozen',
        'media_status':'awaiting_natural_narration','export_ready':False,
        'narration_word_count':sum(len(s['narration'].split()) for s in scenes)}
    out.mkdir(parents=True)
    def write(name,value):
        (out/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    write(NAME+'.narrated-source.json',lesson)
    write('captures.reviewed.json',{'app':'Dispatch','screenshots':selected,
        'source_manifest':reviewed['raw_manifest'],'source_manifest_sha256':RAW_SHA,
        'source_review':str(REVIEW),'source_review_sha256':REVIEW_SHA,'reviewed_at':REVIEWED_AT})
    write('source-citations.json',{'reviewed_at':REVIEWED_AT,'sources':citations})
    (out/'narration.txt').write_text('\n\n'.join(s['narration'] for s in scenes)+'\n')
    report = {'passed':True,'reviewed_at':REVIEWED_AT,'scenes':len(scenes),
        'screenshots':len(selected),'words':lesson['narration_word_count'],
        'lesson_sha256':sha(out/(NAME+'.narrated-source.json')),
        'raw_captures_modified':False,'canonical_lesson_changed':False,
        'narration_generated':False,'rendered':False,'publication_approved':False}
    write('source-preflight.json',report)
    print(json.dumps(report))


if __name__ == '__main__':
    freeze()
