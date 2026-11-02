"""Prepare a pinned BigBoard recording copy without environment files or Git writes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

SUPPORT = Path(__file__).resolve().parent
BASELINE_SHA = '5495e5289471278a6f2512cb1de37839a998f30399f36e20a916886d638335bc'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    baseline = SUPPORT / 'source-baseline.json'
    assert sha(baseline) == BASELINE_SHA, 'Changed source baseline; inspect it first.'
    data = json.loads(baseline.read_text())
    source, target = args.source.resolve(), args.destination.resolve()
    assert target != source and source not in target.parents
    revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == data['source_git_revision'], 'BigBoard revision differs from the reviewed source.'
    for relative, digest in data['source_files'].items():
        rel = Path(relative)
        assert not rel.is_absolute() and '..' not in rel.parts
        original = source / rel
        assert not original.is_symlink() and sha(original) == digest, 'Changed source: ' + relative
    assert (source / 'node_modules/expo/bin/cli').is_file(), 'Install matching dependencies first.'
    result = dict(app='BigBoard', source_revision=revision, source_files_verified=len(data['source_files']),
                  destination=str(target), environment_files_copied=0, original_source_mutations=0, prepared=False)
    if args.prepare:
        assert not target.exists(), 'Preserve existing recording copies; choose a new destination.'
        target.mkdir(parents=True)
        for relative in data['source_files']:
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, output)
        (target / 'node_modules').symlink_to(source / 'node_modules', target_is_directory=True)
        for relative, digest in data['source_files'].items():
            assert sha(target / relative) == digest and sha(source / relative) == digest
        result['prepared'] = True
        result['baseline_sha256'] = BASELINE_SHA
        (target / 'academy-recording-provenance.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
