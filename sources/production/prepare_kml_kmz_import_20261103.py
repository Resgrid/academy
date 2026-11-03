"""Freeze actual Core road directions and Unit guidance, preserving raw pixels."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib,json
from pathlib import Path

S=Path(__file__).resolve().parents[1]
NAME='core-kml-kmz-import'
RAW=S/'captures/expansion/core-kml-kmz-import-20261103'
OUT=S/'expansion/plans'/f'{NAME}-source-20261103'
SCENES=[('Prepare a dedicated import layer',
  [1, 2],
  ['Layer Name', 'Order', 'Type', 'Data Layer', 'Add Layer', 'TRAINING ONLY - KML and KMZ import'],
  'Prepare a separate layer for the import exercise. Enter K M L and K M Z import as the Layer Name, set Order to twenty, choose Data '
  'Layer, and select Add Layer. The returned row shows the new layer with no image. This keeps the imported geometry separate from '
  'the existing ground-floor drawing and the earlier Geo J S O N example.'),
 ('Select the map, target layer and KML file',
  [3, 4],
  ['Custom Maps', 'Import', 'Target Layer', 'TRAINING ONLY - KML and KMZ import', 'File'],
  'On Custom Maps, select Import for the Community coordination centre. In Import Geospatial Data, select the dedicated Target Layer. '
  'Choose the fictional assembly-area K M L file, review the target again and select Import. The file contains one named polygon. The '
  'source files for this exercise are retained with the Academy so the example can be reproduced.'),
 ('Review history and repeat with KMZ',
  [5, 6, 7],
  ['Import History', 'import.kml', 'KML', 'Complete', 'Target Layer', 'import.kmz', 'KMZ'],
  'Import History now shows import dot K M L, Type K M L, and Complete. The returned form has reset its target selection, so choose '
  'the dedicated layer again before the next upload. Choose the access-area K M Z archive and import it. History now contains '
  'separate Complete entries for K M L and K M Z. A completed import still needs a visual geometry review.'),
 ('Read an import failure instead of assuming success',
  [8, 9],
  ['Target Layer', 'Import', 'Import History', 'Failed', 'No placemarks with a point, line or polygon were found in the file.'],
  'This additional test selects the same target and uploads a K M L file with no placemarks. Its returned history row says Failed. '
  'The Error column explains that no placemarks with a point, line or polygon were found. Check the specific result and error for the '
  'intended run. Do not treat returning to the form as proof that useful geometry was imported.'),
 ('Inspect the actual retained polygons and their flags',
  [2, 10, 11, 12],
  ['Region Editor',
   'Regions',
   'KML training assembly area',
   'KMZ training access area',
   'Region Properties',
   'Searchable in dispatch',
   'Dispatchable'],
  'Open Region Editor for the dedicated layer. The two successful imports are visible as separate polygons and named entries. Select '
  'each polygon to review Region Properties. Both imported areas are Custom regions; Searchable in dispatch and Dispatchable are '
  'checked in this example. Review those defaults before operational use. The import status describes processing, while the map and '
  'properties show what was actually retained.'),
 ('Verify search availability and apply the pattern',
  [13],
  ['Indoor Location', 'KML training assembly area', 'KMZ training access area'],
  'On New Call, open Indoor Location and search for training. Both imported areas now appear as selectable results. No call is '
  'dispatched in this exercise. This pattern can bring reviewed planning areas into a search-and-rescue, security, wildland, '
  'industrial or community response department, alongside fire and E M S. Verify coordinates, naming and operational permissions '
  'before relying on imported reference data.')]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Keep frozen sources intact.'
 rows=json.loads((RAW/'manifest.json').read_text());num={int(r['id'][:3]):r for r in rows}
 used=sorted({n for _,ns,_,_ in SCENES for n in ns});now=datetime.now(timezone.utc).isoformat();screens=[]
 for n in used:
  r=deepcopy(num[n]);dom=RAW/(r['id']+'.txt');assert sha(S/r['file'])==r['sha256']
  r['app']=r['app'].capitalize()
  r.update(dom_file=dom.relative_to(S).as_posix(),dom_sha256=sha(dom),eligible_for_lesson=True,review_status='actual_source_personally_reviewed',capture_review={'reviewer':'Root','passed':True,'reviewed_at':now,'sha256':r['sha256'],'method':'Root personally viewed all four actual KML/KMZ import source sheets. Complete and expected Failed business results, two retained polygons, imported flags and returned call search options are visible. Expected empty-file diagnostic is part of this lesson, not an application crash. Original pixels unchanged; no final-video approval.'});screens.append(r)
 lesson={'id':NAME,'title':'Import KML and KMZ and verify the resulting regions','app':'Core','summary':'Import two fictional geospatial sources, diagnose an empty-file failure, and verify retained geometry, region flags and call search results.','audience':['Department administrators','GIS and mapping coordinators','Operations supervisors'],'prerequisites':['A separate fictional practice map and access to Custom Maps, layer creation and imports.','The retained fictional KML/KMZ fixtures under demo/assets; review any operational source before importing.'],'scenes':[{'id':f'{i:02}','title':t,'route':'/User/CustomMaps','capture_refs':[num[n]['id'] for n in ns],'required_labels':labels,'narration':speech,'practice':t,'capture_intent':'Show the actual target/file control, import history result, retained geometry or returned search option being discussed.'} for i,(t,ns,labels,speech) in enumerate(SCENES,1)],'candidate_only':True,'export_ready':False,'publication_approved':False,'source_files':[],'sector_examples':[{'sector':v,'scenario':'Import reviewed reference geometry into a separate layer, inspect the saved regions and verify their intended search and dispatch policy.'} for v in ['Community paramedicine and mental health response','Search and rescue','Security','Wildland','Industrial emergency response','Fire/EMS']],'scope_limits':['Source proposal only; complete speech/caption correspondence, genuine listening, actual encoded-frame and playback reviews remain required.','Actual Core UI created data layer5fca08cc-2c98-453a-be58-cbd24ddc8666 with order20/no image. Imported one fictional polygon from academy-geospatial-assembly.kml and another from academy-geospatial-access.kmz; both returned Complete and distinct regions. Empty KML returned Failed/no placemarks without adding a third region. Both successful imports defaulted searchable/dispatchable true and appeared in New Call search. No physical occupancy, operational boundary validation, automatic tracking or call dispatch is claimed. Names and geometry are synthetic software fixtures.']}
 OUT.mkdir();(OUT/'raw-manifest.snapshot.json').write_bytes((RAW/'manifest.json').read_bytes())
 manifest={'schema_version':1,'id':NAME,'screenshots':screens,'raw_manifest':{'file':(OUT/'raw-manifest.snapshot.json').relative_to(S).as_posix(),'sha256':sha(RAW/'manifest.json')},'excluded_sources':[{'id':r['id'],'reason':'Redundant or superseded before the actual successful returned guidance.'} for r in rows if int(r['id'][:3]) not in used]}
 for f,v in [('lesson.candidate.json',lesson),('captures.reviewed.json',manifest),('source-review.json',{'reviewer':'Root','reviewed_at':now,'actual_images_reviewed':[r['id'] for r in screens],'source_pixels_unchanged':True,'final_video_approval_inferred':False})]:(OUT/f).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
 (OUT/'narration.txt').write_text('\n\n'.join(x['narration'] for x in lesson['scenes'])+'\n')
 print(json.dumps({'lesson':NAME,'scenes':len(SCENES),'sources':len(screens),'words':len((OUT/'narration.txt').read_text().split()),'video_complete':False}))
if __name__=='__main__':main()
