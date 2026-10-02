#!/usr/bin/env python3
"""Attach concrete sector adaptations to every Academy lesson and feature brief.

Companions are written guidance. Existing videos are not labeled updated until
their additional narration and playback checks have actually been completed.
"""
import html,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SECTORS=['Community paramedicine and mental health response','Search and rescue','Security companies and departments','Wildland contractors','Industrial emergency response teams']
# Each row describes a configuration scenario, not an asserted legal/clinical capability.
EXAMPLES={
'01-setup-wizard':[
'Choose the appropriate EMS or mobile-crisis operating pack and review visit coverage and notification setup.',
'Choose Search and rescue, then review mapping, training, inventory and deployments.',
'Choose Security and facilities, then review site groups, patrol staffing and activity records.',
'Use the Fire context with Contract workforce mix; review seasonal crews and deployment dates.',
'Choose Industrial response and applicable HazMat context; review facility groups, equipment and qualifications.'],
'02-department-settings':[
'Set the local time zone for scheduled outreach visits; review whether a daily reset would incorrectly mark an occupied response team available.',
'Choose availability reset rules that suit volunteers and overnight searches; avoid implying that a remote volunteer has arrived at staging.',
'Set patrol-day boundaries and display order; review staffing suppression before excluding an off-duty patrol member from alerts.',
'Review reset times across overnight assignments and the deployment time zone before changing contractor crew availability.',
'Align display time with plant shifts and review automatic resets before overwriting a team engaged in an extended incident.'],
'03-custom-statuses':[
'Use labels such as En route to visit and Contact made with appropriate base meanings; include only approved operational notes.',
'Use Searching assigned area with Searching meaning, an incident destination and an accountability note.',
'Use On patrol, Investigating and Made contact with the corresponding base meanings; distinguish availability from patrol activity.',
'Use Staging, Responding and Returning for crew movement; make notes capture the assigned division or staging point.',
'Use Maintenance and Unavailable for defective equipment, and On scene for the response team; a label alone must not imply equipment readiness.'],
'04-personnel':[
'Create operational roles for clinicians and peer responders, then track credentials separately; membership does not establish clinical scope.',
'Use roles such as Search Team Leader and Navigation Specialist; review current qualifications and actual availability before assignment.',
'Use Patrol Officer and Site Supervisor roles; scope group administration to the intended site and reserve department administration for department-wide ownership.',
'Use Crew Leader, Saw Operator and Driver roles; review seasonal roster membership and current credentials before deployment.',
'Use ERT Leader, HazMat Technician and Equipment Operator roles; role labels do not replace qualification review.'],
'05-groups-units':[
'Model response areas or outreach teams as groups and mobile response vehicles as units; define team positions appropriate to the service.',
'Model bases and field teams as groups and search vehicles or boats as units; define team leader and operator positions.',
'Model clients or sites as groups and patrol vehicles as units; check membership before applying site-scoped dispatch.',
'Model bases and crews as groups and engines or support vehicles as units; require the appropriate driver or crew positions.',
'Model facilities or plants as groups and response vehicles or equipment as units; define operators and response-team positions.'],
'06-dispatch-settings':[
'Compare dispatching the scheduled mobile team with dispatching every member of its response-area group; review who should receive a visit alert.',
'Compare alerting the active search shift with paging an entire volunteer group; check crew propagation and excluded unavailable members.',
'Dispatch the on-duty patrol shift or selected site group; review whether assigning a vehicle should also alert its staffed officers.',
'Dispatch the assigned crew and support vehicle; verify that off-assignment contractor personnel are not unintentionally included.',
'Dispatch the on-duty facility team; review department-wide specialist role exceptions before enabling group-scoped recipient selection.'],
'07-run-cards':[
'Create a reviewed response classification for a mobile-team request; specify eligible resource types and leave clinical triage to approved procedures.',
'Use terrain or search classification to recommend a ground team, boat or specialist resource; review location freshness and qualifications.',
'Use site and incident type to recommend a patrol vehicle and supervisor; inspect recommendations before committing recipients.',
'Use assignment type to recommend crew, engine and support resources; review staffing and deployment availability.',
'Use facility and incident class to recommend plant ERT and specialist equipment; inspect coverage and manual exceptions.'],
'08-shifts':[
'Schedule mobile-crisis or outreach coverage windows and eligible team roles; review gaps and overlapping assignments.',
'Schedule search standby and field-team coverage with eligible roles; do not confuse sign-up with arrival at staging.',
'Schedule site patrol coverage and supervisor positions; review whether members may sign up for multiple shift groups.',
'Schedule crew availability and relief windows; check conflicts with deployments and rest requirements.',
'Schedule facility ERT coverage across plant shifts; review required positions and overlapping assignments.'],
'09-workshifts':[
'Use a static shift to reserve a response vehicle for a defined outreach period; the start and end delimit its commitment.',
'Use a static shift to reserve a search vehicle or boat for an operational period; review its assigned units and commitment dates.',
'Use a static shift to reserve patrol vehicles for an event or site assignment; review start and end times and availability effects.',
'Use a static shift to reserve crew apparatus during travel and assignment; review commitment through the return date.',
'Use a static shift to reserve facility response equipment for a drill or temporary assignment; review unit commitments.'],
'10-mapping':[
'Use current operational team positions for visit coverage; choose a location lifetime and follow the service’s location-access procedures.',
'Set a location lifetime suitable for remote search updates; use search-area POIs and distinguish stale positions from current team location.',
'Map patrol vehicles and site POIs; review stale-location lifetime before treating an old position as current patrol coverage.',
'Map staging, divisions and support vehicles; review device update frequency and stale location during remote assignments.',
'Map facility access points, response equipment and team positions; review indoor or weak-signal limitations and fallback procedures.'],
'11-big-board':[
'Show response-team availability and active work on a coordination display; select an appropriate operational view and protect sensitive details.',
'Show search-team status, incident and staging context; choose status aging thresholds that prompt a check-in.',
'Show patrol status and site coverage; configure aging thresholds for a missed patrol update.',
'Show deployed crews and apparatus status; use staging and response thresholds appropriate to the assignment.',
'Show facility response resources and incidents; use equipment and response-status thresholds for control-room review.'],
'12-chat':[
'Use operational chat for team coordination and handover; keep detailed clinical records in the approved record workflow.',
'Use team chat for search coordination and logistics; confirm incident assignments separately.',
'Use site or patrol chat for low-impact coordination; review recipients before posting client-specific information.',
'Use crew chat for staging and logistics; ensure time-critical instructions also follow approved communications procedures.',
'Use facility chat for coordination and equipment updates; record defects and incidents in their owning workflows.'],
'13-assistant':[
'Ask for help locating setup or operational information, then check it on the owning screen; the assistant is not clinical decision support.',
'Ask how to locate search-team or configuration information; verify the answer and current source records.',
'Ask for help with patrol workflow configuration; inspect site scope and source data before acting.',
'Ask how to find deployment or crew setup information; verify current assignment data and provider availability.',
'Ask for help finding facility workflows; validate answers against current records and approved procedures.'],
'14-admin-assist':[
'Use evidence checks to review roster, communications and upcoming credentials; investigate findings with the service owner.',
'Review empty groups, qualifications and shift conflicts before the next search exercise.',
'Review patrol groups, administrative access and shift conflicts before expanding site coverage.',
'Review seasonal members, qualification expiry and deployment-related setup gaps before mobilization.',
'Review facility groups, credentials and equipment-related setup findings; retain unresolved items in the handover.'],
'15-inventory':[
'Track operational kits and consumables by location; record issues and returns without exposing clinical information.',
'Track rope, radios and search kits; issue equipment to a team, then reconcile returns and damaged items.',
'Track radios, PPE and site keys as appropriate to inventory policy; reconcile equipment issued to patrol staff.',
'Track tools, hose and consumables by base or crew; record transfers and returns after an assignment.',
'Track PPE, spill supplies and response kits; review stock, expiry and damaged equipment.'],
'16-records':[
'Use an approved operational record definition for visits or responses; select fields and access according to the service’s record policy.',
'Record search activity, participants and outcomes; distinguish a saved draft from a reviewed or finalized record.',
'Record patrol or incident activity under an appropriate definition; review required fields and client/site access.',
'Record assignment activity and crew evidence; link the correct call or deployment and retain review status.',
'Record drills and response activity; review the definition, participants and finalization requirements.'],
'17-trainings':[
'Assign approved response and outreach training; review acknowledgments and completion separately from competency or authorization.',
'Assign navigation, search and equipment training; follow up on incomplete sessions.',
'Assign site procedures and incident-report training; review acknowledgment and completion before assigning duties.',
'Assign seasonal crew and equipment training; review completion before mobilization.',
'Assign facility ERT, PPE and response-procedure training; track completion and follow-up.'],
'18-certifications':[
'Track relevant professional and operational credentials and expiry dates; verify originals and renewal requirements with the responsible owner.',
'Track search, rescue and equipment qualifications; review expiry before allocating specialist roles.',
'Track applicable licenses and operational qualifications; review expiry before site assignment.',
'Track crew and operator qualifications and seasonal renewals; verify records before deployment.',
'Track relevant ERT and equipment qualifications and inspections; review impending expiry and renewal evidence.'],
'19-contacts':[
'Maintain approved referral and partner contacts with organizational access rules; keep operational contact notes distinct from clinical records.',
'Maintain land-manager, mutual-aid and logistics contacts for a search area.',
'Maintain client/site contacts and escalation instructions; check access and update ownership.',
'Maintain agency, staging, vendor and assignment contacts; verify who owns current details.',
'Maintain facility, contractor and external-response contacts with escalation notes appropriate to policy.'],
'20-billing':[
'Compare active member counts and enabled modules with subscription capacity; identify the owner of subscription changes.',
'Plan seasonal volunteer capacity and relevant add-ons before increasing the roster.',
'Compare patrol-company roster growth and add-on needs with subscription capacity; review purchases with the account owner.',
'Review seasonal contractor roster and required add-ons; distinguish subscription billing from deployment cost recovery.',
'Review facility roster and operational add-ons against subscription capacity; confirm external billing-system status.'],
'21-workforce':[
'Set worker classifications, operational assignments and reviewed time workflow appropriate to the service.',
'Set workforce tracking only where needed, separating volunteer availability from any payable work.',
'Associate staff, client/site assignments and reviewed worked time; configure compensation and cost allocation according to approved policy.',
'Associate contractor crew, assignment and reviewed worked time; retain rate and cost evidence for authorized finance review.',
'Associate facility staff, work classifications and approved time; review organization-specific approval and compensation rules.'],
'22-deployments':[
'Plan an outreach event or temporary response-coverage deployment with dates, roster and operational objectives.',
'Plan a search deployment with staging, operational period, personnel and resource roster.',
'Plan event-security or temporary site coverage with an operational roster and dates.',
'Plan a crew assignment with operational dates and resources; review cost evidence separately from the operational roster.',
'Plan plant turnaround or mutual-aid coverage with dates, response resources and responsible reviewers.'],
'23-reporting':[
'Report operational coverage, response activity and training progress; interpret metrics according to the service’s approved definitions.',
'Report search activity, team participation and readiness gaps; verify filters and source records.',
'Report patrol/site activity and coverage; review filters before sending a client-facing result.',
'Report crew deployment activity and reviewed cost evidence; distinguish missing records from zero activity.',
'Report facility incidents, drills and readiness; review the time zone, date range and source completeness.'],
'24-checklists':[
'Use a vehicle or operational-kit checklist; follow up on failed items and distinguish scheduled compliance from an on-demand check.',
'Use search-kit and vehicle readiness checks; assign failed equipment follow-up.',
'Use patrol vehicle or site-opening checks; review failures and missed scheduled checks.',
'Use crew and apparatus readiness checks before mobilization; create accountable defect follow-up.',
'Use response-kit and equipment checks; review required items and route failures to maintenance.'],
'25-work-orders':[
'Turn a response-vehicle or kit defect into a work order with an owner, state and completion evidence.',
'Track defective radios or search equipment through review, repair and return to service.',
'Track patrol equipment and vehicle defects through assigned repairs and verification.',
'Track apparatus and tool defects with assignment impact and return-to-service evidence.',
'Track response-equipment defects through repair ownership and verified completion.'],
'26-business-operations':[
'Connect approved operational activity to the service’s cost workflow; review eligibility and export prerequisites outside the operational roster.',
'Keep operational search records and any approved cost evidence together without assuming reimbursement eligibility.',
'Connect client/site service activity to reviewed costs and invoices; verify source activity before authorized billing.',
'Connect crew assignment activity and approved costs to the contracting workflow; validate rates and evidence before financial submission.',
'Connect facility or contracted response activity to reviewed internal cost allocation and invoicing where applicable.'],
'27-notifications':[
'Review eligible channels and intended team recipients before an authorized communication test; configuration alone does not prove delivery.',
'Review volunteer alert channels and inactive members; test reviewed recipients and fallback communications.',
'Review site/patrol alert recipients and channel preferences; prove delivery through a reviewed test.',
'Review crew communication channels and remote-connectivity limitations before mobilization.',
'Review on-duty facility recipients and specialist escalation channels; test reviewed recipients and fallback procedures.'],
'28-call-intake':[
'Use an approved operational request type for a visit or mobile response; keep clinical triage and sensitive detail under the service’s procedures.',
'Use Rescue or a reviewed search type and clear staging information; select the appropriate team.',
'Use Investigation or a reviewed patrol incident type with the correct site and selected resources.',
'Use a reviewed assignment or incident type and staging details; select crew and support resources.',
'Use a reviewed facility incident type and access location; select the facility team and specialist equipment.'],
'29-reference-workflows':[
'Organize approved response and referral procedures with responsible owners and review dates.',
'Organize search, navigation and equipment protocols and mutual-aid references.',
'Organize site instructions, escalation procedures and patrol reference documents.',
'Organize assignment, equipment and agency procedures with seasonal review ownership.',
'Organize facility response plans, access instructions and equipment procedures with current owners.'],
'30-apps-integrations':[
'Choose member, dispatch and display apps according to response-team duties; verify device registration and external providers separately.',
'Choose field-member, dispatch and coordination-display apps; verify location update and remote connectivity.',
'Choose patrol-member, dispatcher and site-display apps; verify site scope and device registration.',
'Choose crew-member, dispatch and coordination apps; verify device updates during remote assignments.',
'Choose responder, control-room and display apps; verify provider prerequisites and facility connectivity.']}
PRIMER_MAP={'00-start':'01-setup-wizard','01-people':'04-personnel','02-security':'02-department-settings','03-units':'05-groups-units','04-apps':'30-apps-integrations','05-calls':'28-call-intake','06-communication':'27-notifications','07-mapping':'10-mapping','08-shifts':'08-shifts','09-training':'17-trainings','10-knowledge':'29-reference-workflows','11-checklists':'24-checklists','12-maintenance':'25-work-orders','13-inventory':'15-inventory','14-records':'16-records','15-deployments':'22-deployments','16-business':'26-business-operations','17-automation':'30-apps-integrations','18-ptt':'12-chat','19-adp':'16-records','20-plans':'20-billing','21-ai':'13-assistant','22-relay':'28-call-intake','23-self-hosting':'30-apps-integrations'}
SPECIAL={
'17-automation':['Use a reviewed workflow for an operational handover task; inspect external provider output before adoption.','Use a reviewed workflow for search logistics or follow-up; inspect failed executions.','Use a reviewed workflow for patrol follow-up; verify client/site scope and external delivery.','Use a reviewed workflow for assignment follow-up; inspect provider failures and retries.','Use a reviewed workflow for drill or equipment follow-up; inspect execution history.'],
'18-ptt':['Plan operational team channels and verify device and add-on prerequisites.','Plan search-team and staging channels; test approved participants and fallback radio procedures.','Plan site and patrol channels with intended memberships; test authorized device access.','Plan crew and staging channels; test connectivity and approved fallback communications.','Plan facility response channels; test device access and approved fallback communications.'],
'19-adp':['Review protected-record access, key and recovery prerequisites according to the service’s policy.','Review protected operational details and recovery ownership; verify authorized access.','Review client/site protected-data access and recovery responsibilities.','Review protected assignment data and key/recovery ownership.','Review protected facility information and recovery procedures with responsible owners.'],
'22-relay':['If an approved audio dispatch feed exists, configure an appropriate reviewed relay source; validate transcription and recipient selection.','Review the authorized dispatch audio source, transcription quality and search-team classification before using Relay.','Review whether the organization has an appropriate authorized audio feed; validate site classification and recipients.','Review the authorized assignment/dispatch feed and remote connection prerequisites; verify parsed output.','Review the authorized control-room dispatch feed and provider prerequisites; verify parsed incident details.'],
'23-self-hosting':['Configure isolated service providers and test operational workflows; review protected-data handling and backups.','Configure databases, workers and mapping providers; test remote devices and restore procedures.','Configure department/site boundaries, providers and worker operations; test actual device and alert behavior.','Configure providers and workers and test deployment workflows; review remote connectivity and backups.','Configure facility providers, worker processing and backups; test restore and external system boundaries.']}

