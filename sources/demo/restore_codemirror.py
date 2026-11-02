#!/usr/bin/env python3
"""Restore the exact pinned editor sources needed by the Workflow page."""
import hashlib
import json
from pathlib import Path
import tarfile


def restore(destination):
    vendor = Path(__file__).resolve().parent / 'vendor'
    manifest = json.loads((vendor / 'codemirror-manifest.json').read_text())
    archive = vendor / manifest['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('CodeMirror archive hash mismatch.')
    with tarfile.open(archive) as source:
        for item in manifest['files']:
            target = Path(destination) / item['target']
            if Path(destination).resolve() not in target.resolve().parents:
                raise ValueError('Unsafe editor asset path.')
            data = source.extractfile(item['source']).read()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError('CodeMirror source hash mismatch: ' + item['source'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)


if __name__ == '__main__':
    restore(Path(__file__).resolve().parent / 'publish/web/wwwroot/lib/codemirror')
    print('Restored pinned CodeMirror source assets and MIT license.')
