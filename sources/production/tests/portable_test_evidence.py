"""Exact historical test inputs, independent of a surrounding Core checkout.

These test-only contexts change input locations. Production implementations,
expected hashes, proof fields, approvals and strict validators stay unchanged.
"""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from unittest.mock import patch


FIXTURES = Path(__file__).resolve().parent / 'fixtures/standalone-evidence-20261030'
MANIFEST_SHA256 = '315d35dbba33f324674c19dfecf4d4e12c846e257149818ac7d1bb98a4df7ea9'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest():
    path = FIXTURES / 'manifest.json'
    if sha(path) != MANIFEST_SHA256:
        raise ValueError('Portable test evidence manifest changed.')
    return json.loads(path.read_text())


@contextmanager
def retained_core_sources(module):
    """Supply all exact cited bytes through the historical ROOT.parents[2] locator."""
    data = manifest()
    evidence_path = module.SOURCES / module.BASE / 'source-evidence.json'
    identity = [x for x in data['source_evidence'] if x['lesson_id'] == module.NAME]
    if len(identity) != 1 or sha(evidence_path) != identity[0]['sha256']:
        raise ValueError('Original cited-source manifest changed or is missing.')
    evidence = json.loads(evidence_path.read_text())['files']
    fixtures = [x for x in data['cited_core_files'] if x['lesson_id'] == module.NAME]
    expected = {(x['repo'], x['path'], x['sha256']) for x in evidence}
    retained = {(x['repo'], x['cited_path'], x['sha256']) for x in fixtures}
    if len(evidence) != len(fixtures) or expected != retained:
        raise ValueError('Portable cited-source coverage differs from original evidence.')
    for entry in fixtures:
        path = FIXTURES / entry['fixture_file']
        if sha(path) != entry['sha256'] or path.stat().st_size != entry['bytes']:
            raise ValueError('Exact historical Core test fixture changed.')
    # Only ROOT's parent locator is used later by these retained modules.
    # SOURCES, UTILITY and every PINS entry still identify original Academy
    # assets. The production sha function independently rechecks all63 cited
    # files against the unchanged historical source-evidence manifest.
    with patch.object(module, 'ROOT', FIXTURES / 'core/layout/academy/repo'):
        yield


@contextmanager
def retained_playback_raw(module):
    """Use byte-for-byte original genuine observations outside ignored _reports."""
    entries = [x for x in manifest()['genuine_raw_playback'] if x['lesson_id'] == module.NAME]
    if len(entries) != 1 or entries[0]['sha256'] != module.RAW_SHA:
        raise ValueError('Portable raw playback identity differs from production pin.')
    entry = entries[0]
    path = FIXTURES / entry['fixture_file']
    if sha(path) != module.RAW_SHA or path.stat().st_size != entry['bytes']:
        raise ValueError('Original genuine raw playback bytes changed.')
    with patch.object(module, 'RAW', path):
        yield
