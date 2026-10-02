"""Add source-present workflows that the public Admin Assist feature catalog groups broadly."""
import json
import re
from pathlib import Path
from prepare import ROOT, OUT, scene, source_ref

# id, area, source file, controller, action, title, purpose, setup, observed result
EXTRAS = [
 ('passkeys','security','Passkeys','Passkeys','RegistrationOptions','Passkeys and account recovery',
  'Passkeys add a device-backed sign-in factor and need deliberate naming, removal, and recovery handling.',
  'Enroll from account security on a compatible demo device. Name the credential and review the remaining recovery factors.',
  'Confirm an actual sign-in and check the credential list after a controlled removal.'),
 ('messaging-account-links','communication','MessagingAccounts','MessagingAccounts','Index','Link a messaging-platform account',
  'Account linking associates a member with a configured external assistant platform.',
  'Confirm a platform is configured, generate a short-lived linking code, and complete linking in the intended platform.',
  'Review the linked identity and a controlled permitted action. Keep the temporary code out of the recording.'),
 ('connect-profile','knowledge','Connect','Connect','Profile','Connect department profiles and posts',
  'Connect provides a department profile, posts, and communication surfaces.',
  'Review the intended public profile content, then prepare a fictional profile and sample post through their owning screens.',
  'Check the visible audience and the published sample content in the demo environment.'),
 ('navigation-search','knowledge','Search','Search','GetSearchResults','Search and navigation',
  'Navigation search helps members find the work they are authorized to access.',
  'Search for a known department feature using a member account and an administrator account.',
  'Compare the returned navigation options with each account permission scope.'),
 ('resource-orders','deployments','Orders','Orders','New','Mutual-aid resource orders',
  'Resource orders describe requested resources and the fills departments offer or accept.',
  'Review ordering settings and participating departments. Create a fictional request, offer a fill, and review acceptance.',
  'Reconcile requested quantities, accepted fills, and the remaining resource need.'),
 ('external-order-lifecycle','deployments','DeploymentOrders','DeploymentOrders','New','External orders and deployment closeout',
  'An external order records the department fills and their mobilization, release, and actual return home.',
  'Enter an approved sample external order, link its deployment, record the fill transitions, and complete closeout.',
  'Review dates and resource identity. This workspace records manual entry and artifact snapshots; it is not an external ordering connector.'),
 ('deployment-time-reports','deployments','RecordDeployments','RecordDeployments','TimeReport','Deployment time and export reports',
  'Read-only deployment reports bring time entries, supporting artifacts, and export outputs together.',
  'Open a recorded demo deployment and review its time report, summary, and available exports.',
  'Reconcile each time entry with the roster and recorded dates before finance review.'),
 ('record-quality-review','records','RecordsQuality','RecordsQuality','Rubric','Quality review and sampling',
  'Post-finalization review uses rubrics, sampling, scores, and trends to identify reporting follow-up.',
  'Confirm rollout and reviewer access, configure an approved rubric, sample finalized records, and score a demo review.',
  'Review criteria, sample scope, notes, and amendment recommendations without treating a score as a rewritten incident report.'),
 ('records-health','records','RecordsQuality','RecordsHealth','Index','Records health and prevention attachments',
  'Records health and prevention attachment screens make retained record support and issues visible to authorized users.',
  'Review the records health view and attach a synthetic support file to an appropriate prevention record.',
  'Verify parent-record access and the restricted-attachment behavior on the intended member account.'),
 ('incident-analysis','records','IncidentAnalysis','IncidentAnalysis','Edit','NERIS incident analysis lifecycle',
  'Incident analysis is a separately validated and submitted artifact linked to an incident report.',
  'Start analysis from a demo incident, edit and validate it, then review finalization and submission readiness.',
  'Confirm the analysis lifecycle separately from the incident report. Submission waits for the required incident destination identity.'),
 ('community-risk-reduction','records','RecordPermits','RecordCrr','Index','Community risk reduction activities',
  'Community risk reduction records education and prevention activity with attendee counts.',
  'Confirm the community-risk feature and access, record a fictional activity, and review its summary and analytics scope.',
  'Check counts, dates, ownership, and the activity audience without placing attendee personal information into the example.'),
 ('record-revisions','records','RecordDocuments','RecordDocuments','Diff','Record revisions and differences',
  'Revision and difference views help reviewers understand how a record changed.',
  'Open two revisions of a synthetic record and review their differences and any permitted export.',
  'Confirm the selected revisions and access to the parent record before interpreting the difference.'),
 ('submission-reconciliation','records','RecordSubmissions','RecordSubmissions','Details','Submission outcomes and reconciliation',
  'Submission details and reconciliation keep a recorded report distinct from its external filing outcome.',
  'Review a test submission status and reconcile a known destination response through the owning workflow.',
  'Check the destination identity, accepted or failed outcome, and any corrections needed.'),
 ('record-inventory-evidence','records','RecordsInventory','RecordsInventory','Edit','Inventory use attached to records',
  'Record inventory workflows connect consumption and evidence to the incident or activity record.',
  'Link synthetic inventory use to a record, refresh its evidence, and review supported reversal handling.',
  'Reconcile the record, item, quantity, and corresponding stock movement.'),
 ('deployment-connectors','records','RecordDeploymentConnectors','RecordDeploymentConnectors','New','Deployment connector administration',
  'Deployment connector screens manage connector configuration, enablement, tokens, and runs.',
  'Review connector terms and ownership, configure a demo destination, and inspect a controlled run.',
  'Confirm the target integration, observed run, and token lifecycle. Mask credentials during capture.'),
 ('maintenance-parts-costs','maintenance','WorkOrderOperations','WorkOrders','Operations','Parts, vendor charges, and approvals',
  'Work-order operations connect parts, vendor charges, approval requests, and spending policy to a repair.',
  'Review policy, reserve a sample part, record its movement and a vendor charge, then request the required approval.',
  'Reconcile repair cost and part movement with the work order and approval decision.'),
 ('maintenance-bulk','maintenance','WorkOrderOperations','WorkOrders','Bulk','Preview bulk maintenance changes',
  'Bulk maintenance tools preview imported rows or assignment changes before applying them.',
  'Use the import template or select demo rows, preview the proposed changes, and review the row outcomes.',
  'Confirm the preview, current revisions, and the observed result after an authorized demo apply.'),
 ('ai-dispatch-rollout','ai','AiDispatch','AiDispatch','Index','AI dispatch settings and activity',
  'The checkout contains gated AI dispatch settings for enrichment fields, confidence, sender scope, token limits, and activity.',
  'Confirm host enablement and department rollout before reviewing the settings. Saving settings alone does not start enrichment.',
  'Check the Running state, activity outcomes, and usage. This source-present feature is unverified on the target deployment.')
]

