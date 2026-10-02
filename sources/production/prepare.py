"""Build a source-backed Resgrid training production package; never runs Resgrid actions."""
import csv
import hashlib
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'evidence/resgrid'
OUT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'Core/Resgrid.AdminAssist/Catalog'
CONTROLLERS = ROOT / 'Web/Resgrid.Web/Areas/User/Controllers'
VIEWS = ROOT / 'Web/Resgrid.Web/Areas/User/Views'
LOC = {e.attrib['name']: e.findtext('value') for e in ET.parse(
    ROOT / 'Core/Resgrid.Localization/Areas/User/AdminAssist/AdminAssist.resx').getroot().findall('data')}
ORDER = ['people', 'security', 'units', 'apps', 'calls', 'communication', 'mapping',
         'shifts', 'training', 'knowledge', 'checklists', 'maintenance', 'inventory',
         'records', 'deployments', 'business', 'automation', 'ptt', 'adp', 'plans', 'ai']

# Editorial scenarios and exercises. These are teaching examples, not product defaults.
AREA = {
 'people': ('Build a roster dispatch can use', 'Administrators',
  'An out-of-date roster leaves dispatchers guessing which station, team, or role a member belongs to.',
  ['Create Station 1 and Station 2 with their addresses.', 'Invite sample members and assign their station groups.', 'Create Engineer and Officer roles and assign them deliberately.'],
  'Verify a sample member appears in the correct group and role. Check an accepted invitation and the member contact details.',
  'An invitation is not an accepted membership. A role label is not proof of a current certification. Review both separately.',
  'Invite one sample member, assign a station and role, and have that member sign in. Track unaccepted invitations.'),
 'security': ('Configure a department and protect access', 'Administrators',
  'Wrong time zones distort schedules, and broad permissions expose work to people who do not need it.',
  ['Confirm the department address and time zone.', 'Choose the modules the department will use and review permissions.', 'Enroll two administrators in MFA before reviewing enforcement and recovery.'],
  'Use separate administrator and member accounts to check allowed actions and resource visibility. Test recovery before enforcing stricter sign-in rules.',
  'Hiding a module is not evidence that API access stops. MFA enrollment is separate from a tested factor and recovery path.',
  'Complete Setup Wizard, save on each owning screen, then Verify again. Keep unknown checks visible and assign follow-up owners.'),
 'units': ('Represent apparatus, crews, and GPS devices', 'Administrators and dispatchers',
  'A vehicle name alone does not tell a dispatcher its type, home station, crew, or location source.',
  ['Create Engine and Rescue unit types.', 'Add Engine 1 with its type, Station 1, and crew roles.', 'Assign the crew and, when used, register a tracking device against the unit.'],
  'Confirm the unit type, home station, crew, and status. For hardware tracking, check a recent received position and the stale-position behavior.',
  'An old GPS position is not a live position. Crew assignment, reported unit status, and physical readiness are distinct.',
  'Create Engine 1 in the demo department and verify the assigned crew from the dispatcher view. Measure incomplete unit records.'),
 'apps': ('Put the right Resgrid app on each device', 'Members, dispatchers, and commanders',
  'A configured department still needs members and shared devices to sign in to the correct department with the correct permissions.',
  ['Set up a member device with Responder and notification permissions.', 'Set up an apparatus tablet with Unit and select its unit.', 'Grant appropriate Dispatch or Command access and configure a station Big Board.'],
  'Check the active department, device identity, and a controlled notification test. Check what a shared station screen exposes.',
  'Installing an app does not prove alerts arrive. Verify OS notification and location settings on the actual device used.',
  'Use a sample member, unit tablet, dispatcher, and station display to follow the same training incident. Record which devices complete the test.'),
 'calls': ('Take an incident from intake to closeout', 'Dispatchers and administrators',
  'Inconsistent call classification and unclear recipients create avoidable re-entry and uncertainty during dispatch.',
  ['Configure call types, priorities, and response statuses.', 'Create a training call, confirm its map location, and choose recipients.', 'Review response progress, close the training call, and find it in archived calls.'],
  'Check the saved call details and intended recipients. Use a controlled communication test to evaluate delivery separately from the saved dispatch.',
  'Run-card recommendations require review. Shift routing, unit crew routing, group routing, and automatic status changes can affect different people.',
  'Create a Medical training call for Station 1. Confirm the location, recipients, status transitions, closeout, and archived record.'),
 'communication': ('Make alerts reach the intended audience', 'Administrators, officers, and members',
  'Repeated messages create noise, while incomplete contacts and device preferences can leave intended recipients unreachable.',
  ['Confirm member contacts and notification preferences.', 'Create an Officers distribution list and a focused notification rule.', 'Run an explicit communication test and review the recorded outcomes.'],
  'Ask test recipients to confirm the actual channel and time received. Review missing or failed results and the intended audience.',
  'A provider handoff is not confirmed delivery. Staffing suppression, recipient selection, and contact eligibility each deserve a separate check.',
  'Send only to the demo audience. Record recipients, observed receipts, failures, and follow-up actions; compare with the expected audience.'),
 'mapping': ('Make location information useful and current', 'Dispatchers and administrators',
  'A map can mislead when old positions remain visible or useful sites and reference layers are missing.',
  ['Review personnel and unit location-age settings.', 'Add stations and hospitals as points of interest.', 'Add a relevant map layer, planned route, or weather zone and review its audience.'],
  'Check marker age and source, POI placement, reference-layer alignment, and the intended weather-alert coverage.',
  'Location sharing requires client permission. Uploaded floor plans are reference material; verify currency and alignment before relying on them.',
  'Follow a sample unit and compare a recent position with a stale position. Record missing POIs and outdated reference layers.'),
 'shifts': ('Plan coverage and keep dispatch aligned', 'Schedulers, dispatchers, and members',
  'A paper duty schedule and a dispatch roster can drift apart, especially when members sign up or trade shifts.',
  ['Create an assigned or signup shift with groups and staffing needs.', 'Have demo members sign up or complete a trade where supported.', 'Review whether dispatch follows groups or shifts and confirm the calendar time zone.'],
  'Compare the scheduled roster with the people dispatch would include at the selected time. Check trade completion and the visible duty coverage.',
  'A calendar event is not automatically a duty assignment. Shift dispatch behavior must be reviewed on Dispatch Settings.',
  'Schedule a weekend duty crew, change one assignment, and verify the expected roster. Track unfilled slots and unresolved trades.'),
 'training': ('Assign learning and track qualifications', 'Training officers and members',
  'Scattered training records make it harder to see incomplete assignments and upcoming certification renewals.',
  ['Create certification types with their renewal periods.', 'Record current member certifications and review expiry settings.', 'Create a training with materials and an optional quiz, then assign the intended audience.'],
  'Check a sample member completion and certification expiry. Review reminders, grace periods, and any configured enforcement effects.',
  'A completed training, a personnel role, and a current certification represent different facts. Track each through its owning feature.',
  'Assign a refresher to the demo group and complete it as a member. Review overdue learning and certifications approaching renewal.'),
 'knowledge': ('Give members a dependable reference library', 'Officers, dispatchers, and members',
  'Procedures and contacts hidden in individual email threads are difficult to find and keep current.',
  ['Add key outside contacts and organize categories.', 'Upload a current procedure and set its intended visibility.', 'Create approved protocol questions or a form for a repeatable dispatch task.'],
  'Open the contact, document, protocol, and form as an intended member. Check ownership, version currency, attachments, and visibility.',
  'A shared link needs an explicit data-sharing review. Keep protocol content aligned with department-approved procedures.',
  'Find the hospital contact and current procedure as a sample member. Track outdated material and items without a responsible owner.'),
 'checklists': ('Record routine checks and missed work', 'Readiness officers and members',
  'Paper checks make it difficult to see which apparatus was inspected and which scheduled checks were missed.',
  ['Start from a checklist template or build the approved checks.', 'Assign the checklist and set its recurring schedule.', 'Complete a demo check, record a defect, and review compliance.'],
  'Compare due checks with completed, skipped, and overdue results. Confirm defects have an assigned follow-up owner.',
  'A completion report documents recorded checks. A failed item still requires action through the department repair process.',
  'Complete a daily Engine 1 check and leave a second demo check overdue. Confirm that the compliance view distinguishes both.'),
 'maintenance': ('Turn defects into accountable repairs', 'Fleet officers and technicians',
  'A defect reported in chat can be forgotten when it has no work order, owner, approval, or return-to-service record.',
  ['Confirm Readiness Pro access, the Maintenance module, and permissions.', 'Create a work order from a reported defect and assign responsibility.', 'Record corrective work and follow the configured approval and safety-hold process.'],
  'Review the repair history, recorded costs, approval state, and any safety hold. Release follows the owning maintenance workflow.',
  'Checklists are available separately from Readiness Pro. Buying maintenance access does not configure the module or approval policy.',
  'Track a demo pump-test defect through assignment, repair, review, and documented return to service. Measure unresolved work-order age.'),
 'inventory': ('Know what is available, issued, and expiring', 'Logistics officers and members',
  'Unrecorded transfers and missing expiry dates make stock levels unreliable and replenishment harder to plan.',
  ['Define the stock locations and items the department will track.', 'Record a receipt, transfer, and equipment issue using sample stock.', 'Review counts, expiry, low-stock alerts, and purchasing needs.'],
  'Reconcile a physical demo count with recorded stock. Check the destination of a transfer, the equipment assignee, and the expiry record.',
  'A purchase order is distinct from a received delivery. Reconcile the receipt before assuming stock is available.',
  'Receive ten demo supplies, transfer two, and issue one durable item. Reconcile the resulting balances and inspect expiry alerts.'),
 'records': ('Keep incident and prevention records reviewable', 'Report writers, reviewers, and records officers',
  'Incident information becomes harder to review and report when it is spread across calls, attachments, and separate files.',
  ['Review record settings, definitions, numbering, visibility, and retention.', 'Create a report linked to a training call and complete its required data.', 'Use review, evidence, exports, or submission workflows appropriate to the record.'],
  'Check draft and review status, evidence provenance, restricted access, and the actual outcome of any test submission.',
  'A queued submission is not acceptance by its destination. Legal holds and disclosure reviews require their owning workflows.',
  'Prepare one complete training incident report and one incomplete draft. Use the work queue to assign corrections and compare analytics scope.'),
 'deployments': ('Keep deployment activity and cost evidence together', 'Deployment coordinators and finance officers',
  'Extended mutual-aid work needs clear personnel, apparatus, dates, and cost records that can be reviewed after demobilization.',
  ['Create a deployment or start from an external resource order.', 'Identify the assigned personnel, apparatus, and operational dates.', 'Record deployment activity and finance documentation for review.'],
  'Reconcile the deployment resources and dates with supporting records. Review any daily time and cost documentation required by the workflow.',
  'Deployment Finance is separate from the Business Operations add-on. A prepared record does not guarantee reimbursement.',
  'Record a two-day demo strike-team deployment and reconcile the participating people and units with the supporting documents.'),
 'business': ('Connect service activity to costs and billing', 'Finance staff and business administrators',
  'Re-entering activity into estimates, invoices, and cost spreadsheets creates inconsistent rates and missed supporting evidence.',
  ['Confirm Business Operations access and configure billing identity and approved rates.', 'Prepare a demo bid or contract and the corresponding service invoice.', 'Review payments, invoice aging, deployment costs, or MARS claim evidence as applicable.'],
  'Reconcile source activity, quantities, rates, totals, and recorded payment or claim outcomes. Use a payment-provider test environment.',
  'Pay-data reporting also requires enabled Advanced Data Protection. Annual rates and reporting requirements need current finance review.',
  'Prepare a standby estimate and draft invoice from sample activity. Compare recorded cost with the billed amount and explain any difference.'),
 'automation': ('Automate a repeatable task with visible outcomes', 'Administrators and integration owners',
  'Manual copying between systems costs time and hides failures when there is no recorded execution history.',
  ['Choose one event and an approved destination for a workflow.', 'Configure the workflow action, data mapping, and integration access.', 'Trigger a controlled demo event and review Workflow Runs for success or failure.'],
  'Confirm the intended action at the destination and inspect the recorded run. Test a controlled failure and document who owns retries.',
  'A saved workflow is not evidence that its destination received data. Protected content requires the separately reviewed egress path.',
  'Create a demo-only new-call workflow and inspect its run. Record successful and failed execution evidence, owner, and recovery steps.'),
 'ptt': ('Set up voice channels for team coordination', 'Administrators and field teams',
  'Field teams need the correct channel membership and working device audio before an exercise or deployment.',
  ['Confirm Push-to-Talk access and supported clients.', 'Create a training channel and add its intended members.', 'Join from two demo devices and verify transmit, receive, and microphone permissions.'],
  'Check membership and actual audio in both directions on the devices used. Review channel access after membership changes.',
  'Push-to-Talk channel setup is separate from phone voice alerts and audio-stream configuration.',
  'Run a two-device training-channel check and record which members can transmit and receive.'),
 'adp': ('Plan protected-data access and recovery', 'Security administrators and records officers',
  'Sensitive content needs deliberate enrollment, controlled access, key recovery, and reviewed external disclosure paths.',
  ['Confirm Advanced Data Protection access and review the enrollment checklist.', 'Prepare administrator MFA and department key-recovery arrangements.', 'Enroll through the owning screen and review supported content, search, exports, and integrations.'],
  'Use sample protected content to verify an authorized read, a denied read, and the approved recovery procedure. Review egress separately.',
  'Buying the add-on does not enroll the department. Enrollment and migration behavior must be confirmed for the target release.',
  'Document who owns enrollment, key recovery, and disclosure review. Use only synthetic protected content for the recording.'),
 'plans': ('Match subscription capacity to the roster', 'Managing members and administrators',
  'Large onboarding can stop at personnel or unit limits when capacity has not been reviewed in advance.',
  ['Review the observed base plan, personnel count, and unit count.', 'Compare planned onboarding with available capacity.', 'Review add-on entitlements and their separate configuration prerequisites.'],
  'Check observed subscription evidence and current resource counts. Use the owning billing screen for any authorized subscription change.',
  'Missing billing evidence means capacity is unknown. Only the managing member performs subscription changes.',
  'Compare current counts with a proposed roster expansion. Document headroom and optional add-ons without purchasing anything.'),
 'ai': ('Understand AI availability and human review', 'Administrators and officers',
  'AI product descriptions and code can move ahead of deployment availability, so training must distinguish released tools from planned ones.',
  ['Use deterministic Setup Wizard and Setup Report for configuration guidance.', 'Check whether Admin AI is enabled for the target department.', 'Check release and rollout before teaching Enhanced AI summaries or drafts.'],
  'Record the target deployment version and observed feature availability. Human reviewers remain responsible for any generated explanation or draft.',
  'The catalog in this checkout marks Enhanced AI as planned. This lesson explains its scope; it does not demonstrate a released configuration.',
  'Ask a configuration question through an available tool, inspect its evidence, and identify any unknowns before making a change.')
}