def add_companion(path,title,examples):
    text=path.read_text() if path.exists() else title+'\n'
    marker='\n\nADAPT THIS WORKFLOW TO YOUR DEPARTMENT\n'
    text=text.split(marker)[0]
    text+=marker+'Firehouse 51 is synthetic demonstration data. Apply the same workflow to your department’s procedures.\n'
    for sector,example in zip(SECTORS,examples):text+=f'\n{sector}: {example}\n'
    text+='\nPractice: reproduce the configuration in your training department, save it, inspect the result, and identify the responsible reviewer. Sector examples are written companions; their presence does not certify provider delivery, clinical scope, or an updated video export.\n'
    path.write_text(text)

def main():
    p=BASE/'course.json';course=json.loads(p.read_text())
    for l in course['lessons']:
        examples=SPECIAL.get(l['id'],EXAMPLES[PRIMER_MAP[l['id']]])
        l['sector_examples']=dict(zip(SECTORS,examples))
        l['sector_narration_status']='written companion installed; new narration pending'
        add_companion(BASE/'scripts'/f"{l['id']}.txt",l['title'],examples)
    by_id={l['id']:l for l in course['lessons']}
    for f in course['features']:
        examples=by_id[f['lesson']]['sector_examples']
        f['sector_examples']={s:f"{f['label']}: {e}" for s,e in examples.items()}
        add_companion(BASE/'scripts'/f"feature-{f['id']}.txt",f['label'],list(f['sector_examples'].values()))
    course['sector_coverage']={'required_sectors':SECTORS,'lessons_with_written_examples':len(course['lessons']),'features_with_written_examples':len(course['features']),'companion':'deep-dive/sectors.html','narrated_revision':'in production; written companions are available now'}
    p.write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n')
    dp=BASE/'deep-dive/course.json';deep=json.loads(dp.read_text())
    for l in deep['lessons']:l['sector_examples']=dict(zip(SECTORS,EXAMPLES[l['id']]))
    dp.write_text(json.dumps(deep,ensure_ascii=False,indent=2)+'\n')
    matrix={'sectors':SECTORS,'deep_lessons':deep['lessons'],'primer_lessons':[{k:l[k] for k in ['id','title','sector_examples','sector_narration_status']} for l in course['lessons']]}
    (BASE/'deep-dive/sector-examples.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2)+'\n')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Resgrid — adapt the workflow</title><style>body{font:17px/1.6 system-ui;margin:0;background:#edf2f6;color:#172f46}main{max-width:1040px;margin:auto;padding:28px}h1{line-height:1.15}a{color:#17636e}select,input,button{font:inherit;padding:12px;border:1px solid #a9bac8;border-radius:8px;background:white;width:100%;box-sizing:border-box}label{display:block;margin:15px 0 6px;font-weight:700}.card{background:white;border:1px solid #cfdae3;border-radius:12px;padding:24px;margin:20px 0}.eyebrow{font-size:13px;color:#416a78;text-transform:uppercase;letter-spacing:.08em}.scope{background:#d8eee7;padding:18px;border-radius:10px}.muted{color:#526a7e}h2{font-size:23px;margin:7px 0}.controls{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:700px){.controls{grid-template-columns:1fr}}</style><main><a href="../">← Academy library</a><p class="eyebrow">Sector adaptation workbook</p><h1>Use Resgrid for your department’s work</h1><p>Firehouse 51 supplies fictional demonstration data. The same roster, status, dispatch, resource, readiness and record workflows can serve other organizations.</p><p class="scope">Every detailed lesson and all 173 feature briefs now include written sector examples. New detailed narration is in production. Existing video exports have not yet all received the narrated adaptation section.</p><div class="controls"><div><label for="sector">Your department</label><select id="sector"></select></div><div><label for="search">Find a workflow</label><input id="search" type="search" placeholder="Statuses, dispatch, shifts, inventory…"></div></div><p id="count" class="muted"></p><div id="cards"></div><p class="muted">Choose role and record policies appropriate to your organization. Software labels and operating packs do not establish qualifications, clinical scope or external system delivery.</p></main><script>const data=__DATA__;const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));const sector=document.querySelector('#sector');for(const s of data.sectors){const o=document.createElement('option');o.textContent=s;sector.append(o)}function render(){const q=document.querySelector('#search').value.toLowerCase();const rows=data.deep_lessons.filter(l=>JSON.stringify(l).toLowerCase().includes(q));document.querySelector('#count').textContent=rows.length+' detailed workflows';document.querySelector('#cards').innerHTML=rows.map(l=>'<article class="card"><p class="eyebrow">'+esc(l.id)+'</p><h2>'+esc(l.title)+'</h2><p>'+esc(l.sector_examples[sector.value])+'</p><p class="muted">Practice: configure in a training department, save, verify the observed result and record the next reviewer.</p><p class="muted">Detailed video: '+esc(l.status)+'</p></article>').join('')}sector.onchange=render;document.querySelector('#search').oninput=render;render();</script></html>'''
    page=page.replace('← Academy library</a>', '← Academy library</a> · <a href="./">Watch detailed videos and review storyboards</a>')
    page=page.replace("const sector=document", "const statusLabels={'video-verified':'Video assembled; browser playback verified','video-assembled':'Video assembled; browser playback review pending','captured-scripted':'Captures and script ready; video assembly pending','pending-capture':'Detailed capture and narration pending'};const sector=document")
    page=page.replace('esc(l.status)', 'esc(statusLabels[l.status] || l.status)')
    page=page.replace("+'</p></article>'", "+'</p>'+(['video-verified','video-assembled','captured-scripted'].includes(l.status)?'<a href=\"review/'+esc(l.id)+'/\">'+(l.status.startsWith('video-')?'Watch this walkthrough':'Review the storyboard')+'</a>':'')+'</article>'")
    page=page.replace("rows.length+' detailed workflows'", "rows.length+' detailed workflow'+(rows.length===1?'':'s')")
    (BASE/'deep-dive/sectors.html').write_text(page.replace('__DATA__',json.dumps(matrix,ensure_ascii=False).replace('<','\\u003c')))
    report={'passed':all(len(l['sector_examples'])==5 for l in deep['lessons']+course['lessons']) and all(len(f['sector_examples'])==5 for f in course['features']),'deep_lessons':len(deep['lessons']),'primer_lessons':len(course['lessons']),'feature_briefs':len(course['features']),'sector_examples':5*(len(deep['lessons'])+len(course['lessons'])+len(course['features'])),'video_exports_updated':False}
    (BASE/'deep-dive/sector-coverage-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
