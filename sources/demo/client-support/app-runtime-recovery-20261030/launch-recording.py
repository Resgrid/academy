#!/usr/bin/env python3
"""Check/launch an exact isolated local recording source; never operate app data.

Default is source-only/read-only. --launch starts an owned detached supervisor
and Metro on the fixed localhost port. Runtime observations and sanitized logs
stay in ignored _reports. Existing source profiles and original apps stay intact.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
REPORTS = ROOT / '_reports/recording-runtime-recovery-20261030'
CONFIG = {
    'dispatch': {'app': 'Dispatch', 'prefix': 'DISPATCH', 'port': 19101,
                 'profiles': {'dispatch-source-profile-v1.json': 'fa769eb7cbbeb443aaaae7d8d98c5d88d6d533278126508bd1523d457e0511a2'}},
    'ic': {'app': 'IC', 'prefix': 'IC', 'port': 19104,
           'profiles': {'ic-source-profile-v1.json': '499e95dae76a5d87376de17ebe15f7624f3fb0fc8abb6c8474657924210bb2f3'}},
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def relative_file(root, name):
    require(isinstance(name, str) and name and not name.startswith('/') and '\\' not in name
            and all(p not in ('', '.', '..', 'private', '.git', 'node_modules') and not p.startswith('.env')
                    for p in name.split('/')), 'Unsafe bound source file.')
    path = root / name
    require(path.resolve().is_relative_to(root.resolve()) and path.is_file() and not path.is_symlink(),
            'Missing, escaped or symlinked bound source file: ' + name)
    return path


def source_check(alias, profile_name):
    cfg = CONFIG[alias]
    require(profile_name in cfg['profiles'], 'Choose an explicitly retained source profile.')
    profile_path = relative_file(PACKAGE, profile_name)
    require(sha(profile_path) == cfg['profiles'][profile_name], 'Source profile changed.')
    profile = json.loads(profile_path.read_text())
    target = ROOT.parent / 'capture-apps' / cfg['app']
    original = ROOT.parents[3] / cfg['app']
    core = ROOT.parents[2]
    require(target.is_dir() and not target.is_symlink() and not (target / '.git').exists(), 'Use the existing isolated recording copy.')
    require(target.resolve() != original.resolve() and not target.resolve().is_relative_to(original.resolve()), 'Original checkout is never a runtime target.')
    require((target / 'node_modules').is_symlink() and (target / 'node_modules').resolve() == (original / 'node_modules').resolve(),
            'Original dependency symlink differs.')
    require(not any(target.glob('.env*')), 'Isolated recording root must not contain dotenv files.')
    revision = subprocess.check_output(['git', '-C', str(original), 'rev-parse', 'HEAD'], text=True).strip()
    require(revision == profile['original_revision'], 'Original source revision changed; retain this profile and review a new one.')
    for name, digest in profile['original_source_hashes'].items():
        require(sha(relative_file(original, name)) == digest, 'Original source changed: ' + name)
    for name, digest in profile['core_contract_hashes'].items():
        require(sha(relative_file(core, name)) == digest, 'Core contract changed: ' + name)
    for name, digest in profile['files'].items():
        require(sha(relative_file(target, name)) == digest, 'Bound isolated source changed: ' + name)
    require(profile['app'] == cfg['app'] and profile['records_readonly_observation']['passed'] is True,
            'Wrong or unverified source profile.')
    return cfg, profile, target, profile_path


def runtime_environment(cfg):
    # Only booleans about required inherited public credentials are reportable.
    prefix = cfg['prefix']
    require(bool(os.environ.get(prefix + '_MAPBOX_PUBKEY')), 'Corresponding inherited public Mapbox variable is missing.')
    env = os.environ.copy()
    env.update(APP_ENV='development', EXPO_NO_DOTENV='1', EXPO_NO_TELEMETRY='1', DO_NOT_TRACK='1',
               EXPO_OFFLINE='1', CI='1', BROWSER='none')
    env[prefix + '_BASE_API_URL'] = 'http://127.0.0.1:18967'
    env[prefix + '_API_VERSION'] = 'v4'
    env[prefix + '_RESGRID_API_URL'] = '/api/v4'
    for suffix in ('COUNTLY_APP_KEY', 'COUNTLY_SERVER_URL', 'SENTRY_DSN', 'LOGGING_KEY', 'APP_KEY'):
        env[prefix + '_' + suffix] = ''
    return env


def write_new(path, value):
    require(path.resolve().is_relative_to(REPORTS.resolve()) and not path.is_symlink(), 'Runtime observation must stay in ignored report folder.')
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def worker(alias, profile_name, run_name):
    cfg, profile, target, profile_path = source_check(alias, profile_name)
    env = runtime_environment(cfg)
    with socket.socket() as listener:
        require(listener.connect_ex(('127.0.0.1', cfg['port'])) != 0, 'Fixed app port is already owned; never replace another process.')
    command = ['node', 'node_modules/expo/bin/cli', 'start', '--web', '--localhost', '--clear', '--port', str(cfg['port'])]
    child = subprocess.Popen(command, cwd=target, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    sensitive = [v for k, v in os.environ.items() if v and len(v) >= 8 and
                 any(tag in k.upper() for tag in ('MAPBOX', 'TOKEN', 'PASSWORD', 'SECRET', 'APP_KEY', 'SENTRY', 'LOGGING_KEY', 'COUNTLY'))]
    def stop(signum, _frame):
        if child.poll() is None:
            child.send_signal(signum)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    write_new(REPORTS / (run_name + '.process.json'), {
        'created_at': stamp(), 'app': cfg['app'], 'supervisor_pid': os.getpid(), 'metro_pid': child.pid,
        'source_profile_file': profile_name, 'source_profile_sha256': sha(profile_path),
        'original_revision': profile['original_revision'], 'local_port': cfg['port'],
        'fixed_training_api': 'http://127.0.0.1:18967', 'command': command,
        'mapbox_inherited_present': True, 'inherited_values_recorded': False,
        'analytics_disabled': True, 'dotenv_disabled_and_absent': True,
        'browser_auth_api_data_or_DB_actions': False,
    })
    with (REPORTS / (run_name + '.sanitized.log')).open('x') as stream:
        for line in child.stdout:
            for value in sensitive:
                line = line.replace(value, '[redacted inherited environment value]')
            stream.write(line)
            stream.flush()
    code = child.wait()
    write_new(REPORTS / (run_name + '.exit.json'), {'observed_at': stamp(), 'exit_code': code,
                                                  'app': cfg['app'], 'metro_pid': child.pid})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', choices=CONFIG, required=True)
    parser.add_argument('--profile')
    parser.add_argument('--launch', action='store_true')
    parser.add_argument('--foreground', action='store_true', help='Keep the owned supervisor in a persistent exec session.')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--run-name', help=argparse.SUPPRESS)
    args = parser.parse_args()
    profile_name = args.profile or args.app + '-source-profile-v1.json'
    cfg, profile, target, profile_path = source_check(args.app, profile_name)
    if args.worker:
        require(args.run_name and args.run_name.replace('-', '').isalnum(), 'Invalid local run identity.')
        worker(args.app, profile_name, args.run_name)
        return
    result = {'passed': True, 'mode': 'source_check', 'app': cfg['app'], 'profile': profile_name,
              'profile_sha256': sha(profile_path), 'source_files_bound': len(profile['files']),
              'original_revision': profile['original_revision'], 'files_written': 0, 'browser_or_data_actions': False}
    if args.launch:
        runtime_environment(cfg)
        REPORTS.mkdir(parents=True, exist_ok=True)
        run_name = args.app + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        if args.foreground:
            print(json.dumps({'app': cfg['app'], 'run_name': run_name, 'source_profile_sha256': sha(profile_path),
                              'fixed_port': cfg['port'], 'mode': 'persistent_owned_supervisor'}), flush=True)
            worker(args.app, profile_name, run_name)
            return
        proc = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--app', args.app,
                                 '--profile', profile_name, '--worker', '--run-name', run_name],
                                cwd=ROOT, env=os.environ.copy(), start_new_session=True,
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result.update(mode='launch_requested', supervisor_pid=proc.pid, run_name=run_name,
                      fixed_local_url='http://localhost:' + str(cfg['port']),
                      observation_folder=str(REPORTS), http_bundle_ready=False)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
