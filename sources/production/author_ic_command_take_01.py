#!/usr/bin/env python3
"""Validate and export IC's frozen, untimed source-screen assembly recipe.

This reads the immutable narrated-source snapshot, never the mutable canonical
lesson. No speech positions are estimated. A later timed recipe must consume
real approved audio/captions, genuine transcript anchors and fresh media QA.
No browser, API, rendering, speech generation or publishing runs here.
"""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys


FREEZE = Path("expansion/plans/app-ic-command-board-capture-freeze-20261027-v2")
PINS = {
    "app-ic-command-board.narrated-source.json": "d25f95a7ef930001dfcdac28ba41f48cdf95eb79476fc81e6047bb6225c244c5",
    "untimed-screen-sequence.json": "23474e5d7bebd79b2c65e94eafe261dc3c697e34463956d4cc0140b4efcbbf6f",
    "captures.reviewed.json": "5ff13eecbdae60aaf530fa0b361f52026bc9dce05249513c5919d4859279969c",
    "source-readiness.json": "b4cc532993bef651f06001ab86b279f8aa19b0a065b181371439b28a69f90203",
    "source-revision.json": "99ef419a816d750fca97fe54116101f3023ae3d3b2b34b21d2d2441ee746cc21",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned_document(sources, name):
    data = (sources / FREEZE / name).read_bytes()
    if digest(data) != PINS[name]:
        raise ValueError(f"Frozen input changed: {name}")
    return json.loads(data)


def build_recipe(sources):
    sources = Path(sources).resolve()
    sys.path.insert(0, str(sources.parent / "scripts"))
    import verify_capture_evidence as evidence

    frozen = {name: pinned_document(sources, name) for name in PINS}
    lesson = frozen["app-ic-command-board.narrated-source.json"]
    sequence = frozen["untimed-screen-sequence.json"]
    captures = frozen["captures.reviewed.json"]
    readiness = frozen["source-readiness.json"]
    if lesson["id"] != "app-ic-command-board" or lesson.get("export_ready") is not False:
        raise ValueError("Use the unapproved source freeze, not a ready canonical file.")
    if len(lesson["scenes"]) != 9 or len(captures["screenshots"]) != 19:
        raise ValueError("Frozen scene or capture count differs.")
    if any(readiness[key] is not False for key in (
        "audio_approved", "media_approved", "browser_playback_approved", "export_ready"
    )):
        raise ValueError("Source readiness cannot supply media approval.")

    validator = evidence._Validator(sources)
    by_id = {}
    for index, row in enumerate(captures["screenshots"]):
        field = f"screenshots[{index}]"
        validator.asset(row, field, image=True)
        validator.application(row, field)
        validator.observations(row, field)
        by_id[row["id"]] = row
    if validator.issues:
        raise ValueError(json.dumps(validator.issues, ensure_ascii=False))

    scenes = []
    span_count = 0
    for lesson_scene, source_scene in zip(lesson["scenes"], sequence["scenes"]):
        if lesson_scene["id"] != source_scene["id"]:
            raise ValueError("Frozen scene order differs.")
        spans = source_scene["spans"]
        if " ".join(span["text"] for span in spans) != lesson_scene["narration"]:
            raise ValueError("Source-screen spans changed a narrated word.")
        available = set()
        for span in spans:
            if any(key in span for key in ("start", "end", "duration")):
                raise ValueError("Untimed source correspondence cannot assign media positions.")
            for capture_ref in span["capture_refs"]:
                available.update(evidence._normalized(label)
                                 for label in by_id[capture_ref]["visible_labels"])
        if any(evidence._normalized(label) not in available
               for label in lesson_scene["required_labels"]):
            raise ValueError(f"Scene {lesson_scene['id']} lacks a visible requirement.")
        scenes.append({
            "id": lesson_scene["id"],
            "title": lesson_scene["title"],
            "route": lesson_scene["route"],
            "required_labels": copy.deepcopy(lesson_scene["required_labels"]),
            "narration": lesson_scene["narration"],
            "spans": copy.deepcopy(spans),
        })
        span_count += len(spans)
    word_count = len(re.findall(r"\b[\w'-]+\b", " ".join(x["narration"] for x in scenes)))
    if span_count != 28 or word_count != 887:
        raise ValueError("Frozen narration or span count differs.")
    return {
        "schema_version": 1,
        "lesson_id": lesson["id"],
        "app": "IC",
        "kind": "untimed_source_screen_recipe",
        "narrated_source_file": str(FREEZE / "app-ic-command-board.narrated-source.json"),
        "narrated_source_sha256": PINS["app-ic-command-board.narrated-source.json"],
        "capture_manifest_file": str(FREEZE / "captures.reviewed.json"),
        "capture_manifest_sha256": PINS["captures.reviewed.json"],
        "word_count": word_count,
        "source_image_count": len(by_id),
        "span_count": span_count,
        "timing": "Unassigned; requires real approved speech and genuine transcript anchors.",
        "media_approved": False,
        "export_ready": False,
        "scenes": scenes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write", type=Path, help="Write the untimed recipe to a new file; existing files are refused.")
    args = parser.parse_args()
    recipe = build_recipe(args.sources)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        with args.write.open("x") as stream:
            stream.write(json.dumps(recipe, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "source_checks_passed": True,
        "lesson": recipe["lesson_id"],
        "scenes": len(recipe["scenes"]),
        "words": recipe["word_count"],
        "spans": recipe["span_count"],
        "images": recipe["source_image_count"],
        "media_approved": False,
    }))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(str(exc)) from exc
