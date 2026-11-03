"""Check or apply retained source only to an explicitly isolated Unit recording copy."""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser(description=__doc__);a.add_argument('--recording-copy',type=Path,required=True);a.add_argument('--apply',action='store_true');args=a.parse_args();root=args.recording_copy.expanduser().resolve()
if root.name!='Unit-records' or root.parent.name!='capture-apps' or not (root/'package.json').is_file():raise SystemExit('Choose the isolated capture-apps/Unit-records copy.')
changes=[]
for row in json.loads((P/'source-identities.json').read_text())['files']:
 rel=Path(row['file']);target=root/rel
 if rel.is_absolute() or '..' in rel.parts or target.is_symlink() or any(p.is_symlink() for p in target.parents):raise SystemExit('Unsafe retained path.')
 for state in ['before','after']:
  if sha(P/state/rel)!=row[state+'_sha256']:raise SystemExit('Changed retained source bytes.')
 actual=sha(target)
 if actual not in [row['before_sha256'],row['after_sha256']]:raise SystemExit('Unrecognized target bytes: '+str(rel))
 changes.append((row,target,actual==row['before_sha256']))
if args.apply:
 for row,target,change in changes:
  if change:target.write_bytes((P/'after'/row['file']).read_bytes())
print(json.dumps({'passed':True,'applied':args.apply,'files':len(changes),'files_needing_change':sum(x[2] for x in changes),'git_or_build_or_runtime_actions':False}))
