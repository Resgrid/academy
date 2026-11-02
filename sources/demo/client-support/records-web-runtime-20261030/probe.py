"""Measure actual local HTML and JS bundle delivery; never save response bodies.

Only the fixed Responder/Unit recording ports are requested. This performs no
browser execution, sign-in, app API, database, location or provider operation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
PORTS = {'responder': 19102, 'unit-records': 19103}
PATTERN = re.compile(r'\b(?:pk|sk)\.[A-Za-z0-9_.-]{12,}')


class Scripts(HTMLParser):
    def __init__(self): super().__init__(); self.sources = []
    def handle_starttag(self, tag, attrs):
        if tag == 'script' and dict(attrs).get('src'): self.sources.append(dict(attrs)['src'])


class LocalOnly(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urllib.parse.urlsplit(req.full_url), urllib.parse.urlsplit(newurl)
        if new.hostname not in {'localhost', '127.0.0.1', '::1'} or new.port != old.port:
            raise ValueError('Unexpected non-recording redirect refused.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe(app):
    port = PORTS[app]
    base = 'http://localhost:' + str(port) + '/'
    result = {'app': app, 'url': base, 'observed_at': datetime.now(timezone.utc).isoformat(),
        'response_body_saved': False, 'browser_or_sign_in_or_app_data_actions': False, 'passed': False}
    client = urllib.request.build_opener(LocalOnly())
    try:
        with client.open(base, timeout=30) as r:
            body = r.read(512 * 1024 + 1)
            assert r.status == 200 and len(body) <= 512 * 1024
            result['html'] = {'status': r.status, 'content_type': r.headers.get('Content-Type', ''),
                'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}
        scripts = Scripts(); scripts.feed(body.decode('utf-8'))
        urls = [urllib.parse.urljoin(base, s) for s in scripts.sources]
        bundles = [u for u in urls if urllib.parse.urlsplit(u).path.endswith('.bundle')]
        assert bundles, 'No actual bundle resource in returned HTML.'
        measurements = []
        for url in bundles:
            parsed = urllib.parse.urlsplit(url)
            assert parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1', '::1'} and parsed.port == port
            assert not parsed.username and not parsed.password and not re.search(r'(?i)(token|password|api_key|secret)=', parsed.query)
            with client.open(url, timeout=60) as response:
                digest = hashlib.sha256(); size = 0
                for chunk in iter(lambda: response.read(1024 * 1024), b''):
                    digest.update(chunk); size += len(chunk)
                kind = response.headers.get('Content-Type', '')
                assert response.status == 200 and size > 100000 and ('javascript' in kind or 'ecmascript' in kind)
                measurements.append({'resource_path': parsed.path, 'status': response.status,
                    'content_type': kind, 'bytes': size, 'sha256': digest.hexdigest(),
                    'method': 'Complete actual served response streamed to hash only; not browser execution proof.'})
        result.update(bundles=measurements, passed=True)
    except urllib.error.HTTPError as e:
        # Only bounded sanitized error text is retained; no successful JS body.
        text = e.read(65536).decode('utf-8', errors='replace')
        try: message = json.loads(text).get('message', '')
        except (ValueError, AttributeError): message = 'Non-JSON HTTP failure; body not retained.'
        result.update(http_error=e.code, diagnostic=PATTERN.sub('[redacted-client-value]', message)[:2600])
    except Exception as e:
        result.update(error=type(e).__name__, diagnostic=PATTERN.sub('[redacted-client-value]', str(e))[:1000])
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', choices=[*PORTS, 'both'], default='both')
    p.add_argument('--retain-report', action='store_true')
    a = p.parse_args(); apps = list(PORTS) if a.app == 'both' else [a.app]
    with ThreadPoolExecutor(max_workers=len(apps)) as pool: rows = list(pool.map(probe, apps))
    report = {'passed': all(r['passed'] for r in rows), 'observations': rows,
        'browser_display_or_authenticated_api_or_saved_record_verified': False}
    if a.retain_report:
        folder = ROOT / '_reports/recording-runtime-recovery-20261030'
        folder.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        path = folder / ('http-bundle-probe-' + stamp + '.json')
        with path.open('x') as f: f.write(json.dumps(report, indent=2) + '\n')
        report['report_file'] = str(path)
    print(json.dumps(report))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__': main()
