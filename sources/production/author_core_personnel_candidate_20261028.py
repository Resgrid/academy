"""Reproduce a bounded, source-only Personnel roles/requirements candidate.

Default/--check is read-only; --write-source retains new named source artifacts
only and refuses changed existing output. No browser, DB, app, canonical lesson,
freeze, audio, timing, readiness, website, target or Git operation.
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
SOURCES=ROOT/'sources'
CORE=ROOT.parents[2]
NAME='core-personnel-administration'
BASE=Path('expansion/plans/core-personnel-administration-candidate-20261028')
RAW=Path('captures/expansion/core-personnel-administration-20261028/manifest.json')
REVIEW=Path('captures/expansion/core-personnel-administration-20261028-reviewed/manifest.json')
ROLE_TRACE=Path('expansion/plans/core-personnel-role-requirements-source-trace-20261028')
PROFILE_TRACE=Path('expansion/plans/core-personnel-role-assignment-width-source-trace-20261028')
PROFILE_AUDIT=Path('expansion/audits/core-personnel-role-profile-readback-20261028.json')
PINS={RAW:'bc40abcc3cba9f8a193b7d9b2a646e1a9c691ae795bc7857ec4f5ddbe3a09192',
 PROFILE_AUDIT:'6e5a114bc7d3c3ca36e8c1712640dc497da69caa1b5135103b2e9d08319cef1f',
 ROLE_TRACE/'source-evidence.json':'2dc805f642035b75ba5004b2d991d5a7ce6b00e022c5d3ffa5c511edd9a96a09',
 ROLE_TRACE/'source-trace.json':'a3800de73f400864f51c2578b9077d7898278ee4f024044cea47db17f932e430',
 PROFILE_TRACE/'source-evidence.json':'2780d62936b637e290779bf16d84c683ae4f9d8a4686a0a2892d0eb248e3e704',
 PROFILE_TRACE/'source-trace.json':'50e0c0a69d8f82c45990f225b565f9cd6e852ff6b98a17dcd8f3486f01faf50a'}
EXTRA_SOURCE_PINS={
 'Web/Resgrid.Web/Areas/User/Views/Personnel/AddRole.cshtml':'edd382667208a3ff558c8b977830b85b49b6e0a6b4ba2f519b695629e7a23ee3',
 'Web/Resgrid.Web/Areas/User/Views/Personnel/ViewRole.cshtml':'42b50092fc3de6d91726e4749fbfc37f5665853da713d9f29c70f53e2ba13d42',
 'Web/Resgrid.Web/Areas/User/Models/Personnel/AddRoleModel.cs':'d1197b76fe05ddb4e4fc286fe84944fa224f540c0a9a3f269cd75e7cfcfc26dd',
 'Web/Resgrid.Web/Areas/User/Models/Personnel/EditRoleModel.cs':'c4870e3b2f8e4223769ddebc8f3a93d2336e7e9fce4acddc12e6e7cf7ae240ab'}
REVIEWED_AT='2026-10-28T23:34:19Z'
ROLE='TRAINING ONLY - Community response navigator'
DESCRIPTION='Fictional Academy role for community paramedicine and mental health response coordination. Software training only; no professional qualification or system administration privilege.'
TYPE='TRAINING ONLY - Record review 20261028'
CODE='TRN-REVIEW-20261028'
OFF_NOTICE='Enforcement is off: these requirements are informational until a department administrator turns on Warn only or Enforce in Settings'
GROUP_HELP='Rows with the same group number are satisfied by any one of them (EMT or AEMT or Paramedic); leave blank for a stand-alone requirement.'
REQ=['Required certifications','Type','Mandatory','Any-of group','Allow trainee','Grace override (days)',
     '7','Add requirement','Save','Back to roles','Member eligibility',OFF_NOTICE,GROUP_HELP]
CATALOG=['Order','Icon','Name','Description','Users In Role','Chief','Driver / Operator','Firefighter',
         'Officer','Paramedic','Rescue Technician','1','2','3','4','View','Edit','Required certifications','Save order']
LABELS={
 1:['Personnel','Add a Person','Manage Invites','Manage Roles','All Personnel','Ungrouped Personnel',
    'Firehouse 51','Search:','Name','Roles','Staffing','Status','State','Matthew Casey','Officer','On Shift','Standing By','Admin','View','Edit','Set Staffing','Set Status'],
 2:['Personnel Roles','Add Role','Role order:']+CATALOG,
 3:['Add Role','Name','Name of the Role','Description','A description of the role','Custom icon',
    'Choose File','No file chosen','Preview','Light map','Dark map','In a list','No custom icon. Showing the default icon.'],
 4:['Add Role','Name',ROLE,'Description',DESCRIPTION,'Custom icon','Choose File','No file chosen','Preview','Light map','Dark map'],
 5:['Description',DESCRIPTION,'Custom icon','Choose File','No file chosen','Preview','Light map','Dark map',
    'In a list','No custom icon. Showing the default icon.','Cancel','Save'],
 6:CATALOG+[ROLE,DESCRIPTION,'7','0'],
 7:REQ+[ROLE,'Certification types','This role has no members.'],
 8:REQ+[ROLE,'TRAINING ONLY -','This role has no members.'],
 9:REQ+[ROLE,'TRAINING ONLY -','Saved.','This role has no members.'],
 10:REQ+[ROLE,'TRAINING ONLY -','Certification types','This role has no members.'],
 11:['Certification types','Code','Type','Category','Applies to','Validity','Records','Requirements',
     'Driver / operator endorsement','DEMO-CERT-3',CODE,TYPE,'Other','Person','12 months','1','Edit'],
 12:['Edit type','Type',TYPE,'Code',CODE,'A role requirement references this type, so its code can no longer change.',
     'Category','Other','Applies to','Person','Issuing authority','Academy Software Exercise (fictional)',
     'Default validity (months)','12','Never expires','Credit hours per renewal','Requires supervisor verification'],
 13:REQ+[ROLE,'TRAINING ONLY -','Driver / operator','This role has no members.'],
 14:REQ+[ROLE,'TRAINING ONLY -','Driver / operator','1','This role has no members.'],
 15:REQ+[ROLE,'TRAINING ONLY -','This role has no members.'],
 16:['View Role',ROLE,DESCRIPTION],
 19:['Group','Truck 81','Is Group Admin?','Roles','Officer','Emergency Contacts','No emergency contacts have been added.'],
 20:['Group','Truck 81','Is Group Admin?','Roles','Officer','Community','Chief','Rescue Technician',
     'Paramedic','Firefighter','Driver / Operator'],
 21:['Group','Truck 81','Is Group Admin?','Roles','Officer',ROLE],
 22:['Department Settings','User Type','Normal User','Department Admin','Disable User','Hide User','Cancel','Save'],
 23:['Personnel','Manage Roles','Search:','Matthew Casey','Roles','Officer',ROLE,'Staffing','On Shift',
     'Status','Standing By','State','Admin','View','Edit','Showing 1 to 1 of 1 entries (filtered from 14 total entries)'],
 24:['Group','Truck 81','Is Group Admin?','Roles','Officer',ROLE],
 25:['Department Settings','User Type','Normal User','Department Admin','Disable User','Hide User','Cancel','Save'],
 26:['View Role',ROLE,DESCRIPTION,'Matthew Casey'],
 27:REQ+[ROLE,'TRAINING ONLY -','Member','Status','Missing or lapsed','Matthew Casey','Qualified'],
 28:CATALOG+[ROLE,DESCRIPTION,'7'],
}
EXCLUDED={17:'EditRole member picker is only a2px line; no readable selectable member list. Retain as diagnosis only, exclude the learner workflow.',
          18:'Opened picker remains an unreadable narrow vertical line despite DOM option names. No visible member selection or save; exclude all picker-success claims.'}
LIMITS={
 1:'Actual roster launchers and visible Casey row only. Bottom people/count are offscreen; use023 for14total. No invite/person creation/staffing/status action.',
 2:'Six original roles/order/counts and role-order help. Save order was never used; no new map appearance is shown.',
 3:'Blank upper Add Role and default icon preview only. Save is offscreen; lower icon guidance is clipped and excluded.',
 4:'Prepared name/complete Description, empty icon chooser and default previews. Not yet saved; preview labels truncate the long name. Use005 for Save.',
 5:'Complete default-icon preview and Save; Name is above viewport. No icon upload or actual map change.',
 6:'Saved seventh role0members, original6names/order/counts retained. New row View/Required certifications launchers shown. No Save order.',
 7:'Empty new role requirements, explicit no-members message and departmentOff notice; no policy change.',
 8:'Prepared one Type51004 row with MandatoryON/Anyblank/AllowtraineeOFF/grace7. Selected long name is clipped; retain prefix only. Full identity is independently shown011/012, not invented inside this selector.',
 9:'Saved one row/Saved banner/Off/no-members. Long selected type name is clipped; do not promote full option text from DOM.',
 10:'Fresh saved single-rule readback; type text remains clipped. No second save or eligibility outcome.',
 11:'Actual type51004 now1Record/1Requirement with full name/code. This is later than the frozen Certification lesson’s earlier0Requirement image.',
 12:'Actual readonly Code and disabled Person scope. Code help/fullidentity readable. Lower verification help/Active/Save are clipped or offscreen; no type edit.',
 13:'UNSAVED two distinct types, bothMandatoryON and blankAny-of. Driver/type labels are clipped; preserve readable prefixes only. Second row grace blank; original row remains7. No save/person evaluation.',
 14:'UNSAVED bothAny-of1; originalgrace7/secondblank remain. This is an OR-form illustration only, not persisted policy or re-evaluated eligibility.',
 15:'Normal reload discarded local second row/group1; original saved single row/blankgroup/grace7 remains. No Save.',
 16:'Role title/complete Description only; blank table area has no explicit no-members text. Use006/007 for member count/empty-state evidence.',
 19:'Casey’s existing Officer chip loaded; Truck81/GroupAdmin checked are baseline. Account identity/contact fields are outside this image. No edit yet.',
 20:'Normal fullwidth Roles lookup with Community typed and Officer retained. Last new-role option is vertically clipped; do not claim its full text or a completed selection here.021 supplies complete selected chips. No claim the lookup filtered to one result.',
 21:'Prepared full Officer+new-role chips; group/admin baseline unchanged. Save not pictured here and persistence not yet established.',
 22:'Before the one normal full-profile Save: DepartmentAdmin remains selected, DisableOFF/HideOFF; Save fully visible. Roles are above viewport, supplied by021. No privilege toggle was changed.',
 23:'Actual saved roster searchCasey shows both roles, OnShift/StandingBy/Admin and14total. No actual arrival, staffing/status or admin change is inferred.',
 24:'Fresh profile both role chips plusTruck81/GroupAdmin retained. Parent separately compared35selected non-sensitive/non-email/non-role controls; not a comprehensive backend data assertion.',
 25:'Fresh DepartmentAdminON/DisableOFF/HideOFF readback. Save remains untouched on this reopen; no role chips in this viewport.',
 26:'Actual new role View now lists Casey. No other member added or removed; role membership is distinct from actual arrival/qualification.',
 27:'Actual software Qualified for single fictional rule while enforcementOff. No block/removal/warning delivery or professional qualification award. Full selected type text remains clipped.',
 28:'New seventh role1member; original6order/counts unchanged. No icon added/reorder/delete. This is the captured final state only.',
}

SCENES=[
 ('orient','Distinguish roster roles, staffing and status',[1,2],['Personnel','Roles','Staffing','Status','State','Manage Roles','Add Role','Users In Role'],
  'Personnel shows a member’s roles separately from staffing, status, and administrative state. In our fictional Chicago Fire department, Casey begins with Officer, On Shift, Standing By, and Admin. Choose Manage Roles to inspect the catalog. The page lists each role’s description and member count. It also explains how role order chooses an available custom icon for a person’s map pin. We will leave the original six roles and their order unchanged, and add one clearly marked coordination exercise.',
  'Identify Casey’s current role, staffing, status and state before opening Manage Roles.'),
 ('new-role','Give the role a clear operational purpose',[2,3,4],['Add Role','Name',ROLE,'Description',DESCRIPTION,'Custom icon','No file chosen'],
  'Choose Add Role. Enter Training Only, Community Response Navigator as the Name. Use the Description to explain the fictional community paramedicine and mental health coordination exercise. Our description explicitly separates software training from professional qualification and system administration privileges. Custom icon is optional and remains empty. A useful role name tells another administrator what the role is for; its description explains the intended scope before anyone is assigned to it.',
  'Prepare one unique fictional role name and a specific coordination description.'),
 ('save-role','Save the role and verify the empty starting point',[5,6,16],['Preview','Light map','Dark map','In a list','No custom icon. Showing the default icon.','Save',ROLE,'0','View'],
  'The lower form previews the default icon on light and dark backgrounds and in a list. No custom file has been selected. Use Save, then find the new role at the end of the catalog. Users In Role is zero, and the original six rows retain their order and counts. Choose View on the new row to read its stored name and full description. Creating the role has given us a saved definition, but has not yet assigned a member.',
  'Save your own role and verify its name, description and zero-member count.'),
 ('requirement','Save one deliberate certification requirement',[6,7,8,9,10],['Required certifications','Add requirement','Type','Mandatory','Any-of group','Allow trainee','Grace override (days)','7','Save','Saved.','This role has no members.'],
  'From the new role’s row, open Required certifications. The notice says enforcement is Off, and Member eligibility says the role has no members. Add requirement creates a row. Select the fictional record-review type, check Mandatory, leave Any-of group blank, leave Allow trainee clear, and enter seven for Grace override. Save, then reopen the page and read the same single row. The seven-day setting concerns the removal grace calculation if enforcement applies; it does not change a certification record’s expiry.',
  'Save only the new role’s one fictional requirement and confirm the reopened settings.'),
 ('type-lock','Check the referenced type and code lock',[10,11,12],['Certification types',CODE,TYPE,'Records','Requirements','1','Edit','Code','A role requirement references this type, so its code can no longer change.','Applies to','Person'],
  'Choose Certification types to verify the full identity behind the narrow requirement selector. The training review row shows its complete code, one existing record, and now one requirement. Open its Edit control. Code is read-only, and the help explains that a role requirement references this type. Applies to remains locked at Person because a record already uses it. We are inspecting these fields only. Keep the existing record and type settings intact.',
  'Compare the full type code and requirement count, then inspect the locked fields without saving.'),
 ('alternatives','Compare independent rules and alternatives without saving',[10,13,14,15],['Add requirement','Mandatory','Any-of group','Allow trainee','Driver / operator','1','7'],
  'Back on the role’s requirements page, add a second, distinct type for an unsaved comparison. With both Mandatory boxes checked and both group fields blank, the rows express separate requirements: both would be needed. Give both rows group number one, and they become alternatives: either could satisfy that group. This is a form preview, so do not Save. Reloading restores the original single row, blank group, and seven-day override. Saving would replace the stored requirement set; the discarded preview changes none of it.',
  'Preview two distinct rows with blank groups and matching groups, then discard them and verify the saved single rule.'),
 ('member-profile','Open the member editor and preserve the baseline',[1,19],['Matthew Casey','Edit','Group','Truck 81','Is Group Admin?','Roles','Officer'],
  'To assign the role, return to Personnel and use Edit on Casey’s row. In the profile’s Roles field, wait for the existing Officer selection to load. It must remain selected when adding another role. Group is Truck 81 and Is Group Admin is already checked in this fictional account; leave both unchanged. This page contains other profile settings, so keep the exercise focused on the intended additional role rather than changing membership, contact, or administrative options.',
  'Open the intended fictional member and confirm the existing Officer selection and group settings.'),
 ('select-role','Prepare the additional role without replacing Officer',[19,20,21],['Roles','Officer','Community',ROLE,'Group','Truck 81','Is Group Admin?'],
  'Use the profile’s Roles selector for the additional assignment. Community is entered in the lookup, while Officer remains selected. The prepared selection then contains two complete chips: Officer and the new Training Only, Community Response Navigator role. Read both names before saving. This control submits the whole selected role set, so an existing role must remain present if you intend to preserve it. Adding the new chip is preparation; we still need a saved readback.',
  'Prepare exactly Officer plus your new role and verify both complete selected names.'),
 ('profile-save','Save the intended role set with profile settings preserved',[21,22,23],['Roles','Officer',ROLE,'Department Settings','Department Admin','Disable User','Hide User','Save','Matthew Casey','On Shift','Standing By','Admin'],
  'Before saving, compare the unchanged profile controls. Department Admin is already selected, while Disable User and Hide User are clear. We leave them that way. Use the normal Save once. Back in Personnel, search for Matthew Casey. His row now lists Officer and the new coordination role together. Staffing remains On Shift, status remains Standing By, and administrative state still reads Admin. The result is an additional operational role on the same member, not a new staffing or status selection.',
  'Save once and verify the two roster roles alongside the unchanged staffing, status and state.'),
 ('profile-readback','Confirm the stored selection and baseline flags',[23,24,25],['Edit','Group','Truck 81','Is Group Admin?','Roles','Officer',ROLE,'Department Admin','Disable User','Hide User'],
  'Use the member’s Edit control again to check persistence. Both role chips are present in the fresh profile. Truck 81 remains selected and Is Group Admin remains checked. Farther down, Department Admin is still selected, while Disable User and Hide User remain clear. This second visit is read-only. Verify the particular fields involved in your exercise instead of assuming that a typed or selected value was stored. Keep unrelated profile and permission choices unchanged.',
  'Reopen the member and compare both role chips and the visible group and administrative flags.'),
 ('verify-member','Check the role’s actual member and software eligibility',[23,28,26,28,27],['Manage Roles',ROLE,'Users In Role','1','View','Matthew Casey','Required certifications','Member eligibility','Qualified',OFF_NOTICE],
  'Return through Manage Roles. The new role now has one member. Choose its View control to see Casey listed under the stored description. Open Required certifications from that role’s row to inspect Member eligibility. Casey is marked Qualified for this single fictional software rule. The Off notice remains visible: this result does not demonstrate enforcement blocking or removal. Read the rule, the member, and the software result together, and keep professional authorization decisions outside this training exercise.',
  'Cross-check the role’s member count, Casey’s membership and the single-rule software result.'),
 ('adapt','Apply the same careful role workflow across sectors',[28,23],['Users In Role',ROLE,'Matthew Casey','Officer'],
  'Chicago Fire can use this workflow to describe an exercise coordination role. Community care and mental health teams can organize operational responsibilities without patient detail. Search and rescue can distinguish search and support roles; security teams can define site responsibilities; wildland teams can organize seasonal coordination; and industrial response teams can separate staff functions from equipment inspections. In each setting, use clear descriptions, deliberate requirements, and verified membership. Preserve existing assignments and administrative settings, and check saved results before relying on them.',
  'Define one fictional role suited to your sector and identify its intended requirement and membership checks.'),
]

GAPS=[
 'This bounded role/requirement/membership exercise does not demonstrate Add a Person, invitations, account creation, password/reset/MFA, permission-matrix edits, member disable/hide changes, staffing/status changes or roster deletion.',
 'No role order save, icon upload/new map appearance, role rename/delete or removal of a baseline member. Existing6roles/order/counts are preserved in002/028.',
 'Requirement selectors clip long type names; full training type/code are readable only in011/012. Driver selector prefix is readable in013/014; no full option literal is promoted from hidden DOM.',
 '013/014 are unsaved AND/OR form previews only.015 normal reload restores the saved single rule. No saved alternative set or live eligibility recalculation is demonstrated.',
 '017/018 narrow member picker is diagnostic-only and excluded.020 new-role option’s final line is clipped; only lookup text/existing Officer are retained.021 proves complete selected chips;023/024 prove persistence.',
 'Profile Save is a full-profile operation. Parent compared35non-sensitive/non-email/non-role controls with equal before/after hashes; excluded credential/contact-like fields and comprehensive backend invariants are not asserted.',
 'Department/global enforcement remainsOff.027 Qualified is a software evaluation against one fictional rule, not an Enforce gate, role-removal/notification result, or professional qualification.',
 'Earlier Certification freeze0Requirements/editableCode footage predates this new role requirement and remains unchanged historical material.',
]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def encoded(value):return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()

def prepare(sources=SOURCES,core_source=CORE):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions,visible_controls_digest
    for path,digest in PINS.items():assert sha(sources/path)==digest,'Changed held input: '+str(path)
    source_rows={}
    for rel in [ROLE_TRACE/'source-evidence.json',PROFILE_TRACE/'source-evidence.json']:
        for row in json.loads((sources/rel).read_text())['files']:
            if row['path'] in source_rows:assert source_rows[row['path']]['sha256']==row['sha256']
            source_rows[row['path']]={'repo':'Core','path':row['path'],'sha256':row['sha256'],'matches_retained_Core_head':True}
    for path,digest in EXTRA_SOURCE_PINS.items():source_rows[path]={'repo':'Core','path':path,'sha256':digest,'matches_retained_Core_head':True}
    for row in source_rows.values():assert sha(core_source/row['path'])==row['sha256'],row['path']
    source={'kind':'read_only_cited_source_identity','core_head':'6f83872110b0382f2911d099e95d6a4ef7da8315',
      'files':sorted(source_rows.values(),key=lambda r:r['path']),'source_identity_not_runtime_binary_attestation':True,
      'no_application_source_copied_or_modified':True}
    raw=json.loads((sources/RAW).read_text());assert len(raw)==28
    audit=json.loads((sources/PROFILE_AUDIT).read_text())
    assert audit['before_selected_roles']==['51002'] and audit['after_selected_roles']==['51002','51007']
    assert audit['non_role_control_count']==35 and audit['all_compared_non_role_controls_unchanged'] is True
    assert audit['before_non_role_controls_sha256']==audit['after_non_role_controls_sha256']
    accepted,rejected=[],[]
    for n,row in enumerate(raw,1):
        assert int(row['id'][:3])==n
        assert sha(sources/row['file'])==row['sha256'] and sha(sources/row['dom_file'])==row['dom_sha256'],row['id']
        assert _image_dimensions(sources/row['file'])==(1434,773)
        labels=list(dict.fromkeys(LABELS.get(n,[])))
        out=copy.deepcopy(row);out.update(visible_labels=labels,required_labels=labels,visible_controls=[],visible_field_text=[],
          missing_required_labels=[],source_only=True,eligible_for_lesson=n not in EXCLUDED,
          visual_review='independent_actual_original_size_pixels_reviewed',scope_limit=LIMITS.get(n,EXCLUDED.get(n)),
          state=LIMITS.get(n,EXCLUDED.get(n)),url=row['provenance']['url'],captured_at=row['provenance']['captured_at'],
          label_observation_method='Every original1434x773JPEG independently viewed. Only legible foreground labels retained; no clipped long options, hidden DOM values or invented geometry. All raw28fullDOM byte streams are independently hash-bound and privacy-scanned; originals remain unchanged.')
        out['capture_review']={'passed':n not in EXCLUDED,'reviewer':'Codex independent original-size stored-image review','reviewed_at':REVIEWED_AT,
          'sha256':row['sha256'],'controls_sha256':visible_controls_digest([]),'application_visible':True,'no_errors':n not in EXCLUDED,
          'controls_reviewed':True,'controls_fully_visible':n not in EXCLUDED,'controls_unobstructed':n not in EXCLUDED,
          'method':'Fully-visible review applies only to the manually retained foreground labels/phase, not every field or raw DOM option. Raw media/DOM/metadata bytes are preserved.'}
        if n in EXCLUDED:out['exclusion_reason']=EXCLUDED[n];rejected.append(out)
        else:accepted.append(out)
    by={int(r['id'][:3]):r for r in accepted}
    captures={'app':'Core','kind':'bounded_reviewed_personnel_role_sources','source_manifest':RAW.as_posix(),'source_manifest_sha256':PINS[RAW],
      'screenshots':accepted,'rejected_sources':rejected,'source_only':True,'export_ready':False,'publication_approved':False}
    sectors={'Chicago Fire':'Describe an exercise coordination role and verify its saved requirements/membership.',
      'Community care and mental health':'Organize operational coordination without patient details or a claim of clinical authorization.',
      'Search and rescue':'Separate search/support responsibilities and preserve existing assignments.',
      'Security':'Define site responsibilities while keeping administrative permission choices explicit and unchanged.',
      'Wildland':'Maintain seasonal coordination roles with deliberate membership checks.',
      'Industrial response':'Distinguish staff functions from equipment inspections and verify the saved role set.'}
    lesson={'id':NAME,'title':'Create personnel roles, set requirements and verify member assignments','app':'Core',
      'audience':['department administrators','personnel coordinators'],
      'summary':'Create a fictional operational role, save one certification requirement, compare unsaved AND/OR alternatives, preserve a member’s existing role while adding the new one, and verify stored membership and software eligibility.',
      'prerequisites':['Use a fictional practice department with existing authorized personnel-role and certification setup/view permissions.',
        'Prepare a distinct fictional Person certification type and an already reviewed record for the intended fictional member.',
        'Record current member roles/group/admin/status settings; retain them when adding the single exercise role.'],
      'scenes':[],'sector_examples':sectors,'source_files':[r['path'] for r in source['files']],
      'candidate_only':True,'source_review_required':True,'bounded_scope_only':True,'whole_personnel_module_complete':False,
      'export_ready':False,'publication_approved':False}
    sequence=[]
    for slug,title,numbers,labels,narration,practice in SCENES:
        assert set(numbers)<=set(by),slug
        union={label for n in numbers for label in by[n]['visible_labels']}
        assert set(labels)<=union,(slug,set(labels)-union)
        refs=[by[n]['id'] for n in numbers]
        lesson['scenes'].append({'id':slug,'title':title,'route':by[numbers[0]]['url'].split(':18967')[-1],
          'capture_refs':refs,'required_labels':labels,'narration':narration,'practice':practice,
          'capture_intent':'Show the named navigation/controls before prepared values and actual stored results; preserve the distinction between unsaved previews and saves.',
          'source_limits':[by[n]['scope_limit'] for n in numbers]})
        sequence.append({'scene_id':slug,'title':title,'narration':narration,'screens':[
          {'capture_id':by[n]['id'],'file':by[n]['file'],'sha256':by[n]['sha256'],
           'required_labels':[x for x in labels if x in by[n]['visible_labels']],'phase':by[n]['scope_limit']} for n in numbers],
          'timing':'untimed source-only candidate; no audio/cue/cut/duration estimate'})
    narration='\n\n'.join(r['narration'] for r in lesson['scenes'])+'\n'
    words=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",narration));assert 800<=words<=1100,words
    assert len(lesson['scenes'])==12 and len(accepted)==26 and len(rejected)==2
    scenario={'schema_version':1,'id':NAME+'-actual-ui-20261028','mode':'Manual normal-UI replay; no executable seed or automatic writes',
      'executed_by_helper':False,'department_id':51,'capture_manifest':{'file':RAW.as_posix(),'sha256':PINS[RAW]},
      'role':{'actual_returned_id':51007,'name':ROLE,'description':DESCRIPTION,'icon_file':None,'position':7,'members_before':0,'members_after':1},
      'saved_requirement':{'type_id':51004,'type':TYPE,'code':CODE,'mandatory':True,'any_of_group':None,'allow_trainee':False,'grace_override_days':7},
      'discarded_preview':{'second_type':'Driver / operator endorsement (DEMO-CERT-3)','mandatory_both':True,
        'first_groups':[None,None],'second_groups':[1,1],'original_grace':7,'second_grace':None,'saved':False,
        'discard':'Normal reload015 restored saved one row with blank group. No Save in013/014.'},
      'member':{'name':'Matthew Casey','actual_seeded_user_id':'DA25F49E-FEA4-5C8D-82D9-163D7D2023F9',
        'roles_before':[{'id':51002,'name':'Officer'}],'roles_after':[{'id':51002,'name':'Officer'},{'id':51007,'name':ROLE}],
        'group':'Truck 81','group_admin':True,'department_admin':True,'disabled':False,'hidden':False,
        'staffing':'On Shift','status':'Standing By','normal_full_profile_save_count':1},
      'global_enforcement':'Off','observed_software_eligibility':'Qualified for saved single fictional rule',
      'original_role_order_and_counts':[{'name':n,'count':c} for n,c in [('Chief',1),('Driver / Operator',1),('Firefighter',3),('Officer',3),('Paramedic',4),('Rescue Technician',2)]],
      'profile_readback_audit':{'file':PROFILE_AUDIT.as_posix(),'sha256':PINS[PROFILE_AUDIT],
        'compared_controls':35,'before_after_sha256':audit['before_non_role_controls_sha256'],'scope':audit['excluded_fields']},
      'guards':['Use only ordinary existing permissions in isolated fictionalDepartment51; no auth/security/role-policy changes.',
        'Search exact new role/type/record first. If already present, reopen/read rather than duplicate or overwrite an unknown row. Actual returnedIDs are observations, not values to fabricate.',
        'Preserve original6role names/order/counts, existingOfficer membership, all calls/units/member status/staffing and saved globalOff policy.',
        'Use only own new role for requirement save. Do not save the two-row AND/OR preview; a save replaces the entire type set.',
        'For member assignment use the normal Personnel row Edit/profileRoles control, wait for Officer to load, retain it and add only new51007. Exclude unreadable EditRole picker017/018.',
        'Normal profile Save has broad scope; preserve baseline group/admin/disabled/hidden/contact/preferences, perform no password/email/PIN/reset/invite/provider action, and verify visible baseline fields after reopen.',
        'No professional/clinical qualification, Enforce gate, notification-delivery, GPS/arrival or map-change claim.'],
      'normal_replay':['Personnel → Manage Roles → Add Role → own exact Name/Description, empty icon → Save → verify seventh role0members → View name/description.',
        'Own row Required certifications → Add requirement → select actual training type51004 → MandatoryON/Anyblank/AllowtraineeOFF/grace7 → Save → fresh saved readback.',
        'Certification types → read fullcode/1record/1requirement → own Edit → Code readonly/help and Personscope disabled; no changes.',
        'Own requirement Addrequirement → distinctDriver type → bothblank groups forAND → bothgroup1 forOR → NO Save → normalreload → verify originalsingle rule.',
        'Personnel Casey Edit → waitOfficerchip → normal profileRoles lookup/add newrole → verifyOfficer+newrolechips → preserve baselineflags → normalSave once.',
        'Roster searchCasey → bothroles and existingstate/staffing/status → Edit → bothchips/group/adminflags retained; no secondSave.',
        'Manage Roles → newcount1 → View actualCasey → newrowRequiredcertifications → actualQualified for singlefictionalrule/globalOff.']}
    report={'kind':'bounded_personnel_role_source_candidate_review','status':'HOLD for parent script/copy review; not frozen/voiced/canonical',
      'reviewed_at':REVIEWED_AT,'original_size_images_individually_reviewed':28,'dimensions':[1434,773],
      'accepted_sources':26,'rejected_sources':EXCLUDED,'fullDOM_byte_streams_privacy_bound':28,'raw_media_DOM_hash_matches':56,
      'source_file_hashes_verified':len(source['files']),'scenes':12,'spoken_words':words,'six_sector_spoken_and_companions':True,
      'profile_audit':{'file':PROFILE_AUDIT.as_posix(),'sha256':PINS[PROFILE_AUDIT],'compared_controls':35,
        'scope':'Selected non-sensitive/non-email/non-role controls equal; no comprehensive backend field assertion.'},
      'limits':GAPS,'no_app_browser_DB_audio_timing_canonical_readiness_site_target_Git_operation':True,
      'raw_bindings':[{k:r[k] for k in ['id','file','sha256','dom_file','dom_sha256']} for r in raw]}
    docs={REVIEW:encoded(captures),BASE/'candidate.json':encoded(lesson),BASE/'captures.reviewed.json':encoded(captures),
      BASE/'screen-sequence.json':encoded({'id':NAME,'status':'untimed candidate only','scenes':sequence}),
      BASE/'narration.txt':narration.encode(),BASE/'scenario.json':encoded(scenario),BASE/'source-review.json':encoded(report),
      BASE/'source-evidence.json':encoded(source),BASE/'source-trace-links.json':encoded({'role_trace':{'file':(ROLE_TRACE/'source-trace.json').as_posix(),'sha256':PINS[ROLE_TRACE/'source-trace.json']},
        'profile_trace':{'file':(PROFILE_TRACE/'source-trace.json').as_posix(),'sha256':PINS[PROFILE_TRACE/'source-trace.json']},'limits':GAPS})}
    docs[BASE/'source-hashes.json']=encoded({'id':NAME,'status':'Unvoiced source-only candidate; no freeze or publication',
      'inputs':[{'file':p.as_posix(),'sha256':h} for p,h in PINS.items()],
      'outputs':[{'file':p.as_posix(),'sha256':hashlib.sha256(v).hexdigest()} for p,v in docs.items()],
      'helper':{'file':'production/'+Path(__file__).name,'sha256':sha(__file__)},'historical_sources_preserved':True})
    return docs,report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--core-source',type=Path,default=CORE)
    parser.add_argument('--check',action='store_true',help='Read-only verification (default).')
    parser.add_argument('--write-source',action='store_true',help='Write only new named reviewed/candidate source artifacts.')
    args=parser.parse_args();docs,report=prepare(args.sources.resolve(),args.core_source.resolve())
    for rel,data in docs.items():
        path=args.sources/rel
        assert not path.exists() or path.read_bytes()==data,'Preserve existing candidate; choose a new version: '+str(rel)
    if args.write_source:
        for rel,data in docs.items():
            path=args.sources/rel;path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(data)
    print(json.dumps({'passed':True,'source_only':True,'scenes':12,'spoken_words':report['spoken_words'],
      'accepted_sources':26,'rejected_sources':2,'source_files':report['source_file_hashes_verified'],
      'outputs':len(docs),'frozen_or_canonical_or_ready':False,'files_written':args.write_source}))

if __name__=='__main__':main()
