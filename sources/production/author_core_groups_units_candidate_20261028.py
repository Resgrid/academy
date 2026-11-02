"""Retain a bounded, unvoiced Groups/Units candidate from actual source images.

Default/--check is read-only. --write-source creates named new source artifacts
only, refusing changed existing bytes. No browser/DB/app/freeze/audio/timing,
canonical/readiness/site/target or Git operation.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SOURCES=ROOT/'sources'; CORE=ROOT.parents[2]
NAME='core-groups-units-administration'
BASE=Path('expansion/plans/core-groups-units-administration-candidate-20261028')
RAW=Path('captures/expansion/core-groups-units-administration-20261028/manifest.json')
REVIEW=Path('captures/expansion/core-groups-units-administration-20261028-reviewed/manifest.json')
TRACE=Path('expansion/plans/core-groups-units-administration-source-trace-20261028')
STAFFING=Path('expansion/audits/core-groups-units-staffing-readonly-observation-20261028.json')
PINS={RAW:'e9e15926ce3e965702edbde126d9450cc1aa71ed236c56f54259ea9847ccce0b',
 STAFFING:'46f85b7ae20bfb4aecc74bf006cc38120aef6001babf84728d50cbcde2406181',
 TRACE/'source-evidence.json':'72d9d6437accc60649d2ec489598fe1c2d316579801b473fd8a78c878f82ccd8',
 TRACE/'source-trace.json':'2f0a0973816407bc3248302143623d3129d95cdae3ce5fc5765ff9ab7d0cef96',
 TRACE/'runtime-config-and-parent-progress.observed.json':'692b6c09f64de05ce0b6d534f807b9a48bd414631de3aa1ccf2554a2dd981d86'}
EXTRA_SOURCE_PINS={
 'Web/Resgrid.Web/Areas/User/Views/Units/Index.cshtml':'db05d44d60f86883678e9f62b13c6e4a68c6a5ad0f76aae69c2459f273199173',
 'Web/Resgrid.Web/wwwroot/js/app/internal/units/resgrid.units.index.js':'9c7b508018695f1d2fd33f69a4fd11964ede06f0444cf8a2b341df33c79376c3'}
REVIEWED_AT='2026-10-28T23:56:45Z'
ORG='TRAINING ONLY - Community coordination 20261028'
STATION='TRAINING ONLY - Community base 20261028'
TYPE='TRAINING ONLY - Community response vehicle'
UNIT='TRAINING ONLY - Community van 20261028'
PERSON_ROLE='TRAINING ONLY - Community response navigator'
ONE_GROUP="Users can only be in one group at a time. If you don't see your user in the list they are already in a group."
GROUP=['Group type','Organizational Group','Station Group','Group Name','Parent Group']
MEMBERS=['Group Admins','Group Users','Select users...','Save Group',ONE_GROUP]
COORD=['Gps Coordinates','41.8500','-87.6500','what3words Address']
TYPE_FIELDS=['Unit Type Name',TYPE,'Class','Support','Actions (Custom Unit Statuses)','Standard Actions','Map Icon','Van','Custom icon','No file chosen']
SEATS=['Name',UNIT,'Type','Station','Roles','Role Name','Required Personnel Role','Required?',
 'Coordination seat',PERSON_ROLE,'Optional support seat','-- None --','Add Role','Browse Templates']
STAFF=['Unit Staffing','Engine 51','Fully Staffed','Officer / Team Lead','Christopher Herrmann',
 UNIT,'Not Staffed','Coordination seat','Requires: '+PERSON_ROLE+' (Required)',
 'Optional support seat','Not Occupied','Cancel','Save']
LABELS={
 1:['Stations & Groups','Types','Firehouse 51 — Training Department'],
 2:['Groups','Add New Group','Group Name','Type','Parent','Members','Firehouse 51','Station','None','Command','Engine 51','Truck 81','Squad 3','Ambulance 61','Organizational','Edit'],
 3:['New Group']+GROUP+['None','Select Printer','Cancel']+MEMBERS,
 4:['New Group']+GROUP+[ORG,'None','Select Printer','Cancel']+MEMBERS,
 6:['Edit Group']+GROUP+[ORG,'None','Print Calls to Printer','Select Printer','Cancel']+MEMBERS,
 7:['New Group']+GROUP+['Station Address','Street','City','State/Province','Zip/Postal Code','Country','United States','Gps Coordinates'],
 8:['New Group']+GROUP+[STATION,ORG,'Station Address','Street','City','State/Province','Zip/Postal Code','Country','United States','Gps Coordinates'],
 9:COORD+['Select Printer','Group Admins','Group Users','Save Group','Cancel',ONE_GROUP],
 10:COORD+['Select Printer','Group Admins','Group Users','Save Group','Cancel',ONE_GROUP],
 11:['Groups','Add New Group','Group Name','Type','Parent','Members',ORG,STATION,'Organizational','Station','None','0','Edit'],
 12:['Edit Group']+GROUP+[STATION,ORG,'Station Address','Street','City','State/Province','Zip/Postal Code','Country','United States']+COORD,
 13:COORD+['Select Printer','Print Calls to Printer','Group Admins','Group Users','Save Group','Cancel',ONE_GROUP],
 14:['Units','New Unit','Unit Staffing','All Units','Ungrouped Units','Firehouse 51',ORG,'Name','Type','Status','Timestamp','Engine 51','Truck 81','Squad 3','Ambulance 61','Battalion 25','Reserve Engine 51','Edit'],
 15:['New Unit','Name','Type','Aerial','here','Station','No Station','Roles','Browse Templates','Add Role','Role Name','Required Personnel Role','Required?','Cancel','Save'],
 16:['Unit Types','New Unit Type','Name','Actions (Custom Unit Statuses)','Map Icon','Aerial','Rescue','Ambulance','Command','Engine','Default Unit Actions','Default','Edit'],
 17:['New Unit Type','Unit Type Name','Class','None','Actions (Custom Unit Statuses)','Standard Actions','Map Icon','Default','Custom icon','No file chosen','Preview','Light map','Dark map','In a list'],
 18:['New Unit Type']+TYPE_FIELDS+['Preview','Light map','Dark map'],
 19:TYPE_FIELDS+['Preview','Light map','Dark map','In a list','No custom icon. Showing the default icon.','Cancel','Save'],
 20:['Unit Types','New Unit Type','Name','Actions (Custom Unit Statuses)','Map Icon',TYPE,'Default Unit Actions','Van','Edit'],
 21:['Edit Unit Type']+TYPE_FIELDS+['Preview','Light map','Dark map'],
 22:['New Unit']+SEATS+['Save','Cancel'],
 23:['Unit Role Templates','Security Companies','Security Patrol','Alarm Response Team','Protective Services Detail','Use these roles','Close'],
 25:['New Unit']+SEATS+['Save','Cancel'],
 26:['Units','New Unit','Unit Staffing','Search:','Name',UNIT,'Type',TYPE,'Status','Available','Edit',ORG,'Showing 1 to 1 of 1 entries (filtered from 8 total entries)'],
 27:['Edit Unit']+SEATS+['Update','Cancel'],
 28:['Edit Unit','Name',UNIT,'Type','Station','No Station','Firehouse 51',STATION,'Optional support seat','-- None --',PERSON_ROLE,'Required?','Update'],
 29:STAFF,
 30:STAFF+['Wallace Boden','Darren Ritter'],
 32:STAFF,
 33:['Units','All Units','Ungrouped Units',ORG,STATION,UNIT,TYPE,'Name','Type','Status','Available','Edit','Showing 1 to 1 of 1 entries'],
 34:['Units','All Units','Ungrouped Units',ORG,STATION,UNIT,TYPE,'Name','Type','Status','Available','Edit','Showing 1 to 1 of 1 entries'],
}
EXCLUDED={5:'Own new organizational row is clipped by the footer. Use006 for saved form and011 for full own catalog rows; not a saved-row proof.',
 24:'Transient modal backdrop still dims the form after closing templates. Superseded by settled025.',
 31:'Failed/stale Casey-query intent: JPEG is byte-identical to030 and does not show Casey. No claimed successful search, eligibility filter or selection.'}
LIMITS={
 1:'Only open department menu foreground; no background-role operation. Stations & Groups/Types are actual launchers.',
 2:'Six original groups/types/parents/member counts, read only. Dispatch/message columns are local generated aliases, not delivery evidence.',
 3:'Blank Organizational default and empty member/admin selectors; no printer configuration.',
 4:'Prepared own root name/Organizational/ParentNone/empty selectors and SaveGroup. Not stored yet.',
 6:'Fresh saved own root Name/Organizational/ParentNone/empty selectors; PrintCallsOFF. No secondSave.',
 7:'Station selected; physical-location help and address/GPS alternatives. GPS hints partly clipped; no validation error or saved location.',
 8:'Prepared Stationname and own parent. Address unused; Country defaultUnitedStates is not a verified address.',
 9:'Complete typed illustrative pair41.8500,-87.6500, blankW3W, empty people/printer. No deviceGPS/geocode/map proof.',
 10:'Actual SaveGroup with empty member/admin sets. No new membership/admin right/printer selection.',
 11:'Both new full catalog rows,0members, ownStationparentORG; original6 preserved. Edit launchers visible.',
 12:'Fresh saved Stationtype/name/parent/coordinate pair. Disabled type radios; no conversion/update.',
 13:'Fresh saved pair, blankW3W, PrintCallsOFF and empty people. Save visible but not pressed on readback.',
 14:'Existing Unit list and normal NewUnit/UnitStaffing launchers. Bottom seventh unit/count offscreen; no status/timestamp change claim.',
 15:'Blank NewUnit defaults/NoStation/empty roles table and here type link. No unit stored.',
 16:'Actual unit-type catalog/NewUnitType launcher. Existing5type rows read only; unrelated priority content not discussed.',
 17:'Blank new type/default fields and class help. Save clipped/offscreen; use019.',
 18:'Prepared own type Support/StandardActions/Van/no file. Actual greenVan preview is visible; it is a built-in preview, not a custom upload or real map.',
 19:'Actual Van preview and Save fully visible; no custom file. Raw cautious preview note is superseded by independent visible Van inspection.',
 20:'Saved own type full name/DefaultUnitActions/Van row. Class must be read in021, not inferred from this table.',
 21:'Fresh full type name/Support/StandardActions/Van/no custom file. Save belowviewport; no type update.',
 22:'Prepared unit/two seats, required personnel-role name fully readable. Closed Type/Station names truncate; use021/026 for fullType and028 for fullStation.',
 23:'Foreground template gallery only. Security category selector truncates, but card tags SecurityCompanies/readable titles/usebuttons/Close are complete. No Use these roles action.',
 25:'Settled complete prepared2seat form and Save; Type/Station text still truncated. No people assigned; not yet stored.',
 26:'Actual saved unit full name/type/Van glyph. Available is a display, not proof of stored active-state readiness or staffing. Timestamp is not asserted as a stored event.',
 27:'Fresh unit/two seat definitions. Closed Type/Station text clipped; do not promote fullDOM options as visible. No Update.',
 28:'Normal opened Station dropdown shows full selected ownStation/NoStation/Firehouse51; no selection change. Dropdown obscures first seat name; use027 for it.',
 29:'Read-only staffing: Engine51 one configured seat/Herrmann; own2NotOccupied/NotStaffed. FullyStaffed is relative to configured seats, not physical attendance or full operational readiness.',
 30:'Opened own required-seat picker lists visible nonmatching people too; it is NOT a qualification filter. Casey is offscreen. No selection or save. Lower list clipped; do not claim all14visible.',
 32:'Closed lookup,8selected values unchanged according to retained parent audit. No globalSave. No stored timestamp/other backend invariant claim.',
 33:'Actual parent selection includes own unit under childStation; Search clear. Only this parent/one-child case shown, not every arbitrary tree depth.',
 34:'Actual selected childStation shows same saved unit/type; no station reassignment, status action or timestamp persistence claim.',
}
SCENES=[
 ('groups','Inspect groups and their hierarchy',[1,2],['Stations & Groups','Groups','Add New Group','Type','Parent','Members'],
  'Open the department menu and choose Stations and Groups. The table separates each group’s type, parent, and member count. Our fictional Chicago Fire department already has a station and organizational groups beneath it. We will add an empty coordination parent and a separate station beneath that parent. Read the existing rows first so the new exercise is easy to identify and the original memberships remain intact.',
  'Identify the existing parent relationships before adding your own fictional group.'),
 ('org','Prepare an organizational parent',[2,3,4],['Add New Group','Organizational Group','Group Name',ORG,'Parent Group','None'],
  'Choose Add New Group and keep Organizational Group selected. Enter Training Only, Community Coordination, followed by the exercise date. Parent Group remains None, making this a top-level group. Group Admins and Group Users stay empty. These fields describe different membership responsibilities; choosing an administrator is a permission decision. We are preparing a structure, so we do not move a person from an existing group or assign an administrator.',
  'Prepare an empty organizational root with a unique training name and Parent None.'),
 ('org-read','Save and reopen the empty group',[4,6],['Save Group','Edit Group',ORG,'Parent Group','None','Group Admins','Group Users'],
  'Use Save Group. The fresh Edit Group readback retains its full name and Parent None, and displays the Organizational type read-only. Both membership selectors remain empty. The page explains that a person can belong to only one group at a time. When maintaining a populated group, let its existing selections load before saving: the form submits the complete member and administrator selection.',
  'Reopen the saved root and check its type, parent and empty membership.'),
 ('station','Prepare a station under the new parent',[2,7,8],['Add New Group','Station Group','Group Name',STATION,'Parent Group',ORG,'Station Address'],
  'Create another group and select Station Group. Name it Training Only, Community Base, with the exercise date, and choose the new coordination group as its parent. A station requires a physical reference location. The form offers address fields, a coordinate pair, or a what3words address. We will use an explicitly illustrative Chicago coordinate pair. The parent describes the organizational relationship; it does not replace the station’s own location.',
  'Prepare a Station group with your own organizational group as its parent.'),
 ('coordinates','Enter a complete illustrative coordinate pair',[9,10],['Gps Coordinates','41.8500','-87.6500','what3words Address','Group Admins','Group Users','Save Group'],
  'In Gps Coordinates, enter latitude forty-one point eight five and longitude minus eighty-seven point six five. Enter both values together. The street fields are unused and what3words stays blank. This is a typed station reference, not a device-location reading or proof that anyone arrived there. Keep the member and administrator selectors empty and leave printing unconfigured. Use Save Group once after checking the prepared values.',
  'Save the complete fictional pair with no membership or provider setup changes.'),
 ('station-read','Verify the saved station and relationship',[11,12,13],['Group Name',ORG,STATION,'Organizational','Station','Parent','0','Edit','41.8500','-87.6500','Print Calls to Printer'],
  'The returned catalog shows both new groups with zero members. The organizational root has no parent, while the station names that root as its parent. Use the station’s Edit control to check its full name and relationship again. Scroll to verify the saved coordinate pair, blank what3words field, and clear Print Calls to Printer option. This readback checks the particular fields we stored without changing the station type or configuring printing.',
  'Compare the catalog relationship with the station’s reopened name, parent and coordinates.'),
 ('unit-plan','Separate a unit definition from its crew',[14,15],['Units','New Unit','Type','here','Station','No Station','Roles','Add Role','Required Personnel Role'],
  'Open Units and choose New Unit. The form separates Name, Type, Station, and the unit’s role positions. No Station is available, but our exercise will use the station we just created. A role position defines a seat; it does not select the person occupying that seat. Before completing this unit, use the type link to create a distinct training vehicle type that will be recognizable in the unit list.',
  'Identify the type, station and seat-definition controls before creating the unit.'),
 ('type','Create a useful unit type',[15,16,17,18],['here','New Unit Type','Unit Type Name',TYPE,'Class','Support','Standard Actions','Map Icon','Van','No file chosen'],
  'From the Unit Types section, choose New Unit Type. Enter Training Only, Community Response Vehicle. Set Class to Support; the help explains that class is used for reports, defaults, and integrations, separately from the display name. Keep Actions on Standard Actions and choose Van for Map Icon. The optional custom-icon file remains empty. These choices define the new type without changing an existing type or a department status set.',
  'Prepare an own Support type with Standard Actions and the built-in Van icon.'),
 ('type-read','Save the built-in icon and verify the type',[19,20,21],['Preview','Van','Light map','Dark map','Save',TYPE,'Default Unit Actions','Edit','Support','Standard Actions'],
  'The preview now shows the built-in green Van symbol on light and dark backgrounds and in a list. No custom image has been uploaded. Save, then read the new type row in the catalog. It shows the full name, Default Unit Actions, and Van. Open Edit to verify Support, Standard Actions, and the Van choice again. This confirms the type configuration; it is not a demonstration of a vehicle’s live map location.',
  'Verify the saved type’s full name, class, actions and built-in icon.'),
 ('seats','Define two distinct positions',[14,15,22],['New Unit','Name',UNIT,'Type','Station','Add Role','Coordination seat',PERSON_ROLE,'Optional support seat','-- None --','Required?'],
  'Return to New Unit and name the vehicle Training Only, Community Van, with the exercise date. Select the new type and station. Add two positions with different names. Coordination Seat requires the existing Community Response Navigator personnel role, and its Required box is checked. Optional Support Seat has no personnel-role restriction and its Required box is clear. These are the unit’s seat definitions. No person is assigned by creating either row.',
  'Prepare the two seat definitions and compare their personnel-role conditions.'),
 ('templates','Inspect a template without applying it',[22,23,25],['Browse Templates','Unit Role Templates','Security Companies','Security Patrol','Use these roles','Close','Coordination seat','Optional support seat'],
  'Browse Templates opens reusable starting layouts. Here the Security Companies cards show examples such as Security Patrol and Alarm Response Team. Use These Roles would add a template’s positions to the form for review before saving. For this exercise, choose Close instead. The settled unit form still contains our two prepared positions. Inspect a template’s suggested roles deliberately rather than assuming its names or suggested qualifications match your department.',
  'Inspect and close a template, leaving the two prepared positions unchanged.'),
 ('unit-read','Save the unit and reopen its definition',[25,26,27,28],['Save',UNIT,TYPE,'Edit','Coordination seat','Optional support seat','Station',STATION],
  'Use Save on the prepared unit. The returned list shows its full name and training vehicle type. Open Edit and check that both positions and their Required choices remain. Open the Station dropdown to read the complete selected Community Base name; the closed field truncates it. We are verifying the stored definition without pressing Update. The list’s Available display alone does not establish crew readiness or prove a newly recorded status event.',
  'Reopen the saved unit and verify its full station selection and both seat definitions.'),
 ('staffing','Inspect staffing without changing assignments',[26,29,30,32],['Unit Staffing','Engine 51','Christopher Herrmann','Fully Staffed',UNIT,'Not Staffed','Coordination seat','Optional support seat','Not Occupied','Save'],
  'Open Unit Staffing to distinguish positions from assigned people. Engine fifty-one retains Herrmann in its one configured seat. The new van is Not Staffed, and both positions are Not Occupied. Opening a person selector does not itself prove that the listed people hold the required role. We close it without selecting anyone. Save on this page replaces staffing selections across the department, so we leave it untouched and preserve every existing assignment.',
  'Read the new unit’s empty seats and existing crew, then leave without saving staffing.'),
 ('hierarchy','Find the unit through its parent and station',[26,33,34],['All Units',ORG,STATION,UNIT,TYPE,'Showing 1 to 1 of 1 entries'],
  'Finish with the group tree on Units. Expand and select the Community Coordination parent. Its view includes the vehicle assigned to the child Community Base station. Select that station directly and the same unit appears. This demonstrates the saved relationship from organizational parent to station to unit. These tree choices filter the view; they do not move a unit, assign a crew member, or change its status.',
  'Find the saved unit through both its parent group and its station.'),
 ('adapt','Apply the structure across sectors',[34,11],['Group Name',ORG,STATION,UNIT,TYPE],
  'Chicago Fire can separate a coordination structure from a station and its vehicles. Community care and mental health teams can organize operational teams and bases without patient detail. Search and rescue can distinguish coordination groups, staging bases, and resources; security teams can structure patrol resources; wildland teams can organize seasonal bases; and industrial response teams can separate facility groups from response vehicles. In each setting, verify saved relationships and seat requirements, then manage actual staffing as a separate, deliberate operation.',
  'Sketch a fictional parent, station, type and unit suited to your sector before changing real configuration.'),
]
GAPS=['No existing membership/admin assignment, printing/W3W/geocoding/provider-delivery test, deviceGPS or geofence operation.',
 'No validation-error capture was made; blank Station help is not a failed-save demonstration.',
 '005newrow clipped,024transientbackdrop,031staleCasey lookup are excluded.030does not prove qualification filtering, Casey visibility or selection.',
 'Type/Station closed values truncate in022/025/027. FullType is shown018/020/021/026 and fullStation in028; no hiddenDOM literal promoted.',
 'No unit staffing change or globalSave. Parent audit records all8selector values unchanged; no hypothetical qualified/blocked assignment outcome.',
 'Available and Timestamp displays are not evidence of stored active-state readiness, unchanged stored timestamps, actual dispatch or physical presence.',
 'Van preview is actually visible018/019; no custom-icon upload or live map appearance.',
 'No template application, type/unit update, existing object deletion, whole-department hierarchy-depth guarantee or professional qualification claim.']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def prepare(sources=SOURCES,core=CORE):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    for p,h in PINS.items():assert sha(sources/p)==h,'Changed held input: '+str(p)
    source=json.loads((sources/TRACE/'source-evidence.json').read_text())
    runtime=json.loads((sources/TRACE/'runtime-config-and-parent-progress.observed.json').read_text())
    rows={r['path']:r for r in source['files']}
    for r in runtime['additional_source_pins']:rows[r['path']]=r
    # The observed parent/child unit filter is corroborated by these unmodified
    # view/script inputs, added as exact hashes rather than source-code copies.
    for path,digest in EXTRA_SOURCE_PINS.items():
        rows[path]={'repo':'Core','path':path,'sha256':digest,'matches_retained_Core_profile_head':True}
    for r in rows.values():assert sha(core/r['path'])==r['sha256'],r['path']
    source={'Core_profile_head':source['Core_profile_head'],'kind':'read_only_source_identity','files':list(rows.values()),'not_runtime_binary_attestation':True}
    raw=json.loads((sources/RAW).read_text());assert len(raw)==34
    audit=json.loads((sources/STAFFING).read_text());assert audit['before']==audit['after'] and len(audit['before'])==8 and audit['selections_unchanged'] and not audit['global_staffing_save_clicked']
    assert raw[29]['sha256']==raw[30]['sha256'],'Stale031identity changed; review anew.'
    accepted=[];rejected=[]
    for n,r in enumerate(raw,1):
        assert int(r['id'][:3])==n and sha(sources/r['file'])==r['sha256'] and sha(sources/r['dom_file'])==r['dom_sha256']
        assert _image_dimensions(sources/r['file'])==(1434,773)
        labels=list(dict.fromkeys(LABELS.get(n,[])));out=copy.deepcopy(r)
        limit=LIMITS.get(n,EXCLUDED.get(n));assert limit
        out.update(visible_labels=labels,required_labels=labels,visible_field_text=[],visible_controls=[],missing_required_labels=[],
          eligible_for_lesson=n not in EXCLUDED,source_only=True,scope_limit=limit,state=limit,
          url=r['provenance']['url'],captured_at=r['provenance']['captured_at'],visual_review='independent_original_size_actual_pixels_reviewed',
          label_observation_method='All34original1434x773images independently viewed. Only readable foreground pixels retained; all fullDOM streams are hash-bound/privacy-scanned. No hidden options, clipped fullnames or fabricated control rectangles.')
        out['capture_review']={'passed':n not in EXCLUDED,'reviewer':'Codex independent original-size stored-image review','reviewed_at':REVIEWED_AT,
          'sha256':r['sha256'],'controls_sha256':visible_controls_digest([]),'application_visible':True,'no_errors':n not in EXCLUDED,
          'controls_reviewed':True,'controls_fully_visible':n not in EXCLUDED,'controls_unobstructed':n not in EXCLUDED,
          'method':'Fully-visible scope is the manually retained labels/phase, not every rawDOM element or entire page. Raw media/DOM/manifest preserved.'}
        if n in EXCLUDED:out['exclusion_reason']=EXCLUDED[n];rejected.append(out)
        else:accepted.append(out)
    by={int(r['id'][:3]):r for r in accepted}
    sectors={'Chicago Fire':'Separate coordination groups, stations and response vehicles; verify definitions before staffing.',
      'Community care and mental health':'Organize operational teams/bases without patient detail or clinical authorization claims.',
      'Search and rescue':'Distinguish coordination, staging bases and resources.',
      'Security':'Inspect patrol templates and choose deliberate local positions rather than applying them blindly.',
      'Wildland':'Separate seasonal coordination groups, bases and resource types.',
      'Industrial response':'Distinguish facility groups from response vehicles and their seat requirements.'}
    lesson={'id':NAME,'title':'Create groups, stations and a unit with deliberate crew positions','app':'Core','audience':['department administrators','resource coordinators'],
      'summary':'Create an organizational parent, a Station group, a Support unit type and a two-position unit; verify saved relationships, inspect unchanged staffing, and find the unit through the group tree.',
      'prerequisites':['Use a fictional practice department and existing authorized group/unit/type permissions.',
        'Prepare unique training names and an illustrative coordinate pair; preserve all current members and unit crews.',
        'Have the intended personnel role available for the unit position; do not change actual staffing in this exercise.'],
      'sector_examples':sectors,'source_files':[r['path'] for r in source['files']],'scenes':[],
      'candidate_only':True,'export_ready':False,'publication_approved':False,'source_review_required':True,'whole_group_unit_module_complete':False}
    sequence=[]
    for slug,title,numbers,labels,words,practice in SCENES:
        assert set(numbers)<=set(by),slug
        union={v for n in numbers for v in by[n]['visible_labels']}
        assert set(labels)<=union,(slug,set(labels)-union)
        refs=[by[n]['id'] for n in numbers]
        scene={'id':slug,'title':title,'route':by[numbers[0]]['url'].split(':18967')[-1],
          'capture_refs':refs,'required_labels':labels,'narration':words,'practice':practice,
          'capture_intent':'Control-first actual source order; distinguish prepared forms, normal saves, fresh readbacks and read-only selections.',
          'source_limits':[by[n]['scope_limit'] for n in numbers]}
        lesson['scenes'].append(scene);sequence.append({'scene_id':slug,'title':title,'narration':words,
          'screens':[{'capture_id':by[n]['id'],'file':by[n]['file'],'sha256':by[n]['sha256'],
          'required_labels':[x for x in labels if x in by[n]['visible_labels']],'phase':by[n]['scope_limit']} for n in numbers],
          'timing':'untimed source-only candidate; no audio, cue/cut timing or duration estimate'})
    narration='\n\n'.join(r['narration'] for r in lesson['scenes'])+'\n'
    count=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert 900<=count<=1200,count
    scenario={'id':NAME+'-actual-ui-20261028','mode':'Manual normal-UI replay, no automatic writes','executed_by_helper':False,'department_id':51,
      'actual_ids':{'organizational_group':51007,'station_group':51008,'unit_type':51006,'unit':51008},
      'organizational_group':{'name':ORG,'type':'Organizational','parent':None,'members':[],'admins':[]},
      'station_group':{'name':STATION,'type':'Station','parent_name':ORG,'coordinates':['41.8500','-87.6500'],'address_route_used':False,'what3words':None,'printer':None,'members':[],'admins':[]},
      'unit_type':{'name':TYPE,'class':'Support','actions':'Standard Actions','map_icon':'Van','custom_file':None},
      'unit':{'name':UNIT,'type_name':TYPE,'station_name':STATION,'positions':[{'name':'Coordination seat','personnel_role':PERSON_ROLE,'personnel_role_id':51007,'required':True},
        {'name':'Optional support seat','personnel_role':None,'required':False}],'people_assigned':[]},
      'read_only_staffing':{'audit':STAFFING.as_posix(),'sha256':PINS[STAFFING],'eight_selections_unchanged':True,'global_save_clicked':False,'Engine51_ChristopherHerrmann_retained':True},
      'guards':['Read exact names first. If present, reopen/compare rather than duplicate or overwrite. Resolve actual IDs by normalUI; never fabricate returnedIDs.',
        'Preserve existing groups/members/admins, all existing units/types/crew/calls/statuses. No group-member moves, administrator grants or globalstaffingSave.',
        'Use the complete illustrative pair; no GPSpermission, real address, W3W/printer/provider/key setup.',
        'NewUnit configures seats only. Do not treat Available, timestamps, picker options or template suggestions as staffed/qualified/physical-readiness proof.',
        'No timestamp invariance claim: default displayed timestamps may use a clock fallback.',
        'No templateApply, existing-type/unitUpdate, delete, status/staffing or account/security change.'],
      'normal_replay':['Department menu→Stations&Groups→AddNewGroup→ownOrganizational/ParentNone/emptypeople→SaveGroup→freshEdit.',
        'AddNewGroup→Station/ownparent→completeillustrativepair→emptyW3W/printer/people→SaveGroup→catalogandfreshEditname,parent,pair.',
        'Units→NewUnit→typehere→UnitTypes/NewUnitType→ownSupport/StandardActions/Van/nofile→Save→catalog/freshEdit.',
        'NewUnit→ownname/type/station→AddRole twice→CoordinationrequiredownPersonnelRole;OptionalSupportNone→BrowseTemplates/Closewithoutapply→Save.',
        'List→ownEdit→readstored2seats;openStationdropdownfullnamewithoutchangingselection;noUpdate.',
        'UnitStaffing→readEngineHerrmannandown2NotOccupied→open/closepickerwithoutselection→noSave.',
        'Units→clearSearch→selectorganizationalparentandchildStation→sameownunit; no reassignment.'],
      'source_history':'Earlier proposed None/Default/othercoordinates replay and pre-save runtime note remain historical; this package binds actual final choices and stored readbacks.',
      'boundaries':GAPS}
    report={'kind':'bounded_groups_units_source_candidate_review','status':'HOLD for parent full-script review; no freeze or qualification',
      'reviewed_at':REVIEWED_AT,'original_size_images_individually_viewed':34,'dimensions':[1434,773],
      'accepted_sources':len(accepted),'rejected_sources':EXCLUDED,'fullDOM_streams_read_and_privacy_bound':34,'raw_pair_hash_matches':68,
      'scenes':15,'spoken_words':count,'six_sector_spoken_and_companions':True,'cited_source_files':len(source['files']),
      'staffing_audit':{'file':STAFFING.as_posix(),'sha256':PINS[STAFFING],'all8selectedvalues_unchanged':True,'no_globalSave':True},
      'limits':GAPS,'no_app_browser_DB_audio_timing_canonical_readiness_site_target_Git_change':True,
      'raw_bindings':[{k:r[k] for k in ['id','file','sha256','dom_file','dom_sha256']} for r in raw]}
    caps={'app':'Core','kind':'bounded_reviewed_groups_units_sources','source_manifest':RAW.as_posix(),'source_manifest_sha256':PINS[RAW],
      'screenshots':accepted,'rejected_sources':rejected,'source_only':True,'publication_approved':False,'export_ready':False}
    docs={REVIEW:encoded(caps),BASE/'candidate.json':encoded(lesson),BASE/'captures.reviewed.json':encoded(caps),
      BASE/'screen-sequence.json':encoded({'id':NAME,'status':'untimed candidate only','scenes':sequence}),BASE/'narration.txt':narration.encode(),
      BASE/'scenario.json':encoded(scenario),BASE/'source-review.json':encoded(report),BASE/'source-evidence.json':encoded(source)}
    docs[BASE/'source-hashes.json']=encoded({'id':NAME,'status':'Unvoiced source-only candidate',
      'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      'outputs':[{'file':p.as_posix(),'sha256':hashlib.sha256(v).hexdigest()} for p,v in docs.items()],
      'recipe':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},'historical_sources_preserved':True})
    return docs,report
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sources',type=Path,default=SOURCES);p.add_argument('--core-source',type=Path,default=CORE)
    p.add_argument('--check',action='store_true');p.add_argument('--write-source',action='store_true');a=p.parse_args();docs,report=prepare(a.sources.resolve(),a.core_source.resolve())
    for rel,data in docs.items():assert not (a.sources/rel).exists() or (a.sources/rel).read_bytes()==data,'Preserve existing output: '+str(rel)
    if a.write_source:
        for rel,data in docs.items():
            dest=a.sources/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():dest.write_bytes(data)
    print(json.dumps({'passed':True,'source_only':True,'scenes':15,'spoken_words':report['spoken_words'],'accepted_sources':report['accepted_sources'],
      'rejected_sources':3,'source_files':report['cited_source_files'],'files_written':a.write_source,'frozen_or_canonical_or_ready':False}))
if __name__=='__main__':main()
