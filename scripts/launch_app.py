#!/usr/bin/env python3
"""Launch a Resgrid client against an isolated Academy stack; --plan is read-only.

The app public Mapbox environment variable is inherited without printing or saving
its value. Native device capabilities are not simulated.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'sources/demo'
sys.path.insert(0, str(DEMO))
from settings import load
from source_profiles import (PROFILE_DEFAULTS, load_source_set, managed_client, managed_source,
                             original_source, select_profile, summary, verify_client, verify_pin)

APPS = {'Dispatch': ('DISPATCH', 19101), 'Responder': ('RESPOND', 19102),
        'Unit': ('UNIT', 19103), 'IC': ('IC', 19104)}


def plan(args):
    name, pinned = select_profile(DEMO, args.source_profile)
    source_set = load_source_set(name, ROOT)
    verify_pin(pinned, source_set)
    prefix, default_port = APPS[args.app]
    paths_file = DEMO / 'private/client-paths.json'
    paths = json.loads(paths_file.read_text()) if paths_file.exists() else {}
    entry = paths.get(args.app, {}) if name == 'expansion' else {}
    if entry and (entry['manifest_sha256'] != source_set['manifest_sha256'] or entry['definition_sha256'] != source_set['definition_sha256']):
        raise ValueError('The prepared client source profile changed; review it and prepare a separate verified copy.')
    if name == 'legacy' and not args.source:
        raise ValueError('Legacy launch requires --source. Use --source-profile expansion for managed verified client checkouts.')
    source = (args.source or Path(entry.get('launch_directory', managed_client(DEMO, args.app, source_set)))).expanduser().resolve()
    original = Path(entry.get('source', managed_source(DEMO, args.app))).resolve()
    if name == 'expansion' and original_source(source, args.app, source_set):
        raise ValueError('Expansion clients must launch from isolated checkouts, preserving original app files.')
    web_port = args.web_port or (load(DEMO)['ports']['web'] if (DEMO / 'private/stack.json').exists() else PROFILE_DEFAULTS[name][1])
    port = args.port or default_port
    if not 1024 <= port <= 65535 or not 1024 <= web_port <= 65535:
        raise ValueError('Use loopback ports between 1024 and 65535.')
    return {'app': args.app, 'source_set': summary(source_set), 'source': str(original),
            'launch_directory': str(source), 'api_origin': 'http://127.0.0.1:' + str(web_port),
            'web_url': 'http://127.0.0.1:' + str(port), 'port': port,
            'required_environment_variable': prefix + '_MAPBOX_PUBKEY',
            'mode': 'Expo normal development; clear Metro cache; environment-file loading and analytics disabled',
            'notice': 'Plan does not read or print map credentials, start Expo or open a browser.'}


def execute(instructions):
    source = Path(instructions['launch_directory'])
    source_set = load_source_set(instructions['source_set']['source_profile'], ROOT)
    if source_set['name'] == 'expansion':
        verify_client(Path(instructions['source']), source, instructions['app'], source_set)
    cli = source / 'node_modules/expo/bin/cli'
    if not cli.is_file():
        raise ValueError('Prepare/install the app dependencies first; see scripts/prepare_apps.py.')
    prefix = APPS[instructions['app']][0]
    key = instructions['required_environment_variable']
    if not os.environ.get(key, '').startswith('pk.'):
        raise ValueError('Set ' + key + ' to the app public Mapbox key in your local environment.')
    origin = instructions['api_origin']
    env = dict(os.environ)
    env.update({'APP_ENV': 'development', 'EXPO_NO_DOTENV': '1', 'EXPO_NO_TELEMETRY': '1',
                'DO_NOT_TRACK': '1', 'CI': '1', 'BROWSER': 'none', 'EXPO_OFFLINE': '1'})
    env.update({prefix + '_BASE_API_URL': origin, prefix + '_API_VERSION': 'v4',
                prefix + '_RESGRID_API_URL': '/api/v4', prefix + '_CHANNEL_API_URL': origin + '/'})
    env.update({prefix + '_' + name: '' for name in
                ('COUNTLY_APP_KEY', 'COUNTLY_URL', 'COUNTLY_SERVER_URL', 'SENTRY_DSN', 'LOGGING_KEY')})
    node = shutil.which('node')
    if not node:
        raise ValueError('Node.js must be available on PATH.')
    print('Launching ' + instructions['app'] + ' against ' + origin + '.', flush=True)
    # The normal Metro development CSS loader is required for these NativeWind apps.
    return subprocess.call([node, str(cli), 'start', '--web', '--localhost',
                            '--port', str(instructions['port']), '--clear'], cwd=source, env=env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', choices=APPS, required=True)
    parser.add_argument('--source-profile', choices=PROFILE_DEFAULTS)
    parser.add_argument('--source', type=Path, help='Legacy app directory, or an already verified expansion launch copy.')
    parser.add_argument('--port', type=int)
    parser.add_argument('--web-port', type=int)
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    try:
        instructions = plan(args)
        if args.plan:
            print(json.dumps(instructions, indent=2))
        else:
            raise SystemExit(execute(instructions))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
