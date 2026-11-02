#!/usr/bin/env python3
"""Opt-in Unit checklist source/caption authoring; no speech or render commands.

With no arguments, verify the immutable eight-scene candidate, 17 untimed
spans, eight actual screenshots and genuine 54-cue/one-second exports. This
mode needs no audio and writes nothing. It does not create a timed plan.

--write-plan requires local actual audio, corrected SRT and completed narration
QA, with independently supplied SHA256 values and --ffmpeg. The helper checks
the report and repeats the complete PCM decode/each-cue energy measurement
before constructing a plan. It never estimates word times, splits cues, trims
audio, renders, publishes, changes canonicals or approves frames/playback.

Existing user confirmation that all eight generated paragraphs play, plus the
parent's eight-asset/190.64s composition readback, is source-listening provenance.
It is NOT a claim that the parent listened to an exact downloaded AAC. No new
user listening approval is requested. Later exact-export hashes and full decode
QA bind that existing source confirmation to the retained media. Rendered frame
and actual browser playback review remain separate mandatory work.
"""

import argparse
import array
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import tempfile
import wave


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
NAME = "app-unit-readiness-checklists"
BASE = Path("expansion/plans/app-unit-readiness-checklists-candidate-20261027-v2")
FROZEN = "822c1c42f26c43a0ed0a20e1562c9d42dd1417e80287cbaf25ddcc68fe8446a2"
INPUTS = {
    BASE / (NAME + ".narrated-source.json"): FROZEN,
    BASE / "captures.reviewed.json": "411803c22f300edded7c40732931bce1fe2266bc75d6d1f6a7d459056e86e4ec",
    BASE / "untimed-screen-sequence.json": "9bdf20cc2d78290986557c513fde9e5998c5992f005393ad0895632c60129cee",
    BASE / "parent-source-review-before-voice.json": "072e0ee531d5e2bc1b2f20b3c4fdc0b9b2017ec4e4f2760a0031093ca2854a8d",
    BASE / "source-citations.json": "e294805eebe68d5e6e62923584f2a5a6e6612eab8849a02267dfdbd67b8ec3ac",
    BASE / "narration.txt": "17d890c11f2ad5bcf78ca039bfa6d12c2565d4fd4651a3f9c2f3b9508c4f3ecd",
    Path("expansion/audio/" + NAME + ".fresh.txt"): "c9f507552d1ec6abf322dc0efb423afac9c66a6109a692419ae3022170c37c09",
    Path("expansion/audio/" + NAME + ".fresh.srt"): "25e954f3eb7a2a9690044aa21bc7263a41a4a8ca3e0873ec145551860f9624e9",
    Path("expansion/audio/" + NAME + ".one-second.txt"): "8bd606c58de108316e395661edb4c3e00189c08345dc80704fc26ffe3812dc0c",
}
RAW = Path("expansion/audio/" + NAME + ".fresh.srt")
SCENE_CUES = [(1, 8), (9, 14), (15, 22), (23, 29), (30, 35), (36, 41), (42, 47), (48, 54)]
PICTURES = [(1, 8, 8), (9, 14, 9), (15, 22, 10), (23, 29, 11),
            (30, 35, 12), (36, 42, 13), (43, 47, 14), (48, 54, 15)]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def read(path):
    return json.loads(Path(path).read_text())


def cue_references():
    """Literal pictured labels -> genuine spoken references, manually reviewed."""
    return {
        3: {"Engine 51": "Engine 51"},
        4: {"Checklists": "Checklists", "Start checklist": "Start checklist"},
        5: {"Engine 51 — daily readiness": "Engine 51 daily readiness", "Engine 51": "Engine 51"},
        7: {"Ambulance 61 — equipment check": "Ambulance 61"},
        9: {"Engine 51 · Version 1": "Version 1"},
        10: {"Equipment ready for the exercise (Required)": "Equipment ready for the exercise", "Critical": "Critical"},
        11: {"Pass": "Pass", "Note": "Note"}, 14: {"Note": "note", "Next": "Next"},
        15: {"Stock and supplies recorded (Required)": "Stock and supplies recorded"},
        16: {"Pass": "Pass"}, 20: {"Next": "Next"},
        23: {"Handover notes reviewed (Required)": "Handover notes reviewed"},
        24: {"Pass": "Pass", "Note": "Note"},
        27: {"Save progress": "Save progress"}, 28: {"Close": "Close"},
        30: {"Local drafts": "Local drafts", "Draft 1": "Draft 1"},
        31: {"History": "History", "Engine 51 · 10/27/2026, 11:21:34 PM": "timestamped Engine 51 entry"},
        36: {"Pass": "Pass"},
        39: {"Save progress": "Save progress", "Submit checklist": "Submit checklist"},
        42: {"Submit checklist": "Submit checklist"},
        43: {"Submitted · Score: 100": "Submitted, Score 100"}, 44: {"Close": "Close"},
        48: {"Submitted · Score: 100": "submitted result"},
    }


