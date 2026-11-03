"""Freeze actual Core road directions and Unit guidance, preserving raw pixels."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path

S=Path(__file__).resolve().parents[1]
NAME='core-unit-road-guidance'
RAW=S/'captures/expansion/core-route-road-guidance-20261102'
OUT=S/'expansion/plans'/f'{NAME}-source-20261103'
SCENES=[
('Open the planned route directions',[1],['Routes','Directions','TRAINING ONLY - Community supply loop'],
'In Core, open Routes and find the Community supply loop. Select Directions on that plan’s row. This fictional two-stop supply exercise helps a coordinator review the proposed roads before assigning work. The directions are provider estimates for the saved locations. They do not show a vehicle journey or prove that a road is suitable for your vehicle.'),
('Review the whole loop and its estimates',[2],['12.7 km • 31 min (56 min)','Start Route'],
'The Directions page draws the planned loop and displays twelve point seven kilometres, thirty-one minutes, and fifty-six minutes in parentheses. The longer total includes the planned stop dwell times. Review the map and the intended stop locations together. Start Route is available here, but opening this page alone has not started a new execution.'),
('Read the individual road instructions',[3,5,11],['Turn-by-Turn Directions','6.8 km • 14 min','632 m • 3 min','5.3 km • 14 min'],
'Scroll to Turn-by-Turn Directions. Supply point A has its own leg distance and duration, followed by the individual turns. Further down, Community point B has a separate leg. The final Firehouse fifty-one section is the return leg to the station. Read the road names and distances in the relevant section, rather than assuming the overall duration describes every leg.'),
('Check the stop work and planned dwell',[6],['Stop Summary','Stop Name','Dwell (min)','Contact','Notes'],
'Stop Summary brings the saved stop names, addresses, Dwell, Contact and Notes together. This example plans ten minutes at Supply point A and fifteen at Community point B. These are planning values, not measured check-in durations. Check the notes with the crew before beginning. A search-and-rescue supply run, community paramedicine route, security round, wildland support task or industrial response assignment can use the same planning pattern.'),
('Review the Unit preview before starting',[7],['View Route','12.7 km','31m','Start Route'],
'In Unit, View Route shows the same saved plan with two stops, twelve point seven kilometres and thirty-one minutes. Review those details before selecting Start Route. Route planning and the active unit execution are separate states. The stop-completion lesson covers the manual Check In, Check Out and End Route operations after an assignment is started.'),
('Open guidance from the active execution',[9,10],['Active Route','CURRENT STEP','Directions','Distance','Duration','ETA','No traffic data','Open in Maps'],
'On Active Route, review Current Step and select Directions. The returned Directions view shows its own road line, Distance, Duration and E T A. Here it connects Supply point A to Community point B and shows five hundred eighty-three metres and two minutes. This is a shorter scope than the complete station-to-stops-and-return loop shown in Core. Read the endpoints before comparing the totals. No traffic data is shown, and location is unavailable in this software exercise. Open in Maps is available for an external map handoff; that handoff is not performed in this recording.'),
]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Keep frozen sources intact.'
 rows=json.loads((RAW/'manifest.json').read_text());num={int(r['id'][:3]):r for r in rows}
 used=sorted({n for _,ns,_,_ in SCENES for n in ns});now=datetime.now(timezone.utc).isoformat();screens=[]
 for n in used:
  r=deepcopy(num[n]);dom=RAW/(r['id']+'.txt');assert sha(S/r['file'])==r['sha256']
  r['app']=r['app'].capitalize()
  r.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_personally_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':now,'sha256':r['sha256'],'method':'Root personally viewed all three original road-source sheets, full Unit guidance screenshot and the full actual return-leg screenshot. Actual controls and estimated route data are visible. Source008 predates the progress-contract repair and is excluded; actual reopened009 and returned010 replace it. No pixel edits or final-video approval.'});screens.append(r)
 lesson={'id':NAME,'title':'Review road guidance in Core and Unit','app':'Core','summary':'Review a planned road loop, leg instructions and stop dwell, then compare the Unit preview and active-route guidance.','audience':['Dispatch coordinators','Unit crews','Department administrators'],'prerequisites':['A reviewed training route plan with valid stop locations and a configured routing provider.','Appropriate Core and Unit permissions; review actual road suitability separately.'],'scenes':[{'id':f'{i:02}','title':t,'route':'/User/Routes' if i<5 else '/routes','capture_refs':[num[n]['id'] for n in ns],'required_labels':labels,'narration':speech,'practice':t,'capture_intent':'Show actual route controls and returned estimates at the matching narration step.'} for i,(t,ns,labels,speech) in enumerate(SCENES,1)],'candidate_only':True,'export_ready':False,'publication_approved':False,'source_files':[],'sector_examples':[{'sector':v,'scenario':'Plan suitable stops and road references, review their estimates and independently verify the active unit assignment.'} for v in ['Community paramedicine and mental health response','Search and rescue','Security','Wildland','Industrial emergency response','Fire/EMS']],'scope_limits':['Source proposal only; complete speech/caption correspondence, genuine listening, actual encoded-frame and playback reviews remain required.','Actual Mapbox road calculation in the isolated training stack. Core12.7km/31min/56min includes station start/return and25minutes planned dwell. Unit returned583m/2min guidance between its displayed endpoints. No physical journey, GPS fix, traffic result, guaranteed ETA, road suitability or external navigation handoff is claimed. Isolated runtime/provider support and Unit progress-contract compatibility repairs are retained under demo.']}
 OUT.mkdir();(OUT/'raw-manifest.snapshot.json').write_bytes((RAW/'manifest.json').read_bytes())
 manifest={'schema_version':1,'id':NAME,'screenshots':screens,'raw_manifest':{'file':(OUT/'raw-manifest.snapshot.json').relative_to(S).as_posix(),'sha256':sha(RAW/'manifest.json')},'excluded_sources':[{'id':r['id'],'reason':'Redundant or superseded before the actual successful returned guidance.'} for r in rows if int(r['id'][:3]) not in used]}
 for f,v in [('lesson.candidate.json',lesson),('captures.reviewed.json',manifest),('source-review.json',{'reviewer':'Root','reviewed_at':now,'actual_images_reviewed':[r['id'] for r in screens],'source_pixels_unchanged':True,'final_video_approval_inferred':False})]:(OUT/f).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
 (OUT/'narration.txt').write_text('\n\n'.join(x['narration'] for x in lesson['scenes'])+'\n')
 print(json.dumps({'lesson':NAME,'scenes':len(SCENES),'sources':len(screens),'words':len((OUT/'narration.txt').read_text().split()),'video_complete':False}))
if __name__=='__main__':main()
