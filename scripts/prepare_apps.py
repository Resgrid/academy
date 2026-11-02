#!/usr/bin/env python3
"""Prepare pinned isolated client apps; --plan never clones, installs or writes."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'sources/demo'
sys.path.insert(0, str(DEMO))
from source_profiles import (APPS, acquire, load_source_set, managed_client, managed_source,
                             original_source, select_profile, summary, verify_client,
                             verify_cited, verify_pin, verify_repository)


def plan(args):
    name, pinned = select_profile(DEMO, args.source_profile)
    source_set = load_source_set(name, ROOT)
    verify_pin(pinned, source_set)
    if name != 'expansion':
        raise ValueError('Pinned multi-app preparation requires --source-profile expansion. Legacy launch_app.py --source remains available.')
    apps = APPS if args.app == 'all' else (args.app,)
    if len(apps) > 1 and (args.source or args.destination):
        raise ValueError('--source and --destination require a single --app.')
    entries = []
    for app in apps:
        source = (args.source or managed_source(DEMO, app)).expanduser().resolve()
        destination = (args.destination or (managed_client(DEMO, app, source_set) if app in source_set['support'] else source)).expanduser().resolve()
        if app not in source_set['support'] and destination != source:
            raise ValueError(app + ' runs its clean isolated source checkout; no extra capture patch is declared.')
        if original_source(destination, app, source_set):
            raise ValueError('Launch destinations must be isolated from the recorded original ' + app + ' checkout.')
        entries.append({'app': app, 'source': str(source), 'launch_directory': str(destination),
                        'acquire_upstream': args.source is None,
                        'revision': source_set['repositories'][app]['head'],
                        'compatibility': source_set['support'].get(app),
                        'install_dependencies': bool(args.install_deps),
                        'dependency_lock': source_set['dependencies'][app]})
    return {'source_set': summary(source_set), 'apps': entries,
            'notice': 'Read-only plan. Execution never overwrites a nonempty prepared copy, edits original source, starts Expo or opens a browser. Package installation requires --install-deps and a managed checkout.'}


def install_dependencies(source, app, source_set):
    if source != managed_source(DEMO, app) or original_source(source, app, source_set):
        raise ValueError('Dependency installation is restricted to the managed isolated checkout.')
    package_manager = source_set['dependencies'][app]['package_manager']
    corepack, yarn = shutil.which('corepack'), shutil.which('yarn')
    if corepack:
        command = [corepack, 'yarn']
    elif yarn:
        command = [yarn]
    else:
        raise ValueError('Install Corepack or ' + package_manager + ' first; no dependency files were changed.')
    version = subprocess.check_output(command + ['--version'], cwd=source, text=True).strip()
    if version != package_manager.split('@')[-1]:
        raise ValueError(app + ' requires ' + package_manager + '; the selected package manager differs.')
    subprocess.run(command + ['install', '--frozen-lockfile'], cwd=source, check=True)


def execute(instructions):
    source_set = load_source_set('expansion', ROOT)
    private = DEMO / 'private'
    paths_file = private / 'client-paths.json'
    paths = json.loads(paths_file.read_text()) if paths_file.exists() else {}
    for entry in instructions['apps']:
        app, source, destination = entry['app'], Path(entry['source']), Path(entry['launch_directory'])
        if entry['acquire_upstream']:
            acquire(source, app, source_set)
        verify_repository(source, app, source_set)
        verify_cited(source, app, source_set, source_set['dependencies'][app]['files'])
        if entry['install_dependencies']:
            install_dependencies(source, app, source_set)
        if not (source / 'node_modules/expo/bin/cli').is_file():
            raise ValueError(app + ' dependencies are missing. Use --install-deps for its managed checkout, or a verified read-only source with dependencies for a supported capture copy.')
        if entry['compatibility'] and not (destination.exists() and any(destination.iterdir())):
            script = ROOT / entry['compatibility']['prepare']
            subprocess.run([sys.executable, str(script), '--source', str(source), '--destination', str(destination)], check=True)
        verify_client(source, destination, app, source_set)
        paths[app] = {'source': str(source), 'launch_directory': str(destination),
                      'manifest_sha256': source_set['manifest_sha256'],
                      'definition_sha256': source_set['definition_sha256']}
        private.mkdir(parents=True, exist_ok=True, mode=0o700)
        paths_file.write_text(json.dumps(paths, indent=2) + '\n')
        paths_file.chmod(0o600)
        print(app + ' source, support patch and dependency metadata verified; launch directory: ' + str(destination))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-profile', choices=['legacy', 'expansion'])
    parser.add_argument('--app', choices=['all', *APPS], default='all')
    parser.add_argument('--source', type=Path, help='Read-only verified source for a single app; the default acquires its pinned isolated checkout.')
    parser.add_argument('--destination', type=Path, help='Fresh isolated capture copy for Responder or IC.')
    parser.add_argument('--install-deps', action='store_true', help='Allow frozen Yarn installation only in managed isolated clones.')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    try:
        instructions = plan(args)
        if args.plan:
            print(json.dumps(instructions, indent=2))
        else:
            execute(instructions)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error) + '\nClient preparation stopped; existing source and prepared copies were preserved.') from error


if __name__ == '__main__':
    main()
