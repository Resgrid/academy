"""Extract record-definition take01 actual frames with retained numerical checks.

The unchanged generic checker performs full-source and every-caption pixel
comparisons. This wrapper supplies only the reviewed Records inputs and scope.
No visual approval, hearing, browser proof or publication is manufactured.
"""
import hashlib
import importlib.util
from pathlib import Path
import sys

sys.dont_write_bytecode = True
PRODUCTION = Path(__file__).resolve().parent
RETAINED = PRODUCTION / 'review_core_administration_final_frames_20261030.py'
RETAINED_SHA = '3adce14ebbedf3d6b95945f81fe2f07b87bee939b81624bcfa180272e68e99fc'


def main():
    if hashlib.sha256(RETAINED.read_bytes()).hexdigest() != RETAINED_SHA:
        raise ValueError('Changed retained numerical checker; preserve exact review code.')
    spec = importlib.util.spec_from_file_location('retained_records_frame_checker', RETAINED)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CONFIG = {
        'records': ('core-records-administration', 'core-records-administration-take-01',
            'expansion/plans/core-records-administration-capture-freeze-20261030/core-records-administration.narrated-source.json',
            'expansion/plans/core-records-administration-take-01-final-inputs-20261030/plan.json', 135),
    }
    module.main()


if __name__ == '__main__':
    main()
