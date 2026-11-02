"""Pinned source sets for isolated Academy reproductions; no work at import time."""
import hashlib
import json
from pathlib import Path
import subprocess

ACADEMY = Path(__file__).resolve().parents[2]
PROFILE_DEFAULTS = {
    'legacy': ('resgrid-academy-capture', 18867),
    'expansion': ('resgrid-academy-expansion', 18967),
}
APPS = ('Dispatch', 'Responder', 'Unit', 'IC')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def select_profile(demo, requested=None):
    saved = Path(demo) / 'private/source-profile.json'
    pinned = json.loads(saved.read_text()) if saved.exists() else None
    name = requested or (pinned['source_profile'] if pinned else 'legacy')
    if name not in PROFILE_DEFAULTS:
        raise ValueError('Unknown source profile: ' + name)
    if pinned and pinned['source_profile'] != name:
        raise ValueError('This recording profile already pins another source profile. Use a separate Academy checkout; existing data was preserved.')
    return name, pinned


def load_source_set(name, academy=ACADEMY):
    academy = Path(academy)
    if name == 'legacy':
        path = academy / 'sources/evidence/source-manifest.json'
        manifest = json.loads(path.read_text())
        return {'name': name, 'manifest_path': str(path), 'manifest_sha256': digest(path),
                'repositories': {'Core': {'head': manifest['recorded_source_head'], 'upstream': manifest['upstream']}},
                'snapshots': {}, 'support': {}, 'dependencies': {}, 'academy': str(academy)}
    if name != 'expansion':
        raise ValueError('Unknown source profile: ' + name)
    definition = academy / 'sources/demo/source-profiles.json'
    specification = json.loads(definition.read_text())['expansion']
    path = academy / specification['manifest']
    if digest(path) != specification['manifest_sha256']:
        raise ValueError('Expansion source manifest hash changed; review and refresh the source profile deliberately.')
    manifest = json.loads(path.read_text())
    if manifest['missing_references'] or manifest['excluded_references']:
        raise ValueError('Expansion evidence has unresolved source references.')
    repositories = {}
    for repo, metadata in manifest['repositories'].items():
        repositories[repo] = {'head': metadata['head'], 'upstream': specification['upstreams'][repo],
                              'recorded_original_root': metadata['source_root']}
    snapshots = {repo: {} for repo in repositories}
    for file in manifest['files']:
        snapshot = academy / 'sources' / file['snapshot_path']
        if digest(snapshot) != file['snapshot_sha256']:
            raise ValueError('Expansion snapshot hash mismatch: ' + file['snapshot_path'])
        snapshots[file['repo']][file['path']] = file['source_sha256']
    for relative, expected in specification['support_hashes'].items():
        if digest(academy / relative) != expected:
            raise ValueError('Recording support hash changed: ' + relative + '. Review and refresh source-profiles.json before continuing.')
    core_patch = json.loads((academy / 'sources/demo/core-support/workflow-edit-validation.json').read_text())
    if core_patch['baseline_head'] != repositories['Core']['head']:
        raise ValueError('Workflow support patch and expansion Core HEAD disagree.')
    if digest(academy / 'sources/demo/core-support/workflow-edit-validation.patch') != core_patch['patch_sha256']:
        raise ValueError('Workflow support patch hash mismatch.')
    return {'name': name, 'manifest_path': str(path), 'manifest_sha256': digest(path),
            'repositories': repositories, 'snapshots': snapshots, 'support': specification['client_support'],
            'core_patch': core_patch, 'dependencies': specification['dependencies'], 'academy': str(academy),
            'definition_sha256': digest(definition), 'support_hashes': specification['support_hashes']}


def summary(source_set):
    return {'source_profile': source_set['name'], 'manifest': source_set['manifest_path'],
            'manifest_sha256': source_set['manifest_sha256'], 'repositories': source_set['repositories'],
            'workflow_patch_sha256': source_set.get('core_patch', {}).get('patch_sha256'),
            'definition_sha256': source_set.get('definition_sha256'),
            'support_hashes': source_set.get('support_hashes', {}),
            'client_support': source_set['support'], 'dependency_locks': source_set['dependencies']}


def verify_pin(pinned, source_set):
    if pinned and pinned['manifest_sha256'] != source_set['manifest_sha256']:
        raise ValueError('The source manifest differs from this recording profile pin. Preserve the current profile and use a separate checkout.')
    if pinned and pinned.get('definition_sha256') != source_set.get('definition_sha256'):
        raise ValueError('The source profile definition differs from this installation pin. Review support changes in a separate checkout; existing state was preserved.')


def save_pin(demo, source_set):
    path = Path(demo) / 'private/source-profile.json'
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(summary(source_set), indent=2) + '\n')
    path.chmod(0o600)


def git(root, *arguments):
    return subprocess.check_output(['git', '-C', str(root), *arguments], text=True).strip()


def managed_source(demo, repo):
    return Path(demo).resolve() / 'checkout-expansion' / repo


