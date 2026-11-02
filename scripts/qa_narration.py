#!/usr/bin/env python3
"""Decode complete narration, align exact-script captions and measure every cue.

Signal energy can detect silent/unfinished exports; it cannot establish spoken-word
accuracy or replace listening. Raw media/transcripts and frozen lessons stay intact.
"""
import argparse
import array
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile
import wave

from render_walkthrough import audio_duration

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('academy_caption_alignment', ROOT / 'sources/production/descript/align_captions.py')
alignment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cue_energy(samples, rate, cues, duration, threshold):
    measured, issues = [], []
    previous = 0
    for index, cue in enumerate(cues, 1):
        start, end = alignment.seconds(cue['start']), alignment.seconds(cue['end'])
        if not (0 <= start < end <= duration + .002 and start >= previous - .002):
            issues.append('Invalid, overlapping or out-of-bounds cue ' + str(index))
        previous = end
        clip = samples[max(0, int(start * rate)):min(len(samples), int(end * rate))]
        rms = math.sqrt(sum(value * value for value in clip) / len(clip)) / 32768 if clip else 0
        peak = max((abs(value) for value in clip), default=0) / 32768
        measured.append({'cue': index, 'start': start, 'end': end, 'samples': len(clip),
                         'rms': round(rms, 9), 'peak': round(peak, 9), 'below_threshold': rms < threshold})
        if rms < threshold:
            issues.append('Silent/low-energy speech cue ' + str(index))
    return measured, issues


def audit(lesson_path, audio, raw, corrected, report_path, ffmpeg, expected_sha=None, threshold=.001):
    lesson_path, audio, raw, corrected, report_path = map(lambda p: Path(p).resolve(), (lesson_path, audio, raw, corrected, report_path))
    if corrected in {lesson_path, audio, raw} or report_path in {lesson_path, audio, raw, corrected}:
        raise ValueError('QA outputs must be separate from frozen inputs and each other.')
    fingerprints = {str(path): sha(path) for path in (lesson_path, audio, raw)}
    lesson = json.loads(lesson_path.read_text())
    if expected_sha and fingerprints[str(lesson_path)] != expected_sha:
        raise ValueError('Frozen lesson SHA256 differs from the expected script.')
    brief = {'lesson': lesson['id'], 'scenes': lesson['scenes']}
    reference = ' '.join(scene['narration'] for scene in lesson['scenes']).split()
    with tempfile.TemporaryDirectory(prefix='academy-narration-qa-') as directory:
        pcm = Path(directory) / 'decoded.wav'
        duration = audio_duration(ffmpeg, audio, pcm)
        with wave.open(str(pcm), 'rb') as stream:
            rate = stream.getframerate()
            if stream.getnchannels() != 1 or stream.getsampwidth() != 2:
                raise ValueError('Expected mono 16-bit PCM from full decode.')
            samples = array.array('h', stream.readframes(stream.getnframes()))
        if sys.byteorder != 'little':
            samples.byteswap()
    raw_text = raw.read_text(encoding='utf-8-sig')
    raw_cues = alignment.parse_srt(raw_text)
    text, align_report = alignment.align(brief, raw_text, media_duration=duration)
    cues = alignment.parse_srt(text)
    raw_levels, raw_issues = cue_energy(samples, rate, raw_cues, duration, threshold)
    corrected_levels, corrected_issues = cue_energy(samples, rate, cues, duration, threshold)
    exact = ' '.join(cue['text'] for cue in cues).split() == reference
    possible_speech_gaps = []
    for change in align_report['text_changes']:
        largest = max(len(change['transcription'].split()), len(change['script'].split()))
        if change['operation'] in {'insert', 'delete'} and largest > 3 or change['operation'] == 'replace' and largest > 8:
            possible_speech_gaps.append(change)
    issues = [*raw_issues, *corrected_issues]
    if not exact:
        issues.append('Corrected captions differ from the frozen script.')
    if align_report['layout_review']:
        issues.append('Caption layout requires review.')
    if possible_speech_gaps:
        issues.append('Large transcript changes require speech review.')
    if any(sha(path) != value for path, value in fingerprints.items()):
        issues.append('An input changed during QA; repeat against completed immutable exports.')
    if corrected.exists() and corrected.read_text() != text:
        raise ValueError('Corrected caption destination already contains different data; choose a fresh path.')
    corrected.parent.mkdir(parents=True, exist_ok=True)
    corrected.write_text(text, encoding='utf-8')
    rms = math.sqrt(sum(value * value for value in samples) / len(samples)) / 32768 if samples else 0
    result = {'passed': not issues, 'lesson_id': lesson['id'], 'checked_at': datetime.now(timezone.utc).isoformat(),
              'method': 'Complete FFmpeg decode to mono 48kHz PCM; Descript raw cue boundaries retained; exact frozen-script text projection; every raw and corrected speech cue measured.',
              'lesson': {'file': str(lesson_path), 'sha256': fingerprints[str(lesson_path)], 'words': len(reference), 'scenes': len(lesson['scenes'])},
              'audio': {'file': str(audio), 'sha256': fingerprints[str(audio)], 'full_decode': 'passed', 'duration_seconds': duration,
                        'sample_rate': rate, 'decoded_samples': len(samples), 'rms': round(rms, 9),
                        'peak': max((abs(value) for value in samples), default=0) / 32768,
                        'full_scale_samples': sum(abs(value) >= 32767 for value in samples)},
              'raw_captions': {'file': str(raw), 'sha256': fingerprints[str(raw)], 'cues': len(raw_cues), 'energy': raw_levels},
              'corrected_captions': {'file': str(corrected), 'sha256': sha(corrected), 'cues': len(cues), 'exact_script': exact, 'energy': corrected_levels},
              'signal_threshold_rms': threshold, 'silent_raw_cues': sum(x['below_threshold'] for x in raw_levels),
              'silent_corrected_cues': sum(x['below_threshold'] for x in corrected_levels),
              'minimum_raw_cue_rms': min(x['rms'] for x in raw_levels), 'minimum_corrected_cue_rms': min(x['rms'] for x in corrected_levels),
              'alignment': align_report, 'possible_speech_gaps': possible_speech_gaps, 'issues': issues,
              'human_listening_review': 'not performed',
              'limits': ['Energy establishes non-silent signal, not word recognition or intelligibility.', 'Script correction projects text onto existing ASR cue boundaries; no word-level timing or human listening is asserted.']}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('lesson', 'audio', 'raw', 'corrected', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--ffmpeg', default=shutil.which('ffmpeg'))
    parser.add_argument('--expected-lesson-sha256')
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error('Supply --ffmpeg or put FFmpeg on PATH.')
    try:
        result = audit(args.lesson, args.audio, args.raw, args.corrected, args.report, args.ffmpeg, args.expected_lesson_sha256)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps({key: result[key] for key in ('passed', 'lesson_id', 'silent_raw_cues', 'minimum_raw_cue_rms', 'issues')}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
