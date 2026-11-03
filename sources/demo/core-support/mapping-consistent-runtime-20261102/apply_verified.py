#!/usr/bin/env python3
"""Check or apply the retained mapping patch to an explicitly isolated checkout."""
import argparse,hashlib,json
from pathlib import Path

P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--isolated-checkout',type=Path,required=True)
 parser.add_argument('--apply',action='store_true')
 a=parser.parse_args();root=a.isolated_checkout.expanduser().resolve()
 academy=P.parents[3]
 if root in [academy,academy.parent/'Core',academy.parent/'Unit']:
  raise SystemExit('Choose an isolated recording copy; the primary repositories are preserved.')
 if not (root/'Resgrid.sln').is_file():raise SystemExit('A complete isolated Core checkout is required.')
 rows=json.loads((P/'source-identities.json').read_text())['files'];actions=[]
 for r in rows:
  rel=Path(r['file'])
  if rel.is_absolute() or '..' in rel.parts:raise SystemExit('Invalid retained relative path.')
  target=root/rel
  if target.is_symlink() or any(x.is_symlink() for x in target.parents):raise SystemExit('Symlink target refused.')
  for state in ['before','after']:
   if sha(P/state/rel)!=r[state+'_sha256']:raise SystemExit('Retained support hash mismatch.')
  actual=sha(target)
  if actual not in [r['before_sha256'],r['after_sha256']]:raise SystemExit('Unrecognized source content: '+r['file'])
  actions.append((r,target,actual==r['before_sha256']))
 if a.apply:
  for r,target,change in actions:
   if change:target.write_bytes((P/'after'/r['file']).read_bytes())
 print(json.dumps({'passed':True,'applied':a.apply,'files':len(actions),'files_needing_change':sum(x[2] for x in actions),'build_or_runtime_deployment_performed':False,'git_mutations':0}))

if __name__=='__main__':main()
