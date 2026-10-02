"""Check the installed voice edition against its source audio and exact scripts."""
import argparse
import array
import concurrent.futures
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from align_captions import BASE, ROOT, parse_srt, seconds

def validate(lesson, ffmpeg):
    ident = lesson["id"]
    brief = json.loads((ROOT / (ident + "-edit-brief.json")).read_text())
    reference = " ".join(s["narration"] for s in brief["scenes"]).split()
    source = ROOT / "natural/audio" / (ident + ".m4a")
    raw = parse_srt((ROOT / "natural/captions" / (ident + "-raw.srt")).read_text())
    decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(source),
        "-map", "0:a:0", "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
        capture_output=True, check=True)
    samples = array.array("f")
    samples.frombytes(decoded.stdout)
    if sys.byteorder != "little":
        samples.byteswap()
    levels = []
    for i, cue in enumerate(raw):
        clip = samples[int(seconds(cue["start"]) * 16000):int(seconds(cue["end"]) * 16000)]
        rms = math.sqrt(sum(v * v for v in clip) / len(clip)) if clip else 0
        if rms < .001:
            raise ValueError(f"{ident}: source speech cue {i + 1} is silent")
        levels.append(rms)
    srt_text = (BASE / "media" / (ident + ".srt")).read_text()
    cues = parse_srt(srt_text)
    if " ".join(c["text"] for c in cues).split() != reference:
        raise ValueError(ident + ": installed captions differ from the script")
    previous = 0
    for cue in cues:
        start, end = seconds(cue["start"]), seconds(cue["end"])
        if not (start >= previous - .002 and end > start and end <= lesson["duration_seconds"] + .05):
            raise ValueError(ident + ": invalid installed caption timing")
        previous = end
    for block in re.split(r"\n\s*\n", srt_text.strip()):
        lines = block.splitlines()[2:]
        if len(lines) > 2 or max(map(len, lines)) > 48:
            raise ValueError(ident + ": caption layout exceeds two lines / 48 columns")
    measured = subprocess.run([ffmpeg, "-v", "info", "-i", str(BASE / lesson["video"]),
        "-map", "0:a:0", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json",
        "-f", "null", "-"], capture_output=True, text=True, check=True)
    match = re.search(r'\{\s*"input_i".*?\}', measured.stderr, re.S)
    if not match:
        raise ValueError(ident + ": loudness measurement unavailable")
    loud = json.loads(match.group())
    integrated, peak = float(loud["input_i"]), float(loud["input_tp"])
    if not (-18 <= integrated <= -14 and peak <= -.8):
        raise ValueError(f"{ident}: unexpected audio level {integrated} LUFS / {peak} dBTP")
    return {"lesson": ident, "source_cues_checked": len(raw), "silent_source_cues": 0,
            "minimum_source_cue_rms": round(min(levels), 6), "installed_caption_cues": len(cues),
            "complete_script_and_caption_layout": "passed", "integrated_loudness_lufs": integrated,
            "true_peak_dbtp": peak, "voice": "Warm Lulu", "human_listening_review": "pending"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", required=True)
    args = parser.parse_args()
    course = json.loads((BASE / "course.json").read_text())
    lessons = [l for l in course["lessons"] if l.get("voice") == "Warm Lulu"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        reports = list(pool.map(lambda lesson: validate(lesson, args.ffmpeg), lessons))
    result = {"result": "passed", "natural_voice_lessons": len(reports), "total_lessons": len(course["lessons"]),
        "source_cues_checked": sum(x["source_cues_checked"] for x in reports),
        "pending_voice_lessons": [l["id"] for l in course["lessons"] if l.get("voice") != "Warm Lulu"],
        "human_listening_review": "pending", "lessons": reports}
    (ROOT / "natural/audio-quality-validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "lessons"}), flush=True)

if __name__ == "__main__":
    main()
