"""Read-only verification of retained exact reporting/billing source snapshots."""
import hashlib,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=p.parents[2]
d=json.loads((p/'source-evidence.json').read_text())
for r in d['files']:
 q=s/r['snapshot_file'];assert hashlib.sha256(q.read_bytes()).hexdigest()==r['sha256'],r['file']
for name in ['coverage-matrix.json','source-trace.json','reporting-capture-outline.json','billing-capture-outline.json','scenario.replay.json']:
 json.loads((p/name).read_text())
print(json.dumps({'passed':True,'retained_source_files':len(d['files']),'source_only':True,'files_written':False}))
