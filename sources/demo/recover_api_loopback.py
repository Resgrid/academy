#!/usr/bin/env python3
"""Check/recover only an isolated Academy API proxy after a web restart.

Default is read-only. Docker can retain the proxy in the previous network
namespace even while its container:<web-id> setting still names the same web
container. Compare the actual namespace identities before restarting anything.
No volumes, application containers, credentials or Docker Desktop are changed.
"""
import argparse
import json
import re
import subprocess
import time


def run(args, timeout=12):
    return subprocess.run(['docker', *args], check=True, capture_output=True,
                          text=True, timeout=timeout).stdout.strip()


def inspect(name):
    return json.loads(run(['inspect', name]))[0]


def namespaces(web, proxy):
    return {name: run(['exec', name, 'readlink', '/proc/self/ns/net'])
            for name in (web, proxy)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stack-name', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'resgrid-academy-[A-Za-z0-9_-]+', args.stack_name):
        raise SystemExit('Only explicitly named resgrid-academy stacks are supported.')
    web, proxy = (args.stack_name + suffix for suffix in ('-web-1', '-loopback-1'))
    w, p = inspect(web), inspect(proxy)
    if not w['State']['Running'] or not p['State']['Running']:
        raise SystemExit('Both existing containers must be running; no application start is attempted.')
    if p['HostConfig']['NetworkMode'] != 'container:' + w['Id']:
        raise SystemExit('Proxy names another web container; correct its Compose configuration explicitly.')
    before = namespaces(web, proxy)
    same = before[web] == before[proxy]
    report = {'stack_name': args.stack_name, 'before': before,
              'namespace_matches': same, 'proxy_restarted': False,
              'application_restarted': False, 'volumes_changed': False}
    if not same and args.execute:
        run(['restart', '--time', '5', proxy], timeout=20)
        for _ in range(4):
            after = namespaces(web, proxy)
            if after[web] == after[proxy]:
                break
            time.sleep(1)
        report.update(after=after, namespace_matches=after[web] == after[proxy],
                      proxy_restarted=True)
    print(json.dumps(report, indent=2))
    if args.execute and not report['namespace_matches']:
        raise SystemExit('Proxy namespace is still different; inspect the named stack before retrying.')


if __name__ == '__main__':
    main()