def managed_client(demo, app, source_set):
    if app in source_set['support']:
        return Path(demo).resolve() / 'capture-apps' / app
    return managed_source(demo, app)


def original_source(root, repo, source_set):
    original = source_set['repositories'][repo].get('recorded_original_root')
    return bool(original and Path(root).resolve() == Path(original).resolve())


def acquire(root, repo, source_set):
    root = Path(root)
    metadata = source_set['repositories'][repo]
    if root.exists() and not root.is_dir():
        raise ValueError('Source destination is not a directory: ' + str(root))
    if root.exists() and any(root.iterdir()):
        if not (root / '.git').exists():
            raise ValueError('Source destination is nonempty and is not a Git checkout: ' + str(root))
        return
    root.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'clone', '--no-checkout', metadata['upstream'], str(root)], check=True)
    subprocess.run(['git', '-C', str(root), 'checkout', '--detach', metadata['head']], check=True)


def verify_repository(root, repo, source_set, allowed_changes=()):
    root = Path(root).resolve()
    if not (root / '.git').exists() or Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root:
        raise ValueError('Supply a complete, independent Git checkout for ' + repo + ': ' + str(root))
    if git(root, 'rev-parse', 'HEAD') != source_set['repositories'][repo]['head']:
        raise ValueError(repo + ' HEAD differs from the pinned source set; no checkout or local edits were reset.')
    changes = set(git(root, 'diff', '--name-only', 'HEAD').splitlines())
    if changes - set(allowed_changes):
        raise ValueError(repo + ' has unrecorded tracked edits; preserve them and choose a clean isolated checkout.')


def verify_cited(root, repo, source_set, overrides=None):
    expected = dict(source_set['snapshots'].get(repo, {}))
    expected.update(overrides or {})
    for relative, checksum in expected.items():
        path = Path(root) / relative
        actual = digest(path) if path.is_file() else None
        if actual != checksum:
            raise ValueError(repo + ' source hash mismatch: ' + relative)


def prepare_core(root, demo, source_set, allow_apply=True):
    if source_set['name'] != 'expansion':
        return {'patch': 'legacy profile: no expansion patch'}
    root = Path(root).resolve()
    metadata = source_set['core_patch']
    files = metadata['files']
    verify_repository(root, 'Core', source_set, [file['path'] for file in files])
    actual = [digest(root / file['path']) for file in files]
    baseline = [file['baseline_sha256'] for file in files]
    modified = [file['modified_sha256'] for file in files]
    if actual == modified:
        state = 'already applied; hashes verified'
    elif actual == baseline:
        if not allow_apply:
            raise ValueError('The expansion workflow patch has not been applied; run the reviewed expansion setup first.')
        if root != managed_source(demo, 'Core') or original_source(root, 'Core', source_set):
            raise ValueError('Automatic support patches are restricted to the managed isolated expansion checkout. Review/apply the patch manually in a disposable checkout, then pass --core again; the original checkout was preserved.')
        patch = Path(source_set['academy']) / 'sources/demo/core-support/workflow-edit-validation.patch'
        subprocess.run(['git', '-C', str(root), 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(root), 'apply', str(patch)], check=True)
        if [digest(root / file['path']) for file in files] != modified:
            raise ValueError('Workflow patch result hashes differ from the retained fix.')
        state = 'applied only to managed isolated checkout; hashes verified'
    else:
        raise ValueError('Workflow patch files have mixed or unknown hashes; preserve local edits and review before continuing.')
    verify_cited(root, 'Core', source_set)
    return {'patch': state, 'patch_sha256': metadata['patch_sha256']}


def client_baseline(app, source_set):
    support = source_set['support'].get(app)
    if not support:
        return None
    return json.loads((Path(source_set['academy']) / support['baseline']).read_text())


def verify_client(source, destination, app, source_set):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not destination.is_dir():
        raise ValueError(app + ' launch directory does not exist; prepare the isolated client first: ' + str(destination))
    verify_repository(source, app, source_set)
    verify_cited(source, app, source_set)
    baseline = client_baseline(app, source_set)
    if baseline:
        if baseline['source_git_revision'] != source_set['repositories'][app]['head']:
            raise ValueError(app + ' compatibility baseline and source HEAD disagree.')
        verify_cited(source, app, {'snapshots': {}}, baseline['source_files'])
        verify_cited(source / 'node_modules', app, {'snapshots': {}}, baseline.get('dependency_source_files', {}))
        verify_cited(destination, app, source_set, baseline['patched_files'])
        link = destination / 'node_modules'
        if not link.is_symlink() or link.resolve() != (source / 'node_modules').resolve():
            raise ValueError(app + ' prepared copy must link to its verified source dependencies.')
    else:
        if destination != source:
            raise ValueError(app + ' uses its managed clean checkout directly; no recording compatibility patch is declared.')
        verify_cited(destination, app, source_set)
    for relative, checksum in source_set['dependencies'][app]['files'].items():
        if digest(source / relative) != checksum:
            raise ValueError(app + ' dependency metadata changed: ' + relative)