# Coverage grouping includes auxiliary controllers rather than silently dropping them.
GROUPS = {
 'people': 'Personnel Groups',
 'security': 'Department Security AccountSecurity TwoFactor Passkeys Account AdminAssist Help Moderation',
 'units': 'Units UnitTracking Types',
 'apps': 'Home Profile Command',
 'calls': 'Dispatch RunCards Templates CustomStatuses',
 'communication': 'Messages Notifications DistributionLists CommunicationTest Chat ChatbotSettings MessagingAccounts',
 'mapping': 'Mapping CustomMaps IndoorMaps Routes WeatherAlerts',
 'shifts': 'Shifts Workshifts Calendar',
 'training': 'Trainings Certifications',
 'knowledge': 'Contacts Documents Notes Protocols Forms Files Links Connect Search',
 'checklists': 'Checklists ChecklistsScheduling ChecklistReporting ChecklistReports ChecklistReminders',
 'maintenance': 'WorkOrders WorkOrderOperations WorkOrderMaintenance WorkOrderReporting ReadinessProBilling',
 'inventory': 'Inventory InventoryOperations InventoryPurchasing',
 'records': 'Records IncidentReports IncidentAnalysis Logs Reports RecordDefinitions RecordOccupancies RecordInspections RecordHydrants RecordPermits RecordInvestigations RecordEvidence RecordLegalHolds RecordSubmissions RecordsAnalytics RecordSavedReports RecordsExportTemplates Disclosures RecordsQuality RecordsHealth RecordPreventionAttachments RecordDocuments RecordCalls RecordsInventory RecordDeployments RecordDeploymentConnectors',
 'deployments': 'Deployments DeploymentOrders Orders',
 'business': 'Invoicing RateSchedules Contracts Bids DeploymentWizard CalOesMars Workforce BusinessOperationsBilling',
 'automation': 'Workflows UserDefinedFields',
 'ptt': 'Voice', 'adp': 'DataProtection ProtectedWorkflows',
 'plans': 'Subscription', 'ai': 'AiDispatch AiBilling'
}

