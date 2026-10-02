"""Check a configured Pages domain without changing repository settings."""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit


def normalize_domain(value):
    value = value.strip().lower().rstrip('.')
    if not value or len(value) > 253 or not re.fullmatch(r'[a-z0-9.-]+', value):
        raise ValueError('Enter a domain name only, without a scheme, path, port or wildcard.')
    labels = value.split('.')
    if len(labels) < 2 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in labels):
        raise ValueError('Enter a valid domain name; use Punycode for internationalized names.')
    return value


def check_domain(expected, pages_url):
    if not expected.strip():
        return 'Using the existing GitHub Pages address or configured custom domain.'
    domain = normalize_domain(expected)
    current = urlsplit(pages_url)
    if current.scheme not in ('https', 'http') or current.username or current.password or current.port or (current.hostname or '').lower() != domain:
        raise ValueError('The expected domain is not the configured Pages address. Save it in Settings > Pages > Custom domain, then rerun deployment.')
    return 'The configured custom domain matches the expected domain.'


def configured_domain(override, config_path):
    if override.strip():
        return normalize_domain(override)
    config = json.loads(Path(config_path).read_text())
    return normalize_domain(config['custom_domain'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).resolve().parents[1] / 'pages.json')
    args = parser.parse_args()
    try:
        print(check_domain(configured_domain(os.environ.get('ACADEMY_CUSTOM_DOMAIN', ''), args.config), os.environ.get('ACADEMY_PAGES_URL', '')))
    except ValueError as error:
        raise SystemExit(str(error))

