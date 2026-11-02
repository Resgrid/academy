"""Read-only Inventory source/transcript preflight; optionally save NEW scaffold.

This cannot create a render plan or approve narration, timing, playback or media.
Actual decoded M4A QA and complete listening evidence remain separate requirements.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources"
FREEZE = Path("expansion/plans/core-inventory-movements-capture-freeze-20261028")
NAME = "core-inventory-movements"
PINS = {
    str(FREEZE / (NAME + ".narrated-source.json")): "261b4f3f205e38e0579e96ac24bdd56c600c41c708d3987fb498c3155866975c",
    str(FREEZE / "captures.reviewed.json"): "281d31686119c2ae542ac7e78d11dd6e698f279759e0db7e3465c149cbad83e2",
    str(FREEZE / "untimed-screen-sequence.json"): "2f8b9cbcf4f379c1bbecd2f6184ba7f99ac7b1c4d68a850749760d7a614c9184",
    str(FREEZE / "narration.txt"): "ff8a84104e732cf0e5a807fc7d0db6259968daf866121f15c3a4e68dfed39ddd",
    str(FREEZE / "parent-source-review.json"): "7066eeb3aff241ed2c09d6647ee5e26c1acabbd38f83872c2d69f4110438d99d",
    str(FREEZE / "source-citations.json"): "e074d96870548a58631dd4634c1e333f94a02f33a4a5a59ba8aad3fc006dea17",
    str(FREEZE / "scenario-fixture.json"): "00784d491927e6d348c9f19c913933e7c9c97e94d4ea857b7b6ef142b94cf501",
    "expansion/audio/core-inventory-movements-generated-20261028.plain.txt": "ad0868551601ab911e6f45d2f57afe7d34d888d072c82027aa20a840d01e60ef",
    "expansion/audio/core-inventory-movements-generated-20261028.raw.srt": "f4fa221133123c8a76ffed3bd84e59147dfee6546b82cb811f31205fc4195b64",
    "expansion/audio/core-inventory-movements-generated-20261028.one-second.txt": "e9ca93f0d71b8372434b70f0bf0bc487a95b00253940db0ec44edb87a5e64a56",
    "expansion/audio/core-inventory-movements-generated-20261028.provenance.json": "983a11327a259e15af184e9c75b6bb3993135ff377971887f20fe0b44de42f9a",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalized(text):
    return " ".join(text.split())


def asset(relative):
    p = (SOURCES / relative).resolve()
    need(p.is_relative_to(SOURCES.resolve()), "Input escapes source root.")
    return p


def correspondence(lesson, spans, cues, shots):
    """Map exact words, requiring every photo cut to be a real cue boundary."""
    script = normalized(" ".join(scene["narration"] for scene in lesson["scenes"]))
    need(normalized(" ".join(c["text"] for c in cues)) == script, "SRT differs from frozen spoken words.")
    need(normalized(" ".join(s["narration_exact"] for s in spans)) == script, "Held source spans differ from frozen spoken words.")
    by_scene = {scene["id"]: scene for scene in lesson["scenes"]}
    need(len(by_scene) == len(lesson["scenes"]), "Duplicate scene IDs.")
    starts, position = {}, 0
    for i, cue in enumerate(cues):
        starts[position] = i
        position += len(cue["text"].split())
    total_words = position
    position, result = 0, []
    for i, span in enumerate(spans):
        start_word = position
        position += len(span["narration_exact"].split())
        need(start_word in starts, "Source cut is inside a raw cue; review genuine one-second anchors before splitting. No interpolation allowed.")
        need(position == total_words or position in starts, "Source span ends inside a raw cue; genuine service anchor required.")
        first = starts[start_word]
        after = starts[position] if position < total_words else len(cues)
        shot = shots[span["capture_ref"]]
        need(span["scene_id"] in by_scene, "Unknown source scene.")
        need(set(span["required_labels"]) <= set(shot["visible_labels"]), "Named source controls are not in the retained reviewed foreground labels.")
        result.append({
            "span": i + 1, "scene_id": span["scene_id"], "capture_ref": span["capture_ref"],
            "source_file": shot["file"], "source_sha256": shot["sha256"],
            "narration_exact": span["narration_exact"], "required_labels": span["required_labels"],
            "first_actual_cue": first + 1, "last_actual_cue": after,
            "actual_exported_cue_start": cues[first]["start"],
            "next_source_actual_cue_start": cues[after]["start"] if after < len(cues) else None,
            "last_actual_speech_end": cues[after - 1]["end"],
            "boundary_method": "Unchanged genuine exported SRT cue boundary; no split, interpolation or estimated word time.",
            "final_screen_hold_end": None,
            "scope_limit": span.get("scope_limit", ""),
            "cue_correspondence": [dict(cues[j], cue=j + 1) for j in range(first, after)],
        })
    need(position == total_words, "Unmapped spoken words.")
    for scene in lesson["scenes"]:
        selected = [s for s in spans if s["scene_id"] == scene["id"]]
        need(normalized(" ".join(s["narration_exact"] for s in selected)) == normalized(scene["narration"]), "Scene/spoken source correspondence differs.")
        union = {label for s in selected for label in shots[s["capture_ref"]]["visible_labels"]}
        need(set(scene["required_labels"]) <= union, "A named scene control has no reviewed source.")
    return result


def prepare():
    for relative, digest in PINS.items():
        need(sha(asset(relative)) == digest, "Changed held input: " + relative)
    sys.path.insert(0, str(ROOT / "scripts"))
    from render_walkthrough import load_cues
    from verify_capture_evidence import _Validator, _image_dimensions
    lesson = read(asset(str(FREEZE / (NAME + ".narrated-source.json"))))
    captures = read(asset(str(FREEZE / "captures.reviewed.json")))["screenshots"]
    sequence = read(asset(str(FREEZE / "untimed-screen-sequence.json")))["spans"]
    review = read(asset(str(FREEZE / "parent-source-review.json")))
    need(len(lesson["scenes"]) == 12 and len(captures) == 16 and len(sequence) == 16, "Held source inventory differs.")
    need(review["actual_source_images_inspected"] == 16 and review["source_only"] is True, "Parent source review is missing.")
    shots = {shot["id"]: shot for shot in captures}
    need(len(shots) == 16, "Duplicate held screenshots.")
    for shot in captures:
        p = asset(shot["file"])
        need(sha(p) == shot["sha256"] and _image_dimensions(p) == (1434, 773), "Actual original source identity/dimensions differ.")
        need(shot["eligible_for_lesson"] is True and shot["capture_review"]["passed"] is True and shot["capture_review"]["sha256"] == shot["sha256"], "Source review is missing or stale.")
        validator = _Validator(SOURCES)
        validator.observations(shot, shot["id"])
        need(not validator.issues, "; ".join(validator.issues))
    prefix = "expansion/audio/" + NAME + "-generated-20261028"
    cues = load_cues(asset(prefix + ".raw.srt"))
    script = normalized(" ".join(scene["narration"] for scene in lesson["scenes"]))
    need(len(script.split()) == 828 and len(cues) == 93, "Actual word/cue count differs.")
    need(normalized(asset(prefix + ".plain.txt").read_text()) == script, "Plain actual transcript differs from frozen words.")
    anchors = asset(prefix + ".one-second.txt").read_text()
    need(normalized(re.sub(r"\[\d\d:\d\d:\d\d\]", "", anchors)) == script, "One-second actual transcript differs from frozen words.")
    marks = re.findall(r"\[(\d\d):(\d\d):(\d\d)\]", anchors)
    need(len(marks) > 300, "Dense service-exported one-second anchors missing.")
    media = read(asset(prefix + ".provenance.json"))
    need(media["asset_count"] == 12 and len(media["actual_generated_audio_assets"]) == 12 and all(a["type"] == "audio" and a["duration_seconds"] > 0 for a in media["actual_generated_audio_assets"]), "All12 actual speech assets required before transcript correspondence.")
    spans = correspondence(lesson, sequence, cues, shots)
    return {
        "kind": "source_and_actual_transcript_correspondence_scaffold_only", "lesson_id": NAME,
        "frozen_lesson_sha256": PINS[str(FREEZE / (NAME + ".narrated-source.json"))],
        "source_pins": PINS, "actual_sources": 16, "scenes": 12, "words": 828,
        "actual_generated_assets": 12, "service_composition_seconds": media["composition_duration_seconds"],
        "raw_cues": 93, "source_spans": spans,
        "timing_precision": "All16 source openings already coincide with actual SRT cue starts. Genuine one-second TXT is retained but no subcue cut is currently required.",
        "source_review_attribution": {"reviewer": review["reviewer"], "file": str(FREEZE / "parent-source-review.json"), "sha256": PINS[str(FREEZE / "parent-source-review.json")], "assembler_performed_new_pixel_review": False},
        "first_frame_start": None, "decoded_master_hold_end": None, "render_plan": None,
        "audio_approved": False, "rendering_approved": False, "publication_approved": False,
        "pending_requirements": [
            "Parent-obtained complete M4A hash and full decoded duration/sample inventory.",
            "Exact frozen script and every actual raw/corrected cue energy pass against that M4A.",
            "Complete actual listening approval bound to frozen source and downloaded audio.",
            "Manual spoken-reference mapping to literal source controls before renderer plan approval.",
            "Readable holds, full source/caption/encoded-interval review and actual native beginning/middle/end playback after any render.",
        ],
        "scope_limits": [
            "Legacy originals have no retained DOM; no DOM, field rectangles or accessible controls are invented.",
            "Partial return is a saved-result review; its intervening dialog is absent.",
            "Station/Unit/Personnel are the pictured holder labels. Balances14/5/1 are a dated snapshot before later usage.",
            "Alert is Resolved Low stock, not a demonstrated expiring-lot alert. Report chooser is not generated output or PDF.",
            "Service composition/media durations do not substitute for decoded downloaded audio or listening approval.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-scaffold", type=Path, help="Write a NEW source-only JSON beneath sources/expansion/plans.")
    args = parser.parse_args()
    scaffold = prepare()
    if args.write_scaffold:
        target = args.write_scaffold.resolve()
        need(target.is_relative_to((SOURCES / "expansion/plans").resolve()) and not target.exists(), "Use a NEW source-plan path; preserve existing history.")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(scaffold, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"source_transcript_preflight": "passed", "actual_assets": 12, "actual_sources": 16, "scenes": 12, "words": 828, "raw_cues": 93, "one_second_splits_required": 0, "scaffold_written": bool(args.write_scaffold), "render_plan_created": False, "audio_or_publication_approved": False}, indent=2))


if __name__ == "__main__":
    main()
