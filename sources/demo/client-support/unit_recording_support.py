"""Independent, opt-in Unit recording source preparation and launch guards.

No global profile or private pin is read or changed. Planning never invokes Git,
reads credentials, writes files, or starts a process. Execution only accepts the
clean pinned managed checkout and prepares a fresh sibling capture directory.
The CLI never clones/installs, kills a server, opens a browser, or logs an env.
"""
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
from urllib.parse import urlsplit

VERSION = 'unit-web-recording-20261027'
BASELINE_NAME = 'unit-recording-source-baseline-20261027.json'
BASELINE_SHA256 = '34019db05b8c57bf95f12cc3b0d5b1b4654055215da6358d3aec1448146b91c9'
PROVENANCE = '.academy-unit-recording.json'
EXCLUDED = ('.git', 'node_modules', '.env*', 'private', '.private', '.aws', '.ssh',
            '.codex', '.claude', '.agents', '.npmrc', '.netrc', 'credentials.*',
            'secrets.*', '*.pem', '*.key', '*.p12', '*.p8', '*.pfx', '*.keystore',
            '*.mobileprovision', '.expo', '.metro*', 'dist', 'build', 'coverage',
            'logs', '*.log', 'Pods', 'DerivedData', '.gradle', '.cxx', '.DS_Store')
RUNTIME_DIRECTORIES = {'.expo', '.metro-cache'}
HELPERS = ('unit_recording_support.py', 'unit-recording-prepare.py', 'unit-recording-launch.py')


class SupportError(ValueError):
    """Actionable failure that contains no file contents or environment values."""


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(name):
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise SupportError('A source/patch path is not a safe relative path.')
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
        raise SupportError('A source/patch path escapes its declared root.')
    return path


def excluded(name):
    return any(fnmatch.fnmatchcase(part.casefold(), pattern.casefold())
               for part in relative(name).parts for pattern in EXCLUDED)


def no_links(path, root):
    path, root = Path(path), Path(root)
    if path != root and root not in path.parents:
        raise SupportError('Path must remain inside its managed root.')
    for current in (path, *path.parents):
        if current.is_symlink():
            raise SupportError('Managed source/destination paths must not use symlinks.')
        if current == root:
            return
    raise SupportError('Path does not reach its managed root.')


def file_hashes(root, expected, label):
    for name, wanted in expected.items():
        path = Path(root).joinpath(*relative(name).parts)
        no_links(path, Path(root))
        if not path.is_file() or digest(path) != wanted:
            raise SupportError(label + ' hash changed: ' + name)


class Layout:
    def __init__(self, support=None):
        self.support = Path(support or Path(__file__).resolve().parent).resolve()
        self.demo = self.support.parent
        self.sources = self.demo.parent
        self.source = self.demo / 'checkout-expansion' / 'Unit'
        self.captures = self.demo / 'capture-apps'
        self.default_destination = self.captures / 'Unit-recording-20261027'

    def destination(self, value=None, fresh=False):
        path = Path(os.path.abspath(os.path.expanduser(str(value or self.default_destination))))
        if path.parent != self.captures or not re.fullmatch(r'Unit-recording-[A-Za-z0-9][A-Za-z0-9-]{0,64}', path.name):
            raise SupportError('Choose a direct capture-apps/Unit-recording-<version> destination.')
        no_links(path, self.demo)
        if path == self.source or self.source in path.parents or path in self.source.parents:
            raise SupportError('Source and recording destination must be separate.')
        if fresh and path.exists():
            raise SupportError('Recording destination already exists; choose a fresh versioned directory.')
        return path


def load_bundle(layout):
    path = layout.support / BASELINE_NAME
    if not path.is_file() or digest(path) != BASELINE_SHA256:
        raise SupportError('Recording baseline changed; restore the reviewed support bundle.')
    baseline = json.loads(path.read_text())
    for field in ('source_files', 'patched_files', 'dependency_files', 'dependency_source_files'):
        if not isinstance(baseline.get(field), dict) or not baseline[field]:
            raise SupportError('Recording baseline is incomplete: ' + field)
        for name, value in baseline[field].items():
            relative(name)
            if not re.fullmatch('[0-9a-f]{64}', value):
                raise SupportError('Recording baseline contains an invalid checksum.')
    patches = []
    for item in baseline.get('patches', []):
        patch = layout.sources.joinpath(*relative(item['file']).parts)
        no_links(patch, layout.sources)
        if not patch.is_file() or digest(patch) != item['sha256']:
            raise SupportError('A reviewed recording patch changed; restore the support bundle.')
        patches.append(patch.read_text())
    if len(patches) != 2:
        raise SupportError('Both reviewed Unit patches are required.')
    identity = {BASELINE_NAME: BASELINE_SHA256}
    for name in HELPERS:
        path = layout.support / name
        if not path.is_file() or path.is_symlink():
            raise SupportError('Recording support helper is missing or linked.')
        identity[name] = digest(path)
    identity.update({item['file']: item['sha256'] for item in baseline['patches']})
    return baseline, patches, identity


