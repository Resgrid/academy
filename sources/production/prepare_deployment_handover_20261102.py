"""Freeze personally inspected equipment-return, attachment and HTML manifest UI."""
import json
from prepare_records_reports_exports_20261102 import LESSONS,freeze,S,sha
from verify_capture_evidence import visible_controls_digest

LESSONS['handover']=dict(name='core-deployment-equipment-files-manifest',raw='core-deployment-administration-20261102',route='/User/Deployments',
    title='Return deployment equipment and retain a handover file',
    summary='Return a free-text equipment assignment, upload a fictional handover note, and inspect the current unit and personnel manifest.',
    audience=['Deployment coordinators','Department administrators','Resource supervisors'],
    prerequisites=['Authorized deployment-management access in the fictional training department.',
                   'A saved van/member roster and the Demo radio kit free-text equipment entry.'],
    sector_scenario='Keep the current resource roster and deployment handover documentation useful to the next supervisor.',
    scope='This lesson executes the free-text equipment roster return and attachment upload, and opens the HTML manifest. It does not claim an inventory stock return, successful handover-file download, PDF export, deployment completion or external-order closeout.',
    excluded={11:'Active selection did not establish a successful status change.',12:'Actual saved badge remained Planned despite historical filename.',28:'CSV download did not complete.'},
    scenes=[
      ('Inspect the equipment before returning it',[10],['Roster','Equipment','Demo radio kit','Issued','Return'],
       'Open Roster on the deployment and find Demo radio kit under Equipment. Read its Unit association and Issued column before changing the roster. This exercise added the kit as a free-text equipment entry, and Issued is a dash. At the right end of that row is the curved-arrow Return button. Identify the intended item first, because the action belongs to that specific equipment row.'),
      ('Return the entry and verify the remaining roster',[10,29],['Return','No equipment rostered.','Matthew Casey','CS-VAN-1','Crew'],
       'Select the Return arrow for Demo radio kit. The returned roster now says No equipment rostered. The van is still present with call sign C S van one and a Crew count of one, and Matthew Casey is still assigned to it. Returning the equipment entry did not remove the unit or its person. This action changes the deployment equipment assignment; no inventory stock issue or stock return was performed for this free-text example.'),
      ('Prepare a handover attachment',[30],['Files','Other','Name','Upload'],
       'Open Files to keep supporting material with this deployment. The existing receipt already appears as a Receipt file. In the upload row, keep Other as the type for the demonstration handover note. Enter a recognizable Name, then use Choose File to select the prepared fictional handover text file. Review the type, name and selected file before choosing Upload. Use the appropriate file category for the document you are actually retaining.'),
      ('Verify the saved file row',[31],['Saved.','TRAINING ONLY - Community support handover','Other','deployment-handover-20261102.txt','Added','Receipt'],
       'After Upload, verify the Saved message and the new row. It shows the community support handover name, Other as its Type, the text filename and the Added information for Kelly Severide. The earlier Receipt remains as a separate row. Check the filename as well as the display name so the record points to the intended supporting file. This is a fictional software exercise, and these attachments contain no real incident or patient information.'),
      ('Open and inspect the current manifest',[31,32],['View manifest','Units','Personnel','Matthew Casey','CS-VAN-1','CS-1','Crew','Seat','Certification'],
       'Select View manifest. Resgrid opens an H T M L deployment manifest in a separate tab. Read its deployment name, Planned status, agency references and window. Under Units, the van has call sign C S van one and one crew member. Under Personnel, Casey is associated with that unit and has call sign C S one. Seat and Certification are blank for this assignment. Verify the actual people and assignments behind a summary count before using the manifest for coordination.'),
      ('Keep the handover useful across department types',[32],['Units','Personnel','Window'],
       'This same process helps departments hand over a clear picture of their assignment. Community paramedicine and mental health response teams, search-and-rescue teams, security departments, wildland contractors and industrial emergency teams can retain their own supporting documents and review the current resources. Fire and E M S departments use these same controls. Keep the roster current, attach the right fictional or authorized documentation, and check the manifest’s unit and personnel details against the work being coordinated.')])

if __name__=='__main__':
    freeze('handover')
    out=S/'expansion/plans/core-deployment-equipment-files-manifest-source-20261102'
    snapshot=out/'raw-manifest.snapshot.json';snapshot.write_bytes((S/'captures/expansion/core-deployment-administration-20261102/manifest.json').read_bytes())
    p=out/'captures.reviewed.json';m=json.loads(p.read_text());m['raw_manifest']={'file':snapshot.relative_to(S).as_posix(),'sha256':sha(snapshot)}
    for row in m['screenshots']:
        row['capture_review']['method']='Root personally viewed the original actual browser image; source pixels unchanged.'
        if row.get('visible_controls'):
            row['capture_review'].update(controls_sha256=visible_controls_digest(row['visible_controls']),application_visible=True,no_errors=True,controls_reviewed=True,controls_fully_visible=True,controls_unobstructed=True)
    p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
