"""Scan Academy files and local Git objects without printing credential values."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path


PATTERNS = {
    'private-key material': rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
    'GitHub credential': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
    'AWS access credential': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'Google API credential': rb'\bAIza[A-Za-z0-9_-]{35}\b',
    'Slack credential': rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b',
    'Stripe secret credential': rb'\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b',
    'JWT bearer credential': rb'\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b',
    'credential-bearing URL': rb'https?://[^\s/<>"\']{1,128}:[^\s/@<>"\']{1,256}@',
    'private editor or signed URL': rb'https?://share\.descript\.com/view/[A-Za-z0-9_-]{10,}|https?://web\.descript\.com/(?:project|editor)/[A-Za-z0-9_-]{20,}|[?&](?:X-Goog-Signature|X-Amz-Signature|access_token|sig)=[A-Za-z0-9%_-]{8,}',
}
COMPILED = {name: re.compile(pattern, re.I if name in {'credential-bearing URL', 'private editor or signed URL'} else 0) for name, pattern in PATTERNS.items()}
CREDENTIAL_KEY = rb'[A-Za-z0-9_.:-]*(?:password|passwd|secret|token|api[_-]?key|accountkey|connectionstring|signingkey|encryptionkey)[A-Za-z0-9_.:-]*'
ASSIGNMENTS = (
    re.compile(rb'(?:^|[\r\n{,])\s*["\'](' + CREDENTIAL_KEY + rb')["\']\s*:\s*["\']([^"\'\r\n]{12,512})["\']', re.I | re.M),
    re.compile(rb'\b(' + CREDENTIAL_KEY + rb')["\']?\s*=\s*["\']([^"\'\r\n]{12,512})["\']', re.I),
)
PLACEHOLDER = re.compile(rb'example|placeholder|changeme|replace[_ -]?me|your[_ -]|dummy|sample|<|\$\{|\{\{', re.I)
PRIVATE_SUFFIXES = {'.pem', '.key', '.pfx', '.p12', '.jks', '.keystore', '.mobileprovision', '.env'}
PRIVATE_NAMES = {'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', 'credentials.json', 'credentials.yml', 'credentials.yaml', 'secrets.json', 'secrets.yml', 'secrets.yaml', '.netrc', '.npmrc', '.pypirc'}


def scan_bytes(data, extra_values=()):
    findings = {name for name, pattern in COMPILED.items() if pattern.search(data)}
    if any(value and value in data for value in extra_values):
        findings.add('known private training-stack credential')
    for match in (match for pattern in ASSIGNMENTS for match in pattern.finditer(data)):
        key, value = match.groups()
        if PLACEHOLDER.search(value):
            continue
        if re.search(rb'header(?:name)?$', key, re.I) and re.fullmatch(rb'X-[A-Za-z0-9-]+', value):
            continue  # A named HTTP header is metadata, not the credential sent in it.
        frequencies = [value.count(bytes([item])) / len(value) for item in set(value)]
        entropy = -sum(p * math.log2(p) for p in frequencies)
        if entropy >= 3.5 and re.fullmatch(rb'[A-Za-z0-9+/=_:;.@!%&*-]+', value):
            findings.add('possible embedded credential assignment')
    return sorted(findings)


def private_file(path):
    return path.suffix.lower() in PRIVATE_SUFFIXES or path.name.lower() in PRIVATE_NAMES or path.name.lower().startswith('.env.') or bool({'local-stack', 'private'}.intersection(path.parts))


def scan_stream(stream, extra_values=()):
    findings, previous = set(), b''
    overlap = max([4096] + [len(value) for value in extra_values])
    while True:
        chunk = stream.read(1024 * 1024)
        if not chunk:
            break
        data = previous + chunk
        findings.update(scan_bytes(data, extra_values))
        previous = data[-overlap:]
    return sorted(findings)


def git(root, *arguments):
    return subprocess.run(['git', '-C', str(root), *arguments], check=True, capture_output=True).stdout


def scan_repository(root, extra_values=()):
    root = Path(root).resolve()
    findings, count, total = [], 0, 0
    ignored_metadata = 0
    if Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != root:
        raise ValueError('Audit the root of the Academy Git repository.')
    publishable = git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
    paths = sorted(set(item.decode('utf-8') for item in publishable.split(b'\0') if item))
    for name in paths:
        path = root / name
        relative = Path(name)
        if path.is_symlink():
            findings.append({'path': relative.as_posix(), 'rule': 'symlink needs review'})
            continue
        if not path.is_file():
            continue
        count += 1
        total += path.stat().st_size
        if private_file(relative):
            findings.append({'path': relative.as_posix(), 'rule': 'private credential/configuration file'})
        with path.open('rb') as stream:
            for rule in scan_stream(stream, extra_values):
                findings.append({'path': relative.as_posix(), 'rule': rule})
    tracked = git(root, 'ls-files', '-z').split(b'\0')
    tracked = [item for item in tracked if item]
    commits = int(git(root, 'rev-list', '--all', '--count').strip() or b'0')
    object_metadata = git(root, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize)')
    blob_count = 0
    for row in object_metadata.splitlines():
        ident, kind, size = row.split()
        if kind != b'blob':
            continue
        blob_count += 1
        for rule in scan_bytes(git(root, 'cat-file', 'blob', ident.decode()), extra_values):
            findings.append({'path': 'Git blob ' + ident.decode(), 'rule': rule})
    for name in ('config', 'config.worktree'):
        path = root / '.git' / name
        if path.is_file():
            for rule in scan_bytes(path.read_bytes(), extra_values):
                findings.append({'path': '.git/' + name + ' (local metadata)', 'rule': rule})
    return {'passed': not findings, 'working_files_scanned': count, 'working_bytes_scanned': total, 'tracked_files': len(tracked), 'reachable_commits': commits, 'stored_git_blobs_scanned': blob_count, 'excluded_os_cache_files': ignored_metadata, 'known_private_values_checked': len(extra_values), 'finding_count': len(findings), 'findings': findings, 'scope': 'All tracked and non-ignored untracked working files; all stored Git blobs and local Git config. Ignored generated credentials and caches stay local. Only paths and rule names are reported.', 'limitations': 'Pattern matching cannot identify every possible credential. Review unfamiliar files before publishing; run again before each commit.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    try:
        result = scan_repository(args.root)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit('Audit could not complete; check repository access and Git availability.') from error
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
