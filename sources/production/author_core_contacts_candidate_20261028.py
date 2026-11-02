"""Reproduce a source-only Contacts lesson candidate; never publish or freeze it.

Default and --check are read-only. --write-candidate writes only the named
candidate package (or a separate --output-dir), refusing changed existing files.
No browser, application requests, database, credentials, TTS or media rendering.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-contacts-administration'
BASE = Path('expansion/plans/core-contacts-administration-candidate-20261028')
RAW = Path('captures/expansion/core-contacts-20261028/manifest.json')
RAW_SHA = '413fb809c1d9f6e14f1b92ff90029865720770e08e75b5bbfa11c845f3a839f7'
SOURCE_SHA = '0ca20e0f95ce12e305a4e96826761f81acc02c89bb40e193236c60c3ee68e2e8'
REVIEWED_AT = '2026-10-28T20:30:19Z'
CATEGORY = 'Academy Partner Directory'
PERSON_DESCRIPTION = 'TRAINING ONLY - Fictional community partner liaison. Verify current contact details before operational use.'
COMPANY = 'Academy Logistics Desk (fictional)'
COMPANY_DESCRIPTION = 'TRAINING ONLY - Fictional supply and mutual-aid coordination contact.'
ADDRESS = '1000 Training Avenue (fictional)'

# These are independently readable pixel observations, not wholesale DOM labels.
# Reserved synthetic channels are restored only where visibly readable in JPEGs;
# the recorded form DOM deliberately redacts their values and remains unchanged.
LABELS = {
 1: ['Categories', 'Add Category', 'Name', 'Description', 'Color', 'Contacts In Category', 'Last Updated'],
 2: ['Add Category', 'Name', CATEGORY, 'Color', '#0080ff', 'Display On Map', 'Map Icon', 'Default', 'Description', 'Fictional training partners and logistics contacts.', 'Cancel', 'Save'],
 3: ['Categories', CATEGORY, 'Fictional training partners and logistics contacts.', '#0080ff', 'Contacts In Category', '0', 'View', 'Edit'],
 4: ['Add Contact', 'Contact Type', 'Person', 'Location or Company', 'Category', CATEGORY, 'First Name', 'Sylvie', 'Last Name', 'Brett', 'Company\\Location Name', 'Academy Community Partners (fictional)', 'Email Address', 'liaison@example.invalid', 'Cell Phone', '+13125550142'],
 5: ['Other Data', 'Description', PERSON_DESCRIPTION],
 6: ['Contacts', 'New Contact', 'Categories', 'All Contacts', 'No Category Contacts', CATEGORY, 'Search:', 'Brett', 'Sylvie Brett', 'Person', 'View', 'Edit', 'Showing 1 to 1 of 1 entries (filtered from 4 total entries)'],
 7: ['Sylvie Brett', 'Contact Details', 'Name:', 'Type:', 'Person', 'Email:', 'liaison@example.invalid', 'Cell Phone:', '+13125550142', 'Created By:', 'Wallace Boden'],
 8: ['Description', PERSON_DESCRIPTION],
 9: ['Add Contact', 'Contact Type', 'Person', 'Location or Company', 'Category', CATEGORY, 'First Name', 'Last Name', 'Company\\Location Name', COMPANY, 'Email Address', 'logistics@example.invalid'],
 10: ['Office Phone', '+13125550143', 'Other Data', 'Description', COMPANY_DESCRIPTION],
 11: ['Location Info', 'GPS Location', '41.8722', '-87.6524', 'Entrance GPS Location', 'Exit GPS Location'],
 12: ['Physical Address', 'Address', ADDRESS, 'City', 'Chicago', 'State', 'IL', 'Postal Code', '60607', 'Country', 'United States', 'Mailing Address', 'Same as Physical?', 'Cancel', 'Save'],
 13: ['Contacts', 'New Contact', 'Categories', CATEGORY, 'Sylvie Brett', 'Person', COMPANY, 'Location\\Company', 'View', 'Edit', 'Showing 1 to 2 of 2 entries'],
 14: ['Contacts', CATEGORY, 'Search:', 'Logistics', COMPANY, 'Location\\Company', 'View', 'Edit', 'Showing 1 to 1 of 1 entries (filtered from 2 total entries)'],
 16: [COMPANY, 'Contact Details', 'Name:', 'Type:', 'Location\\Company', 'Email:', 'logistics@example.invalid', 'Location Info', 'GPS Location:', '41.8722,-87.6524'],
 17: ['Physical Address', 'Address:', ADDRESS, 'City:', 'Chicago', 'State:', 'IL', 'Postal Code:', '60607', 'Country:', 'United States', 'Description', COMPANY_DESCRIPTION],
 18: ['Edit Contact', 'Contact Type', 'Location or Company', 'Category', CATEGORY, 'Company\\Location Name', COMPANY, 'Email Address', 'logistics@example.invalid'],
 19: ['Company\\Location Name', COMPANY, 'Office Phone', '+13125550143', 'Other Data', 'Description', COMPANY_DESCRIPTION],
 20: ['Physical Address', 'Address', ADDRESS, 'City', 'Chicago', 'State', 'IL', 'Postal Code', '60607', 'Country', 'United States', 'Mailing Address', 'Same as Physical?', 'Cancel', 'Save'],
 21: ['Company\\Location Name', COMPANY, 'Office Phone', '+13125550144', 'Other Data', 'Description', COMPANY_DESCRIPTION],
 23: ['Company\\Location Name', COMPANY, 'Office Phone', '+13125550144', 'Other Data', 'Description', COMPANY_DESCRIPTION],
 24: ['Categories', CATEGORY, 'Fictional training partners and logistics contacts.', '#0080ff', 'Contacts In Category', '2', 'View', 'Edit'],
}
EXCLUDED = {
 15: 'Transient white entry fade obscures the contact content; superseded by stable016/017. No saved-field proof from faded pixels.',
 22: 'Failed Quill replacement shows malformed/truncated attempted text. It did not persist;023 retains the original description. Excluded from successful editing and narration.',
}
LIMITS = {
 4: 'Prepared Person form only; lower Fax/Office and Save are offscreen. Reserved channels restored from actual pixels, not redacted DOM.',
 5: 'Initial Description prepared only;008 proves saved original text. Lower Other Info editor clipped and excluded.',
 7: 'View Category displays numeric0, not the selected category name. Use006/list for named category. No membership/account/recipient or channel-delivery result.',
 9: 'Prepared company identity; blank first/last names visible. Office Phone is below viewport, provided by010.',
 11: 'Complete typed location pair only; entrance/exit pairs blank. No GPS/device location, geocode, map display or navigation proof.',
 12: 'Prepared physical address with Same as Physical checked; mailing fields disabled/blank here.020 later supplies persisted copied values. No real-address verification.',
 16: 'View Category displays numeric1; mailing section blank. Do not promote a named category or mailing text from this View. Read named category in018 and copied mailing values in020.',
 17: 'Physical address and original Description visible; Mailing Address is blank in View. No mailing readback claim here.',
 18: 'Fresh Edit shows the saved named category; Office Phone and addresses are offscreen, provided by019/020.',
 19: 'Fresh Edit before phone change shows0143. No change made in this frame.',
 20: 'Fresh Edit shows copied mailing values; Same as Physical checkbox is clear on reopening. No promise that this checkbox stays checked or that View renders mailing values.',
 21: 'Prepared office-phone0144; persistence is independently read back in023. Save button is offscreen here.',
 23: 'Parent ordinary Save/leave/reopen provenance plus fresh Edit actual0144 verifies the phone change. Full-DOM hash matches021 because credential-like form values are redacted; independent JPEG shows0144. The original description remains, not failed022replacement.',
}

# Each paragraph remains unvoiced and unfrozen until the parent review.
SCENES = [
 ('directory', 'Choose the directory and its categories', [1], ['Categories', 'Add Category', 'Contacts In Category'],
  'Contacts gives your department a shared directory of people, organizations, and locations. Keep member accounts and roster roles in Personnel; use this directory for useful operational references. In our fictional Chicago Fire training department, open Contacts, then Categories. The category table separates its name, description, color, and contact count. It starts empty here, even though the department already has uncategorized contacts. We will create a small partner directory and verify each saved entry.'),
 ('category', 'Create and verify a useful category', [2,3], ['Add Category', 'Name', CATEGORY, 'Color', 'Display On Map', 'Map Icon', 'Default', 'Description', 'Save', 'Contacts In Category', '0'],
  'Choose Add Category. Enter Academy Partner Directory as the Name and describe it as fictional training partners and logistics contacts. Keep the blue color so the category is easy to recognize. Display On Map remains unchecked and Map Icon stays Default. Those controls are separate from organizing the directory. Save, then read the returned category row. Its name, description, and blue color are present, while Contacts In Category is zero. That saved row is our starting point for adding contacts.'),
 ('person', 'Prepare a person and a clear description', [4,5], ['Contact Type', 'Person', 'Category', CATEGORY, 'First Name', 'Sylvie', 'Last Name', 'Brett', 'Email Address', 'Cell Phone', 'Description', PERSON_DESCRIPTION],
  'Return to Contacts and choose New Contact. Select Person, then Academy Partner Directory. Enter Sylvie and Brett in the first and last name fields. The organization field can add context; here it contains Academy Community Partners, marked fictional. Email Address and Cell Phone hold deliberately reserved training values. Scroll to Description and explain the purpose of the entry. Our text identifies a fictional community partner liaison and asks the reader to verify current details before operational use. Keep that description useful and specific.'),
 ('person-readback', 'Find and inspect the saved person', [6,7,8], ['Search:', 'Brett', 'Sylvie Brett', 'Person', CATEGORY, 'View', 'Contact Details', 'liaison@example.invalid', '+13125550142', 'Description', PERSON_DESCRIPTION],
  'After saving the person, use the Contacts table Search field to enter Brett. The result shows Sylvie Brett, the Person type, and the named category. Choose View and check the saved name and training contact channels. Scroll down to read the complete Description again. These separate checks confirm that both the identity and the useful context were stored. To verify category membership, use the named category in the list or the edit form; the Additional Info category value on this View is numeric.'),
 ('company', 'Add a separate organization', [9,10], ['Contact Type', 'Location or Company', 'Category', CATEGORY, 'Company\\Location Name', COMPANY, 'Office Phone', '+13125550143', 'Description', COMPANY_DESCRIPTION],
  'Create a second entry using Location or Company. Keep the same category, leave the person name fields empty, and enter Academy Logistics Desk, marked fictional, in Company Location Name. The organization has its own reserved training email and an Office Phone ending in zero one four three. Its Description explains that it is a fictional supply and mutual-aid coordination contact. Using the appropriate contact type and phone field makes the directory easier to understand when someone else opens the entry.'),
 ('location', 'Enter an explicit reference point and address', [11,12], ['Location Info', 'GPS Location', '41.8722', '-87.6524', 'Entrance GPS Location', 'Exit GPS Location', 'Physical Address', ADDRESS, 'Mailing Address', 'Same as Physical?', 'Save'],
  'In Location Info, GPS Location has a latitude field and a longitude field. Enter the complete fictional Chicago pair together. Entrance GPS Location and Exit GPS Location are separate pairs and stay blank in this exercise. Continue to Physical Address and enter the fictional Training Avenue street, Chicago, Illinois, and postal code. Check Same as Physical under Mailing Address, then use Save at the bottom of the form. These are stored directory reference values; entering coordinates does not establish a device position, a verified entrance, or a successful route.'),
 ('filters', 'Combine the category and text filters', [13,14], [CATEGORY, 'Sylvie Brett', 'Person', COMPANY, 'Location\\Company', 'Showing 1 to 2 of 2 entries', 'Search:', 'Logistics', 'View', 'Edit'],
  'Back in Contacts, select Academy Partner Directory in the category tree. Both newly saved entries appear: the person and the logistics organization. Now enter Logistics in Search. The table narrows the selected category to the organization, and the count says that one result is filtered from two entries. Read the name and type before choosing View or Edit. A short list can reflect the combination of these filters, so check the selected category and search text before deciding that an entry is missing.'),
 ('readback', 'Verify location and copied address on the owning forms', [16,17,18,20], [COMPANY, 'Contact Details', 'GPS Location:', '41.8722,-87.6524', 'Physical Address', ADDRESS, 'Description', COMPANY_DESCRIPTION, 'Edit Contact', CATEGORY, 'Mailing Address', 'Same as Physical?'],
  'Open the saved organization. Contact Details shows its name and email, and Location Info shows the stored coordinate pair. Farther down, verify the physical address and original Description. For the named category and copied mailing address, return to the list and choose Edit. The category is selected by name, and the reopened mailing fields contain the copied street, city, state, and postal code. Same as Physical is clear on reopening here. Check those actual fields rather than assuming the blank mailing section on View proves that nothing was saved.'),
 ('phone-edit', 'Verify a small saved change', [19,21,23], ['Office Phone', '+13125550143', '+13125550144', 'Description', COMPANY_DESCRIPTION],
  'Use a small, easy-to-check edit to confirm your maintenance workflow. In the reopened organization form, Office Phone ends in zero one four three. Change that final digit to four. After saving and reopening the same contact, the field now ends in zero one four four. Read the reopened value, not just the value you typed. The original supply and mutual-aid Description remains in place. A successful change to one field is a reason to verify that field specifically, rather than assume every attempted edit was stored.'),
 ('handover', 'Review the finished directory and adapt it', [24,13], ['Categories', CATEGORY, 'Contacts In Category', '2', 'Sylvie Brett', COMPANY],
  'Finish in Categories. Academy Partner Directory now contains two contacts. Give someone responsibility for reviewing those details as partners change. Chicago Fire can use this pattern for logistics contacts. Community care and mental health teams can maintain operational partner directories without patient detail. Search and rescue can organize staging and support contacts; security teams can group site contacts; wildland crews can maintain supply references; and industrial response teams can organize facility coordination contacts. In each setting, choose clear categories, verify saved values, and keep the directory current.'),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()

def prepare(sources):
    sys.path.insert(0,str(ROOT/'scripts'))
    from verify_capture_evidence import _image_dimensions, visible_controls_digest
    source=sources/BASE/'source-evidence.json'
    assert sha(sources/RAW)==RAW_SHA, 'Raw manifest changed; review a new version.'
    assert sha(source)==SOURCE_SHA, 'Cited source manifest changed.'
    evidence=json.loads(source.read_text())
    for entry in evidence['files']:
        assert sha(sources/entry['retained_file'])==entry['sha256'], entry['path']
    raw=json.loads((sources/RAW).read_text())
    assert isinstance(raw,list) and len(raw)==24
    by_number={int(row['id'][:3]):row for row in raw}
    assert set(by_number)==set(range(1,25))
    reviewed,rejected=[],[]
    for n,row in by_number.items():
        assert sha(sources/row['file'])==row['sha256'],row['id']
        assert sha(sources/row['dom_file'])==row['dom_sha256'],row['id']
        assert _image_dimensions(sources/row['file'])==(row['width'],row['height'])
        labels=LABELS.get(n,[])
        out=copy.deepcopy(row)
        out.update(visible_labels=labels,visible_controls=[],visible_field_text=[],required_labels=labels,
            missing_required_labels=[],visual_review='actual_pixels_and_full_dom_reviewed',
            eligible_for_lesson=n not in EXCLUDED,review_status='visually_reviewed',
            source_only=True,scope_limit=LIMITS.get(n,'Only retained fully readable directory labels and stated phase; no account, dispatch, communication or map result.'),
            label_observation_method='All24 original1434x773 JPEGs independently viewed after two overview sheets; exact visible literals manually retained. FullDOM common bodies and every full-file difference reviewed; all raw DOM/value redactions preserved. No hidden/offscreen literals or raw field geometry promoted.')
        out['url']=row['provenance']['url'];out['captured_at']=row['provenance']['captured_at']
        out['capture_review']={'passed':n not in EXCLUDED,'reviewer':'Codex independent stored-image/full-DOM review','reviewed_at':REVIEWED_AT,
            'sha256':row['sha256'],'controls_sha256':visible_controls_digest([]),'application_visible':True,
            'no_errors':n not in EXCLUDED,'controls_reviewed':True,'controls_fully_visible':n not in EXCLUDED,'controls_unobstructed':n not in EXCLUDED,
            'method':'Original-size pixel inspection and recorded-DOM corroboration, scoped to retained labels. Reserved synthetic email/phone literals and selected values restored manually only when actually readable. No application operation by reviewer.'}
        if n in EXCLUDED:
            out['exclusion_reason']=EXCLUDED[n];rejected.append(out)
        else:
            reviewed.append(out)
    by_id={r['id']:r for r in reviewed}
    sectors={
        'Chicago Fire':'Maintain fictional logistics and mutual-aid coordination contacts in a reviewed category.',
        'Community care and mental health':'Organize operational partners and outreach references without patient or clinical details.',
        'Search and rescue':'Group staging, equipment and support contacts; a saved directory point is not an arrival report.',
        'Security':'Group site and coordination contacts without real client information in a training environment.',
        'Wildland':'Keep supply and assignment support contacts current; verify changes before the next exercise.',
        'Industrial response':'Organize facility coordination and equipment-support contacts with a responsible directory owner.'}
    lesson={'id':NAME,'title':'Create and maintain useful contact categories, people and organizations','app':'Core',
        'audience':['department administrators','dispatchers maintaining an operational directory'],
        'summary':'Create a category, save a person and an organization, verify reference-location and copied-address fields, combine filters, and read back a saved phone change.',
        'prerequisites':['Use your department Contacts permissions and a fictional practice directory.','Prepare reserved training contact channels and a clearly fictional address/location pair.'],
        'sector_examples':sectors,'source_files':[r['retained_file'] for r in evidence['files']],
        'candidate_only':True,'export_ready':False,'publication_approved':False,'scenes':[]}
    sequence=[]
    for slug,title,numbers,labels,narration in SCENES:
        ids=[by_number[n]['id'] for n in numbers]
        assert set(ids)<=set(by_id),slug
        union=set(label for ident in ids for label in by_id[ident]['visible_labels'])
        assert set(labels)<=union,(slug,set(labels)-union)
        scene={'id':slug,'title':title,'route':by_id[ids[0]]['url'].split(':18967')[-1],
            'capture_refs':ids,'capture_intent':'Show the named controls before saved results; use the ordered source frames without implying an unpictured click.',
            'required_labels':labels,'narration':narration,'practice':'Reproduce this step only with a fictional contact you own; leave and reopen to verify stored values.'}
        lesson['scenes'].append(scene)
        sequence.append({'scene_id':slug,'title':title,'screens':[{'capture_id':ident,'sha256':by_id[ident]['sha256'],'file':by_id[ident]['file']} for ident in ids],
            'required_label_union':labels,'narration':narration,'timing':'untimed; no audio, cue times, cuts or duration estimates',
            'source_limits':[by_id[ident]['scope_limit'] for ident in ids]})
    count=len(re.findall(r"\b[\w]+(?:['’\-][\w]+)*\b",' '.join(x['narration'] for x in lesson['scenes'])))
    assert 600<=count<=1100,count
    captures={'app':'Core','kind':'reviewed_source_subset','source_manifest':RAW.as_posix(),'source_manifest_sha256':RAW_SHA,
        'screenshots':reviewed,'rejected_sources':rejected,'source_only':True,'publication_approved':False,'export_ready':False}
    scenario={'schema_version':1,'id':NAME+'-20261028','environment':'Isolated fictional Department51 Firehouse51 only','mode':'Manual UI replay definition; no executable seed or automatic changes',
        'executed_by_helper':False,'actual_parent_capture_manifest':RAW.as_posix(),'actual_parent_capture_manifest_sha256':RAW_SHA,
        'category':{'name':CATEGORY,'description':'Fictional training partners and logistics contacts.','color':'#0080ff','display_on_map':False,'map_icon':'Default'},
        'person':{'type':'Person','first_name':'Sylvie','last_name':'Brett','company_name':'Academy Community Partners (fictional)','category':CATEGORY,'email':'liaison@example.invalid','cell_phone':'+13125550142','description':PERSON_DESCRIPTION},
        'organization':{'type':'Location or Company','name':COMPANY,'category':CATEGORY,'email':'logistics@example.invalid','initial_office_phone':'+13125550143','final_office_phone':'+13125550144','description':COMPANY_DESCRIPTION,
            'location_pair':['41.8722','-87.6524'],'entrance_pair':None,'exit_pair':None,
            'physical_address':{'street':ADDRESS,'city':'Chicago','state':'IL','postal_code':'60607','country':'United States'},'same_as_physical_on_create':True},
        'guards':['Confirm fictional Department51 and required existing Contacts permissions.','Search for exact names/category first; if present reopen and compare instead of creating duplicates or overwriting an unknown row.','Resolve actual returned IDs through normal UI; no fixed IDs, direct endpoint calls or database writes.','Reserved channels are directory values only; never dial/send a message, test delivery or perform geocoding/GPS lookup.','Preserve the three uncategorized baseline contacts, original calls and all unrelated settings.','Initial rich-text description create/readback is demonstrated. Failed022replacement is excluded; do not replay it as success.'],
        'normal_replay':['Contacts→Categories→Add Category→Name/Color/description; keep Display On Map OFF/Map Icon Default→Save→verify count0.','Contacts→New Contact→Person/category/name/training channels/initial Description→Save→Search Brett→View identity and Description.','New Contact→Location or Company/category/name/email/office0143/initial Description→paired GPS fields→physical address→Same as Physical→Save.','Category tree→verify two entries→Search Logistics→View name/location/physical address/Description.','Edit same organization→verify named category/office0143/copied mailing fields; Same as Physical appears clear on reopen.','Change only own Office Phone0143→0144→ordinary Save→leave/reopen→read0144.','Categories→verify contact count2. No delete, notification, real partner contact or protected-data permission operation.'],
        'result_boundaries':{'View_category':'Displays ContactType numeric0/1; verify category name in list/Edit.','View_mailing':'Blank when linked to same physical address; copied values verified only on Edit020.','rich_text_edit':'Attempted replacement022failed and did not persist; original Description retained023.','map':'Stored reference coordinates only; no map or route/GPS/device-location proof.'}}
    report={'kind':'core_contacts_candidate_source_review','status':'parent script/label review required; not frozen or canonical','raw_manifest_sha256':RAW_SHA,'source_evidence_sha256':SOURCE_SHA,
        'original_jpegs_individually_reviewed':24,'full_dom_files_reviewed':24,'dom_review_method':'Read full common bodies001/002/004/006/007/018 and every complete per-file difference; raw24DOMs independently hashed and privacy-scanned.',
        'raw_files':len(list((sources/RAW.parent).glob('*.*'))),'media_dom_hash_matches':48,'reviewed_source_count':22,'rejected':EXCLUDED,
        'scenes':len(SCENES),'spoken_words':count,'audio_or_timing_created':False,'freeze_created':False,'canonical_changed':False,
        'source_correspondence_notes':['Initial person Save button is not pictured; scene4 starts after saving and shows actual persisted result instead of inventing that click.','Company Save is fully visible012; all form labels are read only in their actual scroll view.','Phone change prepared021/result023; no claim that typed text alone proves persistence.','Some reserved form values are redacted in DOM. Their manual labels come from independently viewed actual pixels; generic form value collection is discarded.','015 faded and022failed richtext attempt excluded even though raw metadata requests unsupported success labels.','View category/mailing shortcomings are retained as bounded product behavior, not repaired or reinterpreted.'],
        'source_bindings':[{'id':r['id'],'file':r['file'],'sha256':r['sha256'],'dom_file':r['dom_file'],'dom_sha256':r['dom_sha256']} for r in raw]}
    return {'candidate.json':lesson,'captures.reviewed.json':captures,'screen-sequence.json':{'id':NAME,'status':'untimed candidate only','scenes':sequence},'scenario.json':scenario,'source-review.json':report}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=SOURCES)
    parser.add_argument('--check',action='store_true',help='Read-only input, label-union and candidate-byte verification (default).')
    parser.add_argument('--write-candidate',action='store_true',help='Write only this unqualified candidate package; never canonical lessons.')
    parser.add_argument('--output-dir',type=Path,help='Separate candidate package directory; defaults to the versioned plans directory.')
    args=parser.parse_args()
    output=(args.output_dir or args.sources/BASE).resolve()
    if (args.sources/'expansion/lessons').resolve()==output or (args.sources/'expansion/lessons').resolve() in output.parents:
        raise ValueError('Canonical lesson output is prohibited.')
    docs=prepare(args.sources.resolve())
    planned=[(output/name,encoded(obj)) for name,obj in docs.items()]
    # Check every existing file before creating any output. A differing retained
    # candidate must never leave a partially rewritten package behind.
    for p,payload in planned:
        if p.exists():
            assert p.read_bytes()==payload,'Existing candidate differs; retain it and create a new version: '+str(p)
    for p,payload in planned:
        if not p.exists() and args.write_candidate:
            output.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as stream: stream.write(payload)
    print(json.dumps({'passed':True,'operation':'write unqualified candidate' if args.write_candidate else 'read-only check',
        'id':NAME,'scenes':len(SCENES),'words':docs['source-review.json']['spoken_words'],'reviewed_sources':22,'excluded_sources':2,
        'planned_outputs':[{'file':name,'sha256':hashlib.sha256(encoded(obj)).hexdigest()} for name,obj in docs.items()],
        'canonical_or_publication_mutations':False},indent=2))

if __name__=='__main__':
    main()
