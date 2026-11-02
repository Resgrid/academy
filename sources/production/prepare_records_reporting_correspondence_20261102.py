"""Prepare exact real-screen/caption proposals for the two Records reporting lessons."""
from pathlib import Path
import hashlib
import json
import sys

S=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def build():
    cfg={}
    definitions={
        'reports':('core-records-saved-reports','core-records-saved-reports-source-20261102-v2',72,
            [('01',1,1,1),('01',2,7,2),('02',8,8,4),('02',9,9,3),('02',10,16,4),('03',17,22,4),('04',23,32,5),
             ('05',33,33,5),('05',34,37,6),('05',38,38,5),('05',39,41,9),('06',42,42,9),('06',43,49,10),
             ('07',50,50,10),('07',51,51,11),('07',52,56,12),('08',57,57,13),('08',58,58,16),('08',59,60,14),('08',61,63,15),('09',64,72,15)],
            {1:{'Records':'Records','Reports':'Reports','Saved reports':'Saved reports'},7:{'New report':'New report'},
             8:{'Report name':'name','Description':'description'},9:{'Definition':'definition'},11:{'Columns':'Columns'},13:{'record.number':'record dot number','record.state':'record dot state','Summary':'Summary'},15:{'Notes':'Notes'},
             17:{'Sort by':'Sort by','record.number':'record dot number','Descending':'Descending'},18:{'Group by':'Group by','Aggregates (JSON)':'Aggregates'},
             23:{'Filters (JSON)':'Filters'},28:{'Max rows':'Max rows'},29:{'Include drafts':'Include drafts','Include restricted fields':'Include restricted fields'},30:{'Version mappings (JSON)':'Version mappings'},
             33:{'Validate':'Validate'},34:{'The report is valid.':'The report is valid'},38:{'Save':'Save'},39:{'Saved reports':'Saved reports','Report saved.':'Report saved','Definition':'definition'},40:{'Columns':'columns','Run':'Run'},42:{'Run':'Run'},
             43:{'Rows (2 / 2)':'two of two rows','Record number':'Record number','State':'State'},44:{'Summary':'Summary'},45:{'Finalized':'Finalized'},47:{'CSV':'C S V'},50:{'Edit':'Edit'},
             51:{'Descending':'descending'},52:{'Group by':'Group by','record.state':'record dot state'},53:{'Aggregates (JSON)':'Aggregates','Count':'Count'},54:{'Count':'Count'},57:{'The report is valid.':'The report is valid'},58:{'Save':'Save'},
             59:{'· Group by record.state':'Group by record dot state'},60:{'Last run':'Last run'},61:{'Groups':'Groups','Finalized':'Finalized','Count':'count'},62:{'Rows (2 / 2)':'two rows'},72:{'Groups':'grouped total'}},
            {'012-group-by-state-count-prepared':['Count']},
            ['Screen 004 shows initial selection, not the validation banner; screen 006 is withheld until validation is discussed.',
             'Second Save uses the current grouped-report action bar, screen016. Source005 remains only in initial detail-report preparation.',
             'Actual CSV was downloaded and inspected; no spreadsheet application is represented as Resgrid.']),
        'exports':('core-records-export-templates','core-records-export-templates-source-20261102',82,
            [('01',1,1,1),('01',2,7,2),('02',8,15,21),('03',16,19,21),('03',20,23,20),('04',24,31,5),('05',32,40,6),
             ('06',41,42,7),('06',43,43,20),('06',44,45,9),('06',46,49,10),('07',50,52,11),('07',53,57,12),
             ('08',58,61,14),('08',62,65,15),('09',66,66,16),('09',67,68,17),('09',69,70,18),('09',71,73,19),('10',74,80,19),('10',81,82,12)],
            {1:{'Records':'Records','Manage':'Manage','Report exports':'Report exports'},7:{'New export':'New export'},8:{'Export name':'Export name','Key':'Key'},13:{'Description':'description'},
             16:{'Format':'Format','CSV':'C S V','Scope':'scope'},17:{'Training':'Training','Record definitions':'Record definitions'},20:{'File name':'File name'},21:{'Delimiter':'Delimiter','Include a header row':'header row','Enabled':'Enabled'},
             24:{'Columns':'Columns'},25:{'Record number':'Record number','Record type':'Record type','State':'State','Duration (minutes)':'Duration in minutes','Finalized (UTC)':'Finalized'},26:{'Course (records)':'Course from records'},
             34:{'Include narrative and personal detail (Tier 2)':'Include narrative and personal detail'},35:{'Include restricted sections (Tier 1)':'restricted sections'},
             41:{'Schedule':'schedule','Window (days)':'Window'},43:{'Save':'Save'},44:{'Format':'format','Training':'Training'},45:{'Window (days)':'window'},46:{'Report exports':'Report exports','The export was saved.':'The export was saved'},47:{'Scope':'scope','No schedule (Workflow only)':'No schedule'},
             50:{'Run now':'Run now'},53:{'Manual':'Manual','Records':'records'},54:{'Bytes':'bytes','Checksum':'checksum','Download':'Download'},55:{'Download':'Download'},
             58:{'Schedule':'Schedule','Daily':'Daily'},59:{'Hour (department local time)':'Hour','Window (days)':'window'},60:{'Weekday (0 = Sunday)':'weekday','Day of month (1-28)':'day-of-month'},62:{'Save':'Save'},
             66:{'Next run':'Next run'},67:{'Daily':'Daily'},70:{'No schedule (Workflow only)':'No schedule','Save':'Save'},71:{'Next run':'Next run','No schedule (Workflow only)':'No schedule'},
             80:{'Schedule':'schedule'},81:{}},
            {'016-daily-saved-next-run':['11/03/2026 06:00:00']},
            ['Creation-form screens020/021 are an explicitly retained later normal-UI unsaved replay of the original settings, cancelled without creating a duplicate.',
             'Initial Save uses the unobscured replay control; original saved readback and successful two-record/316-byte CSV run remain original execution evidence.',
             'Daily setting and next-run readback are demonstrated, followed by saved No schedule cleanup. No automatic execution or external delivery is claimed.'])
    }
    for key,(name,folder,count,spans,refs,labels,notes) in definitions.items():
        base=S/'expansion/plans'/folder;audio=S/'expansion/audio';cfg[key]=dict(name=name,source_folder=folder,cues=count,
            source_sha256=sha(base/'lesson.candidate.json'),captures_sha256=sha(base/'captures.reviewed.json'),audio_sha256=sha(audio/(name+'.m4a')),
            captions_sha256=sha(audio/(name+'.actual.corrected.srt')),qa_sha256=sha(audio/(name+'.actual.qa.json')),
            spans=spans,refs=refs,additional_labels=labels,supporting_applications=[],scene_apps={},context_notes=notes)
    dest=S/'production/records_reporting_complete_inputs_20261102.json'
    assert not dest.exists(),'Preserve existing correspondence input freeze.'
    dest.write_text(json.dumps(cfg,indent=2,ensure_ascii=False)+'\n')
    original=S/'production/prepare_administration_complete_20261102.py'
    script=original.read_text().replace('administration_complete_inputs_20261102.json',dest.name).replace('fff312194a2e9ee873893ed5ec091a6e39dee48a0e15cbbede122d8ec13acb44',sha(dest))
    output=S/'production/prepare_records_reporting_complete_20261102.py';assert not output.exists();output.write_text(script)
    print('Prepared hash-bound correspondence inputs; no Root, listening, encoded-frame or playback approval inferred.')


if __name__=='__main__': build()