def main():
    path=OUT/'course.json';data=json.loads(path.read_text()); existing={f['id'] for f in data['features']}
    for fid,area,filename,controller,action,title,purpose,setup,verify in EXTRAS:
        if fid in existing:continue
        source=ROOT/f'Web/Resgrid.Web/Areas/User/Controllers/{filename}Controller.cs'
        module=next(m for m in data['lessons'] if m['area']==area)
        entry=dict(id=fid,area=area,lesson=module['id'],label=title,purpose=purpose,value=purpose,setup=setup,
                   requirements=[],release_status='source-present; deployment unverified',location={'Controller':controller,'Action':action},
                   source=source_ref(source,'class '+controller+'Controller'),capture_status='not recorded',
                   verification_status='source reviewed; deployment unverified',docs_url='https://docs.resgrid.com/',
                   owner_action_in_source=True,view_fields=[],capture_steps=[setup,verify])
        data['features'].append(entry);module['features'].append(fid)
        module['scenes'].insert(len(module['scenes'])-3,scene('feature',title,[purpose,setup],
          purpose+' '+setup+' '+verify+' Confirm availability in the demo department before recording the live workflow.',feature_id=fid,tag='Source-present workflow'))
        (OUT/'scripts'/('feature-'+fid+'.txt')).write_text('\n'.join([title,'Capture pending; source-present workflow',
         'Problem and impact: '+purpose,'Configuration: '+setup,'Verification: '+verify,
         'Owner: '+controller+' / '+action,'Evidence: '+json.dumps(entry['source'])])+ '\n')
    supplement_lessons=[
      {'id':'22-relay','area':'relay','title':'Relay: bring an audio dispatch feed into Resgrid','role':'System operators and dispatch administrators',
       'status':'reference-based illustrated lesson; live walkthrough pending','features':[],
       'public_reference':'https://docs.resgrid.com/apps/relay/',
       'scenes':[
         scene('title','Connect the existing dispatch feed',['Scanner or audio feed','Tone detection and captured dispatch audio'],
          'Resgrid Relay listens to an audio feed, detects configured tones, records dispatch audio, and creates calls for the associated department or groups. It can help departments connect an existing paging process when they cannot modify the upstream dispatch system.'),
         scene('workflow','Prepare a controlled audio test',['Identify the approved tone pair','Connect and check the audio input','Review recording and recipient configuration'],
          'The recording plan begins with an approved sample audio feed and known tone frequencies. Check the input signal, configure the intended recording behavior, and review the department or group recipients. Verify the exact installer and interface against the supported Relay release before capture.'),
         scene('verify','Verify the resulting call',['Play a synthetic tone-and-voice test','Inspect the call, captured audio, and recipients'],
          'Use synthetic test audio. Inspect the resulting call, the captured recording, and the intended recipients. Test nonmatching tones separately and document what was observed. The public Relay installation page contains incomplete older steps, so it is a feature reference rather than a verified modern installation procedure.'),
         scene('exercise','Keep the test repeatable',['Retain a sample audio fixture','Record configuration, release, and observed result'],
          'Retain the synthetic audio fixture, selected release, approved configuration, and observed test result. A recorder will need the supported Relay application and an audio test setup to turn this briefing into a live walkthrough.')
       ]},
      {'id':'23-self-hosting','area':'self-hosting','title':'Self-hosting: configuration and operating responsibilities','role':'Self-hosted system operators',
       'status':'reference-based illustrated lesson; infrastructure walkthrough pending','features':[],
       'public_reference':'https://docs.resgrid.com/self-hosted/quick-start/',
       'scenes':[
         scene('title','Plan a self-hosted environment',['Choose an evaluation deployment','Plan web, API, and event endpoints'],
          'The current self-hosted quick start describes a single Linux-server evaluation using Docker Compose. Plan separate web, API, and events hostnames. Infrastructure operation is a separate learning path from department administration.'),
         scene('workflow','Configure, initialize, verify',['Review the supported installer and configuration','Start the stack and inspect migration progress','Create the first account and department'],
          'Review the supported installer, generate deployment-specific credentials, and inspect the resulting configuration. Start the stack, review worker migration progress, and verify all three endpoints. Create the first account and department after initialization.'),
         scene('feature','Department settings and host settings',['Department screens configure operational behavior','Static config classes define host configuration'],
          'Department screens configure operational behavior. In this checkout, host configuration uses public static fields in configuration classes. The configuration processor reads JSON keys or environment variables and assigns those fields. Use the source and release documentation to identify the exact host setting; avoid applying a generic appsettings recipe.'),
         scene('verify','Operate and recover the system',['Back up data and configuration before updates','Retain the prior release and test recovery'],
          'Before updating, back up the data and configuration and retain prior image references. A rollback can require restoring the database as well as the application. Treat a running evaluation as the start of operations preparation, with monitoring and a tested recovery procedure.'),
         scene('exercise','Choose the infrastructure walkthrough',['Linux Compose • Windows • Kubernetes / k3s • RICK','Record the supported release and deployment layout'],
          'Detailed infrastructure capture needs the chosen deployment layout: Linux Compose, Windows, Kubernetes or k3s, or an Incident Command Kit. Record the supported release and verify installation, endpoint connectivity, backup, and recovery in that environment. Use the linked official guides for the matching layout.')
       ]}
    ]
    ids={m['id'] for m in data['lessons']}
    for m in supplement_lessons:
        if m['id'] not in ids:data['lessons'].append(m)
    data['coverage']['supplemental_source_workflows']=len(EXTRAS)
    data['coverage']['recording_briefs']=len(data['features'])
    data['learning_paths']['Complete series']=[m['id'] for m in data['lessons']]
    data['learning_paths']['System operator']=['00-start','23-self-hosting','22-relay','17-automation','02-security']
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    for m in data['lessons']:
        text=[m['title'],'Audience: '+m['role'],m['status'],'']
        for i,s in enumerate(m['scenes'],1):text += [f'SCENE {i}: {s["title"]}', 'ON SCREEN: '+' | '.join(s['body']), 'NARRATION: '+s['narration'],'']
        (OUT/'scripts'/(m['id']+'.txt')).write_text('\n'.join(text)+'\n')
    print('Supplemented:',len(data['features']),'feature briefs and',len(data['lessons']),'lessons')

if __name__=='__main__':main()
