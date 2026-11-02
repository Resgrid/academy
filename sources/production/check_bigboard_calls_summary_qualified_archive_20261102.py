"""Read-only portable verification of the finished Calls Summary lesson archive."""
from pathlib import Path
import hashlib
import json
import sys

sys.dont_write_bytecode = True
S = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(S.parent / 'scripts'))
from expansion_site import _prepare
from verify_capture_evidence import verify_document

NAME = 'app-bigboard-call-summary-display'
MASTER = '47ba2bfe2cde50266f5450f0fa3275c734e4c00e914bfdd457e83902bf57929c'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text())


def main():
    take = S / 'expansion/rendered' / (NAME + '-take-01')
    canonical = read(S / 'expansion/lessons' / (NAME + '.json'))
    evidence = read(take / 'evidence.reviewed.json')
    hearing = read(S / 'expansion/audio' / (NAME + '.listening-review.json'))
    audio_qa = read(take / 'encoded-audio.qa.json')
    if sha(take / (NAME + '.mp4')) != MASTER or evidence['video']['sha256'] != MASTER:
        raise ValueError('Changed qualified video master.')
    if not hearing['complete_natural_narration'] or hearing['reviewer'] != 'User':
        raise ValueError('Genuine complete User hearing review is missing.')
    if hearing['audio_sha256'] != sha(S / 'expansion/audio' / (NAME + '.m4a')):
        raise ValueError('Hearing review binds different audio.')
    if not audio_qa['passed'] or audio_qa['audio']['sha256'] != MASTER or audio_qa['corrected_captions']['cues'] != 63:
        raise ValueError('Encoded audio QA does not bind this master.')
    report = verify_document(evidence, S)
    if not report['passed']:
        raise ValueError('; '.join(report['issues']))
    _prepare(canonical, S)
    print(json.dumps({'passed': True, 'lesson': NAME, 'master_sha256': MASTER,
                      'screen_intervals': len(evidence['rendered_segments']), 'caption_cues': 63,
                      'playback_positions': [row['position'] for row in evidence['browser_playback']],
                      'approvals_created': False, 'files_modified': 0}))


if __name__ == '__main__':
    main()
