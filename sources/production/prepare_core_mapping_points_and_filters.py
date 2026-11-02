"""Freeze narration against reviewed, genuine Core mapping screens.

This source preparation does not generate audio, estimate speech timing, render
video, or qualify the broader unfinished mapping lesson for publication.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'core-mapping-points-and-filters'
RAW = Path('captures/expansion/core-mapping-20261028/manifest.json')
RAW_SHA = '85d6c828e73e5255426c9c0c8e416ee144d900eb0148909e2f406d626eecf936'
OUT = SOURCES / 'expansion/plans/core-mapping-points-and-filters-capture-freeze-20261028-v2'
REVIEWED_AT = '2026-10-28T15:40:28+00:00'
STEPS = [
('001-saved-department-map-center', 'Read the department map center',
 ['Address', 'Default Map Center GPS Coordinates', '41.8721', '-87.6523'],
 "In Department Settings, find Address and Default Map Center GPS Coordinates. Our fictional training department has a complete latitude and longitude pair. The page explains that an explicit center takes precedence over address geocoding. Read the saved values before changing them. A department map center is a viewing reference; it does not establish a unit's current position. This recording reviews the existing center without changing or saving it."),
('003-engine-filter-result', 'Find named resources with the text filter',
 ['Engine', 'Engine 51', 'Reserve Engine 51'],
 "Open Mapping and enter Engine in Filter marker text. Two named engine markers remain. The training fixture includes positions in different states, so this is a filter demonstration rather than a local response recommendation. Filtering changes this map view. It does not rename resources, remove calls, or establish that a displayed unit is ready to respond."),
('004-labels-hidden', 'Reduce label clutter',
 ['Filter marker text', 'Hide labels', 'Show units'],
 "Clear the text filter and check Hide labels. The marker symbols remain while their name labels disappear. This can reduce clutter when several objects overlap. Restore the labels while learning unfamiliar symbols, and use the category controls to decide which kinds of objects you want to inspect."),
('005-units-hidden-calls-remain', 'Separate visibility from missing data',
 ['Show units', 'TRAINING — Warehouse alarm', 'TRAINING — Community medical standby', 'TRAINING — Vehicle rescue exercise'],
 "Uncheck Show units and adjust the zoom to see the three training calls. The unit markers disappear from this view while the calls remain. When a resource seems missing, check the text filter and category visibility before changing its record. Restore Show units afterward. Visibility in a map is separate from an object's saved location and operational status."),
('013-poi-types-empty', 'Open point-of-interest management',
 ['POIs', 'Add POI Type', 'Destination', 'Point Count'],
 "Return to the map controls and open Manage POIs. This department initially has no point types. Add POI Type creates a category for related points. A department might organize staging locations, search assembly points, security rally points, contractor access points, or industrial response destinations. Choose a category name that its users will recognize."),
('014-poi-type-prepared', 'Configure the point category',
 ['Name', 'Academy Staging', 'Is Destination', 'Color', 'Marker', 'Icon'],
 "Name the type Academy Staging. Check Is Destination to identify this category as potential destinations for a person or unit. Review Color, Marker and Icon. We retain the blue default color and standard pin, with no symbol selected under Icon. A destination category describes a point's intended use; it does not verify that a location is accessible or suitable for a real deployment."),
('015-poi-type-preview-save', 'Review the preview and save the category',
 ['Academy Staging', 'Preview', 'No custom icon. The default marker is used.', 'Add POI Type'],
 "Scroll to the preview and save control. This example has no custom image, and the form says the default marker is used. The preview helps review appearance, but it is still a form. Choose Add POI Type to save the category, then read the result in the list."),
('016-poi-type-saved', 'Verify the saved category',
 ['Academy Staging', '#0080ff', 'Yes', 'View', 'Add', 'Import'],
 "The list now contains Academy Staging, the saved blue color, Destination Yes, and a point count of zero. View opens the category's information and map. Add creates an individual point in it. Choose Add for this example. The separate Import control is visible, but this walkthrough creates the point manually."),
('017-staging-poi-prepared', 'Enter a point with paired coordinates',
 ['Add POI', 'Latitude', '41.8721', 'Longitude', '-87.6523', 'Academy Staging Point', 'Note'],
 "Enter the latitude and longitude in their separate fields, using decimal notation. Name this record Academy Staging Point, enter a clearly fictional address, and add a note identifying it as an exercise location. Review the coordinate signs and the point's purpose, then choose Add POI. For community paramedicine and mental health teams, use permitted operational destinations and keep sensitive visit details out of general map notes."),
('019-poi-saved-list', 'Read back the saved point',
 ['Academy Staging Point', '41.8721', '-87.6523', 'Edit', 'Showing 1 to 1 of 1 entries'],
 "In the category's List tab, check the saved name, address, note, latitude and longitude. The list now contains one entry. Compare the coordinate pair with what you entered. A successful navigation alone is not enough; this stored row gives you the actual values to verify. Select Edit to reopen the record."),
('020-poi-reopened-values', 'Reopen and verify the stored values',
 ['Edit POI', 'Latitude', '41.8721', 'Longitude', '-87.6523', 'Academy Staging Point', 'Save POI'],
 "The Edit POI form reopens with the saved values. Check the record identity and both coordinates before making any future change. This recording only reads them back. Save POI is available for a deliberate edit, but we return to Mapping without changing the point."),
('021-operating-map-staging-point', 'Locate the point on the operating map',
 ['Mapping', 'Academy Staging Point', 'Show POIs'],
 "On the operating map, filter for Academy Staging Point and keep Show POIs checked. The actual saved marker and its name are now visible on the map. Compare its position with recognizable surroundings. A saved coordinate can be plotted accurately and still describe the wrong intended location, so review the placement before operational use."),
('022-operating-map-staging-popup', 'Inspect the point popup',
 ['Academy Staging Point', 'Academy Staging'],
 "Open the marker to inspect its popup. Check the point name and its Academy Staging category. Use the saved List or Edit view when you need to review the complete note or exact coordinates. This connection between a named record and its actual map position is useful for search teams, security departments, wildland contractors and industrial teams as well as fire and EMS."),
('023-poi-category-hidden', 'Recognize a hidden point',
 ['Academy Staging Point', 'Show POIs', 'Show units'],
 "Uncheck Show POIs while retaining the point's name in the text filter. The marker disappears. This does not delete the saved point. If a dispatcher cannot find a known location, this is one concrete visibility setting to check before creating a duplicate record."),
('024-poi-category-restored', 'Restore the point in the same view',
 ['Academy Staging Point', 'Show POIs'],
 "Check Show POIs again. The same saved marker returns without recreating or editing it. Clear the text filter when you want the broader operating picture. Keep a responsible owner for reviewing destination names, notes and coordinates as department operations change."),
('026-legend-staging-type', 'Distinguish POI symbols from response status',
 ['Stations, hydrants and points of interest', 'These icons do not change with status.', 'Academy Staging'],
 "Open Map Icon Legend and find Stations, hydrants and points of interest. Academy Staging now appears in that group. The legend explicitly states that these icons do not change with status. Keep this distinction clear: a staging point is a place, while a responding unit or member has a separate operational status. A location marker alone does not tell you who is available to use it.")]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze():
    assert not OUT.exists(), 'Preserve existing freezes; use a new version path.'
    assert sha(SOURCES / RAW) == RAW_SHA
    raw = json.loads((SOURCES / RAW).read_text())
    assert len(raw) == 26
    by_id = {row['id']: row for row in raw}
    scenes, selected = [], []
    for number, (ident, title, labels, narration) in enumerate(STEPS, 1):
        row = dict(by_id[ident])
        assert sha(SOURCES / row['file']) == row['sha256']
        assert sha(SOURCES / row['dom_file']) == row['dom_sha256']
        row.update(visible_labels=labels, visible_controls=[], eligible_for_lesson=True)
        row['capture_review'] = {
            'passed': True, 'reviewer': 'Codex exact saved JPEG inspection',
            'reviewed_at': REVIEWED_AT, 'sha256': row['sha256'],
            'application_visible': True, 'labels_legible': True, 'no_errors': True,
            'scope': 'Only the listed readable foreground labels and values. Popup fine text is not used to teach exact notes or coordinates; the list and reopened form show those values.'}
        selected.append(row)
        scenes.append({'id': f'{number:02}', 'title': title,
                       'required_labels': labels, 'narration': narration,
                       'capture_evidence': {'status': 'actual_screenshot_reviewed', 'capture_refs': [ident]}})
    citations = []
    for relative in [
        'Web/Resgrid.Web/Areas/User/Controllers/MappingController.cs',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/AddPOIType.cshtml',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/AddPOI.cshtml',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/POIs.cshtml',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/ViewType.cshtml',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/Index.cshtml',
        'Web/Resgrid.Web/Areas/User/Views/Mapping/Legend.cshtml']:
        file = Path('evidence/expansion/Core') / relative
        assert (SOURCES / file).read_bytes() == (Path('/Users/shawn/Documents/dev/Core') / relative).read_bytes()
        citations.append({'file': str(file), 'sha256': sha(SOURCES / file)})
    lesson = {
        'id': NAME, 'title': 'Use map filters and create useful points of interest',
        'app': 'Core', 'audience': ['Dispatchers', 'Department administrators', 'Mapping coordinators'],
        'summary': 'Inspect map visibility controls, create a destination category and fictional point, and verify its persisted values and operating-map marker.',
        'prerequisites': ['Use the isolated fictional Academy training department and an authorized mapping administrator.',
                          'Use permitted training coordinates and fictional notes; verify real operational destinations through department procedures.'],
        'scenes': scenes, 'source_files': [item['file'] for item in citations],
        'capture_limitations': [
            'The existing department map center is read, not changed or saved.',
            'Training units have mixed-state positions; no current device GPS, availability, routed response or nearest-resource proof is inferred.',
            'New POI type and point are saved through normal UI; Edit is opened for readback only.',
            'No custom-icon upload, POI import or deletion is taught.',
            'The separate layer save failed on PostgreSQL and was restored. No layer success is included in this focused sequence.',
            'Indoor maps, route creation, weather events and external geospatial imports remain outside this focused lesson.',
            'The type-specific map popup displays escaped HTML in this version; that screenshot is excluded. The operating-map popup renders the saved point normally.',
            'This preparation has no generated narration, timed captions or rendered video.'],
        'authoring_status': 'actual_capture_reviewed_narration_frozen',
        'media_status': 'awaiting_natural_narration', 'export_ready': False,
        'narration_word_count': sum(len(scene['narration'].split()) for scene in scenes)}
    OUT.mkdir(parents=True)
    def write(name, value):
        (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    write(NAME + '.narrated-source.json', lesson)
    write('captures.reviewed.json', {'app': 'Core', 'screenshots': selected,
                                   'source_manifest': str(RAW), 'source_manifest_sha256': RAW_SHA,
                                   'reviewed_at': REVIEWED_AT})
    write('source-citations.json', {'sources': citations, 'reviewed_at': REVIEWED_AT})
    (OUT / 'narration.txt').write_text('\n\n'.join(scene['narration'] for scene in scenes) + '\n')
    report = {'passed': True, 'reviewed_at': REVIEWED_AT, 'scenes': len(scenes),
              'screenshots': len(selected), 'raw_capture_count': len(raw),
              'words': lesson['narration_word_count'], 'lesson_sha256': sha(OUT / (NAME + '.narrated-source.json')),
              'raw_captures_modified': False, 'canonical_lesson_changed': False,
              'narration_generated': False, 'rendered': False, 'publication_approved': False}
    write('source-preflight.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    freeze()
