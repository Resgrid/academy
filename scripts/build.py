"""Build the Academy website from the authoring sources retained in this repository."""
import argparse
import subprocess
import sys
from pathlib import Path

from export_site import export
from verify_sources import verify
from sync_course import sync


def build(root, *, local_preview=False):
    root = Path(root).resolve()
    sources = root / 'sources'
    sync(sources)
    result = verify(sources)
    if not result['passed']:
        raise ValueError('Authoring inputs are incomplete: ' + '; '.join(result['issues']))
    for script, arguments in [('deep_dive.py', ['--refresh-pages']), ('library.py', [])]:
        subprocess.run([sys.executable, str(sources / 'production' / script), *arguments], check=True)
    return export(sources, root / 'site', local_preview=local_preview)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--local-preview', action='store_true', help='Build a self-contained local copy without the Pages total-size gate. Deployment must separately package and validate the Release-media site.')
    args = parser.parse_args()
    import json
    print(json.dumps(build(args.root, local_preview=args.local_preview), indent=2))
