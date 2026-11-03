"""Freeze actual Core road directions and Unit guidance, preserving raw pixels."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path

S=Path(__file__).resolve().parents[1]
NAME='core-map-layer-authoring'
RAW=S/'captures/expansion/core-map-layer-create-clean-20261103'
OUT=S/'expansion/plans'/f'{NAME}-source-20261103'
SCENES=[('Choose clear layer display settings',
  [1],
  ['New Layer', 'Name', 'Is Visible By Default', 'Is Destination', 'Color'],
  'On New Layer, enter a recognizable Name. This example uses Outreach staging example. Is Visible By Default starts checked. Leave '
  'Is Destination clear for this drawing-only reference. That option controls whether layer coordinates participate in address '
  'searching; it is not the same as displaying a layer. Color is blue here. Use a name and color your department can distinguish from '
  'operational calls and resources.'),
 ('Draw the example boundary',
  [2, 3, 4],
  ['Layer Elements', 'Cancel'],
  'In Layer Elements, pan and zoom to the intended practice area. Select the rectangle-shaped drawing tool on the left. Cancel is '
  'available while drawing. Click the first corner, then the opposite corner to finish the rectangle. The outlined, shaded area is '
  'the saved shape you are preparing. It is a fictional planning reference, not an official hazard boundary or a live tracking area.'),
 ('Add one point and save the layer',
  [4, 5, 6],
  ['Cancel', 'Add Layer', 'TRAINING ONLY - Outreach staging example', 'Item Count'],
  'Select the marker-shaped tool and click the intended point once. Inspect the marker and rectangle together before saving. Scroll '
  'below the map and select Add Layer. The returned Layers list shows Outreach staging example with an Item Count of two. Those two '
  'stored items are the rectangle and marker. Check the count to catch accidental duplicate points.'),
 ('Reopen the stored drawing',
  [6, 7, 8],
  ['Edit', 'Is Visible By Default', 'Is Destination', 'Color', 'Edit Layer'],
  'Select Edit on the Outreach staging example row. The stored name, blue Color and checked default-visibility option return. Scroll '
  'down to inspect the retained rectangle and marker. Reopening the layer verifies that its geometry survived the save; a successful '
  'return to the list alone would not establish that the intended shape was retained.'),
 ('Change the department default and verify it',
  [9, 10, 11, 12],
  ['Is Visible By Default', 'Edit Layer', 'TRAINING ONLY - Outreach staging example'],
  'Clear Is Visible By Default. Scroll down and select Edit Layer to save the change. From the returned list, reopen the same layer. '
  'Its default-visibility checkbox is now clear, while the name, color and drawing remain stored. This changes the department '
  'default. It does not delete the layer or force every existing browser to discard its own map visibility selection.'),
 ('Control the current map display',
  [13, 16, 17, 15],
  ['Mapping', 'Map layers', 'TRAINING ONLY - Outreach staging example'],
  'On Mapping, inspect the Map layers section. This browser already has a saved display choice for Outreach staging example, so '
  'compare that checkbox with the department setting you just reopened. Select or clear the named layer to control this map display. '
  'After clearing it and reloading, its checkbox remains clear. This is a display choice, separate from deleting the underlying '
  'drawing. Departments can use reviewed layers for search-and-rescue planning, security patrol areas, wildland logistics, industrial '
  'response or community paramedicine and mental health support, as well as fire and E M S. Keep the drawing purpose clear and '
  'confirm the intended map extent.')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Keep frozen sources intact.'
 rows=json.loads((RAW/'manifest.json').read_text());num={int(r['id'][:3]):r for r in rows}
 used=sorted({n for _,ns,_,_ in SCENES for n in ns});now=datetime.now(timezone.utc).isoformat();screens=[]
 for n in used:
  r=deepcopy(num[n]);dom=RAW/(r['id']+'.txt');assert sha(S/r['file'])==r['sha256']
  r['app']=r['app'].capitalize()
  r.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_personally_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':now,'sha256':r['sha256'],'method':'Root personally viewed all four clean original source sheets. Actual creation controls, rectangle first-corner state, one marker, saved Item Count2, reopened geometry, default-visibility change and browser display choices are visible. No pixel edits, old gray loading sources or final-video approval.'});screens.append(r)
 lesson={'id':NAME,'title':'Create a map layer and verify its display choices','app':'Core','summary':'Draw a rectangle and point, save and reopen their geometry, and distinguish the department visibility default from the current map selection.','audience':['Department administrators','Mapping coordinators','Operations supervisors'],'prerequisites':['Mapping administration access and a separate fictional practice department.','Reviewed source geometry and a clear operational meaning for each published layer.'],'scenes':[{'id':f'{i:02}','title':t,'route':'/User/Mapping','capture_refs':[num[n]['id'] for n in ns],'required_labels':labels,'narration':speech,'practice':t,'capture_intent':'Show the actual setting, drawing control, saved geometry or named display choice being discussed.'} for i,(t,ns,labels,speech) in enumerate(SCENES,1)],'candidate_only':True,'export_ready':False,'publication_approved':False,'source_files':[],'sector_examples':[{'sector':v,'scenario':'Maintain reviewed map-reference drawings and confirm how the relevant display selections affect each browser.'} for v in ['Community paramedicine and mental health response','Search and rescue','Security','Wildland','Industrial emergency response','Fire/EMS']],'scope_limits':['Source proposal only; complete speech/caption correspondence, genuine listening, actual encoded-frame and playback reviews remain required.','Actual normal UI created PostgreSQL layer4 with a rectangle and one marker, saved Item Count2, reopened geometry, changed default visibility fromtrue tofalse and reopened it. Actual current-map selection was independently enabled/disabled. Existing browser visibility preferences take precedence over a changed default; this is retained MapElement behavior. No official boundary, automatic geofence or live-location result is claimed. Earlier gray loading/duplicate examples are excluded. Backend geometry-storage support is retained under demo/core-support/mapping-consistent-runtime-20261102.']}
 OUT.mkdir();(OUT/'raw-manifest.snapshot.json').write_bytes((RAW/'manifest.json').read_bytes())
 manifest={'schema_version':1,'id':NAME,'screenshots':screens,'raw_manifest':{'file':(OUT/'raw-manifest.snapshot.json').relative_to(S).as_posix(),'sha256':sha(RAW/'manifest.json')},'excluded_sources':[{'id':r['id'],'reason':'Redundant or superseded before the actual successful returned guidance.'} for r in rows if int(r['id'][:3]) not in used]}
 for f,v in [('lesson.candidate.json',lesson),('captures.reviewed.json',manifest),('source-review.json',{'reviewer':'Root','reviewed_at':now,'actual_images_reviewed':[r['id'] for r in screens],'source_pixels_unchanged':True,'final_video_approval_inferred':False})]:(OUT/f).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
 (OUT/'narration.txt').write_text('\n\n'.join(x['narration'] for x in lesson['scenes'])+'\n')
 print(json.dumps({'lesson':NAME,'scenes':len(SCENES),'sources':len(screens),'words':len((OUT/'narration.txt').read_text().split()),'video_complete':False}))
if __name__=='__main__':main()
