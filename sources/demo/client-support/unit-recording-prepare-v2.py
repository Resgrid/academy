#!/usr/bin/env python3
"""Explicitly prepare a fresh pinned v2 Unit recording copy; --plan is read-only."""
import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path
from unit_recording_support_v2 import Layout, SupportError, preparation_plan, prepare


class QuietParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid recording-helper options; use --help. Credentials belong only in the inherited environment.\n')


def main():
    parser = QuietParser(description=__doc__)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--plan', action='store_true')
    args = parser.parse_args()
    layout = Layout()
    try:
        if args.plan:
            print(json.dumps(preparation_plan(layout, args.destination), indent=2))
        else:
            prepare(layout, args.destination)
            print('Prepared verified fresh v2 Unit recording copy; no original/profile pin was changed.')
    except SupportError as error:
        parser.exit(1, str(error) + '\n')
    except OSError:
        parser.exit(1, 'Unit recording filesystem check failed; source/existing copies were preserved. A newly created incomplete destination must not launch.\n')


if __name__ == '__main__':
    main()
