#!/usr/bin/env python3
"""Hash-guarded static-file repair of an isolated Academy recording container."""
import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def run(*args):return subprocess.run(args,check=True,capture_output=True).stdout
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stack-name',required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'resgrid-academy-[a-zA-Z0-9-]+',args.stack_name):
        parser.error('Only a named resgrid-academy-* recording stack is allowed.')
    container=args.stack_name+'-web-1'
    identities=json.loads((ROOT/'source-identities.json').read_text())
    repaired=ROOT/'after'/identities['file']
    assert sha(repaired.read_bytes())==identities['after_sha256']
    runtime=identities['runtime_file']
    with tempfile.TemporaryDirectory(prefix='academy-route-static-') as tmp:
        original=Path(tmp)/'current.js'
        run('docker','cp',container+':'+runtime,str(original))
        current=sha(original.read_bytes())
        result={'container':container,'file':runtime,'observed_sha256':current,'execute':args.execute,'database_changed':False,'application_restarted':False}
        if current==identities['after_sha256']:
            result['status']='already_applied'
        elif current!=identities['before_sha256']:
            raise RuntimeError('Runtime file differs from the reviewed baseline; refusing to overwrite it.')
        elif not args.execute:
            result['status']='ready_for_review'
        else:
            private=ROOT.parents[1]/'private'/'route-static-repair-20261102'
            private.mkdir(parents=True,exist_ok=True)
            backup=private/(args.stack_name+'-routes-new.js')
            if backup.exists():assert sha(backup.read_bytes())==current
            else:backup.write_bytes(original.read_bytes())
            mounts=json.loads(run('docker','inspect',container))[0]['Mounts']
            volume=args.stack_name+'_web-publish'
            assert any(m['Type']=='volume' and m['Name']==volume and m['Destination']=='/app' for m in mounts)
            relative=runtime.removeprefix('/app/')
            # The web application deliberately mounts /app read-only. A networkless
            # helper changes only this reviewed static file in its named publish volume.
            run('docker','run','--rm','--pull','never','--network','none',
                '--mount','type=volume,src='+volume+',dst=/publish',
                '--mount','type=bind,src='+str(repaired)+',dst=/reviewed.js,readonly',
                '--entrypoint','sh','nginx:1.27-alpine','-c',
                'set -eu; actual=$(sha256sum "$1" | cut -d " " -f 1); test "$actual" = "$2"; cp /reviewed.js "$1"',
                'academy-static-repair','/publish/'+relative,identities['before_sha256'])
            run('docker','cp',container+':'+runtime,str(original))
            assert sha(original.read_bytes())==identities['after_sha256']
            result.update(status='applied_and_verified',saved_sha256=identities['after_sha256'])
        print(json.dumps(result,indent=2))
if __name__=='__main__':main()
