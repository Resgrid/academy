"""Assemble approved Descript narration with the original local illustrations."""
import argparse
import array
import concurrent.futures
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import textwrap
from align_captions import align, parse_srt, seconds, BASE, ROOT

def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-2500:])
    return result

def timestamp(value, comma=True):
    ms = round(value * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}{"," if comma else "."}{ms%1000:03}'

def duration(ffmpeg, path):
    info = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", info)
    if not match:
        raise ValueError("Cannot read media duration: " + path.name)
    h, m, s = map(float, match.groups())
    return h * 3600 + m * 60 + s

def make_lesson(ident, ffmpeg, pause):
    work = BASE / "build/natural" / ident
    work.mkdir(parents=True, exist_ok=True)
    narration = work / "narration-export.media"
    if not narration.exists():
        narration = ROOT / "natural/audio" / (ident + ".m4a")
    raw = ROOT / "natural/captions" / (ident + "-raw.srt")
    brief = json.loads((ROOT / (ident + "-edit-brief.json")).read_text())
    raw_text = raw.read_text()
    voice_duration = duration(ffmpeg, narration)
    # Original narration exports retain their editorial closing lines. The course
    # script defines the current lesson; remove only known, complete closing cues
    # before alignment when those lines are absent from the current script.
    sys.path.insert(0, str(BASE.parent / 'scripts'))
    from render_public_media import INTRO_TAIL, TAIL, parse_captions, publication_cut
    expected = ' '.join(scene['narration'] for scene in brief['scenes'])
    editorial = INTRO_TAIL if ident == '00-start' else TAIL
    if editorial not in expected:
        cut, retained = publication_cut(ident, parse_captions(raw_text), voice_duration)
        if cut < voice_duration:
            prepared = work / 'narration-publication.m4a'
            run([ffmpeg, '-v', 'error', '-y', '-i', str(narration), '-t', str(cut),
                 '-map', '0:a:0', '-c:a', 'copy', str(prepared)])
            narration = prepared
            voice_duration = duration(ffmpeg, narration)
            raw_text = ''.join(f'{i}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}\n\n'
                               for i, c in enumerate(retained, 1))
    level_info = run([ffmpeg, "-v", "info", "-i", str(narration), "-map", "0:a:0",
                      "-af", "volumedetect", "-f", "null", "-"]).stderr
    level = re.search(r"mean_volume: (-?[0-9.]+) dB", level_info)
    if not level or float(level.group(1)) < -60:
        raise ValueError("Narration is silent or too quiet: " + ident)
    # A successful export can still contain unfinished TTS paragraphs as silence.
    # Check every spoken cue before relying on transcript text or overall volume.
    decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(narration),
                              "-map", "0:a:0", "-ar", "16000", "-ac", "1",
                              "-f", "f32le", "-"], capture_output=True, check=True)
    samples = array.array("f")
    samples.frombytes(decoded.stdout)
    cue_levels = []
    for index, cue in enumerate(parse_srt(raw_text)):
        clip = samples[int(seconds(cue["start"]) * 16000):int(seconds(cue["end"]) * 16000)]
        rms = math.sqrt(sum(v * v for v in clip) / len(clip)) if clip else 0
        cue_levels.append(rms)
        if rms < .001:
            raise ValueError(f"Unrendered or silent narration cue {index + 1}: {ident}")
    srt, audit = align(brief, raw_text, media_duration=voice_duration)
    for change in audit["text_changes"]:
        if change["operation"] in ("delete", "insert"):
            value = change["transcription"] if change["operation"] == "delete" else change["script"]
            if len(value.split()) > 3:
                raise ValueError("Possible extra or missing speech: " + ident + " " + value)
        elif change["operation"] == "replace" and max(
                len(change["transcription"].split()), len(change["script"].split())) > 8:
            raise ValueError("Unexpected narration difference: " + ident)
    cues = parse_srt(srt)
    word_starts, count = {}, 0
    for i, cue in enumerate(cues):
        word_starts[count] = i
        count += len(cue["text"].split())
    boundaries, source_cuts, word_count = [0], [0.0], 0
    for i, scene in enumerate(brief["scenes"]):
        if i:
            if word_count not in word_starts:
                raise ValueError("A subtitle cue crosses a scene boundary: " + ident + " " + scene["title"])
            cue_index = word_starts[word_count]
            start = seconds(cues[cue_index]["start"])
            prior_end = seconds(cues[cue_index - 1]["end"])
            source_cuts.append((start + prior_end) / 2)
            boundaries.append(cue_index)
        word_count += len(scene["narration"].split())
    source_cuts.append(voice_duration)
    boundaries.append(len(cues))
    out_cues, chapters = [], []
    for i, scene in enumerate(brief["scenes"]):
        shift = pause * i
        for cue in cues[boundaries[i]:boundaries[i+1]]:
            wrapped = textwrap.wrap(cue["text"], width=42, break_on_hyphens=False, break_long_words=False)
            if len(wrapped) > 2:
                wrapped = textwrap.wrap(cue["text"], width=48, break_on_hyphens=False, break_long_words=False)
            if len(wrapped) > 2:
                raise ValueError("Caption layout exceeds two lines: " + ident)
            out_cues.append({**cue, "start": timestamp(seconds(cue["start"]) + shift),
                            "end": timestamp(seconds(cue["end"]) + shift), "text": "\n".join(wrapped)})
        chapters.append({"title": scene["title"], "start": source_cuts[i] + shift,
                         "end": source_cuts[i+1] + shift + (pause if i < len(brief["scenes"])-1 else 0)})
    subtitle = work / "captions.srt"
    subtitle.write_text("\n\n".join(
        f'{i+1}\n{c["start"]} --> {c["end"]}\n{c["text"]}'
        for i, c in enumerate(out_cues)) + "\n\n")
    # One small silent hold per scene transition preserves the voice's prosody.
    n = len(chapters)
    filters = ["[0:a]asplit=" + str(n) + "".join(f"[s{i}]" for i in range(n))]
    for i in range(n):
        f = f'[s{i}]atrim=start={source_cuts[i]:.6f}:end={source_cuts[i+1]:.6f},asetpts=PTS-STARTPTS'
        if i < n-1:
            f += f",apad=pad_dur={pause}"
        filters.append(f + f"[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[out]")
    voice = work / "prepared.wav"
    run([ffmpeg, "-y", "-v", "error", "-i", str(narration), "-filter_complex", ";".join(filters),
         "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(voice)])
    total = voice_duration + pause * (n-1)
    listing = work / "visuals.txt"
    text = ""
    for i, chapter in enumerate(chapters):
        image = BASE / "build" / ident / f"{i:02}.png"
        if not image.exists():
            image = ROOT / "slides" / f"{ident}-slide-{i+1:02}.png"
        assert image.is_file()
        text += f"file '{image}'\nduration {chapter['end']-chapter['start']:.6f}\n"
    last_image = BASE / "build" / ident / f"{n-1:02}.png"
    if not last_image.exists():
        last_image = ROOT / "slides" / f"{ident}-slide-{n:02}.png"
    text += f"file '{last_image}'\n"
    listing.write_text(text)
    metadata = work / "chapters.txt"
    text = ";FFMETADATA1\ntitle=" + brief["title"] + "\ncomment=Resgrid Academy video lesson\n"
    for c in chapters:
        text += (f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c["start"]*1000)}\n'
                 f'END={round(c["end"]*1000)}\ntitle={c["title"].replace("=", "-")}\n')
    metadata.write_text(text)
    output = work / "finished.mp4"
    run([ffmpeg, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-i", str(voice), "-i", str(subtitle), "-f", "ffmetadata", "-i", str(metadata),
         "-map", "0:v:0", "-map", "1:a:0", "-map", "2:0", "-map_metadata", "3",
         "-map_chapters", "3", "-r", "30", "-t", f"{total:.6f}", "-c:v", "libx264",
         "-preset", "ultrafast", "-tune", "stillimage", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
         "-c:s", "mov_text", "-metadata:s:s:0", "language=eng", "-movflags", "+faststart", str(output)])
    info = subprocess.run([ffmpeg, "-hide_banner", "-i", str(output)], capture_output=True, text=True).stderr
    for prop in ("1920x1080", "30 fps", "Subtitle: mov_text", "48000 Hz", "Chapters:"):
        if prop not in info:
            raise ValueError("Natural-voice output missing " + prop + ": " + ident)
    for c in chapters:
        run([ffmpeg, "-v", "error", "-ss", str((c["start"] + c["end"]) / 2), "-i", str(output),
             "-t", "1", "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"])
    # Install only after the complete script, timing, formats, and scene samples pass.
    backup = BASE / "build/original-narration"
    backup.mkdir(exist_ok=True)
    media = BASE / "media"
    for suffix in (".mp4", ".srt", ".vtt", ".chapters.json"):
        old = media / (ident + suffix)
        if not (backup / old.name).exists():
            shutil.copy2(old, backup / old.name)
    shutil.copy2(output, media / (ident + ".mp4"))
    audio_sources = ROOT / "natural/audio"
    audio_sources.mkdir(exist_ok=True)
    # Store an audio-only source in the portable editable package.
    if narration != audio_sources / (ident + ".m4a"):
        run([ffmpeg, "-y", "-v", "error", "-i", str(narration), "-map", "0:a:0",
             "-c:a", "copy", str(audio_sources / (ident + ".m4a"))])
    shutil.copy2(subtitle, media / (ident + ".srt"))
    vtt = "WEBVTT\n\nNOTE English captions\n\n"
    vtt += re.sub(r"\d{2}:\d{2}:\d{2},\d{3}", lambda m: m.group().replace(",", "."), subtitle.read_text())
    (media / (ident + ".vtt")).write_text(vtt)
    (media / (ident + ".chapters.json")).write_text(json.dumps(chapters, indent=2) + "\n")
    audit.update({"voice": "Warm Lulu", "voice_library_id": "itMkRQx56fOF4CJe1D0C",
                  "duration_seconds": round(total, 2), "source_audio_seconds": voice_duration,
                  "transition_pause_seconds": pause, "scenes": n, "sample_decode": "all scene midpoint samples passed",
                  "format": "1920x1080, 30 fps, H.264, AAC 48kHz, English mov_text captions",
                  "human_listening_review": "pending", "chapters": chapters})
    audit["source_mean_volume_db"] = float(level.group(1))
    audit["spoken_cue_audio_check"] = {"checked_cues": len(cue_levels),
                                       "silent_cues": 0, "minimum_rms": min(cue_levels)}
    (ROOT / "natural" / (ident + "-validation.json")).write_text(json.dumps(audit, indent=2) + "\n")
    print("Natural narration installed: " + ident + f" ({total:.1f}s, {n} scenes)", flush=True)
    return ident, audit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", required=True)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--lesson", action="append")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--pause", type=float, default=.45)
    args = parser.parse_args()
    if args.all:
        args.lesson = [l["id"] for l in json.loads((BASE / "course.json").read_text())["lessons"]]
    if not 0 <= args.pause <= 1:
        raise ValueError("Pause must be 0-1 seconds")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda ident: make_lesson(ident, args.ffmpeg, args.pause), args.lesson))
    course_file = BASE / "course.json"
    course = json.loads(course_file.read_text())
    for ident, audit in results:
        lesson = next(x for x in course["lessons"] if x["id"] == ident)
        lesson["duration_seconds"] = audit["duration_seconds"]
        lesson["voice"] = "Warm Lulu"
        for scene, chapter in zip(lesson["scenes"], audit["chapters"]):
            scene["start_seconds"] = chapter["start"]
            scene["duration_seconds"] = chapter["end"] - chapter["start"]
    course["voice_status"] = {"converted_lessons": sum(l.get("voice") == "Warm Lulu" for l in course["lessons"]),
                            "total_lessons": len(course["lessons"]), "voice": "Warm Lulu",
                            "human_listening_review": "pending"}
    course_file.write_text(json.dumps(course, indent=2) + "\n")

if __name__ == "__main__":
    main()
