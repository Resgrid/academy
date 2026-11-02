#!/usr/bin/env python3
"""Omit a missing Android-only provider-file reference in the owned iOS recorder.
No private provider file is copied; original source and all iOS/UI/auth settings stay.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path('/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025')
TARGET = ROOT / 'native-unit-20261028/source/app.config.ts'
PATCH = Path(__file__).with_name('unit-ios-recording-config.patch')
BEFORE = '855d5eebad86036ce3383edecb7505367f241a219590ac125980271470775695'
PATCH_HASH = '5237a7d0cf4a8f1e3be3bc8c748184ecc02c4e9d356409a76899a90174a6f8b4'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if TARGET.is_symlink() or sha(TARGET) != BEFORE or sha(PATCH) != PATCH_HASH:
        raise ValueError('Recording-only config input changed; original is not touched')
    source = ROOT / 'repo/sources/demo/client-support/unit_recording_support_v2.py'
    spec = importlib.util.spec_from_file_location('exact_native_patch', source)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    sections = module.patch_sections(PATCH.read_text())
    if len(sections) != 1 or sections[0][:2] != ('app.config.ts', False): raise ValueError('Unexpected native config patch scope')
    original = TARGET.read_text(); result = module.exact_patch(original, sections[0][2])
    if result != original.replace("    googleServicesFile: 'google-services.json',\n", ''): raise ValueError('Unreviewed config change')
    TARGET.write_text(result)
    report = {'kind': 'isolated_ios_recording_configuration_override', 'at': datetime.now(timezone.utc).isoformat(), 'before_sha256': BEFORE,
              'after_sha256': sha(TARGET), 'patch_sha256': PATCH_HASH, 'change': 'Omit only Android googleServicesFile path, which references an ignored private file unavailable in clean iOS recorder.',
              'original_modified': False, 'ios_ui_or_auth_modified': False, 'private_provider_config_copied': False, 'android_behavior_tested': False}
    p = ROOT / 'native-unit-20261028/ios-recording-config-override.json'; p.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
