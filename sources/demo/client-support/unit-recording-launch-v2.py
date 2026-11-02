#!/usr/bin/env python3
"""Explicitly launch a verified v2 Unit recording copy; --plan needs no credentials."""
import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from unit_recording_support_v2 import Layout, SupportError, launch_plan, launch


class QuietParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid recording-helper options; use --help. Credentials belong only in the inherited environment.\n')


def main():
    parser = QuietParser(description=__doc__)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--port', type=int, default=19103)
    parser.add_argument('--api-origin', default='http://127.0.0.1:18967')
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    try:
        if args.plan:
            print(json.dumps(launch_plan(Layout(), args.destination, args.port, args.api_origin), indent=2))
        else:
            raise SystemExit(launch(Layout(), args.destination, args.port, args.api_origin))
    except SupportError as error:
        parser.exit(1, str(error) + '\n')
    except OSError:
        parser.exit(1, 'Unit recording launch filesystem/process check failed; no existing server was stopped.\n')


if __name__ == '__main__':
    main()
