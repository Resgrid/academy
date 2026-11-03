"""Freeze actual Core road directions and Unit guidance, preserving raw pixels."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path

S=Path(__file__).resolve().parents[1]
NAME='core-indoor-call-location'
RAW=S/'captures/expansion/core-indoor-call-location-20261102'
OUT=S/'expansion/plans'/f'{NAME}-source-20261103'
SCENES=[('Review the room and its search controls',
  [9],
  ['Region Properties', 'Briefing room - training', 'Type', 'Searchable in dispatch', 'Dispatchable', 'Save Region'],
  'In the ground-floor Region Editor, select the Briefing room polygon to open Region Properties. Review its Name, Room Type, Color '
  'and Description. Searchable in dispatch is checked, while Dispatchable is clear in this example. These are separate options. We '
  'will verify the search setting through New Call, rather than assuming both checkboxes mean the same thing.'),
 ('Hide the room from new searches',
  [10, 11],
  ['Searchable in dispatch', 'Save Region', 'Indoor Location', 'No results found'],
  'Clear Searchable in dispatch and select Save Region. On New Call, open Indoor Location and search for Briefing. The returned '
  'search now says No results found. This removes the room from that new selection search. It has not deleted the underlying floor '
  'plan or the room polygon.'),
 ('Restore the search option and verify it',
  [12, 13],
  ['Searchable in dispatch', 'Save Region', 'Indoor Location', 'Briefing room - training'],
  'Return to the same room’s properties, check Searchable in dispatch and save again. Repeat the Indoor Location search on New Call. '
  'Briefing room now returns as a selectable result. Dispatchable remains clear during this test. The actual returned option verifies '
  'which setting controls this search in the recorded system.'),
 ('Select the indoor reference and keep the outdoor position accurate',
  [1, 2, 4, 3],
  ['Indoor Location', 'Briefing room - training', 'Lat', 'Lng', 'Set Pin on Map'],
  'Select Briefing room from Indoor Location. Review the selected room name before saving the call. The outdoor location is separate. '
  'This fictional exercise also enters a latitude and longitude and uses Set Pin on Map to place the outdoor marker. Selecting an '
  'indoor room has not automatically supplied those outdoor coordinates. Review the outdoor map and the indoor reference together so '
  'responders have the intended context.'),
 ('Save pending and reopen the retained reference',
  [5, 6, 7, 8],
  ['Save as pending (do not dispatch yet)',
   'Create and Dispatch Call',
   'Pending Calls',
   'View',
   'Update Call',
   'Indoor Location',
   'Briefing room - training'],
  'After preparing the call information, select Save as pending, do not dispatch yet. The submit button still reads Create and '
  'Dispatch Call, so verify that the pending checkbox is selected before submitting this exercise. The returned Pending Calls list '
  'contains the saved call. Open View and confirm the Pending banner. Then use Update Call and scroll back to Indoor Location. '
  'Briefing room is still selected. This checks the persisted reference independently of the original form.'),
 ('Distinguish a saved room from a live location',
  [9, 8],
  ['Region Properties', 'Indoor Location', 'Briefing room - training'],
  'The floor plan and selected room are stored references. They do not establish who is currently inside the room, track movement or '
  'confirm physical arrival. Keep that distinction clear when briefing a crew. A community paramedicine or mental health team can use '
  'a reviewed coordination-room reference; search-and-rescue, security, wildland support and industrial teams can use equivalent '
  'named areas. Use verified local map information and the appropriate live-location tools separately. This exercise demonstrates '
  'room search and a saved pending-call reference.')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Keep frozen sources intact.'
 rows=json.loads((RAW/'manifest.json').read_text());num={int(r['id'][:3]):r for r in rows}
 used=sorted({n for _,ns,_,_ in SCENES for n in ns});now=datetime.now(timezone.utc).isoformat();screens=[]
 for n in used:
  r=deepcopy(num[n]);dom=RAW/(r['id']+'.txt');assert sha(S/r['file'])==r['sha256']
  r['app']=r['app'].capitalize()
  r.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_personally_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':now,'sha256':r['sha256'],'method':'Root personally viewed all four original indoor-call source sheets. Actual room properties, search-off/no-results and restored result, separate outdoor coordinates, pending save/readback and retained room selection are visible. No pixel edits or final-video approval.'});screens.append(r)
 lesson={'id':NAME,'title':'Make indoor rooms searchable and retain a call reference','app':'Core','summary':'Verify room search availability, distinguish outdoor and indoor locations, and reopen a saved pending call to check the retained room.','audience':['Department administrators','Dispatch coordinators','Facility and operations supervisors'],'prerequisites':['A reviewed custom indoor map, ground-floor image and named room; see the floor-plan setup lesson.','Appropriate region and call administration permissions in a fictional training department.'],'scenes':[{'id':f'{i:02}','title':t,'route':'/User/Dispatch/NewCall','capture_refs':[num[n]['id'] for n in ns],'required_labels':labels,'narration':speech,'practice':t,'capture_intent':'Show the actual room property, returned search option, pending save or reopened reference being explained.'} for i,(t,ns,labels,speech) in enumerate(SCENES,1)],'candidate_only':True,'export_ready':False,'publication_approved':False,'source_files':[],'sector_examples':[{'sector':v,'scenario':'Maintain reviewed named indoor references and verify that the intended call keeps its room context.'} for v in ['Community paramedicine and mental health response','Search and rescue','Security','Wildland','Industrial emergency response','Fire/EMS']],'scope_limits':['Source proposal only; complete speech/caption correspondence, genuine listening, actual encoded-frame and playback reviews remain required.','Actual Core UI changed Searchable for roomf57fb4a2 off/on and verified absent/returned New Call search results while Dispatchable remainedfalse. Pending call51018 retained the selected room and separate outdoor39.7394113,-104.9916387 coordinates after save and reopen. The historical source sequence first saved the call, then tested search availability; tutorial groups the settings exercise before the independent saved-call example. No call dispatch, physical arrival, occupancy, sensor fix or indoor live tracking is claimed. Ground floor image is a self-authored fictional schematic.']}
 OUT.mkdir();(OUT/'raw-manifest.snapshot.json').write_bytes((RAW/'manifest.json').read_bytes())
 manifest={'schema_version':1,'id':NAME,'screenshots':screens,'raw_manifest':{'file':(OUT/'raw-manifest.snapshot.json').relative_to(S).as_posix(),'sha256':sha(RAW/'manifest.json')},'excluded_sources':[{'id':r['id'],'reason':'Redundant or superseded before the actual successful returned guidance.'} for r in rows if int(r['id'][:3]) not in used]}
 for f,v in [('lesson.candidate.json',lesson),('captures.reviewed.json',manifest),('source-review.json',{'reviewer':'Root','reviewed_at':now,'actual_images_reviewed':[r['id'] for r in screens],'source_pixels_unchanged':True,'final_video_approval_inferred':False})]:(OUT/f).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
 (OUT/'narration.txt').write_text('\n\n'.join(x['narration'] for x in lesson['scenes'])+'\n')
 print(json.dumps({'lesson':NAME,'scenes':len(SCENES),'sources':len(screens),'words':len((OUT/'narration.txt').read_text().split()),'video_complete':False}))
if __name__=='__main__':main()
