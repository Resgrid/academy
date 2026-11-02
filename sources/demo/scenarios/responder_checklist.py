#!/usr/bin/env python3
"""Add a new fictional checklist exposing supported answer and witness controls.

This writes only a new immutable definition/version in the isolated Academy
database. It does not seed answers, submissions, witness attestations, evidence,
users, units, work orders, device locations, providers or global settings.
Required photo/signature inspection is deliberately disabled; those controls
are viewed without claiming physical evidence or requesting device permissions.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from uuid import UUID, uuid5

DEMO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO))
from manage import sql

NS = UUID('fd7c0fe3-2606-4f42-916b-a5297dc92ab7')
def ident(name):
    return str(uuid5(NS, name))

NAME = 'TRAINING ONLY — Answer types and witness practice'
FORM = {'Name': NAME, 'Instructions': 'Fictional software exercise only. No physical inspection, equipment reading, photographic evidence or signature is represented.',
        'Category': 4, 'TargetType': 2, 'PassThreshold': 100,
        'RequireLocation': False, 'RequiresIndependentWitness': True,
        'Sections': [{'Id': ident('section'), 'Name': 'Software controls', 'Items': []}]}
for kind, label in enumerate(['Applicability practice', 'Yes or no practice', 'Checkbox practice',
                              'Numeric reading practice', 'Quantity practice', 'Free text practice',
                              'Select list practice', 'Date practice', 'Photo evidence controls',
                              'Signature controls']):
    FORM['Sections'][0]['Items'].append({
        'Id': ident('item:' + str(kind)), 'Name': 'TRAINING — ' + label, 'Type': kind,
        'Required': kind == 0, 'Critical': False, 'AllowNotApplicable': kind == 0,
        'RequireNoteOnFail': False, 'Weight': 0 if kind else 1,
        'PassingValue': 'Training option A' if kind == 6 else 'true',
        'Options': ['Training option A', 'Training option B'] if kind == 6 else [],
        'Units': 'fictional units' if kind in (3,4) else None,
        'CreateWorkOrderOnFail': False, 'SetUnitStateOnFail': False, 'HoldAssetOnFail': False})

def main():
    encoded = json.dumps(FORM, separators=(',', ':')).replace("'", "''")
    definition, version = ident('definition'), ident('version')
    query = f"""
BEGIN;
SELECT pg_advisory_xact_lock(81510055);
DO $$
DECLARE uid text;
BEGIN
 IF current_database()<>'resgrid_academy' OR NOT EXISTS
 (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only isolated Academy dept51 is supported'; END IF;
 SELECT u.id INTO STRICT uid FROM aspnetusers u JOIN departmentmembers m ON m.userid=u.id
 WHERE u.normalizedusername='BODEN' AND m.departmentid=51 AND NOT m.isdeleted;
 IF NOT EXISTS(SELECT 1 FROM checklistdefinitions WHERE id='{definition}') THEN
 INSERT INTO checklistdefinitions(id,departmentid,content,revision,createdon,updatedon,createdby,isprotected,currentversionid,publishedversion,retired)
 VALUES('{definition}',51,'{encoded}',1,now(),now(),uid,false,'{version}',1,false);
 ELSIF NOT EXISTS(SELECT 1 FROM checklistdefinitions WHERE id='{definition}' AND departmentid=51 AND content::jsonb='{encoded}'::jsonb AND currentversionid='{version}' AND NOT retired)
 THEN RAISE EXCEPTION 'Existing scenario definition differs; preserve for review'; END IF;
 IF NOT EXISTS(SELECT 1 FROM checklistdefinitionversions WHERE id='{version}') THEN
 INSERT INTO checklistdefinitionversions(id,departmentid,parentid,content,revision,createdon,updatedon,createdby,isprotected,version)
 VALUES('{version}',51,'{definition}','{encoded}',1,now(),now(),uid,false,1);
 ELSIF NOT EXISTS(SELECT 1 FROM checklistdefinitionversions WHERE id='{version}' AND departmentid=51 AND parentid='{definition}' AND content::jsonb='{encoded}'::jsonb)
 THEN RAISE EXCEPTION 'Existing scenario version differs; preserve for review'; END IF;
END $$;
SELECT json_build_object('database',current_database(),'department_id',51,'definition_id','{definition}',
 'version_id','{version}','name','{NAME}','new_answers_seeded',0,'witness_required',true,
 'delivery','Definition/version fixture only; no attestation, provider or physical evidence operation');
COMMIT;
"""
    result = next(json.loads(row) for row in sql(query).splitlines() if row.startswith('{'))
    result.update({'prepared_at': datetime.now(timezone.utc).isoformat(),
                   'seed_script': str(Path(__file__).relative_to(DEMO)),
                   'seed_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'sql_sha256': hashlib.sha256(query.encode()).hexdigest(),
                   'source_contract': ['Core/Resgrid.Model/Checklists/ChecklistContracts.cs',
                                       'Core/Resgrid.Model/Checklists/ChecklistEntities.cs',
                                       'src/components/checklists/checklist-run-sheet.tsx'], 'ui_actions': []})
    path = DEMO / 'scenario-reports/responder-checklist.json'
    if path.exists(): result['ui_actions'] = json.loads(path.read_text()).get('ui_actions', [])
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
