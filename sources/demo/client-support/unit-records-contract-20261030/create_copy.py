#!/usr/bin/env python3
"""Opt in to a NEW filtered Unit Records source copy; no runtime actions.

Only the pinned public source-file inventory is copied. No environment/private,
Git/native-output files, dependency installs, server/browser/simulator operations
or changes to a historical source profile are made.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('unit_records_source_prepare', PACKAGE / 'prepare.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def create(target, original, core, package=PACKAGE):
    M.require(not target.exists() and not target.is_symlink(), 'Destination already exists; preserve it and use the read-only preparer.')
    target, original, core, package = [path.resolve() for path in [target, original, core, package]]
    M.require(target.parent.name == 'capture-apps' and (target.name == 'Unit-records' or target.name.startswith('Unit-records-')), 'Use a new dedicated capture-apps/Unit-records destination.')
    M.require(not any(part.startswith('native-unit') for part in target.parts), 'Historical native Unit trees are forbidden.')
    M.require(target != original and not target.is_relative_to(original) and not original.is_relative_to(target), 'Original checkout cannot be a destination.')
    body = M.read(package, 'contract-metadata.json')
    M.require(M.digest(body) == M.METADATA_SHA256, 'Pinned contract metadata changed.')
    metadata = json.loads(body)
    baseline = M.read(package, metadata['base_compatibility_metadata']['file'])
    M.require(M.digest(baseline) == metadata['base_compatibility_metadata']['sha256'], 'Pinned copy inventory changed.')
    M.require(M.digest(M.read(package, metadata['patch']['file'])) == metadata['patch']['sha256'], 'Retained patch changed.')
    M.require(M.digest(M.read(package, metadata['contract_excerpts']['file'])) == metadata['contract_excerpts']['sha256'], 'Core excerpt changed.')
    excluded = {'.git', 'node_modules', 'private', '.private', '.aws', '.ssh', '.codex', '.agents', 'coverage', 'dist', 'build', 'web-build', '.expo', '.next', 'ios', 'android', 'artifacts'}
    for row in metadata['original_files']:
        relative = M.relative(row['file'])
        M.require(not any(part in excluded or part.startswith('.env') or 'credential' in part.lower() or 'secret' in part.lower() for part in relative.parts), 'Private/environment/output path rejected.')
        M.require(relative.suffix.lower() not in {'.pem', '.p12', '.pfx', '.key', '.keystore', '.jks'}, 'Key-file path rejected.')
        M.require(M.digest(M.read(original, row['file'])) == row['sha256'], 'Original source changed before copy: ' + row['file'])
    for row in metadata['core_contract_files']:
        M.require(M.digest(M.read(core, row['file'])) == row['sha256'], 'Core contract changed before copy: ' + row['file'])
    M.require((original / 'node_modules').is_dir(), 'Existing original Unit dependencies are required; none are installed here.')
    # Every source/Core/input guard above completes before the first write.
    target.mkdir(parents=True)
    for row in metadata['original_files']:
        data = M.read(original, row['file'])
        M.require(M.digest(data) == row['sha256'], 'Original changed during copying; preserve incomplete copy without launching.')
        path = target / row['file']
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    (target / 'node_modules').symlink_to(original / 'node_modules', target_is_directory=True)
    checked = M.inspect(target, original, core, package)
    M.require(checked['state'] == 'before', 'Fresh source copy is not an unpatched baseline.')
    return {'passed': True, 'files_copied': len(metadata['original_files']), 'production_state': 'before',
        'contract_metadata_sha256': M.METADATA_SHA256, 'environment_private_or_key_values_read': False,
        'original_and_native_sources_changed': False, 'dependencies_installed': False,
        'runtime_app_data_server_browser_simulator_actions': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--core-source', type=Path, required=True)
    parser.add_argument('--create', action='store_true', help='Explicit opt-in; without this flag no copy is made.')
    args = parser.parse_args()
    if not args.create:
        print(json.dumps({'read_only': True, 'copy_performed': False, 'opt_in_required': '--create'}))
    else:
        print(json.dumps(create(args.target, args.original, args.core_source), indent=2))
