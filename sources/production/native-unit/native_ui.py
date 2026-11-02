#!/usr/bin/env python3
"""Normal XCTest UI inbox client for the one dedicated Academy simulator only.

No Unit app store/container/API access. Only the independently installed XCTest
runner's Documents inbox is used. Screenshot reads simctl raw pixels after two
current credential/foreground guards. Credentials use a transient 0600 runner
file, never argv, command receipts, screenshot, print output or public source.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

BASE = Path('/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025/native-unit-20261028')
SOURCE_ROOT = BASE.parent / 'repo/sources'
RAW = SOURCE_ROOT / 'captures/expansion/unit-native-20261028'
RUNNER_BUNDLE = 'com.resgrid.academy.UnitUITests.xctrunner'
ACTIONS = {'inspect', 'tap', 'scroll', 'landscape', 'signin', 'configure_local_training_server', 'deny_own_location_permission', 'open_local_project_confirmation', 'show_inventory_complete_confirmation', 'confirm_matching_inventory_alert', 'dismiss_inventory_confirmation', 'capture_guard', 'stop'}


def actual_session():
    data = json.loads((BASE / 'session.json').read_text())
    if data.get('dedicated') is not True or data.get('user_session_reused') is not False or data.get('owner') != 'academy_training':
        raise ValueError('Not our dedicated simulator session')
    device = str(uuid.UUID(data['udid']))
    if device.lower() != data['udid'].lower(): raise ValueError('Missing exact dedicated simulator UUID')
    before = json.loads((BASE / 'devices-before.private.json').read_text())
    previous = {row['udid'].lower() for rows in before['devices'].values() for row in rows}
    if device.lower() in previous or data.get('name') != 'Academy Training Unit iPad 20261028':
        raise ValueError('Dedicated session would reuse a pre-existing simulator')
    return data


def runner_directory(session):
    command = ['xcrun', 'simctl', 'get_app_container', session['udid'], RUNNER_BUNDLE, 'data']
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode: raise ValueError('Own XCTest runner is not installed/running; no other container is accessed')
    root = Path(result.stdout.strip()).resolve()
    if session['udid'].lower() not in str(root).lower() or '/Containers/Data/Application/' not in str(root):
        raise ValueError('Runner data path is outside the dedicated simulator')
    path = root / 'Documents/AcademyDriver'
    ready = json.loads((path / 'ready.json').read_text())
    if ready.get('simulator_udid') != session['udid'] or ready.get('normal_ui_only') is not True: raise ValueError('Runner session binding failed')
    return path


def send(action, parameters=None):
    if action not in ACTIONS: raise ValueError('Unsupported normal UI action')
    session = actual_session(); directory = runner_directory(session)
    name = str(uuid.uuid4()); request = {'id': name, 'action': action, **(parameters or {})}
    path = directory / 'request.json'
    if path.exists(): raise ValueError('Previous ordinary UI request still pending')
    if action == 'signin':
        value = json.loads((SOURCE_ROOT / 'demo/private/credentials.json').read_text())['demo_password']
        private = directory / 'credentials.private.json'
        fd = os.open(private, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream: json.dump({'username': 'boden', 'password': value}, stream)
    temporary = directory / (name + '.tmp')
    temporary.write_text(json.dumps(request)); temporary.rename(path)
    result_path = directory / ('response-' + name + '.json')
    # Full native accessibility enumeration can exceed forty seconds on the
    # large iPad Settings screen. The host still yields while this process runs;
    # no subsequent UI command is dispatched before the observation completes.
    deadline = time.monotonic() + (120 if action == 'inspect' else 40)
    while not result_path.is_file() and time.monotonic() < deadline: time.sleep(0.1)
    if not result_path.is_file(): raise ValueError('Normal XCTest UI command timed out; no alternative app/state path attempted')
    result = json.loads(result_path.read_text())
    receipts = BASE / 'ui-receipts'; receipts.mkdir(exist_ok=True)
    (receipts / (name + '.json')).write_text(json.dumps({'request': request, 'response': result}, ensure_ascii=False, indent=2) + '\n')
    if not result.get('ok'): raise ValueError('Ordinary UI guard/action failed: ' + str(result.get('error', 'unknown')))
    return result


def capture(name):
    if not re.fullmatch(r'\d{3}-[a-z0-9-]+', name): raise ValueError('Use a new numbered native screenshot name')
    guard = send('capture_guard')
    if guard['result'].get('capture_allowed') is not True: raise ValueError('Credentials/foreground block capture')
    observation = send('inspect'); session = actual_session()
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / (name + '.png')
    if path.exists(): raise ValueError('Preserve original native image; choose a fresh name')
    guard2 = send('capture_guard')
    if guard2['result'].get('capture_allowed') is not True: raise ValueError('Current native capture privacy guard failed')
    command = ['xcrun', 'simctl', 'io', session['udid'], 'screenshot', '--type=png', str(path)]
    start = datetime.now(timezone.utc).isoformat(); result = subprocess.run(command, capture_output=True)
    end = datetime.now(timezone.utc).isoformat()
    if result.returncode: raise ValueError('Actual dedicated simulator screenshot failed')
    from PIL import Image
    with Image.open(path) as im: width, height = im.size
    record = {'kind': 'raw_native_source_capture_pending_review', 'app': 'Unit', 'file': str(path.relative_to(SOURCE_ROOT)),
              'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'width': width, 'height': height,
              'provenance': {'method': 'ios_simulator_screenshot', 'started_at': start, 'captured_at': end, 'command': command,
                             'exit_code': result.returncode, 'simulator_udid': session['udid'], 'runtime': session['runtime'],
                             'bundle_id': 'com.resgrid.unit.development'},
              'native_accessibility_observation': observation, 'observation_is_dom': False, 'visible_labels': [],
              'pixel_review': 'pending actual image inspection', 'publication_approved': False, 'source_only': True}
    (RAW / (name + '.native.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    return {key: record[key] for key in ('kind', 'file', 'sha256', 'width', 'height', 'source_only')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=sorted(ACTIONS | {'capture'}))
    parser.add_argument('--label'); parser.add_argument('--element-type'); parser.add_argument('--direction'); parser.add_argument('--name')
    parser.add_argument('--username-label'); parser.add_argument('--password-label'); parser.add_argument('--submit-label')
    args = parser.parse_args()
    if args.action == 'capture': result = capture(args.name or '')
    else:
        parameters = {key.replace('_', '-').replace('-', '_'): value for key, value in vars(args).items() if key not in ('action', 'name') and value is not None}
        result = send(args.action, parameters)
        if args.action == 'inspect':
            result = {**result, 'result': {**result['result'], 'elements': [
                {key: item[key] for key in ('type', 'label', 'identifier', 'placeholder') if key in item}
                for item in result['result']['elements'][:160]
            ]}}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
