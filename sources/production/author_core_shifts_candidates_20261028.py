"""Retain bounded actual-screen shift authoring candidates; no application calls.

Raw40 JPEG/DOM pairs, all historical lessons and source snapshots remain unchanged.
Default checks inputs only. --write-candidates creates these two candidate packages
and the separate reviewed subset. Neither candidate is a canonical lesson/video.
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
S=ROOT/'sources'
RAW=Path('captures/expansion/core-shifts-administration-20261028')
REVIEW=Path('captures/expansion/core-shifts-administration-20261028-reviewed')
RECURRING=Path('expansion/plans/core-shifts-administration-candidate-20261028')
STATIC=Path('expansion/plans/core-static-workshifts-candidate-20261028')
RAW_SHA='b5ee334f8af8575525ec5141c4c63095c5741372ab60c9222058c6ec988bb502'
SOURCE_SHA='830eb757b05b5cc29a050eff25fc2edf4299b68cf92e96c6e2d7957744b5f7ed'
REVIEWED_AT='2026-10-28T22:09:16Z'
ASSIGNED='TRAINING ONLY - Coverage authoring 20261028'
SIGNUP='TRAINING ONLY - Approval and trade 20261028'
UNIT='TRAINING ONLY - Static demo unit 20261028'
STATIC_NAME='TRAINING ONLY - Static Nov4'
DESCRIPTION='TRAINING ONLY. Fictional scheduling and equipment-window software exercise. No deployment, travel, work, expense, payment or live apparatus-availability claim.'
APPROVAL='Signups and trades need supervisor approval'
LABELS={
1:['Shifts','Your Shifts','On Duty Now','Approvals','Shift Staffing','Recurring Group Shifts','Add Recurring Group Shift','Name','Type','Schedule','Groups','Personnel','A Shift — Firehouse 51','Assigned','Signup','Manual','Approval required','View Calendar','Edit Details','Edit Calendar','Edit Groups','Calendar','Add Static Shift','October 2026'],
2:['New Shift','Start >','Schedule >','Slots >','Personnel >','Finish','Name',ASSIGNED,'Code','TRN28A','Assignment Type','Assigned',APPROVAL,'Color','#93c5fd','Previous','Next'],
3:['Start Time','09:00','End Time','01:00'],
4:['Schedule >','Slots >','Start Time','09:00','End Time','11:00','OCTOBER 2026','NOVEMBER 2026','DECEMBER 2026','JANUARY 2027','4'],
5:['Slots >','Add Group to Shift','Shift Group','Firehouse 51','Shift Roles','Shift Role','Officer','Roles Count','1','Add Role to Group','Remove Role','Remove Group','Previous','Next'],
6:['Personnel >','Non-Group Personnel','Firehouse 51','Matthew Casey','Command','Engine 51','Truck 81','Squad 3','Ambulance 61','Previous','Next'],
7:['Finish','Previous','Click the finish button below to create your new shift.'],
8:['Shifts','Recurring Group Shifts',ASSIGNED,'Assigned','Manual','Groups','Personnel','1','View Calendar','Edit Details','Edit Calendar','Edit Groups'],
9:['Edit Shift Details','Name',ASSIGNED,'Code','TRN28A','Color','#93c5fd','Start Time','09:00','End Time','11:00',APPROVAL,'Non-Group Personnel','Firehouse 51','Matthew Casey'],
10:['Start Time','09:00','End Time','11:00',APPROVAL,'Non-Group Personnel','Firehouse 51','Matthew Casey','Command','Engine 51','Truck 81','Squad 3','Ambulance 61','Cancel','Update Shift'],
11:[ASSIGNED+' Calendar'],
12:[],
13:['Calendar','Add Static Shift','November 2026','Today','Previous','Next','Month','Week','Day',ASSIGNED,'04'],
14:[ASSIGNED,'4 Nov 2026','Shift Day Detail','Type:','Assigned','Status:','Upcoming','Start:','11/04/2026 0900','End:','11/04/2026 1100','Staffing','Fully staffed','Firehouse 51','Role','Required','Needed','Officer','1','0','Roster','Name','Roles','Status','Matthew Casey','Your Status','You are not on this shift day.','Signup for Shift with Firehouse 51','Add person to this day','Add to day'],
15:[ASSIGNED,'4 Nov 2026','Shift Day Detail','Assigned','Upcoming','11/04/2026 0900','11/04/2026 1100','Fully staffed','Firehouse 51','Required','Needed','Officer','1','0','Roster','Matthew Casey','Your Status','Signup for Shift with Firehouse 51'],
16:['Shift Settings','Shift Signup Settings','Allow Signups For Multiple Groups','Allow a member to sign up for multiple shift groups. Review overlaps and local coverage rules separately.','Cancel','Save'],
17:['New Shift','Start >','Name',SIGNUP,'Code','TRN28S','Assignment Type','Signup',APPROVAL,'Color','#a7f3d0','Previous','Next'],
18:['Schedule >','Start Time','09:00','End Time','11:00','NOVEMBER 2026','5','6'],
19:['Slots >','Add Group to Shift','Shift Group','Firehouse 51','Shift Roles','Shift Role','Officer','Roles Count','1','Add Role to Group','Previous','Next'],
20:['Personnel >','Non-Group Personnel','Firehouse 51','Command','Engine 51','Truck 81','Squad 3','Ambulance 61','Previous','Next'],
21:['Finish','Previous','Click the finish button below to create your new shift.'],
22:['Shifts','Recurring Group Shifts',ASSIGNED,SIGNUP,'Approval required','Assigned','Signup','Manual','Groups','Personnel','1','0','View Calendar','Edit Details','Edit Calendar','Edit Groups'],
23:['Edit Shift Details','Name',SIGNUP,'Code','TRN28S','Color','#a7f3d0','Start Time','09:00','End Time','11:00',APPROVAL,'Cancel','Update Shift'],
24:['Edit Shift Calendar','OCTOBER 2026','NOVEMBER 2026','DECEMBER 2026','JANUARY 2027','5','6'],
25:[],
26:[SIGNUP,'5 Nov 2026','Shift Day Detail','Type:','Signup','Status:','Upcoming','Start:','11/05/2026 0900','End:','11/05/2026 1100','Staffing','Open slots: 1','Sign-ups and trades on this shift need supervisor approval.','Firehouse 51','Role','Required','Needed','Officer','1','Roster','Nobody is on this day yet.','Your Status','You are not on this shift day.','Signup for Shift with Firehouse 51'],
27:['New Unit','Name',UNIT,'Type','Engine','Station','No Station','Roles','Role Name','Required Personnel Role','Required?','Cancel','Save'],
28:['Units','New Unit','Unit Staffing','Search:',UNIT,'Engine','Available','View Events','Logs','Map','Edit','Showing 1 to 1 of 1 entries (filtered from 7 total entries)'],
29:['Edit Unit','Name',UNIT,'Type','Engine','Station','No Station','Roles','Role Name','Required Personnel Role','Required?','Cancel','Hardware GPS tracking','Certifications & inspections','Update'],
30:['Description',DESCRIPTION,'Start Date/Time','2026/11/04 09:00','End Date/Time','2026/11/05 09:00','Units','Select units...','Cancel','Create Static Shift'],
31:['Description','Start Date/Time','2026/11/04 09:00','End Date/Time','2026/11/05 09:00','Units','Select units...'],
32:['Description',DESCRIPTION,'Start Date/Time','2026/11/04 09:00','End Date/Time','2026/11/05 09:00','Units',UNIT,'Cancel','Create Static Shift'],
33:['New Static Shift','Name','Color','#fde68a','Description',DESCRIPTION],
34:['New Static Shift','Name',STATIC_NAME,'Color','#fde68a'],
35:['Start Date/Time','2026/11/04 09:00','End Date/Time','2026/11/05 09:00','Units',UNIT,'Cancel','Create Static Shift'],
36:['View Static Shift Day','Edit Static Shift','Delete Static Shift','Shift Day 4 Nov 2026 09:00','Shift Day Detail',STATIC_NAME,DESCRIPTION,'Units',UNIT,'Unit Role'],
37:['Edit Static Shift','Name',STATIC_NAME,'Color','#fde68a','Description',DESCRIPTION,'Start Date/Time','11/4/2026 3:00:00 AM'],
38:['Start Date/Time','11/4/2026 3:00:00 AM','End Date/Time','11/5/2026 3:00:00 AM','Units','Editing a static shift will clear out all assignments or sign-ups for this shift and reassign them based on the new settings. If you have any assignments or sign-ups for this shift they will be removed and the new settings will be applied.','Cancel','Update'],
39:['Shift Approvals','Sign-ups and trades waiting for approval in the groups you supervise. Nobody is on duty for a pending request until it is approved.','Sign-ups waiting for approval','No sign-ups are waiting for approval.','Trades waiting for approval','No trades are waiting for approval.','0'],
40:['On Duty Now','Refresh','On duty as of 10/28/2026 1653. This page refreshes every minute.','A Shift — Firehouse 51','10/28/2026 0800 - 10/29/2026 0800','Fully staffed','Firehouse 51','Nobody on duty','Command','Wallace Boden','Chief','Truck 81','Matthew Casey','Officer','Squad 3','Ambulance 61','Engine 51','Christopher Herrmann'],
}
REJECT={3:'Prepared EndTime was01:00 with open picker; corrected before save in004.',11:'Actual specific calendar widget failed, FullCalendar undefined; diagnostic only.',12:'Poor scroll position clips month/header and own tile; superseded013.',25:'Transient fade/white overlay obscures content; superseded026.',31:'Unit picker still blank; superseded genuine selected-chip032/035.',33:'Long unsaved name clipped; final short name034/036/037. Description unchanged and separately visible030.',37:'Readable product discrepancy diagnostic: Edit shows03:00 instead of prepared09:00; do not teach this as successful update.',38:'Readable product discrepancy diagnostic:03:00 fields, blank Units and assignment-clearing warning; all Static writes stopped.'}
LIMITS={
4:'November4selected; Next below viewport, so no spoken click-on-Next instruction is attached to this picture.',
10:'Update Shift fully legible in actual pixels despite generic raw DOM clipping false-negative; no Update clicked.',
13:'Calendar tile title is truncated. The separate own row above supplies full name;014provides actual dated detail.',
14:'4Nov2026and all role/roster fields readable in actual pixels; generic date-label false-negative corrected here. Fully staffed is relative to one configured Officer slot.',
18:'Upper heading offscreen; both future date cells and09:00/11:00are readable. No saved result until022/024/026.',
24:'November5/6highlights readable; current-day active CSS selector alone is not a selected-date list. Two shared-calendar entries and day51110 independently read back; Nov6childID not opened.',
26:'No member request, pending row, approval, trade or attendance executed. Signupbutton is visible availability only.',
28:'Full resource name wraps in result row; Searchinput text is clipped and is not used as a full-name observation.',
30:'Name/header offscreen; Units blank at this earlier preparation. Description and corrected dates are valid bounded observations only.',
32:'Actual EndDate/Unit chip/Create all fully visible despite raw generic DOM false-negatives. Existing long unsaved name is offscreen.',
34:'Native color picker overlays part of Description. Only unobscured heading/name/color are retained; use030/036for complete Description.',
35:'Native color popup occludes upper Description only. Future dates, own Unit chip and Create are fully readable; Description omitted from this row.',
36:'Saved day shows09:00and unit association, but later Edit disagrees. Does not prove live automatic unit commit/release, filled unit role or successful update.',
40:'Read-only existing current AShift roster,10fictional members. New future shift creation is not physical arrival, live unit crew selection or qualification.',
}
SECTORS={
'Chicago Fire':'A fictional station coverage schedule and a separate software equipment window.',
'Community care and mental health':'Operational team coverage and a service-vehicle support window; no patient detail or clinical conclusions.',
'Search and rescue':'A fictional standby roster and support-equipment schedule; no staging arrival claim.',
'Security':'A fictional site-coverage roster and separate equipment window.',
'Wildland':'A fictional relief schedule and support-resource window; no rest-rule or qualification certification.',
'Industrial response':'A fictional drill-support roster and facility-response equipment schedule; no readiness/work/payment certification.'}

def scene(ident,title,shots,labels,narration,practice):
    return dict(id=ident,title=title,capture_numbers=shots,required_labels=labels,narration=narration,practice=practice)

RECUR_SCENES=[
scene('schedules','Choose the schedule you need',[1],['Recurring Group Shifts','Add Recurring Group Shift','Calendar','Add Static Shift','Your Shifts','On Duty Now'],
"Shifts brings two kinds of scheduling into one place. Recurring Group Shifts organizes people and required roles across dated shift days. Add Static Shift creates a separate fixed window for resources. Start by identifying the work you need to coordinate. In our fictional Chicago Fire department, we will create an assigned personnel schedule, then a separate signup schedule. Your Shifts, On Duty Now, Approvals and Shift Staffing are separate views. A scheduled roster gives you recorded coverage; check current operational information separately.",
'Identify Add Recurring Group Shift and Add Static Shift, then decide which matches your practice task.'),
scene('assigned-start','Name an Assigned shift',[2],['Name','Code','TRN28A','Assignment Type','Assigned','Color',APPROVAL,'Next'],
"Choose Add Recurring Group Shift to open New Shift. Enter a distinctive practice name and the short code T R N twenty-eight A. Assignment Type is Assigned, so the administrator chooses the people for this schedule. Use a light background color because the calendar text is black. The supervisor approval checkbox is clear in this example. That control governs signups and trades; it is not the list of assigned personnel. Review these choices before using Next to open Schedule.",
'Prepare a uniquely named Assigned shift and read its code, color and approval setting before continuing.'),
scene('manual-days','Select a date and both times',[4],['Start Time','09:00','End Time','11:00','NOVEMBER 2026','4','Slots >'],
"Schedule gives you a multi-month date picker and separate Start Time and End Time fields. Our example selects November fourth, twenty twenty-six, from nine to eleven in the morning. Check both displayed times after leaving the fields and confirm the intended date is highlighted. This is a manually selected schedule, even though it appears under Recurring Group Shifts. The wizard shown here does not offer a rotation preset. Once the date and times are correct, continue to the Slots stage.",
'Select one future practice date and verify both time fields after leaving them.'),
scene('minimums','Configure the group and role minimum',[5],['Add Group to Shift','Shift Group','Firehouse 51','Shift Role','Officer','Roles Count','1','Add Role to Group'],
"In Slots, Add Group to Shift adds a group row. Firehouse fifty-one is selected here. Add Role to Group creates a required-role row for that group. Choose Officer and leave Roles Count at one. These values define what coverage the schedule should compare against its roster. Adding a role minimum does not assign a person. Review the group, role and count together, then continue to Personnel. Use the department’s published role conventions when configuring your own coverage requirements.",
'Add one practice group with one existing role and a required count of one.'),
scene('assigned-person','Choose an assigned member',[6],['Personnel >','Non-Group Personnel','Firehouse 51','Matthew Casey','Next'],
"Personnel separates Non-Group Personnel from the individual group pickers. Non-group entries are described as floaters or standbys. In the Firehouse fifty-one picker, choose Matthew Casey. His selected name is visible as a chip. Leave the other group pickers empty for this small exercise. The text explains that assigned people fill role slots according to their group and roles. Verify the selected member under the intended group; selecting a name elsewhere is a different assignment. Use Next when that review is complete.",
'Select one eligible existing practice member under the intended group and verify the visible chip.'),
scene('finish','Submit once and inspect the new row',[7,8],['Finish',ASSIGNED,'Assigned','Manual','Groups','Personnel','Edit Details','Edit Calendar','Edit Groups'],
"The Finish stage contains an instruction and a separate Finish control at the lower right. That lower control creates the schedule. Submit once and read the returned row in Recurring Group Shifts. Our new row says Assigned and Manual, with one group and one person. It offers View Calendar, Edit Details, Edit Calendar and Edit Groups. Those actions inspect different parts of the saved schedule. Confirm the new row before opening an editor or assuming that a prepared wizard has already been stored.",
'Create your own practice schedule once and verify its returned type, schedule mode and counts.'),
scene('verify','Verify the stored fields and dated roster',[9,10,14,15],['TRN28A','09:00','11:00','Matthew Casey','4 Nov 2026','Required','Needed','Officer','1','0','Fully staffed','Roster'],
"Reopen Edit Details to check the stored name, code, light blue color and nine-to-eleven time window. Casey remains selected under Firehouse fifty-one. In the shared calendar, open the November fourth entry. Its day detail is Upcoming and shows the same times. The Officer row says Required one and Needed zero; the roster lists Casey as Assigned. Fully staffed means this configured one-role requirement is filled. It does not establish arrival, qualifications or an apparatus crew assignment. Read the actual role counts behind the summary.",
'Leave and reopen the saved details, then inspect the dated role requirement and named roster.'),
scene('signup','Prepare a separate approval-enabled Signup shift',[17,18,19,20,21],['TRN28S','Assignment Type','Signup',APPROVAL,'09:00','11:00','Officer','Roles Count','1','Personnel >','Finish'],
"For a signup schedule, create a separate practice entry with code T R N twenty-eight S and Assignment Type Signup. Check Signups and trades need supervisor approval. The help says that a signup or trade does not put anyone on duty until a group supervisor approves it. Select November fifth and sixth, using the same morning time window and one required Officer for Firehouse fifty-one. Leave every Personnel picker empty. Members can request their own dates separately. Review Finish and submit this new schedule once.",
'Prepare a separate future Signup schedule with approval enabled and no preassigned people.'),
scene('signup-result','Read the saved Signup day without assuming coverage',[22,23,24,26],['Approval required','TRN28S','Signup','Upcoming','Open slots: 1','Required','Needed','Roster','Nobody is on this day yet.','Signup for Shift with Firehouse 51'],
"The saved row now carries Approval required. Reopen its details and calendar to verify the setting, times and two selected dates. On November fifth, the day detail is Signup and Upcoming. It shows Open slots one, an Officer requirement of one, and Nobody is on this day yet. Your Status says that the current user is not on this day, and a group signup button is available. An empty roster remains unfilled even though the schedule has been created. A member request and its supervisor review are separate operations.",
'Open the saved Signup day and compare Required, Needed and the actual roster before reporting coverage.'),
scene('policy','Review the separate group policy and approval queue',[16,39],['Shift Signup Settings','Allow Signups For Multiple Groups','Shift Approvals','No sign-ups are waiting for approval.','No trades are waiting for approval.'],
"Department Shift Settings has a separate Allow Signups For Multiple Groups option. It is off here and remains unchanged. The help asks you to review overlaps and local coverage rules separately. This department policy is different from the approval checkbox on an individual shift. Open Approvals to review waiting signups and trades in groups you supervise. Both queues are empty in this example. The page states that a pending request does not put anyone on duty until it is approved. An empty queue is not a completed approval.",
'Read the existing multiple-group policy, then distinguish an empty approval queue from an approved request.'),
scene('current-duty','Separate a future roster from current duty',[40],['On Duty Now','A Shift — Firehouse 51','Fully staffed','Wallace Boden','Christopher Herrmann'],
"On Duty Now shows a timestamp and the currently active shift, grouped by assignment. Here the existing A Shift is active, with its recorded members and roles. Our new November dates are future schedules. Keep those two questions separate: who is scheduled on a selected day, and which schedule is active now. The page says it refreshes every minute and also offers Refresh. These are recorded roster views; use the appropriate operational workflow to verify current availability and other information your team needs.",
'Read the current-duty timestamp and compare its active shift with your future practice date.'),
scene('adapt','Apply the same review habit',[1,14],['Recurring Group Shifts','Required','Needed','Roster'],
"Chicago Fire can use this pattern to coordinate station coverage. Community care and mental health teams can schedule operational team coverage without patient detail. Search and rescue can organize standby roles; security teams can coordinate site coverage; wildland crews can plan relief rosters; and industrial response teams can schedule drill support. In every setting, choose the right assignment type, state the group and role requirements clearly, and verify the saved dated roster. Handle member requests, approvals, attendance and trades through their own reviewed steps.",
'Choose one sector scenario and write the group, role, date and saved-result checks your team would use.')]

STATIC_SCENES=[
scene('entry','Open the fixed resource window',[1,13],['Calendar','Add Static Shift'],
"Use Add Static Shift from the shared Shifts calendar when you need a fixed resource window. This is separate from the recurring group schedule used for people and role minimums. Our practice entry will cover November fourth to fifth and use a separate training unit. Start with a clear purpose and an explicit start and end. Keep the entry easy to identify so another administrator can review the resource, date and context before relying on it.",
'Find Add Static Shift and define a fictional resource window before opening the form.'),
scene('resource','Prepare a separate practice resource',[27,28,29],['New Unit','Name',UNIT,'Engine','No Station','Roles','Save'],
"Prepare an identifiable practice unit through New Unit. Here its name says Training Only, Static demo unit, followed by the exercise date. Choose the existing Engine type, leave Station at No Station and keep Roles empty. Save the new entry once, then find and reopen it to verify those choices. The returned unit has the default Available status. This separate software resource lets us demonstrate scheduling without changing another apparatus or its crew. No device position or hardware tracking setup is part of this example.",
'Create and reopen a uniquely named disposable practice unit without adding crew or location data.'),
scene('identity','Use a readable name and calendar color',[34],['New Static Shift','Name',STATIC_NAME,'Color','#fde68a'],
"On New Static Shift, enter Training Only, Static November fourth as the name. The short name stays readable in this form. Choose a light yellow background color. The help reminds you that calendar text is black, so review contrast along with the color itself. A distinctive name and color make the entry easier to recognize when it appears alongside personnel shifts. They are labels for the schedule; they do not change the unit’s operational status.",
'Enter a short practice name and a light calendar background that keeps black text readable.'),
scene('purpose','Give the resource window explicit context',[30],['Description',DESCRIPTION],
"Description is a separate rich-text editor. Explain why the resource window exists and what another reader should verify. This example identifies a fictional scheduling exercise and makes clear that it does not record deployment, travel, work, expense or payment. Keep that context attached to the schedule itself. A useful description tells the next administrator what the entry represents without requiring them to infer its purpose from a color or short name. Review the complete text before creating the entry.",
'Write a software-only description that explains the purpose and limits of your practice window.'),
scene('window','Verify both dates and the selected resource',[32,35],['Start Date/Time','2026/11/04 09:00','End Date/Time','2026/11/05 09:00','Units',UNIT,'Create Static Shift'],
"Set Start Date and Time to November fourth, twenty twenty-six, at nine in the morning, and End Date and Time to November fifth at nine. Check the displayed values after leaving each field; this picker displays a year, month, day and twenty-four-hour time. Under Units, select only the new training unit and verify its visible chip. Read both endpoints and the resource name together before using Create Static Shift. The form’s travel and availability help describes its intended scheduling meaning; verify operational effects separately.",
'Verify the future start and end after leaving the fields, then confirm the one selected practice unit.'),
scene('saved','Inspect the newly saved day',[35,36],['Create Static Shift','View Static Shift Day','Shift Day Detail',STATIC_NAME,'Units',UNIT,'Unit Role'],
"Choose Create Static Shift once. In the shared calendar, open the new entry. View Static Shift Day shows the name, description, November fourth at nine, and the selected training unit. The Unit Role table is empty because this unit has no configured roles or filled positions in the exercise. Read the saved identity and association before making another change. This view demonstrates the created scheduling entry; it does not demonstrate a real deployment or an automatic change to another unit’s availability.",
'Open the saved day and verify its name, description and resource association.'),
scene('readback-stop','Stop when the reopened editor disagrees',[37,38],['Edit Static Shift','Start Date/Time','11/4/2026 3:00:00 AM','End Date/Time','11/5/2026 3:00:00 AM','Units','Update'],
"Reopen Edit Static Shift and compare its values before submitting an update. In this example, the editor shows three in the morning instead of the nine shown on the saved day, and its Units selection is blank. Stop here. Do not submit an editor whose values disagree with the entry you intended to maintain. The visible warning also says that editing clears existing assignments or signups and reapplies the settings. Resolve the discrepancy and review the intended result before attempting an update.",
'Compare saved day and editor values; stop before Update if either the time window or resource selection differs.'),
scene('adapt','Adapt the fixed-window review to your work',[36],['Shift Day Detail',STATIC_NAME,'Units',UNIT],
"Chicago Fire can use a reviewed resource window for a software equipment exercise. Community care and mental health teams can coordinate operational vehicle support without patient information. Search and rescue can schedule support equipment; security teams can identify equipment windows; wildland crews can plan support resources; and industrial response teams can coordinate facility drill equipment. Keep the resource identity, dates and purpose clear. Confirm the saved result and resolve conflicting readbacks before further edits. The surrounding operational decisions still need their own appropriate review.",
'Describe one sector-specific resource window and the saved-value checks required before its next edit.')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
def prepare():
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    assert sha(S/RAW/'manifest.json')==RAW_SHA
    source=json.loads((S/RECURRING/'source-evidence.json').read_text());assert sha(S/RECURRING/'source-evidence.json')==SOURCE_SHA
    for f in source['files']:assert sha(S/f['snapshot_file'])==f['sha256']
    raw=json.loads((S/RAW/'manifest.json').read_text())['captures'];assert len(raw)==40
    records={};accepted=[];rejected=[]
    for original in raw:
        n=int(original['id'][:3]);assert sha(S/original['file'])==original['sha256'] and sha(S/original['dom_file'])==original['dom_sha256']
        assert _image_dimensions(S/original['file'])==(1434,773)
        row=copy.deepcopy(original);row.update(visible_labels=LABELS[n],visible_controls=[],visible_field_text=[],required_labels=LABELS[n],missing_required_labels=[],
          eligible_for_lesson=n not in REJECT,source_only=True,review_status='independent_original_size_pixels_reviewed',visual_review='actual_pixels_reviewed',
          scope_limit=LIMITS.get(n,'Only the readable controls and stated prepared or stored phase are supported; no additional operation or provider delivery inferred.'),
          label_observation_method='Every raw original1434x773JPEG independently viewed. Reviewed metadata retains readable pixels only, correcting generic clipping false-negatives without changing raw image/DOM bytes.')
        row['capture_review']={'passed':n not in REJECT,'reviewer':'Codex independent original-size actual Core image review','reviewed_at':REVIEWED_AT,'sha256':row['sha256'],
          'controls_sha256':visible_controls_digest([]),'application_visible':True,'no_errors':n not in REJECT,'controls_reviewed':True,'controls_fully_visible':n not in REJECT,'controls_unobstructed':n not in REJECT,
          'method':row['scope_limit'] if n not in REJECT else REJECT[n]}
        records[n]=row
        if n in REJECT:row['rejection_reason']=REJECT[n];rejected.append(row)
        else:accepted.append(row)
    manifest={'app':'Core','kind':'bounded_reviewed_actual_shift_sources','source_manifest':(RAW/'manifest.json').as_posix(),'source_manifest_sha256':RAW_SHA,
      'screenshots':accepted,'rejected_sources':rejected,'source_only':True,'publication_approved':False,'export_ready':False}
    outputs={REVIEW/'manifest.json':encoded(manifest)}
    for ident,title,authored,directory,gaps in [
      ('core-shifts-administration','Create assigned and signup shift schedules',RECUR_SCENES,RECURRING,['No actual member signup request, pending→approved/denied decision, trade proposal/finalization or attendance operation.','Specific View Calendar page failed with FullCalendar undefined; the actual shared calendar was used instead.']),
      ('core-static-workshifts','Create a fixed resource window and verify its readback',STATIC_SCENES,STATIC,['Edit readback time disagrees09:00saveddayversus03:00editor; no successful Update can be taught.','Edit Units selector is blank while saveddayhasownunit; no Update/delete performed.','Diagnostic scenes037/038are not eligible renderer input.','No demonstrated automatic live unit commit/release, role fill or operational readiness.'])]:
        scenes=[]
        for item in authored:
            scene=copy.deepcopy(item);nums=scene.pop('capture_numbers');rows=[records[n] for n in nums];union={v for row in rows for v in row['visible_labels']};assert set(scene['required_labels'])<=union,(scene['id'],set(scene['required_labels'])-union)
            scene.update(route=rows[0]['url'].replace('http://127.0.0.1:18967',''),capture_refs=[r['id'] for r in rows],capture_intent='Use these actual prepared controls before the separately observed stored result; preserve each source boundary.',
              source_limits=[r['scope_limit'] for r in rows],renderable=all(r['eligible_for_lesson'] for r in rows))
            scenes.append(scene)
        candidate={'id':ident,'title':title,'app':'Core','audience':['department administrators','shift supervisors'],'summary':'Create small fictional schedules and verify their actual stored values and coverage counts.','prerequisites':['Use a fictional practice department and existing shift create/view/update permissions.','Use existing groups, roles and members; prepare future dates and identifiable practice entries.'],
          'scenes':scenes,'sector_examples':SECTORS,'source_files':[{'repo':f['repo'],'path':f['path']} for f in source['files']],
          'candidate_only':True,'export_ready':False,'publication_approved':False,'source_complete':ident=='core-shifts-administration','bounded_scope_only':True,'whole_module_operations_complete':False,'capture_limitations':gaps}
        narration='\n\n'.join(s['narration'] for s in scenes)+'\n';count=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert 600<=count<=1150,(ident,count)
        sequence={'id':ident,'status':'untimed source candidate; no audio or scene-duration estimates','raw_manifest_sha256':RAW_SHA,'reviewed_manifest':(REVIEW/'manifest.json').as_posix(),
          'scenes':[{'scene_id':s['id'],'title':s['title'],'capture_refs':s['capture_refs'],'required_labels':s['required_labels'],'narration':s['narration'],'renderable':s['renderable'],'timing':'untimed; no speech/cue/transition estimate'} for s in scenes]}
        report={'kind':'bounded_actual_core_shift_source_candidate_review','id':ident,'spoken_words':count,'scenes':len(scenes),'all_six_sectors_in_spoken_outro':True,'parent_script_review_pending':True,'full_module_complete':False,'missing_operations_or_limits':gaps,
          'raw_manifest':{'file':(RAW/'manifest.json').as_posix(),'sha256':RAW_SHA},'source_evidence':{'file':(RECURRING/'source-evidence.json').as_posix(),'sha256':SOURCE_SHA},'source_snapshots':len(source['files']),
          'original_jpegs_reviewed':40,'paired_hashes_matching':80,'retained_eligible_images':len(accepted),'diagnostic_or_rejected_images':len(rejected),'no_canonical_readiness_voice_or_site_changes':True}
        outputs.update({directory/'candidate.json':encoded(candidate),directory/'screen-sequence.json':encoded(sequence),directory/'narration.txt':narration.encode(),directory/'source-review.json':encoded(report)})
    return outputs

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');parser.add_argument('--write-candidates',action='store_true');args=parser.parse_args();outputs=prepare()
    for path,payload in outputs.items():
        target=S/path
        if target.exists():assert target.read_bytes()==payload,'Preserve historical candidate; choose a new version.'
    if args.write_candidates:
        for path,payload in outputs.items():
            target=S/path;target.parent.mkdir(parents=True,exist_ok=True)
            if not target.exists():target.write_bytes(payload)
    print(json.dumps({'source_checked':True,'candidate_packages':2,'outputs':len(outputs),'canonical_ready':False,'rendered':False,'app_mutations_from_helper':False}))

if __name__=='__main__':main()
