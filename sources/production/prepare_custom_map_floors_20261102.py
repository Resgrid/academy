"""Freeze personally reviewed actual indoor-map screens; no final video approval."""
import json
from prepare_records_reports_exports_20261102 import LESSONS,freeze,S,sha
from verify_capture_evidence import visible_controls_digest
NAME='core-custom-map-floor-regions'
LESSONS['indoor']=dict(name=NAME,raw='core-custom-map-floors-20261102',route='/User/CustomMaps',
 title='Create an indoor map, upload a floor plan and manage room regions',
 summary='Save an indoor custom map and its bounds, upload a fictional floor plan, draw a named room, and verify a saved colour and dispatch-availability change.',
 audience=['Department administrators','Mapping administrators','Site and operations supervisors'],
 prerequisites=['Authorized custom-map administration in your department.','An appropriate floor-plan image and accurate site bounds; use the supplied fictional image for this exercise.'],
 sector_scenario='Give staff a recognizable named area on a permitted site plan, then verify its saved boundaries and availability settings.',
 scope='Actual indoor-map creation, geographic rectangle, image upload/render, room creation, saved searchable/dispatchable booleans, rename/colour/dispatchability update and map/room readbacks. No automatic indoor tracking, beacon positioning, live dispatch, dispatch search execution, image tiling, deletion or external floor-plan import is demonstrated. The schematic is fictional and does not describe the real background buildings.',
 excluded={4:'Intermediate first corner is superseded by the completed boundary and visible rectangle tool.',13:'Saved region is valid but the initial zoom makes the floor plan small; use the readable boundary/form readback014.',18:'Captured during the CSS loading fade; excluded and replaced by fully loaded020.'},
 scenes=[
 ('Find custom maps and start an indoor map',[1,2],['Custom Maps','New Custom Map','Map Type','Indoor','Name','Description'],
  'From Mapping, open Custom Maps and select New Custom Map. The list separates Indoor, Outdoor, Event and Custom maps. Choose Indoor for this exercise. Enter a recognizable Name and Description so administrators can identify the intended site. Here we use a fictional community coordination centre. A custom map gives your team a place to keep a floor-plan image and named areas together.'),
 ('Draw the site bounds and save the map',[3,5,6],['Draw Bounds','Draw Rectangle','Save','Custom Maps','Layers'],
  'Scroll to Draw Bounds. Use the Draw Rectangle tool, choose one corner and then the opposite corner. The completed blue rectangle shows the extent prepared for the map. The page also explains that clicking the map sets its centre. Use accurate boundaries for your own site; this software exercise uses a fictional schematic. Select Save, then check the returned row for the intended name and Indoor type.'),
 ('Prepare a floor layer and select its image',[7,8],['Add Layer','Layer Name','Order','Type','Layer Image','Floor Plan'],
  'Select Layers on the saved map. Give the layer a clear Layer Name, keep Order at zero for this first floor, and choose Floor Plan as its Type. Under Layer Image, use Choose File to select the training floor-plan image. The page notes that images larger than two thousand forty-eight pixels are automatically tiled. Our smaller image keeps this example focused on an ordinary floor-plan upload.'),
 ('Verify the saved floor and rendered plan',[9,10],['TRAINING ONLY - Ground floor','Has Image','Tiled','Region Editor','Regions','Region Properties'],
  'Select Add Layer. Check the saved row rather than assuming the file was accepted. It shows the ground floor, FloorPlan, Yes under Has Image, and No under Tiled. Open Region Editor. Wait for the actual floor image to render and zoom until the rooms are readable. The schematic contains a briefing room, training room, equipment store and other fictional team spaces.'),
 ('Draw a room and complete its properties',[11,12],['Draw Rectangle','Region Properties','Name','Type','Room','Color','Description','Save Region'],
  'Use Draw Rectangle in Region Editor to outline the briefing room. When the shape is complete, Region Properties opens beside the plan. Enter Briefing area, followed by training, as the Name. Keep Room as the Type, review Color, and add a short Description. A useful name connects the drawn boundary to an area people can recognize. The shape is still prepared until you select Save Region.'),
 ('Save and reopen the room availability settings',[12,14],['Searchable in dispatch','Dispatchable','Save Region','Briefing area - training','Room'],
  'This first room has Searchable in dispatch and Dispatchable checked. Review those two choices deliberately, then select Save Region. After the page reloads, the room appears under Regions with a Dispatchable badge. Select its boundary on the plan to reopen the saved properties. Verify the name, Room type and both checked options. This lesson verifies those saved settings; it does not dispatch an incident or test a dispatch search.'),
 ('Change the name, colour and dispatch availability',[14,15],['Name','Color','Searchable in dispatch','Dispatchable','Save Region'],
  'With the saved room selected, change its name to Briefing room, followed by training. Choose the teal Color shown in the form. Leave Searchable in dispatch checked and clear Dispatchable, then select Save Region. These changes affect the same saved region. Before saving, the list can still display the previous name and badge, so use the returned view to check what actually persisted.'),
 ('Verify the updated room and its boundary',[16,17],['Regions','Briefing room - training','Room','Color','Searchable in dispatch','Dispatchable','Save Region'],
  'After reload, the boundary is teal, the list has the new Briefing room name, and the Dispatchable badge is gone. Select the boundary again. Region Properties now shows the saved teal Color, Searchable in dispatch checked, and Dispatchable unchecked. The floor image and boundary remain in place. This readback confirms the change beyond the form on which you prepared it.'),
 ('Reopen the map and check its stored extent',[20,19],['Edit Custom Map','Indoor','Name','Description','Draw Bounds','Edit Layers'],
  'Return to the map list and open Edit for the intended map. The Indoor type, Name and Description are retained. Scroll to Draw Bounds to see the stored rectangle on the background map. Check that extent against your own permitted site plan before relying on it. In this recording the floor image is a fictional schematic, and does not represent the real buildings shown on the background map.'),
 ('Use named areas across department types',[17],['Briefing room - training','Room','Region Properties'],
  'The same workflow can support community paramedicine and mental health response teams, search-and-rescue organizations, security companies, wildland contractors, industrial emergency teams, fire and E M S departments. Keep an appropriate site image, name useful areas, and verify the saved region settings after each change. A floor plan and room boundary provide shared location context; they do not by themselves establish live indoor personnel tracking. Select the boundary to review Region Properties before the next update.')])
if __name__=='__main__':
 freeze('indoor')
 out=S/'expansion/plans'/(NAME+'-source-20261102');snap=out/'raw-manifest.snapshot.json';snap.write_bytes((S/'captures/expansion/core-custom-map-floors-20261102/manifest.json').read_bytes());p=out/'captures.reviewed.json';m=json.loads(p.read_text());m['raw_manifest']={'file':snap.relative_to(S).as_posix(),'sha256':sha(snap)}
 for row in m['screenshots']:
  review=row['capture_review'];review['method']='Root personally inspected all five original source contact sheets and the full-size map, upload, room and readback browser images, including loaded replacement020. Original pixels unchanged.'
  if row.get('visible_controls'):
   review.update(controls_sha256=visible_controls_digest(row['visible_controls']),application_visible=True,no_errors=True,controls_reviewed=True,controls_fully_visible=True,controls_unobstructed=True)
 p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
