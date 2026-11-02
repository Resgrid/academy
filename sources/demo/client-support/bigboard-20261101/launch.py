"""Launch only an isolated BigBoard copy against the fictional local Academy API."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

SUPPORT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recording-directory', type=Path, required=True)
    parser.add_argument('--api-origin', default='http://127.0.0.1:18967')
    parser.add_argument('--port', type=int, default=19105)
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    root = args.recording_directory.resolve()
    proof = json.loads((root / 'academy-recording-provenance.json').read_text())
    assert proof['prepared'] and proof['app'] == 'BigBoard' and Path(proof['destination']) == root
    origin = urlsplit(args.api_origin)
    assert origin.scheme == 'http' and origin.hostname and not origin.username and not origin.password
    assert origin.hostname == 'localhost' or ipaddress.ip_address(origin.hostname).is_loopback
    assert origin.path in ('', '/') and not origin.query and not origin.fragment
    assert 1024 <= args.port <= 65535 and (root / 'node_modules/expo/bin/cli').is_file()
    baseline = json.loads((SUPPORT / 'source-baseline.json').read_text())
    for relative in ('package.json', 'yarn.lock', 'env.js', 'app.config.ts'):
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == baseline['source_files'][relative]
    result = dict(app='BigBoard', recording_directory=str(root), api_origin=args.api_origin,
                  browser_origin='http://localhost:' + str(args.port), environment_file_loading=False,
                  analytics=False, map_key='inherited BIGBOARD_MAPBOX_PUBKEY; never printed or written',
                  prerequisite='The isolated API CORS allowlist must include this browser origin.', launch=not args.plan)
    print(json.dumps(result, indent=2), flush=True)
    if args.plan:
        return
    assert os.environ.get('BIGBOARD_MAPBOX_PUBKEY', '').startswith('pk.'), 'Provide the public map key in the local environment.'
    env = dict(os.environ)
    env.update(APP_ENV='development', EXPO_NO_DOTENV='1', EXPO_NO_TELEMETRY='1', EXPO_OFFLINE='1',
               DO_NOT_TRACK='1', CI='1', BROWSER='none')
    env.update(BIGBOARD_BASE_API_URL=args.api_origin.rstrip('/'), BIGBOARD_API_VERSION='v4',
               BIGBOARD_RESGRID_API_URL='/api/v4', BIGBOARD_MAINTENANCE_MODE='false')
    for key in ('LOGGING_KEY', 'APP_KEY', 'SENTRY_DSN', 'COUNTLY_APP_KEY', 'COUNTLY_SERVER_URL'):
        env['BIGBOARD_' + key] = ''
    node = shutil.which('node')
    assert node, 'Node.js is required.'
    raise SystemExit(subprocess.call([node, str(root / 'node_modules/expo/bin/cli'), 'start', '--web',
                                     '--localhost', '--port', str(args.port), '--clear'], cwd=root, env=env))


if __name__ == '__main__':
    main()
