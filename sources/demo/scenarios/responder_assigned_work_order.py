#!/usr/bin/env python3
"""Prepare an independent fictional assigned order without apparatus effects.

Only the named isolated Academy database/dept51 is supported. The existing
fictional Boden member receives a new software-practice assignment. It uses a
separate TRAINING year2099 number, never changes the live numbering counter,
and never changes a unit, asset, safety hold, provider, approval or global setting.
No acceptance, completion, hours or photographs are fabricated by this fixture.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

DEMO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO))
from manage import sql

ID = 'e6158298-a817-4d92-b075-a7d7ed331b5e'
REQUEST = '5bcd0bea-70d8-4d7e-8b60-b68e359f524b'
NAME = 'TRAINING ONLY — Assigned software practice'
CONTENT = {'Fields': {'Title': NAME, 'Description': 'Fictional Academy software exercise. No real equipment defect, repair, inspection, personnel work or payment is represented.',
                     'Currency': 'USD', 'Steps': [{'Text': 'TRAINING ONLY — Review the fictional software workflow', 'Completed': False}]}}

def main():
    encoded = json.dumps(CONTENT, separators=(',', ':')).replace("'", "''")
    query = f"""
BEGIN;
SELECT pg_advisory_xact_lock(81510056);
DO $$
DECLARE uid text; gid integer;
BEGIN
 IF current_database()<>'resgrid_academy' OR NOT EXISTS
 (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only isolated Academy dept51 is supported'; END IF;
 SELECT u.id INTO STRICT uid FROM aspnetusers u JOIN departmentmembers m ON m.userid=u.id
 WHERE u.normalizedusername='BODEN' AND m.departmentid=51 AND NOT m.isdeleted;
 SELECT departmentgroupid INTO STRICT gid FROM departmentgroups WHERE departmentid=51 AND name='Firehouse 51';
 IF NOT EXISTS(SELECT 1 FROM workorders WHERE id='{ID}') THEN
   IF EXISTS(SELECT 1 FROM workorders WHERE departmentid=51 AND numberyear=2099 AND numbersequence=1)
   THEN RAISE EXCEPTION 'Training number is occupied; no overwrite permitted'; END IF;
   INSERT INTO workorders(id,departmentid,content,revision,createdon,updatedon,createdby,isprotected,
     requestid,numberyear,numbersequence,type,priority,status,sourcetype,targetgroupid,
     assignedtouserid,dueon,setunitoutofservice,restoreunitstateonclose,isdeleted,currencycode)
   VALUES('{ID}',51,'{encoded}',1,now(),now(),uid,false,'{REQUEST}',2099,1,2,1,2,0,gid,
     uid,current_date+interval '1 day',false,false,false,'USD');
 ELSIF NOT EXISTS(SELECT 1 FROM workorders WHERE id='{ID}' AND departmentid=51
   AND requestid='{REQUEST}' AND assignedtouserid=uid AND targetunitid IS NULL
   AND NOT setunitoutofservice AND numberyear=2099 AND numbersequence=1)
 THEN RAISE EXCEPTION 'Existing scenario identity differs; preserve for review'; END IF;
END $$;
SELECT json_build_object('database',current_database(),'department_id',51,'work_order_id',id,
 'title',content::jsonb->'Fields'->>'Title','number_year',numberyear,'number_sequence',numbersequence,
 'current_status',status,'assignment_accepted_on',assignmentacceptedon,
 'unit_targeted',targetunitid IS NOT NULL,'set_unit_out_of_service',setunitoutofservice,
 'delivery','Fixture assignment only; no provider or physical maintenance operation')
FROM workorders WHERE id='{ID}';
COMMIT;
"""
    report = next(json.loads(row) for row in sql(query).splitlines() if row.startswith('{'))
    report.update({'prepared_at': datetime.now(timezone.utc).isoformat(),
                   'seed_script': str(Path(__file__).relative_to(DEMO)),
                   'seed_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'sql_sha256': hashlib.sha256(query.encode()).hexdigest(),
                   'source_contract': ['Core/Resgrid.Model/WorkOrders/WorkOrderModels.cs', 'Core/Resgrid.Services/WorkOrdersService.cs'],
                   'ui_actions': []})
    path = DEMO / 'scenario-reports/responder-assigned-work-order.json'
    if path.exists(): report['ui_actions'] = json.loads(path.read_text()).get('ui_actions', [])
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
