#!/usr/bin/env python3
"""Create or resume a local recording stack without deleting Docker resources."""
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'sources/demo'
sys.path.insert(0, str(DEMO))
from settings import DEFAULT_NAME, load, profile

INFRA = ['postgres', 'redis', 'rabbit', 'mail']
DATABASES = ['resgrid_academy_docs', 'resgrid_academy_oidc', 'resgrid_academy_workers']


def plan(args):
    saved = DEMO / 'private/stack.json'
    selected = load() if saved.exists() else profile(args.name or DEFAULT_NAME, args.web_port or 18867)
    if args.name and selected['name'] != args.name or args.web_port and selected['ports']['web'] != args.web_port:
        raise ValueError('This checkout already has a recording profile. Use it, or use another Academy checkout for another profile.')
    manifest = json.loads((ROOT / 'sources/evidence/source-manifest.json').read_text())
    pointer = DEMO / 'private/core-path.json'
    default_core = Path(json.loads(pointer.read_text())['path']) if pointer.exists() else DEMO / 'checkout'
    core = (args.core or default_core).expanduser().resolve()
    return {'stack': selected, 'core_checkout': str(core), 'acquire_upstream': args.core is None and not (core / 'Resgrid.sln').is_file(),
            'upstream': manifest['upstream'], 'recorded_revision': manifest['recorded_source_head'],
            'steps': ['Check Docker Compose, .NET SDK, Git and OpenSSL', 'Acquire recorded Resgrid revision if no checkout was supplied',
                      'Generate local credentials and TLS/OIDC certificates', 'Restore and publish five Resgrid applications',
                      'Create this profile’s volumes and infrastructure', 'Create auxiliary databases and apply Resgrid migrations',
                      'Seed Firehouse 51 once; preserve an existing department', 'Start applications and check health'],
            'web_url': 'http://127.0.0.1:' + str(selected['ports']['web']),
            'credentials_file': 'sources/demo/private/credentials.json',
            'notice': 'This plan does not start containers or write credentials. Application source comes from Resgrid/Core; evidence snapshots may include later working-tree changes.'}


def require_fresh_credentials_for_existing_storage(docker, selected):
    if (DEMO / 'private/credentials.json').exists():
        return
    for volume in ('postgres-data', 'config', 'web-publish'):
        result = subprocess.run([docker, 'volume', 'inspect', selected['name'] + '_' + volume], capture_output=True)
        if result.returncode == 0:
            raise ValueError('This Docker profile already has storage but its credentials are missing. Restore its private/ files or use another profile; no data was changed.')


def wait_for_infrastructure(manager):
    for _ in range(90):
        states = []
        for service in INFRA[:3]:
            result = manager.docker('inspect', manager.STACK + '-' + service + '-1', '--format', '{{.State.Health.Status}}', capture_output=True)
            states.append(result.stdout.strip())
        if states == ['healthy'] * 3:
            return
        if 'unhealthy' in states:
            raise ValueError('Infrastructure is unhealthy. Inspect this profile’s container logs before retrying.')
        time.sleep(2)
    raise ValueError('Infrastructure did not become healthy within three minutes; rerun to resume.')


def department_seed_needed(manager):
    name = manager.sql('SELECT name FROM departments WHERE departmentid=51;')
    if name and not name.startswith('Firehouse 51'):
        raise ValueError('Department 51 is not the training fixture. Existing data was preserved.')
    return not bool(name)


