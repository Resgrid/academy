#!/usr/bin/env python3
"""Add an independent fictional signup practice day; never reset UI actions.

Only resgrid_academy / Firehouse 51 Training is supported. This inserts a new
signup shift, one group and a two-person Chief requirement plus a future day.
It creates no enrollment and touches no existing staffing, trade, approval,
user, unit, credential, provider, queue, notification or global setting.
Run with --date YYYY-MM-DD to repeat a particular future training scenario.
"""

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

DEMO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO))
from manage import sql

NAME = "TRAINING — Academy signup practice"


def query_for(day):
    # day is parsed as a date before interpolation; no free-form SQL input.
    day = date.fromisoformat(day.isoformat())
    return f"""
BEGIN;
SELECT pg_advisory_xact_lock(81510053);
DO $$
DECLARE
 sid integer; gid integer; rid integer; sgid integer; sday integer;
 before_staffing text; after_staffing text;
BEGIN
 IF current_database() <> 'resgrid_academy'
    OR NOT EXISTS (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only the isolated fictional Academy database and department are supported'; END IF;
 IF DATE '{day.isoformat()}' <= (now() AT TIME ZONE 'America/Los_Angeles')::date
 THEN RAISE EXCEPTION 'Choose a future department-local training day'; END IF;
 IF (SELECT count(*) FROM departmentmembers m JOIN aspnetusers u ON u.id=m.userid
     WHERE m.departmentid=51 AND NOT m.isdeleted AND u.normalizedusername='BODEN') <> 1
 THEN RAISE EXCEPTION 'The fictional Boden member is required'; END IF;
 SELECT departmentgroupid INTO STRICT gid FROM departmentgroups WHERE departmentid=51 AND name='Firehouse 51';
 SELECT personnelroleid INTO STRICT rid FROM personnelroles WHERE departmentid=51 AND name='Chief';
 SELECT md5(concat(
   (SELECT coalesce(json_agg(t ORDER BY shiftstaffingid)::text,'[]') FROM shiftstaffings t),
   (SELECT coalesce(json_agg(t ORDER BY shiftstaffingpersonid)::text,'[]') FROM shiftstaffingpersons t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignupid)::text,'[]') FROM shiftsignups t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeid)::text,'[]') FROM shiftsignuptrades t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeuserid)::text,'[]') FROM shiftsignuptradeusers t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeusershiftid)::text,'[]') FROM shiftsignuptradeusershifts t)
 )) INTO before_staffing;
 SELECT shiftid INTO sid FROM shifts WHERE departmentid=51 AND name='{NAME}';
 IF sid IS NULL THEN
   INSERT INTO shifts(name,code,scheduletype,assignmenttype,color,startday,starttime,endtime,hours,departmentid,allowpartials,requireapproval)
   VALUES('{NAME}','ACAD-SIGNUP',1,1,'#16a34a',DATE '{day.isoformat()}','13:00','15:00',2,51,false,false)
   RETURNING shiftid INTO sid;
 ELSE
   IF NOT EXISTS (SELECT 1 FROM shifts WHERE shiftid=sid AND departmentid=51
       AND code='ACAD-SIGNUP' AND scheduletype=1 AND assignmenttype=1
       AND starttime='13:00' AND endtime='15:00' AND hours=2
       AND allowpartials=false AND requireapproval=false)
   THEN RAISE EXCEPTION 'Existing scenario differs; preserve it for human review'; END IF;
 END IF;
 IF EXISTS(SELECT 1 FROM shiftpersons WHERE shiftid=sid)
 THEN RAISE EXCEPTION 'Scenario has standing assignments; preserve and review rather than resetting them'; END IF;
 SELECT shiftgroupid INTO sgid FROM shiftgroups WHERE shiftid=sid AND departmentgroupid=gid;
 IF sgid IS NULL THEN
   INSERT INTO shiftgroups(shiftid,departmentgroupid) VALUES(sid,gid) RETURNING shiftgroupid INTO sgid;
 END IF;
 IF NOT EXISTS(SELECT 1 FROM shiftgrouproles WHERE shiftgroupid=sgid AND personnelroleid=rid) THEN
   INSERT INTO shiftgrouproles(shiftgroupid,personnelroleid,required,optional) VALUES(sgid,rid,2,0);
 ELSIF NOT EXISTS(SELECT 1 FROM shiftgrouproles WHERE shiftgroupid=sgid AND personnelroleid=rid AND required=2 AND optional=0) THEN
   RAISE EXCEPTION 'Existing scenario capacity differs; no overwrite allowed';
 END IF;
 SELECT shiftdayid INTO sday FROM shiftdays WHERE shiftid=sid AND day=DATE '{day.isoformat()}';
 IF sday IS NULL THEN
   INSERT INTO shiftdays(shiftid,day,processed) VALUES(sid,DATE '{day.isoformat()}',false) RETURNING shiftdayid INTO sday;
 END IF;
 SELECT md5(concat(
   (SELECT coalesce(json_agg(t ORDER BY shiftstaffingid)::text,'[]') FROM shiftstaffings t),
   (SELECT coalesce(json_agg(t ORDER BY shiftstaffingpersonid)::text,'[]') FROM shiftstaffingpersons t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignupid)::text,'[]') FROM shiftsignups t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeid)::text,'[]') FROM shiftsignuptrades t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeuserid)::text,'[]') FROM shiftsignuptradeusers t),
   (SELECT coalesce(json_agg(t ORDER BY shiftsignuptradeusershiftid)::text,'[]') FROM shiftsignuptradeusershifts t)
 )) INTO after_staffing;
 IF before_staffing <> after_staffing THEN
   RAISE EXCEPTION 'Existing staffing, signup, trade or approval data changed; rolling back';
 END IF;
 RAISE NOTICE 'Independent Academy readiness fixture prepared without enrollment or provider operations';
END $$;
SELECT json_build_object(
 'database',current_database(),'department_id',51,'name',s.name,'shift_id',s.shiftid,
 'shift_day_id',d.shiftdayid,'day',d.day::date,'start_time',s.starttime,'end_time',s.endtime,
 'shift_group_id',g.shiftgroupid,'department_group_id',g.departmentgroupid,
 'required_role','Chief','capacity_requirement',r.required,'requires_approval',s.requireapproval,
 'standing_assignment_count',(SELECT count(*) FROM shiftpersons p WHERE p.shiftid=s.shiftid),
 'current_enrollment_count',(SELECT count(*) FROM shiftsignups p WHERE p.shiftid=s.shiftid AND p.shiftday=d.day),
 'seed_added_enrollments',0,'existing_staffing_preserved',true,
 'delivery','Fixture rows only; no provider, queue, email, SMS or push operation')
FROM shifts s JOIN shiftdays d ON d.shiftid=s.shiftid
JOIN shiftgroups g ON g.shiftid=s.shiftid
JOIN shiftgrouproles r ON r.shiftgroupid=g.shiftgroupid
WHERE s.departmentid=51 AND s.name='{NAME}' AND d.day=DATE '{day.isoformat()}';
COMMIT;
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=date.fromisoformat, default=None)
    args = parser.parse_args(argv)
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    day = args.date or today + timedelta(days=1)
    if day <= today:
        parser.error("--date must be a future America/Los_Angeles day")
    query = query_for(day)
    output = sql(query)
    result = next(json.loads(line) for line in output.splitlines() if line.startswith("{"))
    report = {**result, "prepared_at": datetime.now(timezone.utc).isoformat(),
              "seed_script": str(Path(__file__).relative_to(DEMO)),
              "seed_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "sql_sha256": hashlib.sha256(query.encode()).hexdigest(),
              "source_contract": ["Core/Resgrid.Model/Shift.cs", "Core/Resgrid.Model/ShiftGroupRole.cs",
                                  "Core/Resgrid.Services/ShiftsService.Scheduling.cs",
                                  "Web/Resgrid.Web.Services/Controllers/V4/ShiftsController.cs"],
              "ui_actions": []}
    folder = DEMO / "scenario-reports"; folder.mkdir(exist_ok=True)
    path = folder / "responder-readiness.json"
    if path.exists():
        previous = json.loads(path.read_text())
        if previous.get("shift_day_id") == report["shift_day_id"]:
            report["ui_actions"] = previous.get("ui_actions", [])
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