def check_correspondence(lesson, cues, records, assignments, references):
    by_id = {row["id"]: row for row in records}
    need(set(assignments) == set(range(1, 55)), "Every genuine cue needs exactly one actual source image.")
    for index, names in references.items():
        row = by_id[assignments[index]]
        for label, phrase in names.items():
            need(label in row["visible_labels"], f"Cue{index}: unseen pictured control {label}.")
            need(phrase.casefold() in cues[index - 1]["text"].casefold(), f"Cue{index}: reference absent from genuine speech.")
    for scene, (first, last) in zip(lesson["scenes"], SCENE_CUES):
        spoken = " ".join(c["text"] for c in cues[first - 1:last]).split()
        need(spoken == scene["narration"].split(), "Genuine cue crosses or changes a scene boundary: " + scene["id"])
        visible = set().union(*(set(by_id[assignments[i]]["visible_labels"]) for i in range(first, last + 1)))
        need(set(scene["required_labels"]) <= visible, "Scene contains an unmatched pictured label: " + scene["id"])
    need(assignments[42].startswith("013-") and assignments[43].startswith("014-"),
         "Keep Submit on the working form; switch at genuine cue43, not before it.")


def source_preflight(root=ROOT):
    root = Path(root).resolve()
    sources = root / "sources"
    sys.path.insert(0, str(root / "scripts"))
    from render_walkthrough import load_cues
    from verify_capture_evidence import _Validator

    for relative, expected in INPUTS.items():
        need(sha(sources / relative) == expected, "Frozen source/export hash differs: " + str(relative))
    lesson = read(sources / BASE / (NAME + ".narrated-source.json"))
    sequence = read(sources / BASE / "untimed-screen-sequence.json")
    records = read(sources / BASE / "captures.reviewed.json")["screenshots"]
    review = read(sources / BASE / "parent-source-review-before-voice.json")
    expected = " ".join(x["narration"] for x in lesson["scenes"]).split()
    need((len(lesson["scenes"]), len(expected), len(records)) == (8, 497, 8), "Frozen source count differs.")
    need(review["lesson_sha256"] == FROZEN and review["script_approved_for_private_narration"] is True,
         "The existing parent whole-script/source review is missing.")
    need((sources / "expansion/audio" / (NAME + ".fresh.txt")).read_text().split() == expected,
         "Fresh plain words differ from all eight frozen scenes.")
    dense = (sources / "expansion/audio" / (NAME + ".one-second.txt")).read_text()
    need(re.sub(r"\[\d\d:\d\d:\d\d\]", "", dense).split() == expected, "Dense TXT words differ from frozen narration.")
    raw = load_cues(sources / RAW)
    need(len(raw) == 54 and " ".join(c["text"] for c in raw).split() == expected, "Fresh SRT is not the full exact54-cue script.")
    need(raw[42]["start"] == 145.289 and raw[-1]["end"] == 190.469, "Actual cue transition/closing timing changed.")
    need("[00:02:21]" in dense and "[00:02:25]" in dense, "Missing genuine submission-boundary anchors.")
    spans = [span for scene in sequence["scenes"] for span in scene["spans"]]
    need(len(spans) == 17, "Expected17 untimed editorial spans.")
    for scene, authored in zip(sequence["scenes"], lesson["scenes"]):
        need(scene["id"] == authored["id"] and " ".join(s["text"] for s in scene["spans"]).split() == authored["narration"].split(),
             "Untimed spans do not preserve each whole scene.")
    validator = _Validator(sources)
    for row in records:
        need(row["app"] == "Unit" and row["kind"] == "application_screenshot", "No substitute/non-Unit illustration is permitted.")
        need(row.get("eligible_for_lesson") is True and row["capture_review"]["passed"] is True, "Source has no bounded actual-image review.")
        for field, digest in (("file", "sha256"), ("dom_file", "dom_sha256")):
            need(sha(sources / row[field]) == row[digest], "Source pixels/DOM changed: " + row["id"])
        need(row["capture_review"]["sha256"] == row["sha256"], "Review is for different pixels.")
        validator.observations(row, row["id"])
    need(not validator.issues, "; ".join(validator.issues))
    numbered = {int(row["id"].split("-")[0]): row["id"] for row in records}
    assignments = {}
    for first, last, number in PICTURES:
        for cue in range(first, last + 1):
            need(cue not in assignments, "Duplicate actual-cue assignment.")
            assignments[cue] = numbered[number]
    check_correspondence(lesson, raw, records, assignments, cue_references())
    return {"root": root, "sources": sources, "lesson": lesson, "raw": raw,
            "records": records, "assignments": assignments, "untimed_spans": len(spans)}


