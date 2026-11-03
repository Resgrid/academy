"""Freeze the personally inspected, successfully saved planned deployment and roster."""
from pathlib import Path
from datetime import datetime, timezone
import json
from prepare_records_reports_exports_20261102 import LESSONS, freeze, S, sha

LESSONS['deployment_setup'] = dict(
 name='core-deployment-setup-roster', raw='core-deployment-administration-20261102', route='/User/Deployments',
 title='Create a deployment and verify its resource roster',
 summary='Choose the deployment purpose and local window, retain agency identifiers, and verify a saved unit, member and equipment roster.',
 audience=['Department administrators','Deployment coordinators','Resource supervisors'],
 prerequisites=['Authorized deployment-management access in a fictional training department.','An existing training unit, active member and contact; all examples are fictional.'],
 sector_scenario='Prepare a named assignment and verify the actual unit, people and equipment committed to it.',
 scope='The recorded deployment is Planned and Operational only. It has one unit, one member without a configured seat, and a free-text equipment entry. Status transitions, time submission/approval, stock transactions and external-order billing have separate execution requirements.',
 excluded={1:'Earlier index capture; use the inspected menu/index pair015/002.',10:'Return control reserved for the equipment-return walkthrough.',11:'Active was selected but a successful status change was not established.',12:'The actual badge remained Planned; an Active selection is not a saved Active status.',14:'Earlier collapsed time-entry selectors; excluded from usable time-entry instruction.'},
 scenes=[
 ('Find the deployment workspace',[15,2],['Deployments','New Deployment'],
  'In Core’s left menu, open Deployments. This workspace keeps a named assignment, its resources, time reports and expenses together. Use it for a community support assignment, a search operation, a security detail or a contractor deployment, as well as fire and E M S work. The list shows each deployment’s status, finance mode, identifiers and window. Select New Deployment to prepare a separate fictional community support exercise.'),
 ('Choose the purpose, finance mode and contact',[3],['Name *','Finance mode','Operational only','Contact','Call ID'],
  'Give the deployment a recognizable Name. Choose Finance mode deliberately. The help explains that Operational only keeps time and expenses for the record, Cost recovery feeds a reimbursement claim, and Billable feeds a customer invoice. This exercise uses Operational only. Select the fictional Community Centre as Contact. Call I D is optional; its help describes one deployment per call. It stays blank in this example. Add Notes that explain the assignment and identify the exercise as fictional.'),
 ('Set the local window and jurisdiction facts',[3],['Window','Home country','Host country','Time zone','Currency','Out of province / state','Travel via air'],
  'Set the Window from November second at eight in the morning to November fourth at six in the evening. In Jurisdiction, choose the home and host countries and their state or province. Both are United States, Illinois here. Review Time zone and Currency. The page explains that the accounting time zone belongs to the deployment, while displayed dates and times use the department’s time zone. This example retains Central Time and U S D. Out of province or state and Travel via air remain unchecked for the local exercise.'),
 ('Retain agency identifiers and save',[4,5],['Agency identifiers','Incident #','Service request #','Resource order #','Request #','Cost code','Point of hire','Save','Saved.','Planned'],
  'Use Agency identifiers for the references supplied for this assignment: Incident number, Service request number, Resource order number, Request number, Cost code and Point of hire. The example uses clearly fictional training references. These fields help the department relate its deployment record to the requesting organization’s paperwork. Select Save, then read the returned details. The Saved message and Planned badge establish that the deployment exists. Verify its window, contact, jurisdiction and currency against the intended assignment.'),
 ('Reopen and verify the duration settings',[5,23],['Edit','Edit Deployment','Window','Max days','3','Cancel'],
  'Use Edit to inspect the stored settings. The reopened Window retains November second at eight through November fourth at six. Max days reads three. When an end has not been supplied, the maximum-days value helps define the deployment window used for resource checks; this example has an explicit end as well. Check the values before making a later scheduling change. This visit only verifies what was stored. Use Cancel to return to the deployment without submitting another edit.'),
 ('Add the unit and verify its row',[6,7],['Roster','Add unit','Call sign','CS-VAN-1','Crew'],
  'In Roster, choose the training community van from the unit selector. Enter C S van one as its Call sign, then select Add unit. The returned row now lists that vehicle and call sign. Its Crew value is initially zero because no member has been assigned to it yet. Adding a unit and adding its people are separate steps. Check the saved unit row before assigning a member to it.'),
 ('Assign the member to the saved unit',[7,8],['Member','Matthew Casey','Unit','Seat','Certification','Seat even when a requirement fails','Add member'],
  'Under Personnel, choose Matthew Casey as Member and select the saved community van as Unit. This training unit has no configured seat, so Seat and Certification remain blank. Read the seat help: marked seats require a personnel role, and certification requirements and expirations are checked. Keep Seat even when a requirement fails unchecked in this exercise. Select Add member. Verify that Casey appears beside the intended unit and that its Crew count becomes one. A unit name alone did not establish that personnel assignment.'),
 ('Record equipment and verify the complete roster',[8,9],['Equipment','Demo radio kit','Add equipment','Issued','Matthew Casey','CS-VAN-1'],
  'In Equipment, enter Demo radio kit, select the same unit and choose Add equipment. The saved row now associates the kit with the van. Its Issued column is a dash in this exercise: this is a free-text deployment equipment entry, and no inventory issue was performed. Review the final roster together. It contains the saved unit and call sign, Casey assigned to that unit, and the named kit. Use the stored rows to verify the assignment rather than relying on a prepared form.'),
 ('Apply the roster process to your department',[9],['Units','Personnel','Equipment','Crew'],
  'Use this same prepare, save and verify process for community paramedicine and mental health response teams, search and rescue, security companies, wildland contractors and industrial emergency teams. Fire and E M S departments use the same workspace. Choose names, contacts, unit assignments and equipment that fit your organization’s work. Confirm the people behind the unit count, and keep the deployment’s identifiers and window useful for the supervisors who will review its work.')])

if __name__=='__main__':
 freeze('deployment_setup')
 cfg=LESSONS['deployment_setup'];out=S/'expansion/plans'/(cfg['name']+'-source-20261102')
 # Preserve the exact raw manifest at this freeze; later lessons append new captures.
 snap=out/'raw-manifest.snapshot.json';snap.write_bytes((S/'captures/expansion'/cfg['raw']/'manifest.json').read_bytes())
 p=out/'captures.reviewed.json';m=json.loads(p.read_text());m['raw_manifest']={'file':snap.relative_to(S).as_posix(),'sha256':sha(snap)}
 for row in m['screenshots']:row['capture_review']['method']='Root personally inspected the original actual browser screenshot individually in this recording session. Source pixels are unchanged.'
 p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 review=out/'source-review.json';d=json.loads(review.read_text());d['method']='Root personally viewed every selected original screenshot individually. The pre-create and later menu/readback captures have explicit roles; no status-change success is inferred.';review.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'immutable_raw_manifest_snapshot':True,'source_only':True,'natural_narration_and_final_video_reviews':'pending'}))
