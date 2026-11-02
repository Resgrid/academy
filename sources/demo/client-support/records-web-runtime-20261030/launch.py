"""Source-bound recovery for the separate Responder and Unit Records web servers.

Default is read-only. --launch verifies the exact retained contract and original
source first, then serves only the fixed loopback recording port. It never reads
credential/env files, prints env values, installs dependencies or operates apps.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SUPPORT = HERE.parent
ROOT = HERE.parents[3]
CORE = ROOT.parents[2]
ARTIFACT = ROOT.parent
REPORTS = ROOT / '_reports/recording-runtime-recovery-20261030'
APPS = {'responder': ('Responder', 'Responder', 'RESPOND', 'RESPOND_MAPBOX_PUBKEY', 19102),
    'unit-records': ('Unit-records', 'Unit', 'UNIT', 'UNIT_MAPBOX_PUBKEY', 19103)}
PATTERN = re.compile(r'(?:\b(?:pk|sk)\.[A-Za-z0-9_.-]{12,}|\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_.-]{10,}|(?<=://)[^/\s:@]+:[^/\s@]+@)')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d): return (json.dumps(d, indent=2) + '\n').encode()
def need(ok, message):
    if not ok: raise ValueError(message)


def inspect(app):
    directory, original_name, prefix, key, port = APPS[app]
    target = ARTIFACT / 'capture-apps' / directory
    original = CORE.parent / original_name
    package = SUPPORT / (('responder' if app == 'responder' else 'unit') + '-records-contract-20261030')
    preparer = package / 'prepare.py'
    spec = importlib.util.spec_from_file_location('records_runtime_' + app.replace('-', '_'), preparer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checked = module.inspect(target, original, CORE)
    need(checked['state'] == 'after', 'The complete retained Records contract patch is required.')
    need(not list(target.glob('.env*')), 'Refuse environment files in isolated recording copy; no values inspected.')
    allowed = {r['file']: r['after_sha256'] for r in checked['metadata']['files']}
    if app == 'responder':
        baseline = json.loads((SUPPORT / 'responder-source-baseline.json').read_text())
        allowed.update(baseline['patched_files'])
        for name, digest in baseline['source_files'].items():
            p = original / name
            need((sha(p) if p.exists() else None) == digest, 'Original Responder compatibility source drift: ' + name)
        for name, digest in baseline.get('dependency_source_files', {}).items():
            need(sha(original / 'node_modules' / name) == digest, 'Linked Responder dependency drift: ' + name)
    def runtime_file(p):
        # Later synthetic tests and generated coverage XML in the original tree
        # are outside the executable recording profile. Retained Records tests
        # are still checked by the exact contract preparer above.
        return p.is_file() and not any(x in {'__tests__', '__snapshots__', 'coverage'} for x in p.parts) and not re.search(r'\.(?:test|spec)\.', p.name) and p.suffix in {'.ts', '.tsx', '.js', '.jsx', '.json', '.css', '.png', '.jpg', '.svg'}
    names = {p.relative_to(target).as_posix() for p in (target / 'src').rglob('*') if runtime_file(p)}
    names |= {p.relative_to(original).as_posix() for p in (original / 'src').rglob('*') if runtime_file(p)}
    for name in ['package.json', 'yarn.lock', 'metro.config.js', 'babel.config.js', 'app.config.ts', 'env.js', 'global.css', 'theme-tokens.css', 'global.web.css', 'tsconfig.json']:
        if (target / name).exists() or (original / name).exists(): names.add(name)
    identity = []
    for name in sorted(names):
        path = Path(name)
        need(not any(x in {'private', '.git', 'node_modules'} or x.startswith('.env') for x in path.parts), 'Private source path refused.')
        dest, old = target / path, original / path
        need(dest.is_file() and not dest.is_symlink(), 'Missing/symlink isolated source: ' + name)
        actual = sha(dest)
        need(actual == allowed.get(name, sha(old) if old.is_file() else None), 'Unreviewed isolated source difference: ' + name)
        identity.append({'file': name, 'sha256': actual})
    deps = []
    for name in ['expo/package.json', 'expo/bin/cli', 'expo-router/package.json', 'react-native/package.json', 'nativewind/package.json', '@sentry/react-native/package.json']:
        p = target / 'node_modules' / name
        need(p.is_file(), 'Missing installed runtime dependency: ' + name)
        deps.append({'file': name, 'sha256': sha(p)})
    result = {'app': directory, 'target': str(target), 'original': str(original),
        'port': port, 'url': 'http://localhost:' + str(port), 'api_origin': 'http://127.0.0.1:18967',
        'contract_metadata_sha256': module.METADATA_SHA256, 'preparer_sha256': sha(preparer),
        'source_files_checked': len(identity), 'source_identity_sha256': hashlib.sha256(encoded(identity)).hexdigest(),
        'source_files': identity, 'runtime_dependency_identity_sha256': hashlib.sha256(encoded(deps)).hexdigest(),
        'runtime_dependencies': deps, 'metro_config_sha256': sha(target / 'metro.config.js'),
        'native_profiles_or_original_sources_changed': False, 'environment_values_recorded': False}
    return result, target, prefix, key, port


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', choices=APPS, required=True)
    p.add_argument('--launch', action='store_true')
    args = p.parse_args()
    result, target, prefix, key, port = inspect(args.app)
    if not args.launch:
        print(json.dumps({k:v for k,v in result.items() if k not in {'source_files','runtime_dependencies'}}))
        return
    need(bool(os.environ.get(key)), 'Inherited corresponding public Mapbox variable is required; no value displayed.')
    for family, host in [(socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')]:
        with socket.socket(family) as probe:
            probe.settimeout(1)
            code = probe.connect_ex((host, port))
            need(code != 1, 'Sandbox denied local-network access; use the authorized loopback execution path.')
            need(code != 0, 'Recording port already has a listener; no process is stopped by this helper.')
    env = os.environ.copy()
    env.update(APP_ENV='development', EXPO_NO_DOTENV='1', EXPO_NO_TELEMETRY='1', DO_NOT_TRACK='1',
        CI='1', BROWSER='none', EXPO_OFFLINE='1', SENTRY_DISABLE_AUTO_UPLOAD='true')
    env.update({prefix + '_BASE_API_URL': result['api_origin'], prefix + '_API_VERSION': 'v4',
        prefix + '_RESGRID_API_URL': '/api/v4', prefix + '_LOGGING_KEY': '', prefix + '_SENTRY_DSN': '',
        prefix + '_COUNTLY_APP_KEY': '', prefix + '_COUNTLY_URL': '', prefix + '_COUNTLY_SERVER_URL': ''})
    if args.app == 'responder': env[prefix + '_CHANNEL_API_URL'] = result['api_origin'] + '/'
    node = shutil.which('node')
    need(node is not None, 'Existing Node runtime required; this helper never installs packages.')
    command = [node, str(target / 'node_modules/expo/bin/cli'), 'start', '--web', '--localhost', '--port', str(port), '--clear']
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    base = REPORTS / (args.app + '-' + stamp)
    result.update(checked_at=datetime.now(timezone.utc).isoformat(), wrapper_sha256=sha(Path(__file__)),
        command=command, inherited_mapbox_present=True, new_launch=True, no_browser_opened=True,
        EXPO_NO_DOTENV=True, analytics_disabled=True, cache_clear_requested=True)
    with base.with_suffix('.source.json').open('xb') as f: f.write(encoded(result))
    with base.with_suffix('.log').open('x') as log:
        process = subprocess.Popen(command, cwd=target, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', errors='replace', start_new_session=True)
        print(json.dumps({'app': result['app'], 'pid': process.pid, 'url': result['url'],
            'source_identity_sha256': result['source_identity_sha256'], 'source_receipt': str(base.with_suffix('.source.json'))}), flush=True)
        for line in process.stdout:
            clean = PATTERN.sub('[redacted-client-value]', line)
            # The inherited value stays only in the child environment and its
            # expected live public config; no raw body or env dump is recorded.
            log.write(clean); log.flush()
            sys.stdout.write(clean); sys.stdout.flush()
        raise SystemExit(process.wait())


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, KeyError) as e: raise SystemExit('Recording recovery stopped: ' + str(e))