def verify_media_qa(context, *, audio, audio_sha, corrected, corrected_sha, qa_path, qa_sha):
    """Check a hash-bound completed report; actual re-decode is also mandatory below."""
    for label, digest in (("audio", audio_sha), ("corrected SRT", corrected_sha), ("QA", qa_sha)):
        need(isinstance(digest, str) and re.fullmatch(r"[a-f0-9]{64}", digest), "Supply independent expected " + label + " SHA256.")
    paths = [Path(p).resolve() for p in (audio, corrected, qa_path)]
    for p in paths:
        need(p.is_relative_to(context["sources"]), "Actual media/QA must remain inside sources.")
        need("estimated" not in p.name.casefold(), "Estimated exports cannot satisfy actual-media QA.")
    audio, corrected, qa_path = paths
    need(sha(qa_path) == qa_sha, "QA report hash differs.")
    qa = read(qa_path)
    need(qa.get("passed") is True and qa.get("issues") == [], "Actual narration QA must pass with zero issues.")
    need(qa.get("lesson", {}).get("sha256") == FROZEN and qa["lesson"].get("words") == 497
         and qa["lesson"].get("scenes") == 8, "QA does not bind this full eight-scene497-word source.")
    need(sha(audio) == audio_sha and audio.stat().st_size > 100_000, "Actual audio changed, missing or placeholder-sized.")
    need(sha(corrected) == corrected_sha, "Corrected SRT hash differs.")
    detail = qa.get("audio", {})
    need(detail.get("sha256") == audio_sha and detail.get("full_decode") == "passed", "A complete decode of the exact actual audio is required.")
    duration = detail.get("duration_seconds")
    need(finite(duration) and context["raw"][-1]["end"] <= duration <= context["raw"][-1]["end"] + 2,
         "Partial/truncated audio does not enclose the full genuine transcript.")
    need(detail.get("sample_rate") == 48000 and finite(detail.get("decoded_samples"))
         and abs(detail["decoded_samples"] - duration * 48000) < 1, "Full decoded48kHz sample inventory required.")
    threshold = qa.get("signal_threshold_rms")
    need(finite(threshold) and threshold >= .001, "Cue-energy threshold missing or weakened.")
    need(qa.get("silent_raw_cues") == qa.get("silent_corrected_cues") == 0, "Every raw/corrected speech cue must be non-silent.")
    for key, expected_sha in (("raw_captions", INPUTS[RAW]), ("corrected_captions", corrected_sha)):
        part = qa.get(key, {})
        need(part.get("sha256") == expected_sha and part.get("cues") == 54, "QA caption inventory differs: " + key)
        levels = part.get("energy", [])
        need(len(levels) == 54, "All54 measured cue energies are required: " + key)
        for index, (level, cue) in enumerate(zip(levels, context["raw"]), 1):
            need(level.get("cue") == index and finite(level.get("start")) and finite(level.get("end"))
                 and abs(level["start"] - cue["start"]) < 1e-9 and abs(level["end"] - cue["end"]) < 1e-9
                 and level.get("samples", 0) > 0 and finite(level.get("rms")) and level["rms"] >= threshold
                 and level.get("below_threshold") is False, "Invalid/missing/silent cue-energy row: " + str(index))
    need(qa["corrected_captions"].get("exact_script") is True and not qa.get("possible_speech_gaps"), "Unresolved script/speech mismatch.")
    from render_walkthrough import load_cues
    cues = load_cues(corrected)
    need(len(cues) == 54 and all((c["start"], c["end"], c["text"].split()) == (o["start"], o["end"], o["text"].split())
         for c, o in zip(cues, context["raw"])), "Corrected captions must preserve every genuine cue bound and exact word.")
    return qa, audio, corrected, qa_path


