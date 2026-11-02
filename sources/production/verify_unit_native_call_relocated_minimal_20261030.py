"""Regression guard for the two omitted frozen Unit native source snapshots.

Default only rehashes the exact immutable public graph. --run copies only that
241-file graph into a temporary relocated repo and runs the unchanged actual
author, proving both missing-file failures, hash-drift rejection and success.
No target repository, app, source package, review or approval is modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASE = Path('sources/expansion/plans/app-unit-call-lifecycle-native-portability-20261030')
ALLOWLIST = BASE / 'exact-dependency-allowlist.json'
ALLOWLIST_SHA = '01a4ada862e78bd1e2cc1adacb9031fa2fe58708f751a6922b8dde27a70efc6c'
AUTHOR = Path('sources/production/author_unit_native_call_lifecycle_take_01_20261030.py')
EXPECTED = {
    'sources/production/native-unit-call-set-active-compatibility-20261029/before/src/app/call/[id].tsx':
        'e6f88c2b1468959840f7fe81b32b2637ee1982f35be4f9aefc5cfd8e4596d605',
    'sources/production/native-unit-call-set-active-compatibility-20261029/after/src/app/call/[id].tsx':
        '30afe9ef7fbb2372b77c69d61c2079a5c60ce55c54c58a703bd021f933bebac1',
}


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encoded(d): return (json.dumps(d, indent=2) + '\n').encode()


def pinned_graph():
    assert __debug__, 'Use ordinary Python; optimized mode disables retained guards.'
    assert sha(ROOT / ALLOWLIST) == ALLOWLIST_SHA, 'Changed reviewed exact allowlist.'
    d = json.loads((ROOT / ALLOWLIST).read_text())
    assert d['allow_prefix_copy'] is False and d['source_package_or_review_receipt_changes_required'] is False
    assert {r['file']: r['sha256'] for r in d['eligible_exact_files']} == EXPECTED
    rows = d['minimal_author_public_files']
    assert len(rows) == 241 and len({r['file'] for r in rows}) == 241
    for r in rows:
        path = Path(r['file'])
        assert not path.is_absolute() and not any(x in {'.', '..', 'private', '.git', 'node_modules'} or x.startswith('.env') for x in path.parts)
        p = ROOT / path
        assert p.resolve().is_relative_to(ROOT) and not p.is_symlink()
        assert p.is_file() and sha(p) == r['sha256'] and p.stat().st_size == r['bytes'], 'Changed/missing immutable public input: ' + r['file']
    return d, rows


def run_author(relocated):
    result = subprocess.run([sys.executable, '-B', str(relocated / AUTHOR)], cwd=relocated,
        env={'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1'}, capture_output=True, text=True)
    assert not (relocated / 'sources/expansion/plans/app-unit-call-lifecycle-native-take-01-final-inputs-20261030').exists()
    return result


def regression(rows):
    cases = []
    with tempfile.TemporaryDirectory(prefix='academy-unit-native-minimal-relocation-') as folder:
        relocated = Path(folder) / 'repo'
        for row in rows:
            target = relocated / row['file']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row['file'], target)
        for name in EXPECTED:
            path = relocated / name
            path.unlink()  # This is the new temporary regression copy only.
            bad = run_author(relocated)
            assert bad.returncode != 0 and 'public source snapshot asset missing/unreadable' in bad.stderr
            cases.append({'case': 'omit_exact_' + ('before' if '/before/' in name else 'after') + '_snapshot',
                'expected_rejection': 'public source snapshot asset missing/unreadable', 'observed': True})
            shutil.copyfile(ROOT / name, path)
        after = relocated / next(x for x in EXPECTED if '/after/' in x)
        after.write_bytes(after.read_bytes() + b'\n')  # Synthetic temporary hash drift only.
        bad = run_author(relocated)
        assert bad.returncode != 0 and 'public source snapshot hash differs' in bad.stderr
        cases.append({'case': 'exact_snapshot_hash_drift', 'expected_rejection': 'public source snapshot hash differs', 'observed': True})
        shutil.copyfile(ROOT / after.relative_to(relocated), after)
        good = run_author(relocated)
        assert good.returncode == 0, good.stderr
        actual = json.loads(good.stdout)
        assert actual['source_recipe_ready'] is True and actual['actual_Root_full_map_review_passed'] is True
        assert actual['actual_cues'] == 88 and actual['source_spans'] == 23
        assert actual['actual_User_hearing_required'] is True and actual['final_inputs_written'] is False
        assert actual['rendered_or_published'] is False
        for row in rows: assert sha(relocated / row['file']) == row['sha256']
        cases.append({'case': 'exact_241_file_graph_in_fresh_relocation', 'passed': True, 'actual_author_result': actual})
    return cases


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', action='store_true')
    p.add_argument('--retain-report', action='store_true')
    args = p.parse_args()
    assert not args.retain_report or args.run, 'A report requires actual relocated execution.'
    graph, rows = pinned_graph()
    cases = regression(rows) if args.run else []
    report = {'kind': 'Actual minimal-copy relocation regression for the omitted native Unit call source snapshots',
        'passed': bool(cases), 'allowlist_sha256': ALLOWLIST_SHA, 'guard_sha256': sha(Path(__file__)),
        'exact_native_dependencies': 224, 'exact_public_author_graph_files': len(rows),
        'public_graph_bytes': sum(r['bytes'] for r in rows), 'cases': cases,
        'target_repository_or_original_source_changed': False, 'native_app_or_profile_or_review_or_approval_changed': False,
        'actual_installed_target_verification': 'Root must run the target author after copying the two exact allowlisted files; relocated success does not substitute for that check.'}
    if args.retain_report:
        output = ROOT / BASE / 'relocated-minimal-regression-report.json'
        body = encoded(report)
        with output.open('xb') as f: f.write(body)
    print(json.dumps({'pinned_public_files': len(rows), 'relocated_cases_run': len(cases), 'passed': bool(cases),
        'exact_snapshot_exceptions': 2, 'target_changed': False}))


if __name__ == '__main__': main()
