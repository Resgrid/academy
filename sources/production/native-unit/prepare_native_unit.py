#!/usr/bin/env python3
"""Prepare only a fresh owned Unit native source from the reviewed pinned tree.

Reads original Git objects (archive/ls-tree only), copies no Git/environment/
private data, verifies retained exact patches and SDK/lock identity, and links
installed dependency source. No install/build/launch/server/auth action here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True
REVISION = '0753b6baafbaec74617a412cd9c87fa9de899d47'
ARTIFACT = Path('/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025')
SUPPORT = ARTIFACT / 'repo/sources/demo/client-support'
ORIGINAL = Path('/Users/shawn/Documents/dev/Unit')
DESTINATION = ARTIFACT / 'native-unit-20261028/source'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('unit_recording_support_v2', SUPPORT / 'unit_recording_support_v2.py')
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    baseline, patches, support_identity = support.load_bundle(support.Layout(SUPPORT))
    if baseline['source_git_revision'] != REVISION:
        raise ValueError('Reviewed source revision changed')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    def git(*arguments):
        result = subprocess.run(['git', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', '-C', str(ORIGINAL), *arguments], env=env, capture_output=True)
        if result.returncode:
            raise ValueError('Read-only pinned Git source verification failed')
        return result.stdout
    if git('rev-parse', 'HEAD').decode().strip() != REVISION:
        raise ValueError('Original source HEAD differs from pinned revision; no copy made')
    files = [x.decode() for x in git('ls-tree', '-r', '--name-only', '-z', REVISION).split(b'\0') if x]
    selected = [name for name in files if not support.excluded(name)]
    if DESTINATION.exists() or DESTINATION.is_symlink():
        raise ValueError('Native source destination already exists; preserve it')
    support.file_hashes(ORIGINAL, baseline['dependency_files'], 'Original dependency manifest/lock')
    deps = ORIGINAL / 'node_modules'
    support.file_hashes(deps, baseline['dependency_source_files'], 'Installed SDK source')
    if not args.prepare:
        print(json.dumps({'mode': 'read-only plan', 'revision': REVISION, 'selected_files': len(selected), 'destination': str(DESTINATION), 'patch_count': len(patches), 'native_or_server_action': False}, indent=2))
        return
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    archive = git('archive', '--format=tar', REVISION, '--', *selected)
    DESTINATION.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as stream:
        for member in stream:
            support.relative(member.name)
            if support.excluded(member.name):
                raise ValueError('Archive unexpectedly contains an excluded path')
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Archive has a link or special file; preserve failed copy for review')
            target = DESTINATION / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(stream.extractfile(member).read())
    support.file_hashes(DESTINATION, baseline['source_files'], 'Pinned archived source')
    support.file_hashes(DESTINATION, baseline['dependency_files'], 'Archived dependency manifests')
    before = {name: sha(DESTINATION / name) for name in selected}
    for patch in patches:
        for name, new, hunks in support.patch_sections(patch):
            target = DESTINATION / name
            old = '' if new else target.read_text()
            if new and target.exists():
                raise ValueError('Recording new-file patch would overwrite an existing file')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(support.exact_patch(old, hunks))
    support.file_hashes(DESTINATION, baseline['patched_files'], 'Reviewed recording output')
    (DESTINATION / 'node_modules').symlink_to(deps, target_is_directory=True)
    after = {str(p.relative_to(DESTINATION)): sha(p) for p in DESTINATION.rglob('*') if p.is_file() and 'node_modules' not in p.relative_to(DESTINATION).parts}
    changed = {name for name, digest in after.items() if before.get(name) != digest}
    if changed != set(baseline['patched_files']):
        raise ValueError('Prepared source has undeclared changes')
    proof = {'kind': 'fresh_native_unit_pinned_source_preparation', 'created_at': datetime.now(timezone.utc).isoformat(), 'revision': REVISION,
             'original_source': str(ORIGINAL), 'destination': str(DESTINATION), 'archive_source_files': before, 'prepared_source_files': after,
             'support_identity': support_identity, 'dependency_manifest_files': baseline['dependency_files'], 'sdk_source_files': baseline['dependency_source_files'],
             'original_writes': False, 'git_mutations': False, 'environment_or_private_data_copied': False, 'native_build_or_launch': False}
    path = DESTINATION.parent / 'source-preparation.json'
    path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'prepared': True, 'revision': REVISION, 'files': len(after), 'declared_recording_outputs': len(changed), 'proof': str(path), 'proof_sha256': sha(path)}, indent=2))


if __name__ == '__main__':
    main()
