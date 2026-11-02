#!/usr/bin/env python3
"""Append fresh fictional station fixes for repeatable nearest-person captures.

Only the three seeded Academy officers are eligible. This preserves every prior
status, keeps the latest status type, and emits no event or notification. A recent
fix is left untouched. It is simulated training telemetry, never device GPS.
The default and --plan are offline. Writing requires --write-training-fixes.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUERY = """
BEGIN;
SELECT pg_advisory_xact_lock(81510054);
DO $$ BEGIN
 IF current_database() <> 'resgrid_academy' OR NOT EXISTS
 (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only the isolated fictional Academy department is supported'; END IF;
 IF (SELECT count(DISTINCT u.id) FROM aspnetusers u JOIN departmentmembers m ON m.userid=u.id
 WHERE m.departmentid=51 AND NOT m.isdeleted AND u.normalizedusername IN ('CASEY','KIDD','HERRMANN')) <> 3
 THEN RAISE EXCEPTION 'The three seeded fictional officers are required'; END IF;
 IF (SELECT count(*) FROM aspnetusers u JOIN LATERAL
 (SELECT 1 FROM actionlogs a WHERE a.userid=u.id AND a.departmentid=51 ORDER BY timestamp DESC,actionlogid DESC LIMIT 1) a ON true
 WHERE u.normalizedusername IN ('CASEY','KIDD','HERRMANN')) <> 3
 THEN RAISE EXCEPTION 'Each seeded officer must already have a training status'; END IF;
 IF EXISTS (SELECT 1 FROM aspnetusers u JOIN LATERAL
 (SELECT * FROM actionlogs a WHERE a.userid=u.id AND a.departmentid=51 ORDER BY timestamp DESC,actionlogid DESC LIMIT 1) a ON true
 WHERE u.normalizedusername IN ('CASEY','KIDD','HERRMANN') AND
 (a.geolocationdata IS DISTINCT FROM '41.8721,-87.6523' OR a.note IS NULL OR a.note NOT IN
 ('Training status demonstration','SIMULATED Academy station position — no device GPS')))
 THEN RAISE EXCEPTION 'An officer was changed by a walkthrough; preserve that state'; END IF;
END $$;
INSERT INTO actionlogs(userid,departmentid,actiontypeid,timestamp,geolocationdata,note)
SELECT u.id,51,a.actiontypeid,timezone('UTC',now()),'41.8721,-87.6523',
 'SIMULATED Academy station position — no device GPS'
FROM aspnetusers u JOIN LATERAL
 (SELECT * FROM actionlogs a WHERE a.userid=u.id AND a.departmentid=51 ORDER BY timestamp DESC,actionlogid DESC LIMIT 1) a ON true
WHERE u.normalizedusername IN ('CASEY','KIDD','HERRMANN')
AND a.timestamp < timezone('UTC',now()) - interval '2 minutes';
SELECT json_build_object('scenario','fresh fictional officer locations',
 'source','Simulated fixture at the fictional department station; no browser or device GPS',
 'fixes',(SELECT json_agg(json_build_object('member',u.normalizedusername,'action_log_id',a.actionlogid,'status_type_preserved',a.actiontypeid,'timestamp',a.timestamp))
 FROM aspnetusers u JOIN LATERAL
 (SELECT * FROM actionlogs a WHERE a.userid=u.id AND a.departmentid=51 ORDER BY timestamp DESC,actionlogid DESC LIMIT 1) a ON true
 WHERE u.normalizedusername IN ('CASEY','KIDD','HERRMANN')));
COMMIT;
"""


def execute_query(query):
    # Keep help, offline plans and argument errors independent of local settings,
    # private configuration and Docker. Only the explicit write path imports this.
    sys.path.insert(0, str(ROOT))
    from manage import sql
    return sql(query)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--plan', action='store_true', help='Describe the scenario without contacting Docker or the database (default).')
    action.add_argument('--write-training-fixes', action='store_true', help='Append guarded simulated fixes in the configured isolated Academy stack.')
    args = parser.parse_args(argv)
    if not args.write_training_fixes:
        print(json.dumps({
            'state_changes': 'none',
            'database_contacted': False,
            'scenario': 'fresh fictional officer locations',
            'members': ['CASEY', 'KIDD', 'HERRMANN'],
            'position': '41.8721,-87.6523',
            'source': 'Simulated fixture at the fictional department station; no browser or device GPS',
            'write_option': '--write-training-fixes',
            'guards': ['resgrid_academy database', 'Firehouse 51 training department', 'three existing seeded officers with unchanged training positions and notes', 'preserve status types and prior history', 'leave fixes newer than two minutes untouched'],
        }, indent=2))
        return 0
    result = next(json.loads(line) for line in execute_query(QUERY).splitlines() if line.startswith('{'))
    output = ROOT / 'scenario-reports' / 'fresh-training-positions.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
