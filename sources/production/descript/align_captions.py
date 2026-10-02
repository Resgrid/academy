"""Correct Descript SRT text from recorded scripts while preserving ASR cue timing.

This is cue alignment, not independently measured per-word alignment. Audit every
text change, retain raw exports, and keep human playback review pending.
"""
import argparse
import difflib
import json
from pathlib import Path
import re
import shutil
import subprocess
import textwrap

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / "production/descript"

def seconds(value):
    h, m, tail = value.replace(",", ".").split(":")
    return 3600 * int(h) + 60 * int(m) + float(tail)

def parse_srt(text):
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            raise ValueError("Unexpected SRT block")
        start, end = lines[1].split(" --> ")
        cues.append({"start": start, "end": end, "text": " ".join(lines[2:])})
    return cues

def normalized(word):
    return re.sub(r"[^a-z0-9]", "", word.lower())

def align(brief, raw, media_duration=None):
    cues = parse_srt(raw)
    reference = " ".join(s["narration"] for s in brief["scenes"]).split()
    heard, cue_ids = [], []
    for i, cue in enumerate(cues):
        words = cue["text"].split()
        heard.extend(words)
        cue_ids.extend([i] * len(words))
    matcher = difflib.SequenceMatcher(
        None, list(map(normalized, heard)), list(map(normalized, reference)), autojunk=False)
    corrected = [[] for _ in cues]
    changes = []
    for op, a, b, c, d in matcher.get_opcodes():
        if op != "equal":
            changes.append({"operation": op, "transcription": " ".join(heard[a:b]),
                            "script": " ".join(reference[c:d])})
        for j in range(c, d):
            if op == "equal":
                target = cue_ids[a + j - c]
            elif b > a:
                target = cue_ids[min(b - 1, a + (j - c) * (b - a) // max(1, d - c))]
            else:
                target = cue_ids[min(a, len(cue_ids) - 1)]
            corrected[target].append(reference[j])
    out, review = [], []
    last_end = 0.0
    for i, cue in enumerate(cues):
        start, end = seconds(cue["start"]), seconds(cue["end"])
        if not (0 <= start < end and start >= last_end - .002):
            raise ValueError("Invalid or overlapping cue timing")
        last_end = end
        if not corrected[i]:
            continue
        content = " ".join(corrected[i])
        # Preserve export timing; permit up to 48 columns rather than inventing
        # sub-cue timestamps when correcting a long machine transcription.
        wrapped = textwrap.wrap(content, width=42, break_on_hyphens=False, break_long_words=False)
        if len(wrapped) > 2:
            wrapped = textwrap.wrap(content, width=48, break_on_hyphens=False, break_long_words=False)
        if len(wrapped) > 2:
            review.append({"cue": i + 1, "reason": "more than two caption lines"})
        out.append(f'{len(out)+1}\n{cue["start"]} --> {cue["end"]}\n' + "\n".join(wrapped))
    srt = "\n\n".join(out) + "\n\n"
    reconstructed = " ".join(c["text"] for c in parse_srt(srt)).split()
    if reconstructed != reference:
        raise ValueError("Corrected subtitles differ from recorded script: " + brief["lesson"])
    limit = media_duration if media_duration is not None else sum(s["duration_seconds"] for s in brief["scenes"])
    if last_end > limit + .2:
        raise ValueError("Caption extends beyond the local lesson")
    return srt, {"lesson": brief["lesson"], "cues": len(out),
                 "match_ratio": round(matcher.ratio(), 4), "text_changes": changes,
                 "layout_review": review, "human_playback_review": "pending"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remux", action="store_true")
    parser.add_argument("--ffmpeg")
    args = parser.parse_args()
    raw_files = sorted((ROOT / "captions/raw").glob("*.srt"))
    if len(raw_files) != 24:
        raise ValueError("Expected all 24 exported transcripts")
    outdir = ROOT / "captions/corrected"
    outdir.mkdir(parents=True, exist_ok=True)
    audit = []
    for file in raw_files:
        brief = json.loads((ROOT / (file.stem + "-edit-brief.json")).read_text())
        srt, report = align(brief, file.read_text())
        (outdir / file.name).write_text(srt)
        audit.append(report)
    (ROOT / "captions/validation.json").write_text(json.dumps({
        "method": "Descript speech-timed cues; exact-script text corrections projected onto existing cue boundaries",
        "status": "timing and complete script coverage validated; human playback review pending",
        "lessons": audit}, indent=2) + "\n")
    if args.remux:
        if not args.ffmpeg:
            raise ValueError("--ffmpeg is required for remux")
        backup = ROOT / "captions/estimated"
        backup.mkdir(exist_ok=True)
        for file in outdir.glob("*.srt"):
            lesson = file.stem
            media = BASE / "media" / (lesson + ".mp4")
            temp = media.with_name(lesson + ".speech-timed.mp4")
            subprocess.run([args.ffmpeg, "-y", "-v", "error", "-i", str(media),
                "-i", str(file), "-map", "0:v:0", "-map", "0:a:0", "-map", "1:0",
                "-map_metadata", "0", "-map_chapters", "0", "-c:v", "copy",
                "-c:a", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=eng",
                "-movflags", "+faststart", str(temp)], check=True)
            temp.replace(media)
            for ext in ("srt", "vtt"):
                old = BASE / "media" / (lesson + "." + ext)
                if not (backup / old.name).exists():
                    shutil.copy2(old, backup / old.name)
            (BASE / "media" / file.name).write_text(file.read_text())
            vtt = "WEBVTT\n\nNOTE Speech-timed Descript cues; script-corrected text. Human playback review pending.\n\n"
            vtt += re.sub(r"\d{2}:\d{2}:\d{2},\d{3}",
                          lambda m: m.group().replace(",", "."), file.read_text())
            (BASE / "media" / (lesson + ".vtt")).write_text(vtt)
    print(json.dumps({"lessons": len(audit), "cues": sum(x["cues"] for x in audit),
                      "minimum_match_ratio": min(x["match_ratio"] for x in audit),
                      "layout_flags": sum(len(x["layout_review"]) for x in audit),
                      "remuxed": args.remux}))

if __name__ == "__main__":
    main()
