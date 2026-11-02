#!/usr/bin/env python3
"""Prepare one independent fictional deployment and its existing-member roster.

Only the isolated resgrid_academy / Firehouse 51 Training dataset is supported.
The fixture creates no call, user, unit, rate, financial transaction, provider
request, notification, approval, report or global setting. Existing UI actions
on this deployment are preserved on rerun. Amounts and actual work stay empty.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

DEMO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO))
from manage import sql

DEPLOYMENT = "8fdaedc4-69f8-45aa-95cd-42d73fe24421"
UNIT = "7b8f04a2-32b5-4caa-b4a9-c990647a5e09"
PERSON = "d6c227d2-4bd5-41d9-b340-ce4a9b764580"
NAME = "TRAINING ONLY — Academy field operations"

QUERY = f"""
BEGIN;
SELECT pg_advisory_xact_lock(81510054);
DO $$
DECLARE uid text; engine integer; before_rows text; after_rows text;
BEGIN
 IF current_database() <> 'resgrid_academy'
 OR NOT EXISTS (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only the isolated fictional Academy database and department are supported'; END IF;
 SELECT u.id INTO STRICT uid FROM aspnetusers u JOIN departmentmembers m ON m.userid=u.id
 WHERE u.normalizedusername='BODEN' AND m.departmentid=51 AND NOT m.isdeleted;
 SELECT unitid INTO STRICT engine FROM units WHERE departmentid=51 AND name='Engine 51';
 SELECT md5(concat(
 (SELECT coalesce(json_agg(t ORDER BY deploymentid)::text,'[]') FROM deployments t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymentunitid)::text,'[]') FROM deploymentunits t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymentpersonnelid)::text,'[]') FROM deploymentpersonnel t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymenttimereportid)::text,'[]') FROM deploymenttimereports t),
 (SELECT coalesce(json_agg(t ORDER BY deploymentexpenseid)::text,'[]') FROM deploymentexpenses t)
 )) INTO before_rows;
 IF EXISTS(SELECT 1 FROM deployments WHERE deploymentid='{DEPLOYMENT}') THEN
   IF NOT EXISTS(SELECT 1 FROM deployments WHERE deploymentid='{DEPLOYMENT}' AND departmentid=51 AND name='{NAME}' AND callid IS NULL AND financemode=1)
   THEN RAISE EXCEPTION 'Scenario identity mismatch; preserve for review'; END IF;
 ELSE
   INSERT INTO deployments(deploymentid,departmentid,financemode,name,status,incidentnumber,costcode,
     starton,localtimezoneid,locale,measurementsystem,currency,notes,addedon,addedbyuserid)
   VALUES('{DEPLOYMENT}',51,1,'{NAME}',2,'TRAINING-ACAD-OPS','TRAINING-NO-BILLING',
     current_date,'America/Los_Angeles','en-US','US','USD',
     'Fictional Academy software exercise only. No deployment, physical work, bill, reimbursement, signature or government submission is represented.',now(),uid);
 END IF;
 IF NOT EXISTS(SELECT 1 FROM deploymentunits WHERE deploymentunitid='{UNIT}') THEN
   INSERT INTO deploymentunits(deploymentunitid,deploymentid,departmentid,unitid,callsign,notes,addedon)
   VALUES('{UNIT}','{DEPLOYMENT}',51,engine,'TRAINING Engine 51','Fictional software roster; no actual apparatus deployed.',now());
 ELSIF NOT EXISTS(SELECT 1 FROM deploymentunits WHERE deploymentunitid='{UNIT}' AND deploymentid='{DEPLOYMENT}' AND departmentid=51 AND unitid=engine)
 THEN RAISE EXCEPTION 'Scenario unit identity mismatch'; END IF;
 IF NOT EXISTS(SELECT 1 FROM deploymentpersonnel WHERE deploymentpersonnelid='{PERSON}') THEN
   INSERT INTO deploymentpersonnel(deploymentpersonnelid,deploymentid,departmentid,deploymentunitid,userid,callsign,addedon)
   VALUES('{PERSON}','{DEPLOYMENT}',51,'{UNIT}',uid,'TRAINING Boden',now());
 ELSIF NOT EXISTS(SELECT 1 FROM deploymentpersonnel WHERE deploymentpersonnelid='{PERSON}' AND deploymentid='{DEPLOYMENT}' AND departmentid=51 AND userid=uid AND deploymentunitid='{UNIT}')
 THEN RAISE EXCEPTION 'Scenario member identity mismatch'; END IF;
 SELECT md5(concat(
 (SELECT coalesce(json_agg(t ORDER BY deploymentid)::text,'[]') FROM deployments t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymentunitid)::text,'[]') FROM deploymentunits t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymentpersonnelid)::text,'[]') FROM deploymentpersonnel t WHERE deploymentid<>'{DEPLOYMENT}'),
 (SELECT coalesce(json_agg(t ORDER BY deploymenttimereportid)::text,'[]') FROM deploymenttimereports t),
 (SELECT coalesce(json_agg(t ORDER BY deploymentexpenseid)::text,'[]') FROM deploymentexpenses t)
 )) INTO after_rows;
 IF before_rows<>after_rows THEN RAISE EXCEPTION 'Existing deployment/report/expense rows changed'; END IF;
END $$;
SELECT json_build_object('database',current_database(),'department_id',51,'deployment_id',deploymentid,
 'name',name,'finance_mode',financemode,'status',status,'call_id',callid,
 'unit_roster_id','{UNIT}','personnel_roster_id','{PERSON}',
 'existing_rows_preserved',true,'delivery','Fixture rows only; no provider or financial operation')
FROM deployments WHERE deploymentid='{DEPLOYMENT}';
COMMIT;
"""


def main():
    result = next(json.loads(row) for row in sql(QUERY).splitlines() if row.startswith('{'))
    report = {**result, 'prepared_at': datetime.now(timezone.utc).isoformat(),
              'seed_script': str(Path(__file__).relative_to(DEMO)),
              'seed_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sql_sha256': hashlib.sha256(QUERY.encode()).hexdigest(),
              'source_contract': ['Core/Resgrid.Model/Invoicing/DeploymentModels.cs',
                                  'Web/Resgrid.Web.Services/Controllers/V4/DeploymentsController.cs'],
              'ui_actions': []}
    path = DEMO / 'scenario-reports/responder-operations.json'
    if path.exists():
        report['ui_actions'] = json.loads(path.read_text()).get('ui_actions', [])
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