def git_state(source):
    """Read-only future execution; tests replace this entire boundary, never run Git."""
    def read(*args):
        env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
        command = ['git', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', '-C', str(source), *args]
        result = subprocess.run(command, env=env, capture_output=True, check=False)
        if result.returncode:
            raise SupportError('Cannot verify the managed Git checkout; no source was changed.')
        return result.stdout.decode('utf-8')
    return {'root': read('rev-parse', '--show-toplevel').strip(),
            'head': read('rev-parse', 'HEAD').strip(),
            'status': read('status', '--porcelain=v1', '--untracked-files=all', '--ignore-submodules=none'),
            'files': read('ls-files', '--cached', '-z').split('\0')[:-1]}


def verify_source(layout, baseline):
    source = layout.source
    no_links(source, layout.demo)
    if not source.is_dir() or not (source / '.git').is_dir() or (source / '.git').is_symlink():
        raise SupportError('Prepare the clean managed Unit checkout first; this helper never clones it.')
    state = git_state(source)
    if Path(state['root']).resolve() != source or state['head'] != baseline['source_git_revision']:
        raise SupportError('Managed Unit checkout is not at the reviewed pinned revision.')
    if state['status'].strip():
        raise SupportError('Managed Unit source has modified or untracked files; preserve it and use a clean pinned checkout.')
    tracked = state['files']
    if not tracked or len(set(tracked)) != len(tracked):
        raise SupportError('Managed Unit tracked-file inventory is invalid.')
    required = set(baseline['source_files']) | set(baseline['dependency_files'])
    if not required <= set(tracked):
        raise SupportError('Pinned Unit inputs must be tracked files.')
    file_hashes(source, baseline['source_files'], 'Original source')
    file_hashes(source, baseline['dependency_files'], 'Dependency lock/manifest')
    for name in baseline.get('must_be_absent', []):
        path = source.joinpath(*relative(name).parts)
        if path.exists() or path.is_symlink():
            raise SupportError('Source already contains a recording-only file: ' + name)
    dependencies = source / 'node_modules'
    if not dependencies.is_dir() or dependencies.is_symlink():
        raise SupportError('Install the pinned dependencies in the managed checkout first; no install is performed here.')
    file_hashes(dependencies, baseline['dependency_source_files'], 'Installed SDK source')
    cli = dependencies / 'expo/bin/cli'
    no_links(cli, dependencies)
    if not cli.is_file():
        raise SupportError('Managed Expo CLI is missing; no dependency installation is performed here.')
    inventory = {}
    for name in tracked:
        relative(name)
        if excluded(name):
            continue
        path = source.joinpath(*relative(name).parts)
        no_links(path, source)
        if not path.is_file():
            raise SupportError('A tracked application source is missing or not a regular file.')
        inventory[name] = digest(path)
    return inventory, digest(cli)


def patch_sections(text):
    lines, result, index = text.splitlines(keepends=True), [], 0
    while index < len(lines):
        if not lines[index].startswith('--- ') or index + 1 >= len(lines) or not lines[index + 1].startswith('+++ '):
            raise SupportError('Recording patch has unsupported headers.')
        old, new = lines[index][4:].strip(), lines[index + 1][4:].strip()
        if not new.startswith('b/') or old != '/dev/null' and (not old.startswith('a/') or old[2:] != new[2:]):
            raise SupportError('Recording patch paths are invalid.')
        name = str(relative(new[2:]))
        if excluded(name):
            raise SupportError('Recording patch targets an excluded path.')
        end = index + 2
        while end < len(lines) and not lines[end].startswith('--- '):
            end += 1
        result.append((name, old == '/dev/null', lines[index + 2:end]))
        index = end
    return result


def exact_patch(original, hunks):
    source, output, position, index = original.splitlines(keepends=True), [], 0, 0
    while index < len(hunks):
        header = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n?', hunks[index])
        if not header:
            raise SupportError('Recording patch hunk is malformed.')
        start, count, new_count = int(header[1]), int(header[2] or 1), int(header[4] or 1)
        start = start - 1 if count else start
        index += 1
        chunk = []
        while index < len(hunks) and not hunks[index].startswith('@@ '):
            line = hunks[index]
            if not line.startswith((' ', '-', '+')):
                raise SupportError('Recording patch contains an unsupported hunk line.')
            chunk.append(line)
            index += 1
        expected = [line[1:] for line in chunk if line.startswith((' ', '-'))]
        replacement = [line[1:] for line in chunk if line.startswith((' ', '+'))]
        if count != len(expected) or new_count != len(replacement) or start < position or source[start:start + count] != expected:
            raise SupportError('Recording patch does not match its exact reviewed input; no fuzzy apply is allowed.')
        output.extend(source[position:start])
        output.extend(replacement)
        position = start + count
    output.extend(source[position:])
    return ''.join(output)


def patch_outputs(layout, baseline, patches):
    outputs = {}
    for text in patches:
        for name, creates, hunks in patch_sections(text):
            if name not in baseline['patched_files'] or name in outputs:
                raise SupportError('Recording patch target is undeclared or repeated.')
            if creates != (name in baseline.get('must_be_absent', [])):
                raise SupportError('Recording patch creation/deletion does not match the baseline.')
            if not creates and name not in baseline['source_files']:
                raise SupportError('Recording patch input is undeclared.')
            old = '' if creates else layout.source.joinpath(*relative(name).parts).read_text()
            new = exact_patch(old, hunks).encode('utf-8')
            if hashlib.sha256(new).hexdigest() != baseline['patched_files'][name]:
                raise SupportError('Recording patch output hash does not match: ' + name)
            outputs[name] = new
    if set(outputs) != set(baseline['patched_files']):
        raise SupportError('The recording patches do not produce all declared output files.')
    return outputs


def preparation_plan(layout, destination=None):
    baseline, _, _ = load_bundle(layout)
    target = layout.destination(destination, fresh=True)
    return {'support_version': VERSION, 'mode': 'read-only plan; execution verification pending',
            'managed_source': str(layout.source), 'destination': str(target),
            'pinned_revision': baseline['source_git_revision'], 'patches': baseline['patches'],
            'outputs': baseline['patched_files'], 'credential_requirement': 'none for planning',
            'notice': 'No Git, copy, install, private/profile pin, environment read, server or browser action.'}


def prepare(layout, destination=None):
    baseline, patches, identity = load_bundle(layout)
    target = layout.destination(destination, fresh=True)
    inventory, cli_hash = verify_source(layout, baseline)
    outputs = patch_outputs(layout, baseline, patches)
    # Nothing is created until every input/patch/output has been verified.
    target.parent.mkdir(parents=True, exist_ok=True)
    no_links(target, layout.demo)
    target.mkdir()  # Exclusive: even an empty existing directory is refused.
    for name, wanted in inventory.items():
        data = layout.source.joinpath(*relative(name).parts).read_bytes()
        if hashlib.sha256(data).hexdigest() != wanted:
            raise SupportError('Source changed during copying; new destination is incomplete and must not launch.')
        path = target.joinpath(*relative(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    for name, data in outputs.items():
        path = target.joinpath(*relative(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (target / 'node_modules').symlink_to(layout.source / 'node_modules', target_is_directory=True)
    expected = {**inventory, **baseline['patched_files']}
    file_hashes(target, expected, 'Prepared source')
    # Revalidate the complete source/dependencies after the copy as well.
    after, after_cli = verify_source(layout, baseline)
    if after != inventory or after_cli != cli_hash:
        raise SupportError('Source changed during preparation; new destination is incomplete and must not launch.')
    record = {'schema_version': 1, 'support_version': VERSION,
              'prepared_at': datetime.now(timezone.utc).isoformat(),
              'source_revision': baseline['source_git_revision'], 'support_hashes': identity,
              'source_files': inventory, 'prepared_files': expected, 'expo_cli_sha256': cli_hash,
              'dependency_files': baseline['dependency_files'], 'dependency_source_files': baseline['dependency_source_files'],
              'excluded_patterns': list(EXCLUDED), 'environment_values_recorded': False,
              'scope': 'Source compatibility only; no browser/native/provider success or media qualification.'}
    with (target / PROVENANCE).open('x') as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return record


def verify_prepared(layout, destination=None):
    baseline, patches, identity = load_bundle(layout)
    target = layout.destination(destination)
    record_path = target / PROVENANCE
    if not target.is_dir() or not record_path.is_file() or record_path.is_symlink():
        raise SupportError('Recording copy has no completed preparation provenance; prepare a fresh copy.')
    try:
        record = json.loads(record_path.read_text())
    except (ValueError, OSError):
        raise SupportError('Recording provenance is unreadable; preserve this copy and prepare a fresh version.') from None
    inventory, cli_hash = verify_source(layout, baseline)
    patch_outputs(layout, baseline, patches)
    expected = {**inventory, **baseline['patched_files']}
    if (record.get('schema_version') != 1 or record.get('support_version') != VERSION
            or record.get('source_revision') != baseline['source_git_revision']
            or record.get('support_hashes') != identity or record.get('source_files') != inventory
            or record.get('prepared_files') != expected or record.get('expo_cli_sha256') != cli_hash
            or record.get('dependency_files') != baseline['dependency_files']
            or record.get('dependency_source_files') != baseline['dependency_source_files']):
        raise SupportError('Recording provenance no longer matches the reviewed source/support; prepare a fresh version.')
    dependencies = target / 'node_modules'
    if not dependencies.is_symlink() or dependencies.resolve() != layout.source / 'node_modules':
        raise SupportError('Recording copy must link only its verified managed-source dependencies.')
    file_hashes(target, expected, 'Prepared source')
    actual = set()
    allowed_directories = {str(parent) for name in expected for parent in PurePosixPath(name).parents if str(parent) != '.'}
    for root, directories, files in os.walk(target, followlinks=False):
        root = Path(root)
        kept = []
        for name in directories:
            path = root / name
            if path == dependencies:
                continue
            if path.is_symlink():
                raise SupportError('Recording copy contains an unexpected linked directory.')
            if root == target and name in RUNTIME_DIRECTORIES:
                continue
            if path.relative_to(target).as_posix() not in allowed_directories:
                raise SupportError('Recording copy contains an unexpected or private directory.')
            kept.append(name)
        directories[:] = kept
        for name in files:
            path = root / name
            if path == record_path:
                continue
            if path.is_symlink():
                raise SupportError('Recording copy contains an unexpected linked file.')
            actual.add(path.relative_to(target).as_posix())
    if actual != set(expected):
        raise SupportError('Recording copy contains unexpected, private, environment or missing files.')
    return target


def launch_plan(layout, destination=None, port=19103, api_origin='http://127.0.0.1:18967'):
    load_bundle(layout)
    target = layout.destination(destination)
    url = urlsplit(api_origin)
    try:
        api_port = url.port
    except ValueError:
        raise SupportError('Use a valid loopback API origin.') from None
    if (url.scheme != 'http' or url.hostname not in ('localhost', '127.0.0.1', '::1')
            or url.username is not None or url.password is not None or url.path not in ('', '/')
            or url.query or url.fragment or api_port is None or not 1024 <= api_port <= 65535):
        raise SupportError('Only a local HTTP loopback API origin without credentials/path/query is allowed.')
    if isinstance(port, bool) or not isinstance(port, int) or not 1024 <= port <= 65535:
        raise SupportError('Use a local web port between 1024 and 65535.')
    origin = api_origin.rstrip('/')
    return {'support_version': VERSION, 'mode': 'read-only launch plan; verification pending',
            'destination': str(target), 'api_origin': origin, 'port': port,
            'command': ['node', 'node_modules/expo/bin/cli', 'start', '--web', '--localhost', '--port', str(port), '--clear'],
            'required_environment_variable': 'UNIT_MAPBOX_PUBKEY (execution only; inherited, never printed/saved)',
            'CI_restart': 'CI mode disables Metro watch/reload. Explicitly restart this server with --clear after reviewed source changes.',
            'notice': 'No credentials read, files written, Git called, server started/killed, browser opened or profile pin changed.'}


def launch(layout, destination=None, port=19103, api_origin='http://127.0.0.1:18967'):
    instructions = launch_plan(layout, destination, port, api_origin)
    target = verify_prepared(layout, destination)
    if not os.environ.get('UNIT_MAPBOX_PUBKEY', '').startswith('pk.'):
        raise SupportError('Set inherited UNIT_MAPBOX_PUBKEY before launch; its value is never printed or saved.')
    node = shutil.which('node')
    if not node:
        raise SupportError('Node.js must already be available; this helper does not install it.')
    env = dict(os.environ)
    env.update({'APP_ENV': 'development', 'EXPO_NO_DOTENV': '1', 'EXPO_NO_TELEMETRY': '1',
                'DO_NOT_TRACK': '1', 'CI': '1', 'BROWSER': 'none', 'EXPO_OFFLINE': '1',
                'UNIT_BASE_API_URL': instructions['api_origin'], 'UNIT_API_VERSION': 'v4',
                'UNIT_RESGRID_API_URL': '/api/v4', 'UNIT_CHANNEL_API_URL': instructions['api_origin'] + '/'})
    env.update({'UNIT_' + name: '' for name in ('COUNTLY_APP_KEY', 'COUNTLY_URL', 'COUNTLY_SERVER_URL', 'SENTRY_DSN', 'LOGGING_KEY')})
    command = [node, str(target / 'node_modules/expo/bin/cli'), *instructions['command'][2:]]
    print('Launching verified Unit recording copy against the local API; CI source changes require an explicit restart.', flush=True)
    return subprocess.call(command, cwd=target, env=env)
