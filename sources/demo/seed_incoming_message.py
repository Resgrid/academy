#!/usr/bin/env python3
"""Add one fictional incoming acknowledgement message without sending notifications.

This optional recording scenario preserves an existing response on repeated runs.
It never modifies an existing member, credential, message or department setting.
"""
import argparse
import json
from pathlib import Path
from manage import sql

QUERY = """
BEGIN;
SELECT pg_advisory_xact_lock(81510052);
DO $$ BEGIN
 IF current_database() <> 'resgrid_academy' OR NOT EXISTS
    (SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE 'Firehouse 51%Training%')
 THEN RAISE EXCEPTION 'Only the isolated fictional Academy department is supported'; END IF;
 IF (SELECT count(*) FROM aspnetusers u JOIN departmentmembers m ON m.userid=u.id
     WHERE m.departmentid=51 AND NOT m.isdeleted AND u.normalizedusername IN ('BODEN','CASEY')) <> 2
 THEN RAISE EXCEPTION 'The two fictional training members are required'; END IF;
END $$;
INSERT INTO messages(subject,isbroadcast,sendinguserid,receivinguserid,body,senton,
                     isdeleted,systemgenerated,type,departmentid)
SELECT 'TRAINING ONLY — Acknowledge briefing',false,
       (SELECT id FROM aspnetusers WHERE normalizedusername='CASEY'),
       (SELECT id FROM aspnetusers WHERE normalizedusername='BODEN'),
       'Fictional Academy exercise: please acknowledge the training briefing. No emergency or real deployment.',
       timezone('UTC',now()),false,false,1,51
WHERE NOT EXISTS (SELECT 1 FROM messages WHERE departmentid=51 AND subject='TRAINING ONLY — Acknowledge briefing');
INSERT INTO messagerecipients(userid,isdeleted,messageid,message_messageid,departmentid)
SELECT m.receivinguserid,false,m.messageid,m.messageid,51 FROM messages m
WHERE m.departmentid=51 AND m.subject='TRAINING ONLY — Acknowledge briefing'
AND NOT EXISTS (SELECT 1 FROM messagerecipients r WHERE r.messageid=m.messageid AND r.userid=m.receivinguserid);
SELECT json_build_object('message_id',m.messageid,'type',m.type,'recipient_row_id',r.messagerecipientid,
 'response_already_present',r.response IS NOT NULL AND r.response <> '',
 'delivery','Fixture rows only; no provider, queue, email, SMS or push operation')
FROM messages m JOIN messagerecipients r ON r.messageid=m.messageid AND r.userid=m.receivinguserid
WHERE m.departmentid=51 AND m.subject='TRAINING ONLY — Acknowledge briefing';
COMMIT;
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=('briefing', 'readiness'), default='briefing')
    args = parser.parse_args()
    query = QUERY
    if args.scenario == 'readiness':
        query = query.replace('TRAINING ONLY — Acknowledge briefing', 'TRAINING ONLY — Confirm equipment readiness')
        query = query.replace('please acknowledge the training briefing', 'please confirm the fictional equipment-readiness briefing')
    output = sql(query)
    result = next(json.loads(line) for line in output.splitlines() if line.startswith('{'))
    directory = Path(__file__).resolve().parent / 'scenario-reports'
    directory.mkdir(exist_ok=True)
    (directory / ('incoming-message-' + args.scenario + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
