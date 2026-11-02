#!/usr/bin/env python3
"""Prepare an isolated IC web recording checkout; never starts Expo or a browser."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SUPPORT = Path(__file__).resolve().parent
BASELINE = SUPPORT / 'ic-source-baseline.json'
PATCH = SUPPORT / 'ic-web-text.patch'
# Excluded by directory/name anywhere in the tree. Source dependency installation stays read-only.
EXCLUDES = [
    '.git', '.env*', 'node_modules', '.expo', 'dist', 'build', 'logs', '*.log',
    'private', '.private', '.aws', '.ssh', '.codex', '.claude', '.npmrc',
    'coverage', 'Pods', 'DerivedData', '.gradle', '.cxx', '.DS_Store',
    '*.p12', '*.p8', '*.pem', '*.key', '*.keystore', '*.mobileprovision',
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('/Users/shawn/Documents/dev/IC'))
    parser.add_argument('--destination', type=Path, default=SUPPORT.parents[4] / 'capture-apps' / 'IC')
    args = parser.parse_args()
    source = args.source.resolve()
    target = args.destination.resolve()
    if target == source or source in target.parents:
        raise SystemExit('Destination must be outside the original app checkout.')
    baseline = json.loads(BASELINE.read_text())
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != baseline['source_git_revision']:
        raise SystemExit('Source Git revision changed; inspect and regenerate the compatibility patch first.')
    for rel, expected in baseline['source_files'].items():
        path = source / rel
        actual = sha(path) if path.exists() else None
        if actual != expected:
            raise SystemExit('Original source changed for ' + rel + '; inspect before preparing.')
    dependencies = source / 'node_modules'
    if not dependencies.is_dir():
        raise SystemExit('Original dependency installation is missing; this script does not install packages.')
    if target.exists() and any(target.iterdir()):
        raise SystemExit('Destination is nonempty; choose a new isolated destination rather than overwrite it.')
    target.mkdir(parents=True, exist_ok=True)
    command = ['rsync', '-a', '--safe-links']
    command += [item for excluded in EXCLUDES for item in ['--exclude', excluded]]
    command += [str(source) + '/', str(target) + '/']
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
    (target / 'node_modules').symlink_to(dependencies, target_is_directory=True)
    subprocess.run(['patch', '--batch', '--forward', '-p1', '--input', str(PATCH)], cwd=target, check=True, stdout=subprocess.DEVNULL)
    for rel, expected in baseline['patched_files'].items():
        if sha(target / rel) != expected:
            raise SystemExit('Patched file verification failed for ' + rel)
    # Verify the patch never touched original source files.
    for rel, expected in baseline['source_files'].items():
        path = source / rel
        if (sha(path) if path.exists() else None) != expected:
            raise SystemExit('Original source verification failed for ' + rel)
    provenance = {
        'app': 'IC', 'original_checkout': str(source), 'source_git_revision': revision,
        'isolated_checkout': str(target), 'dependencies_symlink': str(dependencies),
        'source_files': baseline['source_files'],
        'patched_files': {rel: sha(target / rel) for rel in baseline['patched_files']},
        'support_files': {p.name: sha(p) for p in [BASELINE, PATCH, Path(__file__), SUPPORT / 'ic-launch-recording.sh', SUPPORT / 'ic-verify-text.cjs', SUPPORT / 'ic-verify-camera.cjs']},
        'excluded_patterns': EXCLUDES,
        'runtime': {'api_origin': 'http://127.0.0.1:18967', 'api_path': '/api/v4', 'web_port': 19104, 'analytics': 'disabled by launcher', 'map_token': 'inherited unchanged; no value persisted in support files'},
        'scope': 'Recording-only Text DOM compatibility, source-declared camera defaults, retained pre-load imperative camera requests, actual center/zoom callbacks and Metro dependency-symlink visibility; original app files unchanged; no UI launched.',
    }
    (SUPPORT / 'ic-recording-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print('Isolated IC checkout prepared:', target)

if __name__ == '__main__':
    main()
