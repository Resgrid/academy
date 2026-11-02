"""Read-only check of the frozen, personally reviewed Calls Summary source.

Changed scripts/images require a new version and real review; this checker never
creates approvals, hearing receipts, renderer plans or publication evidence.
"""
from pathlib import Path
import hashlib
import json
import sys

S = Path(__file__).resolve().parents[1]
R = S.parent
sys.path.insert(0, str(R / 'scripts'))
from verify_capture_evidence import _Validator

FOLDER = S / 'expansion/plans/app-bigboard-call-summary-display-source-proposal-20261102'
PINS = {'lesson.candidate.json': '356849f353bd1829def2f36ec65fe8032e058a42450febf6390ce67f02fb6113',
        'captures.reviewed.json': '1b7d0a05ccfdaf5c93d28653bf2bd91364f2b603ebe77686b849b08231bc2838'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    for name, expected in PINS.items():
        if sha(FOLDER / name) != expected:
            raise ValueError('Changed frozen source: ' + name)
    lesson = json.loads((FOLDER / 'lesson.candidate.json').read_text())
    manifest = json.loads((FOLDER / 'captures.reviewed.json').read_text())
    review = json.loads((FOLDER / 'source-review.json').read_text())
    if review['source_sha256'] != PINS['lesson.candidate.json'] or review['capture_manifest_sha256'] != PINS['captures.reviewed.json']:
        raise ValueError('Source review does not bind these inputs.')
    if sha(FOLDER / 'narration.txt') != review['narration_sha256']:
        raise ValueError('Narration text changed.')
    if (FOLDER / 'narration.txt').read_text() != '\n\n'.join(x['narration'] for x in lesson['scenes']) + '\n':
        raise ValueError('Narration differs from the complete source script.')
    validator = _Validator(S)
    observed = {}
    for shot in manifest['screenshots']:
        validator.application(shot, shot['id'], {})
        validator.asset(shot, shot['id'], image=True)
        validator.accepted_image(shot, shot['id'])
        observed[shot['id']] = validator.observations(shot, shot['id'])
        if sha(S / shot['dom_file']) != shot['dom_sha256']:
            raise ValueError('Original DOM sidecar changed.')
    for scene in lesson['scenes']:
        available = set().union(*(observed[ident] for ident in scene['capture_refs']))
        if not {label.casefold() for label in scene['required_labels']} <= available:
            raise ValueError('An authored UI control is not in the reviewed source images.')
    if validator.issues:
        raise ValueError('; '.join(validator.issues))
    print(json.dumps({'passed': True, 'scenes': len(lesson['scenes']), 'reviewed_source_images': len(observed),
                      'publication_approved': False, 'final_media_review_inferred': False}))


if __name__ == '__main__':
    main()
