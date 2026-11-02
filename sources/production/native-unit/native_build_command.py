#!/usr/bin/env python3
"""Run an explicit local build command; scrub output, never expose an env/secret.

Owns only the dedicated native artifact tree. No implicit install, server kill,
app launch, simulator selection or user-data operation. Use after source guard.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path('/Users/shawn/Documents/dev/Core/artifacts/academy-expansion-20261025/native-unit-20261028')
SOURCE = ROOT / 'source'
CREDENTIALS = ROOT.parent / 'repo/sources/demo/private/credentials.json'


def known_values():
    values = set()
    def read(value):
        if isinstance(value, dict):
            for x in value.values(): read(x)
        elif isinstance(value, list):
            for x in value: read(x)
        elif isinstance(value, str) and len(value) >= 8: values.add(value)
    read(json.loads(CREDENTIALS.read_text()))
    for name, value in os.environ.items():
        if value and any(x in name.lower() for x in ('password', 'secret', 'token', 'mapbox_pubkey')):
            values.add(value)
    values.add('boden')
    return sorted(values, key=len, reverse=True)


def scrub(text, values):
    for value in values: text = text.replace(value, '[REDACTED]')
    text = re.sub(r'\b(?:pk|sk)\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b', '[REDACTED]', text)
    text = re.sub(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', '[REDACTED]', text)
    return text


def reject_sensitive_arguments(command, values):
    if any(value in argument for argument in command for value in values if value):
        raise ValueError('Sensitive values must not enter command arguments or receipts')


def main():
    name, separator, *command = sys.argv[1:]
    if separator != '--' or not re.fullmatch(r'[a-z0-9-]+', name) or not command:
        raise ValueError('Use a scoped name -- explicit command')
    if not SOURCE.is_dir(): raise ValueError('Verified native source is absent')
    env = dict(os.environ)
    if not env.get('UNIT_MAPBOX_PUBKEY', '').startswith('pk.'):
        raise ValueError('Inherited Unit map configuration is unavailable; no value was printed')
    env.update({'APP_ENV': 'development', 'EXPO_NO_DOTENV': '1', 'EXPO_NO_TELEMETRY': '1', 'EXPO_OFFLINE': '1', 'CI': '1',
                'UNIT_BASE_API_URL': 'http://127.0.0.1:18967', 'UNIT_API_VERSION': 'v4', 'UNIT_RESGRID_API_URL': '/api/v4',
                'UNIT_CHANNEL_API_URL': 'http://127.0.0.1:18967/', 'SENTRY_DISABLE_AUTO_UPLOAD': 'true', 'SENTRY_ALLOW_FAILURE': 'true',
                'RCT_NO_LAUNCH_PACKAGER': '1', 'COCOAPODS_DISABLE_STATS': 'true'})
    env.update({'UNIT_' + key: '' for key in ('COUNTLY_APP_KEY', 'COUNTLY_URL', 'COUNTLY_SERVER_URL', 'SENTRY_DSN', 'LOGGING_KEY')})
    values = known_values()
    reject_sensitive_arguments(command, values)
    (ROOT / 'logs').mkdir(exist_ok=True)
    path = ROOT / 'logs' / (name + '.log')
    if path.exists(): raise ValueError('Preserve the previous log; choose a new command name')
    started = datetime.now(timezone.utc).isoformat()
    process = subprocess.Popen(command, cwd=SOURCE, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    with path.open('w') as stream:
        for line in process.stdout:
            stream.write(scrub(line, values)); stream.flush()
    code = process.wait()
    report = {'name': name, 'command': command, 'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'exit_code': code, 'log': str(path), 'log_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'local_api_only': True, 'credentials_or_map_values_logged': False}
    (ROOT / 'logs' / (name + '.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if code:
        print('Sanitized diagnostic tail:')
        print(''.join(path.read_text().splitlines(keepends=True)[-18:]))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
