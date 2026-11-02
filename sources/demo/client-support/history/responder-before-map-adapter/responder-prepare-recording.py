#!/usr/bin/env python3
"""Prepare an isolated Responder web-capture checkout without editing the source."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

SUPPORT = Path(__file__).resolve().parent
BASELINE = SUPPORT / 'responder-source-baseline.json'
PATCH = SUPPORT / 'responder-web-compat.patch'
EXCLUDES = [
    '.git', '.env*', 'node_modules', '.expo', 'dist', 'build', 'logs', '*.log',
    'private', '.private', '.aws', '.ssh', '.codex', '.claude', '.npmrc',
    'coverage', 'Pods', 'DerivedData', '.gradle', '.cxx', '.DS_Store',
    '*.p12', '*.p8', '*.pem', '*.key', '*.keystore', '*.mobileprovision',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def verify_files(root, files):
    for relative, expected in files.items():
        if sha(root / relative) != expected:
            raise SystemExit('Source/patch baseline changed: ' + str(root / relative))


def provenance(source, destination, baseline):
    support_files = [BASELINE, PATCH, Path(__file__), SUPPORT / 'responder-launch-recording.sh', SUPPORT / 'responder-verify-web.cjs']
    report = {
        'app': 'Responder', 'prepared_at': datetime.now(timezone.utc).isoformat(),
        'original_checkout': str(source), 'isolated_checkout': str(destination),
        'source_git_revision': baseline['source_git_revision'],
        'dependencies_symlink': str(source / 'node_modules'),
        'source_files': baseline['source_files'], 'patched_files': baseline['patched_files'],
        'support_files': {p.name: sha(p) for p in support_files},
        'excluded_patterns': EXCLUDES,
        'runtime': {'api_origin': 'http://127.0.0.1:18967', 'api_path': '/api/v4', 'web_port': 19102,
                    'analytics': 'disabled by launcher', 'mapbox_key': 'inherited unchanged; never persisted in support files',
                    'expo_mode': 'normal development with --clear; no --no-dev or --minify'},
        'changes': ['Metro can see read-only dependencies through its symlink.',
                    'WebView HTML uses a sandboxed browser iframe with original source.html and matching color-scheme metadata; no invented content, scripts, or native bridge.',
                    'Call menu opens on web press release; native onPressIn behavior is unchanged.',
                    'Calendar detail GET uses query id, matching Core V4 CalendarController.GetCalendarItem(int id); original calendarItemId query failed after attendance signup.',
                    'Web logout uses the existing app AlertDialog components with the original translated title/message/button labels and existing logout callbacks because React Native Alert.alert has no web implementation; native confirmation is unchanged.'],
        'css_diagnosis': 'Expo 57 normal-development CSS modules inject the utility stylesheet. --no-dev --minify on the Metro development server omitted that stylesheet in actual captures. Normal development with fresh Metro cache restores the source-defined styling. No fabricated CSS was injected.',
        'limitations': ['Native camera, background GPS, Bluetooth/PTT hardware, push delivery and external providers remain unverified.',
                        'Local SignalR negotiation returned HTTP 401 in initial authenticated session; do not claim realtime success.',
                        'Scripted WebView/native bridge behavior is not simulated by the browser iframe.'],
        'scope': 'Capture compatibility only; original app files verified unchanged; no credentials or environment files copied.'
    }
    (SUPPORT / 'responder-recording-provenance.json').write_text(json.dumps(report, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('/Users/shawn/Documents/dev/Responder'))
    parser.add_argument('--destination', type=Path, default=SUPPORT.parents[3] / 'capture-apps' / 'Responder')
    parser.add_argument('--verify-existing', action='store_true', help='Verify the prepared checkout and refresh provenance without copying.')
    args = parser.parse_args()
    source, destination = args.source.resolve(), args.destination.resolve()
    if destination == source or source in destination.parents:
        raise SystemExit('Destination must be outside the original checkout.')
    baseline = json.loads(BASELINE.read_text())
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != baseline['source_git_revision']:
        raise SystemExit('Original Git revision changed; inspect the recording patch before preparing.')
    verify_files(source, baseline['source_files'])
    dependencies = source / 'node_modules'
    if not dependencies.is_dir():
        raise SystemExit('The source dependency installation is missing; this script does not install packages.')
    if not args.verify_existing:
        if destination.exists() and any(destination.iterdir()):
            raise SystemExit('Destination is nonempty; choose a fresh destination or --verify-existing.')
        destination.mkdir(parents=True, exist_ok=True)
        command = ['rsync', '-a', '--safe-links']
        command += [part for excluded in EXCLUDES for part in ['--exclude', excluded]]
        subprocess.run(command + [str(source) + '/', str(destination) + '/'], check=True, stdout=subprocess.DEVNULL)
        (destination / 'node_modules').symlink_to(dependencies, target_is_directory=True)
        subprocess.run(['patch', '--batch', '--forward', '-p1', '--input', str(PATCH)], cwd=destination, check=True, stdout=subprocess.DEVNULL)
    if not (destination / 'node_modules').is_symlink() or (destination / 'node_modules').resolve() != dependencies.resolve():
        raise SystemExit('Prepared checkout must reuse the expected read-only dependency installation.')
    verify_files(destination, baseline['patched_files'])
    verify_files(source, baseline['source_files'])
    provenance(source, destination, baseline)
    print('Verified isolated Responder capture checkout:', destination)


if __name__ == '__main__':
    main()
