#!/usr/bin/env python3
"""IC timed-authoring scaffold; actual decoded-audio QA is a hard prerequisite.

With no arguments, checks only the frozen source and genuine transcript exports.
--write requires independently supplied actual audio, corrected SRT and full QA
hashes. This does not export speech, render, publish or approve encoded frames
or browser playback. Original narration, screenshots and untimed recipe stay intact.
"""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
NAME = "app-ic-command-board"
FROZEN = "d25f95a7ef930001dfcdac28ba41f48cdf95eb79476fc81e6047bb6225c244c5"
TRANSCRIPTS = {
    "app-ic-command-board.fresh.txt": "1272bc2c1c9ea0f79658d056aff15c0ccaa5574c65de1ac6c2732b0312ee0eea",
    "app-ic-command-board.fresh.srt": "ec2c09344519c2640288743eed6f6f19ca0d319276ef1f2a76c84a415153f018",
    "app-ic-command-board.one-second.txt": "58965a6014fbcddbaebf8df0035c8bcbd81ef335e3b79e0fe9a0c81c687f2b25",
}
SOURCE_PREFLIGHT = "7c830c4eef3382a7cd3c226dbc75f1751f6414452e7d790c387ea87227c19dea"

# These are actual source cue IDs, not estimated operation times. Shared images
# may span several editorial units. Cue59 begins the prepared note-body speech.
SOURCE_CUES = [
    (1, 8, 39), (9, 16, 27), (17, 23, 35),
    (24, 25, 28), (26, 29, 29), (30, 36, 30),
    (37, 43, 31), (44, 49, 32), (50, 52, 34),
    (53, 58, 33), (59, 65, 37), (66, 70, 49),
    (71, 76, 48), (77, 82, 50), (83, 85, 44),
    (86, 87, 45), (88, 88, 46), (89, 93, 47), (94, 104, 51),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transcript_preflight(root):
    root = Path(root).resolve()
    sources = root / "sources"
    sys.path.insert(0, str(root / "scripts"))
    from render_walkthrough import load_cues

    offline = load_module(sources / "production/author_ic_command_take_01.py", "ic_offline_source")
    recipe = offline.build_recipe(sources)
    freeze = sources / offline.FREEZE
    lesson = json.loads((freeze / "app-ic-command-board.narrated-source.json").read_text())
    need(sha(freeze / "app-ic-command-board.narrated-source.json") == FROZEN, "Wrong narrated-source snapshot.")
    source_review = sources / "expansion/plans/app-ic-command-board-v2-final-source-preflight-20261027.json"
    need(sha(source_review) == SOURCE_PREFLIGHT, "Source preflight changed; review before rebinding.")
    for filename, expected in TRANSCRIPTS.items():
        need("estimated" not in filename, "Estimated speech exports cannot supply timing.")
        need(sha(sources / "expansion/audio" / filename) == expected, "Fresh transcript changed: " + filename)
    expected_words = " ".join(scene["narration"] for scene in lesson["scenes"]).split()
    plain = (sources / "expansion/audio/app-ic-command-board.fresh.txt").read_text()
    dense = (sources / "expansion/audio/app-ic-command-board.one-second.txt").read_text()
    need(plain.split() == expected_words, "Plain fresh transcript differs from the frozen script.")
    need(re.sub(r"\[\d\d:\d\d:\d\d\]", "", dense).split() == expected_words,
         "Genuine one-second TXT words differ from the frozen script.")
    need("[00:03:12] scope. Our [00:03:13] note keeps staging" in dense,
         "Missing genuine one-second note-body corroboration.")
    raw = load_cues(sources / "expansion/audio/app-ic-command-board.fresh.srt")
    need(len(raw) == 104 and " ".join(cue["text"] for cue in raw).split() == expected_words,
         "Fresh SRT is not the exact actual 104-cue script.")
    need(raw[58]["text"].startswith("Our note keeps staging") and raw[58]["start"] == 192.729,
         "The real note-body cue boundary changed.")
    records = json.loads((freeze / "captures.reviewed.json").read_text())["screenshots"]
    by_number = {int(row["id"].split("-")[1]): row for row in records}
    cue_sources = {}
    for first, last, number in SOURCE_CUES:
        need(number in by_number, "Source image absent from the frozen reviewed subset.")
        for cue in range(first, last + 1):
            need(cue not in cue_sources, "Duplicate source-cue assignment.")
            cue_sources[cue] = by_number[number]["id"]
    need(set(cue_sources) == set(range(1, 105)), "Incomplete source-cue correspondence.")
    by_id = {row["id"]: row for row in records}
    for index, references in cue_references().items():
        for label, phrase in references.items():
            need(label in by_id[cue_sources[index]]["visible_labels"],
                 f"Cue{index}: unseen literal label {label}.")
            need(phrase.casefold() in raw[index - 1]["text"].casefold(),
                 f"Cue{index}: spoken reference absent from actual speech.")
    return lesson, recipe, freeze, raw, records, cue_sources


def verify_media_qa(sources, audio, audio_sha, corrected, corrected_sha, qa_path, qa_sha, raw):
    """Consume completed actual-audio QA before constructing any timed plan."""
    for name, expected in (("audio", audio_sha), ("corrected SRT", corrected_sha), ("QA", qa_sha)):
        need(isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected), "Supply the explicit actual " + name + " SHA256.")
    paths = [Path(value).resolve() for value in (audio, corrected, qa_path)]
    for path in paths:
        need(path.is_relative_to(sources.resolve()), "Media/QA inputs must be retained inside sources.")
        need("estimated" not in path.name.casefold(), "Estimated exports cannot supply media approval.")
    audio, corrected, qa_path = paths
    need(sha(qa_path) == qa_sha, "Actual-audio QA hash differs.")
    qa = json.loads(qa_path.read_text())
    need(qa.get("passed") is True and qa.get("issues") == [], "Completed audio QA must pass with zero issues.")
    need(qa.get("lesson", {}).get("sha256") == FROZEN, "Audio QA is for another narrated-source snapshot.")
    need(qa.get("lesson", {}).get("words") == 887 and qa.get("lesson", {}).get("scenes") == 9,
         "Audio QA script count differs.")
    need(sha(audio) == audio_sha and audio.stat().st_size > 100_000, "Actual audio is missing, changed or an empty placeholder.")
    need(sha(corrected) == corrected_sha, "Corrected-caption hash differs.")
    details = qa.get("audio", {})
    need(details.get("sha256") == audio_sha and details.get("full_decode") == "passed",
         "Require a successful complete decode of this exact actual audio.")
    duration = details.get("duration_seconds")
    need(isinstance(duration, (int, float)) and not isinstance(duration, bool) and math.isfinite(duration)
         and raw[-1]["end"] <= duration <= raw[-1]["end"] + 2,
         "Decoded audio duration does not enclose the actual complete transcript.")
    need(details.get("sample_rate") == 48000
         and abs(details.get("decoded_samples", 0) - duration * 48000) < 480,
         "Require the complete decoded 48kHz PCM sample inventory.")
    need(qa.get("silent_raw_cues") == qa.get("silent_corrected_cues") == 0,
         "Every actual raw and corrected speech cue must be non-silent.")
    threshold = qa.get("signal_threshold_rms")
    need(isinstance(threshold, (int, float)) and threshold >= .001, "Cue-energy threshold is missing or weakened.")
    for field, expected in (("raw_captions", TRANSCRIPTS["app-ic-command-board.fresh.srt"]),
                            ("corrected_captions", corrected_sha)):
        data = qa.get(field, {})
        need(data.get("sha256") == expected and data.get("cues") == 104, "QA caption inventory differs: " + field)
        energy = data.get("energy", [])
        need(len(energy) == 104 and all(row.get("below_threshold") is False
             and row.get("samples", 0) > 0 and row.get("rms", 0) >= threshold for row in energy),
             "Incomplete, silent or low-energy speech cue inventory: " + field)
    need(qa["corrected_captions"].get("exact_script") is True, "Corrected captions must preserve the exact script.")
    need(not qa.get("possible_speech_gaps"), "Unresolved speech gaps cannot supply approval.")
    return qa, audio, corrected, qa_path


