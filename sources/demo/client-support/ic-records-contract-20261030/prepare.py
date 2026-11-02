#!/usr/bin/env python3
"""Check/apply only the approved isolated IC Records contract patch.

Default is read-only. --apply verifies EVERY original/Core/base-compatibility and
target baseline before the first write. It never copies a source tree, installs,
launches/reloads, touches app data, changes environment, or invokes Git. Existing
historical helpers/profiles remain untouched. New test files may already match
their exact retained bytes after a baseline regression run; unknown edits fail.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

PACKAGE = Path(__file__).resolve().parent
METADATA_SHA256 = 'b1f748010f9e4d2144d85069c887b8b9aee675f3342382d6d3f90bca457dc8c1'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    p = Path(value)
    require(not p.is_absolute() and '..' not in p.parts and p.parts, 'Unsafe relative path.')
    return p


def read(root, name, missing=False):
    path = root / relative(name)
    require(not path.is_symlink(), 'Symlinked file rejected: ' + name)
    require(path.resolve().is_relative_to(root.resolve()), 'Path escapes root: ' + name)
    if missing and not path.exists():
        return None
    require(path.is_file(), 'Required file missing: ' + name)
    return path.read_bytes()


def fingerprint(data):
    return None if data is None else digest(data)


def inspect(target, original, core_source, package=PACKAGE):
    require(not target.is_symlink(), 'Target root may not be a symlink.')
    target, original, core_source, package = [p.resolve() for p in (target, original, core_source, package)]
    require(target != original and not target.is_relative_to(original) and not original.is_relative_to(target), 'Original checkout cannot be an apply target.')
    require(target.is_dir() and not (target / '.git').exists(), 'Target must be an existing isolated copy, not a Git checkout.')
    require((target / 'node_modules').is_symlink() and (target / 'node_modules').resolve() == (original / 'node_modules').resolve(), 'Expected original dependency symlink is missing.')
    body = read(package, 'contract-metadata.json')
    require(digest(body) == METADATA_SHA256, 'Reviewed contract metadata changed.')
    metadata = json.loads(body)
    require(digest(read(package, metadata['patch']['file'])) == metadata['patch']['sha256'], 'Retained patch changed.')
    require(digest(read(package, metadata['contract_excerpts']['file'])) == metadata['contract_excerpts']['sha256'], 'Core contract excerpt changed.')
    base = package / metadata['base_compatibility_metadata']['file']
    require(digest(base.read_bytes()) == metadata['base_compatibility_metadata']['sha256'], 'Historical compatibility baseline changed.')
    for row in metadata['original_files']:
        require(digest(read(original, row['file'])) == row['sha256'], 'Original source changed: ' + row['file'])
    for row in metadata['core_contract_files']:
        require(digest(read(core_source, row['file'])) == row['sha256'], 'Core contract changed: ' + row['file'])
    for row in metadata['base_compatibility_files'] + metadata['unchanged_target_gate_files']:
        require(digest(read(target, row['file'])) == row['sha256'], 'Existing compatibility/gate file changed: ' + row['file'])
    states, plan = [], []
    for row in metadata['files']:
        after = read(package, row['after_snapshot'])
        require(digest(after) == row['after_sha256'], 'After snapshot changed: ' + row['file'])
        current = read(target, row['file'], missing=True)
        current_sha = fingerprint(current)
        if row['before_sha256'] is not None:
            require(digest(read(package, row['before_snapshot'])) == row['before_sha256'], 'Before snapshot changed: ' + row['file'])
            require(current_sha in (row['before_sha256'], row['after_sha256']), 'Unknown target edit: ' + row['file'])
            states.append('before' if current_sha == row['before_sha256'] else 'after')
        else:
            require(row['new_regression_test'] is True and '/__tests__/' in row['file'], 'Only declared new regression files are allowed.')
            require(read(original, row['file'], missing=True) is None, 'Original acquired a same-path test; review a new package.')
            require(current_sha in (None, row['after_sha256']), 'Unknown existing test file: ' + row['file'])
        plan.append({'file': row['file'], 'before': current, 'after': after})
    require(len(set(states)) == 1, 'Partially patched production target rejected.')
    state = states[0]
    if state == 'after':
        require(all(p['before'] == p['after'] for p in plan), 'Patched production copy has an incomplete test package.')
    return {'target': target, 'original': original, 'core_source': core_source, 'package': package, 'metadata': metadata, 'state': state, 'plan': plan}


def atomic_write(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix='.academy-records-contract-', dir=path.parent)
    try:
        with os.fdopen(handle, 'wb') as stream:
            stream.write(data)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()


def apply(checked):
    # Re-run every guard immediately before preparing any write.
    fresh = inspect(checked['target'], checked['original'], checked['core_source'], checked['package'])
    require(fresh['state'] == checked['state'], 'Target changed after preflight.')
    if fresh['state'] == 'after':
        return 0
    for row in fresh['plan']:
        require(read(fresh['target'], row['file'], missing=True) == row['before'], 'Target changed before the first write.')
    written = []
    try:
        for row in fresh['plan']:
            if row['before'] == row['after']:
                continue
            path = fresh['target'] / row['file']
            require(read(fresh['target'], row['file'], missing=True) == row['before'], 'Concurrent target edit; stopping.')
            mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
            atomic_write(path, row['after'], mode)
            written.append((row, mode))
        require(inspect(fresh['target'], fresh['original'], fresh['core_source'], fresh['package'])['state'] == 'after', 'Post-apply verification failed.')
    except BaseException:
        for row, mode in reversed(written):
            path = fresh['target'] / row['file']
            require(read(fresh['target'], row['file']) == row['after'], 'Concurrent edit prevents automatic rollback; preserve it for review.')
            if row['before'] is None:
                path.unlink()
            else:
                atomic_write(path, row['before'], mode)
        raise
    return len(written)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--core-source', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path, help='Optional NEW report file; rejected if it exists. No report is written by default.')
    args = parser.parse_args()
    require(args.report is None or not args.report.exists(), 'Report destination already exists.')
    require(args.report is None or args.report.resolve().is_relative_to(PACKAGE.resolve()), 'Report must remain in this new support package.')
    checked = inspect(args.target, args.original, args.core_source)
    writes = apply(checked) if args.apply else 0
    final = inspect(args.target, args.original, args.core_source)
    result = {'passed': True, 'checked_at': datetime.now(timezone.utc).isoformat(), 'mode': 'apply' if args.apply else 'read_only', 'production_state': final['state'], 'files_written': writes,
              'contract_metadata_sha256': METADATA_SHA256, 'original_source_unchanged': True, 'core_contracts_unchanged': True, 'base_compatibility_files_unchanged': len(final['metadata']['base_compatibility_files']),
              'auth_store_context_api_offline_gates_unchanged': True, 'browser_api_db_reload_actions': False,
              'target_files': [{'file': r['file'], 'sha256': fingerprint(read(final['target'], r['file'], missing=True))} for r in final['metadata']['files']]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.open('x').write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        raise SystemExit('IC Records preparation stopped: ' + str(error)) from error
