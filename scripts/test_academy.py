"""Run current guards and byte-pinned historical authoring regressions separately.

Old recipes intentionally refuse changed tooling. Their regression tests use a
separate copy with the exact retained validator; current tests use today's gate.
No production inputs, expected hashes or review receipts are changed.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from media_delivery import sha_file

ROOT = Path(__file__).resolve().parents[1]
LEGACY_SHA = '40f41d12497d273feb950d5db1a04a6880466b229ee2d6756a929f87f70c04fa'
FIXTURE = Path('sources/production/tests/fixtures/review-tools-20261030/verify_capture_evidence.py.txt')
RENDERER = Path('sources/production/tests/fixtures/review-tools-20261030/render_walkthrough.py.txt')
RENDERER_SHA = '89f19e92b3005c0e0be9fb5b1babc4e5d780f1529d31ca278eb14c3ca1abc881'
PUBLISHER = Path('sources/production/tests/fixtures/review-tools-20261030/expansion_site.py.txt')
PUBLISHER_SHA = 'b2dd8f71fa5350e5b02f45bd3f0f8fbe7b16d511ccb908efd9ab11cbcaead0f8'
LEGACY = {
    'scripts/tests': {'test_app_reference_qualification_guards_20261030', 'test_app_reference_v2_authoring',
                      'test_records_definition_authoring_guards_20261030', 'test_records_lifecycle_final_authoring'},
    'sources/production/tests': {'test_core_administration_qualification_guards_20261030',
                                'test_core_billing_shifts_take_02_authoring_guards',
                                'test_core_billing_shifts_take_02_authoring_guards_v2',
                                'test_reporting_release_guards', 'test_workforce_release_guards'},
}


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main():
    if (sha_file(ROOT / FIXTURE) != LEGACY_SHA or sha_file(ROOT / RENDERER) != RENDERER_SHA
            or sha_file(ROOT / PUBLISHER) != PUBLISHER_SHA):
        raise ValueError('Retained historical validator bytes changed.')
    for folder, old_modules in LEGACY.items():
        suite = unittest.defaultTestLoader.discover(str(ROOT / folder), top_level_dir=str(ROOT / folder))
        current = unittest.TestSuite(case for case in cases(suite) if case.id().split('.')[0] not in old_modules)
        result = unittest.TextTestRunner(verbosity=2).run(current)
        if not result.wasSuccessful():
            return 1
    with tempfile.TemporaryDirectory(prefix='academy-historical-regressions-') as directory:
        root = Path(directory)
        ignored = shutil.ignore_patterns('private', '__pycache__', 'build', 'checkout', 'checkout-expansion',
                                         'capture-apps', 'node_modules', '.git', '.venv', 'publish', 'logs')
        for folder in ('scripts', 'sources'):
            shutil.copytree(ROOT / folder, root / folder, ignore=ignored, symlinks=True)
        shutil.copyfile(ROOT / FIXTURE, root / 'scripts/verify_capture_evidence.py')
        shutil.copyfile(ROOT / RENDERER, root / 'scripts/render_walkthrough.py')
        shutil.copyfile(ROOT / PUBLISHER, root / 'scripts/expansion_site.py')
        if sha_file(root / 'scripts/verify_capture_evidence.py') != LEGACY_SHA:
            raise ValueError('Historical regression workspace did not retain the required validator.')
        for folder, modules in LEGACY.items():
            for module in sorted(modules):
                print('Historical exact-tool regression:', module, flush=True)
                subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', folder,
                                '-p', module + '.py', '-v'], cwd=root, check=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
