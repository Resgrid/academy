#!/usr/bin/env python3
"""Read only local Metro HTML/JavaScript; never execute a browser or call APIs.

Response bodies and environment values are never printed or persisted. Optional
--write-observation retains only hashes, counts and sanitized compilation errors
in ignored runtime reports. No app authentication, state or database operation.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent.parents[3]
REPORTS = ROOT / '_reports/recording-runtime-recovery-20261030'
CONFIG = {'dispatch': 19101, 'ic': 19104}


def safe_message(text):
    for name, value in os.environ.items():
        if value and len(value) >= 8 and any(word in name.upper() for word in
                ('MAPBOX', 'TOKEN', 'PASSWORD', 'SECRET', 'APP_KEY', 'SENTRY', 'LOGGING_KEY', 'COUNTLY')):
            text = text.replace(value, '[redacted inherited environment value]')
    return text[:1500]


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=50) as response:
            return response.status, response.headers.get('Content-Type', ''), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get('Content-Type', ''), error.read()


def check(alias):
    port = CONFIG[alias]
    base = 'http://localhost:' + str(port)
    result = {'app': alias, 'observed_at': datetime.now(timezone.utc).isoformat(), 'url': base,
              'body_saved_or_printed': False, 'browser_auth_api_or_DB_actions': False, 'passed': False}
    try:
        status, mime, html = get(base + '/')
        result['html'] = {'status': status, 'content_type': mime, 'bytes': len(html), 'sha256': hashlib.sha256(html).hexdigest()}
        if status != 200:
            return result
        scripts = re.findall(rb'<script[^>]+src=["\']([^"\']+)', html)
        bundles = [p.decode().replace('&amp;', '&') for p in scripts if b'expo-router' in p and b'.bundle' in p]
        if len(bundles) != 1:
            result['error'] = 'HTML does not name exactly one Expo Router app bundle.'
            return result
        url = urllib.parse.urljoin(base + '/', bundles[0])
        parsed = urllib.parse.urlparse(url)
        if parsed.hostname not in ('127.0.0.1', 'localhost') or parsed.port != port or not parsed.path.endswith('.bundle'):
            result['error'] = 'App bundle is not served by the expected local app port.'
            return result
        status, mime, body = get(url)
        result['bundle'] = {'status': status, 'content_type': mime, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(),
                            'modules': body.count(b'__d('), 'local_router_bundle': True,
                            'Records_wire_markers_present': all(x in body for x in (b'ClientRecordId', b'Sections', b'Rows', b'Withheld'))}
        result['passed'] = status == 200 and 'javascript' in mime and len(body) > 100000 and body.count(b'__d(') > 100
        if status != 200:
            try:
                detail = json.loads(body)
                result['compilation_error'] = safe_message(str(detail.get('message', detail.get('type', 'Metro compilation error'))))
            except (ValueError, UnicodeError, AttributeError):
                result['compilation_error'] = 'Non-JSON Metro error response (body withheld).'
    except (OSError, urllib.error.URLError) as error:
        result['error'] = safe_message(str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app', choices=CONFIG, required=True)
    parser.add_argument('--write-observation', action='store_true')
    args = parser.parse_args()
    result = check(args.app)
    if args.write_observation:
        REPORTS.mkdir(parents=True, exist_ok=True)
        path = REPORTS / (args.app + '-http-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.json')
        with path.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
