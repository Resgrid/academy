"""Technical QA only for genuine-anchor Pending-call caption parts.

Default checks immutable inputs. --write-qa writes NEW derivative captions and
full decoded-audio/cue QA; it never creates a renderer plan, listener approval,
canonical/readiness/site content, publication or a changed audio file.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / 'sources'
NAME = 'app-dispatch-pending-call-to-dispatch'
BASE = SOURCES / 'expansion/plans/app-dispatch-pending-call-to-dispatch-take-01-source-correspondence-20261028'
HELPER = SOURCES / 'production/author_dispatch_pending_call_take_01.py'
PINS = {
    HELPER: 'e95e1fee699074fc137c2d81c3761926a3cc69696a64a30f45a0a4cc7c83cd3c',
    BASE / 'scaffold.json': 'f1c3867bdd594931dfb8dd9ae6c4cefd2d3f23884ef67e91c7e1c2982ac8786d',
    SOURCES / 'expansion/audio' / (NAME + '.m4a'): 'ce23775d1bc4c9e249b508179830639abd1530c656e175e6b05a48fe7cd9dfcb',
    SOURCES / 'expansion/audio' / (NAME + '.actual.qa.json'): 'c37cd2381f61a260f390cc3c846cb86c64a7fd901827997952df4a57415e6e99',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def stamp(value):
    # Preserve service millisecond bounds, including exact integer-second cuts.
    ms = round(value * 1000)
    hours, ms = divmod(ms, 3600000); minutes, ms = divmod(ms, 60000); seconds, ms = divmod(ms, 1000)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}'


def prepare():
    for path, digest in PINS.items(): need(sha(path) == digest, 'Changed held input: ' + path.name)
    spec = importlib.util.spec_from_file_location('pending_held_author', HELPER)
    author = importlib.util.module_from_spec(spec); spec.loader.exec_module(author)
    scaffold = author.prepare()
    parts = [c for span in scaffold['source_spans'] for c in span['cue_correspondence']]
    need(len(parts) == 71 and [c['candidate_cue'] for c in parts] == list(range(1, 72)), 'Candidate correspondence differs.')
    blocks = []
    for number, cue in enumerate(parts, 1):
        wrapped = textwrap.wrap(cue['text'], width=42, break_on_hyphens=False, break_long_words=False)
        if len(wrapped) > 2: wrapped = textwrap.wrap(cue['text'], width=48, break_on_hyphens=False, break_long_words=False)
        need(len(wrapped) <= 2, 'Actual caption needs separate layout review, never guessed cuts.')
        blocks.append(f'{number}\n{stamp(cue["start"])} --> {stamp(cue["end"])}\n' + '\n'.join(wrapped))
    raw69 = json.loads((SOURCES / 'expansion/audio' / (NAME + '.actual.qa.json')).read_text())
    need(raw69['passed'] is True and not raw69['issues'] and raw69['silent_raw_cues'] == raw69['silent_corrected_cues'] == 0 and raw69['raw_captions']['cues'] == 69, 'Original full actual69cue QA is not passed.')
    need(raw69['audio']['sha256'] == PINS[SOURCES / 'expansion/audio' / (NAME + '.m4a')] and raw69['audio']['full_decode'] == 'passed' and raw69['audio']['decoded_samples'] == 11251462, 'Actual raw audio QA identity changed.')
    return author, scaffold, raw69, '\n\n'.join(blocks) + '\n\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-qa', action='store_true')
    parser.add_argument('--ffmpeg', type=Path)
    args = parser.parse_args(); author, scaffold, raw69, text = prepare()
    if args.write_qa:
        need(args.ffmpeg is not None, 'Provide the approved FFmpeg binary for full actual decode.')
        derived = BASE / (NAME + '.derived71.srt')
        corrected = BASE / (NAME + '.derived71.corrected.srt')
        report = BASE / (NAME + '.derived71.actual.qa.json')
        provenance = BASE / (NAME + '.derived71.provenance.json')
        need(not any(p.exists() for p in [derived, corrected, report, provenance]), 'Use NEW derivative paths; preserve all prior QA/captions.')
        with derived.open('x') as stream: stream.write(text)
        sys.path.insert(0, str(ROOT / 'scripts'))
        from qa_narration import audit
        from render_walkthrough import load_cues
        lesson = author.asset(str(author.BASE / (NAME + '.narrated-source.json')))
        audio = SOURCES / 'expansion/audio' / (NAME + '.m4a')
        result = audit(lesson, audio, derived, corrected, report, str(args.ffmpeg), scaffold['frozen_lesson_sha256'])
        need(result['passed'] and len(load_cues(corrected)) == 71 and not result['alignment']['text_changes'], 'Derived actual audio/caption QA failed; preserve results and do not approve rendering.')
        need(result['audio']['decoded_samples'] == 11251462 and result['audio']['duration_seconds'] == raw69['audio']['duration_seconds'], 'Actual decoded audio identity differs from original QA.')
        doc = {'kind': 'actual_audio_genuine_anchor_caption_qa_only', 'lesson_id': NAME,
               'source_pins': [{'file': str(p.relative_to(SOURCES)), 'sha256': digest} for p, digest in PINS.items()],
               'frozen_lesson_sha256': scaffold['frozen_lesson_sha256'], 'raw69_preserved': True,
               'actual_service_anchor_splits': scaffold['genuine_anchor_splits'], 'word_precision_seconds': 1,
               'interpolated': False, 'exact_words': 598, 'derived_cues': 71,
               'derived': {'file': str(derived.relative_to(SOURCES)), 'sha256': sha(derived)},
               'corrected': {'file': str(corrected.relative_to(SOURCES)), 'sha256': sha(corrected)},
               'actual_qa': {'file': str(report.relative_to(SOURCES)), 'sha256': sha(report)},
               'full_decode': 'passed', 'silent_raw_cues': result['silent_raw_cues'], 'silent_corrected_cues': result['silent_corrected_cues'],
               'minimum_raw_cue_rms': result['minimum_raw_cue_rms'],
               'decoded_audio_end_and_final_source_hold_seconds': result['audio']['duration_seconds'],
               'last_speech_end_seconds': 234.23, 'all_required_inputs_approved': False,
               'listening_approval': 'pending actual complete lesson-specific user review',
               'renderer_plan_created': False, 'rendered_video_created': False, 'publication_approved': False,
               'limitations': ['Full decode and per-cue energy are technical checks, not speech recognition or subjective listening.', 'Raw69SRT, original raw69QA, actual audio and frozen598words remain unchanged.']}
        provenance.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'passed': True, 'derived_cues': 71, 'minimum_raw_cue_rms': result['minimum_raw_cue_rms'], 'silent_cues': result['silent_raw_cues'], 'actual_duration_seconds': result['audio']['duration_seconds'], 'listening_approved': False, 'renderer_plan_created': False}, indent=2))
    else:
        print(json.dumps({'source_audio_preflight': 'passed', 'candidate_cues': 71, 'actual_audio_seconds': raw69['audio']['duration_seconds'], 'files_written': False, 'listening_approved': False, 'renderer_plan_created': False}, indent=2))


if __name__ == '__main__':
    main()
