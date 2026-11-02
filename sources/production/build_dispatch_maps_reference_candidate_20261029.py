"""Build a NEW unvoiced Dispatch reference candidate from reviewed real pixels.

Read-only by default; --write-candidate never freezes narration, creates media,
changes a canonical lesson or runs an app/API/browser. Raw sources stay intact.
"""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'sources';APP=ROOT.parents[3]/'Dispatch'
RAW=Path('captures/expansion/dispatch-workspace-reference-20261029')
OUT=S/'expansion/plans/app-dispatch-map-and-site-reference-candidate-20261029'
RAW_SHA='390c8ae576f448aa9af45920cbd0c32c64aac1e43a3ff21769d037eb49e60141'
HEAD='044b1d88b2ce7fc851a7d0b60b94db072f51ebc9'
REVIEW_TIME='2026-10-29T05:55:50Z'
NAME='app-dispatch-map-and-site-reference'
LABELS={
2:['☰','Resgrid Dispatch','Active Calls','Units','Map','Personnel','Notes','Activity Log'],
3:['☰','Menu','Home','Calls','POIs','Map','Personnel','Units','Weather Alerts','Protocols','Contacts','Records','Deployments','Chat','Close Menu'],
4:['Resgrid Dispatch','Chicago','🗂️'],
5:['Map Layers','Show All','Hide All','Academy Staging'],
6:['Map Layers','Show All','Hide All','Academy Staging'],
7:['Resgrid Dispatch','Chicago','🗂️'],
8:['Resgrid Dispatch','Chicago','🗂️'],
9:['Search POIs...','All types','Name (A-Z)','Academy Staging Point','Academy Staging','DESTINATION','TRAINING ONLY - 1000 Training Avenue','Fictional exercise assembly point. No real deployment or access approval.'],
10:['Search POIs...','Academy Staging','Name (A-Z)','Academy Staging Point','DESTINATION','TRAINING ONLY - 1000 Training Avenue','Fictional exercise assembly point. No real deployment or access approval.'],
11:['Staging','Academy Staging','Name (A-Z)','Academy Staging Point','DESTINATION','TRAINING ONLY - 1000 Training Avenue','Fictional exercise assembly point. No real deployment or access approval.'],
13:['Search protocols...','No protocols found','No protocols have been created for your department yet.'],
14:['Search contacts...','Fleet Workshop (fictional)','Training Warehouse (fictional)','Community Centre (fictional)','Sylvie Brett','Academy Logistics Desk (fictional)'],
15:['Warehouse','Training Warehouse (fictional)'],
16:['Contact Details','Training Warehouse (fictional)','Company','Notes','Pre-Plan','Files','Calls','Contact Information','Email','Office Phone','training1@firehouse51.example','312-555-0110'],
17:['Contact Details','Training Warehouse (fictional)','Company','Details','Pre-Plan','Files','Calls','No notes found for this contact','Notes added to this contact will appear here'],
18:['Contact Details','Training Warehouse (fictional)','Company','Details','Notes','Files','Calls','No pre-incident plan has been recorded for this contact.'],
19:['Contact Details','Training Warehouse (fictional)','Company','Details','Notes','Pre-Plan','Calls','No files have been attached to this contact.'],
20:['Contact Details','Training Warehouse (fictional)','Company','Details','Notes','Pre-Plan','Files','Related calls','Calls linked to this contact, plus calls at any occupancy this contact is linked to.','No related calls','No earlier calls were found at this location or with these contacts.'],
21:['☰','Resgrid Dispatch','App Info','App Name','Version','0.0.1','Environment','development','Account','Server','Login Info','Active Unit','None Selected','Sign-in and security','Shared device','Logout','Preferences','Theme','dark'],
22:['Preferences','Theme','dark','Language','Select option','Keep Alive','Support','Help Center','Contact Us','System Status','Privacy Policy','Terms of Service'],
24:['Menu','POIs','Map','Personnel','Units','Weather Alerts','Protocols','Contacts','Records','Deployments','Chat','Assistant','Settings','Close Menu'],
}
LIMITS={
2:'Clean loaded console after normal warning Close. Do not claim any status/staffing/PTT/provider action. Counts are this recording only.',
3:'Upper Menu readable through Chat. Assistant and Settings are offscreen here and are supplied only by024.',
4:'Actual Chicago cartography. Individual overlapping/truncated marker names are excluded; no device GPS claim.',
5:'Foreground layer panel only. Academy Staging switch is visibly enabled. Dimmed background is excluded.',
6:'Foreground layer panel only. Academy Staging switch is visibly disabled after local Hide All. No record deletion.',
7:'Full real Chicago map after local POI-layer hiding. Call/unit markers remain; no backend record changed.',
8:'Full real Chicago map after local Show All restored the blue staging marker. No GPS or native operation.',
9:'Actual empty search/All types/Name(A-Z) and one fictional POI card. No alternate sort outcome demonstrated.',
10:'Actual selected Academy Staging type and same existing card. Filter changes only the local list.',
11:'Actual Staging query and type filter. The Search POIs placeholder is replaced by the value; not retained as a printed label.',
13:'Settled actual empty Protocols result, not a configured procedure or successful filtered query.',
14:'Fictional directory only. Displayed email values are not needed by this lesson; no communication sent.',
15:'Warehouse query and matching fictional contact; search placeholder replaced by value.',
16:'Readable foreground title/contact information only. Selected Details label and physical address are too low contrast and excluded. Lower location/system rows are offscreen. Background directory is excluded.',
17:'Readable foreground Notes empty-state text. Selected Notes label is low contrast and excluded; use016 for the prior readable Notes control.',
18:'Readable foreground pre-plan empty state. Selected Pre-Plan label is low contrast and excluded; use017 for its prior readable control.',
19:'Readable foreground Files empty state. Selected Files label is low contrast and excluded; use018 for its prior readable control.',
20:'Readable foreground related-call scope and empty result. Selected Calls label is low contrast and excluded; use019 for its prior readable control. This is not the active-call list.',
21:'Readable Settings overview; unused truncated loopback URL value is omitted from public label metadata. Login Info/security/server/shared/active-unit controls stayed closed.',
22:'Readable Preferences/Support; actual displayed theme value is dark, not the richer AX choice name. No settings changed, wake-lock result or external support navigation.',
24:'Lower Menu after normal sidebar scroll; Settings and Assistant are in viewport. Home/Calls are above this viewport and excluded.',
}
SOURCES=[
'src/app/(app)/home.web.tsx','src/app/(app)/map.web.tsx','src/app/(app)/map.tsx','src/app/(app)/pois.tsx','src/app/(app)/contacts.tsx','src/app/(app)/protocols.tsx','src/app/(app)/settings.tsx','src/components/sidebar/side-menu.tsx','src/components/pois/poi-card.tsx','src/components/pois/poi-detail-screen.tsx','src/components/contacts/contact-details-sheet.tsx','src/components/contacts/contact-notes-list.tsx','src/components/contacts/contact-preplan-panel.tsx','src/components/contacts/contact-files-panel.tsx','src/components/calls/location-history-panel.tsx','src/lib/poi-display.ts','src/lib/poi-map-layers.ts','src/hooks/use-map-layers.ts','src/hooks/use-active-map-layers.ts','src/api/mapping/mapping.ts','src/api/contacts/contacts.ts','src/api/contacts/contactNotes.ts','src/api/contacts/contactPreplans.ts','src/api/contacts/contactFiles.ts','src/api/contacts/contactCallHistory.ts','src/translations/en.json']

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def encoded(data):return (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode()
def scene(id,title,route,ids,labels,narration,practice):
 return {'id':id,'title':title,'route':route,'capture_refs':ids,'required_labels':labels,'narration':narration,'practice':practice}

def build():
 assert sha(S/RAW/'manifest.json')==RAW_SHA,'Changed raw capture manifest.'
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=APP,text=True).strip()==HEAD,'Changed Dispatch source revision.'
 sys.path.insert(0,str(ROOT/'scripts'))
 from verify_capture_evidence import _image_dimensions
 raw=json.loads((S/RAW/'manifest.json').read_text());by_number={int(r['id'][:3]):r for r in raw['screenshots']};assert len(by_number)==24
 source_manifest=json.loads((S/'evidence/expansion/source-manifest.json').read_text());pinned={r['path']:r for r in source_manifest['files'] if r['repo']=='Dispatch'}
 code=[]
 for name in SOURCES:
  path=APP/name;assert path.is_file(),name
  digest=sha(path);p=pinned.get(name)
  if p:assert digest==p['source_sha256'],'Changed retained source: '+name
  code.append({'path':name,'sha256':digest,'retained_profile_match':True if p else None})
 accepted=[];reviews=[]
 for number,row in by_number.items():
  image=S/row['file'];dom=S/row['dom_file'];assert sha(image)==row['sha256'] and sha(dom)==row['dom_sha256'];assert _image_dimensions(image)==(1434,773)
  if number not in LABELS:
   reason={1:'Development warning visible; superseded by clean002.',12:'POI detail address/type/note have insufficient contrast and lower fields are clipped. Excluded from operational detail proof.',23:'Map popup title/address are white-on-white; AX content is not readable pixel proof. Only coordinates are legible, so the named-popup operation is excluded.'}[number]
   reviews.append({'id':row['id'],'sha256':row['sha256'],'eligible_for_lesson':False,'observation':reason});continue
  retained=deepcopy(row);retained['visible_labels']=LABELS[number];retained['visible_controls']=[]
  retained['eligible_for_lesson']=True;retained['review_status']='actual_foreground_pixels_reviewed_for_bounded_reference_scope';retained['source_observation_limits']=LIMITS[number]
  retained['raw_label_differences']={'added_from_actual_pixels':[x for x in LABELS[number] if x not in row['visible_labels']],'excluded_from_scope':[x for x in row['visible_labels'] if x not in LABELS[number]]}
  retained['capture_review']={'passed':True,'reviewer':'Codex dispatch_ic_coverage actual Dispatch source-image reviewer','reviewed_at':REVIEW_TIME,'sha256':row['sha256'],'controls_sha256':hashlib.sha256(b'[]').hexdigest(),'application_visible':True,'no_errors':True,'controls_reviewed':True,'controls_fully_visible':True,'controls_unobstructed':True,
    'method':'Personally viewed each of the24 unchanged1434x773 JPEGs through view_image at full tool display. Only readable in-viewport foreground labels are retained. No100-percent manual pixel inspection is asserted. Placeholder/input values and canvas Chicago text are literal manual observations where the raw DOM collector omitted them. Selected low-contrast tab labels, obscured background, clipped/offscreen fields and unused URL values are excluded. No metadata authenticates pixels or provider/device results.'}
  accepted.append(retained);reviews.append({'id':row['id'],'sha256':row['sha256'],'eligible_for_lesson':True,'observation':LIMITS[number]})
 ids=lambda numbers:[by_number[n]['id'] for n in numbers]
 scenes=[
 scene('01','Start from the dispatch workspace','/home → Menu',ids([2,3]),['Resgrid Dispatch','Active Calls','Map','Notes','Menu','POIs','Contacts'],
 'Dispatch brings calls, apparatus, personnel, a map, and reference notes into one workspace. This lesson follows a read-only reference check in a fictional training department. From Home, open the menu in the upper-left corner. Map, POIs, Protocols, and Contacts lead to different kinds of information. Choose the reference that answers your question before changing a call or assigning resources. We will use the map and site records without making a dispatch.',
 'Find Map, POIs, Protocols and Contacts in the menu before opening a reference page.'),
 scene('02','Use layers to simplify the map','/map',ids([4,5,6,7,6,8]),['Chicago','🗂️','Map Layers','Academy Staging','Hide All','Show All'],
 'Open Map for a larger view of the Chicago training area. The folder control in the lower-left corner opens Map Layers. Academy Staging is enabled in this example. Choose Hide All and inspect the changed layer switch, then close the panel to compare the map. The blue staging point disappears while the other incident and unit markers remain. Reopen the panel and choose Show All to restore the layer. These controls change what this map displays; they do not delete the point or dispatch a resource.',
 'Compare the enabled and disabled layer views, then restore the original visible layers.'),
 scene('03','Find a known point in the POI list','/pois',ids([3,9,10,11]),['POIs','Search POIs...','All types','Academy Staging','Staging','Academy Staging Point'],
 'For a named reference, choose POIs from the menu. The list starts with All types and Name, A to Z. Select Academy Staging in the type selector, then enter Staging in Search POIs. The existing Academy Staging Point remains in the result. A type filter and a search work together, so check both when a point seems missing. This example has only one point; it does not demonstrate a change in sorting order.',
 'Locate the staging point by its displayed type and name. Keep a filtered list separate from the full department catalog.'),
 scene('04','Read the point as a stored reference','/pois',ids([11]),['Academy Staging Point','Academy Staging','DESTINATION','TRAINING ONLY - 1000 Training Avenue','Fictional exercise assembly point. No real deployment or access approval.'],
 'Read the card before using its location. It identifies Academy Staging Point, its Academy Staging type, a Destination badge, and a clearly marked training address. The note calls it a fictional exercise assembly point and says it provides no real deployment or access approval. Use those stored details to confirm you found the intended reference. A point on this map is not evidence that a device reported its position or that a crew reached the site.',
 'Check the point name, type, training address and note together rather than relying on its map symbol alone.'),
 scene('05','Check whether a protocol is available','/protocols',ids([3,13]),['Protocols','Search protocols...','No protocols found','No protocols have been created for your department yet.'],
 'Protocols is a separate menu entry for departmental procedures. Here the page says No protocols found and explains that none have been created for the department. That is the available information for this exercise. There is no procedure to open or follow in this recording. Treat an empty reference page as something to resolve through your authorized departmental process, rather than assuming the app supplied the missing instructions.',
 'Read the empty-state message and distinguish an unconfigured protocol list from an available procedure.'),
 scene('06','Find and identify the site contact','/contacts',ids([3,14,15,16]),['Contacts','Search contacts...','Warehouse','Training Warehouse (fictional)','Contact Details','Company','Contact Information','Email','Office Phone'],
 'Open Contacts to find the site record. Enter Warehouse in Search contacts, then open Training Warehouse, marked fictional. Contact Details keeps that name and the Company category above its reference tabs. The Contact Information section shows an email address and office phone for this training record. Confirm the identity before reading further; a similar place name is not enough. We inspect the stored reference here without calling, emailing, opening an address link, or changing the contact.',
 'Find the fictional warehouse and confirm its full name and category before using its supporting tabs.'),
 scene('07','Read supporting context and its gaps','/contacts → Contact Details',ids([16,17,18,19,20]),['Notes','Pre-Plan','Files','Calls','No notes found for this contact','No pre-incident plan has been recorded for this contact.','No files have been attached to this contact.','Related calls','No related calls'],
 'The supporting tabs stay with the same contact. Open Notes: this warehouse has no notes in that tab. Pre-Plan explicitly says that no pre-incident plan has been recorded. Files says that no files have been attached. Check each message rather than assuming a tab contains material because its name is present. Calls opens Related calls, covering calls linked to this contact and calls at its linked occupancies. The example returns No related calls. That result describes this contact query; it does not mean the dispatch console has no active incidents.',
 'Match each reference tab to its actual result. Record a missing reference as missing rather than describing an unshown plan, file or incident history.'),
 scene('08','Locate settings and apply the reference pattern','Menu → /settings',ids([24,21,22]),['Settings','App Info','App Name','Version','Environment','Preferences','Theme','Language','Keep Alive','Support'],
 'Settings is lower in the menu. App Info identifies the app, version, and environment, which helps when requesting support. Scrolling reveals Preferences, including Theme, Language, and Keep Alive, followed by Support links. We leave those settings and links unchanged; this browser view does not prove a device wake lock or native hardware behavior. Apply the same map, point, and contact checks to fire and EMS, community-care or mental-health teams, search and rescue, security, wildland contractors, and industrial teams. The common task is finding the right place and recognizing which reference information is actually available.',
 'Locate the app version and preference controls without changing an account, server or security setting. Choose a sector scenario and identify the references you would need.')]
 sectors=[('fire-ems','Fire and EMS','Use the displayed staging layer and fictional warehouse contact to rehearse a reference check before an exercise, without dispatching apparatus.'),('community-response','Community response and mental-health teams','Use a fictional care-site or assembly point to practice selecting the correct place and recognizing missing contact reference information.'),('search-and-rescue','Search and rescue','Use the point list and layer comparison to rehearse finding a rendezvous reference; no search deployment or physical GPS is demonstrated.'),('security','Security','Identify a fictional site contact and distinguish its stored phone/email information from an actual communication or access authorization.'),('wildland','Wildland','Practice locating a contractor staging reference and checking for an available preplan; the empty tab supplies no field procedure.'),('industrial','Industrial response','Review a fictional assembly point, site contact and explicit missing files/history without treating the reference as a completed response.')]
 candidate={'id':NAME,'title':'Dispatch: map layers and site references','app':'Dispatch','source_only':True,'status':'UNVOICED candidate pending parent whole-script review','audience':['Dispatchers and control-room coordinators','Team members authorized to read department mapping and site references'],'summary':'Use a real map-layer comparison, POI filters and a fictional contact to find reference information and recognize missing records. Locate workspace settings without changing them.','prerequisites':['An existing authorized Dispatch session and permission to view the fictional local department. No sign-in flow is demonstrated.','The already configured Academy Staging layer/point and fictional warehouse contact used in these actual screens.','Only local display/search controls are exercised; original calls and department records remain unchanged.'],'scenes':scenes,'sector_examples':[{'sector':a,'title':b,'scenario':c} for a,b,c in sectors],'source_files':SOURCES,'scope_limits':['This is a bounded browser reference lesson, not complete Dispatch coverage. Published allocation, status/staffing and pending-call lessons remain separate.','Protocol/contact supporting views are actual empty states; no procedure, preplan, attachment, linked call or provider result is invented.','No device location, route provider, communication, active-unit change, account/security/shared/server save or external support action was performed.','Native maps/hardware, Keep Alive effectiveness, offline behavior and provider delivery need separate actual evidence.','POI detail012 and popup023 are excluded because their important text is unreadable; no source styling patch or artificial geography was used.'],'narration_frozen':False,'parent_whole_script_approved':False,'publication_approved':False}
 for s in scenes:
  union={l for r in accepted if r['id'] in s['capture_refs'] for l in r['visible_labels']};assert set(s['required_labels'])<=union,(s['id'],set(s['required_labels'])-union)
  assert all(x in {r['id'] for r in accepted} for x in s['capture_refs'])
 candidate['narration_word_count']=len(' '.join(s['narration'] for s in scenes).split())
 selected=list(dict.fromkeys(x for scene in scenes for x in scene['capture_refs']))
 sequence={'lesson_id':NAME,'source_only':True,'audio_or_timing_assigned':False,'scenes':[{'scene_id':s['id'],'screens':[{'capture_ref':id,'file':by_number[int(id[:3])]['file'],'sha256':by_number[int(id[:3])]['sha256'],'timing':None} for id in s['capture_refs']],'purpose':s['title']} for s in scenes]}
 manifest={'app':'Dispatch','kind':'reviewed_actual_read_only_source_subset','source_manifest':(RAW/'manifest.json').as_posix(),'source_manifest_sha256':RAW_SHA,'reviewed_at':REVIEW_TIME,'screenshots':[r for r in accepted if r['id'] in selected],'unused_reviewed_source_ids':[r['id'] for r in accepted if r['id'] not in selected],'publication_approved':False,'raw_files_modified':False}
 review={'kind':'all24_actual_source_pixel_and_scope_review','reviewer':'Codex dispatch_ic_coverage','reviewed_at':REVIEW_TIME,'method':'All24 unchanged1434x773 JPEG originals were personally displayed through view_image. No100-percent manual pixel inspection asserted. Metadata alone is not pixel proof.','observations':reviews,'pixel_privacy':'No filled credentials, authentication identifiers, private keys or token values were visible in the inspected JPEGs. Contact emails/phone/address are expressly fictional training references; no communication occurred.','dom_privacy':'DOM receipts replace token-shaped values before storage; an early AX tool read exposed the Mapbox feedback URL, after which all AX output was redacted. No unredacted token was written into this capture batch.','selected_contact_tabs':'Low-contrast selected tab labels are excluded. The preceding screenshot provides the readable unselected control; the next supplies the actual foreground result. Future cue timing must respect that order.','browser_ownership':{'family':'Chrome','browser_id':'3','tab_id':'393909008','ownership':'NEW dedicated agent-created tab','final_url':'http://localhost:19101/home','handoff':True},'capture_actions_read_only':True,'no_canonical_site_target_or_audio_changes':True}
 evidence={'app':'Dispatch','git_revision':HEAD,'source_profile':'evidence/expansion/source-manifest.json','source_profile_sha256':sha(S/'evidence/expansion/source-manifest.json'),'files':code,'no_source_changes':True}
 api={'kind':'source_only_endpoint_correspondence_no_direct_requests','read_paths':['/Mapping/GetMapDataAndMarkers','/Mapping/GetMayLayers','/Mapping/GetPoiTypes','/Mapping/GetPois','/Contacts/GetAllContacts','/Contacts/GetContactById','/Contacts/GetContactNotesByContactId','/Contacts/GetContactPreplan','/ContactFiles/GetFilesForContact','/Contacts/GetContactCallHistory'],'view_only_actions':['Map local Hide All / Show All','POI local type and text filter','Contact local text search and read-only tabs','Settings scroll/inspection only'],'not_performed':['All record writes','All auth/storage/credential inspection','All provider communications and permission requests']}
 assets={NAME+'.candidate.json':encoded(candidate),'narration.txt':('\n\n'.join(s['narration'] for s in scenes)+'\n').encode(),'captures.reviewed.json':encoded(manifest),'screen-sequence.untimed.json':encoded(sequence),'literal-source-review.json':encoded(review),'source-evidence.json':encoded(evidence),'api-and-scope.json':encoded(api)}
 return candidate,assets

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write-candidate',action='store_true');args=p.parse_args();candidate,assets=build()
 if args.write_candidate:
  assert not OUT.exists(),'New-only candidate; preserve prior work.';OUT.mkdir(parents=True)
  for name,body in assets.items():
   with (OUT/name).open('xb') as f:f.write(body)
  spec=importlib.util.spec_from_file_location('unchanged_privacy',ROOT/'scripts/audit_public_repo.py');privacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(privacy)
  files=list((S/RAW).glob('*'))+list(OUT.iterdir())+[Path(__file__)];findings=[];hashed=[]
  for file in files:
   if not file.is_file():continue
   with file.open('rb') as stream:rules=privacy.scan_stream(stream)
   findings.extend({'file':file.relative_to(S).as_posix(),'rule':r} for r in rules);hashed.append({'file':file.relative_to(S).as_posix(),'sha256':sha(file)})
  report={'kind':'source_only_Dispatch_candidate_preflight','scenes':len(candidate['scenes']),'narration_words':candidate['narration_word_count'],'all_raw_images_personally_reviewed':24,'selected_source_images':len(json.loads(assets['captures.reviewed.json'])['screenshots']),'untimed_spans':sum(len(s['screens']) for s in json.loads(assets['screen-sequence.untimed.json'])['scenes']),'source_script_helper_sha256':sha(__file__),'hashes':hashed,'general_pattern_privacy':{'files':len(hashed),'known_private_values_checked':0,'findings':findings,'limit':'No credential file was read; parent may run its separately authorized known-value audit before freeze/public installation.'},'narration_frozen':False,'parent_review_pending':True,'rendered':False,'publication_approved':False}
  assert not findings,findings
  (OUT/'preflight.json').write_bytes(encoded(report))
 print(json.dumps({'source_preflight':True,'output':str(OUT),'scenes':len(candidate['scenes']),'narration_words':candidate['narration_word_count'],'files_written':args.write_candidate,'audio_or_timing_assigned':False,'canonical_ready_changed':False}))

if __name__=='__main__':main()