def cue_references():
    refs = {
        4: {"Call Details": "Call Details"},
        6: {"Active Command": "Active Command", "Open Command Board": "Open Command Board"},
        8: {"Open Command Board": "Open Command Board"}, 9: {"Command Board": "Command Board"},
        10: {"IC: WALLACE BODEN": "Wallace Boden"},
        13: {"Command Structure": "Command Structure", "Search Division — TRAINING": "Search Division", "Staging — TRAINING": "Staging"},
        14: {"Squad 3": "Squad 3"}, 15: {"ROTATE": "Rotate", "REQUIREMENTS": "Requirements"},
        17: {"Resources": "Resources"}, 18: {"All": "All", "Unassigned": "Unassigned", "Assigned": "Assigned"},
        19: {"Squad 3": "Squad 3", "Engine 51": "Engine 51", "Exercise Gate Marshal": "Exercise Gate Marshal"},
        20: {"Engine 51": "Engine 51", "Christopher Herrmann": "Christopher Herrmann", "Officer / Team Lead": "Officer or Team Lead"},
        21: {"UNASSIGNED": "unassigned"}, 24: {"Tactical Objectives": "Tactical Objectives", "Add": "Add"},
        26: {"Add Objective": "Add Objective", "Benchmark": "Benchmark", "Type": "Type"}, 28: {"Add": "Add"},
        30: {"Progress": "Progress", "50%": "fifty percent"}, 31: {"50%": "fifty percent"},
        32: {"Outcome": "Outcome", "Close-out note": "Close-out note", "Complete Objective": "Complete Objective"},
        37: {"Add Need": "Add Need", "Add": "Add"}, 38: {"Medical": "Medical", "Category": "Category"},
        39: {"Qty": "Qty", "2": "two", "Details": "Details"}, 41: {"Add": "Add"},
        45: {"OPEN": "open", "MEDICAL • 0/2": "zero of two filled"},
        47: {"Fill": "Fill", "1": "one", "of 2": "of two"},
        48: {"Note / Reason": "Note or Reason", "Save Fill": "Save Fill"},
        51: {"PARTIAL FILL": "Partial Fill", "MEDICAL • 1/2": "one of two"},
        52: {"History": "History", "Wallace Boden": "Wallace Boden"},
        53: {"MEDICAL • 1/2": "one of two", "BENCHMARK • 50%": "fifty percent"},
        57: {"Notes": "Notes", "Add Note": "Add Note"},
        59: {"TRAINING ONLY — Staging remains at the fictional west gate. No operational deployment.": "fictional west gate"},
        61: {"Visibility": "Visibility", "Internal": "Internal"},
        62: {"Visible to command staff only — the log records who added it, not the text": "visible to command staff only"},
        64: {"Public": "Public"}, 65: {"Save": "Save"}, 66: {"INTERNAL": "Internal"},
        67: {"ICS Role Assignments": "ICS Role Assignments", "Matthew Casey": "Matthew Casey", "SAFETY OFFICER": "Safety Officer"},
        71: {"Timers & PAR": "Timers and PAR", "TRAINING PAR reminder": "Training PAR reminder", "OVERDUE": "overdue"},
        72: {"Acknowledge": "Acknowledge"}, 77: {"Accountability": "Accountability"},
        78: {"Check-in timers are active, but no timers are configured for this call.": "no timers are configured"},
        79: {"Refresh": "Refresh"}, 83: {"Incident Map": "Incident Map", "Squad 3": "Squad 3"},
        84: {"Search Division — TRAINING": "Search Division"}, 86: {"Save View": "Save View"},
        88: {"Incident Map": "incident map"}, 90: {"Save View": "Save View"},
        91: {"Line": "Line", "Area": "Area", "Text": "Text"},
        94: {"Incident Log": "Incident Log"},
        95: {"Objective 'TRAINING — Primary search checked' progress 50%": "progress update"},
        99: {"Incident map created by Wallace Boden (Command) [Incident Commander]": "map-created entry"},
    }
    return refs