def execute(args, instructions):
    for executable in ('docker', 'dotnet', 'git', 'openssl'):
        if not shutil.which(executable):
            raise ValueError(executable + ' must be installed and available on PATH. See sources/demo/README.md.')
    docker = shutil.which('docker')
    subprocess.run([docker, 'info'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([docker, 'compose', 'version'], check=True, stdout=subprocess.DEVNULL)
    require_fresh_credentials_for_existing_storage(docker, instructions['stack'])
    core = Path(instructions['core_checkout'])
    logs = DEMO / 'logs'
    logs.mkdir(exist_ok=True)
    if instructions['acquire_upstream']:
        if core.exists() and any(core.iterdir()):
            raise ValueError('The automatic checkout folder is not empty. Supply --core with a valid Resgrid checkout.')
        with (logs / 'checkout.log').open('w') as log:
            subprocess.run(['git', 'clone', instructions['upstream'], str(core)], check=True, stdout=log, stderr=subprocess.STDOUT)
            subprocess.run(['git', '-C', str(core), 'checkout', '--detach', instructions['recorded_revision']], check=True, stdout=log, stderr=subprocess.STDOUT)
    if not (core / 'Resgrid.sln').is_file():
        raise ValueError('No Resgrid.sln in --core. Supply a complete Resgrid/Core checkout.')
    private = DEMO / 'private'
    private.mkdir(exist_ok=True, mode=0o700)
    (private / 'stack.json').write_text(json.dumps(instructions['stack'], indent=2) + '\n')
    (private / 'core-path.json').write_text(json.dumps({'path': str(core)}, indent=2) + '\n')
    for name in ('stack.json', 'core-path.json'):
        (private / name).chmod(0o600)
    os.environ['RESGRID_CORE_PATH'] = str(core)
    for script in ('prepare.py', 'prepare_tls.py', 'prepare.py'):
        subprocess.run([sys.executable, str(DEMO / script)], check=True)
    spec = importlib.util.spec_from_file_location('academy_demo_manager', DEMO / 'manage.py')
    manager = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(manager)
    print('Restoring Resgrid dependencies; progress is in sources/demo/logs/restore.log.', flush=True)
    with (logs / 'restore.log').open('w') as log:
        subprocess.run(['dotnet', 'restore', str(core / 'Resgrid.sln'), '-p:SKIP_LIBMAN_RESTORE=1'], check=True, stdout=log, stderr=subprocess.STDOUT)
    manager.build()
    for volume in ('web-publish', 'console-publish', 'config', 'gateway-config'):
        manager.docker('volume', 'create', manager.STACK + '_' + volume, capture_output=True)
    manager.compose('create', *INFRA)
    manager.start([manager.STACK + '-' + service + '-1' for service in INFRA])
    wait_for_infrastructure(manager)
    manager.stage()
    for database in DATABASES:
        exists = manager.sql("SELECT 1 FROM pg_database WHERE datname='" + database + "';", db='postgres')
        if not exists:
            manager.sql('CREATE DATABASE ' + database + ' OWNER academy;', db='postgres')
    with (logs / 'migrations.log').open('w') as log:
        manager.compose('run', '--rm', 'migrate', stdout=log, stderr=subprocess.STDOUT)
    if department_seed_needed(manager):
        subprocess.run([sys.executable, str(DEMO / 'seed.py')], check=True)
        manager.sql((private / 'seed.sql').read_text())
        print('Seeded Firehouse 51 with fictional training data.', flush=True)
    else:
        print('Firehouse 51 already exists; preserving its data and workflow history.', flush=True)
    subprocess.run([sys.executable, str(DEMO / 'reserve_status_ids.py')], check=True)
    manager.compose('create', *manager.SERVICES)
    manager.start([manager.STACK + '-' + service + '-1' for service in manager.SERVICES])
    for attempt in range(12):
        try:
            manager.health()
            break
        except SystemExit:
            if attempt == 11:
                raise
            time.sleep(5)
    report = {'stack': instructions['stack'], 'web_url': instructions['web_url'], 'core_revision': subprocess.run(['git', '-C', str(core), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip(),
              'seed_applied_only_if_absent': True, 'credentials_file': instructions['credentials_file']}
    (DEMO / 'setup-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Recording stack ready: ' + instructions['web_url'])
    print('Sign in as boden using demo_password from sources/demo/private/credentials.json.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', type=Path, help='Use a complete existing Resgrid/Core checkout; otherwise acquire the recorded revision locally.')
    parser.add_argument('--name', help='New recording profile name, starting resgrid-academy-.')
    parser.add_argument('--web-port', type=int, help='New profile web port; the other ports move by the same offset.')
    parser.add_argument('--plan', action='store_true', help='Display the steps without generating credentials or using Docker.')
    args = parser.parse_args()
    try:
        instructions = plan(args)
        if args.plan:
            print(json.dumps(instructions, indent=2))
        else:
            execute(args, instructions)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error) + '\nSetup stopped. Generated state stays local; inspect sources/demo/logs and rerun to resume.') from error


if __name__ == '__main__':
    main()
