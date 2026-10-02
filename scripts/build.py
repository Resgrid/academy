"""Build the Academy website from the authoring sources retained in this repository."""
import argparse
import subprocess
import sys
from pathlib import Path

from export_site import export
from verify_sources import verify
from sync_course import sync


def build(root):
    root = Path(root).resolve()
    sources = root / 'sources'
    sync(sources)
    result = verify(sources)
    if not result['passed']:
        raise ValueError('Authoring inputs are incomplete: ' + '; '.join(result['issues']))
    for script, arguments in [('deep_dive.py', ['--refresh-pages']), ('library.py', [])]:
        subprocess.run([sys.executable, str(sources / 'production' / script), *arguments], check=True)
    return export(sources, root / 'site')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    import json
    print(json.dumps(build(args.root), indent=2))