def repeat_actual_decode(context, audio, corrected, qa, ffmpeg):
    need(bool(ffmpeg), "Supply --ffmpeg for the mandatory actual full re-decode before timing.")
    from render_walkthrough import audio_duration
    from qa_narration import alignment, cue_energy
    before = sha(audio)
    with tempfile.TemporaryDirectory(prefix="unit-checklist-actual-decode-") as tmp:
        pcm = Path(tmp) / "actual.wav"
        duration = audio_duration(str(ffmpeg), audio, pcm)
        with wave.open(str(pcm), "rb") as stream:
            need(stream.getnchannels() == 1 and stream.getsampwidth() == 2 and stream.getframerate() == 48000,
                 "Actual decoder must supply complete mono16-bit48kHz PCM.")
            samples = array.array("h", stream.readframes(stream.getnframes()))
        if sys.byteorder != "little":
            samples.byteswap()
    need(sha(audio) == before, "Actual audio changed during decode.")
    need(len(samples) == qa["audio"]["decoded_samples"] and abs(duration - qa["audio"]["duration_seconds"]) < 1 / 48000,
         "Actual decoded sample inventory differs from completed QA.")
    for field, caption_path in (("raw_captions", context["sources"] / RAW), ("corrected_captions", corrected)):
        measured_cues = alignment.parse_srt(caption_path.read_text(encoding="utf-8-sig"))
        levels, issues = cue_energy(samples, 48000, measured_cues, duration, qa["signal_threshold_rms"])
        need(not issues, "Actual re-decode found silent/truncated speech: " + "; ".join(issues))
        need(levels == qa[field]["energy"], "Actual re-decoded cue measurements differ from QA: " + field)
    return duration