def build(root, *, audio, audio_sha, corrected, corrected_sha, qa_path, qa_sha):
    root = Path(root).resolve()
    sources = root / "sources"
    lesson, recipe, freeze, raw, records, cue_sources = transcript_preflight(root)
    qa, audio, corrected, qa_path = verify_media_qa(
        sources, audio, audio_sha, corrected, corrected_sha, qa_path, qa_sha, raw)
    from render_walkthrough import load_cues, words
    from verify_capture_evidence import instruction_scene_digest

    cues = load_cues(corrected)
    need(len(cues) == 104, "Corrected cue count differs.")
    need(all(c["start"] == old["start"] and c["end"] == old["end"] for c, old in zip(cues, raw)),
         "Corrected SRT must retain every genuine source cue bound.")
    need(" ".join(c["text"] for c in cues).split() == " ".join(s["narration"] for s in lesson["scenes"]).split(),
         "Corrected speech differs from the immutable script.")
    refs = cue_references()
    by_id = {row["id"]: row for row in records}
    entries = []
    for index, cue in enumerate(cues, 1):
        references = refs.get(index, {})
        for label, phrase in references.items():
            need(label in by_id[cue_sources[index]]["visible_labels"], f"Cue{index}: unseen literal label {label}.")
            need(phrase.casefold() in cue["text"].casefold(), f"Cue{index}: spoken reference absent from unchanged speech.")
        entries.append(dict(cue, cue=index, screenshot_id=cue_sources[index], required_labels=list(references),
                            spoken_references=references, instructional=bool(references)))
    groups, position = [], 0
    for authored in lesson["scenes"]:
        expected, actual, group = words(authored["narration"]), [], []
        while len(actual) < len(expected):
            cue = entries[position]
            position += 1
            actual += words(cue["text"])
            group.append(cue)
        need(actual == expected, "A genuine source cue crosses a scene boundary; review actual anchors before changing captions.")
        groups.append((authored, group))
    need(position == len(entries), "Unmapped closing speech.")
    reviewed_at = datetime.now(timezone.utc).isoformat()
    duration, scenes, holds = qa["audio"]["duration_seconds"], [], []
    for index, (authored, group) in enumerate(groups):
        start = 0 if index == 0 else group[0]["start"]
        end = duration if index == len(groups) - 1 else groups[index + 1][1][0]["start"]
        screens = []
        for j, cue in enumerate(group):
            at = start if j == 0 else cue["start"]
            if not screens or screens[-1]["screenshot_id"] != cue["screenshot_id"]:
                if screens:
                    screens[-1]["end"] = at
                screens.append({"screenshot_id": cue["screenshot_id"], "start": at, "end": end})
        for screen in screens:
            need(screen["end"] - screen["start"] >= 2, "Source screen is an unreadable flash cut.")
            holds.append({"scene_id": authored["id"], **screen})
        built = {"id": authored["id"], "title": authored["title"], "kind": "operational", "start": start, "end": end,
                 "visual_required_labels": authored["required_labels"], "screens": screens, "captions": group}
        instruction_review = {
            "passed": True, "reviewer": "Codex", "reviewed_at": reviewed_at,
            "correspondence_reviewed": True, "no_unseen_controls": True,
            "mapping_sha256": instruction_scene_digest(built, by_id),
            "method": "Exact19 stored-JPEG pixel/privacy review and28-span source preflight retained. All104 fresh SRT cues were manually mapped to matching actual UI. Scene06 uses actual cue59 to show the prepared note body after Notes/Add Note; the genuine one-second TXT corroborates this boundary. Original speech words, cue bounds and source pixels remain unchanged. This is source/cue review only, not encoded-frame or browser playback approval.",
        }
        scenes.append({"id": authored["id"], "start": start, "end": end, "screens": screens,
                       "captions": [{key: cue[key] for key in ("cue", "screenshot_id", "required_labels", "spoken_references", "instructional")} for cue in group],
                       "instruction_review": instruction_review})
    need(len(holds) == 22 and len({c["screenshot_id"] for c in entries}) == 19, "Expected source-screen sequence changed.")
    relative = lambda path: path.relative_to(sources).as_posix()
    plan = {
        "schema_version": 1, "lesson_id": NAME, "duration_seconds": duration,
        "instruction_mapping": "reviewed_scene_coverage", "display_context": "TRAINING ONLY · fictional incident and positions",
        "narration": {"file": relative(audio), "sha256": audio_sha, "kind": "approved_natural_narration", "approval": {
            "reviewer": "Codex", "reviewed_at": reviewed_at, "sha256": audio_sha, "complete_natural_narration": True,
            "qa_file": relative(qa_path), "qa_sha256": qa_sha,
            "method": "Consume completed actual full-decode PCM, all104 raw/corrected cue energies and exact887-word frozen-script QA. Parent verified nine actual generated WAV assets and the established Lulu stock voice; user confirmed narration audible. No agent subjective listening is asserted."}},
        "captions": {"file": relative(corrected), "sha256": corrected_sha, "kind": "speech_timed_srt", "approval": {
            "reviewer": "Codex", "reviewed_at": reviewed_at, "sha256": corrected_sha, "audio_sha256": audio_sha,
            "speech_timing_reviewed": True, "method": "All104 actual Descript cue bounds retained unchanged. The note-body transition uses the original SRT cue59 boundary, corroborated by genuine integer-second TXT. No estimated, interpolated or newly split speech positions."}},
        "capture_manifests": [{"file": relative(freeze / "captures.reviewed.json"), "sha256": sha(freeze / "captures.reviewed.json")}],
        "screenshot_reviews": {row["id"]: {"reviewer": "Codex", "reviewed_at": row["capture_review"]["reviewed_at"],
            "sha256": row["sha256"], "application_visible": True, "labels_legible": True, "no_errors": True,
            "method": row["capture_review"]["method"]} for row in records},
        "scenes": scenes,
        "source_freeze": {"lesson_sha256": FROZEN, "voice_source": relative(freeze / "app-ic-command-board.narrated-source.json"),
            "spoken_words": 887, "untimed_sequence_sha256": sha(freeze / "untimed-screen-sequence.json"),
            "genuine_plain_transcript_sha256": TRANSCRIPTS["app-ic-command-board.fresh.txt"],
            "genuine_srt_sha256": TRANSCRIPTS["app-ic-command-board.fresh.srt"],
            "genuine_one_second_txt_sha256": TRANSCRIPTS["app-ic-command-board.one-second.txt"],
            "source_preflight_sha256": SOURCE_PREFLIGHT},
        "limitations": ["Every source pixel and narrated word remains unchanged; encoded-frame and actual beginning/middle/end browser playback review remain required.",
            "Six sector companions reuse the bounded warehouse workflow; no separate sector deployment is implied.",
            "No objective completion, need closure, role/resource move, check-in/PAR success, physical arrival, device GPS, native hardware, provider delivery, offline replay, transfer or command/call closure is demonstrated."],
    }
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    for name in ("audio", "corrected", "qa-path"):
        parser.add_argument("--" + name, type=Path)
    for name in ("audio-sha", "corrected-sha", "qa-sha"):
        parser.add_argument("--" + name)
    parser.add_argument("--write", type=Path, help="Write a NEW concrete plan only after all actual-media QA inputs pass.")
    args = parser.parse_args()
    provided = [args.audio, args.audio_sha, args.corrected, args.corrected_sha, args.qa_path, args.qa_sha]
    if not any(provided) and not args.write:
        lesson, recipe, freeze, raw, records, cue_sources = transcript_preflight(args.root)
        print(json.dumps({"source_transcript_checks_passed": True, "scenes": 9, "words": 887,
                          "real_srt_cues": len(raw), "images": len(records), "concrete_plan_written": False,
                          "actual_audio_qa_required": True, "media_approved": False}))
        return
    if not all(provided):
        parser.error("Supply actual --audio/--audio-sha, --corrected/--corrected-sha and --qa-path/--qa-sha before timed authoring.")
    plan = build(args.root, audio=args.audio, audio_sha=args.audio_sha, corrected=args.corrected,
                 corrected_sha=args.corrected_sha, qa_path=args.qa_path, qa_sha=args.qa_sha)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        with args.write.open("x") as stream:
            stream.write(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"actual_media_qa_passed": True, "concrete_plan_written": bool(args.write),
                      "scenes": len(plan["scenes"]), "duration_seconds": plan["duration_seconds"],
                      "rendered_frame_or_browser_approval": False}))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        raise SystemExit(str(exc)) from exc