def local(key):
    return LOC.get(key, key or '') or ''

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_ref(path, text=None):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path),
            'line': 1 if not text else next((i for i,l in enumerate(path.read_text().splitlines(),1) if text in l),1)}

def human(s):
    return re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s).replace('_', ' ')

def scene(kind, title, body, narration, **extra):
    return dict(kind=kind, title=title, body=body, narration=narration, **extra)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    caps, settings, lessons, controller_rows = [], [], [], []
    action_pattern = r'public\s+(?:async\s+)?(?:Task\s*<\s*(?:IActionResult|ActionResult)\s*>|IActionResult|ActionResult)\s+(\w+)\s*\('
    action_index = {}
    declarations = {}
    for file in sorted(CONTROLLERS.glob('*Controller.cs')):
        text = file.read_text()
        classes = list(re.finditer(r'public\s+(?:(?:sealed|partial|abstract)\s+)*class\s+(\w+)Controller\b', text))
        declarations[file] = []
        for i, match in enumerate(classes):
            name = match.group(1)
            chunk = text[match.end():classes[i+1].start() if i+1<len(classes) else len(text)]
            actions = set(re.findall(action_pattern,chunk))
            declarations[file].append(name)
            action_index.setdefault(name,set()).update(actions)
    for number, aid in enumerate(ORDER, 1):
        path = CATALOG / (aid+'.yaml')
        data = json.loads(path.read_text())
        a = data['Areas'][0]
        title, role, problem, flow, verify, issue, practice = AREA[aid]
        module = {'id': f'{number:02}-{aid}', 'area': aid, 'title': title,
                  'role': role, 'catalog_version': data['Version'],
                  'status': 'illustrated lesson; live walkthrough pending',
                  'problem': problem, 'workflow': flow, 'verification': verify,
                  'common_issue': issue, 'exercise': practice, 'features': [],
                  'evidence': [source_ref(path),source_ref(ROOT/'docs/admin-assist/setup-guide.md')]}
        scenes = [scene('title',title,[role,local(a['PurposeKey'])],
                         f'Welcome to Resgrid Academy. In this lesson, we will {title.lower()}. {problem} We will explain the features, the setup decisions, and a practical way to check the result.'),
                  scene('scenario','A department scenario',[local(a['ExampleKey']),local(a['ValueKey'])],
                         local(a['ExampleKey'])+' '+local(a['ValueKey'])+' The examples in this series use a fictional department and are teaching scenarios, not default settings.')]
        for cap in data['Capabilities']:
            c = {'id':cap['Id'], 'area':aid, 'lesson':module['id'], 'label':local(cap['LabelKey']),
                 'purpose':local(cap['PurposeKey']), 'value':local(cap['ValueKey']),
                 'setup':local(cap['AdoptionKey']), 'requirements':cap['Requirements'],
                 'release_status':cap['ReleaseStatus'], 'location':cap['Location'],
                 'docs_url':'https://docs.resgrid.com'+cap.get('DocsPath',a['DocsPath']),
                 'source':source_ref(path,'"Id": "'+cap['Id']+'"'),
                 'capture_status':'not recorded', 'verification_status':'source reviewed; deployment unverified'}
            controller=CONTROLLERS/(cap['Location']['Controller']+'Controller.cs')
            action=cap['Location']['Action']
            c['owner_action_in_source'] = action in action_index.get(cap['Location']['Controller'],set())
            view=VIEWS/cap['Location']['Controller']/(action+'.cshtml')
            c['view_fields'] = sorted(set(re.findall(r'asp-for="([^"]+)"|(?:TextBoxFor|DropDownListFor)\(m\s*=>\s*m\.([A-Za-z0-9_.]+)',view.read_text()))) if view.exists() else []
            c['view_fields'] = [next(x for x in pair if x) for pair in c['view_fields']]
            c['capture_steps'] = [f'Open {c["label"]} as the intended {role.lower()}.',
                                  c['setup'], 'Demonstrate one controlled sample through the owning screen.',
                                  verify, 'Show one common issue and the evidence used to diagnose it.']
            if not c['owner_action_in_source']:
                c['capture_steps'].insert(1,'Resolve the catalog-to-screen action mismatch before recording; do not invent a working route.')
            caps.append(c);module['features'].append(c['id'])
            requirement_names=[human(r['Id']) for r in c['requirements'] if r['Kind'] in ['addon','module','protection']]
            narration = c['label']+'. '+c['purpose']+' '+c['setup']
            if cap['ReleaseStatus'] != 'available': narration += ' This feature is marked planned in the source catalog. Verify release availability before recording a configuration walkthrough.'
            elif requirement_names: narration += ' Availability also depends on '+', '.join(dict.fromkeys(requirement_names))+'. Check access in the target department.'
            scenes.append(scene('feature',c['label'],[c['purpose'],c['setup']],narration,
                                feature_id=c['id'], tag='Planned' if cap['ReleaseStatus']!='available' else 'Feature & setup'))
        scenes += [scene('workflow','Configure one useful workflow',flow,
                    'For the training scenario, work in this order. '+' '.join(f'Step {i}. {step}' for i,step in enumerate(flow,1))),
                   scene('verify','Verify the result',[verify,issue],
                    'Now verify the result. '+verify+' A common problem to watch for: '+issue),
                   scene('exercise','Try it with your department',[practice,'Record the result, the owner, and the next review date.'],
                    'Your practice task is simple. '+practice+' Record the result, who owns the follow-up, and when it should be reviewed. Use the linked feature scripts for the detailed screen recording plan.')]
        module['scenes']=scenes;lessons.append(module)
        articles={x['Id']:x for x in data['Articles']}
        for s in data['Settings']:
            settings.append({'id':s['Id'],'area':aid,'lesson':module['id'],'label':local(s['LabelKey']),
                             'help':articles.get(s['Id'],{}).get('Body',local(s['HelpKey'])),
                             'location':s['Location'],'default':s.get('DefaultValue'),
                             'classification':s.get('Classification'),'secret':s.get('Secret'),
                             'availability':s.get('Availability'),'source':source_ref(path,'"Id": "'+s['Id']+'"')})
    ctrl_group={c:a for a,names in GROUPS.items() for c in names.split()}
    for file in sorted(CONTROLLERS.glob('*Controller.cs')):
        name=file.stem.removesuffix('Controller');text=file.read_text()
        actions=sorted(set(re.findall(action_pattern,text)))
        declared=declarations[file]
        area=ctrl_group.get(name,next((ctrl_group[n] for n in declared if n in ctrl_group),'unassigned'))
        controller_rows.append({'source_file':file.name,'controller':name,'declared_controllers':declared,'area':area,
                                'actions':actions,'source':source_ref(file),
                                'recording_status':'capture pending',
                                'mapped_features':[c['id'] for c in caps if c['location']['Controller'] in declared]})
    intro = {'id':'00-start','area':'orientation','title':'Resgrid: from the first alert to the next shift',
             'role':'All department roles','status':'illustrated lesson; live walkthrough pending', 'features':[],
             'scenes':[
       scene('title','Ready for the next call',['A connected operation','People • apparatus • information'],
        'Welcome to Resgrid Academy. Resgrid brings dispatch, people, apparatus, and department management into a connected system. This series explains what each feature does, how to prepare it, and how to tell whether it is helping your department.'),
       scene('workflow','One incident. A connected workflow.',['Prepare people and units','Create and coordinate the call','Review records and restore readiness'],
        'Picture a fictional department with two stations, an engine, and a rescue unit. First, administrators organize members, groups, roles, and units. A dispatcher creates a training call and selects the intended resources. Members respond through their assigned devices. After closeout, officers complete records and follow up on equipment, supplies, and staffing.'),
       scene('feature','Build the foundation',['Department address and time zone','Members, groups, roles, and units','Permissions and account recovery'],
        'Start with the foundation. Set the department address and time zone. Build the roster, home stations, personnel roles, and unit types. Review who can dispatch, manage information, and administer the department. Prepare account recovery as you set up stronger sign-in protections. These choices influence later schedules, recipients, maps, and reports.'),
       scene('feature','Coordinate the response',['Call types, priorities, and recipient routing','Status updates and location information','Messages, notification tests, and voice'],
        'For operations, learn call intake, types, priorities, recipient routing, run cards, and response statuses. Mapping adds location and site context. Messaging and notification rules keep the intended audience informed. Verify communications on actual devices. A saved call or provider handoff is different from confirmed receipt by a member.'),
       scene('feature','Keep the department ready',['Shifts, training, and certifications','Checklists, maintenance, and inventory','Documents, contacts, protocols, and calendars'],
        'Between calls, shifts help plan coverage. Training and certification records make learning and renewal work visible. Checklists record routine inspections. Maintenance gives defects an owner and a documented repair process. Inventory records where equipment and supplies are stored, issued, and replenished. Documents, contacts, protocols, and calendars give members a shared reference point.'),
       scene('feature','Make the back office reviewable',['Incident and prevention records','Deployment documentation and finance','Reporting, costs, contracts, and billing'],
        'Records connect incident reporting, prevention, investigation, evidence, review, and disclosure. Deployments keep extended response activity and supporting documents together. Business Operations adds commercial and costing workflows where enabled. Teach the source activity, review decisions, and recorded outcomes together, rather than treating an export or prepared claim as a completed external submission.'),
       scene('verify','Availability is part of configuration',['Check the release and department access','Confirm modules, permissions, and entitlements','Configure, test, and review the observed result'],
        'Feature availability depends on the deployed release and department access. Some features need an enabled module, a permission, an add-on, or protection enrollment. The source catalog marks Enhanced AI as planned. Buying an add-on is separate from configuring it. Setup Report helps review configuration evidence; it does not prove that every operational workflow or notification has succeeded.'),
       scene('exercise','Learn by doing',['Choose your role-based learning path','Practice in a department with sample data','Keep the result and follow-up owner'],
        'Choose the learning path that matches your responsibility: administrator, dispatcher, member, or specialist. Each chapter explains a department problem, the relevant features, setup decisions, and a practice task. These illustrated lessons are based on the current source. Live screen walkthroughs will be recorded against a verified demo department, with the same scenarios and feature scripts.')
      ]}
    lessons.insert(0,intro)
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    manifest={'title':'Resgrid Academy','prepared_on':'2026-10-01','source_head':head,
              'source_scope':'Current working tree, including uncommitted source changes; not a deployed release guarantee.',
              'format':'1080p illustrated lessons with synthetic narration, subtitles, chapters, and editable sources',
              'walkthrough_status':'Live application and mobile screen recordings pending a demo environment.',
              'coverage':{'areas':len(ORDER),'catalog_features':len(caps),'catalog_settings':len(settings),
                          'user_controller_source_files':len(controller_rows),'unique_controller_types':len(action_index),'unassigned_controller_sources':[c['source_file'] for c in controller_rows if c['area']=='unassigned']},
              'lessons':lessons,'features':caps,'settings':settings,'controllers':controller_rows,
              'public_reference':['https://docs.resgrid.com/','https://resgrid.com/'],
              'learning_paths':{
                'Administrator':['00-start','01-people','02-security','03-units','04-apps','06-communication','20-plans','17-automation'],
                'Dispatcher':['00-start','05-calls','03-units','07-mapping','06-communication','08-shifts','10-knowledge','18-ptt'],
                'Member':['00-start','04-apps','08-shifts','06-communication','09-training','11-checklists'],
                'Specialist':['00-start','12-maintenance','13-inventory','14-records','15-deployments','16-business','19-adp'],
                'Complete series':[m['id'] for m in lessons]}}
    (OUT/'course.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    for m in lessons:
        text=[m['title'],'Audience: '+m['role'],m['status'],'']
        for i,s in enumerate(m['scenes'],1):text += [f'SCENE {i}: {s["title"]}', 'ON SCREEN: '+' | '.join(s['body']), 'NARRATION: '+s['narration'],'']
        (OUT/'scripts'/(m['id']+'.txt')).write_text('\n'.join(text)+'\n')
    for c in caps:
        text=[c['label'],'Production status: source-backed recording brief; capture pending',
              'Problem / impact: '+c['value'],'What it does: '+c['purpose'],
              'Prerequisites: '+json.dumps(c['requirements']), 'Release: '+c['release_status'],'',
              'CAPTURE SCRIPT']+[f'{i}. {step}' for i,step in enumerate(c['capture_steps'],1)]+[
              '', 'FIELDS FOUND IN THE OWNING VIEW: '+', '.join(c['view_fields']),
              'Screen locator for the editor: '+json.dumps(c['location']),
              'Source evidence: '+json.dumps(c['source']), 'Documentation reference: '+c['docs_url'],
              '', 'Before release: confirm labels, permissions, exact save/closeout behavior, target version, and the visible outcome in the demo application.']
        (OUT/'scripts'/('feature-'+c['id']+'.txt')).write_text('\n'.join(text)+'\n')
    with (OUT/'coverage.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['feature_id','area','lesson','feature','release_status','controller','action','action_found_in_source','capture_status','docs_reference'])
        for c in caps:writer.writerow([c['id'],c['area'],c['lesson'],c['label'],c['release_status'],c['location']['Controller'],c['location']['Action'],c['owner_action_in_source'],c['capture_status'],c['docs_url']])
    (OUT/'production'/'controller-coverage.json').write_text(json.dumps(controller_rows,indent=2)+'\n')
    print(json.dumps(manifest['coverage'],indent=2))

if __name__ == '__main__':
    raise SystemExit('This is the original catalog scaffold. Edit the retained course sources and use scripts/build.py for this edition.')