def build(root=ROOT, *, audio, audio_sha, corrected, corrected_sha, qa_path, qa_sha, ffmpeg):
    context = source_preflight(root)
    qa, audio, corrected, qa_path = verify_media_qa(context, audio=audio, audio_sha=audio_sha,
        corrected=corrected, corrected_sha=corrected_sha, qa_path=qa_path, qa_sha=qa_sha)
    duration = repeat_actual_decode(context, audio, corrected, qa, ffmpeg)
    from verify_capture_evidence import instruction_scene_digest
    now = datetime.now(timezone.utc).isoformat()
    by_id = {r["id"]: r for r in context["records"]}
    references = cue_references()
    scenes = []
    for index, (authored, (first, last)) in enumerate(zip(context["lesson"]["scenes"], SCENE_CUES)):
        start = 0 if index == 0 else context["raw"][first - 1]["start"]
        end = duration if index == 7 else context["raw"][SCENE_CUES[index + 1][0] - 1]["start"]
        screens, expanded = [], []
        for number in range(first, last + 1):
            cue = context["raw"][number - 1]
            sid = context["assignments"][number]
            if not screens or screens[-1]["screenshot_id"] != sid:
                at = start if not screens else cue["start"]
                if screens:
                    screens[-1]["end"] = at
                screens.append({"screenshot_id": sid, "start": at, "end": end})
            names = references.get(number, {})
            expanded.append(dict(cue, cue=number, screenshot_id=sid, required_labels=list(names),
                                 spoken_references=names, instructional=bool(names)))
        need(all(s["end"] - s["start"] >= 2 for s in screens), "Unreadable flash cut; use genuine timing review.")
        built = {"id": authored["id"], "title": authored["title"], "kind": "operational", "start": start,
                 "end": end, "visual_required_labels": authored["required_labels"], "screens": screens, "captions": expanded}
        review = {"passed": True, "reviewer": "Codex source/caption review", "reviewed_at": now,
                  "correspondence_reviewed": True, "no_unseen_controls": True,
                  "mapping_sha256": instruction_scene_digest(built, by_id),
                  "method": "Eight immutable original JPEGs personally inspected during scaffold preparation; existing independent pixel/DOM/privacy and parent497-word source review preserved. All54 actual cues mapped to these screens. Cue42 retains Submit on013; cue43 switches to014 at its real145.289s boundary. Cue45 describes absent buttons, not a clickable control. No word times inferred. Frame/browser checks pending."}
        scenes.append({"id": authored["id"], "start": start, "end": end, "screens": screens,
            "captions": [{k: c[k] for k in ("cue", "screenshot_id", "required_labels", "spoken_references", "instructional")} for c in expanded],
            "instruction_review": review})
    sources = context["sources"]
    relative = lambda path: Path(path).relative_to(sources).as_posix()
    return {"schema_version": 1, "lesson_id": NAME, "duration_seconds": duration,
        "instruction_mapping": "reviewed_scene_coverage", "display_context": "TRAINING ONLY · simulated checklist answers",
        "narration": {"file": relative(audio), "sha256": audio_sha, "kind": "approved_natural_narration", "approval": {
            "reviewer": "User source-playback confirmation; completed actual-export QA", "reviewed_at": now,
            "sha256": audio_sha, "complete_natural_narration": True, "qa_file": relative(qa_path), "qa_sha256": qa_sha,
            "method": "Existing user confirmation all eight generated paragraphs audible; parent readback of eight generated assets/190.64s source composition. Exact retained export now passes full decode, all54 measured cue energies and exact497 words, independently hash-bound and re-decoded. Does not claim parent personally listened to downloaded AAC or that browser video playback was tested."}},
        "captions": {"file": relative(corrected), "sha256": corrected_sha, "kind": "speech_timed_srt", "approval": {
            "reviewer": "Codex exact exported-cue correspondence", "reviewed_at": now, "sha256": corrected_sha,
            "audio_sha256": audio_sha, "speech_timing_reviewed": True,
            "method": "Actual fresh54-cue export plus genuine one-second TXT; every cue bound and word retained, full decoded cue energy checked. No invented or proportional timing."}},
        "capture_manifests": [{"file": str(BASE / "captures.reviewed.json"), "sha256": INPUTS[BASE / "captures.reviewed.json"]}],
        "screenshot_reviews": {r["id"]: {"reviewer": "Existing independent source review plus Codex original-JPEG inspection",
            "reviewed_at": now, "sha256": r["sha256"], "application_visible": True, "labels_legible": True, "no_errors": True,
            "method": r["capture_review"]["method"]} for r in context["records"]},
        "scenes": scenes, "source_freeze": {"lesson_sha256": FROZEN, "spoken_words": 497,
            "inputs": {str(k): v for k, v in INPUTS.items()}},
        "publishable": False, "frame_review": "pending", "browser_playback_review": "pending",
        "limitations": ["Simulated training answers only; no physical readiness/inspection certification.",
            "Same-tab save/reopen only; no offline, browser-restart, cross-device or device-location proof.",
            "No failure/N-A/escalation, witness, signature, photo or native hardware operation.",
            "All eight source images and narrated words remain intact; rendered frames and beginning/middle/end browser playback require their own real review."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    for name in ("audio", "corrected", "qa-path"):
        parser.add_argument("--" + name, type=Path)
    for name in ("audio-sha", "corrected-sha", "qa-sha", "ffmpeg"):
        parser.add_argument("--" + name)
    parser.add_argument("--write-plan", type=Path, help="NEW path only; never a canonical, raw or frozen source.")
    args = parser.parse_args()
    provided = [args.audio, args.audio_sha, args.corrected, args.corrected_sha, args.qa_path, args.qa_sha, args.ffmpeg]
    try:
        if not any(provided) and not args.write_plan:
            context = source_preflight(args.root)
            print(json.dumps({"source_caption_preflight_passed": True, "scenes": 8, "words": 497,
                "genuine_cues": 54, "reviewed_photos": 8, "untimed_spans": 17, "last_cue_end": 190.469,
                "concrete_plan_written": False, "actual_audio_qa_required": True, "render_or_publication_approved": False}))
            return 0
        if not all(provided):
            parser.error("Supply actual audio/corrected/QA files, all three independent expected SHA256 values and --ffmpeg before timed authoring.")
        if args.write_plan:
            destination = args.write_plan.resolve()
            need(destination.is_relative_to(args.root.resolve() / "sources/expansion/plans") and not destination.exists(),
                 "Write only a NEW plan under sources/expansion/plans; never overwrite source/history.")
        plan = build(args.root, audio=args.audio, audio_sha=args.audio_sha, corrected=args.corrected,
            corrected_sha=args.corrected_sha, qa_path=args.qa_path, qa_sha=args.qa_sha, ffmpeg=args.ffmpeg)
        if args.write_plan:
            # All source, hash and actual re-decode gates precede directory/file creation.
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("x") as stream:
                stream.write(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"actual_decode_qa_passed": True, "plan_written": bool(args.write_plan), "scenes": 8,
            "duration_seconds": plan["duration_seconds"], "rendered": False, "publishable": False}))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
