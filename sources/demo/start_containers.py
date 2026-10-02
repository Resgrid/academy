#!/usr/bin/env python3
"""Bounded starts of Academy containers; never restarts Docker Desktop."""
import subprocess, sys
names=sys.argv[1:]
if not names or any(not n.startswith('resgrid-academy-') for n in names):
    raise SystemExit('Only explicitly named resgrid-academy containers are supported.')
for name in names:
    for attempt in range(2):
        status=subprocess.run(['docker','inspect',name,'--format','{{.State.Running}}'],capture_output=True,text=True,check=True).stdout.strip()
        if status=='true': break
        try:
            subprocess.run(['docker','start',name],check=True,timeout=12)
        except subprocess.TimeoutExpired:
            print(f'{name}: startup client timed out; retrying only this container.',flush=True)
    result=subprocess.run(['docker','inspect',name,'--format','{{.State.Running}}'],capture_output=True,text=True,check=True).stdout.strip()
    if result!='true': raise SystemExit(f'{name} did not start.')
    print(f'{name}: running',flush=True)
