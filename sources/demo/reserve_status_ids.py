#!/usr/bin/env python3
"""Reserve the built-in status range in this isolated Academy database only.

Resgrid treats status IDs <=25 as built-in. A fresh database starts its sequences
at 1; advance counters without deleting or rewriting existing training records.
"""
import json
from pathlib import Path
from manage import sql

result = sql('''DO $$ BEGIN
 IF current_database() <> 'resgrid_academy' OR
    NOT EXISTS(SELECT 1 FROM departments WHERE departmentid=51 AND name LIKE '%Training Department%')
 THEN RAISE EXCEPTION 'Only the isolated Academy department is supported'; END IF;
 PERFORM setval('customstates_customstateid_seq',GREATEST(25,(SELECT last_value FROM customstates_customstateid_seq),(SELECT COALESCE(max(customstateid),0) FROM customstates)),true);
 PERFORM setval('customstatedetails_customstatedetailid_seq',GREATEST(25,(SELECT last_value FROM customstatedetails_customstatedetailid_seq),(SELECT COALESCE(max(customstatedetailid),0) FROM customstatedetails)),true);
END $$;
SELECT json_build_object('custom_set_last_id',(SELECT last_value FROM customstates_customstateid_seq),'custom_option_last_id',(SELECT last_value FROM customstatedetails_customstatedetailid_seq),'existing_rows_preserved',true);''')
report={'purpose':'Reserve built-in status IDs <=25 in isolated training fixture','result':json.loads(result.splitlines()[-1])}
Path(__file__).with_name('status-id-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
